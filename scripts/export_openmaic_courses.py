#!/usr/bin/env python3
"""导出 OpenMAIC 课程讲义为 markdown，归档进 ai-learning/courses/。

用法: python3 scripts/export_openmaic_courses.py
数据源: ../OpenMAIC/data/classrooms/*.json（场景结构 + speech 讲稿 + quiz 题目）
产出:   ai-learning/courses/ 下每节课一个 md（frontmatter 带课堂 id 可溯源）
增量:   已存在的文件跳过（课程生成后内容不再变）；--force 全量重写
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
COURSES_DIR = Path("../OpenMAIC/data/classrooms").resolve()
OUT_DIR = ROOT / "ai-learning" / "courses"

SERIES_CONFIG = {
    "harness": {
        "match": "harness",
        "prefix": "AgentHarness课",
        "title": "AgentHarness 课",
        # 关键词对生成后的实际课程名；课程名优先于场景标题（场景会回顾上节而误中）
        "no_rules": [(1, "turn"), (2, "哲学"), (3, "主循环"), (4, "沙箱"),
                     (5, "上下文"), (6, "LLM API"), (7, "MCP"), (8, "外壳"), (9, "封顶")],
        "default_no": 1,
    },
    "vllm": {
        "match": "vllm",
        "prefix": "vLLM课",
        "title": "vLLM 课",
        "no_rules": [(2, "调度"), (3, "请求的一生"), (4, "深潜"), (5, "执行层"),
                     (6, "采样"), (7, "投机")],
        "default_no": 1,
    },
}


def parse_time(v):
    try:
        return int(v) / 1000
    except (TypeError, ValueError):
        pass
    from datetime import datetime
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0


def detect_series(name):
    n = name.lower()
    for cfg in SERIES_CONFIG.values():
        if cfg["match"] in n:
            return cfg
    return None


def series_no(cfg, name, titles):
    for no, key in cfg["no_rules"]:
        if key in name:
            return no
    for no, key in cfg["no_rules"]:
        if any(key in t for t in titles):
            return no
    return cfg["default_no"]


def export(course_file: Path, force=False) -> Path | None:
    d = json.loads(course_file.read_text())
    cid = d["id"]
    stage = d.get("stage", {})
    name = stage.get("name") or cid
    scenes = d.get("scenes", [])
    titles = [s.get("title", "") for s in scenes]
    cfg = detect_series(name)
    if cfg is None:
        print(f"  [skip] {cid} 「{name}」不属于任何已配置系列", file=sys.stderr)
        return None
    no = series_no(cfg, name, titles)
    date = time.strftime("%Y-%m-%d", time.localtime(parse_time(d.get("createdAt"))))

    out = OUT_DIR / f"{cfg['prefix']}{no}_{cid}.md"
    if out.exists() and not force:
        return None

    lines = [
        "---",
        f'title: "{cfg["title"]} {no}：{name}"',
        'domain: "ai-learning"',
        'content_type: "course_notes"',
        f'classroom_id: "{cid}"',
        f'portal_url: "http://localhost:3000/classroom/{cid}"',
        f'generated_from: "OpenMAIC data/classrooms/{cid}.json"',
        f'created_on: "{date}"',
        "---",
        "",
        f"# {cfg['title']} {no}：{name}",
        "",
        f"> OpenMAIC 互动课堂讲义导出（{date}，共 {len(scenes)} 场景）。"
        f"配音频互动版：http://localhost:3000/classroom/{cid}",
        "",
    ]

    for s in scenes:
        lines.append(f"## 场景 {s.get('order', '?')}：{s.get('title', '')}")
        lines.append("")
        # 讲稿：合并该场景所有 speech 段落
        speeches = [a.get("text", "") for a in s.get("actions", [])
                    if a.get("type") == "speech" and a.get("text")]
        if speeches:
            lines.append("  ".join(speeches))  # 同场景讲稿连缀成段
            lines.append("")
        # 测验：题目+选项+答案+解析
        content = s.get("content") or {}
        if content.get("type") == "quiz":
            for q in content.get("questions", []):
                lines.append(f"**{q.get('id', '?')}. {q.get('question', '')}**")
                lines.append("")
                for opt in q.get("options", []):
                    mark = " ✅" if opt.get("value") in (q.get("answer") or []) else ""
                    lines.append(f"- {opt.get('value')}. {opt.get('label', '')}{mark}")
                lines.append("")
                if q.get("analysis"):
                    lines.append(f"> 解析：{q['analysis']}")
                    lines.append("")
        # 幻灯片要点（若有 slide 内容）
        if content.get("type") == "slide" and isinstance(content.get("outline"), dict):
            points = content["outline"].get("points") or []
            if points:
                for p in points:
                    lines.append(f"- {p}")
                lines.append("")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    return out


def main():
    force = "--force" in sys.argv
    files = sorted(COURSES_DIR.glob("*.json"), key=lambda p: parse_time(
        json.loads(p.read_text()).get("createdAt")))
    written = []
    for f in files:
        out = export(f, force=force)
        if out:
            written.append(out.name)
    if written:
        print(f"exported {len(written)}:")
        for w in written:
            print(f"  ai-learning/courses/{w}")
    else:
        print("nothing new (all up to date)")


if __name__ == "__main__":
    main()
