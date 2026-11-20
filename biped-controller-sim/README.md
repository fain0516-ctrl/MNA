# 이족보행 로봇 제어기 시뮬레이션 (PyBullet): PID → LQR → MPC

PID, LQR, MPC를 순서대로 공부하기 위한 PyBullet 실행 예제와, GitHub에 공개된 이족보행 로봇 제어기 시뮬레이션 저장소 조사 결과를 모은 폴더입니다.

```
biped-controller-sim/
├── survey/                  GitHub 저장소 조사 결과 (2026-11-20)
│   ├── biped_controller_sim_repos.xlsx   전체 목록 1,269개 (★ PyBullet 또는 PID/PD/LQR/MPC 언급 372개)
│   └── summary.md                        스타 수 기준 상위 요약
├── 1_PID/   관절 PID 토크 제어: 앉았다 일어서기 → 체중 이동 → 한 발 들기
├── 2_LQR/   LQR 발목 토크 균형 제어: 몸통을 밀었을 때 버티기
└── 3_MPC/   LIPM + ZMP MPC 로 질량 중심 궤적 생성 → 역기구학 → 관절 PID 로 걷기
```

세 폴더는 서로 독립적입니다. 폴더 하나만 내려받아도 실행됩니다 (공통 로봇 모델 `biped_model.py`가 폴더마다 들어 있습니다).

## 빠른 실행 (노트북)

```bash
cd biped-controller-sim/1_PID        # 또는 2_LQR, 3_MPC
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py --gui                 # PyBullet 창으로 보기
python main.py                       # 창 없이 실행, 결과 그래프(png)만 저장
```

### Python 버전 주의
- 확인한 환경: Python 3.11 + pybullet 3.2.7 (Linux). 세 예제 모두 창 없는 모드와 GUI 모드(가상 디스플레이)에서 실행해 확인했습니다.
- 같은 환경에서 Python 3.13으로는 `pip install pybullet`이 소스 빌드에서 실패했습니다. 설치가 안 되면 Python 3.10~3.11 가상환경을 쓰거나 `conda install -c conda-forge pybullet`을 시도해 보세요.

## 공통 로봇 모델 (`biped_model.py`)
- 실행할 때 URDF를 직접 만들어 씁니다 (외부 모델 파일 불필요). 몸통 10 kg, 전체 14.4 kg.
- 다리마다 5관절: `hip_roll, hip_pitch, knee, ankle_pitch, ankle_roll`.
- `leg_ik(x, y, z)`: 고관절 기준 발목 위치 → 발바닥이 지면과 평행하게 되는 관절각 (해석적 역기구학). PyBullet 순기구학으로 오차 0.1 mm 이하임을 확인했습니다.
- PyBullet 기본 모터를 끄고 `TORQUE_CONTROL`로 직접 토크를 넣습니다. 시뮬레이션 간격 1 ms.

## 실행 확인 결과 (창 없는 모드, 기본 옵션)

| 폴더 | 내용 | 결과 |
|---|---|---|
| 1_PID | 관절 PID 로 동작 추종 | 넘어지지 않음, 관절 추종 오차 RMS 최대 0.92°, 몸통 roll 보정을 켜면 한 발 들 때 흔들림 최대 3.3° (끄면 5.5°) |
| 2_LQR | 60 N, 0.1 s 앞으로 밀기 | 최대 기울기 4.7° 후 원래 자세로 복귀. 밀기 비교: LQR 70 N까지 버팀, 발목도 PID 고정이면 50 N까지 |
| 3_MPC | 6걸음, 보폭 8 cm | 넘어지지 않고 0.40 m 전진 (발목 최종 위치 0.405~0.409 m), 계획 질량 중심과 실제 차이 최대 x 1.3 cm, y 4.2 cm |

## 참고한 자료와 라이선스

이 폴더의 코드는 아래 저장소를 읽고 구조와 방법을 참고해 새로 작성한 것입니다. 코드를 그대로 복사하지는 않았습니다.

| 저장소 | 참고한 부분 | 라이선스 |
|---|---|---|
| [Einsbon/bipedal-robot-walking-simulation](https://github.com/Einsbon/bipedal-robot-walking-simulation) | PyBullet 이족 보행, 역기구학으로 보행 궤적 만들기 | MIT (Copyright (c) 2018 Sunbin Kim) |
| [rdesarz/biped-walking-controller](https://github.com/rdesarz/biped-walking-controller) | LIPM, ZMP preview control → 발 궤적 → 역기구학 → PyBullet 흐름 | MIT (Copyright (c) 2025 Romain Desarzens) |
| [haruki1526/LeggedRobotsForBullet](https://github.com/haruki1526/LeggedRobotsForBullet) | PyBullet 이족 preview control 예제 | MIT (Copyright (c) 2019 Haruki Takamura) |
| [tayalmanan28/Biped-Pybullet](https://github.com/tayalmanan28/Biped-Pybullet) | PyBullet 이족 시뮬레이션 구성 | MIT (Copyright (c) 2022 Manan Tayal) |

라이선스는 각 저장소의 LICENSE 파일에서 확인했습니다 (2026-11-20).

논문:
- S. Kajita, F. Kanehiro, K. Kaneko, K. Fujiwara, K. Harada, K. Yokoi, H. Hirukawa, "Biped Walking Pattern Generation by Using Preview Control of the Zero-Moment Point," ICRA 2003. (LIPM, ZMP)
- P.-B. Wieber, "Trajectory Free Linear Model Predictive Control for Stable Walking in the Presence of Strong Perturbations," IEEE-RAS Humanoids 2006. (jerk 입력, ZMP 추종 MPC 구성)
