---
title: "Agent 心跳检测与实时 Dashboard 设计"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-04-23"
---

# Agent 心跳检测与实时 Dashboard 设计

> 主题：基于事件日志层设计 Agent 心跳检测机制、实时 Dashboard 数据流、以及任务执行延迟告警系统
> 背景：EverAgent 多 Agent 协作系统已进入 Phase 1+ 事件溯源阶段，亟需可观测性基础设施保障系统健康与任务 SLA

---

## 1. 问题域与系统边界

### 1.1 为什么需要心跳与可观测性

EverAgent 采用「全局调度 + 子 Agent 自治」的分布式架构，NeuronAgent、ByteAgent、PsycheAgent 等 7 个子 Agent 并行运行于不同项目目录。Phase 1 引入的事件日志层（`events/YYYY-MM-DD/evt_*.yaml`）已提供审计追溯能力，但缺乏**实时健康感知**与**任务执行延迟干预**机制。具体痛点包括：

- **Agent 失联不可知**：子 Agent 崩溃或网络中断后，任务状态停留在 `in_progress`，阻塞项目锁长达 72h
- **Dashboard 静态化**：`python3 scripts/everagent.py dashboard` 启动的 FastAPI 服务仅展示聚合状态，无实时事件推送与 Agent 级健康指标
- **延迟无告警**：任务从 `claimed` 到 `done` 的耗时分布未知，无法识别长尾延迟与瓶颈 Agent

### 1.2 设计目标

| 目标 | 指标 | 优先级 |
|------|------|--------|
| Agent 存活感知 | 心跳 TTL ≤ 5min，误报率 < 1% | P0 |
| 实时 Dashboard | SSE 推送延迟 ≤ 2s，支持 50+ 并发连接 | P0 |
| 延迟告警 | 任务耗时 > 2h 触发告警，支持分级通知 | P1 |
| 零侵入采集 | 不修改现有 Agent 执行协议（AGENTS.md） | P0 |

---

## 2. 心跳检测机制设计

### 2.1 直觉类比（Layer 1）

将 Agent 心跳类比为医院 ICU 的心电监护仪：每个 Agent 定期发送「脉搏」（heartbeat event），Dashboard 持续绘制「心率曲线」。若脉搏消失超过阈值，系统自动标记「Agent 失联」并释放项目锁，如同监护仪触发警报并通知护士站。

### 2.2 形式定义（Layer 2）

**心跳事件 Schema**：

```yaml
event_id: evt_20260423_120000_001
type: agent_heartbeat
timestamp: 2026-04-23T12:00:00+08:00
actor: NeuronAgent
project: ai-learning
task_id: T030
payload:
  status: "executing"      # idle | executing | waiting
  progress: 65             # 百分比，仅 executing 时有效
  memory_mb: 512           # 可选：资源使用采样
  step: "writing_report"   # 可选：当前执行阶段
```

**存活判定函数**：

```python
def is_agent_alive(agent: str, project: Optional[str] = None, ttl_minutes: int = 5) -> bool:
    heartbeat = get_latest_heartbeat(agent, project)
    if heartbeat is None:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=ttl_minutes)
    return heartbeat.astimezone(timezone.utc) >= cutoff
```

**状态机扩展**：

```
alive ──(ttl 内无心跳)──→ suspected ──(连续 2 周期无心跳)──→ dead
  ↑                                                            │
  └────────────(心跳恢复)──────────────────────────────────────┘
```

- `alive`：正常执行中
- `suspected`：疑似失联（软状态，触发预警但不释放锁）
- `dead`：确认失联（自动释放项目锁，任务标记为 `abandoned`）

### 2.3 变体全景（Layer 3）

| 方案 | 机制 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| **Push 心跳**（选中） | Agent 主动 emit `agent_heartbeat` | 实现简单，与现有事件层无缝集成 | Agent 崩溃则立即停止心跳 | EverAgent 当前架构 |
| Pull 探活 | Dashboard 定期查询 Agent 进程 | 不依赖 Agent 配合 | 需进程级访问权限，跨机器难扩展 | 单机部署 |
| 任务事件推断 | 通过 `task_started`/`task_done` 推断存活 | 零额外事件 | 无法检测 idle Agent，延迟高 | 辅助手段 |
| 分布式共识 | Raft/Paxos 维护 Agent 成员列表 | 强一致性 | 过度设计，与当前规模不匹配 | 未来扩展 |

