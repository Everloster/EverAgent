# Five Learning Projects Task Board

> 目的：为其他 Agent 提供可直接接单的跨项目任务分发表
> 适用范围：`ai-learning` / `cs-learning` / `philosophy-learning` / `psychology-learning` / `biology-learning`
> 更新日期：**2026-03-30**（项目优化任务1，由 Claude Sonnet 4.6 全量重写）

---

## 使用原则

1. 同一时间同一子项目只允许一个 Agent 写入。
2. 优先接"高价值、低歧义、能直接产出报告"的任务。
3. 写入前先读取对应项目的 `CONTEXT.md`，避免越过防幻觉边界。
4. 完成任务后同步更新对应项目的 `CONTEXT.md`（不只是本文件）。

---

## 项目进度概览（截至 2026-03-30）

| 项目 | 当前状态 | 论文/文本精读 | 知识/概念报告 | 主要缺口 | 建议优先级 |
|------|----------|:---:|:---:|----------|:---:|
| `ai-learning` | 🟢 高度活跃 | 24 篇 | 7 篇 | 分布式训练（ZeRO）、视频理解（VideoMAE） | P1 |
| `cs-learning` | 🟢 成熟建设中 | 17 篇 | 1 篇 | 网络（DNS） | P1 |
| `philosophy-learning` | 🟡 结构成型 | 7 篇文本分析 + 1 篇论文分析 | 2 篇 | 黑格尔、20 世纪分析哲学（现象学、语言哲学） | P1 |
| `psychology-learning` | 🟢 快速扩张 | 10 篇 | 1 篇 | 发展心理学、临床心理学，人物图谱亟需更新 | P2 |
| `biology-learning` | 🟡 初步成型 | 4 篇 | 1 篇 | 睡眠神经科学、昼夜节律分子机制、缺 roadmap | P2 |

> ⚠️ 注意：上述"已有报告量"仅统计已录入 CONTEXT.md 的报告；如有报告文件未录入，请先完成 CONTEXT.md 更新再接任务。

---

## 推荐接单池

### P1：最适合马上开工

| 项目 | 建议任务 | 任务价值 | 适合的 Agent 类型 |
|------|----------|----------|------------------|
| `ai-learning` | 精读 `ZeRO (2019)` | 分布式训练主线最大缺口；与 FlashAttention、Scaling Laws 形成 LLM 训练完整闭环 | 熟悉分布式训练 |
| `ai-learning` | 精读 `VideoMAE (2022)` 或 `EVA-02 (2023)` | 视觉自监督方向（MAE → VideoMAE）后续；与已有 DINOv2、MAE 形成序列 | 熟悉视觉 AI |
| `cs-learning` | 精读 `Chubby (2006)` | 分布式协调服务主线缺口；Paxos → Chubby → ZooKeeper 链路目前断在中间 | 熟悉分布式系统 |
| `philosophy-learning` | 精读 `Nagel (1974) What Is It Like to Be a Bat?` | 心灵哲学主线入口；与 AI 意识、人格问题高度交叉 | 熟悉哲学文本分析 |

### P2：第二批推荐

| 项目 | 建议任务 | 任务价值 | 适合的 Agent 类型 |
|------|----------|----------|------------------|
| `ai-learning` | 知识报告：`MoE (混合专家)` 深度解析 | GPT-4/Mixtral 架构基础；ai-learning 工程模块缺口 | 熟悉 LLM 架构 |
| `cs-learning` | 精读 `DNS (1987, RFC 1034/1035)` | 网络方向第一篇；与 TCP/IP 自然衔接 | 熟悉网络协议 |
| `philosophy-learning` | 精读 `黑格尔《精神现象学》导论` 或 `罗尔斯《正义论》第一章` | 补齐德国唯心论 or 当代政治哲学主线 | 熟悉哲学文本 |
| `psychology-learning` | 制作"认知偏差全景图"知识报告 | 整合已有的 Kahneman/Tversky 系列报告；提升项目导航价值 | 熟悉认知心理学 |
| `biology-learning` | 创建 `roadmap/` 目录 + 撰写学习路径 | biology 是唯一缺 roadmap 的子项目；结构完整性补缺 | 任意 Agent |
| `biology-learning` | 精读 `Walker et al. (2017) Why We Sleep 核心论据综述` | 把"睡眠科学"方向的论文精读链跑通第一个高影响力节点 | 熟悉睡眠/神经科学 |

