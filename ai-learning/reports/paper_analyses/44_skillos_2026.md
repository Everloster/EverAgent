---
title: "SkillOS: Learning Skill Curation for Self-Evolving Agents"
domain: "ai-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-05-13"
---

# SkillOS: Learning Skill Curation for Self-Evolving Agents

## 基本信息卡片

```text
论文标题：SkillOS: Learning Skill Curation for Self-Evolving Agents
作者：Siru Ouyang, Jun Yan, Yanfei Chen, Rujun Han, Zifeng Wang, Bhavana Dalvi Mishra, Rui Meng, Chun-Liang Li, Yizhu Jiao, Kaiwen Zha, Maohao Shen, Vishy Tirumalashetty, George Lee, Jiawei Han, Tomas Pfister, Chen-Yu Lee
机构：University of Illinois Urbana-Champaign; Google Cloud AI Research; Massachusetts Institute of Technology
发表年份：2026
版本：arXiv:2605.06614v1, submitted on 2026-05-07
领域：LLM Agent, Self-Evolving Agents, Skill Curation, Procedural Memory, Reinforcement Learning
论文长度：11 pages main text, 6 figures, 3 tables
重要性评级：⭐⭐⭐
```

---

## 一句话总结

> SkillOS 把“Agent 如何从经验中整理可复用技能”变成一个可训练的强化学习问题，用 grouped task streams 和复合奖励训练 skill curator 管理外部 SkillRepo。

---

## 读前定位

这篇论文非常适合放在 Agent 系统主线里读。

它不是在训练一个更强的基础模型。

它也不是单纯给 Agent 加一个向量数据库或长上下文记忆。

它研究的是一个更工程化、也更接近真实部署的问题：

```text
Agent 做完任务以后，如何把经验整理成下一次真的能用的技能？
```

在传统 Agent 系统里，常见做法有三类：

第一类是不记忆。每个任务从 prompt、工具和当前上下文重新开始。

第二类是原始记忆。把历史轨迹、问答、日志或总结存起来，下次检索出来。

第三类是手工技能。人类写 SKILL.md、workflow、工具说明和注意事项。

SkillOS 关心的是第四类：

```text
让一个可训练的 curator 从执行轨迹中学习如何插入、更新、删除技能。
```

这使它和已有 `Agent Systems`、`Agent Skills`、`Agent Memory`、`Agent 自进化技术路径` 等知识报告构成自然延伸。

---

## Step 1 | 背景与动机（WHY）

### 1.1 one-off problem solver 的局限

论文开头指出，LLM-based agents 越来越多地用于 streaming tasks，但主流范式仍然像一次性解题器。

也就是说，Agent 完成当前任务后，下一次未必能系统性复用这次经验。

这在真实环境里非常浪费：

- WebShop 里常见的筛选、比较、回退路径会重复出现。
- ALFWorld 里常见的物体状态变化、位置搜索、失败恢复会重复出现。
- 数学推理里常见的分解、约束建模、验证答案会重复出现。

如果 Agent 每次都从零探索，性能和效率都会受损。

### 1.2 procedural memory 为什么关键

论文把 reusable skills 视为 self-evolution 的程序性记忆。

这里的“技能”不是模型参数里的隐式知识，而是外部、可读、可编辑、可检索的 Markdown 文件。

这点很重要。

外部技能库有几个优势：

- 可审计：人类能打开技能文件看内容。
- 可组合：不同技能可以一起进入上下文。
- 可迁移：不一定绑定某个 executor 模型。
- 可维护：可以增删改，不需要重新训练 executor。

### 1.3 现有方法的问题

论文认为已有 skill curation 方法有三类不足。

第一，手工技能很强，但不规模化。Anthropic-style skills 需要人类专业知识编写，无法覆盖 deployment 中不断出现的新任务。

第二，prompt 或 heuristic memory operation 有固定规则，但缺少来自下游任务表现的反馈。它可能会存很多看似合理、实际无用的内容。

