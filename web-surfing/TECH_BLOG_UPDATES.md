# 顶尖技术博客更新

想找下一篇值得读的 AI 技术文章，可以从这里翻。点中文标题看原文，点「阅读报告」看已有的学习报告；鼠标停在标题上可查看原题。

每次查询「顶尖技术博客最近有什么更新」，都更新这一页，保留之前的文章和学习记录。

想听播客，可以看 [小宇宙精选播客历史速看表](../podcast-learning/PODCAST_UPDATES.md)。

**最近检查：2026-11-15（北京时间）** · **累计收录时段：2026-09-02—2026-11-13**

检查了 **28 个官方渠道**，目前收录 **502 篇**日期已核实的文章：**47 篇已学习**，**10 篇有相关报告**，**445 篇未做学习任务**。部分渠道的历史仍有缺口，见[获取情况](#coverage)。

**本次补充 18 篇**，增量检查覆盖 2026-11-08—2026-11-15。新增包括常驻 Agent 安全、安全评测、ChatGPT Wallet、llama.cpp 1.0、机器人仿真与 GPU 通信优化，学习状态以各条目的报告入口为准。 Google Research 的三篇候选已取得正文，但尚未核实日期，单列在待补区，不计入新增。

范围包括 AI 研究、模型与开发工具发布、Agent、评测、训练和推理工程。不同团队围绕同一技术写的独立文章分别保留，同一篇文章的镜像合并。

**跳转：** [11 月](#m202611) · [10 月](#m202610) · [9 月](#m202609) · [已有学习报告](#studied) · [只标月份的文章](#month-only) · [日期待补](#undated) · [已学习的旧文](#older) · [渠道获取情况](#coverage)

| 发布时间 | 已收录 | 已学习 |
| --- | ---: | ---: |
| [2026-11](#m202611) | 150 篇 | 4 篇 |
| [2026-10](#m202610) | 215 篇 | 39 篇 |
| [2026-09](#m202609) | 137 篇 | 4 篇 |

「已学习」表示有直接研究该文或该系列的已完成报告；「相关报告」只提供背景，仍可继续深读本篇。「未做」表示未找到对应专题报告，日报提及或参考文献引用不算完成学习。

各月按厂商分组，点击展开。文章多的渠道可通过页面搜索查模型、工具或关键词。

<a id="m202611"></a>

## 2026 年 11 月

<details open>
<summary><strong>Sakana AI · 1 篇</strong></summary>

- **11-02** [Schmidhuber 与 Sakana 的 AI 研究研讨会](https://sakana.ai/symposium-2026 "【開催レポート】Sakana AIシンポジウム：Jürgen Schmidhuberが語るAIのこれまでとこれから、日本から挑む言語モデル・世界モデル・Physical AI") · 未做  
  回顾语言模型、世界模型和物理 AI 的讨论，适合了解研究方向。

</details>


<details>
<summary><strong>OpenAI 研究与技术更新 · 24 篇 · 1 篇已学习</strong></summary>

- **11-13** [ChatGPT Wallet：Agent 支付的授权与安全检查](https://openai.com/index/introducing-chatgpt-wallet "Introducing ChatGPT Wallet") · 未做

  介绍让 Agent 在不接触真实卡号的情况下付款，并为每次购买设置安全检查与授权边界；先从美国部分用户开放。

- **11-12** [支持儿童 AI 安全研究](https://openai.com/index/children-first-declaration "Supporting research on AI and children’s safety") · 未做

  宣布资助面向儿童 AI 安全的研究，并支持共享的风险与机会度量工具；这是一则研究资助承诺，非技术报告。

- **11-11** [JioStar：大规模视频发现中的评测与生产防护](https://openai.com/index/jiostar-vijay-seshadri "JioStar’s chief architect on AI discovery at 500M-user scale") · 未做

  介绍面向视频和板球内容的语音检索助手，讨论评测、防护和生产部署；规模与使用效果来自客户案例。

- **11-10** [新加坡航空：客服、旅行发现与受管内部 AI 平台](https://openai.com/index/singapore-airlines-travel-work "Singapore Airlines elevates travel &amp; work with OpenAI technology") · 未做

  介绍 API 在旅客服务中的应用，以及员工平台 Jarvis 和软件开发工作流；服务改善数字为客户自报。

- **11-10** [Cogent：结合企业上下文的自动化漏洞修复](https://openai.com/index/cogent-security "Cogent and OpenAI build cyber defense factories for enterprises") · 未做

  讨论修复 Agent 如何理解业务系统、风险与可安全执行的变更，重点是将漏洞发现衔接到企业修复流程。

- **11-10** [AI 与自由职业：任务需求、技能组合和项目预算](https://openai.com/index/ai-effect-on-freelance-work "Work at the Frontier: AI’s effect on freelance work") · 未做

  介绍与 Upwork 合作的市场研究，比较不同任务的需求变化与 AI 项目特征；平台上的观察不等于整个劳动力市场的因果结论。

- **11-10** [Businesses in ChatGPT：商家信息与 Business Agent](https://openai.com/index/introducing-businesses-chatgpt "Introducing Businesses in ChatGPT") · 未做

  介绍商家资料和产品订阅接入、聚合洞察及 Business Agent 测试发布，说明商家对话与 ChatGPT 独立回答的区分。

- **11-09** [Control Room：集中追踪与中止研究推理任务](https://openai.com/index/control-room "Control Room: A central system to track and stop model workloads across our research infrastructure") · 未做

  介绍把任务身份、推理引擎和监控告警连接起来，在安全或可靠性问题出现时停止模型输出；停机时延与故障处理能力为官方报告。

- **11-09** [CodeRabbit：用多 Agent、评测与安全检查审查 AI 代码](https://openai.com/index/coderabbit-codex-daybreak "CodeRabbit scales agentic software development and ships 20x more") · **已学习**

  结合案例摘要与 CodeRabbit 官方文档分析审查、评测和运行时验证，附可运行的离线实验。原页全文未核验，交付增幅为客户自报。 [阅读报告](../ai-learning/reports/knowledge_reports/CodeRabbit_多Agent代码审查_评测与运行时验证_深度解析_20261110.md)

- **11-09** [Kuken：用模型检索历史设备图纸](https://openai.com/index/kuken "Kuken Industries searches 70 years of drawings in minutes") · 未做

  介绍根据图纸内容、零件信息和现场需求建立检索应用，并比较模型的提取准确率与成本；效率变化来自客户案例。

- **11-06** [OpenAI 与 Hacktron 合作开展安全研究](https://openai.com/index/partnering-with-hacktron "Partnering with Hacktron to find vulnerabilities in OpenAI’s systems") · 未做

  介绍利用前沿 AI 查找漏洞、检查第三方服务连接的安全研究合作；这是一则协作进展说明。

- **11-06** [BioBasicsBench：评测 Agent 处理日常湿实验数据](https://openai.com/index/measuring-how-ai-agents-handle-wet-lab-science "Measuring how AI agents handle everyday wet-lab science") · 未做

  用实验室常见任务检查 Agent 对原始数据的理解与分析，区分工具使用能力和具体科学判断。

- **11-05** [Cult.fit：让不同职能的团队用 Codex 制作工具](https://openai.com/index/cultfit-builds-with-codex "Cult.fit builds operational muscle with Codex") · 未做

  以健身服务企业的内部实践为例，介绍业务团队如何把重复工作转成工具，并调整协作方式。

- **11-05** [GPT-6 Cyber：漏洞研究与授权范围对齐](https://openai.com/index/introducing-gpt-6-cyber "GPT‑6 Cyber: Advancing the frontier of aligned cybersecurity agents") · 未做

  介绍安全模型的漏洞发现、验证与修复能力，以及遵守任务边界的训练和评测；性能与对齐结果均为官方报告。

- **11-05** [Franklin Templeton：用 AI 支持投资研究](https://openai.com/index/franklin-templeton "Franklin Templeton uses OpenAI to support investment research") · 未做

  介绍如何组织研究观点、比较分析结果和检查风险；这是辅助研究工作流的案例，不代表投资结果已经改善。

- **11-05** [Merge：把 OpenAI 工具用于代码与业务工作](https://openai.com/index/merge-builds-with-openai "Merge builds product and business tools with OpenAI technology") · 未做

  介绍团队如何将模型、ChatGPT 和 Codex 用于代码审查、营销准备和内部业务工具。

- **11-04** [Linux 内核漏洞研究：从发现到验证与候选补丁](https://openai.com/index/a-thousand-fewer-paths-to-root "A thousand fewer paths to root") · 未做

  介绍受控环境中的自动化安全研究流程；动态复现、可利用性判断与人工审查分别承担不同验证责任。

- **11-04** [Images 2.6：图像生成、GIF 与更精细的编辑](https://openai.com/index/introducing-images-2-6 "Introducing Images 2.6") · 未做

  介绍图像模型的生成和编辑更新，以及面向 API 的控制能力；便于了解制作与迭代工作流。

- **11-04** [DevRev：结合企业知识与权限的自主服务](https://openai.com/index/devrev-enterprise-self-service "DevRev delivers autonomous self-service with GPT-6.1 Sol") · 未做

  介绍 Computer、Operator 与企业 Harness 如何连接实时数据、控制动作，并用企业任务评测模型组合。

- **11-03** [把 ChatGPT 与 Codex 用于 CAD、PCB 和仿真](https://openai.com/index/accelerating-engineering-for-the-physical-world "Accelerating engineering for the physical world") · 未做

  汇集物理工程中的辅助设计与分析工作流，关注 AI 如何接入专业工具及工程师的检查环节。

- **11-03** [Cisco：把网络情报与 AI 安全分析结合](https://openai.com/index/cisco-cyber "How Cisco defends at machine speed with OpenAI") · 未做

  介绍网络安全团队利用模型组织信息、支持检测与调查的实践，属于企业应用案例。

- **11-02** [LifeVal：评测 AI 能否帮人完成日常事务](https://openai.com/index/lifeval "LifeVal") · 未做

  介绍覆盖育儿、财务和政务手续等日常任务的评测，重点看 AI 是否真正帮助用户完成事情。

- **11-02** [Qodo × Codex：把团队知识带入代码审查](https://openai.com/index/qodo-codex-plugin "Qodo builds context into AI code review with Codex") · 未做

  介绍如何把公司知识和编码规范纳入审查上下文，关注跨仓库代码检查的工作流。

- **11-02** [Pando：为 Codex 带来的开发规模扩展 Git](https://openai.com/index/scaling-git-at-openai "Scaling Git at OpenAI") · 未做

  介绍保持 Git 协议和客户端兼容的新后端，重点是并发写入、读取吞吐与大型单仓库的存储设计。

</details>


<details>
<summary><strong>Google DeepMind · 8 篇</strong></summary>

- **11-13** [开放天气 AI 数据：SatWeave 卫星影像与 PARDIG 降水](https://deepmind.google/blog/opening-the-datasets-behind-our-ai-weather-models "Opening the datasets behind our AI weather models") · 未做

  介绍用于天气、水文与气候研究的历史数据和实时订阅；原文及发布时间元数据均为 11 月 13 日，未采用 RSS 中冲突的 11 月 10 日。

- **11-12** [Gemini 4 Hydrogen：面向日常编码与 Agent 执行的模型](https://deepmind.google/blog/introducing-gemini-4-hydrogen "Introducing Gemini 4 Hydrogen") · 未做

  介绍不同思考档位，以及与 Carbon、Argon 配合的多模型任务分工；速度、成本与评测结果为官方报告。

- **11-11** [AlphaGenome 2：预测遗传变异对不同细胞的影响](https://deepmind.google/blog/alphagenome-2-deciphering-how-cells-read-dna-to-better-understand-disease "AlphaGenome 2: Deciphering how cells read DNA to better understand disease") · 未做

  介绍结合 DNA 序列与单细胞生物学的预测模型，帮助研究者分析遗传变异、细胞类型与疾病的关系。

- **11-10** [AlphaProof Code：用 Lean 验证 Signal 加密代码](https://deepmind.google/blog/introducing-alphaproof-code "Introducing AlphaProof Code: a breakthrough in verifying complex software at depth") · 未做

  介绍研究者引导 Agent 为 Signal 加密协议的实际代码建立形式化证明；证明针对指定安全性质，不等同于整个应用没有漏洞。

- **11-10** [Gemini 4 Carbon：编程、科学推理与安全能力更新](https://deepmind.google/blog/gemini-4-carbon-is-now-available "Gemini 4 Carbon is now available") · 未做

  汇总新模型在知识工作、Agent 编程、科学与网络安全任务上的更新，并说明可用入口与模型安全评测。

- **11-09** [Gemini Robotics 2.5：机器人灵巧操作与技能学习](https://deepmind.google/blog/gemini-robotics-2-5-accelerates-real-world-physical-intelligence "Gemini Robotics 2.5 accelerates real-world general dexterity") · 未做

  介绍视觉—语言—动作模型在操作技能、学习速度和真实环境适应上的更新；能力与安全表现为官方报告。

- **11-05** [Gemini Omni 1.2 Flash：更长的视频与多轮编辑](https://deepmind.google/blog/gemini-omni-12-flash-fast-and-cost-effective-with-longer-clips "Gemini Omni 1.2 Flash: Fast and cost-effective with longer clips") · 未做

  介绍原生 15 秒视频生成、参考素材遵循和对话式局部编辑，并说明不同分辨率之间的制作流程。

- **11-03** [Google Antigravity：Agent 驱动的化学信息学](https://deepmind.google/blog/agentic-cheminformatics-with-google-antigravity "Agentic cheminformatics with Google Antigravity") · 未做

  介绍化学信息学 Skills 如何支持化合物检索与药物发现工作流；应用效果仍需结合具体实验判断。

</details>


<details>
<summary><strong>Google Research · 2 篇</strong></summary>

- **11-11** [用可穿戴设备做心血管-肾脏-代谢风险分析](https://research.google/blog/using-wearables-to-enable-cardiovascular-kidney-metabolic-ckm-risk-profiling-for-personalized-coaching "Using wearables to enable cardiovascular-kidney-metabolic (CKM) risk profiling for personalized coaching") · 未做

  介绍可穿戴设备数据如何支持 CKM 风险分层与个性化健康指导研究。

- **11-09** [Language Explorer：探索世界语言](https://research.google/blog/exploring-the-worlds-languages-with-language-explorer "Exploring the world's languages with Language Explorer") · 未做

  发布用于浏览和比较世界语言资源的 Language Explorer 工具。

</details>


<details>
<summary><strong>AMD ROCm · 18 篇</strong></summary>

- **11-13** [GPU 发起 SDMA：RCCL 与 rocSHMEM 的跨卡通信](https://rocm.blogs.amd.com/software-tools-optimization/gpu-initiated-sdma/README.html "GPU-Initiated DMA Copy Engines in RCCL and rocSHMEM") · 未做

  介绍由 GPU 内核触发节点内 DMA 拷贝，将数据传输与计算资源分开调度，以改善推理中的通信重叠。

- **11-12** [AMD Life Science 26.08：完整的医学影像栈](https://rocm.blogs.amd.com/artificial-intelligence/rocm-ls-2608/README.html "AMD Life Science 26.08: A Complete Medical Imaging Stack on AMD Instinct™ GPUs") · 未做

  汇总从数据读取、预处理到病理与 CT 分析的医学影像工作流在 Instinct GPU 上的整套栈发布。

- **11-12** [超越嵌入量化：Quark UINT4 量化 Qwen3.8-Flash-Next](https://rocm.blogs.amd.com/artificial-intelligence/quark-qwen-ple/README.html "Beyond Embedding Quantization: Quark UINT4 Qwen3.8-Flash-Next on Ryzen AI Halo") · 未做

  用 Quark 把专家权重量化到 UINT4，在 128GB 统一内存的 Ryzen AI Halo 上为运行时缓冲和 KV Cache 腾出空间。

- **11-11** [长上下文服务的并行策略：MI300X 上的 GLM-5.3-Flash](https://rocm.blogs.amd.com/artificial-intelligence/glm53flash-mi300x-vllm/README.html "Parallelism for Long-Context Serving: GLM-5.3-Flash on MI300X") · 未做

  介绍 GLM-5.3-Flash 在单节点八卡 MI300X 上的推理配置，FP8 权重之外大部分显存留给 KV Cache；性能数字为作者自报。

- **11-11** [MI355X 上加速 GLM-5.2：EvalScope 基准与前缀缓存](https://rocm.blogs.amd.com/artificial-intelligence/glm5.2-mi355x-kvcache/README.html "Accelerating GLM-5.2 on AMD Instinct MI355X: EvalScope Benchmarks with Prefix Caching") · 未做

  围绕 MoE、稀疏注意力与长输入带来的计算、带宽和互联瓶颈，介绍内核调优与前缀缓存基准。

- **11-10** [引入 ROCm 手册](https://rocm.blogs.amd.com/software-tools-optimization/rocm-handbooks-intro/README.html "Introducing the ROCm Handbooks") · 未做

  按主题重新组织的 ROCm 文档手册，便于按学习路径查阅各专题。

- **11-09** [MONAILabel 0.8.5：在 AMD GPU 上交互标注医学图像](https://rocm.blogs.amd.com/artificial-intelligence/monailabel-2608/README.html "MONAILabel 0.8.5 on AMD Instinct™ GPUs: Interactive Medical-Image Annotation") · 未做

  介绍 ROCm 适配、脾脏 CT 分割测试与模型建议—人工修正的标注流程，并区分模型推理和预处理、文件读写的耗时。

- **11-06** [ROCm InferaSim：用仿真筛选模型服务配置](https://rocm.blogs.amd.com/software-tools-optimization/inferasim/README.html "ROCm InferaSim: Cut LLM Serving Trial Costs and Deploy the Best Configuration") · 未做

  面向引擎、并行方式、精度和调度参数的组合搜索，介绍如何在实际部署前缩小待测配置范围。

- **11-06** [PrimusClaw：GPU 集群里的受管 Agent 运行时](https://rocm.blogs.amd.com/software-tools-optimization/primusclaw/README.html "PrimusClaw: An Open-Source Managed Agent Runtime for AMD Instinct GPU Clusters") · 未做

  介绍部署在自有 Kubernetes 集群中的会话存储、Agent Harness 与独立沙箱，便于将任务放到 GPU 资源附近执行。

- **11-05** [在线量化：同一检查点适配多种推理场景](https://rocm.blogs.amd.com/artificial-intelligence/online_quantization/README.html "Online Quantization: Smooth Path from One Checkpoint to Any Desired Serving Scenario") · 未做

  讨论把权重量化移到加载与服务阶段的工程方法，以及显存、精度和推理效率之间的取舍。

- **11-05** [用 madengine 分析 Primus 训练：从算子到内核](https://rocm.blogs.amd.com/software-tools-optimization/madengine-primus-profiling/README.html "From Operator to Kernel: Profile DeepSeek-V4-Flash in Primus with madengine") · 未做

  以 DeepSeek-V4-Flash 的缩小训练配置为例，关联框架算子、GPU 内核与通信，定位训练步骤中的开销。

- **11-04** [MI355X 上的 GLM-5.2：优化编码 Agent 的交互](https://rocm.blogs.amd.com/software-tools-optimization/glm52-agentx-mi355x/README.html "GLM-5.2 AgentX on AMD Instinct MI355X: Boosting Throughput and Interactivity") · 未做

  围绕持续增长的提示词、上下文复用与并发任务，介绍基于 AgentX 负载的吞吐和交互延迟优化。

- **11-04** [AMD GPU 性能分析第七篇：AI 与 PyTorch](https://rocm.blogs.amd.com/software-tools-optimization/profiling-guide/ai_tinyopenfold/README.html "Performance Profiling on AMD GPUs - Part 7: AI/PyTorch® Edition") · 未做

  把系列性能分析方法应用到 AI 工作负载，说明如何从应用层追踪到 GPU 执行与瓶颈。

- **11-04** [用 Quark 混合精度量化运行 Wan2.2](https://rocm.blogs.amd.com/artificial-intelligence/quark-wan22-mixed-precision/README.html "Quark Mixed-Precision Quantization for Wan2.2 Video Generation on AMD Instinct GPUs") · 未做

  介绍视频生成模型在 AMD GPU 上的量化实践，关注精度配置、显存占用与生成质量的平衡。

- **11-03** [FlyDSL Mono：降低 ATOM 模型服务的解码延迟](https://rocm.blogs.amd.com/software-tools-optimization/flydsl-mono-atom/README.html "FlyDSL Mono Kernels for High-Interactivity LLM Serving in ATOM") · 未做

  围绕高交互性模型服务，介绍内核优化如何减少解码等待，让编码 Agent 更快进入下一步工具调用。

- **11-02** [MI300X 内存加载停顿与指令调度](https://rocm.blogs.amd.com/software-tools-optimization/scheduling_VMEM_loads_gfx942/README.html "Device Memory Load Issue Stalls and Scheduling Opportunities in Lock-Stepped Kernels on AMD Instinct™ MI300X") · 未做

  分析设备内存和缓存层级里的加载停顿，探索锁步执行内核的指令调度优化。

- **11-02** [在多张 AMD RDNA 4 GPU 上扩展扩散推理](https://rocm.blogs.amd.com/artificial-intelligence/diffusion-xdit-rdna4/README.html "How to Scale Diffusion Inference Across AMD RDNA 4 GPUs") · 未做

  围绕图像与视频生成，介绍如何利用多卡显存和计算资源运行更大的扩散模型工作负载。

- **11-02** [TeaCache：加速 Ryzen AI 上的 Stable Diffusion](https://rocm.blogs.amd.com/software-tools-optimization/sd-teacache-npu/README.html "Faster Stable Diffusion on AMD Ryzen™ AI with TeaCache") · 未做

  介绍如何复用中间结果、减少重复计算，在不重新训练模型的前提下加速 NPU 上的图像生成。

</details>


<details>
<summary><strong>NVIDIA 技术博客 · 24 篇</strong></summary>

- **11-13** [cuBLAS 新 FP64 算法：在整数 Tensor Core 上做高精度计算](https://developer.nvidia.com/blog/faster-scientific-simulations-with-new-fp64-algorithms-in-nvidia-cublas "Faster Scientific Simulations with New FP64 Algorithms in NVIDIA cuBLAS") · 未做

  讨论如何利用整数 Tensor Core 实现双精度矩阵乘法，比较科学计算中的速度、精度与适用条件。

- **11-13** [cuPhoton：用 GPU 加速黑洞观测的干涉测量](https://developer.nvidia.com/blog/run-gpu-powered-black-hole-interferometry-with-nvidia-cuphoton "Run GPU-Powered Black Hole Interferometry with NVIDIA cuPhoton") · 未做

  以甚长基线干涉测量为例，介绍如何处理射电观测信号并用 GPU 加速相关计算；这是科学计算工程教程。

- **11-13** [cuDLA Python：在 Jetson Orin 上使用专用推理加速器](https://developer.nvidia.com/blog/run-native-dla-inference-in-python-on-nvidia-jetson-agx-orin-using-cudla "Run Native DLA Inference in Python on NVIDIA Jetson AGX Orin Using cuDLA") · 未做

  介绍通过 Python 创建 DLA 设备、加载编译网络和提交推理任务，将受支持的网络运算从 GPU 卸载。

- **11-13** [两台 DGX Station：用 vLLM 部署 GLM-5.3](https://developer.nvidia.com/blog/when-one-gpu-isnt-enough-serving-glm-5-3-across-two-nvidia-dgx-stations-with-vllm "When One GPU Isn’t Enough: Serving GLM-5.3 Across Two NVIDIA DGX Stations with vLLM") · 未做

  介绍通过 RDMA 连接两台工作站，借助张量并行容纳大型 MoE 模型；区分激活参数量与完整权重的显存需求。

- **11-13** [SOMA Retargeter：将人体动作适配到机器人](https://developer.nvidia.com/blog/adapt-human-motion-for-robots-with-nvidia-soma-retargeter "Adapt Human Motion for Robots with NVIDIA SOMA Retargeter") · 未做

  介绍开源动作重定向工具，按机器人的比例、关节结构与活动范围调整人类动作，并为后续训练准备数据。

- **11-11** [AICR 与 AIBOM：核对 GPU 配置和实际运行的 AI 资产](https://developer.nvidia.com/blog/validating-gpu-platforms-with-runtime-ai-inventory-via-the-nvidia-dsx-ai-factory "Validating GPU Platforms with Runtime AI Inventory via the NVIDIA DSX AI Factory") · 未做

  将可复现的部署配方与运行时资产清单结合，追踪支持范围内的模型、依赖和工作负载；区分配置意图与实际观测。

- **11-10** [车载算力与延迟预算内运行自动驾驶推理模型](https://developer.nvidia.com/blog/running-av-reasoning-models-within-onboard-compute-and-latency-limits "Running AV Reasoning Models Within Onboard Compute and Latency Limits") · 未做

  讨论更大的推理模型如何适配车载系统的计算与实时性约束。

- **11-10** [用 NVIDIA Snapshot 秒级启动与恢复 GPU 工作负载](https://developer.nvidia.com/blog/start-and-restore-gpu-workloads-in-seconds-with-nvidia-snapshot "Start and Restore GPU Workloads in Seconds with NVIDIA Snapshot") · 未做

  DSX AI Factory 平台的新开源组件，把已初始化的 GPU 工作负载做成可复用快照，缩短冷启动。

- **11-10** [Agent Substrate：面向大规模 Agent 的 Kubernetes 演进](https://developer.nvidia.com/blog/agent-substrate-advancing-kubernetes-for-agents-at-scale "Agent Substrate: Advancing Kubernetes for Agents at Scale") · 未做

  针对 Agent 大部分时间在等待人、工具或模型响应的特点，讨论 Kubernetes 运行方式的改造。

- **11-10** [NVKE 与 NVKR：管理 GPU 基础设施上的 Kubernetes](https://developer.nvidia.com/blog/manage-kubernetes-clusters-for-gpu-infrastructure-with-nvidia-kubernetes-engine "Manage Kubernetes Clusters for GPU Infrastructure with NVIDIA Kubernetes Engine") · 未做

  介绍两个公开预览的开源项目，围绕集群供给、租户隔离、升级与恢复构建受管 Kubernetes 服务。

- **11-09** [Holoscan 5：机械臂重力补偿与低延迟控制](https://developer.nvidia.com/blog/make-a-robot-arm-feel-weightless-with-nvidia-holoscan-5 "Make a Robot Arm Feel Weightless with NVIDIA Holoscan 5") · 未做

  以读取关节状态、计算补偿力矩、发送指令三个算子搭建控制环，说明队列、线程划分、看门狗及延迟和抖动测量。

- **11-06** [在 Blackwell GPU 上加速 FLUX 3 Image Klein](https://developer.nvidia.com/blog/speed-up-image-generation-with-flux-3-image-klein-on-nvidia-blackwell-gpus "Speed Up Image Generation with FLUX 3 Image Klein on NVIDIA Blackwell GPUs") · 未做

  围绕设计工具与图像编辑中的生成等待，介绍扩散模型部署和推理延迟优化。

- **11-06** [Reshard：加快强化学习中的权重同步](https://developer.nvidia.com/blog/accelerating-reinforcement-learning-weight-refit-with-the-reshard-collective "Accelerating Reinforcement Learning Weight Refit with the Reshard Collective") · 未做

  说明训练与推理使用不同并行布局时，如何重新分片并传输模型权重，以支持分离式 RL 后训练。

- **11-05** [NVIDIA DSX OS：配置、验证与运维 GPU 集群](https://developer.nvidia.com/blog/configure-certify-and-operate-kubernetes-gpu-clusters-with-nvidia-dsx-os "Configure, Certify, and Operate Kubernetes GPU Clusters with NVIDIA DSX OS") · 未做

  讨论 GPU 集群的环境一致性与性能就绪检查，关注分布式训练中单个异常节点带来的影响。

- **11-05** [让每字节显存更有用：NVIDIA 的软硬件协同](https://developer.nvidia.com/blog/five-ways-nvidia-co-design-maximizes-the-value-of-every-byte-in-the-ai-factory "Five Ways NVIDIA Co-Design Maximizes the Value of Every Byte in the AI Factory") · 未做

  从低精度权重、KV Cache 到上下文存储，讨论推理服务怎样减少冗余占用和重复计算；性能数字需结合其测试条件。

- **11-04** [NVIDIA 如何把 Agent 用进 AI 集群运维](https://developer.nvidia.com/blog/how-nvidia-uses-ai-agents-to-streamline-ai-factory-operations "How NVIDIA Uses AI Agents to Streamline AI Factory Operations") · 未做

  介绍将计算、网络、硬件和调度信息组织到运维工作流中，帮助工程师调查跨系统问题。

- **11-04** [CUDA 13.5：Vera Rubin 正式支持与开发更新](https://developer.nvidia.com/blog/nvidia-cuda-13-5-brings-nvidia-vera-rubin-ga-support "NVIDIA CUDA 13.5 Brings NVIDIA Vera Rubin GA Support") · 未做

  梳理新一代硬件支持及 CUDA 开发能力的变化，适合关注 GPU 软件栈适配与迁移的读者。

- **11-04** [Factory Operations Blueprint：多 Agent 调查生产问题](https://developer.nvidia.com/blog/how-nvidia-factory-operations-blueprint-coordinates-ai-agents-to-investigate-production-issues "How NVIDIA Factory Operations Blueprint Coordinates AI Agents to Investigate Production Issues") · 未做

  介绍如何协调不同 Agent 收集证据、分析故障，并把分散的生产信息汇总成可追踪的调查过程。

- **11-04** [NVIDIA NeMo：把 Agent 失败变成测试与 Harness 修复](https://developer.nvidia.com/blog/use-nvidia-nemo-to-turn-agent-failures-into-tests-and-harness-fixes "Use NVIDIA NeMo to Turn Agent Failures into Tests and Harness Fixes") · 未做

  用轨迹定位问题、生成针对性评测，再修改指令并比较开发集与留出任务；示例覆盖工具、记忆、技能和控制流程。

- **11-02** [分布式训练的自动故障恢复](https://developer.nvidia.com/blog/keep-distributed-training-running-with-automated-workload-recovery "Keep Distributed Training Running with Automated Workload Recovery") · 未做

  讨论大规模训练中硬件与软件故障的影响，以及自动恢复工作负载的工程方法。

- **11-02** [让 Kubernetes 从第一天适配 Vera Rubin](https://developer.nvidia.com/blog/making-kubernetes-ai-ready-for-nvidia-vera-rubin-on-day-one "Making Kubernetes AI-Ready for NVIDIA Vera Rubin on Day One") · 未做

  介绍新 GPU 硬件对应的驱动、内核、运行时与网络配置，关注基础设施就绪与验证。

- **11-02** [用 NVIDIA Cosmos 构建交互式仿真世界模型](https://developer.nvidia.com/blog/build-world-models-for-interactive-simulation-with-nvidia-cosmos "Build World Models for Interactive Simulation with NVIDIA Cosmos") · 未做

  面向物理 AI 开发，讨论如何让世界模型适配传感器、任务和数据，并进入仿真应用。

- **11-02** [NVIDIA Attribution：为分布式 AI 故障寻找根因](https://developer.nvidia.com/blog/diagnose-distributed-ai-workload-failures-with-nvidia-attribution "Diagnose Distributed AI Workload Failures with NVIDIA Attribution") · 未做

  将任务日志、指标和调度状态关联起来，用可复现规则给出故障原因、受影响节点和证据路径。

- **11-02** [Workload Map：统一描述 Kubernetes 上的 AI 任务](https://developer.nvidia.com/blog/support-new-ai-frameworks-faster-using-nvidia-workload-map "Support New AI Frameworks Faster Using NVIDIA Workload Map") · 未做

  为不同训练与服务框架描述 Pod 组、角色和副本关系，减少调度器、控制器和观察工具重复编写适配逻辑。

</details>


<details>
<summary><strong>Hugging Face 与机构作者 · 19 篇</strong></summary>

- **11-13** [SimReady：搭建机械臂抓取与放置仿真](https://huggingface.co/blog/nvidia/simready-assets-robot-pick-and-place "Build a Robot Pick-and-Place Simulation with SimReady Assets") · 未做

  NVIDIA 团队用机器人、夹爪和饮料罐资产构建 Isaac Sim 场景，说明碰撞、质量、关节等仿真属性及验证步骤。

- **11-13** [XYBench：AI 能否识别提问背后的真正问题](https://huggingface.co/blog/allenai/xybench "XYBench: Helping with the problem behind the question") · 未做

  Ai2 团队评测助手面对错误前提或误选方案时的表现，检查它是否只回答表面问题，还是帮助用户重新识别目标。

- **11-13** [llama.cpp 1.0：为本地 AI 生态提供更稳定的基础](https://huggingface.co/blog/ggml-org/llama-cpp-v1 "llama.cpp v1.0.0 : A stronger foundation for the local AI ecosystem") · 未做

  项目团队介绍 1.0 版本面向下游集成的稳定性目标，以及跨硬件推理、量化与接口演进的方向。

- **11-12** [3D 生成模型微调指南](https://huggingface.co/blog/3d-lora-finetuning "The Definitive Fine-Tuning Guide for 3D Generation Models") · 未做

  面向 3D 生成模型的 LoRA 微调实操指南。

- **11-12** [LLMON：在 Granite 中显式区分指令、数据与工具内容](https://huggingface.co/blog/ibm-granite/llmon-an-llm-native-markup-language-now-in-granite "LLMON: An LLM-Native Markup Language, now in Granite 4.1 3B and 8B") · 未做

  IBM 团队介绍面向模型的上下文标记语言，讨论结构化训练、提示注入防护及小模型能力；防护效果仍受模型与任务条件限制。

- **11-11** [BotPsy：十亿参数以下的端侧个人助理](https://huggingface.co/blog/qvac/botpsy "BotPsy: On-Device Personal Assistant with a Sub-Billion-Parameter Agentic Language Model") · 未做

  qvac 介绍用不到十亿参数的 Agent 语言模型在设备上运行个人助理。

- **11-11** [面向多向量嵌入模型的 Token Pooling 感知训练](https://huggingface.co/blog/token-pooling "Token Pooling-Aware Training for Multi-Vector Embedding Models") · 未做

  介绍在训练阶段就考虑 token pooling 的多向量嵌入模型方法。

- **11-10** [Hugging Face 中的决策模型](https://huggingface.co/blog/decision "Decision Models in Hugging Face") · 未做

  介绍 HF 生态对决策模型的新支持。

- **11-09** [HOPE：考虑专家协作关系的 MoE 剪枝](https://huggingface.co/blog/amazon/higher-order-pruning-experts "Your Experts Have Partners. There&#x27;s HOPE for Keeping Them Together") · 未做

  Amazon 研究团队介绍二阶专家剪枝，将专家之间的相互作用纳入删除决策；文章给出校准方法、使用示例和作者实验结果。

- **11-09** [Nemotron-Personas-Finance-Japan：日本金融场景合成人物数据](https://huggingface.co/blog/nvidia/nemotron-personas-finance-japan "Nemotron-Personas-Finance-Japan: A Synthetic Dataset Capturing Japan&#x27;s Demographics and Financial Context") · 未做

  NVIDIA 与 Elith 介绍结合官方统计、概率图模型和文本生成的合成数据流程，用于金融 Agent 开发、用户模拟与评测。

- **11-06** [Open ASR 排行榜加入埃及与尼日利亚英语](https://huggingface.co/blog/open-asr-leaderboard-liva "Egyptian and Nigerian English join the Open ASR Leaderboard") · 未做

  补充不同口音的保留测试数据和分组结果，关注语音识别评测的代表性与数据泄漏问题。

- **11-06** [ToyBlocks：用可控积木世界研究机器人学习](https://huggingface.co/blog/allenai/toyblocks "ToyBlocks: A controlled world for robot learning and evaluation") · 未做

  Ai2 介绍自动生成任务和示范的仿真环境，让研究者改变数据与模型条件，再追踪机器人行为及失败原因。

- **11-05** [Cosmos 3：面向交互仿真的四组开放模型](https://huggingface.co/blog/nvidia/cosmos-interactive-world-simulation "New NVIDIA Cosmos 3 Open Models for Interactive World Simulation") · 未做

  介绍驾驶多传感器场景、仿真转视频和双臂机器人动作预测等模型；各检查点面向不同的世界模拟任务。

- **11-05** [Phonon TTS：在设备上运行的语音合成](https://huggingface.co/blog/phonon-tts "A Closer Look at Phonon TTS. Launching High-Quality On-Device Speech That Tops the Benchmarks.") · 未做

  回顾端侧语音模型的开放发布、定制声音与使用方式；不同规模模型的许可条件需分别核对。

- **11-04** [Dharma Field Extractor：按要求从文档提取 JSON 字段](https://huggingface.co/blog/Dharma-AI/dharma-field-extractor "Dharma Field Extractor: Any Document In, Structured Fields in JSON Out") · 未做

  介绍专门用于字段抽取的小模型，区分全文 OCR 与结构化业务数据提取；与大模型的对比为作者自测。

- **11-03** [StateBench：长文中的状态变化，模型能跟住吗？](https://huggingface.co/blog/allenai/statebench "StateBench: Testing how language models track state changes over long documents") · 未做

  Ai2 将状态跟踪分为四种复杂度，比较 Transformer、循环与混合架构；长上下文不等于能可靠追踪多步状态变化。

- **11-03** [Palette：让小模型按指定设计语言制作幻灯片](https://huggingface.co/blog/ibm-research/palette-deck-building "Palette: teaching a small model to build decks in your design language") · 未做

  IBM 介绍合成训练数据、规划与绘制分工，以及渲染检查的组合；评测成绩为作者自报。

- **11-03** [Transformers MIC：用小模型提前捕捉集成回归](https://huggingface.co/blog/transformers-mic "Transformers Model Integration Contracts") · 未做

  提出将缩小的模型 fixture、可运行用例和人工复核基线打包为集成契约，在 CPU 上更早发现回归。

- **11-03** [CWE-bench v2：更透明的安全漏洞修复评测](https://huggingface.co/blog/cwe-bench "CWE-bench v2: More coverage, quality, and transparency") · 未做

  开放程序化评分的真实仓库任务，检查 Agent 能否修复安全弱点并保留原有功能，同时保留未公开测试集。

</details>


<details>
<summary><strong>PyTorch · 7 篇</strong></summary>

- **11-12** [默认即快：Helion 内核的编译期启发式](https://pytorch.org/blog/fast-by-default-compile-time-heuristics-for-helion-kernels "Fast by Default: Compile-Time Heuristics for Helion Kernels") · 未做

  分析内核 IR 与数据流，按 matmul、reduction、pointwise 分类后直接选择快速配置，减少耗时的自动调优。

- **11-12** [一周内用 AI 把 SGLang 接入 IBM Spyre](https://pytorch.org/blog/integrating-sglang-into-spyre-in-under-a-week-with-ai "Integrating SGLang into Spyre in Under a Week with AI") · 未做

  两人团队借助 AI 编码 Agent 写出约 1500 行插件，把 SGLang 接到 IBM Spyre；过程细节以原文为准。

- **11-12** [在欧洲公共基础设施上训练 1T 参数 MoE](https://pytorch.org/blog/training-a-1t-parameter-moe-on-eu-public-infrastructure-with-pytorch-and-torchtitan "Training a 1T-Parameter MoE on EU public infrastructure with PyTorch and TorchTitan") · 未做

  介绍在共享公共超算上预训练约一万亿参数 MoE 模型时遇到的架构与互连瓶颈及应对。

- **11-10** [ExecuTorch WebGPU：浏览器 GPU 上运行 PyTorch 模型](https://pytorch.org/blog/executorch-webgpu-pytorch-models-on-the-gpu-in-the-browser "ExecuTorch WebGPU: PyTorch Models on the GPU, in the Browser") · 未做

  通过 torch.export 导出 .pte 文件，在浏览器 WebGPU 上推理，无需转换为其他框架格式。

- **11-10** [TPU v7 上用 SGLang-TorchTPU 服务 Muse Spark Open](https://pytorch.org/blog/optimizing-muse-spark-open-on-tpu-v7-with-sglang-torchtpu "Optimizing Muse Spark Open on TPU v7 with SGLang-TorchTPU") · 未做

  816B 参数 MoE 模型在单台四芯片 TPU v7 主机上的服务实践。

- **11-03** [KV Cache 技术交流回顾：CXL、调度与 LMCache](https://pytorch.org/blog/kvcache-meetup-korea-2026-event-recap "KVCache Meetup Korea 2026: Event Recap") · 未做

  整理 CXL 内存扩展、GPU/HBM 瓶颈、推理调度和 LMCache MP Mode 的技术分享；活动发生在 9 月，文章于 11 月发布。

- **11-02** [Ray 加速器 SIG：面向多种硬件的协作计划](https://pytorch.org/blog/announcing-the-special-interest-group-sig-for-ray-on-accelerators "Announcing the Special Interest Group (SIG) for Ray on Accelerators") · 未做

  介绍围绕 Ray 与硬件加速器成立的特别兴趣组；这是协作方向的公告，不代表所有硬件支持已经交付。

</details>


<details>
<summary><strong>Z.ai / 智谱 · 5 篇</strong></summary>

- **11-05** [金融 AI 从试用到日常：任务、数据与查错](https://autoclaw.z.ai/blog/news/autoclaw-finance-observation-01-agent-cluster-earnings-review "AI in Finance Pilot to Daily Use: 3 Deciding Conditions") · 未做

  从金融工作流讨论清晰的任务、真实资料和可见错误如何影响日常使用；这是产品团队的实践分析。

- **11-04** [AutoClaw 多 Agent 研究：规划、分工与复核](https://autoclaw.z.ai/blog/product/autoclaw-agent-cluster-multi-agent-research "Multi-Agent Research with AutoClaw: Plan, Divide, and Review") · 未做

  介绍怎样为并行研究设定一致的比较维度，按依赖关系组织汇总与复核；更多 Agent 不自动等于更好的报告。

- **11-03** [AutoClaw Goal Mode：用交付证据推进多步骤任务](https://autoclaw.z.ai/blog/product/autoclaw-goal-mode-multi-step-tasks "How to Use AutoClaw Goal Mode for Multi-Step Tasks") · 未做

  说明如何定义可验证的目标，将执行与评估分开，并检查文件、来源或实际交互等完成证据。

- **11-03** [AutoClaw 定时任务：明确时间、动作与交付位置](https://autoclaw.z.ai/blog/product/autoclaw-scheduled-tasks-reminders-recurring-work "How to Schedule AI Tasks with AutoClaw") · 未做

  介绍一次性提醒与周期工作如何设置、核对和维护，强调时区、来源范围、输出格式与接收位置。

- **11-02** [AutoClaw Design：把产品简报变成可编辑界面](https://autoclaw.z.ai/blog/product/product-brief-to-ui-design-with-autoclaw "How to Turn a Product Brief into an Editable UI with AutoClaw") · 未做

  从明确用户任务和交互状态开始，介绍界面生成、局部修订、跨设备预览与交付检查。

</details>

<details>
<summary><strong>Cloudflare AI · 4 篇</strong></summary>

- **11-13** [Kitesurf 开源：运行在 Workers 上的 Agent 浏览器](https://blog.cloudflare.com/kitesurf-open-source "Kitesurf is now open source") · 未做

  介绍基于 Rust 与 WebAssembly 的实验性浏览器引擎，支持页面脚本、截图和 CDP，可本地运行或部署到自有 Workers。

- **11-13** [面对 AI 自动化渗透测试：更新防御与资产管理](https://blog.cloudflare.com/adapting-to-ai-penetration-testing-orchestrators "Adapting to AI penetration testing orchestrators: The Modern Security Model") · 未做

  汇总对 AI 安全测试编排流量的观测，从暴露面、运行时防护与持续修复讨论应对方式；规模统计为 Cloudflare 的平台观测。

- **11-05** [Agent 代表人访问网站，身份该如何传递？](https://blog.cloudflare.com/trusted-agent-delegation "Agents aren’t humans (but they kinda are)") · 未做

  讨论代理请求中用户身份与授权信息的丢失，提出网站、用户和 Agent 服务之间的可信委托思路。

- **11-04** [识别个人 Agent 流量，并设定访问规则](https://blog.cloudflare.com/personal-agents-visibility-control "See the agents, set the terms: new visibility and control for personal agents") · 未做

  介绍站点如何观察个人 Agent 的访问，并为自动化请求设置控制；重点是区分请求身份与访问许可。

</details>

<details>
<summary><strong>Microsoft Research · 2 篇</strong></summary>

- **11-10** [Lazarus：重编程休眠神经元给 AI Agent 植入后门](https://www.microsoft.com/en-us/research/blog/lazare-veni-foras-reprogramming-dormant-neurons-to-backdoor-ai-agents "Lazare, veni foras: Reprogramming Dormant Neurons to Backdoor AI Agents") · 未做

  安全研究：通过重编程模型中的休眠神经元，让 Agent 在隐藏触发条件下执行恶意命令；重点看威胁场景与防御含义。

- **11-05** [PDD Kit：验证 Agent 写出的代码是否符合意图](https://www.microsoft.com/en-us/research/blog/formally-verifying-agent-written-full-stack-web-apps-with-pdd-kit "Formally verifying agent-written full-stack web apps with PDD Kit") · 未做

  将开发者意图变成 Verus 规格，对可覆盖的逻辑做形式化证明，其余部分用测试；示例验证的是登录逻辑对规格的符合性。

</details>

<details>
<summary><strong>vLLM · 9 篇 · 1 篇已学习</strong></summary>

- **11-12** [DeepSeek-V4.1-Flash 在 Vera Rubin NVL72：58 倍吞吐](https://vllm.ai/blog/2026-11-12-deepseek-v41-flash-vera-rubin "DeepSeek-V4.1-Flash on Vera Rubin NVL72: 58x Throughput vs. GB300 NVL72 at 387 tokens/s") · **已学习**
  [深度解析](../../ai-learning/reports/knowledge_reports/vLLM_Vera_Rubin_NVL72_58x吞吐与机架级内存池_深度解析_20261113.md)：SM107 内核重写 / TP8 低延迟 / 机架级内存池；"58×"口径辨析（直接相除 1.78×）。

  报告新机架上以 AgentX 负载测得的吞吐与单用户延迟；性能数字为官方配置下的结果。

- **11-12** [vLLM 首日支持 Inkling 2 Small](https://vllm.ai/blog/2026-11-12-inkling2-small "Inkling 2 Small on vLLM: Day-0 Support") · 未做

  介绍 Thinking Machines 新模型的当天适配，包括注意力残差、相对偏置注意力解码内核与投机解码支持。

- **11-12** [H3-Image 首日支持：Vera Rubin 上 0.87 秒生成 4K](https://vllm.ai/blog/2026-11-12-minimax-h3-image-rubin "H3-Image Day-0 Support: 4K in 0.87s with Vera Rubin") · 未做

  MiniMax 图像模型在 vLLM 的当天支持，给出 4K 生成速度与吞吐数字；收益测算为作者口径。

- **11-11** [编码器分离：用 EPD 扩展多模态服务](https://vllm.ai/blog/2026-11-11-encoder-disaggregation-epd "Encoder Disaggregation in vLLM: Scaling Multimodal Serving with EPD") · 未做

  介绍 vLLM 编码器解耦的新进展：仅元数据的多模态请求、专用编码器执行、远程嵌入传输与跨编码器缓存。

- **11-06** [零数值偏差与异步 RL：校正旧策略产生的样本](https://vllm.ai/blog/2026-11-06-zero-mismatch-async-rl "Zero Mismatch, Simple Async RL: REINFORCE Zero, DeepSeek-V4.1 and Kimi K3.1") · 未做

  讨论逐位对齐 rollout 与训练内核，并用重要性采样处理异步训练中的策略滞后；介绍相关模型与硬件适配。

- **11-06** [vLLM 迁移到 LibTorch Stable ABI](https://vllm.ai/blog/2026-11-06-stable-abi-cuda "Migrating vLLM to the LibTorch Stable ABI") · 未做

  介绍 CUDA 构建及编译依赖的迁移，目标是让兼容的 PyTorch 升级不再要求重新构建 vLLM。

- **11-06** [VeRL-Omni 0.3：异步训练与多模态后训练](https://vllm.ai/blog/2026-11-06-verl-omni-v0-3-0 "VeRL-Omni v0.3.0: Async Training and Broader Multimodal Post-Training") · 未做

  介绍异步 RL、默认 V1 训练器，以及覆盖图像、视频、音频和多模态理解的训练配方。

- **11-04** [vLLM 对 Kimi K3.1 Pro 的首日支持](https://vllm.ai/blog/2026-11-04-kimi-k31-pro "vLLM Delivers Day-0 Support for Kimi K3.1 Pro") · 未做

  介绍混合架构的稀疏注意力、压缩 KV Cache、上下文并行和低延迟解码；这是服务引擎适配文章。

- **11-04** [Kinference：vLLM 与 Kubernetes 的推理控制面](https://vllm.ai/blog/2026-11-04-introducing-kinference "Introducing Kinference: An Open Source Inference Control Plane for vLLM and Kubernetes") · 未做

  面向多租户推理平台，介绍 Token 限流、用量与成本统计、负载均衡及推理策略管理。

</details>

<details>
<summary><strong>腾讯混元 · 2 篇</strong></summary>

- **11-04** [Hy4：视觉、Computer Use 与长流程任务](https://hy.tencent.ai/research/hy4 "Introducing Hy4 - Tencent Hy") · 未做

  官方介绍相较 preview 的训练扩展，以及视觉理解、跨应用操作、研究与个人助理工作流；效果为厂商自报。

- **11-01** [Hyra 2.0：从反复解题转向改进研究工具](https://hy.tencent.ai/research/hyra2 "Hyra 2.0: The Next Step for Auto Research") · 未做

  介绍让通用 Agent 开发和改善科学模型、研究工作流及软件工具，以便把一次研究投入复用到后续任务。

</details>

<details>
<summary><strong>Apple 机器学习研究 · 5 篇</strong></summary>

- **11-12** [语言模型对齐的理论极限](https://machinelearning.apple.com/research/theoretical-limits-alignment "Theoretical Limits of Language Model Alignment") · 未做

  从理论角度讨论强化学习等对齐方法在改进输出与保留基座能力之间的边界。

- **11-10** [加权状态汤：高效长上下文检索](https://machinelearning.apple.com/research/weighted-state-souping "Weighted State Souping for Efficient Long-Context Retrieval") · 未做

  NeurIPS 2026 PALM 工作坊论文，研究状态空间模型的状态混合（souping）方法如何改善长上下文检索。

- **11-10** [评测评测者：LLM 评委与个性化写作风格](https://machinelearning.apple.com/research/evaluating-evaluators-llm-judges "Evaluating the Evaluators: Investigating LLM Judges for Personalized Writing Style Assessment") · 未做

  NeurIPS 2026「能否信任 AI 评测」工作坊论文，检查 LLM 评委在个性化写作风格评估中的可靠性。

- **11-10** [门控为什么重要：SSM 的记忆与上下文学习](https://machinelearning.apple.com/research/gating-memorization-in-context "On the Importance of Gating: Memorization vs. In-Context Learning in State Space Models") · 未做

  分析状态空间模型中门控机制对记忆与上下文学习的影响。

- **11-05** [更快的检索如何支持更高效的 RAG](https://machinelearning.apple.com/research/faster-retrieval "Faster Retrieval for Better, More Efficient RAG") · 未做

  从最大内积搜索入手，讨论检索查询与文档向量分布的差异，以及如何利用查询特征改善检索效率。

</details>

<details>
<summary><strong>GitHub AI &amp; ML · 2 篇</strong></summary>

- **11-12** [Agent Skills 实践指南：一次构建、任意 Agent 运行](https://github.blog/ai-and-ml/github-copilot/build-once-run-on-any-agent-a-practical-guide-to-agent-skills "Build once, run on any agent: A practical guide to agent skills") · 未做

  讨论把可复用的工程工作写成文件化的 agent skills，工具、项目上下文与权限仍由运行环境决定。

- **11-06** [Agentic Engineering：从生成代码到完整开发流程](https://github.blog/ai-and-ml/github-copilot/beyond-code-generation-a-developers-guide-to-agentic-engineering "Beyond code generation: A developer’s guide to agentic engineering") · 未做

  围绕规划、编码、审查和生产问题调查展开，说明开发者如何组织 Agent 工作，以及哪些判断仍需自己承担。

</details>

<details>
<summary><strong>Amazon Science · 3 篇</strong></summary>

- **11-11** [Tiros：用自动推理验证云网络隔离](https://www.amazon.science/blog/using-mathematics-to-validate-network-configurations "Using mathematics to validate network configurations") · 未做

  将路由表和网络策略转换为逻辑命题，静态检查可达路径是否符合隔离要求；证明针对建模后的配置，不代替对整个系统的安全审计。

- **11-10** [Mitra-v2：表格基础模型的合成预训练扩展](https://www.amazon.science/blog/mitra-v2-scaling-synthetic-pretraining-for-tabular-foundation-models "Mitra-v2: Scaling synthetic pretraining for tabular foundation models") · 未做

  扩大合成数据配比训练表格基础模型，使其不训新模型即可适配新表格；基准成绩为作者自报。

- **11-05** [回顾 Polyak–Łojasiewicz 条件与梯度法收敛](https://www.amazon.science/blog/hamed-karimi-wins-ecml-pkdd-test-of-time-award "Hamed Karimi wins ECML PKDD Test-of-Time Award") · 未做

  借论文获奖回顾不依赖强凸性的线性收敛分析及其影响；讨论对象是既有优化理论，并非本周提出的新算法。

</details>

<details>
<summary><strong>Anthropic · 8 篇 · 1 篇已学习</strong></summary>

- **11-13** [怎样构建可靠的 AI 安全评测](https://www.anthropic.com/research/building-strong-safety-evaluations "Building strong safety evaluations") · 未做

  从场景设计、多轮交互、裁判校准到预注册和统计报告，说明安全评测如何更贴近风险问题，并让结果可复现。

- **11-09** [Claude Fable 5.2 与 Mythos 5.2：技术任务与安全评测](https://www.anthropic.com/claude-fable-and-mythos-5-2 "Introducing Claude Fable 5.2 and Claude Mythos 5.2") · 未做

  介绍编程、推理、视觉和科学任务的能力变化，以及两个版本的访问与防护差异；性能、安全性和案例结果均为官方报告。

- **11-09** [Claude 电子设计：从电路、PCB 到实物原型](https://www.anthropic.com/research/claude-electronics-design "Testing Claude on real-world electronics design") · 未做

  报告与 Diode 合作设计三种设备的实验，讨论几何推理、布局布线、固件和制造约束；长期可靠性与商业认证仍未验证。

- **11-06** [Agent 记忆的组成：记录、整理与纠错](https://www.anthropic.com/research/components-of-agent-memory "The components of agent memory") · **已学习**

  将运行中捕获经历与离线整理记忆分开，介绍通过 dreaming 反思日志、纠正错误并形成可复用记忆的设计。 [阅读报告](../ai-learning/reports/knowledge_reports/Anthropic_Agent记忆组件_显著性判断与Dreaming_深度解析_20261108.md)

- **11-06** [让 AI 参与科学模型的构建与解释](https://www.anthropic.com/research/teaching-ai-to-build-scientific-models "Teaching AI to build scientific models") · 未做

  研究者讨论从科学假设、模型构造到结果解释的变化，关注 AI 怎样进入科学建模过程及其局限。

- **11-05** [研究者怎样使用 Claude 做科学工作](https://www.anthropic.com/research/how-researchers-use-claude "AI for scientific discovery: How researchers use Claude") · 未做

  基于研究会话分析不同学科与任务的使用分布，区分数据分析、写作、提出想法和采集数据等环节。

- **11-04** [Claude 参与 vault 蛋白颗粒结构研究](https://www.anthropic.com/research/investigating-vault-particles-with-claude "Investigating vault particles with Claude") · 未做

  介绍从序列文献检索、分离方法优化到结构解析的研究流程；这是官方实验室披露的阶段性结果。

- **11-02** [FlashProve：证明模型回答来自指定推理计算](https://www.anthropic.com/research/provable-inference "Progress on provable inference for large language models") · 未做

  讨论以 zkSNARK 构建可验证推理，使用户能检查响应是否来自承诺的模型；密码学保证与系统成本需一起看。

</details>

<details>
<summary><strong>Mistral AI · 1 篇</strong></summary>

- **11-05** [Mistral Studio：企业 Agent、工作流与上下文](https://mistral.ai/news/build-with-studio "Le Chonk brings the brains. Studio gets it working.") · 未做

  介绍受管 Agent、应用、企业上下文和可观测性，支持在云、VPC 或本地基础设施中部署企业工作流。

</details>

<details>
<summary><strong>Google Developers · 2 篇</strong></summary>

- **11-06** [Agent 注意力偏移：旧 TODO 怎样让任务跑偏](https://developers.googleblog.com/agent-distraction "Agent Distraction") · 未做

  通过代码中的 TODO 与工单状态分析无关调查、过期问题和任务范围扩张，讨论清理上下文噪声的价值。

- **11-03** [按任务成本路由：选择 Gemini 模型与思考深度](https://developers.googleblog.com/cost-per-task-using-cheap-classifiers-to-route-across-gemini-models-and-thinking-levels "Cost per task: Using cheap classifiers to route across Gemini models and thinking levels") · 未做

  讨论用低成本分类器为任务选择模型和思考配置，并从任务效果与总成本衡量路由策略。

</details>

<details>
<summary><strong>MiniMax · 1 篇</strong></summary>

- **11-11** [MiniMax H3-Image：开放权重的图像生成与编辑](https://www.minimax.io/blog/minimax-h3-image "Bringing 4K Image Generation into the 10-Second Era") · 未做

  介绍文生图、多参考图与图像编辑能力，以及后训练和采样优化；4K 生成速度与质量为官方自报，日期按原页显示。

</details>

<details>
<summary><strong>OpenAI Developers · 3 篇 · 1 篇已学习</strong></summary>

- **11-12** [常驻 Agent 的安全：控制面、沙箱与身份隔离](https://developers.openai.com/blog/securing-persistent-agents-like-openclaw-at-openai "Securing persistent agents like OpenClaw at OpenAI") · **已学习**

  介绍如何把可信控制面与 Agent 执行环境分开，结合 Codex 沙箱、自动审查、独立身份与可观测性，限制长期运行 Agent 的权限。 [阅读报告](../ai-learning/reports/knowledge_reports/常驻Agent安全_控制面隔离与权限交集_深度解析_20261115.md)

- **11-10** [四个 GPT-Live 案例：语音交互、任务委托与评测](https://developers.openai.com/blog/pushing-voice-agents-further "Pushing voice agents further: inside four GPT-Live builds") · 未做

  汇集 Juno、Picsart、Treater 和 Weekend 的开发经验，讨论实时对话中的任务分工、语音提示与实际交互评测。

- **11-09** [Codex × ModRetro：从游戏创意到复古掌机](https://developers.openai.com/blog/build-a-game-with-modretro-chromatic "Building a retro handheld game with Codex and ModRetro") · 未做

  介绍通过 Codex 插件开发掌机游戏的流程，将代码生成、构建和实际设备体验串联起来。

</details>

[回到顶部](#顶尖技术博客更新)

<a id="m202610"></a>

## 2026 年 10 月

<details>
<summary><strong>OpenAI Developers · 2 篇 · 1 篇已学习</strong></summary>

- **10-14** [OpenAI 多供应商故障切换](https://developers.openai.com/blog/designing-failover-across-openai-model-providers "Designing failover across OpenAI model providers") · 未做  
  介绍模型服务切换的设计，以及预览模型和关键业务对直连能力的要求。

- **10-14** [GPT-6 如何维护大型代码库](https://developers.openai.com/blog/maintaining-software-with-the-gpt-6-family "Maintaining software with the GPT-6 family") · **已学习**  
  从删除无用代码、清理旧实验到改善 CI，介绍 Codex 的实际维护流程。 [阅读报告](../ai-learning/reports/knowledge_reports/GPT6软件维护_从广义侦察到证据驱动清理_深度解析_20261020.md)

</details>

<details>
<summary><strong>OpenAI 研究与技术更新 · 8 篇 · 3 篇已学习</strong></summary>

- **10-30** [ChatGPT 社区安全报告与青少年保护](https://openai.com/index/community-safety-report-and-new-protections-for-teens "Community safety report and new protections for teens") · 未做  
  介绍安全保护的更新及相关使用情况；适合关注产品安全机制的读者。

- **10-27** [Check Point 用 Daybreak 做漏洞研究](https://openai.com/index/check-point-daybreak "How Check Point accelerates vulnerability research with Daybreak") · 未做  
  安全团队如何把 AI 放进漏洞发现与分析流程，是这篇案例的重点。

- **10-26** [CodeRabbit 用 GPT-6.1 Sol 检查代码安全](https://openai.com/index/gpt-6-1-sol-coderabbit-code-security "GPT-6.1 Sol helps CodeRabbit strengthen security across complex codebases") · 未做  
  关注复杂代码库里的安全审查，以及模型如何参与这一工作。

- **10-23** [ChatGPT 十亿用户存储架构：下篇](https://openai.com/index/scaling-storage-one-billion-users-part-two "Rapidly scaling online storage to serve over 1 billion ChatGPT users (Part II)") · **已学习**  
  延续上篇，讨论在线存储扩容、多租户管理与可靠性。 [阅读报告](../ai-learning/reports/knowledge_reports/OpenAI_十亿用户在线存储_CosmosDB多租户与可靠性_深度解析_20261025.md)

- **10-22** [Decisions API：让应用更快作出响应](https://openai.com/index/decisions-api "Build more responsive apps with the Decisions API") · **已学习**  
  介绍低延迟决策接口的调用方式、使用场景与能力边界。 [阅读报告](../ai-learning/reports/knowledge_reports/OpenAI_Decisions_API_低延迟决策与响应式应用_深度解析_20261025.md)

- **10-21** [让数千个 Agent 并行分析生物数据](https://openai.com/index/scaling-ai-research-for-complex-biological-data "Using thousands of AI agents to uncover new leads in biological data") · **已学习**  
  看并行研究如何汇总证据、筛选线索，以及科学发现如何验证。 [阅读报告](../ai-learning/reports/knowledge_reports/OpenAI_千Agent并行生物数据研究_证据聚合与科学发现_深度解析_20261025.md)

- **10-14** [一万个 Agent 连续运行的研究案例](https://openai.com/index/third-moment-research "How Third Moment Research runs 10,000 agents for 36+ hours") · 未做  
  Third Moment Research 介绍大规模、长时间 Agent 工作的组织方式。

- **10-08** [LegalOn 如何降低 Codex 使用成本](https://openai.com/index/legalon-halves-codex-costs "LegalOn halves Codex costs while maintaining development speed") · 未做  
  围绕开发速度与费用的取舍，介绍团队的使用调整；成效为案例方自报。

</details>

<details>
<summary><strong>Anthropic · 13 篇</strong></summary>

- **10-27** [AI Agent 会怎样影响专家判断](https://www.anthropic.com/research/agents-judgment-calls "How AI agents shape experts’ judgment calls") · 未做  
  研究专家与 Agent 协作时，建议如何改变人的判断过程。

- **10-27** [Claude 辅助药物开发的早期进展](https://www.anthropic.com/research/early-progress-drug-development "Early progress on accelerating drug development with Claude") · 未做  
  展示药物研究中的应用与限制，区分候选线索和已验证成果。

- **10-23** [英国 AISI 网络测试事件的对齐分析](https://www.anthropic.com/research/alignment-assessment-ukaisi "An alignment assessment of the UK AISI cybertesting incident") · 未做  
  通过具体事件分析模型行为，适合观察安全评估怎样处理异常证据。

- **10-20** [Claude 设计蝎毒蛋白结合物](https://www.anthropic.com/research/claude-scorpion-toxin-binder-design "How Claude designed protein binders against scorpion neurotoxins") · 未做  
  从设计候选分子到实验验证，介绍 AI 参与生物研究的过程。

- **10-16** [公众和 AI 从业者的预期为何不同](https://www.anthropic.com/research/ai-expectations-gap "The AI expectations gap") · 未做  
  比较双方对 AI、就业和经济影响的看法，关注调查证据与分歧来源。

- **10-16** [用 Claude 设计更高效的量子电路](https://www.anthropic.com/research/designing-efficient-quantum-circuits "Designing more efficient quantum circuits with Claude") · 未做  
  观察模型如何参与电路设计，以及优化结果怎样被检验。

- **10-16** [Anthropic 内部的岗位和工作怎样变化](https://www.anthropic.com/research/employment-at-anthropic "How employment is changing at Anthropic") · 未做  
  研究 AI 使用对工作组织、招聘与劳动需求的影响。

- **10-16** [在 AI 前沿工作，会改变哪些预期](https://www.anthropic.com/research/expectations-for-the-future "Working at the frontier shapes expectations for the future") · 未做  
  汇总公司内部就业变化和公众预期差异两项研究。

- **10-13** [Anthropic 重新设计版本管理](https://www.anthropic.com/research/redesigning-source-control "Redesigning source control at Anthropic") · 未做  
  讨论源代码管理怎样适应新的开发方式，适合关注多人、多 Agent 协作。

- **10-12** [小模型能否在廉价设备上自我复制](https://www.anthropic.com/research/self-replicating-ai "AI models may be capable of self-replicating without access to a datacenter") · 未做  
  研究不依赖数据中心的复制能力与风险，重点看实验条件和限制。

- **10-09** [排查模型在评测中的意外行为](https://www.anthropic.com/research/investigating-unintended-model-actions "Investigating unintended model actions in our evaluations and internal use") · 未做  
  披露评测和内部使用中的异常动作，以及团队如何调查这些现象。

- **10-08** [Claude 与缺失的天空地图](https://www.anthropic.com/research/the-missing-map-of-the-sky "The missing map of the sky") · 未做  
  以天文研究为案例，观察模型参与科学问题分析的方式。

- **10-01** [Claude 正在怎样改变科学研究](https://www.anthropic.com/research/claude-shaped-science "Claude-shaped science") · 未做  
  从科学应用的实际材料出发，讨论研究流程中正在发生的变化。

</details>

<details>
<summary><strong>Google Research · 9 篇 · 2 篇已学习</strong></summary>

- **10-21** [用 AI 辅助基层产科超声检查](https://research.google/blog/empowering-frontline-maternal-care-with-ai-assisted-ultrasound "Empowering frontline maternal care with AI-assisted ultrasound") · 未做  
  研究如何让低成本设备和非超声专科操作者获得更有用的检查结果。

- **10-16** [自主湿实验室：让 Agent 接受现实检验](https://research.google/blog/grounding-ai-agents-in-biological-reality-building-blocks-for-autonomous-wet-labs "Grounding AI agents in biological reality: Building blocks for autonomous wet labs") · **已学习**  
  把模型规划、实验执行与测量反馈连起来，解释生物实验为何不能只靠文字推理。 [阅读报告](../ai-learning/reports/knowledge_reports/Google_自主湿实验室Agent_生物现实约束与闭环_深度解析_20261021.md)

- **10-14** [Deep Review：分段核验长文和技术材料](https://research.google/blog/analyzing-technical-documents-with-deep-review "Analyzing technical documents with Deep Review") · **已学习**  
  解释分段、推理预算分配、并行检查与整体复核如何配合。 [阅读报告](../ai-learning/reports/paper_analyses/50_paper_assistant_tool_deep_review_2026.md)

- **10-14** [Earth AI：面向地理问题的 Agent](https://research.google/blog/putting-earth-ai-to-work-geospatial-agents-for-our-planets-biggest-challenges "Putting Earth AI to work: Geospatial agents for our planet&#x27;s biggest challenges") · 未做  
  把遥感等模型和多步骤工作流结合，用于分析真实世界的地理问题。

- **10-14** [Google Research 2026 研究进展总览](https://research.google/blog/research-2026-10-ways-were-amplifying-human-ingenuity "Research@ 2026: 10 ways we&#x27;re amplifying human ingenuity") · 未做  
  汇总科学、健康与生成式 AI 的代表方向，适合先建立主题地图。

- **10-07** [AI 让作品变好，也会让人变强吗](https://research.google/blog/does-better-work-always-mean-better-workers "Does better work always mean better workers?") · 未做  
  区分工作产出质量与人的判断能力，关注使用 AI 对学习过程的影响。

- **10-06** [用地理基础模型分析公共健康](https://research.google/blog/earth-ais-planetary-geospatial-foundation-models-for-global-public-health "Unlocking Earth AI’s planetary geospatial foundation models for global public health") · 未做  
  介绍 Earth AI 的地理数据表示如何用于疾病和公共健康问题。

- **10-05** [从上下文看 Agent 的隐私与安全](https://research.google/blog/open-and-emergent-problems-in-agentic-privacy-and-security-a-contextual-angle "Open and Emergent Problems in Agentic Privacy and Security: A Contextual Angle") · 未做  
  把用户、任务和环境一起纳入分析，讨论 Agent 带来的新型信息边界问题。

- **10-02** [让联邦学习的隐私保证可证明](https://research.google/blog/toward-provably-private-learning-from-federated-data "Toward provably private learning from federated data") · 未做  
  讨论分散数据上的学习机制，以及隐私、实用性和系统实现的取舍。

</details>

<details>
<summary><strong>Google DeepMind · 9 篇</strong></summary>

- **10-30** [用 AI 加快规划审批：DeepMind 与英国政府的合作](https://deepmind.google/blog/speeding-up-planning-decisions-with-ai "Speeding up planning decisions with AI") · 未做

  介绍 AI 在规划审批评估中的应用，关注如何辅助行政流程，而不是把规划理解为 Agent 的任务规划。

- **10-28** [Gemini 4 Carbon 发布](https://deepmind.google/blog/gemini-4-carbon-our-next-frontier-model "Gemini 4 Carbon: Our next frontier model") · 未做  
  介绍新模型的综合能力与官方评测，适合和其他前沿模型横向比较。

- **10-27** [Genie 4：新一代世界模拟](https://deepmind.google/blog/genie-4-a-new-generation-of-world-simulation "Genie 4: A new generation of world simulation") · 未做  
  聚焦可交互世界生成，关注控制方式、连续性和模型限制。

- **10-22** [从树木覆盖率到全球森林类型图](https://deepmind.google/blog/beyond-tree-cover-mapping-the-worlds-forest-types "Beyond tree cover: mapping the world’s forest types") · 未做  
  用 AI 区分不同森林类型，为生态与环境分析提供更细的地图。

- **10-15** [用 Antigravity 加速抗菌肽搜索](https://deepmind.google/blog/accelerating-antimicrobial-discovery "Accelerating the search for antimicrobial peptides with Google Antigravity") · 未做  
  观察 AI 工具怎样参与候选搜索和科学研究流程。

- **10-13** [Gemini 4 Argon 的安全开发过程](https://deepmind.google/blog/developing-gemini-4-argon-responsibly-and-safely "Developing Gemini 4 Argon responsibly and safely") · 未做  
  介绍模型发布对应的风险评估、防护措施与责任边界。

- **10-13** [Gemini 4 Argon 用于机器人](https://deepmind.google/blog/gemini-4-argon-for-robotics "Gemini 4 Argon for Robotics") · 未做  
  关注模型能力怎样连接感知、决策和机器人任务。

- **10-13** [Gemini 4 Argon 的复杂问题能力](https://deepmind.google/blog/introducing-gemini-4-argon "Gemini 4 Argon: Built to solve your hardest problems") · 未做  
  介绍模型在难题上的能力与官方测试，配合安全说明阅读更完整。

- **10-06** [EmbeddingGemma 2：轻量多模态嵌入](https://deepmind.google/blog/embeddinggemma-2-an-open-lightweight-multimodal-embedding-model "EmbeddingGemma 2: an open, lightweight multimodal embedding model") · 未做  
  面向语义检索等应用，介绍开放嵌入模型的输入类型与部署方向。

</details>

<details>
<summary><strong>Google Developers · 13 篇 · 2 篇已学习</strong></summary>

- **10-22** [可治理、可持续改进的 Google Cloud Agent](https://developers.googleblog.com/architecting-governed-self-evolving-ai-agents-on-gemini-agent-platform "Architecting Governed, Self-Evolving AI Agents on Google Cloud") · 未做  
  介绍模型、执行流程和治理机制如何共同组成可维护的 Agent 系统。

- **10-22** [API Gateway 支持流式响应](https://developers.googleblog.com/streaming-comes-to-api-gateway-real-time-and-ai-ready-apis-without-changing-your-spec "Streaming comes to API Gateway: real-time and AI-ready APIs, without changing your spec") · **已学习**\
  作为 Agent 请求全链路的续篇，讲清逐字输出、工具执行与断线恢复；结合 Google 网关边界和本地流式实验。 [阅读报告](../ai-learning/reports/knowledge_reports/Agent请求全链路_流式响应与断线恢复_科普讲解_20261102.md)

- **10-21** [跨框架管理 Agent 开发生命周期](https://developers.googleblog.com/powering-the-agent-development-lifecycle-with-any-framework-from-adk-to-langchain-and-beyond "Powering the Agent Development Lifecycle with any framework") · 未做  
  连接 ADK、LangChain 等框架，关注开发、评测与上线流程。

- **10-20** [TPU 上的 vLLM 与 SGLang 新推理引擎](https://developers.googleblog.com/announcing-new-vllm-and-sglang-inference-engines-on-tpu "Announcing New vLLM and SGLang Inference Engines on TPU") · **已学习**  
  介绍 TorchTPU 路线及各引擎的支持范围、能力差异与部署条件。 [阅读报告](../ai-learning/reports/knowledge_reports/Google_TPU_vLLM_SGLang_TorchTPU推理引擎_能力矩阵与口径核验_深度解析_20261025.md)

- **10-20** [Coral NPU：让端侧 AI 更容易迁移](https://developers.googleblog.com/unifying-edge-ai-how-coral-npus-open-standard-brings-portable-energy-viable-intelligence-from-model-to-silicon "Unifying Edge AI: How Coral NPU’s open standard brings portable, energy-viable intelligence from model to silicon") · 未做  
  讨论从模型到芯片的开放标准，以及功耗和可移植性的取舍。

- **10-19** [LiteRT Tensor API：直接编写端侧模型](https://developers.googleblog.com/native-model-authoring-for-edge-with-litert-tensor-api "Native Model Authoring for Edge with LiteRT Tensor API") · 未做  
  介绍端侧模型开发接口，以及模型表达和运行部署之间的衔接。

- **10-19** [用 ADK 构建不长时间沉默的语音 Agent](https://developers.googleblog.com/step-by-step-guide-build-a-voice-agent-that-never-goes-silent-using-adk "Step by Step guide: Build a Voice Agent That Never Goes Silent using ADK") · 未做  
  关注长任务期间的反馈和语音交互，改善用户等待时的体验。

- **10-15** [Agent 评估怎样超越“感觉不错”](https://developers.googleblog.com/evaluating-ai-agents-moving-past-the-vibe-check "Evaluating AI agents: moving past the vibe check") · 未做  
  把主观体验转成可检查的任务表现，介绍更系统的评估方法。

- **10-15** [google/adk-recipes 的三层结构](https://developers.googleblog.com/three-layers-one-repo-a-tour-of-googleadk-recipes "Three layers, one repo: a tour of google/adk-recipes") · 未做  
  通过一个代码仓了解 ADK 示例、可复用方案与完整应用如何组织。

- **10-14** [Apigee hybrid 接入 MCP](https://developers.googleblog.com/announcing-mcp-support-in-apigee-hybrid-agentic-tools-that-run-in-your-own-cluster "Announcing MCP support in Apigee hybrid: agentic tools that run in your own cluster") · 未做  
  让 Agent 工具运行在自己的集群中，关注接口暴露与运行环境。

- **10-08** [ML Drift：边缘 GPU 推理](https://developers.googleblog.com/ml-drift-next-gen-gpu-aiml-inference-at-the-edge "ML Drift: Next-Gen GPU AI/ML Inference at the Edge") · 未做  
  介绍面向边缘设备的 AI/ML 推理方案与开发方式。

- **10-08** [AQuA：在请求之外诊断线上 Agent 的质量问题](https://developers.googleblog.com/the-outer-loop-insights-first-an-ambient-quality-agent-that-diagnoses-your-production-agent "The Outer Loop, Insights First: An Ambient Quality Agent That Diagnoses Your Production Agent") · 未做

  分析运行轨迹与部署源码快照，聚类并核验失败模式，区分模型、编排、工具契约和指令问题。

- **10-06** [在端侧做多模态语义搜索](https://developers.googleblog.com/google-ai-edge-with-embeddinggemma-2 "Bring multimodal semantic search to the edge with EmbeddingGemma 2") · 未做  
  用 EmbeddingGemma 2 组织语义检索，关注设备侧的数据与运行流程。

</details>

<details>
<summary><strong>Microsoft Research · 6 篇 · 1 篇已学习</strong></summary>

- **10-30** [用合成企业数据评估 Copilot](https://www.microsoft.com/en-us/research/blog/from-synthetic-enterprise-data-evaluations-to-real-microsoft-copilot-ai-confidence "From synthetic enterprise data evaluations to real Microsoft Copilot AI confidence") · 未做  
  研究怎样生成更接近实际业务的数据，检验模型在企业场景中的表现。

- **10-22** [Flint-interactive：可交互的数据可视化语言](https://www.microsoft.com/en-us/research/blog/flint-interactive-a-language-for-creating-interactive-data-visualizations "Flint-interactive: A language for creating interactive data visualizations") · **已学习**  
  围绕事件、状态更新和图表交互，解释 AI 生成可视化的实现方式。 [阅读报告](../ai-learning/reports/knowledge_reports/Flint_interactive_交互式数据可视化语言_语义事件与更新算子_深度解析_20261025.md)

- **10-21** [KLS 猜想的新进展](https://www.microsoft.com/en-us/research/blog/solving-a-31-year-old-grand-challenge-in-mathematics-the-kls-conjecture "Solving a 31-year-old grand challenge in mathematics – the KLS conjecture") · 未做  
  介绍一个长期数学难题的研究结果；具体结论以原文论证为准。

- **10-15** [Magnetar：基于证明的通用计算](https://www.microsoft.com/en-us/research/blog/proof-based-general-purpose-computing-with-magnetar "Proof-based general-purpose computing with Magnetar") · 未做  
  关注计算结果如何附带可验证依据，以及这种方式的用途。

- **10-12** [模拟学生学习，改进 AI 辅导](https://www.microsoft.com/en-us/research/blog/simulating-student-learning-for-better-ai-tutoring "Simulating student learning for better AI tutoring") · 未做  
  通过学习过程模拟来设计与评估辅导策略，而不只测试单次回答。

- **10-07** [Agent Lightning 1.0：在真实 Harness 中训练](https://www.microsoft.com/en-us/research/blog/agent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses "Agent Lightning v1.0: A 3,500-Line Lightweight Agentic RL Framework for Training Agents with Real Harnesses") · 未做  
  介绍轻量 Agent 强化学习框架，关注训练和实际运行流程如何对接。

</details>

<details>
<summary><strong>Apple 机器学习研究 · 10 篇 · 2 篇已学习</strong></summary>

- **10-26** [GHARP：实时高斯头部动画](https://machinelearning.apple.com/research/gharp-head-animation "GHARP: Real-Time Gaussian Head Animation from Large-Scale Reconstruction Prior") · 未做  
  利用大规模重建先验生成头部动画，关注实时性与视觉表现。

- **10-15** [MLX 与 RDMA：多台 Mac 协同推理](https://machinelearning.apple.com/research/mlx-distributed-inference "Local and Distributed Large LLM Inference with MLX and RDMA on Mac Studio") · **已学习**  
  解释本地与分布式大模型推理的差异，以及网络和模型划分的作用。 [阅读报告](../ai-learning/reports/knowledge_reports/Apple_MLX_RDMA_Mac_Studio分布式大模型推理_深度解析_20261021.md)

- **10-15** [先规划还是先找工具](https://machinelearning.apple.com/research/plan-retrieve-tool-discovery "Plan or Retrieve First? A Scale Study of Tool Discovery Architectures") · **已学习**  
  比较大规模工具目录中的发现架构，关注任务复杂度怎样影响选择。 [阅读报告](../ai-learning/reports/paper_analyses/49_plan_retrieve_tool_discovery_2026.md)

- **10-15** [基于选择的多模态搜索推理](https://machinelearning.apple.com/research/selection-structured-reasoning "Selection-Based Structured Reasoning: Toward Efficient Multimodal Search Agents") · 未做  
  研究多模态 Agent 如何组织候选选择，提升搜索过程的效率。

- **10-14** [检测一句话中的语言切换](https://machinelearning.apple.com/research/code-switching-detection "Code-Switching Detection via Language-Selective Dimensions in Speech Foundation Models") · 未做  
  通过语音基础模型中的语言相关维度，识别混合语言的切换位置。

- **10-14** [三模态掩码扩散模型的设计空间](https://machinelearning.apple.com/research/tri-modal-masked-diffusion "The Design Space of Tri-Modal Masked Diffusion Models") · 未做  
  比较不同设计选择，适合关注多模态扩散模型的结构。

- **10-13** [数据有限时，双语预训练如何配比](https://machinelearning.apple.com/research/mix-dont-tune "Mix, Don&#x27;t Tune: Bilingual Pre-Training Outperforms Hyperparameter Search in Data-Constrained Settings") · 未做  
  比较语言混合与超参数搜索，研究小语种和有限数据场景的训练方法。

- **10-12** [Minions：把闲置 Apple 芯片组成 GPU 云](https://machinelearning.apple.com/research/distributed-gpu-cloud "Minions: A Dynamic and Distributed Virtual GPU Cloud Built on Idle Apple Silicon Devices") · 未做  
  介绍动态组织多台设备的方式，关注分布式算力的利用与限制。

- **10-12** [让大模型评判翻译质量有多难](https://machinelearning.apple.com/research/llm-translation-quality-annotation "Large Language Models for Machine Translation Quality Annotation: Humans and Models Are Both Challenged") · 未做  
  同时检查人类和模型的标注困难，提醒读者关注评价标准本身。

- **10-12** [Self-Compacting Agents：压缩自己的长轨迹](https://machinelearning.apple.com/research/self-compacting-language-agents "Self-Compacting Language Model Agents") · 未做  
  研究如何缩减 Agent 的历史内容，同时保留后续任务需要的信息。

</details>

<details>
<summary><strong>Ai2 · 1 篇</strong></summary>

- **10-27** [Novelty Bench：大模型能判断研究创新吗](https://allenai.org/blog/novelty-bench "Can we trust LLMs to judge whether a research idea is novel?") · 未做  
  Ai2 发布研究想法新颖性评估；同时有其 Hugging Face 官方镜像。 [官方镜像](https://huggingface.co/blog/allenai/novelty-bench)

</details>

<details>
<summary><strong>Kimi · 1 篇 · 1 篇已学习</strong></summary>

- **10-24** [Kimi K3.1 Pro](https://www.kimi.com/en/blog/kimi-k3-1-pro "Kimi K3.1 Pro") · **已学习**  
  聚焦联合强化学习、长程 Agent 能力与开放权重的实际边界。 [阅读报告](../ai-learning/reports/knowledge_reports/Kimi_K3_1_Pro_联合RL_长程Agent与开放权重_深度解析_20261026.md)

</details>

<details>
<summary><strong>vLLM · 20 篇 · 5 篇已学习</strong></summary>

- **10-29** [vLLM 首日支持 Mistral Large 4](https://vllm.ai/blog/2026-10-29-mistral-large-4 "Day 0 support for Mistral Large 4 on vLLM") · 未做  
  介绍新模型的运行支持，关注部署要求与推理配置。

- **10-23** [DeepSeek-V4.1-Flash 的机架级服务](https://vllm.ai/blog/2026-10-23-deepseek-v41-flash-pd-wide-ep "Serving DeepSeek-V4.1-Flash at Scale: vLLM Matches DeepInfer and Scales to GB300 NVL72") · **已学习**  
  解释预填充与解码分离、Wide-EP 及大规模部署的性能条件。 [阅读报告](../ai-learning/reports/knowledge_reports/vLLM_DeepSeek-V4.1-Flash_PD分离与Wide-EP机架级服务_深度解析_20261025.md)

- **10-23** [GLM-5.3 推理优化：PCP、DCP 与 HiSparse](https://vllm.ai/blog/2026-10-23-glm53-part2-pcp-dcp-hisparse "GLM-5.3 Optimizations, Part 2: PCP, DCP, and Hybrid HiSparse on 16 H200s") · **已学习**  
  围绕百万级上下文，拆解并行策略、稀疏计算与显存使用。 [阅读报告](../ai-learning/reports/knowledge_reports/GLM5_3_vLLM_PCP_DCP_HiSparse_百万上下文推理_深度解析_20261025.md)

- **10-23** [vLLM 首日支持 MiniMax M3.1 Flash](https://vllm.ai/blog/2026-10-23-minimax-m31-flash "vLLM Delivers Day-0 Support for MiniMax-M3.1-Flash") · **已学习**  
  关注新模型的服务端接入、内核支持与部署边界。 [阅读报告](../ai-learning/reports/knowledge_reports/MiniMax_M3_1_Flash_Agent模型与vLLM_Day0支持_深度解析_20261025.md)

- **10-21** [vLLM 首日支持 Flint](https://vllm.ai/blog/2026-10-21-flint "Day-0 Support for Flint on vLLM") · 未做  
  介绍 Flint 模型的适配与使用方式，便于判断实际运行条件。

- **10-21** [Humming：量化推理的高性能算子库](https://vllm.ai/blog/2026-10-21-humming "Announcing Humming: Fast, Flexible Kernels for Quantized Inference") · **已学习**  
  把量化模型与 GEMM 内核连接起来，关注格式支持和性能取舍。 [阅读报告](../ai-learning/reports/knowledge_reports/vLLM_Humming_量化推理Kernel库_深度解析_20261025.md)

- **10-20** [vLLM TorchTPU](https://vllm.ai/blog/2026-10-20-vllm-torchtpu "Introducing vLLM TorchTPU") · 相关报告  
  介绍 vLLM 在 TorchTPU 上的运行路线，和 Google、PyTorch 的配套文章合读。 [相关报告](../ai-learning/reports/knowledge_reports/Google_TPU_vLLM_SGLang_TorchTPU推理引擎_能力矩阵与口径核验_深度解析_20261025.md)

- **10-19** [弹性专家并行如何减少扩缩容停顿](https://vllm.ai/blog/2026-10-19-elastic-ep-near-zero-downtime "Achieving near-zero-downtime scaling in Elastic Expert Parallelism") · 未做  
  研究专家分布变化时，怎样维持服务连续性。

- **10-16** [Kimi K3 的 MegaKernel 优化](https://vllm.ai/blog/2026-10-16-kimi-k3-megakernel "Hyper Optimizing Kimi K3 in vLLM: Moving Fast and Responsibly") · 未做  
  介绍快速推进内核优化时的工程过程与验证要求。

- **10-16** [Kimi K3 在 MI355X 上的吞吐优化](https://vllm.ai/blog/2026-10-16-kimi-k3-mi355x "Scaling Kimi K3 on AMD Instinct MI355X: Matching NVIDIA HGX B300 Throughput per GPU on AgentX") · 未做  
  以 AgentX 为工作负载比较性能，阅读时留意配置和统计口径。

- **10-16** [vLLM 首日支持 Reflection Beam](https://vllm.ai/blog/2026-10-16-reflection-beam "Serving Reflection Beam on vLLM from Day 0") · 未做  
  介绍新开放模型的服务适配与部署方式。

- **10-15** [vLLM 首日支持 Muse Spark Open](https://vllm.ai/blog/2026-10-15-muse-spark-open "Day 0 support for Muse Spark Open on vLLM") · 未做  
  关注开放多模态模型在 vLLM 中的运行支持。

- **10-15** [vLLM 支持 Nemotron 3.5 Super VL](https://vllm.ai/blog/2026-10-15-nemotron-3-5-super-vl-vllm "Announcing Day 0 Support for NVIDIA Nemotron 3.5 Super VL on vLLM") · 未做  
  介绍多模态模型的推理接入，以及具体支持范围。

- **10-14** [不用置信度头的自适应验证](https://vllm.ai/blog/2026-10-14-adaptive-verification-online-estimator "Adaptive Verification Without a Confidence Head") · 未做  
  研究推理过程中如何调整验证策略，减少额外模型组件的需求。

- **10-14** [用推送式 KV 传输优化分离推理](https://vllm.ai/blog/2026-10-14-nixl-push-connector "Push-Based KV Transfer to Improve TTFT and TPOT for Disaggregated Inference in vLLM") · 未做  
  关注缓存传输对首 token 延迟和逐 token 延迟的影响。

- **10-14** [让 RL 训练与推理逐位一致](https://vllm.ai/blog/2026-10-14-train-inference-consistency "Finish RL Training Faster: Bitwise-Consistent, High-Performance, Agent-Driven") · 未做  
  把计算一致性、运行性能和 Agent 辅助优化放进同一条训练链路。

- **10-12** [双向 KV 传输如何改善多轮 Agent 推理](https://vllm.ai/blog/2026-10-12-bidirectional-kvxfer-multiturn-agentic-workload "Improve TTFT for Multi-Turn Agentic Workloads with Bi-Directional KV Transfer in vLLM") · 未做  
  围绕多轮对话中的缓存复用，减少重复预填充带来的等待。

- **10-12** [MAGI-2 音视频模型接入 vLLM-Omni](https://vllm.ai/blog/2026-10-12-magi2-preview-musa "MAGI-2 Preview on vLLM-Omni: Bringing a 114B Audio-Video MoE DiT to Moore Threads MUSA with torchada") · 未做  
  介绍大型音视频 MoE 扩散模型在摩尔线程 MUSA 上的运行适配。

- **10-09** [vLLM 对 Vera Rubin NVL72 的支持](https://vllm.ai/blog/2026-10-09-vera-rubin-preview "vLLM Support for NVIDIA Vera Rubin NVL72: 7.8x Throughput over GB200 NVL72") · 未做  
  介绍新硬件平台的吞吐测试；性能数字属于官方配置下的结果。

- **10-07** [DeepSeek-V4.1-Flash 的持续推理优化](https://vllm.ai/blog/2026-10-07-deepseek-v41-flash "DeepSeek-V4.1-Flash on vLLM: 5x Agentic Throughput Since Day 0") · **已学习**  
  回顾首日支持后的 Agent 吞吐改进，与后续机架级服务文章配套。 [阅读报告](../ai-learning/reports/knowledge_reports/vLLM_DeepSeek-V4.1-Flash_PD分离与Wide-EP机架级服务_深度解析_20261025.md)

</details>

<details>
<summary><strong>PyTorch · 19 篇 · 3 篇已学习</strong></summary>

- **10-28** [PyTorch 2.15 发布说明](https://pytorch.org/blog/pytorch-2-15-release-blog "PyTorch 2.15 Release Blog") · 未做  
  集中浏览本版功能、性能和兼容性变化，按所用模块深入查看。

- **10-26** [用 ExecuTorch 优化 Arm 流式语音识别](https://pytorch.org/blog/optimizing-streaming-speech-recognition-on-arm-edge-devices-with-executorch "Optimizing Streaming Speech Recognition on Arm® Edge Devices with ExecuTorch") · 未做  
  关注边缘设备上的持续音频输入、响应时间和计算开销。

- **10-21** [FlyDSL：在 AMD GPU 上加速 PyTorch](https://pytorch.org/blog/accelerating-pytorch-on-amd-gpus-with-flydsl "Accelerating PyTorch on AMD GPUs with FlyDSL") · **已学习**  
  介绍用 Python 表达 GPU 内核与布局的方式，以及接入 PyTorch 的路线。 [阅读报告](../ai-learning/reports/knowledge_reports/PyTorch_FlyDSL_AMD_GPU_Kernel加速_深度解析_20261025.md)

- **10-21** [TorchTitan：新模型、规模化训练与 TitanRL](https://pytorch.org/blog/torchtitan-update-new-sota-models-performance-at-scale-titanrl "TorchTitan Update: New SOTA Models, Performance at Scale, TitanRL") · **已学习**  
  从训练框架看模型覆盖、性能和强化学习能力的更新。 [阅读报告](../ai-learning/reports/knowledge_reports/PyTorch_TorchTitan_SOTA模型规模化训练与TitanRL_深度解析_20261025.md)

- **10-20** [IBM Spyre 的 MLIR 数据流后端](https://pytorch.org/blog/from-ktir-to-spyrecode-an-mlir-dataflow-backend-for-ibm-spyre "From KTIR to SpyreCode: An MLIR Dataflow Backend for IBM Spyre") · 未做  
  介绍从 KTIR 到 SpyreCode 的编译路径，适合关注新加速器接入。

- **10-20** [TorchTPU：PyTorch 的 TPU 后端](https://pytorch.org/blog/introducing-torchtpu "Introducing TorchTPU") · 相关报告  
  了解原生后端设计，及其与上层训练、推理框架的关系。 [相关报告](../ai-learning/reports/knowledge_reports/Google_TPU_vLLM_SGLang_TorchTPU推理引擎_能力矩阵与口径核验_深度解析_20261025.md)

- **10-19** [TorchNeuron：Trainium 的原生 PyTorch 后端](https://pytorch.org/blog/introducing-torchneuron-native-pytorch-backend-for-aws-trainium "Introducing TorchNeuron: Native PyTorch backend for AWS Trainium") · **已学习**  
  解释模型如何运行在 AWS 芯片上，以及算子和分布式支持的边界。 [阅读报告](../ai-learning/reports/knowledge_reports/Amazon_TorchNeuron_Trainium原生PyTorch后端_深度解析_20261025.md)

- **10-19** [Helion × CompileIQ：联合搜索编译控制](https://pytorch.org/blog/one-search-two-layers-compiler-controls-inside-pytorch-helion-using-nvidia-compileiq "One Search, Two Layers: Compiler Controls Inside PyTorch Helion using NVIDIA CompileIQ") · 未做  
  把编译器参数纳入内核调优过程，关注搜索空间如何组织。

- **10-16** [Zephon：弹性且确定性的数据加载](https://pytorch.org/blog/bringing-elastically-deterministic-data-loading-to-torchtitan-with-zephon "Bringing Elastically Deterministic Data Loading to TorchTitan with Zephon") · 未做  
  讨论训练规模变化后，如何保持数据读取行为可复现。

- **10-15** [ExecuTorch 接入 Arm Cortex-M](https://pytorch.org/blog/bringing-executorch-to-arm-cortex-m-cpus "Bringing ExecuTorch to Arm Cortex-M CPUs") · 未做  
  把模型运行能力带到微控制器，关注受限设备的开发条件。

- **10-15** [Muse Spark 开放权重](https://pytorch.org/blog/muse-spark-open "Muse Spark Is Now an Open-Weights Model") · 未做  
  介绍模型权重开放及 PyTorch 生态的接入情况。

- **10-13** [扩展 Inductor 以支持 IBM Spyre](https://pytorch.org/blog/extending-inductor-for-the-ibm-spyre-accelerator "Extending Inductor for the IBM Spyre Accelerator") · 未做  
  从编译器后端角度介绍新硬件的适配工作。

- **10-08** [把 Spyre 做成原生 PyTorch 设备](https://pytorch.org/blog/building-spyre-as-a-native-pytorch-device "Building Spyre as a Native PyTorch Device") · 未做  
  关注张量、运行时与硬件集成，而不只是在应用层做包装。

- **10-08** [NVIDIA Dynamo 的会话感知推理](https://pytorch.org/blog/session-aware-agentic-inference-with-nvidia-dynamo "Session-Aware Agentic Inference with NVIDIA Dynamo") · 未做  
  围绕多轮 Agent 会话组织服务，关注缓存和请求调度。

- **10-06** [FBTriton：重做批量 Embedding 计算](https://pytorch.org/blog/modernizing-table-batched-embeddings-with-fbtriton "Modernizing Table Batched Embeddings with FBTriton") · 未做  
  用 Triton 更新 Embedding 的实现，关注内核与框架的衔接。

- **10-05** [PyTorch 媒体处理生态的变化](https://pytorch.org/blog/evolution-of-the-pytorch-media-processing-landscape "Evolution of the PyTorch Media Processing Landscape") · 未做  
  梳理音视频等数据处理工具，便于选择合适的输入流水线。

- **10-05** [PyTorch 加速器集成工作组进展](https://pytorch.org/blog/pytorch-hardware-enablement-updates-from-the-acceleration-integration-working-group "PyTorch Hardware Enablement: Updates from the Accelerator Integration Working Group") · 未做  
  了解不同硬件进入 PyTorch 生态时的接口和协作方向。

- **10-02** [用 Helion 编写可移植的 vLLM 线性层后端](https://pytorch.org/blog/building-a-high-performance-and-portable-vllm-linear-backend-with-helion "Building a High-Performance and Portable vLLM Linear Backend with Helion") · 未做  
  讨论性能优化与跨硬件可移植性如何同时考虑。

- **10-01** [TLX 优化不规则 Flash Attention](https://pytorch.org/blog/optimizing-jagged-flash-attention-with-tlx-the-road-toward-sota-fa4-on-blackwell "Optimizing Jagged Flash Attention with TLX: The Road Toward SOTA FA4 on Blackwell") · 未做  
  聚焦不等长序列的注意力计算，以及 Blackwell 上的内核优化。

</details>

<details>
<summary><strong>AMD ROCm · 23 篇 · 3 篇已学习</strong></summary>

- **10-30** [MONAI Model Zoo 在 ROCm 上的推理验证](https://rocm.blogs.amd.com/artificial-intelligence/monai-zoo-2608/README.html "Bringing the MONAI Model Zoo to AMD Instinct™ GPUs: Validated Inference on ROCm") · 未做  
  把医疗模型库迁移到 AMD GPU，关注模型支持与验证过程。

- **10-28** [MI308X 上的 DeepSeek-V4 Flash 强化学习](https://rocm.blogs.amd.com/ecosystems-and-partners/deepseek-v4-mi308-aiter-backed-rl/README.html "DeepSeek-V4 Flash RL on AMD Instinct MI308X GPUs with an AITER-Backed RL Stack") · 未做  
  介绍 AITER 支持的训练栈，以及 AMD 平台的适配方式。

- **10-27** [用 AMD Quark 训练 EAGLE3 草稿模型](https://rocm.blogs.amd.com/artificial-intelligence/eagle3-training/README.html "Training EAGLE3 Speculative Decoding Draft Models on AMD Instinct MI350X with AMD Quark") · 未做  
  关注投机解码所需的小模型如何训练与部署。

- **10-27** [ROCm 10.0 支持 Ray 2.58](https://rocm.blogs.amd.com/artificial-intelligence/rocm10-ray/README.html "ROCm 10.0.0 Support for Ray 2.58.0: Enabling Scalable AI Workflows") · 未做  
  介绍分布式 AI 工作流的运行支持与软件栈组合。

- **10-27** [Triton GEMM 的 Warp 流水线](https://rocm.blogs.amd.com/software-tools-optimization/triton-warp-pipeline/README.html "Two Waves, One Stage Apart: Warp-Pipelining Triton GEMMs on AMD Instinct") · 未做  
  通过错开计算阶段安排工作，研究 AMD GPU 上矩阵乘法的优化。

- **10-26** [用 hipCIM 加速数字病理流水线](https://rocm.blogs.amd.com/artificial-intelligence/monai-hipcim-2608/README.html "Accelerating MONAI Digital-Pathology Pipelines on AMD Instinct™ GPUs with hipCIM") · 未做  
  把大幅病理图像的处理放到 GPU，关注数据准备开销。

- **10-26** [AMD GPU 上训练和部署 YOLO](https://rocm.blogs.amd.com/ecosystems-and-partners/ultralytics-amd/README.html "Ultralytics YOLO on AMD GPUs: Train, Run, and Deploy with ROCm™") · 未做  
  给出 Ultralytics 模型在 ROCm 上的运行路线。

- **10-26** [XLA 中的 Group-GEMM](https://rocm.blogs.amd.com/software-tools-optimization/openxla-group-gemm/README.html "Group-GEMM in XLA: Making Mixture-of-Experts Fast and Memory-Efficient") · 未做  
  把分组矩阵乘法用于 MoE，关注计算效率与显存开销。

- **10-23** [RDNA 4 的 FP8 GEMM 优化](https://rocm.blogs.amd.com/software-tools-optimization/rdna-fp8-gemm/README.html "FP8 GEMM Optimization on AMD RDNA™ 4 Architecture") · **已学习**  
  从矩阵指令、共享内存和 tile 搜索理解低精度计算的实现。 [阅读报告](../ai-learning/reports/knowledge_reports/AMD_RDNA4_FP8_GEMM_WMMA与Tile搜索_深度解析_20261025.md)

- **10-23** [分布式 3D Gaussian Splatting](https://rocm.blogs.amd.com/software-tools-optimization/scaling-gsplat/README.html "Scaling 3D Gaussian Splatting with Distributed Compute: Why One GPU Is Never Enough") · **已学习**  
  解释 Gaussian 分片和 GPU 通信，关注扩展性能何时受限。 [阅读报告](../ai-learning/reports/knowledge_reports/AMD_分布式3D_Gaussian_Splatting_Gaussian分片与RCCL_深度解析_20261025.md)

- **10-21** [Micro-World 2：流式交互世界模型](https://rocm.blogs.amd.com/artificial-intelligence/Micro-World-V2/README.html "Micro-World 2: Streaming Real-time Interactive World Model") · 未做  
  关注连续生成与实时交互，适合追踪可持续运行的世界模型。

- **10-21** [在 AMD GPU 上优化世界动作模型](https://rocm.blogs.amd.com/artificial-intelligence/faster-action-models/README.html "Optimizing World Action Models on AMD GPUs") · 未做  
  从运行性能出发，研究模型与硬件实现的配合。

- **10-21** [Primus 的 MoE 训练优化](https://rocm.blogs.amd.com/software-tools-optimization/primus-moe-optimization/README.html "MoE Training Optimization with Primus") · 未做  
  介绍专家模型训练中的计算和系统优化。

- **10-20** [rocOpt：GPU 加速的决策优化](https://rocm.blogs.amd.com/artificial-intelligence/rocopt/README.html "Introducing rocOpt: GPU-Accelerated Decision Optimization on AMD ROCm") · 未做  
  了解 ROCm 上的优化求解工具及其应用方向。

- **10-20** [用 hipCIM 加速整张病理切片的读写](https://rocm.blogs.amd.com/software-tools-optimization/hipcim-26-08/README.html "hipCIM 26.06: GPU-Accelerated Whole-Slide Image I/O on AMD Instinct™ GPUs") · 未做  
  关注大图像 I/O，补足模型推理之外的数据处理环节。

- **10-20** [MegaKernel：低延迟交互式推理](https://rocm.blogs.amd.com/software-tools-optimization/megakernel-intro/README.html "Bringing Ultra-Fast, Interactive LLM Inference to AMD Instinct™ MI355X GPUs") · **已学习**  
  把多个计算步骤组织进持久化内核，关注单请求交互与吞吐服务的区别。 [阅读报告](../ai-learning/reports/knowledge_reports/AMD_ROCm_MegaKernel_MI355X交互式单请求推理_深度解析_20261025.md)

- **10-16** [RDNA 3/4 的 FP16 GEMM 优化](https://rocm.blogs.amd.com/software-tools-optimization/rdna-fp16-gemm/README.html "FP16 GEMM Optimization on AMD RDNA™ 3 and RDNA™ 4 Architectures") · 未做  
  对比两代 GPU 的矩阵乘法实现与调优方法。

- **10-14** [单节点 MI300X 服务 GLM-5.3 长上下文](https://rocm.blogs.amd.com/artificial-intelligence/glm53-mi300x-vllm/README.html "Long Context, One Node: Serving GLM-5.3-FP8 on MI300X with DP8+EP8") · 未做  
  介绍 DP8 与 EP8 的组合，以及模型精度和显存要求。

- **10-08** [用 Primus 从头训练混合架构 LLM](https://rocm.blogs.amd.com/artificial-intelligence/primus-hybrid-llm/README.html "Pre-Training Hybrid LLMs from Scratch in Primus on AMD Instinct™ GPUs") · 未做  
  关注训练配置与 AMD GPU 上的基础设施支持。

- **10-08** [Kimi K3 MXFP4 的分离式 Wide-EP 服务](https://rocm.blogs.amd.com/software-tools-optimization/di-kimi-k3-mxfp4/README.html "DI Series: Serving Kimi-K3 MXFP4 Wide-EP Disaggregated on AMD Instinct MI300X and MI325X") · 未做  
  介绍 MI300X、MI325X 上的低精度与并行部署组合。

- **10-08** [MI455X 与 MI355X 推理数据怎么比较](https://rocm.blogs.amd.com/software-tools-optimization/mi455x-vs-mi355x/README.html "AMD Instinct MI455X vs MI355X: A Technical Look at the Advancing AI 2026 Inference Numbers") · 未做  
  解释发布测试中的硬件和配置口径，避免直接套用性能倍数。

- **10-06** [GPU 性能不能只看峰值 FLOPs](https://rocm.blogs.amd.com/artificial-intelligence/taf-blog/README.html "Completing the GPU Performance Picture: Understanding TAF Alongside Peak FLOPs and MAF") · 未做  
  结合 TAF、MAF 等指标，补充对实际运行效率的判断。

- **10-05** [ROCm 10.1：缓解数据搬运瓶颈](https://rocm.blogs.amd.com/ecosystems-and-partners/rocm-10.1-blog/README.html "ROCm 10.1: Breaking the Data-Movement Bottleneck") · 未做  
  介绍软件栈如何改善数据移动，以及对计算任务的影响。

</details>

<details>
<summary><strong>NVIDIA 技术博客 · 31 篇 · 6 篇已学习</strong></summary>

- **10-30** [为 NVIDIA Dynamo 构建经过验证的 Kubernetes 环境](https://developer.nvidia.com/blog/build-a-validated-kubernetes-runtime-for-nvidia-dynamo "Build a Validated Kubernetes Runtime for NVIDIA Dynamo") · 未做  
  关注模型服务运行时的配置、兼容性和验证流程。

- **10-30** [用 NemoClaw 构建可自行控制的专用 Agent](https://developer.nvidia.com/blog/build-specialized-agents-on-a-stack-you-control-with-nvidia-nemoclaw "Build Specialized Agents on a Stack You Control with NVIDIA NemoClaw") · 相关报告  
  介绍自有运行栈上的 Agent 开发，关注模型、工具与执行环境的组合。 [相关报告](../ai-learning/reports/knowledge_reports/NVIDIA_OpenShell_Sentry_Agent运行时安全架构_深度解析_20261021.md)

- **10-30** [用少量命令运行边缘 AI 模型](https://developer.nvidia.com/blog/run-ai-models-for-edge-application-development-with-just-a-few-commands "Run AI Models for Edge Application Development with Just a Few Commands") · 未做  
  介绍边缘应用的快速开发入口，方便先验证模型是否适合设备。

- **10-27** [提升 DGX Spark 上 MoE 推理的三种方法](https://developer.nvidia.com/blog/3-ways-to-boost-moe-inference-on-nvidia-dgx-spark "3 Ways to Boost MoE Inference on NVIDIA DGX Spark") · 未做  
  围绕本地硬件和专家模型，比较不同优化方向。

- **10-27** [让 Nemotron 学会本地规则](https://developer.nvidia.com/blog/fine-tuning-nvidia-nemotron-to-know-local-rules-not-just-local-languages "Fine-Tuning NVIDIA Nemotron to Know Local Rules, Not Just Local Languages") · 未做  
  把语言适配延伸到制度与业务规则，关注专用模型的微调。

- **10-27** [CUDA 13.4 的 GPU 显存隔离与共享](https://developer.nvidia.com/blog/memory-enforced-gpu-sharing-in-kubernetes-with-nvidia-cuda-13-4 "Memory-Enforced GPU Sharing in Kubernetes with NVIDIA CUDA 13.4") · 未做  
  讨论 Kubernetes 多任务共用 GPU 时，如何约束显存占用。

- **10-26** [Mission Control 2.5：集群故障自动恢复](https://developer.nvidia.com/blog/how-nvidia-mission-control-2-5-brings-autonomous-recovery-to-kubernetes "How NVIDIA Mission Control 2.5 Brings Autonomous Recovery to Kubernetes") · 未做  
  介绍 Kubernetes 运行环境的恢复机制与运维流程。

- **10-23** [TensorRT 全局性能调优：上篇](https://developer.nvidia.com/blog/scaling-nvidia-tensorrt-performance-optimization-beyond-a-single-build-route-with-the-global-performance-tuner-part-1 "Scaling NVIDIA TensorRT Performance Optimization Beyond a Single Build Route with the Global Performance Tuner, Part 1") · **已学习**  
  把不同构建路线纳入搜索，同时考虑性能和精度。 [阅读报告](../ai-learning/reports/knowledge_reports/TensorRT_GlobalPerformanceTuner_可搜索build_route与精度感知调优_深度解析_20261025.md)

- **10-23** [TensorRT 全局性能调优：下篇](https://developer.nvidia.com/blog/scaling-nvidia-tensorrt-performance-optimization-beyond-a-single-build-route-with-the-global-performance-tuner-part-2 "Scaling NVIDIA TensorRT Performance Optimization Beyond a Single Build Route with the Global Performance Tuner, Part 2") · **已学习**  
  继续讨论精度感知、端到端调优与构建路线搜索。 [阅读报告](../ai-learning/reports/knowledge_reports/TensorRT_GlobalPerformanceTuner_可搜索build_route与精度感知调优_深度解析_20261025.md)

- **10-23** [用 Agent 教 Microduck 在仿真中行走](https://developer.nvidia.com/blog/using-ai-agents-to-teach-robots-like-microduck-to-walk-in-simulation "Using AI Agents to Teach Robots Like Microduck to Walk in Simulation") · **已学习**  
  解释 Agent 准备工作、RL 训练与真实机器人验证的分工。 [阅读报告](../ai-learning/reports/knowledge_reports/NVIDIA_Microduck_Agentic_Robotics_仿真训练与Sim2Real_深度解析_20261025.md)

- **10-22** [八台 DGX Spark 协同运行大模型](https://developer.nvidia.com/blog/running-frontier-class-ai-models-across-8-nvidia-dgx-spark-nodes "Running Frontier-Class AI Models Across 8 NVIDIA DGX Spark Nodes") · 未做  
  介绍桌面集群的分布式推理配置，关注内存与互联条件。

- **10-21** [RFD4-Proteina：在推理时搜索蛋白质设计](https://developer.nvidia.com/blog/design-proteins-with-rfd4-proteina-using-reward-guided-inference-time-search "Design Proteins with RFD4-Proteina Using Reward-Guided Inference-Time Search") · 未做  
  用奖励引导候选搜索，关注设计目标如何进入生成过程。

- **10-21** [用 Agent 辅助搭建 AI 工厂数字孪生](https://developer.nvidia.com/blog/developing-an-ai-factory-digital-twin-with-an-agent-assisted-workflow "Developing an AI Factory Digital Twin with an Agent-Assisted Workflow") · 未做  
  把设计和仿真组织成工作流，观察 Agent 在工程准备中的作用。

- **10-21** [OpenShell 的规模化 Agent 安全架构](https://developer.nvidia.com/blog/how-nvidia-openshell-reference-architecture-secures-and-governs-ai-agent-workloads-at-scale "How NVIDIA OpenShell Reference Architecture Secures and Governs AI Agent Workloads at Scale") · **已学习**  
  解释执行隔离、治理与基础设施如何共同约束 Agent 行为。 [阅读报告](../ai-learning/reports/knowledge_reports/NVIDIA_OpenShell_Sentry_Agent运行时安全架构_深度解析_20261021.md)

- **10-21** [Sentry：在运行时保护 Agent](https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime "Inside NVIDIA Sentry: Secure AI Agents at Runtime") · **已学习**  
  关注实际执行过程中的监测与控制，补充提示词层面的约束。 [阅读报告](../ai-learning/reports/knowledge_reports/NVIDIA_OpenShell_Sentry_Agent运行时安全架构_深度解析_20261021.md)

- **10-19** [CUDA Tile 加速 Mamba-2](https://developer.nvidia.com/blog/accelerating-mamba-2-with-high-performance-forward-pass-kernels-in-nvidia-cuda-tile "Accelerating Mamba-2 with High-Performance Forward Pass Kernels in NVIDIA CUDA Tile") · **已学习**  
  从分块和内核融合解释状态空间模型前向计算的优化。 [阅读报告](../ai-learning/reports/knowledge_reports/NVIDIA_CUDA_Tile_Mamba2高性能Kernel_深度解析_20261021.md)

- **10-16** [RTX Spark：开发、测试与部署放在一台机器](https://developer.nvidia.com/blog/code-test-and-deploy-on-one-machine-with-nvidia-rtx-spark "Code, Test, and Deploy on One Machine with NVIDIA RTX Spark") · 未做  
  介绍本地 AI 工作站的开发流程与运行场景。

- **10-15** [Nemotron 3.5 Super VL：多模态专用 Agent](https://developer.nvidia.com/blog/nvidia-nemotron-3-5-super-vl-powers-specialized-agents-with-multimodal-reasoning "NVIDIA Nemotron 3.5 Super VL Powers Specialized Agents with Multimodal Reasoning") · 未做  
  介绍模型的多模态推理定位，关注专用任务适配。

- **10-15** [在 GB300 NVL72 上运行 Muse Spark Open](https://developer.nvidia.com/blog/scale-agentic-coding-workflows-with-metas-muse-spark-open-on-nvidia-gb300-nvl72 "Scale Agentic Coding Workflows with Meta’s Muse Spark Open on NVIDIA GB300 NVL72") · 未做  
  围绕编码 Agent 工作负载，介绍开放模型的规模化服务。

- **10-14** [用 NeMo Gym 训练芯片设计 Agent](https://developer.nvidia.com/blog/optimizing-agent-reliability-and-tool-calling-efficiency-for-chip-design-using-nvidia-nemo-gym "Optimizing Agent Reliability and Tool Calling Efficiency for Chip Design Using NVIDIA NeMo Gym") · 未做  
  关注工具调用效率与可靠性，观察专业任务如何转成训练环境。

- **10-13** [用 Agent 把 Spark UDF 改写为 GPU 计算](https://developer.nvidia.com/blog/rewrite-apache-spark-udfs-gpu-acceleration-ai-agents "How to Rewrite Apache Spark UDFs for GPU Acceleration with AI Agents") · 未做  
  介绍代码迁移流程，以及改写后的正确性和性能检查。

- **10-12** [ReplaySSM：重新安排混合模型的状态存储](https://developer.nvidia.com/blog/replayssm-rethinking-state-storage-for-faster-hybrid-model-decoding "ReplaySSM: Rethinking State Storage for Faster Hybrid-Model Decoding") · 未做  
  研究解码阶段的状态保存和重用，减少运行开销。

- **10-08** [用前沿模型准备机器人仿真素材](https://developer.nvidia.com/blog/5-steps-to-create-simready-assets-for-robotics-with-frontier-ai-models "5 Steps to Create SimReady Assets for Robotics with Frontier AI Models") · 未做  
  分步骤介绍可用于仿真的场景资产怎样制作与整理。

- **10-08** [KDD Cup 的数据分析 Agent 经验](https://developer.nvidia.com/blog/building-reliable-data-analytics-agents-lessons-from-the-kdd-cup "Building Reliable Data Analytics Agents: Lessons from the KDD Cup") · 未做  
  围绕可靠的数据分析任务，讨论工具、流程与评测的设计。

- **10-07** [制造机器的机器：AI 工程系统](https://developer.nvidia.com/blog/the-machines-that-make-the-machines "The Machines that Make the Machines") · 未做  
  介绍 AI 与工程设计、制造系统的结合，适合看应用侧的系统视角。

- **10-07** [用数字孪生和 Agent 验证 AI 工厂变更](https://developer.nvidia.com/blog/validate-ai-factory-changes-with-digital-twins-and-ai-agents "Validate AI Factory Changes with Digital Twins and AI Agents") · 未做  
  在真实环境改动前先做仿真与检查，关注变更验证流程。

- **10-06** [AICR 1.0：可验证的 GPU 集群配置](https://developer.nvidia.com/blog/aicr-v1-0-open-stable-and-verifiable-gpu-cluster-configuration "AICR v1.0: Open, stable, and verifiable GPU cluster configuration") · 未做  
  介绍开放配置方案，关注环境一致性和部署前检查。

- **10-06** [Megatron Core 的确定性预训练](https://developer.nvidia.com/blog/scale-bitwise-deterministic-pretraining-with-nvidia-megatron-core "Scale Bitwise-Deterministic Pretraining with NVIDIA Megatron Core") · 未做  
  讨论规模化训练中如何获得逐位一致的计算结果。

- **10-01** [DOCA Agent Skills：辅助开发 BlueField 应用](https://developer.nvidia.com/blog/build-applications-on-nvidia-bluefield-faster-with-nvidia-doca-agent-skills "Build Applications on NVIDIA BlueField Faster with NVIDIA DOCA Agent Skills") · 未做  
  把平台知识组织成 Agent 可使用的技能，支持专用硬件开发。

- **10-01** [用 C++ 和 TensorRT RTX 做本地 AI 应用](https://developer.nvidia.com/blog/build-local-ai-apps-with-c-and-nvidia-tensorrt-rtx-samples "Build Local AI Apps with C++ and NVIDIA TensorRT RTX Samples") · 未做  
  通过示例连接模型推理与桌面应用开发。

- **10-01** [面向沙特阿拉伯语方言微调 Nemotron](https://developer.nvidia.com/blog/fine-tuning-nvidia-nemotron-for-saudi-arabic-dialects-with-a-path-to-other-languages "Fine-Tuning NVIDIA Nemotron for Saudi Arabic Dialects, with a Path to Other Languages") · 未做  
  介绍语言适配过程，并讨论向其他语言迁移的方法。

</details>

<details>
<summary><strong>Hugging Face 与机构作者 · 17 篇 · 4 篇已学习</strong></summary>

- **10-29** [Apple 平台的开放语音与决策模型](https://huggingface.co/blog/anydecisionmodel "Introducing AnySpeechRecognizer and AnyDecisionModel: Open Models for Speech and Decisions on Apple Platforms") · 未做  
  介绍 AnySpeechRecognizer、AnyDecisionModel 及其本地应用方向。

- **10-29** [Granite Switch 4.1.1：像更新软件一样更新模型](https://huggingface.co/blog/ibm-granite/granite-switch-4-1-1 "Granite Switch 4.1.1 — Update models like you update software") · 未做  
  关注模型更新的组织方式，以及版本迭代的实际操作。

- **10-27** [LFM3：构建专用多模态模型](https://huggingface.co/blog/LiquidAI/lfm3 "Build specialized multimodal models with LFM3") · 未做  
  Liquid AI 介绍新模型路线，关注任务适配与部署方向。

- **10-23** [查询模型能否运行在 AWS Trainium](https://huggingface.co/blog/torch-neuronx-model-support "Does Your Model Run on AWS Trainium? Look It Up") · 相关报告  
  提供兼容性查询入口，适合部署前确认支持范围。 [相关报告](../ai-learning/reports/knowledge_reports/Amazon_TorchNeuron_Trainium原生PyTorch后端_深度解析_20261025.md)

- **10-22** [用 Granite 时间序列模型做集成预测](https://huggingface.co/blog/ibm-research/granite-timeseries-ensemble-r1 "Ensemble forecasting with IBM Granite time-series models") · 未做  
  研究多个预测模型如何组合，关注时序任务中的方法选择。

- **10-22** [ThinkingBox：把数据库评分变成 RL 奖励](https://huggingface.co/blog/microsoft/thinkingbox-training "Turning Database Grading into RL Rewards: Post-Training Agents with ThinkingBox") · **已学习**  
  用实际业务终态训练 Agent，区分“声称完成”和“真的做对”。 [阅读报告](../ai-learning/reports/knowledge_reports/Microsoft_ThinkingBox_数据库评分转RL奖励与Agent后训练_深度解析_20261025.md)

- **10-21** [缩小词表，降低小语言模型推理成本](https://huggingface.co/blog/Dharma-AI/vocabx-vocabulary-specialization "How Specializing the Vocabulary of SLMs Can Cut Inference Cost by 77% in Real Applications") · 未做  
  Dharma AI 介绍面向具体应用的词表定制，注意收益的任务依赖。

- **10-21** [Microduck：从 Isaac Lab 仿真到真实机器人](https://huggingface.co/blog/nvidia/microduck-isaac-lab-sim-to-real "Train in Simulation, Deploy on a Real Robot: Microduck with Isaac Lab 3.0") · **已学习**  
  通过完整实践介绍训练与部署，补充 NVIDIA 博客的 Agent 训练视角。 [阅读报告](../ai-learning/reports/knowledge_reports/NVIDIA_Microduck_Agentic_Robotics_仿真训练与Sim2Real_深度解析_20261025.md)

- **10-20** [AnyLanguageModel 1.0：Apple 平台本地模型实践](https://huggingface.co/blog/anylanguagemodel-1-0 "AnyLanguageModel 1.0: One Year of Local Models on Apple Platforms") · 未做  
  回顾本地模型工具的演进，关注应用接入与运行体验。

- **10-20** [ALTK-Evolve：从经验中学习客服工作方法](https://huggingface.co/blog/ibm-research/altk-evolve-bc "ALTK-Evolve: How learned memory tops the τ²-bench leaderboard on customer service tasks without a frontier model") · **已学习**  
  把运行轨迹提炼成可复用记忆，关注稳定成功率、成本和记忆治理。 [阅读报告](../ai-learning/reports/knowledge_reports/ALTK_Evolve_学习型Memory与Agent服务任务_深度解析_20261021.md)

- **10-19** [用 TorchNeuron 运行 Hugging Face 模型](https://huggingface.co/blog/hf-torchneuron "TorchNeuron: running HF models on AWS Trainium is easier than ever") · 相关报告  
  从开发者使用角度介绍 Trainium 接入，和后端架构文章配套。 [相关报告](../ai-learning/reports/knowledge_reports/Amazon_TorchNeuron_Trainium原生PyTorch后端_深度解析_20261025.md)

- **10-16** [Reflection Beam：开放大模型接入](https://huggingface.co/blog/reflection-beam "Welcome Beam: a 501B open model you can own, customize, and scale") · 未做  
  介绍模型、定制和部署能力；开放范围以模型许可为准。

- **10-15** [Muse Spark Open：多模态 MoE 开放模型](https://huggingface.co/blog/meta-muse-spark-open "Welcome Muse Spark Open: open-weight frontier multimodal mixture-of-experts model from Meta") · 未做  
  从 Hugging Face 生态了解模型权重与使用方式。

- **10-13** [LFM2.5：在设备上运行私有 Agent](https://huggingface.co/blog/LiquidAI/lfm25-24b-a2b "Run fast, private agents on-device with LFM2.5-24B-A2B") · 未做  
  关注端侧模型的速度、资源需求与数据处理方式。

- **10-08** [用 ML Intern 做出自己需要的模型](https://huggingface.co/blog/building-with-ml-intern "The model that didn&#x27;t exist, so you made it yourself") · 未做  
  通过模型构建案例，了解工具如何支持定制任务。

- **10-03** [ThinkingBox：Agent 说完成，数据库却不对](https://huggingface.co/blog/microsoft/thinkingbox "The Agent Said It Was Done. The Database Disagreed.") · **已学习**  
  用有状态业务任务揭示评价盲区，是后训练篇的基础。 [阅读报告](../ai-learning/reports/knowledge_reports/Microsoft_ThinkingBox_数据库评分转RL奖励与Agent后训练_深度解析_20261025.md)

- **10-02** [AutoSynthData：为企业 Agent 生成训练数据](https://huggingface.co/blog/ServiceNow-AI/autosynthdata "AutoSynthData: Generating Training Data for Enterprise Agents") · 未做  
  ServiceNow 介绍合成数据流程，关注企业任务的训练材料。

</details>

<details>
<summary><strong>GitHub AI &amp; ML · 4 篇</strong></summary>

- **10-19** [把 Copilot App 会话接到 VS Code](https://github.blog/ai-and-ml/github-copilot/how-to-continue-a-github-copilot-app-session-in-vs-code "How to continue a GitHub Copilot app session in VS Code") · 未做  
  介绍对话和工作如何在两个入口之间续接。

- **10-13** [GitHub 的上下文感知密钥检测模型](https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-with-less-noise "GitHub’s model for secret detection: Finding more secrets with less noise") · 未做  
  关注误报、检出质量与运行开销，适合看专用模型的工程落地。

- **10-07** [密钥保护怎样跟上软件产出规模](https://github.blog/ai-and-ml/github-copilot/secret-protection-must-scale-with-software "Secret protection must scale with software") · 未做  
  从更多代码和提交出发，讨论扫描与防护能力如何扩展。

- **10-05** [ReviewBench：开放的 AI 代码审查基准](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review "ReviewBench: An open benchmark for AI code review") · 未做  
  评估审查 Agent 是否发现有价值的问题，关注任务设计与评价标准。

</details>

<details>
<summary><strong>Cloudflare AI · 5 篇 · 1 篇已学习</strong></summary>

- **10-26** [GLM-5.3 跨请求 KV Cache 暴露事件](https://blog.cloudflare.com/kv-cache-exposure-remediation "Cross-request KV cache exposure in the GLM-5.3 Workers AI model, and our remediation with SGLang") · 未做  
  Cloudflare 复盘租户隔离问题及 SGLang 修复，适合检查服务端边界。

- **10-21** [WebMCP：让电商站点能被 Agent 使用](https://blog.cloudflare.com/webmcp-commerce "How Commerce.com and Cloudflare are getting storefronts ready for AI agents") · 未做  
  介绍 Commerce.com 与 Cloudflare 的接入实践，关注网站与工具接口的衔接。

- **10-19** [Clairic：面向信息提取的模型](https://blog.cloudflare.com/clairic-extraction-model "Introducing Clairic, a new System One class of extraction models") · 未做  
  介绍专用提取模型的定位，关注它与通用模型在任务上的分工。

- **10-19** [Cloudflare 怎样降低 AI 代码审查推理费用](https://blog.cloudflare.com/obsessive-inference-optimization "Cutting our inference bill by 68% by being obsessive about optimization") · **已学习**  
  拆解请求、模型与服务优化，并核对文章里的成本比较口径。 [阅读报告](../ai-learning/reports/knowledge_reports/Cloudflare_AI代码审查推理成本优化_68%降本_深度解析_20261025.md)

- **10-15** [Cloudflare × OpenAI：AI 如何发现网站内容](https://blog.cloudflare.com/cloudflare-openai-discovery-agentic-web "Cloudflare and OpenAI: making AI discovery better for everyone | Cloudflare Blog") · 未做  
  介绍双方的研究试点，关注内容发现、网站和 AI 访问之间的关系。

</details>

<details>
<summary><strong>Amazon Science · 6 篇 · 2 篇已学习</strong></summary>

- **10-29** [面向旅行应用加速语言模型](https://www.amazon.science/blog/speeding-up-language-models-for-travel-applications "Speeding up language models for travel applications") · 未做  
  围绕具体业务任务优化模型速度，关注专用需求与通用能力的取舍。

- **10-23** [让有声书的语音合成更自然](https://www.amazon.science/blog/better-speech-synthesis-for-audiobooks "Better speech synthesis for audiobooks") · 未做  
  研究长篇朗读中的语音表现，关注文本到声音的生成质量。

- **10-22** [TorchNeuron 背后的系统设计](https://www.amazon.science/blog/the-science-behind-torchneuron-amazons-new-pytorch-backend-for-aws-trainium-chips "The science behind TorchNeuron, Amazon’s new PyTorch backend for AWS Trainium chips") · **已学习**  
  解释 Trainium 原生 PyTorch 后端的执行路径与算子支持。 [阅读报告](../ai-learning/reports/knowledge_reports/Amazon_TorchNeuron_Trainium原生PyTorch后端_深度解析_20261025.md)

- **10-20** [让第三方复核 AI 安全评估](https://www.amazon.science/blog/strengthening-ai-safety-evaluation-through-independent-third-party-review "Strengthening AI safety evaluation through independent third-party review") · **已学习**  
  通过 AVERI 案例检查评估本身，关注独立性与证据的可核查程度。 [阅读报告](../ai-learning/reports/knowledge_reports/Amazon_AVERI_第三方安全评估元评估_独立性与可核查边界_深度解析_20261025.md)

- **10-12** [改变模型架构，一定要从头训练吗](https://www.amazon.science/blog/can-we-change-an-ai-models-architecture-without-retraining-it-from-scratch "Can we change an AI model’s architecture without retraining it from scratch?") · 未做  
  研究复用已有训练成果的方法，关注架构改造的条件与代价。

- **10-01** [以图为中心的 Agent 智能](https://www.amazon.science/blog/graph-centric-agentic-intelligence "Graph-centric agentic intelligence") · 未做  
  讨论图结构怎样参与 Agent 的表示、组织与推理。

</details>

<details>
<summary><strong>Sakana AI · 7 篇</strong></summary>

- **10-30** [用 AI 分析美国中期选举的社交媒体信息](https://sakana.ai/us-midterms-analysis "Intelligence Report: SNSのAI分析からみる米中間選挙") · 未做  
  Sakana 展示公开信息分析案例，阅读时留意数据范围与推断边界。

- **10-28** [Sakana API Platform 企业早期访问](https://sakana.ai/api-platform-earlyaccess "Sakana API Platform、エンタープライズ向けにアーリーアクセスプログラムを開始") · 未做  
  介绍平台对外提供的能力与接入安排，作为产品能力更新查看。

- **10-23** [Sakana Aquarium：用本体组织决策 Agent](https://sakana.ai/aquarium-release "オントロジーを基盤に、意思決定・実行を支援するAIエージェントプラットフォーム「Sakana Aquarium」") · 未做  
  关注结构化业务知识如何连接分析、决策和执行。

- **10-20** [QD-Rec：兼顾质量和多样性的推荐](https://sakana.ai/qd-rec "オープンエンドな探索を意思決定支援へ：推薦の質と多様性を高める「QD-Rec」を提案") · 未做  
  把开放式搜索用于推荐，研究不只追求单一最优答案的方法。

- **10-15** [My Fish：看见 Sakana Chat 记住了什么](https://sakana.ai/my-fish "Sakana Chatが覚えていることを見てみよう：メモリを可視化する新機能「My Fish」") · 未做  
  介绍记忆可视化功能，关注用户如何理解和管理持久记忆。

- **10-12** [MASS：通过群体协作实现自我改进](https://sakana.ai/mass "Recursive Self-Improvement through Collective Intelligence") · 未做  
  研究多 Agent 集体搜索和递归改进，重点看评估与扩展条件。

- **10-09** [Sakana Namazu 接入医生证据检索](https://sakana.ai/namazu-aillis "医師向け検索ツール「Evidence Finder」にSakana Namazuを導入：日本仕様のAIを、医療の現場へ") · 未做  
  展示医疗信息搜索工具的应用，关注资料检索与专业使用场景。

</details>

<details>
<summary><strong>MiniMax · 2 篇 · 2 篇已学习</strong></summary>

- **10-22** [MiniMax Code Mini App](https://www.minimax.io/blog/minimax-code-mini-app-1792650729 "Introducing MiniMax Code Mini App") · **已学习**  
  把长时间运行的前后端应用接入 Agent，关注持久页面与插件运行方式。 [阅读报告](../ai-learning/reports/knowledge_reports/MiniMax_Code_Mini_App_持久工作面与Agent插件运行时_深度解析_20261026.md)

- **10-19** [MiniMax M3.1 Flash](https://www.minimax.io/blog/minimax-m31f "MiniMax M3.1 Flash: Redefining Agent Performance and Cost") · **已学习**  
  介绍 Agent 能力、成本定位与部署条件，并结合 vLLM 支持情况分析。 [阅读报告](../ai-learning/reports/knowledge_reports/MiniMax_M3_1_Flash_Agent模型与vLLM_Day0支持_深度解析_20261025.md)

</details>

<details>
<summary><strong>Mistral AI · 3 篇</strong></summary>

- **10-29** [Mistral Large 4 开放权重](https://mistral.ai/news/mistral-large-4-oss "Le Chonk: Built for Coders, Trusted by Defenders.") · 未做  
  聚焦编码与网络安全能力，关注开放版本、评测与使用条件。

- **10-22** [Voxtral 3：把听、说、推理与工具调用连起来](https://mistral.ai/news/voxtral-3 "Voxtral 3") · 未做

  介绍语音识别、语音合成与实时 Voice Agent SDK，关注多语言、打断处理及多步骤工具工作流。

- **10-06** [Mistral Large 4 首次发布](https://mistral.ai/news/mistral-large-4 "Introducing Mistral Large 4") · 未做  
  了解模型预览版的能力定位，与后续开放权重版本区分阅读。

</details>

<details>
<summary><strong>Manus · 5 篇 · 1 篇已学习</strong></summary>

- **10-30** [Manus 如何用自己的 Agent 重做工作流程](https://manus.im/blog/rebuilding-manus-with-manus "Rebuilding Manus with Manus: What changed, what broke, and how we work now") · 相关报告  
  复盘哪些改变有效、哪些地方出错，适合研究团队怎样实际使用 AI。 [相关报告](../ai-learning/reports/knowledge_reports/多设备多Agent共享Context与会话续接_Manus实践与架构边界_深度解析_20261029.md)

- **10-15** [Manus Automations：持续处理重复任务](https://manus.im/blog/introducing-automations "Introducing Automations: Put Repetitive Work on Autopilot") · 未做  
  介绍用 Agent 组织多步骤自动化，以及触发与执行方式。

- **10-13** [Manus for Business：团队共用项目上下文](https://manus.im/blog/manus-team-plan "Introducing Manus for Business: Become an AI-native company today") · **已学习**  
  把指令、资料、Skills 和连接器配置放入 Project，减少重复设置并支持团队协作。 [阅读报告](../ai-learning/reports/knowledge_reports/多设备多Agent共享Context与会话续接_Manus实践与架构边界_深度解析_20261029.md)

- **10-01** [Manus Game Dev：从想法到可玩的游戏](https://manus.im/blog/introducing-game-developer "Introducing Game Dev: Enabling Everyone to Make the Games They Want to Play") · 未做  
  展示游戏制作能力，关注生成之后怎样继续修改与迭代。

- **10-01** [Manus 2.0 的视频编辑器](https://manus.im/blog/introducing-video-editor "Introducing Video Editor in Manus 2.0: Anyone Can Now Make A Video Worth Posting") · 未做  
  把视频生成和编辑放进一个工作流程，介绍实际制作方式。

</details>


<details>
<summary><strong>Z.ai / 智谱 · 1 篇</strong></summary>

- **10-29** [AutoClaw 接入 GLM-5.3-flashX-Legal](https://autoclaw.z.ai/blog/model/GLM-5.3-flashX-Legal "GLM-5.3-flashX-Legal Is Now Available in AutoClaw - Z.ai") · 未做

  介绍法律模型在合同修订、证据核对和合规研究中的应用；能力与评测为官方自述。

</details>

[回到顶部](#顶尖技术博客更新)

<a id="m202609"></a>

## 2026 年 9 月

本次从 9 月 2 日开始补存量。

<details>
<summary><strong>OpenAI Developers · 4 篇 · 1 篇已学习</strong></summary>

- **09-23** [给 LED 屏接上语音助手](https://developers.openai.com/blog/bringing-my-led-display-to-life "Bringing my LED display to life with GPT-Live-1 and Codex") · 未做  
  用 Codex、GPT-Live-1 和树莓派，把一块显示屏变成可对话的设备。

- **09-11** [重新设计 Skills、AGENTS.md 与提示词](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra "Rethinking skills and prompts for GPT-6 Astra") · **已学习**  
  讨论模型能力变化后，哪些指令该保留，哪些会挤占上下文、限制发挥。 [阅读报告](../ai-learning/reports/knowledge_reports/GPT6_Astra指令架构_从Prompt堆叠到按需控制_深度解析_20261015.md)

- **09-04** [用 Astra 做建筑可视化](https://developers.openai.com/blog/architectural-visualization-with-astra "Architectural visualization with Astra") · 未做  
  从房屋设计到 Blender 镜头和 Unreal Engine 漫游，展示完整制作过程。

- **09-04** [用 Astra 制作太空探索游戏](https://developers.openai.com/blog/how-to-build-games-with-astra "Building games with Astra") · 未做  
  把概念、美术和程序生成串起来，展示 Codex 参与游戏开发的过程。

</details>

<details>
<summary><strong>OpenAI 研究与技术更新 · 8 篇 · 1 篇已学习</strong></summary>

- **09-28** [前沿模型训练需要怎样的安全论证](https://openai.com/index/towards-safety-cases-for-frontier-ai-training "Towards safety cases for frontier AI training") · 未做  
  讨论如何为训练过程建立可检查的安全证据，而不只给出安全承诺。

- **09-22** [Parallel 用 Astra 调整研究工作流](https://openai.com/index/parallel-cuts-time-and-cost-with-astra "Parallel cut research time and cost in half with GPT‑6 Astra") · 未做  
  介绍研究任务在时间与费用上的变化；阅读时留意任务范围与对照条件。

- **09-11** [ChatGPT 十亿用户存储架构：上篇](https://openai.com/index/scaling-storage-one-billion-users-part-one "Rapidly scaling online storage to serve over 1 billion ChatGPT users") · **已学习**  
  从流量增长出发，解释在线存储如何应对规模、热点与可靠性问题。 [阅读报告](../ai-learning/reports/knowledge_reports/OpenAI_十亿用户在线存储_CosmosDB多租户与可靠性_深度解析_20261025.md)

- **09-10** [GPT-Live-1：实时语音 API](https://openai.com/index/introducing-gpt-live-1-in-the-api "Build more natural voice experiences with GPT‑Live‑1 in the API") · 未做  
  介绍更自然的语音交互，以及开发者如何接入实时体验。

- **09-10** [Agents API 发布](https://openai.com/index/introducing-the-agents-api "Introducing the Agents API") · 未做  
  介绍面向 Agent 应用的新接口及其工作方式，适合追踪运行框架的变化。

- **09-10** [用 Codex 和 ChatGPT 寻找抗菌分子](https://openai.com/index/using-codex-chatgpt-to-search-for-new-antimicrobials "How a researcher uses Codex and ChatGPT to search for new antimicrobial molecules") · 未做  
  展示研究人员如何把代码、数据分析和候选分子筛选串起来。

- **09-06** [OpenAI 内部怎样用 AI 加速研究](https://openai.com/index/research-acceleration-view-inside-openai "Research acceleration: The view inside OpenAI") · 未做  
  从内部工作案例观察 AI 的实际帮助，以及仍需研究人员判断的环节。

- **09-03** [GPT-6 Astra 安全概览](https://openai.com/index/safety-overview-gpt-6-astra "Safety overview: GPT-6 Astra") · 未做  
  集中了解模型的风险评估与防护措施，和能力发布配合阅读。

</details>

<details>
<summary><strong>Anthropic · 7 篇</strong></summary>

- **09-30** [机器人现在能做哪些工作](https://www.anthropic.com/research/what-work-can-robots-do "What work can robots do?") · 未做  
  把任务能力与经济可行性分开评估，避免把演示成功等同于可规模化替代。

- **09-29** [人们到底希望 AI 做什么](https://www.anthropic.com/research/your-thoughts-on-ai "What do you want from AI?") · 未做  
  介绍面向公众的意见收集，关注使用需求、期待与担忧。

- **09-24** [Project Swap：当 Agent 替人交易](https://www.anthropic.com/research/project-swap "Project Swap: What happens when agents trade for us?") · 未做  
  搭建一个由 Agent 参与的小型市场，观察交易过程哪里有效、哪里失灵。

- **09-23** [Claude 发现新的酶系统线索](https://www.anthropic.com/research/claude-discovers-novel-enzyme-system "Claude discovers a novel enzyme system with CRISPR-like repeats") · 未做  
  介绍带有 CRISPR 类重复序列的发现过程，以及生物学证据。

- **09-17** [Claude 如何辅助生物分子建模](https://www.anthropic.com/research/claude-uplifts-biomolecular-modeling "How Claude is uplifting biomolecular modeling") · 未做  
  关注模型在专业研究任务中的帮助，及其与工具、领域知识的关系。

- **09-09** [近期网络安全事件的对齐评估](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents "An alignment assessment of recent cybersecurity incidents") · 未做  
  结合具体事件判断模型行为，了解风险分析如何落到可检查的案例上。

- **09-04** [形式化验证费马大定理](https://www.anthropic.com/research/formalizing-fermats-last-theorem "Formalizing Fermat&#x27;s Last Theorem") · 未做  
  介绍把数学论证转成形式化证明的工作，关注 AI 与验证工具的分工。

</details>

<details>
<summary><strong>Google Research · 2 篇</strong></summary>

- **09-29** [Diffusion Controller：统一图像生成控制](https://research.google/blog/how-diffusion-controller-unifies-and-simplifies-ai-image-generation "How Diffusion Controller unifies and simplifies AI image generation") · 未做  
  介绍如何用一套控制方式组织不同的图像生成需求。

- **09-24** [保持长视频连贯性的自动生成方法](https://research.google/blog/coherent-long-form-video-generation "Automating coherent long-form video generation") · 未做  
  关注长时间生成中内容一致性与制作流程的组织。

</details>

<details>
<summary><strong>Google DeepMind · 10 篇</strong></summary>

- **09-30** [Gemini 4 Argon 首次介绍](https://deepmind.google/blog/gemini-4-argon-our-next-era-of-frontier-intelligence "Gemini 4 Argon: our next era of frontier intelligence") · 未做  
  了解这一代模型的定位与能力方向，和后续详细发布区分阅读。

- **09-30** [SynthID Bio：生物领域的生成标记](https://deepmind.google/blog/introducing-synthid-bio "Introducing SynthID Bio") · 未做  
  介绍把生成内容识别技术延伸到生物领域的方案。

- **09-24** [Gemini Live Avatar：实时语音与虚拟形象](https://deepmind.google/blog/introducing-gemini-38-live-with-live-avatar "Introducing Gemini 3.8 Live with Live Avatar") · 未做  
  关注实时交互体验，以及声音与可视化角色怎样结合。

- **09-23** [Private AI Compute 的服务端安全记忆](https://deepmind.google/blog/advancing-private-ai-compute-with-secure-server-side-memory "Advancing Private AI Compute with secure, server-side memory") · 未做  
  讨论云端持久记忆如何兼顾个性化、隔离和隐私保护。

- **09-23** [Gemini 3.8 文本转语音](https://deepmind.google/blog/say-hello-to-gemini-38-text-to-speech "Gemini 3.8 text-to-speech says hello") · 未做  
  介绍语音生成能力，适合关注声音表现和应用接入。

- **09-15** [Gemini 3.8 Live 与扩展思考](https://deepmind.google/blog/introducing-gemini-3-8-live-and-3-8-live-extended-thinking "Introducing Gemini 3.8 Live and 3.8 Live Extended Thinking") · 未做  
  比较实时对话和更多推理计算的使用方式。

- **09-08** [AlphaGenome Atlas：人类基因变异预测图](https://deepmind.google/blog/alphagenome-atlas-a-predictive-map-of-every-possible-dna-letter-change-in-the-human-genome "AlphaGenome Atlas: A predictive map of every possible DNA letter change in the human genome") · 未做  
  把可能的 DNA 单字符变化组织成可查询预测，关注用途和验证边界。

- **09-03** [WeatherNext 3：全球天气预测模型](https://deepmind.google/blog/introducing-weathernext-3-our-most-advanced-and-accurate-global-weather-ai-model "Introducing WeatherNext 3, our most advanced and accurate global weather AI model") · 未做  
  介绍气象预测能力和官方评测，重点看任务与预测范围。

- **09-02** [Gemini 3.8 Flash 与 Flash Cyber](https://deepmind.google/blog/introducing-gemini-3-8-flash-and-38-flash-cyber "Introducing Gemini 3.8 Flash and 3.8 Flash Cyber") · 未做  
  分别关注通用快速模型和网络安全用途的能力与发布说明。

- **09-02** [面向机构的主动网络防御](https://deepmind.google/blog/proactive-cyber-defense-for-governments-and-enterprises "Proactive cyber defense for governments and enterprises") · 未做  
  讨论 AI 如何进入漏洞发现和防御流程，以及相应的使用边界。

</details>

<details>
<summary><strong>Google Developers · 3 篇</strong></summary>

- **09-15** [零信任 Agent：检查意图而不只是语法](https://developers.googleblog.com/build-zero-trust-ai-agents-that-judge-intent-not-just-syntax "Build zero-trust AI agents that judge intent, not just syntax") · 未做  
  讨论合法格式的调用仍可能违背目的时，如何设计额外的判断机制。

- **09-09** [ADK for Kotlin 1.0](https://developers.googleblog.com/announcing-adk-for-kotlin-10-building-production-ready-ai-agents-in-kotlin-android-and-beyond "Announcing ADK for Kotlin 1.0: Building Production-Ready AI Agents in Kotlin, Android, and Beyond") · 未做  
  面向 Kotlin、Android 等环境构建 Agent，介绍正式版本的开发能力。

- **09-09** [Harness 工程：评估、迭代与防护](https://developers.googleblog.com/the-anatomy-of-harness-engineering-how-to-evaluate-iterate-and-guard-ai-coding-agents "The Anatomy of Harness Engineering: How to Evaluate, Iterate, and Guard AI Coding Agents") · 未做  
  把编码 Agent 的运行流程作为设计对象，介绍如何持续验证和改进。

</details>

<details>
<summary><strong>Microsoft Research · 4 篇</strong></summary>

- **09-30** [用机器学习预警空间天气对电网的风险](https://www.microsoft.com/en-us/research/blog/forecasting-space-weather-risks-on-power-grids "Forecasting space weather risks on power grids") · 未做  
  把太阳活动的观测转成地面风险预测，关注提前量与实用性。

- **09-29** [Quine：面向复杂生物问题的研究系统](https://www.microsoft.com/en-us/research/blog/introducing-quine-an-ai-research-system-designed-for-the-complexity-of-biology "Introducing Quine: An AI research system designed for the complexity of biology") · 未做  
  介绍 AI 研究系统如何组织生物学中的多步骤分析。

- **09-23** [机器人推理卸载：端侧与远端怎么分工](https://www.microsoft.com/en-us/research/blog/offloaded-inference-for-real-world-physical-ai-robotics "Offloaded inference for real-world physical AI robotics") · 未做  
  研究真实机器人场景中算力、网络与响应时间的取舍。

- **09-21** [RetroChimera：预测小分子合成路径](https://www.microsoft.com/en-us/research/blog/improving-synthesis-prediction-of-small-molecules-at-scale-with-retrochimera "Improving synthesis prediction of small molecules at scale with RetroChimera") · 未做  
  介绍规模化合成预测，关注模型怎样支持化学研究。

</details>

<details>
<summary><strong>腾讯混元 · 1 篇</strong></summary>

- **09-21** [强化学习的 batch 越大越好吗](https://hy.tencent.ai/research/100116 "When Do Larger Batches Help Scale LLM Reinforcement Learning?") · 未做  
  把吞吐提升与学习效率损失放在一起，判断增大 batch 何时能更快达到目标。

</details>

<details>
<summary><strong>vLLM · 15 篇 · 1 篇已学习</strong></summary>

- **09-29** [把 vLLM 拆开部署：实用指南](https://vllm.ai/blog/2026-09-29-disaggregated-serving-guide "Taking vLLM Apart: A Practical Guide to Disaggregated Serving") · 未做  
  解释分离式服务的组件和取舍，适合从单机走向分布式部署。

- **09-24** [在 vLLM 中加入生成水印](https://vllm.ai/blog/2026-09-24-watermarking-in-vllm "Watermarking in vLLM") · 未做  
  介绍文本生成水印的服务支持，关注接入方式与适用范围。

- **09-22** [用一个 uv 参数缩短 vLLM 启动时间](https://vllm.ai/blog/2026-09-22-python-bytecode-startup "Reducing vLLM startup time with one uv flag") · 未做  
  从 Python 字节码处理入手，讨论启动开销优化。

- **09-22** [vllm-metal：Apple Silicon 上的并发服务](https://vllm.ai/blog/2026-09-22-vllm-metal-v0-28-0 "Announcing vllm-metal: Concurrent Serving on Apple Silicon") · 未做  
  关注 Mac 上多请求推理的支持方式与运行限制。

- **09-21** [Qwen3.8-2.4T 的预填充与解码分离](https://vllm.ai/blog/2026-09-21-qwen38-pd-serving "PD Serving of Qwen3.8-2.4T") · 未做  
  介绍超大模型服务时的部署拆分和系统配置。

- **09-18** [多 GPU 视频字幕生成](https://vllm.ai/blog/2026-09-18-pynvvideocodec "Scaling Multi-GPU Video Captioning with PyNvVideoCodec and vLLM") · 未做  
  将视频解码和 vLLM 推理组合，关注数据处理与算力利用。

- **09-15** [为 Kimi K3 训练 DSpark](https://vllm.ai/blog/2026-09-15-kimi-k3-dspark "How we trained the fastest DSpark for Kimi-K3 using GB300 NVL72") · 未做  
  介绍在 GB300 NVL72 上的训练过程及其服务目标。

- **09-15** [Chord：Kimi K2.x 的 INT4 MoE 推理](https://vllm.ai/blog/2026-09-15-novita-chord-w4a16-moe "vLLM x Novita AI: Chord, Faster INT4 MoE for Kimi K2.x. Up to 1.3x on H200, 2.15x on Untuned B300") · 未做  
  围绕低精度专家计算做优化，关注不同 GPU 上的收益差异。

- **09-14** [ROCm 上训练与 rollout 逐位一致](https://vllm.ai/blog/2026-09-14-rl-kernel-v0-1-0-train-rollout-bitwise-consistency "vime × RL-Kernel × AMD: Bitwise Train–Rollout Consistency on ROCm") · 未做  
  解释 RL-Kernel 如何处理训练和采样路径之间的计算差异。

- **09-13** [Kimi K3 吞吐优化过程](https://vllm.ai/blog/2026-09-13-kimi-k3-performance-optimization "Kimi K3 Performance Optimizations in vLLM: The Road to 2.8× Throughput") · 未做  
  逐项追踪服务瓶颈和改进，避免只看最终的倍数结论。

- **09-10** [MiniMax M3 在 MI355X 上的性能排查](https://vllm.ai/blog/2026-09-10-minimax-m3-mi355x "Following the Bottleneck: Optimizing MiniMax M3 on AMD Instinct MI355X") · 未做  
  从实际瓶颈出发，介绍 AMD 平台的推理优化路径。

- **09-10** [分层 KV Cache 卸载](https://vllm.ai/blog/2026-09-10-tiered-kv-offloading "Tiered KV Cache Offloading in vLLM") · 未做  
  把缓存放到不同存储层级，讨论显存容量、传输和延迟的取舍。

- **09-08** [GLM-5.3 推理优化：HiSparse 卸载](https://vllm.ai/blog/2026-09-08-glm53-part1-hybrid-sparse-offloading "GLM 5.3 Optimizations, Part 1: Hybrid HiSparse Offloading in vLLM") · **已学习**  
  解释稀疏注意力与缓存卸载如何配合，是后续并行优化篇的基础。 [阅读报告](../ai-learning/reports/knowledge_reports/GLM5_3_vLLM_PCP_DCP_HiSparse_百万上下文推理_深度解析_20261025.md)

- **09-08** [vLLM × AgentX：面向真实 Agent 请求优化](https://vllm.ai/blog/2026-09-08-vllm-agentx "vLLM x AgentX: Optimizing for Real-World Agentic Serving") · 未做  
  将多轮、工具调用等工作负载纳入服务评估。

- **09-07** [Tenstorrent 硬件上的 vLLM 插件](https://vllm.ai/blog/2026-09-07-vllm-tt-plugin "Serving LLMs on Tenstorrent Hardware: Inside the vLLM TT Plugin") · 未做  
  介绍新硬件后端怎样接入模型服务框架。

</details>

<details>
<summary><strong>PyTorch · 7 篇</strong></summary>

- **09-30** [Torch Spyre 如何验证上游兼容性](https://pytorch.org/blog/from-upstream-changes-to-downstream-confidence-inside-torch-spyres-integration-with-pytorch-crcr "From Upstream Changes to Downstream Confidence: Inside Torch Spyre’s Integration with PyTorch CRCR") · 未做  
  介绍持续集成和回归检查，避免框架更新破坏硬件后端。

- **09-22** [让 vLLM 模型实现不依赖特定硬件](https://pytorch.org/blog/hardware-agnostic-models-in-vllm "Hardware-Agnostic Models in vLLM") · 未做  
  讨论模型层与设备实现的解耦，降低新增后端的适配负担。

- **09-22** [Shopify 的持续学习闭环](https://pytorch.org/blog/how-shopify-built-a-continual-learning-loop-with-pytorch-and-vllm "How Shopify built a continual learning loop with PyTorch and vLLM") · 未做  
  把 PyTorch 训练和 vLLM 服务连接起来，观察模型如何从实际使用中更新。

- **09-21** [TinyTorch：亲手实现一个深度学习框架](https://pytorch.org/blog/tinytorch-dont-just-import-pytorch-build-it "TinyTorch: Don’t Just Import PyTorch. Build It.") · 未做  
  通过搭建基础组件理解 PyTorch 背后的机制，适合实践学习。

- **09-16** [低精度 Flash Attention 4](https://pytorch.org/blog/low-precision-flash-attention-4-end-to-end-block-scaled-attention-for-blackwell "Low Precision Flash Attention 4: End-to-End Block-Scaled Attention for Blackwell") · 未做  
  围绕块级缩放注意力，介绍 Blackwell 上的端到端实现。

- **09-11** [Helion × Hugging Face Kernels](https://pytorch.org/blog/helion-x-%f0%9f%a4%97-hf-kernels-building-and-shipping-out-of-the-box-performant-kernels "Helion x 🤗 HF Kernels: Building and Shipping Out-of-the-box Performant Kernels") · 未做  
  介绍如何开发、发布和分发可直接使用的高性能算子。

- **09-02** [PyTorch 2.14 发布说明](https://pytorch.org/blog/pytorch-2-14-release-blog "PyTorch 2.14 Release Blog") · 未做  
  作为前一版基线，查看本版功能和兼容性变化。

</details>

<details>
<summary><strong>AMD ROCm · 24 篇</strong></summary>

- **09-30** [AIM：从配置发现到模型部署](https://rocm.blogs.amd.com/artificial-intelligence/aims-deployment-exp/README.html "AIM: Unified User Experience from Profile Discovery to Deployment") · 未做  
  关注模型运行配置如何被发现、选择和投入使用。

- **09-30** [在 Ryzen AI Max+ 小主机上运行机器人策略](https://rocm.blogs.amd.com/artificial-intelligence/molmoact2-ryzers-strix/README.html "Running MolmoAct2 Robot Policy on an AMD Ryzen AI Max+ 395 Mini PC") · 未做  
  介绍 MolmoAct2 的本地部署，便于理解桌面设备的能力边界。

- **09-30** [TraceLens Agent：自动定位性能瓶颈](https://rocm.blogs.amd.com/software-tools-optimization/tracelens-analysis-agent/README.html "Automating Performance Bottleneck Identification with the TraceLens Agent") · 未做  
  让 Agent 读取性能轨迹并辅助分析，关注诊断过程的可检查性。

- **09-29** [强化学习机械臂的 Sim-to-Real](https://rocm.blogs.amd.com/artificial-intelligence/sim2real-rl-instinct/README.html "Unlocking Sim2Real for a Robotic Arm with RL Accelerated by AMD Instinct GPUs") · 未做  
  介绍从仿真训练到真实设备迁移的流程与困难。

- **09-28** [Verl 0.9.0 与 ROCm 10.0](https://rocm.blogs.amd.com/artificial-intelligence/verl_0.9.0_rocm7.15/README.html "Verl 0.9.0 on ROCm™ 10.0: Next-Generation RL Post-Training on AMD Instinct™ GPUs") · 未做  
  介绍 AMD GPU 上的 RL 后训练支持与版本组合。

- **09-25** [模型参数都分布在哪里](https://rocm.blogs.amd.com/artificial-intelligence/model-weight-profiles/README.html "Model Weight Profiles: Where Do the Parameters Go?") · 未做  
  用权重分布分析理解显存需求与模型结构。

- **09-25** [Strix Halo 上的本地量化和多后端部署](https://rocm.blogs.amd.com/artificial-intelligence/quark-strix-halo/README.html "Local Quantization and Multi-Backend Deployment with AMD Quark on Strix Halo") · 未做  
  通过 AMD Quark 处理模型量化，关注从转换到实际运行的完整链路。

- **09-25** [UltraQuant：Qwen3.8 的低精度 Agent 服务](https://rocm.blogs.amd.com/software-tools-optimization/ultraquant-kv4/README.html "UltraQuant on AMD Instinct: More Efficient Agentic Serving for Qwen3.8-MXFP4") · 未做  
  讨论量化后的服务效率，以及缓存、计算与质量之间的取舍。

- **09-23** [排查 RL 训练中的 logprob 不一致](https://rocm.blogs.amd.com/software-tools-optimization/logprob-debug/README.html "Debugging Logprob Mismatches in LLM Reinforcement Learning") · 未做  
  解释如何定位训练与生成路径之间的概率计算差异。

- **09-22** [Zebra-HyLo：把 Transformer 改造成混合模型](https://rocm.blogs.amd.com/artificial-intelligence/hylo-long-context/README.html "Zebra-HyLo: Upcycling Transformers into Long-Context Hybrid LLMs on AMD Instinct™ GPUs") · 未做  
  研究复用已有模型、扩展长上下文能力的方法。

- **09-22** [比较 Kimi K3 的三种推理框架](https://rocm.blogs.amd.com/artificial-intelligence/kimi-k3-mad/README.html "Benchmarking Kimi-K3 Across vLLM, SGLang, and ATOM on MI350X") · 未做  
  在同一 AMD 平台比较 vLLM、SGLang 与 ATOM，关注测试配置。

- **09-22** [Advanced Thread Trace：深入观察 GPU 执行](https://rocm.blogs.amd.com/software-tools-optimization/profiling-guide/att/README.html "Performance Profiling on AMD GPUs - Part 6: Advanced Thread Trace (ATT) - The Microscope for Your Application") · 未做  
  通过线程级轨迹排查性能问题，补充宏观指标看不到的细节。

- **09-21** [GLM-5.2 何时适合预填充上下文并行](https://rocm.blogs.amd.com/artificial-intelligence/glm52-mxfp4-mi355/README.html "Serving GLM-5.2-MXFP4 on AMD Instinct™ MI355X: When Prefill Context Parallelism Pays") · 未做  
  分析长输入服务中并行开销与收益的平衡点。

- **09-21** [Hyperloom：多 Agent 自动优化推理](https://rocm.blogs.amd.com/software-tools-optimization/hyperloom-optimization/README.html "Hyperloom: A Multi-Agent Harness for Autonomous Inference Optimization on AMD GPUs") · 未做  
  介绍面向 AMD GPU 的优化 Harness，关注尝试、评估与结果验证。

- **09-17** [复现 AMD MLPerf Inference v6.1](https://rocm.blogs.amd.com/artificial-intelligence/mlperf-inf_v6.1-repro/README.html "Reproducing AMD MLPerf Inference v6.1 Submission Results") · 未做  
  提供官方测试的复现路线，便于检查结果对应的环境和配置。

- **09-17** [用 FlyDSL 编写扩散注意力算子](https://rocm.blogs.amd.com/software-tools-optimization/flydsl-customized-attention/README.html "Implementing a High-Performance Custom Diffusion Attention Kernel with FlyDSL") · 未做  
  从具体内核示例理解布局、计算和性能调优。

- **09-16** [MI355X 上的 DFlash 投机解码](https://rocm.blogs.amd.com/artificial-intelligence/dflash-on-MI355x/README.html "DFlash Speculative Decoding on AMD Instinct MI355X: Up to 5× Faster Qwen3.5 Inference") · 未做  
  介绍 Qwen3.5 的解码加速方案；性能需结合工作负载判断。

- **09-16** [AMD MLPerf v6.1 的技术细节](https://rocm.blogs.amd.com/artificial-intelligence/mlperf-inf-v6.1/README.html "Technical Dive into AMD MLPerf Inference v6.1 Submission") · 未做  
  拆解官方提交中的软件、硬件和优化条件。

- **09-15** [Poro2 与知识图谱处理医疗文本](https://rocm.blogs.amd.com/artificial-intelligence/poro2-knowledge-graph/README.html "Knowledge Graph Integration With Poro2 For Enriching Medical Text Processing") · 未做  
  把语言模型与结构化知识结合，关注信息补充和文本理解。

- **09-15** [用 ROCprof Compute Viewer 看线程轨迹](https://rocm.blogs.amd.com/software-tools-optimization/thread-trace/README.html "Thread Trace Part 1: ROCprof Compute Viewer") · 未做  
  介绍性能调试工具的基本使用与观察方式。

- **09-14** [从简单到高效：GEMM 实现阶梯](https://rocm.blogs.amd.com/software-tools-optimization/hipkittens-gemm-ladder/README.html "An Educational GEMM Ladder for Helios GPUs") · 未做  
  通过逐步优化的矩阵乘法示例理解 GPU 编程。

- **09-09** [缩小 hipBLASLt 内核调优的搜索范围](https://rocm.blogs.amd.com/software-tools-optimization/iteratively-tuning-hipblaslt/README.html "Iteratively Tuning hipBLASLt TensileLite Kernels: A Smaller Search, a Faster Kernel") · 未做  
  围绕 TensileLite 做迭代调优，关注搜索成本与性能收益。

- **09-08** [把 NVFP4 在线转换为 MXFP4](https://rocm.blogs.amd.com/software-tools-optimization/nvfp4-to-mxfp4/README.html "Efficiently Serving NVFP4 Models on AMD Instinct™ MI350X/MI355X Accelerators via Online NVFP4 to Quark MXFP4 Requantization") · 未做  
  介绍 NVIDIA 格式模型在 AMD 平台上的量化格式适配。

- **09-08** [veRL 在 AMD 上的后训练实践](https://rocm.blogs.amd.com/software-tools-optimization/verl/README.html "veRL on AMD: Production-Ready RL Post-Training on ROCm") · 未做  
  讨论 RL 后训练的软件栈与运行条件，适合准备部署的读者。

</details>

<details>
<summary><strong>NVIDIA 技术博客 · 32 篇</strong></summary>

- **09-30** [NeMo Relay：追踪 Agent Harness 的行为](https://developer.nvidia.com/blog/tracing-agent-harness-behavior-with-nvidia-nemo-relay "Tracing Agent Harness Behavior with NVIDIA NeMo Relay") · 未做  
  让运行流程留下可分析的轨迹，帮助定位行为和性能问题。

- **09-29** [TensorRT Model Connect 的 AI 开发经验](https://developer.nvidia.com/blog/ai-native-by-design-lessons-learned-from-building-nvidia-tensorrt-model-connect "AI Native by Design: Lessons Learned from Building NVIDIA TensorRT Model Connect") · 未做  
  分享构建过程中的设计取舍，观察 AI 工具如何影响软件工程。

- **09-29** [VSS Blueprint 3.3：视觉 Agent 的成本优化](https://developer.nvidia.com/blog/lower-the-cost-of-building-and-running-visual-ai-agents-with-nvidia-vss-blueprint-3-3 "Lower the Cost of Building and Running Visual AI Agents with NVIDIA VSS Blueprint 3.3") · 未做  
  关注视觉工作流的构建和运行费用，以及组件选择。

- **09-28** [给 Agent 加上 OpenShell 运行时控制](https://developer.nvidia.com/blog/add-runtime-controls-to-ai-agents-with-nvidia-openshell "Add Runtime Controls to AI Agents with NVIDIA OpenShell") · 相关报告  
  解释如何在执行环境中落实权限与操作边界。 [相关报告](../ai-learning/reports/knowledge_reports/NVIDIA_OpenShell_Sentry_Agent运行时安全架构_深度解析_20261021.md)

- **09-28** [Open Agent Safety Platform：持续监测参考方案](https://developer.nvidia.com/blog/nvidia-open-agent-safety-platform-a-reference-for-continuous-in-silicon-agent-monitoring "NVIDIA Open Agent Safety Platform: A Reference for Continuous In-Silicon Agent Monitoring") · 相关报告  
  从基础设施层观察 Agent 安全，关注持续监测如何参与防护。 [相关报告](../ai-learning/reports/knowledge_reports/NVIDIA_OpenShell_Sentry_Agent运行时安全架构_深度解析_20261021.md)

- **09-24** [生物基础模型的 MoE 训练](https://developer.nvidia.com/blog/efficient-moe-training-for-biological-foundation-models "Efficient MoE Training for Biological Foundation Models") · 未做  
  介绍专家模型在生物任务中的训练效率优化。

- **09-23** [SWE-Serve：本地测试通过之后呢](https://developer.nvidia.com/blog/how-swe-serve-exposes-the-gap-between-local-tests-and-live-serving "How SWE-Serve Exposes the Gap Between Local Tests and Live Serving") · 未做  
  通过真实服务评测，暴露开发测试与线上运行之间的差距。

- **09-23** [NV-Reason-CT：开放的三维 CT 视觉语言模型](https://developer.nvidia.com/blog/introducing-nv-reason-ct-open-3d-ct-vlm-for-radiologist-chain-of-thought-reasoning "Introducing NV-Reason-CT Open 3D CT VLM for Radiologist Chain-of-Thought Reasoning") · 未做  
  面向放射影像推理，介绍模型及其专业任务定位。

- **09-23** [NodeWright：管理 Kubernetes 节点群](https://developer.nvidia.com/blog/manage-kubernetes-node-fleets-with-nodewright "Manage Kubernetes Node Fleets with NodeWright") · 未做  
  关注支撑 AI 工作负载的节点管理与集群维护。

- **09-23** [AI 任务启动前先检查 GPU 集群](https://developer.nvidia.com/blog/validate-gpu-cluster-readiness-before-ai-workloads-land "Validate GPU Cluster Readiness Before AI Workloads Land") · 未做  
  介绍就绪检查，减少配置和环境问题进入昂贵运行阶段。

- **09-22** [用 Agent 和 Isaac ROS 加速 ROS 2 节点](https://developer.nvidia.com/blog/accelerating-a-ros-2-node-with-an-ai-agent-and-nvidia-isaac-ros "Accelerating a ROS 2 Node with an AI Agent and NVIDIA Isaac ROS") · 未做  
  把机器人软件优化变成可执行工作流，关注迁移与验证。

- **09-22** [机密计算如何保护生产推理](https://developer.nvidia.com/blog/enabling-private-high-performance-production-ai-inference-with-nvidia-confidential-computing "Enabling Private High-Performance Production AI Inference with NVIDIA Confidential Computing") · 未做  
  讨论数据隐私与推理性能的结合，以及部署时的边界。

- **09-21** [Agent 评估：从工具调用到任务完成](https://developer.nvidia.com/blog/how-to-evaluate-ai-agents-from-tool-calls-to-task-completion "How to Evaluate AI Agents From Tool Calls to Task Completion") · 未做  
  区分过程指标和最终结果，介绍更完整的评估方法。

- **09-21** [Dynamo-Triton 的多设备模型服务](https://developer.nvidia.com/blog/simplifying-model-serving-across-multiple-gpus-with-nvidia-tensorrt-multi-device-integration-in-nvidia-dynamo-triton "Simplifying Model Serving Across Multiple GPUs with NVIDIA TensorRT Multi-Device Integration in NVIDIA Dynamo-Triton") · 未做  
  介绍 TensorRT 跨多块 GPU 的集成，降低服务部署复杂度。

- **09-18** [AIPerf：规模化测量 LLM 推理](https://developer.nvidia.com/blog/benchmarking-llm-inference-at-scale-with-aiperf "Benchmarking LLM Inference at Scale with AIPerf") · 未做  
  关注负载生成、指标和测试口径，适合建立性能比较基线。

- **09-16** [用 Agent 准备三维仿真场景](https://developer.nvidia.com/blog/how-to-use-ai-agents-to-prepare-3d-scenes-for-simulation "How to Use AI Agents to Prepare 3D Scenes for Simulation") · 未做  
  介绍场景处理工作流，减少人工准备机器学习环境的工作。

- **09-16** [Jetson 上的 TensorRT Edge-LLM 评测](https://developer.nvidia.com/blog/tensorrt-edge-llm-completes-the-mlperf-edge-agentic-benchmark-6-4x-faster-on-jetson-agx-thor "TensorRT Edge-LLM Completes the MLPerf Edge Agentic Benchmark 6.4x Faster on Jetson AGX Thor") · 未做  
  介绍边缘 Agent 基准测试；官方加速倍数需结合硬件与任务理解。

- **09-16** [用 Agent 把 CUDA Tile 代码从 Python 转到 Rust](https://developer.nvidia.com/blog/translating-cuda-tile-operations-from-python-to-rust-using-agentic-ai "Translating CUDA Tile Operations from Python to Rust Using Agentic AI") · 未做  
  通过语言迁移案例，观察 GPU 代码生成后的验证要求。

- **09-15** [稠密模型还是 MoE：怎样选择](https://developer.nvidia.com/blog/dense-vs-moe-models-active-parameters-throughput-and-when-to-choose-each "Dense vs. MoE Models: Active Parameters, Throughput, and When to Choose Each") · 未做  
  比较活跃参数、吞吐和使用场景，避免只用总参数量判断。

- **09-15** [Groq 3 LPX：确定性执行与交互式推理](https://developer.nvidia.com/blog/how-nvidia-groq-3-lpx-deterministic-execution-drives-power-efficient-high-interactivity-inference-on-nvidia-vera-rubin "How NVIDIA Groq 3 LPX Deterministic Execution Drives Power-Efficient High-Interactivity Inference on NVIDIA Vera Rubin") · 未做  
  讨论执行方式如何影响能耗和交互响应，结合 Vera Rubin 平台介绍。

- **09-15** [NVLink 6 的多层可靠性设计](https://developer.nvidia.com/blog/how-nvidia-nvlink-6-delivers-multi-layer-resiliency-for-ai-factories "How NVIDIA NVLink 6 Delivers Multi-Layer Resiliency for AI Factories") · 未做  
  从互联层解释 AI 集群如何应对故障和运行扰动。

- **09-14** [在 JAX 中加速无丢弃 MoE 训练](https://developer.nvidia.com/blog/accelerating-dropless-moe-training-in-jax-with-nvidia-transformer-engine "Accelerating Dropless MoE Training in JAX with NVIDIA Transformer Engine") · 未做  
  介绍 Transformer Engine 对专家训练的支持和优化。

- **09-10** [BioNeMo 的高吞吐结构预测](https://developer.nvidia.com/blog/high-throughput-structure-prediction-with-bionemo-inference-runtime "High-Throughput Structure Prediction with BioNeMo Inference Runtime") · 未做  
  关注生物模型的批量推理与运行时组织。

- **09-10** [Nemotron 3 Ultra 的 NIM 全栈优化](https://developer.nvidia.com/blog/how-full-stack-nim-optimizations-deliver-2-5x-more-users-on-nemotron-3-ultra "How Full-Stack NIM Optimizations Deliver 2.5x More Users on Nemotron 3 Ultra") · 未做  
  从模型到服务栈分析并发能力，注意官方测试的具体配置。

- **09-09** [CUDA 13.4：Windows on Arm 与 GPU 共享控制](https://developer.nvidia.com/blog/cuda-toolkit-13-4-adds-windows-on-arm-support-and-greater-control-over-shared-gpus "CUDA Toolkit 13.4 Adds Windows on Arm Support and Greater Control over Shared GPUs") · 未做  
  集中查看工具链的平台支持和共享 GPU 管理变化。

- **09-09** [多模态服务何时适合拆分编码、预填充与解码](https://developer.nvidia.com/blog/when-to-use-encode-prefill-decode-disaggregation-to-accelerate-multimodal-model-serving "When to Use Encode-Prefill-Decode Disaggregation to Accelerate Multimodal Model Serving") · 未做  
  分析三阶段拆分的收益与通信开销，避免为拆分而拆分。

- **09-08** [CUDA Rust：两条 GPU 内核开发路线](https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels "Introducing CUDA Rust: Two Tracks for Writing GPU Kernels") · 未做  
  介绍用 Rust 编写 GPU 计算的选择及工具支持。

- **09-04** [用 NemoClaw 构建带记忆的 Agent](https://developer.nvidia.com/blog/building-a-memory-driven-agent-with-nvidia-nemoclaw "Building a Memory-Driven Agent with NVIDIA NemoClaw") · 相关报告  
  关注记忆如何进入实际工作流，可与运行时安全研究配合阅读。 [相关报告](../ai-learning/reports/knowledge_reports/NVIDIA_OpenShell_Sentry_Agent运行时安全架构_深度解析_20261021.md)

- **09-04** [在 Jetson 上部署和优化推理模型](https://developer.nvidia.com/blog/frontier-reasoning-reaches-the-edge-how-to-deploy-and-optimize-models-on-nvidia-jetson "Frontier Reasoning Reaches the Edge: How to Deploy and Optimize Models on NVIDIA Jetson") · 未做  
  介绍边缘硬件的模型运行流程，以及优化时的资源限制。

- **09-03** [PAIR：在局域网内调度可用推理算力](https://developer.nvidia.com/blog/nvidia-pair-virtual-inference-router-expands-available-compute-on-your-local-network "NVIDIA PAIR Virtual Inference Router Expands Available Compute on Your Local Network") · 未做  
  通过虚拟路由组织本地网络中的设备，关注算力共享的实现方式。

- **09-02** [把投机解码纳入模型协同设计](https://developer.nvidia.com/blog/co-designing-ai-models-using-speculative-decoding-for-faster-llm-inference "Co-Designing AI Models Using Speculative Decoding for Faster LLM Inference") · 未做  
  从模型设计阶段考虑推理加速，而不只在部署后追加优化。

- **09-02** [现代 CUDA 工具箱的逐步优化示例](https://developer.nvidia.com/blog/the-modern-cuda-toolbox-in-practice-a-step-by-step-optimization-walkthrough "The Modern CUDA Toolbox in Practice: A Step-by-Step Optimization Walkthrough") · 未做  
  用完整过程说明怎样测量、定位和改善 GPU 代码。

</details>

<details>
<summary><strong>Hugging Face 与机构作者 · 7 篇</strong></summary>

- **09-29** [MCP Agent 的来源感知核验](https://huggingface.co/blog/MultiverseComputingCAI/getting-the-source-right-not-just-the-fact-source "Getting the Source Right, Not Just the Fact: Source-Aware Verification for MCP Agents") · 未做  
  不只检查事实是否正确，也检查它是否来自合适、可信的来源。

- **09-28** [Holo4：通用电脑操作 Agent](https://huggingface.co/blog/Hcompany/holo4 "Holo4: powering generalist computer-use agents") · 未做  
  H Company 介绍 computer-use 模型与任务能力。

- **09-22** [让评测结果更容易复现](https://huggingface.co/blog/evaleval-aisi "How UK AISI and EvalEval Are Making Benchmark Results Reproducible") · 未做  
  UK AISI 与 EvalEval 介绍基准复现工作，关注配置与结果可比性。

- **09-15** [Agent 这次做对，下次还能做对吗](https://huggingface.co/blog/ibm-research/altk-evolve-consistency "Your Agent Aced the Task. Will It Do It Again?") · 未做  
  IBM 讨论重复运行的一致性，适合补充单次成功率之外的可靠性评估。

- **09-03** [Funes：让编码 Agent 使用可自行管理的记忆](https://huggingface.co/blog/funes "Give Your Coding Agents a Memory You Own") · 未做  
  介绍记忆工具的接入，关注长期积累怎样跨任务使用。

- **09-03** [用 GRPO 改善小模型的结构化输出](https://huggingface.co/blog/grpo-with-trl-ifstruct "Fine-tuning a 350M Model for Better Structured Outputs in 100 GRPO Steps") · 未做  
  以小规模训练示例说明格式能力如何学习，关注评测与训练设定。

- **09-03** [用 TRL 和 OpenEnv 训练模型写代码画水彩](https://huggingface.co/blog/train-to-paint-with-code "Training a coding model to paint watercolours with TRL and OpenEnv") · 未做  
  把代码生成和环境反馈接起来，展示强化学习实验的完整玩法。

</details>

<details>
<summary><strong>Amazon Science · 3 篇</strong></summary>

- **09-25** [Trainium 上的实时视频生成内核](https://www.amazon.science/blog/a-kernel-centric-path-to-real-time-video-generation-on-trainium "A kernel-centric path to real-time video generation on Trainium") · 未做  
  从算子工程理解视频生成延迟，关注硬件与算法的配合。

- **09-21** [让模型设计和描述抗体](https://www.amazon.science/blog/advancing-ai-for-biology-teaching-models-to-design-and-characterize-antibodies "Advancing AI for biology: Teaching models to design and characterize antibodies") · 未做  
  围绕生物任务介绍训练与评估，区分模型候选和实验结果。

- **09-10** [机器学习研究 Agent 为什么没有过拟合](https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit "Why don’t machine learning research agents overfit?") · 未做  
  研究自动实验与评估之间的关系，关注结论成立的任务条件。

</details>

<details>
<summary><strong>Sakana AI · 7 篇</strong></summary>

- **09-28** [SAIL：扩展上下文内模仿学习](https://sakana.ai/sail "SAIL: Scaling In-Context Imitation Learning") · 未做  
  研究从上下文中的示范学习，关注模型如何利用已有行为经验。

- **09-17** [Sakana Chat 更新模型并加入记忆](https://sakana.ai/chat-fugumax "Sakana Chatをアップデート：最新モデルに刷新、メモリー機能を追加") · 未做  
  了解聊天产品的长期记忆入口及使用方式。

- **09-16** [Sakana Marlin：与报告对话](https://sakana.ai/marlin-update "Sakana Marlinアップデート：レポートと対話する「Interactive Reading」と、出力スライドのPowerPoint対応") · 未做  
  增加交互式阅读和 PowerPoint 输出，关注研究产物如何继续被使用。

- **09-14** [不用反向传播训练千层网络](https://sakana.ai/pc-alm "Training 1000-layer networks without backpropagation") · 未做  
  介绍 PC-ALM 路线，关注训练方法和实验成立的条件。

- **09-12** [世界模型研究的前沿综述](https://sakana.ai/world-models-royal-society-issue "英国王立協会特集号に見る、世界モデルの最前線とAIの未来") · 未做  
  结合英国皇家学会专题讨论，梳理世界模型的研究方向。

- **09-11** [Fugu Max 与 Fugu Ultra v2](https://sakana.ai/fugu-max-release "Introducing Fugu Max and Fugu Ultra v2: Orchestrating the Pareto Frontier") · 未做  
  围绕性能取舍和模型编排介绍新版本，而不只比较单个模型得分。

- **09-03** [Percept-Lens：深入研究 AI 图像检测](https://sakana.ai/percept-lens "Percept-Lens: A Deep Dive into AI-Generated Image Detection") · 未做  
  关注生成图像的识别方法、评测及其局限。

</details>

<details>
<summary><strong>DeepSeek · 1 篇 · 1 篇已学习</strong></summary>

- **09-10** [DeepSeek-V4.1-Flash](https://www.deepseek.com/en/news/deepseek-v4-1-flash "Introducing DeepSeek-V4.1-Flash: smarter, faster, more efficient.") · **已学习**  
  介绍模型的能力与效率更新；已有报告进一步拆解架构和 KV 压缩。 [阅读报告](../ai-learning/reports/knowledge_reports/DeepSeek-V4.1-Flash架构解剖_CED非对称与KV压缩极限_20260919.md)

</details>

<details>
<summary><strong>Manus · 2 篇</strong></summary>

- **09-29** [Manus Flex：接入自己的模型 API](https://manus.im/blog/introducing-manus-flex "Introducing Manus Flex: Use your own API key in the Manus workspace") · 未做  
  在同一工作空间选择推理供应商、模型和思考强度。

- **09-28** [Manus 2.0：Cascade、Cloud Computer 与新工作流](https://manus.im/blog/introducing-manus-2-0 "Introducing Manus 2.0") · 相关报告  
  介绍新一代运行架构和产品入口，关注任务怎样持续执行。 [相关报告](../ai-learning/reports/knowledge_reports/多设备多Agent共享Context与会话续接_Manus实践与架构边界_深度解析_20261029.md)

</details>

[回到顶部](#顶尖技术博客更新)

<a id="studied"></a>

## 已有学习报告

本轮清单中，47 篇原文对应 37 份已完成报告。有些报告研究一个系列或比较多篇原文，因此两者数量不同。

<details>
<summary><strong>展开报告速查</strong></summary>

- [常驻 Agent：控制面隔离与权限交集](../ai-learning/reports/knowledge_reports/常驻Agent安全_控制面隔离与权限交集_深度解析_20261115.md) · 对应本页 1 篇原文。

- [CodeRabbit：多 Agent 审查、评测与运行时验证](../ai-learning/reports/knowledge_reports/CodeRabbit_多Agent代码审查_评测与运行时验证_深度解析_20261110.md) · 对应本页 1 篇原文；案例原页全文未核验。

- [Anthropic Agent 记忆：显著性、Dreaming 与纠错](../ai-learning/reports/knowledge_reports/Anthropic_Agent记忆组件_显著性判断与Dreaming_深度解析_20261108.md) · 对应本页 1 篇原文。
- [Agent 逐字输出与断线恢复（全链路续篇）](../ai-learning/reports/knowledge_reports/Agent请求全链路_流式响应与断线恢复_科普讲解_20261102.md) · 对应本页 1 篇原文。
- [Kimi K3.1 Pro](../ai-learning/reports/knowledge_reports/Kimi_K3_1_Pro_联合RL_长程Agent与开放权重_深度解析_20261026.md) · 对应本页 1 篇原文。
- [DeepSeek-V4.1-Flash 的机架级服务](../ai-learning/reports/knowledge_reports/vLLM_DeepSeek-V4.1-Flash_PD分离与Wide-EP机架级服务_深度解析_20261025.md) · 对应本页 2 篇原文。
- [TensorRT 全局性能调优](../ai-learning/reports/knowledge_reports/TensorRT_GlobalPerformanceTuner_可搜索build_route与精度感知调优_深度解析_20261025.md) · 对应本页 2 篇原文。
- [ChatGPT 十亿用户存储架构](../ai-learning/reports/knowledge_reports/OpenAI_十亿用户在线存储_CosmosDB多租户与可靠性_深度解析_20261025.md) · 对应本页 2 篇原文。
- [Microduck：从仿真训练到实机](../ai-learning/reports/knowledge_reports/NVIDIA_Microduck_Agentic_Robotics_仿真训练与Sim2Real_深度解析_20261025.md) · 对应本页 2 篇原文。
- [MiniMax M3.1 Flash 与 vLLM 支持](../ai-learning/reports/knowledge_reports/MiniMax_M3_1_Flash_Agent模型与vLLM_Day0支持_深度解析_20261025.md) · 对应本页 2 篇原文。
- [GLM-5.3 推理优化：PCP、DCP 与 HiSparse](../ai-learning/reports/knowledge_reports/GLM5_3_vLLM_PCP_DCP_HiSparse_百万上下文推理_深度解析_20261025.md) · 对应本页 2 篇原文。
- [分布式 3D Gaussian Splatting](../ai-learning/reports/knowledge_reports/AMD_分布式3D_Gaussian_Splatting_Gaussian分片与RCCL_深度解析_20261025.md) · 对应本页 1 篇原文。
- [RDNA 4 的 FP8 GEMM 优化](../ai-learning/reports/knowledge_reports/AMD_RDNA4_FP8_GEMM_WMMA与Tile搜索_深度解析_20261025.md) · 对应本页 1 篇原文。
- [Decisions API：让应用更快作出响应](../ai-learning/reports/knowledge_reports/OpenAI_Decisions_API_低延迟决策与响应式应用_深度解析_20261025.md) · 对应本页 1 篇原文。
- [MiniMax Code Mini App](../ai-learning/reports/knowledge_reports/MiniMax_Code_Mini_App_持久工作面与Agent插件运行时_深度解析_20261026.md) · 对应本页 1 篇原文。
- [ThinkingBox：把数据库评分变成 RL 奖励](../ai-learning/reports/knowledge_reports/Microsoft_ThinkingBox_数据库评分转RL奖励与Agent后训练_深度解析_20261025.md) · 对应本页 2 篇原文。
- [Flint-interactive：可交互的数据可视化语言](../ai-learning/reports/knowledge_reports/Flint_interactive_交互式数据可视化语言_语义事件与更新算子_深度解析_20261025.md) · 对应本页 1 篇原文。
- [TorchNeuron：Trainium 的原生 PyTorch 后端](../ai-learning/reports/knowledge_reports/Amazon_TorchNeuron_Trainium原生PyTorch后端_深度解析_20261025.md) · 对应本页 2 篇原文。
- [Humming：量化推理的高性能算子库](../ai-learning/reports/knowledge_reports/vLLM_Humming_量化推理Kernel库_深度解析_20261025.md) · 对应本页 1 篇原文。
- [TorchTitan：新模型、规模化训练与 TitanRL](../ai-learning/reports/knowledge_reports/PyTorch_TorchTitan_SOTA模型规模化训练与TitanRL_深度解析_20261025.md) · 对应本页 1 篇原文。
- [FlyDSL：在 AMD GPU 上加速 PyTorch](../ai-learning/reports/knowledge_reports/PyTorch_FlyDSL_AMD_GPU_Kernel加速_深度解析_20261025.md) · 对应本页 1 篇原文。
- [让数千个 Agent 并行分析生物数据](../ai-learning/reports/knowledge_reports/OpenAI_千Agent并行生物数据研究_证据聚合与科学发现_深度解析_20261025.md) · 对应本页 1 篇原文。
- [OpenShell 的规模化 Agent 安全架构](../ai-learning/reports/knowledge_reports/NVIDIA_OpenShell_Sentry_Agent运行时安全架构_深度解析_20261021.md) · 对应本页 2 篇原文。
- [TPU 上的 vLLM 与 SGLang 新推理引擎](../ai-learning/reports/knowledge_reports/Google_TPU_vLLM_SGLang_TorchTPU推理引擎_能力矩阵与口径核验_深度解析_20261025.md) · 对应本页 1 篇原文。
- [让第三方复核 AI 安全评估](../ai-learning/reports/knowledge_reports/Amazon_AVERI_第三方安全评估元评估_独立性与可核查边界_深度解析_20261025.md) · 对应本页 1 篇原文。
- [MegaKernel：低延迟交互式推理](../ai-learning/reports/knowledge_reports/AMD_ROCm_MegaKernel_MI355X交互式单请求推理_深度解析_20261025.md) · 对应本页 1 篇原文。
- [ALTK-Evolve：从经验中学习客服工作方法](../ai-learning/reports/knowledge_reports/ALTK_Evolve_学习型Memory与Agent服务任务_深度解析_20261021.md) · 对应本页 1 篇原文。
- [CUDA Tile 加速 Mamba-2](../ai-learning/reports/knowledge_reports/NVIDIA_CUDA_Tile_Mamba2高性能Kernel_深度解析_20261021.md) · 对应本页 1 篇原文。
- [Cloudflare 怎样降低 AI 代码审查推理费用](../ai-learning/reports/knowledge_reports/Cloudflare_AI代码审查推理成本优化_68%降本_深度解析_20261025.md) · 对应本页 1 篇原文。
- [自主湿实验室：让 Agent 接受现实检验](../ai-learning/reports/knowledge_reports/Google_自主湿实验室Agent_生物现实约束与闭环_深度解析_20261021.md) · 对应本页 1 篇原文。
- [先规划还是先找工具](../ai-learning/reports/paper_analyses/49_plan_retrieve_tool_discovery_2026.md) · 对应本页 1 篇原文。
- [MLX 与 RDMA：多台 Mac 协同推理](../ai-learning/reports/knowledge_reports/Apple_MLX_RDMA_Mac_Studio分布式大模型推理_深度解析_20261021.md) · 对应本页 1 篇原文。
- [Deep Review：分段核验长文和技术材料](../ai-learning/reports/paper_analyses/50_paper_assistant_tool_deep_review_2026.md) · 对应本页 1 篇原文。
- [GPT-6 如何维护大型代码库](../ai-learning/reports/knowledge_reports/GPT6软件维护_从广义侦察到证据驱动清理_深度解析_20261020.md) · 对应本页 1 篇原文。
- [Manus for Business：团队共用项目上下文](../ai-learning/reports/knowledge_reports/多设备多Agent共享Context与会话续接_Manus实践与架构边界_深度解析_20261029.md) · 对应本页 1 篇原文。
- [重新设计 Skills、AGENTS.md 与提示词](../ai-learning/reports/knowledge_reports/GPT6_Astra指令架构_从Prompt堆叠到按需控制_深度解析_20261015.md) · 对应本页 1 篇原文。
- [DeepSeek-V4.1-Flash](../ai-learning/reports/knowledge_reports/DeepSeek-V4.1-Flash架构解剖_CED非对称与KV压缩极限_20260919.md) · 对应本页 1 篇原文。

</details>

<a id="month-only"></a>

## 原文只公布了月份

以下 Apple 研究页只标明月份，保留原始精度，不补造日期，也不计入上面的逐日统计。均未找到对应学习报告。

| 原文月份 | 文章与导读 |
| --- | --- |
| 2026-10 | [强模型到底需要多复杂的 Harness？](https://machinelearning.apple.com/research/harness-autonomous-ml-engineering) 研究自主机器学习工程任务中，运行框架的作用与复杂度。 |
| 2026-10 | [RISED：跨环境选择与自蒸馏](https://machinelearning.apple.com/research/rised-multi-environment-selection) 用评价标准组织多环境 Agent 训练。 |
| 2026-10 | [Normalizing Trajectory Models](https://machinelearning.apple.com/research/normalizing-trajectory-models) 研究生成轨迹的建模方式，与逐步扩散路线比较。 |
| 2026-09 | [共享、选择性的持久记忆](https://machinelearning.apple.com/research/shared-selective-persistent-memory) 研究编码 Agent 怎样在多个任务之间复用有用经验；具体日期未公布。 |

<a id="undated"></a>

## 原文已找到，发布日期待补

这些条目已取得正文，但尚未核实完整发布时间，可能含更早的文章。先保留阅读入口，不把搜索显示的日期当成发布日，也不计入逐日收录数量。

<details>
<summary><strong>Google Research：本轮新发现，日期待核实</strong></summary>

- [Antigravity /teamwork：协同解决科学与工程问题](https://research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature "Advancing science &amp; engineering with Antigravity’s /teamwork") · 未做。汇集数学、形式化验证、分子结构与内核优化等协作案例，介绍模型生成与外部验证的配合；结果为官方报告。
- [Agile Deliberation：帮助人明确主观分类标准](https://research.google/blog/agile-deliberation-how-ai-helps-humans-define-the-gray-areas "Agile Deliberation: How AI helps humans define the gray areas") · 未做。用交互式讨论澄清图像分类中的模糊边界，让标注标准更一致。
- [用可穿戴传感器检测高血压迹象](https://research.google/blog/detecting-signs-of-hypertension-using-wearable-sensors "Detecting signs of hypertension using wearable sensors") · 未做。研究用消费级智能手表信号识别高血压风险；属于研究方法，不代替临床诊断。

2026-11-15 已取得三篇正文，但阅读结果未保留发布日期，官方 RSS 与原始页面回源均连接失败；日期留待下次核实，不计入近期文章数量。

</details>

<details>
<summary><strong>Ai2：待补日期的研究文章</strong></summary>

- [Olmo 3 与 Nextcloud：透明、可审计的自托管 AI](https://allenai.org/blog/nextcloud) · 未做。正文已读；本轮未取得确切发布日期，原始页面返回 403，不采用搜索的相对日期。
- [LitPivot：用动态文献检索发展研究想法](https://allenai.org/blog/litpivot) · 未做。让新论文影响研究方向，而不只是最后补参考文献。
- [Olmo-core 3：开放的规模化训练基础设施](https://allenai.org/blog/olmocore3) · 未做。介绍 MoE 训练系统与框架更新。
- [OlmoEarth 1.3：全球卫星数据嵌入](https://allenai.org/blog/olmoearth-v1-3) · 未做。介绍模型与预计算地理表示。
- [FairStress：更深入地评估模型公平性](https://allenai.org/blog/fairstress) · 未做。不只看最终选择，也检查决策过程中的差异。
- [BenchMIRT：基准究竟测量了什么](https://allenai.org/blog/benchmirt) · 未做。分析单道题目如何影响模型能力评估。
- [AstaBrief：开放的快速报告生成模型](https://allenai.org/blog/astabrief) · 未做。关注科学资料检索、证据综合和报告生成。
- [Bolmo：让语言模型直接处理字节](https://allenai.org/blog/bolmo-nature) · 未做。介绍字节级模型的研究与后续开放产物。
- [Goodfire 用开放后训练栈研究行为变化](https://allenai.org/blog/goodfire-olmo) · 未做。观察偏好训练怎样改变模型表现。
- [PLANTEUR：热带农作物制图基准](https://allenai.org/blog/planteur) · 未做。研究遥感模型在不同地理环境中的表现。
- [AI 辅助科学研究中真正困难的部分](https://allenai.org/blog/swedish-autodiscovery-recap) · 未做。讨论从文献搜索、数据分析到假设验证的实际难点。
- [让未来科学家学会质疑 AI 研究工具](https://allenai.org/blog/autodiscovery-student-challenge) · 未做。通过 AutoDiscovery 的使用案例讨论研究结果的检查。

</details>

<details>
<summary><strong>Z.ai 与 Anthropic：待补日期的文章</strong></summary>

- [GLM-Legal：专业法律 Agent](https://z.ai/blog/glm-legal) · 未做。介绍面向法律专业工作的模型与 Agent 能力。
- [GLM 如何构建自己的推理基础设施](https://z.ai/blog/glm-built-its-inference-infrastructure) · 未做。关注模型参与基础设施开发与自我改进的实践。
- [GLM-5.3 官方介绍](https://z.ai/blog/glm-5.3) · 相关报告。模型发布日待核实；已有 [vLLM 长上下文推理研究](../ai-learning/reports/knowledge_reports/GLM5_3_vLLM_PCP_DCP_HiSparse_百万上下文推理_深度解析_20261025.md)。
- [Anthropic 经济情景模型](https://www.anthropic.com/institute/econ-scenarios) · **已学习**。将 AI 能力与采用假设映射到经济情景；已有 [深度报告](../ai-learning/reports/knowledge_reports/Anthropic经济情景模型_深度解析_20260911.md)。本次页面未提供可核实的完整发布日期。

</details>

<a id="older"></a>

## 已学习的旧文

这几篇原文早于本轮时间范围，已有学习报告。单独保留，方便回看。

- **2026-07-16 · 已学习** [Kimi K3：开放前沿模型](https://www.kimi.com/blog/kimi-k3)  
  已有从信息流和模型结构入手的科普报告。 [阅读报告](../ai-learning/reports/knowledge_reports/KimiK3_信息流三方向_科普讲解_20260728.md)

- **2026-07-09 · 已学习** [Manus Branch：同一个起点，多个独立方向](https://manus.im/blog/manus-branch)  
  从指定消息分出新的会话，继承当时的历史、文件与指令。 [阅读报告](../ai-learning/reports/knowledge_reports/多设备多Agent共享Context与会话续接_Manus实践与架构边界_深度解析_20261029.md)

- **2026-05-06 · 已学习** [Manus Projects：从每次任务中学习](https://manus.im/blog/manus-projects-self-updating)  
  把可复用经验提出为项目更新建议，经确认后应用。 [阅读报告](../ai-learning/reports/knowledge_reports/多设备多Agent共享Context与会话续接_Manus实践与架构边界_深度解析_20261029.md)

- **2025-10-29 · 已学习** [Manus Wide Research：怎样绕开单个上下文窗口](https://manus.im/blog/manus-wide-research-solve-context-problem)  
  让多个独立工作单元分工，再汇总结果；并不意味着共享一个模型输入窗口。 [阅读报告](../ai-learning/reports/knowledge_reports/多设备多Agent共享Context与会话续接_Manus实践与架构边界_深度解析_20261029.md)

<a id="coverage"></a>

## 渠道获取情况

2026-11-15 已检查注册表全部 28 个渠道，并按缺口补查官方目录、原文与关键词漏选项。本次新增 18 篇日期已核实的文章；原有条目、导读和报告链接继续保留。日期取自 RSS、原文或官方目录，不采用搜索相对时间。

阅读器丢失 XML、返回旧快照或读取失败时，回读同一官方来源；压缩的 RSS 解压后再核对条目。部分目录仍只返回旧内容或页面外壳，已记录在下表，不将“未获取到”写成“没有更新”。 Google Research 的三篇候选已取得正文，但尚未核实日期，单列在待补区，不计入新增。

搜索命中的 Depth Anything 3、Seedance 2.5 与 Decoupled DiLoCo，经原始页面确认分别为 2025 年 11 月、2026 年 7 月和 2026 年 4 月旧文，未作为近期新增。此前 Language Explorer 的 11 月 9 日原文日期、MiniMax H3-Image 的 11 月 11 日页面日期继续保留。

| 渠道 | 累计已收录 | 获取情况与待补项 |
| --- | ---: | --- |
| [OpenAI Developers](https://developers.openai.com/blog/) | 9 | 搜索补到常驻 Agent 安全文，已回读正文与原始 HTML，确认发表于 11 月 12 日；目录快照仍偏旧，历史缺口保留。 |
| [OpenAI 研究与技术更新](https://openai.com/news/) | 40 | 已核对官方 RSS 与正文，新增 ChatGPT Wallet；律所访谈仍未取得足够正文，培训、采购和促销公告未纳入。 |
| [Anthropic](https://www.anthropic.com/engineering) | 28 | 工程与研究目录补到 11 月 13 日的安全评测指南，已回读正文；新闻目录中的非技术公告未纳入，旧经济情景文章日期缺口保留。 |
| [Google Research](https://research.google/blog/) | 13 | RSS 与原始页面回源连接失败，搜索补到 /teamwork、Agile Deliberation 和可穿戴高血压检测；已取得正文但尚未核实日期，单列待补，不计入近期新增。 |
| [Google DeepMind](https://deepmind.google/discover/blog/) | 27 | 已复查目录并解压官方 RSS，补入 Gemini 4 Hydrogen 与天气 AI 数据开放两篇。天气文章 RSS 日期与正文冲突，原始 HTML 确认发表于 11 月 13 日，按原文收录；搜索中的 DiLoCo 等旧文未作新增。 |
| [Google Developers](https://developers.googleblog.com/) | 18 | 已复查搜索和目录，返回内容仍偏旧；家居与 A2A 等候选未取得近期发布日期，近期及分页历史仍可能遗漏。 |
| [Microsoft Research](https://www.microsoft.com/en-us/research/blog/) | 12 | 已核对官方 RSS 并复查目录，窗口内的 Lazarus 研究已收录；本轮未取得需新增的日期已核实条目，历史覆盖仍主要从 9 月下旬开始。 |
| [Apple 机器学习研究](https://machinelearning.apple.com/) | 15 | 已核对官方订阅，窗口内返回的四篇均已收录；另有 4 篇只标月份，9 月历史可能不全。 |
| [Meta AI / FAIR](https://ai.meta.com/blog/) | 0 | 本轮搜索未取得可核实的窗口内新文；此前目录与近期覆盖不足的缺口保留。 |
| [Ai2](https://allenai.org/blog) | 1 | 本轮搜索未取得需新增的官网条目；官方 Hugging Face 机构文章 XYBench 收入下方对应渠道，不重复计数，旧文日期缺口保留。 |
| [ByteDance Seed](https://seed.bytedance.com/en/) | 0 | 搜索命中 Depth Anything 3 与 Seedance 2.5，已读正文并核对原始 HTML，分别发表于 2025 年 11 月和 2026 年 7 月，不计为近期新文；招聘公告未纳入。 |
| [腾讯混元](https://hy.tencent.ai/research) | 3 | 本轮搜索未取得日期已核实的新增条目；已有 Hy4、Hyra 2.0 及此前目录快照缺口保留。 |
| [Qwen](https://qwen.ai/blog) | 0 | 搜索返回多个模型和 AgentWorld 候选，但回读仍为动态页面外壳，未取得可核实的近期发布日期；保留获取缺口。 |
| [Kimi](https://www.kimi.com/blog) | 1 | 本轮搜索命中 K2 Thinking 旧候选，未取得近期发布日期；已有 K3 条目与 vLLM 适配文继续保留，不重复计数。 |
| [vLLM](https://vllm.ai/blog/) | 44 | 已核对官方订阅，窗口内四篇均已收录；既有 VeRL-Omni 和编码器拆分条目保留，本轮未重复新增。 |
| [PyTorch](https://pytorch.org/blog/) | 33 | 已核对官方 RSS 并复查目录，窗口内五篇已收录；本轮未取得需新增的日期已核实条目。 |
| [AMD ROCm](https://rocm.blogs.amd.com/blog.html) | 65 | 已核对官方 RSS 与正文，新增 RCCL / rocSHMEM 中 GPU 发起 SDMA 的通信优化文章。 |
| [NVIDIA 技术博客](https://developer.nvidia.com/blog/) | 87 | 已核对官方 RSS 与正文，新增 cuBLAS FP64、cuPhoton 黑洞干涉测量、cuDLA Python、双 DGX Station 部署 GLM-5.3，以及 SOMA 动作重定向五篇。 |
| [Hugging Face 与机构作者](https://huggingface.co/blog) | 43 | 已核对官方订阅与机构原文，新增 NVIDIA SimReady、Ai2 XYBench、llama.cpp 1.0 和 IBM LLMON 四篇；云市场支付公告未纳入。 |
| [GitHub AI & ML](https://github.blog/ai-and-ml/) | 6 | 已核对官方 RSS，窗口内的 Agent Skills 实践指南已收录；9 月历史覆盖仍有限。 |
| [Cloudflare AI](https://blog.cloudflare.com/) | 9 | 已核对官方 RSS 与正文，新增 Kitesurf 开源和 AI 安全测试编排的防御分析；通用用量计费、共识算法和基金公告未纳入。 |
| [Amazon Science](https://www.amazon.science/blog) | 12 | 已核对官方 RSS 与正文，补入 11 月 11 日 Tiros 自动推理验证网络隔离的文章；Mitra-v2 已收录。 |
| [Sakana AI](https://sakana.ai/blog) | 15 | 已核对官方订阅，本轮未取得窗口内新增技术条目；顾问任命等人事公告未纳入，既有日英文条目保留。 |
| [MiniMax](https://www.minimax.io/blog) | 3 | 已复查搜索与目录，H3-Image 已收录，本轮未取得更多日期已核实的条目；目录快照缺口保留。 |
| [Mistral AI](https://mistral.ai/news) | 4 | 已复查搜索与官方目录，最新可见的 Studio 已收录；本轮未取得日期已核实的新增条目。 |
| [Z.ai / 智谱](https://z.ai/blog) | 6 | 本轮搜索未取得日期已核实的新增条目；此前目录快照偏旧与主站旧文日期缺口保留。 |
| [DeepSeek](https://www.deepseek.com/en/news) | 1 | 已核对官方 sitemap，阅读器丢失 XML 后回读公开来源，未取得已核实日期的近期新增条目；发布信号源不代表全部研究产出。 |
| [Manus](https://manus.im/blog) | 7 | 已复查搜索与目录，新增候选主要为通用游戏工具与创意指南，未纳入技术清单；既有研究、工程条目和报告链接保留。 |

## 日期与学习记录怎么维护

- 发布日期取自原文、官方目录或官方订阅。页面修改时间、搜索抓取时间和报告写作时间分别看待；日期冲突未解决时先放入待补区。
- 中文导读依据官方标题、摘要和已读正文，方便选题；文章中的性能与效果仍是作者的主张。需要深入判断时，继续看原文及对应报告。
- 后续新增文章合并进相应月份，更新检查日期和学习状态。较短时间的刷新保留历史条目，已写好的导读和报告链接也保留。
- 同文镜像、中英文版本和跟踪参数不重复计数；系列文章有各自内容时分别保留。
- 新完成的学习报告补回原条目；只有引用关系或相关背景时标「相关报告」。

维护入口：[技术博客雷达](./skills/ai-tech-blog-radar/SKILL.md) · [官方渠道清单](./sources/ai-tech-blogs.json) · [全部学习报告](../docs/REPORT_INDEX.md)
