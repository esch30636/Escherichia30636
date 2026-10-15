# 计算机网络 —— 第1章 绪论（Chapter 1: Introduction）

> 原始 PDF：`D:\Escherichia30636\计算机网络\Chapter_1_2.pdf`
> PDF 总页数：36 页
> 整理日期：2026-10-15

本笔记覆盖该 PDF 的 36 页，对应 Chapter 1（Introduction）的后半部分：网络核心（network core）、性能（performance）与网络安全（network security）。按课件原有的章—节组织连续讲解，保留课件页脚标注的原始页序（`Introduction: 1-33` … `Introduction: 1-68`）；课件正文只用页脚标记页序、不含小节编号，因此大节编号沿用课件 Chapter 1 roadmap 中的条目序号，其下小节编号为组织连续讲解而补充。

---

## 1.4 网络核心：分组交换、电路交换与 Internet 结构

网络核心指互连路由器构成的网络以及其中采用的数据交换方式。本节按课件顺序讲授：分组交换的存储转发机制、分组交换中的排队与丢包、电路交换及其复用方式 FDM/TDM、两种交换方式的定量对比与定性取舍，最后是 Internet“网络的网络”结构如何由若干互连方案逐步得到。

### 1.4.1 分组交换：存储转发（Packet Switching: Store-and-Forward）

在分组交换网络中，源主机把要发送的数据划分为**分组（packet）**，每个分组的长度为 $L$ 比特（bit）。分组从源主机出发，经过若干段**链路（link）**与中间的**分组交换机／路由器（router）**到达目的主机。每段链路具有一个**链路传输速率（link transmission rate）**$R$，单位为比特每秒（bps，即 bit/s）。

**传输时延（packet transmission delay）**是把一个 $L$ 比特的分组推上（push out）一条速率为 $R$ bps 的链路所需的耗时。其依据是：推完整个分组共需向链路推入 $L$ 比特，而链路每秒能推入 $R$ 比特，故所需时间为

$$d_{\text{trans}} = \frac{L}{R}$$

式中 $L$ 为分组长度，单位 bit；$R$ 为链路传输速率，单位 bps；$d_{\text{trans}}$ 的单位为秒（s）。课件把这一时延写作 *packet transmission delay: takes $L/R$ seconds to transmit (push out) $L$-bit packet into link at $R$ bps*。

$d_{\text{trans}}$ 是把比特从主机或路由器推上链路的耗时，它只取决于分组长度与链路速率这两个量，与两端之间的距离无关。与之相对的**传播时延**（比特在物理介质中前进的耗时）在同一章稍后给出公式，两者的区别也在那里说明。

**存储转发（store and forward）**是分组交换转发方式的定义：一个分组必须**整个到达**路由器之后，才能在下一段链路上被传输（*store and forward: entire packet must arrive at router before it can be transmitted on next link*）。路由器不能“边收边发”，必须先完整接收并存储该分组，再从输出链路把它完整推出。因此，对同一个采用存储转发方式处理的分组，中间路由器先完整接收，再开始通过输出链路发送。这里的先后限制针对该分组在路由器处的接收与转发，不表示链路上的发送时延与传播时延不能重叠。

**【源图，课件页 1-33】** 左侧为源主机（source），其右侧画有等待发送的分组队列，队列中的三个分组自左向右标号为 3、2、1，1 号位于最靠近链路的位置，即最先被发送；队列左侧标注 *L bits per packet*，另有一个虚线框分组位于队列上方。源主机与中间一台路由器（圆柱形交换机符号）之间、该路由器与右侧目的主机（destination）之间各为一条标注 *R bps* 的链路。图中用带有分组的虚线框标出当前正在被推上链路的那个分组。该图用于说明“同一分组依次经过多段链路”的过程。

#### 例题 1-1：一跳（one-hop）传输时延（课件页 1-33）

**题干**（课件原文）：*One-hop numerical example:* $L = 10$ Kbits；$R = 100$ Mbps；求一跳的传输时延（one-hop transmission delay）。

**解**

第 1 步：统一长度单位。课件按 $1\ \text{Kbit} = 1000\ \text{bit}$ 计算，故

$$L = 10\ \text{Kbit} = 10 \times 10^{3}\ \text{bit} = 10^{4}\ \text{bit}$$

第 2 步：统一速率单位。

$$R = 100\ \text{Mbps} = 100 \times 10^{6}\ \text{bit/s} = 10^{8}\ \text{bit/s}$$

第 3 步：代入传输时延公式 $d_{\text{trans}} = L/R$：

$$d_{\text{trans}} = \frac{L}{R} = \frac{10^{4}\ \text{bit}}{10^{8}\ \text{bit/s}} = 10^{-4}\ \text{s}$$

第 4 步：把秒换算为毫秒（$1\ \text{s} = 10^{3}\ \text{ms}$）：

$$d_{\text{trans}} = 10^{-4} \times 10^{3}\ \text{ms} = 0.1\ \text{ms}$$

**答案**：一跳传输时延 $d_{\text{trans}} = 0.1\ \text{ms}$（$10^{-4}$ s），与课件给出的 *one-hop transmission delay = 0.1 msec* 一致。

**用原数据校验**：把 $0.1\ \text{ms}$ 与题给的 $R = 100$ Mbps 相乘，看链路在这段时间内能推出的比特数是否为原题给定的 $L$：

$$d_{\text{trans}} \times R = 0.1 \times 10^{-3}\ \text{s} \times 100 \times 10^{6}\ \text{bit/s} = 10^{-4}\ \text{s} \times 10^{8}\ \text{bit/s} = 10^{4}\ \text{bit} = 10\ \text{Kbit} = L$$

校验值与分组长度 $L$ 完全相等，结果正确。

**【补充推演】** 由存储转发的定义可以直接推出多段链路的情形：若源到目的之间共有 $N$ 段速率同为 $R$ 的链路（中间经过 $N-1$ 台路由器），且暂不考虑处理时延、排队时延与传播时延，则同一分组在每一段链路上都要完整地经历一次“完整到达后再完整发出”，各段的传输时延均为 $L/R$，总传输时延为 $N \cdot L/R$。取 $N = 3$、代入例题 1-1 的同一组数据，可得 $3 \times 0.1\ \text{ms} = 0.3\ \text{ms}$。此推演不是课件原例题，仅用于说明“存储转发”在链数增加时的直接后果。另需注意，当源端连续发送多个分组时，各分组在相邻链路上的传输在时间上可以部分重叠（前一个分组已被路由器完整收下并开始在下一段链路上推出时，后一个分组正好到达该路由器），因此 $M$ 个分组走完 $N$ 段链路的总时间不是 $M \cdot N \cdot L/R$。

### 1.4.2 分组交换：排队与丢包（Queueing and Loss）

分组交换的核心机制除了存储转发，还有**排队（queueing）**。课件的判断是：当“工作”到达的速度快于它被处理（服务）的速度时，就发生排队（*Queueing occurs when work arrives faster than it can be serviced*）。这里的“工作”是到达路由器、需要从某条输出链路发送出去的分组，服务速度就是该输出链路的传输速率。

**【源图，课件页 1-34、1-35】** 两页使用同一张网络图：左侧为主机 A 与 B，它们各自经一条接入链路连到同一台路由器，A 的接入链路标注 *R = 100 Mb/s*，B 一侧的接入链路上未标注数值；该路由器的输出链路标注 *R = 1.5 Mb/s*，连向第二台路由器；第二台路由器再向下连第三台路由器，并分别连到主机 C、D、E。第一台路由器的输出端口处用引线指出 *queue of packets waiting for transmission over output link*（等待在输出链路上传输的分组队列），队列内画有多个彩色小方块表示排队的各个分组，输出链路上也画有若干正在被传输的分组方块。

课件页 1-34 页面下方另有三张照片配图：排满车辆等候的停车场、排成一列等候的人群、街道上依次排队的公交车。这三张照片是课件为“排队”这一现象配的直观图片，不含任何技术参数。该页除标题、这张网络图与上述判据句之外没有其他文字。

课件页 1-35 在同一张网络图下给出结论段 *Packet queuing and loss*：如果在一段时间内，到达链路的速率（单位 bps）超过链路的传输速率（单位 bps），那么

- 分组将排队，等待在输出链路上被传输；
- 若路由器中用于存放排队分组的存储器（缓冲区，buffer）被填满，分组就可能被丢弃（dropped，即丢失，lost）。

用图中已经标注的两个速率数据，可以直接算出队列增长的数量来源。接入链路的到达速率为 $R_{\text{in}} = 100$ Mb/s，输出链路的传输速率为 $R_{\text{out}} = 1.5$ Mb/s，两者之差为

$$R_{\text{in}} - R_{\text{out}} = 100\ \text{Mb/s} - 1.5\ \text{Mb/s} = 98.5\ \text{Mb/s}$$

