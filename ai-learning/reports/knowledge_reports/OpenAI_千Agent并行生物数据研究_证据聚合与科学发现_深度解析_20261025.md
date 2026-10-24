---
title: "OpenAI 千 Agent 并行生物数据研究：证据聚合与科学发现的深度解析"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["AI-for-Science", "Agent", "GPT-Rosalind", "Perturb-seq", "科学发现", "证据聚合"]
---

# OpenAI 千 Agent 并行生物数据研究：证据聚合与科学发现的深度解析

**研究对象**：OpenAI 官方文章《Using thousands of AI agents to uncover new leads in biological data》（页面时间戳 2026-10-23T10:00，新闻稿口径为 2026-10-21），及其直接链接的一手材料：配套 bioRxiv 预印本《Distributed AI agents enable comprehensive discovery of biological insights at scale》（Sun et al., 2026-10-16）、被解读的原始数据论文《Genome-scale functional mapping of the mammalian whole brain with in vivo Perturb-seq》（Shi et al., 2026-03-18）、PerturbAI 的数据卡与官方新闻稿、OpenAI 的 GPT-Rosalind 发布页。

> **标注约定**（全文通用）
> - `[原文事实]`：可在引用来源中逐字或逐表核对到的内容，括注来源与定位。
> - `[自报]`：OpenAI / PerturbAI / 合作方自述、未经独立复现的数据与结论。
> - `[代码证据]`：来自仓库、配置、数据卡、目录结构的可核对事实。
> - `[第三方转述]`：媒体或聚合站点转述的、来自一手来源的数字。
> - `[推测]` / `[待验证]`：本报告作者的推断或尚未解决的疑点。
>
> **本报告未运行任何 agent、未访问受限数据集、未复现任何评测。** 文中一切性能与能力数字均为来源转述；`[自报]` 与 `[第三方转述]` 不可混为一谈。
>
> **全文最重要的阅读纪律**：本项工作**没有产生任何已被实验验证的生物发现**。它的产出是"线索"和"假说"，而不是"发现"。§2.2 给出了三层状态的严格定义，后文所有案例都按这三层标注。

---

## 开头三行：x → f → f(x)

- **x**：现代功能基因组学实验的产出规模已经**远超人类科学家的解释带宽**——一次全脑 Perturb-seq 扰动筛选能同时测到近 2,000 个基因敲除在 770 万个细胞里的转录反应，但"理解这些结果意味着什么"需要把细胞类型差异、扰动间相似性、疾病相关性以及散落在几十年文献里的机制知识整合起来。`[原文事实]` 论文原文把瓶颈说得很直白："**our capacity to interpret the results from them is limited by human expert capacity**"（预印本 Introduction）。OpenAI 提出的问题是：**能不能把"解释"这一步也变成可扩展的？**
- **f**：答案是"分布式生物推理"（distributed biological reasoning）——**按数据的天然可分解单元切分任务，而不是按科学问题切分**：一个扰动（gene disruption）= 一个独立 agent，1,946 个 agent 拿到各自的细胞类型分辨 DEG 谱、实验上下文、同一套提示词与带文献检索的分析环境，各自产出"证据链接"的报告，再被合并成一张把基因、细胞效应、文献与可能机制连起来的 **reasoning atlas**；每个 agent 的每个发现都必须被打上 `agree / inferred / disagree / no literature` 标签，冲突不靠投票消解，而是显式暴露给人工复核。`[原文事实]` 关键设计是**对照实验保持模型、提示、工具、数据访问不变，只变并行度**，再用"打乱扰动身份、保留转录谱"的对照排除"模型只靠表达谱猜答案"的捷径。
- **f(x)**：接受 f 之后可以得到三个**已被量化**的收益：(1) **覆盖度**——单 agent 在最大负载下只引用 11 篇文献，分布式 agent 保留了 711 倍以上的引用（论文口径）；(2) **结论恢复能力**——在不给 agent 看源论文的条件下，71 条源研究发现中有 35 条 matched、13 条 refined、9 条 partially recovered；在 55 条仅依赖 DEG 数据、可直接检验的发现里，48 条 matched/refined、4 条部分恢复；(3) **人类偏好**——30 位博士级生物学家评审 60 份报告，在 20 组配对、每组 3 次判断的 60 个选择中，分布式报告获选 45 次（75%），单 agent 获选 10 次，另有 5 次平局。**但验证状态必须同时说明**：以上三项**都是"解释质量"的指标，不是"科学正确性"的指标**；本工作没有做湿实验，因此**没有任何一条新机制进入"已验证"层**。真正被这次工作改变的是**科学工作的排队结构**（从"先做筛选再想解释"变成"筛选完立刻产出可排序的待验证清单"），而不是生物学本身。

---

## 一、一手来源清单与读法

| 编号 | 来源 | 类型 | 本报告用途 | 定位 |
|---|---|---|---|---|
| S01 | OpenAI《Using thousands of AI agents to uncover new leads in biological data》 | 官方发布文 | 厂商叙事主线、两个案例、75% 与 32 分钟等数字 | https://openai.com/index/scaling-ai-research-for-complex-biological-data （页面时间戳 2026-10-23T10:00） |
| S02 | bioRxiv 预印本《Distributed AI agents enable comprehensive discovery of biological insights at scale》（Alexander Sun, Joshua J Park, David DeTomaso, … Xin Jin） | 一手论文（未同行评审） | 方法、对照、恢复率、held-out 预测、文献标签体系 | https://www.biorxiv.org/content/10.64898/2026.10.15.759436v1 （2026-10-16，CC-BY 4.0） |
| S03 | bioRxiv《Genome-scale functional mapping of the mammalian whole brain with in vivo Perturb-seq》（Shi et al.） | 一手论文（数据来源） | 1,947 基因、7.7M 细胞、原始结论、利益冲突 | https://www.biorxiv.org/content/10.64898/2026.03.16.711480v1 （2026-03-18） |
| S04 | PerturbAI 新闻稿《PerturbAI and OpenAI Unveil First-of-Its-Kind AI Reasoning Agents》 | 合作方一手说明 | 75% 偏好、8M 细胞口径、商业延伸（药物靶点发现） | https://perturb.ai/news/perturbai-launches-ai-reasoning-agents （2026-10-21） |
| S05 | Hugging Face 数据卡 `perturbai/wholebrain_crispr_atlas` | 一手数据卡 | 数据规模、格式、访问门槛、引用关系 | https://huggingface.co/datasets/perturbai/wholebrain_crispr_atlas |
| S06 | R&D World《OpenAI runs 1,946 GPT-Rosalind agents on a mouse brain atlas》（Brian Buntz） | 媒体转述 | 30 位盲评者、7,586 篇引用、单 agent 也提出 DCTN1 线索 | https://www.rdworldonline.com/openai-deploys-nearly-2000-gpt-rosalind-agents-to-generate-biological-research-leads-in-32-minutes （2026-10-21T22:16Z） |
| S07 | Unite.AI《OpenAI Unveils Mouse Brain Reasoning Atlas From GPT-Rosalind Agents》 | 媒体转述 | 数据行数与体积、作者机构等二手补充 | https://www.unite.ai/openai-unveils-mouse-brain-reasoning-atlas-from-gpt-rosalind-agents （2026-10-21） |
| S08 | OpenAI《Introducing GPT-Rosalind for life sciences research》 | 官方发布文 | 模型定位、可用渠道、上线与定价时间、公开评测 | https://openai.com/index/introducing-gpt-rosalind （2026-04-16，含 2026-09-11 / 2026-10-05 更新） |
| S09 | GitHub `jinlabneurogenomics/wholebrainperturbseq` | 代码 | 数据论文分析代码 | https://github.com/jinlabneurogenomics/wholebrainperturbseq |
| S10 | GitHub `jinlabneurogenomics/distributed_agent` | 一手代码与复现说明 | agent runtime、corpus tooling、论文 notebook、托管 MCP、Codex CLI 本地运行与数据准备口径 | https://github.com/jinlabneurogenomics/distributed_agent |

