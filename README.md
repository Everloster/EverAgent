# 🧠 EverAgent — 个人学习与研究工作台

> 用 AI Agent 驱动的个人知识体系，覆盖 AI 技术、计算机科学、哲学思想、心理学、生命科学与开源生态
> 创建日期：2026-03-23 | 最后更新：2026-03-26（自动任务：Raft论文分析 + 柏拉图洞穴比喻文本分析）

> **AI/Agent 使用本仓库？** → 请直接阅读 [AGENTS.md](./AGENTS.md)，本文件供人类阅读。

---

## 项目全景

EverAgent 是以 AI Agent 为核心工具的个人知识库，通过系统化学习路径、深度分析报告和自动化工具，将学习从"被动积累"变为"主动建构"。目前包含 **6 个子项目**：

| 项目 | 领域 | 内容量 | 状态 |
|------|------|--------|------|
| [🤖 AI Learning](./ai-learning/README.md) | 人工智能技术·论文精读·技术深度报告 | 15 篇精读 + 5 篇深度报告 | 🟢 活跃 |
| [💻 CS Learning](./cs-learning/README.md) | 计算机科学·系统·算法·分布式 | 10 篇精读 + 1 篇人物图谱 | 🟡 建设中 |
| [📚 Philosophy Learning](./philosophy-learning/README.md) | 西方哲学史·经典文本·概念辨析 | 3 篇文本分析 + 1 篇论文分析 + 1 篇人物图谱 | 🟡 建设中 |
| [🧠 Psychology Learning](./psychology-learning/README.md) | 心理学·经典实验精读·行为经济学 | 2 篇精读 + 1 篇人物图谱 | 🟡 建设中 |
| [🧬 Biology Learning](./biology-learning/README.md) | 时间生物学·睡眠科学·运动生理学 | 1 篇概念报告 | 🔵 初始化 |
| [📈 GitHub Trending Analyzer](./github-trending-analyzer/README.md) | 开源热点追踪·Repo 深度研究 | 58 篇 Repo 报告 + 7 篇汇总 | 🟢 活跃 |

---

## 工作区校验

仓库已提供一个轻量级校验脚本，用来检查：

- 学习型子项目报告的 YAML frontmatter 是否完整
- `README.md` / `CONTEXT.md` 中的相对链接是否可达
- 各项目 `skills` 是否回链到共享模板
- 仓库里是否残留 `.DS_Store` 之类的卫生问题

运行方式：

```bash
python3 scripts/validate_workspace.py
```

## 整体学习理念

六个项目共享同一套底层方法论：

```
提问  →  深度研究  →  结构化输出  →  持续迭代
```

能随时间积累的深度，才是真正的竞争力。

---

*"能随算力扩展的通用方法，长期总是赢。" — Rich Sutton, The Bitter Lesson (2019)*

> 本仓库收录的学术论文 PDF 仅供个人学习使用，版权归原作者及出版机构所有。详见 [DISCLAIMER.md](./DISCLAIMER.md)。
