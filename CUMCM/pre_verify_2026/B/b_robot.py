# -*- coding: utf-8 -*-
"""B 题 机器狗程序: 自动搜索定位与清除策略 (与官方模拟器协议完全兼容)。

策略核心 (问题3 全向 / 问题4 全向+定向通用):
  1) 覆盖扫描: 在保证覆盖的站集上逐站扫描 20 个频道。
     问题3: 原点 + 半径1200m 六边形 (7站) —— 已证盘内任一点距最近站 <= 969 m < 1000 <= r_G,
             故每个全向源必被至少一站检测到;
     问题4: 原点 + 600m 十二环 + 1200m 十二环 + 2100m 二十四环 (49站) ——
             数值验证(40万样本)对任意 (G, 定向方向): disk(G,1000) 内各站方向角最大间隙
             158.4° < 180°, 故任意 ±90° 扇区内必有站且距离 <= 1000 m, 每个源必被检测到;
  2) 扫描中 near(<=5m) 直接清除 (<=20m 清除半径内, 必成功);
  3) 逐源归航: 沿示向度方向行进, 每 100m 步重新检测校正方向;
     越过源后示向度翻转 -> 步长减半回头, 指数收敛到 near(<=5m) 后清除。
     归航方向始终朝向源, 距离单调下降 -> 全程保持在接收半径与定向扇区内(有保证);
  4) 问题3: 两站以上示向度用交会区域形心作为起点(全向源无扇区风险, 省行进时间);
     问题4: 归航一律从"离交会点最近的示向站"出发(保定向扇区安全)。

用法:
  python b_robot.py --direct [--mixed] --seed N [--out out/res.json]   # 进程内直连自研环境
  python b_robot.py --http --url http://127.0.0.1:2026 --robot-id X    # HTTP 连模拟器(自研/官方)
"""
import sys
import os
import json
import time
import argparse

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np

from b_geom import region
from b_sim import SimWorld, gen_scenario

STEP0 = 100.0          # 归航初始步长
MAX_HOMING = 80        # 单源归航最大测量次数
D2R = np.pi / 180.0


def ring(r, k):
    a = np.deg2rad(np.arange(0.0, 360.0, 360.0 / k))
    return r * np.column_stack([np.cos(a), np.sin(a)])


def sweep_stops(problem):
    if problem == 3:
        return np.vstack([[0.0, 0.0], ring(1200.0, 6)])
    return np.vstack([[0.0, 0.0], ring(600.0, 12), ring(1200.0, 12), ring(2100.0, 24)])


# ---------------- 客户端: 同一接口, 两种实现 ----------------

class SimClient:
    """进程内直连 SimWorld (无 HTTP 开销, 供蒙特卡洛批量)。"""

    def __init__(self, world):
        self.w = world
        self.w.entered = True

    def enter(self):
        return dict(accepted=True, virtual_time_s=0.0)

    def measure(self, pos, ch):
        dt, res = self.w.step((float(pos[0]), float(pos[1])), True, ch)
        return dict(accepted=True, virtual_time_s=round(self.w.t, 6), **res)

    def clear(self, pos, ch):
        dt, res = self.w.step((float(pos[0]), float(pos[1])), False, ch)
        return dict(accepted=True, virtual_time_s=round(self.w.t, 6), **res)

    def exit(self):
        self.w.exited = True
        return dict(accepted=True, virtual_time_s=round(self.w.t, 6), exit_reason='user_exit')


class HTTPClient:
    """HTTP+JSON 客户端, 兼容官方模拟器与自研 b_sim.py。"""

    def __init__(self, url, robot_id):
        import urllib.request
        self.url = url.rstrip('/')
        self.robot_id = robot_id
        self.seq = 0
        self.urllib = urllib.request

    def _post(self, path, payload):
        rid = f'{path.strip("/")}-{self.seq}'
        self.seq += 1
        body = dict(payload, arena_id='default', robot_id=self.robot_id, request_id=rid)
        data = json.dumps(body).encode('utf-8')
        last = None
        for _ in range(5):                      # 网络异常时用同一 request_id 重试(幂等)
            try:
                req = self.urllib.Request(self.url + path, data=data,
                                          headers={'Content-Type': 'application/json'})
                with self.urllib.urlopen(req, timeout=10) as r:
                    resp = json.loads(r.read().decode('utf-8'))
                if resp.get('accepted'):
                    return resp
                last = resp
                break
            except Exception as e:
                last = e
                time.sleep(0.2)
        raise RuntimeError(f'HTTP {path} 失败: {last}')

    def enter(self):
        return self._post('/enter', {})

    def measure(self, pos, ch):
        return self._post('/measure', {'position': {'x': float(pos[0]), 'y': float(pos[1])},
                                       'channel': int(ch)})

    def clear(self, pos, ch):
        return self._post('/clear', {'position': {'x': float(pos[0]), 'y': float(pos[1])},
                                     'channel': int(ch)})

    def exit(self):
        return self._post('/exit', {})


