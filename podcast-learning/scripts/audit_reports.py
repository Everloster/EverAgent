#!/usr/bin/env python3
"""
audit_reports.py — podcast-learning 报告质量审计（防复发机制，2026-10-14 建立）

背景：2026-10-14 review 发现两类复发硬伤——①压缩比声明凭手感填（虚高 2-4pp）；
②frontmatter 字段复制模板残留（chapters 抄错期）。本脚本把 review 项全部机械化。

分期（按 frontmatter created）：
  v2 期    created >= V2_SINCE（2026-10-10）：全项检查，违规=ERROR（提交前必须清零）
  过渡期   2026-09-22 <= created < V2_SINCE：查文件存在/压缩比/必填字段，违规=WARN
  legacy   created < 2026-09-22：豁免（历史形态，仅统计）

检查项（v2）：v2 六章节｜压缩比声明 vs 实测(≤2pp)｜transcript/polished 文件存在｜
  duration vs 转写末段(±120s)｜必填字段｜chapters 数字开头｜wikilink 目标存在｜
  数字表首列格式

用法：
  python3 scripts/audit_reports.py            # 审计（ERROR>0 退出码 1）
  python3 scripts/audit_reports.py --fix      # 顺带自动校准压缩比声明（frontmatter+polished 头部）
  python3 scripts/audit_reports.py --strict   # WARN 也算失败
  python3 scripts/audit_reports.py <file.md>  # 只审一篇
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent      # podcast-learning/
REPO = ROOT.parent                                         # EverAgent/
REPORTS = ROOT / 'reports'
V2_SINCE = '2026-10-10'          # 第一篇完整 v2 报告（孙宇晨）创建日
TRANSITION_SINCE = '2026-09-22'  # transcript 三件套惯例成型日
V2_SECTIONS = ['⚡ 速览', '## 概览', '## 增量观点', '## 关键数字', '## Limitations', '## 思考与追问']
REQUIRED_FM = ['source_url', 'notable_correction', 'duration', 'pipeline', 'transcript_segments']
COMPRESS_TOL_PP = 2.0
DURATION_TOL_S = 120

# wikilink 目标缓存（全库 md 文件名 → 路径集合，一次构建）
def build_link_index():
    idx = {}
    for p in list(REPO.rglob('*.md')) + list((ROOT / 'reports' / 'transcripts').glob('*.txt')):
        idx.setdefault(p.stem, []).append(p)   # stem 同时覆盖 basename 去扩展名（SKILL.md / *.polished.txt 链接）
    return idx

def fm(t, key):
    m = re.search(rf'^{key}:\s*(.*)$', t, re.M)
    return m.group(1).strip().strip('"`') or None if m else None

def audit_file(path, link_idx, fix=False):
    t = path.read_text(encoding='utf-8')
    name = path.name
    errors, warns, notes = [], [], []

    created = fm(t, 'created') or '2026-01-01'
    m_nd = re.match(r'(\d{4}-\d{2}-\d{2})', name)
    name_date = m_nd.group(1) if m_nd else created
    # 分期判据：SKILL v2 显式声明（pipeline/polished_by）或文件名日期 >= V2_SINCE；
    # created frontmatter 不可信（2026-10 批量回填污染过，见 2026-10-14 review）
    is_v2 = ('SKILL v2' in t) or name_date >= V2_SINCE
    is_transition = (not is_v2) and name_date >= TRANSITION_SINCE
    if not (is_v2 or is_transition):
        return errors, warns, notes + ['legacy 豁免']

    def err(msg): errors.append(f'{name}: {msg}')
    def warn(msg): warns.append(f'{name}: {msg}')

    # --- 压缩比声明 vs 实测（v2=ERROR，过渡期=WARN）---
    m_decl = re.search(r'约 raw 的 ([\d.]+)%', t)
    h_raw, h_pol = fm(t, 'hanzi_chars_raw'), fm(t, 'hanzi_chars_polished')
    if m_decl and h_raw and h_pol:
        decl, real = float(m_decl.group(1)), int(h_pol) / int(h_raw) * 100
        if abs(decl - real) > COMPRESS_TOL_PP:
            if is_v2 and not fix:
                err(f'压缩比声明 {decl}% vs 实测 {real:.1f}%（> {COMPRESS_TOL_PP}pp）')
            elif is_v2 and fix:
                t = re.sub(r'约 raw 的 [\d.]+%（按汉字数 [\d/]+）?',
                           f'约 raw 的 {real:.1f}%（按汉字数 {h_pol}/{h_raw}）', t, count=1)
                pp = ROOT / (fm(t, 'polished_transcript_path') or '')
                if pp.exists():
                    pt = re.sub(r'约为(?:转写)?(?:全文)?的? ?[\d.]+%',
                                f'约 {real:.1f}%（按汉字数）', pp.read_text(encoding='utf-8'), count=1)
                    pp.write_text(pt, encoding='utf-8')
                path.write_text(t, encoding='utf-8')
                notes.append(f'{name}: 压缩比声明已自动校准 → {real:.1f}%')
            else:
                warn(f'压缩比声明 {decl}% vs 实测 {real:.1f}%')

    # --- transcript / polished 文件存在 ---
    for key in ('transcript_path', 'polished_transcript_path'):
        v = fm(t, key)
        if v is None:
            (err if is_v2 else warn)(f'缺 frontmatter "{key}"')
            continue
        if v in ('null', 'none') or v.startswith('/') or '，' in v or len(v) > 90:
            notes.append(f'{name}: {key} 为特例（外部路径/多件说明/null）→ {v[:60]}')
            continue
        if not (ROOT / v).exists():
            (err if is_v2 else warn)(f'{key} 文件不存在 → {v[:80]}')

    # --- duration vs 转写末段 ---
    dur, tp = fm(t, 'duration_seconds'), fm(t, 'transcript_path')
    if dur and tp and tp.startswith('reports/') and (ROOT / tp).exists():
        stamps = [int(h) * 3600 + int(m) * 60 + int(s)
                  for h, m, s in re.findall(r'\[(\d+):(\d+):(\d+) ->', (ROOT / tp).read_text(encoding='utf-8'))]
        if stamps and abs(stamps[-1] - int(dur)) > DURATION_TOL_S:
            msg = f'duration_seconds={dur} vs 转写末段 {stamps[-1]}（差 {abs(stamps[-1]-int(dur))}s）'
            if '，' in (tp or '') or len(tp) > 90:
                notes.append(f'{name}: {msg}（多件专题聚合口径，豁免）')
            else:
                (err if is_v2 else warn)(msg)

    # --- 必填字段 / chapters（v2 期）---
    if is_v2:
        for f in REQUIRED_FM:
            if fm(t, f) is None: err(f'缺 frontmatter "{f}"')
        ch = fm(t, 'chapters')
        if ch and not re.match(r'\d+', ch):
            err(f'chapters 非数字开头（疑似模板残留）→ {ch[:40]}')
        for sec in V2_SECTIONS:
            if sec == '⚡ 速览':
                if '速览' not in t: err(f'缺 v2 章节 "{sec}"')
            elif sec not in t: err(f'缺 v2 章节 "{sec}"')

    # --- wikilink 目标存在（v2 期）---
    if is_v2:
        for m in re.finditer(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]', t):
            tgt = m.group(1).strip()
            base = tgt.rsplit('/', 1)[-1]
            base = re.sub(r'\.(md|txt)$', '', base)
            if tgt and tgt not in link_idx and base not in link_idx:
                err(f'wikilink 无目标 → [[{tgt}]]')

    # --- 数字表首列格式（v2 期）：禁止纯省略号/非数字条目 ---
    if is_v2:
        for m in re.finditer(r'^\|\s*([^|\n]+?)\s*\|(?:[^|\n]*\|)+\s*$', t, re.M):
            first = m.group(1)
            if first and re.fullmatch(r'[.…]+', first):
                err(f'数字表存在非数字条目 → "{first}"')

    return errors, warns, notes

def main():
    args = sys.argv[1:]
    fix, strict = '--fix' in args, '--strict' in args
    targets = [pathlib.Path(a) for a in args if not a.startswith('--')]
    files = targets or sorted(REPORTS.glob('*.md'))
    link_idx = build_link_index()
    E, W, N = [], [], []
    for f in files:
        if not f.is_absolute(): f = ROOT / f if not f.exists() else f
        e, w, n = audit_file(f, link_idx, fix=fix)
        E += e; W += w; N += n
    print(f'审计 {len(files)} 篇：ERROR {len(E)}｜WARN {len(W)}｜提示 {len(N)}')
    for line in E: print('  ✗', line)
    for line in W: print('  ⚠', line)
    if fix and N: [print('  ↻', l) for l in N if '校准' in l]
    sys.exit(1 if E or (strict and W) else 0)

if __name__ == '__main__':
    main()
