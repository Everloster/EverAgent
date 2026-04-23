---
title: "Agent Memory 系统深度解析"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-04-22"
---

# Agent Memory 系统深度解析

## 目录

- [引言](#引言)
- [Layer 1 直觉类比：为什么 Agent 需要记忆](#layer-1-直觉类比为什么-agent-需要记忆)
- [Layer 2 形式定义：记忆系统的核心问题与解决框架](#layer-2-形式定义记忆系统的核心问题与解决框架)
- [Layer 3 变体全景：记忆系统的演化路径](#layer-3-变体全景记忆系统的演化路径)
  - [阶段一：无记忆（Stateless）](#阶段一无记忆stateless)
  - [阶段二：会话内记忆（In-Session Memory）](#阶段二会话内记忆in-session-memory)
  - [阶段三：持久化记忆（Persistent Memory）](#阶段三持久化记忆persistent-memory)
  - [阶段四：智能记忆（Intelligent Memory）—— claude-mem](#阶段四智能记忆intelligent-memory--claude-mem)
- [Layer 4 工程实现：claude-mem 架构深度剖析](#layer-4-工程实现claude-mem-架构深度剖析)
  - [系统组件](#系统组件)
  - [记忆流水线：捕获 → 压缩 → 索引 → 注入](#记忆流水线捕获--压缩--索引--注入)
  - [搜索流水线：三层检索工作流](#搜索流水线三层检索工作流)
  - [会话生命周期与 Hooks](#会话生命周期与-hooks)
  - [数据库架构](#数据库架构)
- [Layer 5 前沿动态：记忆系统的未来](#layer-5-前沿动态记忆系统的未来)
- [总结](#总结)

---

## 引言

"Claude，我们上周重构了 auth 模块，你还记得为什么把 JWT 验证从中间件移到服务层吗？"

"抱歉，我不记得了。每次对话对我来说都是全新的开始。"

这是 2025 年大多数 AI 编程 Agent 用户的日常痛点。Agent 可以处理复杂任务，但**一旦会话结束，所有上下文烟消云散**。下次打开项目，Agent 像第一次见一样，需要重新了解代码库、重新理解架构决策、重新学习项目约定。

claude-mem 正是为解决这个痛点而生。它是一个 Claude Code 插件，自动捕获每次编码会话的所有操作，用 AI 压缩成结构化记忆，并在新会话开始时智能注入相关上下文。

本文将从 5 层理解模型出发，深度解析 Agent Memory 系统的设计哲学、工程实现和演化趋势。

---

## Layer 1 直觉类比：为什么 Agent 需要记忆

想象你有一个私人助理，但他有一个奇怪的毛病——**每天早上一觉醒来，就完全不记得昨天发生的事**。你需要每天重新告诉他：
- 你是谁
- 你们昨天讨论了什么
- 项目目前进展到哪一步
- 为什么做了某些决策

这就是无记忆 Agent 的用户体验。

**人类程序员的记忆方式**：
- 短期记忆：当前编辑的文件、正在调试的 bug、刚写的函数逻辑
- 中期记忆：本周的迭代计划、当前分支的功能范围、最近的架构讨论
- 长期记忆：项目整体架构、技术选型原因、团队编码规范、历史重大决策

**Agent 需要三种对应的记忆**：
1. **上下文记忆**（Context Memory）：当前会话内的对话历史
2. **项目记忆**（Project Memory）：跨会话的项目知识、架构、约定
3. **个人记忆**（Personal Memory）：用户的偏好、习惯、编码风格

claude-mem 解决的是**项目记忆**和**个人记忆**——让 Agent 在每次新会话开始时，就已经"记得"项目的关键信息。

---

## Layer 2 形式定义：记忆系统的核心问题与解决框架

### 核心问题

Agent Memory 系统需要解决五个核心问题：

| 问题 | 描述 | 挑战 |
|------|------|------|
| **捕获** | 记录 Agent 在会话中做了什么 | 工具调用种类繁多，如何统一捕获？ |
| **压缩** | 原始记录太多，如何提炼精华 | 不丢失关键信息的前提下大幅缩减体积 |
| **索引** | 如何快速找到相关记忆 | 支持语义搜索、时间线查询、关键词匹配 |
| **注入** | 新会话开始时加载哪些记忆 | 上下文窗口有限，不能全部加载 |
| **时效** | 记忆会过时，如何管理生命周期 | 代码变了，旧记忆可能变成误导 |

### 核心公式

```
有效记忆 = 捕获完整性 × 压缩保真度 × 检索精准度 × 注入相关性
```

四个因子缺一不可：
- 捕获不完整 → 遗漏关键决策
- 压缩失真 → 丢失重要细节
- 检索不准 → 找到不相关的记忆
- 注入不当 → 上下文窗口浪费或信息不足

### 记忆系统的分类框架

| 类型 | 存储位置 | 生命周期 | 典型实现 |
|------|---------|---------|---------|
| 上下文记忆 | 内存/上下文窗口 | 单次会话 | 对话历史 |
| 项目记忆 | 本地文件/数据库 | 项目存续期 | CLAUDE.md、项目文档 |
| 持久记忆 | 本地数据库/云端 | 跨项目长期 | claude-mem、mem0 |
| 外部记忆 | 向量数据库 | 按需查询 | RAG、知识图谱 |

---

## Layer 3 变体全景：记忆系统的演化路径

### 阶段一：无记忆（Stateless）

**特征**：每次 API 调用独立，模型不保留任何历史信息。

**代表**：早期 GPT-3 API、简单的单次问答系统。

**问题**：
- 多轮对话需要客户端手动拼接历史
- 无法跨会话保持状态
- 每个请求都是"第一次见"

**解决方式**：客户端维护对话历史，每次请求携带完整上下文。

### 阶段二：会话内记忆（In-Session Memory）

**特征**：单次会话内保持对话历史，会话结束即清空。

**代表**：ChatGPT、Claude.ai 网页版、Claude Code 原生会话。

**机制**：
```python
# 伪代码：会话内记忆
session_messages = []
while session_active:
    user_input = get_user_input()
    session_messages.append({"role": "user", "content": user_input})
    response = llm.chat(messages=session_messages)
    session_messages.append({"role": "assistant", "content": response})
# 会话结束，session_messages 丢弃
```

**局限**：
- 跨会话完全失忆
- 长会话上下文窗口溢出
- 无法积累项目知识

### 阶段三：持久化记忆（Persistent Memory）

**特征**：将会话中的关键信息保存到持久存储，新会话时加载。

**代表项目**：

| 项目 | 机制 | 特点 |
|------|------|------|
| **mem0** | 用户事实提取 + 向量存储 | 专注用户偏好和事实记忆 |
| **supermemory** | 网页内容保存 + 检索 | 专注网页浏览记忆 |
| **openmemory** | 开源记忆框架 | 通用记忆基础设施 |
| **claude-mem** | 工具调用捕获 + AI 压缩 + 相关性注入 | 专注编码会话记忆 |

**共同挑战**：
- 保存什么？（全部保存 vs 选择性保存）
- 如何压缩？（原始记录 vs AI 摘要）
- 如何检索？（关键词 vs 语义搜索）
- 何时注入？（会话开始 vs 按需加载）

### 阶段四：智能记忆（Intelligent Memory）—— claude-mem

**诞生背景**：

claude-mem 由 thedotmack 创建，定位是"A Claude Code plugin that automatically captures everything Claude does during your coding sessions, compresses it with AI, and injects relevant context back into future sessions" <ref>https://github.com/thedotmack/claude-mem</ref>。

**核心创新**：

不同于简单的"保存对话历史"，claude-mem 实现了**完整的记忆流水线**：

```
原始工具调用
    ↓
生命周期 Hooks 捕获
    ↓
AI 压缩成结构化观察（Observation）
    ↓
向量化索引（Chroma + SQLite FTS5）
    ↓
新会话开始时相关性检索
    ↓
智能注入上下文
```

**关键设计决策**：

1. **不是保存对话，而是保存观察**：不保存"用户说了什么、AI 回了什么"，而是保存"AI 发现了什么、做了什么决策、遇到了什么问题"
2. **AI 压缩，不是人工摘要**：用另一个 AI 调用把原始工具输出压缩成结构化摘要，保留关键信息，丢弃噪音
3. **相关性注入，不是全量加载**：新会话开始时，根据当前任务自动检索最相关的记忆片段注入，而不是加载全部历史

---

## Layer 4 工程实现：claude-mem 架构深度剖析

### 系统组件

claude-mem 由 5 个核心组件构成 <ref>https://github.com/thedotmack/claude-mem</ref>：

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code 会话层                        │
├─────────────────────────────────────────────────────────────┤
│  Plugin Hooks（6 个生命周期钩子）                             │
│  ├── session-start-hook.js                                  │
│  ├── user-prompt-submit-hook.js                             │
│  ├── post-tool-use-hook.js                                  │
│  ├── summary-hook.js                                        │
│  ├── stop-hook.js                                           │
│  └── session-end-hook.js                                    │
├─────────────────────────────────────────────────────────────┤
│  Worker Service（HTTP API，端口 37777）                       │
│  ├── 10 个搜索端点                                          │
│  ├── Web Viewer UI                                          │
│  └── Bun 运行时管理                                         │
├─────────────────────────────────────────────────────────────┤
│  数据层                                                      │
│  ├── SQLite（sessions, observations, summaries, prompts）    │
│  ├── FTS5 全文搜索（observations_fts, summaries_fts）        │
│  └── Chroma Vector DB（语义搜索）                            │
├─────────────────────────────────────────────────────────────┤
│  mem-search Skill（v5.4.0+）                                 │
│  └── 自然语言查询 + 渐进披露                                  │
└─────────────────────────────────────────────────────────────┘
```

### 记忆流水线：捕获 → 压缩 → 索引 → 注入

#### 步骤 1：捕获（Capture）

通过 Claude Code 插件生命周期 Hooks 实现 <ref>https://github.com/thedotmack/claude-mem/blob/main/CLAUDE.md</ref>：

```
SessionStart → UserPromptSubmit → PostToolUse → Summary → SessionEnd
```

**6 个 Hooks 的职责**：

| Hook | 触发时机 | 捕获内容 |
|------|---------|---------|
| SessionStart | 新会话开始 | 初始化会话记录，注入相关历史记忆 |
| UserPromptSubmit | 用户提交消息前 | 记录用户输入 |
| PostToolUse | 工具调用完成后 | 记录工具类型、参数、输出结果 |
| Summary | 会话进行中（定期） | 触发 AI 压缩当前观察 |
| Stop | 用户中断会话 | 保存中断状态 |
| SessionEnd | 会话正常结束 | 最终压缩，生成会话摘要 |

**捕获的数据类型**：

```typescript
interface ToolCall {
  tool: string;           // "Read", "Edit", "Bash", "Grep" 等
  params: object;         // 工具参数
  output: string;         // 工具输出（可能很大）
  timestamp: number;      // 时间戳
}

interface Observation {
  session_id: string;
  tool_calls: ToolCall[];
  raw_output: string;     // 原始输出（可能数千 tokens）
  compressed_summary: string;  // AI 压缩后的摘要
  embedding: number[];    // 向量嵌入
  created_at: number;
}
```

#### 步骤 2：压缩（Compression）

这是 claude-mem 的核心创新。不是简单截断或提取关键词，而是用 AI 进行**语义压缩** <ref>https://aicoding.juejin.cn/post/7606136581061771291</ref>：

```python
# 伪代码：AI 压缩流程
def compress_observation(raw_tool_output):
    prompt = f"""
    将以下工具调用输出压缩成结构化观察记录。
    保留：关键发现、架构决策、问题原因、解决方案
    丢弃：具体代码内容、重复信息、临时输出
    
    原始输出：
    {raw_tool_output}
    
    输出格式：
    - 发现：[关键发现]
    - 决策：[做出的决策及原因]
    - 问题：[遇到的问题]
    - 解决：[解决方案]
    - 文件：[涉及的关键文件]
    """
    
    compressed = llm.generate(prompt)
    return compressed
```

**压缩效果**：
- 原始工具输出：2,000-10,000 tokens
- 压缩后观察：100-300 tokens
- 压缩比：10:1 到 50:1

**压缩质量的关键**：
- 保留"为什么"比保留"做了什么"更重要
- 架构决策的上下文比具体代码更有价值
- 失败和教训比成功路径更值得记住

#### 步骤 3：索引（Index）

claude-mem 使用双重索引机制 <ref>https://docs.claude-mem.ai/architecture/database</ref>：

**SQLite + FTS5 全文搜索**：

```sql
-- 核心表
CREATE TABLE observations (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FTS5 虚拟表（全文搜索）
CREATE VIRTUAL TABLE observations_fts USING fts5(
    content,
    content='observations',
    content_rowid='id'
);

-- 自动同步触发器
CREATE TRIGGER observations_ai AFTER INSERT ON observations BEGIN
    INSERT INTO observations_fts(rowid, content) VALUES (new.id, new.content);
END;
```

**Chroma 向量数据库**：

```python
# 伪代码：向量索引
import chromadb

client = chromadb.Client()
collection = client.get_or_create_collection("claude-mem")

def index_observation(observation):
    embedding = get_embedding(observation.compressed_summary)
    collection.add(
        ids=[observation.id],
        embeddings=[embedding],
        documents=[observation.compressed_summary],
        metadatas=[{
            "session_id": observation.session_id,
            "created_at": observation.created_at,
            "tool_types": observation.tool_types
        }]
    )
```

**双重索引的优势**：
- FTS5：精确关键词匹配，适合查找特定文件名、函数名
- Chroma：语义相似度搜索，适合"上次处理类似问题的经验"

#### 步骤 4：注入（Injection）

新会话开始时，claude-mem 不是加载全部历史，而是**智能选择相关记忆注入** <ref>https://github.com/FlorianBruniaux/claude-code-ultimate-guide/blob/main/examples/plugins/claude-mem.md</ref>：

```python
# 伪代码：相关性注入
def inject_relevant_memories(user_prompt, session_context):
    # 1. 获取当前任务的嵌入向量
    query_embedding = get_embedding(user_prompt)
    
    # 2. 向量搜索：找语义相关的历史观察
    semantic_results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    # 3. 全文搜索：找包含相同关键词的观察
    keyword_results = fts5_search(
        extract_keywords(user_prompt),
        limit=5
    )
    
    # 4. 时间线搜索：找最近的相关工作
    recent_results = query_recent_observations(
        session_id=current_project,
        limit=3
    )
    
    # 5. 合并去重，按相关性排序
    all_results = merge_and_deduplicate(
        semantic_results, keyword_results, recent_results
    )
    
    # 6. 注入上下文（控制 token 预算）
    injected_memories = []
    token_budget = 2000  # 留给记忆的 token 上限
    for result in all_results:
        if count_tokens(injected_memories) + count_tokens(result) < token_budget:
            injected_memories.append(result)
        else:
            break
    
    return format_memories_for_context(injected_memories)
```

**注入格式示例**：

```markdown
## 相关历史记忆

[2026-04-15] 你之前重构了 auth 模块：
- 发现：JWT 验证在中间件层导致循环依赖
- 决策：将 JWT 验证从中间件移到服务层
- 涉及文件：src/auth/jwt.ts, src/middleware/auth.ts

[2026-04-18] 你优化了数据库查询：
- 发现：用户列表查询 N+1 问题
- 解决：添加 eager loading，查询时间从 2s 降到 200ms
- 涉及文件：src/services/user.ts
```

### 搜索流水线：三层检索工作流

claude-mem v5.4.0+ 引入了 `mem-search` Skill，提供三层检索工作流 <ref>https://aicoding.juejin.cn/post/7606136581061771291</ref>：

```
用户查询
    ↓
Layer 1: search（搜索）
    - 用自然语言或关键词在记忆索引里搜索
    - 返回紧凑列表（标题 + 时间 + 摘要）
    - Token 开销：~100 tokens
    ↓
Layer 2: timeline（时间线）
    - 如果用户想深入了解某个时间段
    - 返回该时间段的所有观察摘要
    - Token 开销：~300 tokens
    ↓
Layer 3: get_observations（获取详情）
    - 只拉取真正需要的观察全文
    - Token 开销：按需，通常 500-1000 tokens
```

**为什么分三层？**

因为记忆库可能积累数千条观察，如果一次性全部加载，上下文窗口直接爆炸。三层检索像漏斗一样逐层过滤，只在真正需要时才加载详细内容。

### 会话生命周期与 Hooks

完整的会话生命周期 <ref>https://github.com/thedotmack/claude-mem/blob/main/CLAUDE.md</ref>：

```
┌─────────────┐
│  会话开始   │
└──────┬──────┘
       │ SessionStart Hook
       │ - 创建会话记录
       │ - 检索并注入相关历史记忆
       ↓
┌─────────────┐
│  用户输入   │
└──────┬──────┘
       │ UserPromptSubmit Hook
       │ - 记录用户输入
       ↓
┌─────────────┐
│  工具调用   │◄──────┐
└──────┬──────┘      │
       │ PostToolUse  │
       │ - 捕获工具调用│
       │ - 原始输出   │
       ↓             │
┌─────────────┐      │
│  继续循环？  │──────┘
└──────┬──────┘（是）
       │（否）
       ↓
┌─────────────┐
│  Summary Hook│
│ - AI 压缩当前观察
│ - 写入数据库
│ - 更新向量索引
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ SessionEnd  │
│ - 生成会话摘要
│ - 最终持久化
│ - 清理临时数据
└─────────────┘
```

### 数据库架构

claude-mem 使用 SQLite 作为核心数据库 <ref>https://docs.claude-mem.ai/architecture/database</ref>：

**核心表结构**：

```sql
-- 会话表
CREATE TABLE sdk_sessions (
    id TEXT PRIMARY KEY,
    project_path TEXT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    summary TEXT
);

-- 观察表（核心）
CREATE TABLE observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sdk_sessions(id),
    content TEXT NOT NULL,           -- AI 压缩后的内容
    raw_content TEXT,                -- 原始内容（可选保留）
    tool_type TEXT,                  -- Read/Edit/Bash/Grep
    file_path TEXT,                  -- 涉及文件
    created_at TIMESTAMP
);

-- 会话摘要表
CREATE TABLE session_summaries (
    id INTEGER PRIMARY KEY,
    session_id TEXT REFERENCES sdk_sessions(id),
    summary TEXT NOT NULL,
    key_decisions TEXT,              -- JSON 数组
    created_at TIMESTAMP
);

-- 用户提示表
CREATE TABLE user_prompts (
    id INTEGER PRIMARY KEY,
    session_id TEXT REFERENCES sdk_sessions(id),
    prompt TEXT NOT NULL,
    created_at TIMESTAMP
);
```

**FTS5 全文搜索虚拟表**：

```sql
-- 观察全文搜索
CREATE VIRTUAL TABLE observations_fts USING fts5(
    content,
    content='observations',
    content_rowid='id'
);

-- 摘要全文搜索
CREATE VIRTUAL TABLE session_summaries_fts USING fts5(
    summary,
    content='session_summaries',
    content_rowid='id'
);

-- 自动同步触发器
CREATE TRIGGER observations_ai AFTER INSERT ON observations BEGIN
    INSERT INTO observations_fts(rowid, content) VALUES (new.id, new.content);
END;
```

**设计决策：为什么用 SQLite？**

1. **零配置**：不需要单独的数据库服务器，开箱即用
2. **本地优先**：数据保存在用户本地，隐私安全
3. **单文件**：整个数据库一个文件，易于备份和迁移
4. **FTS5 内置**：SQLite 3.9+ 原生支持全文搜索，无需额外依赖
5. **足够快**：对于个人编码会话的记忆量（通常 < 10万条记录），SQLite 完全够用

### Worker Service

claude-mem 运行一个本地 HTTP 服务（端口 37777）<ref>https://github.com/thedotmack/claude-mem</ref>：

```
Worker Service API（端口 37777）
├── GET  /health              # 健康检查
├── GET  /search              # 语义搜索
├── GET  /search/keyword      # 关键词搜索
├── GET  /timeline            # 时间线查询
├── GET  /observations/:id    # 获取单条观察
├── GET  /sessions            # 会话列表
├── GET  /sessions/:id        # 会话详情
├── GET  /stats               # 统计信息
└── GET  /viewer              # Web UI 首页
```

**Web Viewer UI**：

提供一个浏览器界面查看记忆库：
- 按时间线浏览所有会话
- 搜索特定关键词
- 查看观察详情
- 管理记忆（删除过时的）

---

## Layer 5 前沿动态：记忆系统的未来

### 当前研究边界

1. **记忆与 Harness 的融合**：claude-mem 证明记忆应该是 Harness 的一等公民，而不是外挂。未来所有 Agent Harness 可能都内置记忆层。

2. **多模态记忆**：目前的记忆主要是文本。当 Agent 开始处理图像、音频、视频时，记忆系统需要支持多模态索引和检索。

3. **记忆共享**：团队级别的记忆——"整个团队对项目的共同记忆"。不是每个人各自保存一份，而是共享一个项目记忆库。

4. **记忆版本控制**：代码有 Git，记忆也应该有版本控制。当代码重构后，旧记忆如何标记为过时？如何追溯"当时为什么做这个决策"？

### 未解问题

1. **记忆准确性**：AI 压缩会丢失信息，如何确保关键细节不被压缩掉？有没有"不可压缩"的标签机制？

2. **记忆冲突**：旧记忆说"auth 模块用 JWT"，新记忆说"auth 模块改成 Session 了"，Agent 如何知道哪个是最新的？

3. **隐私边界**：记忆库中可能包含敏感信息（API 密钥、内部架构），如何自动识别和保护？

4. **记忆膨胀**：长期使用后，记忆库可能积累数万条观察，检索性能如何保障？是否需要"记忆归档"机制？

5. **跨项目记忆**："我在项目 A 学到的模式，能否应用到项目 B？"跨项目记忆迁移的边界在哪里？

### 与其他记忆方案对比

| 方案 | 捕获方式 | 压缩方式 | 索引方式 | 注入方式 | 适用场景 |
|------|---------|---------|---------|---------|---------|
| **claude-mem** | Hooks 自动捕获 | AI 语义压缩 | FTS5 + Chroma | 相关性检索 | 编码会话 |
| **mem0** | 显式 API 调用 | 提取用户事实 | 向量搜索 | 自动注入 | 用户偏好 |
| **supermemory** | 浏览器插件 | 网页摘要 | 向量搜索 | 聊天查询 | 网页浏览 |
| **CLAUDE.md** | 手动编写 | 无 | 无 | 每次加载 | 项目规范 |
| **RAG** | 文档导入 | 文本分块 | 向量搜索 | 按需检索 | 知识库问答 |

**关键洞察**：没有"最好的"记忆系统，只有"最适合场景"的记忆系统。claude-mem 的优势在于**自动化**——不需要用户手动保存，一切通过 Hooks 自动完成。

### 演化趋势预测

**短期（6 个月）**：
- 主流 Agent 工具（Claude Code、Cursor、Codex）可能内置记忆层
- 记忆与 Skill 的融合——"记忆即 Skill"，自动生成的项目特定 Skill
- 记忆共享机制——团队级记忆库

**中期（1-2 年）**：
- 记忆版本控制——类似 Git 的记忆分支和合并
- 记忆质量评估——自动识别过时、冲突、低质量的记忆
- 跨项目记忆迁移——"我在 100 个项目中学到的模式"

**长期（3-5 年）**：
- 记忆可能成为 Agent 的"身份"——不同 Agent 的区别在于它们的记忆
- 记忆交易/共享市场——"购买一个资深工程师的项目记忆"
- 记忆与模型的深度融合——模型微调时注入个人记忆

---

## 总结

Agent Memory 系统经历了四个阶段的演化：

```
 Stateless（无记忆）
    ↓
 In-Session Memory（会话内记忆）
    ↓
 Persistent Memory（持久化记忆）
    ↓
 Intelligent Memory（智能记忆——claude-mem）
```

claude-mem 代表了当前最先进的编码 Agent 记忆方案，其核心创新在于：

1. **自动化捕获**：通过 Hooks 自动记录所有工具调用，零用户干预
2. **AI 压缩**：用 AI 把原始输出压缩成结构化观察，10:1 到 50:1 的压缩比
3. **双重索引**：FTS5 全文搜索 + Chroma 向量搜索，兼顾精确匹配和语义相似
4. **相关性注入**：新会话时只注入最相关的记忆，控制上下文窗口
5. **本地优先**：SQLite 单文件数据库，隐私安全，零配置

从 Harness 视角看，Memory 是 Harness 的**状态层**。一个完整的 Harness 应该包含：
- **控制层**：工作流/图编排（Archon/deer-flow）
- **能力层**：Skills（TDD、代码审查等）
- **状态层**：Memory（项目知识、历史决策）
- **工具层**：MCP（外部 API、数据库）

claude-mem 填补了"状态层"的空白，让 Agent 从"每次全新开始"变成"带着经验工作"。

最终，一个拥有完善记忆的 Agent，就像一个在这个项目上工作了多年的资深工程师——他知道代码库的历史、理解架构决策的原因、记得踩过的坑。这才是 AI 编程 Agent 真正走向实用的关键一步。

---

**数据来源**：

- claude-mem GitHub: <https://github.com/thedotmack/claude-mem>
- claude-mem 架构文档: <https://docs.claude-mem.ai/architecture/overview>
- claude-mem 数据库架构: <https://docs.claude-mem.ai/architecture/database>
- claude-mem 深度解读: <https://aicoding.juejin.cn/post/7606136581061771291>
- claude-mem 插件模板: <https://github.com/FlorianBruniaux/claude-code-ultimate-guide/blob/main/examples/plugins/claude-mem.md>
- claude-mem CLAUDE.md: <https://github.com/thedotmack/claude-mem/blob/main/CLAUDE.md>
