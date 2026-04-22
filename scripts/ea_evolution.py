#!/usr/bin/env python3
"""EverAgent Self-Evolution Engine — Phase 5 implementation.

Analyzes event history and task execution patterns to automatically
generate optimization suggestions and create improvement tasks.

Usage:
    python3 scripts/ea_evolution.py [--days 7] [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from ea_common import now_iso
from ea_events import emit_event, load_events
from ea_task_dsl import render_task_dsl_to_state, sync_task_dsls_to_project_states
from task_state import TaskEntry, load_tasks_for_project, write_task_state_file


# ---------------------------------------------------------------------------
# Insight models
# ---------------------------------------------------------------------------

class Insight:
    def __init__(
        self,
        category: str,
        severity: str,
        title: str,
        description: str,
        metric_value: float | None = None,
        suggested_action: str = "",
    ):
        self.category = category
        self.severity = severity  # critical / warning / info
        self.title = title
        self.description = description
        self.metric_value = metric_value
        self.suggested_action = suggested_action

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "metric_value": self.metric_value,
            "suggested_action": self.suggested_action,
        }


# ---------------------------------------------------------------------------
# Pattern recognition engines
# ---------------------------------------------------------------------------

def analyze_task_completion_patterns(days: int = 7) -> list[Insight]:
    """Analyze task completion patterns: duration, failure rates, bottlenecks."""
    insights: list[Insight] = []
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    events = load_events(start_date=since)

    # Group events by task_id
    task_events: dict[str, list] = defaultdict(list)
    for e in events:
        if e.task_id:
            task_events[e.task_id].append(e)

    # Calculate completion times
    completion_times: list[timedelta] = []
    failed_tasks = 0
    abandoned_tasks = 0

    for task_id, evts in task_events.items():
        started = None
        done = None
        failed = False
        for e in evts:
            if e.type == "task_started":
                started = datetime.fromisoformat(e.timestamp.replace("Z", "+00:00"))
            elif e.type == "task_done":
                done = datetime.fromisoformat(e.timestamp.replace("Z", "+00:00"))
            elif e.type == "task_failed":
                failed = True
            elif e.type == "task_abandoned":
                abandoned_tasks += 1

        if started and done:
            completion_times.append(done - started)
        elif failed:
            failed_tasks += 1

    # Insight 1: Average completion time
    if completion_times:
        avg_seconds = sum(t.total_seconds() for t in completion_times) / len(completion_times)
        avg_hours = avg_seconds / 3600

        if avg_hours > 4:
            insights.append(Insight(
                category="performance",
                severity="warning",
                title="任务平均完成时间过长",
                description=f"过去 {days} 天任务平均完成时间 {avg_hours:.1f} 小时，建议优化任务拆分粒度",
                metric_value=avg_hours,
                suggested_action="将大型知识报告拆分为多个子任务",
            ))
        else:
            insights.append(Insight(
                category="performance",
                severity="info",
                title="任务完成效率良好",
                description=f"平均完成时间 {avg_hours:.1f} 小时",
                metric_value=avg_hours,
            ))

    # Insight 2: Failure rate
    total_completed = len(completion_times)
    total_attempted = total_completed + failed_tasks
    if total_attempted > 0:
        failure_rate = failed_tasks / total_attempted
        if failure_rate > 0.3:
            insights.append(Insight(
                category="quality",
                severity="critical",
                title="任务失败率过高",
                description=f"失败率 {failure_rate*100:.1f}%（{failed_tasks}/{total_attempted}），需要审查任务定义和前置条件",
                metric_value=failure_rate,
                suggested_action="审查失败任务的输入校验和依赖条件",
            ))
        elif failure_rate > 0.1:
            insights.append(Insight(
                category="quality",
                severity="warning",
                title="任务失败率偏高",
                description=f"失败率 {failure_rate*100:.1f}%",
                metric_value=failure_rate,
            ))

    # Insight 3: Abandoned tasks
    if abandoned_tasks > 2:
        insights.append(Insight(
            category="process",
            severity="warning",
            title="存在被放弃的任务",
            description=f"{abandoned_tasks} 个任务被标记为 abandoned，可能存在资源竞争或任务定义不清",
            suggested_action="审查 abandoned 任务的原因，优化任务领取机制",
        ))

    return insights


def analyze_agent_performance(days: int = 7) -> list[Insight]:
    """Analyze per-agent performance and identify degradation."""
    insights: list[Insight] = []
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    events = load_events(start_date=since)

    agent_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"done": 0, "failed": 0, "started": 0})
    for e in events:
        if not e.actor or e.actor == "system":
            continue
        if e.type == "task_done":
            agent_stats[e.actor]["done"] += 1
        elif e.type == "task_failed":
            agent_stats[e.actor]["failed"] += 1
        elif e.type == "task_started":
            agent_stats[e.actor]["started"] += 1

    for agent, stats in sorted(agent_stats.items()):
        total = stats["done"] + stats["failed"]
        if total == 0:
            continue
        success_rate = stats["done"] / total

        if success_rate < 0.5:
            insights.append(Insight(
                category="agent_health",
                severity="critical",
                title=f"{agent} 成功率严重下降",
                description=f"成功率仅 {success_rate*100:.1f}%（{stats['done']}/{total}）",
                metric_value=success_rate,
                suggested_action=f"暂停向 {agent} 分配新任务，审查其最近输出质量",
            ))
        elif success_rate < 0.8:
            insights.append(Insight(
                category="agent_health",
                severity="warning",
                title=f"{agent} 成功率偏低",
                description=f"成功率 {success_rate*100:.1f}%",
                metric_value=success_rate,
            ))

    # Identify inactive agents
    active_agents = set(agent_stats.keys())
    from project_registry import load_agents_registry
    try:
        registry = load_agents_registry()
        all_agents = {a.agent for a in registry}
        inactive = all_agents - active_agents
        if inactive:
            insights.append(Insight(
                category="agent_health",
                severity="info",
                title="存在未活跃的 Agent",
                description=f"{', '.join(inactive)} 在过去 {days} 天无活动记录",
                suggested_action="检查这些 Agent 的任务队列或考虑重新激活",
            ))
    except Exception:
        pass

    return insights


def analyze_project_health() -> list[Insight]:
    """Analyze project-level health indicators."""
    insights: list[Insight] = []

    from task_state import PROJECTS
    for project in PROJECTS:
        tasks = load_tasks_for_project(project)
        open_tasks = [t for t in tasks if t.status == "open"]
        in_progress = [t for t in tasks if t.status == "in_progress"]
        p1_open = [t for t in open_tasks if t.priority == "P1"]

        if len(in_progress) > 3:
            insights.append(Insight(
                category="capacity",
                severity="warning",
                title=f"{project} 并发任务过多",
                description=f"{len(in_progress)} 个任务正在执行，可能超出 Agent 处理能力",
                suggested_action="限制并发或增加 Agent 资源",
            ))

        if len(p1_open) > 5:
            insights.append(Insight(
                category="backlog",
                severity="warning",
                title=f"{project} P1 任务积压",
                description=f"{len(p1_open)} 个 P1 任务待处理",
                suggested_action="优先处理 P1 任务或重新评估优先级",
            ))

    return insights


def analyze_event_patterns(days: int = 7) -> list[Insight]:
    """Analyze event patterns for anomalies."""
    insights: list[Insight] = []
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    events = load_events(start_date=since)

    if not events:
        insights.append(Insight(
            category="system",
            severity="info",
            title="事件日志为空",
            description=f"过去 {days} 天无事件记录，系统可能未激活",
        ))
        return insights

    # Event type distribution
    type_counts = Counter(e.type for e in events)
    total = len(events)

    # Check for validation failures
    validation_failures = type_counts.get("validation_failed", 0)
    if validation_failures > 5:
        insights.append(Insight(
            category="quality",
            severity="warning",
            title="校验失败频繁",
            description=f"{validation_failures} 次校验失败",
            suggested_action="审查 frontmatter 和输出规范",
        ))

    # Check for lock contention
    lock_acquired = type_counts.get("lock_acquired", 0)
    lock_released = type_counts.get("lock_released", 0)
    if lock_acquired > lock_released + 2:
        insights.append(Insight(
            category="system",
            severity="warning",
            title="可能存在未释放的锁",
            description=f"acquired {lock_acquired} 次，released {lock_released} 次",
            suggested_action="运行 project_lock.py check 检查过期锁",
        ))

    return insights


# ---------------------------------------------------------------------------
# Action generation
# ---------------------------------------------------------------------------

def generate_optimization_tasks(insights: list[Insight], dry_run: bool = True) -> list[str]:
    """Generate optimization tasks from critical insights."""
    actions: list[str] = []
    task_id_counter = 31  # Start from T031

    for insight in insights:
        if insight.severity != "critical":
            continue

        task_id = f"T{task_id_counter:03d}"
        task_id_counter += 1

        # Map category to project
        project_map = {
            "performance": "ai-learning",
            "quality": "ai-learning",
            "agent_health": "global",
            "capacity": "global",
            "backlog": "global",
            "process": "global",
            "system": "global",
        }
        project = project_map.get(insight.category, "global")

        task_content = f"""apiVersion: everagent.io/v1
