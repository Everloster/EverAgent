# AI 关键人物与机构演变

## Transformer 八位作者的命运

2017 年《Attention Is All You Need》发表后，8 位 Google 工程师各奔东西：

### 核心贡献者

**Ashish Vaswani**
- 论文首轮讲述者
- Google Brain → Adept AI（联合创始人）→ 后离职
- 角色：架构核心设计

**Noam Shazeer**
- Google Brain → Character.AI（联合创始人/CEO）
- LaMDA/Bard 早期核心
- 现今：聊天机器人领域代表人物

**Niki Parmar & Jakob Uszkoreit**
- Google Brain → Adept AI（联合创始人）
- 角色：实现与优化

**Llion Jones**
- Google → Sakana AI（2023，与 David Ha 共创）
- 研究方向："AI 模型的进化"

**Aidan N. Gomez**
- Google → Cohere（CEO/联合创始人，2019）
- 企业 LLM 领域代表公司
- Cohere 融资数亿美元

**Łukasz Kaiser**
- Google → OpenAI（2019）
- 后离开，回 Google Research

**Illia Polosukhin**
- Google → NEAR Protocol（区块链+AI）
- 将 Transformer 带入 Web3

### 解读
**为什么跑了 7 家公司？** Transformer 的成功让每位作者都成为"建国功臣"，但 Google 的激励体系无法比肩创业公司的股权和自由度。这是**大公司研究成果向创业公司转化**的经典路径。

---

## OpenAI 的机构分裂：Anthropic 的诞生

### 2021 年关键离职

OpenAI 的核心安全研究团队**集体离职**，创立 Anthropic：

**关键人物**：
- **Dario Amodei**（CEO）：OpenAI 研究 VP，GPT-3 领导者
- **Daniela Amodei**（总裁）：OpenAI 运营 VP
- **Tom Brown**：GPT-3 第一作者
- **Chris Olah**：可解释性研究专家（Circuit 系列）
- **Sam McCandlish**、**Jack Clark** 等约 7 人

**离职核心原因**：对 OpenAI 在 AI 安全方向的重视程度不满，认为**商业化速度优先于安全研究**。

### 结果
- **OpenAI**：追求快速商业化 → ChatGPT（2022）→ 引爆 AI 热潮
- **Anthropic**：安全优先 → Claude（Constitutional AI）→ 以对齐和安全著称

**时代意义**：代表了 AI 发展的**两种哲学对立**——快速商业化 vs 审慎安全。两家公司的竞争定义了 2023-2026 年的 AI 产业格局。

---

## Google 战略重组：Brain vs DeepMind

### 2023 年 4 月合并

```
Google Brain（2011，Jeff Dean / Greg Corrado / Andrew Ng）
        +
DeepMind（2010，Demis Hassabis，2014被收购）
        ↓
Google DeepMind（2023-至今）
  CEO：Demis Hassabis
  目标：对抗 OpenAI + Anthropic
```

### 关键人物

**Demis Hassabis（Google DeepMind CEO）**
- 背景：游戏开发（《主题医院》）→ 神经科学博士
- 创立 DeepMind 后连续突破：AlphaGo → AlphaFold → Gemini
- 2024 年诺贝尔化学奖（AlphaFold 蛋白质结构预测）
- 使 DeepMind 成为**生物计算领域**的标杆

**Jeff Dean（Chief Scientist）**
- Google 基础设施设计者，TPU 架构设计者
- Google Brain 精神核心
- 代表：计算效率与大规模训练

**Oriol Vinyals（DeepMind）**
- Seq2Seq 模型提出者（序列到序列，2014）
- AlphaStar（星际争霸 AI）核心
- Gemini 多模态研究参与者

### 战略意义
Google 的合并是**对 OpenAI 威胁的直接应对**，通过整合资源集中对抗，Gemini 和 PaLM 系列随之加速。

---

## 深度学习三巨头（2018 年图灵奖）

