# AI 关键论文索引

> 本文件列出所有推荐下载的关键论文，包含 Arxiv 下载链接、作者、摘要要点。
> 请手动点击链接下载 PDF 保存到本目录（papers/）。
> 更新日期：2026-03-28（v6：补充 DINOv2）

## 📌 编号规则说明

论文编号（01-32）按**首次加入索引的顺序**分配，**不代表阅读顺序或重要性排序**。部分编号存在空缺属于正常情况：

| 空缺编号 | 原因 |
|----------|------|
| #06 AlexNet (2012) | PDF 需登录才能下载，暂未收录到本地（索引条目已保留） |

如需了解推荐阅读顺序，请参考 [Learning_Roadmap.md](../roadmap/Learning_Roadmap.md)。

---

## ⭐⭐⭐ 第一优先级（必读精读）

### 1. Attention Is All You Need（Transformer）
- **文件名建议**：`01_attention_is_all_you_need_2017.pdf`
- **作者**：Vaswani, Shazeer, Parmar 等（Google Brain / Google Research）
- **年份**：2017
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/1706.03762
  - Arxiv 页面: https://arxiv.org/abs/1706.03762
- **核心贡献**：提出 Transformer 架构，完全基于注意力机制，取代 RNN/CNN，奠定现代 LLM 基础
- **关键概念**：Self-Attention, Multi-Head Attention, Positional Encoding, Encoder-Decoder

---

### 2. BERT（双向 Transformer 预训练）
- **文件名建议**：`02_bert_2018.pdf`
- **作者**：Devlin, Chang, Lee, Toutanova（Google）
- **年份**：2018
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/1810.04805
  - Arxiv 页面: https://arxiv.org/abs/1810.04805
- **核心贡献**：双向预训练语言模型，MLM + NSP 任务，在11个NLP任务上刷新SOTA
- **关键概念**：Masked Language Model, Next Sentence Prediction, Fine-tuning

---

### 3. Language Models are Few-Shot Learners（GPT-3）
- **文件名建议**：`03_gpt3_2020.pdf`
- **作者**：Brown, Mann, Ryder 等（OpenAI）
- **年份**：2020
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/2005.14165
  - Arxiv 页面: https://arxiv.org/abs/2005.14165
- **核心贡献**：1750亿参数，证明大模型在 few-shot 场景下的强大能力
- **关键概念**：In-Context Learning, Few-Shot, Zero-Shot, Scaling

---

### 4. Training language models to follow instructions with human feedback（InstructGPT）
- **文件名建议**：`04_instructgpt_rlhf_2022.pdf`
- **作者**：Ouyang, Wu, Jiang 等（OpenAI）
- **年份**：2022
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/2203.02155
  - Arxiv 页面: https://arxiv.org/abs/2203.02155
- **核心贡献**：RLHF 技术使 LLM 学会遵循人类指令，ChatGPT 的技术前身
- **关键概念**：RLHF, PPO, Reward Model, SFT

---

### 5. Scaling Laws for Neural Language Models
- **文件名建议**：`05_scaling_laws_2020.pdf`
- **作者**：Kaplan, McCandlish, Henighan 等（OpenAI）
- **年份**：2020
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/2001.08361
  - Arxiv 页面: https://arxiv.org/abs/2001.08361
- **核心贡献**：揭示模型性能与参数量、数据量、计算量的幂律关系
- **关键概念**：Power Law, Compute Budget, Optimal Model Size

---

## ⭐⭐ 第二优先级（重点阅读）

### 6. ImageNet Classification with Deep CNNs（AlexNet）
- **文件名建议**：`06_alexnet_2012.pdf`
- **作者**：Krizhevsky, Sutskever, Hinton（多伦多大学）
- **年份**：2012
- **下载状态**：⚠️ **PDF 未下载** — NeurIPS 官方链接需登录，可尝试以下备用方式手动获取：
  - NeurIPS 官方：https://papers.nips.cc/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf
  - 备用搜索：在 Google Scholar 搜索 "AlexNet Krizhevsky 2012" 通常可找到公开版本
  - 或直接在 Chrome 访问：https://www.semanticscholar.org/paper/ImageNet-classification-with-deep-convolutional-Krizhevsky-Sutskever/abd1c342495432171beb7ca8fd9551ef13cbd0ff
- **核心贡献**：GPU 训练深度 CNN，ImageNet 错误率从26%降至15%，掀起深度学习浪潮

---