**决策理由**：Push 心跳与现有 `ea_events.py` 的 `emit_event()` 完全兼容，无需引入新依赖；`agent_heartbeat` 事件类型已在 `EVENT_TYPES` 中预注册（`scripts/ea_events.py:51`）。

### 2.4 工程实现（Layer 4）

**Agent 侧心跳发射**（零侵入封装）：

```python
# scripts/agent_heartbeat.py —— 由 Agent 在任务执行循环中调用
from ea_events import emit_event
import threading
import time

_heartbeat_thread: threading.Thread | None = None
_stop_event = threading.Event()

def _heartbeat_loop(agent: str, project: str, task_id: str, interval: int = 60):
    while not _stop_event.is_set():
        emit_event(
            event_type="agent_heartbeat",
            actor=agent,
            project=project,
            task_id=task_id,
            payload={"status": "executing"},
        )
        _stop_event.wait(interval)

def start_heartbeat(agent: str, project: str, task_id: str, interval: int = 60):
    global _heartbeat_thread
    _stop_event.clear()
    _heartbeat_thread = threading.Thread(
        target=_heartbeat_loop,
        args=(agent, project, task_id, interval),
        daemon=True,
    )
    _heartbeat_thread.start()

def stop_heartbeat():
    _stop_event.set()
    if _heartbeat_thread:
        _heartbeat_thread.join(timeout=5)
```

**集成点**：在 `task_exec.py start` 成功后调用 `start_heartbeat()`，在 `task_exec.py finish/fail` 后调用 `stop_heartbeat()`。无需修改 Agent 业务代码。

**Dashboard 侧健康检查**：

```python
# scripts/ea_dashboard.py 扩展
from ea_events import is_agent_alive, load_events
from datetime import datetime, timedelta, timezone

@app.get("/api/health")
async def api_health():
    agents = ["NeuronAgent", "ByteAgent", "PsycheAgent", "BioAgent", "SocratesAgent", "TrendAgent", "PracticeAgent"]
    health = {}
    for agent in agents:
        alive = is_agent_alive(agent, ttl_minutes=5)
        latest = get_latest_heartbeat(agent)
        health[agent] = {
            "alive": alive,
            "last_seen": latest.isoformat() if latest else None,
            "ttl_seconds": 300,
        }
    return health
```

### 2.5 前沿动态（Layer 5）

- **OpenTelemetry 集成**：未来可将心跳事件导出为 OTel Span，接入 Prometheus/Grafana 生态
- **自适应 TTL**：根据历史心跳抖动动态调整 TTL，减少网络抖动导致的误报（参考 Kubernetes Pod 驱逐策略）
- **心跳压缩**：高并发场景下，将 N 个心跳合并为批量事件，降低 I/O 压力

---

## 3. 实时 Dashboard 数据流设计

### 3.1 架构总览

```
┌─────────────┐     emit_event()     ┌──────────────┐     SSE / WebSocket     ┌─────────────┐
│   Agent     │ ───────────────────→ │  Event Log   │ ──────────────────────→ │  Dashboard  │
│  (Neuron)   │   agent_heartbeat    │ (YAML files) │     /api/events         │  (Browser)  │
└─────────────┘                      └──────────────┘                         └─────────────┘
       │                                    │
       │ task_claimed / task_done           │ load_events()
       ↓                                    ↓
┌─────────────┐                      ┌──────────────┐
│  Task State │ ←─────────────────── │  Aggregator  │
│  (YAML)     │   task_state_cli.py  │  (Python)    │
└─────────────┘                      └──────────────┘
```

### 3.2 数据流分层

| 层级 | 组件 | 职责 | 技术选型 |
|------|------|------|----------|
| **采集层** | Agent + `emit_event()` | 生成事件 | 现有 `ea_events.py`，零修改 |
| **存储层** | `events/YYYY-MM-DD/*.yaml` | 持久化审计日志 | 文件系统，按日期分片 |
| **聚合层** | `load_events()` + 内存索引 | 过滤、排序、统计 | Python 生成器，惰性加载 |
| **服务层** | FastAPI + SSE | 推送实时数据 | `ea_dashboard.py`，已存在 |
| **展示层** | HTML + Vanilla JS | 可视化渲染 | 现有 Dashboard UI 扩展 |

### 3.3 SSE 实时推送优化

当前 `ea_dashboard.py` 的 SSE 实现采用轮询（`asyncio.sleep(2)`），存在 2s 延迟。优化方案：

**文件系统 Watch 机制**（Linux inotify / macOS fsevents）：

