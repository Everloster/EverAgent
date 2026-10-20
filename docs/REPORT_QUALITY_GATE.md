# EverAgent 报告质量下限

> 目标：让 Pi、Claude Code、Codex 等不同 Harness，以及不同模型生成的报告，都经过同一套可观察、可阻断、可升级的质量流程。
> 当前机器可读策略由 [`config/report-quality-policy.json`](../config/report-quality-policy.json) 维护；每个 `policy_id` 的不可变副本保存在 [`config/report-quality-policies/`](../config/report-quality-policies/)。
> “质量下限”表示未完成证据登记和独立复核的报告不能进入完成状态；它不能数学保证每个判断都真实，因此仍需来源核验与定期人工校准。

## 1. 模型角色

当前默认生成器、Reviewer、升级顺序、稀缺模型和禁用模型只认机器策略：

```bash
python3 scripts/report_quality.py policy --json
```

生成与复核必须记录真实模型和 Harness；两者分开记账，运行环境不能替代模型身份。常规 Reviewer 使用独立新会话，只看任务、报告、证据账本和原始来源；升级 Reviewer 只在策略条件命中时使用。

## 2. 三档质量等级

| 等级 | 适用 | 默认复核 |
|---|---|---|
| `standard` | 日报、常规清单、实验记录 | 一次独立复核 |
| `important` | 文章/论文精读、概念深挖、repo 深研、播客学习报告 | 一次独立复核；失败后按策略升级 |
| `flagship` | 长期基准报告、公开发布、关键决策材料 | 两次独立复核，其中至少一次使用强模型 |

精确总分、单项门槛和最低来源数由机器策略维护。只要出现伪造引用、关键数字无法追溯、漏答核心要求或安全问题，综合分再高也不能通过。

## 3. report-v2 产物

新增报告使用：

```yaml
quality_schema: "report-v2"
quality_tier: "important"
```

每篇报告旁边有两个机器可读文件：

```text
reports/topic.md
reports/.quality/topic.evidence.json
reports/.quality/topic.review.json
```

- `evidence.json`：任务要求、生成模型与 Harness、来源、关键 claim、报告锚点、局限，以及 standard/deep 播客的 `source_coverage` 内容覆盖表。
- `review.json`：独立 Reviewer、来源优先生成的 `source_content_map`、已核验的要求/claim/来源、五维评分、未解决问题和最终判定所用策略版本。
- JSON schema：[report-evidence-v1](../schemas/report-evidence-v1.schema.json)、[report-review-v1](../schemas/report-review-v1.schema.json)。

`kind: local` 的来源使用仓库相对路径，并且必须指向仓内普通文件；绝对路径、越界路径和符号链接会被拒绝。

`check --finalize` 会把当时的 `policy_id`、策略 SHA-256、报告 SHA-256 与证据账本 SHA-256 写入最终判定。已完成报告后续从不可变策略归档加载该版本复验，策略调阈值不会追溯击穿旧报告；正文或证据在判定后变化则必须开启新 revision。
调整策略时必须生成新的 `policy_id` 和归档文件；提交门禁止修改或删除已存在的策略归档。

`status: in_progress` 或 `planned` 的草稿只留在本地工作区。新增报告提交前必须完成两个质量文件，通过独立复核，并用 `check --finalize` 切换为 `completed` 或 `archived`；提交门禁会以 `META009` 阻断未完成草稿。

只登记会影响结论的关键 claim，不把每句话拆成记录。引用摘录保持短小，避免复制大段受版权保护的原文。

## 4. 标准流程

### 初始化

```bash
python3 scripts/report_quality.py init path/to/report.md \
  --tier important \
  --generator-model '<policy.default_generator>' \
  --harness codex
```

命令会升级 frontmatter 并创建空白 evidence/review 文件。生成者在研究过程中填写 evidence 文件；空模板不能通过门禁。

### 独立复核

在新的模型会话中追加 Reviewer 模板：

```bash
python3 scripts/report_quality.py review-template path/to/report.md \
  --reviewer-model '<policy.default_reviewer>' \
  --harness claude-code \
  --role primary_review

python3 scripts/report_quality.py review-prompt path/to/report.md
```

把 `review-prompt` 的输出交给 Reviewer。Reviewer 必须实际读取关键来源，再填写 `.review.json`；生成者自己的同一 run 不能充当独立复核。

Reviewer 的顺序固定为“来源优先”：先在不看报告结论的情况下，从原始材料独立列出核心内容/论证单元，并写入 `source_content_map`；再读报告与 evidence，把每个独立单元映射到 `source_coverage`，标记为 `covered / partial / missing`。只核对报告主动登记的 claim 会产生选择偏差——被生成者完全省略的内容不会出现在 claim 列表中。`standard/deep` 播客若声明有 shownotes 章节，evidence 与 Reviewer 地图必须逐章留痕；核心单元遗漏时记录 `core_requirement_missing`，即使其余 claim 全部准确也不能通过。

播客 Reviewer 还必须运行 `podcast-learning/scripts/audit_transcript.py` 或核对同等机器收据；头尾抽查与重复率不能替代时间戳单调性检查。

### 判定

