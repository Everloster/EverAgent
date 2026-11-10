package core

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

type OpError struct {
	Message string
	Code    int
}

func (e *OpError) Error() string             { return e.Message }
func blocked(message string, code int) error { return &OpError{message, code} }
func ErrorCode(err error) int {
	var e *OpError
	if errors.As(err, &e) {
		return e.Code
	}
	var exit *exec.ExitError
	if errors.As(err, &exit) {
		return exit.ExitCode()
	}
	if err != nil {
		return 1
	}
	return 0
}

type Author struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

func identityFailure(message string, identity Object) error {
	// Keep the failed observation's code: a later diagnose can succeed and
	// cannot reconstruct it. Never include native paths or error payloads.
	if reason := text(identity["model_reason_code"]); regexp.MustCompile(`^[a-z][a-z0-9-]{0,95}$`).MatchString(reason) {
		message += " (" + reason + ")"
	}
	return blocked(message, 1)
}

func RequireModel(identity Object) error {
	observed := identity["current_model_confirmed"] == true && identity["model_confidence"] == "session-bound"
	declared := identity["user_model_declared"] == true && identity["model_confidence"] == "declared" && identity["model_source"] == "user-declared" && len(object(identity["declaration"])) > 0
	if model(identity["model"]) == "" || !(observed || declared) {
		return identityFailure("当前模型未核实；先 eacli session diagnose --json 修复自动读取，确实无法核实才请用户指定。已授权源码和只读工作可继续", identity)
	}
	return nil
}
func ValidIdentity(identity Object) error {
	if identity["resolved"] != true || !regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._-]{0,160}$`).MatchString(text(identity["name"])) || strings.HasSuffix(text(identity["name"]), "-unknown") || !regexp.MustCompile(`^noreply@[^\s<>@]+$`).MatchString(text(identity["email"])) {
		return identityFailure("当前 Agent 身份未识别；运行 eacli session diagnose --json 修复，不从配置猜测署名", identity)
	}
	return RequireModel(identity)
}
func ValidateIdentity(identity Object, committer, author, expected Author) []string {
	errors := []string{}
	if e := ValidIdentity(identity); e != nil {
		errors = append(errors, e.Error())
	}
	if committer != (Author{text(identity["name"]), text(identity["email"])}) {
		errors = append(errors, "Git Committer does not match the current Agent/model")
	}
	if author != expected {
		errors = append(errors, "Git Author does not match the repository owner")
	}
	return errors
}
func IdentityEnvironment(identity Object, base []string, author Author) ([]string, error) {
	if e := ValidIdentity(identity); e != nil {
		return nil, e
	}
	if strings.TrimSpace(author.Name) == "" || strings.ContainsAny(author.Name, "\r\n<>") || !regexp.MustCompile(`^[^\s<>@]+@[^\s<>@]+$`).MatchString(author.Email) {
		return nil, blocked("repository author policy invalid", 1)
	}
	env := map[string]string{}
	for _, entry := range base {
		k, v, ok := strings.Cut(entry, "=")
		if ok {
			env[k] = v
		}
	}
	count := 0
	if value := env["GIT_CONFIG_COUNT"]; value != "" {
		var e error
		count, e = strconv.Atoi(value)
		if e != nil || count < 0 || count > 1024 {
			return nil, blocked("invalid GIT_CONFIG_COUNT", 2)
		}
	}
	env["GIT_AUTHOR_NAME"], env["GIT_AUTHOR_EMAIL"], env["GIT_COMMITTER_NAME"], env["GIT_COMMITTER_EMAIL"] = author.Name, author.Email, text(identity["name"]), text(identity["email"])
	for _, pair := range [][2]string{{"user.name", text(identity["name"])}, {"user.email", text(identity["email"])}} {
		env[fmt.Sprintf("GIT_CONFIG_KEY_%d", count)], env[fmt.Sprintf("GIT_CONFIG_VALUE_%d", count)] = pair[0], pair[1]
		count++
	}
	env["GIT_CONFIG_COUNT"] = strconv.Itoa(count)
	// Commit, message reuse, hooks and the quality gate must all see the actual
	// Git objects, not a workstation's refs/replace view of their contents.
	env["GIT_NO_REPLACE_OBJECTS"] = "1"
	out := []string{}
	for k, v := range env {
		out = append(out, k+"="+v)
	}
	return out, nil
}

type commitOption struct {
	key   string
	value *string
}

var valueOptions = []string{"-m", "-F", "-C", "-c", "--message", "--file", "--reuse-message", "--reedit-message", "--author", "--date", "--cleanup", "--squash", "--trailer"}
var commitFlags = []string{"-q", "--quiet", "-v", "--verbose", "-s", "--signoff", "--no-signoff", "-S", "--gpg-sign", "--no-gpg-sign", "--no-verify", "--verify", "--allow-empty", "--allow-empty-message", "--amend", "--no-post-rewrite", "--no-edit", "-e", "--edit", "--dry-run", "--short", "--branch", "--porcelain", "--long", "-z", "--null", "--ahead-behind", "--no-ahead-behind", "--renames", "--no-renames", "--find-renames"}

func commitOptions(args []string) ([]commitOption, error) {
	options := []commitOption{}
	for n := 0; n < len(args); n++ {
		a := args[n]
		var v string
		key := a
		if contains(valueOptions, a) {
			n++
			if n == len(args) {
				return nil, blocked(a+" 缺少参数值", 2)
			}
			v = args[n]
		} else if len(a) > 2 && contains([]string{"-m", "-F", "-C", "-c"}, a[:2]) {
			key, v = a[:2], a[2:]
		} else if k, x, ok := strings.Cut(a, "="); ok && (contains(valueOptions, k) || contains([]string{"--gpg-sign", "--find-renames"}, k)) {
			key, v = k, x
		} else if contains(commitFlags, a) {
			options = append(options, commitOption{key: a})
			continue
		} else {
			return nil, blocked("不接受改变待提交 tree 的模式、未审计选项或 pathspec；先显式 git add："+a, 2)
		}
		options = append(options, commitOption{key, &v})
	}
	return options, nil
}
func gitRead(ctx context.Context, cwd string, env []string, args ...string) (string, error) {
	b, e := command(ctx, cwd, env, 2<<20, append([]string{"git", "--no-replace-objects"}, args...)...)
	if e != nil {
		return "", blocked("无法读取仓库或 Git index", 1)
	}
	return strings.TrimSpace(string(b)), nil
}

// Commit and the repository-owned gate must see the same repository and index.
// A caller may use an alternate index, but never redirect repository discovery
// or objects. Absolute index paths survive the gate's different working dir.
func commitEnvironment(base []string) error {
	for _, entry := range base {
		key, value, _ := strings.Cut(entry, "=")
		switch key {
		case "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE", "GIT_SHALLOW_FILE", "GIT_REPLACE_REF_BASE":
			return blocked("提交不接受仓库定位环境变量 "+key+"；请在目标 checkout 中运行", 2)
		case "GIT_INDEX_FILE":
			if !filepath.IsAbs(value) {
				return blocked("GIT_INDEX_FILE 必须是绝对路径，避免提交和门禁使用不同 index", 2)
			}
		}
	}
	return nil
}

func commitRoot(ctx context.Context, cwd string, env []string) (string, error) {
	// Independently compare the effective location with the gate's
	// explicit-checkout discovery semantics;
	// retain caller config for hooks and signing, but refuse a different target.
	canonical := []string{}
	for _, entry := range env {
		key, _, _ := strings.Cut(entry, "=")
		if !strings.HasPrefix(key, "GIT_") || key == "GIT_INDEX_FILE" {
			canonical = append(canonical, entry)
		}
	}
	root := ""
	for _, option := range []string{"--show-toplevel", "--absolute-git-dir"} {
		actual, err := gitRead(ctx, cwd, env, "rev-parse", option)
		if err != nil {
			return "", err
		}
		expected, err := gitRead(ctx, cwd, canonical, "rev-parse", option)
		if err != nil || realPath(actual) != realPath(expected) {
			return "", blocked("提交与质量门的 Git 仓库定位不一致；未执行提交", 2)
		}
		if option == "--show-toplevel" {
			root = realPath(actual)
		}
	}
	return root, nil
}

func messageArgs(ctx context.Context, parts []commitOption, cwd, temp string, env []string, stdin io.Reader) ([]string, error) {
	messages, files, reused := []string{}, []string{}, []commitOption{}
	amend, noEdit := false, false
	for _, p := range parts {
		switch p.key {
		case "-m", "--message":
			messages = append(messages, *p.value)
		case "-F", "--file":
			files = append(files, *p.value)
		case "-C", "-c", "--reuse-message", "--reedit-message":
			reused = append(reused, p)
		case "--amend":
			amend = true
		case "--no-edit":
			noEdit = true
		}
	}
	groups := 0
	for _, n := range []int{len(messages), len(files), len(reused)} {
		if n > 0 {
			groups++
		}
	}
	if groups > 1 || len(files) > 1 || len(reused) > 1 {
		return nil, blocked("commit message 来源冲突", 2)
	}
	var message *string
	if len(messages) > 0 {
		x := strings.Join(messages, "\n\n")
		message = &x
	} else if len(files) > 0 {
		var b []byte
		var e error
		if files[0] == "-" {
			b, e = io.ReadAll(io.LimitReader(stdin, 1<<20+1))
		} else {
			path := files[0]
			if !filepath.IsAbs(path) {
				path = filepath.Join(cwd, path)
			}
			f, err := os.Open(path)
			if err != nil {
				return nil, blocked("无法读取 commit message 文件", 2)
			}
			b, e = io.ReadAll(io.LimitReader(f, 1<<20+1))
			f.Close()
		}
		if e != nil || len(b) > 1<<20 {
			return nil, blocked("commit message 文件不可用或过大", 2)
		}
		x := string(b)
		message = &x
	} else if len(reused) > 0 || amend && noEdit {
		revision := "HEAD"
		if len(reused) > 0 {
			revision = *reused[0].value
		}
		sha, e := gitRead(ctx, cwd, env, "rev-parse", "--verify", "--end-of-options", revision+"^{commit}")
		if e != nil {
			return nil, e
		}
		b, e := command(ctx, cwd, env, 1<<20, "git", "--no-replace-objects", "show", "-s", "--format=%B", sha)
		if e != nil {
			return nil, blocked("无法读取复用的 commit message", 2)
		}
		x := string(b)
		message = &x
	}
	out := []string{}
	for _, p := range parts {
		if message != nil && contains([]string{"-m", "--message", "-F", "--file", "-C", "-c", "--reuse-message", "--reedit-message"}, p.key) {
			continue
		}
		out = append(out, p.key)
		if p.value != nil {
			out = append(out, *p.value)
		}
	}
	if message != nil {
		path := filepath.Join(temp, "message.txt")
		s := *message
		if s != "" && !strings.HasSuffix(s, "\n") {
			s += "\n"
		}
		if e := os.WriteFile(path, []byte(s), 0600); e != nil {
			return nil, e
		}
		out = append(out, "-F", path)
	}
	if len(reused) > 0 {
		if contains([]string{"-c", "--reedit-message"}, reused[0].key) {
			out = append(out, "--edit")
		} else {
			out = append(out, "--no-edit")
		}
	}
	if amend {
		out = append(out, "--reset-author")
	}
	return out, nil
}
func signingEvidence(identity Object) string {
	o := Object{}
	for _, k := range []string{"name", "email", "cli", "model", "model_source", "model_confidence", "current_model_confirmed", "user_model_declared", "scope_ref", "observation_ref"} {
		o[k] = identity[k]
	}
	d := object(identity["declaration"])
	o["declaration.id"], o["declaration.scope_ref"] = d["id"], d["scope_ref"]
	if identity["cli"] == "claude-code" && identity["model_source"] == "claude-session-runtime" && identity["current_model_confirmed"] == true && identity["model_confidence"] == "session-bound" && regexp.MustCompile(`^[0-9a-f]{24}$`).MatchString(text(identity["scope_ref"])) && regexp.MustCompile(`^[0-9a-f]{24}$`).MatchString(text(identity["observation_ref"])) {
		o["observation_ref"] = "claude-session"
	}
	if identity["current_model_confirmed"] == true && identity["observation_ref"] != nil {
		o["model_source"] = "session-observation"
	}
	return Digest(o)
}

type CommitOptions struct {
	// IdentityOnly lets a caller require only verified Committer attribution.
	// Other repositories retain their explicitly supplied quality policy.
	IdentityOnly bool
	// ContentGuard is an optional, caller-owned check of the exact staged content.
	// Unlike Gate/Preflight it may accompany IdentityOnly (e.g. public disclosure).
	ContentGuard   func(context.Context, string, []string) error
	Directory      string
	IdentityReader func() Object
	AuthorReader   func() (Author, error)
	Gate           func(context.Context, string, []string) error
	Preflight      func(string, Object) error
	Stdin          io.Reader
	Stdout, Stderr io.Writer
}

func Commit(ctx context.Context, args []string, options CommitOptions) error {
	if options.IdentityReader == nil {
		return blocked("Committer identity reader unavailable", 1)
	}
	if !options.IdentityOnly && (options.AuthorReader == nil || options.Gate == nil) {
		return blocked("repository quality owner unavailable", 1)
	}
	if options.Stdin == nil {
		options.Stdin = os.Stdin
	}
	if options.Stdout == nil {
		options.Stdout = os.Stdout
	}
	if options.Stderr == nil {
		options.Stderr = os.Stderr
	}
	parts, e := commitOptions(args)
	if e != nil {
		return e
	}
	base := os.Environ()
	if e := commitEnvironment(base); e != nil {
		return e
	}
	identity := options.IdentityReader()
	author := Author{text(identity["name"]), text(identity["email"])}
	if options.AuthorReader != nil {
		selected, err := options.AuthorReader()
		if err != nil && !options.IdentityOnly {
			return err
		}
		if err == nil {
			author = selected
		}
	}
	env, e := IdentityEnvironment(identity, base, author)
	if e != nil && options.IdentityOnly {
		// Author is a default, not an independent admission policy in this mode.
		author = Author{text(identity["name"]), text(identity["email"])}
		env, e = IdentityEnvironment(identity, base, author)
	}
	if e != nil {
		return e
	}
	root, e := commitRoot(ctx, options.Directory, env)
	if e != nil {
		return e
	}
	if !options.IdentityOnly && options.Preflight != nil {
		if e = options.Preflight(root, identity); e != nil {
			return e
		}
	}
	expectedAuthor := author.Name + " <" + author.Email + ">"
	for _, p := range parts {
		if !options.IdentityOnly && p.key == "--author" && *p.value != expectedAuthor {
			return blocked("--author 必须与仓库主人身份一致", 2)
		}
	}
	temp, e := os.MkdirTemp("", "everagent-commit-*")
	if e != nil {
		return e
	}
	defer os.RemoveAll(temp)
	forwarded, e := messageArgs(ctx, parts, root, temp, env, options.Stdin)
	if e != nil {
		return e
	}
	if options.IdentityOnly {
		// No quality gate, asset check or Author-policy re-read. A public caller
		// may explicitly check disclosure; bind that check to the committed tree.
		guardedTree := ""
		if options.ContentGuard != nil {
			guardedTree, e = gitRead(ctx, root, env, "write-tree")
			if e != nil {
				return e
			}
			if e = options.ContentGuard(ctx, root, env); e != nil {
				return e
			}
			after, err := gitRead(ctx, root, env, "write-tree")
			if err != nil || after != guardedTree {
				return blocked("公开内容检查期间暂存区已变化；请重新提交", 3)
			}
		}
		cleanEnv := env[:0]
		for _, entry := range env {
			if !strings.HasPrefix(entry, "EVERAGENT_PUBLIC_CONTENT_TREE=") {
				cleanEnv = append(cleanEnv, entry)
			}
		}
		env = cleanEnv
		if guardedTree != "" {
			env = append(env, "EVERAGENT_PUBLIC_CONTENT_TREE="+guardedTree)
		}
		// Git still owns normal commit errors and the caller's configured hooks.
		c := exec.CommandContext(ctx, "git", append([]string{"--no-replace-objects", "commit"}, forwarded...)...)
		c.Dir, c.Env, c.Stdin, c.Stdout, c.Stderr = root, env, options.Stdin, options.Stdout, options.Stderr
		if e = c.Run(); e != nil {
			return e
		}
		for _, p := range parts {
			if p.key == "--dry-run" {
				return nil
			}
		}
		if guardedTree != "" {
			tree, err := gitRead(ctx, root, env, "rev-parse", "HEAD^{tree}")
			if err != nil || tree != guardedTree {
				return blocked("commit 已生成，但不是已检查的公开内容；保留现场，禁止推送", 3)
			}
		}
		actual, err := gitRead(ctx, root, env, "show", "-s", "--format=%cn <%ce>", "HEAD")
		if err != nil || actual != text(identity["name"])+" <"+text(identity["email"])+">" {
			return blocked("commit 已生成，但 Committer 核验失败；保留现场，禁止自动重放或推送", 3)
		}
		return nil
	}
	before, e := gitRead(ctx, root, env, "write-tree")
	if e != nil {
		return e
	}
	if e = options.Gate(ctx, root, env); e != nil {
		return e
	}
	after, e := gitRead(ctx, root, env, "write-tree")
	if e != nil {
		return e
	}
	if after != before {
		return blocked("quality gate 期间 Git index 已变化，请重新检查", 3)
	}
	fresh := options.IdentityReader()
	nextAuthor, e := options.AuthorReader()
	if e != nil {
		return e
	}
	if e = ValidIdentity(fresh); e != nil {
		return e
	}
	if signingEvidence(fresh) != signingEvidence(identity) {
		return blocked("quality gate 期间 Agent/模型身份已变化，请重新核实", 3)
	}
	if nextAuthor != author {
		return blocked("quality gate 期间仓库 Author 策略已变化", 3)
	}
	if options.Preflight != nil {
		if e = options.Preflight(root, fresh); e != nil {
			return e
		}
	}
	// A repository hook may reuse this successful gate for this exact tree.
	// It must still validate identity. This is not an authorization token and
	// never lets the commit wrapper itself skip its gate or tree rechecks.
	for n := 0; n < len(env); {
		if strings.HasPrefix(env[n], "EVERAGENT_QUALITY_GATE_TREE=") {
			env = append(env[:n], env[n+1:]...)
		} else {
			n++
		}
	}
	env = append(env, "EVERAGENT_QUALITY_GATE_TREE="+before)
	c := exec.CommandContext(ctx, "git", append([]string{"--no-replace-objects", "commit"}, forwarded...)...)
	c.Dir = root
	c.Env = env
	c.Stdin = options.Stdin
	c.Stdout = options.Stdout
	c.Stderr = options.Stderr
	if e = c.Run(); e != nil {
		return e
	}
	for _, p := range parts {
		if p.key == "--dry-run" {
			return nil
		}
	}
	tree, e1 := gitRead(ctx, root, env, "rev-parse", "HEAD^{tree}")
	actualAuthor, e2 := gitRead(ctx, root, env, "show", "-s", "--format=%an <%ae>", "HEAD")
	actualCommitter, e3 := gitRead(ctx, root, env, "show", "-s", "--format=%cn <%ce>", "HEAD")
	if e1 != nil || e2 != nil || e3 != nil || tree != before || actualAuthor != expectedAuthor || actualCommitter != text(identity["name"])+" <"+text(identity["email"])+">" {
		return blocked("commit 已生成，但 tree/身份后置核验失败；保留现场，先 Review，禁止推送", 3)
	}
	return nil
}

func Push(ctx context.Context, cwd, remote, branch string) (Object, error) {
	if !regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`).MatchString(remote) || !regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._/-]{0,160}$`).MatchString(branch) || strings.Contains(branch, "..") {
		return nil, blocked("invalid Git remote or branch", 2)
	}
	actual, e := gitRead(ctx, cwd, nil, "branch", "--show-current")
	if e != nil {
		return nil, e
	}
	if actual != branch {
		return nil, blocked("push 必须明确对应当前 checkout 的分支", 2)
	}
	head, e := gitRead(ctx, cwd, nil, "rev-parse", "HEAD")
	if e != nil {
		return nil, e
	}
	destinations, e := gitRead(ctx, cwd, nil, "remote", "get-url", "--push", "--all", remote)
	if e != nil {
		return nil, e
	}
	list := strings.Split(destinations, "\n")
	if len(list) != 1 || list[0] == "" || strings.HasPrefix(list[0], "-") {
		return nil, blocked("push 需要唯一明确目的地，不自动推送多个 pushurl", 2)
	}
	destination := list[0]
	u, e := url.Parse(destination)
	if e == nil && (u.Scheme == "http" || u.Scheme == "https") && u.User != nil {
		return nil, blocked("push URL 不得内嵌凭据，使用 Git credential helper", 2)
	}
	ref := "refs/heads/" + branch
	check := func() error {
		local, cancel := context.WithTimeout(ctx, 5*time.Second)
		defer cancel()
		rules, err := command(local, cwd, nil, 1<<20, "git", "config", "--null", "--get-regexp", `^url\..*\.(insteadof|pushinsteadof)$`)
		if err != nil && ErrorCode(err) != 1 {
			return blocked("无法核实 Git URL rewrite，未推送", 1)
		}
		for _, row := range strings.Split(string(rules), "\x00") {
			if row == "" {
				continue
			}
			_, value, _ := strings.Cut(row, "\n")
			if strings.HasPrefix(destination, value) {
				return blocked("实际 push URL 仍匹配 URL rewrite；先核对目的地，未推送", 2)
			}
		}
		aliases, err := gitRead(local, cwd, nil, "remote")
		if err != nil {
			return err
		}
		if contains(strings.Split(aliases, "\n"), destination) {
			return blocked("push URL 与 remote 别名重名，未推送", 2)
		}
		return nil
	}
	if e = check(); e != nil {
		return nil, e
	}
	remoteSHA := func() string {
		if check() != nil {
			return ""
		}
		local, cancel := context.WithTimeout(ctx, 30*time.Second)
		defer cancel()
		b, e := command(local, cwd, nil, 8192, "git", "ls-remote", "--exit-code", "--refs", destination, ref)
		if e != nil {
			return ""
		}
		fields := strings.Fields(string(b))
		if len(fields) == 2 && fields[1] == ref && regexp.MustCompile(`^(?:[0-9a-f]{40}|[0-9a-f]{64})$`).MatchString(fields[0]) {
			return fields[0]
		}
		return ""
	}
	base := remoteSHA()
	if base == "" {
		return nil, blocked("无法读取实际 push 目的分支，未推送", 1)
	}
	fetchCtx, cancel := context.WithTimeout(ctx, 2*time.Minute)
	_, e = command(fetchCtx, cwd, nil, 1<<20, "git", "fetch", "--no-tags", "--no-write-fetch-head", destination, base)
	cancel()
	if e != nil {
		return nil, blocked("无法获取实际 push 目的分支，未推送", 1)
	}
	if _, e = command(ctx, cwd, nil, 8192, "git", "--no-replace-objects", "merge-base", "--is-ancestor", base, head); e != nil {
		return nil, blocked("远端不是待推送 SHA 的祖先；先检查并集成，不强推", 3)
	}
	if e = check(); e != nil {
		return nil, e
	}
	pushCtx, cancel := context.WithTimeout(ctx, 2*time.Minute)
	_, pushErr := command(pushCtx, cwd, nil, 1<<20, "git", "push", "--porcelain", destination, head+":"+ref)
	cancel()
	var pushCode any = ErrorCode(pushErr)
	if errors.Is(pushErr, context.DeadlineExceeded) {
		pushCode = nil
	}
	report := Object{"status": "pushed-unverified", "remote": remote, "branch": branch, "head": head, "base": base, "fast_forward": true, "verified": false, "remote_sha": nil, "push_exit_code": pushCode, "exit_code": 1}
	sha := remoteSHA()
	if sha != "" {
		report["remote_sha"] = sha
	}
	if sha == head {
		report["status"], report["verified"], report["exit_code"] = "pushed", true, 0
		if pushErr != nil {
			report["transport_warning"] = "push-acknowledgement-lost-but-remote-sha-verified"
		}
	} else {
		report["reason"] = "remote-sha-unverified; query the original destination before any retry"
	}
	return report, nil
}