**读法说明**：S01 是"怎么讲"，S02 是"实际做了什么、怎么验证"，S03 是"数据从哪来、原始结论是什么"，S04/S06/S07 是"合作方与媒体补齐了哪些细节"，S05 是"别人能不能拿到数据"，S08 是"底层模型是什么"，S10 是"别人具体能复现到哪一层"。**本报告的分析主体建立在 S02 上，而不是 S01 上**——因为 S01 里的每一个数字都要在 S02 里找口径。

---

## 二、原文问题与回答的重构

### 2.1 OpenAI 到底在回答什么问题

`[原文事实]` S01 的开篇把目标说得很克制："What if scientists could uncover new clues about Alzheimer's and Parkinson's in minutes instead of months?"（S01）——注意用词是 **new clues（新线索）**，不是 new insights，更不是 discoveries。

`[原文事实]` S01 给出的四条论证线：

1. **规模问题**："Researchers can now alter thousands of genes and measure their effects across millions of cells. But understanding what these results mean for human disease requires connecting complex experimental findings with decades of scattered scientific knowledge."（S01）
2. **方法命名**："The team divided the analysis among thousands of AI agents powered by GPT-Rosalind, an approach we call distributed biological reasoning."（S01）
3. **产出物定义**："Their reports were combined into a reasoning atlas linking genes, cellular effects, relevant publications, and possible biological mechanisms."（S01）
4. **人的位置**："These findings help prioritize further experiments needed to test the proposed biological mechanisms."（S01）——**产出的是"要做的实验"，不是"已知的机制"**。

`[评]` 这四条构成了一个相当完整、也相当保守的论证：OpenAI 卖的不是"AI 发现了新机制"，而是"AI 把实验数据里还没被读出来的部分排成了一张待验证清单"。**这个定位是诚实的**（论文的标题也只敢说 "insights at scale"），但媒体转述在传播中普遍把它推向了"发现"（§5.5 会列出具体例子）。

### 2.2 三层状态：线索 / 假说 / 验证（本报告的核心区分框架）

这是理解这项工作科学有效性的关键，也是所有二手报道最容易糊掉的地方。本报告给出一个严格定义：

| 状态 | 定义 | 本项工作的实例 | 谁来判定 |
|---|---|---|---|
| **L1 线索（observation / lead）** | 数据集内部可复现的定量观察，**不依赖任何文献解释** | 小脑 GABAergic 神经元中 Tsc2 敲除产生 83 个 FDR<0.1 的 DEG，而 Tsc1 敲除为 0（S02 Fig. 2M） | 实验数据本身；本工作只是把已有的图谱读出来 |
| **L2 假说（hypothesis / mechanistic interpretation）** | 把 L1 线索与文献连接后得到的**机制解释**，本工作**未做实验检验** | "DCTN1 缺失可能改变神经元内胆固醇分布，并促成神经退行"（S01、S06） | 只能由后续湿实验判定 |
| **L3 验证（validated finding）** | 有独立实验（如胆固醇成像、DCTN1 敲除神经元表型）支持 | **本工作没有产出任何 L3 结论** | — |

`[原文事实]` 支持这一划分的最强证据来自论文自身：S02 在描述 Tsc1/Tsc2 的小脑差异时明确写道——"This finding with no-literature flag marks a potential knowledge gap as **these relationships remain hypotheses for investigations**."（S02）以及 Nup93 案例——"this mechanism **remains a hypothesis**"（S02 Fig. 3F）。

`[评]` **"lead ≠ discovery"是这项工作最应该被正确转述的一点**。同一篇论文里，既有被 agent 正确识别的 L1 观察，也有被人工复核**推翻**的机制外推（§4.4 的 Wdr26 案例），也有没有任何文献先例、只能标 `no literature` 的知识缺口。把这三层压平成一个"AI 发现生物学新机制"的标题，会同时丢掉这项工作的方法论价值和它的科学边界。

---

## 三、系统如何工作：分布式生物推理的工作流

### 3.1 任务分解：切分单元是"扰动"，不是"科学问题"

`[原文事实]` S02："We ran **1,946 AI agents** independently and in parallel (Fig. 1A). Each agent received cell-type-resolved differentially expressed gene (DEG) profiles, experimental context, and a shared prompt and coding environment with analytical tools and literature access. Agents could inspect the data, **compare perturbations**, and pursue perturbation-specific analyses."（S02）

`[原文事实]` 污染控制是显式设计的："Importantly, the source manuscript and conclusions were withheld: we used **GPT-Rosalind-5.5**, whose stated knowledge cutoff was **December 2025**, preceding the release of the source manuscript in **March 2026**."（S02）

`[评]` 这一条决定了这项工作**能不能被有意义地评价**。如果 agent 的训练知识里已经含有源论文的结论，那么"恢复源论文结论"就只是复述，"发现新线索"就只是被污染的产物。作者把知识截止日期放在源论文发布之前（甚至早于整篇预印本近 10 个月），使"恢复率"成为一个有意义的指标。

`[原文事实]` 数据侧的分母是 1,947：**源论文扰动了 1,947 个疾病相关基因**（S03 摘要："transcriptome-wide responses to loss of **1,947 disease-associated genes**, profiling over **7.7 million cells**"），而系统跑了 **1,946 个 agent**（S02）。`[推测]` 二者差 1，合理的解释是有一个基因的扰动没有可分析的转录响应（论文的 workload 实验也只用了"有可检测转录响应"的 893 个扰动），但**本报告未在读到的论文部分找到对这一差的显式说明**，记为待验证。

### 3.2 每个 agent 的产出：一份"证据链接"的报告

