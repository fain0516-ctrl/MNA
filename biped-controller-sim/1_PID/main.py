"""1_PID: 관절 PID 토크 제어로 이족 로봇의 자세 동작(앉았다 일어서기 -> 좌우 체중 이동 -> 한 발 들기)을 따라가게 한다.

실행:
    python main.py            # 화면 없이 실행 (결과 그래프 pid_result.png 저장)
    python main.py --gui      # PyBullet 창으로 보기
"""
import argparse
import math

import numpy as np
import pybullet as p

from biped_model import Biped, HIP_Y, leg_ik


class PID:
    """벡터형 PID. 미분항은 측정값(관절 속도)으로 계산해 기준값이 급변할 때 튀지 않게 한다."""

    def __init__(self, kp, ki, kd, dt, i_limit=50.0):
        self.kp, self.ki, self.kd, self.dt = kp, ki, kd, dt
        self.i_limit = i_limit
        self.integral = None

    def __call__(self, q_ref, q, dq, dq_ref=None):
        e = q_ref - q
        if self.integral is None:
            self.integral = np.zeros_like(e)
        self.integral = np.clip(self.integral + e * self.dt, -self.i_limit, self.i_limit)  # anti-windup
        de = (dq_ref if dq_ref is not None else 0.0) - dq
        return self.kp * e + self.ki * self.integral + self.kd * de


# 관절별 이득: [hip_roll, hip_pitch, knee, ankle_pitch, ankle_roll]
# 발목 관절은 뒤에 달린 링크(발)가 가벼워서 이득을 낮게 둔다. 너무 크면 시뮬레이션이 발산한다.
KP = np.array([400.0, 400.0, 400.0, 200.0, 200.0])
KI = np.array([200.0, 200.0, 200.0, 100.0, 100.0])
KD = np.array([6.0, 6.0, 6.0, 0.6, 0.6])
# 한 발로 서려면 전체 질량 중심이 왼발 위에 와야 한다. 오른다리가 남아 있으므로
# 몸통은 고관절 간격(HIP_Y)보다 조금 더 옮긴다.
SHIFT = 1.15 * HIP_Y
# 바깥쪽 루프: 몸통 roll 각도를 보고 hip_roll 기준값을 보정하는 비례(P) 제어.
# 0 으로 두면(--no-balance) 관절 PID 만 쓰는 경우와 비교할 수 있다.
# 0.5 근처가 이 모델에서 가장 덜 흔들렸고, 1.0 이상이면 발산해서 넘어졌다.
K_ROLL = 0.5


def smooth(a, b, s):
    """0..1 구간에서 부드럽게(코사인) a -> b."""
    s = min(max(s, 0.0), 1.0)
    return a + (b - a) * (1 - math.cos(math.pi * s)) / 2


def reference(t, h0):
    """시간 t 에서의 (몸통 높이, 몸통 좌우 이동량, 오른발 들어올림 높이)."""
    dy = SHIFT
    if t < 1.0:                       # 서 있기
        return h0, 0.0, 0.0
    if t < 5.0:                       # 앉았다 일어서기 2회 (6 cm)
        return h0 - 0.06 * (1 - math.cos(2 * math.pi * (t - 1.0) / 2.0)) / 2, 0.0, 0.0
    if t < 7.5:                       # 몸통을 왼발 위로 천천히 이동
        return h0, smooth(0.0, dy, (t - 5.0) / 2.5), 0.0
    if t < 8.0:                       # 흔들림이 가라앉을 때까지 대기
        return h0, dy, 0.0
    if t < 9.0:                       # 오른발 4 cm 들기
        return h0, dy, smooth(0.0, 0.04, (t - 8.0) / 1.0)
    if t < 10.0:                      # 한 발로 서 있기
        return h0, dy, 0.04
    if t < 11.0:                      # 오른발 내리기
        return h0, dy, smooth(0.04, 0.0, (t - 10.0) / 1.0)
    if t < 13.0:                      # 가운데로 복귀
        return h0, smooth(dy, 0.0, (t - 11.0) / 2.0), 0.0
    return h0, 0.0, 0.0


