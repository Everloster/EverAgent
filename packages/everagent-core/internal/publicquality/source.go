// Package publicquality implements the public repository's deterministic checks.
// It does not infer model qualification from process names, execute report
// contents, call models, or read the private repository.
package publicquality

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"maps"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
	"unicode/utf8"
)

const TextLimit = 2 << 20
const metadataLimit = 8 << 20

type Finding struct {
	File     string `json:"file,omitempty"`
	Line     int    `json:"line,omitempty"`
	Severity string `json:"severity"`
	Code     string `json:"code"`
	Message  string `json:"message"`
}

func issue(file, code, message string) Finding {
	return Finding{File: file, Severity: "error", Code: code, Message: message}
}
func warning(file, code, message string) Finding {
	f := issue(file, code, message)
	f.Severity = "warning"
	return f
}
func digest(b []byte) string { h := sha256.Sum256(b); return hex.EncodeToString(h[:]) }
func safePath(p string) bool {
	return p != "" && p != "." && p != ".." && path.Clean(p) == p && !path.IsAbs(p) && !strings.HasPrefix(p, "../") && !strings.ContainsAny(p, "\\\x00\r\n\t") && utf8.ValidString(p)
}

type Entry struct{ Mode, OID string }

// A snapshot reads only its listed paths. Git blobs are immutable; a worktree
// snapshot separately verifies every consumed file before returning evidence.
type Snapshot struct {
	entries    map[string]Entry
	read       func(string, Entry, int) ([]byte, error)
	prefix     func(string, Entry, int) ([]byte, error)
	cache      map[string][]byte
	readHashes map[string]string
}

func newSnapshot(entries map[string]Entry, read func(string, Entry, int) ([]byte, error)) *Snapshot {
	return &Snapshot{entries: entries, read: read, cache: map[string][]byte{}, readHashes: map[string]string{}}
}
func (s *Snapshot) Paths() []string {
	out := make([]string, 0, len(s.entries))
	for p := range s.entries {
		out = append(out, p)
	}
	sort.Strings(out)
	return out
}
func (s *Snapshot) Has(p string) bool { _, ok := s.entries[p]; return ok }
func (s *Snapshot) Dir(p string) bool {
	if p == "." || p == "" {
		return true
	}
	for f := range s.entries {
		if strings.HasPrefix(f, p+"/") {
			return true
		}
	}
	return false
}
func (s *Snapshot) Bytes(p string, limit int) ([]byte, error) {
	if !safePath(p) {
		return nil, errors.New("invalid-repository-path")
	}
	e, ok := s.entries[p]
	if !ok {
		return nil, os.ErrNotExist
	}
	if e.Mode != "100644" && e.Mode != "100755" {
		return nil, errors.New("non-regular-repository-file")
	}
	if b, ok := s.cache[p]; ok {
		if len(b) > limit {
			return nil, errors.New("file-too-large")
		}
		return b, nil
	}
	b, err := s.read(p, e, limit)
	if err != nil {
		return nil, err
	}
	if len(b) > limit {
		return nil, errors.New("file-too-large")
	}
	s.cache[p] = b
	s.readHashes[p] = digest(b)
	return b, nil
}
func (s *Snapshot) Text(p string) (string, error) {
	b, e := s.Bytes(p, TextLimit)
	if e != nil {
		return "", e
	}
	b = bytes.TrimPrefix(b, []byte{0xef, 0xbb, 0xbf})
	if !utf8.Valid(b) || bytes.IndexByte(b, 0) >= 0 {
		return "", errors.New("non-utf8-text")
	}
	return string(b), nil
}
func (s *Snapshot) Prefix(p string, n int) ([]byte, error) {
	if !safePath(p) {
		return nil, errors.New("invalid-repository-path")
	}
	entry, ok := s.entries[p]
	if !ok {
		return nil, os.ErrNotExist
	}
	if entry.Mode != "100644" && entry.Mode != "100755" {
		return nil, errors.New("non-regular-repository-file")
	}
	if b, ok := s.cache[p]; ok {
		return b[:min(n, len(b))], nil
	}
	if s.prefix != nil {
		return s.prefix(p, entry, n)
	}
	b, e := s.Bytes(p, TextLimit)
	if e != nil {
		return nil, e
	}
	return b[:min(n, len(b))], nil
}

type capped struct {
	buffer   bytes.Buffer // Do not promote Buffer.ReadFrom: io.Copy would bypass Write.
	limit    int
	overflow bool
}

