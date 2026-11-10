package core

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
	"time"
)

// Each reader sees a synthetic HOME, environment, clock and exact ancestry.
// Tests must never discover the developer's real sessions or credentials.
func testInspector(t *testing.T, harness string) (*Inspector, map[string]string) {
	t.Helper()
	home := realPath(t.TempDir())
	rules, err := readerRules("")
	if err != nil {
		t.Fatal(err)
	}
	now := time.Unix(1780000000, 123000000)
	env := map[string]string{}
	name := harness
	if len(rules[harness].ProcessNames) > 0 {
		name = rules[harness].ProcessNames[0]
	}
	owner := Process{PID: 4200, Parent: 1, Name: name, Image: "/fixture/" + name, Started: "fixture-owner-start", StartTime: now.Add(-time.Minute)}
	if runtime.GOOS == "windows" {
		images := map[string]string{
			"kimi-desktop": `C:\Program Files\Kimi\Kimi.exe`,
			"minimax-code": `C:\Program Files\MiniMax Code\MiniMax Code.exe`,
			"zcode":        `C:\Program Files\ZCode\ZCode.exe`,
		}
		if image, ok := images[harness]; ok {
			owner.Name, owner.Image = filepath.Base(image), image
		}
	}
	shell := Process{PID: 4201, Parent: owner.PID, Name: "bash", Image: "/bin/bash", Started: "fixture-shell-start", StartTime: now.Add(-time.Second)}
	i := &Inspector{Home: home, Directory: home, Getenv: func(key string) string { return env[key] }, Now: func() time.Time { return now }, Rules: rules, Processes: []Process{shell, owner}}
	i.ReadProcess = func(pid int) (Process, error) {
		for _, p := range i.Processes {
			if p.PID == pid {
				return p, nil
			}
		}
		return Process{}, errors.New("not a caller ancestor")
	}
	i.ProcessArgs = func(pid int) ([]string, error) { return nil, errors.New("no native argv fixture") }
	i.ProcessCwd = func(p Process) (string, error) { return i.Directory, nil }
	return i, env
}

func writeFixture(t *testing.T, path string, data []byte, now time.Time) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, data, 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.Chtimes(path, now, now); err != nil {
		t.Fatal(err)
	}
}

func encoded(t *testing.T, value any) []byte {
	t.Helper()
	b, err := json.Marshal(value)
	if err != nil {
		t.Fatal(err)
	}
	return b
}

func TestMetadataProjection(t *testing.T) {
	raw := []byte(`{"session":"one","body":{"text":"PRIVATE-DIALOG-SENTINEL","model":"wrong"},"model":"right"}`)
	v, err := metadata(raw, "session", "model")
	if err != nil || v["model"] != "right" || len(v) != 2 || strings.Contains(string(encoded(t, v)), "PRIVATE") {
		t.Fatalf("projection: %v %v", v, err)
	}
	for _, bad := range []string{`{"model":"one","model":"two"}`, `{"model":"one"} {}`, `{"x":`, `[]`, `{"x":` + strings.Repeat("[", 33) + "0" + strings.Repeat("]", 33) + "}"} {
		if _, err := fields([]byte(bad)); err == nil {
			t.Fatalf("accepted invalid/ambiguous metadata: %.80s", bad)
		}
	}
}

func TestDigestCanonicalCompatibility(t *testing.T) {
	wire := []byte(`{"a":"\u4e2d\u6587\ud83d\udc4b","b":1.0,"c":["<>"]}`)
	var value Object
	if err := decode(wire, &value); err != nil {
		t.Fatal(err)
	}
	hash := sha256.Sum256(wire)
	if got := Digest(value); got != hex.EncodeToString(hash[:]) {
		t.Fatalf("existing canonical receipt hash changed: %s", got)
	}
}

