# 🧠 EverAgent — 个人学习与研究工作台

> 把“我想了解 X”变成可长期复用、可追溯的报告、实验和知识索引。
> AI 负责读原文、查证、运行必要实验与整理；我负责提出问题、阅读和继续追问。

![EverAgent 学习与研究全景图](./docs/assets/everagent-horizontal.jpg)

EverAgent 保存可以公开分享的知识资产；设备、网络和服务等私有上下文由并排的 `EverAgent-infra` 管理，并通过 eacli 按需读取。

## 直接这样用

| 你说 | EverAgent 会做什么 |
|---|---|
| “顶尖技术博客最近有什么更新？” | 扫描官方技术信源，筛选并解释最值得看的内容 |
| “把最值得看的 5 篇都做 AI 学习任务” | 阅读原文、交叉核验，形成可独立阅读的深度报告 |
| “这个 GitHub repo 值得用吗？” | 先快速讲清；明确要深挖时再研究源码、论文与竞品 |
| “小宇宙精选播客最近有什么更新？” | 检查新集，按需转写、核验并整理学习报告 |
| “顶尖技术播客最近有什么更新？” | 扫描中英文 SOTA AI 技术节目，过滤已学习单集并给出深挖优先级 |
| “用一个最小 Demo 讲清这项技术” | 运行真实代码，保存输出、失败记录与实验笔记 |
| “这个设备或服务出问题了，帮我查” | 转入私有基础设施仓实测、修复并沉淀档案 |

只需描述目标，Agent 会按意图选择项目和工作流。

## 最近产出

<!-- AUTO-RECENT:START -->
| 日期 | 报告 | 领域 |
|------|------|------|
| 2026-10-25 | [菠萝健康派 × 师永刚：中美抗癌十年，就医路径、费用真相与「被看见」的病人](./podcast-learning/reports/2026-10-21_xiaoyuzhou-boluo-jiankang_shiyonggang-cn-us-cancer-decade.md) | 🎙️ Podcast Learning |
| 2026-10-25 | [张小珺 × Lindon Gao（Dyna Robotics）：机器人长跑里的闭环、推论与「不犯错的 CEO」包袱](./podcast-learning/reports/2026-10-15_xiaoyuzhou-zhangxiaojun_vol154-dyna-lindon.md) | 🎙️ Podcast Learning |
| 2026-10-25 | [半拿铁 No.223：“莆田系”医事——从电线杆到手术台，以及一门擅长招徕却难建信誉的生意](./podcast-learning/reports/2026-10-21_xiaoyuzhou-bannatie_putian-medical-system-history.md) | 🎙️ Podcast Learning |
| 2026-10-25 | [vLLM 在 GB300 NVL72 上服务 DeepSeek-V4.1-Flash：P/D 分离 + Wide-EP 的机制拆解与口径核验](./ai-learning/reports/knowledge_reports/vLLM_DeepSeek-V4.1-Flash_PD分离与Wide-EP机架级服务_深度解析_20261025.md) | 🤖 AI Learning |
| 2026-10-25 | [vLLM Humming：量化推理 GEMM Kernel 库的设计、支持矩阵与证据边界](./ai-learning/reports/knowledge_reports/vLLM_Humming_量化推理Kernel库_深度解析_20261025.md) | 🤖 AI Learning |
<!-- AUTO-RECENT:END -->

[浏览全部报告 →](./docs/REPORT_INDEX.md)

## 项目全景

> 下表由 `python3 scripts/reindex.py` 自动生成。

<!-- AUTO-OVERVIEW:START -->
| 项目 | 报告 | Wiki(概念/实体/综合) |
|------|------|----------------------|
| 🤖 [AI Learning](./ai-learning/) | 144 篇 | 54/30/1 |
| 💻 [CS Learning](./cs-learning/) | 33 篇 | 24/17/1 |
| 📚 [Philosophy Learning](./philosophy-learning/) | 22 篇 | 20/14/1 |
| 🧠 [Psychology Learning](./psychology-learning/) | 17 篇 | 13/13/0 |
| 🧬 [Biology Learning](./biology-learning/) | 18 篇 | 14/9/0 |
| ⚗️ [AI Practice](./ai-practice/) | 10 篇 | 9/1/0 |
| 🎙️ [Podcast Learning](./podcast-learning/) | 96 篇 | 58/54/0 |
| 🔭 [GitHub Research](./github-trending-analyzer/) | 124 篇 | 0/0/0 |
| 🏄 [Web Surfing](./web-surfing/) | 47 篇 | 0/0/0 |
<!-- AUTO-OVERVIEW:END -->

## 质量如何保证

- **原始材料优先**：先读文章、论文、源码或转写，再写结论；新事实和关键数字必须可追溯。
- **证据与观点分开**：区分来源事实、作者主张和分析者推断，缺口明确标注。
- **独立质量门**：重要报告配套证据账本，由独立 Reviewer 复核并通过机器检查后完成。
- **按需加载上下文**：只读取当前任务需要的 Owner，避免旧提示、无关历史和私有信息污染结果。

研究原则见 [METHODOLOGY.md](./METHODOLOGY.md)，报告流程见 [REPORT_WORKFLOW.md](./docs/REPORT_WORKFLOW.md)，跨模型质量门见 [REPORT_QUALITY_GATE.md](./docs/REPORT_QUALITY_GATE.md)。

## 知识如何积累

- `reports/` 保存可以脱离对话阅读的长期产出。
- `wiki/` 连接概念、人物、机构、综合理解与未解问题。
- 知识学习项目通过 `PROFILE.md`、`MAP.md` 和 `CONTEXT.md` 记录读者偏好、覆盖缺口与已有产出；工具型项目采用自己的轻量结构。

工作循环很简单：

```text
提出问题 → AI 研究并归档 → 阅读报告 → 继续追问 → 更新长期理解
```

## 入口

| 目的 | 从这里开始 |
|---|---|
| 阅读已有成果 | [报告索引](./docs/REPORT_INDEX.md) |
| 让 Agent 在本仓工作 | [AGENTS.md](./AGENTS.md) |
| 首次拉取或换机 | [WORKSPACE_SETUP.md](./docs/WORKSPACE_SETUP.md) |
| 理解 Context 与 Harness 架构 | [CONTEXT_ENGINEERING.md](./docs/CONTEXT_ENGINEERING.md) |
| 查看提交、安全与协作规则 | [PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) |

EverAgent 2.0 采用知识优先架构。早期多 Agent 编排框架保存在 `legacy-v1-multiagent` 分支。

*“能随算力扩展的通用方法，长期总是赢。” — Rich Sutton, The Bitter Lesson (2019)*

> 仓库中的学术论文 PDF 仅供个人学习使用，版权归原作者及出版机构所有。详见 [DISCLAIMER.md](./DISCLAIMER.md)。