第三，已有 RL 方法多关注“如何使用技能”或短任务流中的局部适配，难以学习 update/delete 这类长期管理动作。

SkillOS 的核心判断是：

```text
真正难的不是插入一条新技能，而是长期维护一个紧凑、有用、适配 executor 的 SkillRepo。
```

---

## Step 2 | 核心贡献（WHAT）

### 2.1 贡献一：模块化的 executor-curator 分工

SkillOS 把系统拆成两个角色。

`Agent Executor`：

- 冻结不训练。
- 接收当前任务、环境观察和检索出的相关技能。
- 负责实际完成任务。

`Skill Curator`：

- 可训练。
- 观察 executor 的执行轨迹、自评结果和相关技能。
- 通过函数调用更新 SkillRepo。

这个分工的关键价值是：学习发生在 curator，而不是 executor。

这避免了频繁微调大 executor 的成本，也降低了灾难性遗忘风险。

### 2.2 贡献二：SkillRepo 作为外部 OS 式技能仓库

论文把技能表示成 Markdown 文件。

每个 skill 有两部分：

- YAML frontmatter：技能名称和适用场景描述。
- Markdown instructions：可执行知识、工作流、约束、可复用启发式。

curator 可用三种操作管理仓库：

```text
insert_skill
update_skill
delete_skill
```

这就是标题中 `SkillOS` 的 OS 隐喻：技能不是一次性上下文，而是一组可被文件操作管理的外部能力资源。

### 2.3 贡献三：grouped task streams

SkillOS 不把训练任务当作独立样本。

它先给任务标注 skill-relevant attributes，例如 topic、skills、concepts、pitfalls，再按属性相似度构造任务组。

形式化地说，论文令每个任务 `x_i` 有属性集合：

```text
Z_i = {z_i^1, z_i^2, ..., z_i^|Z_i|}
```

再把数据集划分成：

```text
D = {G_1, G_2, ..., G_M}
G_m = {x_m,1, x_m,2, ..., x_m,|G_m|}
```

同组任务存在非平凡技能依赖。

这样早期任务产生的技能，会在后续相关任务中被检验。

这比随机任务流更适合训练 curator，因为它把“长期有用性”压缩到一个可学习的短时间窗口里。

### 2.4 贡献四：复合奖励

论文的奖励不是只看当前任务成功。

它定义复合奖励：

```text
r = r_task + lambda_f r_fc + lambda_u r_cnt + lambda_c r_comp
```

四个部分分别是：

`r_task`：

对组内第 2 到最后一个任务的平均成功率，衡量 evolving SkillRepo 对后续任务的下游帮助。

`r_fc`：

函数调用是否有效，衡量 curator 是否生成可执行的 insert/update/delete 操作。

`r_cnt`：

技能内容质量，由外部 judge Qwen3-32B 打分。

`r_comp`：

压缩奖励，鼓励 SkillRepo 相对 curator 输入上下文更短，避免把轨迹原样复制进技能库。

这个奖励设计体现出 SkillOS 的核心立场：

```text
技能要能提高后续任务表现，也要格式合法、语义有用、足够紧凑。
```

### 2.5 贡献五：用 GRPO 训练 curator

论文使用 Grouped Reward Policy Optimization。

对同一个任务组采样 `N` 条完整 curation sequence rollouts。

每个 rollout 都形成不同的 SkillRepo 历史。

优势函数为：

```text
A_n = r_n - (1/N) sum_{n'=1}^{N} r_{n'}
```

然后使用 clipped surrogate objective：

```text
L = E_n [min(rho_n A_n, clip(rho_n, 1-epsilon, 1+epsilon) A_n)]
```

其中：

```text
rho_n = pi_S(c_n | chi) / pi_old(c_n | chi)
```

论文还说明：把同一个 rollout 的 advantage 均匀分配给 curation tokens，并去掉 GRPO 中的 KL term 来鼓励探索。

