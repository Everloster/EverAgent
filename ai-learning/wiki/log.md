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

<!-- 后续 ingest / query-archive / lint 在此追加 -->
