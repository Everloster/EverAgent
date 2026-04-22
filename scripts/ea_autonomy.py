#!/usr/bin/env python3
"""EverAgent v3.0 Autonomous Engine — Self-governing task allocation and optimization.

This module provides autonomous capabilities:
- Intelligent task-agent matching based on capability scores
- Load balancing across agents and projects
- Automatic task decomposition for large tasks
- Self-healing: detect and recover from failures
- Predictive scheduling based on historical patterns

Usage:
    from ea_autonomy import AutonomousScheduler
    scheduler = AutonomousScheduler()
    task = scheduler.recommend_task(agent="NeuronAgent")
    scheduler.assign_task(task.id, agent="NeuronAgent")
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from ea_database import (
    get_agent_leaderboard,
    get_db,
    list_tasks,
    query_events,
    record_metric,
    upsert_task,
)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class AgentProfile:
    name: str
    project: str
    domain: str
    capability_score: float
    success_rate: float
    avg_duration_sec: Optional[float]
    current_load: int
    max_concurrent: int = 3


@dataclass
class TaskRecommendation:
    task_id: str
    project: str
    target: str
    priority: str
    estimated_duration: float
    confidence: float
    reason: str


# ---------------------------------------------------------------------------
# Agent Capability Registry
# ---------------------------------------------------------------------------

class AgentRegistry:
    """Dynamic agent capability registry."""

    def __init__(self):
        self._cache: dict[str, AgentProfile] = {}
        self._last_update: Optional[datetime] = None

    def refresh(self) -> None:
        """Refresh agent profiles from database."""
        self._cache.clear()
        rows = get_agent_leaderboard()
        for row in rows:
            # Count current load
            active = list_tasks(claimed_by=row["name"], status="in_progress")
            profile = AgentProfile(
                name=row["name"],
                project=row["project"],
                domain=row.get("domain", ""),
                capability_score=row.get("capability_score", 1.0),
                success_rate=row.get("success_rate", 0) / 100.0,
                avg_duration_sec=row.get("avg_duration_sec"),
                current_load=len(active),
            )
            self._cache[row["name"]] = profile
        self._last_update = datetime.now(timezone.utc)

    def get_profile(self, name: str) -> Optional[AgentProfile]:
        """Get agent profile by name."""
        if not self._cache or self._is_stale():
            self.refresh()
        return self._cache.get(name)

    def list_available(self, project: Optional[str] = None) -> list[AgentProfile]:
        """List agents available for work."""
        if not self._cache or self._is_stale():
            self.refresh()

        available = []
        for profile in self._cache.values():
            if profile.current_load < profile.max_concurrent:
                if project is None or profile.project == project:
                    available.append(profile)
        return available

    def _is_stale(self) -> bool:
        if self._last_update is None:
            return True
        return datetime.now(timezone.utc) - self._last_update > timedelta(minutes=5)


# ---------------------------------------------------------------------------
# Intelligent Task Matching
# ---------------------------------------------------------------------------

class TaskMatcher:
    """Match tasks to agents based on multiple factors."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def score_match(self, task: dict[str, Any], agent: AgentProfile) -> float:
        """Score how well an agent matches a task (0-1)."""
        scores: list[float] = []

        # 1. Domain match (weight: 0.3)
        task_type = task.get("type", "")
        domain_bonus = 0.3 if self._type_matches_domain(task_type, agent.domain) else 0.0
        scores.append(domain_bonus)

        # 2. Success rate (weight: 0.25)
        scores.append(agent.success_rate * 0.25)

        # 3. Capability score (weight: 0.2)
        scores.append(agent.capability_score * 0.2)

        # 4. Load factor (weight: 0.15)
        load_factor = 1.0 - (agent.current_load / agent.max_concurrent)
        scores.append(load_factor * 0.15)

        # 5. Historical performance on similar tasks (weight: 0.1)
        hist_score = self._historical_performance(agent.name, task.get("type", ""))
        scores.append(hist_score * 0.1)

        return sum(scores)

    def find_best_agent(self, task: dict[str, Any]) -> Optional[tuple[AgentProfile, float]]:
        """Find the best agent for a task."""
        project = task.get("project")
        candidates = self.registry.list_available(project)

        if not candidates:
            return None

        best = None
        best_score = -1.0
        for agent in candidates:
            score = self.score_match(task, agent)
            if score > best_score:
                best_score = score
                best = agent

        return best, best_score if best else None

    def _type_matches_domain(self, task_type: str, domain: str) -> bool:
        """Check if task type matches agent domain."""
        mapping = {
            "paper_analysis": ["ai-learning", "cs-learning", "biology-learning"],
            "knowledge_report": ["ai-learning", "cs-learning", "philosophy-learning", "psychology-learning"],
            "text_analysis": ["philosophy-learning", "psychology-learning"],
            "concept_report": ["cs-learning", "philosophy-learning"],
            "project_optimization": ["global"],
            "new_project": ["global"],
            "maintenance": ["global"],
        }
        return domain in mapping.get(task_type, [])

    def _historical_performance(self, agent_name: str, task_type: str) -> float:
        """Get historical success rate for agent on similar tasks."""
        events = query_events(
            event_types=["task_done", "task_failed"],
            actor=agent_name,
            limit=50,
        )
        if not events:
            return 0.5  # Neutral default

        done = sum(1 for e in events if e["type"] == "task_done")
        total = len(events)
        return done / total if total > 0 else 0.5


