# 计算机网络 —— 第1章 绪论（Chapter 1: Introduction）

> **原始 PDF**：`D:\Escherichia30636\计算机网络\Chapter_1_3.pdf`
> **PDF 总页数**：24 页（对应课件幻灯片 Introduction: 1-69 至 1-92）
> **整理日期**：2026-10-15
>
> 本文按课件原有的章—节—小节顺序连续组织，保留课件的章节顺序与术语。课件未给出形如“1.7.1”的节号，正文中的 1.7、1.8、1.9、1.10 及各小节编号为按课件 roadmap 顺序与幻灯片页码补充的稳定编号；每小节标题后以括注给出对应的幻灯片编号与 PDF 页范围。定义、说明、公式关系、层次对应与图示还原均并入所属小节，不另设独立板块。

---

## 1.7 协议分层与参考模型（Protocol "layers" and reference models）

> 对应课件幻灯片 Introduction: 1-70 至 1-80（原 PDF 第 2—12 页）。课件第 1 页与第 13 页的 Chapter 1 roadmap 中，本大节对应条目 *Protocol layers, service models*（协议分层、服务模型）。

### 1.7.1 分层与参考模型的动因

课件在进入分层主题前先列出网络系统的构成要素。网络是复杂的，由许多“部件”（pieces）组成：

- 主机（hosts）
- 路由器（routers）
- 各种传输介质构成的链路（links of various media）
- 应用（applications）
- 协议（protocols）
- 硬件与软件（hardware, software）

课件随后提出两个问题：对于网络自身的结构（structure of network），是否存在组织它的方法；以及对于我们对网络的讨论（our discussion of networks），是否存在组织它的方法。这两个问题分别指向网络自身的结构化设计与讲解网络时的结构化叙述。

课件对“为什么分层”（Why layering?）给出的回答属于复杂系统设计/讨论的一般方法：

1. **显式结构便于识别系统各部件的身份及其相互关系**。课件称之为用于讨论的分层参考模型（layered *reference model* for discussion）。显式结构（explicit structure）的作用是让各个部件在模型中有确定位置，从而使部件之间的依赖关系可以被明确写出。
2. **模块化（modularization）便于系统的维护与更新**。课件给出两条推论：
   - 某一层的服务实现（service *implementation*）发生改变时，对系统其余部分透明（transparent to rest of system）；
   - 课件举例：登机口流程（gate procedure）的改变不影响系统其余部分。

这里需要区分两个概念：**层所提供的服务**与**该层服务的实现方式**。分层模型的稳定性建立在“服务不变、实现可变”这一区分上；只有当某层的实现改动不改变它向上一层提供的服务时，系统其余部分才不需要随之改动。

### 1.7.2 分层组织示例：航空旅行的组织

> 课件幻灯片 1-71、1-72。

课件以航空旅行系统的组织作为分层的示例（Example: organization of air travel），用于说明一个端到端过程可以分解为一连串步骤，每一步涉及一种服务。

#### 例题 1：航空旅行系统的组织（Example: organization of air travel）

**题干**：如何定义/讨论航空旅行系统（How would you *define/discuss* the system of airline travel?）？

**课件的回答**：它是一个包含一系列步骤的过程（a series of steps），涉及多种服务（involving many services）。整个过程被标注为“人加行李的端到端传递”（end-to-end transfer of person plus baggage）。

**步骤序列**：图中沿一条从出发地到目的地再返回出发地方向的路径列出以下步骤：

| 出发侧（自上而下） | 到达侧（自下而上） |
|---|---|
| ticket (purchase) 购票 | ticket (complain) 票务处理（投诉/退改） |
| baggage (check) 行李托运 | baggage (claim) 行李提取 |
| gates (load) 登机口装载 | gates (unload) 登机口卸载 |
| runway takeoff 跑道起飞 | runway landing 跑道降落 |
| airplane routing 航线选择 | airplane routing 航线选择 |

**路径关系**：图中路径由出发侧自上而下依次经过上述步骤，经中间的 airplane routing（航线选择）横跨到到达侧，再自下而上依次经过到达侧步骤回到起点方向。源图仅以一条折线表示这一行程路径，未标注各步骤之间的接口参数，故此处不给出步骤间的参数数值。

#### 例题 2：航空旅行按服务分层（layers: each layer implements a service）

**题干**：把例题 1 的步骤序列按“层”重新组织，使每一步对应一种服务。

