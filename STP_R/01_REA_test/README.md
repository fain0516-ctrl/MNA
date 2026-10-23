# REA 시험 실행 결과 (2026-10-20)

대상 프로그램: [morluto/rea](https://github.com/morluto/rea), npm 패키지 `rea-agents` 6.7.0
환경: 클라우드 리눅스 (Ubuntu 24.04, Node 22.22)
분석 대상: Claude가 직접 만든 시험용 프로그램 2개 (`hello.c`, `jsapp/`)

## 결과

| 시험 | REA 명령 | 결과 |
|---|---|---|
| 준비 상태 점검 | `rea doctor` | Node는 정상입니다. 분석 엔진(Ghidra, Hopper, IDA)은 없음으로 나왔습니다. |
| JavaScript 앱 분석 | `rea analyze-javascript-application` | 성공했습니다. 함수 4개, 모듈 2개, 호출 지점 4개를 찾았고, `search`와 `add` 함수 및 연결 관계를 근거(파일 위치, 해시)와 함께 기록했습니다. → [`js-app-analysis.json`](js-app-analysis.json) |
| C 프로그램 구조 분석 | `rea inspect-binary-layout` | 성공했습니다(보조 도구 pwntools 4.15.0을 설치한 뒤). 64비트 리눅스 실행 파일임을 확인했고, `main`, `check_password`, `strcmp`, `puts`라는 이름과 보안 설정(PIE, NX, Full RELRO)을 찾았습니다. → [`c-program-layout.json`](c-program-layout.json) |
| C 프로그램 역컴파일(코드 복원) | `rea function` / `decompile` | 실행하지 못했습니다. Ghidra가 필요한데, 이 환경에서는 GitHub 다운로드가 차단되어 있습니다. |

## 다음 단계

실행 파일을 코드로 되돌리는 핵심 기능은 Ghidra 12.1.x가 있어야 합니다. Ghidra는 무료이고 Java 21이 필요합니다.
사용자 컴퓨터에 설치하거나, 이 클라우드 환경에서 GitHub 다운로드를 허용하면 진행할 수 있습니다.
