# Learning Projects Task Board

> 本文件为自动生成视图，由 `scripts/task_board_aggregator.py` 维护
> **请勿直接编辑**，编辑将覆盖
> 任务权威源：各项目的 `.project-task-state`，以及根目录的 `/.project-task-state`（global 任务）
> 更新日期：**2026-04-16**

---

## 使用原则

1. 同一时间同一子项目只允许一个 Agent 写入。
2. 领取前先运行 `python3 scripts/execution_validator.py --mode=input --task-id=TXXX --project=<project>`。
3. 输入校验通过后立即获取项目锁：`python3 scripts/project_lock.py acquire --project=<project> --task-id=TXXX --agent=<AgentName>`。
4. 完成任务后先运行输出校验，再提交、推送，最后释放项目锁。

---

## 项目进度概览

| 项目 | 当前状态 | 论文/文本精读 | 知识/概念报告 | 知识报告比 |
|------|----------|:---:|:---:|:---:|
| `ai-learning` | 🟢 | 37 | 18 | 33% |
| `cs-learning` | 🟢 | 21 | 4 | 16% |
| `philosophy-learning` | 🟡 | 10 | 2 | 17% |
| `psychology-learning` | 🟡 | 12 | 2 | 14% |
| `biology-learning` | 🟡 | 5 | 1 | 17% |

---

## 任务队列

### 开放任务池（P3）

```yaml
- id: T011
  project: philosophy-learning
  type: knowledge_report
  target: "扩展知识跨时代比较至自由意志专题"
  value: "现有比较聚焦知识论, 自由意志是另一高张力主线"
  priority: P3
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null

- id: T010
  project: psychology-learning
  type: maintenance
  target: "更新心理学关键人物图谱"
  value: "加入 Bandura/Seligman/Harlow 等新精读作者; 图谱严重落后内容"
  priority: P3
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null

```

### 最近完成（自动生成）

```yaml
- id: T013
  project: ai-learning
  type: paper_analysis
  target: "EVA-02 (2023)"
  value: "工程类论文主线缺口；大规模视觉模型与训练并行框架"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: claude-sonnet-4-6
  claimed_at: 2026-04-16T10:00:00+08:00
  started_at: 2026-04-16T10:05:00+08:00
  done_at: 2026-04-16T11:30:00+08:00

- id: T014
  project: cs-learning
  type: paper_analysis
  target: "BGP (RFC 4271, 2006)"
  value: "网络方向深化（BGP是互联网路由基础）"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: claude-sonnet-4-6
  claimed_at: 2026-04-16T10:00:00+08:00
  started_at: 2026-04-16T10:05:00+08:00
  done_at: 2026-04-16T11:30:00+08:00

- id: T006
  project: ai-learning
  type: knowledge_report
  target: "MoE (混合专家) 深度解析"
  value: "GPT-4/Mixtral 架构基础; 已有精读(#21)可支撑深度报告"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: claude-sonnet-4-6
  claimed_at: 2026-04-06T00:00:00+08:00
  started_at: 2026-04-06T00:00:00+08:00
  done_at: 2026-04-06T00:00:00+08:00

- id: T007
  project: philosophy-learning
  type: text_analysis
  target: "罗尔斯《正义论》第一章"
  value: "当代政治哲学主线入口"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: claude-sonnet-4-6
  claimed_at: 2026-04-06T00:00:00+08:00
  started_at: 2026-04-06T00:00:00+08:00
  done_at: 2026-04-06T00:00:00+08:00

- id: T009
  project: biology-learning
  type: paper_analysis
  target: "Walker et al. (2017) Why We Sleep 核心论据综述"
  value: "睡眠科学方向高影响力节点"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: claude-sonnet-4-6
  claimed_at: 2026-04-06T00:00:00+08:00
  started_at: 2026-04-06T00:00:00+08:00
  done_at: 2026-04-06T00:00:00+08:00

- id: T001
  project: ai-learning
  type: paper_analysis
  target: "VideoMAE (2022) 或 EVA-02 (2023)"
  value: "视觉自监督序列: MAE -> VideoMAE; 与 DINOv2/MAE 形成闭环"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: MiniMax-M2.7
  claimed_at: 2026-04-04T10:00:00+08:00
  started_at: 2026-04-04T10:30:00+08:00
  done_at: 2026-04-05T15:47:00+08:00

- id: T002
  project: ai-learning
  type: paper_analysis
  target: "MegaScale (2024)"
  value: "工程类论文主线缺口; 大规模训练系统实践"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: MiniMax-M2.7
  claimed_at: 2026-04-04T10:00:00+08:00
  started_at: 2026-04-04T10:30:00+08:00
  done_at: 2026-04-05T15:47:00+08:00

- id: T003
  project: cs-learning
  type: paper_analysis
  target: "DNS (1987, RFC 1034/1035)"
  value: "网络方向第一篇; 与 TCP/IP 自然衔接"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: MiniMax-M2.7
  claimed_at: 2026-04-05T10:00:00+08:00
  started_at: 2026-04-05T10:30:00+08:00
  done_at: 2026-04-05T15:47:00+08:00

- id: T004
  project: cs-learning
  type: knowledge_report
  target: "分布式系统知识图谱"
  value: "19篇精读可归纳 Storage/Consensus/Coordination/Messaging 四主线; 知识报告比仅5%"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: MiniMax-M2.7
  claimed_at: 2026-04-05T10:00:00+08:00
  started_at: 2026-04-05T10:30:00+08:00
  done_at: 2026-04-05T15:47:00+08:00

- id: T005
  project: philosophy-learning
  type: text_analysis
  target: "黑格尔《精神现象学》导论"
  value: "补齐德国唯心论主线; 与康德/亚里士多德形成三角"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: MiniMax-M2.7
  claimed_at: 2026-04-05T10:00:00+08:00
  started_at: 2026-04-05T10:30:00+08:00
  done_at: 2026-04-05T15:47:00+08:00

```

### Global Tasks

```yaml
- id: T012
  project: global
  type: maintenance
  target: "github-trending-analyzer 周报自动化"
  value: "目前靠手动触发, 可用 schedule 技能自动化"
  priority: P3
  required_capability: full_admin
  status: open
  claimed_by: null
  claimed_at: null

```