---

## Step 3 | 技术细节（HOW）

### 3.1 闭环执行流程

每个时间点 `t`，系统有当前 SkillRepo：

```text
S_t = {s_t^1, s_t^2, ..., s_t^N_t}
```

任务 `x_t` 到达后：

1. 用 BM25 从 `S_t` 中检索相关技能 `S~_t`。
2. 冻结 executor 根据任务、观察和技能执行动作。
3. 产生轨迹 `xi_t = {o_1, a_1, ..., o_n, a_n}`。
4. curator 观察轨迹、自评结果和相关技能。
5. curator 输出 curation operations。
6. `ApplyOps` 把 `S_t` 更新成 `S_{t+1}`。

这个设计让执行和学习分离：

```text
executor 负责做事
curator 负责让下一次更会做事
```

### 3.2 为什么 BM25 足够

论文使用 BM25 检索技能，而不是复杂向量检索。

这不是重点所在。

因为 SkillOS 的创新不在 retrieval model，而在 curator 如何生成和维护被检索对象。

换句话说：

```text
检索只是入口。
真正难的是仓库里有没有好技能。
```

### 3.3 为什么 update/delete 很重要

很多 memory agent 容易停在 insert。

每次失败就加一条经验，每次成功也加一条经验。

这种做法短期有效，长期会让上下文越来越重，重复技能越来越多，甚至出现互相冲突的建议。

SkillOS 通过训练让 curator 逐步从 insert 转向 update。

论文 Figure 4 显示，训练早期 insert 占主导；随着训练推进，update 越来越频繁，delete 保持较小但略有增长。

这说明 curator 学到的不是“看到经验就存”，而是“已有技能能否被修订和合并”。

### 3.4 压缩奖励的实际意义

`r_comp` 的形式是：

```text
r_comp = average_i (1 - |S_i| / |chi_i|)
```

其中 `|S_i|` 是 SkillRepo token 长度，`|chi_i|` 是 curator 输入上下文 token 长度。

直觉上，它鼓励 curator 把轨迹压缩成短技能，而不是把所有观察和动作粘贴进去。

这和工程上的经验完全一致。

一个好的 Agent skill 往往不是“我上次怎么做的逐字记录”，而是：

- 什么情况下使用。
- 标准流程是什么。
- 常见失败点是什么。
- 何时不要使用。
- 出错后如何恢复。

### 3.5 内容质量奖励的风险

`r_cnt` 使用 Qwen3-32B 作为外部 judge 给 curation decision 打分。

这带来一个值得注意的限制：

judge 评价的是内容质量和潜在有用性，不等于 executor-grounded utility。

论文用 `r_task` 作为主反馈来缓解这个问题。

因此，`r_cnt` 更像正则项：它帮助 curator 不要写出无意义技能，但不能替代下游任务表现。

---

## Step 4 | 实验验证

### 4.1 数据集与任务

论文评估三类任务。

`ALFWorld`：

文本交互式 embodied AI 环境，包含家居任务、导航、物体操作、状态变化。

`WebShop`：

模拟在线购物环境，需要根据用户需求浏览、筛选并购买产品。

`Reasoning`：

单轮推理任务，包括 AIME24、AIME25、GPQA-Diamond。训练数据来自 DeepMath-103k 中随机采样的 33,000 条数据。

### 4.2 训练配置

论文训练配置如下：

- curator base model：Qwen3-8B。
- training-time executor：Qwen3-8B。
- optimizer method：GRPO。
- learning rate：`1e-6`。
- batch size：32。
- group size：8。
- training hardware：16 H100 GPUs。
- training framework：verl。
- training time：ALFWorld 约 3 天，reasoning 约 2.5 天，WebShop 约 5 天。
- reward weights：`lambda_f = 1.0`, `lambda_u = 0.1`, `lambda_c = 0.05`。
- 结果报告：3 次运行均值和标准差。

