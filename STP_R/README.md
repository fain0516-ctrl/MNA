# STP_R

"REA를 활용한 프로그램 개발" 프로젝트의 결과물 모음입니다. 목표: 2026년 4분기 내 테스트 모델 생성.

| 폴더 | 내용 |
|---|---|
| [01_REA_test](01_REA_test/README.md) | REA([morluto/rea](https://github.com/morluto/rea), `rea-agents` 6.7.0) 설치와 시험 분석. 직접 만든 샘플(JavaScript 앱, C 프로그램)을 분석한 결과 |
| [02_S10plus_thermal](02_S10plus_thermal/REPORT.md) | Galaxy S10+ (SM-G975N) 발열 원인 진단과 루팅 없는 최적화 실험 |
| [03_carrier_debloat](03_carrier_debloat/REPORT.md) | Galaxy S10+ 통신사(U+, SKT) 선탑재 앱 제거와 완료 확인 절차 |

## 요약

- **REA:** AI 에이전트를 기존 분석 도구(Ghidra, Hopper, IDA)에 연결하는 MCP 서버입니다. JavaScript 앱 분석과 ELF 구조 분석은 성공했습니다. 역컴파일은 Ghidra가 필요한데, 클라우드 환경에서 GitHub 다운로드가 막혀 진행하지 못했습니다.
- **S10+:** 발열의 주범은 큰 코어(M4)였습니다. 게임 부스터 "퍼포먼스 관리"를 끄고 "표준"으로 두자 게임 중 온도가 59°C에서 48°C로 내려갔습니다(약간의 프레임 드랍 있음). 메모리 정리로 스왑 사용량이 4.3GB에서 2.2GB로 줄었습니다.
- **통신사 앱:** U+ 잔재 4개와 불필요한 SKT 앱 1개를 ADB로 제거했습니다(루팅 없음, 복구 가능). PASS와 자급제 서비스 앱은 유지했고, 제거 후 전화, 문자, 데이터가 정상인 것을 확인했습니다.
