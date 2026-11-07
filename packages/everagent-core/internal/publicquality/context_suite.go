package publicquality

func auditSuites(s *Snapshot, rules *Rules, reports []Report, out *ContextAudit) []Finding {
	f := findingList{file: "evals/ace-report-tasks.json", items: []Finding{}}
	suite, e := JSON(s, f.file)
	if e != nil {
		return []Finding{issue(f.file, "CONTEXT_CASES", "ACE任务集不可读。")}
	}
	cases := array(suite["cases"])
	out.Cases = len(cases)
	f.require(len(cases) > 0, "CONTEXT_CASES", "ACE任务集不能为空。")
	routes := map[string]bool{"root": true}
	for _, c := range Collections {
		routes[c.ID] = true
	}
	ids := []string{}
	for _, raw := range cases {
		item := obj(raw)
		id := str(item["id"])
		ids = append(ids, id)
		for _, field := range []string{"id", "prompt", "expected_route", "artifact_policy", "max_initial_project_files", "quality_tier", "required_checks", "expected_skill_paths", "forbidden_skill_paths", "completion_signals", "expected_completed", "expected_stop_reason"} {
			_, exists := item[field]
			f.require(exists, "CONTEXT_CASE_FIELDS", "ACE用例缺字段："+id+"/"+field)
		}
		f.require(nonempty(id) && nonempty(item["prompt"]) && routes[str(item["expected_route"])], "CONTEXT_CASE_ROUTE", "ACE用例缺id、prompt或有效route。")
		for _, field := range []string{"expected_skill_paths", "forbidden_skill_paths", "artifact_expected_skill_paths", "expected_initial_files", "required_checks", "artifact_required_checks", "completion_signals"} {
			value, exists := item[field]
			if !exists { // Required fields are checked above; optional constraints may be absent.
				continue
			}
			values, valid := value.([]any)
			for _, value := range values {
				text, ok := value.(string)
				valid = valid && ok && nonempty(text)
			}
			f.require(valid, "CONTEXT_CASE_FIELDS", "ACE用例约束须为字符串数组："+id+"/"+field)
		}
		expected, forbidden := stringsOf(item["expected_skill_paths"]), set(stringsOf(item["forbidden_skill_paths"]))
		for _, p := range expected {
			f.require(!forbidden[p], "CONTEXT_CASE_CONFLICT", "ACE用例的skill正负样本重叠："+id)
		}
		for _, field := range []string{"expected_skill_paths", "forbidden_skill_paths", "artifact_expected_skill_paths", "expected_initial_files"} {
			for _, p := range stringsOf(item[field]) {
				_, e := s.Bytes(p, TextLimit)
				f.require(e == nil, "CONTEXT_CASE_PATH", "ACE用例引用不可读文件："+id+"/"+p)
			}
		}
		f.require(len(array(item["completion_signals"])) > 0, "CONTEXT_CASE_COMPLETION", "ACE用例缺完成条件："+id)
		f.require(!(item["must_pause_before_research"] == true && item["must_not_pause_before_research"] == true), "CONTEXT_CASE_CONFLICT", "ACE用例同时要求暂停与继续："+id)
		requiresQuality := contains(item["required_checks"], "quality_gate") || contains(item["artifact_required_checks"], "quality_gate")
		_, knownTier := obj(rules.Current["tiers"])[str(item["quality_tier"])]
		f.require(!requiresQuality || knownTier, "CONTEXT_CASE_TIER", "ACE用例的质量等级无效："+id)
		f.require(requiresQuality || item["quality_tier"] == nil, "CONTEXT_CASE_TIER", "ACE用例声明等级却不要求质量检查："+id)
	}
	f.require(unique(ids), "CONTEXT_CASE_IDS", "ACE用例id重复。")
	anchors, e := JSON(s, "evals/report-quality-anchors.json")
	f.require(e == nil, "CONTEXT_ANCHORS", "报告质量锚点不可读。")
	anchorIDs := []string{}
	for _, raw := range array(anchors["anchors"]) {
		item := obj(raw)
		anchorIDs = append(anchorIDs, str(item["id"]))
		_, e := s.Bytes(str(item["report_path"]), TextLimit)
		f.require(nonempty(item["id"]) && e == nil, "CONTEXT_ANCHORS", "质量锚点需有id与可读报告。")
	}
	f.require(unique(anchorIDs), "CONTEXT_ANCHORS", "质量锚点id重复。")
	for _, raw := range cases {
		item := obj(raw)
		id := str(item["reference_anchor"])
		f.require(id == "" || containsString(anchorIDs, id), "CONTEXT_ANCHORS", "ACE用例引用未知质量锚点。")
	}
	f.file = "evals/report-quality-replays.json"
	replays, e := JSON(s, f.file)
	v, valid := integer(replays["schema_version"])
	replayCases := array(replays["cases"])
	f.require(e == nil && valid && v == 1 && len(replayCases) > 0, "CONTEXT_REPLAYS", "已有报告回放集须是非空v1对象。")
	byPath := map[string]Report{}
	for _, r := range reports {
		byPath[r.Path] = r
	}
	replayIDs := []string{}
	for _, raw := range replayCases {
		item := obj(raw)
		id := str(item["id"])
		replayIDs = append(replayIDs, id)
		r, ok := byPath[str(item["report_path"])]
		f.require(nonempty(id) && ok, "CONTEXT_REPLAY_TARGET", "已有报告回放缺id或报告："+id)
		if !ok {
			continue
		}
		out.ReportReplays++
		result := rules.Evaluate(r)
		f.require(result.Decision == "pass", "CONTEXT_REPLAY_QUALITY", "已登记报告质量/快照复验未通过："+id)
		if result.Decision != "pass" {
			f.items = append(f.items, result.Findings...)
		}
		f.require(r.RawMetadata.String("quality_tier") == str(item["quality_tier"]) && r.RawMetadata.String("status") == str(item["status"]), "CONTEXT_REPLAY_METADATA", "已有报告回放元数据漂移："+id)
		minimum, ok := number(item["minimum_score"])
		f.require(ok && result.Score != nil && *result.Score >= minimum, "CONTEXT_REPLAY_SCORE", "已有报告回放分数不满足下限："+id)
	}
	f.require(unique(replayIDs), "CONTEXT_REPLAYS", "已有报告回放id重复。")
	return f.items
}

