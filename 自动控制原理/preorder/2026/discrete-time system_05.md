# 自动控制原理II —— 线性离散系统（五）：离散系统的动态性能与稳态误差

> **来源课件**：`D:\Escherichia30636\自动控制原理\preorder\2026\discrete-time system_05.pdf`（共 28 页）
> **所属章节**：第7章 线性离散系统的分析与设计（Analysis and Design of Linear Discrete-Time System / Sampled-data System）—— 7.6 节的后半部分（7.6.2 动态性能、7.6.3 稳态误差）
> **整理日期**：2026-09-15
> **本课件承接关系**：7.6.1 稳定性由课件 `discrete-time system_04` 讲完；本课件从 7.6.2 动态性能进入，到 7.6.3 稳态误差结束。

---

## 结构体系

### 第7章章节总目录（课件第1页）
```
Chapter 7 Analysis and Design of Linear Discrete-Time System (Sampled-data System)
7.1  Introduction
7.2  The Sampling Process and Sampling Theorem
7.3  Signal Recovery and Zero-Order Hold
7.4  Z-Transform and Inverse Z Transform
7.5  Mathematical Models of Discrete-Time Systems                        ← 课件 _03
7.6  Performance Analysis of Discrete-Time Systems                       ← 红色高亮，课件 _04（7.6.1）与本课件（7.6.2、7.6.3）
7.7  Digital Control Design for Discrete-Time Systems
```

### 7.6 节内容索引（课件第4页、第15页，两次出现）
```
7.6 Performance Analysis of Discrete-Time Systems
├── Stability                                ← 已由课件 _04 讲完（7.6.1）
├── Dynamic Performance                      ← 本课件 7.6.2（第4页红色）
└── Steady-state Errors                      ← 本课件 7.6.3（第15页红色）
```

### 7.6 节的三条稳定性主线回顾（课件第2页、第3页）
```
7.6 节要讲的三个问题（第2页原文字）
├── s-Domain to z-Domain Mapping
├── Necessary and Sufficient Condition for Stability of Linear Discrete-Time Systems
│     — All poles of Φ(z) lie in the unit circle of z plane
└── Routh criterion in w domain (Generalized Routh Criterion)

三种判别方法总览图（第3页）
"we've learned three methods to determine the stability of a discrete-time systems."
├── [s] 平面：σ–jω，紧贴 jω 轴左侧的阴影带＝稳定区，右侧＝不稳定区
├── z = e^{sT}  →  [z] 平面：Re–Im，单位圆内＝稳定区，圆外＝不稳定区
└── w = (z+1)/(z−1)  →  [w] 平面：u–jυ，左半平面（阴影带）＝稳定区
```

### 7.6.2 动态性能（课件第5–14页）
```
7.6.2 Dynamic Performance Analysis of Discrete-Time Systems
├── 1. General algorithm to obtain the dynamic performance（第5页）
│     ├── (1) Obtain the impulse transfer function：
│     │        GH(z)=Z[G(s)H(s)]，Φ(z)=G(z)/(1+GH(z))=M(z)/D(z)
│     ├── (2) C(z)=Φ(z)R(z)=M(z)/D(z)·z/(z−1)=c(0)+c(T)z⁻¹+c(2T)z⁻²+⋯
│     ├── (3) c*(t)=c(0)δ(t)+c(T)δ(t−T)+c(2T)δ(t−2T)+⋯
│     └── (4) Determine the specifications σ%、t_s
├── Example 1（第6页，无 ZOH，T=K=1）→ t_p=3T, σ%=20.7%, t_s=5T
├── Example 1（第7页，有 ZOH，T=K=1）→ t_p=4T, σ%=40%,  t_s=12T
├── 对比图（第8页）：有 ZOH / 无 ZOH / 连续系统 三条响应与三个指标
├── 2. Relationship between dynamic response and closed-loop poles（第9页）
│     ├── Φ(z)=M(z)/D(z)=(b_m/a_n)·∏(z−z_i)/∏(z−p_k)，m≤n
│     ├── C(z)=M(1)/D(1)·z/(z−1)+Σ c_k z/(z−p_k)
│     ├── (1) Single closed-loop poles on the real axis：c_k(nT)=c_k·p_k^n
│     │     ├── 极点位置与响应形状对照图（第10页，6 个波形）
│     │     └── [z] 平面响应图（第11页，8 个波形）
│     └── (2) Closed-loop Complex conjugate poles（第12页）
│           └── c_{k,k}(nT)=2|c_k|e^{anT}cos(nωT+φ_k)，a=(1/T)ln|p_k|，ω=θ_k/T
│                 └── θ_k=±45°、90°、135° 的响应对照图（第13页）
└── 小结：两条求取途径（第14页）(1) General method  (2) Closed-loop poles
```

### 7.6.3 稳态误差（课件第16–28页）
```
7.6.3 Steady-state error of discrete systems
├── 性能指标示意图（第17页）：超调量、误差带、稳态误差(t→∞)、上升时间 t_r、峰值时间 t_p、调节时间 t_s
├── 1. General method to obtain steady-state error（第16页）
│     └── 先求系统响应，再按定义在响应序列上读取稳态误差
│     └── Example（第16页，沿用 T=K=1 的例题数据与响应表）
├── 2. Using final value theorem to obtain steady-state error（第18页）
│     ├── Let：GH(z)=Z[G(s)H(s)]=1/(z−1)^v·GH_0(z)，lim_{z→1}GH_0(z)=K（v：System type）
│     ├── Φ_e(z)=E(z)/R(z)=1/(1+GH(z))
│     ├── Algorithm：(1) Determine the stability
│     │              (2) Obtain the impulse transfer function from E(z) to R(z)
│     │              (3) Obtain e(∞) by the final value theorem
│     └── Example 1（第19–20页，K=2、T=1）
│           ├── G(z)=K(1−e^{−T})z/((z−1)(z−e^{−T}))，v=1
│           ├── Φ_e(z)=(z−1)(z−e^{−T})/[(z−1)(z−e^{−T})+K(1−e^{−T})z]
│           ├── D(z)=z²+[K(1−e^{−T})−(1+e^{−T})]z+e^{−T}=0 → 0<K<2(1+e^{−T})/(1−e^{−T})=4.33
│           └── r₁=1(t)：e₁(∞)=0；r₂=t：e₂(∞)=T/K；r₃=t²/2：e₃(∞)=∞
└── 3. Static Error Constant Method（第21–27页）
      ├── 适用条件与前置分解（第21页）：For stable linear discrete systems subject to
      │     r(t) and sampled at the error signal；v: System type；Φ_e(z)、e(∞) 极限式
      ├── 三类输入下的误差常数定义与结论（第22页）
      │     ├── r(t)=A·1(t)  ：K_p = 1 + lim_{z→1} GH(z)，e(∞T)=A/K_p   （右侧浅绿方框）
      │     ├── r(t)=A·t     ：K_v = lim_{z→1}(z−1)GH(z)，e(∞T)=AT/K_v  （右侧浅绿方框）
      │     └── r(t)=(A/2)t² ：K_a = lim_{z→1}(z−1)²GH(z)，e(∞T)=AT²/K_a（右侧浅绿方框）
      ├── 按 z=1 极点个数划分系统型别（第23页）
      │     ├── Type 0：K_p=常数；Type≥1：K_p=∞, e(∞)=0
      │     └── Type 0：K_v=0, e(∞)=∞；Type=1：K_v=常数；Type≥2：K_v=∞, e(∞)=0
      ├── 加速度误差常数的型别结论（第24页）
      │     └── Type 0,1：K_a=0, e(∞)=∞；Type=2：K_a=常数；Type≥3：K_a=∞, e(∞)=0
      ├── 型别—误差常数—稳态误差总表（第25页，3 型 × 3 常数 × 3 误差 = 9 格）
      ├── Example 2（第26页）：r(t)=2t 时有无 ZOH 的 e(∞) 对比
      │     ├── no ZOH ：K_v=K，  e(∞)=AT/K_v=2T/K — dependent of T
      │     └── with ZOH：K_v=KT， e(∞)=AT/K_v=A/K=2/K — independent of T
      ├── Example 3（第27页）：T=0.25，r(t)=2·1(t)+t，求 e(∞)<0.5 的 K 范围 → 2<K<2.472
      └── 小结：7.6.3 的三种求法（第28页）
            (1) General method: obtain system response
            (2) Final value theorem：G(z)→Φ_e(z)、D(z)→Stability、e(∞)=lim(z−1)R(z)Φ_e(z)
            (3) Static error constant：G(z)→v, K_p, K_v, K_a → Obtain e(∞)
```

### 页码—主题速查
| 页码 | 主题 |
|---|---|
| 1 | 第7章章节目录（7.6 红色高亮） |
| 2 | 7.6 节三条任务 |
| 3 | 三种判稳方法总览图（[s]/[z]/[w] 三平面） |
| 4 | 7.6 节目录（Dynamic Performance 红色） |
| 5 | 7.6.2 动态性能一般算法（四步）+ 结构图 |
| 6 | Example 1：无 ZOH，T=K=1 |
| 7 | Example 1：有 ZOH，T=K=1 |
| 8 | 三条响应对比图与指标数据表 |
| 9 | 动态响应与闭环极点（一般表达式、实极点） |
| 10 | 实极点位置—波形对照（6 个波形） |
| 11 | [z] 平面极点—波形对照（8 个波形） |
| 12 | 闭环共轭复极点（一般表达式） |
| 13 | 共轭复极点位置—波形对照（4 组） |
| 14 | 7.6.2 小结：两条途径 |
| 15 | 7.6 节目录（Steady-state Errors 红色） |
| 16 | 7.6.3 一般方法 + 例题（沿用 T=K=1 响应表） |
| 17 | 控制系统性能指标示意图 |
| 18 | 终值定理法（Let + Algorithm 三步） |
| 19–20 | Example 1：K=2、T=1，三种输入的 e(∞) |
| 21 | 静态误差常数法总述 + 误差处采样结构图 |
| 22 | 三类输入的 e(∞T) 推导与 K_p、K_v、K_a 定义 |
| 23 | 型别划分依据 + K_p、K_v 的型别结论 |
| 24 | K_a 的型别结论 |
| 25 | 型别—误差常数—稳态误差总表 |
| 26 | Example 2：有无 ZOH 的 e(∞) 对比 |
| 27 | Example 3：由 e(∞)<0.5 求 K 范围 |
| 28 | 7.6.3 三种求法总纲 |

---

## 知识点详解

### 知识点 1：7.6 节的主题构成与三种稳定性判别方法的总览

**定义**：课件第2页把 7.6 节（Performance Analysis of Discrete-Time Systems）的内容列为三条：

1. **s-Domain to z-Domain Mapping**（s 域到 z 域的映射）；
2. **Necessary and Sufficient Condition for Stability of Linear Discrete-Time Systems**（线性离散时间系统稳定性的充分必要条件）——条件是"All poles of $\Phi(z)$ lie in the unit circle of z plane"，即 $\Phi(z)$ 的全部极点位于 $z$ 平面单位圆内；
3. **Routh criterion in w domain (Generalized Routh Criterion)**（w 域的劳斯判据，即广义劳斯判据）。

课件第3页给出这三条主线的图形总览（原图文字为："we've learned three methods to determine the stability of a discrete-time systems."）：图中的 **[s] 平面**（横轴 $\sigma$，纵轴 $j\omega$，原点标 $0$）把紧贴 $j\omega$ 轴左侧的竖直条带画成斜线阴影并标注"稳定区"，$j\omega$ 轴右侧标注"不稳定区"；图中给出映射公式

$$z = e^{sT}$$

**[z] 平面**（横轴 Re，纵轴 Im，横轴上标出 $-1$、$0$、$1$）画出单位圆，圆内标注"稳定区"、圆外标注"不稳定区"，并紧贴单位圆内侧画出斜线阴影带；图中给出映射公式

$$w = \frac{z+1}{z-1}$$

**[w] 平面**（横轴 $u$，纵轴 $j\upsilon$，原点标 $0$）把紧贴 $j\upsilon$ 轴左侧的竖直条带画成斜线阴影，即左半平面为稳定区。第3页 [s] 平面阴影带顶部标有一个 $\otimes$ 记号（原图如此，该页未对记号作文字说明）。

**理解**：
- 第2页的三条不是三个独立理论，而是同一个问题的三个环节：第一条建立 $z=e^{sT}$ 下 $s$ 平面区域与 $z$ 平面区域的对应关系；第二条给出稳定性判据的最终结论（$\Phi(z)$ 的全部极点位于单位圆内）；第三条给出"如何在不直接求根的条件下判断极点是否都在单位圆内"的办法。
- 三条的顺序不可交换：第二条的结论以第一条的映射关系为依据；第三条的做法（双线性变换到 $w$ 域再用劳斯判据）以第二条的结论为待判定目标。
- 第3页的三个平面图说明"稳定区"的边界形状在三套坐标下各不相同：$[s]$ 平面是虚轴，$[z]$ 平面是单位圆，$[w]$ 平面是虚轴。其中 $[s]$ 平面与 $[w]$ 平面的稳定区都是左半平面，形状相同；$[z]$ 平面的稳定区由半平面变为单位圆内部。

**作用**：这是 7.6 节的总纲。它确定了本节所有内容都围绕"极点位置"这一条线索展开：稳定性看极点是否在单位圆内，动态性能看极点在单位圆内的具体位置（第10、11、13页），稳态误差看 $z=1$ 处极点的个数（第18、19页）。与前置知识点"Z 变换定义 $z=e^{Ts}$""劳斯判据"直接相连；与后置的 7.6.2、7.6.3 是总纲与展开的关系。

---

### 知识点 2：离散系统动态性能的一般求取算法

**定义**：课件第5页（7.6.2 节）给出"Obtain the dynamic performance"的一般算法，共四步。

设系统的脉冲传递函数（impulse transfer function）为

$$
GH(z) = Z\left[G(s)H(s)\right], \qquad
\Phi(z) = \frac{G(z)}{1+GH(z)} = \frac{M(z)}{D(z)}
$$

这里 $GH(z)$ 表示**两个环节相乘后再取 Z 变换**，$G(z)$ 表示**单独对 $G(s)$ 取 Z 变换**，$M(z)$、$D(z)$ 分别为闭环脉冲传递函数的分子与分母多项式。

(1) **Obtain the impulse transfer function**：求出 $GH(z)$ 与 $\Phi(z)$。

(2) 求输出：

$$
C(z) = \Phi(z)R(z) = \frac{M(z)}{D(z)}\cdot\frac{z}{z-1}
= c(0) + c(T)z^{-1} + c(2T)z^{-2} + \cdots
$$

（式中 $R(z)=z/(z-1)$ 为单位阶跃的 Z 变换，$c(0)$、$c(T)$、$c(2T)$ 为输出序列各采样时刻的值。）

(3) 写出采样输出：

$$
c^{*}(t) = c(0)\delta(t) + c(T)\delta(t-T) + c(2T)\delta(t-2T) + \cdots
$$

(4) **Determine the specifications** $\sigma\%$、$t_s$（超调量与调节时间）。

课件第5页右侧给出对应的系统结构：参考输入 $r$ 与反馈信号在相加点（$\otimes$）比较，偏差 $e$ 经**采样开关**得到 $e^{*}$，再送入 $G(s)$，输出 $c$ 经采样开关得到 $c^{*}$，反馈通路为 $H(s)$。图中上方三个括号分别标出：$\Phi(z)$ 覆盖 $r\to c$ 全程，$\Phi_e(z)$ 覆盖 $r\to e^{*}$，$G(z)$ 覆盖 $e^{*}\to c$。

**理解**：
- 这个算法把"求动态性能"归约为"求一个序列"。$C(z)$ 展开成 $z^{-1}$ 的幂级数后，$z^{-k}$ 的系数就是第 $k$ 个采样时刻的输出值 $c(kT)$，所以不需要求出 $c(t)$ 的连续表达式。
- 第 (2) 步中 $\Phi(z)$ 的分母 $D(z)$ 决定序列的形状，分子 $M(z)$ 决定序列的幅度与相位；分母的根就是闭环极点，这正是后面第9页起把响应与极点位置联系起来的原因。
- $c^{*}(t)$ 是一串冲激之和，每个冲激的面积等于该时刻的采样值。第 (3) 步只是把第 (2) 步的序列改写为时域表达，两者包含的信息相同。
- 第 (4) 步的 $\sigma\%$ 与 $t_s$ 不能在 $z$ 域上直接套连续系统的公式求得，必须回到序列 $c(kT)$ 上按定义读取（峰值与终值的差占比、进入并保持在误差带内的时刻）。课件第6、7页的例题正是这样做。
- 结构图中"比较点在采样开关之前"这一点决定了 $\Phi(z)$ 的写法：偏差 $e$ 采样后进入 $G(s)$，而反馈通道中的 $H(s)$ 与 $G(s)$ 是被同一个采样信号激励的，因此反馈项是 $GH(z)=Z[G(s)H(s)]$ 而不是 $G(z)H(z)$。

**作用**：这是 7.6.2 节的第一条主线，也是"定义法"求动态性能的完整流程。后续第9–13页的"极点法"是本算法的替代路线：不必逐项做长除法，只由极点位置即可判断响应形状。与知识点 3、4 是"通用流程"与"由极点直接判断"的关系；与知识点 6 的性能指标定义直接相连（第 (4) 步的 $\sigma\%$、$t_s$ 由第17页定义）。

---

### 知识点 3：动态响应与闭环实极点的关系

**定义**：课件第9页给出 7.6.2 节第 2 条主线"Relationship between dynamic response and closed-loop poles"。设

$$
\Phi(z) = \frac{M(z)}{D(z)} = \frac{b_m}{a_n}\cdot\frac{\prod_{i=1}^{m}(z-z_i)}{\prod_{k=1}^{n}(z-p_k)}, \qquad m \le n
$$

（$z_i$ 为零点，$p_k$ 为闭环极点，$b_m$、$a_n$ 为分子、分母最高次项系数，$m\le n$ 表示分子阶次不高于分母阶次。）

输入为单位阶跃 $R(z)=z/(z-1)$ 时，

$$
C(z) = \Phi(z)R(z) = \frac{M(z)}{D(z)}\cdot\frac{z}{z-1}
= \frac{M(1)}{D(1)}\cdot\frac{z}{z-1} + \sum_{k=1}^{n}\frac{c_k z}{z-p_k}
$$