func (w *capped) Len() int       { return w.buffer.Len() }
func (w *capped) Bytes() []byte  { return w.buffer.Bytes() }
func (w *capped) String() string { return w.buffer.String() }

func (w *capped) Write(p []byte) (int, error) {
	n := len(p)
	left := w.limit - w.Len()
	if n > left {
		w.overflow = true
		p = p[:max(0, left)]
	}
	_, _ = w.buffer.Write(p)
	return n, nil
}

func git(ctx context.Context, root string, limit int, args ...string) ([]byte, error) {
	ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()
	c := gitCommand(ctx, root, args...)
	out := &capped{limit: limit}
	c.Stdout = out
	c.Stderr = io.Discard
	if err := c.Run(); err != nil {
		return nil, errors.New("git-snapshot-read-failed")
	}
	if out.overflow {
		return nil, errors.New("git-snapshot-budget")
	}
	return out.Bytes(), nil
}
func gitCommand(ctx context.Context, root string, args ...string) *exec.Cmd {
	// A refs/replace overlay is a local view, not the blob/tree being committed.
	// Apply literal object semantics to every read, including HEAD and prefixes.
	c := exec.CommandContext(ctx, "git", append([]string{"--no-replace-objects", "--no-pager", "--literal-pathspecs", "-C", root}, args...)...)
	c.WaitDelay = time.Second
	// The caller's index is intentional (including core's inherited index).
	// Alternate repositories, config injections and lazy network fetches are not.
	for _, entry := range os.Environ() {
		key, _, _ := strings.Cut(entry, "=")
		if strings.HasPrefix(key, "GIT_") && key != "GIT_INDEX_FILE" {
			continue
		}
		c.Env = append(c.Env, entry)
	}
	c.Env = append(c.Env, "GIT_TERMINAL_PROMPT=0", "GIT_OPTIONAL_LOCKS=0", "GIT_NO_LAZY_FETCH=1")
	return c
}

// Read only a bounded prefix for format detection. A large image must not be
// loaded into memory, or be labelled text-scanned just because it is recognized.
func blobPrefix(ctx context.Context, root, oid string, n int) ([]byte, error) {
	ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()
	cmd := gitCommand(ctx, root, "cat-file", "blob", oid)
	cmd.Stderr = io.Discard
	stdout, e := cmd.StdoutPipe()
	if e != nil {
		return nil, errors.New("git-blob-unreadable")
	}
	if cmd.Start() != nil {
		return nil, errors.New("git-blob-unreadable")
	}
	b, e := io.ReadAll(io.LimitReader(stdout, int64(n)))
	if len(b) == n {
		cancel()
	}
	wait := cmd.Wait()
	if e != nil || len(b) < n && wait != nil {
		return nil, errors.New("git-blob-unreadable")
	}
	return b, nil
}

var objectID = regexp.MustCompile(`^(?:[0-9a-f]{40}|[0-9a-f]{64})$`)

func gitID(ctx context.Context, root string, args ...string) (string, error) {
	b, e := git(ctx, root, 512, args...)
	s := strings.TrimSpace(string(b))
	if e != nil || !objectID.MatchString(s) {
		return "", errors.New("git-object-id-unavailable")
	}
	return s, nil
}

func entries(raw []byte, index bool) (map[string]Entry, error) {
	out := map[string]Entry{}
	for _, row := range bytes.Split(raw, []byte{0}) {
		if len(row) == 0 {
			continue
		}
		meta, name, ok := bytes.Cut(row, []byte{'\t'})
		fields := strings.Fields(string(meta))
		if !ok || len(fields) != 3 || !safePath(string(name)) {
			return nil, errors.New("invalid-git-entry")
		}
		mode, oid := fields[0], fields[2]
		if index {
			oid = fields[1]
			if fields[2] != "0" {
				return nil, errors.New("unmerged-index")
			}
		} else if fields[1] != "blob" && fields[1] != "commit" {
			return nil, errors.New("unsupported-git-entry")
		}
		if !objectID.MatchString(oid) {
			return nil, errors.New("invalid-git-entry")
		}
		if _, ok := out[string(name)]; ok {
			return nil, errors.New("duplicate-git-entry")
		}
		out[string(name)] = Entry{mode, oid}
	}
	return out, nil
}

type Candidate struct {
	Before, After                *Snapshot
	Changed, Added               []string
	Root, Scope, Head, IndexTree string
	Base                         string
	ctx                          context.Context
	root                         *os.Root
	worktreeState                map[string]string
}

func (c *Candidate) Close() {
	if c.root != nil {
		c.root.Close()
	}
}

