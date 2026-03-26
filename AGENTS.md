# EverAgent — AI Navigation Hub

## ⚡ Startup Protocol（每次新对话必须执行）
**第一步：询问用户模式**（不可跳过，不可假设）
> "你用的是本地离线模型还是在线大模型？"

- **在线模型** → 加载目标项目 `CONTEXT.md`，按需读取具体报告文件
- **离线模型** → 加载目标项目 `knowledge/INDEX.md`，再按需加载对应 `topic.md`

**第二步：确认工作范围**
> 询问用户要在哪个项目工作，加载对应 `CONTEXT.md`，之后不再跨项目加载任何文件

## 📁 项目索引
| 项目 | CONTEXT 入口 | 领域 |
|------|-------------|------|
| ai-learning | [CONTEXT.md](./ai-learning/CONTEXT.md) | AI/ML 论文精读·技术报告 |
| cs-learning | [CONTEXT.md](./cs-learning/CONTEXT.md) | 计算机科学·系统·算法 |
| philosophy-learning | [CONTEXT.md](./philosophy-learning/CONTEXT.md) | 西方哲学史·文本分析 |
| psychology-learning | [CONTEXT.md](./psychology-learning/CONTEXT.md) | 心理学·经典实验 |
| biology-learning | [CONTEXT.md](./biology-learning/CONTEXT.md) | 时间生物学·睡眠·运动生理 |
| github-trending-analyzer | [CONTEXT.md](./github-trending-analyzer/CONTEXT.md) | 开源热点分析工具·Repo 知识库 |

## 🚨 铁律
1. **每次只加载一个项目的 CONTEXT.md**，禁止跨项目并发加载，除非是对整体项目空间进行重构修改，目前只允许claude和chatgpt模型在整个项目空间工作。
2. 本文件（AGENTS.md）是唯一全局入口，README.md 供人类阅读，AI 忽略
3. 不确定去哪时：查上方表格 → 加载对应 CONTEXT.md → 按其指引操作
4. **防幻觉规则**：未加载的文件内容禁止推测或虚构；CONTEXT.md 中未列出的报告，须明确告知用户"该内容尚未研究"，不得用模型自身训练数据填充
