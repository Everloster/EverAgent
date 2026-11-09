package core

import (
	"database/sql"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"strconv"
	"strings"
	"testing"
	"time"
)

func fixtureDB(t *testing.T, path string) *sql.DB {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
		t.Fatal(err)
	}
	db, err := sql.Open("sqlite", path)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { db.Close() })
	return db
}

func sqlFixture(t *testing.T, db *sql.DB, query string, args ...any) {
	t.Helper()
	if _, err := db.Exec(query, args...); err != nil {
		t.Fatal(err)
	}
}

func TestNativeDatabasePath(t *testing.T) {
	path := filepath.Join(t.TempDir(), "state_5.sqlite")
	db := fixtureDB(t, path)
	sqlFixture(t, db, "CREATE TABLE threads(id TEXT PRIMARY KEY)")
	sqlFixture(t, db, "INSERT INTO threads VALUES('thread-one')")
	read, err := openReadDB(path)
	if err != nil {
		t.Fatal(err)
	}
	defer read.Close()
	var id string
	if err = read.QueryRow("SELECT id FROM threads").Scan(&id); err != nil || id != "thread-one" {
		t.Fatalf("native database path was not readable: %q %v", id, err)
	}
}

func TestCodexModelEvidence(t *testing.T) {
	for _, tc := range []string{"current", "long-turn", "no-index", "conflict", "wrong-header", "wrong-thread", "ended", "stale-file", "archived", "restart", "nested", "missing-id", "disagreeing-ids", "duplicate-model"} {
		t.Run(tc, func(t *testing.T) {
			i, env := testInspector(t, "codex")
			now := i.Now()
			env["CODEX_THREAD_ID"] = "thread-one"
			env["CODEX_MODEL"] = "misleading-default"
			root := filepath.Join(i.Home, ".codex")
			path := filepath.Join(root, "sessions/2026/01/01/rollout-fixture-thread-one.jsonl")
			header := "thread-one"
			if tc == "wrong-header" {
				header = "another-thread"
			}
			record := func(kind string, payload Object) string {
				// The actual native envelope order is part of the format.
				body := string(encoded(t, payload))
				if kind == "event_msg" {
					body = `{"type":` + strconv.Quote(text(payload["type"])) + `,"turn_id":` + strconv.Quote(text(payload["turn_id"])) + "}"
				}
				return `{"timestamp":` + strconv.Quote(now.Format(time.RFC3339Nano)) + `,"type":` + strconv.Quote(kind) + `,"payload":` + body + "}\n"
			}
			data := record("session_meta", Object{"id": header, "cwd": i.Directory, "originator": "synthetic"})
			data += record("event_msg", Object{"type": "task_started", "turn_id": "turn-one"})
			data += record("turn_context", Object{"turn_id": "turn-one", "model": "observed-model", "instructions": "PRIVATE-DIALOG-SENTINEL"})
			if tc == "duplicate-model" {
				data = strings.Replace(data, `"model":"observed-model"`, `"model":"old-model","model":"observed-model"`, 1)
			}
			if tc == "long-turn" || tc == "wrong-thread" {
				data += record("response_item", Object{"body": strings.Repeat("x", maxTailBytes+1024)})
			}
			thread := "thread-one"
			if tc == "wrong-thread" {
				thread = "other-thread"
			}
			data += record("token_usage_record", Object{"thread_id": thread, "turn_id": "turn-one"})
			if tc == "ended" {
				data += record("event_msg", Object{"type": "task_complete", "turn_id": "turn-one"})
			}
			writeFixture(t, path, []byte(data), now)
			if tc != "no-index" {
				db := fixtureDB(t, filepath.Join(root, "state_5.sqlite"))
				sqlFixture(t, db, "CREATE TABLE threads(id TEXT PRIMARY KEY, rollout_path TEXT, model TEXT, archived INTEGER, updated_at_ms INTEGER)")
				indexed, archived := "observed-model", 0
				if tc == "conflict" {
					indexed = "different-model"
				}
				if tc == "archived" {
					archived = 1
				}
				sqlFixture(t, db, "INSERT INTO threads VALUES(?,?,?,?,?)", "thread-one", path, indexed, archived, now.UnixMilli())
			}
			switch tc {
			case "stale-file":
				os.Chtimes(path, now.Add(-301*time.Second), now.Add(-301*time.Second))
			case "restart":
				i.Processes[1].StartTime = now.Add(5 * time.Second)
			case "nested":
				other := i.Processes[1]
				other.PID = 5000
				i.Processes = append(i.Processes, other)
			case "missing-id":
				delete(env, "CODEX_THREAD_ID")
			case "disagreeing-ids":
				env["CODEX_SESSION_ID"] = "another-thread"
			}
			v := i.Inspect()
			want := tc == "current" || tc == "long-turn" || tc == "no-index"
			if (v["current_model_confirmed"] == true) != want {
				t.Fatalf("%s: %v\n%v", tc, v, i.Diagnose())
			}
			h, id := i.BoundSession()
			if want && (h != "codex" || id != "thread-one") || !want && (h != "" || id != "") {
				t.Fatalf("current session binding disagrees with native reader: %q/%q", h, id)
			}
			if want && v["model"] != "observed-model" {
				t.Fatalf("configured default used instead of native model: %v", v)
			}
			session := i.NormalizeSession(Object{"known": true}, v, Object{"status": "ok"}, Object{}, nil, nil, nil)
			m := object(object(session["actor"])["model"])
			if v["configured_model_source"] != "env:CODEX_MODEL" || m["configured"] != "misleading-default" || m["configured_source"] != "env:CODEX_MODEL" || m["source"] != v["model_source"] {
				t.Fatalf("configured source lost or replaced native evidence: %v", session)
			}
			if want && m["id"] != "observed-model" || !want && m["id"] != "unknown" || (object(session["readiness"])["commit"] == true) != want {
				t.Fatalf("hint provenance changed model readiness: %v", session)
			}
			if tc == "long-turn" && v["model_source"] != "codex-thread-state" {
				t.Fatalf("long-turn fallback: %v", v)
			}
			if body := string(encoded(t, v)); strings.Contains(body, "PRIVATE-DIALOG") || strings.Contains(body, i.Home) {
				t.Fatal("identity leaked native source content or paths")
			}
		})
	}
}

