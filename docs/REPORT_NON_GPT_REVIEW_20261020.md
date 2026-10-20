# 最近三个月非 GPT 报告质量 Review

> 审计日期：2026-10-20
> 窗口：2026-07-20 至 2026-10-20，以报告首次加入 Git 的日期为准。
> 完整逐篇账本：[REPORT_NON_GPT_REVIEW_20261020.json](./REPORT_NON_GPT_REVIEW_20261020.json)

## 结论

最近三个月共新增 **146 篇**正式报告。依据 `report-v2` evidence 的生成模型或首次新增 commit 的 committer 身份，排除明确由 GPT/OpenAI 生成的 8 篇后，本次复核 **138 篇**。

> **范围订正**：初版审计只扫描当前工作树 `bf3642c`，没有先核对 `origin/main`。远端当时已多出 3 个 commit，其中包含大小马 V94 播客报告和 2026-10-19 AI 日报。两篇现已补入账本；以后全量审计必须记录目标 Git ref，并在当前分支不包含远端目标时停止宣称“全量完成”。

| 判定 | 数量 | 含义 |
|---|---:|---|
| 保留 | 66 | 核心证据与论证成立，无内容级返工必要 |
| 保留历史快照 | 38 | AI 日报等时效产物，保持当日语境，只补结构元数据 |
| 局部修复 | 28 | 主线可保留，补来源、收紧措辞或修正局部事实 |
| 重写 | 6 | 核心来源不可用、主张与证据错位，或报告对原材料的核心内容召回严重不足 |

总体判断：**质量差异主要由证据类型和任务风险决定，未形成“某个非 GPT 模型普遍不能用”的结论。** Podcast 的转写、Limitations 和归因纪律整体较好；真正的硬失败集中在医学建议、破损转写、无音频降级和把二手材料包装成一手逆向。

## 修订进度（2026-10-20）

- **6/6 篇重写完成正文处理**：前五篇重建核心来源链；大小马 V94 恢复十个 shownotes 章节的核心论证、案例与分歧。
- **28/28 篇局部修复完成正文处理**：来源定位、措辞边界、元数据、转写工件与公开 commit 已按清单补齐。
- **大小马 V94 已完成 revision 4 升级复核**：Kimi K3 先建立 17 个独立来源单元，再核对十章覆盖与 C01–C15，最终 93.5 分通过并归档。
- **Bruce 与 PuRo-2B 已完成独立复核**：Bruce 在领域审计补齐元数据后以 revision 3、94.6 分通过；PuRo-2B 以 revision 2、95.65 分通过；三篇失效旧 hash 均未复用。
- 其余 **104 篇**保持“保留/历史快照”，没有为追求结构一致性重写正文。
- 审计脚本同步修正一处误报：模板占位符检查现在忽略 fenced/inline code，`num_output_placeholders` 等真实代码标识不再被当成未完成模板。

逐篇状态写入同名 JSON 的 `remediation_status`；顶层 `remediation` 汇总可供后续自动检查。

## 本次漏检复盘

1. **范围判断失误**：我把当前脏工作树当成仓库最新快照，没有先比较 `HEAD` 与 `origin/main`。大小马 V94 根本不在本地 136 篇中，却仍使用了“全量”措辞。
2. **审核目标偏差**：我重点找伪造、错数字、坏转写和私有路径，默认“来源可靠 + 边界诚实”就足以保留，没有从用户消费面检查学习价值。
3. **Evidence 的选择偏差**：旧 evidence 只登记报告已经写入的 10 条 claim；整段被省略的内容没有 claim id，自然不会成为 unsupported claim。
4. **Reviewer 的共同盲区**：Generator 与 Reviewer 都是 GLM-5.3 / Claude Code。新 context 消除了对话污染，没有消除同模型对“短、克制、少复述”的共同偏好。
5. **把静态通过当成质量通过**：93.05 分证明已写内容大体可靠，却没有证明报告覆盖节目。用户早已明确“跑脚本检查是自嗨，要看学习反馈”，我没有把这条反馈落实到播客门禁。
6. **确定性检查没有真的执行**：旧 Reviewer 声称检查了转写完整性，但第 1004–1005 行存在时间戳倒退；本次运行 `audit_transcript.py` 才发现。机器可判定的问题不应靠头尾抽查代替。
7. **第一版修复仍停在 Prompt**：我最初只要求 Reviewer “先画内容地图”，review 工件却只保存 `coverage_unit_ids_checked`。这仍允许弱模型机械填满 ID。二次自审后增加 `source_content_map`，要求保存 Reviewer 独立识别的内容单元、来源、重要性、覆盖判断和映射；有 shownotes 时按章节数做最低校验。
8. **我第一次重写仍然漏了核心内容**：初版重写先漏掉第十章“航天突破的意义”，二次人工回读补上；revision 3 的独立地图又发现第 10:16 章“大卫的价值观史观”仍未完整进入正文，并以 `REV033` 阻断。说明生成者自己填写 `source_coverage` 仍会受同一套内容选择影响，必须保留来源独立 Reviewer。
9. **恢复报告时漏恢复了 wiki 增量**：我从远端 commit 只恢复了报告与证据工件，遗漏 `sun-yuchen` 实体页和 `work-ethic` 的 V94 对照段。Kimi K3 终审对 R04 做实地核验后发现；现已按原 commit 精确补回。

