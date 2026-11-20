"""2_LQR: 발목 토크를 LQR 로 계산해 앞뒤로 밀렸을 때 버티는 균형 제어.

로봇 전체를 발목을 축으로 하는 역진자(inverted pendulum)로 보고, 앞뒤 기울기
theta (발목에서 질량 중심까지 선분이 수직과 이루는 각) 와 각속도를 상태로 쓴다.
    상태 x = [theta, theta_dot],  입력 u = 발목 토크 (양발 합)
    선형화 모델:  theta_ddot = (g / L) * theta - u / (m L^2)
LQR 이득 K 는 연속시간 리카티 방정식(scipy.linalg.solve_continuous_are)으로 구한다.
발목 이외의 관절은 1_PID 와 같은 관절 PID 로 자세를 붙잡아 둔다.

실행:
    python main.py                     # 화면 없이, 기본 미는 힘으로 LQR 실행 + 그래프 저장
    python main.py --gui               # PyBullet 창으로 보기
    python main.py --compare           # LQR 과 '발목도 PID 로 고정' 두 경우를 여러 힘으로 비교
    python main.py --push 60           # 미는 힘 [N] 바꾸기 (0.1 s 동안 몸통을 앞으로 민다)
"""
import argparse

import numpy as np
import pybullet as p
from scipy.linalg import solve_continuous_are

from biped_model import Biped, FOOT_SIZE, FOOT_X

G = 9.81
# 관절 PID 이득 [hip_roll, hip_pitch, knee, ankle_pitch, ankle_roll]
KP = np.array([400.0, 400.0, 400.0, 200.0, 200.0])
KI = np.array([200.0, 200.0, 200.0, 100.0, 100.0])
KD = np.array([6.0, 6.0, 6.0, 0.6, 0.6])
# LQR 가중치: 상태 [theta, theta_dot], 입력 u
Q = np.diag([2000.0, 50.0])
R = np.array([[0.01]])
ANKLE_PITCH = [3, 8]   # 관절 배열에서 왼/오른 ankle_pitch 위치


class PID:
    def __init__(self, kp, ki, kd, dt, i_limit=50.0):
        self.kp, self.ki, self.kd, self.dt, self.i_limit = kp, ki, kd, dt, i_limit
        self.integral = 0.0

    def __call__(self, q_ref, q, dq):
        e = q_ref - q
        self.integral = np.clip(self.integral + e * self.dt, -self.i_limit, self.i_limit)
        return self.kp * e + self.ki * self.integral - self.kd * dq


def lqr_gain(m, L):
    A = np.array([[0.0, 1.0], [G / L, 0.0]])
    B = np.array([[0.0], [-1.0 / (m * L * L)]])
    P = solve_continuous_are(A, B, Q, R)
    K = np.linalg.solve(R, B.T @ P)       # u = -K x
    eig = np.linalg.eigvals(A - B @ K)
    return K, eig


