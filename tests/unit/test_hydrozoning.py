import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from agent import hydrozoning
from validation.product_data import load_catalog

CATALOG, _ = load_catalog()


def area(name, plant="turf", sun="full_sun", soil="silt loam", slope=2.0,
         sqft=800.0, min_dim=20.0):
    return {"name": name, "plant_type": plant, "sun_exposure": sun,
            "soil_texture": soil, "slope_percent": slope,
            "area_sqft": sqft, "min_dimension_ft": min_dim}


class TestSlopeClass(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(hydrozoning.slope_class(0), "flat")
        self.assertEqual(hydrozoning.slope_class(5), "flat")
        self.assertEqual(hydrozoning.slope_class(8), "moderate")
        self.assertEqual(hydrozoning.slope_class(20), "steep")

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            hydrozoning.slope_class(-1)


class TestFeasibleMethods(unittest.TestCase):
    def test_beds_route_to_drip(self):
        opts = hydrozoning.feasible_methods("shrubs", 6.0, CATALOG)
        self.assertEqual(opts[0].method, "drip")

    def test_trees_route_to_tree_watering(self):
        opts = hydrozoning.feasible_methods("trees", 10.0, CATALOG)
        self.assertEqual(opts[0].method, "tree_watering")

    def test_large_turf_offers_rotor_first(self):
        # 5004-PC publishes 25-50 ft radius: feasible at 30 ft dimension.
        opts = hydrozoning.feasible_methods("turf", 30.0, CATALOG)
        self.assertEqual(opts[0].method, "rotor")
        self.assertTrue(any("5004" in m for m in opts[0].example_products))

    def test_mid_turf_offers_rotary_nozzles(self):
        # 15 ft strip: below the rotor's published 25 ft minimum,
        # within R-VAN14 (8-14) and R-VAN18 (13-18) minimums.
        opts = hydrozoning.feasible_methods("turf", 15.0, CATALOG)
        methods = [o.method for o in opts]
        self.assertNotIn("rotor", methods)
        self.assertEqual(opts[0].method, "rotary_nozzle")

    def test_tiny_strip_falls_back_when_no_product_fits(self):
        # 5 ft strip: smallest published radius in catalog is 8 ft (R-VAN14).
        opts = hydrozoning.feasible_methods("turf", 5.0, CATALOG)
        self.assertEqual(opts[0].method, "drip")
        self.assertIn("catalog", opts[0].reason)

    def test_unknown_plant_type_rejected(self):
        with self.assertRaises(ValueError):
            hydrozoning.feasible_methods("cactus_farm", 10.0, CATALOG)


class TestAssignHydrozones(unittest.TestCase):
    def test_same_conditions_group_together(self):
        zones = hydrozoning.assign_hydrozones(
            [area("front lawn"), area("back lawn")], CATALOG)
        self.assertEqual(len(zones), 1)
        self.assertEqual(zones[0].total_area_sqft, 1600.0)
        self.assertEqual(zones[0].areas, ("front lawn", "back lawn"))

    def test_sun_exposure_splits_zones(self):
        zones = hydrozoning.assign_hydrozones(
            [area("front lawn"), area("shade lawn", sun="shade")], CATALOG)
        self.assertEqual(len(zones), 2)

    def test_plant_type_splits_zones(self):
        zones = hydrozoning.assign_hydrozones(
            [area("lawn"), area("beds", plant="shrubs", min_dim=5)], CATALOG)
        self.assertEqual(len(zones), 2)
        methods = {z.method for z in zones}
        self.assertEqual(methods, {"rotary_nozzle", "drip"})

    def test_slope_class_splits_zones(self):
        zones = hydrozoning.assign_hydrozones(
            [area("flat lawn", slope=2), area("bank", slope=20)], CATALOG)
        self.assertEqual(len(zones), 2)

    def test_missing_field_rejected(self):
        with self.assertRaises(ValueError):
            hydrozoning.assign_hydrozones([{"name": "bad"}], CATALOG)


class TestValveZoneGrouping(unittest.TestCase):
    def devices(self, flows, key=("turf",)):
        return [{"flow_gpm": f, "hydrozone_key": key} for f in flows]

    def test_within_limit_single_zone(self):
        zones = hydrozoning.group_into_valve_zones(self.devices([1, 1, 2]), 8.0)
        self.assertEqual(len(zones), 1)
        self.assertEqual(zones[0].total_flow_gpm, 4.0)

    def test_split_when_over_limit(self):
        zones = hydrozoning.group_into_valve_zones(self.devices([3, 3, 3, 3]), 8.0)
        self.assertEqual(len(zones), 2)
        for z in zones:
            self.assertLessEqual(z.total_flow_gpm, 8.0)

    def test_hydrozones_never_mix(self):
        devs = self.devices([1, 1], key=("turf",)) + self.devices([1, 1], key=("shrubs",))
        zones = hydrozoning.group_into_valve_zones(devs, 8.0)
        self.assertEqual(len(zones), 2)
        keys = {z.hydrozone_key for z in zones}
        self.assertEqual(len(keys), 2)

    def test_single_oversized_device_is_an_error(self):
        with self.assertRaises(ValueError):
            hydrozoning.group_into_valve_zones(self.devices([9.5]), 8.0)


if __name__ == "__main__":
    unittest.main()
