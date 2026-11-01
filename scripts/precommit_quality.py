#!/usr/bin/env python3
"""Validate the exact staged snapshot before an EverAgent commit."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from .report_catalog import new_report_paths
except ImportError:
    from report_catalog import new_report_paths


ROOT = Path(__file__).resolve().parents[1]


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
        raise RuntimeError("cannot read staged paths")
    return {item for item in proc.stdout.split("\0") if item}


def report_for_sidecar(path: str) -> str | None:
    candidate = Path(path)
    if candidate.parent.name != ".quality":
        return None
    for suffix in (".evidence.json", ".review.json"):
        if candidate.name.endswith(suffix):
            report = candidate.parent.parent / f"{candidate.name[:-len(suffix)]}.md"
            return str(report) if (ROOT / report).is_file() else None
    return None


def report_audit_command(changed_paths: set[str], new_paths: set[str] | None = None) -> list[str]:
    return [sys.executable, "scripts/audit_reports.py", "--all", "--summary-only",
            *(f"--changed-path={path}" for path in sorted(changed_paths)),
            *(f"--new-path={path}" for path in sorted(new_paths or ()))]


def main() -> int:
    try:
        staged = git_paths("diff", "--cached", "--no-renames", "--name-only", "--diff-filter=ACMRTUXB")
        added_reports = {str(path.relative_to(ROOT)) for path in new_report_paths("--cached", root=ROOT)}
        modified_or_removed = git_paths("diff", "--cached", "--no-renames", "--name-only", "--diff-filter=DMRTUXB")
    except (RuntimeError, OSError):
        print("[precommit-quality] BLOCKED: cannot read staged snapshot", file=sys.stderr)
        return 1
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

    # This gate needs Git's old blobs as well as index blobs, not checkout files.
    if not run("incremental public content", [sys.executable, "scripts/audit_public_context.py", "--staged"], ROOT):
        return 1

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
            # Always check: a staged target deletion can break an unchanged README.
            ("root README links", [sys.executable, "scripts/check_readme_links.py"]),
            (
                "versioned report audit",
                report_audit_command(staged | modified_or_removed, added_reports),
            ),
        ]
        if staged & {"scripts/whoami_agent.py", "scripts/git_identity.py", "scripts/ecommit.sh",
                     "scripts/git_commit.py", "scripts/test_git_commit.py",
                     "scripts/test_whoami_agent.py", "scripts/test_git_identity.py"} or any(
                         path.startswith(("scripts/agent_identity/", "packages/everagent-core/"))
                         or path in {"scripts/agent_identity.py", "scripts/agent_model_declare.py",
                                     "scripts/core_bootstrap.py", "scripts/script-catalog.json",
                                     "scripts/script_catalog.py", "scripts/test_core_contracts.py", "scripts/test_model_observations.py",
                                     "config/git-policy.json"} for path in staged):
            checks.append((
                "agent identity regression",
                [sys.executable, "-m", "unittest", "scripts.test_whoami_agent",
                 "scripts.test_git_identity", "scripts.test_git_commit", "scripts.test_core_contracts",
                 "scripts.test_model_observations", "-q"],
            ))
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
