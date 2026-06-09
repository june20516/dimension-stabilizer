# Progress Log

## Session: 2026-06-08

### Phase 1: 개념 정립 & 연구
- **Status:** complete
- **Started:** 2026-06-08
- Actions taken:
  - 멀미(감각 충돌) 원인 및 개입 방식 2갈래 조사
  - 선행 연구 비교 (노이즈 주입 vs 방향 일치 진동) → findings.md 기록
  - 대상 정정: VR 아님 → 평면 3D 게임. 데이터 소스 HMD→입력장치 전환
  - 프로젝트 폴더 및 계획/설계 문서 구조 생성
  - 폴더명 오타 수정: dimension-syncronizer → dimension-synchronizer
  - 입력장치 확정: 마우스(주) + 컨트롤러(부). 공통 인터페이스(정규화 회전 속도)로 추상화 결정
  - 골전도 연구: 전정 자극 근거 주파수 ~500Hz 확인 (VEMP·vection). "저주파 보장" 부담 해소
  - 구현 경로 1차 검토: 단일 골전도 이어폰 + SW only
  - **최종 확정(사용자)**: **두 트랙 병행 검증** — A=골전도 이어폰(전정), B=아두이노+모터(촉각). 공통 코어 공유, OFF/A/B 3way 검증
  - 문서 재구성: task_plan / concept / hardware-design / software-architecture / build-roadmap / validation-plan / README 갱신
- Files created/modified:
  - task_plan.md (created)
  - findings.md (created)
  - progress.md (created)
  - README.md (created)
  - docs/concept-and-hypothesis.md (created)
  - docs/hardware-design.md (created)
  - docs/software-architecture.md (created)
  - docs/build-roadmap.md (created)
  - docs/validation-plan.md (created)

### Phase 2: 장비 준비 & 구매 (양 트랙)
- **Status:** in_progress
- Actions taken:
  - 골전도 부품 조사: 유선 완제품 희소 → 베어 트랜스듀서 자작으로 결정
  - 트랜스듀서 선정: 소형 8Ω 골전도(Adafruit #1674 / 동일 제네릭) ×2. **국내 정품 구매 완료(도착 대기)**
  - 알리 키워드 낚시 판별법 정리(Type/IEC-711/SPL → 탈락)
  - 주파수 정밀화: 반응대역 250–1000Hz(노이즈 1–4kHz) — 주파수는 관건 아님, 출력·효과가 변수
- Files created/modified:
  - findings.md (갱신)

## Session: 2026-06-09

### Phase 2/4 설계: Track A 마운트 확정
- **Status:** in_progress
- Actions taken:
  - 마운트 브레인스토밍(시각 컴패니언). 폼팩터 A(헤드폰)/B(헤드밴드)/C(이어후크) 비교 → B 탈락(수평 밴드가 유양돌기 못 지남)
  - 핵심 정립: **압착력이 골전도 1순위 변수**, 두개골 전체 전달로 유양돌기 정중앙 불필요(임상도 이마 Fz 사용)
  - 온이어→**오버이어 도너**로 전환(쿠션 링 뒤-아래가 유양돌기 통과). 트랜스듀서는 쿠션 도려내고 **돌출** 마운트(쿠션 위 부착 금지=댐핑·분산)
  - **Stage 0 사전 게이트** 정의(테이프+손압착 위치 지도, 아두이노+DRV8833 500Hz, 판단 트리)
  - 폴백 사다리: 1순위 오버이어 도너 / 2순위 골전도 이어폰 프레임 재사용
  - 도너 보유 현황: 헤드폰·골전도 없음, 안경만 → 싸구려 오버이어 신규 구매로 결정
- Files created/modified:
  - hardware-design.md (Track A 전면 개정), findings.md, task_plan.md, validation-plan.md, README.md

### Phase 3: 공통 코어 — 완료
- **Status:** complete
- Actions taken:
  - TDD로 공통 코어 구현 (RED→GREEN 반복, 테스트 21개 전부 통과)
  - `pc/config.py` CoreConfig(데드존·gain·max_level·attack/decay·mouse_scale)
  - `pc/mapping.py` `yaw_to_levels`(순수) + `LevelSmoother`(attack/decay, 채널별 독립)
  - `pc/input_mouse.py` MouseYawSource(pynput 글로벌 리스너, add_dx/poll 인터페이스로 I/O 분리)
  - `pc/core.py` 메인 루프 + level_bar 콘솔 표시. `python -m pc.core`로 실행
  - 마일스톤 검증: 우/좌 회전 시뮬레이션 → 해당 채널 차오름 + attack(빠름)/decay(느림) 확인
  - 환경: pc/.venv 생성, pynput 1.8.2 설치, requirements.txt/.gitignore 추가
- Files created/modified:
  - pc/config.py, pc/mapping.py, pc/input_mouse.py, pc/core.py (created)
  - pc/tests/{test_mapping,test_input_mouse,test_core}.py (created)
  - pc/requirements.txt, .gitignore (created), task_plan.md, progress.md

### 프로젝트명 변경: Dimension Synchronizer → **Dimension Stabilizer**
- 사유: 이름 어감(사용자 선호). 기존 명칭 사용 적어 비용 낮음(내용 4곳, 코드 0곳)
- 변경: README/task_plan 제목, `firmware/dimension_stabilizer.ino`(예정 파일명), 폴더 `~/personal/dimension-stabilizer`
- 유지: progress.md 과거 오타수정 로그(위 line 13)는 역사 기록이라 그대로 둠
- 영향: 테스트 21개·venv 정상. git 아님. 메모리 폴더 비어 무관

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| 우회전 시뮬 (dx=+15) | yaw=+0.30 | 오른쪽 채널만 상승 | R 0.15→0.25, L 0 | ✅ |
| 정지 | yaw=0 | decay로 천천히 하강 | R 0.25→0.06 | ✅ |
| 좌회전 시뮬 (dx=-15) | yaw=-0.30 | 왼쪽 채널 상승, 오른쪽 decay | L 0.15→0.25, R↓ | ✅ |
| 단위 테스트 전체 | — | 통과 | 21/21 OK | ✅ |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
|           |       | 1       |            |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 3(공통 코어) 완료. Phase 2는 부품 대기로 블로킹 |
| Where am I going? | 하드웨어 도착 → 4 Track A(이어폰) / 5 Track B(모터) → 8 3way 검증 |
| What's the goal? | 두 트랙(전정/촉각) 다 만들어 평면 3D 게임 멀미 완화 효과 비교 |
| What have I learned? | See findings.md. 공통 코어는 OS 무관(순수), 입력/오디오/시리얼만 OS 경계 |
| What have I done? | 공통 코어 TDD 구현·검증 완료(테스트 21개). 하드웨어 제작 미착수 |

---
*Update after completing each phase or encountering errors*
