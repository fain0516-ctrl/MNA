"""간단한 3D 이족 로봇 모델 (URDF 자동 생성), 역기구학, PyBullet 보조 함수.

다리당 5개 관절: hip_roll, hip_pitch, knee, ankle_pitch, ankle_roll  (총 10 관절)
이 파일은 1_PID, 2_LQR, 3_MPC 폴더에 똑같이 들어 있습니다.
"""
import math
import os
import tempfile

import numpy as np
import pybullet as p
import pybullet_data

# ---- 치수 [m] / 질량 [kg] ----
TORSO_SIZE = (0.16, 0.30, 0.30)
TORSO_MASS = 10.0
HIP_Y = 0.10            # 몸통 중심에서 고관절까지 좌우 거리
HIP_Z = -0.15           # 몸통 중심에서 고관절까지 높이
THIGH = 0.25
SHANK = 0.25
ANKLE_H = 0.05          # 발목 관절에서 발바닥까지 높이
FOOT_SIZE = (0.20, 0.10, 0.03)
FOOT_X = 0.02           # 발 중심의 앞쪽 오프셋
M_THIGH, M_SHANK, M_FOOT, M_SMALL = 0.8, 0.6, 0.6, 0.1

JOINTS = ["hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll"]
SIDES = {"L": 1.0, "R": -1.0}


def _inertia_box(m, sx, sy, sz):
    return (m / 12 * (sy**2 + sz**2), m / 12 * (sx**2 + sz**2), m / 12 * (sx**2 + sy**2))


def _link(name, mass, size, xyz, color):
    ixx, iyy, izz = _inertia_box(mass, *size)
    geo = f'<box size="{size[0]} {size[1]} {size[2]}"/>'
    org = f'<origin xyz="{xyz[0]} {xyz[1]} {xyz[2]}"/>'
    col = "" if size[0] < 0.02 else f"<collision>{org}<geometry>{geo}</geometry></collision>"
    return f"""
  <link name="{name}">
    <inertial>{org}<mass value="{mass}"/>
      <inertia ixx="{ixx}" ixy="0" ixz="0" iyy="{iyy}" iyz="0" izz="{izz}"/></inertial>
    <visual>{org}<geometry>{geo}</geometry><material name="{name}_m"><color rgba="{color}"/></material></visual>
    {col}
  </link>"""


def _joint(name, parent, child, xyz, axis, lim=2.5):
    return f"""
  <joint name="{name}" type="revolute">
    <parent link="{parent}"/><child link="{child}"/>
    <origin xyz="{xyz[0]} {xyz[1]} {xyz[2]}"/><axis xyz="{axis}"/>
    <limit lower="{-lim}" upper="{lim}" effort="300" velocity="30"/>
  </joint>"""


def make_urdf():
    s = '<?xml version="1.0"?>\n<robot name="simple_biped">'
    s += _link("torso", TORSO_MASS, TORSO_SIZE, (0, 0, 0), "0.2 0.4 0.8 1")
    for side, sg in SIDES.items():
        t = side + "_"
        s += _link(t + "hip", M_SMALL, (0.01, 0.01, 0.01), (0, 0, 0), "0.5 0.5 0.5 1")
        s += _link(t + "thigh", M_THIGH, (0.05, 0.05, THIGH), (0, 0, -THIGH / 2), "0.8 0.8 0.8 1")
        s += _link(t + "shank", M_SHANK, (0.05, 0.05, SHANK), (0, 0, -SHANK / 2), "0.7 0.7 0.7 1")
        s += _link(t + "ankle", M_SMALL, (0.01, 0.01, 0.01), (0, 0, 0), "0.5 0.5 0.5 1")
        s += _link(t + "foot", M_FOOT, FOOT_SIZE, (FOOT_X, 0, -ANKLE_H + FOOT_SIZE[2] / 2), "0.9 0.3 0.2 1")
        s += _joint(t + "hip_roll", "torso", t + "hip", (0, sg * HIP_Y, HIP_Z), "1 0 0")
        s += _joint(t + "hip_pitch", t + "hip", t + "thigh", (0, 0, 0), "0 1 0")
        s += _joint(t + "knee", t + "thigh", t + "shank", (0, 0, -THIGH), "0 1 0")
        s += _joint(t + "ankle_pitch", t + "shank", t + "ankle", (0, 0, -SHANK), "0 1 0")
        s += _joint(t + "ankle_roll", t + "ankle", t + "foot", (0, 0, 0), "1 0 0")
    s += "\n</robot>\n"
    path = os.path.join(tempfile.gettempdir(), "simple_biped.urdf")
    with open(path, "w") as f:
        f.write(s)
    return path


