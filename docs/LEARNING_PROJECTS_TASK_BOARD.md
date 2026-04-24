# Learning Projects Task Board

> 本文件为自动生成视图，由 `scripts/task_board_aggregator.py` 维护
> **请勿直接编辑**，编辑将覆盖
> 任务权威源：各项目的 `.project-task-state`，以及根目录的 `/.project-task-state`（global 任务）
> 更新日期：**2026-04-24**

---

## 使用原则

1. 同一时间同一子项目只允许一个 Agent 写入。
2. 领取前先运行 `python3 scripts/execution_validator.py --mode=input --task-id=TXXX --project=<project>`。
3. 输入校验通过后立即获取项目锁：`python3 scripts/project_lock.py acquire --project=<project> --task-id=TXXX --agent=<AgentName>`。
4. 完成任务后先运行输出校验，再提交、推送，最后释放项目锁。
5. `claimed` / `in_progress` / `help_needed` 超过 72h 的任务会显示在“超时任务”区块，建议改为 `abandoned` 或人工 `reopen`。

---

## 项目进度概览

| 项目 | 当前状态 | 论文/文本精读 | 知识/概念报告 | 知识报告比 |
|------|----------|:---:|:---:|:---:|
| `ai-learning` | 🟢 | 37 | 28 | 43% |
| `ai-practice` | 🔴 | 0 | 0 | 0% |
| `biology-learning` | 🟡 | 9 | 3 | 25% |
| `cs-learning` | 🟢 | 24 | 5 | 17% |
| `philosophy-learning` | 🟡 | 12 | 3 | 20% |
| `psychology-learning` | 🟡 | 12 | 3 | 20% |

---

## 任务队列

### 开放任务池（P1）

```yaml
- id: T043
  project: biology-learning
  type: maintenance
  target: "修正 CONTEXT 防幻觉边界与导航状态"
  value: "biology-learning 已新增 P02/P03/P04/P17/P26 等报告，但 CONTEXT 边界仍称除 P01/P08/P09/P25 外其余未独立精读；需要修正边界、下一步推荐与导航描述，保持与已有报告一致"
  priority: P1
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null
  context_links:
    - biology-learning/AGENTS.md
    - biology-learning/CONTEXT.md
    - biology-learning/reports/paper_analyses
    - biology-learning/reports/concept_reports

```

### 开放任务池（P2）

```yaml
- id: T045
  project: ai-practice
  type: maintenance
  target: "同步 exp_005 后的 ai-practice 上下文与 wiki 导航"
  value: "ai-practice 已有 exp_005 MoE Transformer 教学笔记；检查 README/CONTEXT/wiki/index/log 是否一致，补齐导航和边界说明，不新增实验"
  priority: P2
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null
  context_links:
    - ai-practice/AGENTS.md
    - ai-practice/CONTEXT.md
    - ai-practice/README.md
    - ai-practice/wiki/index.md
    - ai-practice/experiments/exp_005_moe_transformer.md

- id: T044
  project: philosophy-learning
  type: maintenance
  target: "清理 CONTEXT 防幻觉边界重复条目并同步最新覆盖"
  value: "philosophy-learning CONTEXT 的防幻觉边界存在重复条目，且最新 Gettier/Russell/Singer 等完成情况需要让边界描述更一致；只做元信息维护，不新增报告"
  priority: P2
  required_capability: task_executor
  status: open
  claimed_by: null
  claimed_at: null
  context_links:
    - philosophy-learning/AGENTS.md
    - philosophy-learning/CONTEXT.md
    - philosophy-learning/reports/text_analyses
    - philosophy-learning/wiki/index.md

```

### 最近完成（自动生成）

