# EverAgent Context Engineering

> 目标：让项目 context 随模型和 Harness 演进，同时保留可追溯、可评估、可回滚的治理方式。

## 分层

| 层 | Owner | 放什么 | 避免什么 |
|---|---|---|---|
| 常驻项目层 | `AGENTS.md` | 安全不变量、意图路由、权限边界、关键入口 | 教程、历史备忘、模型临时补丁 |
| 任务发现层 | skill name + description | 窄而清楚的触发条件 | 完整功能清单、宽泛“只要相关就用” |
| 工作流层 | `SKILL.md` | 决策流程、输入输出、必要约束 | 复制所有参考资料 |
| 专项知识层 | references / `METHODOLOGY.md` / 领域文档 | 仅本任务需要的详细方法和 schema | 默认全部加载 |
| 确定性层 | scripts / hooks / CI | 能机械判断的格式、安全与一致性规则 | 依赖模型记住重复口令 |
| 单次任务层 | 用户 prompt | 目标、交付物、授权、完成与停止条件 | 永久化一次性偏好 |

这个结构同时吸收两类看似相反的证据：

- OpenAI 对 GPT-6 Astra 的建议强调缩短发现层和常驻层，减少冲突与无关上下文；
- ACE（Agentic Context Engineering）强调保留详细领域经验，避免反复整篇压缩造成 brevity bias 与 context collapse。

二者可以同时成立：**入口保持小，知识保持全，细节按需加载，更新使用局部 delta。**

## 指令生命周期

新增或修改一条长期规则时记录四件事：

1. **触发条件**：什么任务需要它；
2. **证据**：哪次失败、用户偏好或安全要求支持它；
3. **Owner**：应属于根协议、领域协议、skill、reference 还是脚本；
4. **复核条件**：模型升级、工具替换或连续任务无再现时，何时重新评估。

只出现一次且风险低的问题留在任务报告或 commit 中。跨任务重复出现，或一次出现就造成严重风险的问题，才进入长期 context。

## ACE 增量循环

```text
执行任务（Generator）
  → 基于产物和门禁识别具体成功/失败（Reflector）
  → 形成一条最小、带作用域的 delta（Curator）
  → 用历史任务回放验证
  → 保留、修正或撤销
```

Curator 不重写整份 context。完整重写容易丢失例外、证据来源和仍有效的旧规则。

## 模型与 Harness 适配

- 仓库中的长期规则默认保持模型无关。
- 模型特有倾向优先由运行时提示或小型 overlay 调节。
- 升级模型时重点回放：自主推进、澄清、工具选择、测试范围、子任务委派和停止时机。
- 新模型已经稳定具备的通用能力，不继续用仓库规则逐步教一遍。
- Harness 能确定性保证的规则迁到代码；文本只保留调用条件和失败含义。
- 报告模型角色、额度偏好和升级顺序由 [`config/report-quality-policy.json`](../config/report-quality-policy.json) 统一维护，具体流程见 [REPORT_QUALITY_GATE.md](./REPORT_QUALITY_GATE.md)。

## 发现面与 Owner

- 自动发现面只放 `.agents/skills/`；当前保持一个报告路由 skill，避免所有领域模板同时进入发现预算。
- 各项目 `skills/` 是由领域 `AGENTS.md` 条件链接的按需 playbook。入口只保留模式选择与不变量，模板、故障历史和长示例放进 `references/`。
- `CLAUDE.md` 只负责导入 `AGENTS.md` 和真正的 Claude 专属 overlay，不复制公共文档目录。
- 公共规则的唯一 Owner、字节预算和禁止复制片段由 [`config/instruction-policy.json`](../config/instruction-policy.json) 维护，并由 context eval 阻断漂移。

## 预算与指标

- Codex 官方 `AGENTS.md` 合并上限默认 32 KiB；超过上限会停止继续加入文件。
- Skill 初始发现清单默认最多占上下文窗口 2%；窗口未知时为 8,000 characters。
- 静态预算只用于发现风险。最终判断依赖真实任务的成功率、无效读取、澄清次数、工具调用、compaction、返工和安全结果。
- 行为回放同时记录 skill precision / recall、无关 context 读取率、澄清率和提前停止率；均值之外必须查看 P10 与零分率。

运行：

```bash
python3 scripts/eval_report_context.py
python3 scripts/eval_report_context.py --json
python3 scripts/eval_report_context.py --template > /tmp/ace-run.json
python3 scripts/eval_report_context.py --score /tmp/ace-run.json
python3 scripts/eval_report_context.py --aggregate /tmp/*-run.json
```

## 参考

- [OpenAI：Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [OpenAI：Using GPT-6 — Prompting best practices](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md#prompting-best-practices)
- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills)
- [OpenAI：Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Zhang et al.：Agentic Context Engineering](https://arxiv.org/abs/2510.04618)
- [HumanLayer：Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)
