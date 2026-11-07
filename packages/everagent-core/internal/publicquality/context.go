package publicquality

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"path"
	"regexp"
	"strings"
	"unicode/utf8"

	"go.yaml.in/yaml/v3"
)

const instructionPolicy = "config/instruction-policy.json"
const reportSkill = ".agents/skills/everagent-report/SKILL.md"

type ContextAudit struct {
	Files                    int       `json:"active_context_files"`
	AgentFiles               int       `json:"agents_files"`
	DiscoverableSkills       int       `json:"discoverable_skill_count"`
	Cases                    int       `json:"ace_cases"`
	ReportReplays            int       `json:"recorded_report_replays"`
	BehaviorContextSHA256    string    `json:"behavior_context_sha256"`
	HistoricalBehaviorStatus string    `json:"historical_behavior_status"`
	BehaviorReplayExecuted   bool      `json:"behavioral_replay_executed"`
	Findings                 []Finding `json:"findings"`
}

func agentFile(p string) bool {
	return p == "AGENTS.md" || path.Base(p) == "AGENTS.md" && strings.Count(p, "/") == 1
}
func domainSkill(p string) bool {
	for _, c := range Collections {
		if strings.HasPrefix(p, c.ID+"/skills/") {
			return true
		}
	}
	return false
}
func behaviorInput(p string) bool {
	parts := strings.SplitN(p, "/", 3)
	projectSkill := len(parts) == 3 && parts[1] == "skills"
	return agentFile(p) || p == "CLAUDE.md" || p == "evals/ace-report-tasks.json" ||
		path.Base(p) == "SKILL.md" && (strings.HasPrefix(p, ".agents/skills/") || projectSkill)
}
func contextPaths(s *Snapshot) []string {
	selected := set([]string{"AGENTS.md", "CLAUDE.md", reportSkill, "METHODOLOGY.md", "docs/REPORT_WORKFLOW.md",
		"docs/CONTEXT_ENGINEERING.md", "docs/PROTOCOL_COMMON.md", "docs/REPORT_METADATA.md", "docs/REPORT_QUALITY_GATE.md", instructionPolicy})
	for _, p := range s.Paths() {
		if agentFile(p) || domainSkill(p) && (path.Base(p) == "SKILL.md" || path.Base(path.Dir(p)) == "references" && path.Ext(p) == ".md") {
			selected[p] = true
		}
	}
	return sortedBoolKeys(selected)
}

var managedPolicy = regexp.MustCompile(`(?s)<!-- BEGIN MANAGED EACLI TOKEN PLAN POLICY -->.*?<!-- END MANAGED EACLI TOKEN PLAN POLICY -->`)
var paragraphBreak = regexp.MustCompile(`\n\s*\n`)
var unconditionalRead = regexp.MustCompile(`每次.*(?:先)?读|开始任何工作前.*读|默认通读|必须.*通读`)
var excludesFullRead = regexp.MustCompile(`不(?:要|得).*通读|禁止.*通读`)
var triggerPositive = regexp.MustCompile(`(?i)\b(?:use|when)\b|用于|适用`)
var triggerNegative = regexp.MustCompile(`(?i)\b(?:skip|exclude|except|not)\b|不用于|不适用|跳过`)