func TestCodexConcurrentObservation(t *testing.T) {
	for _, tc := range []string{"mtime-advances", "prefix-completes", "record-completes", "still-partial", "future-clock", "malformed"} {
		t.Run(tc, func(t *testing.T) {
			i, _ := testInspector(t, "codex")
			now := i.Now()
			path := filepath.Join(i.Home, ".codex/sessions/2026/01/01/rollout-fixture-thread-one.jsonl")
			record := func(kind, payload string) string {
				return `{"timestamp":` + strconv.Quote(now.Format(time.RFC3339Nano)) + `,"type":` + strconv.Quote(kind) + `,"payload":` + payload + "}\n"
			}
			data := record("session_meta", `{"id":"thread-one"}`) + record("event_msg", `{"type":"task_started","turn_id":"turn-one"}`)
			data += record("turn_context", `{"turn_id":"turn-one","model":"older-model"}`)
			initial, mtime := data, now
			switch tc {
			case "mtime-advances":
				mtime = now.Add(time.Millisecond)
			case "prefix-completes", "still-partial":
				initial += `{"timestamp":`
			case "record-completes":
				initial += `{"timestamp":` + strconv.Quote(now.Format(time.RFC3339Nano)) + `,"type":"turn_context","payload":`
			case "future-clock":
				mtime = now.Add(10 * time.Second)
			case "malformed":
				initial += `{"timestamp":INVALID}`
			}
			writeFixture(t, path, []byte(initial), mtime)
			refreshes := 0
			i.Now = func() time.Time {
				refreshes++
				advanced := now.Add(20 * time.Millisecond)
				if tc == "mtime-advances" || tc == "prefix-completes" || tc == "record-completes" {
					writeFixture(t, path, []byte(strings.ReplaceAll(data, "older-model", "current-model")), advanced)
				}
				return advanced
			}
			found, reason := i.codex("thread-one", i.Processes[1], now)
			want := tc == "mtime-advances" || tc == "prefix-completes" || tc == "record-completes"
			if want {
				if found["model"] != "current-model" || reason != "" || refreshes != 1 {
					t.Fatalf("did not reread the completed native observation: %v %q refreshes=%d", found, reason, refreshes)
				}
			} else if found != nil || tc == "malformed" && (reason != "native-metadata-invalid" || refreshes != 0) ||
				tc != "malformed" && (reason != "native-observation-in-progress" || refreshes != 2) {
				t.Fatalf("unresolved observation reused an older model or retried indefinitely: %v %q refreshes=%d", found, reason, refreshes)
			}
		})
	}
}

