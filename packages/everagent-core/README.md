# everagent-core

可安装的公共 Python core：当前调用方身份、模型证据、会话契约、脚本目录与 Git 原语。
Python ≥3.10，运行时仅用标准库；macOS、Linux、Windows 使用同一契约。

## 所有权

| 内容 | Owner |
|---|---|
| core 版本 | `src/everagent_core/__init__.py`，包元数据由此读取 |
| harness 识别与厂商邮箱 | `src/everagent_core/identity/detect.py` |
| 调用方祖先与进程创建身份 | `src/everagent_core/identity/processes.py` |
| 当前模型自动读取、配置提示与用户声明 | `identity/observations.py`、`identity/models.py`、`identity/declarations.py` |
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

先自动核实 Codex 当前 thread、Pi 当前 shell context、TRAE 精确 thread 与 Claude Code 原生 UUID session；只有无法核实时，
才由用户明确指定，再用 `declare-model --model <id> --user-confirmed`。
配置提示和 `AGENT_ID` 不能授权 Git 署名；声明有会话范围与有效期，不标为 runtime verified。

完整规则见 [身份与会话契约](../../docs/AGENT_SESSION.md)、
[Git 协议](../../docs/PROTOCOL_COMMON.md#c-push-flow推送流程--全局统一)。
验证入口：`python3 -m unittest scripts.test_core_contracts scripts.test_whoami_agent scripts.test_git_identity scripts.test_git_commit`。
