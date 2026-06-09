"""마우스 입력 어댑터의 정규화 로직 테스트 (pynput I/O 제외, 순수 부분).

MouseYawSource: 리스너 콜백이 add_dx()로 가로 이동을 누적하고,
메인 루프가 poll()로 tick당 yaw_rate를 읽어간다(읽으면 리셋).
"""
import unittest

from pc.config import CoreConfig
from pc.input_mouse import MouseYawSource


class MouseYawSourceTest(unittest.TestCase):
    def setUp(self):
        self.cfg = CoreConfig(mouse_scale=0.02)

    def test_no_movement_gives_zero_yaw(self):
        src = MouseYawSource(self.cfg)
        self.assertEqual(src.poll(), 0.0)

    def test_poll_scales_accumulated_dx(self):
        src = MouseYawSource(self.cfg)
        src.add_dx(10)
        self.assertAlmostEqual(src.poll(), 0.2)

    def test_poll_resets_accumulator(self):
        src = MouseYawSource(self.cfg)
        src.add_dx(10)
        src.poll()
        self.assertEqual(src.poll(), 0.0)

    def test_multiple_dx_accumulate_within_tick(self):
        src = MouseYawSource(self.cfg)
        src.add_dx(5)
        src.add_dx(5)
        self.assertAlmostEqual(src.poll(), 0.2)

    def test_negative_dx_gives_negative_yaw(self):
        src = MouseYawSource(self.cfg)
        src.add_dx(-10)
        self.assertAlmostEqual(src.poll(), -0.2)


if __name__ == "__main__":
    unittest.main()
