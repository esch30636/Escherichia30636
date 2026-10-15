# 计算机网络 —— 第1章 绪论（Chapter 1: Introduction）

> **原始 PDF**：`D:\Escherichia30636\计算机网络\Chapter_1_1.pdf`
> **PDF 总页数**：32 页（对应课件页脚编号 Introduction: 1-1 ～ 1-32）
> **整理日期**：2026-10-15

本笔记按课件原有的章—节顺序组织：课件第 1 章的主题为 Introduction，正文按“什么是 Internet 与什么是协议 → 网络边缘与接入网 → 物理介质 → 网络核心”的顺序连续讲解，每节末尾括注对应的课件页号以便溯源。课件本身只在页脚标注 “Introduction: 1-N”（1 为章号，N 为该章内的页序号），**未给出小节编号**；因此本文中的 `1.1`、`1.2`、`1.3`、`1.4` 及其下级编号（如 `1.2.3`）均为整理时补充的稳定编号，用于分节，不代表课件原有的编号。课件中未编号的内容按其在页序中的位置归入相应小节。

**课程与教材信息**（课件页 1-1、1-2）：课程名称为 Computer Network，任课教师刘智伟。课件列出三项教材，按课件原样列出：

| 序号 | 课件所列教材信息 |
|------|------------------|
| 1 | 计算机网络：自顶向下方法，原书第 8 版，机械工业出版社 |
| 2 | Computer Networking: A Top Down Approach, 9th ed., Pearson |
| 3 | 何顶新，郑定富，胡晓娅. 计算机网络及应用，北京：化学工业出版社，2011.06 |

其中第 1 项为第 2 项的中文译本，课件标出的版次分别为“原书第 8 版”与“9th ed.”（第 9 版），两者版次号不一致；课件未说明三本书的选用优先级与各章对应关系。课程成绩构成为：

| 考核项 | 课件原文 | 占比 |
|--------|----------|------|
| 平时 | Assignments (experiment + homework) + attendance，即作业（实验 + 家庭作业）+ 出勤 | 30% |
| 期末 | Final | 70% |

**本章目标与路线图**（课件页 1-3、1-4）：第 1 章的目标有两点——建立对计算机网络的整体感觉与全貌、初步接触术语（Get “feel,” “big picture,” introduction to terminology）；更多细节与深度在课程的后续部分展开（more depth, detail later in course）。课件给出的本章路线图共 7 项，顺序为：

1. What is the Internet? What is a protocol?（什么是 Internet，什么是协议）
2. Network edge: hosts, access network, physical media（网络边缘：主机、接入网、物理介质）
3. Network core: packet/circuit switching, internet structure（网络核心：分组交换/电路交换、Internet 结构）
4. Performance: loss, delay, throughput（性能：丢包、时延、吞吐量）
5. Protocol layers, service models（协议分层、服务模型）
6. Security（安全）
7. History（历史）

课件在讲授过程中多次重列这一路线图，每次把当前正在讲授的条目高亮、其余条目转灰以标示进度。重列时第 5 项与第 6 项的先后顺序出现过互换（课件页 1-11 把 Security 排在 Protocol layers, service models 之前，与课件页 1-4 相反），两页除这一处顺序外条目文字一致，此处按课件原样记录，不作统一。本课件（共 32 页）覆盖到路线图的第 3 项“网络核心”中的转发与路由，路线图其余各项属于本章后续课件页及后续章节。

---

## 1.1 什么是 Internet 与什么是协议（What is the Internet? What's a Protocol?）（课件页 1-5～1-10）

课件用两个互相补充的视角回答“什么是 Internet”：从构成部件出发的“构件”视角（a “nuts and bolts” view）和从对外提供的服务出发的“服务”视角（a “services” view）。两视角之后引出协议的定义与例示。

### 1.1.1 Internet 的“构件”视角

从构件出发，Internet 的构成可归纳为四类成分，课件给出的说明与例子如下：

| 构成成分 | 课件说明 | 课件给出的例子 |
|----------|----------|----------------|
| 联网计算设备（connected computing devices） | 数十亿计的联网计算设备（Billions of connected computing devices）；主机 = 端系统（hosts = end systems）；这些设备运行网络应用（network apps），位于 Internet 的“边缘”（at Internet's “edge”） | 图中绘出笔记本、台式机、手机、服务器、车辆等 |
| 分组交换机（packet switches） | 转发分组（forward packets），分组即数据块（chunks of data） | 路由器（routers）、交换机（switches） |
| 通信链路（communication links） | 在设备之间传送数据；传输速率（transmission rate）称为带宽（bandwidth） | 光纤（fiber）、铜缆（copper）、无线电（radio）、卫星（satellite） |
| 网络（networks） | 设备、路由器与链路的集合，由某个组织管理（collection of devices, routers, links: managed by an organization） | — |

