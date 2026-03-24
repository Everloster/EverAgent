# CS 经典书籍索引（25部）

> 计算机科学必读教材与经典著作，覆盖算法、系统、语言、分布式等核心领域
> 创建日期：2026-03-24

---

## 选书原则

1. **经过时间检验**：大多数书至少已有10年影响力
2. **理论深度优先**：优先选择讲清"为什么"而非"怎么做"的书
3. **对应学习路径**：每本书均标注适合的 Phase

---

## 📐 理论基础与算法

### B01 | Introduction to Algorithms (CLRS)
**作者**：Cormen, Leiserson, Rivest, Stein
**版本**：第4版（2022）
**适合阶段**：Phase 2
**核心内容**：数据结构、排序、图算法、动态规划、贪心、摊还分析、NP完全性
**为什么读**：算法教材的"圣经"，覆盖面最广、证明最严谨。大学算法课的标准教材。
**阅读建议**：不需要逐章读完；重点：第6章（堆）、第15章（DP）、第22-25章（图）、第34章（NP）
**难度**：⭐⭐⭐⭐

---

### B02 | The Algorithm Design Manual
**作者**：Steven Skiena
**版本**：第3版（2020）
**适合阶段**：Phase 2
**核心内容**：算法设计策略 + 算法目录（War Stories，真实工程问题）
**为什么读**：比CLRS更注重实际应用，有大量"如何将实际问题转化为标准算法"的案例。
**阅读建议**：与CLRS互补；第二部分的算法目录可作为工具书使用
**难度**：⭐⭐⭐

---

### B03 | Structure and Interpretation of Computer Programs (SICP)
**作者**：Harold Abelson & Gerald Jay Sussman
**版本**：第2版（1996，MIT免费在线）
**适合阶段**：Phase 1
**核心内容**：计算的本质、抽象、递归、流处理、元循环解释器、编译器
**为什么读**：MIT 18年的本科入门教材；Lisp/Scheme 代码，但思想超越语言。被誉为"CS领域最重要的教材"。
**阅读建议**：至少读完前3章；第4-5章（解释器/编译器）是进阶宝藏
**难度**：⭐⭐⭐（概念密度高，但例子清晰）
**在线版**：https://mitpress.mit.edu/sicp/

---

### B04 | Concrete Mathematics
**作者**：Graham, Knuth, Patashnik
**版本**：第2版（1994）
**适合阶段**：Phase 1-2（数学基础）
**核心内容**：求和、递推、生成函数、组合数学、概率、数论
**为什么读**：算法分析所需的数学工具书；Knuth 的写作风格独特（页边注）
**阅读建议**：选读需要的章节；第2章（求和）、第7章（生成函数）最实用
**难度**：⭐⭐⭐⭐

---

### B05 | The Art of Computer Programming (TAOCP)
**作者**：Donald Knuth
**卷数**：已出版4卷（Vol.1-4A）
**适合阶段**：Phase 2+（参考书）
**核心内容**：基本算法、半数值算法、排序与搜索、组合算法
**为什么读**：算法领域的终极参考书，Knuth 毕生之作。Bill Gates 曾说"如果你能读懂整套TAOCP，请给我发你的简历。"
**阅读建议**：作为参考书使用，而非通读；Vol.1 第1章适合通读
**难度**：⭐⭐⭐⭐⭐

---

## 🖥️ 操作系统

### B06 | Operating Systems: Three Easy Pieces (OSTEP)
**作者**：Remzi H. Arpaci-Dusseau & Andrea C. Arpaci-Dusseau
**版本**：在线免费，持续更新
**适合阶段**：Phase 3
**核心内容**：虚拟化（CPU/内存）、并发、持久化（文件系统）
**为什么读**：目前最好的OS入门教材。写作风格轻松，概念清晰，与 xv6 实验配合使用。
**在线版**：https://pages.cs.wisc.edu/~remzi/OSTEP/
**难度**：⭐⭐⭐

---

### B07 | Computer Systems: A Programmer's Perspective (CS:APP)
**作者**：Bryant & O'Hallaron
**版本**：第3版（2015）
**适合阶段**：Phase 3
**核心内容**：从程序员视角理解计算机系统：数据表示、汇编、内存层次结构、链接、异常控制流、虚拟内存、I/O
**为什么读**：CMU 15-213 的教材；填补"会写代码但不理解底层"的知识空白。Lab 实验（Bomb Lab、Shell Lab等）极具价值。
**难度**：⭐⭐⭐

