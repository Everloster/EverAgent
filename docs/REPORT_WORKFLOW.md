# EverAgent 报告生产工作流

> 适用范围：用户明确要求研究、精读、深挖、分析并归档，或现有任务协议要求形成长期报告时。
> 本文件是报告流程的唯一公共 owner；领域差异仍由各项目 `AGENTS.md` 与专用 skill 负责。
> 跨模型证据账本、独立复核、评分和升级策略见 [REPORT_QUALITY_GATE.md](./REPORT_QUALITY_GATE.md)。

## 1. 先判断是否需要报告

| 常见任务 | 默认动作 | 是否落报告 |
|---|---|---|
| 查一个事实、解释一条命令、临时转换 | 直接回答 | 否 |
| “帮我学 / 精读 / 深入 / 出报告” | 研究并归档 | 是 |
| 文章、论文或长文的深度分析 | 读原文、交叉核验、写报告 | 是 |
| GitHub 链接且未说明目的 | 轻量介绍 | 否 |
| GitHub 链接并明确“深挖 / 研究 / 出报告” | 走 repo 深研 skill | 是 |
| 播客或视频链接 | 走静默转写与报告流程 | 是 |
| 上网查清单或一次性公开信息 | 先直接交付；有长期复用价值时归档 | 条件式 |
| 最小 demo / 实验 | 运行代码并写实验笔记 | 是 |
| 追问已有主题 | 优先更新原报告并记录日期 | 通常不新建 |

用户已明确主题和交付物时直接推进。开放式学习请求若没有主题或方向，且选题会实质改变结果，先问一次当前兴趣；确认后再研究，并按需更新领域 `MAP.md`。其它缺失信息只有会实质改变研究对象、风险或最终形态时才提问。

### 本次任务合同

在当前会话中明确四项即可，无需新建计划文件：目标、交付物、验收信号、停止条件。用户已授权的本地与可逆步骤持续执行到验收信号满足；只有真正的外部写入、不可逆动作或会改变报告方向的歧义才暂停。

## 2. 最小上下文加载

按以下顺序加载，够用即停：

1. 当前路径生效的 `AGENTS.md`。
2. 与报告体裁对应的 skill；不要同时读取所有模板。
3. `METHODOLOGY.md` 中与本次来源类型、证据和结尾要求相关的章节。
4. `config/report-quality-policy.json` 中当前任务等级需要的模型与评分策略。
5. 通过 `eacli context get --domain <domain> --json` 取得领域入口；需要定位具体主题时用 `eacli context search --domain <domain> --query "<主题>" --json`，只读取命中的报告或 wiki 页面。
6. 仅在以下条件读取画像文件：
   - `PROFILE.md`：需要选择讲解深度、写作风格，或用户本轮表达了新偏好；
   - `MAP.md`：需要判断覆盖缺口，或报告完成后新增了长期主题；
   - `wiki/open-questions.md`：需要续接旧问题，或准备沉淀新的未解问题。
7. 只有需要 evidence-record 写作约束时读取 `docs/external-skills/scientific-agent-skills/scientific-writing/SKILL.md`；需要对立假说和判别性预测时读取同目录的 `hypothesis-generation/SKILL.md`。

不要默认通读整个 `reports/`、`wiki/`、所有 skills 或三份画像文件。目录扫描只用于定位，正文读取应由任务相关性驱动。

## 3. ACE 循环：生成、反思、策展

这里的 ACE 指 Agentic Context Engineering。报告任务采用轻量三段循环：

### Generator：完成当前报告

- 明确研究问题、来源边界、读者和交付路径。
- 为新报告选择 `standard / important / flagship`，运行 `report_quality.py init`，在研究过程中填写 evidence manifest。
- 先读原始材料，再写事实；知识截止后的事实必须联网核验。
- 把事实、来源解读和自己的推断分开。
- 观点文章或论证型材料在能澄清主线时使用 `x → f → f(x)`；实证论文按研究问题、设计、结果与局限组织。

### Reflector：检查真实缺陷

完成初稿后，检查：

- 关键结论是否有可追溯来源；
- 数字、日期、单位与正文是否一致；
- 是否把厂商自述、二手转述或推测写成事实；
- 是否遗漏限制、反例、适用边界；
- 用户要求的交付物是否全部完成；
- 是否出现无关扩写、重复结论或模板残留。

### Independent Reviewer：独立复核

- 使用全新会话，只提供任务、报告、证据账本和原始来源，不提供生成者的推理过程。
- 逐项复核用户要求、关键 claim 与来源支持关系，填写五维评分和未解决问题。
- Reviewer 的默认选择、升级顺序、稀缺与禁用模型只从 `config/report-quality-policy.json` 读取；运行 `python3 scripts/report_quality.py policy --json` 查看当前值。
- Reviewer 不直接宣称通过；最终判定由 `report_quality.py check` 计算。

运行确定性检查：

