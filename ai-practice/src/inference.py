import os
import torch
import tiktoken
from model import TransformerLanguageModel, device, d_model, context_length, num_blocks, num_heads, dropout

def load_model():
    # 初始化模型
    model = TransformerLanguageModel()
    model = model.to(device)
    
    # 加载已保存的模型权重
    if os.path.exists('model-ckpt.pt'):
        model.load_state_dict(torch.load('model-ckpt.pt'))
        print(f"模型已从 model-ckpt.pt 加载")
    else:
        print("错误：找不到模型文件 model-ckpt.pt")
        exit(1)
    
    model.eval()
    return model

def generate_text(model, prompt, max_tokens=100):
    # 初始化tokenizer
    encoding = tiktoken.get_encoding("cl100k_base")
    
    # 编码输入文本
    start_ids = encoding.encode(prompt)
    x = torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...]
    
    # 生成文本
    y = model.generate(x, max_new_tokens=max_tokens)
    
    # 解码并返回生成的文本
    return encoding.decode(y[0].tolist())

def main():
    # 加载模型
    model = load_model()
    
    print("欢迎使用文本生成模型！")
    print("输入 'quit' 或 'exit' 退出程序")
    
    while True:
        # 获取用户输入
        prompt = input("\n请输入提示词: ")
        
        # 检查是否退出
        if prompt.lower() in ['quit', 'exit']:
            break
            
        # 如果输入为空，跳过
        if not prompt.strip():
            continue
            
        try:
            # 生成文本
            generated_text = generate_text(model, prompt)
            print("\n生成的文本:")
            print("---------------")
            print(generated_text)
            print("---------------")
        except Exception as e:
            print(f"生成过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()