package core

import (
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

var vendorEmail = map[string]string{
	"claude-code": "noreply@anthropic.com", "cowork": "noreply@anthropic.com", "codex": "noreply@openai.com", "chatgpt": "noreply@openai.com",
	"copilot-cli": "noreply@github.com", "copilot": "noreply@github.com", "gemini-cli": "noreply@google.com", "cursor": "noreply@cursor.com", "cursor-cli": "noreply@cursor.com",
	"trae": "noreply@trae.com", "goose": "noreply@block.xyz", "aider": "noreply@aider.chat", "opencode": "noreply@opencode.ai", "windsurf": "noreply@codeium.com",
	"qwen-code": "noreply@alibabacloud.com", "amp": "noreply@sourcegraph.com", "kimi-cli": "noreply@moonshot.ai", "kimi-desktop": "noreply@moonshot.ai",
	"minimax-code": "noreply@minimaxi.com", "qoderclicn": "noreply@qoder.com.cn", "zcode": "noreply@z.ai", "pi": "noreply@pi.dev", "dsh": "noreply@deepseek.com",
}
var envModel = map[string][]string{"opencode": {"OPENCODE_MODEL"}, "trae": {"TRAE_MODEL"}, "codex": {"CODEX_MODEL"}, "claude-code": {"ANTHROPIC_MODEL", "CLAUDE_MODEL"}, "cowork": {"ANTHROPIC_MODEL", "CLAUDE_MODEL"}, "gemini-cli": {"GEMINI_MODEL"}, "cursor": {"CURSOR_MODEL"}, "cursor-cli": {"CURSOR_MODEL"}, "pi": {"PI_MODEL"}, "zcode": {"ZCODE_MODEL"}, "kimi-cli": {"KIMI_MODEL"}, "minimax-code": {"MINIMAX_MODEL"}, "qoderclicn": {"QODERCN_MODEL"}}

func (i *Inspector) detectHarness() (string, string) {
	for _, p := range i.Processes {
		for _, h := range ruleOrder(i.Rules) {
			if i.matches(p, h) {
				if h == "claude-code" && i.Getenv("CLAUDE_CODE_IS_COWORK") != "" {
					h = "cowork"
				}
				return h, "process-ancestry"
			}
		}
	}
	rules := []struct {
		h    string
		keys []string
	}{
		{"cowork", []string{"CLAUDE_CODE_IS_COWORK"}}, {"amp", []string{"AMP_CURRENT_THREAD_ID"}},
		{"trae", []string{"TRAECLI_SESSION_INBOX"}}, {"codex", []string{"CODEX_THREAD_ID", "CODEX_SANDBOX", "CODEX_CI"}},
		{"gemini-cli", []string{"GEMINI_CLI"}}, {"copilot-cli", []string{"COPILOT_AGENT_SESSION_ID", "GH_COPILOT_CLI"}},
		{"cursor-cli", []string{"CURSOR_AGENT"}}, {"cursor", []string{"CURSOR_TRACE_ID"}}, {"opencode", []string{"OPENCODE"}},
		{"windsurf", []string{"CODEIUM_EDITOR_APP_ROOT"}}, {"qwen-code", []string{"QWEN_CODE"}}, {"aider", []string{"AIDER_API_KEY"}},
		{"claude-code", []string{"CLAUDECODE", "CLAUDE_CODE"}}, {"goose", []string{"GOOSE_PROVIDER"}}, {"qoderclicn", []string{"QODERCN_CLI"}},
		{"zcode", []string{"ZCODE_APP_VERSION", "ZCODE_ENV", "ZCODE_PROCESS_LABEL"}}, {"kimi-cli", []string{"KIMI_CLI", "KIMI_CODE_CLI"}},
		{"minimax-code", []string{"MINIMAX_CODE"}}, {"pi", []string{"PI_CODING_AGENT", "PI_SESSION_ID"}},
	}
	if i.Getenv("DSH_SHELL") == "1" && i.Getenv("DSH_SESSION_ID") != "" {
		return "dsh", "runtime-environment"
	}
	for _, r := range rules {
		if r.h == "amp" && i.Getenv("AGENT") == "amp" || r.h == "cursor-cli" && i.Getenv("CURSOR_EXTENSION_HOST_ROLE") == "agent-exec" {
			return r.h, "runtime-environment"
		}
		for _, k := range r.keys {
			if i.Getenv(k) != "" {
				return r.h, "runtime-environment"
			}
		}
	}
	return "", "unresolved"
}
func (i *Inspector) nativeID(h string) string {
	keys := i.Rules[h].SessionKeys
	if h == "trae" && len(keys) > 2 {
		if i.Getenv(keys[0]) != "" || i.Getenv(keys[1]) != "" {
			keys = keys[:2]
		} else {
			keys = keys[2:]
			if _, ok := i.owner("codex"); ok {
				return ""
			}
		}
	}
	value := ""
	for _, key := range keys {
		x := i.Getenv(key)
		if x != "" {
			if !nativePattern.MatchString(x) || value != "" && value != x {
				return ""
			}
			value = x
		}
	}
	return value
}
func (i *Inspector) Hint(h string) Object {
	for _, key := range append(append([]string{}, envModel[h]...), "AGENT_MODEL") {
		if m := model(i.Getenv(key)); m != "" {
			return Object{"model": m, "source": "env:" + key, "confidence": "environment-hint"}
		}
	}
	path, key, kind := "", "", "toml"
	switch h {
	case "codex":
		root := i.root(h, i.Getenv("CODEX_HOME"))
		if root != "" {
			path = filepath.Join(root, "config.toml")
			key = "model"
		}
	case "trae":
		if i.Home != "" {
			path = filepath.Join(i.Home, ".trae", "traecli.toml")
			key = "model"
		}
	case "kimi-cli":
		if i.Home != "" {
			path = filepath.Join(i.Home, ".kimi-code", "config.toml")
			key = "default_model"
		}
	case "minimax-code":
		if i.Home != "" {
			path = filepath.Join(i.Home, ".minimax", "config.yaml")
			key = "defaultModel"
			kind = "yaml"
		}
	case "qoderclicn":
		if i.Home != "" {
			path = filepath.Join(i.Home, ".qoder-cn", "settings.json")
			kind = "json"
		}
	}
	m := ""
	if path != "" {
		if b, e := readSmall(path, 1<<20, false); e == nil {
			if kind == "json" {
				var v Object
				if decode(b, &v) == nil {
					m = model(object(v["model"])["name"])
				}
			} else {
				re := regexp.MustCompile(`^\s*` + regexp.QuoteMeta(key) + `\s*=\s*"([^"\n]+)"\s*(?:#.*)?$`)
				if kind == "yaml" {
					re = regexp.MustCompile(`^\s*` + regexp.QuoteMeta(key) + `\s*:\s*["']?([^"'\n#]+)["']?\s*(?:#.*)?$`)
				}
				for _, line := range strings.Split(string(b), "\n") {
					if kind == "toml" && strings.HasPrefix(strings.TrimSpace(line), "[") {
						break
					}
					if match := re.FindStringSubmatch(line); match != nil {
						m = strings.TrimSpace(match[1])
						break
					}
				}
				if h == "kimi-cli" || h == "minimax-code" {
					parts := strings.Split(m, "/")
					m = parts[len(parts)-1]
				}
				if h == "minimax-code" && strings.HasPrefix(strings.ToLower(m), "minimax-") {
					m = m[len("minimax-"):]
				}
				m = model(m)
			}
		}
	}
	if m != "" {
		return Object{"model": m, "source": "config-default", "confidence": "configured"}
	}
	return Object{"model": "unknown", "source": "unresolved", "confidence": "unknown"}
}
func unresolved(source string) Object {
	return Object{"schema_version": 2, "name": "agent-unknown", "email": "noreply@everloster.com", "cli": nil, "cli_source": source, "model": "unknown", "model_source": "unresolved", "model_confidence": "unknown", "current_model_confirmed": false, "user_model_declared": false, "harness_resolved": false, "resolved": false, "commit_ready": false}
}

func InspectIdentity() Object {
	i, e := NewInspector()
	if e != nil {
		return unresolved("reader-config-invalid")
	}
	identity, _ := i.inspect()
	return identity
}
func (i *Inspector) Inspect() Object { identity, _ := i.inspect(); return identity }
func (i *Inspector) inspect() (Object, Object) {
	if i.Getenv("AGENT_ID") != "" {
		v := unresolved("explicit-override")
		v["model_source"] = "explicit-identity"
		v["model_reason_code"] = "explicit-identity-is-not-model-evidence"
		return v, Object{"status": "unavailable", "reason_code": "explicit-identity-is-not-model-evidence"}
	}
	h, source := i.detectHarness()
	facts := i.readFacts(false)
	if h == "" {
		if value := text(object(facts["fields"])["harness"]); value != "" {
			h, source = value, "user-declared"
		}
	}
	if h == "" {
		v := unresolved(source)
		v["model_reason_code"] = "current-harness-unresolved"
		return v, Object{"harness": nil, "status": "unavailable", "readers": []string{}, "reason_code": "current-harness-unresolved"}
	}
	evidence, probe := i.modelEvidence(h)
	m := text(evidence["model"])
	email := vendorEmail[h]
	if email == "" {
		email = "noreply@everloster.com"
	}
	name := strings.Trim(regexp.MustCompile(`[^A-Za-z0-9._-]+`).ReplaceAllString(h+"-"+m, "-"), "-")
	v := Object{"schema_version": 2, "name": strings.ToLower(name), "email": email, "cli": h, "cli_source": source, "harness_user_declared": source == "user-declared", "model": m, "model_source": evidence["source"], "model_confidence": evidence["confidence"], "current_model_confirmed": evidence["current_model_confirmed"], "user_model_declared": evidence["user_model_declared"], "harness_resolved": true, "resolved": !strings.HasSuffix(name, "-unknown"), "commit_ready": evidence["current_model_confirmed"] == true || evidence["user_model_declared"] == true}
	for _, k := range []string{"declaration", "scope_ref", "observed_at", "requested_model", "configured_model", "observed_model", "user_declared_model", "observation_ref", "request_observation"} {
		if x, ok := evidence[k]; ok {
			v[k] = x
		}
	}
	// Preserve this observation's failure, not a later diagnostic's result.
	if reason := text(probe["reason_code"]); reason != "" {
		v["model_reason_code"] = reason
	}
	return v, probe
}
func (i *Inspector) modelEvidence(h string) (Object, Object) {
	hint := i.Hint(h)
	scope := i.scope(h)
	found, probe := i.observe(h, scope)
	e := Object{"requested_model": nil, "configured_model": nil, "observed_model": nil, "user_declared_model": nil, "current_model_confirmed": false, "user_model_declared": false}
	if model(hint["model"]) != "" {
		e["configured_model"] = hint["model"]
	}
	requested := found != nil && found["source"] == "opencode-session-request"
	if found != nil && !requested {
		e["model"], e["source"], e["confidence"] = found["model"], found["source"], "session-bound"
		e["current_model_confirmed"] = true
		e["observed_model"] = found["model"]
		e["requested_model"] = found["requested_model"]
		e["scope_ref"] = Digest(scope)[:24]
		e["observed_at"] = found["observed_at"]
		e["observation_ref"] = found["observation_ref"]
		return e, probe
	}
	if requested {
		e["requested_model"] = found["requested_model"]
		metadata := object(found["request_metadata"])
		observation := Object{"source": found["source"], "scope_ref": Digest(scope)[:24], "observed_at": found["observed_at"], "observation_ref": found["observation_ref"]}
		for _, k := range []string{"provider_id", "variant", "step_completed", "storage_version", "binding"} {
			if v, ok := metadata[k]; ok {
				observation[k] = v
			}
		}
		e["request_observation"] = observation
	}
	declared := i.readModel(h, Digest(hint))
	facts := i.readFacts(true)
	fields := object(facts["fields"])
	timing := object(object(facts["field_times"])["model"])
	if model(fields["model"]) != "" && (fields["harness"] == nil || fields["harness"] == h) && (declared == nil || number(timing["declared_at"]) >= number(declared["declared_at"])) {
		declared = clone(facts)
		declared["model"] = fields["model"]
		declared["declared_at"] = timing["declared_at"]
		declared["expires_at"] = timing["expires_at"]
	}
	discarded := number(facts["model_discarded_at"])
	if declared != nil && (discarded == 0 || number(declared["declared_at"]) > discarded) && seconds(i.Now()) < number(declared["expires_at"]) {
		e["model"], e["source"], e["confidence"], e["user_model_declared"] = declared["model"], "user-declared", "declared", true
		e["user_declared_model"] = declared["model"]
		e["declaration"] = Object{"id": declared["id"], "scope_ref": Digest(declared["scope"])[:24], "expires_at": declared["expires_at"]}
		return e, probe
	}
	if requested {
		e["model"], e["source"], e["confidence"] = "unknown", "opencode-session-request", "requested"
	} else {
		for k, v := range hint {
			e[k] = v
		}
	}
	return e, probe
}
func (i *Inspector) Diagnose() Object {
	identity, probe := i.inspect()
	ready := identity["commit_ready"] == true
	status := "repair-needed"
	if ready {
		status = "ready"
	}
	owners := []string{"packages/everagent-core/config.go", "packages/everagent-core/process.go", "packages/everagent-core/identity.go", "packages/everagent-core/observations.go", "packages/everagent-core/declarations.go"}
	if identity["cli"] == "opencode" {
		owners = append(owners, "packages/everagent-core/opencode.go", "packages/everagent-core/src/everagent_core/identity/opencode_plugin.mjs")
	}
	return Object{"schema_version": 1, "status": status, "identity": identity, "automatic_probe": probe, "reader_config": Object{"owner": "packages/everagent-core/src/everagent_core/identity/readers.json", "override_environment": "EVERAGENT_IDENTITY_CONFIG", "status": "valid"}, "repair": Object{"owner_repository": "EverAgent", "owners": owners, "order": []string{"inspect-current-caller-binding", "repair-supported-reader-or-adapter", "verify-current-session-and-regressions", "request-explicit-user-facts-if-unverifiable"}, "validation": []string{"eacli session current --json", "eacli session diagnose --json"}, "boundary": "Only current-caller metadata; retain privacy, process/session binding, freshness and unknown states."}, "user_fallback": Object{"role": "last-resort", "available": i.factScope() != nil, "fields": []string{"device", "harness", "form", "model"}, "requires_explicit_user_confirmation": true}, "authorized_source_repair_allowed": true, "authorized_read_only_allowed": true, "commit_allowed": ready, "diagnostics_are_model_evidence": false}
}

// Form is a classification, not model evidence or a task authorization.
func (i *Inspector) Form(h string) string {
	if form := i.Rules[h].Form; form != "" {
		return form
	}
	return "unknown"
}
func (i *Inspector) HostApp() Object {
	for _, p := range i.Processes {
		if i.matches(p, "dsh") {
			return Object{"id": "dsh", "kind": "dsh", "status": "verified", "verified": true, "source": "caller-process-entry"}
		}
		if app := appForProcess(p, os.PathSeparator == '\\'); app != "" {
			return Object{"id": app, "kind": "desktop", "verified": true, "source": "caller-process-image", "model_api": "unavailable"}
		}
	}
	return Object{"id": nil, "kind": "terminal", "verified": false, "source": "unresolved"}
}
