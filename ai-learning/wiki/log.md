# ai-learning · Wiki 操作日志

> append-only。每次 ingest / query-archive / lint 追加一条记录。
> 格式：`## [YYYY-MM-DD] {操作类型} | {标题}`
> 快速查看最近 5 条：`grep "^## \[" log.md | tail -5`

---

## [2026-04-06] phase1-init | Phase 1 起步：人物图谱 + 第一个 concept
- 新建 entities：hinton_geoffrey / lecun_yann / bengio_yoshua / vaswani_ashish / shazeer_noam / wei_jason / openai / google_brain_deepmind（共 8 个）
- 新建 concepts：attention_mechanism（共 1 个）
- 数据源：AI关键人物图谱、01_transformer_2017、self_attention_深度解析、21_moe_2017
- commit：c8899d2

## [2026-04-07] phase1-close | Phase 1 闭环：补全 entity / concept / overview / index
- 新建 entities：brown_tom / schulman_john / dao_tri / meta_ai（共 4 个，累计 12 个）
- 新建 concepts：transformer_architecture / scaling_laws / rlhf / lora_peft / moe_architecture / kv_cache / self_supervised_learning / sparse_activation（共 8 个，累计 9 个）
- 新建 overview.md：四条主线 + 技术拐点 + 概念依赖图 + 缺失页面清单
- 更新 index.md：将所有 entity / concept / overview 登记到对应表格，移除占位符
- 数据源：03_gpt3_2020、04_instructgpt_2022、05_scaling_laws_2020、15_lora_2021、17_mae_2022、18_flashattention_2022、21_moe_2017、35_dinov2_2023、Scaling_Laws_深度解析、RLHF_深度解析、LoRA_深度解析、MoE_混合专家_深度解析_20260406、KV_Cache_深度解析_20260330、AI关键人物图谱
- 状态：plan §8 短期标准 ≥10 entities / ≥8 concepts 双双满足

## [2026-04-07] query-archive | MoE vs Dense 推理成本比较
- 触发查询：MoE 相对 Dense 在推理成本和参数效率上的本质区别？为什么 DeepSeek-V3 的 671B/37B 配比更有效率？
- 涉及概念：moe_architecture / sparse_activation / scaling_laws（≥3，按 plan §3.2 归档）
- 新建：syntheses/moe_vs_dense_inference_cost.md
- 更新：index.md syntheses 表新增条目
- 数据源：MoE_混合专家_深度解析_20260406、21_moe_2017、33_mistral_7b_2023、Scaling_Laws_深度解析

## [2026-04-07] lint-fix | lora_peft.md 补 K 投影与 r 边际
- 触发：Phase 1 闭环验证 Q2（LoRA 为何注入 Q/V 而非 K/O）发现 wiki 缺 2 个细节
- 修补 1：注入位置选择，明确 K 单独注入边际不显著的论文实验依据
- 修补 2：r 的边际递减（r=4→16 差异小，r=64+ 边际极低）
- 数据源：LoRA_深度解析 §应用位置 / §陷阱1 / §陷阱3
- 验证结论：Q1 ✅ 全 wiki 可答；Q2 ⚠️→✅ 已补全后可答

## [2026-04-09] ingest | Agent Systems 深度解析
- 新建 concepts：agent_systems（含 ReAct/Tool Use/MCP 区分与联系，300字以上）
- 新建 reports：Agent_ReAct_ToolUse_深度解析_20260409（5层框架 + Python ReAct Loop + 检验题 + 资源推荐）
- 数据源：ReAct paper (Yao 2022, arXiv:2210.03629)、Anthropic MCP docs、MCP llms.txt
- 状态：plan §8 Agent Systems 概念页 ✅ 完成

## [2026-04-11] ingest | GPT-1 论文精读（AI演义四条线 P0-1）
- 新建报告：reports/paper_analyses/37_gpt1_2018.md（7步分析，1.17亿参数 Transformer Decoder 预训练-微调范式开创）
- 新建 entity：wiki/entities/radford_alec.md（GPT-1/2、CLIP、Whisper 核心作者）
- 新建 concept：wiki/concepts/pretraining_finetuning.md（预训练-微调两阶段范式）
- 更新 wiki/index.md：新增 Radford entity + pretraining_finetuning concept
- 数据源：AI演义 PDF（谢青池）+ GPT-1 原论文知识
- 状态：AI演义计划 P0-1 完成

