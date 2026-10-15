# 计算机网络 —— 传输层（Chapter 6 The Transport Layer）

> 来源课件：`D:\Escherichia30636\计算机网络\Chapter6 The Transport Layer.pdf`，共 114 页
> 整理日期：2026-10-15
> 全文按课件原有的章—节—小节顺序组织（6.1 至 6.7），小节编号在课件未给出时按层级补齐，术语与符号沿用课件原文。

本章要掌握两类内容。第一类是传输层各项服务背后的原理：多路复用与多路分解（multiplexing, demultiplexing）、可靠数据传输（reliable data transfer）、流量控制（flow control）、拥塞控制（congestion control）。第二类是 Internet 实际使用的传输层协议：UDP（无连接传输）、TCP（面向连接的可靠传输）以及 TCP 的拥塞控制。展开顺序因此是：先讲传输层共性的服务原理，再逐个讲解 UDP 与 TCP 的具体实现，最后回到拥塞控制的原理与 TCP 的具体算法。

## 6.1 传输层服务（Transport-Layer Services）

### 6.1.1 传输层的定位与端到端逻辑通信

传输层为运行在不同主机上的应用进程（app process）之间提供**逻辑通信**（logical communication）。这里的"逻辑"指的是：应用进程看到的是一条直接把两个进程连起来的通路，而实际的数据要经过中间的网络层、数据链路层和物理层设备逐跳转发，两个进程之间并没有一条独占的物理线路。

传输层协议运行在**端系统**（end system）中，不在路由器中运行。在发送端，传输层把应用层交下来的应用报文（app message）分割为若干**报文段**（segment），再交给网络层；在接收端，传输层把收到的报文段重新组装为报文，交给应用层。分段、传输、重组是传输层的基本职责。

对同一个应用，可用的传输层协议通常不止一个。在 Internet 中，应用可以选择 TCP 或 UDP，两者提供的服务差别很大，应用按自身需求选择。

### 6.1.2 传输层与网络层的分工（Transport vs. Network Layer）

网络层提供的是**主机到主机**（host-to-host）的逻辑通信，传输层提供的是**进程到进程**（process-to-process）的逻辑通信。二者的服务对象不同：网络层不区分同一台主机上具体是哪个进程在收发数据，传输层则要把数据准确地交付给主机内的某个进程。

课件用一组逐项对应关系说明这两层的分工（课件称 household analogy，"12 个孩子给 12 个孩子寄信"）：

| 家庭寄信的对应物 | 网络中的对应物 |
|---|---|
| kids（孩子） | processes（进程） |
| letters in envelopes（信封中的信件） | app messages（应用报文） |
| houses（房屋） | hosts（主机） |
| postal service（邮政服务） | network-layer protocol（网络层协议） |
| Ann and Bill（负责分拣、转交孩子信件的人） | transport protocol（传输协议） |

这组对应关系说明的核心事实是：邮政系统只负责把信件送到正确的房屋（网络层把分组送到正确的主机），而把信件交到同一房屋内正确的孩子手上需要另外一个角色来完成（传输层把报文段交给正确的进程）。传输层的这段职责就是 6.2 节的多路分解。

### 6.1.3 Internet 传输层协议提供的服务

Internet 有两个传输层协议，能力不同：

- **TCP（Transmission Control Protocol）**：提供可靠的、按序的交付（reliable, in-order delivery）。在可靠交付之上，TCP 还提供拥塞控制（congestion control）、流量控制（flow control）和连接建立（connection setup）。
- **UDP（User Datagram Protocol）**：提供不可靠的、无序的交付（unreliable, unordered delivery）。它是"尽力而为"（best-effort）的 IP 服务的无附加功能扩展（no-frills extension）。

Internet 传输层**不提供**的服务包括：

- 延迟保证（delay guarantees）；
- 带宽保证（bandwidth guarantees）。

也就是说，使用 TCP 或 UDP 的应用都不能向传输层要求"这段数据必须在多少毫秒内到达"或"必须占用多少带宽"。时延和带宽的保证只能由应用层自己设法处理，或者由网络中的其他机制在有限范围内近似实现。

## 6.2 多路复用与多路分解（Multiplexing and Demultiplexing）

### 6.2.1 基本概念

**多路复用（multiplexing）发生在发送端**：传输层处理来自多个套接字（socket）的数据，为每份数据加上传输层首部（transport header），首部信息在接收端用于多路分解。

**多路分解（demultiplexing）发生在接收端**：主机根据首部信息，把收到的报文段交付给正确的套接字。

课件用三台主机的拓扑说明这一对操作：左侧主机在应用层有进程 P3，其传输层有一个套接字；中间主机在应用层有进程 P1 与 P2，其传输层有两个套接字；右侧主机在应用层有进程 P4，其传输层有一个套接字。发送端多个套接字的数据先被加上传输层首部，再经网络层向下传递；接收端沿用首部中的信息，将报文段上交给对应的套接字。要点是：多路复用与多路分解是一对互逆的操作，复用靠"加首部"，分解靠"读首部"。

### 6.2.2 多路分解的工作过程

主机收到的是 IP 数据报（IP datagram）。多路分解依赖以下事实：

- 每个数据报都带有**源 IP 地址**和**目的 IP 地址**；
- 每个数据报承载**一个**传输层报文段；
- 每个报文段都带有**源端口号**与**目的端口号**。

主机用 IP 地址与端口号共同决定把报文段送往哪个套接字。

TCP/UDP 报文段的通用格式为：最前面是 32 位的首部第一行，其中左边 16 位为源端口号（source port #），右边 16 位为目的端口号（dest port #）；其后是其他首部字段（other header fields，如长度、校验和等）；再往后是应用数据（application data，即 payload，载荷）。

需要区分几个编号：

- **端口号**（port number）是 16 位量，标识主机内的一个套接字；
- **IP 地址**是 32 位量（IPv4），标识网络中的一台主机。

两者结合才能唯一定位一台主机上的一个进程端点。

### 6.2.3 熟知端口号（Well-known Port Number）

端口号的分配有两类方式：一类由标准固定分配给知名服务，称为熟知端口号；另一类由操作系统在进程创建套接字时动态分配，称为临时端口号（ephemeral port number）。课件给出的一组常见服务及其熟知端口号，按 UDP / TCP 分类如下：

| 应用协议 | 端口号 | 所属传输协议 |
|---|---|---|
| RIP（Routing Information Protocol） | 520 | UDP |
| DNS（Domain Name System） | 53 | UDP |
| TFTP（Trivial File Transfer Protocol） | 69 | UDP |
| SNMP（Simple Network Management Protocol） | 161 | UDP |
| DHCP（Dynamic Host Configuration Protocol） | 67/68 | UDP |
| SMTP（Simple Mail Transfer Protocol） | 25 | TCP |
| FTP（File Transfer Protocol） | 21/20 | TCP |
| BGP（Border Gateway Protocol） | 179 | TCP |
| HTTP（HyperText Transfer Protocol） | 80 | TCP |
| HTTPS（HTTP Secure） | 443 | TCP |

课件在此处强调：**端口号只具有本地意义**（The port number only has local meaning），同一端口号出现在不同计算机上时彼此没有关系。原因是端口号只用于在**本主机内部**区分套接字，它的作用范围止于该主机；跨主机的寻址由 IP 地址承担。因此 A 主机上的 80 端口与 B 主机上的 80 端口是两个互不相关的端点，只是恰好编号相同。

### 6.2.4 无连接的多路分解（Connectionless Demultiplexing）

UDP 套接字在创建时被赋予一个**主机本地端口号**（host-local port #）。课件给出的代码片段为：

```c
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('', 10000))
```

`AF_INET` 表示使用 IPv4 地址族，`SOCK_DGRAM` 表示使用数据报（UDP）套接字，`bind` 把该套接字绑定到本机端口 10000 上。发送时，向 UDP 套接字写入数据报必须指定**目的 IP 地址**与**目的端口号**。

接收端的行为规则有两条：

1. 主机收到 UDP 报文段后，检查报文段中的目的端口号；
2. 把该 UDP 报文段交付给具有该端口号的套接字。

由此得到无连接多路分解的关键性质：**目的端口号相同、但源 IP 地址和/或源端口号不同的 IP 数据报，会被交付到目的主机上的同一个套接字**。也就是说，UDP 套接字只由"目的端口号"这一个本地量区分（外加目的 IP 地址用于定位主机），它不区分对端是谁，凡是指向同一目的端口的报文都汇集到同一个套接字。

### 6.2.5 无连接多路分解示例

三台主机的示例中，各套接字的绑定端口为：

- 左侧主机上，进程 P3 的套接字调用 `clientSocket.bind(('', 9157))`，绑定本机端口 9157；
- 中间主机是服务器主机，进程 P1 的套接字调用 `serverSocket.bind(('', 6428))`，绑定本机端口 6428；
- 右侧主机上，进程 P4 的套接字调用 `clientSocket.bind(('', 5775))`，绑定本机端口 5775。

图中标出的报文段及其端口字段如下（按图中所标逐条列出）：

| 图中位置 | 源端口 | 目的端口 |
|---|---|---|
| 左侧主机与服务器之间的报文 | 9157 | 6428 |
| 服务器与左侧主机之间的报文 | 6428 | 9157 |
| 右侧主机与服务器之间的报文 | ？ | ？ |
| 服务器与右侧主机之间的报文 | ？ | ？ |

其中右侧主机与服务器之间两段报文的端口字段在原图中标为"？"，即原图未给出数值。

补充说明（非课件原文）：在 UDP 中，若应用没有显式调用 `bind` 指定本地端口，操作系统会在首次发送时为该套接字分配一个临时端口号；该端口号在调用发生之前无法预先写在图上，因此图中用"？"占位。此说明仅为解释"？"的成因，不代表课件给出了具体数值。

本例要说明的规则与 6.2.4 一致：服务器主机在 6428 端口上只有一个 UDP 套接字，凡目的端口为 6428 的报文段（不论其源 IP 地址、源端口号为何）都被分解到这一个套接字，交给进程 P1。

### 6.2.6 面向连接的多路分解（Connection-Oriented Demultiplexing）

TCP 套接字由**四元组**（4-tuple）标识：

- 源 IP 地址（source IP address）；
- 源端口号（source port number）；
- 目的 IP 地址（dest IP address）；
- 目的端口号（dest port number）。

多路分解时，接收端使用全部四个值来决定把报文段送往哪个套接字。这种分解方式带来两个直接结果：

1. **服务器主机可以同时支持多个 TCP 套接字**，每个套接字由各自的四元组唯一标识。与 UDP 不同，TCP 服务器不是把所有到达同一端口的报文都交给同一个套接字。
2. **Web 服务器为每个连接的客户建立不同的套接字**。对于非持久 HTTP（non-persistent HTTP），每一个请求都建立新的连接，因此每个请求使用不同的套接字。

四元组中的源 IP 地址与源端口号把来自不同客户的连接区分开，这是"面向连接"在传输层多路分解上的具体体现：套接字不再只由本地端口标识，而是由一整条连接的四个端点值标识。

### 6.2.7 面向连接多路分解示例

课件给出同一拓扑的两个版本。

拓扑：主机 A（IP 地址 A）在应用层运行进程 P1，其传输层有一个套接字；主机 C（IP 地址 C）在应用层运行进程 P2 与 P3，其传输层有两个套接字；服务器主机 B（IP 地址 B）在应用层运行进程 P4、P5、P6，其传输层有三个套接字。

图中标出的三段指向服务器的报文段为：

| 源 IP,端口 | 目的 IP,端口 | 对应的服务器端套接字 |
|---|---|---|
| A, 9157 | B, 80 | P4 的套接字 |
| C, 5775 | B, 80 | P5 的套接字 |
| C, 9157 | B, 80 | P6 的套接字 |

图中的反方向报文段为：

| 源 IP,端口 | 目的 IP,端口 |
|---|---|
| B, 80 | A, 9157 |
| B, 80 | C, 5775 |

课件给出的结论是：**三段报文段都指向 IP 地址 B、目的端口 80，却被分解到不同的套接字**。原因正是 6.2.6 中的规则——TCP 分解使用四元组。三段报文段的目的 IP 与目的端口相同，但源 IP 地址与源端口号不同（A,9157 / C,5775 / C,9157 三者两两不同），因此四元组不同，被交给三个不同的套接字，分别由进程 P4、P5、P6 处理。

同一拓扑的另一版本把服务器端改为**多线程服务器**（threaded server）：应用层只有一个进程 P4，但该进程内有多个线程，三段报文段被分解到同一进程 P4 下的三个不同套接字。这说明"每个连接一个套接字"与"每个连接一个进程"是两回事：多路分解是按套接字进行的，一个进程（或线程组）可以持有多个套接字。

## 6.3 无连接传输：UDP（Connectionless Transport: UDP）

### 6.3.1 UDP 概述

UDP（User Datagram Protocol，用户数据报协议）由 RFC 768 定义，是 Internet 的传输层协议之一。课件用"no frills"（无附加功能）、"bare bones"（最简骨架）来描述它，含义是：UDP 在 IP 之上几乎不增加额外机制。

UDP 提供"尽力而为"（best effort）服务，具体后果是 UDP 报文段可能：

- 丢失（lost）；
- 以乱序交付给应用（delivered out-of-order to app）。

UDP 是**无连接**（connectionless）的，表现为：

- UDP 的发送方与接收方之间没有握手（no handshaking）；
- 每个 UDP 报文段独立于其他报文段被处理（each UDP segment handled independently of others），即报文段之间不保留先后关系或状态。

### 6.3.2 UDP 报文段格式

UDP 报文段首部共 4 个字段，每个字段 16 位，首部总长 8 字节：

| 字段 | 长度 | 含义 |
|---|---|---|
| source port #（源端口号） | 16 位 | 发送进程的端口号 |
| dest port #（目的端口号） | 16 位 | 接收进程的端口号 |
| length（长度） | 16 位 | UDP 报文段的总长度，单位为字节，**含首部** |
| checksum（校验和） | 16 位 | 用于检测传输中出现的比特差错 |
| application data (payload) | 变长 | 应用数据（载荷） |

字段 `length` 的含义需注意：它是"UDP 报文段、含首部在内"的字节数，因此该字段的最小合法值为 8（仅有首部、无载荷）。首部第一行由源端口号与目的端口号各占 16 位组成，共 32 位（图中标注 "32 bits"），第二行由 length 与 checksum 各占 16 位组成，共 32 位。

### 6.3.3 为什么需要 UDP 与 UDP 的典型用途

课件用"为什么会有 UDP"这一问题引出其存在理由。相比 TCP，UDP 具备以下特点：

- **不需要连接建立**（no connection establishment），而连接的建立过程会引入额外时延；
- **简单**：发送方和接收方都不需要维护连接状态（no connection state at sender, receiver），而 TCP 需要为每条连接维护状态；
- **首部开销小**（small header size）：UDP 首部固定 8 字节，TCP 首部固定部分为 20 字节；
- **没有拥塞控制**（no congestion control）：UDP 可以按应用希望的速度发送，不受拥塞控制的速率限制。

UDP 的典型用途：

- **流式多媒体应用**（streaming multimedia apps）：这类应用容忍丢失（loss tolerant）但对速率敏感（rate sensitive），不希望因重传与速率调节而引入时延和速率波动；
- **DNS**；
- **SNMP**。

课件还指出，若要在 UDP 之上获得可靠传输，需要**在应用层自行添加可靠性机制**，实现与应用相关的差错恢复（application-specific error recovery）。也就是说，可靠性不是由 UDP 提供，而是由应用自己负责。

### 6.3.4 UDP 校验和（UDP Checksum）

校验和的目标是检测传输报文段中的"差错"（errors），例如比特翻转（flipped bits）。

**发送方**的操作：

1. 把报文段的内容（**包括首部字段**）看作一串 16 位整数（sequence of 16-bit integers）；
2. 计算这些 16 位整数之和；
3. 对该和取**反码**（One's (1s) complement），即按位取反，得到校验和；
4. 把校验和值写入 UDP 首部的 checksum 字段。

**接收方**的操作：

1. 对收到的报文段计算校验和；
2. 将计算所得的校验和与报文段中 checksum 字段的值比较：
   - 若**不相等**——检测到差错；
   - 若**相等**——未检测到差错。但课件特别注明："But maybe errors nonetheless? More later …."，即校验和相等并不意味着一定没有差错，仍可能存在未被检测出的差错。这一点是反码求和的固有局限：某些多位同时发生的差错会使和保持不变，从而无法被检测。

### 6.3.5 Internet 校验和计算示例（课件 6-19）

对两个 16 位整数求校验和的完整示例如下。

**输入数据**：两个 16 位整数

$$x = 1110011001100110_2,\qquad y = 1101010101010101_2$$

写成十六进制：$x = \text{0xE666}$，$y = \text{0xD555}$。

**第 1 步：按位相加（不带回卷）**

$$\begin{aligned}
&\ \ 1110011001100110\\
+&\ \ 1101010101010101\\
\hline
1&\ \ 1011101110111011
\end{aligned}$$

即二进制和为 $1\,1011101110111011_2$，对应十六进制 $0\text{x1BBBB}$。最高位产生了进位（carryout），图中用打圈的 ① 标出。

**第 2 步：回卷（wraparound）**

相加时，若最高位产生进位，必须把该进位加到结果中去（Note: when adding numbers, a carryout from the most significant bit needs to be added to the result）。因此把第 16 位之外的进位 1 加到低 16 位上：

$$\text{0x1BBBB} \Rightarrow \text{0xBBBB} + 1 = \text{0xBBBC}$$

十六进制 0xBBBC 的二进制为 $1011101110111100_2$，与图中标注的 sum 行 $1011101110111100$ 一致。

**第 3 步：取反得到校验和**

对 sum 逐位取反：

$$\text{checksum} = \overline{1011101110111100} = 0100010001000011_2 = \text{0x4443}$$

与图中 checksum 行 $0100010001000011$ 一致。

**第 4 步：用原始数据校验**

把 sum 与 checksum 相加：

$$\begin{aligned}
&\ \ 1011101110111100\\
+&\ \ 0100010001000011\\
\hline
&\ \ 1111111111111111
\end{aligned}$$

结果为 $\text{0xFFFF}$，即全 1。这说明：在接收端，把包括 checksum 字段在内的全部 16 位字求和得到全 1（等价于校验和为 0），即认为未检测到差错。校验成立，说明计算无误。

课件还指出，更多同类练习可在交互式练习页面 `http://gaia.cs.umass.edu/kurose_ross/interactive/` 上练习。

### 6.3.6 例题：1 的补码求和（Exercise，课件 6-20）

**题干**（三小问，原文照录）：

a. Suppose you have the following 2 bytes: 01011100 and 01100101. What is the 1s complement of the sum of these 2 bytes?

b. Suppose you have the following 2 bytes: 11011010 and 01100101. What is the 1s complement of the sum of these 2 bytes?

c. For the bytes in part (a), give an example where one bit is flipped in each of the 2 bytes and yet the 1s complement doesn't change.

**解答 a**

已知两个字节：$a_1 = 01011100_2$，$a_2 = 01100101_2$。

第 1 步：写成十六进制便于核对。$01011100_2 = \text{0x5C}$，$01100101_2 = \text{0x65}$。

第 2 步：按位相加。

$$\begin{aligned}
&\ \ 01011100\\
+&\ \ 01100101\\
\hline
&\ \ 11000001
\end{aligned}$$

逐位核对（从最低位到最高位）：

- 第 0 位：$0+1=1$，本位 1，进位 0；
- 第 1 位：$0+0=0$，本位 0，进位 0；
- 第 2 位：$1+1=0$，本位 0，进位 1；
- 第 3 位：$1+0+1=0$，本位 0，进位 1；
- 第 4 位：$1+0+1=0$，本位 0，进位 1；
- 第 5 位：$1+1+1=1$，本位 1，进位 1；
- 第 6 位：$0+1+1=0$，本位 0，进位 1；
- 第 7 位：$0+0+1=1$，本位 1，进位 0（最高位无进位产生）。

和为 $11000001_2 = \text{0xC1}$，最高位没有进位，无需回卷。

