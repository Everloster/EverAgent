---
title: "生成模型演化全景：GAN → DDPM → Stable Diffusion → DiT"
domain: ai-learning
report_type: knowledge_report
status: complete
updated_on: 2026-04-16
---

# 生成模型演化全景：GAN → DDPM → Stable Diffusion → DiT

> 基于已精读论文：GAN (2014)、DDPM (2020)、Latent Diffusion/Stable Diffusion (2021)、DiT (2022)
> 5层理解模型（L1~L5）+ 演化谱系图

---

## 摘要（≤3 bullets）

- **范式跳跃**：生成模型经历了"对抗博弈（GAN）→ 马尔科夫链去噪（DDPM）→ 潜空间压缩去噪（LDM）→ Transformer骨干（DiT）"四个阶段，每次跳跃都解决了前代的核心缺陷。
- **关键转折**：LDM（Stable Diffusion）将去噪过程从像素空间移至潜空间，使训练计算量降低约50倍，同时引入交叉注意力实现文本条件控制，开启了图文生成的开源生态爆发。
- **架构趋势**：DiT以Scaling Laws驱动的实验证明"Transformer骨干 > U-Net骨干"，为Sora等视频生成系统奠定了架构基础——生成模型骨干正在向统一的Transformer范式靠拢。

---

## L1：是什么——四代生成模型速览

### 概念定义

**生成模型（Generative Model）**：学习数据分布 $p(x)$，能从该分布中采样出新样本的模型。评判标准：生成质量（FID分数）、多样性（recall）、训练稳定性、可控性。

### 四代模型一览表

| 模型 | 论文 | 年份 | 核心机制 | 典型FID（ImageNet 256²） |
|------|------|------|---------|--------------------------|
| **GAN** | Goodfellow et al. | 2014 | 生成器G vs 判别器D 博弈 | BigGAN: ~7（条件） |
| **DDPM** | Ho et al. | 2020 | T步马尔科夫加噪·逆向去噪 | 3.17（无条件） |
| **LDM (SD)** | Rombach et al. | 2021 | 潜空间压缩+去噪+交叉注意力 | 3.60（条件，f=4） |
| **DiT** | Peebles & Xie | 2022 | Transformer取代U-Net骨干 | DiT-XL/2: 2.27 |

> **一句话总结**：每一代生成模型都在回答"上一代的核心问题是什么"，然后用新工具解决它。

---

## L2：怎么工作——核心机制深入

### 2.1 GAN：对抗博弈框架

**问题背景**（2014年）：VAE生成图像模糊，MCMC采样太慢，需要一种无需显式建模 $p(x)$ 的生成方法。

**核心思想**：两个网络相互博弈——

```
生成器 G: z ~ p(z)  →  G(z) ≈ x_real
判别器 D: x → [0,1]，判断真假
```

**目标函数**（minimax博弈）：

$$\min_G \max_D \mathbb{E}_{x \sim p_{data}}[\log D(x)] + \mathbb{E}_{z \sim p_z}[\log(1 - D(G(z)))]$$

**理论结论**（Goodfellow证明）：
- 最优 $D^*(x) = \frac{p_{data}(x)}{p_{data}(x) + p_G(x)}$
- 最优 $G$ 使 $p_G = p_{data}$，等价于最小化JS散度
- 无需马尔科夫链，无需显式似然计算

**致命缺陷**：
1. **训练不稳定**：博弈容易陷入模式崩溃（Mode Collapse）——G只生成少数几种图像欺骗D
2. **梯度消失**：D过强时，G梯度消失；D过弱时，G无法学习
3. **评估困难**：FID、IS等指标与人类感知仍有差距
4. **可控性差**：早期GAN难以精确控制生成内容

---

### 2.2 DDPM：扩散去噪框架

**问题背景**（2020年）：GAN不稳定、VAE模糊、Flow模型参数量爆炸。需要一种训练稳定、生成质量高的生成方法。

**核心思想**：借鉴非平衡热力学——数据可以通过逐步加噪变成纯噪声，模型学习逆向去噪过程。

**前向过程**（固定，无需学习）：

$$q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t} x_{t-1}, \beta_t \mathbf{I})$$

$$q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar{\alpha}_t} x_0, (1-\bar{\alpha}_t)\mathbf{I})$$

其中 $\bar{\alpha}_t = \prod_{s=1}^t (1-\beta_s)$，允许**任意时间步直接加噪**，无需逐步迭代。