// AuditContext checks the current public owners and recorded fixtures. It does
// not run agents or promote an old successful A/B record to a new experiment.
func AuditContext(s *Snapshot, rules *Rules, reports []Report) ContextAudit {
	out := ContextAudit{HistoricalBehaviorStatus: "unknown", Findings: []Finding{}}
	f := findingList{file: instructionPolicy, items: []Finding{}}
	policy, e := JSON(s, instructionPolicy)
	if e != nil {
		out.Findings = append(out.Findings, issue(instructionPolicy, "CONTEXT_POLICY", "指令策略不可读。"))
		return out
	}
	v, ok := integer(policy["schema_version"])
	f.require(ok && v == 1, "CONTEXT_POLICY", "指令策略schema_version必须为1。")
	for _, owner := range keys(obj(policy["owners"])) {
		p := str(nested(policy, "owners", owner))
		_, e := s.Bytes(p, TextLimit)
		f.require(e == nil, "CONTEXT_OWNER", "指令owner必须是仓内可读普通文件："+owner)
	}
	for _, raw := range array(policy["basis"]) {
		f.require(strings.HasPrefix(str(obj(raw)["url"]), "https://developers.openai.com/"), "CONTEXT_BASIS", "指令策略依据不是登记的官方开发者文档。")
	}
	budgets := obj(policy["budgets"])
	budget := func(key string) int {
		n, valid := integer(budgets[key])
		f.require(valid && n > 0, "CONTEXT_BUDGET", "指令预算需为正整数："+key)
		return n
	}
	rootWarn, rootMax := budget("root_repo_owned_bytes_warn"), budget("root_repo_owned_bytes_max")
	domainMax, bridgeMax := budget("domain_agents_bytes_max"), budget("claude_bridge_bytes_max")
	skillMax, descMax := budget("discoverable_skill_count_max"), budget("discoverable_skill_description_chars_max")
	entryMax, playbookWarn := budget("discoverable_skill_entrypoint_bytes_max"), budget("on_demand_playbook_entrypoint_bytes_warn")
	texts := map[string]string{}
	sizes := map[string]int{}
	for _, p := range contextPaths(s) {
		text, e := s.Text(p)
		if e != nil {
			out.Findings = append(out.Findings, issue(p, "CONTEXT_UNREADABLE", "现行context不可读。"))
			continue
		}
		texts[p] = text
		bytes, _ := s.Bytes(p, TextLimit) // Same captured bytes; Text strips only a UTF-8 BOM.
		sizes[p] = len(bytes)
		out.Files++
		out.Findings = append(out.Findings, CheckLinks(s, p, true)...)
		for _, stale := range []string{"贴一个 GitHub repo 链接即可触发", "每次研究完顺手做一次事C", "每批任务结束，若发现新问题/新解法，把一行改进写进", "禁止修改 SKILL.md / 脚本 / README", "WebFetch", "WebSearch", "每次上网前先读"} {
			if strings.Contains(text, stale) {
				out.Findings = append(out.Findings, issue(p, "CONTEXT_STALE_DIRECTIVE", "存在已退役指令："+stale))
			}
		}
	}
	root := managedPolicy.ReplaceAllString(texts["AGENTS.md"], "")
	rootBytes, _ := s.Bytes("AGENTS.md", TextLimit)
	rootSize := len(managedPolicy.ReplaceAll(rootBytes, nil))
	if rootSize > rootWarn {
		out.Findings = append(out.Findings, warning("AGENTS.md", "CONTEXT_SIZE", "根协议超过软预算。"))
	}
	f.require(rootSize <= rootMax, "CONTEXT_SIZE", "根协议自有内容超过预算。")
	checkSnippets := func(p, text, field string, insensitive bool) {
		for _, snippet := range stringsOf(policy[field]) {
			value := snippet
			if insensitive {
				value = strings.ToLower(value)
			}
			if strings.Contains(text, value) {
				out.Findings = append(out.Findings, issue(p, "CONTEXT_OWNER_DUPLICATION", "出现应由按需owner维护的规则或模型补丁："+snippet))
			}
		}
	}
	checkSnippets("AGENTS.md", root, "root_forbidden_snippets", false)
	duplicates := map[string]map[string]bool{}
	for _, p := range s.Paths() {
		if !agentFile(p) {
			continue
		}
		out.AgentFiles++
		text := texts[p]
		common := text
		chain := sizes["AGENTS.md"]
		if p == "AGENTS.md" {
			common = root
		} else {
			chain += sizes[p]
			if sizes[p] > domainMax {
				out.Findings = append(out.Findings, issue(p, "CONTEXT_SIZE", "领域AGENTS超过预算。"))
			}
			checkSnippets(p, text, "domain_agents_forbidden_snippets", false)
		}
		if chain > 32*1024 {
			out.Findings = append(out.Findings, issue(p, "CONTEXT_CHAIN_SIZE", "AGENTS加载链超过32KiB。"))
		} else if chain >= 24*1024 {
			out.Findings = append(out.Findings, warning(p, "CONTEXT_CHAIN_SIZE", "AGENTS加载链达到32KiB的75%。"))
		}
		checkSnippets(p, strings.ToLower(common), "common_context_forbidden_model_tokens", true)
		for _, block := range paragraphBreak.Split(text, -1) {
			normal := strings.Join(strings.Fields(block), " ")
			if utf8.RuneCountInString(normal) < 120 || strings.HasPrefix(normal, "<!-- BEGIN MANAGED") {
				continue
			}
			key := digest([]byte(normal))
			if duplicates[key] == nil {
				duplicates[key] = map[string]bool{}
			}
			duplicates[key][p] = true
		}
		for n, line := range strings.Split(text, "\n") {
			if unconditionalRead.MatchString(line) && !excludesFullRead.MatchString(line) {
				finding := warning(p, "CONTEXT_UNCONDITIONAL_READ", "规则可能要求不必要的全量读取。")
				finding.Line = n + 1
				out.Findings = append(out.Findings, finding)
			}
		}
	}
	for _, paths := range duplicates {
		if len(paths) > 1 {
			out.Findings = append(out.Findings, warning("AGENTS.md", "CONTEXT_DUPLICATION", "多个协议含相同长段落："+strings.Join(sortedBoolKeys(paths), ", ")))
		}
	}
	for _, p := range stringsOf(policy["model_neutral_owner_files"]) {
		text, e := s.Text(p)
		f.require(e == nil, "CONTEXT_OWNER", "模型中立owner不可读。")
		checkSnippets(p, strings.ToLower(text), "model_neutral_forbidden_model_tokens", true)
	}
	bridge := texts["CLAUDE.md"]
	f.require(strings.Count(bridge, "@AGENTS.md") == 1 && sizes["CLAUDE.md"] <= bridgeMax, "CONTEXT_BRIDGE", "CLAUDE.md须仅导入一次AGENTS且符合预算。")
	checkSnippets("CLAUDE.md", bridge, "claude_forbidden_snippets", false)
	for _, p := range s.Paths() {
		if path.Base(p) != "SKILL.md" {
			continue
		}
		discoverable := strings.HasPrefix(p, ".agents/skills/") && strings.Count(p, "/") == 3
		if !discoverable && !domainSkill(p) {
			continue
		}
		text, e := s.Text(p)
		if e != nil {
			out.Findings = append(out.Findings, issue(p, "CONTEXT_SKILL", "skill不可读。"))
			continue
		}
		bytes, _ := s.Bytes(p, TextLimit)
		if !discoverable {
			if len(bytes) > playbookWarn {
				out.Findings = append(out.Findings, warning(p, "CONTEXT_SKILL_SIZE", "按需playbook超过软预算。"))
			}
			continue
		}
		out.DiscoverableSkills++
		meta, e := ParseFrontmatter(text)
		desc := meta.String("description")
		if e != nil || !nonempty(meta["name"]) || !nonempty(desc) || p == reportSkill && meta.String("name") != "everagent-report" {
			out.Findings = append(out.Findings, issue(p, "CONTEXT_SKILL", "自动发现skill缺少有效name/description。"))
		}
		if utf8.RuneCountInString(desc) > descMax || len(bytes) > entryMax {
			out.Findings = append(out.Findings, issue(p, "CONTEXT_SKILL_SIZE", "自动发现skill超过描述或入口预算。"))
		}
		if !triggerPositive.MatchString(desc) || !triggerNegative.MatchString(desc) {
			out.Findings = append(out.Findings, warning(p, "CONTEXT_SKILL_TRIGGER", "skill描述需明确触发与非触发边界。"))
		}
	}
	f.require(out.DiscoverableSkills <= skillMax, "CONTEXT_SKILL_COUNT", "自动发现skill数量超过预算。")
	out.Findings = append(out.Findings, f.items...)
	out.Findings = append(out.Findings, checkPublicBindings(s)...)
	out.Findings = append(out.Findings, auditSuites(s, rules, reports, &out)...)
	h := sha256.New()
	for _, p := range s.Paths() {
		if !behaviorInput(p) {
			continue
		}
		b, e := s.Bytes(p, TextLimit)
		if e != nil {
			out.Findings = append(out.Findings, issue(p, "CONTEXT_FINGERPRINT", "行为context指纹输入不可读。"))
			continue
		}
		fmt.Fprintf(h, "%s\x00", p)
		h.Write(b)
		h.Write([]byte{0})
	}
	out.BehaviorContextSHA256 = hex.EncodeToString(h.Sum(nil))
	out.Findings = append(out.Findings, historicalBehavior(s, str(nested(policy, "owners", "ace_context_ab_result")), &out)...)
	out.Findings = append(out.Findings, rules.Sampling(reports).Findings...)
	return out
}