也就是说，若 A 以接入链路速率持续发送，则每秒有 $98.5$ Mb 的比特到达、却无法在当秒从输出链路发出，这部分只能留在路由器的缓冲区中，使队列长度以每秒 $98.5$ Mb 的量持续增长；缓冲区容量有限，一旦队列占满全部缓冲区，其后到达的分组只能被丢弃（对应 1-35 页结论段的第二条）。这张图上只标注了 A 一侧接入链路的速率 $R = 100$ Mb/s，B 一侧的接入链路上没有标注数值，因此对 B 只能说明其机制相同，不能代入具体数值；若 A、B 同时以同速率发送，则按同样的“到达速率减输出速率”方式逐项相加，差额会更大。

排队与丢包是分组交换相对电路交换的主要代价，两者的对比在本节 1.4.5 小节给出；课件页 1-50 还有一张图从“性能”角度重复说明这一机制。

### 1.4.3 电路交换（Circuit Switching）

课件把电路交换定位为分组交换的**替代方案（alternative to packet switching）**。

**资源分配方式**：端到端资源被分配给并保留给源到目的之间的“呼叫”（*end-end resources allocated to, reserved for "call" between source and destination*）。在一次呼叫的整个期间，端到端路径上的资源被分配给该呼叫并为其保留。这些资源专属于该呼叫，其他呼叫不能使用，即专用资源、不共享（*dedicated resources: no sharing*）。由此带来的直接结果是：该呼叫获得**电路式的（circuit-like）、可保证的（guaranteed）性能**——一旦呼叫建立成功，沿途的传输能力就确定地属于这次呼叫；反之，若某段电路未被该呼叫使用，它就处于空闲（idle）状态，而由于不允许共享，这段空闲资源也不会被其他呼叫占用（*circuit segment idle if not used by call (no sharing)*）。

课件同时指出，这种交换方式传统上用于**电话网（traditional telephone networks）**。课件在本页脚注给出补充链接：*Check out the online interactive exercises for more examples: http://gaia.cs.umass.edu/kurose_ross/interactive*。

**【源图，课件页 1-36】** 图右侧为 4 台路由器（圆柱形交换机符号）排成方形拓扑，上边与下边各是一条横向链路、左边与右边各是一条纵向链路，每条链路都并排画出 **4 条电路**（4 条平行细线）；路由器上还有向上的引出线连接到各自的主机。图中可见主机位置为左上、右上与右下三处。图中用一条红色粗线标出一次呼叫所走的路径：从左上主机向下进入左上路由器，沿**上方链路**行进，进入右上路由器，再沿**右侧链路**向下，进入右下路由器后继续向下到达右下主机。按课件文字，这次呼叫占用的是**上方链路的第 2 条电路**和**右侧链路的第 1 条电路**；同一时段内其余各条电路未被这次呼叫使用，也不被任何其他呼叫使用。

由此可以归纳出电路交换相对分组交换的两个结构性差别：其一，通信前必须先建立呼叫、沿途预留资源，因此存在呼叫建立过程；其二，只要呼叫存在，被占用的资源就不会被其他通信共享，即使该呼叫暂时没有数据要发送（电路段空闲），这部分资源也不释放。

### 1.4.4 电路交换的复用方式：频分复用与时分复用（FDM and TDM）

电路交换的一条链路上要同时承载多个呼叫，就需要复用（multiplexing）。课件给出两种方式。

**频分复用（Frequency Division Multiplexing，FDM）**：把光、电磁的频率划分为若干个（窄）频带，每个呼叫分配自己的一个频带，在该频带上能够以其最大速率发送。课件原文：*optical, electromagnetic frequencies divided into (narrow) frequency bands*；*each call allocated its own band, can transmit at max rate of that narrow band*。由于每个呼叫独占一个窄频带，它在整个呼叫期间都可以发送，可用的最大速率就是这一个窄频带的带宽。

**时分复用（Time Division Multiplexing，TDM）**：把时间划分成时隙（slot），每个呼叫分配周期性出现的时隙，每个呼叫只能在属于自己的时隙内发送，发送时可使用的最大速率是（较宽的）频带的最大速率。课件原文：*time divided into slots*；*each call allocated periodic slot(s), can transmit at maximum rate of (wider) frequency band (only) during its time slot(s)*。与 FDM 相比，TDM 中的呼叫在频率上使用整条（较宽的）频带，但在时间上只能间歇使用。

**【源图，课件页 1-37】** 两幅图，图例均标 *4 users*（4 个用户），并用蓝、绿、黄、品红四种颜色分别代表 4 个用户：

- FDM 子图：纵轴为频率（frequency），横轴为时间（time）。频率轴被划分为 4 条平行的色带，自上而下依次为蓝、绿、黄、品红，色带之间用虚线分隔；每条色带沿整个时间轴连续延伸，表示该用户在整个呼叫期间占用这一窄频带。
- TDM 子图：纵轴为频率，横轴为时间。时间轴被分成等宽的时隙，每个时隙在频率方向上占据同一段频带，时隙按蓝、绿、黄、品红的顺序周而复始地着色，即每个用户的时隙周期性出现，每个时隙内该用户使用整段频带。

两种复用方式的对照如下表：

| 对照项 | FDM（频分复用） | TDM（时分复用） |
|--------|----------------|----------------|
| 被划分的资源维度 | 频率（光、电磁频率） | 时间 |
| 分配单元 | 一个（窄）频带 | 周期性出现的时隙 |
| 呼叫独占范围 | 该频带，在整个呼叫期间持续占用 | 该时隙，仅在轮到自己的时隙内占用 |
| 发送时的可用最大速率 | 所分配的窄频带的最大速率 | （较宽的）频带的最大速率，但只在所属时隙内 |
| 图中用户数 | 4 个（蓝、绿、黄、品红） | 4 个（蓝、绿、黄、品红周期轮转） |

两种方式共同的后果与电路交换一致：分配出去的频带或时隙即使在呼叫空闲时也不会被其他呼叫使用，因此电路交换的资源利用率取决于呼叫的持续占用特性。这一性质是下一小节讨论分组交换与电路交换取舍的基础。

### 1.4.5 分组交换与电路交换的对比

课件页 1-38 用一个定量例子比较两种交换方式能支持的用户数，页 1-39 则给出定性结论。

#### 例题 1-2：1 Gb/s 链路下的用户数（课件页 1-38）

**题干**（课件原文）：*example:* 链路速率 $1$ Gb/s；每个用户（each user）：“active”（活跃）时占用 $100$ Mb/s，活跃时间占全部时间的 $10\%$。*Q: how many users can use this network under circuit-switching and packet switching?*（在电路交换与分组交换下，这个网络分别能供多少个用户使用？）

**【源图，课件页 1-38】** 左侧画出 $N$ 个用户（*N users*），共同连到一台路由器，该路由器右侧接一条标注 *1 Gbps link* 的链路输出。图右侧同时给出二项分布的表达式

$$P(X>10) = 1 - \sum_{k=0}^{10}\binom{35}{k}(0.1)^{k}(0.9)^{35-k}$$

**解**

**(1) 电路交换下的用户数**

第 1 步：把链路速率统一为 Mb/s。

$$1\ \text{Gb/s} = 1000\ \text{Mb/s}$$

第 2 步：电路交换下每个活跃用户需要被保留 $100$ Mb/s 的固定资源（由 1.4.3 小节“专用资源、不共享”的性质，无论该用户当前是否在发送，这份资源都为其保留），因此可支持的用户数等于链路总速率除以每个用户占用的速率：

$$\frac{1000\ \text{Mb/s}}{100\ \text{Mb/s}} = 10$$

即电路交换下可支持 $10$ 个用户。课件给出的结果为 *circuit-switching: 10 users*。

**用原数据校验**：$10 \times 100\ \text{Mb/s} = 1000\ \text{Mb/s} = 1\ \text{Gb/s}$，恰好等于链路速率，没有剩余带宽可再容纳第 11 个用户（$11 \times 100 = 1100\ \text{Mb/s} > 1000\ \text{Mb/s}$），校验通过。

**(2) 分组交换下的用户数**

分组交换不预留资源，用户按需发送，因此可以接入多于 10 个用户，代价是当同时活跃的用户超过 10 个时，瞬时总需求会超过链路容量。课件的设定是接入 $35$ 个用户，并计算“同时活跃的用户数超过 10”的概率。

第 1 步：明确随机变量与参数。设 $X$ 为同一时刻处于活跃状态的用户数。每个用户独立地以概率 $p = 0.1$ 处于活跃（课件给定 *active 10% of time*），参与统计的用户数 $n = 35$。因此

$$X \sim B(35,\ 0.1),\qquad P(X=k) = \binom{35}{k}(0.1)^{k}(0.9)^{35-k},\quad k = 0,1,\dots,35$$

第 2 步：明确“超载”对应的事件。每个活跃用户需要 $100$ Mb/s，链路容量为 $1$ Gb/s $= 1000$ Mb/s，恰好等于 $10$ 个活跃用户的需求。因此

- $X \le 10$：总需求 $X \times 100\ \text{Mb/s} \le 1000\ \text{Mb/s}$，链路够用；
- $X > 10$：例如 $X = 11$ 时需求为 $11 \times 100 = 1100\ \text{Mb/s} > 1000\ \text{Mb/s}$，需求超过链路容量，这正是课件要求计算概率的事件。

