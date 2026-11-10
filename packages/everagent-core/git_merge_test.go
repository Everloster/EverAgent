package core

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func mergeFixture(t *testing.T, divergent, conflict bool) (string, string, string, CommitOptions) {
	t.Helper()
	dir, options := gitFixture(t)
	testGit(t, dir, "commit", "-m", "base")
	testGit(t, dir, "switch", "-c", "topic")
	path := "topic.txt"
	if conflict {
		path = "tracked.txt"
	}
	writeFixture(t, filepath.Join(dir, path), []byte("topic\n"), time.Now())
	testGit(t, dir, "add", path)
	testGit(t, dir, "commit", "-m", "topic")
	target := testGit(t, dir, "rev-parse", "HEAD")
	testGit(t, dir, "switch", "main")
	if divergent {
		path = "main.txt"
		if conflict {
			path = "tracked.txt"
		}
		writeFixture(t, filepath.Join(dir, path), []byte("main\n"), time.Now())
		testGit(t, dir, "add", path)
		testGit(t, dir, "commit", "-m", "main")
	}
	head := testGit(t, dir, "rev-parse", "HEAD")
	options.IdentityOnly = true
	options.Gate = func(context.Context, string, []string) error { t.Fatal("quality gate ran"); return nil }
	options.Preflight = func(string, Object) error { t.Fatal("preflight ran"); return nil }
	return dir, head, target, options
}

func TestMergeFastForwardAndUpToDate(t *testing.T) {
	dir, _, target, options := mergeFixture(t, false, false)
	testGit(t, dir, "config", "merge.ff", "false")
	testGit(t, dir, "config", "branch.main.mergeOptions", "--no-ff --squash --autostash")
	options.IdentityReader, options.AuthorReader = nil, nil
	for _, key := range []string{"GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL"} {
		if err := os.Unsetenv(key); err != nil {
			t.Fatal(err)
		}
	}
	t.Setenv("GIT_CONFIG_COUNT", "1")
	t.Setenv("GIT_CONFIG_KEY_0", "user.useConfigOnly")
	t.Setenv("GIT_CONFIG_VALUE_0", "true")
	options.ContentGuard = func(context.Context, string, []string) error { t.Fatal("no commit needs no content guard"); return nil }
	count := testGit(t, dir, "rev-list", "--all", "--count")
	for i := 0; i < 2; i++ {
		if err := Merge(context.Background(), "topic", options); err != nil {
			t.Fatal(err)
		}
		if testGit(t, dir, "rev-parse", "HEAD") != target || testGit(t, dir, "rev-list", "--all", "--count") != count {
			t.Fatal("fast-forward/up-to-date created or selected a different commit")
		}
	}
}

func TestMergeDivergentUsesCommitPolicyAndExactTarget(t *testing.T) {
	for _, quality := range []bool{false, true} {
		t.Run(map[bool]string{false: "identity-only", true: "quality"}[quality], func(t *testing.T) {
			dir, head, target, options := mergeFixture(t, true, false)
			testGit(t, dir, "config", "merge.ff", "only")
			testGit(t, dir, "config", "branch.main.mergeOptions", "--ff-only --squash --commit")
			identities, authors, guards, gates := 0, 0, 0, 0
			readIdentity, readAuthor := options.IdentityReader, options.AuthorReader
			options.IdentityReader = func() Object {
				identities++
				if identities == 1 {
					// The symbolic target moves after it was resolved. It must not be
					// resolved again, either for the merge or its parent verification.
					tree := testGit(t, dir, "rev-parse", "topic^{tree}")
					newTarget := testGit(t, dir, "commit-tree", tree, "-p", target, "-m", "moved target")
					testGit(t, dir, "update-ref", "refs/heads/topic", newTarget)
				}
				return readIdentity()
			}
			options.AuthorReader = func() (Author, error) { authors++; return readAuthor() }
			options.ContentGuard = func(ctx context.Context, cwd string, env []string) error {
				guards++
				if cwd != dir || !contains(env, "GIT_AUTHOR_EMAIL=owner@example.invalid") || !contains(env, "GIT_COMMITTER_EMAIL=noreply@openai.com") {
					t.Fatal("content guard lost the merge's double identity")
				}
				for _, path := range []string{"main.txt", "topic.txt"} {
					if _, err := gitRead(ctx, cwd, env, "show", ":"+path); err != nil {
						t.Fatal("guard did not see merged index", err)
					}
				}
				return nil
			}
			if quality {
				options.IdentityOnly = false
				options.Preflight = nil
				options.Gate = func(context.Context, string, []string) error { gates++; return nil }
			}
			if err := Merge(context.Background(), "topic", options); err != nil {
				t.Fatal(err)
			}
			if testGit(t, dir, "show", "-s", "--format=%P") != head+" "+target {
				t.Fatal("merge did not use the one resolved target")
			}
			if testGit(t, dir, "show", "-s", "--format=%an <%ae>|%cn <%ce>") != "Fixture Owner <owner@example.invalid>|codex-fixture-model <noreply@openai.com>" {
				t.Fatal("merge lost final double identity")
			}
			if !quality && (identities != 1 || authors != 2 || guards != 1 || gates != 0) || quality && (identities != 2 || authors != 3 || gates != 1 || guards != 0) {
				t.Fatalf("unexpected policy calls: identities=%d authors=%d guards=%d gates=%d", identities, authors, guards, gates)
			}
			if testGit(t, dir, "status", "--porcelain") != "" || testGit(t, dir, "config", "merge.ff") != "only" {
				t.Fatal("merge left dirty state or mutated config")
			}
		})
	}
}

