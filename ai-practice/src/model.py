# 导入必要的库
import os                # 用于文件和目录操作
import requests         # 用于发送HTTP请求
import math            # 用于数学计算
import tiktoken        # OpenAI的分词器
import torch           # PyTorch深度学习框架
import torch.nn as nn  # PyTorch神经网络模块
from torch.nn import functional as F  # PyTorch函数式API

# 超参数设置
batch_size = 4        # 每批训练的样本数
context_length = 16   # 上下文长度，即每次处理的序列长度
d_model = 64         # 模型的维度，即词嵌入和各层的特征维度
num_blocks = 8       # Transformer块的数量
num_heads = 4        # 注意力机制的头数
learning_rate = 1e-3  # 学习率
dropout = 0.1        # Dropout比率，用于防止过拟合
max_iters = 5000     # 最大训练迭代次数
eval_interval = 50   # 评估间隔
eval_iters = 20      # 评估时的迭代次数
device = 'cuda' if torch.cuda.is_available() else 'cpu'  # 设备选择：优先使用GPU
TORCH_SEED = 1337    # 随机种子，确保结果可复现
torch.manual_seed(TORCH_SEED)  # 设置随机种子

# 加载训练数据
if not os.path.exists('data/sales_textbook.txt'):
    # 如果本地没有数据文件，从网络下载
    url = 'https://huggingface.co/datasets/goendalf666/sales-textbook_for_convincing_and_selling/raw/main/sales_textbook.txt'
    with open('data/sales_textbook.txt', 'w') as f:
        f.write(requests.get(url).text)

# 读取文本文件
with open('data/sales_textbook.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 使用TikToken进行分词（与GPT-3使用相同的分词器）
encoding = tiktoken.get_encoding("cl100k_base")  # 获取分词器
tokenized_text = encoding.encode(text)  # 将文本转换为token序列
max_token_value = max(tokenized_text) + 1  # 获取最大token值（词表大小）
tokenized_text = torch.tensor(tokenized_text, dtype=torch.long, device=device)  # 转换为张量

# 划分训练集和验证集
split_idx = int(len(tokenized_text) * 0.9)  # 90%用于训练
train_data = tokenized_text[:split_idx]  # 训练数据
val_data = tokenized_text[split_idx:]    # 验证数据

# 定义前馈神经网络
class FeedForward(nn.Module):
    """前馈神经网络模块
    包含两个线性层,中间使用ReLU激活函数,并应用Dropout
    第一个线性层扩展维度*4,第二个线性层压缩回原始维度
    """
    def __init__(self):
        super().__init__()
        self.d_model = d_model
        self.dropout = dropout
        self.ffn = nn.Sequential(
            nn.Linear(self.d_model, self.d_model * 4),  # 扩展维度
            nn.ReLU(),                                  # 激活函数
            nn.Linear(self.d_model * 4, self.d_model),  # 压缩维度
            nn.Dropout(dropout),                        # 防止过拟合
        )

    def forward(self, x):
        return self.ffn(x)

# 定义缩放点积注意力机制
class Attention(nn.Module):
    """实现注意力机制
    包含Query、Key、Value三个线性变换,以及注意力计算和mask操作
    """
    def __init__(self, head_size: int):
        super().__init__()
        self.d_model = d_model
        self.head_size = head_size
        self.context_length = context_length
        self.dropout = dropout

        # 定义Q、K、V的线性变换层
        self.key_layer = nn.Linear(self.d_model, self.head_size, bias=False)
        self.query_layer = nn.Linear(self.d_model, self.head_size, bias=False)
        self.value_layer = nn.Linear(self.d_model, self.head_size, bias=False)
        # 创建下三角矩阵作为mask
        self.register_buffer('tril', torch.tril(torch.ones((self.context_length, self.context_length))))
        self.dropout_layer = nn.Dropout(self.dropout)

    def forward(self, x):
        B, T, C = x.shape  # 批次大小，序列长度，特征维度
        assert T <= self.context_length
        assert C == self.d_model
        
        # 计算Q、K、V
        q = self.query_layer(x)  # 查询向量
        k = self.key_layer(x)    # 键向量
        v = self.value_layer(x)  # 值向量

        # 计算注意力权重
        weights = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))  # 缩放点积注意力
        weights = weights.masked_fill(self.tril[:T, :T] == 0, float('-inf'))  # 应用mask
        weights = F.softmax(weights, dim=-1)  # softmax归一化
        weights = self.dropout_layer(weights)  # 应用dropout

        # 计算输出
        out = weights @ v  # 加权求和
        return out

# 定义多头注意力机制
class MultiHeadAttention(nn.Module):
    """多头注意力机制
    将输入分割成多个头，每个头独立计算注意力，然后合并结果
    """
    def __init__(self, head_size: int):
        super().__init__()
        self.num_heads = num_heads
        self.head_size = head_size
        self.d_model = d_model
        self.context_length = context_length
        self.dropout = dropout

        # 创建多个注意力头
        self.heads = nn.ModuleList([Attention(head_size=self.head_size) for _ in range(self.num_heads)])
        # 输出投影层
        self.projection_layer = nn.Linear(self.d_model, self.d_model)
        self.dropout_layer = nn.Dropout(dropout)

    def forward(self, x):
        # 并行计算所有注意力头
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        # 投影到输出空间
        out = self.projection_layer(out)
        out = self.dropout_layer(out)
        return out