```yaml
- id: T037
  project: biology-learning
  type: paper_analysis
  target: "Roenneberg & Merrow (2022) The circadian system, sleep, and the health/disease balance"
  value: "J Sleep Research 综述; 昼夜节律系统、睡眠与健康/疾病平衡的整合视角"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: BioAgent
  claimed_at: 2026-04-24T00:00:00+08:00
  started_at: 2026-04-24T00:00:00+08:00
  done_at: 2026-04-24T00:00:00+08:00

- id: T038
  project: biology-learning
  type: paper_analysis
  target: "Hayes et al. (2013) Circadian Rhythms in Exercise Performance: Implications for Hormonal and Muscular Adaptation"
  value: "运动表现昼夜节律; 激素与肌肉适应的时间生物学机制"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: BioAgent
  claimed_at: 2026-04-24T00:00:00+08:00
  started_at: 2026-04-24T00:00:00+08:00
  done_at: 2026-04-24T00:00:00+08:00

- id: T039
  project: biology-learning
  type: concept_report
  target: "运动时间生物学：整合 Hayes/Ezagouri/Gupta 研究的个体化训练时间窗"
  value: "整合 P17 Hayes(2013) + P20 Ezagouri(2023) + P21 Gupta(2025); 最佳运动时间的个体化决策框架"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: BioAgent
  claimed_at: 2026-04-24T00:00:00+08:00
  started_at: 2026-04-24T00:00:00+08:00
  done_at: 2026-04-24T00:00:00+08:00

- id: T040
  project: philosophy-learning
  type: text_analysis
  target: "Gettier (1963) Is Justified True Belief Knowledge?"
  value: "3页震动20世纪知识论; JTB定义的两个反例; 知识论转向"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: SocratesAgent
  claimed_at: 2026-04-24T00:00:00+08:00
  started_at: 2026-04-24T00:00:00+08:00
  done_at: 2026-04-24T00:00:00+08:00

- id: T041
  project: philosophy-learning
  type: text_analysis
  target: "Russell (1905) On Denoting"
  value: "摹状词理论; 法国现任国王是秃子难题; 逻辑分析哲学威力"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: SocratesAgent
  claimed_at: 2026-04-24T00:00:00+08:00
  started_at: 2026-04-24T00:00:00+08:00
  done_at: 2026-04-24T00:00:00+08:00

- id: T042
  project: philosophy-learning
  type: text_analysis
  target: "Singer (1972) Famine, Affluence, and Morality"
  value: "功利主义义务论证; 全球贫困的道德义务; 有效利他主义理论基础"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: SocratesAgent
  claimed_at: 2026-04-24T00:00:00+08:00
  started_at: 2026-04-24T00:00:00+08:00
  done_at: 2026-04-24T00:00:00+08:00

- id: T026
  project: ai-learning
  type: knowledge_report
  target: "AI Coding Agent 终端架构：Scaffolding x Harness x Context 三层模型"
  value: "核心文献: arxiv 2603.05344 (Building AI Coding Agents for the Terminal); GitHub 实证: obra/superpowers (2055今日+70176月增,'agentic skills framework'); Grok Code Fast 靠 edit format 从 6.7%->68.3%; Harness 决定性证据; 与 ToA 论技术互证; 与 EverAgent 自身架构对照"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: NeuronAgent
  claimed_at: 2026-04-23T10:00:00+08:00
  started_at: 2026-04-23T11:30:00+08:00
  done_at: 2026-04-23T12:00:00+08:00

- id: T025
  project: ai-learning
  type: knowledge_report
  target: "垂直 AI Agent 爆发：金融领域三大架构解析（TradingAgents x Kronos x ai-hedge-fund）"
  value: "GitHub 三榜实证: TauricResearch/TradingAgents (18792月增,多Agent金融交易) + shiyu-coder/Kronos (6486周+7042月,'Foundation Model for Financial Markets') + virattt/ai-hedge-fund (1058日+4314周,55K stars); 垂直域 Agent 技术架构 vs 通用 Agent 差异; 金融时序数据与 LLM 融合的技术路径"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: NeuronAgent
  claimed_at: 2026-04-23T10:00:00+08:00
  started_at: 2026-04-23T10:05:00+08:00
  done_at: 2026-04-23T11:30:00+08:00

- id: T024
  project: ai-learning
  type: knowledge_report
  target: "Managed Agents Platform：multica 的 Agent-as-Teammate 范式解析"
  value: "GitHub 周榜实证: multica-ai/multica (10864周增,'Turn coding agents into real teammates — assign tasks, track progress, compound skills'); Agent 团队管理产品化路径; 与 LangGraph/CrewAI/AutoGen 的定位差异; Compound Skills 机制"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: NeuronAgent
  claimed_at: 2026-04-23T10:00:00+08:00
  started_at: 2026-04-23T10:35:00+08:00
  done_at: 2026-04-23T10:55:00+08:00

- id: T023
  project: ai-learning
  type: knowledge_report
  target: "自进化 Agent 架构：hermes-agent x GenericAgent 的技能树机制"
  value: "GitHub 月/周双榜#1实证: NousResearch/hermes-agent (53110周增+81412月增,91K总stars,'The agent that grows with you'); 对照: lsdefine/GenericAgent ('Self-evolving agent: grows skill tree from 3.3K-line seed'); Self-improvement 技术实现路径; 自进化的可信度与边界分析"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: NeuronAgent
  claimed_at: 2026-04-23T10:00:00+08:00
  started_at: 2026-04-23T10:05:00+08:00
  done_at: 2026-04-23T10:30:00+08:00

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
