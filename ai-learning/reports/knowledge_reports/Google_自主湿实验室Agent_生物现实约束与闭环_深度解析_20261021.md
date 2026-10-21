---
title: "Google 自主湿实验室 Agent：用物理现实、实验反馈与人类战略闭合科学发现"
domain: "ai-learning"
report_type: "text_analysis"
status: "completed"
updated_on: "2026-10-22"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["autonomous_wet_lab", "scientific_agents", "verid", "lab_in_the_loop", "aptamer_design", "protein_binder_design"]
related_concepts: ["digital_twin", "closed_loop_learning", "human_in_the_loop", "experimental_grounding", "biosecurity"]
related_entities: ["google_research", "google_deepmind", "pylabrobot"]
---

# Google 自主湿实验室 Agent：用物理现实、实验反馈与人类战略闭合科学发现

> 核心原文：Google Research，[Grounding AI agents in biological reality: Building blocks for autonomous wet labs](https://research.google/blog/grounding-ai-agents-in-biological-reality-building-blocks-for-autonomous-wet-labs/)，2026-10。
>
> 配套一手材料：[VERID](https://www.gstatic.com/science-ai/verid_semantic_lab.pdf)、[Aptamers as a sandbox for lab-in-the-loop agentic molecular discovery](https://arxiv.org/abs/2610.24806)、[Agent-guided epitope excision enables economical de novo binder design](https://www.gstatic.com/science-ai/epitope_excision.pdf)。核验日期：2026-10-21。

## x → f → f(x)

- **x：作者在解决什么问题？** 科学 Agent 可以提出大量分子设计，但模型不了解实验台的实时物理状态，计算预测也无法可靠替代真实实验；真正的瓶颈从“生成候选”转向“安全执行、获得反馈并据此纠错”。
- **f：作者的回答是什么？** 建立三层闭环：VERID 用语义数字孪生约束机器人执行；aptamer 实验用快速湿实验反馈训练 Agent 识别假阳性；epitope excision 降低蛋白设计的计算成本，并让人类定战略、Agent 做战术搜索。
- **f(x)：接受这个框架后该怎么做？** 自主实验室应先建设可验证的执行层和数据闭环，再扩大 Agent 权限。Agent 的自主性要与验证速度、物理风险和目标可观测性共同设计。

---

## 一页结论

这组工作最重要的贡献不是宣称“AI 已能独立做药”，而是把自主科学发现拆成三个可以分别验证的工程问题：

1. **能否安全、可恢复地操作现实设备？** VERID 用持久化数字孪生记录几何、容量、试剂、吸头和仪器状态；所有 command block 先仿真，再下发硬件，并同步保存状态、视频和动作日志。
2. **能否从真实失败中改变下一轮策略？** Aptamer 闭环中，Agent 先把非特异性 G-quadruplex 当成高亲和候选，真实 counter-screen 暴露“黏珠子”的捷径后，它修改规则并在第三轮恢复 specificity 与 hit rate。
3. **能否让昂贵搜索更高效？** 蛋白 binder 工作把大靶标裁成局部 epitope window，使 FAP 的单次 refolding 运行时间约降 **88%**；在相同上限预算下，人类给出目标区域、Agent 调参和分配算力的混合组取得最高计算 hit rate。

**[推测] 三项工作共同支持一个判断：科学 Agent 的核心能力不是一次生成正确答案，而是让假设进入可测量的现实循环，在每一层保留验证器、状态和回滚点。**

但“自主湿实验室”仍是方向而非已完成系统。三项工作各自有真实实验数据，彼此之间却还没有一次端到端的组合运行，S1 也明确把连接这些线程列为下一步；VERID 的实证主要是染料和水；aptamer 只有两个主要蛋白靶标和三轮实验；FAP autonomy 对比只有一个大靶标、一个 scaffold 类与一个 Agent 模型。序列需要人类授权，机器人运行有人监督，实验结果也还不等于药效、安全性或临床价值。

---

## 1. 四份材料各自证明什么

| 来源 | 实际证据 | 不能推出的结论 |
|---|---|---|
| [S1：Google 博客](https://research.google/blog/grounding-ai-agents-in-biological-reality-building-blocks-for-autonomous-wet-labs/) | 三项研究的统一叙事、安全措施和关键结果 | 厂商综述会压缩方法细节，不能单独支撑泛化与因果判断 |
| [S2：VERID paper](https://www.gstatic.com/science-ai/verid_semantic_lab.pdf) | 三个染料实验 case study、仿真门、状态恢复、trace dossier、物理 self-play | 尚未展示 VERID 驱动复杂活体或致病实验；低风险染料结果不能直接外推到生物系统 |
| [S3：Aptamer paper](https://arxiv.org/abs/2610.24806) | 约 4,400 个测序构建体、两类主要靶标、三轮闭环、counter-screen、单克隆验证 | 样本仍是少量靶标；部分纳摩尔结果来自已知 motif 的 Agent 改造，不全是严格 de novo |
| [S4：Epitope excision paper](https://www.gstatic.com/science-ai/epitope_excision.pdf) | 15 targets / 3,666 designs 的裁剪验证、FAP 算力与 autonomy 对照、yeast display | 自主性比较集中于单一 FAP 靶标、三螺旋 scaffold 和 Gemini 3.1 Pro |

三份论文在当前材料中均应视为项目方一手 preprint/technical paper。它们提供了真实实验和精确数字，但尚缺独立复现与长期运行证据。

---

## 2. VERID：先解决“代码正确但物理错误”

### 2.1 为什么普通工具调用不够

液体处理机器人不是无状态 API。一个指令是否安全取决于当前台面：

- 槽的长度能否容纳 8 通道吸头；
- 某孔是否还有足够体积；
- 目标板是否盖着盖子；
- 前一步故障后哪些洗涤、稀释和读数已经完成；
- 枪头内壁、液面高度和停留时间是否引入系统偏差。

LLM 可以生成语法正确的 PyLabRobot 代码，却无法仅凭代码文本判断这些条件。VERID 因此在 Agent 与硬件之间加入一个长寿命的**语义数字孪生**。

### 2.2 四项核心服务

1. **Introspection**：用结构化实体树查询设备、labware、well、volume、liquid height 与 tip inventory；
2. **Simulation gate**：克隆当前状态，快速执行虚拟 dry-run，检查质量守恒、几何碰撞、容量、耗材与耗时；
3. **Safe execution**：只有通过物理、体积与化学规则的 command block 才能下发；
4. **Trace dossier**：把状态快照、代码、底层硬件命令、仪器 telemetry、顶部与侧面视频对齐到同一时间轴。

这相当于为湿实验建立“类型系统 + 事务日志 + 回放调试器”。它不会保证科学假设正确，但能让 Agent 的每一次行动有明确的前置状态、验证和审计证据。

### 2.3 三个 case study 揭示的真实价值

**案例一：重复并不能修复系统偏差。** 染料连续稀释出现异常，视频与执行 trace 显示枪头靠近孔底造成密度分层和遮挡。修改混匀与吸液高度后，四种染料的平均两倍稀释因子达到 **1.92×–1.99×**，replicate spread 降至极小。

**案例二：持久状态支持故障恢复和因果诊断。** 第四种染料执行中通信失败，系统从故障点续跑，不必重做前三种。仿真还发现 8 个吸头至少跨 **72.0 mm**，超过槽长 **71.2 mm**，于是改为 7 通道混匀、两次 4 通道取样。后续 8-column factorial diagnostic 通过反转通道分配，把约 **−28.6%** 的缺口从 Channel 8 移到 Channel 1，证明问题不是 Channel 8 硬件故障，而是 7 个枪头内壁残液造成 **+4.9 µL / +40.6%** carryover。

**案例三：物理 self-play 学到可迁移的实验规则。** Agent 在固定一块 96-well plate、有限吸头与 RGB 相机条件下推断盲测染料混合物。冷启动多轮实验最终 loss 为 **307 mnats**；把不含样本答案的物理与程序经验传给下一代后，两轮达到 **58 mnats**，改善超过五倍。它学到相机饱和、视角反射、小体积移液误差、垂直浓度梯度与光谱退化等限制。

这些案例说明 trace 的用途不是“事后留档”，而是让 Agent 能设计判别性实验，把随机噪声、系统偏差与目标信号分开。

---

## 3. Aptamer 闭环：Agent 先走捷径，再被现实纠正

### 3.1 为什么选 aptamer

Aptamer 是能与蛋白结合的短 DNA/RNA 序列。它的序列本身就是功能分子，不需要经历蛋白设计中的克隆、表达和纯化长链路。S3 的流程每轮约设计 **1,000** 个候选，进行 pooled synthesis、磁珠 pull-down 与 NGS；单轮约 **10 天**，成本约 **$3/候选**。论文精确统计为 **4,405** 个测序构建体，其中除了三轮主实验，还包含一组 supplementary Round 1b expansion pool；正文常将其概括为约 4,400。

这使“设计 → 实验 → 定量正负反馈 → 下一轮”能在数周内循环，而传统 SELEX 往往从 `10^13–10^15` 随机分子出发，经历 8–15 轮选择。

**谁在做什么：闭环里没有一步湿实验是 Agent 亲手执行的。** S3 的 Methods 把分工写得很明确：

| 环节 | 执行者 |
|---|---|
| 每轮候选设计、测序数据分析、下一轮策略修改 | Agent |
| pull-down、PCR、sequencing 等全部湿实验操作 | 人类研究者 |
| 把整理后的数据交回 Agent | 人类研究者 |

所以 “lab-in-the-loop” 的准确含义是：实验在环里，人握着实验台；Agent 的贡献是设计与从负反馈中修改规则的能力。这也是本文将其称为实验闭环、而不是无人湿实验室的原因——把这组工作读成“AI 已能独立操作湿实验室”是最大的误读（程序层面的序列授权与协议审查另见 §6）。

### 3.2 两个靶标，两种失败模式

| 靶标 | Round 1 | Round 2 | Round 3 | Agent 学到什么 |
|---|---:|---:|---:|---|
| α-thrombin hit rate | 0.0%（0/167） | 26.0%（54/208） | 42.1%（131/311） | 固定 primer 会侵入核心折叠；加入 clamped flanking stem 后恢复，并继续多样化 |
| Myoglobin hit rate | 10.2%（20/196） | 3.7%（9/244） | 33.5%（184/549） | 单看 pull-down 会奖励非特异 G4；必须减去裸磁珠与 off-target 结合，并改用非 G4 scaffold |

Myoglobin 的过程最有学习价值。Round 2 中 G-quadruplex 被大量富集，raw binding 看起来更强，但 specificity 从 **75.0% 降到 19.1%**。分析 Agent 从原始 count matrix 发现，**97% 的 cross-reactive binders** 是会黏附磁珠和其他蛋白的 G4。Round 3 它限制未夹紧 G4、加入 bead residual subtraction，并把组合转向非 G4 结构，最终 specificity 恢复到 **72.4%**，hit rate 达 **33.5%**。

α-thrombin 的 specificity 最终达到 **98.5%**。八个 full-length 候选的单克隆磁珠滴定与 pooled enrichment 的相关性为 **Pearson r=0.90**。其中 Agent 改造的已知 motif 达到初步 apparent `K_D = 24.6–133 nM`；严格 de novo scaffold 只显示低微摩尔级结合，说明“42.1% hit rate”不能被误读为大量高亲和全新药物分子。

### 3.3 真实实验为何不可替代

S3 用 Round 3 Myoglobin 库评测 9 个工具的 12 个开放指标。多种 target-conditioned 3D、inverse folding、foundation model 与 G4 scorer 的 ROC-AUC 多数接近或低于随机（约 **0.36–0.52**）；只有 target-agnostic 的 ViennaRNA 稳定性/折叠纯度达到 **0.729 / 0.763**，但它不知道具体蛋白靶标，无法判断 affinity 与 specificity。

这揭示闭环的本质：模型容易优化一个可见 proxy，而真实 counter-screen 才能暴露 proxy 与目标之间的裂缝。没有裸磁珠、off-target 和多轮负反馈，Agent 会把实验伪影当成成功经验。

---

## 4. Epitope excision：把算力花在结合位点附近

### 4.1 技术动机

De novo protein binder 通常经历 backbone generation、sequence design 和 complex refolding。大靶标的大部分残基离结合界面很远，却仍让 AlphaFold3 支付更大的 token bucket 与近似二次计算成本。

Epitope excision 只保留接触残基和周围 halo。S4 在 **15 个 targets、3,666 个 designs** 上测试 11 Å halo：

- excised interface 的 median Cα RMSD 为 **0.37 Å**；
- **88.2%** 设计低于 1 Å，**93.7%** 低于 2 Å；
- 相比 full target，平均 ranking `ΔROC-AUC = -0.048`，说明总体接近，但并非无损；
- 7/15 小靶标已在最小 256-token bucket，裁剪没有速度收益。

因此，裁剪适合大、多结构域靶标，不是普遍免费加速。halo 太小会损伤局部几何，MSA 的作用也随靶标变化。

### 4.2 FAP 上的算力与 autonomy 对照

FAP extracellular domain 有 **719 residues**。完整复合物约 779 tokens，落在 AF3 的 1024-token bucket，单 fold 约 **59.3 s**；85–130 residue crop + binder 落入 256-token bucket，约 **6.9 s**，单次运行时间下降约 **88%**。

在相同 hit 定义与 **132.87 GPU-hour** 上限下：

| 组别 | 决策者 | 计算 hit rate | GPU-hours | hits/GPU-h | 命中 epitope 数 |
|---|---|---:|---:|---:|---:|
| A | 人类独立 | 5.06% | 132.87 | 12.6 | 4 |
| B | 人类定战略 + Agent 做战术 | **9.33%** | **77.18** | **23.2** | 7 |
| C | Agent 独立 | 6.18% | 124.43 | 14.5 | **13** |

三组的差别可以用一句话讲清：**谁决定“在哪打”，谁决定“怎么打”。** 蛋白设计有两级决策——战略级（结合靶标的哪个区域、为什么）和战术级（epitope 集合、crop 尺寸、ProteinMPNN 参数、算力分配、何时迭代），三组只是两级决策的不同分配：

- **A 组，human alone**：两级都由人类决定。hit rate 5.06%，预算用满（132.87 GPU-h），命中 4 个 epitope，每 GPU 小时产出 12.6 个 hits——中规中矩，但没有杠杆；
- **B 组，human + agent 混合**：人类给战略级先验，指定 catalytic rim 这一生物目标区域；Gemini 3.1 Pro 接管全部战术级决策（epitope set、crop size、ProteinMPNN 参数、算力分配与迭代动作）。hit rate 提高到 **9.33%**（相对 A 组约 **+84%**），只花 **77.18 GPU-h（约 58% 预算）**，命中 7 个 epitope，每 GPU 小时产出 23.2 个 hits，接近 A 组的两倍；
- **C 组，agent alone**：Agent 自己先探索“在哪里绑定”，再优化“怎么绑定”。它最终收敛到与人类相近的 mouth-occlusion 策略，但前期开放探索多消耗了算力（124.43 GPU-h），hit rate 6.18%；换来的是覆盖面——命中 **13** 个 epitope，三组中最多。

**[推测]** 由此可以得到一个比“全自主越多越好”更细的判断：**战略先验便宜且正确时，人类一句话就能砍掉大半搜索空间，这层不宜过早交给 Agent；战术优化繁琐、高频、可量化，更适合交给 Agent；当没有人说得清该在哪打时，agent-alone 用算力换覆盖，是更昂贵的探索方式。**

湿实验用 5,000-member yeast-display library、三轮 FACS 与测序筛选，四个代表性 enriched clones 的 apparent `K_D` 为 **3.0–9.1 nM**。这证明存在强结合候选，但还未证明可溶表达、FAP domain specificity、酶抑制、细胞效果、毒性或药代性质。

---

## 5. 三层合在一起，才接近自主实验室

```text
科学目标与安全边界（人类）
          ↓
候选生成与资源分配（Agent + 计算工具）
          ↓
协议规划 → VERID 状态查询 → 仿真门 → 人类审批 → 机器人执行
          ↓
状态 / 视频 / 仪器 / 实验读数的统一 trace
          ↓
反例诊断、规则更新与下一轮设计
```

**每一层各自解决一类其他层无法替代的失败**，人类战略则横跨三层：

| 层 | 解决什么失败 | 如果缺这一层 | 已验证到哪一步 |
|---|---|---|---|
| **执行层：VERID** | 代码正确但物理错误——几何碰撞、容量与耗材、故障后无法恢复 | 再正确的科学计划也会在台面上报废，且事后无法归因 | 三个染料 case study：偏差诊断、故障点恢复、self-play 经验迁移；尚未驱动复杂生物协议 |
| **反馈层：aptamer 闭环** | 计算代理指标与真实目标的裂缝——proxy hack、非特异结合 | Agent 把“黏磁珠”当成亲和力，把实验伪影固化为经验 | 两个靶标三轮闭环 + counter-screen 纠正 G4 捷径；全部湿实验由人类执行 |
| **计算经济层：epitope excision** | 算力浪费在远离结合界面的残基上 | 搜索预算撑不起足够轮次的闭环学习 | 15 targets / 3,666 designs 裁剪验证 + FAP 固定预算对照；仅单一靶标、scaffold 与模型 |
| **人类战略与审批（横跨三层）** | 战略错配——预算烧在宽泛探索、越过未验证的风险边界 | 自动化只会更快地做错事 | FAP 中 B 组混合对照优于两端；序列授权、协议审查与运行监督 |

这张表的最后一列是全篇最需要直白说出的限制：**每一层都有真实数据支撑，但没有任何一层跑过另外两层。** VERID 没有执行过 aptamer 或 binder 协议；aptamer 闭环没有 VERID 仿真门，湿实验靠人手；epitope excision 是计算 campaign 加 yeast-display 验证，同样不经 VERID。层与层之间的接口——仿真门接入实验闭环、实验读数直接驱动下一轮计算——正是 S1 明确列为 next step 的部分。**[推测]** 对“Google 做出了自主湿实验室”的准确读法是“三块各自经过验证的积木，加一张尚未拼装的图纸”，而不是一个已经跑通的端到端系统。

因此，自主程度不应只按“Agent 做了多少步骤”衡量，而应按每层是否存在可观测状态、判定标准、失败隔离和人工控制点衡量。

---

## 6. 安全框架与现实边界

Google 在 S1 中披露三类措施：

1. 选择受控、非感染、无 gain-of-function 风险的测试床，并对设计序列做 biosecurity screening；
2. 所有机器人协议先在 VERID dry-run，通过数字孪生检查后才执行；
3. 人类授权和审查序列、核对 wet-lab protocol，并监督机器人运行。

这些措施说明当前系统是**human-directed autonomous discovery**，不是无人值守的开放式生物实验员。安全也不能只靠序列筛查：目标函数投机、实验捷径、错误数据进入学习环、trace 被篡改、跨轮积累偏差和硬件失效都需要独立控制。

值得特别关注的是 Myoglobin 的 G4 事件。它虽然没有造成生物安全事故，却是一个清晰的 alignment failure：系统忠实优化了“raw pull-down enrichment”，但这不是研究者真正需要的“target-specific binding”。未来更高风险实验中，同类目标错配可能产生更严重后果。

---

## 7. 局限

1. VERID 的核心实证是染料、水和光学/流体误差，没有完成复杂生物协议的长期无人运行；
2. aptamer 研究集中在三轮与少量蛋白靶标，不能估计跨靶标稳定性；
3. aptamer apparent affinity 的纳摩尔结果主要来自 Agent 改造的 literature motifs，strict de novo 仍较弱；
4. pooled hit、yeast display enrichment 和 apparent `K_D` 都不等于药效、选择性、安全性或临床成功；
5. epitope excision 在某些 shallow-MSA/局部结构敏感靶标上会降低 ranking，不能固定关闭 MSA；
6. autonomy 对照只覆盖 FAP、三螺旋 binder 与一个 LLM controller；C 组还自行在 94% 预算处停止；
7. B-variant 显示评分装置本身能让计算 hit rate 大幅变化，autonomy 效果必须与 metric 选择分开；
8. 三项研究由 Google 团队自报，尚缺独立实验室复现和端到端组合验证。

---

## 8. 思考与追问

### 8.1 自主实验室的最小单元应是“可回放实验事务”

一次事务至少应包含：目标、版本化协议、初始数字孪生状态、仿真收据、审批者、真实动作、传感器记录、结果、异常和下一轮学习。只有这样，Agent 学到的规则才能追溯到具体物理证据，并在发现污染后撤销。

### 8.2 负数据可能比更多生成能力更稀缺

Aptamer 结果说明，高质量 bare-bead、off-target 和失败 readout 直接决定 Agent 是否学到正确目标。未来科学 Agent 的竞争优势可能来自“能产生怎样的判别性负数据”，而不只是能生成多少候选。

### 8.3 人类应控制哪一层？

S4 暗示一个可执行的分工：人类定义研究问题、不可越过的安全边界、关键评价指标与初始搜索区域；Agent 负责参数搜索、预算调度、异常诊断和候选组合。随着验证器成熟，再逐层下放，而不是一次性追求全自主。

### 8.4 下一步最关键的组合实验

把 VERID 与真实 aptamer 或 protein binder 闭环连起来，在预注册目标与预算下比较：人工协议、Agent 规划但人工执行、VERID 仿真门下的 Agent 执行。连续运行多轮，统计科学 hit、物理失败、人工干预、污染恢复、每个有效候选的时间与成本，以及错误经验是否进入下一轮。只有这个端到端实验，才能检验“自主湿实验室”是否从三块优秀组件变成可靠系统。

---

## 参考来源

1. Google Research. [Grounding AI agents in biological reality](https://research.google/blog/grounding-ai-agents-in-biological-reality-building-blocks-for-autonomous-wet-labs/), 2026.
2. Delley et al. [Semantic Representation for Agentic Self-Play in Automated Laboratories (VERID)](https://www.gstatic.com/science-ai/verid_semantic_lab.pdf), 2026.
3. Cutts et al. [Aptamers as a sandbox for lab-in-the-loop agentic molecular discovery](https://arxiv.org/abs/2610.24806), 2026.
4. Kim et al. [Agent-guided epitope excision enables economical de novo binder design](https://www.gstatic.com/science-ai/epitope_excision.pdf), 2026.
5. PyLabRobot. [Open-source laboratory automation interface](https://github.com/PyLabRobot/pylabrobot).