func checkPublicBindings(s *Snapshot) []Finding {
	f := findingList{file: "scripts/ecommit.sh", items: []Finding{}}
	wrapper, _ := s.Text(f.file)
	engine, _ := s.Text("packages/everagent-core/cmd/ea-git/main.go")
	f.require(strings.Contains(wrapper, "./cmd/ea-git") && strings.Contains(engine, "core.Commit(") && strings.Contains(engine, "publicquality.Check("), "CONTEXT_COMMIT_BINDING", "提交入口须绑定共享Go core与同一公开质量门。")
	workflowPath := ".github/workflows/quality.yml"
	text, e := s.Text(workflowPath)
	var workflow map[string]any
	if e != nil || yaml.Unmarshal([]byte(text), &workflow) != nil {
		return append(f.items, issue(workflowPath, "CONTEXT_CI", "CI定义不可读。"))
	}
	runs := []string{}
	for _, job := range obj(workflow["jobs"]) {
		row := obj(job)
		if row["if"] != nil || row["continue-on-error"] != nil && row["continue-on-error"] != false {
			continue
		}
		for _, step := range array(row["steps"]) {
			step := obj(step)
			if step["if"] != nil || step["continue-on-error"] != nil && step["continue-on-error"] != false {
				continue
			}
			run := strings.ReplaceAll(str(step["run"]), "\\\r\n", " ")
			runs = append(runs, strings.ReplaceAll(run, "\\\n", " "))
		}
	}
	commands := strings.Join(runs, "\n")
	// A static wiring check, not proof that GitHub ran it. Require real,
	// mandatory command lines, not a comment/echo or a best-effort step.
	for _, check := range []struct{ label, pattern string }{
		{"Go test ./...", `(?m)^\s*go[ \t]+-C[ \t]+packages/everagent-core[ \t]+test[ \t]+(?:-(?:mod=readonly|count=1|timeout=[1-9][0-9]*[smh]|race|v)[ \t]+)*\./\.\.\.[ \t]*$`},
		{"Go vet ./...", `(?m)^\s*go[ \t]+-C[ \t]+packages/everagent-core[ \t]+vet[ \t]+(?:-(?:mod=readonly|v)[ \t]+)*\./\.\.\.[ \t]*$`},
		{"Go head gate", `(?m)^\s*go[ \t]+-C[ \t]+packages/everagent-core[ \t]+run[ \t]+(?:-(?:mod=readonly|trimpath|buildvcs=false)[ \t]+)*\./cmd/ea-quality[ \t]+quick[ \t]+--scope[ \t]+head[ \t]+--base[ \t]+[^\n;&|]+$`},
	} {
		if !regexp.MustCompile(check.pattern).MatchString(commands) {
			f.items = append(f.items, issue(workflowPath, "CONTEXT_CI", "CI缺少必需Go检查："+check.label))
		}
	}
	return f.items
}
