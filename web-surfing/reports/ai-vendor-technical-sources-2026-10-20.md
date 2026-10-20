---
title: "AI 厂商官方技术源雷达：内容质量与订阅可行性实测"
domain: "web-surfing"
report_type: "web_report"
status: "completed"
updated_on: "2026-10-20"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "standard"
reader_contract: "standalone"
semantic_tags: ["ai_sources", "technical_blogs", "vendor_research", "rss", "content_radar"]
related_entities: ["openai", "anthropic", "google_deepmind", "microsoft_research", "qwen", "kimi"]
---

# AI 厂商官方技术源雷达：内容质量与订阅可行性实测

> 核验时间：2026-10-20。范围只含厂商与实验室官方一手源；个人博客、媒体、Newsletter 和社交账号留到下一轮。

## 结论

厂商官方源值得做，而且已经能稳定找到与 OpenAI《Rethinking skills and prompts for GPT-6 Astra》同类的高价值材料。真正有效的订阅单位应是**技术栏目、URL 路径与主题过滤器**，不能把整个厂商官网都当成技术源。

本轮从 25 个以上候选入口中抽读了 40 余个官方页面或代表文章，并实测 RSS、sitemap、HTML 列表和搜索通道。建议首期只保留 **20 个来源：12 个必看、8 个观察**：

- **必看**：能持续给出机制、实验、工程经验或开放产物，足以触发学习任务。
- **观察**：重要但噪声、营销、自报 benchmark 或更新量较高；先做标题和摘要筛选，命中后再读原文。
- **不收为固定源**：没有稳定技术栏目，或内容以产品发布、论文索引、公司新闻为主；重大事件再按厂商名搜索。

RSS 不能单独解决订阅。20 个核心源中，当前有 8 个目标栏目能通过官方 RSS/Atom 发现更新；其余需要 sitemap、HTML 列表或官方域名搜索补齐。OpenAI Developer Blog 是最典型的反例：页面声明的 `developers.openai.com/rss.xml` 是开发文档总 feed，实测 138 条中没有 Blog 文章，若直接订阅会漏掉本次作为标杆的技术博客。

## 范围与判断方法

每个候选至少检查以下项目：

1. 官方入口能否稳定定位近期内容；
2. 抽读代表文章是否包含机制、实验设计、失败模式、数字口径、代码/模型/论文等可复核产物；
3. 更新是否主要由客户案例、融资、合作和产品宣传构成；
4. RSS/Atom、sitemap、HTML 列表或搜索中，哪一种能可靠发现新增内容；
5. 该源适合直接触发深读，还是只适合发出“有新版本”的提醒。

网页正文优先通过项目的 eacli `web.search` / `web.read` 读取。eacli 不暴露 HTTP Content-Type、XML 根节点和 feed 条目时，才用只读 HTTP 对 RSS、sitemap 与页面 `<link rel="alternate">` 做内容级核验。

## 必看：12 个核心源

