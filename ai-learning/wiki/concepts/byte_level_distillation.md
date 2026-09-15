# 字节级蒸馏（Byte-Level Distillation）

> 概念实体 · 首次引入：2026-09-11（Marathe & Pagnoni et al.《Breaking the Token Ceiling》，arXiv:2609.12303）

## 一句话定义

把蒸馏的学习单位从 token 换成字节：教师的 token 概率分布经**单次前向**转换到字节级——近似版 **Marginalize-It**（前缀聚合+重归一化，丢弃已结束 token 的概率）与精确版 **End-Of-Token**（词表加 <eot> 吸收悬空概率，代价是每 token 训练算力 +30.94%）。

## 核心结论（~1.28B 学生，约万亿字节过度训练）

- 缩放律外推天花板：EOT 蒸馏 52.4% > Bytes 监督 51.2% > MI 蒸馏 50.5% > Token 蒸馏 48.4%（6 benchmark 平均，LR=4e-3）
- Token 模型低算力占优但早饱和；字节模型起步慢、斜率陡、终盘反超
- 效率：1/6 训练文本追平、1/5 logit 存储（小词表免 top-600 截断）
- **警示**：全部为外推；实测最大 checkpoint（44.6%）仍未超 Llama-3.2-1B（45.9）/Gemma-2B（50.3）；换验证集追平点移动 27 倍；推理成本比较未做

## 谱系位置

- 前作谱系：ByT5 → MegaByte → CANINE → **BLT**（本文一作 Pagnoni 即 BLT 作者）→ H-Net / EvaByte
- 直接前作：Hayase 2025 / Phan 2024（精确转换但需多次教师前向）；微调阶段转换：Bolmo（Minixhofer 2025）
- 与 [[knowledge_distillation]] 的关系：字节化把"top-k 截断存储"这一离线蒸馏暗伤直接消除
- 来源报告：[[47_byte_distillation_2026]]
