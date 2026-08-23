import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from validation import product_data

VALID_RECORD = {
    "manufacturer": "Test Manufacturer",
    "product_family": "Fixture Family",
    "model": "FIXTURE-1",
    "status": "current",
    "application_type": "rotary_nozzle",
    "pressure_range_psi": {"min": 30, "max": 55},
    "flow_range_gpm": {"min": 0.1, "max": 1.2},
    "source": {
        "url": "https://example.com/fixture-spec",
        "document_title": "synthetic fixture spec (not a real product)",
        "retrieved_on": "2026-08-01",
    },
    "notes": "Synthetic test fixture, not real manufacturer data.",
}


class CatalogTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write_record(self, name: str, record) -> None:
        path = self.data_dir / "test_manufacturer" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record) if isinstance(record, dict) else record)


class TestLoadCatalog(CatalogTestCase):
    def test_empty_directory_is_valid_empty_catalog(self):
        records, issues = product_data.load_catalog(self.data_dir)
        self.assertEqual(records, [])
        self.assertEqual(issues, [])

    def test_missing_directory_is_empty_catalog(self):
        records, issues = product_data.load_catalog(self.data_dir / "does_not_exist")
        self.assertEqual((records, issues), ([], []))

    def test_valid_record_loads(self):
        self.write_record("fixture1.json", VALID_RECORD)
        records, issues = product_data.load_catalog(self.data_dir)
        self.assertEqual(issues, [])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["model"], "FIXTURE-1")

    def test_record_without_source_rejected(self):
        bad = {k: v for k, v in VALID_RECORD.items() if k != "source"}
        self.write_record("bad.json", bad)
        records, issues = product_data.load_catalog(self.data_dir)
        self.assertEqual(records, [])
        self.assertEqual(len(issues), 1)
        self.assertIn("source", issues[0].problem)

    def test_malformed_json_reported_not_crashing(self):
        self.write_record("broken.json", "{not json")
        self.write_record("good.json", VALID_RECORD)
        records, issues = product_data.load_catalog(self.data_dir)
        self.assertEqual(len(records), 1)
        self.assertEqual(len(issues), 1)
        self.assertIn("invalid JSON", issues[0].problem)


class TestFreshness(CatalogTestCase):
    def test_fresh_record_not_stale(self):
        self.write_record("fixture1.json", VALID_RECORD)
        records, _ = product_data.load_catalog(self.data_dir)
        stale = product_data.stale_records(records, datetime.date(2026, 8, 23))
        self.assertEqual(stale, [])

    def test_old_record_flagged_stale(self):
        old = json.loads(json.dumps(VALID_RECORD))
        old["source"]["retrieved_on"] = "2024-01-01"
        self.write_record("old.json", old)
        records, _ = product_data.load_catalog(self.data_dir)
        stale = product_data.stale_records(records, datetime.date(2026, 8, 23))
        self.assertEqual(len(stale), 1)

    def test_usable_for_design_excludes_stale_and_discontinued(self):
        fresh = VALID_RECORD
        old = json.loads(json.dumps(VALID_RECORD))
        old["model"] = "FIXTURE-OLD"
        old["source"]["retrieved_on"] = "2024-01-01"
        discontinued = json.loads(json.dumps(VALID_RECORD))
        discontinued["model"] = "FIXTURE-GONE"
        discontinued["status"] = "discontinued"
        self.write_record("fresh.json", fresh)
        self.write_record("old.json", old)
        self.write_record("gone.json", discontinued)
        records, _ = product_data.load_catalog(self.data_dir)
        usable = product_data.usable_for_design(records, datetime.date(2026, 8, 23))
        self.assertEqual([r["model"] for r in usable], ["FIXTURE-1"])


class TestRealDataDirectory(unittest.TestCase):
    def test_committed_catalog_has_no_invalid_records(self):
        # Whatever is committed under data/manufacturers must be schema-valid.
        records, issues = product_data.load_catalog()
        self.assertEqual(issues, [], f"invalid committed product records: {issues}")


if __name__ == "__main__":
    unittest.main()
