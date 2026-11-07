package publicquality

import (
	"maps"
	"math"
)

// These checks validate the recorded review contract, not that a model
// actually read its sources. The independent session's evidence remains
// necessary; a process name or a worker's chat message is not substituted.
type ReviewSummary struct {
	Score         *float64           `json:"score"`
	Dimensions    map[string]float64 `json:"dimension_scores"`
	Models        []string           `json:"reviewer_models"`
	Revision      int                `json:"revision_round"`
	StrongReviews int                `json:"strong_reviews"`
	ScarceCalls   int                `json:"scarce_model_calls"`
}

type QualityResult struct {
	Report       string `json:"report"`
	Decision     string `json:"decision"`
	PolicyID     string `json:"policy_id"`
	PolicySHA256 string `json:"policy_sha256"`
	PolicySource string `json:"policy_source"`
	ReviewSummary
	Findings []Finding `json:"findings"`
}

func isDraft(r Report) bool {
	return containsString([]string{"in_progress", "planned"}, r.Metadata.String("status"))
}

func (rules *Rules) checkReview(r Report, record Object, ev evidenceSummary, policy Object) ([]Finding, ReviewSummary) {
	_, file := artifactPaths(r.Path)
	f := findingList{file: file, items: schemaFindings(file, "REV000", rules.review, record)}
	s := ReviewSummary{Revision: 1, Dimensions: map[string]float64{}, Models: []string{}}
	if len(f.items) > 0 {
		return f.items, s
	}
	s.Revision, _ = integer(record["revision_round"])
	tier := obj(nested(policy, "tiers", r.Metadata.String("quality_tier")))
	f.require(record["report_path"] == r.Path, "REV002", "复核记录与报告路径不一致。")
	f.require(record["quality_tier"] == r.Metadata.String("quality_tier"), "REV003", "复核等级与报告不一致。")
	reviews := array(record["reviews"])
	required, _ := integer(tier["reviewers_required"])
	f.require(len(reviews) >= required, "REV006", "独立复核数量不足。")
	runIDs := []string{}
	scarceWithoutOverride := 0
	countScarce := func(actor Object) {
		if qualified(str(actor["model"]), policy, "scarce_models") {
			s.ScarceCalls++
			if actor["explicit_model_override"] != true {
				scarceWithoutOverride++
			}
		}
	}
	for _, raw := range reviews {
		item := obj(raw)
		actor := obj(item["reviewer"])
		requiredFields(&f, actor, "REV009", "model", "harness", "run_id")
		id := str(actor["run_id"])
		runIDs = append(runIDs, id)
		f.require(id != str(ev.generator["run_id"]), "REV013", "生成与复核使用了同一run_id。")
		f.require(actor["independent_context"] == true, "REV010", "复核必须记录独立会话。")
		model := normalizeModel(str(actor["model"]), policy)
		s.Models = append(s.Models, model)
		f.items = append(f.items, modelFindings(file, actor, str(item["role"]), policy)...)
		if qualified(model, policy, "strong_reviewers") {
			s.StrongReviews++
		}
		countScarce(actor)
		if qualified(model, policy, "scarce_models") && item["role"] == "escalation_review" {
			f.require(nonempty(item["escalation_reason"]), "MODEL003", "稀缺模型升级复核缺少原因。")
		}
		score := 0.0
		for _, dimension := range keys(obj(policy["dimensions"])) {
			weight, _ := number(nested(policy, "dimensions", dimension))
			value, _ := number(nested(item, "scores", dimension))
			score += value * weight / 100
			if old, ok := s.Dimensions[dimension]; !ok || value < old {
				s.Dimensions[dimension] = value
			}
			f.require(nonempty(nested(item, "score_reasons", dimension)), "REV023", "缺少评分理由："+dimension)
		}
		score = math.RoundToEven(score*100) / 100
		if s.Score == nil || score < *s.Score {
			s.Score = &score
		}
		checks := map[string][]string{"critical_claim_ids_checked": ev.criticalClaims, "source_ids_checked": ev.criticalSources, "requirement_ids_checked": ev.requirements}
		if sourceMapRequired(r) {
			checks["coverage_unit_ids_checked"] = ev.coverage
			checkContentMap(&f, r, item, ev)
		}
		for _, field := range keysStringLists(checks) {
			f.require(subset(checks[field], stringsOf(item[field])), "REV016", "未完整核对："+field)
		}
		for _, field := range []string{"unsupported_claims", "missing_requirements", "hard_failures"} {
			f.require(len(array(item[field])) == 0, "REV018", "复核仍有未解决项："+field)
		}
		f.require(subset(stringsOf(item["unsupported_claims"]), ev.claims), "REV024", "不支持的claim清单含未知ID。")
		f.require(subset(stringsOf(item["missing_requirements"]), ev.requirements), "REV025", "缺失要求清单含未知ID。")
		f.require(nonempty(item["notes"]), "REV027", "复核缺少审查摘要。")
	}
	f.require(unique(runIDs), "REV019", "复核run_id重复，不算独立复核。")
	requiredStrong, _ := integer(tier["strong_reviewers_required"])
	f.require(s.StrongReviews >= requiredStrong, "REV020", "强模型复核数量不足。")
	countScarce(ev.generator)
	for _, previous := range array(record["history"]) {
		for _, raw := range array(obj(previous)["reviews"]) {
			countScarce(obj(obj(raw)["reviewer"]))
		}
	}
	limit, _ := integer(nested(policy, "model_policy", "scarce_model_max_calls_per_report"))
	f.require(scarceWithoutOverride <= limit, "MODEL004", "未获显式覆盖的稀缺模型调用超过单篇上限。")
	minimum, _ := number(tier["minimum_total"])
	f.require(s.Score == nil || *s.Score >= minimum, "SCORE001", "最低复核总分未达门槛。")
	for _, dimension := range keys(obj(tier["minimum_dimension_scores"])) {
		minimum, _ := number(nested(tier, "minimum_dimension_scores", dimension))
		if value, ok := s.Dimensions[dimension]; ok {
			f.require(value >= minimum, "SCORE002", "最低维度分未达门槛："+dimension)
		}
	}
	return f.items, s
}

