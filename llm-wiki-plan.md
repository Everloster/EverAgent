# EverAgent × LLM Wiki 重构计划

> 基于 Karpathy《LLM Wiki》的思路，对 EverAgent 进行架构重构
> 作者：Claude Sonnet 4.6 · 日期：2026-04-06

---

## 一、诊断：EverAgent 现在是什么？

EverAgent 目前本质上是一个**报告生成系统**，而不是 Karpathy 所描述的 **persistent wiki**。

### 1.1 当前架构

```
raw sources (papers/)
    ↓ [一次性消费]
reports/ (paper_analyses + knowledge_reports)
    ↓ [静态产出]
knowledge/ (INDEX.md + 少量主题文件)
```

每次摄入一篇论文，产出一个独立的分析报告，然后结束。报告是**终点**，不是**起点**。

### 1.2 与 Karpathy 模式的核心差距

| 维度 | 当前状态 | Karpathy 模式 |
|------|---------|--------------|
| **知识积累方式** | 报告并排放置，不互相增强 | 每次摄入都更新整个 wiki |
| **层次结构** | Raw → Reports（两层） | Raw → Wiki → Schema（三层） |
| **跨领域连接** | 零（五个子项目完全隔离） | 任意概念跨域链接 |
| **摄入的影响范围** | 1 篇论文 → 1 个报告 | 1 篇论文 → 更新 10-15 个 wiki 页面 |
| **好的问答去哪里** | 消失在聊天记录中 | 归档回 wiki，持续沉淀 |
| **LOG** | 无（只有 git log） | append-only log.md，可 grep |
| **Lint 操作** | 无 | 定期健康检查（矛盾、孤岛、过时） |
| **知识粒度** | 大块报告（100-300 行）| 原子页面（20-50 行）+ 聚合页面 |

### 1.3 已有的好基础

不是推倒重来。EverAgent 有几个值得保留的资产：

- **90 篇高质量报告**：有严格的 7 步分析框架，内容密度高
- **knowledge/ 目录框架**：INDEX.md + 主题文件的雏形已存在
- **AGENTS.md 自包含协议**：每个子项目的 Schema 设计成熟
- **git 版本管理**：天然支持 wiki 的版本历史
- **Obsidian 可直接使用**：仓库本身就是 markdown 文件集合，可立即打开

---

## 二、目标架构

### 2.1 三层结构（对齐 Karpathy）

```
Layer 1: Raw Sources（不可变）
├── {project}/papers/          ← 原始 PDF（已有）
└── {project}/raw/             ← 新增：文章剪报、笔记、外部素材

Layer 2: Wiki（LLM 维护，持续生长）
└── {project}/wiki/            ← 核心变化：替代现有 knowledge/
    ├── index.md               ← 内容目录（每次摄入更新）
    ├── log.md                 ← 时序操作日志（append-only）
    ├── overview.md            ← 领域全局综述（定期更新）
    ├── entities/              ← 人物/机构/系统页面
    │   ├── hinton_geoffrey.md
    │   ├── openai.md
    │   └── transformer_arch.md
    ├── concepts/              ← 核心概念页面
    │   ├── attention_mechanism.md
    │   ├── scaling_laws.md
    │   └── moe_architecture.md
    └── syntheses/             ← 合成分析（好的问答归档在此）
        ├── moe_vs_dense_comparison.md
        └── timeline_llm_2017_2026.md

Layer 3: Schema（人 + LLM 共同维护）
├── {project}/AGENTS.md        ← 已有，需补充 wiki 操作规范
└── CLAUDE.md                  ← 已有，需补充 wiki 操作规范
```

### 2.2 现有 reports/ 的定位

reports/ **保留但降级**为"源材料层"的一部分：

```
reports/ ← 摄入的原始分析（只增不改）
wiki/    ← 知识的综合表示（持续进化）
```

每篇报告精读完毕后，其知识应**渗透到 wiki 的多个页面**，而不是只躺在 reports/ 里。

---

## 三、三种操作的重新定义

### 3.1 Ingest（摄入）

**现状**：读论文 → 写一个 paper_analysis 报告 → 结束

**目标**：读论文 → 写报告 → **然后更新 wiki 的多个页面**

