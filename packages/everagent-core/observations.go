package core

import (
	"bufio"
	"bytes"
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"io"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
	"unicode/utf8"

	_ "modernc.org/sqlite"
)

const maxTailBytes = 4 << 20
const maxRecordBytes = 128 << 10

var automaticReaders = map[string][]string{"codex": {"codex-turn-context", "codex-thread-state"}, "pi": {"pi-session-runtime"}, "trae": {"trae-thread-runtime"}, "claude-code": {"claude-session-runtime"}, "zcode": {"zcode-model-io"}, "minimax-code": {"minimax-session-runtime"}, "kimi-desktop": {"kimi-desktop-session-runtime"}, "kimi-cli": {"kimi-cli-session-runtime"}, "dsh": {"dsh-tool-response"}, "opencode": {"opencode-session-request"}}
var codexEnvelope = regexp.MustCompile(`^\s*\{\s*"timestamp"\s*:\s*"[^"\n]+"(?:\s*,\s*"ordinal"\s*:\s*\d+)?\s*,\s*"type"\s*:\s*"([^"]+)"\s*,\s*"payload"\s*:`)

// fields selects slices, not decoded conversation strings. json.Valid performs
// syntax checking without materializing unselected messages/tool arguments.
// Duplicate keys and excessive nesting are rejected, never last-key-wins.
func fields(raw []byte) (map[string][]byte, error) {
	if !utf8.Valid(raw) || !json.Valid(raw) {
		return nil, errors.New("metadata-invalid")
	}
	raw = bytes.TrimSpace(raw)
	if len(raw) < 2 || raw[0] != '{' {
		return nil, errors.New("metadata-not-object")
	}
	out := map[string][]byte{}
	n := len(raw)
	pos := 1
	space := func() {
		for pos < n && (raw[pos] == ' ' || raw[pos] == '\t' || raw[pos] == '\n' || raw[pos] == '\r') {
			pos++
		}
	}
	for {
		space()
		if pos >= n || raw[pos] == '}' {
			return out, nil
		}
		start := pos
		pos++
		for pos < n {
			if raw[pos] == '\\' {
				pos += 2
				continue
			}
			if raw[pos] == '"' {
				pos++
				break
			}
			pos++
		}
		var key string
		if e := json.Unmarshal(raw[start:pos], &key); e != nil {
			return nil, e
		}
		if _, exists := out[key]; exists {
			return nil, errors.New("metadata-duplicate-key")
		}
		space()
		pos++
		space()
		start = pos
		depth, quoted := 0, false
		for pos < n {
			c := raw[pos]
			if quoted {
				if c == '\\' {
					pos += 2
					continue
				}
				if c == '"' {
					quoted = false
				}
			} else if c == '"' {
				quoted = true
			} else if c == '{' || c == '[' {
				depth++
				if depth > 32 {
					return nil, errors.New("metadata-nesting-limit")
				}
			} else if c == '}' || c == ']' {
				if depth == 0 {
					break
				}
				depth--
			} else if c == ',' && depth == 0 {
				break
			}
			pos++
		}
		out[key] = bytes.TrimSpace(raw[start:pos])
		space()
		if pos < n && raw[pos] == ',' {
			pos++
		}
	}
}
func metadata(raw []byte, keys ...string) (Object, error) {
	f, e := fields(raw)
	if e != nil {
		return nil, e
	}
	v := Object{}
	for _, k := range keys {
		if b, ok := f[k]; ok {
			var x any
			if e := decode(b, &x); e != nil {
				return nil, e
			}
			v[k] = x
		}
	}
	return v, nil
}
func tail(path string, budget int) ([][]byte, bool, bool, error) {
	if !regular(path, false) {
		return nil, false, false, errors.New("file unavailable")
	}
	f, e := os.Open(path)
	if e != nil {
		return nil, false, false, e
	}
	defer f.Close()
	before, e := f.Stat()
	if e != nil {
		return nil, false, false, e
	}
	offset := max(int64(0), before.Size()-int64(budget))
	if _, e = f.Seek(offset, io.SeekStart); e != nil {
		return nil, false, false, e
	}
	b, e := io.ReadAll(io.LimitReader(f, int64(budget)))
	if e != nil {
		return nil, false, false, e
	}
	after, e := f.Stat()
	if e != nil {
		return nil, false, false, e
	}
	terminated := len(b) == 0 || b[len(b)-1] == '\n'
	lines := bytes.Split(bytes.TrimSuffix(b, []byte{'\n'}), []byte{'\n'})
	if len(b) == 0 {
		lines = nil
	}
	if offset > 0 && len(lines) > 0 {
		lines = lines[1:]
	}
	return lines, terminated, before.Size() == after.Size() && before.ModTime() == after.ModTime(), nil
}
func recentFile(path string, now time.Time) bool {
	s, e := os.Stat(path)
	return e == nil && regular(path, false) && fresh(s.ModTime(), now)
}
func openReadDB(path string) (*sql.DB, error) {
	if !regular(path, false) || !filepath.IsAbs(path) {
		return nil, errors.New("native-database-unavailable")
	}
	u := url.URL{Scheme: "file", Path: filepath.ToSlash(path)}
	q := url.Values{"mode": {"ro"}, "_pragma": {"query_only(1)", "trusted_schema(0)", "busy_timeout(250)"}}
	u.RawQuery = q.Encode()
	db, e := sql.Open("sqlite", u.String())
	if e != nil {
		return nil, e
	}
	db.SetMaxOpenConns(1)
	return db, nil
}
func queryRows(ctx context.Context, db interface {
	QueryContext(context.Context, string, ...any) (*sql.Rows, error)
}, query string, args ...any) ([]Object, error) {
	rows, e := db.QueryContext(ctx, query, args...)
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	columns, e := rows.Columns()
	if e != nil {
		return nil, e
	}
	out := []Object{}
	for rows.Next() {
		if len(out) >= 1000 {
			return nil, errors.New("query row budget exceeded")
		}
		v := make([]any, len(columns))
		pointers := make([]any, len(v))
		for n := range v {
			pointers[n] = &v[n]
		}
		if e := rows.Scan(pointers...); e != nil {
			return nil, e
		}
		row := Object{}
		for n, k := range columns {
			if b, ok := v[n].([]byte); ok {
				v[n] = string(b)
			}
			row[k] = v[n]
		}
		out = append(out, row)
	}
	return out, rows.Err()
}
func columns(ctx context.Context, db *sql.DB, table string) map[string]bool {
	rows, e := queryRows(ctx, db, "PRAGMA table_info("+table+")")
	if e != nil {
		return nil
	}
	out := map[string]bool{}
	for _, r := range rows {
		out[text(r["name"])] = true
	}
	return out
}

