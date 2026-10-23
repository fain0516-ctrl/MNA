# S10+ 메모리 정리 순위 (2026-10-22 측정 기준)

측정: 게임(트릭컬) 실행 중 `adb shell dumpsys meminfo` 결과. 숫자는 실제 메모리 점유량(PSS)입니다.
전체 RAM 7.6GB, 상태 **"low"(부족)**. 스왑(압축 저장) 4.3GB 사용 중.

## 1. 지우기보다 "게임 전에 닫기"가 훨씬 효과 큼

| 순위 | 앱 | 메모리 | 할 일 |
|---|---|---|---|
| 1 | YouTube (ReVanced) `app.revanced.android.youtube` | **674MB** | 게임 전에 최근 앱에서 완전히 닫기 |
| 2 | 삼성 인터넷 `com.sec.android.app.sbrowser` | 161MB (+탭 21MB) | 게임 전에 닫기 |
| 3 | 카카오톡 `com.kakao.talk` | 220MB | 필요한 앱이므로 유지 |

YouTube 하나가 아래 블로트웨어를 전부 합친 것보다 큽니다.

## 2. 비활성화 후보 (블로트웨어)

### A. 안전 — 대부분 안 쓰는 기능 (되돌리기 가능)
| 앱 | 메모리 | 무엇인지 | 영향 |
|---|---|---|---|
| `com.microsoft.appmanager` | 80MB + 36MB | Link to Windows (PC와 폰 연결) | PC 연동을 안 쓰면 영향 없음 |
| `com.samsung.android.smartsuggestions` | 35MB + 28MB | 스마트 제안 | 추천 기능만 사라짐 |
| `com.samsung.android.rubin.app` | 28MB | 맞춤 서비스(사용 패턴 분석) | 맞춤 추천만 사라짐 |
| `com.sec.android.app.dexonpc` | 13MB | PC용 DeX | DeX를 안 쓰면 영향 없음 |
| `com.samsung.android.bixby.wakeup` | 11MB | "하이 빅스비" 호출어 | 음성 호출만 사라짐 |
| `com.samsung.android.knox.analytics.uploader` | 9MB | 녹스 사용 통계 업로드 | 영향 없음 |

합계 약 **240MB**

### B. 쓰는지 확인 필요
| 앱 | 메모리 | 무엇인지 |
|---|---|---|
| `com.samsung.android.spay` (+`samsungpass`, `authfw`) | 67MB + 16MB + 8MB | 삼성페이 / 삼성패스 |
| `com.google.android.tts` | 77MB | 구글 음성 읽기(TTS) |
| `kr.go.kma.weatherapp` | 22MB | 기상청 날씨 앱 |

### C. 그대로 두기 (지우면 안 됨)
| 앱 | 이유 |
|---|---|
| `com.samsung.android.game.gos`, `gametools` | **2차 실험에서 온도를 내려준 그 기능**입니다 |
| `com.samsung.android.fmm` | 내 디바이스 찾기 (분실·보안 대비) |
| `com.samsung.android.honeyboard` | 삼성 키보드 |
| 시스템·구글 서비스(`gms`, `systemui`, `phone` 등) | 폰 작동에 필수 |

## 3. 비활성화 방법 (PC 명령 창)

비활성화(`disable-user`)는 삭제가 아니라 꺼두는 것이라 언제든 되돌릴 수 있습니다.

사용자 확인(2026-10-22): DeX와 Link to Windows는 사용 → 제외. 삼성페이·빅스비는 미사용 → 추가.

```
adb shell pm disable-user --user 0 com.samsung.android.smartsuggestions
adb shell pm disable-user --user 0 com.samsung.android.rubin.app
adb shell pm disable-user --user 0 com.samsung.android.bixby.wakeup
adb shell pm disable-user --user 0 com.samsung.android.knox.analytics.uploader
adb shell pm disable-user --user 0 com.samsung.android.spay
```

되돌리기 (예시):
```
adb shell pm enable com.samsung.android.spay
```

## 4. 확인할 것: 두 번째 사용자 공간
목록에 `u150`으로 시작하는 프로세스가 있었습니다. 보안 폴더를 쓰지 않으신다면 무엇인지 확인이 필요합니다.
```
adb shell pm list users
```
