# Galaxy S10+ (SM-G975N) 발열 진단 보고서

측정일: 2026-10-22 · 방법: PC에서 ADB(읽기 전용 명령), 루팅·부트로더 해제 없음
대상 기기: Galaxy S10+ 한국 모델 (Exynos 9820, 코드명 beyond2lte), 배터리 교체 완료
부하 조건: 게임 "트릭컬" (`com.epidgames.trickcalrevive`, Unity 엔진)

## 1. 발열 원인

| 측정 | 결과 |
|---|---|
| 부품별 온도 (`dumpsys thermalservice`) | AP(CPU) 47.3°C, PA(통신 증폭기) 40.8°C, USB 37.1°C, 표면 36.6°C, 배터리 34.0°C |
| 앱별 CPU (`dumpsys cpuinfo`) | 게임 146%, surfaceflinger 25%, audioserver 20% |
| 게임 스레드 (`top -H`) | UnityMain 58%, mali-cmar-backend 29%, UnityGfxDeviceWorker 26% |
| 2분 연속 기록 | 큰 코어(M4, 6~7번) 평균 2.06GHz, 60회 중 44회가 2.08~2.34GHz |

**결론:** 주 열원은 큰 코어(M4)입니다. 게임 내내 2.2GHz 안팎으로 동작했습니다. 그래픽칩(Mali, 평균 426MHz / 최대 702MHz)은 보조 요인입니다.

Exynos 9820 코어 묶음: 0~3번 작은 코어(A55) / 4~5번 중간 코어(A75) / 6~7번 큰 코어(M4).

## 2. 게임 부스터 설정 비교 실험

게임 부스터 실험실의 "퍼포먼스 관리"가 켜져 있었습니다. 이 항목은 삼성의 게임 성능 조절 기능(GOS)을 끄는 옵션으로 보입니다([SamMobile](https://www.sammobile.com/news/want-the-best-game-performance-on-your-galaxy-heres-how-to-do-it/)).

| 실험 | 큰 코어 평균 | 그래픽칩 평균 | 최고 온도 | 끝 온도 | 체감 |
|---|---|---|---|---|---|
| A: 퍼포먼스 관리 켬 | 2.06GHz | 426MHz | 59.3°C | 58.2°C | 부드러움 |
| B: 끔 + 표준 | 1.45GHz | 327MHz | 57.8°C | **48.1°C** | 약간 프레임 드랍 |
| C: 끔 + 성능 | 2.10GHz | 420MHz | 60.3°C | 55.5°C | 부드러움, 뜨거움 |

B는 처음 40초 뒤 GOS가 작동해 큰 코어가 평균 1.14GHz로 내려갔고, 게임 중에도 온도가 하강했습니다.
B는 이미 데워진 상태(54°C)에서 시작했으므로 숫자는 대략적인 비교입니다.

**권장 설정:** 퍼포먼스 관리 끔 + 게임 최적화 "표준".

## 3. 메모리 정리

| 항목 | 내용 |
|---|---|
| 정리 전 | RAM 상태 "low", 스왑 4.3GB 사용 |
| 원인 | 게임 2.4GB, 백그라운드 YouTube 674MB, 사용하지 않는 보안 폴더가 서비스 한 벌을 따로 실행 |
| 조치 | 보안 폴더 삭제, 앱 5개 비활성화 ([목록](tools/S10plus_memory_debloat.md)), 게임 전 YouTube 닫기 |
| 정리 후 | 스왑 2.2GB, MemAvailable 약 3.3GB (재부팅 직후 값이라 효과가 일부 섞여 있음) |

## 4. 남은 과제

루팅 없이 고를 수 있는 설정은 "부드럽고 뜨거움"과 "약간 끊기고 시원함" 두 가지뿐입니다.
그 중간(부드러움 유지 + 발열 감소)은 커스텀 커널로 큰 코어 최고 속도를 약 1.8GHz로 제한하고 언더볼팅하는 방법이 후보입니다. 부트로더 해제(Knox 영구 해제)가 필요하므로 여분 기기에서 진행할 예정입니다. 효과는 추정이며 실측으로 확인해야 합니다.

## 도구

- [adb_command_cheatsheet.md](tools/adb_command_cheatsheet.md): 사용한 ADB 명령과 다른 폰 호환 여부
- [probe.sh](tools/probe.sh): 기기 쪽 측정 스크립트
- [S10plus_memory_debloat.md](tools/S10plus_memory_debloat.md): 메모리 순위와 비활성화 목록

## 표지 로그 (logs/)

원본 측정 로그는 개인 기기 정보(설치 앱 목록, 네트워크 주소 등)가 섞여 있어 그대로 넣지 않았습니다. 대신 각 파일 머리에 명령·조건·날짜를 적고, 위 숫자를 확인할 수 있는 줄만 남긴 발췌본을 넣었습니다.

| 파일 | 내용 | 근거가 되는 항목 |
|---|---|---|
| [01_thermal_status.txt](logs/01_thermal_status.txt) | 부품별 온도 | 1장 |
| [02_cpuinfo.txt](logs/02_cpuinfo.txt) | 게임·시스템 CPU 사용률 | 1장 |
| [03_game_threads.txt](logs/03_game_threads.txt) | 게임 스레드 상위 5개 | 1장 |
| [04_freq_A_perfmgmt_on.txt](logs/04_freq_A_perfmgmt_on.txt) | 실험 A, 60회 전체 | 2장 |
| [05_freq_B_off_standard.txt](logs/05_freq_B_off_standard.txt) | 실험 B, 60회 전체 | 2장 |
| [06_freq_C_off_performance.txt](logs/06_freq_C_off_performance.txt) | 실험 C, 60회 전체 | 2장 |
| [07_proc_meminfo_after.txt](logs/07_proc_meminfo_after.txt) | 정리 후 메모리 요약 | 3장 |
