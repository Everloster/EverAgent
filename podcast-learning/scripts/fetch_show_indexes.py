#!/usr/bin/env python3
"""精选播客节目单拉取/刷新。

读 `wiki/curated-podcasts.opml`（小宇宙 OPML 导出），逐个抓节目的公开 RSS，
生成/刷新 `wiki/show-indexes/{slug}.md`（全量单集索引，新→旧排列）。

- 「状态」列由人工/agent 维护（如「✅ 已处理」），刷新时按 guid/链接保留，不会被覆盖
- 新增单集检测：与旧文件按 **guid + 链接双键** diff（guid 藏在标题单元格的 HTML 注释里，
  防单集链接换域名时全量误报 NEW + 状态丢失——2026-08-31 硅谷101 sv101.net→fireside.fm 实例），
  stdout 汇总打印 NEW 行；某节目新增占比 > 30% 判为疑似链接变更，降级 SUSPECT 不计入 NEW
- 版本化索引只在单集清单、元数据或状态真正变化时写入；单纯刷新日期不制造 diff。
  同一单集页面链接未变时保留旧 guid，避免喜马拉雅等源轮换音频 CDN 地址造成无意义改动
- 幂等；失败节目跳过并在结尾汇总，不静默

用法：
  python3 fetch_show_indexes.py
  python3 fetch_show_indexes.py --show crossing --dry-run --json
"""

import argparse
import html
import json
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
    # 2026-09-25 从「我也在听的品质播客」分享合集并入（OPML 导出丢档，collection API 补齐）
    "无尽的谈话♾️": "wujin-tanhua", "半拿铁·故事篇": "bannatie-gushipian",
    "人文清华播客：对话清华学者": "renwen-qinghua", "Ready Go": "ready-go",
    "商业就是这样": "shangye-jiushi-zheyang",
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
    """读取旧索引的链接/guid 状态，并保存每个稳定页面链接对应的旧 guid。

    状态列可能含 |（如 [[wikilink|别名]]），不能用 split('|')，用正则按列取。
    """
    by_link, by_guid, guid_by_link = {}, {}, {}
    if not path.exists():
        return by_link, by_guid, guid_by_link
    for line in path.read_text(encoding="utf-8").splitlines():
        # 链接后 [^|]* 段容纳 guid 注释；状态列用贪婪 (.*) 到行尾竖线——
        # 状态可含 [[wikilink|别名]] 的竖线，不能用 [^|]*（跨不过去会整行失配）
        m = re.search(r"\]\((https?://[^)]*)\)([^|]*)\|\s*(.*)\|\s*$", line)
        if not m:
            continue
        status = m.group(3).strip()
        link_key = norm_link(m.group(1))
        by_link[link_key] = status
        g = re.search(r"<!--g:(.*?)-->", m.group(2))
        if g:
            by_guid[g.group(1)] = status
            guid_by_link[link_key] = g.group(1)
    return by_link, by_guid, guid_by_link


def without_refresh_stamp(text):
    """比较版本化内容时忽略“最近拉取”日期；真正有变化时仍写入本次日期。"""
    return re.sub(r"(最近拉取：)\d{4}-\d{2}-\d{2}", r"\1<date>", text)


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


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--show",
        action="append",
        default=[],
        metavar="SLUG_OR_TITLE",
        help="只刷新指定节目，可重复；接受 show-index slug 或 OPML 完整标题",
    )
    parser.add_argument("--dry-run", action="store_true", help="只抓取和比较，不写索引文件")
    parser.add_argument("--json", action="store_true", help="只输出一份机器可读 JSON 摘要")
    return parser


