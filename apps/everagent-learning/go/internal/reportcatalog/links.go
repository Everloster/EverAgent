package reportcatalog

import (
	"errors"
	"html"
	"net/url"
	"path"
	"regexp"
	"strings"
	"unicode"
)

var htmlTags = regexp.MustCompile(`<[^>]*>`)

// HeadingSlug preserves the existing report-reader anchor convention.
func HeadingSlug(s string) string {
	s = strings.ToLower(html.UnescapeString(htmlTags.ReplaceAllString(s, "")))
	s = strings.Map(func(r rune) rune {
		if r == '-' || r == '_' {
			return r
		}
		if unicode.IsPunct(r) || unicode.IsSymbol(r) || unicode.IsControl(r) {
			return -1
		}
		if r == ' ' {
			return '-'
		}
		return r
	}, s)
	return s
}

var escapedDestination = regexp.MustCompile(`\\([() ])`)

// Historical index destinations use the original local URL decoding rules;
// this only resolves identities in the caller-listed source, never opens files.
func localTarget(file, target string) (p, fragment string, external bool, err error) {
	target = html.UnescapeString(escapedDestination.ReplaceAllString(target, "$1"))
	u, e := url.Parse(target)
	if e != nil {
		return "", "", false, e
	}
	if u.Scheme != "" || u.Host != "" || strings.HasPrefix(target, "//") {
		return "", "", true, nil
	}
	p = file
	if u.Path != "" {
		if strings.HasPrefix(u.Path, "/") {
			p = path.Clean(strings.TrimLeft(u.Path, "/"))
		} else {
			p = path.Clean(path.Join(path.Dir(file), u.Path))
		}
	}
	if p != "." && !safePath(p) {
		return "", "", false, errors.New("outside-repository")
	}
	return p, u.Fragment, false, nil
}