对应修复已经落到 Git 快照预检、`report_depth`、`reader_contract`、`source_coverage`、Reviewer `source_content_map`、shownotes 逐章最低覆盖、来源优先复核和播客结构审计中。以后报告审核先回答“用户只读报告能学到什么”，再回答“机器门禁是否通过”。

## 范围与方法

1. 使用 `scripts/report_catalog.py` 的九类正式报告边界，排除 transcript、shownotes 和 wiki。
2. 用 Git 首次新增 commit 与 `evidence.json` 识别生成模型；模型不明确时保守纳入，只有明确 GPT/OpenAI 身份才排除。
3. 逐篇检查标题、摘要、核心结论、来源、数字、推断标签、Limitations 和结尾；运行全库静态审计与 Podcast 领域审计。
4. 对高风险报告阅读全文并回查本地 transcript、polished、quality sidecar 或公开来源。
5. 额外抽查 8 条 AI 日报高风险头条，均能找到对应公开证据；核验脑科学报告的 5 条传播性主张，其中 11.5 小时空腹研究未定位，MIT/Harvard 数字与研究设计存在错配。
6. GitHub 报告通过 eacli `repo.public.*` 回查 Laya 与 CUA；Magpie 的 typed repo 读取暂时失败，降级 web.search 确认仓库与公开页面。
7. 审计完成前比较当前 HEAD 与目标远端 ref；若目标 ref 含当前工作树没有的报告，使用固定 commit 读取或隔离 worktree 审查，不能以脏工作区为全库快照。

静态结果中有 **133 条 WARN**：83 条缺 semantic tags、41 篇缺 frontmatter，以及少量证据锚点/占位符提示。它们多数是旧版结构债务，不能直接等同于内容错误。Podcast 领域审计为 `ERROR 0 / WARN 0`，说明格式和三件套机制有效，但仍无法替代医学事实与原始语音质量判断。

## 必须重写：6 篇

| 优先级 | 报告 | 生成身份 | 原因 |
|---|---|---|---|
| P0 | [2026-09-22_meta-muse_product-research.md](../ai-learning/reports/2026-09-22_meta-muse_product-research.md) | claude-code-glm-5.3-1m | 核心标题与结论依赖单一二手 APK 逆向文章，关键权限、端点与架构未由实际 APK 或第二来源验证；需以真实 APK/官方材料重建证据链。 |
| P0 | [2026-07-04_bilibili-kema_huangxiang-brain.md](../podcast-learning/reports/2026-07-04_bilibili-kema_huangxiang-brain.md) | kimi-cli-k3 | 核心可操作建议建立在嘉宾口述且未定位的一手研究上；11.5 小时空腹研究未检出，MIT/Harvard 数字与研究设计被混写，医学与教育风险较高。 |
| P0 | [2026-10-06_xiaoyuzhou-tulong-dashihua_karl-deisseroth.md](../podcast-learning/reports/2026-10-06_xiaoyuzhou-tulong-dashihua_karl-deisseroth.md) | pi-glm-5.3 | 英文回答被 Whisper 强制转成破碎中文，报告大量内容仅为“可辨大意”；核心来源失真，必须改用视频字幕、英文原声或原书。 |
| P1 | [2026-08-13_ximalaya-bannatie-gushipian_jiangzhushan.md](../podcast-learning/reports/2026-08-13_ximalaya-bannatie-gushipian_jiangzhushan.md) | claude-code-glm-5.3-flash | 无音频、无 transcript，正文由 shownotes 标题级推断与典籍记忆拼成；当前只能保留为降级索引，取得音频后重写。 |
| P1 | [cooking-logic-timing-douyin.md](../web-surfing/reports/cooking-logic-timing-douyin.md) | kimi-cli-k3 | 将视频口述直接写成烹饪化学结论，盐、热锅冷油、谷氨酸钠等多处存在过度简化或常见误区；无公开原视频链接且暴露本地路径。 |
| P1 | [2026-09-06_xiaoyuzhou-daxiaoma-keji_v94-rocket-recovery-sunology.md](../podcast-learning/reports/2026-09-06_xiaoyuzhou-daxiaoma-keji_v94-rocket-recovery-sunology.md) | claude-code-glm-5.3 | 事实核验可靠，但 78 分钟、2.27 万字转写被压成 2227 字报告，真正承载节目内容的概览与分析仅 829 字；十个 shownotes 章节的大量论证只留索引。旧 Reviewer 仅核对生成者主动登记的 claim，93.05 分没有反映内容召回失败。 |