## [2026-04-11] ingest | GPT-2 论文精读（AI演义四条线 P0-2）
- 新建报告：reports/paper_analyses/38_gpt2_2019.md（7步分析，1.5B参数 零样本多任务学习 WebText数据集 Pre-Norm标准化 Scaling信念验证）
- Wiki 概念更新：pretraining_finetuning.md 中已涵盖 GPT-2 的 zero-shot 转折
- 数据源：AI演义 PDF + GPT-2 原论文知识
- 状态：AI演义计划 P0-2 完成

## [2026-04-11] ingest | The Bitter Lesson 精读（AI演义四条线 P0-3）
- 新建报告：reports/paper_analyses/22_bitter_lesson_2019.md（7步分析，70年AI历史元认知纲领 搜索与学习两大可扩展方法 四领域验证）
- 新建 entity：wiki/entities/sutton_rich.md（RL奠基人，TD Learning，Bitter Lesson作者）
- 新建 concept：wiki/concepts/bitter_lesson.md（苦涩教训：通用计算>知识编码，四条时间线哲学总纲）
- 更新 wiki/index.md：新增 Sutton entity + bitter_lesson concept
- 数据源：Sutton 2019 原文 + AI演义 PDF
- 状态：AI演义计划 P0-3 完成，Batch P0 全部完成

## [2026-04-11] ingest | Stable Diffusion / LDM 精读（AI演义四条线 P1-1）
- 新建报告：reports/paper_analyses/20_stable_diffusion_2021.md（7步分析，潜空间扩散两阶段架构 交叉注意力条件机制 f=4~8最优平衡）
- 新建 entity：wiki/entities/rombach_robin.md（LDM/SD 第一作者，LMU Munich & Runway ML）
- 新建 concept：wiki/concepts/latent_diffusion.md（感知压缩+语义生成解耦，交叉注意力条件机制）
- 更新 wiki/index.md：新增 Rombach entity + latent_diffusion concept
- 数据源：LDM 原论文 CVPR 2022 + CLIP #12 + DDPM #09
- 状态：AI演义计划 P1-1 完成

## [2026-04-11] ingest | DiT 精读（AI演义四条线 P1-2）
- 新建报告：reports/paper_analyses/27_dit_2022.md（7步分析，Transformer 替换 U-Net 骨架 AdaLN-Zero Scaling Laws Sora 技术基础）
- 新建 entity：wiki/entities/peebles_william.md（DiT 第一作者 NYU→OpenAI Sora 核心贡献者）
- 新建 entity：wiki/entities/xie_saining.md（DiT 共同作者 NYU 助理教授）
- 新建 concept：wiki/concepts/diffusion_transformer.md（Patchify AdaLN-Zero Scaling Laws）
- 更新 wiki/index.md：新增 Peebles + Xie entities + diffusion_transformer concept
- 数据源：DiT 原论文 ICCV 2023 + ViT #11 + LDM #20
- 状态：AI演义计划 P1-2 完成

## [2026-04-11] ingest | ReAct 论文精读（AI演义四条线 P1-3）
- 新建报告：reports/paper_analyses/17_react_2022.md（7步分析，Thought-Action-Observation 循环 推理+行动协同 自我纠错机制 多任务统一框架）
- 新建 entity：wiki/entities/yao_shunyu.md（ReAct 第一作者 00后 SWE-bench 作者 Princeton→Meta AI）
- Wiki concept：agent_systems.md 已在 P1-3 前完成（覆盖 ReAct Loop/MCP/ToolUse）
- 更新 wiki/index.md：新增 Yao entity
- 更新 wiki/log.md
- 数据源：ReAct 原论文 arXiv:2210.03629 + CoT #10 + 已有 Agent 知识报告
- 状态：AI演义计划 P1-3 完成，Batch P1 全部完成

## [2026-04-11] ingest | LAION-5B + RefinedWeb 精读（AI演义四条线 P2-1 & P2-2）
- 新建报告：reports/paper_analyses/29_laion5b_2022.md（7步分析，58.5亿图文对 CLIP过滤 开源多模态数据基础 Stable Diffusion数据源）
- 新建报告：reports/paper_analyses/30_refinedweb_2023.md（7步分析，5T tokens progressive filtering Falkon LLM数据基础）
- 新建 entity：wiki/entities/schuhmann_christoph.md（LAION创始人 LAION-5B负责人）
- 新建 entity：wiki/entities/penedo_guilherme.md（RefinedWeb第一作者 TII Falkon核心）
- 新建 entity：wiki/entities/tii.md（TII阿联酋技术创新研究院 Falkon+RefinedWeb诞生地）
- 新建 concept：wiki/concepts/large_scale_data_filtering.md（URL去重 CLIP评分 progressive质量过滤 方法论）
- 更新 wiki/index.md：新增 3 entities + 1 concept
- 数据源：LAION-5B/RefinedWeb 原论文 + Scaling Laws #05 + CLIP #12
- 状态：AI演义计划 P2-1 和 P2-2 完成