由此得到三个基本对应关系：**主机（host）与端系统（end system）是同一概念**，指位于 Internet 边缘、运行网络应用的设备；**分组（packet）是数据的切块**，由分组交换机转发；**传输速率以带宽度量**，其单位是比特每秒（bit/s，课件未在本页写出单位符号，此为补充说明）。通信链路的传输速率在本课件后续页（课件页 1-24 起）用符号 $R$ 表示并给出定量关系，本处只给出名称。

课件进一步把 Internet 定义为“网络的网络”（Internet: “network of networks”），由互联的 ISP（interconnected ISPs）构成。ISP 即 Internet 服务提供商（Internet Service Provider）。课件用一张“网络之网络”结构图表示 Internet 的成员网络与连接关系：位于边缘的家庭网络（home network）、企业网络（enterprise network）与移动网络（mobile network）各自通过接入链路连到本地或区域 ISP（local or regional ISP），本地或区域 ISP 再上连国家或全球 ISP（national or global ISP）；内容提供商网络（content provider network）与数据中心网络（datacenter network）也接入到同一 ISP 层级之下。图中以“圆圈内加交叉线”的符号表示路由器，各区域之间的连线表示通信链路。这一结构说明：Internet 由大量彼此独立的网络经 ISP 互联而成，端系统处在边缘，转发设备处在核心，二者由接入网与物理链路连接（该图在课件页 1-12～1-14、1-15、1-22、1-29 等处重复使用，各以不同侧重讲解，本文在各相应小节按新语境说明，不重复罗列图元）。

课件页 1-7 在结构图之上补充指出**协议无处不在（protocols are everywhere）**：协议控制报文的发送与接收（control sending, receiving of messages）。课件给出的协议或协议相关名称举例如下：

| 课件所列名称 | 课件在同处标注的对应应用或场景 |
|--------------|----------------------------------|
| HTTP (Web) | Web 应用 |
| streaming video | 流媒体视频 |
| Zoom | 视频会议应用 |
| TCP | 传输控制协议，课件页 1-10 的例示即使用 TCP 建立连接 |
| IP | 网际协议 |
| WiFi | 无线局域网接入 |
| 4/5G | 蜂窝移动接入 |
| Ethernet | 以太网 |

同页还给出 **Internet 标准（Internet standards）** 的两个名词：RFC（Request for Comments，请求评论）与 IETF（Internet Engineering Task Force，Internet 工程任务组）。课件只给出这两个名称，未说明二者关系（即 IETF 负责制定、RFC 作为标准文档发布），也未给出具体 RFC 编号。

### 1.1.2 Internet 的“服务”视角与联网设备举例

换用服务的角度，Internet 被描述为两部分：

1. **向应用提供服务的基础设施（Infrastructure that provides services to applications）**。课件列举的应用为：Web、流媒体视频（streaming video）、多媒体电话会议（multimedia teleconferencing）、电子邮件（email）、游戏（games）、电子商务（e-commerce）、社交媒体（social media）、互联家电（inter-connected appliances）等，原文以省略号结尾表示列举未穷尽。
2. **为分布式应用提供编程接口（provides programming interface to distributed applications）**。该接口是“挂钩”（“hooks”），使发送方与接收方应用能够连接到 Internet 的传输服务（transport service）并使用它；接口提供服务选项（service options），课件原文称其类似于邮政服务提供的选项（“provides service options, analogous to postal service”，此句为课件原文中的类比表述，此处仅作原样记录）。这里的传输服务指 Internet 为应用提供的数据传送能力，具体服务模型在本章后续“协议分层、服务模型”部分展开。

“构件”视角中“联网计算设备”这一项，课件用一组具体设备清单加以展开，用以说明接入 Internet 的设备远不止传统计算机。课件所列设备名称如下（英文为课件原文，括号内中文为整理时补充的译名）：

- Web-enabled toaster + weather forecaster（可联网的烤面包机 + 天气预报器）
- Internet phones（联网电话）
- Slingbox: remote control cable TV（Slingbox：远程控制有线电视）
- Security Camera（安防摄像头）
- IP picture frame（IP 相框）
- Internet refrigerator（联网冰箱）
- Tweet-a-watt: monitor energy use（Tweet-a-watt：监测用电量）
- sensorized, bed mattress（带传感器的床垫）
- Amazon Echo
- Gaming devices（游戏设备）
- Pacemaker & Monitor（心脏起搏器与监测器）
- cars（汽车）
- scooters（滑板车）
- bikes（自行车）
- AR devices（增强现实设备）
- Fitbit
- diapers（尿布）

页末以 “Others?” 作开放式提问，课件未给出答案。

### 1.1.3 协议的定义与构成

协议分为“人协议”与“网络协议”两类对照介绍。**人协议（Human protocols）** 的课件举例为：问时间（“what's the time?”）、表示要提问（“I have a question”）、相互介绍（introductions）。**网络协议（Network protocols）** 有两条说明：协议的执行者是计算机或其他设备，而不是人（computers (devices) rather than humans）；Internet 中的全部通信活动都由协议支配（all communication activity in Internet governed by protocols）。