def run(push, use_lqr, gui=False, sim_time=4.0, push_at=1.0, push_dur=0.1, verbose=False):
    robot = Biped(gui=gui)
    dt = robot.dt
    pid = PID(np.tile(KP, 2), np.tile(KI, 2), np.tile(KD, 2), dt)
    q_ref = np.array(robot.stand_pose())
    m = robot.total_mass()
    ankle_x = p.getLinkState(robot.id, robot.foot["L"])[4][0]   # 발목 관절의 x 위치 (양발 같음)
    ankle_z = p.getLinkState(robot.id, robot.foot["L"])[4][2]
    c0 = robot.com()
    L = c0[2] - ankle_z
    K, eig = lqr_gain(m, L)
    if verbose:
        print(f"질량 m = {m:.1f} kg, 발목~질량중심 높이 L = {L:.3f} m")
        print(f"LQR 이득 K = {np.round(K, 1)},  닫힌 루프 고유값 = {np.round(eig, 2)}")
    # 발이 들리지 않으려면 ZMP 가 발바닥 안에 있어야 한다 -> 발목 토크 한계
    # u > 0 이면 발끝 쪽으로 눌러 ZMP 가 앞으로, u < 0 이면 뒤꿈치 쪽으로 간다.
    toe = FOOT_X + FOOT_SIZE[0] / 2
    heel = FOOT_SIZE[0] / 2 - FOOT_X
    u_max, u_min = 0.9 * m * G * toe, -0.9 * m * G * heel

    theta_prev = None
    log = {"t": [], "theta": [], "u": [], "x": []}
    fell_at = None
    for k in range(int(sim_time / dt)):
        t = k * dt
        c = robot.com()
        theta = np.arctan2(c[0] - ankle_x, c[2] - ankle_z)
        dtheta = 0.0 if theta_prev is None else (theta - theta_prev) / dt
        theta_prev = theta
        q, dq = robot.joint_state()
        tau = pid(q_ref, q, dq)
        u = 0.0
        if use_lqr:
            u = -float((K @ np.array([theta, dtheta]))[0])
            u = float(np.clip(u, u_min, u_max))
            tau[ANKLE_PITCH] = u / 2.0          # 양발이 반씩 낸다
        robot.apply_torque(tau)
        if push_at <= t < push_at + push_dur:
            p.applyExternalForce(robot.id, -1, [push, 0, 0], [0, 0, 0], p.LINK_FRAME)
        robot.step()
        if gui:
            import time; time.sleep(dt)
        if k % 5 == 0:
            log["t"].append(t); log["theta"].append(theta); log["u"].append(u if use_lqr else tau[ANKLE_PITCH].sum())
            log["x"].append(c[0])
        if fell_at is None and robot.fallen():
            fell_at = t
            break
    robot.close()
    return fell_at, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gui", action="store_true")
    ap.add_argument("--push", type=float, default=60.0, help="몸통을 0.1 s 동안 앞으로 미는 힘 [N]")
    ap.add_argument("--compare", action="store_true", help="여러 힘에서 LQR 과 PID 고정을 비교")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    if args.compare:
        print("미는 힘[N]   LQR 발목 제어   발목도 PID 로 고정")
        for f in [20, 30, 40, 50, 60, 70, 80, 90, 100]:
            a, _ = run(f, True)
            b, _ = run(f, False)
            print(f"{f:8.0f}     {'버팀' if a is None else '넘어짐':8s}       {'버팀' if b is None else '넘어짐'}")
        return

    fell, log = run(args.push, True, gui=args.gui, verbose=True)
    th = np.degrees(np.array(log["theta"]))
    print(f"미는 힘 {args.push:.0f} N: 최대 기울기 {np.abs(th).max():.2f} deg, 마지막 기울기 {th[-1]:.2f} deg")
    print("결과: 넘어짐 (t = %.2f s)" % fell if fell else "결과: 넘어지지 않고 원래 자세로 복귀")
    if not args.no_plot:
        _, log2 = run(args.push, False)
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
        ax[0].plot(log["t"], th, label="LQR ankle")
        ax[0].plot(log2["t"], np.degrees(log2["theta"]), label="PID hold (no LQR)")
        ax[0].axvspan(1.0, 1.1, color="r", alpha=0.2, label="push")
        ax[0].set_ylabel("lean theta [deg]"); ax[0].legend(); ax[0].set_title(f"push {args.push:.0f} N for 0.1 s")
        ax[1].plot(log["t"], log["u"], label="LQR ankle torque (sum)")
        ax[1].plot(log2["t"], log2["u"], label="PID ankle torque (sum)")
        ax[1].set_ylabel("torque [Nm]"); ax[1].set_xlabel("time [s]"); ax[1].legend()
        fig.tight_layout(); fig.savefig("lqr_result.png", dpi=100)
        print("그래프 저장: lqr_result.png")


if __name__ == "__main__":
    main()
