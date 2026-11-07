# everagent-core

公共 Go module：当前调用方的身份与模型证据、用户声明、会话组合、Git 原语和公开仓质量门。
可直接编译进 CLI，不依赖解释器、独立身份 helper 或相邻私仓。Go 版本与依赖由 `go.mod` / `go.sum` 固定。

当前源码为 `0.4.0-dev`；不是设备安装态或九类客户端均已验收的声明。
本次退役 Python core 和相关 wrapper，保留 `scripts/ecommit.sh`；已有设备安装副本须单独升级和验收。

## 入口

在公开仓根目录运行：

```bash
go -C packages/everagent-core run ./cmd/everagent-identity inspect --json
go -C packages/everagent-core run ./cmd/everagent-identity diagnose --json
scripts/ecommit.sh -m "[maintenance] global: 本次修改"
```

eacli 的完整会话入口为 `session current → diagnose → declare`；公共独立入口对应
`everagent-identity inspect → diagnose → declare`。自动核实失败先修可行的配置/读取路径，确实无法
取证才记录用户明确给出的 harness/form/model；公共 core 不拥有私有设备登记，不能自行认领设备。

公开质量检查不联网、不调用模型、不读取私仓：

```bash
# 只读预览未提交修改；提交器使用 index，CI 使用 head + 固定 base SHA。
go -C packages/everagent-core run -mod=readonly -trimpath -buildvcs=false ./cmd/ea-quality quick --scope worktree
# 更新生成区，不改报告正文或元数据。
go -C packages/everagent-core run ./cmd/ea-quality index --write
```

`quick` 按变更选择报告/Context/Go 回归；`full` 扩大检查。`context`、`privacy`、`links`、`index`、
`scripts`、`policy`、`catalog`、`report --report <仓内路径>`、`sampling` 是按问题使用的入口，
不要求每次全部运行。输出 JSON；失败非零。`go run` 本身将非零状态折叠为1，需区分参数错误时
使用构建后的 CLI；ecommit 已保留实际退出码。
`quick/full` 默认只返回检查状态、完整错误/告警计数和最多16条位置，错误优先；`--details` 展开全部诊断，
不因输出精简而跳过检查，也不把未展示的历史告警称为不存在。

## 所有权

| 内容 | Owner |
|---|---|
| 版本与会话组合 | `core.go`、`session.go` |
| 调用方进程、harness 与宿主 | `process*.go`、`identity.go`、`apps.go` |
| 有界读取配置 | `config.go`；`src/everagent_core/identity/readers.json` |
| 原生模型证据、声明及失效 | `observations*.go`、`declarations.go` |
| DSH 官方 shellEnv 插件 | `src/everagent_core/identity/dsh_plugin.mjs`；产品接口要求的 JS 适配，不运行 Python |
| JSON 形状 | `src/everagent_core/schemas/`；保留资产路径，不代表仍有 Python 包 |
| Git 参数、消息、双身份与 tree 核验 | `git.go` |
| 公开质量与快照 | `internal/publicquality/`；`cmd/ea-quality` |
| 公开提交绑定 | `cmd/ea-git`；`scripts/ecommit.sh` |
| 报告模型资格、评分与不可变版本 | [公开策略](../../config/report-quality-policy.json)；core 不复制另一套策略 |

Git Author 只认目标仓的策略，公开入口读取 index 中的 `config/git-policy.json`。提交前后复验
当前模型证据、Author 和 index；提交后再核对真实 commit。外部 hooksPath 不被替换。
消息和显式 trailer 沿用 Git 原生语义。push 绑定捕获的 SHA 与唯一实际目的地，读回匹配才算已核实。

质量门检查构建源码/依赖锁与待审快照一致；影响 core 时把同一模块快照导出到仓外 scratch 运行
Go test/vet，不使用未暂存的实现或自动下载工具。测试使用临时 HOME、最小环境和既有 Go 缓存，不继承
调用方的会话变量、认证环境或 SSH agent。该环境不是安全沙箱，源码绑定也不是对恶意检查器的防篡改证明。
生成索引逐文件原子替换，失败返回已写清单，不宣称多文件事务。

## 验证边界

```bash
go -C packages/everagent-core test ./...
go -C packages/everagent-core vet ./...
```

合成回归覆盖当前会话绑定、九类读取器的支持/未知边界、声明失效、Git 参数与 hook、公开隐私、
来源/复核 SHA、独立会话、报告范围与旧策略、转写和 Context。真实客户端、模型调用、设备安装及
跨平台运行仍需各自证据，交叉编译不等于实机通过。

OpenCode V2 目前只能核实 requested Model.Ref，不是 provider 返回型号；Cursor 只有 harness/声明
绑定。这些缺口保持 unknown/requested，不能仅凭配置放行提交。Context 检查会复验已登记报告和历史
行为记录，不执行新模型回放，也不把过期 A/B 结果当成本次改进证据。

完整契约见 [AGENT_SESSION](../../docs/AGENT_SESSION.md)、[Git 协议](../../docs/PROTOCOL_COMMON.md)
和 [报告质量门](../../docs/REPORT_QUALITY_GATE.md)。公开仓的学习、报告作者工具及既有实验脚本不属于
本 module；它们不是 Go 身份/提交/质量链的运行依赖。