### 7. Deep Residual Learning for Image Recognition（ResNet）
- **文件名建议**：`07_resnet_2015.pdf`
- **作者**：He, Zhang, Ren, Sun（微软研究院）
- **年份**：2015
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/1512.03385
  - Arxiv 页面: https://arxiv.org/abs/1512.03385
- **核心贡献**：残差连接解决梯度消失，152层网络训练成功

---

### 8. Generative Adversarial Networks（GAN）
- **文件名建议**：`08_gan_2014.pdf`
- **作者**：Goodfellow, Pouget-Abadie 等
- **年份**：2014
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/1406.2661
  - Arxiv 页面: https://arxiv.org/abs/1406.2661
- **核心贡献**：生成对抗网络，生成式 AI 的奠基之作

---

### 9. Denoising Diffusion Probabilistic Models（DDPM）
- **文件名建议**：`09_ddpm_2020.pdf`
- **作者**：Ho, Jain, Abbeel（UC Berkeley）
- **年份**：2020
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/2006.11239
  - Arxiv 页面: https://arxiv.org/abs/2006.11239
- **核心贡献**：扩散模型的现代形式，Stable Diffusion 等的理论基础

---

### 10. Chain-of-Thought Prompting Elicits Reasoning in LLMs
- **文件名建议**：`10_chain_of_thought_2022.pdf`
- **作者**：Wei, Wang, Schuurmans 等（Google）
- **年份**：2022
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/2201.11903
  - Arxiv 页面: https://arxiv.org/abs/2201.11903
- **核心贡献**：CoT 提示大幅提升 LLM 推理能力，Few-shot CoT 范式

---

### 11. Learning Transferable Visual Models From Natural Language（CLIP）
- **文件名建议**：`11_clip_2021.pdf`
- **作者**：Radford, Kim, Hallacy 等（OpenAI）
- **年份**：2021
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/2103.00020
  - Arxiv 页面: https://arxiv.org/abs/2103.00020
- **核心贡献**：文本-图像对比学习，多模态 AI 基础

---

### 12. LLaMA: Open and Efficient Foundation Language Models
- **文件名建议**：`12_llama_2023.pdf`
- **作者**：Touvron, Lavril 等（Meta AI）
- **年份**：2023
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/2302.13971
  - Arxiv 页面: https://arxiv.org/abs/2302.13971
- **核心贡献**：开源高性能 LLM，推动开源 LLM 生态爆发

---

## ⭐ 第三优先级（扩展阅读）

### 13. Efficient Estimation of Word Representations（Word2Vec）
- **文件名建议**：`13_word2vec_2013.pdf`
- **下载链接**：https://arxiv.org/pdf/1301.3781
- **阅读状态**：✅ 已完成（见 `reports/paper_analyses/13_word2vec_2013_分析报告.md`）

### 14. Neural Machine Translation by Jointly Learning to Align（Bahdanau Attention）
- **文件名建议**：`14_bahdanau_attention_2014.pdf`
- **下载链接**：https://arxiv.org/pdf/1409.0473

### 15. LoRA: Low-Rank Adaptation of Large Language Models
- **文件名建议**：`15_lora_2021.pdf`
- **下载链接**：https://arxiv.org/pdf/2106.09685

### 16. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks（RAG）
- **文件名建议**：`16_rag_2020.pdf`
- **下载链接**：https://arxiv.org/pdf/2005.11401

### 17. ReAct: Synergizing Reasoning and Acting in Language Models
- **文件名建议**：`17_react_2022.pdf`
- **下载链接**：https://arxiv.org/pdf/2210.03629

### 18. FlashAttention: Fast and Memory-Efficient Exact Attention
- **文件名建议**：`18_flashattention_2022.pdf`
- **下载链接**：https://arxiv.org/pdf/2205.14135

---

## 📚 补充论文（来自《AI演义》笔记，v2新增）

### ⭐⭐⭐ 补充高优先级

### 19. Vision Transformer（ViT）
- **文件名建议**：`19_vit_2020.pdf`
- **作者**：Dosovitskiy 等（Google Brain）
- **年份**：2020
- **下载链接**：https://arxiv.org/pdf/2010.11929
- **核心贡献**：将图像分成 16×16 的 Patch 序列，直接用 Transformer 处理图像，推动 CV 领域从 CNN 迁移到 Transformer

---

