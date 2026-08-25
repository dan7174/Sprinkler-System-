import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from audit import lifecycle, replacement, troubleshooting
from validation.product_data import load_catalog

CATALOG, _ = load_catalog()


class TestTroubleshootingTrees(unittest.TestCase):
    def test_all_trees_are_internally_consistent(self):
        for symptom in troubleshooting.list_symptoms():
            with self.subTest(symptom=symptom):
                self.assertTrue(troubleshooting.validate_tree(symptom))

    def test_core_symptoms_covered(self):
        symptoms = troubleshooting.list_symptoms()
        for expected in ("low_pressure_all_zones", "zone_dead", "misting_fogging",
                         "dry_spots", "valve_weeps_when_off", "drip_zone_failure",
                         "runoff_or_overspray", "heads_not_rising"):
            self.assertIn(expected, symptoms)

    def test_every_step_has_test_expected_and_both_branches(self):
        # docs/06 s.17: test, expected result, interpretation, next action.
        for symptom in troubleshooting.list_symptoms():
            for step in troubleshooting.get_tree(symptom):
                self.assertTrue(step.test.strip())
                self.assertTrue(step.expected.strip())
                for interp, nxt in (step.if_expected, step.if_not):
                    self.assertTrue(interp.strip())
                    self.assertTrue(nxt.strip())

    def test_electrical_path_escalates_to_electrician(self):
        tree = troubleshooting.get_tree("zone_dead")
        nexts = {n for s in tree for n in (s.if_expected[1], s.if_not[1])}
        self.assertIn("ESCALATE_ELECTRICIAN", nexts)

    def test_backflow_work_escalates_to_certified_tester(self):
        tree = troubleshooting.get_tree("low_pressure_all_zones")
        nexts = {n for s in tree for n in (s.if_expected[1], s.if_not[1])}
        self.assertIn("ESCALATE_BACKFLOW_TESTER", nexts)

    def test_markdown_renders_with_step_references(self):
        md = troubleshooting.to_markdown("zone_dead")
        self.assertIn("Expected:", md)
        self.assertIn("go to step", md)
        self.assertIn("licensed electrician", md)

    def test_unknown_symptom_rejected(self):
        with self.assertRaises(ValueError):
            troubleshooting.get_tree("gremlins")


class TestLifecycle(unittest.TestCase):
    def test_exact_match(self):
        ident = lifecycle.identify("R-VAN18", CATALOG)
        self.assertTrue(ident.matched)
        self.assertEqual(ident.record["model"], "R-VAN18")

    def test_sloppy_spelling_matches(self):
        ident = lifecycle.identify("rvan 18", CATALOG)
        self.assertTrue(ident.matched)
        self.assertEqual(ident.record["model"], "R-VAN18")

    def test_ambiguous_prefix_lists_candidates(self):
        ident = lifecycle.identify("1804", CATALOG)
        # exact match "1804" exists, so this matches directly
        self.assertTrue(ident.matched)
        ident2 = lifecycle.identify("R-VAN", CATALOG)
        self.assertFalse(ident2.matched)
        self.assertGreater(len(ident2.candidates), 1)
        self.assertIn("identify the exact model", ident2.guidance)

    def test_unknown_model_gives_upgrade_guide_guidance(self):
        report = lifecycle.lifecycle_status("Maxi-Paw 2045A", CATALOG)
        self.assertEqual(report["status"], "unknown_requires_verification")
        self.assertIn(lifecycle.UPGRADE_GUIDE_URL, report["action"])

    def test_current_model_status(self):
        report = lifecycle.lifecycle_status("5004-PC", CATALOG)
        self.assertEqual(report["status"], "current")
        self.assertTrue(report["source_url"].startswith("http"))

    def test_empty_model_rejected(self):
        with self.assertRaises(ValueError):
            lifecycle.identify("   ", CATALOG)


class TestReplacement(unittest.TestCase):
    def test_direct_replacement_same_family(self):
        result = replacement.check_replacement(
            {"application_type": "rotary_nozzle", "zone_pressure_psi": 45.0,
             "radius_needed_ft": 15.0, "arc_needed_degrees": 180.0},
            "R-VAN18", CATALOG)
        self.assertEqual(result.classification, "direct_replacement")

    def test_radius_mismatch_forces_redesign(self):
        result = replacement.check_replacement(
            {"application_type": "rotary_nozzle", "zone_pressure_psi": 45.0,
             "radius_needed_ft": 22.0},
            "R-VAN18", CATALOG)
        self.assertEqual(result.classification, "redesign_required")
        self.assertTrue(any("radius" in r for r in result.reasons))

    def test_method_change_is_redesign_with_consequences(self):
        result = replacement.check_replacement(
            {"application_type": "spray_head", "zone_pressure_psi": 45.0},
            "R-VAN18", CATALOG)
        self.assertEqual(result.classification, "redesign_required")
        self.assertTrue(any("whole zone" in c or "entire zone" in c
                            for c in result.consequences))

    def test_pressure_outside_range_is_redesign(self):
        result = replacement.check_replacement(
            {"application_type": "rotary_nozzle", "zone_pressure_psi": 25.0,
             "radius_needed_ft": 15.0},
            "R-VAN18", CATALOG)
        self.assertEqual(result.classification, "redesign_required")

    def test_missing_pressure_range_needs_field_verification(self):
        # 1800 spray bodies have no radius data; swapping body models works
        # but flags what must be confirmed.
        result = replacement.check_replacement(
            {"application_type": "spray_head", "zone_pressure_psi": 45.0,
             "radius_needed_ft": 12.0},
            "1804-SAM-PRS", CATALOG)
        self.assertEqual(result.classification, "compatible_with_adjustments")
        self.assertTrue(result.field_verification)

    def test_unknown_replacement_model_rejected(self):
        with self.assertRaises(ValueError):
            replacement.check_replacement(
                {"application_type": "rotor", "zone_pressure_psi": 45.0},
                "UNICORN-1", CATALOG)

    def test_missing_zone_pressure_rejected(self):
        with self.assertRaises(ValueError):
            replacement.check_replacement(
                {"application_type": "rotor"}, "5004-PC", CATALOG)


if __name__ == "__main__":
    unittest.main()
