# ai-practice — 领域协议

> 用个人设备可运行的最小实现理解 AI 技术，产出代码、真实输出与实验笔记。

## 路由

最小 demo、复现实验或性能验证读取 [experiment_analysis](./skills/experiment_analysis/SKILL.md)。需要归档实验笔记时同时使用根级 [`everagent-report`](../.agents/skills/everagent-report/SKILL.md)。

## 领域约束

- 优先 CPU、单卡或缩尺模拟；与真实规模的差异必须写清。
- 损失、准确率、速度和显存等数值只能来自本次实际运行；未运行则标 `[待补充]`。
- 笔记引用代码时给出文件路径与行号或 notebook cell。
- 验证先覆盖受影响路径；只有失败、跨模块影响或未解决风险才扩大。

需要既有覆盖时查询 eacli `knowledge.practice`；CONTEXT、MAP 与 PROFILE 条件读取。实验目录、元数据与质量门由选中的 skill 和根级工作流拥有。
