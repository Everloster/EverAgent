# 环境配置指南

> 按需安装：不同阶段依赖不同，建议用虚拟环境隔离。

---

## 第一步：检查硬件

```bash
python src/check_hardware.py
```

这个脚本会输出：
- CPU / 内存信息
- GPU 型号 + 显存大小
- CUDA 版本
- 训练兼容性评估

**解读**：
- 阶段 1-3：CPU 或任意 GPU 均可
- 阶段 4（GRPO 微调）：推荐 GPU ≥ 8GB 显存（4-bit 量化），16GB+ 效果更好

---

## 第二步：创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# 或 .venv\Scripts\activate  # Windows
```

---

## 第三步：按阶段安装依赖

### 阶段 1 — Transformer 从零实现

```bash
pip install torch torchvision torchaudio tiktoken requests
```

**版本要求**：PyTorch ≥ 2.0，Python ≥ 3.9

### 阶段 2 & 3 — Transformers 库 + HuggingFace 生态

```bash
pip install transformers datasets huggingface_hub pyarrow pandas tqdm
```

### 阶段 4 — GRPO 微调（需要 CUDA）

```bash
pip install unsloth trl peft
# unsloth 会自动安装正确版本的 bitsandbytes 和 transformers
```

> ⚠️ unsloth 安装需要 CUDA 环境，CPU-only 机器无法安装。如果没有 GPU，可以只阅读 Notebook 理解流程。

---

## 第四步：国内 HuggingFace 镜像配置

HuggingFace 在国内访问可能很慢，建议配置镜像：

```bash
# 临时设置（当前终端生效）
export HF_ENDPOINT=https://hf-mirror.com

# 永久设置（写入 shell 配置文件）
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.zshrc
source ~/.zshrc
```

或者在 Python 代码中设置（需在 import 之前）：
```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

---

## 第五步：下载阶段 4 所需模型（可选，需提前准备）

阶段 4 需要 `Qwen/Qwen2.5-3B-Instruct`，首次下载约 6GB（4-bit 量化约 2GB）：

```bash
# 推荐：使用 huggingface_hub 下载（支持断点续传）
python -c "
from huggingface_hub import snapshot_download
snapshot_download('Qwen/Qwen2.5-3B-Instruct', local_dir_use_symlinks=False)
"
```

---

## 常见问题排查

### Q: `torch.cuda.is_available()` 返回 False

原因和解决方案：
1. **没有安装 CUDA**：去 NVIDIA 官网下载对应版本
2. **PyTorch 版本与 CUDA 不匹配**：重新安装 `pip install torch --index-url https://download.pytorch.org/whl/cu121`（替换 cu121 为你的 CUDA 版本）
3. **macOS M 系列芯片**：用 `torch.backends.mps.is_available()` 检查 Metal Performance Shaders

### Q: 下载模型太慢

```bash
export HF_ENDPOINT=https://hf-mirror.com
# 如果 hf-mirror.com 也慢，可以试试：
# export HF_ENDPOINT=https://mirrors.tuna.tsinghua.edu.cn/hugging-face-models
```

### Q: `CUDA out of memory` 错误（阶段 4）

原因：显存不足。解决：
```python
# 确认 load_in_4bit=True（4-bit 量化，节省 75% 显存）
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen2.5-3B-Instruct",
    load_in_4bit=True,   # ← 必须为 True
    max_seq_length=512,  # ← 降低序列长度（原为 1024）
)
# 如果仍然 OOM，降低 per_device_train_batch_size=1（已经是最小值）
# 最后手段：换用更小的模型（Qwen2.5-1.5B）
```

### Q: `TikToken` 相关 ImportError

```bash
pip install tiktoken
```

### Q: `unsloth` 安装失败

unsloth 需要 CUDA 工具链。如果是 CPU-only 机器：
```bash
# 只安装 CPU 版本的依赖（阶段 4 代码无法运行，但可以阅读）
pip install transformers peft
```

---

## Jupyter Notebook 启动

```bash
# 安装 jupyter（若未安装）
pip install jupyter

# 启动（默认在浏览器打开）
jupyter notebook

# 或者使用 VS Code 的 Jupyter 插件（推荐，体验更好）
```

---

## 一键环境检查脚本

```bash
python -c "
import sys
print(f'Python: {sys.version}')
try:
    import torch
    print(f'PyTorch: {torch.__version__}')
    print(f'CUDA available: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'CUDA device: {torch.cuda.get_device_name(0)}')
except ImportError:
    print('PyTorch: NOT INSTALLED')
try:
    import transformers
    print(f'Transformers: {transformers.__version__}')
except ImportError:
    print('Transformers: NOT INSTALLED')
try:
    import tiktoken
    print(f'TikToken: {tiktoken.__version__}')
except ImportError:
    print('TikToken: NOT INSTALLED')
"
```
