# Kimi K3

> 概念 · 首次出现：2026-08-04（晚点聊177）/ 2026-08-26（张小珺152）双期对照处理

## 定义

[[moonshot-ai|月之暗面]] 2026-07-16 官宣、07-27 随 47 页技术报告全量开源的模型：**2.8T 总参数 / 约 104B 激活 MoE**（896 路由专家选 16），**首个 3T 级开放权重模型**；原生 1M 上下文、原生多模态（agentic）。前身 Kimi Linear（约 48B）预研混合架构。

## 架构总览（"集百家之长"）

| 维度 | 设计 | 谱系 |
|------|------|------|
| 序列 | [[kda-linear-attention|KDA]] 线性注意力 : Gated MLA ≈ 3:1（69+24 层，末层必 MLA） | RetNet→DeltaNet→GDN→KDA |
| 深度 | [[attention-residuals|Attention Residuals]]（块状版） | ResNet→DenseNet→Hyper-Connections |
| 宽度 | Stable LatentMoE + [[quantile-balancing|Quantile Balancing]] + SiTU-GLU | LatentMoE（NVIDIA）/ GPT-OSS |
| 位置 | **全模型 NoPE**（首个全 NoPE frontier 模型） | RNoPE（Cohere） |
| 优化器 | Muon（Moonlight VDK + K2 QK-Clip 沿革）+ Per-head Muon | Moonlight / nanoGPT Speedrun |
| 后训练 | [[mopd|MOPD]] 多教师 on-policy 蒸馏 + QAT from SFT（MXFP4/MXFP8） | MiniLLM（OPD 源头） |
| Infra | MoonEP 动态 EP、FP8 offload、Flash KDA、AgentEnv、[[kernel-development-agent|Kernel Development Agent]] | DeepEP / Mooncake / CUTLASS |

## 关键数字

2.8T/104B（激活魄力=杨植麟"有概率的非共识"）· scaling efficiency 2.5×（同验证损失 FLOPs≈40%）· 1M 上下文（8K→64K→256K→1M 阶梯）· 69 层 KDA 仅 54MB 固定状态（MLA 部分约 27GB）· 定价 $0.3/$3/$15 vs DeepSeek-V4 $0.04/$0.44/$0.87 · CodeBench 2.0 比最强模型 -4.0 分但成本 38%

## 两期对照的关键判断

- 双重身份：十年架构改良史的集大成 + hybrid/全 NoPE scale 到 3T 的存在性证明
- 与 DeepSeek-V4 分化：Kimi 提升开源上限（贵）、DeepSeek 性价比（Flash 档）；技术上 hybrid+全 NoPE vs KV compression+稀疏注意力，都 scale 到 frontier
- 生态冲击：7-24 五十余家开放权重公开信、Dario 回应、国产芯片适配（摩尔线程/AMD）
- 护城河分层：权重=这一代智能副本；环境+验证+算力+"模型内科"=下一代流水线（未开放）

## 引用本概念的报告

- [[2026-08-26_xiaoyuzhou-zhangxiaojun_kimi-k3-report]]（学术领读）
- [[2026-08-04_rss-wandian-latetalk_kimi-k3]]（工业生态）
- [[2026-09-02_multi_kimi-k3-dueling-reads]]（对照层）