第 3 步：写出待求概率，利用互补事件

$$P(X>10) = 1 - P(X \le 10) = 1 - \sum_{k=0}^{10}\binom{35}{k}(0.1)^{k}(0.9)^{35-k}$$

第 4 步：逐项计算 $k = 0,1,\dots,10$ 的每一项。计算时使用 $(0.9)^{35} = 0.0250316$，并利用递推关系

$$\frac{P(X=k+1)}{P(X=k)} = \frac{35-k}{k+1}\cdot\frac{0.1}{0.9}$$

逐项结果如下（各概率保留 7 位小数）：

| $k$ | $\binom{35}{k}$ | $(0.1)^{k}$ | $(0.9)^{35-k}$ | $P(X=k)$ | 累计 $P(X\le k)$ |
|----|----------------|------------|----------------|----------|------------------|
| 0 | 1 | $1$ | 0.0250316 | 0.0250316 | 0.0250316 |
| 1 | 35 | $10^{-1}$ | 0.0278129 | 0.0973449 | 0.1223765 |
| 2 | 595 | $10^{-2}$ | 0.0309032 | 0.1838738 | 0.3062503 |
| 3 | 6545 | $10^{-3}$ | 0.0343369 | 0.2247346 | 0.5309849 |
| 4 | 52360 | $10^{-4}$ | 0.0381521 | 0.1997641 | 0.7307490 |
| 5 | 324632 | $10^{-5}$ | 0.0423912 | 0.1376153 | 0.8683643 |
| 6 | 1623160 | $10^{-6}$ | 0.0471013 | 0.0764529 | 0.9448172 |
| 7 | 6724520 | $10^{-7}$ | 0.0523348 | 0.0351926 | 0.9800098 |
| 8 | 23535820 | $10^{-8}$ | 0.0581498 | 0.0136860 | 0.9936958 |
| 9 | 70607460 | $10^{-9}$ | 0.0646109 | 0.0045620 | 0.9982578 |
| 10 | 183579396 | $10^{-10}$ | 0.0717899 | 0.0013180 | 0.9995758 |

表中每一项都满足 $P(X=k) = \binom{35}{k}(0.1)^k(0.9)^{35-k}$，例如第 $k=4$ 行：$52360 \times 10^{-4} \times 0.0381521 = 0.1997641$，与表中数值一致。交叉检验：由二项分布的性质 $\sum_{k=0}^{35} P(X=k) = 1$，而表中前 11 项（$k=0,\dots,10$）之和为 $0.9995758$，小于 1，剩余概率集中在尾部 $k \ge 11$ 的各项上，数值上是合理的。

第 5 步：得到前 11 项之和

$$P(X\le 10) = 0.9995758$$

于是

$$P(X>10) = 1 - 0.9995758 = 0.0004242$$

第 6 步：用尾部各项直接求和交叉校验。对 $k = 11,12,\dots$ 继续用同一递推关系计算：

| $k$ | $P(X=k)$ |
|----|----------|
| 11 | 0.0003328 |
| 12 | 0.0000739 |
| 13 | 0.0000145 |
| 14 | 0.0000025 |
| 15 | 0.0000004 |
| 16 | $5.48\times10^{-8}$ |
| 17 | $6.81\times10^{-9}$ |
| 18 | $7.57\times10^{-10}$ |

逐项相加：$0.0003328 + 0.0000739 = 0.0004067$；$+0.0000145 = 0.0004213$；$+0.0000025 = 0.0004238$；$+0.0000004 = 0.0004242$；再依次加上 $5.48\times10^{-8}$、$6.81\times10^{-9}$、$7.57\times10^{-10}$ 得 $0.0004243$。$k \ge 19$ 的项已小于 $10^{-10}$，可忽略。尾部求和结果 $0.0004243$ 与第 5 步的 $1 - 0.9995758 = 0.0004242$ 一致（末位差异来自各项截断），校验通过。

**答案**：电路交换下可支持 **10 个用户**；分组交换下接入 **35 个用户**时，同一时刻活跃用户数超过 10 的概率为

$$P(X>10) = \sum_{k=11}^{35}\binom{35}{k}(0.1)^{k}(0.9)^{35-k} = 0.0004243 \approx 4.24 \times 10^{-4}$$

**与课件数值的核对（含课件笔误说明）**：课件在此页写的是 *packet switching: with 35 users, probability > 10 active at same time is less than .0004*，并在旁边提出 *Q: how did we get value 0.0004? A: HW problem (for those with course in probability only)*——课件把该概率的计算留作作业题，只给出结论值。按上式逐项计算，精确值为 $4.243\times10^{-4}$；该值**大于** $4\times10^{-4}$，因此课件“小于 0.0004（less than .0004）”的严格不等式表述不成立，这是课件的笔误，不能用“四舍五入”解释。可以采用的表述是：课件给出的量级约 $4\times10^{-4}$，精算值为 $4.24\times10^{-4}$。

**(3) 两种结果的对照**

| 项目 | 电路交换 | 分组交换 |
|------|----------|----------|
| 资源分配 | 每个活跃用户预留 100 Mb/s，无论是否在发送 | 不预留，按需发送 |
| 可支持用户数 | 10 | 35 |
| 超载风险 | 第 11 个用户无法建立呼叫（资源已全部分配完） | 同时活跃用户超过 10 时总需求超过链路容量，概率 $4.24\times10^{-4}$ |
| 超载时的后果 | 呼叫被拒绝（发生在建立阶段） | 分组排队、时延增大、缓冲区满时丢包 |

课件在前两页已经说明分组交换发生排队与丢包的条件，本页的数值结果说明：在用户间歇活跃（活跃时间占 10%）的条件下，分组交换以很小的超载概率换取了 $35/10 = 3.5$ 倍的用户接入数量。这也说明课件在页 1-39 使用的措辞 *bursty*（突发的）——数据有时要发送、有时不发送，而不是一直占用链路。

#### 分组交换与电路交换的定性取舍（课件页 1-39）

课件先提出 *Is packet switching a "slam dunk winner"?*，然后分两面给出结论。

**分组交换的优势**（课件原文）：

- 适合**突发式（bursty）数据**——有时有数据要发送，另一些时候没有数据要发送；
- **资源共享**（resource sharing）：链路能力按需被多个用户共同使用，空闲资源不会被单个呼叫长期占用；
- **更简单、无需呼叫建立**（simpler, no call setup）：不需要在发送数据前经历预留端到端资源的过程。

**分组交换的代价**（课件原文）：

- 可能出现**过度拥塞（excessive congestion）**：由于缓冲区溢出造成分组时延与丢包（*packet delay and loss due to buffer overflow*）；
- 因此需要**协议**来提供可靠数据传输与拥塞控制（*protocols needed for reliable data transfer, congestion control*）——这是电路交换不需要、而分组交换必须由上层机制弥补的部分。

**课件的后续问题**：*Q: How to provide circuit-like behavior with packet-switching?*——如何在分组交换中提供类似电路的（可保证的）性能？课件给出的回答是 *"It's complicated." We'll study various techniques that try to make packet switching as "circuit-like" as possible.*：课件不在此处展开具体技术，只说明后续将学习各种尽量使分组交换具备电路式性能的技术。

课件在此页还提出一道讨论题 *Q: human analogies of reserved resources (circuit switching) versus on-demand allocation (packet switching)?*，要求用人类活动中的例子对照“预留资源”与“按需分配”。这里不使用任何类比，只给出两个方式在四个维度上的直接对照：

| 维度 | 预留资源（电路交换） | 按需分配（分组交换） |
|------|----------------------|----------------------|
| 资源占用 | 呼叫期间持续占用固定的频带或时隙 | 只在有分组要发送时占用链路 |
| 性能保证 | 呼叫建立成功后传输能力确定，性能可保证 | 无保证，时延随拥塞程度变化 |
| 对突发数据的适应 | 空闲期的资源不能被其他通信使用，适应性差 | 空闲资源可被其他通信使用，适应性好 |
| 控制开销 | 需要呼叫建立（预留过程） | 无需呼叫建立，但需要可靠传输、拥塞控制等协议 |

### 1.4.6 Internet 结构：网络的网络（Internet Structure: A "Network of Networks"）

课件从页 1-40 起转入 Internet 的全局结构。起点是一句话：**主机（hosts）通过接入 ISP（access Internet Service Providers）接入 Internet**；而各个接入 ISP 之间又必须互相连接（interconnected），这样才能使任意两台主机——不论它们位于何处——互相发送分组。由此得到的结果是一个**“网络的网络”（network of networks）**，其结构非常复杂，而且这种结构的**演化由经济因素（economics）与国家政策（national policies）驱动**（*evolution driven by economics, national policies*），不是由单一技术方案一次设计出来的。