协议的严格定义为（课件原文）：Protocols define the format, order of messages sent and received among network entities, and actions taken on message transmission, receipt（协议定义网络实体之间所发送和接收的**报文格式（format）**、**报文次序（order）**，以及在**报文发送、接收时所采取的动作（actions）**）。该定义可拆成三个必须同时规定的成分：

| 成分 | 课件原文对应词 | 必须规定的内容 |
|------|----------------|----------------|
| 格式 | format | 报文的字段构成与各字段的取值形式 |
| 次序 | order | 报文的先后顺序，即哪一方先发、收到什么之后发什么 |
| 动作 | actions | 在发送报文、接收报文这两个时刻分别执行什么操作 |

课件同时以“规则针对什么”的方式复述该定义：规则针对的是具体发送哪些报文（specific messages sent），以及在收到报文或其他事件发生时采取哪些具体动作（specific actions taken when message received, or other events）。其中“其他事件”指收到报文之外的触发条件，课件本处未举例，后续章节在具体协议中给出。

### 1.1.4 人协议与计算机网络协议的对比例示

课件用两张并排的时序图对照说明人协议与计算机网络协议，两图共用一条自上而下的时间轴（图中标注 time），箭头表示报文的方向，箭头的上下位置表示先后顺序。

**人协议（对话双方为两个人）**，按时间轴自上而下：

| 步骤 | 方向 | 报文内容 | 说明 |
|------|------|----------|------|
| 1 | 甲 → 乙 | Hi | 打招呼，发起交互 |
| 2 | 乙 → 甲 | Hi | 应答 |
| 3 | 甲 → 乙 | Got the time? | 提出请求 |
| 4 | 乙 → 甲 | 2:00 | 给出所请求的信息 |

**计算机网络协议（对话双方为一台笔记本电脑与一台服务器）**，按同一时间轴自上而下：

| 步骤 | 方向 | 报文内容 | 说明 |
|------|------|----------|------|
| 1 | 客户机 → 服务器 | TCP connection request（TCP 连接请求） | 请求建立 TCP 连接 |
| 2 | 服务器 → 客户机 | TCP connection response（TCP 连接响应） | 对连接请求的应答 |
| 3 | 客户机 → 服务器 | GET http://gaia.cs.umass.edu/kurose_ross | HTTP 请求报文，请求获取该 URL 标识的资源 |
| 4 | 服务器 → 客户机 | \<file\> | 服务器回送被请求的文件 |

两张时序图逐条对应：打招呼对应连接请求与响应（一次问答各一个报文），提问与回答对应 GET 请求与文件回送。课件没有给出上述报文的任何字段细节（如 TCP 报文的首部字段、端口号、HTTP 方法之外的版本号等），也没有给出连接的建立时长等参数；上表四行报文与图中四个箭头一一对应，报文文字、方向与先后次序均与课件一致，图中第 3 步的 URL 原文为 `GET http://gaia.cs.umass.edu/kurose_ross`，第 4 步原文写作 `<file>`，表示服务器回送的文件，课件未给出该文件的实际名称与大小。页末有课件提出的问题：Q: other human protocols?（还有哪些人协议？），课件未给出答案，属开放式提问。

---

## 1.2 网络边缘与接入网（Network Edge and Access Networks）（课件页 1-12～1-24）

课件用同一张 Internet 结构图分三次（课件页 1-12、1-13、1-14）叠加文字，把 Internet 从外到内划为三段：网络边缘、接入网与物理介质、网络核心。随后（课件页 1-15 起）提出端系统如何接入边缘路由器的问题，并按住宅、机构、移动三类场景逐一讲解各类接入网，直至课件页 1-24 的主机分组发送功能。

### 1.2.1 Internet 结构的三段划分与网络边缘

课件对三段结构的规定为：

1. **网络边缘（network edge）**：由主机（hosts）构成；主机分为客户机（clients）与服务器（servers）两类角色；服务器通常放置在数据中心（data centers）中。
2. **接入网与物理介质（access networks, physical media）**：由有线（wired）与无线（wireless）通信链路构成，把边缘的主机接入到网络核心。
3. **网络核心（network core）**：由互相连接的路由器（interconnected routers）构成，其整体表现为“网络的网络”（network of networks）。

这一划分给出了一条从端系统到核心的路径：端系统（客户机或服务器）位于边缘；端系统经接入网中的有线或无线链路连接到边缘路由器；边缘路由器处在由路由器互联而成的网络核心中，分组沿核心中的路由器逐跳转发（网络核心的转发与路由见 1.4）。服务器集中在数据中心，是主机的一种布置方式，数据中心网络本身也是一种接入网（见 1.2.8）。

### 1.2.2 接入网总览：端系统如何接入边缘路由器

课件以提问方式引出本节：Q: How to connect end systems to edge router?（端系统如何连接到边缘路由器？）课件随即列出接入网的三类场景：

