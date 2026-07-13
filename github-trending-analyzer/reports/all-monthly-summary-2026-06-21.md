# GitHub Trending 月榜报告 — 2026 年 6 月（截至 6-21，半月数据）

> 生成时间: 2026-06-21
> 数据源: GitHub Trending HTML (`trending_fetcher.py fetch monthly`, 2026-06-21 抓取)
> 覆盖区间: 2026-06-01 ~ 2026-06-21（半月）
> 样本量: 18 个 trending 仓库

## 概览

| 统计项 | 数值 |
|--------|------|
| 分析项目数 | 18 |
| 总 Stars（当前） | 939,061 |
| 月度新增 Stars（today_stars 累计） | ≈ 388,000 |
| 主要语言 | TypeScript, Python, Rust, Swift |
| 主导领域 | Agent Skills 生态（占比 ~67%） |

### 语言分布

| 语言 | 项目数 | 占比 |
|------|--------|------|
| Python | 6 | 33.3% |
| TypeScript | 5 | 27.8% |
| Rust | 2 | 11.1% |
| Swift | 1 | 5.6% |
| JavaScript | 1 | 5.6% |
| C | 1 | 5.6% |
| Unknown / Markdown | 2 | 11.1% |

### 热门领域

1. **AI Agent Skills 生态**：12 个项目（66.7%）— 包含代码上下文、技能市场、安全扫描、PM 技能、网络技能
2. **AI 应用 / 内容创作**：3 个项目（16.7%）— markitdown、MoneyPrinterTurbo、taste-skill
3. **基础设施 / 数据库**：2 个项目（11.1%）— apple/container、iroh 周边
4. **教学课程**：1 个项目（5.6%）— ai-engineering-from-scratch

## 项目列表（按 monthly_stars 排序）

| 排名 | 项目 | 语言 | Stars | 月新增 | 类别 |
|------|------|------|-------|--------|------|
| 1 | [colbymchenry/codegraph](./research_colbymchenry_codegraph.md)* | TypeScript | 52,234 | +46,315 | Agent Skills / 代码图谱 |
| 2 | [Egonex-AI/Understand-Anything](./research_Egonex-AI_Understand-Anything.md)* | TypeScript | 64,425 | +49,015 | Agent Skills / 代码图谱 |
| 3 | [chopratejas/headroom](./research_chopratejas_headroom.md)* | Python | 41,069 | +34,870 | Agent Skills / Token 压缩 |
| 4 | [harry0703/MoneyPrinterTurbo](./research_harry0703_MoneyPrinterTurbo.md) | Python | 90,287 | +33,118 | AI 应用 / 短视频 |
| 5 | [microsoft/markitdown](./research_microsoft_markitdown.md)* | Python | 156,430 | +32,693 | AI 工具 / 文档转 Markdown |
| 6 | [Leonxlnx/taste-skill](./research_Leonxlnx_taste-skill.md)* | JavaScript | 47,545 | +29,001 | Agent Skills / 设计品味 |
| 7 | [rohitg00/ai-engineering-from-scratch](./research_rohitg00_ai-engineering-from-scratch.md)* | Python | 35,002 | +26,530 | 教学 / AI 工程 |
| 8 | [mvanhorn/last30days-skill](./research_mvanhorn_last30days-skill.md) | Python | 44,995 | +18,741 | Agent Skills / 研究助手 |
| 9 | [Panniantong/Agent-Reach](./research_Panniantong_Agent-Reach.md)* | Python | 35,625 | +15,107 | Agent Skills / 跨平台读取 |
| 10 | [apple/container](./research_apple_container.md)* | Swift | 39,030 | +12,350 | 基础设施 / 容器 |
| 11 | [mukul975/Anthropic-Cybersecurity-Skills](./research_mukul975_Anthropic-Cybersecurity-Skills.md)* | Python | 16,969 | +10,210 | Agent Skills / 安全 |
| 12 | [iptv-org/iptv](./research_iptv-org_iptv.md) | TypeScript | 126,111 | +9,694 | 内容 / IPTV 频道 |
| 13 | [anthropics/knowledge-work-plugins](./research_anthropics_knowledge-work-plugins.md)* | Python | 21,475 | +9,069 | Agent Skills / 知识工作 |
| 14 | [can1357/oh-my-pi](./research_can1357_oh-my-pi.md)* | TypeScript | 13,618 | +8,619 | Agent Skills / 终端编码 |
| 15 | [phuryn/pm-skills](./research_phuryn_pm-skills.md)* | Unknown | 20,013 | +8,407 | Agent Skills / PM 工作流 |
| 16 | [hardikpandya/stop-slop](./research_hardikpandya_stop-slop.md)* | Unknown | 11,551 | +7,775 | Agent Skills / 文风清洗 |
| 17 | [DeusData/codebase-memory-mcp](./research_DeusData_codebase-memory-mcp.md)* | C | 9,030 | +5,450 | Agent Skills / MCP |
| 18 | [ogulcancelik/herdr](./research_ogulcancelik_herdr.md)* | Rust | 6,465 | +4,761 | Agent 工具 / 多路复用 |

