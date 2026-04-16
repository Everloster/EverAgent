#!/usr/bin/env python3
"""Generate the task-board view from versioned task-state files."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from task_state import GLOBAL_PROJECT, LEARNING_PROJECTS, TaskEntry, load_all_tasks


ROOT = Path(__file__).resolve().parents[1]
TASK_BOARD = ROOT / "docs" / "LEARNING_PROJECTS_TASK_BOARD.md"


class ProjectStats:
    def __init__(self, paper_analyses: int = 0, knowledge_reports: int = 0) -> None:
        self.paper_analyses = paper_analyses
        self.knowledge_reports = knowledge_reports

    @property
    def knowledge_ratio(self) -> float:
        total = self.paper_analyses + self.knowledge_reports
        if total == 0:
            return 0.0
        return self.knowledge_reports / total

    @property
    def status_emoji(self) -> str:
        total = self.paper_analyses + self.knowledge_reports
        if total >= 20:
            return "🟢"
        if total >= 5:
            return "🟡"
        return "🔴"


def generate_project_stats() -> dict[str, ProjectStats]:
    stats: dict[str, ProjectStats] = {}
    for project_name, project_path in LEARNING_PROJECTS.items():
        reports_dir = project_path / "reports"
        paper_count = 0
        knowledge_count = 0
        if reports_dir.exists():
            if (reports_dir / "paper_analyses").exists():
                paper_count += sum(1 for _ in (reports_dir / "paper_analyses").rglob("*.md"))
            if (reports_dir / "text_analyses").exists():
                paper_count += sum(1 for _ in (reports_dir / "text_analyses").rglob("*.md"))
            if (reports_dir / "knowledge_reports").exists():
                knowledge_count += sum(1 for _ in (reports_dir / "knowledge_reports").rglob("*.md"))
            if (reports_dir / "concept_reports").exists():
                knowledge_count += sum(1 for _ in (reports_dir / "concept_reports").rglob("*.md"))
        stats[project_name] = ProjectStats(paper_count, knowledge_count)
    return stats


def format_scalar(value: str | None) -> str:
    return "null" if value is None else value


def format_task_yaml(task: TaskEntry) -> list[str]:
    lines = [f"- id: {task.id}"]
    lines.append(f"  project: {task.project}")
    lines.append(f"  type: {task.type}")
    lines.append(f'  target: "{task.target}"')
    if task.value:
        lines.append(f'  value: "{task.value}"')
    lines.append(f"  priority: {task.priority}")
    lines.append(f"  required_capability: {task.required_capability}")
    lines.append(f"  status: {task.status}")
    lines.append(f"  claimed_by: {format_scalar(task.claimed_by)}")
    lines.append(f"  claimed_at: {format_scalar(task.claimed_at)}")
    if task.started_at is not None:
        lines.append(f"  started_at: {task.started_at}")
    if task.done_at is not None:
        lines.append(f"  done_at: {task.done_at}")
    if task.failed_reason is not None:
        lines.append(f'  failed_reason: "{task.failed_reason}"')
    return lines


def append_task_block(lines: list[str], heading: str, tasks: list[TaskEntry]) -> None:
    if not tasks:
        return
    lines.extend([heading, "", "```yaml"])
    for task in tasks:
        lines.extend(format_task_yaml(task))
        lines.append("")
    lines.append("```")
    lines.append("")


def generate_task_board_view(tasks: list[TaskEntry], stats: dict[str, ProjectStats]) -> str:
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    lines = [
        "# Learning Projects Task Board",
        "",
        "> 本文件为自动生成视图，由 `scripts/task_board_aggregator.py` 维护",
        "> **请勿直接编辑**，编辑将覆盖",
        "> 任务权威源：各项目的 `.project-task-state`，以及根目录的 `/.project-task-state`（global 任务）",
        f"> 更新日期：**{now}**",
        "",
        "---",
        "",
        "## 使用原则",
        "",
        "1. 同一时间同一子项目只允许一个 Agent 写入。",
        "2. 领取前先运行 `python3 scripts/execution_validator.py --mode=input --task-id=TXXX --project=<project>`。",
        "3. 输入校验通过后立即获取项目锁：`python3 scripts/project_lock.py acquire --project=<project> --task-id=TXXX --agent=<AgentName>`。",
        "4. 完成任务后先运行输出校验，再提交、推送，最后释放项目锁。",
        "",
        "---",
        "",
        "## 项目进度概览",
        "",
        "| 项目 | 当前状态 | 论文/文本精读 | 知识/概念报告 | 知识报告比 |",
        "|------|----------|:---:|:---:|:---:|",
    ]

    for project_name in LEARNING_PROJECTS:
        project_stats = stats[project_name]
        lines.append(
            f"| `{project_name}` | {project_stats.status_emoji} | "
            f"{project_stats.paper_analyses} | {project_stats.knowledge_reports} | "
            f"{project_stats.knowledge_ratio:.0%} |"
        )

    lines.extend(["", "---", "", "## 任务队列", ""])

    tasks_by_priority = {
        "P1": [task for task in tasks if task.project != GLOBAL_PROJECT and task.is_open and task.priority == "P1"],
        "P2": [task for task in tasks if task.project != GLOBAL_PROJECT and task.is_open and task.priority == "P2"],
        "P3": [task for task in tasks if task.project != GLOBAL_PROJECT and task.is_open and task.priority == "P3"],
    }
    append_task_block(lines, "### 开放任务池（P1）", tasks_by_priority["P1"])
    append_task_block(lines, "### 开放任务池（P2）", tasks_by_priority["P2"])
    append_task_block(lines, "### 开放任务池（P3）", tasks_by_priority["P3"])

    active_tasks = [task for task in tasks if task.is_active]
    append_task_block(lines, "### 进行中任务", active_tasks)

    done_tasks = sorted(
        (task for task in tasks if task.is_done),
        key=lambda task: task.done_at or "",
        reverse=True,
    )[:10]
    append_task_block(lines, "### 最近完成（自动生成）", done_tasks)

    global_tasks = [task for task in tasks if task.project == GLOBAL_PROJECT and not task.is_done]
    append_task_block(lines, "### Global Tasks", global_tasks)

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Task Board Aggregator")
    parser.add_argument("--dry-run", action="store_true", help="Only print the generated board")
    args = parser.parse_args()

    tasks = load_all_tasks(include_global=True)
    if not tasks:
        print("[ERROR] No task-state files were found", file=sys.stderr)
        return 1

    view = generate_task_board_view(tasks, generate_project_stats())

    if args.dry_run:
        print(view, end="")
        return 0

    TASK_BOARD.write_text(view, encoding="utf-8")
    print(f"[PASS] Updated {TASK_BOARD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
