# podcast-learning — 领域协议

> 领域：播客/访谈内容学习。**本地转写驱动**：我发链接 → 本地转写出原文 → 润色 → 总结/讨论 → 报告。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。
> **版权与引用**：见 [COPYRIGHT.md](./COPYRIGHT.md)。节目版权归主理人/嘉宾/制作方所有，本项目仅做个人学习。

---

## 工作模式：链接 → 本地转写 → 报告

用户发一个播客/视频链接（或本地音频文件），或说"上次那期继续"，按以下循环：

1. **读画像与地图** — [PROFILE.md](./PROFILE.md)、[MAP.md](./MAP.md)、[wiki/open-questions.md](./wiki/open-questions.md)
2. **下载 + 本地转写** — 用 `scripts/transcribe.py`（yt-dlp 下载音频 + **whisper.cpp** 本地转写，Metal 加速），产出 `reports/transcripts/{slug}.transcript.txt`。首次用需按 [SETUP.md](./SETUP.md) 装依赖。**B站链接例外**：yt-dlp 被 412 拦截，音频获取改走 `opencli bilibili download` + ffmpeg + whisper-cli，官方字幕作校验源（详见 [skills/transcription](./skills/transcription/SKILL.md) §一）。
3. **拉 shownotes（推荐）** — 用 WebFetch 拉小宇宙/Apple Podcasts 页面，提取**章节时间戳 + 嘉宾身份 + 书单 + 关键概念**。whisper 对人名/英文术语/数字误识别率高，shownotes 是**修正源**。
4. **润色** — 基于原始转写去口水词、断句、纠正明显错字，产出 `.{slug}.polished.txt`（与转写并列存放）。**只修表达，不改事实**；无法辨识处保留原文并标 `[?]`。
5. **按 shownotes 重组（推荐）** — 把 raw 段按 shownotes 章节时间戳归类合并，**去掉时间戳**（避免读者被时间码干扰阅读流），每节一段连续文本，加 `## 章节标题`。
6. **提取/总结** — 通读润色稿，提取核心观点/关键人物/新概念/关键数字/金句。
7. **写报告** — 存 `reports/`，带 frontmatter，结尾必带「思考与追问」三问。
8. **沉淀** — 更新 wiki（人物/概念页）、未解问题汇入 open-questions。
9. **更新画像** — 把新关注的节目/人物/主题写回 PROFILE（仅凭用户真实表达，禁止臆测）。

> "继续讨论"场景：用户读完转写/报告后追问，围绕转写原文与已查证事实展开，不引入转写外的编造内容。

---

## 催更：精选节目单刷新（用户主动触发，无 cron）

用户说「刷一下播客 / 催更 / 这周有什么新集」时：

1. 跑 `python3 scripts/fetch_show_indexes.py` 全量刷新 51 档索引（~2 分钟，51 档 × 0.3s 限速）
2. 按 stdout `NEW |` 行汇总，**按 PROFILE.md 兴趣排序**呈现（关注节目/人物优先，不按节目原序）
3. `SUSPECT |` 行 = 疑似 RSS 链接变更的误报（新增占比 >30% 自动降级），人工核对，不当新集汇报
4. 问用户要不要转写哪几集（**不自动转写**）

> 2026-08-31 起 cron 退役：原周一 09:47 周更 cron 挂在当时的会话里，会话结束即失效，从未持久化。索引 diff 用 guid+链接双键（guid 藏在标题单元格 HTML 注释），防单集链接换域名时全量误报 NEW + 人工状态丢失。

---

## 领域特化

- **转写后端**：`scripts/transcribe.py`（本地 **whisper.cpp / ggml-large-v3 / Metal 加速** / 全程离线）。本机实测 **1h53min 音频 7m30s 墙钟**（约 15× 实时），比 faster-whisper CPU int8 估算快 25-50 倍。详细安装见 [SETUP.md](./SETUP.md)。
- **报告类型**：`reports/`（单期总结/跨期专题/概念追踪，同目录按 frontmatter `report_type` 区分）。
- **特化要求（关键）**：
  - **转录中未出现的引用、数据、人物言论禁止推测**
  - **关键引用保留原文**（哪怕标点残缺）
  - **转录质量差时在 Limitations 标注，不强行总结**
  - **润色只改表达不改事实**
  - **whisper 对中英人名/英文术语/关键数字的误识别率高**（实测："李继刚"→"李金刚"、"GB"→原吞字、"860 亿"→"861"），**必须以 WebFetch 拉取的 shownotes 二次校验**