| 类别 | 课件原文 | 对应的接入技术（按本课件所讲内容） |
|------|----------|-------------------------------------|
| 住宅接入网 | residential access nets | 电缆接入（课件页 1-16、1-17）、DSL（课件页 1-18）、光纤到户 FTTH（课件页 1-23） |
| 机构接入网 | institutional access networks (school, company) | 以太网与 WiFi 混合的企业网（课件页 1-21） |
| 移动接入网 | mobile access networks (WiFi, 4G/5G) | 无线局域网与蜂窝接入（课件页 1-20） |

其中第三列为整理时按本课件后续页内容补注，课件只列出三类名称。住宅接入中另有家庭网络（课件页 1-19）与数据中心网络（课件页 1-22）两页作为补充场景，前者描述住宅内部把多种终端接入到对外链路的设备组合，后者描述服务器集中布置时的接入方式。

### 1.2.3 住宅接入：电缆接入与混合光纤同轴（HFC）

电缆接入（cable-based access）的拓扑为：多户住宅中的每一户各有一台电缆调制解调器（cable modem），经一个分路器（splitter）接到同轴电缆上，户内还接有电视机与计算机各一台；多户共用同一根同轴电缆干线，干线汇入电缆头端（cable headend）。头端一侧设有 CMTS（cable modem termination system，电缆调制解调器终端系统），CMTS 再连接到 ISP 一侧的一组路由器。课件对此给出的说明是：data, TV transmitted at different frequencies over shared cable distribution network（数据与电视在不同频率上、经由共享的电缆分配网传输）。

电缆接入在同一条同轴电缆上划分出多个频道，各频道的编号与用途为：1～6 号为视频频道（VIDEO，共 6 个），7～8 号为数据频道（DATA，共 2 个），9 号为控制频道（CONTROL，共 1 个），合计 9 个频道。不同频道占用不同频段，因而视频、数据与控制信息可在同一介质上并行传送。由此引出频分复用（frequency division multiplexing, FDM）的定义（课件原文）：frequency division multiplexing (FDM): different channels transmitted in different frequency bands（频分复用：不同的频道在不同的频带中传输）。其直接含义是：同一条物理介质上同时存在多个频道，各频道占用互不重叠的频率区间。

课件页 1-17 补充电缆接入的技术要点与速率数据：

1. **HFC（hybrid fiber coax，混合光纤同轴）**：该接入网由光纤与同轴电缆混合构成，其速率是非对称的（asymmetric）：
   - 下行传输速率（downstream transmission rate）：最高 40 Mbps – 1.2 Gbps；
   - 上行传输速率（upstream transmission rate）：30 – 100 Mbps。
2. **网络构成**：由 cable、fiber 组成的网络把家庭连接到 ISP 路由器（network of cable, fiber attaches homes to ISP router）。
3. **共享性**：各家庭共享接入网至 cable headend 的这一段（homes share access network to cable headend）。这一点与 1.2.4 的 DSL 使用专用线形成对照。

速率数据的核对（补充说明，非课件原有内容）：按 1 Gbps = 1000 Mbps 换算，下行上限 1.2 Gbps = 1200 Mbps，是下行下限 40 Mbps 的 30 倍，也远大于上行上限 100 Mbps，与课件所称“非对称”一致。课件未给出上下行速率不等的成因解释。

### 1.2.4 住宅接入：数字用户线（DSL）

数字用户线（digital subscriber line, DSL）接入的拓扑为：住宅内设有电话机一台、计算机一台、DSL 调制解调器（DSL modem）与分路器（splitter）各一个；户内的语音线路与数据线路经 splitter 汇合到一条电话线上，该线连到中心局（central office）。中心局内有 DSLAM（DSL access multiplexer，数字用户线接入复用器）；DSLAM 一方面向上连到电话网（telephone network，图中以黑色圆点表示网络中的节点，课件未标注这些圆点的具体名称），另一方面向下连接到 ISP 一侧的一组路由器。课件对家庭至中心局这段线路的标注是：voice, data transmitted at different frequencies over dedicated line to central office（语音与数据以不同频率、经专用线传输到中心局）。

课件给出的技术要点为：

1. 使用已有的电话线连接到中心局的 DSLAM（use existing telephone line to central office DSLAM）。
2. 在该电话线上对数据的处理方式是频率分离：承载的数据送往 Internet（data over DSL phone line goes to Internet），承载的语音送往电话网（voice over DSL phone line goes to telephone net）。
3. 速率数据（均为专用，dedicated）：
   - 下行传输速率：24 – 52 Mbps（dedicated downstream transmission rate）；
   - 上行传输速率：3.5 – 16 Mbps（dedicated upstream transmission rate）。

**电缆接入与 DSL 的对照**（由课件前述数据汇总，非课件原有表格）：

| 比较项 | 电缆接入（cable-based access） | DSL |
|--------|-------------------------------|-----|
| 所用介质 | 光纤与同轴电缆混合（HFC） | 已有的电话线（双绞线） |
| 频谱使用方式 | 频分复用，电视与数据占用不同频道 | 语音与数据以不同频率传输 |
| 到 ISP 的线路性质 | 各家庭共享接入网到 cable headend 的一段 | 到中心局的线路为专用 |
| 下行速率 | 40 Mbps – 1.2 Gbps | 24 – 52 Mbps |
| 上行速率 | 30 – 100 Mbps | 3.5 – 16 Mbps |
| 汇聚设备 | cable headend 处的 CMTS | 中心局内的 DSLAM |

