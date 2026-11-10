package publicquality

import (
	"context"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"runtime/debug"
	"strings"
	"time"

	core "github.com/Everloster/EverAgent/packages/everagent-core"
)

const modulePath = "github.com/Everloster/EverAgent/packages/everagent-core"
const moduleDir = "packages/everagent-core"

type Step struct {
	ID              string `json:"id"`
	Status          string `json:"status"`
	Detail          string `json:"detail,omitempty"`
	PreserveScratch bool   `json:"preserve_scratch,omitempty"`
}
type GateResult struct {
	Mode            string        `json:"mode,omitempty"`
	SchemaVersion   int           `json:"schema_version"`
	OK              bool          `json:"ok"`
	Scope           string        `json:"scope"`
	Head            string        `json:"head"`
	Base            string        `json:"base"`
	IndexTree       string        `json:"index_tree"`
	Changed         int           `json:"changed_paths"`
	Reports         int           `json:"report_count"`
	Privacy         PrivacyResult `json:"privacy"`
	ReportAudit     *ReportAudit  `json:"report_audit,omitempty"`
	Context         *ContextAudit `json:"context,omitempty"`
	Steps           []Step        `json:"checks"`
	Findings        []Finding     `json:"findings"`
	RetainedScratch string        `json:"retained_scratch,omitempty"`
}

// Summary bounds routine CLI/commit output without dropping any checks. Full
// diagnostics remain available through ea-quality --details.
type GateSummary struct {
	Mode            string    `json:"mode,omitempty"`
	SchemaVersion   int       `json:"schema_version"`
	OK              bool      `json:"ok"`
	Scope           string    `json:"scope"`
	Head            string    `json:"head"`
	Base            string    `json:"base"`
	IndexTree       string    `json:"index_tree"`
	Changed         int       `json:"changed_paths"`
	Reports         int       `json:"report_count"`
	Steps           []Step    `json:"checks"`
	Errors          int       `json:"errors"`
	Warnings        int       `json:"warnings"`
	Findings        []Finding `json:"findings"`
	Omitted         int       `json:"omitted_findings"`
	Details         string    `json:"details_hint,omitempty"`
	RetainedScratch string    `json:"retained_scratch,omitempty"`
}

func (r GateResult) Summary() GateSummary {
	out := GateSummary{Mode: r.Mode, SchemaVersion: r.SchemaVersion, OK: r.OK, Scope: r.Scope, Head: r.Head,
		Base: r.Base, IndexTree: r.IndexTree, Changed: r.Changed, Reports: r.Reports, Steps: r.Steps,
		Findings: []Finding{}, RetainedScratch: r.RetainedScratch}
	for _, severity := range []string{"error", "warning"} {
		for _, finding := range r.Findings {
			if finding.Severity != severity {
				continue
			}
			if severity == "error" {
				out.Errors++
			} else {
				out.Warnings++
			}
			if len(out.Findings) < 16 {
				out.Findings = append(out.Findings, finding)
			}
		}
	}
	out.Omitted = len(r.Findings) - len(out.Findings)
	if out.Omitted > 0 {
		out.Details = "Use --details for all findings from the selected snapshot."
	}
	return out
}

func noErrors(findings []Finding) bool {
	for _, f := range findings {
		if f.Severity == "error" {
			return false
		}
	}
	return true
}

// Audit performs only deterministic reads of the captured snapshot. Report
// content changes do not trigger unrelated context audits or full Go tests.
func Audit(c *Candidate, full bool) GateResult {
	out := GateResult{SchemaVersion: 1, Scope: c.Scope, Head: c.Head, Base: c.Base, IndexTree: c.IndexTree,
		Changed: len(c.Changed), Steps: []Step{}, Findings: []Finding{}}
	add := func(id string, findings []Finding) {
		status := "passed"
		if !noErrors(findings) {
			status = "failed"
		}
		out.Steps = append(out.Steps, Step{ID: id, Status: status})
		out.Findings = append(out.Findings, findings...)
	}
	out.Privacy = AuditPrivacy(c, nil)
	add("public-content", out.Privacy.Findings)
	add("readme-links-and-media", CheckLinks(c.After, "README.md", true))
	reports, findings := Catalog(c.After)
	out.Reports = len(reports)
	add("report-catalog", findings)
	add("report-index", CheckIndex(c.After, reports))
	add("script-catalog", CheckScriptIndex(c.After))
	rules, err := LoadRules(c.After)
	if err != nil {
		add("report-policy", []Finding{issue(policyPath, "POLICY_UNAVAILABLE", err.Error())})
	} else {
		add("report-policy", nil)
		r := AuditReports(c, rules, reports, full || FullReportAuditRequired(c.Changed))
		out.ReportAudit = &r
		add("reports", r.Findings)
		if full || ContextRequired(c.Changed) {
			context := AuditContext(c.After, rules, reports)
			out.Context = &context
			add("context", context.Findings)
		} else if SamplingRequired(c.Changed) {
			add("review-sampling", rules.Sampling(reports).Findings)
		}
	}
	out.OK = noErrors(out.Findings)
	return out
}