## [2026-04-11] ingest | Google Translate (GNMT) + DeepVideo 精读（AI演义四条线 P2-3 & P2-4）
- 新建报告：reports/paper_analyses/39_google_translate_2016.md（7步分析，GNMT深层残差LSTM WordPiece Attention NMT工业部署里程碑）
- 新建报告：reports/paper_analyses/40_deepvideo_2014.md（7步分析，Sports-1M数据集 四种时序融合策略 Slow Fusion 多分辨率架构）
- 新建 entity：wiki/entities/wu_yonghui.md（GNMT第一作者 Google Brain 深层残差LSTM+WordPiece）
- 新建 entity：wiki/entities/karpathy_andrej.md（Deep Video第一作者 Stanford→Tesla CS231n讲师）
- 更新 wiki/index.md：新增 Wu + Karpathy entities
- 数据源：GNMT/DeepVideo 原论文 + CNN 基础 #06
- 状态：AI演义计划 P2-3 和 P2-4 完成，Batch P2 全部完成

<!-- 后续 ingest / query-archive / lint 在此追加 -->

## [2026-05-13] ingest | SkillOS 论文精读
- 新建报告：reports/paper_analyses/44_skillos_2026.md
- 新建 concept：wiki/concepts/skill_curation.md
- 新建 entity：wiki/entities/google_cloud_ai_research.md
- 更新 wiki/index.md：新增 Skill Curation 概念与 Google Cloud AI Research 机构
- 更新 CONTEXT.md 与 papers/PAPERS_INDEX.md：登记 arXiv:2605.06614 精读状态
- 关联实践：ai-practice exp_007 SkillOS 技能库策展小型实验复现

## [2026-05-07] ingest | 1M Long Context 三阶段深度解析
- 新建报告：reports/knowledge_reports/Long_Context_1M_三阶段深度解析_20260507.md
- 新建 concept：wiki/concepts/long_context_systems.md
- 更新 wiki/index.md：新增 long_context_systems 条目
- 更新 CONTEXT.md：追加知识报告清单
- 关联概念：attention_mechanism / kv_cache / rag / in_context_learning / llms_plus

## [2026-04-15] ingest | 奶头乐ChatBot真实战略价值 + 开源vs闭源ToA博弈 深度解析
- 新建报告：reports/knowledge_reports/奶头乐ChatBot的真实战略价值_20260415.md（数据飞轮·RLHF依赖·三类数据质量对比·OpenAI/Anthropic/国内厂商战略·Model Collapse反面）
- 新建报告：reports/knowledge_reports/开源vs闭源在ToA世界的重新博弈_20260415.md（CLI原生论5条机制·MCP开源生态·本地部署经济学·DeepSeek分水岭·三种终局场景·监管变量）
- 新建 concept：wiki/concepts/toc_as_data_infrastructure.md
- 新建 concept：wiki/concepts/opensource_vs_closedsource_toa.md
- 更新 wiki/index.md：新增 2 个 concept 条目
- 前置报告：ToA_CLI_Agentic原生论_深度解析_20260415
- 关联概念：toa_paradigm / rlhf / scaling_laws / agent_systems / bidirectional_domestication

## [2026-04-15] ingest | EverAgent 作为 ToA 原型的解剖
- 新建报告：reports/knowledge_reports/EverAgent_ToA原型解剖_20260415.md（119 commits 实证 + ToA五要素审计 + git history 考古 + 四个未解问题 + 设计模式提炼 + 自我批判）
- 新建 concept：wiki/concepts/toa_system_design.md（可复用设计模式 + 未解问题对照表 + 人类角色演化实证）
- 更新 wiki/index.md：Concepts 表新增 toa_system_design 条目
- 核心数据：git log 119 commits，8种模型身份（OpenAI/Anthropic/MiniMax/智谱），task-execution 41次 / project-optimization 36次
- 关键发现：`98d0e53 interrupted by limit` 失败记录；命名漂移（3种MiniMax写法）；质量回顾机制缺失；协议遵守依赖自律
- 前置报告：ToA_CLI_Agentic原生论 + 双向驯化与多Agent涌现

