# B 站关注列表、最近投稿与未看更新采集方案调研

> 日期：2026-10-14
> 目标：在不逐个轮询 1761 个 UP 主的前提下，导出完整关注列表，获取关注 UP 的最近视频，并区分“动态未读”与“视频未看”。

## 结论

现成能力已经覆盖大部分需求，最佳路线是 **OpenCLI 登录态 + B 站 Web API + 本地游标状态**，不需要维护 1761 个独立 RSS，也不应该逐个调用每个 UP 主的投稿接口。

1. **完整关注列表可导出**：`/x/relation/followings` 每页最多 50 条。登录态实测总数 1761，第 36 页 11 条，第 37 页为空，因此完整导出需要 36 次低频请求。
2. **所有关注 UP 的最近视频可聚合获取**：`/x/polymer/web-dynamic/v1/feed/all?type=video` 是关注时间线，支持 `offset` 游标；一次返回约 20 条，不需要逐 UP 查询。
3. **官方动态页推荐的“哪些 UP 有更新”可直接取得**：`/x/polymer/web-dynamic/v1/portal` 与 `/x/polymer/web-dynamic/v1/uplist` 返回官方展示的关注 UP 子集及 `has_update`。本次实测共返回 59 个候选，其中 10 个 `has_update=true`。这不是完整 1761 人列表，而是动态页当前展示/推荐的子集。
4. **“动态未读”不等于“视频没播放过”**：动态接口没有 `watched` 或 `progress` 字段。真正的视频观看状态必须与 `/x/web-interface/history/cursor` 合并；该接口每页最多 30 条，支持游标分页并返回 `bvid`、`progress`、`duration`、`view_at`。
5. **当前 OpenCLI 已具备基础命令**：`following`、`feed`、`history` 都已可用；缺口是 `following` 不自动翻完全部页面、`history` 只取首屏 30 条、没有公开 `portal/uplist` 与 `feed/nav` 的命令，也没有持久化已读基线。

## 需求拆解

| 需求 | 最合适的数据源 | 是否已有 OpenCLI 命令 | 备注 |
|---|---|---:|---|
| 导出全部关注 UP | `x/relation/followings` | 有：`following` | 需循环 36 页并去重 |
| 获取关注者最近投稿 | `x/polymer/web-dynamic/v1/feed/all?type=video` | 有：`feed --type video` | 游标分页，不要逐 UP 请求 |
| 获取动态页推荐的更新 UP | `portal` + `uplist` | 无 | 返回 `has_update`，仅官方展示子集 |
| 获取动态未读数 | `feed/all/update` | 无 | 需要保存 `update_baseline` |
| 按 UP 维护动态未读 | `feed/nav` | 无 | 按 `author.mid` 保存最大 `id_str` |
| 判断视频未看/部分观看/看完 | `history/cursor` | 部分：`history` | 现命令只取最多 30 条，需游标分页 |

## 登录态实测

所有测试均通过本机 Chrome 登录态执行，Cookie 未导出、未写入仓库。

### 完整关注列表

```text
GET https://api.bilibili.com/x/relation/followings
    ?vmid=<self_uid>&pn=<page>&ps=50&order=desc
```

实测：

- `data.total = 1761`
- 第 1 页 50 条
- 第 36 页 11 条
- 第 37 页 0 条

可保留字段：`mid`、`uname`、`sign`、`face`、`mtime`、`tag`、`special`、认证信息。原始列表体现个人关注偏好，应该存本机私有数据目录或私有仓，不应直接提交到公开 EverAgent。

### 关注视频流

```text
GET https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all
    ?type=video&offset=<cursor>&platform=web
```

返回 `items`、`has_more`、`offset`、`update_baseline`、`update_num`。视频项包含：

- UP 主：`modules.module_author.mid/name/pub_ts`
- 视频：`modules.module_dynamic.major.archive.bvid/title/duration_text`
- 动态 ID：`id_str`

响应中没有观看进度字段。

### 官方推荐/展示的更新 UP

```text
GET https://api.bilibili.com/x/polymer/web-dynamic/v1/portal?up_list_more=1
GET https://api.bilibili.com/x/polymer/web-dynamic/v1/uplist?offset=<cursor>&platform=web
```

返回项包含 `mid`、`uname`、`face`、`has_update`。本次实测首批 50 条、续页 9 条，合计 59 条；其中 10 条 `has_update=true`。

这个列表适合回答“B 站动态页现在提示哪些 UP 有更新”，但不能代替完整关注列表，也不能证明对应视频从未播放。

### 动态未读

```text
GET https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all/update
    ?type=video&update_baseline=<last_seen_dynamic_id>

GET https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/nav
    ?offset=<cursor>
```

`feed/all/update` 返回 `update_num`；`feed/nav` 返回简化动态项、作者、视频链接、`offset` 与 `has_more`。动态 ID 超出 JavaScript 安全整数范围，应以字符串按“长度 + 字典序”比较，不能转成普通 Number。

### 视频观看历史

```text
GET https://api.bilibili.com/x/web-interface/history/cursor
    ?ps=30&type=archive
    &max=<previous_cursor.max>
    &view_at=<previous_cursor.view_at>
    &business=<previous_cursor.business>
```

实测连续两页均返回 30 条，游标可继续向前翻。关键字段：

- `history.bvid`
- `progress`
- `duration`
- `view_at`
- `author_mid` / `author_name`

判断建议：

