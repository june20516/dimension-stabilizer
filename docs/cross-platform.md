# 크로스플랫폼 전략 (Windows 위주 + macOS 보조)

결론부터: **이 프로젝트는 OS 무관하게 동작하도록 설계됨.** 공통 코어는 100% 이식 가능하고,
OS가 갈리는 지점은 **얇게 격리된 3개 경계**뿐이다. 코드/펌웨어/문서는 git으로 공유하고,
venv와 OS별 설정값만 각 머신에서 따로 둔다.

## 1. 이식성 현황 (지금까지 = 공통 코어)
| 모듈 | OS 의존 | 비고 |
|------|---------|------|
| `pc/config.py` | 없음 | 순수 dataclass |
| `pc/mapping.py` | 없음 | 순수 math (yaw→level, attack/decay) |
| `pc/input_mouse.py` | **경계 ①** | pynput 자체는 Win/macOS/Linux 지원 |
| `pc/core.py` | 없음 | `time`, `print('\r')` — 양쪽 터미널 OK |

- 요구사항: **Python 3.10+** (`X | None`, `tuple[...]` 문법).
- venv는 `.gitignore` 처리 → 커밋 안 됨. 각 OS에서 새로 만들고 `requirements.txt`로 재현.
- 경로 차이: macOS `pc/.venv/bin/`, Windows `pc\.venv\Scripts\`.

## 2. OS가 갈리는 3개 경계

### 경계 ① 마우스 입력 — `pc/input_mouse.py`
- **pynput**은 Windows/macOS/Linux 모두 지원 → 데스크톱 커서 추적은 양쪽 OK.
  - macOS: **입력 모니터링 권한** 필요. Windows: 권한 불필요.
- **실게임의 진짜 관문(=OS 차이가 아니라 입력 모드 문제):** FPS는 보통 **포인터 락(상대
  마우스 모드)** 으로 커서를 화면 중앙에 고정한다. 그러면 OS 커서가 안 움직여 pynput의
  `on_move`(절대 위치 기반)가 **양쪽 OS 모두에서** delta를 못 준다.
- **대응:** OS별 raw input 백엔드를 `MouseYawSource.add_dx()` 인터페이스 뒤에 끼운다
  (설계상 이미 분리됨 — pynput 부분만 교체).
  - **Windows**: Raw Input API(`WM_INPUT`/`GetRawInputData`) 또는 Interception 드라이버.
  - **macOS**: `CGEventTap` + `kCGMouseEventDeltaX` (커서 락에서도 delta 수신).
  - 실사용이 Windows 위주이므로 **Windows raw input을 우선 구현**, macOS는 데스크톱
    검증용 pynput로 충분(필요 시 CGEventTap 추가).

### 경계 ② 오디오 장치 — Track A `backend_audio.py` (Phase 4)
- **sounddevice(PortAudio)** 는 Win/macOS/Linux 지원 → 라이브러리 차원 이식 OK.
- 갈리는 건 **장치 선택**: device index와 host API가 다름
  (Windows **WASAPI/DirectSound**, macOS **CoreAudio**). 이어폰 장치명도 머신마다 다름.
  → 애초에 **머신별 설정**이라 OS 문제라기보다 환경 설정. `config`에 device 지정으로 흡수.
- 저지연: Windows는 WASAPI(가능하면 exclusive), macOS는 CoreAudio. sounddevice가 추상화.

### 경계 ③ 시리얼 포트 — Track B `backend_serial.py` (Phase 5)
- **pyserial** 양쪽 지원. Arduino 펌웨어는 보드에서 돌아 **OS 무관**.
- 갈리는 건 **포트 이름**뿐: Windows `COM3`, macOS `/dev/cu.usbmodemXXXX`(또는 `/dev/cu.usbserial-*`).
  → `config`의 `serial_port`로 지정. 자동탐색 시 `serial.tools.list_ports` 사용(크로스플랫폼).

## 3. 권장 워크플로
1. **공유(git)**: `pc/` 소스 + 테스트, `firmware/`, `docs/` — 전부 OS 무관.
2. **각 OS 로컬**: venv 생성 + `pip install -r pc/requirements.txt`.
3. **OS별 설정**: 시리얼 포트·오디오 device index는 `config`에서 분기하거나 머신별 오버라이드
   (예: 환경변수/로컬 설정 파일). 코드 분기 최소화.
4. **백엔드 분기**: 마우스 raw input만 OS별 모듈로 분리, 나머지는 단일 코드 + 설정값.

## 4. 한 줄 요약
> 순수 코어·펌웨어·문서는 그대로 양쪽에서. **마우스 raw input(게임용)** 만 OS별 백엔드가
> 필요하고, **오디오 장치·시리얼 포트**는 라이브러리는 공통이고 *설정값*만 다르다.
