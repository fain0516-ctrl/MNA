"""Einsbon/bipedal-robot-walking-simulation 의 walking_simulation_example.py 를
노트북에서 바로 돌릴 수 있게 고친 실행 파일.

원본과 같은 것: 로봇(humanoid_leg_12dof.8.urdf), 보행 점 생성과 역기구학(walkGenerator.py),
              모터 제어(motorController.py, PyBullet POSITION_CONTROL), 보행 파라미터, 실행 순서
바꾼 것:
  - 창 없이 실행 옵션 (--gui 없으면 DIRECT)
  - 원본 마지막의 Enter 키 대기 무한 루프 대신, 정해진 횟수만 걷고 끝냄
  - 보행 점 3D 그래프(plt.show)를 창 대신 파일로 저장
  - 넘어짐 판정, 이동 거리 출력

실행:
    python main.py            # 창 없이 실행
    python main.py --gui      # PyBullet 창으로 보기 (원본처럼 실시간에 가깝게 보려면 --realtime 추가)
    python main.py --cycles 8 --stride 70
"""
import argparse
import os
import time

import numpy as np
import pybullet as p
import pybullet_data

HERE = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, HERE)
import motorController   # noqa: E402  (원본 모듈, np.float 만 수정)
import walkGenerator     # noqa: E402  (원본 모듈 그대로)

# motor parameters (원본 값)
motor_kp = 0.5
motor_kd = 0.5
motor_torque = 1.5
motor_max_velocity = 5.0
# physics parameters (원본 값)
fixedTimeStep = 1. / 2000
numSolverIterations = 200


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gui", action="store_true")
    ap.add_argument("--realtime", action="store_true", help="GUI 에서 실제 시간 속도로 재생")
    ap.add_argument("--cycles", type=int, default=4, help="오른발+왼발 반복 횟수 (원본 4)")
    ap.add_argument("--stride", type=float, default=90, help="보폭 [mm] (원본 90)")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    physicsClient = p.connect(p.GUI if args.gui else p.DIRECT)
    p.setTimeStep(fixedTimeStep)
    p.setPhysicsEngineParameter(numSolverIterations=numSolverIterations)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, 0)
    if args.gui:
        p.resetDebugVisualizerCamera(cameraDistance=1, cameraYaw=10, cameraPitch=-0, cameraTargetPosition=[0.4, 0, 0.1])
    p.loadURDF("plane.urdf")
    robotID = p.loadURDF(os.path.join(HERE, "humanoid_leg_12dof.8.urdf"), [0, 0, 0.31],
                         p.getQuaternionFromEuler([0, 0, 0]), useFixedBase=False)

    motors = motorController.MotorController(robotID, physicsClient, fixedTimeStep, motor_kp, motor_kd,
                                             motor_torque, motor_max_velocity)
    # [추가] GUI 실시간 재생 옵션: stepSimulation 을 감싸서 잠깐씩 쉰다
    if args.gui and args.realtime:
        _step = p.stepSimulation
        p.stepSimulation = lambda *a, **k: (_step(*a, **k), time.sleep(fixedTimeStep))

    walk = walkGenerator.WalkGenerator()
    walk.setWalkParameter(bodyMovePoint=8, legMovePoint=8, height=50, stride=args.stride, sit=50, swayBody=30,
                          swayFoot=0, bodyPositionForwardPlus=5, swayShift=3, liftPush=0.5, landPull=0.7,
                          timeStep=0.06, damping=0.0, incline=0.0)
    walk.generate()
    walk.inverseKinematicsAll()

    if not args.no_plot:   # [변경] walk.showGaitPoint3D() (창) 대신 파일로 저장
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.show = lambda: plt.savefig(os.path.join(HERE, "einsbon_gait_points.png"), dpi=90)
        walk.showGaitPoint3D()
        print("보행 점 그래프 저장: einsbon_gait_points.png")

    actionTime = walk._timeStep
    p.setGravity(0, 0, -9.8)
    p.setRealTimeSimulation(0)
    motors.setMotorsAngleInFixedTimestep(walk.walkAnglesStartRight[0], 2, 0)
    for _ in range(int(1 / fixedTimeStep)):     # rest 1 second
        p.stepSimulation()

    start = np.array(p.getBasePositionAndOrientation(robotID)[0])
    walkPointNum = walk._bodyMovePoint + walk._legMovePoint
    min_z = start[2]
    for i in range(walkPointNum):
        motors.setMotorsAngleInFixedTimestep(walk.walkAnglesStartLeft[i], actionTime, 0)
    for _ in range(args.cycles):
        for i in range(np.size(walk.walkAnglesWalkingRight, 0)):
            motors.setMotorsAngleInFixedTimestep(walk.walkAnglesWalkingRight[i], actionTime, 0)
        for i in range(np.size(walk.walkAnglesWalkingLeft, 0)):
            motors.setMotorsAngleInFixedTimestep(walk.walkAnglesWalkingLeft[i], actionTime, 0)
        min_z = min(min_z, p.getBasePositionAndOrientation(robotID)[0][2])
    for i in range(walkPointNum):
        motors.setMotorsAngleInFixedTimestep(walk.walkAnglesEndRight[i], actionTime, 0)
    for _ in range(int(1 / fixedTimeStep)):     # rest 1 second
        p.stepSimulation()

    pos, orn = p.getBasePositionAndOrientation(robotID)
    rpy = np.degrees(p.getEulerFromQuaternion(orn))
    p.disconnect()
    planned = (2 * args.cycles + 1) * args.stride / 1000.0
    print(f"반복 {args.cycles} 회, 보폭 {args.stride} mm")
    print(f"몸통 이동: x {pos[0] - start[0]:.3f} m, y {pos[1] - start[1]:.3f} m  (보폭 x 걸음 수로 어림한 값 약 {planned:.2f} m)")
    print(f"마지막 자세 roll/pitch/yaw [deg] = {np.round(rpy, 1)}, 몸통 높이 {pos[2]:.3f} m (처음 {start[2]:.3f} m)")
    fallen = pos[2] < 0.5 * start[2] or abs(rpy[0]) > 45 or abs(rpy[1]) > 45
    print("결과: 넘어짐" if fallen else "결과: 넘어지지 않고 끝까지 걸음")


if __name__ == "__main__":
    main()
