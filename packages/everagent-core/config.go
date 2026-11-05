package core

import (
	"embed"
	"errors"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
)

// One configuration owner during migration; it moves with the core, not into
// an installation-specific second registry.
//
//go:embed src/everagent_core/identity/readers.json
var readerAssets embed.FS

type Rule struct {
	ProcessNames []string `json:"process_names,omitempty"`
	SessionKeys  []string `json:"session_keys,omitempty"`
	Root         string   `json:"root,omitempty"`
	ModelKey     string   `json:"model_key,omitempty"`
	Form         string   `json:"form"`
}

func readerRules(override string) (map[string]Rule, error) {
	b, e := readerAssets.ReadFile("src/everagent_core/identity/readers.json")
	if e != nil {
		return nil, e
	}
	var raw struct {
		Schema    int               `json:"schema_version"`
		Harnesses map[string]Object `json:"harnesses"`
	}
	if e = decode(b, &raw); e != nil {
		return nil, e
	}
	if override != "" {
		b, e = readSmall(override, 65536, false)
		if e != nil {
			return nil, errors.New("identity-config-unavailable")
		}
		var patch Object
		if decode(b, &patch) != nil || number(patch["schema_version"]) != 1 || len(patch) != 2 {
			return nil, errors.New("identity-config-schema-invalid")
		}
		changes, ok := patch["harnesses"].(map[string]any)
		if !ok || len(changes) > 64 {
			return nil, errors.New("identity-config-harnesses-invalid")
		}
		for key, value := range changes {
			fields, ok := value.(map[string]any)
			if !ok {
				return nil, errors.New("identity-config-rule-invalid")
			}
			if raw.Harnesses[key] == nil {
				raw.Harnesses[key] = Object{}
			}
			for k, v := range fields {
				raw.Harnesses[key][k] = v
			}
		}
	}
	nameRE := regexp.MustCompile(`^[a-z][a-z0-9-]{0,63}$`)
	envRE := regexp.MustCompile(`^[A-Z][A-Z0-9_]{1,127}$`)
	secretRE := regexp.MustCompile(`TOKEN|PASSWORD|SECRET|COOKIE|AUTH|API_KEY`)
	keyRE := regexp.MustCompile(`^[A-Za-z][A-Za-z0-9_]{0,63}$`)
	rules := map[string]Rule{}
	for name, fields := range raw.Harnesses {
		if !nameRE.MatchString(name) {
			return nil, errors.New("identity-config-rule-invalid")
		}
		var r Rule
		for k, v := range fields {
			switch k {
			case "process_names", "session_keys":
				items, ok := v.([]any)
				if !ok || len(items) > 16 {
					return nil, errors.New("identity-config-signature-invalid")
				}
				values := []string{}
				for _, item := range items {
					s, ok := item.(string)
					if !ok || len(s) == 0 || len(s) > 128 {
						return nil, errors.New("identity-config-signature-invalid")
					}
					if k == "process_names" && (strings.ContainsAny(s, "/\\*?\n\r") || contains([]string{"node", "python", "python3", "bash", "zsh", "sh", "pwsh", "cmd.exe"}, strings.ToLower(s))) {
						return nil, errors.New("identity-config-generic-process-refused")
					}
					if k == "session_keys" && (!envRE.MatchString(s) || secretRE.MatchString(s)) {
						return nil, errors.New("identity-config-session-key-invalid")
					}
					values = append(values, s)
				}
				if k == "process_names" {
					r.ProcessNames = values
				} else {
					r.SessionKeys = values
				}
			case "root":
				r.Root = text(v)
				if r.Root == "" || len(r.Root) > 1024 || strings.ContainsAny(r.Root, "\n\r\x00*?$") || !(strings.HasPrefix(r.Root, "~/") || filepath.IsAbs(r.Root)) {
					return nil, errors.New("identity-config-root-invalid")
				}
			case "model_key":
				r.ModelKey = text(v)
				if !keyRE.MatchString(r.ModelKey) {
					return nil, errors.New("identity-config-model-key-invalid")
				}
			case "form":
				r.Form = text(v)
			default:
				return nil, errors.New("identity-config-rule-invalid")
			}
		}
		if !contains([]string{"cli", "desktop", "web"}, r.Form) {
			return nil, errors.New("identity-config-form-invalid")
		}
		rules[name] = r
	}
	return rules, nil
}
func contains(values []string, s string) bool {
	for _, v := range values {
		if s == v {
			return true
		}
	}
	return false
}
func ruleOrder(rules map[string]Rule) []string {
	// A deterministic tie is necessary when a configured signature overlaps.
	// Specific runtime owners precede their enclosing Desktop application.
	order := []string{"dsh", "codex", "claude-code", "trae", "qoderclicn", "zcode", "kimi-cli", "kimi-desktop", "minimax-code", "pi", "opencode", "cursor-cli"}
	extra := []string{}
	for key := range rules {
		if !contains(order, key) {
			extra = append(extra, key)
		}
	}
	sort.Strings(extra)
	return append(order, extra...)
}

func (i *Inspector) root(harness, override string) string {
	if override == "" {
		override = i.Rules[harness].Root
	}
	path := expandHome(override, i.Home)
	if !filepath.IsAbs(path) {
		return ""
	}
	return realPath(path)
}
