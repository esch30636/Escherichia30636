# 计算机网络 —— 局域网（Chapter 4 Local Area Network）

> 原始课件：`D:\Escherichia30636\计算机网络\Chapter4 Local Area Network.pdf`
> PDF 总页数：39 页
> 整理日期：2026-10-15
>
> 全文按课件原有的章—节—小节顺序组织，保留课件页码编号（4-1～4-39）与原有术语。课件本身只给出页码，未给出「4.1、4.2」形式的节号，本节号为整理时按课件页面顺序补充的稳定编号，与课件页码一一对应，不改变课件原有顺序。

---

## 4.1 LAN 技术总览（课件 4-2）

数据链路层此前已经讲授的内容是：链路层服务（services）、差错检测与纠正（error detection/correction）、多路访问（multiple access）。本章进入局域网技术，包括四项内容：LAN 模型（LAN model）、编址（addressing）、以太网（Ethernet）、集线器与交换机（hubs, switches）。

课件给出的整体图景是：若干「用户主机」（user hosts）连接到一个标为 LAN 的区域；该 LAN 通过一台标为 ROUTER 的设备连到标为 Internet 的区域，Internet 一侧有一台 Web Server。这一结构说明：LAN 内部各主机之间的通信由链路层与物理层技术完成；主机与 Internet 中 Web Server 之间的通信必须经过路由器做网络层转发。因此本章讨论的编址、帧格式、交换设备都只解决「同一 LAN 内部」的交付问题，跨 LAN 的交付由网络层负责。

---

## 4.2 LAN 模型（课件 4-3 ～ 4-5）

### 4.2.1 数据链路层划分为 LLC 子层与 MAC 子层（4-3）

课件把三层模型与子层划分并列画出。自下而上依次为物理层（Physical layer）、数据链路层（Data link layer）、网络层（Network layer）；其中数据链路层在局域网环境下被进一步划分为两个子层：

- **LLC 子层（Logical Link Control，逻辑链路控制）**：位于 MAC 之上、网络层之下。其职能是「为上层提供连接环境」（provide the connection environment to the upper level），即向网络层提供统一的数据链路层服务接口。
- **MAC 子层（Media Access Control，介质访问控制）**：位于 LLC 之下、物理层之上。其职能是「对下层提供介质访问」（providing media access to the lower layer），即解决多个站点如何共享同一传输介质的问题。

划分的依据是两者处理的问题不同。多个站点共享传输介质时，接入规则随介质与拓扑而变（总线、令牌环、无线等各不相同）；而链路层的差错控制、流量控制、复用与解复用等向网络层提供的服务与介质无关。把与介质相关的部分集中在 MAC，与介质无关的部分集中在 LLC，同一套 LLC 就能覆盖多种 MAC。

### 4.2.2 LLC 子层看不到其下的局域网（4-4）

课件画出节点 1（node 1）与节点 2（node 2）两个协议栈，每侧自下而上为 Physical layer、MAC、LLC、Network layer，中间是一个标为「Local area network」的区域。图中三类箭头表示对等层之间的通信关系：

- LLC 与 LLC 之间是一条横贯两侧、跨过整个 LAN 区域的粗双向箭头；
- MAC 与 MAC 之间、Physical 与 Physical 之间的双向箭头分别终止在 LAN 区域的两侧。

图上的说明为「下面的 LAN 对 LLC 子层是不可见的」（The following LAN is invisible for LLC sub layer）。这组箭头表达的是：LLC 实体之间的通信表现为一条直接链路，LLC 不需要知道中间经过怎样的介质与接入方式；MAC 与物理层的通信才真正穿越 LAN。因此 LLC 与具体局域网技术解耦。

同一页下方给出结论性说明：**对同一个 LLC，可以提供多种 MAC 选择**（For the same LLC, several MAC options may be provided）。这正是 4.3 节中 IEEE 802 把 802.2 定为唯一 LLC 标准、而把 802.3、802.4、802.5、802.6、802.11 等并列作为不同 MAC 标准的结构原因。

### 4.2.3 MAC 帧格式与 LLC PDU 格式（4-5）

课件标题为「LLC and MAC」，用三行框图标出 MAC 帧与 LLC PDU 的封装关系。

第一行是 MAC 帧（MAC Frame，课件原图），自左至右字段为：

| 字段 | 含义 |
|------|------|
| MAC Control | MAC 控制 |
| Destination MAC Address | 目的 MAC 地址 |
| Source MAC Address | 源 MAC 地址 |
| Data | 数据 |
| CRC | 循环冗余校验码 |

第二行是 LLC PDU（LLC 协议数据单元），自左至右字段为：

| 字段 | 长度 | 含义 |
|------|------|------|
| DSAP | 1 octet（八位组） | Destination Service Access Point，目的服务访问点 |
| SSAP | 1 octet | Source Service Access Point，源服务访问点 |
| LLC Control | 1 or 2 octets | LLC 控制字段 |
| Information | variable（可变长） | 信息字段 |

图中的虚线表明：整个 LLC PDU 被装入 MAC 帧的 Data 字段；而 DSAP、SSAP 两处再单独展开为第三行的 LLC 地址字段（LLC Address Fields）：

| 比特/字段 | 含义 |
|-----------|------|
| I/G | individual/group，单播/组播标志 |
| DSAP value | DSAP 取值 |
| C/R | command/response，命令/响应标志 |
| SSAP value | SSAP 取值 |

即 DSAP 八位组由 1 比特 I/G 标志加 7 比特 DSAP 取值构成，SSAP 八位组由 1 比特 C/R 标志加 7 比特 SSAP 取值构成。服务访问点（SAP）的作用是指明 LLC 之上的哪一个上层协议或哪个上层实体使用本次链路层服务，从而使同一 MAC 之上可以复用多个上层协议。

> **辨析（整理者补充）**：本页的 MAC 帧画出了「MAC Control」字段，这是 IEEE 802 通用 MAC 帧格式的写法；它与 4.5.5 节起给出的以太网 MAC 帧（以 6 字节目的地址开头、无独立的 MAC Control 字段）不是同一种格式，两者不可混用。本页原图只给出字段的相对位置与长度单位，未给出各字段的字节数，因此此处不补填字节数。

---

## 4.3 IEEE 802 工作组（课件 4-6）

IEEE 802 标准的结构框图如下。框体左端竖排的 **802.1A** 贯穿整列，作为横向上覆盖全部子标准的分区；右侧按协议层次分为三段，自上而下标注为 **LLC**、**MAC**、**PHY**：

| 层次 | 标准 | 内容 |
|------|------|------|
| LLC | 802.1D | Bridge（网桥） |
| LLC | 802.2 | LLC |
| MAC/PHY | 802.3 | CSMA/CD |
| MAC/PHY | 802.4 | Token Bus（令牌总线） |
| MAC/PHY | 802.5 | Token ring（令牌环） |
| MAC/PHY | 802.6 | DBDQ |
| MAC/PHY | 802.11 | Wi-Fi |
| MAC/PHY | …… | 后续补充的其他 MAC/PHY 标准 |

