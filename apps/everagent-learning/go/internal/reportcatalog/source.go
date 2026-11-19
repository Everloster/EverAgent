// Package reportcatalog parses the existing public Markdown report collections.
// It has no quality-gate, Git, database, CLI, or private-repository dependency.
package reportcatalog

import (
	"bytes"
	"errors"
	"os"
	"path"
	"sort"
	"strings"
	"unicode/utf8"
)

const textLimit = 2 << 20

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
func safePath(p string) bool {
	return p != "" && p != "." && p != ".." && path.Clean(p) == p && !path.IsAbs(p) && !strings.HasPrefix(p, "../") && !strings.ContainsAny(p, "\\\x00\r\n\t") && utf8.ValidString(p)
}

// A caller-scoped source keeps the same listed-path and text budgets as the
// original catalog adapter, without importing quality snapshots or reading Git.
type fileSource struct {
	listed map[string]bool
	read   func(string, int) ([]byte, error)
}

func newFileSource(paths []string, read func(string, int) ([]byte, error)) *fileSource {
	s := &fileSource{listed: make(map[string]bool, len(paths)), read: read}
	for _, p := range paths {
		s.listed[p] = true
	}
	return s
}
func (s *fileSource) Paths() []string {
	out := make([]string, 0, len(s.listed))
	for p := range s.listed {
		out = append(out, p)
	}
	sort.Strings(out)
	return out
}
func (s *fileSource) Text(p string) (string, error) {
	if !safePath(p) {
		return "", errors.New("invalid-repository-path")
	}
	if !s.listed[p] {
		return "", os.ErrNotExist
	}
	b, err := s.read(p, textLimit)
	if err != nil {
		return "", err
	}
	if len(b) > textLimit {
		return "", errors.New("file-too-large")
	}
	b = bytes.TrimPrefix(b, []byte{0xef, 0xbb, 0xbf})
	if !utf8.Valid(b) || bytes.IndexByte(b, 0) >= 0 {
		return "", errors.New("non-utf8-text")
	}
	return string(b), nil
}
