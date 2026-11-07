package publicquality

import (
	"context"
	"encoding/json"
	"maps"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

func jsonText(t *testing.T, v any) string {
	t.Helper()
	b, err := json.Marshal(v)
	if err != nil {
		t.Fatal(err)
	}
	return string(b)
}

// A small synthetic policy exercises the validator without copying the live
// model policy into tests. The real owners and recorded reports are checked by
// ea-quality, including when the gate exports the module to a clean snapshot.
func qualityFixture(t *testing.T) (map[string]string, string) {
	t.Helper()
	enum := func(values ...string) Object {
		items := make([]any, len(values))
		for i, v := range values {
			items[i] = v
		}
		return Object{"enum": items}
	}
	object := func(properties Object, required ...string) Object {
		items := make([]any, len(required))
		for i, v := range required {
			items[i] = v
		}
		return Object{"type": "object", "properties": properties, "required": items}
	}
	list := func(item Object) Object { return Object{"type": "array", "items": item} }
	text := Object{"type": "string", "minLength": 1}
	actor := object(Object{"model": text, "harness": text, "run_id": text, "independent_context": Object{"type": "boolean"}}, "model", "harness", "run_id")
	claim := object(Object{"support": enum("direct", "derived", "inference")}, "support")
	source := object(Object{"kind": enum("primary", "official", "secondary", "local", "execution")}, "kind")
	evidence := object(Object{"quality_tier": enum("standard"), "generator": actor, "sources": list(source), "claims": list(claim)}, "generator", "sources", "claims", "quality_tier")
	reviewItem := object(Object{
		"role": enum("primary_review", "escalation_review", "flagship_final_review"), "reviewer": actor,
		"scores":        object(Object{"evidence": Object{"type": "number", "minimum": 0, "maximum": 100}}, "evidence"),
		"hard_failures": list(enum("fabricated_or_unread_source")),
	}, "role", "reviewer", "scores", "hard_failures")
	reviewSchema := object(Object{"quality_tier": enum("standard"), "reviews": list(reviewItem)}, "quality_tier", "reviews")
	policy := Object{
		"schema_version": 1, "policy_id": "synthetic-1", "current_report_schema": "report-v2",
		"dimensions": Object{"evidence": 100}, "hard_failure_codes": []any{"fabricated_or_unread_source"},
		"model_policy": Object{"default_generator": "writer", "default_reviewer": "reader", "premium_reviewer_order": []any{"strong"},
			"strong_reviewers": []any{"strong"}, "scarce_models": []any{"scarce"}, "disabled_models": []any{"disabled"},
			"scarce_model_max_calls_per_report": 1, "scarce_model_preferred_roles": []any{"escalation_review"}, "explicit_user_override_allowed": true},
		"tiers": Object{"standard": Object{"minimum_dimension_scores": Object{"evidence": 80}, "minimum_total": 80,
			"minimum_sources": 1, "minimum_primary_sources": 1, "minimum_critical_claims": 1, "reviewers_required": 1,
			"strong_reviewers_required": 0, "max_revision_rounds": 1}},
		"cross_model_sampling": Object{"enabled": true, "eligible_tiers": []any{"standard"}, "important_reports_per_sample": 2},
	}
	p := "ai-learning/reports/topic.md"
	body := "---\ntitle: Topic\ndomain: ai-learning\nreport_type: concept_report\nquality_schema: report-v2\nquality_tier: standard\nstatus: completed\nupdated_on: 2026-11-01\nsemantic_tags: [test]\n---\n# Topic\n事实一 [原文](../../docs/source.md)。\n"
	ev := Object{"schema_version": 1, "report_path": p, "quality_tier": "standard", "created_on": "2026-11-01",
		"generator":   Object{"model": "writer", "harness": "fixture", "run_id": "write-1", "explicit_model_override": false},
		"task":        Object{"summary": "研究事实", "requirements": []any{Object{"id": "R1", "text": "核对事实一"}}},
		"sources":     []any{Object{"id": "S1", "kind": "local", "title": "原文", "locator": "docs/source.md", "accessed_on": "2026-11-01"}},
		"claims":      []any{Object{"id": "C1", "claim": "事实一", "report_anchor": "事实一", "support": "direct", "source_ids": []any{"S1"}, "critical": true, "evidence": "可核对出处"}},
		"limitations": []any{"合成测试，不是真实研究。"},
	}
	rev := Object{"schema_version": 1, "report_path": p, "quality_tier": "standard", "revision_round": 1,
		"reviews": []any{Object{"role": "primary_review", "reviewer": Object{"model": "reader", "harness": "fixture", "run_id": "review-1", "independent_context": true, "explicit_model_override": false},
			"scores": Object{"evidence": 95}, "score_reasons": Object{"evidence": "已核对"}, "critical_claim_ids_checked": []any{"C1"}, "source_ids_checked": []any{"S1"},
			"requirement_ids_checked": []any{"R1"}, "unsupported_claims": []any{}, "missing_requirements": []any{}, "hard_failures": []any{}, "notes": "完整原文核对"}},
	}
	ep, rp := artifactPaths(p)
	files := map[string]string{p: body, "docs/source.md": "# 来源\n事实一\n", evidenceSchemaPath: jsonText(t, evidence), reviewSchemaPath: jsonText(t, reviewSchema),
		policyPath: jsonText(t, policy), policyArchive + "synthetic-1.json": jsonText(t, policy), ep: jsonText(t, ev)}
	decodedPolicy, _ := DecodeJSON([]byte(files[policyPath]))
	rev["decision"] = Object{"status": "pass", "score": 95, "policy_id": "synthetic-1", "policy_sha256": canonicalDigest(decodedPolicy),
		"report_sha256": digest([]byte(body)), "evidence_sha256": digest([]byte(files[ep]))}
	files[rp] = jsonText(t, rev)
	return files, p
}

func evaluateFixture(t *testing.T, files map[string]string, p string) QualityResult {
	t.Helper()
	rules, err := LoadRules(memory(files))
	if err != nil {
		t.Fatal(err)
	}
	r, err := info(p, files[p], "")
	if err != nil {
		t.Fatal(err)
	}
	return rules.Evaluate(r)
}

func editObject(t *testing.T, files map[string]string, p string, edit func(Object)) {
	t.Helper()
	v, err := DecodeJSON([]byte(files[p]))
	if err != nil {
		t.Fatal(err)
	}
	edit(obj(v))
	files[p] = jsonText(t, v)
}

func TestQualityEvidenceAndReviewBindings(t *testing.T) {
	base, p := qualityFixture(t)
	if got := evaluateFixture(t, base, p); got.Decision != "pass" {
		t.Fatalf("valid fixture: %+v", got)
	}
	ep, rp := artifactPaths(p)
	for _, tc := range []struct {
		name, code string
		edit       func(map[string]string)
	}{
		{"same-run", "REV013", func(f map[string]string) {
			editObject(t, f, rp, func(v Object) { obj(obj(array(v["reviews"])[0])["reviewer"])["run_id"] = "write-1" })
		}},
		{"not-independent", "REV010", func(f map[string]string) {
			editObject(t, f, rp, func(v Object) { obj(obj(array(v["reviews"])[0])["reviewer"])["independent_context"] = false })
		}},
		{"duplicate-reviews", "REV019", func(f map[string]string) {
			editObject(t, f, rp, func(v Object) { v["reviews"] = append(array(v["reviews"]), array(v["reviews"])[0]) })
		}},
		{"missing-requirement", "REV016", func(f map[string]string) {
			editObject(t, f, rp, func(v Object) { obj(array(v["reviews"])[0])["requirement_ids_checked"] = []any{} })
		}},
		{"changed-report", "QG014", func(f map[string]string) { f[p] += "改变后的结论\n" }},
		{"changed-evidence-bytes", "QG015", func(f map[string]string) { f[ep] += "\n" }},
		{"missing-source", "EVM035", func(f map[string]string) { delete(f, "docs/source.md") }},
		{"disabled-model", "MODEL001", func(f map[string]string) {
			editObject(t, f, rp, func(v Object) { obj(obj(array(v["reviews"])[0])["reviewer"])["model"] = "disabled" })
		}},
		{"forged-policy-sha", "QG008", func(f map[string]string) {
			editObject(t, f, rp, func(v Object) { obj(v["decision"])["policy_sha256"] = strings.Repeat("0", 64) })
		}},
		{"low-score", "SCORE001", func(f map[string]string) {
			editObject(t, f, rp, func(v Object) { obj(array(v["reviews"])[0])["scores"] = Object{"evidence": 60} })
		}},
	} {
		t.Run(tc.name, func(t *testing.T) {
			files := maps.Clone(base)
			tc.edit(files)
			got := evaluateFixture(t, files, p)
			if got.Decision == "pass" || !hasCode(got.Findings, tc.code) {
				t.Fatalf("missing %s: %+v", tc.code, got)
			}
		})
	}
}

func TestPolicyQualificationAndPinnedDecision(t *testing.T) {
	files, p := qualityFixture(t)
	_, rp := artifactPaths(p)
	// Current policy may tighten; an unchanged completed report still uses its
	// immutable policy. A forged/missing archive is not a downgrade to current.
	editObject(t, files, policyPath, func(v Object) {
		v["policy_id"] = "synthetic-2"
		obj(obj(v["tiers"])["standard"])["strong_reviewers_required"] = 1
	})
	files[policyArchive+"synthetic-2.json"] = files[policyPath]
	if got := evaluateFixture(t, files, p); got.Decision != "pass" || got.PolicySource != "archive" {
		t.Fatalf("pinned report unexpectedly changed: %+v", got)
	}
	editObject(t, files, rp, func(v Object) {
		current, _ := DecodeJSON([]byte(files[policyPath]))
		obj(v["decision"])["policy_id"] = "synthetic-2"
		obj(v["decision"])["policy_sha256"] = canonicalDigest(current)
	})
	if got := evaluateFixture(t, files, p); !hasCode(got.Findings, "REV020") {
		t.Fatal("current strong-review requirement was not enforced", got)
	}
	editObject(t, files, rp, func(v Object) { obj(obj(array(v["reviews"])[0])["reviewer"])["model"] = "strong" })
	if got := evaluateFixture(t, files, p); got.Decision != "pass" {
		t.Fatal(got)
	}
	delete(files, policyArchive+"synthetic-2.json")
	if _, err := LoadRules(memory(files)); err == nil {
		t.Fatal("missing current policy archive accepted")
	}
}

func TestAffectedReportsAndImmutableArtifacts(t *testing.T) {
	files, p := qualityFixture(t)
	for _, tc := range []struct{ name, target, code string }{
		{"source-deleted", "docs/source.md", "EVM035"},
		{"archive-deleted", policyArchive + "synthetic-1.json", "POLICY_IMMUTABLE"},
		{"orphan-sidecar", "ai-learning/reports/.quality/missing.review.json", "ORPHAN_QUALITY_ARTIFACT"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			after := maps.Clone(files)
			delete(after, tc.target)
			if tc.name == "orphan-sidecar" {
				after[tc.target] = "{}"
			}
			s := memory(after)
			rules, err := LoadRules(memory(files))
			if err != nil {
				t.Fatal(err)
			}
			rules.source = s
			reports, _ := Catalog(s)
			got := AuditReports(&Candidate{Before: memory(files), After: s, Changed: []string{tc.target}}, rules, reports, false)
			if !hasCode(got.Findings, tc.code) {
				t.Fatalf("%s did not affect %s: %+v", tc.target, p, got)
			}
		})
	}
}

