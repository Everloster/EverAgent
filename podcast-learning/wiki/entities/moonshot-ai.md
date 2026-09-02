# 月之暗面（Moonshot AI / Kimi）

> 机构实体 · 首次深度出现：2026-09-02（K3 双期对照处理）

## 身份

- 中国大模型公司，创始人**杨植麟**（口头禅"有概率的非共识"——解释 K3 敢把激活提到 104B）、联合创始人**周昕宇**（K3 定版后朋友圈"Have faith in scaling and RL"）
- 模型谱系：Kimi K1.5（partial rollout）→ K2（1T/32.6B，MuonClip 贡献业界）→ K2.5（reasoning-effort budget control、Agentic GRM）→ **K3（2.8T/104B，2026-07-16 官宣、07-27 权重+47 页报告全量开源，首个 3T 级开放权重模型）**；Kimi Linear（约 48B）为 K3 架构前身
- 核心研究员：苏剑林（RoPE 原始提出者、Quantile Balancing 博客）

## 方法论标签

- **"模型内科"**（孙宇涛概括）：让行为 trace 可靠获取、让不稳定/collapse 可明确归因；"不科学＝出于利益把 ablation、变量控制干掉"
- **"用 infra 换算力"**（晚点聊嘉宾评）：MoonEP、Flash KDA、FP8 offload、QAT 训推一致——中国公司缺算力把效率压到极致
- K3 战略：提升**开源能力上限**（API 显著更贵 $3/$15），与 DeepSeek-V4 的性价比路线（Flash 档 $0.44）形成分化
- 未开放的部分（护城河）：自我演化知识图谱任务系统、MOPD 原始专家 checkpoint——"开源了权重，没开源产生权重的流水线"

## 架构遗产（K3）

见 [[kimi-k3]]、[[kda-linear-attention]]、[[quantile-balancing]]、[[attention-residuals]]、[[mopd]]、[[kernel-development-agent]]

## 引用本实体的报告

- [[2026-08-26_xiaoyuzhou-zhangxiaojun_kimi-k3-report|张小珺152 领读 K3 技术报告]]
- [[2026-08-04_rss-wandian-latetalk_kimi-k3|晚点聊177 详解 Kimi K3]]
- [[2026-09-02_multi_kimi-k3-dueling-reads|K3 一鱼两吃对照]]
