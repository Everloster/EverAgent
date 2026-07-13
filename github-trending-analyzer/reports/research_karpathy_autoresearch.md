# karpathy/autoresearch 深度研究报告

## 项目概述

`karpathy/autoresearch` 是 Andrej Karpathy 于 2026 年 3 月发布的一个**实验性项目**，核心命题只有一句话：**把一个真实但极小的 LLM 训练环境交给 AI Agent，让它整夜自主做研究实验**。[README]

Agent 的工作循环是：修改代码 → 训练 5 分钟 → 检查指标是否改善 → 保留或丢弃 → 重复。人类早上醒来时，会看到一份实验日志和（理想情况下）一个更好的模型。[README]

它最颠覆直觉的设计在于**人机分工的重新划分**：研究者**不再直接改 Python 代码**，而是编写 `program.md` 这个 Markdown 文件——它为 AI Agent 提供上下文、设定"自主研究组织"的运行规则。训练代码本身是 [nanochat](https://github.com/karpathy/nanochat) 的单 GPU 简化版。[README][代码]

README 开头 Karpathy 用一段"未来考古"式的科幻叙事定调："有朝一日，前沿 AI 研究由自主 Agent 集群在天空中的算力巨构上完成……这个仓库讲的是这一切如何开始的故事。" 项目定位因此不是生产工具，而是一个**范式演示 / 教学原型**。[README]

> 一句话定位：**用一个"5 分钟一轮"的最小训练靶场，演示"AI 自己做 AI 研究"的可行性，并把研究者的角色从'写代码'上移到'写 Agent 的组织规则'。**

## 基本信息

| 项目 | 数据 |
|------|------|
| 仓库 | karpathy/autoresearch |
| 作者 | Andrej Karpathy（前 OpenAI 创始成员、前特斯拉 AI 总监）[Web] |
| 创建时间 | 2026-03-06 [API] |
| 最近推送 | 2026-03-26 [API] |
| Stars | 90,153 [API] |
| Forks | 13,011 [API] |
| 开放 Issue | 202 [API] |
| 主语言 | Python（41,273 字节）+ Jupyter Notebook（8,208 字节）[API] |
| 许可证 | MIT [README] |
| 贡献者数 | 9（karpathy 本人 28 次提交，为最高）[API] |
| 发版/Tag | 无 releases、无 tags [API] |
| 默认分支 | master [API] |

**核心文件清单**（仓库刻意保持极小，只有三个文件"真正重要"）[README][代码]：

```
prepare.py      — 固定常量、数据准备、分词器、dataloader、评估（禁止修改）
train.py        — GPT 模型 + 优化器 + 训练循环（Agent 唯一修改的文件）
program.md      — Agent 指令（人类唯一迭代的文件）
pyproject.toml  — 依赖
analysis.ipynb  — 结果分析
progress.png    — 进度图
```

## 技术分析

### 3.1 三文件架构：约束即设计

项目的工程哲学是**用极致的约束换取实验的可比性与可控性**。`program.md` 明确划出 Agent 的能力边界 [代码]：

- **能做**：只改 `train.py`——架构、优化器、超参、训练循环、batch size、模型大小全部开放。
- **不能做**：改 `prepare.py`（含评估函数 `evaluate_bpb`，是"ground truth 指标"）、装新依赖、改评估 harness。[代码]

这个设计直接呼应了"Evolve the Harness"式的思路：**冻结评估与数据管线（环境契约），只让 Agent 在受控的代码面里搜索**。

### 3.2 固定 5 分钟时间预算 + val_bpb 指标

训练**恒定跑 5 分钟墙钟时间**（不含启动/编译），指标是 `val_bpb`（验证集 bits per byte，越低越好）。[README][代码]

两个关键设计动机 [README]：
1. **可比性**：无论 Agent 改了模型大小/架构/batch size，实验都在同一时间预算下比较。`val_bpb` 与词表大小无关，因此架构改动可被公平比较。
2. **平台自适应**：固定预算意味着 autoresearch 会为"你当前这块 GPU"找到该预算下最优的模型——代价是跨平台结果不可比。

作者估算：**约 12 次实验/小时，睡一觉约 100 次实验**。[README]

### 3.3 train.py 里的真实技术栈（Agent 的起点基线）

读 `train.py` 源码可见基线并非玩具，而是集成了多项前沿技巧 [代码]：

- **Flash Attention 3**：通过 `kernels` 库动态加载；Hopper（cap 9.0）用 `varunneal/flash-attention-3`，非 Hopper 回退到 `kernels-community/flash-attn3`。[代码]
- **优化器 Muon + AdamW** 组合（README 明示）。[README]
- **Value Embedding / Value Residual（ResFormer 式）**：`has_ve()` 按层交替启用，通过一个输入相关的 per-head gate（`ve_gate`，`2*sigmoid(...)`）把 value embedding 混入 v。[代码]
- **GQA（分组查询注意力）**：`n_head` 与 `n_kv_head` 分离，`c_k/c_v` 用 `n_kv_head` 维度。[代码]
- **RoPE 旋转位置编码**：`apply_rotary_emb` 手写实现。[代码]
- **窗口注意力模式 `SSSL`**：短短短长的交替 banded attention（README 建议小算力改用纯 "L"）。[代码]
- **RMSNorm**：`norm(x)` 用 `F.rms_norm`。[代码]

基线默认配置 [代码]：`n_layer=12, n_head=6, n_embd=768, vocab_size=32768, sequence_len=2048`（README 的 forks 指南中提到默认 `DEPTH=8`，说明 baseline 参数在迭代中有过调整，以代码为准）。

### 3.4 program.md：Agent 的"研究组织操作系统"

`program.md` 本质是一个**超轻量的 skill**，把整个自主研究流程编码为自然语言协议 [代码]：

1. **Setup**：与用户商定 run tag → 建分支 `autoresearch/<tag>` → 读三个文件 → 校验数据 → 初始化 `results.tsv`。
2. **Experimentation**：每轮改 `train.py` → 跑 5 分钟 → 目标是最低 `val_bpb`。**首轮必须先建立 baseline**。
3. **简洁性判据（Simplicity criterion）**：同等效果下越简单越好；"删代码换来同等或更好结果"是最佳结果；"0.001 的提升却加 20 行 hacky 代码"不值得。[代码]
4. **Logging**：结果写入 TSV（`commit / val_bpb / memory_gb / status / description`，status ∈ keep/discard/crash）。[代码]

这套设计的深层含义：**研究进步的"配方"被外置到 Markdown**，人类通过迭代 `program.md`（加更多 Agent、改研究策略）来提升"研究组织"本身的效率，而非直接调模型。

### 3.5 实验循环与结果记录：results.tsv 作为"实验室笔记本"

整个系统的可复现性由一张 TSV 表撑起。每完成一轮 5 分钟训练，Agent 必须往 `results.tsv` 追加一行，字段为 `commit / val_bpb / memory_gb / status / description`。[代码]

- **commit**：每次实验对应一个 git commit，保证任意结果都能回溯到确切代码状态。[代码]
- **status ∈ {keep, discard, crash}**：`keep` 表示指标改善予以保留，`discard` 表示无效回滚，`crash` 表示训练崩溃（如 OOM 或 NaN loss）。[代码]
- **description**：自然语言记录这一轮改了什么、假设是什么。[代码]

这本质上是把"科学实验记录规范"编码进 Agent 协议：**每个改动都是一次受控实验，都有基线对照、量化指标和明确结论**。`analysis.ipynb` 与 `progress.png` 则把这张表可视化成 `val_bpb` 随实验次数下降的曲线，让人类一眼看出"这一夜的研究组织跑得好不好"。[代码][推测]

### 3.6 防呆机制：让 Agent 快速失败

`prepare.py` 与训练循环里内置了若干"快速失败"逻辑，避免 Agent 把宝贵的墙钟预算浪费在无效运行上。从提交历史可见，早期修复过 **NaN loss 的快速失败** 与 **无限循环** 问题（2026-03-11 提交）。[API] 这体现了一个务实取向：**在把控制权交给 Agent 的同时，用硬约束兜住最常见的失败模式**，让"整夜无人值守"真正可行。

## 社区活跃度

- **爆发式关注**：90,153 stars / 13,011 forks [API]，对一个"实验性教学仓库"是现象级数字，主要由 Karpathy 的个人影响力 + "AI 自研 AI"话题驱动 [推测]。
- **提交节奏**：核心提交集中在 **2026-03-06 至 2026-03-26** 的三周窗口内（从近期 commits 可见：03-09 加初学者指南、03-11 修 NaN loss 快速失败与无限循环、03-16 加 AMD ROCm fork、03-21 增强 README）。[API]
- **此后进入休眠**：最近推送停在 **2026-03-26**（截至 2026-07-07 已约 3.5 个月无新提交）。[API] 这符合其"一次性范式演示"的定位，而非持续维护的框架 [推测]。
- **贡献者结构**：9 位贡献者，karpathy 本人 28 次提交居首，其余为社区 PR（如 bug fix、fork 链接）。[API]
- **社区扩散以 fork 为主**：README 维护了一个"Notable forks"列表，覆盖 MacOS（miolini、trevin-creator/MLX）、Windows（jsegov/RTX）、AMD（andyluo7）等平台移植。[README] 这说明社区活力更多体现在**平台适配的分叉**而非主仓库贡献。

## 发展趋势

- **定位是"起点"而非"产品"**：README 的科幻叙事和"the story of how it all began"表明，Karpathy 意在**抛出一个可被无限迭代的范式**（研究组织即代码），而把具体演进交给社区 fork 与各人的 `program.md`。[README]
- **可迭代方向明确**：作者直言"如何迭代 `program.md`、如何往里加更多 Agent 以找到研究进步最快的'研究组织代码'是显而易见的"。[README] 这暗示未来方向是**多 Agent 研究组织 + program.md 的进化**。
- **小算力民主化**：README 用大篇幅给出在 MacBook 等小设备上的调参指南（换 TinyStories 数据集、降 `vocab_size`/`MAX_SEQ_LEN`/`DEPTH`、改窗口模式为 "L"），显示作者希望降低参与门槛。[README]
- **平台支持不亲自扩展**：作者明确表示暂不打算亲自支持 CPU/MPS，鼓励社区 fork——意味着主仓库会保持"极小内核"，生态在外围生长。[README]

## 竞品对比

autoresearch 处在两个交叉赛道：**极简 LLM 训练教学仓库**（nanoGPT/nanochat 谱系）与 **AI 自主科研 Agent**（AI-Scientist 谱系）。

| 项目 | Stars | 语言 | 许可证 | 最近推送 | 定位差异 |
|------|-------|------|--------|---------|---------|
| **karpathy/autoresearch** | **90,153** | Python | MIT | 2026-03-26 | AI Agent 自主迭代训练代码，5 分钟/轮靶场 |
| karpathy/nanochat | 55,976 | Python | MIT | 2026-07-04 | autoresearch 的"母体"，全功能极简 ChatGPT 复刻 [API] |
| karpathy/nanoGPT | 60,872 | Python | MIT | 2025-11-12 | 经典极简 GPT 训练教学，人工调参 [API] |
| KellerJordan/modded-nanogpt | 5,474 | Python | MIT | 2026-07-03 | 人类竞速刷 nanoGPT 训练速度纪录（Muon 优化器发源地）[API] |
| SakanaAI/AI-Scientist | 14,167 | Jupyter Notebook | NOASSERTION | 2025-12-19 | 端到端自主科研（写论文/评审），范围更大 [API] |

**关键区别**[代码][API][推测]：
- **vs nanochat/nanoGPT**：后两者是"人来调"的教学仓库；autoresearch 把"调"这个动作交给 Agent，人只写 `program.md`。它是 nanochat 的**单 GPU 单文件裁剪版 + Agent 循环外壳**。
- **vs modded-nanogpt**：modded-nanogpt 是**人类专家竞速**刷纪录（同样用 Muon）；autoresearch 是**让 Agent 自动**做类似的速度优化搜索。二者指标哲学相通（固定目标下比速度/效率），执行主体不同。
- **vs AI-Scientist**：AI-Scientist 覆盖"提假设→做实验→写论文→同行评审"的完整科研链；autoresearch 只聚焦"训练代码的实验迭代"这一窄环节，但因此**更可控、可复现、门槛更低**。

## 总结评价

**优点**：
- **范式清晰且可复现**：三文件 + 5 分钟预算 + 单指标，把"AI 自研 AI"这个宏大命题压缩成任何有一块 GPU 的人都能跑的最小实验。[README][代码]
- **分工洞察深刻**：把研究者的角色从"改代码"上移到"写 `program.md`（研究组织规则）"，是对未来研究工作形态的一个具体主张。[代码]
- **基线不糊弄**：`train.py` 集成 FA3、Muon、ResFormer value residual、GQA、RoPE、窗口注意力等前沿技巧，Agent 是在真实 SOTA 基线上做优化搜索。[代码]
- **教学价值高**：MIT 许可 + 详尽的小算力调参指南 + 社区 fork 生态，降低了参与门槛。[README]

**局限**：
- **非持续维护的生产工具**：2026-03-26 后进入休眠，定位是"一次性范式演示"。[API]
- **跨平台结果不可比**：固定时间预算的代价是不同 GPU 上的 `val_bpb` 无法横向比较。[README]
- **仅限单 GPU / NVIDIA**：主仓库不支持 CPU/MPS/多卡，需依赖社区 fork。[README]
- **"自主研究"的深度有限**：搜索空间被限制在单文件 `train.py` 内的训练技巧，距离 AI-Scientist 式的完整科研自动化还有距离 [推测]。

**评价**：这是一个**影响力远超代码量**的项目——90K stars 买的不是一套可部署框架，而是 Karpathy 对"研究工作范式迁移"的一次高浓度示范。它的真正产物是那句被反复引用的主张：**未来研究者编程的对象不再是 Python 文件，而是 Agent 的组织规则（`program.md`）**。对想理解"AI 自主研究""harness/scaffolding 演进"的人，它是一个几乎零门槛的最佳起点。

---
*报告生成时间: 2026-07-07*
*研究方法: github-deep-research 多轮深度研究*
