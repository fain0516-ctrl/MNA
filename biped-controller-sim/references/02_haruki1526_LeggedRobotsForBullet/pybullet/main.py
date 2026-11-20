"""haruki1526/LeggedRobotsForBullet 의 bipedal/example_preview_control.py 를
노트북에서 바로 돌릴 수 있게 고친 실행 파일.

원본과 같은 것: 로봇(URDF), 역기구학, ZMP preview control, 발 궤적, 관절 위치 제어 (모두 원본 모듈 그대로 사용)
바꾼 것: 창 없이 실행 옵션, 걸음 수 지정, 넘어짐 판정, 결과 수치 출력, 그래프를 창 대신 파일로 저장

실행:
    python main.py              # 창 없이 20 걸음, haruki_result.png 저장
    python main.py --gui        # PyBullet 창으로 보기
    python main.py --cycles 50  # 원본 예제와 같은 50 걸음
"""
import argparse
import os

import numpy as np
import pybullet as pb

os.chdir(os.path.dirname(os.path.abspath(__file__)))   # urdf/ 와 meshes/ 를 상대 경로로 찾기 때문

from robot import Bipedal                      # noqa: E402  (원본 모듈)
from walking_generator import PreviewControl   # noqa: E402  (원본 모듈)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gui", action="store_true")
    ap.add_argument("--cycles", type=int, default=20, help="걸음 수 (원본 예제는 50)")
    ap.add_argument("--stride", type=float, default=0.1, help="보폭 [m] (원본 0.1)")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    # ---- 여기부터 원본 example_preview_control.py 와 같은 흐름 ----
    bipedal = Bipedal(gui=args.gui)
    targetRPY = [0.0, 0.0, 0.0]
    pre = PreviewControl(Tsup_time=0.3, Tdl_time=0.1, previewStepNum=190)
    bipedal.positionInitialize(initializeTime=0.2)
    CoMTrajectory = np.empty((0, 3), float)
    supPoint = np.array([0., 0.065])
    base_log = []
    fell_at = None
    for w in range(args.cycles):
        comTrj, footTrjL, footTrjR = pre.footPrintAndCOMtrajectoryGenerator(inputTargetZMP=supPoint, inputFootPrint=supPoint)
        CoMTrajectory = np.vstack((CoMTrajectory, comTrj))
        for i in range(len(comTrj)):
            targetPositionR = footTrjR[i] - comTrj[i]
            targetPositionL = footTrjL[i] - comTrj[i]
            PosR = bipedal.inverseKinematics(targetPositionR, targetRPY, bipedal.R)
            PosL = bipedal.inverseKinematics(targetPositionL, targetRPY, bipedal.L)
            bipedal.setLeftLegJointPositions(PosL)
            bipedal.setRightLegJointPositions(PosR)
            bipedal.oneStep()
            pos = bipedal.getRobotPosition()
            base_log.append(pos)
            # [추가] 넘어짐 판정
            if fell_at is None and pos[2] < 0.3:
                fell_at = w
        supPoint[0] += args.stride
        supPoint[1] = -supPoint[1]
    # ---- 원본 흐름 끝 ----

    base = np.array(base_log)
    rpy = bipedal.getEuler()
    bipedal.disconnect()
    planned = CoMTrajectory[-1, 0]
    print(f"걸음 수 {args.cycles}, 보폭 {args.stride} m")
    print(f"계획한 질량 중심 최종 x = {planned:.3f} m, 시뮬레이션 몸통 최종 x = {base[-1, 0]:.3f} m, 높이 {base[-1, 2]:.3f} m")
    print(f"마지막 자세 roll/pitch/yaw [deg] = {np.round(np.degrees(rpy), 1)}")
    print("결과: 넘어짐 (%d 번째 걸음)" % fell_at if fell_at is not None else "결과: 넘어지지 않고 끝까지 걸음")

    if not args.no_plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
        t = np.arange(len(CoMTrajectory)) / 240.0
        ax[0].plot(t, CoMTrajectory[:, 0], label="CoM plan (preview control)")
        ax[0].plot(t, pre.px_ref_log[: len(t)], "k--", label="ZMP ref")
        ax[0].plot(np.arange(len(base)) / 240.0, base[:, 0], label="base x in PyBullet")
        ax[0].set_ylabel("x [m]"); ax[0].legend()
        ax[1].plot(t, CoMTrajectory[:, 1], label="CoM plan")
        ax[1].plot(t, pre.py_ref_log[: len(t)], "k--", label="ZMP ref")
        ax[1].plot(np.arange(len(base)) / 240.0, base[:, 1], label="base y in PyBullet")
        ax[1].set_ylabel("y [m]"); ax[1].set_xlabel("time [s]"); ax[1].legend()
        fig.tight_layout(); fig.savefig("haruki_result.png", dpi=100)
        print("그래프 저장: haruki_result.png")


if __name__ == "__main__":
    main()
