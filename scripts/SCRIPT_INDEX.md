# 脚本目录

> Generated from script-catalog.json; do not edit by hand.
> source-sha256: `27676cd63245d06563252307052f0acb11d0233667e015bccf6f1eec6f99dcdc`
> generator-sha256: `9213269c0c54296587a29c36f16de6135b241179cc634a50cad17ddf05268125`

| ID | 入口 | 描述 | 范围 |
|---|---|---|---|
| `session.core` | `packages/everagent-core/cmd/everagent-identity/main.go` | 自动核实当前调用方的harness和模型；diagnose协助修复，declare仅记录用户兜底。 | 当前调用方；不扫描其他会话正文 |
| `git.core` | `packages/everagent-core/cmd/ea-git/main.go` | 核实双身份；提交只消费暂存tree，绑定同源质量门、消息和前后身份。 | 当前公开checkout和暂存tree |
| ↳ compatibility | `scripts/ecommit.sh` | 薄Bash入口；构建并调用ea-git commit，不配置Git或跳过门禁。 | 同 canonical |
| `quality.public` | `packages/everagent-core/cmd/ea-quality/main.go` | 检查公开内容、报告来源和复核快照、Context及索引；不调用模型或改历史产物。 | 当前公开快照；不读私仓、不做真实模型回放 |
| `evaluation.harness-experiment` | `scripts/harness_selection.py` | 消费可信评测器记录，按硬门和 Pareto 前沿选择最多三个 context 候选；不执行或发布。 | 可信评测记录与一次有界实验 |