### 三人分道扬镳

**Geoffrey Hinton（多伦多大学）**
- 深度信念网络（RBM，2006）发明者
- Dropout 发明者（2012）
- 2012 年 AlexNet 学生 Krizhevsky 的导师
- 2013 年加入 Google（DNNresearch）
- **2023 年离开 Google，公开警告 AI 风险**
- **立场**：对 AI 存在风险持严肃态度，呼吁监管和对齐研究
- 影响：推动了学术界对 AI 安全的重视

**Yann LeCun（Meta AI Chief Scientist）**
- CNN/LeNet 发明者（1989）
- 2013 年创立 Meta AI (FAIR)
- **立场**：认为 LLM 不是通往 AGI 的路，倡导"世界模型"（World Models）
- 态度：对当前 AI 恐慌论持保留态度，强调需要新范式
- 影响：推动 CV 和自监督学习研究

**Yoshua Bengio（Mila 创始人）**
- 序列模型和注意力机制早期贡献者
- 成立 Mila（蒙特利尔学习算法研究所）
- **坚守学术独立**，不加入大公司
- **立场**：关注 AI 安全和对齐，在政策层面积极发声
- 2023 年后：更加重视 AI 风险，呼吁国际合作和监管

### 三人分歧本质

```
LeCun：自回归 LLM 过时论 + 对恐慌论保留
  └─ 倡导多元化路径，not LLM-only

Hinton：从 LLM 怀疑者 → AI 风险警示者
  └─ 立场转变最大，现在最高警戒度

Bengio：学术独立 + 早期对齐关注
  └─ 坚持安全研究优先
```

**影响**：三人代表了学界对 AI 未来的三种主要态度——技术多元化、风险警惕、安全优先。

---

## OpenAI 内部纠纷：Sam Altman vs Ilya Sutskever

### 关键事件

**2023 年 11 月**：Sam Altman 被董事会短暂离职（5 天后复职）

**核心分歧**：
- Sam Altman：追求快速商业化和规模扩张
- Ilya Sutskever（首席科学家）：优先考虑安全对齐

### Ilya Sutskever 的关键角色

**背景**：
- AlexNet 作者之一
- OpenAI 首席科学家
- 参与 2023 年 11 月投票驱逐 Altman 的董事会决定

**转变**：
- 后公开表示对投票决定感到后悔
- 2024 年离开 OpenAI，创立 **Safe Superintelligence Inc. (SSI)**
- **宗旨**：认为 AGI 安全是当前最重要的事

**影响**：虽然回归失败，但 SSI 的创立象征了**安全研究的独立化**。

---

## 中国 AI 的关键人物

### 李飞飞
- ImageNet 创始人（奠定 CV 基准）
- Stanford AI Lab 主任（2014-2018）
- 2017-2018 在 Google Cloud 任 VP
- 回到学术，现加州大学助理教授
- 影响：CV 基准化与迁移学习普及

### 何恺明
- ResNet（2015）第一作者（改变深度学习）
- Mask R-CNN 等经典架构
- MSRA → Facebook FAIR → MIT（2023）
- 影响：目标检测和实例分割领域 SOTA

### 谢赛宁
- Vision Transformer（ViT）共同作者
- DiT（扩散 Transformer，Sora 基础）
- UC Berkeley / NYU 助理教授 + Meta 顾问
- 影响：将 Transformer 成功应用于视觉

### 梁文锋（WeLab 创始人/DeepSeek）
- 幻方量化创始人（量化私募）
- 拥有大量 GPU 资源（投资回报用于 AI）
- 2024 年 DeepSeek-R1 震撼 AI 界
- **核心成就**：以极低成本（相比 OpenAI）实现接近 o1 的推理能力
- 引发"硬件彩票论"和"算力军备竞赛"反思

---

## 人才流动的宏观规律

