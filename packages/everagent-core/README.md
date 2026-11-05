# everagent-core

## Go 迁移候选

根目录的 Go module 提供同源身份读取、声明、会话组合与 Git 原语，版本为 `0.4.0-dev`。
CLI 可将其直接编译进单个二进制，不需要运行时解释器或独立身份 helper：

```bash
go -C packages/everagent-core test ./...
go -C packages/everagent-core run ./cmd/everagent-identity inspect --json
```

这是源码迁移检查点，尚未替换下述旧安装入口。合成回归不证明各客户端、平台或安装态已验收；
仓库质量门禁由各调用方注入，不因迁移而跳过。Go 模块依赖与哈希由 `go.mod` / `go.sum` 固定。

## 旧入口（迁移中）

可安装的公共 Python core：当前调用方身份、模型证据、会话契约、脚本目录与 Git 原语。
Python ≥3.10，运行时仅用标准库；macOS、Linux、Windows 使用同一契约。
0.3.0为当前源码候选；安装态及真实平台支持分别验收，不以版本号或fixture通过证明已部署。

## 所有权

| 内容 | Owner |
|---|---|
| core 版本 | `src/everagent_core/__init__.py`，包元数据由此读取 |
| harness 识别与厂商邮箱 | `src/everagent_core/identity/detect.py` |
| 有界签名/路径/字段修复配置 | `identity/readers.json`、`identity/config.py`；不配置模型答案 |
| 调用方祖先与进程创建身份 | `src/everagent_core/identity/processes.py` |
| 当前模型自动读取、配置提示与用户声明 | `identity/observations.py`、`identity/models.py`、`identity/declarations.py` |
| DSH 官方 shellEnv 适配 | `identity/dsh_plugin.mjs`；当前调用元数据，随包分发 |
| 宿主 App 元数据、会话组合 | `apps.py`、`session.py` |
| 脚本描述验证与生成 | `catalog.py` |
| Git 原语、trailer 与 tree 校验 | `git.py` |
| JSON 契约 | `schemas/` |

core 不保存私有设备、地址、网络、凭据或任务记录。仓库作者策略由
[`config/git-policy.json`](../../config/git-policy.json) 注入；每个仓库提供自己的质量门禁。
private eacli 的随包副本由 generator 生成并锁定 source commit 和文件 SHA-256，禁止手改 vendor。

## 使用

源码入口：`python3 scripts/agent_identity.py --json`；旧 `whoami_agent.py` 保持兼容。
安装包入口：`everagent-identity inspect --json`，无需相邻仓库。

先自动核实当前会话；失败时用 `everagent-identity diagnose --json` 定位公开 owner，Agent 先修复可行的
读取器与绑定并复验。Codex、Pi、TRAE、Claude Code、ZCode、MiniMax Code、Kimi Code CLI/Desktop 与 DSH 的现有自动来源继续保留回归；
cursor-cli 提供进程/会话声明绑定（`sand-exit-watch` + `CURSOR_CONVERSATION_ID`），尚无自动模型读取器。
eacli完整会话入口收敛为current→diagnose→declare；独立core对应inspect/diagnose/declare。
确实无法核实时才由用户明确补device/harness/form/model，再用`declare --model <id> --user-confirmed`等显式字段；
旧declare-model保持模型兼容。字段有各自时间与TTL，冲突过滤保留模型撤销边界，普通字段更新不续期旧模型；声明不授予权限。
配置提示和`AGENT_ID`不能授权Git署名；interface与外层host分开，未知模型id为unknown，配置/请求各自单列。

OpenCode 2.0.27新增仅请求元数据读取：native session ID+唯一当前祖先+精确cwd，V2 SQLite只选标量，
不读正文或其他会话。它不是provider responseModel；返回requested及request_observation，自动确认仍为false，
需要实际型号时保留用户兜底。未完成/变化/过期等边界与固定官方源码依据见AGENT_SESSION。

Git identity默认验证实际Author/Committer；legacy show显式兼容零退出。push绑定captured SHA与唯一目的地，
拒绝再次URL rewrite/remote别名歧义，读回匹配才verified；传输或读回异常沿原结果核验，不自动重推。
agent list为eacli同伴入口，session peers兼容；活动探针需显式check-activity，旧安装看实际字段，不假称已轻量。

完整规则见 [身份与会话契约](../../docs/AGENT_SESSION.md)、
[Git 协议](../../docs/PROTOCOL_COMMON.md#c-push-flow推送流程--全局统一)。
验证入口：`python3 -m unittest scripts.test_core_contracts scripts.test_whoami_agent scripts.test_git_identity scripts.test_git_commit scripts.test_model_observations`。
只改文档不重复运行未受影响的全套；模型读取改动优先对应合成fixture，真实安装/模型调用另按授权验收。