前五篇的共同点是**核心证据层坏了**；大小马 V94 暴露的是**消费层与复核层坏了**：原始材料完整、事实也较准确，但报告不能独立承载学习任务。两类问题都无法靠补一个链接解决。

## 局部修复：28 篇

### P1：优先处理

| 优先级 | 报告 | 生成身份 | 修复点 |
|---|---|---|---|
| P1 | [PuRo-2B_开放低成本预训练配方_MuonHyperball与RTX5090_深度解析_20261015.md](../ai-learning/reports/knowledge_reports/PuRo-2B_开放低成本预训练配方_MuonHyperball与RTX5090_深度解析_20261015.md) | claude-code-glm-5.3-1m | 既有独立 review 已指出 FP4“唯一选项”、arXiv 作者元数据、Table 7/19 页码和“外推/内插”四处局部问题；主体可靠，无需重写。 |
| P1 | [vLLM_V1架构总览_深度解析_20260821.md](../ai-learning/reports/knowledge_reports/vLLM_V1架构总览_深度解析_20260821.md) | kimi-cli-k3 | 公共报告写入真实本机绝对路径，且源码证据只对本地 tag 可读；改为公开仓 commit/文件链接即可。 |
| P1 | [vLLM_调度器_continuous_batching真身_20260909.md](../ai-learning/reports/knowledge_reports/vLLM_调度器_continuous_batching真身_20260909.md) | zcode-glm-5.3 | 源码判断有价值，但仅引用本地 checkout 的行号，缺公共 commit 链接；旧版占位符启发式也需澄清。 |
| P1 | [中国AI创业与一级市场故事线_从模型信仰到应用求生_20260731.md](../ai-learning/reports/knowledge_reports/中国AI创业与一级市场故事线_从模型信仰到应用求生_20260731.md) | trae-openrouter-3o | 大量数字有来源但质量层级混杂，核心“价值单向迁徙”外推强于证据；需降格低质量二手源并收紧全称结论。 |
| P1 | [投机解码SpeculativeDecoding_科普讲解_20260720.md](../ai-learning/reports/knowledge_reports/投机解码SpeculativeDecoding_科普讲解_20260720.md) | kimicli-K3 | 正文正确说明“保持输出分布”，但标题和开篇“一个字不改/完全相同”易被理解为同随机过程下序列逐字相同；需改成分布无损。 |
| P1 | [48_vista_2026.md](../ai-learning/reports/paper_analyses/48_vista_2026.md) | zcode-glm-5.3 | 论文数字结构清楚，但代码证据指向私有 infra 与本机目录；公开报告应改为公共 commit/file 位置并补可复核限制。 |
| P1 | [research_NandhaKishorM_laya.md](../github-trending-analyzer/reports/research_NandhaKishorM_laya.md) | pi-glm-5.3 | 源码深度足够，但无 frontmatter/公共定位；竞品与当前统计需加快照日期和来源链接。 |
| P1 | [research_trycua_cua_sourcecode.md](../github-trending-analyzer/reports/research_trycua_cua_sourcecode.md) | kimi-cli-k3 | 源码地图质量高，但无 frontmatter且写入 ~/workspace 私有路径；应换成公共 commit/file 证据。 |
| P1 | [research_yetone_magpie.md](../github-trending-analyzer/reports/research_yetone_magpie.md) | zcode-glm-5.3 | 代码研究主体可信，但无 frontmatter、无公共证据链接，且 stars/版本/adapter 数均高度易变；需固定快照和来源。 |
| P1 | [2026-02-11_xiaoyuzhou-chengwei-buffett_nantian.md](../podcast-learning/reports/2026-02-11_xiaoyuzhou-chengwei-buffett_nantian.md) | claude-code-glm-5.3 | 原始 transcript 未入仓，仅 polished 可复核；大量商业史和投资数字来自口播，应补原始工件 receipt 与关键事实来源，并移除 /srv 路径。 |
| P1 | [2026-08-04_rss-guigu101_shengying.md](../podcast-learning/reports/2026-08-04_rss-guigu101_shengying.md) | kimi-cli-k3 | 公开报告包含本地/私有 URL 路径，市场融资数字与人名仍有未核实项；需清理路径并补公开来源。 |
| P1 | [2026-08-21_bilibili-fanshu_yanzheng.md](../podcast-learning/reports/2026-08-21_bilibili-fanshu_yanzheng.md) | kimi-cli-k3 | 大众医学转述把 Omega-6 等复杂问题简化成单向促炎；需补一手来源并把自查建议降格。 |
| P1 | [2026-08-24_xiaoyuzhou-boluo-jiankang_liufangqi.md](../podcast-learning/reports/2026-08-24_xiaoyuzhou-boluo-jiankang_liufangqi.md) | kimi-cli-k3 | 肠癌治疗数据和“先别手术”传播风险高，虽有声明但核心数字未对应具体研究；需逐项绑定指南/试验适用边界。 |
| P1 | [2026-09-03_bilibili-bruce-phd_energy-boost.md](../podcast-learning/reports/2026-09-03_bilibili-bruce-phd_energy-boost.md) | claude-code-glm-5.3-1m | 独立 review 已给出 3 处超出字幕证据的修词、广告时长和速览限定问题；另缺 transcript/polished 路径字段。 |
| P1 | [2026-09-27_xiaoyuzhou-boluo-jiankang_chengruoqian.md](../podcast-learning/reports/2026-09-27_xiaoyuzhou-boluo-jiankang_chengruoqian.md) | claude-code-glm-5.3-flash | 生长激素、肿瘤风险、骨龄频率等临床建议主要来自口述；需用指南和队列数据校准，并移除公开报告中的内部 artifact 路径。 |
| P1 | [2026-10-08_xiaoyuzhou-shuoyi-jieyao_vol91-cod-mercury.md](../podcast-learning/reports/2026-10-08_xiaoyuzhou-shuoyi-jieyao_vol91-cod-mercury.md) | pi-glm-5.3 | 毒理数字密集且未逐项核对 FDA/EPA/WHO；结论框架可留，但必须绑定一手阈值、份量和适用人群。 |