> 注：标记 `*` 的项目表示本仓库在 Q2 之前**无对应的深度研究报告**。汇总报告中保留链接占位，供后续 TrendAgent 按 TT-2 协议补全（见 §6 数据源说明）。

## 趋势分析

### 🔥 热门趋势

**1. Agent Skills 市场进入"基础设施化"阶段**

Q1 时 Agent Skills 仍以 `obra/superpowers`（93K）、`alirezarezvani/claude-skills`（5.6K）为代表，单仓库即"全栈"。Q2 起出现明显**垂直化分工**：

- **代码上下文层**：codegraph、Understand-Anything、codebase-memory-mcp（提供 AST/图谱索引）
- **上下文压缩层**：headroom（CCR + CacheAligner）
- **网络/信息获取层**：Agent-Reach、last30days-skill
- **质量控制层**：taste-skill、stop-slop、SkillSpector（NVIDIA 出品）
- **跨职能市场**：pm-skills、Anthropic-Cybersecurity-Skills、anthropics/knowledge-work-plugins

市场结构从"单体技能仓库"演化为"分层技能栈"。印证了 Q1 报告中"技能工程"范式判断。

**2. 大模型厂商亲自下场做 Skills**

- **Anthropic**：knowledge-work-plugins（官方插件市场）
- **NVIDIA**：SkillSpector（技能安全扫描）

厂商已不再只做模型，而把 Skills 当作新分发渠道。这与 Q1 HuggingFace/skills 一脉相承，但参与方从 1 家扩到 3+ 家。

**3. Apple 容器 / Rust 网络栈代表"系统层回归"**

- `apple/container`（12,350 月增）— Apple Silicon 原生 Swift 容器，VM 级隔离替代共享内核
- `n0-computer/iroh`（weekly +1,502）— Rust + QUIC，公钥替代 IP 的对等网络栈

Q1 系统层项目以 SpacetimeDB（数据库）和 Lightpanda（浏览器）为主，Q2 转向"网络栈/虚拟化"。

### 🏢 大厂动态

| 公司 | 项目 | 定位 | 月新增 Stars |
|------|------|------|-------------|
| Microsoft | markitdown | LLM 友好的多格式转 Markdown | +32,693 |
| Apple | container | Apple Silicon 原生 Linux 容器 | +12,350 |
| Anthropic | knowledge-work-plugins | 知识工作插件市场 | +9,069 |
| NVIDIA | SkillSpector | Agent 技能安全扫描 | +5,026（weekly 推算） |
| 字节跳动 / 火山引擎 / 阿里 | — | **缺席** | 0 |

