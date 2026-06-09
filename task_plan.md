# Task Plan: Dimension Stabilizer

> 평면 3D 게임 멀미 완화 — **두 트랙 비교 실험** (전정 자극 vs 촉각)

## Goal
평면 모니터 3D 게임(FPS류)의 멀미/불편함을 줄이기 위해, 게임 카메라 회전(마우스·컨트롤러)을 감지해 방향성 햅틱 큐를 주는 **두 가지 구현을 모두 만들어 비교**한다.
- **Track A (전정 자극)**: 골전도 이어폰 + PC 오디오로 좌/우 ~500Hz 진동 (소프트웨어 온리)
- **Track B (촉각)**: 아두이노 + 코인 진동모터로 좌/우 진동

두 트랙은 **공통 코어**(입력 → 회전 속도 → 좌/우 세기)를 공유하고 출력단만 다르다. 최종적으로 **OFF / 전정 / 촉각 3way 블라인드 비교**로 효과를 검증한다.

## Current Phase
Phase 3(공통 코어) **완료** → 하드웨어 도착 후 Phase 4(Track A)/5(Track B). Phase 2는 부품 대기로 블로킹

## Phases

### Phase 1: 개념 정립 & 연구
- [x] 대상 정의 (VR 아님 / 평면 3D 게임)
- [x] 가설·메커니즘 정리 — 전정 자극 vs 촉각 (concept-and-hypothesis.md)
- [x] 선행 연구 조사 — 자극 주파수 ~500Hz (findings.md)
- [x] 구현 경로 확정 — **두 트랙 병행 + 공통 코어**
- **Status:** complete

### Phase 2: 장비 준비 & 구매 (양 트랙)
- [x] **Track A 트랜스듀서**: 베어 골전도 8Ω ×2 (구매완료, 도착 대기)
- [ ] **Track A 마운트**: 오버이어 헤드폰 도너 1 + 의료용 양면테이프 + 벨크로/단단한 받침
- [ ] **Track B**: 아두이노 Uno + 스타터 키트 + 코인 진동모터 2~4
- [~] Python + `pynput` 설치 완료(pc/.venv). `sounddevice`(Phase 4)·Arduino IDE(Phase 5) 미설치
- **Status:** pending (하드웨어 대기)

### Phase 3: 공통 코어 (트랙 무관)
- [x] 마우스 delta → 정규화 `yaw_rate` (`pc/input_mouse.py` MouseYawSource, + 컨트롤러 어댑터는 Phase 6)
- [x] 매핑: `yaw_rate` → `(left_level, right_level)` ∈ [0,1] (데드존·감도·상한·attack/decay) (`pc/mapping.py`)
- **마일스톤:** ✅ 회전 시 좌/우 level 값 콘솔 출력 (`pc/core.py`, 시뮬레이션 검증 완료)
- **Status:** complete
- 산출물: `pc/{config,mapping,input_mouse,core}.py`, 테스트 21개(`pc/tests/`) 전부 통과. TDD로 작성

### Phase 4: Track A — 골전도 트랜스듀서 마운트 (전정 자극)
- [ ] **Stage 0 게이트**: 트랜스듀서를 테이프/손으로 귀 뒤 부착, 아두이노+DRV8833 500Hz → 느껴지나/최적 위치 진단 (hardware-design A.6)
- [ ] 오버이어 도너 가공: 쿠션 도려내고 트랜스듀서 돌출 마운트(벨크로), 좌/우
- [ ] 코어 연결: `level` → 500Hz 진폭·채널 → 트랜스듀서 (PC오디오 또는 아두이노 경로)
- **마일스톤:** 오른쪽 회전 시 오른쪽 유양돌기 진동 (Track A POC)
- **Status:** pending

### Phase 5: Track B — 아두이노 + 모터 (촉각)
- [ ] 아두이노 기본기(LED Blink/Fade/시리얼) → 모터 1개 구동
- [ ] 코어 연결: `level` → 시리얼 → PWM → 좌/우 모터
- **마일스톤:** 오른쪽 회전 시 오른쪽 모터 진동 (Track B POC)
- **Status:** pending
- 참고: Phase 4와 독립 — 순서 바꾸거나 병행 가능

### Phase 6: 컨트롤러 어댑터 (선택, 공통)
- [ ] 오른쪽 스틱 → 동일 `yaw_rate` 인터페이스
- **Status:** pending

### Phase 7: 각 트랙 튜닝
- [ ] Track A: 캐리어(500Hz 톤 vs 대역 노이즈), 세기·패닝
- [ ] Track B: 모터 위치(유양돌기 근처), 세기 곡선·데드존
- **Status:** pending

### Phase 8: 3way 효과 검증
- [ ] OFF(샴) / 전정(A) / 촉각(B) 블라인드 비교 (validation-plan.md)
- **마일스톤:** 세 조건의 불편함 지표 비교·기록
- **Status:** pending

## Key Questions
1. ~~주 입력?~~ → **마우스(주) + 컨트롤러(부)**, 공통 `yaw_rate`.
2. ~~모터 2 vs 4방향?~~ → **좌/우 2채널**(이어폰 스테레오 / 모터 2개). 위/아래 보류.
3. ~~전정 vs 촉각?~~ → **둘 다 만들어 3way 비교**로 답한다 (Track A=전정, Track B=촉각).
4. Track A 캐리어 = 500Hz 톤 vs 대역 노이즈? (Phase 7 비교)
5. 별도 오디오 출력 확보 방법? (Phase 2)
6. 효과 측정 = 자가 SSQ식 + 블라인드 3way (validation-plan.md)

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 대상 = 평면 3D 게임 (VR 아님) | VR에선 멀미 없음, 모니터 3D에서만 불편 |
| 회전 소스 = 마우스(주)+컨트롤러(부) | 게임 비종속·저지연. 공통 `yaw_rate`로 추상화 |
| **두 트랙 병행** (A=전정/이어폰, B=촉각/모터) | "전정 vs 촉각" 미결 질문을 실험으로 직접 비교 |
| **공통 코어 + 출력 백엔드 2개** | 입력·매핑은 한 번만. 출력만 오디오/시리얼로 분기 |
| 출력 세기 표준 = `level` ∈ [0,1] | A: 오디오 진폭, B: PWM 0-255 로 각자 스케일 |
| Track A 타겟 = ~500Hz, 유선·저지연 | 전정 근거 주파수. BT 지연 회피 |
| 검증 = OFF/전정/촉각 3way 블라인드 | 두 메커니즘을 같은 잣대로 비교 |
| Track A 마운트 = 오버이어 헤드폰 도너 + 트랜스듀서 돌출 | 압착력이 골전도 성패 1순위. 밴드 클램프 활용, 링 뒤-아래가 유양돌기 통과 |
| 정확한 유양돌기 정중앙 집착 안 함 | 두개골 전체 전달(임상도 이마 Fz 사용). "귀 뒤 단단한 뼈 단단 접촉"이 타깃 |
| 폴백 2순위 = 골전도 이어폰 프레임 재사용 | 1순위(오버이어 도너) 실패 대비 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- 단계마다 상태 갱신: pending → in_progress → complete
- 공통 코어를 먼저(Phase 3) 만들면 두 트랙이 그걸 그대로 재사용 → 중복 최소화
- "만드는 것"과 "효과 입증"은 난이도가 다름 — Phase 8이 진짜 난관
- 평면 3D + 방향 진동은 선행 연구가 얇음 → 탐색적 실험. 설계 상세는 docs/ 참고
