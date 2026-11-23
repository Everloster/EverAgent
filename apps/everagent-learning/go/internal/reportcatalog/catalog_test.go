package reportcatalog

import (
	"encoding/json"
	"os"
	"testing"
)

func TestSharedCatalogContract(t *testing.T) {
	data, err := os.ReadFile("testdata/shared_contract.json")
	if err != nil {
		t.Fatal(err)
	}
	var contract struct {
		PathCases []struct {
			Path       string `json:"path"`
			Collection string `json:"collection"`
			Matches    bool   `json:"matches"`
		} `json:"path_cases"`
		TitleCases []struct {
			Path, Title, Expected string
		} `json:"title_cases"`
		AliasCases []struct {
			Raw      Metadata `json:"raw"`
			Field    string   `json:"field"`
			Expected string   `json:"expected"`
		} `json:"alias_cases"`
		DateCases []struct {
			Path, Text, Fallback, Expected string
		} `json:"date_cases"`
	}
	if err := json.Unmarshal(data, &contract); err != nil {
		t.Fatal(err)
	}
	for _, tc := range contract.PathCases {
		collection, ok := CollectionFor(tc.Path)
		if ok != tc.Matches || ok && collection.ID != tc.Collection {
			t.Errorf("path %q: collection=%q matches=%v", tc.Path, collection.ID, ok)
		}
	}
	for _, tc := range contract.TitleCases {
		if got := displayTitle(tc.Path, tc.Title); got != tc.Expected {
			t.Errorf("title %q: got=%q want=%q", tc.Title, got, tc.Expected)
		}
	}
	for _, tc := range contract.AliasCases {
		if got := str(normalize(tc.Raw)[tc.Field]); got != tc.Expected {
			t.Errorf("alias %v: got=%q want=%q", tc.Raw, got, tc.Expected)
		}
	}
	for _, tc := range contract.DateCases {
		report, err := info("ai-learning/reports/"+tc.Path, tc.Text, tc.Fallback)
		if err != nil || report.UpdatedOn != tc.Expected {
			t.Errorf("date %q: got=%q want=%q err=%v", tc.Path, report.UpdatedOn, tc.Expected, err)
		}
	}
}

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
