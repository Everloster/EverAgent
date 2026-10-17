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

以下文件是条件路由，不是启动时的必读清单：

| 当前任务 | 读取的唯一公共 Owner |
|---|---|
| 研究证据、来源与写作判断 | [METHODOLOGY.md](./METHODOLOGY.md) 的相关章节 |
| 新建、续写或审计长期报告 | [`everagent-report`](./.agents/skills/everagent-report/SKILL.md) |
| 报告流程与完成定义 | [REPORT_WORKFLOW.md](./docs/REPORT_WORKFLOW.md) |
| 证据账本、独立复核与模型升级 | [REPORT_QUALITY_GATE.md](./docs/REPORT_QUALITY_GATE.md) |
| Context 或 Harness 调整 | [CONTEXT_ENGINEERING.md](./docs/CONTEXT_ENGINEERING.md) |
| commit、push 或安全边界 | [PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) |
| 新增或迁移报告元数据 | [REPORT_METADATA.md](./docs/REPORT_METADATA.md) |

## §1 按意图路由

路由看用户意图，不看当前目录。确定项目后读取该项目 `AGENTS.md`；未命中 A–F 的任务在根目录完成。

| 类 | 意图 | 项目 | 默认产出 |
|---|---|---|---|
| A | 学习、精读、深入研究概念/论文/文章 | `ai-learning` / `cs-learning` / `philosophy-learning` / `psychology-learning` / `biology-learning` | 研究报告 |
| B | 用最小可运行 demo 理解 AI 技术 | `ai-practice` | 代码、真实输出、实验笔记 |
| C | 播客或视频学习 | `podcast-learning` | 静默转写、润色稿、报告 |
| D | GitHub repo 或 trending | `github-trending-analyzer` | 裸链接口头介绍；明确深挖才写报告 |
| E | 查网站、抓公开数据、整理清单 | `web-surfing` | 直接答复；有长期价值时归档 |
| F | 设备、网络、服务和基础设施 | `../EverAgent-infra/` | 修复与私有档案 |

只有同类请求反复出现、需要专用脚本或需要长期索引时，才新增项目。

## §2 Context 加载

1. 先读项目 `AGENTS.md`，再选一个与任务直接匹配的 skill 或 reference；够用即停。
2. 涉及既有积累时按顶部 Personal Context-first 获取最小切片，不默认扫描全部报告、wiki 或 skills。
3. `PROFILE.md` 只用于适配读者或记录用户明确偏好；`MAP.md` 只用于覆盖判断与长期方向；`open-questions.md` 只用于续接或沉淀问题。
4. 模型补丁不写入公共 context；有稳定 overlay 时按需注入，否则依赖机器策略与行为评估。

## §3 执行边界

- 主题、来源或交付物明确时直接推进，不停在能力确认、列计划或首版实现。开放式学习请求若缺少方向且选题会实质改变结果，先问一次当前兴趣；确认后按需更新 `MAP.md`。
- 开始前在当前会话中明确目标、交付物、必要检查和停止条件；无需把一次性任务合同写入仓库。
- 只有缺失信息会实质改变结果，或外部写入、发布、生产数据、权限扩大及不可逆操作尚未获授权时才询问。
- 最终外部发布仍需确认时，先完成本地可审阅产物与必要检查，再停在发布动作前。
- 验证范围与改动风险匹配：先做受影响检查；只有失败、跨模块影响或未解决风险才扩大，不重复运行已通过且未受影响的检查。
- 用户明确指令优先于 skill 的一般建议。若某个 skill 迫使任务暂停、偏离或留有未完成项，指出具体文件和适用规则。

## §4 全局不变量

- **语言**：项目沟通、报告正文和 commit 描述使用中文；代码、命令、专有名词与原文引用保持原样。
- **证据**：未读内容不得推测；数字和知识截止后的事实必须可追溯；推断标 `[推测]` 或 `[待验证]`。
- **安全**：遵守 [PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §A；公开仓不得写入私有设备、账号、网络或凭据信息。
- **提交**：一律使用 `scripts/ecommit.sh`；身份识别为 `*-unknown` 时禁止提交。
- **工具**：做工具或代码前依次检查官方 CLI、官方 MCP/SDK、成熟开源方案，再考虑自写；联网遵守顶部 Token Plan-first。
- **知识维护**：wiki 只随报告或明确请求做最小更新；PROFILE 只记录用户真实表达。

项目结构与人类导航见 [README.md](./README.md)。F 类细节始终留在并排私有仓 `../EverAgent-infra/`。
