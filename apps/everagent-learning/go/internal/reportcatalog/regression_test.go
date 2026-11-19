package reportcatalog

import (
	"encoding/json"
	"errors"
	"net/url"
	"reflect"
	"strings"
	"testing"
)

func TestHistoricalDatePrecedence(t *testing.T) {
	for _, tc := range []struct {
		name, path, body, want string
	}{
		{"updated", "2026-09-01_report.md", "---\nupdated_on: 2026-11-01\ncreated: 2026-10-01\n---\n报告生成时间：2026-08-01", "2026-11-01"},
		{"created", "2026-09-01_report.md", "---\ncreated: 2026-10-01\n---\n报告生成时间：2026-08-01", "2026-10-01"},
		{"filename", "2026-09-01_report.md", "---\nupdated_on: unknown\n---\n报告生成时间：2026-08-01", "2026-09-01"},
		{"footer", "report.md", "# 历史报告\n报告生成时间：2026-08-01", "2026-08-01"},
		{"index", "report.md", "# 历史报告", "2026-07-01"},
		// Preserve the old projection's shape-only date rule, not a new audit.
		{"legacy date shape", "report.md", "---\nupdated_on: 2026-02-31\n---\n# 历史报告", "2026-02-31"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			r, err := info("ai-learning/reports/"+tc.path, tc.body, "2026-07-01")
			if err != nil || r.UpdatedOn != tc.want {
				t.Fatalf("date=%q want=%q err=%v", r.UpdatedOn, tc.want, err)
			}
		})
	}
	r, err := info("ai-learning/reports/unknown.md", "# 未知日期", "")
	if err != nil || r.UpdatedOn != "" {
		t.Fatal("unknown date must not acquire an mtime or current date", r, err)
	}
}

func TestHistoricalIndexEncodedPaths(t *testing.T) {
	// These are the old generated-link fixture names; only parsing is migrated.
	for _, name := range []string{"with space.md", "with#hash.md", "with?query.md", "with%20literal.md", "with(unbalanced.md", "with|pipe.md", "with&copy;.md", "中文报告.md"} {
		t.Run(name, func(t *testing.T) {
			p := "ai-learning/reports/" + name
			destination := strings.ReplaceAll((&url.URL{Path: "../" + p}).EscapedPath(), "&", "%26")
			files := map[string]string{
				p:                      "# 历史报告\n",
				"docs/REPORT_INDEX.md": "| 2026-07-01 | [旧报告](" + destination + ") | ai-learning |\n",
			}
			reports, findings := CatalogFiles([]string{p, "docs/REPORT_INDEX.md", p}, func(path string, limit int) ([]byte, error) {
				if limit != textLimit {
					t.Fatalf("unexpected read budget: %d", limit)
				}
				return []byte(files[path]), nil
			})
			if len(reports) != 1 || reports[0].UpdatedOn != "2026-07-01" || len(findings) != 0 {
				t.Fatal("encoded path lost its fallback date", reports, findings)
			}
		})
	}
}

func TestPartialLegacyMetadataAndDisplayTitles(t *testing.T) {
	body := "---\ntitle: 测试报告\nstatus: done\nupdated_on: 2026-11-01\nsemantic_tags: 学习\nx: [unterminated\n---\n# 正文\n"
	r, err := info("ai-learning/reports/report.md", body, "")
	if err != nil || r.MetadataStatus != "partial-invalid-yaml" || r.Title != "测试报告" || r.UpdatedOn != "2026-11-01" || r.Metadata.String("status") != "completed" || r.RawMetadata.String("status") != "done" || !reflect.DeepEqual(r.Tags, []string{"学习"}) {
		t.Fatal("legacy scalars or aliases changed", r, err)
	}
	m := partialMetadata("---\ntitle: one\ntitle: two\ncreated: 2026-11-01\n---\n")
	if m.String("title") != "" || m.String("created") != "2026-11-01" {
		t.Fatal("ambiguous fields were retained", m)
	}
	for title, want := range map[string]string{
		"Brook：引言":         "《AI演义》01｜Brook：引言",
		"AI演义 · 1 · Brook": "《AI演义》01｜Brook",
		"《AI演义》01｜Brook":   "《AI演义》01｜Brook",
		"《AI演义》02｜Brook":   "《AI演义》02｜Brook",
	} {
		if got := displayTitle("ai-learning/reports/AI演义_01_Brook.md", title); got != want {
			t.Fatalf("title=%q got=%q want=%q", title, got, want)
		}
	}
}

func TestCallerScopeUTF8AndWarningJSON(t *testing.T) {
	p := "ai-learning/reports/report.md"
	for _, tc := range []struct {
		name string
		body []byte
		err  error
		code string
	}{
		{"BOM", []byte("\xef\xbb\xbf---\nupdated_on: 2026-11-01\n---\n# 正文"), nil, ""},
		{"invalid UTF-8", []byte{0xff}, nil, "REPORT_UNREADABLE"},
		{"NUL", []byte("# 正文\x00"), nil, "REPORT_UNREADABLE"},
		{"oversized callback", []byte(strings.Repeat("x", textLimit+1)), nil, "REPORT_UNREADABLE"},
		{"read error", nil, errors.New("fixture read failed"), "REPORT_UNREADABLE"},
		{"unknown date", []byte("# 正文"), nil, "REPORT_DATE_UNKNOWN"},
		{"partial YAML", []byte("---\nupdated_on: 2026-11-01\nx: [unfinished\n---\n# 正文"), nil, "REPORT_METADATA_PARTIAL"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			reads := 0
			reports, findings := CatalogFiles([]string{p, p, "../secret.md", "podcast-learning/reports/transcripts/private.md"}, func(path string, limit int) ([]byte, error) {
				reads++
				if path != p || limit != textLimit {
					t.Fatalf("read escaped caller report scope: %q %d", path, limit)
				}
				return tc.body, tc.err
			})
			if reads != 1 {
				t.Fatalf("duplicate paths changed read count: %d", reads)
			}
			if tc.code == "" {
				if len(reports) != 1 || len(findings) != 0 {
					t.Fatal(reports, findings)
				}
				return
			}
			if len(findings) != 1 || findings[0].Code != tc.code || findings[0].File != p {
				t.Fatal(findings)
			}
			severity := "warning"
			if tc.code == "REPORT_UNREADABLE" {
				severity = "error"
				if len(reports) != 0 {
					t.Fatal("unreadable report entered catalog", reports)
				}
			}
			if findings[0].Severity != severity {
				t.Fatal(findings)
			}
			encoded, err := json.Marshal(findings[0])
			if err != nil || strings.Contains(string(encoded), `"line"`) || strings.Contains(string(encoded), "fixture read failed") {
				t.Fatal("warning JSON changed or leaked reader error", string(encoded), err)
			}
		})
	}
}

func TestHeadingSlugCompatibility(t *testing.T) {
	for title, want := range map[string]string{
		"你好 World":                   "你好-world",
		"<em>Title</em> &amp; More!": "title--more",
		"重复_标题-1":                    "重复_标题-1",
		"中文：标题（说明）🚀":                 "中文标题说明",
		"A\t B\n":                    "a-b",
	} {
		if got := HeadingSlug(title); got != want {
			t.Fatalf("slug(%q)=%q want=%q", title, got, want)
		}
	}
}
