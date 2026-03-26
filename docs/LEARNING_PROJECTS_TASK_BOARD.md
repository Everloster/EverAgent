# Five Learning Projects Task Board

> 目的：为其他 Agent 提供可直接接单的跨项目任务分发表
> 适用范围：`ai-learning` / `cs-learning` / `philosophy-learning` / `psychology-learning` / `biology-learning`
> 更新日期：2026-03-26

---

## 使用原则

1. 同一时间同一子项目只允许一个 Agent 写入。
2. 优先接“高价值、低歧义、能直接产出报告”的任务。
3. 写入前先读取对应项目的 `CONTEXT.md`，避免越过防幻觉边界。
4. 完成任务后同步更新对应项目的 `README.md` 与 `CONTEXT.md`。

---

## 项目进度概览

| 项目 | 当前状态 | 已有报告量 | 主要问题 | 建议优先级 |
|------|----------|------------|----------|------------|
| `ai-learning` | 成熟活跃 | 23 | 核心工程专题仍有缺口 | P1 |
| `cs-learning` | 成熟建设中 | 13 | 网络/协调服务/文件系统缺口明显 | P1 |
| `philosophy-learning` | 结构成型 | 7 | 20 世纪哲学与德国哲学仍偏薄 | P1 |
| `psychology-learning` | 早期成型 | 3 | 认知偏差与行为经济学主线未展开 | P2 |
| `biology-learning` | 初始化期 | 1 | 仍缺首批独立论文精读 | P2 |

---

## 推荐接单池

### P1：最适合马上开工

| 项目 | 建议任务 | 任务价值 | 适合的 Agent 类型 |
|------|----------|----------|------------------|
| `ai-learning` | 精读 `FlashAttention (2022)` | 补齐 LLM 工程链路关键缺口 | 熟悉 LLM/系统优化 |
| `cs-learning` | 精读 `Chubby` 或 `ZooKeeper/ZAB` | 补齐协调服务与一致性主线 | 熟悉分布式系统 |
| `philosophy-learning` | 精读 `Nagel (1974) What Is It Like to Be a Bat?` | 打开心灵哲学主线，与 AI/心理学交叉强 | 熟悉哲学文本分析 |

### P2：第二批推荐

| 项目 | 建议任务 | 任务价值 | 适合的 Agent 类型 |
|------|----------|----------|------------------|
| `psychology-learning` | 精读 `Kahneman & Tversky (1979)` | 从经典实验推进到行为经济学核心 | 熟悉心理学/行为科学 |
| `biology-learning` | 精读 `Roenneberg (2012) Social Jetlag and Obesity` | 把现有综合报告落到论文级分析 | 熟悉生命科学文献 |
| `ai-learning` | 精读 `Mistral 7B` 或 `DINO v2` | 分别补 LLM 开源脉络或视觉自监督后续 | 熟悉 AI 论文 |
| `cs-learning` | 精读 `A Fast File System for UNIX` | 把 UNIX 主线从哲学扩展到文件系统实现 | 熟悉 OS/文件系统 |

### P3：结构整理型任务

| 项目 | 建议任务 | 任务价值 |
|------|----------|----------|
| `psychology-learning` | 制作心理学流派思维导图 | 提升项目导航与教学价值 |
| `philosophy-learning` | 扩展“核心概念跨时代比较”之“自由/正义/存在” | 把项目从文本库推进为问题库 |
| `biology-learning` | 补齐 timeline / papers / books 索引质量 | 为后续 Agent 降低选题成本 |

---

## 并发安排建议

推荐最多同时开 3 个学习项目：

- Agent A：`ai-learning`
- Agent B：`cs-learning`
- Agent C：`philosophy-learning` 或 `psychology-learning`

`biology-learning` 更适合作为补位任务，在前 3 个项目有人推进后再启动。

---

## 不建议重复领取的任务

- `psychology-learning` 的 `Miller (1956)` 与 `Milgram (1963)` 已完成，不应再次领取。
- `ai-learning` 的 `AlexNet` 已完成，不应继续作为待办入口。
- `philosophy-learning` 的 `《美诺》`、`洞穴比喻`、`Gettier`、`笛卡尔《沉思录》` 已完成，不应重复开工。
- `cs-learning` 的 `UNIX` 与 `Kafka` 已完成，接单前先看 `CONTEXT.md`。

---

## 交付标准

每个 Agent 接任务时，至少完成以下 4 项：

1. 新增正式报告文件到对应 `reports/` 目录
2. 按 `docs/REPORT_METADATA.md` 补齐 frontmatter
3. 更新对应项目 `CONTEXT.md`
4. 如 README 中有状态追踪或待办列表，同步修正

---

## 建议接单顺序

1. `ai-learning` → `FlashAttention`
2. `cs-learning` → `Chubby` / `ZooKeeper`
3. `philosophy-learning` → `Nagel (1974)`
4. `psychology-learning` → `Prospect Theory`
5. `biology-learning` → `Social Jetlag and Obesity`

这套顺序的目标不是平均推进，而是优先补最能提升项目“知识主线完整度”的缺口。