func TestConfigRepairDoesNotConfigureAnswers(t *testing.T) {
	root := t.TempDir()
	path := filepath.Join(root, "readers.json")
	for _, tc := range []struct {
		name string
		rule Object
		ok   bool
	}{
		{"rename-process", Object{"process_names": []string{"new-codex"}}, true},
		{"new-root", Object{"root": filepath.Join(root, "sessions")}, true},
		{"field-key", Object{"model_key": "actualModel"}, true},
		{"model-answer", Object{"model": "fake-proof"}, false},
		{"generic-process", Object{"process_names": []string{"node"}}, false},
		{"credential-variable", Object{"session_keys": []string{"API_TOKEN"}}, false},
		{"glob-path", Object{"root": "~/.codex/*"}, false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			writeFixture(t, path, encoded(t, Object{"schema_version": 1, "harnesses": Object{"codex": tc.rule}}), time.Now())
			_, err := readerRules(path)
			if (err == nil) != tc.ok {
				t.Fatalf("result %v", err)
			}
		})
	}
}

func TestHarnessAndHints(t *testing.T) {
	i, env := testInspector(t, "pi")
	env["CODEX_THREAD_ID"] = "inherited-codex"
	env["PI_SESSION_ID"], env["PI_MODEL"], env["PI_CODING_AGENT"] = "pi-native", "actual-pi", "true"
	v := i.Inspect()
	if v["cli"] != "pi" || v["model"] != "actual-pi" || v["current_model_confirmed"] != true || v["configured_model_source"] != "env:PI_MODEL" {
		t.Fatalf("nearest native caller: %v", v)
	}
	env["PI_CODING_AGENT"] = "false"
	v = i.Inspect()
	if v["model"] != "actual-pi" || v["commit_ready"] != false || v["current_model_confirmed"] != false {
		t.Fatalf("configuration used as proof: %v", v)
	}
	session := i.NormalizeSession(Object{"known": true}, v, Object{"status": "ok"}, Object{}, nil, nil, nil)
	m := object(object(session["actor"])["model"])
	if m["id"] != "unknown" || m["configured"] != "actual-pi" || m["configured_source"] != "env:PI_MODEL" || object(session["readiness"])["commit"] != false {
		t.Fatalf("environment hint changed session readiness: %v", session)
	}
	i.Processes[1].Name = "pi-similar-not-agent"
	delete(env, "PI_SESSION_ID")
	delete(env, "PI_CODING_AGENT")
	delete(env, "CODEX_THREAD_ID")
	if v = i.Inspect(); v["harness_resolved"] != false || v["model_reason_code"] != "current-harness-unresolved" {
		t.Fatalf("substring process match: %v", v)
	}
	i, env = testInspector(t, "codex")
	writeFixture(t, filepath.Join(i.Home, ".codex/config.toml"), []byte("[nested]\nmodel = \"not-a-default\"\n"), i.Now())
	if i.Hint("codex")["model"] != "unknown" {
		t.Fatal("nested TOML treated as default")
	}
	v = i.Inspect()
	session = i.NormalizeSession(Object{"known": true}, v, Object{"status": "ok"}, Object{}, nil, nil, nil)
	if v["configured_model_source"] != nil || object(object(session["actor"])["model"])["configured_source"] != nil {
		t.Fatalf("missing hint acquired a source: %v", session)
	}
	writeFixture(t, filepath.Join(i.Home, ".codex/config.toml"), []byte("model = \"default-model\"\nprofile = \"selected\"\n[profiles.selected]\nmodel = \"profile-model\"\n"), i.Now())
	v = i.Inspect()
	session = i.NormalizeSession(Object{"known": true}, v, Object{"status": "ok"}, Object{}, nil, nil, nil)
	m = object(object(session["actor"])["model"])
	if v["configured_model_source"] != "config-default" || m["configured"] != "default-model" || m["configured_source"] != "config-default" || m["id"] != "unknown" || object(session["readiness"])["commit"] != false {
		t.Fatalf("default hint was lost or interpreted as the effective profile: %v", session)
	}
	delete(v, "configured_model_source") // Older identity clients have no provenance field.
	session = i.NormalizeSession(Object{"known": true}, v, Object{"status": "ok"}, Object{}, nil, nil, nil)
	m = object(object(session["actor"])["model"])
	if m["configured"] != "default-model" || m["configured_source"] != nil {
		t.Fatalf("legacy hint source was guessed: %v", session)
	}
	env["AGENT_ID"] = "spoofed-identity"
	if v = i.Inspect(); v["commit_ready"] != false || v["model_reason_code"] != "explicit-identity-is-not-model-evidence" {
		t.Fatal("AGENT_ID must not authorize commits")
	}
}