（第一项是终值对应的分量，系数为 $M(1)/D(1)$；第二项是各极点产生的暂态分量之和，$c_k$ 为对应极点 $p_k$ 的留数系数。）

(1) **Single closed-loop poles on the real axis**（闭环实极点，且互不相同）：

$$
c_k^{*}(t) = Z^{-1}\left[\frac{c_k z}{z-p_k}\right], \qquad k = 1,2,\cdots,n
$$

$$
c_k(nT) = c_k\,p_k^{\,n}, \qquad k = 1,2,\cdots,n
$$

课件第10页进一步按 $p_k$ 的符号分类并给出位置—波形对照：$p_k>0$ 时分为 $p_k>1$、$p_k=1$、$p_k<1$ 三种；$p_k<0$ 时同样给出对应的三种情形（$p_k<-1$、$p_k=-1$、$-1<p_k<0$）。

**第10页图（z-Plane 极点位置与 $c_k^{*}(t)$ 波形对照）**：图中画出 $z$ 平面实轴（标 $-1$、$0$、$1$）与单位圆，实轴上用 $\times$ 标出极点位置，并用箭头连到各自对应的 $c_k^{*}(t)$ 波形（横轴为采样序号 $n$，纵轴为 $c_k(nT)$）：

- $\times$ 在 $+1$ 右侧（$|z|>1$ 正实轴）：波形为逐项递增的单调阶梯，包络线向上弯（单调发散）；
- $\times$ 在 $+1$ 处：波形为各采样值相等的常值序列，包络线为水平线（等幅）；
- $\times$ 在 $0$ 与 $+1$ 之间：波形为逐项递减的单调阶梯，包络线向下弯（单调衰减）；
- $\times$ 在 $-1$ 与 $0$ 之间：波形为正负交替、幅度递减的序列（衰减振荡）；
- $\times$ 在 $-1$ 处：波形为正负交替、幅度不变的序列（等幅振荡）；
- $\times$ 在 $-1$ 左侧（$|z|>1$ 负实轴）：波形为正负交替、幅度递增的序列（发散振荡）。

**第11页图（[z] 平面极点位置与 $c_k^{*}(t)$ 波形对照）**：图中画出 $z$ 平面（纵轴标 $j$，原点标 $0$）与单位圆，沿实轴自左至右排列 8 个 $c_k^{*}(t)$ 波形，纵轴刻度按波形分别为 $10\sim-8$、$1\sim-1$、$1\sim-1$ 等：

1. 最左（$|z|>1$ 的负实轴）：正负交替且幅度递增的序列，纵轴刻度最大到 $+10$、最小到 $-8$（发散振荡）；
2. 第二个（$z=-1$）：正负交替、幅度恒为 $\pm1$ 的序列（等幅振荡）；
3. 第三个（$-1<z<0$）：$+1$ 起始，随后 $-0.5$、$+0.4$、$-0.35$、$+0.25$、$-0.2$…… 正负交替、幅度递减（衰减振荡）；
4. 第四个（靠近 $0$）：$t=0$ 处为 $+1$，其后各采样值迅速衰减到接近 $0$（在 $-0.15$ 与 $+0.15$ 之间小幅摆动后贴近横轴）；
5. 第五个：$t=0$ 处为 $+1$，$t=T$ 处为 $-0.4$，其后各采样值贴近横轴（衰减最快的两支之一）；
6. 第六个（$0<z<1$）：$+1$、$+0.5$、$+0.3$、$+0.2$、$+0.1$…… 全部为正、单调递减到 $0$（单调衰减）；
7. 第七个（$z=+1$）：各采样值恒为 $+0.6$ 附近的常值序列，图下方标注 $\omega=0$，横轴上标出 $1$（等幅，$\omega=0$）；
8. 最右（$|z|>1$ 的正实轴）：序列从 $0$ 起逐项递增到 $+10$（单调发散）。

**理解**：
- $c_k(nT)=c_k p_k^{n}$ 的含义是：第 $k$ 个极点对输出的贡献是一个几何序列，公比就是极点本身。因此极点在实轴上的位置直接决定这一支分量的增减与符号交替。
- 实轴上 $p_k>0$ 时 $p_k^{n}$ 恒为正，序列单调；$p_k<0$ 时 $p_k^{n}$ 的符号逐项改变，序列出现正负交替。这就是"极点符号决定是否振荡"的完整内容。
- $|p_k|$ 决定增减：$|p_k|>1$ 时 $|p_k|^{n}$ 随 $n$ 增大而增大，序列发散；$|p_k|=1$ 时 $|p_k|^{n}=1$，幅度不变；$|p_k|<1$ 时逐项衰减到零。
- $|p_k|$ 越接近 $0$，衰减越快；因此同样在单位圆内的极点，靠近原点的极点对应的暂态分量消失得比靠近圆周的更快。第11页图中第 4、5 两支波形在 $t=T$ 之后就贴近横轴，就是这一点的直接体现。
- 第10页图中单位圆上的两个点 $z=+1$ 与 $z=-1$ 都对应等幅序列，区别在于 $\omega=0$ 时序列为正的常值（不振荡），$\omega=\pi/T$（$z=-1$）时序列为正负交替（振荡）。这说明"是否振荡"由极点在实轴上的正负决定，"是否衰减"由极点到原点的距离决定，两个因素彼此独立。

**作用**：这是 7.6.2 节的第二条主线，把知识点 2 的第 (4) 步（求 $\sigma\%$、$t_s$）转化为一次极点定位判断。它为后面的设计问题（第7章 7.7 节按性能要求配置极点）提供了直接的依据：要求"无振荡"就要求全部闭环极点位于正实轴，要求"衰减快"就要求极点靠近原点。与知识点 4（复极点）构成"实极点/复极点"两类情形的并列关系。

---

### 知识点 4：动态响应与闭环共轭复极点的关系

**定义**：课件第12页给出 **(2) Closed-loop Complex conjugate poles**（闭环共轭复极点）。设

$$
p_k = |p_k|e^{j\theta_k}, \qquad \bar{p}_k = |p_k|e^{-j\theta_k}
$$

则这两个极点共同产生的分量为

$$
c^{*}_{\,k,k}(k) = Z^{-1}\left[\frac{c_k z}{z-p_k} + \frac{\bar{c}_k z}{z-\bar{p}_k}\right]
$$

$$
c_{k,k}(nT) = c_k p_k^{\,n} + \bar{c}_k \bar{p}_k^{\,n}
$$

$$
= |c_k|e^{j\varphi_k}e^{(a+j\omega)nT} + |c_k|e^{-j\varphi_k}e^{(a-j\omega)nT}
$$

$$
= 2|c_k|e^{anT}\cos(n\omega T + \varphi_k)
$$

其中各量为

$$
a = \frac{1}{T}\ln|p_k|, \qquad \omega = \frac{\theta_k}{T}, \qquad 0 < \theta_k < \pi
$$

- $|p_k|$：极点到原点的距离（极点的模）；
- $\theta_k$：极点相角，取值范围 $0<\theta_k<\pi$，即极点在 $z$ 平面上半平面；
- $\bar{p}_k$：$p_k$ 的共轭极点（下半平面对称位置）；
- $c_k$、$\bar{c}_k$：对应极点处的留数系数，互为共轭，写成 $|c_k|e^{\pm j\varphi_k}$；
- $a$：由 $|p_k|$ 通过 $a=\frac{1}{T}\ln|p_k|$ 定义的对数量，它出现在指数 $e^{anT}$ 中，$e^{anT} = |p_k|^{n}$；
- $\omega$：由 $\theta_k$ 通过 $\omega=\theta_k/T$ 定义的振荡角频率，$n\omega T = n\theta_k$。

**第13页图（共轭复极点位置与响应波形对照）**：图中标题为"z 平面"，画纵轴 $j$、横轴与原点 $0$，并画出单位圆；图中用射线把每一对共轭极点 $(\times)$ 连到自己的响应波形，左上方另有文字 $|p_k|<1,\ |p_k|>1$。四组对照为：

- $\theta_k=90^\circ,\ |p_k|<1$（单位圆内、正虚轴上的一对极点）：响应为衰减振荡，每个周期含 4 个采样点（一个周期内出现 $0$、峰、$0$、谷），幅度逐周期递减；
- $\theta_k=45^\circ,\ |p_k|<1$（单位圆内、辐角 $45^\circ$ 的一对极点）：响应为衰减振荡，每个周期含 8 个采样点，振荡比 $\theta_k=90^\circ$ 时缓慢，幅度逐周期递减；
- $\theta_k=135^\circ,\ |p_k|=1$（单位圆上、辐角 $135^\circ$ 的一对极点）：响应为等幅振荡，每个周期含 $360^\circ/135^\circ=2.67$ 个采样点，包络线为两条水平线；
- $\theta_k=-45^\circ,\ |p_k|>1$（单位圆外、辐角 $-45^\circ$ 的一对极点）：响应为发散振荡，每个周期含 8 个采样点，包络线为向外张开的楔形。

**理解**：
- 共轭极点必须成对处理的原因是一对共轭极点产生的两项含 $e^{\pm j\varphi_k}$ 与 $e^{\pm j\omega nT}$，两项相加后按欧拉公式合并为一个实余弦：$e^{j\psi}+e^{-j\psi}=2\cos\psi$。因此结果 $2|c_k|e^{anT}\cos(n\omega T+\varphi_k)$ 是实数，与 $c_{k,k}(nT)$ 应为实序列这一要求一致。
- 结果由三个因子相乘构成：$2|c_k|$ 是幅度系数（由留数决定），$e^{anT}=|p_k|^{n}$ 是包络因子，$\cos(n\omega T+\varphi_k)$ 是振荡因子。三个因子对应的三个信息分别是：响应幅度、衰减或发散的快慢、振荡的快慢与初相。
- 振荡的快慢由相角 $\theta_k$ 决定：$n\omega T=n\theta_k$ 说明每经过一个采样周期，余弦的相位前进 $\theta_k$。因此 $\theta_k$ 越大，一个周期所需的采样点数越少，振荡越快；第13页中 $\theta_k=90^\circ$ 时每周期 4 点、$\theta_k=45^\circ$ 时每周期 8 点，正是 $360^\circ/\theta_k$ 的算术结果。
- 当 $\theta_k=0$ 或 $\theta_k=\pi$ 时，极点落在实轴上，退化为知识点 3 的实极点情形（$\theta_k=\pi$ 对应负实轴上的等幅或衰减振荡，即cos 取 $\pm1$ 的交替序列）。
- 当 $|p_k|=1$ 时 $a=\frac{1}{T}\ln 1=0$，$e^{anT}=1$，包络不衰减也不增长，响应为等幅振荡；这就是 $|p_k|=1$ 对应临界情形在复极点下的具体形式。

**作用**：这是知识点 3 的补充与一般化，两者合起来覆盖单位圆内所有极点位置。它给出了"振荡周期"这一可直接读出的量：一个振荡周期内的采样点数 $=360^\circ/\theta_k$，从而把相角与响应的快慢联系起来。与知识点 3 是"实极点/复极点"的并列关系；与知识点 1 中"单位圆为稳定边界"的结论直接相连（$|p_k|$ 与 1 的大小关系决定包络的增减）。

---

### 知识点 5：动态性能求取的两条途径小结

**定义**：课件第14页（标题 7.6.2 Analysis of discrete-time dynamic performance）把本节的方法归纳为两条：

**(1) General method（一般方法）**：

$$
G(z) \rightarrow \Phi(z) \xrightarrow{\ \ \ } C(z) = \sum_{n=0}^{\infty} c(nT)z^{-n}
$$

$$
c^{*}(t) = \sum_{n=0}^{\infty} c(nT)\delta(t-nT) \rightarrow \textbf{Obtain } \sigma\%,\ t_s \textbf{ by definition}
$$

**(2) Closed-loop poles（闭环极点法）**：

$$
\text{Closed-loop poles } p_k \xrightarrow{\ \ \ } \text{Response } c_k(nT) = C_k\,p_k^{\,n}
$$

（课件原文此处系数写作大写的 $C_k$，与第9、10页的小写 $c_k$ 记号不同。）

**理解**：
- 两条途径的输入不同：第一条的输入是脉冲传递函数 $\Phi(z)$，输出是一串具体的数值 $c(nT)$，因此可以得到确切的 $\sigma\%$ 与 $t_s$；第二条的输入只是极点 $p_k$，输出是各分量的通式 $C_k p_k^{n}$，只能得到响应的形状与变化趋势，不能得到确切的峰值与调节时间。
- 两条途径都需要先知道 $\Phi(z)$ 的分母（即极点），区别在于是否继续做长除法或部分分式展开得到全部数值。
- 第一条中的"by definition"指 $\sigma\%$ 与 $t_s$ 按定义在序列上读取（对照第17页的指标定义），而不是套用连续系统的二阶近似公式。
- 第二条的价值在于设计阶段：设计时先按性能要求确定极点应放置的位置，再由极点位置反推需要什么控制器，此时用不到具体数值序列。

**作用**：这是 7.6.2 节的收束，把知识点 2 与知识点 3、4 并列为可选的两种做法。与知识点 6（性能指标定义）配合构成完整流程：第二条确定形状，第一条确定数值，指标按第17页的定义读取。

---

### 知识点 6：控制系统性能指标的定义

**定义**：课件第17页（图题为"控制系统性能指标"）用一条阶跃响应曲线 $C(t)$（横轴 $t$，纵轴 $C(t)$，参考终值标 $1.0$，纵轴原点标 $0$）给出各项指标：

- **超调量**（标注"超调量"）：响应曲线的峰值高出终值 $1.0$ 的那一段，图中用竖直双箭头标出，箭头从峰值水平线量到 $1.0$ 的参考线；
- **误差带**（标注"误差带"）：在 $1.0$ 附近画出的两条水平虚线所夹的带状区域；
- **稳态误差**（标注"稳态误差 $ (t \to \infty) $ "）：响应终了时与参考值 $1.0$ 之间的差，图中用竖直箭头量出；
- **上升时间 $t_r$**（标注"上升时间 $t_r$"）：从 $t=0$ 到响应曲线首次到达 $1.0$ 参考线的水平距离，图中用水平双箭头标出；
- **峰值时间 $t_p$**（标注"峰值时间 $t_p$"）：从 $t=0$ 到响应曲线到达峰值的水平距离；
- **调节时间 $t_s$**（标注"调节时间 $t_s$"）：从 $t=0$ 到响应曲线进入并（此后一直）保持在误差带内的水平距离，图中在进入误差带处画有竖直虚线作为终点。

曲线走向：从 $C(0)=0$ 上升，越过 $1.0$ 后到达峰值（峰值高于 $1.0$），随后下降并穿越 $1.0$，出现一次低于 $1.0$ 的下凹，再次上升并穿越 $1.0$，此后在 $1.0$ 附近做幅度很小的起伏，终了时的稳态值略低于 $1.0$ 参考线。

**理解**：
- 六项指标中，$t_r$、$t_p$、$t_s$ 都是时间量，都以 $t=0$ 为起点，区别只在终点取在哪里：$t_r$ 取首次到达参考值处，$t_p$ 取峰值处，$t_s$ 取进入并保持于误差带处。
- "误差带"是一对以参考值为中心的容许范围，$t_s$ 的终点取"最后一次离开误差带之后不再出去"的时刻，因此 $t_s$ 的判定必须看此后所有的采样点。
- "超调量"是峰值相对终值的百分比，是相对量；"稳态误差"是终了值相对参考值的差，是绝对量。两者测量的是不同时刻的不同对象：前者测峰值，后者测 $t\to\infty$ 的极限。
- 图上把误差带画在参考值 $1.0$ 的两侧，而稳态误差用箭头标在曲线终了位置与 $1.0$ 之间，说明"是否落在误差带内"与"稳态误差是否为零"是两个独立的判断：一个系统可以稳态误差不为零而响应最终落在误差带内，也可以稳态误差为零但收敛很慢（$t_s$ 很大）。

**作用**：这是 7.6.2 与 7.6.3 共用的指标定义页。7.6.2 的例题（第6、7页）取 $\sigma\%$ 与 $t_s$ 两项，7.6.3（第16页起）集中讨论稳态误差。与知识点 2、5 是"目标"与"方法"的关系；与知识点 7、8 是"指标"与"稳态误差求取"的关系。

---

---

### 知识点 7：稳态误差的一般求取途径、误差脉冲传递函数与终值定理

**定义**：课件把 7.6.3 节的稳态误差求取分为三种途径，其中前两种在本知识点中给出。

**途径一（课件第16页）：1. General method to obtain steady-state error**（一般方法）。做法是先按 7.6.2 的一般算法求出系统的输出响应序列，再按定义在序列上读取稳态误差。该页原题为"Example Consider the system shown in the figure, T=K=1. Obtain the dynamic specifications. ($\sigma\%$, $t_s$)"，并给出与第8页相同的对比曲线图。

**途径二（课件第18页）：2. Using final value theorem to obtain steady-state error**（用终值定理求取稳态误差）。第18页先作定义：设

$$
GH(z) = Z\left[G(s)H(s)\right] = \frac{1}{(z-1)^{v}}GH_0(z), \qquad \lim_{z\to 1}GH_0(z) = K
$$

其中 $v$ 标注为 **System type**（系统型别），$GH_0(z)$ 为把 $GH(z)$ 中全部 $(z-1)$ 因子提出之后剩下的部分，$K$ 为 $GH_0(z)$ 在 $z\to1$ 处的极限。

算法（Algorithm）：

1. **Determine the stability**（先判定稳定性）；
2. **Obtain the impulse transfer function from $E(z)$ to $R(z)$**（求从 $E(z)$ 到 $R(z)$ 的脉冲传递函数）：

$$
\Phi_e(z) = \frac{E(z)}{R(z)} = \frac{1}{1+GH(z)}
$$

3. **Obtain $e(\infty)$ by the final value theorem**（用终值定理求 $e(\infty)$）：

$$
e(\infty) = \lim_{z\to 1}(z-1)\Phi_e(z)R(z)
= \lim_{z\to 1}(z-1)\cdot R(z)\cdot\frac{1}{1+GH(z)}
$$

第18页右侧的系统结构为：$r$ 与反馈在相加点比较（$\otimes$），偏差 $e$ 采样得到 $e^{*}$ 后送入 $G(s)$，输出 $c$ 采样得到 $c^{*}$，反馈通路为 $H(s)$；括号标出 $\Phi(z)$ 覆盖 $r\to c$、$\Phi_e(z)$ 覆盖 $r\to e^{*}$、$G(z)$ 覆盖 $e^{*}\to c$。

