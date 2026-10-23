# ADB 진단 명령 정리 (S10+ 발열 작업에서 실제로 쓴 것)

모든 명령은 PC의 명령 창(`platform-tools` 폴더)에서 입력합니다. 폰에 변화를 주는 것은 **⚙ 표시** 명령뿐이고, 나머지는 읽기만 합니다.

## 다른 폰에서도 되는가?

- **안드로이드 폰이면 대부분 됩니다.** 이 명령들은 ARM 칩이 아니라 **안드로이드(그리고 그 바탕인 리눅스)** 의 기능이기 때문입니다.
- **아이폰은 안 됩니다.** ADB 자체가 없습니다.
- 칩 제조사(삼성 엑시노스, 퀄컴 스냅드래곤 등)나 폰 제조사에 따라 **경로·이름이 다른 것**이 일부 있습니다. 아래 표의 "호환" 칸을 보세요.

## 1. 연결

| 명령 | 하는 일 | 호환 |
|---|---|---|
| `adb devices` | PC가 폰을 알아보는지 확인 (`device`면 성공) | 모든 안드로이드 |

## 2. 온도

| 명령 | 하는 일 | 호환 |
|---|---|---|
| `adb shell dumpsys thermalservice` | 부품별 온도(AP=CPU, PA=통신, SKIN=표면, BAT=배터리)와 발열 제한 단계 | 대부분의 최신 안드로이드. 센서 이름은 제조사마다 다름 |
| `/sys/class/thermal/...` | 센서 원본 값 | 루팅 필요한 경우가 많음 (이 폰은 거부됨) |

## 3. CPU 사용량

| 명령 | 하는 일 | 호환 |
|---|---|---|
| `adb shell dumpsys cpuinfo` | 최근 몇 분간 앱별 CPU 사용률 | 모든 안드로이드 |
| `adb shell top -n 1 -b` | 지금 이 순간 앱별 CPU·메모리 | 모든 안드로이드 |
| `adb shell pidof 패키지이름` | 앱의 번호(PID) 알아내기 | 모든 안드로이드 |
| `adb shell top -H -b -n 1 -p 번호` | 한 앱 안의 작업(스레드)별 CPU | 모든 안드로이드 |
| `adb shell ps -T -p 번호 -o TID,PSR,NAME` | 각 작업이 몇 번 코어에 있는지 | 모든 안드로이드 |

## 4. 코어·그래픽칩 속도

| 명령 | 하는 일 | 호환 |
|---|---|---|
| `adb shell cat /sys/devices/system/cpu/cpu6/cpufreq/scaling_cur_freq` | 6번 코어의 현재 속도(kHz) | 경로는 리눅스 공통. **단, 코어 묶음 번호는 칩마다 다름** (S10+ 엑시노스 9820은 0~3 / 4~5 / 6~7). 루팅 없이 읽히는지는 폰마다 다름 |
| `adb shell cat /sys/devices/system/cpu/cpu*/cpufreq/cpuinfo_max_freq` | 코어별 최고 속도 → 다른 폰에서 코어 묶음을 알아내는 법 | 위와 같음 |
| `adb shell cat /sys/kernel/gpu/gpu_clock` | 그래픽칩 현재 속도 | **삼성 엑시노스 전용.** 퀄컴 폰은 `/sys/class/kgsl/kgsl-3d0/gpuclk` 등 다른 경로 |

## 5. 메모리

| 명령 | 하는 일 | 호환 |
|---|---|---|
| `adb shell dumpsys meminfo` | 앱별 메모리 순위 (무거울 땐 시간 초과 날 수 있음) | 모든 안드로이드 |
| `adb shell cat /proc/meminfo` | 남은 메모리(MemAvailable), 스왑 사용량 등 요약 (빠름) | 모든 안드로이드 |

## 6. 앱·사용자 관리

| 명령 | 하는 일 | 호환 |
|---|---|---|
| `adb shell pm list users` | 폰 안의 사용자 공간 (보안 폴더 등) | 모든 안드로이드 |
| `adb shell pm list packages -d` | 꺼둔 앱 목록 | 모든 안드로이드 |
| ⚙ `adb shell pm disable-user --user 0 패키지이름` | 앱 끄기 (삭제 아님) | 모든 안드로이드. **패키지 이름은 제조사마다 다름** (`com.samsung...`은 삼성폰에만 있음) |
| ⚙ `adb shell pm enable 패키지이름` | 꺼둔 앱 되살리기 | 모든 안드로이드 |

## 7. 연속 기록 (2초마다 60회)

```
adb shell "for i in $(seq 1 60); do echo $i $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq /sys/devices/system/cpu/cpu4/cpufreq/scaling_cur_freq /sys/devices/system/cpu/cpu6/cpufreq/scaling_cur_freq) GPU=$(cat /sys/kernel/gpu/gpu_clock 2>/dev/null) $(dumpsys thermalservice | grep mName=AP | head -n 1); sleep 2; done" > freq_log.txt
```
다른 폰에서 쓸 때는 `cpu0/cpu4/cpu6` 를 그 폰의 코어 묶음 번호로, GPU 경로를 그 칩의 경로로 바꿔야 합니다.

## 결과 파일 저장 규칙
명령 끝에 `> 파일이름.txt` 를 붙이면 화면 대신 파일로 저장됩니다.
