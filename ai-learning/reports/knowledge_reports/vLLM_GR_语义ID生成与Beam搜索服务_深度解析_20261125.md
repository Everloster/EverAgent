---
title: "vLLM-GR：把一次推荐变成一组有效候选，推理引擎要改什么"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-26"
source_url: "https://vllm.ai/blog/2026-11-24-vllm-gr-announcement"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["vllm-gr", "recommendation", "beam-search", "semantic-id", "kv-cache", "inference"]
---

# vLLM-GR：把一次推荐变成一组有效候选，推理引擎要改什么

## 概述

vLLM-GR 为推荐提供候选搜索：模型生成短语义 ID，引擎保留多条路径及父子关系，共享历史 KV，每轮按目录前缀过滤。输出只有几个 token，一次请求却可能探索上百条候选。

工程重点是让搜索循环、状态继承和调度正确衔接。性能图测量特定预算下的候选生成，输出有效、排序分数和推荐效果仍需分别解释。 [原文](https://vllm.ai/blog/2026-11-24-vllm-gr-announcement)

**提炼句：** 输出很短，不代表搜索工作很少。

## 取景框 f(x)

**x｜问题：** 一次推荐只输出很短的 ID，为什么仍要做宽搜索？怎样让候选有效、历史状态对应正确，并控制尾延迟？

**f｜取景框：** 从约束搜索看推荐推理：词表定义可生成的分量，目录定义可存在的条目，beam 预算定义探索路径，父路径状态定义下一步的历史。

**f(x)｜判断变化：** 评估延迟要固定搜索工作量和候选条件。目录成员资格不保证业务可用或用户喜欢，当前候选生成与计划中的外部候选排序也属于不同能力。

## 模型怎样把视频变成可生成的 ID

普通推荐服务会从库存中召回候选，再做排序。生成式推荐的一条路线，是给每个条目分配由多个离散 token 组成的语义 ID，简称 SID。模型读取用户交互历史，自回归地预测下一个 SID 分量，完整序列再映射回条目。

一个自拟目录可以包含 `A-X-1`、`A-Y-2`、`B-Z-3`。第一个分量让模型选择某种粗分组，后续分量继续缩小范围。具体分量的意义、SID 怎样学习以及碰撞怎样处理，取决于训练与编码方案；不能把这个教学目录当成 OneRec 的真实分类法。

序列的联合概率是各步条件概率的乘积。若用户历史为 `h`，SID 为 `(s₁, s₂, s₃)`，则：

```text
P(s₁, s₂, s₃ | h) = P(s₁ | h) × P(s₂ | h, s₁) × P(s₃ | h, s₁, s₂)
```

这里 `h` 包括模型接收的历史与任务输入，`sᵢ` 是第 `i` 个 ID 分量。实现一般累加对数概率，避免许多小概率相乘产生数值问题。

如果每一步只保留概率最高的一个分量，后面的候选就很难补回来。因此候选生成需要保留多条部分路径。beam width 决定留下多少条路径，candidate width 决定某一步准备多少候选供筛选，两者可以不同。这是搜索预算，与最终要展示多少条视频也不同。

## 一次请求里的路径怎样继续

文章把整个搜索交给 EngineCore 管理。前端提交请求后，调度器安排用户历史的 prefill，worker 计算第一步分数，设备上的选择逻辑保存幸存 token、累计分数及父路径。下一步 decode 按父路径读取正确的 KV，继续扩展，最后一次性返回候选和分数。[架构说明](https://vllm.ai/blog/2026-11-24-vllm-gr-announcement)

关键是保存父路径关系。若上一轮第二条路径在新一轮分裂成两条，这两个孩子都需要继承同一个父路径的状态。只把分数排序而没有同步选择对应 KV，会让模型在错误历史上继续生成，即使结果长度与 API 格式完全正确。

```text
用户历史 prefill → 共享历史 KV → 多条 SID 前缀
                                 ↓
                       过滤并选择候选
                                 ↓
                   按父路径继承后缀 KV，继续生成
                                 ↓
                       完整 SID 与序列分数
```

所有路径共享相同用户历史，因此可以共同访问 prompt KV；路径已经生成的后缀则必须按分支区分。共享可以减少对长历史的重复拷贝，但后缀、临时候选数组和搜索状态仍会随搜索宽度变化。

搜索的一轮输出决定下一轮有哪些路径、各自继承谁的状态。如果前端每轮都重新请求引擎，就要反复搬交这些关系并等待主机往返。vLLM-GR 在引擎内保存和推进循环，又让主机准备与设备执行重叠，减少这段协调等待。模型计算、分支状态管理和最终结果回主机仍要完成。

## 目录约束必须在前缀上生效

一个分量在词表里合法，不表示它与之前的分量组合后就是现存条目。例如目录允许 `A-X-1` 和 `B-Z-3`，词表仍可能生成 `A-Z-3`。完整生成后才删除无效 ID，会浪费搜索名额，甚至返回很少候选。

目录约束可以在每一轮只允许仍有合法后续的前缀。这样，当路径为 `A` 时，只有真实目录里的下一层可选。文章示意图同样在中间步骤排除不存在的前缀。约束只是保证成员资格，相关性仍由模型及后续策略判断。[目录过滤示意](https://vllm.ai/blog/2026-11-24-vllm-gr-announcement)

下面的自拟 Python 示例展示词表组合和目录之间的差别，可以直接运行。

```python
from itertools import product

catalog = {("A", "X", "1"), ("A", "Y", "2"), ("B", "Z", "3")}
vocabulary = [sorted({sid[i] for sid in catalog}) for i in range(3)]
combinations = set(product(*vocabulary))

def allowed_next(prefix):
    return sorted({sid[len(prefix)] for sid in catalog
                   if sid[:len(prefix)] == prefix and len(prefix) < len(sid)})

print(len(combinations), len(combinations & catalog))  # 18 3
print(allowed_next(("A",)))  # ['X', 'Y']
print(allowed_next(("A", "Z")))  # []
```

这里没有运行神经网络或模拟 beam 的概率排序，只检查了目录前缀的成员关系。正式服务还要保证约束数据和 tokenizer 匹配：更换 tokenizer 后，相同字符串可能编码成不同 token。约束制品记录数据和 tokenizer 的 digest，就能检查这两个条件。

目录成员资格也只是业务条件的一部分。下架、地区限制、库存、重复 SID 或用户资格，仍需目录维护和返回前的业务检查。不能把合法 SID 自动解释为任何用户都可以消费的条目。

## 已实现的服务范围与路线图分开看

本文引用的代码版本为 `dda07adc0fee8e269d89c0d82359e778bfa72b10`。README 将项目描述为 vLLM 的独立扩展，当前模型支持列出 OneRec-1.7B，输出是按序列似然排列的候选 SID；给外部候选集打分的排序路径仍属计划。架构图中出现 HSTU、OneTrans 等例子，不等于本版本已完整支持它们。[固定版本 README](https://github.com/vllm-project/vllm-gr/blob/dda07adc0fee8e269d89c0d82359e778bfa72b10/README.md)

发布页说明 vLLM-GR 0.30.0 基于 vLLM 0.30.0，支持 NVIDIA CUDA 与 Ascend NPU。核对时的离线 V1 文档还列出限制：使用异步调度，逻辑 batch 为 1—8，并行规模参数为 1，不支持把 speculative decoding、LoRA、量化、混合模型等功能直接与该 V1 beam 会话组合。当前目录表的受约束生成要求三个有效 token。[离线接口与限制](https://github.com/vllm-project/vllm-gr/blob/dda07adc0fee8e269d89c0d82359e778bfa72b10/examples/offline_inference/beam_search/README.md)

这些限制属于特定路径和核对版本。不能因为底层来自 vLLM，就推断上游的全部特性都可以组合使用。部署前应对照自己的硬件、模型和目录形式核对兼容性。

README 还区分权重更新与目录更新：权重更新需要暂停并排空实例；线上目录替换要求 CUDA 上的异步 beam 执行。实际系统应在切换时保存模型、tokenizer、目录和约束制品的对应版本，避免生成器使用新权重而映射仍沿旧目录。

## P99 图证明了什么

发布文章测量的是候选生成的尾延迟。概览图输入长度固定为 1,024 token，比较 beam width 128 或 256、batch size 1、4、8，以及多种 GPU/NPU。不同图来自不同设置，正文保留了候选池、约束开关与计时范围差异。[性能评估](https://vllm.ai/blog/2026-11-24-vllm-gr-announcement)

| 场景 | vLLM-GR P99 | 对照 P99 | 应怎样读 |
| --- | ---: | ---: | --- |
| H20，width 256，batch 8 | 369.4 ms | SGLang 1,280.1 ms；NVIDIA SID-GR 428.1 ms | 此配置中 GR 延迟较低，不能外推所有负载 |
| RTX PRO 6000，width 256，batch 1 | 29.21 ms | NVIDIA SID-GR 28.25 ms | 此配置中对照略低 |
| A2，width 256，batch 8 | 312.69 ms | xLLM 324.60 ms | 两者均启用目录表，仍需核对其他设置 |

表中数字均为发布方测试。RTX PRO 6000 的说明最具体：OneRec-1.7B、BF16、合成输入、生成三个 token、禁用目录约束，三次预热后计时 48 个 batch。计时覆盖整 batch 和候选回主机，排除 HTTP。GR 与 NVIDIA SID-GR 的候选池为 W，SGLang Beam 为 2W，因此搜索工作量并非完全相同。

其他比较的完整 backend revision 与部分预热次数未记录；Ascend 比较里 SGLang 的约束设置也没有记录。P99 对样本数敏感，48 次计时能提示尾延迟，却不足以稳定刻画罕见长尾。单请求 batch 的计时结果还没有覆盖线上队列、突发流量与服务端过载。

同一硬件上，batch 或 beam width 改变后领先者也可能变化。先固定输入、候选质量及计时范围，再讨论性能收益，比抽出图中的最大倍数更有用。

## 推荐质量仍要单独评估

更宽的 beam search 可能找到概率更高的路径，却不保证更好的点击、留存、购买或内容多样性。训练目标、样本分布与目录映射决定序列概率怎样对应用户偏好，线上服务还需要过滤、去重和排序。

一个可实施的验证顺序，是先对小目录核对全部输出的成员关系、父路径 KV 和分数，再固定模型与真实输入比较搜索预算，最后做自己的离线相关性和线上业务评估。冷缓存、热缓存、目录切换、空目录和过载都属于值得检验的条件。这是本文提出的验证设计，未将其写成已有产品收益。

把返回结果接进业务之前，需要知道每个 ID 怎样映射回条目，分数是序列似然还是另一种排序分数，以及搜索预算限制了哪些候选。接口返回成功只确认取得了一组结果，成员资格、业务可用性和推荐效果仍需各自检查。

**资料范围：** 依据 vLLM 发布文和固定版本源码。比较的候选池、约束开关及计时范围并非全部一致，性能数据为发布方测量。
