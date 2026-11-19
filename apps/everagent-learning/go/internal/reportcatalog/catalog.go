package reportcatalog

import (
	"errors"
	"fmt"
	"path"
	"regexp"
	"sort"
	"strings"

	"go.yaml.in/yaml/v3"
)

type Collection struct{ ID, Title, Emoji, Root string }

var Collections = []Collection{
	{"ai-learning", "AI Learning", "🤖", "ai-learning/reports"},
	{"cs-learning", "CS Learning", "💻", "cs-learning/reports"},
	{"philosophy-learning", "Philosophy Learning", "📚", "philosophy-learning/reports"},
	{"psychology-learning", "Psychology Learning", "🧠", "psychology-learning/reports"},
	{"biology-learning", "Biology Learning", "🧬", "biology-learning/reports"},
	{"ai-practice", "AI Practice", "⚗️", "ai-practice/experiments"},
	{"podcast-learning", "Podcast Learning", "🎙️", "podcast-learning/reports"},
	{"github-trending-analyzer", "GitHub Research", "🔭", "github-trending-analyzer/reports"},
	{"web-surfing", "Web Surfing", "🏄", "web-surfing/reports"},
}

func CollectionFor(p string) (Collection, bool) {
	if !safePath(p) || strings.ToLower(path.Ext(p)) != ".md" {
		return Collection{}, false
	}
	for _, c := range Collections {
		if !strings.HasPrefix(p, c.Root+"/") {
			continue
		}
		rel := strings.TrimPrefix(p, c.Root+"/")
		if c.ID == "podcast-learning" {
			for _, part := range strings.Split(rel, "/") {
				if part == "transcripts" {
					return Collection{}, false
				}
			}
		}
		if c.ID == "ai-practice" && !(strings.HasPrefix(rel, "exp_") && !strings.Contains(rel, "/") || strings.HasPrefix(path.Base(rel), "评估笔记")) {
			return Collection{}, false
		}
		return c, true
	}
	return Collection{}, false
}

type Metadata map[string]any

func str(v any) string                      { s, _ := v.(string); return s }
func (m Metadata) String(key string) string { return str(m[key]) }

var aliases = map[string]map[string]string{"status": {"complete": "completed", "done": "completed"}, "report_type": {"概念深度解析": "concept_report", "concept_deep_dive": "concept_report", "ai_news_daily": "daily_summary", "daily_digest": "daily_summary"}}

func normalize(m Metadata) Metadata {
	n := Metadata{}
	for k, v := range m {
		n[k] = v
	}
	for k, values := range aliases {
		if v, ok := values[str(n[k])]; ok {
			n[k] = v
		}
	}
	return n
}

// Use the maintained YAML parser, but keep scalar frontmatter values as text.
// Aliases, duplicate keys and nested depth bombs are not report metadata.
func yamlValue(n *yaml.Node, depth int) (any, error) {
	if depth > 24 {
		return nil, errors.New("metadata-depth")
	}
	switch n.Kind {
	case yaml.MappingNode:
		m := map[string]any{}
		for i := 0; i < len(n.Content); i += 2 {
			k := n.Content[i]
			if k.Kind != yaml.ScalarNode || k.Value == "" {
				return nil, errors.New("metadata-key")
			}
			if _, ok := m[k.Value]; ok {
				return nil, errors.New("duplicate-metadata-key")
			}
			v, e := yamlValue(n.Content[i+1], depth+1)
			if e != nil {
				return nil, e
			}
			m[k.Value] = v
		}
		return m, nil
	case yaml.SequenceNode:
		a := []any{}
		for _, child := range n.Content {
			v, e := yamlValue(child, depth+1)
			if e != nil {
				return nil, e
			}
			a = append(a, v)
		}
		return a, nil
	case yaml.ScalarNode:
		return n.Value, nil
	default:
		return nil, errors.New("metadata-alias-or-unsupported-node")
	}
}
func ParseFrontmatter(text string) (Metadata, error) {
	lines := strings.Split(text, "\n")
	if len(lines) == 0 || strings.TrimSpace(lines[0]) != "---" {
		return Metadata{}, nil
	}
	end := -1
	for i := 1; i < len(lines); i++ {
		if strings.TrimSpace(lines[i]) == "---" {
			end = i
			break
		}
	}
	if end < 0 {
		return nil, errors.New("frontmatter-not-closed")
	}
	header := strings.Join(lines[1:end], "\n")
	if len(header) > 64<<10 {
		return nil, errors.New("frontmatter-budget")
	}
	if strings.TrimSpace(header) == "" {
		return Metadata{}, nil
	}
	var root yaml.Node
	if yaml.Unmarshal([]byte(header), &root) != nil || len(root.Content) != 1 {
		return nil, errors.New("invalid-frontmatter-yaml")
	}
	v, e := yamlValue(root.Content[0], 0)
	m, ok := v.(map[string]any)
	if e != nil || !ok {
		return nil, errors.New("invalid-frontmatter-mapping")
	}
	return Metadata(m), nil
}