### 20. Stable Diffusion / Latent Diffusion Models
- **文件名建议**：`20_stable_diffusion_2021.pdf`
- **作者**：Rombach, Blattmann 等（海德堡大学）
- **年份**：2021（发布于2022）
- **下载链接**：https://arxiv.org/pdf/2112.10752
- **核心贡献**：在潜空间运行扩散模型，大幅降低计算成本；结合 CLIP 文本编码器实现文生图，Stable Diffusion 直接基于此

---

### 21. Outrageously Large Neural Networks（Sparsely-Gated MoE）
- **文件名建议**：`21_moe_2017.pdf`
- **作者**：Shazeer, Mirhoseini 等（Google Brain）
- **年份**：2017
- **下载链接**：https://arxiv.org/pdf/1701.06538
- **核心贡献**：现代 MoE（混合专家）架构的奠基论文，稀疏激活大幅降低推理成本，是 GPT-4、Gemini 等的关键技术

---

### 22. The Bitter Lesson（非论文，Rich Sutton 博客）
- **文件名建议**：`22_bitter_lesson_2019.md`（保存为 Markdown）
- **作者**：Rich Sutton（强化学习先驱，Sutton & Barto 教材作者）
- **年份**：2019
- **下载状态**：✅ **已保存** — 本地文件：`22_bitter_lesson_2019.md`（英文原文 + 中文译文 + 核心观点提炼）
- **核心思想**：AI 70年历史的最大教训——"能随算力扩展的通用方法，长期来看总是赢"。这是理解整个 AI 发展史的**元认知框架**。⭐⭐⭐ 强烈推荐
- **延伸阅读**：项目 [AI发展时间线·硬件彩票章节](../roadmap/AI_Development_Timeline.md) 对这一思想做了深度展开

---

### ⭐⭐ 补充中优先级

### 23. Distilling the Knowledge in a Neural Network（知识蒸馏）
- **文件名建议**：`23_distilling_2015.pdf`
- **作者**：Hinton, Vinyals, Dean
- **年份**：2015
- **下载链接**：https://arxiv.org/pdf/1503.02531
- **核心贡献**：知识蒸馏范式——用大模型的"软标签"训练小模型，开创了教师-学生学习框架

---

### 24. Mastering Go without Human Knowledge（AlphaGo Zero）
- **文件名建议**：`24_alphago_zero_2017.pdf`
- **作者**：Silver 等（DeepMind）
- **年份**：2017
- **下载链接**：https://arxiv.org/pdf/1712.01815
- **核心贡献**：纯强化学习，无需人类先验知识；启发了 OpenAI 的 test-time compute 思路（每步执行1600次 MCTS 搜索）

---

### 25. ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- **文件名建议**：`25_zero_2019.pdf`
- **作者**：Rajbhandari 等（微软 DeepSpeed 团队）
- **年份**：2019
- **下载链接**：https://arxiv.org/pdf/1910.02054
- **核心贡献**：通过切分优化器状态、梯度、参数，解决大模型训练的显存问题；DeepSpeed 的核心工作

---

### 26. Tulu 3：后训练全流程开源
- **文件名建议**：`26_tulu3_2024.pdf`
- **作者**：Lambert 等（Allen Institute for AI）
- **年份**：2024
- **下载链接**：https://arxiv.org/pdf/2411.15124
- **核心贡献**：完整开源后训练三段流程（SFT→DPO→RLVR），性能媲美 GPT-4o-mini 和 Claude 3.5-Haiku

---

### 27. Scalable Diffusion Models with Transformers（DiT）
- **文件名建议**：`27_dit_2022.pdf`
- **作者**：Peebles, 谢赛宁（NYU）
- **年份**：2022
- **下载链接**：https://arxiv.org/pdf/2212.09748
- **核心贡献**：用 Transformer 替换扩散模型中的 U-Net，Sora 的架构基础

---

### ⭐ 补充背景参考

### 28. Brook for GPUs: Stream Computing（GPU 通用计算起源）
- **文件名建议**：`28_brook_2004.pdf`
- **年份**：2004
- **下载链接**：https://arxiv.org/pdf/cs/0406040

### 29. LAION-5B: Open Large-Scale Dataset
- **文件名建议**：`29_laion5b_2022.pdf`
- **年份**：2022
- **下载链接**：https://arxiv.org/pdf/2210.08402

### 30. The RefinedWeb Dataset for Falcon LLM
- **文件名建议**：`30_refinedweb_2023.pdf`
- **年份**：2023
- **下载链接**：https://arxiv.org/pdf/2306.01116

