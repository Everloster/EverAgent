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
| `enabled` | 是否参与默认更新查询 |
| `homepage` | 人工访问入口 |
| `discovery.kind` | `rss`、`search` 或 `sitemap` |
| `discovery.url/query` | 对应的 feed、sitemap 或官方域名查询 |
| `allow_domains` | 结果域名白名单 |
| `path_prefixes` | URL 路径白名单 |
| `include_any` | 至少命中一个才保留；空数组表示不加此门 |
| `exclude_any` | 来源专属噪声词 |
| `why` | 收录理由 |

`global_exclude_any` 只放稳定的公司新闻噪声词。不要把具体模型名或一次性事件写成全局规则。

## 采集

- `rss`：eacli `web.read` → 必要时只读 HTTP XML fallback。
- `search`：eacli `web.search`，查询自动附带 `after:YYYY-MM-DD`，随后再按解析到的发布日期过滤。
- `sitemap`：eacli `web.read` → 必要时只读 HTTP XML fallback；`lastmod` 表示页面变更，不等于首次发布日期。

所有结果再经过域名、路径、来源过滤词、全局噪声词和 URL 去重。Qwen 等使用 `?id=` 区分文章的站点会保留业务 query，只删除 `utm_*` 等追踪参数。

## 输出

`updates --format json` 是 Agent 消费面，包含：

- 查询时间窗和成功来源数；
- `deep_read_candidate`、`release_signal`、`technical_update`；
- 每条的来源、URL、日期、摘要和入选理由；
- failures、Token Plan 选择证据和 XML fallback 记录。

脚本只做候选发现与轻量分流，不替代文章原文阅读，也不自动创建学习报告。