func TestSourceEditsDoNotRewriteHistoricalMetadata(t *testing.T) {
	base, p := qualityFixture(t)
	base[p] = strings.Replace(base[p], "report_type: concept_report", "report_type: concept_deep_dive", 1)
	base[p] = strings.Replace(base[p], "[原文]", "[原始材料]", 1)
	_, rp := artifactPaths(p)
	editObject(t, base, rp, func(v Object) { obj(v["decision"])["report_sha256"] = digest([]byte(base[p])) })
	for _, tc := range []struct {
		name, changed, errorCode string
		edit                     func(map[string]string)
	}{
		{"source-edit", "docs/source.md", "", func(f map[string]string) { f["docs/source.md"] += "来源补充\n" }},
		{"source-deleted", "docs/source.md", "EVM035", func(f map[string]string) { delete(f, "docs/source.md") }},
		{"report-edit", p, "META010", func(f map[string]string) { f[p] += "正文补充\n" }},
	} {
		t.Run(tc.name, func(t *testing.T) {
			after := maps.Clone(base)
			tc.edit(after)
			s := memory(after)
			rules, err := LoadRules(s)
			if err != nil {
				t.Fatal(err)
			}
			reports, _ := Catalog(s)
			result := AuditReports(&Candidate{Before: memory(base), After: s, Changed: []string{tc.changed}}, rules, reports, true)
			errorFound := false
			for _, f := range result.Findings {
				if f.Code == "META010" && tc.changed != p && f.Severity != "warning" {
					t.Fatal("unmodified historical metadata blocks a source edit", f)
				}
				if f.Severity == "error" && (tc.errorCode == "" || f.Code == tc.errorCode) {
					errorFound = true
				}
			}
			if errorFound != (tc.errorCode != "") {
				t.Fatalf("unexpected source/report enforcement: %+v", result)
			}
		})
	}
}

