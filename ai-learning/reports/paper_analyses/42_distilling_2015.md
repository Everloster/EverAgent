---
title: "Distilling the Knowledge in a Neural Network"
domain: "ai-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-04-25"
---

# Distilling the Knowledge in a Neural Network

## 📋 基本信息卡片

```text
论文标题：Distilling the Knowledge in a Neural Network
作者：Geoffrey Hinton, Oriol Vinyals, Jeff Dean
机构：Google Inc.; Hinton 另隶属 University of Toronto 与 Canadian Institute for Advanced Research
发表年份：2015
发表场所：arXiv 1503.02531v1, stat.ML, 2015-03-09
核心主题：知识蒸馏、软标签、模型压缩、教师-学生训练
重要性评级：⭐⭐⭐
```

---

## 🎯 一句话总结

> 这篇论文把“大模型或集成模型学到的泛化方式”定义为输出分布，并用高温 softmax 软标签把它迁移到更易部署的小模型中。

---

## 读前定位

这篇论文不是第一篇“模型压缩”论文。

它明确承接 Caruana 等人的模型压缩工作，但给出了一个更通用、更容易复用的训练形式：用教师模型在高温 softmax 下产生软目标，用学生模型在同一温度下拟合这些软目标，训练完成后再把学生模型温度设回 1。

它的历史价值在于三点。

第一，它让“知识”从参数值中解放出来，转化为输入到输出的函数映射。

第二，它把错误类别之间的相对概率视为有用信息，而不是噪声。

第三，它证明蒸馏不只是 MNIST 玩具实验，也能迁移到商业语音识别声学模型和超大图像分类数据集 JFT。

---

## 🌍 Step 1 | 背景与动机（WHY）

### 1.1 论文要解决的问题

集成模型通常能提高机器学习性能：训练多个模型，再平均它们的预测。

问题是部署阶段不同于训练阶段。

训练可以慢，可以消耗大量计算，可以使用多个模型。

部署要面对延迟、吞吐、内存、能耗和用户规模。

论文用“昆虫幼虫与成虫”的类比说明这个矛盾：训练阶段和部署阶段目标不同，所以模型形态也不必相同。

这就是蒸馏的动机：

- 训练阶段使用 cumbersome model：大模型、强正则模型、集成模型。
- 部署阶段使用 distilled model：小模型、单模型、低延迟模型。
- 中间通过软目标把教师的泛化行为迁移给学生。

### 1.2 在它之前怎么做

论文提到 Caruana 等人已经证明，大型集成模型获得的知识可以转移到单个小模型。

Caruana 路线使用的是 logits 作为目标，让小模型最小化教师 logits 和学生 logits 之间的平方差。

Hinton、Vinyals、Dean 的改动是：不用直接拟合 logits，而是提高 softmax 温度，让教师输出更“软”的类别分布，再用交叉熵训练学生。

这样一来，蒸馏可以兼容概率分布、交叉熵、硬标签联合训练，并且在高温极限下还能解释 logits matching 为什么成立。

### 1.3 为什么软标签有信息

硬标签只告诉学生：“这张图是 2。”

软标签还告诉学生：“这张 2 更像 3，还是更像 7。”

论文给出的直觉例子是：

- 某个 2 被误认为 3 的概率可能是 `10^-6`。
- 同一个 2 被误认为 7 的概率可能是 `10^-9`。
- 对另一个 2，这两个概率关系可能反过来。

这些极小概率的比例构成了类别间相似性结构。

普通 one-hot 训练会丢掉这种结构。

高温 softmax 会把这些低概率类别抬起来，让它们对交叉熵梯度产生更明显的作用。

---

## 💡 Step 2 | 核心贡献（WHAT）

### 2.1 贡献一：高温 softmax 蒸馏

神经网络通常用 softmax 把每个类别的 logit `z_i` 转成概率 `q_i`。

论文定义温度 `T`：

```text
q_i = exp(z_i / T) / Σ_j exp(z_j / T)
```

当 `T = 1` 时，就是常规 softmax。

