---
title: "vLLM 调度器：continuous batching 的真身（课论断 ↔ 源码对照篇）"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-09-09"
---

# vLLM 调度器：continuous batching 的真身（课论断 ↔ 源码对照篇）

> 本文是 vLLM 源码级学习长线（计划见 `roadmap/vLLM_源码级学习计划_20260821.md`）的**阶段 1 产出**。
> **版本坐标**：本地 clone `../vllm`，checkout 在 **v0.27.1**（commit `6e448d0`）。所有 `file:line` 证据以该 tag 为准；三路并行源码勘察 + 主会话汇总复核。
> **读法**：本报告配合 OpenMAIC 第二节概念课《调度器：continuous batching 的真身》（`quhgC1KncC`）食用——课给了直觉地图，本文逐条把地图对到源码地形上。**最大的发现写在前面：课的方向全对，但相当一部分机制细节是 V0 时代的心智模型**，v0.27.1 的 V1 已经长成了另一副更锋利的骨架。

---

## 一、课论断 ↔ 源码真相对照表（本文灵魂）

第二节概念课的五条核心论断，逐条验证。这张表本身就是「概念课开路 → 源码跟进」学习方法的第一次实战记录。

| # | 课的论断 | 源码真相 | 裁决 |
|---|---|---|---|
| 1 | 调度器每个 step 检查谁生成了结束符，移出完成的请求 | **EOS/长度在模型执行之后判**：`update_from_output()`（`scheduler.py:1670`）逐 token 调 `check_stop()`（`utils.py:94-130`），移出 RUNNING 在 `scheduler.py:1946-1948`，不在 `schedule()` 里 | 方向对，位置错 |
| 2 | 完成的请求立即退出，释放 KV Cache | 成立但更精细：`_free_request()`（`scheduler.py:2300-2327`）释放块，`finished_req_ids` 随**下一个 step** 的 SchedulerOutput 带给 worker（`:1218-1222`）；**stop string 例外**——它在**前端** detokenizer 判（`output_processor.py:655-704`），触发则反发 abort | 方向对，发现双屋檐 |
| 3 | 抢占有 RECOMPUTE 和 SWAP 两种 | **SWAP 已死**：全仓 `grep -ri swap vllm/v1/` 零命中，`PreemptionMode` 无任何引用。V1 只有 recompute：释放全部 KV（`:1290`）、`num_computed_tokens=0`（`:1294`）、头插回 waiting 队头（`:1314`） | **课过时**（V0 记忆） |
| 4 | max_num_seqs / max_num_batched_tokens 两个旋钮 | 成立，且有**第三个旋钮** `long_prefill_token_threshold`（`config/scheduler.py:70`）单请求单步再切一刀；`max_num_batched_tokens` 实际映射为 `max_num_scheduled_tokens`（`scheduler.py:110-114`） | 对，但少讲了一个 |
| 5 | chunked prefill = 长 prompt 切块逐步处理 | 语义对，但**没有「prefill scheduler」这个实体**：`scheduler.py:441-450` 注释明说——调度器里没有 prefill/decode 之分，只有每个请求的 `num_computed_tokens` 追赶 `num_tokens_with_spec`，切块是这个统一语义的自然结果 | 机制画像过时 |

**方法论注记**：概念课（由 glm-5.3 生成）的「错误」集中在 V0/V1 交替期——训练数据里 V0 时代的博客/论文占多数。这提示：概念课适合建立问题空间（**为什么**），机制细节（**怎么做的**）必须落到源码。两者不是替代关系，是漏斗的两段。

---

## 二、一次 `schedule()` 的完整解剖

`Scheduler.schedule()`（`scheduler.py:439-1253`）三阶段结构：

```
schedule(throttle_prefills):
  token_budget = max_num_scheduled_tokens            # :459（暂停态则 0）
  kv_cache_manager.new_step_starts()                 # :475

  ── 阶段一：RUNNING 循环（:483-671）─────────────────
  for request in running（budget 尽则停）:
    num_new_tokens = num_tokens_with_spec - num_computed_tokens
                                       # :516-520（截 long_prefill 阈值 :521-522、budget :523）
    loop: new_blocks = allocate_slots(...)          # :576-582
        None（没空闲 KV 块）→ 抢占：
          FCFS 弹 running 队尾（最新加入者）:615
          PRIORITY 弹 (priority, arrival) 最大者 :590-594
          受害者：释放全部 KV、num_computed_tokens=0、回 waiting 队头
                                       # _preempt_request :1274-1315
    token_budget -= num_new_tokens    # :637

  ── 阶段二：WAITING 循环（:684-1106，仅当本步无抢占）──
  while waiting and token_budget > 0:
    num_running >= max_num_seqs → break             # :690-692（旋钮一）
    新请求先查 prefix cache：get_computed_blocks    # :745-853（衔接阶段 2）
    num_new_tokens 截 budget          # :913（旋钮二，chunked prefill 在此发生）
    allocate_slots 失败 → break（不动现有 running）# :987-994
    running.append；status=RUNNING                  # :1055-1074

  ── 阶段三：组装 SchedulerOutput（:1108-1253）────────
  断言预算/并发不变量                  # :1109-1119
  new_reqs_data（全量）/ cached_reqs_data（只发 diff）# :1132-1158
  _update_after_schedule：推进各请求 num_computed_tokens
                                       # :1317-1365
```

