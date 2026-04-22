#!/usr/bin/env python3
"""EverAgent v3.0 Database Layer — SQLite backend with dual-write compatibility.

This module provides a SQLite database backend while maintaining full backward
compatibility with v2.0 file-based state. All writes go to BOTH database and
files (dual-write); reads prefer database with fallback to files.

Schema:
    tasks          — Task state (replaces .project-task-state)
    events         — Event log (replaces events/*.yaml)
    agents         — Agent registry and performance metrics
    reports        — Report metadata with semantic tags
    knowledge_graph — Entity/Concept/Report relationships
    metrics        — Time-series metrics for analytics
"""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ea_common import EVENTS_DIR, ROOT, format_iso8601, now_iso

DB_PATH = ROOT / ".everagent.db"

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
-- Tasks: authoritative task state
CREATE TABLE IF NOT EXISTS tasks (
    id              TEXT PRIMARY KEY,
    project         TEXT NOT NULL,
    type            TEXT NOT NULL,
    target          TEXT NOT NULL,
    value           TEXT,
    priority        TEXT NOT NULL DEFAULT 'P2',
    required_capability TEXT NOT NULL DEFAULT 'task_executor',
    status          TEXT NOT NULL DEFAULT 'open',
    claimed_by      TEXT,
    claimed_at      TEXT,
    started_at      TEXT,
    done_at         TEXT,
    failed_reason   TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    version         INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_claimed_by ON tasks(claimed_by);

-- Events: immutable event log (Event Sourcing)
CREATE TABLE IF NOT EXISTS events (
    event_id        TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    timestamp       TEXT NOT NULL,
    actor           TEXT NOT NULL,
    project         TEXT,
    task_id         TEXT,
    payload         TEXT,  -- JSON
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
CREATE INDEX IF NOT EXISTS idx_events_project ON events(project);
CREATE INDEX IF NOT EXISTS idx_events_task ON events(task_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);

-- Agents: registry + runtime metrics
CREATE TABLE IF NOT EXISTS agents (
    name            TEXT PRIMARY KEY,
    project         TEXT NOT NULL,
    domain          TEXT,
    status          TEXT NOT NULL DEFAULT 'active',
    total_tasks     INTEGER NOT NULL DEFAULT 0,
    completed_tasks INTEGER NOT NULL DEFAULT 0,
    failed_tasks    INTEGER NOT NULL DEFAULT 0,
    avg_duration_sec REAL,
    last_heartbeat  TEXT,
    capability_score REAL NOT NULL DEFAULT 1.0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Reports: metadata with semantic indexing
CREATE TABLE IF NOT EXISTS reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    path            TEXT NOT NULL UNIQUE,
    project         TEXT NOT NULL,
    title           TEXT,
    report_type     TEXT,
    status          TEXT,
    updated_on      TEXT,
    semantic_tags   TEXT,  -- JSON array
    related_concepts TEXT, -- JSON array
    related_entities TEXT, -- JSON array
    word_count      INTEGER,
    frontmatter_valid INTEGER NOT NULL DEFAULT 0,
    quality_score   REAL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_reports_project ON reports(project);
CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type);

-- Knowledge Graph: entity/concept relationships
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    node_type       TEXT NOT NULL,  -- 'entity' | 'concept' | 'report'
    project         TEXT,
    description     TEXT,
    first_seen      TEXT,
    mention_count   INTEGER NOT NULL DEFAULT 1,
    UNIQUE(name, node_type, project)
);

CREATE TABLE IF NOT EXISTS knowledge_edges (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id       INTEGER NOT NULL,
    target_id       INTEGER NOT NULL,
    edge_type       TEXT NOT NULL DEFAULT 'relates_to',
    weight          REAL NOT NULL DEFAULT 1.0,
    first_seen      TEXT,
    UNIQUE(source_id, target_id, edge_type)
);

CREATE INDEX IF NOT EXISTS idx_kg_nodes_type ON knowledge_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_kg_edges_source ON knowledge_edges(source_id);

-- Metrics: time-series for analytics
CREATE TABLE IF NOT EXISTS metrics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name     TEXT NOT NULL,
    metric_value    REAL NOT NULL,
    labels          TEXT,  -- JSON
    timestamp       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_time ON metrics(timestamp);

-- Project locks: distributed lock tracking
CREATE TABLE IF NOT EXISTS project_locks (
    project         TEXT PRIMARY KEY,
    agent           TEXT NOT NULL,
    task_id         TEXT NOT NULL,
    claimed_at      TEXT NOT NULL,
    git_commit_sha  TEXT,
    expires_at      TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

_local = threading.local()


@contextmanager
def get_db():
    """Get a database connection (thread-local)."""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield _local.conn
    except Exception:
        _local.conn.rollback()
        raise


def init_db() -> None:
    """Initialize database schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    print(f"[INFO] Database initialized: {DB_PATH}")


# ---------------------------------------------------------------------------
# Task operations (dual-write compatible)
# ---------------------------------------------------------------------------

def sync_tasks_from_files() -> int:
    """One-time migration: load all .project-task-state files into DB."""
    from task_state import load_all_tasks

    tasks = load_all_tasks()
    with get_db() as conn:
        for t in tasks:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks
                (id, project, type, target, value, priority, required_capability,
                 status, claimed_by, claimed_at, started_at, done_at, failed_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    t.id, t.project, t.type, t.target, t.value, t.priority,
                    t.required_capability, t.status, t.claimed_by, t.claimed_at,
                    t.started_at, t.done_at, t.failed_reason,
                ),
            )
        conn.commit()
    return len(tasks)


def get_task(task_id: str) -> Optional[dict[str, Any]]:
    """Read task from DB (fallback to file if not in DB)."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row:
        return dict(row)
    # Fallback to v2.0 file
    from task_state import find_task
    t = find_task(task_id)
    if t:
        return {
            "id": t.id, "project": t.project, "type": t.type,
            "target": t.target, "value": t.value, "priority": t.priority,
            "status": t.status, "claimed_by": t.claimed_by,
            "claimed_at": t.claimed_at, "started_at": t.started_at,
            "done_at": t.done_at, "failed_reason": t.failed_reason,
        }
    return None


def list_tasks(
    project: Optional[str] = None,
    status: Optional[str] = None,
    claimed_by: Optional[str] = None,
) -> list[dict[str, Any]]:
    """List tasks with optional filtering."""
    query = "SELECT * FROM tasks WHERE 1=1"
    params: list[Any] = []
    if project:
        query += " AND project = ?"
        params.append(project)
    if status:
        query += " AND status = ?"
        params.append(status)
    if claimed_by:
        query += " AND claimed_by = ?"
        params.append(claimed_by)
    query += " ORDER BY updated_at DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def upsert_task(task_dict: dict[str, Any]) -> None:
    """Write task to DB (dual-write: also updates file via task_state)."""
    now = now_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO tasks
            (id, project, type, target, value, priority, required_capability,
             status, claimed_by, claimed_at, started_at, done_at, failed_reason, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status=excluded.status,
                claimed_by=excluded.claimed_by,
                claimed_at=excluded.claimed_at,
                started_at=excluded.started_at,
                done_at=excluded.done_at,
                failed_reason=excluded.failed_reason,
                updated_at=excluded.updated_at,
                version=version+1
            """,
            (
                task_dict["id"], task_dict.get("project", ""), task_dict.get("type", ""),
                task_dict.get("target", ""), task_dict.get("value"), task_dict.get("priority", "P2"),
                task_dict.get("required_capability", "task_executor"), task_dict.get("status", "open"),
                task_dict.get("claimed_by"), task_dict.get("claimed_at"), task_dict.get("started_at"),
                task_dict.get("done_at"), task_dict.get("failed_reason"), now,
            ),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Event operations (dual-write compatible)
# ---------------------------------------------------------------------------

def emit_event_db(
    event_type: str,
    actor: str,
    project: Optional[str] = None,
    task_id: Optional[str] = None,
    payload: Optional[dict[str, Any]] = None,
    event_id: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> str:
    """Write event to DB (dual-write: caller should also emit to file)."""
    eid = event_id or f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    ts = timestamp or now_iso()
    payload_json = json.dumps(payload, ensure_ascii=False) if payload else None

    with get_db() as conn:
        conn.execute(
            "INSERT INTO events (event_id, type, timestamp, actor, project, task_id, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (eid, event_type, ts, actor, project, task_id, payload_json),
        )
        conn.commit()
    return eid


def query_events(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    event_types: Optional[list[str]] = None,
    project: Optional[str] = None,
    task_id: Optional[str] = None,
    actor: Optional[str] = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Query events with filtering."""
    query = "SELECT * FROM events WHERE 1=1"
    params: list[Any] = []

    if start_time:
        query += " AND timestamp >= ?"
        params.append(start_time)
    if end_time:
        query += " AND timestamp <= ?"
        params.append(end_time)
    if event_types:
        placeholders = ",".join("?" * len(event_types))
        query += f" AND type IN ({placeholders})"
        params.extend(event_types)
    if project:
        query += " AND project = ?"
        params.append(project)
    if task_id:
        query += " AND task_id = ?"
        params.append(task_id)
    if actor:
        query += " AND actor = ?"
        params.append(actor)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    results = []
    for r in rows:
        d = dict(r)
        if d.get("payload"):
            d["payload"] = json.loads(d["payload"])
        results.append(d)
    return results


# ---------------------------------------------------------------------------
# Agent operations
# ---------------------------------------------------------------------------

def register_agent(name: str, project: str, domain: Optional[str] = None) -> None:
    """Register or update an agent."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO agents (name, project, domain)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                project=excluded.project,
                domain=excluded.domain,
                last_heartbeat=datetime('now')
            """,
            (name, project, domain),
        )
        conn.commit()


def record_agent_heartbeat(agent: str) -> None:
    """Update agent heartbeat timestamp."""
    with get_db() as conn:
        conn.execute(
            "UPDATE agents SET last_heartbeat = datetime('now') WHERE name = ?",
            (agent,),
        )
        conn.commit()


def update_agent_stats(agent: str, duration_sec: float, success: bool) -> None:
    """Update agent performance statistics."""
    with get_db() as conn:
        if success:
            conn.execute(
                """
                UPDATE agents SET
                    total_tasks = total_tasks + 1,
                    completed_tasks = completed_tasks + 1,
                    avg_duration_sec = CASE
                        WHEN avg_duration_sec IS NULL THEN ?
                        ELSE (avg_duration_sec * completed_tasks + ?) / (completed_tasks + 1)
                    END
                WHERE name = ?
                """,
                (duration_sec, duration_sec, agent),
            )
        else:
            conn.execute(
                "UPDATE agents SET total_tasks = total_tasks + 1, failed_tasks = failed_tasks + 1 WHERE name = ?",
                (agent,),
            )
        conn.commit()


def get_agent_leaderboard() -> list[dict[str, Any]]:
    """Get agent performance leaderboard."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT name, project, total_tasks, completed_tasks, failed_tasks,
                   avg_duration_sec, capability_score,
                   CASE WHEN total_tasks > 0 THEN ROUND(completed_tasks * 100.0 / total_tasks, 1) ELSE 0 END as success_rate
            FROM agents
            ORDER BY capability_score DESC, success_rate DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Knowledge Graph operations
# ---------------------------------------------------------------------------

def upsert_knowledge_node(name: str, node_type: str, project: Optional[str] = None, description: Optional[str] = None) -> int:
    """Upsert a knowledge graph node. Returns node id."""
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO knowledge_nodes (name, node_type, project, description, first_seen)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(name, node_type, project) DO UPDATE SET
                mention_count = mention_count + 1
            RETURNING id
            """,
            (name, node_type, project, description),
        )
        row = cur.fetchone()
        conn.commit()
        return row[0]


def create_knowledge_edge(source_id: int, target_id: int, edge_type: str = "relates_to", weight: float = 1.0) -> None:
    """Create a relationship between two knowledge nodes."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO knowledge_edges (source_id, target_id, edge_type, weight, first_seen)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(source_id, target_id, edge_type) DO UPDATE SET
                weight = weight + 1.0
            """,
            (source_id, target_id, edge_type, weight),
        )
        conn.commit()


