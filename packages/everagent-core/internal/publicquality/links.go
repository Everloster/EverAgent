package publicquality

import (
	"bytes"
	"errors"
	"html"
	"io"
	"net/url"
	"path"
	"regexp"
	"strconv"
	"strings"
	"unicode"

	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/ast"
	"github.com/yuin/goldmark/extension"
	mdtext "github.com/yuin/goldmark/text"
	"github.com/yuin/goldmark/util"
	nethtml "golang.org/x/net/html"
)

var errPath = errors.New("outside-repository")

func itoa(n int) string { return strconv.Itoa(n) }
func blank(s string) string {
	return strings.Map(func(r rune) rune {
		if r == '\n' {
			return r
		}
		return ' '
	}, s)
}

var comments = regexp.MustCompile(`(?s)<!--.*?(?:-->|$)`)
var fenceStart = regexp.MustCompile(`^[ ]{0,3}(\x60{3,}|~{3,})`)

// This checker is local-only. Ignore examples/comments without losing line
// numbers; it never follows an HTTP link or executes a report.
func prose(text string, inline bool) string {
	text = comments.ReplaceAllStringFunc(text, blank)
	lines := strings.SplitAfter(text, "\n")
	fence := ""
	for i, line := range lines {
		m := fenceStart.FindStringSubmatch(line)
		if fence != "" {
			lines[i] = blank(line)
			trim := strings.TrimSpace(line)
			if len(trim) >= len(fence) && strings.Trim(trim, string(fence[0])) == "" {
				fence = ""
			}
		} else if m != nil {
			fence = m[1]
			lines[i] = blank(line)
		} else if (strings.HasPrefix(line, "    ") || strings.HasPrefix(line, "\t")) && !strings.HasPrefix(strings.TrimSpace(line), "<") {
			lines[i] = blank(line)
		}
	}
	text = strings.Join(lines, "")
	if !inline {
		return text
	}
	b := []byte(text)
	for i := 0; i < len(b); i++ {
		if b[i] != '`' {
			continue
		}
		n := 1
		for i+n < len(b) && b[i+n] == '`' {
			n++
		}
		end := -1
		for j := i + n; j < len(b); j++ {
			if b[j] != '`' {
				continue
			}
			k := j
			for k < len(b) && b[k] == '`' {
				k++
			}
			if k-j == n {
				end = k
				break
			}
			j = k - 1
		}
		if end < 0 {
			i += n - 1
			continue
		}
		for j := i; j < end; j++ {
			if b[j] != '\n' {
				b[j] = ' '
			}
		}
		i = end - 1
	}
	return string(b)
}

type Link struct {
	Line   int
	Target string
}

func htmlParts(text string) ([]Link, map[string]bool) {
	z := nethtml.NewTokenizer(strings.NewReader(text))
	links := []Link{}
	anchors := map[string]bool{}
	offset := 0
	for {
		kind := z.Next()
		start := offset
		offset += len(z.Raw())
		if kind == nethtml.ErrorToken {
			if z.Err() == io.EOF {
				break
			}
			break
		}
		if kind != nethtml.StartTagToken && kind != nethtml.SelfClosingTagToken {
			continue
		}
		t := z.Token()
		line := 1 + strings.Count(text[:min(start, len(text))], "\n")
		for _, a := range t.Attr {
			if a.Key == "id" || t.Data == "a" && a.Key == "name" {
				anchors[a.Val] = true
			}
			switch a.Key {
			case "href", "src", "poster":
				if a.Val != "" {
					links = append(links, Link{line, a.Val})
				}
			case "srcset":
				for _, token := range strings.Fields(a.Val) {
					if strings.HasPrefix(token, "data:") {
						continue
					}
					for _, candidate := range strings.Split(token, ",") {
						if candidate != "" && !srcsetSize.MatchString(candidate) {
							links = append(links, Link{line, candidate})
						}
					}
				}
			}
		}
	}
	return links, anchors
}

var srcsetSize = regexp.MustCompile(`^[\d.]+[wx]$`)
var htmlTags = regexp.MustCompile(`<[^>]*>`)