**【源图，课件页 1-40】** 图中用若干蓝色云团分别标注了不同类型的网络，可见的标注有 *mobile network*（移动网络，云内画有基站、手机与汽车）、*home network*（家庭网络，云内画有住宅与终端设备）、*enterprise network*（企业网络，云内画有办公楼内的主机与服务器）、*national or global ISP*（国家或全球 ISP，云内画有多台路由器）、*local or regional ISP*（本地或区域 ISP，云内画有多台路由器）、*content provider network*（内容提供商网络，云内画有服务器）、*datacenter network*（数据中心网络，云内画有机架式服务器），各云团之间用线相连表示互连关系。

课件在这一页末尾给出方法上的说明：*Let's take a stepwise approach to describe current Internet structure*——采用逐步（stepwise）的方式描述当前的 Internet 结构。随后 8 页（1-41 至 1-48）就是这个逐步推演过程。

#### 逐步推演：从孤立的接入网到分层的网络之网络

**第 1 步（课件页 1-41）：问题的提出。** 课件的问题是：*given millions of access ISPs, how to connect them together?*——面对数以百万计的接入 ISP，如何把它们连接起来？**【源图】** 该页图面中央是一个由蓝色小云团（access net）围成的大圆圈，每个云团内标注 *access net*，云团之间留有空隙并以省略号（…）表示数量还有很多，全部接入网在这一步都是彼此孤立的。

**第 2 步（课件页 1-42）：直接两两互连的方案不成立。** 一种做法是让每个接入 ISP 与所有其他接入 ISP 直接相连。课件指出这一方案不可扩展（*doesn't scale*）：所需的连接数为 $O(N^2)$，其中 $N$ 为接入 ISP 的数量。**【源图】** 该页图与上一页相同，只是在若干对 access net 之间加上了密集的蓝色连线（图中以几个节点为中心向其余节点发出大量连线的方式表示连接数按平方增长），并在图中央写出 *connecting each access ISP to each other directly doesn't scale: $O(N^2)$ connections.*。其数量关系可以这样理解：若共有 $N$ 个接入 ISP，每个都要与其余 $N-1$ 个相连，则连接总数为 $N(N-1)/2$ 条，随 $N$ 的平方增长；当 $N$ 以百万计（$N = 10^{6}$）时，连接数约为 $5\times10^{11}$ 条，无法实现。课件只给出 $O(N^2)$ 这一量级结论，未给出具体数值。

**第 3 步（课件页 1-43）：引入全球中转 ISP。** 课件给出的方案是 *Option: connect each access ISP to one global transit ISP?*——把每个接入 ISP 连到一个全球中转 ISP。同时给出一个关键限定：*Customer and provider ISPs have economic agreement.*——客户 ISP 与提供商 ISP 之间存在经济协议，即接入 ISP（客户）为使用全球 ISP（提供商）的中转服务付费，这种连接不是纯技术连接，而是有商业关系的连接。**【源图】** 该页图面中央是一个较大的蓝色椭圆，内部标注 *global ISP* 并画有多台互连的路由器，四周的 access net 各自用一条线连到 global ISP 云内的某个路由器上。此方案下连接数由 $O(N^2)$ 降为 $O(N)$ 量级：每个接入 ISP 只需一条连接到全球 ISP。

**第 4 步（课件页 1-44）：竞争者出现。** 课件接着指出 *But if one global ISP is viable business, there will be competitors ….*——如果一家全球 ISP 是一门可盈利的生意，就会出现竞争者。**【源图】** 该页图中出现三个蓝色椭圆云团，分别标注 *ISP A*、*ISP B*、*ISP C*，每个云内画有多台互连的路由器；四周的 access net 分别连到三个 ISP 云团之一，即不同接入网选择了不同的全球 ISP。

**第 5 步（课件页 1-45）：竞争者之间互连：IXP 与对等链路。** 课件在第 4 步的文字后追加 *…. who will want to be connected*——这些互相竞争的 ISP 会希望彼此连接。为此出现两种结构：**Internet 交换点（IXP，Internet exchange point）**与**对等链路（peering link）**。**【源图】** 该页图在上一页三朵 ISP 云的基础上，用红色粗线把 ISP A、ISP B、ISP C 连接起来，图中标出两个 IXP（蓝色小椭圆，内部标注 IXP）：一处位于 ISP A 与 ISP B 之间（由红线相连），另一处位于 ISP A 与 ISP C 之间；ISP B 与 ISP C 之间也由红色对等链路直接相连。图中红色标注文字 *Internet exchange point* 指向 IXP 图元，*peering link* 指向 ISP 之间的红线。

**第 6 步（课件页 1-46）：区域网络出现。** 课件指出 *… and regional networks may arise to connect access nets to ISPs*——可能出现区域网络，用来把接入网连接到 ISP。**【源图】** 该页图在上一页基础上新增一个淡紫色椭圆云团，标注 *regional ISP*，位置在 ISP C 云团下方；图的左上部另有一个同类的淡紫色小椭圆（同一结构在 ISP A 一侧的表示），若干 access net 先接入 regional ISP，再由 regional ISP 接入上层 ISP。也就是说，接入网与全球 ISP 之间可以隔一层区域 ISP。

**第 7 步（课件页 1-47）：内容提供商网络出现。** 课件指出 *… and content provider networks (e.g., Google, Microsoft, Akamai) may run their own network, to bring services, content close to end users*——内容提供商网络（例如 Google、Microsoft、Akamai）可能自建网络，把服务与内容送到离终端用户更近的位置。**【源图】** 该页图中新增一条橙色横向带，标注 *Content provider network*，带内画有两组机房／服务器图元（以带机架的建筑物图标表示），橙色带与 ISP A、ISP B 云团以及图中的 IXP 都有连线，并与上方若干 access net 直接相连；图中还出现一个位于橙色带内的 IXP 图元。该步骤的含义是：内容提供商不再只把自己的服务器挂在某个 ISP 后面，而是自建跨越多个 ISP 范围的网络，直接与各接入网或 IXP 相连。

**第 8 步（课件页 1-48）：当前结构的概括。** 课件给出总结段落：*At "center": small # of well-connected large networks*——处在“中心”位置的是数量很少、连通度很高的大型网络，具体有两类：

- ***tier-1* 商业 ISP**（例如 Level 3、Sprint、AT&T、NTT），具有国家与国际范围的覆盖（*national & international coverage*）；
- **内容提供商网络**（例如 Google、Facebook）：连接其自身数据中心的专用网络，常常绕过 tier-1 与区域 ISP（*private network that connects its data centers to Internet, often bypassing tier-1, regional ISPs*）。

**【源图】** 该页图为分层示意图：最上层并排三个椭圆，分别为 *Tier 1 ISP*、*Tier 1 ISP* 与橙色的 *Google*，三者之间由连线相连（顶层还有一条跨越的弧线连接上述大型网络）；第二层是三个标注 *IXP* 的蓝色小椭圆；第三层是两个标注 *Regional ISP* 的淡紫色椭圆；最下层是 8 个标注 *access ISP* 的浅蓝色椭圆，它们分别连到区域 ISP、IXP 或 Tier 1 ISP。图中各层之间用细实线表示互连关系。

#### 逐步推演过程小结

页 1-41 至 1-48 的推演可以按“每步新增的成分”归纳如下表：

| 步骤 | 课件页 | 新增成分 | 该步要说明的问题 |
|------|--------|----------|------------------|
| 1 | 1-41 | 数以百万计彼此孤立的接入网（access net） | 提出“如何互连”的问题 |
| 2 | 1-42 | 任意两两直接互连 | 连接数 $O(N^2)$，不能扩展，方案被否 |
| 3 | 1-43 | 全球中转 ISP（global ISP），客户与提供商之间有经济协议 | 连接数降为 $O(N)$ 量级 |
| 4 | 1-44 | 竞争性 ISP（ISP A、ISP B、ISP C） | 单一全球 ISP 可盈利则必有竞争者 |
| 5 | 1-45 | Internet 交换点（IXP）与对等链路（peering link） | 竞争者也必须互连 |
| 6 | 1-46 | 区域网络（regional ISP） | 接入网与 ISP 之间可隔一层区域网络 |
| 7 | 1-47 | 内容提供商网络（content provider network） | 内容与服务被送到离终端用户更近处 |
| 8 | 1-48 | 少量连通度高的大型网络（tier-1 ISP、内容提供商网络） | 概括当前 Internet 的“中心”结构 |

课件把这一过程表述为**描述当前 Internet 结构的分步方法**，而不是历史上真实发生的、严格按此顺序的演化记录；课件在第 1 步之前就明确指出该结构的演化由经济与国家政策驱动，因此每一步（尤其是第 4、5、7 步）都同时是经济关系的产物。

---

## 1.5 性能：丢包、时延与吞吐量（Performance: Loss, Delay, Throughput）

课件页 1-49 再次给出 **Chapter 1 的路线图（roadmap）**，用于标示讲授进度。该页列出的 8 项内容按课件顺序为：

