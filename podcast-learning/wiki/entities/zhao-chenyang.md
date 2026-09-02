# 赵晨阳

> 人物实体 · 首次出现：2026-08-04（晚点聊 177，1h55m 对谈）；163 期曾解读 DeepSeek-V4

## 身份

- **RadixArk 创始成员**、**SGLang 核心开发者**（UCLA 读博期间加入；SGLang 第一时间适配 V4、K3、GLM 5.2 等中国开源模型）
- 清华本科 → UCLA 博士
- 与 [[sheng-ying|盛颖]]（RadixArk 联创/CEO、SGLang 发起人）同门：RadixArk 圈子（参见 E247）；与 [[zeng-zhiyuan|曾致远]] 清华同系同届

## 核心观点（2026-08-04 详解 K3 时）

- **流水线护城河论**（本期最核心论断）："权重是一次训练的产物，但环境是能够反复复用、产出下一代权重的流水线。全世界得到了这一代智能，没得到造下一代智能的流水线"
- **任务总成本**："单价便宜的模型可能绕一倍甚至十倍弯路，反而更贵"
- **速度非本质**："首发速度反映的是架构有多新、serving stack 有多难"
- **RSI 已在运作**："在有验证器的领域（便宜、可验证、难作弊），RSI loop 已高速运作——这不是自我进化，是在清晰边界下不断自我提升，这正在发生"（以 Kernel Development Agent 为证）
- 推理工程第一手：KDA 白板式缓存（copy-on-write/snapshot/donate）、投机采样 1KB 投影重放、Flash KDA、训推一致=off-policyness
- "我很难说 Kimi Delta Attention 和 Kernel Development Agent 哪一个更伟大"

## 引用本人物的报告

- [[2026-08-04_rss-wandian-latetalk_kimi-k3|晚点聊177 详解 Kimi K3]]（主报告）
- [[2026-09-02_multi_kimi-k3-dueling-reads|K3 一鱼两吃对照]]
