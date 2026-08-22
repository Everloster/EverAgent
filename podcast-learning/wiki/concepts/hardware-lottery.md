# Hardware Lottery（硬件彩票 / 系统彩票）

> 概念 · 首次出现：2026-07-28（Vol.148 游凯超访谈）
> 概念出处：Sara Hooker《The Hardware Lottery》(2020)；嘉宾在访谈中澄清非 David Patterson 所写

## 定义

一个算法能否胜出，取决于它能否被当时的硬件/系统**高效实现**，而非仅取决于算法本身的优劣。抽中彩票者吃尽时代红利；抽不中的即使概念上 make sense 也难以存活。

## 例证（访谈）

- **正例**：Transformer 抽中了 GPU 的彩票（大量矩阵乘法、适合并行）
- **反例**：Hinton 强推的 Capsule Network——概念合理但 GPU 不友好，至今未广泛应用
- **FlashAttention 清场**：它证明精确的 softmax attention 可以被高效实现，此前所有近似 softmax 的研究路线作废
- **autoregressive decoding 翻身**：曾被判「逐 token 太慢没用」，continuous batching + PagedAttention + speculative decoding 把成本打下来
- **linear attention**：Mamba2 的 chunk parallel 让分段计算高效可行，该路线才成立

## 推论（嘉宾）

- 摩尔定律黄金时代软硬件可各自为战；专用算力时代算法必须主动适配硬件，硬件公司则需不断押注下一代形态
- 方法论：「通过第一性原理去看清楚时代发展的主线，然后屏蔽噪音，持续在一个有用的方向投入」

## 引用

- [[2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao|对游凯超3小时访谈]]（Vol.148）
