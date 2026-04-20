import os
from pathlib import Path
import pandas as pd
from datasets import load_dataset, load_from_disk

# Hugging Face 数据集默认缓存目录
DEFAULT_CACHE_DIR = os.path.expanduser('~/.cache/huggingface/datasets')

def load_and_show_dataset(dataset_name=None, local_path=None, split='train', num_samples=10):
    """
    加载本地的Huggingface数据集并打印前N条数据样例
    
    参数:
        dataset_name: 数据集名称，例如 'openai/gsm8k'，如果提供则从缓存加载
        local_path: 数据集的本地路径，如果提供则直接从该路径加载
        split: 数据集分片名称，默认为'train'
        num_samples: 要显示的样例数量，默认为10
    
    返回:
        加载的数据集对象
    """
    try:
        # 方式1: 通过数据集名称加载（使用本地缓存）
        if dataset_name:
            print(f"正在从本地缓存加载数据集: {dataset_name}")
            # 修复: 使用正确的参数
            if '/' in dataset_name:
                # 对于类似openai/gsm8k的数据集，需要指定配置名称
                repo_id, dataset_id = dataset_name.split('/')
                # 尝试加载main配置
                try:
                    dataset = load_dataset(dataset_name, 'main', split=split, trust_remote_code=True, 
                                          use_auth_token=False)
                except Exception as e:
                    print(f"加载main配置失败: {str(e)}，尝试不指定配置...")
                    # 如果main配置加载失败，尝试不指定配置
                    dataset = load_dataset(dataset_name, split=split, trust_remote_code=True)
            else:
                dataset = load_dataset(dataset_name, split=split, trust_remote_code=True)
        
        # 方式2: 通过本地路径直接加载
        elif local_path:
            print(f"正在从本地路径加载数据集: {local_path}")
            # 修复本地路径格式，确保使用正确的路径分隔符
            local_path = os.path.normpath(local_path)
            
            # 检查路径是否存在
            if not os.path.exists(local_path):
                # 尝试查找正确的路径
                print(f"路径不存在，尝试查找正确的路径...")
                for dataset_dir in Path(DEFAULT_CACHE_DIR).rglob('dataset_info.json'):
                    if dataset_name and dataset_name.replace('/', '___') in str(dataset_dir):
                        local_path = str(dataset_dir.parent)
                        print(f"找到可能的路径: {local_path}")
                        break
            
            # 加载数据集
            if os.path.exists(local_path):
                # 检查是否是arrow文件目录
                arrow_files = list(Path(local_path).glob('*.arrow'))
                if arrow_files:
                    print(f"找到Arrow文件，尝试直接加载数据集...")
                    # 尝试使用load_dataset加载本地arrow文件
                    try:
                        dataset = load_dataset('arrow', data_files=[str(f) for f in arrow_files], split=split)
                    except Exception as e:
                        print(f"加载Arrow文件失败: {str(e)}")
                        # 尝试使用load_from_disk
                        dataset = load_from_disk(local_path)
                else:
                    # 尝试使用load_from_disk
                    dataset = load_from_disk(local_path)
                
                # 如果数据集有分片，选择指定的分片
                if isinstance(dataset, dict) and split in dataset:
                    dataset = dataset[split]
            else:
                raise FileNotFoundError(f"找不到数据集路径: {local_path}")
        else:
            raise ValueError("必须提供 dataset_name 或 local_path 参数之一")
        
        # 打印数据集信息
        print(f"\n数据集加载成功!")
        print(f"数据集大小: {len(dataset)} 条记录")
        print(f"数据集字段: {', '.join(dataset.column_names)}")
        
        # 设置pandas显示选项，确保内容不被截断
        pd.set_option('display.max_colwidth', 80)
        pd.set_option('display.width', 1000)
        
        # 转换为DataFrame并显示样例
        df = dataset.to_pandas().head(num_samples)
        print(f"\n数据样例(前{num_samples}条):")
        print(df)
        
        # 恢复pandas默认设置
        pd.reset_option('display.max_colwidth')
        pd.reset_option('display.width')
        
        return dataset
    
    except Exception as e:
        print(f"加载数据集时出错: {str(e)}")
        
        # 如果加载失败，尝试列出可用的本地数据集
        if os.path.exists(DEFAULT_CACHE_DIR):
            print("\n可用的本地数据集:")
            for dataset_dir in Path(DEFAULT_CACHE_DIR).rglob('dataset_info.json'):
                try:
                    # 从目录名称中提取数据集名称
                    path_parts = str(dataset_dir.parent).split(os.sep)
                    dataset_name = None
                    config_name = None
                    
                    # 提取数据集名称和配置
                    for part in path_parts:
                        if "___" in part:
                            dataset_name = part.replace("___", "/")
                        elif part in ['main', 'socratic']:
                            config_name = part
                    
                    if dataset_name:
                        info_str = f"- {dataset_name}"
                        if config_name:
                            info_str += f" (配置: {config_name})"
                        info_str += f" (路径: {dataset_dir.parent})"
                        print(info_str)
                        
                        # 检查是否有arrow文件
                        arrow_files = list(Path(dataset_dir.parent).glob('*.arrow'))
                        if arrow_files:
                            print(f"  发现 {len(arrow_files)} 个Arrow文件")
                            for arrow_file in arrow_files[:3]:  # 只显示前3个
                                print(f"  - {arrow_file.name}")
                            if len(arrow_files) > 3:
                                print(f"  - ... 等 {len(arrow_files)-3} 个文件")
                except Exception:
                    continue
        return None

# 示例用法
if __name__ == "__main__":
    # 示例1: 通过数据集名称加载
    print("示例1: 通过数据集名称加载")
    dataset = load_and_show_dataset(dataset_name="openai/gsm8k")
    
    # 示例2: 通过本地路径加载
    print("\n示例2: 通过本地路径加载")
    # 使用从示例1中找到的实际路径
    if dataset is None:
        # 如果示例1加载失败，尝试直接使用缓存路径
        # 修正路径，指向包含arrow文件的目录
        local_dataset_path = os.path.join(DEFAULT_CACHE_DIR, "openai___gsm8k", "main", "0.0.0", "e53f048856ff4f594e959d75785d2c2d37b678ee")
        
        # 检查是否存在arrow文件
        arrow_files = list(Path(local_dataset_path).glob('*.arrow'))
        if arrow_files:
            print(f"找到 {len(arrow_files)} 个Arrow文件")
            # 使用第一个arrow文件的目录
            local_dataset_path = str(arrow_files[0].parent)
        else:
            print("未找到Arrow文件，尝试查找其他可能的路径")
    else:
        # 如果示例1成功，跳过示例2
        print("示例1已成功加载数据集，跳过示例2")
        exit()
        
    if os.path.exists(local_dataset_path):
        load_and_show_dataset(local_path=local_dataset_path)
    else:
        print(f"本地路径不存在: {local_dataset_path}")
        print("尝试查找可用的数据集路径...")
        load_and_show_dataset(dataset_name=None, local_path=None)  # 这将触发错误处理并列出可用数据集