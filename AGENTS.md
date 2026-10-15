# EverAgent — 主协议

<!-- BEGIN MANAGED EACLI TOKEN PLAN POLICY -->
## Token Plan-first（由 everagentcli 管理）

对联网搜索、网页读取、公开 GitHub 仓库、图像/视频理解、结构化数据和媒体生成任务，Agent **必须先走 eacli 的三家 Token Plan 能力面**：

1. 先用 `eacli tokenplan catalog --json` 识别 canonical capability；用 `eacli tool select --capability <id> --device auto --json` 获取 provider/device 选择证据。
2. 实际调用用 `eacli tool invoke --capability <id> --input-json ... --device auto --request-id <stable-id> --json`；安装与认证状态用 `eacli tokenplan doctor|verify --device all --json`。
3. 当 typed capability 已存在时，不直接绕过 eacli 调 `mcporter`、provider MCP、`mmx` 或供应商私有参数。eacli 不可用或尚未覆盖时才允许最小降级，并记录原因；有时间应优先修 eacli。
4. 凭据只在最终执行设备本地解析，禁止写入 prompt、argv、RPC、仓库或结果。只读能力才允许按 catalog 自动 fallback；生成类任务禁止自动重放。
5. Agent 启动时必须保留项目 context-file 加载；禁止使用跳过项目指令的参数。Claude Code 通过仓库 `CLAUDE.md` 的 `@AGENTS.md` 导入本策略。

这是默认执行与审计策略，不是安全沙箱；用户明确指令、仓库安全红线和授权等级始终优先。

## Personal Context-first（由 everagentcli 管理）

当任务涉及已经积累的个人设备、网络、服务、项目或学习资料时，Agent **先取最小上下文，再读 owner**：

1. 先用 `eacli context catalog --json` 确认领域、唯一 owner、敏感级别与现有 typed entry。
2. 已知领域用 `eacli context get --domain <id> --json`；需要定位资料用 `eacli context search --query <text> --json`，不得默认通读整个仓库或巨型档案。
3. 结果中的仓库相对路径与 SHA-256 是 provenance，不是第二份事实；需要修改时仍回到 owner 文件并遵守该仓协议。
4. `EverAgent-infra` 私有上下文不得复制进公开仓；CLI 不可用时才最小化直接读取 owner，并记录原因。
5. `eacli context verify --repo all --json` 用于检查目录、owner、来源与章节漂移；它只读且不自动修复。
<!-- END MANAGED EACLI TOKEN PLAN POLICY -->

> 个人学习与研究工作台。核心资产是可独立阅读、可追溯的报告，以及由报告沉淀出的知识索引。

## §0 核心入口

- 研究证据与写作方法：[METHODOLOGY.md](./METHODOLOGY.md)
- 报告任务的统一流程与完成定义：[docs/REPORT_WORKFLOW.md](./docs/REPORT_WORKFLOW.md)
- Context 分层、ACE 增量更新与评估：[docs/CONTEXT_ENGINEERING.md](./docs/CONTEXT_ENGINEERING.md)
- 安全、提交与 push 规则：[docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md)
- 报告元数据：[docs/REPORT_METADATA.md](./docs/REPORT_METADATA.md)

## §1 按意图路由

路由看用户意图，不看当前目录。确定目标项目后，只读该项目的 `AGENTS.md` 和任务实际需要的资料。

| 类 | 意图 | 项目 | 默认产出 |
|---|---|---|---|
| A | 学习、精读、深入研究概念/论文/文章 | `ai-learning` / `cs-learning` / `philosophy-learning` / `psychology-learning` / `biology-learning` | 研究报告 |
| B | 用最小可运行 demo 理解 AI 技术 | `ai-practice` | 代码、真实输出、实验笔记 |
| C | 播客或视频学习 | `podcast-learning` | 静默转写、润色稿、报告 |
| D | GitHub repo 或 trending | `github-trending-analyzer` | 仅链接时口头介绍；明确深挖时报告 |
| E | 查网站、抓公开数据、整理清单 | `web-surfing` | 直接答复；有长期价值时报告 |
| F | 设备、网络、服务和基础设施 | `../EverAgent-infra/` | 修复与私有档案 |

无法归类的临时任务直接在根目录完成。只有同类请求反复出现、需要专用脚本或需要长期索引时，才新增项目。

## §2 Context 加载

1. 先读当前项目 `AGENTS.md`，再按其中的条件链接读取材料。
2. 涉及已有个人或项目积累时，按顶部 Personal Context-first 获取最小切片；不要默认通读整个仓库、全部报告或全部 wiki。
3. `PROFILE.md` 只在需要适配读者或记录用户明确偏好时读写；`MAP.md` 只在判断覆盖与更新长期方向时读写；`open-questions.md` 只在续接或沉淀问题时读取。
4. 报告任务使用 repo skill [`everagent-report`](./.agents/skills/everagent-report/SKILL.md)。复杂体裁只加载对应领域 skill，不并读所有模板。
5. 模型特有的主动性、测试范围、委派或写作补丁放在运行时配置或小型 overlay；仓库协议保留模型无关的不变量。

## §3 报告任务

用户明确要求“研究 / 精读 / 深挖 / 出报告”时，按 [REPORT_WORKFLOW.md](./docs/REPORT_WORKFLOW.md) 完成研究、写作、最小知识沉淀和质量检查。一次性问答不为归档而归档。

完成报告后运行：

```bash
python3 scripts/reindex.py
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

领域有额外审计器时一并运行。历史报告的告警作为修复队列；当前任务新增的错误必须清零。

## §4 全局不变量

- **语言**：项目过程、解释、报告正文和 commit 描述使用中文；代码、命令、专有名词与原文引用保持原样。
- **证据**：未读内容不得推测；数字和知识截止后的事实必须有可复核来源；推断标 `[推测]` 或 `[待验证]`。
- **安全**：遵守 [PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §A；公开仓不得写入私有设备、账号、网络或凭据信息。
- **权限**：本地、可逆、只读和用户已明确授权的步骤可持续推进；发布、外部写入、生产数据变更和不可逆操作按实际风险取得授权。
- **提交**：一律使用 `scripts/ecommit.sh`；身份识别为 `*-unknown` 时禁止提交。commit 与 push 流程见 [PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §B/§C。
- **工具选型**：做工具或代码前依次检查官方 CLI、官方 MCP/SDK、成熟开源方案，再考虑自写；联网能力遵守顶部 Token Plan-first。
- **知识维护**：wiki 只随报告或明确请求做最小更新，不单独开展批量美化。PROFILE 只记录用户真实表达。
- **外部方法**：报告证据写作可按需读取 `docs/external-skills/scientific-agent-skills/scientific-writing/SKILL.md`；提出可证伪假说时读取同目录 `hypothesis-generation/SKILL.md`。

## §5 目录与领域扩展

项目结构和人类导航见 [README.md](./README.md)。A 类领域保持：

```text
{domain}-learning/
├── AGENTS.md
├── PROFILE.md
├── CONTEXT.md
├── MAP.md
├── reports/
├── wiki/
└── skills/
```

新增领域时复制该骨架，并更新本文件路由表与 README。F 类内容始终留在并排私有仓 `../EverAgent-infra/`。

> 旧多 Agent 状态机、锁和 Dashboard 已归档在 `legacy-v1-multiagent` 分支；当前仓库保持知识优先。