func TestReadmeUsesStagedContentAndDeletedTargets(t *testing.T) {
	root := fixtureRepo(t)
	writeFixture(t, root, "README.md", "[source](source.md#source)\n")
	writeFixture(t, root, "source.md", "# Source\n")
	commitFixture(t, root)
	writeFixture(t, root, "README.md", "[missing](missing.md)\n")
	runGit(t, root, "add", "README.md")
	writeFixture(t, root, "README.md", "[source](source.md#source)\n")
	if noErrors(CheckLinks(captureFixture(t, root, "index").After, "README.md", true)) {
		t.Fatal("unstaged repair hid a staged broken link")
	}
	runGit(t, root, "add", "README.md")
	runGit(t, root, "rm", "source.md")
	if noErrors(CheckLinks(captureFixture(t, root, "index").After, "README.md", true)) {
		t.Fatal("unchanged README did not detect a deleted target")
	}
}

func TestReportScopeDoesNotExpandOrdinaryEdits(t *testing.T) {
	paths := []string{"ai-learning/reports/topic.md", "ai-learning/reports/.quality/topic.transcription-review.json", "README.md", "docs/REPORT_INDEX.md"}
	if FullReportAuditRequired(paths) || ContextRequired(paths) || !SamplingRequired(paths) {
		t.Fatal("ordinary report edit expanded into a global audit")
	}
	for _, p := range []string{"ai-practice/experiments/exp_fixture.md", "podcast-learning/reports/.quality/deleted.review.json"} {
		if !SamplingRequired([]string{p}) {
			t.Fatal("missing sampling trigger", p)
		}
	}
	for _, p := range []string{"schemas/report-review-v1.schema.json", moduleDir + "/internal/publicquality/review.go", ".github/workflows/quality.yml"} {
		if !FullReportAuditRequired([]string{p}) || !ContextRequired([]string{p}) {
			t.Fatal("gate change did not expand its audit", p)
		}
	}
	for _, suffix := range []string{"evidence", "review", "transcription-review"} {
		if artifactReport("ai-learning/reports/.quality/topic."+suffix+".json") != "ai-learning/reports/topic.md" {
			t.Fatal("sidecar was not mapped to its owner")
		}
	}
}