图中的层次关系是：802.1D 位于 802.2 LLC 之上，其余 802.3、802.4、802.5、802.6、802.11 并列位于 802.2 LLC 之下，作为同一 LLC 之上的不同 MAC/PHY 方案。这与 4.2.2 节「对同一个 LLC，可以提供多种 MAC 选择」一致。

课件说明 802.1D 的用途如下。局域网中的设备常用冗余链路（redundant links）互连，以提高可靠性（resilience）；冗余链路会产生环路（loops），环路会消耗网络资源并使网络失效。802.1D 实现生成树协议（Spanning Tree Protocol，STP），为 LAN 构造无环的逻辑拓扑，从而阻塞任意两个网络设备之间的冗余链路。

---

## 4.4 LAN 地址与 MAC 地址（课件 4-7 ～ 4-10）

### 4.4.1 两类地址的分工（4-7）

网络层地址与 LAN 地址的分工如下。

**32 位 IP 地址（32-bit IP address）**：

- 属于网络层地址（network-layer address）；
- 用途是把数据报送到目的网络（used to get datagram to destination network）。

**LAN 地址（LAN address，又称 MAC 地址或物理地址，MAC or physical address）**：

- 是网络适配器（network adapter）的唯一标识；
- 用途是把数据报从一个接口送到与之物理连接的另一接口，即同一网络内部的交付（used to get datagram from one interface to another physically-connected interface, same network）；
- 在多数局域网中为 **48 位** MAC 地址，固化（burned in）在适配器的只读存储器 ROM（Read-Only Memory）中。

分工的划分依据是作用范围：IP 地址标识「目的网络」，用于跨网络寻址；MAC 地址标识「目的接口」，只在同一物理网络内部有效。一旦数据报到达目的网络，就改用 MAC 地址完成最后一跳的交付。

### 4.4.2 MAC 地址的分配方式与可移植性（4-8）

MAC 地址空间的管理方式：

- MAC 地址的分配由 IEEE 管理（MAC address allocation administered by IEEE）；
- 制造商向 IEEE 购买 MAC 地址空间的一部分（manufacturer buys portion of MAC address space），以保证唯一性（to assure uniqueness）。

课件给出的两组对应关系是：MAC 地址对应社会保障号（like Social Security Number），IP 地址对应邮政地址（like postal address）。这两条对应关系表达的是地址结构性质的区别：MAC 地址是全局唯一且不随位置改变的编号，IP 地址是随所在网络而改变的编号。

由此引出的两个性质是：

- **MAC 是平面地址（flat address），因而具有可移植性（portability）**：可以把网卡从一条 LAN 移到另一条 LAN，地址仍有效。
- **IP 是层次化地址（hierarchical address），不可移植（NOT portable）**：IP 地址取决于主机所接入的网络，接入点改变则地址必须改变。

### 4.4.3 适配器上的 MAC 地址与 EUI-48 地址格式（4-9）

每条 LAN 上的每个适配器都有唯一的 LAN 地址（Each adapter on LAN has unique LAN address）。课件左侧画出 LAN 与四个节点，节点上的 adapter（适配器）标注地址如下：

| 节点位置（课件原图） | 地址 |
|----------------------|------|
| 上方节点 | 1A-23-F9-CD-06-9B |
| 左侧节点 | 5C-66-AB-90-75-B1 |
| 右侧节点 | 88-B2-2F-54-1A-0F |
| 下方节点 | 49-BD-D2-C7-56-2A |

页面右侧是一块型号为 TP-LINK TG-3269C 的网卡，并标出四个部件的功能：

| 部件 | 功能 |
|------|------|
| EEPROM 芯片，例如 93C46 | 存储 MAC 地址和网卡信息 |
| BootROM 插槽 | 网络无盘工作站的启动 |
| REALTEK（瑞昱）8169SC 芯片 | 实现以太网的数据链路层和物理层 |
| 网络隔离变压器 | 使核心芯片与外部隔离，提高抗干扰能力，对核心芯片进行保护（防雷击） |

页面下半部给出「IEEE 802 局域网的 MAC 地址格式」，即扩展的唯一标识符 EUI-48（EUI-48 = Extended Unique Identifier，48 位）。48 位被分为两段：

| 字段 | 占用的字节 | 分配方 |
|------|------------|--------|
| 组织唯一标识符 OUI（Organizationally Unique Identifier） | 第一字节、第二字节、第三字节 | 由 IEEE 的注册管理机构分配 |
| 网络接口标识符 | 第四字节、第五字节、第六字节 | 由获得 OUI 的厂商自行分配 |

图中对每个字节按比特自左至右标注 b7 b6 b5 b4 b3 b2 b1 b0，并对每个比特位给出占位标记。课件同时列出三种书写表示法及示例：

| 表示法 | 示例 |
|--------|------|
| XX-XX-XX-XX-XX-XX（图中关联 Windows） | 00-0C-CF-93-8C-92 |
| XX:XX:XX:XX:XX:XX（图中关联 Apple/Android/Linux） | 00:0C:CF:93:8C:92 |
| XXXX.XXXX.XXXX（图中关联 Cisco） | 000C.CF93.8C92 |

三种写法指向同一个 48 位地址：00-0C-CF-93-8C-92 中前 3 字节 00-0C-CF 为 OUI，后 3 字节 93-8C-92 为厂商自行分配的网络接口标识符。

### 4.4.4 地址类型位与总地址数量（4-10）

在第一字节中，有两个特殊比特的含义由箭头从 OUI 的第一字节引出：

- 第一字节的 **b1 位**：0 表示全局管理（全局管理地址），1 表示本地管理（本地管理地址）；
- 第一字节的 **b0 位**：0 表示单播（unicast），1 表示多播（multicast，组播）。

据此，全部 MAC 地址分为四类：

| 第一字节 b1 | 第一字节 b0 | MAC 地址类型 | 地址数量占比 | 总地址数量 |
|-------------|-------------|--------------|--------------|------------|
| 0 | 0 | 全局管理 单播地址：厂商生产网络设备（网卡、交换机、路由器）时固化 | 1/4 | $2^{48}=281{,}474{,}976{,}710{,}656$（二百八十多万亿） |
| 0 | 1 | 全局管理 多播地址：标准网络设备所支持的多播地址，用于特定功能 | 1/4 | （同上，占总量 1/4） |
| 1 | 0 | 本地管理 单播地址：由网络管理员分配，覆盖网络接口的全局管理单播地址 | 1/4 | （同上，占总量 1/4） |
| 1 | 1 | 本地管理 多播地址：用户对主机进行软件配置，以表明其属于哪组多播。注意：剩余 46 位全为 1 时，就是广播地址 FF-FF-FF-FF-FF-FF | 1/4 | （同上，占总量 1/4） |