- 历史中不存在该 BVID：在已覆盖的历史时间窗内可标记为“未看”。
- `0 <= progress < duration`：部分观看。
- `progress < 0` 或 `progress >= duration`：按 B 站客户端惯例视为看完。

抓历史时只需翻到最旧 `view_at` 早于本轮候选视频最早发布时间，不必同步全部历史。

## GitHub 现成方案评估

| 项目 | 可复用内容 | 结论 |
|---|---|---|
| [jackwener/OpenCLI](https://github.com/jackwener/OpenCLI) | 已实现 `following`、`feed`、`history`，直接复用 Chrome 登录态 | **主方案**；补少量命令即可形成完整工作流 |
| [lovetingyuan/minibili](https://github.com/lovetingyuan/minibili) | `feed/nav` 游标翻页、每 UP 最新动态 ID、基线与本地已读状态算法 | **最佳未读算法参考**，不是现成 CLI |
| [bggRGjQaUbCoE/PiliPlus](https://github.com/bggRGjQaUbCoE/PiliPlus) | 已实现 `portal`、`uplist`、动态游标分页 | API 行为参考，完整 App 过重 |
| [the1812/Bilibili-Evolved](https://github.com/the1812/Bilibili-Evolved) | 用动态 ID 基线计算通知数，支持视频动态过滤 | 适合浏览器内体验，不适合结构化导出 |
| [moushicheng/bilibili-API-collect](https://github.com/moushicheng/bilibili-API-collect) | 关注、动态与历史接口字段文档 | 参考资料；原始 SocialSisterYi 仓库已转入 deprecated 分支 |
| [DIYgod/RSSHub](https://github.com/DIYgod/RSSHub) | B 站单 UP 视频 RSS、关注相关路由 | 适合精选 UP 长期订阅；不适合直接维护 1761 路 RSS，关注路由也不是全量更新收件箱 |
| [LifeArchiveProject/BilibiliHistoryFetcher](https://github.com/LifeArchiveProject/BilibiliHistoryFetcher) | 完整观看历史同步、SQLite、定时任务与分析 | 若以后要做观看行为档案可复用；当前需求明显过重 |

## 推荐实现

### 第一阶段：零新增依赖

直接使用现有 OpenCLI：

```bash
# 单页关注列表
opencli bilibili following --page 1 --limit 50 -f json

# 最近关注视频
opencli bilibili feed --type video --pages 5 --limit 100 -f json

# 最近观看记录；当前命令最多取首屏 30 条
opencli bilibili history --limit 30 -f json
```

适合临时选题，不足以形成稳定资产。

### 第二阶段：本地 B 站收件箱（已实现）

本仓已新增只读脚本：

```text
web-surfing/skills/site-bilibili/scripts/bilibili_inbox.py
```

它通过 OpenCLI 浏览器桥接复用 Chrome 登录态，已实现三个命令：

1. `followings`：循环 `pn=1..N`，每页 50 条，低频请求，输出 JSON/CSV/Markdown。
2. `recommended-ups`：合并 `portal` 与 `uplist`，返回官方动态页当前展示的更新 UP。
3. `inbox`：游标抓取关注视频和观看历史，以 BVID 合并为“未看 / 打开 / 部分观看 / 已看完”，支持时间、时长和官方更新过滤。

常用调用：

```bash
SCRIPT=web-surfing/skills/site-bilibili/scripts/bilibili_inbox.py
python3 "$SCRIPT" recommended-ups --format md
python3 "$SCRIPT" inbox --since-hours 168 --min-duration-minutes 10 --unwatched-only --format md
```

建议输出结构：

```json
{
  "bvid": "BV...",
  "title": "...",
  "creator_mid": "...",
  "creator_name": "...",
  "published_at": 0,
  "dynamic_id": "...",
  "dynamic_unread": true,
  "watch_state": "unwatched",
  "progress_seconds": 0,
  "duration_seconds": 0,
  "url": "https://www.bilibili.com/video/BV..."
}
```

原始 1761 人列表放本地私有数据目录；公开仓只保留用户确认后的精选 UP 清单和可复用代码，不保存 Cookie/SESSDATA。当前实现不持久化动态已读基线，避免扫描动作悄悄改变“已读”语义；需要长期红点状态时再增加显式 `mark-seen` 动作。

### 第三阶段：接入播客学习

从 `updates/unwatched` 输出中人工或规则筛选长视频、访谈、知识类内容；用户选中后只把视频 URL 送入现有 `podcast-learning` 的 eacli 静默转写链。不要自动下载全部更新。

## 边界与风险

- 以上均为 B 站 Web 客户端正在使用的非公开业务 API，可能随前端升级变化。
- Cookie 只应由 OpenCLI 浏览器桥接在本机解析，禁止写入命令参数、日志、报告或仓库。
- 批量导出关注列表建议每页间隔 300–800 ms；出现 `-352`、验证码或限流立即停止。
- `portal/uplist.has_update` 表示动态页更新提示，不等同于视频播放状态。
- OpenCLI 1.8.6 的 `me` 实测错误显示 `following=0`；真实关注数应取 `portal.my_info.following` 或 `relation/followings.data.total`。

---
*报告生成时间: 2026-10-14*
*数据来源: GitHub 代码检索、B 站登录态 Web API、OpenCLI 1.8.6 只读实测*
*说明: 未导出或保存 Cookie、账号 UID、完整关注明细；接口均可能随 B 站前端变更。*
