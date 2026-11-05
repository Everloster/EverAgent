package core

import (
	"context"
	"errors"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func testGit(t *testing.T, cwd string, args ...string) string {
	t.Helper()
	b, err := boundedCommand(cwd, nil, 10*time.Second, 1<<20, append([]string{"git"}, args...)...)
	if err != nil {
		t.Fatalf("git %v: %v; output=%s", args, err, b)
	}
	return strings.TrimSpace(string(b))
}

func gitFixture(t *testing.T) (string, CommitOptions) {
	t.Helper()
	// Real Git, but no user's hooks, signing defaults, index or global identity.
	t.Setenv("GIT_CONFIG_GLOBAL", os.DevNull)
	t.Setenv("GIT_CONFIG_NOSYSTEM", "1")
	t.Setenv("GIT_CONFIG_COUNT", "0")
	// An empty GIT_DIR/INDEX_FILE is still a path override, not an unset key.
	for _, key := range []string{"GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"} {
		t.Setenv(key, "") // testing restores the original value on cleanup.
		if err := os.Unsetenv(key); err != nil {
			t.Fatal(err)
		}
	}
	dir := realPath(t.TempDir())
	testGit(t, dir, "init", "--initial-branch=main")
	writeFixture(t, filepath.Join(dir, "tracked.txt"), []byte("staged\n"), time.Now())
	testGit(t, dir, "add", "tracked.txt")
	identity := Object{"resolved": true, "name": "codex-fixture-model", "email": "noreply@openai.com", "cli": "codex",
		"model": "fixture-model", "model_source": "codex-turn-context", "model_confidence": "session-bound",
		"current_model_confirmed": true, "user_model_declared": false, "scope_ref": "fixture-scope", "observation_ref": "fixture-turn"}
	options := CommitOptions{Directory: dir, IdentityReader: func() Object { return clone(identity) },
		AuthorReader: func() (Author, error) { return Author{"Fixture Owner", "owner@example.invalid"}, nil },
		Gate:         func(context.Context, string, []string) error { return nil }, Stdin: strings.NewReader(""), Stdout: io.Discard, Stderr: io.Discard}
	return dir, options
}

func fixtureMessage(subject string) string { return subject + "\n\nCo-Authored-By: Aiden\n" }

func TestCommitOnlyStagedTreeAndIdentity(t *testing.T) {
	dir, options := gitFixture(t)
	writeFixture(t, filepath.Join(dir, "tracked.txt"), []byte("unstaged\n"), time.Now())
	message := fixtureMessage("[maintenance] fixture: 校验提交树与身份")
	if err := Commit(context.Background(), []string{"-m", message, "--trailer", "Reviewed-by: Fixture"}, options); err != nil {
		t.Fatal(err)
	}
	if body := testGit(t, dir, "show", "HEAD:tracked.txt"); body != "staged" {
		t.Fatalf("unstaged content was committed: %s", body)
	}
	if who := testGit(t, dir, "show", "-s", "--format=%an <%ae>|%cn <%ce>", "HEAD"); who != "Fixture Owner <owner@example.invalid>|codex-fixture-model <noreply@openai.com>" {
		t.Fatalf("incorrect authorship: %s", who)
	}
	actual := testGit(t, dir, "show", "-s", "--format=%B", "HEAD")
	if !strings.Contains(actual, "Reviewed-by: Fixture") || strings.Count(actual, "Co-Authored-By: Aiden") != 1 {
		t.Fatalf("lost or duplicated trailers: %s", actual)
	}
	if err := Commit(context.Background(), []string{"--amend", "--no-edit"}, options); err != nil {
		t.Fatal(err)
	}
	if after := testGit(t, dir, "show", "-s", "--format=%B", "HEAD"); after != actual {
		t.Fatal("amend changed the caller's message")
	}
}

func TestCommitRejectsContentModesBeforeGate(t *testing.T) {
	_, options := gitFixture(t)
	options.Gate = func(context.Context, string, []string) error {
		t.Fatal("invalid arguments reached the gate")
		return nil
	}
	options.IdentityReader = func() Object { t.Fatal("invalid arguments reached identity detection"); return nil }
	for _, args := range [][]string{{"--all"}, {"--", "tracked.txt"}, {"-i", "tracked.txt"}, {"--only"}, {"--reset-author"}, {"--fixup", "HEAD"}} {
		if err := Commit(context.Background(), args, options); ErrorCode(err) != 2 {
			t.Fatalf("accepted content mode %v: %v", args, err)
		}
	}
}

func TestCommitGateAndEvidenceFailures(t *testing.T) {
	for _, tc := range []string{"configured-model", "failed-gate", "index-changed", "model-changed", "author-changed", "claude-progress", "post-hook-tree"} {
		t.Run(tc, func(t *testing.T) {
			dir, options := gitFixture(t)
			identity := options.IdentityReader()
			options.IdentityReader = func() Object { return clone(identity) }
			switch tc {
			case "configured-model":
				identity["current_model_confirmed"], identity["model_confidence"] = false, "configured"
				options.Gate = func(context.Context, string, []string) error { t.Fatal("unverified model reached gate"); return nil }
			case "failed-gate":
				options.Gate = func(context.Context, string, []string) error { return errors.New("gate failed") }
			case "index-changed":
				options.Gate = func(context.Context, string, []string) error {
					writeFixture(t, filepath.Join(dir, "tracked.txt"), []byte("changed-during-gate"), time.Now())
					testGit(t, dir, "add", "tracked.txt")
					return nil
				}
			case "model-changed":
				options.Gate = func(context.Context, string, []string) error { identity["model"] = "new-model"; return nil }
			case "author-changed":
				reader := options.AuthorReader
				options.AuthorReader = func() (Author, error) { return reader() }
				options.Gate = func(context.Context, string, []string) error {
					reader = func() (Author, error) { return Author{"Changed", "owner@example.invalid"}, nil }
					return nil
				}
			case "claude-progress":
				identity["cli"], identity["model_source"] = "claude-code", "claude-session-runtime"
				identity["scope_ref"], identity["observation_ref"] = strings.Repeat("a", 24), strings.Repeat("b", 24)
				options.Gate = func(context.Context, string, []string) error {
					identity["observation_ref"] = strings.Repeat("c", 24)
					return nil
				}
			case "post-hook-tree":
				// Simulate an external pre-commit hook which changes the index.
				git := testGit(t, dir, "rev-parse", "--git-dir")
				path := filepath.Join(dir, git, "hooks/pre-commit")
				writeFixture(t, path, []byte("#!/bin/sh\nprintf 'hook-mutated' > tracked.txt\ngit add tracked.txt\n"), time.Now())
				if err := os.Chmod(path, 0700); err != nil {
					t.Fatal(err)
				}
			}
			err := Commit(context.Background(), []string{"-m", fixtureMessage("[maintenance] fixture: 门禁边界")}, options)
			if tc == "claude-progress" {
				if err != nil {
					t.Fatalf("same Claude session progressing invalidated signature: %v", err)
				}
			} else if err == nil {
				t.Fatalf("%s did not block", tc)
			}
			_, headErr := boundedCommand(dir, nil, time.Second, 1024, "git", "rev-parse", "--verify", "HEAD")
			if tc != "claude-progress" && tc != "post-hook-tree" && headErr == nil {
				t.Fatal("failed gate/evidence generated a commit")
			}
		})
	}
}

func TestPushReadsActualDestination(t *testing.T) {
	dir, options := gitFixture(t)
	if err := Commit(context.Background(), []string{"-m", fixtureMessage("[maintenance] fixture: 初始提交")}, options); err != nil {
		t.Fatal(err)
	}
	fetch, target := filepath.Join(t.TempDir(), "fetch.git"), filepath.Join(t.TempDir(), "push.git")
	testGit(t, dir, "clone", "--bare", dir, fetch)
	testGit(t, dir, "clone", "--bare", dir, target)
	base := testGit(t, dir, "rev-parse", "HEAD")
	testGit(t, dir, "remote", "add", "origin", fetch)
	testGit(t, dir, "remote", "set-url", "--push", "origin", target)
	writeFixture(t, filepath.Join(dir, "tracked.txt"), []byte("next"), time.Now())
	testGit(t, dir, "add", "tracked.txt")
	if err := Commit(context.Background(), []string{"-m", fixtureMessage("[maintenance] fixture: 实际目的地")}, options); err != nil {
		t.Fatal(err)
	}
	v, err := Push(context.Background(), dir, "origin", "main")
	if err != nil || v["verified"] != true || v["head"] != testGit(t, target, "rev-parse", "main") {
		t.Fatalf("push verification: %v %v", v, err)
	}
	if testGit(t, fetch, "rev-parse", "main") != base {
		t.Fatal("fetch destination changed instead of pushurl")
	}
	testGit(t, dir, "remote", "set-url", "--add", "--push", "origin", fetch)
	if _, err := Push(context.Background(), dir, "origin", "main"); err == nil {
		t.Fatal("multiple push destinations accepted")
	}
}

func TestIdentityEnvironmentPreservesGitConfig(t *testing.T) {
	_, options := gitFixture(t)
	author, _ := options.AuthorReader()
	env, err := IdentityEnvironment(options.IdentityReader(), []string{"GIT_CONFIG_COUNT=1", "GIT_CONFIG_KEY_0=core.filemode", "GIT_CONFIG_VALUE_0=false", "HOME=/fixture"}, author)
	if err != nil {
		t.Fatal(err)
	}
	joined := "\n" + strings.Join(env, "\n") + "\n"
	for _, entry := range []string{"GIT_CONFIG_COUNT=3", "GIT_CONFIG_KEY_0=core.filemode", "GIT_CONFIG_VALUE_0=false", "HOME=/fixture"} {
		if !strings.Contains(joined, "\n"+entry+"\n") {
			t.Fatalf("lost process-local configuration: %s", entry)
		}
	}
	if _, err := exec.LookPath("git"); err != nil {
		t.Fatal(err)
	}
}
