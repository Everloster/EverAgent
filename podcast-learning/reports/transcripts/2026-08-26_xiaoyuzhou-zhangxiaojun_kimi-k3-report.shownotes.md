# 张小珺 152 领读Kimi K3技术报告 — shownotes

> 152. 领读Kimi K3技术报告：从架构创新聊起，注意力美学、多教师蒸馏和开源MoE｜发布 2026-08-26T09:33:46.732Z｜时长 7459s

```
今天的节目是一集学习播客，学习Kimi K3技术报告，希望和大家一起领略“技术之美”。
K3是有效扩展到2.8T总参数并全量开源的MoE模型。大家可能注意到，这集技术报告的领读距离模型发布已经过去一段时间。期间，我们试图寻找一位合适的嘉宾，我们希望这位嘉宾的学术和工作背景非常适合讲K3。最后找到孙宇涛。
宇涛目前是清华大学计算机系博士候选人，上海创智学院璞锐学者。他从博士开始的研究方向是LLM架构、预训练，架构创新一直是他的兴趣点，这正好是K3亮点之一。
宇涛透过领读K3技术报告也串联讲解了十多篇相关论文。他的语速非常快——前方语速预警。
OUTLINE:
02:00 宇涛的自我介绍和研究经历，为什么对架构创新最感兴趣？
16:05 从Kimi K3论文出发，论文讲解的框架与脉络
19:02 宇涛开始领读论文：
1 导读
Kimi K3将设计概括为沿sequence、depth和width三个维度扩展信息流；其中depth与width本质上仍是模型容量扩展的两种组织⽅式，这⼀“三维 scaling”更多是贯穿论⽂的叙事框架。
2 Model Architecture
2.1 线性注意⼒的前世今⽣
[Microsoft Research] RetNet：最初的 data-independent decay 与 chunk-recurrent 递归形式
[NVIDIA] Gated DeltaNet：引⼊ gated delta rule
[Moonshot AI] Kimi Linear：fine-grained decay及其带来的infra变化
2.2 Gated MLA
[Alibaba Qwen] Gated Attention for Large Language Models：attention gating与训练稳定性
2.3 Attention Residuals
[Microsoft Research] On Layer Normalization in the Transformer Architecture：Pre-LN、Post-LN与训练稳定性
[ByteDance Seed] Hyper-Connections：残差连接的新维度
[Moonshot AI] Attention Residuals：以跨深度attention取代固定残差累积，使各层选择性聚合此前表⽰
2.4 Stable LatentMoE与SiTU-GLU
[NVIDIA] LatentMoE：通过latent expert space降低MoE通信与权重访问成本
[OpenAI] GPT-OSS：以clamped SwiGLU控制激活值
2.5 Muon
[Moonshot AI] Moonlight / Muon is Scalable for LLM Training：更好的优化表现及随之突出的 activation outlier问题
2.6 Quantile Balancing
[科学空间] 《MoE环游记：6、最优分配促均衡》：从最优分配推导Quantile Balancing
2.7 Native Vision
3 Pre-Training
3.1 Scaling Law
[OpenBMB] MiniCPM：WSD的训练预算扩展、稳定阶段复⽤、继续训练与提前停⽌
3.2 Long-Context Extension
[Cohere] RNoPE：交替使⽤RoPE与NoPE，兼顾位置建模与长上下⽂检索
4 Post-Training
4.1 Post-Training Pipeline
4.2 Reinforcement Learning
[Moonshot AI] Kimi K1.5：提出partial rollout，通过复⽤未完成轨迹降低长CoT rollout开销
[Moonshot AI] Kimi K2.5：reasoning-effort budget control 与 Agentic Generative Reward Model
4.3 Multi-Teacher On-Policy Distillation
[Microsoft Research] MiniLLM：基于student-generated samples的on-policy distillation
4.4 Deployment-Aware Post-Training
4.5 Draft Model Fine-Tuning
5 Infrastructure
5.1 Pre-Training
5.1.1 KDA Kernel
[FLA] Flash Linear Attention：KDA kernel与线性注意⼒⾼效实现
5.1.2 Distributed Training
[DeepSeek-AI] DeepSeek-V3 Technical Report：DualPipe与细粒度MoE communication–computation overlap
MoE overlap的资源trade-off与cross-PP activation transfer
5.1.3 Perfectly Balanced Expert-Parallel MoE Training
5.1.4 Memory-Efficient Training
[Moonshot AI] Mooncake：Mooncake Transfer Engine与cross-PP activation remote offload
5.1.5 Multimodal Encoder Optimization
5.2 RL
5.2.1 Long-Context RL Infrastructure
5.2.2 Sandbox Infrastructure
5.3 Inference
5.3.1 KDA-Aware Prefix Cache Management
5.3.2 High-Performance Kernels
5.3.3 Fleet-Level Scheduling
LINKS：
我们的播客在小宇宙、Apple Podcast、Spotify等全音频平台播出；
我们的视频播客在小宇宙、Bilibili、小红书、视频号、抖音等全视频平台播出；
如果你想服用文字版，请搜索我们工作室的公众号：语言即世界language is world。
DISCLAIMER: 本内容不作为投资建议。
CONTACT: xiaojunzhang@lisw.ai
Jump into the new world-and explore with us!😉
```
