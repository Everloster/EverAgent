# MOPD（多教师 On-Policy 蒸馏）

> 概念 · 首次出现：2026-08-04（晚点聊177）/ 2026-08-26（张小珺152）

## 定义

**Multi-Teacher On-Policy Distillation**：先分别训练多个领域专家模型，再将其能力通过 on-policy 蒸馏合入统一学生模型（"合板"）。K3 结构：**9 个专家 = 3 域（general/agentic/coding）× 3 档推理努力度（low/high/max）**（对照报告核验；"九个领域专家"是不精确说法）。

## 动机：解耦（晚点聊的工程组织视角）

各领域的 data/environment/reward/rollout 长度/harness/recipe 都不同——joint 大 RL run 合板时耦合压力巨大；MOPD 让各小团队只需交付自己领域的专家模型。公开采用者：MiMo V2、DeepSeek V4、NVIDIA Nemotron 3 Ultra、K3。

**为何不写论文**：无法抽象成 clean 研究问题（避开麻烦路径而非打败某基线）；Frontier 圈内 credit 不依赖公开发表。

## 学术源头（张小珺期的谱系）

**MiniLLM**（顾宇轩，微软研究院）：Reverse KL、学生自己生成、教师逐步 verify/纠正——"老师讲课 vs 自己做题老师批改"，后被 Thinking Machine Lab 命名为 on-policy distillation。

## on-policy vs off-policy 蒸馏

- on-policy：学生自生成轨迹、教师打分提供稠密奖励——合板时更好
- off-policy：学生模仿教师预先生成的数据——拿不到教师权重/logits 时只能如此（如蒸馏闭源模型）
- 业界已从"大蒸小"变为"**自己蒸馏自己**"：一半动机是 post-train 团队管理（专项 RL 模型合并难、异构 reward 一锅烩难；数据高度异构而模型高度同构，多教师合并容易得多）——非 K3 首创，是 widely accepted 做法
- "自己蒸自己原地飞升"仍是愿景，关键在 scalable 的外在监督信号

## 引用本概念的报告

- [[2026-08-26_xiaoyuzhou-zhangxiaojun_kimi-k3-report]]、[[2026-08-04_rss-wandian-latetalk_kimi-k3]]、[[2026-09-02_multi_kimi-k3-dueling-reads]]