def select_shows(shows, requested, parser=None):
    if not requested:
        return shows
    wanted = set(requested)
    selected = []
    matched = set()
    for title, feed in shows:
        slug = SLUGS.get(title.strip()) or "show-" + re.sub(r"\W", "", title)[:20]
        keys = {title, title.strip(), slug}
        if keys & wanted:
            selected.append((title, feed))
            matched.update(keys & wanted)
    missing = sorted(wanted - matched)
    if missing:
        message = "未知节目：" + ", ".join(missing)
        if parser is not None:
            parser.error(message)
        raise ValueError(message)
    return selected


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    shows = parse_opml(OPML)
    shows = select_shows(shows, args.show, parser)
    today = time.strftime("%Y-%m-%d")
    if not args.dry_run:
        OUT_DIR.mkdir(exist_ok=True)
    failures, all_new, suspects = [], [], []
    results = []
    for i, (title, feed) in enumerate(shows, 1):
        slug = SLUGS.get(title.strip()) or "show-" + re.sub(r"\W", "", title)[:20]
        dest = OUT_DIR / f"{slug}.md"
        try:
            xml = fetch(feed)
            items = re.findall(r"<item>(.*?)</item>", xml, re.S)
            if not items:
                raise ValueError("RSS 无 item")
            old_by_link, old_by_guid, old_guid_by_link = load_old_keys(dest)
            has_old = bool(old_by_link or old_by_guid)
            rows, show_new = [], []
            for it in items:
                t, link = field(it, "title"), field(it, "link")
                guid = field(it, "guid")
                date, dur = fmt_date(field(it, "pubDate")), fmt_dur(field(it, "itunes:duration"))
                m = re.match(r"(\d+)\s*[\.、]", t)
                link_key = norm_link(link)
                known = guid in old_by_guid or link_key in old_by_link
                status = old_by_guid.get(guid) or old_by_link.get(link_key, "—")
                # 页面链接稳定时，旧 guid 比会轮换的 enclosure/CDN 地址更适合作为版本化标识。
                stable_guid = old_guid_by_link.get(link_key, guid)
                rows.append((m.group(1) if m else "—", date, dur, t, link, status, stable_guid))
                if has_old and not known:
                    show_new.append((t, link, date))
            # 护栏：新增占比过高 → 疑似链接变更，降级不计入 NEW
            if show_new and len(rows) >= 10 and len(show_new) / len(rows) > 0.3:
                suspects.append((title, len(show_new), len(rows), show_new[0][0]))
            else:
                all_new.extend((title, t, link) for t, link, _ in show_new)
            # 新→旧：有集数按集数，无集数按日期字符串
            rows.sort(key=lambda r: (r[0].isdigit() and int(r[0]) or 0, r[1]), reverse=True)
            rendered = render(title, feed, rows, today)
            old_text = dest.read_text(encoding="utf-8") if dest.exists() else ""
            changed = without_refresh_stamp(old_text) != without_refresh_stamp(rendered)
            if changed and not args.dry_run:
                dest.write_text(rendered, encoding="utf-8")
            results.append({
                "title": title,
                "slug": slug,
                "episodes": len(rows),
                "changed": changed,
                "new_episodes": [
                    {"title": item_title, "url": link, "published_on": date}
                    for item_title, link, date in show_new
                ],
            })
            if not args.json:
                mode = "[dry-run] " if args.dry_run else ""
                suffix = "有变化" if changed else "无变化"
                print(f"[{i}/{len(shows)}] {mode}{title} → {slug}.md（{len(rows)} 集，{suffix}）")
        except Exception as e:  # noqa: BLE001
            failures.append((title, str(e)))
            if not args.json:
                print(f"[{i}/{len(shows)}] {title} 失败: {e}", file=sys.stderr)
        time.sleep(0.3)

    summary = {
        "schema_version": 1,
        "dry_run": args.dry_run,
        "requested_shows": args.show,
        "processed": len(results),
        "changed": sum(1 for item in results if item["changed"]),
        "shows": results,
        "new_episodes": [
            {"show": show, "title": title, "url": link}
            for show, title, link in all_new
        ],
        "suspects": [
            {"show": title, "new_count": count, "total": total, "example": first}
            for title, count, total, first in suspects
        ],
        "failures": [{"show": title, "error": error} for title, error in failures],
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print()
        if all_new:
            print("=== 新增单集 ===")
            for show, title, link in all_new:
                print(f"NEW | {show} | {title} | {link}")
        else:
            print("=== 无新增单集 ===")
        if suspects:
            print("=== 疑似链接变更（新增占比>30%，已降级，请人工核对）===")
            for title, count, total, first in suspects:
                print(f"SUSPECT | {title} | {count}/{total} 集判定新增，如 {first}")
        if failures:
            print("=== 失败节目 ===")
            for title, error in failures:
                print(f"FAIL | {title} | {error}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
