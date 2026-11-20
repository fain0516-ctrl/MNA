"""tayalmanan28/Biped-Pybullet 의 main.py 를 노트북에서 바로 돌릴 수 있게 고친 실행 파일.

원본과 같은 것: 동작 함수(stand, squat, jump, torsoTwist, walk)의 내용, 로봇, 역기구학, preview control (원본 모듈 그대로)
바꾼 것:
  - 원본은 while True 로 끝없이 돈다 -> --time 초가 지나면 멈추고 결과를 출력
  - 창 없이 실행(--gui 없을 때). 이때 GUI 슬라이더(Incline, Stride, Step height) 대신 명령행 값 사용
  - 넘어짐 판정, 몸통 위치 기록, 그래프 파일 저장

실행:
    python main.py                         # 창 없이 walk 10 초
    python main.py --gui                   # 창으로 보기 (슬라이더로 경사, 보폭, 발 높이 조절 가능)
    python main.py --action squat --time 5
    python main.py --stride 0.15 --step-height 0.05
"""
import argparse
import os

import numpy as np
import pybullet as p

os.chdir(os.path.dirname(os.path.abspath(__file__)))   # biped.urdf, meshes/ 를 상대 경로로 찾음

from robot import Biped                   # noqa: E402  (원본 모듈, gui 옵션만 추가)
from walking import PreviewControl        # noqa: E402  (원본 모듈)

CFG = {"gui": False, "params": None, "max_steps": 2400}
LOG = []


class _Stop(Exception):
    pass


def make_biped():
    """[추가] 원본의 Biped() 대신 호출. oneStep 을 감싸서 시간 제한과 기록을 넣는다."""
    biped = Biped(gui=CFG["gui"], params=CFG["params"])
    orig_step = biped.oneStep

    def step():
        orig_step()
        LOG.append(biped.getRobotPosition())
        if len(LOG) >= CFG["max_steps"]:
            raise _Stop()
    biped.oneStep = step
    return biped


# ======== 아래 함수들은 원본 main.py 의 내용 그대로 (Biped() -> make_biped() 만 바꿈) ========
def stand():
    biped = make_biped()
    CoM_height = 0.45

    targetRPY = [0.0, 0.0, 0.0]
    targetPosL = [0.0, 0.065, -CoM_height]
    targetPosR = [0.0, -0.065, -CoM_height]
    biped.positionInitialize(initializeTime=0.2)

    while True:
        incline = biped.getIncline()
        biped.resetIncline(incline)
        targetRPY[1] = incline

        biped.setLegPositions(targetPosL, targetPosR, targetRPY)
        biped.oneStep()


def squat():
    biped = make_biped()
    CoM_height = 0.45

    targetRPY = [0.0, 0.0, 0.0]
    targetPosL = [0.0, 0.065, -CoM_height]
    targetPosR = [0.0, -0.065, -CoM_height]
    biped.positionInitialize(initializeTime=0.1)

    dp = 0.002
    while True:
        incline = biped.getIncline()
        biped.resetIncline(incline)
        targetRPY[1] = incline

        for _ in range(100):
            biped.setLegPositions(targetPosL, targetPosR, targetRPY)
            biped.oneStep()
            targetPosL[2] += dp
            targetPosR[2] += dp

        for _ in range(100):
            biped.setLegPositions(targetPosL, targetPosR, targetRPY)
            biped.oneStep()
            targetPosL[2] -= dp
            targetPosR[2] -= dp


def jump(withTorsoTwist=False):
    biped = make_biped()
    CoM_height = 0.45

    targetRPY = [0.0, 0.0, 0.0]
    targetPosL = [0.0, 0.065, -CoM_height]
    targetPosR = [0.0, -0.065, -CoM_height]
    biped.positionInitialize(initializeTime=0.1)

    dp = 0.0025
    dRPY = 0.0065
    while True:
        incline = biped.getIncline()
        biped.resetIncline(incline)
        targetRPY[1] = incline

        for _ in range(60):
            biped.setLegPositions(targetPosL, targetPosR, targetRPY)
            biped.oneStep()
            targetPosL[2] += dp
            targetPosR[2] += dp
            if withTorsoTwist:
                targetRPY[2] += dRPY

        for _ in range(60):
            biped.setLegPositions(targetPosL, targetPosR, targetRPY)
            biped.oneStep()
            targetPosL[2] -= dp
            targetPosR[2] -= dp
            if withTorsoTwist:
                targetRPY[2] -= dRPY