func TestMergeInvalidAuthorDoesNotPrepareState(t *testing.T) {
	for _, scenario := range []string{"missing", "unavailable", "empty", "bad-name", "bad-email"} {
		t.Run(scenario, func(t *testing.T) {
			dir, head, target, options := mergeFixture(t, true, false)
			tree := testGit(t, dir, "write-tree")
			switch scenario {
			case "missing":
				options.AuthorReader = nil
			case "unavailable":
				options.AuthorReader = func() (Author, error) { return Author{}, errors.New("private@example.invalid unavailable") }
			case "empty":
				options.AuthorReader = func() (Author, error) { return Author{}, nil }
			case "bad-name":
				options.AuthorReader = func() (Author, error) { return Author{"Bad <Name>", "private@example.invalid"}, nil }
			case "bad-email":
				options.AuthorReader = func() (Author, error) { return Author{"Owner", "invalid-email"}, nil }
			}
			err := Merge(context.Background(), "topic", options)
			if ErrorCode(err) != 1 || strings.Contains(err.Error(), "@") {
				t.Fatal("invalid pre-merge Author did not fail privately", err)
			}
			if testGit(t, dir, "rev-parse", "HEAD") != head || testGit(t, dir, "rev-parse", "topic") != target || testGit(t, dir, "write-tree") != tree || testGit(t, dir, "status", "--porcelain") != "" {
				t.Fatal("invalid pre-merge Author changed checkout state")
			}
			for _, name := range []string{"MERGE_HEAD", "MERGE_MSG", "ORIG_HEAD"} {
				if _, err := os.Lstat(filepath.Join(dir, ".git", name)); !os.IsNotExist(err) {
					t.Fatalf("invalid pre-merge Author created %s", name)
				}
			}
		})
	}
}

func TestMergeRejectsIncomingAuthorPolicyDrift(t *testing.T) {
	for _, quality := range []bool{false, true} {
		t.Run(map[bool]string{false: "identity-only", true: "quality"}[quality], func(t *testing.T) {
			dir, head, target, options := mergeFixture(t, true, false)
			options.IdentityOnly = !quality
			options.ContentGuard = func(context.Context, string, []string) error { t.Fatal("author drift reached guard"); return nil }
			read, calls := options.AuthorReader, 0
			options.AuthorReader = func() (Author, error) {
				calls++
				// Incoming tracked content changes repository-derived policy.
				if _, err := os.Stat(filepath.Join(dir, "topic.txt")); err == nil {
					return Author{"Changed Owner", "changed@example.invalid"}, nil
				} else if !os.IsNotExist(err) {
					t.Fatal(err)
				}
				return read()
			}
			err := Merge(context.Background(), "topic", options)
			if ErrorCode(err) != 3 || !strings.Contains(err.Error(), "author policy changed") || strings.Contains(err.Error(), "@") || calls != 2 {
				t.Fatal("incoming Author policy was adopted or failure was not private", err)
			}
			if testGit(t, dir, "rev-parse", "HEAD") != head || testGit(t, dir, "rev-parse", "MERGE_HEAD") != target || testGit(t, dir, "show", ":topic.txt") != "topic" || testGit(t, dir, "show", ":main.txt") != "main" {
				t.Fatal("author drift committed or discarded the prepared merge")
			}
		})
	}
}

