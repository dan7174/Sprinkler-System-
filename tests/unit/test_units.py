import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from calculators import units


class TestPressureHeadConversions(unittest.TestCase):
    def test_psi_to_feet_known_value(self):
        # 1 psi supports about 2.31 ft of water (Rain Bird LIDM standard value)
        self.assertAlmostEqual(units.psi_to_feet_of_head(1.0), 2.31, places=6)

    def test_feet_to_psi_known_value(self):
        # 10 ft of water column is about 4.33 psi
        self.assertAlmostEqual(units.feet_of_head_to_psi(10.0), 4.33, places=6)

    def test_round_trip_is_consistent_within_rounding(self):
        # 2.31 and 0.433 are independently rounded published values;
        # a round trip must agree within that rounding error (<0.1%).
        round_trip = units.feet_of_head_to_psi(units.psi_to_feet_of_head(50.0))
        self.assertAlmostEqual(round_trip, 50.0, delta=50.0 * 0.001)

    def test_negative_sign_preserved_for_pressure_head(self):
        self.assertLess(units.psi_to_feet_of_head(-5.0), 0)


class TestFlowConversions(unittest.TestCase):
    def test_gpm_to_gph(self):
        self.assertEqual(units.gpm_to_gph(2.5), 150.0)

    def test_gph_to_gpm(self):
        self.assertEqual(units.gph_to_gpm(60.0), 1.0)

    def test_gpm_to_cfs_known_value(self):
        # 448.831 gpm = 1 cfs
        self.assertAlmostEqual(units.gpm_to_cfs(448.831), 1.0, places=6)

    def test_negative_flow_rejected(self):
        with self.assertRaises(ValueError):
            units.gpm_to_gph(-1.0)


class TestExactConversions(unittest.TestCase):
    def test_gallons_to_liters_exact(self):
        self.assertAlmostEqual(units.gallons_to_liters(1.0), 3.785411784, places=9)

    def test_inches_to_millimeters_exact(self):
        self.assertEqual(units.inches_to_millimeters(1.0), 25.4)

    def test_psi_to_kpa(self):
        self.assertAlmostEqual(units.psi_to_kpa(1.0), 6.894757, places=6)


class TestInputRejection(unittest.TestCase):
    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            units.psi_to_feet_of_head(math.nan)

    def test_infinity_rejected(self):
        with self.assertRaises(ValueError):
            units.gpm_to_gph(math.inf)

    def test_non_number_rejected(self):
        with self.assertRaises(ValueError):
            units.psi_to_kpa("50")

    def test_boolean_rejected(self):
        with self.assertRaises(ValueError):
            units.gpm_to_gph(True)


if __name__ == "__main__":
    unittest.main()
