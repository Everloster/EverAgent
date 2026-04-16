# Five Learning Projects Task Board

> 目的：为 Agent 提供可直接领取的跨项目结构化任务队列
> 适用范围：`ai-learning` / `cs-learning` / `philosophy-learning` / `psychology-learning` / `biology-learning`
> **本文件为只读视图**，由 `scripts/task_board_aggregator.py` 自动生成
> 如需编辑任务，请编辑对应项目的 `.project-task-state` 文件
> 更新日期：**2026-04-16**（v6: 新增T013/T014任务，同步ai/cs知识报告数量）

---

## 使用原则

1. 同一时间同一子项目只允许一个 Agent 写入。
2. 优先接"高价值、低歧义、能直接产出报告"的任务。
3. 写入前先读取对应项目的 `CONTEXT.md`，避免越过防幻觉边界。
4. 完成任务后同步更新对应项目的 `CONTEXT.md`（不只是本文件）。

---

## 项目进度概览

| 项目 | 当前状态 | 论文/文本精读 | 知识/概念报告 | 知识报告比 | 主要缺口 |
|------|----------|:---:|:---:|:---:|----------|
| `ai-learning` | 🟢 高度活跃 | 35 | 16 | 46% | 工程类（EVA-02、Megatron-LM） |
| `cs-learning` | 🟢 成熟建设中 | 20 | 3 | 15% | 网络（BGP）、编译器/DB理论 |
| `philosophy-learning` | 🟡 结构成型 | 8 (7文本+1论文) | 2 | 25% | 德国唯心论、分析哲学 |
| `psychology-learning` | 🟢 快速扩张 | 12 | 1 | 8% | 发展/临床心理学 |
| `biology-learning` | 🟡 初步成型 | 4 | 1 | 25% | 睡眠神经科学 |

---

## 任务队列

### 领取协议

```
1. Agent 读取本文件, 从 status: open 的任务中选择匹配自身能力的任务
2. 将所选任务 status 改为 claimed, 填写 claimed_by 和 claimed_at
3. 执行任务, 完成后将 status 改为 done, 填写 done_at
4. 同步更新: CONTEXT.md + 已完成列表(本文件底部)
5. 冲突处理: 两个 Agent 同时 claim 同一任务, 以先 push 者为准
```

### 开放任务池

```yaml
# P1: 高价值, 可直接开工
- id: T001
  project: ai-learning
  type: paper_analysis
  target: "VideoMAE (2022) 或 EVA-02 (2023)"
  value: "视觉自监督序列: MAE -> VideoMAE; 与 DINOv2/MAE 形成闭环"
  priority: P1
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
  status: done
  claimed_by: MiniMax-M2.7
  claimed_at: 2026-04-05T10:00:00+08:00
  started_at: 2026-04-05T10:30:00+08:00
  done_at: 2026-04-05T15:47:00+08:00

# P2: 第二批推荐
- id: T006
  project: ai-learning
  type: knowledge_report
  target: "MoE (混合专家) 深度解析"
  value: "GPT-4/Mixtral 架构基础; 已有精读(#21)可支撑深度报告"
  priority: P2
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
  status: done
  claimed_by: claude-sonnet-4-6
  claimed_at: 2026-04-06T00:00:00+08:00
  started_at: 2026-04-06T00:00:00+08:00
  done_at: 2026-04-06T00:00:00+08:00

- id: T008
  project: psychology-learning
  type: knowledge_report
  target: "认知偏差全景图"
  value: "整合 Kahneman/Tversky 系列报告; 提升导航价值"
  priority: P2
  status: done
  claimed_by: MiniMax-M2.7
  claimed_at: 2026-04-05T10:00:00+08:00
  started_at: 2026-04-05T10:30:00+08:00
  done_at: 2026-04-05T15:47:00+08:00

- id: T009
  project: biology-learning
  type: paper_analysis
  target: "Walker et al. (2017) Why We Sleep 核心论据综述"
  value: "睡眠科学方向高影响力节点"
  priority: P2
  status: done
  claimed_by: claude-sonnet-4-6
  claimed_at: 2026-04-06T00:00:00+08:00
  started_at: 2026-04-06T00:00:00+08:00
  done_at: 2026-04-06T00:00:00+08:00

# 新增任务（2026-04-16）
- id: T013
  project: ai-learning
  type: paper_analysis
  target: "EVA-02 (2023) 或 Megatron-LM (2021)"
  value: "工程类论文主线缺口；大规模视觉模型与训练并行框架"
  priority: P1
  status: open
  claimed_by: null
  claimed_at: null

- id: T014
  project: cs-learning
  type: paper_analysis
  target: "BGP (RFC 4271, 2006) 或 Dijkstra Go To (1968)"
  value: "网络方向深化（BGP是互联网路由基础）或编程语言理论起点"
  priority: P2
  status: open
  claimed_by: null
  claimed_at: null

# P3: 结构整理型
- id: T010
  project: psychology-learning
  type: maintenance
  target: "更新心理学关键人物图谱"
  value: "加入 Bandura/Seligman/Harlow 等新精读作者; 图谱严重落后内容"
  priority: P3
  status: open
  claimed_by: null
  claimed_at: null

- id: T011
  project: philosophy-learning
  type: knowledge_report
  target: "扩展知识跨时代比较至自由意志专题"
  value: "现有比较聚焦知识论, 自由意志是另一高张力主线"
  priority: P3
  status: open
  claimed_by: null
  claimed_at: null

- id: T012
  project: global
  type: maintenance
  target: "github-trending-analyzer 周报自动化"
  value: "目前靠手动触发, 可用 schedule 技能自动化"
  priority: P3
  status: open
  claimed_by: null
  claimed_at: null
```

