# AI Practice — 实验地图

记录已有的代码、教学材料与运行证据，帮助选择实验入口。状态描述只适用于所列产物，不评价整个领域的掌握程度。

## 已有材料

| 主题 | 当前材料 | 入口 | 待补证据 |
|---|---|---|---|
| Transformer | 教学实现与笔记 | [exp_001](./experiments/exp_001_transformer_from_scratch.md)、[model.py](./src/model.py) | 当前环境复现与训练稳定性对照 |
| HuggingFace / Transformers | 教学 Notebook 与笔记 | [exp_002](./experiments/exp_002_huggingface_basics.md)、[exp_003](./experiments/exp_003_transformers_library.md) | 固定依赖的端到端复现 |
| MoE | 小规模实现与笔记 | [exp_005](./experiments/exp_005_moe_transformer.md)、[moe_model.py](./src/moe_model.py) | 专家并行与真实大模型路由统计 |
| Long Context | 缩尺模拟与成本模型 | [exp_006](./experiments/exp_006_long_context_1m_simulation.md)、[模拟代码](./src/long_context_simulation.py) | 真实长上下文模型的训练和检索实验 |
| LoRA / GRPO | 微调教程与 CPU toy 运行记录 | [exp_004](./experiments/exp_004_qwen25_grpo_finetune.md)、[exp_008](./experiments/exp_008_grpo_simulation.md) | 真实模型完整训练与同任务消融 |
| Agent Skill 策展 | 确定性缩尺模拟 | [exp_007](./experiments/exp_007_skillos_curator_simulation.md)、[模拟代码](./src/skillos_curator_simulation.py) | 真实技能文件、模型策展与基线对照 |

教程、代码存在和实际运行不是同一证据。具体口径见根目录的[学习与实践记录](../AI_PROGRESS.md#怎样阅读这些证据)。本地模型选型类旧笔记中的工具估算，暂不列为实测吞吐基准。

## 后续候选

以下尚未完成，供选择下一次实验，不作为自动执行清单：

- 补一个现有实验的依赖版本、完整命令和可公开输出；
- 在同一 toy task 上比较 SFT、PPO 与 GRPO；
- 用合成数据做 Context 检索、更新、删除和拒答实验。

## 维护

新增产物或验证结论变化时更新对应行，保留失败与缩尺限制。运行输出先去除个人路径和设备标识；只公开可复用的配置与结果。影响跨领域摘要时，再同步 [AI_PROGRESS.md](../AI_PROGRESS.md)，不为每次小改重复维护两份状态。
