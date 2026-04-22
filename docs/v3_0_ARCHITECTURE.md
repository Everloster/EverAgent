# EverAgent v3.0 — 分布式自治架构设计

> 版本：v3.0-alpha | 日期：2026-04-22
> 目标：从文件驱动进化为数据库驱动、事件驱动、自治优化的认知操作系统

---

## 架构愿景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EverAgent v3.0 — 自治认知网络                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  接入层   │ 多 Agent 网关 │ WebSocket 实时通道 │ CLI / API / Dashboard       │
├─────────────────────────────────────────────────────────────────────────────┤
│  编排层   │ 自治调度器 ←→ 任务 DAG 引擎 ←→ Agent 能力市场                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  认知层   │ 向量知识库 + 图数据库 + 语义搜索引擎                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  数据层   │ SQLite (核心状态) + 事件流 (审计) + 向量存储 (语义)                │
├─────────────────────────────────────────────────────────────────────────────┤
│  执行层   │ 沙箱化 Agent 运行时 + 增量验证 + 自动回滚                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 核心设计原则

1. **数据库即真相**：SQLite 是单一真相源，文件是视图/缓存
2. **事件即血液**：所有变更通过事件总线流动，支持订阅和回放
3. **自治即目标**：系统能自我诊断、自我修复、自我优化
4. **语义即连接**：知识图谱自动构建，跨项目语义关联

---

## 数据模型（SQLite Schema）

```sql
-- 任务表（替代 .project-task-state）
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,           -- T001
    project TEXT NOT NULL,
    type TEXT NOT NULL,
    target TEXT NOT NULL,
    value TEXT,
    priority TEXT CHECK(priority IN ('P1','P2','P3')),
    status TEXT CHECK(status IN ('open','claimed','in_progress','done','failed','abandoned')),
    claimed_by TEXT,
    claimed_at TIMESTAMP,
    started_at TIMESTAMP,
    done_at TIMESTAMP,
    failed_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 事件表（替代 events/ 目录）
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,  -- evt_20260422_120000_001
    type TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actor TEXT NOT NULL,
    project TEXT,
    task_id TEXT,
    payload JSON,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Agent 注册表
CREATE TABLE agents (
    name TEXT PRIMARY KEY,
    project TEXT,
    domain TEXT,
    status TEXT CHECK(status IN ('active','inactive','degraded')),
    success_rate REAL DEFAULT 0.0,
    total_tasks INTEGER DEFAULT 0,
    avg_duration REAL,
    last_heartbeat TIMESTAMP,
    capabilities JSON
);

-- 知识图谱节点
CREATE TABLE knowledge_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT CHECK(type IN ('entity','concept','paper','report')),
    project TEXT,
    vector_embedding BLOB,          -- 语义向量
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知识图谱关系
CREATE TABLE knowledge_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    FOREIGN KEY (source_id) REFERENCES knowledge_nodes(id),
    FOREIGN KEY (target_id) REFERENCES knowledge_nodes(id)
);

-- 项目锁表（替代 .agent-lock 文件）
CREATE TABLE project_locks (
    project TEXT PRIMARY KEY,
    agent TEXT NOT NULL,
    task_id TEXT NOT NULL,
    claimed_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    git_commit_sha TEXT
);

-- 执行日志（自动化 QA 数据）
CREATE TABLE execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    phase TEXT CHECK(phase IN ('input_validation','execution','output_validation','git_commit')),
    status TEXT CHECK(status IN ('success','failure')),
    duration_ms INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 自治调度器设计

```python
class AutonomousScheduler:
    """自治任务调度器 — 核心 v3.0 组件"""
    
    def schedule(self) -> list[Assignment]:
        # 1. 收集所有 open 任务
        open_tasks = self.db.query("SELECT * FROM tasks WHERE status = 'open'")
        
        # 2. 收集所有 active Agent
        agents = self.db.query("SELECT * FROM agents WHERE status = 'active'")
        
        # 3. 构建能力匹配矩阵
        assignments = []
        for task in open_tasks:
            best_agent = self._match_agent(task, agents)
            if best_agent:
                assignments.append(Assignment(task, best_agent))
        
        # 4. 检查依赖约束（DAG）
        valid_assignments = self._validate_dependencies(assignments)
        
        # 5. 检查资源约束（并发限制）
        final_assignments = self._apply_resource_limits(valid_assignments)
        
        return final_assignments
    
    def _match_agent(self, task: Task, agents: list[Agent]) -> Agent | None:
        """多维度 Agent 匹配算法"""
        scores = []
        for agent in agents:
            score = (
                self._capability_match(agent, task) * 0.4 +
                agent.success_rate * 0.3 +
                self._load_balance_factor(agent) * 0.2 +
                self._historical_performance(agent, task.type) * 0.1
            )
            scores.append((agent, score))
        
        return max(scores, key=lambda x: x[1])[0] if scores else None
```

---

## 事件驱动架构

```python
class EventBus:
    """中央事件总线 — 替代文件系统事件存储"""
    
    def __init__(self):
        self.subscribers: dict[str, list[Callable]] = {}
        self.event_store: EventStore  # SQLite / Kafka / Redis
    
    def emit(self, event: Event) -> None:
        # 1. 持久化到事件存储
        self.event_store.append(event)
        
        # 2. 广播给订阅者
        for subscriber in self.subscribers.get(event.type, []):
            asyncio.create_task(subscriber(event))
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        self.subscribers.setdefault(event_type, []).append(handler)

# 内置订阅者
class AutoHealer:
    """自动修复订阅者"""
    
    async def on_task_failed(self, event: Event):
        # 自动分析失败原因，决定重试或升级
        if event.payload.get('retryable', False):
            await self.scheduler.retry_task(event.task_id)
        else:
            await self.escalator.escalate(event)

class MetricsCollector:
    """实时指标收集"""
    
    async def on_any_event(self, event: Event):
        # 更新 Prometheus / Grafana 指标
        self.metrics.counter('everagent_events_total', 1, 
                           labels={'type': event.type})
```

---

## 知识图谱自动构建

```python
class KnowledgeGraphBuilder:
    """自动从报告中提取实体关系，构建知识图谱"""
    
    def ingest_report(self, report_path: Path) -> None:
        # 1. 解析 frontmatter
        frontmatter = parse_frontmatter(report_path)
        
        # 2. 提取实体（使用 LLM 或规则）
