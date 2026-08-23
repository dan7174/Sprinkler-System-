import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from calculators import scheduling


class TestPlantDemand(unittest.TestCase):
    def test_etc_known_value(self):
        # ETo 0.20 in/day, Kc 0.8 -> ETc 0.16 in/day
        self.assertAlmostEqual(
            scheduling.crop_evapotranspiration_in_per_day(0.20, 0.8), 0.16, places=9
        )

    def test_implausible_coefficient_rejected(self):
        with self.assertRaises(ValueError):
            scheduling.crop_evapotranspiration_in_per_day(0.20, 2.5)

    def test_rain_reduces_demand_but_not_below_zero(self):
        self.assertAlmostEqual(scheduling.net_daily_demand_in(0.16, 0.06), 0.10, places=9)
        self.assertEqual(scheduling.net_daily_demand_in(0.16, 0.50), 0.0)


class TestIntervalAndDepth(unittest.TestCase):
    def test_raw_known_value(self):
        # Loam AWHC 2.0 in/ft, 6 in (0.5 ft) turf roots, 50% MAD -> 0.5 in
        self.assertAlmostEqual(
            scheduling.readily_available_water_in(2.0, 0.5, 0.5), 0.5, places=9
        )

    def test_mad_above_one_rejected(self):
        with self.assertRaises(ValueError):
            scheduling.readily_available_water_in(2.0, 0.5, 1.5)

    def test_interval_known_value(self):
        # 0.5 in RAW / 0.16 in/day = 3.125 days between irrigations
        self.assertAlmostEqual(scheduling.irrigation_interval_days(0.5, 0.16), 3.125, places=9)

    def test_gross_depth_known_value(self):
        # 0.5 in net at 75% efficiency -> 0.667 in gross
        self.assertAlmostEqual(scheduling.gross_depth_in(0.5, 0.75), 0.6667, places=4)

    def test_impossible_efficiency_rejected(self):
        with self.assertRaises(ValueError):
            scheduling.gross_depth_in(0.5, 1.2)


class TestRuntime(unittest.TestCase):
    def test_runtime_known_value(self):
        # 0.6667 in gross at PR 1.5 in/hr -> 26.67 minutes
        self.assertAlmostEqual(scheduling.runtime_minutes(0.6667, 1.5), 26.67, places=2)

    def test_hand_calculation_cross_check(self):
        # Independent check: 1.0 in at 2.0 in/hr is half an hour.
        self.assertEqual(scheduling.runtime_minutes(1.0, 2.0), 30.0)


class TestCycleAndSoak(unittest.TestCase):
    def test_max_cycle_known_value(self):
        # PR 1.5, intake 0.5, storage 0.1 in -> 60*0.1/1.0 = 6 minutes
        self.assertAlmostEqual(
            scheduling.max_cycle_minutes_before_runoff(1.5, 0.5, 0.1), 6.0, places=9
        )

    def test_no_limit_when_soil_keeps_up(self):
        self.assertIsNone(scheduling.max_cycle_minutes_before_runoff(0.4, 0.5, 0.1))

    def test_split_into_cycles(self):
        plan = scheduling.cycle_and_soak(26.67, 6.0)
        self.assertTrue(plan.cycle_and_soak_required)
        self.assertEqual(plan.cycles, 5)
        self.assertAlmostEqual(plan.minutes_per_cycle, 26.67 / 5, places=9)
        self.assertLessEqual(plan.minutes_per_cycle, 6.0)

    def test_single_cycle_when_within_limit(self):
        plan = scheduling.cycle_and_soak(5.0, 6.0)
        self.assertFalse(plan.cycle_and_soak_required)
        self.assertEqual(plan.cycles, 1)
        self.assertEqual(plan.minutes_per_cycle, 5.0)

    def test_no_runoff_limit_means_one_cycle(self):
        plan = scheduling.cycle_and_soak(45.0, None)
        self.assertEqual(plan.cycles, 1)


if __name__ == "__main__":
    unittest.main()