---

### B08 | The Design of the UNIX Operating System
**作者**：Maurice J. Bach
**版本**：1986
**适合阶段**：Phase 3
**核心内容**：Unix 内核实现：缓冲区缓存、文件系统、进程、内存管理、IPC
**为什么读**：从代码层面理解 Unix 内核；Linux 内核学习者的预备读物
**难度**：⭐⭐⭐⭐

---

## 🌐 计算机网络

### B09 | Computer Networks: A Top-Down Approach
**作者**：Kurose & Ross
**版本**：第8版（2021）
**适合阶段**：Phase 3
**核心内容**：从应用层到物理层，协议设计、DNS、HTTP、TCP/IP、路由算法、网络安全
**为什么读**：网络教材中可读性最强；自顶向下的顺序符合直觉；wireshark 实验实用
**难度**：⭐⭐⭐

---

### B10 | TCP/IP Illustrated, Volume 1
**作者**：W. Richard Stevens
**版本**：第2版（2011）
**适合阶段**：Phase 3（网络深化）
**核心内容**：TCP/IP 协议的详细解析，大量真实抓包分析
**为什么读**：网络工程师必备；理解 TCP 状态机的最佳参考书
**难度**：⭐⭐⭐（参考书，选读）

---

## 🗄️ 数据库

### B11 | Readings in Database Systems (Red Book)
**作者**：Bailis, Hellerstein, Stonebraker（编）
**版本**：第5版（在线免费）
**适合阶段**：Phase 3-4
**核心内容**：数据库领域经典论文集，含编者点评
**为什么读**：数据库研究者的必读论文集；每篇论文有编者的现代解读，极有价值
**在线版**：http://www.redbook.io/
**难度**：⭐⭐⭐（论文集，选读）

---

### B12 | Database Internals
**作者**：Alex Petrov
**版本**：2019
**适合阶段**：Phase 3-4
**核心内容**：存储引擎（B-Tree、LSM-Tree）、分布式系统（共识、复制、一致性）的内部实现
**为什么读**：填补"会用数据库但不了解内部"的空白；RocksDB、TiKV 等现代引擎的原理解析
**难度**：⭐⭐⭐

---

## 📡 分布式系统

### B13 | Designing Data-Intensive Applications (DDIA)
**作者**：Martin Kleppmann
**版本**：2017（中文版：数据密集型应用系统设计）
**适合阶段**：Phase 4
**核心内容**：数据模型、存储引擎、编码、复制、分片、事务、流处理
**为什么读**：目前工程师学习分布式系统最佳的单本书；理论扎实，工程实践导向。
**难度**：⭐⭐⭐

---

### B14 | Distributed Systems: Principles and Paradigms
**作者**：Tanenbaum & Van Steen
**版本**：第3版（2017，在线免费）
**适合阶段**：Phase 4
**核心内容**：通信、命名、同步、一致性与复制、容错、安全
**为什么读**：分布式系统的系统性教材，理论完整
**难度**：⭐⭐⭐

---

## ⚙️ 编程语言与编译器

### B15 | Compilers: Principles, Techniques, and Tools (Dragon Book)
**作者**：Aho, Lam, Sethi, Ullman
**版本**：第2版（2006）
**适合阶段**：Phase 5
**核心内容**：词法分析、语法分析、语义分析、中间代码生成、优化、目标代码生成
**为什么读**：编译器领域的权威教材；理解 LLVM、GCC 的理论基础
**难度**：⭐⭐⭐⭐

---

### B16 | Types and Programming Languages (TAPL)
**作者**：Benjamin C. Pierce
**版本**：2002
**适合阶段**：Phase 5
**核心内容**：类型系统理论：简单类型系统、多态、子类型、递归类型、System F
**为什么读**：理解 Rust/Haskell/TypeScript 类型系统的理论基础；编程语言理论研究的入门书
**难度**：⭐⭐⭐⭐⭐（形式化程度高）

---

### B17 | Programming Language Pragmatics
**作者**：Michael L. Scott
**版本**：第4版（2015）
**适合阶段**：Phase 5
**核心内容**：语言设计、词法与语法、语义、类型、控制流、数据抽象、并发
**为什么读**：比 Dragon Book 更注重语言设计决策的权衡；适合想理解"为什么Python/Java/C++是这样设计的"
**难度**：⭐⭐⭐