---

## 并发安排建议

- **推荐最多同时开 3 个学习项目**, 4 个以上会有 CONTEXT 竞写风险。
- 推荐组合（当前时间点）：
  - Agent A：`philosophy-learning`（T007 罗尔斯《正义论》或 T011 自由意志专题）
  - Agent B：`ai-learning`（T006 MoE 深度解析）
  - Agent C：`biology-learning`（T009 Walker睡眠研究）

---

## 已完成, 不应重复领取

### ai-learning (35篇精读 + 16篇知识报告)
Transformer、BERT、GPT-3、InstructGPT、ResNet、GAN、DDPM、AlexNet、Scaling Laws、Chain-of-Thought、LoRA、ViT、CLIP、LLaMA、Swin Transformer、MAE、DINOv2、FlashAttention、LLaMA-2、Mistral 7B、Word2Vec、Tulu3、MoE #21 (2017)、ZeRO #25 (2019)、VideoMAE #36 (2022)、MegaScale #31 (2024)、GPT-1 (2018)、GPT-2 (2019)、Bitter Lesson (2019)、Stable Diffusion/LDM (2021)、DiT (2022)、ReAct (2022)、LAION-5B (2022)、RefinedWeb (2023)、Google Translate/GNMT (2016)、DeepVideo (2014)；知识报告：Self-Attention、RLHF、Scaling Laws、LoRA、AI关键人物图谱、DINOv2深度解析、KV Cache、MoE混合专家深度解析、RAG深度解析、Agent/ReAct/ToolUse深度解析、Test-Time Compute深度解析、In-Context Learning深度解析、ToA/CLI原生论、双向驯化与多Agent涌现、EverAgent ToA原型解剖、奶头乐ChatBot战略价值、开源vs闭源ToA博弈、生成模型演化全景GAN→DDPM→LDM→DiT (2026-04-16)

### cs-learning (20篇精读 + 3篇知识报告)
Turing (1950)、Shannon (1948)、MapReduce (2004)、Bigtable (2006)、Lamport Clocks (1978)、GFS (2003)、Dynamo (2007)、Raft (2014)、Spanner (2012)、Paxos (2001)、Kafka (2011)、UNIX (1974)、ZooKeeper (2010)、FFS (1984)、Byzantine Generals (1982)、CSP (1978)、TCP/IP (1974)、Chubby (2006)、Chord (2001)、DNS RFC 1034/1035 (1987)；知识报告：CS关键人物图谱、分布式系统知识图谱、操作系统内核设计深度解析 (2026-04-16)

### philosophy-learning (9篇文本分析 + 1篇论文分析 + 2篇概念报告)
柏拉图《理想国》洞穴比喻、柏拉图《美诺》、笛卡尔《沉思录》、Gettier (1963)、康德《道德形而上学基础》、亚里士多德《尼各马可伦理学》、Nagel (1974) What Is It Like to Be a Bat?、黑格尔《精神现象学》导论 (1807)、罗尔斯《正义论》第一章 (1971)；概念报告：哲学关键人物图谱、知识跨时代比较

### psychology-learning (12篇精读 + 2篇知识报告)
Miller (1956)、Milgram (1963)、Festinger & Carlsmith (1959)、Kahneman & Tversky (1979) 前景理论、Seligman & Maier (1967) 习得性无助、Darley & Latane (1968) 旁观者效应、Asch (1951) 从众实验、Zimbardo (1971) 斯坦福监狱实验、Rosenhan (1973)、Tversky & Kahneman (1974) 启发式与偏差、Bandura (1961) Bobo 娃娃实验、Harlow (1958) 恒河猴实验；知识报告：心理学关键人物图谱、认知偏差全景图

### biology-learning (5篇精读 + 1篇概念报告)
Social Jetlag and Obesity (2012)、Sleep GH 1988、GH Sleep Physiology 1996、Social Jetlag 代谢综合征 (2017)、Walker Why We Sleep 核心论据综述 (2017)；概念报告：晚型人作息与力量训练

---

## 交付标准

每个 Agent 接任务时, 至少完成以下 5 项:

1. 新增正式报告文件到对应 `reports/` 目录
2. 按 `docs/REPORT_METADATA.md` 补齐 frontmatter
3. 文件命名遵循 `{序号}_{简称}_{年份}.md`（无中文后缀）
4. 更新对应项目 `CONTEXT.md`（已有报告 + 防幻觉边界两处都要更新）
5. 更新本文件: 任务 status -> done + 已完成列表追加
