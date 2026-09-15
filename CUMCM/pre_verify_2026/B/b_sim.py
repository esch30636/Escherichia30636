# -*- coding: utf-8 -*-
"""B 题 自研仿真环境 (不安装官方模拟器, 严格按附件2通信协议自实现)。

物理规则 (与官方一致):
  * 目标区域: 半径 1800 m 圆盘, 圆心原点, 东 x 北 y;
  * 干扰源: 10-16 个, 频道互异且取自 1..20; 有效接收半径 r ~ U[1000,1500];
    全向 / 定向(±90° 覆盖, 定向方向未知);
  * 示向度: 真实方位角 + 误差, 误差 ∈ [-1°,1°], 同一检测点重复检测误差不变
    (按 (源, 坐标) 缓存); svd_deg 保留两位小数, [0,360) 归一化;
  * 近距离阈值 5 m (且在覆盖内) -> "near"; 清除半径 20 m (与朝向无关);
  * 计时: 移动 = 距离/5 s; /measure 含切换 1 s (频道变化时) + 检测 5 s;
    /clear 含 3 s (未发现) / 5 s (成功); /enter /exit 不推进时钟;
    虚拟时间微秒累计, 响应保留至多 6 位小数。

协议 (与官方一致): POST /enter /measure /clear /exit, HTTP+JSON。
用法:
  python b_sim.py --port 2026 [--mixed] [--p-dir 0.5] [--seed 42]
                  [--scenario scenario.json] [--truth out/truth.json]
  --mixed 时干扰源含定向源, 各源独立以概率 p_dir 为定向。
"""
import sys
import os
import json
import time
import threading
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np

ARENA = 'default'
DISK = 1800.0
V_MAX = 5.0                      # 移动速度 m/s
T_MEASURE = 5.0                  # 检测动作耗时
T_SWITCH = 1.0                   # 切换频道耗时
T_CLEAR_OK = 5.0                 # 成功清除(精确定位3+清除2)
T_CLEAR_MISS = 3.0               # 未发现可清除目标
NEAR_R = 5.0                     # 近距离阈值
CLEAR_R = 20.0                  # 清除半径
ERR_DEG = 1.0                    # 示向度误差上界
MAX_VIRTUAL = 360000.0           # 虚拟时限
MAX_REAL = 1200                  # 现实时限(自研环境固定返回)
COORD_MAX = 2000000.0            # 坐标绝对值上限
MAX_BODY = 65536                 # 请求体上限
IDEMPOTENCY_CAP = 100000         # 幂等记录上限 -> 429
R_MIN, R_MAX = 1000.0, 1500.0    # 有效接收半径范围
N_SRC_LO, N_SRC_HI = 10, 16      # 干扰源个数范围


