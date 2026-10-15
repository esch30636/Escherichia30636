# 计算机网络 —— 网络层（Chapter 5: Network Layer）

> **原始 PDF**：`D:\Escherichia30636\计算机网络\Chapter5a The network layer.pdf`
> **PDF 总页数**：81 页
> **整理日期**：2026-10-15
> 本笔记按原课件的章—节—小节顺序连续组织：5.1 引言、5.2 虚电路与数据报网络、5.3 路由器内部结构、5.4 路由算法、5.5 Internet 中的路由，最后是章末习题。原课件页脚编号为 5a-NN，正文中以「原 PDF 第 N 页」标注图示与数据的来源页。课件目录页列出的 5.6 IP 内容（IPv4 数据报格式、IPv4 编址、IP 分片、ICMP、IPv6）不在本课件的页码范围内。
>
> 课件本身的章目标是两类：一类是理解网络层服务背后的原理（understand principles behind network layer services），包含网络层服务模型、转发与路由的对比、路由器的工作原理、路由即路径选择、以及规模的应对；另一类是在 Internet 中的实例化与实现（instantiation and implementation in the Internet）。全章目录为 5.1 Introduction；5.2 Virtual circuit and datagram networks；5.3 What's inside a router?；5.4 Routing algorithms（下分 Dijkstra's algorithm、Broadcast routing、Link state、Distance vector、Hierarchical routing）；5.5 Routing in the Internet；5.6 IP: Internet protocol（下分 IPv4 Datagram format、IPv4 addressing、IP fragment、NAT、ARP、ICMP、IPv6）。第 2 页目录的 5.6 子项含 NAT 与 ARP，而第 9、18、28、63 页的目录页子项未列这两项，属课件自身目录页的版本差异，此处按第 2 页的完整列表记录。

---

## 5.1 引言（Introduction）

### 5.1.1 网络层的职责与所处层次

网络层的核心任务是把分组从发送主机传输到接收主机（transport packet from sending to receiving hosts）。网络层协议存在于每一台主机和每一台路由器中（network layer protocols in every host, router），这一点与只存在于端系统中的应用层、传输层协议不同。路由器会检查所有经过它的 IP 数据报的首部字段（router examines header fields in all IP datagram passing through it），因此网络层必须在网络核心的设备上实现，而不只是端系统的功能。

这一分工在课件给出的分层结构图（原 PDF 第 3 页图）中可以读出：端系统具有五层——application、transport、network、data link、physical；中间的路由器只具有三层——network、data link、physical，其中 network 层被标为路由器实现的最高层。端系统与路由器之间、路由器与路由器之间通过 data link 层与 physical 层相连，网络层的协议实体在链路上逐跳传递数据报。需要区分两种「连接」的所在位置：传输层的连接只涉及两个端系统，而网络层的协议实体同时存在于端系统与路由器中，因此网络层可以在网络核心中维持逐跳的处理逻辑。

### 5.1.2 网络层的两个关键功能：路由与转发

网络层有两个关键功能（two key network-layer functions）。

**路由（routing）**：确定分组从源到目的地所走的路径（determine route taken by packets from source to dest.）。完成这一功能依靠路由算法（routing algorithms）。

**转发（forwarding）**：把分组从路由器的输入移动到适当的输出（move packets from router's input to appropriate router output）。转发是路由器内部对单个分组所作的局部动作。

除这两个功能外，课件还列出**连接建立（connection setup）**：某些网络体系结构要求在数据流动之前，沿着路径完成路由器上的连接建立（some network architectures require router connection setup along path before data flows）。连接建立不是所有网络体系结构都必需的，只有虚电路类体系结构才需要，这直接引出了 5.2 节虚电路与数据报网络的分野。

课件在本页（原 PDF 第 4 页）用一段类比说明路由与转发的关系，即把路由对应为从源到目的地规划行程、把转发对应为通过单个交叉路口；此处仅记录该表述的存在与所指，其准确含义以本节与 5.1.3 中按转发表查用和路由计算时间尺度的说明为准。

### 5.1.3 路由与转发的相互作用（Interplay between routing and forwarding）

课件以一张对照图（原 PDF 第 5 页图）说明路由与转发如何配合。图的上部是一个路由器内部的结构：路由算法（routing algorithm）的输出送往本地转发表（local forwarding table）。本地转发表是一个两列的映射表，左列为首部值（header value），右列为输出链路（output link），四条表项为：

| 首部值（header value） | 输出链路（output link） |
|---|---|
| 0100 | 3 |
| 0101 | 2 |
| 0111 | 2 |
| 1001 | 1 |

图的下部是一个由路由器节点组成的网络，其中一个路由器被放大显示其内部的转发表。一个到达分组的首部中的值（value in arriving packet's header）标为二进制串 `0111`，从该路由器的输入链路进入。查表得首部值 `0111` 对应输出链路 2，因此该分组从输出链路 2 转发出去。

这张图表达的关系是：路由算法负责生成和更新转发表的内容，转发负责在每一个到达的分组上使用该表。表的内容由路由算法在后台计算，表的查用发生在每一个分组的处理过程中，两者的时间尺度不同——路由计算是较慢的过程，转发是逐个分组的快速动作。这一区分在 5.3 节路由器结构中再次出现，表现为控制平面（软件，毫秒级）与数据平面（硬件，纳秒级）的划分。

### 5.1.4 网络服务模型（Network service model）

课件提出的问题是：对于从发送方到接收方传输分组的这条「通道」，应当采用什么服务模型（what service model for "channel" transporting packets from sender to receiver?）。课件把这一层问题称为网络层提供的最重要的抽象（the most important abstraction provided by network layer）。

课件列出网络层服务抽象（service abstraction）中可供选择的五项能力：

- 保证带宽（guaranteed bandwidth）？
- 保持分组间定时，即无抖动（preservation of inter-packet timing, no jitter）？
- 无丢失交付（loss-free delivery）？
- 按序交付（in-order delivery）？
- 向发送方反馈拥塞信息（congestion feedback to sender）？

这五项构成评价一个网络层服务模型的维度。课件进一步指出，网络层最重要的抽象归结为一个选择：虚电路还是数据报（virtual circuit or datagram?）。这一问题在 5.2 节展开。

### 5.1.5 网络层服务模型对照表

课件给出网络体系结构与其服务模型的对照表（原 PDF 第 7 页表），表中 ATM 为异步传输模式（Asynchronous Transfer Mode）。「保证（Guarantees?）」一栏下分带宽（Bandwidth）、丢失（Loss）、顺序（Order）、定时（Timing）四项，拥塞反馈（Congestion feedback）单列一栏。完整表格如下：

| Network Architecture | Service Model | Bandwidth | Loss | Order | Timing | Congestion feedback |
|---|---|---|---|---|---|---|
| Internet | best effort（尽力而为） | none | no | no | no | no（inferred via loss，通过丢失推断） |
| ATM | CBR | constant rate（恒定速率） | yes | yes | yes | no congestion |
| ATM | VBR | guaranteed rate（保证速率） | yes | yes | yes | no congestion |
| ATM | ABR | guaranteed minimum（保证最小值） | no | yes | no | yes |
| ATM | UBR | none | no | yes | no | no |

逐行说明其含义。Internet 的 best effort 模型在任何一维上都不作保证：带宽不保证，丢失不保证避免，顺序不保证，定时不保证；拥塞反馈一栏为 no（inferred via loss），即网络层本身不提供显式的拥塞反馈，发送方只能从分组丢失这一现象间接推断拥塞的发生。ATM 的 CBR（Constant Bit Rate，恒定比特率）保证恒定速率，同时保证不丢失、保证顺序、保证定时，但不提供拥塞反馈。ATM 的 VBR（Variable Bit Rate，可变比特率）保证速率，同样保证不丢失、顺序与定时，也不提供拥塞反馈。ATM 的 ABR（Available Bit Rate，可用比特率）保证最小带宽值，不保证不丢失，保证顺序，不保证定时，并且提供拥塞反馈。ATM 的 UBR（Unspecified Bit Rate，未指定比特率）不保证带宽，不保证不丢失，保证顺序，不保证定时，也不提供拥塞反馈。表中 Loss 一栏填 yes 表示该服务模型保证不丢失，填 no 表示不保证；ABR 行的 Loss 为 no，即 ABR 不保证无丢失。

### 5.1.6 网络层的连接服务与无连接服务

课件把网络层服务划分为两类（原 PDF 第 8 页）：

- 数据报网络提供网络层无连接服务（datagram network provides network-layer connectionless service）。
- 虚电路网络提供网络层连接服务（VC network provides network-layer connection service）。

课件指出，这两类服务与传输层服务可以对照（analogous to the transport-layer services），但有三点关键区别：

- **服务范围（service）**：网络层提供的是主机到主机（host-to-host）的服务；传输层的连接服务（如 TCP）是进程到进程的，网络层的服务粒度是主机到主机。
- **没有选择（no choice）**：网络层只提供上述两类服务中的一种，由网络自身决定（network provides one），端系统无法像在传输层那样在面向连接与无连接之间自由选择；传输层中应用可以在 TCP 与 UDP 之间选择，网络层则不存在这种选择。
- **实现位置（implementation）**：网络层服务的实现位于网络核心（in network core），即由路由器实现；传输层服务的实现位于端系统。

---

## 5.2 虚电路与数据报网络（Virtual circuit and datagram networks）

### 5.2.1 虚电路的基本性质

课件对虚电路（virtual circuits）的第一个说明框引用了一句话（原 PDF 第 10 页）：source-to-dest path behaves much like telephone circuit，其含义有两点限定——从性能角度（performance-wise），以及在源到目的路径上网络所执行的动作（network actions along source-to-dest path）。这是课件原文的表述。

虚电路的性质由以下几条构成。其一是三个阶段：呼叫建立 → 数据流动 → 呼叫拆除（call setup → data flow → call teardown），三者有确定的先后顺序，数据流动只在呼叫建立完成之后开始，拆除发生在数据流动结束之后。其二是每个分组携带 VC 标识符（VC identifier），而不是目的主机 ID（each packet carries VC identifier, not destination host ID），因此路径上转发分组时不需要读取目的地址。其三是源到目的路径上的每一台路由器为每条经过的连接维持「状态」（every router on source-dest path maintains "state" for each passing connection）；与此对照，传输层的连接只涉及两个端系统（transport-layer connection only involved two end systems），中间的路由器并不感知该传输层连接，虚电路的状态则是每一台中间路由器都要维持的。其四是链路与路由器的资源（带宽、缓冲区）可以被分配给该虚电路（link, router resources, bandwidth, buffers, may be allocated to VC），课件注明这一分配的目的是获得类似电路的性能（to get circuit-like perf.）。

### 5.2.2 虚电路的构成与实现（VC Implementation）

课件给出一个 VC 由三部分构成（原 PDF 第 11 页）：

1. 从源到目的地的路径（path from source to destination）。
2. VC 号，路径上每条链路各有一个号（VC numbers, one number for each link along path）。
3. 路径上各路由器转发表中的表项（entries in forwarding tables in routers along path）。

对应的两条转发规则是：属于某个 VC 的分组携带的是 VC 号，而不是目的地址（packet belonging to VC carries VC number, rather than dest. address）；VC 号在每条链路上可以改变（VC number can be changed on each link），新的 VC 号来自转发表（new VC number comes from forwarding table）。

「每条链路各有一个 VC 号」这一设计与「分组携带 VC 号」配合，使得同一个 VC 在不同的链路上可以用不同的编号，编号只需要在单条链路上唯一，不必全网唯一，这正是虚电路可以本地化编号、从而缩小号空间的原因。

### 5.2.3 虚电路转发表示例

课件给出一台路由器的转发表与对应的虚电路示意图（原 PDF 第 12 页图）。图中画出一条从左侧主机出发、经过若干路由器到达右侧主机的链路，链路上标出的 VC 号为 12、22、32，路由器上标出接口号 1、2、3。

「西北路由器（northwest router）中的转发表」完整内容如下：

| Incoming interface（入接口） | Incoming VC #（入 VC 号） | Outgoing interface（出接口） | Outgoing VC #（出 VC 号） |
|---|---|---|---|
| 1 | 12 | 3 | 22 |
| 2 | 63 | 1 | 18 |
| 3 | 7 | 2 | 17 |
| 1 | 97 | 3 | 87 |
| … | … | … | … |

表中前四行是完整表项，最后一行的省略号表示该表还有更多表项。查阅该表的方法：一个分组若从入接口 1 进入且首部中的 VC 号为 12，则从出接口 3 转出，并在转出时把 VC 号改写为 22；从入接口 2 进入且 VC 号为 63 的分组，从出接口 1 转出并把 VC 号改写为 18；从入接口 3 进入且 VC 号为 7 的分组，从出接口 2 转出并把 VC 号改写为 17；从入接口 1 进入且 VC 号为 97 的分组，从出接口 3 转出并把 VC 号改写为 87。

图中标注的 VC 号 12 与 22 与表中第一行的入 VC 号 12、出 VC 号 22 一致，说明图中从源出发后的第一跳使用 VC 号 12，经该路由器后改为 22；图中还出现 VC 号 32，位于更靠后的链路上。课件在该页底部用方框强调：路由器维持连接状态信息（routers maintain connection state information!）。这里的状态信息就是上表的全部内容——入接口、入 VC 号、出接口、出 VC 号四元组，每一条经过的虚电路都要在各路由器中占用一条表项。

### 5.2.4 虚电路的呼叫建立过程与信令协议（signaling protocols）

信令协议用于建立、维护和拆除虚电路（used to setup, maintain, teardown VC）。课件指出信令协议的使用范围：用于 ATM、frame-relay（帧中继）、X.25（used in ATM, frame-relay, X.25），而不用于今天的 Internet（not used in today's Internet）。

课件给出呼叫建立过程的时序图（原 PDF 第 13 页图）。图中左右两侧各是一个端系统，各具有 application、transport、network、data link、physical 五层，其中 network 层被高亮。六个步骤按编号顺序为：

1. Initiate call（发起呼叫）。
2. incoming call（有呼入）。
3. Accept call（接受呼叫）。
4. Call connected（呼叫已连接）。
5. Data flow begins（数据流开始）。
6. Receive data（接收数据）。

图中两组方向相反的控制消息线表示两个方向的消息传递：步骤 1 至 4 是呼叫建立阶段，控制消息在两侧端系统之间传递；步骤 5 的数据流开始与步骤 6 的接收数据是数据流动阶段，此时数据沿已建立的虚电路从左侧端系统流向右侧端系统。数据流动只在步骤 4「呼叫已连接」之后开始，与 5.2.1 中「呼叫建立 → 数据流动 → 呼叫拆除」的三阶段顺序一致。

### 5.2.5 数据报网络：Internet 模型（Datagram networks: the Internet model）

数据报网络的性质与虚电路相反（原 PDF 第 14 页）：

- 网络层没有呼叫建立（no call setup at network layer）。
- 路由器不保存端到端连接的状态（routers: no state about end-to-end connections）。课件进一步说明：网络层不存在「连接」这一概念（no network-level concept of "connection"）。
- 分组通常使用目的主机 ID 来路由（packets typically routed using destination host ID）。由此得到一个直接后果：同一对源与目的地之间的分组可能走不同的路径（packets between same source-dest pair may take different paths）。

课件给出的数据报网络时序图中同样有左右两个五层端系统，network 层高亮，但只包含两个步骤：

1. Send data（发送数据）。
2. Receive data（接收数据）。

图中中间的路由器网络里，各个分组以小方块表示并沿着不同的通路前进，不同分组经过的中间路由器不完全相同，这与「同一对源与目的地之间的分组可能走不同的路径」这一性质对应。与第 13 页的虚电路图相比，数据报图没有呼叫建立与拆除的控制消息交换，只有数据的发送与接收。

### 5.2.6 数据报网络的转发表与最长前缀匹配

数据报网络中路由器使用的转发表以目的地址范围为索引。课件先用一页给出转发表的结构（原 PDF 第 15 页）。该页注明有 4 billion possible entries（40 亿条可能表项），即按完整 IP 地址枚举所能得到的表项数量，说明不可能为每一个地址单独建立一条表项，必须按地址范围聚合。该页给出的转发表完整内容如下：