func TestRenameContractMatchesIndexAndCI(t *testing.T) {
	for _, kind := range []string{"same-domain", "copy", "cross-domain", "two-copies", "from-note"} {
		t.Run(kind, func(t *testing.T) {
			root := fixtureRepo(t)
			old := "ai-learning/reports/old.md"
			if kind == "from-note" {
				old = "docs/old.md"
			}
			body := "---\ntitle: Legacy\ndomain: ai-learning\nreport_type: concept_report\nstatus: completed\nquality_schema: report-v1\nupdated_on: 2026-11-01\nsemantic_tags: [legacy]\n---\n# Legacy\n来源：https://example.invalid/source\n"
			writeFixture(t, root, old, body)
			commitFixture(t, root)
			base := captureFixture(t, root, "head").Head
			next := "ai-learning/reports/new name.md"
			if kind == "cross-domain" {
				next = "cs-learning/reports/new.md"
			}
			writeFixture(t, root, next, body)
			if kind != "copy" {
				if err := os.Remove(filepath.Join(root, old)); err != nil {
					t.Fatal(err)
				}
			}
			if kind == "two-copies" {
				writeFixture(t, root, "ai-learning/reports/another.md", body)
			}
			runGit(t, root, "add", ".")
			staged := captureFixture(t, root, "index")
			selected := newReports(staged)
			want := 1
			if kind == "same-domain" {
				want = 0
			}
			if len(selected) != want {
				t.Fatalf("new report classification: %v", selected)
			}
			commitFixture(t, root)
			ci := captureFixture(t, root, "head")
			if err := ci.CompareBase(base); err != nil {
				t.Fatal(err)
			}
			if !maps.Equal(selected, newReports(ci)) {
				t.Fatal("CI and staged classification disagree")
			}
			if err := ci.CompareBase("main"); err == nil {
				t.Fatal("mutable CI base accepted")
			}
		})
	}
}

