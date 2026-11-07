package publicquality

import (
	"path"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

var placeholders = regexp.MustCompile(`(?i:\bTODO\b|\bTBD\b|PLACEHOLDER)|待填写|待补充内容|\{[A-Z][A-Z0-9_]{2,}\}`)
var evidenceMarker = regexp.MustCompile(`(?i)https?://|arxiv[:/. ]\s*\d{4}\.\d{4,5}|doi[:/. ]\s*10\.|\bRFC\s*\d+|\[(?:代码|API|README|Web|原始材料|一手|二手|推测|待验证)\]|(?:Table|Figure|Fig\.|§|p\.)\s*\d+`)
var wikiLink = regexp.MustCompile(`\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]`)

func newReports(c *Candidate) map[string]bool {
	removed := map[string][]string{}
	for _, p := range c.Before.Paths() {
		col, ok := CollectionFor(p)
		if !ok || c.After.Has(p) {
			continue
		}
		b, e := c.Before.Bytes(p, TextLimit)
		if e != nil {
			continue
		}
		key := col.ID + ":" + digest(b)
		removed[key] = append(removed[key], p)
	}
	result := map[string]bool{}
	for _, p := range c.Added {
		col, ok := CollectionFor(p)
		if !ok {
			continue
		}
		result[p] = true
		b, e := c.After.Bytes(p, TextLimit)
		if e != nil {
			continue
		}
		key := col.ID + ":" + digest(b)
		if len(removed[key]) > 0 {
			// One deleted preimage can exempt one exact same-collection move,
			// not several copies or a move across knowledge domains.
			removed[key] = removed[key][1:]
			delete(result, p)
		}
	}
	return result
}

func wikiTargets(s *Snapshot, r Report, target string) []string {
	name := strings.TrimSpace(target)
	for _, ext := range []string{".md", ".txt"} {
		name = strings.TrimSuffix(name, ext)
	}
	if name == "" || name == "..." || name == "…" || strings.Contains(name, "{") {
		return nil
	}
	out := []string{}
	if !strings.Contains(name, "/") {
		for _, p := range s.Paths() {
			if containsString([]string{".md", ".txt"}, path.Ext(p)) && strings.TrimSuffix(path.Base(p), path.Ext(p)) == name {
				out = append(out, p)
			}
		}
	} else {
		for _, base := range []string{".", path.Dir(r.Path), r.Domain, r.Domain + "/wiki"} {
			for _, ext := range []string{"", ".md", ".txt"} {
				p := path.Clean(path.Join(base, name+ext))
				if safePath(p) && s.Has(p) {
					out = append(out, p)
				}
			}
		}
	}
	return out
}

func reportDependencies(s *Snapshot, r Report) map[string]bool {
	out := map[string]bool{}
	text, e := s.Text(r.Path)
	if e != nil {
		return out
	}
	for _, link := range LocalLinks(text) {
		p, _, external, e := localTarget(r.Path, link.Target)
		if e == nil && !external {
			out[p] = true
		}
	}
	ep, rp := artifactPaths(r.Path)
	for _, p := range []string{ep, rp, strings.TrimSuffix(rp, ".review.json") + ".transcription-review.json"} {
		out[p] = true
	}
	if r.Domain == "podcast-learning" {
		for _, key := range transcriptFields {
			p, e := transcriptPath(r.Metadata.String(key))
			if e == nil && p != "" {
				out[p] = true
			}
		}
	}
	if ev, e := JSON(s, ep); e == nil {
		for _, v := range array(ev["sources"]) {
			item := obj(v)
			p := str(item["locator"])
			if item["kind"] == "local" && safePath(p) {
				out[p] = true
			}
		}
	}
	for _, match := range wikiLink.FindAllStringSubmatch(prose(text, true), -1) {
		for _, p := range wikiTargets(s, r, match[1]) {
			out[p] = true
		}
	}
	return out
}

func FullReportAuditRequired(changed []string) bool {
	files := set([]string{"scripts/audit_reports.py", "scripts/report_quality.py", "scripts/report_catalog.py", "scripts/lint_evidence.py", "scripts/precommit_quality.py", "podcast-learning/scripts/audit_transcript.py", ".github/workflows/quality.yml"})
	for _, p := range changed {
		if files[p] || strings.HasPrefix(p, "schemas/report-") || strings.HasPrefix(p, "config/report-quality-") || strings.HasPrefix(p, "packages/everagent-core/internal/publicquality/") || strings.HasPrefix(p, "packages/everagent-core/cmd/ea-quality/") {
			return true
		}
	}
	return false
}
func ContextRequired(changed []string) bool {
	if FullReportAuditRequired(changed) {
		return true
	}
	for _, p := range changed {
		if containsString([]string{"AGENTS.md", "CLAUDE.md", "METHODOLOGY.md", "SKILL.md"}, path.Base(p)) || strings.Contains(p, "/skills/") {
			return true
		}
		for _, prefix := range []string{".agents/", "evals/", "config/instruction-", "docs/REPORT_", "docs/CONTEXT_", "docs/AGENT_", "docs/PROTOCOL_", "docs/HARNESS_"} {
			if p != "docs/REPORT_INDEX.md" && strings.HasPrefix(p, prefix) {
				return true
			}
		}
		if p == "scripts/eval_report_context.py" || p == "scripts/run_ace_context_ab.py" {
			return true
		}
	}
	return false
}
func SamplingRequired(changed []string) bool {
	for _, p := range changed {
		for _, c := range Collections {
			if strings.HasPrefix(p, c.Root+"/") {
				return true
			}
		}
	}
	return false
}

type ReportAudit struct {
	ReportsScanned int       `json:"reports_scanned"`
	Full           bool      `json:"full"`
	Errors         int       `json:"errors"`
	Warnings       int       `json:"warnings"`
	Findings       []Finding `json:"findings"`
}

func AuditReports(c *Candidate, rules *Rules, reports []Report, all bool) ReportAudit {
	out := ReportAudit{Full: all, Findings: []Finding{}}
	changed, newPaths := set(c.Changed), newReports(c)
	for _, p := range c.Changed {
		if strings.HasPrefix(p, policyArchive) && c.Before.Has(p) {
			out.Findings = append(out.Findings, issue(p, "POLICY_IMMUTABLE", "既有策略归档不得修改或删除；请新增policy_id。"))
		}
		if c.After.Has(p) && path.Base(path.Dir(p)) == ".quality" {
			owner := artifactReport(p)
			_, known := CollectionFor(owner)
			if !known || !c.After.Has(owner) {
				out.Findings = append(out.Findings, issue(p, "ORPHAN_QUALITY_ARTIFACT", "质量文件缺少对应报告。"))
			}
		}
	}
	covered, sourcePaths, enforced := map[string]bool{}, map[string]bool{}, map[string]bool{}
	titles := map[string][]string{}
	for _, r := range reports {
		deps := reportDependencies(c.After, r)
		affected := changed[r.Path]
		for p := range deps {
			affected = affected || changed[p]
		}
		// A deleted wiki target is absent from the after index; use the same
		// safe reference resolver against the immutable before snapshot too.
		if !affected && len(c.Changed) > 0 {
			for p := range reportDependencies(c.Before, r) {
				affected = affected || changed[p]
			}
		}
		if !all && !affected {
			continue
		}
		out.ReportsScanned++
		for p := range deps {
			if strings.HasSuffix(p, ".transcript.txt") {
				sourcePaths[p] = true
				if affected {
					enforced[p] = true
				}
			}
		}
		if r.Domain == "podcast-learning" {
			if p, e := transcriptPath(r.Metadata.String("transcript_path")); e == nil && p != "" {
				covered[p] = true
			}
		}
		out.Findings = append(out.Findings, auditReport(c.After, rules, r, newPaths[r.Path], changed[r.Path], affected)...)
		titles[r.Title] = append(titles[r.Title], r.Path)
	}
	for p := range changed {
		if strings.HasSuffix(p, ".transcript.txt") {
			sourcePaths[p] = true
			enforced[p] = true
		}
	}
	for _, p := range sortedBoolKeys(sourcePaths) {
		if covered[p] {
			continue
		}
		if !c.After.Has(p) && !sourcePathsReferenced(c.After, reports, p) {
			continue
		}
		b, e := c.After.Bytes(p, TextLimit)
		var issues []Finding
		if e != nil {
			issues = []Finding{issue(p, "POD101", "被引用的转写来源不可读。")}
		} else {
			issues = AuditTranscript(b, p).Findings
		}
		for _, f := range issues {
			if !enforced[p] && f.Severity == "error" {
				f.Severity = "warning"
			}
			out.Findings = append(out.Findings, f)
		}
	}
	for _, title := range keysStringLists(titles) {
		if len(titles[title]) > 1 {
			for _, p := range titles[title] {
				out.Findings = append(out.Findings, warning(p, "CAT001", "所检查报告存在同名标题。"))
			}
		}
	}
	for _, f := range out.Findings {
		if f.Severity == "error" {
			out.Errors++
		} else if f.Severity == "warning" {
			out.Warnings++
		}
	}
	return out
}
func sourcePathsReferenced(s *Snapshot, reports []Report, p string) bool {
	for _, r := range reports {
		if reportDependencies(s, r)[p] {
			return true
		}
	}
	return false
}
func sortedBoolKeys(m map[string]bool) []string {
	out := []string{}
	for k := range m {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

func auditReport(s *Snapshot, rules *Rules, r Report, isNew, reportChanged, affected bool) []Finding {
	f := findingList{file: r.Path, items: []Finding{}}
	text, e := s.Text(r.Path)
	if e != nil {
		return []Finding{issue(r.Path, "REPORT_UNREADABLE", "报告无法完整读取。")}
	}
	schema := r.Metadata.String("quality_schema")
	versioned := schema == "report-v1" || schema == currentReportSchema
	enforce := isNew || versioned
	check := func(ok bool, code, message string, strict bool) {
		if ok {
			return
		}
		finding := issue(r.Path, code, message)
		if !strict {
			finding.Severity = "warning"
		}
		f.items = append(f.items, finding)
	}
	check(r.MetadataStatus == "parsed", "META001", "元数据无法无歧义解析。", enforce || affected)
	check(strings.HasPrefix(text, "---\n") || strings.HasPrefix(text, "---\r\n"), "META001", "缺少frontmatter。", enforce)
	for _, key := range []string{"title", "domain", "report_type", "status", "updated_on"} {
		check(truth(r.Metadata[key]), "META002", "缺少元数据字段："+key, enforce)
	}
	check(r.Metadata.String("domain") == "" || r.Metadata.String("domain") == r.Domain, "META003", "报告domain与实际目录不一致。", enforce)
	date := r.Metadata.String("updated_on")
	check(date == "" || ValidDate(date), "META004", "updated_on不是有效日期。", enforce)
	status := r.Metadata.String("status")
	// Display aliases are not permission to weaken a versioned report contract.
	status = r.RawMetadata.String("status")
	check(status == "" || containsString([]string{"completed", "in_progress", "planned", "archived", "cached", "superseded", "degraded_shownotes_only"}, status), "META005", "报告status不符合规范。", enforce)
	check(schema == "" || versioned, "META006", "报告使用未知quality_schema。", enforce)
	check(!isNew || schema == currentReportSchema, "META006", "新报告必须使用report-v2。", true)
	_, hasTags := r.Metadata["semantic_tags"]
	check(hasTags, "META007", "缺少semantic_tags。", enforce)
	check(!isNew || !isDraft(r), "META009", "新报告必须复核并finalize，不能提交草稿。", true)
	if schema == currentReportSchema {
		for _, key := range []string{"status", "report_type"} {
			// A source or shared owner edit must recheck its dependents, not
			// require unrelated historical metadata to be rewritten. New or
			// directly edited reports still use canonical metadata values.
			check(r.RawMetadata.String(key) == r.Metadata.String(key), "META010", "report-v2需使用规范元数据值："+key, isNew || reportChanged)
		}
	}
	check(titleLine.MatchString(text), "STRUCT001", "缺少H1标题。", enforce)
	if len(text) < 2000 {
		f.warn("STRUCT002", "正文短于2000 bytes，需确认不是未完成稿。")
	}
	check(isDraft(r) || !placeholders.MatchString(prose(text, true)), "STRUCT003", "已完成报告仍有正文占位符。", enforce)
	check(isDraft(r) || evidenceMarker.MatchString(text), "EVID001", "已完成报告没有可识别证据锚点。", enforce)
	if enforce && r.Domain == "github-trending-analyzer" && strings.HasPrefix(path.Base(r.Path), "research_") {
		for _, marker := range []string{"[API]", "[代码]"} {
			check(strings.Contains(text, marker), "REPO001", "仓库深研缺少证据标记："+marker, true)
		}
	}
	if enforce && r.Domain == "podcast-learning" {
		depth := r.Metadata.String("report_depth")
		needed := isNew && ValidDate(date) && date >= "2026-10-20"
		check(!needed || depth != "", "POD002", "新播客缺少report_depth。", true)
		check(depth == "" || containsString([]string{"brief", "standard", "deep"}, depth), "POD002", "未知report_depth。", true)
		check(!(needed || depth != "") || r.Metadata.String("reader_contract") == "standalone", "POD003", "播客需要standalone阅读契约。", true)
		if sourceMapRequired(r) {
			duration, _ := strconv.Atoi(r.Metadata.String("duration_seconds"))
			if duration >= 3600 && hanzi(text) < 3500 {
				f.warn("POD006", "长音频报告字数较少；需人工检查核心内容召回。")
			}
		}
	}
	if r.Domain == "podcast-learning" {
		for _, finding := range checkPodcast(s, r, text) {
			if finding.Severity == "error" && !affected && !isNew {
				finding.Severity = "warning"
			}
			f.items = append(f.items, finding)
		}
	}
	for _, link := range LocalLinks(text) {
		p, _, external, e := localTarget(r.Path, link.Target)
		if external {
			continue
		}
		if !containsString([]string{".md", ".txt", ".json", ".csv", ".py", ".sh", ".go"}, strings.ToLower(path.Ext(p))) && e == nil {
			continue
		}
		row, exists := s.entries[p]
		check(e == nil && exists && (row.Mode == "100644" || row.Mode == "100755"), "LINK001", "相对链接不指向仓内普通文件。", enforce || affected)
	}
	for _, m := range wikiLink.FindAllStringSubmatch(prose(text, true), -1) {
		target := strings.TrimSpace(m[1])
		stem := strings.TrimSuffix(path.Base(target), path.Ext(target))
		if stem == "..." || stem == "…" || strings.Contains(target, "{") {
			continue
		}
		check(len(wikiTargets(s, r, target)) > 0, "LINK002", "wikilink目标不存在或限定路径不匹配。", isNew || affected || enforce && len(wikiTargets(s, r, stem)) == 0)
	}
	f.items = append(f.items, lintEvidence(r.Path, text)...)
	if schema == currentReportSchema && !isDraft(r) {
		f.items = append(f.items, rules.Evaluate(r).Findings...)
	} else if schema == currentReportSchema {
		check(r.Metadata.String("quality_tier") != "", "QG002", "report-v2草稿缺少quality_tier。", enforce)
	}
	return f.items
}

var preciseNumbers = regexp.MustCompile(`\d+\.\d+|%|[nN]\s*=\s*\d+|Table\s+\d|Figure\s+\d|Fig\.\s*\d|p\s*[<=>]\s*0?\.\d+`)
var verifiableCitation = regexp.MustCompile(`(?i)https?://\S+|arxiv[:/]\s*\d{4}\.\d{4,5}|arxiv\.org/abs/|doi[:\s]\s*10\.\d{4,9}/|doi\.org/10\.|\bRFC\s?\d{3,5}\b`)
var recentYear = regexp.MustCompile(`202[4-9]`)
var passageCitation = regexp.MustCompile(`[a-z]+\d+[a-e]?|Ch\.\s*\d+|§\s*\d+|p\.\s*\d+|》|“|"`)

func lintEvidence(file, text string) []Finding {
	out := []Finding{}
	warn := func(msg string) { out = append(out, warning(file, "EVID900", msg)) }
	fuzzy := 0
	for _, phrase := range []string{"显著提升", "显著提高", "显著改善", "大幅提升", "大幅提高", "大幅改善", "研究表明", "实验证明", "结果显示", "多家博客", "有报告称", "显著差异"} {
		fuzzy += strings.Count(text, phrase)
	}
	numbers, cites := len(preciseNumbers.FindAllString(text, -1)), len(verifiableCitation.FindAllString(text, -1))
	switch {
	case strings.Contains(file, "paper_analyses"):
		if numbers < 2 {
			warn("论文分析缺少精确数字。")
		}
		if fuzzy > 3 && numbers < 5 {
			warn("模糊提升表述较多，缺少对应数字。")
		}
	case strings.Contains(file, "knowledge_reports") || strings.Contains(file, "concept_reports"):
		if recentYear.MatchString(text) && cites == 0 {
			warn("涉及近期事实但未发现可核验引用。")
		}
		marked := false
		for _, m := range []string{"[推测]", "[待验证]", "[未验证]", "[动物实验]", "[体外实验]", "[初步]"} {
			marked = marked || strings.Contains(text, m)
		}
		if fuzzy > 5 && cites == 0 && !marked {
			warn("无来源的模糊表述较多，且未标明推测。")
		}
	case strings.Contains(file, "text_analyses"):
		if len(passageCitation.FindAllString(text, -1)) < 4 {
			warn("文本分析的页码、章节或直接引用较少。")
		}
	}
	return out
}