测试时还额外使用 Qwen3-32B、Gemini-2.5-Pro 和 appendix 中的 Gemini-3.1-Flash-Lite 作为 executor。

### 4.3 ALFWorld 主结果

ALFWorld 上，SkillOS 在三个 executor 下都提升成功率并减少步数。

关键平均结果：

| Executor | No Memory Avg. SR | Strongest baseline Avg. SR | SkillOS Avg. SR | SkillOS Steps |
|----------|-------------------|-----------------------------|-----------------|---------------|
| Qwen3-8B | 47.9 | ReasoningBank 55.7 | 61.2 | 18.9 |
| Qwen3-32B | 54.5 | SkillOS-gemini 63.6 / ReasoningBank 61.4 | 68.6 | 17.3 |
| Gemini-2.5-Pro | 66.4 | SkillOS-gemini 79.3 | 80.2 | 14.8 |

作者强调，Qwen3-8B curator 训练后甚至超过 Gemini-2.5-Pro 直接做 curator 的 SkillOS-gemini。

这个结果很关键。

它说明 skill curation 不是纯粹的通用推理能力问题，而是一个可以通过 executor-grounded feedback 学到的专门能力。

### 4.4 WebShop 与 Reasoning 主结果

WebShop 和 reasoning 的结果同样支持主张。

| Executor | WebShop No Memory Score | WebShop SkillOS Score | Reasoning No Memory Avg. Acc | Reasoning SkillOS Avg. Acc |
|----------|-------------------------|-----------------------|-------------------------------|----------------------------|
| Qwen3-8B | 33.3 | 40.6 | 69.6 | 73.8 |
| Qwen3-32B | 41.5 | 49.2 | 74.0 | 79.7 |
| Gemini-2.5-Pro | 48.6 | 56.0 | 81.8 | 88.6 |

WebShop 中，SkillOS 不仅分数更高，steps 也更少。

Reasoning 中，SkillOS 在 AIME24、AIME25、GPQA 的平均准确率都有提升。

论文解释说，agentic tasks 的收益通常更大，因为它们有更直接的程序性规律：动作顺序、环境约束、失败恢复、搜索策略等。

推理任务也受益，但可复用内容更抽象，例如分解、验证、约束建模。

### 4.5 泛化实验

SkillOS 的一个重要卖点是 curator 和 executor 解耦。

训练时 executor 是 Qwen3-8B，但测试时可换成 Qwen3-32B 或 Gemini-2.5-Pro。

论文报告：

- ALFWorld 上 Qwen3-8B executor 从 47.9 提升到 61.2。
- ALFWorld 上 Gemini-2.5-Pro executor 从 66.4 提升到 80.2。

这说明训练得到的 curator 不只适配一个固定 executor。

同时，Figure 3 显示跨任务泛化也存在。推理任务训练出的 curator 迁移到 agentic tasks 效果尤其好，因为它学到的 decomposition、verification、adaptive planning 更抽象。

### 4.6 消融实验

论文 Table 3 在 ALFWorld 上做消融：

| 方法 | Avg. SR | Steps |
|------|---------|-------|
| SkillOS-GRPO | 61.2 | 18.9 |
| w/o `r_cnt` | 58.6 | 20.1 |
| w/o `r_comp` | 60.0 | 19.3 |
| w/o grouping | 57.3 | 20.6 |

结论很清楚：

- 内容质量奖励有明显作用。
- 压缩奖励作用较小但稳定。
- 去掉 grouped task streams 下降最大。

这再次说明，SkillOS 的核心不是单个奖励技巧，而是“相关任务成组 + 下游反馈归因”的训练构造。

### 4.7 SkillRepo 演化

论文分析 SkillRepo 的内容演化，发现两个现象。

第一，Markdown section 变得更有执行价值。

早期常出现泛泛的 guidance、tips、recommendations。训练后期更多出现 failure handling、conditional branches、fallback logic。

第二，技能从 task-specific 向 meta-strategy 迁移。