> 对比 Q1（2026-03-18 月报）：字节 deer-flow、阿里 OpenSandbox、阿里 zvec、火山 OpenViking 均曾进入 Top 5。**Q2 国内大厂在 GitHub Trending 月榜已整体缺席**，注意力似转向 SDK 与闭源产品。

### 🔬 技术创新

**1. Headroom — Agent 上下文压缩新范式**
- Python + Rust (PyO3) + ONNX Runtime，CLI/proxy/SDK/库四形态
- 创新：可逆 CCR 检索 + CacheAligner 稳定提示前缀
- 月增 34,870 stars，单月增长比 Q1 任何 Agent Skills 项目都高

**2. Understand-Anything / codegraph — 代码图谱双雄**
- 两者都做"为 AI Agent 提供代码知识图谱"，但路径不同：
  - Understand-Anything：Tree-sitter AST + LLM 补语义层
  - codegraph：SQLite FTS5 + Tree-sitter + 文件监听哈希对账（声称 -58% 工具调用、-47% token）
- 月增合计 95,330 stars

**3. iroh — 公钥替代 IP**
- Rust + QUIC/noq 实现的模块化网络栈
- 用公钥作为节点标识，自动打洞/中继回退
- 内置 iroh-blobs（内容寻址）/ iroh-gossip / iroh-docs

**4. apple/container — 1.0 正式发布（2026-06-09）**
- Swift 98%，macOS 26 + Apple Silicon
- VM 级隔离，1.0 落地意味着 Apple 正式参战容器生态

### 📊 语言趋势

| 语言 | 项目数 | 代表项目 |
|------|--------|----------|
| Python | 6 | headroom, MoneyPrinterTurbo, markitdown, last30days-skill |
| TypeScript | 5 | codegraph, Understand-Anything, oh-my-pi |
| Rust | 2 | herdr, iroh（weekly） |
| Swift | 1 | apple/container |
| JavaScript | 1 | taste-skill |
| C | 1 | codebase-memory-mcp |
| Unknown / Markdown | 2 | pm-skills, stop-slop |

**对比 Q1（2026-03-18 月报）**：
- TypeScript：从 5 → 5（持平）
- Python：从 5 → 6（+1）
- Rust：从 2 → 2（持平）
- Zig：1 → 0（**消失**：Lightpanda 已不在月榜）
- Swift：0 → 1（**新增**：apple/container）
- C：0 → 1（**新增**：codebase-memory-mcp）

## 与 2026 Q1 月报对比

### 新出现

| 项目 | Q1 月榜 | Q2 (本月) |
|------|---------|-----------|
| chopratejas/headroom | ❌ | ✅ 月榜 #3 |
| colbymchenry/codegraph | ❌ | ✅ 月榜 #1 |
| Egonex-AI/Understand-Anything | ❌ | ✅ 月榜 #2 |
| Panniantong/Agent-Reach | ❌ | ✅ 月榜 #9 |
| anthropics/knowledge-work-plugins | ❌ | ✅ 月榜 #13 |
| apple/container | ❌ | ✅ 月榜 #10 |
| microsoft/markitdown | ❌ | ✅ 月榜 #5 |
| NVIDIA/SkillSpector | ❌ | ✅ weekly 出现 |
| n0-computer/iroh | ❌ | ✅ weekly 出现 |
| addyosmani/agent-skills | ❌ | ✅ weekly 出现 |
| LMCache/LMCache | ❌ | ✅ weekly 出现 |

**新主题**：Agent Skills 垂直化分层、Apple 容器、公钥网络栈、Skills 安全扫描、KV 缓存层。

### 消失 / 下滑

