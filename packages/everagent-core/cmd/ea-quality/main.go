package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"time"

	q "github.com/Everloster/EverAgent/packages/everagent-core/internal/publicquality"
)

func main() { os.Exit(run()) }
func run() int {
	args := os.Args[1:]
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "ea-quality <disclosure|quick|full|context|catalog|privacy|links|index|scripts|policy|report|sampling> --repo-root <checkout> [--scope index|worktree|head] [--base <full-sha>] [--write]; quick is the lightweight disclosure compatibility entry, other audits are opt-in")
		return 2
	}
	command := args[0]
	f := flag.NewFlagSet("ea-quality "+command, flag.ContinueOnError)
	root := f.String("repo-root", "../..", "public checkout")
	defaultScope := "worktree"
	if command == "quick" || command == "disclosure" || command == "full" {
		defaultScope = "index"
	}
	scope := f.String("scope", defaultScope, "snapshot scope")
	base := f.String("base", "", "immutable comparison object ID (head scope only)")
	tempRoot := f.String("temp-root", "", "existing scratch parent outside any checkout")
	report := f.String("report", "", "repository-relative report for a quality check")
	write := f.Bool("write", false, "update generated indexes (index action, worktree scope only)")
	_ = f.Bool("json", true, "structured result")
	details := f.Bool("details", false, "include all quick/full diagnostics instead of the bounded summary")
	check := f.Bool("check", false, "explicit read-only check (the default)")
	if e := f.Parse(args[1:]); e != nil || f.NArg() != 0 {
		return 2
	}
	if *write && (command != "index" || *scope != "worktree" || *base != "" || *check) {
		fmt.Fprintln(os.Stderr, "--write requires index --scope worktree and cannot be combined with --check or --base")
		return 2
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	ctx, cancel := context.WithTimeout(ctx, 10*time.Minute)
	defer cancel()
	if command == "quick" || command == "disclosure" || command == "full" {
		check := q.CheckDisclosure
		if command == "full" {
			check = q.Check
		}
		out, err := check(ctx, q.CheckOptions{Root: *root, Scope: *scope, Base: *base, TempRoot: *tempRoot, Full: command == "full"})
		var result any = out
		if !*details {
			result = out.Summary()
		}
		if err != nil {
			return emit(map[string]any{"ok": false, "error": err.Error(), "result": result}, 1)
		}
		if !out.OK {
			return emit(result, 1)
		}
		return emit(result, 0)
	}
	c, e := q.Capture(ctx, *root, *scope)
	if e != nil {
		return emit(map[string]any{"ok": false, "error": e.Error()}, 1)
	}
	defer c.Close()
	if *base != "" {
		if e := c.CompareBase(*base); e != nil {
			return emit(map[string]any{"ok": false, "error": e.Error()}, 1)
		}
	}
	findings := []q.Finding{}
	out := map[string]any{"schema_version": 1, "scope": c.Scope, "head": c.Head, "base": c.Base, "index_tree": c.IndexTree}
	switch command {
	case "scripts":
		value, issues := q.ScriptCatalog(c.After)
		out["catalog"] = value
		findings = issues
		if *check {
			findings = q.CheckScriptIndex(c.After)
		}
	case "policy", "report", "sampling", "context":
		rules, err := q.LoadRules(c.After)
		if err != nil {
			return emit(map[string]any{"ok": false, "error": err.Error()}, 1)
		}
		if command == "policy" {
			out["policy"] = rules.Current
			break
		}
		reports, issues := q.Catalog(c.After)
		findings = append(findings, issues...)
		if command == "context" {
			result := q.AuditContext(c.After, rules, reports)
			out["context"] = result
			findings = append(findings, result.Findings...)
		} else if command == "sampling" {
			result := rules.Sampling(reports)
			out["sampling"] = result
			findings = append(findings, result.Findings...)
		} else {
			found := false
			for _, r := range reports {
				if r.Path != *report {
					continue
				}
				found = true
				result := rules.Evaluate(r)
				out["quality"] = result
				findings = append(findings, result.Findings...)
			}
			if !found {
				return emit(map[string]any{"ok": false, "error": "report-not-in-snapshot"}, 1)
			}
		}
	case "catalog":
		reports, issues := q.Catalog(c.After)
		out["reports"] = reports
		findings = issues
	case "privacy":
		result := q.AuditPrivacy(c, nil)
		out["privacy"] = result
		findings = result.Findings
	case "links":
		findings = q.CheckLinks(c.After, "README.md", true)
	case "index":
		if *write {
			result, err := q.WriteIndexes(c)
			out["written"] = result
			out["ok"] = err == nil
			if err != nil {
				out["error"] = err.Error()
				return emit(out, 1)
			}
			return emit(out, 0)
		}
		reports, issues := q.Catalog(c.After)
		findings = append(issues, q.CheckIndex(c.After, reports)...)
		findings = append(findings, q.CheckScriptIndex(c.After)...)
		out["report_count"] = len(reports)
	default:
		fmt.Fprintln(os.Stderr, "unsupported quality action")
		return 2
	}
	ok := true
	for _, f := range findings {
		if f.Severity == "error" {
			ok = false
		}
	}
	if e := c.Verify(); e != nil {
		ok = false
		out["error"] = e.Error()
	}
	out["findings"] = findings
	out["ok"] = ok
	code := 0
	if !ok {
		code = 1
	}
	return emit(out, code)
}
func emit(value any, code int) int {
	e := json.NewEncoder(os.Stdout)
	e.SetEscapeHTML(false)
	if e.Encode(value) != nil {
		return 1
	}
	return code
}