func TestClaudeCurrentCaller(t *testing.T) {
	for _, tc := range []string{"current", "tool-cd", "wrong-session", "wrong-cwd", "sidechain", "latest-missing-model", "old", "future", "partial", "malformed", "symlink", "oversized"} {
		t.Run(tc, func(t *testing.T) {
			i, env := testInspector(t, "claude-code")
			now := i.Now()
			env["CLAUDE_CODE_SESSION_ID"] = "12345678-1234-1234-1234-123456789abc"
			env["ANTHROPIC_MODEL"] = "misleading-default"
			cwd := i.Directory
			row := Object{"type": "assistant", "sessionId": env["CLAUDE_CODE_SESSION_ID"], "cwd": cwd,
				"timestamp": now.Format(time.RFC3339Nano), "uuid": "assistant-one", "isSidechain": false,
				"message": Object{"model": "observed-model", "content": []any{Object{"text": "PRIVATE-DIALOG-SENTINEL"}}}}
			path := filepath.Join(i.Home, ".claude/projects", regexp.MustCompile(`[^a-zA-Z0-9]`).ReplaceAllString(cwd, "-"), env["CLAUDE_CODE_SESSION_ID"]+".jsonl")
			initial := string(encoded(t, row)) + "\n"
			suffix := ""
			switch tc {
			case "tool-cd":
				i.Directory = filepath.Join(cwd, "child")
				i.ProcessCwd = func(Process) (string, error) { return cwd, nil }
			case "wrong-session":
				row["sessionId"] = "other"
			case "wrong-cwd":
				row["cwd"] = filepath.Join(cwd, "other")
			case "sidechain":
				row["isSidechain"] = true
			case "latest-missing-model":
				row["message"] = Object{"model": nil}
			case "old":
				row["timestamp"] = now.Add(-301 * time.Second).Format(time.RFC3339Nano)
			case "future":
				row["timestamp"] = now.Add(10 * time.Second).Format(time.RFC3339Nano)
			case "partial":
				suffix = `{"type":"assistant","message":`
			case "malformed":
				suffix = "not-json\n"
			case "oversized":
				row["message"] = Object{"model": "new-model", "content": strings.Repeat("x", maxRecordBytes)}
			}
			if tc != "latest-missing-model" {
				initial = ""
			}
			writeFixture(t, path, []byte(initial+string(encoded(t, row))+"\n"+suffix), now)
			if tc == "symlink" {
				if runtime.GOOS == "windows" {
					t.Skip("Windows symlink privilege is not part of reader tests")
				}
				os.Rename(path, path+".saved")
				if err := os.Symlink(path+".saved", path); err != nil {
					t.Fatal(err)
				}
			}
			v := i.Inspect()
			want := tc == "current" || tc == "tool-cd"
			if (v["current_model_confirmed"] == true) != want {
				t.Fatalf("%v\n%v", v, i.Diagnose())
			}
			if (text(v["model_reason_code"]) == "") != want {
				t.Fatalf("lost the same observation's failure reason: %v", v)
			}
			session := i.NormalizeSession(Object{"known": true}, v, Object{"status": "ok"}, Object{}, nil, nil, nil)
			if object(object(session["actor"])["model"])["automatic_reason_code"] != v["model_reason_code"] {
				t.Fatalf("session discarded the observation reason: %v", session)
			}
			if strings.Contains(string(encoded(t, v)), "PRIVATE-DIALOG") {
				t.Fatal("conversation body appeared in result")
			}
		})
	}
}

