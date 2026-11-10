---
title: "AI演义·30｜Stable Diffusion v1.4：从提示词到像素图像"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-10"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["ai_history", "stable_diffusion", "text_to_image", "classifier_free_guidance", "latent_diffusion"]
revision_scope: "文字与结构修订；保留原稿技术资料和历史核验记录，未重新复现实验。"
---

# AI演义·30｜Stable Diffusion v1.4：从提示词到像素图像

[返回总览第 30 节](../AI演义_笔记分析与项目整合报告.md#paper-sd14) · [上一章：LDM](AI演义_29_LDM_潜空间怎样降低图像生成成本_科普讲解_20261106.md)

输入“窗边花瓶里的一朵红花”，系统要编码文字、在潜空间反复去噪，再解码成图。前一章解释LDM方法，本章固定看Stable Diffusion v1.4的权重、组件与参考程序。

中文只是教学示意，v1.4主要用英文图文训练，`a red flower in a vase by a window`更贴近其训练语言。[^card]

<a id="method-model-program"></a>

## 1. 方法、权重和执行程序

| 层次 | 对象 | 提供什么 |
|---|---|---|
| 方法 | LDM | 在可解码的压缩表示上进行扩散 |
| 模型 | v1.4 checkpoint | 选定组件与训练所得参数 |
| 程序 | CompVis脚本或Diffusers pipeline | 加载、采样、解码及输出处理 |

Checkpoint是保存的模型参数，加载方式要匹配文件组织。LDM v2的文本实验用BERT tokenizer与联合训练Transformer，v1.4则使用冻结CLIP文本编码器，需要分别查论文和模型卡。[^ldm] [^card]

一个具体加载问题是`use_ema: false`。EMA是训练中参数的指数移动平均，参考配置面向只存EMA参数的checkpoint，此时false表示不再从另一套参数切到EMA；若加载同时含两套参数的完整checkpoint，false才会使用非EMA权重。[^readme] 配置含义与所装文件有关，不能仅凭开关判断权重从未做EMA。

<a id="text-encoder"></a>

## 2. 文本条件来自未汇聚的序列表示

分词器将提示转成token，CLIP文本Transformer输出条件序列。Token不必是一词或一字。参考`FrozenCLIPEmbedder`返回`last_hidden_state`，保留不同位置的表示，区别于CLIP图文匹配使用的整体文本表示。[^encoder]

“CLIP ViT-L/14”标识配对模型型号，本例使用其中的文本Transformer，没有将文字切成14×14图块。生成也不是先算成品图与文字的总相似度再照分数作画。

配置`cond_stage_trainable: false`与代码关闭梯度表明该阶段文本参数冻结，编码计算仍要执行。[^config] 原参考tokenizer最大长度77 token，会截断和填充，特殊标记也占空间；这不是77个词或所有现代客户端的统一上限。

<a id="latent-and-unet"></a>

## 3. 反复计算发生在64×64潜网格

自编码器高宽各缩8倍，512×512×3图像对应64×64×4潜表示。[^card] 四通道是学习表示，不是RGB加透明度。空间位置为原来的1/64，实际速度还受通道、网络、文本与解码影响。

新图从该形状的随机噪声开始，U-Net读取当前潜状态、噪声时间与文本条件，预测噪声。部分层通过交叉注意力，由图像特征提出查询、文本提供键和值，影响去噪计算。它提供条件通道，不保证每词对应唯一图像区域或空间关系正确。

<a id="training"></a>

## 4. 训练时的已知噪声与生成时的新噪声

```text
真实花照 → 编码器 → 干净的潜表示
                          ↓ 加入程序已知的噪声
                   带噪潜表示 + 时间步
                          ↓
文字描述 → 文本编码器 → U-Net 预测噪声
                          ↓
                与实际加入的噪声比较
```

噪声由程序生成，作为学习目标，网络只接收受扰状态、时间和条件，未偷看干净原图。[^card] 训练后普通请求使用已有权重，从新噪声产生潜表示再解码，不为每个提示重新训练，也不在线检索训练图作答案。但这种生成方式不排除参数记忆，模型卡确实报告了重复训练图的重现。

<a id="cfg"></a>

## 5. CFG组合同一网络的两种预测

v1.4后续训练以10%概率丢弃文本条件，让同一网络学习有条件和无条件预测。丢的是条件，图片仍参与训练。[^card]

Classifier-Free Guidance（CFG，无分类器引导）在采样时组合：[^cfg]

> 引导预测＝无条件预测＋引导强度×（有条件预测−无条件预测）

两者共用参数，代码可拼成加倍batch调用同一U-Net，仍需计算两组输入，并非省去一半工作；省去的是额外训练的分类器。[^plms]

该代码中强度1回到普通有条件预测，大于1才继续强化条件方向。原CFG论文采用“有条件＋w×差值”，无额外引导点为w＝0，两套数字不能直接互换。

更强引导改变已有预测的组合，不增加知识。它涉及样本质量与多样性取舍，不能保证越强越好，或修好模型未学会的花瓶、窗户关系。

<a id="sampling"></a>

## 6. 采样器决定怎样更新状态

```text
提示词 → 固定的 CLIP 文本编码器 ─────────────┐
                                            ↓
新潜空间噪声 → U-Net 预测 → CFG 组合 → 采样器更新
                    ↑                      │
                    └──── 下一状态继续 ────┘
                                  ↓ 最后
                              图像解码器
                                  ↓
                              像素图片
```

同权重可配不同采样程序。官方README参考命令是PLMS、50步、CFG 7.5、512×512；固定模型卡的Diffusers示例用默认PNDM调度器，不能称所有客户端只有一个默认采样器。[^readme]

v1配置的1000扩散时间步定义噪声范围，不要求用户执行1000采样迭代。PLMS的50步也非恰好50次模型前向：首步额外估计下一状态，CFG每次还处理两组输入。[^config] [^plms] 最后一次解码只将完成的潜表示转为像素，前面仍多步生成。

此PLMS实现要求`eta=0`，不能套用基本DDPM每步新增随机噪声的描述。起始噪声仍决定生成变化，seed可帮助同设置比较；采样器、精度、软件或设备改变时，相同seed不保证逐像素相同。

<a id="data-and-checkpoints"></a>

## 7. 训练沿革有分支

模型卡记录的“步”是更新次数，不是图片数：[^card-training]

| checkpoint | 起点 | 阶段 |
|---|---|---|
| v1.1 | 前期训练 | LAION-2B-en，237,000步、256×256；高分辨率子集194,000步、512×512 |
| v1.2 | v1.1 | 美学筛选集515,000步、512×512 |
| v1.3 | v1.2 | 美学筛选集195,000步、512×512，10%丢条件 |
| v1.4 | v1.2 | laion-aesthetics v2 5+，225,000步、512×512，10%丢条件 |

v1.3与v1.4都从v1.2继续，不能串成四个版本逐一接续。v1.1高分辨率子集约1.7亿个原分辨率至少1024×1024的例子，训练时仍处理成指定输入尺寸。v1.2筛选要求原图至少512×512、美学预测大于5、水印概率预测小于0.5。

这些自动条件不保证逐张授权、无水印或事实正确。模型卡与README对v1.2子集名称略有不同，本章不强行合并为完全一致的命名。

CLIP在数据端与生成端承担不同工作。LAION-5B英语筛选以ViT-B/32图文相似度过滤配对，影响训练材料；v1.4以ViT-L/14文本侧编码提示，影响生成条件。[^laion] 前者仍继承模型盲区，自动过滤不等于完整数据核验。

<a id="evaluation-and-cost"></a>

## 8. 评测配置与资源

固定模型卡从COCO2017验证集随机取10,000提示，生成512×512图，用50步PLMS比较若干1.5–8.0 CFG强度，并注明未针对FID优化。[^card-eval] 比较不同checkpoint时，需要同时固定采样器、分辨率和引导强度。

训练配置32×8张A100，即256卡；全局batch 2048来自256×每卡4图×梯度累积2轮，不是每卡同时装2048图。[^card-training]

README列U-Net约8.6亿参数、文本编码器1.23亿参数，参考实现运行条件至少10GB显存；模型卡另有半精度、attention slicing建议。不同实现与设置不能汇成当前所有设备的统一门槛。

<a id="editing-and-controls"></a>

## 9. 图生图的起点与控制量

图生图先编码已有图，再加噪并按新提示生成，保留部分原构图。README将其联系到SDEdit，`strength`越接近1，扰动越强、变化空间越大，也更可能丢失原语义。[^img2img]

它与CFG不是同一控制：strength影响保留多少输入，CFG scale组合条件预测，步数安排采样离散过程，seed控制随机选择。结果不理想时，应判断问题发生在哪个环节，不能一律靠加长提示词。

<a id="limits-and-history"></a>

## 10. 组件组合的能力与边界

模型卡列出文字渲染、复杂组合、人脸人体、非英语和自编码损失等问题。[^card-limits] “红方块在蓝球上方”要求属性与空间绑定，比一般漂亮花照更易暴露失败。模型卡也承认未做额外去重，观察到重复图记忆，不能由噪声起点推出绝不重现训练图。

参考程序的生成后安全检查与不可见水印是附加处理，不等于网络保证安全或水印不可移除。[^readme] 权重按带用途限制的CreativeML OpenRAIL-M发布；README允许条款下商用，也不建议缺少额外措施时直接服务化。

```text
图文表示与数据筛选 ──→ 训练材料与文本条件
感知压缩 ──────────→ 较小、可解码的图像空间
扩散与噪声预测 ────→ 在这个空间里学会生成
引导与采样程序 ────→ 调整文字影响与生成路径
公开权重和代码 ────→ 他人可以加载、研究和继续开发
```

v1.4的代表性在于这些已有路线形成可读取、加载和研究的组合，不是每个组件都在此首次发明。模型卡开发者为Robin Rombach、Patrick Esser，LDM论文有五位作者；仓库另感谢Stability AI算力、Runway合作与LAION支持。[^card] [^readme] 模型、论文和项目合作记录不能合并成同一机构或推定后续私人履历。

<a id="three-questions"></a>

[下一章DiT](AI演义_31_DiT_Transformer怎样接替去噪骨架_科普讲解_20261106.md)将保留潜空间和扩散训练，检查反复预测噪声的U-Net是否可由Transformer替代。文字编码、采样与解码仍是可分别理解的系统部分。

<a id="sources-and-scope"></a>

## 来源与修订范围

本次沿用原稿对LDM论文、v1.4模型卡、配置和采样代码的阅读。模型卡固定于提交`133a221b8aa7292a167afc5127cb63fb5005638b`，晚于首次发布，不冒充2022原稿；代码是此前读取的master快照，未绑定GitHub commit。

讲义第49页、节目 **03:45:52–03:52:54** 与上一章共享，非另有v1.4专章。[^podcast] 原有[转写核查记录](.quality/AI演义_30_StableDiffusion_v14_文生图系统怎样协同工作_科普讲解_20261106.transcription-review.json)保留，未重新听音或测字错率，本次未训练、生成、部署测速或验证全部许可条款；模型卡评价只核对协议，未逐点读取曲线数值。

## 来源与延伸阅读

[^card]: [Stable Diffusion v1.4 官方模型卡，固定版本](https://huggingface.co/CompVis/stable-diffusion-v1-4/blob/133a221b8aa7292a167afc5127cb63fb5005638b/README.md)，Model Details、Training、Examples。其模型类型、开发者与固定 CLIP 等记录，不能替代 LDM 论文的具体实验配置。
[^ldm]: [LDM 原论文 v2](https://arxiv.org/pdf/2112.10752v2)，§§3.1–3.3、§4.3.1；更完整的压缩与条件机制见[上一章](AI演义_29_LDM_潜空间怎样降低图像生成成本_科普讲解_20261106.md)。
[^encoder]: [官方 `FrozenCLIPEmbedder` 源码](https://github.com/CompVis/stable-diffusion/blob/master/ldm/modules/encoders/modules.py)，核对 tokenizer、`max_length=77`、冻结与 `last_hidden_state`；[CLIP 原论文](https://arxiv.org/pdf/2103.00020v1) §2.4（PDF 第 5 页），说明文本 Transformer 及整体文本表示的原始用途。本文不把 CLIP 论文的序列长度写法当作 v1 实现配置。
[^config]: [官方 v1 推理配置](https://github.com/CompVis/stable-diffusion/blob/master/configs/stable-diffusion/v1-inference.yaml)，核对 `timesteps: 1000`、四潜通道、冻结条件编码器、`crossattn`、AutoencoderKL 与 U-Net 配置。
[^cfg]: Ho、Salimans，[Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598v1)，§3.2、Algorithms 1–2、§4.1；短版在 NeurIPS 2021 workshop 展示，本 arXiv 版本于 2022 年 7 月提交。论文用“有条件预测＋w×差值”，代码用“无条件预测＋s×差值”，两者的无额外引导点分别为 w＝0、s＝1。
[^plms]: [官方 `PLMSSampler` 源码](https://github.com/CompVis/stable-diffusion/blob/master/ldm/models/diffusion/plms.py)，`make_schedule`、`p_sample_plms` 与其内部 `get_model_output`：CFG 共用网络、成对 batch、首步额外估计及 eta 限制。
[^readme]: [CompVis Stable Diffusion 官方 README](https://github.com/CompVis/stable-diffusion/blob/master/README.md)，Stable Diffusion v1、Reference Sampling Script、Diffusers Integration、EMA-only 与完整 checkpoint 的装载说明、开头组件规模与合作说明。参考命令参数不等于所有客户端的默认值。
[^card-training]: 固定版本[模型卡 Training](https://huggingface.co/CompVis/stable-diffusion-v1-4/blob/133a221b8aa7292a167afc5127cb63fb5005638b/README.md#training)，包括四个 checkpoint 的来历、分辨率、数据筛选及训练配置。v1.3、v1.4 都从 v1.2 继续。
[^laion]: [LAION-5B 原论文](https://arxiv.org/abs/2210.08402)，§3.1 的图文相似度过滤与 §3.2 的安全限制；本章对应[仓内 PDF](../../papers/29_laion5b_2022.pdf)第 4–6 页，只核与这两种 CLIP 用途有关的内容，未重做数据集审计。
[^card-eval]: 固定版本[模型卡 Evaluation Results](https://huggingface.co/CompVis/stable-diffusion-v1-4/blob/133a221b8aa7292a167afc5127cb63fb5005638b/README.md#evaluation-results)。本章核评价协议，不转录未经逐点核验的曲线数值。
[^img2img]: 官方 README 的 [Image Modification with Stable Diffusion](https://github.com/CompVis/stable-diffusion/blob/master/README.md#image-modification-with-stable-diffusion)，其 SDEdit 引用与 `strength` 说明；未将 SDEdit 全文列作本章已精读材料。
[^card-limits]: 固定版本[模型卡 Limitations and Bias](https://huggingface.co/CompVis/stable-diffusion-v1-4/blob/133a221b8aa7292a167afc5127cb63fb5005638b/README.md#limitations-and-bias)、Safety Module、Uses，以及官方 README 的研究权重与安全提醒。
[^podcast]: [小宇宙节目与 shownotes](https://www.xiaoyuzhoufm.com/episode/68ff9d1b083a71a4eb86c52c)、[《AI演义》讲义](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf)第 49 页。若节目直链在浏览器受限，可在小宇宙 App 搜索节目标题。本文只发布核查范围与解释，不公开私有转写全文。
