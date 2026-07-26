# EverAgent — 主协议

> 个人学习工作台。AI 帮我快速研究一个新领域/概念，产出高质量报告，我抽空阅读。
> 本质是**知识库**，不是任务管理系统。AI 被「怎么做好研究」驱动，不被状态机协调。

---

## §0 定位

- **使用方式**：单用户、对话即学习。我说"帮我学 X"，AI 现场研究并归档。
- **核心资产**：各领域的 `reports/`（我读的东西）+ `wiki/`（知识索引）。
- **核心 IP**：[METHODOLOGY.md](./METHODOLOGY.md) — 先规定怎么读、怎么查、怎么验证，再谈输出。

---

## §1 项目注册表（6 类）

10 个子项目按**工作模式**归为 6 类。**按「意图」路由，不按「当前目录」路由**：识别用户想干什么 → 判定属于哪一类 → 读对应项目 `AGENTS.md` 独立工作。判不进 A–F 的，直接在 EverAgent 根目录处理（见 §1.5）。

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

**工作流**：我发一个播客/视频链接 → AI 本地转写出原文（whisper.cpp）→ 润色 → 总结或继续讨论 → 产出报告（详见该项目 AGENTS.md）。

### D 类 · 开源仓库研究（1 个）— 自带脚本与协议

| 项目 | 路径 | 内容 |
|------|------|------|
| 开源热点 | `github-trending-analyzer/` | 发 repo 链接 → 输出/更新研究报告；trending 日/周/月汇总 |

**工作流自成体系**（有自己的 TASK_PROTOCOL、验证脚本、命名规范），读该项目 `AGENTS.md` 独立执行，本次不改动其协议。

### E 类 · 上网冲浪（1 个）— opencli 驱动 + 站点技能沉淀

| 项目 | 路径 | 内容 |
|------|------|------|
| 帮我上网 | `web-surfing/` | 发上网需求 → 以 `opencli` 为主力抓公开数据 → 产出清单/报告；常访问的站点沉淀成可复用技能 |

**工作流**：我说"帮我上 X 网站看看 / 抓一下 Y" → **先查复用**（本项目沉淀过？opencli 有适配器？agent-reach 覆盖？）→ 有则复用、无则 `opencli browser` 直驱 → 只读公开数据产出报告 → 这站以后还会来就沉淀成 `skills/site-{name}/`（详见该项目 AGENTS.md）。

### F 类 · 基础设施与设备（1 个）— 修复驱动 + 档案沉淀

| 项目 | 路径 | 内容 |
|------|------|------|
| 基础设施与设备 | `infra/` | VPS/代理网络 + 各终端设备的安装、修复、排障；一设备一档 |

**工作流**：我说"电脑/设备 X 有问题 / 看看这台机器" → 判型（VPS/代理网络 → 根 `DeviceNode.md`；终端设备 → `infra/devices/{hostname}.md`）→ 实测修复 → 命令级可复现沉淀到对应档案（详见 `infra/AGENTS.md`）。

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
  ├─ "帮我上 X 网站/抓一下 Y/整理清单" → E 类 web-surfing（opencli 驱动）
  ├─ "电脑/设备 X 有问题 / 看看这台机器" → F 类 infra（VPS/代理网络 → 根 DeviceNode.md；终端设备 → infra/devices/）
  └─ A–F 都不匹配（杂事/工具/一次性调研/流程） → 直接在 EverAgent 根目录干活
```

**兜底（归不进 A–F 时）**：不新建"杂物"子项目，直接在根目录处理。默认遵守：

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
B/C/D/E 各类有特化工作流，见各自项目 `AGENTS.md`。

---

## §3 目录约定

```
EverAgent/
├── AGENTS.md            # 本文件
├── METHODOLOGY.md       # 通用研究方法论（强制）
├── README.md            # 人类导航（含自动生成的报告计数）
├── scripts/
│   ├── reindex.py       # 重建 README 计数 + docs/REPORT_INDEX.md 阅读索引
│   ├── lint_evidence.py # 证据密度自检（非阻塞）
│   ├── git_identity.py  # 提交身份校验（Committer + Author 双身份）
│   └── ecommit.sh       # 双身份提交包装（Author=Everloster）
├── docs/                # PROTOCOL_COMMON（提交/安全规则）、SEARCH（搜索阶梯）、REPORT_METADATA、REPORT_INDEX（自动生成）、personal
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