func TestMinimaxLease(t *testing.T) {
	i, _ := testInspector(t, "minimax-code")
	db := fixtureDB(t, filepath.Join(i.Home, ".minimax/v2/sqlite/runtime-state.sqlite"))
	sqlFixture(t, db, "CREATE TABLE local_runtime_session_locks(session_id TEXT,owner_id TEXT,owner_kind TEXT,expires_at_ms INTEGER)")
	sqlFixture(t, db, "CREATE TABLE local_runtime_token_usage(session_id TEXT,model TEXT,ts INTEGER,turn_id TEXT)")
	sqlFixture(t, db, "INSERT INTO local_runtime_session_locks VALUES(?,?,?,?)", "session-one", "turn-lease:4200:one", "turn", i.Now().Add(time.Minute).UnixMilli())
	sqlFixture(t, db, "INSERT INTO local_runtime_token_usage VALUES(?,?,?,?)", "session-one", "provider/actual-model", i.Now().UnixMilli(), "turn-one")
	if v := i.Inspect(); v["model"] != "actual-model" || v["current_model_confirmed"] != true {
		t.Fatalf("lease not observed: %v\n%v", v, i.Diagnose())
	}
	sqlFixture(t, db, "INSERT INTO local_runtime_session_locks VALUES(?,?,?,?)", "session-two", "turn-lease:4200:two", "turn", i.Now().Add(time.Minute).UnixMilli())
	if i.Inspect()["current_model_confirmed"] != false {
		t.Fatal("ambiguous conversation accepted")
	}
	sqlFixture(t, db, "DELETE FROM local_runtime_session_locks WHERE session_id='session-two'")
	sqlFixture(t, db, "UPDATE local_runtime_session_locks SET owner_id='turn-lease:9999:foreign'")
	if i.Inspect()["current_model_confirmed"] != false {
		t.Fatal("foreign process lease accepted")
	}
}

func TestDshExactEntryAndResponse(t *testing.T) {
	i, env := testInspector(t, "dsh")
	p := &i.Processes[1]
	p.Name = "node"
	env["DSH_SESSION_ID"], env["DSH_SHELL"], env["DSH_RUNTIME_PID"], env["DSH_HOME"] = "session-one", "1", "4200", i.Home
	path := filepath.Join(i.Home, "runtime/everagent-identity/4200-native/call.json")
	env["DSH_IDENTITY_RECEIPT"] = path
	i.ProcessArgs = func(pid int) ([]string, error) {
		if pid != 4200 {
			t.Fatalf("non-caller PID queried: %d", pid)
		}
		return []string{"node", "/fixture/node_modules/@deepseek-ai/dsh/lib/bin.js", "web"}, nil
	}
	v := Object{"schema_version": 1, "pid": 4200, "session": "session-one", "model": "response-model", "requested_model": "requested-alias", "turn": 1, "step": 2, "call": "call-one", "observed_at": seconds(i.Now())}
	writeFixture(t, path, encoded(t, v), i.Now())
	if runtime.GOOS == "windows" {
		if i.Inspect()["current_model_confirmed"] != false {
			t.Fatal("Windows unimplemented native argv reader accepted")
		}
		return
	}
	if got := i.Inspect(); got["model"] != "response-model" || got["requested_model"] != "requested-alias" || got["current_model_confirmed"] != true {
		t.Fatalf("valid DSH response unavailable: %v\n%v", got, i.Diagnose())
	}
	for _, patch := range []Object{{"pid": 9999}, {"session": "foreign"}, {"observed_at": seconds(i.Now().Add(-301 * time.Second))}, {"model": nil}} {
		changed := clone(v)
		for key, val := range patch {
			changed[key] = val
		}
		writeFixture(t, path, encoded(t, changed), i.Now())
		if i.Inspect()["current_model_confirmed"] != false {
			t.Fatalf("invalid DSH receipt accepted: %v", patch)
		}
	}
	i.ProcessArgs = func(int) ([]string, error) { return []string{"node", "/fixture/unrelated.js", "web"}, nil }
	writeFixture(t, path, encoded(t, v), i.Now())
	if i.Inspect()["current_model_confirmed"] != false {
		t.Fatal("generic Node process accepted as DSH")
	}
}

