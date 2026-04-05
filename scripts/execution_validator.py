#!/usr/bin/env python3
"""
Execution Validator — 任务执行输入/输出标准化校验

适用范围：所有学习型子Agent（ai-learning / cs-learning / philosophy-learning / psychology-learning / biology-learning）
参考：docs/EXECUTION_SCHEMA.md

校验模式：
  --mode=input   任务领取前校验
  --mode=output  任务完成后校验
  --mode=self-check  校验脚本自身

返回码：
  0  校验通过
  1  校验失败
  2  脚本错误
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Project paths ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
TASK_BOARD = ROOT / "docs" / "LEARNING_PROJECTS_TASK_BOARD.md"
EXECUTION_SCHEMA = ROOT / "docs" / "EXECUTION_SCHEMA.md"

PROJECTS = {
    "ai-learning": ROOT / "ai-learning",
    "cs-learning": ROOT / "cs-learning",
    "philosophy-learning": ROOT / "philosophy-learning",
    "psychology-learning": ROOT / "psychology-learning",
    "biology-learning": ROOT / "biology-learning",
    "github-trending-analyzer": ROOT / "github-trending-analyzer",
}

LEARNING_PROJECTS = {
    name: path for name, path in PROJECTS.items() if name != "github-trending-analyzer"
}

# ── ISO8601 正则 ─────────────────────────────────────────────────────────────────
# 接受两种格式：
#   1. 简单格式：YYYY-MM-DD（如 2026-04-05）
#   2. 完整格式：YYYY-MM-DDTHH:MM:SS+08:00 或 YYYY-MM-DDTHH:MM:SSZ
ISO8601_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\+\d{2}:\d{2}|Z)?)?$"
)
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")

# ── Frontmatter ─────────────────────────────────────────────────────────────────
REQUIRED_FRONTMATTER_KEYS = {"title", "domain", "report_type", "status", "updated_on"}
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

# ── Task Schema ─────────────────────────────────────────────────────────────────
VALID_TASK_TYPES = {
    "paper_analysis",
    "knowledge_report",
    "text_analysis",
    "concept_report",
    "project_optimization",
    "new_project",
    "maintenance",
}
VALID_STATUS = {"open", "claimed", "in_progress", "done", "failed", "abandoned"}


@dataclass
class ValidationIssue:
    severity: str  # ERROR | WARN
    field: str
    message: str


@dataclass
class ValidationResult:
    passed: bool
    task_id: str
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_error(self, field: str, message: str) -> None:
        self.issues.append(ValidationIssue("ERROR", field, message))
        self.passed = False

    def add_warning(self, field: str, message: str) -> None:
        self.issues.append(ValidationIssue("WARN", field, message))


# ── 解析工具 ─────────────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return None
    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def parse_task_from_board(task_id: str) -> Optional[dict[str, str]]:
    """从 Task Board 中解析指定 task_id 的任务数据"""
    if not TASK_BOARD.exists():
        return None
    text = TASK_BOARD.read_text(encoding="utf-8")
    yaml_blocks = re.findall(r"```yaml\n(.*?)```", text, re.DOTALL)
    for block in yaml_blocks:
        chunks = re.split(r"\n(?=- id:)", block.strip())
        for chunk in chunks:
            if not chunk.strip():
                continue
            task: dict[str, str] = {}
            for line in chunk.splitlines():
                line = line.strip().lstrip("- ")
                if ":" in line:
                    key, _, value = line.partition(":")
                    task[key.strip()] = value.strip().strip('"')
            if task.get("id") == task_id:
                return task
    return None


def get_project_for_agent() -> Optional[str]:
    """根据当前工作目录推断项目名称"""
    # 如果从项目子目录运行，可以推断项目名
    # 这里主要作为备用
    return None


# ── Input 校验 ──────────────────────────────────────────────────────────────────

def validate_input_schema(
    task_id: str,
    project: Optional[str] = None,
) -> ValidationResult:
    """
    校验任务输入（领取前调用）
    对应 EXECUTION_SCHEMA.md §1
    """
    result = ValidationResult(passed=True, task_id=task_id)

    # 1. 检查 Task Board 存在性
    if not TASK_BOARD.exists():
        result.add_error("task_board", f"Task Board not found: {TASK_BOARD}")
        return result

    # 2. 解析 Task Board 中的任务
    task = parse_task_from_board(task_id)
    if task is None:
        result.add_error("task_id", f"Task {task_id} not found in Task Board")
        return result

    # 3. 校验 task_id 非空（已在上面确保存在）

    # 4. 校验 project 匹配
    task_project = task.get("project", "")
    if project and task_project and project != task_project:
        result.add_error("project", f"Project mismatch: expected {task_project}, got {project}")

    # 5. 校验 type 有效
    task_type = task.get("type", "")
    if task_type and task_type not in VALID_TASK_TYPES:
        result.add_warning("type", f"Unknown task type: {task_type}")

    # 6. 校验 target 非空
    target = task.get("target", "")
    if not target:
        result.add_warning("target", "Task target is empty")

    # 7. 校验 status 为 open（领取时才检查）
    status = task.get("status", "")
    if status != "open":
        result.add_warning("status", f"Task status is '{status}', expected 'open' for new claims")

    # 8. 校验 claimed_by / claimed_at 为 null
    claimed_by = task.get("claimed_by", "")
    if claimed_by and claimed_by != "null":
        result.add_warning("claimed_by", f"Task already claimed by {claimed_by}")

    # 9. 校验 EXECUTION_SCHEMA.md 存在
    if not EXECUTION_SCHEMA.exists():
        result.add_warning("schema", f"EXECUTION_SCHEMA.md not found: {EXECUTION_SCHEMA}")

    # 10. 校验项目目录存在
    if task_project and task_project in PROJECTS:
        project_path = PROJECTS[task_project]
        if not project_path.exists():
            result.add_error("project_path", f"Project directory not found: {project_path}")
        else:
            # 11. 校验 CONTEXT.md 存在
            context_path = project_path / "CONTEXT.md"
            if not context_path.exists():
                result.add_warning("context", f"CONTEXT.md not found: {context_path}")

    return result


# ── Output 校验 ─────────────────────────────────────────────────────────────────

def validate_output_schema(
    task_id: str,
    project: Optional[str] = None,
) -> ValidationResult:
    """
    校验任务输出（完成后调用）
    对应 EXECUTION_SCHEMA.md §2
    """
    result = ValidationResult(passed=True, task_id=task_id)

    # 1. 检查 Task Board 存在性
    if not TASK_BOARD.exists():
        result.add_error("task_board", f"Task Board not found: {TASK_BOARD}")
        return result

    # 2. 解析 Task Board 中的任务
    task = parse_task_from_board(task_id)
    if task is None:
        result.add_error("task_id", f"Task {task_id} not found in Task Board")
        return result

    # 3. 校验 task_id 一致（已在上面确保存在）

    # 4. 校验 status 为 done 或 failed
    status = task.get("status", "")
    if status not in ("done", "failed"):
        result.add_warning("status", f"Task status is '{status}', expected 'done' or 'failed'")

    # 5. 校验 done_at / failed_reason
    done_at = task.get("done_at", "")
    failed_reason = task.get("failed_reason", "")

    if status == "done":
        if not done_at or done_at == "null":
            result.add_error("done_at", "status=done but done_at is null")
        elif not ISO8601_RE.match(done_at):
            result.add_warning("done_at", f"done_at may not be ISO8601: {done_at}")
    elif status == "failed":
        if not failed_reason or failed_reason == "null":
            result.add_error("failed_reason", "status=failed but failed_reason is null")

    # 6. 校验 claimed_by 非空
    claimed_by = task.get("claimed_by", "")
    if not claimed_by or claimed_by == "null":
        result.add_warning("claimed_by", "Task claimed_by is null")

    # 7. 校验 started_at 非空（如果 status 不是 open）
    if status != "open" and status != "claimed":
        started_at = task.get("started_at", "")
        if not started_at or started_at == "null":
            result.add_warning("started_at", "Task started_at is null for non-open task")

    # 8. 校验 project 目录存在
    task_project = task.get("project", "")
    if task_project and task_project in PROJECTS:
        project_path = PROJECTS[task_project]
        if not project_path.exists():
            result.add_error("project_path", f"Project directory not found: {project_path}")
        else:
            # 9. 校验 CONTEXT.md 已更新
            context_path = project_path / "CONTEXT.md"
            if not context_path.exists():
                result.add_warning("context", f"CONTEXT.md not found: {context_path}")

            # 10. 校验 reports 目录存在
            reports_dir = project_path / "reports"
            if not reports_dir.exists():
                result.add_warning("reports", f"reports directory not found: {reports_dir}")

    # 11. 校验 frontmatter（如果创建了新报告）
    if status == "done":
        report_issues = _validate_reports_frontmatter(task_project, project_path if task_project in PROJECTS else None)
        result.issues.extend(report_issues)

    return result


def _validate_reports_frontmatter(
    project: str,
    project_path: Optional[Path],
) -> list[ValidationIssue]:
    """校验项目最近创建的报告的 frontmatter"""
    issues: list[ValidationIssue] = []
    if not project_path:
        return issues

    reports_dir = project_path / "reports"
    if not reports_dir.exists():
        return issues

    # 获取最近修改的 3 个报告文件
    report_files = sorted(
        (p for p in reports_dir.rglob("*.md") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:3]

    for report_path in report_files:
        text = report_path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm is None:
            issues.append(ValidationIssue(
                "ERROR",
                str(report_path.relative_to(ROOT)),
                "missing YAML frontmatter"
            ))
            continue

        missing_keys = REQUIRED_FRONTMATTER_KEYS - set(fm)
        if missing_keys:
            issues.append(ValidationIssue(
                "WARN",
                str(report_path.relative_to(ROOT)),
                f"frontmatter missing keys: {', '.join(sorted(missing_keys))}"
            ))

        # 校验 domain 与项目一致
        domain = fm.get("domain", "")
        if domain and project not in domain.lower():
            issues.append(ValidationIssue(
                "WARN",
                str(report_path.relative_to(ROOT)),
                f"frontmatter domain '{domain}' may not match project '{project}'"
            ))

    return issues


# ── Self-check 模式 ─────────────────────────────────────────────────────────────

def validate_self_check() -> ValidationResult:
    """校验脚本自身是否正确配置"""
    result = ValidationResult(passed=True, task_id="self-check")

    # 1. 检查 EXECUTION_SCHEMA.md 存在
    if not EXECUTION_SCHEMA.exists():
        result.add_error("schema", f"EXECUTION_SCHEMA.md not found: {EXECUTION_SCHEMA}")
    else:
        text = EXECUTION_SCHEMA.read_text(encoding="utf-8")
        required_sections = ["§1", "§2", "§3", "§4"]
        for section in required_sections:
            if section not in text:
                result.add_error("schema", f"Missing section {section} in EXECUTION_SCHEMA.md")

    # 2. 检查 TASK_BOARD 存在
    if not TASK_BOARD.exists():
        result.add_error("task_board", f"Task Board not found: {TASK_BOARD}")

    # 3. 检查所有项目目录存在
    for name, path in PROJECTS.items():
        if not path.exists():
            result.add_warning("project", f"Project directory not found: {path} (expected for {name})")

    # 4. 检查 validate_workspace.py 存在（作为依赖）
    validate_workspace = ROOT / "scripts" / "validate_workspace.py"
    if not validate_workspace.exists():
        result.add_warning("dependency", f"validate_workspace.py not found: {validate_workspace}")

    return result


# ── CLI 入口 ────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execution Validator — 任务执行输入/输出标准化校验",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
返回码：
  0  校验通过
  1  校验失败
  2  脚本错误（文件不存在、参数错误等）

示例：
  python3 scripts/execution_validator.py --mode=input --task-id=T001
  python3 scripts/execution_validator.py --mode=output --task-id=T001 --project=ai-learning
  python3 scripts/execution_validator.py --mode=self-check
        """,
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["input", "output", "self-check"],
        help="校验模式",
    )
    parser.add_argument(
        "--task-id",
        help="任务 ID（如 T001）",
    )
    parser.add_argument(
        "--project",
        help="项目名称（如 ai-learning）",
    )
    return parser


def print_result(result: ValidationResult) -> None:
    """打印校验结果"""
    if result.passed:
        print(f"[PASS] Task {result.task_id}")
    else:
        print(f"[FAIL] Task {result.task_id}")

    for issue in result.issues:
        prefix = "ERROR" if issue.severity == "ERROR" else "WARN "
        print(f"  [{prefix}] {issue.field}: {issue.message}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # mode=input
    if args.mode == "input":
        if not args.task_id:
            print("[ERROR] --task-id is required for --mode=input", file=sys.stderr)
            return 2
        result = validate_input_schema(args.task_id, args.project)
        print_result(result)
        return 0 if result.passed else 1

    # mode=output
    elif args.mode == "output":
        if not args.task_id:
            print("[ERROR] --task-id is required for --mode=output", file=sys.stderr)
            return 2
        result = validate_output_schema(args.task_id, args.project)
        print_result(result)
        return 0 if result.passed else 1

    # mode=self-check
    elif args.mode == "self-check":
        result = validate_self_check()
        print_result(result)
        return 0 if result.passed else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
