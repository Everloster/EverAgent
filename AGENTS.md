# EverAgent — 主协议

> 个人学习工作台。AI 帮我快速研究一个新领域/概念，产出高质量报告，我抽空阅读。
> 本质是**知识库**，不是任务管理系统。AI 被「怎么做好研究」驱动，不被状态机协调。

---

## §0 定位

- **使用方式**：单用户、对话即学习。我说"帮我学 X"，AI 现场研究并归档。
- **核心资产**：各领域的 `reports/`（我读的东西）+ `wiki/`（知识索引）。
- **核心 IP**：[METHODOLOGY.md](./METHODOLOGY.md) — 先规定怎么读、怎么查、怎么验证，再谈输出。

---

## §1 项目注册表（4 类）

8 个子项目按**工作模式**归为 4 类。**按「意图」路由，不按「当前目录」路由**：识别用户想干什么 → 判定属于哪一类 → 读对应项目 `AGENTS.md` 独立工作。判不进 A–D 的，直接在 EverAgent 根目录处理（见 §1.5）。

### A 类 · 知识研究领域（5 个）— 对话启发式学习

| 领域 | 路径 | 内容 |
|------|------|------|
| AI/ML | `ai-learning/` | 论文精读·技术报告 |
| 计算机科学 | `cs-learning/` | 系统·算法·分布式 |
| 哲学 | `philosophy-learning/` | 世界哲学·文本分析（含中国哲学） |
| 心理学 | `psychology-learning/` | 经典实验·概念 |
| 生物学 | `biology-learning/` | 时间生物学·睡眠·运动生理 |

**工作流**：我说"帮我学 X"→ AI 现场研究 → 产出高质量报告 → 我读 → 追问循环（详见 §2）。

### B 类 · 代码实践（1 个）— 低成本 demo 与理解

| 项目 | 路径 | 内容 |
|------|------|------|
| AI 实践 | `ai-practice/` | 各类 AI 技术的低成本可运行实现 + 配套教学笔记 |

**工作流**：我说"帮我用最小 demo 理解 X"→ AI 写可运行代码 → 实际运行拿真实数值 → 写教学笔记（详见该项目 AGENTS.md）。

### C 类 · 播客学习（1 个）— 本地转写驱动

| 项目 | 路径 | 内容 |
|------|------|------|
| 播客 | `podcast-learning/` | 发链接 → 本地转写 → 润色 → 总结/讨论 → 报告 |

**工作流**：我发一个播客/视频链接 → AI 本地转写出原文（faster-whisper）→ 润色 → 总结或继续讨论 → 产出报告（详见该项目 AGENTS.md）。

### D 类 · 开源仓库研究（1 个）— 自带脚本与协议

| 项目 | 路径 | 内容 |
|------|------|------|
| 开源热点 | `github-trending-analyzer/` | 发 repo 链接 → 输出/更新研究报告；trending 日/周/月汇总 |

**工作流自成体系**（有自己的 TASK_PROTOCOL、验证脚本、命名规范），读该项目 `AGENTS.md` 独立执行，本次不改动其协议。

> 每个项目自包含：读该项目 `AGENTS.md` + 根 `METHODOLOGY.md` 即可独立工作。

---

## §1.5 路由与兜底（重要）

**路由靠意图，不靠 cwd。** 无论我把终端 cd 在哪，判定入口都是"这句话想干什么"：

```
我的请求
  ↓ 先按意图归类
  ├─ "帮我学/精读/深入 X"        → A 类 {domain}-learning
  ├─ "用最小 demo 跑通 X"        → B 类 ai-practice
  ├─ 发来播客/视频链接            → C 类 podcast-learning
  ├─ 发来 repo 链接 / trending    → D 类 github-trending-analyzer
  └─ A–D 都不匹配（杂事/工具/一次性调研/流程） → 直接在 EverAgent 根目录干活
```

**兜底（归不进 A–D 时）**：不新建"杂物"子项目，直接在根目录处理。默认遵守：

1. **搜索用最省钱有效的档位** — 见 [docs/SEARCH.md](./docs/SEARCH.md)（本机已装 `llm` + Gemini websearch，默认联网入口）。
2. **真读来源、标注证据** — 复用 METHODOLOGY §一/§二：不凭记忆下结论，事实带来源，推测标 `[推测]`；知识截止后的事实必须联网核实（§三）。
3. **安全铁律** — 复用 PROTOCOL_COMMON §A：不伪装身份、不提交密钥、领域隔离、冲突上报。
4. **一次性小事直接答，不留垃圾文件**；确有长期价值的产出，再考虑落成文件或按 §5 升级为正式领域。

**升级规则**：兜底的事若命中任一条，就**先建正式子项目/领域再继续**（按 §5，并登记到本表 + README）——① 同类请求出现 ≥3 次且形态稳定；② 需自带脚本/验证/命名规范；③ 产出需长期索引累积。反例（留在根目录即可）：查一个事实、临时格式转换、装一个工具、跑一条命令、做一张对照表。

---

## §2 对话即学习（A 类主流程）

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
B/C/D 三类各有特化工作流，见各自项目 `AGENTS.md`。

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
├── docs/                # PROTOCOL_COMMON（提交/安全规则）、SEARCH（搜索阶梯）、REPORT_METADATA、personal
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

- **搜索/查资料**：[docs/SEARCH.md](./docs/SEARCH.md) — 从最省钱有效档位起爬（本地 → `llm` Gemini websearch → WebSearch/Fetch → 专业 Skill）。
- **安全与防幻觉**：[docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §A — 未读内容禁止推测；数值必须有来源；不编造。
- **提交规范**：[docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §B/§C — commit 格式、push flow（`GIT_NO_OPTIONAL_LOCKS=1`）。
- **git 身份**：首次提交前 `python3 scripts/git_identity.py validate`，pre-commit hook 强制校验。
- **历史版本**：旧的多 Agent 编排框架（任务状态机/锁/事件溯源/Dashboard）归档在 `legacy-v1-multiagent` 分支。

---

## §5 新增领域

复制任一领域结构：`AGENTS.md` + `PROFILE.md` + `MAP.md` + `reports/` + `wiki/{concepts,entities,syntheses,open-questions.md}` + `skills/`，然后更新 §1 表格与 README。