func TestMergePreparationUsesExpectedAuthor(t *testing.T) {
	dir, head, target, options := mergeFixture(t, true, true)
	writeFixture(t, filepath.Join(dir, ".git", "info", "attributes"), []byte("tracked.txt merge=fixture\n"), time.Now())
	writeFixture(t, filepath.Join(dir, ".git", "capture-merge.sh"), []byte("#!/bin/sh\nprintf '%s <%s>|%s <%s>' \"$GIT_AUTHOR_NAME\" \"$GIT_AUTHOR_EMAIL\" \"$GIT_COMMITTER_NAME\" \"$GIT_COMMITTER_EMAIL\" > .git/merge-identity\nexit 1\n"), time.Now())
	testGit(t, dir, "config", "merge.fixture.driver", "sh .git/capture-merge.sh")
	if err := Merge(context.Background(), "topic", options); err == nil {
		t.Fatal("fixture merge driver did not leave a conflict")
	}
	b, err := os.ReadFile(filepath.Join(dir, ".git", "merge-identity"))
	if err != nil || string(b) != "Fixture Owner <owner@example.invalid>|codex-fixture-model <noreply@openai.com>" {
		t.Fatal("merge preparation did not receive the expected double identity", err)
	}
	if testGit(t, dir, "rev-parse", "HEAD") != head || testGit(t, dir, "rev-parse", "MERGE_HEAD") != target {
		t.Fatal("merge driver conflict state was not retained")
	}
}

func TestMergeRefusesDirtyOrExistingOperation(t *testing.T) {
	for _, scenario := range []string{"staged", "unstaged", "untracked", "intent-to-add", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer", "alternate-index"} {
		t.Run(scenario, func(t *testing.T) {
			dir, head, target, options := mergeFixture(t, true, false)
			switch scenario {
			case "staged", "untracked", "intent-to-add":
				writeFixture(t, filepath.Join(dir, "unrelated.txt"), []byte("do not commit"), time.Now())
				if scenario == "staged" {
					testGit(t, dir, "add", "unrelated.txt")
				} else if scenario == "intent-to-add" {
					testGit(t, dir, "add", "-N", "unrelated.txt")
				}
			case "unstaged":
				writeFixture(t, filepath.Join(dir, "tracked.txt"), []byte("do not overwrite"), time.Now())
			case "alternate-index":
				t.Setenv("GIT_INDEX_FILE", filepath.Join(t.TempDir(), "index"))
				testGit(t, dir, "read-tree", "HEAD")
			default:
				writeFixture(t, filepath.Join(dir, ".git", scenario), []byte(target+"\n"), time.Now())
			}
			before := testGit(t, dir, "status", "--porcelain")
			options.IdentityReader = func() Object { t.Fatal("dirty merge reached identity reader"); return nil }
			if err := Merge(context.Background(), "topic", options); err == nil {
				t.Fatal("dirty or existing operation accepted")
			}
			if testGit(t, dir, "rev-parse", "HEAD") != head || testGit(t, dir, "status", "--porcelain") != before {
				t.Fatal("refused merge changed user state")
			}
		})
	}
}

func TestMergeRefusesInvalidTarget(t *testing.T) {
	dir, head, _, options := mergeFixture(t, true, false)
	options.IdentityReader = func() Object { t.Fatal("invalid target reached identity reader"); return nil }
	for _, target := range []string{"", "  ", "--abort", "--ff-only", "missing", "HEAD^{tree}"} {
		if err := Merge(context.Background(), target, options); err == nil {
			t.Fatalf("accepted target %q", target)
		}
	}
	if testGit(t, dir, "rev-parse", "HEAD") != head {
		t.Fatal("invalid target changed HEAD")
	}
}