三个容易被教科书忽略的细节：

1. **抢占会连坐**：本 step 一旦发生抢占，WAITING 队列整轮禁止进新请求（`:684`）——先把危机处理干净再谈扩张。
2. **FCFS 抢队尾**：抢占的是最新加入的请求（`:615`），不是最早的——让「已经投入最多计算」的请求先完成，直觉上是沉没成本保护。
3. **prefix cache 查找发生在准入时**（`:745-853`）——调度器与内存管理器（阶段 2 的主角）在这里第一次握手。

## 三、EngineCore 一个 step 的时序（iteration 粒度证据）

continuous batching 的「step 粒度」在引擎侧的铁证（`core.py:584-614`）：**每个 step 恰好调一次 `schedule()`、一次 `execute_model()`、一次 `update_from_output()`**：

```
前端 AsyncLLM ──ZMQ──► [input 线程] 解码+预处理 → input_queue
                          │
                     [主线程 busy loop :1377]
                       (1) _process_input_queue   :1382 → scheduler.add_request
                       (2) step() :584:
                           a. scheduler.schedule() → SchedulerOutput     :595
                           b. execute_model(non_block=True) → Future      :596
                           c. get_grammar_bitmask（与 forward 并行）      :597
                           d. Future.result()==None → sample_tokens()    :602-604
                           e. update_from_output → 完成检测+KV 释放       :609
                       (3) outputs → output_queue :1441
                          │
                     [output 线程] msgspec 编码 → ZMQ PUSH → 前端
```

值得记住的三个机制：

- **execute/sample 两相拆分**（阶段 0 报告的说法在此得到验证）：`gpu_model_runner.execute_model`（`:4516-4536`）只存状态返回 None，`sample_tokens`（`:4553`）才真正采样——为的是让 grammar bitmask 计算与 GPU forward 重叠。
- **「busy loop」需限定**：空闲时阻塞在 `input_queue.get(block=True)`（`core.py:1418-1422`），不是纯自旋；busy 体现在有请求时每轮无条件推进一个完整 step。
- **停止条件的双屋檐**：EOS/stop_token/长度在 EngineCore 进程判（`utils.py:94-134`），**stop string 在前端判**（`output_processor.py:655-704`，因为要等 detokenize 出文本）——前端发现 stop string 后反发 abort 走 `FINISHED_ABORTED`（`core.py:485-491`）。

## 四、请求状态机（11 态）

定义在 `request.py:348-364`，`is_finished = status > PREEMPTED`（`:369-371`）：

```
WAITING ──准入──► RUNNING ──┬─► FINISHED_STOPPED/LENGTH_CAPPED/REPETITION（utils.py:105/116/126）
   ▲                        ├─► PREEMPTED ──重新准入──► RUNNING（scheduler.py:1062-1074）
   │                        ├─► WAITING_FOR_STREAMING_REQ（流式续写，"停而不退" :2088-2089）
   │                        └─► FINISHED_ABORTED（外部 abort :2295）
   ├─► WAITING_FOR_STRUCTURED_OUTPUT_GRAMMAR（grammar 编译中）
   ├─► WAITING_FOR_REMOTE_KVS（KV connector 异步拉远程前缀 :1026）
   └─ 出生：request.py:97（注意：没有 QUEUED 状态——QUEUED 只是日志事件）
```

教科书之外的三条新边：**流式可恢复请求**（一次 finish 可转为续写）、**远程 KV 等待**（分布式前缀缓存的调度面）、**grammar 等待**（结构化输出的编译期不占 running 名额）。

## 五、旋钮全解（v0.27.1 实测默认值）

| 旋钮 | 作用点 | 类默认 | 服务端实际默认（`arg_utils.py:2515-2596`） |
|---|---|---|---|
| `max_num_seqs` | waiting 准入硬卡（`scheduler.py:690-692`） | 128 | H100 级 API server **1024**；中小 GPU **256** |
| `max_num_batched_tokens` | 每 step token 预算（`:459`） | 2048 | H100 级 API server **8192**；中小 GPU **2048**；throughput 模式 ×2（`:2744-2749`） |
| `long_prefill_token_threshold` | 单请求单步上限（`:521-522, 899-901`） | 0（禁用） | 同左 |
| `enable_chunked_prefill` | 关闭时放不下整个 prompt 直接不准入（`:905-911`） | True | 按模型支持度（`arg_utils.py:2601`） |
| `policy` | fcfs / priority（`config/scheduler.py:99`） | fcfs | fcfs |
| `async_scheduling` | 启用 AsyncScheduler（见 §七.4） | None | — |

约束链（`config/scheduler.py:249-285`）：关 chunked prefill 时必须 `max_num_batched_tokens ≥ max_model_len`；恒要求 `≥ max_num_seqs`。

