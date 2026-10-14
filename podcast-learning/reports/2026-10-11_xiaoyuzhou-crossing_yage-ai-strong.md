---
title: "十字路口：鸭哥——Context Infrastructure 三要素、0人公司与睡眠回归实验"
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/6aca7f91e742e36efcc10957
show: "十字路口Crossing"
episode: "“有了AI，我感觉自己强得可怕！”｜对谈鸭哥（2026-10-11，公路播客）"
host: "Cody"
guest: "鸭哥（Superlinear Academy 联合创始人；哥大 PhD；微软/Pinterest/Samsara）"
duration: "1h12m"
duration_seconds: 4350
transcript_segments: 2447
chapters: 4（shownotes Part1-4）
polished: true
polished_by: "Claude (pi)（结构化精编，约 raw 的 12.4%（按汉字数 2462/19854），头部已标注）"
polished_at: 2026-10-12
status: archived
created: 2026-10-12
updated_on: 2026-10-12
transcript_path: reports/transcripts/2026-10-11_xiaoyuzhou-crossing_yage-ai-strong.transcript.txt
polished_transcript_path: reports/transcripts/2026-10-11_xiaoyuzhou-crossing_yage-ai-strong.polished.txt
pipeline: eacli podcast（Razer whisper large-v3/CUDA/VAD）→ pull 成功（122KB）→ web.read（智谱）shownotes → 精编（SKILL v2）
source_shownotes_chapters: true
notable_correction: "JV/GEV/GVT→Jev｜Flood Code→Claude Code｜签问3.5→千问 3.5｜止读→top-k[?]｜Fable 5→[?]｜压根/压哥→鸭哥｜蒸留/真留→蒸馏｜侥幸的话→时髦的话[?]；老鸭汤/可达鸭/永哥说餐饮 为口播原名"
hanzi_chars_raw: 19854
total_chars_raw: 82167
hanzi_chars_polished: 2466
total_chars_polished: 5331
---

# 十字路口：鸭哥——Context Infrastructure 三要素

## ⚡ 速览

- Jev=GPT+JSON mode，火的三条件：**基模到（千问 4B 碾压 GPT-4o）×需求到（agentic 成本敏感）×包装到（System 1 叙事）**。
- Context Infrastructure 三要素：搜集整理→让 AI 消费→**闭环复利**；"一切都是文件"，反对 memgpt 式抽象。
- 0 人公司半年 5700 粉：AI 写全部内容+自己运营+UTM 归因自我迭代——"老鸭汤要熬的，直接拿去是老鸭汤不是你的汤"。

## 概览

