# 播客报告写作 SKILL — 详细参考

> 按需参考：只读取入口 `SKILL.md` 为当前任务指出的章节，不把本文件当作固定行程逐项执行。

> 每次做播客学习任务（转写→润色→报告→沉淀）时对照本文件执行。它是 2026-10-09 对最近 5 篇报告审计后的沉淀，目的：**每次任务都比上批好一点**。
> 维护规则：每批任务结束先反思；只有跨节目可复用或高风险的问题才以最小 delta 更新本文件，一次性特例留在报告。

---

## 一、开工前（顺序固定）

1. 先用 `eacli knowledge.podcasts` 或仓内 URL/标题检索查重；需要刷新节目单时只跑目标节目：
   `python3 scripts/fetch_show_indexes.py --show <slug> --dry-run --json`。确认要写回后再去掉
   `--dry-run`；不要为查一集默认刷新全部节目。随后运行 `sync_index_status.py` 核对状态列
   （✅ = 跳过）。技术播客雷达中尚未进入个人精选 OPML 的节目不运行该脚本，直接按单集
   `source_url` 查重并保留雷达来源信息。
2. shownotes **先于润色**拿到（智谱 web.read；对含"加息/投资/金融"字样的小宇宙 URL 会触发 1301 审查误判 → curl 公开页面降级并记录）
3. 转写通道判定：小宇宙域名走 Razer eacli podcast；transistor/fireside 直链走本地 `transcribe.py`（Razer 白名单不批）；中英混合音频（外文回答）当前 pipeline 无法正确转写——提前决定"转译大意版"策略并在 frontmatter 标注
4. 转写完成必跑 `python3 podcast-learning/scripts/audit_transcript.py <transcript> --json`
   （同句连续 >3 段失败、时间戳与尾部间隔可见）+ 人工头尾抽查

## 二、润色产物契约（2026-10-09 修订）

默认产物为 **digest（结构化精编）**：`.{slug}.polished.txt` 可为按主题重组的精编稿，但**必须在文件头部标注压缩比**（如"精编版，约为转写全文的 20%，按 X 节主题重组"）+ 保留 [?] 语义。全文逐句润色仅用于用户点名深读的集。理由：审计发现 polished 实际都是精编（10-23%），与其悄悄违约不如诚实命名——但文件名保持 .polished.txt 不动（改扩展名会破坏既有引用），靠头部声明区分。

## 三、报告写作规范（模板 v2）

1. **先选深度，不默认压短**：frontmatter 写 `report_depth: brief | standard | deep` 与 `reader_contract: standalone`。
   - `brief`：用户明确要速览、摘要或日报式交付；正文可控制在约 2500 汉字。
   - `standard`：播客“学习任务”的默认值。报告必须独立重构节目主线、关键例子、分歧与分析；60 分钟以上高密度节目通常需要约 4000–8000 汉字，但长度只是诊断信号，核心标准是内容覆盖。
   - `deep`：用户要求深挖、跨期资料或节目包含高风险/高密度论证；按问题完整性决定篇幅。
2. **顶部「⚡ 速览」**：≤3 行、每行 ≤25 字，30 秒可读完。速览是入口，不能替代正文。
3. **报告必须独立可读**：polished 是证据与细节层，报告是主要消费面。报告应简洁重构所有核心论证，再增加跨集对照和自己的分析；禁止以“polished 已经写过”为由省略节目主线。避免逐句重复，不避免必要的语义复述。
4. **先做来源覆盖表**：按 shownotes、精编章节或自然论证单元列出 `source_coverage`。每个单元标 `core/supporting`、`included/omitted`、报告锚点和省略理由；frontmatter 声明有 shownotes 章节时，每章都要登记。`standard/deep` 的核心单元不得省略。Reviewer 必须先独立读来源，把自己的内容地图写入 `source_content_map`，再映射这张表，不能只审生成者主动登记的 claims 或机械填满 coverage ID。
5. **正文结构**：至少包含内容地图，以及 3 个以上展开后的主线小节；每节需回答“节目说了什么、用了什么例子、证据边界是什么、我如何理解”。数字表和事实核验表不能代替论证正文。
6. **原话引用规范**：「关键观点」引的是润色修正版时，节末统一注明“原话据润色稿，原转写含误识别”；未经修正的原样引用单独标注。引用用于保留声音和关键推理，不追求数量。
7. **wiki 双链 ≥1**：正文至少 1 处 `[[...]]` 链到概念/实体页或相关报告；没有可链对象时在 Limitations 写明。
8. **frontmatter 数字禁止手填**：写完报告必跑 `python3 scripts/fill_report_stats.py <报告>`。跨期多文件等特殊报告若脚本不能正确聚合，只用 `--dry-run` 检查并在 frontmatter 明示多文件口径。
9. **思考与追问·问 2 全量汇入 open-questions**；问 3 的行动项若可执行，写明谁/何时，或明确挂起。
10. **新报告 frontmatter**：增加 `quality_schema: "report-v2"`、`quality_tier: "important"`、`report_depth` 和 `reader_contract: standalone`，并逐字段核对实际节目。

