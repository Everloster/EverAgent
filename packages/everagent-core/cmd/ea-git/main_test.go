package main

import (
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func gitFixture(t *testing.T) string {
	t.Helper()
	t.Setenv("GIT_CONFIG_GLOBAL", os.DevNull)
	t.Setenv("GIT_CONFIG_NOSYSTEM", "1")
	t.Setenv("GIT_CONFIG_COUNT", "0")
	for _, key := range []string{"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"} {
		t.Setenv(key, "")
		if err := os.Unsetenv(key); err != nil {
			t.Fatal(err)
		}
	}
	root := t.TempDir()
	gitRun(t, root, "init", "-q")
	gitRun(t, root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "core.hooksPath="+os.DevNull,
		"commit", "-q", "--allow-empty", "-m", "提交入口测试\n\nCo-Authored-By: Aiden")
	return root
}

func gitRun(t *testing.T, root string, args ...string) {
	t.Helper()
	cmd := exec.Command("git", args...)
	cmd.Dir = root
	if output, err := cmd.CombinedOutput(); err != nil {
		t.Fatalf("fixture git: %v %s", err, output)
	}
}

func TestAuthorPolicyUsesOnlyIndex(t *testing.T) {
	root := gitFixture(t)
	if err := os.Mkdir(filepath.Join(root, "config"), 0700); err != nil {
		t.Fatal(err)
	}
	p := filepath.Join(root, "config/git-policy.json")
	write := func(body string) {
		t.Helper()
		if err := os.WriteFile(p, []byte(body), 0600); err != nil {
			t.Fatal(err)
		}
	}
	write(`{"schema_version":1,"author":{"name":"Fixture Owner","email":"owner@example.invalid"}}`)
	gitRun(t, root, "add", "config/git-policy.json")
	write(`{"schema_version":1,"author":{"name":"Unstaged","email":"other@example.invalid"}}`)
	author, err := readAuthor(context.Background(), root)
	if err != nil || author.Name != "Fixture Owner" {
		t.Fatalf("used unstaged author policy: %+v %v", author, err)
	}
	for _, body := range []string{`{"schema_version":1,"schema_version":1}`, `{"schema_version":1,"author":{"name":"","email":"x@y"}}`, `{"schema_version":1,"author":{"name":"Fixture","email":"bad\naddress"}}`} {
		write(body)
		gitRun(t, root, "add", "config/git-policy.json")
		if _, err := readAuthor(context.Background(), root); err == nil {
			t.Fatal("invalid author policy accepted")
		}
	}
}

func TestContentModesFailBeforeIdentityAndGate(t *testing.T) {
	root := gitFixture(t)
	old, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = os.Chdir(old) })
	// No author policy: reaching that read would fail with 1, not argument code 2.
	for _, args := range [][]string{{"--all"}, {"--only", "note.md"}, {"--reset-author"}, {"--", "note.md"}} {
		if code := run(append([]string{"--repo-root", root, "commit"}, args...)); code != 2 {
			t.Fatalf("invalid content mode reached a later stage: %v = %d", args, code)
		}
	}
}

func TestGitIdentReadsEffectiveEnvironment(t *testing.T) {
	root := gitFixture(t)
	t.Setenv("GIT_AUTHOR_NAME", "Author Fixture")
	t.Setenv("GIT_AUTHOR_EMAIL", "author@example.invalid")
	t.Setenv("GIT_COMMITTER_NAME", "Committer Fixture")
	t.Setenv("GIT_COMMITTER_EMAIL", "committer@example.invalid")
	for variable, expected := range map[string]string{"GIT_AUTHOR_IDENT": "Author Fixture", "GIT_COMMITTER_IDENT": "Committer Fixture"} {
		got, err := gitIdent(context.Background(), root, variable)
		if err != nil || got.Name != expected {
			t.Fatalf("effective %s: %+v %v", variable, got, err)
		}
	}
}
