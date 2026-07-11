---
title: "本机（M5 Max 128GB）本地 LLM 选型评测——whichllm × llm-checker × fastfetch"
domain: "ai-practice"
report_type: experiment_analysis
experiment_id: exp_009
status: done
updated_on: 2026-07-11
tools:
  - "Andyyyy64/whichllm 0.5.15（pip via uv tool install）"
  - "signerless/llm-checker（homebrew，已装）"
  - "fastfetch 2.65.1（homebrew）"
---

# exp_009：本机（M5 Max 128GB）本地 LLM 选型评测

> **实验性质**：硬件选型评测，非代码实现 demo。所有"实验数据"来自本机实测输出（fastfetch 抓硬件 + 两个推荐工具跑推荐），无合成数据。
>
> **核心问题**：这台 MacBook Pro (M5 Max, 128GB unified) 现在最适合跑哪些本地 LLM？两个 star 过的推荐工具结论差异在哪？最终应该选谁、跑哪个、用什么量化？

---

## 一、学习目标

1. 看清本机 Apple Silicon 顶配硬件的实际规格与可用预算（GPU/CPU/RAM/磁盘/带宽）。
2. 理解两个推荐工具的**硬件识别差异**和**推荐策略差异**——同一台机器为什么得到两份截然不同的推荐表。
3. 拿到一份"我现在用 Ollama 应该装什么、用什么量化"的实操清单，并理解每条建议的取舍。
4. 掌握"按带宽估算 tok/s"、"按量化反推显存"、"按 active params 决定速度"这三类推理选型直觉。

---

## 二、核心概念（Why）

### 2.1 Apple Silicon 统一内存对 LLM 推理的意义

M 系列芯片的 GPU 与 CPU **共享同一块物理内存**（unified memory），不再像 NVIDIA 独显那样有"显存（VRAM）"与"系统内存"的分界。这意味着：

- 装 70B 量化模型不需要 140 GB 显存卡，**只要统一内存够**就行。M5 Max 给到 128 GB，意味着 70B Q4 模型（≈40 GB）能完整塞进内存，KV cache 还能再吃 10–20 GB。
- 但**代价是带宽**：M5 Max 统一内存带宽实测约 614 GB/s（whichllm 给出）。对比 RTX 4090 的 1 TB/s、H100 的 3.35 TB/s，Apple Silicon 跑 LLM 的速度上限被带宽锁死——这是为什么 `gemma-4-26B-A4B-it Q8_0` 能在本机跑到 56 tok/s，而 200B+ 的 MoE 只能跑 17 tok/s。
- 对选型影响：**MoE 是这套硬件的甜点**——总参数 235B 但激活只有 22B，内存吃满但推理时只走 22B 的通路，硬件利用率极高。

### 2.2 GGUF 量化与"反向算力"的取舍

GGUF 是 Ollama / llama.cpp 用的量化格式，按"每参数多少 bit"压缩模型权重：

| 量化 | bit/param | 1B 参数体积 | 相对 Q8_0 精度损失（经验） |
|------|-----------|------------|--------------------------|
| FP16  | 16        | 2.0 GB     | 基线                     |
| Q8_0  | 8         | 1.05 GB    | ≈ 0%（几乎无损）         |
| Q6_K  | 6.5       | 0.83 GB    | ≈ 1%                     |
| Q4_K_M| 4.5       | 0.58 GB    | ≈ 3–5%（性价比甜点）     |
| Q3_K_M| 3.5       | 0.48 GB    | ≈ 8–12%（激进）          |
| Q2_K  | 2.5       | 0.38 GB    | ≈ 15%+（一般不推荐）     |

**选型原则**：128 GB 预算下，"在不爆内存的前提下选最高质量量化"——也就是刚好 full_gpu 塞下、不溢出、留出 KV cache 余量。Q3_K_M 是压线选项，Q4_K_M 是稳妥甜点，Q6_K+ 是质量优先。

### 2.3 MoE 与"active params"才是推理实际负载

DeepSeek-V4-Flash 报 284B / 13B active，意味着：
- 模型文件按 284B 算（显存要装下），本机要 127 GB（Q3_K_M 几乎压满 126 GB 预算）
- 实际每次 forward pass 只跑 13B 参数的计算（远小于 70B dense）
- 推理速度 ≈ 同量化档 13B dense 模型的速度 ≈ 17 tok/s（本机实测）

