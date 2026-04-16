# Learning Projects Task Board

> 本文件为自动生成视图，由 `scripts/task_board_aggregator.py` 维护
> **请勿直接编辑**，编辑将覆盖
> 任务权威源：各项目的 `.project-task-state`，以及根目录的 `/.project-task-state`（global 任务）
> 更新日期：**2026-04-16**（T020-T026 基于 GitHub Trending 日/周/月实时数据重写）

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
| `ai-learning` | 🟢 | 37 | 19 | 34% |
| `cs-learning` | 🟢 | 22 | 4 | 15% |
| `philosophy-learning` | 🟡 | 10 | 2 | 17% |
| `psychology-learning` | 🟡 | 12 | 2 | 14% |
| `biology-learning` | 🟡 | 5 | 1 | 17% |

---

## 任务队列

### 🔥 开放任务池（P1/P2）— ai-learning 2026 Q1 Agent × Harness 专项
> 数据来源：GitHub Trending 日/周/月榜 2026-04-16 实时抓取，所有任务均有 GitHub 实证支撑

```yaml
# ── 主线一：Harness Engineering ───────────────────────────────────────────

- id: T020
  project: ai-learning
  type: knowledge_report
  target: "Agent Harness 三大设计流派：everything-claude-code x deer-flow x Archon"
  value: "月榜#1 affaan-m/everything-claude-code (81757月增) + bytedance/deer-flow (31460月增) + coleam00/Archon (4263周增,'first open-source harness builder'); performance vs long-horizon vs deterministic 三种哲学"
  priority: P1
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null

- id: T021
  project: ai-learning
  type: knowledge_report
  target: "Agent Skills 生态：从 Karpathy 的 CLAUDE.md 到可复用技能树"
  value: "日榜#1 forrestchang/andrej-karpathy-skills (9646今日+30919周); addyosmani/agent-skills (6693周) + mattpocock/skills (14248月) + obra/superpowers (70176月); Karpathy LLM编程哲学->CLAUDE.md 机制; Skills 作为 Harness 核心组件"
  priority: P1
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null

- id: T022
  project: ai-learning
  type: knowledge_report
  target: "Agent Memory 系统深度解析：claude-mem 的设计与上下文工程实践"
  value: "双榜实证 thedotmack/claude-mem (2305今日+10779周,58K stars); 捕获->压缩->注入三步机制; Memory 在 Harness 架构中的位置; mvanhorn/last30days-skill (18023月) 对比"
  priority: P1
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null

# ── 主线二：Agent 架构与进化 ──────────────────────────────────────────────

- id: T023
  project: ai-learning
  type: knowledge_report
  target: "自进化 Agent 架构：hermes-agent x GenericAgent 的技能树机制"
  value: "月/周双榜#1 NousResearch/hermes-agent (53110周+81412月,91K stars,'The agent that grows with you'); 对照 lsdefine/GenericAgent ('grows skill tree from 3.3K-line seed'); Self-improvement 实现与边界"
  priority: P1
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null

- id: T024
  project: ai-learning
  type: knowledge_report
  target: "Managed Agents Platform：multica 的 Agent-as-Teammate 范式解析"
  value: "周榜实证 multica-ai/multica (10864周,'Turn coding agents into real teammates'); Agent 团队管理产品化; Compound Skills 机制; vs LangGraph/CrewAI/AutoGen 定位差异"
  priority: P1
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null

- id: T025
  project: ai-learning
  type: knowledge_report
  target: "垂直 AI Agent 爆发：金融领域三大架构（TradingAgents x Kronos x ai-hedge-fund）"
  value: "三榜实证: TauricResearch/TradingAgents (18792月) + shiyu-coder/Kronos (6486周) + virattt/ai-hedge-fund (1058今日,55K stars); 垂直域 vs 通用 Agent 技术权衡; 金融时序数据与 LLM 融合路径"
  priority: P2
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null

- id: T026
  project: ai-learning
  type: knowledge_report
  target: "AI Coding Agent 终端架构：Scaffolding x Harness x Context 三层模型"
  value: "核心文献 arxiv 2603.05344; GitHub实证 obra/superpowers (2055今日+70176月); Grok Code Fast 6.7%->68.3% 靠 edit format; Harness决定性证据; 与 ToA 论技术互证; EverAgent 自身架构对照"
  priority: P2
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null

```

### 开放任务池（P3）— 其他子项目

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
- id: T016
  project: ai-learning
  type: knowledge_report
  target: "Megatron-LM 大规模语言模型训练系统深度解析"
  value: "工程类主线剩余缺口; 张量并行+流水线并行+数据并行 3D并行体系; CONTEXT.md 下一步推荐"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: NeuronAgent
  claimed_at: 2026-04-16T16:22:12+08:00
  started_at: 2026-04-16T16:22:15+08:00
  done_at: 2026-04-16T16:30:34+08:00

- id: T015
  project: cs-learning
  type: paper_analysis
  target: "Dijkstra Go To Statement Considered Harmful (1968)"
  value: "编程语言理论入口; 结构化编程革命宣言; CONTEXT.md 下一步推荐"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: ByteAgent
  claimed_at: 2026-04-16T16:22:12+08:00
  started_at: 2026-04-16T16:22:15+08:00
  done_at: 2026-04-16T16:25:41+08:00

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
