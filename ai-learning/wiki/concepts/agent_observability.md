# Agent 可观测性（Observability）

> 心跳检测 · 实时 Dashboard · 延迟告警 · 事件溯源

## 定义

Agent 可观测性是指通过心跳事件、任务状态流、资源采样等手段，实时感知分布式 Agent 系统的健康状态、执行进度与异常行为，并支持自动干预的能力体系。

## 核心机制

### 心跳检测（Heartbeat）

- **Push 模型**：Agent 主动周期性 emit `agent_heartbeat` 事件到事件日志层
- **TTL 判定**：Dashboard 根据最近心跳时间与 TTL（默认 5min）判定 alive / suspected / dead 三态
- **零侵入集成**：通过 `scripts/agent_heartbeat.py` 封装，不修改 Agent 业务协议

### 实时 Dashboard 数据流

- **采集层**：Agent → `emit_event()` → `events/YYYY-MM-DD/*.yaml`
- **聚合层**：`load_events()` 按时间窗口过滤、排序、统计
- **服务层**：FastAPI + SSE（Server-Sent Events）推送实时数据
- **展示层**：HTML + Vanilla JS，支持 Agent 健康面板、事件流、性能指标

### 延迟告警分级

| 级别 | 条件 | 动作 |
|------|------|------|
| INFO | 任务 > 30min | Dashboard 黄标 |
| WARN | 任务 > 2h | Dashboard 红标 + 事件流高亮 |
| CRITICAL | 任务 > 6h 或 Agent 失联 | 自动释放锁 + 标记 abandoned |

## 与 EverAgent 架构的关系

- 基于 Phase 1 事件日志层（`ea_events.py`）构建，无需新存储后端
- `agent_heartbeat` 事件类型已预注册于 `EVENT_TYPES`
- 告警引擎（`ea_alerts.py`）只读取任务状态与事件流，不修改状态机

## 关联概念

- [agent_systems.md](./agent_systems.md) — Agent 系统基础：ReAct / Tool Use / MCP
- [toa_system_design.md](./toa_system_design.md) — ToA 系统设计模式与审计链

## 参考

- 报告：`Agent_心跳检测与实时Dashboard设计.md`（2026-04-23）
- 代码：`scripts/ea_events.py`、`scripts/ea_dashboard.py`、`scripts/ea_alerts.py`
