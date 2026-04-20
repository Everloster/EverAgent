import sys
import platform
import psutil
import torch
import cpuinfo

def check_hardware():
    print("系统信息:")
    print(f"操作系统: {platform.system()} {platform.version()}")
    print(f"Python版本: {sys.version.split()[0]}")
    
    # CPU信息
    cpu_info = cpuinfo.get_cpu_info()
    print("\nCPU信息:")
    print(f"CPU型号: {cpu_info['brand_raw']}")
    print(f"CPU核心数: {psutil.cpu_count(logical=False)} (物理核心)")
    print(f"CPU线程数: {psutil.cpu_count(logical=True)} (逻辑核心)")
    
    # 内存信息
    memory = psutil.virtual_memory()
    print("\n内存信息:")
    print(f"总内存: {memory.total / (1024**3):.2f} GB")
    print(f"可用内存: {memory.available / (1024**3):.2f} GB")
    print(f"内存使用率: {memory.percent}%")
    
    # CUDA信息
    print("\nGPU/CUDA信息:")
    print(f"PyTorch版本: {torch.__version__}")
    print(f"CUDA是否可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA版本: {torch.version.cuda}")
        print(f"当前GPU设备: {torch.cuda.get_device_name()}")
        print(f"GPU数量: {torch.cuda.device_count()}")
        print(f"当前GPU显存总量: {torch.cuda.get_device_properties(0).total_memory / (1024**2):.2f} MB")
        print(f"当前GPU显存占用: {torch.cuda.memory_allocated() / (1024**2):.2f} MB")
        print(f"当前GPU显存缓存: {torch.cuda.memory_reserved() / (1024**2):.2f} MB")

    # vLLM检查
    print("\nvLLM状态检查:")
    try:
        import vllm
        print(f"✓ vLLM已安装，版本: {vllm.__version__}")
        try:
            import vllm._C
            print("✓ vLLM C++扩展已正确编译")
            # 检查CUDA兼容性
            if hasattr(vllm, 'cuda_available') and vllm.cuda_available():
                print("✓ vLLM CUDA支持正常")
            else:
                print("! vLLM CUDA支持异常，请检查CUDA安装")
        except ImportError:
            print("! vLLM C++扩展未正确编译，需要重新安装")
    except ImportError:
        print("! vLLM未安装，请使用命令安装：pip install vllm")

    # 训练兼容性评估
    print("\n训练兼容性评估:")
    if torch.cuda.is_available():
        print("✓ GPU可用，支持加速训练")
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if gpu_mem >= 8:
            print("✓ GPU显存充足，可以进行中等规模模型训练")
        else:
            print("! GPU显存较小，建议减小batch_size或模型大小")
    else:
        print("! 未检测到GPU，将使用CPU训练（速度较慢）")
    
    if memory.total / (1024**3) >= 16:
        print("✓ 系统内存充足")
    else:
        print("! 系统内存可能不足，建议关闭其他程序")

if __name__ == "__main__":
    check_hardware()