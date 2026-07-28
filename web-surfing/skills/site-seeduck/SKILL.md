# site-seeduck — SeedHub (seeduck.cc) 取数手册

> **站点性质**：SeedHub「影视&动漫分享」——电影/动漫/剧集资源索引站，带豆瓣评分、分类、年份/语言标签。
> **公开可访问、无需登录**。opencli **无专属适配器**，走 `opencli browser` 直驱。
> **合规**：只抓公开元数据（片名/评分/年份/类型/详情链接）做片单整理；**不下载资源**。

---

## §1 URL 结构（核心，直接套用）

### 分类根
```
电影  /categories/1/movies/
动漫  /categories/2/movies/
剧集  /categories/3/movies/
```

### 排序参数 `?order=`
| 值 | 含义 |
|----|------|
| `score` | 豆瓣评分降序（做 Top 榜用这个） |
| `update` | 最近更新（追新用这个） |
| `date` | 上映时间 |
| `view` | 近期热门 |

### 翻页
```
?page=N&order=score      # N 从 1 起；每类约 2000+ 页
```

### 标签筛选 `/categories/{cat}/tags/{tagId}/movies/`（★关键）
在分类页顶部"常用标签"里，语言/年份都是 tag。**剧集(cat=3)** 常用 tagId：

| 语言 tag | tagId | | 年份 tag | tagId |
|------|------|---|------|------|
| 英语 | 8783 | | 2026 | 65055 |
| 汉语普通话 | 64362 | | 2025 | 64938 |
| 日语 | 26544 | | 2024 | 64343 |
| **韩语** | **22290** | | 2023 | 64419 |
| 粤语 | 13567 | | 2022 | 64257 |

> tagId 是**分类内局部**的（电影/动漫的同名标签 id 不同）。要别的分类/语言，先 `extract` 分类根页读"常用标签"里的链接拿 id。

**组合示例**：
```
韩语剧集按豆瓣评分   https://seeduck.cc/categories/3/tags/22290/movies/?order=score
韩语剧集按最近更新   https://seeduck.cc/categories/3/tags/22290/movies/?order=update
```

### 详情页
```
/movies/{id}/     # 单部片详情，如 /movies/115513/
```

---

## §2 抓取命令（实测可用）

```bash
opencli doctor                                    # 先确认桥接绿
opencli browser sd open "https://seeduck.cc/categories/3/tags/22290/movies/?order=score"
opencli browser sd extract                         # 返回 {url,title,content} JSON
```

### 多页遍历 + 解析（韩剧 Top10 任务用的就是这套）
```bash
for p in 1 2 3 4 5 6; do
  opencli browser sd open "https://seeduck.cc/categories/3/tags/22290/movies/?page=${p}&order=score" >/dev/null 2>&1
  sleep 1
  opencli browser sd extract 2>/dev/null
done | python3 -c "
import json,sys,re
raw=sys.stdin.read()
objs=re.findall(r'\{.*?\"content\":.*?\n\}', raw, re.S)
seen=set(); rows=[]
for o in objs:
    try: d=json.loads(o)
    except: continue
    for b in re.split(r'\n(?=\[!\[)', d['content']):      # 每部片一个 block，以 [![封面 开头
        m=re.search(r'\]\((/movies/\d+/)', b)              # 详情链接
        t=re.search(r'##\s*(.+)', b)                       # 片名
        info=re.search(r'-\s*(\d{4})\s*/\s*剧集\s*/\s*([^/]+?)\s*/', b)  # 年份/地区
        score=re.search(r'豆瓣评分:\s*\[([\d.]+)\]\((https://movie\.douban\.com/subject/\d+/?)\)', b)
        typ=re.search(r'类型:\s*(.+)', b)
        if m and t and info and score:
            yr=int(info.group(1)); country=info.group(2).strip()
            title=t.group(1).strip(); sc=float(score.group(1)); db=score.group(2)
            url='https://seeduck.cc'+m.group(1)
            types=re.sub(r'\[|\]\(.*?\)','',typ.group(1)).strip() if typ else ''
            if url in seen: continue
            seen.add(url)
            if 2024<=yr<=2026:                             # ← 年份过滤，按需改
                rows.append((sc,yr,title,country,types,url,db))
rows.sort(key=lambda x:-x[0])
for r in rows: print(f'{r[0]} | {r[1]} | {r[2]} | {r[4]} | {r[5]} | {r[6]}')
"
```

---

## §3 页面数据格式（extract content 里每部片的 block）

```
[![片名](封面webp)](/movies/{id}/ "片名")
-   ## 片名
-   2025 / 剧集 / 韩国 / 韩语 / 主演A 主演B
-   类型: [爱情](...) / [剧情](...)
-   豆瓣评分: [9.3](https://movie.douban.com/subject/{doubanId}/)
```
解析靠正则即可（见 §2）。每页约 20 条。

---

## §4 坑 & 注意

1. **"剧集"里混综艺/真人秀**：韩综（如《犯罪现场Zero》《黑白厨师》《地球游戏厅》）也在 cat=3。做"韩剧"榜要按 `类型` 含"真人秀"剔除。
2. **评分是站点标注的豆瓣分**，可能滞后，报告里注明"以豆瓣链接为准"。
3. **图床域名会变**（`sh1.pcie.pppoe.top` 等），封面链接不稳定，别依赖。
4. **低频抓取**：`sleep 1` 起步，别高频遍历几百页触发封禁。
5. tagId 分类内局部，跨分类要重新读标签。
6. **全站无搜索功能（2026-07-28 实测）**：首页无搜索框，`/search/?q=` 被 nginx 403，`/sitemap.xml` 在 CF challenge 后。**找指定某部片只能「语言 tag + `order=score` 翻页 + 本地正则匹配片名」**（日语剧集实测：豆瓣 8.5+ 在前 8 页/160 部内）。`sidhub.cc` 会 301 到 `seeduck.cc`，同一个站。

---

*沉淀于 2026-07-14，首次任务：韩剧 Top10 2024-2026；2026-07-28 二次任务：日剧 TOP10(2016–2025）指定片检索，补 §4.6（无搜索）*
