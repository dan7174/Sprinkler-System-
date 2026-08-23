import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from agent.tracking import DesignLog
from validation.schema_validation import validation_errors


class TestDesignLog(unittest.TestCase):
    def test_assumption_requires_all_parts(self):
        log = DesignLog()
        with self.assertRaises(ValueError):
            log.assume("Soil is silt loam", "", "Jar test")
        with self.assertRaises(ValueError):
            log.assume("", "Wrong runtimes", "Jar test")

    def test_field_items_deduplicate(self):
        log = DesignLog()
        log.require_field_verification("Confirm meter size")
        log.require_field_verification("Confirm meter size")
        self.assertEqual(len(log.field_verification_items), 1)

    def test_unknown_review_trigger_rejected(self):
        log = DesignLog()
        with self.assertRaises(ValueError):
            log.trigger_review("vibes_check")

    def test_review_triggers_name_the_professional(self):
        log = DesignLog()
        log.trigger_review("backflow_device_selection_or_test")
        log.trigger_review("line_voltage_wiring")
        joined = " ".join(log.required_professional_review)
        self.assertIn("backflow", joined)
        self.assertIn("Licensed electrician", joined)

    def test_export_fits_design_project_schema(self):
        log = DesignLog()
        log.assume("Winter water use is representative of static pressure",
                   "Summer pressure may be lower than tested",
                   "Re-test pressure in July before construction")
        log.require_field_verification("Confirm elevation to highest head")
        log.trigger_review("backflow_device_selection_or_test")
        project = {
            "project_id": "T1",
            "project_mode": "residential_new_design",
            "status": "preliminary_not_for_construction",
            "site_intake": self._minimal_intake(),
            **log.export(),
        }
        self.assertEqual(validation_errors("design_project.schema.json", project), [])

    @staticmethod
    def _minimal_intake():
        return {
            "intake_id": "T1-I", "collected_on": "2026-08-23",
            "property": {"jurisdiction": "Test"},
            "water_supply": {"source_type": "municipal"},
        }


if __name__ == "__main__":
    unittest.main()
