---
title: Transformers 库三层 API 实践
type: tutorial_note
stage: 2
notebook: notebooks/02_transformers_library.ipynb
prerequisites: ["python_basics"]
updated_on: 2026-04-20
---

## 学习目标

- [ ] 理解 HuggingFace Transformers 三层 API 的抽象层次
- [ ] 能用 `pipeline()` 快速完成情感分析等任务
- [ ] 理解 `AutoTokenizer` + `AutoModel` 的灵活用法
- [ ] 对比手写 Transformer（阶段 1）和预训练模型的能力差距

---

## 核心概念（Why）

### 三层 API 的设计哲学

HuggingFace Transformers 库提供从最高到最低抽象的三层接口，对应不同使用场景：

```
pipeline()              ← 最高层：一行代码，适合快速验证
AutoTokenizer +         ← 中间层：指定模型，适合生产应用
AutoModel
底层 logits 处理        ← 最低层：完全自定义，适合研究开发
```

**经验规则**：
- 探索阶段 → 用 `pipeline()`
- 产品化 → 用 `AutoClass`
- 研究复现 → 直接操作 logits

### 预训练 vs 手写的能力差距

阶段 1 的教学模型：
- 参数量：~130K（13 万）
- 训练数据：1 本销售教科书，~66K 词
- 上下文长度：16 tokens

阶段 2 用到的 BERT-base：
- 参数量：110M（1.1 亿）—— **约是手写模型的 800 倍**
- 训练数据：BookCorpus + Wikipedia（33 亿词）—— **约是手写数据的 50,000 倍**
- 上下文长度：512 tokens

这就是为什么预训练模型能做情感分析、翻译等复杂任务，而教学规模的模型只能做简单语言模式匹配。

---

## 实现解析

### 层次 1：pipeline（最高抽象）

```python
from transformers import pipeline

# 默认模型：distilbert-base-uncased-finetuned-sst-2-english
classifier = pipeline("sentiment-analysis")
result = classifier("I love this!")
# → [{'label': 'POSITIVE', 'score': 0.9998}]
```

**`pipeline()` 在背后做了什么**：
1. 根据任务类型选择默认模型
2. 自动下载模型权重和 tokenizer
3. 处理 tokenization → forward → 解码的完整流程

### 层次 2：AutoClass（中间抽象）

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
model = AutoModelForSequenceClassification.from_pretrained(model_name, torch_dtype="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)

classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
```

**`torch_dtype="auto"` 的作用**：
- 自动选择最优数据类型（GPU 上用 float16，CPU 上用 float32）
- 节省 GPU 显存（float16 比 float32 减少 50%）

### 层次 3：直接操作 logits（最低抽象）

```python
from torch import nn

pt_outputs = pt_model(**pt_batch)
predictions = nn.functional.softmax(pt_outputs.logits, dim=-1)
# predictions: shape [batch_size, num_labels]
# 对于情感分析：[P(1星), P(2星), P(3星), P(4星), P(5星)]
```

---

## 实验结果

**注**：运行 `notebooks/02_transformers_library.ipynb` 获取实际输出。

**预期结果示例**（`nlptown/bert-base-multilingual-uncased-sentiment`）：
- 输入：`"I love this product!"`
- 预测标签：`5 stars`（最高评分）

该模型支持英语、法语、德语、荷兰语、意大利语、西班牙语。  
中文（`"你好啊"`）的分类结果可能不稳定（训练数据不含中文）。

---

## 思考题与延伸实验

1. **API 性能对比**：`pipeline()` 和直接用 `AutoModel` 推理，速度上有差异吗？用 `time` 模块测量 100 次推理的总耗时。

2. **任务扩展**：将 `pipeline` 的任务类型改为 `"text-generation"`，用 GPT-2 生成文本。与阶段 1 的教学模型生成质量对比如何？

3. **批量推理**：`classifier(["text1", "text2", "text3"])` 和三次单独调用，哪个更快？为什么？

4. **模型选择**：`AutoModel` 和 `AutoModelForSequenceClassification` 有什么区别？什么场景用哪个？

5. **与阶段 1 对比**：阶段 1 的模型训练了 5000 步，在 sales_textbook 上的语言能力和 BERT 比较，差距有多大？

---

## 参考资料

- [HuggingFace Transformers 官方文档 - pipeline](https://huggingface.co/docs/transformers/main_classes/pipelines)
- [HuggingFace Transformers 官方文档 - AutoClass](https://huggingface.co/docs/transformers/autoclass_tutorial)
- [nlptown/bert-base-multilingual-uncased-sentiment 模型页](https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment)