- *What is the Internet?*（什么是 Internet？）
- *What is a protocol?*（什么是协议？）
- *Network edge: hosts, access network, physical media*（网络边缘：主机、接入网、物理介质）
- *Network core: packet/circuit switching, internet structure*（网络核心：分组交换／电路交换、Internet 结构）
- *Performance: loss, delay, throughput*（性能：丢包、时延、吞吐量）
- *Security*（安全）
- *Protocol layers, service models*（协议分层、服务模型）
- *History*（历史）

其中前四项在图中以灰色显示，表示已经讲过；**第五项 *Performance: loss, delay, throughput* 以蓝色加粗显示**，表示从这一张开始进入性能部分。

本节处理性能的三个量：**丢包（loss）、时延（delay）、吞吐量（throughput）**，依次给出丢包与时延的成因、结点时延的四个来源及其定量核算、排队时延与流量强度、真实互联网的时延测量、分组丢失，以及吞吐量与瓶颈链路。

### 1.5.1 分组时延与丢包的产生（课件页 1-50）

课件页 1-50 把前面已经出现的排队与丢包现象放到“性能”语境下重新表述，给出三条结论：

- 分组在路由器的缓冲区中排队，等待轮到它被传输（*packets queue in router buffers, waiting for turn for transmission*）；
- 当到达链路的速率（暂时地）超过输出链路的能力时，队列长度会增长（*queue length grows when arrival rate to link (temporarily) exceeds output link capacity*）；
- 当用于存放排队分组的存储器被填满时，发生分组丢失（*packet loss occurs when memory to hold queued packets fills up*）。

**【源图，课件页 1-50】** 左侧为主机 A 与主机 B，各自经一条链路连到第一台路由器，第一台路由器再经一条链路连到第二台路由器（A 到第一台路由器的链路上画有一个蓝色分组方块，B 到第一台路由器的链路上画有一个绿色分组方块）。图中用三处引线标出三件事：

- *packet being transmitted (transmission delay)*——引线指向第一台路由器输出链路上正在被推出的分组，说明**正在传输的分组**这一状态对应传输时延；
- *packets in buffers (queueing delay)*——引线指向第一台路由器内部缓冲区中排队的若干分组方块，说明**缓冲区中等待的分组**对应排队时延；
- *free (available) buffers: arriving packets dropped (loss) if no free buffers*——引线指向缓冲区中尚未占用的位置（空位），说明当没有空闲缓冲区时，到达的分组会被丢弃。

这三处标注与 1.4.2 小节的结论一致，区别在于本页把“排队”和“丢包”明确对应到**排队时延**与**分组丢失**这两个性能结果上，并由此引出下一页对这一时延的分解。

### 1.5.2 结点时延的四个来源（Packet Delay: Four Sources，课件页 1-51、1-52）

课件把分组经过一台路由器的时延分解为四项之和：

$$d_{\text{nodal}} = d_{\text{proc}} + d_{\text{queue}} + d_{\text{trans}} + d_{\text{prop}}$$

式中各项含义与来源如下。

**结点处理时延（$d_{\text{proc}}$，nodal processing）**：该时延段所做的工作是**检查比特差错（check bit errors）**与**确定输出链路（determine output link）**，典型量级为通常小于微秒（*typically < microsecs*），即 $d_{\text{proc}} < 10^{-6}$ s 量级。它由路由器处理分组的机制决定，与链路速率、链路长度无直接比例关系。

**排队时延（$d_{\text{queue}}$，queueing delay）**：定义为*在输出链路处等待被传输的时间*（*time waiting at output link for transmission*），它**取决于路由器的拥塞程度**（*depends on congestion level of router*）。由于拥塞程度随到达流量动态变化，$d_{\text{queue}}$ 是四项中唯一不能由单个分组的长度和链路参数直接确定的量。

**传输时延（$d_{\text{trans}}$，transmission delay）**：指把分组的所有比特推上链路的时间。符号定义为：$L$ 为分组长度（packet length），单位比特（bits）；$R$ 为链路传输速率（link transmission rate），单位比特每秒（bps）。公式为

$$d_{\text{trans}} = \frac{L}{R}$$

$d_{\text{trans}}$ 的单位为秒。它与 1.4.1 小节的 *packet transmission delay* 是同一个量。

**传播时延（$d_{\text{prop}}$，propagation delay）**：指比特在物理链路上前进所需的时间。符号定义为：$d$ 为物理链路的长度（length of physical link）；$s$ 为传播速率（propagation speed），约为 $2\times10^{8}$ m/sec。公式为

$$d_{\text{prop}} = \frac{d}{s}$$

$d$ 的单位为米（m），$s$ 的单位为米每秒（m/s），$d_{\text{prop}}$ 的单位为秒。

课件在页 1-52 末尾给出结论：*d trans and d prop very different*——传输时延与传播时延是两个**完全不同**的量。从两个公式可以看出两者的决定因素互不相同：$d_{\text{trans}} = L/R$ 只取决于分组长度与该段链路的传输速率，与链路有多长无关；$d_{\text{prop}} = d/s$ 只取决于链路的物理长度与信号的传播速率，与分组有多长、链路速率多高无关。

**【源图，课件页 1-51、1-52】** 两页使用同一张示意图：主机 A 与主机 B 各自连到第一台路由器，第一台路由器再经一条链路连到第二台路由器。图上有四处文字标注与引线：*transmission*（位于 A/B 到第一台路由器的链路旁，指向正在该链路上传输的分组方块）、*nodal processing*（位于第一台路由器下方，引线指向该路由器）、*queueing*（位于第一台路由器下方，引线指向路由器内部的排队位置）、*propagation*（位于两台路由器之间的链路上方，用双向箭头指向该链路）。页 1-51 给出 $d_{\text{nodal}}$ 的四项求和公式以及 $d_{\text{proc}}$、$d_{\text{queue}}$ 的定义；页 1-52 重复同一张图与同一个求和公式，另给出 $d_{\text{trans}} = L/R$ 与 $d_{\text{prop}} = d/s$ 两个公式，并用一条两端带圈的连线把这两个公式连起来，标注 *d trans and d prop very different*。

四项时延的来源、公式与单位汇总如下表：

| 分量 | 课件名称 | 含义 | 公式 | 主要决定因素 | 单位 |
|------|----------|------|------|----------------|------|
| $d_{\text{proc}}$ | nodal processing | 检查比特差错、确定输出链路所占的时间 | 课件未给出公式 | 路由器处理机制；课件给出典型值 < 1 μs | s |
| $d_{\text{queue}}$ | queueing delay | 在输出链路处等待被传输的时间 | 课件未给出公式 | 路由器的拥塞程度 | s |
| $d_{\text{trans}}$ | transmission delay | 把 $L$ 比特推上速率为 $R$ 的链路的时间 | $d_{\text{trans}} = L/R$ | 分组长度 $L$（bit）、链路传输速率 $R$（bps） | s |
| $d_{\text{prop}}$ | propagation delay | 比特在物理链路上前进 $d$ 米的时间 | $d_{\text{prop}} = d/s$ | 链路长度 $d$（m）、传播速率 $s$（约 $2\times10^{8}$ m/s） | s |

按该公式，一个分组在一次“结点”上的总时延是四项之和；其中 $d_{\text{trans}}$ 与 $d_{\text{prop}}$ 可以分别用 $L$、$R$、$d$、$s$ 四个已知量算出，而 $d_{\text{queue}}$ 需要知道路由器的拥塞状况，$d_{\text{proc}}$ 通常按远小于其他项处理。

### 1.5.3 传输时延与传播时延的核算：商队对照模型（Caravan Analogy，课件页 1-53、1-54）

课件在给出 $d_{\text{trans}}=L/R$ 与 $d_{\text{prop}}=d/s$ 之后，用“车辆—车队—收费站—公路”构造了一个可手算的对照模型，把比特、分组、链路传输、链路传播这几类对象与它们的量对应起来。该模型是课件自带的对照模型，其对应关系与全部数值均取自课件原文：

| 对照模型中的对象 | 对应的网络对象 | 课件给出的量 |
|---|---|---|
| 一辆汽车（car） | 一个比特（bit） | — |
| 十辆车组成的车队（ten-car caravan） | 一个 10 比特分组（10-bit packet） | 分组长度 $L=10$ bit |
| 收费站对一辆车的服务（toll service） | 链路传输（link transmission） | 服务一辆车 $1/R=12$ s |
| 车辆在公路上的行驶 | 链路传播（propagation） | 行驶速度 100 km/hr |
| 两个收费站之间的距离 | 链路长度 $d$ | 100 km |
| 收费站（toll booth） | 课件页 1-53 标注为 link（链路）；页 1-54 标注为 router（路由器） | — |

课件两页对收费站的标注不同（一处标 link，一处标 router），这里按原文分别标注，不统一改写。

#### 例题 1-3：车队在第 2 个收费站前排队完毕需要多久（课件页 1-53）

**题干**（课件原文）：car ~ bit; caravan ~ packet; toll service ~ link transmission；收费站服务一辆车需要 12 sec（即比特传输时间）；车辆以 100 km/hr "propagate"；*Q: How long until caravan is lined up before 2nd toll booth?*。原图为：十辆车组成的车队在第 1 个收费站前，收费站之后是 100 km 的公路，再是第 2 个收费站，其后又是 100 km 与第 3 个收费站。

