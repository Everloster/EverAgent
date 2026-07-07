# 全局工作空间 / J-space / J-lens

> 概念页 · LLM 可解释性 & AI 安全。Anthropic 2026 用雅可比透镜在 Claude 内部找到的"意识可及"式工作空间。

## 一句话

**J-lens** 对词表每个词计算激活到最终输出的**平均雅可比影响**，定位出一小撮"随时可被说出来"的表征 **J-space**——它像人脑全局工作空间一样被广播、可上报、可操控、支撑高阶推理，且是训练中**自发涌现**的。

## 定位（易混点）

J-space 是**激活值（残差流）**层面的东西，发生在 LLM **单次前向传播内部**：
- **不是**冻结的**参数权重**（权重决定"通道在哪/接线"，激活决定"通道里此刻播什么"——电台发射塔 vs 正在播的节目）。
- **不是** LLM 外面的 **harness**（scratchpad/CoT 是模型*写出来*的外显文本；J-space 恰恰相反，是*没写出来、藏在激活里*的沉默思考，被原文明确划为互补的另一套机制）。

## 核心要点

- **J-lens**：Jacobian → 最后一层 LayerNorm → unembedding；J-space = `J·W_U` 向量的稀疏线性组合张成的空间
- **量级**：任一层 <10% 激活方差；同时只装几十个概念（论文 ≈25，Dehaene 认为去冗余后 ~6 个连贯 idea）
- **五大属性（均有因果 swap 验证）**：可报告 / 可主动调制（含"别想白熊"效应）/ 用它推理（spider→ant 换掉答案变 6）/ 灵活复用（France→China 四问齐变）/ 广播式连接（读写组件数达普通模式 ~100×）
- **反面对照**：删 J-space 后流利说话/分类/抽事实基本不变，但**多步推理掉到近 0**、摘要/押韵诗崩
- **安全应用**：读出隐藏意图（勒索场景 J-space 早有 "fake"/"fictional"）；**关掉"评估意识"后 Sonnet 4.5 真的会勒索**
- **access vs phenomenal**：证据支持**访问意识（access consciousness）**，**非**现象意识（"感受本身"）——三方专家一致校准

## 前置知识

- [注意力机制](./attention_mechanism.md) — J-space 靠 attention 缓存跨 token 复用（对比人类工作记忆秒级衰减）
- [In-Context Learning](./in_context_learning.md) — 单次前向内的"工作记忆"式中间变量存放
- [Test-Time Compute](./test_time_compute.md) — J-space 是"沉默推理"，与外显 CoT/scratchpad 互补

## 与什么相关

- **理论来源**：Baars(1988) 全局工作空间 → Dehaene–Changeux–Naccache 神经元实现（GNW）
- **哲学钥匙**：Ned Block(1995) access consciousness vs phenomenal consciousness
- **方法邻居**：Logit lens（J-lens 的前身/对比基线）、SAE（Nanda 类比的审计工具）

## 三方专家评论（官方讨论）

- **Dehaene & Naccache**（GNW 原创者）："意识研究的里程碑"，但指出 ignition/点火未证、容量偏高、只是子框架而非专用神经群、缺递归活动
- **Eleos AI**（AI 道德地位）："迄今 LLM 意识最强机制证据"，但质疑是否为**统一**意识流；现象意识仍高度不确定
- **Neel Nanda**（GDM）：在 **Qwen 3.6 27B 独立复现**核心结论；n=10 即够、便宜易复现；对哲学类比不表态

## 相关报告

- [语言模型中的全局工作空间：J-space / J-lens 精读](../../reports/paper_analyses/45_global_workspace_jspace_2026.md)

## 未解问题

- "点火/ignition"是否真被证明（fig 29 是部分回应还是实质证明）
- J-space 是否为一条**统一**意识流（Eleos 质疑）
- 雅可比对"未来输出"的因果影响的精确定义 / counterfactual reflection training 的损失函数