**逆向过程**（模型学习）：

$$p_\theta(x_{t-1}|x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t), \Sigma_\theta(x_t, t))$$

**Ho et al. 的关键简化**：不直接预测 $\mu$，而是**预测噪声 $\epsilon$**：

$$L_{simple} = \mathbb{E}_{t, x_0, \epsilon} \left[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\right]$$

这等价于加权负ELBO，权重设为1时（不再重加权）效果最好。

**实验结果**：
- CIFAR-10 FID: **3.17**（无条件，超越BigGAN的9.22）
- T=1000步，骨干网络为U-Net with self-attention

**核心局限**：
1. **采样极慢**：T=1000步逆向，生成一张图需数分钟（GPU）
2. **像素空间昂贵**：直接在高分辨率像素上操作，256×256图像计算成本巨大
3. **条件控制弱**：原始DDPM是无条件生成，文本控制需额外设计

---

### 2.3 LDM（Stable Diffusion）：潜空间压缩

**问题背景**（2021年）：DDPM在像素空间计算量太大，难以扩展到高分辨率；GAN的文本控制虽然有CLIP等工具但架构受限。

**两阶段架构**（核心创新）：

```
阶段1：感知压缩（预训练，冻结）
  图像 x (H×W×3) → 编码器E → z (h×w×c)
  其中 f = H/h = W/w ∈ {4, 8, 16, 32}
  解码器D: z → x̂

阶段2：潜空间扩散（主要训练）
  在 z 空间运行DDPM去噪
  DM: ε_θ(z_t, t, τ_θ(y))
```

**关键参数选择**（论文消融实验结论）：
- $f=4$：FID最优（3.60）vs $f=8$（3.90），但计算增加4倍
- $f=8$：最佳速度-质量权衡，Stable Diffusion实际采用此配置
- $f=32$：信息损失太大，FID显著下降

**交叉注意力条件机制**：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right) \cdot V$$

其中：
- $Q = W_Q \cdot \phi_i(z_t)$（来自图像潜表示）
- $K = W_K \cdot \tau_\theta(y)$，$V = W_V \cdot \tau_\theta(y)$（来自文本/条件编码器）

这使得任意模态（文本、语义图、布局）都可以作为条件，只需替换 $\tau_\theta$。

**计算效率提升**（实测，论文Table 8）：
- LDM-4 vs DDPM（像素空间）：训练速度提升约2.7×，推理速度提升约50×
- 显存占用：从 ~20GB（256²像素DDPM）降至 ~6GB（LDM-4）

**开源生态影响**：
- Stability AI 以LDM为基础发布Stable Diffusion 1.x（2022.8），48小时下载超100万次
- 催生 ControlNet、IP-Adapter、SDXL、SD 3等一系列工作

---

### 2.4 DiT：Transformer取代U-Net

**问题背景**（2022年）：LDM/DDPM的骨干网络U-Net并非为扩散模型设计，其归纳偏置可能限制了Scaling能力。是否可以用Transformer替换U-Net？

**架构设计**：

```
输入: z_t (latent, 32×32×4) → patchify → N个tokens
      t (时间步) + y (类别标签) → 条件向量c

12个DiT块，每块：
  LayerNorm (adaptive, conditioned on c)
  Multi-Head Self-Attention
  LayerNorm (adaptive)
  MLP (pointwise feedforward)

输出: 预测噪声 ε 和对角协方差 Σ
```

**AdaLN-Zero（核心条件机制）**：

```python
# 条件向量c调制LayerNorm参数
scale, shift = MLP(c).chunk(2, dim=-1)
x = LayerNorm(x) * (1 + scale) + shift

# Zero初始化：输出层权重归零，保证训练稳定性
```

实验对比四种条件注入方式：AdaLN-Zero > AdaLN > cross-attn > in-context conditioning

**Scaling实验（核心结论）**：

| 模型规模 | 参数量 | GFLOPs | FID (ImageNet 256²) |
|---------|--------|---------|---------------------|
| DiT-S/2 | 33M | 6.1 | 68.4 |
| DiT-B/2 | 130M | 23 | 43.5 |
| DiT-L/2 | 458M | 80 | 23.3 |
| DiT-XL/2 | 675M | 119 | **2.27** |

**验证了Scaling Laws对生成模型的适用性**：FID与计算量呈幂律关系，U-Net在同等计算下FID更差。