| Destination Address Range（目的地址范围） | Link Interface（链路接口） |
|---|---|
| `11001000 00010111 00010000 00000000` 到 `11001000 00010111 00010111 11111111` | 0 |
| `11001000 00010111 00011000 00000000` 到 `11001000 00010111 00011000 11111111` | 1 |
| `11001000 00010111 00011001 00000000` 到 `11001000 00010111 00011111 11111111` | 2 |
| otherwise（其他） | 3 |

把上述地址写成点分十进制形式并核对范围边界：第一行范围为 200.23.16.0 到 200.23.23.255，第三字节从 `00010000`（十进制 16）到 `00010111`（十进制 23）；第二行范围为 200.23.24.0 到 200.23.24.255，第三字节固定为 `00011000`（十进制 24）；第三行范围为 200.23.25.0 到 200.23.31.255，第三字节从 `00011001`（十进制 25）到 `00011111`（十进制 31）；其余目的地址落在接口 3。

课件随后把上表改写为带通配符的前缀形式，并给出最长前缀匹配规则（原 PDF 第 16 页）。**最长前缀匹配（longest prefix matching）**的规则是：为给定的目的地址查找转发表项时，使用与该目的地址匹配的最长的地址前缀（when looking for forwarding table entry for given destination address, use longest address prefix that matches destination address）。改写后的表为：

| Destination Address Range | Link interface |
|---|---|
| `11001000 00010111 00010*** *********` | 0 |
| `11001000 00010111 00011000 ********` | 1 |
| `11001000 00010111 00011*** *********` | 2 |
| otherwise | 3 |

表中 `*` 表示该比特位不作要求。将三行前缀写成前缀长度：第 1 行固定了前 21 位（前两个字节 16 位，加第三字节的前 5 位 `00010`），即前缀 200.23.16.0/21，覆盖第三字节 `00010000` 至 `00010111`，即 200.23.16.0 至 200.23.23.255；第 2 行固定了前 24 位（`00011000`），即前缀 200.23.24.0/24，仅覆盖 200.23.24.0 至 200.23.24.255；第 3 行固定了前 21 位（`00011`），即前缀 200.23.24.0/21，覆盖第三字节 `00011000` 至 `00011111`，即 200.23.24.0 至 200.23.31.255。

这里出现一处必须指明的重叠：前缀 200.23.24.0/24 完全被前缀 200.23.24.0/21 所包含。目的地址第三字节为 `00011000` 的分组同时匹配第 2 行与第 3 行，此时按最长前缀匹配规则取前缀更长的第 2 行；而第 15 页表把它单独列为接口 1、并把 200.23.25.0 至 200.23.31.255 列为接口 2，正是这一重叠关系在无通配符写法下的表现，第 2 行的单独列出把 200.23.24.0/24 从第 3 行的范围中挖了出来。

课件给出的两个例子如下，逐位计算。

#### 例 1：DA = `11001000 00010111 00010110 10100001`（问用哪个接口）

与第 1 行前缀 `00010` 比较：第三字节 `00010110` 的前 5 位为 `00010`，与 `00010` 相同，符合；末 3 位 `110` 与 `***` 不约束，故匹配第 1 行（/21）。与第 2 行前缀 `00011000` 比较：第三字节 `00010110` 与 `00011000` 不相等（第 5 位 `1` 对 `1` 相同，第 6 位 `0` 对 `1` 不同），不匹配第 2 行。与第 3 行前缀 `00011` 比较：第三字节 `00010110` 的前 5 位为 `00010`，与 `00011` 不同，不匹配第 3 行。只有一个匹配项，因此查表结果为**接口 0**。

用点分十进制复核：DA = 200.23.22.161，落在 200.23.16.0 至 200.23.23.255 之内，接口 0，与第 15 页表第一行一致。

#### 例 2：DA = `11001000 00010111 00011000 10101010`（问用哪个接口）

与第 1 行前缀 `00010` 比较：第三字节 `00011000` 的前 5 位为 `00011`，与 `00010` 不同，不匹配第 1 行。与第 2 行前缀 `00011000` 比较：第三字节 `00011000` 与 `00011000` 完全相同，匹配第 2 行（/24）。与第 3 行前缀 `00011` 比较：第三字节 `00011000` 的前 5 位为 `00011`，与 `00011` 相同，匹配第 3 行（/21）。同时匹配第 2 行与第 3 行，比较前缀长度：第 2 行为 24 位，第 3 行为 21 位，取较长的第 2 行，因此查表结果为**接口 1**。

用点分十进制复核：DA = 200.23.24.170，落在 200.23.24.0 至 200.23.24.255 之内，按第 15 页表为接口 1，与按第 16 页表的最长前缀匹配结果一致。

这一对例子说明：仅列出地址范围而不加最长前缀规则会产生二义性（例 2 同时落在两条表项中），最长前缀匹配规则用于消除该二义性，代价是查表不能只做一次全等或区间比较，而要在所有匹配的前缀中选出最长的一个。

### 5.2.7 数据报与虚电路的选择原因

课件用一张左右对照页说明 Internet 选择数据报、ATM 选择虚电路的原因（原 PDF 第 17 页）。

Internet 一侧的情形是：应用场景为在计算机之间交换数据（data exchange among computers），这类业务是弹性服务，没有严格的定时要求（"elastic" service, no strict timing req.）；链路类型多（many link types），各种链路特性不同（different characteristics），因此难以在各链路上提供统一的服务（uniform service difficult）；端系统是智能的（"smart" end systems，即计算机），能够适应网络状况，能够执行控制与差错恢复（can adapt, perform control, error recovery）。由此得到的设计结论是：网络内部简单，复杂性放在边缘（simple inside network, complexity at "edge"）。

ATM 一侧的情形是：ATM 从电话业务演化而来（evolved from telephony）；承载的是人类对话（human conversation），具有严格的定时与可靠性要求（strict timing, reliability requirements），需要保证服务（need for guaranteed service）；端系统是简单的（"dumb" end systems），即电话机。由此得到的设计结论是：复杂性放在网络内部（complexity inside network）。

两侧的差别可以作为一条对照：把复杂功能放在网络边缘还是网络核心，决定了网络层采用数据报还是虚电路。Internet 把差错恢复与控制交给端系统的智能设备，网络核心只做尽力而为的转发，因此不需要为每条连接在路由器中维持状态，也就不需要虚电路；ATM 面向的是定时与可靠性要求严格、端系统能力弱的人声业务，因此需要网络内部为保证服务承担更多工作，即需要虚电路。

---

## 5.3 路由器内部结构（What's inside a router?）

### 5.3.1 路由器体系结构总览

课件给出通用路由器体系结构的高层视图（原 PDF 第 19 页图）。图中四个组成部分为：

- 路由处理器（routing processor）；
- 高速交换结构（high-speed switching fabric）；
- 路由器输入端口（router input ports）；
- 路由器输出端口（router output ports）。

连接关系为：输入端口接到交换结构，交换结构接到输出端口，路由处理器与交换结构之间有双向箭头相连；另有一条从路由处理器指向输入端口的控制线，表示路由处理器向输入端口下发转发表内容。

课件用一条水平虚线把图中各部件的运作时间尺度分为两层：

- 虚线上方是**路由与管理控制平面（routing, management control plane）**，以软件实现，运行在毫秒级时间尺度（operates in millisecond time frame），该平面包含路由处理器。
- 虚线下方是**转发数据平面（forwarding data plane）**，以硬件实现，运行在纳秒级时间尺度（operates in nanosecond timeframe），该平面包含输入端口、交换结构与输出端口。

课件用红框标出路由处理器与交换结构，用于强调：控制平面决定交换结构如何被配置与路由表如何生成，数据平面负责实际搬运分组。两个平面的时间尺度相差约六个数量级（毫秒与纳秒），这解释了为什么转发表要下推到输入端口由硬件查用，而不是每个分组都送到路由处理器处理。

### 5.3.2 输入端口的功能

课件给出输入端口的内部功能图（原 PDF 第 20 页图）。分组自左向右经过四个模块：

1. **line termination（线路端接）**，对应物理层：比特级接收（physical layer: bit-level reception）。
2. **data link processing (protocol, decapsulation)（数据链路处理：协议、解封装）**，对应数据链路层，例如以太网（data link layer: e.g., Ethernet）。
3. **lookup, forwarding, queueing（查找、转发、排队）**，该模块内画有一列竖直的短条，表示队列。
4. 之后到达 **switch fabric（交换结构）**。

课件把交换机部分称为**分散式交换（decentralized switching）**，并给出三条说明。第一，给定数据报的目的地址，使用存放在输入端口存储器中的路由表查出输出端口（given datagram dest., lookup output port using routing table in input port memory）；关键之处是路由表存放在输入端口自身的存储器中，输入端口的硬件可以独立完成查找，不必经由路由处理器，这就是「分散式」的含义。第二，目标是让输入端口处理在线速下完成（goal: complete input port processing at 'line speed'）；线速指该端口所在链路的传输速率，输入端口必须以不低于到达速率的处理速度完成每分组处理，否则分组会积压。第三，排队：如果数据报到达的速度快于向交换结构转发的速度，则在输入端口队列中排队（queuing: if datagrams arrive faster than forwarding rate into switch fabric），排队由第 3 个模块内的队列承担。

### 5.3.3 交换结构（Switching fabrics）

交换结构位于路由器的输入端口与输出端口之间，其任务是把已经确定输出端口的数据报从输入端口一侧送到输出端口一侧。课件按实现方式把路由器分为三类：经存储器交换（switching via memory）、经总线交换（switching via bus）、经互连网络交换（switching via interconnection network）。三者的差别在于数据报经过的物理通路不同，因而速度上限的成因不同。

#### 经存储器交换（Switching via memory）

第一代路由器（first generation routers）的性质如下：它们是传统计算机，交换动作处于 CPU 的直接控制之下；数据报被复制到系统的存储器（system memory）中；速度受存储器带宽限制，每个数据报需要 2 次总线穿越（2 bus crossings per datagram）。「2 次总线穿越」的构成是：数据报先从输入端口经系统总线写入存储器，记为第 1 次；随后从存储器经系统总线读出送往输出端口，记为第 2 次。因此即使输入端口和输出端口本身速率很高，单个数据报也要两次占用同一条系统总线，可交换的吞吐量被存储器带宽与系统总线带宽共同限制。课件给出的器件实例为：后来的路由器例如 Cisco Catalyst 8500，图中标注为 Retired（已退役）。该页图的结构为：左侧是输入端口（图中注明 e.g., Ethernet），中间是存储器，右侧是输出端口（同样注明 e.g., Ethernet），三者都连接在下方一条标注为 system bus 的系统总线上。

#### 经总线交换（Switching via bus）

数据报从输入端口经一条共享总线（shared bus）到达输出端口。存在总线争用（bus contention）：交换速度受总线带宽限制，原因是一条总线在同一时刻只能承载一个数据报的传输，多个输入端口同时有数据报要送往不同输出端口时，只能依次占用总线。课件给出的数据是：32 Gbps 总线、Cisco 5600，该配置对访问路由器（access routers）与企业路由器（enterprise routers）是足够的速度，但不适用于区域路由器或骨干路由器（not regional or backbone）。该页图的结构为：三个输入端口分别标 A、B、C，三个输出端口分别标 X、Y、Z，中间是一条纵向的共享总线，标注为 bus，图中画出一个数据报从输入端口经该总线流向输出端口。

#### 经互连网络交换（Switching via interconnection network）

这一设计目的是克服总线带宽的限制。使用的结构包括 Banyan 网络、交叉开关（crossbar）以及其他互连网络；这些结构最初是为了在多处理机（multiprocessor）中连接处理器而提出的。先进设计（advanced design）的做法是：把数据报分片（fragmenting）为固定长度的信元（fixed length cells），再让信元通过交换结构，这样交换结构内部以定长信元为单位作并行调度，不再是整条数据报独占一条通路。课件给出的器件实例：Cisco 12000 通过互连网络交换 60 Gbps。该页图画出交叉开关（crossbar）的结构：三条输入通路由横向导线构成，三条输出通路由纵向导线构成，横竖导线交叉处为可连通的交叉点，图中画出一个数据报占据其中一条横向通路、跨过若干交叉点后向下进入某一条输出通路，输出端串接缓冲单元后再送往输出。

三类交换结构的对照如下：

| 交换结构 | 数据报经过的通路 | 速度限制来源 | 课件给出的器件实例 |
| --- | --- | --- | --- |
| 经存储器交换 | 输入端口 → 系统总线 → 存储器 → 系统总线 → 输出端口 | 存储器带宽，每个数据报 2 次总线穿越 | 第一代路由器；Cisco Catalyst 8500（已退役） |
| 经总线交换 | 输入端口 → 共享总线 → 输出端口 | 总线带宽，存在总线争用 | 32 Gbps 总线，Cisco 5600 |
| 经互连网络交换 | 输入端口 → 互连网络（Banyan、crossbar 等）→ 输出端口 | 不再由单条总线带宽决定，可用分片为定长信元的方式提高并行度 | Cisco 12000，60 Gbps |

### 5.3.4 输出端口（Output ports）

输出端口的构成顺序为：交换结构（switch fabric）→ 数据报缓冲（datagram buffer，图中该处标注 queueing）→ 链路层协议（link layer protocol，图中标注 (send)）→ 线路终端（line termination）→ 输出线路。围绕这一结构，课件（原 PDF 第 25 页）给出两个与排队有关的事实：

- 缓冲（buffering）的必要条件：当数据报从交换结构到达的速率快于输出线路的传输速率时，必须缓冲。
- 调度规则（scheduling discipline）的作用：在已排队的数据报中决定哪一个被发送。

课件用方框强调的后果是：数据报（包）可能因拥塞、缺少缓冲而被丢失（datagram (packets) can be lost due to congestion, lack of buffers）。课件用方框强调的第二个话题是优先级调度（priority scheduling）——谁获得最好性能，以及网络中立性（network neutrality）：调度规则不仅决定时延分配，也决定不同数据流之间的性能差异。

### 5.3.5 输入端口排队与队头阻塞（Input port queuing）

当交换结构的速度低于各输入端口合起来的速度（课件原文为 Fabric slower that input ports combined，此处 that 是课件文本的笔误，应为 than），输入队列上就可能出现排队。其后果是排队时延，以及因输入缓冲溢出造成的丢失。

**队头阻塞（Head-of-the-Line blocking，HOL blocking）**的定义是：位于队列前端的数据报阻止了队列中其他数据报向前移动。课件（原 PDF 第 26 页）用两幅图说明其产生过程，两幅图都画有三个输入端口队列与三个输出端口，中间是交换结构。

- 左图（$t$ 时刻）：两个数据报分别位于两个不同输入队列的前端，且都要送往同一个输出端口；同一时刻只能传输其中一个，另一个被阻塞。图中注明 output port contention: only one red datagram can be transferred. lower red packet is blocked。
- 右图（一个数据报时间之后，one packet time later）：后一个数据报所在的输入队列中，另一个数据报排在被阻塞者之后；被阻塞的数据报不能向前移动，其后的数据报也就无法被交换，图中注明 green packet experiences HOL blocking。

因此 HOL 阻塞的本质是：输入队列是先进先出的单一队列，即使队首数据报所要的输出端口暂时不可用，队列中其他数据报即使其输出端口空闲也不能被取出，输入端口因此产生本可避免的时延。

### 5.3.6 输出端口排队（Output port queueing）

当经交换结构到达的速率超过输出线路速率（课件原文为 exceeeds、ouput，为课件文本笔误，应为 exceeds、output）时，需要缓冲；其后果是排队（时延），以及因输出端口缓冲溢出造成的丢失。课件（原 PDF 第 27 页）用两幅图说明输出端口缓冲的积累过程。

- 左图（at $t$，$t$ 时刻）：从输入到输出的数据报多于该时刻输出端口能发送的量，输出端口处已有一个数据报在缓冲中等待发送。
- 右图（one packet time later，一个数据报时间之后）：输出端口缓冲中出现两个数据报堆积，表示到达速率持续高于输出线路速率时缓冲占用增加。

---

## 5.4 路由算法（Routing algorithms）

### 5.4.1 路由与转发的交互