# ---------------------------------------------------------------------------
# Autonomous Scheduler
# ---------------------------------------------------------------------------

class AutonomousScheduler:
    """Self-governing task scheduler."""

    def __init__(self):
        self.registry = AgentRegistry()
        self.matcher = TaskMatcher(self.registry)

    def recommend_task(self, agent: str) -> Optional[TaskRecommendation]:
        """Recommend the best task for an agent."""
        profile = self.registry.get_profile(agent)
        if not profile:
            return None

        if profile.current_load >= profile.max_concurrent:
            return None

        # Get open tasks for agent's project
        tasks = list_tasks(project=profile.project, status="open")
        if not tasks:
            # Fallback: check other projects
            tasks = list_tasks(status="open")

        if not tasks:
            return None

        # Score each task for this agent
        best_task = None
        best_score = -1.0
        for task in tasks:
            score = self.matcher.score_match(task, profile)
            if score > best_score:
                best_score = score
                best_task = task

        if not best_task:
            return None

        # Estimate duration
        est_duration = profile.avg_duration_sec or 3600
        if best_task.get("priority") == "P1":
            est_duration *= 0.8  # P1 tasks tend to be more focused

        return TaskRecommendation(
            task_id=best_task["id"],
            project=best_task["project"],
            target=best_task["target"],
            priority=best_task["priority"],
            estimated_duration=est_duration,
            confidence=best_score,
            reason=f"Domain match + {profile.success_rate*100:.0f}% success rate + low load ({profile.current_load}/{profile.max_concurrent})",
        )

    def assign_task(self, task_id: str, agent: str) -> bool:
        """Autonomously assign a task to an agent."""
        task = list_tasks(status="open")
        task_dict = next((t for t in task if t["id"] == task_id), None)
        if not task_dict:
            print(f"[WARN] Task {task_id} not available")
            return False

        # Update task state
        task_dict["status"] = "claimed"
        task_dict["claimed_by"] = agent
        task_dict["claimed_at"] = datetime.now(timezone.utc).isoformat()
        upsert_task(task_dict)

        # Record metric
        record_metric("task_auto_assigned", 1.0, {
            "task_id": task_id,
            "agent": agent,
            "project": task_dict["project"],
        })

        print(f"[PASS] Auto-assigned {task_id} to {agent}")
        return True

    def rebalance_load(self) -> list[str]:
        """Rebalance tasks across agents for optimal load distribution."""
        actions: list[str] = []
        self.registry.refresh()

        # Find overloaded agents
        overloaded = []
        underloaded = []
        for profile in self.registry._cache.values():
            if profile.current_load > profile.max_concurrent:
                overloaded.append(profile)
            elif profile.current_load < profile.max_concurrent // 2:
                underloaded.append(profile)

        # Simple rebalance: suggest transfers
        for busy in overloaded:
            actions.append(f"SUGGEST: {busy.name} overloaded ({busy.current_load}/{busy.max_concurrent})")

        for idle in underloaded:
            actions.append(f"SUGGEST: {idle.name} underutilized ({idle.current_load}/{idle.max_concurrent})")

        return actions

    def detect_anomalies(self) -> list[str]:
        """Detect anomalies in the system."""
        anomalies: list[str] = []

        # Check for tasks stuck in_progress too long
        in_progress = list_tasks(status="in_progress")
        now = datetime.now(timezone.utc)
        for task in in_progress:
            started = task.get("started_at")
            if started:
                started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                hours = (now - started_dt).total_seconds() / 3600
                if hours > 24:
                    anomalies.append(f"STUCK: {task['id']} in_progress for {hours:.1f}h")

        # Check for failed task clusters
        recent_failed = query_events(event_types=["task_failed"], limit=20)
        if len(recent_failed) >= 5:
            anomalies.append(f"ALERT: {len(recent_failed)} recent failures detected")

        return anomalies