def query_knowledge_graph(node_type: Optional[str] = None, project: Optional[str] = None) -> list[dict[str, Any]]:
    """Query knowledge graph nodes."""
    query = "SELECT * FROM knowledge_nodes WHERE 1=1"
    params: list[Any] = []
    if node_type:
        query += " AND node_type = ?"
        params.append(node_type)
    if project:
        query += " AND project = ?"
        params.append(project)
    query += " ORDER BY mention_count DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Metrics operations
# ---------------------------------------------------------------------------

def record_metric(metric_name: str, metric_value: float, labels: Optional[dict[str, str]] = None) -> None:
    """Record a time-series metric."""
    labels_json = json.dumps(labels, ensure_ascii=False) if labels else None
    with get_db() as conn:
        conn.execute(
            "INSERT INTO metrics (metric_name, metric_value, labels) VALUES (?, ?, ?)",
            (metric_name, metric_value, labels_json),
        )
        conn.commit()


def get_metrics(metric_name: str, start_time: Optional[str] = None, end_time: Optional[str] = None) -> list[dict[str, Any]]:
    """Query metrics."""
    query = "SELECT * FROM metrics WHERE metric_name = ?"
    params: list[Any] = [metric_name]
    if start_time:
        query += " AND timestamp >= ?"
        params.append(start_time)
    if end_time:
        query += " AND timestamp <= ?"
        params.append(end_time)
    query += " ORDER BY timestamp DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Lock operations
