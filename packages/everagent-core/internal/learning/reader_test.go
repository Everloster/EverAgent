package learning

import (
	"encoding/json"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func fixture(t *testing.T) (string, *Reader, func(string, string)) {
	t.Helper()
	root := filepath.Join(t.TempDir(), "renamed public fork")
	put := func(p, body string) {
		t.Helper()
		file := filepath.Join(root, filepath.FromSlash(p))
		if err := os.MkdirAll(filepath.Dir(file), 0700); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(file, []byte(body), 0600); err != nil {
			t.Fatal(err)
		}
	}
	put("config/report-quality-policy.json", "{}")
	put("docs/REPORT_INDEX.md", "# 报告目录\n")
	// Construct synthetic userinfo to test rejection without a credential-shaped URL in source.
	privateSource := (&url.URL{Scheme: "https", Host: "example.invalid", Path: "/", User: url.User("fixture")}).String()
	put("ai-learning/reports/demo.md", "---\ntitle: 示例报告\nupdated_on: 2026-11-01\nsource_url: "+privateSource+"\nsemantic_tags: [学习]\n---\n# 中文标题\n\n正文。\n")
	put("podcast-learning/reports/transcripts/private.md", "PRIVATE_TRANSCRIPT")
	put(".git/config", "PRIVATE_REMOTE")
	r, err := Open(root)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { r.Close() })
	return root, r, put
}

func TestPublicScopeAndCompleteness(t *testing.T) {
	root, r, put := fixture(t)
	put("ai-learning/reports/.hidden.md", "PRIVATE_HIDDEN")
	list, err := r.List()
	if err != nil || list["total"] != 1 {
		t.Fatalf("list: %v %v", list, err)
	}
	row := list["reports"].([]Object)[0]
	if row["source_url"] != "" || row["updated_on"] != "2026-11-01" {
		t.Fatal(row)
	}
	b, _ := json.Marshal(list)
	if strings.Contains(string(b), root) || strings.Contains(string(b), "PRIVATE_") {
		t.Fatal("private content or local root escaped")
	}
	for _, p := range []string{"../secret.md", "/etc/passwd", ".git/config", "ai-learning/reports/.hidden.md", "ai-learning/reports/x:stream.md", "podcast-learning/reports/transcripts/private.md"} {
		if _, err := r.Detail(p); err == nil {
			t.Errorf("detail accepted %s", p)
		}
	}
	if _, err := r.Asset("config/report-quality-policy.json"); err == nil {
		t.Fatal("served non-image")
	}
	long := "# 长文\n\n" + strings.Repeat("足够长的正文。", 20000) + "\nEND_OF_REPORT"
	put("ai-learning/reports/long.md", long)
	result, err := r.Detail("ai-learning/reports/long.md")
	if err != nil {
		t.Fatal(err)
	}
	detail := result["report"].(Object)
	if detail["bytes"] != len(long) || detail["truncated"] != false || !strings.HasSuffix(detail["markdown"].(string), "END_OF_REPORT") || !strings.Contains(detail["html"].(string), "END_OF_REPORT") {
		t.Fatal("long report lost its tail")
	}
	put("ai-learning/reports/long.md", strings.Repeat("x", detailLimit+1))
	if _, err := r.Detail("ai-learning/reports/long.md"); err == nil || err.Error() != "report_too_large" {
		t.Fatal(err)
	}
	list, err = r.List()
	if err != nil || list["complete"] != false {
		t.Fatal("an unreadable report became a complete list", err)
	}
}

func TestLinkedFilesStayOutsideReader(t *testing.T) {
	root, r, put := fixture(t)
	secret := filepath.Join(t.TempDir(), "secret.md")
	if err := os.WriteFile(secret, []byte("PRIVATE_SOURCE"), 0600); err != nil {
		t.Fatal(err)
	}
	put("docs/assets/original.png", "image")
	if err := os.Link(secret, filepath.Join(root, "ai-learning/reports/hard.md")); err != nil {
		t.Fatal(err)
	}
	if _, err := r.Detail("ai-learning/reports/hard.md"); err == nil {
		t.Fatal("served hardlink")
	}
	if list, err := r.List(); err != nil || list["complete"] != false {
		t.Fatal("rejected report hidden from catalog coverage", list, err)
	}
	if err := os.Link(secret, filepath.Join(root, "docs/assets/hard.png")); err != nil {
		t.Fatal(err)
	}
	if _, err := r.Asset("docs/assets/hard.png"); err == nil {
		t.Fatal("served hardlinked asset")
	}
	t.Run("symlink", func(t *testing.T) {
		if err := os.Symlink(secret, filepath.Join(root, "ai-learning/reports/linked.md")); err != nil {
			t.Skipf("platform cannot create symlinks: %v", err)
		}
		if _, err := r.Detail("ai-learning/reports/linked.md"); err == nil {
			t.Fatal("served symlink")
		}
		list, err := r.List()
		if err != nil || list["total"] != 1 {
			t.Fatal("linked file entered report catalog", list, err)
		}
	})
}

