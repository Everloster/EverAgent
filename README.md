# EverAgent — 个人学习与研究工作台

EverAgent 收录 AI、计算机科学等领域的学习报告、阅读笔记和小型实验，也整理构建个人上下文（Personal Context）的方法与案例。

可以从这里查资料、运行教学实验，或跟着指南整理自己的项目记录，让 AI 按任务读取。已有实践的范围、结果和缺口集中在 [AI 学习与实践记录](./AI_PROGRESS.md)；这里不是可直接部署的个人助手。

![EverAgent 学习与研究全景图](./docs/assets/everagent-horizontal.jpg)

## 从哪里开始

| 想做什么 | 入口 |
|---|---|
| 找一篇报告阅读 | [完整报告索引](./docs/REPORT_INDEX.md) |
| 运行代码或小型实验 | [AI Practice](./ai-practice/README.md) |
| 从少量文件搭建自己的上下文 | [Personal Context 构建指南](./PERSONAL_CONTEXT.md) |
| 参考私有实践中可公开的经验 | [多设备 Context 案例](./PERSONAL_CONTEXT.md#真实脱敏案例多设备-agent-会话-context) |
| 看已有产出验证到了哪一步 | [AI 学习与实践记录](./AI_PROGRESS.md) |
| 使用 Coding Agent 参与研究 | [AGENTS.md](./AGENTS.md) |

## 怎么使用

阅读报告和笔记不需要安装工具。在本地查看或修改，可以先克隆：

```bash
git clone https://github.com/Everloster/EverAgent.git
cd EverAgent
```

运行实验时，按 [AI Practice 的说明](./ai-practice/README.md#快速开始)选择一个入口并配置依赖，不必安装所有实验环境。

使用 Coding Agent 时，先让它读取 `AGENTS.md`，再给出具体问题或材料。例如：“解释这篇论文的方法与局限”“检查这个开源项目的一条实现路径”“用最小实验比较两种方法”。协议中的 eacli、模型访问、联网检索和转写等工具需要另行配置，克隆本仓不会提供这些服务或认证。阅读指南和照着整理本地记录，不依赖这套运行环境。

## 内容怎样组织

- 各学习领域的 `reports/` 保存报告，`wiki/` 整理概念、实体与未解问题。
- 各领域的 `MAP.md` 记录覆盖范围和缺口；它不是掌握程度的评分。
- `ai-practice/` 保存 Notebook、脚本、实验笔记和部分历史输出。
- `docs/` 与 `scripts/` 保存写作约定、索引和检查工具。Agent 的指令分层见 [Context Engineering](./docs/CONTEXT_ENGINEERING.md)。

## 最近产出

<!-- AUTO-RECENT:START -->
| 日期 | 报告 | 领域 |
|------|------|------|
| 2026-10-25 | [菠萝健康派 × 师永刚：中美抗癌十年，就医路径、费用真相与「被看见」的病人](./podcast-learning/reports/2026-10-21_xiaoyuzhou-boluo-jiankang_shiyonggang-cn-us-cancer-decade.md) | 🎙️ Podcast Learning |
| 2026-10-25 | [晚点聊 184：Astra 之后，具身智能的护城河从大脑移到哪里](./podcast-learning/reports/2026-10-15_rss-wandian-latetalk_184-embodied-quarterly-26q3.md) | 🎙️ Podcast Learning |
| 2026-10-25 | [忽左忽右 510：侨批不是一封家书，而是一套跨国金融与亲缘基础设施](./podcast-learning/reports/2026-10-23_xiaoyuzhou-huzuo-huyou_ep510-thai-qiaopi-network.md) | 🎙️ Podcast Learning |
| 2026-10-25 | [张小珺 × Lindon Gao（Dyna Robotics）：机器人长跑里的闭环、推论与「不犯错的 CEO」包袱](./podcast-learning/reports/2026-10-15_xiaoyuzhou-zhangxiaojun_vol154-dyna-lindon.md) | 🎙️ Podcast Learning |
| 2026-10-25 | [声东击西 #408：互联网增长的红利、代价与一个人的十年自我重建](./podcast-learning/reports/2026-10-22_rss-shengdong-jixi_ep408-lijing-internet-growth-self-reconstruction.md) | 🎙️ Podcast Learning |
<!-- AUTO-RECENT:END -->

[浏览全部报告 →](./docs/REPORT_INDEX.md)

## 项目全景

下表由 `python3 scripts/reindex.py` 生成；数量表示已收录的文件，不表示每篇都通过了同一标准的复核。

<!-- AUTO-OVERVIEW:START -->
| 项目 | 报告 | Wiki(概念/实体/综合) |
|------|------|----------------------|
| 🤖 [AI Learning](./ai-learning/) | 148 篇 | 54/30/1 |
| 💻 [CS Learning](./cs-learning/) | 33 篇 | 24/17/1 |
| 📚 [Philosophy Learning](./philosophy-learning/) | 22 篇 | 20/14/1 |
| 🧠 [Psychology Learning](./psychology-learning/) | 17 篇 | 13/13/0 |
| 🧬 [Biology Learning](./biology-learning/) | 18 篇 | 14/9/0 |
| ⚗️ [AI Practice](./ai-practice/) | 10 篇 | 9/1/0 |
| 🎙️ [Podcast Learning](./podcast-learning/) | 103 篇 | 58/54/0 |
| 🔭 [GitHub Research](./github-trending-analyzer/) | 124 篇 | 0/0/0 |
| 🏄 [Web Surfing](./web-surfing/) | 47 篇 | 0/0/0 |
<!-- AUTO-OVERVIEW:END -->

## 阅读时需要注意

报告会区分原始资料、来源方的主张和分析推断。较新的重要报告附有证据账本与独立模型复核记录，历史材料的验证程度并不一致。具体方法见 [研究方法论](./METHODOLOGY.md)、[报告流程](./docs/REPORT_WORKFLOW.md)和[质量检查说明](./docs/REPORT_QUALITY_GATE.md)。

实验结果只适用于记录中的数据、实现与环境。缩尺模拟不能替代真实模型训练，单次评估也不能证明长期效果；可核对的例子与缺口集中在 [AI_PROGRESS.md](./AI_PROGRESS.md)。

私人对话、设备、账号、网络和访问入口不应进入公开仓。相关经验只保留可公开的模式与证据边界，见[私有经验的公开处理方式](./PERSONAL_CONTEXT.md#10-私有经验怎样安全进入公开仓)。公开摘要不等于原始数据开放，也不构成匿名性保证。

早期多 Agent 编排框架保存在 `legacy-v1-multiagent` 分支；当前仓库以学习资料和实验为主。安全与协作约定见 [PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md)。

仓库中的学术论文 PDF 仅供个人学习使用，版权归原作者及出版机构所有。详见 [DISCLAIMER.md](./DISCLAIMER.md)。