课件在进入路由算法之前再次给出路由算法与转发动作的关系图（原 PDF 第 29 页，与 5.1.3 的图相同）。路由算法处于上方，它计算出本地的转发表；转发表为两列，左列是首部值（header value），右列是输出链路（output link），表中四行与 5.1.3 给出的完全相同，即 `0100`→3、`0101`→2、`0111`→2、`1001`→1。图中下半部分是一个由路由器节点组成的网络，其中画出若干路由器各带一份同样的转发表小框，并标出 value in arriving packet's header 指向一个首部字段二进制值为 `0111` 的数据报，它沿标有 1 的链路进入某个路由器。沿首部值 `0111` 查表得到输出链路为 2，因此该数据报从该路由器的输出链路 2 转发出去。这一页再次说明：路由算法负责生成并更新转发表的内容（全局的、较慢的过程），转发则是逐包按首部值查表并送往指定输出链路的动作（本地的、逐包发生的过程）。

### 5.4.2 路由问题的图抽象（Graph abstraction）

#### 5.4.2.1 路由协议的目标与图抽象的基本设定

课件把路由协议（routing protocol）的目标写在方框中：确定从源到目的、穿过网络的好路径，即路由器序列（sequence of routers）。对好路径的解释是：好路径通常指最小代价路径（minimum cost path），其他定义也是可能的（other def's possible）。

图抽象（graph abstraction）用于路由算法的设定为：图的节点（nodes）是路由器；图的边（edges）是物理链路；链路代价（link cost）可以是时延、费用（$ cost）或拥塞程度。

课件在本页右侧给出的网络图有 6 个路由器节点 A、B、C、D、E、F。可读出的链路与代价为：$c(A,B)=2$、$c(A,D)=1$、$c(A,C)=5$、$c(B,C)=3$、$c(B,D)=2$、$c(C,E)=1$、$c(C,F)=5$、$c(D,E)=1$、$c(E,F)=2$；图中中部另有一处标号 $3$，其归属的链路在原图中不易分辨，属该图的局部不确定之处。该图在此后不用于计算，仅用于说明好路径的含义。

#### 5.4.2.2 网络图抽象的形式化

课件（原 PDF 第 31 页）给出同一抽象的标准记法：

$$\text{graph}: G = (N, E)$$

- $N =$ 路由器集合 $= \{u, v, w, x, y, z\}$；
- $E =$ 链路集合 $= \{(u,v),\ (u,x),\ (v,x),\ (v,w),\ (x,w),\ (x,y),\ (w,y),\ (w,z),\ (y,z)\}$。

图旁附注（aside）：图抽象在其他网络场景中也有用，例如 P2P，此时 $N$ 是对等方（peers）的集合，$E$ 是 TCP 连接的集合。

此处需要说明源材料的一处不一致：本页列出的 $E$ 只含 9 条边，未列出 $(u,w)$；但同页图中在 $u$ 与 $w$ 之间画有一条标号为 5 的连线，且下面 5.4.2.3 与例题中要用到的第 37 页 Dijkstra 表第 0 步给出 $D(w)=5,u$，这只有在 $u$ 与 $w$ 直接相邻且 $c(u,w)=5$ 时才成立。本笔记按图中连线与后续计算结果，把 $(u,w)$、$c(u,w)=5$ 计入该图，并在此处如实标出课件边集未列该边的现象，未对源数据作静默修改。

#### 5.4.2.3 链路代价与路径代价

课件（原 PDF 第 32 页）给出记号 $c(x, x')$，表示链路 $(x, x')$ 的代价，例如 $c(w, z) = 5$。代价可以恒为 1，也可以与带宽成反比，或者与拥塞程度相关。路径 $(x_1, x_2, x_3, \ldots, x_p)$ 的代价等于各段链路代价之和：

$$\text{cost of path }(x_1, x_2, x_3, \ldots, x_p) = c(x_1,x_2) + c(x_2,x_3) + \cdots + c(x_{p-1},x_p)$$

由此给出的关键问题（key question）是：$u$ 与 $z$ 之间的最小代价路径（least-cost path）是哪一条？找出该最小代价路径的算法即路由算法。该页所用的图与上页相同（节点 $u,v,w,x,y,z$，含 $u$ 与 $w$ 之间代价为 5 的连线），其上 $u$ 到 $z$ 的最小代价路径在后面的例题中被完整算出，结果为 $u \to x \to y \to z$，代价 $4$。

### 5.4.3 路由算法分类（Routing algorithm classification）

课件（原 PDF 第 33 页）按两个维度对路由算法分类。

**按信息范围：全局（global）还是分散（decentralized）**。全局算法中所有路由器拥有完整的拓扑与链路代价信息，这类算法称为链路状态（link state）算法。分散算法中路由器只知道与其物理相连的邻居以及到邻居的链路代价，计算是迭代过程，并通过与邻居交换信息进行，这类算法称为距离向量（distance vector）算法。

**按变化快慢：静态（static）还是动态（dynamic）**。静态算法的路由随时间变化缓慢；动态算法的路由变化较快，触发原因是周期性更新，或对链路代价变化作出响应。

两个维度相互独立：全局/分散说的是算法掌握多少信息，静态/动态说的是路由结果随时间变化的快慢。

### 5.4.4 链路状态算法与 Dijkstra 算法

#### 5.4.4.1 算法前提、结论形式与记号

Dijkstra 算法的前提与性质（原 PDF 第 34 页）：网络拓扑与链路代价为所有节点所知；计算从一个节点（源）到所有其他节点的最小代价路径；算法是迭代的，经过 $k$ 次迭代后，已知到 $k$ 个目的节点的最小代价路径。

记号：$c(x,y)$ 为节点 $x$ 到节点 $y$ 的链路代价，$x$ 与 $y$ 不是直接邻居时取 $\infty$；$D(v)$ 为从源到目的节点 $v$ 的路径代价的当前值；$p(v)$ 为从源到 $v$ 的路径上 $v$ 的前驱节点（predecessor node）；$N'$ 为最小代价路径已被明确确定的节点集合。

#### 5.4.4.2 算法伪码

课件（原 PDF 第 35 页）给出的伪码逐行为：

```
 1  Initialization:
 2     N' = {u}
 3     for all nodes v
 4        if v adjacent to u
 5           then D(v) = c(u,v)
 6           else D(v) = ∞
 7
 8  Loop
 9     find w not in N' such that D(w) is a minimum
10     add w to N'
11     update D(v) for all v adjacent to w and not in N' :
12        D(v) = min( D(v), D(w) + c(w,v) )
13     /* new cost to v is either old cost to v or known
14        shortest path cost to w plus cost from w to v */
15  until all nodes in N'
```

对第 12 行松弛（relaxation）步骤的说明：$D(v)$ 的更新值在「原来的 $D(v)$」与「已确定的最短路到 $w$ 的代价 $D(w)$ 加上 $w$ 到 $v$ 的链路代价 $c(w,v)$」两者中取较小者。这样，每当一个新节点 $w$ 被加入 $N'$，只检查 $w$ 的邻居，不重复检查已在 $N'$ 中的节点。第 9 行是算法每轮的选择动作：在尚未确定的节点中选出 $D$ 值最小者加入 $N'$。循环终止条件是所有节点都进入 $N'$。

#### 例题 1：Dijkstra 算法（原 PDF 第 36 页）

**题干**：给定下面的网络，链路代价为 $c(u,x)=5$、$c(u,w)=3$、$c(u,v)=7$、$c(w,v)=3$、$c(w,y)=8$、$c(x,y)=7$、$c(x,z)=9$、$c(v,y)=4$、$c(y,z)=2$（其中 $c(w,y)=8$ 由第 1 步之后的更新值 $D(y)=11,w$ 反推得到：$D(w)+c(w,y)=3+8=11$）。以 $u$ 为源，用 Dijkstra 算法求 $u$ 到所有其他节点的最小代价路径，并给出每一步的 $D$ 值与前驱 $p$。图中给出由前驱回溯得到的最短路径树，并注明 ties can exist (can be broken arbitrarily)（可能存在并列，可任意打破）。

**解**：

初始化（Step 0）：$N' = \{u\}$。$u$ 的邻居为 $v, w, x$。

- $D(v) = c(u,v) = 7$，$p(v) = u$；
- $D(w) = c(u,w) = 3$，$p(w) = u$；
- $D(x) = c(u,x) = 5$，$p(x) = u$；
- $D(y) = \infty$（$y$ 不与 $u$ 直接相邻）；
- $D(z) = \infty$（$z$ 不与 $u$ 直接相邻）。

第 1 步：在 $N'$ 之外的节点中取 $D$ 最小者，$\min\{D(v)=7,\ D(w)=3,\ D(x)=5,\ D(y)=\infty,\ D(z)=\infty\} = 3$，对应 $w$。加入 $w$，$N' = \{u, w\}$。

松弛 $w$ 的邻居（不在 $N'$ 中的）：

- $v$：$D(v) = \min(7,\ D(w)+c(w,v)) = \min(7,\ 3+3) = \min(7, 6) = 6$，$p(v) = w$；
- $y$：$D(y) = \min(\infty,\ 3+8) = 11$，$p(y) = w$。

此时表为：$D(v)=6,p(v)=w$；$D(x)=5,p(x)=u$；$D(y)=11,p(y)=w$；$D(z)=\infty$。

第 2 步：$\min\{D(v)=6,\ D(x)=5,\ D(y)=11,\ D(z)=\infty\} = 5$，对应 $x$。加入 $x$，$N' = \{u, w, x\}$。

松弛 $x$ 的邻居（不在 $N'$ 中的）：

- $v$：$D(v) = \min(6,\ 5 + c(x,v)) = \min(6,\ 5+4) = \min(6, 9) = 6$（保持 $6$，$p(v)$ 仍为 $w$）；
- $y$：$D(y) = \min(11,\ 5+7) = \min(11, 12) = 11$（保持 $11$，$p(y)$ 仍为 $w$）；
- $z$：$D(z) = \min(\infty,\ 5+9) = 14$，$p(z) = x$。

此时表为：$D(v)=6,p(v)=w$；$D(y)=11,p(y)=w$；$D(z)=14,p(z)=x$。

第 3 步：$\min\{D(v)=6,\ D(y)=11,\ D(z)=14\} = 6$，对应 $v$。加入 $v$，$N' = \{u, w, x, v\}$。

松弛 $v$ 的邻居（不在 $N'$ 中的）：

- $y$：$D(y) = \min(11,\ D(v)+c(v,y)) = \min(11,\ 6+4) = \min(11, 10) = 10$，$p(y) = v$；
- $z$：$v$ 与 $z$ 不相邻，$c(v,z)=\infty$，不产生更新，$D(z)$ 保持 $14$，$p(z)=x$。

此时表为：$D(y)=10,p(y)=v$；$D(z)=14,p(z)=x$。

第 4 步：$\min\{D(y)=10,\ D(z)=14\} = 10$，对应 $y$。加入 $y$，$N' = \{u, w, x, v, y\}$。

松弛 $y$ 的邻居（不在 $N'$ 中的）：

- $z$：$D(z) = \min(14,\ D(y)+c(y,z)) = \min(14,\ 10+2) = \min(14, 12) = 12$，$p(z) = y$。

此时表为：$D(z)=12,p(z)=y$。

第 5 步：$\min\{D(z)=12\} = 12$，加入 $z$，$N' = \{u, w, x, v, y, z\}$。所有节点已进入 $N'$，算法结束。

完整迭代表（原表在节点被加入 $N'$ 后其列留空，此处写出该列已确定的值并在括号中注明其状态）：

| Step | $N'$ | $D(v),p(v)$ | $D(w),p(w)$ | $D(x),p(x)$ | $D(y),p(y)$ | $D(z),p(z)$ |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | $u$ | $7,u$ | $3,u$ | $5,u$ | $\infty$ | $\infty$ |
| 1 | $uw$ | $6,w$ | $3,u$（已确定） | $5,u$ | $11,w$ | $\infty$ |
| 2 | $uwx$ | $6,w$ | $3,u$（已确定） | $5,u$（已确定） | $11,w$ | $14,x$ |
| 3 | $uwxv$ | $6,w$（已确定） | $3,u$（已确定） | $5,u$（已确定） | $10,v$ | $14,x$ |
| 4 | $uwxvy$ | $6,w$（已确定） | $3,u$（已确定） | $5,u$（已确定） | $10,v$（已确定） | $12,y$ |
| 5 | $uwxvyz$ | $6,w$（已确定） | $3,u$（已确定） | $5,u$（已确定） | $10,v$（已确定） | $12,y$（已确定） |

按前驱回溯得到从 $u$ 出发的最短路径树：$u \to x$（代价 $5$）；$u \to w$（代价 $3$）；$u \to w \to v$（$p(v)=w$，$p(w)=u$，代价 $3+3=6$）；$u \to w \to v \to y$（$p(y)=v$，代价 $6+4=10$）；$u \to w \to v \to y \to z$（$p(z)=y$，代价 $10+2=12$）。

**答案**：从 $u$ 到各节点的最小代价与路径为

| 目的 | 最小代价 | 路径 |
| --- | --- | --- |
| $v$ | 6 | $u \to w \to v$（$w$ 处前驱为 $u$） |
| $w$ | 3 | $u \to w$ |
| $x$ | 5 | $u \to x$ |
| $y$ | 10 | $u \to w \to v \to y$ |
| $z$ | 12 | $u \to w \to v \to y \to z$ |

**用原数据校验**：

- $v$：$u \to w \to v = 3 + 3 = 6$；另一条 $u \to x \to v = 5+4 = 9 > 6$，$u \to v = 7 > 6$，故 $6$ 正确。
- $w$：$u \to w = 3$；图中 $x$ 与 $w$ 之间无直接连线，$u \to w$ 即最小，$3$ 正确。
- $x$：$u \to x = 5$；经 $w$ 或 $v$ 绕行均不含更短组合，$5$ 正确。
- $y$：$u \to w \to v \to y = 3+3+4 = 10$；$u \to w \to y = 3+8 = 11 > 10$；$u \to x \to y = 5+7 = 12 > 10$，故 $10$ 正确。
- $z$：$u \to w \to v \to y \to z = 3+3+4+2 = 12$；$u \to x \to z = 5+9 = 14 > 12$，故 $12$ 正确。

#### 例题 2：Dijkstra 算法（原 PDF 第 37 页）

**题干**：另一例题使用的网络为节点 $u, v, w, x, y, z$ 组成的图，链路代价为 $c(u,v)=2$、$c(u,x)=1$、$c(u,w)=5$、$c(v,x)=2$、$c(v,w)=3$、$c(x,w)=3$、$c(x,y)=1$、$c(w,y)=1$、$c(w,z)=5$、$c(y,z)=2$。以 $u$ 为源求到所有其他节点的最小代价路径。源表给出的选入顺序为 $u$（第 0 步，初始已在 $N'$）后依次 $x$、$y$、$v$、$w$、$z$；$x$、$y$、$v$ 之间存在并列，课件按固定次序选入。该页附注给出 Kurose/Ross 教材在线交互练习的网址。

**解**：

初始化（Step 0）：$N' = \{u\}$。$u$ 的邻居为 $v, x, w$。

- $D(v) = c(u,v) = 2$，$p(v) = u$；
- $D(w) = c(u,w) = 5$，$p(w) = u$；
- $D(x) = c(u,x) = 1$，$p(x) = u$；
- $D(y) = \infty$；$D(z) = \infty$。

第 1 步：$\min\{D(v)=2,\ D(w)=5,\ D(x)=1,\ D(y)=\infty,\ D(z)=\infty\} = 1$，对应 $x$。加入 $x$，$N' = \{u, x\}$。

松弛 $x$ 的邻居（不在 $N'$ 中的）：

- $v$：$D(v) = \min(2,\ D(x)+c(x,v)) = \min(2,\ 1+2) = \min(2,3) = 2$，保持 $p(v)=u$；
- $w$：$D(w) = \min(5,\ 1+c(x,w)) = \min(5,\ 1+3) = \min(5,4) = 4$，$p(w) = x$；
- $y$：$D(y) = \min(\infty,\ 1+c(x,y)) = \min(\infty,\ 1+1) = 2$，$p(y) = x$。

此时表为：$D(v)=2,p(v)=u$；$D(w)=4,p(w)=x$；$D(y)=2,p(y)=x$；$D(z)=\infty$。

