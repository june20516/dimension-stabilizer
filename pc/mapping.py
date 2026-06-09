"""공통 코어 매핑 — yaw_rate → (left_level, right_level).

순수 로직(하드웨어 무관). 두 출력 백엔드가 그대로 재사용한다.
부호 규약: yaw_rate > 0 = 오른쪽 회전 → 오른쪽 채널.
"""
from pc.config import CoreConfig

Levels = tuple[float, float]  # (left, right), 각 [0, max_level]


def yaw_to_levels(yaw_rate: float, config: CoreConfig) -> Levels:
    """회전 속도를 좌/우 세기로 변환 (스무딩 전 순간값).

    데드존 차감 → gain 적용 → max_level clamp → 부호로 채널 선택.
    데드존을 빼서 경계에서 level이 0부터 연속적으로 시작한다.
    """
    magnitude = abs(yaw_rate)
    if magnitude <= config.deadzone:
        return (0.0, 0.0)

    level = (magnitude - config.deadzone) * config.gain
    level = min(level, config.max_level)

    if yaw_rate > 0:
        return (0.0, level)   # 오른쪽 회전 → 오른쪽 채널
    return (level, 0.0)       # 왼쪽 회전 → 왼쪽 채널


class LevelSmoother:
    """attack/decay 1차 스무딩. 채널별 독립 상태 유지.

    매 tick `update(target)`로 현재 level을 목표값 쪽으로 보간한다.
    상승 시 attack, 하강 시 decay 계수 사용 → "빨리 켜지고 천천히 꺼짐".
    """

    def __init__(self, config: CoreConfig) -> None:
        self._config = config
        self._left = 0.0
        self._right = 0.0

    def update(self, left_target: float, right_target: float) -> Levels:
        self._left = self._approach(self._left, left_target)
        self._right = self._approach(self._right, right_target)
        return (self._left, self._right)

    def _approach(self, current: float, target: float) -> float:
        coeff = self._config.attack if target > current else self._config.decay
        return current + (target - current) * coeff