> **补充说明（整理者补充）**：上表「各占 1/4」是按两个比特的四种取值平均划分得到的说法。实际分配中，全局管理单播地址才是厂商固化到网卡上的地址，其数量远超过全部可用地址的 1/4；课件此处的「1/4」是指四类地址在编码空间上的等分，不代表实际已分配的地址数量比例。广播地址 FF-FF-FF-FF-FF-FF 属于本地管理多播地址中的特例：b1=1、b0=1，其余 46 位全为 1。

课件给出的两个查询 MAC 地址的网址是 `https://standards-oui.ieee.org/oui/oui.txt`（IEEE 的 OUI 注册文本）和 `https://mac.bmcx.com/`（MAC 地址查询）。查询的依据就是前三字节的 OUI 与 IEEE 注册表的对应关系。

课件还提出并回答了「什么是随机 MAC 地址技术」（What is the random MAC address technology?）：这是一项隐私特性（privacy feature），为每条 LAN 使用一个不同的、临时的 MAC 地址（a different, temporary MAC address），以防止设备在不同网络之间被跟踪。用随机地址替换设备固有的硬件地址后，观测者难以通过 MAC 地址监视用户的移动与行为，尤其在多个公共 Wi-Fi 热点之间切换时。该特性是 iOS、Android、macOS 等现代操作系统的默认功能。

随机 MAC 地址与地址类型表的联系是：随机生成的地址属于本地管理地址（第一字节 b1 = 1），因为它不来自 IEEE 分配的 OUI，只在本机所在链路中临时有效；而厂商固化的地址属于全局管理地址（第一字节 b1 = 0）。

---

## 4.5 以太网（课件 4-11 ～ 4-18）

### 4.5.1 以太网的地位与速率演进（4-11）

以太网被称为「占主导地位的」（dominant）LAN 技术，也是**第一种被广泛使用的局域网技术**（first widely used LAN technology）。课件列出的速率节点为：

- （早期版本的）快速以太网（Fast Ethernet）100 Mbps；
- 现代标准：千兆以太网（Gigabit Ethernet）1 Gbps、万兆以太网（10 Gigabit Ethernet）10 Gbps，以及更高速率 25 Gbps、40 Gbps、50 Gbps、100 Gbps。

课件配 Metcalfe 的以太网草图（Metcalfe's Ethernet sketch，课件原图）。图中元素自左至右、自上而下为：一条水平线标为 **THE ETHER**（作为共享传输介质），线的右端标为 **TERMINATOR**（终端匹配器）；线上有多个站点，每个站点通过 **TAP**（分接头）接入，分接头上接 **TRANSCEIVER**（收发器），收发器经 **INTERFACE CABLE**（接口电缆）连到 **INTERFACE CONTROLLER**（接口控制器），接口控制器属于 **STATION**（站点）。这幅草图表达的是总线型以太网的接入方式：所有站点通过分接头与收发器挂接在同一条共享介质上，介质两端用终端匹配器端接。

### 4.5.2 以太网的物理拓扑（4-12）

以太网的物理拓扑（physical topology）分为先后两个阶段。

**总线（bus）**：流行至 20 世纪 90 年代中期。所有节点处于同一个冲突域（collision domain）内，节点之间可能相互冲突。课件配图标注为「bus: coaxial cable」，即总线使用同轴电缆。

**星形（star）**：今天普遍采用（现代以太网）。中心有一台有源交换机（active switch in center）；每一条「辐条」（spoke）各自运行一套（独立的）以太网协议，节点之间不会相互冲突。课件配图画出中心一台交换机，四条链路连接四台主机。

拓扑改变带来的是冲突域结构的变化：总线结构下全部站点共享一个冲突域，任一时刻只允许一个站点发送；星形结构下每条交换机—主机链路是一个独立的冲突域，这些链路可以独立工作。

### 4.5.3 以太网是无连接、不可靠的（4-13）

以太网有两个服务性质：

- **无连接（connectionless）**：发送网卡与接收网卡之间没有握手（no handshaking between sending and receiving network interface cards, NICs）。发送方直接把帧发到介质上，不先建立连接。
- **不可靠（unreliable）**：接收 NIC 不向发送 NIC 发送确认（acks）或否定确认（negative acks, nacks）。因此被丢弃帧中的数据只有在初始发送方使用更高层的恢复技术（higher layer recovery data techniques，例如 TCP）时才能恢复，否则丢弃的数据就丢失。

以太网的 MAC 协议是**非时隙 CSMA/CD 加二进制退避**（unslotted CSMA/CD with binary backoff）。

> **范围说明**：课件此处只写出「非时隙 CSMA/CD 加二进制退避」这一名称，未展开 CSMA/CD 的具体流程与二进制退避的窗口规则；下一节的例题也只用到 CSMA/CD 的冲突检测时间约束，未给出协议流程细节。因此本笔记不补写课件未给出的协议状态与退避算法步骤。

### 4.5.4 802.3 以太网标准：链路层与物理层（4-14）

802.3 之下存在许多不同的以太网标准，它们的共同点是 **MAC 协议与帧格式相同**（common MAC protocol and frame format），不同点有两类：

- 速率不同：10 Mbps、100 Mbps、1 Gbps、10 Gbps、25 Gbps、40 Gbps、50 Gbps、100 Gbps；
- 物理层介质不同：光纤（fiber）、电缆（cable）。

配图以五层协议栈（application、transport、network、link、physical）为基础，把 link 与 physical 两层展开：上层是「MAC protocol and frame format」一个方框，其下并列六个快速以太网物理层标准，分为两行（课件原图排布）：

| 位置（课件原图） | 标准 | 图中圈注 |
|------------------|------|----------|
| 上行左 | 100BASE-TX | 标注 copper (twister pair) physical layer |
| 上行中 | 100BASE-T2 | 未加圈注 |
| 上行右 | 100BASE-FX | 标注 fiber physical layer |
| 下行左 | 100BASE-T4 | 标注 copper (twister pair) physical layer |
| 下行中 | 100BASE-SX | 标注 fiber physical layer |
| 下行右 | 100BASE-BX | 标注 fiber physical layer |

该图表达的结构是：同一套 MAC 协议与帧格式之下，可以挂接多种物理层实现，各实现之间只在速率与所使用介质上不同。

> **核对记录**：课件原图对 100BASE-T2 未加圈注，而 100BASE-T2 按标准同样是双绞线（铜缆）物理层；此处按原图如实记录「未加圈注」，不替原图补加标注。图中「twister pair」为课件原拼写，规范写法为 twisted pair（双绞线）。

### 4.5.5 以太网帧结构（4-15 ～ 4-18）

#### 4.5.5.1 帧的总体分层与字段长度（4-15）

课件画出 IP 层、MAC 层、物理层三个层次的封装关系：IP 层的数据单元标为 **IP datagram**（IP 数据报）；它向下交付给 MAC 层，被封装成 **Ethernet MAC frame**（以太网 MAC 帧）；MAC 帧再向下交给物理层，物理层在帧前插入 **8 byte** 的前导部分。

MAC 层各字段以字节为单位的长度为：

