"""마우스 입력 어댑터 — 가로 이동 → 정규화 yaw_rate (공통 코어 1차 입력).

규약: yaw_rate > 0 = 오른쪽 회전. 백엔드는 이 인터페이스만 알면 된다
(컨트롤러 어댑터도 동일한 poll() -> yaw_rate 형태로 Phase 6에서 추가).

스레드 모델: pynput 리스너 콜백 스레드가 add_dx()로 누적,
메인 루프가 poll()로 tick당 소비. 누적/리셋은 락으로 보호.

알려진 한계: pynput on_move는 절대 커서 위치 기반이라, 포인터 락(상대
마우스 모드)인 FPS에서는 커서가 안 움직여 dx가 0일 수 있다. Phase 3
데스크톱 검증에는 충분하며, 게임 통합 시 raw input 경로는 추후 과제.
"""
import threading

from pc.config import CoreConfig


class MouseYawSource:
    def __init__(self, config: CoreConfig) -> None:
        self._scale = config.mouse_scale
        self._accum_dx = 0.0
        self._lock = threading.Lock()
        self._prev_x: float | None = None
        self._listener = None  # pynput.mouse.Listener (start() 시 생성)

    def add_dx(self, dx: float) -> None:
        """가로 이동량 누적 (리스너 콜백 스레드에서 호출)."""
        with self._lock:
            self._accum_dx += dx

    def poll(self) -> float:
        """tick당 yaw_rate 반환 후 누적 리셋 (메인 루프에서 호출)."""
        with self._lock:
            dx = self._accum_dx
            self._accum_dx = 0.0
        return dx * self._scale

    # --- pynput I/O (지연 import; 단위 테스트 대상 아님) ---
    def start(self) -> None:
        from pynput import mouse

        def on_move(x: float, _y: float) -> None:
            if self._prev_x is not None:
                self.add_dx(x - self._prev_x)
            self._prev_x = x

        self._listener = mouse.Listener(on_move=on_move)
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