## 四、收尾（顺序固定）

1. `fill_report_stats.py <报告>`——数字校验
2. `sync_index_status.py`——状态回填
3. 从仓库根目录运行 `python3 scripts/reindex.py`、`python3 scripts/audit_reports.py --changed`、`python3 scripts/reindex.py --check`
4. CONTEXT 只追加本期产物与必要边界；普通过程记录不进入长期上下文
5. 若本批出现跨节目复用价值或高风险问题，以一条局部 delta 更新本 skill；否则不改

## 五、纪律红线（2026-10-14 全库 review 后立，违反即返工）

1. **压缩比声明必须取 fill_report_stats 实测值**，禁止手感估——虚高 2-4pp 属诚实性缺陷（2026-10-14 全库查出 4 篇已校准；声明与实测差 >2pp 会被 audit_reports.py 拦下）。
2. **frontmatter 逐字段回看一眼再提交**——2026-10-12 实证：chapters 字段整段复制了另一期的模板。凡复用上一期报告当骨架，改完必须逐字段比对源集 shownotes。
3. **修辞强度不得高于证据强度**：禁用「恰好完备/互斥完备/公理级/所有报告中最 X」类全称断言，除非已逐一核对并在文中写明核对范围；对照性结论用「对照/互补/形成张力」，不用「统一/收束/证明」。
4. **[?] 核实义务**：一次 web.search 就能清掉的 [?]（产品名/人名/公司名）必须在成稿前清；清不掉的才保留，并在 Limitations 写明尝试过什么。靠 [?] 兑底堆密度 = 偷懒。
5. **「原话」引文拼接规则**：允许用省略号跨段拼接，但不得改字/改序/补词；拼接后的语义不得超出原语境。
6. **数字表条目必须是数字**，来源分三级标注：转写原文 / 口播口径 / 嘉宾转述（二手）——二手数字不标注就当一手用是最大风险（2026-10-12 Jev 100 亿估值实证）。
7. **高精度不等于高覆盖**：Reviewer 必须从原始来源反推核心内容，不能把“报告中登记的 claim 全部正确”误判成“报告完整”。2026-10-20 大小马 V94 实证：2.27 万字转写被压成 2227 字报告，概览+分析仅 829 字，旧门禁仍给出 93.05 分。
8. **来源优先必须留下工件**：只在 Prompt 里要求 Reviewer 先画内容地图不可审计。`standard/deep` 播客的 review 必须保存 `source_content_map`，逐项记录来源、重要性、与 `source_coverage` 的映射及覆盖判断。

## 六、已知坑速查（持续追加）

- 智谱 web.read 对小宇宙金融词 URL 误判 1301 → curl 降级
- Razer artifact 拉回：`eacli pull` 当前单文件上限 190KB；更大 transcript 用
  `podcast-learning/scripts/podcast_artifact_pull.py pull` 自动走 `eacli invoke` 远程分片、
  `eacli pull` 拉回并按原 artifact SHA-256 重组（2026-10-19：同一份 234593 bytes artifact
  首轮手工按 100KB 拆成三片；helper 端到端复验按 180KB 拆成两片，重组哈希均一致）
- whisper 转写专名灾难区：Seedance(8+ 写法)/CapCut(5+)/汞→拱肱股肿/鳕→血雪/Li An→李治霖(6 写法)——shownotes 是唯一修正源，无 shownotes 的集慎引专名
- 中英混合访谈：英文被强转破碎中文，两次尝试（zh/auto）均失败——引用以视频字幕/原书为准
- frontmatter source_url 后不要写中文注释（URL 正则会吞）——2026-10-09 sync 失配实证
- transistor/fireside 源的 shownotes 直接从 RSS feed 拿（episode description），比 web.read 稳