type Report struct {
	Path           string   `json:"path"`
	Domain         string   `json:"domain"`
	Title          string   `json:"title"`
	UpdatedOn      string   `json:"updated_on"`
	Tags           []string `json:"tags"`
	Metadata       Metadata `json:"metadata"`
	RawMetadata    Metadata `json:"raw_metadata"`
	MetadataStatus string   `json:"metadata_status"`
}

var isoDate = regexp.MustCompile(`^\d{4}-\d{2}-\d{2}$`)
var filenameDate = regexp.MustCompile(`\d{4}-\d{2}-\d{2}`)
var footerDate = regexp.MustCompile(`报告生成时间[:：]\s*(\d{4}-\d{2}-\d{2})`)
var titleLine = regexp.MustCompile(`(?m)^#\s+([^\r\n]+)`)
var chapterFile = regexp.MustCompile(`^AI演义_(\d{2})_`)
var chapterTitle = regexp.MustCompile(`^(?:《AI演义》|AI演义)\s*[·｜|]?\s*(\d+)\s*[·｜|:：]?\s*`)

func displayTitle(p, title string) string {
	c := chapterFile.FindStringSubmatch(path.Base(p))
	if c == nil {
		return title
	}
	m := chapterTitle.FindStringSubmatchIndex(title)
	if m != nil {
		n := strings.TrimLeft(title[m[2]:m[3]], "0")
		want := strings.TrimLeft(c[1], "0")
		if n != want {
			return title
		}
		title = title[m[1]:]
	}
	return "《AI演义》" + c[1] + "｜" + title
}
func info(p, text, fallback string) (Report, error) {
	r := Report{Path: p, Tags: []string{}}
	c, ok := CollectionFor(p)
	if !ok {
		return r, errors.New("not-a-report")
	}
	r.Domain = c.ID
	m, e := ParseFrontmatter(text)
	if e != nil {
		// Old unversioned reports contain malformed optional YAML fields. Keep
		// their discoverable scalar metadata visible without repairing history
		// or claiming a valid contract. The reader does not audit or repair reports.
		m = partialMetadata(text)
		r.MetadataStatus = "partial-invalid-yaml"
	} else {
		r.MetadataStatus = "parsed"
	}
	r.RawMetadata = m
	r.Metadata = normalize(m)
	r.Title = str(r.Metadata["title"])
	if r.Title == "" {
		if m := titleLine.FindStringSubmatch(text); m != nil {
			r.Title = strings.TrimSpace(m[1])
		} else {
			r.Title = strings.TrimSuffix(path.Base(p), path.Ext(p))
		}
	}
	r.Title = displayTitle(p, r.Title)
	r.UpdatedOn = r.Metadata.String("updated_on")
	if r.UpdatedOn == "" {
		r.UpdatedOn = r.Metadata.String("created")
	}
	if !isoDate.MatchString(r.UpdatedOn) {
		if s := filenameDate.FindString(path.Base(p)); s != "" {
			r.UpdatedOn = s
		} else if m := footerDate.FindStringSubmatch(text); m != nil {
			r.UpdatedOn = m[1]
		} else if isoDate.MatchString(fallback) {
			r.UpdatedOn = fallback
		} else {
			r.UpdatedOn = ""
		}
	}
	switch tags := r.Metadata["semantic_tags"].(type) {
	case []any:
		for _, tag := range tags {
			r.Tags = append(r.Tags, fmt.Sprint(tag))
		}
	case string:
		if tags != "" {
			r.Tags = []string{tags}
		}
	}
	return r, nil
}