早期技能更像“某个具体物体怎么处理”。

后期技能更多覆盖：

- state verification。
- fallback planning。
- systematic search。
- strategy adjustment。

这很像一个 Agent 从“记案例”进化为“总结方法论”。

### 4.8 技能使用归因

论文 Figure 6 比较 SkillOS-base 和 SkillOS 的技能使用情况。

SkillOS 在 ALFWorld 上：

- 在所有 evaluation examples 上都调用技能。
- 成功技能使用率更高。
- Skill coverage 更大。
- 每个 example 使用的平均技能数更少。

这说明收益不是来自“塞更多技能进上下文”，而是来自更精准地使用更有用的技能。

---

## Step 5 | 历史叙事

### 5.1 从 ReAct 到 Skills

ReAct 把 Agent 执行抽象成 Thought-Action-Observation 循环。

它解决的是“如何一边推理一边行动”。

SkillOS 解决的是下一层问题：

```text
行动完以后，经验如何变成下一轮可复用技能？
```

### 5.2 从 Memory 到 Procedural Memory

早期 Agent memory 常把历史内容当作可检索文本。

这种方式接近 episodic memory：保存过去发生过什么。

SkillOS 更接近 procedural memory：保存以后应该怎么做。

这让它比单纯 case replay 更适合长时间部署。

### 5.3 从手工技能到可训练策展

Anthropic-style Agent Skills 把技能文件标准化为可加载、可组合的能力单元。

但它主要依赖人类编写。

SkillOS 的价值在于提出一个训练 recipe，让 curator 学习如何维护这些技能。

这意味着 `SKILL.md` 风格的文件可能不只是人写给 Agent 的说明书，也可能成为 Agent 自我演化的中间表示。

### 5.4 与 EverAgent 的关系

EverAgent 项目本身也有 AGENTS.md、skills、任务状态、事件日志、wiki ingest。

SkillOS 对这种系统有直接启发：

- 子项目协议类似 skill boundary。
- 报告和 wiki 是外部程序性记忆。
- 任务完成后的 CONTEXT/wiki 更新类似 curation。
- 未来可以让 curator 学习何时新建、合并、删除技能页。

所以这篇论文不仅是理论上的 Agent 研究，也能反照当前仓库的工程治理。

---

## Step 6 | 工程实践

### 6.1 最小复现应该复现什么

完整复现 SkillOS 成本很高。

最小复现不应该试图训练 Qwen3-8B curator，而应该先复现四个接口：

```text
TaskGroup
SkillRepo
AgentExecutor
SkillCurator
```

以及三个操作：

```text
insert
update
delete
```

本次配套在 `ai-practice` 中新增的 `exp_007` 就是这个思路。

### 6.2 真实工程落地架构

一个可落地的 SkillOS-like 系统可以这样拆：

```text
events/trajectories/     保存任务轨迹
skills/                  保存 Markdown 技能
curator/                 读轨迹，生成 skill patch
retriever/               根据任务检索 skills
evaluator/               记录后续任务成功率、步数、人工反馈
```

其中最难的是 evaluator。

没有可靠的下游反馈，就很难判断一个 skill patch 是否真的有价值。

### 6.3 复现坑点

第一，skill 写得越长不一定越好。

论文中的压缩奖励提醒我们：技能应该是轨迹的抽象，而不是轨迹的备份。

第二，judge 不是万能。

内容质量 judge 可以防止胡写，但真正的效用要看 executor 是否用得上。

第三，grouping 不是数据预处理小事。

它决定了 curator 能否在训练中看到“前面操作影响后面结果”的反馈。

第四，curator-executor mismatch 很真实。

强 curator 写出的技能如果超出弱 executor 的能力范围，可能反而不好用。

### 6.4 推荐学习路径

建议按这个顺序学习：