def _finite(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return False
    return np.isfinite(f) and abs(f) <= COORD_MAX


class SimWorld:
    """核心物理模拟 (纯逻辑, 与 HTTP 无关, 可被机器人进程内直接调用)。"""

    def __init__(self, sources, seed=None):
        self.sources = list(sources)
        self.rng = np.random.default_rng(seed)
        self.by_channel = {s['channel']: s for s in self.sources}
        self.err_cache = {}          # (src_id, (x, y)) -> 误差(度), 定点固定
        self.t = 0.0                 # 虚拟时钟(秒)
        self.pos = (0.0, 0.0)
        self.channel = 1
        self.entered = False
        self.exited = False
        self.robot_id = None
        self.stat = dict(n_measure=0, n_clear=0, dist_move=0.0, n_switch=0)

    # ---------- 物理 ----------
    def _in_sector(self, src, p):
        if not src.get('directional', False):
            return True
        th = np.radians(src['direction_deg'])
        return (p[0] - src['x']) * np.cos(th) + (p[1] - src['y']) * np.sin(th) >= 0.0

    def _error(self, src_id, p):
        key = (src_id, p)
        if key not in self.err_cache:
            self.err_cache[key] = float(self.rng.uniform(-ERR_DEG, ERR_DEG))
        return self.err_cache[key]

    def step(self, p, is_measure, channel):
        """一次合法动作: 返回 (耗时, 结果dict)。推进时钟/位置/频道。"""
        dx, dy = p[0] - self.pos[0], p[1] - self.pos[1]
        dt = np.hypot(dx, dy) / V_MAX
        self.stat['dist_move'] += float(np.hypot(dx, dy))
        if is_measure:
            if channel != self.channel:
                dt += T_SWITCH
                self.stat['n_switch'] += 1
            dt += T_MEASURE
        self.pos = (float(p[0]), float(p[1]))
        if is_measure:
            self.channel = channel
            self.stat['n_measure'] += 1
            self.t += dt
            return dt, self._measure_result(channel)
        self.stat['n_clear'] += 1
        res = self._clear_result(channel)
        dt += T_CLEAR_OK if res['clear_result'] == 'success' else T_CLEAR_MISS
        self.t += dt
        return dt, res

    def _measure_result(self, channel):
        src = self.by_channel.get(channel)
        if src is None or src.get('cleared', False):
            return {'measure_result': 'no_signal'}
        d = np.hypot(self.pos[0] - src['x'], self.pos[1] - src['y'])
        if d > src['r'] or not self._in_sector(src, self.pos):
            return {'measure_result': 'no_signal'}
        if d <= NEAR_R:
            return {'measure_result': 'near'}
        true_b = np.degrees(np.arctan2(src['y'] - self.pos[1], src['x'] - self.pos[0]))
        svd = round((true_b + self._error(src['id'], self.pos)) % 360.0, 2)
        return {'measure_result': 'direction', 'svd_deg': svd}

    def _clear_result(self, channel):
        src = self.by_channel.get(channel)
        if src is None or src.get('cleared', False):
            return {'clear_result': 'no_target_in_range'}
        d = np.hypot(self.pos[0] - src['x'], self.pos[1] - src['y'])
        if d <= CLEAR_R:
            src['cleared'] = True
            src['cleared_at'] = round(self.t, 6)
            return {'clear_result': 'success'}
        return {'clear_result': 'no_target_in_range'}


def gen_scenario(seed=None, mixed=False, p_dir=0.5, n_src=None):
    """生成随机案例: 10-16 个源, 频道互异, 盘内均匀, r~U[1000,1500]。"""
    rng = np.random.default_rng(seed)
    if n_src is None:
        n_src = int(rng.integers(N_SRC_LO, N_SRC_HI + 1))
    chans = rng.choice(np.arange(1, 21), size=n_src, replace=False)
    rad = DISK * np.sqrt(rng.uniform(0, 1, n_src))
    ang = rng.uniform(0, 2 * np.pi, n_src)
    sources = []
    for i in range(n_src):
        s = dict(id=i, channel=int(chans[i]),
                 x=float(rad[i] * np.cos(ang[i])), y=float(rad[i] * np.sin(ang[i])),
                 r=float(rng.uniform(R_MIN, R_MAX)), directional=False)
        if mixed and rng.uniform() < p_dir:
            s['directional'] = True
            s['direction_deg'] = float(rng.uniform(0.0, 360.0))
        sources.append(s)
    return sources


# ---------------- HTTP 服务 ----------------

class SimHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    server_version = 'BSimServer/1.0'
    world = None          # 由 serve() 注入
    world_lock = None
    idem = None           # request_id -> (content_md5, response_dict)
    robot_id = 'robot-1'
    truth_path = None
    scenario = None
    ended = False

    def _send(self, status, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_reject(self, status=400):
        self._send(status, dict(accepted=False,
                                real_timestamp_ms=int(time.time() * 1000),
                                virtual_time_s=0.0))

    def do_GET(self):
        self._send(405, dict(accepted=False, real_timestamp_ms=int(time.time() * 1000),
                             virtual_time_s=0.0))

    def do_POST(self):
        path = self.path.split('?')[0]
        if self.path != path or path not in ('/enter', '/measure', '/clear', '/exit'):
            self._json_reject(404 if path not in ('/enter', '/measure', '/clear', '/exit')
                              else 405)
            return
        ct = self.headers.get('Content-Type', '')
        ct = ct.strip().lower()
        if ct == 'application/json':
            pass
        elif ct.startswith('application/json;'):
            if ct != 'application/json; charset=utf-8':
                self._json_reject(415)
                return
        else:
            self._json_reject(415)
            return
        ce = self.headers.get('Content-Encoding', 'identity').strip().lower()
        if ce not in ('', 'identity'):
            self._json_reject(415)
            return
        try:
            n = int(self.headers.get('Content-Length', 0))
        except ValueError:
            self._json_reject(400)
            return
        if n > MAX_BODY:
            self._json_reject(413)
            return
        raw = self.rfile.read(n) if n > 0 else b''
        try:
            body = json.loads(raw.decode('utf-8'), object_pairs_hook=_no_dup)
        except Exception:
            self._json_reject(400)
            return
        if not isinstance(body, dict):
            self._json_reject(400)
            return
        with self.world_lock:
            self._handle(path, body)

    def _handle(self, path, body):
        ts = int(time.time() * 1000)
        # ---- 基础字段校验 (400) ----
        base = ('arena_id', 'robot_id', 'request_id')
        if any(k not in body for k in base) or any(k not in base for k in body
                                                    if path in ('/enter', '/exit')):
            self._json_reject(400)
            return
        for k in base:
            v = body.get(k)
            if not isinstance(v, str):
                self._json_reject(400)
                return
        rid, rqid = body['robot_id'], body['request_id']
        if not (1 <= len(rid.encode('utf-8')) <= 64 and 1 <= len(rqid.encode('utf-8')) <= 128):
            self._json_reject(400)
            return
        if any(ord(c) < 32 for c in rid + rqid):
            self._json_reject(400)
            return
        if path in ('/measure', '/clear'):
            keys = base + ('position', 'channel')
            if any(k not in body for k in keys) or len(body) != len(keys):
                # 未声明字段 -> 200 accepted=false (帮助发现拼写错误, 与官方一致)
                self._send(200, dict(accepted=False, real_timestamp_ms=ts, virtual_time_s=0.0))
                return
            pos = body['position']
            if (not isinstance(pos, dict) or set(pos.keys()) != {'x', 'y'}
                    or not _finite(pos['x']) or not _finite(pos['y'])):
                self._json_reject(400)
                return
            ch = body['channel']
            if isinstance(ch, bool) or not isinstance(ch, (int, float)) \
                    or float(ch) != int(ch) or not (1 <= int(ch) <= 20):
                self._json_reject(400)
                return
            ch = int(ch)
        else:
            if len(body) != 3:
                self._send(200, dict(accepted=False, real_timestamp_ms=ts, virtual_time_s=0.0))
                return
        # ---- 幂等 ----
        key = rqid
        sig = (path, json.dumps(body, sort_keys=True, ensure_ascii=False))
        if key in self.idem:
            if self.idem[key][0] == sig:
                self._send(200, self.idem[key][1])
            else:
                self._json_reject(409)
            return
        if len(self.idem) >= IDEMPOTENCY_CAP:
            self._json_reject(429)
            return
        # ---- 业务接受判定 (200 accepted=false 不占用幂等记录) ----
        if body['arena_id'] != ARENA or rid != self.robot_id:
            self._send(200, dict(accepted=False, real_timestamp_ms=ts, virtual_time_s=0.0))
            return
        w = self.world
        resp = dict(accepted=False, real_timestamp_ms=ts, virtual_time_s=0.0)
        if path == '/enter':
            if w.entered or self.ended:
                self._send(200, resp)
                return
            w.entered = True
            w.robot_id = rid
            resp = dict(accepted=True, real_timestamp_ms=ts, virtual_time_s=0.0,
                        max_virtual_duration_s=MAX_VIRTUAL, max_real_duration_s=MAX_REAL,
                        remaining_real_duration_s=MAX_REAL)
        elif path == '/exit':
            if not w.entered or w.exited:
                self._send(200, resp)
                return
            w.exited = True
            self.ended = True
            resp = dict(accepted=True, real_timestamp_ms=ts,
                        virtual_time_s=round(w.t, 6), exit_reason='user_exit')
            self._dump_truth()
        else:  # measure / clear
            if not w.entered or w.exited:
                self._send(200, resp)
                return
            dt, res = w.step((float(body['position']['x']), float(body['position']['y'])),
                             path == '/measure', ch)
            resp = dict(accepted=True, real_timestamp_ms=ts, virtual_time_s=round(w.t, 6))
            resp.update(res)
        self.idem[key] = (sig, resp)
        self._send(200, resp)

    def _dump_truth(self):
        if not self.truth_path:
            return
        w = self.world
        n_cleared = sum(1 for s in w.sources if s.get('cleared', False))
        out = dict(scenario=self.scenario,
                   n_sources=len(w.sources),
                   n_cleared=n_cleared,
                   cleared_channels=[s['channel'] for s in w.sources if s.get('cleared', False)],
                   total_virtual_time_s=round(w.t, 6),
                   per_source=[dict(channel=s['channel'], cleared=s.get('cleared', False),
                                    cleared_at=s.get('cleared_at'))
                               for s in w.sources],
                   stat=w.stat)
        with open(self.truth_path, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(f'[b_sim] 测试结束, 真值写入 {self.truth_path}: '
              f'清除 {n_cleared}/{len(w.sources)}, 虚拟时间 {w.t:.1f} s')

    def log_message(self, *a):
        pass


def _no_dup(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError(f'duplicate key {k}')
        d[k] = v
    return d


def serve(scenario, port, robot_id, truth_path):
    SimHandler.scenario = scenario
    SimHandler.world = SimWorld(scenario)
    SimHandler.world_lock = threading.Lock()
    SimHandler.idem = {}
    SimHandler.robot_id = robot_id
    SimHandler.truth_path = truth_path
    SimHandler.ended = False
    srv = ThreadingHTTPServer(('127.0.0.1', port), SimHandler)
    print(f'[b_sim] 自研仿真环境就绪: http://127.0.0.1:{port}  '
          f'干扰源 {len(scenario)} 个'
          f' (定向 {sum(1 for s in scenario if s.get("directional"))} 个), '
          f'robot_id={robot_id}')
    if truth_path:
        print(f'[b_sim] 结束后真值写 {truth_path}')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=2026)
    ap.add_argument('--mixed', action='store_true', help='含定向干扰源(问题4)')
    ap.add_argument('--p-dir', type=float, default=0.5, help='定向源概率')
    ap.add_argument('--seed', type=int, default=None)
    ap.add_argument('--scenario', type=str, default=None, help='场景 JSON 文件')
    ap.add_argument('--truth', type=str, default=None, help='结束后真值输出文件')
    ap.add_argument('--robot-id', type=str, default='robot-1')
    args = ap.parse_args()
    if args.scenario:
        with open(args.scenario, encoding='utf-8') as f:
            scenario = json.load(f)['sources']
    else:
        scenario = gen_scenario(seed=args.seed, mixed=args.mixed, p_dir=args.p_dir)
    serve(scenario, args.port, args.robot_id, args.truth)