func historicalBehavior(s *Snapshot, p string, out *ContextAudit) []Finding {
	record, e := JSON(s, p)
	if e != nil {
		out.HistoricalBehaviorStatus = "unreadable"
		return []Finding{issue(p, "CONTEXT_BEHAVIOR_RECORD", "历史行为回放记录不可读；未执行新回放。")}
	}
	v, ok := integer(record["schema_version"])
	if !ok || v != 1 {
		out.HistoricalBehaviorStatus = "invalid-schema"
		return []Finding{issue(p, "CONTEXT_BEHAVIOR_RECORD", "历史行为回放schema无效。")}
	}
	repetitions, _ := integer(record["repetitions"])
	switch {
	case nested(record, "comparison", "accepted") != true:
		out.HistoricalBehaviorStatus = "unaccepted"
	case repetitions < 3:
		out.HistoricalBehaviorStatus = "insufficient-repetitions"
	case nested(record, "refs", "candidate", "context_sha256") != out.BehaviorContextSHA256:
		out.HistoricalBehaviorStatus = "context-changed"
	default:
		out.HistoricalBehaviorStatus = "current-record"
		for _, label := range []string{"baseline", "candidate"} {
			runs, _ := integer(nested(record, "summaries", label, "runs"))
			passed, _ := integer(nested(record, "summaries", label, "successful_runs"))
			if runs != out.Cases*repetitions || passed != runs {
				out.HistoricalBehaviorStatus = "incomplete"
			}
		}
	}
	if out.HistoricalBehaviorStatus != "current-record" {
		return []Finding{warning(p, "CONTEXT_BEHAVIOR_NOT_CURRENT", "历史回放不能证明本次架构改进；里程碑验收需按现行context重新回放。")}
	}
	return nil
}
