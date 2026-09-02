# Quantile Balancing（QB，分位数均衡）

> 概念 · 首次出现：2026-08-26（张小珺152）/ 2026-08-04（晚点聊177）

## 定义

K3 的 MoE 专家负载均衡：**利用 router 分数分布的分位数一步算出每个专家的 bias**，使约 16/896 比例的 token 选中每个专家（第 17 名分数作入选门槛），免去辅助 loss 与固定步长超参。出处：苏剑林（科学空间）博客《MoE 环游记 6：最优分配促均衡》——**无论文**。

## 三代演进（晚点聊框架）

1. **auxiliary loss**：质量-均衡权衡、训练不稳定罪魁
2. **loss-free routing**（DeepSeek V3 固定步长 bias update）：只知过热过冷不知量；更新 ad hoc、无收敛标准；底层不 work 迫使大家把前几层改 dense
3. **Quantile Balancing**：线性规划/最优分配一步推导 bias——免调参、第一层可直接 MoE（前几层 dense 并非 ground truth，是 loss-free 语境下的权宜）

## 细节与工程

- bias 不在当前 step 用而下一步用——避免 token 间信息泄露
- 单 batch 4M～几十 M token 无法精确求分位数：博客方案是各 GPU 算局部分位数再 pooling；K3 用**值域切桶 histogram** 统计（常数级存储，嘉宾自述"有可能是我理解错"）
- 苏剑林立场：QB 与 loss-free 在正常情况下可推出数学等价形式

## 为什么重要

896 选 16 的极端稀疏下稳定均衡——嘉宾猜想是 scale 到 3T 的关键之一；"用分位数直接估 bias"的思路可推广到其他路由/资源分配问题（open question）。

## 引用本概念的报告

- [[2026-08-26_xiaoyuzhou-zhangxiaojun_kimi-k3-report]]、[[2026-08-04_rss-wandian-latetalk_kimi-k3]]、[[2026-09-02_multi_kimi-k3-dueling-reads]]