func TestMarkdownUsesSafeStandardRenderer(t *testing.T) {
	_, r, put := fixture(t)
	put("docs/assets/test.png", "image")
	put("ai-learning/reports/render.md", "# 中文标题\n\n## 重复标题\n\n## 重复标题\n\n| 列 | 值 |\n| --- | --- |\n| a | b |\n\n[报告](demo.md#中文标题) ![图](../../docs/assets/test.png)\n\n脚注[^注]，再次[^注]。\n\n[^注]: [来源](https://example.invalid/)\n\n<script>alert(1)</script>\n\n[危险](javascript:alert)\n\n```go\n# 不是标题\n```\n")
	result, err := r.Detail("ai-learning/reports/render.md")
	if err != nil {
		t.Fatal(err)
	}
	d := result["report"].(Object)
	html := d["html"].(string)
	for _, expected := range []string{"<table>", `id="重复标题"`, `id="重复标题-1"`, "dashboard?report=ai-learning%2Freports%2Fdemo.md#%E4%B8%AD%E6%96%87%E6%A0%87%E9%A2%98", "api/asset?path=docs%2Fassets%2Ftest.png", `class="footnotes"`, `href="#fn:1"`, `id="fn:1"`} {
		if !strings.Contains(html, expected) {
			t.Errorf("missing %s from %s", expected, html)
		}
	}
	if strings.Contains(html, "<script") || strings.Contains(html, `href="javascript`) || len(d["outline"].([]Object)) != 3 {
		t.Fatal("unsafe HTML or fenced example treated as heading", html)
	}
	put("podcast-learning/PODCAST_UPDATES.md", "# 更新\n\n<details open onclick=\"bad()\">\n<summary>节目</summary>\n\n[正文](../ai-learning/reports/demo.md)\n\n</details>\n\n<iframe src=\"https://example.invalid/\"></iframe>\n")
	result, err = r.Detail("podcast-learning/PODCAST_UPDATES.md")
	if err != nil {
		t.Fatal(err)
	}
	html = result["report"].(Object)["html"].(string)
	if !strings.Contains(html, "<details open") || !strings.Contains(html, "<summary>节目</summary>") || !strings.Contains(html, "dashboard?report=") || strings.Contains(html, "onclick") || strings.Contains(html, "<iframe") {
		t.Fatal(html)
	}
	put("podcast-learning/PODCAST_UPDATES.md", strings.Repeat("<details>", 258)+"TAIL"+strings.Repeat("</details>", 258))
	if _, err := r.Detail("podcast-learning/PODCAST_UPDATES.md"); err == nil || err.Error() != "render_too_deep" {
		t.Fatal("deep rendering silently lost content", err)
	}
}

func TestLivingListsPreserveDatesAndReportStatus(t *testing.T) {
	_, r, put := fixture(t)
	podcast := "# 播客\n\n最近检查：**2026-11-07**\n\n| 日期 | 节目 | 本期内容 | 时长 | 学习报告 |\n| --- | --- | --- | --- | --- |\n| 2026-11-06 | Weekly | [中文标题](https://example.invalid/one \"Original\") · [音频](https://example.invalid/one.mp3) | 60m | — |\n\n<details>\n<summary>Show &amp; Co · 更新</summary>\n\n| 日期 | 本期内容 | 时长 | 学习报告 |\n| --- | --- | --- | --- |\n| 2026-11-06 | [中文标题](https://example.invalid/one \"Original\") | 60m | [阅读报告](../ai-learning/reports/demo.md) |\n| 2026-11-05 | [同名](https://example.invalid/two) | 30m | [相关报告：片段](../ai-learning/reports/demo.md) |\n| 2026-11-31 | [错误日期](https://example.invalid/bad) | 30m | — |\n\n</details>\n"
	put("podcast-learning/PODCAST_UPDATES.md", podcast)
	feed := r.feed(podcast, "podcast-learning/PODCAST_UPDATES.md")
	items := feed["items"].([]Object)
	if len(items) != 2 || feed["checked_on"] != "2026-11-07" {
		t.Fatal(feed)
	}
	if items[0]["report_status"] != "available" || items[0]["channel"] != "Show & Co" || items[0]["original_title"] != "Original" || items[1]["report_status"] != "related" {
		t.Fatal(items)
	}
	blog := "# 博客\n\n最近检查：2026-11-07\n\n## 2025 年 12 月\n\n<details>\n<summary>Lab · 列表</summary>\n\n- **12-31** [标题 &amp; 原文](https://example.invalid/blog \"English\") · 介绍\n  [相关报告](../ai-learning/reports/demo.md)\n- **11-30** [月份不符](https://example.invalid/no) · 简介\n\n</details>\n\n## 附录\n\n- **12-30** [不是月表](https://example.invalid/appendix) · 内容\n"
	feed = r.feed(blog, "web-surfing/TECH_BLOG_UPDATES.md")
	items = feed["items"].([]Object)
	if len(items) != 1 || items[0]["date"] != "2025-12-31" || items[0]["title"] != "标题 & 原文" || items[0]["report_label"] != "相关报告" || items[0]["report_url"] == "" {
		t.Fatal(feed)
	}
}

