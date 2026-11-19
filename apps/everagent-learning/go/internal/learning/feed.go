package learning

import (
	"html"
	"io"
	"net/url"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/ast"
	"github.com/yuin/goldmark/extension"
	extast "github.com/yuin/goldmark/extension/ast"
	mdtext "github.com/yuin/goldmark/text"
	nethtml "golang.org/x/net/html"
)

var checkedDate = regexp.MustCompile(`最近检查[：:]\s*(?:\*\*)?(\d{4}-\d{2}-\d{2})`)
var monthHeading = regexp.MustCompile(`^(\d{4})\s*年\s*(\d{1,2})\s*月$`)
var monthDay = regexp.MustCompile(`^(\d{2})-(\d{2})$`)

type feedLink struct{ title, url, original string }

func linksIn(n ast.Node, source []byte) []feedLink {
	links := []feedLink{}
	if n == nil {
		return links
	}
	_ = ast.Walk(n, func(child ast.Node, entering bool) (ast.WalkStatus, error) {
		if entering {
			if link, ok := child.(*ast.Link); ok {
				links = append(links, feedLink{nodeText(link, source), html.UnescapeString(string(link.Destination)), html.UnescapeString(string(link.Title))})
			}
		}
		return ast.WalkContinue, nil
	})
	return links
}

// A title feed is a projection of the two existing living lists, not a fetcher
// or a second report store. Month headings own publication years; check dates
// describe freshness only. The later per-show table owns a podcast's status.
func (r *Reader) feed(body, current string) Object {
	// The living lists also contain compact details/summary blocks without a
	// blank before their table/list. Add parser-only boundaries; the original
	// Markdown remains unchanged in the detail response. Fenced samples remain
	// fenced and are still ignored by the Markdown parser.
	lines := strings.Split(body, "\n")
	for i, line := range lines {
		trim := strings.ToLower(strings.TrimSpace(line))
		if strings.HasPrefix(trim, "<summary>") || strings.HasPrefix(trim, "<details") || trim == "</details>" {
			lines[i] = "\n" + line + "\n"
		}
	}
	source := []byte(strings.Join(lines, "\n"))
	doc := goldmark.New(goldmark.WithExtensions(extension.GFM)).Parser().Parse(mdtext.NewReader(source))
	kind, channel, checked := "blog", "", ""
	if strings.HasPrefix(current, "podcast-learning/") {
		kind = "podcast"
	}
	if m := checkedDate.FindStringSubmatch(body); m != nil {
		if d, err := time.Parse("2006-01-02", m[1]); err == nil {
			checked = d.Format("2006-01-02")
		}
	}
	year, month := 0, 0
	items := []Object{}
	positions := map[string]int{}
	for n := doc.FirstChild(); n != nil; n = n.NextSibling() {
		switch block := n.(type) {
		case *ast.Heading:
			channel = ""
			if block.Level == 2 {
				year, month = 0, 0
				if m := monthHeading.FindStringSubmatch(strings.TrimSpace(nodeText(block, source))); m != nil {
					year, _ = strconv.Atoi(m[1])
					month, _ = strconv.Atoi(m[2])
				}
			}
		case *ast.HTMLBlock:
			raw := string(block.Lines().Value(source))
			if block.HasClosure() {
				raw += string(block.ClosureLine.Value(source))
			}
			if name, found := summaryText(raw); found {
				channel = strings.TrimSpace(strings.SplitN(name, " · ", 2)[0])
			}
			if strings.Contains(strings.ToLower(raw), "</details>") {
				channel = ""
			}
		case *extast.Table:
			if kind != "podcast" {
				continue
			}
			for _, item := range r.podcastRows(block, source, current, channel) {
				key := item["url"].(string)
				if index, ok := positions[key]; ok {
					items[index] = item
				} else {
					positions[key] = len(items)
					items = append(items, item)
				}
			}
		case *ast.List:
			if kind != "blog" || year == 0 || month < 1 || month > 12 {
				continue
			}
			for item := block.FirstChild(); item != nil; item = item.NextSibling() {
				if projected := r.blogItem(item, source, current, channel, year, month); projected != nil {
					items = append(items, projected)
				}
			}
		}
	}
	sort.SliceStable(items, func(i, j int) bool { return items[i]["date"].(string) > items[j]["date"].(string) })
	unique, seen := []Object{}, map[string]bool{}
	for _, item := range items {
		key := item["url"].(string)
		if !seen[key] {
			seen[key] = true
			unique = append(unique, item)
		}
	}
	return Object{"kind": kind, "checked_on": checked, "items": unique}
}

