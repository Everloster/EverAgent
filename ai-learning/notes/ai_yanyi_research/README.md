# 《AI演义》发展路径研究

36个研究对象的阶段材料已完成分批独立核查，并已整合为[正式报告](../../reports/AI演义_笔记分析与项目整合报告.md)。2026-11-04的修订补充了基础术语、跨路线讲解和具体实验对照，并通过新一轮独立复核与旗舰质量门；历次复核保存在[终审记录](../../reports/.quality/AI演义_笔记分析与项目整合报告.review.json)。主报告保留完整路线，分节展开篇提供更细的解释；写作期中间稿已归档到本地审阅缓存，不作为公开副本。

主稿以共同问题串联历史、范式变迁和人物／组织条件，不按36篇摘要拼贴。用户已认可两段样章，并明确要求少数学、重点讲背景、解决的问题、作用与整体路线连接。

## 主报告与终审

- [AI演义深读：从关键论文看懂AI的发展路径](../../reports/AI演义_笔记分析与项目整合报告.md)
- [完整证据账本](../../reports/.quality/AI演义_笔记分析与项目整合报告.evidence.json)
- [终审记录](../../reports/.quality/AI演义_笔记分析与项目整合报告.review.json)

## 分节展开与路线地图

- [《AI演义》01｜Brook：GPU 很快，为什么普通程序还不容易用上它？](../../reports/knowledge_reports/AI演义_01_Brook_GPU通用计算_科普讲解_20261104.md)（从逐行计算讲到数据流、核函数、规约与 GPU 的使用成本）
- [《AI演义》02｜AlexNet：数据、模型和 GPU 为什么必须合在一起看？](../../reports/knowledge_reports/AI演义_02_AlexNet_图像识别突破_科普讲解_20261104.md)（跟着猫照片理解卷积、训练反馈、双 GPU 分工，以及冠军成绩的比较条件）
- [《AI演义》03｜ResNet：网络更深了，为什么连训练集都学不好？](../../reports/knowledge_reports/AI演义_03_ResNet_深层网络如何训练_科普讲解_20261104.md)（从中间特征的修正讲到残差块、梯度传播，以及千层网络的泛化问题）
- [《AI演义》04｜蒸馏：大模型学到的本领，小模型怎样接过去？](../../reports/knowledge_reports/AI演义_04_知识蒸馏_从教师到学生_科普讲解_20261104.md)（跟着猫照片理解软标签与温度，再核对语音、少量迁移数据和未见类别的实验条件）
- [《AI演义》05｜Word2Vec：词向量怎样学出来，又知道些什么？](../../reports/knowledge_reports/AI演义_05_Word2Vec_词向量怎样学出来_科普讲解_20261104.md)（从“苹果”的局部预测讲到词向量更新、训练成本，以及固定表示与上下文表示的区别）
- [《AI演义》06｜seq2seq 与 Attention：模型怎样翻译一句话？](../../reports/knowledge_reports/AI演义_06_seq2seq与Attention_模型怎样翻译一句话_科普讲解_20261105.md)（跟着黑猫句子理解编码、生成和按步读取，再看两篇论文不同的长句表现与实验条件）
- [《AI演义》07｜GNMT 与 Transformer：翻译怎样变快，为什么还要逐词生成？](../../reports/knowledge_reports/AI演义_07_GNMT与Transformer_从翻译系统到并行架构_科普讲解_20261105.md)（从翻译服务的罕见词、漏译和速度问题，讲到 Q/K/V、目标遮罩、并行训练，以及自动指标与人评的差别）
- [《AI演义》08｜GPT-1 与 BERT：只是读了很多文本，怎么就能做不同任务？](../../reports/knowledge_reports/AI演义_08_GPT1与BERT_预训练怎样迁移到不同任务_科普讲解_20261105.md)（用黑猫问答分清预训练、微调、双向表示和答案抽取，再看收益与失败）
- [《AI演义》09｜GPT-2 与 GPT-3：只给说明和例子，模型就能换任务吗？](../../reports/knowledge_reports/AI演义_09_GPT2与GPT3_任务怎样进入上下文_科普讲解_20261105.md)（从任务写进输入讲到零、单、少示例实验，以及评测污染、数据规模和可靠性的边界）
- [《AI演义》10｜Scaling Laws 与 Chinchilla：同一份算力，模型和数据怎样分？](../../reports/knowledge_reports/AI演义_10_ScalingLaws与Chinchilla_算力预算怎样分配_科普讲解_20261105.md)（从固定预算讲到三种实验估计、真实成绩与反例，再分清一次训练和长期使用的成本）
- [《AI演义》11｜ZeRO：多加 GPU，怎样让训练真正装得下？](../../reports/knowledge_reports/AI演义_11_ZeRO_多卡怎样分担训练显存_科普讲解_20261105.md)（用四卡账本解释三阶段分片、训练协作与通信，再看容量分析、实际实验和更省显存却更慢的反例）
- [《AI演义》12｜RefinedWeb：网页怎样变成好用的训练数据？](../../reports/knowledge_reports/AI演义_12_RefinedWeb_网页怎样变成训练数据_科普讲解_20261105.md)（跟着一篇网页理解正文提取、过滤与两种去重，用训练对照和反例判断数据是否处理得当）
- [《AI演义》13｜LAION：图片和文字，怎样变成训练数据？](../../reports/knowledge_reports/AI演义_13_LAION_图文怎样变成训练数据_科普讲解_20261105.md)（从网页图文配对讲到 CLIP 筛选、开放索引与训练对照，再看数据偏差和使用边界）
- [《AI演义》14｜MegaScale：一万张 GPU，怎样一起把模型练完？](../../reports/knowledge_reports/AI演义_14_MegaScale_万卡怎样协同训练_科普讲解_20261105.md)（跟着一次训练理解多卡分工、通信等待、实际提速和故障恢复）
- [《AI演义》15｜稀疏 MoE：大模型怎样只计算一部分？](../../reports/knowledge_reports/AI演义_15_稀疏MoE_大模型怎样只计算一部分_科普讲解_20261105.md)（跟着一次词预测理解路由与专家分工，再用真实实验分清容量、计算量和实际成本）
- [《AI演义》16｜LoRA：少量参数，怎样让大模型适配新任务？](../../reports/knowledge_reports/AI演义_16_LoRA_少量参数怎样适配新任务_科普讲解_20261105.md)（跟着对话摘要理解低秩更新与合并部署，再分清省参数、省显存、提速和记忆的边界）
- [《AI演义》17｜AlphaGo Zero：没有人类棋谱，怎样学会下棋？](../../reports/knowledge_reports/AI演义_17_AlphaGoZero_不靠棋谱怎样学会下棋_科普讲解_20261105.md)（跟着一步棋理解网络建议、树搜索和胜负反馈，再看两次训练、模仿与棋力的差别，以及推理时计算的联系）
- [《AI演义》18｜InstructGPT：模型怎样学会按要求回答？](../../reports/knowledge_reports/AI演义_18_InstructGPT_模型怎样学会按要求回答_科普讲解_20261105.md)（用一份图书馆通知讲清示范、偏好比较与强化学习，再分清更受偏好、事实可靠和原有能力）
- [《AI演义》19｜CoT：中间步骤怎样帮助模型作答？](../../reports/knowledge_reports/AI演义_19_CoT_中间步骤怎样帮助模型作答_科普讲解_20261105.md)（用一道苹果题讲清提示示范、中间步骤与消融，再看“答案对、解释错”的真实反例）
- [《AI演义》20｜ReAct：模型怎样边查边想，把任务做下去？](../../reports/knowledge_reports/AI演义_20_ReAct_模型怎样边查边想_科普讲解_20261105.md)（跟着 Apple Remote 查询理解推理、动作与观察，再看查错对象、重复操作和任务成功率的边界）
- [《AI演义》21｜Tülu 3：示范、偏好和验算，怎样一起训练助手？](../../reports/knowledge_reports/AI演义_21_Tulu3_后训练配方怎样起作用_科普讲解_20261105.md)（用彩笔题区分三种反馈，再看关键词奖励失效、能力回退与开放评测）
- [《AI演义》22｜DeepVideo：多看几帧，为什么还不够？](../../reports/knowledge_reports/AI演义_22_DeepVideo_模型怎样利用视频时间信息_科普讲解_20261105.md)（用跳绳视频讲清单帧、多帧与聚合，再看真实失败、训练成本和动作分类迁移）
- [《AI演义》23｜双流网络：把运动先算出来，识别动作会更容易吗？](../../reports/knowledge_reports/AI演义_23_TwoStream_外观与运动怎样共同识别动作_科普讲解_20261105.md)（用跳绳场景讲清 RGB 与光流分工、小数据训练与融合，再看未全面胜出的比较、真实错误和预处理成本）