第 3 步：取反码。

$$\overline{11000001} = 00111110_2 = \text{0x3E}$$

**答案 a**：两字节之和为 $11000001_2$，其 1 的补码为 $00111110_2$（0x3E）。

**解答 b**

已知两个字节：$b_1 = 11011010_2$，$b_2 = 01100101_2$。

第 1 步：写成十六进制。$11011010_2 = \text{0xDA}$，$01100101_2 = \text{0x65}$。

第 2 步：按位相加。

$$\begin{aligned}
&\ \ 11011010\\
+&\ \ 01100101\\
\hline
1&\ \ 00111111
\end{aligned}$$

逐位核对：

- 第 0 位：$0+1=1$，本位 1，进位 0；
- 第 1 位：$1+0=1$，本位 1，进位 0；
- 第 2 位：$0+1=1$，本位 1，进位 0；
- 第 3 位：$1+0=1$，本位 1，进位 0；
- 第 4 位：$1+0=1$，本位 1，进位 0；
- 第 5 位：$0+1=1$，本位 1，进位 0；
- 第 6 位：$1+1=0$，本位 0，进位 1；
- 第 7 位：$1+0+1=0$，本位 0，进位 1（产生最高位进位）。

和连同进位为 $1\,00111111_2 = \text{0x13F}$。

第 3 步：回卷。把最高位进位 1 加到低 8 位上：

$$\text{0x13F} \Rightarrow \text{0x3F} + 1 = \text{0x40} = 01000000_2$$

第 4 步：取反码。

$$\overline{01000000} = 10111111_2 = \text{0xBF}$$

**答案 b**：两字节之和回卷后为 $01000000_2$（0x40），其 1 的补码为 $10111111_2$（0xBF）。

**解答 c**

要求：对 a 中的两个字节各翻转 1 个比特，而 1 的补码不变。

a 中两字节为 $01011100$ 与 $01100101$，和为 $11000001$，补码为 $00111110$。

翻转方案：把两个字节的**最低位**（第 0 位）互换取值：

- $01011100$ 的第 0 位由 0 改为 1，得到 $01011101$；
- $01100101$ 的第 0 位由 1 改为 0，得到 $01100100$。

第 1 步：验证和为不变。

$$\begin{aligned}
&\ \ 01011101\\
+&\ \ 01100100\\
\hline
&\ \ 11000001
\end{aligned}$$

逐位核对：

- 第 0 位：$1+0=1$，本位 1，进位 0；
- 第 1 位：$0+0=0$，本位 0，进位 0；
- 第 2 位：$1+1=0$，本位 0，进位 1；
- 第 3 位：$1+0+1=0$，本位 0，进位 1；
- 第 4 位：$1+0+1=0$，本位 0，进位 1；
- 第 5 位：$1+1+1=1$，本位 1，进位 1；
- 第 6 位：$0+1+1=0$，本位 0，进位 1；
- 第 7 位：$0+0+1=1$，本位 1，进位 0。

和为 $11000001_2$，与 a 中原两字节之和完全相同。

第 2 步：取反码。

$$\overline{11000001} = 00111110_2$$

补码仍为 $00111110_2$，未发生变化。

第 3 步：用原始数据校验并说明原因。两个字节各翻转 1 个比特后，总和不变的原因是：翻转发生在两个数的**同一权重位**（均为第 0 位，权重 $2^0$），其中一个数在该位由 0 变 1（对该位和的贡献增加 $2^0$），另一个数在该位由 1 变 0（贡献减少 $2^0$），两个变化量在同一权重位上数值相等、符号相反，互相抵消，因此整个和不变，1 的补码也不变。

**答案 c**：把 a 中两字节的最低比特互换，得到 $01011101$ 与 $01100100$；两数之和仍为 $11000001$，1 的补码仍为 $00111110$。两个比特翻转之所以不改变校验和，是因为一个在该权重位上增加 $2^0$、另一个在同一权重位上减少 $2^0$，两者恰好抵消，和保持不变。

本例题的结论与 6.3.4 中接收方的"YES - no error detected. But maybe errors nonetheless?"相呼应：校验和相等不能保证报文段无差错，c 问给出的正是一个具体的漏检实例。

## 6.4 可靠数据传输原理（Principles of Reliable Data Transfer）

可靠数据传输在**应用层（application layer）、传输层（transport layer）、链路层（link layer）**中都重要，课件把它列为"重要网络主题 top-10 列表"中的一项。本节的核心驱动变量是：**不可靠信道的特性决定可靠数据传输协议（reliable data transfer protocol，缩写 rdt）的复杂度**。课件把"不可靠信道可能发生什么"（比特差错、丢包、丢包的种类与位置）作为贯穿全节的变量：每增加一种信道不可靠性，协议就相应增加机制。

### 6.4.1 可靠数据传输的分层位置与接口模型

#### 6.4.1.1 服务视图与实现视图

课件用两张图给出同一个问题的两个视角。

**（a）provided service（所提供的服务）**。图中纵向标出 application layer 与 transport layer 两层边界。上层是两个进程：sending process（发送进程）与 receiver process（接收进程）；两者之间用标有 data 的箭头穿过下方的"可靠信道（reliable channel）"框相连。这一视图只说明对外效果：上层把数据交给传输层，数据经"可靠信道"后原样出现在对端上层，上层的每一个数据项都被正确、按序交付一次。

**（b）service implementation（服务的实现）**。传输层内部不是一条"可靠信道"，而是分别位于两端的两个协议实体与一条真实信道：

- 发送侧实体标注为 reliable data transfer protocol (sending side)，接收侧实体标注为 reliable data transfer protocol (receiving side)；
- 两个实体之间是**不可靠信道（unreliable channel）**，且该信道双向：图中有 packet 箭头自发送侧指向接收侧，同时有反向箭头自接收侧折回发送侧。

因此实现视图的结论是：可靠传输不是由信道本身提供的能力，而是由两端传输层实体在同一条不可靠信道上共同运行一个协议（rdt 协议）来实现的功能。

#### 6.4.1.2 四个接口函数

协议实体两侧共有四个接口函数，课件的说明如下：

| 接口函数 | 调用方向与调用者 | 课件原文说明 | 作用 |
|---|---|---|---|
| `rdt_send()` | 由上层（如应用程序）调用，进入发送侧传输层实体 | called from above, (e.g., by app.). Passed data to deliver to receiver upper layer | 上层把要交付给对端上层的数据交给发送方协议实体 |
| `udt_send()` | 由发送侧 rdt 调用，向下进入信道 | called by rdt, to transfer packet over unreliable channel to receiver | rdt 把打包好的 packet 交给不可靠信道发送 |
| `rdt_rcv()` | 由接收侧信道到达事件触发，向上进入接收侧 rdt | called when packet arrives on rcv-side of channel | 接收侧 rdt 得知有一个 packet 到达 |
| `deliver_data()` | 由接收侧 rdt 调用，向上交给上层 | called by rdt to deliver data to upper | 接收侧 rdt 把解包出的数据交给本端上层 |

图中数据流的方向是：上层 data → `rdt_send()` → 发送侧实体 → `udt_send()` → packet → 不可靠信道（双向箭头）→ packet → `rdt_rcv()` → 接收侧实体 → `deliver_data()` → data → 上层。图中 packet 的标注带有方框，表示它是协议实体之间传送的单位；data 的标注位于协议实体之外的上层侧。

#### 6.4.1.3 建模时采用的两条约定

本节后续内容按两条约定组织：

1. **逐步（incrementally）构造**可靠数据传输协议（reliable data transfer protocol，简称 rdt）的发送方与接收方。逐步是指：先假设信道完全可靠（rdt1.0），再逐步加入比特差错（rdt2.0）、ACK/NAK 受损（rdt2.1、rdt2.2）、丢包（rdt3.0）等条件。
2. **只考虑单向数据传输（unidirectional data transfer）**，即数据只从发送方流向接收方。即便在此前提下，**控制信息仍会沿两个方向流动**（but control info will flow on both directions），因为接收方需要向发送方回送确认或否认确认。

### 6.4.2 有限状态机（FSM）描述方法

课件约定用**有限状态机（finite state machine，FSM）**来描述发送方与接收方。FSM 图例的构成要素为：

- **状态（state）**：以圆圈表示，图中标注为 state 1、state 2。课件对状态的说明是：处于某"状态"时，**下一个状态由下一个事件唯一确定**（when in this "state" next state uniquely determined by next event）。
- **事件（event）**：触发状态转移的输入，在转移线上方以横线之上的一行标注，图例中标注为 event causing state transition。
- **动作（actions）**：状态转移时执行的操作，在事件行之下以横线之下的一行标注，图例中标注为 actions taken on state transition。
- 转移箭头由当前状态指向下一状态；起始状态用一条无源端的虚线箭头指出。
- 课件在 FSM 图中用大写希腊字母 $\Lambda$（lambda）表示**空动作**，即该转移不执行任何动作。
- 状态自身返回自身的转移画成自环（self-loop）。

本节各 FSM 图中出现的函数（含各课件自造的检查函数）含义约定如下，后文各协议的表均使用这些记号：

| 记号 | 含义 |
|---|---|
| `rdt_send(data)` | 上层向本端 rdt 交付数据的事件 |
| `rdt_rcv(rcvpkt)` | 本端收到一个 packet 的事件，收到的包记为 rcvpkt |
| `make_pkt(...)` | 按参数构造一个 packet，返回该 packet |
| `sndpkt` | 发送方保有的、最近一次发送的 packet |
| `extract(rcvpkt, data)` | 从收到的 packet 中取出数据字段，结果记为 data |
| `deliver_data(data)` | 把数据交付本端上层 |
| `udt_send(pkt)` | 把 packet 交给不可靠信道发送 |
| `corrupt(rcvpkt)` / `notcorrupt(rcvpkt)` | 按校验和判定收到的包是否在传输中出了比特差错 |
| `isACK(rcvpkt)` / `isNAK(rcvpkt)` | 判定收到的包是确认还是否认确认 |
| `has_seq0(rcvpkt)` / `has_seq1(rcvpkt)` | 判定收到的包携带的序号是 0 还是 1 |
| `make_pkt(ACK, chksum)` / `make_pkt(NAK, chksum)` | 构造只有确认/否认确认与校验和、不含数据的控制包 |
| `isACK(rcvpkt,0)` / `isACK(rcvpkt,1)` | 判定收到的包是"确认序号 0 的包"还是"确认序号 1 的包" |
| `start_timer` / `stop_timer` / `timeout` | 启动倒计时定时器、停止定时器、定时器到期事件 |

### 6.4.3 rdt1.0：完全可靠信道上的可靠传输

**信道假设**：底层信道完全可靠（underlying channel perfectly reliable），具体包含两条：

- 不产生比特差错（no bit errors）；
- 不丢失 packet（no loss of packets）。

在此假设下，发送方与接收方各用一个独立的 FSM 描述：发送方把数据送入底层信道，接收方从底层信道读出数据。

**发送方 FSM**（只有一个状态）：

| 当前状态 | 事件 | 动作 | 下一状态 |
|---|---|---|---|
| Wait for call from above | `rdt_send(data)` | `packet = make_pkt(data)`；`udt_send(packet)` | Wait for call from above（自环） |

`make_pkt(data)` 只带一个参数，因为信道不会出错，既不需要校验和，也不需要序号；接收方也无需任何反馈，所以发送方发完即回到同一状态等待下一次上层调用，不存在第二个状态。

**接收方 FSM**（也只有一个状态）：

| 当前状态 | 事件 | 动作 | 下一状态 |
|---|---|---|---|
| Wait for call from below | `rdt_rcv(packet)` | `extract(packet, data)`；`deliver_data(data)` | Wait for call from below（自环） |

`extract(packet, data)` 取出数据后立即交付上层，交付后回到同一状态等待下一个包。

rdt1.0 是全节的**基线模型**：它把"可靠"当成信道已有性质，因此协议本身不包含任何检错、反馈、重传或定时机制。后续 rdt2.0 至 rdt3.0 的所有机制都是为弥补 rdt1.0 假设被破坏后出现的缺口而加入的。

### 6.4.4 rdt2.0：存在比特差错的信道

#### 6.4.4.1 新的信道假设与新增机制

新的假设是：**底层信道可能在 packet 中翻转比特（underlying channel may flip bits in packet）**。应对办法是用**校验和（checksum）检测比特差错**。

课件先以一个问题引入：在日常对话中，人如何从"差错"中恢复（How do humans recover from "errors" during conversation?）。课件随后给出的技术答案是：由接收方向发送方**显式反馈**接收结果；收到这种反馈后，发送方决定是继续发送新数据还是重发当前 packet。从差错中恢复（how to recover from errors）的三个要点为：

- **确认（acknowledgments，ACKs）**：接收方显式告诉发送方该 packet 已正确收到（receiver explicitly tells sender that pkt received OK）；
- **否认确认（negative acknowledgments，NAKs）**：接收方显式告诉发送方该 packet 有差错（receiver explicitly tells sender that pkt had errors）；
- **发送方收到 NAK 后重传该 packet**（sender retransmits pkt on receipt of NAK）。

rdt2.0 相对 rdt1.0 **新增的三种机制**是：

1. **差错检测（error detection）**；
2. **接收方反馈（receiver feedback）**：控制报文（control msgs）ACK、NAK 自接收方流向发送方（receiver → sender）；
3. **重传（retransmission）**。

#### 6.4.4.2 停等（stop and wait）工作方式

rdt2.0 的工作方式是**停等**：**发送方发一个 packet，然后等待接收方的响应**（sender sends one packet, then waits for receiver response）。因此 rdt2.0 的发送方在任意时刻最多只有一个未被确认的 packet 在信道中，收到 ACK 或 NAK 之前不会发送下一个数据包。这一方式直接决定了后面的序号空间大小。

#### 6.4.4.3 rdt2.0 发送方 FSM

rdt2.0 发送方有两个状态。

| 当前状态 | 事件 | 动作 | 下一状态 |
|---|---|---|---|
| Wait for call from above | `rdt_send(data)` | `sndpkt = make_pkt(data, checksum)`；`udt_send(sndpkt)` | Wait for ACK or NAK |
| Wait for ACK or NAK | `rdt_rcv(rcvpkt) && isNAK(rcvpkt)` | `udt_send(sndpkt)` | Wait for ACK or NAK（自环） |
| Wait for ACK or NAK | `rdt_rcv(rcvpkt) && isACK(rcvpkt)` | $\Lambda$（空动作） | Wait for call from above |

`make_pkt(data, checksum)` 相比 rdt1.0 的 `make_pkt(data)` 多了一个 checksum 参数，用于让接收方检错。状态 Wait for ACK or NAK 上的重传动作用 `udt_send(sndpkt)` 表示**重发上一次发送的同一个 packet**，而不是重新构造；这也是发送方必须把最近发送的 packet 保存在 `sndpkt` 中的原因。收到 ACK 的转移动作为 $\Lambda$，因为发送方没有额外动作，只需回到等待上层调用的状态。（课件图中此处变量拼写为 `snkpkt`，与 `sndpkt` 指同一变量。）

#### 6.4.4.4 rdt2.0 接收方 FSM

rdt2.0 接收方只有一个状态。

