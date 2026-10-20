---
title: "实测笔记：book-to-skill 能优化 EverAgent 学习类项目吗？"
domain: "ai-practice"
report_type: "experiment_analysis"
status: "completed"
created: "2026-07-29"
updated_on: "2026-10-20"
semantic_tags: ["book_to_skill", "docling", "pdf_extraction", "progressive_disclosure"]
source_url: "https://github.com/virgiliojr94/book-to-skill"
artifact_paths:
  - "experiments/book-to-skill-demo/kimi-k3-tech-report/SKILL.md"
  - "experiments/book-to-skill-demo/kimi-k3-tech-report/chapters/ch02-architecture-kda.md"
---

# 实测笔记：book-to-skill 能优化 EverAgent 学习类项目吗？

> 类型：B 类 ai-practice 低成本 demo + 实测评估。
> 日期：2026-07-29。素材：Kimi K3 官方技术报告（47 页 / 38K token）。工具：[book-to-skill](https://github.com/virgiliojr94/book-to-skill)；星数是当时观察值，不作为实验结论证据。
> 结论先行：**能优化，但只在一个特定场景；且对公式密集的学术论文有硬伤。别当银弹。**

## 运行环境与版本可追溯性

| 项目 | 可确认信息 | 证据边界 |
|---|---|---|
| `book-to-skill` | 实验日前最近的公开 commit 为 [`c6bc1b7`](https://github.com/virgiliojr94/book-to-skill/tree/c6bc1b7927822e563aae6212c07670f5a3d95ea7)，其 `pyproject.toml` 标记版本 `1.2.0`、Python `>=3.9` | 原实验没有保存 clone 的 `HEAD`，因此这个 commit 是日期锚点，不能证明当时 checkout 精确等于它 |
| Python | Homebrew Python 3，venv 隔离 | 原实验没有保存 `python --version`；具体 major/minor/patch 无法事后可靠恢复 |
| `docling` | 通过 `.venv/bin/pip install docling` 安装；上游 `technical` extra 当时未固定版本 | 原实验没有保存 `pip freeze`，具体版本未知；复现实验必须显式 pin 并保存 lock/receipt |
| 运行平台 | Apple Silicon Mac，Homebrew Python，PEP 668 环境 | 未保存 macOS、芯片与依赖完整清单，性能数据不用于跨机器比较 |

提交到仓库的实验产物只有 [`SKILL.md`](./kimi-k3-tech-report/SKILL.md) 和 [`ch02-architecture-kda.md`](./kimi-k3-tech-report/chapters/ch02-architecture-kda.md)。`$TMPDIR/book_skill_work/full_text.txt`、`metadata.json` 及其它草稿未归档，因此本报告只能复核已提交的两件产物与当时记录的输出统计。

## 一、怎么跑的（可复现）

1. `git clone book-to-skill` → `python3 scripts/extract.py --check` 查依赖
2. Homebrew Python PEP668 外部管理，建 venv：`python3 -m venv .venv && .venv/bin/pip install docling`
3. 抽取（技术书模式，docling 保表格/公式）：`.venv/bin/python scripts/extract.py k3_tech_report.pdf --mode technical`
   - 结果：47 页 → 28,602 词 / ~38K token / 检测 17 章，输出 `$TMPDIR/book_skill_work/{full_text.txt,metadata.json}`
4. 按其 SKILL.md 方法论（"提取结构非摘要"）蒸馏成 skill。仓库最终只保留核心 `SKILL.md` 与一篇 KDA 章节样本；速查写在 `SKILL.md` 内，未单独提交术语表和其它章节。

## 二、实测发现（一手，非听说）

### ✅ 做得好的
- **docling 抽取质量高**：行内数学符号完整保留（`α_t ∈ (0,1)^{d_k}`、`S_t ∈ R^{d_k×d_v}`）、章节层级识别对（`## 2.1.1`）、引用编号 `[64]` 都在。比 pdftotext（会丢结构）强一档——**技术文档装 docling 是对的**。
- **架构合理**：核心 SKILL.md 只放心智模型+章节索引（~4k token），章节文件按需加载不占预算。这个"渐进式披露"设计确实能省 token。
- **理念先进**："提取结构不做摘要" + "Discovery Loop Tax（省 token）" 是对的方向。

### ❌ 硬伤（这次实测撞到的关键局限）
- **编号公式全丢**：docling 对 K3 报告的独立公式块（Eq.1–6）输出 `<!-- formula-not-decoded -->` 占位——**公式主体没抽出来**。对 KDA 这种靠公式讲清的机制，蒸馏出的章节只能靠行内符号 + 人工补全。→ **对公式密集的学术论文，它会丢最硬核的部分。**
- **无 ToC 时章节靠标题扫描**：K3 报告没 ToC，工具 WARN 章节映射可能漏/重。
- **"蒸馏"这步本质是 LLM 干的**：工具 = `extract.py`(抽取) + 一套喂给 agent 的 prompt(SKILL.md)。质量下限取决于抽取，上限取决于跑它的模型。它不是"确定性程序"。
- **复现 receipt 缺失**：没有保存 Python、docling 精确版本、上游 checkout HEAD 和 `pip freeze`。结论可由已提交产物支持，但无法做到依赖级完全复现。

## 三、能否优化 EverAgent 学习类项目？——分场景结论

| 场景 | 结论 | 理由 |
|------|------|------|
| **一整本厚技术书**（几百页、prose 为主） | ✅ **值得用** | 这是它主场：自动按章蒸馏 + `/book 主题` 按需查，补 EverAgent 现在薄弱的"厚书检索" |
| **大批量文档/文件夹** | ✅ 值得用 | 一次折叠成一个可查 skill，省"记得哪篇讲啥" |
| **公式密集的学术论文**（如 K3/多数 AI 论文） | ⚠️ **有限** | 公式会丢；不如现有 `paper_analysis`（人工真读、逐符号）。**这恰是 ai-learning 的主力场景** |
| **单篇深读** | ❌ 不需要 | 现有 `paper_analysis` 更强 |

### 和 EverAgent 现有能力的关系（关键）
EverAgent **早已有它 80% 的思想**：`wiki/concepts/`（42 页结构化知识）、`拆书取景` skill、按需加载的 reports——都是"把知识变成 agent 可用结构"。所以 book-to-skill **不是补缺失能力，是把已有做法产品化**。

## 四、给 Everloster 的建议

1. **不整体引入**（否则就是"和现有方法论 80% 重合的工具"，违背"先复用再造轮子"铁律）。
2. **可借鉴的 2 个点**，折进现有 `拆书取景`/`paper_analysis` skill：
   - **章节文件按需加载**的目录结构（core SKILL.md + chapters/）——比现在单篇长报告更省 token
   - **Discovery Loop Tax** 视角：报告设计时算一下"回答一个问题要读多少"
3. **真要用它的场景**：哪天你有**一整本 prose 型技术书/文档想随用随查**（不是公式密集论文），直接上 book-to-skill；公式密集的 AI 论文仍走 `paper_analysis`。
4. **docling 值得单独留着**：它抽 PDF 保结构的能力，对 ai-learning 的 papers/ 处理有独立价值（哪怕不用 book-to-skill）。

## 五、思考与追问
1. 要不要把"章节文件按需加载"这个结构，试点折进 `paper_analysis` 或 `拆书取景` skill？（省 token，且是你已认可的渐进式披露）
2. docling 保留下来专门处理 `papers/` 那 30 篇 PDF，值不值得做一个"论文 → 结构化 md"的批处理？
3. 公式丢失这个硬伤，有没有更强的抽取器（如 Nougat/mathpix 类）值得对比？——但那又是"为工具而工具"的风险，得先确认真需求。