当 `T > 1` 时，分布更平滑，错误类别的概率被放大，类别间暗知识更容易被学生模型学习。

蒸馏流程是：

1. 用教师模型在高温 `T` 下生成 soft target。
2. 用学生模型在同样高温 `T` 下拟合 soft target。
3. 训练完成后，学生模型推理时恢复 `T = 1`。

### 2.2 贡献二：软标签和硬标签联合训练

如果 transfer set 有真实标签，论文不建议只改写 soft target。

作者发现更好的做法是用两个目标函数的加权平均：

- 高温下对教师 soft target 的交叉熵。
- 温度 1 下对真实 hard label 的交叉熵。

论文还指出，soft target 产生的梯度幅度随 `1/T^2` 缩放。

因此，当同时使用软标签和硬标签时，需要把 soft-target 目标乘以 `T^2`，避免调温度时改变两个目标的相对贡献。

### 2.3 贡献三：logits matching 是蒸馏的特例

论文推导了一个关键结论：

在温度相对于 logits 足够高，并且每个样本的教师 logits 与学生 logits 都分别做零均值处理时，蒸馏的交叉熵梯度近似为：

```text
∂C / ∂z_i ≈ (z_i - v_i) / (N T^2)
```

其中：

- `z_i` 是学生模型第 `i` 类 logit。
- `v_i` 是教师模型第 `i` 类 logit。
- `N` 是类别数。
- `T` 是蒸馏温度。

所以在高温极限下，蒸馏等价于最小化教师与学生 logits 的平方差。

这解释了 Caruana logits matching 的有效性，也说明 Hinton 版本是更一般的形式。

### 2.4 贡献四：specialist models

论文不只讨论“小模型压缩”。

它还提出了一种适合超大分类任务的 specialists ensemble：

- 一个 generalist model 覆盖所有类别。
- 多个 specialist models 只关注容易混淆的类别簇。
- specialist 把无关类别合并为 dustbin class，从而缩小 softmax。
- 每个 specialist 从 generalist 权重初始化，独立快速训练。

这与 Mixture of Experts 不同。

MoE 用 gating network 动态分配样本，训练时专家之间强耦合。

specialist 路线先用 generalist 的混淆结构定义类别簇，然后 specialists 独立训练，更容易并行。

---

## 🔍 Step 3 | 技术细节（HOW）

### 3.1 蒸馏算法

```text
输入：
  教师模型 F
  学生模型 f
  transfer set D
  温度 T
  hard-label loss 权重 α

训练：
  对每个样本 x:
    p_T = softmax(F(x) / T)
    q_T = softmax(f(x) / T)
    q_1 = softmax(f(x) / 1)

    L_soft = CE(p_T, q_T)
    L_hard = CE(y, q_1)
    L = T^2 * L_soft + α * L_hard

推理：
  使用 softmax(f(x) / 1)
```

论文在语音识别实验中尝试温度 `[1, 2, 5, 10]`，并对 hard-target 交叉熵使用 `0.5` 的相对权重。

表 1 所用最佳温度在原文排版中用粗体标出，但纯文本提取无法保留粗体；因此本报告只记录候选温度集合与硬标签权重，不额外推断最佳温度值。

### 3.2 为什么温度不是越高越好

高温会让所有类别概率更平均，从而暴露低概率类别的相对关系。

但论文也指出，在较低温度下，蒸馏会更少关注远低于平均值的负 logits。

这可能是好事，因为非常负的 logits 在教师训练目标中约束较弱，可能噪声更大。

MNIST 小学生模型实验支持这个判断：

- 当学生每层有 `300` 个或更多隐藏单元时，所有大于 `8` 的温度结果相近。
- 当学生被缩小到每层 `30` 个隐藏单元时，`2.5` 到 `4` 的温度明显优于更高或更低温度。

这说明温度是容量相关的超参数。

学生越小，越需要忽略一部分过细、过噪的暗知识。

### 3.3 transfer set 可以没有标签

论文强调，transfer set 可以完全由无标签数据构成。

如果有真实标签，则可以把硬标签目标作为辅助项。