`[原文事实]` S02 Fig. 1B 说明了一份代表性报告（以 *Psmb4* 为例）的结构："linking cell-type breadth, directional transcriptional programs, and cross-perturbation similarities to biological interpretations, **caveats**, and proposed experiments."（S02）——注意其中明确包含 **caveats（注意事项/局限）** 与 **proposed experiments（建议实验）** 两栏。

`[原文事实]` 证据链接标签体系（S02 Fig. 2B）：对 **1,519 条发现**做四分类：

| 标签 | 定义（论文原文口径） | 含义 |
|---|---|---|
| `agree` | 已有文献直接支持 | 观察与文献一致 |
| `inferred` | 有机制性支持但没有直接匹配的观察 | 合理外推，**未证实** |
| `disagree` | 与文献导出的预期冲突 | 需要人工复核 |
| `no literature` | 没有检索到相关先例 | **是检索缺口，不是"没有相关研究"的证明**（论文图注原文："denotes a retrieval gap, not proof that no relevant study exists"） |

`[原文事实]` 完整论文给出了四类的精确分布：`agree` 420 条（27.6%）、`inferred` 636 条（41.9%）、`disagree` 101 条（6.6%）、`no literature` 362 条（23.8%）；全部并行运行共记录 39,185 次论文阅读并保留 16,445 条引用（S02 Fig. 2B–C）。这意味着**只有 27.6% 属于直接文献一致**；其余多数需要区分“机制性外推”“显式冲突”和“未检索到先例”，不能合并写成“有文献支持”。

`[评]` 这套标签是本项工作**最值得迁移的部分**。它把"AI 说的话"变成"带证据等级的结构化陈述"，而且第四类的定义（检索缺口 ≠ 不存在）直接堵住了 AI 研究最常见的过度断言。详见 §9。

### 3.3 文献检索：并行度如何转化为覆盖度

`[原文事实]` S02 的负载实验："We assigned one agent between one and **893 perturbations** while keeping the same model, prompt, tools, and data access."（S02）——注意这里的关键约束：**模型、提示、工具、数据访问全部固定**，唯一变量是并行度。

`[原文事实]` 结果："At 893 perturbations, the single agent cited **11 references**, while the distributed agents retained **711x more references** (Fig. 2E). 'No-literature-retrieved' flags increasingly dominated single-agent outputs, whereas distributed agents maintained similar flag proportions across workloads (Fig. 2F, Table 2)."（S02）

`[原文事实]` S06 转述："the distributed agents retained **7,586 references**, approximately 711 times as many"；并补充"the team recruited **30 doctoral-level biologists** for a blinded review"。`[待验证]` 7,586 ÷ 11 ≈ 690，与论文的 711× 不完全一致；可能是论文与报道采用了不同的引用计数口径（如"引用"vs"保留"、去重前后）。本报告以论文的 711× 为准并保留该不一致。

`[评]` **"711× 引用"不是"711× 知识"**。它是**检索广度**的指标：单 agent 在 893 个扰动的负载下，其上下文预算被"读文献"挤占，最终只留下 11 篇引用，而 `no-literature` 标签开始占主导。换句话说，**单 agent 的失败模式是"注意力被稀释 + 检索预算耗尽"，而不是"推理能力不足"**。这解释了为什么论文说 distributed agents "maintained similar flag proportions across workloads"——并行化保护了**每个子任务的检索深度**。

### 3.4 合并：从 agent 报告到 reasoning atlas

`[原文事实]` S01："Their reports were combined into a reasoning atlas linking genes, cellular effects, relevant publications, and possible biological mechanisms."（S01）S02 的摘要把它描述为 "assembles their outputs into an atlas linking biological interpretations and supporting evidence"。

`[代码证据]` S10 已公开并可访问。仓库明确提供 agent runtime、corpus tooling、论文分析 notebook 与补充表，并给出两条复现层级：① 托管只读 MCP 暴露 Findings、Claims、supporting evidence 与 release-specific tools，但不含原始数据，不能重新计算统计；② 本地路径默认用 Codex CLI，可下载固定 SHA-256 的 **10.8 GB Parquet**，准备全部八个 BioEval task manifest，需预留约 **35 GB**、最终占用约 **31 GB**。仓库还提供 Shi 与 Shi holdout 两套 corpus、Git LFS 论文产物、`prepare-manuscript` 与 notebook 复现入口，软件许可为 MIT。换言之，**论文表格与图的离线复现材料已公开，完整 agent 重跑仍受数据下载、模型访问与运行成本约束**。

### 3.5 工作流机制示意

```
                    ┌────────── 输入层：已有实验数据（非新实验）──────────┐
                    │  whole-brain in vivo Perturb-seq atlas            │
                    │  1,947 疾病相关基因 × 7.7M 单核细胞 × 19,070 mRNA │
                    │  8,588 sgRNAs / Allen WMB 分类标注               │
                    │  公开 benchmark 入口：10.8 GB pinned Parquet     │
                    └───────────────────────┬──────────────────────────┘
                                            │  按扰动切成 1,946 份
                    ┌───────────────────────┼──────────────────────────┐
                    ▼                       ▼                          ▼
        ┌───────────────────┐  ┌───────────────────┐      ┌───────────────────┐
        │  Agent #1 (Tsc1)  │  │  Agent #2 (Tsc2)  │ ...  │ Agent #1946       │
        │  ┌─────────────┐  │  │  ┌─────────────┐  │      │  ┌─────────────┐  │
        │  │ DEG 谱        │  │  │  │ DEG 谱        │  │      │  │ DEG 谱        │  │
        │  │ 实验上下文    │  │  │  │ 实验上下文    │  │      │  │ 实验上下文    │  │
        │  │ 共享提示词    │  │  │  │ 共享提示词    │  │      │  │ 共享提示词    │  │
        │  │ 分析工具+文献 │  │  │  │ 分析工具+文献 │  │      │  │ 分析工具+文献 │  │
        │  └──────┬──────┘  │  │  └──────┬──────┘  │      │  └──────┬──────┘  │
        │         ▼         │  │         ▼         │      │         ▼         │
        │  交叉扰动比较       │  │  交叉扰动比较       │      │  交叉扰动比较       │
        │  文献检索 + 机制解释 │  │  文献检索 + 机制解释 │      │  文献检索 + 机制解释 │
        │  每条发现打标签      │  │  每条发现打标签      │      │  每条发现打标签      │
        │  agree/inferred/    │  │  agree/inferred/    │      │  agree/inferred/    │
        │  disagree/no-lit    │  │  disagree/no-lit    │      │  disagree/no-lit    │
        │  + caveats + 建议实验│  │  + caveats + 建议实验│      │  + caveats + 建议实验│
        └─────────┬─────────┘  └─────────┬─────────┘      └─────────┬─────────┘
                  │                       │                          │
                  └───────────────────────┴──────────────────────────┘
                                          ▼
                    ┌────────────── 合并层 ──────────────┐
                    │  reasoning atlas                    │
                    │  基因 ↔ 细胞效应 ↔ 文献 ↔ 可能机制    │
                    │  冲突不投票消解，显式上抛人工复核      │
                    └──────────────┬─────────────────────┘
                                   ▼
                    ┌────────────── 评估层 ──────────────┐
                    │  ① 恢复源论文结论（不给 agent 看原文） │
                    │  ② 文献覆盖 vs 单 agent（固定模型/工具）│
                    │  ③ held-out 扰动效应预测             │
                    │  ④ 打乱对照（打乱扰动身份、保留转录谱）│
                    │  ⑤ 盲评：30 位博士级生物学家           │
                    └──────────────┬─────────────────────┘
                                   ▼
                    ┌────────────── 产出层 ──────────────┐
                    │  L1 线索（数据内观察）                │
                    │  L2 假说（机制解释，未验证）          │
                    │  L3 验证 → 本工作未产出，需后续湿实验   │
                    └────────────────────────────────────┘
```

