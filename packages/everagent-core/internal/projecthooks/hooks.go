// Package projecthooks installs only explicitly selected repositories' own
// .git/hooks files. It never reads external hook files or changes Git routing.
package projecthooks

import (
	"context"
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"time"
)

const Version = "1.0.0"
const owner = "everagent-project-hooks"
const manifestName = "everagent/manifest.json"

//go:embed templates/*
var templates embed.FS

var files = map[string]string{
	"pre-commit":                   "pre-commit",
	"pre-merge-commit":             "pre-merge-commit",
	"post-commit":                  "post-commit",
	"post-merge":                   "post-merge",
	"everagent/identity-check":     "identity-check",
	"everagent/collect-and-verify": "collect-and-verify",
}

type manifest struct {
	Schema    int               `json:"schema_version"`
	Owner     string            `json:"owner,omitempty"`
	Version   string            `json:"version,omitempty"`
	Bundle    string            `json:"bundle_sha256,omitempty"`
	Installed string            `json:"installed_at,omitempty"`
	Files     map[string]string `json:"files"`
}

type Report struct {
	Schema          int      `json:"schema_version"`
	Root            string   `json:"repository_root"`
	Version         string   `json:"version"`
	Bundle          string   `json:"bundle_sha256"`
	Status          string   `json:"status"`
	Selected        bool     `json:"git_selects_project_hooks"`
	SelectionKnown  bool     `json:"selection_known"`
	Changed         []string `json:"changed_files,omitempty"`
	Backup          string   `json:"backup_directory,omitempty"`
	Error           string   `json:"error,omitempty"`
	ConfigModified  bool     `json:"git_configuration_modified"`
	ExternalTouched bool     `json:"external_hooks_read_or_modified"`
}

type gitRunner func(context.Context, string, ...string) (string, error)

type Options struct {
	Root        string
	Install     bool
	AdoptLegacy bool
	git         gitRunner
	platform    string
}

func hash(body []byte) string {
	sum := sha256.Sum256(body)
	return hex.EncodeToString(sum[:])
}

func versionParts(value string) ([3]int, error) {
	var parts [3]int
	n, err := fmt.Sscanf(value, "%d.%d.%d", &parts[0], &parts[1], &parts[2])
	if err != nil || n != 3 || parts[0] < 0 || parts[1] < 0 || parts[2] < 0 || fmt.Sprintf("%d.%d.%d", parts[0], parts[1], parts[2]) != value {
		return parts, errors.New("invalid-installed-hook-version")
	}
	return parts, nil
}

func desired() (map[string][]byte, manifest) {
	bodies := map[string][]byte{}
	m := manifest{Schema: 2, Owner: owner, Version: Version, Files: map[string]string{}}
	for path, name := range files {
		body, err := templates.ReadFile("templates/" + name)
		if err != nil {
			panic(err) // Build-time embedded resources, never supplied by a caller.
		}
		bodies[path], m.Files[path] = body, hash(body)
	}
	keys := ordered(m.Files)
	var joined strings.Builder
	joined.WriteString(Version)
	for _, key := range keys {
		fmt.Fprintf(&joined, "\x00%s\x00%s", key, m.Files[key])
	}
	m.Bundle = hash([]byte(joined.String()))
	return bodies, m
}

func ordered[V any](values map[string]V) []string {
	keys := make([]string, 0, len(values))
	for key := range values {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

func gitRead(ctx context.Context, root string, args ...string) (string, error) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "git", append([]string{"-C", root}, args...)...)
	// Git's ordinary configuration remains intact; only stale checkout-location
	// variables are removed when an installer targets a different explicit repo.
	for _, entry := range os.Environ() {
		key, _, _ := strings.Cut(entry, "=")
		switch key {
		case "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_PREFIX":
			continue
		}
		cmd.Env = append(cmd.Env, entry)
	}
	cmd.WaitDelay = time.Second
	body, err := cmd.Output()
	if err != nil || len(body) > 16384 {
		return "", errors.New("project-git-metadata-unavailable")
	}
	return strings.TrimSpace(string(body)), nil
}

func directory(path string, optional bool) error {
	info, err := os.Lstat(path)
	if optional && os.IsNotExist(err) {
		return nil
	}
	if err != nil || !info.IsDir() || info.Mode()&os.ModeSymlink != 0 {
		return errors.New("project-hook-directory-missing-or-symlink")
	}
	return nil
}