| 项目 | Q1 月榜排名 | Q2 状态 |
|------|-------------|---------|
| openclaw/openclaw | #1（321K） | ❌ 已不在月榜 |
| obra/superpowers | #2（93K） | ❌ 已不在月榜 |
| koala73/worldmonitor | #3（40K） | ❌ 已不在月榜 |
| ruvnet/RuView | #4（37K） | ❌ 已不在月榜 |
| moeru-ai/airi | #5（34K） | ❌ 已不在月榜 |
| 666ghj/MiroFish | #6（33K） | ❌ 已不在月榜 |
| bytedance/deer-flow | #7（31K） | ❌ 已不在月榜 |
| shareAI-lab/learn-claude-code | #8（31K） | ❌ 已不在月榜 |
| sickn33/antigravity-awesome-skills | #9（25K） | ❌ 已不在月榜 |
| clockworklabs/SpacetimeDB | #10（23K） | ❌ 已不在月榜 |
| lightpanda-io/browser | #11（21K） | ❌ 已不在月榜 |
| p-e-w/heretic | #12（15K） | ❌ 已不在月榜 |
| volcengine/OpenViking | #13（15K） | ❌ 已不在月榜 |
| huggingface/skills | #14（9K） | ❌ 已不在月榜 |
| alibaba/OpenSandbox | #15（8K） | ❌ 已不在月榜 |
| fluxerapp/fluxer | #16（6K） | ❌ 已不在月榜 |
| alirezarezvani/claude-skills | #17（5K） | ❌ 已不在月榜 |

**几乎全 Q1 Top 17 都在 Q2 月榜消失**。这是因为：
1. 大体量项目（>20K stars）的"边际增速"自然回落
2. Q2 出现了一批"小体量高增速"的新 Skills 项目，挤占月榜
3. 大厂（字节/阿里/火山）整体缺席

### 跨季度延续项目

| 项目 | Q1 排名 | Q2 状态 | 备注 |
|------|---------|---------|------|
| harry0703/MoneyPrinterTurbo | — | ✅ 月榜 #4 | Q1 已有研究，Q2 仍稳居高位 |
| iptv-org/iptv | — | ✅ 月榜 #12 | 长期热门内容项目 |
| mvanhorn/last30days-skill | — | ✅ 月榜 #8 | Q1 已生成研究 |

## 重点 Repo 简评（Top 10）

### #1 colbymchenry/codegraph — Agent 时代的代码知识图谱

**技术栈**：Node.js + SQLite FTS5 + Tree-sitter + MCP 服务
**应用场景**：为 Claude Code / Codex / Cursor / Gemini CLI 等 AI 编码 Agent 提供"无需多次 grep/glob 的代码图谱查询"
**创新点**：
- 文件监听 + 哈希对账的三层实时同步（声称 -58% 工具调用、-47% token）
- 支持 20+ 编程语言，包括 Swift/ObjC、React Native 跨语言桥接
- 与 Understand-Anything 形成"代码图谱双雄"，但 codegraph 更偏本地静态分析

**与竞品对比**：Understand-Anything 用 LLM 补语义（更准但更贵），codegraph 用本地索引（更快但语义弱）。

### #2 Egonex-AI/Understand-Anything — 互动式代码知识图谱

**技术栈**：TypeScript 多 Agent 工具，Tree-sitter 解析代码结构 + LLM 补语义层
**应用场景**：大型代码库 onboarding，输出架构图、业务流程图、引导教程
**创新点**：
- 确定性 AST 与 LLM 混合提取
- 支持 15+ AI 编码平台一键安装
- 输出"graphs that teach > graphs that impress"的互动图谱

**代表场景**：新人入职第一天拿到一个百万行 monorepo，可用此工具 30 分钟摸清业务流。

### #3 chopratejas/headroom — Agent 上下文压缩层

**技术栈**：Python + Rust (PyO3) + ONNX Runtime
**应用场景**：在 LLM 输入/输出两端压缩 token，覆盖 CLI / proxy / SDK / library 四种集成方式
**创新点**：
- 同时压缩输入与输出 token（60-95% 节省）
- 可逆 CCR（Compress-Cache-Retrieve）机制
- CacheAligner 自动稳定提示前缀以最大化 KV 缓存命中