type CheckOptions struct {
	Root, Scope, Base, TempRoot string
	Full                        bool
}

// CheckDisclosure is the sole automatic public-content check. It reads only
// changed public paths and does not load report policy, scan the catalog, run
// tests, execute models or depend on eacli/private checkouts.
func CheckDisclosure(ctx context.Context, options CheckOptions) (GateResult, error) {
	if options.Scope == "" {
		options.Scope = "index"
	}
	c, err := Capture(ctx, options.Root, options.Scope)
	if err != nil {
		return GateResult{}, err
	}
	defer c.Close()
	if options.Base != "" {
		if err = c.CompareBase(options.Base); err != nil {
			return GateResult{}, err
		}
	}
	p := AuditDisclosure(c)
	out := GateResult{Mode: "public-disclosure", SchemaVersion: 1, Scope: c.Scope,
		Head: c.Head, Base: c.Base, IndexTree: c.IndexTree, Changed: len(c.Changed),
		Privacy: p, Findings: p.Findings, Steps: []Step{}}
	if err = c.Verify(); err != nil {
		return out, err
	}
	out.OK = noErrors(out.Findings)
	status := "passed"
	if !out.OK {
		status = "failed"
	}
	out.Steps = append(out.Steps, Step{ID: "public-disclosure", Status: status})
	return out, nil
}

// Check remains an explicitly requested full audit, never a commit prerequisite.
// Scratch is external and any tests use the captured module.
func Check(ctx context.Context, options CheckOptions) (GateResult, error) {
	if options.Scope == "" {
		options.Scope = "index"
	}
	c, err := Capture(ctx, options.Root, options.Scope)
	if err != nil {
		return GateResult{}, err
	}
	defer c.Close()
	if options.Base != "" {
		if err = c.CompareBase(options.Base); err != nil {
			return GateResult{}, err
		}
	}
	out := Audit(c, options.Full)
	step := verifyBuildSources(c.After)
	out.Steps = append(out.Steps, step)
	if step.Status == "passed" && (options.Full || coreChanged(c.Changed)) {
		scratch, err := makeScratch(options.TempRoot, c.Root)
		if err != nil {
			return out, err
		}
		defer func() {
			if out.RetainedScratch == "" {
				_ = os.RemoveAll(scratch)
			}
		}()
		module, err := materializeModule(c.After, scratch)
		if err != nil {
			return out, err
		}
		env, err := checkEnvironment(ctx, scratch)
		if err != nil {
			if errors.Is(err, errProcessCleanup) {
				out.RetainedScratch = scratch
			}
			out.Steps = append(out.Steps, Step{ID: "core-environment", Status: "failed", Detail: err.Error()})
		} else {
			for _, verb := range []string{"test", "vet"} {
				args := []string{verb, "-mod=readonly"}
				if verb == "test" {
					args = append(args, "-count=1", "-timeout=120s")
				}
				args = append(args, "./...")
				step := goStep(ctx, module, "core-"+verb, env, args...)
				out.Steps = append(out.Steps, step)
				if step.PreserveScratch {
					out.RetainedScratch = scratch
					break
				}
				if ctx.Err() != nil {
					break
				}
			}
		}
	}
	if err := c.Verify(); err != nil {
		out.Steps = append(out.Steps, Step{ID: "snapshot-stability", Status: "failed", Detail: err.Error()})
	} else {
		out.Steps = append(out.Steps, Step{ID: "snapshot-stability", Status: "passed"})
	}
	for _, step := range out.Steps {
		out.OK = out.OK && step.Status == "passed"
	}
	return out, nil
}

func coreChanged(paths []string) bool {
	for _, p := range paths {
		if strings.HasPrefix(p, moduleDir+"/") || containsString([]string{"scripts/ecommit.sh", "scripts/hooks/pre-commit", "config/git-policy.json", "scripts/script-catalog.json"}, p) {
			return true
		}
	}
	return false
}