func TestDesktopScopeAndProcessRecheck(t *testing.T) {
	i, env := testInspector(t, "minimax-code")
	env["ORCA_TERMINAL_HANDLE"] = "inherited-terminal"
	first := i.scope("minimax-code")
	if first["execution_ref"] == nil {
		t.Fatal("desktop must bind its execution shell")
	}
	i.Processes[0].Started = "another-execution"
	if Digest(first) == Digest(i.scope("minimax-code")) {
		t.Fatal("desktop declaration carried across shells")
	}
	i.Processes = []Process{i.Processes[1], i.Processes[0]}
	if i.scope("minimax-code") != nil {
		t.Fatal("desktop borrowed its outer launch shell")
	}
	i, _ = testInspector(t, "codex")
	p := i.Processes[1]
	i.ProcessCwd = func(Process) (string, error) {
		i.Processes[1].Started = "restarted"
		return i.Directory, nil
	}
	if i.callerCwd(p) != "" {
		t.Fatal("changed process supplied a cwd")
	}
}

func TestDeclarationLifecycle(t *testing.T) {
	i, env := testInspector(t, "cursor-cli")
	env["CURSOR_CONVERSATION_ID"] = "conversation-one"
	if _, err := i.DeclareFacts(Object{"model": "chosen"}, false, 300, nil); err == nil {
		t.Fatal("declaration without user confirmation")
	}
	if _, err := i.DeclareFacts(Object{"model": "chosen"}, true, 300, Object{"model": "observed"}); err == nil {
		t.Fatal("declaration overrode automatic evidence")
	}
	receipt, err := i.DeclareFacts(Object{"model": "chosen"}, true, 300, nil)
	if err != nil || receipt["grants_permissions"] != false {
		t.Fatalf("declare: %v %v", receipt, err)
	}
	v := i.Inspect()
	if v["user_model_declared"] != true || v["current_model_confirmed"] != false || v["model"] != "chosen" {
		t.Fatalf("declared identity: %v", v)
	}
	start := i.Now()
	i.Now = func() time.Time { return start.Add(100 * time.Second) }
	if _, err = i.DeclareFacts(Object{"device": "fixture-device"}, true, 300, nil); err != nil {
		t.Fatal(err)
	}
	i.Now = func() time.Time { return start.Add(301 * time.Second) }
	if v = i.Inspect(); v["user_model_declared"] != false || object(i.Facts()["fields"])["device"] != "fixture-device" {
		t.Fatalf("unrelated declaration refreshed model TTL: %v", v)
	}
	env["CURSOR_CONVERSATION_ID"] = "conversation-two"
	if i.Facts() != nil {
		t.Fatal("facts leaked across native sessions")
	}
	env["CURSOR_CONVERSATION_ID"] = "conversation-one"
	env["CURSOR_MODEL"] = "new-configured-model"
	if i.Facts() != nil {
		t.Fatal("facts survived changed model hint")
	}
}

