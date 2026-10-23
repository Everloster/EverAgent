# 有界 Harness 改进实验

> 通用方法与选优原语；真实执行环境、权限、原始轨迹由各自项目拥有。
> 原理论证见 [HarnessPro 学习报告](../ai-learning/reports/paper_analyses/51_harnesspro_2026.md)。

## 用途与入口

用户遇到重复读取、无关 context 和等待问题时，先固定任务、模型、Harness、执行器与验收，再试一个
有界 context delta。[harness_selection.py](../scripts/harness_selection.py) 只消费可信评测器生成的
规范化记录；它不启动 Agent、不评分回答、不改授权或配置、不发布候选。

```bash
python3 scripts/harness_selection.py <可信评测器生成的记录.json>
python3 -m unittest scripts.test_harness_selection -q
```

`candidate-ready` 表示候选已满足输入记录中的证据条件，可以进入指定范围的晋级 review；返回值始终
保留 `production_apply=false`。`no-improvement` 保留 seed，不把缺样本或未知成本当成功。

## 冻结合同

| 字段 | 含义与约束 |
|---|---|
| `search_surface` | 首版仅 `context-only`；不接受跨执行器对照 |
| `required_cases` | 完整冻结用例集；不能删除失败任务 |
| `baseline` / `candidates` | 一个 seed、最多三个候选；精确 context revision |
| `binding` | 同模型、Harness、suite SHA、真实执行配置 SHA；候选 revision 独立 |
| `aggregate` | 现有可信评测器的质量、P10、均衡独立样本、计量完整度；每例每侧至少三次 |
| `comparison` | 原比较器的 `ok` / `acceptance_ready`；新模块不能代替或降低其验收 |
| `evidence` | 原件核验、身份、所有 attempts、独立 Review、holdout、用户路径；关键失败为零 |

执行端要在候选沙箱外核对原件 SHA、真实 session / run ID、stdout / stderr / 退出状态、改动产物和
完整 attempts，再形成输入记录。`evidence` 字段是这次核验的投影；给任意 JSON 写上 `true` 并不构成
真实证明。被测 Agent 不能写入最终评分记录。公开测试全部为独立合成数据，不含私有轨迹。

Train、validation、holdout 按任务家族分离。验证期间只返允许的聚合信息，冻结候选后才检查新家族；
不将同一来源的片段或模板改名分进不同集合。provider prompt cache 单列；结果 cache 不能凑样本。

## 选择与停止

先要求安全违规、关键失败为零，均分与 P10 不降，原行为回归通过；所有样本、未缓存输入、耗时和
晋级范围的真实用户路径完整。缺少 holdout、Review 或原件核验时，候选不进入前沿。

通过后展示质量最大化、完整未缓存输入最小化的 Pareto 前沿，耗时不得退化；不完整成本保持未知。
完全相同的指标优先保留基线；候选间按维护面与稳定 ID 排序。实现不做归一化，常量维度和零成本
不会造成除零。约 10% 是首轮工程目标，独立展示，不冒充原评测器阈值或已实现收益。

无合格新候选、预算耗尽或一代结束即收口。后续问题由真实需求触发，方法本身不授予无限循环、安装、
生产调度、扩大模型额度或公开发布权限。源码重构与运行态发布继续使用各项目已有流程。
