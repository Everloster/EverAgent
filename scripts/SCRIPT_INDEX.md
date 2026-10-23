# 脚本目录

> Generated from script-catalog.json; do not edit by hand.
> source-sha256: `2a032240a36a776ad931833600c348ad3176fdc64f5fc4e23b090331d80caa3b`
> generator-sha256: `a62b18e2c1d16f8ba9f57e556b7863565c858570b49a63d3ac19c890a520962b`

| ID | 入口 | 描述 | 范围 |
|---|---|---|---|
| `agent.identity` | `scripts/agent_identity.py` | 自动核实当前 harness/model；失败先诊断并修复可行读取路径，用户指定兜底。 | 当前调用方和 checkout |
| ↳ compatibility | `scripts/whoami_agent.py` | 旧 whoami 名称；转交同一公共 core 身份实现。 | 同 canonical |
| ↳ compatibility | `scripts/agent_identity/__init__.py` | 旧 Python 包 import 路径；转交同一公共 core。 | 同 canonical |
| `agent.model-declaration` | `scripts/agent_model_declare.py` | 自动核实和可行修复仍无法取证时，记录用户明确指定的当前模型，绑定本会话并在有效期后失效。 | 当前调用方和 checkout |
| `git.identity` | `scripts/git_identity.py` | 校验 Author、当前 Agent Committer 和模型确认依据。 | 当前调用方和 checkout |
| `git.commit` | `scripts/git_commit.py` | 提交已经暂存的 tree，校验身份、门禁和 index 不变；共同作者显式填写。 | 当前调用方和 checkout |
| ↳ compatibility | `scripts/ecommit.sh` | 兼容 Bash 入口；仅寻找 Python 并转交提交器。 | 同 canonical |
| `scripts.catalog` | `scripts/script_catalog.py` | 查看本族脚本的描述、owner、兼容名、平台和输入输出契约。 | 当前调用方和 checkout |
| `core.bootstrap` | `scripts/core_bootstrap.py` | 从当前公开 checkout 加载唯一公共 core，实现稳定脚本的源码运行。 | 当前调用方和 checkout |
| `evaluation.harness-experiment` | `scripts/harness_selection.py` | 消费可信评测器记录，按硬门和 Pareto 前沿选择最多三个 context 候选；不执行或发布。 | 可信评测记录与一次有界实验 |