## [2026-04-15] ingest | 双向驯化 & 多Agent涌现 深度解析
- 新建报告：reports/knowledge_reports/双向驯化与多Agent涌现_深度解析_20260415.md（ToA盲区两论 + 四种驯化机制 + 四种涌现类型 + 叠加风险结构 + EverAgent活体案例）
- 新建 concept：wiki/concepts/bidirectional_domestication.md（双向驯化 · 多Agent涌现 · 两论叠加效应）
- 更新 wiki/index.md：Concepts 表新增 bidirectional_domestication 条目
- 核心论点：碳基调教硅基是显性箭头，硅基调教碳基是结构性副产品；多Agent涌现在计算上不可约，单Agent Alignment框架的四个假设全部失效；两者叠加是ToA世界最深层的结构性风险
- 前置报告：ToA_CLI_Agentic原生论_深度解析_20260415
- 关联概念：agent_systems / toa_paradigm / in_context_learning / bitter_lesson

## [2026-04-15] ingest | ToA 范式 · CLI 原生论 · 硅碳加速论 深度解析
- 新建报告：reports/knowledge_reports/ToA_CLI_Agentic原生论_深度解析_20260415.md（5层分析框架 + 概念关系网络 + 批判性分析 + 行动推论）
- 新建 concept：wiki/concepts/toa_paradigm.md（ToA 定义 · CLI 原生论机制 · 硅碳加速剪刀差 · 开放问题三条）
- 更新 wiki/index.md：Concepts 表新增 toa_paradigm 条目
- 核心观点：ToC/ToB → ToA 范式迁移；CLI 是 Agent 母语（强化学习天然适配）；硅碳剪刀差指数 vs 线性；GUI 是"最大迁移成本"而非 Bitter Lesson
- 数据源：用户 2026-04-15 观点输入 + 项目内已有报告（agent_systems / bitter_lesson / scaling_laws / test_time_compute）
- 关联已有概念：agent_systems / bitter_lesson / scaling_laws / test_time_compute / in_context_learning

## [2026-04-09] ingest | RAG 深度解析
- 新建 concepts：rag（检索增强生成，Naive → Advanced → Modular RAG 演进，GraphRAG · Self-RAG · Reranker）
- 新建 reports：RAG_深度解析_20260409（5层框架 + Python Pipeline + 检验题 + 资源推荐）
- 数据源：Lewis et al. 2020 (RAG), Gao et al. 2022 (HyDE), Yao et al. 2023 (Self-RAG), Microsoft GraphRAG 2024
- 状态：RAG 核心范式 / Reranker / Chunk 策略 / 知识库选型 / 与 Fine-tuning 对比全覆盖

## [2026-04-09] ingest | In-Context Learning 深度解析
- 新建 concepts：in_context_learning（通过 prompt demonstrations 无梯度更新完成新任务，Bayesian / Task Recognition / Knowledge Activation 三派理论）
- 新建 reports：In_Context_Learning_深度解析_20260409（5层框架 + ICL 三阶段机制 + 代码实现 + 检验题 + 资源推荐）
- 数据源：Brown et al. 2020 (GPT-3), Rubin et al. 2022, Wei et al. 2023, Liu et al. 2024 (Position Bias), Gould et al. 2023
- 状态：ICL 定义 / 三阶段运作机制 / 三大理论流派 / Scaling Laws / Position Bias / Instruction Tuning 影响全覆盖

## [2026-04-09] ingest | Test-time Compute & Reasoning Models 深度解析
- 主题：Test-time Compute · Reasoning Models（test-time scaling / o1-o3 / DeepSeek-R1 / GRPO / PRM / MCTS）
- 新建报告：reports/knowledge_reports/Test_Time_Compute_深度解析_20260409.md
- 新建 wiki 概念页：wiki/concepts/test_time_compute.md（含传统 training-time scaling 对比，300字以上）
- 更新 wiki/index.md Concepts 表格新增条目
- 数据源：Wei et al. 2022 CoT、OpenAI o1/o3 技术报告、DeepSeek-R1 论文、Brown et al. 2024 Inference-Time Scaling
- 状态：plan §知识深度解析完成