func keysStringLists(m map[string][]string) []string {
	o := Object{}
	for k := range m {
		o[k] = true
	}
	return keys(o)
}

func checkContentMap(f *findingList, r Report, item Object, ev evidenceSummary) {
	units := array(item["source_content_map"])
	f.require(len(units) >= max(3, len(ev.coverage), chapters(r)), "REV028", "来源优先地图未覆盖足够的独立来源单元或shownotes章节。")
	ids, mapped := []string{}, []string{}
	for _, raw := range units {
		unit := obj(raw)
		requiredFields(f, unit, "REV029", "id", "title", "importance", "assessment", "notes")
		ids = append(ids, str(unit["id"]))
		sources, coverage := stringsOf(unit["source_ids"]), stringsOf(unit["matched_coverage_unit_ids"])
		f.require(len(sources) > 0 && subset(sources, ev.sources), "REV031", "来源地图必须绑定已登记来源。")
		f.require(subset(coverage, ev.coverage), "REV032", "来源地图引用了未知覆盖单元。")
		mapped = append(mapped, coverage...)
		if unit["importance"] == "core" {
			f.require(unit["assessment"] == "covered" && len(coverage) > 0, "REV033", "核心来源单元没有被完整覆盖。")
		}
	}
	f.require(unique(ids), "REV034", "来源地图ID重复。")
	f.require(subset(ev.coverage, mapped), "REV035", "独立来源地图未映射全部已登记覆盖单元。")
}