```python
# 使用 watchfiles 库（可选依赖，降级为轮询）
try:
    from watchfiles import awatch
    HAS_WATCHFILES = True
except ImportError:
    HAS_WATCHFILES = False

async def event_generator():
    if HAS_WATCHFILES:
        async for changes in awatch(EVENTS_DIR):
            new_events = load_events(start_date=today)
            for event in new_events[-10:]:
                yield f"data: {json.dumps(event.to_dict())}\n\n"
    else:
        # 降级轮询
        while True:
            await asyncio.sleep(2)
            ...
```

**优势**：事件产生到推送延迟从 2s 降至 < 100ms；`watchfiles` 是 Rust 绑定，性能 overhead 极低。

### 3.4 Dashboard UI 扩展

在现有 `DASHBOARD_HTML` 基础上新增「Agent 健康」面板：

```html
<div class="card">
    <h3>Agent Health</h3>
    <div id="agent-health"></div>
</div>

<script>
async function fetchHealth() {
    const res = await fetch('/api/health');
    return res.json();
}
function renderHealth(health) {
    const container = document.getElementById('agent-health');
    container.innerHTML = Object.entries(health).map(([agent, h]) => {
        const statusClass = h.alive ? 'badge-green' : 'badge-red';
        const statusText = h.alive ? 'ONLINE' : 'OFFLINE';
        return `<div class="agent-health-item">
            <span>${agent}</span>
            <span class="badge ${statusClass}">${statusText}</span>
            <span class="last-seen">${h.last_seen ? new Date(h.last_seen).toLocaleTimeString() : 'N/A'}</span>
        </div>`;
    }).join('');
}
// 每 10s 刷新健康状态
setInterval(() => fetchHealth().then(renderHealth), 10000);
</script>
```

---

## 4. 任务延迟告警系统设计

### 4.1 延迟定义与分级

| 级别 | 条件 | 动作 | 通知方式 |
|------|------|------|----------|
| **INFO** | 任务耗时 > 30min | 记录日志 | Dashboard 黄标 |
| **WARN** | 任务耗时 > 2h | 触发告警 | Dashboard 红标 + 事件流高亮 |
| **CRITICAL** | 任务耗时 > 6h 或 Agent 失联 | 自动干预 | 释放锁 + 标记 abandoned + 通知管理员 |

### 4.2 告警检测引擎

**基于事件流的延迟计算**：

```python
# scripts/ea_alerts.py
from ea_events import load_events
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

@dataclass
class Alert:
    level: str      # INFO | WARN | CRITICAL
    task_id: str
    agent: str
    project: str
    duration_minutes: int
    message: str

def check_latency_alerts(project: str | None = None, warn_threshold: int = 120, critical_threshold: int = 360) -> list[Alert]:
    """扫描所有 in_progress 任务，计算已耗时并生成告警。"""
    from task_state import load_tasks_for_project, PROJECTS
    alerts = []
    projects = [project] if project else list(PROJECTS.keys())

    for proj in projects:
        tasks = load_tasks_for_project(proj)
        for task in tasks:
            if task.status != "in_progress" or not task.started_at:
                continue
            started = datetime.fromisoformat(task.started_at.replace("Z", "+00:00"))
            duration = int((datetime.now(timezone.utc) - started).total_seconds() / 60)

            if duration >= critical_threshold:
                level = "CRITICAL"
            elif duration >= warn_threshold:
                level = "WARN"
            elif duration >= 30:
                level = "INFO"
            else:
                continue

            alerts.append(Alert(
                level=level,
                task_id=task.id,
                agent=task.claimed_by or "unknown",
                project=proj,
                duration_minutes=duration,
                message=f"Task {task.id} in {proj} running for {duration}min by {task.claimed_by}",
            ))
    return alerts
```

**自动干预逻辑**（CRITICAL 级别）：

```python
def auto_intervene(alert: Alert):
    """对 CRITICAL 告警执行自动恢复。"""
    if alert.level != "CRITICAL":
        return

    # 1. 检查 Agent 是否存活
    alive = is_agent_alive(alert.agent, alert.project)
    if alive:
        # Agent 存活但任务卡住，可能是死锁或无限循环
        emit_event(
            event_type="system_audit",
            actor="ea_alerts",
            project=alert.project,
            task_id=alert.task_id,
            payload={"action": "flag_stuck_task", "duration_min": alert.duration_minutes},
        )
    else:
        # Agent 失联，释放锁并标记 abandoned
        from project_lock import release_lock
        from task_state_cli import command_abandon
        release_lock(alert.project, alert.task_id, alert.agent)
        command_abandon(argparse.Namespace(task_id=alert.task_id, reason=f"auto-intervene: agent dead after {alert.duration_minutes}min"))
```

