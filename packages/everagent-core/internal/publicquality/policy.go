package publicquality

import (
	"errors"
	"maps"
	"regexp"
	"sort"
	"strings"

	jsonschema "github.com/santhosh-tekuri/jsonschema/v6"
)

const policyPath = "config/report-quality-policy.json"
const policyArchive = "config/report-quality-policies/"
const evidenceSchemaPath = "schemas/report-evidence-v1.schema.json"
const reviewSchemaPath = "schemas/report-review-v1.schema.json"
const currentReportSchema = "report-v2"

var policyID = regexp.MustCompile(`^[a-z0-9][a-z0-9._-]*$`)

type offlineSchemas struct{}

func (offlineSchemas) Load(string) (any, error) {
	return nil, errors.New("external-schema-loading-disabled")
}

type Rules struct {
	source                 *Snapshot
	Current                Object
	evidence, review       *jsonschema.Schema
	evidenceDoc, reviewDoc Object
	revisions              map[string]Object
}

func LoadRules(s *Snapshot) (*Rules, error) {
	r := &Rules{source: s, revisions: map[string]Object{}}
	var e error
	r.evidenceDoc, e = JSON(s, evidenceSchemaPath)
	if e != nil {
		return nil, errors.New("evidence-schema-unreadable")
	}
	r.reviewDoc, e = JSON(s, reviewSchemaPath)
	if e != nil {
		return nil, errors.New("review-schema-unreadable")
	}
	c := jsonschema.NewCompiler()
	c.DefaultDraft(jsonschema.Draft2020)
	c.UseLoader(offlineSchemas{})
	for p, doc := range map[string]Object{evidenceSchemaPath: r.evidenceDoc, reviewSchemaPath: r.reviewDoc} {
		if e := c.AddResource("https://quality.invalid/"+p, doc); e != nil {
			return nil, errors.New("artifact-schema-invalid")
		}
	}
	r.evidence, e = c.Compile("https://quality.invalid/" + evidenceSchemaPath)
	if e != nil {
		return nil, errors.New("evidence-schema-invalid")
	}
	r.review, e = c.Compile("https://quality.invalid/" + reviewSchemaPath)
	if e != nil {
		return nil, errors.New("review-schema-invalid")
	}
	r.Current, e = JSON(s, policyPath)
	if e != nil || r.validatePolicy(r.Current) != nil {
		return nil, errors.New("report-policy-invalid")
	}
	archived, e := r.revision(str(r.Current["policy_id"]))
	if e != nil || canonicalDigest(archived) != canonicalDigest(r.Current) {
		return nil, errors.New("active-policy-archive-mismatch")
	}
	return r, nil
}
func set(items []string) map[string]bool {
	out := map[string]bool{}
	for _, s := range items {
		out[s] = true
	}
	return out
}
func keys(m Object) []string {
	out := []string{}
	for k := range m {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}
func sameStrings(a, b []string) bool { return maps.Equal(set(a), set(b)) }
func subset(a, b []string) bool {
	s := set(b)
	for _, v := range a {
		if !s[v] {
			return false
		}
	}
	return true
}
func unique(items []string) bool { return len(items) == len(set(items)) }
func (r *Rules) validatePolicy(p Object) error {
	version, ok := integer(p["schema_version"])
	if !ok || version != 1 || !policyID.MatchString(str(p["policy_id"])) || p["current_report_schema"] != currentReportSchema {
		return errors.New("policy-header")
	}
	dimensions := obj(p["dimensions"])
	total := 0.0
	for _, v := range dimensions {
		n, ok := number(v)
		if !ok || n < 0 || n > 100 {
			return errors.New("policy-dimensions")
		}
		total += n
	}
	if len(dimensions) == 0 || total != 100 {
		return errors.New("policy-dimensions")
	}
	tiers := obj(p["tiers"])
	evTiers := stringsOf(nested(r.evidenceDoc, "properties", "quality_tier", "enum"))
	revTiers := stringsOf(nested(r.reviewDoc, "properties", "quality_tier", "enum"))
	reviewItem := nested(r.reviewDoc, "properties", "reviews", "items", "properties")
	if !sameStrings(keys(tiers), evTiers) || !sameStrings(evTiers, revTiers) || !sameStrings(keys(dimensions), keys(obj(nested(reviewItem, "scores", "properties")))) {
		return errors.New("policy-schema-drift")
	}
	if !sameStrings(stringsOf(p["hard_failure_codes"]), stringsOf(nested(reviewItem, "hard_failures", "items", "enum"))) ||
		!sameStrings([]string{"primary", "official", "secondary", "local", "execution"}, stringsOf(nested(r.evidenceDoc, "properties", "sources", "items", "properties", "kind", "enum"))) ||
		!sameStrings([]string{"direct", "derived", "inference"}, stringsOf(nested(r.evidenceDoc, "properties", "claims", "items", "properties", "support", "enum"))) ||
		!sameStrings([]string{"primary_review", "escalation_review", "flagship_final_review"}, stringsOf(nested(reviewItem, "role", "enum"))) {
		return errors.New("policy-validator-drift")
	}
	models := obj(p["model_policy"])
	if !nonempty(models["default_generator"]) || !nonempty(models["default_reviewer"]) {
		return errors.New("model-policy")
	}
	for _, key := range []string{"premium_reviewer_order", "strong_reviewers", "scarce_models", "disabled_models"} {
		a, ok := models[key].([]any)
		if !ok || len(stringsOf(a)) != len(a) {
			return errors.New("model-policy-list")
		}
	}
	if !subset(stringsOf(models["premium_reviewer_order"]), stringsOf(models["strong_reviewers"])) {
		return errors.New("model-policy-qualification")
	}
	for _, v := range stringsOf(models["scarce_models"]) {
		if contains(models["disabled_models"], v) {
			return errors.New("model-policy-disabled-scarce")
		}
	}
	for _, raw := range tiers {
		tier := obj(raw)
		minimums := obj(tier["minimum_dimension_scores"])
		if !sameStrings(keys(minimums), keys(dimensions)) {
			return errors.New("tier-dimensions")
		}
		for _, v := range minimums {
			n, ok := number(v)
			if !ok || n < 0 || n > 100 {
				return errors.New("tier-score")
			}
		}
		for _, k := range []string{"minimum_total", "minimum_sources", "minimum_primary_sources", "minimum_critical_claims", "reviewers_required", "strong_reviewers_required", "max_revision_rounds"} {
			n, ok := number(tier[k])
			if !ok || n < 0 {
				return errors.New("tier-minimum")
			}
		}
	}
	return nil
}
func (r *Rules) revision(id string) (Object, error) {
	if !policyID.MatchString(id) {
		return nil, errors.New("policy-id-invalid")
	}
	if v, ok := r.revisions[id]; ok {
		return v, nil
	}
	p, e := JSON(r.source, policyArchive+id+".json")
	if e != nil || str(p["policy_id"]) != id || r.validatePolicy(p) != nil {
		return nil, errors.New("archived-policy-invalid")
	}
	r.revisions[id] = p
	return p, nil
}

var modelSeparators = regexp.MustCompile(`[\s_]+`)

func normalizeModel(model string, p Object) string {
	normal := func(s string) string {
		return modelSeparators.ReplaceAllString(strings.ToLower(strings.TrimSpace(s)), "-")
	}
	v := normal(model)
	for k, target := range obj(nested(p, "model_policy", "aliases")) {
		if normal(k) == v {
			return str(target)
		}
	}
	return v
}
func qualified(model string, p Object, kind string) bool {
	for _, v := range stringsOf(nested(p, "model_policy", kind)) {
		if normalizeModel(v, p) == normalizeModel(model, p) {
			return true
		}
	}
	return false
}
func modelFindings(file string, actor Object, role string, p Object) []Finding {
	out := []Finding{}
	models := obj(p["model_policy"])
	override := actor["explicit_model_override"] == true
	if override && models["explicit_user_override_allowed"] != true {
		out = append(out, issue(file, "MODEL005", "当前策略不允许模型显式覆盖。"))
	}
	if override && !nonempty(actor["override_reason"]) {
		out = append(out, issue(file, "MODEL006", "显式模型覆盖必须记录原因。"))
	}
	model := str(actor["model"])
	if qualified(model, p, "disabled_models") {
		out = append(out, issue(file, "MODEL001", "记录使用了策略禁用模型。"))
	}
	if qualified(model, p, "scarce_models") && !contains(models["scarce_model_preferred_roles"], role) && !override {
		out = append(out, warning(file, "MODEL002", "稀缺模型用于默认角色之外；需核对授权。"))
	}
	return out
}