func TestRenameDoesNotHideExistingContractErrors(t *testing.T) {
	root := fixtureRepo(t)
	old := "ai-learning/reports/old.md"
	body := "---\ntitle: Legacy\ndomain: ai-learning\nreport_type: concept_report\nstatus: done\nquality_schema: report-v1\nupdated_on: 2026-11-01\nsemantic_tags: [legacy]\n---\n# Legacy\n来源：https://example.invalid/source\n"
	writeFixture(t, root, old, body)
	commitFixture(t, root)
	runGit(t, root, "mv", old, "ai-learning/reports/renamed.md")
	c := captureFixture(t, root, "index")
	files, _ := qualityFixture(t)
	rules, err := LoadRules(memory(files))
	if err != nil {
		t.Fatal(err)
	}
	reports, _ := Catalog(c.After)
	result := AuditReports(c, rules, reports, false)
	for _, f := range result.Findings {
		if f.Code == "META005" && f.Severity == "error" {
			return
		}
	}
	t.Fatal("renaming bypassed a versioned report contract", result)
}

func TestGateSourceBindingAndScratchBoundary(t *testing.T) {
	hashes := map[string]string{"git.go": digest([]byte("original"))}
	files := map[string]string{moduleDir + "/git.go": "original"}
	if err := compareBuildSources(memory(files), hashes); err != nil {
		t.Fatal(err)
	}
	files[moduleDir+"/new.go"] = "new source"
	if compareBuildSources(memory(files), hashes) == nil {
		t.Fatal("new unstaged source not rejected")
	}
	delete(files, moduleDir+"/new.go")
	files[moduleDir+"/git.go"] = "modified"
	if compareBuildSources(memory(files), hashes) == nil {
		t.Fatal("stale executable source not rejected")
	}
	root := fixtureRepo(t)
	if _, err := makeScratch(root, root); err == nil {
		t.Fatal("scratch directory inside a checkout accepted")
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := Capture(ctx, root, "index"); err == nil {
		t.Fatal("cancelled capture treated as empty changes")
	}
}

func TestGateSummaryPreservesFailureAndCounts(t *testing.T) {
	result := GateResult{OK: false, Steps: []Step{{ID: "context", Status: "failed"}}}
	for i := 0; i < 100; i++ {
		result.Findings = append(result.Findings, warning("history.md", "OLD", "历史告警"))
	}
	result.Findings = append(result.Findings, issue("current.md", "CURRENT", "当前错误"))
	got := result.Summary()
	if got.OK || got.Errors != 1 || got.Warnings != 100 || len(got.Findings) != 16 || got.Omitted != 85 || got.Details == "" {
		t.Fatalf("summary lost diagnostics: %+v", got)
	}
	if got.Findings[0].Code != "CURRENT" || got.Steps[0].Status != "failed" || len(result.Findings) != 101 || result.Findings[0].Code != "OLD" {
		t.Fatal("summary hid an error or mutated the full evidence")
	}
}

const publicCIWorkflow = "jobs:\n  validate:\n    steps:\n      - run: |\n          go -C packages/everagent-core test -mod=readonly ./...\n          go -C packages/everagent-core vet -mod=readonly ./...\n          go -C packages/everagent-core run -mod=readonly -trimpath -buildvcs=false \\\n            ./cmd/ea-quality quick --scope head --base \"$BASE_REVISION\"\n"

func TestPublicCIWiringRequiresExecutableGoSteps(t *testing.T) {
	base := map[string]string{
		"scripts/ecommit.sh":              "./cmd/ea-git",
		moduleDir + "/cmd/ea-git/main.go": "core.Commit( publicquality.Check(",
	}
	workflow := publicCIWorkflow
	for _, tc := range []struct {
		name, text string
		valid      bool
	}{
		{"wired", workflow, true},
		{"commented", strings.ReplaceAll(workflow, "go -C", "# go -C"), false},
		{"echoed", strings.ReplaceAll(workflow, "go -C", "echo go -C"), false},
		{"ignored-failures", strings.ReplaceAll(workflow, "- run: |", "- continue-on-error: true\n        run: |"), false},
		{"disabled-step", strings.ReplaceAll(workflow, "- run: |", "- if: false\n        run: |"), false},
		{"narrowed-tests", strings.Replace(workflow, "test -mod=readonly ./...", "test -mod=readonly ./internal/publicquality", 1), false},
		{"filtered-tests", strings.Replace(workflow, "test -mod=readonly", "test -mod=readonly -run '^$'", 1), false},
		{"listed-tests", strings.Replace(workflow, "test -mod=readonly", "test -mod=readonly -list .", 1), false},
		{"skipped-test-execution", strings.Replace(workflow, "test -mod=readonly", "test -mod=readonly -exec true", 1), false},
		{"skipped-gate-execution", strings.Replace(workflow, "run -mod=readonly", "run -mod=readonly -exec true", 1), false},
		{"no-base", strings.Replace(workflow, " --base \"$BASE_REVISION\"", "", 1), false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			files := maps.Clone(base)
			files[".github/workflows/quality.yml"] = tc.text
			if got := checkPublicBindings(memory(files)); noErrors(got) != tc.valid {
				t.Fatalf("unexpected wiring result: %+v", got)
			}
		})
	}
}

