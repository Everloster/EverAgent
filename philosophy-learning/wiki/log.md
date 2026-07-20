# philosophy-learning · Wiki 操作日志

> append-only。每次 ingest / query-archive / lint 追加一条记录。
> 格式：`## [YYYY-MM-DD] {操作类型} | {标题}`
> 快速查看最近 5 条：`grep "^## \[" log.md | tail -5`

---

<!-- 日志从此处开始追加 -->

## [2026-06-21] ingest | 美学三论：康德 + 杜威 + 丹托（SocratesAgent 主导）
- 新建报告：reports/text_analyses/美学三论_20260621.md（898 行 / ~13,000 字 / text_analysis）
- 更新 wiki 页面：
  - 新建 concepts/aesthetics.md（美学三论比较框架）
  - 更新 wiki/index.md：concepts 表新增"美学"分类 + 1 个新概念入册
  - 更新 philosophy-learning/CONTEXT.md：text_analyses 列表追加新报告；新增"美学主线"边界区
- 数据源：康德《判断力批判》§1-§16, §42-§50（1790）/ Dewey《Art as Experience》Ch.1-3（1934）/ Danto "The End of Art" 1984 论文 + 1997 专著
- 报告特色：3 家原典互参（中德英）+ 6 张对比表 + 3 张 mermaid 图（关系图 / 时间线 / 张力地图）+ AI 生成艺术相关性追问
- 报告严格区分"原典主张"与"分析者推论"，后者均以 [推论] 标注
- 防幻觉边界：康德 §17-§41, §51-§83 / 杜威 Ch.4-14 / 丹托 1997 专著 Ch.6-10 标注"未在本次精读范围"
- 状态：plan §8 短期标准 ≥10 entities / ≥8 concepts 继续满足（11 entity + 15 concept）
- 哲学史定位：补齐"美学"分支——这是哲学学习的第 6 个主分支（之前覆盖：认识论/形而上学/伦理学/政治哲学/心灵哲学/语言哲学）

## [2026-06-03] ingest | 维特根斯坦《逻辑哲学论》深度精读（MiniMax-M3 主导）
- 新建报告：reports/text_analyses/09_wittgenstein_tractatus_1921.md（713 行 / 58.6 KB / text_analysis）
- 更新 wiki 页面：
  - 新建 entities/wittgenstein_ludwig.md
  - 新建 concepts/picture_theory_of_meaning.md（图示说 / Bildtheorie）
  - 新建 concepts/sayable_and_unsayable.md（可说与不可说 / unsinnig 划界）
  - 新建 concepts/language_limit_world_limit.md（5.6 语言界限即世界界限）
- 更新 wiki/index.md：entities 表追加 1 项（11 entity 总数）；concepts 表新增"语言哲学"分类，3 个新概念入册
- 更新 philosophy-learning/CONTEXT.md：text_analyses 列表追加新报告；防幻觉边界移除"维特根斯坦尚无独立报告"（已覆盖）
- 数据源：用户直接调度，绕开 SocratesAgent task board；本项目首份由 MiniMax-M3 生成的 text_analysis
- 报告特色：7 步分析框架 + 11 个 LLM 联结角度（全部 [推论] 标注，区分原意与类比）—— 首次将 LLM 工程议题（in-context learning、RLHF、mechanistic interpretability、emergent abilities）与维特根斯坦语言哲学系统化联结
- 状态：plan §8 短期标准 ≥10 entities / ≥8 concepts 双双满足（11 entity + 14 concept）

## [2026-04-08] phase2-init | Phase 2 起步：philosophy-learning wiki 内容蒸馏
- 新建 entities：socrates / plato / aristotle / descartes_rene / hume_david(stub) / kant_immanuel / hegel_georg / nagel_thomas / rawls_john / gettier_edmund（共 10 个）
- 新建 concepts：theory_of_forms / socratic_method / cogito_ergo_sum / mind_body_dualism / categorical_imperative / virtue_ethics_eudaimonia / dialectic / justice_as_fairness / jtb_knowledge / qualia_subjective_experience / epistemic_luck（共 11 个）
- 新建 overview.md：5 主线（认识论/形而上学/伦理学/心灵哲学/政治哲学）+ 时间拐点 + 概念依赖图 + 7 大对立张力
- 重写 index.md：将所有 entity / concept / overview 按学科分组登记
- 数据源：哲学关键人物图谱、知识_跨时代比较、knowledge/epistemology.md、01_plato_republic_cave_-380、02_descartes_meditations_1641、03_gettier_1963（text + paper）、04_nagel_bat_1974、04_plato_meno_-380、05_kant_groundwork_1785、06_aristotle_nicomachean_ethics_-350、07_hegel_phaenomenologie_1807、08_rawls_theory_of_justice_1971
- 状态：plan §8 短期标准 ≥10 entities / ≥8 concepts 双双满足（10 entity + 11 concept）
- 已知问题：休谟为 stub（待《人性论》精读）；维特根斯坦/海德格尔/尼采/弗雷格 在人物图谱中是节点但无独立精读，本轮不建页