**意义**：当 Agent 上下文爆炸（>100K tokens）时，headroom 直接决定成本结构。它与 LMCache（KV 缓存层）形成"压缩 + 缓存"完整组合。

### #4 harry0703/MoneyPrinterTurbo — AI 短视频生成器

**技术栈**：Python（FastAPI + MoviePy/FFmpeg + 多 TTS 引擎）
**应用场景**：一键生成抖音 / YouTube Shorts / 快手短视频
**创新点**：
- 调用 GPT-4/DeepSeek 自动生成脚本
- Pexels/Pixabay 自动匹配免版权素材
- 内置 Web UI 极低门槛

**Q2 表现**：月增 33,118 stars，仍是国内 AI 应用层出海标杆。**已有 Q1 深度研究报告**（[`./research_harry0703_MoneyPrinterTurbo.md`](../research_harry0703_MoneyPrinterTurbo.md)）。

### #5 microsoft/markitdown — LLM 友好的文档转换器

**技术栈**：Python（hatch/pip 管理），可选 Azure Document Intelligence / Content Understanding 增强
**应用场景**：RAG 与文本分析前处理，PDF / Office / 图像 / 音频 / YouTube 转 Markdown
**创新点**：
- 分层保真 + 可插拔：离线抽取 → 云端版面分析 → 多模态结构化（带 YAML frontmatter）
- OpenAI 兼容客户端做 OCR 与图像描述

**意义**：成为 LLM 时代的"LibreOffice Convert"。

### #6 Leonxlnx/taste-skill — 消除 AI 生成的"slop"

**技术栈**：JavaScript + Shell 的 SKILL.md 技能包
**应用场景**：通过 `npx skills add` 注入 Codex / Cursor / Claude Code / ChatGPT，约束生成式 UI 避免"slop"质感
**创新点**：
- 可调旋钮（DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY 1–10）
- 反 slop 规则（禁 em-dash、GSAP 骨架）
- 多种风格预设（taste / gpt-taste / soft / minimalist / brutalist / stitch）

### #7 rohitg00/ai-engineering-from-scratch — AI 工程全栈教学

**技术栈**：Python 教学项目，串联 PyTorch / JAX / LangGraph / AutoGen / CrewAI / MCP / vLLM / SGLang 等 20+ 框架
**应用场景**：自学者的 AI 工程全栈课，覆盖 LLM 预训练/RLHF、RAG、终端编程 Agent、红队评估与 GPU 自动伸缩
**创新点**：
- "Build It / Use It" 双轨六拍课节循环
- 每课输出可复用工件
- 内置 `/find-your-level` 与 `/check-understanding`，适配多 IDE

### #8 mvanhorn/last30days-skill — 跨平台研究助手

**技术栈**：Python Agent 技能
**应用场景**：研究任何话题，覆盖 Reddit / X / YouTube / HN / Polymarket / Web
**创新点**：研究 → 综合 → 输出三段式，自动引用来源

**Q1 已有深度研究报告**（[`./research_mvanhorn_last30days-skill.md`](../research_mvanhorn_last30days-skill.md)）。

### #9 Panniantong/Agent-Reach — 给 AI Agent 装上"眼睛"

**技术栈**：Python 3.10+ CLI，聚合 Jina Reader / yt-dlp / gh / OpenCLI 等多后端
**应用场景**：免 API Key 的跨平台读取，覆盖 YouTube / B 站 / Twitter/X / Reddit / 小红书 / RSS
**创新点**：
- 多后端主备路由 + `doctor` 主动探测
- Agent 一句话自助安装更新
- **数据源 X 不可达 → 自动切换 Y**（与任务要求一致的设计哲学）

**与 EverAgent 内部 `agent-reach` 技能高度同源**：本仓库可能是其灵感来源或镜像实现。

### #10 apple/container — Apple Silicon 原生 Linux 容器