# ---------------------------------------------------------------------------

def acquire_lock_db(project: str, agent: str, task_id: str, git_commit_sha: str = "", ttl_hours: int = 72) -> bool:
    """Acquire project lock in DB."""
    now = datetime.now(timezone.utc)
    expires = now + __import__("datetime").timedelta(hours=ttl_hours)

    with get_db() as conn:
        # Check existing lock
        row = conn.execute("SELECT * FROM project_locks WHERE project = ?", (project,)).fetchone()
        if row:
            expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
            if expires_at > now:
                return False  # Lock held and not expired

        conn.execute(
            """
            INSERT INTO project_locks (project, agent, task_id, claimed_at, git_commit_sha, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(project) DO UPDATE SET
                agent=excluded.agent,
                task_id=excluded.task_id,
                claimed_at=excluded.claimed_at,
                git_commit_sha=excluded.git_commit_sha,
                expires_at=excluded.expires_at
            """,
            (project, agent, task_id, now.isoformat(), git_commit_sha, expires.isoformat()),
        )
        conn.commit()
    return True


def release_lock_db(project: str) -> None:
    """Release project lock in DB."""
    with get_db() as conn:
        conn.execute("DELETE FROM project_locks WHERE project = ?", (project,))
        conn.commit()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="EverAgent v3.0 Database")
    sub = parser.add_subparsers(dest="command")

    init_p = sub.add_parser("init", help="Initialize database")
    init_p.set_defaults(func=lambda _: (init_db(), print("[PASS] Database initialized")) or 0)

    sync_p = sub.add_parser("sync", help="Sync tasks from files to DB")
    sync_p.set_defaults(func=lambda _: print(f"[PASS] Synced {sync_tasks_from_files()} tasks"))

    stats_p = sub.add_parser("stats", help="Show database stats")
    stats_p.set_defaults(func=lambda _: print_stats())

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    return args.func(args)


def print_stats() -> None:
    """Print database statistics."""
    with get_db() as conn:
        tables = ["tasks", "events", "agents", "reports", "knowledge_nodes", "knowledge_edges", "metrics", "project_locks"]
        for table in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table:20}: {count:6}")


if __name__ == "__main__":
    import sys
    sys.exit(main())