func TestMergeRetainsConflictsAndPolicyFailures(t *testing.T) {
	for _, scenario := range []string{"conflict", "guard", "author-policy"} {
		t.Run(scenario, func(t *testing.T) {
			dir, head, target, options := mergeFixture(t, true, scenario == "conflict")
			options.ContentGuard = func(context.Context, string, []string) error { return errors.New("disclosure refused") }
			if scenario == "author-policy" {
				read, calls := options.AuthorReader, 0
				options.AuthorReader = func() (Author, error) {
					calls++
					if calls > 1 {
						return Author{}, errors.New("private@example.invalid missing")
					}
					return read()
				}
			}
			err := Merge(context.Background(), "topic", options)
			if err == nil || strings.Contains(err.Error(), "@") || testGit(t, dir, "rev-parse", "HEAD") != head || testGit(t, dir, "rev-parse", "MERGE_HEAD") != target {
				t.Fatal("merge failure committed, aborted, or disclosed policy", err)
			}
			if scenario == "conflict" && testGit(t, dir, "ls-files", "--unmerged") == "" {
				t.Fatal("conflict state was not retained")
			}
		})
	}
}

func TestMergeRefusesStateRaces(t *testing.T) {
	for _, scenario := range []string{"before-merge-index", "before-merge-head", "before-merge-branch", "prepared-index", "prepared-head", "prepared-branch", "prepared-parents", "quality-index"} {
		t.Run(scenario, func(t *testing.T) {
			dir, head, target, options := mergeFixture(t, true, false)
			mutate := func() {
				switch {
				case strings.HasSuffix(scenario, "index"):
					writeFixture(t, filepath.Join(dir, "unrelated.txt"), []byte("racing staged work"), time.Now())
					testGit(t, dir, "add", "unrelated.txt")
				case strings.HasSuffix(scenario, "head"):
					testGit(t, dir, "update-ref", "HEAD", target)
				case strings.HasSuffix(scenario, "branch"):
					testGit(t, dir, "branch", "other", head)
					testGit(t, dir, "symbolic-ref", "HEAD", "refs/heads/other")
				case strings.HasSuffix(scenario, "parents"):
					writeFixture(t, filepath.Join(dir, ".git", "MERGE_HEAD"), []byte(head+"\n"), time.Now())
				}
			}
			if strings.HasPrefix(scenario, "before-merge") {
				read := options.IdentityReader
				options.IdentityReader = func() Object { mutate(); return read() }
			} else if scenario == "quality-index" {
				options.IdentityOnly = false
				options.Gate = func(context.Context, string, []string) error { return nil }
				options.Preflight = func(string, Object) error { mutate(); return nil }
			} else {
				read, calls := options.AuthorReader, 0
				options.AuthorReader = func() (Author, error) {
					calls++
					if calls > 1 {
						mutate()
					}
					return read()
				}
			}
			if err := Merge(context.Background(), "topic", options); ErrorCode(err) != 3 {
				t.Fatal("merge state race did not fail closed", err)
			}
			if testGit(t, dir, "rev-list", "--all", "--not", head, target) != "" {
				t.Fatal("merge state race produced a commit")
			}
		})
	}
}

func TestMergeDoesNotOverwriteIgnoredFiles(t *testing.T) {
	dir, head, _, options := mergeFixture(t, false, false)
	writeFixture(t, filepath.Join(dir, ".git", "info", "exclude"), []byte("topic.txt\n"), time.Now())
	writeFixture(t, filepath.Join(dir, "topic.txt"), []byte("private ignored work"), time.Now())
	if err := Merge(context.Background(), "topic", options); err == nil {
		t.Fatal("merge overwrote ignored work")
	}
	b, err := os.ReadFile(filepath.Join(dir, "topic.txt"))
	if err != nil || string(b) != "private ignored work" || testGit(t, dir, "rev-parse", "HEAD") != head {
		t.Fatal("ignored work or HEAD changed", err)
	}
}

func TestMergeChecksPostHookTree(t *testing.T) {
	dir, head, target, options := mergeFixture(t, true, false)
	path := filepath.Join(dir, ".git", "hooks", "pre-commit")
	writeFixture(t, path, []byte("#!/bin/sh\nprintf unrelated > unrelated.txt\ngit add unrelated.txt\n"), time.Now())
	if err := os.Chmod(path, 0700); err != nil {
		t.Fatal(err)
	}
	if err := Merge(context.Background(), "topic", options); ErrorCode(err) != 3 {
		t.Fatal("hook mutation not detected", err)
	}
	if testGit(t, dir, "show", "-s", "--format=%P") != head+" "+target || testGit(t, dir, "show", "HEAD:unrelated.txt") != "unrelated" {
		t.Fatal("failed post-check did not retain state")
	}
}
