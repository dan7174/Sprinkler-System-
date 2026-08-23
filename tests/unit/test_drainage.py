import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from calculators import drainage


class TestRationalMethod(unittest.TestCase):
    def test_known_value(self):
        # C=0.9 roof/pavement, i=2.5 in/hr, A=0.5 acre -> 1.125 cfs
        self.assertAlmostEqual(drainage.rational_peak_flow_cfs(0.9, 2.5, 0.5), 1.125, places=9)

    def test_coefficient_above_one_rejected(self):
        with self.assertRaises(ValueError):
            drainage.rational_peak_flow_cfs(1.2, 2.5, 0.5)

    def test_zero_area_rejected(self):
        with self.assertRaises(ValueError):
            drainage.rational_peak_flow_cfs(0.9, 2.5, 0.0)


class TestSlope(unittest.TestCase):
    def test_one_percent_grade(self):
        self.assertAlmostEqual(drainage.slope_ft_per_ft(1.0, 100.0), 0.01, places=9)

    def test_zero_run_rejected(self):
        with self.assertRaises(ValueError):
            drainage.slope_ft_per_ft(1.0, 0.0)


class TestManningsCapacity(unittest.TestCase):
    def test_4in_pvc_at_one_percent(self):
        # 4 in smooth pipe (n=0.010) at 1%: computed 0.248 cfs (about 111 gpm),
        # consistent with published gravity-drain capacity tables.
        q = drainage.mannings_full_flow_cfs(4.0, 0.01, 0.010)
        self.assertAlmostEqual(q, 0.248, delta=0.005)

    def test_larger_pipe_carries_more(self):
        q4 = drainage.mannings_full_flow_cfs(4.0, 0.01, 0.010)
        q6 = drainage.mannings_full_flow_cfs(6.0, 0.01, 0.010)
        self.assertGreater(q6, q4)
        # capacity grows faster than area (R also grows): ratio > (6/4)^2
        self.assertGreater(q6 / q4, (6.0 / 4.0) ** 2)

    def test_steeper_slope_carries_more(self):
        flat = drainage.mannings_full_flow_cfs(4.0, 0.005, 0.010)
        steep = drainage.mannings_full_flow_cfs(4.0, 0.02, 0.010)
        self.assertGreater(steep, flat)
        # Q scales with sqrt(S): 4x slope -> 2x capacity
        self.assertAlmostEqual(steep / flat, 2.0, places=9)

    def test_rougher_pipe_carries_less(self):
        smooth = drainage.mannings_full_flow_cfs(4.0, 0.01, 0.010)
        rough = drainage.mannings_full_flow_cfs(4.0, 0.01, 0.020)
        self.assertAlmostEqual(rough, smooth / 2.0, places=9)

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            drainage.mannings_full_flow_cfs(0.0, 0.01, 0.010)
        with self.assertRaises(ValueError):
            drainage.mannings_full_flow_cfs(4.0, -0.01, 0.010)


if __name__ == "__main__":
    unittest.main()
