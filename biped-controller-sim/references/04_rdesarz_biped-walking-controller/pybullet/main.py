"""rdesarz/biped-walking-controller 의 examples/example_4_physics_simulation.py 를
노트북에서 바로 돌릴 수 있게 다시 짠 실행 파일.

원본에서 그대로 쓰는 것 (biped_walking_controller/ 폴더, 수정 없음):
  - preview_control.py : LIPM + ZMP preview control (compute_preview_control_matrices, update_control, compute_zmp_ref)
  - foot.py            : 발자국 순서(compute_steps_sequence), 발 궤적(compute_feet_trajectories, Bezier 곡선)
  - state_machine.py   : foot.py 가 import 하는 Foot 정의
바꾼 것 (원본은 노트북에서 바로 돌리기 어려움):
  - 원본 로봇은 Talos (talos_data 저장소의 URDF 와 메시 필요) + Pinocchio 로 QP 역기구학
    -> 이 폴더의 단순 이족 로봇(biped_model.py, URDF 자동 생성)과 해석적 역기구학(leg_ik)으로 교체
  - 그 로봇 크기에 맞춰 질량 중심 높이 zc, 발 높이를 바꿈 (아래 PARAMS)
  - 관절 제어는 원본과 같이 PyBullet POSITION_CONTROL

실행:
    python main.py            # 창 없이 실행, rdesarz_result.png 저장
    python main.py --gui      # PyBullet 창으로 보기
    python main.py --steps 10 --stride 0.08
"""
import argparse
import math
import os
import sys

import numpy as np
import pybullet as p

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from biped_walking_controller.foot import (   # noqa: E402  (원본 그대로)
    compute_feet_trajectories, BezierCurveFootPathGenerator, compute_steps_sequence)
from biped_walking_controller.preview_control import (   # noqa: E402  (원본 그대로)
    PreviewControllerParams, compute_preview_control_matrices, update_control, compute_zmp_ref,
    cubic_spline_interpolation)