# ---------------------------------------------------------------------------
# Self-Healing
# ---------------------------------------------------------------------------

class SelfHealing:
    """Automatic recovery from failures."""

    def __init__(self, scheduler: AutonomousScheduler):
        self.scheduler = scheduler

    def heal_stuck_tasks(self, dry_run: bool = True) -> list[str]:
        """Find and recover stuck tasks."""
        actions: list[str] = []
        in_progress = list_tasks(status="in_progress")
        now = datetime.now(timezone.utc)

        for task in in_progress:
            started = task.get("started_at")
            if not started:
                continue
            started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
            hours = (now - started_dt).total_seconds() / 3600

            if hours > 48:
                action = f"RESET: {task['id']} stuck for {hours:.1f}h"
                if not dry_run:
                    task["status"] = "open"
                    task["claimed_by"] = None
                    task["claimed_at"] = None
                    task["started_at"] = None
                    upsert_task(task)
                    record_metric("task_auto_reset", 1.0, {"task_id": task["id"], "hours": str(int(hours))})
                actions.append(action)

        return actions

    def heal_abandoned_locks(self, dry_run: bool = True) -> list[str]:
        """Release expired locks."""
        from ea_database import get_db

        actions: list[str] = []
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM project_locks WHERE expires_at < datetime('now')"
            ).fetchall()

            for row in rows:
                action = f"RELEASE: Expired lock for {row['project']}"
                if not dry_run:
                    conn.execute("DELETE FROM project_locks WHERE project = ?", (row["project"],))
                    record_metric("lock_auto_released", 1.0, {"project": row["project"]})
                actions.append(action)

            if not dry_run:
                conn.commit()

        return actions


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="EverAgent v3.0 Autonomous Engine")
    sub = parser.add_subparsers(dest="command")

    recommend_p = sub.add_parser("recommend", help="Recommend task for agent")
    recommend_p.add_argument("--agent", required=True, help="Agent name")
    recommend_p.set_defaults(func=command_recommend)

    assign_p = sub.add_parser("assign", help="Auto-assign task to agent")
    assign_p.add_argument("--task-id", required=True, help="Task ID")
    assign_p.add_argument("--agent", required=True, help="Agent name")
    assign_p.set_defaults(func=command_assign)

    balance_p = sub.add_parser("balance", help="Show load balance suggestions")
    balance_p.set_defaults(func=command_balance)

    heal_p = sub.add_parser("heal", help="Run self-healing")
    heal_p.add_argument("--dry-run", action="store_true", default=True, help="Show what would be done")
    heal_p.set_defaults(func=command_heal)

    anomalies_p = sub.add_parser("anomalies", help="Detect anomalies")
    anomalies_p.set_defaults(func=command_anomalies)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    return args.func(args)


def command_recommend(args: argparse.Namespace) -> int:
    scheduler = AutonomousScheduler()
    rec = scheduler.recommend_task(args.agent)
    if rec:
        print(f"Recommended task for {args.agent}:")
        print(f"  ID: {rec.task_id}")
        print(f"  Target: {rec.target}")
        print(f"  Priority: {rec.priority}")
        print(f"  Est. duration: {rec.estimated_duration/3600:.1f}h")
        print(f"  Confidence: {rec.confidence:.2f}")
        print(f"  Reason: {rec.reason}")
    else:
        print(f"No suitable tasks found for {args.agent}")
    return 0


def command_assign(args: argparse.Namespace) -> int:
    scheduler = AutonomousScheduler()
    success = scheduler.assign_task(args.task_id, args.agent)
    return 0 if success else 1


def command_balance(args: argparse.Namespace) -> int:
    scheduler = AutonomousScheduler()
    suggestions = scheduler.rebalance_load()
    print("Load Balance Suggestions:")
    for s in suggestions:
        print(f"  {s}")
    return 0


def command_heal(args: argparse.Namespace) -> int:
    scheduler = AutonomousScheduler()
    healing = SelfHealing(scheduler)

    print("Self-Healing Report:")
    stuck = healing.heal_stuck_tasks(dry_run=args.dry_run)
    locks = healing.heal_abandoned_locks(dry_run=args.dry_run)

    for action in stuck + locks:
        print(f"  {action}")

    if not stuck and not locks:
        print("  System healthy — no issues detected")

    return 0


def command_anomalies(args: argparse.Namespace) -> int:
    scheduler = AutonomousScheduler()
    anomalies = scheduler.detect_anomalies()
    print("Anomaly Detection:")
    for a in anomalies:
        print(f"  {a}")
    if not anomalies:
        print("  No anomalies detected")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