func TestHistoricalBehaviorIsNotANewReplay(t *testing.T) {
	const recordPath = "evals/results/synthetic-context-ab.json"
	fingerprint := strings.Repeat("a", 64)
	for _, tc := range []struct {
		name, status string
		change       func(Object)
		errors       bool
	}{
		{"matching-complete", "current-record", func(Object) {}, false},
		{"changed-context", "context-changed", func(r Object) {
			obj(nested(r, "refs", "candidate"))["context_sha256"] = strings.Repeat("b", 64)
		}, false},
		{"unaccepted", "unaccepted", func(r Object) { obj(r["comparison"])["accepted"] = false }, false},
		{"insufficient-repetitions", "insufficient-repetitions", func(r Object) { r["repetitions"] = 2 }, false},
		{"partial-baseline", "incomplete", func(r Object) {
			obj(nested(r, "summaries", "baseline"))["successful_runs"] = 5
		}, false},
		{"partial-candidate", "incomplete", func(r Object) {
			obj(nested(r, "summaries", "candidate"))["runs"] = 5
		}, false},
		{"invalid-schema", "invalid-schema", func(r Object) { r["schema_version"] = 99 }, true},
	} {
		t.Run(tc.name, func(t *testing.T) {
			record := Object{
				"schema_version": 1, "repetitions": 3,
				"comparison": Object{"accepted": true},
				"refs":       Object{"candidate": Object{"context_sha256": fingerprint}},
				"summaries": Object{
					"baseline":  Object{"runs": 6, "successful_runs": 6},
					"candidate": Object{"runs": 6, "successful_runs": 6},
				},
			}
			tc.change(record)
			out := ContextAudit{Cases: 2, BehaviorContextSHA256: fingerprint}
			got := historicalBehavior(memory(map[string]string{recordPath: jsonText(t, record)}), recordPath, &out)
			if out.HistoricalBehaviorStatus != tc.status || out.BehaviorReplayExecuted || noErrors(got) == tc.errors {
				t.Fatalf("wrong historical evidence result: %+v, %+v", out, got)
			}
			if (len(got) == 0) != (tc.status == "current-record") {
				t.Fatalf("stale/incomplete record must remain visible: %+v", got)
			}
		})
	}
	for _, files := range []map[string]string{{}, {recordPath: "not-json"}} {
		out := ContextAudit{Cases: 2, BehaviorContextSHA256: fingerprint}
		got := historicalBehavior(memory(files), recordPath, &out)
		if noErrors(got) || out.HistoricalBehaviorStatus != "unreadable" || out.BehaviorReplayExecuted {
			t.Fatalf("unreadable history accepted: %+v, %+v", out, got)
		}
	}
}

