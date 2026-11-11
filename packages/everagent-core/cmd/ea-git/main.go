// ea-git binds the public Author, verified Committer and public-content checks.
// Commit/merge/push do not require eacli/private checkouts or report quality gates.
// Optional project hooks delegate identity checks to the installed eacli.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	core "github.com/Everloster/EverAgent/packages/everagent-core"
	"github.com/Everloster/EverAgent/packages/everagent-core/internal/projecthooks"
	"github.com/Everloster/EverAgent/packages/everagent-core/internal/publicquality"
)

func main() { os.Exit(run(os.Args[1:])) }

func run(args []string) int {
	f := flag.NewFlagSet("ea-git", flag.ContinueOnError)
	root := f.String("repo-root", "../..", "explicit checkout root")
	if err := f.Parse(args); err != nil || f.NArg() == 0 {
		fmt.Fprintln(os.Stderr, "ea-git [--repo-root <checkout>] commit <options> | merge <revision> | push [--remote origin] [--branch main] | validate | hooks install [--adopt-legacy] | hooks status")
		return 2
	}
	absolute, err := filepath.Abs(*root)
	if err == nil {
		absolute, err = filepath.EvalSymlinks(absolute)
	}
	if err != nil || os.Chdir(absolute) != nil {
		fmt.Fprintln(os.Stderr, "checkout unavailable")
		return 1
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	reader := func() (core.Author, error) { return readAuthor(ctx, absolute) }
	switch f.Arg(0) {
	case "hooks":
		return projecthooks.Run(ctx, absolute, f.Args()[1:], os.Stdout)
	case "commit", "merge":
		options := core.CommitOptions{
			IdentityOnly: true, EnforceAuthor: true, Directory: absolute, IdentityReader: core.InspectIdentity, AuthorReader: reader,
			ContentGuard: func(ctx context.Context, target string, _ []string) error {
				if target != absolute {
					return errors.New("commit must target this public checkout")
				}
				ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
				defer cancel()
				result, e := publicquality.CheckDisclosure(ctx, publicquality.CheckOptions{Root: target, Scope: "index"})
				encoder := json.NewEncoder(os.Stderr)
				encoder.SetEscapeHTML(false)
				if encodeErr := encoder.Encode(result.Summary()); e == nil {
					e = encodeErr
				}
				if e == nil && !result.OK {
					e = errors.New("new public content contains a disclosure blocker")
				}
				return e
			},
		}
		if f.Arg(0) == "merge" {
			if f.NArg() != 2 {
				return 2
			}
			err = core.Merge(ctx, f.Arg(1), options)
		} else {
			err = core.Commit(ctx, f.Args()[1:], options)
		}
	case "push":
		flags := flag.NewFlagSet("push", flag.ContinueOnError)
		remote := flags.String("remote", "origin", "exact remote")
		branch := flags.String("branch", "", "current branch")
		if flags.Parse(f.Args()[1:]) != nil || flags.NArg() != 0 {
			return 2
		}
		if *branch == "" {
			checkout, _ := core.Checkout(absolute)
			*branch, _ = checkout["branch"].(string)
		}
		policy, policyErr := readPushPolicy(ctx, absolute)
		if policyErr != nil {
			err = policyErr
			break
		}
		var report core.Object
		report, err = core.PushWithGuard(ctx, absolute, *remote, *branch, func(ctx context.Context, root, base, head string) error {
			return core.CheckPushIdentities(ctx, root, base, head, policy)
		})
		if report != nil {
			_ = json.NewEncoder(os.Stdout).Encode(report)
		}
	case "validate":
		if f.NArg() != 1 {
			return 2
		}
		identity := core.InspectIdentity()
		if err = core.ValidIdentity(identity); err != nil {
			break
		}
		committer, e := gitIdent(ctx, absolute, "GIT_COMMITTER_IDENT")
		if e != nil {
			err = e
			break
		}
		if committer.Name != identity["name"] || committer.Email != identity["email"] {
			err = errors.New("Git Committer does not match the current Agent/model")
			break
		}
		expected, e := reader()
		if e != nil {
			err = e
			break
		}
		author, e := gitIdent(ctx, absolute, "GIT_AUTHOR_IDENT")
		if e != nil || author != expected {
			err = errors.New("Git Author does not match the repository owner")
		}
	default:
		return 2
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
	return core.ErrorCode(err)
}

func readAuthor(ctx context.Context, root string) (core.Author, error) {
	c, err := publicquality.Capture(ctx, root, "index")
	if err != nil {
		return core.Author{}, err
	}
	defer c.Close()
	policy, err := publicquality.JSON(c.After, "config/git-policy.json")
	if err != nil || fmt.Sprint(policy["schema_version"]) != "1" {
		return core.Author{}, errors.New("repository author policy unavailable")
	}
	row, ok := policy["author"].(map[string]any)
	if !ok {
		return core.Author{}, errors.New("repository author policy invalid")
	}
	name, _ := row["name"].(string)
	email, _ := row["email"].(string)
	if strings.TrimSpace(name) == "" || strings.ContainsAny(name, "\r\n<>") || !regexp.MustCompile(`^[^\s<>@]+@[^\s<>@]+$`).MatchString(email) {
		return core.Author{}, errors.New("repository author policy invalid")
	}
	return core.Author{Name: name, Email: email}, c.Verify()
}

func readPushPolicy(ctx context.Context, root string) (core.PushIdentityPolicy, error) {
	c, err := publicquality.Capture(ctx, root, "head")
	if err != nil {
		return core.PushIdentityPolicy{}, err
	}
	defer c.Close()
	value, err := publicquality.JSON(c.After, "config/git-policy.json")
	if err != nil {
		return core.PushIdentityPolicy{}, errors.New("committed push identity policy unavailable")
	}
	raw, err := json.Marshal(value)
	var policy struct {
		Schema    int         `json:"schema_version"`
		Author    core.Author `json:"author"`
		Forbidden []string    `json:"forbidden_commits"`
	}
	if err != nil || json.Unmarshal(raw, &policy) != nil || policy.Schema != 1 {
		return core.PushIdentityPolicy{}, errors.New("committed push identity policy invalid")
	}
	return core.PushIdentityPolicy{Author: policy.Author, ForbiddenCommits: policy.Forbidden}, c.Verify()
}

func gitIdent(ctx context.Context, root, variable string) (core.Author, error) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "git", "-C", root, "var", variable)
	cmd.WaitDelay = time.Second
	data, err := cmd.Output()
	if err != nil || len(data) > 4096 {
		return core.Author{}, errors.New("Git identity read failed")
	}
	m := regexp.MustCompile(`^([^\r\n<>]+) <([^\r\n<>]+)> [0-9]+ [-+][0-9]{4}\s*$`).FindStringSubmatch(string(data))
	if m == nil {
		return core.Author{}, errors.New("Git identity invalid")
	}
	return core.Author{Name: m[1], Email: m[2]}, nil
}
