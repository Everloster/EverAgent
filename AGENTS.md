# EverAgent — 主协议

> 个人学习工作台。AI 帮我快速研究一个新领域/概念，产出高质量报告，我抽空阅读。
> 本质是**知识库**，不是任务管理系统。AI 被「怎么做好研究」驱动，不被状态机协调。

---

## §0 定位

- **使用方式**：单用户、对话即学习。我说"帮我学 X"，AI 现场研究并归档。
- **核心资产**：各领域的 `reports/`（我读的东西）+ `wiki/`（知识索引）。
- **核心 IP**：[METHODOLOGY.md](./METHODOLOGY.md) — 先规定怎么读、怎么查、怎么验证，再谈输出。

---

## §1 领域注册表

| 领域 | 路径 | 内容 |
|------|------|------|
| AI/ML | `ai-learning/` | 论文精读·技术报告 |
| 计算机科学 | `cs-learning/` | 系统·算法·分布式 |
| 哲学 | `philosophy-learning/` | 世界哲学·文本分析（含中国哲学） |
| 心理学 | `psychology-learning/` | 经典实验·概念 |
| 生物学 | `biology-learning/` | 时间生物学·睡眠·运动生理 |
| ML 工程 | `ai-practice/` | 代码实验·教学笔记 |
| 播客 | `podcast-learning/` | 播客内容学习 |
| 开源热点 | `github-trending-analyzer/` | Repo 研究（自动化工具，自带脚本） |

每个领域自包含：读该领域 `AGENTS.md` + `METHODOLOGY.md` 即可独立工作。

---

## §2 对话即学习（主流程）

```
我："帮我学 X" / "深入 Y" / "上次那个继续"
  ↓
AI：1. 识别领域 → 读该领域 AGENTS.md
    2. 读 PROFILE.md（我会什么、偏好）+ MAP.md（覆盖与缺口）+ wiki/open-questions.md
    3. 查 wiki/concepts/ 与 reports/：已有则深化，没有则新建
    4. 按 METHODOLOGY 做研究：真读原文、查证、标注证据
    5. 写报告到 reports/，结尾必带「思考与追问」三问
    6. 沉淀：更新 wiki、未解问题汇入 open-questions、更新 PROFILE/MAP
    7. 自检：lint_evidence.py + reindex.py
  ↓
我：抽空读报告 → 有新问题继续对话 → 循环
```

没有任务领取、状态迁移、并发锁。追问已有主题时续写原报告，不另开新文件。

---

## §3 目录约定

```
EverAgent/
├── AGENTS.md            # 本文件
├── METHODOLOGY.md       # 通用研究方法论（强制）
├── README.md            # 人类导航（含自动生成的报告计数）
├── scripts/
│   ├── reindex.py       # 重建 README 报告/wiki 计数
│   ├── lint_evidence.py # 证据密度自检（非阻塞）
│   └── git_identity.py  # 提交身份校验
├── docs/                # PROTOCOL_COMMON（提交/安全规则）、REPORT_METADATA、personal
└── {domain}-learning/
    ├── AGENTS.md        # 领域边界 + 特化（~50 行）
    ├── PROFILE.md       # 学习者画像
    ├── MAP.md           # 领域地图（覆盖与缺口）
    ├── reports/         # 报告产出
    ├── wiki/            # concepts/ entities/ syntheses/ open-questions.md
    └── skills/          # 领域特化研究模板
```

---

## §4 全局规则

- **安全与防幻觉**：[docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §A — 未读内容禁止推测；数值必须有来源；不编造。
- **提交规范**：[docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §B/§C — commit 格式、push flow（`GIT_NO_OPTIONAL_LOCKS=1`）。
- **git 身份**：首次提交前 `python3 scripts/git_identity.py validate`，pre-commit hook 强制校验。
- **历史版本**：旧的多 Agent 编排框架（任务状态机/锁/事件溯源/Dashboard）归档在 `legacy-v1-multiagent` 分支。

---

## §5 新增领域

复制任一领域结构：`AGENTS.md` + `PROFILE.md` + `MAP.md` + `reports/` + `wiki/{concepts,entities,syntheses,open-questions.md}` + `skills/`，然后更新 §1 表格与 README。
