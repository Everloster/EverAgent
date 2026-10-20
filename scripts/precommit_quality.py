#!/usr/bin/env python3
"""Validate the exact staged snapshot before an EverAgent commit."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOTS = {
    "ai-learning/reports",
    "cs-learning/reports",
    "philosophy-learning/reports",
    "psychology-learning/reports",
    "biology-learning/reports",
    "ai-practice/experiments",
    "podcast-learning/reports",
    "github-trending-analyzer/reports",
    "web-surfing/reports",
}


def run(label: str, command: list[str], cwd: Path) -> bool:
    print(f"[precommit-quality] {label}")
    proc = subprocess.run(command, cwd=cwd, check=False)
    if proc.returncode != 0:
        print(f"[precommit-quality] BLOCKED: {label} failed", file=sys.stderr)
        return False
    return True


def git_paths(*args: str) -> set[str]:
    proc = subprocess.run(
        ["git", *args, "-z"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return set()
    return {item for item in proc.stdout.split("\0") if item}


def is_report(path: str) -> bool:
    candidate = Path(path)
    if candidate.suffix.lower() != ".md" or "transcripts" in candidate.parts:
        return False
    text = candidate.as_posix()
    if text.startswith("ai-practice/experiments/"):
        return candidate.name.startswith("exp_") or "评估笔记" in candidate.name
    return any(text.startswith(f"{root}/") for root in REPORT_ROOTS)


def report_for_sidecar(path: str) -> str | None:
    candidate = Path(path)
    if candidate.parent.name != ".quality":
        return None
    for suffix in (".evidence.json", ".review.json"):
        if candidate.name.endswith(suffix):
            report = candidate.parent.parent / f"{candidate.name[:-len(suffix)]}.md"
            return str(report) if (ROOT / report).is_file() else None
    return None


def main() -> int:
    staged = git_paths("diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB")
    added = git_paths("diff", "--cached", "--name-only", "--diff-filter=A")
    modified_or_removed = git_paths("diff", "--cached", "--name-only", "--diff-filter=DMRTUXB")
    changed_policy_archives = sorted(
        path
        for path in modified_or_removed
        if path.startswith("config/report-quality-policies/")
    )
    if changed_policy_archives:
        print(
            "[precommit-quality] BLOCKED: archived report policies are immutable; add a new policy_id instead: "
            + ", ".join(changed_policy_archives),
            file=sys.stderr,
        )
        return 1
    added_reports = sorted(path for path in added if is_report(path))
    orphan_sidecars = sorted(
        path
        for path in staged
        if Path(path).parent.name == ".quality" and report_for_sidecar(path) is None
    )
    if orphan_sidecars:
        print(
            "[precommit-quality] BLOCKED: orphan quality artifacts: " + ", ".join(orphan_sidecars),
            file=sys.stderr,
        )
        return 1
    sidecar_reports = sorted({
        report
        for path in staged
        if (report := report_for_sidecar(path)) is not None
    })

    with tempfile.TemporaryDirectory(prefix="everagent-staged-") as directory:
        snapshot = Path(directory)
        export = subprocess.run(
            ["git", "checkout-index", "--all", "--force", f"--prefix={snapshot}/"],
            cwd=ROOT,
            check=False,
        )
        if export.returncode != 0:
            print("[precommit-quality] BLOCKED: cannot materialize staged snapshot", file=sys.stderr)
            return 1

        checks: list[tuple[str, list[str]]] = [
            (
                "versioned report audit",
                [sys.executable, "scripts/audit_reports.py", "--all", "--summary-only"],
            ),
        ]
        if staged & {"scripts/whoami_agent.py", "scripts/git_identity.py", "scripts/ecommit.sh",
                     "scripts/test_whoami_agent.py", "scripts/test_git_identity.py"}:
            checks.append((
                "agent identity regression",
                [sys.executable, "-m", "unittest", "scripts.test_whoami_agent", "scripts.test_git_identity", "-q"],
            ))
        if added_reports:
            checks.append(
                (
                    "new report contract",
                    [sys.executable, "scripts/audit_reports.py", "--strict", *added_reports],
                )
            )
        for report in sidecar_reports:
            checks.append(
                (
                    f"quality sidecar: {report}",
                    [sys.executable, "scripts/report_quality.py", "check", report],
                )
            )
        checks.extend(
            [
                ("report index consistency", [sys.executable, "scripts/reindex.py", "--check"]),
                ("context evaluation", [sys.executable, "scripts/eval_report_context.py"]),
            ]
        )
        for label, command in checks:
            if not run(label, command, snapshot):
                return 1

    print("[precommit-quality] all gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