| 当前状态 | 事件 | 动作 | 下一状态 |
|---|---|---|---|
| Wait for call from below | `rdt_rcv(rcvpkt) && corrupt(rcvpkt)` | `udt_send(NAK)` | Wait for call from below（自环） |
| Wait for call from below | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt)` | `extract(rcvpkt, data)`；`deliver_data(data)`；`udt_send(ACK)` | Wait for call from below（自环） |

接收方不保存数据包也不保存序号，只按当前到达的这一个包是否正确来回复 ACK 或 NAK。图中两个自环分别对应两个互斥的到达事件。

#### 6.4.4.5 rdt2.0 无差错运行过程

无差错情形下在两张 FSM 上走的一条完整路径为：

1. 发送方处于 Wait for call from above；上层调用 `rdt_send(data)`，动作为 `make_pkt(data, checksum)`、`udt_send(sndpkt)`，转移进入 Wait for ACK or NAK。
2. 该 packet 经信道到达接收方，未发生比特翻转。接收方处于 Wait for call from below，发生事件 `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt)`，动作为 `extract(rcvpkt,data)`、`deliver_data(data)`、`udt_send(ACK)`，接收方仍处 Wait for call from below（自环）。
3. ACK 经信道回到发送方。发送方在 Wait for ACK or NAK 上发生事件 `rdt_rcv(rcvpkt) && isACK(rcvpkt)`，动作为 $\Lambda$，转移回 Wait for call from above，一个数据项的传输完成。

无差错时该路径只涉及发送方两个状态之间的一次往返和接收方一次自环。

#### 6.4.4.6 rdt2.0 差错运行过程

数据包受损情形下的一条完整路径为：

1. 发送方在 Wait for call from above 收到 `rdt_send(data)`，动作 `make_pkt(data, checksum)`、`udt_send(sndpkt)`，进入 Wait for ACK or NAK。
2. 该 packet 在信道中被翻转了比特。接收方在 Wait for call from below 发生事件 `rdt_rcv(rcvpkt) && corrupt(rcvpkt)`，动作为 `udt_send(NAK)`，接收方留在 Wait for call from below。
3. NAK 经信道回到发送方。发送方在 Wait for ACK or NAK 上发生事件 `rdt_rcv(rcvpkt) && isNAK(rcvpkt)`，动作为 `udt_send(sndpkt)`，即重传 `sndpkt`，发送方留在 Wait for ACK or NAK。
4. 重传的 packet 到达接收方且未发生比特翻转。接收方发生事件 `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt)`，动作为 `extract(rcvpkt,data)`、`deliver_data(data)`、`udt_send(ACK)`。
5. ACK 回到发送方。发送方发生事件 `rdt_rcv(rcvpkt) && isACK(rcvpkt)`，动作 $\Lambda$，回到 Wait for call from above。

比特差错靠"接收方报错 + 发送方重传"修复；该过程可能重复多次，直到某一次重传的 packet 正确到达。

#### 6.4.4.7 rdt2.0 的致命缺陷

问题是：**what happens if ACK/NAK corrupted?**

- 如果 ACK 或 NAK 在反向传输中受损，**发送方不知道接收方那里发生了什么**（sender doesn't know what happened at receiver）；
- 此时**不能简单地直接重传**，因为可能产生**重复包（possible duplicate）**：若受损的是 NAK，发送方重传是对的；若受损的是 ACK，则接收方已经交付过一次数据，重传会使接收方再交付一次同样的数据，上层就会收到重复数据。

处理重复包（handling duplicates）的三条办法是：

- 发送方在 ACK/NAK 受损时**重传当前 packet**（sender retransmits current pkt if ACK/NAK corrupted）；
- 发送方**给每个 packet 加上序号**（sender adds sequence number to each pkt）；
- 接收方**丢弃（不向上交付）重复的 packet**（receiver discards (doesn't deliver up) duplicate pkt）。

rdt2.0 的缺陷在于缺少序号，无法区分"新到达的数据包"与"重传造成的数据包副本"。修复办法是引入序号，rdt2.1 就是加入序号并同时处理 ACK/NAK 受损的协议。

### 6.4.5 rdt2.1：发送方与接收方处理受损的 ACK/NAK

#### 6.4.5.1 发送方 FSM

rdt2.1 发送方由 rdt2.0 的两个状态扩展为**四个状态**：按"等待上层交付序号 0 或 1 的数据"与"等待序号 0 或 1 的确认"分成四种。每个数据包的序号写入 `make_pkt` 的第一个参数。

| 当前状态 | 事件 | 动作 | 下一状态 |
|---|---|---|---|
| Wait for call 0 from above | `rdt_send(data)` | `sndpkt = make_pkt(0, data, checksum)`；`udt_send(sndpkt)` | Wait for ACK or NAK 0 |
| Wait for ACK or NAK 0 | `rdt_rcv(rcvpkt) && ( corrupt(rcvpkt) \|\| isNAK(rcvpkt) )` | `udt_send(sndpkt)` | Wait for ACK or NAK 0（自环） |
| Wait for ACK or NAK 0 | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && isACK(rcvpkt)` | $\Lambda$ | Wait for call 1 from above |
| Wait for call 1 from above | `rdt_send(data)` | `sndpkt = make_pkt(1, data, checksum)`；`udt_send(sndpkt)` | Wait for ACK or NAK 1 |
| Wait for ACK or NAK 1 | `rdt_rcv(rcvpkt) && ( corrupt(rcvpkt) \|\| isNAK(rcvpkt) )` | `udt_send(sndpkt)` | Wait for ACK or NAK 1（自环） |
| Wait for ACK or NAK 1 | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && isACK(rcvpkt)` | $\Lambda$ | Wait for call 0 from above |

两点需注意：

- 收到**受损的 ACK/NAK** 与收到 **NAK** 被合并成同一个事件 `corrupt(rcvpkt) || isNAK(rcvpkt)`，动作都是重传 `sndpkt` 并留在原状态。这正是对 rdt2.0 缺陷的处理：确认信息受损时按"没收到正确确认"处理，重传当前包。
- 课件图中此处未使用 `isACK(rcvpkt,0)` 这类带序号的判定，只用 `notcorrupt(rcvpkt) && isACK(rcvpkt)`。成立的原因是发送方处于 Wait for ACK or NAK 0 时信道中只可能存在序号 0 数据包的确认（停等方式），因此不需要再校验确认针对的是哪个序号。

#### 6.4.5.2 接收方 FSM

rdt2.1 接收方有两个状态，分别对应"期待收到序号 0 的数据包"与"期待收到序号 1 的数据包"。**接收方不发送带序号的 ACK，其 ACK 与 NAK 只带校验和（chksum）**；接收方通过自己当前所处状态隐含表达它在确认哪一个序号。

| 当前状态 | 事件 | 动作 | 下一状态 |
|---|---|---|---|
| Wait for 0 from below | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && has_seq0(rcvpkt)` | `extract(rcvpkt, data)`；`deliver_data(data)`；`sndpkt = make_pkt(ACK, chksum)`；`udt_send(sndpkt)` | Wait for 1 from below |
| Wait for 0 from below | `rdt_rcv(rcvpkt) && (corrupt(rcvpkt))` | `sndpkt = make_pkt(NAK, chksum)`；`udt_send(sndpkt)` | Wait for 0 from below（自环） |
| Wait for 0 from below | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && has_seq1(rcvpkt)` | `sndpkt = make_pkt(ACK, chksum)`；`udt_send(sndpkt)` | Wait for 0 from below（自环） |
| Wait for 1 from below | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && has_seq1(rcvpkt)` | `extract(rcvpkt, data)`；`deliver_data(data)`；`sndpkt = make_pkt(ACK, chksum)`；`udt_send(sndpkt)` | Wait for 0 from below |
| Wait for 1 from below | `rdt_rcv(rcvpkt) && (corrupt(rcvpkt))` | `sndpkt = make_pkt(NAK, chksum)`；`udt_send(sndpkt)` | Wait for 1 from below（自环） |
| Wait for 1 from below | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && has_seq0(rcvpkt)` | `sndpkt = make_pkt(ACK, chksum)`；`udt_send(sndpkt)` | Wait for 1 from below（自环） |

（课件图中两条带 `has_seq0`／`has_seq1` 的横线跨越两个状态绘制，其连线归属按"接收方只在正确收到期待序号的数据包时才交付并改换期待序号"这一语义确定，上表即按此语义填充。）行为规则可概括为：

- 正确收到**期待序号的包**：交付数据、回 ACK、把期待序号换成另一个；
- 正确收到**非期待序号的包**（即上一个包的重复副本）：不交付，直接回 ACK（该 ACK 只是再次确认已经正确收到的那个包），状态不变，因此重复包不会造成重复交付；
- 收到**受损的包**：回 NAK，状态不变。

#### 6.4.5.3 rdt2.1 的讨论

**发送方（sender）**：

- **必须检查收到的 ACK/NAK 是否受损**（must check if received ACK/NAK corrupted）；
- packet 中已加入序号（seq # added to pkt）；
- **两个序号（0、1）就够用**（two seq. #'s (0,1) will suffice）。原因：rdt2.1 采用停等方式，发送方在收到当前 packet 的确认之前不会发送下一个数据包，因此接收方在任一时刻只需要区分两件事——到达的包是"它正在等的那一个"还是"上一个包的副本"，两种情况用 1 个比特即可区分，故序号空间为 2 足够；
- **状态数是原来的两倍**（twice as many states）：状态必须"记住"所期待的 packet 应具有的序号是 0 还是 1（state must "remember" whether "expected" pkt should have seq # of 0 or 1）。

**接收方（receiver）**：

- **必须检查收到的 packet 是否是重复包**（must check if received packet is duplicate）：状态本身指示当前期待的 packet 序号是 0 还是 1（state indicates whether 0 or 1 is expected pkt seq #）；
- 注意：**接收方无法知道它上一次发出的 ACK/NAK 是否被发送方正确收到**（receiver can not know if its last ACK/NAK received OK at sender）。因此接收方不能依赖"我上次已经确认过"来判断发送方状态，只能按当前状态对每一个到达的包作出反应；这也是发送方需要自己处理受损确认（重传）的原因。

### 6.4.6 rdt2.2：不使用 NAK 的协议

#### 6.4.6.1 机制

rdt2.2 的要点是：

- 与 rdt2.1 **功能相同**，但**只使用 ACK**（same functionality as rdt2.1, using ACKs only）；
- **用"对最后一个正确收到的 packet 的 ACK"代替 NAK**（instead of NAK, receiver sends ACK for last pkt received OK）；
- 因此**接收方必须在 ACK 中显式包含被确认 packet 的序号**（receiver must explicitly include seq # of pkt being ACKed）；
- **发送方收到重复的 ACK 时，所执行的动作与收到 NAK 相同：重传当前 packet**（duplicate ACK at sender results in same action as NAK: retransmit current pkt）。

由此得到的判定规则是：发送方在等待序号 $n$ 的确认时，若收到的 ACK 是"确认序号 $1-n$"（即上一次已确认过的那个序号），等价于收到 NAK。

#### 6.4.6.2 发送方片段

课件此处给出的发送方 FSM 是**片段（fragment）**，即完整 FSM 的一部分。

| 当前状态 | 事件 | 动作 | 下一状态 |
|---|---|---|---|
| Wait for call 0 from above | `rdt_send(data)` | `sndpkt = make_pkt(0, data, checksum)`；`udt_send(sndpkt)` | Wait for ACK 0 |
| Wait for ACK 0 | `rdt_rcv(rcvpkt) && ( corrupt(rcvpkt) \|\| isACK(rcvpkt,1) )` | `udt_send(sndpkt)` | Wait for ACK 0（自环） |
| Wait for ACK 0 | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && isACK(rcvpkt,0)` | $\Lambda$ | 片段外的对应状态（Wait for call 1 from above） |

与 rdt2.1 发送方相比，唯一的差别是 NAK 分支被替换：rdt2.1 中是 `corrupt(rcvpkt) || isNAK(rcvpkt)`，rdt2.2 中是 `corrupt(rcvpkt) || isACK(rcvpkt,1)`，即**"收到确认另一个序号的 ACK"承担了 NAK 的角色**。上表最后一行在原图中以一条指向左下方的箭头画出、箭头未连回所显示的状态；按 rdt2.1 的相同结构，完整协议中正确收到 ACK 0 后应转入等待上层交付序号 1 数据的状态（Wait for call 1 from above）。该状态在原图中未画出，属按协议语义补全。

#### 6.4.6.3 接收方片段

接收方 FSM 同为片段，画出的状态是 Wait for 0 from below。

| 当前状态 | 事件 | 动作 | 下一状态 |
|---|---|---|---|
| Wait for 0 from below | `rdt_rcv(rcvpkt) && ( corrupt(rcvpkt) \|\| has_seq1(rcvpkt) )` | `udt_send(sndpkt)` | Wait for 0 from below（自环） |
| （Wait for 1 from below） | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && has_seq1(rcvpkt)` | `extract(rcvpkt, data)`；`deliver_data(data)`；`sndpkt = make_pkt(ACK1, chksum)`；`udt_send(sndpkt)` | Wait for 0 from below |

说明：

- 自环条件 `corrupt(rcvpkt) || has_seq1(rcvpkt)` 的含义是：**收到受损的包，或收到不是当前期待序号（此处期待 0）的正确包**，两者都只用 `udt_send(sndpkt)` 把上一次发出的 ACK（此处为 ACK1）再发一次，状态不变。rdt2.1 中"受损回 NAK"的动作在这里被"重发上一次的 ACK"取代，这就是"无 NAK"的实现方式。
- 表中第二行 `notcorrupt && has_seq1` 且交付数据、回 ACK1 的转移，其起点状态被片段边界截去；按"只在正确收到期待序号包时交付并更换期待序号"的语义，它属于未画出的 Wait for 1 from below 状态，转入 Wait for 0 from below，即该边来自"Wait for 1 from below 收到正确的序号 1 包：extract/deliver_data、make_pkt(ACK1, chksum)、udt_send，进入 Wait for 0 from below"。此处箭头方向表示的是"由 Wait for 1 进入 Wait for 0"，不应理解为 Wait for 0 收到序号 1 却交付数据。
- 与 rdt2.1 的一个差别是 ACK 的写法：rdt2.2 中写为 `make_pkt(ACK1, chksum)` / `isACK(rcvpkt,1)`，即**确认序号被写进 ACK 本身**，而 rdt2.1 中只需要 `make_pkt(ACK, chksum)`，序号由状态隐含。

### 6.4.7 rdt3.0：信道既可能出错又可能丢包

#### 6.4.7.1 新假设与方法

**新假设**：底层信道**还可能丢失 packet**，包括数据包与 ACK（underlying channel can also lose packets (data, ACKs)）。课件指出：

- 已有的**校验和、序号、ACK、重传**这些机制"会有帮助……但并不够"（checksum, seq. #, ACKs, retransmissions will be of help … but not enough）；
- 必须分别处理的两种情况是**数据丢失（Data lost?）** 与 **ACK 丢失（ACK lost?）**。

**方法**：**发送方为 ACK 等待"合理的"一段时间**（sender waits "reasonable" amount of time for ACK），具体为：

- 若在这段时间内没有收到 ACK，就重传（retransmits if no ACK received in this time）；
- 若 packet（或 ACK）只是**被延迟**而非丢失（if pkt (or ACK) just delayed (not lost)）：重传将造成**重复包**，但**序号已经能够处理这种情况**（retransmission will be duplicate, but seq. #'s already handles this）；并且**接收方必须指明它正在确认的 packet 的序号**（receiver must specify seq # of pkt being ACKed）；
- 这需要**倒计时定时器（countdown timer）**。

因此 rdt3.0 相对 rdt2.2 新增的机制只有两项：**倒计时定时器**及其超时事件。序号、校验和、带序号的 ACK 沿用 rdt2.2。

#### 6.4.7.2 rdt3.0 发送方 FSM

rdt3.0 发送方为四个状态，与 rdt2.2 的四个状态一一对应，差别是增加定时器的启动、停止与超时转移。

| 当前状态 | 事件 | 动作 | 下一状态 |
|---|---|---|---|
| Wait for call 0 from above | `rdt_send(data)` | `sndpkt = make_pkt(0, data, checksum)`；`udt_send(sndpkt)`；`start_timer` | Wait for ACK 0 |
| Wait for call 0 from above | `rdt_rcv(rcvpkt)` | $\Lambda$ | Wait for call 0 from above（自环） |
| Wait for ACK 0 | `rdt_rcv(rcvpkt) && ( corrupt(rcvpkt) \|\| isACK(rcvpkt,1) )` | $\Lambda$ | Wait for ACK 0（自环） |
| Wait for ACK 0 | `timeout` | `udt_send(sndpkt)`；`start_timer` | Wait for ACK 0（自环） |
| Wait for ACK 0 | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && isACK(rcvpkt,0)` | `stop_timer` | Wait for call 1 from above |
| Wait for call 1 from above | `rdt_send(data)` | `sndpkt = make_pkt(1, data, checksum)`；`udt_send(sndpkt)`；`start_timer` | Wait for ACK 1 |
| Wait for call 1 from above | `rdt_rcv(rcvpkt)` | $\Lambda$ | Wait for call 1 from above（自环） |
| Wait for ACK 1 | `rdt_rcv(rcvpkt) && ( corrupt(rcvpkt) \|\| isACK(rcvpkt,0) )` | $\Lambda$ | Wait for ACK 1（自环） |
| Wait for ACK 1 | `timeout` | `udt_send(sndpkt)`；`start_timer` | Wait for ACK 1（自环） |
| Wait for ACK 1 | `rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && isACK(rcvpkt,1)` | `stop_timer` | Wait for call 0 from above |

说明：

- **定时器只在发送数据包时启动**（`start_timer` 与 `udt_send(sndpkt)` 在同一动作序列内），因此定时器计时的是"当前这个未确认数据包的往返过程"。
- 收到**受损的包或确认了另一个序号的 ACK** 时动作为 $\Lambda$，**不停表也不重传**：它继续等待，交给定时器超时来处理。
- 超时后重传同一份 `sndpkt` 并**重启定时器**，状态不变，因此可反复超时重传，处理数据包丢失或 ACK 丢失两类情况。
- 正确收到期待序号的 ACK 时执行 `stop_timer` 并切换到另一个"等待上层调用"的状态。由于 ACK 带序号，被延迟到达的旧 ACK 不会被当作对新数据包的确认。

至此，6.4 节的协议演进形成如下机制叠加关系：rdt1.0（无机制）→ rdt2.0（校验和 + ACK/NAK + 重传，停等）→ rdt2.1（加入序号，处理受损的 ACK/NAK）→ rdt2.2（取消 NAK，改用带序号的 ACK）→ rdt3.0（加入倒计时定时器，处理丢包）。

### 6.4.8 rdt3.0 的运行场景

rdt3.0 发送方只有一个定时器，序号在 0 与 1 之间交替。其动作规则为：上层调用 `rdt_send(data)` 时，用当前序号和校验和封装分组并发送，同时启动定时器；收到序号匹配且未损坏的 ACK 时停止定时器，翻转序号并准备发送下一份数据；收到损坏的 ACK 或序号不匹配的 ACK 时不做任何动作；定时器超时时重传最近一个分组并重启定时器。接收方规则与 rdt2.2 相同：序号正确且未损坏则交付数据并回送对应序号的 ACK，序号不符（重复分组）则丢弃数据并重发该分组应得的 ACK。

以下四种事件序列按课件 rdt3.0 in action 图（发送方在左、接收方在右，斜线箭头为分组与 ACK 的传递方向）逐步还原。

#### (a) 无丢失（no loss）

| 步骤 | 发送方动作 | 接收方动作 |
|---|---|---|
| 1 | 发送 pkt0（seq=0），启动定时器 | — |
| 2 | — | 收到 pkt0：校验正确、序号等于期望值 0，交付数据，回送 ack0 |
| 3 | 收到 ack0：未损坏且序号匹配，停止定时器，序号翻转为 1 | — |
| 4 | 发送 pkt1（seq=1），启动定时器 | — |
| 5 | — | 收到 pkt1：校验正确、序号等于期望值 1，交付数据，回送 ack1 |
| 6 | 收到 ack1：停止定时器，序号翻转为 0，取新数据 | — |
| 7 | 发送 pkt0（seq=0，这是**新**数据） | — |
| 8 | — | 收到 pkt0：校验正确、序号等于期望值 0，交付数据，回送 ack0 |

要点在于：序号只有 0 和 1 两位，但发送方每收到一个正确 ACK 就翻转序号，所以同一个序号 0 会随后续的新数据再次出现；接收方依据"当前期望的序号"而不是"序号是否出现过"来判断新旧数据。图中 (a) 的最后一段正是"发送方再次发送 pkt0、接收方再次回送 ack0"，与第 1～2 步的图形相同，但承载的数据不同。

#### (b) 数据分组丢失（packet loss）

| 步骤 | 发送方动作 | 接收方动作 |
|---|---|---|
| 1 | 发送 pkt0，启动定时器 | — |
| 2 | — | 收到 pkt0，交付数据，回送 ack0 |
| 3 | 收到 ack0，停止定时器，序号翻转为 1 | — |
| 4 | 发送 pkt1，启动定时器；pkt1 在信道中丢失（图中在 pkt1 箭头上画叉并标注 loss） | — |
| 5 | 定时器超时（图中标注 timeout） | — |
| 6 | 重传 pkt1，重启定时器 | — |
| 7 | — | 收到重传的 pkt1：序号等于期望值 1，交付数据，回送 ack1 |
| 8 | 收到 ack1，停止定时器，序号翻转为 0 | — |
| 9 | 发送 pkt0 | — |
| 10 | — | 收到 pkt0，交付数据，回送 ack0 |

数据分组丢失后，接收方完全没有感知；发送方通过定时器超时发现异常并重传。由于原 pkt1 从未到达接收方，重传的 pkt1 对接收方而言就是首次接收，不触发重复检测。

#### (c) ACK 丢失（ACK loss）

| 步骤 | 发送方动作 | 接收方动作 |
|---|---|---|
| 1 | 发送 pkt0，启动定时器 | — |
| 2 | — | 收到 pkt0，交付数据，回送 ack0 |
| 3 | 收到 ack0，停止定时器，序号翻转为 1 | — |
| 4 | 发送 pkt1，启动定时器 | — |
| 5 | — | 收到 pkt1，交付数据，回送 ack1；ack1 在信道中丢失（图中在 ack1 箭头上画叉并标注 loss） |
| 6 | 定时器超时（图中标注 timeout） | — |
| 7 | 重传 pkt1，重启定时器 | — |
| 8 | — | 收到 pkt1：当前期望序号是 0，而分组序号为 1，判定为重复分组（图中标注 detect duplicate），丢弃其中的数据，重发 ack1 |
| 9 | 收到 ack1，停止定时器，序号翻转为 0 | — |
| 10 | 发送 pkt0 | — |
| 11 | — | 收到 pkt0，交付数据，回送 ack0 |

ACK 丢失并不导致数据丢失，只会把发送方的推进推迟一个超时周期；代价是接收方必须对重复分组**重新回送 ACK**，否则发送方会无限重传同一个分组。

#### (d) 过早超时／ACK 延迟（premature timeout / delayed ACK）

| 步骤 | 发送方动作 | 接收方动作 |
|---|---|---|
| 1 | 发送 pkt0，启动定时器 | — |
| 2 | — | 收到 pkt0，交付数据，回送 ack0 |
| 3 | 收到 ack0，停止定时器，序号翻转为 1 | — |
| 4 | 发送 pkt1，启动定时器 | — |
| 5 | 定时器超时（ACK 尚未到达，属于超时时间过短造成的提前超时） | 收到 pkt1，交付数据，回送 ack1（该 ack1 在信道中延迟，未丢失） |
| 6 | 重传 pkt1，重启定时器 | — |
| 7 | — | 收到 pkt1：期望序号为 0，判定为重复分组（图中标注 detect duplicate），丢弃数据，再次回送 ack1 |
| 8 | 收到延迟到达的 ack1：停止定时器，序号翻转为 0 | — |
| 9 | 发送 pkt0 | — |
| 10 | 收到第二次 ack1：序号与当前状态不匹配，执行"什么都不做"（图中标注 do nothing），即丢弃重复 ACK | — |
| 11 | — | 收到 pkt0，交付数据，回送 ack0 |
| 12 | 收到 ack0，停止定时器，序号翻转为 1 | — |

场景 (d) 说明两点：一是接收方依靠序号识别重复分组的能力，使"过早超时"不会破坏正确性；二是重复 ACK 到达发送方时会被丢弃，只会浪费一次传输，不影响数据交付。这四种场景合起来覆盖了底层信道的主要异常：数据分组损坏或丢失、ACK 分组损坏或丢失，以及超时估计偏差导致的重复传输。

### 6.4.9 rdt3.0 的性能与停等（stop-and-wait）工作方式