---

## 文件命名规范

> 2026-07-18 重构：旧格式 `{date}_{platform}_{show_id}_{slug}` 中 show_id（BV 号/episode hash）可读性太差，已废弃。**show_id 不再入文件名，溯源靠 frontmatter `source_url`。**

报告 / 转录 / 润色稿三件套共享同一前缀：

```
{YYYY-MM-DD}_{platform}-{show_slug}_{guest_or_topic}.{md|transcript.txt|polished.txt}
```

| 字段 | 取值规则 | 示例 |
|------|---------|------|
| `{YYYY-MM-DD}` | 节目发布日期（**不是处理日期**）| `2026-07-09` |
| `{platform}` | `xiaoyuzhou` / `bilibili` / `youtube` / `local` | `xiaoyuzhou` |
| `{show_slug}` | **节目的可读 slug**（小写连字符，拼音或英文），同一节目固定同一 slug | 明镜与点点→`mingjing-diandian`、课代表立正→`kedaibiao-lizheng`、CLS同学→`cls-tongxue`、鹿哥Gustav→`luge-gustav` |
| `{show_slug}` 例外 | 跨节目综合用 `multi` | `xiaoyuzhou-multi` |
| `{guest_or_topic}` | **嘉宾 slug**（小写连字符）；无嘉宾（单口/综合）用**主题 slug** | `wangxiaochuan` / `lijigang` / `breakfast` / `notes` |

### 命名实例

| 文件 | 类型 | 命名依据 |
|------|------|---------|
| `2026-06-18_xiaoyuzhou-mingjing-diandian_wangxiaochuan.md` | 报告 | 王小川作客《明镜与点点》 |
| `2026-06-20_bilibili-cls-tongxue_hangye-bangdan.md` | 报告 | CLS 同学单口 → 主题 slug |
| `2026-06-21_xiaoyuzhou-multi_notes.md` | 报告 | 3 期跨节目综合 → `multi` + `notes` |
| `2026-07-09_xiaoyuzhou-mingjing-diandian_lijigang.md` | 报告 | 李继刚作客《明镜与点点》 |
| `2026-07-09_xiaoyuzhou-mingjing-diandian_lijigang.transcript.txt` | 原始转录 | 5,372 段，**带时间戳** |
| `2026-07-09_xiaoyuzhou-mingjing-diandian_lijigang.polished.txt` | 润色稿 | 按 shownotes 36 章节，**不带时间戳** |
| `2026-07-14_bilibili-luge-gustav_breakfast.md` | 报告 | 鹿哥Gustav 单口 → 主题 slug |

### 反例（不要用）

| 反例 | 错误原因 |
|------|---------|
| `2026-07-09_xiaoyuzhou_6a4b22ad_lijigang.md` | **旧格式**：show_id（hash/BV号）入文件名，可读性差——已废弃 |
| `2026-07-09_xiaoyuzhou_mingjing-reading.md` | slug 写"mingjing-reading"是错的——mingjing 是主持不是嘉宾；show_slug 缺失 |
| `2026-07-09_xiaoyuzhou-mingjing-diandian.transcript.txt` | transcript/polished 缺 guest_or_topic，无法与报告关联 |
| `2026-07-09_podcast-mingjing-diandian_lijigang.md` | platform 字段不标准化（podcast 太宽泛） |
| `2026-07-09_xiaoyuzhou-mingjing-diandian_李继刚.md` | slug 不要用中文（跨平台兼容性） |

---

## 转录与润色规范

### transcript.txt（原始转录）

