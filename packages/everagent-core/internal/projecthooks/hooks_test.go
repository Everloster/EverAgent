package projecthooks

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func fixture(t *testing.T) (string, Options) {
	t.Helper()
	root := filepath.Join(t.TempDir(), "project with spaces")
	if err := os.MkdirAll(filepath.Join(root, ".git"), 0700); err != nil {
		t.Fatal(err)
	}
	root, err := filepath.EvalSymlinks(root)
	if err != nil {
		t.Fatal(err)
	}
	opts := Options{Root: root, Install: true, platform: "darwin"}
	opts.git = func(_ context.Context, got string, args ...string) (string, error) {
		if got != root {
			t.Fatal("inspected another checkout")
		}
		switch strings.Join(args, " ") {
		case "rev-parse --show-toplevel":
			return root, nil
		case "rev-parse --git-path hooks":
			return filepath.Join(root, ".git", "hooks"), nil
		default:
			t.Fatalf("unexpected Git operation: %v", args)
			return "", nil
		}
	}
	return root, opts
}

func put(t *testing.T, path, body string, mode os.FileMode) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(body), mode); err != nil {
		t.Fatal(err)
	}
}

func get(t *testing.T, path string) []byte {
	t.Helper()
	body, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return body
}

func TestInstallIsLocalAndIdempotent(t *testing.T) {
	root, opts := fixture(t)
	hooks := filepath.Join(root, ".git", "hooks")
	config := filepath.Join(root, ".git", "config")
	put(t, config, "leave existing project configuration alone\n", 0600)
	put(t, filepath.Join(hooks, "pre-commit.sample"), "original sample\n", 0755)
	report, err := Apply(context.Background(), opts)
	if err != nil || report.Status != "installed" || !report.Selected || len(report.Changed) != 7 {
		t.Fatalf("install: %+v %v", report, err)
	}
	before := get(t, filepath.Join(hooks, manifestName))
	report, err = Apply(context.Background(), opts)
	if err != nil || report.Status != "current" || len(report.Changed) != 0 || report.Backup != "" {
		t.Fatalf("repeat: %+v %v", report, err)
	}
	if !bytes.Equal(before, get(t, filepath.Join(hooks, manifestName))) {
		t.Fatal("no-op rewrote installation metadata")
	}
	if string(get(t, config)) != "leave existing project configuration alone\n" || string(get(t, filepath.Join(hooks, "pre-commit.sample"))) != "original sample\n" {
		t.Fatal("configuration or samples changed")
	}
	for path := range files {
		info, err := os.Stat(filepath.Join(hooks, path))
		if err != nil || info.Mode().Perm() != 0755 {
			t.Fatalf("hook not executable: %s %v", path, err)
		}
	}
}

func TestNewerInstallationsAndEmptyTargetsAreRefused(t *testing.T) {
	root, opts := fixture(t)
	if _, err := Apply(context.Background(), opts); err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(root, ".git/hooks", manifestName)
	var m manifest
	if err := json.Unmarshal(get(t, path), &m); err != nil {
		t.Fatal(err)
	}
	m.Version = "2.0.0"
	body, _ := json.Marshal(m)
	put(t, path, string(body), 0600)
	if _, err := Apply(context.Background(), opts); err == nil || !strings.Contains(err.Error(), "newer") {
		t.Fatalf("newer version not protected: %v", err)
	}
	if !bytes.Equal(get(t, path), body) {
		t.Fatal("newer manifest changed")
	}
	opts.Root = ""
	if _, err := Apply(context.Background(), opts); err == nil {
		t.Fatal("an implicit current directory was accepted")
	}
}

func TestStatusDoesNotCreateDirectories(t *testing.T) {
	root, opts := fixture(t)
	opts.Install = false
	report, err := Apply(context.Background(), opts)
	if err != nil || report.Status != "not-installed" {
		t.Fatalf("status: %+v %v", report, err)
	}
	if _, err := os.Stat(filepath.Join(root, ".git", "hooks")); !os.IsNotExist(err) {
		t.Fatal("status created hooks")
	}
}

func TestExternalSelectionIsReportedWithoutTouchingIt(t *testing.T) {
	root, opts := fixture(t)
	external := filepath.Join(t.TempDir(), "never-create-or-read", "hooks")
	base := opts.git
	opts.git = func(ctx context.Context, root string, args ...string) (string, error) {
		if strings.Join(args, " ") == "rev-parse --git-path hooks" {
			return external, nil
		}
		return base(ctx, root, args...)
	}
	report, err := Apply(context.Background(), opts)
	if err != nil || report.Selected || !report.SelectionKnown || report.Status != "installed" {
		t.Fatalf("selection was disguised: %+v %v", report, err)
	}
	if report.ConfigModified || report.ExternalTouched {
		t.Fatal("installation expanded scope")
	}
	if _, err := os.Stat(filepath.Dir(external)); !os.IsNotExist(err) {
		t.Fatal("external path touched")
	}
	if _, err := os.Stat(filepath.Join(root, ".git", "hooks", "pre-commit")); err != nil {
		t.Fatal(err)
	}
}