func (i *Inspector) observe(h string, scope Object) (Object, Object) {
	probe := Object{"harness": h, "readers": automaticReaders[h], "status": "unavailable"}
	fail := func(reason string) (Object, Object) { probe["reason_code"] = reason; return nil, probe }
	if _, ok := automaticReaders[h]; !ok {
		probe["status"] = "unsupported"
		return fail("automatic-reader-not-implemented")
	}
	if scope == nil {
		return fail("current-caller-scope-unavailable")
	}
	p, ok := i.owner(h)
	if !ok || p.Started == "" {
		return fail("current-caller-process-unavailable")
	}
	native := i.nativeID(h)
	if h == "zcode" {
		if os.PathSeparator == '\\' {
			probe["status"] = "unsupported"
			return fail("automatic-reader-platform-unsupported")
		}
		if p.Name != "zcode-cli" {
			return fail("current-caller-is-not-session-owner")
		}
		native = i.zcodeToken(p)
		if scope["execution_ref"] == nil {
			return fail("current-execution-scope-unavailable")
		}
	}
	if contains([]string{"kimi-desktop", "minimax-code"}, h) {
		if scope["execution_ref"] == nil {
			return fail("current-execution-scope-unavailable")
		}
	} else if h != "kimi-cli" {
		if native == "" {
			return fail("native-session-binding-unavailable")
		}
		if h != "zcode" && scope["session_ref"] != Digest([]string{h, native})[:24] {
			return fail("native-session-scope-mismatch")
		}
	}
	if !contains([]string{"zcode", "minimax-code", "kimi-desktop"}, h) {
		count := 0
		for _, row := range i.Processes {
			if i.matches(row, h) {
				count++
			}
		}
		if count != 1 {
			return fail("ambiguous-harness-ancestry")
		}
	}
	now := i.Now()
	var found Object
	var err error
	reason := "native-metadata-unavailable-or-invalid"
	switch h {
	case "codex":
		found, err = i.codex(native, p, now)
	case "pi":
		if m := model(i.Getenv("PI_MODEL")); m != "" && i.Getenv("PI_CODING_AGENT") == "true" && i.nativeID("pi") == native {
			found = Object{"model": m, "source": "pi-session-runtime"}
		}
	case "trae":
		found, err = i.trae(native, p, now)
	case "claude-code":
		found, reason = i.claude(native, p, now)
	case "zcode":
		found, err = i.zcode(native, p, now)
	case "minimax-code":
		found, err = i.minimax(p, now)
	case "kimi-cli":
		found, err = i.kimiCLI(p, now)
	case "kimi-desktop":
		found, err = i.kimiDesktop(p, now)
	case "dsh":
		found, err = i.dsh(native, p, now)
	case "opencode":
		found, reason = i.opencode(native, p, now)
	}
	if err != nil {
		return fail("automatic-probe-error")
	}
	if found == nil || model(found["model"]) == "" {
		return fail(reason)
	}
	if !i.sameProcess(p) || Digest(i.scope(h)) != Digest(scope) {
		return fail("native-caller-changed")
	}
	at, ok := found["observed_at"]
	if !ok {
		at = seconds(now)
	}
	age := seconds(i.Now()) - number(at)
	if age < 0 || age > 300 {
		return fail("native-observation-stale")
	}
	ref := found["session"]
	if ref == nil {
		ref = native
	}
	found["observation_ref"] = Digest([]any{h, ref, found["turn"], found["model"]})[:24]
	found["observed_at"] = at
	probe["status"], probe["reason_code"], probe["source"] = "observed", nil, found["source"]
	if found["source"] == "opencode-session-request" {
		probe["status"], probe["reason_code"] = "requested", "provider-response-model-unavailable"
	}
	return found, probe
}

