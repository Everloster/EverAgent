package core

import (
	"context"
	"encoding/json"
	"errors"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/coder/websocket"
)

func (i *Inspector) minimax(p Process, now time.Time) (Object, error) {
	root := i.root("minimax-code", "")
	if root == "" {
		return nil, nil
	}
	path := filepath.Join(root, "sqlite/runtime-state.sqlite")
	if !within(path, root) {
		return nil, nil
	}
	db, e := openReadDB(path)
	if e != nil {
		return nil, e
	}
	defer db.Close()
	ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
	defer cancel()
	pids := map[int]bool{}
	for _, p := range i.Processes {
		pids[p.PID] = true
	}
	locks, e := queryRows(ctx, db, "SELECT session_id,owner_id,expires_at_ms FROM local_runtime_session_locks WHERE owner_kind='turn'")
	if e != nil {
		return nil, e
	}
	held := []string{}
	lease := regexp.MustCompile(`^turn-lease:(\d+):`)
	for _, r := range locks {
		match := lease.FindStringSubmatch(text(r["owner_id"]))
		if match == nil {
			continue
		}
		pid, _ := strconv.Atoi(match[1])
		if pids[pid] && number(r["expires_at_ms"]) > seconds(now)*1000 {
			held = append(held, text(r["session_id"]))
		}
	}
	if len(held) != 1 {
		return nil, nil
	}
	rows, e := queryRows(ctx, db, "SELECT model,ts,turn_id FROM local_runtime_token_usage WHERE session_id=? ORDER BY ts DESC LIMIT 1", held[0])
	if e != nil || len(rows) != 1 {
		return nil, e
	}
	row := rows[0]
	at := time.UnixMilli(int64(number(row["ts"])))
	parts := strings.Split(text(row["model"]), "/")
	m := model(parts[len(parts)-1])
	if m == "" || !afterStart(at, p) || !fresh(at, now) {
		return nil, nil
	}
	return Object{"model": m, "source": "minimax-session-runtime", "session": held[0], "turn": row["turn_id"]}, nil
}

func (i *Inspector) kimiCLI(p Process, now time.Time) (Object, error) {
	cwd := i.callerCwd(p)
	if cwd == "" {
		return nil, nil
	}
	executable, e := exec.LookPath("kimi")
	if e != nil {
		return nil, e
	}
	b, e := boundedCommand("", nil, 2*time.Second, 1<<20, executable, "session", "list", "--cwd", cwd, "--limit", "16", "--json")
	if e != nil {
		return nil, e
	}
	rawDirs := regexp.MustCompile(`"sessionDir"\s*:\s*("(?:\\.|[^"\\])*")`).FindAllSubmatch(b, 17)
	if len(rawDirs) < 1 || len(rawDirs) > 16 {
		return nil, nil
	}
	root := i.root("kimi-cli", "")
	if root == "" {
		return nil, nil
	}
	seen := map[string]bool{}
	candidates := []string{}
	for _, raw := range rawDirs {
		var dir string
		if json.Unmarshal(raw[1], &dir) != nil || !filepath.IsAbs(dir) {
			return nil, nil
		}
		if seen[dir] {
			continue
		}
		seen[dir] = true
		if s, e := os.Lstat(dir); e != nil || !s.IsDir() {
			return nil, nil
		}
		if !within(dir, root) {
			return nil, nil
		}
		b, e := readSmall(filepath.Join(dir, "state.json"), 1<<20, false)
		if e != nil {
			return nil, e
		}
		state, e := metadata(b, "id", "cwd", "createdAt", "updatedAt", "archived")
		if e != nil {
			return nil, e
		}
		created, updated := number(state["createdAt"])/1000, number(state["updatedAt"])/1000
		if created <= 0 || updated <= 0 {
			return nil, nil
		}
		if state["archived"] != false || state["id"] != filepath.Base(dir) || text(state["cwd"]) == "" || realPath(text(state["cwd"])) != cwd || created > seconds(now)+2 || updated < seconds(p.StartTime)-2 || updated > seconds(now)+2 {
			continue
		}
		candidates = append(candidates, dir)
	}
	if len(candidates) != 1 {
		return nil, nil
	}
	dir := candidates[0]
	path := filepath.Join(dir, "agents/main/wire.jsonl")
	if !within(path, root) {
		return nil, nil
	}
	lines, _, stable, e := tail(path, maxTailBytes)
	if e != nil || !stable {
		return nil, e
	}
	var request Object
	for n := len(lines) - 1; n >= 0; n-- {
		raw := lines[n]
		if !strings.Contains(string(raw), "llm.request") {
			continue
		}
		if len(raw) > maxRecordBytes {
			return nil, nil
		}
		r, e := kimiRecord(raw)
		if e != nil {
			return nil, e
		}
		if r["type"] == "llm.request" {
			request = r
			break
		}
	}
	at := time.UnixMilli(int64(number(request["time"])))
	m := model(request["model"])
	step := text(request["turnStep"])
	if request["kind"] != "loop" || m == "" || !regexp.MustCompile(`^[A-Za-z0-9._:-]{1,128}$`).MatchString(step) || !afterStart(at, p) || !fresh(at, now) || request["modelAlias"] != nil && model(request["modelAlias"]) == "" {
		return nil, nil
	}
	return Object{"model": m, "source": "kimi-cli-session-runtime", "observed_at": seconds(at), "turn": step, "session": filepath.Base(dir)}, nil
}
func kimiRecord(raw []byte) (Object, error) {
	return metadata(raw, "type", "model", "time", "usageScope", "kind", "provider", "modelAlias", "turnStep")
}

