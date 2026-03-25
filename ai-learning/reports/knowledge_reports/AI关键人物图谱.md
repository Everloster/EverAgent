---
title: "AI关键人物图谱"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-03-23"
---
# AI 关键人物图谱：追踪那些改变世界的研究者

> 技术史不只是算法的历史，更是人的历史。
> 理解"谁在哪里做了什么，后来去了哪里"，能帮助你理解 AI 领域的权力结构、研究文化和未来走向。
> 更新日期：2026-03-23

---

## 一、Transformer 的八位作者：一篇论文的命运发散

2017年，Google 的8位工程师联合发表了《Attention Is All You Need》，这可能是 AI 史上影响力最大的一篇论文。但他们随后各奔东西，成为整个 AI 行业格局的缩影。

```
Attention Is All You Need（2017）
           │
    ┌──────┴──────────────────────────────────────┐
    │                                              │
Noam Shazeer                            Ashish Vaswani
  Google Brain → Character.AI              Google → Adept AI（后回Google）
  联合创始人/CEO                            联合创始人（后离开）
  LaMDA/Bard 早期贡献者
    │
Niki Parmar, Jakob Uszkoreit            Llion Jones
  → Adept AI（联合创始人）                  → Sakana AI（2023，与 David Ha 共创）
                                           "AI 模型的进化" 研究
    │
Aidan Gomez                             Łukasz Kaiser
  → Cohere（CEO/联合创始人，2019）           → OpenAI（2019）
  企业 LLM 领域代表公司                     后离开，回 Google Research
    │
Illia Polosukhin                        David Ha（非作者但相关）
  → NEAR Protocol（区块链+AI）              → Stability AI（研究总监）
  将 Transformer 带入 Web3 领域             → Sakana AI（联合创始人，2023）
```

### 解读：为什么8人跑了7家公司？

Transformer 的成功让每位作者都成为了炙手可热的"建国功臣"。Google 提供了研究环境，但无法给予创业公司能给的股权激励和自由度。**这是 AI 人才从大公司流向创业公司的经典模式**——核心技术突破往往发生在大公司，但商业化往往由前员工的创业公司来完成。

---

## 二、OpenAI 的分裂：Anthropic 的诞生

这是 AI 史上最重要的一次机构分裂，直接塑造了当前的两强格局。

```
OpenAI（成立2015）
       │
       ├── Dario Amuodei（研究VP）
       ├── Daniela Amuodei（运营VP）
       ├── Tom Brown（GPT-3 第一作者）
       ├── Chris Olah（可解释性研究）
       ├── Sam McCandlish
       ├── Jack Clark
       └── 其他约7人

       2021年，因与 OpenAI 的安全方向和商业化路径产生分歧

       ▼ 集体离职，创立 Anthropic

Anthropic（2021成立）
       │
       ├── Dario Amuodei → CEO
       ├── Daniela Amuodei → 总裁
       ├── Chris Olah → 可解释性核心（Circuit 系列研究）
       ├── Tom Brown → 早期研究
       └── Constitutional AI, Claude 系列
```

### 解读：安全 vs 速度的根本分歧

离开的核心原因据报道是：Dario 等人认为 OpenAI 在追求商业化的路上，对 AI 安全的重视程度不够。他们希望建立一家"安全研究优先"的公司。

**结果**：OpenAI 推出了 ChatGPT（2022），引爆 AI 热潮；Anthropic 推出了 Claude，以"Constitutional AI"和更强的安全性著称。两家公司代表了 AI 发展的两种哲学——快速商业化 vs 审慎对齐研究。

---

## 三、Google Brain × DeepMind 合并：Google 的战略重组

```
Google Brain（2011成立，Jeff Dean、Greg Corrado、Andrew Ng）
     +
DeepMind（2010成立，Demis Hassabis，2014被Google收购）
     │
     │ 2023年4月合并
     ▼
Google DeepMind
     │
     ├── Demis Hassabis → CEO
     ├── 继续 AlphaFold、Gemini 系列
     └── 成为对抗 OpenAI+Anthropic 的主力

```

### 关键人物轨迹

**Jeff Dean**（Google Brain 灵魂人物）
- 设计了 Google 的 TPU 架构
- 推动了 Google Brain 的成立
- 合并后任 Chief Scientist，Google DeepMind

**Demis Hassabis**（DeepMind CEO）
- 游戏开发者出身（《主题医院》设计者）
- 神经科学 PhD → 创立 DeepMind
- AlphaGo → AlphaFold → Gemini，三次里程碑
- 2024年诺贝尔化学奖（AlphaFold蛋白质结构预测）

**Oriol Vinyals**（DeepMind）
- 序列到序列（Seq2Seq）模型的提出者
- AlphaStar（星际争霸AI）核心
- 参与 Gemini 多模态研究

---

## 四、Hinton / LeCun / Bengio：深度学习三巨头的分道扬镳

```
深度学习三巨头（共同获得2018年图灵奖）
       │
       ├── Geoffrey Hinton（多伦多大学）
       │     ├── 深度信念网络（2006）
       │     ├── Dropout 发明者
       │     ├── 2012年 AlexNet 学生（Krizhevsky）
       │     ├── 2013年加入 Google（DNNresearch）
       │     ├── 2023年离开 Google，警告 AI 风险
       │     └── 立场：对 AI 存在风险持严肃态度，呼吁监管
       │
       ├── Yann LeCun（纽约大学/Meta AI）
       │     ├── CNN/LeNet 发明者（1989）
       │     ├── 2013年加入 Facebook，创立 FAIR
       │     ├── 现任 Meta AI 首席科学家
       │     └── 立场：认为 LLM 不是通往 AGI 的路，倡导 "World Model"
       │
       └── Yoshua Bengio（蒙特利尔大学/Mila）
             ├── 序列模型、注意力机制早期贡献
             ├── 成立 Mila（蒙特利尔学习算法研究所）
             ├── 不加入大公司，坚守学术
             └── 立场：关注 AI 安全，与 Hinton 立场接近
```