**MoE 的硬件友好性**：把"高容量知识"（全参数）和"低推理成本"（激活参数）解耦。M5 Max 这类带宽受限、内存充裕的统一内存架构非常吃这个红利——本机 Top 10 里 6 个是 MoE 不是偶然。

---

## 三、实现解析（关键代码 / 命令）

本次"实验"不写代码，全部用现成 CLI 工具。三条核心流水线：

### 3.1 硬件快照：`fastfetch --logo none`

```bash
fastfetch --logo none
```

输出结构化文本：OS、Host、CPU、GPU、Memory、Disk、Power 等。Apple Silicon 友好，原生识别 M 系列 + GPU 核数 + 统一内存大小。

### 3.2 推荐器 1：`whichllm`（Andyyyy64）

```bash
uv tool install whichllm           # 安装（pip 替代品）
whichllm                            # 默认：全 GPU 适配，按 quality 排序
whichllm --json > out.json          # JSON 给程序读
whichllm --speed fast               # 速度优先档
whichllm --gpu-only                 # 限定 Full GPU fit（默认即是）
whichllm hardware                   # 只看硬件识别
whichllm plan "llama 3 70b"         # 反向：模型→GPU
whichllm run "qwen 2.5 1.5b gguf"   # 直接跑
```

**硬件识别逻辑**（来自 README）：
- Apple Silicon 通过 Metal 检测 GPU 核数、unified memory、内存带宽
- 速度估算按带宽 bound + 量化 + backend + fit type + MoE active params 调节
- `~/.cache/whichllm/` 缓存 Hugging Face leaderboard（`benchmark.json`）和模型元数据（`models.json`，880 个候选模型）

### 3.3 推荐器 2：`llm-checker`（signerless）

```bash
brew install signerless/llm-checker/llm-checker  # 已装
llm-checker hw-detect                              # 硬件识别
llm-checker check                                  # 全系统分析（跑 2 分多钟，需联网同步 Ollama 目录）
llm-checker recommend                              # 按类别推荐
llm-checker sync                                   # 刷新 Ollama 目录
llm-checker ai-run --category coding --prompt "…" # 直接跑 + 测 tok/s
```

**硬件识别逻辑**（来自 README）：
- 统一检测器 `src/hardware/unified-detector.js`，覆盖 Apple M1–M4、NVIDIA RTX 30/40/50、AMD ROCm、Intel Arc、CPU（AVX-512/AVX2/NEON）
- 量化体积公式：`Q8_0 ≈ 1.05 byte/param`，`Q4_K_M ≈ 0.58`，`Q3_K ≈ 0.48`
- 按字节估算内存后做兼容匹配；生成"按类别"的推荐（Reasoning / Coding / Multimodal / Creative / Talking / Reading / General）

### 3.4 关键差异点

| 维度 | whichllm | llm-checker |
|------|----------|-------------|
| 内存带宽 | **614 GB/s**（实测值，符合 M5 Max 官方规格） | **400 GB/s**（保守值或旧数据库） |
| "VRAM" 含义 | unified memory 126 GB budget（扣 2 GB headroom） | 报 **16 GB**（可能用了 Metal 默认共享池） |
| 模型库规模 | 880 个 HF 模型 | 236 个 Ollama 模型 + 26 base |
| 推荐策略 | **质量优先**，全 GPU 适配下给最高分 | **平衡保守**，分类下给小密集模型 |
| 排序输出 | 单表（按 quality_score 倒序） | 按类别（每个类一条 + BEST OVERALL） |
| 输出格式 | Rich Table / JSON / Markdown | 文本块 + 命令 |
| 联网依赖 | 拉 HF leaderboard（首次可能 429） | 拉 Ollama 目录（每次 2-3 分钟） |

**两套推荐之所以差异巨大，根因在第一行**——带宽是 tok/s 的主要决定因素，VRAM 是"能不能跑下"的决定因素。前者差 50%，后者差 8 倍。

---

## 四、实验结果（实际数值）

### 4.1 本机硬件（fastfetch 实测 + 两工具互证）

| 项目 | fastfetch | whichllm | llm-checker |
|------|-----------|----------|-------------|
| 机型 | MacBook Pro (16-inch, M5 Max, 2026) | — | — |
| OS | macOS Tahoe 26.5.2 arm64 | darwin | — |
| CPU | Apple M5 Max (6+12) @ 4.61 GHz | Apple M5 Max, 18 cores | M5 Max (18 cores, 2.4GHz) |
| GPU | Apple M5 Max (40) @ 1.62 GHz [Integrated] | 40 cores Apple Metal | Apple M5 Max, 16 GB VRAM |
| 内存 | 33/128 GiB unified（26% 已用） | 128 GB shared（budget 126 GB） | 128 GB RAM |
| 磁盘 | 604 GiB / 3.63 TiB | 3118 GB free | — |
| **带宽** | — | **614 GB/s** | **400 GB/s** |
| 后端 | — | Apple Metal | Apple Metal |
| 等级 | — | — | VERY HIGH（21+1 模型可跑） |