func readFile(path string) ([]byte, os.FileMode, error) {
	info, err := os.Lstat(path)
	if os.IsNotExist(err) {
		return nil, 0, nil
	}
	if err != nil || !info.Mode().IsRegular() || info.Size() > 1<<20 {
		return nil, 0, errors.New("hook-file-not-bounded-regular-file")
	}
	body, err := os.ReadFile(path)
	return body, info.Mode().Perm(), err
}

// inspect refuses to overwrite even one modified or unowned installed file.
// Legacy adoption requires the exact six-file manifest from the earlier local
// installation; the flag does not authorize replacing arbitrary hooks.
func inspect(hooks string) (manifest, map[string][]byte, map[string]os.FileMode, error) {
	before := map[string][]byte{}
	modes := map[string]os.FileMode{}
	body, mode, err := readFile(filepath.Join(hooks, manifestName))
	if err != nil {
		return manifest{}, nil, nil, err
	}
	var old manifest
	if body != nil {
		if json.Unmarshal(body, &old) != nil || len(old.Files) != len(files) || (old.Schema != 1 && (old.Schema != 2 || old.Owner != owner)) {
			return old, nil, nil, errors.New("unrecognized-hook-manifest")
		}
		for path, digest := range old.Files {
			if _, ok := files[path]; !ok || len(digest) != 64 {
				return old, nil, nil, errors.New("invalid-managed-hook-list")
			}
		}
		before[manifestName], modes[manifestName] = body, mode
	}
	for _, path := range ordered(files) {
		body, mode, err := readFile(filepath.Join(hooks, path))
		if err != nil {
			return old, nil, nil, err
		}
		if body != nil {
			if old.Files == nil || old.Files[path] != hash(body) || mode != 0755 {
				return old, nil, nil, fmt.Errorf("unowned-or-modified-hook: %s", path)
			}
			before[path], modes[path] = body, mode
		} else if old.Files != nil {
			return old, nil, nil, fmt.Errorf("managed-hook-missing: %s", path)
		}
	}
	return old, before, modes, nil
}

func atomicWrite(path string, body []byte, mode os.FileMode) error {
	file, err := os.CreateTemp(filepath.Dir(path), ".ea-hook-next-")
	if err != nil {
		return err
	}
	name := file.Name()
	defer os.Remove(name)
	if err = file.Chmod(mode); err == nil {
		_, err = file.Write(body)
	}
	if err == nil {
		err = file.Sync()
	}
	closeErr := file.Close()
	if err != nil {
		return err
	}
	if closeErr != nil {
		return closeErr
	}
	return os.Rename(name, path)
}