func TestOpenCodeV1ToolBoundRequest(t *testing.T) {
	for _, tc := range []string{"current", "missing-hook", "wrong-pid", "wrong-call", "wrong-session", "completed-tool", "foreign-message", "duplicate-call", "wrong-cwd", "unsupported-version", "stale-tool", "future-tool", "malformed", "oversized"} {
		t.Run(tc, func(t *testing.T) {
			i, env := testInspector(t, "opencode")
			env["OPENCODE"], env["OPENCODE_SESSION_ID"], env["OPENCODE_CALL_ID"], env["OPENCODE_RUNTIME_PID"] = "1", "ses_current", "call_current", "4200"
			at := i.Now().Add(-2 * time.Second).UnixMilli()
			started := i.Now().Add(-time.Second).UnixMilli()
			if tc == "stale-tool" {
				i.Processes[1].StartTime = i.Now().Add(-10 * time.Minute)
				at, started = i.Now().Add(-302*time.Second).UnixMilli(), i.Now().Add(-301*time.Second).UnixMilli()
			}
			if tc == "future-tool" {
				started = i.Now().Add(time.Second).UnixMilli()
			}
			db := fixtureDB(t, filepath.Join(i.Home, ".local/share/opencode/opencode.db"))
			sqlFixture(t, db, `CREATE TABLE session(id TEXT PRIMARY KEY,directory TEXT,version TEXT,workspace_id TEXT,time_archived INTEGER,time_compacting INTEGER)`)
			sqlFixture(t, db, `CREATE TABLE message(id TEXT PRIMARY KEY,session_id TEXT REFERENCES session(id),time_created INTEGER,time_updated INTEGER,data TEXT)`)
			sqlFixture(t, db, `CREATE TABLE part(id TEXT PRIMARY KEY,message_id TEXT REFERENCES message(id),session_id TEXT,time_created INTEGER,time_updated INTEGER,data TEXT)`)
			sqlFixture(t, db, `CREATE TABLE session_message(id TEXT PRIMARY KEY,session_id TEXT REFERENCES session(id))`)
			sqlFixture(t, db, `INSERT INTO session VALUES(?,?,?,NULL,NULL,NULL)`, "ses_current", i.Directory, "1.18.32")
			message := Object{"role": "assistant", "modelID": "requested-alias", "providerID": "provider", "variant": "high", "path": Object{"cwd": i.Directory}, "time": Object{"created": at}, "text": "PRIVATE-DIALOG-SENTINEL"}
			part := Object{"type": "tool", "tool": "bash", "callID": "call_current", "state": Object{"status": "running", "time": Object{"start": started}, "input": Object{"command": "PRIVATE-COMMAND-SENTINEL"}}}
			switch tc {
			case "missing-hook":
				delete(env, "OPENCODE_CALL_ID")
			case "wrong-pid":
				env["OPENCODE_RUNTIME_PID"] = "9999"
			case "wrong-call":
				env["OPENCODE_CALL_ID"] = "call_another"
			case "wrong-session":
				env["OPENCODE_SESSION_ID"] = "ses_another"
			case "completed-tool":
				object(part["state"])["status"] = "completed"
			case "wrong-cwd":
				object(message["path"])["cwd"] = filepath.Join(i.Directory, "another")
			case "unsupported-version":
				sqlFixture(t, db, `UPDATE session SET version='1.99.0'`)
			case "oversized":
				message["text"] = strings.Repeat("x", maxRecordBytes)
			}
			data := encoded(t, message)
			if tc == "malformed" {
				data = []byte(`{"role":`)
			}
			sqlFixture(t, db, `INSERT INTO message VALUES(?,?,?,?,?)`, "msg_current", "ses_current", at, at, string(data))
			sqlFixture(t, db, `INSERT INTO part VALUES(?,?,?,?,?,?)`, "prt_current", "msg_current", "ses_current", started, started, string(encoded(t, part)))
			if tc == "foreign-message" {
				sqlFixture(t, db, `UPDATE message SET session_id='ses_foreign'`)
			}
			if tc == "duplicate-call" {
				sqlFixture(t, db, `INSERT INTO part SELECT 'prt_duplicate',message_id,session_id,time_created,time_updated,data FROM part`)
			}
			got := i.Inspect()
			if got["current_model_confirmed"] != false || got["commit_ready"] != false || got["observed_model"] != nil {
				t.Fatalf("request became actual-model/commit proof: %v", got)
			}
			if tc == "current" {
				observation := object(got["request_observation"])
				if got["requested_model"] != "requested-alias" || observation["binding"] != "active-tool" || observation["storage_version"] != "1.18.32" || got["model_reason_code"] != "provider-response-model-unavailable" {
					t.Fatalf("active call unavailable: %v\n%v", got, i.Diagnose())
				}
				owners := string(encoded(t, object(i.Diagnose()["repair"])["owners"]))
				if !strings.Contains(owners, "packages/everagent-core/opencode.go") || !strings.Contains(owners, "identity/opencode_plugin.mjs") {
					t.Fatal("diagnose does not point to the applicable reader and binding adapter")
				}
			} else if got["requested_model"] != nil {
				t.Fatalf("borrowed unbound request: %v", got)
			}
			if strings.Contains(string(encoded(t, got)), "PRIVATE-") {
				t.Fatal("body/arguments escaped scalar projection")
			}
		})
	}
}

