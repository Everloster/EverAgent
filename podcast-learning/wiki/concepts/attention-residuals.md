# Attention Residuals（AttnRes）

> 概念 · 首次出现：2026-08-04（晚点聊177）/ 2026-08-26（张小珺152）

## 定义

把 attention"旋转 90 度"到**层间**：每层一个可学习 **pseudo query**（所有 token 共享），与各深度表示匹配后经 softmax 决定从哪些浅层读取——取代固定的残差累积，让深层**选择性**聚合此前层表示。K3 用于重构深度方向信息流（[[kimi-k3|K3]] 的"depth 维 scaling"）。

## 谱系（连接方式演化）

ResNet（两版本；恺明时代已论 LN 与稳定性）→ Post-LN 因梯度消失被 Pre-LN 取代 → **DenseNet**（黄高：深层聚合所有浅层；孙宇涛选其为创新性最强之一）→ Hyper-Connections（字节 Seed：在 residual 分支上用比 hidden state 更大的容量表示推理深度状态；论文太抽象没出圈）→ **AttnRes**（把 DenseNet 的 heavyweight 聚合换成 lightweight attention）

## 关键性质

- **Pre-LN 的超集**（可退化回 Pre-LN）——否则触及 Post-LN 旧问题，大 run 不敢上
- 对推理**近乎免费**——一切"推理更慢换更好效果"的设计都会被质疑"为什么不直接扩 size"，残差类改进无此问题
- 块状实现：Block Attention Residuals（块内汇总+块间 attention，类似稀疏注意力）
- 论文 3 个一作、2026 春发布、马斯克转发、**杨植麟拍板直接进 K3 而非下一代**

## 与 mHC 对偶

| | mHC（DeepSeek V4） | AttnRes（K3） |
|---|---|---|
| 机制 | 多条 residual stream 递归压缩传递 | 深度方向的下三角 attention map，跨层直读 |
| 像什么 | 层方向的 RNN/线性注意力 | 深度方向的 attention |
| 表达力 | 受压缩传递限制 | 上限更高 |

K3 与 V4 分别证明两条路线都能 scale 到 frontier——层间信息流问题没有唯一解。

## 引用本概念的报告

- [[2026-08-26_xiaoyuzhou-zhangxiaojun_kimi-k3-report]]、[[2026-08-04_rss-wandian-latetalk_kimi-k3]]、[[2026-09-02_multi_kimi-k3-dueling-reads]]