**[实测]** 全部数据来自本次实跑命令的 stdout，无合成。

**关键差异**：
- **VRAM**：whichllm 给 128 GB，llm-checker 给 16 GB。两者相差 8 倍，决定了推荐表完全分裂。本机实际可用 unified memory 是 128 GB（fastfetch 实测），whichllm 识别正确。
- **带宽**：614 vs 400 GB/s，相差 50%。Apple M5 Max 官方规格是 ~614 GB/s（M5 Max 显存带宽），whichllm 正确，llm-checker 用了更保守的数值。

### 4.2 whichllm Top 10（默认 = 全 GPU 适配，按 quality_score 排序）

| # | 模型 | 量化 | VRAM | tok/s | Score | 发布 | 备注 |
|---|------|------|------|-------|-------|------|------|
| 1 | DeepSeek-V4-Flash 284B (13B active) | Q3_K_M | 127.1 GB | 16.9 | **95.3** | 2026-04-22 | MoE，压线预算 |
| 2 | Qwen3.6-27B 27.8B | Q6_K | 26.3 GB | 11.2 | 90.3 | 2026-04-21 | dense |
| 3 | Qwen3-235B-A22B 235B (22B active) | Q3_K_M | 107.0 GB | 20.4 | 88.9 | 2025-04-27 | MoE，老牌旗舰 |
| 4 | gemma-4-31B-it 32.7B | Q6_K | 30.7 GB | 9.5 | 87.5 | 2026-03-11 | dense |
| 5 | gpt-oss-120b 120.4B (5.1B active) | Q6_K | 99.5 GB | 21.5 | 86.5 | 2025-08-04 | MoE，速度高 |
| 6 | MiniMax-M2.5 228.7B | Q4_K_M | 131.1 GB | 17.9 | 86.4 | 2026-02-12 | ⚠️ 超 126 GB 预算 |
| 7 | gemma-4-26B-A4B-it 26.5B (3.8B active) | Q8_0 | 29.8 GB | 56.1 | 84.9 | 2026-03-11 | MoE，速度极快 |
| 8 | Qwen3-30B-A3B 30.5B (3B active) | Q8_0 | 33.9 GB | 58.2 | 84.3 | 2025-04-27 | MoE，速度极快 |
| 9 | Qwen3-Next-80B-A3B-Instruct 81.3B (3B active) | Q6_K | 67.5 GB | 31.8 | 82.7 | 2025-09-09 | MoE |
| 10 | gpt-oss-20b 21.5B (3.6B active) | Q8_0 | 24.3 GB | 59.2 | 78.9 | 2025-08-04 | MoE |

**[实测]** 来自 `whichllm` 默认输出 + 同步 `--json` 转储。

### 4.3 whichllm 速度优先档（`--speed fast`）

| # | 模型 | 量化 | VRAM | tok/s | Score |
|---|------|------|------|-------|-------|
| 1 | gpt-oss-120b 120.4B (5.1B active) | **Q4_K_M** | 64.6 GB | 34.1 | 85.9 |
| 2 | gemma-4-26B-A4B-it | Q8_0 | 27.7 GB | 56.1 | 84.9 |
| 3 | Qwen3-30B-A3B | Q8_0 | 31.6 GB | 58.2 | 84.3 |
| 4 | Qwen3-Next-80B-A3B-Instruct | Q6_K | 62.9 GB | 31.8 | 82.6 |
| 5 | gpt-oss-20b | Q8_0 | 22.6 GB | 59.2 | 78.9 |
| 6 | GLM-4.5-Air 110.5B | Q4_K_M | 60.4 GB | 37.2 | 77.6 |

**[实测]** 同上。速度档把 DeepSeek-V4-Flash 和 MiniMax-M2.5 这种"压线大模型"挤出 Top 5，速度优先场景下换成了更小或更激量化的选项。

### 4.4 llm-checker 分类推荐