func openRootFile(root *os.Root, p string) (*os.File, error) {
	parts := strings.Split(p, "/")
	var before os.FileInfo
	for i := range parts {
		s, e := root.Lstat(strings.Join(parts[:i+1], "/"))
		if e != nil {
			return nil, e
		}
		if s.Mode()&os.ModeSymlink != 0 || i < len(parts)-1 && !s.IsDir() {
			return nil, errors.New("linked-repository-file")
		}
		if i == len(parts)-1 {
			if !s.Mode().IsRegular() {
				return nil, errors.New("not-regular-file")
			}
			before = s
		}
	}
	f, e := openInput(root, p)
	if e != nil {
		return nil, e
	}
	info, e := f.Stat()
	if e != nil || !info.Mode().IsRegular() || !os.SameFile(before, info) {
		f.Close()
		return nil, errors.New("not-regular-file")
	}
	return f, nil
}
func readRoot(root *os.Root, p string, limit int) ([]byte, error) {
	f, e := openRootFile(root, p)
	if e != nil {
		return nil, e
	}
	defer f.Close()
	info, e := f.Stat()
	if e != nil || info.Size() > int64(limit) {
		return nil, errors.New("file-too-large")
	}
	b, e := io.ReadAll(io.LimitReader(f, int64(limit)+1))
	if e != nil || len(b) > limit {
		return nil, errors.New("file-read-incomplete")
	}
	return b, nil
}
func worktreeEntries(ctx context.Context, root string, r *os.Root, tracked map[string]Entry) (map[string]Entry, map[string]string, error) {
	after := map[string]Entry{}
	for p, e := range tracked {
		after[p] = e
	}
	raw, e := git(ctx, root, metadataLimit, "ls-files", "--others", "--exclude-standard", "-z")
	if e != nil {
		return nil, nil, e
	}
	for _, p := range strings.Split(string(raw), "\x00") {
		if p == "" {
			continue
		}
		if !safePath(p) {
			return nil, nil, errors.New("unsafe-untracked-path")
		}
		after[p] = Entry{Mode: "100644"}
	}
	states := map[string]string{}
	for p, row := range after {
		info, e := r.Lstat(p)
		if errors.Is(e, os.ErrNotExist) {
			delete(after, p)
			continue
		}
		if e != nil {
			return nil, nil, e
		}
		switch {
		case info.Mode().IsRegular():
			row.Mode = "100644"
			if info.Mode()&0111 != 0 {
				row.Mode = "100755"
			}
		case info.Mode()&os.ModeSymlink != 0:
			row.Mode = "120000"
		default:
			row.Mode = "special"
		}
		after[p] = row
		states[p] = fmt.Sprintf("%s:%d:%d", info.Mode(), info.Size(), info.ModTime().UnixNano())
	}
	return after, states, nil
}

