#!/usr/bin/env python3
"""EverAgent Event Sourcing layer — Phase 1 implementation.

All state mutations are recorded as immutable events under events/YYYY-MM-DD/.
This provides full audit trail, real-time observability, and enables future
features like replay, metrics, and automated optimization.

Event Schema (v1.0):
    event_id   : str   — unique event identifier (evt_{timestamp}_{seq})
    type       : str   — event type (see EVENT_TYPES)
    timestamp  : str   — ISO8601 when the event occurred
    actor      : str   — Agent or system component that triggered the event
    project    : str   — target project (optional for global events)
    task_id    : str   — related task ID (optional)
    payload    : dict  — event-specific data
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from ea_common import EVENTS_DIR, format_iso8601, parse_iso8601


EVENT_TYPES = {
    # Task lifecycle
    "task_claimed",
    "task_started",
    "task_done",
    "task_failed",
    "task_help_needed",
    "task_cancelled",
    "task_abandoned",
    "task_reopened",
    # Lock lifecycle
    "lock_acquired",
    "lock_released",
    "lock_expired",
    # Validation
    "input_validated",
    "output_validated",
    "validation_failed",
    # Report / knowledge
    "report_created",
    "report_modified",
    "wiki_updated",
    # Agent
    "agent_heartbeat",
    "agent_registered",
    # System
    "system_sync",
    "system_audit",
}


@dataclass
class Event:
    event_id: str
    type: str
    timestamp: str
    actor: str
    project: Optional[str] = None
    task_id: Optional[str] = None
    payload: dict[str, Any] = field(default_factory=dict)
    message_id: Optional[str] = None
    aamp: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "type": self.type,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "project": self.project,
            "task_id": self.task_id,
            "payload": self.payload,
            "message_id": self.message_id,
            "aamp": self.aamp,
        }

    def to_yaml(self) -> str:
        """Serialize event to a compact YAML block."""
        lines = [
            f"event_id: {self.event_id}",
            f"type: {self.type}",
            f"timestamp: {self.timestamp}",
            f"actor: {self.actor}",
        ]
        if self.project:
            lines.append(f"project: {self.project}")
        if self.task_id:
            lines.append(f"task_id: {self.task_id}")
        if self.message_id:
            lines.append(f"message_id: {self.message_id}")
        if self.aamp:
            lines.append(f"aamp: {json.dumps(self.aamp, ensure_ascii=False, separators=(',', ':'))}")
        if self.payload:
            lines.append("payload:")
            for key, value in self.payload.items():
                if isinstance(value, str):
                    lines.append(f'  {key}: "{value}"')
                else:
                    lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
        return "\n".join(lines)


def _next_sequence(directory: Path) -> int:
    """Count existing event files to determine next sequence number.

    Uses a simple file-based counter stored in .seq to avoid race conditions
    in multi-process scenarios.
    """
    seq_file = directory / ".seq"
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        seq_file.write_text("1", encoding="utf-8")
        return 1

    try:
        current = int(seq_file.read_text(encoding="utf-8").strip())
    except (ValueError, FileNotFoundError):
        current = 0

    next_seq = current + 1
    seq_file.write_text(str(next_seq), encoding="utf-8")
    return next_seq


def emit_event(
    event_type: str,
    actor: str,
    project: Optional[str] = None,
    task_id: Optional[str] = None,
    payload: Optional[dict[str, Any]] = None,
    aamp: Optional[dict[str, Any]] = None,
) -> Event:
    """Emit a new event and persist it to the events directory.

    Returns the created Event object.
    """
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unknown event type: {event_type}. Valid: {EVENT_TYPES}")

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M%S")

    day_dir = EVENTS_DIR / date_str
    day_dir.mkdir(parents=True, exist_ok=True)

    seq = _next_sequence(day_dir)
    event_id = f"evt_{date_str.replace('-', '')}_{time_str}_{seq:03d}"
    message_id = f"<{event_id}@everagent.local>"
    aamp_envelope = aamp or _build_aamp_envelope(
        event_type=event_type,
        event_id=event_id,
        message_id=message_id,
        actor=actor,
        project=project,
        task_id=task_id,
        payload=payload or {},
    )

    event = Event(
        event_id=event_id,
        type=event_type,
        timestamp=format_iso8601(now),
        actor=actor,
        project=project,
        task_id=task_id,
        payload=payload or {},
        message_id=message_id,
        aamp=aamp_envelope,
    )

    event_path = day_dir / f"{event_id}.yaml"
    event_path.write_text(event.to_yaml() + "\n", encoding="utf-8")

    return event


def _build_aamp_envelope(
    event_type: str,
    event_id: str,
    message_id: str,
    actor: str,
    project: Optional[str],
    task_id: Optional[str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact AAMP 1.1 envelope for task lifecycle events."""
    if not task_id:
        return {}

    intent_by_event = {
        "task_claimed": "task.ack",
        "task_started": "task.stream.opened",
        "task_help_needed": "task.help_needed",
        "task_done": "task.result",
        "task_failed": "task.result",
        "task_cancelled": "task.cancel",
    }
    intent = intent_by_event.get(event_type)
    if not intent:
        return {}

    envelope: dict[str, Any] = {
        "version": "1.1",
        "intent": intent,
        "task_id": task_id,
        "message_id": message_id,
        "dispatch_context": {
            "project": project,
            "actor": actor,
            "event_type": event_type,
        },
    }
    if event_type == "task_done":
        envelope["status"] = "completed"
    elif event_type == "task_failed":
        envelope["status"] = "rejected"
    elif event_type == "task_help_needed" and payload.get("suggested_options"):
        envelope["suggested_options"] = payload["suggested_options"]
    elif event_type == "task_started":
        envelope["stream_id"] = f"stream_{task_id}"
    return envelope