课件第21页（静态误差常数法开头）重复给出了上述 $\Phi_e(z)$ 与 $e(\infty)$ 的表达式，并在第28页（7.6.3 小结）把本途径列为第 (2) 种方法，列出三个要素：

$$
\text{(2) Final value theorem}\quad
\begin{cases}
G(z) \to \Phi_e(z)\\
D(z) \to \text{Stability}\\
e(\infty)=\lim\limits_{z\to1}(z-1)R(z)\Phi_e(z)
\end{cases}
$$

式中 $D(z)$ 为闭环离散系统的特征多项式（闭环脉冲传递函数的分母），$R(z)$ 为输入信号的 Z 变换。

**理解**：
- 终值定理把"求 $t\to\infty$ 的极限值"换成"求 $z\to1$ 的极限值"，从而不需要求出响应序列的每一项。使用的条件是 $z\Phi_e(z)R(z)$ 的极点全部位于单位圆内（即闭环稳定、且 $R(z)$ 引入的极点已被 $(z-1)$ 消去）。这就是算法第 (1) 步必须先判稳、第28页把 $D(z)\to\text{Stability}$ 单列一行、第21页适用条件先写 "For stable linear discrete systems" 的原因：不稳定系统的响应不收敛，终值定理不适用。
- $\Phi_e(z)=1/(1+GH(z))$ 是关于误差的脉冲传递函数。它的分母 $1+GH(z)=0$ 就是闭环特征方程，与 $\Phi(z)$ 的分母相同，所以判稳只需判一次。
- $e(\infty)$ 的表达式里，$R(z)$ 由输入形式决定，$1/(1+GH(z))$ 由系统结构决定，$(z-1)$ 因子来自终值定理。三者的乘积取 $z\to1$ 的极限即得稳态误差。误差是否为零，取决于 $(z-1)$ 与 $1+GH(z)$ 在 $z=1$ 处的零点、极点相消情况，这正是"系统型别 $v$"起作用的地方。
- 课件把 $GH(z)$ 统一写成 $\frac{1}{(z-1)^{v}}GH_0(z)$ 的形式，目的是把"在 $z=1$ 处的极点个数"这一影响稳态误差的唯一结构特征单独提出来，其余部分归入 $GH_0(z)$。于是 $v$ 相同、$K$ 相同的系统，稳态误差表达式完全相同。
- 第28页给出的三要素之间次序不可交换：先由 $G(z)$ 求出 $\Phi_e(z)$，再判断稳定性，最后才允许取极限。
- 本途径与"一般方法"的差别在于：一般方法要真正解出 $e(kT)$ 的序列（用 Z 反变换或长除法）再取 $k\to\infty$，本途径只在 $z$ 域内取一次极限，不需要反变换。本途径对任意形式的 $R(z)$ 都适用，不限于阶跃、斜坡、加速度三类标准输入。

**作用**：这是 7.6.3 节的方法主体，也是第三种途径（静态误差常数法）的出发点：把 $R(z)$ 按输入类型代入本式取极限，即得第22页的三个误差常数定义。它把稳态误差的计算归结为三步：判稳、写 $\Phi_e(z)$、代入 $R(z)$ 取极限。与知识点 6 是"指标定义"与"指标计算"的关系；与知识点 8 是"方法"与"型别分类"的关系；与知识点 9–15（静态误差常数法）是"一般式"与"分类结论表"的关系。

---

### 知识点 8：系统型别 $v$、$GH_0(z)$ 与常数 $K$

**定义**：课件第18页与第21页给出同一组定义式

$$
GH(z) = Z\left[G(s)H(s)\right] = \frac{1}{(z-1)^{v}}GH_0(z), \qquad
\lim_{z\to 1}GH_0(z) = K
$$

并标注 $v$ 为 **System type**（系统型别），$K$ 为 $GH_0(z)$ 在 $z\to1$ 处的极限值。

课件第23页给出型别的判别依据（原文）：

> Similar to the continuous system, we can divide the discrete-time system as type 0, type I, type II,… according to the numbers of the pole $z=1$ of the impulse transfer function.

即：与连续系统类似，根据脉冲传递函数中 $z=1$ 极点的个数，把离散时间系统划分为 0 型、I 型、II 型……

在课件第19页的例题中，$G(z)=\dfrac{K(1-e^{-T})z}{(z-1)(z-e^{-T})}$，图中用红色标出 $v=1$，即该系统的开环脉冲传递函数在 $z=1$ 处有一个极点，故为一型系统；此时 $GH_0(z)=\dfrac{K(1-e^{-T})z}{z-e^{-T}}$，$\lim_{z\to1}GH_0(z)=K$。

**理解**：
- $v$ 的定义是"$GH(z)$ 中因子 $(z-1)$ 的重数"，即开环脉冲传递函数在 $z=1$ 处的极点个数。这个数只能取非负整数，$v=0$ 称为 0 型，$v=1$ 称为一型（type I），$v=2$ 称为二型。
- 型别只统计 $z=1$ 这一个点上的极点，其他位置的极点（例如 $z=-0.5$、$z=e^{-T}$）不计入型别。
- 型别是**开环**脉冲传递函数 $GH(z)$ 的性质，不是闭环传递函数的性质。闭环的稳定性由 $D(z)$ 的根是否全在单位圆内决定，与型别是两件独立的事：一个系统可以既有 $v=1$ 又是不稳定的。
- $K$ 是把 $(z-1)^v$ 提出之后剩余部分在 $z=1$ 处的取值。这一步是为了让 $K$ 不含 $(z-1)$ 引起的无穷大或零，从而成为一个有限非零的表征开环增益的量：因为 $\lim_{z\to1}GH_0(z)=K$ 有限非零，$GH_0(z)$ 在 $z=1$ 处解析且不为零，所以 $(z-1)^v$ 的全部幂次都来自 $GH(z)$ 在 $z=1$ 的极点。
- $v$ 与 $K$ 的取法保证 $\lim_{z\to1}(z-1)^vGH(z)=K$。在计算 $e(\infty)$ 时，$(z-1)^v$ 与输入 $R(z)$ 带来的 $(z-1)$ 因子相消，$v$ 越大则越容易被完全消去，从而稳态误差为零；$v$ 不足时 $(z-1)$ 残留在分母上，极限为无穷大。
- 型别与连续系统"积分环节个数"的对应关系：$z=1$ 极点对应连续域中 $s=0$ 极点，即积分环节 $1/s$。$v$ 的数值等于开环通路中积分环节的个数（在采样后体现为 $z=1$ 处极点的重数）。
- 第20页的例题正是按此分类得到结果：$r_1(t)=1(t)$ 时 $e_1(\infty)=0$，$r_2(t)=t$ 时 $e_2(\infty)=T/K$（有限），$r_3(t)=t^2/2$ 时 $e_3(\infty)=\infty$。三个结果依次对应"$v$ 足够、$v$ 恰好、$v$ 不足"三种情形，输入每提高一阶，所需的 $v$ 就多一个。

**作用**：这是知识点 7 中公式的结构说明，也是静态误差常数法的分类索引。$v$ 一旦确定，即可在第25页的总表中定位到该型别所在的行，读出三个误差常数中哪一个是有限非零值、哪两个为 0 或 $\infty$，从而判断该型别系统对阶跃、斜坡、加速度三类输入分别能否实现零稳态误差。与本课件第19、20页的例题以及第26、27页的例题直接相连，是这些例题求解的判断依据。

---

### 知识点 9：静态误差常数法（Static Error Constant Method）

**定义**：课件第 21 页给出该方法的名称与定位：

- 标题：**3. Static Error Constant Method**（静态误差常数法）；
- 功能说明：**shows how e(∞) changes with r(t)**（说明 e(∞) 如何随 r(t) 变化）；
- 适用条件（原文）：**(For stable linear discrete systems subject to r(t) and sampled at the error signal)**，即：适用于稳定的线性离散系统，参考输入为 r(t)，且采样发生在误差信号处；
- 方法的前置分解（"Let" 之后的方程组）：

$$
\begin{cases}
GH(z) = Z[G(s)H(s)] = \dfrac{1}{(z-1)^{\nu}}GH_0(z)\\[2mm]
\lim\limits_{z\to1}GH_0(z) = K
\end{cases}
\qquad \nu:\ \text{System type（系统型别）}
$$

- 误差脉冲传递函数与稳态误差极限式：

$$
\Phi_e(z) = \frac{E(z)}{R(z)} = \frac{1}{1+GH(z)}
$$

$$
e(\infty) = \lim_{z\to1}(z-1)\Phi_e(z)R(z) = \lim_{z\to1}(z-1)\cdot R(z)\cdot \frac{1}{1+GH(z)}
$$

式中：$G(s)$ 为前向通路传递函数，$H(s)$ 为反馈通路传递函数，$GH(z) = Z[G(s)H(s)]$ 为开环脉冲传递函数，$\nu$ 为系统型别，$GH_0(z)$ 为提出 $z=1$ 极点后的剩余部分，$K$ 为 $GH_0(z)$ 在 $z\to1$ 时的极限值，$E(z)$、$R(z)$ 分别为误差信号与参考输入的 Z 变换，$T$ 为采样周期。

**理解**：
- 这一方法的要素有三项：输入信号 $r(t)$ 的类型、系统型别 $\nu$、三个静态误差常数（$K_p$、$K_v$、$K_a$）。三者确定后，稳态误差由一条不含极限运算的代数式直接给出。
- 采用这一方法的原因在于：把 $R(z)$ 与 $\Phi_e(z)$ 直接代入 $e(\infty)=\lim_{z\to1}(z-1)R(z)/(1+GH(z))$ 时，分子与分母在 $z\to1$ 处同时趋于零（对阶跃、斜坡、加速度这些输入，$R(z)$ 含 $(z-1)$ 的负幂次，而 $1+GH(z)$ 在 $z=1$ 处为无穷），必须比较两者在 $z\to1$ 处趋于零的阶数，极限才有非零有限值。把 $GH(z)$ 在 $z=1$ 处的极点重数单独提出，写成 $GH(z)=GH_0(z)/(z-1)^{\nu}$ 且 $\lim GH_0(z)=K\ne0$，就可以把"趋于零的阶数比较"转化为一个确定的分母 $(z-1)^{\nu}$ 与一个确定的分子的比较。
- $\nu$ 的作用是记录 $GH(z)$ 在 $z=1$ 处的极点重数；输入的阶数（阶跃为 0 阶，斜坡为 1 阶，加速度为 2 阶）与 $\nu$ 相等时，稳态误差为有限非零常数；$\nu$ 大于输入阶数时，$e(\infty)=0$；$\nu$ 小于输入阶数时，$e(\infty)=\infty$。
- 第 21 页标题编号为 "3."，而第 28 页把三种方法编号为 (1)(2)(3)，两处编号一致：静态误差常数法是 7.6.3 节的第三种方法，前两种（一般方法、终值定理法）在课件第 20 页及其之前。

**作用**：这是 7.6.3 节的收口方法。前两种方法（求系统响应、终值定理）都要处理 $R(z)$ 与 $\Phi_e(z)$ 的完整表达式，本方法把结论固化成"输入类型—系统型别—误差常数"的对应表（第 25 页），在已知 $GH(z)$ 时只需计算一次 $z\to1$ 的极限。在工程上它用于两件事：由系统的型别预判能否跟踪某类输入；由稳态误差指标反求开环增益的取值范围（第 27 页例题）。

---

---

### 知识点 10：静态位置误差常数 K_p（Static Position Error Constant）

**定义**：对应输入 $r(t)=A\cdot 1(t)$。课件第 22 页给出完整推导链

$$
e(\infty T) = \lim_{z\to1}(z-1)\cdot\frac{Az}{z-1}\cdot\frac{1}{1+GH(z)}
= \frac{A}{1+\lim\limits_{z\to1}GH(z)}
= \frac{A}{K_p}
$$

并定义（课件第 22、23 页，两处写法一致）

$$
\boxed{K_p = 1+\lim_{z\to1}GH(z)}
$$

第 22 页右侧浅绿方框给出结论式：

$$
= \frac{A}{K_p}
$$

第 23 页给出型别结论：

- **Type 0：$K_p$=constant**（0 型系统 $K_p$ 为有限常数）
- **Type $\ge$ 1：$K_p=\infty$，$e(\infty)=0$**（I 型及以上系统 $K_p$ 为无穷大，稳态误差为零）

**理解**：
- 本课件把常数项 1 并入了位置误差常数的定义：$K_p=1+\lim_{z\to1}GH(z)$。这与多数教材的写法不同（教材通常定义 $K_p=\lim_{z\to1}GH(z)$，并把 $e(\infty)$ 写成 $A/(1+K_p)$）。差别的直接后果有四点：
  1. **数值不同**：对 0 型系统，课件定义的 $K_p$ 比教材定义的 $K_p$ 大 1。
  2. **公式形式不同**：课件写成 $e(\infty)=A/K_p$，分母中不含单独的 "1+"，因为 1 已经被吸收进 $K_p$；教材写成 $e(\infty)=A/(1+K_p)$。
  3. **代入时不可混用**：若用教材定义的 $K_p=\lim_{z\to1}GH(z)$ 去套课件的 $A/K_p$，会把结果算大；若用课件的 $K_p$ 去套教材的 $A/(1+K_p)$，会把结果算小。两种定义下算出的 $e(\infty)$ 数值相同，但必须先统一口径。
  4. **对 $\nu\ge1$ 的系统两者一致**：此时 $\lim_{z\to1}GH(z)=\infty$，两个定义都给出 $K_p=\infty$，$e(\infty)=0$，加上常数 1 不改变结果。
- 定义的直接含义：$K_p$ 对 0 型系统是一个有限正数，其大小由开环脉冲传递函数在 $z=1$ 处的取值决定；$\nu\ge1$ 时该取值发散，故 $K_p=\infty$、稳态误差为 0。
- "Position"（位置）一词的来源是：$r(t)=A\cdot1(t)$ 是位置恒定的输入（阶跃），误差常数描述系统跟随位置给定值的精度。

**作用**：它是三个误差常数中唯一含常数项 1 的一个，也是唯一在 $\nu=0$（无积分环节）时取有限值的常数。在总表（第 25 页）中，它对应"阶跃输入"这一列，决定 0 型系统对阶跃输入是否存在稳态误差。

---

### 知识点 11：静态速度误差常数 K_v（Static Velocity Error Constant）

**定义**：对应输入 $r(t)=A\cdot t$。课件第 22 页给出推导链

$$
e(\infty T) = \lim_{z\to1}(z-1)\cdot\frac{ATz}{(z-1)^2}\cdot\frac{1}{1+GH(z)}
= \frac{AT}{\lim\limits_{z\to1}(z-1)GH(z)}
= \frac{AT}{K_v}
$$

并定义（课件第 22、23 页一致）

$$
\boxed{K_v = \lim_{z\to1}(z-1)GH(z)}
$$

第 22 页右侧浅绿方框给出结论式：

$$
= \frac{AT}{K_v}
$$

第 23 页给出型别结论：

- **Type 0：$K_v=0$，$e(\infty)=\infty$**
- **Type = 1：$K_v$= constant**（I 型系统 $K_v$ 为有限常数）
- **Type $\ge$ 2：$K_v=\infty$，$e(\infty)=0$**

**理解**：
- 与 $K_p$ 不同，$K_v$ 的定义中不含常数项 1，课件与教材在这一点上写法一致。
- 定义中乘上的因子 $(z-1)$ 起"扣除一个 $z=1$ 极点"的作用：$\nu=0$ 时 $GH(z)$ 在 $z=1$ 处不为零，乘积趋于 0，故 $K_v=0$，$e(\infty)=\infty$（0 型系统无法跟踪斜坡输入）；$\nu=1$ 时乘积的极限为有限非零值，$K_v$ 为常数；$\nu\ge2$ 时乘积仍含 $(z-1)$ 的正幂，趋于 $\infty$。
- 分子中出现 $T$ 的原因：斜坡信号的 Z 变换为 $Z[A t]=ATz/(z-1)^2$，采样周期 $T$ 由 Z 变换带入，最终结果 $e(\infty T)=AT/K_v$ 中含 $T$。
- "Velocity"（速度）一词的来源是：$r(t)=At$ 是位置随时间线性变化的输入，其变化率（速度）为常数 $A$，误差常数描述系统跟随恒定速度输入的精度。注意 $A$ 是斜坡的**斜率**（速度），不是幅值。

**作用**：它决定 I 型系统的稳态精度，是工程中最常被指定的指标（"速度误差系数不小于某值"）。第 26、27 页两道例题全部落在 $\nu=1$ 的情形，都用 $K_v$ 计算，说明这一常数在本节的实际地位。

---

### 知识点 12：静态加速度误差常数 K_a（Static Acceleration Error Constant）

**定义**：对应输入 $r(t)=\dfrac{A}{2}t^2$。课件第 22 页给出推导链

$$
e(\infty T) = \lim_{z\to1}(z-1)\cdot\frac{AT^2z(z+1)}{2(z-1)^3}\cdot\frac{1}{1+GH(z)}
= \frac{AT^2}{\lim\limits_{z\to1}(z-1)^2GH(z)}
= \frac{AT^2}{K_a}
$$

并定义（课件第 22、24 页一致）

$$
\boxed{K_a = \lim_{z\to1}(z-1)^2GH(z)}
$$

第 22 页右侧浅绿方框给出结论式：

$$
= \frac{AT^2}{K_a}
$$

第 24 页给出型别结论：

- **Type 0, 1：$K_a=0$，$e(\infty)=\infty$**
- **Type = 2：$K_a$= constant**（II 型系统 $K_a$ 为有限常数）
- **Type $\ge$ 3：$K_a=\infty$，$e(\infty)=0$**

**理解**：
- 定义中乘上的因子是 $(z-1)^2$，比 $K_v$ 的定义多扣一个 $z=1$ 极点，因此只有 $\nu\ge2$ 时极限才可能为有限非零值。
- 输入 $r(t)=\frac{A}{2}t^2$ 的二阶导数为常数 $A$，故 $A$ 是加速度值；这也是分母中保留系数 $\frac{1}{2}$、而误差公式中不含 $\frac{1}{2}$ 的原因（该系数在求导定义 $A=\ddot r$ 时被抵消）。
- 分子中 $T^2$ 的来源：$Z\left[\frac{A}{2}t^2\right]=\frac{AT^2z(z+1)}{2(z-1)^3}$，两个 $T$ 由 Z 变换带入。
- 三个常数对 $T$ 的依赖程度不同：$K_p$ 的定义中不含 $T$；$K_v$ 对应的误差公式含 $T$ 的一次幂；$K_a$ 对应的误差公式含 $T$ 的二次幂。误差公式中 $T$ 的幂次等于输入信号的阶数。

