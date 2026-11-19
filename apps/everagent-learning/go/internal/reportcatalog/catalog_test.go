package reportcatalog

import "testing"

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
