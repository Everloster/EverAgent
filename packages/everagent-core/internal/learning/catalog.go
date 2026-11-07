// Package learning is the local reading application's Go adapter. The shared
// report catalog owns discovery/metadata; this package owns only its JSON view,
// safe public-file reads, and rendering. It never executes a chosen checkout.
package learning

import (
	"bytes"
	"errors"
	"io"
	"io/fs"
	"net/url"
	"os"
	"path"
	"path/filepath"
	"sort"
	"strings"
	"unicode"
	"unicode/utf8"

	"github.com/Everloster/EverAgent/packages/everagent-core/internal/publicquality"
)

const publicBase = "https://github.com/Everloster/EverAgent"
const detailLimit = 2 << 20
const assetLimit = 6 << 20

type Object = map[string]any

var pins = []Object{
	{"id": "podcast-updates", "path": "podcast-learning/PODCAST_UPDATES.md", "title": "小宇宙精选播客", "domain": "podcast-learning", "domain_title": "播客学习", "note": "近期单集 · 报告状态"},
	{"id": "tech-blog-updates", "path": "web-surfing/TECH_BLOG_UPDATES.md", "title": "顶尖技术博客", "domain": "web-surfing", "domain_title": "Web 冲浪", "note": "近期文章 · 标题速览"},
}
var assetTypes = map[string]string{".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}

type Reader struct{ root *os.Root }

func Open(root string) (*Reader, error) {
	if root == "~" || strings.HasPrefix(root, "~/") {
		home, err := os.UserHomeDir()
		if err != nil {
			return nil, errors.New("repo_missing")
		}
		if root == "~" {
			root = home
		} else {
			root = filepath.Join(home, strings.TrimPrefix(root, "~/"))
		}
	}
	real, err := filepath.EvalSymlinks(root)
	if err != nil {
		return nil, errors.New("repo_missing")
	}
	r, err := os.OpenRoot(real)
	if err != nil {
		return nil, errors.New("repo_missing")
	}
	return &Reader{root: r}, nil
}
func (r *Reader) Close() error { return r.root.Close() }

func safePath(p string) bool {
	if !utf8.ValidString(p) || p == "" || strings.ContainsAny(p, "\\\x00\r\n\t:") || path.IsAbs(p) {
		return false
	}
	for _, part := range strings.Split(p, "/") {
		if part == "" || strings.HasPrefix(part, ".") {
			return false
		}
	}
	return true
}

// os.Root contains every open even when a directory is replaced concurrently.
// Component and inode checks additionally reject linked paths and hardlinks.
func (r *Reader) file(p string) (*os.File, error) {
	if !safePath(p) {
		return nil, errors.New("unsafe_path")
	}
	parts := strings.Split(p, "/")
	var before os.FileInfo
	for i := range parts {
		info, err := r.root.Lstat(strings.Join(parts[:i+1], "/"))
		if err != nil || info.Mode()&os.ModeSymlink != 0 || i < len(parts)-1 && !info.IsDir() {
			return nil, errors.New("unsafe_path")
		}
		before = info
	}
	if !before.Mode().IsRegular() {
		return nil, errors.New("unsafe_path")
	}
	f, err := openFile(r.root, p)
	if err != nil {
		return nil, errors.New("unreadable")
	}
	info, err := f.Stat()
	if err != nil || !info.Mode().IsRegular() || !os.SameFile(before, info) || !singleLink(f, info) {
		f.Close()
		return nil, errors.New("unsafe_path")
	}
	return f, nil
}
func (r *Reader) exists(p string) bool {
	f, err := r.file(p)
	if err != nil {
		return false
	}
	f.Close()
	return true
}
func (r *Reader) read(p string, limit int) ([]byte, error) {
	f, err := r.file(p)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	info, err := f.Stat()
	if err != nil {
		return nil, errors.New("unreadable")
	}
	if info.Size() > int64(limit) {
		return nil, errors.New("report_too_large")
	}
	b, err := io.ReadAll(io.LimitReader(f, int64(limit)+1))
	if err != nil {
		return nil, errors.New("unreadable")
	}
	if len(b) > limit {
		return nil, errors.New("report_too_large")
	}
	return b, nil
}

func pinFor(p string) Object {
	for _, pin := range pins {
		if pin["path"] == p {
			return pin
		}
	}
	return nil
}
func publicURL(s string) string {
	if strings.Contains(s, "\\") || strings.IndexFunc(s, unicode.IsControl) >= 0 {
		return ""
	}
	u, err := url.Parse(s)
	if err != nil || u.User != nil || u.Hostname() == "" || u.Opaque != "" || u.Scheme != "http" && u.Scheme != "https" {
		return ""
	}
	return s
}
func blobURL(p string) string {
	u, _ := url.Parse(publicBase + "/blob/main/")
	u.Path += p
	return u.String()
}
func project(report publicquality.Report) Object {
	c, _ := publicquality.CollectionFor(report.Path)
	m := report.Metadata
	out := Object{"id": report.Path, "path": report.Path, "domain": report.Domain, "domain_title": c.Title,
		"title": report.Title, "updated_on": report.UpdatedOn, "tags": report.Tags[:min(6, len(report.Tags))],
		"github_url": blobURL(report.Path), "source_url": publicURL(m.String("source_url")), "metadata_status": report.MetadataStatus}
	for _, key := range []string{"created", "status", "quality_tier", "report_depth", "report_type", "source", "show", "episode"} {
		out[key] = m.String(key)
	}
	return out
}

func (r *Reader) List() (Object, error) {
	paths := []string{"docs/REPORT_INDEX.md"}
	visited := 0
	for _, collection := range publicquality.Collections {
		// A symlinked collection root must not be walked, even if its target is
		// inside the checkout. Missing collections are normal in a new fork.
		linked := false
		parts := strings.Split(collection.Root, "/")
		for i := range parts {
			info, err := r.root.Lstat(strings.Join(parts[:i+1], "/"))
			if err != nil && !errors.Is(err, fs.ErrNotExist) {
				return nil, errors.New("catalog_unreadable")
			}
			if err != nil || !info.IsDir() || info.Mode()&os.ModeSymlink != 0 {
				linked = true
				break
			}
		}
		if linked {
			continue
		}
		err := fs.WalkDir(r.root.FS(), collection.Root, func(p string, d fs.DirEntry, err error) error {
			if err != nil {
				return errors.New("catalog_unreadable")
			}
			visited++
			if visited > 20000 {
				return errors.New("catalog_too_large")
			}
			if !safePath(p) || d.Type()&os.ModeSymlink != 0 {
				if d.IsDir() {
					return fs.SkipDir
				}
				return nil
			}
			if d.IsDir() && collection.ID == "podcast-learning" && d.Name() == "transcripts" {
				return fs.SkipDir
			}
			if !d.IsDir() {
				// Let the catalog report unreadable candidates. Filtering them
				// here would turn a failed read into an apparently complete list.
				if _, ok := publicquality.CollectionFor(p); ok {
					paths = append(paths, p)
				}
			}
			return nil
		})
		if err != nil {
			return nil, err
		}
	}
	reports, findings := publicquality.CatalogFiles(paths, r.read)
	sort.Slice(reports, func(i, j int) bool {
		if reports[i].UpdatedOn != reports[j].UpdatedOn {
			return reports[i].UpdatedOn > reports[j].UpdatedOn
		}
		return reports[i].Path > reports[j].Path
	})
	rows, domains, pinned := []Object{}, []Object{}, []Object{}
	counts := map[string]int{}
	for _, report := range reports {
		rows = append(rows, project(report))
		counts[report.Domain]++
	}
	for _, c := range publicquality.Collections {
		domains = append(domains, Object{"id": c.ID, "title": c.Title, "count": counts[c.ID]})
	}
	for _, pin := range pins {
		if r.exists(pin["path"].(string)) {
			pinned = append(pinned, pin)
		}
	}
	latest := ""
	if len(reports) > 0 {
		latest = reports[0].UpdatedOn
	}
	complete := true
	for _, finding := range findings {
		if finding.Severity == "error" {
			complete = false
		}
	}
	return Object{"repo_name": "EverAgent", "remote_base": publicBase, "domains": domains, "reports": rows, "pins": pinned,
		"total": len(rows), "latest_on": latest, "complete": complete, "warnings": findings}, nil
}

func (r *Reader) Detail(p string) (Object, error) {
	if !safePath(p) || !strings.HasSuffix(p, ".md") {
		return nil, errors.New("unsafe_path")
	}
	pin := pinFor(p)
	if _, ok := publicquality.CollectionFor(p); !ok && pin == nil {
		return nil, errors.New("unknown_collection")
	}
	raw, err := r.read(p, detailLimit)
	if err != nil {
		return nil, err
	}
	text := bytes.TrimPrefix(raw, []byte{0xef, 0xbb, 0xbf})
	if !utf8.Valid(text) || bytes.IndexByte(text, 0) >= 0 {
		return nil, errors.New("invalid_utf8")
	}
	var detail Object
	if pin != nil {
		detail = Object{"updated_on": "", "tags": []string{}, "github_url": blobURL(p), "pinned": true, "pinned_note": pin["note"]}
		for _, key := range []string{"id", "path", "title", "domain", "domain_title"} {
			detail[key] = pin[key]
		}
		for _, key := range []string{"created", "status", "quality_tier", "report_depth", "report_type", "source", "source_url", "show", "episode"} {
			detail[key] = ""
		}
	} else {
		reports, _ := publicquality.CatalogFiles([]string{p, "docs/REPORT_INDEX.md"}, func(name string, limit int) ([]byte, error) {
			if name == p {
				return raw, nil
			}
			return r.read(name, limit)
		})
		if len(reports) != 1 {
			return nil, errors.New("unreadable")
		}
		detail = project(reports[0])
	}
	body := stripFrontmatter(string(text))
	rendered, outline, err := r.render(body, p, pin != nil)
	if err != nil {
		return nil, err
	}
	detail["markdown"], detail["html"], detail["outline"] = body, rendered, outline
	detail["bytes"], detail["truncated"] = len(raw), false
	if pin != nil {
		detail["update_feed"] = r.feed(body, p)
	}
	return Object{"report": detail, "info_title": detail["title"]}, nil
}
func stripFrontmatter(text string) string {
	lines := strings.SplitAfter(text, "\n")
	if len(lines) == 0 || strings.TrimSpace(lines[0]) != "---" {
		return text
	}
	for i := 1; i < len(lines); i++ {
		if strings.TrimSpace(lines[i]) == "---" {
			return strings.Join(lines[i+1:], "")
		}
	}
	return text
}

func assetMIME(p string) (string, error) {
	allowed := strings.HasPrefix(p, "docs/assets/")
	for _, c := range publicquality.Collections {
		allowed = allowed || strings.HasPrefix(p, c.Root+"/")
	}
	for _, part := range strings.Split(p, "/") {
		if part == "transcripts" || part == "sources" || part == "raw" {
			allowed = false
		}
	}
	if !allowed {
		return "", errors.New("unsafe_path")
	}
	mime := assetTypes[strings.ToLower(path.Ext(p))]
	if mime == "" {
		return "", errors.New("unsupported_asset")
	}
	return mime, nil
}

func (r *Reader) Asset(p string) (Object, error) {
	mime, err := assetMIME(p)
	if err != nil {
		return nil, err
	}
	b, err := r.read(p, assetLimit)
	if err != nil {
		if err.Error() == "report_too_large" {
			err = errors.New("unsupported_asset")
		}
		return nil, err
	}
	return Object{"mime": mime, "data": b}, nil
}