---

## 🔒 安全与密码学

### B18 | Introduction to Modern Cryptography
**作者**：Katz & Lindell
**版本**：第3版（2020）
**适合阶段**：Phase 6
**核心内容**：完美保密性、计算安全性、对称加密（AES）、消息认证码、公钥密码学（RSA/ECC）、数字签名
**为什么读**：密码学的严谨入门书；以可证明安全为基础，不只讲实现
**难度**：⭐⭐⭐⭐

---

### B19 | Computer Security: Art and Science
**作者**：Matt Bishop
**版本**：第2版（2018）
**适合阶段**：Phase 6
**核心内容**：安全策略、访问控制、密码学、认证、恶意代码、网络安全、形式化方法
**为什么读**：系统安全的全面教材，覆盖从理论到实践
**难度**：⭐⭐⭐

---

## 🛠️ 软件工程与系统设计

### B20 | The Mythical Man-Month
**作者**：Fred Brooks
**版本**：20周年纪念版（1995）
**适合阶段**：Phase 1+（随时可读）
**核心内容**：软件项目管理的经验教训，包含"No Silver Bullet"论文
**为什么读**：1975年写成，但关于软件复杂性的洞察至今有效。每位软件工程师的必读书。
**难度**：⭐（随笔风格，不需技术背景）

---

### B21 | A Philosophy of Software Design
**作者**：John Ousterhout
**版本**：第2版（2021）
**适合阶段**：Phase 2+
**核心内容**：复杂性的本质、模块深度vs宽度、注释的哲学、错误处理
**为什么读**：Raft 算法作者的软件设计哲学；对抗"战术编程"、提倡"战略编程"的简洁宣言
**难度**：⭐⭐

---

### B22 | Clean Code
**作者**：Robert C. Martin（"Uncle Bob"）
**版本**：2008
**适合阶段**：Phase 2+
**核心内容**：命名、函数、注释、格式、对象、错误处理、测试
**为什么读**：工程实践入门；与 B21 互补（B21 更偏设计，B22 更偏代码层面）
**注意**：部分观点有争议（如"所有注释都是代码臭味"），需批判性阅读
**难度**：⭐⭐

---

## 📖 历史与文化

### B23 | Hackers: Heroes of the Computer Revolution
**作者**：Steven Levy
**版本**：1984（25周年纪念版2010）
**适合阶段**：任何阶段（背景阅读）
**核心内容**：MIT AI Lab、游戏黑客、个人电脑革命的历史叙事
**为什么读**：理解黑客文化和开源精神的起源；了解 Stallman、Woz、Jobs 等人物的真实背景
**难度**：⭐（历史叙事）

---

### B24 | The Innovators
**作者**：Walter Isaacson
**版本**：2014
**适合阶段**：任何阶段（背景阅读）
**核心内容**：从 Ada Lovelace 到 Larry Page，计算机发明者的群像传记
**为什么读**：补充 CS 发展时间线的人物故事；理解技术突破是如何被特定历史条件所催生的
**难度**：⭐（传记叙事）

---

### B25 | Code: The Hidden Language of Computer Hardware and Software
**作者**：Charles Petzold
**版本**：第2版（2022）
**适合阶段**：Phase 1（零基础）
**核心内容**：从摩斯电码到逻辑门，从加法器到操作系统，用最直觉的方式解释计算机的工作原理
**为什么读**：计算机工作原理的最佳科普书；完全不需要编程背景；适合 CS 零基础入门
**难度**：⭐（科普读物）

---

## 按学习阶段速查

```
Phase 1 基础入门：B03（SICP）、B04（Concrete Math）、B25（Code）、B20（人月神话）
Phase 2 算法：    B01（CLRS）、B02（Algorithm Design Manual）、B21（软件设计哲学）
Phase 3 系统：    B06（OSTEP）、B07（CS:APP）、B09（计算机网络）、B08（Unix内核）
Phase 4 分布式：  B13（DDIA）、B11（Red Book）、B12（Database Internals）
Phase 5 语言：    B15（Dragon Book）、B16（TAPL）、B17（PL Pragmatics）
Phase 6 安全：    B18（现代密码学）、B19（计算机安全）
背景阅读：        B23（Hackers）、B24（The Innovators）
```