# ---------------- 策略 ----------------

class Strategy:
    def __init__(self, client, problem=3, verbose=False):
        self.c = client
        self.problem = problem
        self.verbose = verbose
        self.pos = np.array([0.0, 0.0])

    def run(self):
        c = self.c
        c.enter()
        cleared = {}                    # channel -> 清除时刻(虚拟秒)
        bearings = {}                   # channel -> [(stop, svd)]
        t0 = time.time()
        sweep_t = 0.0
        for stop in sweep_stops(self.problem):
            self.pos = stop
            for ch in range(1, 21):
                if ch in cleared:
                    continue
                r = c.measure(stop, ch)
                sweep_t = r['virtual_time_s']
                if r.get('measure_result') == 'near':
                    rr = c.clear(stop, ch)
                    cleared[ch] = rr['virtual_time_s']
                    sweep_t = rr['virtual_time_s']
                    if self.verbose:
                        print(f'  扫描 near -> 清除 ch{ch} @{rr["virtual_time_s"]:.0f}s')
                elif r.get('measure_result') == 'direction':
                    bearings.setdefault(ch, []).append((stop, r['svd_deg']))
        pending = [ch for ch in bearings if ch not in cleared]
        # 贪婪排序: 距当前(最后扫描站)最近的示向站优先
        order = sorted(pending, key=lambda ch: min(
            np.hypot(*(rec[0] - self.pos)) for rec in bearings[ch]))
        for ch in order:
            t = self._hunt(ch, bearings[ch])
            if t is not None:
                cleared[ch] = t
        t_end = c.exit()['virtual_time_s']
        res = dict(n_cleared=len(cleared),
                   cleared_channels=sorted(cleared),
                   per_source=dict((ch, round(t, 1)) for ch, t in cleared.items()),
                   total_virtual_time_s=round(t_end, 1),
                   sweep_time_s=round(sweep_t, 1),
                   wall_time_s=round(time.time() - t0, 2))
        return res

    # ---- 单源归航与清除 ----
    def _hunt(self, ch, recs):
        if self.problem == 3 and len(recs) >= 2:
            pts, unb = region([r[0] for r in recs], [r[1] for r in recs])
            ref = None
            if pts is not None and not unb:
                ref = pts.mean(axis=0)
                r = self.c.measure(ref, ch)
                if r.get('measure_result') == 'near':
                    return self.c.clear(ref, ch)['virtual_time_s']
                if r.get('measure_result') == 'direction':
                    return self._homing(ch, ref, r['svd_deg'])
            start, svd = self._nearest_rec(recs, ref)
            return self._homing(ch, start, svd)
        start, svd = self._nearest_rec(recs, None)
        return self._homing(ch, start, svd)

    @staticmethod
    def _nearest_rec(recs, ref):
        """选离参考点(形心或交会点)最近的示向站; 无参考点时用交会交叉点均值。"""
        if ref is None and len(recs) >= 2:
            pts = []
            for i in range(len(recs)):
                s1, a1 = recs[i]
                u1 = np.array([np.cos(a1 * D2R), np.sin(a1 * D2R)])
                for j in range(i + 1, len(recs)):
                    s2, a2 = recs[j]
                    u2 = np.array([np.cos(a2 * D2R), np.sin(a2 * D2R)])
                    den = u1[0] * u2[1] - u1[1] * u2[0]
                    if abs(den) < 1e-9:
                        continue
                    d = s2 - s1
                    t1 = (d[0] * u2[1] - d[1] * u2[0]) / den
                    t2 = (d[0] * u1[1] - d[1] * u1[0]) / den
                    if t1 >= 0 and t2 >= 0:
                        pts.append(s1 + t1 * u1)
            if pts:
                ref = np.mean(pts, axis=0)
        if ref is not None:
            i = int(np.argmin([np.hypot(*(r[0] - ref)) for r in recs]))
            return recs[i]
        return recs[-1]

    def _homing(self, ch, start, svd):
        """沿示向度归航: 每步重新检测校正; 示向度翻转(越过源)则步长减半回头。

        定向源越过源后会离开 ±90° 扇区, measure 变 no_signal 且不再返回示向度:
        此时先直接尝试清除(清除半径 20m 与朝向无关), 失败则向上一检测点二分回退,
        二分区间收敛到扇区边界(即源附近), 几次迭代内必进入 20m 清除半径。
        """
        c = self.c
        pos = np.asarray(start, dtype=float)
        step = STEP0
        u = np.array([np.cos(svd * D2R), np.sin(svd * D2R)])
        travel = u
        prev = pos
        for _ in range(MAX_HOMING):
            r = c.measure(pos, ch)
            if r.get('measure_result') == 'near':
                return c.clear(pos, ch)['virtual_time_s']
            if r.get('measure_result') == 'direction':
                u = np.array([np.cos(r['svd_deg'] * D2R), np.sin(r['svd_deg'] * D2R)])
                if travel is not None and float(np.dot(u, travel)) < 0.0:
                    step = max(step / 2.0, 2.0)      # 越过源: 回头半步
                travel = u
                prev = pos
                pos = prev + step * u
            else:                                     # no_signal: 越出定向扇区(或异常)
                rr = c.clear(pos, ch)                 # 距源<=20m 时清除成功(与朝向无关)
                if rr.get('clear_result') == 'success':
                    return rr['virtual_time_s']
                pos = (pos + prev) / 2.0              # 二分回到扇区边界(源附近)
        if self.verbose:
            print(f'  !! ch{ch} 归航未收敛')
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--direct', action='store_true', help='进程内直连自研环境')
    ap.add_argument('--mixed', action='store_true', help='含定向源(问题4)')
    ap.add_argument('--p-dir', type=float, default=0.5)
    ap.add_argument('--seed', type=int, default=None)
    ap.add_argument('--http', action='store_true', help='HTTP 连接模拟器')
    ap.add_argument('--url', type=str, default='http://127.0.0.1:2026')
    ap.add_argument('--robot-id', type=str, default='robot-1')
    ap.add_argument('--out', type=str, default=None)
    ap.add_argument('-v', '--verbose', action='store_true')
    args = ap.parse_args()

    problem = 4 if args.mixed else 3
    if args.direct:
        scenario = gen_scenario(seed=args.seed, mixed=args.mixed, p_dir=args.p_dir)
        world = SimWorld(scenario, seed=args.seed)
        client = SimClient(world)
        n_src = len(scenario)
        print(f'[robot] 直连自研环境: 问题{problem}, {n_src} 个源 '
              f'(定向 {sum(1 for s in scenario if s.get("directional"))}), seed={args.seed}')
    else:
        client = HTTPClient(args.url, args.robot_id)
        n_src = None
        print(f'[robot] HTTP 连接 {args.url} (robot_id={args.robot_id}), 问题{problem}')
    st = Strategy(client, problem=problem, verbose=args.verbose)
    res = st.run()
    res['problem'] = problem
    if n_src is not None:
        res['n_sources'] = n_src
        res['clear_ratio'] = round(res['n_cleared'] / n_src, 4)
        res['avg_clear_time_s'] = round(res['total_virtual_time_s'] / max(res['n_cleared'], 1), 1)
    print(f"[robot] 完成: 清除 {res['n_cleared']}" +
          (f"/{n_src} (比例 {res['clear_ratio']:.2%})" if n_src else ' 个') +
          f", 总虚拟时间 {res['total_virtual_time_s']:.0f} s" +
          (f", 平均定位清除时间 {res['avg_clear_time_s']:.0f} s" if n_src else '') +
          f", 墙钟 {res['wall_time_s']} s")
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print(f'[robot] 结果写入 {args.out}')


if __name__ == '__main__':
    main()