### 31. MegaScale: Scaling LLM Training to 10,000+ GPUs
- **文件名建议**：`31_megascale_2024.pdf`
- **年份**：2024（字节跳动）
- **下载链接**：https://arxiv.org/pdf/2402.15627

### 32. Deep Unsupervised Learning using Nonequilibrium Thermodynamics（扩散模型原版）
- **文件名建议**：`32_diffusion_original_2015.pdf`
- **年份**：2015
- **下载链接**：https://arxiv.org/pdf/1503.03585

---

### 33. Mistral 7B
- **文件名建议**：`33_mistral_7b_2023.pdf`
- **作者**：Jiang 等（Mistral AI）
- **年份**：2023
- **下载链接**：https://arxiv.org/pdf/2310.06825
- **核心贡献**：通过 GQA 与 Sliding Window Attention 提升 7B 开源模型的性能-效率比，推动“小而强”的开源 LLM 路线

---

### 34. LLaMA 2
- **文件名建议**：`34_llama2_2023.pdf`
- **作者**：Touvron 等（Meta AI）
- **年份**：2023
- **下载链接**：https://arxiv.org/pdf/2307.09288
- **核心贡献**：系统性开放基础模型与 Chat 模型，推动开源对话模型、安全微调与私有化部署生态发展

---

### 35. DINOv2: Learning Robust Visual Features without Supervision
- **文件名建议**：`35_dinov2_2023.pdf`
- **作者**：Maxime Oquab 等（Meta AI Research）
- **年份**：2023
- **发表**：arXiv:2304.07193, TMLR 2024
- **下载链接**：
  - Arxiv PDF: https://arxiv.org/pdf/2304.07193
  - Arxiv 页面: https://arxiv.org/abs/2304.07193
- **核心贡献**：通过1.42亿精选图像的自监督预训练，首次证明纯自监督ViT在分类、分割、深度估计等全视觉任务上超越OpenCLIP；KoLeo正则化、知识蒸馏传承、CV基础模型范式
- **关键概念**：自监督学习、知识蒸馏、KoLeo正则化、LVD-142M、视觉基础模型
- **阅读状态**：✅ 已完成（见 `reports/paper_analyses/35_dinov2_2023.md`）

---

## 快速下载脚本（在有网络环境中运行）

```bash
#!/bin/bash
# 保存为 download_papers.sh 并运行
PAPERS_DIR="./papers"
mkdir -p "$PAPERS_DIR"

declare -A PAPERS=(
  ["01_attention_is_all_you_need_2017.pdf"]="https://arxiv.org/pdf/1706.03762"
  ["02_bert_2018.pdf"]="https://arxiv.org/pdf/1810.04805"
  ["03_gpt3_2020.pdf"]="https://arxiv.org/pdf/2005.14165"
  ["04_instructgpt_rlhf_2022.pdf"]="https://arxiv.org/pdf/2203.02155"
  ["05_scaling_laws_2020.pdf"]="https://arxiv.org/pdf/2001.08361"
  ["07_resnet_2015.pdf"]="https://arxiv.org/pdf/1512.03385"
  ["08_gan_2014.pdf"]="https://arxiv.org/pdf/1406.2661"
  ["09_ddpm_2020.pdf"]="https://arxiv.org/pdf/2006.11239"
  ["10_chain_of_thought_2022.pdf"]="https://arxiv.org/pdf/2201.11903"
  ["11_clip_2021.pdf"]="https://arxiv.org/pdf/2103.00020"
  ["12_llama_2023.pdf"]="https://arxiv.org/pdf/2302.13971"
  ["13_word2vec_2013.pdf"]="https://arxiv.org/pdf/1301.3781"
  ["14_bahdanau_attention_2014.pdf"]="https://arxiv.org/pdf/1409.0473"
  ["15_lora_2021.pdf"]="https://arxiv.org/pdf/2106.09685"
  ["16_rag_2020.pdf"]="https://arxiv.org/pdf/2005.11401"
  ["17_react_2022.pdf"]="https://arxiv.org/pdf/2210.03629"
  ["18_flashattention_2022.pdf"]="https://arxiv.org/pdf/2205.14135"
)

for filename in "${!PAPERS[@]}"; do
  url="${PAPERS[$filename]}"
  echo "Downloading $filename..."
  curl -L "$url" -o "$PAPERS_DIR/$filename" --max-time 60
  sleep 2  # Be respectful to arxiv servers
done

echo "Done! Check $PAPERS_DIR for downloaded papers."
```
