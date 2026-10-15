# EverAgent 报告质量下限

> 目标：让 Pi、Claude Code、Codex 等不同 Harness，以及不同模型生成的报告，都经过同一套可观察、可阻断、可升级的质量流程。
> 机器可读策略由 [`config/report-quality-policy.json`](../config/report-quality-policy.json) 唯一维护。
> “质量下限”表示未完成证据登记和独立复核的报告不能进入完成状态；它不能数学保证每个判断都真实，因此仍需来源核验与定期人工校准。

## 1. 模型角色

| 角色 | 默认选择 | 使用原则 |
|---|---|---|
| 主生成器 | GLM 5.3 | 额度充足，承担资料整理、初稿和第一次修订 |
| 常规 Reviewer | GLM 5.3 的独立新会话 | 不读取生成过程，只看任务、报告、证据账本和原始来源 |
| 强模型升级 | GPT-5.6 Sol → Kimi K3 | 常规复核失败、旗舰报告或高风险事实需要时使用 |
| 稀缺资源 | Kimi K3 | 默认只用于升级复核或旗舰终审，每篇最多一次；用户明确指定时可覆盖 |
| 禁用 | MiniMax M3 | 不进入任何新报告的生成、修订或复核链路 |

Harness 与模型分别记录。`pi`、`claude-code`、`codex` 是运行环境，不作为模型质量的替代指标。

## 2. 三档质量等级

| 等级 | 适用 | 默认复核 |
|---|---|---|
| `standard` | 日报、常规清单、实验记录 | GLM 5.3 独立复核一次，总分 ≥82 |
| `important` | 文章/论文精读、概念深挖、repo 深研、播客学习报告 | GLM 5.3 独立复核一次，总分 ≥88；失败后升级 |
| `flagship` | 长期基准报告、公开发布、关键决策材料 | 两次独立复核，其中至少一次使用强模型，总分 ≥92 |

证据一致性使用更高的单项门槛。只要出现伪造引用、关键数字无法追溯、漏答核心要求或安全问题，综合分再高也不能通过。

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

- `evidence.json`：任务要求、生成模型与 Harness、来源、关键 claim、报告锚点和局限。
- `review.json`：独立 Reviewer、已核验的要求/claim/来源、五维评分及未解决问题。
- JSON schema：[report-evidence-v1](../schemas/report-evidence-v1.schema.json)、[report-review-v1](../schemas/report-review-v1.schema.json)。

`status: in_progress` 或 `planned` 的草稿只留在本地工作区。新增报告提交前必须完成两个质量文件，通过独立复核，并用 `check --finalize` 切换为 `completed` 或 `archived`；提交门禁会以 `META009` 阻断未完成草稿。

只登记会影响结论的关键 claim，不把每句话拆成记录。引用摘录保持短小，避免复制大段受版权保护的原文。

## 4. 标准流程

### 初始化

```bash
python3 scripts/report_quality.py init path/to/report.md \
  --tier important \
  --generator-model glm-5.3 \
  --harness codex
```

命令会升级 frontmatter 并创建空白 evidence/review 文件。生成者在研究过程中填写 evidence 文件；空模板不能通过门禁。

### 独立复核

在新的模型会话中追加 Reviewer 模板：

```bash
python3 scripts/report_quality.py review-template path/to/report.md \
  --reviewer-model glm-5.3 \
  --harness claude-code \
  --role primary_review

python3 scripts/report_quality.py review-prompt path/to/report.md
```

把 `review-prompt` 的输出交给 Reviewer。Reviewer 必须实际读取关键来源，再填写 `.review.json`；生成者自己的同一 run 不能充当独立复核。

### 判定

```bash
python3 scripts/report_quality.py check path/to/report.md --finalize
# 播客等需要归档状态的体裁可加：--final-status archived
```

结果只有四种：

- `pass`：写入判定，并把草稿状态切换为 `completed`，允许归档和提交；
- `needs_review`：证据或复核记录尚未完成；
- `revise`：分数或内容检查未过，生成者按问题清单修订；
- `escalate`：超过常规修订轮次，按策略交给 GPT-5.6 Sol，无法使用时再调用 Kimi K3。

修订正文后开启新一轮，旧 Reviewer 记录会进入 `history`，不会与新版分数混算：

```bash
python3 scripts/report_quality.py new-revision path/to/report.md
```

`scripts/audit_reports.py` 会自动调用这套检查。`scripts/ecommit.sh` 在 commit 前检查已暂存报告、索引与 context，因此不同 Harness 共享相同下限。

## 5. 五维评分

| 维度 | 权重 | Reviewer 核心问题 |
|---|---:|---|
| `evidence_fidelity` | 35 | 来源是否真的支持结论，数字、时间、口径是否准确 |
| `request_coverage` | 20 | 用户明确要求是否全部回答 |
| `reasoning_quality` | 20 | 推理链、反例、边界和替代解释是否成立 |
| `readability` | 15 | 是否能脱离对话独立阅读，结构是否清楚 |
| `limitations` | 10 | 不确定性、资料缺口和外推边界是否诚实 |

Reviewer 必须为每一维填写评分理由；`unsupported_claims` 和 `missing_requirements` 使用 evidence manifest 中的 ID。多 Reviewer 时按最低总分与最低单项分判定，防止平均分掩盖某个 Reviewer 发现的严重问题。

## 6. 配额策略

1. GLM 5.3 完成默认生成和常规独立复核。
2. 第一次未通过时，先让 GLM 5.3 按具体问题修订。
3. 修订后仍未通过，推荐 GPT-5.6 Sol 复核；不可用时调用 Kimi K3。
4. Kimi K3 默认每篇最多一次，只做升级复核或旗舰终审。
5. 用户明确指定模型时记录 `explicit_model_override: true` 与 `override_reason`，保留真实决策来源。

该策略控制默认资源分配，不阻止用户在具体任务中直接指定模型。

## 7. 回归评估

跨模型或 Harness 比较使用 `evals/ace-report-tasks.json`，每个组合至少重复三次。记录：

- 硬失败率；
- 五维总分；
- P10（最差 10%）分数；
- 修订与升级率；
- Kimi K3 调用次数；
- token、耗时和工具失败。

接受新配置的条件：关键错误率为 0、P10 不下降，并且质量不退化时成本或耗时有所改善。平均分只作为辅助指标。

```bash
python3 scripts/eval_report_context.py --template > /tmp/glm-codex-run.json
# 完成真实回放并填写观测值后
python3 scripts/eval_report_context.py --score /tmp/glm-codex-run.json
python3 scripts/eval_report_context.py --aggregate /tmp/*-run.json
```

OpenAI 对 GPT-6 Astra 的建议强调缩短常驻指令、渐进式披露和明确完成条件；官方 eval 指南强调先定义任务，再运行固定输入并分析迭代。本机制把这些原则落实为跨模型共享的证据与评分合同：

- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Working with evals](https://developers.openai.com/api/docs/guides/evals)
