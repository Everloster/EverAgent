package core

import (
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func TestPushIdentityChecksNewCommitsAndRevokedAncestry(t *testing.T) {
	root := t.TempDir()
	hooks := t.TempDir()
	git := func(author, email, committer, committerEmail string, args ...string) string {
		t.Helper()
		cmd := exec.Command("git", append([]string{"-c", "core.hooksPath=" + hooks, "-c", "commit.gpgsign=false", "-C", root}, args...)...)
		cmd.Env = append(os.Environ(), "GIT_AUTHOR_NAME="+author, "GIT_AUTHOR_EMAIL="+email, "GIT_COMMITTER_NAME="+committer, "GIT_COMMITTER_EMAIL="+committerEmail)
		out, err := cmd.CombinedOutput()
		if err != nil {
			t.Fatalf("fixture git failed: %s", out)
		}
		return strings.TrimSpace(string(out))
	}
	git("Historical", "old@example.invalid", "Historical", "old@example.invalid", "init", "-q", "-b", "main")
	if err := os.WriteFile(filepath.Join(root, "file"), []byte("content\n"), 0600); err != nil {
		t.Fatal(err)
	}
	git("Historical", "old@example.invalid", "Historical", "old@example.invalid", "add", "file")
	git("Historical", "old@example.invalid", "Historical", "old@example.invalid", "commit", "-qm", "historical")
	base := git("", "", "", "", "rev-parse", "HEAD")
	policy := PushIdentityPolicy{Author: Author{"Owner", "owner@example.invalid"}}
	git("Owner", "owner@example.invalid", "fixture-model", "noreply@example.invalid", "commit", "--allow-empty", "-qm", "valid")
	good := git("", "", "", "", "rev-parse", "HEAD")
	if err := CheckPushIdentities(context.Background(), root, base, good, policy); err != nil {
		t.Fatalf("existing historical identities were rejected: %v", err)
	}
	git("Wrong", "PRIVATE_SENTINEL@example.invalid", "fixture-model", "noreply@example.invalid", "commit", "--allow-empty", "-qm", "wrong author")
	bad := git("", "", "", "", "rev-parse", "HEAD")
	if err := CheckPushIdentities(context.Background(), root, base, bad, policy); err == nil || strings.Contains(err.Error(), "PRIVATE_SENTINEL") {
		t.Fatal("bad Author accepted or exposed")
	}
	policy.ForbiddenCommits = []string{base}
	if err := CheckPushIdentities(context.Background(), root, base, good, policy); err == nil {
		t.Fatal("revoked ancestor was reintroduced")
	}
	policy.ForbiddenCommits = []string{"not-an-object"}
	if err := CheckPushIdentities(context.Background(), root, base, good, policy); err == nil {
		t.Fatal("invalid revocation policy accepted")
	}
}
