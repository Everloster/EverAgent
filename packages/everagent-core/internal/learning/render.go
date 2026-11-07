package learning

import (
	"bytes"
	"errors"
	"html"
	"net/url"
	"path"
	"strconv"
	"strings"
	"unicode"

	"github.com/Everloster/EverAgent/packages/everagent-core/internal/publicquality"
	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/ast"
	"github.com/yuin/goldmark/extension"
	"github.com/yuin/goldmark/renderer"
	mdhtml "github.com/yuin/goldmark/renderer/html"
	mdtext "github.com/yuin/goldmark/text"
	"github.com/yuin/goldmark/util"
	nethtml "golang.org/x/net/html"
	"golang.org/x/net/html/atom"
)

func localTarget(current, raw string) (string, string) {
	if strings.Contains(raw, "\\") || strings.IndexFunc(raw, unicode.IsControl) >= 0 {
		return "", ""
	}
	u, err := url.Parse(raw)
	if err != nil || u.Scheme != "" || u.Host != "" || u.Opaque != "" || strings.HasPrefix(u.Path, "/") || u.Path == "" {
		return "", ""
	}
	target := path.Clean(path.Join(path.Dir(current), u.Path))
	if !safePath(target) {
		return "", ""
	}
	return target, u.Fragment
}

func (r *Reader) link(current, raw string) string {
	raw = strings.TrimSpace(raw)
	if strings.HasPrefix(raw, "#") {
		u, err := url.Parse(raw)
		if err != nil || strings.IndexFunc(u.Fragment, unicode.IsControl) >= 0 {
			return ""
		}
		return "#" + url.PathEscape(u.Fragment)
	}
	if publicURL(raw) != "" {
		return raw
	}
	target, fragment := localTarget(current, raw)
	if target == "" || !r.exists(target) {
		return ""
	}
	suffix := ""
	if fragment != "" {
		suffix = "#" + url.PathEscape(fragment)
	}
	if _, ok := publicquality.CollectionFor(target); ok || pinFor(target) != nil {
		return "dashboard?report=" + url.QueryEscape(target) + suffix
	}
	return blobURL(target) + suffix
}
func (r *Reader) image(current, raw string) string {
	if publicURL(raw) != "" {
		return raw
	}
	target, _ := localTarget(current, raw)
	if target == "" {
		return ""
	}
	// Use the HTTP allowlist and the same confined file open, without loading
	// every image into memory just to render a report. HTTP checks it again.
	if _, err := assetMIME(target); err != nil {
		return ""
	}
	f, err := r.file(target)
	if err != nil {
		return ""
	}
	defer f.Close()
	info, err := f.Stat()
	if err != nil || info.Size() > assetLimit {
		return ""
	}
	return "api/asset?path=" + url.QueryEscape(target)
}

func nodeText(n ast.Node, source []byte) string {
	return html.UnescapeString(string(util.UnescapePunctuations(n.Text(source))))
}

func (r *Reader) render(body, current string, pinned bool) (string, []Object, error) {
	// CommonMark/GFM and footnotes are maintained upstream. Raw HTML is disabled
	// for reports. The two fixed lists need details/summary; their rendered HTML
	// still passes the same strict tag/attribute/URL projection below.
	md := goldmark.New(goldmark.WithExtensions(extension.GFM, extension.Footnote))
	if pinned {
		md.Renderer().AddOptions(mdhtml.WithUnsafe())
	} else {
		md.Renderer().AddOptions(renderer.WithNodeRenderers(util.Prioritized(rawRenderer{}, 100)))
	}
	source := []byte(body)
	document := md.Parser().Parse(mdtext.NewReader(source))
	headings := []Object{}
	used := map[string]bool{}
	_ = ast.Walk(document, func(n ast.Node, entering bool) (ast.WalkStatus, error) {
		if !entering {
			return ast.WalkContinue, nil
		}
		if heading, ok := n.(*ast.Heading); ok {
			title := nodeText(heading, source)
			base := publicquality.HeadingSlug(title)
			if base == "" {
				base = "section"
			}
			id := base
			for i := 1; used[id]; i++ {
				id = base + "-" + strconv.Itoa(i)
			}
			used[id] = true
			heading.SetAttributeString("id", []byte(id))
			if heading.Level <= 3 && len(headings) < 40 {
				headings = append(headings, Object{"level": heading.Level, "text": title})
			}
		}
		return ast.WalkContinue, nil
	})
	var rendered bytes.Buffer
	if md.Renderer().Render(&rendered, source, document) != nil {
		return "", nil, errors.New("render_failed")
	}
	nodes, err := nethtml.ParseFragment(&rendered, &nethtml.Node{Type: nethtml.ElementNode, Data: "div", DataAtom: atom.Div})
	if err != nil {
		return "", nil, errors.New("render_failed")
	}
	var output bytes.Buffer
	for _, node := range nodes {
		clean, err := r.cleanHTML(node, current, pinned, 0)
		if err != nil {
			return "", nil, err
		}
		if clean != nil {
			if nethtml.Render(&output, clean) != nil {
				return "", nil, errors.New("render_failed")
			}
		}
	}
	return output.String(), headings, nil
}

