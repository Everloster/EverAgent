# ai-practice — 领域协议

> 领域：LLM 工程实践教学（Transformer 实现·HuggingFace 生态·参数高效微调·RLHF/GRPO）。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。

---

## 工作模式：对话即学习

用户说"帮我学 X / 跑个实验验证 Y / 上次那个继续"，按以下循环：

1. **读画像与地图** — [PROFILE.md](./PROFILE.md)、[MAP.md](./MAP.md)、[wiki/open-questions.md](./wiki/open-questions.md)
2. **查已有积累** — 翻 `wiki/concepts/`、`experiments/`、`notebooks/`，已有则深化而非重复
3. **做实验/研究** — 写可运行代码或从已有 notebook 提炼；按 METHODOLOGY 标注证据
4. **写笔记** — 教学笔记存 `experiments/exp_NNN_*.md`，结尾必带「思考与追问」三问
5. **沉淀** — 更新 wiki（概念页）、未解问题汇入 open-questions
6. **更新画像** — 把新兴趣/水平/偏好写回 PROFILE（仅凭用户真实表达，禁止臆测）

---

## 领域特化

- **产出类型**：`experiments/`（教学笔记）、`notebooks/` `src/`（代码实验）
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
status: done
updated_on: YYYY-MM-DD
---
```

---

## 完成后自检

```bash
python3 scripts/reindex.py
```

提交规范见根 [AGENTS.md](../AGENTS.md) 与 [docs/PROTOCOL_COMMON.md](../docs/PROTOCOL_COMMON.md)。