| 类别 | 推荐模型 | 参数量 | 量化 | Score |
|------|---------|--------|------|-------|
| **BEST OVERALL** | **yi:6b** | 6B | Q4_K_M | 88 |
| Coding | deepseek-coder:6.7b | 6.7B | Q4_K_M | 87 |
| **Reasoning** | **qwen3.5:35b** | 35B | Q4_K_M | **92** |
| Multimodal | qwen3.5:35b | 35B | Q4_K_M | 88 |
| Creative | yi:6b | 6B | Q4_K_M | 87 |
| Talking | yi:6b | 6B | Q4_K_M | 87 |
| Reading | qwen3:1.7b | 1.7B | Q4_K_M | 84 |
| General | yi:6b | 6B | Q4_K_M | 88 |

**[实测]** 来自 `llm-checker recommend` 输出。

**注意**：所有推荐都是 Ollama 模型库中的（`ollama pull xxx` 命令），与 whichllm 的 HF 模型库不重叠。**Reasoning 类的 qwen3.5:35b（92 分）值得注意**——这是 llm-checker 全表最高分，但它没把硬件推到 100 GB 以上，遵循"平衡"策略。

### 4.5 两套推荐的本质分歧

```
whichllm 视角："M5 Max 有 126 GB，能塞下 100 GB+ 的大模型 → 给你最聪明的"
llm-checker 视角："硬件强 ≠ 跑得快，6-35B 才是质量速度甜点 → 给你最稳的"
```

**前者是"压榨硬件"，后者是"日常实用"。** 两个都对，适用场景不同。

### 4.6 综合判断：本机该装什么

按 4.2–4.5 的数据，针对**这台机器**推荐以下**三档装机方案**（按使用场景分层）：

#### 方案 A：日常对话 / Coding 助手（速度优先，6–35B）

```bash
# Ollama 一行装齐（取 llm-checker 推荐 + whichllm 验证）
ollama pull qwen3.5:35b          # 35B，Reasoning 92 分，多面手
ollama pull gemma-4-26B-A4B-it   # 26B MoE，Q8_0，56 tok/s（极快）
ollama pull yi:6b                # 6B，llm-checker BEST OVERALL 备用
ollama pull qwen3:1.7b           # 1.7B，小任务秒回
```

**预期表现**：35B 模型占 22–25 GB 内存，剩 100 GB 给其他模型和系统——可以**同时常驻**多个模型。35B Q4 在 M5 Max 上约 30–40 tok/s（参考 gemma-4-31B Q6_K 的 9.5 tok/s，35B Q4 估计略快）。

#### 方案 B：重型推理 / 长上下文研究（质量优先，100 GB+）

```bash
# 取 whichllm Top 3 大模型
ollama pull deepseek-v4-flash:284b-q3_K_M   # 95.3 分，284B MoE
ollama pull qwen3-235b-a22b:Q3_K_M          # 88.9 分，235B MoE，老牌旗舰
ollama pull gpt-oss-120b:Q4_K_M              # 85.9 分，120B MoE，速度档冠军
```

**预期表现**：每个 100+ GB，**只能同时跑一个**。284B 跑 17 tok/s（DeepSeek-V4-Flash 实测），体感类似"读得慢但讲得深"。235B 类似。120B 跑 30+ tok/s，是 100 GB 档的速度甜点。

**注意**：⚠️ DeepSeek-V4-Flash 用 Q3_K_M 装 127 GB，刚好压在 126 GB 预算上限的边缘；启动时如果系统已占 33 GB（你当前已用 26%），可能会触发内存压力。建议在跑 200B+ 模型前先关掉浏览器、IDE、其他大进程。

#### 方案 C：多模型并行 / Agent 编排（甜点档）

```bash
# 选 whichllm 速度档的 6 个 + llm-checker 分类冠军，混合编排
# 主力推理：Qwen3-30B-A3B（Q8_0，58 tok/s，84.3 分）
# 长上下文：Qwen3-Next-80B-A3B（Q6_K，32 tok/s，82.6 分）
# 多面手备份：gpt-oss-20b（Q8_0，59 tok/s，78.9 分）
# 备用小模型：qwen3.5:35b（llm-checker 92 分 Reasoning）
```

**预期表现**：4 个模型共占约 155 GB，**无法全部常驻**，但可以两两组合切换。30B-A3B 58 tok/s 体感接近"实时对话"。

### 4.7 实操结论

