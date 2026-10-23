# 스마트폰을 "40핀 없는 라즈베리파이"로 쓰기: 피코 USB 제어 가능성 분석

대상: Galaxy S10+ (SM-G975N, Exynos 9820, Android 12, 루팅 없음)
구상: 스마트폰 USB-C 포트에 2포트 분배기를 달고, 한쪽은 전원, 다른 한쪽은 케이블로 Raspberry Pi Pico를 연결해 제어 신호를 보낸다.
성격: 하드웨어 제작 전 단계의 가능성 분석입니다. 실측은 아직 하지 않았고, 근거는 문서 끝의 출처 목록에 있습니다.

---

## 1. 결론 요약

| 질문 | 답 | 조건 |
|---|---|---|
| ① 폰 CPU로 연산이 되는가 | **된다.** 제어 판단, 센서 처리, 카메라 영상 처리까지 충분한 성능 | 지속 부하에서의 발열과 "실시간이 아니다"라는 점은 설계로 피해야 함 |
| ② USB로 제어 신호를 뽑아 피코에 보낼 수 있는가 | **된다.** 루팅 없이 일반 앱으로 가능 | 폰이 USB host 기능을 지원해야 하고, 연결할 때 사용자 권한 허용이 필요 |
| 충전하면서 동시에 피코 연결 | **가장 불확실한 부분.** 아무 분배기로는 안 되고, 되더라도 폰과 허브 조합에 따라 다름 | 실물 테스트로 확인해야 함 (5장) |

한 줄로 정리하면, **폰은 "두뇌", 피코는 "손발과 반사신경"** 으로 역할을 나누면 실현 가능합니다. 타이밍이 중요한 일(모터 PWM, 센서 샘플링, 비상 정지)은 전부 피코가 하고, 폰은 "무엇을 할지"만 USB로 내려보내는 구조여야 합니다.

"모든 스마트폰에 해당한다"는 가정은 조금 수정이 필요합니다. Android 문서는 USB host API를 모든 기기가 지원한다고 보장하지 않습니다(출처 [A1]). 대부분의 최근 폰은 지원하지만, 기기마다 확인이 필요합니다(7.1절).

---

## 2. "40핀 없는 라즈베리파이" 비유가 맞는 부분과 다른 부분

맞는 부분:
- 리눅스 커널 위에서 도는 ARM 컴퓨터이고, 성능은 라즈베리파이보다 높습니다.
- 화면, 터치, 카메라, 배터리(무정전 전원 역할), Wi-Fi, 블루투스, 셀룰러가 이미 붙어 있습니다.

다른 부분 (설계에 영향이 큼):
1. **GPIO가 없다.** 그래서 피코가 GPIO 역할을 대신합니다. 이 구상의 핵심이 바로 이것이고 방향은 맞습니다.
2. **USB 포트가 하나뿐이다.** 충전, 데이터, ADB가 모두 이 포트 하나를 씁니다. 라즈베리파이는 전원 포트와 USB 포트가 따로 있습니다.
3. **앱이 샌드박스 안에서 돈다.** 루팅 없이 백그라운드 프로그램(데몬)을 자유롭게 상주시킬 수 없고, 삼성 One UI는 백그라운드 앱을 적극적으로 종료합니다(6.3절).
4. **24시간 상시 가동용으로 설계되지 않았다.** 배터리, 발열, 화면 꺼짐 관리가 모두 "사람이 들고 쓰는 폰" 기준입니다.

---

## 3. 세부 질문 ①: 폰 CPU로 연산이 가능한가

### 3.1 성능

삼성이 공개한 Exynos 9820 사양(출처 [S1], [S2]):
- CPU: "Dual-core (Custom CPU) + Dual-core (Cortex-A75) + Quad-core (Cortex-A55)", 즉 2+2+4 구성의 8코어
- GPU: ARM Mali-G76 MP12
- NPU: 내장. 삼성 발표 기준 전작보다 AI 작업이 약 7배 빠름
- 메모리: LPDDR4x

피코의 RP2040은 "Dual ARM Cortex-M0+ @ 133MHz", SRAM 264kB입니다(출처 [P1]). 연산 능력 차이는 수천 배 단위라서, 제어 로직은 물론 카메라 영상 인식까지 폰 쪽에서 충분히 처리할 수 있습니다. **연산 성능은 병목이 아닙니다.**

