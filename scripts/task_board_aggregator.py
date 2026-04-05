#!/usr/bin/env python3
"""
Task Board Aggregator — 从项目状态文件生成 Task Board 汇总视图

功能：
  1. 读取各项目的 .project-task-state 文件
  2. 生成 Task Board 汇总视图
  3. 同步更新 docs/LEARNING_PROJECTS_TASK_BOARD.md

用法：
  python3 scripts/task_board_aggregator.py              # 生成视图
  python3 scripts/task_board_aggregator.py --dry-run   # 仅显示不写入
  python3 scripts/task_board_aggregator.py --force     # 强制覆盖

返回码：
  0  成功
  1  失败（文件不存在、解析错误等）
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
PROJECTS = {
    "ai-learning": ROOT / "ai-learning",
    "cs-learning": ROOT / "cs-learning",
    "philosophy-learning": ROOT / "philosophy-learning",
    "psychology-learning": ROOT / "psychology-learning",
    "biology-learning": ROOT / "biology-learning",
}

# ── ISO8601 正则 ─────────────────────────────────────────────────────────────────
ISO8601_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\+\d{2}:\d{2}|Z)?"
)

# ── 数据结构 ─────────────────────────────────────────────────────────────────────

@dataclass
class TaskEntry:
    id: str
    project: str
    type: str
    target: str
    value: str = ""
    priority: str = "P2"
    status: str = "open"
    claimed_by: Optional[str] = None
    claimed_at: Optional[str] = None
    started_at: Optional[str] = None
    done_at: Optional[str] = None
    failed_reason: Optional[str] = None

    @property
    def is_open(self) -> bool:
        return self.status == "open"

    @property
    def is_active(self) -> bool:
        return self.status in ("claimed", "in_progress")

    @property
    def is_done(self) -> bool:
        return self.status == "done"


@dataclass
class ProjectStats:
    name: str
    paper_analyses: int = 0
    knowledge_reports: int = 0
    status_emoji: str = "🟡"

    @property
    def total_analyses(self) -> int:
        return self.paper_analyses

    @property
    def knowledge_ratio(self) -> float:
        total = self.paper_analyses + self.knowledge_reports
        if total == 0:
            return 0.0
        return self.knowledge_reports / total


# ── 解析器 ─────────────────────────────────────────────────────────────────────

def parse_project_task_state(project_path: Path) -> list[TaskEntry]:
    """解析 .project-task-state 文件"""
    state_file = project_path / ".project-task-state"
    if not state_file.exists():
        return []

    text = state_file.read_text(encoding="utf-8")
    # 支持 YAML 列表格式
    tasks: list[TaskEntry] = []

    # 简单解析：按 "- id:" 分块
    chunks = re.split(r"\n(?=- id:)", text.strip())
    for chunk in chunks:
        if not chunk.strip() or chunk.strip().startswith("#"):
            continue

        task_data: dict[str, str] = {}
        for line in chunk.splitlines():
            line = line.strip().lstrip("- ")
            if ":" in line:
                key, _, value = line.partition(":")
                task_data[key.strip()] = value.strip().strip('"').strip("'")

        if "id" in task_data:
            tasks.append(TaskEntry(
                id=task_data.get("id", ""),
                project=task_data.get("project", project_path.name),
                type=task_data.get("type", ""),
                target=task_data.get("target", ""),
                value=task_data.get("value", ""),
                priority=task_data.get("priority", "P2"),
                status=task_data.get("status", "open"),
                claimed_by=task_data.get("claimed_by") or None,
                claimed_at=task_data.get("claimed_at") or None,
                started_at=task_data.get("started_at") or None,
                done_at=task_data.get("done_at") or None,
                failed_reason=task_data.get("failed_reason") or None,
            ))

    return tasks


def collect_all_tasks() -> list[TaskEntry]:
    """从所有项目收集任务"""
    all_tasks: list[TaskEntry] = []
    for project_name, project_path in PROJECTS.items():
        tasks = parse_project_task_state(project_path)
        all_tasks.extend(tasks)
    return all_tasks


def generate_project_stats() -> dict[str, ProjectStats]:
    """从项目目录统计报告数量"""
    stats: dict[str, ProjectStats] = {}

    for project_name, project_path in PROJECTS.items():
        reports_dir = project_path / "reports"
        if not reports_dir.exists():
            stats[project_name] = ProjectStats(name=project_name)
            continue

        paper_count = sum(1 for _ in (reports_dir / "paper_analyses").rglob("*.md")) if (reports_dir / "paper_analyses").exists() else 0
        text_count = sum(1 for _ in (reports_dir / "text_analyses").rglob("*.md")) if (reports_dir / "text_analyses").exists() else 0
        knowledge_count = sum(1 for _ in (reports_dir / "knowledge_reports").rglob("*.md")) if (reports_dir / "knowledge_reports").exists() else 0
        concept_count = sum(1 for _ in (reports_dir / "concept_reports").rglob("*.md")) if (reports_dir / "concept_reports").exists() else 0

        # 确定状态 emoji（基于活动度）
        if paper_count + text_count + knowledge_count + concept_count >= 20:
            status = "🟢"
        elif paper_count + text_count + knowledge_count + concept_count >= 5:
            status = "🟡"
        else:
            status = "🔴"

        stats[project_name] = ProjectStats(
            name=project_name,
            paper_analyses=paper_count + text_count,
            knowledge_reports=knowledge_count + concept_count,
            status_emoji=status,
        )

    return stats


# ── 生成器 ─────────────────────────────────────────────────────────────────────

def format_task_yaml(task: TaskEntry, indent: int = 2) -> str:
    """将 TaskEntry 格式化为 YAML 块"""
    spaces = " " * indent
    lines = [f"{spaces}- id: {task.id}"]
    lines.append(f"{spaces}  project: {task.project}")
    lines.append(f"{spaces}  type: {task.type}")
    lines.append(f"{spaces}  target: \"{task.target}\"")
    if task.value:
        lines.append(f"{spaces}  value: \"{task.value}\"")
    lines.append(f"{spaces}  priority: {task.priority}")
    lines.append(f"{spaces}  status: {task.status}")
    if task.claimed_by:
        lines.append(f"{spaces}  claimed_by: {task.claimed_by}")
    if task.claimed_at:
        lines.append(f"{spaces}  claimed_at: {task.claimed_at}")
    if task.started_at:
        lines.append(f"{spaces}  started_at: {task.started_at}")
    if task.done_at:
        lines.append(f"{spaces}  done_at: {task.done_at}")
    if task.failed_reason:
        lines.append(f"{spaces}  failed_reason: \"{task.failed_reason}\"")
    return "\n".join(lines)


def generate_task_board_view(tasks: list[TaskEntry], stats: dict[str, ProjectStats]) -> str:
    """生成完整的 Task Board Markdown 内容"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# Five Learning Projects Task Board",
        "",
        "> 本文件为自动生成视图，由 `scripts/task_board_aggregator.py` 维护",
        "> **请勿直接编辑**，编辑将覆盖",
        "> 手动编辑请修改各项目的 `.project-task-state` 文件",
        "",
        f"> 生成时间：{now}",
        "",
        "---",
        "",
        "## 使用原则",
        "",
        "1. 同一时间同一子项目只允许一个 Agent 写入。",
        "2. 优先接「高价值、低歧义、能直接产出报告」的任务。",
        "3. 写入前先读取对应项目的 `CONTEXT.md`，避免越过防幻觉边界。",
        "4. 完成任务后同步更新对应项目的 `CONTEXT.md`（不只是本文件）。",
        "5. **本文件为只读视图**，如需编辑任务，请编辑对应项目的 `.project-task-state` 文件。",
        "",
        "---",
        "",
        "## 项目进度概览",
        "",
        "| 项目 | 当前状态 | 论文/文本精读 | 知识/概念报告 | 知识报告比 |",
        "|------|----------|:---:|:---:|:---:|",
    ]

    # 项目进度表格
    for project_name in ["ai-learning", "cs-learning", "philosophy-learning", "psychology-learning", "biology-learning"]:
        if project_name in stats:
            s = stats[project_name]
            ratio = f"{s.knowledge_ratio:.0%}"
            lines.append(f"| `{project_name}` | {s.status_emoji} | {s.paper_analyses} | {s.knowledge_reports} | {ratio} |")

    lines.extend(["", "---", "", "## 任务队列", ""])

    # 按状态分组
    open_tasks = [t for t in tasks if t.is_open]
    active_tasks = [t for t in tasks if t.is_active]
    done_tasks = [t for t in tasks if t.is_done]

    # 开放任务池
    lines.append("### 开放任务池")
    lines.append("")
    lines.append("```yaml")

    # 按 priority 分组
    p1_tasks = [t for t in open_tasks if t.priority == "P1"]
    p2_tasks = [t for t in open_tasks if t.priority == "P2"]
    p3_tasks = [t for t in open_tasks if t.priority == "P3"]

    if p1_tasks:
        lines.append("# P1: 高价值, 可直接开工")
        for task in p1_tasks:
            lines.append(format_task_yaml(task))
            lines.append("")

    if p2_tasks:
        lines.append("# P2: 第二批推荐")
        for task in p2_tasks:
            lines.append(format_task_yaml(task))
            lines.append("")

    if p3_tasks:
        lines.append("# P3: 结构整理型")
        for task in p3_tasks:
            lines.append(format_task_yaml(task))
            lines.append("")

    lines.append("```")
    lines.append("")

    # 进行中任务
    if active_tasks:
        lines.append("### 进行中任务")
        lines.append("")
        lines.append("```yaml")
        for task in active_tasks:
            lines.append(format_task_yaml(task))
            lines.append("")
        lines.append("```")
        lines.append("")

    # 已完成任务（最近10条）
    if done_tasks:
        lines.append("### 最近完成（自动生成）")
        lines.append("")
        lines.append("```yaml")
        # 按 done_at 排序，取最近的10条
        sorted_done = sorted(done_tasks, key=lambda t: t.done_at or "", reverse=True)[:10]
        for task in sorted_done:
            lines.append(format_task_yaml(task))
            lines.append("")
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Task Board Aggregator")
    parser.add_argument("--dry-run", action="store_true", help="仅显示不写入")
    parser.add_argument("--force", action="store_true", help="强制覆盖")
    args = parser.parse_args()

    # 检查 Task Board 是否存在
    if not TASK_BOARD.exists():
        print(f"[ERROR] Task Board not found: {TASK_BOARD}", file=sys.stderr)
        return 1

    # 收集任务
    tasks = collect_all_tasks()
    print(f"[INFO] Collected {len(tasks)} tasks from {len(PROJECTS)} projects")

    # 生成统计
    stats = generate_project_stats()

    # 生成视图
    view = generate_task_board_view(tasks, stats)

    if args.dry_run:
        print(view)
        return 0

    # 写入
    if not args.force:
        # 检查是否有变化
        existing = TASK_BOARD.read_text(encoding="utf-8")
        if existing == view:
            print("[INFO] No changes, skipping write")
            return 0

    TASK_BOARD.write_text(view, encoding="utf-8")
    print(f"[INFO] Updated {TASK_BOARD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