| 来源 | 抽读样本与实际价值 | 更新与订阅 | 结论 |
|---|---|---|---|
| [OpenAI Developer Blog](https://developers.openai.com/blog/) + 研究型 Index | [Rethinking skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) 给出渐进披露、完成条件和 eval 方法；[Harness engineering](https://openai.com/index/harness-engineering) 披露 3 名工程师、约 1500 个 PR、百万行 agent 生成代码后的仓库设计经验。 | **无可用的 Blog 专用 RSS**。使用 [developer sitemap index](https://developers.openai.com/sitemap-index.xml) 过滤 `/blog/`；主站 [News RSS](https://openai.com/news/rss.xml) 只作补充并过滤客户案例。 | 必看。OpenAI 全站更新不能直接进入阅读队列。 |
| [Anthropic Engineering](https://www.anthropic.com/engineering) + [Research](https://www.anthropic.com/research) | [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 从真实失败模式推导跨会话状态、增量开发和测试合同；[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) 是生产 eval 教程。 | 未发现可靠 RSS；[官方 sitemap](https://www.anthropic.com/sitemap.xml) 可过滤 `/engineering/` 与 `/research/`，并带 `lastmod`。 | 必看。当前最接近 OpenAI Developer Blog 的稳定对照源。 |
| [Google Research Blog](https://research.google/blog/) | [Deep Review](https://research.google/blog/analyzing-technical-documents-with-deep-review/) 公开文档分段、多智能体审查和四个顶会试点；[Agentic Privacy and Security](https://research.google/blog/open-and-emergent-problems-in-agentic-privacy-and-security-a-contextual-angle/) 给出上下文完整性与动态评估框架。 | [官方 RSS](https://research.google/blog/rss/) 可用；实测近 30 天约 10 篇。 | 必看。研究解释通常比产品发布页更完整。 |
| [Google DeepMind Blog](https://deepmind.google/discover/blog/) | [Private AI Compute memory](https://deepmind.google/blog/advancing-private-ai-compute-with-secure-server-side-memory/) 给出安全 enclave、设备派生密钥与服务端记忆架构；[EmbeddingGemma 2](https://deepmind.google/blog/embeddinggemma-2-an-open-lightweight-multimodal-embedding-model/) 连接模型卡和完整评测。 | [官方 RSS](https://deepmind.google/blog/rss.xml) 可用；实测近 30 天约 11 篇。需过滤合作、地区发布和纯产品公告。 | 必看，但只收研究、安全、架构和模型机制。 |
| [Microsoft Research Blog](https://www.microsoft.com/en-us/research/blog/) | [AgentRx](https://www.microsoft.com/en-us/research/blog/systematic-debugging-for-ai-agents-introducing-the-agentrx-framework) 给出 115 条人工标注失败轨迹及 +23.6% 定位改进；[SkillOpt](https://www.microsoft.com/en-us/research/blog/skillopt-agent-skills-as-trainable-parameters) 覆盖 6 个 benchmark、7 个模型、52 个评测单元。 | [官方 RSS](https://www.microsoft.com/en-us/research/feed/) 在 eacli 复核通道可读；本机直接访问偶发 403，因此保留 HTML 列表或官方域名搜索作为 fallback。 | 必看。agent、评估、系统与人机协作内容密度高。 |
| [Apple Machine Learning Research](https://machinelearning.apple.com/) | [Tool Discovery Architectures](https://machinelearning.apple.com/research/plan-retrieve-tool-discovery) 与 [Self-Compacting Language Model Agents](https://machinelearning.apple.com/research/self-compacting-language-agents) 直接给研究摘要和论文入口。 | [官方 RSS](https://machinelearning.apple.com/rss.xml) 可用；更新常随会议集中出现。 | 必看。网页偏摘要，命中后应继续读论文。 |
| [AI at Meta / FAIR](https://ai.meta.com/blog/) | [FAIR agents, robustness and architecture release](https://ai.meta.com/blog/meta-fair-updates-agents-robustness-safety-architecture/) 同时给模型、代码与数据；[robotics release](https://ai.meta.com/blog/fair-robotics-open-source/) 包含 10 万任务的 PARTNR benchmark。 | 未发现 RSS；HTML 列表可读，官方 sitemap 在本机受 403 限制。按 `site:ai.meta.com/blog` 每周检索更稳。 | 必看。只收 FAIR 研究与开放产物，过滤消费产品宣传。 |
| [Ai2 Blog](https://allenai.org/blog) | [DR Tulu](https://allenai.org/blog/dr-tulu) 公开训练 recipe、checkpoint、RLER 与 MCP agent library；[AstaBrief](https://allenai.org/blog/astabrief) 披露 SFT/DPO 数据、95% judge-human 一致率和约 6000 条 DPO 样本。 | 未发现可靠 RSS，本机直连偶发 403；HTML 列表与官方域名搜索可用。 | 必看。开放训练过程和可复现实物是其主要优势。 |
| [ByteDance Seed](https://seed.bytedance.com/en/) | [EdgeBench](https://seed.bytedance.com/en/blog/edgebench-measuring-real-world-environment-learning-and-discovering-a-new-scaling-law) 包含 134 个超长任务、每项至少 12 小时、已开放 51 项及评测框架；Seed 模型文章通常附模型、数据或报告入口。 | 无 RSS；官方 sitemap 含 Blog URL，但 XML 末尾存在结构异常，自动化时应优先轮询 `blog_list` HTML，再用 sitemap 作提示。 | 必看。中文厂商中研究解释和开放产物较完整。 |
| [Tencent HY Research](https://hy.tencent.ai/research) | `Learning from context is harder than we thought`、[CL-bench Life](https://hy.tencent.ai/research/100039) 与 [Hyra](https://hy.tencent.ai/research/hyra) 聚焦 context learning、scaffold 和 RL 训练效率，首页摘要直接给出实验设计与量化结果。 | 无 RSS；本机直连受 EdgeOne 567 限制，但 eacli 网页读取和官方域名搜索可用。 | 必看。新源，当前技术密度很高；先观察半年稳定性。 |
| [Qwen Blog](https://qwen.ai/blog) | [Qwen3-Coder](https://qwenlm.github.io/blog/qwen3-coder/) 披露 480B/35B MoE、7.5T token 和 long-horizon RL；Qwen3.5 等新站文章继续覆盖架构、训练与 agent 评估。 | 当前站点无 RSS且为动态页面；旧站 sitemap 已基本冻结。用新站 HTML 列表加官方域名搜索。 | 必看。重大模型文通常足以进入深读，但 benchmark 仍按厂商自报处理。 |
| [Kimi Research & Tech Blog](https://www.kimi.com/blog) | [Kimi K3](https://www.kimi.com/blog/kimi-k3) 披露 2.8T 参数、KDA/AttnRes、GPU kernel 和编译器实验；[Agent Swarm](https://www.kimi.com/blog/agent-swarm) 展示 100 sub-agent 产品路线并明确是早期研究预览。 | 无 RSS；Blog HTML 列表可读，sitemap 只覆盖部分页面。以 HTML 列表为主，官方搜索为兜底。 | 必看。模型技术文很强，产品研究预览需要另行验证。 |

## 观察：8 个重要但需过滤的源

| 来源 | 为什么有价值 | 主要问题 | 订阅建议 |
|---|---|---|---|
| [NVIDIA Technical Blog](https://developer.nvidia.com/blog/) | [Mamba-2 CUDA Tile](https://developer.nvidia.com/blog/accelerating-mamba-2-with-high-performance-forward-pass-kernels-in-nvidia-cuda-tile/) 可深入到 kernel 与硬件 benchmark；[agent eval](https://developer.nvidia.com/blog/how-to-evaluate-ai-agents-from-tool-calls-to-task-completion/) 解释 step/E2E、环境状态和多次 trial。 | 实测 RSS 近 30 天约 41 篇，大量内容服务 NVIDIA 产品。 | 订阅 [RSS](https://developer.nvidia.com/blog/feed/)，只保留 inference、kernel、agent eval、CUDA、系统优化等主题。 |
| [Hugging Face Blog](https://huggingface.co/blog) | [开源生态年度数据](https://huggingface.co/blog/huggingface/state-of-os-hf-spring-2026) 与 [复现 2200 篇 ICML 论文](https://huggingface.co/blog/icml-2026-open-reproductions) 有独家平台数据和真实实验。 | 官方、合作方和社区作者混在同一 feed；实测近 30 天约 21 篇。 | 订阅 [RSS](https://huggingface.co/blog/feed.xml)，优先 Hugging Face 官方作者、平台数据与复现实验。 |
| [Amazon Science Blog](https://www.amazon.science/blog) | [研究 agent 为何不过拟合](https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit) 和 [graph-centric agents](https://www.amazon.science/blog/graph-centric-agentic-intelligence) 有完整论证与实验背景。 | 学科范围很广，RSS 混入公司研究新闻。 | 订阅 [RSS](https://www.amazon.science/index.rss)，只收 `/blog/`，再按 agent、ML systems、reasoning 过滤。 |
| [Sakana AI Blog](https://sakana.ai/blog) | AI Scientist、SAIL、[collective self-improvement](https://sakana.ai/mass/) 等选题原创性高。 | feed 混合日文产品、公司新闻和研究，部分网页只是论文摘要入口。 | 订阅 [Atom](https://sakana.ai/feed.xml)，只提升带论文、代码或实验的研究条目。 |
| [MiniMax Blog](https://www.minimax.io/blog) | [M3](https://www.minimax.io/blog/minimax-m3) 对 MSA、1M context、operator 优化和 agent 训练给出较多细节；[MaxProof](https://www.minimax.io/blog/minimax-maxproof-math-proof-evolution) 是完整技术路线文。 | 新闻、产品与技术博客并存；无 RSS，sitemap 对 Blog 覆盖不完整。 | HTML Blog 列表加官方域名搜索；只有技术博客触发深读。 |
| [Mistral News](https://mistral.ai/news) | [Physics AI](https://mistral.ai/news/physics-ai-research) 链接技术报告和数据集；[Mistral Large 4](https://mistral.ai/news/mistral-large-4) 有架构规模和 agent benchmark。 | 同一列表混入融资、地区扩张、合作与产品公告，模型文仍以自报成绩为主。 | HTML 列表；按 `technical report / research / architecture / open weights` 过滤。 |
| [Z.ai Blog](https://z.ai/blog) | [GLM-5.3](https://z.ai/blog/glm-5.3) 覆盖代码、长任务 RL、网络安全能力和 token-efficiency；[GLM-5](https://z.ai/blog/glm-5) 介绍异步 RL infra。 | 无 RSS，官方 sitemap 不包含 Blog；自建 benchmark 和厂商比较占比较高。 | 官方域名搜索兜底；涉及重大能力数字时等待模型卡、代码或独立评测。 |
| [DeepSeek Research & News](https://www.deepseek.com/en/news) | 发布影响大，sitemap 简洁，适合第一时间发现模型、论文和开源仓库。 | 抽读 V4 Preview 与 V4.1 Flash 后，正文主要是简短规格、价格和 benchmark 图，通常不足以单独支撑深度学习报告。 | 轮询 [sitemap](https://www.deepseek.com/sitemap.xml)；命中新发布后继续读论文、GitHub 与 model card。 |

## 暂不进入固定名单

以下主体仍可能产生重要材料，但当前不值得占用固定订阅位：

- **xAI News**：模型发布文能提供 benchmark 与安全口径，但整体仍是产品发布页，未发现独立技术/研究栏目和可靠 RSS；重大版本时搜索即可。
- **Cohere Labs**：官方 Research 页和技术报告 PDF 有价值，但更像论文索引，不像持续解释技术判断的博客；后续放入论文雷达更合适。
- **BAAI、上海 AI Lab、百度研究、DAMO**：有论文、模型、新闻和社区内容，尚未找到一个同时满足高技术密度、稳定更新、低噪声和可订阅性的统一官方栏目。按模型/论文发布触发搜索即可。
- **AWS/Azure/Google Cloud/Databricks/Together 等应用与云工程博客**：文章量大、产品绑定强。后续可单独做“AI 工程实践源”，不与前沿模型和研究源混为一组。

“不进入固定名单”只表示不持续抓取，不表示忽略这些机构的重大发布。

## 订阅通道实测

### 1. 可直接使用的 RSS/Atom

首期可接入 8 个目标 feed：

1. Google Research：<https://research.google/blog/rss/>
2. Google DeepMind：<https://deepmind.google/blog/rss.xml>
3. Microsoft Research：<https://www.microsoft.com/en-us/research/feed/>
4. Apple ML Research：<https://machinelearning.apple.com/rss.xml>
5. NVIDIA Technical Blog：<https://developer.nvidia.com/blog/feed/>
6. Hugging Face Blog：<https://huggingface.co/blog/feed.xml>
7. Amazon Science：<https://www.amazon.science/index.rss>
8. Sakana AI：<https://sakana.ai/feed.xml>

OpenAI 的 <https://openai.com/news/rss.xml> 可以用于发现主站更新，但近 30 天可见约 65 条，混有大量客户案例和产品新闻；不能替代 Developer Blog 的 sitemap 订阅。Microsoft Research feed 在复核通道返回标准 RSS，但本机直连会随边缘节点出现 403，不应把它当成唯一通道。

### 2. Sitemap 优先

- OpenAI Developer Blog：`sitemap-index.xml → sitemap-0.xml`，过滤 `/blog/`。
- Anthropic：`sitemap.xml`，过滤 `/engineering/` 与 `/research/`。
- DeepSeek：`sitemap.xml`，过滤 `/en/news/` 并比较 `lastmod`。
- ByteDance Seed：sitemap 能发现文章，但 XML 结构异常；HTML `blog_list` 应作为主通道。

Sitemap 的 `lastmod` 只能作为“页面发生变化”的信号，不能直接当成发布日期或更新频率。Anthropic 等站点会批量修改旧页时间。

### 3. HTML 列表与搜索兜底

Qwen、Kimi、MiniMax、Mistral、Tencent HY、Meta FAIR、Ai2 和 Z.ai 都需要这一层。统一做法是：

- 优先读取官方 Blog/Research 列表页；
- 只保存 canonical URL、标题、发布日期和首见时间；
- 列表页失效或被 WAF 拦截时，用 `site:官方域名 + 技术主题` 搜索；
- 不把搜索摘要当文章证据，命中后必须回读官方正文、论文、模型卡或仓库。

## 建议的最小雷达机制

[推测] 暂时不需要新建庞大的评分体系。后续自动化只需四步：

1. **发现**：8 个 RSS/Atom + 可靠 sitemap + 少量 HTML 列表。
2. **去重**：按 canonical URL 去重，记录首次发现和内容更新时间。
3. **三类分流**：
   - 技术深读：包含机制/架构、实验或失败模式、可复核产物中的至少两项；
   - 发布提醒：只有规格、价格和厂商 benchmark；
   - 丢弃：融资、客户案例、招聘、合作、地区扩张和纯营销。
4. **每周汇总**：只把少量技术深读候选交给学习任务；发布提醒留一段摘要，不自动生成长报告。

建议先手工或半自动运行两周，再决定是否写脚本。验收只看三个结果：是否稳定发现真正值得读的文章、误报是否可接受、有没有漏掉已知重大技术发布。没有必要为每篇文章建立复杂评分表。

## 局限

- 本报告判断的是“官方内容源能否成为长期雷达”，不评价厂商模型的绝对能力。
- 厂商文章中的 benchmark、成本和能力数字均属于厂商自报；除非报告另行引用独立评测，否则不能当成已复现事实。
- 部分动态站点、WAF 和边缘节点会让同一 URL 在不同通道返回 200 或 403；长期自动化必须在实际执行设备上复测并保留 fallback。
- RSS 的近 30 天数量按 2026-10-20 feed 中可见条目统计；截断 feed 只能提供下限。
- 这轮只覆盖厂商与实验室。个人研究者、顶级工程师博客、Newsletter、X/Bluesky 和专业媒体应另建一层，不能直接混入本名单。