def torsoTwist():
    biped = make_biped()
    CoM_height = 0.45

    targetRPY = [0.0, 0.0, -0.25]
    targetPosL = [0.0, 0.065, -CoM_height]
    targetPosR = [0.0, -0.065, -CoM_height]
    biped.positionInitialize(initializeTime=0.1)

    dp = 0.005
    while True:
        incline = biped.getIncline()
        biped.resetIncline(incline)
        targetRPY[1] = incline

        for _ in range(100):
            biped.setLegPositions(targetPosL, targetPosR, targetRPY)
            biped.oneStep()
            targetRPY[2] += dp

        for _ in range(100):
            biped.setLegPositions(targetPosL, targetPosR, targetRPY)
            biped.oneStep()
            targetRPY[2] -= dp


def walk():
    biped = make_biped()
    # CoM_height = 0.45
    # CoM_to_body = np.array([0.0, 0.0, 0.0])

    targetRPY = [0.0, 0.0, 0.0]
    pre = PreviewControl(dt=1./240., Tsup_time=0.3, Tdl_time=0.1, previewStepNum=190)
    biped.positionInitialize(initializeTime=0.2)
    CoM_trajectory = np.empty((0, 3), float)

    trjR_log = np.empty((0, 3), float)
    trjL_log = np.empty((0, 3), float)
    supPoint = np.array([0., 0.065])

    while True:
        incline = biped.getIncline()
        biped.resetIncline(incline)
        targetRPY[1] = incline

        stepHeight = biped.getStepHeight()

        # Generates one cycle trajectory
        CoM_trj, footTrjL, footTrjR = pre.footPrintAndCoM_trajectoryGenerator(inputTargetZMP=supPoint,
                                                                              inputFootPrint=supPoint,
                                                                              stepHeight=stepHeight)
        CoM_trajectory = np.vstack((CoM_trajectory, CoM_trj))
        trjR_log = np.vstack((trjR_log, footTrjR))
        trjL_log = np.vstack((trjL_log, footTrjL))

        for j in range(len(CoM_trj)):
            targetPosR = footTrjR[j] - CoM_trj[j]
            targetPosL = footTrjL[j] - CoM_trj[j]

            biped.setLegPositions(targetPosL, targetPosR, targetRPY)
            biped.oneStep()

        supPoint[0] += biped.getStride()
        supPoint[1] = -supPoint[1]


# ======== 원본 함수 끝 ========


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", default="walk", help="walk, stand, squat, jump_w_Twist, jump_wo_Twist, torsoTwist")
    ap.add_argument("--gui", action="store_true")
    ap.add_argument("--time", type=float, default=10.0, help="시뮬레이션 시간 [s] (원본은 무한 반복)")
    ap.add_argument("--incline", type=float, default=0.0, help="바닥 경사 [rad] (창 없을 때)")
    ap.add_argument("--stride", type=float, default=0.1, help="보폭 [m] (창 없을 때)")
    ap.add_argument("--step-height", type=float, default=0.04, help="발 높이 [m] (창 없을 때)")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()
    CFG["gui"] = args.gui
    CFG["params"] = {"incline": args.incline, "stride": args.stride, "step_height": args.step_height}
    CFG["max_steps"] = int(args.time * 240)
    actions = {"walk": walk, "squat": squat, "torsoTwist": torsoTwist, "stand": stand,
               "jump_w_Twist": lambda: jump(withTorsoTwist=True), "jump_wo_Twist": lambda: jump(withTorsoTwist=False)}
    try:
        actions.get(args.action, stand)()
    except _Stop:
        pass
    rpy = p.getEulerFromQuaternion(p.getBasePositionAndOrientation(1)[1])   # 로봇 id = 1 (plane = 0)
    p.disconnect()
    base = np.array(LOG)
    fell = np.where(base[:, 2] < 0.3)[0]
    print(f"동작 {args.action}, {args.time} 초")
    print(f"몸통 최종 위치 x = {base[-1, 0]:.3f} m, y = {base[-1, 1]:.3f} m, 높이 {base[-1, 2]:.3f} m")
    print(f"마지막 자세 roll/pitch/yaw [deg] = {np.round(np.degrees(rpy), 1)}")
    print("결과: 넘어짐 (t = %.2f s)" % (fell[0] / 240) if len(fell) else "결과: 넘어지지 않음")
    if not args.no_plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        t = np.arange(len(base)) / 240.0
        fig, ax = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
        for i, n in enumerate("xyz"):
            ax[i].plot(t, base[:, i]); ax[i].set_ylabel(f"base {n} [m]")
        ax[0].set_title(f"tayalmanan28/Biped-Pybullet: {args.action}"); ax[2].set_xlabel("time [s]")
        fig.tight_layout(); fig.savefig(f"tayal_{args.action}.png", dpi=100)
        print(f"그래프 저장: tayal_{args.action}.png")


if __name__ == "__main__":
    main()
