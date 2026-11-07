package publicquality

import (
	"context"
	"encoding/json"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func TestCappedOutputCannotBypassWrite(t *testing.T) {
	for _, size := range []int{0, 16, 17, 4097} {
		for _, readerFrom := range []bool{false, true} {
			out := &capped{limit: 16}
			var reader io.Reader = strings.NewReader(strings.Repeat("x", size))
			if readerFrom {
				// LimitedReader has no WriterTo; io.Copy would select a promoted
				// bytes.Buffer.ReadFrom instead of the intended bounded Write.
				reader = io.LimitReader(reader, int64(size))
			}
			n, err := io.Copy(out, reader)
			if err != nil || n != int64(size) || out.Len() != min(16, size) || out.overflow != (size > 16) {
				t.Fatalf("size=%d readerFrom=%t: consumed=%d kept=%d overflow=%t err=%v", size, readerFrom, n, out.Len(), out.overflow, err)
			}
		}
	}
	out := &capped{limit: 3}
	_, _ = io.WriteString(out, "abc")
	_, _ = io.WriteString(out, "d")
	if out.String() != "abc" || !out.overflow {
		t.Fatal("WriteString bypassed cap or lost prefix")
	}
}

func fixtureRepo(t *testing.T) string {
	t.Helper()
	root := t.TempDir()
	runGit(t, root, "init", "-q")
	runGit(t, root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "core.hooksPath=/dev/null", "commit", "-q", "--allow-empty", "-m", "测试快照\n\nCo-Authored-By: Aiden")
	return root
}
func runGit(t *testing.T, root string, args ...string) string {
	t.Helper()
	c := exec.Command("git", args...)
	c.Dir = root
	for _, v := range os.Environ() {
		if !strings.HasPrefix(v, "GIT_") {
			c.Env = append(c.Env, v)
		}
	}
	out, e := c.CombinedOutput()
	if e != nil {
		t.Fatalf("fixture git: %v %s", e, out)
	}
	return strings.TrimSpace(string(out))
}
func writeFixture(t *testing.T, root, p, text string) {
	t.Helper()
	p = filepath.Join(root, filepath.FromSlash(p))
	if e := os.MkdirAll(filepath.Dir(p), 0700); e != nil {
		t.Fatal(e)
	}
	if e := os.WriteFile(p, []byte(text), 0600); e != nil {
		t.Fatal(e)
	}
}
func commitFixture(t *testing.T, root string) {
	t.Helper()
	runGit(t, root, "add", ".")
	runGit(t, root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "更新测试快照\n\nCo-Authored-By: Aiden")
}
func captureFixture(t *testing.T, root, scope string) *Candidate {
	t.Helper()
	c, e := Capture(context.Background(), root, scope)
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(c.Close)
	return c
}
func memory(files map[string]string) *Snapshot {
	entries := map[string]Entry{}
	for p, body := range files {
		entries[p] = Entry{"100644", digest([]byte(body))}
	}
	return newSnapshot(entries, func(p string, _ Entry, n int) ([]byte, error) { return []byte(files[p]), nil })
}
func hasCode(f []Finding, code string) bool {
	for _, item := range f {
		if item.Code == code {
			return true
		}
	}
	return false
}

func TestIndexUsesFrozenTreeNotWorktree(t *testing.T) {
	root := fixtureRepo(t)
	writeFixture(t, root, "note.md", "# note\n")
	commitFixture(t, root)
	writeFixture(t, root, "note.md", "sk-"+strings.Repeat("x", 24))
	runGit(t, root, "add", "note.md")
	writeFixture(t, root, "note.md", "# clean preview\n")
	c := captureFixture(t, root, "index")
	got := AuditPrivacy(c, nil)
	if !hasCode(got.Findings, "KNOWN_TOKEN_PREFIX") {
		t.Fatal("staged content was not audited")
	}
	if e := c.Verify(); e != nil {
		t.Fatal(e)
	}
	preview := captureFixture(t, root, "worktree")
	if len(AuditPrivacy(preview, nil).Findings) != 0 {
		t.Fatal("worktree preview unexpectedly used the index")
	}
	runGit(t, root, "add", "note.md")
	if c.Verify() == nil {
		t.Fatal("concurrent index change was accepted")
	}
}

func TestSnapshotReadsLiteralObjectsDespiteReplaceRefs(t *testing.T) {
	for _, kind := range []string{"blob", "tree", "head"} {
		t.Run(kind, func(t *testing.T) {
			root := fixtureRepo(t)
			baseline := "# baseline\n"
			writeFixture(t, root, "note.md", baseline)
			commitFixture(t, root)
			head := runGit(t, root, "rev-parse", "HEAD")
			baseTree := runGit(t, root, "rev-parse", "HEAD^{tree}")
			baseBlob := runGit(t, root, "rev-parse", "HEAD:note.md")
			staged := "sk-" + strings.Repeat("x", 24) + "\n"
			writeFixture(t, root, "note.md", staged)
			runGit(t, root, "add", "note.md")
			indexTree := runGit(t, root, "write-tree")
			indexBlob := runGit(t, root, "rev-parse", ":note.md")
			switch kind {
			case "blob":
				runGit(t, root, "replace", indexBlob, baseBlob)
				if got := runGit(t, root, "cat-file", "blob", indexBlob); got != strings.TrimSpace(baseline) {
					t.Fatal("fixture did not exercise a real blob replacement")
				}
			case "tree":
				runGit(t, root, "replace", indexTree, baseTree)
			case "head":
				other := runGit(t, root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit-tree", indexTree, "-m", "替换视图测试\n\nCo-Authored-By: Aiden")
				runGit(t, root, "replace", head, other)
			}
			c := captureFixture(t, root, "index")
			before, e1 := c.Before.Bytes("note.md", TextLimit)
			after, e2 := c.After.Bytes("note.md", TextLimit)
			// Use a fresh snapshot to exercise the separate prefix read path.
			prefix, e3 := captureFixture(t, root, "index").After.Prefix("note.md", 3)
			if e1 != nil || e2 != nil || e3 != nil || string(before) != baseline || string(after) != staged || string(prefix) != "sk-" {
				t.Fatalf("%s substituted an audited object: %v %v %v", kind, e1, e2, e3)
			}
			if !hasCode(AuditPrivacy(c, nil).Findings, "KNOWN_TOKEN_PREFIX") {
				t.Fatal("replacement hid the staged privacy finding or polluted its baseline")
			}
			h := captureFixture(t, root, "head")
			if err := h.CompareBase(head); err != nil {
				t.Fatal(err)
			}
			literalHead, err := h.After.Bytes("note.md", TextLimit)
			if err != nil || string(literalHead) != baseline || len(h.Changed) != 0 || c.Verify() != nil {
				t.Fatal("HEAD/CI baseline did not use the same literal object semantics")
			}
		})
	}
}
func TestWorktreePathDriftAndLinkedContent(t *testing.T) {
	root := fixtureRepo(t)
	writeFixture(t, root, "note.md", "note\n")
	commitFixture(t, root)
	c := captureFixture(t, root, "worktree")
	writeFixture(t, root, "new.md", "new\n")
	if c.Verify() == nil {
		t.Fatal("new untracked path not detected")
	}
	if e := os.Symlink(t.TempDir(), filepath.Join(root, "linked")); e != nil {
		t.Skip("symlinks unavailable")
	}
	if _, e := readRoot(c.root, "linked/hidden.md", 1024); e == nil {
		t.Fatal("followed symlink")
	}
}
func TestPrivacyBaselineIsPerPathPerOccurrence(t *testing.T) {
	address := "192.0." + "2.1"
	c := &Candidate{Before: memory(map[string]string{"a.md": address}), After: memory(map[string]string{"a.md": address + "\n" + address, "b.md": address}), Changed: []string{"a.md", "b.md"}}
	got := AuditPrivacy(c, nil)
	if got.Existing != 1 || len(got.Findings) != 2 {
		t.Fatalf("wrong baseline accounting: %+v", got)
	}
}
func TestPrivacyDecodedKeysAndNonExemptAssignments(t *testing.T) {
	key := "pass" + "word"
	secretText := strings.Repeat("z", 20)
	encoded := `{"\u0070assword":"` + secretText + `"}`
	if !hasCodeFind(contentHits(encoded, "data.json"), "CREDENTIAL_VALUE") {
		t.Fatal("escaped JSON key bypassed credential scan")
	}
	body := key + "=" + secretText
	c := &Candidate{Before: memory(map[string]string{"a.txt": body}), After: memory(map[string]string{"a.txt": body + "-suffix"}), Changed: []string{"a.txt"}}
	if !hasCode(AuditPrivacy(c, nil).Findings, "CREDENTIAL_VALUE") {
		t.Fatal("assignment prefix inherited baseline exemption")
	}
	body = "package p\nvar " + key + " = settings.Value\n"
	if hasCodeFind(contentHits(body, "example.go"), "CREDENTIAL_VALUE") {
		t.Fatal("Go reference mistaken for literal")
	}
	quoted, _ := json.Marshal(secretText)
	body = "package p\nvar " + key + " = " + string(quoted) + "\n"
	if !hasCodeFind(contentHits(body, "example.go"), "CREDENTIAL_VALUE") {
		t.Fatal("quoted value received reference exemption")
	}
}
func hasCodeFind(h []privacyHit, c string) bool {
	for _, v := range h {
		if v.finding.Code == c {
			return true
		}
	}
	return false
}
func TestPrivacyMediaAndTranscriptPermission(t *testing.T) {
	root := fixtureRepo(t)
	writeFixture(t, root, "doc.png", "\x89PNG\r\n\x1a\n"+strings.Repeat("\x00", TextLimit+1))
	runGit(t, root, "add", "doc.png")
	c := captureFixture(t, root, "index")
	r := AuditPrivacy(c, nil)
	if r.SkippedBinary != 1 || r.Scanned != 0 || len(r.Findings) != 0 {
		t.Fatalf("binary not separately skipped: %+v", r)
	}
	body := "public source"
	p := "notes.transcript.txt"
	permit := Object{"schema_version": json.Number("1"), "sha256": digest([]byte(body)), "source_url": "https://example.invalid/source", "permission_url": "https://example.invalid/license", "permission_note": "Test source permission", "maintainer_confirmed": true}
	raw, _ := json.Marshal(permit)
	c = &Candidate{Before: memory(map[string]string{}), After: memory(map[string]string{p: body, p + ".publication.json": string(raw)}), Changed: []string{p}}
	if hasCode(AuditPrivacy(c, nil).Findings, "FULL_TRANSCRIPT_PUBLICATION") {
		t.Fatal("valid content-bound permission rejected")
	}
	c.Before = c.After
	c.After = memory(map[string]string{p: body})
	c.Changed = []string{p + ".publication.json"}
	if !hasCode(AuditPrivacy(c, nil).Findings, "FULL_TRANSCRIPT_PUBLICATION") {
		t.Fatal("deleted permission did not recheck unchanged source")
	}
}
func TestStrictJSONAndArchiveCanonicalBytes(t *testing.T) {
	for _, s := range []string{`{"a":1,"a":2}`, `{} {}`, `[1,]`} {
		if _, e := DecodeJSON([]byte(s)); e == nil {
			t.Fatal("invalid JSON accepted")
		}
	}
	s := "{\"z\":\"中文\u2028<>&\",\"a\":1.0,\"b\":1e2,\"c\":0.00001}"
	v, e := DecodeJSON([]byte(s))
	if e != nil {
		t.Fatal(e)
	}
	got, e := canonical(v)
	if e != nil {
		t.Fatal(e)
	}
	want := "{\"a\":1.0,\"b\":100.0,\"c\":1e-05,\"z\":\"中文\u2028<>&\"}"
	if string(got) != want {
		t.Fatalf("canonical archive bytes differ: %s", got)
	}
}