### 3.2 진짜 제약 1: 발열과 지속 성능

앞선 진단([STP_R/02_S10plus_thermal](../STP_R/02_S10plus_thermal/REPORT.md))에서 확인한 것처럼, 이 폰의 발열 주범은 큰 코어(M4)였고 게임 부하에서 59°C까지 올라갔습니다. 이 구상에서는 상황이 더 나빠집니다.
- 충전 중에는 배터리와 충전 회로에서 열이 추가로 납니다.
- 장치 안에 넣거나 거치하면 손으로 들 때보다 방열이 나빠집니다.
- 장시간 부하가 걸리면 삼성이 온도 기준으로 성능을 낮춥니다(앞선 진단에서 낮은 피부 온도에서도 쓰로틀링이 걸리는 것을 확인).

설계 방향: 연산을 "가끔, 짧게" 하거나, 작은 코어로 충분한 수준으로 유지하고, 무거운 영상 처리는 해상도와 프레임 수를 낮춰서 돌립니다.

### 3.3 진짜 제약 2: Android는 실시간 운영체제가 아니다

Android의 기본 커널과 앱 실행 환경은 "정해진 시간 안에 반드시 응답한다"를 보장하지 않습니다. 실시간 성능을 얻으려고 커널에 RT_PREEMPT 패치를 적용하고 Android 내부를 고친 연구가 따로 있을 정도입니다(출처 [R1], RWTH Aachen 대학, Kalkov, Franke, Kowalewski). 루팅도 안 된 일반 폰에서는 이런 수정을 할 수 없습니다.

의미: 폰에서 "1ms마다 모터 출력을 갱신" 같은 일을 하면 가끔 수십 ms씩 밀립니다(가비지 컬렉션, 화면 꺼짐, 다른 앱 등). 그래서 **시간에 민감한 루프는 전부 피코에서 돌려야** 합니다. 피코는 운영체제 없이 돌기 때문에 이런 일에 적합하고, PIO 상태 머신 8개, PWM 16채널을 갖고 있습니다(출처 [P1]).

---

## 4. 세부 질문 ②: USB로 제어 신호를 뽑아 피코에 보낼 수 있는가

### 4.1 경로

```
[Android 앱]
   │  UsbManager → 권한 허용 → UsbDeviceConnection.bulkTransfer()
   ▼
[USB 케이블 / 허브]
   ▼
[Pico]  USB CDC(가상 시리얼)로 명령 수신
   │  GPIO / PWM / UART / I2C / SPI
   ▼
[모터 드라이버, 서보, 릴레이, 센서 …]  ← 별도 전원
```

### 4.2 폰 쪽: 루팅 없이 가능

- Android는 3.1부터 "USB host mode"를 지원합니다. 이 모드에서 폰이 호스트가 되어 연결된 USB 기기에 전원을 공급하고 기기를 인식합니다(출처 [A1]).
- 앱은 `android.hardware.usb` 패키지의 `UsbManager`, `UsbDevice`, `UsbDeviceConnection` 등을 써서 `bulkTransfer()` 또는 `controlTransfer()`로 데이터를 주고받습니다. 이 전송은 UI 스레드가 아닌 별도 스레드에서 해야 합니다(출처 [A1]).
- **권한:** 앱이 `requestPermission()`을 부르면 사용자에게 권한 대화상자가 뜹니다. 대신 `USB_DEVICE_ATTACHED` 인텐트 필터와 `device_filter.xml`로 피코의 vendor-id/product-id를 등록해 두면, 꽂을 때 시스템이 앱 실행 여부를 묻고, 사용자가 수락하면 **분리될 때까지** 자동으로 접근 권한을 얻습니다(출처 [A1]). 즉 피코를 뽑았다 다시 꽂으면 다시 허용해야 할 수 있습니다.
- 시리얼 통신 라이브러리: 오픈소스 `usb-serial-for-android`(mik3y)는 "No root access, ADK, or special kernel drivers are required"라고 명시하고, CDC/ACM 기기를 USB 인터페이스 종류로 자동 인식합니다(출처 [L1]). 피코를 CDC 기기로 만들면 이 라이브러리로 바로 붙일 수 있습니다.