func makeScratch(parent, root string) (string, error) {
	if parent == "" {
		parent = os.TempDir()
	}
	parent, err := filepath.Abs(parent)
	if err == nil {
		parent, err = filepath.EvalSymlinks(parent)
	}
	if err != nil {
		return "", errors.New("scratch-parent-unavailable")
	}
	// Do not export candidate code into any checkout, including another repo
	// or a linked worktree selected through TMPDIR.
	for dir := parent; ; dir = filepath.Dir(dir) {
		if dir == root {
			return "", errors.New("scratch-inside-checkout")
		}
		if _, err := os.Lstat(filepath.Join(dir, ".git")); err == nil {
			return "", errors.New("scratch-inside-checkout")
		}
		if dir == filepath.Dir(dir) {
			break
		}
	}
	return os.MkdirTemp(parent, "everagent-public-gate-")
}

func materializeModule(s *Snapshot, scratch string) (string, error) {
	dir := filepath.Join(scratch, "module")
	total := 0
	for _, p := range s.Paths() {
		if !strings.HasPrefix(p, moduleDir+"/") {
			continue
		}
		// The retired interpreter implementation is not a Go build dependency.
		if strings.HasSuffix(p, ".py") || strings.HasSuffix(p, ".pyc") {
			continue
		}
		b, err := s.Bytes(p, TextLimit)
		if err != nil {
			return "", errors.New("snapshot-module-file-unreadable")
		}
		total += len(b)
		if total > 32<<20 {
			return "", errors.New("snapshot-module-budget-exceeded")
		}
		target := filepath.Join(dir, filepath.FromSlash(strings.TrimPrefix(p, moduleDir+"/")))
		if err := os.MkdirAll(filepath.Dir(target), 0700); err != nil {
			return "", err
		}
		if err := os.WriteFile(target, b, 0600); err != nil {
			return "", err
		}
	}
	return dir, nil
}

// Tests receive only toolchain essentials, existing Go caches and a disposable
// HOME. This prevents accidental use of the caller's sessions or credentials;
// it is not an OS sandbox for hostile repository code.
func checkEnvironment(ctx context.Context, scratch string) ([]string, error) {
	copyKeys := func(keys ...string) []string {
		out := []string{}
		for _, key := range keys {
			if value, ok := os.LookupEnv(key); ok {
				out = append(out, key+"="+value)
			}
		}
		return out
	}
	base := append(copyKeys("PATH", "SystemRoot", "WINDIR", "COMSPEC", "PATHEXT"),
		"GOTOOLCHAIN=local", "GOENV=off", "GOWORK=off", "GOFLAGS=", "GOPROXY=off", "GOSUMDB=off")
	// With GOENV disabled these are Go's documented environment/default
	// cache paths. Do not run even go env with the caller's real HOME: the
	// Go telemetry sidecar could outlive that query or use personal settings.
	caches := map[string]string{"GOCACHE": os.Getenv("GOCACHE"), "GOMODCACHE": os.Getenv("GOMODCACHE")}
	if caches["GOCACHE"] == "" {
		dir, err := os.UserCacheDir()
		if err != nil {
			return nil, errors.New("无法确定Go构建缓存；请显式设置GOCACHE。")
		}
		caches["GOCACHE"] = filepath.Join(dir, "go-build")
	}
	if caches["GOMODCACHE"] == "" {
		gopath := os.Getenv("GOPATH")
		if gopath == "" {
			dir, err := os.UserHomeDir()
			if err != nil {
				return nil, errors.New("无法确定Go模块缓存；请显式设置GOMODCACHE。")
			}
			gopath = filepath.Join(dir, "go")
		}
		paths := filepath.SplitList(gopath)
		if len(paths) == 0 || paths[0] == "" {
			return nil, errors.New("GOPATH首路径为空；请显式设置GOMODCACHE。")
		}
		caches["GOMODCACHE"] = filepath.Join(paths[0], "pkg", "mod")
	}
	for _, key := range []string{"GOCACHE", "GOMODCACHE"} {
		value := caches[key]
		info, err := os.Stat(value)
		if !filepath.IsAbs(value) || err != nil || !info.IsDir() {
			return nil, errors.New("Go检查需要已有的本地缓存目录：" + key)
		}
		base = append(base, key+"="+value)
	}
	home, temp := filepath.Join(scratch, "home"), filepath.Join(scratch, "tmp")
	for _, dir := range []string{home, temp} {
		if err := os.MkdirAll(dir, 0700); err != nil {
			return nil, errors.New("无法准备Go检查的临时环境。")
		}
	}
	env := append(base, "HOME="+home, "USERPROFILE="+home, "GOPATH="+filepath.Join(home, "go"),
		"XDG_CONFIG_HOME="+filepath.Join(home, ".config"), "XDG_DATA_HOME="+filepath.Join(home, ".local", "share"),
		"APPDATA="+filepath.Join(home, "AppData", "Roaming"), "LOCALAPPDATA="+filepath.Join(home, "AppData", "Local"),
		"TMPDIR="+temp, "TMP="+temp, "TEMP="+temp, "GIT_CONFIG_GLOBAL="+os.DevNull,
		"GIT_CONFIG_NOSYSTEM=1", "GIT_TERMINAL_PROMPT=0", "EACLI_TEST_SSH=0", "EACLI_TEST_CONTEXT_SSH=0")
	toolCtx, cancel := context.WithTimeout(ctx, 15*time.Second)
	defer cancel()
	// The official off command skips telemetry startup. Only disposable
	// settings are changed; no user-wide preference or undocumented flag.
	cmd := exec.CommandContext(toolCtx, "go", "telemetry", "off")
	cmd.Dir, cmd.Env, cmd.WaitDelay = scratch, env, time.Second
	if err := runCheckProcess(cmd); err != nil {
		return nil, errors.Join(errors.New("Go临时环境准备未完成；未运行源码测试。"), err)
	}
	return env, nil
}