**作用**：它决定 II 型系统的稳态精度，在随动系统中对应"等加速跟踪"指标。与 $K_p$、$K_v$ 一起构成三个误差常数的完整集合，并在第 25 页总表中占据第 3 列。

---

### 知识点 13：型别—误差常数—稳态误差总表（第 25 页）

**定义**：课件第 25 页用一张表（中文列头"型别"，英文列头 "Static Error Constant" 与 "Steady-State Error"）汇总结论；右上角浅绿方框重复给出 $GH(z)$ 的规范分解。表格完整内容如下（型别行 $\nu$ 为定义行，其余三行为结论值）：

| 型别 $\nu$ | $K_p$ | $K_v$ | $K_a$ | $r=A\cdot1(t)$：$e(\infty)=\dfrac{A}{K_p}$ | $r=A\cdot t$：$e(\infty)=\dfrac{AT}{K_v}$ | $r=A\cdot t^2/2$：$e(\infty)=\dfrac{AT^2}{K_a}$ |
|---|---|---|---|---|---|---|
| **$\nu$（定义行）** | $K_p=\lim GH(z)$ | $K_v=\lim(z-1)GH(z)$ | $K_a=\lim(z-1)^2GH(z)$ | $\dfrac{A}{K_p}$ | $\dfrac{AT}{K_v}$ | $\dfrac{AT^2}{K_a}$ |
| **0** | $K_p$ | $0$ | $0$ | $\dfrac{A}{K_p}$ | $\infty$ | $\infty$ |
| **I** | $\infty$ | $K_v$ | $0$ | $0$ | $\dfrac{AT}{K_v}$ | $\infty$ |
| **II** | $\infty$ | $\infty$ | $K_a$ | $0$ | $0$ | $\dfrac{AT^2}{K_a}$ |

（表中极限记号均省略下标 $z\to1$；定义行三式中 $K_p=\lim GH(z)$ 系课件原样，与第 22、23 页的 $K_p=1+\lim GH(z)$ 不一致，见"补充知识点总结"。）

右上角绿框：

$$
\begin{cases}
GH(z)=\dfrac{1}{(z-1)^{\nu}}GH_0(z)\\[2mm]
\lim\limits_{z\to1}GH_0(z)=K
\end{cases}
$$

**理解**：
- 读表方式是沿对角线：型别 $\nu$ 等于输入阶数时，稳态误差为有限非零值（表格对角线上 0 型—阶跃 $A/K_p$、I 型—斜坡 $AT/K_v$、II 型—加速度 $AT^2/K_a$ 三格）；型别高于输入阶数时（对角线上方），稳态误差为 0；型别低于输入阶数时（对角线下方），稳态误差为 $\infty$。
- 表格中三个误差常数格子的规律：0 型行的 $K_v=0$、$K_a=0$；I 型行的 $K_p=\infty$、$K_a=0$；II 型行的 $K_p=\infty$、$K_v=\infty$。即"$K_p$ 只对 0 型有限，$K_v$ 只对 I 型有限，$K_a$ 只对 II 型有限"。
- 表中稳态误差列与误差常数列的对应关系是固定的三条式子：阶跃配 $K_p$、斜坡配 $K_v$、加速度配 $K_a$，三者的分子依次为 $A$、$AT$、$AT^2$。

**作用**：这是整个静态误差常数法（知识点 9–12）的结论汇总，也是后续解题（第 26、27 页例题）时唯一需要查的表。它把"求 $e(\infty)$"转化为"先定 $\nu$，再定输入类型，最后查一处格子"。

---

---

### 知识点 14：ZOH 对离散系统稳态误差的影响（第 26 页例题结论）

**定义**：课件第 26 页对同一被控对象 $\dfrac{K}{s(s+1)}$、同一采样周期 $T$、同一输入 $r(t)=2t$（即 $A=2$），分别计算无 ZOH 与有 ZOH 两种结构下的稳态误差：

$$
\text{no ZOH：}\quad e(\infty)=\frac{AT}{K_v}=\frac{2T}{K}\quad\text{（— dependent of T）}
$$

$$
\text{with ZOH：}\quad e(\infty)=\frac{AT}{K_v}=\frac{A}{K}=\frac{2}{K}\quad\text{（— independent of T）}
$$

**理解**：
- 两组结果中 $K_v$ 的数值不同是全部差别的来源：无 ZOH 时 $K_v=K$，有 ZOH 时 $K_v=KT$。分母中的 $K_v$ 与分子中的 $AT$ 恰好把 $T$ 约掉（$AT/(KT)=A/K$），因此有 ZOH 的 $e(\infty)$ 不含 $T$；无 ZOH 时 $AT/K$ 中 $T$ 保留，故 $e(\infty)$ 随 $T$ 变化。
- 这一差别只在被控对象 $G(s)$ 含有积分环节（本例为 $1/s$）时出现，因为零阶保持器在 $z$ 域引入因子 $(1-z^{-1})$，它与 $s$ 域积分环节的采样结果共同决定 $z=1$ 处极点的结构与 $K_v$ 的取值。
- 结论的直接含义：加入零阶保持器后，I 型系统对斜坡输入的稳态误差只由开环增益 $K$ 决定，采样周期 $T$ 的变化（在保持稳定性的前提下）不改变该误差。反过来，无 ZOH 时减小 $T$ 会减小稳态误差。

**作用**：这是静态误差常数法的一个应用性结论，说明"$K_v$ 的数值依赖于前向通路的实际结构（是否含 ZOH）"，而这一点在查第 25 页的总表时不会体现（总表只按型别分类）。因此使用总表前必须先求出与真实结构对应的 $GH(z)$。

---

---

### 知识点 15：稳态误差的三种求法（7.6.3 小结，第 28 页）

**定义**：课件第 28 页以标题 **7.6.3 Steady-state error of discrete systems** 给出三种求法：

$$
\text{(1) General method: obtain system response（一般方法：求取系统响应）}
$$

$$
\text{(2) Final value theorem}\quad
\begin{cases}
G(z) \to \Phi_e(z)\\
D(z) \to \text{Stability}\\
e(\infty)=\lim\limits_{z\to1}(z-1)R(z)\Phi_e(z)
\end{cases}
$$

$$
\text{(3) Static error constant}\quad
\begin{cases}
G(z) \to \nu,\ K_p,\ K_v,\ K_a\\
\text{Obtain } e(\infty)
\end{cases}
$$

**理解**：
- 三种方法的输入量与产出量不同。方法 (1) 直接求 $c(kT)$ 或 $e(kT)$ 的时间序列（用 Z 反变换），取 $k\to\infty$ 的极限，得到 $e(\infty)$；方法 (2) 在 $z$ 域内用终值定理取极限，不需要反变换；方法 (3) 只用到 $GH(z)$ 在 $z=1$ 附近的局部信息（型别与三个极限值），连 $\Phi_e(z)$ 的完整表达式都不需要写出。
- 三者的适用性依次收窄、计算量依次减小：方法 (1) 适合表格给出的数值序列或难以解析求解的情形；方法 (2) 适合任意 $R(z)$；方法 (3) 只适合阶跃、斜坡、加速度这三类标准输入，且要求 $GH(z)$ 能按 $z=1$ 极点重数分解。
- 方法 (2) 中的 $D(z)\to\text{Stability}$ 是不可省略的一步：只有当 $D(z)$ 的根全部位于 $z$ 平面单位圆内时，终值定理才给出有限的 $e(\infty)$。

**作用**：这是 7.6.3 节的总纲，用于说明"本节给出了三条路径而非一条"。它同时给出了各方法的输入—输出关系（$G(z)\to\Phi_e(z)$、$D(z)\to\text{Stability}$、$G(z)\to\nu,K_p,K_v,K_a$），便于在解题时按已知条件选择方法。

---

---

## 补充知识点总结

> 本节按页码范围分栏列出，两栏各自保持原有编号。第一栏对应课件第 1–20 页，第二栏对应课件第 21–28 页。

### 补充条目（课件第 1–20 页）

**1. 课件第1页（章节总目录）**：Chapter 7 的七个小节标题如下（7.6 为红色高亮）
7.1 Introduction；7.2 The Sampling Process and Sampling Theorem；7.3 Signal Recovery and Zero-Order Hold；7.4 Z-Transform and Inverse Z Transform；7.5 Mathematical Models of Discrete-Time Systems；**7.6 Performance Analysis of Discrete-Time Systems**；7.7 Digital Control Design for Discrete-Time Systems。

**2. 课件第2页（7.6 节的三条任务）**：
- s-Domain to z-Domain Mapping
- Necessary and Sufficient Condition for Stability of Linear Discrete-Time Systems —— All poles of $\Phi(z)$ lie in the unit circle of $z$ plane
- Routh criterion in w domain (Generalized Routh Criterion)

**3. 课件第3页（三种方法总览图）的完整标注**：
- 红色文字："we've learned three methods to determine the stability of a discrete-time systems."
- [s] 平面：横轴 $\sigma$，纵轴 $j\omega$，原点 $0$；紧贴 $j\omega$ 轴左侧的竖直阴影带标注"稳定区"，$j\omega$ 轴右侧标注"不稳定区"；阴影带顶部有一个 $\otimes$ 记号。
- 映射公式 $z=e^{sT}$，居中大号字，配绿色右向箭头。
- [z] 平面：横轴 Re，纵轴 Im，横轴标 $-1$、$0$、$1$；单位圆内标注"稳定区"，圆外标注"不稳定区"；紧贴单位圆内侧有斜线阴影带。
- [w] 平面：横轴 $u$，纵轴 $j\upsilon$，原点 $0$；紧贴 $j\upsilon$ 轴左侧的竖直阴影带（左半平面）。
- 映射公式 $w=\dfrac{z+1}{z-1}$，配绿色弧形箭头（由 [z] 平面指向 [w] 平面）。

**4. 课件第4页与第15页（7.6 节目录页，两次出现）**：条目为 Stability、Dynamic Performance、Steady-state Errors；第4页中 **Dynamic Performance** 为红色（进入 7.6.2），第15页中 **Steady-state Errors** 为红色（进入 7.6.3）。

**5. 课件第5页的完整公式组**：
- $GH(z)=Z[G(s)H(s)]$
- $\Phi(z)=\dfrac{G(z)}{1+GH(z)}=\dfrac{M(z)}{D(z)}$
- $C(z)=\Phi(z)R(z)=\dfrac{M(z)}{D(z)}\cdot\dfrac{z}{z-1}=c(0)+c(T)z^{-1}+c(2T)z^{-2}+\cdots$
- $c^{*}(t)=c(0)\delta(t)+c(T)\delta(t-T)+c(2T)\delta(t-2T)+\cdots$
- (4) Determine the specifications $\sigma\%$、$t_s$

**6. 课件第8页（对比曲线图）的完整信息**：
- 纵轴 $h^{*}(t)$，刻度 $0$、$0.2$、$0.4$、$0.6$、$0.8$、$1.0$、$1.2$、$1.4$；横轴 $t$，刻度 $0$、$5$、$10$、$15$、$20$、$25$。
- 图例：蓝色圆点＝"有 ZOH 时"；红色圆点＝"无 ZOH 时"；黑色实线＝"连续系统"。
- 在 $h^{*}=1.0$ 两侧画出两条青色水平线，右侧标注"$5\%$"，即 $\pm5\%$ 误差带。
- 曲线走向：连续系统曲线从 $0$ 上升，峰值约 $1.16$ 出现在 $t\approx3.7$，随后下降到约 $0.97$ 并逐渐回到 $1.0$；无 ZOH 的采样点在第 3 个采样时刻达到峰值 $1.207$（红色，虚线竖线标 $t_p$），第 5 个采样时刻起进入 $\pm5\%$ 带（红色虚线竖线标 $t_s$）；有 ZOH 的采样点在第 4 个采样时刻达到峰值 $1.3996$（蓝色，蓝色虚线竖线标 $t_p$），第 12 个采样时刻起进入 $\pm5\%$ 带（蓝色虚线竖线标 $t_s$，位于 $t\approx12$）。
- 图内数据表（三行）：

| 类别 | $t_p$ | $\sigma\%$ | $t_s$ |
|---|---|---|---|
| 有 ZOH 时（蓝） | 4T | 40.0% | 12T |
| 无 ZOH 时（红） | 3T | 20.7% | 5T |
| 连续系统（黑） | 3.7s | 16.3% | 5.3s |

**7. 课件第9页的重要记号**：$\Phi(z)=\dfrac{M(z)}{D(z)}=\dfrac{b_m}{a_n}\dfrac{\prod_{i=1}^{m}(z-z_i)}{\prod_{k=1}^{n}(z-p_k)}$（$m\le n$）；$C(z)=\dfrac{M(1)}{D(1)}\cdot\dfrac{z}{z-1}+\sum\limits_{k=1}^{n}\dfrac{c_k z}{z-p_k}$；$c_k^{*}(t)=Z^{-1}\left[\dfrac{c_k z}{z-p_k}\right]$，$k=1,2,\cdots,n$；$c_k(nT)=c_k p_k^{n}$，$k=1,2,\cdots,n$。标题为"2. Relationship between dynamic response and closed-loop poles"，子标题为"(1) Single closed-loop poles on the real axis"。

**8. 课件第10页的文字**：$c_k(nT)=c_k p_k^{n}$，$k=1,2,\cdots,n$；**$p_k>0$**：$p_k>1$、$p_k=1$、$p_k<1$ 三种；**$p_k<0$**：（对应 $p_k<-1$、$p_k=-1$、$-1<p_k<0$ 三种，由该页 z 平面图上的 $\times$ 位置给出）。

**9. 课件第12页的公式补充**：$c_{k,k}(nT)=c_k p_k^{n}+\bar{c}_k\bar{p}_k^{\,n}=|c_k|e^{j\varphi_k}e^{(a+j\omega)nT}+|c_k|e^{-j\varphi_k}e^{(a-j\omega)nT}=2|c_k|e^{anT}\cos(n\omega T+\varphi_k)$；$a=\dfrac{1}{T}\ln|p_k|$，$\omega=\dfrac{\theta_k}{T}$，$0<\theta_k<\pi$；$p_k=|p_k|e^{j\theta_k}$，$\bar{p}_k=|p_k|e^{-j\theta_k}$。

**10. 课件第13页图上的文字**：标题"z 平面"；左上角文字 $|p_k|<1,\ |p_k|>1$；四组波形标注 $\theta_k=90^\circ,|p_k|<1$；$\theta_k=45^\circ,|p_k|<1$；$\theta_k=135^\circ,|p_k|=1$；$\theta_k=-45^\circ,|p_k|>1$。

**11. 课件第14页的小结文字**：
- (1) General method：$G(z)\rightarrow\Phi(z)\longrightarrow C(z)=\sum\limits_{n=0}^{\infty}c(nT)z^{-n}$，$c^{*}(t)=\sum\limits_{n=0}^{\infty}c(nT)\delta(t-nT)\rightarrow$ Obtain $\sigma\%$, $t_s$ by definition；
- (2) Closed-loop poles $p_k\longrightarrow$ Response $c_k(nT)=C_k p_k^{n}$（课件此处系数记作大写 $C_k$）。

**12. 课件第16页的完整文字**：标题 7.6.3 Steady-state error；小标题"1. General method to obtain steady-state error"；例题文字为"Example Consider the system shown in the figure, T=K=1. Obtain the dynamic specifications. ($\sigma\%$, $t_s$)."（该页原题沿用了动态性能的说法）；右侧系统结构为 $r\to\otimes\to e\to$ 采样 $\to e^{*}\to\dfrac{K}{s(s+1)}\to c\to$ 采样 $\to c^{*}$，反馈直接回相加点（比较点前无 $H(s)$ 模块，此处为记号，实际含义为单位反馈）；左侧给出 $h(0)=0$、$h(1)=0.632$、$h(2)=1.097$、$h(3)=1.207$、$h(4)=1.117$、$h(5)=1.014$、$h(6)=0.964$、$h(7)=0.970$、$h(8)=0.991$、$h(9)=1.004$、$h(10)=1.007$、$h(11)=1.003$、$h(12)=1.000$、$\vdots$；右侧为第8页同样的对比曲线图与数据表。

**13. 课件第17页的全部标注**：C(t)（纵轴）、$1.0$、$0$、$t$（横轴）、超调量、误差带、稳态误差、$(t\to\infty)$、上升时间 $t_r$、峰值时间 $t_p$、调节时间 $t_s$、图题"控制系统性能指标"。

**14. 课件第18页的完整文字**：标题"2. Using final value theorem to obtain steady-state error"；Let 组的两个式子；"v: System type"（红色）；Algorithm 的三步；$\Phi_e(z)=\dfrac{E(z)}{R(z)}=\dfrac{1}{1+GH(z)}$；$e(\infty)=\lim\limits_{z\to1}(z-1)\Phi_e(z)R(z)=\lim\limits_{z\to1}(z-1)\cdot R(z)\cdot\dfrac{1}{1+GH(z)}$。

