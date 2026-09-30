# Physical AI Training Package (Team Share Edition)

5지 로봇 그리퍼 파지 제어용 SAC-HER 물리 강화학습 독립 실행 패키지입니다.

---

## 1. 디렉토리 구성 (최소 필수 단위)

```
physical_ai_training_pkg/
├── train_massive_curriculum_v6_multicore.py   # 메인 비동기 병렬 학습 스크립트
├── universal_grasp_env.py                     # MuJoCo 촉각/취약물체 물리 환경
├── sts3215_sim2real_env.py                    # Sim-to-Real 래퍼 (Admittance + TDPA + FSM)
├── train_sac_her.py                           # 신경망 구조 (SACActor 정의)
├── requirements.txt                           # 최소 의존성 패키지 목록
├── mcp_joint_control/                         # 하위 제어기 및 모터 통신 프로토콜 패키지
│   ├── control/                               # Admittance, TDPA, Grasp FSM
│   └── hardware/                              # STS3215 시리얼 프로토콜
└── stl/                                       # MuJoCo 손가락 링크 메쉬 파일
    ├── proximal_phalanx.stl
    ├── middle_phalanx.stl
    └── distal_phalanx.stl
```

---

## 2. 의존성 설치

### (1) NVIDIA RTX 4090 / GPU 환경 (권장: CUDA 12.1+)
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install mujoco "numpy<2.0.0"
```

### (2) 일반 CPU 환경
```bash
pip install -r requirements.txt
```

---

## 3. 학습 실행

```bash
python train_massive_curriculum_v6_multicore.py
```

* **동작 원리**:
  * 호스트 CPU 코어 수에 맞추어 `max(2, min(14, CPU - 2))`개의 독립 워커 프로세스가 MuJoCo 물리 시뮬레이션을 병렬 수행합니다.
  * CUDA 장치가 감지되면(RTX 4090 등) Actor/Critic 신경망 추론 및 SAC 역전파(Backpropagation) 연산이 GPU VRAM으로 자동 가속됩니다.
  * 체크포인트 가중치(`actor_v6_step_*.pth`) 및 최종 가중치가 현재 디렉토리에 자동 저장됩니다.