### 3.6 对照组设计：本工作最硬的部分

`[原文事实]` S02 设置了三层对照：

1. **单 agent baseline（负载实验）**：模型、提示、工具、数据访问固定，单个 agent 承担 1→893 个扰动，与分布式模式对比（S02 Fig. 2E–F）。
2. **扰动身份打乱（shuffling）**："Perturbation-identity shuffling while preserving transcriptional profiles, with literature-label distributions for **unshuffled, within-screen-shuffled, and out-of-screen-shuffled** inputs."（S02 Fig. 2H–I）——**在保留转录谱的前提下打乱扰动身份**，用来检验 agent 的标签是不是只依赖表达谱形状。
3. **held-out 预测**：留出扰动、预测其转录响应，并与多个基线比较（响应基线、物理互作基线、DepMap essentiality 基线、DEG 幅度基线，以及 **Biomni workflow** 基线）（S02 Fig. 3K–L）。

`[评]` 这三层对照的设计水平明显高于多数"AI 做科学"的宣传稿。特别是打乱对照：**如果 agent 只是从表达谱形状倒推生物学身份，那么打乱后标签分布应当几乎不变**；论文正是用这一点来排除这条捷径。这与 §3.1 的知识截止日期控制共同构成了"结论不是背出来的"的双重保证。

---

## 四、案例证据表：逐个案例的原始问题、agent 结论、验证方式与未证实之处

| # | 原始生物问题 | Agent 产出的结论 | 层级 | 验证方式 | 尚未证实之处 |
|---|---|---|---|---|---|
| 1 | **Tsc1 vs Tsc2 在小脑是否一致？**（两基因协同调控 mTOR） | 在小脑 GABAergic 神经元中，Tsc2 敲除产生 **83** 个 FDR<0.1 的 DEG（突触与钙信号相关），Tsc1 敲除**为 0**；两者在若干其他神经元群高度相关（`agree`） | **L1**（数据内观察）+ L2（与结节性硬化症小脑异常的关联） | 来自已有图谱（S02 Fig. 2J、2M）；与源论文结论一致 | **L2 部分**：哪些改变可被现有 mTOR 抑制剂纠正、哪些指向新疗法，均需湿实验；论文未验证 |
| 2 | **DCTN1 缺失与胆固醇合成/转运是否相关？**（DCTN1 突变致 Perry 综合征） | Dctn1 敲除使胆固醇合成相关基因表达升高；结合"胆固醇转运问题会促使细胞合成更多胆固醇"的文献，提出"DCTN1 缺失改变神经元内胆固醇分布并促成神经退行"的假说 | **L2 假说** | 3 位盲评者给出平均 follow-up priority **4.3/5**（S06） | **完全未验证**：细胞内胆固醇分布、神经退行因果关系均无实验证据；`[第三方转述]` S06 还指出**单 agent baseline 也独立提出了这条线索**——即该线索**并非分布式并行独有** |
| 3 | **Grin2a / Grin2b（两个 NMDA 受体亚基）效应是否相似？** | 两者驱动**相反**的转录程序，由 agent 定义的 **47 基因 signature** 表征；该现象亦为源论文结论之一 | **L1**（源论文结论被恢复）+ L2（邻域解释） | 论文 Fig. 1F 专门对比源论文结论与 agent 分析；源论文摘要亦称"closely related disease genes such as two NMDA receptor subunits can drive opposing transcriptional programs"（S03） | 具体神经环路机制未验证 |
| 4 | **Wdr26 与 Tsc2 的关系？**（跨扰动相似性） | Wdr26 与 Tsc2 高度相似（cosine **0.629**），但 agent 打出 **`disagree`** 标签：从成纤维细胞 GID-AMPK 研究外推，预测 Wdr26 缺失会升高 AMPK、降低 mTOR，与观察相反 | **L2 假说，且被人工复核推翻** | **人工复核**："different subunits in GID have distinct functions and *WDR26* loss did not suppress mTORC in a subsequent study"（S02 引用 26、27） | **该机制外推已被后续研究否定**；这是本工作中"agent 会犯的典型错误"最有说服力的实例 |
| 5 | **Rab7 与 Tsc1/Tsc2 是否收敛？** | 标为 `inferred`：基于 RAB7 在内体运输与 mTORC1 调控中的既定作用，预测存在收敛 | **L2 假说** | 论文明确写出"although this convergence was **not directly demonstrated**"（S02） | 未证实；`inferred` 标签的价值即在于把这种外推与 `agree` 区分开 |
| 6 | **Psmb4 / Smarcb1 / Smarcb2 的蛋白稳态与 SWI/SNF 程序** | agent 报告把细胞类型广度、方向性转录程序与跨扰动相似性连起来，并给出未被论文覆盖的额外洞察（蛋白酶体补偿、应激反应、重塑与维持基因诱导） | **L1 + L2** | 论文 Fig. 1F 逐条对比"源论文结论 / agent 分析 / agent 额外洞察"三栏 | 额外洞察均为假说层级，未实验验证 |
| 7 | **held-out 扰动的转录响应可预测吗？** | 平衡准确率 **0.705**；正确识别零 DEG 扰动 **142/172 = 82%**；非零 DEG 扰动 **59/100 = 59%**；并给出具体锚点推理（*Psmc5* 预测 520 DEG vs 观测 624，落于 Psmc1 430 与 Psmb4 742 之间；*Fus* 预测 180 vs 观测 130） | **L2 假说（定量）** | 与响应基线、物理互作基线、DepMap essentiality 基线、DEG 幅度基线、Biomni workflow 比较；另有 depletion 预测（38 个显著 depletion 扰动，Fisher 精确检验 + BH 校正），与 DepMap 对比 | 预测的是**转录响应幅度**，不是生物功能；且 agent 只拿到转录证据，depletion 与细胞计数在预测时被 withheld |
| 8 | **Nup93 为何"无响应"？** | agent 预测 Nup93 无响应，并提出机制解释：既有核孔骨架的**持续性**可在编辑到取材的 **21–28 天**间隔内缓冲转录后果 | **L2 假说** | 论文明确标注"this mechanism **remains a hypothesis**" | 未验证；缓冲假说本身有实验设计上的可检验含义 |

