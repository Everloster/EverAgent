# EverAgent 报告系统 Review：面向常用 ACE 任务的 Context 与质量门改造

> 日期：2026-10-15
> 范围：公开仓全部报告资产、报告生成协议、skills、索引与质量检查。
> ACE：本文指 Agentic Context Engineering，也覆盖本仓常见的“研究 / 反思 / 策展”型 Agent 任务。

## 结论摘要

本次对 **452 篇正式报告、约 7.25 MB 文本**做了全量静态扫描，并从九个产出域抽取 **34 篇**进行结构与内容抽样 review。项目已经拥有较强的研究方法论，但报告生产机制此前存在五个系统问题：

1. 常驻 context 重复且过大，Podcast 路径的两层 `AGENTS.md` 达 **33,657 bytes**，超过 Codex 官方默认 32 KiB 合并上限。
2. 质量检查分裂：Podcast 有严格门禁，其他领域主要依赖非阻塞的 `lint_evidence.py`，GitHub 协议甚至明确写着“不靠脚本校验”。
3. 全局报告索引只收录 328 个 Markdown 文件，其中混入 10 个 shownotes，又漏掉 124 篇 GitHub 深研和 10 篇 AI 实验笔记。
4. 历史元数据不统一：155 篇无 frontmatter，279 篇无 semantic tags，12 篇使用非规范 status。
5. 缺少 context 的行为回放：无法回答规则精简后，路由、早停、误触发、无效读取和安全表现是否真的改善。

本次已完成机制改造：建立统一报告目录、全仓审计器、报告专用 repo skill、分层 context 文档和 13 个 ACE 回放任务；精简所有高频 `AGENTS.md`；修复全局索引覆盖、一个真实断链和一个缺失状态字段；把 GitHub 报告模板与生成器升级到当前元数据合同。

静态 context 指标从 **66,775 bytes 降到 16,311 bytes（−75.6%）**。最重的 Podcast 路径占默认预算的 **24.3%**，所有任务路径均低于 25%，重复长段落归零。

---

## 1. Review 方法

### 1.1 全量静态扫描

扫描以下正式产物：

| 领域 | 报告数 | 中位大小 | P90 大小 |
|---|---:|---:|---:|
| AI Learning | 113 | 16,462 B | 27,800 B |
| CS Learning | 33 | 13,846 B | 24,987 B |
| Philosophy Learning | 22 | 16,984 B | 51,836 B |
| Psychology Learning | 17 | 14,999 B | 24,459 B |
| Biology Learning | 18 | 16,009 B | 31,009 B |
| AI Practice | 10 | 9,809 B | 17,652 B |
| Podcast Learning | 73 | 13,996 B | 27,555 B |
| GitHub Research | 124 | 10,136 B | 17,466 B |
| Web Surfing | 42 | 23,798 B | 44,455 B |
| **合计** | **452** | — | — |

`podcast-learning/reports/transcripts/` 下 10 个 shownotes Markdown 被认定为来源产物，不计入报告数。

### 1.2 分层 review