### 1.2.5 家庭网络

家庭网络描述住宅内部把多种终端接入到对外链路的设备组合。房屋外部的连线为 to/from headend or central office（去往/来自 headend 或中心局），即家庭网络对外经电缆接入或 DSL 接入连接到上一级的 headend 或中心局。房屋内部由外向内依次为：

| 图中元素 | 课件标注 | 说明 |
|----------|----------|------|
| 调制解调器 | cable or DSL modem | 电缆调制解调器或 DSL 调制解调器，视对外接入类型而定 |
| 带交叉线圆圈符号的设备 | router, firewall, NAT | 分别承担路由、防火墙与 NAT 三项功能 |
| 有线连接 | wired Ethernet (1 Gbps) | 有线以太网，速率 1 Gbps，图中一条标注线指向台式机 |
| 无线接入设备 | WiFi wireless access point (54, 450 Mbps) | WiFi 无线接入点，速率 54、450 Mbps，图中以带波纹的符号表示 |
| 各类终端 | Wireless and wired devices | 无线与有线设备，图中画有手机、笔记本、台式机、显示器/电视类设备与冰箱等外形图标 |

课件用红色虚线椭圆把无线接入点、路由器与调制解调器三者圈在一起，并标注 often combined in single box（这三者常常组合在单个盒子中），说明住宅中常见的做法是把调制解调器、路由器（含防火墙与 NAT）与无线接入点做在一个设备里。

术语说明：课件在本页只给出缩写 NAT，未给出全称与解释；NAT 的全称为 Network Address Translation（网络地址转换），Firewall 即防火墙（用于过滤进出家庭网络的报文）。以上为补充解释，用于说明该缩写的含义。有线以太网部分的速率为 1 Gbps；无线部分的 54、450 Mbps 两个数值与 1.2.6 中 802.11 的速率列举一致。

### 1.2.6 无线接入网

总体的说明为：共享的无线接入网把端系统连接到路由器，连接经由基站（base station）完成，基站又称“接入点”（aka “access point”）。此处“共享”指多台端系统使用同一个无线接入网（同一频段资源）与其上的路由器通信，与 1.2.3 中“各家庭共享一段接入网”相对应。无线接入分为两类。

**第一类：无线局域网（Wireless local area networks, WLANs）**

- 通常位于建筑物内或建筑物周围（typically within or around building），覆盖距离约 100 ft（换算约为 30.48 m，换算值由整理者补充，课件只给出 100 ft）。
- 标准与速率：802.11b/g/n (WiFi)：11、54、450 Mbps，即 802.11b、802.11g、802.11n 三代标准的传输速率分别为 11 Mbps、54 Mbps、450 Mbps（课件把三代标准并列写成 “802.11b/g/n (WiFi)” 并在其后给出对应数值序列，未逐一代次分列）。
- 图中房屋内有笔记本、冰箱等设备与无线接入点、路由器，路由器经一条连线对外并标注 to Internet。

**第二类：广域蜂窝接入网（Wide-area cellular access networks）**

- 由移动、蜂窝网络运营商提供（provided by mobile, cellular network operator），覆盖范围为 10's km，即数十千米；
- 速率为 10's Mbps，即数十 Mbps；
- 采用 4G/5G 蜂窝网络。
- 图中移动网络的云状区域内有手机、汽车、笔记本、塔形基站与路由器符号，路由器经一条连线对外并标注 to Internet。

**两类无线接入的对照**（按课件原文整理）：

| 比较项 | 无线局域网（WLANs） | 广域蜂窝接入网 |
|--------|---------------------|----------------|
| 覆盖范围 | 建筑物内或周边，约 100 ft | 数十千米（10's km） |
| 速率 | 11、54、450 Mbps（802.11b/g/n） | 数十 Mbps（10's Mbps） |
| 技术与标准 | 802.11b/g/n（WiFi） | 4G/5G |
| 提供方 | 课件未指明（通常为家庭或机构自行部署，此为补充说明） | 移动、蜂窝网络运营商 |
| 接入方式 | 端系统经基站（接入点）连接到路由器 | 端系统经蜂窝基站接入运营商网络 |

### 1.2.7 企业接入网

企业网（enterprise network）指公司、大学等机构自建的接入网，其使用者是机构内部的终端与服务器，而不是家庭用户。课件的定义性描述有三条：

1. 适用对象为 companies, universities, etc.（公司、大学等机构）。
2. 技术上是混合的有线与无线链路技术（mix of wired, wireless link technologies），并把交换机（switch）与路由器（router）混合组网；课件明确说明这两类设备的差别将在后续章节展开（we'll cover differences shortly）。
3. 链路速率指标：
   - 以太网（Ethernet）：有线接入，速率为 100 Mbps、1 Gbps、10 Gbps；
   - WiFi：无线接入点（wireless access point），速率标为 11、54、450 Mbps。

