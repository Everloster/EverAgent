---
title: Transformers 库加载预训练模型实践
type: experiment_analysis
status: done
experiment_id: exp_003
notebook: notebooks/learn_transformers.ipynb
updated_on: 2026-04-20
---

## 实验摘要

> 使用 HuggingFace Transformers 库的三种 API 层级（pipeline、AutoClass、底层模型）加载预训练情感分类模型，验证多语言文本分类能力，覆盖从最高抽象到最低抽象的使用模式。

## Step 1 实验目标

- **工程问题**：掌握 `transformers` 库三层 API 的使用差异与适用场景
- **模型**：`nlptown/bert-base-multilingual-uncased-sentiment`（多语言 BERT，5 类情感打分 1-5 星）
- **背景**：与 exp_001 形成对比——exp_001 是手写 Transformer，本实验是使用预训练好的工业级模型

## Step 2 实现方法

**框架**：`transformers`（HuggingFace）

**三层 API 实践**（来自 `notebooks/learn_transformers.ipynb`）：

| 层级 | API | 特点 |
|------|-----|------|
| 最高抽象 | `pipeline("sentiment-analysis")` | 一行代码，自动选择默认模型 |
| 中间层 | `pipeline(model=model, tokenizer=tokenizer)` | 指定模型 + tokenizer，灵活控制 |
| 最低层 | `AutoModelForSequenceClassification` 直接推理 | 手动处理 logits → softmax |

**模型**：`nlptown/bert-base-multilingual-uncased-sentiment`
- 基座：BERT-base（12层，768维，12头，1.1亿参数）
- 多语言：支持英语、法语、德语、荷兰语、意大利语、西班牙语等

**加载方式**：
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained(model_name, torch_dtype="auto")
```

## Step 3 关键发现

- `pipeline("sentiment-analysis")` 默认模型为 `distilbert-base-uncased-finetuned-sst-2-english`（英语二分类 POSITIVE/NEGATIVE）
- `nlptown/bert-base-multilingual-uncased-sentiment` 支持中文输入（"你好啊" 等中文句子可正常分类）
- `torch_dtype="auto"` 会根据硬件自动选择 float16/bfloat16，节省显存
- `AutoClass` 系列（AutoTokenizer、AutoModel*）相比硬编码 class 名更具可移植性

**实际结果**：`[需运行 notebook 获取具体分类置信度得分]`

## Step 4 代码参考

| 功能 | 文件 | 单元 |
|------|------|------|
| 默认 pipeline 调用 | `notebooks/learn_transformers.ipynb` | Cell 1 |
| 指定模型的 pipeline | `notebooks/learn_transformers.ipynb` | Cell 4 |
| AutoModel 底层推理 + softmax | `notebooks/learn_transformers.ipynb` | Cell 6 |

## Step 5 局限性与下一步

**局限性**：
- BERT-base 参数量（110M）vs exp_001 手写模型（<1M）差距悬殊，说明工业预训练的价值
- 情感分析任务相对简单，未测试更复杂任务（生成、问答）

**建议后续**：
- 将此处的 AutoTokenizer 用法迁移到 exp_004 的 GRPO 微调流程
- 比较 pipeline 抽象与 AutoClass 在推理速度上的差异（是否有额外开销）
