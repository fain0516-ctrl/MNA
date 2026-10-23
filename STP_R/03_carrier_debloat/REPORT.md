# Galaxy S10+ 통신사 선탑재 앱 제거

- 기기: Galaxy S10+ (SM-G975N), Android 12, 루팅 없음, 부트로더 잠김
- 상황: U+ 전용 모델로 출고된 폰을 현재 SKT 유심(자급제)으로 사용
- 날짜: 2026-10-23
- 방법: PC의 ADB(Google platform-tools). 루팅 없이 "사용자 0에서 제거" 방식이라 공장 초기화나 아래 복구 명령으로 되돌릴 수 있습니다.

## 1. 통신사 앱 찾기

```
adb shell pm list packages > pkgs.txt
findstr /i "skt skplanet tworld ktfreetel olleh kt. uplus lguplus" pkgs.txt
```

주의: `findstr`에서 `.`은 아무 글자 하나와 맞는 기호라서 `kt.`이 `desktop`에도 걸렸습니다. 그래서 DeX 앱 3개(`com.sec.android.app.desktoplauncher`, `com.samsung.desktopsystemui`, `com.sec.android.desktopmode.uiservice`)가 함께 나왔는데, 통신사 앱이 아니므로 제외했습니다.

## 2. 판단 결과

| 패키지 | 판단 | 근거 |
|---|---|---|
| `com.lguplus.appstore` | 제거 | U+ 스토어. U+ 유심을 쓰지 않음 |
| `com.lguplus.mobile.cs` | 제거 | U+ 고객센터 앱. U+ 유심을 쓰지 않음 |
| `com.lguplus.tsmproxy` | 제거 | 공개 자료로 정확한 용도 확인 못 함. 이름상 U+ 유심 결제(TSM) 관련으로 추정. U+ 유심이 없어 불필요하다고 판단 |
| `com.lguplus.lgugpsnwps` | 제거 | 공개 자료로 정확한 용도 확인 못 함. 이름상 U+ GPS 관련으로 추정. 같은 이유로 제거 |
| `com.skt.skaf.OA00018282` | 제거 | 사용자가 앱 정보 화면에서 확인 후 불필요하다고 판단 |
| `com.sktelecom.tauth` | **유지** | PASS by SKT(구 T인증). 본인인증에 사용 (사용자 확인) |
| `com.sktelinkapp` | **유지** | 자급제 전용 서비스 (사용자 확인) |

용도를 모르는 앱은 아래 명령으로 폰에 앱 정보 화면을 띄워 이름을 확인했습니다.

```
adb shell am start -a android.settings.APPLICATION_DETAILS_SETTINGS -d package:패키지명
```

## 3. 제거 명령

```
adb shell pm uninstall -k --user 0 com.lguplus.appstore
adb shell pm uninstall -k --user 0 com.lguplus.mobile.cs
adb shell pm uninstall -k --user 0 com.lguplus.tsmproxy
adb shell pm uninstall -k --user 0 com.lguplus.lgugpsnwps
adb shell pm uninstall -k --user 0 com.skt.skaf.OA00018282
```

복구: `adb shell cmd package install-existing 패키지명`

## 4. 완료 확인

명령이 `Success`를 돌려줘도 그것만으로는 부족해서 네 가지로 확인했습니다.

| 단계 | 명령 / 방법 | 결과 |
|---|---|---|
| 1. 목록에서 사라짐 | `adb shell pm list packages \| findstr "lguplus OA00018282"` | 출력 없음 (5개 모두 사라짐) |
| 2. 사용자 0 설치 상태 | `adb shell dumpsys package com.lguplus.appstore \| findstr "installed="` | `User 0: ... installed=false ... enabled=0` |
| 3. 재부팅 후 유지 | `adb reboot` 후 1번 다시 실행 | 출력 없음 (재부팅 후에도 제거 유지) |
| 4. 기능 | 다른 폰으로 전화 걸기/받기, 문자, MMS, 모바일 데이터, PASS 인증 | 모두 정상 |

참고: `pm list packages -u`로 보면 제거한 앱이 계속 나옵니다. 원본 APK가 읽기 전용 시스템 영역에 남아 있기 때문이고, 그래서 복구가 가능합니다.

## 5. 다른 폰에 적용할 때

통신사 패키지 이름은 통신사와 모델마다 다릅니다. 이 표를 그대로 쓰지 말고 1단계부터 직접 목록을 뽑아서 판단하세요. VoLTE 통화, 문자, 통신사 망 설정에 쓰이는 앱이 섞여 있을 수 있으므로 이름만 보고 일괄 삭제하지 않는 것이 안전합니다.
