#!/usr/bin/env python3
"""精选播客节目单拉取/刷新。

读 `wiki/curated-podcasts.opml`（小宇宙 OPML 导出），逐个抓节目的公开 RSS，
生成/刷新 `wiki/show-indexes/{slug}.md`（全量单集索引，新→旧排列）。

- 「状态」列由人工/agent 维护（如「✅ 已处理」），刷新时按单集链接保留，不会被覆盖
- 新增单集检测：与旧文件按链接 diff，stdout 汇总打印 NEW 行（供周更 cron 汇报）
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
            s = p[0] * 3600 + (p[1] if len(p) > 1 else 0) * 60 + (p[2] if len(p) > 2 else 0)
        else:
            s = int(float(d))
    except ValueError:
        return d or "?"
    return f"{s // 3600}h{(s % 3600) // 60:02d}m" if s >= 3600 else f"{s // 60}m{s % 60:02d}s"


def norm_link(link):
    return link.split("?")[0].rstrip("/")


def load_old_statuses(path):
    """旧索引里 单集链接 → 状态 的映射（保留人工维护的 ✅ 等标记）。

    状态列可能含 |（如 [[wikilink|别名]]），不能用 split('|')，用正则从尾部取。
    """
    if not path.exists():
        return {}
    statuses = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.search(r"\]\((https?://[^)]*)\)\s*\|(.*)\|\s*$", line)
        if m:
            statuses[norm_link(m.group(1))] = m.group(2).strip()
    return statuses


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
    for num, date, dur, title, link, status in rows:
        tcell = title.replace("|", "\\|")
        title_md = f"[{tcell}]({link})" if link else tcell
        lines.append(f"| {num} | {date} | {dur} | {title_md} | {status} |")
    return "\n".join(lines) + "\n"


def main():
    shows = parse_opml(OPML)
    today = time.strftime("%Y-%m-%d")
    OUT_DIR.mkdir(exist_ok=True)
    failures, all_new = [], []
    for i, (title, feed) in enumerate(shows, 1):
        slug = SLUGS.get(title.strip()) or "show-" + re.sub(r"\W", "", title)[:20]
        dest = OUT_DIR / f"{slug}.md"
        try:
            xml = fetch(feed)
            items = re.findall(r"<item>(.*?)</item>", xml, re.S)
            if not items:
                raise ValueError("RSS 无 item")
            old_statuses = load_old_statuses(dest)
            old_links = set(old_statuses)
            rows = []
            for it in items:
                t, link = field(it, "title"), field(it, "link")
                date, dur = fmt_date(field(it, "pubDate")), fmt_dur(field(it, "itunes:duration"))
                m = re.match(r"(\d+)\s*[\.、]", t)
                status = old_statuses.get(norm_link(link), "—")
                rows.append((m.group(1) if m else "—", date, dur, t, link, status))
                if old_links and norm_link(link) not in old_links:
                    all_new.append((title, t, link))
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
    if failures:
        print("=== 失败节目 ===")
        for t, e in failures:
            print(f"FAIL | {t} | {e}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
