# ai-practice — 领域协议

> 领域：**各类 AI 技术的低成本可运行 demo 与理解**——类似"教学材料配套代码"。
> 用最小、可在个人机器（CPU / 单卡 / 缩尺模拟）上跑起来的 demo，把一项 AI 技术讲透。
> 涵盖但不限于：Transformer/注意力、微调（LoRA/GRPO）、RAG、Agent、多模态、推理优化、扩散模型等。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。
> 联网与个人上下文遵守根 `AGENTS.md` 的托管策略，本文件不重复工具细节。

---

## 工作模式：对话即学习

用户要求最小 demo 或实验验证时，使用根 skill [`everagent-report`](../.agents/skills/everagent-report/SKILL.md) 与 [REPORT_WORKFLOW](../docs/REPORT_WORKFLOW.md)。通过 eacli 从 `knowledge.practice` 获取最小 context，再按需读取 CONTEXT、MAP、PROFILE 和一个实验 skill。代码必须实际运行并记录观察值。

---

## 领域特化

- **产出类型**：`experiments/`（教学笔记）、`notebooks/` `src/`（可运行代码/缩尺模拟）
- **低成本优先**：能 CPU 跑就不要求 GPU；跑不动全量就缩尺模拟（toy 维度/小数据），在笔记里注明这是缩尺 demo 及其与真实规模的差异
- **特化要求（关键）**：**笔记中的数值（损失/准确率/速度/显存）必须来自实际运行**，未运行标 `[待补充]`，禁止虚构；代码引用含文件路径+行号或 cell 编号
- **教学笔记 6 节**：学习目标 / 核心概念(Why) / 实现解析(关键代码) / 实验结果(实际数值) / 思考题与延伸 / 参考资料
- **特化模板**：[skills/experiment_analysis/SKILL.md](./skills/experiment_analysis/SKILL.md)

---

## 笔记 frontmatter

```yaml
---
title: "实验名称"
domain: "ai-practice"
report_type: experiment_analysis
experiment_id: exp_NNN
notebook: notebooks/xxx.ipynb   # 若有对应 notebook
status: in_progress
updated_on: YYYY-MM-DD
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["experiment"]
---
```

---

## 完成后自检

```bash
python3 scripts/reindex.py
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

提交规范见根 [AGENTS.md](../AGENTS.md) 与 [docs/PROTOCOL_COMMON.md](../docs/PROTOCOL_COMMON.md)。