func (rules *Rules) Evaluate(r Report) QualityResult {
	result := QualityResult{Report: r.Path, Decision: "blocked", PolicySource: "current"}
	f := findingList{file: r.Path, items: []Finding{}}
	f.require(r.MetadataStatus == "parsed", "META001", "报告元数据必须无歧义地解析。")
	f.require(r.Metadata.String("quality_schema") == currentReportSchema, "QG001", "质量校验需要report-v2。")
	evidencePath, reviewPath := artifactPaths(r.Path)
	evidence, evidenceErr := JSON(rules.source, evidencePath)
	review, reviewErr := JSON(rules.source, reviewPath)
	for _, v := range []struct {
		file, absent, invalid string
		err                   error
	}{{evidencePath, "QG003", "QG004", evidenceErr}, {reviewPath, "QG005", "QG006", reviewErr}} {
		if !rules.source.Has(v.file) {
			f.items = append(f.items, issue(v.file, v.absent, "缺少报告质量产物。"))
		} else if v.err != nil {
			f.items = append(f.items, issue(v.file, v.invalid, "质量产物不是有界、无歧义的JSON对象。"))
		}
	}
	policy := rules.Current
	decision := obj(review["decision"])
	if !isDraft(r) && len(decision) > 0 {
		archived, e := rules.revision(str(decision["policy_id"]))
		f.require(nonempty(decision["policy_id"]) && nonempty(decision["policy_sha256"]), "QG007", "最终判定缺少策略版本引用。")
		f.require(e == nil, "QG016", "最终判定引用的策略归档不可用。")
		if e == nil {
			matches := decision["policy_sha256"] == canonicalDigest(archived)
			f.require(matches, "QG008", "策略归档摘要与最终判定不一致。")
			if matches {
				policy, result.PolicySource = archived, "archive"
			}
		}
	}
	result.PolicyID, result.PolicySHA256 = str(policy["policy_id"]), canonicalDigest(policy)
	f.require(len(obj(nested(policy, "tiers", r.Metadata.String("quality_tier")))) > 0, "QG002", "报告等级缺失或未被该策略定义。")
	ev := evidenceSummary{}
	if evidenceErr == nil {
		var findings []Finding
		findings, ev = rules.checkEvidence(r, evidence, policy)
		f.items = append(f.items, findings...)
	}
	if reviewErr == nil {
		var findings []Finding
		findings, result.ReviewSummary = rules.checkReview(r, review, ev, policy)
		f.items = append(f.items, findings...)
	}
	if !isDraft(r) && reviewErr == nil {
		f.require(len(decision) > 0, "QG011", "已完成报告缺少最终判定。")
		f.require(decision["status"] == "pass", "QG012", "已完成报告的判定不是pass。")
		score, scoreOK := number(decision["score"])
		f.require(scoreOK && result.Score != nil && score == *result.Score, "QG013", "最终分数与复核记录不一致。")
		reportBytes, reportErr := rules.source.Bytes(r.Path, TextLimit)
		evidenceBytes, evErr := rules.source.Bytes(evidencePath, TextLimit)
		rh, eh := digest(reportBytes), digest(evidenceBytes)
		f.require(reportErr == nil && decision["report_sha256"] == rh, "QG014", "报告内容与最终判定摘要不一致。")
		f.require(evErr == nil && decision["evidence_sha256"] == eh, "QG015", "证据账本与最终判定摘要不一致。")
		if raw, exists := review["editorial_update"]; exists {
			editorial := obj(raw)
			content := maps.Clone(review)
			delete(content, "decision")
			delete(content, "editorial_update")
			f.require(editorial["report_sha256"] == rh && editorial["evidence_sha256"] == eh && editorial["review_content_sha256"] == canonicalDigest(content), "QG017", "编辑继承与正文、证据或原复核不一致。")
		}
	}
	result.Findings = f.items
	incomplete := set([]string{"QG003", "QG004", "QG005", "QG006", "REV005", "REV006", "REV014", "REV015", "REV016", "REV017"})
	failure := set([]string{"REV018", "SCORE001", "SCORE002"})
	errors, blocked, failed := false, false, false
	for _, f := range f.items {
		if f.Severity != "error" {
			continue
		}
		errors = true
		failed = failed || failure[f.Code]
		blocked = blocked || !incomplete[f.Code] && !failure[f.Code]
	}
	switch {
	case !errors:
		result.Decision = "pass"
	case blocked:
		result.Decision = "blocked"
	case failed:
		maxRounds, _ := integer(nested(policy, "tiers", r.Metadata.String("quality_tier"), "max_revision_rounds"))
		result.Decision = "revise"
		if result.Revision > maxRounds {
			result.Decision = "escalate"
		}
	default:
		result.Decision = "needs_review"
	}
	return result
}
