# ai-practice — 项目上下文与防幻觉边界

> PracticeAgent 在执行任务前必须读取本文件。
> 本文件记录所有已完成实验，防止重复生成。

---

## 项目概览

- **项目路径**：`ai-practice/`
- **领域**：ML 工程实践·LLM 训练与微调·Transformer 实现
- **来源**：从 Neverland/ML（github.com/Everloster/Neverland）迁移，迁移日期：2026-04-20

---

## 已有实验（边界区）

> 以下实验已生成报告，禁止重复创建同名或同内容的报告。

| exp_id | 实验名称 | 对应 Notebook | 报告路径 |
|--------|---------|--------------|---------|
| exp_001 | 从零实现 Transformer 语言模型 | notebooks/step-by-step.ipynb | experiments/exp_001_transformer_from_scratch.md |
| exp_002 | HuggingFace 数据集与模型 API 实践 | notebooks/learn_huggingface.ipynb | experiments/exp_002_huggingface_basics.md |
| exp_003 | Transformers 库加载预训练模型 | notebooks/learn_transformers.ipynb | experiments/exp_003_transformers_library.md |
| exp_004 | Qwen2.5-3B GRPO 强化学习微调 | notebooks/Unsloth-Qwen2.5_(3B)-GRPO.ipynb | experiments/exp_004_qwen25_grpo_finetune.md |
| exp_005 | MoE Transformer 稀疏激活实验 | notebooks/05_moe_transformer.ipynb | experiments/exp_005_moe_transformer.md |
| exp_006 | Long Context 1M 缩尺模拟实验 | src/long_context_simulation.py | experiments/exp_006_long_context_1m_simulation.md |
| exp_007 | SkillOS 技能库策展小型实验复现 | src/skillos_curator_simulation.py | experiments/exp_007_skillos_curator_simulation.md |

---

## 已有代码文件

| 文件 | 说明 |
|------|------|
| `src/model.py` | Transformer LM 完整实现（教学版，d_model=64） |
| `src/moe_model.py` | MoE Transformer 实现（4 experts, top_k=2，与 model.py 对比） |
| `src/long_context_simulation.py` | 1M long context 三阶段缩尺模拟（预训练窗口、needle 后训练、full-context vs RAG、KV cache 成本） |
| `src/skillos_curator_simulation.py` | SkillOS 技能策展缩尺模拟（grouped task streams、SkillRepo、insert/update/delete、raw memory 对照） |
| `src/inference.py` | 模型推理脚本（加载 model-ckpt.pt 交互生成） |
| `src/check_hardware.py` | 硬件兼容性检查（OS/CPU/GPU/CUDA/vLLM） |
| `src/load_local_dataset.py` | HuggingFace 数据集加载工具（支持本地缓存） |
| `data/sales_textbook.txt` | 销售教科书训练数据（452KB，1460行，66323词） |

---

## ⚠️ 边界（防幻觉）

以下实验已有报告，禁止重复生成：exp_001、exp_002、exp_003、exp_004、exp_005、exp_006、exp_007

exp_005 已包含 MoE Transformer 教学笔记与 `wiki/concepts/mixture_of_experts.md` 概念页；后续维护仅同步导航、索引、边界说明，不新增同主题实验。

exp_006 已包含 Long Context 1M 缩尺模拟脚本、教学笔记与 `wiki/concepts/long_context_simulation.md` 概念页；后续可扩展为 TinyTransformer 真实训练，但不得重复生成同名机制模拟。

exp_007 已包含 SkillOS 技能库策展缩尺模拟脚本、教学笔记与 `wiki/concepts/skillos_curator_simulation.md` 概念页；后续可扩展为真实 Markdown SkillRepo 或本地 LLM curator，但不得重复生成同名机制模拟。

---

## 后续实验方向（可选任务来源）

- LoRA/QLoRA 微调对比实验
- vLLM 推理速度基准测试
- Long Context TinyTransformer 真实训练与 RoPE/ALiBi 对比
- 更大规模 Transformer 训练（d_model=256+）
- GRPO vs SFT 效果对比
- 量化（GPTQ/AWQ）效果评估
