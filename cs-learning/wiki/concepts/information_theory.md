---
id: concept-information_theory
title: "信息论（Information Theory）"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [02_shannon_1948, CS关键人物图谱]
status: active
---

# 信息论

## 一句话定义
Shannon 1948 年《A Mathematical Theory of Communication》提出的理论：用概率论刻画"信息"这一抽象量，为通信、压缩、纠错码、密码学奠定数学基础。

## 核心概念

### 信息熵 H
对一个离散随机变量 X，其信息熵定义为：

```
H(X) = -Σ p(x) · log₂ p(x)
```

- 单位：bit（log 底为 2）
- 直觉：H(X) 是描述 X 所需的**平均最少比特数**
- 极值：等概率分布时 H 最大（log n），确定分布时 H = 0

来源：02_shannon_1948 / CS关键人物图谱 §Shannon

### 源编码定理（Source Coding Theorem）
任何无损压缩的平均码长 ≥ 信息熵 H(X)。这给出**压缩的理论下限**——ZIP / Huffman / 算术编码都在逼近这个下限。来源：02_shannon_1948

### 信道容量 C（Channel Capacity）
对一条有噪信道，存在最大可靠传输速率 C。在 R < C 时，存在编码方案使错误率任意小；在 R > C 时，错误率不可避免。

**Shannon-Hartley 定理**（高斯信道下）：
```
C = B · log₂(1 + S/N)
```
其中 B 为带宽，S/N 为信噪比。来源：02_shannon_1948

### 互信息 I(X; Y)
衡量两个随机变量的相互依赖程度：
```
I(X; Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)
```
- I = 0 ⟺ X 与 Y 独立
- I 是 KL 散度的对称化

## 历史地位
- Shannon 1937 年硕士论文用布尔代数分析继电器电路，被誉为"历史上最重要的硕士论文"
- 1948 年的信息论论文奠定了通信、压缩、密码学的共同数学基础
- 信息论的工具后来渗透到生物学（DNA 信息含量）、神经科学、统计物理（最大熵原理）等领域

来源：CS关键人物图谱 §Shannon

## 工程影响

| 领域 | 应用 |
|------|------|
| **数据压缩** | Huffman / 算术编码 / DEFLATE（ZIP）/ Brotli |
| **纠错码** | Hamming / Reed-Solomon / LDPC / Turbo / Polar Codes |
| **密码学** | 完美保密性（One-Time Pad 的信息论证明） |
| **机器学习** | 交叉熵损失 / KL 散度 / 互信息最大化 / 决策树熵增益 |
| **通信** | 5G/6G 信道编码逼近 Shannon 极限 |

来源：CS关键人物图谱 §Shannon

## 在本项目的相关报告
- [02_shannon_1948](../../reports/paper_analyses/02_shannon_1948.md)
- [CS 关键人物图谱](../../reports/knowledge_reports/CS关键人物图谱.md)

## 跨域连接
- [computation_theory](./computation_theory.md)：与图灵的计算理论同为 1940s 末的两大基础工作
- ai-learning 的 KL/交叉熵损失：信息论在 ML 损失函数中的直接应用

## 被引用于
- [computation_theory](./computation_theory.md)
- [tcp_ip](./tcp_ip.md)
- [distributed_messaging](./distributed_messaging.md)
- entities/[shannon_claude](../entities/shannon_claude.md)

## 开放问题
- 量子信息论中熵与互信息的扩展（von Neumann 熵）
- 算法信息论（Kolmogorov 复杂度）与 Shannon 信息论的统一边界