### 三人分歧的本质

- **LeCun**：认为自回归 LLM 是"过时的"，世界模型才是未来，对当前 AI 恐慌论持保留态度
- **Hinton**：从 "LLM 只是模式匹配" 的怀疑者，转变为对 AI 风险高度警惕的警示者
- **Bengio**：学术独立，早期就关注对齐问题，在政策层面积极发声

**这三种立场恰好代表了整个领域对 AI 未来的三种主要态度**。

---

## 五、Sam Altman vs Elon Musk：OpenAI 的另一场分裂

```
OpenAI 创始团队（2015）
       │
       ├── Elon Musk（联合创始人，早期最大赞助商）
       │     └── 2018年离开董事会
       │           原因：与 Sam Altman 在公司方向上存在分歧
       │           后续：2023年成立 xAI，发布 Grok 系列
       │
       └── Sam Altman（CEO）
             ├── 2019年引入微软投资（10亿→100亿→百亿级）
             ├── ChatGPT → GPT-4 → o1 系列
             ├── 2023年11月被董事会短暂解雇（5天后复职）
             └── 2024年出走风波：多名高管离职
                   Greg Brockman（总裁，暂休）
                   Ilya Sutskever（离职，成立 SSI 安全超智能公司）
                   Mira Murati（CTO，2024年离职）
```

### Ilya Sutskever 的关键角色

Ilya Sutskever（AlexNet 作者之一，OpenAI 首席科学家）是这场风波的核心人物：
- 参与了2023年11月投票驱逐 Sam Altman 的董事会决定
- 后公开表示后悔
- 2024年离开 OpenAI，创立 **Safe Superintelligence Inc. (SSI)**
- 立场：认为 AGI 安全是当前最重要的事

---

## 六、中国 AI 的关键人物

```
李飞飞（Stanford / Google Cloud）
  ├── ImageNet 创始人（奠定 CV 基准）
  ├── Stanford AI Lab 主任
  └── 2017-2018 在 Google Cloud 任 VP，后回学术

何恺明（MSRA → Facebook FAIR → MIT）
  ├── ResNet（2015）第一作者
  ├── Mask R-CNN 等 CV 经典架构
  └── 2023年离开 Meta，加入 MIT 任教

谢赛宁（UC Berkeley → Meta FAIR / NYU）
  ├── Vision Transformer（ViT）共同作者
  ├── DiT（扩散 Transformer，Sora 基础）
  └── 现任 NYU 助理教授 + Meta 顾问

梁文锋（DeepSeek 创始人，幻方量化创始人）
  ├── 量化私募背景，拥有大量 GPU 资源
  ├── 2024年 DeepSeek-R1 震动 AI 界
  └── 以极低成本实现接近 o1 的推理能力，引发算力军备竞赛反思
```

---

## 七、人才流动的宏观规律

### 规律1：大公司孵化，创业公司收割
Google / Facebook 投入大量资源做基础研究，但关键研究者往往会创业将其商业化。
**典型路径**：大公司研究员 → 发论文 → 被挖角或自己创业 → 新一轮融资 → 再次被大公司收购

### 规律2：安全分歧是最常见的离职原因
OpenAI → Anthropic，以及多位高管的离职，核心矛盾几乎都是"商业化速度 vs AI 安全"的价值观冲突。

### 规律3：学术 vs 工业的选择越来越难
LeCun 和 Bengio 代表了坚守学术的路径，但薪酬差距导致 AI 学术界人才持续流失。

### 规律4：地理集聚效应
- 湾区（San Francisco/Bay Area）：OpenAI, Anthropic, Google DeepMind
- 纽约：Meta AI (FAIR), NYU
- 蒙特利尔：Mila, Element AI（后被ServiceNow收购）
- 北京/杭州/深圳：智谱AI, 百川智能, DeepSeek, 阿里通义

---

## 八、人物关系网络图（文字版）

```
Hinton ──培养──► Krizhevsky（AlexNet）──► Sutskever（OpenAI 联创）
  │                                              │
  │                                    ──► Sam Altman（OpenAI CEO）
  │                                              │
  └──培养──► Radford（GPT系列作者）              │
                                        ──► Dario Amuodei（Anthropic）
Vaswani                                         │
  │                                    ──► Chris Olah（可解释性）
  ├──► Gomez → Cohere
  ├──► Shazeer → Character.AI          Demis Hassabis
  ├──► Parmar/Uszkoreit → Adept AI      ├──► AlphaGo / AlphaFold
  └──► Jones → Sakana AI               └──► Google DeepMind CEO

LeCun ──► FAIR（Meta AI）──► 何恺明 → MIT
Bengio ──► Mila ──► 大量加拿大 AI 人才输出
```

---

## 九、推荐延伸阅读

- **书籍**：《The Coming Wave》（Mustafa Suleyman，DeepMind 联创）
- **播客**：Lex Fridman Podcast（对谈多位上述人物）
- **文章**：《The Man of Many Fathers》（关于 Transformer 归属权争议）
- **文档**：OpenAI 2023年11月董事会事件时间线（多家媒体报道）

---

> **学习建议**：了解这些人物背景，有助于理解论文背后的研究文化。
> 当你读 InstructGPT 时，知道 Dario 两年后离开创立 Anthropic；
> 当你读 ResNet 时，知道何恺明后来去了 Meta 又回到学术——这些不只是花边，而是理解 AI 生态的线索。