### 4.3 피코 쪽

- RP2040에는 "USB 1.1 controller and PHY, with host and device support"가 있습니다(출처 [P1]). 피코는 USB 기기(device) 역할로 동작하면 됩니다.
- Pico C SDK의 `pico_stdio_usb`는 stdin/stdout을 "USB serial (CDC)"로 내보냅니다(출처 [P2]). 즉 `printf`/`getchar` 수준으로 폰과 대화할 수 있어서 시작하기 가장 쉽습니다. SDK 문서는 이를 "a developer convenience"라고 부르며, 더 세밀한 제어가 필요하면 TinyUSB를 직접 쓰라고 안내합니다(출처 [P2]). MicroPython도 기본적으로 USB 시리얼을 제공합니다.

### 4.4 통신 규약에서 꼭 넣어야 할 것

단순히 문자열을 흘려보내는 것보다 아래를 갖춘 작은 규약을 권장합니다.
1. **프레임 구조:** 시작 바이트, 명령 종류, 값, 체크섬. 끊긴 데이터나 잡음으로 엉뚱한 명령이 실행되는 것을 막습니다.
2. **하트비트와 페일세이프:** 폰이 주기적으로(예: 100ms) "살아 있음" 신호를 보내고, 피코는 일정 시간(예: 300ms) 신호가 없으면 모터를 멈추는 등 안전 상태로 갑니다. 폰 앱이 죽거나, 케이블이 빠지거나, 허브가 재연결될 때를 대비하는 장치이고, **이 구상에서 가장 중요한 안전장치**입니다.
3. **응답(ACK)과 상태 보고:** 피코가 명령 수신과 센서 값을 돌려보내면 폰에서 상태를 표시하고 기록할 수 있습니다.

---

## 5. 가장 큰 불확실성: 2포트 분배기로 충전과 피코 연결을 동시에

### 5.1 "분배기"의 종류가 중요하다

USB-C에서는 데이터 역할(호스트/기기)과 전원 역할(전원 공급/전원 수신)이 서로 다른 개념입니다. 리눅스 커널의 USB Type-C 코드도 데이터 역할(`TYPEC_HOST`, `TYPEC_DEVICE`)과 전원 역할(`TYPEC_SOURCE`, `TYPEC_SINK`)을 따로 정의합니다(출처 [K1]). 이 구상이 동작하려면 폰이 **데이터는 호스트, 전원은 수신(충전)** 인 상태가 되어야 합니다.

- **단순 Y자 분배 케이블(전기적으로 선만 나눈 것):** 권장하지 않습니다. 충전기와 폰이 서로 전원을 내보내려 하거나, 폰이 어떤 역할을 해야 할지 판단하지 못할 수 있습니다.
- **PD(Power Delivery) 충전 입력 포트가 있는 USB-C 허브:** 현실적인 선택지입니다. 허브가 충전기 전원을 받아 폰 쪽으로 넘겨주고(일반적으로 "PD 패스스루"라고 광고), 동시에 USB 포트를 제공합니다. TI 기술지원 답변도 USB-C 폰은 Type-C와 Power Delivery를 통해 "role swap of data and power"를 하는 방식일 가능성이 높다고 설명합니다(출처 [H2]).

### 5.2 S10+에서 되는가: "보고된 사례는 있으나 보장은 없다"

- 한 액세서리 판매자 블로그는 Galaxy S10, S20 계열이 특정 OTG 어댑터로 충전과 주변기기 연결을 동시에 할 수 있다고 적고 있습니다(출처 [H1]). 다만 공식 문서가 아니고, 어댑터 모델을 명시하지 않았습니다.
- 반대로 USB 액세서리 제조사 Plugable은 "Some phones will only allow for one type of function on the USB port at a time"라고 경고합니다(출처 [H3]).
- 삼성 공식 문서에서 S10+의 "충전 + USB host 동시 지원"을 명시한 자료는 이번 조사에서 찾지 못했습니다.

따라서 **허브 하나를 사서 직접 확인하는 것이 첫 단계**입니다. 확인 방법(ADB로 PC에서 실행):

```
adb shell dumpsys battery
adb shell dumpsys usb
```