from biped_model import Biped, HIP_Y, HIP_Z, ANKLE_H, leg_ik   # noqa: E402  (Talos + Pinocchio 대신)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gui", action="store_true")
    ap.add_argument("--steps", type=int, default=15, help="걸음 수 (원본 15). 짝수면 마지막에 두 발이 나란히 모이지 않음 (원본 foot.py 동작)")
    ap.add_argument("--stride", type=float, default=0.1, help="보폭 [m] (원본 0.1)")
    ap.add_argument("--foot-height", type=float, default=0.03, help="발 높이 [m] (원본 Talos 는 0.01)")
    ap.add_argument("--t-ss", type=float, default=0.8, help="한 발 지지 시간 [s] (원본 0.8)")
    ap.add_argument("--t-ds", type=float, default=0.3, help="두 발 지지 시간 [s] (원본 0.3)")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    # ---- 원본 get_standard_params() 의 값. zc 만 이 로봇에 맞게 아래에서 다시 정함 ----
    dt, t_init, t_end, t_preview = 1.0 / 1000.0, 2.0, 0.4, 1.6
    t_ss, t_ds = args.t_ss, args.t_ds

    robot = Biped(gui=args.gui, dt=dt)
    # 원본처럼 PyBullet 위치 제어를 쓴다 (biped_model 은 기본으로 모터를 꺼 두므로 다시 켬)
    def apply_q(q):
        p.setJointMotorControlArray(robot.id, robot.jids, p.POSITION_CONTROL, targetPositions=list(q),
                                    forces=[200.0] * 10, positionGains=[0.3] * 10, velocityGains=[1.0] * 10)

    c0 = robot.com()
    base0 = robot.base_state()[0]
    zc = c0[2]                                 # 원본 Talos 는 0.89 m
    pelvis_h = base0[2]
    ctrler_params = PreviewControllerParams(zc=zc, g=9.81, Qe=1.0, Qx=np.zeros((3, 3)), R=1e-6,
                                            n_preview_steps=int(round(t_preview / dt)))
    ctrler_mat = compute_preview_control_matrices(ctrler_params, dt)

    # 원본은 발바닥 높이를 z = 0 으로 두고 발 궤적을 만든다 (Bezier 곡선의 z 제어점이 0 기준 절댓값).
    # 그래서 발바닥 위치(z = 0)로 계획하고, 관절 명령을 만들 때 발목 높이 ANKLE_H 를 더한다.
    lf0 = np.array([0.0, HIP_Y, 0.0])
    rf0 = np.array([0.0, -HIP_Y, 0.0])
    feet_mid = 0.5 * (lf0 + rf0)
    com_initial_target = np.array([feet_mid[0], feet_mid[1], zc])
    # 몸통 위치 = 질량 중심 목표 - com_offset. 처음 자세에서 명령이 튀지 않도록 처음 몸통 위치를 기준으로 잡는다.
    com_offset = feet_mid[:2] - base0[:2]

    def command(com_xy, lf, rf):
        pelvis = np.asarray(com_xy) - com_offset
        q = []
        for f, sg in ((lf, 1.0), (rf, -1.0)):
            hip = np.array([pelvis[0], pelvis[1] + sg * HIP_Y, pelvis_h + HIP_Z])
            ankle = np.asarray(f) + np.array([0.0, 0.0, ANKLE_H])
            q += leg_ik(*(ankle - hip))
        apply_q(q)

    # ---- 원본: 1초 동안 질량 중심을 발 사이에 붙잡는 안정화 단계 ----
    x_k = np.array([0.0, com_initial_target[0], 0.0, 0.0])
    y_k = np.array([0.0, com_initial_target[1], 0.0, 0.0])
    for _ in range(math.ceil(1.0 / dt)):
        zmp_ref_horizon = np.ones((ctrler_params.n_preview_steps - 1, 2)) * feet_mid[0:2]
        _, x_k, y_k = update_control(ctrler_mat, feet_mid[0:2], zmp_ref_horizon, x_k.copy(), y_k.copy())
        command([x_k[1], y_k[1]], lf0, rf0)
        robot.step()

    # ---- 원본: 발자국, 발 궤적, ZMP 기준값 ----
    steps_pose, steps_ids = compute_steps_sequence(rf_initial_pose=rf0, lf_initial_pose=lf0,
                                                   n_steps=args.steps, l_stride=args.stride)
    t, lf_path, rf_path, phases = compute_feet_trajectories(
        rf_initial_pose=rf0, lf_initial_pose=lf0, n_steps=args.steps, steps_pose=steps_pose,
        t_ss=t_ss, t_ds=t_ds, t_init=t_init, t_final=t_end, dt=dt,
        traj_generator=BezierCurveFootPathGenerator(args.foot_height))
    zmp_ref = compute_zmp_ref(t=t, com_initial_pose=com_initial_target[0:2], steps=steps_pose[:, 0:2],
                              ss_t=t_ss, ds_t=t_ds, t_init=t_init, t_final=t_end,
                              interp_fn=cubic_spline_interpolation)
    zmp_padded = np.vstack([zmp_ref, np.repeat(zmp_ref[-1][None, :], ctrler_params.n_preview_steps, axis=0)])

    # ---- 원본: 걷기 단계 ----
    log = {"t": [], "com_ref": [], "com_pb": [], "zmp_ref": []}
    fell_at = None
    for k, _ in enumerate(phases[:-2]):
        zmp_ref_horizon = zmp_padded[k + 1: k + ctrler_params.n_preview_steps]
        _, x_k, y_k = update_control(ctrler_mat, zmp_padded[k], zmp_ref_horizon, x_k.copy(), y_k.copy())
        command([x_k[1], y_k[1]], lf_path[k], rf_path[k])
        robot.step()
        if k % 10 == 0:
            log["t"].append(t[k]); log["com_ref"].append([x_k[1], y_k[1]])
            log["com_pb"].append(robot.com()[:2]); log["zmp_ref"].append(zmp_padded[k])
        if fell_at is None and robot.fallen():
            fell_at = t[k]
            break

    feet_end = [p.getLinkState(robot.id, robot.foot[s])[4][0] for s in "LR"]
    base = robot.base_state()[0]
    robot.close()
    cr, cp_ = np.array(log["com_ref"]), np.array(log["com_pb"])
    print(f"걸음 수 {args.steps}, 보폭 {args.stride} m, zc = {zc:.3f} m, preview 구간 {t_preview} s")
    print(f"계획 발 위치 최종 x = {steps_pose[-1][0]:.3f} m, 시뮬레이션 발목 x = 왼 {feet_end[0]:.3f}, 오른 {feet_end[1]:.3f} m")
    print(f"계획 질량 중심과 시뮬레이션 질량 중심 차이 최대: x {np.abs(cr[:, 0] - cp_[:, 0]).max() * 100:.1f} cm, "
          f"y {np.abs(cr[:, 1] - cp_[:, 1]).max() * 100:.1f} cm")
    print(f"몸통 최종 위치 x = {base[0]:.3f} m")
    print("결과: 넘어짐 (t = %.2f s)" % fell_at if fell_at else "결과: 넘어지지 않고 끝까지 걸음")
    if not args.no_plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        zr = np.array(log["zmp_ref"])
        fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
        for i, n in enumerate("xy"):
            ax[i].plot(log["t"], zr[:, i], "k--", label="ZMP ref")
            ax[i].plot(log["t"], cr[:, i], label="CoM (preview control)")
            ax[i].plot(log["t"], cp_[:, i], label="CoM in PyBullet")
            ax[i].set_ylabel(f"{n} [m]"); ax[i].legend(fontsize=8)
        ax[0].set_title("rdesarz preview control on simple biped"); ax[1].set_xlabel("time [s]")
        fig.tight_layout(); fig.savefig("rdesarz_result.png", dpi=100)
        print("그래프 저장: rdesarz_result.png")


if __name__ == "__main__":
    main()
