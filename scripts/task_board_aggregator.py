#!/usr/bin/env python3
"""Generate the task-board view from versioned task-state files."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from task_state import GLOBAL_PROJECT, LEARNING_PROJECTS, TaskEntry, load_all_tasks


ROOT = Path(__file__).resolve().parents[1]
TASK_BOARD = ROOT / "docs" / "LEARNING_PROJECTS_TASK_BOARD.md"
ROOT_README = ROOT / "README.md"
GLOBAL_AGENTS = ROOT / "AGENTS.md"
README_OVERVIEW_START = "<!-- PROJECT_OVERVIEW:START -->"
README_OVERVIEW_END = "<!-- PROJECT_OVERVIEW:END -->"
REGISTRY_ROW_PATTERN = re.compile(
    r"^\| \*\*(?P<agent>[^*]+)\*\* \| `(?P<project>[^`]+)/` \| `(?P<protocol>[^`]+)` \| (?P<domain>.+?) \| (?P<status>[^|]+) \|$"
)
PROJECT_TITLES = {
    "ai-learning": "🤖 AI Learning",
    "cs-learning": "💻 CS Learning",
    "philosophy-learning": "📚 Philosophy Learning",
    "psychology-learning": "🧠 Psychology Learning",
    "biology-learning": "🧬 Biology Learning",
    "github-trending-analyzer": "📈 GitHub Trending Analyzer",
}


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


class CatalogEntry:
    def __init__(self, project: str, domain: str, status: str) -> None:
        self.project = project
        self.domain = domain
        self.status = status.strip()

    @property
    def title(self) -> str:
        return PROJECT_TITLES.get(self.project, self.project.replace("-", " ").title())

    @property
    def readme_link(self) -> str:
        return f"[{self.title}](./{self.project}/README.md)"


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


def count_wiki_pages(project_path: Path) -> str:
    entities_dir = project_path / "wiki" / "entities"
    concepts_dir = project_path / "wiki" / "concepts"
    entity_count = sum(1 for path in entities_dir.glob("*.md")) if entities_dir.exists() else 0
    concept_count = sum(1 for path in concepts_dir.glob("*.md")) if concepts_dir.exists() else 0
    if entity_count == 0 and concept_count == 0:
        return "—"
    return f"{entity_count} entities · {concept_count} concepts"


def count_trending_reports(project_path: Path) -> str:
    reports_dir = project_path / "github-trending-reports"
    repo_reports = len(list(reports_dir.glob("research_*.md"))) if reports_dir.exists() else 0
    summary_reports = len(list(reports_dir.glob("all-*.md"))) if reports_dir.exists() else 0
    return f"{repo_reports} 篇 Repo 报告 + {summary_reports} 篇汇总报告"


def load_catalog_entries() -> list[CatalogEntry]:
    entries: list[CatalogEntry] = []
    for line in GLOBAL_AGENTS.read_text(encoding="utf-8").splitlines():
        match = REGISTRY_ROW_PATTERN.match(line.strip())
        if not match:
            continue
        entries.append(
            CatalogEntry(
                project=match.group("project"),
                domain=match.group("domain").strip(),
                status=match.group("status").strip(),
            )
        )
    return entries


def format_report_summary(project: str, stats: dict[str, ProjectStats]) -> str:
    if project == "github-trending-analyzer":
        return count_trending_reports(ROOT / project)
    project_stats = stats.get(project, ProjectStats())
    return f"{project_stats.paper_analyses} 篇精读/文本 + {project_stats.knowledge_reports} 篇知识/概念报告"


def build_root_readme_overview(stats: dict[str, ProjectStats]) -> str:
    entries = load_catalog_entries()
    lines = [
        README_OVERVIEW_START,
        f"EverAgent 是以 AI Agent 为核心工具的个人知识库，通过系统化学习路径、深度分析报告和自动化工具，将学习从\"被动积累\"变为\"主动建构\"。目前包含 **{len(entries)} 个子项目**：",
        "",
        "| 项目 | 领域 | 报告量 | Wiki 页面 | 状态 |",
        "|------|------|--------|-----------|------|",
    ]
    for entry in entries:
        project_path = ROOT / entry.project
        wiki_summary = "—" if entry.project == "github-trending-analyzer" else count_wiki_pages(project_path)
        lines.append(
            f"| {entry.readme_link} | {entry.domain} | {format_report_summary(entry.project, stats)} | {wiki_summary} | {entry.status} |"
        )
    lines.append(README_OVERVIEW_END)
    return "\n".join(lines)


def sync_root_readme_overview(stats: dict[str, ProjectStats] | None = None) -> None:
    if stats is None:
        stats = generate_project_stats()
    text = ROOT_README.read_text(encoding="utf-8")
    replacement = build_root_readme_overview(stats)
    if README_OVERVIEW_START in text and README_OVERVIEW_END in text:
        start = text.index(README_OVERVIEW_START)
        end = text.index(README_OVERVIEW_END) + len(README_OVERVIEW_END)
        updated = text[:start] + replacement + text[end:]
    else:
        section_pattern = re.compile(r"## 项目全景\n\n.*?\n---", re.DOTALL)
        updated = section_pattern.sub(f"## 项目全景\n\n{replacement}\n\n---", text, count=1)
    ROOT_README.write_text(updated, encoding="utf-8")


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
    parser.add_argument("--sync-readme", action="store_true", help="Refresh the root README project overview")
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
    if args.sync_readme:
        sync_root_readme_overview(generate_project_stats())
    print(f"[PASS] Updated {TASK_BOARD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