**课件的组织方式**：把出发侧与到达侧的动作分列左右两列，中间列出该层所提供的服务（课件以斜体标注服务名）：

| 出发侧动作 | 服务（service） | 到达侧动作 |
|---|---|---|
| ticket (purchase) | *ticketing service*（票务服务） | ticket (complain) |
| baggage (check) | *baggage service*（行李服务） | baggage (claim) |
| gates (load) | *gate service*（登机口服务） | gates (unload) |
| runway takeoff | *runway service*（跑道服务） | runway landing |
| airplane routing | *routing service*（航线服务） | airplane routing |

**结论（层的定义性表述）**：每一层实现一种服务（each layer implements a service）。该服务的实现方式是：

- 通过该层自身的层内动作（via its own internal-layer actions）；
- 依赖下一层提供的服务（relying on services provided by layer below）。

在图中 ticketing、baggage、gate、runway、routing 五种服务各占一个水平条带，条带自左向右贯通；其中 airplane routing 所在条带被画成一条较窄的横线，与其余四个条带的宽度不同，课件未对该画法差异作文字说明，此处亦不作技术解读。

### 1.7.3 因特网协议栈的五层结构

> 课件幻灯片 1-74。

课件给出分层的因特网协议栈（Layered Internet protocol stack）。自顶向下五层及其定位与代表协议如下：

| 层（英文） | 定位（课件原文表述） | 代表协议 |
|---|---|---|
| *application* 应用层 | supporting network applications，支持网络应用 | HTTP、IMAP、SMTP、DNS |
| *transport* 传输层 | process-process data transfer，进程到进程的数据传送 | TCP、UDP |
| *network* 网络层 | routing of datagrams from source to destination，把数据报从源路由到目的 | IP、routing protocols（路由协议） |
| *link* 链路层 | data transfer between neighboring network elements，相邻网络元素之间的数据传送 | Ethernet、802.11（WiFi）、PPP |
| *physical* 物理层 | bits "on the wire"，比特在“线”上传输 | 课件未列出具体协议 |

课件图中以五格堆叠图给出层序，自顶向下依次为 application、transport、network、link、physical。物理层在课件文字与源图中均未列出具体协议，此处照录为空，不作补充。

### 1.7.4 服务、分层与封装：逐层封装过程与数据单元

> 课件幻灯片 1-75 至 1-79。这一组幻灯片是同一封装过程的连续图示。幻灯片 1-75 至 1-77 在页面上同时画出源端与目的端两个五层协议栈，左侧栈旁标注 source（源），右侧栈旁标注 destination（目的）；两个栈自顶向下的层序同为 application、transport、network、link、physical。以下按封装发生的顺序说明，并在每一步给出该层所依赖的下一层服务。

**（1）应用层交换报文（幻灯片 1-75 上层）**

应用层交换报文（messages），以实现某种应用服务，并使用传输层提供的服务。图中该层的水平箭头上画出的数据单元为：

$$M$$

即应用层报文（application-layer message），图中记为 $M$。

**（2）传输层封装为报文段（幻灯片 1-75）**

传输层协议把应用层报文 $M$ 与传输层首部 $H_t$ 一起封装，产生传输层报文段（transport-layer **segment**）：

$$[H_t \mid M]$$

其中 $H_t$（transport layer header，传输层首部）由传输层协议用于实现其服务。传输层协议利用网络层提供的服务（using services of network layer），把 $M$ 从一个进程传送给另一个进程（from one process to another）；课件注明这一传送可以是可靠的（e.g., reliably）。

**（3）网络层封装为数据报（幻灯片 1-76）**

网络层协议把传输层报文段 $[H_t \mid M]$ 与网络层首部 $H_n$ 一起封装，产生网络层数据报（network-layer **datagram**）：

$$[H_n \mid H_t \mid M]$$

其中 $H_n$（network layer header，网络层首部）由网络层协议用于实现其服务。网络层协议利用链路层提供的服务（using link layer services），把传输层报文段 $[H_t \mid M]$ 从一台主机传送到另一台主机（from one host to another）。

**（4）链路层封装为帧（幻灯片 1-77）**

链路层协议把网络层数据报 $[H_n \mid H_t \mid M]$ 与链路层首部 $H_l$ 一起封装，产生链路层帧（link-layer **frame**）：

$$[H_l \mid H_n \mid H_t \mid M]$$

其中 $H_l$（link layer header，链路层首部）由链路层协议用于实现其服务。链路层协议把数据报从一台主机传送到相邻主机（from host to neighboring host）。