func TestDeclarationConflictRevokesOldModel(t *testing.T) {
	i, env := testInspector(t, "cursor-cli")
	env["CURSOR_CONVERSATION_ID"] = "one"
	if _, err := i.DeclareFacts(Object{"model": "old-model"}, true, 600, nil); err != nil {
		t.Fatal(err)
	}
	start := i.Now()
	i.Now = func() time.Time { return start.Add(time.Second) }
	if _, err := i.DeclareFacts(Object{"device": "fixture-device"}, true, 600, Object{"model": "automatic-new"}); err != nil {
		t.Fatal(err)
	}
	if v := i.Inspect(); v["user_model_declared"] != false {
		t.Fatalf("revoked model revived: %v", v)
	}
	if _, err := i.DeclareFacts(Object{"model": "same-timestamp"}, true, 600, nil); err != nil {
		t.Fatal(err)
	}
	if i.Inspect()["user_model_declared"] != false {
		t.Fatal("same-timestamp declaration bypassed discard boundary")
	}
	i.Now = func() time.Time { return start.Add(2 * time.Second) }
	if _, err := i.DeclareFacts(Object{"model": "new-user-model"}, true, 600, nil); err != nil {
		t.Fatal(err)
	}
	if i.Inspect()["model"] != "new-user-model" {
		t.Fatal("later explicit confirmation should be accepted")
	}
}

func TestUnknownSessionDoesNotProbeApps(t *testing.T) {
	i, _ := testInspector(t, "dsh")
	i.ProcessArgs = func(int) ([]string, error) { t.Fatal("unknown device probed an application"); return nil, nil }
	v := i.NormalizeSession(Object{"known": false}, nil, nil, nil, nil, nil, nil)
	if v["status"] != "unknown-device" || object(v["readiness"])["read_only"] != false {
		t.Fatalf("unknown-device contract: %v", v)
	}
}

func TestBoundedCommandFailsOnCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := command(ctx, "", nil, 1024, "git", "--version"); err == nil {
		t.Fatal("cancelled command reported success")
	}
	if _, err := boundedCommand("", nil, time.Second, 1, "git", "--version"); err == nil {
		t.Fatal("truncated subprocess output reported success")
	}
}

func kimiFixture(t *testing.T, i *Inspector, id string, legacy bool) (string, Object, []byte) {
	t.Helper()
	now := i.Now()
	dir := filepath.Join(i.root("kimi-cli", ""), kimiWorkspaceKey(i.Directory), id)
	state := Object{"id": id, "version": 2, "cwd": i.Directory, "createdAt": now.Add(-time.Hour).UnixMilli(), "updatedAt": now.UnixMilli(), "archived": false,
		"agents": Object{"main": Object{"type": "main"}}, "lastPrompt": "PRIVATE-METADATA-SENTINEL"}
	if legacy {
		delete(state, "id")
		delete(state, "version")
		delete(state, "cwd")
		delete(state, "archived")
		state["workDir"] = i.Directory
		state["createdAt"] = now.Add(-time.Hour).Format(time.RFC3339Nano)
		state["updatedAt"] = now.Format(time.RFC3339Nano)
	}
	wire := append([]byte(`{"type":"llm.request",`), encoded(t, Object{"model": "native-kimi", "time": now.UnixMilli(), "kind": "loop", "turnStep": "turn-1", "modelAlias": "kimi-for-code"})[1:]...)
	wire = append(wire, '\n')
	writeFixture(t, filepath.Join(dir, "state.json"), encoded(t, state), now)
	writeFixture(t, filepath.Join(dir, "agents/main/wire.jsonl"), wire, now)
	return dir, state, wire
}

