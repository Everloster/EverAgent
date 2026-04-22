#!/usr/bin/env python3
"""EverAgent v3.0 Stream Processing Engine — Event-driven real-time analytics.

This module provides stream processing capabilities on top of the event log:
- Real-time event consumers (pub/sub pattern)
- Windowed aggregations (tumbling/sliding windows)
- Continuous queries for live dashboards
- Automatic metric recording from event streams

Usage:
    from ea_stream import EventStream, Window
    stream = EventStream()
    stream.subscribe("task_done", my_handler)
    stream.start()
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

from ea_database import emit_event_db, query_events, record_metric
from ea_events import emit_event, load_events


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Event:
    event_id: str
    type: str
    timestamp: str
    actor: str
    project: Optional[str] = None
    task_id: Optional[str] = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class WindowResult:
    window_start: datetime
    window_end: datetime
    event_count: int
    event_types: dict[str, int]
    actor_counts: dict[str, int]
    project_counts: dict[str, int]


# ---------------------------------------------------------------------------
# Event Stream (Pub/Sub)
# ---------------------------------------------------------------------------

class EventStream:
    """Real-time event stream with pub/sub support."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable[[Event], None]]] = defaultdict(list)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_check = datetime.now(timezone.utc)
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Subscribe to a specific event type."""
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Unsubscribe from an event type."""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def emit(self, event: Event) -> None:
        """Emit an event to all subscribers."""
        # Global subscribers (*)
        for handler in self._subscribers.get("*", []):
            try:
                handler(event)
            except Exception as exc:
                print(f"[WARN] Handler error for {event.type}: {exc}")

        # Type-specific subscribers
        for handler in self._subscribers.get(event.type, []):
            try:
                handler(event)
            except Exception as exc:
                print(f"[WARN] Handler error for {event.type}: {exc}")

    def start(self, poll_interval: float = 2.0) -> None:
        """Start background polling for new events."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, args=(poll_interval,), daemon=True)
        self._thread.start()
        print(f"[INFO] Event stream started (poll={poll_interval}s)")

    def stop(self) -> None:
        """Stop background polling."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        print("[INFO] Event stream stopped")

    def _poll_loop(self, poll_interval: float) -> None:
        """Background loop: poll for new events and emit to subscribers."""
        while self._running:
            time.sleep(poll_interval)
            try:
                self._check_new_events()
            except Exception as exc:
                print(f"[WARN] Poll error: {exc}")

    def _check_new_events(self) -> None:
        """Check for new events since last poll."""
        now = datetime.now(timezone.utc)
        # Query DB for new events
        events = query_events(start_time=self._last_check.isoformat(), limit=100)
        for e in events:
            event = Event(
                event_id=e["event_id"],
                type=e["type"],
                timestamp=e["timestamp"],
                actor=e["actor"],
                project=e.get("project"),
                task_id=e.get("task_id"),
                payload=e.get("payload", {}),
            )
            self.emit(event)
        if events:
            self._last_check = now


# ---------------------------------------------------------------------------
# Windowed Aggregations
# ---------------------------------------------------------------------------

class Window:
    """Tumbling window for event aggregation."""

    def __init__(self, size_minutes: int = 5):
        self.size = timedelta(minutes=size_minutes)
        self._events: deque[Event] = deque()
        self._lock = threading.Lock()

    def add(self, event: Event) -> None:
        """Add an event to the window."""
        with self._lock:
            self._events.append(event)
            self._trim()

    def _trim(self) -> None:
        """Remove events outside the window."""
        cutoff = datetime.now(timezone.utc) - self.size
        while self._events:
            ts = datetime.fromisoformat(self._events[0].timestamp.replace("Z", "+00:00"))
            if ts < cutoff:
                self._events.popleft()
            else:
                break

    def compute(self) -> WindowResult:
        """Compute aggregation for the current window."""
        with self._lock:
            self._trim()
            now = datetime.now(timezone.utc)
            start = now - self.size

            event_types: dict[str, int] = defaultdict(int)
            actor_counts: dict[str, int] = defaultdict(int)
            project_counts: dict[str, int] = defaultdict(int)

            for e in self._events:
                event_types[e.type] += 1
                actor_counts[e.actor] += 1
                if e.project:
                    project_counts[e.project] += 1

            return WindowResult(
                window_start=start,
                window_end=now,
                event_count=len(self._events),
                event_types=dict(event_types),
                actor_counts=dict(actor_counts),
                project_counts=dict(project_counts),
            )


# ---------------------------------------------------------------------------
# Continuous Queries
# ---------------------------------------------------------------------------

class ContinuousQuery:
    """Continuous query that runs on a schedule and produces results."""

    def __init__(self, name: str, interval_seconds: int, query_fn: Callable[[], dict[str, Any]]):
        self.name = name
        self.interval = interval_seconds
        self.query_fn = query_fn
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.last_result: Optional[dict[str, Any]] = None

    def start(self) -> None:
        """Start the continuous query."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"[INFO] Continuous query '{self.name}' started (interval={self.interval}s)")

    def stop(self) -> None:
        """Stop the continuous query."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    def _loop(self) -> None:
        """Run query on schedule."""
        while self._running:
            try:
                self.last_result = self.query_fn()
            except Exception as exc:
                print(f"[WARN] Query '{self.name}' error: {exc}")
            time.sleep(self.interval)