### P3：结构整理型任务

| 项目 | 建议任务 | 任务价值 |
|------|----------|----------|
| `psychology-learning` | 更新"心理学关键人物图谱"（加入 Bandura、Seligman 等新精读的作者） | 报告增加了 7 篇后，人物图谱已严重落后于内容 |
| `ai-learning` | 更新 `roadmap/Learning_Roadmap.md` Phase 完成度 | Phase 2/3 大量论文已完成，但进度条仍显示 0% |
| `cs-learning` | 新增"分布式系统知识图谱"知识报告 | 16 篇论文已可归纳出 Storage/Consensus/Coordination/Messaging 四主线 |
| `philosophy-learning` | 扩展"知识跨时代比较"至"自由意志"专题 | 现有跨时代比较聚焦知识论，自由意志是另一个高张力主线 |
| `全局` | 为 github-trending-analyzer 添加周报自动触发 schedule | 目前 trending 分析靠手动触发，可用 schedule 技能自动化 |

---

## 并发安排建议

- **推荐最多同时开 3 个学习项目**，4 个以上会有 CONTEXT 竞写风险。
- 推荐组合（当前时间点）：
  - Agent A：`ai-learning`（ZeRO 或 VideoMAE）
  - Agent B：`cs-learning`（Chubby）
  - Agent C：`philosophy-learning`（Nagel） 或 `biology-learning`（补 roadmap）

---

## 已完成，不应重复领取

### ai-learning
Transformer、BERT、GPT-3、InstructGPT、ResNet、GAN、DDPM、AlexNet、Scaling Laws、Chain-of-Thought、LoRA、ViT、CLIP、LLaMA、Swin Transformer、MAE、DINOv2、FlashAttention、LLaMA-2、Mistral 7B、Word2Vec、Tulu3、MoE (混合专家) #21 (2017)；知识报告：Self-Attention、RLHF、Scaling Laws、LoRA、AI关键人物图谱、DINOv2深度解析、KV Cache

### cs-learning
Turing (1950)、Shannon (1948)、MapReduce (2004)、Bigtable (2006)、Lamport Clocks (1978)、GFS (2003)、Dynamo (2007)、Raft (2014)、Spanner (2012)、Paxos (2001)、Kafka (2011)、UNIX (1974)、ZooKeeper (2010)、FFS (1984)、Byzantine Generals (1982)、CSP (1978)、TCP/IP (1974)、Chubby (2006)

### philosophy-learning
柏拉图《理想国》洞穴比喻、柏拉图《美诺》、笛卡尔《沉思录》、Gettier (1963)、康德《道德形而上学基础》、亚里士多德《尼各马可伦理学》、Nagel (1974) What Is It Like to Be a Bat?；概念报告：哲学关键人物图谱、知识跨时代比较

### psychology-learning
Miller (1956)、Milgram (1963)、Festinger & Carlsmith (1959)、Kahneman & Tversky (1979) 前景理论、Seligman & Maier (1967) 习得性无助、Darley & Latané (1968) 旁观者效应、Asch (1951) 从众实验、Zimbardo (1971) 斯坦福监狱实验、Rosenhan (1973)、Tversky & Kahneman (1974) 启发式与偏差、Bandura (1961) Bobo 娃娃实验

### biology-learning
Social Jetlag and Obesity (2012)、Sleep GH 1988、GH Sleep Physiology 1996、Social Jetlag 代谢综合征 (2017)；概念报告：晚型人作息与力量训练

---

## 交付标准

每个 Agent 接任务时，至少完成以下 4 项：

1. 新增正式报告文件到对应 `reports/` 目录
2. 按 `docs/REPORT_METADATA.md` 补齐 frontmatter
3. 更新对应项目 `CONTEXT.md`（已有报告 + 防幻觉边界两处都要更新）
4. 如果任务完成后导致本 Task Board 的"已完成"列表需要更新，同步更新本文件