### P2：维护性修复

| 优先级 | 报告 | 生成身份 | 修复点 |
|---|---|---|---|
| P2 | [Evoken陈冕晚点访谈_AI应用生存策略_20260729.md](../ai-learning/reports/knowledge_reports/Evoken陈冕晚点访谈_AI应用生存策略_20260729.md) | kimi-cli-k3 | 访谈自述与分析已分层，但来源字符串不可直接复核；补原访谈链接和可验证经营数据即可。 |
| P2 | [KimiK3_信息流三方向_科普讲解_20260728.md](../ai-learning/reports/knowledge_reports/KimiK3_信息流三方向_科普讲解_20260728.md) | trae-openrouter-3o | 科普主线清楚；需把官方 benchmark/“开源新王”“全球首个”与独立结论分层，并补局限章节。 |
| P2 | [Laya_System1决策模型_深度解析_20260922.md](../ai-learning/reports/knowledge_reports/Laya_System1决策模型_深度解析_20260922.md) | zcode-glm-5.3 | 源码与实测充分，但需固定公共 commit、刷新易变统计并明确与 GitHub repo 报告的职责边界。 |
| P2 | [PersonalContext正交论_PC构建指南_20261010.md](../ai-learning/reports/knowledge_reports/PersonalContext正交论_PC构建指南_20261010.md) | pi-glm-5.3 | 概念框架有价值，但来源多为描述性条目而非可点击定位，部分行业判断需补 [推测] 与失效条件。 |
| P2 | [评估笔记_book-to-skill能否优化学习项目_20260729.md](../ai-practice/experiments/book-to-skill-demo/评估笔记_book-to-skill能否优化学习项目_20260729.md) | trae-openrouter-3o | 实验结论与真实输出充分；补规范 frontmatter、产物路径与环境版本即可。 |
| P2 | [2026-07-29_bilibili-kedaibiao-lizheng_jove-fde.md](../podcast-learning/reports/2026-07-29_bilibili-kedaibiao-lizheng_jove-fde.md) | kimi-cli-k3 | 正文证据分层清楚，但 frontmatter 缺 transcript/polished 路径，已有文件可直接回填。 |
| P2 | [2026-07-30_xiaoyuzhou-wandian-latetalk_chenmian.md](../podcast-learning/reports/2026-07-30_xiaoyuzhou-wandian-latetalk_chenmian.md) | trae-openrouter-3o | 内容可信且自述边界清楚；需明确 polished=false/缺失原因并补标准来源定位。 |
| P2 | [2026-08-14_bilibili-zhuzhu-baofengxue_bauman-work-consumerism.md](../podcast-learning/reports/2026-08-14_bilibili-zhuzhu-baofengxue_bauman-work-consumerism.md) | kimi-cli-k3 | 双源读法很好，但公开报告暴露本地书籍路径；改为规范书目信息和章节页码即可。 |
| P2 | [2026-09-02_multi_kimi-k3-dueling-reads.md](../podcast-learning/reports/2026-09-02_multi_kimi-k3-dueling-reads.md) | claude-code-glm-5.3-1m | 对照价值高，但跨期来源路径和限制不够明确；补两份单期报告/原始材料的职责与外推边界。 |
| P2 | [2026-09-22_xiaoyuzhou-bannatie-zhoukan_no50-weekly-news.md](../podcast-learning/reports/2026-09-22_xiaoyuzhou-bannatie-zhoukan_no50-weekly-news.md) | claude-code-glm-5.3-flash | 报告信息完整，但 transcript 曾经人工分片重录、无 polished；应补 artifact receipt、去内部路径，并明确哪些数字仅为节目转述。 |
| P2 | [2026-10-09_rss-kedaibiao-lizheng_career-methods-series.md](../podcast-learning/reports/2026-10-09_rss-kedaibiao-lizheng_career-methods-series.md) | pi-glm-5.3 | 跨 10 件 transcript 的特殊元数据目前不可机器解析；内容可留，改成显式 source list 与聚合统计。 |
| P2 | [huizhou-rental-guide-2026-09.md](../web-surfing/reports/huizhou-rental-guide-2026-09.md) | claude-code-glm-5.3-1m | 决策信息充分且多轮订正，但缺规范 frontmatter，部分 Gemini/搜索聚合口径应降格并标过期时间。 |