func TestUnknownAndModifiedHooksAreNotOverwritten(t *testing.T) {
	for _, managed := range []bool{false, true} {
		t.Run(map[bool]string{false: "unknown", true: "modified"}[managed], func(t *testing.T) {
			root, opts := fixture(t)
			if managed {
				if _, err := Apply(context.Background(), opts); err != nil {
					t.Fatal(err)
				}
			}
			path := filepath.Join(root, ".git", "hooks", "pre-commit")
			put(t, path, "user-owned customization\n", 0755)
			if _, err := Apply(context.Background(), opts); err == nil {
				t.Fatal("customized hook overwritten")
			}
			if string(get(t, path)) != "user-owned customization\n" {
				t.Fatal("customized bytes changed")
			}
		})
	}
}

func TestLegacyAdoptionRequiresMatchingManifestAndKeepsBackup(t *testing.T) {
	root, opts := fixture(t)
	hooks := filepath.Join(root, ".git", "hooks")
	legacy := manifest{Schema: 1, Files: map[string]string{}}
	for path := range files {
		body := "#!/bin/sh\n# legacy " + path + "\n"
		put(t, filepath.Join(hooks, path), body, 0755)
		legacy.Files[path] = hash([]byte(body))
	}
	body, _ := json.Marshal(legacy)
	put(t, filepath.Join(hooks, manifestName), string(body), 0600)
	if _, err := Apply(context.Background(), opts); err == nil {
		t.Fatal("legacy installation adopted without consent")
	}
	opts.AdoptLegacy = true
	report, err := Apply(context.Background(), opts)
	if err != nil || report.Backup == "" || report.Status != "installed" {
		t.Fatalf("adopt: %+v %v", report, err)
	}
	for path, digest := range legacy.Files {
		if hash(get(t, filepath.Join(report.Backup, path))) != digest {
			t.Fatal("legacy recovery bytes not preserved")
		}
	}
	if !bytes.Equal(get(t, filepath.Join(report.Backup, manifestName)), body) {
		t.Fatal("legacy manifest not preserved")
	}
}

func TestSymlinkBoundariesAndWorktreesAreRefused(t *testing.T) {
	for _, relative := range []string{".git", ".git/hooks", ".git/hooks/everagent", ".git/hooks/everagent/backups", ".git/hooks/pre-commit", ".git/hooks/everagent/manifest.json"} {
		t.Run(relative, func(t *testing.T) {
			root, opts := fixture(t)
			path := filepath.Join(root, relative)
			if relative == ".git" {
				if err := os.Remove(path); err != nil {
					t.Fatal(err)
				}
			}
			if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
				t.Fatal(err)
			}
			outside := t.TempDir()
			if err := os.Symlink(outside, path); err != nil {
				t.Fatal(err)
			}
			if _, err := Apply(context.Background(), opts); err == nil {
				t.Fatal("symlink boundary accepted")
			}
			entries, err := os.ReadDir(outside)
			if err != nil || len(entries) != 0 {
				t.Fatal("symlink target changed")
			}
		})
	}
	root, opts := fixture(t)
	if err := os.Remove(filepath.Join(root, ".git")); err != nil {
		t.Fatal(err)
	}
	put(t, filepath.Join(root, ".git"), "gitdir: /outside/worktree\n", 0600)
	if _, err := Apply(context.Background(), opts); err == nil {
		t.Fatal("followed a worktree Git-directory pointer")
	}
}

func TestMissingManagedFileLockAndUnsupportedPlatform(t *testing.T) {
	root, opts := fixture(t)
	if _, err := Apply(context.Background(), opts); err != nil {
		t.Fatal(err)
	}
	if err := os.Remove(filepath.Join(root, ".git/hooks/pre-commit")); err != nil {
		t.Fatal(err)
	}
	if _, err := Apply(context.Background(), opts); err == nil {
		t.Fatal("silently restored a missing managed hook")
	}
	root, opts = fixture(t)
	lock := filepath.Join(root, ".git/hooks/everagent-install.lock")
	if err := os.MkdirAll(lock, 0700); err != nil {
		t.Fatal(err)
	}
	if _, err := Apply(context.Background(), opts); err == nil {
		t.Fatal("installer lock ignored")
	}
	if _, err := os.Stat(lock); err != nil {
		t.Fatal("another operation's lock removed")
	}
	root, opts = fixture(t)
	opts.platform = "windows"
	if _, err := Apply(context.Background(), opts); err == nil {
		t.Fatal("unsupported platform advertised as working")
	}
	if _, err := os.Stat(filepath.Join(root, ".git/hooks")); !os.IsNotExist(err) {
		t.Fatal("unsupported platform wrote hooks")
	}
}

