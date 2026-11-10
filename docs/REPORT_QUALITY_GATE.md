# 可选严格审查与历史记录

日常写作统一见[REPORT_WORKFLOW.md](REPORT_WORKFLOW.md)。本页和旧评分工具不再规定提交门槛；普通笔记、草稿、实验和报告可以不创建evidence/review文件。

## 何时使用旧工具

仅在用户明确需要评分、正式证据账本、既有report-v2兼容或历史结果核查时，主动使用：

```bash
python3 scripts/report_quality.py --help
python3 scripts/report_quality.py policy --json
go -C packages/everagent-core run ./cmd/ea-quality report --report <报告路径>
```

这些工具继续读取原有policy与合同，因此可能报告旧标准不满足；这不是普通提交失败的理由，也不授权自动切换模型、创建Reviewer或修改报告状态。
`check --finalize`等写入操作只在明确采用该旧合同并完成相应工作时使用，不通过补模板或伪造评分让报告“通过”。

## 历史如何保留

- 原evidence、review、策略归档与报告版本保留，不删除、不重打分。
- 旧评分只说明当时绑定的正文、证据和policy，不自动覆盖后续修改。
- 需要独立复核时按当前用户要求选择范围和角色，不强制每篇一轮或两轮。
- 研究仍须来源可靠、范围清楚；取消机械评分不允许编造引用、假报实测或掩盖缺口。

完整旧流程与字段见[历史原文](archive/report-process-20261110/REPORT_QUALITY_GATE.md)，不作为当前默认规则。