| 字段 | 长度 | 说明 |
|------|------|------|
| Destination address（目的地址） | 6 byte | 目的 MAC 地址 |
| Source address（源地址） | 6 byte | 源 MAC 地址 |
| type（类型） | 2 byte | 上层协议类型 |
| data（数据） | 46 ～ 1500 byte | 承载 IP 数据报，课件原图标注 IP datagram 装入此处 |
| FCS | 4 byte | 帧检验序列 |

物理层插入的 8 byte 由两部分构成：前 7 byte 是**前导字段**（Preamble field），后 1 byte 是**帧首定界符**（Start of Frame Delimiter，SFD）。课件原图顶部给出的比特串为前导部分「10101010101010 …… 101010101010」，随后接定界符部分「101010101010101011」。

课件给出 FCS 的定义：FCS（Frame Check Sequence，帧检验序列）是一个 **32 位差错检测码**（32-bit error-detecting code），使用循环冗余校验（Cyclic Redundancy Check，CRC）算法计算得到。

#### 4.5.5.2 封装与前导字段（4-16）

**发送适配器把 IP 数据报（或其他网络层协议分组）封装进以太网帧**（Sending adapter encapsulates IP datagram or other network layer protocol packet in Ethernet frame）。图中给出的帧为前导（Preamble）、目的地址（Dest. Address）、源地址（Source Address）、类型（Type）、数据（Data）、CRC 依次排列，类型字段位于源地址之后、数据之前。

**前导字段（Preamble）**：

- 由 7 字节的 10101010 模式，后接 1 字节的 10101011 模式组成；
- 作用是使接收方与发送方的时钟速率同步（synchronize receiver, sender clock rates）。

前导字段的比特模式是交替的 1 与 0，接收方据此锁定发送方的位定时；末字节 10101011 的结尾连续两个 1 是一个不会出现在前导交替模式中的标志，接收方检测到它即判定帧正式开始，因此这一字节称为帧首定界符（SFD）。

> **核对记录**：课件文字对末字节写作 pattern 10101011；同一页图与 4-15 页顶部的示意比特串该处写为 101010101011，属于原图的示意串写法。本笔记的字段长度与功能说明采用 10101011，并如实照录 4-15 页的示意比特串。

#### 4.5.5.3 地址、类型与 CRC 字段（4-17）

- **地址（Addresses）**：6 字节。帧被 LAN 上的所有适配器接收，若地址不匹配则被丢弃（frame is received by all adapters on a LAN and dropped if address does not match）。这一性质说明以太网网卡在介质上按共享方式接收全部帧，靠地址筛选帧。
- **类型（Type）**：2 字节，指示上层协议（indicates the higher layer protocol），大多为 IP，但也可能支持其他协议，例如 Novell IPX 和 AppleTalk。
- **CRC**：4 字节，在接收方校验（checked at receiver），若检测到差错，帧被直接丢弃（the frame is simply dropped）。这与以太网「不可靠」的说明一致：接收方不返回确认，出错帧只做丢弃处理。

#### 4.5.5.4 数据字段与帧长限制（4-18）

- **数据（Data）字段长度**：46 ～ 1500 字节；
- **最短帧长（Minimum frame length）**：64 字节；
- **最长帧长（Maximum frame length）**：1518 字节。

**最短帧长 64 字节的由来**。课件给出的条件是：对 IEEE 802.3，争用期（contention period）$2\tau$ 为 $51.2\ \mu s$，速率 $R = 10\ \text{Mbps}$。CSMA/CD 要求发送方在发送过程中持续检测冲突，只有在「整个往返传播时延 $2\tau$ 内发送方仍处于发送状态」时才能检测到最远端站点造成的冲突，因此帧的发送时间必须不小于往返传播时延：

$$\frac{L_{\min}}{R} \ge 2\tau$$

代入课件给出的数据：

$$L_{\min} = R \cdot 2\tau = 10 \times 10^{6}\ \text{bit/s} \times 51.2 \times 10^{-6}\ \text{s} = 512\ \text{bit}$$

$$512\ \text{bit} \div 8 = 64\ \text{byte}$$

即最短帧长为 64 字节。反过来，MAC 帧中地址（6+6 字节）、类型（2 字节）、FCS（4 字节）共占 $6+6+2+4 = 18$ 字节，因此数据字段的最小长度为：

$$64 - 18 = 46\ \text{byte}$$

这正是数据字段下界取 46 字节的原因。若数据不足 46 字节，MAC 层必须填充（pad）到 46 字节；否则帧的发送时间小于 $2\tau$，发送方可能在帧发送结束后才检测到冲突，无法执行冲突后的重发，CSMA/CD 的冲突检测不再成立。

**最长帧长 1518 字节的由来**。课件给出的理由是：它确保一个站点不会过长地占用共享介质从而阻塞其他站点（one station didn't block others on the shared medium for too long），同时也使网卡只需维持少量在当时价格昂贵的缓冲存储器（allowed NICs to maintain a small amount of then-expensive buffer memory）。最长帧长与数据字段上界的关系可同样核验：

$$6 + 6 + 2 + 1500 + 4 = 1518\ \text{byte}$$

即 1518 字节对应数据字段取上界 1500 字节。

> **说明**：64 字节与 1518 字节均指 MAC 帧本身，不含物理层插入的 8 字节前导与 SFD；若计入前导与 SFD，物理层在介质上实际传送的长度分别为 72 字节与 1526 字节。

---

#### 例题：最短数据帧长度与最远站距（课件 4-19，Exercise-1）

**题干（Exercise-1）**：

In a LAN using CSMA/CD protocol, the transmission medium is a complete cable, the transmission rate is 1 Gbps, and the signal propagation rate in the cable is 200,000 km/s. If the minimum data frame length is reduced by 800 bits, the distance between the farthest two stations needs to be at least

(1) increased by 160 m　(2) increased by 80 m
(3) reduced by 160 m　　(4) reduced by 80 m

即：在使用 CSMA/CD 协议的局域网中，传输介质是一根完整电缆，传输速率 1 Gbps，电缆中信号传播速率 200,000 km/s。若最短数据帧长度减少 800 bit，则相距最远的两个站点之间的距离至少应

(1) 增加 160 m　(2) 增加 80 m
(3) 减少 160 m　　(4) 减少 80 m

**解**：

第 1 步：明确待求量与约束关系。CSMA/CD 要求帧的发送时间不小于往返传播时延，即

$$\frac{L_{\min}}{R} = 2\tau = \frac{2D}{v}$$

其中 $L_{\min}$ 为最短数据帧长度（单位 bit），$R$ 为传输速率（单位 bit/s），$\tau$ 为单程传播时延（单位 s），$D$ 为相距最远的两个站点之间的距离（单位 m），$v$ 为信号在电缆中的传播速率（单位 m/s）。

第 2 步：列出已知量并统一单位。

- $R = 1\ \text{Gbps} = 1 \times 10^{9}\ \text{bit/s}$
- $v = 200{,}000\ \text{km/s} = 2 \times 10^{5}\ \text{km/s} = 2 \times 10^{8}\ \text{m/s}$
- 最短数据帧长度的变化量 $\Delta L = -800\ \text{bit}$