func (i *Inspector) dsh(native string, p Process, now time.Time) (Object, error) {
	root, path := i.Getenv("DSH_HOME"), i.Getenv("DSH_IDENTITY_RECEIPT")
	if i.Getenv("DSH_SHELL") != "1" || !filepath.IsAbs(root) || !filepath.IsAbs(path) || i.Getenv("DSH_RUNTIME_PID") != strconv.Itoa(p.PID) {
		return nil, nil
	}
	base := filepath.Join(root, "runtime/everagent-identity")
	if !within(path, base) {
		return nil, nil
	}
	rel, e := filepath.Rel(realPath(base), realPath(path))
	if e != nil {
		return nil, e
	}
	parts := strings.Split(rel, string(filepath.Separator))
	if len(parts) != 2 || !strings.HasPrefix(parts[0], strconv.Itoa(p.PID)+"-") {
		return nil, nil
	}
	b, e := readSmall(path, 4096, true)
	if e != nil {
		return nil, e
	}
	var v Object
	if decode(b, &v) != nil {
		return nil, nil
	}
	at := time.UnixMicro(int64(number(v["observed_at"]) * 1e6))
	if number(v["schema_version"]) != 1 || number(v["pid"]) != float64(p.PID) || v["session"] != native || !afterStart(at, p) || !fresh(at, now) || model(v["model"]) == "" || model(v["requested_model"]) == "" || len(text(v["call"])) < 1 || len(text(v["call"])) > 256 {
		return nil, nil
	}
	for _, key := range []string{"turn", "step"} {
		n, ok := v[key].(json.Number)
		if !ok {
			return nil, nil
		}
		if _, e := n.Int64(); e != nil {
			return nil, nil
		}
	}
	return Object{"model": v["model"], "requested_model": v["requested_model"], "source": "dsh-tool-response", "observed_at": v["observed_at"], "turn": []any{v["turn"], v["step"], v["call"]}}, nil
}

type kimiTurn struct {
	Agent, Session, Conversation, Turn string
	At                                 time.Time
}
type kimiControl struct {
	endpoint, token string
	turns           []kimiTurn
}

func (i *Inspector) kimiRoot() string {
	root := i.Getenv("KIMI_SHARE_DIR")
	if root == "" && i.Home != "" {
		if os.PathSeparator == '\\' {
			app := i.Getenv("APPDATA")
			if app == "" {
				app = filepath.Join(i.Home, "AppData/Roaming")
			}
			root = filepath.Join(app, "kimi-desktop/daimon-share")
		} else {
			root = filepath.Join(i.Home, "Library/Application Support/kimi-desktop/daimon-share")
		}
	}
	root = expandHome(root, i.Home)
	if !filepath.IsAbs(root) {
		return ""
	}
	return realPath(root)
}
func (i *Inspector) kimiState(path string) (kimiControl, error) {
	b, e := readSmall(path, 1<<20, false)
	if e != nil {
		return kimiControl{}, e
	}
	state, e := metadata(b, "schemaVersion", "lifecycleStatus", "control", "daemonGeneration", "activeKernelTurns")
	if e != nil {
		return kimiControl{}, e
	}
	invalid := errors.New("native control state unavailable")
	if number(state["schemaVersion"]) != 1 || state["lifecycleStatus"] != "running" {
		return kimiControl{}, invalid
	}
	endpoint := object(object(state["control"])["endpoint"])
	pid := int(number(endpoint["pid"]))
	pids := map[int]bool{}
	for _, p := range i.Processes {
		pids[p.PID] = true
	}
	u, e := url.Parse(text(endpoint["url"]))
	if e != nil {
		return kimiControl{}, invalid
	}
	port, e := strconv.Atoi(u.Port())
	if u.Scheme != "ws" || !contains([]string{"127.0.0.1", "::1", "localhost"}, u.Hostname()) || u.User != nil || e != nil || port < 1 || port > 65535 || pid <= 1 || !pids[pid] || number(object(state["daemonGeneration"])["pid"]) != float64(pid) || text(object(endpoint["auth"])["token"]) == "" {
		return kimiControl{}, invalid
	}
	rows := array(state["activeKernelTurns"])
	if len(rows) < 1 || len(rows) > 16 {
		return kimiControl{}, invalid
	}
	out := kimiControl{endpoint: u.String(), token: text(object(endpoint["auth"])["token"])}
	sessions := map[string]bool{}
	for _, raw := range rows {
		row := object(raw)
		turn := text(row["turnId"])
		if n, ok := row["turnId"].(json.Number); ok {
			if _, e := n.Int64(); e == nil {
				turn = string(n)
			}
		}
		t := kimiTurn{text(row["ownerAgentId"]), text(row["kernelSessionId"]), text(row["conversationKey"]), turn, stamp(row["startedAt"])}
		valid := !t.At.IsZero()
		for _, v := range []string{t.Agent, t.Session, t.Conversation, t.Turn} {
			valid = valid && nativePattern.MatchString(v)
		}
		if !valid {
			continue
		}
		if sessions[t.Session] {
			return kimiControl{}, invalid
		}
		sessions[t.Session] = true
		out.turns = append(out.turns, t)
	}
	if len(out.turns) == 0 {
		return kimiControl{}, invalid
	}
	return out, nil
}

