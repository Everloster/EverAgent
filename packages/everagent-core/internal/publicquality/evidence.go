package publicquality

import (
	"errors"
	"path"
	"strings"

	jsonschema "github.com/santhosh-tekuri/jsonschema/v6"
)

type evidenceSummary struct {
	requirements, sources, claims, criticalClaims, criticalSources, coverage []string
	generator                                                                Object
}
type findingList struct {
	file  string
	items []Finding
}

func (f *findingList) require(ok bool, code, message string) {
	if !ok {
		f.items = append(f.items, issue(f.file, code, message))
	}
}
func (f *findingList) warn(code, message string) {
	f.items = append(f.items, warning(f.file, code, message))
}
func schemaFindings(file, code string, schema *jsonschema.Schema, v Object) []Finding {
	e := schema.Validate(v)
	if e == nil {
		return nil
	}
	var failure *jsonschema.ValidationError
	if !errors.As(e, &failure) {
		return []Finding{issue(file, code, "无法完成Schema核验。")}
	}
	out := []Finding{}
	units := failure.BasicOutput().Errors
	for _, u := range units[:min(20, len(units))] {
		out = append(out, issue(file, code, "Schema不匹配："+u.InstanceLocation+" ["+u.KeywordLocation+"]"))
	}
	if len(out) == 0 {
		out = append(out, issue(file, code, "产物不符合现行Schema。"))
	}
	return out
}
func requiredFields(f *findingList, m Object, code string, fields ...string) {
	for _, field := range fields {
		f.require(nonempty(m[field]), code, "缺少非空字段："+field)
	}
}
func sourceMapRequired(r Report) bool {
	return r.Domain == "podcast-learning" && containsString([]string{"standard", "deep"}, r.Metadata.String("report_depth"))
}
func chapters(r Report) int {
	if strings.ToLower(r.Metadata.String("source_shownotes_chapters")) != "true" {
		return 0
	}
	text := r.Metadata.String("chapters")
	n := 0
	for _, c := range text {
		if c < '0' || c > '9' {
			break
		}
		n = n*10 + int(c-'0')
		if n > 10000 {
			return 10001
		}
	}
	return n
}
func artifactPaths(p string) (string, string) {
	base := path.Join(path.Dir(p), ".quality", strings.TrimSuffix(path.Base(p), ".md"))
	return base + ".evidence.json", base + ".review.json"
}
func artifactReport(p string) string {
	if path.Base(path.Dir(p)) != ".quality" {
		return ""
	}
	for _, suffix := range []string{".evidence.json", ".review.json", ".transcription-review.json"} {
		if strings.HasSuffix(p, suffix) {
			return path.Join(path.Dir(path.Dir(p)), strings.TrimSuffix(path.Base(p), suffix)+".md")
		}
	}
	return ""
}
func (rules *Rules) checkEvidence(r Report, manifest Object, policy Object) ([]Finding, evidenceSummary) {
	file, _ := artifactPaths(r.Path)
	f := findingList{file: file, items: schemaFindings(file, "EVM000", rules.evidence, manifest)}
	summary := evidenceSummary{generator: obj(manifest["generator"])}
	// Schema errors already carry locations. Avoid pretending that malformed
	// arrays or booleans provided any usable coverage evidence.
	if len(f.items) > 0 {
		return f.items, summary
	}
	f.require(manifest["report_path"] == r.Path, "EVM002", "证据账本与报告路径不一致。")
	tier := r.Metadata.String("quality_tier")
	f.require(manifest["quality_tier"] == tier, "EVM003", "证据账本与报告等级不一致。")
	gen := summary.generator
	requiredFields(&f, gen, "EVM005", "model", "harness", "run_id")
	f.items = append(f.items, modelFindings(file, gen, "generator", policy)...)
	task := obj(manifest["task"])
	requiredFields(&f, task, "EVM008", "summary")
	for _, v := range array(task["requirements"]) {
		item := obj(v)
		requiredFields(&f, item, "EVM010", "id", "text")
		summary.requirements = append(summary.requirements, str(item["id"]))
	}
	f.require(unique(summary.requirements), "EVM011", "requirement id重复。")
	primary := 0
	sources := array(manifest["sources"])
	for _, v := range sources {
		source := obj(v)
		requiredFields(&f, source, "EVM014", "id", "kind", "title", "locator", "accessed_on")
		summary.sources = append(summary.sources, str(source["id"]))
		kind := str(source["kind"])
		if containsString([]string{"primary", "official", "local", "execution"}, kind) {
			primary++
		}
		if kind == "local" {
			p := str(source["locator"])
			entry, ok := rules.source.entries[p]
			valid := safePath(p) && ok && (entry.Mode == "100644" || entry.Mode == "100755")
			// A file may be binary; validate its repository binding without
			// imposing the text scanner's size limit on an original document.
			if valid {
				_, e := rules.source.Prefix(p, 1)
				valid = e == nil
			}
			f.require(valid, "EVM035", "本地来源必须是仓内存在的普通文件。")
		}
		f.require(ValidDate(str(source["accessed_on"])), "EVM016", "来源accessed_on不是有效日期。")
	}
	f.require(unique(summary.sources), "EVM017", "source id重复。")
	text, _ := rules.source.Text(r.Path)
	criticalSources := map[string]bool{}
	for _, v := range array(manifest["claims"]) {
		claim := obj(v)
		requiredFields(&f, claim, "EVM020", "id", "claim", "report_anchor", "support")
		id := str(claim["id"])
		summary.claims = append(summary.claims, id)
		anchor := str(claim["report_anchor"])
		f.require(anchor != "" && strings.Contains(text, anchor), "EVM021", "claim的report_anchor未出现在报告中。")
		refs := stringsOf(claim["source_ids"])
		f.require(subset(refs, summary.sources), "EVM024", "claim引用了未知来源。")
		support := str(claim["support"])
		if support == "direct" || support == "derived" {
			f.require(len(refs) > 0, "EVM025", "有依据的claim必须绑定来源。")
			f.require(nonempty(claim["evidence"]), "EVM026", "claim缺少简短证据。")
		}
		if support == "inference" {
			marked := str(claim["claim"]) + anchor
			f.require(strings.Contains(marked, "[推测]") || strings.Contains(marked, "[待验证]"), "EVM027", "推断claim未标明推测或待验证。")
		}
		if claim["critical"] == true {
			summary.criticalClaims = append(summary.criticalClaims, id)
			f.require(len(refs) > 0, "EVM028", "关键claim必须绑定来源。")
			for _, ref := range refs {
				criticalSources[ref] = true
			}
		}
	}
	f.require(unique(summary.claims), "EVM030", "claim id重复。")
	for k := range criticalSources {
		summary.criticalSources = append(summary.criticalSources, k)
	}
	coverage := array(manifest["source_coverage"])
	required := sourceMapRequired(r)
	if required {
		f.require(len(coverage) >= 3, "EVM036", "standard/deep播客至少登记3个来源内容单元。")
	}
	coreCount := 0
	for _, v := range coverage {
		item := obj(v)
		requiredFields(&f, item, "EVM039", "id", "title", "importance", "status")
		summary.coverage = append(summary.coverage, str(item["id"]))
		refs := stringsOf(item["source_ids"])
		f.require(len(refs) > 0, "EVM042", "coverage必须绑定来源。")
		f.require(subset(refs, summary.sources), "EVM043", "coverage引用了未知来源。")
		status := str(item["status"])
		if item["importance"] == "core" {
			coreCount++
			f.require(status == "included", "EVM044", "核心内容单元不得省略。")
		}
		if status == "included" {
			anchor := str(item["report_anchor"])
			f.require(anchor != "" && strings.Contains(text, anchor), "EVM045", "已收录内容单元没有有效的报告锚点。")
		} else {
			f.require(nonempty(item["omission_reason"]), "EVM046", "省略内容需要注明原因。")
		}
	}
	f.require(unique(summary.coverage), "EVM047", "source_coverage id重复。")
	if required {
		f.require(coreCount >= 3, "EVM048", "standard/deep播客至少登记3个核心内容单元。")
		f.require(len(summary.coverage) >= chapters(r), "EVM049", "来源覆盖单元少于声明的shownotes章节数。")
	}
	limits := stringsOf(manifest["limitations"])
	nonblank := false
	for _, limit := range limits {
		if strings.TrimSpace(limit) != "" {
			nonblank = true
		}
	}
	f.require(nonblank, "EVM031", "至少记录一项限制或未确认事项。")
	tierPolicy := obj(nested(policy, "tiers", tier))
	for _, check := range []struct {
		count       int
		field, code string
	}{{len(sources), "minimum_sources", "EVM032"}, {primary, "minimum_primary_sources", "EVM033"}, {len(summary.criticalClaims), "minimum_critical_claims", "EVM034"}} {
		minimum, _ := number(tierPolicy[check.field])
		f.require(float64(check.count) >= minimum, check.code, "来源或关键claim数量低于报告等级门槛。")
	}
	return f.items, summary
}