## 六、chunked prefill 真身：没有切块器，只有「追赶」

V1 的调度哲学浓缩在 `scheduler.py:441-450` 的注释里：**不存在 prefill phase 和 decode phase，每个请求只是一个 `num_computed_tokens` 追赶 `num_tokens_with_spec` 的进度条**。由此统一覆盖 chunked prefill、prefix caching、投机解码三种场景：

- 新请求准入时 `num_new_tokens = num_tokens - num_computed_tokens`（`:879`，prefix cache 命中则 num_computed_tokens 已 >0），被预算截断（`:913`）——**切剩下的部分留在 running 里**（`:1055`），下个 step 在阶段一继续追。
- 批的「性质」由 model runner 事后判定：`_is_uniform_decode`（`gpu_model_runner.py:3912-3930`）——所有请求每步恰好 1+spec_tokens 个 token 才算纯 decode 批（可走 CUDA graph），否则就是混相批。**V0 时代的 `ForwardMode.PREFILL/DECODE` 批级标签在 v1/engine 与 v1/core/sched 下零命中**——已随 V0 一起被删除。
- CUDA graph 捕获进度条的二分世界印证：`"decode" if uniform_decode else "mixed prefill-decode"`（`:6989-6990`）。

## 七、v0.27.1 教科书之外的新东西

按「改写心智模型」的力度排序：

1. **Priority scheduling 正式落地**：`policy="priority"` 时等待队列是 `(priority, arrival_time, request_id)` 的堆（`request_queue.py:131-198`），抢占受害者也按最低优先级选（`scheduler.py:590-594`）。LPM/短队列优先等老策略**不存在**——只有 fcfs/priority 两种。
2. **KV transfer/connector 深度嵌入调度**：准入时远程前缀匹配（`:777-826`）、`WAITING_FOR_REMOTE_KVS` 异步加载（`:1026`）、KV 加载失败的 recompute/fail 双策略与回滚（`:2743-2915`）——调度器已是分布式 KV 的前线。
3. **第二个等待队列 `skipped_waiting`**（`:188-189, 2058-2062`）：grammar/远程 KV/流式阻塞的请求单独存放，避免堵死 FCFS 队头——「等待」不再是单队列。
4. **异步调度（AsyncScheduler，`async_scheduler.py:12-70`）**：schedule 第 N+1 步时第 N 步采样还没回来，于是给每个请求加 `num_output_placeholders` 占位（`:39-41`），spec token 先填 `-1`，真实 id 由 worker 回填。只有 70 行，是「重叠调度与执行」的极致尝试。
5. **流式可恢复会话**（`:2076-2092`）：stopped 的请求可以不退出而回 `WAITING_FOR_STREAMING_REQ` 等下一段输入——为长会话省重算。
6. **PauseState / DP prefill 均衡 / encoder 预算**（`:460-462, 479-481, 1469-1627`）：弹性扩缩容与多模态给调度器加的新关节。

## 八、调度器与相邻模块的三次握手（通往后续阶段）

- **↔ 内存管理（阶段 2）**：准入时 `get_computed_blocks`（`:745-853`）查 prefix cache；分配失败触发抢占——调度的一切容量焦虑都来自 KV block pool。
- **↔ 执行层（阶段 3）**：`SchedulerOutput` 的 diff 结构（`cached_reqs` 只发增量，`output.py:115-130`）与 `num_common_prefix_blocks`（cascade attention 用，`:1121-1129`）直接决定 model runner 怎么组批。
- **↔ 投机解码（阶段 5）**：`scheduled_spec_decode_tokens`（`output.py:212`）与动态 spec K（`:1192-1197`）——draft token 的调度位已预留。

---

## 思考与追问

1. **抢占的「连坐」与「抢队尾」是否最优？** 本 step 发生抢占就禁止 waiting 准入（`:684`）、FCFS 抢最新请求（`:615`）——这两个策略在什么负载画像下会成为瓶颈？（联想：大量短请求 + 少量长请求混合时，队尾的新短请求会被反复抢占，每次都归零重算，是否会造成饥饿循环？priority 策略下又如何？）
2. **「追赶语义」的代价是什么？** 统一的 `num_computed_tokens` 追赶让 prefill/decode 边界消失、代码极简，但混相批意味着 attention kernel 要同时处理长短不一的 query 长度——这是否正是 piecewise cudagraph / ubatching 存在的原因？（阶段 3 验证点）
3. **调度器的「立即」有多立即？** 完成检测在 update_from_output、释放块在下个 step 的 finished_req_ids、stop string 甚至要绕道前端——从「模型吐出 EOS」到「KV 块真正可复用」之间隔着多少个 step？（这个问题直接通往阶段 2 的 block pool 生命周期，也可能是一个值得用 GPU 实测的时间线。）

---

*源码引用均基于 v0.27.1；本报告由三路并行源码勘察（scheduler.py 精读 / EngineCore 主循环 / 配置面与队列结构）汇总而成，与 OpenMAIC 第二节概念课《调度器：continuous batching 的真身》互为地图与地形。*