func Apply(ctx context.Context, opts Options) (report Report, err error) {
	bodies, next := desired()
	report = Report{Schema: 1, Version: Version, Bundle: next.Bundle, Status: "blocked"}
	defer func() {
		if err != nil {
			report.Error = err.Error()
			if len(report.Changed) > 0 {
				report.Status = "partial-inspect-backup-before-retrying"
			}
		}
	}()
	platform := opts.platform
	if platform == "" {
		platform = runtime.GOOS
	}
	if platform != "darwin" && platform != "linux" {
		return report, errors.New("project-hooks-platform-not-supported")
	}
	if strings.TrimSpace(opts.Root) == "" {
		return report, errors.New("explicit-repository-required")
	}
	root, err := filepath.Abs(opts.Root)
	if err != nil {
		return report, errors.New("explicit-repository-required")
	}
	root, err = filepath.EvalSymlinks(root)
	if err != nil {
		return report, errors.New("repository-unavailable")
	}
	report.Root = root
	if err = directory(filepath.Join(root, ".git"), false); err != nil {
		return report, err // Linked worktrees and external Git directories need a separate explicit policy.
	}
	hooks := filepath.Join(root, ".git", "hooks")
	for _, path := range []string{hooks, filepath.Join(hooks, "everagent"), filepath.Join(hooks, "everagent", "backups")} {
		if err = directory(path, true); err != nil {
			return report, err
		}
	}
	run := opts.git
	if run == nil {
		run = gitRead
	}
	top, err := run(ctx, root, "rev-parse", "--show-toplevel")
	if err != nil || filepath.Clean(top) != root {
		return report, errors.New("explicit-root-is-not-this-git-checkout")
	}
	selected, selectionErr := run(ctx, root, "rev-parse", "--git-path", "hooks")
	if selectionErr == nil {
		if !filepath.IsAbs(selected) {
			selected = filepath.Join(root, selected)
		}
		report.Selected = filepath.Clean(selected) == hooks
		report.SelectionKnown = true
	}
	old, before, modes, err := inspect(hooks)
	if err != nil {
		return report, err
	}
	if old.Schema == 2 {
		installed, parseErr := versionParts(old.Version)
		if parseErr != nil {
			return report, parseErr
		}
		wanted, _ := versionParts(Version)
		for i := range installed {
			if installed[i] > wanted[i] {
				return report, errors.New("installed-hooks-are-newer; update-the-installer-source")
			}
			if installed[i] < wanted[i] {
				break
			}
		}
	}
	same := old.Owner == owner && old.Version == next.Version && old.Bundle == next.Bundle
	for path, body := range bodies {
		same = same && hash(before[path]) == hash(body) && modes[path] == 0755
	}
	if same {
		report.Status = "current"
		return report, nil
	}
	if !opts.Install {
		report.Status = "update-needed"
		if old.Files == nil {
			report.Status = "not-installed"
		}
		return report, nil
	}
	if old.Schema == 1 && !opts.AdoptLegacy {
		return report, errors.New("verified-legacy-manifest-needs-adopt-legacy")
	}
	if err = os.MkdirAll(filepath.Join(hooks, "everagent"), 0700); err != nil {
		return report, errors.New("cannot-create-project-hook-directory")
	}
	lock := filepath.Join(hooks, "everagent-install.lock")
	if err = os.Mkdir(lock, 0700); err != nil {
		return report, errors.New("project-hook-installer-busy-or-lock-unavailable")
	}
	defer os.Remove(lock)
	// Recheck under our installer lock; other managed invocations cannot race it.
	_, fresh, _, inspectErr := inspect(hooks)
	if inspectErr != nil || !sameFiles(before, fresh) {
		return report, errors.New("hooks-changed-before-installation")
	}
	if len(before) > 0 {
		backups := filepath.Join(hooks, "everagent", "backups")
		if err = os.MkdirAll(backups, 0700); err != nil {
			return report, err
		}
		report.Backup, err = os.MkdirTemp(backups, "install-")
		if err != nil {
			return report, err
		}
		for path, body := range before {
			target := filepath.Join(report.Backup, path)
			if err = os.MkdirAll(filepath.Dir(target), 0700); err != nil {
				return report, err
			}
			if err = os.WriteFile(target, body, modes[path]); err != nil {
				return report, err
			}
		}
	}
	// Helpers first: both old and new entry wrappers always have a complete target.
	paths := []string{"everagent/identity-check", "everagent/collect-and-verify", "pre-commit", "pre-merge-commit", "post-commit", "post-merge"}
	for _, path := range paths {
		target := filepath.Join(hooks, path)
		current, mode, readErr := readFile(target)
		if readErr != nil || string(current) != string(before[path]) || mode != modes[path] {
			return report, fmt.Errorf("hook-changed-during-installation: %s", path)
		}
		if err = atomicWrite(target, bodies[path], 0755); err != nil {
			return report, err
		}
		report.Changed = append(report.Changed, path)
	}
	current, _, readErr := readFile(filepath.Join(hooks, manifestName))
	if readErr != nil || string(current) != string(before[manifestName]) {
		return report, errors.New("hook-manifest-changed-during-installation")
	}
	next.Installed = time.Now().UTC().Format(time.RFC3339)
	body, _ := json.MarshalIndent(next, "", "  ")
	if err = atomicWrite(filepath.Join(hooks, manifestName), append(body, '\n'), 0600); err != nil {
		return report, err
	}
	report.Changed = append(report.Changed, manifestName)
	report.Status = "installed"
	return report, nil
}

func sameFiles(a, b map[string][]byte) bool {
	if len(a) != len(b) {
		return false
	}
	for path, value := range a {
		if string(b[path]) != string(value) {
			return false
		}
	}
	return true
}

func Run(ctx context.Context, root string, args []string, out io.Writer) int {
	if len(args) == 0 || (args[0] != "install" && args[0] != "status") {
		fmt.Fprintln(out, "hooks install [--adopt-legacy] | hooks status; writes only this repository's .git/hooks")
		return 2
	}
	flags := flag.NewFlagSet("hooks", flag.ContinueOnError)
	flags.SetOutput(out)
	adopt := flags.Bool("adopt-legacy", false, "migrate only a matching earlier six-file local manifest")
	if flags.Parse(args[1:]) != nil || flags.NArg() != 0 || (*adopt && args[0] != "install") {
		return 2
	}
	report, err := Apply(ctx, Options{Root: root, Install: args[0] == "install", AdoptLegacy: *adopt})
	if json.NewEncoder(out).Encode(report) != nil || err != nil {
		return 1
	}
	if !report.SelectionKnown || !report.Selected || report.Status == "not-installed" || report.Status == "update-needed" {
		return 3 // Files on disk are not proof that native Git will use them.
	}
	return 0
}