rdt3.0 在功能上是正确的，但课件给出的评价是"性能很差"（performance stinks）。原因是 rdt3.0 采用**停等**方式工作：发送方发出一个分组后必须等到该分组的 ACK 返回，才能发送下一个分组，因而在一个"传输时间 + 往返时间"的周期内只发送了一个分组的数据。

课件给出的算例参数为：

| 符号 | 含义 | 取值 |
|---|---|---|
| $L$ | 分组长度（比特数） | 8000 bit |
| $R$ | 链路速率 | 1 Gbps $=10^{9}$ bit/s |
| $d_{prop}$ | 单向传播时延 | 15 ms |
| RTT | 往返时延 | $2\times15\ \text{ms}=30\ \text{ms}$ |

第 1 步，计算一个分组的发送时延（transmission delay）：

$$D_{trans}=\frac{L}{R}=\frac{8000\ \text{bit}}{10^{9}\ \text{bit/s}}=8\times10^{-6}\ \text{s}=8\ \mu\text{s}$$

第 2 步，写出信道利用率（utilization）定义。$U_{sender}$ 表示"发送方处于发送状态的时间占全部时间的比例"：

$$U_{sender}=\frac{L/R}{RTT+L/R}$$

第 3 步，代入数值。为与课件写法一致，把 $L/R=8\ \mu\text{s}=0.008\ \text{ms}$、$RTT=30\ \text{ms}$、$RTT+L/R=30.008\ \text{ms}$ 代入：

$$U_{sender}=\frac{0.008}{30.008}=0.00027$$

即发送方只有约万分之 2.7 的时间在发送数据。

第 4 步，换算为吞吐量（throughput）。若 RTT 为 30 ms，则每 30 ms 才能发送 1 KB（1 KB $=8000$ bit）：

$$\text{吞吐量}=\frac{8000\ \text{bit}}{0.03\ \text{s}}=266{,}667\ \text{bit/s}\approx266.7\ \text{kbit/s}\approx33.3\ \text{kB/s}$$

课件写作"1KB pkt every 30 msec: 33kB/sec throughput over 1 Gbps link"，即在一条 1 Gbps 的链路上只得到约 33 kB/s 的有效吞吐。

停等操作的时间轴构成如下：发送方在 $t=0$ 发送第一个比特；在 $t=L/R$ 发送完最后一个比特（接收方在 $L/R+d_{prop}$ 处收完整个分组并回送 ACK）；ACK 在 $t=RTT+L/R$ 到达发送方，发送方随即发送下一个分组。图中标注的五行文字依次为：

- first packet bit transmitted, $t=0$（第一个分组比特发出）
- last packet bit transmitted, $t=L/R$（最后一个分组比特发出）
- first packet bit arrives（第一个分组比特到达接收方）
- last packet bit arrives, send ACK（最后一个分组比特到达，回送 ACK）
- ACK arrives, send next packet, $t=RTT+L/R$（ACK 到达，发送下一个分组）

图中的 RTT 标注在发送方"发出最后比特"到"收到 ACK"之间，数值上为 $2d_{prop}$。结论是：在停等方式下，瓶颈不是物理链路的带宽，而是协议本身（network protocol limits use of physical resources）。

### 6.4.10 流水线协议（Pipelined Protocols）

解决停等利用率低的方法是不等 ACK 到达就继续发送，即**流水线**（pipelining）：发送方允许同时存在多个"在途"（in-flight）尚未被确认的分组。流水线带来两个直接后果：

1. 序号范围必须增大（range of sequence numbers must be increased）。因为同一时刻可能有多个分组未被确认，只靠 0、1 两个序号无法区分它们。
2. 需要在发送方和／或接收方设置缓存（buffering at sender and/or receiver）。发送方可能需要缓存已发送未确认的分组以便重传，接收方可能需要缓存乱序到达的分组。

课件用两幅对比图说明这一点：(a) 是一台主机与一台服务器之间的停等协议运行情况，图中只有单个数据分组箭头和单个 ACK 箭头；(b) 是流水线协议运行情况，发送方向上并排出现多个数据分组箭头，返回方向上出现多个 ACK 箭头。两种通用的流水线协议形式是**回退 N 步**（go-Back-N, GBN）与**选择重传**（selective repeat, SR）。

按同一组参数计算流水线带来的利用率提升：若连续发送 3 个分组，则在 $RTT+L/R$ 的周期内发送的数据量为 $3L$：

$$U_{sender}=\frac{3L/R}{RTT+L/R}=\frac{3\times0.008\ \text{ms}}{30.008\ \text{ms}}=\frac{0.024}{30.008}=0.0008$$

课件写作 $0.0024/30.008=0.00081$：其分子在幻灯片上以毫秒为单位书写，$3L/R=24\ \mu s=0.024\ \text{ms}$，按"毫秒制"完整写应为 $0.024/30.008\approx0.0008$，与课件给出的 $0.00081$ 一致（课件分子 0.0024 的小数点位置与 0.024 ms 的量级不一致，此处按 $3L/R=0.024\ \text{ms}$ 复算）。课件结论为"3-packet pipelining increases utilization by a factor of 3"：3 分组的流水线把利用率提高 3 倍，对应吞吐量也提高约 3 倍（约 100 kB/s）。时间轴上的标注为：第一个分组比特在 $t=0$ 发出，最后比特在 $t=L/R$ 发出；接收方在收到第一个分组后回 ACK，随后收到第二个、第三个分组的最后比特并分别回 ACK；发送方在 $t=RTT+L/R$ 处收到 ACK 后继续发送后续分组。

两种流水线协议的对比：

| 对比项 | 回退 N 步（Go-back-N） | 选择重传（Selective Repeat） |
|---|---|---|
| 发送方在途未确认分组数 | 最多 $N$ 个 | 最多 $N$ 个 |
| 接收方确认方式 | 只发送**累积确认**（cumulative ACK），存在空档时不确认该分组之后的分组 | 对每个正确收到的分组**单独确认**（individual ACK） |
| 发送方定时器 | 只为最老的未确认分组维护一个定时器 | 为**每个**未确认分组分别维护定时器 |
| 超时后的重传 | 重传**所有**未确认分组 | 只重传**该**超时的未确认分组 |

补充：要使链路被完全占满，发送方窗口需要足以覆盖一个往返时间内能发出的分组数。按课件参数，$N\approx(RTT+L/R)/(L/R)=30.008/0.008\approx3751$，即需要约 3751 个分组的窗口才能让链路不间断地发送。该数值为按课件数据推算的补充内容，课件本身未给出。

### 6.4.11 回退 N 步（Go-Back-N，GBN）

#### 6.4.11.1 序号与发送窗口

GBN 在分组头中使用 $k$ 比特序号，序号空间为 $2^{k}$。发送方维护一个长度至多 $N$ 的窗口，窗口内是**连续的、已发送但尚未确认**的分组。

窗口示意图从左到右给出序号的四段划分，图中以 `send_base` 与 `nextseqnum` 两个指针标出窗口的左右边界，`send_base` 指向窗口最左端（最低未确认序号），`nextseqnum` 指向下一个待使用的序号；两个指针之间的跨度标为 window size $N$。图中颜色含义为：

| 图中颜色 | 含义 |
|---|---|
| 绿色（already ack'ed） | 已被确认的序号，位于窗口左侧之外 |
| 黄色（sent, not yet ack'ed） | 已发送、尚未确认，位于 $[send\_base,\ nextseqnum-1]$ |
| 蓝色（usable, not yet sent） | 窗口内尚未使用的序号，位于 $[nextseqnum,\ send\_base+N-1]$ |
| 白色（not usable） | 窗口之外、当前不可用的序号 |

GBN 的关键规则：

- **累积确认**：`ACK(n)` 表示"序号 $n$ 及其之前的所有分组都已正确收到"，因此一次 ACK 可能确认多个分组。
- 由于接收方在出现空档时会对同一序号重复回送 ACK，发送方**可能收到重复 ACK**（duplicate ACKs）。
- 发送方只为**最老的**在途分组维护一个定时器。
- 超时事件 `timeout(n)`：重传序号 $n$ **及其窗口内所有更高序号**的分组。

补充：GBN 要求窗口长度满足 $N\le 2^{k}-1$，否则在序号回绕时无法区分新分组与重传分组；课件未列出该约束，此处作为补充说明。

#### 6.4.11.2 GBN 发送方扩展有限状态机

初始状态：`base = 0`，`nextseqnum = 0`，状态为 `Wait`。

事件一：`rdt_send(data)`（上层交付数据）

```
if (nextseqnum < base+N) {
    sndpkt[nextseqnum] = make_pkt(nextseqnum, data, chksum)
    udt_send(sndpkt[nextseqnum])
    if (base == nextseqnum)
        start_timer
    nextseqnum++
}
else
    refuse_data(data)
```

即：若窗口未满，则封装并发送序号为 `nextseqnum` 的分组；若该分组是窗口中的第一个（`base == nextseqnum`），则启动定时器；随后 `nextseqnum` 自增。若窗口已满，则拒绝上层数据（`refuse_data(data)`）。

事件二：`timeout`（定时器超时）

```
start_timer
udt_send(sndpkt[base])
udt_send(sndpkt[base+1])
…
udt_send(sndpkt[nextseqnum-1])
```

即重启定时器，并把从 `base` 到 `nextseqnum-1` 的**全部分组**重新发送一遍。

事件三：`rdt_rcv(rcvpkt) && notcorrupt(rcvpkt)`（收到未损坏的 ACK）

```
base = getacknum(rcvpkt)+1
If (base == nextseqnum)
    stop_timer
else
    start_timer
```

即把窗口左边界推进到被确认序号的下一个序号（累积确认）；若推进后窗口内已无未确认分组，则停止定时器，否则为新的最老未确认分组重启定时器。

事件四：`rdt_rcv(rcvpkt) && corrupt(rcvpkt)`（收到损坏的分组）：动作为 $\Lambda$，即不执行任何操作。

#### 6.4.11.3 GBN 接收方扩展有限状态机

初始状态：`expectedseqnum = 0`，`sndpkt = make_pkt(-1, ACK, chksum)`（一个序号为 -1 的初始 ACK 分组，用于在尚未收到任何正确分组前能够回送 ACK），状态为 `Wait`。

事件一：`rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && hasseqnum(rcvpkt, expectedseqnum)`（收到未损坏且序号恰为期望序号的分组）

```
extract(rcvpkt, data)
deliver_data(data)
sndpkt = make_pkt(expectedseqnum, ACK, chksum)
udt_send(sndpkt)
expectedseqnum++
```

即取出数据向上交付，回送序号为 `expectedseqnum` 的 ACK，然后把 `expectedseqnum` 自增。

事件二：`default`（其余一切情况：分组损坏，或序号不是期望序号）

```
udt_send(sndpkt)
```

即丢弃该分组并**重发最近一次发出的 ACK**，不缓存任何乱序分组。

接收方行为的文字说明为：

- **只发 ACK**：对正确收到的、具有**最高按序序号**（highest in-order seq #）的分组总是回送 ACK；这会**产生重复 ACK**；接收方只需记住一个变量 `expectedseqnum`。
- **乱序分组**（out-of-order pkt）：直接**丢弃，不缓存**（no receiver buffering!），并重新 ACK 具有最高按序序号的分组。

#### 6.4.11.4 GBN 运行示例

图名为 GBN in action，参数为发送方窗口 $N=4$，序号 0～8。链路中序号为 2 的分组丢失。时序还原如下（发送方行为与接收方行为按图中顺序排列）。

| 阶段 | 发送方动作 | 接收方动作 |
|---|---|---|
| 1 | 发送 pkt0 | 收到 pkt0，交付；回送 ack0 |
| 2 | 发送 pkt1 | 收到 pkt1，交付；回送 ack1 |
| 3 | 发送 pkt2（图中在 pkt2 箭头上画叉并标注 loss，该分组丢失；发送方对其启动的定时器对应最老未确认分组 pkt2） | — |
| 4 | 发送 pkt3 | 收到 pkt3，序号 3 不等于期望序号 2，**丢弃**；重发 ack1 |
| 5 | 等待（wait） | — |
| 6 | 收到 ack0，发送 pkt4（窗口左边界推进到 1，窗口变为 1～4） | 收到 pkt4，丢弃；重发 ack1 |
| 7 | 收到 ack1，发送 pkt5（窗口变为 2～5） | 收到 pkt5，丢弃；重发 ack1 |
| 8 | 收到重复 ACK（ack1 的副本），**忽略重复 ACK**（ignore duplicate ACK） | — |
| 9 | pkt2 定时器超时（图中标注 pkt 2 timeout） | — |
| 10 | 重传 pkt2 | 收到 pkt2，交付；回送 ack2 |
| 11 | 重传 pkt3 | 收到 pkt3，交付；回送 ack3 |
| 12 | 重传 pkt4 | 收到 pkt4，交付；回送 ack4 |
| 13 | 重传 pkt5 | 收到 pkt5，交付；回送 ack5 |

图中左侧还平行画出了发送方窗口的状态序列（序号 0～8 的格子，窗口 $N=4$）。按上述时序，窗口位置依次变化为：

| 时刻 | 说明 | $send\_base$ | $nextseqnum$ | 窗口覆盖序号 |
|---|---|---|---|---|
| 初始 | 尚未发送数据 | 0 | 0 | 0～3 |
| 发送 pkt0～pkt3 后 | 窗口内 4 个分组全部在途 | 0 | 4 | 0～3 |
| 收到 ack0 并发送 pkt4 后 | 左边界右移一格 | 1 | 5 | 1～4 |
| 收到 ack1 并发送 pkt5 后 | 左边界再右移一格 | 2 | 6 | 2～5 |
| pkt2 超时后 | 重传窗口内全部在途分组 pkt2、pkt3、pkt4、pkt5 | 2 | 6 | 2～5 |
| 收到 ack2、ack3、ack4、ack5 后 | 窗口内无未确认分组，定时器停止 | 6 | 6 | 6～9 |

此例展示 GBN 的两个特征：序号 2 丢失后，序号 3、4、5 虽然正确到达接收方，但因不是期望序号而被逐一丢弃，接收方反复重发 ack1；发送方超时后把窗口内的 4 个分组全部重传，接收方才按序交付 2、3、4、5。

#### 6.4.11.5 例题：GBN 超时后的重传范围（课件 6-52）

**题干**（原文）：Via the GBN protocol, a sender sent packets with seq # from 0 to 5. If the sender has only received ACK0 and ACK2 when a timeout happens, which packets should the sender retransmit?

中文题意：使用 GBN 协议，发送方发送了序号 0 到 5 的分组。若超时发生时，发送方只收到了 ACK0 和 ACK2，发送方应重传哪些分组？

**解**

第 1 步：明确 GBN 的 ACK 语义。GBN 使用累积确认，`ACK(n)` 表示序号 $n$ 及其之前的所有分组都已正确收到。

第 2 步：解读 ACK0。ACK0 表示序号 0 已被确认，因此 $send\_base\ge1$。

第 3 步：解读 ACK2。ACK2 表示序号 0、1、2 这 3 个分组都已被确认（序号 1 的 ACK 不需要单独出现，它已被 ACK2 覆盖）。因此窗口左边界推进为 $send\_base=2+1=3$。

第 4 步：确定尚未确认的分组。已发送范围为序号 0～5，已被确认到序号 2，故未确认序号为 3、4、5。

第 5 步：确定超时动作。GBN 在超时发生时，重传窗口内最老未确认分组及其后**所有**已发送未确认分组，即重传序号 3、4、5。

**答案**：发送方应重传序号为 3、4、5 的分组。

**校验**：用原数据检查。发送总量为 6 个分组（0～5）；已确认分组为 0、1、2（由 ACK0 与 ACK2 累积确定），共 3 个；未确认分组数为 $6-3=3$，与"重传 3 个分组（3、4、5）"一致。特别地，序号 1 不重传——它已被 ACK2 累积确认，若重传序号 1 反而违背了累积确认的含义。

### 6.4.12 选择重传（Selective Repeat，SR）

#### 6.4.12.1 基本机制

- 接收方对**每一个**正确收到的分组**单独**回送 ACK；对乱序到达的分组予以**缓存**，以便最终按序交付给上层。
- 发送方**只重传未收到 ACK 的分组**；发送方为**每一个**未确认分组维护一个定时器。
- 发送方窗口由 $N$ 个连续序号组成，用来限制"已发送、未确认"的分组的序号范围。

#### 6.4.12.2 发送方与接收方窗口

课件给出两个窗口视图。

(a) 发送方视角的序号空间

| 图中颜色 | 含义 |
|---|---|
| 绿色（already ack'ed） | 已被确认 |
| 黄色（sent, not yet ack'ed） | 已发送、尚未确认 |
| 蓝色（usable, not yet sent） | 可用、尚未发送 |
| 白色（not usable） | 不可用 |

图中以 `send_base` 标出窗口左边界，以 `nextseqnum` 标出已发送与尚未发送的分界，二者之间为已发送未确认的分组；窗口右边界与 `send_base` 之间的距离为 window size $N$。

(b) 接收方视角的序号空间

| 图中颜色 | 含义 |
|---|---|
| 粉色（out of order (buffered) but already ack'ed） | 乱序到达、已缓存并已回送 ACK |
| 灰色（Expected, not yet received） | 期望收到、尚未收到 |
| 浅蓝色（acceptable (within window)） | 窗口内、可接受 |
| 白色（not usable） | 不可用 |

接收方窗口的左边界标为 `rcv_base`，窗口宽度同为 $N$。图中用虚线把发送方窗口的左边界与接收方窗口对应起来，表示两端窗口在理想情况下同步滑动；由于 ACK 存在传播延迟，接收方窗口位置会领先于发送方窗口。

#### 6.4.12.3 发送方与接收方的动作规则

| 端 | 事件 | 动作 |
|---|---|---|
| 发送方 | 上层交付数据（data from above） | 若下一个可用序号落在窗口内，则发送该分组 |
| 发送方 | `timeout(n)` | 重发分组 $n$，重启定时器 |
| 发送方 | 收到 `ACK(n)` 且 $n\in[sendbase,\ sendbase+N-1]$ | 把分组 $n$ 标记为已收到；若 $n$ 是最小的未确认分组，则把窗口左边界推进到下一个未确认序号 |
| 接收方 | 收到分组 $n$ 且 $n\in[rcvbase,\ rcvbase+N-1]$ | 回送 `ACK(n)`；若为乱序分组则缓存；若为按序分组则交付（并把缓存中随后的按序分组一并交付），同时把窗口推进到下一个尚未收到的序号 |
| 接收方 | 收到分组 $n$ 且 $n\in[rcvbase-N,\ rcvbase-1]$ | 回送 `ACK(n)`（属于窗口之前的已确认分组，需重发 ACK 让发送方推进） |
| 接收方 | 其他情况 | 忽略 |

与 GBN 相比，SR 接收方对窗口内的乱序分组不再丢弃，而是缓存并单独确认；SR 发送方只重传真正丢失的那一个分组。代价是发送方需要为每个未确认分组各维护一个定时器，接收方需要缓存空间。

#### 6.4.12.4 SR 运行示例

图名为 Selective repeat in action，参数同样为发送方窗口 $N=4$、序号 0～8，序号 2 的分组丢失。时序还原如下。

| 阶段 | 发送方动作 | 接收方动作 |
|---|---|---|
| 1 | 发送 pkt0 | 收到并交付 pkt0；回送 ack0 |
| 2 | 发送 pkt1 | 收到并交付 pkt1；回送 ack1 |
| 3 | 发送 pkt2（图中在 pkt2 箭头上画叉并标注 loss） | — |
| 4 | 发送 pkt3 | 收到 pkt3，序号 3 在接收窗口内但非期望序号，**缓存**；回送 ack3 |
| 5 | 等待（wait） | — |
| 6 | 收到 ack0，发送 pkt4 | 收到 pkt4，缓冲；回送 ack4 |
| 7 | 收到 ack1，发送 pkt5 | 收到 pkt5，缓冲；回送 ack5 |
| 8 | 记录 ack3 到达（record ack3 arrived） | — |
| 9 | pkt2 定时器超时（图中标注 pkt 2 timeout） | — |
| 10 | 重发 pkt2 | 收到 pkt2：按序交付 pkt2，并把缓存中的 pkt3、pkt4、pkt5 一并按序交付（图中标注 deliver pkt2~pkt5）；回送 ack2 |
| 11 | 记录 ack4 到达（record ack4 arrived） | — |
| 12 | 记录 ack5 到达（record ack5 arrived） | — |