这点在后来半监督学习、模型压缩、数据蒸馏、伪标签训练中都非常重要：教师模型可以把无标签样本变成带有丰富分布信息的训练样本。

---

## 📊 Step 4 | 实验验证

### 4.1 MNIST 初步实验

教师模型设置：

- 单个大网络。
- 两个隐藏层。
- 每层 `1200` 个 ReLU 隐藏单元。
- 使用 dropout 和 weight constraints 强正则。
- 输入图像在任意方向 jitter 最多 `2` 像素。
- 在 MNIST 测试集上得到 `67` 个错误。

普通学生模型：

- 两个隐藏层。
- 每层 `800` 个 ReLU 隐藏单元。
- 无正则。
- 测试错误数 `146`。

蒸馏学生模型：

- 同样是较小网络。
- 只通过匹配大网络在温度 `20` 下产生的 soft targets 进行正则化。
- 测试错误数降到 `74`。

这个结果说明：学生没有显式看到平移增强样本，却通过教师软目标获得了教师从平移增强中学到的泛化方式。

### 4.2 MNIST 缺类 transfer set

论文做了一个非常有解释力的实验：从 transfer set 中删除所有数字 `3`。

这意味着从学生视角看，`3` 是一个从未见过的“神话数字”。

结果：

- 删除所有 `3` 后，学生模型测试错误数为 `206`。
- 其中 `133` 个错误发生在测试集的 `1010` 个 `3` 上。
- 如果把 `3` 类 bias 增加 `3.5`，总错误数变为 `109`。
- 此时 `3` 上的错误数降到 `14`。
- 换句话说，在合适 bias 下，学生从未在训练中见过 `3`，仍能正确识别 `98.6%` 的测试 `3`。

另一个极端设置：

- transfer set 只包含训练集里的 `7` 和 `8`。
- 初始测试错误率为 `47.3%`。
- 将 `7` 和 `8` 的 bias 减少 `7.6` 后，测试错误率降到 `13.2%`。

这个实验非常关键：软目标不只是“标签平滑”，它携带了教师对整个类别空间的函数结构。

### 4.3 商业语音识别声学模型

语音识别实验使用的是 DNN acoustic model。

模型设置：

- `8` 个隐藏层。
- 每层 `2560` 个 ReLU 单元。
- 最终 softmax 有 `14,000` 个 HMM targets。
- 输入是 `26` 帧 `40` 维 Mel-scaled filterbank coefficients。
- 每帧 advance 为 `10ms`。
- 预测第 `21` 帧的 HMM state。
- 参数总数原文称 `about 85M`。
- 训练数据为 `2000` 小时英语语音。
- 训练样本数为 `700M`。

基线系统：

| 系统 | Test Frame Accuracy | WER |
|------|---------------------|-----|
| Baseline | 58.9% | 10.9% |
| 10x Ensemble | 61.1% | 10.7% |
| Distilled Single model | 60.8% | 10.7% |

论文结论是：10 模型集成带来的 frame accuracy 提升，大于 `80%` 被迁移到了单个蒸馏模型中。

WER 的改进较小，论文解释为 frame-level 训练目标与最终 WER 目标之间存在 mismatch。

即便如此，集成在 WER 上获得的改进也被单模型蒸馏继承了。

### 4.4 JFT specialists

JFT 是 Google 内部图像数据集：

- `100 million` labeled images。
- `15,000` labels。
- baseline 是深度卷积网络。
- baseline 训练时间为 `about six months`。

完整集成训练在这种规模下成本过高，所以论文训练 specialists。

specialist 设置：

- 训练 `61` 个 specialist models。
- 每个 specialist 覆盖 `300` 个类，外加 dustbin class。
- 类簇来自 generalist 预测分布协方差矩阵的在线 K-means 聚类。
- 推理时先用 generalist 取 top-1 类，再激活与该类相交的 specialists。

JFT top-1 结果：

| 系统 | Conditional Test Accuracy | Test Accuracy |
|------|---------------------------|---------------|
| Baseline | 43.1% | 25.0% |
| + 61 Specialist models | 45.9% | 26.1% |