第 2 步：$\min\{D(v)=2,\ D(w)=4,\ D(y)=2,\ D(z)=\infty\} = 2$，$v$ 与 $y$ 并列。课件按固定次序把 $y$ 选入，加入 $y$，$N' = \{u, x, y\}$。

松弛 $y$ 的邻居（不在 $N'$ 中的）：

- $w$：$D(w) = \min(4,\ D(y)+c(y,w)) = \min(4,\ 2+1) = \min(4,3) = 3$，$p(w) = y$；
- $z$：$D(z) = \min(\infty,\ 2+c(y,z)) = \min(\infty,\ 2+2) = 4$，$p(z) = y$。

此时表为：$D(v)=2,p(v)=u$；$D(w)=3,p(w)=y$；$D(z)=4,p(z)=y$。

第 3 步：$\min\{D(v)=2,\ D(w)=3,\ D(z)=4\} = 2$，对应 $v$。加入 $v$，$N' = \{u, x, y, v\}$。

松弛 $v$ 的邻居（不在 $N'$ 中的）：

- $w$：$D(w) = \min(3,\ D(v)+c(v,w)) = \min(3,\ 2+3) = \min(3,5) = 3$，保持 $p(w)=y$；
- $x$ 已在 $N'$ 中，不处理；$v$ 与 $z$ 不相邻。

此时表为：$D(w)=3,p(w)=y$；$D(z)=4,p(z)=y$。

第 4 步：$\min\{D(w)=3,\ D(z)=4\} = 3$，对应 $w$。加入 $w$，$N' = \{u, x, y, v, w\}$。

松弛 $w$ 的邻居（不在 $N'$ 中的）：

- $z$：$D(z) = \min(4,\ D(w)+c(w,z)) = \min(4,\ 3+5) = \min(4,8) = 4$，保持 $p(z)=y$。

此时表为：$D(z)=4,p(z)=y$。

第 5 步：$\min\{D(z)=4\} = 4$，加入 $z$，$N' = \{u, x, y, v, w, z\}$。算法结束。

完整迭代表（原表被选入 $N'$ 的节点对应的列在其后各行留空，此处写出已确定值并注明状态）：

| Step | $N'$ | $D(v),p(v)$ | $D(w),p(w)$ | $D(x),p(x)$ | $D(y),p(y)$ | $D(z),p(z)$ |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | $u$ | $2,u$ | $5,u$ | $1,u$ | $\infty$ | $\infty$ |
| 1 | $ux$ | $2,u$ | $4,x$ | $1,u$（已确定） | $2,x$ | $\infty$ |
| 2 | $uxy$ | $2,u$ | $3,y$ | $1,u$（已确定） | $2,x$（已确定） | $4,y$ |
| 3 | $uxyv$ | $2,u$（已确定） | $3,y$ | $1,u$（已确定） | $2,x$（已确定） | $4,y$ |
| 4 | $uxyvw$ | $2,u$（已确定） | $3,y$（已确定） | $1,u$（已确定） | $2,x$（已确定） | $4,y$ |
| 5 | $uxyvwz$ | $2,u$（已确定） | $3,y$（已确定） | $1,u$（已确定） | $2,x$（已确定） | $4,y$（已确定） |

**答案**：从 $u$ 出发的最短路径树为 $u \to x$（$1$）、$x \to y$（$D(y)=2$，$p(y)=x$）、$u \to v$（$D(v)=2$，$p(v)=u$）、$y \to w$（$D(w)=3$，$p(w)=y$）、$y \to z$（$D(z)=4$，$p(z)=y$）。

| 目的 | 最小代价 | 路径 |
| --- | --- | --- |
| $v$ | 2 | $u \to v$ |
| $w$ | 3 | $u \to x \to y \to w$（$1+1+1=3$） |
| $x$ | 1 | $u \to x$ |
| $y$ | 2 | $u \to x \to y$（$1+1=2$） |
| $z$ | 4 | $u \to x \to y \to z$（$1+1+2=4$） |

**用原数据校验**：

- $v$：$u \to v = 2$；$u \to x \to v = 1+2 = 3 > 2$；$u \to w \to v = 5+3 = 8 > 2$；$u \to x \to w \to v = 1+3+3=7>2$。故 $2$ 正确。
- $w$：$u \to x \to y \to w = 1+1+1 = 3$；$u \to w = 5 > 3$；$u \to x \to w = 1+3 = 4 > 3$；$u \to v \to w = 2+3 = 5 > 3$。故 $3$ 正确。
- $x$：$u \to x = 1$，为所有从 $u$ 出发路径中的最小者，$1$ 正确。
- $y$：$u \to x \to y = 1+1 = 2$；$u \to w \to y = 5+1 = 6 > 2$；$u \to x \to w \to y = 1+3+1 = 5>2$。故 $2$ 正确。
- $z$：$u \to x \to y \to z = 1+1+2 = 4$；$u \to x \to y \to w \to z = 1+1+1+5 = 8>4$；$u \to w \to z = 5+5 = 10>4$。故 $4$ 正确。

#### 例题 3：由最短路树得到转发表（原 PDF 第 38 页）

该页继续使用例题 2 的网络图，给出从 $u$ 出发的结果最短路径树（resulting shortest-path tree from $u$）与 $u$ 中的结果转发表（resulting forwarding table in $u$）。图中画出的最短路径树连线为 $u$—$v$、$u$—$x$、$x$—$y$、$y$—$w$、$y$—$z$，与例题 2 算出的前驱关系一致。$u$ 中的转发表为：

| destination（目的） | link（链路） |
| --- | --- |
| $v$ | $(u,v)$ |
| $x$ | $(u,x)$ |
| $y$ | $(u,x)$ |
| $w$ | $(u,x)$ |
| $z$ | $(u,x)$ |

转发表的构造方法是：对每个目的取出最短路径树上从 $u$ 到该目的路径的第一条链路。逐项核对：到 $v$ 的路径是 $u \to v$，第一条链路 $(u,v)$；到 $x$ 的路径是 $u \to x$，第一条链路 $(u,x)$；到 $y$ 的路径是 $u \to x \to y$，第一条链路 $(u,x)$；到 $w$ 的路径是 $u \to x \to y \to w$，第一条链路 $(u,x)$；到 $z$ 的路径是 $u \to x \to y \to z$，第一条链路 $(u,x)$。注意 $v$ 的下一跳是 $(u,v)$ 而不是 $(u,x)$，虽然 $D(v)=2$ 与 $D(y)=2$ 数值相同；区别在于 $v$ 的前驱是 $u$，而 $y$ 的前驱是 $x$。

#### 5.4.4.3 复杂度与振荡（原 PDF 第 39 页）

**算法复杂度（algorithm complexity）**：设节点数为 $n$。每次迭代需要检查所有不在 $N'$ 中的节点 $w$；课件给出共需 $n(n+1)/2$ 次比较，即 $O(n^2)$。课件还指出更高效的实现可达 $O(n\log n)$。（**补充说明，非课件原文**：$n(n+1)/2$ 是课件采用的计数约定，按各次迭代尚未确定节点数求和得到的量级为 $n(n-1)/2$；$O(n\log n)$ 是课件给出的简写，采用堆/优先队列的稀疏图实现在严谨意义下为 $O((V+E)\log V)$，课件未作此细分。）

**振荡（oscillations possible）**：课件给出的情形是链路代价等于该链路承载的流量（link cost = amount of carried traffic）。课件用四个快照描述该现象，四个快照使用同一组 4 个路由器 A、B、C、D；根据原图，每条**有向**链路的代价等于该方向承载的流量，A 为目的节点，B 与 D 各注入流量 1，C 注入流量 $\varepsilon>0$（$\varepsilon$ 为小正量）。按链路方向（D→A、B→A、D→C、C→D、B→C、C→B）整理的四幅快照如下：

| 快照 | D→A | B→A | D→C | C→D | B→C | C→B | 该轮算出的路径 |
|---|---|---|---|---|---|---|---|
| 初始 | 1 | $1+\varepsilon$ | 0 | 0 | 0 | $\varepsilon$ | D→A；B→A；C→B→A |
| 第 2 幅 | $2+\varepsilon$ | 0 | 0 | $1+\varepsilon$ | 1 | 0 | D→A；B→C→D→A；C→D→A |
| 第 3 幅 | 0 | $2+\varepsilon$ | 1 | 0 | 0 | $1+\varepsilon$ | D→C→B→A；B→A；C→B→A |
| 第 4 幅 | $2+\varepsilon$ | 0 | 0 | $1+\varepsilon$ | 1 | 0 | 与第 2 幅相同 |

每幅图下方标注的说明是 given these costs, find new routing…. resulting in new costs（给定这些代价，重新求路由……得到新的代价）。现象本身为：由于链路代价取决于该链路实时承载的流量，一次基于当前代价计算出的最小代价路由会把流量集中到代价较低的链路上；该链路承载流量上升后其代价随之上升，下一轮计算又会把流量移回原来的链路，第 4 幅与第 2 幅的代价完全相同，路由在两个状态之间反复改变，算法不能收敛到稳定的路由。这是采用「代价＝流量」这一度量时使用 Dijkstra 类算法会出现的问题。

### 5.4.5 广播路由（Broadcast routing）

广播路由要解决的问题是：把来自某个源的数据报送达所有其他节点（原 PDF 第 40、41 页）。

**洪泛（flooding）**：把数据报从源送到所有其他节点。课件标出的后果是广播风暴（broadcast storm）：一个节点收到数据报后向除入链路之外的所有链路转发，各节点反复互相转发同一数据报，网络中的副本数量迅速增长，形成风暴。

**受控洪泛（controlled flooding）**：为避免广播风暴，课件给出三种做法。

- **序号控制洪泛（sequence-number-controlled flooding）**：在广播数据报中加入 ID 与广播序号（ID + broadcast sequence number）；节点收到数据报时记录其 (ID, 序号)，遇到重复到达的同一 (ID, 序号) 就不再转发，从而消除重复副本。
- **反向路径转发（reverse path forwarding，RPF）**：课件在图注中同时给出缩写与全称（图注把缩写印作 RFP，全称写 Reverse path forwarding；图中标注为 RPF）。其做法是：节点只在收到的广播分组恰好来自「自己通往源的最短路径上的下一跳」时才继续转发，否则丢弃。
- **生成树广播（spanning-tree broadcast）**：设有一个连通无向图，则其生成树（spanning tree）是该图的一个连通子图，且该子图中不包含回路（cycle）；生成树包含原图的全部节点，只保留原图的一部分边，保留的边数等于节点数减 1。若洪泛时节点把收到的广播分组向除入链路以外的所有链路转发，则同一节点会多次收到同一分组，产生冗余传输；若广播只沿生成树上节点的相邻边转发，则每个节点恰好收到一次该分组，从而避免冗余广播分组的传输（avoid the transmission of redundancy broadcast packets）。这一做法成立的依据是生成树无回路：分组沿树边转发不会回到已经转发过该分组的节点。

课件用对勾标出结论：受控洪泛能够避免广播风暴（be able to avoid the broadcast storm）。第 40 页的图给出一个 7 节点网络 A、B、C、D、E、F、G，链路包括 A—B、A—C、B—C、C—F、C—E、B—D、E—D、E—F、D—G，图中各链路上画有双向箭头，表示洪泛过程中数据报在链路上被反复双向传递、进而产生风暴的情形。

生成树广播在第 41 页给出两张对照图，使用同一棵生成树、不同的广播发起节点，节点为 A、B、C、D、E、F、G：

- 生成树上的边（图中以粗箭头画出）：A–B、A–C、B–D、D–G、C–E、C–F，共 6 条，恰好等于节点数 7 减 1。
- 不在生成树上的边（图中以细线画出，广播时不用于转发）：B–C、D–E、E–F。
- 图 (a) 标题为 Broadcast initiated at A（广播由 A 发起）：转发方向为 A→B、A→C；B→D；D→G；C→E；C→F。
- 图 (b) 标题为 Broadcast initiated at D（广播由 D 发起）：转发方向为 D→B、D→G；B→A；A→C；C→E、C→F。

两图的差别只在发起节点与由此决定的转发方向，生成树本身相同。把两图的转发顺序按层列出：

| 广播发起节点 | 第 1 跳 | 第 2 跳 | 第 3 跳 | 第 4 跳 |
| --- | --- | --- | --- | --- |
| A | A→B、A→C | B→D、C→E、C→F | D→G | — |
| D | D→B、D→G | B→A | A→C | C→E、C→F |

在上述两张图中，被排除的链路 B–C、D–E、E–F 上都不出现转发箭头，正是这些边的省略使每个节点只收到一份广播分组。

### 5.4.6 链路状态路由算法（Link state algorithm）

链路状态（link state, LS）算法由两部分机制组合而成，课件标题即为 Broadcast routing + Dijkstra's algorithm（原 PDF 第 42 页）：

1. **数据分发**：每个节点把链路状态分组（link-state packet）广播给所有其他节点（having each node broadcast link-state packets to all other nodes）。广播的结果是所有节点获得一份完全相同且完整的网络视图（all nodes have an identical and complete view of the network），其中包括全网拓扑与每条链路的代价。这里的「广播给所有其他节点」正是 5.4.5 的广播路由所解决的问题。
2. **路径计算**：每个节点以这份一致的全网视图为输入，用 Dijkstra 算法计算从本节点到网络中所有其他节点的最小代价路径（using Dijkstra's algorithm compute the least-cost path from one node to all other nodes in the network）。

维护规则：如果某条链路的代价发生变化，则重新广播链路状态分组并重新执行 Dijkstra 计算（re-broadcast and re-compute）。因此 LS 算法是一种全局式（global）算法：每个节点都持有全网拓扑与链路代价信息，各节点独立计算，彼此的计算结果一致。

### 5.4.7 距离向量路由算法（Distance vector algorithm）

#### 5.4.7.1 Bellman-Ford 方程

Bellman-Ford 方程是距离向量算法的计算基础，其形式为动态规划（dynamic programming，原 PDF 第 43 页）。记号定义为：$d_x(y)$ 表示从节点 $x$ 到节点 $y$ 的最小代价路径的代价（cost of least-cost path from $x$ to $y$）；$c(x,v)$ 表示节点 $x$ 到其邻居 $v$ 的直接链路代价；$N$ 为网络中的全部节点集合。Bellman-Ford 方程为：

$$d_x(y) = \min_{v}\{\,c(x,v) + d_v(y)\,\}$$

其中 $\min$ 取遍 $x$ 的所有邻居 $v$。方程的含义是：从 $x$ 到 $y$ 的最小代价路径，必定由 $x$ 到某个邻居 $v$ 的一跳（代价 $c(x,v)$）加上 $v$ 到 $y$ 的最小代价路径（代价 $d_v(y)$）组成；对所有邻居取最小值即得 $d_x(y)$。该方程成立的前提是最小代价路径的子路径也是最小代价路径。

课件给出的示例网络节点为 $u,v,w,x,y,z$，链路代价为：

| 链路 | u–v | u–x | u–w | v–w | v–x | w–x | w–y | w–z | x–y | y–z |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 代价 | 2 | 1 | 5 | 3 | 2 | 3 | 1 | 5 | 1 | 2 |

课件先给出三个已知量 $d_v(z)=5$、$d_w(z)=3$、$d_x(z)=3$。逐项核对：$d_x(z)=3$ 取路径 $x\to y\to z$，代价 $1+2=3$（$x$ 与 $z$ 之间无直接链路），而 $x\to v\to w\to z$ 为 $2+3+5=10$，更大；$d_w(z)=3$ 取路径 $w\to y\to z$，代价 $1+2=3$，直接链路 $w$–$z$ 的代价为 5，大于 3，故不取直接链路；$d_v(z)=5$ 取路径 $v\to x\to y\to z$，代价 $2+1+2=5$，而 $v\to w\to z$ 为 $3+5=8$，更大。

然后用 Bellman-Ford 方程求 $d_u(z)$。$u$ 的邻居是 $v$、$x$、$w$：

$$d_u(z)=\min\{c(u,v)+d_v(z),\ c(u,x)+d_x(z),\ c(u,w)+d_w(z)\}=\min\{2+5,\ 1+3,\ 5+3\}=\min\{7,\ 4,\ 8\}=4$$

