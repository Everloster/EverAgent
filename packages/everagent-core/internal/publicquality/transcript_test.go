package publicquality

import (
	"maps"
	"net/url"
	"strings"
	"testing"
)

func TestTranscriptFailuresAndReceiptBinding(t *testing.T) {
	valid := "[00:00:00 -> 00:00:10] 中文 English 混合\n[00:00:10 -> 00:01:00] 最后一句\n"
	audit := AuditTranscript([]byte(valid), "fixture.transcript.txt")
	if audit.Metrics["ok"] != true || !noErrors(audit.Findings) {
		t.Fatal(audit)
	}
	for _, body := range []string{"", "\xff", "[00:61:00 -> 01:02:00] bad\n", "[00:00:09 -> 00:00:01] reversed\n",
		"[00:00:00 -> 00:00:01] repeat\n[00:00:01 -> 00:00:02] repeat\n[00:00:02 -> 00:00:03] repeat\n[00:00:03 -> 00:00:04] repeat\n"} {
		if got := AuditTranscript([]byte(body), "fixture.transcript.txt"); got.Metrics["ok"] != false || !hasCode(got.Findings, "POD102") {
			t.Fatal("invalid transcript accepted", got)
		}
	}
	ref := "sha256:" + digest([]byte(valid))
	receipt := Object{"schema_version": 2, "kind": "podcast-transcript-audit", "source_url": "https://example.invalid/source", "source_ref": ref, "max_consecutive_limit": 3, "audit": audit.Metrics}
	if got := receiptFindings("receipt.json", receipt, ref, "https://example.invalid/source"); !noErrors(got) {
		t.Fatal(got)
	}
	for _, mutate := range []func(Object){
		func(v Object) { v["private_path"] = "private-source" },
		func(v Object) { v["source_ref"] = "sha256:" + strings.Repeat("0", 64) },
		func(v Object) { v["max_consecutive_limit"] = 9 },
		func(v Object) { m := maps.Clone(obj(v["audit"])); m["segments"] = 99; v["audit"] = m },
	} {
		v := maps.Clone(receipt)
		mutate(v)
		if got := receiptFindings("receipt.json", v, ref, "https://example.invalid/source"); !hasCode(got, "POD107") {
			t.Fatal("forged/leaking receipt accepted", got)
		}
	}
	withUser := (&url.URL{Scheme: "https", Host: "example.invalid", User: url.UserPassword("fixture", "fixture"), Path: "/x"}).String()
	for _, raw := range []string{"https://localhost/x", "https://100.64.0.1/x", "https://device.ts.net/x", withUser, "https://example.invalid/x?auth=secret"} {
		if publicSourceURL(raw) {
			t.Fatal("private source URL accepted", raw)
		}
	}
}

func TestPodcastMissingTruncatedAndPrivateSources(t *testing.T) {
	p := "podcast-learning/reports/topic.md"
	raw := "podcast-learning/transcripts/topic.transcript.txt"
	report := "---\ntitle: Topic\ndomain: podcast-learning\ntranscript_path: transcripts/topic.transcript.txt\nduration_seconds: 1000\n---\n# Topic\n"
	r, err := info(p, report, "")
	if err != nil {
		t.Fatal(err)
	}
	if got := checkPodcast(memory(map[string]string{p: report}), r, report); !hasCode(got, "POD101") {
		t.Fatal("missing transcript accepted", got)
	}
	files := map[string]string{p: report, raw: "[00:00:00 -> 00:01:00] 原文\n"}
	if got := checkPodcast(memory(files), r, report); !hasCode(got, "POD104") {
		t.Fatal("declared duration mismatch was hidden", got)
	}
	r.Metadata["transcript_visibility"] = "private"
	if got := checkPodcast(memory(files), r, report); !hasCode(got, "POD107") {
		t.Fatal("private source without bounded receipt accepted", got)
	}
}

func TestSourceFirstMapCannotHideCoreOmission(t *testing.T) {
	r := Report{Domain: "podcast-learning", Metadata: Metadata{"report_depth": "deep", "source_shownotes_chapters": "true", "chapters": "3"}}
	ev := evidenceSummary{sources: []string{"S1"}, coverage: []string{"U1", "U2", "U3"}}
	unit := func(id, match string) Object {
		return Object{"id": id, "title": "来源单元", "importance": "core", "assessment": "covered", "notes": "核对", "source_ids": []any{"S1"}, "matched_coverage_unit_ids": []any{match}}
	}
	item := Object{"source_content_map": []any{unit("M1", "U1"), unit("M2", "U2"), unit("M3", "U3")}}
	f := findingList{}
	checkContentMap(&f, r, item, ev)
	if len(f.items) != 0 {
		t.Fatal(f.items)
	}
	obj(array(item["source_content_map"])[2])["assessment"] = "omitted"
	f.items = nil
	checkContentMap(&f, r, item, ev)
	if !hasCode(f.items, "REV033") {
		t.Fatal("core omission accepted", f.items)
	}
}
