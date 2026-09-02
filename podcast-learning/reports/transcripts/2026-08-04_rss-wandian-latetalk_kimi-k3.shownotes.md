# 晚点聊 177 详解Kimi K3 — shownotes

> Episode 177｜2026-08-04｜1hr55mins

```
晚点聊 LateTalk 177: 详解Kimi K3：强到冲击Anthropic估值的模型什么样？
    
    
    
    
    
    
    
    
    
    
    
      
    
    
    
    
    
    
      
  
  
  
  
  
  
  
  
  
  
    	
  
  
  
  
  
  
  
  
  
  
      
  
    
    
Skip to content
    
  
    
  
    
    
    
  
  
    
Episodes
      
Host
      
Search
      
晚点 LatePost
    
通过 RSS 订阅晚点聊 LateTalk
  
  
  
    
        
    详解Kimi K3：强到冲击Anthropic估值的模型什么样？
  
  
      
        Episode 177
      
      
·
    
      August 4th, 2026
    
    
·
    
      1 hr 55 mins
    
  
  
  
    
    
  
  
      
 RSS
      
 Spotify
      
    
 Share
  
  
  
    
      
        About this Episode
      
    
    
「开源了权重，没开源产生权重的 “流水线”。」
本期我们邀请 RadixArk 创始成员赵晨阳和华盛顿大学博士生曾致远，从推理与算法两条线拆解 K3：它真的比肩 fable 吗？3T 开放权重、混合注意力和智能体训练环境意味着什么？以及开源模型真正开放了什么、又保留了什么？
晨阳是老朋友，他曾在 163 期节目中为我们从 Infra 角度解读了 DeepSeek-V4。在 UCLA 读博期间，晨阳成为 SGLang 核心开发者，SGLang 第一时间适配了 V4 、K3、GLM 5.2 等中国开源模型。
曾致远目前在华盛顿大学读博士二年级，研究大语言模型，师从 Hannaneh Hajishirzi 教授和 Pang Wei Koh 助理教授。
进入具体的技术报告解读前，我们也聊了 K3 如今在美国 AI 界和更广泛的投资市场所引起的巨大关注，以及与 K3 直接相关的开源大辩论。
本期节目已发布图文版，
详解 Kimi K3：强到冲击 Anthropic 估值的模型什么样？丨晚点播客
下面，正式进入节目吧。
本期嘉宾：
赵晨阳，RadixArk 与 SGLang 创始成员
曾致远，华盛顿大学计算机科学博士生
本期主播：
曼祺，《晚点 LatePost》科技报道负责人
时间线跳转：
-K3 为什么成为里程碑
05:13 使用体感：长程任务、惊艳的前端能力与被吐槽的不足
11:15 K3 引发的开源、安全与估值大辩论
16:50 Transformer 的「忒修斯之船」
25:34 贵不贵、慢不慢，看单价之外的任务总成本
29:25 K3 为什么现在慢？新架构、Serving Stack 与前缀复用
34:42 权重一旦开放就收不回；真正的护城河在环境、验证和算力
-KDA（K3 采用的注意力） 和 KDA（kenerl 开发 agent），说不好哪个更伟大？
39:36 架构总览：让信息沿序列与深度更高效流动
42:42 Quantile Balancing：近千个专家如何保持负载均衡
48:38 KDA＋MLA：线性注意力与全局注意力并非二选一
54:12 线性注意力下，百万上下文如何缓解遗忘
57:27 线性注意力给推理系统带来的工程变化
01:00:54 6.3 倍解码加速来自哪里
01:03:34 Attention Residuals：让深层模型选择性读取浅层信息
-优化器、后训练与自动研究
01:10:23 Per-head Muon 与大规模训练稳定性
01:14:46 AI 能否自己发明优化器
01:20:34 MOPD：九个领域专家为什么先分后合
01:27:11 蒸馏的纯技术定义、on-policy 蒸馏与 off-policy 蒸馏的区别
-Infra 优化
01:31:08 KDA 结构下，投机采样回退机制的变化
01:39:47 Flash KDA、QAT 与训练—推理一致
-后面有什么？
01:46:50 下一个开源最强，以及开源能否超过闭源
01:48:29 持续学习、评测与模型平台期
剪辑：甜食
相关链接：
Kimi K3 官方技术博客
Kimi K3: Open Frontier Intelligence（技术报告）
Kimi Linear: An Expressive, Efficient Attention Architecture
Open Weights and American AI Leadership
163 期：
详解 DeepSeek V4：Infra 巨鲸、百万上下文走进现实、极致效率优化
143 期：
阿里、Kimi 都在用的 DeltaNet 是什么？｜与杨松琳聊线性注意力新改进
104 期：
我给线性注意力找“金主”，字节 say No，MiniMax say Yes
103 期：
用 Attention 串起大模型优化史，详解 DeepSeek、Kimi 最新注意力机制改进
详解 DeepSeek V4：Infra 巨鲸“四连击”，百万上下文走进现实
再谈注意力：阿里、Kimi 都在用的 DeltaNet 和线性注意力新改进丨晚点播客
3700 次预训练寻找“线性注意力”非共识，MiniMax-01 开发者讲述 4 年探索
大模型“注意力简史”：与两位 AI 研究者从 DeepSeek、Kimi 最新改进聊起
附录：
KDA（Kimi Delta Attention）：Kimi 提出的线性注意力机制，用固定大小的循环状态压缩历史信息，降低长上下文的计算与存储开销。
Flash KDA：KDA 的高性能 Kernel 实现，通过重叠 chunk 内计算与 chunk 间状态传输，减少计算空转。
Kernel Development Agent（KDA）：用于编写、测试和优化 GPU Kernel 的智能体；缩写同样是 KDA。
MLA（Multi-head Latent Attention）：通过低秩表示压缩 Key-Value Cache；K3 用少量 MLA 层补充对全局上下文的直接访问。
混合注意力（Hybrid Attention）：在同一模型中组合不同注意力机制；K3 采用 3 层 KDA 搭配 1 层 MLA。
NoPE（No Positional Encoding）：不显式加入位置编码，序列位置信息主要由 KDA 的递推、门控与衰减提供。
Attention Residuals（AttnRes）：让模型选择性读取较浅层的历史表示，改善信息沿深度方向的流动。
mHC（Manifold-Constrained Hyper-Connections）：DeepSeek V4 的多通路残差连接方案，与 AttnRes 都用于改善层间信息流。
MoE（Mixture of Experts）：每个 token 只激活少数专家子网络，以较低计算量承载更大的总参数规模。
Stable LatentMoE：K3 的 MoE 方案，共有 896 个路由专家，每个 token 激活其中 16 个。
负载均衡（Load Balancing）与 Quantile Balancing：负载均衡避免 token 过度集中到少数专家；K3 按路由分数的分位数分配专家。
Muon、MuonClip 与 Per-Head Muon：Muon 对更新方向做近似正交化；K2 用 MuonClip 稳定注意力，K3 则按注意力头分别优化。
知识蒸馏（Knowledge Distillation）：让教师模型把能力传递给学生模型，可用于模型压缩或多种能力合并。
Checkpoint：训练过程中保存的模型参数及相关状态快照，可用于恢复、比较或更新模型。
消融实验（Ablation Study）：移除或替换某个组件并比较效果，以判断它是否真正有贡献。
MOPD（Multi-Teacher On-Policy Distillation）：K3 先训练多个领域教师，再把它们的能力在线蒸馏进统一学生模型。
On-policy 蒸馏：学生生成轨迹，教师对这些轨迹提供监督，数据分布更贴近学生当前策略。
Off-policy 蒸馏：学生学习教师预先生成的数据，实施更方便，但可能存在分布偏移。
投机采样（Speculative Decoding）：小模型先猜一批 token，大模型再集中验证，以提高生成速度。
前缀缓存（Prefix Cache）：复用相同提示词前缀的中间计算结果，避免重复计算。
Persistent Rollout：未完成的长轨迹可暂停并在后续轮次继续，减少长尾任务对整批采样的阻塞。
Off-policy Mismatch：训练数据并非由当前模型策略生成，常来自旧 Checkpoint 或不同的推理配置。
Agent 训练环境与 Harness：环境提供工具、沙箱和奖励；Harness 组织提示词、工具、上下文、Skills 与 Memory。
QAT（Quantization-Aware Training）：训练时模拟低精度计算，让模型提前适应量化误差。
忒修斯之船（Ship of Theseus）：节目用这一比喻形容部件不断被替换、却仍沿用 Transformer 名字的模型架构。
持续学习（Continual Learning）与 RSI：持续学习指模型从新任务和反馈中继续更新；RSI 指系统递归改进自身能力。
小红书@
曼祺_火柴Q
即刻@
曼祺_火柴Q
☆《晚点聊 LateTalk》建立「 播客听友群」啦！☆
欢迎关注科技、商业大公司动态和创业创新的小伙伴进群交流，第一时间收听新节目。
这里有更多互动，更多话题讨论。欢迎贡献选题 & 推荐嘉宾。
请先添加「晚点」小助手的微信号，
备注：“晚点聊”
，我们邀请您入群。
关注公众号《晚点 LatePost》和《晚点对话》，阅读更多商业、科技文章：
  
  
      
        
          Episode Host
        
      
      
          
            
              
              程曼祺 Manqi Cheng
          
      
    
      
        Episode Details
      
    
    
      
        
        August 4th, 2026
      
      
        
        1 hr 55 mins 18 secs
      
        
          
 Link with Timestamp
        
        
          
 Download MP3 (106 MB)
        
    
  
  
      
← Previous episode
      
Next episode →
  
  
    
      晚点聊 LateTalk
    
        by 北京晚达科技有限公司 is licensed under 
CC Attribution + NonCommercial (BY-NC)
  
  
    
Episodes
      
Host
      
Search
      
晚点 LatePost
    
通过 RSS 订阅晚点聊 LateTalk
  
  
    Share This Episode
  
  
    
      
Episode Link
      
      
A direct link to this episode page.
      
Embeddable Audio Player
      
      
Paste this code to embed an HTML5 audio player with controls.
      
Download URL
      
      
Useful if you want to create a direct download link, embed in your own player, post from another publishing engine, link to from Patreon, etc.'
    
Social Network Quick Links
    
      
        Tweet
      
      
    
  
    
  
    
    
Powered by Fireside
```
