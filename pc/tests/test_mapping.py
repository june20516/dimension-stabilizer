"""공통 코어 매핑 로직 테스트 (의존성 없음, stdlib unittest).

검증 대상: yaw_rate → (left_level, right_level) 순수 변환 + attack/decay 스무딩.
부호 규약: yaw_rate > 0 = 오른쪽 회전 → 오른쪽 채널.
"""
import unittest

from pc.config import CoreConfig
from pc.mapping import yaw_to_levels, LevelSmoother


class YawToLevelsTest(unittest.TestCase):
    def test_zero_yaw_gives_silence(self):
        cfg = CoreConfig(deadzone=0.0, gain=1.0, max_level=1.0)
        self.assertEqual(yaw_to_levels(0.0, cfg), (0.0, 0.0))

    def test_right_turn_drives_right_channel_only(self):
        cfg = CoreConfig(deadzone=0.0, gain=1.0, max_level=1.0)
        left, right = yaw_to_levels(0.5, cfg)
        self.assertEqual(left, 0.0)
        self.assertAlmostEqual(right, 0.5)

    def test_left_turn_drives_left_channel_only(self):
        cfg = CoreConfig(deadzone=0.0, gain=1.0, max_level=1.0)
        left, right = yaw_to_levels(-0.5, cfg)
        self.assertAlmostEqual(left, 0.5)
        self.assertEqual(right, 0.0)

    def test_within_deadzone_gives_silence(self):
        cfg = CoreConfig(deadzone=0.2, gain=1.0, max_level=1.0)
        self.assertEqual(yaw_to_levels(0.1, cfg), (0.0, 0.0))
        self.assertEqual(yaw_to_levels(-0.2, cfg), (0.0, 0.0))

    def test_deadzone_is_subtracted_for_continuity(self):
        # 데드존 경계 바로 위에서는 level이 0에서 연속적으로 시작.
        cfg = CoreConfig(deadzone=0.2, gain=1.0, max_level=1.0)
        _, right = yaw_to_levels(0.25, cfg)
        self.assertAlmostEqual(right, 0.05)

    def test_gain_scales_level(self):
        cfg = CoreConfig(deadzone=0.0, gain=2.0, max_level=10.0)
        _, right = yaw_to_levels(0.3, cfg)
        self.assertAlmostEqual(right, 0.6)

    def test_level_is_clamped_to_max(self):
        cfg = CoreConfig(deadzone=0.0, gain=1.0, max_level=1.0)
        _, right = yaw_to_levels(5.0, cfg)
        self.assertEqual(right, 1.0)


class LevelSmootherTest(unittest.TestCase):
    def test_instant_when_coeffs_are_one(self):
        cfg = CoreConfig(attack=1.0, decay=1.0)
        s = LevelSmoother(cfg)
        self.assertEqual(s.update(0.0, 0.8), (0.0, 0.8))

    def test_attack_rises_gradually_toward_target(self):
        cfg = CoreConfig(attack=0.5, decay=0.5)
        s = LevelSmoother(cfg)
        # 0 → 1 목표, attack=0.5 → 0.5, 0.75, ...
        _, r1 = s.update(0.0, 1.0)
        self.assertAlmostEqual(r1, 0.5)
        _, r2 = s.update(0.0, 1.0)
        self.assertAlmostEqual(r2, 0.75)

    def test_decay_falls_gradually_toward_target(self):
        cfg = CoreConfig(attack=1.0, decay=0.5)
        s = LevelSmoother(cfg)
        s.update(0.0, 1.0)  # attack=1 → right=1.0 즉시
        _, r = s.update(0.0, 0.0)  # 목표 하강 → decay=0.5 → 0.5
        self.assertAlmostEqual(r, 0.5)

    def test_attack_and_decay_apply_per_channel_independently(self):
        cfg = CoreConfig(attack=1.0, decay=0.5)
        s = LevelSmoother(cfg)
        # 왼쪽 채널 먼저 채움
        l, _ = s.update(1.0, 0.0)
        self.assertAlmostEqual(l, 1.0)
        # 왼쪽 하강(decay), 오른쪽 상승(attack) 동시
        l2, r2 = s.update(0.0, 1.0)
        self.assertAlmostEqual(l2, 0.5)
        self.assertAlmostEqual(r2, 1.0)


if __name__ == "__main__":
    unittest.main()
