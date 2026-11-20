# 참고 저장소 분석 (저장소 1곳 = 폴더 1개)

각 폴더 구성:

| 위치 | 내용 |
|---|---|
| `README.md` | 1. 성격 (PID/LQR/MPC 등 어디에 해당하는지), 2. 원본 구조와 제어 방식, 4. PyBullet 실행 코드에서 바꾼 점과 실행 결과 |
| `original/` | 3. 원본 소스 (2026-11-20 기준 기본 브랜치에서 받은 그대로, LICENSE 포함) |
| `pybullet/` | 4. 노트북에서 바로 실행되도록 다시 짠 코드 (`main.py`, `requirements.txt`, 결과 그래프) |

| 폴더 | 성격 | 원본 그대로 실행 | PyBullet 실행 코드 결과 |
|---|---|---|---|
| [01_Einsbon](01_Einsbon_bipedal-robot-walking-simulation/) | PID/LQR/MPC 아님. 미리 만든 보행 궤적 + 역기구학 + PyBullet 내장 위치 제어 (되먹임 균형 제어 없음) | 안 됨 (`np.float` 삭제로 오류) | 4회 반복, 0.81 m 전진, 넘어지지 않음 |
| [02_haruki1526](02_haruki1526_LeggedRobotsForBullet/) | ZMP preview control (리카티 방정식으로 이득을 구하는 LQR 계열) | 안 됨 (최신 numpy 에서 배열 오류 2곳) | 20걸음, 1.53 m 전진, 넘어지지 않음 |
| [03_tayalmanan28](03_tayalmanan28_Biped-Pybullet/) | 02와 같은 ZMP preview control (코드 구조와 값이 02와 같음) | 안 됨 (02와 같은 numpy 오류) | walk 10초 1.85 m, 다른 동작 5개도 넘어지지 않음 |
| [04_rdesarz](04_rdesarz_biped-walking-controller/) | LIPM + ZMP preview control (LQR 계열) + QP 역기구학 | 이 환경에서는 시도 안 함 (Talos 모델과 Pinocchio 필요). preview control 모듈은 numpy 2.x 에서 오류 | 로봇을 바꿔서 15걸음, 1.50 m 전진, 넘어지지 않음 |

- 확인 환경: Python 3.11, pybullet 3.2.7, numpy 2.4.6. 새 가상환경에 `requirements.txt` 로 설치한 뒤 창 없는 모드와 `--gui` 모드(가상 디스플레이) 모두 실행했습니다.
- 4곳 모두 MIT 라이선스입니다. 다시 짠 코드에도 원본 LICENSE 를 같이 넣었습니다.
- 원본 파일 목록은 GitHub 코드 검색으로 찾았습니다. 그림(gif, png)처럼 검색에 안 잡히는 파일은 빠졌을 수 있고, 실행에 필요한 메시(STL)는 URDF 에 적힌 이름으로 따로 받았습니다.
- 4곳 중 PID, LQR 균형 제어, MPC 를 직접 쓰는 곳은 없습니다. PID → LQR → MPC 순서 공부용 예제는 상위 폴더의 `1_PID`, `2_LQR`, `3_MPC` 입니다.
