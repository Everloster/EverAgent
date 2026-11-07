package publicquality

import (
	"strings"
	"testing"
)

func TestCatalogDiscoveryAndMetadata(t *testing.T) {
	for _, p := range []string{"ai-practice/experiments/exp_demo.md", "ai-practice/experiments/demo/评估笔记.md", "podcast-learning/reports/series/report.md"} {
		if _, ok := CollectionFor(p); !ok {
			t.Fatal("missed report", p)
		}
	}
	for _, p := range []string{"ai-practice/experiments/demo/README.md", "podcast-learning/reports/transcripts/full.md", "podcast-learning/transcripts/full.md"} {
		if _, ok := CollectionFor(p); ok {
			t.Fatal("indexed non-report", p)
		}
	}
	text := "---\ntitle: 测试报告\nstatus: complete\ncreated: 2026-11-01\nsemantic_tags: [Go, '索引']\n---\n# 正文\n"
	r, e := info("ai-learning/reports/report.md", text, "")
	if e != nil {
		t.Fatal(e)
	}
	if r.Metadata.String("status") != "completed" || r.RawMetadata.String("status") != "complete" || r.UpdatedOn != "2026-11-01" || len(r.Tags) != 2 {
		t.Fatalf("incorrect metadata: %+v", r)
	}
	for _, text := range []string{"---\ntitle: one\ntitle: two\n---\n", "---\nx: &a [1]\ny: *a\n---\n", "---\nx: [unterminated\n---\n"} {
		if _, e := ParseFrontmatter(text); e == nil {
			t.Fatal("ambiguous metadata accepted")
		}
	}
}
func TestGeneratedIndexAndMarkers(t *testing.T) {
	s := memory(map[string]string{
		"README.md":                     "# reader\n<!-- AUTO-RECENT:START -->\n<!-- AUTO-RECENT:END -->\n<!-- AUTO-OVERVIEW:START -->\n<!-- AUTO-OVERVIEW:END -->\n",
		"ai-learning/reports/report.md": "---\ntitle: Report\nupdated_on: 2026-11-01\n---\n# Report\n",
		"github-trending-analyzer/reports/research_example.md":      "---\ntitle: Example repo\nupdated_on: 2026-11-01\n---\n# Example\n",
		"podcast-learning/reports/transcripts/example.shownotes.md": "# Source notes\n",
	})
	reports, findings := Catalog(s)
	if len(findings) != 0 || len(reports) != 2 {
		t.Fatal(findings)
	}
	readme, e := GeneratedREADME(s, reports)
	if e != nil {
		t.Fatal(e)
	}
	index := string(GeneratedIndex(reports))
	if !strings.Contains(string(readme), "1 篇") || !strings.Contains(index, "Report") ||
		!strings.Contains(index, "## 🔭 GitHub Research") || !strings.Contains(index, "research_example.md") || strings.Contains(index, ".shownotes.md") {
		t.Fatal("generated views incomplete")
	}
	if _, e := replaceBlock("END START", "START", "END", "body"); e == nil {
		t.Fatal("out of order markers accepted")
	}
}
func TestLocalReadmeLinks(t *testing.T) {
	files := map[string]string{
		"README.md":        "# 你好 World\n[local](docs/a(b).md#重复-1)\n[ref][The Ref]\n[The Ref]: <docs/a(b).md#重复>\n<img src=\"assets/image.png\">\n[here](#你好-world)\n~~~md\n[example](missing.md)\n~~~\n`[code](missing.md)`\n",
		"docs/a(b).md":     "# 重复\n# 重复\n",
		"assets/image.png": "not actually an image",
	}
	if got := CheckLinks(memory(files), "README.md", true); len(got) != 0 {
		t.Fatalf("valid README rejected: %+v", got)
	}
	for _, link := range []string{"[gone](missing.md)", "[anchor](docs/a(b).md#absent)", "<source srcset=\"assets/image.png 1x, missing.png 2x\">", "[escape](../outside.md)", "正文[^note]\n\n[^note]: [原文](missing.md)"} {
		changed := map[string]string{}
		for p, v := range files {
			changed[p] = v
		}
		changed["README.md"] += "\n" + link
		if len(CheckLinks(memory(changed), "README.md", true)) == 0 {
			t.Fatal("broken link missed", link)
		}
	}
	files["README.md"] += "\n引用[^note]，纯文本[ref][absent]。\n\n[^note]: [来源](docs/a(b).md#重复)\n"
	if got := CheckLinks(memory(files), "README.md", true); len(got) != 0 {
		t.Fatalf("footnote body or non-link text misparsed: %+v", got)
	}
}

func TestGeneratedLinksPreserveReportPaths(t *testing.T) {
	for _, name := range []string{"with space.md", "with#hash.md", "with?query.md", "with%20literal.md", "with(unbalanced.md", "with|pipe.md", "with&copy;.md", "中文报告.md"} {
		t.Run(name, func(t *testing.T) {
			p := "ai-learning/reports/" + name
			r := Report{Path: p, Title: "Report", Domain: "ai-learning", UpdatedOn: "2026-11-01"}
			s := memory(map[string]string{
				"README.md": "<!-- AUTO-RECENT:START -->\n<!-- AUTO-RECENT:END -->\n<!-- AUTO-OVERVIEW:START -->\n<!-- AUTO-OVERVIEW:END -->\n",
			})
			readme, err := GeneratedREADME(s, []Report{r})
			if err != nil {
				t.Fatal(err)
			}
			index := string(GeneratedIndex([]Report{r}))
			for file, body := range map[string]string{"README.md": string(readme), "docs/REPORT_INDEX.md": index} {
				count := 0
				for _, link := range LocalLinks(body) {
					dest, fragment, external, err := localTarget(file, link.Target)
					if err == nil && !external && fragment == "" && dest == p {
						count++
					}
				}
				want := 1
				if file == "docs/REPORT_INDEX.md" {
					want = 2 // recent and domain tables
				}
				if count != want {
					t.Fatalf("%s: %d usable links to %q, want %d", file, count, p, want)
				}
			}
			if dates := fallbackDates(memory(map[string]string{"docs/REPORT_INDEX.md": index})); dates[p] != r.UpdatedOn {
				t.Fatalf("encoded path lost its fallback date: %v", dates)
			}
		})
	}
}