### 规律 1：大公司孵化，创业公司收割
- Google 投入研究资源 → Transformer 论文 → 作者创业（Cohere、Adept 等）→ 融资数亿
- OpenAI 研究安全 → Anthropic 创立 → 融资数十亿
- 大公司丧失人才，但社会获益（开放创新）

### 规律 2：安全分歧是最常见的离职原因
- OpenAI → Anthropic（安全 vs 速度）
- Sutskever 创立 SSI（安全优先）
- Hinton 公开警告（对齐重要）

**趋势**：对齐和安全研究从"可选项" 变成"必需项"

### 规律 3：学术 vs 工业的选择
- **坚守学术**：Bengio（Mila）、LeCun（NYU+Meta）
- **入局工业**：多数人被高薪吸引
- **冲突**：薪酬差距导致学术界人才流失，学界地位下降

### 规律 4：地理集聚效应
- **湾区**：OpenAI、Anthropic、Google、Meta
- **纽约**：Meta FAIR、NYU
- **蒙特利尔**：Mila、Element AI
- **北京/杭州/深圳**：智谱、百川、DeepSeek、阿里
- **结论**：资本和人才聚集在少数几个城市

---

## 机构演变树

```
Google Brain (2011)              DeepMind (2010, 被Google收购2014)
    ├─ Jeff Dean                      ├─ Demis Hassabis
    ├─ Greg Corrado                   ├─ Oriol Vinyals
    └─ Andrew Ng                      └─ David Silver
           │                               │
           └─────────── 2023年4月合并 ─────┘
                        │
                   Google DeepMind
                   CEO: Demis Hassabis
                   (对抗 OpenAI+Anthropic)

OpenAI (2015)
    ├─ Elon Musk (联创, 2018离开)
    ├─ Sam Altman (CEO)
    │   ├─ Ilya Sutskever (CSO)
    │   │   └─ 2024 → SSI (Safe Superintelligence)
    │   └─ 多位高管 (2024风波)
    │       ├─ Greg Brockman (暂休)
    │       └─ Mira Murati (CTO, 离职)
    │
    └─ 2021年安全团队离职
        └─ Anthropic (2021)
            ├─ Dario Amodei (CEO)
            ├─ Daniela Amodei (总裁)
            ├─ Chris Olah (可解释性)
            └─ Tom Brown (GPT-3作者)

Transformer作者 (Vaswani et al., 2017)
    ├─ Ashish Vaswani → Adept AI
    ├─ Noam Shazeer → Character.AI
    ├─ Niki Parmar → Adept AI
    ├─ Jakob Uszkoreit → Adept AI
    ├─ Aidan Gomez → Cohere
    ├─ Llion Jones → Sakana AI
    ├─ Łukasz Kaiser → OpenAI
    └─ Illia Polosukhin → NEAR Protocol
```

---

## 2024-2025 新动向

### 独立创业潮
- Ilya Sutskever → SSI（安全）
- 前 OpenAI/Google 高管 → 新创业公司（Sakana、Nous 等）
- **趋势**：从"大公司员工" → "独立创始人"

### 开源争夺
- Meta LLaMA 完全开源
- DeepSeek 开源权重和推理能力
- **结果**：打破 OpenAI 垄断，中国 AI 崛起

### 安全与对齐升温
- Hinton、Bengio 公开警告
- Anthropic、SSI 专注对齐
- **影响**：成为学术热点和融资热点

---

## 学习启示

**为什么关注人物关系？**
1. **理解论文背景**：知道作者后来的动向，理解研究动机
2. **预测产业方向**：人才流向往往先于市场反应
3. **认识 AI 生态**：人的网络 = 知识网络 = 技术网络
4. **理解冲突**：商业化 vs 安全、大公司 vs 创业、东西方竞争

**建议**：
- 读论文时注意作者机构和后续去向
- 关注大型离职/创业事件（这往往代表某个研究方向的升温）
- 理解不同人物的立场差异（Hinton vs LeCun）有助于全面看待 AI 发展
