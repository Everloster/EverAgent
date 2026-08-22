# 模型 × Infra × 硬件 Co-design（联合设计）

> 概念 · 首次出现：2026-07-28（Vol.148 游凯超访谈）

## 定义

摩尔定律终结后通用算力红利消失，模型结构、推理系统、硬件必须联合设计：**模型的结构决定了推理效率的上界**，上界太低系统工程师无力回天；反过来，算法只有能被系统/硬件高效实现才能存活（见 [[hardware-lottery]]）。

## 要点

- 时代背景：黄氏定律——算力两年翻几倍但都是专用算力；「通用的进步已经没了」，所以需要与硬件、系统、harness 多方 co-design
- **RoPE vs ALiBi**：FlashAttention 成训练必须后，凡需改 attention kernel 内部实现的位置编码（ALiBi 等上百种）都被淘汰；RoPE 独立注入 query/key、与 kernel 互补——模型结构与 infra「共鸣」者存
- **DeepSeek 模式**：算法同学懂 infra——DeepSeekMoE 高效粗粒度实现、细粒度 MoE 推理系统首发、FP8 分块量化（符合 MX 格式）都出自算法侧；机制 = 招双料人 + 坐在一起办公耳濡目染。反例：infra 太主导时会为负载均衡选 expert choice 路由，算法上不可接受
- **投机解码落地依赖引擎实现**：EAGLE/MTP（猜 3-5 个 token）→ DFlash（一次约 16 个）→ DSpark（置信度剪枝，16 只验前 8）；「好的推理引擎实现是投机解码能否大规模落地的关键」
- **延伸到 Harness**：Agent 场景保持前缀稳定（prefix caching 复用计算）；反例 = System Prompt 塞精确到秒的时间戳 + 定时任务卡整点（Moonshot：「一群小龙虾一到整点就集体出动攻打月球」）

## 引用

- [[2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao|对游凯超3小时访谈]]（Vol.148）