1. 先读 ReAct，理解 Agent 执行循环。
2. 再读 Agent Memory / Skills 相关报告，理解外部记忆形式。
3. 读 SkillOS，理解技能策展为什么要训练。
4. 跑 `ai-practice` 的 exp_007，观察紧凑 SkillRepo 与 raw memory 的差异。
5. 最后尝试把 EverAgent 某个真实任务轨迹转成 SKILL.md patch。

---

## Step 7 | 个人评价

### 7.1 最重要洞察

这篇论文最重要的洞察是：

```text
Agent 自进化的瓶颈不是“有没有经验”，而是“经验能否被策展成适配未来执行的技能”。
```

大多数记忆系统停在存储层。

SkillOS 把问题推进到治理层。

它问的是：

- 什么该留下？
- 什么该合并？
- 什么该删除？
- 什么形式对 executor 最有用？
- 什么反馈能训练这种判断？

这比“给 Agent 加记忆”更接近真实系统长期运行会遇到的问题。

### 7.2 学习优先级

我给它 9/10。

原因：

- 它切中 Agent 长期部署的核心痛点。
- 方法设计清晰，executor/curator 分离很工程化。
- grouped task streams 和 composite reward 有可迁移价值。
- 结果覆盖 ALFWorld、WebShop、reasoning 和多 executor 泛化。

扣分点：

- 完整复现成本很高。
- LLM-as-a-judge 的 content reward 仍有主观性。
- 技能质量和安全边界还需要更多真实部署验证。
- delete 操作在实验中占比小，长期仓库治理能力还有进一步研究空间。

### 7.3 对 EverAgent 的启发

当前 EverAgent 的状态更新和 wiki ingest 已经是人类/Agent 协作式 curation。

SkillOS 提醒我们，后续可以让系统记录：

- 哪些报告模板被多次复用。
- 哪些 AGENTS.md 规则造成失败或返工。
- 哪些 wiki 概念页在后续任务中真正被引用。
- 哪些技能文件长期不用或使用后失败率高。

这些指标可以成为 EverAgent 自身的 skill curation reward。

### 7.4 一句话批判

SkillOS 很强，但它仍然依赖“任务组、judge、成功信号”这三件事的质量；如果真实部署中反馈稀疏、评价噪声大、任务分组错误，curator 学到的可能是漂亮但无效的技能管理习惯。

---

## 知识图谱位置

```text
ReAct / Tool Use
      │
      v
Agent Memory / Procedural Memory
      │
      v
Anthropic-style Skills / SKILL.md
      │
      v
SkillOS: trainable skill curation
      │
      v
Self-evolving Agent systems
```

## 前置知识

读懂本文最好先掌握：

- ReAct：Agent 如何交替推理和行动。
- RAG/BM25：技能如何被检索进上下文。
- RLHF/GRPO：为什么使用组内相对奖励训练策略。
- Agent Skills：Markdown 技能文件如何成为外部能力单元。
- Procedural Memory：为什么技能比原始轨迹更适合复用。

## 延伸阅读

1. Yao et al., `ReAct: Synergizing Reasoning and Acting in Language Models`.
2. Ouyang et al., `ReasoningBank` 相关工作。
3. Anthropic Agent Skills 文档。
4. Shao et al., GRPO / Grouped Reward Policy Optimization 相关论文。
5. `ai-practice/experiments/exp_007_skillos_curator_simulation.md`。

---

## 可复现实验建议

本仓库已同步创建一个小型实验：

```text
ai-practice/src/skillos_curator_simulation.py
ai-practice/experiments/exp_007_skillos_curator_simulation.md
```

运行：

```bash
python3 ai-practice/src/skillos_curator_simulation.py --groups 5 --tasks-per-group 8 --top-k 2 --seed 13 --order grouped
```

它不会复现论文中的 LLM 训练，但可以复现结构性现象：

- grouped task streams 比随机任务更容易产生复用收益。
- raw memory 会膨胀 SkillRepo。
- update/压缩后的技能库可以用更少技能达到类似或更好的效率。