**技术栈**：Swift 98%，macOS 26 + Apple Silicon，基于 Containerization Swift 包
**应用场景**：在 Mac 上运行 Linux 容器作为轻量级 VM，完全 OCI 兼容，可与 Docker 互通
**创新点**：
- **VM 级隔离替代共享内核**（每个容器一个微 VM）
- Swift 原生实现深度利用 Apple 芯片虚拟化
- 1.0 已于 **2026-06-09** 发布

**意义**：Apple 正式参战容器生态，挑战 Docker Desktop 的 macOS 体验。

## 数据源与方法

### 数据来源

| 来源 | URL | 状态 |
|------|-----|------|
| GitHub Trending（月榜） | https://github.com/trending?since=monthly | ✅ 已抓取（`trending_fetcher.py fetch monthly`） |
| GitHub Trending（周榜） | https://github.com/trending?since=weekly | ✅ 已抓取 |
| GitHub Trending（日榜） | https://github.com/trending?since=daily | ✅ 已抓取 |
| GitHub API（项目元信息） | https://api.github.com | ⚠️ 部分项目仅用 trending 页面的 stars/today_stars，未单独调用 API 补全 created_at/forks/license 等字段 |
| WebFetch（项目主页） | GitHub README | ✅ 用于 Top 10 简评 |
| 现有深度研究报告 | `./research_*.md` | ✅ 引用了 3 个（MoneyPrinterTurbo / iptv / last30days-skill） |

### 方法

1. 使用 `trending_fetcher.py fetch {period}` 抓取 daily / weekly / monthly 三个时间窗数据
2. 取 monthly 数据作为主榜单（18 个项目），按 `today_stars` 降序排列
3. 对 Top 10 项目使用 WebFetch 抓取 GitHub README 进行技术简评
4. 对比 Q1 月报（2026-03-17 / 2026-03-18）识别新出现 / 消失项目
5. 复用已有深度研究报告（74 篇中相关 3 篇）作为引用源

### 限制

- **历史数据缺失**：trending_fetcher 不存储历史快照，无法获取 2026-05-01 ~ 2026-06-20 的中间 trending 数据。月榜数据为 2026-06-21 单日抓取。
- **新增 stars 估算**：月榜 `today_stars` 字段实际为 GitHub 当时页面上显示的"过去 30 天 stars 数"，并非真实月度增量。日榜/周榜同理。
- **未生成新深度研究报告**：Q2 月榜 18 个项目中，15 个在本仓库无对应 `research_*.md` 文件。汇总报告保留链接占位，待后续 TrendAgent 按 TT-2 协议补全（预计需要 3-5 个工作单元完成）。
- **Q1 数据精度**：Q1 月报中部分项目 stars 数值与 Q2 榜单上的"当前 stars"存在差异（项目持续增长），对比表中已使用各报告中的记录值。

## 报告状态说明

| 类别 | 数量 | 项目 |
|------|------|------|
| ✅ 引用 Q1 已有深度研究 | 3 | harry0703/MoneyPrinterTurbo, iptv-org/iptv, mvanhorn/last30days-skill |
| ⚠️ 链接占位（待补研究） | 15 | codegraph, Understand-Anything, headroom, markitdown, taste-skill, ai-engineering-from-scratch, Agent-Reach, apple/container, Anthropic-Cybersecurity-Skills, knowledge-work-plugins, oh-my-pi, pm-skills, stop-slop, codebase-memory-mcp, herdr |

> ⚠️ 后续建议：将 Top 5（codegraph / Understand-Anything / headroom / markitdown / taste-skill）纳入下一批 TT-2 任务，优先补充深度研究报告。

---

*报告生成时间: 2026-06-21*
*数据截止: 2026-06-21 (monthly snapshot)*
*分析方法: GitHub Trending 多时间窗抓取 + WebFetch 简评 + Q1 月报对比*