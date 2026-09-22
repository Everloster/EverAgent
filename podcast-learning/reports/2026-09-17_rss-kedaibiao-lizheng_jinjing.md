---
title: "一个人指挥 400 个 AI：Orca 津晶的多 agent 编排实操（ADE vs Harness）"
domain: "podcast-learning"
report_type: episode_summary
source: 播客（transistor.fm RSS）
source_url: https://share.transistor.fm/s/da94edb8
show: "课代表立正"
episode: "对话 319｜硅谷AI高手们，正在操作几百个AI同时上班（Orca 创始人津晶）"
host: "孙煜征"
guest: "津晶（Orca/Stably 联创，ex-Google，YC）"
duration: "1h06m54s"
duration_seconds: 4014
transcript_segments: 2759
hanzi_chars_raw: 19746
hanzi_chars_polished: 16789
speech_rate_cjk: "295 字/min"
chapters: 14
polished: true
polished_by: "Kimi (k3) 润色"
polished_at: 2026-09-22
status: archived
created: 2026-09-22
updated_on: 2026-09-22
transcript_path: reports/transcripts/2026-09-17_rss-kedaibiao-lizheng_jinjing.transcript.txt
polished_transcript_path: reports/transcripts/2026-09-17_rss-kedaibiao-lizheng_jinjing.polished.txt
pipeline: transistor 直链 mp3 → whisper.cpp / ggml-large-v3 / Metal / **VAD+`-mc 0`**（首轮 VAD-only 在 00:13:01 起灾难性循环幻觉，89.5% 无效，重转修复）→ 14 章重组
source_shownotes_chapters: true
notable_correction: "系统性误识别 85 条（Clock Code→Claude Code、Walker/Volca→Orca、虎精→虎鲸、The Man Test→The Mom Test 等）；首轮转写循环幻觉事故与修复记入 AGENTS.md 已知局限"
---

# 一个人指挥 400 个 AI：Orca 津晶的多 agent 编排实操

> 津晶（Orca 联创，GitHub stablyai/orca，录制时 4.9 万星）本人同时推进 400+ feature、其中 200+ 已跑成自动化 SOP。这期是**多 agent 编排的一线实操报告**——和你自己的 herdr/eacli 舰队互为镜像，值得对照读。

## 一、概览

- **ADE vs Harness**：Harness=把 input→output 的 agent 做成 loop（Codex/Claude Code/Devin）；**ADE（Agent IDE）在 harness 之上**——不绑模型、不做 loop，专注"人与 agent 的管理 workflow"。Orca=70% UI+30% CLI，"orchestration for agents"。
- **400 任务不逐个盯的三层**：①索引搜索聚合；②**让 agent 管 agent**（用户写 orchestration script，典型配方="Claude Code 驾驭着 Codex"，人只看第一步和最后一步）；③SOP 化+定时 manager thread（release agent 每小时自检、需要时主动发消息问她）。
- **护城河观**：坦承与 Claude Desktop/Codex 功能重合、"不是 defensible 的长久 position"；护城河=迭代速度（**4 人团队每天一个 stable 版、每版上百 PR**）+ 同理心（大厂不懂 subscription 用户的痛）+ 借力策略（"Claude Code 有的我们都有，但我们有它们没有的"）。
- **企业侧炸点**："**Anthropic 的账单已成企业第一大开销、超过工程师工资单**"——所以 enterprise 盯 Codex 与 open weight 模型；vendor 中立被低估。
- **创业判断**：DevTool 正在 collapse 成"用 AI 生成"；增长靠借力（不改变用户习惯+跟大厂发布走）+ 造词（他们造了 ADE）；用户访谈学 Michael Seibel：了解到"客户去年收入、最大开销"，目标成为客户第一/第二大开销。

## 二、章节地图（14 章）

开场（一人几百任务）→ Orca 解决什么 → **ADE vs Harness** → 注意力分配 → 为什么不怕被做掉 → 工具的细节（PTY snapshot/升级不丢现场）→ 400 任务三层法 → 月成本（五家订阅，各家 1-2 个 200 美元档；plugin≠skill）→ Google→YC 履历 → 95% 时间做产品的增长法 → 访谈 100 用户方法论 → 反馈只听信息、决策归 4 人 → 为什么不焦虑（饼很大/虎鲸之喻）→ 看好的三类机会（回 2C / 硬件+软件 / compute）。

## 三、关键人物

- **津晶**：Orca（stablyai）联创；ex-Google；YC（首个项目婚礼直播平台进 YC，后做 AI 测试 Stably，再转 Orca）。
- 提及：Michael Seibel（YC group partner，用户理解标准的提出者）、黄仁勋（five-layer cake）、Cloudflare 某工程师（nested worktree 管 20 个 PR review 的用户案例）。

## 四、主要话题

### 1. ADE 是什么

集成性（Linear/GitHub issue→并行 thread→review/测试全链路回写）+ 规模化并行（10-20 feature × 每 feature 4-5 agent）+ 无自有 harness（1 分钟上手）。TUI 优先的商业逻辑：CLI 用户远多于 desktop 用户，且不用每次 Claude Code 更新就重新 wrap。agent 间 context handoff 是 Orca 早有、Codex"这周才出"的功能。

### 2. 工具即细节（prototype→production 的鸿沟）

灵感来自 Ghostty/iTerm 切屏三缺陷：非 worktree centric、tab 标题≠真状态、**一升级 50 个 session 全丢没人敢 update**。Orca 解法：PTY snapshot 进 local database、升级后 restore、跑着的 dev server 不 kill。金句："prototype 到一个真正的 production 中间有一个鸿沟；能力不够是看不见这个鸿沟的，AI 可以帮你更快地带到鸿沟边上。"