### 4.3 告警事件化

所有告警均通过 `emit_event()` 记录，确保可追溯：

```yaml
event_id: evt_20260423_150000_010
type: system_audit
timestamp: 2026-04-23T15:00:00+08:00
actor: ea_alerts
project: ai-learning
task_id: T030
payload:
  alert_level: "WARN"
  duration_minutes: 150
  action: "notify"
  message: "Task T030 running for 150min by NeuronAgent"
```

---

## 5. 与现有系统的集成点

### 5.1 修改清单

| 文件 | 修改类型 | 内容 |
|------|----------|------|
| `scripts/agent_heartbeat.py` | 新增 | 心跳发射封装，供 Agent 集成 |
| `scripts/ea_dashboard.py` | 修改 | 新增 `/api/health` 端点、Agent 健康面板、watchfiles 优化 |
| `scripts/ea_alerts.py` | 新增 | 延迟检测引擎与自动干预逻辑 |
| `scripts/everagent.py` | 修改 | 新增 `alerts` 子命令，支持手动触发检查 |
| `ai-learning/AGENTS.md` | 修改 | 在 §2.1 领取任务流程中追加 `start_heartbeat()` 调用说明 |

### 5.2 不修改的文件（保持兼容）

- `scripts/ea_events.py`：已预定义 `agent_heartbeat`，无需改动
- `scripts/task_state_cli.py`：状态机不变，告警系统只读取不写入
- `scripts/execution_validator.py`：校验逻辑不受影响
- 各子项目 `AGENTS.md`：通过 `agent_heartbeat.py` 封装实现零侵入

---

## 6. 历史叙事与演化路径

### 6.1 从静态脚本到实时系统

EverAgent 的可观测性演进可分为三个阶段：

1. **Phase 0（手动阶段）**：通过 `git log` 和 `docs/LEARNING_PROJECTS_TASK_BOARD.md` 人工判断任务进度，无自动化监控
2. **Phase 1（事件溯源）**：引入 `events/` 目录与 `emit_event()`，实现事后审计，但 Dashboard 仍为静态聚合（2026-04 实现）
3. **Phase 2（实时可观测）**：本报告提出的心跳 + SSE + 告警体系，将延迟从「小时级人工发现」压缩至「秒级自动感知」

### 6.2 与业界方案的对比

| 特性 | EverAgent 本方案 | GitHub Actions | Kubernetes | Temporal |
|------|------------------|----------------|------------|----------|
| 心跳机制 | YAML 事件日志 | Workflow 日志 | kubelet Probe | Worker Poll |
| Dashboard | FastAPI + SSE | Web UI | Grafana | Temporal UI |
| 延迟告警 | 事件流计算 | 无原生支持 | Prometheus Alert | 内置 Timeout |
| 架构侵入性 | 零侵入 | 平台绑定 | 强绑定 | 强绑定 |

EverAgent 的核心差异在于**以文件系统为唯一事实来源**，所有状态通过 YAML 文件表达，Dashboard 是只读视图而非状态持有者。这一设计牺牲了部分性能，但获得了极致的可移植性与可审计性。

---

## 7. 未解问题与下一步

1. **心跳频率权衡**：1min 间隔对 150 行报告任务过于频繁，对 6h 论文精读又显稀疏。是否需要任务级自适应 TTL？
2. **告警疲劳**：自动干预可能导致误杀（如 Agent 实际在执行长任务）。如何引入「人工确认」或「优雅降级」？
3. **跨机器部署**：当前事件日志基于本地文件系统，若 Agent 分布在多机，需引入 NFS 或对象存储同步
4. **Metrics 持久化**：Dashboard 的 `get_metrics()` 仅计算当日事件，历史趋势分析需要时序数据库（如 SQLite + 预聚合表）

---

## 8. 参考与索引

- 代码实现：`scripts/ea_events.py`（事件层）、`scripts/ea_dashboard.py`（Dashboard）、`scripts/task_state_cli.py`（状态机）
- 协议规范：`AGENTS.md` §4（调度协议）、`docs/EXECUTION_SCHEMA.md`（执行校验）
- 相关报告：`Agent_Harness_三大设计流派解析.md`、`Agent_Memory_系统深度解析.md`