`[评]` 这张表的分布很说明问题：**能站得住的是 L1（数据内可复现的观察），最脆的是 L2（机制外推）**，而第 4 行说明 L2 的错误是**可以被具体证伪的**——这正是"证据链接标签 + 人工复核"这套机制存在的理由。若没有 `disagree` 标签与人工复核，Wdr26 的外推极可能被当作新机制写进后续实验计划。

---

## 五、关键数字与逐项口径核对

### 5.1 工作量与规模

| 数字 | 出处 | 口径与注意事项 |
|---|---|---|
| "thousands of AI agents" | S01 标题与正文 | **标题级修辞**；实际为 **1,946** 个（S02），S04 中 OpenAI 的 Joy Jiao 表述为 "Running nearly 2,000 agents in parallel" |
| **1,946 agents** | S02 | 一个扰动一个 agent，独立并行；与源论文的 **1,947** 个基因相差 1（原因未在所读论文部分说明） |
| **32 分钟** | S01、S04、S06 | 完成"分析 + 合成出带证据链接的发现"的总耗时；**未说明**是否含模型排队、是否含人工环节、GPU 型号、token 消耗与美元成本 |
| 人类耗时 "months to a year" | S01、S04、S06 | **纯估计值**：假设 $22/小时、每个扰动 15 分钟解读、每篇文献 10 分钟。论文图注原文明确："**this is not a measured human performance**"（S02 Fig. 2D）；S06 亦称其为 "an illustrative figure" |
| **7.7 million cells** | S03 摘要、S05 数据卡 | 源论文与数据卡口径 |
| "8 million cells" | S04、S07 | 宣传口径；S05 图注亦用 "8M brain cells"，但数据卡 Key Highlights 写 "7.7 million cells"，S07 转述 **7,739,370 行 / 205 GB**——**7.7M 与 8M 的差异是四舍五入还是两套统计，未核实** |
| 19,070 mRNA / 8,588 sgRNA | S05 | 单核转录组测序深度与 guide 数 |
| 205 GB / 7,739,370 行 | S07 转述 S05 | **未从数据卡原文直接核实**（本报告读到的数据卡片段未含行数与体积） |

### 5.2 评估结果

| 指标 | 数值 | 口径 |
|---|---|---|
| 源论文发现恢复 | 71 条中 **35 matched + 13 refined + 9 partially recovered + 14 not covered** | agent **未获得**源论文与结论；知识截止 2025-12 早于源论文 2026-03 |
| 其中"可直接检验"的发现 | **55** 条中 **48** 条 matched 或 refined、**4** 条 partially recovered | 分母从 71 缩到 55，因部分发现所需证据不在 agent 拿到的数据里 |
| 文献标签分布 | **1,519** 条：agree 420（27.6%）、inferred 636（41.9%）、disagree 101（6.6%）、no literature 362（23.8%） | S02 Fig. 2B；`no literature` 只是检索缺口 |
| 负载实验 | 单 agent 与分布式在 **893** 个扰动上对比，负载从 1 递增 | 模型、提示、工具、数据访问固定 |
| 引用量 | 单 agent **11 篇**；分布式 **711×**（S07 转述为 7,586 篇） | **711× 与 7,586/11≈690 的不一致未解决** |
| 盲评偏好 | **75%** 偏好分布式报告 | 30 位博士级专家；20 组配对 × 每组 3 位 = 60 个判断，其中分布式 45、单 agent 10、平局 5；论文未给该比例的置信区间或预注册信息 |
| DCTN1 假说评分 | 平均 follow-up priority **4.3/5**（3 位盲评者） | S06 |
| held-out 预测 | 平衡准确率 **0.705**；零 DEG 142/172（**82%**）；非零 DEG 59/100（**59%**） | 对比响应基线、物理互作基线、DepMap、DEG 幅度基线、Biomni workflow |
| depletion 预测 | **38** 个扰动检出显著 depletion（Fisher 精确检验 + BH） | agent 预测时未获得 depletion 与细胞计数 |

### 5.3 厂商自述与第三方转述的一致与冲突

| 数字 | OpenAI 官方（S01） | PerturbAI（S04） | 媒体（S06/S07） | 论文（S02） | 判断 |
|---|---|---|---|---|---|
| agent 数 | "thousands" | "nearly 2,000" | 1,946 | 1,946 | **一致**（除标题修辞） |
| 耗时 | 32 分钟 | 32 分钟 | 32 分钟 | "in minutes" | **一致**，但**无成本数字** |
| 人类对照 | months to a year | months to a year | months to a year（并注明是 illustrative） | 图注明示 $22/h 等假设，且注明"非实测" | **一致**，且论文与媒体都标注了估计性质 |
| 盲评偏好 | 75% | 75% | 75% | 45/60 选择分布式、10/60 选择单 agent、5/60 平局 | **一致**；完整论文补齐了样本设计，但未给置信区间 |
| 细胞数 | "millions of mouse brain cells" | 8 million | 7.7M / 8M 混用 | 7.7 million | **口径不齐**：论文与数据卡 7.7M，PR 8M |
| 引用倍数 | ">700 vs 11" | 未给 | 7,586（约 711×） | 711× | **数值微冲突**（690 vs 711） |
| DCTN1 线索归属 | "The agents found one such lead in DCTN1" | — | "The study's **single-agent baseline also** generated a lead" | — | **归属需要限定**：该线索并非分布式并行独有 |

`[评]` 总体上，**OpenAI 与 PerturbAI 两方的口径高度一致，且媒体转述基本忠实**；真正的张力不来自数字冲突，而来自**表述层面的升级**：标题用 "uncover new leads"（准确），而大量二手内容直接写成 "AI 发现新机制"（不准确）。

### 5.4 独立复现的缺位

`[推测]` 本项工作的所有评估数字（恢复率、引用覆盖、盲评偏好、held-out 预测）**都由作者团队自行完成**，本报告未检索到任何针对该 reasoning atlas 或该预印本的独立复现或批评。`[推测]` 这类"厂商自评 + 媒体转述 + 无第三方复现"的组合是 AI-for-Science 报道的常见结构，本报告无法据此判断数字真伪，只能按 §5.3 的口径逐条登记。**特别提示**：本报告在此**不引用**其他模型评测中出现的耸动指标（如某些聚合站点把第三方评测写成 "N% hallucination rate" 式的标题）来暗示本工作存在同类问题——**那些数字属于别的模型与别的评测，与本工作无关**。

