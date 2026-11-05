package core

import (
	"context"
	"path/filepath"
	"strings"
	"time"
)

// Checkout reports only repository metadata, never its absolute path. The path
// is returned separately so the private adapter can compare a native host.
func Checkout(cwd string) (Object, string) {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	b, err := command(ctx, cwd, nil, 16384, "git", "rev-parse", "--show-toplevel", "HEAD", "--git-common-dir")
	if err != nil {
		return Object{"status": "outside-git"}, ""
	}
	lines := strings.Split(strings.TrimSpace(string(b)), "\n")
	if len(lines) != 3 {
		return Object{"status": "unavailable"}, ""
	}
	root, common := realPath(lines[0]), lines[2]
	if !filepath.IsAbs(common) {
		common = filepath.Join(cwd, common)
	}
	common = realPath(common)
	main := root
	if filepath.Base(common) == ".git" {
		main = filepath.Dir(common)
	}
	branch, err := command(ctx, root, nil, 1024, "git", "branch", "--show-current")
	if err != nil {
		return Object{"status": "unavailable"}, root
	}
	var name any
	if value := strings.TrimSpace(string(branch)); value != "" {
		name = value
	}
	return Object{"status": "ok", "repository": filepath.Base(main), "branch": name,
		"head": lines[1], "linked_worktree": root != main, "checkout_ref": hashText(root)[:24]}, root
}

func Readiness(device, identity, checkout, host Object) Object {
	reasons := []string{}
	if device["known"] != true {
		reasons = append(reasons, "unknown-device")
	}
	if identity["harness_resolved"] != true {
		reasons = append(reasons, "agent-unresolved")
	}
	if RequireModel(identity) != nil {
		reasons = append(reasons, "model-unverified")
	}
	if checkout["status"] != "ok" {
		reasons = append(reasons, "checkout-unavailable")
	}
	if s := text(host["status"]); contains([]string{"ambiguous-runtime", "unavailable", "disconnected-or-orphaned", "no-caller-handle"}, s) {
		reasons = append(reasons, "runtime-"+s)
	}
	if contains([]string{"orca", "herdr"}, text(host["kind"])) && host["verified"] != true {
		reasons = append(reasons, "caller-unverified")
	}
	if host["workspace_matches_runtime"] == false {
		reasons = append(reasons, "checkout-differs-from-host")
	}
	return Object{"read_only": device["known"] == true, "commit": len(reasons) == 0, "reasons": reasons}
}

// NormalizeSession is shared by standalone clients and the private device
// adapter. It does not infer a machine, a task, or a model from missing fields.
func (i *Inspector) NormalizeSession(device, identity, checkout, host, caller, task, provenance Object) Object {
	ready := Readiness(device, identity, checkout, host)
	worker := task["owner"] != nil && task["verified"] == true
	harness := text(identity["cli"])
	kind, usage := "unresolved", "interactive"
	if identity["harness_resolved"] == true {
		kind = "agent"
		if worker {
			usage = "worker"
		}
	} else if worker && task["kind"] == "executor" {
		kind, usage = "executor-service", "executor"
	}
	hasModel := identity["current_model_confirmed"] == true || identity["user_model_declared"] == true
	name, id := "agent-unknown", "unknown"
	if harness != "" {
		name = harness + "-unknown"
	}
	if hasModel {
		name, id = text(identity["name"]), text(identity["model"])
	}
	m := Object{"id": id, "source": identity["model_source"], "confidence": identity["model_confidence"],
		"confirmed": identity["current_model_confirmed"] == true, "user_declared": identity["user_model_declared"] == true}
	for _, key := range []string{"requested_model", "configured_model", "observed_model", "user_declared_model"} {
		if v := identity[key]; v != nil && v != "" {
			m[strings.TrimSuffix(key, "_model")] = v
		}
	}
	if d := object(identity["declaration"]); text(d["id"]) != "" {
		m["declaration_id"] = text(d["id"])[:min(24, len(text(d["id"])))]
	}
	if v := identity["request_observation"]; v != nil {
		m["request_observation"] = v
	}
	form := "unknown"
	if i != nil {
		form = i.Form(harness)
	}
	face := Object{"kind": form, "source": "unresolved"}
	if form != "unknown" {
		face["source"] = "harness-rule"
		if identity["harness_user_declared"] == true {
			face["source"] = "user-declared"
		}
	}
	// Unknown devices must not initiate application/process probes.
	if i != nil && device["known"] == true {
		app := i.HostApp()
		if host["kind"] == nil && app["id"] != nil {
			host = app
		}
		if app["verified"] == true && app["id"] == harness {
			form = "desktop"
			if harness == "dsh" {
				form = "web"
			}
			face = Object{"kind": form, "application": app["id"], "source": app["source"]}
		}
		facts := i.Facts()
		if value := object(facts["fields"])["form"]; value != nil && face["kind"] == "unknown" {
			face = Object{"kind": value, "source": "user-declared", "declaration_id": text(facts["id"])[:24]}
		}
	}
	execution := Object{}
	for _, k := range []string{"device", "asset_id", "platform", "redline", "archive", "known", "source", "declaration_id", "signals"} {
		if v, ok := device[k]; ok {
			execution[k] = v
		}
	}
	if task == nil {
		task = Object{"owner": nil, "status": "unbound", "verified": false}
	}
	status := "partial"
	if device["known"] != true {
		status = "unknown-device"
	} else if ready["commit"] == true {
		status = "ok"
	}
	value := Object{"schema_version": 2, "observed_at": time.Now().UTC().Format(time.RFC3339), "status": status,
		"usage": usage, "interface": face, "actor": Object{"kind": kind, "harness": identity["cli"],
			"harness_source": identity["cli_source"], "name": name, "model": m},
		"execution": execution, "caller": caller, "host": host, "checkout": checkout, "task": task, "readiness": ready}
	if provenance != nil {
		value["core"] = provenance
	}
	if device["known"] == true && ready["commit"] != true {
		value["next"] = "eacli session diagnose --json"
	}
	return value
}
