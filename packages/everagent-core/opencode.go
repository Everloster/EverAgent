package core

import (
	"context"
	"database/sql"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

// V2's model/time projection is shared by the independently inspected 2.0.27
// and 2.2.5 releases. Their part storage differs, but no body is read here.
// V1 has a separate schema and requires the official shell.env adapter below.
func opencodeSnapshot(ctx context.Context, db *sql.DB, native, cwd string) (Object, error) {
	tx, e := db.BeginTx(ctx, &sql.TxOptions{ReadOnly: true})
	if e != nil {
		return nil, e
	}
	defer tx.Rollback()
	rows, e := queryRows(ctx, tx, `SELECT version,model IS NOT NULL AS selected,
CASE WHEN length(model)<=4096 AND json_valid(model) THEN json_extract(model,'$.id') END AS model,
CASE WHEN length(model)<=4096 AND json_valid(model) THEN json_extract(model,'$.providerID') END AS provider,
CASE WHEN length(model)<=4096 AND json_valid(model) THEN json_extract(model,'$.variant') END AS variant
FROM session_v2 WHERE id=? AND directory=? AND workspace_id IS NULL AND fork_session_id IS NULL LIMIT 1`, native, cwd)
	if e != nil || len(rows) != 1 {
		return nil, e
	}
	own := rows[0]
	if !contains([]string{"2.0.27", "2.2.5"}, text(own["version"])) {
		return nil, nil
	}
	moved, e := queryRows(ctx, tx, "SELECT 1 FROM session_message WHERE session_id=? AND type='location-switched' LIMIT 1", native)
	if e != nil || len(moved) != 0 {
		return nil, e
	}
	paths := []string{"$.model.id", "$.model.providerID", "$.model.variant", "$.time.created", "$.time.streamed", "$.time.completed"}
	names := []string{"model", "provider", "variant", "created_at", "streamed", "completed"}
	expressions := []string{}
	args := []any{}
	for n, path := range paths {
		expressions = append(expressions, "CASE WHEN length(data)<=? THEN CASE WHEN json_valid(data) THEN json_extract(data,?) END END AS "+names[n])
		args = append(args, maxRecordBytes, path)
	}
	args = append(args, maxRecordBytes, native)
	rows, e = queryRows(ctx, tx, "SELECT id,time_created,time_updated,length(data) AS size,"+strings.Join(expressions, ",")+",CASE WHEN length(data)<=? THEN CASE WHEN json_valid(data) THEN json_type(data,'$.error') END END AS error FROM session_message WHERE session_id=? AND type='assistant' ORDER BY seq DESC LIMIT 1", args...)
	if e != nil || len(rows) != 1 {
		return nil, e
	}
	return Object{"session": own, "message": rows[0]}, nil
}

// V1 stores modelID on the assistant as a REQUEST, not a provider response.
// Bind through the exact running call, never the latest session in a directory.
// SQL projects scalars only; tool arguments and conversation bodies stay in DB.
func opencodeV1Snapshot(ctx context.Context, db *sql.DB, native, cwd, call string) (Object, error) {
	tx, e := db.BeginTx(ctx, &sql.TxOptions{ReadOnly: true})
	if e != nil {
		return nil, e
	}
	defer tx.Rollback()
	rows, e := queryRows(ctx, tx, `SELECT version FROM session WHERE id=? AND directory=?
AND workspace_id IS NULL AND time_archived IS NULL AND time_compacting IS NULL LIMIT 1`, native, cwd)
	if e != nil || len(rows) != 1 || rows[0]["version"] != "1.18.32" {
		return nil, e
	}
	own := rows[0]
	rows, e = queryRows(ctx, tx, `SELECT p.id,p.message_id,p.time_created,p.time_updated,
json_extract(p.data,'$.state.time.start') AS started
FROM part p JOIN message m ON m.id=p.message_id AND m.session_id=p.session_id
WHERE p.session_id=? AND CASE WHEN length(p.data)<=? AND json_valid(p.data) THEN
json_extract(p.data,'$.type')='tool' AND json_extract(p.data,'$.callID')=?
AND json_extract(p.data,'$.tool')='bash' AND json_extract(p.data,'$.state.status')='running' END LIMIT 2`, native, maxRecordBytes, call)
	if e != nil || len(rows) != 1 {
		return nil, e
	}
	tool := rows[0]
	rows, e = queryRows(ctx, tx, `SELECT id,time_created,time_updated,
json_extract(data,'$.role') AS role,json_extract(data,'$.modelID') AS model,
json_extract(data,'$.providerID') AS provider,json_extract(data,'$.variant') AS variant,
json_extract(data,'$.time.created') AS created_at,json_extract(data,'$.time.completed') AS completed,
json_extract(data,'$.path.cwd') AS cwd,json_type(data,'$.error') AS error
FROM message WHERE id=? AND session_id=? AND CASE WHEN length(data)<=? THEN json_valid(data) END LIMIT 1`, tool["message_id"], native, maxRecordBytes)
	if e != nil || len(rows) != 1 {
		return nil, e
	}
	return Object{"session": own, "message": rows[0], "tool": tool}, nil
}

func opencodeForeignKey(ctx context.Context, db *sql.DB, table, column, target string) bool {
	rows, e := queryRows(ctx, db, "PRAGMA foreign_key_list("+table+")")
	if e != nil {
		return false
	}
	for _, row := range rows {
		if row["from"] == column && row["table"] == target && row["to"] == "id" {
			return true
		}
	}
	return false
}

func (i *Inspector) opencodeV1(ctx context.Context, db *sql.DB, native, cwd string, p Process, now time.Time) (Object, string) {
	call := i.Getenv("OPENCODE_CALL_ID")
	if !nativePattern.MatchString(call) || i.Getenv("OPENCODE_RUNTIME_PID") != strconv.Itoa(p.PID) {
		return nil, "native-tool-binding-unavailable"
	}
	snapshot, e := opencodeV1Snapshot(ctx, db, native, cwd, call)
	if e != nil || snapshot == nil {
		return nil, "native-tool-metadata-unavailable"
	}
	again, e := opencodeV1Snapshot(ctx, db, native, cwd, call)
	if e != nil || Digest(snapshot) != Digest(again) {
		return nil, "native-observation-in-progress"
	}
	row, tool := object(snapshot["message"]), object(snapshot["tool"])
	validMS := func(v any) bool { n := number(v); return n >= seconds(p.StartTime)*1000 && n <= seconds(now)*1000 }
	valid := row["role"] == "assistant" && row["cwd"] == cwd && model(row["model"]) != "" && model(row["provider"]) != "" &&
		(row["variant"] == nil || model(row["variant"]) != "") && (row["error"] == nil || row["error"] == "null") && row["completed"] == nil &&
		number(row["created_at"]) <= number(tool["started"]) && seconds(now)-number(tool["started"])/1000 <= 300
	for _, entry := range []Object{row, tool} {
		valid = valid && validMS(entry["time_created"]) && validMS(entry["time_updated"]) && number(entry["time_created"]) <= number(entry["time_updated"])
	}
	if !valid || !validMS(row["created_at"]) || !validMS(tool["started"]) {
		return nil, "native-request-metadata-incomplete-or-stale"
	}
	return Object{"model": row["model"], "requested_model": row["model"], "source": "opencode-session-request",
		"observed_at": number(tool["started"]) / 1000, "turn": []any{row["id"], tool["id"], call},
		"request_metadata": Object{"provider_id": row["provider"], "variant": row["variant"], "step_completed": false,
			"storage_version": object(snapshot["session"])["version"], "binding": "active-tool"}}, ""
}

func (i *Inspector) opencode(native string, p Process, now time.Time) (Object, string) {
	if i.Getenv("OPENCODE") != "1" || !strings.HasPrefix(native, "ses_") {
		return nil, "native-tool-context-unavailable"
	}
	cwd := i.Directory
	if i.callerCwd(p) != cwd {
		return nil, "native-cwd-binding-unavailable"
	}
	override := ""
	if x := i.Getenv("XDG_DATA_HOME"); x != "" {
		override = filepath.Join(x, "opencode")
	}
	root := i.root("opencode", override)
	selected := i.Getenv("OPENCODE_DB")
	if selected == ":memory:" || root == "" {
		return nil, "native-database-unavailable"
	}
	database := filepath.Join(root, "opencode.db")
	if selected != "" {
		if filepath.IsAbs(selected) {
			database = selected
		} else if regexp.MustCompile(`^[A-Za-z0-9_.-]+\.db$`).MatchString(selected) {
			database = filepath.Join(root, selected)
		} else {
			return nil, "native-database-path-unverified"
		}
	}
	if database != realPath(database) || !regular(database, false) {
		return nil, "native-database-unavailable"
	}
	before, e := os.Stat(database)
	if e != nil {
		return nil, "native-database-unavailable"
	}
	db, e := openReadDB(database)
	if e != nil {
		return nil, "native-database-unavailable"
	}
	defer db.Close()
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	types, e := queryRows(ctx, db, "SELECT name,type FROM sqlite_master WHERE name IN ('session','message','part','session_v2','session_message')")
	if e != nil {
		return nil, "native-schema-unsupported"
	}
	tables := map[string]bool{}
	for _, r := range types {
		tables[text(r["name"])] = r["type"] == "table"
	}
	if !tables["session_v2"] && tables["session"] && tables["message"] && tables["part"] && tables["session_message"] &&
		opencodeForeignKey(ctx, db, "message", "session_id", "session") && opencodeForeignKey(ctx, db, "part", "message_id", "message") &&
		opencodeForeignKey(ctx, db, "session_message", "session_id", "session") {
		found, reason := i.opencodeV1(ctx, db, native, cwd, p, now)
		after, err := os.Stat(database)
		if err != nil || !os.SameFile(before, after) || i.callerCwd(p) != cwd || i.nativeID("opencode") != native {
			return nil, "native-caller-changed"
		}
		return found, reason
	}
	// Transitional session_message can point to V1; table names are not proof.
	if !tables["session_v2"] || !tables["session_message"] || !opencodeForeignKey(ctx, db, "session_message", "session_id", "session_v2") {
		return nil, "native-schema-unsupported"
	}
	snapshot, e := opencodeSnapshot(ctx, db, native, cwd)
	if e != nil || snapshot == nil {
		return nil, "native-session-metadata-unavailable"
	}
	repeated, e := opencodeSnapshot(ctx, db, native, cwd)
	if e != nil || Digest(snapshot) != Digest(repeated) {
		return nil, "native-observation-in-progress"
	}
	after, e := os.Stat(database)
	if e != nil || !os.SameFile(before, after) || i.callerCwd(p) != cwd || i.nativeID("opencode") != native {
		return nil, "native-caller-changed"
	}
	own, row := object(snapshot["session"]), object(snapshot["message"])
	m, provider, variant := model(row["model"]), model(row["provider"]), model(row["variant"])
	created, updated, at, streamed := number(row["time_created"]), number(row["time_updated"]), number(row["created_at"]), number(row["streamed"])
	validMS := func(v any) bool { n := number(v); return n >= seconds(p.StartTime)*1000 && n <= seconds(now)*1000 }
	valid := regexp.MustCompile(`^msg_[A-Za-z0-9_-]{1,128}$`).MatchString(text(row["id"])) && number(row["size"]) <= maxRecordBytes && m != "" && provider != "" && (row["variant"] == nil || variant != "") && (row["error"] == nil || row["error"] == "null") && created == at && at <= streamed && streamed <= updated && seconds(now)-streamed/1000 <= 300
	for _, key := range []string{"time_created", "time_updated", "created_at", "streamed"} {
		valid = valid && validMS(row[key])
	}
	if row["completed"] != nil {
		n := number(row["completed"])
		valid = valid && validMS(row["completed"]) && streamed <= n && n <= updated
	}
	if !valid {
		return nil, "native-request-metadata-incomplete-or-stale"
	}
	selectedVariant := model(own["variant"])
	if selectedVariant == "" && own["variant"] != nil {
		return nil, "native-request-selection-changed"
	}
	if selectedVariant == "" {
		selectedVariant = "default"
	}
	if variant == "" {
		variant = "default"
	}
	if number(own["selected"]) != 0 && (own["model"] != m || own["provider"] != provider || selectedVariant != variant) {
		return nil, "native-request-selection-changed"
	}
	return Object{"model": m, "requested_model": m, "source": "opencode-session-request", "observed_at": streamed / 1000, "turn": []any{row["id"], row["time_updated"]}, "request_metadata": Object{"provider_id": provider, "variant": row["variant"], "step_completed": row["completed"] != nil, "storage_version": own["version"]}}, ""
}
