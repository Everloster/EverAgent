// ea-git binds the standalone public checkout to the shared identity/Git core
// and public quality owner. It neither reads nor requires the private checkout.
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
	"github.com/Everloster/EverAgent/packages/everagent-core/internal/publicquality"
)

func main() { os.Exit(run(os.Args[1:])) }

func run(args []string) int {
	f := flag.NewFlagSet("ea-git", flag.ContinueOnError)
	root := f.String("repo-root", "../..", "public checkout root")
	if err := f.Parse(args); err != nil || f.NArg() == 0 {
		fmt.Fprintln(os.Stderr, "ea-git [--repo-root <checkout>] commit <git-message-options> | validate")
		return 2
	}
	absolute, err := filepath.Abs(*root)
	if err == nil {
		absolute, err = filepath.EvalSymlinks(absolute)
	}
	if err != nil || os.Chdir(absolute) != nil {
		fmt.Fprintln(os.Stderr, "public checkout unavailable")
		return 1
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	reader := func() (core.Author, error) { return readAuthor(ctx, absolute) }
	switch f.Arg(0) {
	case "commit":
		err = core.Commit(ctx, f.Args()[1:], core.CommitOptions{
			Directory: absolute, IdentityReader: core.InspectIdentity, AuthorReader: reader,
			Preflight: func(target string, _ core.Object) error {
				if target != absolute {
					return errors.New("commit must target this public checkout")
				}
				return nil
			},
			Gate: func(ctx context.Context, target string, _ []string) error {
				ctx, cancel := context.WithTimeout(ctx, 10*time.Minute)
				defer cancel()
				result, e := publicquality.Check(ctx, publicquality.CheckOptions{Root: target, Scope: "index"})
				encoder := json.NewEncoder(os.Stderr)
				encoder.SetEscapeHTML(false)
				if encodeErr := encoder.Encode(result.Summary()); e == nil {
					e = encodeErr
				}
				if e == nil && !result.OK {
					e = errors.New("public quality gate did not pass")
				}
				return e
			},
		})
	case "validate":
		if f.NArg() != 1 {
			return 2
		}
		expected, e := reader()
		if e != nil {
			err = e
			break
		}
		committer, e1 := gitIdent(ctx, absolute, "GIT_COMMITTER_IDENT")
		author, e2 := gitIdent(ctx, absolute, "GIT_AUTHOR_IDENT")
		if e1 != nil || e2 != nil {
			err = errors.New("Git identity unavailable")
			break
		}
		if issues := core.ValidateIdentity(core.InspectIdentity(), committer, author, expected); len(issues) > 0 {
			err = errors.New(strings.Join(issues, "; "))
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