- `dumpsys battery`에서 충전기 연결 여부와 충전 상태를 보고,
- `dumpsys usb`에서 포트의 현재 역할을 봅니다.
- 출력은 기기마다 형식이 다를 수 있으니, 결과를 그대로 붙여 주면 해석하겠습니다.

> 주의: 허브를 꽂으면 USB 포트가 막혀서 **유선 ADB를 쓸 수 없습니다.** 대신 Android 11 이상에서 지원하는 개발자 옵션의 **Wireless debugging**(무선 디버깅)을 쓰면 됩니다. PC와 폰을 같은 Wi-Fi에 두고 "Pair using pairing code"를 선택한 뒤 PC에서 `adb pair ipaddr:port`를 실행합니다(출처 [A3]).

### 5.3 "CTOC" 케이블과 피코 커넥터

USB-C to USB-C 케이블을 생각하셨다면 한 가지 확인할 점이 있습니다. **원래의 Raspberry Pi Pico는 USB-C가 아니라 "Micro-USB B port"** 를 씁니다(출처 [P3]). 그래서
- 허브의 포트가 USB-A면 USB-A to Micro-B 케이블,
- 허브의 포트가 USB-C면 USB-C to Micro-B 케이블이 필요하고,
- C to C로 연결하고 싶다면 USB-C 커넥터가 달린 RP2040/RP2350 보드를 고르면 됩니다.

### 5.4 전원 분리: 모터를 폰 USB로 돌리면 안 된다

- 피코 자체는 USB의 VBUS로 동작하며, 소비 전력이 작아 문제없습니다. 피코의 VSYS 입력 허용 범위는 1.8V~5.5V입니다(출처 [P3]).
- 하지만 모터, 서보, 릴레이처럼 전류를 많이 먹거나 순간적으로 전압을 흔드는 부하를 피코나 허브의 5V에서 끌어 쓰면, 허브가 재연결되거나 폰이 USB 장치를 끊어 버릴 수 있습니다. **구동부는 별도 전원(배터리 팩, 어댑터)을 쓰고, 접지(GND)만 피코와 공통으로** 묶습니다.
- 피코의 GPIO는 3.3V 고정입니다(출처 [P3]). 5V 장치를 직접 연결하면 안 되고 레벨 변환이나 드라이버 보드를 거쳐야 합니다.

---

## 6. 처음 질문에 없던 추가 문제점

### 6.1 배터리: 상시 충전과 부풂

폰을 계속 충전기에 꽂아 두면 배터리가 100% 근처에 오래 머물러 열화와 부풂 위험이 커집니다. 배터리를 이미 교체하셨으니 더 아껴 쓸 가치가 있습니다.
- 삼성의 **Protect battery** 기능을 켜면 충전이 85%로 제한됩니다(설정 → 배터리 → Protect battery. 삼성 안내 문서 기준이며, 메뉴 위치와 이름은 One UI 버전마다 다를 수 있음)(출처 [S3]).
- 발열(6.4절)과 겹치면 열화가 빨라지므로, 거치 위치에 공기가 통하게 합니다.

### 6.2 피코를 다시 꽂을 때마다 권한 허용

4.2절대로, 인텐트 필터 방식은 "분리될 때까지" 권한이 유지됩니다. 케이블이 흔들려 순간 분리되면 다시 허용을 눌러야 할 수 있습니다. 무인 장치라면 커넥터를 고정하고, 재연결 시 앱이 자동으로 다시 붙도록 만들어야 합니다.

### 6.3 백그라운드 종료

삼성 One UI는 앱을 적극적으로 재웁니다. DontKillMyApp 분석에 따르면 Android 11 이후 삼성은 배터리 최적화에서 제외하지 않은 앱의 백그라운드 작업을 막고, 일정 기간 안 쓴 앱을 "Sleeping apps"로 보냅니다(출처 [D1]). 대응:
- 앱 쪽: 화면 알림이 떠 있는 **포그라운드 서비스**로 통신을 돌립니다. Android에는 USB 같은 외부 기기 연결용 포그라운드 서비스 유형 `connectedDevice`가 있고, `UsbManager.requestPermission()` 호출이 이 유형의 실행 조건 중 하나입니다(출처 [A2]).
- 폰 설정 쪽: 해당 앱을 배터리 최적화에서 제외하고, "Never sleeping apps"에 넣고, "Put unused apps to sleep"을 끕니다(출처 [D1]).
- 가장 단순한 방법은 **앱을 화면에 띄워 둔 채 화면이 꺼지지 않게** 하는 것입니다(대신 발열과 화면 번인을 고려).

