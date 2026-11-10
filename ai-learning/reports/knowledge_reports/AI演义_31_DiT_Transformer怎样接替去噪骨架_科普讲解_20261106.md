---
title: "AI演义·31｜DiT：用Transformer承担扩散去噪"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-10"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["ai_history", "diffusion_transformer", "vision_transformer", "scaling", "generative_models"]
revision_scope: "文字与结构修订；保留原稿技术资料和历史核验记录，未重新复现实验。"
---

# AI演义·31｜DiT：用Transformer承担扩散去噪

[返回总览第 31 节](../AI演义_笔记分析与项目整合报告.md#paper-dit) · [上一章：Stable Diffusion v1.4](AI演义_30_StableDiffusion_v14_文生图系统怎样协同工作_科普讲解_20261106.md) · [继续读：技术史的两种视角](../AI演义_笔记分析与项目整合报告.md#lenses)

潜空间、噪声预测、采样和解码都可以保留，反复去噪的网络却未必必须是U-Net。DiT将这一部分改为接近ViT的Transformer，研究网络大小、输入token与计算量怎样影响生成。

本章使用*Scalable Diffusion Models with Transformers*的2023-03-02 v2，首版为2022-12-19。[^paper] DiT即Diffusion Transformer。花照用于说明表示，原实验主要是ImageNet类别条件，不是自由文本生成。

<a id="backbone-not-framework"></a>

## 1. 更换去噪网络，保留扩散方法

U-Net的多尺度与跳跃连接适合图像，DDPM又沿用既有视觉组件。但扩散只要求网络在不同噪声级别预测，并未限定骨架。到本篇时，扩散U-Net已含空间自注意力，DiT不是首次让其交换全局信息。[^background]

<a id="what-changes"></a>

```text
潜空间噪声 → U-Net 反复预测 → 采样器更新 → 最终潜表示 → 图像解码器
```

改为：

```text
潜空间噪声 → Transformer 反复预测 → 采样器更新 → 最终潜表示 → 图像解码器
```

作者复用Stable Diffusion的预训练8倍下采样VAE，在该潜空间重新训练类别条件DiT。[^architecture] 不是直接改名或移植v1.4的U-Net权重，图像编解码器也仍为卷积网络，整个系统不要求消除所有卷积。

<a id="patches-and-tokens"></a>

## 2. 在潜网格上切块

256×256图像经编码成为32×32×4潜表示，加噪后按块映射为token，加入位置表示，再进入Transformer。[^patchify] p＝2时每块覆盖潜空间2×2位置，共16×16＝256块；它不是原图2像素的块，也不是待生成的文字。

| 潜空间块边长p | token数 |
|---|---:|
| 8 | 16 |
| 4 | 64 |
| 2 | 256 |

边长减半、token四倍，同一组参数处理更多位置，计算可以显著增加而参数近似不变。注意力与前馈层建立空间特征联系，但能交换信息不保证已正确识别所有对象关系。

<a id="conditional-blocks"></a>

## 3. 时间与类别怎样进入网络

| 条件块 | 做法 |
|---|---|
| In-context | 将时间与类别作为额外token加入图像序列 |
| Cross-attention | 条件另成序列，由图像token交叉读取 |
| adaLN | 根据条件生成归一化后的缩放与平移 |
| adaLN-Zero | 另控制残差分支输出，以零初始化安排起点 |

这里in-context只指额外条件token，不是提供少量问答示例。adaLN的同层条件参数在各token共享，与逐位置读取长文本的交叉注意力形式不同，类别实验不能证明其在任意文字任务都更好。[^conditioning]

adaLN-Zero让残差输出的缩放从零起步，使每个块初始化为恒等映射，再学习修正，可联系 [ResNet](AI演义_03_ResNet_深层网络如何训练_科普讲解_20261104.md)。它没有将所有权重置零，也不表示完整网络的最终输出等于输入。

XL/2训练400,000步、无额外CFG、50,000生成样本、ft-MSE解码器时，FID依次为35.24、26.14、25.21、19.47。[^block-results] FID为特征分布差异，越低越好。adaLN约6亿参数，adaLN-Zero约6.75亿，计算和条件层也不同，不能将全部差异单独归因于零初始化。

[CFG](AI演义_30_StableDiffusion_v14_文生图系统怎样协同工作_科普讲解_20261106.md#cfg)组合条件与无条件预测；“无额外CFG”仍使用类别条件，只不额外强化。

<a id="output-and-training"></a>

## 4. 输出仍供下一步采样使用

每个token映射回小块，按位置恢复网格，输出噪声预测和反向采样所需的对角协方差参数。[^output] 对角形式不预测所有像素两两关系的巨大矩阵；整理token也不同于最后由VAE解码成像素。

采样器利用输出更新潜状态，再调用网络。整组token可同时处理，不意味着一次完成生成，也不是按语言自回归方式逐块生成。

训练程序先将真实图编码为潜表示，再加入已知噪声。DiT给出噪声预测和反向协方差参数，两部分用不同目标学习：噪声预测与实际噪声计算简化平方误差，协方差参数使用相应的变分目标。因此，DiT沿用了扩散训练框架，也学习反向协方差；早期DDPM的固定方差配置不能直接套到这里。

ImageNet实验batch 256，AdamW恒定学习率0.0001，无权重衰减与warmup，主要增强为水平翻转，评价使用平滑后的EMA参数。[^setup] 这是本篇有效配置，不是所有Transformer均无需warmup的建议。

<a id="scaling"></a>

## 5. 参数规模与输入长度是两条计算轴

作者组合S、B、L、XL四档深宽与p＝8、4、2，共12模型，先比较400,000步，再看总训练计算。[^scaling]

| XL模型，256×256 | 单次前向GFLOPs | 参数，约百万 | FID，无额外CFG |
|---|---:|---:|---:|
| XL/8 | 7.39 | 676 | 106.41 |
| XL/4 | 29.05 | 675 | 43.01 |
| XL/2 | 118.64 | 675 | 19.47 |

参数近似相同，细切块却增加计算并改善结果。GFLOPs计一次前向十亿浮点运算，不是设备每秒性能或完整生成成本，也不包括VAE参数与计算。

相同步数不等成本。Figure 9按“前向运算×batch×训练步×3”估算训练总量，3近似计入前向加反向，不是实测耗时。在较大共同预算下，大模型比延长小模型训练更划算，XL/2也逐渐超过XL/4，说明预算分配会影响结果。

规律限于所测ImageNet配置，不能无限外推，也未同时证明任意数据扩张或换任务有同样收益。

<a id="sampling-budget"></a>

## 6. 增加采样步数能否替代更好的模型

作者对训练400,000步的模型比较16、32、64、128、256、1000采样步：[^sampling-budget]

| 配置 | 每图估计采样计算 | FID-10K |
|---|---:|---:|
| L/2，1000步 | 80.7 TFLOPs | 25.9 |
| XL/2，128步 | 15.2 TFLOPs | 23.7 |

XL估计计算约为五分之一，FID仍更低，更多次询问较弱去噪器未必补足模型差距。它不否定增加步数的收益，结论需保留模型与训练阶段。FID-10K使用10,000样本，不能直接与后面FID-50K混比，运算量也不等墙钟时间。

<a id="benchmark-results"></a>

## 7. 最终结果的训练、引导与解码条件

最终256×256 XL/2训练7,000,000步，512×512版3,000,000步，均远长于前述消融。[^results]

### 256×256类别条件

Table 2用50,000生成样本、250步DDPM、ft-EMA图像解码器：

| 设置 | FID ↓ | Recall |
|---|---:|---:|
| 无额外CFG | 9.62 | 0.67 |
| CFG 1.25 | 3.22 | 0.62 |
| CFG 1.50 | 2.27 | 0.57 |

更强引导改善FID，覆盖度指标Recall下降，无额外引导也不是无条件。LDM-4在CFG 1.5为FID 3.60、Recall 0.48；StyleGAN-XL的FID为2.30。DiT的2.27最低，差距仍不能扩成每图或每种评价均大幅领先。

### 512×512类别条件

64×64×4潜网格按p＝2变成1024 token，前向524.6 GFLOPs。DiT在CFG 1.5为FID 3.04，优于所列此前扩散组合3.85，却弱于StyleGAN-XL的2.41。因此只能说超过表中此前扩散结果。

### 解码器与通道实现

同一个256×256 DiT、CFG 1.5，更换原解码器、ft-MSE、ft-EMA，FID为2.46、2.30、2.27。[^decoder] 三者编码器相同，只微调解码器，才能接收同一种潜表示，不证明任意VAE可互换。图像解码器版本名里的EMA也不同于DiT训练参数EMA。

主结果CFG作用于前三个潜通道，非全部四通道。附录四通道方案调整强度可得相近或更好数值，本章保留主表2.27，不跨配置挑最佳值。

<a id="cost-and-limits"></a>

## 8. 收益不能全归给Transformer

与巨大像素U-Net相比，潜空间模型还受益于表示压缩；与潜空间LDM-4相比，DiT-XL/2单次前向约118.6 GFLOPs，LDM-4约103.6，并非每次计算更省，而是在此规模取得更好样本指标。[^cost]

JAX与TPU-v3 pods训练中，重型XL/2在TPU v3-256、全局batch 256约5.7迭代/秒，这是训练吞吐，不是个人电脑出图速度。

采样仍多步，VAE仍损失信息，细token增加计算与存储；ImageNet类别结果也不覆盖开放文本、视频或完整安全评价。FID、IS、Precision/Recall各有范围，不能代替所有用途的验收。

<a id="history-and-synthesis"></a>

## 9. 技术路线在不同层次组合

ViT提供空间token，残差与初始化经验进入adaLN-Zero，DDPM提供噪声学习与采样，LDM提供压缩表示，CFG调整条件影响，规模实验再比较参数、token和训练／采样计算。旧方法没有随新名称出现而消失，而是承担不同部分。

原论文将DiT在Stable Diffusion、DALL·E 2等文生图系统中替换骨架列为未来方向，未完成现成开放文生图系统的直接替换评测。[^future] 相似Transformer骨架可能复用软件与硬件经验，可联系总览Hardware Lottery视角，但本篇未量化生态收益，也不保证现成优化原样可用。

William Peebles署名UC Berkeley，Saining Xie署名New York University；首页Peebles的星号说明工作在Meta AI的FAIR实习期间开展。[^people] 这不能证明后续任职、Sora团队谱系或具体视频架构。

<a id="three-questions"></a>

读到这里，可以把新论文的问题拆得更具体：当时的限制是什么，换了哪一部分，增加了什么资源，评价是否覆盖目标用途。[总览的两种技术史视角](../AI演义_笔记分析与项目整合报告.md#lenses)会进一步讨论方法之外的数据、硬件与研究环境。

<a id="sources-and-scope"></a>

## 来源与修订范围

本次沿用原稿对固定v2主文1–9页、附录A–D相关实现、模型表、采样和解码器的核验，未训练复现、测本机吞吐或逐图审全部生成样本。图像机制示意与实际类别实验保持区分。

讲义第50页，播客 **03:52:54–03:56:32**。[^podcast] 原有[转写核查记录](.quality/AI演义_31_DiT_Transformer怎样接替去噪骨架_科普讲解_20261106.transcription-review.json)保留，未重新听音或测字错率；人物现职与后续视频模型关系不在核验范围。

## 来源与延伸阅读

[^paper]: Peebles、Xie，[Scalable Diffusion Models with Transformers，v2](https://arxiv.org/pdf/2212.09748v2)；[官方版本记录](https://arxiv.org/abs/2212.09748v2)。首版 2022-12-19，所读版本 2023-03-02；[仓内 PDF](../../papers/27_dit_2022.pdf)。
[^background]: 原论文 §§1–2，扩散 U-Net 从 PixelCNN++ 等结构继承，已有低分辨率空间自注意力；作者研究标准 Transformer 作为去噪骨架，而非首次把注意力用于扩散。
[^architecture]: 原论文 §3.1 的 LDM 描述与 §4 的 Diffusion 设置：固定预训练卷积 VAE，潜空间中训练 Transformer 去噪网络；Figure 3 给出整体结构。
[^patchify]: 原论文 §3.2、Figure 4：256×256×3 图像对应 32×32×4 潜表示，p＝2、4、8；标准正弦—余弦位置表示，token 数由空间尺寸与块大小决定。
[^conditioning]: 原论文 §3.2、Figure 3、附录 A：四种条件块；adaLN 根据 t、类别的嵌入生成缩放和平移，adaLN-Zero 另控制残差输出，初始化块为恒等映射。
[^block-results]: 原论文 Figure 5 与 Table 4：XL/2、400K 训练步、FID-50K、无额外 CFG、ft-MSE 解码器。四种条件设计的完整参数量与计算量并不完全相等，不将比较缩成只有一个数字变化的实验。
[^output]: 原论文 §§3.1–3.2 的噪声和对角协方差输出、线性映射与重排，以及简化噪声目标和协方差的变分训练目标。
[^setup]: 原论文 §4：ImageNet 类别条件、AdamW、恒定学习率 1×10⁻⁴、batch 256、无权重衰减和 warmup、水平翻转、EMA 0.9999；评价默认 250 步 DDPM 与 ADM 的 TensorFlow 评价工具。
[^scaling]: 原论文 §5、Figures 6–9、Table 4。Table 4 中三档 XL 的具体 GFLOPs、参数与 FID；参数和 FLOPs 不包括 VAE。总训练计算使用前向运算量×batch×步数×3 估计，不是直接测得的耗电或墙钟时间。
[^sampling-budget]: 原论文 §5.2、Figure 10：12 个训练 400K 步的模型，六档采样步数；L/2 的 80.7 TFLOPs、FID-10K 25.9，对照 XL/2 的 15.2 TFLOPs、23.7。与最终 FID-50K 的协议分开。
[^results]: 原论文 §5.1、Tables 2–3：256×256 的 7M 训练步、512×512 的 3M 训练步；类别条件、50K 生成样本、250 步 DDPM，CFG 设置逐行区分。512×512 的 Precision/Recall 按原文另用 1000 个真实样本，本文不把该口径套到 FID。
[^decoder]: 原论文附录 A、D、Tables 4–5：扩展分析使用 ft-MSE，最终主表使用 ft-EMA；同一 DiT 更换解码器的 FID 为 2.46／2.30／2.27。附录 A 说明前三个潜通道的 CFG，以及不同四通道强度的另组结果。
[^cost]: 原论文 §§4–5.1、Tables 4、6：256² 的 DiT-XL/2 约 118.6 GFLOPs，LDM-4 主文写 103.6、附表取整为 104；模型计算不含全部生成链。TPU v3-256 的约 5.7 iterations/s 是训练吞吐。
[^future]: 原论文 §6，将在开放文生图系统中进一步探索 DiT 列为后续工作；没有在本文给出自由文本或视频生成的基准结论。
[^people]: 原论文首页作者与脚注。本文不依据讲义中的人物回顾，推导未另查原始材料的后续任职或视频模型贡献。
[^podcast]: [小宇宙节目与 shownotes](https://www.xiaoyuzhoufm.com/episode/68ff9d1b083a71a4eb86c52c)、[《AI演义》讲义](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf)第 50 页。若节目网页访问受限，可在小宇宙 App 按标题搜索。本文不公开私有转写原件。
