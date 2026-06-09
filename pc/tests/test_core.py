"""코어 콘솔 표시 헬퍼 테스트 (메인 루프 I/O 제외, 순수 부분).

level_bar: level [0,1] → 고정폭 막대 문자열. clamp 포함.
"""
import unittest

from pc.core import level_bar


class LevelBarTest(unittest.TestCase):
    def test_empty_bar_is_all_dots(self):
        self.assertEqual(level_bar(0.0, 10), "." * 10)

    def test_full_bar_is_all_hashes(self):
        self.assertEqual(level_bar(1.0, 10), "#" * 10)

    def test_half_bar_is_half_filled(self):
        self.assertEqual(level_bar(0.5, 10), "#" * 5 + "." * 5)

    def test_clamps_above_one(self):
        self.assertEqual(level_bar(1.5, 10), "#" * 10)

    def test_clamps_below_zero(self):
        self.assertEqual(level_bar(-0.2, 10), "." * 10)


if __name__ == "__main__":
    unittest.main()
