"""3_MPC: LIPM(선형 역진자 모델) 위에서 ZMP 를 따라가는 MPC 로 질량 중심 궤적을 만들고,
역기구학 + 관절 PID 로 이족 로봇을 앞으로 걷게 한다.

MPC (매 0.01 s 마다 다시 풂):
    상태 x = [c, c_dot, c_ddot] (x, y 축 각각),  입력 = jerk (c 의 3계 미분)
    ZMP  p = c - (z_c / g) * c_ddot
    비용  sum ||p - p_ref||^2 * Q  +  sum jerk^2 * R     (호라이즌 N 스텝)
    제약이 없으므로 해가 닫힌 꼴(선형 방정식 한 번)로 나온다. 계산한 입력 열 중 첫 번째만 쓰고 다음 주기에 다시 푼다.

실행:
    python main.py                 # 화면 없이 6 걸음, 그래프 mpc_result.png 저장
    python main.py --gui           # PyBullet 창으로 보기
    python main.py --steps 10 --step-length 0.08
"""
import argparse

import numpy as np
import pybullet as p

from biped_model import Biped, HIP_Y, HIP_Z, ANKLE_H, FOOT_X, leg_ik

G = 9.81
# 걷기는 1_PID 의 이득으로는 발목이 물러서 몸이 기울어 넘어졌다 (실험 결과).
# 이득을 올리되, 발목 KD 를 크게 하면 발이 가벼워 시뮬레이션이 발산하므로 1.0 근처로 둔다.
KP = np.array([1500.0, 1500.0, 1500.0, 1000.0, 1000.0])
KI = np.array([200.0, 200.0, 200.0, 100.0, 100.0])
KD = np.array([10.0, 10.0, 10.0, 1.0, 1.0])


class PID:
    def __init__(self, kp, ki, kd, dt, i_limit=50.0):
        self.kp, self.ki, self.kd, self.dt, self.i_limit = kp, ki, kd, dt, i_limit
        self.integral = 0.0

    def __call__(self, q_ref, q, dq, dq_ref):
        e = q_ref - q
        self.integral = np.clip(self.integral + e * self.dt, -self.i_limit, self.i_limit)
        return self.kp * e + self.ki * self.integral + self.kd * (dq_ref - dq)


class ZmpMPC:
    """LIPM + jerk 입력, 제약 없는 선형 MPC."""

    def __init__(self, T, N, zc, q=1.0, r=1e-6):
        self.T, self.N = T, N
        self.A = np.array([[1, T, T * T / 2], [0, 1, T], [0, 0, 1]])
        self.B = np.array([T**3 / 6, T * T / 2, T])
        self.C = np.array([1, 0, -zc / G])
        # 호라이즌 전체의 ZMP 예측: P = Px x0 + Pu U
        self.Px = np.zeros((N, 3))
        self.Pu = np.zeros((N, N))
        Ak = np.eye(3)
        for i in range(N):
            Ak = self.A @ Ak if i > 0 else self.A
            self.Px[i] = self.C @ Ak
        for i in range(N):
            for j in range(i + 1):
                Aij = np.linalg.matrix_power(self.A, i - j)
                self.Pu[i, j] = self.C @ Aij @ self.B
        H = q * self.Pu.T @ self.Pu + r * np.eye(N)
        self.gain = np.linalg.solve(H, q * self.Pu.T)       # U = gain @ (p_ref - Px x0)

    def solve(self, x0, p_ref):
        U = self.gain @ (p_ref - self.Px @ x0)
        return U[0]


def make_plan(n_steps, step_len, t_ss, t_ds, t_start=1.0, t_end=1.5):
    """발자국 순서, ZMP 기준값, 발 궤적에 필요한 시간표를 만든다."""
    feet = {"L": np.array([0.0, HIP_Y]), "R": np.array([0.0, -HIP_Y])}
    phases = [("ds", t_start, None, None)]
    x = 0.0
    swing = "R"
    for i in range(n_steps):
        # 마지막 걸음은 앞서 나간 발 옆에 나란히 모은다
        x_target = x + step_len if i < n_steps - 1 else x
        phases.append(("ss", t_ss, swing, x_target))
        phases.append(("ds", t_ds if i < n_steps - 1 else t_end, None, None))
        x = x_target
        swing = "L" if swing == "R" else "R"
    return feet, phases