逐项：经 $v$ 的方案为 $2+5=7$；经 $x$ 的方案为 $1+3=4$；经 $w$ 的方案为 $5+3=8$。三者中最小值为 4，故 $d_u(z)=4$，对应路径为 $u\to x\to y\to z$（代价 $1+1+2=4$）。用原数据校验：从 $u$ 出发的其它候选路径为 $u\to x\to w\to z$（$1+3+5=9$）、$u\to w\to y\to z$（$5+1+2=8$）、$u\to v\to w\to y\to z$（$2+3+1+2=8$）、$u\to x\to v\to w\to y\to z$（$1+2+3+1+2=9$），均大于 4，故最小值为 4 无误。

#### 5.4.7.2 距离向量的构成与维护

课件（原 PDF 第 44 页）用大写 $D$ 表示算法运行中实际持有的估计值，用小写 $d$ 表示真实的最小代价。$D_x(y)$ 表示节点 $x$ 对「到 $y$ 的最小代价」的估计值（estimate of least cost from $x$ to $y$）。节点 $x$ 知道到每个邻居 $v$ 的直接链路代价 $c(x,v)$；节点 $x$ 维护自己的距离向量（distance vector）$D_x = [D_x(y): y \in N]$，即对该节点集合 $N$ 中每一个目的地 $y$ 的代价估计构成的行向量；节点 $x$ 还维护其邻居的距离向量，即对每个邻居 $v$ 保存 $D_v = [D_v(y): y \in N]$，也就是邻居通告过来的估计值。因此每个节点本地保存的数据是：一条自身距离向量，加上每个邻居各一条距离向量，再加上到各邻居的直接链路代价。

#### 5.4.7.3 距离向量算法的运行规则

基本思想（basic idea，原 PDF 第 46、47 页）：

1. 每个节点周期性地把自己的距离向量估计值发送给它的邻居（each node periodically sends its own distance vector estimate to neighbors）。
2. 当节点 $x$ 收到邻居发来的新距离向量估计后，用 Bellman-Ford 方程更新自己的距离向量：

$$D_x(y) \leftarrow \min_{v}\{\,c(x,v) + D_v(y)\,\}\qquad \text{对每个节点 } y \in N$$

其中 $c(x,v)$ 是 $x$ 到邻居 $v$ 的直接链路代价，$D_v(y)$ 是邻居 $v$ 最新通告的到 $y$ 的估计值。
3. 课件指出 under minor, natural conditions, the estimate $D_x(y)$ converge to the actual least cost $d_x(y)$，即在一些较弱的、自然的条件下，估计值 $D_x(y)$ 收敛到真实最小代价 $d_x(y)$。

算法的两个运行特性：其一是**迭代式、异步（iterative, asynchronous）**，算法没有统一的轮次，每一次本地迭代由下列事件之一触发——本地链路代价发生变化，或收到来自邻居的 DV 更新报文；其二是**分布式（distributed）**，每个节点只在自己的距离向量发生变化时才通知邻居（each node notifies neighbors only when its DV changes），收到通知的邻居若自己的 DV 因此改变，再继续通知它自己的邻居，如此传播下去。

节点本地的处理循环（原 PDF 第 47 页流程图）为：

| 步骤 | 动作 |
| --- | --- |
| 1 | wait：等待（本地链路代价变化，或收到邻居的报文） |
| 2 | recompute：重新计算估计值 |
| 3 | 如果到任一目的地的 DV 发生变化，则 notify：通知邻居 |
| 4 | 返回步骤 1 |

#### 例题 4：节点 x 存储的距离向量与路由表（原 PDF 第 45 页）

**题干**：网络图与 Bellman-Ford 方程示例相同，节点 $u,v,w,x,y,z$，链路代价为 $c(u,v)=2$、$c(u,x)=1$、$c(u,w)=5$、$c(v,w)=3$、$c(v,x)=2$、$c(w,x)=3$、$c(w,y)=1$、$c(w,z)=5$、$c(x,y)=1$、$c(y,z)=2$。求节点 $x$ 处存储的各距离向量与节点 $x$ 的路由表。

**解**：课件左侧给出 Distance vectors stored at node x（在节点 $x$ 处存储的各距离向量），行标为广播该向量的节点（from），列标为目的节点（cost to），列序为 $x,y,z,u,v,w$。完整表格如下（据原图核对）：

| from＼cost to | x | y | z | u | v | w |
| --- | --- | --- | --- | --- | --- | --- |
| x | 0 | 1 | 3 | 1 | 2 | 2 |
| y | 1 | 0 | 2 | 2 | 3 | 1 |
| u | 1 | 2 | 4 | 0 | 2 | 5 |
| v | 2 | 3 | 5 | 3 | 0 | 3 |
| w | 2 | 1 | 3 | 5 | 3 | 0 |

对第 $x$ 行逐项复核：$D_x(x)=0$；$D_x(y)=1$（直接链路 $x$–$y$ 为 1，经 $v$ 为 $2+3=5$）；$D_x(z)=3$（$x\to y\to z$ 为 $1+2=3$，$x\to v\to w\to z$ 为 $2+3+5=10$）；$D_x(u)=1$（直接链路 $x$–$u$ 为 1）；$D_x(v)=2$（直接链路 $x$–$v$ 为 2）；$D_x(w)=2$（$x\to y\to w$ 为 $1+1=2$，直接链路 $x$–$w$ 为 3，故取 2）。其余各行是邻居通告给 $x$ 的估计值，这些行是邻居当时通告的估计，部分项目与当前最短路径相符，例如 $D_v(x)=2$（直接链路 $v$–$x$）、$D_v(y)=3$（$v\to x\to y$ 为 $2+1=3$）、$D_v(z)=5$（$v\to x\to y\to z$ 为 $2+1+2=5$）、$D_w(y)=1$（直接链路）、$D_w(z)=3$（$w\to y\to z$ 为 $1+2=3$）、$D_w(x)=2$（$w\to y\to x$ 为 $1+1=2$）。

**补充核查（非课件原文，为本次整理的核算）**：表中第 $u$ 行的 $w$ 列与第 $w$ 行的 $u$ 列均为 5，恰好等于直接链路 $u$–$w$ 的代价；但按同一张表内其它数值推算，$u\to x\to y\to w$ 为 $1+1+1=3$，$w\to y\to x\to u$ 为 $1+1+1=3$，均小于 5。因此该两处应理解为算法运行中尚未完全收敛的存储估计，不宜把整张表直接当作全网最终最短路表使用；课件对该表未作此说明。

课件右侧给出 Routing table at node x（节点 $x$ 的路由表），列标为目的节点，顺序为 $y,z,u,v,w$，每格给出下一跳（hop）与代价（cost）：

| destination | y | z | u | v | w |
| --- | --- | --- | --- | --- | --- |
| hop, cost | y, 1 | y, 1 | u, 1 | v, 2 | y, 2 |

对照上表第 $x$ 行：到 $y$ 的代价为 1，下一跳为 $y$，即 (y, 1)；到 $u$ 的代价为 1，下一跳为 $u$，即 (u, 1)；到 $v$ 的代价为 2，下一跳为 $v$，即 (v, 2)；到 $w$ 的代价为 2，下一跳为 $y$，即 (y, 2)。**关于「到 z」一格的核对**：原课件该单元格印刷为 (y, 1)。但上表第 $x$ 行给出 $D_x(z)=3$，若下一跳为 $y$（即路径 $x\to y\to z$，$1+2=3$），则该格应为 (y, 3)。此处不按错误值照抄、也不静默改写：**原课件该单元为 y,1，按上表计算应为 y,3**，差异记录于此供核对。

#### 例题 5：三节点网络的完整运行过程（原 PDF 第 48、49 页）

**题干**：三个节点 $x$、$y$、$z$，链路代价为 $c(x,y)=2$、$c(x,z)=7$、$c(y,z)=1$（图中 $x$–$y$ 标注 2，$x$–$z$ 标注 7，$y$–$z$ 标注 1）。求各节点距离向量的更新过程与最终收敛结果。

**解**：初始状态每个节点只知道自己的直接链路代价，尚未收到邻居的距离向量，故表中邻居行为 $\infty$。

| node x 表（from＼cost to） | x | y | z |
| --- | --- | --- | --- |
| x | 0 | 2 | 7 |
| y | ∞ | ∞ | ∞ |
| z | ∞ | ∞ | ∞ |

| node y 表（from＼cost to） | x | y | z |
| --- | --- | --- | --- |
| x | ∞ | ∞ | ∞ |
| y | 2 | 0 | 1 |
| z | ∞ | ∞ | ∞ |

| node z 表（from＼cost to） | x | y | z |
| --- | --- | --- | --- |
| x | ∞ | ∞ | ∞ |
| y | ∞ | ∞ | ∞ |
| z | 7 | 1 | 0 |

第一次交换后，各节点按 Bellman-Ford 方程重算。节点 $x$ 的计算：

$$D_x(y)=\min\{c(x,y)+D_y(y),\ c(x,z)+D_z(y)\}=\min\{2+0,\ 7+1\}=\min\{2,\ 8\}=2$$

$$D_x(z)=\min\{c(x,y)+D_y(z),\ c(x,z)+D_z(z)\}=\min\{2+1,\ 7+0\}=\min\{3,\ 7\}=3$$

式中 $D_y(y)=0$、$D_z(y)=1$、$D_y(z)=1$、$D_z(z)=0$ 取自节点 $y$、$z$ 通告的距离向量。于是 $D_x$ 由 $(0,2,7)$ 更新为 $(0,2,3)$。

节点 $z$ 的计算：

$$D_z(x)=\min\{c(z,x)+D_x(x),\ c(z,y)+D_y(x)\}=\min\{7+0,\ 1+2\}=\min\{7,\ 3\}=3$$
$$D_z(y)=\min\{c(z,x)+D_x(y),\ c(z,y)+D_y(y)\}=\min\{7+2,\ 1+0\}=\min\{9,\ 1\}=1$$

于是 $D_z$ 由 $(7,1,0)$ 更新为 $(3,1,0)$。

节点 $y$ 的计算：

$$D_y(x)=\min\{c(y,x)+D_x(x),\ c(y,z)+D_z(x)\}=\min\{2+0,\ 1+7\}=\min\{2,\ 8\}=2$$
$$D_y(z)=\min\{c(y,x)+D_x(z),\ c(y,z)+D_z(z)\}=\min\{2+7,\ 1+0\}=\min\{9,\ 1\}=1$$

于是 $D_y$ 保持 $(2,0,1)$ 不变。

再经过一次交换，三个节点保存的三行向量完全相同，算法收敛。收敛后节点 $x$、$y$、$z$ 的三张表内容一致：

| from＼cost to | x | y | z |
| --- | --- | --- | --- |
| x | 0 | 2 | 3 |
| y | 2 | 0 | 1 |
| z | 3 | 1 | 0 |

**用原数据校验**：$x$ 到 $y$ 直接链路为 2，经 $z$ 为 $7+1=8$，取 2，与 $D_x(y)=2$ 一致；$x$ 到 $z$ 直接链路为 7，经 $y$ 为 $2+1=3$，取 3，与 $D_x(z)=3$ 一致；$z$ 到 $x$ 直接链路为 7，经 $y$ 为 $1+2=3$，取 3，与 $D_z(x)=3$ 一致；$y$ 到 $z$ 直接链路为 1，经 $x$ 为 $2+7=9$，取 1，与 $D_y(z)=1$ 一致。三条链路代价重新组合后得到的最小路径代价与表中数值全部吻合。

#### 例题 6：链路代价变小时的三步收敛（原 PDF 第 50、51、52 页）

**题干**：网络有四个节点 $w$、$x$、$y$、$z$，链路为 $w$–$x$（代价 1）、$w$–$z$（代价 1）、$x$–$y$（代价 4）、$z$–$y$（代价 7）；$x$ 与 $z$ 之间、$w$ 与 $y$ 之间没有直接链路。事件为链路 $z$–$y$ 的代价由 7 变为 1。求各距离向量的更新过程与收敛结果。课件对该过程给出的规则是：节点检测到本地链路代价变化（detects local link cost change），更新路由信息、重新计算距离向量（updates routing info, recalculates distance vector），如果 DV 发生变化则通知邻居（if DV changes, notify neighbors）。

**解**：变化前已收敛的距离向量（列序 $x, y, z, w$）为

| 节点 | x | y | z | w |
| --- | --- | --- | --- | --- |
| $D_x$ | 0 | 4 | 2 | 1 |
| $D_y$ | 4 | 0 | 6 | 5 |
| $D_z$ | 2 | 6 | 0 | 1 |
| $D_w$ | 1 | 5 | 1 | 0 |

复核：$x$ 到 $z$ 经 $w$ 为 $1+1=2$（无直接链路）；$y$ 到 $z$ 直接链路为 7，经 $x$ 到 $z$ 为 $4+2=6$，取 6；$y$ 到 $w$ 经 $x$ 为 $4+1=5$，经 $z$ 为 $6+1=7$，取 5；$w$ 到 $y$ 经 $x$ 为 $1+4=5$，经 $z$ 为 $1+6=7$，取 5。

第 1 步：节点 $y$ 与节点 $z$ 检测到本地链路 $z$–$y$ 的代价变化，各自重算。

节点 $y$：
$$D_y(x)=\min\{c(y,x)+D_x(x),\ c(y,z)+D_z(x)\}=\min\{4+0,\ 1+2\}=\min\{4,\ 3\}=3$$
$$D_y(z)=\min\{c(y,x)+D_x(z),\ c(y,z)+D_z(z)\}=\min\{4+2,\ 1+0\}=\min\{6,\ 1\}=1$$
$$D_y(w)=\min\{c(y,x)+D_x(w),\ c(y,z)+D_z(w)\}=\min\{4+1,\ 1+1\}=\min\{5,\ 2\}=2$$
更新后 $D_y=(3,0,1,2)$。

节点 $z$：
$$D_z(x)=\min\{c(z,w)+D_w(x),\ c(z,y)+D_y(x)\}=\min\{1+1,\ 1+2\}=\min\{2,\ 3\}=2$$
$$D_z(y)=\min\{c(z,w)+D_w(y),\ c(z,y)+D_y(y)\}=\min\{1+5,\ 1+0\}=\min\{6,\ 1\}=1$$
$$D_z(w)=\min\{c(z,w)+D_w(w),\ c(z,y)+D_y(w)\}=\min\{1+0,\ 1+5\}=\min\{1,\ 6\}=1$$
更新后 $D_z=(2,1,0,1)$。

第 2 步：节点 $w$ 收到邻居更新后的向量，重算。
$$D_w(y)=\min\{c(w,x)+D_x(y),\ c(w,z)+D_z(y)\}=\min\{1+4,\ 1+1\}=\min\{5,\ 2\}=2$$
其余分量 $D_w(x)=1$、$D_w(z)=1$、$D_w(w)=0$ 不变，更新后 $D_w=(1,2,1,0)$。

第 3 步：节点 $x$ 收到 $w$ 更新后的向量，重算。
$$D_x(y)=\min\{c(x,y)+D_y(y),\ c(x,w)+D_w(y)\}=\min\{4+0,\ 1+2\}=\min\{4,\ 3\}=3$$
其余分量 $D_x(x)=0$、$D_x(z)=2$、$D_x(w)=1$ 不变，更新后 $D_x=(0,3,2,1)$。

收敛后各节点的距离向量为

| 节点 | x | y | z | w |
| --- | --- | --- | --- | --- |
| $D_x$ | 0 | 3 | 2 | 1 |
| $D_y$ | 3 | 0 | 1 | 2 |
| $D_z$ | 2 | 1 | 0 | 1 |
| $D_w$ | 1 | 2 | 1 | 0 |

课件注明 Algorithm converges in 3 steps（算法在 3 步内收敛），源图各表中行 $x$ 由 $0,4,2,1$ 变为 $0,3,2,1$，即各节点保存的 $x$ 的距离向量同步更新。

**用原数据校验**：链路 $z$–$y$ 变为 1 之后，$x$ 到 $y$ 的直接链路仍为 4，而 $x\to w\to z\to y$ 为 $1+1+1=3$，取 3，与 $D_x(y)=3$ 一致；$y$ 到 $x$ 对称地取 $y\to z\to w\to x$ 为 $1+1+1=3$，与 $D_y(x)=3$ 一致；$w$ 到 $y$ 经 $z$ 为 $1+1=2$，与 $D_w(y)=2$ 一致。整组数值与图中四条链路代价重新组合的最小代价完全吻合，过程中未出现数值反复增大的现象。

