# SGLang

> 项目实体 · 首次出现：2026-08-04（硅谷101 E247 盛颖访谈）

## 身份

- 开源 LLM 推理/服务引擎，2023 年由盛颖等人在斯坦福读博末期与 LMSYS 社区共同开发；归 **LMSYS 社区**所有
- 核心论文创新：**RadixAttention**（见 [[radix-attention]]）；自称「跑在全球数十万张 GPU 上，每天为谷歌/微软/英伟达/xAI 生成数万亿 token」（节目开场白，制作方陈述）
- 初心其实是 **language**：以 agent 为入口设计、带 frontend 语言（结构化生成）；后因 inference 效率挑战更突出转向 runtime 优化——「有一天我们会 revisit，最终它还是应该是一个 language 的形式」

## 与 vLLM 的关系

- 「idea 撞车」关系；盛颖自视早期工作「被 merge 进了 vLLM」；vLLM 开源早半年多
- **分野在时间轴**（盛颖语）：SGLang 先做 scale up（千卡/万卡级 serving），vLLM 先做社区覆盖与 long-tail 模型支持；如今互相补短板，「老实说其实大家都差不多」
- DeepSeek V4 发布时 SGLang 做到 feature set 第一天全兼容，并首次实现 **RL 的 day zero**（Miles 大部分代码重写）

## 引用

- [[2026-08-04_rss-guigu101_shengying|对话盛颖]]（E247）
- 对比维度见 ai-learning 概念页 `ai-learning/wiki/concepts/llm_inference_engines.md`