图中左侧同样画出窗口状态（标注为 after receipt，即"收到各 ACK 之后"）。按上述时序，只有当序号 2 被确认后，窗口左边界才能越过 2 继续滑动：

| 时刻 | 已确认序号 | $send\_base$ | 窗口覆盖序号 |
|---|---|---|---|
| 初始 | 无 | 0 | 0～3 |
| 收到 ack0、ack1 后 | 0、1 | 2 | 2～5（已发送 0～5） |
| 收到 ack3 后 | 0、1、3 | 2（3 非最小未确认分组，窗口不滑动） | 2～5 |
| 收到 ack4、ack5 后 | 0、1、3、4、5 | 2（仍缺 ack2） | 2～5 |
| 收到 ack2 后 | 0～5 全部确认 | 6 | 6～9 |

原图提出的问题为：Q: what happens when ack2 arrives?（ack2 到达时会发生什么？）

**解答**：ack2 到达时，发送方检查序号 2 是否落在窗口内（$2\in[2,5]$，是），于是把序号 2 标记为已收到；由于序号 2 正是当前最小的未确认分组，发送方把窗口左边界推进到下一个未确认序号。此时序号 3、4、5 的 ACK 之前已经记录（ack3、ack4、ack5 均到达），因此下一个未确认序号是 6，窗口左边界一次推进到 6，窗口覆盖 6～9；发送方随后可以发送序号 6 及之后的新的分组。这一行为正是"窗口左边界推进到下一个未确认序号"规则在连续确认场景下的体现：即便之前的 ACK 是乱序到达的，累积起来的确认信息也会在缺口被填补后一次性生效。

#### 6.4.12.5 选择重传的两难（dilemma）

课件给出一个反例：序号空间为 0、1、2、3（共 4 个序号），窗口长度 $N=3$。由于 $N$ 超过序号空间的一半，接收方无法仅凭序号区分"新分组"与"重传的旧分组"。两种时序如下。

(a) 无问题（no problem）

| 步骤 | 发送方 | 接收方 |
|---|---|---|
| 1 | 发送 pkt0 | 初始窗口为 0、1、2；收到后交付，回 ACK0，窗口移为 1、2、3 |
| 2 | 发送 pkt1 | 收到后交付，回 ACK1，窗口移为 2、3、0 |
| 3 | 发送 pkt2 | 收到后交付，回 ACK2，窗口移为 3、0、1 |
| 4 | 收到 ACK0，发送窗口移为 1、2、3；发送 pkt3，但该包丢失（原图红叉） | 未收到 pkt3，窗口仍为 3、0、1 |
| 5 | 收到 ACK1，发送窗口移为 2、3、0；发送下一轮序号为 0 的新分组 | 序号 0 在当前窗口内，作为新数据接受、缓存；等待 pkt3 后才能按序交付 |

这里的第二个 pkt0 是发送方实际允许发送的新分组。原图的关键是 pkt3 丢失，接收窗口仍为 $\{3,0,1\}$；不能把 pkt3 写成已成功接收，否则会改变两种场景的比较状态。

(b) 出错（oops!）

| 步骤 | 发送方 | 接收方 |
|---|---|---|
| 1 | 发送 pkt0 | 收到 pkt0，交付，回送 ack0 |
| 2 | 发送 pkt1 | 收到 pkt1，交付，回送 ack1 |
| 3 | 发送 pkt2 | 收到 pkt2，交付，回送 ack2 |
| 4 | ack0、ack1、ack2 **全部丢失**（图中在三个 ACK 上均画叉）；发送方窗口仍为 0、1、2，$send\_base=0$ | 窗口已推进为 3、0、1（$rcv\_base=3$） |
| 5 | pkt0 定时器超时（图中标注 timeout），**重传 pkt0** | 收到序号为 0 的分组：0 落在接收窗口 3、0、1 之内，接收方**无法识别这是重复分组**，按新分组接受并缓存，并回送 ack0 |

(b) 中接收方所处窗口状态与 (a) 第 5 步完全相同，接收方"将接受序号为 0 的报文段"这一行为在两种场景下**完全一致**，但 (a) 中的序号 0 是新数据、(b) 中的序号 0 是重传的旧数据。课件的结论是：receiver can't see sender side. receiver behavior identical in both cases! something's (very) wrong!（接收方看不到发送方的状态，两种场景下接收方行为完全相同，这是错误的）。后果是"duplicate data accepted as new in (b)"，即重复数据被当作新数据接受。

课件提出的问题：Q: what relationship between seq # size and window size to avoid problem in (b)?（序号空间大小与窗口大小应满足什么关系，才能避免 (b) 中的问题？）

**解答**：设序号空间大小为 $N_{seq}$、窗口长度为 $N$，则必须满足

$$N\le\frac{N_{seq}}{2}$$

即窗口长度不得超过序号空间的一半（等价地，序号空间至少为窗口长度的 2 倍）。本例中 $N_{seq}=4$，故要求 $N\le2$；课件取 $N=3>2$，因此出现 (b) 的错误。

**校验（用原数据）**：在 $N_{seq}=4$、$N=2$ 时，若 pkt0、pkt1 对应的两个 ACK 全部丢失，发送方超时重传 pkt0 时其窗口为 0、1，而接收方在收到 pkt0、pkt1 后窗口已为 2、3。序号 0 不落在接收窗口 $\{2,3\}$ 内，接收方会按"其他情况"处理（忽略或回送 ACK），不会把重复数据当作新数据接受，问题消失。可见 (b) 的根因是 $N=3$ 使发送方窗口 $\{0,1,2\}$ 与接收方推进后的窗口 $\{3,0,1\}$ 在序号 0 上重叠。

#### 6.4.12.6 GBN 与 SR 的取舍

GBN 的接收方不需要缓存，状态变量只有一个 `expectedseqnum`，但一个分组丢失会导致其后的所有分组被丢弃并重传，带宽浪费随窗口长度增大而增大；SR 的接收方需要缓存乱序分组，发送方需要为每个未确认分组维护定时器，协议状态更复杂，但只重传真正丢失的分组。两者都受窗口长度与序号空间关系的约束：GBN 要求 $N\le2^{k}-1$，SR 要求 $N\le2^{k}/2$。

## 6.5 面向连接的传输：TCP（Connection-Oriented Transport: TCP）

本节之下的分项为 segment structure（报文段结构）、reliable data transfer（可靠数据传输）、flow control（流量控制）、connection management（连接管理）。课件给出的 TCP 相关 RFC 为：RFC 793、RFC 1122、RFC 1323、RFC 2018、RFC 2581。

### 6.5.1 TCP 概述（TCP Overview）

TCP 的基本特征共 6 项：

- **点对点（point-to-point）**：一条 TCP 连接只有**一个发送方和一个接收方**（one sender, one receiver）。TCP 不提供一对多或多对多的传输能力，组播不属于 TCP 的功能范围。
- **可靠的、按序的字节流（reliable, in-order byte stream）**：TCP 把上层交付的数据视为**连续的字节流**，不对字节流内部划界，因此"没有报文边界"（no "message boundaries"）。应用层写入两次的数据可能被合并到一个报文段中发送，也可能被拆分到多个报文段中发送；接收方收到的是按序排列的字节流，需要由应用层自己界定消息边界。
- **流水线（pipelined）**：TCP 允许同时有多个在途报文段，其数目由 TCP 的**拥塞控制和流量控制**共同决定的窗口大小（window size）来限制。
- **全双工数据（full duplex data）**：同一条连接上可以进行**双向**的数据流动，A 向 B 发送数据的同时，B 也可以向 A 发送数据。课件在此处引入 **MSS**（maximum segment size，最大报文段长度），即一个 TCP 报文段中数据部分所能承载的最大字节数。
- **面向连接（connection-oriented）**：在交换数据之前，收发双方要通过**握手**（handshaking，即交换控制报文）初始化发送方与接收方的状态（例如双方各自的初始序号）。
- **流量控制（flow controlled）**：发送方不会以超过接收方处理能力的速率发送数据（sender will not overwhelm receiver）。流量控制保护的是**接收方**，与拥塞控制（保护**网络**）不是同一回事。

### 6.5.2 TCP 报文段结构（TCP Segment Structure）

TCP 报文段的完整字段布局如下，每一行的宽度为 32 比特。

| 行 | 字段 | 宽度 | 含义 |
|---|---|---|---|
| 1 | source port #（源端口号） | 16 bit | 发送方进程的端口号 |
| 1 | dest port #（目的端口号） | 16 bit | 接收方进程的端口号 |
| 2 | sequence number（序号） | 32 bit | 本报文段数据部分**第一个字节**在字节流中的编号（counting by bytes of data (not segments!)：按数据字节计数，而非按报文段计数） |
| 3 | acknowledgment number（确认号） | 32 bit | 期望从对方收到的**下一个字节**的序号 |
| 4 | head len（首部长度） | 4 bit | TCP 首部长度（以 32 位字为单位） |
| 4 | not used（未使用） | 6 bit | 保留未使用 |
| 4 | U A P R S F（标志位） | 6 bit | 六个控制标志，含义见下一表 |
| 4 | receive window（接收窗口） | 16 bit | # bytes rcvr willing to accept，即接收方当前愿意接受的字节数 |
| 5 | checksum（校验和） | 16 bit | Internet checksum (as in UDP)，与 UDP 相同的因特网校验和 |
| 5 | Urg data pointer（紧急数据指针） | 16 bit | 紧急数据的末尾位置指示 |
| 6 | options（变长选项） | 可变长度 | 选项字段 |
| 7 | application data（应用数据） | 可变长度 | 上层交付的载荷 |

六个标志位的含义（课件原文）：

| 标志位 | 名称 | 含义 |
|---|---|---|
| URG | urgent data | 紧急数据（generally not used，一般不使用） |
| ACK | ACK # valid | 确认号字段有效 |
| PSH | push data now | 立即推送数据（generally not used，一般不使用） |
| RST | reset | 连接复位 |
| SYN | synchronize | 连接建立命令 |
| FIN | finish | 连接拆除命令 |

课件对 RST、SYN、FIN 三个标志位的统一说明为 "connection estab (setup, teardown commands)"，即用于连接建立与拆除。需要区分的是：ACK 标志位表示"确认号字段有效"，而 acknowledgment number 字段本身是确认序号；两者的名称相近但作用不同。

由字段布局可以直接读出 TCP 首部的固定长度为 5 行 × 32 bit $=20$ 字节（不含 options 和 application data）；options 为可变长度，因此 TCP 首部长度可变，这正是"head len"字段存在的必要性。图中有三处标注需单独留意：

- **sequence number / acknowledgment number** 两行旁的标注为 "counting by bytes of data (not segments!)"，说明序号与确认号按**字节**计数，而不是按报文段个数计数。
- **receive window** 旁的标注为 "# bytes rcvr willing to accept"，即接收窗口字段给出接收方可接受的字节数，用于流量控制。
- **checksum** 旁的标注为 "Internet checksum (as in UDP)"，即校验算法与 6.3 节 UDP 校验和相同（把报文段内容视作 16 位整数序列求和后取反码）。

### 6.5.3 TCP 序号与确认号（TCP seq. numbers, ACKs）

#### 6.5.3.1 TCP 序号（sequence numbers）

TCP 把应用层交付的数据看作**无结构的、连续有序的字节流**。序号字段（sequence number）的取值规则是：**该报文段数据部分第一个字节在整个字节流中的字节编号**（byte stream "number" of first byte in segment's data）。因此 TCP 的序号以**字节**为单位，而不是以报文段为单位：若某报文段携带 $L$ 字节数据且首字节编号为 $x$，则该报文段覆盖字节 $x,\ x+1,\ \dots,\ x+L-1$，其序号字段为 $x$；下一个报文段的序号为 $x+L$。

TCP 连接建立时，通信双方各自选定一个初始序号（InitialSeqNum，ISN），此后该方向字节流中的每个字节依次获得连续编号。由于序号是 32 位字段，编号在 $0\sim 2^{32}-1$ 的范围内循环使用。

**课件示例**：设 Host A 上的一个进程要通过一条 TCP 连接把 500,000 字节的数据文件发送给 Host B 上的一个进程；MSS（最大报文段长度，即一个报文段能携带的最大数据字节数）为 1,000 字节；第 1 个字节编号为 0。求第 3 个报文段的序号。

逐步计算：

1. 每个报文段最多携带 MSS = 1,000 字节数据，故字节流按每 1,000 字节切分为一个报文段。
2. 第 1 个报文段：数据为字节 $0\sim 999$，序号 = 0。
3. 第 2 个报文段：数据为字节 $1000\sim 1999$，序号 = 1000。
4. 第 3 个报文段：数据为字节 $2000\sim 2999$，序号 = **2000**。
5. 报文段总数为 $500{,}000 \div 1{,}000 = 500$ 个。第 500 个（最后一个）报文段的序号为 $499\times 1000 = 499{,}000$，覆盖字节 $499{,}000\sim 499{,}999$。

用原数据校验：500 个报文段 × 1,000 字节 = 500,000 字节，等于文件长度；字节编号从 0 到 499,999 恰好包含 500,000 个不同的编号，与逐字节编号的规则一致；最后一个报文段末字节编号 499,999 = 文件长度 500,000 − 1，也一致。

源图以一条被分成方格的"文件"长条表示字节编号 $0,\ 1,\ \dots,\ 1{,}000,\ 1{,}999,\ \dots,\ 499{,}999$，用括号把前一段方格标注为 "Data for 1st segment"、紧随其后的一段标注为 "Data for 2nd segment"；方格之间的 "//" 表示被省略的中间方格。图中并排列出 "Seq # of the 1st segment: 0; Seq # of the 2nd segment: 1000;" 与待求的 "Seq # of the 3rd segment: ?"。（方格编号的显示方式为源图排版，实际字节编号是连续的。）

#### 6.5.3.2 TCP 确认号与累积确认（acknowledgments, cumulative ACK）

确认号（acknowledgment number）的取值规则是：**该主机期望从对方收到的下一个字节的序号**（seq # of next byte expected from other side）。由于 TCP 只按字节流的顺序确认，确认号为 $y$ 表示编号为 $y-1$ 及其之前的所有字节都已正确收到，这种一次确认一段连续字节的方式称为**累积确认**（cumulative ACK）。确认号总是与"从对方收到的数据"相对应，与本报文段自身携带的数据无关；TCP 报文段是**全双工**的，一个方向的数据可以捎带另一个方向的确认。

**课件示例**

情形 1：Host A 已收到来自 B 的编号 $0\sim 535$ 的全部字节，现在要向 Host B 发送一个报文段。

- A 正在等待字节 536 及其后的所有字节；
- 所以 A 在确认号字段中填入 **536**。

情形 2（累积确认）：Host A 从 Host B 收到一个含字节 $0\sim 535$ 的报文段，又收到一个含字节 $900\sim 1{,}000$ 的报文段；由于某种原因 A 尚未收到字节 $536\sim 899$。

- A 仍然在等待字节 536（及其后字节）；
- A 发往 B 的下一个报文段的确认号字段中填入 **536**。

说明：第二个报文段（字节 900 及以后）虽已到达，但在它之前存在从 536 开始的缺口（gap），累积确认只能一次报告到缺口起点处，即只能确认到 535，故确认号为 536。接收方是否缓存乱序到达的数据由实现决定。

（记录：课件原文把第二个报文段写作 "another segment containing bytes 900 ~ 1,000"，按字节流编号的语境应为编号 900 起的一段字节；此处照录课件原文。）

#### 6.5.3.3 序号与确认号在报文段中的位置、发送方序号空间与窗口

发送方发出的报文段头部字段，自上而下依次为 source port #、dest port #、sequence number、acknowledgment number、rwnd、checksum、urg pointer，其中 **sequence number** 字段指向下方"发送方序号空间（sender sequence number space）"的起始位置。接收到的报文段（incoming segment to sender）中 **acknowledgment number** 字段填写的值即窗口上沿对应的字节序号。

发送方序号空间（sender sequence number space）自左向右分为四段：

| 段 | 图中标注 | 含义 |
|---|---|---|
| 1 | sent, ACKed | 已发送并已被确认的字节 |
| 2 | sent, not-yet ACKed（"in-flight"） | 已发送但尚未被确认的字节，即在途字节 |
| 3 | usable but not yet sent | 尚可发送、但还没有发送的字节 |
| 4 | not usable | 不可用字节，超出当前允许发送范围的字节 |

图中窗口大小（window size）$N$ 的标尺覆盖第 2 段与第 3 段，即 $N$ 给出当前允许处于"已发送未确认"状态与"可以发送"状态的字节总数上限。随着累积确认到达，第 1 段向右延伸，第 2 段中已被确认的部分并入第 1 段，窗口右沿随之向右滑动。图中未给出 $N$ 的具体数值。

课件在此处的问答是：Q：接收方如何处理乱序到达的报文段？A：TCP 规范没有规定（TCP spec doesn't say），由实现者自行决定（up to implementor）。

#### 6.5.3.4 简单 telnet 场景示例

场景：Host A 为客户端，Host B 为服务器；用户在 A 侧键入字符 'C'，服务器回显该字符。三个报文段及其标注如下：

| 序号 | 方向 | 报文段内容 | 图中旁注 |
|---|---|---|---|
| 1 | Host A → Host B | Seq = 42, ACK = 79, data = 'C' | 左注 "User types 'C'" |
| 2 | Host B → Host A | Seq = 79, ACK = 43, data = 'C' | 右注 "host ACKs receipt of 'C', echoes back 'C'" |
| 3 | Host A → Host B | Seq = 43, ACK = 80 | 左注 "host ACKs receipt of echoed 'C'" |

逐步解释各字段：

1. 第 1 个报文段：A 的字节流中下一个待发字节编号为 42，本段只携带 1 字节数据（字符 'C'），故 Seq = 42，该段覆盖字节 42；A 已收到 B 发来的编号 0 到 78 的字节，期望 B 的下一个字节为 79，故 ACK = 79。
2. 第 2 个报文段：B 的字节流中下一个待发字节编号为 79（B 此前的数据占用字节 0~78），本段携带回显字符 'C'，故 Seq = 79，覆盖字节 79；B 已收到 A 的字节 42，期望 A 的下一个字节为 43，故 ACK = 43。该确认与回显数据在同一个报文段中捎带完成。
3. 第 3 个报文段：A 已收到 B 的字节 79，期望下一个为 80，故 ACK = 80；A 自己有新数据要发送时其序号为 43（A 上一次发送占用字节 42），故 Seq = 43，本段不含数据。

用原数据校验：第 2 段的 ACK = 43 = 第 1 段 Seq 42 + 该段数据长度 1，成立；第 3 段的 ACK = 80 = 第 2 段 Seq 79 + 该段数据长度 1，成立；第 3 段的 Seq = 43 = 第 1 段 Seq 42 + 该段数据长度 1，说明 A 的序号只随实际发送的数据字节推进，收到对方的 ACK 不改变自己的发送序号，成立。

### 6.5.4 TCP 往返时间估计与超时（TCP round trip time, timeout）

#### 6.5.4.1 超时值的设定

Q：如何设定 TCP 的超时值（timeout value）？

- 超时值必须**比 RTT 长**；但 RTT 是变化的（RTT varies）。
- 太短（too short）：产生过早超时（premature timeout），引起不必要的重传。
- 太长（too long）：对报文段丢失反应太慢。

Q：如何估计 RTT？

- SampleRTT（采样 RTT）：从报文段发出的时刻到收到该报文段的确认的时刻之间测得的时间。
- 测量时应**忽略重传**（ignore retransmissions）：即只对未被重传过的报文段测量 SampleRTT。
- SampleRTT 会波动，而希望得到更平滑（"smoother"）的 RTT 估计：对最近若干次测量取平均，而不是只取当前的 SampleRTT。

#### 6.5.4.2 EstimatedRTT：指数加权移动平均