### 5.5 贡献分解：工作流创新 / 模型能力 / 工具与数据 / 人类科学家

这是本报告认为最有迁移价值的一节。把这项工作的产出拆成四层：

| 层 | 具体贡献 | 是否可被其他团队复用 | 证据 |
|---|---|---|---|
| **A. 工作流创新** | ① 按天然可分解单元（扰动）分配 agent；② 强制**证据链接标签**（agree/inferred/disagree/no literature）；③ 冲突**不消解**、显式上抛人工复核；④ **保持模型/提示/工具/数据访问不变**的并行度对照；⑤ **扰动身份打乱**对照；⑥ 多层评估（恢复率 / 覆盖度 / held-out 预测 / 盲评排序） | **高**——与领域无关，是"如何让大量 agent 的产出可被信任"的方法论 | S02（Fig. 1、2、3 与 Methods 描述） |
| **B. 模型能力** | GPT-Rosalind-5.5 的科学推理与工具使用 | **待验证**——论文**没有做模型消融**（只固定模型做并行度对照），因此**无法把效果归因于模型本身**；GPT-Rosalind 的公开评测（BixBench、LABBench2）来自 OpenAI 自家评测 | S02（无模型对照）、S08 |
| **C. 工具与数据基础** | 1,947 基因的**活体**全脑 Perturb-seq 图谱、文献检索与代码执行环境、公开的 agent runtime / corpus tooling / notebook、托管 MCP 与 Codex CLI 本地运行 | **中低**——软件和论文复现产物已公开；完整 benchmark 需 10.8 GB 固定数据、约 31 GB 准备产物，原始数据访问、GPT-Rosalind-5.5 与重跑成本仍是门槛 | S03、S05、S10 |
| **D. 人类科学家的贡献** | 源论文的实验设计（选择 1,947 个疾病相关基因、活体筛选方案）、细胞类型注释体系、**30 位盲评者**的人工评审、**人工复核推翻 Wdr26 外推**、以及外部学者的公开评述 | **不可替代**——这是整条链上"科学判断"的真正所在 | S02、S03、S06、S07 |

`[评]` **四层里只有 A 层可以自由复用，B 层是黑箱，C 层是壁垒，D 层是科学性的锚点。** 一个想复刻这条路的团队，最该抄的是 A 层与评估设计，最难获得的是 C 层，最不能外包的是 D 层。

---

## 六、与替代路径的有边界比较

| 路径 | 相对这项工作的优势 | 相对这项工作的劣势 | 适用边界 |
|---|---|---|---|
| **单 agent（全量上下文）** | 单一推理链，跨扰动的整体一致性更强；实现与调试最简单；成本最低 | 在 893 扰动负载下**只引用 11 篇**，`no-literature` 标签占主导，检索预算被挤压；覆盖面窄 | 扰动数量少（几十以内）、需要全局一致性推理的任务 |
| **传统生物信息学 pipeline** | **统计严格、可复现、无模型幻觉**；DEG/module/相似性分析是确定性的；可直接进版本化流程 | 只产出"列表与相似性"，**不产出机制解释与文献连接**；不排序"下一步做什么" | 差异表达、通路富集、聚类这类**已被充分定义**的分析 |
| **文献综述 agent / 检索式 agent** | 文献覆盖广、擅长综述与证据整理、单任务成本低 | **看不到实验数据**，无法发现"数据里的意外"；本工作中 Tsc1/Tsc2 小脑差异这类**数据内发现**恰恰是纯文献路线拿不到的 | 已有明确问题、只需证据整理的场景 |
| **自主湿实验室**（如 Google 类自动化实验闭环） | **能真正完成 L3 验证**——设计实验、跑实验、读结果 | 成本高、周期长、失败率受物理实验限制；本工作的 L2 假说正好是这类系统的**上游输入** | 需要把假说变成事实的阶段；两者是**流水线上下游**，不是竞品 |

`[评]` 值得强调的是**最后一行**：这项工作的定位不是替代湿实验，而是**成为湿实验的排序器**。它把"做哪个实验"这个决策的搜索空间从数千个扰动压缩到一份带证据等级和 caveats 的清单。S02 Discussion 的原话把这个分工说得很清楚："Reading the literature, weighing explanations, and choosing decisive experiments would remain central to scientific training and judgment, while agents broaden the questions researchers can pursue."

`[评]` 与**传统 pipeline** 的比较还藏着一个容易被忽略的点：本工作实际上**并未取代** DEG 分析——agent 拿到的输入就是"细胞类型分辨的 DEG 谱"，也就是 pipeline 的产物。**pipeline 负责产生可分析的信号，agent 负责解释与排序。** 因此把它描述成"取代生物信息学"是错位的。

---

## 七、科学有效性与可复现性边界

### 7.1 有效性上做得扎实的地方

1. **知识污染控制**：模型知识截止（2025-12）早于源论文发布（2026-03），且源论文与结论被 withheld（S02）。
2. **可归因的对照**：并行度实验固定模型、提示、工具、数据访问（S02 Fig. 2E–F）。
3. **反捷径对照**：打乱扰动身份、保留转录谱（S02 Fig. 2H–I）。
4. **多基线比较**：held-out 预测对比了响应基线、物理互作基线、DepMap、DEG 幅度基线与 Biomni workflow（S02 Fig. 3K–L）。
5. **错误被显式暴露并被人工推翻**：Wdr26 的 `disagree` 标签最终被后续研究否定（S02）。
6. **评估者独立且有量表**：30 位博士级专家不能使用生成式 AI，可在线检索；每人评 6 份报告，四个维度均用五分量表，60 份报告每份获得 3 次评价（S02 Fig. 4H）。

### 7.2 有效性上明显薄弱的地方

1. **所有评估由利益相关方完成**：`[自报]` 预印本作者中包含 OpenAI 员工与 PerturbAI 员工，Grace Zheng 与 Xin Jin 是 PerturbAI 联合创始人（S03 利益冲突声明、S07）。**无独立第三方复现。**
2. **盲评仍是小样本主观评估**：完整论文给出了 20 组配对、60 次选择（45/10/5）和 30 位专家的分配方式，但没有报告 75% 的置信区间、预注册方案或跨领域复验；三位评审对同一报告也不能替代实验验证。
3. **人类对照是构造出来的**：`[自报]` "months to a year" 来自 $22/h、15 min/扰动、10 min/篇 的假设，论文自己标注"not a measured human performance"。它**不能作为"提速 N 倍"的证据**，只能作为量级直觉。
4. **成本缺失**：32 分钟对应多少 token、多少美元、什么硬件，**全部未公开**。
5. **无湿实验**：**没有任何 L3 结论**。
6. **多数产出不是直接文献一致**：1,519 条中 `agree` 仅 27.6%，`inferred` 41.9%，`disagree` 6.6%，`no literature` 23.8%。这不等于 72.3% 都错误，却说明大多数条目必须保留外推、冲突或检索缺口标签，不能被宣传口径压成“文献支持的发现”。
7. **"专家偏好"不等于"专家正确"**：盲评测的是**偏好与排序一致性**，不是**科学正确性**；一个被偏好但机制错误的外推，在该评估下同样得高分。

