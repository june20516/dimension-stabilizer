# Dimension Stabilizer

> 평면 모니터 3D 게임 멀미 완화용 **방향성 햅틱 디바이스** 개인 POC

게임 카메라가 회전할 때(마우스·컨트롤러 입력으로 감지) 방향성 진동 큐를 줘서 멀미/불편함을 줄일 수 있는지 검증하는 프로젝트입니다. **두 가지 구현을 모두 만들어 비교**합니다:
- **Track A (전정 자극)**: 골전도 이어폰 + PC 오디오로 좌/우 ~500Hz 진동 (소프트웨어 온리)
- **Track B (촉각)**: 아두이노 + 코인 진동모터로 좌/우 진동

두 트랙은 **공통 코어**(입력 → 회전 속도 → 좌/우 세기)를 공유하고 출력만 다릅니다. 최종적으로 **OFF / 전정 / 촉각 3way 블라인드**로 효과를 비교합니다.

## 한 줄 가설
"화면 카메라 회전 방향 = 머리 진동 방향"으로 인공 자기운동 단서를 보충하면, 평면 3D 게임의 멀미가 줄어들 것이다. (선행 연구상 VR에선 일부 근거, **평면 게임은 미개척**)

## 현재 상태
- ✅ 개념·가설 정립, 선행 연구 조사 (자극 주파수 ~500Hz 확인)
- ✅ 구현 경로 확정: **두 트랙 병행 + 공통 코어**
- ✅ **공통 코어 구현 완료** (입력→yaw_rate→좌/우 level, TDD 테스트 21개 통과)
- ⏳ 장비 준비·구매 (양 트랙)
- ⬜ Track A(이어폰) → Track B(모터)
- ⬜ 3way 효과 검증

## 실행 / 개발 환경 (Windows·macOS 공통)
공통 코어는 **OS 무관**(순수 파이썬 + 크로스플랫폼 라이브러리). venv는 OS별로 따로 생성합니다(커밋 안 됨).

요구사항: **Python 3.10+** (타입 문법 사용).

```bash
# macOS / Linux
python3 -m venv pc/.venv
pc/.venv/bin/pip install -r pc/requirements.txt
pc/.venv/bin/python -m pc.core        # 마우스 좌우 → 좌/우 level 콘솔 출력

# Windows (PowerShell)
py -m venv pc\.venv
pc\.venv\Scripts\pip install -r pc\requirements.txt
pc\.venv\Scripts\python -m pc.core
```
- **테스트**(설치 불필요, stdlib): `python -m unittest discover -s pc/tests -t .`
- macOS는 마우스 캡처에 **입력 모니터링 권한** 필요(시스템 설정 > 개인정보 보호 > 입력 모니터링). Windows는 불필요.
- OS별로 갈리는 지점(마우스 raw input·오디오 장치·시리얼 포트)은 `docs/cross-platform.md` 참고.

## 문서 색인
| 파일 | 내용 |
|------|------|
| `task_plan.md` | 마스터 계획 — 단계·결정·미결 질문 (진행 추적) |
| `findings.md` | 선행 연구 조사 결과·기술 결정 기록 |
| `progress.md` | 세션별 작업 로그 |
| `docs/concept-and-hypothesis.md` | 문제 정의·가설·메커니즘·성공 기준 |
| `docs/hardware-design.md` | 이어폰 선택·오디오 출력 분리·BOM (+ Plan B 부록) |
| `docs/software-architecture.md` | 데이터 흐름·500Hz 합성·오디오 출력 (+ Plan B 부록) |
| `docs/build-roadmap.md` | 단계별 로드맵 (소프트웨어 중심) |
| `docs/validation-plan.md` | 효과 검증(자가 A/B) 계획 |
| `docs/cross-platform.md` | Windows·macOS 호환 전략 (OS 경계 3곳) |
| `docs/arduino-inventory.md` | 아두이노 보유 부품 현황·역할·환경 메모 |
| `docs/arduino-curriculum.md` | 아두이노 학습 커리큘럼 + 진행 추적(다른 세션 이어가기) |
| `pc/` | 공통 코어 소스 + 테스트 (config·mapping·input_mouse·core) |

## 다음 할 일
1. 장비 구매 — Track A 마운트(싸구려 오버이어 헤드폰 도너 + 의료용 양면테이프) / Track B(아두이노 Uno + DRV8833 + 코인모터). 트랜스듀서는 구매완료
2. **Stage 0 게이트**: 트랜스듀서가 두개골 진동을 느끼게 하는지 + 최적 위치 확인 (docs/hardware-design.md A.6)
3. ~~공통 코어 구현~~ ✅ → 하드웨어 도착 후 Track A 마운트 제작 → Track B