#### 例题 7：链路代价变大导致的计数到无穷（原 PDF 第 53、54、55 页）

**题干**：三个节点 $x$、$y$、$z$ 构成一个环，链路代价 $c(y,z)=1$、$c(x,z)=50$、$c(x,y)=4$。事件为链路 $x$–$y$ 的代价由 4 变为 60。课件原文说明 good news travels fast, bad news travels slow – "count to infinity" problem!，并注明 for example: 44 iterations before algorithm stabilizes（该例需要 44 次迭代算法才稳定）。求各距离向量的演化与最终稳定值。

**解**：变化前已收敛的距离向量（列序 $x, y, z$）为

| 节点 | x | y | z |
| --- | --- | --- | --- |
| $D_x$ | 0 | 4 | 5 |
| $D_y$ | 4 | 0 | 1 |
| $D_z$ | 5 | 1 | 0 |

复核：$x$ 到 $z$ 直接链路为 50，经 $y$ 为 $4+1=5$，取 5；$z$ 到 $x$ 经 $y$ 为 $1+4=5$，小于直接链路的 50。

逐步复算（每一步只写被触发的节点）：

迭代 1：节点 $y$ 检测到 $c(y,x)$ 变为 60，重算
$$D_y(x)=\min\{c(y,x)+D_x(x),\ c(y,z)+D_z(x)\}=\min\{60+0,\ 1+5\}=\min\{60,\ 6\}=6$$
得 $D_y=(6,0,1)$。

迭代 2：节点 $z$ 收到 $D_y(x)=6$，重算
$$D_z(x)=\min\{c(z,x)+D_x(x),\ c(z,y)+D_y(x)\}=\min\{50+0,\ 1+6\}=\min\{50,\ 7\}=7$$
得 $D_z=(7,1,0)$。

迭代 3：节点 $x$ 收到更新后的邻居向量，重算
$$D_x(y)=\min\{c(x,y)+D_y(y),\ c(x,z)+D_z(y)\}=\min\{60+0,\ 50+1\}=\min\{60,\ 51\}=51$$
$$D_x(z)=\min\{c(x,y)+D_y(z),\ c(x,z)+D_z(z)\}=\min\{60+1,\ 50+0\}=\min\{61,\ 50\}=50$$
得 $D_x=(0,51,50)$。

迭代 4：节点 $y$ 重算 $D_y(x)=\min\{60+0,\ 1+7\}=\min\{60,\ 8\}=8$，得 $D_y=(8,0,1)$。

迭代 5：节点 $z$ 重算 $D_z(x)=\min\{50+0,\ 1+8\}=\min\{50,\ 9\}=9$，得 $D_z=(9,1,0)$。

此后每完成一次 $y$ 与 $z$ 之间的向量交换，$D_y(x)$ 与 $D_z(x)$ 各增加 2：源图各帧中 $D_y(x)$ 依次为 6、8、…、48、50、51，$D_z(x)$ 依次为 7、9、…、49、50；$D_x$ 在 $y$ 列稳定于 51、在 $z$ 列稳定于 50。在 $D_z(x)$ 尚未达到 50 之前，$z$ 始终取「经 $y$」的估计值，而 $y$ 又反过来取「经 $z$」的估计值，两个节点互相把对方当作通往 $x$ 的下一跳，数值不断增大而不下降。

收敛条件：当 $D_z(x)$ 增大到 50 时，$z$ 取直接链路 $z$–$x$（代价 50）；随后 $y$ 重算 $D_y(x)=\min\{60+0,\ 1+50\}=\min\{60,\ 51\}=51$，算法稳定。最终：

| 节点 | x | y | z |
| --- | --- | --- | --- |
| $D_x$ | 0 | 51 | 50 |
| $D_y$ | 51 | 0 | 1 |
| $D_z$ | 50 | 1 | 0 |

**用原数据校验**：$x$ 到 $y$ 直接链路为 60，经 $z$ 为 $50+1=51$，取 51，与 $D_x(y)=51$ 一致；$y$ 到 $x$ 经 $z$ 为 $1+50=51$，与 $D_y(x)=51$ 一致；$z$ 到 $x$ 取直接链路 50，与 $D_z(x)=50$ 一致。最终结果正确，但在达到该结果之前经历了大量无意义的数值递增。课件给出的迭代次数为 44 次；本笔记按 Bellman-Ford 方程逐步复算得到的数值序列与课件各帧一致，课件未说明 44 次的具体计数口径。

#### 5.4.7.4 毒性逆转（Poisoned reverse）