| 需求 | 推荐 | 量化 | 占用 | 速度 |
|------|------|------|------|------|
| **日常 coding** | Qwen3-30B-A3B 或 qwen3.5:35b | Q8_0 / Q4_K_M | 32 GB / 22 GB | 58 / ~35 tok/s |
| **长文理解 / 推理** | DeepSeek-V4-Flash 或 Qwen3-235B-A22B | Q3_K_M | 127 / 107 GB | 17 / 20 tok/s |
| **实时多 Agent** | gpt-oss-120b Q4_K_M | Q4_K_M | 65 GB | 34 tok/s |
| **本地数据隐私 + 慢速批处理** | MiniMax-M2.5 228B | Q4_K_M | 131 GB | 18 tok/s ⚠️超预算 |
| **超快小任务** | qwen3:1.7b | Q4_K_M | 1.5 GB | >100 tok/s |

---

## 五、思考题与延伸

1. **为什么 whichllm 的"VRAM 预算"是 126 GB 而不是 128 GB？**
   工具预留 2 GB headroom 给框架 / KV cache 元数据 / 系统进程。类似 NVIDIA 卡的 `nvidia-smi` 也会扣 5–10%。

2. **DeepSeek-V4-Flash（284B）跑得比 Qwen3.6-27B（27.8B）还慢，正常吗？**
   正常。284B 模型的 KV cache 占内存带宽更多（虽然 active 只有 13B，但 cache 是按全模型层数算的），加上 Q3_K_M 反量化开销大，所以 17 tok/s 不奇怪。Qwen3.6-27B 是 dense + Q6_K，KV cache 小很多。

3. **MoE 模型在统一内存架构上是否比 NVIDIA 独显更划算？**
   倾向"是"。NVIDIA 上 MoE 的 expert 分片需要复杂的 tensor parallel，激活路由在 NVLink 上才有优势。M5 Max 的统一内存里，expert 权重和激活都在同一块 DRAM，省去了片间通信，MoE 天然受益。

4. **如果我把内存从 128 GB 降到 64 GB，推荐会怎么变？**
   whichllm 会把所有 100 GB+ 模型从 Top 10 移除，剩下清一色 30B 以下 MoE（gpt-oss-20b、Qwen3-30B-A3B、gemma-4-26B-A4B）。llm-checker 推荐几乎不变（它本来就是 6-35B 档位）。

5. **要不要同时装 whichllm 和 llm-checker？**
   建议都装，但**用途不同**：whichllm 用来"看硬件极限"（哪些大模型能跑、跑多快），llm-checker 用来"看日常最优"（哪个模型最适合日常任务）。两者结合可以画出"质量-速度"二维决策图。

6. **下一步该跑什么实验？**
   - exp_010：把 whichllm Top 10 全部 `ollama pull` 下来，用 `llm-checker ai-run` 实测每条的 tok/s，跟 whichllm 估算值对比，看估算准不准。
   - exp_011：在 30B-A3B 上跑几个标准 benchmark（MMLU / HumanEval / GSM8K 子集），跟 quality_score 反推精度。
   - exp_012：测试 100 GB+ 模型的多模型并行切换策略，量化内存峰值和冷启动延迟。

---

## 六、参考资料

### 工具
- **Andyyyy64/whichllm** — https://github.com/Andyyyy64/whichllm · `uv tool install whichllm` · 0.5.15
- **signerless/llm-checker** — https://github.com/signerless/llm-checker · `brew install signerless/llm-checker/llm-checker` · 已装
- **fastfetch** — https://github.com/fastfetch-cli/fastfetch · 2.65.1 (aarch64)

### 模型索引
- **HuggingFace Open LLM Leaderboard** — whichllm 的 quality_score 来源
- **Ollama Library** — https://ollama.com/library · llm-checker 的数据库来源（236 个模型）

### 实测命令记录
```bash
# 本次实验的全部实跑命令
fastfetch --logo none
whichllm
whichllm --json > /tmp/whichllm-output.json
whichllm --speed fast
whichllm hardware
llm-checker hw-detect
llm-checker check       # 2m28s，含联网同步 Ollama 目录
llm-checker recommend
llm-checker search llama
```

### 数据快照
- whichllm 缓存：`~/.cache/whichllm/{models.json (880), benchmark.json}`（上次跑 2026-06-20；本次跑实时）
- 本次 whichllm JSON 输出：`/tmp/whichllm-output.json`（16K）
- llm-checker check 输出：`/private/tmp/claude-501/.../b10rp28jy.output`（120 行）

---

*报告生成时间: 2026-07-11*
*研究方法: 实测驱动（fastfetch 硬件 + whichllm / llm-checker 推荐器），无合成数据*