## 保留与历史快照

- **66 篇保留**：论证主线与来源边界成立。Podcast 占多数，特点是把嘉宾观点明确归属、保存原始转写并诚实列出 `[?]`。
- **38 篇 AI 日报保留为历史快照**：报告按日期记录当日公开信息，链接密度高；抽样事实核验未发现系统性编造。将旧日报按今天的信息重写会破坏时点价值。
- 对这 104 篇只建议做无语义批量维护，例如 frontmatter、semantic tags 和公开路径清理；不要为了迁移到 `report-v2` 重写正文。

完整的逐篇判定、生成身份、commit、审查深度和理由均在 JSON 账本中。

## 分领域结果

| 领域 | 保留 | 历史快照 | 修复 | 重写 |
|---|---:|---:|---:|---:|
| ai-learning | 10 | 0 | 10 | 1 |
| ai-practice | 0 | 0 | 1 | 0 |
| github-trending-analyzer | 0 | 0 | 3 | 0 |
| philosophy-learning | 2 | 0 | 0 | 0 |
| podcast-learning | 53 | 0 | 13 | 4 |
| web-surfing | 1 | 38 | 1 | 1 |

### 领域判断

- **Podcast**：转写、来源边界和工件保存总体成熟，内容召回门禁仍不成熟。除医学口述、英文转写和无音频降级外，大小马 V94 证明“只写 polished 之外的增量 + 正文 ≤2500”会把学习报告压成索引。
- **AI Learning**：长文推理总体强，常见缺陷是引用只指向本机/私仓、官方 benchmark 与独立结论混写，以及宏大结论比证据走得更远。
- **Web Surfing**：日报适合保留时点；惠州租房报告证据密度高，只需结构维护；炒菜报告把短视频经验包装成化学规则，需重写。
- **GitHub Research**：三篇代码分析均有实质内容，问题是缺 frontmatter、公共 commit 和可点击代码证据，属于修复而非重写。
- **哲学与实验**：三篇均保留。哲学报告明确标出实际阅读章节；book-to-skill 实验记录了真实命令与失败边界。

