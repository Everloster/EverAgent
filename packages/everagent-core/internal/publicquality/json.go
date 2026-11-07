package publicquality

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"math"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"
)

type Object = map[string]any

// Duplicate keys and trailing JSON are errors, not a choice of two different
// policy/credential values by two consumers.
func DecodeJSON(data []byte) (any, error) {
	if !utf8.Valid(data) {
		return nil, errors.New("invalid-json-encoding")
	}
	d := json.NewDecoder(bytes.NewReader(data))
	d.UseNumber()
	var read func(int) (any, error)
	read = func(depth int) (any, error) {
		if depth > 64 {
			return nil, errors.New("json-depth")
		}
		t, e := d.Token()
		if e != nil {
			return nil, e
		}
		switch t {
		case json.Delim('{'):
			m := Object{}
			for d.More() {
				k, e := d.Token()
				if e != nil {
					return nil, e
				}
				key, ok := k.(string)
				if !ok {
					return nil, errors.New("json-key")
				}
				if _, ok := m[key]; ok {
					return nil, errors.New("duplicate-json-key")
				}
				v, e := read(depth + 1)
				if e != nil {
					return nil, e
				}
				m[key] = v
			}
			t, e = d.Token()
			if e != nil || t != json.Delim('}') {
				return nil, errors.New("json-object")
			}
			return m, nil
		case json.Delim('['):
			a := []any{}
			for d.More() {
				v, e := read(depth + 1)
				if e != nil {
					return nil, e
				}
				a = append(a, v)
			}
			t, e = d.Token()
			if e != nil || t != json.Delim(']') {
				return nil, errors.New("json-array")
			}
			return a, nil
		default:
			if _, ok := t.(json.Delim); ok {
				return nil, errors.New("json-delimiter")
			}
			return t, nil
		}
	}
	v, e := read(0)
	if e != nil {
		return nil, e
	}
	if _, e = d.Token(); e != io.EOF {
		return nil, errors.New("trailing-json")
	}
	return v, nil
}

func JSON(s *Snapshot, p string) (Object, error) {
	b, e := s.Bytes(p, TextLimit)
	if e != nil {
		return nil, e
	}
	v, e := DecodeJSON(b)
	m, ok := v.(Object)
	if e != nil || !ok {
		return nil, errors.New("json-object-required")
	}
	return m, nil
}
func obj(v any) Object  { m, _ := v.(Object); return m }
func array(v any) []any { a, _ := v.([]any); return a }
func number(v any) (float64, bool) {
	switch n := v.(type) {
	case json.Number:
		f, e := n.Float64()
		return f, e == nil && !math.IsNaN(f) && !math.IsInf(f, 0)
	case float64:
		return n, !math.IsNaN(n) && !math.IsInf(n, 0)
	case int:
		return float64(n), true
	}
	return 0, false
}
func integer(v any) (int, bool) {
	n, ok := number(v)
	return int(n), ok && math.Trunc(n) == n && n >= 0 && n <= float64(math.MaxInt32)
}
func contains(v any, want string) bool {
	for _, x := range array(v) {
		if str(x) == want {
			return true
		}
	}
	return false
}
func stringsOf(v any) []string {
	out := []string{}
	for _, x := range array(v) {
		if s, ok := x.(string); ok {
			out = append(out, s)
		}
	}
	return out
}
func nonempty(v any) bool { return strings.TrimSpace(str(v)) != "" }
func nested(v any, keys ...string) any {
	for _, k := range keys {
		v = obj(v)[k]
	}
	return v
}

// The archived policy contract predates this Go implementation and hashes
// sorted UTF-8 JSON without HTML escaping. Keep those receipts valid.
func canonical(v any) ([]byte, error) {
	var b strings.Builder
	quote := func(s string) {
		b.WriteByte('"')
		for _, r := range s {
			switch r {
			case '"', '\\':
				b.WriteByte('\\')
				b.WriteRune(r)
			case '\b':
				b.WriteString("\\b")
			case '\f':
				b.WriteString("\\f")
			case '\n':
				b.WriteString("\\n")
			case '\r':
				b.WriteString("\\r")
			case '\t':
				b.WriteString("\\t")
			default:
				if r < 32 {
					b.WriteString("\\u00")
					b.WriteString("0123456789abcdef"[byte(r)>>4 : byte(r)>>4+1])
					b.WriteString("0123456789abcdef"[byte(r)&15 : byte(r)&15+1])
				} else {
					b.WriteRune(r)
				}
			}
		}
		b.WriteByte('"')
	}
	var write func(any) error
	write = func(v any) error {
		switch x := v.(type) {
		case nil:
			b.WriteString("null")
		case bool:
			if x {
				b.WriteString("true")
			} else {
				b.WriteString("false")
			}
		case string:
			quote(x)
		case Object:
			keys := make([]string, 0, len(x))
			for k := range x {
				keys = append(keys, k)
			}
			sort.Strings(keys)
			b.WriteByte('{')
			for i, k := range keys {
				if i > 0 {
					b.WriteByte(',')
				}
				quote(k)
				b.WriteByte(':')
				if e := write(x[k]); e != nil {
					return e
				}
			}
			b.WriteByte('}')
		case []any:
			b.WriteByte('[')
			for i, v := range x {
				if i > 0 {
					b.WriteByte(',')
				}
				if e := write(v); e != nil {
					return e
				}
			}
			b.WriteByte(']')
		case json.Number:
			if !strings.ContainsAny(string(x), ".eE") {
				if x == "-0" {
					b.WriteByte('0')
				} else {
					b.WriteString(string(x))
				}
				break
			}
			n, ok := number(x)
			if !ok {
				return errors.New("invalid-number")
			}
			a := math.Abs(n)
			format := byte('f')
			if a != 0 && (a < 1e-4 || a >= 1e16) {
				format = 'e'
			}
			s := strconv.FormatFloat(n, format, -1, 64)
			if format == 'f' && !strings.Contains(s, ".") {
				s += ".0"
			}
			b.WriteString(s)
		default:
			return errors.New("unsupported-canonical-json-value")
		}
		return nil
	}
	if e := write(v); e != nil {
		return nil, e
	}
	return []byte(b.String()), nil
}
func canonicalDigest(v any) string {
	b, e := canonical(v)
	if e != nil {
		return ""
	}
	return digest(b)
}
