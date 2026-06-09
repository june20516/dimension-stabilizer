"""공통 코어 메인 루프 — Phase 3 마일스톤.

마우스 회전 → yaw_rate → (left_level, right_level) 콘솔 실시간 출력.
이 파이프라인(입력 → 매핑 → 스무딩)을 두 출력 백엔드가 그대로 재사용한다:
  - Track A: (left, right) → 500Hz 진폭/패닝 → 오디오 (backend_audio.py)
  - Track B: (left, right) → PWM 0-255 → 시리얼 (backend_serial.py)

실행: python -m pc.core   (마우스를 좌우로 움직이면 해당 채널 막대가 차오름)
종료: Ctrl-C
macOS: 입력 모니터링 권한 필요 (시스템 설정 > 손쉬운 사용/입력 모니터링).
"""
import time

from pc.config import CoreConfig
from pc.input_mouse import MouseYawSource
from pc.mapping import LevelSmoother, yaw_to_levels

TICK_HZ = 60
_BAR_WIDTH = 12


def level_bar(level: float, width: int = _BAR_WIDTH) -> str:
    """level [0,1] → 고정폭 막대 문자열 ('#' 채움, '.' 빈칸). 범위 밖은 clamp."""
    clamped = min(1.0, max(0.0, level))
    filled = round(clamped * width)
    return "#" * filled + "." * (width - filled)


def render_line(left: float, right: float, yaw_rate: float) -> str:
    """좌/우 막대를 가운데 기준 대칭으로 한 줄에 표시."""
    left_bar = level_bar(left)[::-1]  # 왼쪽 채널은 가운데서 바깥으로 차오르게 반전
    return (
        f"L {left_bar} {left:4.2f} |{right:4.2f} {level_bar(right)} R"
        f"   yaw={yaw_rate:+.3f}"
    )


def run(config: CoreConfig | None = None) -> None:
    config = config or CoreConfig()
    source = MouseYawSource(config)
    smoother = LevelSmoother(config)
    period = 1.0 / TICK_HZ

    source.start()
    print("공통 코어 실행 중 — 마우스를 좌우로 움직여 보세요 (Ctrl-C 종료)")
    try:
        while True:
            yaw_rate = source.poll()
            left_target, right_target = yaw_to_levels(yaw_rate, config)
            left, right = smoother.update(left_target, right_target)
            print(render_line(left, right, yaw_rate), end="\r", flush=True)
            time.sleep(period)
    except KeyboardInterrupt:
        pass
    finally:
        source.stop()
        print()


if __name__ == "__main__":
    run()