第 3 步：求帧长度变化引起的发送时间变化量。由 $t_{\text{trans}} = L/R$，

$$\Delta t_{\text{trans}} = \frac{\Delta L}{R} = \frac{-800\ \text{bit}}{1 \times 10^{9}\ \text{bit/s}} = -8 \times 10^{-7}\ \text{s} = -0.8\ \mu s$$

第 4 步：把发送时间的变化换算为往返传播时延的变化。由约束 $\dfrac{L_{\min}}{R} = 2\tau$，等式两侧必须同步变化，故

$$2\Delta\tau = \Delta t_{\text{trans}} = -0.8\ \mu s$$

第 5 步：求单程传播时延的变化量。

$$\Delta\tau = \frac{-0.8\ \mu s}{2} = -0.4\ \mu s = -0.4 \times 10^{-6}\ \text{s}$$

第 6 步：由传播时延变化求距离变化量。由 $D = v\tau$，

$$\Delta D = v \cdot \Delta\tau = 2 \times 10^{8}\ \text{m/s} \times \left(-0.4 \times 10^{-6}\ \text{s}\right) = -80\ \text{m}$$

即相距最远的两个站点之间的距离至少应**减少 80 m**。

第 7 步：用原数据直接核验。由 $L_{\min}/R = 2D/v$ 解出 $D = \dfrac{L_{\min} v}{2R}$，两边取变化量：

$$\Delta D = \frac{\Delta L \cdot v}{2R} = \frac{(-800\ \text{bit}) \times (2 \times 10^{8}\ \text{m/s})}{2 \times (1 \times 10^{9}\ \text{bit/s})} = \frac{-1.6 \times 10^{11}}{2 \times 10^{9}} = -80\ \text{m}$$

与第 6 步结果一致。该核验只用原题给出的 $R$、$v$ 与 $\Delta L$，不需要知道最短帧长的绝对值与电缆的绝对长度。

**答案**：选 (4)，减少 80 m。

**易错点**：$\tau$ 是单程传播时延，$2\tau$ 是往返传播时延。若把发送时间的减少量 $-0.8\ \mu s$ 直接当作单程时延变化，会得到距离变化 $-160\ \text{m}$（即误选 (3)）；$-0.8\ \mu s$ 对应的往返传播距离变化才是 $2 \times 10^{8} \times 0.8 \times 10^{-6} = 160\ \text{m}$，而站点间距离对应的是往返距离的一半。

---

## 4.6 互联局域网（课件 4-20）

课件以问题形式引出后续内容：「为什么不干脆用一个大 LAN？」（Why not just one big LAN?），并给出三条原因：

- **可承载的流量有限**（Limited amount of supportable traffic）：在单个 LAN 上，所有站点必须共享带宽（all stations must share bandwidth）；
- **冲突域过大**（large "collision domain"）：可能与很多站点发生冲突；
- **长度受限**（limited length）：802.3 规定了最大电缆长度（802.3 specifies maximum cable length）。

这三条原因共同说明：需要把多个较小的 LAN 互联起来，而不是把所有站点接到一个大的共享介质上。互联所用的设备依次为集线器（hubs）、交换机（switches）与路由器。

---

## 4.7 集线器（课件 4-21 ～ 4-23）

### 4.7.1 集线器的定义与比特级中继行为（4-21）

集线器是**物理层设备（Physical Layer device）**，其本质是工作在**比特级（bit level）**的中继器（repeater）：它把从一个接口（interface）接收到的比特重复（repeat）到所有其他接口上。也就是说，集线器不做任何帧格式解析、不做地址判断、不做任何转发决策，输入端口的比特流被直接复制输出到其余全部端口。

集线器可以组成**层次结构（hierarchy）**，也称**多级设计（multi-tier design）**，其顶层放置一个**主干集线器（backbone hub）**。

课件原图可还原为如下层次结构（节点数量按图逐一点数）：

| 层级 | 设备/站点 | 连接介质标注 |
|------|-----------|--------------|
| 顶层 | 主干集线器（backbone hub） | — |
| 第 2 层（左） | 集线器，下挂 4 个站点 | 10BaseT |
| 第 2 层（中） | 集线器，下挂 4 个站点 | 10BaseT |
| 第 2 层（右） | 集线器，下挂 4 个站点 | 10BaseT |

第 2 层三个集线器分别服务的站点组在原图中的标注为：Electrical Engineering、Computer Science、Systems Engineering。即：主干集线器向下连到三个二级集线器，每个二级集线器再连接 4 个终端站点，主干集线器与二级集线器之间的链路标注为 10BaseT。

### 4.7.2 冲突域行为与集线器优点（4-22）

- **LAN 段（LAN segment）**：每一个被集线器连接的 LAN 称为一个 LAN 段。
- **集线器不隔离冲突域（Hubs do not isolate collision domains）**：一个节点可能与 LAN 中位于任意 LAN 段（any segment）上的任意节点发生碰撞。原因是集线器只在比特级复制，任何一个端口上出现的信号都会被复制到全部其他端口，因此整个多级集线器系统仍然构成**同一个冲突域**。

集线器的优点（Hub Advantages）：

1. **简单、便宜（simple, inexpensive device）**：不解析帧、不维护转发表，硬件成本低。
2. **多级结构提供降级运行能力（graceful degradation）**：如果某一个集线器发生故障（malfunctions），LAN 中其余部分仍能继续运行。这是因为故障被限制在连接到该集线器的那些网段，其他集线器分支的比特复制路径不受影响。
3. **扩展节点对之间的最大距离**：每个集线器可扩展 100 m（100 m per Hub）。

### 4.7.3 集线器的局限（4-23）

1. **单一冲突域导致最大吞吐量不增加**：多级集线器系统的吞吐量与单个 LAN 段的吞吐量相同（multi-tier throughput same as single segment throughput）。因为全部节点仍处于同一个冲突域，任一瞬间只能有一个站点成功发送，集线器不提供任何并行传输能力。
2. **单个 LAN 的限制直接约束节点数与覆盖范围**：LAN 自身的限制（如 802.3 对最大电缆长度、最小帧长与往返传播时延的规定）给同一冲突域内的节点数量以及允许的总地理覆盖范围（total allowed geographical coverage）都设了上限。
3. **不能连接不同类型的以太网**：例如 10BaseT 与 100BaseT 不能通过集线器互连。

> **笔误标注与纠正（整理者补充）**：课件在举 10BaseT 与 100BaseT 为例处，括注写为「Twisted-pair cables for distances up to 100 m providing different speed (i.e., 10 Gbps and 100 Gbps, resp.)」。此处所举的两个标准名称 10BaseT、100BaseT 中的「10/100」指 10 Mbps 与 100 Mbps，两者均使用双绞线、单段距离上限 100 m；括注写的「10 Gbps and 100 Gbps」与所举标准名不符，也不符合 100 m 距离限制。据此判定该括注中的速率数值为课件笔误，正确值应为 10 Mbps 与 100 Mbps，课件原文照录于上，此处按标准名称给出的正确速率予以纠正。

