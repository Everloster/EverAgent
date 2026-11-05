package core

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"strconv"
)

func (i *Inspector) scope(h string) Object {
	p, ok := i.owner(h)
	if !ok || p.Started == "" {
		return nil
	}
	scope := Object{"harness": h, "process_ref": hashText(h + ":" + strconv.Itoa(p.PID) + ":" + p.Started)[:24]}
	if native := i.nativeID(h); native != "" {
		scope["session_ref"] = Digest([]string{h, native})[:24]
	}
	terminal := i.Getenv("ORCA_TERMINAL_HANDLE")
	if terminal == "" {
		terminal = i.Getenv("HERDR_PANE_ID")
	}
	if regexp.MustCompile(`^[A-Za-z0-9:._/-]{1,256}$`).MatchString(terminal) {
		scope["terminal_ref"] = Digest(terminal)[:24]
	}
	if scope["session_ref"] == nil && (contains([]string{"desktop", "web"}, i.Form(h)) || scope["terminal_ref"] == nil) {
		for _, row := range i.Processes {
			if row.PID == p.PID {
				break
			}
			if shells[row.Name] && row.Started != "" {
				scope["execution_ref"] = Digest([]any{row.PID, row.Started})[:24]
				break
			}
		}
		if scope["execution_ref"] == nil {
			return nil
		}
	}
	return scope
}
func (i *Inspector) factScope() Object {
	h, _ := i.detectHarness()
	scope := i.scope(h)
	if scope == nil {
		for _, p := range i.Processes {
			if shells[p.Name] && p.Started != "" {
				scope = Object{"execution_ref": Digest([]any{p.PID, p.Started})[:24]}
				break
			}
		}
	}
	if scope == nil {
		return nil
	}
	var harness any
	if h != "" {
		harness = h
	}
	host, _ := os.Hostname()
	platform := map[string]string{"darwin": "Darwin", "linux": "Linux", "windows": "Windows"}[runtime.GOOS]
	scope["automatic_harness"] = harness
	scope["machine_ref"] = Digest([]string{platform, host})[:24]
	scope["hint_sha256"] = Digest(i.Hint(h))
	return scope
}
func (i *Inspector) receiptPath(scope Object, facts bool) string {
	key, prefix := "EVERAGENT_MODEL_DECLARATION", ""
	if facts {
		key, prefix = "EVERAGENT_SESSION_DECLARATION", "facts-"
	}
	if path := i.Getenv(key); path != "" {
		return expandHome(path, i.Home)
	}
	if i.Home == "" || scope == nil {
		return ""
	}
	return filepath.Join(i.Home, ".local/share/everagent/session-models", prefix+Digest(scope)+".json")
}
func receipt(path string) Object {
	if path == "" {
		return nil
	}
	b, e := readSmall(path, 8192, true)
	if e != nil {
		return nil
	}
	var v Object
	if decode(b, &v) != nil {
		return nil
	}
	payload := clone(v)
	delete(payload, "id")
	if v["id"] != Digest(payload) {
		return nil
	}
	return v
}
func validTiming(v Object, now float64, minTTL float64) bool {
	for _, key := range []string{"declared_at", "expires_at"} {
		if _, ok := v[key].(json.Number); !ok {
			if _, ok := v[key].(float64); !ok {
				return false
			}
		}
	}
	at, expiry := number(v["declared_at"]), number(v["expires_at"])
	return at <= now && expiry-at >= minTTL && expiry-at <= 43200 && expiry > at
}
func (i *Inspector) readModel(h, hint string) Object {
	scope := i.scope(h)
	if scope == nil {
		return nil
	}
	v := receipt(i.receiptPath(scope, false))
	if v == nil || number(v["schema_version"]) != 1 || v["source"] != "user" || v["confirmation"] != "explicit" || Digest(v["scope"]) != Digest(scope) || v["hint_sha256"] != hint || model(v["model"]) == "" || !validTiming(v, seconds(i.Now()), 0) {
		return nil
	}
	return v
}
func validFacts(fields Object) bool {
	if len(fields) == 0 {
		return false
	}
	for key, v := range fields {
		if !contains([]string{"device", "harness", "form", "model"}, key) || model(v) == "" {
			return false
		}
		if key == "harness" && !regexp.MustCompile(`^[a-z][a-z0-9-]{0,63}$`).MatchString(text(v)) {
			return false
		}
		if key == "form" && !contains([]string{"cli", "desktop", "web"}, text(v)) {
			return false
		}
	}
	return true
}
func (i *Inspector) readFacts(includeExpired bool) Object {
	scope := i.factScope()
	if scope == nil {
		return nil
	}
	v := receipt(i.receiptPath(scope, true))
	now := seconds(i.Now())
	if v == nil || number(v["schema_version"]) != 2 || v["source"] != "user" || v["confirmation"] != "explicit" || Digest(v["scope"]) != Digest(scope) || !validFacts(object(v["fields"])) || !validTiming(v, now, 300) || !includeExpired && now >= number(v["expires_at"]) {
		return nil
	}
	times := object(v["field_times"])
	fields := object(v["fields"])
	if len(times) != len(fields) {
		return nil
	}
	for key := range fields {
		t := object(times[key])
		if len(t) != 2 || !validTiming(t, now, 300) || number(t["declared_at"]) > number(v["declared_at"]) || number(t["expires_at"]) > number(v["expires_at"]) {
			return nil
		}
	}
	if revoked, ok := v["model_discarded_at"]; ok {
		if _, ok := revoked.(json.Number); !ok {
			return nil
		}
		if number(revoked) < 0 || number(revoked) > number(v["declared_at"]) {
			return nil
		}
	}
	if scope["automatic_harness"] == nil && text(fields["harness"]) != "" && v["harness_hint_sha256"] != Digest(i.Hint(text(fields["harness"]))) {
		return nil
	}
	active, activeTimes := Object{}, Object{}
	for k, value := range fields {
		if includeExpired || now < number(object(times[k])["expires_at"]) {
			active[k] = value
			activeTimes[k] = times[k]
		}
	}
	if len(active) == 0 {
		return nil
	}
	v["fields"], v["field_times"] = active, activeTimes
	return v
}
func (i *Inspector) Facts() Object { return i.readFacts(false) }