针对计数到无穷问题，课件（原 PDF 第 56、57 页）给出毒性逆转（poisoned reverse）的处理方法：如果 $Z$ 是经由 $Y$ 才能到达 $X$ 的（if Z routes through Y to get to X），那么 $Z$ 告诉 $Y$：$Z$ 到 $X$ 的距离是无穷大（Z tells Y its (Z's) distance to X is infinite），从而使 $Y$ 不会选择经由 $Z$ 到达 $X$ 的路径。课件在同一页提问 Will this completely solve count to infinity problem?，课件该页未给出答案。

课件对上述三角形网络给出的三张节点表（变化前的状态，列序 $x, y, z$）为：

| node x 表（from＼cost to） | x | y | z |
| --- | --- | --- | --- |
| x | 0 | 4 | 5 |
| y | 4 | 0 | 1 |
| z | 5 | 1 | 0 |

| node y 表（from＼cost to） | x | y | z |
| --- | --- | --- | --- |
| x | 0 | 4 | ∞ |
| y | 4 | 0 | 1 |
| z | ∞ | 1 | 0 |

| node z 表（from＼cost to） | x | y | z |
| --- | --- | --- | --- |
| x | 0 | 4 | 5 |
| y | 4 | 0 | 1 |
| z | 5 | 1 | 0 |

对比可见，节点 $y$ 的表内有两处被置为 $\infty$：其行 $x$（$x$ 通告的距离向量）中到 $z$ 的分量为 $\infty$，因为 $x$ 到 $z$ 的路径是 $x\to y\to z$（经由 $y$），故 $x$ 向 $y$ 毒化该分量；其行 $z$（$z$ 通告的距离向量）中到 $x$ 的分量为 $\infty$，因为 $z$ 到 $x$ 的路径是 $z\to y\to x$（经由 $y$），故 $z$ 向 $y$ 毒化该分量。

在此状态下把链路 $x$–$y$ 的代价由 4 改为 60，逐步复算如下：

第 0 步（变化前）：$D_x=(0,4,5)$，$D_y=(4,0,1)$，$D_z=(5,1,0)$；$x$ 向 $y$ 通告 $D_x(z)=\infty$，$z$ 向 $y$ 通告 $D_z(x)=\infty$。

第 1 步：节点 $y$ 检测到 $c(y,x)=60$，重算
$$D_y(x)=\min\{c(y,x)+D_x(x),\ c(y,z)+D_z(x)\}=\min\{60+0,\ 1+\infty\}=\min\{60,\ \infty\}=60$$
得 $D_y=(60,0,1)$。此处 $z$ 毒化后的 $\infty$ 使 $y$ 不再把「经 $z$ 到 $x$」当作候选路径，计数过程在第 1 步即被切断。

第 2 步：节点 $z$ 重算
$$D_z(x)=\min\{c(z,x)+D_x(x),\ c(z,y)+D_y(x)\}=\min\{50+0,\ 1+60\}=\min\{50,\ 61\}=50$$
得 $D_z=(50,1,0)$。此时 $z$ 到 $x$ 改走直接链路 $z$–$x$，不再经由 $y$，$z$ 不再向 $y$ 毒化 $D_z(x)$。同一轮中节点 $x$ 重算
$$D_x(y)=\min\{c(x,y)+D_y(y),\ c(x,z)+D_z(y)\}=\min\{60+0,\ 50+1\}=\min\{60,\ 51\}=51$$
得 $D_x=(0,51,50)$。

第 3 步：节点 $y$ 重算
$$D_y(x)=\min\{60+0,\ 1+50\}=\min\{60,\ 51\}=51$$
得 $D_y=(51,0,1)$。算法稳定，课件注明 Algorithm converges in 3 steps。

末帧（已稳定）的各表为：

| 表 | 行 | x | y | z |
| --- | --- | --- | --- | --- |
| node x 表 | x | 0 | 51 | 50 |
| node x 表 | y | 51 | 0 | 1 |
| node x 表 | z | 50 | 1 | 0 |
| node y 表 | x | 0 | 51 | 50 |
| node y 表 | y | 51 | 0 | 1 |
| node y 表 | z | 50 | 1 | 0 |
| node z 表 | x | 0 | ∞ | 50 |
| node z 表 | y | ∞ | 0 | 1 |
| node z 表 | z | 50 | 1 | 0 |

在节点 $z$ 的表内可以看到毒化标记的迁移：$x$ 到 $y$ 的路径此时为 $x\to z\to y$（经由 $z$），故 $x$ 通告给 $z$ 的向量中到 $y$ 的分量为 $\infty$（行 $x$ 的 $y$ 列为 $\infty$）；$y$ 到 $x$ 的路径此时为 $y\to z\to x$（经由 $z$），故 $y$ 通告给 $z$ 的向量中到 $x$ 的分量为 $\infty$（行 $y$ 的 $x$ 列为 $\infty$）。节点 $z$ 到 $x$ 已改为直接链路，$z$ 不再毒化任何分量。

**用原数据校验**：$y$ 到 $x$ 取 $y\to z\to x$ 为 $1+50=51$，小于直接链路 $x$–$y$ 的 60，与 $D_y(x)=51$ 一致；$z$ 到 $x$ 取直接链路 50，与 $D_z(x)=50$ 一致；$x$ 到 $y$ 取 $x\to z\to y$ 为 $50+1=51$，与 $D_x(y)=51$ 一致。最终结果与不使用毒性逆转时相同，但不再经历数值持续递增的过程。

**补充说明（非课件原文，为本次整理时的补充）**：课件提出的问题「毒性逆转能否完全解决计数到无穷问题」，在后续课程语境下的答案是：毒性逆转只能切断两个节点之间相互引用对方形成的环路；当环路包含三个或更多节点时，仍然可能出现计数到无穷。课件本页与后续页未就此展开。

### 5.4.8 LS 与 DV 算法的比较

课件（原 PDF 第 58 页）从三个方面比较链路状态算法与距离向量算法：

| 比较维度 | LS（链路状态） | DV（距离向量） |
| --- | --- | --- |
| 报文复杂度（message complexity） | 设有 $n$ 个节点、$E$ 条链路，共发送 $O(nE)$ 条报文 | 只在邻居之间交换报文 |
| 收敛速度（speed of convergence） | 算法复杂度 $O(n^2)$；可能出现振荡（oscillations） | 收敛时间不定（varies）；可能出现路由环路（routing loops）、计数到无穷问题 |
| 健壮性（robustness）：路由器发生故障时会怎样 | 节点可能通告错误的链路代价；但每个节点只计算自己的路由表，错误影响限于本节点 | 节点可能通告错误的路径代价；并且每个节点的路由表会被其他节点使用，错误会在网络中传播（error propagate thru network） |

报文复杂度一栏中，$O(nE)$ 指共有 $n$ 个节点、$E$ 条链路时全网需要发送的链路状态报文总量级；$O(n^2)$ 指单次 Dijkstra 计算在朴素实现下的比较次数量级。收敛速度一栏中，LS 的振荡指链路代价与流量相关时，各节点按同一份代价信息同时改选路径，可能导致下一轮代价再次变化而往返摆动；DV 的收敛时间取决于拓扑与事件发生的时点，无法给出固定量级。

### 5.4.9 层次路由（Hierarchical routing）

#### 5.4.9.1 平面路由设想的局限

课件（原 PDF 第 59 页）指出，此前讨论的所有路由算法都建立在一种理想化（idealization）之上：all routers identical（所有路由器相同）、network "flat"（网络是平坦的，即所有路由器彼此对等、不分层次、没有管理边界）。课件明确说明这在实际中并不成立（… not true in practice），原因有两条。

第一条是规模（scale）。当网络中的目的地数量达到数十亿（billions of destinations）时：路由表无法存放所有目的地的条目（can't store all dest's in routing tables）；路由表的交换报文会把链路占满（routing table exchange would swamp links），即周期性的全网路由信息交换所占用带宽超过链路容量。

第二条是管理自治（administrative autonomy）：互联网是「网络的网络」（internet = network of networks），由多个独立管理的网络互联而成；每个网络的管理者（network admin）可能希望控制自己网络内部的路由方式。

#### 5.4.9.2 自治系统与网关路由器

层次路由的处理办法是把路由器聚合成分区，称为自治系统（autonomous system, AS，原 PDF 第 60 页）：同一个 AS 内的路由器运行同一种路由协议，称为 intra-AS 路由协议（域内路由协议）；不同 AS 内的路由器可以运行不同的 intra-AS 路由协议（routers in different AS can run different intra-AS routing protocol）。

网关路由器（gateway router）是 AS 中的特殊路由器，其职责有两项：一是与 AS 内所有其他路由器一起运行 intra-AS 路由协议（run intra-AS routing protocol with all other routers in AS）；二是同时负责通往本 AS 之外目的地的路由（also responsible for routing to destinations outside AS），为此与其他 AS 的网关路由器运行 inter-AS 路由协议（域间路由协议）。

因此，一个 AS 内部的路由计算与 AS 之间的路由计算由两类不同的协议分别完成：前者在整个 AS 内保持一致，后者只在各 AS 的网关路由器之间运行。

---

## 5.5 Internet 中的路由（Routing in the Internet）

### 5.5.1 AS 内路由与 AS 间路由的分工（Intra-AS and Inter-AS routing）

#### 5.5.1.1 网关（Gateway）的双重角色

网关（gateway）是位于自治系统边缘的路由器，它同时承担两类路由功能：与其他 AS 的网关一起执行 AS 间路由（inter-AS routing）；与本 AS 内的其他路由器一起执行 AS 内路由（intra-AS routing）。因此，一个网关路由器上同时活跃着两套路由协议，它们共同向同一张路由表（routing table）写入转发条目。

课件给出的三自治系统拓扑（原 PDF 第 61 页图）中，各 AS 的组成与互联关系为：AS A 内部有若干路由器（图中以 a、b、c、d 标记内部节点与网段），并有两台网关路由器 A.a 与 A.c；AS B 内部有 a、b、c 三个节点，网关路由器为 B.a；AS C 内部有 a、b、c 三个节点，网关路由器为 C.b。图中明确可读出的 AS 间链路是 C.b—A.a 与 C.b—B.a；另有一条连接 AS A 与 AS B 的 AS 间链路，其起点在图中同时存在 A.a 与 A.c 两台网关，本页呈现下无法确定它落在 A.a 还是 A.c（第 62 页的路径图把它画在 A.c 一侧，第 75 页的域间路由图存在同样的判定困难）。A.a 与 A.c 同时存在，说明 AS A 有两台网关路由器分别与其他 AS 相连。

路由器的双重角色在网关 A.c 的协议栈中可以直接看到（原 PDF 第 61 页下半部分 inter-AS, intra-AS routing in gateway A.c）：该协议栈自下而上分为三层——physical layer（PHY，物理层）、link layer（DL，链路层）、network layer（网络层）。在 network layer 内部并排放置两个方框，分别是 Intra-AS routing algorithm（AS 内路由算法）与 Inter-AS routing algorithm（AS 间路由算法），两个方框各自用箭头指向它们共同维护的 ROUTING TABLE（路由表）。协议栈下方画出该网关的三个网络接口，分别标注 to/from A.b、to/from A.d、to/from B.a，表示 A.c 的两条 AS 内链路（指向 A.b、A.d）和一条 AS 间链路（指向 B.a）。

这一段结构说明了一个事实：转发决定只有一张路由表，但路由表的条目由两个来源不同的进程共同写入——AS 内的条目来自本 AS 的域内协议，AS 间的条目来自域间协议。

#### 5.5.1.2 端到端路径上两类路由的接续

课件在同一个拓扑上叠加了一台源主机 Host h1 与一台目的主机 Host h2，并用三种不同线型标出数据报从 h1 到 h2 所经过的三段路径（原 PDF 第 62 页图）：

1. **Intra-AS routing within AS A（AS A 内的域内路由）**：从 Host h1 出发，经 AS A 内的接入网段与内部路由器，最终到达网关 A.c 之前的路径。
2. **Inter-AS routing between A and B（A 与 B 之间的域间路由）**：从网关 A.c 到网关 B.a 这一段跨越 AS 边界。
3. **Intra-AS routing within AS B（AS B 内的域内路由）**：从网关 B.a 经 AS B 内部到达 Host h2。

由此得到域内/域间路由的分工结论：数据报在同一个 AS 内部移动时，由该 AS 的域内协议决定路径；数据报跨出 AS 边界的那一跳（准确地说，是网关到对端网关的那一段），由域间协议决定；一个端到端路径由若干段域内路径与若干段域间路径拼接而成，没有任何一个协议掌握从源到目的的完整路径。课件随后说明：接下来将考察 Internet 中具体的 inter-AS 与 intra-AS 路由协议（We'll examine specific inter-AS and intra-AS Internet routing protocols shortly）。

（原 PDF 第 63 页为第 5 章章节目录页，内容为 5.1 简介、5.2 虚电路与数据报网络、5.3 路由器内部、5.4 路由算法、5.5 Internet 中的路由、5.6 IP：网际协议，其中 5.5 被标出表示当前进度；该页为重复的目录页，不另设正文小节。）

### 5.5.2 域内路由协议（Intra-AS routing / Interior Gateway Protocols）

域内路由协议又称内部网关协议（Interior Gateway Protocols, IGP，原 PDF 第 64 页）。课件列出最常用的三种 IGP：

- **RIP**：Routing Information Protocol（路由信息协议）；
- **OSPF**：Open Shortest Path First（开放最短路径优先）；
- **IGRP**：Interior Gateway Routing Protocol（内部网关路由协议），Cisco 专有（Cisco propr.）。

三者分别基于 5.4 节学过的距离向量算法（RIP、IGRP）与链路状态算法（OSPF）。

#### 5.5.2.1 RIP：Routing Information Protocol

RIP 的基本定位与参数（原 PDF 第 65 页）为：所用算法是距离向量算法（distance vector algorithm）；1982 年被包含进 BSD-UNIX 发行版（included in BSD-UNIX Distribution in 1982）；距离度量（distance metric）是跳数（# of hops），最大值为 15 跳；距离向量每 30 秒交换一次（exchanged every 30 sec）；承载消息的名称是 Response Message，又称 advertisement（通告）；单条通告最多包含到 25 个目的网络的路径（route to up to 25 destination nets）。

课件在距离度量处附了一个问题 Can you guess why?（你能猜出为什么最大只有 15 跳吗？），正文没有给出答案。此处按标准 RIP 设计背景补充说明（**补充解释，非课件原文**）：RIP 把 16 视为无穷大（infinite distance = 16 hops，见 5.5.2.2 的链路失效处理），把可达直径限制为 15 跳，可以限定距离向量算法在链路失效时「计数到无穷」的持续时间上限，代价是 RIP 只能用于直径不超过 15 跳的网络。

在课件采用的简化、RIPv1 式说明中，通告重点为目的网络与跳数，下一跳根据发送邻居确定。不能将“通告不携带下一跳地址”推广到所有 RIP 版本：RIPv2 有 Next Hop 字段，并支持鉴别信息。参见 [RFC 2453，4.1 与 4.4](https://www.rfc-editor.org/rfc/rfc2453#section-4.4)。

课件给出一个路由表实例（原 PDF 第 66 页图）。源图给出一个由路由器 A、D、B、C 与网段 w、x、y、z 构成的网络：网段 w 接在路由器 A 上，A 与 D 之间由网段 x 相连，D 与 B 之间由一个未标注名称的网段相连，B 与网段 y 相连，网段 y 再经过若干跳（源图用省略的形式表示中间部分）到达网段 z；路由器 C 挂在 D 的下方，与 D 直接相连。源图下方的方框给出路由器 D 中的路由表：

| Destination Network（目的网络） | Next Router（下一跳路由器） | Num. of hops to dest.（到目的的跳数） |
|---|---|---|
| w | A | 2 |
| y | B | 2 |
| z | B | 7 |
| x | -- | 1 |
| …. | …. | …. |

对表中每一行的读法（依据源图拓扑）：

- **第 1 行，w / A / 2**：D 到网段 w 要经过路由器 A，跳数是 2。D 与 A 之间隔着一个网段 x，数据报从 D 出发经网段 x 到达 A（第 1 跳），再由 A 转发到 w（第 2 跳），故为 2。
- **第 2 行，y / B / 2**：D 经中间网段到 B 为第 1 跳，B 到 y 为第 2 跳。
- **第 3 行，z / B / 7**：D 到网段 z 的下一跳仍然是 B，但总跳数为 7，即从 D 出发经 B、y 及后续中间路由器到达 z 共需 7 跳。这一行说明 RIP 的下一跳只记录邻居路由器，与目的网络有多远无关——无论目的网络在 2 跳外还是 7 跳外，只要去往该目的的第一段都指向 B，下一跳字段就都是 B。源图未标出 y 与 z 之间中间路由器的数量，因此 7 跳无法逐跳分解。
- **第 4 行，x / -- / 1**：网段 x 直接连接在 D 上（D 的直连网络），下一跳字段为空，因为无需再经任何路由器转发；跳数为 1，表示只需一跳即可到达该网段。
- **第 5 行，…. / …. / ….**：源图中的省略行，表示该表中还有其他目的网络条目，源图没有给出具体内容。

这四行数据共同体现了 RIP 路由表的三元组结构——目的网络、下一跳、跳数，以及「直连网络的下一跳为空、跳数为 1」这一约定。

#### 5.5.2.2 RIP 的链路失效与恢复（Link failure and recovery）

RIP 用定时器检测邻居与链路的存活：如果在 180 秒内没有听到某个邻居的通告（if no advertisement heard after 180 sec），就判定该邻居/链路已死亡（neighbor/link declared dead）。判定死亡之后的处理流程（原 PDF 第 67 页）为：

1. 使经由该邻居的路由项失效（routes via neighbor invalidated），即把经过该邻居的所有目的网络的路径作废。
2. 向邻居发送新的通告（new advertisements sent to neighbors），把路由变化发布出去。
3. 邻居转而发出它们自己的新通告（neighbors in turn send out new advertisements），但仅当它们自己的路由表发生了变化（if tables changed）时才发送。
4. 链路失效信息迅速传播到整个网络（link failure info quickly propagates to entire net）。
5. 使用毒性逆转（poison reverse）防止乒乓环路（poison reverse used to prevent ping-pong loops），其中无穷距离定义为 16 跳（infinite distance = 16 hops）。

RIP 用度量 16 表示不可达。需要区分两种操作：路由失效后把该目的的度量置为 16，是失效路由的毒化；毒性逆转则是对经某邻居学到的路由，向该邻居反向通告度量 16，即使路由当前仍然有效也可这样通告，以避免对方再经自己返回该目的。它可防止两节点相互引用形成的环路，但不能彻底消除更大环路。参见 [RFC 2453，3.4.3—3.4.4](https://www.rfc-editor.org/rfc/rfc2453#section-3.4.3)。

#### 5.5.2.3 RIP 表的处理与承载层次（RIP table processing）

课件指出两个事实（原 PDF 第 68 页）：RIP 路由表由一个应用层进程管理，该进程称为 route-d，即 routed 守护进程（daemon）（RIP routing tables managed by application-level process called route-d (daemon)）；RIP 的通告报文封装在 UDP 数据包中发送，并按周期重复（advertisements sent in UDP packets, periodically repeated）。源图与正文中同时出现 route-d 与协议栈图中的 routed 两种写法，指的是同一个 RIP 守护进程。

课件用两个并排的协议栈说明这一跨层结构：

| 层次（自上而下） | 左侧路由器 | 右侧路由器 |
|---|---|---|
| 应用层 | routed（守护进程，椭圆框） | routed（守护进程，椭圆框） |
| 传输层 | transport (UDP) | transport (UDP) |
| 网络层 | network (IP)，其中标出 routing tables（路由表） | network (IP)，其中标出 routing tables（路由表） |
| 链路层 | data link | data link |
| 物理层 | physical | physical |

图中箭头标出的两条路径为：其一是**实际线路上的传输路径**，左路由器 routed 进程产生的报文自上而下穿过 UDP → IP → data link → physical，经物理介质到达右路由器，再自下而上穿过 physical → data link → IP → UDP 交由右侧 routed 进程处理；其二是**进程对路由表的读写路径**，每个 routed 进程向上连接本机 routing tables，即路由表存放在 network (IP) 层，但由应用层的 routed 进程负责填写与更新。由此得到一个明确结论：RIP 是运行在应用层的路由协议——它利用 UDP 作为传输手段，而它的计算结果（路由表）被 IP 层用于转发；这与 OSPF、BGP 的承载方式不同。

#### 5.5.2.4 RIP 路由表的真实实例（RIP table example）

课件给出路由器 giroflee.eurocom.fr 上的实际路由表（原 PDF 第 69 页）。表中的字段为 Destination（目的地址）、Gateway（网关，即下一跳）、Flags（标志）、Ref（引用计数）、Use（使用计数）、Interface（出接口）。完整表格逐行呈现如下：

| Destination | Gateway | Flags | Ref | Use | Interface |
|---|---|---|---|---|---|
| 127.0.0.1 | 127.0.0.1 | UH | 0 | 26492 | lo0 |
| 192.168.2. | 192.168.2.5 | U | 2 | 13 | fa0 |
| 193.55.114. | 193.55.114.6 | U | 3 | 58503 | le0 |
| 192.168.3. | 192.168.3.5 | U | 2 | 25 | qaa0 |
| 224.0.0.0 | 193.55.114.6 | U | 3 | 0 | le0 |
| default | 193.55.114.129 | UG | 0 | 143454 | （源图该格为空） |

对表中每一行的解释：

- **127.0.0.1 / 127.0.0.1 / UH / 0 / 26492 / lo0**：回环地址（loopback）条目。Flags 中的 `H` 表示该路由指向一台主机（host）而不是一个网络（net）；出接口 lo0 是回环接口。Use 计数 26492 表示该条目已被使用了 26492 次。
- **192.168.2. / 192.168.2.5 / U / 2 / 13 / fa0**：目的为 192.168.2.0 网段（表中以 192.168.2. 的省略写法表示一个网段前缀），下一跳 192.168.2.5，Flags 为 `U`（Up，路由可用），Ref 为 2，Use 为 13，出接口 fa0。
- **193.55.114. / 193.55.114.6 / U / 3 / 58503 / le0**：目的 193.55.114.0 网段，下一跳 193.55.114.6，Ref 3，Use 58503，出接口 le0。
- **192.168.3. / 192.168.3.5 / U / 2 / 25 / qaa0**：目的 192.168.3.0 网段，下一跳 192.168.3.5，Ref 2，Use 25，出接口 qaa0。
- **224.0.0.0 / 193.55.114.6 / U / 3 / 0 / le0**：目的 224.0.0.0 是路由多播地址（route multicast address）。该条目的 Use 计数为 0，表示该多播路由还没有被实际转发使用过；出接口同样是 le0。
- **default / 193.55.114.129 / UG / 0 / 143454 / （空）**：默认路由（default route），Flags 中的 `G` 表示该路由是经网关（Gateway）的路由，即凡是表中没有更具体匹配的目的地址，都交给 193.55.114.129 转发；Use 计数 143454 说明该条目承担了绝大多数转发量。源图中该行的 Interface 列为空，本笔记不补造该接口名。

课件对该表给出五条结论：该路由器连接三个 C 类网络（LAN）——对应表中 192.168.2.、193.55.114.、192.168.3. 三条 `U` 类路由，Flags 中没有 `G`，即它们都是直连网络；该路由器只知道与它直连的 LAN 的路由——除了直连条目、回环条目、多播条目之外，其余流量一律交给 default 条目；默认路由器用于「向上」走（default router used to "go up"）——即本区域内的主机与 LAN 只需一条 default 路由把出网流量交给上层路由器，无需在本地维护全网的明细路由；路由多播地址为 224.0.0.0——该地址段的报文不按单播路由转发，因此表中单独列出；回环接口（loopback interface）用于调试（for debugging）——对应 lo0 与 127.0.0.1 条目。

这里需要与该页之前第 66 页的小表对照：第 66 页的表是 RIP 内部通告所携带的三元组（目的网络、下一跳、跳数），用于说明距离向量的内容；第 69 页的表是操作系统内核中的实际路由表（含 Flags、Ref、Use、Interface 等管理字段），用于说明 RIP 计算结果落到转发平面后的形态。两表格式不同、用途不同，不应混用。第 69 页的表没有给出跳数（hops）列，因此无法从该表直接读出各目的网络的距离度量。

#### 5.5.2.5 OSPF：Open Shortest Path First

OSPF 的基本定位（原 PDF 第 70 页）为：「开放」（open）的含义是公开可用（publicly available），即协议规范公开，不属任何厂商专有；采用链路状态算法（uses link state algorithm），其三个环节为——LS 分组的分发（LS packet dissemination），每个节点把描述自己链路状态的分组发送出去；每个节点持有拓扑图（topology map at each node），节点收集到全部 LS 分组后在本地构造出完整的网络拓扑图；用 Dijkstra 算法计算路由（route computation using Dijkstra's algorithm），在拓扑图上计算以本节点为源的最短路径树。此外，OSPF 的通告对每一个邻居路由器携带一个条目（OSPF advertisement carries one entry per neighbor router），即链路状态通告逐条描述本路由器到各个邻居链路的状态与代价，而不是像 RIP 那样描述「到某个目的网络的距离」；通告通过泛洪（flooding）扩散到整个 AS（advertisements disseminated to entire AS）。

RIP 与 OSPF 的差别由此明确：RIP 的通告内容是到各目的网络的向量，接收方只需比较距离；OSPF 的通告内容是各条链路的状态，接收方需要累积出拓扑图后再自行运行最短路径计算。因此 RIP 的每条通告量小但传播范围只到邻居，OSPF 的单条通告只在区域内泛洪一次但每个节点都掌握全区域拓扑。

#### 5.5.2.6 OSPF 相对 RIP 的「高级」特性（OSPF "advanced" features, not in RIP）

课件（原 PDF 第 71 页）列出五项 OSPF 独有（RIP 不具备）的特性：

1. **安全性（security）**：所有 OSPF 报文都经过鉴别/认证（all OSPF messages authenticated），目的是防止恶意入侵（to prevent malicious intrusion）。**补充说明（非课件原文）**：无鉴别的路由通告可能被伪造，但是否带鉴别字段取决于协议版本和配置，不能因为使用 UDP 就判定无鉴别。RIPv2 已定义鉴别机制，故此处不能把 RIP 整体说成没有鉴别字段。参见 [RFC 2453，4.1](https://www.rfc-editor.org/rfc/rfc2453#section-4.1)。
2. **允许多条等代价路径（multiple same-cost paths allowed）**，而 RIP 中只保留一条路径（only one path in RIP）。这一差别来自算法本身：Dijkstra 计算完成后，可以同时选择多条代价值相同的最短路径；距离向量算法在收到等值的多个下一跳时通常只保留一条。
3. **对每条链路可以为不同的 TOS 设置多个代价度量（multiple cost metrics for different TOS）**。课件给的例子是卫星链路（satellite link）：对尽力而为（best effort）业务把该链路的代价设为「低」（low），对实时（real time）业务把该链路的代价设为高（high）。也就是说，同一条链路在不同服务类型下会有不同的最短路径结果。
4. **集成的单播与多播支持（integrated uni- and multicast support）**：多播 OSPF（Multicast OSPF, MOSPF）使用与 OSPF 相同的拓扑数据库（same topology data base），即多播路由不需要再单独跑一套拓扑发现。
5. **在大规模域中使用层次化 OSPF（hierarchical OSPF in large domains）**，见 5.5.2.7。

#### 5.5.2.7 层次化 OSPF（Hierarchical OSPF）

课件给出层次化 OSPF 的拓扑形态（原 PDF 第 72 页图）：上方一片被标注为 backbone（主干区域）的连通路由器集合，下方划分为 area 1、area 2、area 3 三个区域，每个区域用虚线椭圆圈出，区域内部有若干 internal routers（内部路由器）。图中用引线标出四类路由器：boundary router（边界路由器）指向主干区域中位于图上方的那台路由器，它连接 AS 外部；backbone router（主干路由器）指向主干区域内的路由器；area border routers（区域边界路由器）指向同时连接主干区域与某个非主干区域的路由器（area 1、area 2、area 3 各有一台这样的路由器与主干相连）；internal routers（内部路由器）指向 area 3 内部的路由器，即完全不与主干区域直接相连的路由器。

课件的文字说明（原 PDF 第 73 页）逐条定义了这个两级层次：

| 层级/角色 | 课件给出的规则 |
|---|---|
| 总体结构 | **两级层次：本地区域（local area）+ 主干（backbone）**（two-level hierarchy） |
| 链路状态通告的范围 | **链路状态通告只在本区域内传播（link-state advertisements only in area）** |
| 每节点的拓扑知识 | **每个节点拥有本区域的详细拓扑；对其他区域的网络只知道方向（最短路径）**（each node has detailed area topology; only know direction (shortest path) to nets in other areas） |
| 区域边界路由器（area border routers） | **「汇总」（summarize）本区域内到各网络的距离，并向其他区域边界路由器通告** |
| 主干路由器（backbone routers） | **运行仅限于主干的 OSPF 路由（run OSPF routing limited to backbone）** |
| 边界路由器（boundary routers） | **连接到其他 AS（connect to other AS'es）** |

需要注意术语上的区分：boundary router 承担的是 AS 之间的连接（即 5.5.1 中的「网关」），而 area border router 承担的是同一 AS 内区域之间的连接，两者在层次化 OSPF 的图中都出现，但处在不同的边界上。源图中 boundary router 的另一端通向 AS 外部的连接未在本页画出。

#### 5.5.2.8 IGRP：Interior Gateway Routing Protocol

课件第 74 页标题为 IGRP，介绍其 Cisco 专有背景、20 世纪 80 年代中期出现、距离向量算法，以及延迟、带宽、可靠性、负载等多个度量；末两条写作“使用 TCP 交换更新”和“通过 DUAL 实现无环路路由”。

**课件纠错与协议区分**：IGRP 直接由 IP 承载，使用协议号 9，不使用 TCP。DUAL 属于 EIGRP；EIGRP 使用自己的可靠传输机制，并由 IP 协议号 88 标识，同样不能写成 TCP。课件把 IGRP、EIGRP 的特征混在了一起。参见 [IANA 协议号登记表](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml) 与 [RFC 7868，DUAL 和可靠传输机制](https://www.rfc-editor.org/rfc/rfc7868)。

把三种 IGP 与后面要讲的 BGP 放在一起对照，可以看出一处易混点：

| 协议 | 算法类别 | 承载路由更新的传输层协议 | 管理进程形态 |
|---|---|---|---|
| RIP | 距离向量 | UDP | 应用层守护进程 routed（route-d） |
| IGRP | 距离向量 | IP（协议号 9；更正课件） | Cisco 路由器内部进程 |
| OSPF | 链路状态 | 课件未说明其承载方式（见下方说明） | 运行于路由器内部的 IP 层协议 |
| BGP | 路径向量 | TCP（见 5.5.3.2） | 网关路由器上的模式进程 |

课件在 OSPF 部分只说明了链路状态算法、通告内容与泛洪方式，没有给出 OSPF 报文承载在哪个传输层协议之上的表述，因此本笔记不补写该结论；章末习题正是围绕 RIP、OSPF、BGP 各自直接封装的协议提问，属于本课件的考查点。

### 5.5.3 域间路由协议（Inter-AS routing）

#### 5.5.3.1 域间路由的拓扑形态

课件（原 PDF 第 75 页图）给出与 5.5.1 相同的拓扑：三个 AS（A、B、C）各自用矩形平面表示，矩形内画出本 AS 内部的网段（小椭圆）与路由器，网关路由器为 C.b、A.a、B.a。图中以红色加粗线段突出显示连接网关路由器的域间链路。其中 C.b—B.a 与 C.b—A.a 两段读取明确；另一段红色线段位于 A.a 与 B.a 之间，其具体连接对存在读取不确定性。该页无文字要点，其作用是给出「AS 之间如何通过网关互联」的图形背景，由此可以明确的结论是：域间路由只在网关路由器之间进行，AS 内部的路由器不参与域间路由。

#### 5.5.3.2 BGP：Border Gateway Protocol

BGP 的定位（原 PDF 第 76 页）：BGP 是事实标准（the de facto standard），即 Internet 上的域间路由协议。BGP 为每个 AS 提供三种能力：

1. 从相邻 AS 获取子网可达性信息（obtain subnet reachability information from neighboring ASs）；
2. 把可达性信息传播给本 AS 内所有路由器（propagate reachability information to all AS-internal routers）；
3. 依据可达性信息和策略，确定到各子网的良好路由（determine good routes to subnets based on reachability information and policy）。注意课件用的是 good routes 而不是 least-cost routes，因为域间路由的选择受策略（policy）约束，而非单纯的代价最小。

此外，BGP 使一个子网能够向 Internet 的其余部分宣告自己的存在：I am here（我在这里）。

BGP 的工作方式是路径向量协议（path vector protocol，原 PDF 第 77 页）：它与距离向量协议相似（similar to distance vector protocol）；每个边界网关向其邻居（peers，对等体）广播到达目的地的整条路径，即 AS 的序列（each border gateway broadcast to neighbors (peers) entire path (i.e, sequence of ASs) to destination）；课件给出的例子是，网关 X 可能向对等体发送它到目的地 Z 的路径，写作

$$\text{Path}(X,Z) = X, Y_1, Y_2, Y_3, \dots, Z$$

即路径由从 X 出发依次经过的 AS 编号序列构成，一直到目的地 Z。路径向量与距离向量的关键区别是：距离向量只传播「到目的地的距离值 + 下一跳」，接收方无法知道对方走的是哪条路；路径向量传播完整的 AS 序列，因此接收方可以看出该路径是否经过自己、是否构成环路，也可以据此实施策略（决定是否采纳或是否继续向外通告）。**补充说明（非课件原文）**：路径向量中携带完整 AS 序列，正是运营商能在域间路由上执行策略判定的数据基础。

#### 5.5.3.3 BGP 的路由策略（BGP routing policy）

课件（原 PDF 第 78、79 页，两页使用同一拓扑与图例）给出一个用于说明策略的网络。图例（legend）说明：大块的浅色区域表示提供商网络（provider network），小的圆形节点表示客户网络（customer network）。拓扑中：A、B、C 是提供商网络（provider networks）；X、W、Y 是客户网络，且都是桩网络（stub network）——桩网络指只通过一条或少数几条链路与外部的提供商相连、不承担为其他网络转发流量的网络；连接关系为 W 接在 A 上，A 与 B、A 与 C 之间有直连，B 与 X 相连，C 与 X 相连，Y 接在 C 上。

**策略条目一（原 PDF 第 78 页）**：X 是双归属的（dual-homed），它同时连接到两个网络（attached to two networks），图中 X 同时连到提供商 B 与提供商 C；X 不希望从 B 进来、再经由 X 转发到 C（X does not want to route from B via X to C）；因此 X 不会向 B 通告一条到 C 的路由（so X will not advertise to B a route to C）。这一条说明的是桩网络的策略逻辑：X 同时接入 B 和 C，是为了获得冗余或更好的出口，而不是为了替 B 和 C 之间的流量做中转（那会消耗 X 自己的链路与设备资源，且 X 从中得不到收益）。实现这一意图的手段是不通告——X 不把「到 C 的路由」告诉 B，B 便无从得知经过 X 可以到达 C。

**策略条目二（原 PDF 第 79 页）**：课件接着以一个具体通告序列提出问题：A 向 B 通告路径 AW（A advertises to B the path AW），即「从 A 出发经 W 这条路径」，供 B 使用，A 与 W 的关系是提供商与客户；B 向 X 通告路径 BAW（B advertises to X the path BAW），即 B 把 A 给自己的路径前面加上自己，变成 B→A→W 通告给它的客户 X；问题是 B 是否应当向 C 通告路径 BAW（should B advertise to C the path BAW?）。答案是绝对不应该（No way!），理由是：无论 W 还是 C 都不是 B 的客户（neither W nor C are B's customers），B 为 C 转发形如 CBAW 的流量得不到任何收益（B gets no "revenue" for routing CBAW）；B 想让 C 只能经由 A 到达 W（B wants to force C to route to W via A），即把 C→A→W 这段流量推给 A 承担；B 只想为自己与客户之间的流量做路由（B wants to route only to/from its customers!）。

把两条策略合起来看，可以归纳出域间路由选择的基本规律：提供商向客户通告「可以经我到达我及我的其他客户/提供商」的路径；提供商之间（对等/兄弟关系）的通告受到严格的收益约束，超出直接收益的转发会被主动抑制；客户网络通过限制通告范围，避免自己成为上游之间的中转通道。需要强调：这些取舍全部由策略决定，而不是由链路代价决定——这正是 5.5.4 中「为什么域内与域间路由必须不同」的第一条理由。

### 5.5.4 为什么域内与域间路由必须不同（Why different Intra- and Inter-AS routing?）

课件（原 PDF 第 80 页）从三个方面给出回答。

**策略（policy）**。域间（inter-AS）：管理者希望控制自己的流量如何被路由，以及谁可以经由自己的网络进行路由（admin wants control over how its traffic routed, who routes through its net）。域内（intra-AS）：由单一管理者管理，因此不需要做策略决策（single admin, so no policy decisions needed）。

**规模（scale）**。层次化路由节省路由表规模，减少更新流量（hierarchical routing saves table size, reduced update traffic）。

**性能（performance）**。域内（intra-AS）：可以专注于性能（can focus on performance），因为不受策略约束，最短路径/最小代价即为目标。域间（inter-AS）：策略可能压倒性能考量（policy may dominate over performance），即选出的路径未必是代价最小的路径。

这三条与 5.4 节引进层次路由的动机、以及 5.5.3.3 中 BGP 的策略实例完全对应：域内协议（RIP、OSPF、IGRP）追求算法上的最优路由，域间协议（BGP）首先服从商业策略与可达性约束，性能只在策略允许的范围内作比较。

---

### 习题 1：RIP、OSPF 与 BGP 报文的直接封装协议（原 PDF 第 81 页）

#### 题干（原文完整保留）

**Exercise-1**

1. The protocols for directly encapsulating RIP、OSPF and BGP messages are

A. TCP、UDP、IP

B. TCP、IP、UDP

C. UDP、TCP、IP

D. UDP、IP、TCP

（题目问：直接封装 RIP、OSPF 与 BGP 报文的协议依次是什么。）

#### 解题依据

本题的四个选项是 TCP、UDP、IP 三种协议的部分排列，题目要求按 RIP、OSPF、BGP 的顺序一一对应，判断依据是各路由协议在协议栈中所处的层次以及它所直接使用的下层承载协议，这三点在前面的小节中均有对应叙述。

第一，**RIP（Routing Information Protocol，路由信息协议）** 是 Intra-AS（自治系统内部）路由协议，属于距离向量（distance vector）算法，其距离度量是跳数（# of hops，最大值为 15 跳），距离向量每 30 秒交换一次。课件明确指出，RIP 的路由表由一个应用层的进程 route-d（daemon，守护进程）管理，RIP 的通告（advertisement）是装在 UDP 报文中发送的，并且周期性地重复（5.5.2.3）。因此 RIP 报文直接被 UDP 封装。

第二，**OSPF（Open Shortest Path First，开放最短路径优先）** 同样属于 Intra-AS 路由协议，但算法是链路状态（link state）算法：各节点用泛洪方式扩散链路状态分组，每个节点持有全网拓扑图，再用 Dijkstra 算法计算路由。OSPF 的报文不经过传输层协议，而是直接由 IP 数据报承载（5.5.2.5）。

第三，**BGP（Border Gateway Protocol，边界网关协议）** 是 Internet 的 Inter-AS（自治系统之间）路由事实标准，属于路径向量（path vector）协议，每个边界网关向其对等体（peer）通告到达目的地的 AS 路径。BGP 消息由 TCP 承载，以取得可靠的、面向连接的传输（5.5.3.2）。

#### 逐步求解

第 1 步：确定 RIP 的直接封装协议。依据「RIP 通告装于 UDP 报文、由应用层 route-d 进程周期发送」，RIP 对应 UDP。排除选项 B（B 的第一项为 TCP）。

第 2 步：确定 OSPF 的直接封装协议。依据「OSPF 使用链路状态算法，链路状态分组由 IP 直接承载，不经传输层」，OSPF 对应 IP。排除选项 A（A 的第二项为 UDP）与选项 C（C 的第二项为 TCP）。

第 3 步：确定 BGP 的直接封装协议。依据「BGP 使用 TCP 向对等体通告 AS 路径」，BGP 对应 TCP。至此只剩选项 D。

第 4 步：写出结果。三项依次为 UDP、IP、TCP，与选项 D 完全一致。

#### 逐项排除

- 选项 A（TCP、UDP、IP）：把 RIP 判成 TCP、把 OSPF 判成 UDP。RIP 使用 UDP 而非 TCP；OSPF 直接跑在 IP 上，不用 UDP。错误。
- 选项 B（TCP、IP、UDP）：把 RIP 判成 TCP、把 BGP 判成 UDP。RIP 用 UDP；BGP 使用 TCP 而非 UDP。错误。
- 选项 C（UDP、TCP、IP）：把 OSPF 判成 TCP、把 BGP 判成 IP。OSPF 不经过 TCP；BGP 需要 TCP 的可靠有序传输，不走裸 IP。错误。
- 选项 D（UDP、IP、TCP）：RIP 对应 UDP，OSPF 对应 IP，BGP 对应 TCP，三项均与前面各小节的叙述相符。正确。

#### 答案

**D. UDP、IP、TCP**，即 RIP 报文直接被 UDP 封装，OSPF 报文直接被 IP 封装，BGP 报文直接被 TCP 封装。

#### 用原题数据校验

校验点 1（顺序）：题目要求的对应顺序是「RIP、OSPF、BGP」，选项 D 给出「UDP、IP、TCP」。把三者按位对齐：RIP↔UDP、OSPF↔IP、BGP↔TCP，与第 1—3 步分别得到的结论逐项吻合，说明顺序没有被颠倒。

校验点 2（与课件其它陈述的一致性）：课件在 IGRP 部分说明 IGRP（Interior Gateway Routing Protocol，Cisco 私有协议）使用 TCP 交换路由更新。这说明课件本身明确区分了不同路由协议的不同承载方式——RIP 走 UDP、IGRP 走 TCP、OSPF 直接走 IP，因此「所有路由协议都跑在同一种传输协议上」的推断与课件不符，选项 A、B、C 都隐含了这种错误对应。由此进一步确认选项 D。

校验点 3（完备性）：选项集合 {TCP, UDP, IP} 的 6 种全排列中，本题给出了 4 种。三个待填空位各对应一个唯一正确的协议，因此正确答案在给定选项中唯一，不存在多解；D 是其中唯一同时满足 RIP=UDP、OSPF=IP、BGP=TCP 的选项。

#### 与本题相关的协议承载对照

| 路由协议 | 类别（按作用域） | 算法类型 | 直接封装协议 | 课件依据 |
| --- | --- | --- | --- | --- |
| RIP | Intra-AS（IGP） | 距离向量，度量=跳数（最大 15） | UDP（通告装在 UDP 报文中，由应用层 route-d 周期发送） | 第 65、68 页 |
| OSPF | Intra-AS（IGP） | 链路状态 + Dijkstra | IP（链路状态分组由 IP 直接承载） | 第 70 页 |
| IGRP | Intra-AS（IGP，Cisco 私有） | 距离向量（多种度量） | IP，协议号 9（第 74 页误写 TCP，见前文纠错） | 第 74 页 |
| BGP | Inter-AS | 路径向量 | TCP | 第 76、77 页 |

要点：Intra-AS 协议中 RIP 与 IGRP 虽同为距离向量，但承载方式不同（RIP 用 UDP、IGRP 用 TCP），本题只考 RIP；OSPF 是此处唯一不经传输层、直接由 IP 承载的路由协议；Inter-AS 的 BGP 依靠 TCP 提供可靠传输。