---

## 4.8 以太网交换机（课件 4-24 ～ 4-33）

### 4.8.1 多路同时传输（4-24，4-26 为同一内容重复页，合并于此）

交换机与集线器的根本差别在于：**每条链路构成独立的冲突域**，因此可以多对主机同时传输而互不碰撞。

- 主机与交换机之间是**专用的、直接的连接（dedicated, direct connection）**；
- 交换机会**缓存数据包（switches buffer packets）**；
- 每条入链路（incoming link）上仍然使用以太网协议，但**不会发生碰撞**，工作在**全双工（full duplex）**方式；
- 每条链路是它自己的冲突域（each link is its own collision domain）；
- **交换（switching）**的含义：A 到 A′ 与 B 到 B′ 可以同时传输，且不发生碰撞。

课件原图为一个六接口交换机连接六台主机：

| 主机 | 接入接口号 |
|------|------------|
| A | 1 |
| B | 2 |
| C | 3 |
| A′ | 4 |
| B′ | 5 |
| C′ | 6 |

图注原文：switch with six interfaces (1,2,3,4,5,6)。

### 4.8.2 交换机的性质：主动、透明、即插即用（4-25）

以太网交换机是**链路层设备（link-layer device）**，取**主动角色（takes an active role）**：

- **存储并转发以太网帧（store, forward Ethernet frames）**：交换机先把整个帧接收并缓存，再决定是否转发；
- **检查入帧的 MAC 地址**，并把帧**有选择地（selectively）**转发到一个或多个出链路；当帧需要在某个网段上转发时，交换机使用 **CSMA/CD** 来接入该网段。

交换机具有**透明性（transparent）**：主机并不知道交换机的存在。

交换机是**即插即用（plug-and-play）、自学习（self-learning）**的：**不需要配置（switches do not need to be configured）**。

### 4.8.3 交换机转发表（4-27）

课件提出的问题是：交换机如何知道 A′ 可经接口 4 到达、B′ 可经接口 5 到达？

回答是：每台交换机都有一张**交换表（switch table）**，每个表项的组成是三元组：

| 字段 | 含义 |
|------|------|
| MAC address of host | 主机的 MAC 地址 |
| interface to reach host | 到达该主机所用的接口 |
| time stamp | 时间戳（用于表项的老化与管理） |

该表在结构上「看起来像路由表（looks like a routing table!）」。由此引出的第二个问题是：表项如何被创建、如何被维护？是否类似某种路由协议（something like a routing protocol?）——其答案是下一小节的**自学习**：交换机并不运行动态路由协议，而是从收到的帧中直接学习。

### 4.8.4 自学习（4-28）

交换机**学习哪些主机可以经由哪些接口到达（switch learns which hosts can be reached through which interfaces）**：

- 每当收到一个帧，交换机就「学习」到**发送方所在的位置**，即该帧到达的入 LAN 段（incoming LAN segment）；
- 交换机把**发送方/位置对（sender/location pair）**记录到交换表中。

课件原图：主机 A 向 A′ 发送帧，帧的目的地址字段为 A′、源地址字段为 A。交换机的交换表**初始为空（initially empty）**，收到该帧后写入一个表项：

| MAC addr | interface | TTL |
|----------|-----------|-----|
| A | 1 | 60 |

即：源主机 A 位于接口 1 所连的网段，TTL 记为 60。

### 4.8.5 帧过滤与转发算法（4-29）

当交换机收到一个帧时，执行如下流程（课件原文伪代码）：

```
1. record incoming link, MAC address of sending host
2. index switch table using MAC destination address
3. if entry found for destination
   then {
        if destination on segment from which frame arrived
        then drop frame
        else forward frame on interface indicated by entry
   }
   else flood   /* forward on all interfaces except arriving
                   interface */
```

逐条说明：

1. **记录入链路与发送主机的 MAC 地址**：这是自学习动作，把「源 MAC 地址—入接口」对写入交换表。
2. **用目的 MAC 地址检索交换表**：即用帧的目的 MAC 地址作为索引去查表。
3. **若查到目的站点的表项**：
   - 如果目的站点就在该帧到达的那个网段上（destination on segment from which frame arrived），则**丢弃该帧（drop frame）**——因为目的站点已经收到该帧，无需再转发；
   - 否则按表项指示的接口**转发该帧（forward frame on interface indicated by entry）**，即选择性转发到唯一的一条链路。
4. **若未查到表项**：则**泛洪（flood）**，即向**除到达接口以外的所有接口**转发。

#### 例 4-1（课件 4-30）：单交换机自学习与转发全过程

**题干**：交换机有 6 个接口（1,2,3,4,5,6），主机 A（接口 1）向主机 A′（接口 4）发送一个帧，帧的头为 `Source: A`、`Dest: A'`。交换机交换表初始为空。要求：说明该帧的转发过程，以及 A′ 回送应答帧时的转发过程，并给出交换表的变化。

**解**：

第 1 步：自学习。交换机从接口 1 收到 A 发来的帧，记录「源 MAC 地址 A — 入接口 1」，写入交换表：

| MAC addr | interface | TTL |
|----------|-----------|-----|
| A | 1 | 60 |

第 2 步：查表转发。交换机用目的 MAC 地址 A′ 检索交换表，表中没有 A′ 的表项（A′ 的位置未知，location unknown）。

第 3 步：执行泛洪。交换机把该帧从除到达接口 1 以外的所有接口发出，即从接口 2、3、4、5、6 发出。A′ 位于接口 4，因而收到该帧。课件对此步骤的原文标注为：frame destination A′, location unknown: flood。

第 4 步：A′ 回送帧给 A。A′ 发出的帧以 A 为目的地址。交换机从接口 4 收到该帧，先自学习，写入 A′ 的表项；再用目的 MAC 地址 A 检索交换表，查到表项 A/1（destination A location known）。

第 5 步：选择性转发。交换机只从接口 1 发出该帧，即「只在一条链路上选择性发送（selectively send on just one link）」。

此时的交换表为：

| MAC addr | interface | TTL |
|----------|-----------|-----|
| A | 1 | 60 |
| A′ | 4 | 60 |

**答案**：A 发给 A′ 的帧因目的位置未知被泛洪到接口 2、3、4、5、6；A′ 发给 A 的帧因目的地址 A 已在表中而被选择性转发到接口 1。

**用原数据校验**：A 接在接口 1、A′ 接在接口 4，与表中两条表项的接口号一致；泛洪时排除了到达接口 1，因此 A 不会收到自己发出的帧；A′ 的应答帧只经接口 1 转发，正好到达 A 所连的链路。校验通过。

### 4.8.6 交换机的互连（4-31）

**自学习交换机可以相互连接（self-learning switches can be connected together）**，从而构成更大规模的局域网。

课件原图拓扑（逐节点还原）：

| 交换机 | 直接相连的终端站点 | 与其他交换机的连接 |
|--------|--------------------|--------------------|
| S1 | A、B、C | 上行连 S4 |
| S2 | D、E、F | 上行连 S4 |
| S3 | G、H、I | 上行连 S4 |
| S4 | 无终端站点 | 下连 S1、S2、S3（位于根/主干位置） |