企业网的组成部分与连接关系为：企业内的多台台式主机接入以太网交换机（Ethernet switch）；多台笔记本电脑通过 WiFi 接入无线接入点，无线接入点再向上连到以太网交换机；以太网交换机汇聚有线主机与无线接入点后，向上连到机构路由器（institutional router）；机构路由器向下连机构自建的邮件、Web 服务器（institutional mail, web servers），向右经链路连到 ISP（Enterprise link to ISP）。即企业网内部同时存在有线以太网域与无线 WiFi 域，二者经以太网交换机汇聚，再由机构路由器统一出口接到 ISP。课件未在图上标注各段链路的传输速率数值，只有文字给出以太网与 WiFi 的速率范围，不应把图示速率与具体链路段一一对应。

### 1.2.8 数据中心网络

数据中心网络（data center network）的描述为：高带宽链路（high-bandwidth links，速率在数十至数百 Gbps，即 10s to 100s Gbps）把数百至数千台服务器（hundreds to thousands of servers）互连在一起，并把它们接入 Internet。课件在此附有一张数据中心机房实景照片，其来源标注为 Courtesy: Massachusetts Green High Performance Computing Center (mghpcc.org)，该照片只用于示意数据中心机房的物理规模，不含可提取的网络参数。在“网络之网络”结构图中，数据中心网络与内容提供商网络都接在本地或区域 ISP / 国家或全球 ISP 之下，属于与家庭网络、企业网络、移动网络并列的成员网络。

### 1.2.9 光纤到户（FTTH）

光纤到户（fiber to the home，FTTH）是把光纤直接铺到住户的接入方式，属于点到多点结构，采用无源光网络（PON，passive optical network）。其组成部分从网络侧到用户侧依次为：

| 位置（从网络侧到用户侧） | 图元 | 说明 |
|--------------------------|------|------|
| 最左 | ISP | 网络侧起点 |
| 左二 | central office（中心局） | 内含 OLT |
| 中心局内 | OLT（optical line terminal，光线路终端） | 中心局侧的端点设备 |
| 左三 | ODN（optical distribution network，光分配网络） | 内含 splitter |
| ODN 内 | splitter 1 : N（分光器，1 比 N） | 把一个下行信号分配到 N 路，标注 no powered equipment（无有源设备） |
| 最右 | home 1、home 2 … home N | N 个住户，每个住户内含 ONT 与 Wi-Fi |
| 户内 | ONT（optical network terminal，光网络终端）随后接 Wi-Fi | 家中由 Wi-Fi 提供无线接入 |

两段光纤的命名与位置对应关系为：**shared feeder fiber（共享馈线光纤）** 位于中心局与分光器之间，为所有住户共用；**dedicated drop fiber to each home（到各户的专用入户光纤）** 位于分光器与每个住户的 ONT 之间，每户一条。课件另给出三条技术要点：PON 的具体体制为 GPON / 10G-PON；fiber to ONT，即光纤一直铺设到住户的 ONT；Ethernet or Wi-Fi inside the home，即进入住户后户内使用以太网或 Wi-Fi。

FTTH 与前面两种住宅接入的差别在于：cable 与 DSL 在中心局到住户段使用已有的铜质介质（同轴电缆或电话双绞线），FTTH 在该段使用光纤；而 ODN 中的分光器是无源器件，不需要供电（课件明确标注 no powered equipment）。

### 1.2.10 主机：分组数据的发送与传输时延

主机（host）的发送功能（host sending function）由课件定义为三步：

1. 取得应用层报文（takes application message）；
2. 把报文分割为更小的数据块，这些数据块称为分组（packet），每个分组的长度为 $L$ 比特（breaks into smaller chunks, known as packets, of length $L$ bits）；
3. 以传输速率 $R$ 把分组发送（transmits）进接入网。

符号与单位为：

| 符号 | 含义 | 单位 |
|------|------|------|
| $L$ | 一个分组的长度 | bits（比特） |
| $R$ | 链路传输速率（link transmission rate） | bits/sec（比特/秒） |
| $L/R$ | 分组传输时延（packet transmission delay） | sec（秒） |

课件给出的术语等价关系为：链路传输速率 $R$ 又称链路容量（link capacity），又称链路带宽（link bandwidth），三者指同一量。

分组传输时延的定义为把一个 $L$ 比特的分组推入链路所需的时间（time needed to transmit $L$-bit packet into link），公式为

$$
d_{\text{trans}}=\frac{L\ (\text{bits})}{R\ (\text{bits/sec})}\ \text{(sec)}
$$

课件图中共画出一台主机向右侧路由器方向发送两个分组，标注 two packets, L bits each（两个分组，每个 $L$ 比特），分组编号为 1、2，并标出 $R$: link transmission rate；图中的编号 1、2 只表示分组先后次序，不代表数值。

