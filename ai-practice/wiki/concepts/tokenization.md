# Tokenization（分词 / 词元化）

> 将原始文本转换为模型可处理的整数序列（token IDs）的过程，是 LLM 输入处理的第一步。

---

## 直觉理解（Why it exists）

神经网络只能处理数字，不能直接处理文本字符串。Tokenization 建立从"文本字符"到"整数"的映射。

**关键设计问题**：如何切分词？

- **字符级**（character-level）：词表小（几十个字符），序列太长，难以捕捉词语语义
- **词级**（word-level）：词表太大（几十万词），OOV（未知词）问题严重
- **子词级**（subword-level）：**现代 LLM 的标准方案**，平衡词表大小和序列长度

---

## 核心机制（How it works）

### 子词分词算法

现代主流方案：

| 算法 | 使用模型 | 核心思想 |
|------|---------|---------|
| BPE（Byte Pair Encoding） | GPT-2, GPT-4, Qwen | 迭代合并最高频的字节对 |
| WordPiece | BERT | 类似 BPE，但用最大化 likelihood 决定合并 |
| SentencePiece | T5, LLaMA | 不依赖空格，直接在原始字节序列上分词 |

### BPE 工作流程（以 TikToken 为例）

```
输入：  "tokenization"
初始：  ["t","o","k","e","n","i","z","a","t","i","o","n"]
合并1：  "t"+"o" → "to"："to","k","e","n","i","z","a","t","i","o","n"
合并2：  "to"+"k" → "tok"：...
...
最终：  ["token", "ization"]  # 2 个 token
```

**词表大小**决定了模型能处理多少"基本单元"。

### 本项目用到的两种 Tokenizer

| | TikToken `cl100k_base` | HuggingFace AutoTokenizer |
|--|----------------------|--------------------------|
| 用于 | 阶段 1（手写 Transformer） | 阶段 2-4（预训练模型） |
| 词表大小 | ~100,277 | 依模型而定（Qwen：~152,064） |
| 使用方式 | `encoding.encode(text)` | `tokenizer(text, return_tensors="pt")` |
| 特殊 token | 无（教学简化） | `[BOS]`, `[EOS]`, `[PAD]` 等 |

---

## 代码实现（本项目）

### 阶段 1：TikToken（`src/model.py` L36-41）

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 同款编码

# 编码：文本 → token IDs
text = "Hello, world!"
token_ids = encoding.encode(text)      # [9906, 11, 1917, 0]

# 解码：token IDs → 文本
decoded = encoding.decode(token_ids)   # "Hello, world!"

# 词表大小
vocab_size = max(token_ids) + 1        # 约 100,277
```

### 阶段 2-4：HuggingFace AutoTokenizer

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")

# 编码（返回 PyTorch tensor）
inputs = tokenizer("你好，世界！", return_tensors="pt")
# inputs: {'input_ids': tensor([[...]), 'attention_mask': tensor([[...]])

# 解码
text = tokenizer.decode(inputs['input_ids'][0], skip_special_tokens=True)

# Chat 格式（阶段 4 使用）
messages = [{"role": "user", "content": "How many r's in strawberry?"}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
```

---

## 关键概念：Special Tokens

HuggingFace tokenizer 会自动插入特殊 token：

| Token | 含义 | 作用 |
|-------|------|------|
| `[BOS]`（Begin of Sequence） | 序列开始 | 提示模型"新序列开始" |
| `[EOS]`（End of Sequence） | 序列结束 | 告知模型何时停止生成 |
| `[PAD]` | 填充 | 批处理时将短序列填充到统一长度 |
| `<\|im_start\|>` | Qwen 角色开始 | Chat 模板中标记 user/assistant 角色 |

TikToken 在阶段 1 中没有这些特殊 token（教学简化），真实 LLM 推理时这些 token 非常重要。

---

## 与相关概念的关系

- **→ [transformer_from_scratch.md](transformer_from_scratch.md)**：Tokenization 是 Transformer 的前置步骤，`vocab_size` 决定 Embedding 层大小
- **→ [grpo.md](grpo.md)**：GRPO 训练时用 Chat 模板的 tokenizer 处理 prompt 和 response

---

## 进一步学习

- **BPE 论文**：[Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909)
- **视频推荐**：[Andrej Karpathy - Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE)（从零实现 BPE）
- **TikToken 文档**：https://github.com/openai/tiktoken
- **HuggingFace Tokenizer 文档**：https://huggingface.co/docs/transformers/main_classes/tokenizer
