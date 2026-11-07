package publicquality

import "sort"

type SampleReport struct {
	Report     string   `json:"report"`
	SamplingOn string   `json:"sampling_on"`
	Generator  string   `json:"generator_model"`
	Reviewers  []string `json:"reviewer_models"`
	CrossModel bool     `json:"cross_model_audited"`
}
type SampleWindow struct {
	Start    int      `json:"start"`
	End      int      `json:"end"`
	Complete bool     `json:"complete"`
	Covered  bool     `json:"covered"`
	Reports  []string `json:"reports"`
}
type SamplingResult struct {
	PolicyID  string         `json:"policy_id"`
	Enabled   bool           `json:"enabled"`
	Interval  int            `json:"interval"`
	SampleDue bool           `json:"sample_due"`
	Reports   []SampleReport `json:"reports"`
	Windows   []SampleWindow `json:"sampling_windows"`
	Findings  []Finding      `json:"findings"`
}

// A sample belongs to a fixed chronological block, not a rolling debt that
// would force almost every new report to consume a scarce model call.
func (rules *Rules) Sampling(reports []Report) SamplingResult {
	p := rules.Current
	config := obj(p["cross_model_sampling"])
	interval, _ := integer(config["important_reports_per_sample"])
	out := SamplingResult{PolicyID: str(p["policy_id"]), Enabled: config["enabled"] == true, Interval: interval, Reports: []SampleReport{}, Windows: []SampleWindow{}, Findings: []Finding{}}
	if !out.Enabled {
		return out
	}
	if interval < 1 {
		out.Findings = append(out.Findings, issue(policyPath, "SAMPLE_POLICY_INVALID", "启用抽样时窗口大小必须为正整数。"))
		return out
	}
	recorded := str(nested(p, "preference_source", "recorded_on"))
	for _, r := range reports {
		if r.Metadata.String("quality_schema") != currentReportSchema || !containsString([]string{"completed", "archived"}, r.Metadata.String("status")) || !contains(config["eligible_tiers"], r.Metadata.String("quality_tier")) {
			continue
		}
		updated := r.Metadata.String("updated_on")
		if recorded != "" && updated != "" && updated < recorded {
			continue
		}
		ep, rp := artifactPaths(r.Path)
		ev, ee := JSON(rules.source, ep)
		rev, re := JSON(rules.source, rp)
		if ee != nil || re != nil {
			out.Findings = append(out.Findings, issue(r.Path, "SAMPLE_INPUT_UNREADABLE", "符合抽样条件的报告缺少可读质量文件；不将失败当成零样本。"))
			continue
		}
		gen := obj(ev["generator"])
		entry := SampleReport{Report: r.Path, Generator: normalizeModel(str(gen["model"]), p), Reviewers: []string{}}
		reviewers := append([]any{}, array(rev["reviews"])...)
		history := array(rev["history"])
		if len(history) > 0 {
			previous := obj(history[len(history)-1])
			currentRound, _ := integer(rev["revision_round"])
			previousRound, _ := integer(previous["revision_round"])
			if currentRound > 1 && previousRound == currentRound-1 {
				reviewers = append(reviewers, array(previous["reviews"])...)
			}
		}
		seen := map[string]bool{}
		for _, raw := range reviewers {
			a := obj(obj(raw)["reviewer"])
			model := normalizeModel(str(a["model"]), p)
			if model != "" && !seen[model] {
				entry.Reviewers = append(entry.Reviewers, model)
				seen[model] = true
			}
			// Do not turn an invalid historical self-review into a strong sample.
			independent := nonempty(a["run_id"]) && nonempty(a["harness"]) && a["independent_context"] == true && a["run_id"] != gen["run_id"]
			entry.CrossModel = entry.CrossModel || independent && qualified(model, p, "strong_reviewers") && model != entry.Generator
		}
		entry.SamplingOn = str(ev["created_on"])
		if entry.SamplingOn == "" {
			dates := []string{str(nested(rev, "decision", "evaluated_on"))}
			for _, h := range history {
				dates = append(dates, str(nested(h, "decision", "evaluated_on")))
			}
			sort.Strings(dates)
			for _, d := range dates {
				if d != "" {
					entry.SamplingOn = d
					break
				}
			}
		}
		if entry.SamplingOn == "" {
			entry.SamplingOn = updated
		}
		if !ValidDate(entry.SamplingOn) {
			out.Findings = append(out.Findings, issue(r.Path, "SAMPLE_DATE_INVALID", "抽样日期缺失或无效，不能确定固定窗口。"))
		}
		out.Reports = append(out.Reports, entry)
	}
	sort.Slice(out.Reports, func(i, j int) bool {
		a, b := out.Reports[i], out.Reports[j]
		if a.SamplingOn != b.SamplingOn {
			return a.SamplingOn < b.SamplingOn
		}
		return a.Report < b.Report
	})
	for start := 0; start < len(out.Reports); start += interval {
		end := min(start+interval, len(out.Reports))
		w := SampleWindow{Start: start + 1, End: end, Complete: end-start == interval, Reports: []string{}}
		for _, r := range out.Reports[start:end] {
			w.Reports = append(w.Reports, r.Report)
			w.Covered = w.Covered || r.CrossModel
		}
		out.Windows = append(out.Windows, w)
		if w.Complete && !w.Covered {
			out.SampleDue = true
		}
	}
	if out.SampleDue {
		out.Findings = append(out.Findings, issue(policyPath, "SAMPLE_DUE", "有完整固定窗口尚无有效跨模型强审；不足一窗的尾部不追债。"))
	}
	return out
}
