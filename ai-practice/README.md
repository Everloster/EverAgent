# AI Practice — AI 技术的小型实验

这里保存 Transformer、MoE、Long Context、技能策展和 GRPO 等主题的教学代码与实验笔记。部分实验有历史运行输出，部分是 Notebook 教程或缩尺模拟；具体范围见[实验地图](./MAP.md)。

多数例子面向 CPU、单卡或缩尺环境，但依赖和硬件要求不同。RAG、多模态、扩散模型等可以作为后续方向，尚不属于这里已完成的实验覆盖。

## 快速开始

只阅读笔记不需要配置环境。准备运行时，先按 [SETUP.md](./SETUP.md)安装所选实验的依赖，再从仓库根目录进入本目录：

```bash
cd ai-practice
python3 src/check_hardware.py
jupyter notebook notebooks/01_transformer_from_scratch.ipynb
```

硬件检查输出只供本地选择环境，不应未经检查就原样提交。Notebook 按需运行；涉及下载模型、数据或 GPU 训练的单元，先核对其说明和资源要求。

不想从 Notebook 开始，可以阅读[GRPO toy 实验](./experiments/exp_008_grpo_simulation.md)与[对应脚本](./src/grpo_simulation.py)。它用 NumPy 在 CPU 上模拟训练，并非真实 LLM 微调。重新运行时用 `--out-dir` 指定新的输出目录，避免覆盖已有历史结果。

## 现有主线（LLM 工程实践路径）

| 主题 | 入口 | 实现与边界 |
|---|---|---|
| Transformer 原理 | [exp_001](./experiments/exp_001_transformer_from_scratch.md)、[Notebook 01](./notebooks/01_transformer_from_scratch.ipynb) | PyTorch 教学实现，不是大规模预训练 |
| Transformers API | [exp_003](./experiments/exp_003_transformers_library.md)、[Notebook 02](./notebooks/02_transformers_library.ipynb) | HuggingFace 库的使用示例 |
| HuggingFace Hub | [exp_002](./experiments/exp_002_huggingface_basics.md)、[Notebook 03](./notebooks/03_huggingface_api.ipynb) | 模型与数据集管理示例 |
| LoRA / GRPO 微调 | [exp_004](./experiments/exp_004_qwen25_grpo_finetune.md)、[Notebook 04](./notebooks/04_qwen25_grpo_finetuning.ipynb) | Qwen2.5-3B 路线；笔记仅展示早期训练点，不视为收敛验证 |
| MoE | [exp_005](./experiments/exp_005_moe_transformer.md)、[Notebook 05](./notebooks/05_moe_transformer.ipynb) | 稀疏激活与路由的小规模实验 |
| Long Context | [exp_006](./experiments/exp_006_long_context_1m_simulation.md)、[代码](./src/long_context_simulation.py) | 缩尺模拟与 KV Cache 成本模型，不是 1M 上下文真实训练 |
| Skill 策展 | [exp_007](./experiments/exp_007_skillos_curator_simulation.md)、[代码](./src/skillos_curator_simulation.py) | 确定性任务流与技能增删改模拟 |
| GRPO toy | [exp_008](./experiments/exp_008_grpo_simulation.md)、[代码](./src/grpo_simulation.py) | NumPy、2-token 策略，包含共享答案和不同答案的对照 |

本地 LLM 选型的历史材料不作为当前性能基准；工具推荐与速度估算需要和实际推理测量分开。

## 前置知识

- 阅读或修改代码需要 Python 基础；
- Transformer 和 MoE 实验需要了解 Tensor、`nn.Module` 与梯度计算；
- 矩阵乘法、softmax 和 next-token prediction 有助于理解，但不要求先熟悉所有模型或 GPU 工具。

## 章节地图

```text
ai-practice/
├── notebooks/     # 教学 Notebook
├── src/           # 实现与辅助脚本
├── experiments/   # 实验笔记与限制
├── images/        # 图表及部分历史运行输出
├── wiki/          # 概念索引
└── data/          # 部分教学数据
```

## 学习资源索引

- [LEARNING_PATH.md](./LEARNING_PATH.md)：早期四阶段 Notebook 路径；新增实验以本页和 MAP 为准。
- [MAP.md](./MAP.md)：已有证据与待补问题。
- [wiki/index.md](./wiki/index.md)：概念查询。
- [AGENTS.md](./AGENTS.md)：本目录的执行约定。