$$\text{EstimatedRTT} = (1-\alpha)\cdot\text{EstimatedRTT} + \alpha\cdot\text{SampleRTT}$$

符号含义：$\text{EstimatedRTT}$ 为估计的往返时间（单位与 SampleRTT 相同，通常为毫秒或秒）；$\text{SampleRTT}$ 为最新一次采样得到的往返时间；$\alpha$ 为权重系数，典型值 $\alpha = 0.125$。该式为**指数加权移动平均**（exponential weighted moving average）：过去样本对当前估计的影响按指数速度快速衰减。代入 $\alpha = 0.125$ 后，每次更新保留上一次估计的 87.5%（$1-\alpha$），并吸收新样本的 12.5%。

实测曲线 "RTT: gaia.cs.umass.edu to fantasia.eurecom.fr" 中，纵轴为 RTT（milliseconds），刻度为 100、150、200、250、300、350；横轴为 time (seconds)，刻度为 1、8、15、22、29、36、43、50、57、64、71、78、85、92、99、106；图中一组折线由深色菱形点连接而成，图例标为 sampleRTT，逐点波动明显；另一组折线由浅色方块点连接而成，图例标为 EstimatedRTT，走势平滑地跟随 sampleRTT。源图未标注各点的具体坐标数值。

#### 6.5.4.3 DevRTT 与超时间隔

超时间隔（timeout interval）等于 EstimatedRTT 加上一个"安全余量"（safety margin）；EstimatedRTT 的波动越大，所需安全余量越大。用 SampleRTT 偏离 EstimatedRTT 的程度来估计这种波动：

$$\text{DevRTT} = (1-\beta)\cdot\text{DevRTT} + \beta\cdot|\text{SampleRTT} - \text{EstimatedRTT}|$$

典型取值 $\beta = 0.25$。符号含义：$\text{DevRTT}$ 为 RTT 偏差的指数加权移动平均估计（单位同 RTT）；$|\text{SampleRTT} - \text{EstimatedRTT}|$ 为最新一次采样值相对当前估计值的绝对偏差；$\beta$ 为权重系数。

$$\text{TimeoutInterval} = \text{EstimatedRTT} + 4\cdot\text{DevRTT}$$

式中 $\text{EstimatedRTT}$ 为"估计的 RTT"，$4\cdot\text{DevRTT}$ 为"安全余量"（图中分别用箭头从两项下方指出，标注为 "estimated RTT" 与 "'safety margin'"）。当 SampleRTT 与 EstimatedRTT 的偏差增大时，DevRTT 增大，超时间隔随之增大，从而降低过早超时的概率。（课件注明：可在 `http://gaia.cs.umass.edu/kurose_ross/interactive/` 查看在线交互练习中的更多示例。）

### 6.5.5 TCP 可靠数据传输（TCP reliable data transfer）

#### 6.5.5.1 TCP 可靠传输的机制构成

TCP 在 IP 的不可靠服务之上建立可靠数据传输（rdt，reliable data transfer）服务。课件列出的机制要素为：

- 流水线式报文段（pipelined segments）：发送方可以连续发送多个尚未确认的报文段，而不是每发一个就停下来等确认；
- 累积确认（cumulative acks）：确认号语义为下一个期望字节，一次确认一段连续字节；
- 单一重传定时器（single retransmission timer）：一个连接同一时刻只使用一个重传定时器。

重传由以下事件触发：

- 超时事件（timeout events）；
- 重复确认（duplicate acks）。

课件说明，先考虑**简化的 TCP 发送方**，其中：忽略重复确认（ignore duplicate acks），忽略流量控制与拥塞控制（ignore flow control, congestion control）。

#### 6.5.5.2 TCP 发送方事件

**（1）来自应用层的数据（data rcvd from app）**

- 创建报文段并填写序号（create segment with seq #）；
- 序号是该报文段中第一个数据字节的字节流编号（seq # is byte-stream number of first data byte in segment）；
- 若定时器当前未运行则启动定时器：
  - 可把这个定时器理解为针对**最早的未确认报文段**（timer as for oldest unacked segment）；
  - 超时间隔为 TimeOutInterval。

**（2）超时（timeout）**

- 重传引起超时的那个报文段（retransmit segment that caused timeout）；
- 重启定时器（restart timer）。

**（3）收到确认（ack rcvd）**

- 如果该确认确认了此前未被确认的报文段（if ack acknowledges previously unacked segments）：
  - 更新已知被确认的状态（update what is known to be ACKed）；
  - 若仍有未确认的报文段，则启动定时器（start timer if there are still unacked segments）。

#### 6.5.5.3 TCP 发送方（简化）有限状态机

状态机只有一个状态 "wait for event"；初始化动作为：

```
NextSeqNum = InitialSeqNum
SendBase   = InitialSeqNum
```

变量含义：$\text{SendBase}$ 为最早的未被确认字节的序号；$\text{NextSeqNum}$ 为下一个将要发送的字节的序号；$\text{InitialSeqNum}$ 为连接建立时选定的初始序号。

**事件 1：data received from application above（收到上层应用数据）**

```
create segment, seq. #: NextSeqNum
pass segment to IP            (i.e., "send")
NextSeqNum = NextSeqNum + length(data)
if (timer currently not running)
    start timer
```

其中 length(data) 为本次从应用层交来的数据字节数。注意 NextSeqNum 按**数据字节长度**推进，序号仍以字节为单位。

**事件 2：timeout（超时）**

```
retransmit not-yet-acked segment with smallest seq. #
start timer
```

即超时后重传**序号最小的尚未确认的报文段**（最早的未确认报文段），并重启定时器。

**事件 3：ACK received, with ACK field value y（收到确认号字段值为 y 的确认）**

```
if (y > SendBase) {
    SendBase = y          %cumulative acks
    /* SendBase–1: last cumulatively ACKed byte */
    if (there are currently not-yet-acked segments)
        start timer
    else stop timer
}
```

只有当 $y > \text{SendBase}$ 时才更新 SendBase——这体现累积确认的直接效果，并顺带处理了延迟到达的旧确认与重复确认（$y \le \text{SendBase}$ 时状态不变）。更新后，$\text{SendBase}-1$ 为最后一个被累积确认的字节；若此时还有未确认报文段则启动定时器，否则停止定时器。

#### 6.5.5.4 重传场景之一：确认丢失与过早超时

**场景甲：确认丢失（lost ACK scenario）**

| 顺序 | 方向 | 事件 |
|---|---|---|
| 1 | Host A → Host B | Seq = 92, 8 bytes of data |
| 2 | Host B → Host A | ACK = 100（图中在该确认上画红叉 X，表示丢失） |
| 3 | Host A → Host B | 超时后重传 Seq = 92, 8 bytes of data |
| 4 | Host B → Host A | ACK = 100 |

结果标注：SendBase = 100。过程说明：A 发送的报文段覆盖字节 92~99，B 正确收到后回送 ACK = 100（期望下一个字节为 100），但该确认在网络中丢失；A 的定时器到期后重传同一报文段；B 再次收到重复的字节 92~99，由于已确认过这部分字节，仍然回送 ACK = 100；A 收到后把 SendBase 更新为 100。**接收方的累积确认使被重复传输的数据被正确处理，只是链路多传了一份数据。**

**场景乙：过早超时（premature timeout）**

| 顺序 | 方向 | 事件 |
|---|---|---|
| 1 | Host A → Host B | Seq = 92, 8 bytes of data |
| 2 | Host A → Host B | Seq = 100, 20 bytes of data |
| 3 | Host B → Host A | ACK = 100 |
| 4 | Host B → Host A | ACK = 120 |
| 5 | Host A → Host B | 超时后重传（图中标注为 Seq = 92, 8 bytes of data 的报文段） |
| 6 | Host B → Host A | ACK = 120 |

结果标注：初始 SendBase = 92；收到 ACK = 100 后 SendBase = 100；收到 ACK = 120 后 SendBase = 120；重复报文段到达 B 后 B 再次回送 ACK = 120，SendBase 保持 120。过程说明：A 连续发送覆盖字节 92~99 与字节 100~119 的两个报文段；B 两个都收到，分别回送 ACK = 100 与 ACK = 120；A 收到 ACK = 100 后 SendBase 推进到 100 并重启定时器，该定时器在 ACK = 120 到达之前提前到期，于是 A 发送了一次不必要的重传；此后 ACK = 120 到达，SendBase 推进到 120；被重传的旧数据到达 B 后，B 用累积确认再回一个 ACK = 120。**超时值估计偏小会造成不必要的重传；由于累积确认只认字节流位置，重复到达的旧数据不会破坏数据正确性。**

（记录：课件原图把该重传报文段标注为 "Seq = 92, 8 bytes of data"，而同一图又标注 SendBase 已由 92 推进到 100；此处按原图标注呈现，未作改写。）

#### 6.5.5.5 重传场景之二：累积确认避免不必要重传

| 顺序 | 方向 | 事件 |
|---|---|---|
| 1 | Host A → Host B | Seq = 92, 8 bytes of data（覆盖字节 92~99） |
| 2 | Host A → Host B | Seq = 100, 20 bytes of data（覆盖字节 100~119） |
| 3 | Host B → Host A | ACK = 100（图中在该确认上画红叉 X，表示丢失） |
| 4 | Host B → Host A | ACK = 120 |
| 5 | Host A → Host B | 超时后 Seq = 120, 15 bytes of data（覆盖字节 120~134） |

过程说明：A 连续发送两个报文段，B 全部收到，先后回送 ACK = 100 与 ACK = 120；其中 ACK = 100 丢失，但后到的 ACK = 120 是累积确认，表示字节 0~119 全部正确收到，覆盖了丢失确认所要表达的信息；因此 A 在超时触发的动作中不需要重传字节 100~119，而直接发送包含字节 120~134 的新报文段。**累积确认可以消除因单个确认丢失而导致的数据重传。**

#### 6.5.5.6 TCP 确认生成规则（[RFC 1122, RFC 5681]）

接收方事件与对应的 TCP 接收方动作如下（源表完整内容）：

| event at receiver（接收方事件） | TCP receiver action（TCP 接收方动作） |
|---|---|
| arrival of in-order segment with expected seq #. All data up to expected seq # already ACKed（到达按序报文段，其序号为期望序号；直到该期望序号的数据都已被确认） | delayed ACK. Wait up to 500ms for next segment. If no next segment, send ACK（延迟确认：最多等待 500ms 以等待下一个报文段；若没有下一个报文段，则发送 ACK） |
| arrival of in-order segment with expected seq #. One other segment has ACK pending（到达按序报文段，其序号为期望序号；另有一个报文段的确认待发送） | immediately send single cumulative ACK, ACKing both in-order segments（立即发送单个累积确认，同时确认这两个按序报文段） |
| arrival of out-of-order segment higher-than-expect seq. #. Gap detected（到达乱序报文段，其序号高于期望序号，检测到缺口） | immediately send duplicate ACK, indicating seq. # of next expected byte（立即发送重复确认，其中指明期望的下一个字节的序号） |
| arrival of segment that partially or completely fills gap（到达部分或完全填补缺口的报文段） | immediate send ACK, provided that segment starts at lower end of gap（立即发送确认，条件是本报文段从缺口的低端开始） |

第 3 行是重复确认（duplicate ACK）的产生条件：只要收到序号高于期望序号的乱序报文段，接收方就重复发送用期望序号构成的确认；重复确认因此成为发送方判断"某报文段可能丢失"的依据。

#### 6.5.5.7 TCP 快速重传（TCP fast retransmit）

问题背景：超时周期通常相对较长（time-out period often relatively long），因而重传丢失报文段之前存在较长延迟（long delay before resending lost packet）。

检测丢失的方法：通过重复确认检测丢失的报文段（detect lost segments via duplicate ACKs）。发送方通常连续发送许多报文段（sender often sends many segments back-to-back）；若其中某个报文段丢失，则很可能出现许多重复确认（if segment is lost, there will likely be many duplicate ACKs）。

**快速重传规则**：若发送方对**同一数据**收到"三个重复确认"（triple duplicate ACKs），就重传**序号最小的未确认报文段**；此时该未确认报文段很可能已丢失，因此不必等待超时到期。

**快速重传示例**

| 顺序 | 方向 | 事件 |
|---|---|---|
| 1 | Host A → Host B | Seq = 92, 8 bytes of data |
| 2 | Host A → Host B | Seq = 100, 20 bytes of data（该报文段丢失，图中红叉 X 标在 B 侧） |
| 3 | Host B → Host A | ACK = 100 |
| 4 | Host B → Host A | ACK = 100 |
| 5 | Host B → Host A | ACK = 100 |
| 6 | Host B → Host A | ACK = 100 |
| 7 | Host A → Host B | Seq = 100, 20 bytes of data（快速重传） |

过程说明：B 正确收到覆盖字节 92~99 的报文段后回送 ACK = 100，此后每收到一个序号高于期望值 100 的报文段，都会立即回送一个重复的 ACK = 100；图中 A 共收到四条 ACK = 100，其中第 2、3、4 条构成针对同一数据的三个重复确认，发送方据此立即重传 Seq = 100、20 字节数据的报文段，而不等待图中标注的 timeout 到期。**快速重传把丢失恢复的时间从"一个超时周期"缩短为"三个重复确认到达的时间"。**

### 6.5.6 TCP 流量控制（TCP flow control）

#### 6.5.6.1 流量控制要解决的问题

接收方协议栈自下而上依次为 IP code、TCP code、TCP socket receiver buffers、application process，上方为 application（应用）、下方为 OS（操作系统）。图中用两条箭头分别表示两个过程：应用进程从 TCP 套接字缓冲区取走数据的路径，以及 TCP 接收方把数据放入缓冲区的路径。

课件给出的因果关系：

- 应用进程可能从 TCP 套接字缓冲区取走数据的速度**慢于** TCP 接收方向缓冲区投放数据（发送方正在发送）的速度；
- 流量控制（flow control）：由**接收方控制发送方**，使发送方不会因为发送太多、太快而使接收方的缓冲区溢出（sender won't overflow receiver's buffer by transmitting too much, too fast）。

#### 6.5.6.2 rwnd 通告与发送方限制

- 接收方通过在**发给发送方的报文段的 TCP 头部**中填写 rwnd（receive window，接收窗口）字段，通告自己的空闲缓冲区大小；
  - RcvBuffer（接收缓冲区）大小通过套接字选项设置，典型默认值为 4096 字节；
  - 很多操作系统会自动调整 RcvBuffer 的大小；
- 发送方把未确认（"in-flight"，在途）的数据量**限制在接收方 rwnd 值以内**；
- 由此保证接收缓冲区不会溢出。

接收缓冲区方框中，上部为 buffered data（已缓冲的数据），下部为 free buffer space（空闲缓冲空间），方框顶部以向上的箭头标注 "to application process"（交给应用进程），方框底部以向上的箭头标注 "TCP segment payloads"（TCP 报文段载荷）。两个量分别标注为 **RcvBuffer**（缓冲区的总大小）与 **rwnd**（缓冲区中当前空闲的缓冲空间大小），三者关系为：

$$\text{rwnd} = \text{RcvBuffer} - (\text{已缓冲的数据字节数})$$

当应用进程从缓冲区取走数据时，已缓冲数据减少，空闲空间增大，接收方在后续发给发送方的报文段中通告的 rwnd 随之增大；反之，当到达的数据把缓冲区填满时 rwnd 减小到 0。

#### 6.5.6.3 技术问题：RcvWindow = 0 时的死锁与解决

课件描述的情形：

- 假设 RcvWindow = 0，并且接收方已经确认（ACK）了缓冲区内的**所有**报文段；
- 发送方在听到 RcvWindow > 0 之前不再发送新报文段；
- 接收方因为已无新的确认要发给发送方，所以永远不会发送 RcvWindow > 0；
- 结果：**死锁（DEADLOCK）**。

解决办法：

- TCP 规范要求发送方在 RcvWindow = 0 期间继续发送带**一个数据字节**的报文段，目的只是保持能持续收到来自接收方的确认；
- 到某个时刻接收方的缓冲区会变空，RcvWindow > 0 会被传回发送方，发送方随即恢复正常发送。

因此，接收方在窗口变为 0 后仍会被这类"探测"报文段触发确认，确认中携带最新的 rwnd；当应用进程逐步取走缓冲数据后，确认中的 rwnd 变为正值，发送方由此脱离等待状态。

### 6.5.7 连接管理（Connection Management）

#### 6.5.7.1 握手要完成的两件事

在真正交换数据之前，发送方与接收方必须先执行一次"握手（handshake）"。握手要完成两件事：

- **商定建立连接**：双方都要确认对方愿意建立这条连接，而不是单方面发起、另一端毫不知情地被动接收。
- **商定连接参数**：双方就本条连接所使用的各项参数达成一致。

双方在握手完成后都进入已建立状态，课件写作 **ESTAB**。连接变量（connection variables）在服务器端与客户端两侧各自维护：

| 连接变量 | 含义 |
|----------|------|
| seq # client-to-server | 客户端到服务器方向的序号 |
| seq # server-to-client | 服务器到客户端方向的序号 |
| rcvBuffer size | 接收缓冲区大小（接收窗口的依据） |
| at server, client | 上述变量在服务器与客户端两侧各自保存一份 |

对应的套接字 API 调用为：

- 客户端创建套接字：
  `Socket clientSocket = newSocket("hostname","port number");`
- 服务器接受连接，返回一个新的、专用于本次通信的套接字：
  `Socket connectionSocket = welcomeSocket.accept();`

这也说明：`welcomeSocket`（欢迎套接字）只负责接收连接请求，真正与客户端通信的是 `accept()` 返回的 `connectionSocket`。

#### 6.5.7.2 二路握手（2-way Handshake）能否始终成立

最直观的**二路握手**模型是：一方发出"Let's talk"（相当于 `req_conn(x)`），另一方回应"OK"（相当于 `acc_conn(x)`），双方随即都进入 ESTAB。就时序而言，发起方先"choose x"选定序号 x，再发出 `req_conn(x)`；接收方收到后也进入 ESTAB 并回送 `acc_conn(x)`；发起方收到后进入 ESTAB。全过程只有两个方向的报文。

二路握手在网络中**不能**始终正常工作，原因在于网络本身不具备这些假设：

- **可变时延（variable delays）**：报文在网络中的往返时间不固定。
- **重传报文（retransmitted messages）**：例如 `req_conn(x)` 因报文丢失而被重传，同一请求可能出现多次。
- **报文重排序（message reordering）**：报文到达顺序可能与发送顺序不同。
- **无法"看见"对端（can't "see" other side）**：一端不能直接观察另一端的真实状态，只能依据收到的报文推断。

根源在于二路握手的双方无法区分"这条报文是新的请求"和"这条报文是旧请求的重传"。

#### 6.5.7.3 二路握手的失败场景

**失败场景一：半开连接（half open connection）**

时序如下：

1. 客户端 "choose x"，发出 `req_conn(x)`。
2. 服务器收到后进入 ESTAB，回送 `acc_conn(x)`。
3. 客户端（因超时或已放弃）**重传** `req_conn(x)`。
4. 服务器再次收到这条重传请求，于是又建立了一条连接。
5. 连接 x 在服务器侧完成（"connection x completes"），但此时**客户端已经终止**（"client terminates"）。
6. 服务器并不知道客户端已经离开，仍然保留着这条连接（图中标注 "server forgets x"），形成**半开连接（half open connection，no client!）**。

问题实质：服务器无法分辨第 3 步的重传请求是一条全新的连接请求还是一条旧请求的重复，因此建立了客户端早已不存在的连接。

**失败场景二：重复请求与重复数据**

时序如下：

1. 客户端 "choose x"，发出 `req_conn(x)`；服务器进入 ESTAB，回送 `acc_conn(x)`。
2. 客户端**重传** `req_conn(x)`；服务器再次进入 ESTAB。
3. 客户端发送数据 `data(x+1)`，服务器 "accept data(x+1)"。
4. 随后连接 x 完成（"connection x completes"），客户端终止，服务器丢弃 x（"server forgets x"）。
5. 客户端再次**重传** `data(x+1)`，以及 `req_conn(x)`。
6. 服务器又重新进入 ESTAB，并再次 "accept data(x+1)"。

