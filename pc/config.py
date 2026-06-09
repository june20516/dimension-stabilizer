"""공통 코어 설정 — 장치/감도/스무딩 파라미터 (트랙 무관).

출력 백엔드(Track A 오디오, Track B 시리얼)가 공유하는 정규화 파라미터.
장치별 스케일(오디오 진폭, PWM 0-255)은 각 백엔드에서 따로 적용.
"""
from dataclasses import dataclass


@dataclass
class CoreConfig:
    # 매핑 (yaw_rate → level)
    deadzone: float = 0.05   # |yaw_rate| 이 값 이하면 무출력 (손떨림 무시)
    gain: float = 1.0        # yaw_rate → level 스케일(감도)
    max_level: float = 1.0   # level 상한 (clamp)

    # 스무딩 (0..1, 1=즉시반응). 진동이 따라붙는 속도.
    attack: float = 0.6      # level 상승 시 계수 (빠르게 켜짐)
    decay: float = 0.25      # level 하강 시 계수 (천천히 꺼짐)

    # 입력 정규화 (마우스 delta → yaw_rate)
    mouse_scale: float = 0.02  # 픽셀 delta → yaw_rate 변환 계수
