#!/usr/bin/env python3
"""精选播客节目单拉取/刷新。

读 `wiki/curated-podcasts.opml`（小宇宙 OPML 导出），逐个抓节目的公开 RSS，
生成/刷新 `wiki/show-indexes/{slug}.md`（全量单集索引，新→旧排列）。

- 「状态」列由人工/agent 维护（如「✅ 已处理」），刷新时按 guid/链接保留，不会被覆盖
- 新增单集检测：与旧文件按 **guid + 链接双键** diff（guid 藏在标题单元格的 HTML 注释里，
  防单集链接换域名时全量误报 NEW + 状态丢失——2026-08-31 硅谷101 sv101.net→fireside.fm 实例），
  stdout 汇总打印 NEW 行；某节目新增占比 > 30% 判为疑似链接变更，降级 SUSPECT 不计入 NEW
- 幂等；失败节目跳过并在结尾汇总，不静默

用法：python3 fetch_show_indexes.py
"""

import html
import pathlib
import re
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OPML = ROOT / "wiki" / "curated-podcasts.opml"
OUT_DIR = ROOT / "wiki" / "show-indexes"

# 节目标题 → slug（与报告命名规范同源：小写连字符/拼音/英文）
SLUGS = {
    "三五环": "sanwuhuan", "疯投圈": "fengtouquan", "声东击西": "shengdong-jixi",
    "忽左忽右": "huzuo-huyou", "硅谷101": "guigu101", "老talk消息": "laotalk-xiaoxi",
    "知行小酒馆": "zhixing-xiaojiuguan", "十字路口Crossing": "crossing",
    "组织进化论": "zuzhi-jinhualun", "全嘻嘻": "quanxixi", "姜Dora在此": "jiang-dora",
    "声动早咖啡": "shengdong-zaokafei", "无人知晓": "wurenzhixiao", "乱翻书": "luanfanshu",
    "晚点聊 LateTalk": "wandian-latetalk", "大小马聊科技": "daxiaoma-keji",
    "起朱楼宴宾客": "qizhulou", "温柔一刀": "wenrou-yidao",
    "半拿铁 | 商业沉浮录": "bannatie", "纵横四海": "zongheng-sihai",
    "张小珺Jùn｜商业访谈录": "zhangxiaojun", "一苒一刻": "yiran-yike",
    "高能量": "gaonengliang", "成为巴菲特 | 价投村": "chengwei-buffett",
    "是宇弦啊": "yuxian", "面基": "mianji", "AI炼金术": "ai-lianjinshu",
    "开始连接 LinkStart": "linkstart", "此话当真": "cihua-dangzhen",
    "大小马智驾": "daxiaoma-zhijia", "42章经": "42zhangjing", "投资ABC": "touzi-abc",
    "二的三次方": "erde-sancifang", "能者多唠｜商业原声": "nengzhe-duolao",
    "屠龙之术": "tulong-zhishu", "听懂涨声": "tingdong-zhangsheng",
    "第一推动": "diyi-tuidong", "硅基立场": "guiji-lichang",
    "梁将军商业内参": "liangjiangjun", "李诞": "lidan",
    "天真不天真": "tianzhen-butianzhen", "卫诗婕｜漫谈Light the Star": "weishijie",
    "屠龙大实话": "tulong-dashihua", "菠萝健康派": "boluo-jiankang",
    "说医解药": "shuoyi-jieyao", "赛博对话": "saibo-duihua",
    "信号与噪声": "xinhao-yuzaosheng", "半拿铁·周刊": "bannatie-zhoukan",
    "101 Weekly": "101-weekly", "罗永浩的十字路口": "luoyonghao-crossing",
    "课代表立正": "kedaibiao-lizheng",
}

MONTHS = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
          "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def parse_opml(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    shows = []
    for tag in re.findall(r"<outline\b[^>]*>", raw):
        def attr(name):
            m = re.search(rf'{name}="(.*?)"', tag, re.S)
            return html.unescape(m.group(1)) if m else ""
        title, feed = attr("title") or attr("text"), attr("xmlUrl")
        if title and feed:
            shows.append((title, feed))
    return shows


def field(item, tag):
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", item, re.S)
    if not m:
        return ""
    v = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", m.group(1), flags=re.S)
    return html.unescape(v).strip()


def fmt_date(pub):
    parts = pub.split()  # RFC822: 'Wed, 19 Aug 2026 00:00:00 GMT'
    if len(parts) >= 4 and parts[2] in MONTHS:
        return f"{parts[3]}-{MONTHS[parts[2]]}-{parts[1].zfill(2)}"
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", pub)
    return m.group(0) if m else pub[:16]


def fmt_dur(d):
    try:
        if ":" in d:
            p = [int(x) for x in d.split(":")]
            if len(p) == 2:  # MM:SS
                s = p[0] * 60 + p[1]
            else:  # H:MM:SS
                s = p[0] * 3600 + p[1] * 60 + p[2]
        else:
            s = int(float(d))
    except ValueError:
        return d or "?"
    return f"{s // 3600}h{(s % 3600) // 60:02d}m" if s >= 3600 else f"{s // 60}m{s % 60:02d}s"