- **结构全扫**：frontmatter、标题、状态、日期、tags、证据锚点、思考与追问、占位符、相对链接。
- **34 篇分层抽样**：每个领域取最新、最旧、最短、最长报告，检查模板、证据表达、重复内容与读者入口。
- **机制 review**：根与九个项目 `AGENTS.md`、22 个领域 playbook、`METHODOLOGY.md`、元数据规范、索引器和现有质量脚本。
- **外部方法对照**：[GPT-6 Astra 指令文章](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)、[OpenAI Skills 文档](https://learn.chatgpt.com/docs/build-skills)、[OpenAI AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[ACE 论文](https://arxiv.org/abs/2510.04618)和 [HumanLayer ACE 工作流](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)。

静态规则无法判断一篇报告的思想价值，也会把合理的“待验证”或示例误判成风险。全量扫描共记录 755 条相互重叠的 WARN；下列数字是维护线索，不是质量排名，也不能相加后当成问题报告数。

---

## 2. 全库发现

### 2.1 结构债务集中在历史报告

| 信号 | 文件数 / 告警数 | 解读 |
|---|---:|---|
| 无 frontmatter | 155 | 主要是 GitHub 旧报告 115 篇和 Web 旧报告 39 篇 |
| frontmatter 缺必填字段 | 22 | 主要来自早期 AI Practice 笔记；同一文件可能贡献多条告警 |
| 无 semantic tags | 279 | 元数据 Phase 2 在旧报告中尚未回填 |
| A 类学习报告无“思考与追问” | 159 | 大多产于该规范建立之前 |
| 无可识别证据锚点 | 72 | 需人工区分“真无来源”与书目/本地材料格式未被识别 |
| 提到 2024 年后事件但无 URL/arXiv/DOI/RFC | 33 | 启发式风险信号，需要人工核验引用是否以其他格式存在 |
| completed 文档含模板占位符 | 12 | 部分是真正残留，部分是代码或示例中的 TODO |
| 非规范 status | 12 | `complete`、`done` 等历史写法 |
| 缺 H1 | 1 | AI Practice 旧实验笔记 |
| 重复标题 | 10 | GitHub 日/周/月榜使用通用标题，索引需依日期区分 |

这些结果说明全库需要“历史兼容 + 新增严格”的分期门禁。把 452 篇一次性改成新模板会制造巨大 diff，也无法提高事实正确性。本次因此没有批量重写旧报告；新报告执行 `quality_schema: report-v2`，`report-v1` 保留为过渡格式，旧报告保持可读并进入 WARN 队列。

### 2.2 各领域的真实强弱项

#### A 类学习报告

- 113 篇 AI 报告全部已有基本 frontmatter；CS、哲学、心理学、生物学也保持了结构一致性。
- 2026 年 9–10 月的新报告明显强化了一手来源、限制和问题闭环。
- 早期报告常有完整章节，却缺少可点击来源和“思考与追问”；长度不能替代证据。
- 多领域 `AGENTS.md` 重复同一六步流程，导致每个任务常驻加载相同文字。

#### Podcast

- 是当前机制最成熟的领域：73 篇正式报告，领域审计结果为 **ERROR 0 / WARN 0**。
- 三件套、压缩比、章节、时长、wikilink 和数字表已有确定性检查。
- 原 `AGENTS.md` 达 16,808 bytes，与根文件叠加后超过默认 32 KiB；大量细节已经存在于 transcription/report-writing skills，属于重复加载。

#### GitHub Research

- 124 篇报告多数具有 `[代码]`、`[API]`、`[README]`、`[Web]` 证据标签，技术取证习惯较强。
- 115 篇没有 frontmatter，导致全局索引、日期与类型只能猜测。
- 原协议明确拒绝报告脚本门禁，和其他领域治理方式不一致。
- `assets/report_template.md` 仍是英文占位模板，与现行七章中文报告不一致。
- 2026-06 月报保留了 13 个并不存在的深研链接；本次已把缺失项改为纯文本，并修正两个已有报告的错误相对路径。

#### Web Surfing

- 42 篇报告中 40 篇能识别到来源，证据密度整体较高。
- 39 篇无 frontmatter，日报依赖文件名和 mtime 建索引。
- 报告较长：中位 23,798 bytes，P90 44,455 bytes。AI 日报已另有可读性 skill，但通用报告缺少统一完成合同。

#### AI Practice

- 10 篇正式实验笔记散布在 `experiments/`，旧索引逻辑实际上没有收录。
- 模板使用 `type` 与 `status: done`，和全局 `report_type` / `completed` 规范漂移。
- 实验强调真实运行，这是正确的领域硬约束；本次保留并接入统一门禁。

### 2.3 最关键的机制问题

1. **同一事实有多个 owner。** Token Plan、报告收尾和提交命令在根与领域文件重复，更新时容易漂移。
2. **高频入口承担了低频细节。** Podcast 参数、GitHub API 命令和历史备忘长期占据 `AGENTS.md`。
3. **规则只增不减。** GitHub 与 Podcast 都曾要求每次任务更新 skill，容易把一次性异常固化成永久规则。
4. **质量规则主要靠文字提醒。** 除 Podcast 外，缺少对新报告的确定性合同。
5. **索引与资产边界不一致。** source artifact 被当报告，真正的 GitHub/实验报告却未进入全局入口。
6. **只有产物 lint，没有 context eval。** 无法检测常驻字节数、重复段落、无条件读取和 skill 路由回归。

---

## 3. OpenAI 与 ACE 的合并解释

OpenAI 建议缩短 skill 描述和常驻 `AGENTS.md`；ACE 论文提醒不要把长期经验压缩成空泛短句，并报告了 brevity bias 与 context collapse。两者关注的是不同层：

| 层 | 应采用的策略 |
|---|---|
| Skill 发现层 | 短、具体、可区分，降低误触发和截断 |
| 常驻项目层 | 稳定不变量与条件路由，减少无关内容 |
| 被选中的工作流 | 保留足够详细的领域 playbook |
| 历史经验更新 | 使用局部 delta，避免整篇重写丢信息 |
| 硬规则 | 用脚本、hook、CI 执行 |

这次改造采用的原则是：**入口小、知识全、按需读、增量改、结果可测。**

---

## 4. 已落地改造

### 4.1 Context 架构

- 根 `AGENTS.md` 从 16,849 bytes 减至 6,539 bytes，其中仓库自有内容 4,224 bytes；公共文档改成条件路由，不再复制报告命令。
- Podcast `AGENTS.md` 从 16,808 bytes 减至 1,414 bytes；详细转写、润色与报告规则由 playbook 和 references 持有。
- GitHub `AGENTS.md` 从 9,598 bytes 减至 1,218 bytes；只保留轻量介绍、深研和 trending 的分流及代码证据边界。
- Web `AGENTS.md` 从 6,681 bytes 减至 1,184 bytes；只保留站点路由和访问边界。
- 五个 A 类领域和 AI Practice 改为按需读取 PROFILE、MAP、open-questions 和单一体裁 skill。
- 新增 [CONTEXT_ENGINEERING.md](./CONTEXT_ENGINEERING.md)，明确 context owner、ACE delta 更新和模型专属 overlay 边界。

### 4.2 报告生产

- 新增 [REPORT_WORKFLOW.md](./REPORT_WORKFLOW.md)，统一“是否落报告”、最小 context、Generator–Reflector–Curator 循环、报告合同和完成定义。
- 新增 `.agents/skills/everagent-report/`，description 仅承担明确报告请求的路由，并排除短问答与只贴 repo 链接。
- 新报告使用 `quality_schema: report-v2`，并选择 `standard / important / flagship`；历史报告不被强制批量迁移。
- GitHub 报告生成器和模板已输出当前 frontmatter；AI Practice 与 Podcast 模板同步字段。
- “每次任务都扩写 skill”改成“每次反思，只有可复用或高风险发现才写入最小 delta”。

### 4.3 全库目录与质量门

- 新增 `scripts/report_catalog.py`，统一定义九个报告集合。
- `scripts/reindex.py` 改用统一目录：纳入 GitHub 124 篇和 AI Practice 10 篇，排除 Podcast shownotes。
- `scripts/reindex.py --check` 现在真正比较生成结果并在索引漂移时返回失败。
- 新增 `scripts/audit_reports.py`：全量扫描历史债务，对新增报告和版本化报告执行严格合同；中文路径与已暂存的新文件也能被 `--changed` 正确识别。
- 新增 `scripts/report_quality.py` 与 `report-v2`：完成态报告必须具备关键 claim 证据账本、独立 Reviewer 记录、五维评分和通过判定。
- `scripts/ecommit.sh` 在提交前对 Git index 的精确快照运行报告审计、索引一致性和 context 评估，防止工作区未暂存文件掩盖提交内容。
- 修复一处 Podcast 版权链接、一处 Podcast status 缺失，以及 GitHub 月报中的缺失报告链接；生成器也会把缺失报告写成纯文本，避免回归。

### 4.4 评估

- 新增 `scripts/eval_report_context.py`，检查 10 个 `AGENTS.md` 的路径字节预算，并扫描 58 个受治理 context 文件的重复、无条件读取、内部链接、过时指令和 skill 元数据。
- `evals/ace-report-tasks.json` 扩展为 13 个任务，加入简短问答、微小修改和“先准备、最终发布前停下”的决策边界样本。
- 行为评分新增 skill precision / recall、无关 context 读取率、澄清率和提前停止率。
- 新增用户认可的报告质量锚点，并支持按模型、Harness 和 context revision 聚合平均分、P10、零分率、升级率与稀缺模型调用量。
- 支持生成行为记录模板和评分；安全结果必须显式记录为通过，否则该 case 计 0 分：

```bash
python3 scripts/eval_report_context.py --template > /tmp/ace-run.json
# 用固定模型与 Harness 完成任务并填写观察值
python3 scripts/eval_report_context.py --score /tmp/ace-run.json
```

---

## 5. Context 改造前后

| 路径 | 改造前 | 改造后 | 变化 |
|---|---:|---:|---:|
| 全部项目 `AGENTS.md` | 66,775 B | 16,311 B | **−75.6%** |
| 根 | 16,849 B | 6,539 B | −61.2% |
| AI Learning 链 | 21,482 B / 65.6% | 7,901 B / 24.1% | −63.2% |
| Podcast 链 | 33,657 B / 102.7% | 7,953 B / 24.3% | −76.4% |
| GitHub 链 | 26,447 B / 80.7% | 7,757 B / 23.7% | −70.7% |
| 跨文件重复长段落 | 2 组 | 0 组 | 清零 |

百分比以 OpenAI 文档给出的默认 32 KiB `AGENTS.md` 合并上限为分母。该指标只衡量静态输入压力，不代表最终任务质量。

---

## 6. 新的完成与回归策略

### 每次报告任务

1. 只加载当前任务需要的领域和体裁资料；
2. 生成报告并完成一次基于事实的反思；
3. 只提交可复用 context delta；
4. 重建索引；
5. 对 changed report 运行严格门禁；
6. 验证索引没有漂移。

### 每次 context、skill 或 Harness 变更

1. 运行静态 context 评估；
2. 用 ACE 任务集做同模型、同工具、同推理档位的 A/B 回放；
3. 比较路由、上下文读取、无必要提问、完成率、报告门禁和安全结果；
4. 只有质量不退化时，才接受 token、调用量或耗时改善。

### 历史债务

历史报告只在以下情形升级到 `report-v2`：用户继续该主题、报告被新报告直接引用、关键事实被发现错误、或批次修复能由确定性工具安全完成。其余 WARN 保留为可见债务，避免为了整齐而重写数百篇内容。

---

## 7. 尚未自动化的边界

- 静态脚本不能判断一篇报告是否真正解释清楚，也不能验证引用是否支持具体句子。
- 行为回放仍需要实际模型运行并记录工具、文件读取和停止行为；仓库只提供任务集、记录格式和评分器。
- 旧报告的事实更新、引用补齐和推理质量需要按阅读价值逐篇复核。
- 不同模型与 Harness 的最优 context 可能不同，当前结构允许 overlay，但尚未积累跨模型对照数据。

这套机制的目标是让问题可见、让新增债务停止增长，并让后续改动能通过同一批真实任务验证。

---

## 8. 多模型质量下限补强

用户确认的运行偏好是：GLM 5.3 作为额度充足的主力模型；Kimi K3 能力较好但额度有限，优先保留给升级复核；MiniMax M3 不再用于新报告。该偏好已进入机器可读的 `config/report-quality-policy.json`，而不是散落进多个 Harness prompt。

第二阶段引入 `report-v2`：每篇新报告必须同时拥有 evidence manifest 与独立 review 记录。`scripts/report_quality.py` 负责初始化、生成 Reviewer prompt、验证关键 claim 与来源覆盖、计算五维最低分，并在失败时返回 `revise` 或 `escalate`。旗舰报告需要两次独立复核，其中至少一次来自强模型。

默认资源路径为：GLM 5.3 生成 → GLM 5.3 新会话复核 → 首轮修订 → GPT-5.6 Sol 升级复核 → 无法使用时才调用 Kimi K3。Kimi K3 默认每篇最多一次，用户明确指定时可覆盖；MiniMax M3 会被质量门直接拒绝。

提交入口 `scripts/ecommit.sh` 会运行已暂存报告审计、索引一致性和 context 评估。跨模型回放新增质量判定与 P10 聚合，避免平均分掩盖最差报告。完整协议见 [REPORT_QUALITY_GATE.md](./REPORT_QUALITY_GATE.md)。

---

## 9. 按 GPT-6 Astra 原文进行的第二轮重构

第二轮重新读取 OpenAI 原文与 GPT-6 官方 prompting guidance，不再把“压缩字节数”当作唯一目标，而是逐项落实其控制边界：

1. **常驻层只保留控制面。** 九个领域 `AGENTS.md` 删除重复 frontmatter、质量命令和公共收尾流程，总大小从 20,899 bytes 降到 9,772 bytes。`CLAUDE.md` 从 1,295 bytes 缩为 239 bytes，只保留 `@AGENTS.md` bridge。
2. **Skill 发现层只做分类。** 自动发现面维持一个 `everagent-report`，description 从 219 缩为 150 characters，入口从 2,187 缩为 1,310 bytes；简短问答、简单查询和裸 repo 链接均写入非触发边界。
3. **领域 playbook 渐进披露。** 22 个按需 playbook 的入口合计从 150,393 bytes 降到 34,192 bytes（−77.3%），最大入口从 11,678 bytes 降到 5,919 bytes；详细模板、快速索引和历史故障保存在 17 个 `references/` 文件中，由任务分支按需读取。`METHODOLOGY.md` 也从 7,774 bytes 降到 5,578 bytes，把固定七步模板改成按证据类型选择分析维度。
4. **任务 prompt 以边界为中心。** 根协议明确目标、交付物、验收信号和停止条件；本地可逆工作持续推进，只有实质歧义或未授权外部动作才暂停；验证先覆盖受影响范围，避免小改动触发全套测试。
5. **原则进入确定性门禁。** `config/instruction-policy.json` 记录 Owner、常驻字节预算、自动发现 skill 预算和禁止复制片段；pre-commit 已有的 context eval 会阻断再次膨胀。
6. **评估覆盖正负样本。** ACE 回放不仅测报告质量，还测不该触发报告 skill 的一句话问答、裸 repo 链接和 typo 修复，以及应在发布前停止的授权边界。

这轮保留了完整领域知识，没有把长 playbook 删除；变化只发生在何时加载、由谁拥有以及怎样验证。它直接对应原文的三项核心建议：description 可区分、`SKILL.md` 渐进披露、`AGENTS.md` 按任务读取，并补上官方 prompting guidance 对持续完成、决策边界和测试范围的要求。