func summaryText(raw string) (string, bool) {
	z := nethtml.NewTokenizer(strings.NewReader(raw))
	active, found := false, false
	var text strings.Builder
	for {
		switch z.Next() {
		case nethtml.ErrorToken:
			if z.Err() == io.EOF {
				return text.String(), found
			}
			return "", false
		case nethtml.StartTagToken:
			if z.Token().Data == "summary" {
				active, found = true, true
			}
		case nethtml.EndTagToken:
			if z.Token().Data == "summary" {
				active = false
			}
		case nethtml.TextToken:
			if active {
				text.Write(z.Text())
			}
		}
	}
}

func (r *Reader) reportLink(current string, links []feedLink) (feedLink, string, bool) {
	for _, link := range links {
		if !strings.HasPrefix(link.title, "阅读报告") && !strings.HasPrefix(link.title, "相关报告") {
			continue
		}
		u, err := url.Parse(link.url)
		if err != nil || u.Scheme != "" || u.Host != "" || strings.HasPrefix(link.url, "/") || strings.HasPrefix(link.url, "#") {
			return link, "", true
		}
		return link, r.link(current, link.url), true
	}
	return feedLink{}, "", false
}

func (r *Reader) podcastRows(table *extast.Table, source []byte, current, channel string) []Object {
	head := table.FirstChild()
	if head == nil {
		return nil
	}
	columns := []string{}
	for cell := head.FirstChild(); cell != nil; cell = cell.NextSibling() {
		columns = append(columns, strings.TrimSpace(nodeText(cell, source)))
	}
	joined := strings.Join(columns, "|")
	if joined != "日期|节目|本期内容|时长|学习报告" && joined != "日期|本期内容|时长|学习报告" {
		return nil
	}
	items := []Object{}
	for row := head.NextSibling(); row != nil; row = row.NextSibling() {
		if row.ChildCount() != len(columns) {
			continue
		}
		cells := map[string]ast.Node{}
		i := 0
		for cell := row.FirstChild(); cell != nil; cell = cell.NextSibling() {
			cells[columns[i]] = cell
			i++
		}
		date := strings.TrimSpace(nodeText(cells["日期"], source))
		if _, err := time.Parse("2006-01-02", date); err != nil {
			continue
		}
		links := linksIn(cells["本期内容"], source)
		if len(links) == 0 || publicURL(links[0].url) == "" {
			continue
		}
		episode := links[0]
		audio := ""
		for _, link := range links {
			if link.title == "音频" {
				audio = publicURL(link.url)
			}
		}
		report, reportURL, present := r.reportLink(current, linksIn(cells["学习报告"], source))
		status, label := "none", "有报告 · 阅读"
		if present {
			status = "unavailable"
			if reportURL != "" {
				status = "available"
				if strings.HasPrefix(report.title, "相关报告") {
					status, label = "related", "相关报告"
				}
			}
		}
		show := channel
		if cell := cells["节目"]; cell != nil {
			show = nodeText(cell, source)
		}
		items = append(items, Object{"date": date, "title": episode.title, "original_title": episode.original, "url": episode.url,
			"channel": show, "duration": nodeText(cells["时长"], source), "audio_url": audio, "report_url": reportURL,
			"report_status": status, "report_label": label, "report_note": report.title})
	}
	return items
}

func (r *Reader) blogItem(item ast.Node, source []byte, current, channel string, year, month int) Object {
	paragraph := item.FirstChild()
	if paragraph == nil {
		return nil
	}
	first := paragraph.FirstChild()
	strong, ok := first.(*ast.Emphasis)
	if !ok || strong.Level != 2 {
		return nil
	}
	m := monthDay.FindStringSubmatch(nodeText(first, source))
	if m == nil {
		return nil
	}
	mm, _ := strconv.Atoi(m[1])
	dd, _ := strconv.Atoi(m[2])
	date := time.Date(year, time.Month(mm), dd, 0, 0, 0, 0, time.UTC)
	if mm != month || date.Year() != year || int(date.Month()) != month || date.Day() != dd {
		return nil
	}
	links := linksIn(item, source)
	if len(links) == 0 || publicURL(links[0].url) == "" {
		return nil
	}
	article := links[0]
	report, reportURL, _ := r.reportLink(current, links[1:])
	label := "阅读报告"
	if strings.HasPrefix(report.title, "相关报告") || strings.Contains(nodeText(paragraph, source), "相关报告") {
		label = "相关报告"
	}
	return Object{"date": date.Format("2006-01-02"), "title": article.title, "original_title": article.original, "url": article.url,
		"channel": channel, "report_url": reportURL, "report_label": label}
}