# ---------------------------------------------------------------------------
# Built-in stream processors
# ---------------------------------------------------------------------------

def create_task_completion_processor() -> Callable[[Event], None]:
    """Create a processor that tracks task completion metrics."""
    def processor(event: Event) -> None:
        if event.type == "task_done" and event.task_id:
            # Record completion metric
            record_metric("task_completion", 1.0, {
                "project": event.project or "unknown",
                "agent": event.actor,
                "task_id": event.task_id,
            })
            # Update agent stats
            from ea_database import update_agent_stats
            # Estimate duration from payload or default
            duration = event.payload.get("duration_sec", 3600)
            update_agent_stats(event.actor, duration, success=True)

        elif event.type == "task_failed" and event.task_id:
            record_metric("task_failure", 1.0, {
                "project": event.project or "unknown",
                "agent": event.actor,
                "task_id": event.task_id,
            })
            from ea_database import update_agent_stats
            update_agent_stats(event.actor, 0, success=False)

    return processor


def create_project_health_processor() -> Callable[[Event], None]:
    """Create a processor that monitors project health."""
    active_tasks: dict[str, int] = defaultdict(int)

    def processor(event: Event) -> None:
        project = event.project or "global"

        if event.type == "task_started":
            active_tasks[project] += 1
            record_metric("project_active_tasks", active_tasks[project], {"project": project})

        elif event.type in ("task_done", "task_failed", "task_abandoned"):
            active_tasks[project] = max(0, active_tasks[project] - 1)
            record_metric("project_active_tasks", active_tasks[project], {"project": project})

        # Alert if too many concurrent tasks
        if active_tasks[project] > 3:
            record_metric("project_overload", 1.0, {"project": project, "active": str(active_tasks[project])})

    return processor


def create_lock_monitor_processor() -> Callable[[Event], None]:
    """Create a processor that monitors lock health."""
    locks: dict[str, dict[str, Any]] = {}

    def processor(event: Event) -> None:
        if event.type == "lock_acquired" and event.project:
            locks[event.project] = {
                "agent": event.actor,
                "task_id": event.task_id,
                "acquired_at": event.timestamp,
            }

        elif event.type == "lock_released" and event.project:
            if event.project in locks:
                del locks[event.project]

        # Check for stale locks (older than 72h)
        now = datetime.now(timezone.utc)
        for project, info in list(locks.items()):
            acquired = datetime.fromisoformat(info["acquired_at"].replace("Z", "+00:00"))
            if now - acquired > timedelta(hours=72):
                record_metric("stale_lock_detected", 1.0, {
                    "project": project,
                    "agent": info["agent"],
                    "hours": str(int((now - acquired).total_seconds() / 3600)),
                })

    return processor


# ---------------------------------------------------------------------------
# Stream Manager (singleton)
# ---------------------------------------------------------------------------

class StreamManager:
    """Central manager for all stream processing."""

    _instance: Optional[StreamManager] = None
    _lock = threading.Lock()

    def __new__(cls) -> StreamManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.stream = EventStream()
        self.window = Window(size_minutes=5)
        self.queries: list[ContinuousQuery] = []
        self._processors: list[Callable[[Event], None]] = []

    def setup_default_processors(self) -> None:
        """Register all built-in processors."""
        processors = [
            create_task_completion_processor(),
            create_project_health_processor(),
            create_lock_monitor_processor(),
        ]
        for p in processors:
            self._processors.append(p)
            self.stream.subscribe("*", p)

        # Also add window updater
        self.stream.subscribe("*", lambda e: self.window.add(e))

    def add_query(self, name: str, interval: int, query_fn: Callable[[], dict[str, Any]]) -> ContinuousQuery:
        """Add a continuous query."""
        cq = ContinuousQuery(name, interval, query_fn)
        self.queries.append(cq)
        return cq

    def start(self) -> None:
        """Start all stream processing."""
        self.setup_default_processors()
        self.stream.start()
        for q in self.queries:
            q.start()
        print("[INFO] Stream manager started")

    def stop(self) -> None:
        """Stop all stream processing."""
        self.stream.stop()
        for q in self.queries:
            q.stop()
        print("[INFO] Stream manager stopped")

    def get_window_stats(self) -> WindowResult:
        """Get current window statistics."""
        return self.window.compute()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="EverAgent v3.0 Stream Engine")
    sub = parser.add_subparsers(dest="command")

    start_p = sub.add_parser("start", help="Start stream processing")
    start_p.set_defaults(func=lambda _: start_stream())

    stats_p = sub.add_parser("stats", help="Show window statistics")
    stats_p.set_defaults(func=lambda _: print_stats())

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    return args.func(args)


def start_stream() -> int:
    manager = StreamManager()
    manager.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
    return 0


def print_stats() -> int:
    manager = StreamManager()
    stats = manager.get_window_stats()
    print(f"Window: {stats.window_start.strftime('%H:%M:%S')} - {stats.window_end.strftime('%H:%M:%S')}")
    print(f"Events: {stats.event_count}")
    print("By type:")
    for t, c in stats.event_types.items():
        print(f"  {t}: {c}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
