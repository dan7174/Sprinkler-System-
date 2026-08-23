import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from calculators import precipitation


class TestRectangularPrecipitation(unittest.TestCase):
    def test_square_spacing_example(self):
        # 15 x 15 ft square spacing, 3.0 gpm total zone flow:
        # PR = 96.3 * 3 / 225 = 1.284 in/hr
        pr = precipitation.precipitation_rate_rectangular(3.0, 15.0, 15.0)
        self.assertAlmostEqual(pr, 1.284, places=3)

    def test_rectangular_spacing_example(self):
        # 12 ft heads x 15 ft rows, 2.5 gpm:
        # PR = 96.3 * 2.5 / 180 = 1.3375 in/hr
        pr = precipitation.precipitation_rate_rectangular(2.5, 12.0, 15.0)
        self.assertAlmostEqual(pr, 1.3375, places=4)

    def test_hand_calculation_cross_check(self):
        # Independent second method (docs/08 section 24): 1 gpm on 100 sqft
        # = 60 gal/hr = 60 * 231 in^3 over 14400 in^2 = 0.9625 in/hr,
        # matching 96.3/100 within the constant's rounding.
        pr = precipitation.precipitation_rate_rectangular(1.0, 10.0, 10.0)
        self.assertAlmostEqual(pr, 0.9625, delta=0.001)

    def test_zero_and_negative_rejected(self):
        with self.assertRaises(ValueError):
            precipitation.precipitation_rate_rectangular(0.0, 15.0, 15.0)
        with self.assertRaises(ValueError):
            precipitation.precipitation_rate_rectangular(3.0, -15.0, 15.0)


class TestTriangularPrecipitation(unittest.TestCase):
    def test_triangular_beats_square_for_same_flow(self):
        # Triangular area per head is smaller (S * 0.866S), so PR is higher.
        square = precipitation.precipitation_rate_rectangular(3.0, 15.0, 15.0)
        triangular = precipitation.precipitation_rate_triangular(3.0, 15.0)
        self.assertGreater(triangular, square)
        self.assertAlmostEqual(triangular, square / 0.866, places=6)

    def test_triangular_known_value(self):
        # PR = 96.3 * 3 / (15 * 0.866 * 15) = 1.4827 in/hr
        pr = precipitation.precipitation_rate_triangular(3.0, 15.0)
        self.assertAlmostEqual(pr, 1.4827, places=3)


class TestAreaPrecipitation(unittest.TestCase):
    def test_area_form_matches_grid_form(self):
        grid = precipitation.precipitation_rate_rectangular(3.0, 15.0, 15.0)
        area = precipitation.precipitation_rate_from_area(3.0, 225.0)
        self.assertAlmostEqual(grid, area, places=9)


class TestPartCircleAndMatchedPrecipitation(unittest.TestCase):
    def test_full_circle_equivalents(self):
        self.assertAlmostEqual(precipitation.full_circle_equivalent_gpm(1.0, 90.0), 4.0)
        self.assertAlmostEqual(precipitation.full_circle_equivalent_gpm(2.0, 180.0), 4.0)
        self.assertAlmostEqual(precipitation.full_circle_equivalent_gpm(4.0, 360.0), 4.0)

    def test_arc_over_360_rejected(self):
        with self.assertRaises(ValueError):
            precipitation.full_circle_equivalent_gpm(1.0, 400.0)

    def test_matched_family_passes(self):
        # Classic matched-precipitation nozzle family:
        # quarter 1 gpm, half 2 gpm, full 4 gpm.
        result = precipitation.matched_precipitation_check(
            [(1.0, 90.0), (2.0, 180.0), (4.0, 360.0)]
        )
        self.assertTrue(result["matched"])
        self.assertAlmostEqual(result["spread_fraction"], 0.0, places=9)

    def test_mismatched_heads_fail(self):
        # Quarter at 1 gpm (4.0 equivalent) mixed with full at 2 gpm
        # (2.0 equivalent): the quarter area gets double the water.
        result = precipitation.matched_precipitation_check(
            [(1.0, 90.0), (2.0, 360.0)]
        )
        self.assertFalse(result["matched"])
        self.assertAlmostEqual(result["spread_fraction"], 1.0, places=9)

    def test_empty_zone_rejected(self):
        with self.assertRaises(ValueError):
            precipitation.matched_precipitation_check([])


if __name__ == "__main__":
    unittest.main()
