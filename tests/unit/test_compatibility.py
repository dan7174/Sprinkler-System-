import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from agent.compatibility import check_zone

RVAN_RANGE = {"min": 30, "max": 55}


def rvan(model="R-VAN18", flow=1.0, arc=90):
    return {"model": model, "application_type": "rotary_nozzle",
            "flow_gpm": flow, "arc_degrees": arc, "pressure_range_psi": RVAN_RANGE}


class TestZoneCompatibility(unittest.TestCase):
    def test_matched_family_passes(self):
        # quarter 1.0, half 2.0, full 4.0 = matched precipitation
        devices = [rvan(flow=1.0, arc=90), rvan(flow=2.0, arc=180), rvan(flow=4.0, arc=360)]
        result = check_zone(devices, 45.0, 10.0)
        self.assertTrue(result.passes, result.failures)
        self.assertEqual(result.failures, ())

    def test_mixed_methods_fail(self):
        rotor = {"model": "5004-PC", "application_type": "rotor",
                 "flow_gpm": 3.0, "arc_degrees": 180,
                 "pressure_range_psi": {"min": 25, "max": 65}}
        result = check_zone([rvan(), rotor], 45.0, 10.0)
        self.assertFalse(result.passes)
        self.assertTrue(any("mixed application methods" in f for f in result.failures))

    def test_pressure_outside_published_range_fails(self):
        result = check_zone([rvan()], 25.0, 10.0)  # R-VAN min is 30 psi
        self.assertFalse(result.passes)
        self.assertTrue(any("outside its published range" in f for f in result.failures))

    def test_overcapacity_zone_fails(self):
        devices = [rvan(flow=3.0, arc=90), rvan(flow=3.0, arc=90), rvan(flow=3.0, arc=90)]
        result = check_zone(devices, 45.0, 8.0)
        self.assertFalse(result.passes)
        self.assertTrue(any("exceeds the safe zone flow" in f for f in result.failures))

    def test_unmatched_precipitation_fails(self):
        # quarter at 1 gpm (4.0 equivalent) with full at 2 gpm (2.0 equivalent)
        result = check_zone([rvan(flow=1.0, arc=90), rvan(flow=2.0, arc=360)], 45.0, 10.0)
        self.assertFalse(result.passes)
        self.assertTrue(any("not matched" in f for f in result.failures))

    def test_high_utilization_warns_but_passes(self):
        result = check_zone([rvan(flow=3.5, arc=180), rvan(flow=3.5, arc=180)], 45.0, 8.0)
        self.assertTrue(result.passes)
        self.assertTrue(any("80%" in w for w in result.warnings))

    def test_missing_pressure_range_fails_loudly(self):
        d = rvan(); d = dict(d); del d["pressure_range_psi"]
        result = check_zone([d], 45.0, 10.0)
        self.assertFalse(result.passes)
        self.assertTrue(any("no published pressure range" in f for f in result.failures))

    def test_empty_zone_rejected(self):
        with self.assertRaises(ValueError):
            check_zone([], 45.0, 10.0)


if __name__ == "__main__":
    unittest.main()
