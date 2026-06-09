# 소프트웨어 설계 (공통 코어 + 2개 출력 백엔드)

## 1. 데이터 흐름
```
입력장치 → [공통 코어: 입력 읽기 → yaw_rate → (left_level, right_level)]
                                   │
                ┌──────────────────┴───────────────────┐
        [Track A 백엔드]                        [Track B 백엔드]
   level → 500Hz 진폭/패닝 합성             level → 시리얼 → 아두이노
   → PC 오디오 출력(골전도 이어폰)          → PWM → 코인모터
```
**입력·매핑은 공통 코어에서 한 번만.** 출력만 두 백엔드로 분기.

## 2. 공통 코어
### 2.1 입력 읽기 (마우스 주 + 컨트롤러 부)
공통 인터페이스: 어떤 장치든 정규화 `yaw_rate`(좌우 회전 속도)를 낸다.
- **마우스 (1차)**: raw delta. `pynput`/`pygame`(`mouse.get_rel()`). 가로 delta ∝ yaw 속도.
- **컨트롤러 (2차)**: 오른쪽 스틱 X (`pygame`/XInput). 값 자체가 회전 속도.
  - 차이: 마우스 delta=상대값(프레임마다 0 리셋), 스틱=절대값(유지). 어댑터에서 흡수.

### 2.2 매핑 (yaw_rate → 좌/우 세기)
- `|yaw_rate|` → 세기, 부호 → 좌/우.
- **출력 표준: `(left_level, right_level)` 각 [0,1]** — 트랙 무관 정규화 값.
- 요소: **데드존**, **감도(gain)**, **상한(clamp)**, **attack/decay 스무딩**.

## 3. Track A 백엔드 — 골전도 이어폰 (전정 자극)
- **캐리어 500Hz** (전정 근거 주파수). 후보: 순수 톤 / 500Hz 대역 노이즈(연구의 "noisy stim"에 충실) — Phase 7 비교.
- `left_level`·`right_level` → 각 채널 캐리어 **진폭**으로, 스테레오 버퍼 합성.
- **출력**: `sounddevice`로 **이어폰 device index 지정**, 실시간 콜백(작은 블록)으로 저지연.
- 게임 오디오는 **기본 출력 장치**로 그대로 — 손대지 않음(독립 스트림).
- 연결: **유선·저지연**, 블루투스 회피.

## 4. Track B 백엔드 — 아두이노 + 모터 (촉각)
- `level` → PWM 값(0–255)로 스케일, 좌/우 모터에 매핑.
- **시리얼 프로토콜**(텍스트, 디버깅 쉬움): `L<0-255> R<0-255>\n` 예) `L180 R0\n`.
- **펌웨어**: 시리얼 파싱 → `analogWrite` + **워치독**(패킷 끊기면 모터 OFF).
- 회로·배선은 hardware-design.md §Track B.

## 5. 지연(latency)
- 단서는 타이밍이 생명 → 입력→진동 **수십 ms 이내** 목표.
- A: 유선 이어폰 + 작은 오디오 블록. B: USB 시리얼(115200+), 짧은 전송 주기.

## 6. 마일스톤 (구현 순서)
1. (Phase 3) 코어: 입력 → `(left_level, right_level)` 콘솔 출력.
2. (Phase 4) A: 장치 지정 500Hz 톤·패닝 → 코어 연결.
3. (Phase 5) B: LED→모터→시리얼 → 코어 연결.

## 7. 산출물 (예정)
- `pc/core.py` — 입력 어댑터 + 매핑 → `(left_level, right_level)` (공통)
- `pc/backend_audio.py` — Track A: 500Hz 합성 + 오디오 출력(장치 지정)
- `pc/backend_serial.py` — Track B: 시리얼 송신
- `firmware/dimension_stabilizer.ino` — Track B 펌웨어(파싱+PWM+워치독)
- `pc/config.py` — 장치/포트·감도·데드존·캐리어·attack/decay