### 7.3 可复现性边界

| 要素 | 状态 |
|---|---|
| 原始数据 | HF 数据卡仍是门控入口（S05）；S10 的公开复现脚本下载固定 SHA-256 的 10.8 GB Parquet，并生成约 31 GB 的 benchmark 数据，不能据此推断全部原始资产只有 10.8 GB |
| 数据论文分析代码 | **公开**：`jinlabneurogenomics/wholebrainperturbseq`（MIT 未标注，6 stars，创建 2026-05-13，最近推送 2026-09-15）（S09） |
| agent 框架代码 | **公开**：`jinlabneurogenomics/distributed_agent`，MIT；含 agent runtime、corpus tooling、论文 notebook、saved predictions/reports/prompts/run measurements 与八个 BioEval task manifest（S10） |
| reasoning atlas | S10 提供临时托管站点与两个无需额外 Distributed Agents 账号/API key 的只读 MCP 端点；托管层没有原始数据，不能重算统计 |
| 模型 | GPT-Rosalind-5.5，走 OpenAI **trusted access**（需合格机构申请），非公开可下载权重；定价自 2026-10-05 生效（S08） |
| 复现门槛 | **浏览证据与复现论文图表**的门槛已明显降低；**完整重跑 agent**仍需要数据、Codex/OpenAI 认证、GPT-Rosalind-5.5 访问资格和未公开的真实成本预算 |

---

## 八、对 EverAgent 双仓 agent harness / eval 的可迁移启示

`[评]` 以下每条都注明了在本报告中的证据锚点，并区分"可直接迁移"与"需改造"。

### 8.1 可直接迁移

1. **按数据的天然可分解单元分配 agent，而不是按"问题"分配。** `[锚点 S02]` 1,946 个 agent 对应 1,946 个扰动，每个 agent 只负责一个切片。在 EverAgent 的 harness 里，对应的做法是**让一个 agent 负责一个 artifact / 一个文件 / 一个 symbol / 一个 test case**，而不是让一个 agent"负责整个仓库"。这直接对应本工作最硬的收益（单 agent 11 篇 vs 分布式 711×）。
2. **"证据链接标签"是可直接搬走的输出契约。** `[锚点 S02 Fig. 2B]` `agree / inferred / disagree / no literature` 四分类，以及"no literature = 检索缺口而非不存在"的定义，可以原样变成 EverAgent 报告/claim 层的字段。EverAgent 现有的 `support: direct | derived | inference` 三值**缺一个 `disagree`/`no-evidence` 档**，建议补上——否则"检索不到"和"有冲突"这两种最需要人工看的状态会被压进 `inference`。
3. **保持一切不变、只变并行度的对照设计。** `[锚点 S02 Fig. 2E–F]` 这是让"并行化收益"可归因的前提；EverAgent 的 eval 若要比较"单 agent vs 多 agent"，必须固定模型、提示、工具与数据访问。
4. **"打乱身份、保留内容"的反捷径对照。** `[锚点 S02 Fig. 2H–I]` 这一招在代码场景同样可用：把 symbol 名打乱、保留实现与调用关系，看 agent 的结论是否随之改变。
5. **多层评估而非单一分数。** `[锚点 S02]` 恢复率 / 覆盖度 / held-out 预测 / 盲评排序四层，分别对应"会不会漏""看得够不够多""能不能外推""人认不认"。EverAgent 的 eval 不应只用一个总分。

### 8.2 需要改造才能迁移

6. **"冲突不消解、显式上抛"需要一个真实的冲突通道。** `[锚点 S02]` 本工作的 `disagree` 标签最终由人工复核（Wdr26 案例）落地。EverAgent 的双仓结构（公开仓 + 私有仓）天然有跨边界上抛的需要，但需要显式设计"agent 之间如何互相标记冲突"的协议，否则退化为投票。
7. **成本必须与人类对照一起报，且人类对照必须标注是估计还是实测。** `[锚点 S02 Fig. 2D]` 本工作做得对的地方是明确写了"not a measured human performance"；这应当成为 EverAgent 报告规范的一条：**任何"比人类快 N 倍"的说法必须附带对照的构造方式与实测/估计标注。**
8. **污染控制在多 agent 场景下比单 agent 更难。** `[锚点 S02]` 本工作靠"模型知识截止早于源论文发布"来防污染。EverAgent 的 agent 天然会读到仓库里已有的结论（MAP/wiki/历史报告），**同一类污染会更严重**：多 agent 互相引用会让同一个错误被复制 N 份。`[推测]` 需要的对策包括：agent 之间的证据引用需可追溯到一手来源、共享上下文需标记"未经独立验证"。

### 8.3 不可迁移 / 需要警惕

9. **数据与工具门槛无法靠编排弥补。** `[锚点 S05、S08]` 门控数据、限定模型、托管 corpus 服务——这三者决定了这类工作的进入壁垒。EverAgent 可以迁移"编排与评估"，但**不能声称能迁移"科学产出"**，因为后者的绝大部分价值来自数据与湿实验。
10. **不要把"偏好"当成"正确"。** `[锚点 S02 + S04]` 盲评测的是偏好与排序一致性；Wdr26 的案例说明，**一个被人类专家打高分的机制外推仍可能是错的**（该案例最终被后续研究否定）。任何以"专家偏好率"为主指标的 eval 都有这个盲区。
11. **可复现性依赖托管服务时，要标注依赖。** `[锚点 S10]` 本工作的本地复现路径依赖 Codex CLI，且托管 corpus 服务不含原始数据。EverAgent 若采用同类"托管服务 + 本地可跑"的组合，应在报告里写明哪一部分只能查询、哪一部分能离线复算、哪一部分需要模型重跑。

---

## 九、Limitations（本研究自身的边界）