**解**

第 1 步：计算把整个车队推过第 1 个收费站所需的时间，即分组在一段链路上的传输时延 $d_{\text{trans}}$。收费站的通道在任一时刻只服务一辆车，服务一辆车 12 s，车队共 10 辆车：

$$d_{\text{trans}}=10\times 12\ \text{s}=120\ \text{s}=2\ \text{min}$$

课件原文写作：time to "push" entire caravan through toll booth onto highway = $12\times10 = 120$ sec。

第 2 步：计算最后一辆车从第 1 个收费站传播到第 2 个收费站所需的时间，即传播时延 $d_{\text{prop}}$。距离 100 km，速度 100 km/hr：

$$d_{\text{prop}}=\frac{100\ \text{km}}{100\ \text{km/hr}}=1\ \text{hr}=3600\ \text{s}$$

第 3 步：求“第 1 个收费站把整个车队推上公路”完成之后，最后一辆车再行驶到第 2 个收费站所需的总时间。第 1 步结束时时刻为 120 s，此时最后一辆车刚离开第 1 个收费站，它还要 3600 s 才到达第 2 个收费站：

$$t=120\ \text{s}+3600\ \text{s}=3720\ \text{s}=62\ \text{min}$$

**答案**：62 minutes（与课件答案 A: 62 minutes 一致）。

第 4 步：用原始数据校验。第一辆车在 $12\ \text{s}$ 时离开第 1 个收费站，到达第 2 个收费站的时刻为

$$12\ \text{s}+3600\ \text{s}=3612\ \text{s}=60.2\ \text{min}$$

最后一辆车到达第 2 个收费站的时刻为

$$120\ \text{s}+3600\ \text{s}=3720\ \text{s}=62\ \text{min}$$

“车队在第 2 个收费站前排队完毕”要求全部 10 辆车到齐，因此该时刻就是最后一辆车到达的时刻 62 min，与答案相符。两个中间量分别为 $d_{\text{trans}}=2$ min、$d_{\text{prop}}=60$ min。

本模型的直接含义：$d_{\text{trans}}$ 由分组长度与链路速率之比决定，$d_{\text{prop}}$ 由链路长度与传播速度之比决定，两者互相独立，量级可以相差很大。此处 $d_{\text{trans}}=2$ min 远小于 $d_{\text{prop}}=60$ min，即整组比特在链路入口处只用 2 min 就全部发送完毕，但最先发出的比特要 60 min 才到达对端。

#### 例题 1-4：车辆会不会在第 1 个收费站服务完全部车辆之前到达第 2 个收费站（课件页 1-54）

**题干**（课件原文）：suppose cars now "propagate" at 1000 km/hr；and suppose toll booth now takes one min to service a car；*Q: Will cars arrive to 2nd booth before all cars serviced at first booth?*。原图中收费站标注为 toll booth (aka router)，车队仍为 ten-car caravan (aka 10-bit packet)，两站间距仍为 100 km。

**解**

第 1 步：确定第 1 辆车完成服务、离开第 1 个收费站的时刻。服务一辆车需要 1 min，从 $t=0$ 开始服务，第 1 辆车在 $t=1$ min 离开第 1 个收费站。

第 2 步：计算传播时间。

$$d_{\text{prop}}=\frac{100\ \text{km}}{1000\ \text{km/hr}}=0.1\ \text{hr}=6\ \text{min}$$

第 3 步：计算第 1 辆车到达第 2 个收费站的时刻。

$$t_1=1\ \text{min}+6\ \text{min}=7\ \text{min}$$

第 4 步：计算第 1 个收费站在 $t=7$ min 时已经服务完的车辆数。服务时间 1 min/辆、连续服务，第 $k$ 辆车在 $t=k$ min 时服务完毕；到 $t=7$ min 时第 7 辆车恰好服务完毕，尚未服务的车辆数为

$$10-7=3\ \text{辆}$$

第 5 步：得出结论。第 1 辆车在 7 min 时已到达第 2 个收费站，而第 1 个收费站还有 3 辆车没有服务，所以答案是“会”。与课件答案一致：A: Yes! after 7 min, first car arrives at second booth; three cars still at first booth。

第 6 步：用原始数据校验。把整队推过第 1 个收费站需要 $10\times 1\ \text{min}=10$ min，即到 $t=10$ min 第 1 个收费站才服务完全部车辆。$t_1=7\ \text{min}<10\ \text{min}$，第 1 辆车到达第 2 个收费站确实早于第 1 个收费站服务完全队；且第 4 步算出的未服务车辆数 $10-7=3$ 与课件答案中的 three cars still at first booth 一致。

与例题 1-3 的差别：这里传播时间 6 min 小于把整队推过收费站的时间 10 min，先出发的车辆会在后续车辆仍在第 1 个收费站接受服务时就到达第 2 个收费站。对应到网络中的事实是：一个分组沿一段链路传输的过程中，其靠前的比特已经在该链路上传播、甚至可以到达下一跳结点，而该分组的尾部仍在源端被发送，即传输时延与传播时延在时间上是重叠的。这与存储转发（store-and-forward）“整个分组到达路由器后才可向下一段链路传输”的限制不冲突——存储转发约束的是分组整体进入下一段链路的时刻，并不要求该分组的每个比特在链路上彼此串行等待。

### 1.5.4 分组排队时延与流量强度（Packet Queueing Delay，课件页 1-55）

课件在给出四类时延之后，重新回到排队时延 $d_{\text{queue}}$，用三个量刻画它的平均大小。符号与单位（全部取自课件原文）：

| 符号 | 课件原文含义 | 单位 |
|---|---|---|
| $a$ | average packet arrival rate，平均分组到达速率 | 分组/秒（packets/s） |
| $L$ | packet length，分组长度 | 比特（bit） |
| $R$ | link bandwidth，链路带宽（bit transmission rate，比特传输速率） | 比特/秒（bit/s） |

课件定义“流量强度”（traffic intensity）为

$$\frac{L\cdot a}{R}=\frac{\text{arrival rate of bits}}{\text{service rate of bits}}=\frac{\text{比特到达速率}}{\text{比特服务速率}}$$

量纲核对：$La$ 的单位是 $(\text{bit/分组})\times(\text{分组/s})=\text{bit/s}$，即比特到达速率；$R$ 的单位是 $\text{bit/s}$，即比特服务速率；两者之比的单位为 1，无量纲。课件在式子右侧括注：$R$ 为 service rate of bits（比特的服务速率），$L\cdot a$ 为 arrival rate of bits（比特的到达速率），并把 $\dfrac{L\cdot a}{R}$ 命名为 traffic intensity。

课件给出的三种情形（原文）：

- $La/R\sim 0$：average queueing delay small，平均排队时延很小。比特到达速率远小于链路服务速率，分组到达后几乎不需要等待即可被发送。
- $La/R\to 1$：average queueing delay large，平均排队时延很大。比特到达速率接近链路服务速率，队列经常积压，平均排队时延随流量强度上升而迅速增大。
- $La/R>1$：more "work" arriving is more than can be serviced — average delay infinite!，到达的“工作量”超过链路能服务的工作量，平均时延为无穷大。

**【源图，课件页 1-55】** 横轴标注为 traffic intensity = $La/R$，并在横轴上标出数值 1 的位置；纵轴标注为 average queueing delay（平均排队时延）。曲线在 $La/R$ 较小时接近水平且数值很小，当 $La/R$ 趋近 1 时急剧上翘趋向竖直；横轴 1 处有一条竖直虚线，对应 $La/R=1$ 的分界。原图另配两张照片，分别标注 $La/R\sim 0$ 与 $La/R\to 1$；照片内不含可读取的数值与拓扑。

课件未给出 $d_{\text{queue}}$ 关于 $La/R$ 的解析表达式，只给出上述定性关系。把 1.5.2 小节的 $d_{\text{trans}}=L/R$ 与本节的 $La/R$ 对照可知：$La/R$ 是把平均到达速率 $a$、分组长度 $L$、链路速率 $R$ 三者合成一个无量纲量的办法，它决定平均排队时延的数量级。

### 1.5.5 真实互联网的时延与路由：traceroute（课件页 1-56、1-57）

课件提出的问题是：真实互联网中的时延与丢失呈现什么样的数值（*what do "real" Internet delay & loss look like?*）。课件用 traceroute 程序来回答。

#### traceroute 的测量原理（课件页 1-56）

课件原文定义：traceroute program: provides delay measurement from source to router along end-end Internet path towards destination. For all $i$（traceroute 程序给出从源端到通向目的地的端到端互联网路径上各路由器的时延测量；对所有的 $i$）：

1. sends three packets that will reach router $i$ on path towards destination (with time-to-live field value of $i$)：发送三个分组，这些分组能到达通向目的地的路径上的第 $i$ 个路由器，做法是把分组的 time-to-live 字段值置为 $i$；
2. router $i$ will return packets to sender：第 $i$ 个路由器会把这些分组回送给发送端；
3. sender measures time interval between transmission and reply：发送端测量从发出分组到收到回应之间的时间间隔。