func kimiTasks(control kimiControl) (map[string][]Object, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	out := map[string][]Object{}
	// Never send the local control credential to a proxy, a redirect, or a
	// hostname resolved outside loopback. Credentials stay in this Go process.
	transport := &http.Transport{Proxy: nil, DialContext: func(ctx context.Context, network, address string) (net.Conn, error) {
		host, port, e := net.SplitHostPort(address)
		if e != nil || !contains([]string{"127.0.0.1", "::1", "localhost"}, host) {
			return nil, errors.New("nonlocal control refused")
		}
		if host == "localhost" {
			host = "127.0.0.1"
		}
		return (&net.Dialer{Timeout: time.Second}).DialContext(ctx, network, net.JoinHostPort(host, port))
	}}
	defer transport.CloseIdleConnections()
	client := &http.Client{Transport: transport, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	for n, turn := range control.turns {
		conn, _, e := websocket.Dial(ctx, control.endpoint, &websocket.DialOptions{HTTPClient: client, HTTPHeader: http.Header{"Authorization": []string{"Bearer " + control.token}}})
		if e != nil {
			return nil, errors.New("local control connection failed")
		}
		conn.SetReadLimit(1 << 20)
		id := "everagent-identity-" + strconv.Itoa(n)
		request := Object{"jsonrpc": "2.0", "id": id, "method": "backgroundTasks.list", "params": Object{"agentId": turn.Agent, "kernelSessionId": turn.Session, "activeOnly": true, "limit": 100}}
		b, _ := json.Marshal(request)
		e = conn.Write(ctx, websocket.MessageText, b)
		if e != nil {
			conn.CloseNow()
			return nil, errors.New("local control query failed")
		}
		var tasks []Object
		for messages := 0; messages < 32; messages++ {
			_, b, e = conn.Read(ctx)
			if e != nil {
				conn.CloseNow()
				return nil, errors.New("local control query failed")
			}
			var frame Object
			if decode(b, &frame) != nil {
				conn.CloseNow()
				return nil, errors.New("invalid local control response")
			}
			if frame["id"] != id {
				continue
			}
			if frame["error"] != nil {
				conn.CloseNow()
				return nil, errors.New("local control query rejected")
			}
			result := object(frame["result"])
			raw, ok := result["tasks"].([]any)
			if result["kernelSessionId"] != turn.Session || !ok || len(raw) > 100 {
				conn.CloseNow()
				return nil, errors.New("invalid task metadata")
			}
			tasks = []Object{}
			for _, value := range raw {
				t := object(value)
				tasks = append(tasks, Object{"kind": t["kind"], "status": t["status"], "pid": t["pid"], "startedAtMs": t["startedAtMs"]})
			}
			break
		}
		conn.CloseNow()
		if tasks == nil {
			return nil, errors.New("local control response absent")
		}
		out[turn.Session] = tasks
	}
	return out, nil
}
func (i *Inspector) kimiDesktop(p Process, now time.Time) (Object, error) {
	root := i.kimiRoot()
	if root == "" {
		return nil, nil
	}
	path := filepath.Join(root, "daimon/agents/main/runner.state.json")
	control, e := i.kimiState(path)
	if e != nil {
		return nil, e
	}
	queries, e := kimiTasks(control)
	if e != nil {
		return nil, e
	}
	ownShells := []Process{}
	for _, row := range i.Processes {
		if row.PID == p.PID {
			break
		}
		if shells[row.Name] && !row.StartTime.IsZero() {
			ownShells = append(ownShells, row)
		}
	}
	bound := []kimiTurn{}
	for _, turn := range control.turns {
		if !afterStart(turn.At, p) || turn.At.After(now.Add(2*time.Second)) {
			continue
		}
		for _, task := range queries[turn.Session] {
			if task["kind"] != "bash" || task["status"] != "running" {
				continue
			}
			pid := int(number(task["pid"]))
			at := time.UnixMilli(int64(number(task["startedAtMs"])))
			if at.Before(turn.At.Add(-2*time.Second)) || at.After(now.Add(2*time.Second)) {
				continue
			}
			for _, row := range ownShells {
				delta := at.Sub(row.StartTime)
				if row.PID == pid && delta >= -2*time.Second && delta <= 2*time.Second {
					bound = append(bound, turn)
				}
			}
		}
	}
	if len(bound) != 1 {
		return nil, nil
	}
	turn := bound[0]
	check, e := i.kimiState(path)
	if e != nil {
		return nil, e
	}
	found := false
	for _, t := range check.turns {
		if t == turn {
			found = true
		}
	}
	if !found || check.endpoint != control.endpoint || check.token != control.token {
		return nil, nil
	}
	m, e := i.kimiWire(root, turn, p, now)
	if e != nil || m == "" {
		return nil, e
	}
	return Object{"model": m, "source": "kimi-desktop-session-runtime", "session": turn.Session, "turn": turn.Turn}, nil
}
func (i *Inspector) kimiWire(root string, turn kimiTurn, p Process, now time.Time) (string, error) {
	db, e := openReadDB(filepath.Join(root, "daimon/agents/main/sessions/hosted-logical/conversations.sqlite"))
	if e != nil {
		return "", e
	}
	defer db.Close()
	ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
	defer cancel()
	rows, e := queryRows(ctx, db, "SELECT kernel_records_path,workspace_path FROM conversations WHERE kernel_session_id=? AND conversation_key=? AND agent_id=? LIMIT 2", turn.Session, turn.Conversation, turn.Agent)
	if e != nil || len(rows) != 1 {
		return "", e
	}
	records, workspace := text(rows[0]["kernel_records_path"]), text(rows[0]["workspace_path"])
	wireRoot := filepath.Join(root, "daimon/runtime/kimi-code/home/sessions")
	if !filepath.IsAbs(records) || !filepath.IsAbs(workspace) || !within(records, wireRoot) || !within(i.Directory, workspace) || !regular(records, false) {
		return "", nil
	}
	rel, e := filepath.Rel(realPath(wireRoot), realPath(records))
	if e != nil {
		return "", e
	}
	parts := strings.Split(rel, string(filepath.Separator))
	if len(parts) != 5 || parts[1] != turn.Session || strings.Join(parts[2:], "/") != "agents/main/wire.jsonl" {
		return "", nil
	}
	if !recentFile(records, now) {
		return "", nil
	}
	lines, _, stable, e := tail(records, maxTailBytes)
	if e != nil || !stable {
		return "", e
	}
	latest := map[string]Object{}
	envelope := regexp.MustCompile(`^\s*\{\s*"type"\s*:\s*"(usage\.record|llm\.request)"`)
	for n := len(lines) - 1; n >= 0; n-- {
		raw := lines[n]
		match := envelope.FindSubmatch(raw[:min(len(raw), 128)])
		if match == nil {
			continue
		}
		kind := string(match[1])
		if latest[kind] != nil {
			continue
		}
		if len(raw) > maxRecordBytes {
			return "", nil
		}
		row, e := kimiRecord(raw)
		if e != nil {
			return "", e
		}
		latest[kind] = row
		if len(latest) == 2 {
			break
		}
	}
	if len(latest) != 2 {
		return "", nil
	}
	usage, request := latest["usage.record"], latest["llm.request"]
	m := model(usage["model"])
	ua := time.UnixMilli(int64(number(usage["time"])))
	ra := time.UnixMilli(int64(number(request["time"])))
	delta := ua.Sub(ra)
	if usage["usageScope"] != "turn" || request["kind"] != "loop" || request["provider"] != "kimi" || m == "" || model(request["model"]) != m || request["modelAlias"] != nil && model(request["modelAlias"]) == "" || !afterStart(ua, p) || !fresh(ua, now) || ua.Before(turn.At.Add(-2*time.Second)) || ra.Before(turn.At.Add(-2*time.Second)) || delta > 2*time.Second || delta < -2*time.Second {
		return "", nil
	}
	return m, nil
}