// Capture freezes the index through object IDs. Worktree mode is for explicit
// previews; it includes untracked non-ignored files and detects read-time drift.
func Capture(ctx context.Context, root, scope string) (*Candidate, error) {
	if scope != "index" && scope != "worktree" && scope != "head" {
		return nil, errors.New("scope-must-be-index-worktree-or-head")
	}
	abs, e := filepath.Abs(root)
	if e != nil {
		return nil, e
	}
	real, e := filepath.EvalSymlinks(abs)
	if e != nil {
		return nil, e
	}
	top, e := git(ctx, real, 4096, "rev-parse", "--show-toplevel")
	if e != nil || filepath.Clean(strings.TrimSpace(string(top))) != real {
		return nil, errors.New("exact-checkout-root-required")
	}
	head, e := gitID(ctx, real, "rev-parse", "--verify", "HEAD")
	if e != nil {
		return nil, errors.New("existing-head-required")
	}
	base, e := git(ctx, real, metadataLimit, "ls-tree", "-r", "-z", head)
	if e != nil {
		return nil, e
	}
	before, e := entries(base, false)
	if e != nil {
		return nil, e
	}
	tree, e := gitID(ctx, real, "write-tree")
	if e != nil {
		return nil, e
	}
	// Read the immutable tree we just captured, not a second mutable index view.
	index, e := git(ctx, real, metadataLimit, "ls-tree", "-r", "-z", tree)
	if e != nil {
		return nil, e
	}
	after, e := entries(index, false)
	if e != nil {
		return nil, e
	}
	c := &Candidate{Root: real, Scope: scope, Head: head, Base: head, IndexTree: tree, ctx: ctx}
	blobs := func(_ string, entry Entry, limit int) ([]byte, error) {
		b, e := blobPrefix(ctx, real, entry.OID, limit+1)
		if e == nil && len(b) > limit {
			return nil, errors.New("git-snapshot-budget")
		}
		return b, e
	}
	c.Before = newSnapshot(before, blobs)
	c.Before.prefix = func(_ string, row Entry, n int) ([]byte, error) { return blobPrefix(ctx, real, row.OID, n) }
	if scope == "head" {
		c.After = c.Before
		return c, nil
	}
	if scope == "worktree" {
		r, e := os.OpenRoot(real)
		if e != nil {
			return nil, e
		}
		c.root = r
		after, c.worktreeState, e = worktreeEntries(ctx, real, r, after)
		if e != nil {
			c.Close()
			return nil, e
		}
		c.After = newSnapshot(after, func(p string, _ Entry, n int) ([]byte, error) { return readRoot(r, p, n) })
		c.After.prefix = func(p string, _ Entry, n int) ([]byte, error) {
			f, e := openRootFile(r, p)
			if e != nil {
				return nil, e
			}
			defer f.Close()
			return io.ReadAll(io.LimitReader(f, int64(n)))
		}
	} else {
		c.After = newSnapshot(after, blobs)
		c.After.prefix = c.Before.prefix
	}
	changed := map[string]bool{}
	if scope == "index" {
		for p, row := range before {
			if after[p] != row {
				changed[p] = true
			}
		}
		for p, row := range after {
			if before[p] != row {
				changed[p] = true
			}
		}
	} else {
		names, e := git(ctx, real, metadataLimit, "diff", "--no-ext-diff", "--no-renames", "--name-only", "-z", head, "--")
		if e != nil {
			c.Close()
			return nil, e
		}
		for _, p := range strings.Split(string(names), "\x00") {
			if p != "" {
				if !safePath(p) {
					c.Close()
					return nil, errors.New("unsafe-changed-path")
				}
				changed[p] = true
			}
		}
	}
	for p := range after {
		if _, ok := before[p]; !ok {
			changed[p] = true
			c.Added = append(c.Added, p)
		}
	}
	for p := range changed {
		c.Changed = append(c.Changed, p)
	}
	sort.Strings(c.Changed)
	sort.Strings(c.Added)
	return c, nil
}

// CompareBase is for CI's immutable HEAD snapshot. It never fetches history,
// expands a ref from untrusted input, or treats a missing base as an empty tree.
func (c *Candidate) CompareBase(base string) error {
	if c.Scope != "head" || !objectID.MatchString(base) {
		return errors.New("base-requires-full-object-id-and-head-scope")
	}
	raw, err := git(c.ctx, c.Root, metadataLimit, "ls-tree", "-r", "-z", base)
	if err != nil {
		return errors.New("comparison-base-unavailable")
	}
	before, err := entries(raw, false)
	if err != nil {
		return err
	}
	c.Before = newSnapshot(before, c.After.read)
	c.Before.prefix = c.After.prefix
	c.Base = base
	c.Added = nil
	changed := map[string]bool{}
	for p, row := range before {
		if c.After.entries[p] != row {
			changed[p] = true
		}
	}
	for p, row := range c.After.entries {
		if before[p] != row {
			changed[p] = true
		}
		if _, exists := before[p]; !exists {
			c.Added = append(c.Added, p)
		}
	}
	c.Changed = sortedBoolKeys(changed)
	sort.Strings(c.Added)
	return nil
}

func (c *Candidate) Verify() error {
	h, e := gitID(c.ctx, c.Root, "rev-parse", "--verify", "HEAD")
	if e != nil || h != c.Head {
		return errors.New("head-changed-during-check")
	}
	tree, e := gitID(c.ctx, c.Root, "write-tree")
	if e != nil || tree != c.IndexTree {
		return errors.New("index-changed-during-check")
	}
	if c.Scope == "worktree" {
		index, e := git(c.ctx, c.Root, metadataLimit, "ls-tree", "-r", "-z", c.IndexTree)
		if e != nil {
			return e
		}
		tracked, e := entries(index, false)
		if e != nil {
			return e
		}
		_, state, e := worktreeEntries(c.ctx, c.Root, c.root, tracked)
		if e != nil || !maps.Equal(state, c.worktreeState) {
			return errors.New("worktree-paths-changed-during-check")
		}
		for p, h := range c.After.readHashes {
			b, e := readRoot(c.root, p, TextLimit)
			if e != nil || digest(b) != h {
				return errors.New("worktree-changed-during-check")
			}
		}
	}
	return nil
}