def _parse_scalar(value: str) -> Any:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value in ("true", "false"):
        return value == "true"
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value)
        except ValueError:
            return value
    return value


def load_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_types: Optional[set[str]] = None,
    project: Optional[str] = None,
    task_id: Optional[str] = None,
    actor: Optional[str] = None,
) -> list[Event]:
    """Load events with optional filtering.

    Args:
        start_date: Inclusive start date (YYYY-MM-DD)
        end_date: Inclusive end date (YYYY-MM-DD)
        event_types: Filter by event types
        project: Filter by project
        task_id: Filter by task ID
        actor: Filter by actor
    """
    events: list[Event] = []

    if not EVENTS_DIR.exists():
        return events

    for day_dir in sorted(EVENTS_DIR.iterdir()):
        if not day_dir.is_dir():
            continue
        date_part = day_dir.name

        if start_date and date_part < start_date:
            continue
        if end_date and date_part > end_date:
            continue

        for event_file in sorted(day_dir.glob("evt_*.yaml")):
            event = _parse_event_file(event_file)
            if event is None:
                continue

            if event_types and event.type not in event_types:
                continue
            if project and event.project != project:
                continue
            if task_id and event.task_id != task_id:
                continue
            if actor and event.actor != actor:
                continue

            events.append(event)

    return events


def _parse_event_file(path: Path) -> Optional[Event]:
    """Parse a single event file into an Event object."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    data: dict[str, Any] = {"payload": {}}
    in_payload = False

    for raw_line in text.splitlines():
        stripped = raw_line.rstrip()
        if not stripped:
            continue

        # Payload fields are indented with 2 spaces
        if stripped.startswith("  ") and ":" in stripped and not stripped.startswith("    "):
            key, value = stripped[2:].split(":", 1)
            key = key.strip()
            value = value.strip()
            data["payload"][key] = _parse_scalar(value)
            continue

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if key == "payload":
            in_payload = True
            continue

        data[key] = _parse_scalar(value.strip("'"))

    required = {"event_id", "type", "timestamp", "actor"}
    if not required.issubset(data.keys()):
        return None

    return Event(
        event_id=data["event_id"],
        type=data["type"],
        timestamp=data["timestamp"],
        actor=data["actor"],
        project=data.get("project"),
        task_id=data.get("task_id"),
        payload=data.get("payload", {}),
        message_id=data.get("message_id"),
        aamp=data.get("aamp", {}),
    )


def get_latest_heartbeat(agent: str, project: Optional[str] = None) -> Optional[datetime]:
    """Get the most recent heartbeat timestamp for an agent."""
    events = load_events(
        event_types={"agent_heartbeat"},
        actor=agent,
        project=project,
    )
    if not events:
        return None
    latest = max(
        events,
        key=lambda e: parse_iso8601(e.timestamp) or datetime.min.replace(tzinfo=timezone.utc),
    )
    return parse_iso8601(latest.timestamp)


def is_agent_alive(agent: str, project: Optional[str] = None, ttl_minutes: int = 30) -> bool:
    """Check if an agent has sent a heartbeat within the TTL window."""
    heartbeat = get_latest_heartbeat(agent, project)
    if heartbeat is None:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=ttl_minutes)
    return heartbeat.astimezone(timezone.utc) >= cutoff