**15. 课件第20页的完整公式与约分过程**：$0<K<4.33$；$e(\infty)=\lim\limits_{z\to1}(z-1)R(z)\Phi_e(z)$；$\Phi_e(z)=\dfrac{(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}$；三行计算式中，图中用蓝色斜线划掉了分子与分母中相消的 $(z-1)$ 因子：
- $r_1(t)=1(t)$：$e_1(\infty)=\lim\limits_{z\to1}(z-1)\dfrac{z}{z-1}\cdot\dfrac{(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}=0$
- $r_2(t)=t$：$e_2(\infty)=\lim\limits_{z\to1}(z-1)\dfrac{Tz}{(z-1)^2}\cdot\dfrac{(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}=\dfrac{T}{K}$
- $r_3(t)=\dfrac{t^2}{2}$：$e_3(\infty)=\lim\limits_{z\to1}(z-1)\dfrac{Tz(z+1)}{2(z-1)^3}\cdot\dfrac{(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}=\infty$

**16. 记号约定（三个数学量的 Z 变换，课件第20页使用）**：$Z[1(t)]=\dfrac{z}{z-1}$；$Z[t]=\dfrac{Tz}{(z-1)^2}$；$Z\!\left[\dfrac{t^2}{2}\right]=\dfrac{Tz(z+1)}{2(z-1)^3}$。

---

### 补充条目（课件第 21–28 页）

1. **第 21 页系统结构框图（误差处采样）** 图中元素与连接关系如下：
   - 参考输入 $r$ 从左侧进入，经一个采样开关（用带虚线的开关符号表示）得到 $r^*$，$r^*$ 标注在采样开关下方；$r^*$ 送入相加点。
   - 相加点（$\otimes$）有两个输入：正端为 $r^*$，负端来自反馈通路（负号标在相加点下方边上）；相加点输出为误差信号 $e$。
   - $e$ 经第二个采样开关得到 $e^*$；$e^*$ 送入前向通路方框 $G(s)$。
   - $G(s)$ 的输出为 $c$；在 $G(s)$ 输出节点处再经第三个采样开关得到 $c^*$（图中 $c^*$ 标在上方、$c$ 标在下方）。
   - 反馈通路从 $G(s)$ 输出节点（连续信号 $c$ 处）引出，向下经方框 $H(s)$ 返回相加点的负端。
   - 图中画有三条标注弧：$\Phi(z)$ 从最左端（$r^*$ 处）跨到最右端（$c^*$ 处）；$\Phi_e(z)$ 从最左端跨到 $e^*$ 处；$G(z)$ 从 $e^*$ 处跨到最右端。因此 $\Phi(z)=C(z)/R(z)$，$\Phi_e(z)=E(z)/R(z)$，$G(z)$ 为 $e^*$ 到 $c^*$ 的前向脉冲传递函数。
   - 框图上方的适用条件文字与图一一对应："sampled at the error signal"（在误差信号处采样）即指误差通路上的那个采样开关。

2. **第 21 页正文三行文字（原文）**：
   - "3. Static Error Constant Method"
   - "shows how e(∞) changes with r(t)"
   - "(For stable linear discrete systems subject to r(t) and sampled at the error signal)"

3. **第 22 页顶部首式**：$e(\infty T)=\lim\limits_{z\to1}(z-1)\Phi_e(z)R(z)=\lim\limits_{z\to1}(z-1)\cdot R(z)\cdot\dfrac{1}{1+GH(z)}$。注意课件在第 22 页全页使用记号 $e(\infty T)$（含采样周期 $T$），而第 21、23–28 页使用 $e(\infty)$，两种记号指同一量，第 22 页的写法强调该稳态误差以采样时刻为自变量。

4. **三类输入的 Z 变换（由第 22 页各行的中间步骤读出）**：
   - $r(t)=A\cdot1(t)$：$R(z)=\dfrac{Az}{z-1}$
   - $r(t)=A\cdot t$：$R(z)=\dfrac{ATz}{(z-1)^2}$
   - $r(t)=\dfrac{A}{2}t^2$：$R(z)=\dfrac{AT^2z(z+1)}{2(z-1)^3}$

5. **第 22 页三个浅绿结论方框**（原图右侧，自上而下依次为）：
   - $=\dfrac{A}{K_p}$（对应 $r(t)=A\cdot1(t)$ 行）
   - $=\dfrac{AT}{K_v}$（对应 $r(t)=A\cdot t$ 行）
   - $=\dfrac{AT^2}{K_a}$（对应 $r(t)=\dfrac{A}{2}t^2$ 行）

6. **误差常数定义的三处出现与一处不一致（重要）**：
   - 第 22 页：$K_p=1+\lim\limits_{z\to1}GH(z)$，$K_v=\lim\limits_{z\to1}(z-1)GH(z)$，$K_a=\lim\limits_{z\to1}(z-1)^2GH(z)$。
   - 第 23 页：$K_p=1+\lim\limits_{z\to1}GH(z)$，$K_v=\lim\limits_{z\to1}(z-1)GH(z)$（与第 22 页一致）。
   - 第 24 页：$K_a=\lim\limits_{z\to1}(z-1)^2GH(z)$（与第 22 页一致）。
   - 第 25 页表格定义行：$K_p=\lim GH(z)$（**无 "$1+$"**），$K_v=\lim(z-1)GH(z)$，$K_a=\lim(z-1)^2GH(z)$。
   即：第 25 页表格中的 $K_p$ 定义与第 22、23 页相差一个常数 1。三页的 $K_v$、$K_a$ 定义完全一致。使用第 25 页表格的 $e(\infty)=A/K_p$ 格子时，若按第 25 页的 $K_p=\lim GH(z)$ 取值，则该格子的公式应理解为 $A/(1+\lim GH(z))$；若按第 22、23 页的 $K_p=1+\lim GH(z)$ 取值，则该格子的公式就是字面的 $A/K_p$。两种口径下 $e(\infty)$ 的数值结果相同（对 0 型系统），但中间量 $K_p$ 的数值相差 1。**本笔记照原图分别记录，不作统一。**

7. **"型别" 列头为中英混排**：第 25 页表格第一列列头写的是中文"型别"，其余列头为英文 "Static Error Constant"、"Steady-State Error"，表内行标签为 "$\nu$"、"0"、"I"、"II"（红色）。课件整体为中英混排。

8. **型别结论中的不等号写法**：课件原文写作 "Type >=1"、"Type >=2"、"Type >=3"、"Type 0,1"（即 0 型和 1 型并写），本笔记在表格中统一写作 $\ge$。

9. **第 26 页与第 27 页例题中的系统结构（两题结构相同）**：
   - 参考输入 $r$ → 相加点 $\otimes$（负反馈，反馈取自输出端 $c$，为**单位反馈**，框图中没有 $H(s)$ 方框）→ 误差 $e$ → 采样开关 → $e^*$ → **ZOH 方框** → 被控对象方框 → 输出节点 → 输出采样开关 → $c^*$（同时给出连续输出 $c$）。
   - 第 26 页被控对象为 $\dfrac{K}{s(s+1)}$；第 27 页被控对象为 $\dfrac{Ke^{-0.5s}}{s}$。
   - 两题均为 $\nu=1$（前向通路含一个积分环节），故都用 $K_v$ 计算。

10. **第 27 页例题给出的"稳定范围"**：题解第一行原文为 "Solution. The stable range of K is $0<K<2.472$"。该范围是本题的已知条件（由第 20 页对同一系统的 $D(z)$ 作 w 变换—劳斯判据得到），本页未重新推导。

11. **第 26 页 with ZOH 一支中 $K_v$ 的中间表达式为压缩写法**：原图为
    $$K_v=\lim_{z\to1}(z-1)G(z)=\lim_{z\to1}\frac{K(T-Te^{-T})}{z-e^{-T}}=KT$$
    其中 $(z-1)$ 已与 $G(z)$ 分母中的 $(z-1)$ 约去，且分子中的 z 多项式已在 $z\to1$ 处取值（取值结果为 $T-Te^{-T}$），分母保留 $(z-e^{-T})$ 未取值。最终结果 $KT$ 经复算正确。

12. **第 28 页 (2) 中的 $D(z)$**：指闭环离散系统的特征多项式（闭环脉冲传递函数的分母）。其具体表达式出现在课件第 20 页（见本笔记例题 3 第 5–7 步与知识点 8），用于判断稳定性。第 28 页只用 "D(z) → Stability" 表示"必须先判断 $D(z)$ 的根是否全在单位圆内"这一步。

13. **第 28 页 (1) 与 (3) 的措辞**：(1) 为 "General method: obtain system response"；(3) 为 "Static error constant"，其后接两支 "G(z) → ν, K_p, K_v, K_a" 与 "Obtain e(∞)"。

14. **本节未出现的图形**：第 21–28 页没有响应曲线图、没有根轨迹图、没有伯德图；唯一的图形是第 21 页的方框图、第 22 页的方框图、第 25 页的表格，以及第 26、27 页各一幅方框图。

---

---

## 解题方法汇总

### 方法 1：由 $\Phi(z)$ 用长除法求单位阶跃响应序列 $h(k)$，再按定义读取 $\sigma\%$、$t_s$

- **适用场景**：给定离散系统的结构框图与 $G(s)$（可含或不含零阶保持器 $\frac{1-e^{-Ts}}{s}$），要求系统的动态性能指标 $\sigma\%$ 与 $t_s$（课件第5、6、7、14页）。要求系统稳定（$h(k)$ 收敛）。
- **已知条件**：$G(s)$、反馈结构、采样周期 $T$、增益 $K$；输入为单位阶跃 $R(z)=z/(z-1)$。
- **计算步骤**：
  1. 判断采样开关位置，写出开环脉冲传递函数 $GH(z)=Z[G(s)H(s)]$；含零阶保持器时用 $G(z)=Z\left[\frac{1-e^{-Ts}}{s}G_0(s)\right]=(1-z^{-1})Z\left[\frac{G_0(s)}{s}\right]$，分块时对每个采样开关隔开的部分分别取 Z 变换再相乘（如第19页 $G(z)=Z[1/s]\cdot Z\left[\frac{1-e^{-Ts}}{s}\cdot\frac{K}{s+1}\right]$）。
  2. 写出闭环脉冲传递函数 $\Phi(z)=\dfrac{G(z)}{1+GH(z)}=\dfrac{M(z)}{D(z)}$（单位反馈时 $H(s)=1$，$GH(z)=G(z)$）。
  3. 由终值定理先算终值：$c(\infty T)=\lim\limits_{z\to1}(z-1)\Phi(z)\dfrac{z}{z-1}$。
  4. 求 $C(z)=\Phi(z)\dfrac{z}{z-1}$，将其分子、分母都除以 $z$ 的最高次幂，化成 $z^{-1}$ 的升幂形式（分母首项为 $1$）。
  5. 做长除法：用分子首项除以分母首项得到商的第一项（形如 $az^{-1}$），用该项乘整个分母并从分子中减去，所得余式作为新的分子，重复此操作，商中 $z^{-k}$ 的系数即为 $h(k)$。等价地可用递推式 $h(k)=a_1h(k-1)-a_2h(k-2)+\cdots+n(k)$（$a_i$ 为分母归一化后的系数，$n(k)$ 为分子系数）。
  6. 按定义读指标：$\sigma\%=\dfrac{h_{\max}-h(\infty)}{h(\infty)}\times100\%$，峰值出现的采样时刻即 $t_p$；$t_s$ 取从某个采样时刻起 $h(k)$ 一直落在 $h(\infty)(1\pm5\%)$ 范围内的最早时刻。
- **常见错误**：
  - 把 $\Phi(z)$ 写成 $\dfrac{G(z)}{1+G(z)H(z)}$。课件第5页的定义是 $\Phi(z)=\dfrac{G(z)}{1+GH(z)}$，其中 $GH(z)=Z[G(s)H(s)]$，两者一般不相等。
  - 长除法前未把分母首项化为 $1$（未除以 $z$ 的最高次幂），导致商的幂次错位。
  - 把 $t_p$、$\sigma\%$、$t_s$ 当作连续系统的二阶公式代入计算，而不是在序列上按定义读取。
  - 判断 $t_s$ 时只看到"某个采样点落进误差带"就作为终点，未检查此后的采样点是否仍在带内。

### 方法 2：由闭环极点位置直接判断动态响应的形状

- **适用场景**：已知 $\Phi(z)$ 的分母（特征多项式），需要判断响应是否振荡、是否衰减、衰减快慢与振荡快慢（课件第9–14页）。
- **已知条件**：$\Phi(z)=M(z)/D(z)$，$D(z)$ 的根（闭环极点 $p_k$）；输入为单位阶跃。
- **计算步骤**：
  1. 求 $D(z)=0$ 的全部根，得到 $p_1,\cdots,p_n$。
  2. 把 $C(z)=\dfrac{M(z)}{D(z)}\cdot\dfrac{z}{z-1}$ 作部分分式展开：$C(z)=\dfrac{M(1)}{D(1)}\dfrac{z}{z-1}+\sum\limits_{k=1}^{n}\dfrac{c_k z}{z-p_k}$，其中第一项由 $z=1$ 的极点产生（对应终值分量），后 $n$ 项由闭环极点产生（对应暂态分量）。
  3. 对每一项单独求响应：实极点时 $c_k(nT)=c_k p_k^{n}$；共轭复极点对时 $c_{k,k}(nT)=2|c_k|e^{anT}\cos(n\omega T+\varphi_k)$，其中 $a=\frac{1}{T}\ln|p_k|$，$\omega=\frac{\theta_k}{T}$。
  4. 逐项判断形状：$|p_k|<1$ 该分量衰减，$|p_k|=1$ 等幅，$|p_k|>1$ 发散；$p_k>0$（实极点）或 $\theta_k=0$ 时不振荡，$p_k<0$ 或 $\theta_k\neq0$ 时振荡；振荡一周期的采样点数 $=\dfrac{360^\circ}{\theta_k}$。
  5. 把各分量按"变化最慢、衰减最慢"的分量为主导分量叠加，得到整体响应形状。
- **常见错误**：
  - 只看模 $|p_k|$ 判断响应形态，忽略极点的符号/相角，从而把 $z=-1$ 的等幅振荡当成"不衰减"的临界而误判振荡与否（$|p_k|=1$ 只说明幅度不衰减）。
  - 用连续系统的 $\omega_n$、$\zeta$ 与 $z$ 平面极点位置直接换算而不经过 $a=\frac{1}{T}\ln|p_k|$、$\omega=\frac{\theta_k}{T}$ 这两个定义式。
  - 复极点只取其中一个写响应，忘记共轭极点成对出现（结果必须是实序列）。

---

### 方法 3：用终值定理求稳态误差 $e(\infty)$

- **适用场景**：系统稳定，要求某输入信号（或其线性组合）作用下的稳态误差。既适用于标准阶跃、斜坡、抛物线输入（课件第18、19、20页），也适用于任意形式的输入 $R(z)$（不限于这三类）或组合输入（如第27页的 $r(t)=2\cdot1(t)+t$，需分项计算后相加）。
- **已知条件**：开环脉冲传递函数 $GH(z)=Z[G(s)H(s)]$ 或前向 $G(z)$（单位反馈时 $H(z)=1$）；输入信号的 Z 变换 $R(z)$；闭环特征多项式 $D(z)$；采样周期 $T$。
- **计算步骤**：
  1. 先判稳：令闭环特征方程 $D(z)=0$（即 $1+GH(z)=0$ 通分后的分子），求出使全部极点位于单位圆内的参数范围（如第19页得到 $0<K<4.33$），并核对给定参数在该范围内。$D(z)$ 的根全部在单位圆内才可继续。
  2. 写出误差脉冲传递函数：$\Phi_e(z)=\dfrac{E(z)}{R(z)}=\dfrac{1}{1+GH(z)}$（单位反馈时 $\Phi_e(z)=\dfrac{1}{1+G(z)}$）。
  3. 把 $\Phi_e(z)$ 化为分子分母均为多项式的最简分式（第19页：$\Phi_e(z)=\dfrac{(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}$）。
  4. 由输入形式写出 $R(z)$：$1(t)\to\dfrac{z}{z-1}$，$t\to\dfrac{Tz}{(z-1)^2}$，$\dfrac{t^2}{2}\to\dfrac{Tz(z+1)}{2(z-1)^3}$。组合输入则拆成各项分别处理。
  5. 代入 $e(\infty)=\lim\limits_{z\to1}(z-1)R(z)\Phi_e(z)$，逐项约去 $(z-1)$ 因子，再把 $z=1$ 代入剩余部分求值；若约分后分母仍含 $(z-1)$，结果为 $\infty$。组合输入先对每一项分别求极限再相加。
  6. 用原始数据核对：把求得的 $K$、$T$ 代入结果（如第19–20页 $e_2=T/K=1/2=0.5$）。
- **常见错误**：
  - 跳过稳定性判断就直接使用终值定理；或未先判稳而把不稳定系统的极限值当作稳态误差。
  - 用连续系统的终值定理 $\lim_{s\to0}sE(s)$ 代替 Z 域的 $\lim_{z\to1}(z-1)E(z)$。
  - 把 $(z-1)$ 因子漏乘或重复乘：终值定理的标准形式是 $\lim_{z\to1}(z-1)E(z)$。
  - $R(z)$ 取错，特别是把 $t$ 的 Z 变换写成 $\dfrac{Tz}{(z-1)^2}$ 之外的错误形式，或漏掉 $T$ 因子。
  - 判 $v$（系统型别）时数错 $GH(z)$ 在 $z=1$ 处的极点个数（只看表面因式而不看是否约分）。
  - 在 $z\to1$ 处直接对未约分的分式赋值，得到 $0/0$ 的结果而未继续化简。
  - 组合输入时先把 $R(z)$ 合并再求极限，导致无法分辨各项对应哪个误差常数（第27页例题的做法是对 $2\cdot1(t)$ 与 $t$ 分别求 $e_1(\infty)$、$e_2(\infty)$ 后相加）。
  - 组合输入时忘记两个分量可能都非零而漏掉其中一项。

---

### 方法 4：静态误差常数法求 $e(\infty)$

- **适用场景**：系统稳定，输入为标准阶跃 $A\cdot1(t)$、标准斜坡 $A\cdot t$ 或标准加速度 $\frac{A}{2}t^2$，且已能写出开环脉冲传递函数 $GH(z)$（或 $G(z)$，单位反馈时 $H(z)=1$）。
- **已知条件**：$GH(z)$ 的表达式；输入信号的类型与参数 $A$；采样周期 $T$（斜坡与加速度输入时进入公式）。
- **计算步骤**：
  1. 把 $GH(z)$ 的分子分母按 $(z-1)$ 的幂次整理，数出 $z=1$ 极点的重数，得到系统型别 $\nu$；把 $GH(z)$ 写成 $GH(z)=\frac{1}{(z-1)^\nu}GH_0(z)$，确认 $\lim_{z\to1}GH_0(z)=K\ne0$（若极限为 0，说明型别数错了）。
  2. 由输入类型确定应使用的误差常数：阶跃用 $K_p$，斜坡用 $K_v$，加速度用 $K_a$。
  3. 计算该误差常数：$K_p=1+\lim_{z\to1}GH(z)$ 或 $K_v=\lim_{z\to1}(z-1)GH(z)$ 或 $K_a=\lim_{z\to1}(z-1)^2GH(z)$。具体做法是把极限号内函数的分子分母同除以 $(z-1)$ 的相应幂次，再令 $z=1$ 代入（若代入后分母为零而分子非零，则结果为 $\infty$；若分子为零，则结果为 $0$）。
  4. 代入对应公式得稳态误差：$e(\infty)=A/K_p$、$e(\infty)=AT/K_v$ 或 $e(\infty)=AT^2/K_a$。
  5. 与型别结论交叉核对：若 $\nu$ 等于输入阶数，第 3 步算出的常数应为有限非零值；若 $\nu$ 大于输入阶数，结果应为 0；若 $\nu$ 小于输入阶数，结果应为 $\infty$。三者中任意一条不符，即为计算或型别判断有误。
- **常见错误**：
  - 用**闭环**传递函数去数 $z=1$ 极点。型别由**开环** $GH(z)$ 决定。
  - 把 $GH(z)$ 中非 $z=1$ 的极点（如 $z=e^{-T}$、$z=-1$）计入型别。
  - 在 $K_p$ 的两种口径之间混用：用教材定义 $K_p=\lim GH(z)$ 去套课件公式 $A/K_p$，得到偏大的 $e(\infty)$。
  - 斜坡输入时把 $A$ 当作幅值。$r(t)=A\cdot t$ 中 $A$ 是斜率，稳态误差为 $AT/K_v$ 而非 $A/K_v$。
  - 加速度输入时漏掉 $T^2$ 或漏掉 $z(z+1)$ 因子。$Z\left[\frac{A}{2}t^2\right]=\frac{AT^2z(z+1)}{2(z-1)^3}$，代入后分母的 2 与 $(z+1)$ 在 $z\to1$ 处给出的 2 相互抵消，才是 $AT^2/K_a$。
  - 系统不稳定时仍使用本方法。本方法的前提是系统稳定（第 21 页原文 "For stable linear discrete systems"）；若 $D(z)$ 的根不全在单位圆内，$e(\infty)$ 不存在。

---

---

### 方法 5：由稳态误差要求确定开环增益 $K$ 的范围

- **适用场景**：给定输入信号与稳态误差上限（如 $e(\infty)<0.5$），求开环增益 $K$ 的取值范围；且系统存在由稳定性决定的 $K$ 上限。
- **已知条件**：开环脉冲传递函数中含待定增益 $K$；输入信号表达式；采样周期 $T$；稳态误差上限；系统稳定时 $K$ 的稳定范围（可由稳定性分析给出，或由题目直接给出）。
- **计算步骤**：
  1. 写出含 $K$ 的开环脉冲传递函数 $G(z)$（含 ZOH 时用 $G(z)=Z\left[\frac{1-e^{-Ts}}{s}G_p(s)\right]$）。
  2. 确定系统型别 $\nu$（数 $z=1$ 极点个数）。
  3. 由输入信号拆项：对每一类输入分量分别选误差常数并算出 $e_i(\infty)$（阶跃分量在 $\nu\ge1$ 时为 0；斜坡分量用 $AT/K_v$）。
  4. 把各项误差相加得 $e(\infty)$ 关于 $K$ 的表达式（$T$ 通常会在这一步约去）。
  5. 解不等式 $e(\infty)<\varepsilon$ 得 $K$ 的一个下界（或上界）。
  6. 与稳定性给出的 $K$ 范围取交集，写出最终区间。
  7. 代回验证：取区间内一个具体 $K$ 值，算 $e(\infty)$ 确认小于上限；取区间端点外侧的值，确认不满足。
- **常见错误**：
  - 只解稳态误差不等式，忘记与稳定性范围取交集（第 27 页的答案 $2<K<2.472$ 中，$2.472$ 来自稳定性）。
  - 把不等式写成非严格不等号（"<" 与 "≤" 混用）：$1/K<0.5$ 给出的是 $K>2$，$K=2$ 处 $e(\infty)=0.5$ 不满足要求。
  - 对阶跃分量仍写出非零误差：$\nu=1$ 时阶跃输入 $e_1(\infty)=0$。
  - 组合输入中漏算某一项，或把两项的误差常数混用（阶跃分量误用 $K_v$）。

---

### 方法 6：含 ZOH（及纯延迟 $e^{-kTs}$）的开环脉冲传递函数 $G(z)$ 的求取

- **适用场景**：系统框图中前向通路在采样开关之后接有零阶保持器，或被控对象含纯延迟环节 $e^{-\tau s}$。
- **已知条件**：被控对象 $G_p(s)$；采样周期 $T$；延迟时间 $\tau$（若含延迟）。
- **计算步骤**：
  1. 写出采样后的前向通路：$G(z)=Z\left[\dfrac{1-e^{-Ts}}{s}G_p(s)\right]$。
  2. 用 $z$ 变换的位移性质把延迟因子提到 $Z[\cdot]$ 之外：$Z\left[e^{-kTs}X(s)\right]=z^{-k}X(z)$，其中 $k=\tau/T$ 为延迟所包含的采样周期数（第 27 页中 $\tau=0.5$、$T=0.25$，故 $k=2$，$e^{-0.5s}=e^{-2Ts}$ 对应 $z^{-2}$）。
  3. 用 $z$ 变换的线性性质把 $1-e^{-Ts}$ 拆开，得到 $G(z)=(1-z^{-1})\cdot z^{-k}\cdot Z\left[\dfrac{G_p(s)}{s}\right]=\dfrac{z-1}{z}z^{-k}Z\left[\dfrac{G_p(s)}{s}\right]$。
  4. 对 $\dfrac{G_p(s)}{s}$ 作部分分式分解（第 26 页例题中 $G_p(s)=\frac{K}{s(s+1)}$，则 $\frac{G_p(s)}{s}=\frac{K}{s^2(s+1)}=\frac{K}{s^2}-\frac{K}{s}+\frac{K}{s+1}$），逐项查 $z$ 变换表：$Z[1/s^2]=\frac{Tz}{(z-1)^2}$，$Z[1/s]=\frac{z}{z-1}$，$Z[1/(s+a)]=\frac{z}{z-e^{-aT}}$。
  5. 合并为单一分式，整理成关于 $z$ 的多项式之比（第 26 页得到 $\dfrac{K[(T-1+e^{-T})z+(1-e^{-T}-Te^{-T})]}{(z-1)(z-e^{-T})}$）。
  6. 求 $K_v$：把分子分母同除以 $(z-1)$ 后令 $z\to1$ 代入。
- **常见错误**：
  - 把 $e^{-Ts}$ 当作可以放入分子多项式的普通因子，直接用 $z\to1$ 代入；正确做法是先把 $e^{-Ts}$ 化为 $z^{-1}$（或 $z^{-k}$）提出。
  - 延迟的采样周期数算错：$k$ 必须用延迟时间除以采样周期并取整数（$\tau/T$ 应为整数，第 27 页 $\tau/T=0.5/0.25=2$）。
  - 部分分式分解中符号错误：$\dfrac{1}{s^2(s+1)}=\dfrac{-1}{s}+\dfrac{1}{s^2}+\dfrac{1}{s+1}$，$s$ 项系数为 $-1$ 而非 $+1$。
  - 求得 $G(z)$ 后未重新数 $z=1$ 极点重数，直接沿用无 ZOH 时的 $K_v$。有 ZOH 时 $G(z)$ 的分母仍含 $(z-1)$，型别不变，但 $K_v$ 的数值由 $K$ 变为 $KT$（第 26 页两题对比）。

---

---

## 例题汇总

### 例题 1：Example 1（课件第6页）——无零阶保持器的离散系统动态性能

**题干**：Consider the system shown in the figure, T=K=1. Obtain the dynamic specifications ($\sigma\%$, $t_s$).

系统结构（第6页右上图）：参考输入 $r$ 进入相加点 $\otimes$，反馈支路带负号；偏差 $e$ 经**采样开关**得到 $e^{*}$；$e^{*}$ 送入连续环节 $\dfrac{K}{s(s+1)}$（框中字为 $\frac{K}{s(s+1)}$）；环节输出 $c$ 经**另一个采样开关**得到 $c^{*}$，同时 $c$ 直接反馈回相加点（单位反馈）。系统**不含零阶保持器**。已知 $T=K=1$。

**解**：

第 1 步：求 $G(z)$。对照常见 Z 变换对 $Z\left[\dfrac{1}{s(s+1)}\right]=\dfrac{(1-e^{-T})z}{(z-1)(z-e^{-T})}$，得

$$G(z)=Z\left[\frac{K}{s(s+1)}\right]=\frac{K(1-e^{-T})z}{(z-1)(z-e^{-T})}$$

第 2 步：代入 $K=T=1$，取 $e^{-1}=0.368$，得

$$G(z)=\frac{1\times(1-0.368)z}{(z-1)(z-0.368)}=\frac{0.632z}{(z-1)(z-0.368)}$$

第 3 步：求闭环脉冲传递函数。单位反馈且比较点在采样开关之前，$GH(z)=G(z)$，故

$$\Phi(z)=\frac{G(z)}{1+G(z)}=\frac{0.632z}{(z-1)(z-0.368)+0.632z}$$

第 4 步：展开分母：$(z-1)(z-0.368)=z^2-1.368z+0.368$；加上 $0.632z$ 得 $z^2-0.736z+0.368$。于是

$$\Phi(z)=\frac{0.632z}{z^2-0.736z+0.368}$$

第 5 步：求终值。

$$c(\infty T)=\lim_{z\to1}(z-1)\cdot\Phi(z)\cdot\frac{z}{z-1}=\lim_{z\to1}\frac{0.632z}{z^2-0.736z+0.368}=\frac{0.632\times1}{1-0.736+0.368}=\frac{0.632}{0.632}=1$$

第 6 步：求 $C(z)=\Phi(z)\cdot\dfrac{z}{z-1}$：

$$C(z)=\frac{0.632z}{z^2-0.736z+0.368}\cdot\frac{z}{z-1}=\frac{0.632z^2}{z^3-1.736z^2+1.104z-0.368}$$

（分母展开：$(z^2-0.736z+0.368)(z-1)=z^3-z^2-0.736z^2+0.736z+0.368z-0.368=z^3-1.736z^2+1.104z-0.368$。）

第 7 步：用长除法求单位阶跃响应序列 $h(k)$。把分子分母同除以 $z^3$：

$$C(z)=\frac{0.632z^{-1}}{1-1.736z^{-1}+1.104z^{-2}-0.368z^{-3}}$$

第一次相除：商的第一项为 $\dfrac{0.632z^{-1}}{1}=0.632z^{-1}$；用 $0.632z^{-1}$ 乘分母得 $0.632z^{-1}-1.097z^{-2}+0.698z^{-3}-0.233z^{-4}$；从分子减去的余式为 $0+1.097z^{-2}-0.698z^{-3}+0.233z^{-4}$。
第二次相除：商的第二项为 $1.097z^{-2}$；用它乘分母得 $1.097z^{-2}-1.904z^{-3}+1.211z^{-4}-0.404z^{-5}$；余式为 $1.206z^{-3}-0.978z^{-4}+0.404z^{-5}$。
第三次相除：商的第三项为 $1.206z^{-3}$（课件的序列取为 $1.207$）。
继续相除即得商 $=0.632z^{-1}+1.097z^{-2}+1.207z^{-3}+1.117z^{-4}+1.014z^{-5}+0.964z^{-6}+0.970z^{-7}+0.991z^{-8}+1.004z^{-9}+1.007z^{-10}+1.003z^{-11}+1.000z^{-12}+\cdots$
上式的等价递推形式为

$$h(k)=1.736\,h(k-1)-1.104\,h(k-2)+0.368\,h(k-3)$$

用课件给出的数值逐步验算：$h(2)=1.736\times0.632=1.097$；$h(3)=1.736\times1.097-1.104\times0.632=1.904-0.698=1.207$；$h(4)=1.736\times1.207-1.104\times1.097+0.368\times0.632=2.095-1.211+0.233=1.117$；$h(5)$ 用该递推与相邻数值算得 $1.010$（课件表中印为 $1.014$，见"识别不确定处"）；$h(6)=1.736\times1.010-1.104\times1.117+0.368\times1.207=1.753-1.233+0.444=0.964$；其后 $h(7)=0.970$、$h(8)=0.991$、$h(9)=1.004$、$h(10)=1.007$、$h(11)=1.003$、$h(12)=1.000$。

第 8 步：按定义读取指标。终值为 $1$；最大值为 $h(3)=1.207$，故

$$\sigma\%=\frac{1.207-1}{1}\times100\%=20.7\%,\qquad t_p=3T$$

$5\%$ 误差带为 $[0.95,\ 1.05]$：$h(4)=1.117>1.05$（在带外），$h(5)=1.014$、$h(6)=0.964$、$h(7)=0.970$、$h(8)=0.991$、$h(9)=1.004$、$h(10)=1.007$、$h(11)=1.003$、$h(12)=1.000$ 全部落在带内，故

$$t_s=5T$$

**答案**：$\sigma\%=20.7\%$，$t_p=3T$，$t_s=5T$（$T=1$ 即 $t_s=5$ 个采样周期）。代回原题条件验证：$T=K=1$，$e^{-1}=0.368$ 与课件一致；$c(\infty T)=1$ 与单位阶跃输入的终值相符；$\sigma\%$ 用 $h(3)=1.207$ 计算得 $20.69\%\approx20.7\%$；$t_s$ 用 $5\%$ 带逐点核对，$h(4)$ 在带外而 $h(5)$ 起全部在带内，与 $t_s=5T$ 一致。

---

### 例题 2：Example 1（课件第7页）——含零阶保持器的离散系统动态性能

**题干**：Example 1 Consider the system shown in the figure, T=K=1. Obtain the dynamic specifications ($\sigma\%$, $t_s$).

系统结构（第7页右上图）：$r$ 进入相加点 $\otimes$（反馈支路带负号）；偏差 $e$ 经**采样开关**得到 $e^{*}$；$e^{*}$ 依次送入两个环节：**零阶保持器** $\dfrac{1-e^{-Ts}}{s}$ 与连续被控对象 $\dfrac{K}{s(s+1)}$（两个环节之间无采样开关）；输出 $c$ 经**采样开关**得到 $c^{*}$，同时 $c$ 直接反馈回相加点（单位反馈）。已知 $T=K=1$。

**解**：

第 1 步：由于零阶保持器与对象之间没有采样开关，二者作为一个整体取 Z 变换：

$$G(z)=Z\left[\frac{1-e^{-Ts}}{s}\cdot\frac{K}{s(s+1)}\right]=K\cdot\frac{z-1}{z}\cdot Z\left[\frac{1}{s^2(s+1)}\right]$$

（式中用到 $1-e^{-Ts}\leftrightarrow\left(1-z^{-1}\right)=\dfrac{z-1}{z}$ 与 $Z[F(s)/s]=\dfrac{z}{z-1}Z\left[\dfrac{F(s)}{s}\right]$ 的移位性质。）

第 2 步：代入 $Z\left[\dfrac{1}{s^2(s+1)}\right]=\dfrac{(T-1+e^{-T})z+(1-e^{-T}-Te^{-T})}{(z-1)(z-e^{-T})}$，得

$$G(z)=K\cdot\frac{(T-1+e^{-T})z+(1-e^{-T}-Te^{-T})}{(z-1)(z-e^{-T})}$$

第 3 步：代入 $K=T=1$。此时 $T-1+e^{-T}=1-1+0.368=0.368$，$1-e^{-T}-Te^{-T}=1-0.368-0.368=0.264$，故

$$G(z)=\frac{0.368z+0.264}{(z-1)(z-0.368)}$$

第 4 步：求闭环脉冲传递函数（$GH(z)=G(z)$）：

$$\Phi(z)=\frac{G(z)}{1+G(z)}=\frac{0.368z+0.264}{(z-1)(z-0.368)+0.368z+0.264}$$

第 5 步：展开分母：$(z-1)(z-0.368)=z^2-1.368z+0.368$；加上 $0.368z+0.264$ 得 $z^2-z+0.632$。于是

$$\Phi(z)=\frac{0.368z+0.264}{z^2-z+0.632}$$

第 6 步：求终值。

$$c(\infty T)=\lim_{z\to1}(z-1)\cdot\Phi(z)\cdot\frac{z}{z-1}=\frac{0.368+0.264}{1-1+0.632}=\frac{0.632}{0.632}=1$$

第 7 步：求 $C(z)=\Phi(z)\cdot\dfrac{z}{z-1}$：

$$C(z)=\frac{0.368z+0.264}{z^2-z+0.632}\cdot\frac{z}{z-1}=\frac{(0.368z+0.264)z}{z^3-2z^2+1.632z-0.632}=\frac{0.368z^2+0.264z}{z^3-2z^2+1.632z-0.632}$$

（分母展开：$(z^2-z+0.632)(z-1)=z^3-z^2-z^2+z+0.632z-0.632=z^3-2z^2+1.632z-0.632$。）

第 8 步：长除法求 $h(k)$。把分子分母同除以 $z^3$：

$$C(z)=\frac{0.368z^{-1}+0.264z^{-2}}{1-2z^{-1}+1.632z^{-2}-0.632z^{-3}}$$

等价递推式为（$n(k)$ 为分子中 $z^{-k}$ 的系数：$n(1)=0.368$、$n(2)=0.264$，其余为零）

$$h(k)=2h(k-1)-1.632h(k-2)+0.632h(k-3)+n(k)$$

逐步计算：
- $h(0)=0$（分子无 $z^{0}$ 项）
- $h(1)=n(1)=0.3679$
- $h(2)=2h(1)-1.632h(0)+0.632h(-1)+n(2)=2\times0.3679+0.264=0.7358+0.264=1.0000$
- $h(3)=2h(2)-1.632h(1)+0.632h(0)+n(3)=2\times1.0000-1.632\times0.3679=2.0000-0.6004=1.3996$
- $h(4)=2h(3)-1.632h(2)+0.632h(1)=2\times1.3996-1.632\times1.0000+0.632\times0.3679=2.7992-1.6320+0.2325=1.3997$（课件表中印为 $1.3996$，与 $h(3)$ 相同）
- $h(5)=2h(4)-1.632h(3)+0.632h(2)=2.7992-2.2841+0.6320=1.1470$
- $h(6)=2h(5)-1.632h(4)+0.632h(3)=2.2940-2.2841+0.8846=0.8944$
- $h(7)=2h(6)-1.632h(5)+0.632h(4)=1.7888-1.8719+0.8846=0.8015$
- $h(8)=2h(7)-1.632h(6)+0.632h(5)=1.6030-1.4597+0.7249=0.8682$
- $h(9)=2h(8)-1.632h(7)+0.632h(6)=1.7364-1.3081+0.5653=0.9936$（课件表中印为 $0.9937$）
- $h(10)=2h(9)-1.632h(8)+0.632h(7)=1.9874-1.4169+0.5065=1.0770$
- $h(11)=2h(10)-1.632h(9)+0.632h(8)=2.1540-1.6217+0.5487=1.0810$
- $h(12)=2h(11)-1.632h(10)+0.632h(9)=2.1620-1.7577+0.6280=1.0323$
- $h(13)=2h(12)-1.632h(11)+0.632h(10)=2.0646-1.7642+0.6807=0.9811$
- $h(14)=2h(13)-1.632h(12)+0.632h(11)=1.9622-1.6847+0.6832=0.9607$

课件给出的序列（右侧列表）：$h(0)=0$、$h(1)=0.3679$、$h(2)=1.0000$、$h(3)=1.3996$、$h(4)=1.3996$、$h(5)=1.1470$、$h(6)=0.8944$、$h(7)=0.8015$、$h(8)=0.8682$、$h(9)=0.9937$、$h(10)=1.0770$、$h(11)=1.0810$、$h(12)=1.0323$、$h(13)=0.9811$、$h(14)=0.9607$，其后为 $\vdots$。

第 9 步：读取指标。终值为 $1$；最大值为 $h(3)=h(4)=1.3996$，课件取峰值时刻

$$t_p=4T,\qquad \sigma\%=\frac{1.3996-1}{1}\times100\%=39.96\%\approx40\%$$

第 10 步：$5\%$ 误差带为 $[0.95,\ 1.05]$。$h(11)=1.0810>1.05$（在带外）；$h(12)=1.0323$、$h(13)=0.9811$、$h(14)=0.9607$ 均在带内，故

$$t_s=12T$$

**答案**：含零阶保持器时 $t_p=4T$、$\sigma\%=40\%$、$t_s=12T$；与例 1（无零阶保持器）的 $t_p=3T$、$\sigma\%=20.7\%$、$t_s=5T$ 相比，加入零阶保持器使超调量由 $20.7\%$ 增大到 $40\%$、调节时间由 $5T$ 增大到 $12T$（课件第8页对比图数据表：有 ZOH 时 $4T/40.0\%/12T$，无 ZOH 时 $3T/20.7\%/5T$，连续系统 $3.7s/16.3\%/5.3s$）。代回原题条件验证：$T=K=1$；$c(\infty T)=(0.368+0.264)/0.632=1$ 与阶跃输入终值相符；$\sigma\%$ 用 $h(3)=h(4)=1.3996$ 计算得 $39.96\%\approx40\%$；$t_s$ 用 $5\%$ 带逐点核对，$h(11)$ 在带外而 $h(12)$ 起全部在带内，与 $t_s=12T$ 一致。

---

### 例题 3：Example 1（课件第19–20页）——用终值定理求三种输入下的稳态误差

**题干**：Example 1 Consider the discrete system shown in the figure, K=2, T=1; Obtain $e(\infty)$ for $r(t)=1(t)$, $t$, $t^2/2$.

系统结构（第19、20页右上图）：参考输入 $r$ 进入相加点 $\otimes$（反馈支路带负号），相加点前另有虚线采样开关标出 $r^{*}$；偏差 $e$ 经**采样开关**得到 $e^{*}$；$e^{*}$ 先送入积分环节 $\dfrac{1}{s}$；其输出再经**一个采样开关**，然后依次送入**零阶保持器** $\dfrac{1-e^{-Ts}}{s}$ 与连续对象 $\dfrac{K}{s+1}$（二者之间无采样开关）；输出 $c$ 经采样开关得到 $c^{*}$，同时 $c$ 直接反馈回相加点（单位反馈）。图中括号标出 $\Phi(z)$ 覆盖 $r\to c$、$\Phi_e(z)$ 覆盖 $r\to e^{*}$、$G(z)$ 覆盖 $e^{*}\to c$。已知 $K=2$，$T=1$。

**解**：

第 1 步：由结构图确定 $G(z)$。$\dfrac{1}{s}$ 与后面部分被采样开关隔开，故分别取 Z 变换再相乘：

$$G(z)=Z\left[\frac{1}{s}\right]\cdot Z\left[\frac{1-e^{-Ts}}{s}\cdot\frac{K}{s+1}\right]$$

第 2 步：$Z\left[\dfrac{1}{s}\right]=\dfrac{z}{z-1}$；零阶保持器部分 $Z\left[\dfrac{1-e^{-Ts}}{s}\cdot\dfrac{K}{s+1}\right]=\dfrac{z-1}{z}\cdot K\cdot Z\left[\dfrac{1}{s(s+1)}\right]=\dfrac{z-1}{z}\cdot K\cdot\dfrac{(1-e^{-T})z}{(z-1)(z-e^{-T})}=\dfrac{K(1-e^{-T})}{z-e^{-T}}$。二者相乘得

$$G(z)=\frac{z}{z-1}\cdot\frac{K(1-e^{-T})}{z-e^{-T}}=\frac{K(1-e^{-T})z}{(z-1)(z-e^{-T})}$$

第 3 步：确定系统型别。$G(z)$ 的分母含因子 $(z-1)$ 一次，课件标出 $v=1$（一型系统）。

第 4 步：求误差脉冲传递函数。

$$\Phi_e(z)=\frac{1}{1+GH(z)}=\frac{1}{1+\dfrac{K(1-e^{-T})z}{(z-1)(z-e^{-T})}}=\frac{(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}$$

第 5 步：写出闭环特征方程（分母为零）：

$$D(z)=(z-1)(z-e^{-T})+K(1-e^{-T})z=0$$

第 6 步：展开。$(z-1)(z-e^{-T})=z^2-z-e^{-T}z+e^{-T}$；加上 $K(1-e^{-T})z$ 得

$$D(z)=z^2+[K(1-e^{-T})-(1+e^{-T})]z+e^{-T}=0$$

第 7 步：由特征方程求 $K$ 的稳定范围。对二阶特征方程 $z^2+a_1z+a_2=0$，用 $w$ 域劳斯判据（课件直接给出结论）

$$0<K<\frac{2(1+e^{-T})}{(1-e^{-T})}$$

代入 $T=1$：$e^{-1}=0.3679$，$2(1+0.3679)/(1-0.3679)=2\times1.3679/0.6321=2.7358/0.6321=4.33$，即 $0<K<4.33$。给定 $K=2$，满足 $2<4.33$，系统稳定，终值定理可用。

第 8 步：输入 $r_1(t)=1(t)$ 时，$R_1(z)=\dfrac{z}{z-1}$，

$$e_1(\infty)=\lim_{z\to1}(z-1)\cdot\frac{z}{z-1}\cdot\frac{(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}$$

分子分母中的 $(z-1)$ 相消（课件图中用蓝色斜线划掉了两处 $(z-1)$），余下

$$e_1(\infty)=\lim_{z\to1}\frac{z(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}=\frac{1\times0\times(1-e^{-T})}{0+K(1-e^{-T})\times1}=0$$

第 9 步：输入 $r_2(t)=t$ 时，$R_2(z)=\dfrac{Tz}{(z-1)^2}$，

$$e_2(\infty)=\lim_{z\to1}(z-1)\cdot\frac{Tz}{(z-1)^2}\cdot\frac{(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}$$

此处共消去两个 $(z-1)$（分母的 $(z-1)^2$ 中一个、分子中一个，图中用蓝色斜线划掉），余下

$$e_2(\infty)=\lim_{z\to1}\frac{Tz(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}=\frac{T\times1\times(1-e^{-T})}{0+K(1-e^{-T})\times1}=\frac{T}{K}$$

代入 $K=2$、$T=1$：$e_2(\infty)=\dfrac{1}{2}=0.5$。

第 10 步：输入 $r_3(t)=\dfrac{t^2}{2}$ 时，$R_3(z)=\dfrac{Tz(z+1)}{2(z-1)^3}$，

$$e_3(\infty)=\lim_{z\to1}(z-1)\cdot\frac{Tz(z+1)}{2(z-1)^3}\cdot\frac{(z-1)(z-e^{-T})}{(z-1)(z-e^{-T})+K(1-e^{-T})z}$$

此处共消去两个 $(z-1)$，分母中仍剩 $(z-1)$ 一次（图中用蓝色斜线划掉两处 $(z-1)$），

$$e_3(\infty)=\lim_{z\to1}\frac{Tz(z+1)(z-e^{-T})}{2(z-1)\left[(z-1)(z-e^{-T})+K(1-e^{-T})z\right]}$$

$z\to1$ 时分子趋于 $T\times1\times2\times(1-e^{-T})=2T(1-e^{-T})$（有限非零），分母趋于 $2\times0\times K(1-e^{-T})=0$，故

$$e_3(\infty)=\infty$$

**答案**：$e_1(\infty)=0$（单位阶跃输入）；$e_2(\infty)=\dfrac{T}{K}=\dfrac{1}{2}=0.5$（单位斜坡输入 $r=t$）；$e_3(\infty)=\infty$（抛物线输入 $r=t^2/2$）。代回原题条件验证：$K=2$、$T=1$ 满足稳定条件 $0<K<4.33$（第 7 步），故终值定理适用；$e_2=T/K=1/2$ 的量纲为时间，与 $r_2(t)=t$（$T=1$，采样间隔 1 秒）一致；$e_1$ 与 $e_3$ 的结果分别与知识点 8 中"$v$ 足够时为零、$v$ 不足时为无穷"的判断一致：对 $v=1$ 的系统，阶跃输入所需 $v\ge1$（满足，故为零），斜坡输入所需 $v\ge1$ 且 $K$ 有限（满足，故为有限值 $T/K$），抛物线输入需要 $v\ge2$（不满足，故为无穷）。

---

### 例题 4（课件第26页 Example 2）：有无 ZOH 时 $r(t)=2t$ 的稳态误差

**题干**：Consider the stable discrete system shown in the figure. When $r(t)=2t$, obtain $e(\infty)$ with/without ZOH.
（考虑图中所示的稳定离散系统。当 $r(t)=2t$ 时，分别求有、无 ZOH 情况下的 $e(\infty)$。）

系统结构（原图）：参考输入 $r$ 接入相加点 $\otimes$，相加点的负端来自输出端（单位负反馈，无 $H(s)$ 方框）；相加点输出为误差 $e$；$e$ 经采样开关得到 $e^*$；$e^*$ 送入 **ZOH** 方框，ZOH 方框再接被控对象方框 $\dfrac{K}{s(s+1)}$；被控对象输出为 $c$，在输出节点再经采样开关得到 $c^*$。

已知条件：被控对象 $\dfrac{K}{s(s+1)}$；单位负反馈；采样周期 $T$（未给数值，结果以 $T$ 表示）；输入 $r(t)=2t$（即 $A=2$ 的斜坡）；题目声明系统稳定。

**解**：

**第 1 部分：no ZOH（不含零阶保持器）**

第 1 步：写出开环脉冲传递函数。前向通路为 $G(s)=\dfrac{K}{s(s+1)}$，故

$$G(z)=Z\left[\frac{K}{s(s+1)}\right]$$

第 2 步：对 $\dfrac{K}{s(s+1)}$ 作部分分式分解，

$$\frac{K}{s(s+1)}=\frac{K}{s}-\frac{K}{s+1}$$

第 3 步：逐项查 $z$ 变换表，$Z\left[\frac{K}{s}\right]=\frac{Kz}{z-1}$，$Z\left[\frac{K}{s+1}\right]=\frac{Kz}{z-e^{-T}}$，故

$$G(z)=\frac{Kz}{z-1}-\frac{Kz}{z-e^{-T}}$$

第 4 步：通分合并，$G(z)=\dfrac{Kz(z-e^{-T})-Kz(z-1)}{(z-1)(z-e^{-T})}=\dfrac{Kz[(z-e^{-T})-(z-1)]}{(z-1)(z-e^{-T})}$，分子中 $z$ 的一次项相消后得

$$G(z)=\frac{K(1-e^{-T})z}{(z-1)(z-e^{-T})}$$

（与课件原式一致：$G(z)=Z\left[\frac{K}{s(s+1)}\right]=\frac{K(1-e^{-T})z}{(z-1)(z-e^{-T})}$。）

第 5 步：确定系统型别。$G(z)$ 的分母含因子 $(z-1)$ 一次，分子在 $z=1$ 处为 $K(1-e^{-T})\cdot1\ne0$（$T\ne0$），故 $z=1$ 为单极点，$\nu=1$。

第 6 步：计算 $K_v$。按定义 $K_v=\lim\limits_{z\to1}(z-1)G(z)$，代入第 4 步结果，

$$K_v=\lim_{z\to1}(z-1)\cdot\frac{K(1-e^{-T})z}{(z-1)(z-e^{-T})}=\lim_{z\to1}\frac{K(1-e^{-T})z}{z-e^{-T}}$$

第 7 步：令 $z\to1$ 代入，分子 $\to K(1-e^{-T})\cdot1$，分母 $\to 1-e^{-T}$（$T\ne0$ 时 $1-e^{-T}\ne0$），故

$$K_v=\frac{K(1-e^{-T})}{1-e^{-T}}=K$$

（与课件原式一致：$K_v=\lim\limits_{z\to1}(z-1)G(z)=\lim\limits_{z\to1}\frac{K(1-e^{-T})z}{z-e^{-T}}=K$。）

第 8 步：代入斜坡输入的稳态误差公式。输入 $r(t)=2t$ 即 $A=2$，$\nu=1$ 时用 $e(\infty)=\dfrac{AT}{K_v}$，

$$e(\infty)=\frac{2T}{K}$$

第 9 步：结论（课件原注）：**— dependent of T**（与采样周期 $T$ 有关）。

**第 2 部分：with ZOH（含零阶保持器）**

第 10 步：写出含 ZOH 的开环脉冲传递函数。零阶保持器的传递函数为 $\dfrac{1-e^{-Ts}}{s}$，故

$$G(z)=Z\left[\frac{1-e^{-Ts}}{s}\cdot\frac{K}{s(s+1)}\right]$$

第 11 步：把 $1-e^{-Ts}$ 拆开并提取，$Z\left[\frac{1-e^{-Ts}}{s}X(s)\right]=(1-z^{-1})Z\left[\frac{X(s)}{s}\right]$，取 $X(s)=\dfrac{K}{s(s+1)}$，得

$$G(z)=K(1-z^{-1})Z\left[\frac{1}{s^2(s+1)}\right]=K\cdot\frac{z-1}{z}\cdot Z\left[\frac{1}{s^2(s+1)}\right]$$

（与课件原式一致：$G(z)=Z\left[\frac{1-e^{-Ts}}{s}\cdot\frac{K}{s(s+1)}\right]=K\frac{z-1}{z}\cdot Z\left[\frac{1}{s^2(s+1)}\right]$。）

第 12 步：对 $\dfrac{1}{s^2(s+1)}$ 作部分分式分解。设

$$\frac{1}{s^2(s+1)}=\frac{a}{s}+\frac{b}{s^2}+\frac{c}{s+1}$$

通分得 $1=a s(s+1)+b(s+1)+c s^2$。令 $s=0$：$1=b$，故 $b=1$；令 $s=-1$：$1=c\cdot1$，故 $c=1$；比较 $s^2$ 项系数：$0=a+c$，故 $a=-1$。于是

$$\frac{1}{s^2(s+1)}=-\frac{1}{s}+\frac{1}{s^2}+\frac{1}{s+1}$$

第 13 步：逐项查表，$Z\left[-\frac{1}{s}\right]=-\frac{z}{z-1}$，$Z\left[\frac{1}{s^2}\right]=\frac{Tz}{(z-1)^2}$，$Z\left[\frac{1}{s+1}\right]=\frac{z}{z-e^{-T}}$，故

$$Z\left[\frac{1}{s^2(s+1)}\right]=-\frac{z}{z-1}+\frac{Tz}{(z-1)^2}+\frac{z}{z-e^{-T}}$$

第 14 步：把第 13 步结果代入第 11 步的 $G(z)$，逐项相乘：

$$G(z)=K\left[-\frac{z-1}{z}\cdot\frac{z}{z-1}+\frac{z-1}{z}\cdot\frac{Tz}{(z-1)^2}+\frac{z-1}{z}\cdot\frac{z}{z-e^{-T}}\right]$$

三项分别化简为 $K\left[-1+\dfrac{T}{z-1}+\dfrac{z-1}{z-e^{-T}}\right]$。

第 15 步：通分到公分母 $(z-1)(z-e^{-T})$，逐项乘：

- $-1$ 一项：分母补 $(z-1)(z-e^{-T})$，分子为 $-(z-1)(z-e^{-T})$
- $\dfrac{T}{z-1}$ 一项：分母补 $(z-e^{-T})$，分子为 $T(z-e^{-T})$
- $\dfrac{z-1}{z-e^{-T}}$ 一项：分母补 $(z-1)$，分子为 $(z-1)^2$

故分子

$$-(z-1)(z-e^{-T})+T(z-e^{-T})+(z-1)^2$$

第 16 步：展开各项。$(z-1)(z-e^{-T})=z^2-ze^{-T}-z+e^{-T}$，故第一项为 $-z^2+ze^{-T}+z-e^{-T}$；第二项为 $Tz-Te^{-T}$；第三项 $(z-1)^2=z^2-2z+1$。

第 17 步：求和。$z^2$ 项：$-z^2+z^2=0$，消去；$z$ 项：$ze^{-T}+z+Tz-2z=(T-1+e^{-T})z$；常数项：$-e^{-T}-Te^{-T}+1=(1-e^{-T}-Te^{-T})$。故分子为

$$(T-1+e^{-T})z+(1-e^{-T}-Te^{-T})$$

第 18 步：写出合并后的 $G(z)$，

$$G(z)=K\cdot\frac{(T-1+e^{-T})z+(1-e^{-T}-Te^{-T})}{(z-1)(z-e^{-T})}$$

（与课件原式一致：$G(z)=K\frac{(T-1+e^{-T})z+(1-e^{-T}-Te^{-T})}{(z-1)(z-e^{-T})}$；注意分子为 $z$ 的一次式，$z^2$ 项在化简中相消。）

第 19 步：确定系统型别。分母仍含 $(z-1)$ 一次，且分子在 $z=1$ 处为 $(T-1+e^{-T})+(1-e^{-T}-Te^{-T})=T-Te^{-T}=T(1-e^{-T})\ne0$，故 $z=1$ 为单极点，$\nu=1$。

第 20 步：计算 $K_v$。由定义 $K_v=\lim\limits_{z\to1}(z-1)G(z)$，

$$K_v=\lim_{z\to1}\frac{K[(T-1+e^{-T})z+(1-e^{-T}-Te^{-T})]}{z-e^{-T}}$$

第 21 步：令 $z\to1$ 代入分子：$K[(T-1+e^{-T})+(1-e^{-T}-Te^{-T})]=K[T-Te^{-T}]=KT(1-e^{-T})$；分母 $\to 1-e^{-T}$。相除并约去 $(1-e^{-T})$，

$$K_v=\frac{KT(1-e^{-T})}{1-e^{-T}}=KT$$

（与课件原式一致：$K_v=\lim\limits_{z\to1}\frac{K(T-Te^{-T})}{z-e^{-T}}=KT$。）

第 22 步：代入斜坡输入的稳态误差公式，$A=2$，

$$e(\infty)=\frac{AT}{K_v}=\frac{2T}{KT}=\frac{A}{K}=\frac{2}{K}$$

（与课件原式一致：$e(\infty)=\frac{AT}{K_v}=\frac{A}{K}=\frac{2}{K}$。）

第 23 步：结论（课件原注）：**— independent of T**（与采样周期 $T$ 无关）。

**答案**：
- 无 ZOH 时：$G(z)=\dfrac{K(1-e^{-T})z}{(z-1)(z-e^{-T})}$，$K_v=K$，$e(\infty)=\dfrac{2T}{K}$，与采样周期 $T$ 有关。
- 有 ZOH 时：$G(z)=K\dfrac{(T-1+e^{-T})z+(1-e^{-T}-Te^{-T})}{(z-1)(z-e^{-T})}$，$K_v=KT$，$e(\infty)=\dfrac{2}{K}$，与采样周期 $T$ 无关。

代回原题条件验证：取具体数值 $T=1$ s、$K=2$。无 ZOH 时 $e^{-T}=e^{-1}=0.3679$，$G(z)=\frac{2\times0.6321z}{(z-1)(z-0.3679)}$，分子在 $z=1$ 处为 $1.2642\ne0$，$\nu=1$ 正确；$K_v=\frac{2\times0.6321}{0.6321}=2=K$，与第 7 步结论 $K_v=K$ 一致；$e(\infty)=\frac{2\times1}{2}=1$。有 ZOH 时，$T-1+e^{-T}=1-1+0.3679=0.3679$，$1-e^{-T}-Te^{-T}=1-0.3679-0.3679=0.2642$，$G(1)$ 的分子为 $2(0.3679+0.2642)=1.2642\ne0$，$\nu=1$ 正确；$K_v=\frac{2(1-0.3679)}{1-0.3679}=2=KT$，与第 21 步结论 $K_v=KT$ 一致（$KT=2\times1=2$）；$e(\infty)=\frac{2\times1}{2}=1=\frac{A}{K}=\frac{2}{2}=1$，与第 22 步一致。两种结构的 $e(\infty)$ 在 $T=1$ 时数值相同（因 $T=1$ 时 $KT=K$），但当 $T\ne1$ 时二者不同，说明无 ZOH 的 $e(\infty)$ 随 $T$ 变化、有 ZOH 的不随 $T$ 变化。

---

### 例题 5（课件第27页 Example 3）：由稳态误差要求确定 $K$ 的范围

**题干**：Consider the system shown in the figure, $T=0.25$. When $r(t)=2\cdot1(t)+t$, obtain the range of $K$ for $e(\infty)<0.5$.
（考虑图中所示系统，$T=0.25$。当 $r(t)=2\cdot1(t)+t$ 时，求使 $e(\infty)<0.5$ 的 $K$ 的取值范围。）

系统结构（原图）：参考输入 $r$ 接入相加点 $\otimes$，负端直接取自输出端（单位负反馈，无 $H(s)$ 方框）；相加点输出为误差 $e$；$e$ 经采样开关得到 $e^*$；$e^*$ 送入 **ZOH** 方框；ZOH 后接被控对象 $\dfrac{Ke^{-0.5s}}{s}$；输出节点给出 $c$，并经采样开关得到 $c^*$。

已知条件：被控对象 $\dfrac{Ke^{-0.5s}}{s}$；单位负反馈；采样周期 $T=0.25$；输入 $r(t)=2\cdot1(t)+t$（阶跃分量幅值 2，斜坡分量斜率 1）；要求 $e(\infty)<0.5$；题解给出稳定性范围 $0<K<2.472$。

**解**：

第 1 步：写出含 ZOH 的开环脉冲传递函数（前向通路 $G_p(s)=\dfrac{Ke^{-0.5s}}{s}$），

$$G(z)=Z\left[\frac{1-e^{-Ts}}{s}\cdot\frac{Ke^{-0.5s}}{s}\right]$$

第 2 步：把延迟化为 $z$ 的负幂。$T=0.25$，延迟时间 $\tau=0.5$，$\tau/T=0.5/0.25=2$，即延迟等于 2 个采样周期，故 $e^{-0.5s}=e^{-2Ts}$，由位移性质 $Z[e^{-2Ts}X(s)]=z^{-2}X(z)$。

第 3 步：拆出 $1-e^{-Ts}$ 并使用位移性质，

$$G(z)=K(1-z^{-1})z^{-2}Z\left[\frac{1}{s^2}\right]$$

（与课件原式一致：$G(z)=K(1-z^{-1})z^{-2}Z\left[\frac{1}{s^2}\right]$。）

第 4 步：查表 $Z\left[\frac{1}{s^2}\right]=\dfrac{Tz}{(z-1)^2}$，代入得

$$G(z)=K\cdot\frac{z-1}{z}\cdot z^{-2}\cdot\frac{Tz}{(z-1)^2}$$

第 5 步：化简。$\dfrac{z-1}{z}=z^{-1}(z-1)$，与 $z^{-2}$ 相乘得 $z^{-3}(z-1)$，再乘 $\dfrac{Tz}{(z-1)^2}$ 得 $\dfrac{T z^{-2}}{z-1}$，故

$$G(z)=\frac{KT}{z^2(z-1)}$$

（与课件原式一致：$G(z)=Kz^{-2}\frac{z-1}{z}\cdot\frac{Tz}{(z-1)^2}=\frac{KT}{z^2(z-1)}$。）

第 6 步：确定系统型别。分母含 $(z-1)$ 一次，分子 $KT$ 在 $z=1$ 处不为零（$K\ne0$、$T=0.25\ne0$），故 $z=1$ 为单极点，$\nu=1$（课件标注 **v = 1**）。

第 7 步：计算 $K_v$。由定义 $K_v=\lim\limits_{z\to1}(z-1)G(z)$，

$$K_v=\lim_{z\to1}(z-1)\cdot\frac{KT}{z^2(z-1)}=\lim_{z\to1}\frac{KT}{z^2}$$

第 8 步：约去 $(z-1)$ 后令 $z\to1$ 代入，分母 $z^2\to1$，得

$$K_v=KT$$

（与课件原式一致：$K_v=\lim\limits_{z\to1}(z-1)G(z)=\lim\limits_{z\to1}(z-1)\frac{KT}{z^2(z-1)}=KT$。代入 $T=0.25$ 得 $K_v=0.25K$。）

第 9 步：把输入拆项。$r(t)=2\cdot1(t)+t$ 是阶跃分量 $r_1(t)=2\cdot1(t)$ 与斜坡分量 $r_2(t)=t$ 之和，故 $e(\infty)=e_1(\infty)+e_2(\infty)$。

第 10 步：求阶跃分量的稳态误差。$\nu=1\ge1$，按第 25 页总表 I 型行、阶跃列，$e_1(\infty)=0$（课件原式：$r_1(t)=2\cdot1(t)$，$e_1(\infty)=0$）。

第 11 步：求斜坡分量的稳态误差。$r_2(t)=t$ 对应 $A=1$，$\nu=1$ 时用 $e(\infty)=AT/K_v$，

$$e_2(\infty)=\frac{TA}{K_v}=\frac{T\cdot1}{KT}=\frac{1}{K}$$

（分子分母中的 $T$ 相消；课件原式：$r_2(t)=t$，$e_2(\infty)=TA/K_v=1/K$。代入 $T=0.25$、$K_v=0.25K$ 得 $e_2(\infty)=\frac{0.25}{0.25K}=\frac1K$，一致。）

第 12 步：相加得总稳态误差，

$$e(\infty)=e_1(\infty)+e_2(\infty)=0+\frac{1}{K}=\frac{1}{K}$$

（课件原式：$e(\infty)=e_1(\infty)+e_2(\infty)=1/K$。）

第 13 步：代入不等式 $e(\infty)<0.5$，

$$\frac{1}{K}<0.5$$

第 14 步：解不等式。$K>0$（由稳定性范围 $0<K<2.472$ 知 $K$ 取正），两边同乘 $2K$（正数，不等号方向不变）得

$$2<K$$

即 $K>2$（课件原式：$\Rightarrow K>2$）。

第 15 步：与稳定性范围取交集。稳定性给出 $0<K<2.472$，与 $K>2$ 取交集得

$$2<K<2.472$$

（课件绿色方框答案：**2 < K < 2.472**。）

**答案**：$2<K<2.472$。

代回原题条件验证：
- 取区间内 $K=2.4$（满足 $2<2.4<2.472$）：$K_v=KT=2.4\times0.25=0.6$；$e_2(\infty)=\frac{TA}{K_v}=\frac{0.25\times1}{0.6}=0.4167$；$e_1(\infty)=0$；$e(\infty)=0.4167<0.5$，满足要求。
- 取下界 $K=2$：$K_v=0.5$，$e(\infty)=\frac{0.25}{0.5}=0.5$，等于 0.5，不满足严格小于，故 $K>2$ 为严格不等号，与第 14 步结论一致。
- 取下界外侧 $K=1.9$：$K_v=0.475$，$e(\infty)=\frac{0.25}{0.475}=0.5263>0.5$，不满足要求，说明 $K$ 必须大于 2。
- 取上界外侧 $K=2.5$：虽 $e(\infty)=\frac{1}{2.5}=0.4<0.5$ 满足误差要求，但 $2.5>2.472$ 超出稳定范围，系统不稳定，$e(\infty)$ 不存在，故不能取。
- 结论：$K$ 的可行区间由稳态误差要求给出下界 2、由稳定性给出上界 2.472，两者缺一不可。

---

## 识别不确定处与核对记录

本节列出整理过程中发现的、需要在使用笔记时留意的细节。凡属课件原图如此而非识别错误的，均保留原样并在此说明；凡经复算判定的，给出复算依据。

**1. 课件第22、23页与第25页对 $K_p$ 的定义不一致（重要）**
- 第22页、第23页：$K_p = 1+\lim\limits_{z\to1}GH(z)$（两页写法一致，已双次高倍放大核对原图）。
- 第25页表格的"定义行"：$K_p=\lim GH(z)$（**无 "$1+$"**）。三页的 $K_v$、$K_a$ 定义完全一致。
- 后果：使用第25页表格的 $e(\infty)=A/K_p$ 这一格时，若 $K_p$ 按第25页字面取 $\lim GH(z)$，则该格应理解为 $A/(1+\lim GH(z))$；若 $K_p$ 按第22、23页取 $1+\lim GH(z)$，则该格就是字面的 $A/K_p$。两种口径下 $e(\infty)$ 的**数值结果相同**（0 型系统时），但中间量 $K_p$ 的数值相差 1。**本笔记照原图分别记录，不作统一。** 使用总表时须先声明采用哪一页的口径。
- 对 $v\ge1$ 的系统，两处定义都给出 $K_p=\infty$、$e(\infty)=0$，加上常数 1 不改变结果，故此不一致只对 0 型系统在使用时产生影响。

**2. 课件第6页响应表中的 $h(5)$ 与同页递推关系不符（真实差异）**
- 课件表中印为 $h(5)=1.014$；用同页给出的递推关系 $h(k)=1.7358h(k-1)-1.1036h(k-2)+0.3679h(k-3)$ 逐步复算（$h(1)=0.6321$、$h(2)=1.0972$、$h(3)=1.2068$、$h(4)=1.1164$）得 $h(5)=1.0095$。
- 交叉验证：以 $h(5)=1.0095$ 继续递推得 $h(6)=0.9641$，与课件印出的 $h(6)=0.964$ 相符；以 $h(5)=1.014$ 递推得 $h(6)=0.9719$，与课件的 $0.964$ 不符。故课件表中的 $1.014$ 与其余数值不自洽，$1.0095$ 才是与该表其余数值一致的值。
- 除 $h(5)$ 外，课件表中 $h(0)\sim h(12)$ 全部可由该递推关系复现。
- **对结论无影响**：$1.0095$ 与 $1.014$ 都落在 $5\%$ 误差带 $[0.95,1.05]$ 内，故 $t_s=5T$ 与 $\sigma\%=20.7\%$（由 $h(3)=1.2068$ 决定）均不受影响。

**3. 课件第7页 $h(3)$ 与 $h(4)$ 相同并非笔误（经复算确认）**
- 课件表中 $h(3)=1.3996$、$h(4)=1.3996$。经复算：$h(3)=1.39958$、$h(4)=1.39957$，两者在四位小数下均进位为 $1.3996$。因此该表自洽，不是印刷错误（仅因极值附近序列变化极缓）。峰值取 $t_p=4T$、$\sigma\%=(1.3996-1)/1=39.96\%\approx40\%$ 与课件一致。

**4. 课件第27页的稳定范围 $0<K<2.472$ 是题目直接给出的前提**
- 该页 Solution 第一行原文为 "The stable range of K is $0<K<2.472$"，本页未重新推导。
- 注意：**它不是由第19–20页例题的结论（$0<K<4.33$）得到的**。第19–20页例题的系统（被控对象含 $1/s$ 与 $\frac{K}{s+1}$，$T=1$，无纯延迟）与本页系统（被控对象 $\frac{Ke^{-0.5s}}{s}$，$T=0.25$，含纯延迟）是两个不同的系统，稳定范围不同，不可跨题套用。使用本题时把 $2.472$ 当作已知条件代入即可。

**5. 课件第26页 with ZOH 一支中 $K_v$ 的中间表达式为压缩写法**
- 原图为 $K_v=\lim\limits_{z\to1}(z-1)G(z)=\lim\limits_{z\to1}\dfrac{K(T-Te^{-T})}{z-e^{-T}}=KT$。其中 $(z-1)$ 已与 $G(z)$ 分母中的 $(z-1)$ 约去，且分子的 $z$ 多项式已在 $z\to1$ 处取值（取值结果为 $K(T-Te^{-T})$），而分母保留 $(z-e^{-T})$ 未取值。这种"分子已代值、分母未代值"的写法是课件的简写习惯，最终结果 $KT$ 经独立复算正确（见例题 4 第 21 步）。no ZOH 一支的 $K_v=\lim\limits_{z\to1}\frac{K(1-e^{-T})z}{z-e^{-T}}=K$ 亦为同一写法。

**6. 记号 $e(\infty T)$ 与 $e(\infty)$ 混用**
- 课件第22页全页使用 $e(\infty T)$（含采样周期 $T$），第21、23–28页使用 $e(\infty)$。两种记号指同一量，第22页的写法强调该稳态误差以采样时刻为自变量。笔记中均照原页记录。

**7. 课件第16页的例题文字沿用了动态性能的措辞**
- 该页属于 7.6.3 稳态误差，但例题文字仍写作 "Obtain the dynamic specifications ($\sigma\%$, $t_s$)"（与第5、6页的动态性能例题文字相同）。原图如此，未作改动。

**8. 课件第3页 [s] 平面阴影带顶部的 $\otimes$ 记号**
- 原图有该记号，但该页未给出文字说明，笔记中仅作位置描述。

**9. 课件第11页图中极点与波形的对应**
- 该页沿实轴排列 8 个 $c_k^{*}(t)$ 波形。其中第 4、5 两支（均表现为 $t=0$ 后迅速衰减到接近 0、第二个采样值为负）与具体极点位置的对应关系不如其余 6 支明确，笔记中按其序列数值与所在位置如实描述。

**10. 课件第14页的系数记号**
- 该页小结写作 $c_k(nT)=C_k p_k^{n}$（大写 $C_k$），而第9、10页写作小写 $c_k$。笔记中两处均照原图记录。

**11. 课件第25页表格的"型别"列头为中英混排**
- 第一列列头写的是中文"型别"，其余列头为英文 "Static Error Constant"、"Steady-State Error"，表内行标签为 "$v$"、"0"、"I"、"II"（红色）。课件整体为中英混排。

**12. 型别结论中的不等号写法**
- 课件原文写作 "Type >=1"、"Type >=2"、"Type >=3"、"Type 0,1"（0 型与 1 型并写），本笔记在表格中统一写作 $\ge$。

---

## 质量检查

- [x] 结构体系覆盖课件全部 28 页（第1–4页总纲与目录、第5–14页 7.6.2、第15–17页过渡与指标、第18–20页终值定理法、第21–28页静态误差常数法）
- [x] 每个叶子知识点均有"定义 + 理解 + 作用"三部分（共 15 个知识点）
- [x] "理解"部分无比喻、类比、拟人及任何修辞手法（已按"就像/好比/如同/犹如/仿佛/相当于"等标记逐条检索，无命中）
- [x] 补充知识点按页码范围分栏列出，未省略原课件中出现的事实性内容（第1–20页 16 条、第21–28页 14 条）
- [x] 解题方法均含"适用场景、已知条件、计算步骤、常见错误"四项（共 6 种方法）
- [x] 计算步骤具体到"下一步用哪个数字、代入哪个公式"
- [x] 公式符号均已标注含义
- [x] 例题汇总含课件全部例题（第6页、第7页、第19–20页、第26页、第27页共 5 道）
- [x] 每道例题题干完整无删减（含系统结构、$K$ 与 $T$ 的取值、输入表达式）
- [x] 每道例题解题步骤无跳步，长除法、部分分式、通分合并的中间结果均完整呈现
- [x] 每道例题最终答案均代回原题条件验证（含逐点核对误差带）
- [x] 识别不确定处已单列，并与课件自洽性复算结果一并记录
