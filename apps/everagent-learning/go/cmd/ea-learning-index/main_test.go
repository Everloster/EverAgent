package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"everagent.local/learning/internal/learning"
)

func TestFixedJSONCommands(t *testing.T) {
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
	p := "ai-learning/reports/demo.md"
	put(p, "---\ntitle: 示例报告\nupdated_on: 2026-11-01\nsemantic_tags: [学习]\n---\n# 中文标题\n\n正文。\n")
	put("docs/REPORT_INDEX.md", "# 报告目录\n")
	put("docs/assets/test.png", "image")
	list, err := run([]string{root, "list"})
	if err != nil || list["total"] != 1 || list["complete"] != true || list["latest_on"] != "2026-11-01" {
		t.Fatal(list, err)
	}
	if _, ok := list["reports"].([]learning.Object); !ok {
		t.Fatal("reports must remain a JSON array", list)
	}
	b, err := json.Marshal(list)
	if err != nil || strings.Contains(string(b), root) || !strings.Contains(string(b), `"warnings":[]`) || !strings.Contains(string(b), `"pins":[]`) {
		t.Fatal("list JSON changed or leaked the local root", string(b), err)
	}
	detail, err := run([]string{root, "detail", p})
	if err != nil {
		t.Fatal(err)
	}
	d := detail["report"].(learning.Object)
	if detail["info_title"] != "示例报告" || d["path"] != p || d["truncated"] != false || d["metadata_status"] != "parsed" || !strings.Contains(d["html"].(string), `id="中文标题"`) {
		t.Fatal(detail)
	}
	asset, err := run([]string{root, "asset", "docs/assets/test.png"})
	if err != nil || asset["mime"] != "image/png" {
		t.Fatal(asset, err)
	}
	b, err = json.Marshal(asset)
	if err != nil || !strings.Contains(string(b), `"data":"aW1hZ2U="`) {
		t.Fatal("asset bytes must remain base64 in JSON", string(b), err)
	}
	for _, args := range [][]string{nil, {root}, {root, "other"}, {root, "list", p}, {root, "detail"}, {root, "asset"}, {root, "detail", p, "extra"}} {
		if _, err := run(args); err == nil || err.Error() != "bad_usage" {
			t.Fatalf("arguments=%q error=%v", args, err)
		}
	}
	for _, tc := range []struct {
		args []string
		want string
	}{
		{[]string{filepath.Join(root, "missing"), "list"}, "repo_missing"},
		{[]string{root, "detail", "../secret.md"}, "unsafe_path"},
		{[]string{root, "detail", "docs/REPORT_INDEX.md"}, "unknown_collection"},
		{[]string{root, "asset", "config/report-quality-policy.json"}, "unsafe_path"},
	} {
		if _, err := run(tc.args); err == nil || err.Error() != tc.want {
			t.Fatalf("arguments=%q error=%v want=%q", tc.args, err, tc.want)
		}
	}
}
