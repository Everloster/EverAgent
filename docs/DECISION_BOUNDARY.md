# Agent Decision Boundary — 决策边界协议

> 版本：v1.0 | 日期：2026-04-05
> 适用范围：所有 Subagent（EverAgent 除外）
> 参考：AGENTS.md §2

---

## §1 三层决策矩阵

### L1：完全自主（无需 EverAgent 介入）

Subagent 可独立决定并执行，无需任何确认。

| 决策项 | 示例 | 限制 |
|--------|------|------|
| 任务执行细节 | 先读哪篇参考文献、用哪个分析框架 | 必须在 AGENTS.md 定义范围内 |
| 报告内容 | 具体措辞、引用哪段原文、图表类型 | 必须符合防幻觉边界 |
| 格式细节 | 章节顺序、bullet points 数量 | 必须在 SKILL.md 定义范围内 |
| 执行顺序 | 多文件任务中先写哪个报告 | 同一任务内 |
| 时间分配 | 某步骤花多少时间 | 不超过任务总时长上限 |

### L2：自主决策，但须 EverAgent 确认后执行

Subagent 可识别需求，但须上报等待指示。

| 决策项 | 触发条件 | 上报内容 |
|--------|---------|---------|
| 发现防幻觉边界外的空白领域 | 论文/文本超出当前边界定义 | 建议扩充边界，说明理由 |
| 识别高价值但未列入 Task Board 的任务 | 读 PAPERS_INDEX 时发现缺失 | 建议新任务，附优先级评估（P1/P2/P3） |
| 发现任务描述与实际不符 | 领取后发现目标无法完成 | 申请变更为更合适的目标 |
| 项目结构性问题 | CONTEXT.md 与实际报告严重不一致 | 申请 EverAgent 执行任务1（优化） |
| 技术路线分歧 | 同一问题有多种实现方式 | 列出选项，推荐其一 |

### L3：完全禁止（须 EverAgent 执行或用户授权）

| 决策项 | 原因 |
|--------|------|
| 修改全局配置文件 | AGENTS.md、CLAUDE.md、scripts/ |
| 跨项目读写其他子项目文件 | 子项目隔离原则 |
| 修改其他子Agent的AGENTS.md | 权限边界 |
| 创建新项目 | 任务2专属 |
| 直接修改 Task Board | 须走 .project-task-state |
| 删除历史记录 | 禁止删除 done 状态记录 |
| 修改已发布的报告 | 只可追加，不可修改已有结论 |
| 绕过防幻觉边界 | 禁止推测，必须标注"unclear from the text" |

---

## §2 上报协议

当 Subagent 遇到 L2 决策时，通过 commit message 特殊标记：

```bash
git commit -m "[task-execution] {project}: {描述}

Agent: {AgentName}
Task-Type: task-execution
Status: needs-review
Review-Type: boundary_extension | new_task_proposal | task_redirect | structural_fix
Detail: {简洁描述问题和解决方案建议}
"
```

### Review-Type 说明

| Review-Type | 含义 | EverAgent 处理方式 |
|-------------|------|-------------------|
| `boundary_extension` | 建议扩充防幻觉边界 | 更新对应项目的 CONTEXT.md |
| `new_task_proposal` | 建议新任务 | 在 Task Board 追加新任务 |
| `task_redirect` | 申请变更任务目标 | 更新 Task Board 任务描述 |
| `structural_fix` | 项目结构性问题 | 执行任务1（项目优化） |

### EverAgent 处理流程

1. 扫描所有 commit message 中的 `needs-review` 标记
2. 按 `Review-Type` 分类处理
3. 处理完成后将任务标记为 `review-resolved`
4. 在下次调度时通知 Subagent

---

## §3 边界案例

### 案例 1：论文超出边界

**场景**：Subagent 领取了"Transformer (2017)"精读任务，但发现论文涉及 Attention Is All You Need 之外的技术。

**判断**：L2 — 论文内容超出防幻觉边界

**操作**：
```
Status: needs-review
Review-Type: boundary_extension
Detail: Transformer 论文包含 Multi-Head Attention、Positional Encoding 等组件，建议扩充边界到"注意力机制家族"
```

### 案例 2：发现高价值论文

**场景**：Subagent 在阅读参考资料时发现一篇高价值论文，但 Task Board 中没有。

**判断**：L2 — 识别高价值但未列入的任务

**操作**：
```
Status: needs-review
Review-Type: new_task_proposal
Detail: 发现 "FlashAttention (2022)" 与当前任务高度相关，建议新增 P1 任务
```

### 案例 3：任务目标无法完成

**场景**：Subagent 领取了"复现某实验"任务，但发现缺少必要数据。

**判断**：L2 — 任务描述与实际不符

**操作**：
```
Status: needs-review
Review-Type: task_redirect
Detail: 实验原始数据不可获取，建议变更为"理论分析"模式
```

### 案例 4：技术路线选择

**场景**：实现某算法有两种方式，Task Board 未指定。

**判断**：L1 — 执行细节属于 L1 范围

**操作**：自主选择，报告中说明理由

### 案例 5：修改其他项目文件

**场景**：Subagent 发现其他项目有错误，想修复。

**判断**：L3 — 跨项目操作禁止

**操作**：通知 EverAgent，由其转告对应 Subagent

---

## §4 决策优先级

当同时遇到多个 L2 决策时，按以下优先级处理：

1. **任务阻塞**（task_redirect）> 其他
2. **新任务建议**（new_task_proposal）> 边界扩充
3. **结构性问题**（structural_fix）在空闲时处理

---

## §5 快速参考卡

```
L1 可自主：执行细节、报告内容、格式、顺序
L2 须上报：边界外领域、高价值新任务、目标不符、结构问题
L3 禁止：全局配置、跨项目、删除历史、绕过防幻觉

上报格式：Status: needs-review + Review-Type
```