问题实质：客户端已经终止后重传的旧数据被服务器当作新数据接收，导致服务器端收到重复甚至错序的数据。二路握手无法从协议上排除这类情况，因此 TCP 采用三路握手。

#### 6.5.7.4 TCP 三路握手（TCP 3-way Handshake）

TCP 用三个报文把双方的状态绑定在一起，其关键点在于：第三个报文让服务器确认"客户端确实收到了我的响应"。

**客户端状态序列**：LISTEN → SYNSENT → ESTAB。
**服务器状态序列**：LISTEN → SYN RCVD → ESTAB。

报文交换与各步动作：

1. 客户端在 LISTEN 状态下 **choose init seq num, x; send TCP SYN msg**，发出的报文为
   `SYNbit=1, Seq=x`。
   该报文发出后客户端进入 **SYNSENT**。客户端从 LISTEN 到 SYNSENT 的动作是"send SYN（发送 SYN）"。
2. 服务器处于 LISTEN，收到 SYN 后 **choose init seq num, y; send TCP SYNACK msg, acking SYN**，发出的报文为
   `SYNbit=1, Seq=y; ACKbit=1; ACKnum=x+1`。
   三个字段同时置位：SYN 位置 1、自己的序号为 y、确认号是对 x 的确认（x+1）。服务器进入 **SYN RCVD**。
3. 客户端 **received SYNACK(x) indicates server is live; send ACK for SYNACK; this segment may contain client-to-server data**，发出的报文为
   `ACKbit=1, ACKnum=y+1`。
   客户端进入 **ESTAB**。这一步的 ACK 报文可以同时携带客户端到服务器的数据（piggyback，捎带），因此三次握手完成后不必再单独发第一个数据报文。
4. 服务器 **received ACK(y) indicates client is live**，也进入 **ESTAB**。

各状态转换的含义可以逐条对应：

| 转换 | 触发事件 | 动作 | 目的 |
|------|----------|------|------|
| LISTEN → SYNSENT | 客户端应用发起连接 | 选初始序号 x，发 SYN | 请求建立连接 |
| LISTEN → SYN RCVD | 收到 SYN | 选初始序号 y，发 SYNACK（确认 x+1） | 表示愿意连接，并确认收到请求 |
| SYNSENT → ESTAB | 收到 SYNACK(x) | 发 ACK（确认 y+1） | 确认服务器存活，且告知服务器"我已收到你的响应" |
| SYN RCVD → ESTAB | 收到 ACK(y) | 无（进入已建立） | 确认客户端存活 |

**三路握手的有限状态机（FSM）表示**

状态为 `closed`、`listen`、`SYN sent`、`SYN rcvd`、`ESTAB` 五个，转换边（事件/动作）如下：

- `closed` → `SYN sent`：客户端执行
  `Socket clientSocket = newSocket("hostname","port number");`
  事件 `SYN(seq=x)`（动作栏为空）。
- `closed` → `listen`：服务器执行
  `Socket connectionSocket = welcomeSocket.accept();`
  事件为 Λ（空事件，即服务器被动进入监听）。
- `listen` → `SYN rcvd`：事件 `SYN(x)`，动作 `SYNACK(seq=y,ACKnum=x+1)`，并 **create new socket for communication back to client**（为回送客户端的通信创建新套接字）。
- `SYN sent` → `ESTAB`：事件 `SYNACK(seq=y,ACKnum=x+1)`，动作 `ACK(ACKnum=y+1)`。
- `SYN rcvd` → `ESTAB`：事件 `ACK(ACKnum=y+1)`，动作为 Λ。

同一事件 `ACK(ACKnum=y+1)` 同时出现在 `SYN sent` 与 `SYN rcvd` 两条边上，对应客户端与服务器各自收到对方的确认。

### 6.5.8 TCP 关闭连接（Closing a Connection）

#### 6.5.8.1 关闭连接的规则

- 客户端与服务器**各自关闭自己这一侧**的连接：一方要关闭时，发送 **FIN 位 = 1** 的 TCP 报文段。
- 收到对方发来的 FIN 后，**必须回应 ACK**；在收到 FIN 时，这个 ACK **可以与本方自己的 FIN 合并**在同一个报文中发出。
- 双方**同时**交换 FIN 的情况也可以处理（即两个方向的 FIN 交叉发出时协议不会死锁）。

这是"半关闭"（half-close）语义：一方关闭后，另一方向可能仍能发送数据，直到它也发送 FIN。

#### 6.5.8.2 关闭连接的时序与状态

客户端状态序列：ESTAB → FIN_WAIT_1 → FIN_WAIT_2 → TIMED_WAIT → CLOSED。
服务器状态序列：ESTAB → CLOSE_WAIT → LAST_ACK → CLOSED。

报文交换与状态迁移：

1. 客户端应用调用 `clientSocket.close()`，客户端从 ESTAB 进入 **FIN_WAIT_1**，发出
   `FINbit=1, seq=x`。
   客户端在 FIN_WAIT_1 的描述是 **can no longer send but can receive data**（不能再发数据，但还能接收数据）。
2. 服务器收到 FIN 后从 ESTAB 进入 **CLOSE_WAIT**，回送
   `ACKbit=1; ACKnum=x+1`（对 x 的确认）。此时服务器侧标注 **can still send data**（仍可发送数据）。
3. 客户端收到 ACK 后进入 **FIN_WAIT_2**，其描述是 **wait for server close**（等待服务器关闭）。
4. 服务器发送自己的 FIN：
   `FINbit=1, seq=y`，服务器从 CLOSE_WAIT 进入 **LAST_ACK**，此时标注 **can no longer send data**（不能再发送数据）。
5. 客户端回送
   `ACKbit=1; ACKnum=y+1`，并进入 **TIMED_WAIT**；服务器收到后从 LAST_ACK 进入 **CLOSED**。
6. 客户端在 TIMED_WAIT 停留 **timed wait for 2\*max segment lifetime**（等待 2 倍最大报文段生存期），之后进入 **CLOSED**。

其中"2 倍最大报文段生存期"的作用是确保最后一个 ACK 若能到达服务器则服务器已关闭，同时让本连接中滞留在网络中的旧报文段全部过期消失，避免它们干扰后续复用相同端口的新连接。

### 6.5.9 TCP 状态序列总览（Sequences of TCP States）

课件把三路握手与关闭连接的状态合并成客户端与服务器完整的**生命周期环**。

**TCP Client Lifecycle（客户端生命周期）**

| 当前状态 | 动作/事件 | 下一状态 |
|----------|-----------|----------|
| CLOSED | Client application initiates a TCP connection；Send SYN | SYN_SENT |
| SYN_SENT | Receive SYN & ACK, send ACK | ESTABLISHED |
| ESTABLISHED | Client application initiates close connection；Send FIN | FIN_WAIT_1 |
| FIN_WAIT_1 | Receive ACK, send nothing | FIN_WAIT_2 |
| FIN_WAIT_2 | Receive FIN, send ACK | TIME_WAIT |
| TIME_WAIT | Wait 30 seconds | CLOSED |

**TCP Server Lifecycle（服务器生命周期）**

| 当前状态 | 动作/事件 | 下一状态 |
|----------|-----------|----------|
| CLOSED | Server application creates a listen socket | LISTEN |
| LISTEN | Receive SYN, send SYN & ACK | SYN_RCVD |
| SYN_RCVD | Receive ACK, send nothing | ESTABLISHED |
| ESTABLISHED | Receive FIN, send ACK | CLOSE_WAIT |
| CLOSE_WAIT | Send FIN | LAST_ACK |
| LAST_ACK | Receive ACK, send nothing | CLOSED |

注：客户端环中 TIME_WAIT 的等待时间标注为 30 秒（课件原话 "Wait 30 seconds"），而 6.5.8 中的定时等待一般性描述为"2\*max segment lifetime"。两处是同一机制的不同表述，30 秒是课件给出的具体取值。

## 6.6 拥塞控制原理（Principles of Congestion Control）

### 6.6.1 拥塞的定义与现象

课件对**拥塞（congestion）**给出的非正式定义是：**"too many sources sending too much data too fast for network to handle"**（太多发送方发送了太多数据、速率太快，以致网络无法处理）。

必须区分拥塞控制与流量控制：

- **流量控制（flow control）**处理的是**发送方与接收方之间**速率不匹配的问题，即接收方来不及处理时抑制发送方。
- **拥塞（congestion）**处理的是**网络内部（路由器、链路）**承受不了总负载的问题，与某个特定接收方的处理能力无关。

拥塞的具体表现（manifestations）有两类：

- **丢包（lost packets）**：路由器缓冲区溢出（buffer overflow at routers）。
- **长时延（long delays）**：在路由器缓冲区中排队（queueing in router buffers）。

课件把拥塞列为网络领域"十大问题（a top-10 problem）"之一。

### 6.6.2 拥塞的原因与代价：场景 1（Scenario 1）——无穷缓冲、无重传

场景设定：

- 两个发送方、两个接收方（two senders, two receivers）。
- 一台路由器，**缓冲区无限（infinite buffers）**。
- 输出链路容量（output link capacity）为 $R$。
- **无重传（no retransmission）**。

因为缓冲区无限且无重传，所以进入网络的原始数据全部会到达，只是到达时间会被排队推迟。两个发送方共享同一条容量为 $R$ 的输出链路，因此每条连接能获得的最大吞吐量为 $R/2$。

图中记号：$\lambda_{in}$ 表示原始数据输入速率（original data），$\lambda_{out}$ 表示吞吐量（throughput）。图分两幅：

- **吞吐量与负载的关系（$\lambda_{out}$–$\lambda_{in}$ 图）**：当 $\lambda_{in} < R/2$ 时，$\lambda_{out}$ 随 $\lambda_{in}$ 线性增长，$\lambda_{out}=\lambda_{in}$；当 $\lambda_{in}=R/2$ 时达到饱和，$\lambda_{out}=R/2$；此后 $\lambda_{in}$ 再增大，$\lambda_{out}$ 保持水平 $R/2$ 不再上升。课件标注 **maximum per-connection throughput: R/2**（单条连接最大吞吐量 $R/2$）。
- **时延与负载的关系（delay–$\lambda_{in}$ 图）**：随着到达速率 $\lambda_{in}$ 逼近链路容量 $R/2$，排队时延急剧上升。课件标注 **large delays as arrival rate, $\lambda_{in}$, approaches capacity**。

场景 1 的核心结论：即使缓冲区无限、不发生任何丢包，拥塞也会以**时延增大**的形式出现。这是拥塞的"最温和"形态——吞吐量没有损失，代价全部体现为时延。

### 6.6.3 拥塞的原因与代价：场景 2（Scenario 2）——有限缓冲、有重传

场景 2 在场景 1 基础上做了两项改变：

- 路由器改为**有限缓冲（finite buffers）**；
- 发送方对**超时（timed-out）报文进行重传**（sender retransmission of timed-out packet）。

由此引入新的速率记号：

- $\lambda_{in}$：原始数据（original data）速率。
- $\lambda'_{in}$：原始数据加**重传数据**（original data, plus retransmitted data）速率，即传输层真正交给网络的输入速率。
- $\lambda_{out}$：吞吐量。

因为网络中加入了重传数据，故必有 $\lambda'_{in} \ge \lambda_{in}$。有限缓冲意味着报文可能因缓冲区满而被丢弃。

课件用三种逐步逼近现实的理想化假设，分别画出 $\lambda_{out}$–$\lambda'_{in}$ 关系曲线。

**情形 a：完美知识（idealization: perfect knowledge）**

假设发送方**只有当路由器缓冲区可用时才发送**（sender sends only when router buffers available）。此时不会发生因缓冲满而丢包，也就不需要重传，于是 $\lambda'_{in}=\lambda_{in}$，与场景 1 相同。

曲线 a：$\lambda_{out}$ 随 $\lambda'_{in}$ 线性上升，当 $\lambda'_{in}$ 达到 $R/2$ 时 $\lambda_{out}=R/2$，之后保持 $R/2$。图中另注记了 "copy" 与 **free buffer space!**（缓冲区空闲），表示报文被复制/送入时缓冲有余量。

**情形 b：已知丢失（idealization: known loss）**

假设报文**确实可能**因缓冲区满而被路由器丢弃，但发送方**只在确知某报文已丢失时才重传**（sender only resends if packet known to be lost）。

曲线 b：当 $\lambda'_{in}$ 达到 $R/2$ 时，吞吐量 $\lambda_{out}$ 只有 $R/3$。含义是：原本用于承载新数据的部分链路容量被重传的报文占用了，因此实际交付给接收方的"有效数据"低于链路容量。图注同样有 "copy"（副本）与 **free buffer space!**，说明重传的数据与原始数据在网络中同时存在；另有 **no buffer space!**（缓冲区已满）的情形，说明报文正是在缓冲耗尽处被丢弃。

**情形 c：现实情形（realistic: duplicates）**

现实中的发送方无法"确知"某报文是否丢失，只能**依赖超时**判断。当超时设置过早时，发送方会在原报文其实已经送达的情况下**过早超时（times out prematurely）**，于是**发送两份副本，两份都被交付**（sending two copies, both of which are delivered）。

曲线 c：当 $\lambda'_{in}$ 达到 $R/2$ 时，吞吐量 $\lambda_{out}$ 只有 $R/4$。因为每一份被重复发送又都成功交付的数据，额外占用了一份链路容量，所以有效吞吐进一步下降到 $R/4$。

三种情形在 $\lambda'_{in}=R/2$ 处的吞吐量对比：

| 情形 | 假设 | $\lambda'_{in}=R/2$ 处的 $\lambda_{out}$ |
|------|------|------------------------------------------|
| a | 完美知识：缓冲可用才发送，无丢包 | $R/2$ |
| b | 已知丢失：只重传确知丢失的报文 | $R/3$ |
| c | 现实：过早超时，重复副本也被交付 | $R/4$ |

**场景 2 总结出的"代价"（"costs" of congestion）**：

- **排队时延（queuing delays）**；
- **为补偿丢包而付出的额外工作**（more work / retrans to compensate for lost packets）；
- **不必要的重传（unneeded retransmissions）**：链路承载了同一报文的多份副本（link carries multiple copies of pkt），导致**有效吞吐（goodput）下降**。

### 6.6.4 拥塞的原因与代价：场景 3（Scenario 3）——多跳路径与拥塞崩溃

场景 3 进一步逼近真实网络：

- **四个发送方**（four senders）；
- **多跳路径**（multihop paths）：每个报文要经过多台路由器；
- **超时/重传**（timeout/retransmit）。

课件提问：**当 $\lambda_{in}$ 与 $\lambda'_{in}$ 增大时会发生什么？** 并给出回答：**当"红 $\lambda'_{in}$"（即多跳路径上的重传负载）增大时，到达上层队列的所有"蓝报文"都被丢弃，蓝流吞吐量趋近于 0**（as red $\lambda'_{in}$ increases, all arriving blue pkts at upper queue are dropped, blue throughput → 0）。

含义是：在多跳路径中，一个报文可能在**沿途的某一跳**被丢弃，而它此前已经消耗了前面若干跳的传输能力。当上游发送方为了弥补丢失而不断重传、$\lambda'_{in}$ 持续增大时，这些重传报文会把共享缓冲占满，从而挤掉其他连接的报文。于是**一条连接吞吐量的提升以另一条连接吞吐量归零为代价**。

$\lambda_{out}$ 随 $\lambda'_{in}$ 变化的曲线是：曲线先上升，在某处达到峰值，随后**急剧下降并趋近于 0**；横轴上标出 $R/2$。这就是**拥塞崩溃（congestion collapse）**：负载越大，网络实际交付的吞吐量反而越低。

据此得到场景 3 总结的**另一项拥塞"代价"**：

- **当报文被丢弃时，此前为它已经消耗的"上游传输能力"全部被浪费**（when packet dropped, any "upstream transmission capacity used for that packet was wasted!）。

这一点与场景 2 的"重复副本占用容量"不同：场景 2 浪费的是同一条链路上的重复传输，场景 3 浪费的是报文在到达丢弃点之前沿途各跳所消耗的传输能力。

> 补充说明（非课件内容）：源图用颜色区分不同连接的数据流（"红 $\lambda'_{in}$"、"蓝报文"），上述文字按源图标注原样保留颜色词，仅用于对应图中的流，不代表需要记忆颜色信息。

## 6.7 TCP 拥塞控制（TCP Congestion Control）

6.6 节以三种场景（无限缓存、有限缓存下重传、多跳路径下的上游带宽浪费）说明了拥塞的产生机制与代价。本节把拥塞控制落到 Internet 的实际实现上，处理 TCP 如何根据网络中观察到的拥塞程度动态调整发送速率。

### 6.7.1 加性增、乘性减（Additive Increase Multiplicative Decrease，AIMD）

TCP 拥塞控制的基本做法是：**发送方不断增加发送速率（即增大窗口尺寸），以此探测网络可用的带宽，直到发生丢包（loss）为止。**

- **加性增（additive increase）**：在未检测到丢包期间，每经过一个 RTT，把拥塞窗口 `cwnd` 增加 1 MSS。
- **乘性减（multiplicative decrease）**：一旦发生丢包，把 `cwnd` 减半。

其中 `cwnd`（congestion window）指 **TCP 发送方的拥塞窗口尺寸**，即发送方依据自身对网络拥塞程度的感知而允许自己处于未确认状态的字节数上限，单位是字节（或按 MSS 计量的报文段数）。

由于"缓慢线性上升、遇丢包后骤然减半、再缓慢线性上升"交替出现，`cwnd` 随时间的变化曲线呈锯齿形（saw tooth）。课件把这种形状称为 **AIMD 锯齿行为（AIMD saw tooth behavior）**，其含义是**探测带宽**——先加性地增大窗口尺寸，直到发生丢包，再把窗口减半（"additively increase window size … until loss occurs (then cut window in half)"）。源图横轴为时间（time），纵轴为 TCP 发送方拥塞窗口尺寸（`cwnd`: TCP sender congestion window size），锯齿的每个上升段斜率恒定、下降段为垂直跌落一半。

需要区分本节与 6.5 节的流控：6.5 节的接收窗口（`rwnd`）由**接收方**的空闲缓存决定，防止发送方压垮接收方；这里的 `cwnd` 由**发送方**根据网络拥塞的感知确定，防止发送方压垮网络。两者共同约束发送方的可发送数据量。

### 6.7.2 TCP 拥塞控制细节：发送限制与发送速率

**（1）发送方的发送限制**

TCP 发送方通过下式限制在途数据量：

$$\text{LastByteSent}-\text{LastByteAcked}\le \texttt{cwnd}$$

- $\text{LastByteAcked}$：已被对端确认的最后一个字节的序号；
- $\text{LastByteSent}$：已经发出的最后一个字节的序号；
- 两者之差即"已发送但尚未被确认"的字节数，也就是在途（in-flight）字节数；
- $\texttt{cwnd}$：拥塞窗口，其取值是**动态的**（dynamic），是感知到的网络拥塞程度的函数（function of perceived network congestion）。

原图中，已确认区之后的黄色部分是已发送但未确认的数据；蓝色部分位于 `last byte sent` 之后、仍在 `cwnd` 框内，表示窗口内尚可发送的数据；更右侧灰色部分才在拥塞窗口之外。`cwnd` 限制的是在途数据上限，并不表示在途数据始终恰好填满窗口。考虑流量控制时，还须满足在途字节数不超过 `min(cwnd,rwnd)`。

**（2）TCP 发送速率**

课件给出的近似关系是：发送方**大致每发送 `cwnd` 字节的数据，就等待一个 RTT 以接收相应的 ACK，然后继续发送更多字节**（roughly: send cwnd bytes, wait RTT for ACKs, then send more bytes）。由此得到

$$\text{rate}\approx\frac{\texttt{cwnd}}{\text{RTT}}\quad \text{bytes/sec}$$