func codexIndex(root, native string) Object {
	paths, _ := filepath.Glob(filepath.Join(root, "state*.sqlite"))
	sort.Sort(sort.Reverse(sort.StringSlice(paths)))
	if len(paths) > 4 {
		paths = paths[:4]
	}
	for _, path := range paths {
		db, e := openReadDB(path)
		if e != nil {
			continue
		}
		ctx, cancel := context.WithTimeout(context.Background(), 250*time.Millisecond)
		cols := columns(ctx, db, "threads")
		keys := []string{}
		for _, key := range []string{"rollout_path", "model", "archived", "updated_at", "updated_at_ms"} {
			if cols[key] {
				keys = append(keys, key)
			}
		}
		var rows []Object
		if cols["id"] && cols["rollout_path"] {
			rows, e = queryRows(ctx, db, "SELECT "+strings.Join(keys, ",")+" FROM threads WHERE id=? LIMIT 1", native)
		}
		cancel()
		db.Close()
		if e == nil && len(rows) == 1 {
			return rows[0]
		}
	}
	return nil
}
func (i *Inspector) codex(native string, p Process, now time.Time) (Object, error) {
	root := i.root("codex", i.Getenv("CODEX_HOME"))
	if root == "" {
		return nil, nil
	}
	index := codexIndex(root, native)
	path := ""
	if index != nil {
		if number(index["archived"]) != 0 {
			return nil, nil
		}
		path = text(index["rollout_path"])
	} else {
		paths, e := filepath.Glob(filepath.Join(root, "sessions", "*", "*", "*", "rollout-*-"+native+".jsonl"))
		if e != nil || len(paths) != 1 {
			return nil, e
		}
		path = paths[0]
	}
	if !filepath.IsAbs(path) || !within(path, filepath.Join(root, "sessions")) || !recentFile(path, now) {
		return nil, nil
	}
	f, e := os.Open(path)
	if e != nil {
		return nil, e
	}
	raw, e := bufio.NewReaderSize(f, maxRecordBytes+1).ReadSlice('\n')
	f.Close()
	if e != nil || len(raw) > maxRecordBytes {
		return nil, e
	}
	head, e := fields(bytes.TrimSpace(raw))
	if e != nil || string(head["type"]) != `"session_meta"` {
		return nil, e
	}
	payload, e := metadata(head["payload"], "id")
	if e != nil || payload["id"] != native {
		return nil, e
	}
	lines, _, stable, e := tail(path, maxTailBytes)
	if e != nil || !stable {
		return nil, e
	}
	var turnContext, usage Object
	active := ""
	ended := false
	for _, line := range lines {
		match := codexEnvelope.FindSubmatchIndex(line[:min(len(line), 512)])
		if match == nil {
			continue
		}
		kind := string(line[match[2]:match[3]])
		if kind == "turn_context" || kind == "token_usage_record" {
			if len(line) > maxRecordBytes {
				return nil, nil
			}
			row, e := metadata(line, "timestamp")
			if e != nil {
				return nil, e
			}
			spans, e := fields(line)
			if e != nil {
				return nil, e
			}
			key := i.Rules["codex"].ModelKey
			if key == "" {
				key = "model"
			}
			v, e := metadata(spans["payload"], key, "turn_id", "thread_id")
			if e != nil {
				return nil, e
			}
			if kind == "turn_context" {
				turnContext = Object{"model": model(v[key]), "turn": v["turn_id"], "at": stamp(row["timestamp"])}
			} else if v["thread_id"] == native {
				usage = Object{"turn": v["turn_id"], "at": stamp(row["timestamp"])}
			}
		} else if kind == "event_msg" {
			prefix := line[match[1]:min(len(line), match[1]+2048)]
			event := regexp.MustCompile(`^\s*\{\s*"type"\s*:\s*"([^"]+)"`).FindSubmatch(prefix)
			if event != nil && contains([]string{"task_started", "task_complete", "turn_aborted", "shutdown_complete"}, string(event[1])) {
				ended = string(event[1]) != "task_started"
				active = ""
				turn := regexp.MustCompile(`"turn_id"\s*:\s*"([^"\n]+)"`).FindSubmatch(prefix)
				if turn != nil && !ended {
					active = string(turn[1])
				}
			}
		}
	}
	if ended {
		return nil, nil
	}
	indexed := model(index["model"])
	if turnContext != nil {
		at, _ := turnContext["at"].(time.Time)
		if model(turnContext["model"]) != "" && afterStart(at, p) && !at.After(now) && active != "" && turnContext["turn"] == active {
			if indexed != "" && indexed != turnContext["model"] {
				return nil, nil
			}
			return Object{"model": turnContext["model"], "source": "codex-turn-context", "turn": active}, nil
		}
	}
	updated := number(index["updated_at"])
	if x, ok := index["updated_at_ms"]; ok {
		updated = number(x) / 1000
	}
	at, _ := usage["at"].(time.Time)
	updateTime := time.UnixMilli(int64(updated * 1000))
	if indexed != "" && text(usage["turn"]) != "" && afterStart(at, p) && fresh(at, now) && afterStart(updateTime, p) && fresh(updateTime, now) && (active == "" || usage["turn"] == active) && (turnContext == nil || turnContext["turn"] != usage["turn"] || turnContext["model"] == indexed) {
		return Object{"model": indexed, "source": "codex-thread-state", "turn": usage["turn"]}, nil
	}
	return nil, nil
}

