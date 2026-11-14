package core

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
)

// KimiSession contains only native binding metadata, never titles or messages.
// Problem is a static rejection code; callers must not read a rejected source.
type KimiSession struct {
	ID, Directory, StateSHA256, Problem string
	CreatedAt, UpdatedAt                time.Time
	Archived                            bool
}

var kimiSegment = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`)
var kimiSlug = regexp.MustCompile(`[^a-z0-9._-]+`)

// kimiWorkspaceKey follows the native workdir-slug layout in Kimi Code
// 0.42.0 / 2.4.1. A bucket is only a locator: state must independently bind cwd.
func kimiWorkspaceKey(cwd string) string {
	normalized := strings.TrimRight(strings.ReplaceAll(cwd, `\`, "/"), "/")
	parts := strings.Split(normalized, "/")
	slug := strings.Trim(kimiSlug.ReplaceAllString(strings.ToLower(parts[len(parts)-1]), "-"), "-")
	slug = strings.Trim(slug[:min(len(slug), 40)], "-")
	if slug == "" || slug == "." || slug == ".." {
		slug = "workspace"
	}
	return "wd_" + slug + "_" + hashText(normalized)[:12]
}

// KimiSessions reads only the exact cwd bucket, not global indexes, CLI startup
// hooks, other workspaces or wire bodies. Native `session list` can apply staged
// updates and rewrite indexes even when invoked as an apparent read-only query.
// Unrecognized alias layouts are not searched. Overflow is an error, not a
// truncated list that could be mistaken for a unique live session.
func KimiSessions(root, cwd string) ([]KimiSession, error) {
	if !filepath.IsAbs(root) || !filepath.IsAbs(cwd) || filepath.Clean(cwd) != cwd {
		return nil, errors.New("kimi-code-scoped-path-unavailable")
	}
	if actual, e := filepath.EvalSymlinks(root); e != nil || actual != filepath.Clean(root) {
		return nil, errors.New("kimi-code-session-root-unavailable")
	}
	bucket := filepath.Join(root, kimiWorkspaceKey(cwd))
	if _, e := os.Lstat(bucket); errors.Is(e, os.ErrNotExist) {
		return []KimiSession{}, nil
	}
	if !kimiSafePath(root, bucket, true) {
		return nil, errors.New("kimi-code-scoped-bucket-unavailable")
	}
	dir, e := os.Open(bucket)
	if e != nil {
		return nil, errors.New("kimi-code-scoped-bucket-unavailable")
	}
	defer dir.Close()
	before, e := dir.Stat()
	if e != nil {
		return nil, errors.New("kimi-code-scoped-bucket-unavailable")
	}
	entries, e := dir.ReadDir(257)
	if e != nil && !errors.Is(e, io.EOF) {
		return nil, errors.New("kimi-code-scoped-list-unavailable")
	}
	if len(entries) > 256 {
		return nil, errors.New("kimi-code-scoped-list-over-budget")
	}
	sort.Slice(entries, func(a, b int) bool { return entries[a].Name() < entries[b].Name() })
	out := []KimiSession{}
	budget := 4 << 20
	for _, entry := range entries {
		if !entry.IsDir() && entry.Type()&os.ModeSymlink == 0 {
			continue
		}
		row := KimiSession{ID: entry.Name(), Directory: filepath.Join(bucket, entry.Name())}
		if !kimiSegment.MatchString(row.ID) || !kimiSafePath(root, row.Directory, true) {
			row.Problem = "kimi-code-scoped-state-unavailable"
		} else {
			row.Problem = kimiSessionMetadata(root, cwd, &row, &budget)
		}
		if row.Problem == "kimi-code-empty-directory" {
			continue
		}
		out = append(out, row)
	}
	after, e := os.Stat(bucket)
	if e != nil || !os.SameFile(before, after) || before.ModTime() != after.ModTime() || !kimiSafePath(root, bucket, true) {
		return nil, errors.New("kimi-code-scoped-list-changed")
	}
	return out, nil
}

func kimiSafePath(root, path string, directory bool) bool {
	if !within(path, root) {
		return false
	}
	rel, e := filepath.Rel(root, path)
	if e != nil {
		return false
	}
	current := root
	var info os.FileInfo
	for _, part := range strings.Split(rel, string(filepath.Separator)) {
		current = filepath.Join(current, part)
		info, e = os.Lstat(current)
		if e != nil || info.Mode()&os.ModeSymlink != 0 || !ownedFile(info, false) {
			return false
		}
	}
	return info != nil && (directory && info.IsDir() || !directory && info.Mode().IsRegular())
}

func kimiSessionMetadata(root, cwd string, row *KimiSession, budget *int) string {
	path := filepath.Join(row.Directory, "state.json")
	if _, e := os.Lstat(path); errors.Is(e, os.ErrNotExist) {
		path = filepath.Join(row.Directory, "session-meta/state.json")
	}
	if _, e := os.Lstat(path); errors.Is(e, os.ErrNotExist) {
		// Native session indexes omit missing metadata. Ignore only genuinely
		// empty directories; leftover wire/data is an explicit coverage gap,
		// never permission to read an unbound body or assume uniqueness.
		dir, err := os.Open(row.Directory)
		if err == nil {
			names, readErr := dir.Readdirnames(1)
			dir.Close()
			if len(names) == 0 && errors.Is(readErr, io.EOF) {
				return "kimi-code-empty-directory"
			}
		}
		return "kimi-code-scoped-metadata-missing"
	}
	if !kimiSafePath(root, path, false) {
		return "kimi-code-scoped-state-unavailable"
	}
	before, e := os.Stat(path)
	if e != nil || before.Size() > 1<<20 || before.Size() > int64(*budget) {
		return "kimi-code-scoped-state-over-budget"
	}
	b, e := readSmall(path, min(1<<20, *budget), false)
	*budget -= len(b)
	if e != nil {
		return "kimi-code-scoped-state-unavailable"
	}
	after, e := os.Stat(path)
	if e != nil || !os.SameFile(before, after) || before.Size() != after.Size() || before.ModTime() != after.ModTime() || !kimiSafePath(root, path, false) {
		return "kimi-code-scoped-state-changed"
	}
	row.StateSHA256 = hashText(string(b))
	state, e := metadata(b, "id", "version", "cwd", "workDir", "createdAt", "updatedAt", "archived")
	if e != nil {
		return "kimi-code-state-format-unverified"
	}
	id, stateCWD := text(state["id"]), text(state["cwd"])
	if version, present := state["version"]; present {
		if number(version) != 2 {
			return "kimi-code-state-format-unverified"
		}
	} else {
		if _, hasID := state["id"]; hasID {
			return "kimi-code-state-format-unverified"
		}
		if _, hasCWD := state["cwd"]; hasCWD {
			return "kimi-code-state-format-unverified"
		}
		id, stateCWD = row.ID, text(state["workDir"])
	}
	if id == "" || stateCWD == "" {
		return "kimi-code-state-identity-unavailable"
	}
	if id != row.ID || !kimiSameDirectory(stateCWD, cwd) || state["workDir"] != nil && !kimiSameDirectory(text(state["workDir"]), cwd) {
		return "kimi-code-state-identity-mismatch"
	}
	// Do not decode custom values, titles, lastPrompt, other agents or fork data.
	f, _ := fields(b)
	main := map[string][]byte{}
	if a, ok := f["agents"]; ok {
		agents, err := fields(a)
		if err != nil {
			return "kimi-code-state-format-unverified"
		}
		if a, ok := agents["main"]; ok {
			main, err = fields(a)
			if err != nil {
				return "kimi-code-state-format-unverified"
			}
		}
	}
	for _, value := range [][]byte{f["forkedFrom"], main["forkedFrom"], main["parentAgentId"]} {
		if !kimiEmpty(value) {
			return "kimi-code-fork-scope-unverified"
		}
	}
	if kind, present := main["type"]; present && !bytes.Equal(kind, []byte(`"main"`)) {
		return "kimi-code-fork-scope-unverified"
	}
	if !kimiEmpty(f["additionalDirs"]) {
		return "kimi-code-additional-directories-unverified"
	}
	row.CreatedAt, row.UpdatedAt = kimiTime(state["createdAt"]), kimiTime(state["updatedAt"])
	if row.CreatedAt.IsZero() || row.UpdatedAt.IsZero() || row.UpdatedAt.Before(row.CreatedAt) {
		return "kimi-code-state-time-unavailable"
	}
	if archived, present := state["archived"]; present {
		var ok bool
		row.Archived, ok = archived.(bool)
		if !ok {
			return "kimi-code-state-format-unverified"
		}
	}
	return ""
}

func kimiEmpty(raw []byte) bool {
	return len(raw) == 0 || bytes.Equal(raw, []byte("null")) || bytes.Equal(raw, []byte(`""`)) || bytes.Equal(raw, []byte("[]"))
}

func kimiTime(v any) time.Time {
	if n, ok := v.(json.Number); ok {
		ms, e := n.Int64()
		if e == nil && ms > 0 {
			return time.UnixMilli(ms)
		}
		return time.Time{}
	}
	at := stamp(v)
	if at.Unix() <= 0 {
		return time.Time{}
	}
	return at
}

func kimiSameDirectory(a, b string) bool {
	if a == b {
		return true
	}
	return os.PathSeparator == '\\' && strings.EqualFold(filepath.Clean(a), filepath.Clean(b))
}

type kimiObservation struct {
	model, step string
	at          time.Time
	wire        os.FileInfo
	present     bool
}

func (i *Inspector) kimiCLI(p Process, now time.Time) (Object, string) {
	cwd := i.callerCwd(p)
	if cwd == "" {
		return nil, "current-caller-cwd-unavailable"
	}
	root := i.root("kimi-cli", "")
	if home := i.Getenv("KIMI_CODE_HOME"); home != "" {
		if !filepath.IsAbs(home) {
			return nil, "kimi-code-scoped-path-unavailable"
		}
		root = filepath.Join(home, "sessions")
	}
	rows, e := KimiSessions(root, cwd)
	if e != nil {
		return nil, e.Error()
	}
	candidates := []KimiSession{}
	for _, row := range rows {
		if row.Problem != "" {
			return nil, row.Problem
		}
		if !row.Archived && !row.CreatedAt.After(now.Add(2*time.Second)) && afterStart(row.UpdatedAt, p) && !row.UpdatedAt.After(now.Add(2*time.Second)) {
			candidates = append(candidates, row)
		}
	}
	if native := i.nativeID("kimi-cli"); native != "" {
		bound := []KimiSession{}
		for _, row := range candidates {
			if row.ID == native {
				bound = append(bound, row)
			}
		}
		if len(bound) == 0 {
			return nil, "native-session-scope-mismatch"
		}
		candidates = bound
	}
	if len(candidates) == 0 {
		return nil, "kimi-code-live-session-not-unique"
	}
	type active struct {
		row KimiSession
		obs kimiObservation
	}
	live := []active{}
	if len(candidates) == 1 {
		obs, reason := readKimiObservation(root, candidates[0], p, now)
		if reason != "" {
			return nil, reason
		}
		if !obs.present {
			return nil, "native-metadata-unavailable-or-invalid"
		}
		live = append(live, active{row: candidates[0], obs: obs})
	} else {
		for _, row := range candidates {
			obs, reason := readKimiObservation(root, row, p, now)
			if reason == "native-observation-stale" || !obs.present {
				continue
			}
			if reason != "" {
				return nil, reason
			}
			live = append(live, active{row: row, obs: obs})
		}
	}
	if len(live) != 1 {
		return nil, "kimi-code-live-session-not-unique"
	}
	row, obs := live[0].row, live[0].obs
	if i.callerCwd(p) != cwd {
		return nil, "native-caller-changed"
	}
	path := filepath.Join(row.Directory, "agents/main/wire.jsonl")
	after, e := os.Stat(path)
	if e != nil || !kimiSafePath(root, path, false) || !os.SameFile(obs.wire, after) || obs.wire.Size() != after.Size() || obs.wire.ModTime() != after.ModTime() {
		return nil, "native-observation-in-progress"
	}
	again, e := KimiSessions(root, cwd)
	if e != nil || Digest(rows) != Digest(again) {
		return nil, "kimi-code-scoped-list-changed"
	}
	return Object{"model": obs.model, "source": "kimi-cli-session-runtime", "observed_at": seconds(obs.at), "turn": obs.step, "session": row.ID}, ""
}

func readKimiObservation(root string, row KimiSession, p Process, now time.Time) (kimiObservation, string) {
	path := filepath.Join(row.Directory, "agents/main/wire.jsonl")
	if _, e := os.Lstat(path); errors.Is(e, os.ErrNotExist) {
		return kimiObservation{}, ""
	}
	if !kimiSafePath(root, path, false) {
		return kimiObservation{}, "kimi-code-scoped-wire-unavailable"
	}
	before, e := os.Stat(path)
	if e != nil {
		return kimiObservation{}, "kimi-code-scoped-wire-unavailable"
	}
	if before.Size() == 0 {
		return kimiObservation{}, ""
	}
	lines, terminated, stable, e := tail(path, maxTailBytes)
	if e != nil || !stable || !terminated {
		return kimiObservation{}, "native-observation-in-progress"
	}
	var request Object
	envelope := regexp.MustCompile(`^\s*\{\s*"type"\s*:\s*"llm\.request"`)
	for n := len(lines) - 1; n >= 0; n-- {
		raw := lines[n]
		if !envelope.Match(raw[:min(len(raw), 128)]) {
			continue
		}
		if len(raw) > maxRecordBytes {
			return kimiObservation{}, "native-record-oversized"
		}
		request, e = kimiRecord(raw)
		if e != nil {
			return kimiObservation{}, "native-metadata-invalid"
		}
		break
	}
	if request == nil {
		return kimiObservation{}, ""
	}
	at := kimiTime(request["time"])
	m, step := model(request["model"]), text(request["turnStep"])
	if request["kind"] != "loop" || m == "" || !nativePattern.MatchString(step) || len(step) > 128 || request["modelAlias"] != nil && model(request["modelAlias"]) == "" {
		return kimiObservation{}, "native-metadata-unavailable-or-invalid"
	}
	if !afterStart(at, p) || !fresh(at, now) {
		return kimiObservation{present: true}, "native-observation-stale"
	}
	after, e := os.Stat(path)
	if e != nil || !os.SameFile(before, after) || before.Size() != after.Size() || before.ModTime() != after.ModTime() {
		return kimiObservation{}, "native-observation-in-progress"
	}
	return kimiObservation{model: m, step: step, at: at, wire: before, present: true}, ""
}