> **课件文字笔误及更正（幻灯片 1-77，原 PDF 第 9 页）**：该页文字在说明链路层所依赖的下层服务时写作“using network-layer services”（使用网络层服务），即课件原文为
> “Link-layer protocol transfers datagram [Hn| [Ht |M] from host to neighboring host, using network-layer services”。
> 按协议栈的层序，链路层位于网络层之下、物理层之上，链路层实现其服务时所依赖的应当是**物理层服务**（physical-layer services），由物理层把比特序列送上传输介质。若按课件该页文字让链路层依赖网络层，则链路层与网络层之间将形成循环依赖，层序无法成立。因此该处为课件文字笔误，正确表述应为“using physical-layer services”；同页“Network-layer protocol transfers transport-layer segment [Ht | M] from one host to another, using link layer services”一句中的依赖关系（网络层使用链路层服务）则是正确的。
> 同一页的方括号写法为 $[H_n \mid [H_t \mid M]]$，其中内层方括号不配对，属课件原文写法；等价的标准写法为 $[H_n \mid H_t \mid M]$。

由上述四式可直接读出各层数据单元的长度关系（记 $|X|$ 为单元 $X$ 的长度）：

$$|segment| = |M| + |H_t|$$
$$|datagram| = |M| + |H_t| + |H_n|$$
$$|frame| = |M| + |H_t| + |H_n| + |H_l|$$

课件未给出上述任一字段的具体字节数，故不补充数值。

**封装过程中的依赖关系汇总**（与层序一致）：

| 本层协议 | 本层产生/处理的数据单元 | 依赖的下层服务 |
|---|---|---|
| 应用层 | 报文 $M$ | 传输层服务 |
| 传输层 | 报文段 $[H_t \mid M]$ | 网络层服务 |
| 网络层 | 数据报 $[H_n \mid H_t \mid M]$ | 链路层服务 |
| 链路层 | 帧 $[H_l \mid H_n \mid H_t \mid M]$ | 物理层服务（课件原文误作“网络层服务”，见上） |

### 1.7.5 封装的整体图示：名称序列与端到端视图

**（1）封装与数据单元名称（幻灯片 1-78）**

课件以 Matryoshka dolls（stacking dolls，俄罗斯套娃）的图片表示封装，图中四个套娃自左至右由小到大，其下方标注的名称依次为：

| 顺序 | 名称 | 对应数据单元 |
|---|---|---|
| 1（最小） | message（报文） | 应用层报文 $M$ |
| 2 | segment（报文段） | 传输层报文段 $[H_t \mid M]$ |
| 3 | datagram（数据报） | 网络层数据报 $[H_n \mid H_t \mid M]$ |
| 4（最大） | frame（帧） | 链路层帧 $[H_l \mid H_n \mid H_t \mid M]$ |

该页图片本身不含网络技术参数，其作用是给出封装后数据单元的外层逐层包含内层、量级由内到外逐层增大的对应关系。页面上标注了图片出处 `Credit: https://dribbble.com/shots/7182188-Babushka-Boi`。

**（2）封装与解封装的对应表（幻灯片 1-79）**

幻灯片 1-79 把上述四个数据单元与四层一一对应，在源端与目的端之间形成对应表：

| 层 | 数据单元名称 | 数据单元表示 |
|---|---|---|
| application | message | $M$ |
| transport | segment | $[H_t \mid M]$ |
| network | datagram | $[H_n \mid H_t \mid M]$ |
| link | frame | $[H_l \mid H_n \mid H_t \mid M]$ |

源端一侧沿箭头自 application 向下到达 link，完成逐层封装；随后沿物理链路传输；在目的端自 link 向上到达 application，按与封装相反的顺序逐层去掉本层首部：

- link 层收到帧 $[H_l \mid H_n \mid H_t \mid M]$，去掉 $H_l$ 后把 $[H_n \mid H_t \mid M]$ 交给 network 层；
- network 层去掉 $H_n$ 后把 $[H_t \mid M]$ 交给 transport 层；
- transport 层去掉 $H_t$ 后把 $M$ 交给 application 层。

**（3）端到端视图（Encapsulation: an end-end view，幻灯片 1-80）**

幻灯片 1-80 给出封装在网络中间设备参与下的端到端视图，图中出现的实体、所含层与出现在该实体附近的数据单元如下：

| 实体 | 图中标注 | 图中该实体含有的层 | 该实体附近出现的数据单元 |
|---|---|---|---|
| 源主机 | source | application、transport、network、link、physical | $M$；$[H_t \mid M]$；$[H_n \mid H_t \mid M]$；$[H_l \mid H_n \mid H_t \mid M]$ |
| 交换机 | switch | link、physical | 链路层帧 $[H_l \mid H_n \mid H_t \mid M]$ |
| 路由器 | router | network、link、physical | $[H_n \mid H_t \mid M]$ 与 $[H_l \mid H_n \mid H_t \mid M]$ |
| 目的主机 | destination | application、transport、network、link、physical | $[H_l \mid H_n \mid H_t \mid M]$；$[H_n \mid H_t \mid M]$；$[H_t \mid M]$；$M$ |

图中另有四行图例，给出四个数据单元的名称与表示：message 为 $M$，segment 为 $[H_t \mid M]$，datagram 为 $[H_n \mid H_t \mid M]$，frame 为 $[H_l \mid H_n \mid H_t \mid M]$。

由该图可直接读出的结构结论：

- **交换机（switch）只包含链路层与物理层两层**，因此它处理到链路层帧为止，不处理网络层及以上内容；
- **路由器（router）包含网络层、链路层、物理层三层**，因此它处理到网络层数据报；
- **源主机与目的主机包含完整的五层**，只有端主机才具有应用层与传输层，也只有在端主机上才出现报文 $M$ 与报文段 $[H_t \mid M]$；
- 源主机与目的主机之间的传输路径依次经过交换机与路由器；路径上的数据单元随所处链路段不同而在帧与数据报之间变化：在链路层与物理层的每一段链路上承载的是帧，路由器在向上处理到网络层时取出数据报 $[H_n \mid H_t \mid M]$，再为下一段链路重新封装成帧。

课件未在该页标注各链路的具体速率、时延或帧长度数值，故不补充数值。

> **关于图示的简化说明**：1.7.4 与 1.7.5 各页方框中只画出传输层、网络层、链路层的首部 $H_t$、$H_n$、$H_l$，未画出链路层尾部。实际链路层协议中有若干实现会在数据之后附加尾部字段，例如以太网（Ethernet）帧在末尾附加 4 字节的帧校验序列（FCS，Frame Check Sequence）用于差错检测。因此“链路层只在前面加首部”不能推广为所有链路层协议的一般性质，课件此处为简化示意。

---

## 1.8 因特网历史（Internet history）

> 对应课件幻灯片 Introduction: 1-82 至 1-86（原 PDF 第 14—18 页）。课件第 13 页的 roadmap 把本节主题标注为 *History*。课件按五个时期分段。

### 1.8.1 1961—1972：早期分组交换原理（Early packet-switching principles）

课件列出的史实条目：

- **1961**：Kleinrock（克莱因罗克）——排队论（queueing theory）显示出分组交换（packet-switching）的有效性。
- **1964**：Baran（巴兰）——在军用网中采用分组交换。
- **1967**：ARPAnet 由 Advanced Research Projects Agency（美国高级研究计划署）构想提出。
- **1969**：第一个 ARPAnet 节点投入运行。
- **1972**：
  - ARPAnet 公开演示（public demo）；
  - NCP（Network Control Protocol，网络控制协议）成为第一个主机到主机协议（first host-host protocol）；
  - 第一个电子邮件程序出现；
  - ARPAnet 拥有 15 个节点。

**辅助图：早期 ARPAnet 拓扑（THE ARPA NETWORK）**。该页附有一张早期 ARPAnet 连通示意图，用于表示 1969 年最初的 4 个节点及其互连关系。图中可辨认的节点与其配备的主机计算机如下：

| 节点 | 主机计算机标注 |
|---|---|
| SRI（Stanford Research Institute，斯坦福研究所） | SDS 940 |
| UTAH（University of Utah，犹他大学） | PDP-10 |
| UCSB（University of California, Santa Barbara，加州大学圣塔芭芭拉分校） | IBM 360 |
| UCLA（University of California, Los Angeles，加州大学洛杉矶分校） | Sigma 7 |

图中的互连关系为四条链路：SRI—UTAH、SRI—UCSB、SRI—UCLA、UCSB—UCLA。SRI 是该拓扑中的中心节点，与其余三个节点均直接相连；UCSB 与 UCLA 之间另有一条直接链路。

需要区分图与文字所述的时间语境：该图表示的是 1969 年最初运行时的 4 节点网络，而同一页文字所述的 15 个节点是 1972 年的规模。二者不是同一时点的网络状态，不能把 4 节点图当作 1972 年网络的完整拓扑。

### 1.8.2 1972—1980：网络互连、新网络与专有网络（Internetworking, new and proprietary networks）

课件列出的史实条目：

- **1970**：ALOHAnet 卫星网络（satellite network）在夏威夷建成。
- **1974**：Cerf 与 Kahn（瑟夫与卡恩）——提出互连网络的体系结构（architecture for interconnecting networks）。
- **1976**：Xerox PARC 提出以太网（Ethernet）。
- **70 年代后期（late 70's）**：出现专有体系结构 DECnet、SNA、XNA。
- **1979**：ARPAnet 拥有 200 个节点。

课件在同一页用方框列出 **Cerf 与 Kahn 的互连原则（Cerf and Kahn's internetworking principles）**，共四条：

1. **minimalism, autonomy**——最简化、自治：互连网络时不需要对网络内部作任何改动（no internal changes required to interconnect networks）；
2. **best-effort service model**——尽力而为服务模型；
3. **stateless routing**——无状态路由；
4. **decentralized control**——分散式控制。

课件对此方框的结论为：这些原则定义了今天的因特网体系结构（define today's Internet architecture）。

### 1.8.3 1980—1990：新协议、网络数量激增（new protocols, a proliferation of networks）

课件列出的史实条目：

- **1982**：定义 smtp 电子邮件协议。
- **1983**：部署 TCP/IP。
- **1983**：定义 DNS，用于名称到 IP 地址的转换（name-to-IP-address translation）。
- **1985**：定义 ftp 协议。
- **1988**：TCP 拥塞控制（congestion control）。
- **新的国家级网络**：CSnet、BITnet、NSFnet、Minitel。
- **100,000 台主机**连接到这一网络联合体（confederation of networks）。

**辅助图：NSFNET T1 Network 1991 拓扑图**。该页附有一张 1991 年 NSFNET T1 骨干网拓扑图（图题标注 “NSFNET T1 Network 1991”，图内标注版权归属 © Merit Network, Inc.）。该图用于表示 1990 年前后美国国家级科研骨干网的规模与连接形态：图在美国本土轮廓上画出一批骨干节点及其之间的连接链路。图中可辨认的节点标注包括 Boeing, WA；CA*net；SDSC；Palo Alto, CA；Salt Lake Cty, UT；Boulder, CO；Lincoln, NE；San Diego, CA；Houston, TX；Chicago, IL；Cleveland, OH；Pittsburgh, PA；Princeton, NJ；College Park, MD；Atlanta, GA；以及东北部区域的 Ithaca, NY 与跨国的 CAnet、CERN 等标注。个别节点名的完整拼写受图中字体大小所限无法完全确认，此处不再逐一转录，也不据图推断链路速率或节点数目。这张图的作用是给出“多个国家级网络并入同一骨干、并出现跨国连接”这一时间语境的直观印象，不构成需要求解的练习。

### 1.8.4 1990 年代与 2000 年代：商业化、Web 与新应用（commercialization, the Web, new applications）

课件列出的史实条目：

- **1990 年代初（early 1990s）**：ARPAnet 退役（decommissioned）。
- **1991**：NSF 解除对 NSFnet 商业使用的限制；NSFnet 于 1995 年退役（decommissioned, 1995）。
- **1990 年代初：Web**
  - 超文本（hypertext）[Bush 1945, Nelson 1960's]；
  - HTML、HTTP：Berners-Lee；
  - **1994**：Mosaic，其后为 Netscape；
  - **1990 年代后期**：Web 商业化。
- **1990 年代后期—2000 年代（late 1990s – 2000s）**：
  - 更多“杀手级应用”（killer apps）：即时消息（instant messaging）、P2P 文件共享（P2P file sharing）；
  - 网络安全（network security）被提到前台；
  - 约 5 000 万台主机，1 亿以上用户（est. 50 million host, 100 million+ users）；
  - 骨干链路以 Gbps 速率运行（backbone links running at Gbps）。

### 1.8.5 2005 年至今：规模、SDN、移动性与云（scale, SDN, mobility, cloud）

课件列出的条目：

- 宽带家庭接入的大量部署，速率为 10—100 余 Mbps（aggressive deployment of broadband home access, 10-100's Mbps）。
- **2008**：软件定义网络（software-defined networking，SDN）。
- 高速无线接入日益普及：4G/5G、WiFi。
- 服务提供商（Google、FB、Microsoft）建立自己的网络：绕过商用因特网，直接“贴近”终端用户连接（bypass commercial Internet to connect "close" to end user），提供对社交媒体、搜索、视频内容等的“瞬时”访问。
- 企业把服务运行在“云”中（e.g., Amazon Web Services, Microsoft Azure）。
- 智能手机兴起：在上网设备中移动设备数量超过固定设备（2017）。
- 约 150 亿台设备接入因特网（~15B devices attached to Internet，2023，statista.com）。

---

## 1.9 第 1 章小结（Chapter 1: summary）

> 对应课件幻灯片 Introduction: 1-87（原 PDF 第 19 页）。

课件以“我们已经覆盖了大量材料”（We've covered a "ton" of material!）为标题，列出第 1 章已覆盖的内容清单：

- 因特网概述（Internet overview）；
- 什么是协议（what's a protocol?）；
- 网络边缘、接入网、网络核心（network edge, access network, core）：
  - 分组交换与电路交换（packet-switching versus circuit-switching）；
  - 因特网结构（Internet structure）；
- 性能：丢失、时延、吞吐量（performance: loss, delay, throughput）；
- 分层、服务模型（layering, service models）；
- 安全（security）；
- 历史（history）。

课件同时说明学习者此时已具备的内容（You now have）：

- 关于网络的语境、概览、词汇与对网络运行的整体把握（context, overview, vocabulary, "feel" of networking）；
- 后续将有更多深度、细节与趣味内容（more depth, detail, and fun to follow!）。

---

## 1.10 补充幻灯片：OSI 参考模型、分层封装全过程与 Wireshark

> 对应课件幻灯片 Introduction: 1-88 至 1-92（原 PDF 第 20—24 页）。幻灯片 1-88（原 PDF 第 20 页）为单独的分隔标题页，页面文字仅为 “Additional Chapter 1 slides”，不含其他内容与图示；其后四页依次为 ISO/OSI 参考模型、“多于七层的 OSI 分层”、一次分层与封装的完整过程图，以及 Wireshark 工具页。

### 1.10.1 ISO/OSI 七层参考模型与 Internet 协议栈的层次差异

> 课件幻灯片 1-89（原 PDF 第 21 页），标题 ISO/OSI reference model，副标题 “Two layers not found in Internet protocol stack!”。

ISO/OSI 参考模型（Open Systems Interconnection reference model，开放系统互连参考模型）由国际标准化组织（ISO，International Organization for Standardization）提出，共七层。自下而上的层次依次为：

| 序号（自下而上） | 层名（英文） | 中文名 |
|---|---|---|
| 1 | physical | 物理层 |
| 2 | link | 链路层 |
| 3 | network | 网络层 |
| 4 | transport | 传输层 |
| 5 | session | 会话层 |
| 6 | presentation | 表示层 |
| 7 | application | 应用层 |

与之对照，Internet 协议栈（Internet protocol stack）只有五层：application、transport、network、link、physical。两者的对应关系是：Internet 协议栈的 application 层在功能上涵盖了 OSI 的 application、presentation、session 三层的职责；其余四层（transport、network、link、physical）在两种模型中一一对应。

课件明确给出这两个“Internet 协议栈中没有的层”及其职责：

- **presentation（表示层）**：使应用程序能够解释数据的含义（allow applications to interpret meaning of data），例如加密（encryption）、压缩（compression）、以及与具体机器相关的约定（machine-specific conventions）。
- **session（会话层）**：数据交换的同步（synchronization）、检查点（checkpointing）与恢复（recovery of data exchange）。

对这两层职责的说明：

1. presentation 层处理的是数据以什么形式表示。同一段语义内容可以有不同的编码形式（字符编码、字节序、压缩与否、是否加密），presentation 层负责在通信双方之间约定并完成这些表示形式的转换。加密与压缩都不改变数据要表达的内容，只改变承载它的比特序列，因此归入表示层而不是应用层。
2. session 层处理的是一次数据交换对话的状态管理。同步指在数据流中插入分隔点，使接收方能够按段落处理；检查点指在长过程中保存已完成进度的标记；恢复指通信中断后从最近检查点继续，而不是从头重传。这三项都属于对会话过程的控制，不涉及把数据从源转发到目的。

**Internet 协议栈“缺少”这两层的准确含义**：课件原文表述为 Internet stack “missing” these layers（missing 加了引号），并进一步说明：these services, *if needed*, must be implemented in application——这些服务如果需要，必须在应用层实现。课件随后以一个问句 “needed?”（需要吗？）结束，把“表示层与会话层所覆盖的功能是否必须由独立协议层提供”作为开放问题。

这里的“缺少”应理解为：Internet 体系结构没有为表示与会话这两类功能设立独立的协议层，而不是这两类功能在 Internet 中不存在。它们由应用层自行实现（例如应用层协议调用传输层安全机制完成加密、由应用层实体自行完成数据压缩和会话状态维护）。课件的引号用法与本页的 “needed?” 提问都表明这是一种体系结构上的取舍陈述，不是对功能缺失的判断。掌握本页内容后，能够解释为什么在抓包工具中看不到名为 presentation 或 session 的协议层，也能理解分层数不是固定的，层的划分依据是该层所承担的功能。

### 1.10.2 多于七层的 OSI 分层（More than seven OSI layers）

> 课件幻灯片 1-90（原 PDF 第 22 页）。

该页除标题与页码外只有一幅图像，无文字说明、无公式、无数据。图像主体为一个自上而下排列的层名列表，列表实体与 OSI 七层一致，自上而下为 application、presentation、session、transport、network、link、physical，并在 application 之上额外多出两行，名称分别为 **Financial** 与 **Political**；图像中另有圆圈文字 “You are here”（你在这里）指向上方这两行的区域。

该页是对“分层”这一表述方式的延伸性示意：在既有的技术分层之上再叠加两个与协议无关的组织性层名，用来表示现实系统中还存在着协议栈之外的层。它不引入新的协议、新的层次职责或新的数据单元，因此不属于需要掌握的层次模型。

### 1.10.3 分层服务与封装的完整过程

> 课件幻灯片 1-91（原 PDF 第 23 页），标题 Services, Layering and Encapsulation。该页与 1.7.4、1.7.5 所述的封装分组是同一知识点的分步图示，本页是整个过程完成后的最终形态：源端（source）主机与目的端（destination）主机的五层协议栈同时画出，并给出消息自源端应用层逐层封装、沿物理链路传输、在目的端逐层解封装的全过程。

**图的构成**：左侧为源端协议栈，层次自上而下写作 application、transport、network、link、physical；中部自上而下排列四种封装形式的方框，并由一条折线表示信号沿物理链路的传输；右侧为目的端协议栈，层次与源端相同。源端栈下方标注 *source*，目的端栈下方标注 *destination*。图中另有一列数据单元名称：message、segment、datagram、frame，与封装过程逐一对应。

**源端自顶向下的封装过程**：

第 1 步（application 层）：应用层产生报文，记为方框 $M$，数据单元名称为 **message（报文）**。

第 2 步（transport 层）：传输层协议把应用层报文 $M$ 作为载荷，在其前面加上传输层首部 $H_t$，构成传输层报文段（segment）。图中该方框的排列为 $H_t$ 在前、$M$ 在后：

$$H_t \mid M$$

第 3 步（network 层）：网络层协议把整个传输层报文段 $[H_t \mid M]$ 作为载荷，在其前面加上网络层首部 $H_n$，构成数据报（datagram）：

$$H_n \mid H_t \mid M$$

第 4 步（link 层）：链路层协议把整个网络层数据报 $[H_n \mid H_t \mid M]$ 作为载荷，在其前面加上链路层首部 $H_l$，构成帧（frame）：

$$H_l \mid H_n \mid H_t \mid M$$

第 5 步（physical 层）：帧在物理层以信号形式沿链路传输到目的端。

四种封装形式与各层、各数据单元名称的对应关系汇总如下：

| 所在层 | 数据单元名称 | 图示记号 | 本层添加的首部 | 载荷内容 |
|---|---|---|---|---|
| application | message | $M$ | 无 | 应用产生的原始数据 |
| transport | segment | $H_t \mid M$ | $H_t$ | $M$ |
| network | datagram | $H_n \mid H_t \mid M$ | $H_n$ | $H_t \mid M$ |
| link | frame | $H_l \mid H_n \mid H_t \mid M$ | $H_l$ | $H_n \mid H_t \mid M$ |
| physical | 比特流（图中不另标注名称） | 无（图上不画封装方框） | 无 | 整个帧的比特序列 |

**目的端自下而上的解封装过程**：

第 1 步（physical 层）：接收来自链路的信号，还原为帧 $H_l \mid H_n \mid H_t \mid M$。

第 2 步（link 层）：链路层读取并处理首部 $H_l$，将剩下的载荷 $[H_n \mid H_t \mid M]$ 上交给网络层。

第 3 步（network 层）：网络层读取并处理首部 $H_n$，将剩下的载荷 $[H_t \mid M]$ 上交给传输层。

第 4 步（transport 层）：传输层读取并处理首部 $H_t$，将剩下的载荷 $M$ 上交给应用层。

第 5 步（application 层）：应用层得到报文 $M$，与源端应用层产生的报文一致。

**图中反映的两条规则**：

1. 除应用层与物理层外，每一层都在收到的数据之前附加本层首部，因此封装后的数据长度逐层增加，且外层协议的载荷（payload）完整包含内层协议的首部与数据。
2. 目的端各层按相反顺序剥去首部，剥去的顺序与添加的顺序严格相反。

该图只画出了各层的首部 $H_t$、$H_n$、$H_l$，未画出链路层的尾部；如前所述，实际链路层协议中（如以太网帧的 4 字节 FCS）可能有尾部字段，本页图示为简化示意。图中方框只有 $H_t$、$H_n$、$H_l$ 三种记号，说明本图以传输、网络、链路三层的封装为示例，物理层只承担比特传输，不添加首部。

### 1.10.4 Wireshark：在真实主机上观测分层数据单元

> 课件幻灯片 1-92（原 PDF 第 24 页）。

该页用一幅部署示意图说明抓包工具与协议栈各层的对应关系。图中左侧为一台计算机，通过一条网线连接到右侧一台带天线的网络设备（路由器）。图中右上方有一个虚线框，框内标注 **WIRESHARK**，框内另有上下两个方框，上方为 **packet analyzer**（分组分析器），下方为 **packet capture (pcap)**（分组捕获），两者之间有上下双向箭头相连。虚线框下方另有一个自下而上列出各层的方框：

| 图中自下而上的排列 | 标注内容 |
|---|---|
| 第 1 行（最下） | Physical |
| 第 2 行 | Link (Ethernet) |
| 第 3 行 | Network (IP) |
| 第 4 行 | Transport (TCP/UDP) |
| 第 5 行（最上） | application（www browser、email client） |

该层次方框的上下分别用虚线分隔出 **OS** 与 **application** 两个区域：Physical、Link (Ethernet)、Network (IP)、Transport (TCP/UDP) 四行位于标注为 OS 的虚线区域内，最上方的 application（www browser、email client）位于虚线之上。图中另有一条标注为 **copy of all Ethernet frames sent/received**（收发的所有以太网帧的副本）的箭头，从 packet capture (pcap) 方框指向该协议层次方框所在位置，表示捕获动作发生在该接口处。

**图所说明的关系**：分组捕获（packet capture，图中缩写 pcap）从主机的网络接口处复制该主机收发到的所有以太网帧；分组分析器（packet analyzer）对这些副本逐层解析，从而在界面上分别展示 Link (Ethernet)、Network (IP)、Transport (TCP/UDP) 以及 application 各层的数据。图中 “copy of all Ethernet frames” 的标注表明捕获的对象是链路层的帧，因此捕获结果中可以看到完整的链路层首部、网络层首部、传输层首部与应用数据，即 1.10.3 所给的 $H_l \mid H_n \mid H_t \mid M$ 结构。

**与分层模型的对应关系**：图把 Physical、Link、Network、Transport 标注在标注为 OS 的虚线框内，把 application（www browser、email client）标注在虚线之上，说明应用层的实体是用户态应用程序（图中举出万维网浏览器与电子邮件客户端）；网络层及以上各层的协议由操作系统中的协议软件实现；物理层与链路层的功能则部分由网络接口硬件承担。Wireshark 自身在图中被画在虚线框内，其分组捕获组件与协议栈相邻，说明捕获点位于操作系统的链路层接口处。

**工具的性质**：Wireshark 是一个分组分析器（packet analyzer），也常被称为协议分析器（protocol analyzer）或抓包工具（packet sniffer）。它的用途是把前面各页所讲的抽象分层和封装过程落到可观测的字节序列上：通过查看一次真实通信中被捕获的帧，可以逐层展开看到链路层首部、网络层首部、传输层首部与应用层内容的实际字段与取值。本页只是说明工具与分层结构的对应关系，课件未在本页给出具体的抓包数据、字段取值或分析结果，因此本页不包含可复算的例题或数字案例。
