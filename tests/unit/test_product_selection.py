import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from agent import product_selection
from validation.product_data import load_catalog

CATALOG, _ = load_catalog()


class TestSelectAgainstRealCatalog(unittest.TestCase):
    def test_rotary_nozzle_at_45psi_15ft(self):
        result = product_selection.select_products(
            CATALOG, "rotary_nozzle", design_pressure_psi=45.0, radius_needed_ft=15.0)
        models = [c.model for c in result.candidates]
        # 15 ft sits inside R-VAN18's 13-18 published range only
        self.assertTrue(all(m.startswith("R-VAN18") for m in models), models)
        self.assertTrue(models)
        # R-VAN14 (8-14) and R-VAN24 (17-24) excluded with radius reasons
        excluded = {e.model: e.reason for e in result.exclusions}
        self.assertTrue(any(m.startswith("R-VAN14") for m in excluded))
        self.assertIn("radius", next(r for m, r in excluded.items() if m.startswith("R-VAN14")))

    def test_low_pressure_excludes_rvan(self):
        result = product_selection.select_products(
            CATALOG, "rotary_nozzle", design_pressure_psi=25.0, radius_needed_ft=15.0)
        self.assertEqual(result.candidates, ())
        self.assertTrue(all("outside published" in e.reason for e in result.exclusions))

    def test_rotor_at_45psi_35ft(self):
        result = product_selection.select_products(
            CATALOG, "rotor", design_pressure_psi=45.0, radius_needed_ft=35.0)
        self.assertEqual([c.model for c in result.candidates], ["5004-PC"])

    def test_every_candidate_carries_source_url(self):
        result = product_selection.select_products(
            CATALOG, "spray_head", design_pressure_psi=45.0)
        self.assertTrue(result.candidates)
        for c in result.candidates:
            self.assertTrue(c.source_url.startswith("http"))

    def test_invalid_pressure_rejected(self):
        with self.assertRaises(ValueError):
            product_selection.select_products(CATALOG, "rotor", design_pressure_psi=0)


class TestPublishedPerformance(unittest.TestCase):
    def test_exact_row_lookup(self):
        row = product_selection.published_performance(
            "r-van18.csv", 45.0, {"arc_degrees": 270.0})
        self.assertEqual(row["flow_gpm"], 1.51)
        self.assertEqual(row["radius_ft"], 17.0)

    def test_unpublished_pressure_refused_with_available_list(self):
        with self.assertRaises(ValueError) as cm:
            product_selection.published_performance(
                "r-van18.csv", 42.0, {"arc_degrees": 270.0})
        self.assertIn("published pressures", str(cm.exception))

    def test_ambiguous_lookup_refused(self):
        # r-van18.csv has multiple arcs at 45 psi; no match keys = ambiguous
        with self.assertRaises(ValueError):
            product_selection.published_performance("r-van18.csv", 45.0)

    def test_missing_table_reported(self):
        with self.assertRaises(FileNotFoundError):
            product_selection.performance_rows("no-such-product.csv")

    def test_rotor_lookup_by_nozzle(self):
        row = product_selection.published_performance(
            "5004-pc.csv", 45.0, {"nozzle": 3.0})
        self.assertGreater(row["flow_gpm"], 0)
        self.assertGreater(row["radius_ft"], 20)


if __name__ == "__main__":
    unittest.main()