论文称，`61` 个 specialists 带来整体 test accuracy 的 `4.4%` 相对提升。

表 4 还显示，正确类别被越多 specialists 覆盖，top-1 相对提升通常越高：

- 覆盖 `1` 个 specialist：相对提升 `+3.4%`。
- 覆盖 `5` 个 specialists：相对提升 `+11.1%`。
- 覆盖 `9` 个 specialists：相对提升 `+16.6%`。
- 覆盖 `10 or more`：相对提升 `+14.1%`。

### 4.5 soft targets 作为正则器

论文最后用语音模型验证：soft targets 能在少量数据下显著缓解过拟合。

表 5：

| 系统与训练集 | Train Frame Accuracy | Test Frame Accuracy |
|--------------|----------------------|---------------------|
| Baseline, 100% training set | 63.4% | 58.9% |
| Baseline, 3% training set | 67.3% | 44.5% |
| Soft Targets, 3% training set | 65.4% | 57.0% |

这里 `3%` 训练集对应 `about 20M examples`。

硬标签训练在少量数据上训练准确率更高，但测试准确率崩到 `44.5%`。

软标签训练测试准确率达到 `57.0%`，只比全量数据基线的 `58.9%` 低 `1.9` 个百分点。

这说明教师输出分布本身是强正则器。

---

## 🌱 Step 5 | 历史叙事与影响力

### 5.1 前驱

```text
Caruana model compression
        ↓
logits matching
        ↓
Hinton / Vinyals / Dean 2015
        ↓
temperature softmax + soft targets + hard targets
```

这篇论文把模型压缩从经验技巧整理成了可复用范式。

它也给后来“教师-学生”语言提供了标准概念：

- teacher / cumbersome model
- student / distilled model
- soft targets
- temperature
- transfer set
- dark knowledge

### 5.2 与后续技术的关系

后来的很多路线都能看到这篇论文的影子：

- BERT/Transformer 时代的模型压缩，如 DistilBERT、TinyBERT。
- 大模型蒸馏到小模型的 instruction distillation。
- 视觉基础模型中的自蒸馏与教师特征重建。
- 半监督学习里的伪标签与软标签。
- 多模型 ensemble 的部署压缩。

需要注意的是，本论文没有研究现代 LLM 的 chain-of-thought 蒸馏，也没有讨论 RLHF 或 DPO。

它给出的核心机制仍然是分类概率分布上的教师-学生迁移。

### 5.3 在 AI 发展史中的位置

这篇论文处在 2012 AlexNet 之后、2017 Transformer 之前。

当时深度学习已经证明“大模型 + 大数据 + 强训练”很有效，但工业部署仍然受计算成本限制。

知识蒸馏解决的是深度学习走向产品化时的关键矛盾：

```text
训练时追求最大能力
部署时追求最小成本
蒸馏负责把能力迁移到可部署形态
```

这个矛盾在 2020 年后 LLM 时代更明显。

因此，2015 年这篇论文可以看成“能力-成本分离”的早期系统化表达。

---

## 🛠 Step 6 | 工程实践

### 6.1 复现最小版本

最小复现可以从 MNIST 开始：

1. 训练一个强教师：两层 `1200` ReLU、dropout、weight constraints、最多 `2` 像素 jitter。
2. 训练一个弱学生：两层 `800` ReLU，无常规正则。
3. 用教师在 `T = 20` 下输出 soft targets。
4. 学生用 soft-target 交叉熵训练。
5. 学生推理时使用 `T = 1`。

关键不是完全复刻 2015 年模型，而是复刻对照：

- 学生 hard labels-only。
- 学生 soft targets-only。
- 学生 soft targets + hard labels。
- 不同温度。
- 不同学生容量。

### 6.2 超参数注意点

温度：

- 高温会释放更多暗知识。
- 过高温度可能让小容量学生被噪声拖累。
- 论文中每层 `30` 隐藏单元的极小学生，在 `2.5` 到 `4` 温度更好。

hard-label 权重：

- 如果 transfer set 有标签，加入 hard-label loss 往往更稳。
- 论文语音实验使用 hard-target 交叉熵相对权重 `0.5`。