### 6.4 발열은 이 구상에서 더 심해진다

충전 열 + 연산 열 + 밀폐된 거치. 앞선 진단에서 정리한 방법(게임 부스터 "퍼포먼스 관리" 끄기 등)에 더해, 폰 뒷면이 공기에 노출되도록 거치하고 무거운 연산은 꼭 필요할 때만 돌립니다.

### 6.5 안전: 폰이 멈춰도 기계는 멈춰야 한다

폰 앱 충돌, OS 업데이트 재부팅, 배터리 방전, 케이블 분리 등 폰 쪽에서 제어가 끊길 경로가 많습니다. 4.4절의 하트비트 페일세이프와 함께, 위험한 구동부라면 **물리 비상 정지 스위치**를 피코나 전원 쪽에 둡니다.

### 6.6 일상용 폰과 겸용하는 문제

이 S10+는 일상용 폰입니다. 장치에 묶어 두면 그동안 폰을 들고 다닐 수 없고, 반대로 들고 나가면 장치가 멈춥니다. 앞서 언급하신 **여분 폰을 이 용도로 쓰는 것**을 권장합니다. 그 경우 데이터 초기화 후 이 앱만 설치하면 백그라운드 종료와 알림 문제도 줄어듭니다.

### 6.7 대안: 케이블 대신 무선

USB 포트 하나를 충전에 온전히 돌리면 5장의 불확실성이 사라집니다.
- **Pico W + Bluetooth LE:** Pico W는 C SDK 1.5.1(2023년 6월)부터 Bluetooth를 지원하며, BLE는 Central과 Peripheral 역할을 모두 지원합니다(출처 [P4]). 폰은 일반 충전기로 충전하고, 제어 명령은 BLE로 보냅니다.
- **Pico W + Wi-Fi:** 같은 네트워크 안에서 TCP/UDP로 통신합니다. 거리와 속도에 유리합니다.
- 단점: 유선보다 지연 시간이 들쭉날쭉하고 연결이 끊길 수 있습니다. 하지만 어차피 실시간 루프는 피코가 돌리고 페일세이프가 있으므로, 대부분의 용도에서 문제되지 않습니다.

| 방식 | 충전 동시 | 지연/안정성 | 난이도 |
|---|---|---|---|
| USB 유선 (PD 허브) | 허브와 폰 조합에 따라 다름, 실험 필요 | 가장 안정적 | 중간 (허브 구매와 확인) |
| BLE (Pico W) | 문제없음 | 보통 | 중간 (BLE 앱 코드) |
| Wi-Fi (Pico W) | 문제없음 | 보통, 공유기 의존 | 낮음~중간 |

---

## 7. 구체화한 단계별 진행안

### 7.1 0단계: 폰이 USB host를 지원하는지 확인 (지금 바로, 비용 0)

```
adb shell pm list features
```

출력에 `feature:android.hardware.usb.host`가 있으면 지원합니다(Android 문서가 앱 매니페스트에 선언하도록 하는 기능 이름, 출처 [A1]). Windows cmd에서는 `adb shell pm list features | findstr usb` 로 걸러 볼 수 있습니다.

### 7.2 1단계: 충전 없이 피코만 연결

- 폰 ↔ USB-C to Micro-B 케이블(또는 OTG 어댑터) ↔ 피코
- 피코에 MicroPython 또는 `pico_stdio_usb` 예제를 올려 LED를 켜고 끄는 명령을 받게 함
- 폰에서는 플레이스토어의 USB 시리얼 터미널 앱으로 먼저 확인 (코딩 없이 동작 검증)

### 7.3 2단계: PD 허브로 충전 동시 확인

- PD 충전 입력이 있는 USB-C 허브 + 충전기 + 피코
- 5.2절의 `dumpsys` 명령으로 "충전 중"과 "피코 인식"이 동시에 되는지 확인 (무선 디버깅 사용)
- 안 되면 6.7절의 무선 방식으로 전환

