# 🧠 EverAgent — 个人学习与研究工作台

> 用 AI Agent 驱动的个人知识体系，覆盖 AI 技术、计算机科学、哲学思想、心理学、生命科学与开源生态
> 创建日期：2026-03-23 | 最后更新：2026-04-28（新增 EverAgent 项目海报）

> **AI/Agent 使用本仓库？** → 请直接阅读 [AGENTS.md](./AGENTS.md)，本文件供人类阅读。

![EverAgent launch poster](./docs/assets/everagent-launch-poster.png)

---

## 项目全景

<!--
NOTE: The project overview table below is generated.
Refresh it via: python3 scripts/task_board_aggregator.py --sync-readme
-->

<!-- PROJECT_OVERVIEW:START -->
EverAgent 是以 AI Agent 为核心工具的个人知识库，通过系统化学习路径、深度分析报告和自动化工具，将学习从"被动积累"变为"主动建构"。目前包含 **8 个子项目**：

| 项目 | 领域 | 报告量 | Wiki 页面 | 状态 |
|------|------|--------|-----------|------|
| [🤖 AI Learning](./ai-learning/README.md) | AI/ML 论文精读·技术报告 | 40 篇精读/文本 + 31 篇知识/概念报告 | 28 entities · 35 concepts | 🟢 |
| [💻 CS Learning](./cs-learning/README.md) | 计算机科学·系统·算法 | 24 篇精读/文本 + 6 篇知识/概念报告 | 13 entities · 22 concepts | 🟢 |
| [📚 Philosophy Learning](./philosophy-learning/README.md) | 西方哲学·文本分析 | 13 篇精读/文本 + 3 篇知识/概念报告 | 11 entities · 14 concepts | 🟡 |
| [🧠 Psychology Learning](./psychology-learning/README.md) | 心理学·经典实验 | 12 篇精读/文本 + 4 篇知识/概念报告 | 12 entities · 12 concepts | 🟢 |
| [🧬 Biology Learning](./biology-learning/README.md) | 时间生物学·睡眠·运动生理 | 11 篇精读/文本 + 4 篇知识/概念报告 | 9 entities · 11 concepts | 🟡 |
| [📈 GitHub Trending Analyzer](./github-trending-analyzer/README.md) | 开源热点·Repo 知识库 | 74 篇 Repo 报告 + 10 篇汇总报告 | — | 🟢 |
| [⚗️ AI Practice](./ai-practice/README.md) | ML 工程·代码实验·模型训练 | 7 篇教学笔记 | 1 entities · 9 concepts | 🟢 |
| [🎙️ Podcast Learning](./podcast-learning/README.md) | 播客内容学习与知识提取 | 1 篇文本 + 0 篇知识/概念报告 | 2 entities · 5 concepts | 🟢 |
<!-- PROJECT_OVERVIEW:END -->

---

## 工作区校验

仓库已提供一个轻量级校验脚本，用来检查：

- 学习型子项目报告的 YAML frontmatter 是否完整
- `README.md` / `CONTEXT.md` 中的相对链接是否可达
- 各项目 `skills` 是否回链到共享模板
- 仓库里是否残留 `.DS_Store` 之类的卫生问题

运行方式：

```bash
# 全局校验（pre-commit）
python3 scripts/validate_workspace.py

# 一键自检（校验 + 执行协议自检 + 聚合器 dry-run）
python3 scripts/everagent.py doctor

# 巡检 registry / task / lock 是否漂移
python3 scripts/everagent.py audit

# 安全对账：同步视图，并按需清理超时任务
python3 scripts/everagent.py reconcile
python3 scripts/everagent.py reconcile --abandon-stale

# 自进化引擎：分析执行数据，自动发现优化机会
python3 scripts/everagent.py evolve --days 7 --dry-run

# 实时 Dashboard：Web 可视化任务状态与事件流
python3 scripts/everagent.py dashboard --port 8080

# 安装本仓库 pre-commit hook（可选）
python3 scripts/everagent.py hooks install

# 清理超时任务（先巡检，再按需落地 abandon）
python3 scripts/everagent.py sweep-stale-tasks
python3 scripts/everagent.py sweep-stale-tasks --apply

# 任务执行校验（Agent 在领取/完成任务时调用）
python3 scripts/execution_validator.py --mode=input --task-id=T001    # 领取前
python3 scripts/execution_validator.py --mode=output --task-id=T001   # 完成后
```

### Task Board 汇总

Task Board 视图由 `scripts/task_board_aggregator.py` 自动生成：

```bash
python3 scripts/task_board_aggregator.py --dry-run   # 预览
python3 scripts/task_board_aggregator.py              # 生成视图
```

### 新项目创建

新增子项目可通过自动化脚本创建：

```bash
python3 scripts/create_project.py --project={name} --domain={domain} --agent-name={AgentName}
```

---

## Wiki 知识网络

每个学习子项目内置 `wiki/` 层，采用 **Karpathy 持久化 Wiki 模式**——每次摄入新报告后自动更新，形成跨报告的知识图谱：

```
{project}/wiki/
├── index.md       ← 内容目录，每次 ingest 后更新
├── log.md         ← 追加式操作日志
├── entities/      ← 人物 / 机构页面
├── concepts/      ← 核心概念与技术页面
└── syntheses/     ← 多概念合成查询归档
```

> Wiki 是报告的"索引层"：想快速定位某个概念或人物，先读 `wiki/index.md`，再深入对应报告。

---

## 整体学习理念

七个项目共享同一套底层方法论：

```
提问  →  深度研究  →  结构化输出  →  持续迭代
```

能随时间积累的深度，才是真正的竞争力。

---

*"能随算力扩展的通用方法，长期总是赢。" — Rich Sutton, The Bitter Lesson (2019)*

> 本仓库收录的学术论文 PDF 仅供个人学习使用，版权归原作者及出版机构所有。详见 [DISCLAIMER.md](./DISCLAIMER.md)。