func shellFixture(t *testing.T) (string, []string, string) {
	t.Helper()
	root, opts := fixture(t)
	if _, err := Apply(context.Background(), opts); err != nil {
		t.Fatal(err)
	}
	home, bin := t.TempDir(), t.TempDir()
	calls := filepath.Join(t.TempDir(), "calls")
	put(t, filepath.Join(bin, "git"), "#!/bin/sh\nprintf '%s\\n' \"$HOOK_TEST_ROOT\"\n", 0755)
	put(t, filepath.Join(bin, "uname"), "#!/bin/sh\nprintf '%s\\n' \"$HOOK_TEST_OS\"\n", 0755)
	put(t, filepath.Join(bin, "launchctl"), "#!/bin/sh\nprintf '%s\\n' \"$@\" > \"$HOOK_TEST_CALLS\"\nexit 7\n", 0755)
	put(t, filepath.Join(bin, "systemctl"), "#!/bin/sh\nprintf '%s\\n' \"$@\" > \"$HOOK_TEST_CALLS\"\nexit 7\n", 0755)
	put(t, filepath.Join(home, ".local/bin/eacli"), "#!/bin/sh\nprintf '%s\\n' \"$@\" > \"$HOOK_TEST_CALLS\"\nexit \"${HOOK_TEST_IDENTITY_EXIT:-0}\"\n", 0755)
	env := []string{"PATH=" + bin + ":/usr/bin:/bin", "HOME=" + home, "HOOK_TEST_ROOT=" + root, "HOOK_TEST_CALLS=" + calls}
	return root, env, calls
}

func TestPortableIdentityDelegatesAndFailsClosed(t *testing.T) {
	root, env, calls := shellFixture(t)
	for _, name := range []string{"pre-commit", "pre-merge-commit"} {
		cmd := exec.Command("/bin/sh", filepath.Join(root, ".git/hooks", name))
		cmd.Env = env
		if body, err := cmd.CombinedOutput(); err != nil {
			t.Fatalf("valid identity: %v %s", err, body)
		}
		if string(get(t, calls)) != "git\nidentity\nvalidate\n--json\n" {
			t.Fatal("identity implementation was bypassed or arguments changed")
		}
		cmd = exec.Command("/bin/sh", filepath.Join(root, ".git/hooks", name))
		cmd.Env = append(append([]string(nil), env...), "HOOK_TEST_IDENTITY_EXIT=1")
		if cmd.Run() == nil {
			t.Fatal("invalid identity allowed")
		}
	}
	for _, entry := range env {
		if strings.HasPrefix(entry, "HOME=") {
			if err := os.Remove(filepath.Join(strings.TrimPrefix(entry, "HOME="), ".local/bin/eacli")); err != nil {
				t.Fatal(err)
			}
		}
	}
	cmd := exec.Command("/bin/sh", filepath.Join(root, ".git/hooks/pre-commit"))
	cmd.Env = env
	if cmd.Run() == nil {
		t.Fatal("missing CLI allowed a commit")
	}
}

func TestPortableCollectorDispatchIsNonblockingAndNeverForced(t *testing.T) {
	root, env, calls := shellFixture(t)
	for _, platform := range []string{"Darwin", "Linux", "Other"} {
		for _, hook := range []string{"post-commit", "post-merge"} {
			_ = os.Remove(calls)
			cmd := exec.Command("/bin/sh", filepath.Join(root, ".git/hooks", hook))
			cmd.Env = append(append([]string(nil), env...), "HOOK_TEST_OS="+platform)
			if body, err := cmd.CombinedOutput(); err != nil {
				t.Fatalf("failed dispatcher blocked Git: %v %s", err, body)
			}
			if platform == "Other" {
				if _, err := os.Stat(calls); !os.IsNotExist(err) {
					t.Fatal("unknown platform dispatched a service")
				}
				continue
			}
			args := string(get(t, calls))
			if strings.Contains(args, "-k\n") || strings.Contains(args, "restart") || strings.Contains(args, "enable") {
				t.Fatalf("forced service action: %s", args)
			}
			if platform == "Darwin" && (!strings.HasPrefix(args, "kickstart\ngui/") || !strings.HasSuffix(args, "/com.everagent.context-sync\n")) {
				t.Fatalf("wrong launchd request: %s", args)
			}
			if platform == "Linux" && args != "--user\nstart\n--no-block\neveragent-context-sync.service\n" {
				t.Fatalf("wrong systemd request: %s", args)
			}
		}
	}
}
