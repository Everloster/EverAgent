# AI 学习与实践记录

这里按公开产物整理已经研究、实现或评估过的内容，方便找到证据和后续问题。它描述材料的验证范围，不是对个人或模型熟练度的评分。

本页核对日期：2026-10-26。下列实验保留各自的原始日期；本次文档更新不表示重新运行了所有实验。

可核对的 AI 使用记录包括 [Coding Agent 开工行为比较](#e01context-开工探针2026-10-21)与[报告的独立模型复核](#e02一篇报告的质量检查2026-10-25)。阅读笔记、代码实验和实际模型调用分别列出，不将“研究过一个主题”写成“已经实现了对应系统”。

## 怎样阅读这些证据

| 类型 | 能说明什么 | 不能直接说明什么 |
|---|---|---|
| 研究报告 | 对来源、机制和限制的整理 | 已具备对应的工程能力 |
| 代码或 Notebook | 存在一个实现或教学入口 | 当前环境一定能运行 |
| 运行记录 | 记录中的配置曾产生相应输出 | 跨环境可复现或有泛化效果 |
| 受控评估 | 固定样本与口径下的比较结果 | 整个领域都已掌握或长期效果稳定 |

这些类型可以并存，不是自动升级的等级。

## 已有材料与缺口

| 主题 | 公开入口 | 验证范围与缺口 |
|---|---|---|
| Agent、Harness 与 Context Engineering | [指令分层](./docs/CONTEXT_ENGINEERING.md)、[ACE A/B](./docs/ACE_CONTEXT_AB_20261021.md) | 有固定开工探针；不是完整任务质量评估 |
| Personal Context 与 Memory | [构建指南](./PERSONAL_CONTEXT.md)、[三层分析](./ai-learning/reports/knowledge_reports/个人Context与Memory三层架构_OpenViking_手机环境_APP跨对话_深度解析_20261025.md) | 有方法与私有试点的公开摘要；缺可公开重放的更新、删除和收益实验 |
| 研究报告质量 | [质量检查](./docs/REPORT_QUALITY_GATE.md)、[报告索引](./docs/REPORT_INDEX.md) | 部分报告有证据账本与独立模型复核；不覆盖全部历史内容 |
| Transformer、MoE 与 Long Context | [实验地图](./ai-practice/MAP.md) | 有教学实现与缩尺模拟；不等于大规模训练或真实长上下文基准 |
| 后训练与 GRPO | [GRPO 缩尺实验](./ai-practice/experiments/exp_008_grpo_simulation.md) | 有 CPU toy 运行记录；缺同任务下的真实模型消融 |
| 推理系统与 Kernel | [vLLM 调度器](./ai-learning/reports/knowledge_reports/vLLM_调度器_continuous_batching真身_20260909.md)、[Mamba-2 Kernel](./ai-learning/reports/knowledge_reports/NVIDIA_CUDA_Tile_Mamba2高性能Kernel_深度解析_20261021.md) | 以研究和局部源码分析为主；没有统一的多卡吞吐或成本基准 |
| 播客与长内容学习 | [Podcast Learning](./podcast-learning/README.md) | 有转写与报告产出；不同来源的核验程度需要逐篇查看 |
| Agent 安全 | [OpenShell / Sentry 分析](./ai-learning/reports/knowledge_reports/NVIDIA_OpenShell_Sentry_Agent运行时安全架构_深度解析_20261021.md)、[执行协议](./docs/PROTOCOL_COMMON.md) | 有规则、部分门禁与研究；不能替代运行时强隔离或攻击测试 |
| Robotics 与 AI for Science | [Microduck](./ai-learning/reports/knowledge_reports/NVIDIA_Microduck_Agentic_Robotics_仿真训练与Sim2Real_深度解析_20261025.md)、[自主湿实验室](./ai-learning/reports/knowledge_reports/Google_自主湿实验室Agent_生物现实约束与闭环_深度解析_20261021.md) | 文献与实现分析；没有本仓的硬件或湿实验结果 |

## 几项可以具体核对的记录

### E01：Context 开工探针，2026-10-21

[结果 JSON](./evals/results/ace-context-ab-20261021.json)记录了 14 个 case、两组各重复 3 次，共 84 次运行。环境为 Pi、`zai-coding-cn/glm-5.3`、thinking=`medium`。

| 项目 | Baseline | Candidate |
|---|---|---|
| 固定提交 | `4b3811ad` | `35d7da87` |
| 平均分 | 79.76 | 98.57 |
| P10 | 50 | 100 |
| 路由命中率 | 100% | 100% |
| 记录的平均输入 tokens | 64667.4 | 38247.79 |
| 平均耗时 | 44.56 秒 | 35.85 秒 |

比较器记录 `accepted=true`。分数变化来自产物策略、Context 预算等维度，不能说路由命中率也提高了。输入 tokens 是这组运行的记录口径，不等于未缓存用量、实际费用或全项目节省。

[评估报告](./docs/ACE_CONTEXT_AB_20261021.md)和[执行脚本](./scripts/run_ace_context_ab.py)提供更多细节。若重新运行，应固定上述两个提交、模型与任务集，将输出写到新位置，不用当前 `HEAD` 替代历史候选，也不覆盖旧结果。该探针只观察开工行为，不能替代完整任务验收。

### E02：一篇报告的质量检查，2026-10-25

[三层 Context / Memory 报告](./ai-learning/reports/knowledge_reports/个人Context与Memory三层架构_OpenViking_手机环境_APP跨对话_深度解析_20261025.md)有配套[证据账本](./ai-learning/reports/knowledge_reports/.quality/个人Context与Memory三层架构_OpenViking_手机环境_APP跨对话_深度解析_20261025.evidence.json)和[复核记录](./ai-learning/reports/knowledge_reports/.quality/个人Context与Memory三层架构_OpenViking_手机环境_APP跨对话_深度解析_20261025.review.json)。该 revision 的主复核模型为 MiniMax M3.1 Flash，记录为 `decision=pass`、`score=98.4`。

本轮只读检查也返回 `ERROR 0 / WARN 0`。可从仓库根目录核对：

```bash
python3 scripts/report_quality.py check ai-learning/reports/knowledge_reports/个人Context与Memory三层架构_OpenViking_手机环境_APP跨对话_深度解析_20261025.md
```

该分数来自本仓规则下的模型复核，不是外部认证；只绑定记录中的报告与证据版本，不覆盖本页、新指南或新案例摘要，也不能推及其他报告。

### E03：GRPO 的 toy 运行记录，2026-06-21

[源码](./ai-practice/src/grpo_simulation.py)和[实验笔记](./ai-practice/experiments/exp_008_grpo_simulation.md)使用不依赖 Prompt 的 2-token 策略，演示组内采样、相对优势、clip 与 KL 惩罚。

历史配置为 20 个 toy prompt、group size 8、80 steps、seed 0。共享答案模式下所有题的目标都设为 7，训练采样的 accuracy 从约 `0.03` 到 `0.97`，entropy 从 `4.445` 到 `0.135`，KL 从 `0` 到 `3.387`。不同题使用不同答案时，末步 accuracy 约为 `0.19`。

这些数值与已有运行记录一致，本轮未重跑训练。共享答案上的高分不是算术推理能力；反例体现的是策略不看 Prompt 的限制，不是 GRPO 对真实语言模型的效果结论。

### E04：私有试点的公开摘要

[脱敏案例](./PERSONAL_CONTEXT.md#真实脱敏案例多设备-agent-会话-context)和[JSON 摘要](./docs/personal-context-multidevice-case-20261025.json)仅整理已有公开报告的结论与限制，不公开正文、查询、设备或访问方式。

可核对的是摘要与公开来源的对应关系。原始运行资料未公开，不能独立重放；当前摘要也没有可核验的量化检索数据，不用它证明 token 收益、任务收益或匿名性。

## 接下来值得补什么

- 用可公开的数据验证 Context 的检索、更新、删除和拒答，而不只报告私有试点结论；
- 为已有实验补可核对的依赖版本、运行命令与输出，区分工具估算和实际测量；
- 将开工探针延伸到完整任务，记录失败、返工与成本，而不只看平均分。

这些是待讨论的方向，不是已完成的能力或自动派工清单。后续有新证据或发现旧结论不成立时，再更新对应条目；普通报告新增只进入[报告索引](./docs/REPORT_INDEX.md)。