**工程细节**：
- Patch size $p \in \{2, 4, 8\}$：$p=2$最优（更多tokens = 更强表达）但计算量最大
- 训练：AdamW, lr=1e-4, weight decay=0
- 使用预训练VAE（来自Stable Diffusion）作为潜空间编码器

---

## L3：为什么这样设计——设计动机与权衡

### 3.1 GAN vs DDPM：为什么扩散更稳定？

**GAN不稳定的根本原因**：博弈均衡（Nash Equilibrium）在深度网络中难以找到——梯度更新路径不保证收敛到 $p_G = p_{data}$。实践中需要大量调参技巧（spectral norm、gradient penalty、EMA等）。

**DDPM的稳定性来源**：
1. **固定前向过程**：无需学习，消除了博弈的不确定性
2. **简单预测目标**：预测高斯噪声 $\epsilon$ 而非复杂分布，是标准回归问题
3. **时间步平均**：训练时随机采样 $t$，相当于同时训练多个"去噪强度"的模型，天然正则化

**代价**：采样速度。GAN一步生成，DDPM需T=1000步。后续工作（DDIM、DPM-Solver）将步数压缩到50步以下。

### 3.2 像素空间 vs 潜空间：LDM的关键选择

**像素空间的本质问题**：高分辨率图像中大量像素信息是"感知冗余"的——人眼对低频结构的敏感度远超高频细节。在像素空间的每一步去噪都要处理全部信息，包括大量冗余信息。

**LDM的洞察**：将"感知压缩"（去除冗余）和"语义压缩"（学习生成）分离：
- 阶段1 VAE负责感知压缩（可预训练复用）
- 阶段2 扩散模型只需学习语义生成（计算量大幅减少）

**关键权衡**：压缩率 $f$ 越大，计算越省但信息损失越多。论文实验表明 $f=4$~$8$ 是最佳区间——这也解释了为什么Stable Diffusion选择 $f=8$（64×64潜空间对应512×512图像）。

### 3.3 U-Net vs Transformer：DiT的架构选择

**U-Net的归纳偏置**：
- 卷积运算的平移等变性：适合局部纹理学习
- Skip connection跨尺度特征融合：适合多尺度图像处理
- 但：参数共享在大模型时是限制

**Transformer的优势**：
- 自注意力天然建模全局依赖
- Scaling Laws验证充分（语言模型已证明）
- 无归纳偏置约束，参数利用率随规模提升

**DiT的赌注**：既然LDM已经将扩散过程压缩到低维潜空间（32×32），patch化后的token数量（N=256，patch=2）与语言模型的序列长度相当，Transformer处理此规模完全可行。实验结果验证了这个赌注——DiT-XL/2以FID 2.27证明Transformer骨干优于U-Net。

---

## L4：与什么相关——知识网络

### 4.1 与其他生成模型的关系

```
生成模型家族树
├── 显式密度估计
│   ├── 自回归模型 (AR): GPT, PixelRNN, VQVAE-2
│   └── 标准化流 (Flow): GLOW, RealNVP
├── 隐式密度估计
│   └── GAN → BigGAN → StyleGAN2 → GigaGAN
└── 混合/扩散
    ├── VAE → VQVAE → DALL·E 1
    └── 扩散模型
        ├── NCSN (score matching) → DDPM
        ├── DDPM → DDIM (加速) → DPM-Solver (ODE加速)
        ├── DDPM → LDM (潜空间) → Stable Diffusion 1/2/3
        └── LDM → DiT → Sora (时空DiT)
```

### 4.2 与视觉基础模型的关系

- **CLIP**（#12）：Stable Diffusion使用CLIP文本编码器作为 $\tau_\theta$，提供文本条件
- **ViT**（#11）：DiT直接沿用ViT的patchify + Transformer块设计
- **MAE**（#17）：同样是Transformer骨干的视觉模型，与DiT在架构理念上高度相似

### 4.3 与Scaling Laws的关系

- DDPM: 无显式Scaling实验，但T=1000步的设计隐含计算量预留
- DiT: 明确验证生成模型的Scaling Laws，FID ~ GFLOPs^(-α)，与语言模型的loss ~ compute^(-α) 高度类似
- **影响**：Sora(2024)团队在DiT框架基础上引入时空patch，将视频生成建模为"时空token序列的扩散去噪"——Scaling Laws在生成领域得到完全确认