课件提出的问题是：从 A 发送到 G 时，S1 如何知道应该把目的为 G 的帧经由 S4 和 S3 转发出去？

回答是：**自学习（self learning）**，其行为与单交换机情形完全相同（works exactly the same as in single-switch case）。即 S1 只要曾经收到过来自 G 的帧（其入接口是通往 S4 的那个接口），就会在表中建立「G — S1 上行口到 S4」的表项，此后发往 G 的帧只从该接口转发。

#### 例 4-2（课件 4-32）：多交换机自学习全过程

**题干**：拓扑为 S4 位于根部并连接 S1、S2、S3；S1 下挂 A、B、C；S2 下挂 D、E、F；S3 下挂 G、H、I。假设 **C 向 I 发送一个帧，随后 I 向 C 回送一个帧**。各交换机初始交换表为空。要求：给出 S1、S2、S3、S4 的交换表以及数据包转发过程。

> **端口命名说明（整理者补充）**：课件原图中交换机各端口没有编号标注，为叙述需要，按相邻设备对端口命名，全部名称为本笔记自定义，不代表课件原标号。约定：S1 上连 S4 的端口记为 `S1→S4`，S1 连接终端 C 的端口记为 `S1→C`，依此类推；S4 连接 S1 的端口记为 `S4→S1`。

**解**：

第 1 部分：C 发出的帧（源 C，目的 I，I 的位置对沿途各交换机均为未知）

第 1 步：S1 从 `S1→C` 收到该帧。先自学习，写入表项 **C — `S1→C`**（按 4-28 页的 TTL 值记为 60，下同）。用目的地址 I 查表，无表项，执行泛洪：从 `S1→A`、`S1→B`、`S1→S4` 三个端口发出（不包含到达端口 `S1→C`）。

第 2 步：S4 从 `S4→S1` 收到该帧。自学习，写入表项 **C — `S4→S1`**。查表无 I，泛洪：从 `S4→S2`、`S4→S3` 发出。

第 3 步：S2 从 `S2→S4` 收到该帧。自学习，写入表项 **C — `S2→S4`**。查表无 I，泛洪：从 `S2→D`、`S2→E`、`S2→F` 发出。

第 4 步：S3 从 `S3→S4` 收到该帧。自学习，写入表项 **C — `S3→S4`**。查表无 I，泛洪：从 `S3→G`、`S3→H`、`S3→I` 发出。I 从 `S3→I` 所在链路收到该帧。

第 2 部分：I 回送的帧（源 I，目的 C，C 的位置已被沿途各交换机学到）

第 5 步：S3 从 `S3→I` 收到该帧。自学习，写入表项 **I — `S3→I`**。用目的地址 C 查表，已有表项 C — `S3→S4`，因此**不泛洪**，只从 `S3→S4` 转发。

第 6 步：S4 从 `S4→S3` 收到该帧。自学习，写入表项 **I — `S4→S3`**。查表得 C — `S4→S1`，只从 `S4→S1` 转发。

第 7 步：S1 从 `S1→S4` 收到该帧。自学习，写入表项 **I — `S1→S4`**。查表得 C — `S1→C`，只从 `S1→C` 转发。C 收到该帧。

第 8 步：I 的回送帧在 S4 处因目的地址 C 已命中表项而被定向到 `S4→S1`，不会再走 `S4→S2`，因此 **S2 全程没有收到 I 的回送帧，其交换表中没有 I 的表项**（S2 只在第 1 部分收到过 C 发出的帧，故只学到 C）。

最终四台交换机的交换表：

S1：

| MAC addr | interface | TTL |
|----------|-----------|-----|
| C | `S1→C` | 60 |
| I | `S1→S4` | 60 |

S4：

| MAC addr | interface | TTL |
|----------|-----------|-----|
| C | `S4→S1` | 60 |
| I | `S4→S3` | 60 |

S3：

| MAC addr | interface | TTL |
|----------|-----------|-----|
| C | `S3→S4` | 60 |
| I | `S3→I` | 60 |

S2：

| MAC addr | interface | TTL |
|----------|-----------|-----|
| C | `S2→S4` | 60 |

**答案**：C→I 的帧在 S1、S4、S2、S3 上因目的地址未知而逐级泛洪，最终到达 I；I→C 的回送帧在 S3、S4、S1 上均命中已学到的目的表项，逐级定向转发，最终只从 `S1→C` 一条链路送达 C。四台交换机最终都学到了 C，但只有 S1、S3、S4 学到了 I。

**用原数据校验**：拓扑中 C 只接在 S1 上，因此 C 只能由 `S1→C` 到达，与 S1 表项一致；I 只接在 S3 上，与 S3 表项一致；S1 与 S3 之间唯一的路径是 S1—S4—S3，因此 S1 表中 I 的出接口必须是其上行口，S4 表中 C 与 I 分别指向两条不同的下联口，S3 表中 C 的出接口必须是其上行口，均与上表一致。S2 只收到过 C 帧的泛洪副本（所以只有 C 表项）、没有收到 I 的回送帧（所以无 I 表项），符合「自学习只依据收到帧的入接口」这一规则。校验通过。

### 4.8.7 机构网络（4-33）

课件给出一个典型的机构网络（institutional network）结构：

- 一台**路由器（router）**对外连接外部网络（to external network），同时对内连接机构的主干交换机，构成机构网络与外界的分界；
- 主干交换机上方连接两台服务器：**邮件服务器（mail server）**和 **Web 服务器（web server）**；
- 主干交换机下方连接多台接入交换机（课件原图为 3 组），每台接入交换机再下挂多台主机；
- 整个用一台路由器对外的部分构成一个 **IP 子网（IP subnet）**，课件原图以闭合区域标出该 IP 子网的范围。

该图说明的实际组网方式是：终端主机通过多级交换机接入，服务器挂在主干交换机上，整个机构网络通过路由器与外部网络相连。这与「自学习交换机可以级联」的结论一致。

---

## 4.9 虚拟局域网（Virtual Local Area Network, VLAN，课件 4-34 ～ 4-38）

### 4.9.1 引入 VLAN 的动机（4-34）

课件以两种情形说明动机。

情形一（人员跨部门办公）：CS（Computer Science，计算机科学）的用户把办公室搬到了 EE（Electrical Engineering，电气工程）的区域，但仍希望连接到 CS 的交换机上。

情形二（单一广播域带来的问题）：在只有二层交换机构成的局域网中，整个网络是**单一广播域（single broadcast domain）**：

- 在未划分 VLAN 的同一二层广播域内，广播及需要泛洪的流量会传播到其他相应端口。课件列举的来源包括 **ARP**、**DHCP**，以及**目的 MAC 地址位置未知**时触发的泛洪（unknown location of destination MAC address）。这些流量在 LAN 的每一条链路上传播，与接收者是否属于同一部门无关；
- 由此带来**安全/隐私问题与效率问题（security/privacy, efficiency issues）**：广播流量会到达不相干的部门主机，同时占用全网的带宽。

