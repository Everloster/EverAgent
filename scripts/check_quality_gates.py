#!/usr/bin/env python3
"""Quality-gate validator for completed tasks.

For every task with status=done in any {project}/.project-task-state, run the
quality checks declared in tasks/T*.yaml spec.qualityGates and report PASS/FAIL.

Supported checks (auto-detected by name; unknown checks = WARN):

  structural:
    frontmatter_complete     -- report has YAML frontmatter w/ title, domain,
                                report_type, status, updated_on
    markdown_report          -- report file exists, .md, non-empty (>500 bytes)
    wiki_linked              -- state.context_links contains at least one wiki/* path
    transcript_attached      -- state.context_links points to a transcript file
                                (transcript* / *转录*)

  content (heuristic, WARN-only):
    mermaid_diagrams         -- body contains at least one ```mermaid block
    original_text_quotes     -- body contains at least 3 blockquote (>) lines
    *_table                  -- body contains a markdown table (|---|)
    comparison_matrix        -- body contains a markdown table AND a header row
                                with at least 4 columns
    benchmark_*_table        -- body contains a markdown table with header
                                containing the word 'Benchmark' or '基准'

  cross-reference:
    cross_reference_T<NNN>   -- body mentions T<NNN> at least once
    rfc_citation             -- body matches RFC \\d+ pattern

  experiment (ai-practice only):
    code_runs                -- src/<project>/ has at least one .py file
    experiment_notes_frontmatter -- experiments/*.md has YAML frontmatter
    training_curve_artifacts -- experiments/ has at least one .png/.svg/.npy
                                artifact or an embedded ![](path)
    decision_framework       -- experiments notes contain a 'decision' section

  trending (github-trending-analyzer only):
    json_summary             -- a .json sibling file exists next to the .md
                                report
    top10_review             -- body contains a table with ≥ 10 data rows
    trend_comparison_with_q1 -- body references 'Q1' or '2026-03' at least once

Design: cheap, deterministic, no NLP. Unknown check names produce WARN (not FAIL)
so spec evolution doesn't break the gate. Exits 0 if all required checks PASS or
WARN-only, 1 if any required check FAILS.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

import yaml


ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"

RFC_RE = re.compile(r"\bRFC\s*(\d+)\b", re.IGNORECASE)
CROSS_REF_RE = re.compile(r"\bT\d{3}\b")
TABLE_RE = re.compile(r"^\s*\|.*\|.*\|.*$", re.MULTILINE)
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|[\s\-:|]+\|\s*$", re.MULTILINE)
MERMAID_RE = re.compile(r"```mermaid", re.IGNORECASE)
BLOCKQUOTE_RE = re.compile(r"^\s*>\s", re.MULTILINE)
H1_RE = re.compile(r"^#\s+\S+", re.MULTILINE)
DECISION_RE = re.compile(r"##\s*.*[Dd]ecision|##\s*.*决策|##\s*.*判断", re.MULTILINE)
TRANSCRIPT_GLOB = ("transcript*", "*转录*", "*transcript*.md")
Q1_RE = re.compile(r"\bQ1\b|2026-03|2026-04|2026-Q1", re.IGNORECASE)


# ---------- data ----------------------------------------------------------


@dataclass
class TaskContext:
    task_id: str
    project: str
    spec: dict
    state: dict
    state_file: Path
    checks: list[dict] = field(default_factory=list)
    report_path: Path | None = None
    body: str = ""
    frontmatter: dict = field(default_factory=dict)


# ---------- helpers -------------------------------------------------------


def load_active_specs() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in sorted(TASKS_DIR.glob("T*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        tid = (d.get("metadata") or {}).get("id")
        if tid:
            out[tid] = d
    return out


def load_all_states() -> dict[str, dict]:
    out: dict[str, dict] = {}
    candidates = [ROOT / ".project-task-state"]
    for sub in ROOT.iterdir():
        if sub.is_dir() and (sub / ".project-task-state").exists():
            candidates.append(sub / ".project-task-state")
    for sf in candidates:
        data = yaml.safe_load(sf.read_text(encoding="utf-8")) or []
        for entry in data:
            tid = entry.get("id")
            if tid and tid not in out:
                out[tid] = {"entry": entry, "file": sf}
    return out


SUBPROJECT_REPORT_DIRS = {
    "ai-learning": ["reports", "papers"],
    "cs-learning": ["reports", "papers"],
    "philosophy-learning": ["reports", "papers"],
    "psychology-learning": ["reports", "papers"],
    "biology-learning": ["reports", "papers"],
    "podcast-learning": ["reports", "papers"],
    "ai-practice": ["experiments", "src"],
    "github-trending-analyzer": [
        "github-trending-reports",
        "everloster-star-analysis/reports",
        "reports",
    ],
}


def _score_match(md_path: Path, target: str) -> int:
    """Heuristic: how well does this .md match the task target string?

    Returns 0 if no signal, positive int if filename or frontmatter title
    shares substrings with target. Higher = better match.
    """
    if not target:
        return 0
    target_tokens = {t for t in re.split(r"[\s/:×x_，,。、]+", target) if len(t) >= 2}
    score = 0
    fname_tokens = {t for t in re.split(r"[_]+", md_path.stem) if len(t) >= 2}
    score += len(target_tokens & fname_tokens) * 2
    try:
        fm, _ = load_frontmatter_and_body(md_path)
        title = str(fm.get("title", ""))
        title_tokens = {t for t in re.split(r"[\s/:×x_，,。、()]+", title) if len(t) >= 2}
        score += len(target_tokens & title_tokens) * 3
    except Exception:
        pass
    return score


def find_report(project: str, context_links: list[str], target: str = "") -> Path | None:
    """Resolve the report file for a task.

    Priority:
    1. context_links (if any link points to an existing .md)
    2. Scan subproject-specific report dirs, pick best title/filename match
       against task target; fall back to most-recent if no match.
    """
    if context_links:
        for link in context_links:
            p = ROOT / link
            if p.exists() and p.is_file() and p.suffix == ".md":
                return p
    proj_dir = ROOT / project
    if not proj_dir.exists():
        return None
    candidates: list[Path] = []
    for subdir in SUBPROJECT_REPORT_DIRS.get(project, ["reports"]):
        d = proj_dir / subdir
        if d.exists():
            candidates.extend(d.rglob("*.md"))
    if not candidates:
        return None
    if target:
        scored = [(c, _score_match(c, target)) for c in candidates]
        scored.sort(key=lambda x: (-x[1], -x[0].stat().st_mtime))
        best, best_score = scored[0]
        if best_score > 0:
            return best
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_frontmatter_and_body(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5 :]
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


# ---------- check functions ----------------------------------------------


def make_check(name: str) -> Callable[[TaskContext], tuple[str, str]]:
    """Return (status, message). status ∈ {PASS, FAIL, WARN, SKIP}."""

    def check_frontmatter(ctx: TaskContext) -> tuple[str, str]:
        if not ctx.report_path:
            return "FAIL", "no report file"
        required = ["title", "domain", "report_type", "status", "updated_on"]
        missing = [k for k in required if k not in ctx.frontmatter]
        if missing:
            return "FAIL", f"frontmatter missing: {missing}"
        return "PASS", f"frontmatter complete ({len(ctx.frontmatter)} fields)"

    def check_markdown_report(ctx: TaskContext) -> tuple[str, str]:
        if not ctx.report_path or not ctx.report_path.exists():
            return "FAIL", "report file missing"
        size = ctx.report_path.stat().st_size
        if size < 500:
            return "FAIL", f"report too small ({size} bytes)"
        return "PASS", f"report exists, {size} bytes"

    def check_wiki_linked(ctx: TaskContext) -> tuple[str, str]:
        links = ctx.state.get("context_links") or []
        wiki_links = [l for l in links if "wiki/" in str(l)]
        if not wiki_links:
            return "WARN", "no wiki/* link in state.context_links"
        return "PASS", f"{len(wiki_links)} wiki link(s)"

    def check_transcript_attached(ctx: TaskContext) -> tuple[str, str]:
        links = [str(l) for l in (ctx.state.get("context_links") or [])]
        proj_dir = ROOT / ctx.project
        # Scan links + project root for any transcript-like file
        candidates = [ROOT / l for l in links]
        candidates.extend(proj_dir.rglob("transcript*"))
        candidates.extend(proj_dir.rglob("*转录*"))
        hit = next((p for p in candidates if p.exists() and p.is_file()), None)
        if hit:
            return "PASS", f"transcript: {hit.relative_to(ROOT)}"
        return "WARN", "no transcript file detected (allowed for synthesis tasks)"

    def check_mermaid(ctx: TaskContext) -> tuple[str, str]:
        n = len(MERMAID_RE.findall(ctx.body))
        if n >= 1:
            return "PASS", f"{n} mermaid block(s)"
        return "WARN", "no ```mermaid block found"

    def check_quotes(ctx: TaskContext) -> tuple[str, str]:
        n = len(BLOCKQUOTE_RE.findall(ctx.body))
        if n >= 3:
            return "PASS", f"{n} blockquote lines"
        return "WARN", f"only {n} blockquote line(s) (expected ≥3 for text_analysis)"

    def check_table(ctx: TaskContext) -> tuple[str, str]:
        n = len(TABLE_SEPARATOR_RE.findall(ctx.body))
        if n >= 1:
            return "PASS", f"{n} markdown table(s)"
        return "WARN", "no markdown table found"

    def check_comparison_matrix(ctx: TaskContext) -> tuple[str, str]:
        tables = TABLE_RE.findall(ctx.body)
        wide = [t for t in tables if t.count("|") >= 6]  # ≥4 columns
        if wide:
            return "PASS", f"{len(wide)} wide table(s)"
        return "WARN", "no comparison-style wide table found"

    def check_benchmark_table(ctx: TaskContext) -> tuple[str, str]:
        # Generic: any table whose header row contains 'benchmark' or '基准'
        for m in TABLE_RE.finditer(ctx.body):
            header = m.group(0).lower()
            if "benchmark" in header or "基准" in header or "评测" in header:
                return "PASS", "benchmark table header detected"
        return "WARN", "no benchmark/基准 table header"

    def check_cross_reference(ctx: TaskContext) -> tuple[str, str]:
        target = name.split("_")[-1]  # e.g. T060
        n = ctx.body.count(target)
        if n >= 1:
            return "PASS", f"{target} referenced {n}× in body"
        return "FAIL", f"{target} not referenced in body"

    def check_rfc_citation(ctx: TaskContext) -> tuple[str, str]:
        ms = RFC_RE.findall(ctx.body)
        if ms:
            return "PASS", f"RFC citations: {sorted(set(ms))[:3]}"
        return "WARN", "no RFC NNNN citations"

    def check_code_runs(ctx: TaskContext) -> tuple[str, str]:
        proj_dir = ROOT / ctx.project
        py_files = list((proj_dir / "src").rglob("*.py")) if (proj_dir / "src").exists() else []
        if py_files:
            return "PASS", f"{len(py_files)} .py file(s) in src/"
        return "WARN", "no .py files in src/"

    def check_exp_notes(ctx: TaskContext) -> tuple[str, str]:
        proj_dir = ROOT / ctx.project
        exp_files = list((proj_dir / "experiments").rglob("*.md")) if (proj_dir / "experiments").exists() else []
        if not exp_files:
            return "WARN", "no experiments/*.md"
        # Convention varies: some files use `type: experiment_analysis`,
        # others use `domain:`. Require `title`; accept either type/domain.
        for p in exp_files:
            fm, _ = load_frontmatter_and_body(p)
            if "title" in fm and ("type" in fm or "domain" in fm):
                return "PASS", f"{p.name} has frontmatter"
        return "FAIL", "experiments/*.md missing title or type/domain"

    def check_training_artifacts(ctx: TaskContext) -> tuple[str, str]:
        proj_dir = ROOT / ctx.project
        artifacts = []
        if (proj_dir / "experiments").exists():
            for ext in ("*.png", "*.svg", "*.npy", "*.json"):
                artifacts.extend((proj_dir / "experiments").rglob(ext))
        body_artifacts = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", ctx.body)
        if artifacts or body_artifacts:
            return "PASS", f"{len(artifacts)} file(s) + {len(body_artifacts)} image ref(s)"
        return "WARN", "no training-curve artifacts detected"

    def check_decision_framework(ctx: TaskContext) -> tuple[str, str]:
        if DECISION_RE.search(ctx.body):
            return "PASS", "decision section present"
        return "WARN", "no 'decision / 决策' section"

    def check_json_summary(ctx: TaskContext) -> tuple[str, str]:
        if not ctx.report_path:
            return "FAIL", "no report path"
        sibling = ctx.report_path.with_suffix(".json")
        if sibling.exists():
            return "PASS", f"sibling JSON: {sibling.name}"
        # Try month directory
        for j in ctx.report_path.parent.glob("*.json"):
            return "PASS", f"JSON sibling: {j.name}"
        return "WARN", "no .json sibling found"

    def check_top10_review(ctx: TaskContext) -> tuple[str, str]:
        # Count data rows in tables; look for ≥10
        tables = []
        in_table = False
        rows = 0
        for line in ctx.body.splitlines():
            if TABLE_SEPARATOR_RE.match(line):
                in_table = True
                rows = 0
                continue
            if in_table and TABLE_RE.match(line):
                rows += 1
            elif in_table and not TABLE_RE.match(line):
                if rows >= 10:
                    tables.append(rows)
                in_table = False
        if any(r >= 10 for r in tables):
            return "PASS", f"table(s) with ≥10 rows: {tables}"
        return "WARN", "no table with ≥10 rows"

    def check_q1_comparison(ctx: TaskContext) -> tuple[str, str]:
        ms = Q1_RE.findall(ctx.body)
        if ms:
            return "PASS", f"Q1 references: {len(ms)}"
        return "WARN", "no Q1 / 2026-03 comparison reference"

    def check_meta_analysis(ctx: TaskContext) -> tuple[str, str]:
        # Just check body length + structure
        if len(ctx.body) > 5000 and H1_RE.search(ctx.body):
            return "PASS", f"meta-analysis length={len(ctx.body)}, has H1"
        return "WARN", "body < 5000 chars or no H1"

    def check_evidence_graded(ctx: TaskContext) -> tuple[str, str]:
        # Look for evidence-grade markers like "[证据: ...]" or "证据等级"
        if "证据" in ctx.body or "evidence" in ctx.body.lower():
            return "PASS", "evidence markers found"
        return "WARN", "no explicit evidence markers (heuristic)"

    def check_timeline(ctx: TaskContext) -> tuple[str, str]:
        if "时间线" in ctx.body or "Timeline" in ctx.body or "timeline" in ctx.body.lower():
            return "PASS", "timeline section found"
        return "WARN", "no timeline section detected"

    registry: dict[str, Callable[[TaskContext], tuple[str, str]]] = {
        "frontmatter_complete": check_frontmatter,
        "markdown_report": check_markdown_report,
        "wiki_linked": check_wiki_linked,
        "transcript_attached": check_transcript_attached,
        "mermaid_diagrams": check_mermaid,
        "original_text_quotes": check_quotes,
        "feature_comparison_table": check_table,
        "parameter_comparison_table": check_table,
        "benchmark_table": check_benchmark_table,
        "benchmark_comparison_table": check_comparison_matrix,
        "comparison_matrix": check_comparison_matrix,
        "cross_reference_T060": check_cross_reference,
        "cross_reference_T062": check_cross_reference,
        "rfc_citation": check_rfc_citation,
        "code_runs": check_code_runs,
        "experiment_notes_frontmatter": check_exp_notes,
        "training_curve_artifacts": check_training_artifacts,
        "decision_framework": check_decision_framework,
        "json_summary": check_json_summary,
        "top10_review": check_top10_review,
        "trend_comparison_with_q1": check_q1_comparison,
        "meta_analysis_cited": check_meta_analysis,
        "evidence_graded": check_evidence_graded,
        "timeline_table": check_timeline,
    }

    fn = registry.get(name)
    if fn is None:
        return lambda _ctx: ("WARN", f"unknown check '{name}' (not in registry)")
    return fn


# ---------- main ---------------------------------------------------------


def build_context(specs: dict, states: dict) -> list[TaskContext]:
    ctxs: list[TaskContext] = []
    for tid, state_ref in states.items():
        state = state_ref["entry"]
        if state.get("status") != "done":
            continue
        spec = specs.get(tid)
        if not spec:
            continue  # historical state-only task, skip
        project = state.get("project") or (spec.get("metadata") or {}).get("project", "")
        checks = (spec.get("spec") or {}).get("qualityGates") or []
        report = find_report(
            project,
            state.get("context_links") or [],
            target=state.get("target") or "",
        )
        body = ""
        fm: dict = {}
        if report:
            fm, body = load_frontmatter_and_body(report)
        ctxs.append(
            TaskContext(
                task_id=tid,
                project=project,
                spec=spec,
                state=state,
                state_file=state_ref["file"],
                checks=checks,
                report_path=report,
                body=body,
                frontmatter=fm,
            )
        )
    return ctxs


def render_html(ctxs: list[TaskContext], totals: dict[str, int], run_date: str) -> str:
    """Render self-contained HTML (no external CSS/JS) for browser viewing."""
    css = """
    body { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif;
           max-width: 1100px; margin: 2em auto; padding: 0 1em; color: #222; }
    h1 { font-size: 1.6em; border-bottom: 2px solid #333; padding-bottom: 0.3em; }
    h2 { font-size: 1.3em; margin-top: 1.5em; }
    .summary { display: flex; gap: 1.5em; padding: 1em; background: #f5f5f7;
               border-radius: 8px; margin: 1em 0; }
    .summary-item { text-align: center; }
    .summary-num { font-size: 2em; font-weight: 600; }
    .pass { color: #1a7f37; }
    .warn { color: #9a6700; }
    .fail { color: #cf222e; }
    .skip { color: #6e7781; }
    table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.92em; }
    th, td { border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; vertical-align: top; }
    th { background: #f6f8fa; font-weight: 600; }
    tr:nth-child(even) { background: #fafbfc; }
    .task-id { font-family: 'SF Mono', Menlo, monospace; font-weight: 600; }
    .project { color: #6e7781; font-size: 0.9em; }
    .status-PASS { color: #1a7f37; font-weight: 600; }
    .status-FAIL { color: #cf222e; font-weight: 600; }
    .status-WARN { color: #9a6700; font-weight: 600; }
    .req { color: #cf222e; font-size: 0.8em; }
    .opt { color: #6e7781; font-size: 0.8em; }
    code { background: #f6f8fa; padding: 1px 4px; border-radius: 3px; font-size: 0.9em; }
    .footer { color: #6e7781; font-size: 0.85em; margin-top: 2em; text-align: center; }
    """
    rows = []
    for ctx in ctxs:
        report = str(ctx.report_path.relative_to(ROOT)) if ctx.report_path else "<missing>"
        for chk in ctx.checks:
            name = chk.get("check")
            required = chk.get("required", True)
            fn = make_check(name)
            status, msg = fn(ctx)
            cls = f"status-{status}"
            req_cls = "req" if required else "opt"
            req_label = "required" if required else "optional"
            rows.append(
                f'<tr><td><span class="task-id">{ctx.task_id}</span><br>'
                f'<span class="project">{ctx.project}</span></td>'
                f'<td><code>{name}</code><br><span class="{req_cls}">{req_label}</span></td>'
                f'<td><a href="{report}"><code>{report}</code></a></td>'
                f'<td class="{cls}">{status}</td>'
                f'<td>{msg}</td></tr>'
            )

    body_rows = "\n".join(rows) if rows else '<tr><td colspan="5">no checks</td></tr>'
    summary_html = f"""
<div class="summary">
    <div class="summary-item"><div class="summary-num pass">{totals['pass']}</div>PASS</div>
    <div class="summary-item"><div class="summary-num warn">{totals['warn']}</div>WARN</div>
    <div class="summary-item"><div class="summary-num fail">{totals['fail']}</div>FAIL</div>
    <div class="summary-item"><div class="summary-num skip">{totals['skip']}</div>SKIP</div>
    <div class="summary-item"><div class="summary-num">{len(ctxs)}</div>tasks</div>
</div>
"""
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Quality Gates Report — {run_date}</title>
<style>{css}</style>
</head>
<body>
<h1>Quality Gates Report</h1>
<p>Generated {run_date} · {len(ctxs)} done task(s) checked</p>
{summary_html}
<h2>Check Matrix</h2>
<table>
<thead><tr><th>Task / Project</th><th>Check</th><th>Report</th><th>Status</th><th>Message</th></tr></thead>
<tbody>
{body_rows}
</tbody>
</table>
<p class="footer">EverAgent · scripts/check_quality_gates.py · self-contained HTML (no external deps)</p>
</body>
</html>
"""
    return html


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", help="only check this single task")
    parser.add_argument("--html", metavar="PATH",
                        help="also write self-contained HTML report to PATH")
    args, _ = parser.parse_known_args()

    specs = load_active_specs()
    states = load_all_states()
    ctxs = build_context(specs, states)
    if args.task_id:
        ctxs = [c for c in ctxs if c.task_id == args.task_id]
    if not ctxs:
        print(f"no done tasks to check (filter={args.task_id})")
        return 0

    total_pass = total_warn = total_fail = total_skip = 0
    fail_tasks: list[str] = []

    print(f"checking {len(ctxs)} done task(s):\n")
    for ctx in ctxs:
        print(f"── {ctx.task_id} [{ctx.project}] ──")
        if ctx.report_path:
            print(f"   report: {ctx.report_path.relative_to(ROOT)}")
        else:
            print(f"   report: ⚠ NOT FOUND")
        for chk in ctx.checks:
            name = chk.get("check")
            required = chk.get("required", True)
            fn = make_check(name)
            status, msg = fn(ctx)
            icon = {"PASS": "✓", "WARN": "⚠", "FAIL": "✗", "SKIP": "○"}.get(status, "?")
            req_tag = "" if required else " (optional)"
            print(f"   {icon} {name}{req_tag}: {msg}")
            if status == "PASS":
                total_pass += 1
            elif status == "WARN":
                total_warn += 1
            elif status == "FAIL":
                total_fail += 1
                if required:
                    fail_tasks.append(f"{ctx.task_id}/{name}")
            else:
                total_skip += 1
        print()

    print(f"summary: {total_pass} PASS, {total_warn} WARN, {total_fail} FAIL")
    if fail_tasks:
        print(f"\nrequired failures: {fail_tasks}")

    if args.html:
        run_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        html = render_html(
            ctxs,
            {"pass": total_pass, "warn": total_warn, "fail": total_fail, "skip": total_skip},
            run_date,
        )
        out = Path(args.html)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"\n✓ HTML report written: {out}")

    if fail_tasks:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())