### 4.4 与下游应用的关系

| 下游技术 | 依赖的生成模型组件 |
|---------|-----------------|
| ControlNet | Stable Diffusion骨干 + 条件注入扩展 |
| IP-Adapter | LDM的交叉注意力机制 |
| DreamBooth / LoRA | SD微调框架 |
| SDXL / SD3 | DiT架构（SD3完全采用DiT骨干） |
| Sora | 时空DiT（Video DiT）|
| Flux.1 | DiT + 流匹配（Flow Matching）|

---

## L5：前沿与争议

### 5.1 当前最优性能（截至2026年初）

**文生图**：
- Flux.1 Pro（Black Forest Labs，2024）: 目前质量/效率最优的开源/商用模型之一
- Stable Diffusion 3 Medium: 采用完整DiT + 流匹配（Rectified Flow）
- DALL·E 3（OpenAI）: 同样基于DiT骨干，侧重文本一致性

**文生视频**：
- Sora（OpenAI，2024）: 时空DiT，最长60秒，1080p
- Wan2.1（万象，2025）: 开源视频DiT，IDDPM + 时空注意力

### 5.2 核心开放问题

**1. 采样效率**：DDPM的1000步已被DDIM(50步)、DPM-Solver(20步)、Flow Matching(1步)大幅压缩，但"一步高质量采样"仍是研究热点（Consistency Models、LCM等）。

**2. 训练数据问题**：
- LAION-5B（Stable Diffusion数据源）包含大量版权内容，已有多起诉讼
- 数据质量 vs 数据规模的权衡（参见RefinedWeb的Web数据过滤策略）

**3. 评估指标争议**：FID依赖Inception网络特征，不能完全反映人类审美偏好。目前转向人类评分（ELO）或多模态奖励模型评估。

**4. 可控性边界**：即使有ControlNet、LoRA等工具，精确的"像素级控制"仍然困难，尤其是手部细节、文字渲染。

**5. 统一架构的胜利**：DiT→Sora的路径表明，Transformer骨干正在统一视觉生成领域，就像它统一了NLP一样。但是否存在"最优patch size"或"最优latent space维度"，理论解释仍不充分。

### 5.3 Flow Matching：扩散模型的下一步？

**Rectified Flow（Liu et al., 2022）** 和 **Flow Matching（Lipman et al., 2022）** 提出直线化的常微分方程（ODE）路径：从噪声到数据走"直线"而非DDPM的"曲线"。

**优势**：
- 更少步数（理论上1步可行）
- 更稳定的训练目标
- Stable Diffusion 3、Flux.1已采用流匹配替代DDPM

**影响**：Flow Matching正在成为新一代扩散模型的标准，DDPM可能逐渐让位给这一更简洁的框架。

---

## 演化谱系图

```
2014 GAN ─────────────────────────────────────────────────────────────►
  ↓ 模式崩溃、训练不稳定
2020 DDPM ──────────────────────────────────────────────────────────────►
  ↓ 像素空间计算昂贵、无条件控制
2021 LDM (Stable Diffusion) ─────────────────────────────────────────────►
  ↓ U-Net骨干Scaling受限
2022 DiT ────────────────────────────────────────────────────────────────►
  ↓ 步数多、Flow Matching更优
2022+ Flow Matching (Flux.1 / SD3) ────────────────────────────────────►
  ↓ 视频生成
2024 Sora / Wan2.1 (Video DiT) ─────────────────────────────────────────►
```

---

## 知识关联

**本报告整合以下已精读论文**：
- `08_gan_2014` — GAN原始论文
- `09_ddpm_2020` — DDPM扩散模型
- `20_stable_diffusion_2021` — Latent Diffusion Model
- `27_dit_2022` — Diffusion Transformer

**相关知识报告**：
- `self_attention_深度解析` — Transformer注意力机制（DiT基础）
- `Scaling_Laws_深度解析` — 验证DiT Scaling结论的理论框架
- `RLHF_深度解析` — 生成模型质量对齐的后训练方法

**延伸阅读建议**：
1. DDIM (Song et al., 2020) — DDPM的确定性采样加速
2. Consistency Models (Song et al., 2023) — 一步生成蒸馏
3. Rectified Flow (Liu et al., 2022) — Flow Matching理论基础

---

*报告生成：NeuronAgent / Claude Sonnet 4.6 | 2026-04-16*
