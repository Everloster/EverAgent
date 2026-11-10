// Package core owns portable caller identity and Git evidence. It contains no
// private device registry and never searches unrelated processes or conversations.
package core

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"time"
	"unicode/utf16"
)

const Version = "0.5.5"

type Object = map[string]any

var modelPattern = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9:./_-]{0,127}$`)
var nativePattern = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$`)

func text(v any) string { s, _ := v.(string); return s }
func object(v any) Object {
	o, _ := v.(map[string]any)
	if o == nil {
		return Object{}
	}
	return o
}
func number(v any) float64 {
	switch n := v.(type) {
	case json.Number:
		x, _ := n.Float64()
		return x
	case float64:
		return n
	case int:
		return float64(n)
	case int64:
		return float64(n)
	}
	return 0
}
func array(v any) []any { a, _ := v.([]any); return a }
func model(v any) string {
	s := text(v)
	if !modelPattern.MatchString(s) || strings.EqualFold(s, "unknown") {
		return ""
	}
	return s
}
func clone(o Object) Object {
	n := Object{}
	for k, v := range o {
		n[k] = v
	}
	return n
}
func decode(data []byte, out any) error {
	d := json.NewDecoder(bytes.NewReader(data))
	d.UseNumber()
	if err := d.Decode(out); err != nil {
		return err
	}
	var extra any
	if d.Decode(&extra) != io.EOF {
		return errors.New("trailing JSON")
	}
	return nil
}
func Digest(v any) string {
	// The ASCII form preserves existing scoped receipt hashes. It is not an
	// authentication signature: declarations remain explicit user assertions.
	var b bytes.Buffer
	e := json.NewEncoder(&b)
	e.SetEscapeHTML(false)
	_ = e.Encode(v)
	var ascii bytes.Buffer
	for _, r := range strings.TrimSuffix(b.String(), "\n") {
		if r < 128 {
			ascii.WriteRune(r)
		} else if r <= 0xffff {
			fmt.Fprintf(&ascii, `\u%04x`, r)
		} else {
			h, l := utf16.EncodeRune(r)
			fmt.Fprintf(&ascii, `\u%04x\u%04x`, h, l)
		}
	}
	h := sha256.Sum256(ascii.Bytes())
	return hex.EncodeToString(h[:])
}
func hashText(s string) string { h := sha256.Sum256([]byte(s)); return hex.EncodeToString(h[:]) }
func expandHome(path, home string) string {
	if strings.HasPrefix(path, "~/") {
		if home == "" {
			return ""
		}
		return filepath.Join(home, path[2:])
	}
	return path
}
func realPath(path string) string {
	p, e := filepath.Abs(path)
	if e != nil {
		return ""
	}
	if x, e := filepath.EvalSymlinks(p); e == nil {
		return x
	}
	return filepath.Clean(p)
}
func within(path, root string) bool {
	if path == "" || root == "" {
		return false
	}
	r, e := filepath.Rel(realPath(root), realPath(path))
	return e == nil && r != ".." && !strings.HasPrefix(r, ".."+string(filepath.Separator)) && !filepath.IsAbs(r)
}
func stamp(v any) time.Time {
	s := text(v)
	for _, f := range []string{time.RFC3339Nano, "2006-01-02 15:04:05.999999999Z07:00", "2006-01-02T15:04:05.999999999", "2006-01-02 15:04:05.999999999"} {
		t, e := time.ParseInLocation(f, s, time.Local)
		if e == nil {
			return t
		}
	}
	return time.Time{}
}
func seconds(t time.Time) float64 { return float64(t.UnixNano()) / 1e9 }
func fresh(at, now time.Time) bool {
	return !at.IsZero() && !at.After(now) && now.Sub(at) <= 5*time.Minute
}
func afterStart(at time.Time, p Process) bool {
	return !at.IsZero() && !p.StartTime.IsZero() && !at.Before(p.StartTime.Add(-2*time.Second))
}

// Every subprocess has a deadline and an output cap. Only exact caller PIDs or
// explicit repository operations are supplied by readers; never a process scan.
type cappedBuffer struct {
	buffer   bytes.Buffer
	max      int
	overflow bool
}

func (b *cappedBuffer) Write(p []byte) (int, error) {
	n := len(p)
	left := b.max - b.buffer.Len()
	if left > 0 {
		b.buffer.Write(p[:min(left, n)])
	}
	if n > left {
		b.overflow = true
	}
	return n, nil
}
func command(ctx context.Context, cwd string, env []string, limit int, args ...string) ([]byte, error) {
	if len(args) == 0 {
		return nil, errors.New("empty command")
	}
	c := exec.CommandContext(ctx, args[0], args[1:]...)
	c.Dir = cwd
	if env != nil {
		c.Env = env
	}
	c.WaitDelay = time.Second
	b := cappedBuffer{max: limit}
	c.Stdout = &b
	var stderr cappedBuffer
	stderr.max = 4096
	c.Stderr = &stderr
	err := c.Run()
	if ctx.Err() != nil {
		return nil, ctx.Err()
	}
	if b.overflow {
		return nil, errors.New("command output exceeds budget")
	}
	if err != nil {
		return nil, err
	}
	return b.buffer.Bytes(), nil
}
func boundedCommand(cwd string, env []string, timeout time.Duration, limit int, args ...string) ([]byte, error) {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()
	return command(ctx, cwd, env, limit, args...)
}
func regular(path string, private bool) bool {
	s, e := os.Lstat(path)
	return e == nil && s.Mode().IsRegular() && ownedFile(s, private)
}
func readSmall(path string, limit int, private bool) ([]byte, error) {
	if !regular(path, private) {
		return nil, errors.New("file unavailable")
	}
	f, e := os.Open(path)
	if e != nil {
		return nil, e
	}
	defer f.Close()
	s, e := f.Stat()
	if e != nil || s.Size() > int64(limit) {
		return nil, errors.New("file exceeds budget")
	}
	data, e := io.ReadAll(io.LimitReader(f, int64(limit)+1))
	if len(data) > limit {
		return nil, errors.New("file exceeds budget")
	}
	return data, e
}