kind: Task
metadata:
  id: {task_id}
  project: {project}
spec:
  type: project_optimization
  target: "[自动发现] {insight.title}"
  value: "{insight.description} | 建议行动: {insight.suggested_action}"
  priority: P2
  resources:
    max_tokens: 20000
    expected_duration: 1h
  qualityGates:
    - check: frontmatter_complete
      required: true
"""

        task_path = __import__("pathlib").Path("tasks") / f"{task_id}.yaml"
        if not dry_run:
            task_path.write_text(task_content, encoding="utf-8")
            actions.append(f"CREATED: {task_id} -> {project}")
        else:
            actions.append(f"WOULD_CREATE: {task_id} -> {project} ({insight.title})")

    return actions


def print_report(insights: list[Insight], actions: list[str]) -> None:
    """Print a formatted evolution report."""
    print("=" * 60)
    print("EverAgent Self-Evolution Report")
    print(f"Generated at: {now_iso()}")
    print("=" * 60)

    if not insights:
        print("\n✅ No issues detected. System is healthy.")
        return

    # Group by severity
    by_severity: dict[str, list[Insight]] = defaultdict(list)
    for i in insights:
        by_severity[i.severity].append(i)

    for severity in ["critical", "warning", "info"]:
        items = by_severity.get(severity, [])
        if not items:
            continue
        emoji = {"critical": "🔴", "warning": "🟡", "info": "🟢"}[severity]
        print(f"\n{emoji} {severity.upper()} ({len(items)})")
        print("-" * 40)
        for item in items:
            print(f"  [{item.category}] {item.title}")
            print(f"    {item.description}")
            if item.metric_value is not None:
                print(f"    Metric: {item.metric_value}")
            if item.suggested_action:
                print(f"    Action: {item.suggested_action}")

    if actions:
        print(f"\n📋 Generated Tasks ({len(actions)})")
        print("-" * 40)
        for a in actions:
            print(f"  {a}")

    print("\n" + "=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="EverAgent Self-Evolution Engine")
    parser.add_argument("--days", type=int, default=7, help="Analysis window in days")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without creating tasks")
    args = parser.parse_args()

    print(f"[INFO] Analyzing last {args.days} days of event history...")

    # Run all analyzers
    all_insights: list[Insight] = []
    all_insights.extend(analyze_task_completion_patterns(args.days))
    all_insights.extend(analyze_agent_performance(args.days))
    all_insights.extend(analyze_project_health())
    all_insights.extend(analyze_event_patterns(args.days))

    # Generate optimization tasks from critical insights
    actions = generate_optimization_tasks(all_insights, dry_run=args.dry_run)

    # Print report
    print_report(all_insights, actions)

    # Emit system audit event
    emit_event(
        event_type="system_audit",
        actor="ea_evolution",
        payload={
            "insights_count": len(all_insights),
            "critical_count": sum(1 for i in all_insights if i.severity == "critical"),
            "tasks_generated": len(actions),
            "dry_run": args.dry_run,
        },
    )

    if not args.dry_run and actions:
        # Sync new tasks to project states
        sync_results = sync_task_dsls_to_project_states(dry_run=False)
        for r in sync_results:
            print(f"[SYNC] {r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