func TestGateEnvironmentDoesNotInheritSessionOrCredentials(t *testing.T) {
	scratch, originalHome := t.TempDir(), t.TempDir()
	t.Setenv("HOME", originalHome)
	t.Setenv("USERPROFILE", originalHome)
	caches := map[string]string{"GOCACHE": t.TempDir(), "GOMODCACHE": t.TempDir()}
	for key, value := range caches {
		t.Setenv(key, value)
	}
	for _, key := range []string{"OPENAI_API_KEY", "SSH_AUTH_SOCK", "ORCA_SESSION_ID", "GIT_CONFIG_COUNT", "GOFLAGS", "GOENV"} {
		t.Setenv(key, "fixture")
	}
	values, err := checkEnvironment(context.Background(), scratch)
	if runtime.GOOS == "windows" {
		// Until the Job Object adapter exists, fail before launching tests,
		// rather than count an uncontained child process as supported.
		if err == nil || !strings.Contains(err.Error(), "Windows检查进程树回收尚未实现") {
			t.Fatalf("unsupported process containment was not reported: %v", err)
		}
		cmd := exec.CommandContext(context.Background(), "go", "version")
		if err := runCheckProcess(cmd); err == nil || cmd.Process != nil {
			t.Fatal("unsupported process containment started a child")
		}
		return
	}
	if err != nil {
		t.Fatal(err)
	}
	env := map[string]string{}
	for _, value := range values {
		key, value, _ := strings.Cut(value, "=")
		if _, duplicate := env[key]; duplicate {
			t.Fatalf("duplicate environment key: %s", key)
		}
		env[key] = value
	}
	for _, key := range []string{"OPENAI_API_KEY", "SSH_AUTH_SOCK", "ORCA_SESSION_ID", "GIT_CONFIG_COUNT"} {
		if _, exists := env[key]; exists {
			t.Fatalf("test environment inherited %s", key)
		}
	}
	if env["HOME"] != filepath.Join(scratch, "home") || env["USERPROFILE"] != env["HOME"] || env["HOME"] == originalHome {
		t.Fatal("tests are not using a disposable home")
	}
	for key, expected := range map[string]string{
		"GOFLAGS": "", "GOENV": "off", "GOTOOLCHAIN": "local", "GOWORK": "off", "GOPROXY": "off",
		"GIT_CONFIG_GLOBAL": os.DevNull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
		"GOCACHE": caches["GOCACHE"], "GOMODCACHE": caches["GOMODCACHE"],
	} {
		if env[key] != expected {
			t.Fatalf("wrong test environment for %s", key)
		}
	}
	cmd := exec.Command("go", "env", "GOTELEMETRY")
	cmd.Dir, cmd.Env = scratch, values
	if output, err := cmd.CombinedOutput(); err != nil || strings.TrimSpace(string(output)) != "off" {
		t.Fatalf("disposable Go telemetry was not disabled: %v", err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := checkEnvironment(ctx, scratch); err == nil {
		t.Fatal("cancelled toolchain query accepted")
	}
}

func contextFixture(t *testing.T) (map[string]string, string) {
	t.Helper()
	files, report := qualityFixture(t)
	for _, p := range contextPaths(memory(files)) {
		files[p] = "# Owner\n"
	}
	files["CLAUDE.md"] = "@AGENTS.md\n"
	files[reportSkill] = "---\nname: everagent-report\ndescription: Use for reports; skip other tasks.\n---\n# Report\n"
	budgets := Object{}
	for _, key := range []string{"root_repo_owned_bytes_warn", "root_repo_owned_bytes_max", "domain_agents_bytes_max", "claude_bridge_bytes_max", "discoverable_skill_description_chars_max", "discoverable_skill_entrypoint_bytes_max", "on_demand_playbook_entrypoint_bytes_warn"} {
		budgets[key] = 8192
	}
	budgets["discoverable_skill_count_max"] = 1
	files[instructionPolicy] = jsonText(t, Object{"schema_version": 1, "budgets": budgets, "owners": Object{"ace_context_ab_result": "evals/results/fixture.json"}})
	files["evals/results/fixture.json"] = `{"schema_version":1,"comparison":{"accepted":false}}`
	files["scripts/ecommit.sh"], files[moduleDir+"/cmd/ea-git/main.go"] = "./cmd/ea-git", "core.Commit( publicquality.Check("
	files[".github/workflows/quality.yml"] = publicCIWorkflow
	item := Object{"id": "case", "prompt": "Read the source", "expected_route": "root", "artifact_policy": "required", "max_initial_project_files": 2,
		"quality_tier": "standard", "required_checks": []any{"quality_gate"}, "expected_skill_paths": []any{reportSkill}, "forbidden_skill_paths": []any{},
		"completion_signals": []any{"report"}, "expected_completed": true, "expected_stop_reason": "completed"}
	files["evals/ace-report-tasks.json"] = jsonText(t, Object{"schema_version": 2, "cases": []any{item}})
	files["evals/report-quality-anchors.json"] = jsonText(t, Object{"anchors": []any{Object{"id": "anchor", "report_path": report}}})
	files["evals/report-quality-replays.json"] = jsonText(t, Object{"schema_version": 1, "cases": []any{Object{
		"id": "replay", "report_path": report, "quality_tier": "standard", "status": "completed", "minimum_score": 90}}})
	return files, report
}

func auditContextFixture(t *testing.T, files map[string]string) ContextAudit {
	t.Helper()
	s := memory(files)
	rules, err := LoadRules(s)
	if err != nil {
		t.Fatal(err)
	}
	reports, findings := Catalog(s)
	if !noErrors(findings) {
		t.Fatal(findings)
	}
	return AuditContext(s, rules, reports)
}

func TestContextSnapshotKeepsConstraintsAndRawEvidence(t *testing.T) {
	base, report := contextFixture(t)
	baseline := auditContextFixture(t, base)
	if !noErrors(baseline.Findings) || baseline.Cases != 1 || baseline.ReportReplays != 1 || baseline.BehaviorReplayExecuted {
		t.Fatalf("invalid context fixture: %+v", baseline)
	}
	t.Run("all-project-skill-fingerprint", func(t *testing.T) {
		files := maps.Clone(base)
		files["extra-domain/skills/demo/SKILL.md"] = "# New input\n"
		got := auditContextFixture(t, files)
		if got.BehaviorContextSHA256 == baseline.BehaviorContextSHA256 || got.Files != baseline.Files {
			t.Fatal("fingerprint lost an input or expanded the active context scope")
		}
	})
	for _, field := range []string{"expected_skill_paths", "forbidden_skill_paths", "artifact_expected_skill_paths", "expected_initial_files", "required_checks", "artifact_required_checks", "completion_signals"} {
		t.Run(field, func(t *testing.T) {
			for _, bad := range []any{true, nil, []any{reportSkill, 42}} {
				files := maps.Clone(base)
				editObject(t, files, "evals/ace-report-tasks.json", func(v Object) { obj(array(v["cases"])[0])[field] = bad })
				if got := auditContextFixture(t, files); !hasCode(got.Findings, "CONTEXT_CASE_FIELDS") {
					t.Fatalf("invalid %s constraint was silently discarded: %+v", field, got.Findings)
				}
			}
		})
	}
	t.Run("raw-replay-status", func(t *testing.T) {
		files := maps.Clone(base)
		files[report] = strings.Replace(files[report], "status: completed", "status: done", 1)
		_, review := artifactPaths(report)
		editObject(t, files, review, func(v Object) { obj(v["decision"])["report_sha256"] = digest([]byte(files[report])) })
		got := auditContextFixture(t, files)
		if !hasCode(got.Findings, "CONTEXT_REPLAY_METADATA") || hasCode(got.Findings, "CONTEXT_REPLAY_QUALITY") {
			t.Fatalf("raw metadata drift not distinguished from normalized quality: %+v", got.Findings)
		}
	})
	for _, tc := range []struct{ path, budget, code string }{
		{"AGENTS.md", "root_repo_owned_bytes_max", "CONTEXT_SIZE"},
		{"ai-learning/AGENTS.md", "domain_agents_bytes_max", "CONTEXT_SIZE"},
		{"CLAUDE.md", "claude_bridge_bytes_max", "CONTEXT_BRIDGE"},
		{reportSkill, "discoverable_skill_entrypoint_bytes_max", "CONTEXT_SKILL_SIZE"},
	} {
		t.Run("bom-"+tc.budget, func(t *testing.T) {
			files := maps.Clone(base)
			if files[tc.path] == "" {
				files[tc.path] = "# Owner\n"
			}
			editObject(t, files, instructionPolicy, func(v Object) { obj(v["budgets"])[tc.budget] = len(files[tc.path]) })
			if got := auditContextFixture(t, files); !noErrors(got.Findings) {
				t.Fatalf("exact byte budget should pass: %+v", got.Findings)
			}
			files[tc.path] = "\ufeff" + files[tc.path]
			if got := auditContextFixture(t, files); !hasCode(got.Findings, tc.code) || noErrors(got.Findings) {
				t.Fatalf("BOM bytes missing from actual audit budget: %+v", got.Findings)
			}
		})
	}
}