对 $i=1,2,3,\dots$ 依次重复上述三步，就得到源端到路径上各跳路由器的时延序列。**【源图，课件页 1-56】** 一台发送主机经若干个路由器连到一台接收主机，图中的每个路由器上分别标注 *3 probes*（三次探测），表示对每一跳发出三次探测。

补充说明（由上述机制直接得到，课件未展开）：把 time-to-live 置为 $i$ 的第 $i$ 个探测分组最多只能前进 $i$ 跳，超出后被该跳路由器丢弃并回送差错回应，因此发送端测到的时间是“源端到第 $i$ 跳路由器、再从该路由器返回源端”的往返时延（round-trip time, RTT），该值是从源端起算的累计值，不是第 $i$ 跳这一段的单段时延。

#### 实测输出：gaia.cs.umass.edu → www.eurecom.fr（课件页 1-57）

课件标题为 `traceroute: gaia.cs.umass.edu to www.eurecom.fr`，共 19 跳，每跳给出三次探测的往返时延，单位为 ms。逐行完整抄录如下：

| 跳数 $i$ | 路由器 / 主机名（IP 地址） | 第 1 次探测 | 第 2 次探测 | 第 3 次探测 |
|---|---|---|---|---|
| 1 | cs-gw (128.119.240.254) | 1 ms | 1 ms | 2 ms |
| 2 | border1-rt-fa5-1-0.gw.umass.edu (128.119.3.145) | 1 ms | 1 ms | 2 ms |
| 3 | cht-vbns.gw.umass.edu (128.119.3.130) | 6 ms | 5 ms | 5 ms |
| 4 | jn1-at1-0-0-19.wor.vbns.net (204.147.132.129) | 16 ms | 11 ms | 13 ms |
| 5 | jn1-so7-0-0-0.wae.vbns.net (204.147.136.136) | 21 ms | 18 ms | 18 ms |
| 6 | abilene-vbns.abilene.ucaid.edu (198.32.11.9) | 22 ms | 18 ms | 22 ms |
| 7 | nycm-wash.abilene.ucaid.edu (198.32.8.46) | 22 ms | 22 ms | 22 ms |
| 8 | 62.40.103.253 (62.40.103.253) | 104 ms | 109 ms | 106 ms |
| 9 | de2-1.de1.de.geant.net (62.40.96.129) | 109 ms | 102 ms | 104 ms |
| 10 | de.fr1.fr.geant.net (62.40.96.50) | 113 ms | 121 ms | 114 ms |
| 11 | renater-gw.fr1.fr.geant.net (62.40.103.54) | 112 ms | 114 ms | 112 ms |
| 12 | nio-n2.cssi.renater.fr (193.51.206.13) | 111 ms | 114 ms | 116 ms |
| 13 | nice.cssi.renater.fr (195.220.98.102) | 123 ms | 125 ms | 124 ms |
| 14 | r3t2-nice.cssi.renater.fr (195.220.98.110) | 126 ms | 126 ms | 124 ms |
| 15 | eurecom-valbonne.r3t2.ft.net (193.48.50.54) | 135 ms | 128 ms | 133 ms |
| 16 | 194.214.211.25 (194.214.211.25) | 126 ms | 128 ms | 126 ms |
| 17 | \* | \* | \* | \* |
| 18 | \* | \* | \* | \* |
| 19 | fantasia.eurecom.fr (193.55.113.142) | 132 ms | 128 ms | 136 ms |

课件在原图上的标注（按原图文义转述）：

- 分别指向第 1 跳与第 2 跳的两组箭头标注为 *3 delay measurements from gaia.cs.umass.edu to cs-gw.cs.umass.edu* 与 *3 delay measurements to border1-rt-fa5-1-0.gw.umass.edu*，说明每一行中的三个数值是同一条路径上三次独立测量得到的时延；
- 第 7 跳 `nycm-wash.abilene.ucaid.edu (198.32.8.46)` 的 22 ms 处标注 *trans-oceanic link*（跨洋链路）；
- 第 8 至第 12 跳附近标注 *looks like delays decrease! Why?*，并在第 7 跳的 22 ms、第 8 跳的 106 ms、第 11 跳的 112 ms 处作高亮标记（课件未说明高亮的选取判据）；
- 表格下方标注 *\* means no response (probe lost, router not replying)*（星号表示无回应：探测分组丢失，或路由器不回送回应）；
- 另有提示 *\* Do some traceroutes from exotic countries at www.traceroute.org*。

基于原表的逐项说明（以下计算为由原数据直接推算的补充内容，课件未列出）：

1. 第 1、2 跳的三次测量分别为 1 ms、1 ms、2 ms 与 1 ms、1 ms、2 ms，说明源主机到校园网出口路由器的往返时延在毫秒量级。
2. 第 7 跳到第 8 跳之间累计 RTT 出现跃升。按第 1 次探测列计算：$104\ \text{ms}-22\ \text{ms}=82\ \text{ms}$；按第 3 次探测列计算：$106\ \text{ms}-22\ \text{ms}=84\ \text{ms}$。这一数量级的跃升与图中 trans-oceanic link 的标注相符：跨洋链路的传播时延本身就在几十毫秒量级。
3. 第 17、18 跳三次探测均为 `* * *`，按课件注释是无回应（探测分组丢失，或路由器不回送回应）；而第 19 跳仍给出 132 ms、128 ms、136 ms 的测量值，说明第 17、18 跳位置上的结点即使不回送回应，分组仍在被转发。课件跳号从 1 编到 19，其中第 17、18 跳没有时延数值。
4. 若需要单段（逐跳增量的）时延，应对相邻两跳的同一列数值作差；不同列来自不同时刻的探测，不宜跨列相减。

关于“时延看起来变小”（课件原文只提问 Why?，未给出答案；以下为补充解释，非课件原文）：

1. 三次探测在不同时刻发出，沿途各路由器的排队时延随时间波动，后发出的探测遇到较轻的排队，测得的 RTT 可以小于先前的探测。
2. 探测分组可能沿不同路径到达同一跳序号，路径改变会使第 $i$ 跳对应的实际路由器与链路的组合发生变化。
3. 路由器回送回应时的去程与回程路径可能与该路由器转发正常数据时的路径不同，回程方向的拥塞程度也不同。
4. traceroute 输出的每一行是“源到第 $i$ 跳”的累计 RTT，单看相邻两行的数值大小不能直接判定“某一段链路的时延下降了”；图中第 10 跳的 113 ms 与第 11 跳的 112 ms、第 15 跳第 1 次探测的 135 ms 与第 16 跳第 1 次探测的 126 ms 都属这种逐次波动。

### 1.5.6 分组丢失（Packet Loss，课件页 1-58）

课件原文给出三点：

1. queue (aka buffer) preceding link in buffer has finite capacity：链路之前的队列（queue，又称缓冲区 buffer）容量有限；
2. packet arriving to full queue dropped (aka lost)：到达已满队列的分组被丢弃，又称丢失（lost）；
3. lost packet may be retransmitted by previous node, by source end system, or not at all：丢失的分组可能由前一个结点重传，可能由源端系统重传，也可能不被重传。