- **交流语言**：整个项目过程与用户对话一律用**中文**（含解释、追问、报告正文、commit 描述）。代码、命令、专有名词、原文引用保持原样。
- **搜索/查资料**：[docs/SEARCH.md](./docs/SEARCH.md) — 从最省钱有效档位起爬（本地 → `llm` Gemini websearch → WebSearch/exa → firecrawl MCP → opencli；各设备的实际搜索能力见 `infra/devices/` 搜索栈）。
- **安全与防幻觉**：[docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §A — 未读内容禁止推测；数值必须有来源；不编造。
- **提交规范**：[docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §B/§C — commit 格式、push flow（`GIT_NO_OPTIONAL_LOCKS=1`）。
- **git 身份**：提交一律走 `scripts/ecommit.sh`（自动注入 Author=Everloster 双身份）；pre-commit hook 强制校验 Committer 与 Author，裸 `git commit` 未设 `GIT_AUTHOR_*` 会被拦截。
- **历史版本**：旧的多 Agent 编排框架（任务状态机/锁/事件溯源/Dashboard）归档在 `legacy-v1-multiagent` 分支。
- **兴趣确认**：各领域 `wiki/open-questions.md` 是历史快照 ≠ 当前兴趣。用户未指定明确方向的活儿，动手前先习惯性问一句最近的学习兴趣和方向；确认结果写回各领域 `MAP.md` 优先级队列（2026-07-20 确立）。
- **token 纪律（2026-07-21 确立）**：报告质量优先、用户当前兴趣与方向优先。wiki 维护类工作（lint 健康检查/批量重构回填/图谱与索引优化）一律 **hold**，除非用户明确要求；wiki 只在报告产出过程中顺带沉淀，不为 wiki 而 wiki。

---

## §4.5 基础设施与设备：自建 VPS（DeviceNode）+ F 类 infra/

本工作台管理**一台 AWS Lightsail VPS**（东京 / Ubuntu 24.04），用途：自建代理节点（VLESS+Reality，官方 Xray-core + nginx 订阅链接，供科学访问 AI 服务）+ 备用。终端设备维护自 2026-07-26 起升级为 **F 类子项目 `infra/`**。

- **设备维护（F 类）**：协议 [infra/AGENTS.md](./infra/AGENTS.md)；设备档案 `infra/devices/{hostname}.md`（首档 DeviceNode）。设备出问题先读对应档案再动手。
- **档案**：[DeviceNode.md](./DeviceNode.md) — 实例规格、静态 IP、SSH 方式、Xray-core 节点（443 经 nginx SNI 分流）、防火墙端口、订阅链接服务、规则维护、域名管理（<redacted-domain>）、Tailscale 节点与 DERP 中继、运维待办、设备联动摘要。跨设备接手先读它。
- **配置模板**：[infra/DeviceNode/clash-config.template.yaml](./infra/DeviceNode/clash-config.template.yaml) — 去密钥的 Clash 配置模板（占位符 + rule-providers 开源规则集），改规则从这里改再同步到服务端。
- **敏感信息不入库**：SSH 私钥、节点 UUID/Reality 密钥、**订阅链接**等只存个人密码库，`DeviceNode.md` 与模板仅记录非敏感信息。订阅链接等同密码，泄露即重新生成。
- **成本铁律**：按量付费（非免费套餐），勿跑 BT/DHT 等大流量任务；建议设 AWS Budget 告警。不用时记得 Terminate + 释放静态 IP 止血。

---

## §4.6 备忘：Karpathy 的 LLM Wiki

- 原文（idea file）：<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f> — EverAgent 的「原始资料 → reports → wiki → AGENTS.md schema」结构即此模式的多领域实例。
- 改进版 gist（可加置信度标注与 supersession「论断被新证据取代」机制）：<https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2>
- 生态清单：<https://github.com/gavischneider/awesome-llm-wiki>；最火的成品实现 <https://github.com/nashsu/llm_wiki>（桌面应用）。
- **待办（暂缓）**：wiki 健康检查（lint：矛盾/陈旧/孤儿页/supersession）未制度化。当前报告质量优先，等报告足够好、编译出的 wiki 才值得维护，届时回来补这条（2026-07-21 记）。

---

## §5 新增领域

复制任一领域结构：`AGENTS.md` + `PROFILE.md` + `MAP.md` + `reports/` + `wiki/{concepts,entities,syntheses,open-questions.md}` + `skills/`，然后更新 §1 表格与 README。