func (i *Inspector) claude(native string, p Process, now time.Time) (Object, string) {
	if !regexp.MustCompile(`^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$`).MatchString(native) {
		return nil, "native-session-binding-unavailable"
	}
	root := i.root("claude-code", i.Getenv("CLAUDE_CONFIG_DIR"))
	if root == "" {
		return nil, "native-root-unavailable"
	}
	cwd := i.Directory
	pathFor := func(cwd string) string {
		return filepath.Join(root, "projects", regexp.MustCompile(`[^a-zA-Z0-9]`).ReplaceAllString(cwd, "-"), native+".jsonl")
	}
	path := pathFor(cwd)
	if _, e := os.Lstat(path); errors.Is(e, os.ErrNotExist) {
		if other := i.callerCwd(p); other != "" && other != cwd {
			cwd = other
			path = pathFor(cwd)
		}
	}
	for attempt := 0; attempt < 3; attempt++ {
		if !regular(path, false) || !within(path, root) {
			return nil, "native-session-file-unavailable"
		}
		s, e := os.Stat(path)
		if e != nil {
			return nil, "native-session-file-unavailable"
		}
		if now.Sub(s.ModTime()) > 5*time.Minute {
			return nil, "native-session-file-stale"
		}
		transient := s.ModTime().After(now)
		if !transient {
			lines, terminated, stable, e := tail(path, maxTailBytes)
			if e != nil {
				return nil, "native-session-file-unavailable"
			}
			transient = !stable
			if stable {
				for n := len(lines) - 1; n >= 0; n-- {
					raw := lines[n]
					if len(raw) > maxRecordBytes {
						return nil, "native-record-oversized"
					}
					f, e := fields(raw)
					if e != nil {
						if n == len(lines)-1 && !terminated && !json.Valid(raw) {
							var value any
							syntax := json.Unmarshal(raw, &value)
							if syntax != nil && (strings.Contains(syntax.Error(), "unexpected end of JSON") || !utf8.Valid(raw)) {
								transient = true
								break
							}
						}
						return nil, "native-metadata-invalid"
					}
					row, e := metadata(raw, "type", "sessionId", "cwd", "timestamp", "uuid", "isSidechain")
					if e != nil {
						return nil, "native-metadata-invalid"
					}
					if row["type"] != "assistant" || row["isSidechain"] == true {
						continue
					}
					message, e := metadata(f["message"], "model")
					if e != nil {
						return nil, "native-metadata-invalid"
					}
					at := stamp(row["timestamp"])
					m := model(message["model"])
					if row["isSidechain"] != false || row["sessionId"] != native || row["cwd"] != cwd || text(row["uuid"]) == "" || !afterStart(at, p) || m == "" {
						return nil, "native-assistant-binding-invalid"
					}
					if now.Sub(at) > 5*time.Minute {
						return nil, "native-assistant-stale"
					}
					if at.After(now) {
						transient = true
						break
					}
					return Object{"model": m, "source": "claude-session-runtime", "turn": row["uuid"], "observed_at": seconds(now)}, ""
				}
				if !transient {
					return nil, "native-current-assistant-unavailable"
				}
			}
		}
		if attempt < 2 {
			time.Sleep(20 * time.Millisecond)
			now = i.Now()
		}
	}
	return nil, "native-observation-in-progress"
}

