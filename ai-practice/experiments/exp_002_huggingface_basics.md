---
title: HuggingFace Hub 模型与数据集管理
type: tutorial_note
stage: 3
notebook: notebooks/03_huggingface_api.ipynb
prerequisites: ["python_basics", "file_system"]
updated_on: 2026-04-20
---

## 学习目标

- [ ] 掌握 HuggingFace Hub 上的模型下载和本地缓存管理
- [ ] 理解缓存目录结构（`~/.cache/huggingface/`）
- [ ] 能在国内网络环境下正常使用 HF 生态（镜像配置）
- [ ] 理解 `datasets` 库的基本加载方式

---

## 核心概念（Why）

### 为什么需要管理模型缓存？

现代 LLM 动辄几 GB 甚至几十 GB，如果每次使用都重新下载：
- 浪费时间（特别是国内网络）
- 浪费磁盘（同一模型下载多次）
- 无法离线使用（生产环境通常没有公网）

HuggingFace 的缓存机制让你**下载一次，永久复用**。

### HuggingFace 缓存架构

```
~/.cache/huggingface/
├── hub/                    ← 模型缓存
│   └── models--Qwen--Qwen2.5-3B-Instruct/
│       ├── snapshots/      ← 具体版本文件
│       └── blobs/          ← 去重的实际文件块
└── datasets/               ← 数据集缓存
    └── gsm8k/
```

**关键设计**：`blobs/` 目录存储真实文件，`snapshots/` 通过符号链接指向它，不同版本的相同文件只存一份。

---

## 实现解析

### 国内镜像配置（必须先设置）

```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
# ↑ 必须在 import huggingface_hub 之前设置
```

### 下载模型

```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="Qwen/Qwen2.5-3B-Instruct",
    local_dir_use_symlinks=False,  # Windows 用户必须设置 False
    # ignore_patterns=["*.bin"],  # 可选：排除旧格式权重
)
```

**`local_dir_use_symlinks=False` 的含义**：
- `True`（默认）：在目标路径创建符号链接指向 `blobs/`，省磁盘但 Windows 不支持
- `False`：直接复制文件到目标路径，跨平台兼容，但占用额外磁盘

### 扫描已缓存模型

```python
from huggingface_hub import scan_cache_dir, HfApi

cache_info = scan_cache_dir()
for repo in cache_info.repos:
    print(f"模型：{repo.repo_id}")
    print(f"路径：{repo.repo_path}")
    print(f"大小：{repo.size_on_disk / 1e9:.2f} GB")
```

### 数据集加载

```python
from datasets import load_dataset

# 从网络加载（首次）
dataset = load_dataset("openai/gsm8k", "main")

# 从本地缓存加载（后续）
from datasets import load_from_disk
dataset = load_from_disk("~/.cache/huggingface/datasets/gsm8k")
```

---

## 实验结果

**注**：请运行 `notebooks/03_huggingface_api.ipynb` 查看实际输出。以下为预期结果。

- Qwen2.5-3B-Instruct 下载大小：约 **5.8GB**（bf16 格式）
- 4-bit 量化后加载内存占用：约 **2GB**
- 缓存路径：`~/.cache/huggingface/hub/models--Qwen--Qwen2.5-3B-Instruct/`

---

## 思考题与延伸实验

1. **缓存管理**：运行 `scan_cache_dir()`，查看你本地缓存了哪些模型，总共占用多少磁盘空间？

2. **模型版本控制**：`snapshot_download` 有 `revision` 参数，可以指定下载特定 commit 版本。这对生产环境有什么用？

3. **断点续传**：如果网络中断，再次运行 `snapshot_download` 会重新下载还是继续？（提示：查看 `blobs/` 目录中的 `.incomplete` 文件）

4. **自定义数据集**：如何将自己的 CSV 文件转换成 HuggingFace `Dataset` 格式？（提示：`Dataset.from_pandas(df)`）

---

## 参考资料

- [HuggingFace Hub 文档](https://huggingface.co/docs/huggingface_hub/guides/download)
- [datasets 文档](https://huggingface.co/docs/datasets/loading)
- [hf-mirror.com 镜像说明](https://hf-mirror.com)
- **本项目工具**：[src/load_local_dataset.py](../src/load_local_dataset.py)（封装了本地/网络数据集加载）