**对该公式的说明**：课件本页只给出上式与符号含义，未给任何 $L$、$R$ 的具体数值，因此不给出代入数值的算例。该公式的成立前提是：分组长度固定为 $L$ 比特，链路以恒定速率 $R$ 比特/秒把比特推入链路，且不计中间停顿。按此前提，推入的比特数每增加 $L$，所需时间就增加 $L/R$；发送两个分组所需的总时间为 $2L/R$（两个分组串行推入同一条链路），这是该公式对图中“两个分组”情形的直接推论，不是课件给出的独立结论。

---

## 1.3 物理介质（Links: Physical Media）（课件页 1-25～1-27）

接入网与核心中的链路最终都要落实到某种物理介质上。本节先给出比特与物理链路的基本概念及介质分类，再逐一说明双绞线、同轴电缆、光纤与无线电台四类介质，并给出各类无线链路类型的速率与距离数据。

### 1.3.1 比特、物理链路与介质分类

课件给出的三个基本术语为：

1. **比特（bit）**：在发送器/接收器对（transmitter/receiver pairs）之间传播（propagates）。
2. **物理链路（physical link）**：发送器与接收器之间实际存在的东西（what lies between transmitter & receiver）。
3. 物理链路按信号传播方式分为两类：
   - **导引型介质（guided media）**：信号在固体介质中传播（signals propagate in solid media），介质包括铜（copper）、光纤（fiber）、同轴电缆（coax）。
   - **非导引型介质（unguided media）**：信号自由传播（signals propagate freely），例如无线电（radio）。

### 1.3.2 双绞线（Twisted Pair, TP）

双绞线由两根绝缘铜线构成（two insulated copper wires），属于导引型介质。课件给出的分类与速率指标为：

| 类别 | 速率 | 用途（课件标注） |
|------|------|------------------|
| Category 5（5 类） | 100 Mbps、1 Gbps | Ethernet |
| Category 6（6 类） | 10 Gbps | Ethernet |

课件在本节配有一张双绞线线缆与 RJ 型插头的实物照片，不含可提取的技术参数，仅用于识别该介质外形。

### 1.3.3 同轴电缆（Coaxial Cable）

同轴电缆的课件描述为：

1. 两根同心铜导体（two concentric copper conductors）；
2. 双向传输（bidirectional）；
3. 宽带（broadband）：一根电缆上可划分多个频段信道（multiple frequency channels on cable），每个信道速率在数百 Mbps（100's Mbps per channel）。

### 1.3.4 光纤（Fiber Optic Cable）

光纤的课件描述为：

1. 玻璃纤维中传输光脉冲，每个脉冲表示一个比特（glass fiber carrying light pulses, each pulse a bit）；
2. 高速工作（high-speed operation）：点到点高速传输，速率在数十至数百 Gbps（10's–100's Gbps）；
3. 低误码率（low error rate）：中继器（repeater）可以相距很远（repeaters spaced far apart）；不受电磁噪声影响（immune to electromagnetic noise）。

### 1.3.5 无线电台（Wireless Radio）与无线链路类型

**无线电台**的课件描述为：

1. 信号在电磁频谱（electromagnetic spectrum）中的不同频段（bands）上承载；
2. 没有物理导线（no physical “wire”），属非导引型介质；
3. 广播（broadcast）、半双工（half-duplex），方向为发送方到接收方（sender to receiver）；
4. 传播环境的影响（propagation environment effects）有三项：反射（reflection）、被物体遮挡（obstruction by objects）、干扰/噪声（Interference/noise）。

**无线链路类型（radio link types）** 的课件数据为：

| 链路类型 | 速率 | 距离/时延 |
|----------|------|-----------|
| 无线局域网 Wireless LAN（WiFi） | 10–100's Mbps | 数十米（10's of meters） |
| 广域无线 wide-area（如 4G/5G 蜂窝） | 100's Mbps（4G/5G） | 约 10 km（~10 Km） |
| 蓝牙 Bluetooth | 有限速率（limited rates） | 短距离（short distances）；用途为 cable replacement（替代线缆） |
| 地面微波 terrestrial microwave | 45 Mbps 每信道（45 Mbps channels） | 点到点（point-to-point） |
| 卫星 satellite | 下行最高不到 100 Mbps（up to < 100 Mbps，Starlink） | 端到端时延 270 msec（geostationary，对地静止轨道卫星） |

需要区分的是：上表中的“10–100's Mbps”“100's Mbps”“45 Mbps”“< 100 Mbps”都是链路速率的课件标称值（数量级或上限值），不是精确理论极限；270 msec 是课件给出的一条具体端到端时延数值，其限定条件是地球静止轨道（geostationary）。

---

## 1.4 网络核心（The Network Core）（课件页 1-28～1-32）

课件在课件页 1-28 再次给出本章路线图，加重显示的条目为 “Network core: packet/circuit switching, internet structure”，标志本节开始；课件页 1-29 至 1-32 依次讲解网络核心的构成与分组交换、核心的两个关键功能转发与路由，并用公路地图对照二者的区别。课件本部分只讲到分组交换的定性定义与转发/路由的分工，分组交换与电路交换的详细对比、时延计算与统计复用等内容在本课件之后的页面（课件页 1-33 起）才展开。