## [2026-06-22] deepen (conversational-learning) | 程乐松 道教观念史与宗教经典诠释学 思想综述
- 模式：对话学习车道（用户发起"想学习程乐松教授的相关哲学"，§2B）。随项目扩为「世界哲学」范围后中国哲学方向首篇。
- 新建报告：reports/concept_reports/程乐松_道教与宗教诠释学_思想综述_20260622.md（5 层理解模型，含公开来源标注与 [推论] 区分）
- 新建 entity：wiki/entities/cheng_lesong.md（北大哲学系教授·道教观念史）
- 新建 concept：wiki/concepts/religious_hermeneutics_idea_history.md（观念史视角 + 宗教经典诠释学）
- 更新 index.md：Entities 表 + Concepts 新增「中国哲学」组
- 核心知识：以宗教（信仰）的方式看待宗教 · 观念史视角（身体/不死/神秘主义）· 同情性理解 vs 客观性 · 放下现代性的傲慢 · 日常即超越 · 道/术动态互构 · 效验作为神圣性标准
- 数据源：北大哲学系官方简介 + 《道教研究学报》第十期(2018)书评 + 北大文研院未名学者讲座09(2016) + 北大国际合作部赫拉利对谈报道(2025-03)
- 防幻觉：在世学者，全部事实陈述附公开来源，推论标 [推论]
- 执行者：SocratesAgent / Trae Openrouter（对话学习模式）

## [2026-06-22] deepen (conversational-learning) | 程乐松追问深入：以死长生 + vs 西方宗教学
- 模式：对话学习车道追问续写（用户选 #1+#2），未新建报告。
- 续写报告：reports/concept_reports/程乐松_道教与宗教诠释学_思想综述_20260622.md 追加「## 追问深入 [2026-06-22]：两个核心主题深挖」+ 4 道追问检验题
- 更新 concept：wiki/concepts/religious_hermeneutics_idea_history.md 新增「追问深入」小节
- 主题一「以死长生」：外丹丹与毒同体悖论 · 身体是信仰枢纽 · 长生技能/叙事/信仰三面相 · 陈撄宁仙学现代化回响
- 主题二「vs 西方宗教学」：隐匿出发点（西方信仰特征=理论原型/理想型）· 标准先行的方法论偏狭 · 价值中立原则 · "必须懂西方理论但反对单一标准审查" · 信仰不需要辩护
- 数据源：程乐松《从信俗看宗教研究的"中国化"》(中国社科网2025-04) + 《仙学：超越科学与道教的"终结"》(aisixiang) + 未名学者讲座09 + 海淀政协访谈(2023) + 《身体不死与神秘主义》豆瓣目录
- 执行者：SocratesAgent / Trae Openrouter（对话学习模式）

## [2026-07-20] deepen (conversational-learning) | 程乐松一手文本精读：重返经验与「做中国哲学」的手筋
- 背景：用户明确兴趣——程乐松线深挖（非追问攻坚）；前两篇报告（0622 道教综述/0625 当代哲学）均基于二手来源，本篇首次直读一手学术文本。
- 新建报告：reports/concept_reports/程乐松_方法论一手精读_重返经验与做中国哲学_20260720.md（x→f→f(x) 开头三行 + 批判性审视 §七 + 检验题）
- 亲读全文三篇：《重返经验的可能性》（中国社会科学2023(10)）、《重访、拼图与激生》（现代哲学2022(3)）、《断裂的居间性》（哲学动态2024(10)）；调研核验摘引五篇：《自觉的两种进路》（学术月刊2018(7)，含钱穆唯一例证）、《物化与葆光》（含利科专条脚注）、《从信俗看宗教研究的"中国化"》（2025）、《灵验与虔敬》（2024）、《物以化齐言则不齐》（2020）
- 结清 open-questions 两问：①利科=实质方法论资源（两引+批判性专评），"上承钱穆"系微博夸大；②"为己之学"未见学术文本系统论述（公共演说话语）。留「底线思维 vs 道家」仍开放
- 新建 concept：wiki/concepts/chongfan_jingyan_methodology.md（方法论纲领）；更新 entity：cheng_lesong.md（方法论纲领节 + 著作书目补全 + 待深入队列刷新）；更新 wiki/index.md
- 2025-2026 动态采集：一席《善待自己》（2025-12）、2026 毕业致辞（2026-06-26）、中国网专访（2025-11）、《思想的手法》合编（2025-08）——公共发言=方法论的文体转换
- 全局：AGENTS.md §4 新增「兴趣确认」规则（open-questions=历史快照≠当前兴趣，每周 cron 确认）；五领域 MAP.md 优先级队列按 2026-07-20 对话确认更新
- 执行者：kimicli-K3（对话学习模式）