### 3. 400 任务的无人盯守机制

三层：搜索聚合（非 agentic 索引）；**agent 管 agent**（orchestration script 跑 Linear ticket→需求→设计文档→多轮 review→实现→QA→PR+HTML 报告；"人就看第一步和最后一步交出来的东西是否合理"）；SOP+定时（manager thread 定时跑；日更靠 release agent 每小时自检；社区 triage 自动化；跑在团队共享 remote host）。关键原则："**你让我参与的时候，你得给我那种容易 review 的东西。**"

### 4. 成本与订阅经济学

纯 API"每月好几万"；第一方 subscription 补贴狠（Claude/OpenAI 按 API 算 90% profit margin），她的配置=五家（Claude/OpenCode/Codex/Grok/Antigravity）各 1-2 个 200 美元档。plugin≠skill：plugin 偏 UI，skill 偏 AI 能力——"人和 AI 都需要工具上的提升"。

### 5. 用户访谈方法论（The Mom Test 实操）

每个点子打电话深谈 100 人：不问"你愿不愿意付费"，问"你为什么找这个方案、考虑过别的吗、在类似产品上花了多少钱"。Michael Seibel 的标准：了解到"客户去年收入、增幅、最大开销"，**目标是成为客户第一/第二大开销**。情报：很多公司第一大开销已从 Datadog（不是 AWS）变成 AI。

### 6. 三类看好的机会

①**回 2C**（B2B 采购更慢、2C ROI 变好；做把饼做大的，不抢 TikTok 时间）；②**硬件+软件**（国内供应链优势，例 Plaud）；③**compute**（芯片/存储/算力集成是 YC 新热点；黄仁勋 five-layer cake 里"算力与模型之间的优化层"）。

## 五、与 EverAgent/herdr/eacli 舰队的对照（编辑注）

**她有而本库没有的**：跨 harness 的 agent status 聚合面板（working/blocked/需 review）；**带工作现场的 handoff**（eacli 的 fallback 是重选 provider 重发请求，不是带 context 接力）；定时 manager thread + 主动向人升级（比 cron 注入 prompt 多了闭环）；升级不丢现场（PTY snapshot）；"要人参与就给容易 review 的东西"（agent 主动产 HTML 可视化）。
**本库有而她没提的**：能力面路由的证据与审计纪律（凭据不出设备）；知识沉淀链路（reports→wiki→open-questions）。
**理念重叠**：vendor agnostic；skill 放公共目录不锁厂商。

## 六、关键概念词

ADE、harness（loop+tool use）、agent status 聚合、handoff、nested worktree、PTY snapshot/restore、orchestration、SOP/manager thread、release agent、plugin vs skill、vendor agnostic、leverage marketing、The Mom Test、product sense、five-layer cake、零和 vs 做饼。

## 七、关键观点（原话引用）

> "Claude Code 有的我们都有，Codex 有的我们都有，但我们有它们没有的。"

> "Anthropic 的 bill 已经成为他们的第一大开销，已经超过他们工程师的花销。"

> "我 400 多个里面，可能 200 多个已经是自动化在跑。"

> "所有的反馈我们都只把它作为一个信息，最后的决定权还是在我们 team 这四个人。"

> "即使大家说现在 AI 写一个就可以了，但要做成一个好的产品，还是需要非常大的时间和 token 消耗的打磨——好的 taste 还是可以给你一个很大的领先机会。"

> "工业革命之后把人尽量地打造成一个标准件，而标准件的东西是最容易被取代的。"（孙煜征）

## 八、Limitations

- **首轮转写事故**：VAD-only 转写自 00:13:01 起陷入循环幻觉（"我们的 sense 是非常准确的"重复 3225 段，占 89.5%）；VAD 单独不够（触发点在语音中段），加 `-mc 0`（切断上下文自反馈）后修复。本报告全部内容基于修复版；修复版前 13 分钟与旧版逐行比对一致。
- 修正 85 条（polished 文末全表）；[?] 49 处（小众工具名 Py/OpenCore/UltraCode 等），不影响核心论点与数字。
- "月好几万"未明币种；"GitHub 49,000 星"为录制时点（任务书称 7 万，随时间增长）。
- 两段口播广告与片尾预告剪辑已从 polished 删除（raw 保留）。

## 九、思考与追问

1. **handoff 能不能进 eacli？** 她的 handoff 是"Claude Code 用量到顶→一键带 context 转 Codex 继续"；eacli 的 fallback 是请求级重选。两者之间缺的是"会话现场的可迁移性"（worktree+对话历史+todo 状态的序列化格式）。这个格式如果存在，应该长什么样？谁拥有它（harness 厂商没有动力做）？
2. **"人只看第一步和最后一步"的信任建立路径**：她能给 agent 这种自由度，是因为有可自动验收的 artifact（PR+测试+HTML 报告）。你的学习/研究 agent 的"最后一步"是什么——报告的 lint_evidence 通过？你本人读后的反馈率？研究类产出的"容易 review 的东西"该长什么样？
3. **4 人 × 400 任务 vs 1 人 × N 任务**：Orca 的三层（索引聚合/agent 管 agent/SOP 化）里，哪一层对你的单人多项目（10 个子项目+多设备舰队）杠杆最大？定时 manager thread + 主动升级这条，和"AI 新闻早报"失败案例（EverClaw 时代连续失败 14 次被禁用）差在哪？

---

*版权与引用：节目版权归课代表立正（孙煜征）与嘉宾所有；转录与润色稿仅供个人学习；如版权方要求下架请联系。完整节目请去小宇宙/各播客平台收听。*
