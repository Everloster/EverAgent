# 🧠 EverAgent — 个人学习与研究工作台

> 用 AI Agent 驱动的个人知识体系，覆盖 AI 技术、哲学思想与开源生态
> 创建日期：2026-03-23 | 最后更新：2026-03-23

---

## 项目全景

EverAgent 是一个以 AI Agent 为核心工具的个人知识库，通过系统化的学习路径、深度分析报告和自动化工具，将学习从"被动积累"变为"主动建构"。

目前包含 **3 个子项目**：

| 项目 | 领域 | 核心产出 | 状态 |
|------|------|---------|------|
| [🤖 AI Learning](./ai-learning/) | 人工智能技术 | 论文精读 · 技术深度报告 | 🟢 活跃中 |
| [📚 Philosophy Learning](./philosophy-learning/) | 西方哲学史 | 经典文本分析 · 概念图谱 | 🟢 活跃中 |
| [📈 GitHub Trending Analyzer](./github-trending-analyzer/) | 开源生态 | 每日/周/月热点分析报告 | 🟢 活跃中 |

---

## 📂 项目概览

### 🤖 AI Learning — 人工智能系统学习

**目标**：覆盖近20年 AI 发展史、30+ 核心论文精读、持续积累技术深度报告。

三个核心视角：**技术深度**（论文精读）× **历史叙事**（人物图谱、硬件彩票）× **工程实践**（Infra 与数据）

当前进度：
- ✅ Transformer 论文精读报告
- ✅ Tulu 3 后训练流程分析（SFT→DPO→RLVR）
- ✅ Self-Attention 深度解析 + 代码实现
- ✅ RLHF 技术路径深度解析
- ✅ AI 关键人物图谱（Transformer 作者去向 · OpenAI 分裂史）
- 📄 30 篇核心论文 PDF 已就位

→ [进入项目](./ai-learning/README.md)

---

### 📚 Philosophy Learning — 西方哲学系统学习

**目标**：覆盖 2500 年西方哲学史、25 部必读经典、30 篇核心论文。

三个核心视角：**思想深度**（经典文本精读）× **历史叙事**（人物图谱、师承关系）× **当代相关性**（哲学如何照亮 AI、政治、伦理困境）

当前进度：
- ✅ 西方哲学 2500 年发展时间线
- ✅ 哲学关键人物图谱（苏格拉底 → 维特根斯坦）
- ✅ 系统学习路径 Phase 1–5
- 📖 25 部经典书籍索引 + 30 篇论文索引已就位

→ [进入项目](./philosophy-learning/README.md)

---

### 📈 GitHub Trending Analyzer — 开源热点追踪

**目标**：自动抓取 GitHub Trending，对热门项目进行深度研究，生成结构化分析报告。

核心能力：
- 🔄 支持按日 / 周 / 月维度抓取热点项目
- 🔬 对单个仓库进行多轮深度研究（GitHub API + 网络搜索 + 文档分析）
- 📝 输出结构化报告（摘要 · 架构分析 · 竞品对比 · Mermaid 图表）
- 🖥️ 跨平台兼容（Trae · Claude Code · Cursor）

已生成报告（节选）：
- `browser-use`, `LightRAG`, `TradingAgents`, `deer-flow`, `BitNet` 等 40+ 项目深度报告
- 每日 / 周 / 月趋势汇总报告

→ [进入项目](./github-trending-analyzer/)

---

## 🛠️ 技能体系

各子项目均内置专属 Skill，可被 AI Agent 直接调用：

| Skill | 功能 | 所在项目 |
|-------|------|---------|
| `paper_analysis` | 论文7步深度分析法 | ai-learning |
| `knowledge_deep_dive` | AI概念5层理解模型 | ai-learning |
| `text_analysis` | 哲学文本深度分析法 | philosophy-learning |
| `concept_deep_dive` | 哲学概念5层理解模型 | philosophy-learning |
| `github-trending-analyzer` | 热点项目趋势分析 | github-trending-analyzer |
| `github-deep-research` | 单仓库多轮深度研究 | github-trending-analyzer |

---

## 🗺️ 整体学习理念

三个项目看似独立，实则共享同一套底层方法论：

```
提问  →  深度研究  →  结构化输出  →  持续迭代
```

AI 技术的进化、哲学的历史追问、开源世界的涌现——都遵循相同的规律：**能随时间积累的深度，才是真正的竞争力。**

---

*"能随算力扩展的通用方法，长期总是赢。" — Rich Sutton, The Bitter Lesson (2019)*

---

> 本仓库收录的学术论文 PDF 仅供个人学习使用，版权归原作者及出版机构所有。详见 [DISCLAIMER.md](./DISCLAIMER.md)。
