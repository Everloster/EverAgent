# 播客报告写作 SKILL

> 每次做播客学习任务（转写→润色→报告→沉淀）时对照本文件执行。它是 2026-10-09 对最近 5 篇报告审计后的沉淀，目的：**每次任务都比上批好一点**。
> 维护规则：每批任务结束，若发现新问题/新解法，把一行改进写进对应节（保持轻量，勿膨胀成论文）。

---

## 一、开工前（顺序固定）

1. `python3 scripts/sync_index_status.py`——确认该集未被做过（状态列 ✅ = 跳过）
2. shownotes **先于润色**拿到（智谱 web.read；对含"加息/投资/金融"字样的小宇宙 URL 会触发 1301 审查误判 → curl 公开页面降级并记录）
3. 转写通道判定：小宇宙域名走 Razer eacli podcast；transistor/fireside 直链走本地 `transcribe.py`（Razer 白名单不批）；中英混合音频（外文回答）当前 pipeline 无法正确转写——提前决定"转译大意版"策略并在 frontmatter 标注
4. 转写完成必跑重复段检测（同句连续 >3 段报警）+ 头尾抽查

## 二、润色产物契约（2026-10-09 修订）

默认产物为 **digest（结构化精编）**：`.{slug}.polished.txt` 可为按主题重组的精编稿，但**必须在文件头部标注压缩比**（如"精编版，约为转写全文的 20%，按 X 节主题重组"）+ 保留 [?] 语义。全文逐句润色仅用于用户点名深读的集。理由：审计发现 polished 实际都是精编（10-23%），与其悄悄违约不如诚实命名——但文件名保持 .polished.txt 不动（改扩展名会破坏既有引用），靠头部声明区分。

## 三、报告写作规范（模板 v2）

1. **顶部「⚡ 速览」**：≤3 行、每行 ≤25 字，30 秒可读完——用户是抽空阅读，这是第一入口（在"概览"之前，概览保留但压缩到 3-5 条短句）
2. **主要话题 → 增量观点**：只写 polished 里没有的分析性内容（跨集对照、与用户既有知识的连接），**不复述节目内容**——审计发现"章节地图/主要话题/polished"三层重复是报告膨胀的主因。目标正文 ≤2500 汉字（速览+概览+增量观点+数字表+Limitations+追问）
3. **原话引用规范**：「关键观点」引的是润色修正版时，节末统一注明"（原话均据润色稿，原转写含误识别）"；未经修正的原样引用需单独标注
4. **wiki 双链 ≥1**：正文至少 1 处 `[[...]]` 链到概念/实体页或相关报告；该集没有可链对象时在 Limitations 写明（这是审计发现的零双链问题）
5. **frontmatter 数字禁止手填**：写完报告必跑 `python3 scripts/fill_report_stats.py <报告>`（自动统计三件套字数/段数/语速并写回）
6. **思考与追问·问 2 全量汇入 open-questions**（不只挑几条）；问 3 的行动项若可执行，写明"谁/何时"或明确挂起

## 四、收尾（顺序固定）

1. `fill_report_stats.py <报告>`——数字校验
2. `sync_index_status.py`——状态回填
3. `python3 ../scripts/reindex.py` + `lint_evidence.py --domain podcast-learning`
4. CONTEXT 台账追加条目，**末尾加一行「本批改进」**：相对上批改了什么（micro-retro，显性进步记录）
5. 若本批发现新问题/新经验：回写本 SKILL 对应节一行

## 五、已知坑速查（持续追加）

- 智谱 web.read 对小宇宙金融词 URL 误判 1301 → curl 降级
- Razer pull 上限 ~128KB：大 transcript 用 `eacli invoke` 远程 split 分片拉回（2026-10-09 大小马 V95 实证）
- whisper 转写专名灾难区：Seedance(8+ 写法)/CapCut(5+)/汞→拱肱股肿/鳕→血雪/Li An→李治霖(6 写法)——shownotes 是唯一修正源，无 shownotes 的集慎引专名
- 中英混合访谈：英文被强转破碎中文，两次尝试（zh/auto）均失败——引用以视频字幕/原书为准
- frontmatter source_url 后不要写中文注释（URL 正则会吞）——2026-10-09 sync 失配实证
- transistor/fireside 源的 shownotes 直接从 RSS feed 拿（episode description），比 web.read 稳