- **Jev 深拆**：本质是 classification（校准概率+置信度分开）；十年死过四五波（各家 Classification API），现在三条件同时成熟；两个真实应用（browser use 提速 10 倍但缺 ablation；harness 危险分类——开源 harness 缺的补上）；开源复现千问+logits 85% vs 官方 88%；**便宜模型革命**：导游项目 400 亿 token，Sonnet $12,000 vs DeepSeek flash $300。
- **云端电脑线**：Manus(4月)→Grok Bot(8月)→Muse(9月)——持久化 VM 不销毁→AI 能做代码外的生活任务；GPT-6 Astra 几句话做全套 VTuber 皮（建模/绑骨/动捕）="基模干倒一个工业"。
- **娃受伤三段故事**：AI 判断牵拉肘+推荐 urgent care→保险理赔全接管（人只打电话踢一脚）→SOP 沉淀两份文档（给人的+给 AI 的）帮别的家长。"强得可怕=雇了医生+律师+文秘天团 24×7 可无限复制——**前提是会用，很多人给他两个秘书都不会用**。"
- **Gap 原因**：AI 干完体力活剩下全是脑力活强度反升（"以前想 AI 开会我写码；现在 AI 写完码我去开会"）；用 AI 是管理学问题→与课代表全职做 Superlinear Academy。
- **Context Infrastructure**：装眼睛失败（没用途）、录音继续；Intake Skill+Yahoo 式目录+Semantic Search（都开源）；**微信聊天记录+Codex=如虎添翼**（100 人名单查交集）；"Manus Context Engineering 文章值 100 万美元"。
- **0 人公司**：pre-training 学共识（无 alpha）+alignment 偏中庸→off-the-shelf AI=正确的废话→注入横/纵向调研的思维 context→"不像 AI 写的"；AI 自己提议上 X/typefully/UTM 归因→自我闭环；**蒸馏实验**（永哥说餐饮 100 视频→20 条经验，"把你老板蒸馏出来"）；商业化"又赚钱又不赚钱"（教学例子有收入但非自己跑通商业闭环）——"AI 还做不到你说赚钱就赚钱。"
- **奖励什么人**：有 domain expertise + 会**管理**（非使用）AI 的人；人讲内化 AI 讲**外化**（全变文件和 prompt）；不用画饼不用顾自尊心；**"对人类乐观对用 AI 悲观——清晰表达我想要什么极稀缺，直接决定 AI 用得好不好。"**
- **生活实验**：睡眠多变量回归（AI 写 iOS app 同步 HealthKit/CGM/体重→咖啡无关（**证伪省一周**）/酒精正相关/**最强因子=最后用 AI 的时间**→戒晚间 AI→月均睡眠+1h）；三折叠上 AI 写 OpenCloud 移动端（"100% 用 APP 不用电脑"）。
- **赛博许愿**：context infrastructure 进组织——亚马逊 leadership principle 洗脑难，AI 执行=**改 prompt 就贯彻**；与课代表已 agent 对 agent 协作（草案→email→互审→吵几轮→人高层指导→定稿）。

## 增量观点（polished 之外的连接与分析）

1. **"一切都是文件"在本库第四次收敛，且这次给出了反对面**：[[2026-10-05_rss-kedaibiao-lizheng_codex-claude|孙煜征 Document first]]（可移植文档）、[[2026-10-10_bilibili-shaoailun_sunyuchen-ai-era|孙宇晨]]（全数据 MD 化"换 Codex 直接读"）、[[2026-09-23_xiaoyuzhou-weishijie_ruanliang-ai-org|阮良]]（HTML>PPT 因 AI 读得好），鸭哥加上**反对清单**（不要 memgpt memory layer、不要为 MCP 而 MCP）——四期把"文件作为人机接口"的正反面说全了。这与 EverAgent 的 Markdown 两仓结构完全同构。
2. **Jev 三条件是 [[2026-09-24_rss-kedaibiao-lizheng_ai-hype-jev|课代表 215 炒作拆解]]的工程互补版**：215 讲传播机制（如何炒作一个 AI 概念），鸭哥讲技术本质+成熟条件（基模/需求/包装三重奏）——同一事件的两面拼图。而"开源 85% vs 官方 88%"恰好是 [[2026-10-08_rss-guigu101_e255-zhangkuo|E255]] 107-task 的微缩：官方数字与开源复现的差距才是真实水位。
3. **睡眠回归实验是本库方法论的最佳个人实践样本**：多变量回归找最强预测因子→证伪咖啡（省一周实验）→发现"最后用 AI 时间"——**把 E255 的评测思维用在自己身上**；"AI 写 iOS app 绕 HealthKit 限制"与孙宇晨"hack 私有 API 下照片"同款（成为器材的主人）。其结论（晚间高强度 AI 对话→睡眠-1h）直接命中 [[sleep-cybernetics|biology 睡眠线]]，值得回填概念页。
4. **"管理而非使用 AI"+"对用 AI 悲观"接上判断力线并给出新变量**：[[2026-10-08_xiaoyuzhou-daxiaoma-keji_v95-china-us|AK]]的"判断力保值"、阮良的"一把手管理论"之后，鸭哥贡献了最锋利的一条：**瓶颈不在 AI 能力，在"人能否讲清楚自己想要什么"的稀缺性**——这与于红 SEL 的"表达训练"、216 的"跟 AI 直接说话就好"构成同一缺口的证据链。
5. **yage.ai 是 lizheng.ai 的镜像实验**：[[2026-10-05_rss-kedaibiao-lizheng_codex-claude|216 期]]孙煜征手动叙事主权，鸭哥把整个叙事外包给带 context 的 AI（还开源了蒸馏 skill）——**个人 IP 的"手作"与"全自动"两个极点在一周内齐了**；而"AI 提议上 X/自建 UTM"正是 [[2026-09-24_xiaoyuzhou-luanfanshu_today-personal-ai|Today 277]] Proactive 四维度（理解/反馈/频次/时效）的已实现案例。
6. **"leadership principle=一个 prompt"是组织线的最激进推论**：陈彬/阮良/曾鸣都在讲"组织改造难"，鸭哥给出终局解法——**当执行者换成 AI，组织文化从'洗脑工程'降维成'写 markdown'**；agent 对 agent 协作（他与课代表）是这个未来的活体样本，与大小马 V95"投资人用 Muse 卖 Airbnb 股票"互为印证。

## 关键人物

- **鸭哥**：Superlinear Academy 联合创始人（与课代表孙煜征）；哥大 PhD；微软/Pinterest/Samsara；现 Gap 中；yage.ai 主理人。
- Cody：十字路口主播（公路播客乌镇→上海）。
- 课代表/孙煜征：合作伙伴（agent 对 agent 协作对象）。
- "永哥说餐饮"：抖音博主（蒸馏实验素材）。

## 引用书目

Manus《Context Engineering》文章（鸭哥评"值 100 万美元"）；卡尼曼 System 1/2（Jev 包装的理论来源）；DeepSeek 研究员《我不得不把才华埋葬在昨天》（引用感伤）；Artificial Intelligence Index（千问 4B vs GPT-4o 分数出处）。

## 关键概念词

Jev 三条件（基模/需求/包装）｜校准概率与置信度分离｜cascaded classification｜harness classifier｜持久化云端电脑（Manus→Grok Bot→Muse）｜Context Infrastructure 三要素（搜集/消费/闭环）｜一切都是文件（反 memgpt/MCP 滥用）｜Intake Skill / Semantic Search｜微信记录外挂｜pre-training 学共识（无 alpha）/alignment 中庸｜横/纵向调研注入｜0 人公司自我闭环（UTM 归因）｜蒸馏（永哥/老板）｜老鸭汤理论（要熬要养）｜管理 AI ≠ 使用 AI｜内化 vs 外化｜"讲清楚我想要什么"的稀缺性｜多变量回归找睡眠因子｜证伪省时｜器材的主人｜leadership principle=一个 prompt｜agent 对 agent 协作

## 关键观点（原话）

> "Jev 就是 GPT 加上 JSON mode……它大火的三个原因：基模到了、需求有了、包装真的特别厉害。"

> "有了 AI，我感觉自己强得可怕——等于雇了医生、律师助理、文秘天团，24×7 还可以无限复制。前提是你会用：很多人给他两个秘书都不会用。"

> "以前我想 AI 帮我开会、我来写代码；现在 AI 把代码都写完了，我要去开会——所以很累。"

> "一切都是文件……我比较反对单纯为了用 MCP 而用 MCP，或者为了用 memory 而 memory。"

> "老鸭汤是要熬的——你拿过去它还是我的汤，不是你的汤；你要去熬汤、去养虾。"

> "经理的最高境界是他不在场的时候 team 还能正常运转——用 AI 也要这样。"

> "我对人类是乐观的，对用 AI 是悲观的——用好 AI 的前提是你至少能清晰表达我要干什么，想一想有多少人能讲清楚自己想要什么？很少。"

> "贯彻亚马逊 leadership principle，如果是人来执行要天天开会洗脑；如果 AI 来执行——就是加一个 prompt 的问题。"

## 关键数字

| 数字 | 含义 |
|---|---|
| $12,000 → $300 | 导游项目 400 亿 token：Sonnet vs DeepSeek flash 成本 |
| 85% vs 88% | 开源千问复现 Jev vs 官方 benchmark（无微调） |
| 1600 / 5700 | 0 人公司半年成绩：newsletter 订阅 / X 粉丝（0 篇人写） |
| 100 个视频 → 20 条 | 永哥说餐饮蒸馏实验 |
| +1 小时/月 | 戒晚间 AI 后平均睡眠提升 |
| 一周 | 多变量回归证伪"咖啡影响睡眠"省下的实验时间 |
| 几千张 | 幼儿园照片（AI 逆向私有 API 一晚下完） |
| 4B / 20+分 vs 8分 | 千问 3.5 4B vs GPT-4o（AI Index 口径） |
| 1000 人 | 1Password 团队规模（口播"我听说"，传闻口径） |
| 2026.4 / 8 / 9 月 | Manus / Grok Bot / Muse 云端电脑时间线 |

## Limitations

- polished 为精编版（约 raw 12%）；公路播客环境音与闲聊段有删节。
- 转写专名 [?]：Fable 5（设计模型）、top-k 止读、千问分数口径（AI Index 引用未经核）等；Jev/Grok Bot/Muse/Instinct 等产品名为 2026 口播名，与 [[2026-09-24_xiaoyuzhou-luanfanshu_today-personal-ai|277 期]] 一致保留。
- 嘉宾为 Superlinear Academy 联合创始人（AI 教育商业），"0 人公司"为其教学案例——有推广动机；全部运营数据为自述无第三方核验。
- 睡眠回归为个人 n=1 实验（未控制混杂、样本量小），结论按口播归档不构成健康建议；"戒晚间 AI→+1h"的因果性未验证。

## 思考与追问

1. **我真正理解了什么？**这期是"个人 AI 方法论"的集大成：Context Infrastructure 三要素把此前散落的各家说法（Document first/Memory×Proactive/先验 rubrics）统一进一个可实施的框架——**搜集（intake）→消费（文件+索引）→闭环（输出变新 context）**。而"管理而非使用"+"讲清楚想要什么的稀缺性"把瓶颈从 AI 侧彻底移回人侧，与本周所有报告的收敛方向一致。
2. **我还没搞懂什么？①Jev 官方 benchmark 的构成（88% 是什么任务集）；②千问 3.5 4B 的实际分数与口径（AI Index 2026 报告）；③"微信聊天记录备份插件"具体是哪个（复现价值极高）；④0 人公司的文章链接与实际读感（yage.ai）。
3. **下一步读什么/做什么？①把"Intake Skill/Semantic Search/蒸馏 skill"三个开源仓库找来对照 EverAgent 的 intake 流程（本仓的 AGENTS.md/skill 结构已是同类物，可互补）；②"戒晚间 AI"实验可在本仓 owner 侧复刻（Apple Watch 数据+回归，接 [[sleep-cybernetics|睡眠概念页]]）；③回填 [[attention-residuals|注意力残余]] 类概念页：最后用 AI 的时间→睡眠质量，是"注意力保护线"的硬数据版；④读 Manus Context Engineering 原文（鸭哥评值 100 万美元）。