var allowedTags = map[string]bool{}

// Reports retain raw HTML as readable text, except a bare named anchor. This
// keeps old anchor links working without enabling arbitrary report HTML.
type rawRenderer struct{}

func (rawRenderer) RegisterFuncs(reg renderer.NodeRendererFuncRegisterer) {
	reg.Register(ast.KindRawHTML, renderRaw)
	reg.Register(ast.KindHTMLBlock, renderRaw)
}
func renderRaw(w util.BufWriter, source []byte, n ast.Node, entering bool) (ast.WalkStatus, error) {
	if !entering {
		return ast.WalkContinue, nil
	}
	var raw string
	switch node := n.(type) {
	case *ast.RawHTML:
		raw = string(node.Segments.Value(source))
	case *ast.HTMLBlock:
		raw = string(node.Lines().Value(source))
		if node.HasClosure() {
			raw += string(node.ClosureLine.Value(source))
		}
	}
	value, ok := safeAnchor(raw)
	if !ok {
		value = html.EscapeString(raw)
	}
	_, err := w.WriteString(value)
	return ast.WalkSkipChildren, err
}
func safeAnchor(raw string) (string, bool) {
	z := nethtml.NewTokenizer(strings.NewReader(strings.TrimSpace(raw)))
	var out strings.Builder
	count := 0
	for {
		switch z.Next() {
		case nethtml.StartTagToken:
			t := z.Token()
			if t.Data != "a" || len(t.Attr) != 1 || count != 0 {
				return "", false
			}
			a := t.Attr[0]
			if a.Key != "id" && a.Key != "name" || a.Val == "" || len(a.Val) > 512 || strings.IndexFunc(a.Val, func(r rune) bool { return unicode.IsSpace(r) || unicode.IsControl(r) }) >= 0 {
				return "", false
			}
			out.WriteString(`<a id="` + html.EscapeString(a.Val) + `">`)
			count++
		case nethtml.EndTagToken:
			if z.Token().Data != "a" {
				return "", false
			}
			out.WriteString("</a>")
		case nethtml.ErrorToken:
			return out.String(), out.Len() != 0
		default:
			return "", false
		}
	}
}

func init() {
	for _, name := range strings.Fields("p div section h1 h2 h3 h4 h5 h6 ul ol li blockquote pre code em strong del s a img br hr table thead tbody tr th td sup sub") {
		allowedTags[name] = true
	}
}

func (r *Reader) cleanHTML(node *nethtml.Node, current string, pinned bool, depth int) (*nethtml.Node, error) {
	if depth > 256 {
		return nil, errors.New("render_too_deep")
	}
	if node.Type == nethtml.TextNode {
		return &nethtml.Node{Type: nethtml.TextNode, Data: node.Data}, nil
	}
	if node.Type != nethtml.ElementNode || !(allowedTags[node.Data] || pinned && (node.Data == "details" || node.Data == "summary")) {
		return nil, nil
	}
	clean := &nethtml.Node{Type: nethtml.ElementNode, Data: node.Data, DataAtom: node.DataAtom}
	add := func(key, value string) {
		if value != "" {
			clean.Attr = append(clean.Attr, nethtml.Attribute{Key: key, Val: value})
		}
	}
	for _, attr := range node.Attr {
		switch attr.Key {
		case "href":
			if node.Data == "a" {
				add("href", r.link(current, attr.Val))
			}
		case "src":
			if node.Data == "img" {
				add("src", r.image(current, attr.Val))
			}
		case "alt", "title":
			add(attr.Key, attr.Val)
		case "id":
			if len(attr.Val) <= 512 && strings.IndexFunc(attr.Val, unicode.IsControl) < 0 {
				add("id", attr.Val)
			}
		case "class":
			if attr.Val == "footnotes" || attr.Val == "footnote-ref" || attr.Val == "footnote-backref" || node.Data == "code" && strings.HasPrefix(attr.Val, "language-") {
				add("class", attr.Val)
			}
		case "align":
			if (node.Data == "td" || node.Data == "th") && (attr.Val == "left" || attr.Val == "center" || attr.Val == "right") {
				add("align", attr.Val)
			}
		case "open":
			if node.Data == "details" {
				clean.Attr = append(clean.Attr, nethtml.Attribute{Key: "open"})
			}
		case "start":
			if node.Data == "ol" {
				if n, err := strconv.Atoi(attr.Val); err == nil && n >= 0 {
					add("start", attr.Val)
				}
			}
		}
	}
	if node.Data == "a" {
		add("rel", "noreferrer noopener")
	}
	if node.Data == "img" {
		add("loading", "lazy")
	}
	for child := node.FirstChild; child != nil; child = child.NextSibling {
		next, err := r.cleanHTML(child, current, pinned, depth+1)
		if err != nil {
			return nil, err
		}
		if next != nil {
			clean.AppendChild(next)
		}
	}
	return clean, nil
}