def joint_reference(h, dy, lift):
    # 몸통이 +dy 만큼 옮겨가면 발은 몸통 기준으로 -dy 에 있다.
    qL = leg_ik(0.0, -dy, -h)
    qR = leg_ik(0.0, -dy, -(h - lift))
    return np.array(qL + qR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gui", action="store_true", help="PyBullet 창 띄우기")
    ap.add_argument("--time", type=float, default=14.0, help="시뮬레이션 시간 [s]")
    ap.add_argument("--no-plot", action="store_true", help="그래프 저장 안 함")
    ap.add_argument("--no-balance", action="store_true", help="몸통 roll 보정(바깥쪽 루프) 끄기")
    args = ap.parse_args()

    robot = Biped(gui=args.gui)
    pid = PID(np.tile(KP, 2), np.tile(KI, 2), np.tile(KD, 2), robot.dt)
    h0 = robot.stand_height
    n = int(args.time / robot.dt)
    k_roll = 0.0 if args.no_balance else K_ROLL
    log_t, log_ref, log_q, log_z, log_roll = [], [], [], [], []
    q_prev_ref = None
    fell_at = None
    for k in range(n):
        t = k * robot.dt
        q_ref = joint_reference(*reference(t, h0))
        roll = robot.base_state()[1][0]
        q_ref[[0, 5]] += k_roll * roll          # 바깥쪽 P 루프 (몸통 roll -> hip_roll 기준값)
        dq_ref = np.zeros_like(q_ref) if q_prev_ref is None else (q_ref - q_prev_ref) / robot.dt
        q_prev_ref = q_ref
        q, dq = robot.joint_state()
        robot.apply_torque(pid(q_ref, q, dq, dq_ref))
        robot.step()
        if args.gui:
            import time; time.sleep(robot.dt)  # 실제 시간 속도로 보기
        if k % 10 == 0:
            log_t.append(t); log_ref.append(q_ref); log_q.append(q)
            log_z.append(p.getLinkState(robot.id, robot.foot["R"])[0][2])
            log_roll.append(roll)
        if fell_at is None and robot.fallen():
            fell_at = t
    robot.close()

    ref, q = np.array(log_ref), np.array(log_q)
    rms = np.sqrt(np.mean((ref - q) ** 2, axis=0))
    print(f"관절별 추종 오차 RMS [deg]: {np.round(np.degrees(rms), 2)}")
    print(f"최대 RMS = {np.degrees(rms.max()):.2f} deg")
    late = log_roll[int(8 / (10 * robot.dt)):]
    if late:
        print(f"한 발 들기 이후(8 s~) 몸통 roll 최대 = {np.degrees(np.max(np.abs(late))):.1f} deg")
    print("결과: 넘어짐 (t = %.2f s)" % fell_at if fell_at else "결과: 넘어지지 않고 모든 동작 완료")

    if not args.no_plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(4, 1, figsize=(9, 10), sharex=True)
        for i, name in [(2, "L knee"), (7, "R knee")]:
            ax[0].plot(log_t, np.degrees(ref[:, i]), "--", label=name + " ref")
            ax[0].plot(log_t, np.degrees(q[:, i]), label=name)
        ax[0].set_ylabel("angle [deg]"); ax[0].legend(); ax[0].set_title("PID joint tracking")
        for i, name in [(0, "L hip_roll"), (5, "R hip_roll")]:
            ax[1].plot(log_t, np.degrees(ref[:, i]), "--", label=name + " ref")
            ax[1].plot(log_t, np.degrees(q[:, i]), label=name)
        ax[1].set_ylabel("angle [deg]"); ax[1].legend()
        ax[2].plot(log_t, log_z); ax[2].set_ylabel("R foot height [m]")
        ax[3].plot(log_t, np.degrees(log_roll)); ax[3].set_ylabel("torso roll [deg]"); ax[3].set_xlabel("time [s]")
        fig.tight_layout(); fig.savefig("pid_result.png", dpi=100)
        print("그래프 저장: pid_result.png")


if __name__ == "__main__":
    main()