1. **未运行任何 agent、未访问门控数据集、未复现任何评估。** 全部数字为来源转述。
2. **已补读 21 页主论文 PDF，但未读完整补充材料与全部 notebook 实现**：盲评设计、标签分布、reasoning atlas 合成、Fig. 3 指标和数据可用性已核对；主 PDF 多处仍引用 Methods / supplementary tables，本文未逐项审计这些补充材料。
3. **未读到源数据论文全文**，只读了其摘要、标题与利益冲突声明；agent 侧的"55 条可直接检验发现"的分母判定标准未在源论文中核对。
4. **agent 框架仓库已定位并核对 README，但未实际运行**：MIT 许可、托管 MCP、本地 Codex CLI、10.8 GB pinned Parquet、约 31 GB 准备产物和论文 notebook 均来自 S10；本文没有下载数据、调用 MCP 或复现图表。
5. **数据卡的行数与体积未从一手核实**：7,739,370 行 / 205 GB 来自 S07 转述，本报告读到的数据卡片段未含该数字；7.7M vs 8M 的差异未解决。
6. **711× 与 7,586/11≈690 的不一致未解决**（§5.3）。
7. **75% 偏好的样本设计已核对，但统计边界仍在**：20 组配对、60 次判断中 45 次偏好分布式；论文未报告该比例的置信区间、预注册或独立复验。
8. **GPT-Rosalind 的公开评测（BixBench、LABBench2）只读到 S08 的描述性段落**，未核对具体分数与对照模型；S08 亦未解释论文所用 "GPT-Rosalind-5.5" 与该页首发版本的关系。
9. **未核实**是否存在针对本工作的独立第三方复现或批评；本报告只检索到报道，未检索到复现。
10. **未评估合作方的商业动机**：`[自报]` S04 明确将本工作导向"joint drug-target discovery"，且 PerturbAI 图谱"已被下载超过 40,000 次"——**这构成对"哪些线索被优先提出"的无干扰性疑问，但本报告没有数据回答它**。
11. **资料时点**：全部网络读取发生于 2026-10-25（UTC 16:16–17:10 左右）；论文、仓库、榜单与 PR 状态可能随后变化。

---

## 十、思考与追问

### 10.1 我真正理解了什么

- **这项工作的真正创新不是"用了很多 agent"，而是"给每个 agent 配了一套证据等级契约，并且把冲突留给人"。** `disagree` 与 `no literature` 这两个标签，加上"检索缺口 ≠ 不存在"的定义，是让它区别于普通"AI 综述 agent"的核心；Wdr26 案例证明这套契约**真的拦下了一个错误外推**。
- **并行度的收益机制被低估了。** 单 agent 在 893 扰动下只引用 11 篇、`no-literature` 标签开始主导——这不是"模型变笨了"，而是**同一上下文里的检索预算被稀释**。因此并行化的第一收益是**保护子任务的检索深度**，而不是"总产出更多"。任何"多 agent 一定更强"的说法都应该先问：**上下文预算在多 agent 之间是怎么分的？**
- **"新线索"与"新发现"之间存在一个不可跨越的鸿沟，而这个鸿沟靠工程手段跨不过去。** 本工作在 L1（数据内观察）上可信，在 L2（机制假说）上脆弱，在 L3（验证）上完全空白。而 S03 的利益冲突声明、S04 的商业延伸都提醒我们：**推动 L2→L3 的动力来自商业方时，"哪些线索被优先提出"本身就是一个需要被审视的变量**。
- **归因纪律决定了这份工作能学到什么。** 论文固定模型、提示、工具、数据访问做并行度对照，还做了打乱扰动身份的对照——正因为如此，我们才能说"收益来自编排"而不是"来自更强的模型"。**这正是 AI-for-Science 报告应该有的最低证据标准。**

### 10.2 我还没搞懂什么

- **四类标签如何随 agent、细胞类型与效应强度变化？** 总体分布已经取得，但 41.9% `inferred` 中有多少能经后续实验站住，仍决定这套系统的长期价值。
- **盲评的外部有效性如何？** 设计与样本量已经明确；仍需回答专家分配是否充分随机、不同专业背景是否一致、75% 在独立数据和不同模型上能否复现。
- **32 分钟的真实成本**：token 数、美元、硬件、以及"是否包含失败重试"。没有成本，32 分钟就只是工程叙事。
- **7.7M vs 8M**、**711× vs 690**、**1,947 vs 1,946** 三处数字差异的来源。
- **agent 报告的质量方差**：是否存在大量低质量/注水的 agent 报告被合并进 reasoning atlas？论文没有报告 agent 级质量分布。
- **这份 reasoning atlas 里到底有多少条是"值得做实验"的**？follow-up priority 的分布比均值（4.3/5）更有信息量。

### 10.3 下一步读什么或做什么

1. 补读 supplementary methods、八个 BioEval manifest 与 saved run measurements，核对 agent 配置、提示词、失败重试和 32 分钟的真实计量边界。
2. 在隔离环境跑通 S10 的只读 MCP 查询和 `prepare-manuscript`，再决定是否值得下载 10.8 GB benchmark 数据做图表复现。
3. 补读 S03 源论文的 55 条"可直接检验发现"的判定标准，理解"48 条恢复"的分母。
4. 检索是否存在针对该 reasoning atlas 的独立生物学家复盘或反驳（尤其是 Tsc1/Tsc2 小脑差异与 DCTN1-胆固醇假说）。
5. 在 EverAgent 侧做一个**最小可迁移实验**：把现有报告的 claim 层加上 `no-evidence` / `conflict` 两个标签，并用"打乱 anchor、保留正文"做一次反捷径对照，检验本报告 §8.1 的第 2、4 条是否真的可迁移。

---

## 附：来源清单（可复核）

- S01 https://openai.com/index/scaling-ai-research-for-complex-biological-data （OpenAI 官方文章，页面时间戳 2026-10-23T10:00）
- S02 https://www.biorxiv.org/content/10.64898/2026.10.15.759436v1 （Sun et al.《Distributed AI agents enable comprehensive discovery of biological insights at scale》，2026-10-16，CC-BY 4.0，**未同行评审**）
- S03 https://www.biorxiv.org/content/10.64898/2026.03.16.711480v1 （Shi et al.《Genome-scale functional mapping of the mammalian whole brain with in vivo Perturb-seq》，2026-03-18）
- S04 https://perturb.ai/news/perturbai-launches-ai-reasoning-agents （PerturbAI 新闻稿，2026-10-21）
- S05 https://huggingface.co/datasets/perturbai/wholebrain_crispr_atlas （PerturbAI 全脑图谱数据卡，**门控访问**）
- S06 https://www.rdworldonline.com/openai-deploys-nearly-2000-gpt-rosalind-agents-to-generate-biological-research-leads-in-32-minutes （R&D World，2026-10-21）
- S07 https://www.unite.ai/openai-unveils-mouse-brain-reasoning-atlas-from-gpt-rosalind-agents （Unite.AI，2026-10-21）
- S08 https://openai.com/index/introducing-gpt-rosalind （OpenAI，2026-04-16，含 2026-09-11 / 2026-10-05 更新）
- S09 https://github.com/jinlabneurogenomics/wholebrainperturbseq （数据论文分析代码仓库，读取于 2026-10-25）
- S10 https://github.com/jinlabneurogenomics/distributed_agent （agent runtime、corpus tooling、论文 notebook、托管 MCP 与本地复现说明，MIT，读取于 2026-10-25）