```
摄入一篇论文的完整流程：
1. 阅读原文，写 reports/paper_analyses/ 报告（保持不变）
2. 更新 wiki/entities/ 中涉及的作者、机构页面
3. 更新 wiki/concepts/ 中涉及的核心概念页面
4. 如有矛盾，在 wiki/concepts/ 中标注新旧观点差异
5. 更新 wiki/index.md（追加新条目）
6. 追加 wiki/log.md 一行记录
7. 如有新概念缺少页面，创建 wiki/concepts/新概念.md（stub）
```

**一篇论文典型影响范围：**

| 摄入论文 | 新建报告 | 更新 wiki 页面（典型） |
|---------|---------|----------------------|
| FlashAttention | 1 | attention_mechanism.md / io_aware_computing.md / dao_tri.md（人物）/ log.md / index.md = 5 个 |
| Mixtral 8×7B | 1 | moe_architecture.md / mistral_ai.md（机构）/ sparse_activation.md / log.md / index.md = 5 个 |
| 罗尔斯《正义论》| 1 | rawls_john.md / justice_as_fairness.md / social_contract_theory.md / log.md / index.md = 5 个 |

### 3.2 Query（查询）

**现状**：问题 → 临时搜索 → 口头回答 → 消失

**目标**：问题 → 读 wiki/index.md → 读相关页面 → 综合回答 → **结果归档到 wiki/syntheses/**

归档规则：
- 一次性问答：**不归档**
- 涉及多概念的比较/综述：**归档为 syntheses/ 页面**
- 重要结论/矛盾发现：**更新相关 concepts/ 页面**

示例：
```
用户问："MoE 和 Dense 在推理成本上有什么本质区别？"
→ 搜索 wiki：moe_architecture.md + scaling_laws.md
→ 综合回答
→ 结果归档为：wiki/syntheses/moe_vs_dense_inference_cost.md
→ 追加 wiki/log.md 一行
```

### 3.3 Lint（健检）

**现状**：无

**目标**：定期（每 10-15 次摄入后）运行 wiki 健检

```
健检项目：
1. 孤岛页面（无其他页面链接到它）
2. 矛盾标注（同一概念两个页面有冲突结论）
3. 过时声明（新论文已否定旧结论但旧页面未更新）
4. 存根页面（Stub，只有标题无内容，需要补充）
5. 缺失概念（reports 中频繁提到但 wiki 中没有页面）
6. 跨项目连接机会（ai-learning 的"注意力"与 psychology-learning 的"选择性注意"）
```

---

## 四、Wiki 页面规范

### 4.1 Concept 页面格式

```markdown
---
id: concept-attention-mechanism
title: "注意力机制（Attention Mechanism）"
domain: [ai-learning]
type: concept
created: 2026-04-06
updated: 2026-04-06
sources: [01_transformer_2017, 18_flashattention_2022]
status: active   # active | stub | deprecated
---

# 注意力机制

## 一句话定义
[20字以内的核心定义]

## 核心原理
[50-100字，精确]

## 关键公式/结构
[必要时保留，但精简]

## 演化脉络
[前驱 → 本概念 → 后续变体]

## 在项目中的报告
- [Transformer 2017](../../reports/paper_analyses/01_transformer_2017.md)
- [FlashAttention 2022](../../reports/paper_analyses/18_flashattention_2022.md)

## 跨域连接
- [选择性注意（心理学）](../../psychology-learning/wiki/concepts/selective_attention.md)

## 开放问题
[当前仍未解决的核心疑问]
```

### 4.2 Entity 页面格式

```markdown
---
id: entity-hinton-geoffrey
title: "Geoffrey Hinton"
type: entity/person
domains: [ai-learning]
---

# Geoffrey Hinton

## 身份
[机构·角色·活跃年代]

## 核心贡献
[3-5条，每条一句话 + 来源]

## 在本项目中的相关报告
[链接列表]

## 与其他人物的关系
[合作者/传承/对立]
```

### 4.3 log.md 格式

```markdown
# Wiki 操作日志

## [2026-04-06] ingest | FlashAttention (Dao et al. 2022)
- 新建报告：reports/paper_analyses/18_flashattention_2022.md
- 更新：wiki/concepts/attention_mechanism.md（添加 IO-aware 变体）
- 更新：wiki/entities/dao_tri.md（新建）
- 更新：wiki/index.md

## [2026-04-06] query | MoE vs Dense 推理成本比较
- 读取：wiki/concepts/moe_architecture.md
- 归档：wiki/syntheses/moe_vs_dense_inference_cost.md

## [2026-04-07] lint | ai-learning 健检
- 发现孤岛页面：3 个
- 发现存根页面：5 个
- 跨域连接机会：attention（ai）↔ selective_attention（psychology）
```

---

## 五、分阶段迁移计划

### Phase 0：基础设施（优先级最高，1-2天）

**目标**：在不破坏现有系统的前提下，建立 wiki 层骨架

```
每个子项目执行：
1. 创建 wiki/ 目录（不删除 knowledge/，并行运行）
2. 创建 wiki/index.md（空模板）
3. 创建 wiki/log.md（空模板）
4. 更新各子项目 AGENTS.md：补充 wiki 操作规范（§2.x）
5. 更新全局 CLAUDE.md：加入 wiki 操作模式说明
```

**不做的事**：不迁移现有内容，不删除 knowledge/，不改变现有摄入流程

---

### Phase 1：ai-learning wiki 建设（示范项目，1-2周）

**选 ai-learning 作为先行示范项目**，因为它报告数量最多（26篇精读 + 8篇知识报告），知识密度最高。

**Step 1.1：人物/机构 entity 页面**（批量创建）

从现有 AI关键人物图谱 report 提取，创建独立页面：
```
wiki/entities/
├── hinton_geoffrey.md    ← 反向神经网络·Boltzmann机·深度学习
├── lecun_yann.md         ← CNN·ImageNet之前的卷积先驱
├── bengio_yoshua.md      ← 序列建模·注意力前驱
├── vaswani_ashish.md     ← Transformer 第一作者
├── brown_tom.md          ← GPT-3 主要作者
├── schulman_john.md      ← PPO·OpenAI政策梯度
├── wei_jason.md          ← Chain-of-Thought
├── openai.md             ← 机构页面
├── deepmind.md
└── meta_ai.md
```

**Step 1.2：核心概念 concept 页面**（从现有报告蒸馏）

```
wiki/concepts/
├── attention_mechanism.md    ← 从 transformer + flashattention 蒸馏
├── transformer_architecture.md
├── scaling_laws.md           ← 从 Scaling Laws 报告 + 知识报告蒸馏
├── rlhf.md                   ← 从 RLHF 知识报告蒸馏
├── lora_peft.md              ← 从 LoRA 知识报告蒸馏
├── moe_architecture.md       ← 从新 MoE 知识报告蒸馏
├── kv_cache.md               ← 从 KV Cache 知识报告蒸馏
├── self_supervised_learning.md ← 从 MAE/DINOv2/VideoMAE 蒸馏
└── sparse_activation.md
```

**Step 1.3：overview.md**

一篇 AI 领域全局综述，反映所有已读论文后的整体图景。每 10 篇新论文后更新一次。

**Step 1.4：更新 Ingest 流程**

从这一步开始，每次新摄入一篇 ai-learning 论文，**必须**同时：
- 更新相关 entities/ 页面
- 更新相关 concepts/ 页面
- 追加 log.md

---

### Phase 2：其余四个学习子项目（2-3周）

按优先级顺序（报告数量/活跃度）：

1. **cs-learning**：20 篇精读，分布式系统知识密集
2. **philosophy-learning**：9 篇文本分析，哲学家人物图谱重要
3. **psychology-learning**：12 篇实验精读，认知偏差图谱已有
4. **biology-learning**：5 篇精读，睡眠科学节点少但质量高

每个项目执行 Phase 1 的相同步骤（entity + concept + overview + log）。

---

### Phase 3：跨域连接（1周）

这是 Karpathy 模式的精髓：**知识在不同领域间流动**。

**跨域连接清单**（初始版本）：

| 来源概念 | 来源项目 | 目标概念 | 目标项目 | 关系类型 |
|---------|---------|---------|---------|---------|
| 注意力机制 | ai-learning | 选择性注意 | psychology | 类比 |
| RLHF 奖励建模 | ai-learning | 行为强化理论 | psychology | 理论基础 |
| 分布式共识（Raft） | cs-learning | 社会共识形成 | philosophy | 类比 |
| 睡眠剥夺与认知 | biology | 认知资源理论 | psychology | 交叉证据 |
| 扩散模型去噪 | ai-learning | 感知去噪（Helmholtz） | philosophy | 类比 |
| MoE 专家分工 | ai-learning | 亚里士多德分工论 | philosophy | 类比 |
| 正义差异原则 | philosophy | 资源分配（机制设计） | cs-learning | 应用 |

**实现方式**：在 concept 页面的 `## 跨域连接` 区块追加链接 + 一句话说明关系类型。

---

### Phase 4：工具链增强（可选，按需）

**4.1 简单搜索脚本**

```python
# scripts/wiki_search.py
# 用途：在 wiki/ 目录中做关键词搜索，返回相关页面列表
# 供 Agent 在 Query 操作时调用
```

Karpathy 提到 [qmd](https://github.com/tobi/qmd) 作为本地搜索引擎（BM25/vector 混合）。在 wiki 规模较小时，简单的 grep 脚本足够；超过 200 页面后考虑引入 qmd。

**4.2 Lint 脚本**

```python
# scripts/wiki_lint.py
# 检查项：孤岛页面 / 存根页面 / 缺失反向链接 / 过时声明标记
```

**4.3 Obsidian 配置建议**

- 启用 Graph View 查看知识图谱连接结构
- 安装 Dataview 插件：通过 frontmatter 中的 `sources` 字段生成动态表格
- 安装 Obsidian Web Clipper：快速将网页文章剪辑为 markdown 放入 raw/

---

## 六、Schema 修改清单

### 6.1 CLAUDE.md 需新增的规则

```
## Wiki Operations Mode

When ingesting a new source:
1. Write reports/ analysis as usual
2. THEN update wiki/:
   - entities/ for all mentioned persons/orgs
   - concepts/ for all core concepts
   - index.md (append entry)
   - log.md (append one-line record)

When answering a multi-concept query:
- Read wiki/index.md first to find relevant pages
- If the answer is synthesizing 3+ concepts, file it to wiki/syntheses/

When running lint:
- Check for orphan pages, stub pages, contradictions
- Report findings, then fix or create issues
```

### 6.2 各子项目 AGENTS.md 需新增的章节

在现有 `§2 Task Execution Protocol` 后新增 `§2.x Wiki Integration`：

```
### 2.x Wiki Integration（摄入后必须执行）

完成 paper_analysis 或 knowledge_report 后：
1. 识别报告中涉及的实体（人物、机构）→ 更新/创建 wiki/entities/
2. 识别核心概念 → 更新/创建 wiki/concepts/
3. 追加 wiki/log.md 一行记录
4. 更新 wiki/index.md
```

---

## 七、不变的部分

以下内容 **不改变**：

- reports/ 目录结构和命名规范（保持现有 90 篇的完整性）
- 7 步分析框架（paper_analysis 和 text_analysis 的质量标准）
- Task Board 机制（LEARNING_PROJECTS_TASK_BOARD.md）
- git commit 规范（§7）
- 各子项目的 CONTEXT.md（功能不变，只是 wiki/index.md 补充其导航功能）

---

## 八、成功标准

### 短期（Phase 0-1 完成后）

- [ ] ai-learning wiki/ 有 ≥ 10 个 entity 页面、≥ 8 个 concept 页面
- [ ] 每次新摄入后 log.md 有记录
- [ ] 一篇新论文摄入后，能通过 wiki/ 而不是 reports/ 回答 "这个概念是什么" 的问题

### 中期（Phase 2-3 完成后）

- [ ] 5 个子项目都有 wiki/ 层
- [ ] ≥ 10 个跨域连接被建立和记录
- [ ] 一次 Lint 操作被执行并生成健检报告

### 长期（稳定运行后）

- [ ] 每次新摄入自然地更新 wiki 多个页面（无需额外提醒）
- [ ] 好的 syntheses 沉淀在 wiki/ 而非消失在对话中
- [ ] Wiki 可以独立回答 "这个领域目前的整体图景是什么" 的问题，无需重新阅读所有报告

---

## 九、一句话总结

**把 EverAgent 从"论文分析流水线"改造为"持续生长的个人知识百科"。**

Reports 是原材料。Wiki 才是目的地。每次摄入不是结束，是 wiki 又成长了一次。

---

> 参考文档：`llm-wiki.md`（Karpathy）
> 当前项目状态：`docs/LEARNING_PROJECTS_TASK_BOARD.md`
> 执行入口：各子项目 `AGENTS.md`