主报告的对应章节保留完整导读，并直接链接展开篇；展开篇可以返回原章节，也可继续读下一节。其余章节仍见主报告。

- [初始来源／36对象地图](./source-map.md)
- [从seq2seq到Transformer](./sample_sequence.md)
- [Scaling Laws到Chinchilla](./sample_scaling.md)

来源地图覆盖原PDF51页，核定为33篇论文、2篇研究报告、1篇观点文章。原PDF和既有论文二进制未被替换；论文索引中若干已确认的身份、链接和贡献边界做了局部修正。未核的外围履历、优先权或精确数值没有被强行写成结论。

## 可追溯的研究与核查

| 范围 | 研究材料 | 独立核查 |
|---|---|---|
| 来源身份与路线 | [清单](./source-map.json) | [核查](./inventory.review.json) |
| 序列模型样章 | [材料](./sequence-evidence.json) | [核查](./sequence.review.json) |
| 规模与预算样章 | [材料](./scaling-evidence.json) | [核查](./scaling.review.json) |
| 计算基础、视觉突破、优化与蒸馏 | [材料](./phase2/foundations.json) | [核查](./phase2/foundations.review.json) |
| 基础设施与数据 | [材料](./phase2/infrastructure_data.json) | [核查](./phase2/infrastructure_data.review.json) |
| 语言预训练与任务接口 | [材料](./phase2/language_pretraining.json) | [核查](./phase2/language_pretraining.review.json) |
| 对齐、推理、搜索与行动 | [材料](./phase2/alignment_action.json) | [核查](./phase2/alignment_action.review.json) |
| 效率与历史解释框架 | [材料](./phase2/efficiency_and_lesson.json) | [核查](./phase2/efficiency_and_lesson.review.json) |
| 视觉与图文对齐 | [材料](./phase2/vision_alignment.json) | [核查](./phase2/vision_alignment.review.json) |
| 生成路线与具体产品接口 | [材料](./phase2/generation.json) | [核查](./phase2/generation.review.json) |

阶段研究包通过，不自动等于主稿通过旗舰质量门。精确版本、实际阅读范围、图像服务失败的降级、未进行的训练复现及未采用的数值冲突，都在相应记录中保留。原始下载在非发布缓存，不把执行收据、私人环境或整篇外部论文复制进公开仓。

展开篇用具体例子贯穿机制，再回到论文的实验与限制。Brook 一节提醒后续展开时同步更新主稿入口，并实际检查往返定位；AlexNet 一节把模型、训练数据、验证集／测试集和单模型／集成分开核对，人物与机构的时间线另查正式来源；ResNet 一节区分训练退化与泛化失败，并在引用后续改进时标明版本和适用条件；蒸馏一节把教师使用的数据、学生迁移数据和测试集调参分开，也区分已经取得的集成结果与尚未完成的再次蒸馏；Word2Vec 一节区分同年两篇论文的贡献，并用不同任务的实验检查类比、短语和词义消歧的边界。后续各节延续这些已经用过的做法，再按本节问题调整解释方式。