- **保留**所有 whisper 原始输出，包括时间戳、同音误识别、标点缺失
- **头部**加 6-10 行 metadata（节目/嘉宾/平台/时长/转录 pipeline）
- **尾部**删除小宇宙自动加的 4 段片尾广告（"谢谢大家观看 欢迎订阅..."）
- **标点**：whisper.cpp 中文输出无自动标点（与 faster-whisper 一致），**不补**

### polished.txt（润色稿）

- **去掉时间戳**（避免读者被时间码干扰）
- **按 shownotes 章节重组**：每节一段连续文本 + `## 章节标题` + `---` 分隔
- **删除**：广告、口水词、明显无意义重复
- **修正**：仅修**能确定**的同音误识别（如"黑心流"→"黑天鹅"），并在校正清单中列出
- **标记**：不确定项加 `[?]`（如"携带码[?]"）
- **保留**：所有口语化表达、不修标点（除非上下文明显需要）

### 转录字数统计（防 wc -c 陷阱）

- `wc -c` 返回**字节数**（含时间戳 `[HH:MM:SS -> HH:MM:SS]` 和全角空格），**不是字数**
- 正确做法：用 `re.findall(r'[一-鿿]', text)` 统计**汉字字数**
- 报告中务必区分：
  - `hanzi_chars_raw` / `hanzi_chars_polished`（汉字字数）
  - `total_chars_raw` / `total_chars_polished`（含标点+英文+数字）
  - `transcript_segments`（段数）
- **语速估算**：`speech_rate_cjk = hanzi_chars / (duration_seconds / 60)`（中文播客正常 300-400 字/min）
- **音频大小估算**：`audio_size_mb × 277 字/MB ≈ 实际字数`（128kbps mp3 系数）

---

## shownotes 拉取与使用

### 为什么需要 shownotes

1. **修正 whisper 误识别**（人名/英文术语/书名/数字）
2. **识别节目形式**（对谈 vs 单口 vs 多人圆桌）—— whisper 默认不区分说话人
3. **获取章节时间戳**—— polished 重组的依据
4. **获取完整书单**—— 报告"引用书目"段
5. **获取嘉宾身份**—— wiki 实体页

### 拉取方法

```bash
# WebFetch 拉小宇宙 episode 页面
WebFetch https://www.xiaoyuzhoufm.com/episode/{episode_id} "提取：1) 标题/时长/发布者/发布日期 2) 节目描述 3) 时间轴（完整章节时间戳）4) 嘉宾信息 5) 主题标签 6) 提到的书"
```

### 使用规则

1. **章节时间戳 → polished 分节依据**：把 raw 段按时间区间归入对应章节，合并为连续段落
2. **嘉宾/书单/概念词 → 报告"关键人物"和"引用书目"段**
3. **修正 whispection 的同音误识别**（如"李金刚"→李继刚、"金关涛"→金观涛、"GB"→GEB）
4. **所有修正必须在报告 Limitations 段标注**（来源：shownotes）

### 反例（不要做）

- ❌ **仅靠转录 + LLM 总结** → 嘉宾身份/书名/章节大概率错
- ❌ **用 WebSearch 模糊搜** → 小宇宙内容不在公网搜索索引
- ❌ **不看 shownotes 就写报告** → 报告质量必然低，且无法修正

---

## 转写后端（whisper.cpp）经验

### 性能

| 音频 | 时长 | 墙钟 | 速度 |
|------|------|------|------|
| 中文 12.3s | 0.2min | 1.3s | 9.5× 实时 |
| 中文 6815s (本期) | 113min | 7m30s | 15× 实时 |

比 faster-whisper CPU int8（0.25-0.5× 实时）快 25-50 倍。

### 命令

```bash
whisper-cli -m ~/workspace/whisper.cpp/models/ggml-large-v3.bin \
    -l zh -f audio.mp3 \
    -oj -of output_prefix -np
```

- `-m`：模型路径（推荐 large-v3 / 中文 2.9GB）
- `-l zh`：语言（auto 也能用但 zh 更准）
- `-oj -of prefix`：JSON 输出到 `prefix.json`（含时间戳 + 文本）
- `-np`：抑制 whisper 自带进度/计时打印