## [2026-04-16] ingest | 生成模型演化全景：GAN → DDPM → LDM → DiT 知识报告
- 新建报告：reports/knowledge_reports/生成模型演化全景_GAN_DDPM_LDM_DiT_20260416.md（5层框架+演化谱系图，整合4篇已精读论文）
- 新建 concept：wiki/concepts/generative_models_evolution.md（四代演化对比·核心公式·前沿Flow Matching·开放问题）
- 更新 wiki/index.md：Concepts 表格新增 generative_models_evolution 条目
- 数据源：08_gan_2014 / 09_ddpm_2020 / 20_stable_diffusion_2021 / 27_dit_2022 + 相关知识报告
- 执行者：NeuronAgent / Claude Sonnet 4.6
---
## [2026-04-16] ingest | EVA-02: A Visual Representation for Neon Genesis (2023)
- 新建报告：reports/paper_analyses/41_eva02_2023.md（7步分析框架，SwiGLU/2D RoPE/sub-LN架构解析，MIM预训练，IN-1K 90.0%）
- 新建 concept：wiki/concepts/eva02_vision_transformer.md（架构要点·模型规格·EVA系列谱系·关联概念）
- 更新 wiki/index.md：Concepts 表格新增 eva02_vision_transformer 条目
- 更新 CONTEXT.md：已有报告+边界区同步更新
- 数据源：arXiv 2303.11331 + GitHub baaivision/EVA
- 执行者：NeuronAgent / Claude Sonnet 4.6

## [2026-04-16] ingest | Megatron-LM 大规模语言模型训练系统深度解析
- 新建报告：reports/knowledge_reports/Megatron_LM_大规模训练系统_深度解析_20260416.md
- 新建 wiki 页面：wiki/concepts/megatron_lm_3d_parallelism.md
- 更新 wiki/index.md：Concepts 表格新增 megatron_lm_3d_parallelism 条目
- 更新 CONTEXT.md：已有报告+边界区同步更新
- 数据源：Megatron-LM v1/v2/v3 论文知识 + 分布式训练工程经验
- 执行者：NeuronAgent / claude-sonnet-4-6

## [2026-04-23] ingest | Agent 心跳检测与实时 Dashboard 设计
- 新建报告：reports/knowledge_reports/Agent_心跳检测与实时Dashboard设计.md（5层框架：问题域·心跳机制·Dashboard数据流·延迟告警·集成点）
- 新建 concept：wiki/concepts/agent_observability.md（心跳检测·SSE实时推送·分级告警·自动干预）
- 更新 wiki/index.md：Concepts 表新增 agent_observability 条目
- 更新 CONTEXT.md：已有报告列表追加新条目
- 数据源：scripts/ea_events.py / ea_dashboard.py / task_state_cli.py / everagent.py 代码分析 + EverAgent 架构设计

## [2026-04-27] ingest | MIT 2026 AI 三条主线深度研究
- 新建报告：reports/knowledge_reports/MIT_2026_AI_三条主线_深度研究报告.md（LLMs+ · 世界模型 · Agent 编排三层系统化框架）
- 新建 entity：wiki/entities/mit_technology_review.md
- 新建 concepts：wiki/concepts/llms_plus.md / wiki/concepts/world_models.md / wiki/concepts/agent_orchestration.md
- 更新 wiki/index.md：新增 1 个 entity 条目与 3 个 concept 条目
- 更新 CONTEXT.md：已有知识报告列表追加新条目
- 数据源：AI资讯速览 2026-04-24、TechTarget 2026-04-22、MIT News / MIT Sloan 2026、WIRED 2025-12-09

## [2026-04-29] ingest | LLM 国内外主流评估体系详解
- 新建报告：reports/knowledge_reports/LLM_评估体系_深度解析_20260429.md（基准评测范式、国内外 leaderboard 解读、MMLU/C-Eval/GPQA/LiveBench/SWE-bench/BFCL 等逐项分析、场景匹配优先级矩阵）
- 新建 concept：wiki/concepts/llm_evaluation_systems.md（静态闭卷、动态去污染、偏好评测、代码工程、工具调用、多模态、安全评测速查）
- 更新 wiki/index.md：Concepts 表新增 llm_evaluation_systems 条目
- 更新 CONTEXT.md：已有知识报告列表追加新条目
- 数据源：Stanford HELM、LMSYS/LMArena、OpenCompass、C-Eval、CMMLU、SuperCLUE、LiveBench、SWE-bench、BFCL、MMLU-Pro、GPQA