**【源图，课件页 1-58】** 两个端系统 A、B 分别向一台带队列的结点发送分组；该队列用一串方格表示，标注 *buffer (waiting area)*（缓冲区，即等待区）；队列前方有一个正在发出的分组，标注 *packet being transmitted*；从 B 方向到达的一个分组落在队列之外，标注 *packet arriving to full buffer is lost*。图下方另有提示 *\* Check out the Java applet for an interactive animation (on publisher's website) of queuing and loss*。

与 1.5.4 小节的关系：排队时延由流量强度 $La/R$ 决定，表现为分组在队列中的等待时间；当 $La/R$ 的长期取值超过 1 时，队列持续增长直至填满有限容量的缓冲区，此后到达的分组被丢弃，这就是分组丢失的直接原因。分组丢失与排队时延是同一机制（有限缓冲区 + 到达速率超过服务速率）在同一结点上产生的两种后果。

### 1.5.7 吞吐量（Throughput，课件页 1-59 至 1-61）

#### 定义与瞬时、平均吞吐量（课件页 1-59）

课件原文定义：throughput: rate (bits/time unit) at which bits are being sent from sender to receiver，即比特从发送端被送到接收端的速率，单位为 bit/time unit（bit/s）。课件区分两种取值：

- instantaneous（瞬时吞吐量）：rate at given point in time，某一给定时刻的速率；
- average（平均吞吐量）：rate over longer period of time，较长时间段上的速率。

**【源图，课件页 1-59】** 一台服务器要把一个 $F$ 比特的文件发送给客户机（server, with file of F bits to send to client）；服务器到中间结点之间的链路容量标注 $R_s$ bits/sec（link capacity），中间结点到客户机之间的链路容量标注 $R_c$ bits/sec（link capacity）。课件用流体经管道的图形表示比特的发送与接收，两段管道的标注分别为 *pipe that can carry fluid at rate ($R_s$ bits/sec)* 与 *pipe that can carry fluid at rate ($R_c$ bits/sec)*，服务器一侧标注 *server sends bits (fluid) into pipe*。其量值标注即为两段链路的容量 $R_s$ 与 $R_c$。

由平均吞吐量的定义可直接得到（课件未写出该式）：若文件长度为 $F$ 比特、端到端传送耗时为 $T$，则这段时间上的平均吞吐量为 $F/T$，单位为 bit/s。

#### 两段链路串联：瓶颈链路与取小关系（课件页 1-60）

课件把两段链路的容量关系分为两种情形提问。

情形一，$R_s<R_c$：课件原文问 *What is average end-end throughput?*。第二段链路能承载的速率 $R_c$ 大于第一段链路能承载的 $R_s$，发送端最多只能以 $R_s$ 向第一段链路注入比特，因此端到端平均吞吐量为

$$\min(R_s,R_c)=R_s$$

情形二，$R_s>R_c$：课件原文同样问 *What is average end-end throughput?*。第一段链路能承载 $R_s$，但第二段只能承载 $R_c$，接收端从第二段链路取出比特的速率不可能超过 $R_c$，因此

$$\min(R_s,R_c)=R_c$$

课件随后给出定义（原文）：bottleneck link（瓶颈链路）：link on end-end path that constrains end-end throughput，即端到端路径上限制端到端吞吐量的那条链路。上述两种情形中，容量较小的那条链路就是瓶颈链路。

由上述取小关系可直接推广（课件未写出）：端到端路径上串联 $N$ 段链路、容量分别为 $R_1,R_2,\dots,R_N$ 时，端到端吞吐量为 $\min(R_1,R_2,\dots,R_N)$，即路径上容量最小的链路决定端到端吞吐量。

#### 吞吐量：多连接共享骨干链路的网络场景（课件页 1-61）

课件给出的场景（原文）：10 connections (fairly) share backbone bottleneck link $R$ bits/sec，即 10 条连接（大致公平地）共享一条骨干瓶颈链路，骨干链路容量为 $R$ bits/sec。**【源图】** 若干服务器经各自的接入链路 $R_s$ 接入网络，若干客户机经各自的接入链路 $R_c$ 接入网络，共享的骨干链路容量标注为 $R$。

课件给出的结论（原文）：

- per-connection end-end throughput: $\min(R_c,R_s,R/10)$。在 10 条连接平均分享骨干链路的假设下，单条连接的端到端吞吐量取三个量中的最小值：客户机侧接入链路容量 $R_c$、服务器侧接入链路容量 $R_s$、以及骨干链路上该连接分得的容量 $R/10$。
- in practice: $R_c$ or $R_s$ is often bottleneck。实际中瓶颈常常是 $R_c$ 或 $R_s$，即客户机侧或服务器侧的接入链路。

由 $\min$ 关系可直接得到的两点（课件未写出）：

1. 当 $R/10$ 同时小于 $R_c$ 与 $R_s$ 时，瓶颈在骨干链路，单条连接的端到端吞吐量为 $R/10$，10 条连接合计占用 $10\times (R/10)=R$，骨干链路被这 10 条连接占满；
2. 当 $R_c$ 或 $R_s$ 小于 $R/10$ 时，瓶颈在接入链路，此时骨干链路不会被这 10 条连接占满。

课件未给出该场景的具体数值算例，这里不构造课件之外的数值。课件页脚另附提示 *\* Check out the online interactive exercises for more examples: http://gaia.cs.umass.edu/kurose_ross/*。

课件页 1-62 为 Chapter 1 roadmap 定位页，列出本章条目：What *is* the Internet?、What *is* a protocol?、Network edge: hosts, access network, physical media、Network core: packet/circuit switching, internet structure、Performance: loss, delay, throughput、Security\*、Protocol layers, service models、History；该页把 Security 一项加粗，作为后续内容的索引页。以上内容对应其中 Performance 一项，以下进入 Security 一项。

---

## 1.6 网络安全（Network Security）

### 1.6.1 互联网的安全设计背景（课件页 1-63、1-64）

课件页 1-63 与 1-64 的内容完全相同（重复页），合并叙述。

课件原文：Internet not originally designed with (much) security in mind（互联网最初设计时基本没有考虑安全性）。给出三条依据：

1. original vision: "a group of mutually trusting users attached to a transparent network"，最初的设想是“一群互相信任的用户连接在一个透明的网络上”；
2. Internet protocol designers playing "catch-up"，互联网协议设计者一直在“追赶”；
3. security considerations in all layers!，安全性考虑要出现在所有层次上。

课件接着列出现在需要考虑的问题（We now need to think about）：

1. how bad guys can attack computer networks，攻击者会怎样攻击计算机网络；
2. how we can defend networks against attacks，我们怎样防御网络受到的攻击；
3. how to design architectures that are immune to attacks，怎样设计对攻击免疫的体系结构。

### 1.6.2 攻击方式一：分组嗅探（Packet "Sniffing"，课件页 1-65）

课件原文使用 packet sniffing（分组嗅探）这一名称，并给出两个成立条件：

1. broadcast media (shared Ethernet, wireless)：广播式介质，例如共享式以太网（shared Ethernet）与无线介质；
2. promiscuous network interface reads/records all packets (e.g., including passwords!) passing by：处于混杂模式（promiscuous mode）的网络接口会读取并记录所有经过它的分组，例如包括口令。

**【源图，课件页 1-65】** A 与 B 连在共享介质上（图中画有共享链路与集线器），C 也接在同一共享介质上；从 B 发出、目的为 A 的分组在图中用 `src:B | dest:A | payload` 三个字段表示，C 处用箭头标出从共享介质上截取到该分组。即同一广播介质上的任何一台处于混杂模式的主机都能收到并记录目的地址不是自己的分组。

课件提示：Wireshark software used for our end-of-chapter labs is a (free) packet-sniffer，课后实验使用的 Wireshark 就是一个免费的嗅探程序。

### 1.6.3 攻击方式二：伪造身份（IP Spoofing，课件页 1-66）

课件原文定义：IP spoofing: injection of packet with false source address，即注入源地址为伪造地址的分组。

**【源图，课件页 1-66】** A 与 B 连在共享介质上，攻击者 C 也接在同一介质上；C 发出的分组字段为 `src:B | dest:A | payload`，即把源地址伪造成 B 的地址、目的地址填 A 的地址，箭头指向 A。结果是 A 收到的分组在源地址字段上显示为 B，而实际发送者是 C。

由此可直接看出（课件未展开）：接收方仅凭分组头中的源地址字段无法判断真实发送者，源地址字段可以被任意填写。

### 1.6.4 攻击方式三：拒绝服务（Denial of Service，课件页 1-67）

课件原文定义：Denial of Service (DoS): attackers make resources (server, bandwidth) unavailable to legitimate traffic by overwhelming resource with bogus traffic，即攻击者用伪造的业务量压垮资源（服务器、带宽），使合法业务无法使用该资源。

课件给出的攻击步骤（原文）：

1. select target，选定目标；
2. break into hosts around the network (see botnet)，攻入网络中各处的若干主机（见 botnet，僵尸网络）；
3. send packets to target from compromised hosts，从被攻陷的主机向目标发送分组。

**【源图，课件页 1-67】** 中央是一台标注为 target（目标）的服务器，周围多台被攻陷的主机各自画出指向目标的箭头，另有未受控的主机不参与攻击。图中标注 *see botnet* 指向被攻陷主机的集合。

### 1.6.5 防御手段（Lines of Defense，课件页 1-68）

课件列出的防线如下（定义文字取自课件原文）：

| 防线 | 课件原文定义 | 课件给出的说明 |
|---|---|---|
| authentication（认证） | proving you are who you say you are，证明使用者确实是其声称的身份 | cellular networks provides hardware identity via SIM card; no such hardware assist in traditional Internet：蜂窝网络通过 SIM 卡提供硬件身份，传统互联网没有这种硬件支持 |
| confidentiality（机密性） | via encryption，通过加密实现 | — |
| integrity checks（完整性校验） | digital signatures prevent/detect tampering，用数字签名防止或检测篡改 | — |
| access restrictions（访问限制） | password-protected VPNs，带口令保护的 VPN | — |
| firewalls（防火墙） | specialized "middleboxes" in access and core networks，接入网与核心网中的专用“中间盒” | off-by-default: filter incoming packets to restrict senders, receivers, applications（默认关闭：过滤进入的分组，以限制发送方、接收方与应用）；detecting/reacting to DOS attacks（检测并响应 DoS 攻击） |

课件在本页末尾标注：… lots more on security (throughout, Chapter 8)，即安全内容贯穿全书，并在第 8 章集中展开。

按课件页 1-62 的 roadmap 顺序，Security 一项之后的条目为 Protocol layers, service models（协议层次与服务模型），随后是 History；这两项不在本 PDF 的 36 页之内。
