# everagent-core

公共Go模块：当前调用方的身份/模型证据、用户声明、会话组合、Git原语、公开内容保护与可选审查工具。
当前源码为`0.6.0`，不代表已发布或设备已安装。Go版本与依赖由`go.mod`、`go.sum`固定，不依赖Python、独立身份helper或相邻私仓。

## 日常入口

```bash
go -C packages/everagent-core run ./cmd/everagent-identity inspect --json
go -C packages/everagent-core run ./cmd/everagent-identity diagnose --json
scripts/ecommit.sh -m "说明实际修改"
```

身份查询只在需要时使用。提交器自行核实当前Committer；自动失败先修读取路径，确无依据时才承接用户明确声明，不从配置、历史或产品名猜模型。

公开提交使用`CommitOptions.IdentityOnly=true`、`EnforceAuthor=true`与显式`ContentGuard`：
- IdentityOnly只跳过旧Gate/Preflight；EnforceAuthor独立要求有效Author策略、拒绝覆盖并核对最终Author。策略错误不回退全局身份，也不恢复质量流水线。
- ContentGuard仅检查本次暂存内容的新增泄密信号，绑定检查前后及实际提交的tree。
- 未传ContentGuard的IdentityOnly调用方不额外检查内容，原私仓行为保持。
- 旧Gate模式保留给原调用方，不自动变为新的公开默认。安装版eacli按自己的core pin运行，不能把源码修改冒充设备升级。

Git原生的冲突、签名、权限和hooks仍生效，不覆盖仓外hooks。提交后核实实际署名；结果未知或内容后置核验失败时保留现场，不自动重放或推送。
`scripts/egit.sh merge <revision>`在洁净checkout中冻结目标，快进不创建提交，分叉合并复用Commit的双身份与内容检查；冲突保留现场。`scripts/egit.sh push`绑定捕获的SHA与唯一目的地，经PushWithGuard检查新增署名和撤销提交后普通推送，读回匹配才称已核实，不强推。原生Git/GUI不保证经过wrapper，hooks仍按原配置运行。

## 公开内容与主动工具

```bash
# 提交用index，工作区预览用worktree，CI用head和固定base。
go -C packages/everagent-core run ./cmd/ea-quality disclosure --scope worktree
# 需要更新索引时显式调用，不改报告原文。
go -C packages/everagent-core run ./cmd/ea-quality index --write
```

`quick`是disclosure的兼容入口，输出`mode=public-disclosure`；不校验报告评分、Context预算、索引或测试结果。
明显新增凭据及受限原始材料阻断；路径、IP等启发式线索提示。扫描不读取私有仓、不调用模型、不输出匹配原文，也不是完整隐私或二进制内容审计。

`full/context/privacy/report/policy/sampling/catalog/scripts/links/index`均是主动工具。旧严格报告合同与历史评估规则保留供明确需要时使用，不约束所有新笔记或草稿，不自动重打分或运行模型回放。
`full`可能从捕获快照运行Go测试；它不是提交前置。JSON与非零退出如实报告，`--details`展开诊断；`go run`会折叠子程序的非零退出码，正式提交脚本保留实际状态。

## 实现位置

| 内容 | 位置 |
|---|---|
| 版本、会话与调用方 | `core.go`、`session.go`、`process*.go`、`identity.go`、`desktop.go` |
| 模型观测、声明与失效 | `observations*.go`、`kimi.go`、`declarations.go` |
| 有界读取配置 | `config.go`、`src/everagent_core/identity/readers.json` |
| DSH/OpenCode原生绑定 | `src/everagent_core/identity/*_plugin.mjs` |
| Git与公开入口 | `git.go`、`cmd/ea-git`、`scripts/ecommit.sh` |
| 新增内容保护及可选审查 | `internal/publicquality/`、`cmd/ea-quality` |
| 学习工作台读取 | `internal/learning/`、`cmd/ea-learning-index` |

原生日志只取与当前调用绑定的必要元数据；不读取其他会话正文。Kimi枚举不启动CLI、更新或重建索引；原生模型字段不足的客户端继续保留unknown/requested，不以配置自动放行。

## 验证边界

代码改动按需运行对应Go测试与vet，CI按路径选择，不在每次提交重复整套回归。
合成回归不等于真实客户端、模型调用、设备安装或跨平台验收。历史报告、evidence/review和policy原件不因本次简化迁移。

契约见[身份与会话](../../docs/AGENT_SESSION.md)、[提交与公开安全](../../docs/PROTOCOL_COMMON.md)和[写作指南](../../docs/REPORT_WORKFLOW.md)。