func TestURLAndUTF8Rejection(t *testing.T) {
	_, r, put := fixture(t)
	privateSource := (&url.URL{Scheme: "https", Host: "example.invalid", Path: "/", User: url.UserPassword("fixture", "fixture")}).String()
	for _, value := range []string{privateSource, "https://example.invalid/\n", "//example.invalid/", "file:///etc/passwd", "javascript:alert(1)", "https:\\example.invalid"} {
		if publicURL(value) != "" {
			t.Error(value)
		}
	}
	put("ai-learning/reports/invalid.md", string([]byte{0xff, 0xfe}))
	if _, err := r.Detail("ai-learning/reports/invalid.md"); err == nil || err.Error() != "invalid_utf8" {
		t.Fatal(err)
	}
	// A separator inside a code block is not frontmatter.
	input := "# 标题\n\n```\n---\n```\n"
	if stripFrontmatter(input) != input {
		t.Fatal("removed body content")
	}
}

func TestCompactFeedsAndSafeReportAnchors(t *testing.T) {
	_, r, put := fixture(t)
	put("ai-learning/reports/anchor.md", "<a id=\"chapter\"></a>\n\n[跳转](#chapter)\n\n<a id=\"unsafe\" onclick=\"bad()\"></a>\n<script>example()</script>\n\n`&amp;` 与 &amp;\n")
	result, err := r.Detail("ai-learning/reports/anchor.md")
	if err != nil {
		t.Fatal(err)
	}
	html := result["report"].(Object)["html"].(string)
	if !strings.Contains(html, `id="chapter"`) || !strings.Contains(html, `href="#chapter"`) || strings.Contains(html, `<a id="unsafe"`) || !strings.Contains(html, "&lt;script&gt;") {
		t.Fatal(html)
	}
	if !strings.Contains(html, "<code>&amp;amp;</code>") || !strings.Contains(html, "与 &amp;") {
		t.Fatal("standard Markdown/code entity semantics changed", html)
	}
	podcast := `最近检查：**2027-01-03**
<summary><strong>节目 A · 2 条</strong></summary>
| 日期 | 本期内容 | 时长 | 学习报告 |
| --- | --- | --- | --- |
| 2026-12-31 | [跨年主题](https://example.invalid/a "Original &#124; title") | 1小时 | [阅读报告](../ai-learning/reports/demo.md) |
| 2027-01-01 | [新单集](https://example.invalid/new) | 30分钟 | 未做 |
</details>
<summary><strong>节目 B · 1 条</strong></summary>
| 日期 | 本期内容 | 时长 | 学习报告 |
| --- | --- | --- | --- |
| 2026-12-31 | [跨年主题](https://example.invalid/b) | 55分钟 | [相关报告（节目 A 版）](../ai-learning/reports/demo.md) |
`
	feed := r.feed(podcast, "podcast-learning/PODCAST_UPDATES.md")
	items := feed["items"].([]Object)
	if len(items) != 3 || items[0]["date"] != "2027-01-01" || items[1]["original_title"] != "Original | title" || items[2]["channel"] != "节目 B" || items[2]["report_status"] != "related" {
		t.Fatal(feed)
	}
	blog := `## 2026 年 11 月
<summary><strong>AI &amp; ML · 2 篇</strong></summary>
- **11-01** [旧副本](https://example.invalid/a) · 未做
- **11-02** [中文 &amp; 标题](https://example.invalid/a "English &amp; title") · 已学习
  [阅读报告](../ai-learning/reports/demo.md)
- **11-02** [另一篇](https://example.invalid/b) · 相关报告
  [阅读报告](javascript:alert)
`
	feed = r.feed(blog, "web-surfing/TECH_BLOG_UPDATES.md")
	items = feed["items"].([]Object)
	if len(items) != 2 || items[0]["original_title"] != "English & title" || items[0]["channel"] != "AI & ML" || items[1]["report_label"] != "相关报告" || items[1]["report_url"] != "" {
		t.Fatal(feed)
	}
}
