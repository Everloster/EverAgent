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
