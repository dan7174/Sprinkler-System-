import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from validation import schema_validation

SCHEMA_FILES = [
    "site_intake.schema.json",
    "water_test.schema.json",
    "product.schema.json",
    "zone.schema.json",
    "design_project.schema.json",
]


class TestSchemasAreValid(unittest.TestCase):
    def test_all_expected_schema_files_exist(self):
        for name in SCHEMA_FILES:
            self.assertTrue((REPO_ROOT / "schemas" / name).is_file(), name)

    def test_every_schema_is_valid_draft_2020_12(self):
        for name in SCHEMA_FILES:
            with self.subTest(schema=name):
                schema_validation.validator_for(name)


class TestSiteIntakeValidation(unittest.TestCase):
    def setUp(self):
        fixture = REPO_ROOT / "tests" / "fixtures" / "site_intake_minimal.json"
        self.intake = json.loads(fixture.read_text())

    def test_fixture_is_valid(self):
        errors = schema_validation.validation_errors("site_intake.schema.json", self.intake)
        self.assertEqual(errors, [])

    def test_measurement_without_provenance_rejected(self):
        del self.intake["water_supply"]["static_pressure"]["provenance"]
        errors = schema_validation.validation_errors("site_intake.schema.json", self.intake)
        self.assertTrue(any("provenance" in e for e in errors))

    def test_negative_pressure_rejected(self):
        self.intake["water_supply"]["dynamic_tests"][0]["pressure_psi"] = -10
        errors = schema_validation.validation_errors("site_intake.schema.json", self.intake)
        self.assertNotEqual(errors, [])

    def test_dynamic_test_without_flow_rejected(self):
        del self.intake["water_supply"]["dynamic_tests"][0]["flow_gpm"]
        errors = schema_validation.validation_errors("site_intake.schema.json", self.intake)
        self.assertTrue(any("flow_gpm" in e for e in errors))

    def test_missing_water_supply_rejected(self):
        del self.intake["water_supply"]
        errors = schema_validation.validation_errors("site_intake.schema.json", self.intake)
        self.assertTrue(any("water_supply" in e for e in errors))


class TestDesignProjectValidation(unittest.TestCase):
    def setUp(self):
        fixture = REPO_ROOT / "tests" / "fixtures" / "site_intake_minimal.json"
        self.project = {
            "project_id": "FIXTURE-PROJECT-001",
            "project_mode": "residential_new_design",
            "status": "preliminary_not_for_construction",
            "site_intake": json.loads(fixture.read_text()),
        }

    def test_minimal_project_is_valid(self):
        errors = schema_validation.validation_errors("design_project.schema.json", self.project)
        self.assertEqual(errors, [])

    def test_unknown_project_mode_rejected(self):
        self.project["project_mode"] = "golf_course_guessing"
        errors = schema_validation.validation_errors("design_project.schema.json", self.project)
        self.assertTrue(any("project_mode" in e for e in errors))

    def test_nested_intake_is_validated_through_reference(self):
        # Corrupt the nested intake: the cross-file $ref must catch it.
        del self.project["site_intake"]["water_supply"]["source_type"]
        errors = schema_validation.validation_errors("design_project.schema.json", self.project)
        self.assertNotEqual(errors, [])

    def test_zone_with_invalid_arc_rejected(self):
        self.project["zones"] = [{
            "zone_id": "Z1",
            "application_method": "spray",
            "hydrozone": {"plant_type": "turf"},
            "heads": [{"flow_gpm": 1.0, "arc_degrees": 500}],
        }]
        errors = schema_validation.validation_errors("design_project.schema.json", self.project)
        self.assertTrue(any("arc_degrees" in e or "500" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