func (i *Inspector) trae(native string, p Process, now time.Time) (Object, error) {
	root := i.root("trae", "")
	if root == "" {
		return nil, nil
	}
	paths, _ := filepath.Glob(filepath.Join(root, "traecli*.log"))
	sort.Slice(paths, func(a, b int) bool {
		x, e1 := os.Stat(paths[a])
		y, e2 := os.Stat(paths[b])
		return e1 == nil && (e2 != nil || x.ModTime().After(y.ModTime()))
	})
	if len(paths) > 4 {
		paths = paths[:4]
	}
	thread := regexp.MustCompile(`(?:^|[^A-Za-z0-9_])thread_id=` + regexp.QuoteMeta(native) + `(?:$|[^A-Za-z0-9._:-])`)
	modelRE := regexp.MustCompile(`\bconfig_name=([^\s]+)|\bserver reported model ([^\s]+)`)
	dateRE := regexp.MustCompile(`\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?`)
	latest := time.Time{}
	m := ""
	for _, path := range paths {
		lines, _, stable, e := tail(path, 1<<20)
		if e != nil || !stable {
			continue
		}
		for _, raw := range lines {
			if len(raw) > maxRecordBytes || !thread.Match(raw) {
				continue
			}
			match := modelRE.FindSubmatch(raw)
			date := dateRE.Find(raw[:min(256, len(raw))])
			at := stamp(string(date))
			if match != nil && at.After(latest) {
				latest = at
				m = model(string(match[1]) + string(match[2]))
			}
		}
	}
	if m != "" && afterStart(latest, p) && fresh(latest, now) {
		return Object{"model": m, "source": "trae-thread-runtime"}, nil
	}
	return nil, nil
}

func (i *Inspector) zcodeToken(owner Process) string {
	re := regexp.MustCompile(`/\.zcode/cli/exec/bash-startup/([A-Za-z0-9][A-Za-z0-9._-]{0,127})/`)
	for _, p := range i.Processes {
		if p.PID == owner.PID {
			break
		}
		if !shells[p.Name] {
			continue
		}
		args, e := i.ProcessArgs(p.PID)
		if e != nil {
			continue
		}
		for _, arg := range args {
			if m := re.FindStringSubmatch(arg); m != nil {
				return m[1]
			}
		}
	}
	return ""
}
func (i *Inspector) zcode(native string, p Process, now time.Time) (Object, error) {
	root := i.root("zcode", "")
	if root == "" {
		return nil, nil
	}
	path := filepath.Join(root, "model-io-"+native+".jsonl")
	if !within(path, root) || !recentFile(path, now) {
		return nil, nil
	}
	lines, _, stable, e := tail(path, maxTailBytes)
	if e != nil || !stable {
		return nil, e
	}
	re := regexp.MustCompile(`^\s*\{\s*"completedAt"\s*:\s*"([^"\n]+)"\s*,\s*"durationMs"\s*:\s*\d+\s*,\s*"requestId"\s*:\s*"([^"\n]{1,128})"\s*,\s*"attempt"\s*:\s*\d+\s*,\s*"model"\s*:\s*\{\s*"modelId"\s*:\s*"([^"\n]+)"`)
	for n := len(lines) - 1; n >= 0; n-- {
		match := re.FindSubmatch(lines[n][:min(len(lines[n]), 640)])
		if match == nil {
			continue
		}
		at := stamp(string(match[1]))
		m := model(string(match[3]))
		if m == "" || !afterStart(at, p) || !fresh(at, now) {
			return nil, nil
		}
		return Object{"model": m, "source": "zcode-model-io", "turn": string(match[2])}, nil
	}
	return nil, nil
}
