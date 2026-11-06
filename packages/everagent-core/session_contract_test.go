package core

import (
	"encoding/json"
	"path/filepath"
	"strings"
	"testing"
)

func TestBoundSessionUsesAutomaticReaderAndNotDeclarations(t *testing.T) {
	for _, tc := range []string{"current", "configured-key", "hint-only", "declaration-only", "changed-process", "explicit-identity"} {
		t.Run(tc, func(t *testing.T) {
			i, env := testInspector(t, "pi")
			env["PI_CODING_AGENT"], env["PI_MODEL"], env["PI_SESSION_ID"] = "true", "runtime-model", "session-one"
			switch tc {
			case "configured-key":
				r := i.Rules["pi"]
				r.SessionKeys = []string{"FIXTURE_NATIVE_ID"}
				i.Rules["pi"] = r
				env["FIXTURE_NATIVE_ID"] = env["PI_SESSION_ID"]
				delete(env, "PI_SESSION_ID")
			case "hint-only":
				delete(env, "PI_CODING_AGENT")
			case "declaration-only":
				delete(env, "PI_CODING_AGENT")
				if _, err := i.DeclareFacts(Object{"model": "user-model"}, true, 300, nil); err != nil {
					t.Fatal(err)
				}
			case "changed-process":
				i.ReadProcess = func(pid int) (Process, error) { return Process{PID: pid, Started: "restarted"}, nil }
			case "explicit-identity":
				env["AGENT_ID"] = "an-override"
			}
			h, id := i.BoundSession()
			want := tc == "current" || tc == "configured-key"
			if want && (h != "pi" || id != "session-one") || !want && (h != "" || id != "") {
				t.Fatalf("bound session = %q/%q, expected verified=%v", h, id, want)
			}
			// The native reference is opt-in in memory, not added to identity JSON.
			b, _ := json.Marshal(i.Inspect())
			if strings.Contains(string(b), "session-one") {
				t.Fatal("native session ID escaped through public identity")
			}
		})
	}
}

func TestContractPiConfiguredSessionKeyRepairWorks(t *testing.T) {
	i, env := testInspector(t, "pi")
	env["PI_CODING_AGENT"] = "true"
	env["PI_MODEL"] = "synthetic-runtime-model"
	env["PI_SESSION_ID"] = "session-one"
	before := i.Inspect()
	if before["current_model_confirmed"] != true {
		t.Fatal("default Pi fixture not observed")
	}
	path := filepath.Join(i.Home, "readers.json")
	writeFixture(t, path, encoded(t, Object{"schema_version": 1, "harnesses": Object{"pi": Object{"session_keys": []string{"PI_NEW_SESSION_ID"}}}}), i.Now())
	rules, e := readerRules(path)
	if e != nil {
		t.Fatal(e)
	}
	i.Rules = rules
	delete(env, "PI_SESSION_ID")
	env["PI_NEW_SESSION_ID"] = "session-one"
	if i.nativeID("pi") != "session-one" {
		t.Fatal("config not parsed")
	}
	after := i.Inspect()
	if after["current_model_confirmed"] != true || after["observed_model"] != "synthetic-runtime-model" {
		t.Fatal("configured Pi session key repair did not restore current-caller observation")
	}
}
func TestContractKimiDesktopConfiguredRootRepairWorks(t *testing.T) {
	i, env := testInspector(t, "kimi-desktop")
	desired := filepath.Join(i.Home, "relocated-share")
	path := filepath.Join(i.Home, "readers.json")
	writeFixture(t, path, encoded(t, Object{"schema_version": 1, "harnesses": Object{"kimi-desktop": Object{"root": desired}}}), i.Now())
	rules, e := readerRules(path)
	if e != nil {
		t.Fatal(e)
	}
	i.Rules = rules
	if i.Rules["kimi-desktop"].Root != desired {
		t.Fatal("root config was not loaded")
	}
	if i.kimiRoot() != desired {
		t.Fatal("configured Kimi Desktop root repair was ignored")
	}
	env["KIMI_SHARE_DIR"] = filepath.Join(i.Home, "explicit-share")
	if i.kimiRoot() != env["KIMI_SHARE_DIR"] {
		t.Fatal("existing explicit environment priority changed")
	}
}
func TestContractUnknownHarnessAndDeviceFactsAreNotSelfLocked(t *testing.T) {
	i, _ := testInspector(t, "pi")
	i.Processes[1].Name = "unrecognized-fixture"
	i.Processes[1].Image = "/fixture/unrecognized"
	if h, _ := i.detectHarness(); h != "" {
		t.Fatal("fixture unexpectedly auto-detected")
	}
	fields := Object{"device": "fixture-device", "harness": "pi", "form": "cli", "model": "user-chosen-model"}
	result, e := i.DeclareFacts(fields, true, 300, nil)
	if e != nil {
		t.Fatal(e)
	}
	facts := i.Facts()
	for key, value := range fields {
		if object(facts["fields"])[key] != value {
			t.Fatalf("declared %s not readable", key)
		}
	}
	identity := i.Inspect()
	if identity["cli_source"] != "user-declared" || identity["current_model_confirmed"] == true || identity["user_model_declared"] != true || result["grants_permissions"] != false {
		t.Fatal("user fallback semantics changed")
	}
	if RequireModel(identity) != nil {
		t.Fatal("explicit user model fallback incorrectly self-locked")
	}
}
func TestContractUnconfirmedModelCannotBecomeCommitReady(t *testing.T) {
	i, env := testInspector(t, "pi")
	env["PI_MODEL"] = "configured-only"
	identity := i.Inspect()
	if identity["current_model_confirmed"] == true || identity["commit_ready"] == true || RequireModel(identity) == nil {
		t.Fatal("config hint authorized commit")
	}
	ready := Readiness(Object{"known": true}, identity, Object{"status": "ok"}, Object{})
	if ready["commit"] != false {
		t.Fatal("normalized readiness admitted unconfirmed model")
	}
}