## [2026-04-25] ingest | Distilling the Knowledge in a Neural Network (2015)
- 新建报告：reports/paper_analyses/42_distilling_2015.md（7步分析框架，高温softmax/软硬标签联合/logits matching推导，MNIST/ASR/JFT实验数值）
- 新建 concept：wiki/concepts/knowledge_distillation.md（定义、公式、关键证据、工程注意）
- 新建 entities：wiki/entities/vinyals_oriol.md、wiki/entities/dean_jeff.md
- 更新 entities：wiki/entities/hinton_geoffrey.md、wiki/entities/google_brain_deepmind.md
- 更新 wiki/index.md：新增 Knowledge Distillation 概念与 Vinyals/Dean 人物条目
- 更新 CONTEXT.md：已有报告与边界区追加知识蒸馏状态
- 数据源：ai-learning/papers/23_distilling_2015.pdf
- 执行者：NeuronAgent / Codex worker C

## [2026-04-25] ingest | AlphaZero: Mastering Chess and Shogi by Self-Play (2017)
- 新建报告：reports/paper_analyses/43_alphago_zero_2017.md（7步分析框架，说明本地 PDF 与索引标题不一致，按 AlphaZero 论文真实内容分析）
- 新建 concept：wiki/concepts/alphazero_self_play_rl.md（策略价值网络、MCTS、自我对弈闭环、关键训练与比赛数字）
- 新建 entity：wiki/entities/silver_david.md
- 更新 entity：wiki/entities/google_brain_deepmind.md
- 更新 wiki/index.md：新增 AlphaZero 概念与 David Silver 人物条目
- 更新 CONTEXT.md / PAPERS_INDEX.md：追加报告状态，并标明本地 PDF 实为 AlphaZero arXiv 论文
- 数据源：ai-learning/papers/24_alphago_zero_2017.pdf
- 执行者：NeuronAgent / Codex worker E

## [2026-06-21] ingest | MCP / A2A / AGENTS.md 标准化深度解析
- 新建报告：reports/knowledge_reports/MCP_A2A_Agents_md_标准化深度解析_20260621.md（5层框架：USB-C 工具层 / TCP-IP Agent层 / README 元信息层；时间线 2024-11→2026-06；对比矩阵 12 维度；5 个 mermaid 图）
- 新建 concept：wiki/concepts/agent_interop_protocols.md（速查表 + 关系图 + 关键时间线 + 已知局限）
- 更新 wiki/index.md：Concepts 表新增 agent_interop_protocols 条目
- 更新 CONTEXT.md：追加知识报告清单
- 核心数据：MCP 2024-11 Anthropic / 2025-03-26 升级 / 2025-03 OpenAI 跟进；A2A 2025-04-09 Google 发布 / 2025-06-25 捐 Linux 基金会 / 100+ 厂商；AGENTS.md 2025-08 联合发布 / 60K+ 项目
- 数据源：modelcontextprotocol.io + Google A2A spec + agents.md + 多家中文技术博客交叉验证
- 关联概念：agent_systems / agent_orchestration / agent_skill_ecosystem
- 执行者：NeuronAgent / claude-sonnet-4.6

## [2026-06-21] ingest | World Models / JEPA 路线深度报告
- 新建报告：reports/knowledge_reports/World_Models_JEPA_路线深度报告_20260621.md（5层框架 + 双路线对比矩阵 + 4 个 mermaid 图 + 简化 PyTorch 实现 + 关键时间线）
- 更新 concept：wiki/concepts/world_models.md（增加 6 个派生概念条目：JEPA / V-JEPA 2 / AMI / Cosmos / GAIA / Genie）
- 更新 CONTEXT.md：追加知识报告清单
- 核心数据：JEPA 路线 V-JEPA 2 1.2B/1M+hr/2025-06；LeCun 2025-11-19 离开 Meta → AMI 实验室 2026-01 融资 €350M；生成式路线 Cosmos 4B-14B（CES 2025）/ GAIA-2（2025-03）/ Genie 3 720p@24fps（2025-08）
- 数据源：arxiv 2506.09985（V-JEPA 2）+ Meta blog + NVIDIA Cosmos 技术报告 + DeepMind Genie 3 公告 + 多家中文评测
- 关联概念：generative_models_evolution / self_supervised_learning / llms_plus / agent_orchestration
- 执行者：NeuronAgent / claude-sonnet-4.6