### 1.4.1 网络核心的构成与分组交换

课件对网络核心（network core）给出两条定义性描述：

1. 网络核心是互连路由器的网状结构（mesh of interconnected routers）。
2. **分组交换（packet-switching）**：主机把应用层报文分割成**分组（packets）**；网络把这些分组从一个路由器转发到下一个路由器，跨越从源到目的地的路径上的各条链路（network forwards packets from one router to the next, across links on path from source to destination）。

结合 1.1.1 的“网络之网络”结构，分组在网络核心中的行进路径为：源主机所在的家网络/企业网/移动网络接入本地或区域 ISP，本地或区域 ISP 上连国家或全球 ISP，数据中心网络与内容提供商网络亦接在同一 ISP 层级之下；分组在源与目的之间沿这条路径上的路由器逐跳转发。

本处只给出“分组交换”的定义式描述，**没有**给出分组交换与电路交换（circuit switching）的对比数据、时延计算或统计复用结论，这些在课件页 1-33 之后才展开。

### 1.4.2 网络核心的两个关键功能：转发与路由

课件把网络核心的功能分解为两项，并给出各自的动作范围（本地 local 与全局 global）：

**转发（Forwarding）**：

- 又称交换（aka “switching”）；
- 是**本地动作（local action）**：把到达的分组从路由器的输入链路移动到合适的路由器输出链路（move arriving packets from router's input link to appropriate router output link）；
- 判定依据：到达分组首部中的目的地址（destination address in arriving packet's header）。

**路由（Routing）**：

- 是**全局动作（global action）**：确定分组所走的源—目的路径（determine source-destination paths taken by packets）；
- 由**路由算法（routing algorithms）**完成。

两者的分工关系为：路由算法在全局范围内算出路径，并把结果装入路由器的本地转发表；转发则在每个路由器上按本地转发表逐分组执行。课件图给出了这一关系：`routing algorithm` 指向 `local forwarding table`，表按“首部值 → 输出链路”查表。

课件图中给出的 **local forwarding table（本地转发表）完整内容**如下（逐行保留）：

| header value（首部值） | output link（输出链路） |
|---|---|
| 0100 | 3 |
| 0101 | 2 |
| 0111 | 2 |
| 1001 | 1 |

图中同时画出一个到达分组的首部目的地址值为 **0111**，并按图中标注的路径编号 **3 → 2 → 1** 行进。按该图数据逐步复算：

第 1 步：分组到达路径上编号为 3 的路由器，其首部值取自图中标注的目的地址，即 0111。

第 2 步：在该路由器的转发表中查首部值 0111。查表找到匹配行：首部值 0111 对应 output link = 2。

第 3 步：按转发的定义，把该分组从输入链路移动到输出链路 2，即把分组交给路径编号 2 的那台路由器。这一步对应的正是表格中的第 3 行（0111 → 2）。

第 4 步：分组到达编号 2 的路由器，继续查表转发，最终经编号 1 的路由器离开该网络核心区域，对应图中路径标注 3 → 2 → 1。

校验：表中四个首部值 0100、0101、0111、1001 两两不同，而输出链路取值只有 1、2、3 三种，其中 2 出现两次（0101、0111 都指向 2）。这说明转发表把两个不同的目的地址映射到同一条输出链路，即**转发是逐条表项查表，不要求首部值与输出链路一一对应**；对照第 3 步的查表结果，0111 命中且只命中第 3 行，取值为 2，与图中红色路径上该跳的去向一致。

该图还说明了转发与路由的层次关系：转发表的内容由路由算法（全局）产生，转发只做查表与搬移（本地），因此同一个首部值在不同路由器上可以有不同的输出链路——图中的每一台路由器都各有一份自己的转发表副本。

### 1.4.3 路由与转发的图示说明

课件用同一张美国公路地图（课件页 1-31、1-32）说明 routing 与 forwarding 的区别。课件页 1-31 标注 routing，地图上以红色实线标出一条自西向东横贯的路线，西端标注 San Jose，东端标注 Northampton；图中另给出两条由地图服务生成的公路行车信息：5,853 miles / 45 h，3,309 miles / 48 h。课件页 1-32 标注 forwarding（出现两处），使用同一张地图与同一条红色路线，另加两个局部放大框，分别放大西端 San Francisco 一带与东部 Cleveland 一带的路网，框内以红色箭头标出在城市路网上的若干转向动作，即 forwarding 的转向选择。

对照 1.4.2 的定义，这两页图表达的区别是：routing 对应于确定整条从源到目的的路线（对应图中的横贯全美路线与两端城市名）；forwarding 对应于在路线上的每个中间位置决定下一个局部出口（对应图中的两个局部路网放大框与其中的转向）。图中出现的 miles 与小时数是地图服务给出的公路行车里程与时间，**不是**网络性能参数，不应代入任何网络时延计算；本节课件页未给出任何网络侧的数值例，该图只作定性示意。