func atomicReceipt(path string, value Object) error {
	if path == "" {
		return errors.New("declaration path unavailable")
	}
	if s, e := os.Lstat(path); e == nil && (!s.Mode().IsRegular() || !ownedFile(s, true)) {
		return errors.New("declaration path is not a private regular file")
	}
	if e := os.MkdirAll(filepath.Dir(path), 0700); e != nil {
		return e
	}
	f, e := os.CreateTemp(filepath.Dir(path), ".declaration-*")
	if e != nil {
		return e
	}
	name := f.Name()
	defer os.Remove(name)
	defer f.Close()
	e = json.NewEncoder(f).Encode(value)
	if e == nil {
		e = f.Sync()
	}
	if e == nil {
		e = f.Close()
	}
	if e == nil {
		e = os.Rename(name, path)
	}
	return e
}

// DeclareFacts records only explicit user facts. observed must contain current
// automatically verified facts, not a configuration or another declaration.
func (i *Inspector) DeclareFacts(fields Object, confirmed bool, ttl int, observed Object) (Object, error) {
	if !confirmed {
		return nil, errors.New("需要用户明确指定缺失事实；不得根据配置代为确认")
	}
	if !validFacts(fields) {
		return nil, errors.New("只接受明确的 device/harness/form/model")
	}
	if ttl < 300 || ttl > 43200 {
		return nil, errors.New("声明有效期必须为 300–43200 秒")
	}
	for key, value := range fields {
		if x := observed[key]; x != nil && x != "unknown" && x != "" && x != value {
			return nil, errors.New("声明与当前自动证据冲突；先诊断，不能覆盖")
		}
	}
	scope := i.factScope()
	if scope == nil {
		return nil, errors.New("无法绑定当前执行上下文")
	}
	path := i.receiptPath(scope, true)
	now := seconds(i.Now())
	previous := i.readFacts(true)
	retained, times := Object{}, Object{}
	for k, v := range object(previous["fields"]) {
		if _, replaced := fields[k]; replaced {
			continue
		}
		if x := observed[k]; x == nil || x == "unknown" || x == "" || x == v {
			retained[k] = v
		}
	}
	if fields["harness"] != nil && fields["harness"] != object(previous["fields"])["harness"] {
		delete(retained, "model")
		delete(retained, "form")
	}
	discarded := number(previous["model_discarded_at"])
	if object(previous["fields"])["model"] != nil && retained["model"] == nil && fields["model"] == nil {
		discarded = now
	}
	for k := range retained {
		times[k] = object(previous["field_times"])[k]
	}
	for k, v := range fields {
		retained[k] = v
		times[k] = Object{"declared_at": now, "expires_at": now + float64(ttl)}
	}
	expires := float64(0)
	for _, v := range times {
		expires = max(expires, number(object(v)["expires_at"]))
	}
	value := Object{"schema_version": 2, "source": "user", "confirmation": "explicit", "scope": scope, "fields": retained, "field_times": times, "declared_at": now, "expires_at": expires}
	if discarded > 0 {
		value["model_discarded_at"] = discarded
	}
	if scope["automatic_harness"] == nil && retained["harness"] != nil {
		value["harness_hint_sha256"] = Digest(i.Hint(text(retained["harness"])))
	}
	value["id"] = Digest(value)
	if e := atomicReceipt(path, value); e != nil {
		return nil, e
	}
	active, activeTimes := Object{}, Object{}
	for k, v := range retained {
		if now < number(object(times[k])["expires_at"]) {
			active[k] = v
			activeTimes[k] = times[k]
		}
	}
	return Object{"id": value["id"], "fields": active, "field_times": activeTimes, "source": "user-declared", "scope": scope, "expires_at": expires, "automatically_verified": false, "grants_permissions": false}, nil
}