func TestKimiScopedReadDoesNotStartCLI(t *testing.T) {
	for _, legacy := range []bool{false, true} {
		t.Run(map[bool]string{false: "v2", true: "legacy"}[legacy], func(t *testing.T) {
			i, env := testInspector(t, "kimi-cli")
			env["KIMI_MODEL"] = "configured-not-proof"
			dir, _, wire := kimiFixture(t, i, "session-one", legacy)
			// A real CLI would run an updater before parsing `session list`.
			// No executable at all must be necessary for native metadata reads.
			t.Setenv("PATH", t.TempDir())
			got := i.Inspect()
			if got["model"] != "native-kimi" || got["current_model_confirmed"] != true || got["commit_ready"] != true {
				t.Fatalf("native read without CLI: %v", got)
			}
			if strings.Contains(string(encoded(t, got)), "PRIVATE-METADATA") {
				t.Fatal("metadata body escaped projection")
			}
			before, _ := os.ReadFile(filepath.Join(dir, "state.json"))
			i.Diagnose()
			after, _ := os.ReadFile(filepath.Join(dir, "state.json"))
			afterWire, _ := os.ReadFile(filepath.Join(dir, "agents/main/wire.jsonl"))
			if string(before) != string(after) || string(wire) != string(afterWire) {
				t.Fatal("read-only inspection modified native files")
			}
		})
	}
}

