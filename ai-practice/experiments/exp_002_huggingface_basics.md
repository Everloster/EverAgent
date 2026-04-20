---
title: HuggingFace 数据集与模型 API 实践
type: experiment_analysis
status: done
experiment_id: exp_002
notebook: notebooks/learn_huggingface.ipynb
updated_on: 2026-04-20
---

## 实验摘要

> 实践 HuggingFace Hub 核心 API：模型下载、本地缓存管理、数据集加载，重点使用 Qwen2.5-3B-Instruct 验证镜像加速和本地路径管理。

## Step 1 实验目标

- **工程问题**：掌握 HuggingFace 生态的模型/数据集本地管理，支持离线或低带宽场景
- **背景**：为 exp_004（Qwen2.5 GRPO 微调）做环境准备；国内访问 HuggingFace Hub 的镜像配置实践

## Step 2 实现方法

**框架 & 库**：`huggingface_hub`、`datasets`、`pyarrow`、`pandas`

**关键 API 覆盖**（来自 `notebooks/learn_huggingface.ipynb`）：

| 功能 | API | 关键参数 |
|------|-----|---------|
| 模型下载 | `snapshot_download()` | `repo_id="Qwen/Qwen2.5-3B-Instruct"`, `local_dir_use_symlinks=False` |
| 缓存扫描 | `scan_cache_dir()` | 列出所有本地缓存模型及路径/大小 |
| Hub 状态查询 | `HfApi().repo_info()` | 检查模型可访问性 |
| 数据集加载 | `load_dataset()` / `load_from_disk()` | 支持 datasets 格式和 parquet |
| 本地数据集探查 | 自定义 `get_dataset_info()` | 遍历 `~/.cache/huggingface/datasets` |

**镜像配置**（国内访问）：
```python
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'  # 推荐
# 备用：'https://mirrors.tuna.tsinghua.edu.cn/hugging-face-models'
```

**模型规模**：Qwen2.5-3B-Instruct（30亿参数，下载体积约 6GB，4bit 量化约 2GB）

## Step 3 关键发现

- HF Hub 缓存默认路径：`~/.cache/huggingface/`，模型在 `hub/` 子目录，数据集在 `datasets/`
- `local_dir_use_symlinks=False` 在 Windows 上必须设置（避免权限问题），Mac/Linux 可用符号链接
- `scan_cache_dir()` 返回 `HFCacheInfo` 对象，可枚举 `repos`，每个 repo 含 `repo_path`、`size_on_disk`
- 本地缓存后可完全离线使用，无需重新下载

**实际数值**：`[未运行 - 需执行 notebook 获取 Qwen2.5-3B 实际下载大小和缓存路径]`

## Step 4 代码参考

| 功能 | 文件 | 单元 |
|------|------|------|
| HF 镜像设置 + 模型下载 | `notebooks/learn_huggingface.ipynb` | Cell 1 |
| 缓存扫描与 Hub 状态查询 | `notebooks/learn_huggingface.ipynb` | Cell 2 |
| 数据集目录探查工具函数 | `notebooks/learn_huggingface.ipynb` | Cell 3 |

**可复用工具**：
- `src/load_local_dataset.py` — 封装了本地/网络数据集加载逻辑，支持 gsm8k 等格式

## Step 5 局限性与下一步

**局限性**：
- 镜像站稳定性依赖第三方服务，可能出现版本延迟
- `snapshot_download` 不支持断点续传（部分中断需重新下载）

**建议后续**：
- 研究 HF `hf_transfer` 加速包（rust 实现，速度提升约 5x）
- 结合 `src/load_local_dataset.py` 扩展支持更多数据集格式