梯度尺度：

- soft-target loss 需要乘以 `T^2`。
- 否则改温度会同时改 loss 权重，难以比较实验。

### 6.3 常见坑

第一，不能把蒸馏理解成只复制 top-1 标签。

蒸馏的价值恰恰在非 top-1 类别的相对概率。

第二，不能忘记训练温度和推理温度不同。

学生训练时用高温匹配教师，推理时回到 `T = 1`。

第三，不能无脑升温。

极小学生可能更适合中等温度，因为它没有容量拟合所有负 logits 的细节。

第四，评估指标要和业务目标对齐。

语音实验里 frame accuracy 的提升转移更充分，而 WER 提升较小，原因是训练目标与解码后的 WER 不完全一致。

---

## 🤔 Step 7 | 个人评价与学习建议

### 7.1 影响力评分

| 维度 | 评分 | 理由 |
|------|------|------|
| 概念影响 | 5/5 | 定义了知识蒸馏的主流语言与训练范式 |
| 实验说服力 | 4/5 | MNIST、商业 ASR、JFT 三类实验覆盖面广 |
| 理论完整性 | 3/5 | 有 logits matching 推导，但不是完整泛化理论 |
| 工程可复用性 | 5/5 | 温度、软硬标签联合、T² 缩放直接可实现 |
| 当代相关性 | 5/5 | 大模型压缩、开源小模型、视觉自蒸馏仍在使用 |

### 7.2 最重要的洞察

知识不等于参数。

知识也不只是正确答案。

知识是模型对整个输出空间的结构化判断。

当教师说“这是 2”时，真正有价值的是它同时表达了“它有一点像 3，几乎不像 7，更不像 carrot”。

这种相似性结构，是 hard label 永远表达不出来的。

### 7.3 局限与未覆盖问题

论文没有解决以下问题：

- 如何蒸馏生成式语言模型的长文本行为。
- 如何蒸馏多步推理过程。
- 如何在没有高质量教师时避免学生继承教师偏差。
- 如何选择最佳 transfer set。
- 如何蒸馏 specialist ensemble 回单个大 generalist，论文在讨论中明确说尚未证明这一点。

### 7.4 学习优先级建议

建议在读完以下内容后阅读本论文：

1. Softmax 与交叉熵。
2. Dropout 与 ensemble 直觉。
3. AlexNet 时代的深度学习部署问题。
4. 基本语音识别 HMM-DNN 框架。

读完本论文后，适合继续读：

1. DistilBERT / TinyBERT 等 Transformer 蒸馏工作。
2. DINO / DINOv2 等视觉自蒸馏路线。
3. 大模型 instruction distillation 与 synthetic data distillation。
4. MoE 与 specialist/generalist 的关系。

---

## 🧩 关联学习

### 知识图谱位置

```text
Model Compression (Caruana)
        ↓
Distilling the Knowledge in a Neural Network (2015)
        ↓
Teacher-Student Learning
        ↓
DistilBERT / TinyBERT / DINO / DINOv2 / LLM distillation
```

### 与本项目已有报告的连接

- [AlexNet 2012](./06_alexnet_2012.md)：Hinton 系深度学习复兴背景。
- [MoE 2017](./21_moe_2017.md)：Hinton 与 Dean 后续参与的大规模条件计算路线。
- [DINOv2 2023](./35_dinov2_2023.md)：现代视觉自监督中继续使用教师-学生与蒸馏思想。
- [EVA-02 2023](./41_eva02_2023.md)：以 CLIP 特征作为 MIM 重建目标，也可视为教师特征蒸馏的视觉基础模型路线。

### 最小记忆卡片

```text
论文：Hinton, Vinyals, Dean 2015
主题：知识蒸馏
核心：高温 softmax 软标签
公式：softmax(z_i / T)
关键实验：MNIST 146→74 errors；ASR 10x ensemble WER 10.7%，蒸馏单模型 WER 10.7%
工程要点：soft loss 乘 T²；训练高温，推理 T=1；可联合 hard labels
历史地位：教师-学生模型压缩范式标准化
```