```bash
python3 scripts/report_quality.py check path/to/report.md --finalize
# 播客等需要归档状态的体裁可加：--final-status archived
```

结果只有四种：

- `pass`：写入判定，并把草稿状态切换为 `completed`，允许归档和提交；
- `needs_review`：证据或复核记录尚未完成；
- `revise`：分数或内容检查未过，生成者按问题清单修订；
- `escalate`：超过常规修订轮次，按机器策略中的升级顺序选择 Reviewer。

修订正文后开启新一轮，旧 Reviewer 记录会进入 `history`，不会与新版分数混算：

```bash
python3 scripts/report_quality.py new-revision path/to/report.md
```

`scripts/audit_reports.py` 会自动调用这套检查。`scripts/ecommit.sh` 在 commit 前检查精确 staged snapshot，GitHub Actions 在 push 与 PR 后复跑仓库级检查，因此不同 Harness 共享相同下限。

## 5. 五维评分

| 维度 | 权重 | Reviewer 核心问题 |
|---|---:|---|
| `evidence_fidelity` | 35 | 来源是否真的支持结论，数字、时间、口径是否准确 |
| `request_coverage` | 20 | 用户明确要求是否全部回答；报告是否覆盖来源的核心内容，而非只覆盖生成者自行登记的要求 |
| `reasoning_quality` | 20 | 推理链、反例、边界和替代解释是否成立 |
| `readability` | 15 | 是否能脱离对话独立阅读，结构是否清楚 |
| `limitations` | 10 | 不确定性、资料缺口和外推边界是否诚实 |

Reviewer 必须为每一维填写评分理由；`unsupported_claims` 和 `missing_requirements` 使用 evidence manifest 中的 ID。多 Reviewer 时按最低总分与最低单项分判定，防止平均分掩盖某个 Reviewer 发现的严重问题。

对于播客学习报告，`request_coverage` 的高分至少要求：Reviewer 的独立来源地图与原材料相符、核心案例和主要反方进入正文、报告可独立阅读。精编稿保存了细节，不能作为报告省略主线的理由。只填写 `coverage_unit_ids_checked` 而没有 `source_content_map`，不能证明执行过来源优先复核。

## 6. 配额策略

1. 默认生成器、常规 Reviewer 和升级顺序由机器策略选择。
2. 第一次未通过时，生成器先按具体问题修订；再次失败才进入升级复核。
3. 稀缺模型只用于策略允许的角色，并受每篇调用上限约束。
4. 禁用模型不能进入新报告链路。
5. 用户明确指定模型时记录 `explicit_model_override: true` 与 `override_reason`，保留真实决策来源。

该策略控制默认资源分配，不阻止用户在具体任务中直接指定模型。
`standard` 是否改为仅确定性审计，要等 `preference_source.review_after_completed_reports` 达到样本量后，根据真实失败率、返工率和成本再决定；样本不足时不提前取消独立复核。

`important` 报告默认仍可由 GLM 5.3 新会话复核，但每累计 5 篇尚未经过强模型跨模型复核的报告，就抽取一篇交给 Sol；Sol 与生成器相同时再使用 Kimi K3。这样估计同模型盲区，同时避免每篇消耗稀缺额度。达到阈值后 context 门禁会阻断提交，直到完成一次符合条件的跨模型复核。查看当前进度：

```bash
python3 scripts/report_quality.py sampling-status --json
```

## 7. 回归评估

跨模型或 Harness 比较使用 `evals/ace-report-tasks.json`，每个组合至少重复三次。记录：

- 硬失败率；
- 五维总分；
- P10（最差 10%）分数；
- 修订与升级率；
- 稀缺模型调用次数；
- token、耗时和工具失败。

接受新配置的条件：关键错误率为 0、P10 不下降，并且质量不退化时成本或耗时有所改善。平均分只作为辅助指标。

`evals/report-quality-replays.json` 固定了五篇真实报告，覆盖不同体裁与三个生成 Harness，其中两篇是重构后的真实生产样本。静态 context 评估会重新运行其 sidecar 与哈希绑定，防止质量门只在临时 fixture 中成立。

Context 重构另用 `scripts/run_ace_context_ab.py` 运行只读开工探针，自动采集初始文件、repo Skill、澄清边界、tokens 与耗时。单领域调整先用 `--case <id>` 定向检查；全部 case × 两套 Context × 三次重复只用于架构里程碑，不作为普通报告提交的同步门禁。完整行为模板仍负责最终完成、质量门与安全结果，二者不能互相替代。

```bash
python3 scripts/eval_report_context.py --template > /tmp/glm-codex-run.json
# 完成真实回放并填写观测值后
python3 scripts/eval_report_context.py --score /tmp/glm-codex-run.json
python3 scripts/eval_report_context.py --aggregate /tmp/*-run.json
```

OpenAI 对 GPT-6 Astra 的建议强调缩短常驻指令、渐进式披露和明确完成条件；官方 eval 指南强调先定义任务，再运行固定输入并分析迭代。本机制把这些原则落实为跨模型共享的证据与评分合同：

- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Working with evals](https://developers.openai.com/api/docs/guides/evals)