### 软链设置

```bash
ln -sf ~/workspace/whisper.cpp/build/bin/whisper-cli /opt/homebrew/bin/whisper-cli
ln -sf ~/workspace/whisper.cpp/build/bin/whisper-server /opt/homebrew/bin/whisper-server
ln -sf ~/workspace/whisper.cpp/build/bin/whisper-bench /opt/homebrew/bin/whisper-bench
```

### 已知局限

1. **无说话人区分**（diarization）—— 对谈节目需依赖 shownotes 识别嘉宾
2. **中英人名/术语/书名误识别率高**（"李继刚"→"李金刚"）—— 必须以 shownotes 校验
3. **关键数字吞字**（"860 亿"→"861"）—— 报告里要标"未在 polished 中修改"
4. **不自动加中文标点**—— 保留原貌，不补
5. **长音频 + 音乐/过场段易触发循环幻觉**（2026-08-23 硅谷101 E247 实例：无 VAD 时约 39 分钟起整段循环输出无关广告词，音频本身完好）。**解法**：`transcribe.py --whisper-args "--vad -vm ~/workspace/whisper.cpp/models/for-tests-silero-v6.2.0-ggml.bin"` 重跑——VAD 切掉非语音段，循环不再点火。`transcribe.py` 已支持 `--whisper-args` 透传（2026-08-23 新增）

---

## 报告 frontmatter 模板

```yaml
---
title: "标题"
domain: "podcast-learning"
report_type: episode_summary   # 或 cross_episode / concept_tracking
source: 小宇宙播客              # 或 bilibili / youtube / 本地音频
source_url: https://...
show: "节目名"
episode: "（单期 / Vol.XX）"
host: "主持（如有）"
guest: "嘉宾（如有）"
duration: "1h54m"
duration_seconds: 6815
transcript_segments: 5372
hanzi_chars_raw: 35430
hanzi_chars_polished: 35897
total_chars_raw: 42075
total_chars_polished: 43102
audio_size_mb: 128
speech_rate_cjk: "312 字/min"
chapters: 36
polished: true
polished_by: "Claude (MiniMax-M3)"
polished_at: 2026-07-09
status: archived
created: 2026-07-09
updated_on: 2026-07-09
transcript_path: reports/transcripts/{slug}.transcript.txt
polished_transcript_path: reports/transcripts/{slug}.polished.txt
pipeline: yt-dlp → ffmpeg mp3 → whisper.cpp / ggml-large-v3 / Metal / 7m30s → WebFetch shownotes → Claude 按章节重构
source_shownotes_chapters: true
notable_correction: "whisper 误识别 X → 依 shownotes 修正"
---
```

---

## 报告结构（episodic_summary 模板）

1. **概览**（核心 3-5 条 bullet）
2. **章节地图**（shownotes 章节时间戳 + 标题 + 核心命题）
3. **关键人物**（嘉宾 + 提及的真人真名，附身份）
4. **主要话题**（按主题归并，子节）
5. **引用书目**（shownotes 给的完整书单）
6. **关键概念词**（concept 词表）
7. **关键观点**（原话引用，标"原话"）
8. **关键数字**（含 audio_size × 277 = 字数估算）
9. **Limitations**（whisper 误识别 / 说话人缺失 / 数字吞字等）
10. **思考与追问**（3 问，与 open-questions.md 同步）

---

## 完成后自检

```bash
python3 ../scripts/reindex.py
```

逐项核对：
- [ ] 报告 / transcript / polished 三件套命名一致（同一前缀）
- [ ] 报告 frontmatter 路径指向真实文件
- [ ] 报告章节地图与 polished 实际分节一致
- [ ] 报告 Limitations 段列出本场所有 whisper 误识别
- [ ] wiki 概念 / 实体页引用报告文件名
- [ ] open-questions 汇入新问
- [ ] log.md 追加 ingest 条目

提交规范见根 [AGENTS.md](../AGENTS.md) 与 [docs/PROTOCOL_COMMON.md](../docs/PROTOCOL_COMMON.md)。
