package core

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
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
	if v["cli"] != "pi" || v["model"] != "actual-pi" || v["current_model_confirmed"] != true {
		t.Fatalf("nearest native caller: %v", v)
	}
	env["PI_CODING_AGENT"] = "false"
	v = i.Inspect()
	if v["model"] != "actual-pi" || v["commit_ready"] != false || v["current_model_confirmed"] != false {
		t.Fatalf("configuration used as proof: %v", v)
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