func TestKimiNativeWorkspaceKeys(t *testing.T) {
	for cwd, want := range map[string]string{
		"/workspace/Project Two": "wd_project-two_8b6646286453",
		"/workspace/中文":          "wd_workspace_d1229f0dfc6b",
		`C:\workspace\Project\`:  "wd_project_ee63f7b5298f",
		"/workspace/abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH": "wd_abcdefghijklmnopqrstuvwxyz0123456789abcd_5149bedf2554",
	} {
		if got := kimiWorkspaceKey(cwd); got != want {
			t.Errorf("native key for %q: %s, want %s", cwd, got, want)
		}
	}
}

func TestKimiNativeRootRepair(t *testing.T) {
	for _, via := range []string{"reader-config", "native-home"} {
		t.Run(via, func(t *testing.T) {
			i, env := testInspector(t, "kimi-cli")
			root := filepath.Join(i.Home, "custom", "sessions")
			rule := i.Rules["kimi-cli"]
			rule.Root = root
			i.Rules["kimi-cli"] = rule
			kimiFixture(t, i, "session-one", false)
			if via == "native-home" {
				rule.Root = filepath.Join(i.Home, "unused")
				i.Rules["kimi-cli"] = rule
				env["KIMI_CODE_HOME"] = filepath.Dir(root)
			}
			if got, why := i.kimiCLI(i.Processes[1], i.Now()); got == nil || why != "" {
				t.Fatalf("root repair: %v %s", got, why)
			}
		})
	}
}

func TestKimiInactiveAndUnboundDirectories(t *testing.T) {
	i, _ := testInspector(t, "kimi-cli")
	dir, _, _ := kimiFixture(t, i, "session-one", false)
	for _, id := range []string{"archived", "old"} {
		other, state, _ := kimiFixture(t, i, id, false)
		if id == "archived" {
			state["archived"] = true
		} else {
			state["updatedAt"] = i.Now().Add(-10 * time.Minute).UnixMilli()
		}
		writeFixture(t, filepath.Join(other, "state.json"), encoded(t, state), i.Now())
		writeFixture(t, filepath.Join(other, "agents/main/wire.jsonl"), []byte("NOT_A_MODEL_SOURCE"), i.Now())
	}
	if err := os.Mkdir(filepath.Join(filepath.Dir(dir), "empty"), 0700); err != nil {
		t.Fatal(err)
	}
	if got, why := i.kimiCLI(i.Processes[1], i.Now()); got == nil || why != "" {
		t.Fatalf("empty/inactive directories blocked a bound session: %v %s", got, why)
	}
	// A directory with wire but no metadata is not an empty directory. Keep
	// the gap visible and do not open that body or assume unique live binding.
	unbound := filepath.Join(filepath.Dir(dir), "unbound", "agents/main/wire.jsonl")
	writeFixture(t, unbound, []byte("UNBOUND_BODY_MUST_NOT_BE_PARSED"), i.Now())
	rows, err := KimiSessions(i.root("kimi-cli", ""), i.Directory)
	if err != nil || len(rows) != 4 || rows[3].Problem != "kimi-code-scoped-metadata-missing" {
		t.Fatalf("unbound source hidden: %v %v", rows, err)
	}
	if got, why := i.kimiCLI(i.Processes[1], i.Now()); got != nil || why != "kimi-code-scoped-metadata-missing" {
		t.Fatalf("unbound source used: %v %s", got, why)
	}
}

func TestKimiResumeAfterEmptyNewSession(t *testing.T) {
	i, _ := testInspector(t, "kimi-cli")
	kimiFixture(t, i, "session-current", false)
	_, state, _ := kimiFixture(t, i, "session-empty-new", false)
	writeFixture(t, filepath.Join(i.root("kimi-cli", ""), kimiWorkspaceKey(i.Directory), "session-empty-new", "agents/main/wire.jsonl"), []byte{}, i.Now())
	state["createdAt"] = i.Now().Add(-time.Minute).UnixMilli()
	state["updatedAt"] = i.Now().UnixMilli()
	writeFixture(t, filepath.Join(i.root("kimi-cli", ""), kimiWorkspaceKey(i.Directory), "session-empty-new", "state.json"), encoded(t, state), i.Now())
	got, why := i.kimiCLI(i.Processes[1], i.Now())
	if why != "" || got == nil || got["session"] != "session-current" || got["model"] != "native-kimi" {
		t.Fatalf("resume after /new was not identified: %v %q", got, why)
	}
}

func TestKimiNativeScopeRefusesInvalidOrAmbiguousEvidence(t *testing.T) {
	for _, scenario := range []string{"two-live", "wrong-cwd", "wrong-id", "future-schema", "fork", "parent-agent", "extra-directory", "state-future", "state-old", "wire-stale", "wire-before-process", "wire-future", "wire-partial", "latest-invalid", "latest-oversized", "environment-session-mismatch", "process-changed", "cwd-changed", "metadata-changed", "wire-changed"} {
		t.Run(scenario, func(t *testing.T) {
			i, env := testInspector(t, "kimi-cli")
			dir, state, wire := kimiFixture(t, i, "session-one", false)
			switch scenario {
			case "two-live":
				kimiFixture(t, i, "session-two", false)
			case "wrong-cwd":
				state["cwd"] = filepath.Join(i.Directory, "other")
			case "wrong-id":
				state["id"] = "other"
			case "future-schema":
				state["version"] = 3
			case "fork":
				state["forkedFrom"] = "other"
			case "parent-agent":
				object(object(state["agents"])["main"])["parentAgentId"] = "other"
			case "extra-directory":
				state["additionalDirs"] = []string{"/other"}
			case "state-future":
				state["updatedAt"] = i.Now().Add(time.Hour).UnixMilli()
			case "state-old":
				state["updatedAt"] = i.Now().Add(-time.Hour).UnixMilli()
			case "wire-stale", "wire-before-process", "wire-future":
				at := i.Now().Add(-10 * time.Minute)
				if scenario == "wire-before-process" {
					at = i.Now().Add(-2 * time.Minute)
				} else if scenario == "wire-future" {
					at = i.Now().Add(time.Second)
				}
				wire = []byte(`{"type":"llm.request","kind":"loop","model":"native-kimi","turnStep":"turn-2","time":` + string(encoded(t, at.UnixMilli())) + "}\n")
			case "wire-partial":
				wire = append(wire, []byte(`{"type":"llm.request","model":"new`)...)
			case "latest-invalid":
				wire = append(wire, []byte("{\"type\":\"llm.request\",\"model\":\"bad\",oops}\n")...)
			case "latest-oversized":
				wire = append(wire, []byte(`{"type":"llm.request","body":"`+strings.Repeat("x", maxRecordBytes)+"\"}\n")...)
			case "environment-session-mismatch":
				env["KIMI_CLI_SESSION_ID"] = "other"
			case "process-changed":
				i.ReadProcess = func(int) (Process, error) { return Process{}, errors.New("process-restarted") }
			case "cwd-changed", "metadata-changed", "wire-changed":
				calls := 0
				i.ProcessCwd = func(Process) (string, error) {
					calls++
					if calls > 1 {
						if scenario == "cwd-changed" {
							return filepath.Join(i.Directory, "other"), nil
						}
						if scenario == "wire-changed" {
							writeFixture(t, filepath.Join(dir, "agents/main/wire.jsonl"), append(wire, 'x'), i.Now())
						} else {
							state["archived"] = true
							writeFixture(t, filepath.Join(dir, "state.json"), encoded(t, state), i.Now())
						}
					}
					return i.Directory, nil
				}
			}
			writeFixture(t, filepath.Join(dir, "state.json"), encoded(t, state), i.Now())
			writeFixture(t, filepath.Join(dir, "agents/main/wire.jsonl"), wire, i.Now())
			if got, why := i.kimiCLI(i.Processes[1], i.Now()); got != nil || why == "" {
				t.Fatalf("invalid evidence confirmed: %v %q", got, why)
			}
		})
	}
}

