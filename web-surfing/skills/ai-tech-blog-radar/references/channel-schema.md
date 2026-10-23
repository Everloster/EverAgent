# 渠道注册表与采集契约

只有修改渠道结构、适配器或过滤逻辑时读取本文件。

## 注册表

事实源：`web-surfing/sources/ai-tech-blogs.json`。

每个 source 的稳定字段：

| 字段 | 含义 |
|---|---|
| `id` | 小写连字符 ID，CLI 主键 |
| `name` / `vendor` | 展示名与机构 |
| `tier` | `must` 或 `watch` |
| `source_class` | `lab/vendor/project/engineering/platform/release`；默认 `vendor` |
| `enabled` | 是否参与默认更新查询 |
| `homepage` | 人工访问入口 |
| `discovery.kind` | `rss`、`search` 或 `sitemap` |
| `discovery.url/query` | 对应的 feed、sitemap 或官方域名查询 |
| `discovery_fallbacks` | 主通道失败时的备用发现通道；`discovery_mode=merge` 时与主通道合并 |
| `discovery_mode` | `fallback`（默认）或 `merge` |
| `allow_domains` | 结果域名白名单 |
| `path_prefixes` | URL 路径白名单 |
| `exclude_path_prefixes` | 搜索页、作者页等 URL 路径排除项 |
| `include_any` | 至少命中一个才保留；空数组表示不加此门 |
| `exclude_any` | 来源专属噪声词 |
| `title_include_any/title_exclude_any` | 只针对标题的精确收录与排除规则 |
| `hydrate_search_results` | 搜索结果缺日期时是否回读官方正文核验发布日期 |
| `hydrate_limit` | 单个搜索通道最多回读 1–20 个页面，默认 5 |
| `require_topic_lane` | 广谱研究源是否必须命中至少一个 AI 技术主题，避免数学、经济等非 AI 内容混入 |
| `topics` | 来源擅长的主题，仅作来源画像；取值为 `agent_harness/eval_safety/inference_systems/training_models/kernels_hardware/science_multimodal` |
| `publisher_path_index` / `publisher_path_min_segments` | 从平台文章 URL 提取原始发布机构，例如 Hugging Face 的 `/blog/microsoft/...` |
| `preferred_publishers` | 平台源中可信实验室或项目作者；命中后加权并写入入选理由 |
| `why` | 收录理由 |

`global_exclude_any` 只放稳定的公司新闻噪声词。不要把具体模型名或一次性事件写成全局规则。

## 采集

- `rss`：eacli `web.read` → 必要时只读 HTTP XML fallback。
- `search`：eacli `web.search`，查询自动附带 `after:YYYY-MM-DD`，随后再按解析到的发布日期过滤。搜索引擎时间窗不能替代发布日期；指定来源可回读正文补日期。
- `sitemap`：eacli `web.read` → 必要时只读 HTTP XML fallback；`lastmod` 写入 `updated_at`，不写入 `published_at`。
- `fallback`：主通道发生访问或解析错误时才切换备用通道；主通道正常返回零篇表示时间窗内无更新，不触发备用。
- `merge`：执行所有登记通道并按规范 URL 合并，适合无稳定列表、需要多组官方域名搜索的来源。

HTTP XML fallback 使用短连接与 identity 编码，连接重置时只重试一次；若响应以 gzip magic 开头则显式解压，处理 DeepMind 等未稳定声明 `Content-Encoding` 的 feed。

所有结果再经过域名、路径、标题过滤词、来源过滤词、全局噪声词和两阶段去重：先规范 URL，再用规范化标题合并跨站转载，并保留 `alternate_sources`。Qwen 等使用 `?id=` 区分文章的站点会保留业务 query，只删除 `utm_*` 等追踪参数。

## 输出

`updates --format json` 是 Agent 消费面，包含：

- 查询时间窗和成功来源数；
- `deep_read_candidate`、`release_signal`、`technical_update`；
- 每条的来源、URL、日期、摘要和入选理由；
- failures、Token Plan 选择证据和 XML fallback 记录。
- `source_stats`：每源原始条数、筛选后条数、实际发现通道和代表文章。
- `sources_degraded`：主发现通道失败、由备用通道接管的来源数；降级成功不能描述成全量正常。

`channels evaluate --days 14` 输出渠道评分卡，用于新增来源验收与 must/watch 升降级。筛选率只反映过滤强度，不直接代表质量；仍需阅读代表文章。

脚本只做候选发现与轻量分流，不替代文章原文阅读，也不自动创建学习报告。
