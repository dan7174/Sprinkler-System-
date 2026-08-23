import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from calculators import pump

# Synthetic manufacturer-style curve used across tests (flow gpm, head ft)
CURVE = [(0, 180.0), (20, 170.0), (40, 150.0), (60, 120.0), (80, 80.0)]
CURVE_SOURCE = "synthetic test curve (fixture, not a real pump)"


class TestTotalDynamicHead(unittest.TestCase):
    def test_known_value(self):
        # 20 ft lift + 15 ft friction + 40 psi (92.4 ft) = 127.4 ft
        self.assertAlmostEqual(pump.total_dynamic_head_ft(20.0, 15.0, 92.4), 127.4, places=6)

    def test_flooded_suction_reduces_tdh(self):
        self.assertAlmostEqual(pump.total_dynamic_head_ft(-5.0, 15.0, 92.4), 102.4, places=6)

    def test_nonpositive_tdh_rejected(self):
        with self.assertRaises(ValueError):
            pump.total_dynamic_head_ft(-120.0, 15.0, 92.4)

    def test_negative_friction_rejected(self):
        with self.assertRaises(ValueError):
            pump.total_dynamic_head_ft(20.0, -1.0, 92.4)


class TestCurveInterpolation(unittest.TestCase):
    def test_exact_points_returned(self):
        self.assertEqual(pump.head_at_flow_ft(CURVE, 40.0), 150.0)
        self.assertEqual(pump.head_at_flow_ft(CURVE, 0.0), 180.0)
        self.assertEqual(pump.head_at_flow_ft(CURVE, 80.0), 80.0)

    def test_midpoint_interpolation(self):
        # Between (40,150) and (60,120): 50 gpm -> 135 ft
        self.assertAlmostEqual(pump.head_at_flow_ft(CURVE, 50.0), 135.0, places=9)

    def test_unsorted_input_accepted(self):
        shuffled = [CURVE[2], CURVE[0], CURVE[4], CURVE[1], CURVE[3]]
        self.assertAlmostEqual(pump.head_at_flow_ft(shuffled, 50.0), 135.0, places=9)

    def test_extrapolation_refused(self):
        with self.assertRaises(ValueError):
            pump.head_at_flow_ft(CURVE, 100.0)

    def test_duplicate_flows_rejected(self):
        with self.assertRaises(ValueError):
            pump.head_at_flow_ft([(40, 150.0), (40, 140.0)], 40.0)

    def test_single_point_rejected(self):
        with self.assertRaises(ValueError):
            pump.head_at_flow_ft([(40, 150.0)], 40.0)


class TestOperatingPoint(unittest.TestCase):
    def test_passing_operating_point(self):
        result = pump.check_operating_point(CURVE, 50.0, 127.4, CURVE_SOURCE)
        self.assertTrue(result.passes)
        self.assertAlmostEqual(result.pump_head_at_flow_ft, 135.0, places=9)
        self.assertAlmostEqual(result.margin_ft, 7.6, places=6)

    def test_failing_operating_point(self):
        result = pump.check_operating_point(CURVE, 70.0, 127.4, CURVE_SOURCE)
        self.assertFalse(result.passes)
        self.assertLess(result.margin_ft, 0)

    def test_curve_source_required(self):
        with self.assertRaises(ValueError):
            pump.check_operating_point(CURVE, 50.0, 127.4, "")


class TestNpsh(unittest.TestCase):
    def test_npsha_known_value(self):
        # Sea-level style example: 33.9 - 10 lift - 2 friction - 0.8 vapor = 21.1 ft
        self.assertAlmostEqual(pump.npsh_available_ft(33.9, 10.0, 2.0, 0.8), 21.1, places=6)

    def test_flooded_suction_adds_head(self):
        flooded = pump.npsh_available_ft(33.9, -5.0, 2.0, 0.8)
        lifted = pump.npsh_available_ft(33.9, 5.0, 2.0, 0.8)
        self.assertGreater(flooded, lifted)

    def test_npsh_check_passes_with_margin(self):
        result = pump.check_npsh(21.1, 15.0, 2.0)
        self.assertTrue(result.passes)
        self.assertAlmostEqual(result.margin_ft, 4.1, places=6)

    def test_npsh_check_fails_when_short(self):
        result = pump.check_npsh(16.0, 15.0, 2.0)
        self.assertFalse(result.passes)


if __name__ == "__main__":
    unittest.main()