func headingSlug(s string) string {
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

// HeadingSlug is shared by the local reader and the offline anchor checker.
func HeadingSlug(s string) string { return headingSlug(s) }

// Use CommonMark/GFM rather than treating every bracket pair as a link.
// In particular a footnote's body is prose containing links, not a reference
// destination. Unresolved reference labels render as text, not clickable URLs.
func markdownParts(text string) ([]Link, map[string]bool) {
	source := []byte(text)
	document := goldmark.New(goldmark.WithExtensions(extension.GFM, extension.Footnote)).Parser().Parse(mdtext.NewReader(source))
	links, anchors := []Link{}, map[string]bool{}
	used := map[string]bool{}
	_ = ast.Walk(document, func(n ast.Node, entering bool) (ast.WalkStatus, error) {
		if !entering {
			return ast.WalkContinue, nil
		}
		line := 1 + bytes.Count(source[:min(nodeOffset(n), len(source))], []byte{'\n'})
		htmlText := []byte(nil)
		switch v := n.(type) {
		case *ast.Link:
			links = append(links, Link{line, string(util.UnescapePunctuations(v.Destination))})
		case *ast.Image:
			links = append(links, Link{line, string(util.UnescapePunctuations(v.Destination))})
		case *ast.RawHTML:
			htmlText = v.Segments.Value(source)
		case *ast.HTMLBlock:
			htmlText = v.Lines().Value(source)
			if v.HasClosure() {
				htmlText = append(htmlText, v.ClosureLine.Value(source)...)
			}
		case *ast.Heading:
			base := headingSlug(string(v.Text(source)))
			slug := base
			for n := 1; used[slug]; n++ {
				slug = base + "-" + itoa(n)
			}
			used[slug], anchors[slug] = true, true
		}
		if len(htmlText) > 0 {
			local, ids := htmlParts(string(htmlText))
			for _, link := range local {
				link.Line += line - 1
				links = append(links, link)
			}
			for id := range ids {
				anchors[id] = true
			}
		}
		return ast.WalkContinue, nil
	})
	return links, anchors
}

func nodeOffset(n ast.Node) int {
	if n == nil {
		return 0
	}
	switch v := n.(type) {
	case *ast.Text:
		return v.Segment.Start
	case *ast.RawHTML:
		if v.Segments.Len() > 0 {
			return v.Segments.At(0).Start
		}
	}
	if n.Type() != ast.TypeInline && n.Lines().Len() > 0 {
		return n.Lines().At(0).Start
	}
	if child := n.FirstChild(); child != nil {
		return nodeOffset(child)
	}
	// Synthetic footnote controls have no source segments.
	return 0
}

func Anchors(text string) map[string]bool { _, anchors := markdownParts(text); return anchors }
func LocalLinks(text string) []Link       { links, _ := markdownParts(text); return links }

var escapedDestination = regexp.MustCompile(`\\([() ])`)

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
		return "", "", false, errPath
	}
	return p, u.Fragment, false, nil
}
func CheckLinks(s *Snapshot, file string, anchors bool) []Finding {
	text, e := s.Text(file)
	if e != nil {
		return []Finding{issue(file, "UNREADABLE_DOCUMENT", "本地链接检查的文档不可读。")}
	}
	out := []Finding{}
	cache := map[string]map[string]bool{}
	for _, link := range LocalLinks(text) {
		p, fragment, external, e := localTarget(file, link.Target)
		if external {
			continue
		}
		valid := e == nil && (s.Has(p) || s.Dir(p))
		if row, ok := s.entries[p]; ok && row.Mode != "100644" && row.Mode != "100755" {
			valid = false
		}
		if valid && anchors && fragment != "" {
			if s.Dir(p) {
				p = path.Join(p, "README.md")
			}
			if containsString([]string{".md", ".markdown", ".html", ".htm"}, strings.ToLower(path.Ext(p))) {
				if _, ok := cache[p]; !ok {
					body, readErr := s.Text(p)
					if readErr != nil {
						valid = false
					} else {
						cache[p] = Anchors(body)
					}
				}
				valid = valid && cache[p][fragment]
			}
		}
		if !valid {
			f := issue(file, "INVALID_LOCAL_LINK", "本地链接、媒体或锚点不可用。")
			f.Line = link.Line
			out = append(out, f)
		}
	}
	return out
}