func TestOpenCodeV2RequestedOnly(t *testing.T) {
	for _, version := range []string{"2.0.27", "2.2.5"} {
		t.Run(version, func(t *testing.T) {
			i, env := testInspector(t, "opencode")
			env["OPENCODE"], env["OPENCODE_SESSION_ID"] = "1", "ses_current"
			db := fixtureDB(t, filepath.Join(i.Home, ".local/share/opencode/opencode.db"))
			sqlFixture(t, db, `CREATE TABLE session_v2(id TEXT PRIMARY KEY,directory TEXT,version TEXT,workspace_id TEXT,fork_session_id TEXT,model TEXT)`)
			sqlFixture(t, db, `CREATE TABLE session_message(id TEXT PRIMARY KEY,session_id TEXT REFERENCES session_v2(id),type TEXT,seq INTEGER,time_created INTEGER,time_updated INTEGER,data TEXT)`)
			at := i.Now().Add(-time.Second).UnixMilli()
			selected := Object{"id": "requested-alias", "providerID": "provider"}
			sqlFixture(t, db, `INSERT INTO session_v2 VALUES(?,?,?,NULL,NULL,?)`, "ses_current", i.Directory, version, string(encoded(t, selected)))
			message := Object{"model": selected, "time": Object{"created": at, "streamed": at}, "text": "PRIVATE-DIALOG-SENTINEL"}
			sqlFixture(t, db, `INSERT INTO session_message VALUES(?,?,'assistant',1,?,?,?)`, "msg_current", "ses_current", at, at, string(encoded(t, message)))
			got := i.Inspect()
			if got["requested_model"] != "requested-alias" || got["current_model_confirmed"] != false || got["commit_ready"] != false || strings.Contains(string(encoded(t, got)), "PRIVATE-") {
				t.Fatalf("V2 boundary regressed: %v\n%v", got, i.Diagnose())
			}
		})
	}
}