# 定义Transformer块
class TransformerBlock(nn.Module):
    """Transformer的基本构建块
    包含多头注意力机制和前馈神经网络，以及层归一化和残差连接
    """
    def __init__(self, num_heads: int):
        super().__init__()
        self.d_model = d_model
        self.context_length = context_length
        self.head_size = d_model // num_heads
        self.num_heads = num_heads
        self.dropout = dropout

        # 主要组件
        self.multi_head_attention_layer = MultiHeadAttention(head_size=self.head_size)
        self.feed_forward_layer = FeedForward()
        self.layer_norm_1 = nn.LayerNorm(self.d_model)
        self.layer_norm_2 = nn.LayerNorm(self.d_model)

    def forward(self, x):
        # 注意：这里的层序列与原始Transformer论文不同
        # 这里是：LayerNorm -> 多头注意力 -> LayerNorm -> 前馈网络
        x = x + self.multi_head_attention_layer(self.layer_norm_1(x))  # 第一个残差连接
        x = x + self.feed_forward_layer(self.layer_norm_2(x))         # 第二个残差连接
        return x

# 定义Transformer语言模型
class TransformerLanguageModel(nn.Module):
    """完整的Transformer语言模型
    包含词嵌入、位置编码、多个Transformer块和输出层
    """
    def __init__(self):
        super().__init__()
        # 初始化模型参数
        self.d_model = d_model
        self.context_length = context_length
        self.num_heads = num_heads
        self.num_blocks = num_blocks
        self.dropout = dropout
        self.max_token_value = max_token_value

        # 词嵌入层
        self.token_embedding_lookup_table = nn.Embedding(
            num_embeddings=self.max_token_value + 1,
            embedding_dim=self.d_model
        )

        # Transformer块序列
        self.transformer_blocks = nn.Sequential(*(
            [TransformerBlock(num_heads=self.num_heads) for _ in range(self.num_blocks)] +
            [nn.LayerNorm(self.d_model)]  # 最后添加一个层归一化
        ))
        
        # 输出层
        self.language_model_out_linear_layer = nn.Linear(
            in_features=self.d_model,
            out_features=self.max_token_value
        )

    def forward(self, idx, targets=None):
        B, T = idx.shape

        # 位置编码（使用正弦和余弦函数）
        position_encoding_lookup_table = torch.zeros(self.context_length, self.d_model)
        position = torch.arange(0, self.context_length, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, self.d_model, 2).float() * (-math.log(10000.0) / self.d_model))
        # 使用正弦和余弦函数计算位置编码
        position_encoding_lookup_table[:, 0::2] = torch.sin(position * div_term)
        position_encoding_lookup_table[:, 1::2] = torch.cos(position * div_term)
        position_embedding = position_encoding_lookup_table[:T, :].to(device)

        # 前向传播
        x = self.token_embedding_lookup_table(idx) + position_embedding  # 词嵌入 + 位置编码
        x = self.transformer_blocks(x)  # 通过Transformer块
        logits = self.language_model_out_linear_layer(x)  # 生成logits

        # 如果提供了目标，计算损失
        if targets is not None:
            B, T, C = logits.shape
            logits_reshaped = logits.view(B * T, C)
            targets_reshaped = targets.view(B * T)
            loss = F.cross_entropy(logits_reshaped, targets_reshaped)
        else:
            loss = None
        return logits, loss

    def generate(self, idx, max_new_tokens):
        """生成新的token序列"""
        for _ in range(max_new_tokens):
            # 截取最后context_length个token
            idx_crop = idx[:, -self.context_length:]
            # 获取预测
            logits, loss = self(idx_crop)
            # 获取最后一个时间步的logits
            logits_last_timestep = logits[:, -1, :]
            # 计算概率分布
            probs = F.softmax(logits_last_timestep, dim=-1)
            # 从概率分布中采样
            idx_next = torch.multinomial(probs, num_samples=1)
            # 将新的token添加到序列中
            idx = torch.cat((idx, idx_next), dim=1)
        return idx

# 获取训练批次数据
def get_batch(split):
    """获取一个批次的训练或验证数据"""
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - context_length, (batch_size,))
    x = torch.stack([data[i:i+context_length] for i in ix])
    y = torch.stack([data[i+1:i+context_length+1] for i in ix])
    return x.to(device), y.to(device)

@torch.no_grad()
def estimate_loss():
    """估计训练和验证损失"""
    out = {}
    model.eval()  # 评估模式
    for split in ['train', 'valid']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()  # 恢复训练模式
    return out

# 初始化模型
model = TransformerLanguageModel()
model = model.to(device)

# 模型训练或加载
if os.path.exists('model-ckpt.pt'):
    print("发现已训练的模型文件，正在加载...")
    model.load_state_dict(torch.load('model-ckpt.pt'))
else:
    print("未找到已训练的模型文件，开始训练...")
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    tracked_losses = list()
    for step in range(max_iters):
        if step % eval_iters == 0 or step == max_iters - 1:
            losses = estimate_loss()
            tracked_losses.append(losses)
            print('Step:', step, 'Training Loss:', round(losses['train'].item(), 3), 'Validation Loss:',
                  round(losses['valid'].item(), 3))

        xb, yb = get_batch('train')
        logits, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

    # Save the model state dictionary
    torch.save(model.state_dict(), 'model-ckpt.pt')
    print("模型训练完成并保存")

# Generate
model.eval()
start = 'The salesperson'
start_ids = encoding.encode(start)
x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])
y = model.generate(x, max_new_tokens=100)
print('---------------')
print(encoding.decode(y[0].tolist()))
print('---------------')