def norm_link(link):
    return link.split("?")[0].rstrip("/")


def load_old_keys(path):
    """旧索引的键 → 状态 映射，键含链接与 guid 两套（guid 在标题单元格 HTML 注释里）。

    状态列可能含 |（如 [[wikilink|别名]]），不能用 split('|')，用正则按列取。
    """
    by_link, by_guid = {}, {}
    if not path.exists():
        return by_link, by_guid
    for line in path.read_text(encoding="utf-8").splitlines():
        # 链接后 [^|]* 段容纳 guid 注释；状态列用贪婪 (.*) 到行尾竖线——
        # 状态可含 [[wikilink|别名]] 的竖线，不能用 [^|]*（跨不过去会整行失配）
        m = re.search(r"\]\((https?://[^)]*)\)([^|]*)\|\s*(.*)\|\s*$", line)
        if not m:
            continue
        status = m.group(3).strip()
        by_link[norm_link(m.group(1))] = status
        g = re.search(r"<!--g:(.*?)-->", m.group(2))
        if g:
            by_guid[g.group(1)] = status
    return by_link, by_guid


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def render(show, feed, rows, today):
    lines = [
        f"# {show} — 全量单集索引",
        "",
        f"> 来源：官方 RSS（<{feed}>）｜ 最近拉取：{today} ｜ 总集数：{len(rows)}",
        "> 由 `podcast-learning/scripts/fetch_show_indexes.py` 生成/刷新；「状态」列人工维护，刷新不覆盖。",
        "",
        "| 集 | 发布日期 | 时长 | 标题 | 状态 |",
        "|---|---|---|---|---|",
    ]
    for num, date, dur, title, link, status, guid in rows:
        tcell = title.replace("|", "\\|")
        title_md = f"[{tcell}]({link})" if link else tcell
        if guid:  # guid 藏 HTML 注释：渲染不可见，diff 用
            title_md += f"<!--g:{guid}-->"
        lines.append(f"| {num} | {date} | {dur} | {title_md} | {status} |")
    return "\n".join(lines) + "\n"


def main():
    shows = parse_opml(OPML)
    today = time.strftime("%Y-%m-%d")
    OUT_DIR.mkdir(exist_ok=True)
    failures, all_new, suspects = [], [], []
    for i, (title, feed) in enumerate(shows, 1):
        slug = SLUGS.get(title.strip()) or "show-" + re.sub(r"\W", "", title)[:20]
        dest = OUT_DIR / f"{slug}.md"
        try:
            xml = fetch(feed)
            items = re.findall(r"<item>(.*?)</item>", xml, re.S)
            if not items:
                raise ValueError("RSS 无 item")
            old_by_link, old_by_guid = load_old_keys(dest)
            has_old = bool(old_by_link or old_by_guid)
            rows, show_new = [], []
            for it in items:
                t, link = field(it, "title"), field(it, "link")
                guid = field(it, "guid")
                date, dur = fmt_date(field(it, "pubDate")), fmt_dur(field(it, "itunes:duration"))
                m = re.match(r"(\d+)\s*[\.、]", t)
                known = guid in old_by_guid or norm_link(link) in old_by_link
                status = old_by_guid.get(guid) or old_by_link.get(norm_link(link), "—")
                rows.append((m.group(1) if m else "—", date, dur, t, link, status, guid))
                if has_old and not known:
                    show_new.append((t, link, date))
            # 护栏：新增占比过高 → 疑似链接变更，降级不计入 NEW
            if show_new and len(rows) >= 10 and len(show_new) / len(rows) > 0.3:
                suspects.append((title, len(show_new), len(rows), show_new[0][0]))
            else:
                all_new.extend((title, t, link) for t, link, _ in show_new)
            # 新→旧：有集数按集数，无集数按日期字符串
            rows.sort(key=lambda r: (r[0].isdigit() and int(r[0]) or 0, r[1]), reverse=True)
            dest.write_text(render(title, feed, rows, today), encoding="utf-8")
            print(f"[{i}/{len(shows)}] {title} → {slug}.md（{len(rows)} 集）")
        except Exception as e:  # noqa: BLE001
            failures.append((title, str(e)))
            print(f"[{i}/{len(shows)}] {title} 失败: {e}", file=sys.stderr)
        time.sleep(0.3)
    print()
    if all_new:
        print("=== 新增单集 ===")
        for show, t, link in all_new:
            print(f"NEW | {show} | {t} | {link}")
    else:
        print("=== 无新增单集 ===")
    if suspects:
        print("=== 疑似链接变更（新增占比>30%，已降级，请人工核对）===")
        for t, n, total, first in suspects:
            print(f"SUSPECT | {t} | {n}/{total} 集判定新增，如 {first}")
    if failures:
        print("=== 失败节目 ===")
        for t, e in failures:
            print(f"FAIL | {t} | {e}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
