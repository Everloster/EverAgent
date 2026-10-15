# podcast-learning — 领域协议

> 播客与视频学习。版权边界见 [COPYRIGHT.md](./COPYRIGHT.md)。

## 路由

| 意图 | 按需读取 |
|---|---|
| 新节目：下载、转写、润色 | [transcription](./skills/transcription/SKILL.md) |
| 写学习报告 | [report-writing](./skills/report-writing/SKILL.md)，再按体裁读取 [episode_analysis](./skills/episode_analysis/SKILL.md) 或 [qa_chain](./skills/qa_chain/SKILL.md) |
| 继续讨论 | 原报告、对应润色稿和追问涉及的原始片段 |
| 催更或刷新节目 | `scripts/sync_index_status.py` 与 `scripts/fetch_show_indexes.py` |

长期报告同时使用根级 [`everagent-report`](../.agents/skills/everagent-report/SKILL.md)。通过 eacli `knowledge.podcasts` 定位已有内容；仅在需要跨域检索时查询 `knowledge.index`。

## 静默执行边界

- 后台任务不得打开浏览器 UI、系统 URL opener 或任何音视频播放器。
- 站点获取失败时只尝试无 UI 的官方 API、typed capability、adapter 或下载器；仍失败则返回原因。
- 转写默认交给 eacli podcast 的 Razer worker；本地文件或隔离排障才走本地脚本。
- 转写不改事实；不确定内容标 `[?]`，人名、术语和数字用 shownotes、字幕或其他一手材料核验。

命名、参数、润色、章节、统计和领域检查由上述 skills 与脚本拥有，不复制到本文件。