## 按生成环境观察

下表用于发现流程盲区，不是模型排行榜；不同模型承担的任务类型差异很大。

| 生成身份 | 保留 | 历史快照 | 修复 | 重写 |
|---|---:|---:|---:|---:|
| claude-code-glm-5.3 | 2 | 5 | 1 | 1 |
| claude-code-glm-5.3-1m | 6 | 0 | 4 | 1 |
| claude-code-glm-5.3-flash | 2 | 18 | 2 | 1 |
| kimi-cli-k3 | 23 | 0 | 8 | 2 |
| kimicli-K3 | 4 | 0 | 1 | 0 |
| pi-glm-5.3 | 21 | 0 | 4 | 1 |
| trae-openrouter-3o | 3 | 0 | 4 | 0 |
| zcode-glm-5.3 | 5 | 15 | 4 | 0 |

可复用观察：

- Kimi K3 的播客长文通常结构与叙事较强，但更容易把嘉宾的医学或行业数字带入正文；高风险主题需要一手来源复核。
- GLM 5.3 在源码和长报告中能产出高密度证据，但经常把本机 checkout、私仓 reference 或搜索摘要当作公开可复核证据。
- Pi + GLM 的新式 Podcast 报告下限明显提高；现有独立 review 发现的问题多是措辞、路径和证据强度的小偏差。
- Flash 主要承担 AI 日报，适合快速时效任务。它的快照质量不能与论文、医学或源码报告直接比较。
- OpenRouter 3o 的早期报告概念综合能力不错，来源定位与硬证据合同弱于后续流程。

## 实施顺序建议

1. **P0 重写**：脑科学教育、Deisseroth、Meta Muse。它们分别涉及健康建议、破损原始语音与伪一手逆向。
2. **P1 重写/修复**：无音频《蒋竹山》、炒菜化学，以及医学、源码证据和已有 reviewer 明确指出的问题。
3. **P2 批量修复**：frontmatter、source locator、semantic tags、聚合 transcript 清单。
4. **历史日报**：只做 metadata 迁移，不回写今天的事实。

## 机制层发现

这轮审计及随后复盘说明现有质量门有五个盲区：

1. **可访问性没有进入证据门禁**：`file:line` 很精确，但若只指向本机或私仓，公开读者无法复核。
2. **高风险领域没有升级策略**：医学、营养、儿童教育报告目前与普通创业访谈走同一门槛。
3. **source quality 与 source presence 被混为一谈**：有 transcript 或 URL 不代表原始材料可用；破碎英文转写和二手 APK 文章都能绕过静态检查。
4. **审计快照没有固定**：初版只看当前工作树，漏掉 `origin/main` 已提交的两篇报告，却仍宣称完成最近三个月全量审计。
5. **证据精度掩盖内容召回**：Evidence 只登记报告已经选择写入的 claim，Reviewer 也只核对这些 claim；被整段省略的节目内容不会进入失败列表。同模型 Generator/Reviewer 还可能共享同一种压缩偏好。仅在 Prompt 中要求来源优先仍不足，独立内容地图必须成为结构化复核工件。

已落地的机制修复：公开路径检查；医学/健康一手指南或论文；播客 `report_depth` 与 `reader_contract: standalone`；evidence `source_coverage`；Reviewer `source_content_map` 与逐章最低覆盖；standard/deep 报告内容地图与展开小节检查；全量审计固定 Git ref 并核对远端差异。V94 revision 3 已实际触发 `REV033` 阻断，证明新门禁不是只写在文档里的规则。

## 审计边界

- 138 篇完成结构与内容卡片复核；高风险与修复/重写项做了全文和来源回查。对 38 篇日报采用系列审计与高风险抽样，没有逐条重新打开其数千个外链。
- 审计目标 ref 已订正为 `origin/main@1025836`；初版工作树 ref 为 `bf3642c`。本次复盘保留这项失误记录，不用更新后的数字抹掉原始范围错误。
- 未把旧报告全部迁移到 `report-v2`，避免结构性大 diff 被误当成质量提升。
- 本报告给的是当前修复决策。易变数字仍应在真正修订对应报告时重新读取原始来源。