def leg_ik(x, y, z):
    """발목 위치 (고관절 기준, 몸통 좌표계, z<0)를 받아 발바닥이 지면과 평행하도록
    [hip_roll, hip_pitch, knee, ankle_pitch, ankle_roll] 를 돌려준다."""
    roll = math.atan2(y, -z)
    r = math.hypot(y, z)
    d = min(math.hypot(x, r), THIGH + SHANK - 1e-4)
    cos_k = (THIGH**2 + SHANK**2 - d**2) / (2 * THIGH * SHANK)
    knee = math.pi - math.acos(max(-1.0, min(1.0, cos_k)))
    alpha = math.atan2(x, r)
    cos_b = (THIGH**2 + d**2 - SHANK**2) / (2 * THIGH * d)
    beta = math.acos(max(-1.0, min(1.0, cos_b)))
    hip_pitch = -(alpha + beta)
    ankle_pitch = -(hip_pitch + knee)
    return [roll, hip_pitch, knee, ankle_pitch, -roll]


class Biped:
    """PyBullet 안의 로봇 하나. 관절 인덱스 관리와 상태 읽기, 토크 입력을 맡는다."""

    def __init__(self, gui=False, dt=1.0 / 1000.0, stand_height=0.43, friction=1.0):
        self.cid = p.connect(p.GUI if gui else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.setTimeStep(dt)
        self.dt = dt
        self.plane = p.loadURDF("plane.urdf")
        p.changeDynamics(self.plane, -1, lateralFriction=friction)
        self.stand_height = stand_height
        z0 = -HIP_Z + stand_height + ANKLE_H
        self.id = p.loadURDF(make_urdf(), [0, 0, z0], useFixedBase=False)
        self.idx = {}
        for j in range(p.getNumJoints(self.id)):
            self.idx[p.getJointInfo(self.id, j)[1].decode()] = j
        self.names = [s + "_" + n for s in SIDES for n in JOINTS]
        self.jids = [self.idx[n] for n in self.names]
        self.foot = {s: self.idx[s + "_ankle_roll"] for s in SIDES}
        for s in SIDES:
            p.changeDynamics(self.id, self.foot[s], lateralFriction=friction)
        # 기본 모터 끄기 -> 토크 제어를 직접 한다
        p.setJointMotorControlArray(self.id, self.jids, p.VELOCITY_CONTROL, forces=[0.0] * len(self.jids))
        q0 = self.stand_pose()
        for j, q in zip(self.jids, q0):
            p.resetJointState(self.id, j, q)

    def stand_pose(self, dx=0.0, dy=0.0):
        """양발을 고관절 바로 아래에 두고 무릎을 굽힌 기본 자세."""
        q = []
        for s, sg in SIDES.items():
            q += leg_ik(-dx, -dy, -self.stand_height)
        return q

    def joint_state(self):
        st = p.getJointStates(self.id, self.jids)
        return np.array([x[0] for x in st]), np.array([x[1] for x in st])

    def apply_torque(self, tau, limit=200.0):
        tau = np.clip(tau, -limit, limit)
        p.setJointMotorControlArray(self.id, self.jids, p.TORQUE_CONTROL, forces=list(tau))
        return tau

    def base_state(self):
        pos, orn = p.getBasePositionAndOrientation(self.id)
        lin, ang = p.getBaseVelocity(self.id)
        rpy = p.getEulerFromQuaternion(orn)
        return np.array(pos), np.array(rpy), np.array(lin), np.array(ang)

    def com(self):
        """전체 질량 중심."""
        m_tot, c = 0.0, np.zeros(3)
        m = p.getDynamicsInfo(self.id, -1)[0]
        c += m * np.array(p.getBasePositionAndOrientation(self.id)[0]); m_tot += m
        for j in range(p.getNumJoints(self.id)):
            m = p.getDynamicsInfo(self.id, j)[0]
            c += m * np.array(p.getLinkState(self.id, j, computeForwardKinematics=True)[0]); m_tot += m
        return c / m_tot

    def total_mass(self):
        return sum(p.getDynamicsInfo(self.id, j)[0] for j in range(-1, p.getNumJoints(self.id)))

    def fallen(self):
        pos, rpy, _, _ = self.base_state()
        return pos[2] < 0.35 or abs(rpy[0]) > 0.8 or abs(rpy[1]) > 0.8

    def step(self):
        p.stepSimulation()

    def close(self):
        p.disconnect(self.cid)