```bash
python3 scripts/report_quality.py check <报告路径> --finalize  # report-v2
python3 scripts/reindex.py
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

播客报告还需运行其领域审计；代码实验运行该项目要求的真实验证。
完成一次必要检查后，只有正文、证据文件或相关代码继续变化，或检查暴露新风险时才重跑受影响部分。

### Curator：只写入可复用增量

报告完成后，只在发现以下内容时更新 context 或 skill：

- 跨任务可复用的新事实、方法或失败模式；
- 已有规则被真实任务证明过时、冲突或缺失；
- 高风险的一次失败，值得立刻固化为硬边界。

普通一次性细节留在报告中。不要因为每做完一个任务就自动扩写 `AGENTS.md` 或 skill。更新采用局部 delta，保留既有有效内容，避免整份文档由模型反复重写后发生 context collapse。

## 4. 报告合同

新报告使用 `quality_schema: "report-v2"`，并至少包含：

```yaml
---
title: "报告标题"
domain: "所属项目"
report_type: "报告类型"
status: "in_progress"
updated_on: "YYYY-MM-DD"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["tag"]
---
```

独立复核通过后由 `report_quality.py check --finalize` 切换为 `completed`；需要归档语义的体裁使用 `--final-status archived`。

正文最低要求按任务类型变化：

| 类型 | 必须具备 |
|---|---|
| 论文 / 实证研究 | 原始材料、方法与样本、精确数字、证据质量、局限、思考与追问 |
| 文章 / 观点分析 | 原文论证重构、事实核验、作者观点与个人推断分离、反方边界、思考与追问 |
| 概念深挖 | 定义、机制、设计动机、关联概念、前沿与争议、思考与追问 |
| 播客 / 视频 | 原始转写、润色依据、shownotes 核验、来源内容地图、核心论证与案例、增量观点、关键数字、Limitations、思考与追问；标准/深度报告必须独立可读，不能把 polished 当成必读正文 |
| GitHub 深研 | API 元数据、真实代码、量化活跃度、至少两个竞品、证据标签、七章结构 |
| Web 调研 | 查询范围与时间、来源链接、筛选口径、事实与建议分离、数据时点 |
| 代码实验 | 可运行代码、环境与命令、真实输出、失败记录、结论适用范围 |

`思考与追问` 对 A 类学习报告与播客报告强制；短期清单、日报、repo 汇总和实验日志可使用更适合其用途的结尾。

## 5. 报告完成定义

一篇报告只有同时满足以下条件才算完成：

1. 原始材料已实际读取，来源路径或 URL 可复核；
2. 用户要求的问题有明确回答，报告可脱离当前对话独立阅读；
3. 事实、来源主张和分析者推断已区分；
4. 关键数字包含单位、时间和口径；
5. 限制与未解决问题已写明；
6. evidence manifest 覆盖关键 claim，独立 review 达到对应 tier 门槛；
7. 应更新的 MAP、PROFILE、wiki 仅以最小 delta 同步；
8. 报告质量门通过，README 与报告索引处于最新状态。

对 `report_depth: standard | deep` 的播客报告，完成定义还包括：Reviewer 在读报告前先从转写、精编或 shownotes 独立列出核心内容单元，写入 review 的 `source_content_map`，再核对 evidence 的 `source_coverage`。声明有 shownotes 章节时，每章都要在两张地图中留痕；核心单元遗漏属于 `core_requirement_missing`。报告中已写内容全部正确，不能抵消重要内容的大面积缺失。

## 6. 评估报告机制

### 静态门禁

全库审计先固定 Git 快照。记录当前 HEAD 与目标 ref（默认 `origin/main`）；若当前 HEAD 不包含目标 ref，`audit_reports.py --all` 会以 `SCOPE001` 停止。此时在隔离 worktree 中审目标 commit，不能扫描当前脏工作树后宣称“全量完成”。

```bash
python3 scripts/audit_reports.py --changed
python3 scripts/audit_reports.py --all --json
python3 scripts/report_quality.py check <报告路径>
python3 scripts/eval_report_context.py
python3 scripts/reindex.py --check
```

静态门禁检查元数据、来源锚点、学习闭环、占位符、内部链接、索引状态，以及指令 Owner、常驻字节预算、skill description、渐进披露和 ACE 任务集结构。
它还回放 `evals/report-quality-replays.json` 中的真实报告，确认策略版本、最终分数、正文与证据哈希仍一致。模型驱动的完整 ACE Context A/B 不进入每次 commit 的同步阻断；结果过期只告警，留给 Context 架构里程碑验收。

### 行为回放

任务集位于 `evals/ace-report-tasks.json`。在同一模型、推理档位和工具条件下，用旧版与候选 context 各跑相同任务，记录：

```bash
python3 scripts/eval_report_context.py --template > /tmp/ace-run.json
python3 scripts/eval_report_context.py --score /tmp/ace-run.json
python3 scripts/eval_report_context.py --aggregate /tmp/*-run.json
```

- 路由是否正确；
- skill 选择的 precision / recall，是否加载了邻近但无关的 playbook；
- 是否创建了不该创建的报告；
- 首次行动前读取了多少文件，是否命中明确禁止的无关 context；
- 是否发生无必要澄清或审批；
- 是否满足可观察的完成信号，或在真正的授权边界前正确停止；
- 报告门禁是否通过；
- report quality 五维分数及 P10；
- 工具调用、输入 token、compaction 与返工次数。

填写实际加载的仓库 skill、首次行动前文件、澄清次数、完成信号与停止原因；不要根据“应该怎样做”反填理想值。

安全边界、证据正确性和交付完整性不得退化。效率指标只有在质量不降时才有意义。

## 7. Context 变更规则

- `AGENTS.md`：只放稳定不变量、意图路由和按需入口。
- Skill description：只描述能力与准确触发边界。
- `SKILL.md`：放工作流骨架；复杂模式继续路由到 reference。
- 领域文档：放学科特有证据要求和输出形式。
- 脚本 / hook / CI：放可判定、需要稳定执行的硬规则。
- 任务 prompt：放本次目标、交付物、授权与完成定义。

模型专属的行为补丁应记录适用模型和复核条件，不直接升级成跨模型永久规则。