def build_timeline(feet0, phases, dt):
    """시간 순서대로 (ZMP 기준, 왼발, 오른발, 발 높이) 배열을 만든다."""
    feet = {k: v.copy() for k, v in feet0.items()}
    zmp, fl, fr, hl, hr = [], [], [], [], []
    center = lambda f: (f["L"] + f["R"]) / 2 + np.array([FOOT_X, 0])
    prev_zmp = center(feet)
    for i, (kind, dur, swing, x_target) in enumerate(phases):
        n = int(round(dur / dt))
        if kind == "ds":
            # 다음 지지발(= 다음 단계에서 움직이지 않는 발) 쪽으로 ZMP 를 옮긴다
            nxt = phases[i + 1] if i + 1 < len(phases) else None
            if nxt is None:
                goal = center(feet)
            else:
                stance = "L" if nxt[2] == "R" else "R"
                goal = feet[stance] + np.array([FOOT_X, 0])
            for k in range(n):
                s = (k + 1) / n
                zmp.append(prev_zmp + (goal - prev_zmp) * s)
                fl.append(feet["L"].copy()); fr.append(feet["R"].copy()); hl.append(0.0); hr.append(0.0)
            prev_zmp = goal
        else:
            start = feet[swing].copy()
            end = np.array([x_target, start[1]])
            for k in range(n):
                s = (k + 1) / n
                sm = (1 - np.cos(np.pi * s)) / 2
                pos = start + (end - start) * sm
                h = 0.04 * np.sin(np.pi * s)
                zmp.append(prev_zmp.copy())
                if swing == "L":
                    fl.append(pos); fr.append(feet["R"].copy()); hl.append(h); hr.append(0.0)
                else:
                    fr.append(pos); fl.append(feet["L"].copy()); hr.append(h); hl.append(0.0)
            feet[swing] = end
    return np.array(zmp), np.array(fl), np.array(fr), np.array(hl), np.array(hr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gui", action="store_true")
    ap.add_argument("--steps", type=int, default=6)
    ap.add_argument("--step-length", type=float, default=0.08)
    ap.add_argument("--t-ss", type=float, default=0.5, help="한 발 지지 시간 [s]")
    ap.add_argument("--t-ds", type=float, default=0.2, help="두 발 지지 시간 [s]")
    ap.add_argument("--horizon", type=float, default=1.6, help="MPC 예측 구간 [s]")
    ap.add_argument("--pybullet-pd", action="store_true",
                    help="관절 PID 대신 PyBullet 내장 POSITION_CONTROL 사용 (더 단단하게 따라감)")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    robot = Biped(gui=args.gui)
    dt = robot.dt
    T = 0.01                                   # MPC 주기
    sub = int(round(T / dt))
    pid = PID(np.tile(KP, 2), np.tile(KI, 2), np.tile(KD, 2), dt)

    c0 = robot.com()
    base0 = robot.base_state()[0]
    zc = c0[2]
    com_offset = c0[:2] - base0[:2]            # 몸통 위치와 질량 중심의 차이 (처음 자세 기준)
    pelvis_h = base0[2]
    N = int(args.horizon / T)
    mpc = ZmpMPC(T, N, zc)

    feet0, phases = make_plan(args.steps, args.step_length, args.t_ss, args.t_ds)
    zmp, fl, fr, hl, hr = build_timeline(feet0, phases, T)
    M = len(zmp)
    pad = lambda a: np.concatenate([a, np.repeat(a[-1:], N, axis=0)])
    zmp_p = pad(zmp)

    xs = np.array([c0[0], 0, 0.0]); ys = np.array([c0[1], 0, 0.0])
    log = {"t": [], "cx": [], "cy": [], "zx": [], "zy": [], "mx": [], "my": [], "px": [], "py": []}
    q_prev = None
    fell_at = None
    for i in range(M):
        jx = mpc.solve(xs, zmp_p[i:i + N, 0])
        jy = mpc.solve(ys, zmp_p[i:i + N, 1])
        for k in range(sub):
            # 한 MPC 주기 안에서는 jerk 를 일정하게 두고 dt 마다 적분
            Ad = np.array([[1, dt, dt * dt / 2], [0, 1, dt], [0, 0, 1]])
            Bd = np.array([dt**3 / 6, dt * dt / 2, dt])
            xs = Ad @ xs + Bd * jx
            ys = Ad @ ys + Bd * jy
            pelvis = np.array([xs[0], ys[0]]) - com_offset
            s = (k + 1) / sub
            j = min(i + 1, M - 1)
            fL = fl[i] + (fl[j] - fl[i]) * s; fR = fr[i] + (fr[j] - fr[i]) * s
            hL = hl[i] + (hl[j] - hl[i]) * s; hR = hr[i] + (hr[j] - hr[i]) * s
            q_ref = []
            for side, f, h in (("L", fL, hL), ("R", fR, hR)):
                sg = 1.0 if side == "L" else -1.0
                hip = np.array([pelvis[0], pelvis[1] + sg * HIP_Y, pelvis_h + HIP_Z])
                ankle = np.array([f[0], f[1], ANKLE_H + h])
                q_ref += leg_ik(*(ankle - hip))
            q_ref = np.array(q_ref)
            dq_ref = np.zeros(10) if q_prev is None else (q_ref - q_prev) / dt
            q_prev = q_ref
            if args.pybullet_pd:
                p.setJointMotorControlArray(robot.id, robot.jids, p.POSITION_CONTROL, targetPositions=list(q_ref),
                                            forces=[200.0] * 10, positionGains=[0.3] * 10, velocityGains=[1.0] * 10)
            else:
                q, dq = robot.joint_state()
                robot.apply_torque(pid(q_ref, q, dq, dq_ref))
            robot.step()
            if args.gui:
                import time; time.sleep(dt)
        if fell_at is None and robot.fallen():
            fell_at = i * T
            break
        c = robot.com()
        log["t"].append(i * T); log["cx"].append(xs[0]); log["cy"].append(ys[0])
        log["zx"].append(zmp[i, 0]); log["zy"].append(zmp[i, 1])
        log["mx"].append(c[0]); log["my"].append(c[1])
        log["px"].append(xs[0] - zc / G * xs[2]); log["py"].append(ys[0] - zc / G * ys[2])

    base = robot.base_state()[0]
    feet_end = {s: p.getLinkState(robot.id, robot.foot[s])[4] for s in "LR"}
    robot.close()
    print(f"걸음 수 {args.steps}, 보폭 {args.step_length} m, MPC 호라이즌 {N} 스텝 ({args.horizon} s)")
    print(f"MPC 가 만든 ZMP 와 기준 ZMP 의 차이 최대: x {np.max(np.abs(np.array(log['px']) - log['zx'])) * 100:.1f} cm, "
          f"y {np.max(np.abs(np.array(log['py']) - log['zy'])) * 100:.1f} cm")
    print(f"계획한 질량 중심과 시뮬레이션 질량 중심의 차이 최대: x {np.max(np.abs(np.array(log['cx']) - log['mx'])) * 100:.1f} cm, "
          f"y {np.max(np.abs(np.array(log['cy']) - log['my'])) * 100:.1f} cm")
    print(f"몸통 최종 위치: x = {base[0]:.3f} m, y = {base[1]:.3f} m  (계획한 발 위치 x = {fl[-1][0]:.3f} m)")
    print(f"발목 최종 위치: 왼발 x = {feet_end['L'][0]:.3f}, 오른발 x = {feet_end['R'][0]:.3f} m")
    print("결과: 넘어짐 (t = %.2f s)" % fell_at if fell_at else "결과: 넘어지지 않고 끝까지 걸음")

    if not args.no_plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
        for a, k, lab in ((ax[0], "x", "x"), (ax[1], "y", "y")):
            a.plot(log["t"], log["z" + k], "k--", label="ZMP ref")
            a.plot(log["t"], log["p" + k], label="ZMP (MPC model)")
            a.plot(log["t"], log["c" + k], label="CoM plan (MPC)")
            a.plot(log["t"], log["m" + k], label="CoM in PyBullet")
            a.set_ylabel(lab + " [m]"); a.legend(loc="best", fontsize=8)
        ax[0].set_title("LIPM ZMP MPC walking"); ax[1].set_xlabel("time [s]")
        fig.tight_layout(); fig.savefig("mpc_result.png", dpi=100)
        print("그래프 저장: mpc_result.png")


if __name__ == "__main__":
    main()
