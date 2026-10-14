---
name: site-bilibili
description: 读取 B 站登录账号的关注列表、关注动态、最近投稿、动态未读和观看历史；优先复用 OpenCLI bilibili 适配器，缺口用登录态 browser network/eval 核验。
---

# Bilibili 只读取数

## 边界

- 只读。禁止关注、取关、评论、点赞、投币等写操作，除非用户单独明确授权。
- Cookie/SESSDATA 只由 OpenCLI Chrome 桥接在本机使用，不输出、不落盘、不入仓库。
- 完整关注列表和已读游标属于个人偏好数据，放私有/本地数据目录；公开仓只存用户确认后的精选清单。
- 批量请求低频执行；出现 `-352`、验证码或限流立即停止。

## 开始前

```bash
opencli doctor
opencli list -f json | jq '[.[] | select(.site == "bilibili")]'
opencli bilibili whoami -f json
```

## 已有适配器

```bash
# 关注列表，每页最多 50 条；循环到空页
opencli bilibili following --page 1 --limit 50 -f json

# 登录账号的关注视频流，游标由适配器内部处理
opencli bilibili feed --type video --pages 5 --limit 100 -f json

# 观看历史；当前适配器只取最多 30 条
opencli bilibili history --limit 30 -f json
```

不要为获取最新视频而对全部 UP 逐个运行 `user-videos`。

## 仓内收件箱工具

仓内脚本封装了 OpenCLI 登录态与接口游标，不接触 Cookie：

```bash
SCRIPT=web-surfing/skills/site-bilibili/scripts/bilibili_inbox.py

# 导出完整关注列表；原始结果只写私有/本地路径
python3 "$SCRIPT" followings --format json --out ~/.local/share/everagent/bilibili/followings.json

# 官方动态页当前提示有更新的 UP
python3 "$SCRIPT" recommended-ups --format md

# 最近 7 天、至少 10 分钟、尚未播放的学习候选
python3 "$SCRIPT" inbox --since-hours 168 --min-duration-minutes 10 \
  --unwatched-only --format md

# 只看官方动态页当前标记有更新的 UP
python3 "$SCRIPT" inbox --recommended-only --unwatched-only --format md
```

脚本默认抓 5 页关注视频、最多 10 页观看历史；可用 `--feed-pages`、`--history-pages`、
`--limit` 调整。输出文件默认拒绝覆盖，明确传 `--force` 才替换。

## 核心接口

| 用途 | 接口 |
|---|---|
| 完整关注列表 | `/x/relation/followings?vmid=...&pn=...&ps=50&order=desc` |
| 关注视频时间线 | `/x/polymer/web-dynamic/v1/feed/all?type=video&offset=...` |
| 动态未读计数 | `/x/polymer/web-dynamic/v1/feed/all/update?type=video&update_baseline=...` |
| 按 UP 的最近动态 | `/x/polymer/web-dynamic/v1/feed/nav?offset=...` |
| 动态页推荐/展示 UP | `/x/polymer/web-dynamic/v1/portal?up_list_more=1` |
| 推荐 UP 续页 | `/x/polymer/web-dynamic/v1/uplist?offset=...&platform=web` |
| 观看历史 | `/x/web-interface/history/cursor?ps=30&type=archive&max=...&view_at=...&business=...` |

## 状态语义

- `portal/uplist.items[].has_update`：官方动态页提示该 UP 有更新；仅覆盖官方展示子集。
- `feed/all.update_baseline`：当前动态流最新 ID，可作为“看过动态列表”的水位。
- `feed/all/update.data.update_num`：给定水位之后的新增动态数量。
- `feed/nav`：用于按 `author.mid` 计算每个 UP 的最新动态 ID。
- 动态 ID 必须按字符串的长度再按字典序比较，禁止转 JavaScript Number。
- 动态接口没有视频观看状态；用历史中的 `history.bvid`、`progress`、`duration` 合并。

## 浏览器核验

适配器缺字段时再使用浏览器，不要先抓 DOM：

```bash
opencli browser bili-research open 'https://t.bilibili.com/' --window background
opencli browser bili-research wait time 3
opencli browser bili-research network
opencli browser bili-research network --detail '<exact-key>'
opencli browser bili-research close
```

优先检查 `portal`、`uplist`、`feed/nav`、`feed/all`、`history/cursor` 的 JSON 响应。

## 推荐输出

长期任务输出候选视频的 BVID、标题、UP UID/名称、发布时间、动态 ID、动态未读状态、观看状态、进度和 URL。原始账号信息、Cookie 和完整关注偏好不进入公开报告。

## 已知问题

- OpenCLI 1.8.6 的 `me` 可能把关注数显示为 0；使用 `portal.my_info.following` 或 `relation/followings.data.total` 核验。
- `following` 当前不自动全量翻页。
- `history` 当前不支持游标分页。
- `feed` 当前不持久化 `update_baseline`，也不计算每 UP 未读状态。

以上 OpenCLI 原生命令缺口已由仓内 `bilibili_inbox.py` 在调用层补齐；若 B 站字段变化，优先更新该脚本和测试，不修改 Cookie 管理方式。

源码与实测记录见 [`../../reports/bilibili-following-updates-research-2026-10-14.md`](../../reports/bilibili-following-updates-research-2026-10-14.md)。
