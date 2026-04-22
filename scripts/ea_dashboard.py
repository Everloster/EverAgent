#!/usr/bin/env python3
"""EverAgent Real-time Dashboard — Phase 4 implementation.

Lightweight web dashboard using FastAPI + Server-Sent Events (SSE).
Provides real-time task status, agent health, event stream, and
knowledge graph activity.

Usage:
    python3 scripts/ea_dashboard.py [--port 8080]

Endpoints:
    GET /          — Dashboard HTML UI
    GET /api/status   — JSON: current system status
    GET /api/events   — SSE: real-time event stream
    GET /api/metrics  — JSON: aggregated metrics
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ea_common import ROOT
from ea_events import EVENT_TYPES, Event, load_events
from task_state import PROJECTS, TaskEntry, load_tasks_for_project

# FastAPI is optional — gracefully degrade if not installed
try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, StreamingResponse
    import uvicorn

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


app: FastAPI | None = None
if HAS_FASTAPI:
    app = FastAPI(title="EverAgent Dashboard")


# ---------------------------------------------------------------------------
# Data aggregation helpers
# ---------------------------------------------------------------------------

def get_project_status() -> dict[str, dict[str, any]]:
    """Get current status for all projects."""
    status: dict[str, dict[str, any]] = {}
    for project in PROJECTS:
        tasks = load_tasks_for_project(project)
        status[project] = {
            "total": len(tasks),
            "open": sum(1 for t in tasks if t.status == "open"),
            "claimed": sum(1 for t in tasks if t.status == "claimed"),
            "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
            "done": sum(1 for t in tasks if t.status == "done"),
            "failed": sum(1 for t in tasks if t.status == "failed"),
            "abandoned": sum(1 for t in tasks if t.status == "abandoned"),
        }
    return status


def get_recent_events(minutes: int = 60) -> list[dict[str, any]]:
    """Get events from the last N minutes."""
    since = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).strftime("%Y-%m-%d")
    events = load_events(start_date=since)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    recent = []
    for e in events:
        ts = datetime.fromisoformat(e.timestamp.replace("Z", "+00:00"))
        if ts >= cutoff:
            recent.append(e.to_dict())
    return recent[-50:]  # Last 50 events


def get_metrics() -> dict[str, any]:
    """Compute aggregated metrics from events."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_events = load_events(start_date=today)

    task_events = [e for e in today_events if e.type.startswith("task_")]
    type_counts = Counter(e.type for e in today_events)

    # Agent success rate (from task_done / task_failed)
    agent_stats: dict[str, dict[str, int]] = {}
    for e in today_events:
        if e.type in ("task_done", "task_failed") and e.actor:
            if e.actor not in agent_stats:
                agent_stats[e.actor] = {"done": 0, "failed": 0}
            agent_stats[e.actor]["done" if e.type == "task_done" else "failed"] += 1

    agent_performance = []
    for agent, stats in sorted(agent_stats.items()):
        total = stats["done"] + stats["failed"]
        rate = stats["done"] / total if total > 0 else 0
        agent_performance.append({
            "agent": agent,
            "success_rate": round(rate * 100, 1),
            "completed": stats["done"],
            "failed": stats["failed"],
        })

    return {
        "today_events": len(today_events),
        "today_task_events": len(task_events),
        "event_type_distribution": dict(type_counts.most_common()),
        "agent_performance": agent_performance,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# HTML Dashboard
# ---------------------------------------------------------------------------

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EverAgent Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
            padding: 1.5rem 2rem;
            border-bottom: 1px solid #334155;
        }
        .header h1 { font-size: 1.5rem; font-weight: 600; }
        .header .subtitle { color: #94a3b8; font-size: 0.875rem; margin-top: 0.25rem; }
        .container { padding: 1.5rem 2rem; max-width: 1400px; margin: 0 auto; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
        .card {
            background: #1e293b;
            border-radius: 0.75rem;
            padding: 1.25rem;
            border: 1px solid #334155;
        }
        .card h3 { font-size: 0.875rem; color: #94a3b8; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
        .status-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
        .status-item { text-align: center; padding: 0.5rem; background: #0f172a; border-radius: 0.5rem; }
        .status-item .num { font-size: 1.5rem; font-weight: 700; }
        .status-item .label { font-size: 0.75rem; color: #64748b; }
        .open { color: #22d3ee; }
        .in_progress { color: #fbbf24; }
        .done { color: #34d399; }
        .failed { color: #f87171; }
        .event-stream { max-height: 400px; overflow-y: auto; }
        .event-item {
            padding: 0.5rem 0;
            border-bottom: 1px solid #334155;
            font-size: 0.875rem;
            display: flex;
            gap: 0.75rem;
            align-items: baseline;
        }
        .event-time { color: #64748b; font-family: monospace; font-size: 0.75rem; min-width: 80px; }
        .event-type { font-weight: 600; min-width: 100px; }
        .event-type.task_claimed { color: #22d3ee; }
        .event-type.task_started { color: #fbbf24; }
        .event-type.task_done { color: #34d399; }
        .event-type.task_failed { color: #f87171; }
        .event-type.lock_acquired { color: #a78bfa; }
        .event-type.lock_released { color: #94a3b8; }
        .event-actor { color: #94a3b8; }
        .metrics-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
        .metrics-table th { text-align: left; padding: 0.5rem; color: #94a3b8; border-bottom: 1px solid #334155; }
        .metrics-table td { padding: 0.5rem; border-bottom: 1px solid #1e293b; }
        .badge {
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-green { background: #064e3b; color: #34d399; }
        .badge-yellow { background: #451a03; color: #fbbf24; }
        .badge-red { background: #450a0a; color: #f87171; }
        .refresh-indicator { position: fixed; top: 1rem; right: 1rem; width: 8px; height: 8px; border-radius: 50%; background: #34d399; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>EverAgent Dashboard</h1>
        <div class="subtitle">Real-time Cognitive Infrastructure Monitor</div>
        <div class="refresh-indicator" id="refresh-indicator"></div>
    </div>
    <div class="container">
        <div class="grid" id="project-cards"></div>
        <div class="grid">
            <div class="card">
                <h3>Event Stream</h3>
                <div class="event-stream" id="event-stream"></div>
            </div>
            <div class="card">
                <h3>Agent Performance</h3>
                <div id="agent-performance"></div>
            </div>
        </div>
    </div>
    <script>
        async function fetchStatus() {
            const res = await fetch('/api/status');
            return res.json();
        }
        async function fetchMetrics() {
            const res = await fetch('/api/metrics');
            return res.json();
        }
        function renderProjects(status) {
            const container = document.getElementById('project-cards');
            container.innerHTML = Object.entries(status).map(([name, s]) => {
                const health = s.in_progress > 0 ? 'badge-yellow' : s.failed > 0 ? 'badge-red' : 'badge-green';
                const healthText = s.in_progress > 0 ? 'BUSY' : s.failed > 0 ? 'ISSUE' : 'HEALTHY';
                return `
                    <div class="card">
                        <h3>${name} <span class="badge ${health}">${healthText}</span></h3>
                        <div class="status-grid">
                            <div class="status-item"><div class="num open">${s.open}</div><div class="label">Open</div></div>
                            <div class="status-item"><div class="num in_progress">${s.in_progress}</div><div class="label">In Progress</div></div>
                            <div class="status-item"><div class="num done">${s.done}</div><div class="label">Done</div></div>
                            <div class="status-item"><div class="num">${s.claimed}</div><div class="label">Claimed</div></div>
                            <div class="status-item"><div class="num failed">${s.failed}</div><div class="label">Failed</div></div>
                            <div class="status-item"><div class="num">${s.abandoned}</div><div class="label">Abandoned</div></div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        function renderAgentPerformance(metrics) {
            const container = document.getElementById('agent-performance');
            if (!metrics.agent_performance.length) {
                container.innerHTML = '<p style="color:#64748b">No agent activity today</p>';
                return;
            }
            container.innerHTML = `
                <table class="metrics-table">
                    <tr><th>Agent</th><th>Success Rate</th><th>Completed</th><th>Failed</th></tr>
                    ${metrics.agent_performance.map(a => `
                        <tr>
                            <td>${a.agent}</td>
                            <td><span class="badge ${a.success_rate >= 80 ? 'badge-green' : a.success_rate >= 50 ? 'badge-yellow' : 'badge-red'}">${a.success_rate}%</span></td>
                            <td>${a.completed}</td>
                            <td>${a.failed}</td>
                        </tr>
                    `).join('')}
                </table>
            `;
        }
        function escapeHtml(text) {
            if (!text) return '';
            return text.toString()
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
        function appendEvent(event) {
            const stream = document.getElementById('event-stream');
            const time = new Date(event.timestamp).toLocaleTimeString('zh-CN', {hour12: false});
            const div = document.createElement('div');
            div.className = 'event-item';
            const actor = escapeHtml(event.actor);
            const project = event.project ? escapeHtml(event.project) : '';
            const taskId = event.task_id ? escapeHtml(event.task_id) : '';
            div.innerHTML = `
                <span class="event-time">${time}</span>
                <span class="event-type ${escapeHtml(event.type)}">${escapeHtml(event.type)}</span>
                <span class="event-actor">${actor}${project ? ' → ' + project : ''}${taskId ? ' #' + taskId : ''}</span>
            `;
            stream.insertBefore(div, stream.firstChild);
            while (stream.children.length > 50) {
                stream.removeChild(stream.lastChild);
            }
        }
        async function init() {
            const status = await fetchStatus();
            renderProjects(status);
            const metrics = await fetchMetrics();
            renderAgentPerformance(metrics);
            // SSE for real-time events
            const evtSource = new EventSource('/api/events');
            evtSource.onmessage = (e) => {
                const event = JSON.parse(e.data);
                appendEvent(event);
                // Refresh status every few events
                if (Math.random() < 0.3) {
                    fetchStatus().then(renderProjects);
                    fetchMetrics().then(renderAgentPerformance);
                }
            };
        }
        init();
    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# FastAPI routes
# ---------------------------------------------------------------------------

if HAS_FASTAPI and app:

    @app.get("/", response_class=HTMLResponse)
    async def dashboard() -> str:
        return DASHBOARD_HTML

    @app.get("/api/status", response_model=None)
    async def api_status():
        return {
            "projects": get_project_status(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/api/metrics", response_model=None)
    async def api_metrics():
        return get_metrics()

    @app.get("/api/events")
    async def api_events() -> StreamingResponse:
        async def event_generator():
            import asyncio

            # Send recent events first
            for event in reversed(get_recent_events(minutes=60)):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            # Watch for new events
            last_check = datetime.now(timezone.utc)
            while True:
                await asyncio.sleep(2)
                now = datetime.now(timezone.utc)
                events = load_events()
                new_events = [
                    e for e in events
                    if datetime.fromisoformat(e.timestamp.replace("Z", "+00:00")) > last_check
                ]
                for event in new_events:
                    yield f"data: {json.dumps(event.to_dict(), ensure_ascii=False)}\n\n"
                last_check = now

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    if not HAS_FASTAPI:
        print("[ERROR] FastAPI/uvicorn not installed. Run: pip install fastapi uvicorn")
        return 1

    parser = argparse.ArgumentParser(description="EverAgent Real-time Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to run on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()

    print(f"[INFO] Starting EverAgent Dashboard on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