var scalarKey = regexp.MustCompile(`^([a-z][a-z0-9_]*):`)

func partialMetadata(text string) Metadata {
	lines := strings.Split(text, "\n")
	out := Metadata{}
	seen := map[string]bool{}
	if len(lines) == 0 || strings.TrimSpace(lines[0]) != "---" {
		return out
	}
	for _, line := range lines[1:] {
		if strings.TrimSpace(line) == "---" {
			break
		}
		m := scalarKey.FindStringSubmatch(line)
		if m == nil {
			continue
		}
		key := m[1]
		if seen[key] {
			delete(out, key)
			continue
		}
		seen[key] = true
		one, e := ParseFrontmatter("---\n" + line + "\n---\n")
		if e == nil {
			if value, ok := one[key]; ok {
				out[key] = value
			}
		}
	}
	return out
}

func fallbackDates(s *fileSource) map[string]string {
	out := map[string]string{}
	text, e := s.Text("docs/REPORT_INDEX.md")
	if e != nil {
		return out
	}
	pattern := regexp.MustCompile(`^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*\[.*\]\(([^)]+)\)\s*\|`)
	for _, line := range strings.Split(text, "\n") {
		m := pattern.FindStringSubmatch(line)
		if m == nil {
			continue
		}
		p, fragment, external, err := localTarget("docs/REPORT_INDEX.md", m[2])
		if err == nil && fragment == "" && !external && safePath(p) {
			out[p] = m[1]
		}
	}
	return out
}

func catalog(s *fileSource) ([]Report, []Finding) {
	fallback := fallbackDates(s)
	reports := []Report{}
	findings := []Finding{}
	for _, p := range s.Paths() {
		if _, ok := CollectionFor(p); !ok {
			continue
		}
		text, e := s.Text(p)
		if e != nil {
			findings = append(findings, issue(p, "REPORT_UNREADABLE", "报告不是可读的有界UTF-8普通文件。"))
			continue
		}
		r, e := info(p, text, fallback[p])
		if e != nil {
			findings = append(findings, issue(p, "REPORT_METADATA_UNREADABLE", "报告元数据无法解析。"))
			continue
		}
		if r.MetadataStatus != "parsed" {
			findings = append(findings, warning(p, "REPORT_METADATA_PARTIAL", "旧元数据含无效YAML；目录只保留无歧义的单行字段，未修写历史。"))
		}
		if r.UpdatedOn == "" {
			findings = append(findings, warning(p, "REPORT_DATE_UNKNOWN", "无元数据/文件名/旧索引日期；不以当前文件mtime伪造更新日期。"))
		}
		reports = append(reports, r)
	}
	sort.SliceStable(reports, func(i, j int) bool {
		if reports[i].UpdatedOn != reports[j].UpdatedOn {
			return reports[i].UpdatedOn > reports[j].UpdatedOn
		}
		if reports[i].Title != reports[j].Title {
			return reports[i].Title > reports[j].Title
		}
		return reports[i].Path < reports[j].Path
	})
	return reports, findings
}

// CatalogFiles parses only caller-listed files. The caller confines file opens;
// this package preserves bounded UTF-8 reads and the historical date fallback.
func CatalogFiles(paths []string, read func(string, int) ([]byte, error)) ([]Report, []Finding) {
	return catalog(newFileSource(paths, read))
}