### 7.4 3단계: 전용 앱과 규약

- `usb-serial-for-android` 기반의 간단한 앱 + 4.4절의 프레임, 하트비트, 페일세이프
- 포그라운드 서비스, 배터리 최적화 제외, Protect battery 설정

### 7.5 준비물 (1~2단계)

- Raspberry Pi Pico (무선이 필요하면 Pico W)
- USB-C to Micro-B 케이블 (또는 USB-C 단자가 달린 RP2040 보드)
- PD 충전 입력이 있는 USB-C 허브 (2단계)
- 테스트용 LED와 저항, 브레드보드

---

## 출처

Android / Google
- [A1] Android Developers, "USB host overview": https://developer.android.com/develop/connectivity/usb/host
- [A2] Android Developers, "Foreground service types are required" (connectedDevice 유형): https://developer.android.com/about/versions/14/changes/fgs-types-required
- [A3] Android Developers, "Android Debug Bridge (adb)", Connect to a device over Wi-Fi: https://developer.android.com/tools/adb
- [K1] Android 커널 공통 트리 `include/linux/usb/typec.h`: https://android.googlesource.com/kernel/common/+/815e34f802d8c60218bf8b7811f2a4f2a5c7e35a/include/linux/usb/typec.h

Samsung
- [S1] Samsung Newsroom, Exynos 9 Series 9820 발표: https://news.samsung.com/global/samsung-brings-on-device-ai-processing-for-premium-mobile-devices-with-exynos-9-series-9820-processor
- [S2] Samsung, "MobileProcessor 9 Series 9820" 제품 자료(PDF, WikiChip 보관본): https://www.wikichip.org/w/images/e/e0/MobileProcessor-9-Series-9820.pdf
- [S3] Samsung 지원, "'Protect battery' feature in Galaxy phones": https://www.samsung.com/in/support/mobile-devices/battery-protection-feature-in-samsung-galaxy-phones

Raspberry Pi
- [P1] RP2040 Datasheet, Chapter 1 Introduction: https://xiao-seeed-rp2040-renode.readthedocs.io/en/latest/specification/rp2040-datasheet/03_chapter_1_introduction/
- [P2] Pico SDK 문서, `pico_stdio_usb`: https://picodocs.pinout.xyz/group__pico__stdio__usb.html
- [P3] Raspberry Pi Pico Datasheet (PDF): https://cdn.sparkfun.com/assets/7/b/1/b/1/pico-datasheet.pdf
- [P4] Raspberry Pi News, "New functionality: Bluetooth for Pico W" (2023-06-14): https://www.raspberrypi.com/news/new-functionality-bluetooth-for-pico-w/

라이브러리 / 커뮤니티
- [L1] mik3y/usb-serial-for-android README: https://github.com/mik3y/usb-serial-for-android
- [D1] DontKillMyApp, Samsung: https://dontkillmyapp.com/samsung
- [H1] Looperbuy 블로그, "Phones That Can Charge and OTG at the Same Time" (판매자 블로그, 참고용): https://blog.looperbuy.com/?p=1137
- [H2] TI E2E 포럼, TUSB4041I 관련 답변: https://e2e.ti.com/support/interface-group/interface/f/interface-forum/896116/tusb4041i-how-to-get-a-usb-c-device-be-in-upstream-host-mode-and-also-be-charged-simultaneously
- [H3] Plugable 지원 포럼: https://support.plugable.com/t/is-there-a-way-to-power-android-phone-samsung-galaxy-at-the-same-time-as-using-this-adapter/17621

논문
- [R1] I. Kalkov, D. Franke, S. Kowalewski, "A Real-time Extension to the Android Platform", RWTH Aachen University: https://publications.embedded.rwth-aachen.de/file/57

용어 메모: "PD 패스스루"는 허브 판매 페이지에서 흔히 쓰는 표현이지만 위 출처 중 이 단어를 정의한 공식 문서는 없습니다. 이 문서에서는 "허브가 충전기 전원을 폰으로 넘겨주는 기능"이라는 뜻으로만 썼습니다. "USB host mode", "CDC", "Protect battery", "RT_PREEMPT", "connectedDevice", "Wireless debugging"은 각각 해당 출처에 그대로 나오는 용어입니다.
