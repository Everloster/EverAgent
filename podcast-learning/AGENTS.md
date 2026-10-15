# podcast-learning — 领域协议

> 播客与视频学习：链接或本地音频 → Razer 静默转写 → 润色 → 总结/讨论 → 报告。
> 联网、Personal Context 与提交规则由根 `AGENTS.md` 负责；本文件只保留本领域路由和硬边界。
> 节目版权归主理人、嘉宾和制作方所有，个人学习使用边界见 [COPYRIGHT.md](./COPYRIGHT.md)。

## 任务路由

### 单期节目或视频

1. 读取 [transcription skill](./skills/transcription/SKILL.md) 执行下载、静默转写和润色。
2. 读取 [report-writing skill](./skills/report-writing/SKILL.md) 选择报告结构与收尾检查；只有需要问答链时再读 [qa_chain](./skills/qa_chain/SKILL.md)。
3. 通过 eacli 从 `knowledge.podcasts` 获取最小 context；需要定位旧报告时查询 `knowledge.index`，避免默认扫描全部报告。命令格式见根 REPORT_WORKFLOW。
4. 新报告遵守根 [REPORT_WORKFLOW](../docs/REPORT_WORKFLOW.md)，并使用 `quality_schema: "report-v1"`。

### “继续讨论”

先定位并读取原报告、对应润色稿和用户追问涉及的原始片段；在原报告追加 `## 追问深入 [日期]`，不另建重复报告。

### “催更 / 刷一下播客”

```bash
python3 scripts/sync_index_status.py
python3 scripts/fetch_show_indexes.py
```

只汇总 stdout 中未标“✅ 已处理”的 `NEW |` 条目；`SUSPECT |` 先人工核对。向用户展示候选并等待选择，不自动转写。

## 静默执行硬边界

- 后台任务禁止 `opencli browser`、interactive browser、系统 URL opener 和任何音视频播放。
- B 站等站点失败时，只能继续尝试无 UI 的官方 API、站点 adapter 或 `yt-dlp`；失败后返回原因。
- 微信入口中的媒体任务使用 `/ea public <任务和链接>`。
- 转写默认通过 `eacli podcast` 在 Razer 执行；本地文件或 worker 不可用时，才使用 `scripts/transcribe.py`。
- 转写原文不改事实；不确定内容保留并标 `[?]`。人名、英文术语和数字用 shownotes 或其他一手材料核验。

## 产物合同

报告、原始转写和润色稿共享可读文件名前缀：

```text
{YYYY-MM-DD}_{platform}-{show_slug}_{guest_or_topic}.md
{YYYY-MM-DD}_{platform}-{show_slug}_{guest_or_topic}.transcript.txt
{YYYY-MM-DD}_{platform}-{show_slug}_{guest_or_topic}.polished.txt
```

具体命名、转写参数、润色规则、v2 报告章节和数字口径均由以下文件拥有：

- [transcription/SKILL.md](./skills/transcription/SKILL.md)
- [report-writing/SKILL.md](./skills/report-writing/SKILL.md)
- [episode_analysis/SKILL.md](./skills/episode_analysis/SKILL.md)

不要把这些细节复制回本文件。

## 完成定义

```bash
python3 podcast-learning/scripts/fill_report_stats.py <报告路径>
python3 podcast-learning/scripts/audit_reports.py <报告路径>
python3 scripts/reindex.py
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

先修当前任务产生的 ERROR。历史 WARN 进入审计报告，不为完成单期任务而批量改旧文件。报告交付后询问一次学习反馈，并只把可复用的新经验以最小 delta 写回对应 skill。