课件原图：一台路由器对外连接，一台主干交换机下挂服务器与多台接入交换机，终端主机按部门划分为三个区域，图中标注为 Computer Science、Electrical Engineering、Computer Engineering（其中 Computer Science 出现两处，一处位于图左下，另一处位于图右下）。部门划分与物理布线区域并不一致，这正是 VLAN 要解决的问题。

### 4.9.2 VLAN 的定义与基于端口的 VLAN（4-35）

**虚拟局域网（Virtual Local Area Network, VLAN）**：支持 VLAN 能力的交换机可以被配置为，在**单一物理 LAN 基础设施（single physical LAN infrastructure）**之上定义**多个虚拟 LAN（multiple virtual LANs）**。

**基于端口的 VLAN（port-based VLAN）**：由**交换机管理软件（switch management software）**把交换机的端口分组，使**单台物理交换机……作为多台虚拟交换机运行**（operates as multiple virtual switches）。

课件原图为一个 16 端口交换机的端口分组：

| 分组 | 端口范围 | 图注 |
|------|----------|------|
| 分组 1 | 1–8 | Electrical Engineering（VLAN ports 1-8） |
| 分组 2 | 9–15 | Computer Science（VLAN ports 9-15） |

图下方的第二个示意图把同一台物理交换机画成两台虚拟交换机，其中右侧虚拟交换机的图注标为「Computer Science（VLAN ports 9-16）」。

> **核对记录**：课件 4-35 页上半部分示意图与 4-36 页均标注 CS 的端口为 9-15，而 4-35 页下半部分示意图标注为 9-16；同一页内端口总数 16 与「9-15」「9-16」两种写法并存。此处按课件原图分别照录，不作统一。

### 4.9.3 基于端口的 VLAN 的性质（4-36）

1. **流量隔离（traffic isolation）**：去往/来自端口 1-8 的帧只能到达端口 1-8（frames to/from ports 1-8 can only reach ports 1-8）。同一个 VLAN 内部的帧不会跨越到另一个 VLAN 的端口上，因而广播流量被限制在本 VLAN 范围内。
2. **VLAN 的划分依据可以不是端口**：也可以**基于端点的 MAC 地址（MAC addresses of endpoints）**而不是交换机端口来定义 VLAN。
3. **动态成员关系（dynamic membership）**：端口可以在各 VLAN 之间被**动态分配**。这是上一条的直接结果——成员身份由端点的 MAC 地址决定时，端点移动到另一个物理端口后仍留在原 VLAN 中。
4. **VLAN 之间的转发**：通过**路由（routing）**完成，与使用相互独立的交换机时完全相同（just as with separate switches）。实务中厂商出售**交换机与路由器合一的设备（combined switches plus routers）**。

课件原图：一台 16 端口交换机，其中端口 1-8 属于 Electrical Engineering VLAN、端口 9-15 属于 Computer Science VLAN，一台**路由器（router）**同时连接到两个 VLAN 的端口上，作为 VLAN 之间的三层转发设备。

### 4.9.4 跨多台交换机的 VLAN 与干道端口（4-37）

当同一个 VLAN 的成员分布在多台物理交换机上时，需要**干道端口（trunk port）**：它在多台物理交换机之间承载 VLAN 的帧（carries frames between VLANs defined over multiple physical switches）。

- 在交换机之间转发的、属于某个 VLAN 的帧**不能是普通的 802.1 帧（can't be vanilla 802.1 frames）**，必须携带 **VLAN ID 信息**；
- **802.1q 协议**为在干道端口之间转发的帧**添加/移除额外的头部字段（adds/removed additional header fields）**。

课件原图为两台交换机之间用一段线缆相连作为干道：

| 交换机 | 端口与 VLAN 归属（图注原文） |
|--------|------------------------------|
| 左侧交换机 | Electrical Engineering（VLAN ports 1-8）；Computer Science（VLAN ports 9-15）；端口 1–16 |
| 右侧交换机 | Ports 2,3,5 belong to EE VLAN；Ports 4,6,7,8 belong to CS VLAN |

两台交换机之间由一条被标为干道（trunk）的链路连接，该链路同时承载 EE VLAN 与 CS VLAN 的帧。

### 4.9.5 802.1Q VLAN 帧格式（4-38）

课件把 **802.1 帧**与 **802.1Q 帧**的格式上下对照排列，说明插入字段的位置。以下长度值取自课件原图标注；地址/类型/数据/CRC 的长度沿用本课件 4.5.5 节给出的以太网帧结构参数。

**802.1 帧（课件原图字段顺序）**：

| 顺序 | 字段 | 长度 |
|------|------|------|
| 1 | preamble（前导码） | 原图仅标为 preamble，本页未给出字节数 |
| 2 | dest. address（目的地址） | 6 字节 |
| 3 | source address（源地址） | 6 字节 |
| 4 | type（类型） | 2 字节 |
| 5 | data (payload)（数据/净荷） | 46 ～ 1500 字节 |
| 6 | CRC | 4 字节 |

**802.1Q 帧（课件原图字段顺序）**：

| 顺序 | 字段 | 长度 |
|------|------|------|
| 1 | preamble | 同 802.1 帧 |
| 2 | dest. address | 6 字节 |
| 3 | source address | 6 字节 |
| 4 | **Tag Protocol Identifier（标签协议标识符）** | **2 字节，取值 81-00** |
| 5 | **Tag Control Information（标签控制信息）** | **其中含 12 比特 VLAN ID 字段与 3 比特优先级字段（priority field，性质类似 IP 的 TOS）** |
| 6 | type | 2 字节 |
| 7 | data (payload) | 46 ～ 1500 字节 |
| 8 | CRC | **重新计算（Recomputed CRC）** |

课件原图的关键标注是：802.1Q 帧在**源地址之后、type 字段之前**插入两个字段，其中第一个是 2 字节的 Tag Protocol Identifier（值为 81-00），第二个是 Tag Control Information（包含 12 比特 VLAN ID 字段与 3 比特优先级字段，优先级字段的作用类似 IP TOS）；插入字段后**帧尾的 CRC 必须重新计算**。

> **补充说明（由原图标注的位宽直接推得，非课件原文）**：Tag Control Information 中 12 比特 VLAN ID 可表示的取值个数为 $2^{12}=4096$；3 比特优先级字段可表示的取值个数为 $2^{3}=8$。Tag Protocol Identifier 与 Tag Control Information 相加共 4 字节，因此插入标签后帧的固定头部长度比 802.1 帧增加 4 字节，这也是 CRC 必须重算的原因（被校验的内容发生了变化）。

---

## 4.10 本章小结（课件 4-39）

本章讨论**多种链路层技术（various link layer technologies）**，包括：

- LAN 模型（LAN model）；
- 以太网（Ethernet）；
- 集线器、交换机（hubs, switches）；
- VLAN（课件以「\*VLAN」标出，此处照录）。

本章到此结束。