var errProcessCleanup = errors.New("无法确认Go检查进程组已退出；保留临时目录，不自动继续。")

func goStep(ctx context.Context, module, id string, env []string, args ...string) Step {
	ctx, cancel := context.WithTimeout(ctx, 3*time.Minute)
	defer cancel()
	cmd := exec.CommandContext(ctx, "go", args...)
	cmd.Dir, cmd.Env, cmd.WaitDelay = module, env, time.Second
	output := &capped{limit: 8192}
	cmd.Stdout, cmd.Stderr = output, output
	step := Step{ID: id, Status: "passed"}
	if err := runCheckProcess(cmd); err != nil {
		step.Status = "failed"
		step.Detail = "Go检查未完成：" + strings.ReplaceAll(err.Error(), module, "<snapshot>") + "\n" + strings.ReplaceAll(output.String(), module, "<snapshot>")
		if ctx.Err() != nil {
			step.Detail = "Go检查超时或取消。"
		}
		if errors.Is(err, errProcessCleanup) {
			step.PreserveScratch = true
			step.Detail += "\n" + errProcessCleanup.Error()
		}
	}
	return step
}

func verifyBuildSources(s *Snapshot) Step {
	step := Step{ID: "gate-source-binding", Status: "failed"}
	info, ok := debug.ReadBuildInfo()
	if !ok || !containsString([]string{modulePath + "/cmd/ea-quality", modulePath + "/cmd/ea-git"}, info.Path) {
		step.Detail = "质量门须从本仓Go入口构建。"
		return step
	}
	settings := map[string]string{}
	for _, s := range info.Settings {
		settings[s.Key] = s.Value
	}
	if settings["-trimpath"] != "true" || settings["vcs.revision"] != "" || settings["-ldflags"] != "" || settings["-tags"] != "" || settings["-race"] != "" {
		step.Detail = "使用 go run -trimpath -buildvcs=false 的标准入口，不能跳过源码绑定。"
		return step
	}
	for _, dep := range info.Deps {
		if dep.Replace != nil {
			step.Detail = "质量门不能使用未绑定的依赖替换。"
			return step
		}
	}
	if err := compareBuildSources(s, core.BuildSourceHashes()); err != nil {
		step.Detail = err.Error()
		return step
	}
	step.Status = "passed"
	return step
}

func compareBuildSources(s *Snapshot, hashes map[string]string) error {
	for p, expected := range hashes {
		b, err := s.Bytes(moduleDir+"/"+p, TextLimit)
		if err != nil || digest(b) != expected {
			return errors.New("运行中质量门的源码/依赖锁不等于所审快照；先同步暂存源码并重新构建。")
		}
	}
	for _, p := range s.Paths() {
		if strings.HasPrefix(p, moduleDir+"/") && strings.HasSuffix(p, ".go") {
			if _, ok := hashes[strings.TrimPrefix(p, moduleDir+"/")]; !ok {
				return errors.New("所审快照包含当前构建未绑定的Go源码。")
			}
		}
	}
	return nil
}