即发送速率约等于拥塞窗口除以往返时延，单位是字节/秒。该近似用于发送方持续有数据、接收窗口和其他条件不额外限制发送的情形。在这些假设和 RTT 固定时，增大 `cwnd` 会提高可达到的发送速率；实际速率还可能受应用供数、接收窗口、链路容量等因素限制。把该式两边乘以 RTT 并除以 MSS，也可以把速率换算成以报文段数表示的窗口尺寸。

### 6.7.3 TCP 慢启动（Slow Start）

**在课件采用的初始窗口为 1 MSS 的教学模型中，连接开始后进行慢启动，窗口近似每 RTT 加倍；达到 `ssthresh` 时转入拥塞避免，发生丢包时则按相应规则调整。**

具体机制：

- 初始时 $\texttt{cwnd}=1\ \text{MSS}$；
- 每经过一个 RTT 把 `cwnd` 加倍（double cwnd every RTT）；
- 加倍是通过"**每收到一个 ACK 就把 `cwnd` 增加 1 MSS**"实现的。

最后一条是该机制能够实现指数增长的原因：设某一轮发送方发出了 $k$ 个报文段，则在一个 RTT 内会收到 $k$ 个 ACK，每个 ACK 使 `cwnd` 增加 1 MSS，于是 `cwnd` 增加 $k$ 个 MSS，即由 $k$ 变为 $2k$——窗口尺寸在每个 RTT 内翻倍，故发送速率随 RTT 数呈指数增长。

课件对慢启动的总结是：**起始速率较低，但会以指数速度迅速攀升**（initial rate is slow but ramps up exponentially fast）。

Host A 与 Host B 之间的时序图中，纵轴向下为时间（time），左侧用双箭头标注一个 RTT。图中依次画出：第一个 RTT 内 A 向 B 发送 one segment；第二个 RTT 内发送 two segments；第三个 RTT 内发送 four segments——即每个 RTT 内可发送的报文段数目按 1、2、4 递增，直观对应"每 RTT 加倍"。

名称"慢启动"并不是指增长慢，而是指起点低（`cwnd` 只有 1 MSS）；增长本身是指数的。

### 6.7.4 丢包的检测与反应；从慢启动切换到拥塞避免

TCP 通过两种信号判断发生了丢包，两种信号引发不同的反应。

**（1）由超时（timeout）指示的丢包**

- 把 `cwnd` 置为 1 MSS；
- 此后窗口先按慢启动方式指数增长到门限值（threshold），再转为线性增长。

**（2）由 3 个重复 ACK（3 duplicate ACKs）指示的丢包：TCP RENO**

- 重复 ACK 说明网络仍有能力交付部分报文段（dup ACKs indicate network capable of delivering some segments）；
- `cwnd` 减半，随后窗口线性增长。

**（3）TCP Tahoe 的做法**

TCP Tahoe 无论在超时还是 3 个重复 ACK 的情况下，**一律把 `cwnd` 置为 1**。

两种实现的差别在于：只要出现三个重复 ACK，就说明该连接上仍有报文段成功到达接收方，网络并未完全阻断；因此 Reno 不必退回到 `cwnd = 1`，而是从减半后的窗口继续线性增长，避免速率从最低点重新爬升。Tahoe 不做这种区分。

**（4）从慢启动切换到拥塞避免的时机（switching from slow start to CA）**

- **Q**：指数增长应当在何时切换为线性增长？
- **A**：当 `cwnd` 达到**发生超时前其取值的一半**时。

实现方式：

- 设置变量 `ssthresh`（slow start threshold，慢启动门限）；
- 一旦发生丢包事件，就把 `ssthresh` 置为**丢包事件发生前 `cwnd` 取值的一半**。

于是控制流程为：连接开始时 `cwnd = 1 MSS`，按慢启动指数增长；当 `cwnd ≥ ssthresh` 时切换到拥塞避免（congestion avoidance，CA）阶段，改为每 RTT 加 1 MSS 的线性增长；一旦丢包，重新计算 `ssthresh`，并依据丢包信号类型决定新的 `cwnd`。（课件给出在线交互练习链接 `http://gaia.cs.umass.edu/kurose_ross/interactive/`，用于观察该过程的更多实例。）

**`cwnd` 随传输轮次变化的曲线读数（课件 6-106）**

原图第 1—8 轮为 $1,2,4,8,9,10,11,12$ MSS，首个门限为 8 MSS。第 8 轮窗口为 12 MSS，丢包后的门限为 $12/2=6$ MSS。第 9—15 轮两条曲线的读数为：

| 轮次 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|
| Tahoe | 1 | 2 | 4 | 6 | 7 | 8 | 9 |
| Reno | 6 | 7 | 8 | 9 | 10 | 11 | 12 |

**判读条件**：Reno 保持减半窗口而 Tahoe 回到 1 MSS 的对比，对应三次重复 ACK 触发丢包反应的教学示意；若发生的是超时，Reno 也会回到 1 MSS，不能把原图解释成“Reno 超时后仍从 6 MSS 继续”。课件左侧有关超时前窗口一半的文字说明的是门限如何确定，应与曲线所体现的两种丢包反应分别理解。

### 6.7.5 TCP 拥塞控制状态机总结

课件把 TCP 拥塞控制归纳为一个含三个状态的状态机：**慢启动（slow start）**、**拥塞避免（congestion avoidance）**、**快速恢复（fast recovery）**。初始由左侧进入慢启动，初始参数标注为 `cwnd = 1 MSS`、`ssthresh = 64 KB`、`dupACKcount = 0`。全部转移及其动作如下表所列（表中动作顺序与源图一致）。

| 当前状态 | 触发事件 | 执行动作 | 转移到 |
|---|---|---|---|
| 慢启动 | 新 ACK（New ACK） | `cwnd = cwnd + MSS`；`dupACKcount = 0`；按允许发送新报文段 | 慢启动（自环） |
| 慢启动 | 重复 ACK | `dupACKcount++` | 慢启动（自环） |
| 慢启动 | 超时（timeout） | `ssthresh = cwnd/2`；`cwnd = 1 MSS`；`dupACKcount = 0`；重传丢失的报文段 | 慢启动（自环） |
| 慢启动 | `cwnd ≥ ssthresh` | （图中无附加动作） | 拥塞避免 |
| 慢启动 | `dupACKcount == 3` | `ssthresh = cwnd/2`；`cwnd = ssthresh + 3`；重传丢失的报文段 | 快速恢复 |
| 拥塞避免 | 新 ACK | `cwnd = cwnd + MSS·(MSS/cwnd)`；`dupACKcount = 0`；按允许发送新报文段 | 拥塞避免（自环） |
| 拥塞避免 | 重复 ACK | `dupACKcount++` | 拥塞避免（自环） |
| 拥塞避免 | 超时 | `ssthresh = cwnd/2`；`cwnd = 1 MSS`；`dupACKcount = 0`；重传丢失的报文段 | 慢启动 |
| 拥塞避免 | `dupACKcount == 3` | `ssthresh = cwnd/2`；`cwnd = ssthresh + 3`；重传丢失的报文段 | 快速恢复 |
| 快速恢复 | 重复 ACK | `cwnd = cwnd + MSS`；按允许发送新报文段 | 快速恢复（自环） |
| 快速恢复 | 新 ACK | `cwnd = ssthresh`；`dupACKcount = 0` | 拥塞避免 |
| 快速恢复 | 超时 | `ssthresh = cwnd/2`；`cwnd = 1 MSS`；`dupACKcount = 0`；重传丢失的报文段 | 慢启动 |

对该状态机的说明：

- 拥塞避免状态下每收到一个新 ACK 的窗口增量为 $\text{MSS}\cdot(\text{MSS}/\texttt{cwnd})$ 字节。一个 RTT 内收到的 ACK 数约为 $\texttt{cwnd}/\text{MSS}$，故一个 RTT 的累计增量为 $\text{MSS}$，这正是 6.7.1 节"每 RTT 增加 1 MSS"的加性增；写成 `MSS·(MSS/cwnd)` 是为了在逐 ACK 处理时把每 RTT 的提升量摊到各个 ACK 上。
- `dupACKcount` 在每收到一个新 ACK 时清零，只对连续到达的重复 ACK 计数；达到 3 时判定报文段丢失并进入快速恢复。
- 进入快速恢复时 `cwnd = ssthresh + 3`，即"减半后再补偿 3 个 MSS"，对应已经离开网络、到达接收方并触发那 3 个重复 ACK 的 3 个报文段。
- 从快速恢复收到新 ACK（确认了重传的报文段）后 `cwnd = ssthresh`，回到拥塞避免，而不是回到慢启动。
- 三个状态中的任何一个遇到超时，都回到慢启动并把 `cwnd` 置 1 MSS，同时更新 `ssthresh`。

### 6.7.6 TCP 吞吐量（TCP Throughput）

课件讨论的问题是：**平均 TCP 吞吐量作为窗口尺寸与 RTT 的函数是什么？** 推导基于两条简化假设：**忽略慢启动阶段；假定发送方始终有数据可发。**

设 $W$ 为**发生丢包时的窗口尺寸**，以字节为单位。则：

- 平均窗口尺寸（平均在途字节数）是 $\dfrac{3}{4}W$；
- 平均吞吐量是每个 RTT $\dfrac{3}{4}W$ 字节。

写成公式即

$$\text{avg TCP throughput}=\frac{3}{4}\cdot\frac{W}{\text{RTT}}\quad \text{bytes/sec}$$

**补充推导（课件未给出，此处按上述假设补全）：** 忽略慢启动时，窗口在一个锯齿周期内从 $W/2$ 线性增长到 $W$，且在两值之间均匀分布，故时间平均值为

$$\overline{W}=\frac{W/2+W}{2}=\frac{3W}{4}$$

再由 6.7.2 节的 $\text{rate}\approx\texttt{cwnd}/\text{RTT}$，把 `cwnd` 换成时间平均窗口 $\overline{W}=3W/4$，即得上式。源图下方的锯齿图纵轴标出 $W$ 与 $W/2$ 两个刻度，横轴为时间，锯齿在 $W/2$ 与 $W$ 之间往复，与该推导一致。

### 6.7.7 长肥管道上的 TCP（TCP Futures: TCP over "long, fat pipes"）

#### 算例：1500 字节报文段、100 ms RTT、10 Gbps 吞吐量

课件给出的算例是：**报文段长度 1500 字节，RTT 为 100 ms，要求达到 10 Gbps 的吞吐量**，则需要的平均在途报文段数 $\overline{W}=83\,333$ 个。

**补充推导（课件只给出 83 333 这一结果，未展示代入过程，以下为按定义补全）：** 平均在途报文段数等于"一个 RTT 内能够发送出去的报文段数"，即

$$\overline{W}=\frac{\text{吞吐量}\times \text{RTT}}{\text{MSS}}=\frac{10\times10^{9}\ \text{bit/s}\times 0.1\ \text{s}}{1500\times 8\ \text{bit}}=\frac{10^{9}}{1.2\times10^{4}}=83\,333.3\approx 83\,333$$

其中 MSS 以比特计为 $1500\times 8=12\,000$ bit，RTT 以秒计为 0.1 s。校验：$83\,333\times12\,000\ \text{bit}\div0.1\ \text{s}=9.99996\times10^{9}\ \text{bit/s}\approx10\ \text{Gbps}$，与题设要求的 10 Gbps 相符。

按 6.7.6 节的平均窗口关系 $\overline{W}=\dfrac{3}{4}W$，发生丢包时的窗口为

$$W=\frac{4}{3}\times 83\,333=111\,110.7\approx 111\,111\ \text{个报文段}$$

换算成字节为 $83\,333\times1500\ \text{B}=1.25\times10^{8}\ \text{B}=125\ \text{MB}$ 的平均在途字节数，对应丢包时的窗口 $W=1.6667\times10^{8}\ \text{B}\approx166.7\ \text{MB}$。上述字节换算与 $W$ 的求取为补充推导，课件未列出。

**吞吐量与报文段丢失概率的关系（Mathis 1997）**：

$$\text{TCP throughput}=\frac{1.22\cdot \text{MSS}}{\text{RTT}\cdot\sqrt{L}}$$

- $\text{MSS}$：最大报文段长度，单位字节或比特（代入时需与 RTT、吞吐量单位保持一致）；
- $\text{RTT}$：往返时延，单位秒；
- $L$：报文段丢失概率（segment loss probability），无量纲。

**要达到 10 Gbps 吞吐量，需要丢包率 $L=2\times10^{-10}$——这是一个极小的丢包率**（a very small loss rate）。课件强调这一点，用以说明传统 TCP 在长肥管道（high bandwidth-delay product 的链路）上难以跑满带宽。

**补充推导（课件只给出 $L=2\times10^{-10}$ 这一结果，以下为按 Mathis 公式反解并校验）：** 把 $10\ \text{Gbps}=10^{10}$ bit/s、$\text{MSS}=12\,000$ bit、$\text{RTT}=0.1$ s 代入并解出 $\sqrt{L}$：

$$\sqrt{L}=\frac{1.22\cdot \text{MSS}}{\text{RTT}\cdot\text{throughput}}=\frac{1.22\times12\,000}{0.1\times10^{10}}=\frac{14\,640}{10^{9}}=1.464\times10^{-5}$$

$$L=(1.464\times10^{-5})^{2}=2.143\times10^{-10}\approx 2\times10^{-10}$$

用原数据校验：$\dfrac{1.22\times12\,000}{0.1\times\sqrt{2.143\times10^{-10}}}=\dfrac{14\,640}{0.1\times1.4644\times10^{-5}}=\dfrac{14\,640}{1.4644\times10^{-6}}=9.997\times10^{9}\ \text{bit/s}\approx10\ \text{Gbps}$，与题设目标一致。

课件最后指出：正因如此，出现了**面向高速网络的新版本 TCP**（new versions of TCP for high-speed）。

### 6.7.8 TCP 公平性（TCP Fairness）

#### 6.7.8.1 公平性目标

**公平性目标（fairness goal）：若 $K$ 条 TCP 连接共享同一条带宽为 $R$ 的瓶颈链路，则每条连接应当获得 $R/K$ 的平均速率。**

拓扑为：两条 TCP 连接（TCP connection 1、TCP connection 2）各自从一台主机出发，汇聚到标有 "bottleneck router capacity R" 的瓶颈路由器，再经后续路由器转发到同一方向。

#### 6.7.8.2 TCP 为什么是公平的

考虑两条相互竞争的连接。课件给出的理由有两条：

- **加性增使吞吐量的增长斜率为 1**：加性增意味着每条连接在一个 RTT 内各自增加相同的窗口量，因此在"连接 1 吞吐量—连接 2 吞吐量"平面上，两连接速率之和增加的轨迹沿 45° 方向推进（在坐标系中斜率为 1）；
- **乘性减按比例地降低吞吐量**：丢包时每条连接把窗口减半，即吞吐量按同一比例下降，因此该操作把两连接的速率点沿"经过原点的直线"方向拉向原点。

源图的横轴为 Connection 1 throughput，纵轴为 Connection 2 throughput，两者刻度均标到 $R$；从原点出发的 45° 虚线标注为 "equal bandwidth share（等带宽份额）"，另一条连接 $(\text{Connection 1 throughput})=R$ 与 $(\text{Connection 2 throughput})=R$ 两点的斜率为 $-1$ 的实线表示链路总容量约束（即两连接吞吐量之和为 $R$）。箭头表示两连接速率点的运动：加性增沿 45° 斜线方向向右上推进，丢包后乘性减按比例回退，箭头序列逐步收敛到 45° 虚线与容量约束线的交点，即两连接各得 $R/2$ 的点。图中标注的运动序列为"loss: decrease window by factor of 2 → congestion avoidance: additive increase → loss: decrease window by factor of 2 → congestion avoidance: additive increase"。

把上述两点合并，即得到结论：AIMD 的迭代过程使两连接的速率点收敛到等带宽份额线上，因此 TCP 在"两条连接竞争同一瓶颈链路"的情形下趋于公平。

#### 6.7.8.3 公平性与 UDP

多媒体应用往往不使用 TCP，因为**不希望自己的速率被拥塞控制所限**（do not want rate throttled by congestion control）；它们改用 UDP：**以恒定速率发送音频/视频，并容忍丢包**（send audio/video at constant rate, tolerate packet loss）。因此这类 UDP 流不参与上述 AIMD 的调节，会对 TCP 流的公平性造成影响。

#### 6.7.8.4 公平性与并行 TCP 连接

应用可以在两台主机之间**打开多条并行的连接**；网页浏览器就是这样做的。课件举例：**某链路速率为 $R$，已有 9 条连接存在**，则

- 新应用只请求 1 条 TCP 连接时，得到速率 $R/10$；
- 新应用请求 11 条 TCP 连接时，得到速率 $R/2$。

**补充说明（单位与近似）：** 第二种情形下链路中共有 $9+11=20$ 条连接，每条按公平份额得 $R/20$，新应用合计获得 $11\times R/20=0.55R$；课件写为 $R/2$，是把 $0.55R$ 近似表述为约一半链路带宽。第一种情形为 $1\times R/10=0.1R=R/10$，与课件一致。该例说明：**多开并行连接的应用可以从共享链路中获取远高于单条连接公平份额的带宽**，因而公平性是相对于"连接"而言而不是相对于"应用"而言的。

### 6.7.9 显式拥塞通知（Explicit Congestion Notification，ECN）

前面各节的控制方式由端系统依据超时与重复 ACK 推断拥塞，属于端到端（隐式）方式；ECN 属于**网络辅助的拥塞控制（network-assisted congestion control）**：

- **IP 数据报首部（ToS 字段）中的两个比特由网络路由器标记，用以指示拥塞**（two bits in IP datagram header (ToS field) marked by network router to indicate congestion）；
- 该拥塞指示随数据报**被携带到接收主机**（congestion indication carried to receiving host）；
- **接收方在 IP 数据报中看到拥塞指示后，在接收方到发送方的 ACK 报文段上置 ECE（ECN Echo，ECN 回显）比特**，以此把拥塞情况通知发送方。

源图的图示分层给出全过程：

- 左侧为源（source）主机，协议栈自下而上为 physical、link、network、transport、application；
- 源发出的 IP 数据报进入网络前标记为 `ECN=00`；
- 数据报经过网络中一台路由器时，该路由器将其标记为 `ECN=11`，表明途中发生了拥塞；
- 数据报到达右侧目的（destination）主机的 network 层，其协议栈同样为 physical、link、network、transport、application；
- 目的主机返回的 TCP ACK 报文段上带有 `ECE=1`，该 ACK 沿反向路径回到源主机。

**补充说明（字段位置）：** 在 IPv4 首部中，课件所称的 ToS 字段为 8 比特；该字段后来被划分为 6 比特的 DSCP 与 2 比特的 ECN，ECN 使用的正是这 2 个比特，因此图中数据报上的 `ECN=00`、`ECN=11` 分别表示"未经历拥塞"与"经历拥塞（Congestion Experienced）"两种取值。此段为对课件图示取值的补充解释，课件本身只说明"ToS 字段中的两个比特"。

ECN 与 6.7.4 节两种丢包信号的关系是：超时与重复 ACK 都是丢包**已经发生**之后才被发送方察觉；ECN 使路由器可以在缓冲区尚未溢出、报文段尚未被丢弃时就发出拥塞提示，接收方再通过 ECE 通知发送方，因而发送方可以在丢包前就降低速率。

### 6.7.10 本章小结（Chapter 6: Summary）

**（1）传输层服务背后的原理（principles behind transport layer services）**

- 多路复用与多路分解（multiplexing, demultiplexing）——6.2 节；
- 可靠数据传输（reliable data transfer）——6.4 节（原理）与 6.5 节（TCP 中的实现）；
- 流控（flow control）——6.5 节；
- 拥塞控制（congestion control）——6.6 节（原理）与 6.7 节（TCP 中的实现）。

**（2）在 Internet 中的实例化与实现（instantiation, implementation in the Internet）**

- UDP——6.3 节（无连接传输）；
- TCP——6.5 节（面向连接的传输）。

**（3）后续内容（next）**

- 离开网络的"边缘"（leaving the network "edge"），即前面已讲完的应用层与传输层；
- 进入网络的"核心"（into the network "core"）。

本章课件至此结束于第 114 页；接下来的讲解范围是网络核心部分，不属于本章。