func TestKimiScopedDiscoveryDoesNotReadOtherWorkspaces(t *testing.T) {
	i, _ := testInspector(t, "kimi-cli")
	dir, state, _ := kimiFixture(t, i, "session-one", false)
	root := i.root("kimi-cli", "")
	// Corrupt and oversize metadata in another bucket is outside this reader.
	writeFixture(t, filepath.Join(root, "unrelated", "other", "state.json"), []byte("not metadata"), i.Now())
	rows, err := KimiSessions(root, i.Directory)
	if err != nil || len(rows) != 1 || rows[0].Problem != "" {
		t.Fatalf("scoped list: %v %v", rows, err)
	}
	// Native also supports session-meta/state.json; a damaged primary must not
	// silently fall back to that alternate copy.
	if err = os.Rename(filepath.Join(dir, "state.json"), filepath.Join(dir, "original.json")); err != nil {
		t.Fatal(err)
	}
	writeFixture(t, filepath.Join(dir, "session-meta/state.json"), encoded(t, state), i.Now())
	rows, err = KimiSessions(root, i.Directory)
	if err != nil || len(rows) != 1 || rows[0].Problem != "" {
		t.Fatalf("native meta scope: %v %v", rows, err)
	}
	writeFixture(t, filepath.Join(dir, "state.json"), []byte("broken"), i.Now())
	rows, err = KimiSessions(root, i.Directory)
	if err != nil || len(rows) != 1 || rows[0].Problem == "" {
		t.Fatalf("borrowed alternate state: %v %v", rows, err)
	}
}

func TestKimiScopeRejectsSymlinksAndListOverflow(t *testing.T) {
	for _, scenario := range []string{"state", "session", "wire-parent", "overflow"} {
		t.Run(scenario, func(t *testing.T) {
			if runtime.GOOS == "windows" && scenario != "overflow" {
				t.Skip("symlink creation requires Windows developer permissions")
			}
			i, _ := testInspector(t, "kimi-cli")
			dir, _, _ := kimiFixture(t, i, "session-one", false)
			if scenario == "overflow" {
				for n := 0; n < 256; n++ {
					if err := os.Mkdir(filepath.Join(filepath.Dir(dir), "session-"+string(encoded(t, n))), 0700); err != nil {
						t.Fatal(err)
					}
				}
			} else {
				path := filepath.Join(dir, "state.json")
				if scenario == "session" {
					path = dir
				} else if scenario == "wire-parent" {
					path = filepath.Join(dir, "agents")
				}
				moved := filepath.Join(t.TempDir(), "native")
				if err := os.Rename(path, moved); err != nil {
					t.Fatal(err)
				}
				if err := os.Symlink(moved, path); err != nil {
					t.Fatal(err)
				}
			}
			if got, why := i.kimiCLI(i.Processes[1], i.Now()); got != nil || why == "" {
				t.Fatalf("unsafe path/partial list confirmed: %v %s", got, why)
			}
		})
	}
}
