import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from agent.intake_review import review_intake


def load_fixture():
    return json.loads((REPO_ROOT / "tests/fixtures/site_intake_minimal.json").read_text())


def complete_intake():
    intake = load_fixture()
    intake["missing_critical_inputs"] = []
    intake["property"]["utility_locate_status"] = "marked"
    intake["property"]["water_provider"] = "City of Silverton (fixture)"
    intake["water_supply"]["meter_size"] = {"value": 0.75, "unit": "in", "provenance": "verified_field_measurement"}
    intake["water_supply"]["safe_design_flow"] = {"value": 8, "unit": "gpm", "provenance": "calculated"}
    intake["water_supply"]["elevation_source_to_highest_outlet"] = {"value": 4, "unit": "ft", "provenance": "verified_field_measurement"}
    intake["site_geometry"] = {
        "plan_source": "verified_field_dimensions",
        "irrigated_area": {"value": 3200, "unit": "sqft", "provenance": "verified_field_measurement"},
    }
    intake["soil_and_plants"] = {"soil_texture": "silt loam"}
    return intake


class TestIncompleteIntake(unittest.TestCase):
    def test_fixture_is_preliminary_not_for_construction(self):
        # The minimal fixture declares missing critical inputs.
        review = review_intake(load_fixture())
        self.assertFalse(review.ready_for_final_design)
        self.assertEqual(review.required_status, "preliminary_not_for_construction")
        self.assertTrue(review.missing_critical)

    def test_missing_dynamic_test_is_critical(self):
        intake = complete_intake()
        intake["water_supply"]["dynamic_tests"] = []
        review = review_intake(intake)
        self.assertFalse(review.ready_for_final_design)
        self.assertTrue(any("Dynamic pressure" in m.item for m in review.missing_critical))

    def test_static_only_never_ready(self):
        intake = complete_intake()
        del intake["water_supply"]["dynamic_tests"]
        review = review_intake(intake)
        self.assertFalse(review.ready_for_final_design)

    def test_unverified_aerial_plan_is_critical(self):
        intake = complete_intake()
        intake["site_geometry"]["plan_source"] = "aerial_estimate_unverified"
        review = review_intake(intake)
        self.assertTrue(any("Verified site dimensions" in m.item for m in review.missing_critical))

    def test_missing_soil_texture_is_critical(self):
        intake = complete_intake()
        del intake["soil_and_plants"]["soil_texture"]
        review = review_intake(intake)
        self.assertTrue(any("Soil texture" in m.item for m in review.missing_critical))

    def test_schema_invalid_intake_reports_errors_not_review(self):
        review = review_intake({"intake_id": "X"})
        self.assertTrue(review.schema_errors)
        self.assertFalse(review.ready_for_final_design)


class TestCompleteIntake(unittest.TestCase):
    def test_complete_intake_is_ready(self):
        review = review_intake(complete_intake())
        self.assertEqual(review.schema_errors, ())
        self.assertEqual(review.missing_critical, ())
        self.assertTrue(review.ready_for_final_design)
        self.assertEqual(review.required_status, "design_in_progress")

    def test_utility_locate_warning(self):
        intake = complete_intake()
        intake["property"]["utility_locate_status"] = "not_requested"
        review = review_intake(intake)
        self.assertTrue(review.ready_for_final_design)  # warning, not critical
        self.assertTrue(any("811" in w for w in review.warnings))

    def test_every_missing_item_explains_why(self):
        review = review_intake(load_fixture())
        for m in review.missing_critical:
            self.assertTrue(m.why_it_matters.strip())


if __name__ == "__main__":
    unittest.main()
