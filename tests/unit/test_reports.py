import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from reports import bill_of_materials, commissioning, visual_plan, zone_schedule
from validation.product_data import load_catalog

CATALOG, _ = load_catalog()


def make_row(**over):
    base = dict(
        zone_number=1, name="Front lawn", hydrozone="turf / full sun / silt loam / flat",
        application="rotary_nozzle", area_sqft=800.0, device_model="R-VAN18",
        nozzle_and_arc="R-VAN18, 90-360 deg", quantity=8, device_flow_gpm="0.4-1.6",
        total_flow_gpm=6.0, required_pressure_psi=45.0,
        design_margin_psi=6.5, precipitation_rate_in_hr=0.6,
        runtime_minutes=40.0, cycles=2)
    base.update(over)
    return zone_schedule.ZoneRow(**base)


class TestZoneSchedule(unittest.TestCase):
    def test_markdown_contains_required_columns(self):
        md = zone_schedule.to_markdown([make_row()])
        for token in ("Zone", "Flow (gpm)", "Pressure (psi)", "Margin (psi)",
                      "PR (in/hr)", "R-VAN18", "40 min in 2 cycles"):
            self.assertIn(token, md)

    def test_missing_optional_values_say_field_verify(self):
        md = zone_schedule.to_markdown([make_row(design_margin_psi=None,
                                                 precipitation_rate_in_hr=None,
                                                 runtime_minutes=None)])
        self.assertIn("field verify", md)

    def test_invalid_row_rejected(self):
        with self.assertRaises(ValueError):
            make_row(total_flow_gpm=0)
        with self.assertRaises(ValueError):
            make_row(quantity=0)

    def test_empty_schedule_rejected(self):
        with self.assertRaises(ValueError):
            zone_schedule.to_markdown([])


class TestBillOfMaterials(unittest.TestCase):
    def test_lines_join_catalog_source(self):
        lines = bill_of_materials.build_bom(
            [{"model": "R-VAN18", "quantity": 8},
             {"model": "100-DV", "quantity": 2, "accessories": "waterproof wire connectors"}],
            CATALOG)
        self.assertEqual(lines[0].manufacturer, "Rain Bird")
        self.assertTrue(lines[0].source_url.startswith("http"))
        self.assertEqual(lines[0].status, "current")
        self.assertIn("wire connectors", lines[1].accessories)

    def test_unknown_model_fails_loudly(self):
        with self.assertRaises(ValueError):
            bill_of_materials.build_bom([{"model": "MYSTERY-9000", "quantity": 1}], CATALOG)

    def test_markdown_omits_prices_without_verification(self):
        lines = bill_of_materials.build_bom([{"model": "R-VAN18", "quantity": 8}], CATALOG)
        md = bill_of_materials.to_markdown(lines)
        self.assertIn("Prices are omitted", md)
        self.assertNotIn("| Price |", md)

    def test_markdown_shows_price_only_when_supplied(self):
        lines = bill_of_materials.build_bom(
            [{"model": "R-VAN18", "quantity": 8, "verified_unit_price": "$7.98 (verified 2026-08-23)"}],
            CATALOG)
        md = bill_of_materials.to_markdown(lines)
        self.assertIn("Price |", md)
        self.assertIn("$7.98", md)


class TestCommissioning(unittest.TestCase):
    def test_sprinkler_methods_add_head_steps(self):
        steps = commissioning.commissioning_checklist({"rotary_nozzle"})
        self.assertTrue(any("arcs" in s for s in steps))
        self.assertTrue(any("catch-can" in s.lower() for s in steps))

    def test_drip_methods_add_flush_steps(self):
        steps = commissioning.commissioning_checklist({"drip"})
        self.assertTrue(any("flush points" in s.lower() for s in steps))

    def test_winterization_note_required(self):
        with self.assertRaises(ValueError):
            commissioning.maintenance_plan({"spray"}, "")

    def test_plan_includes_winterization(self):
        rows = commissioning.maintenance_plan(
            {"spray"}, "Willamette Valley: drain and insulate backflow before first freeze "
                       "(verify current local practice)")
        self.assertEqual(rows[-1][0], "Winterization")


class TestVisualPlan(unittest.TestCase):
    AREAS = [
        visual_plan.PlanArea("lot", 0, 0, 60, 40),
        visual_plan.PlanArea("house", 20, 5, 25, 15, "House"),
        visual_plan.PlanArea("lawn", 0, 22, 60, 18, "Front lawn"),
    ]

    def render(self, status="Preliminary — Not for construction", **kw):
        return visual_plan.render_svg(
            "Test Plan", "Silverton, OR", "2026-08-23", status, self.AREAS, **kw)

    def test_svg_is_valid_xml_with_title_block(self):
        svg = self.render(
            heads=[visual_plan.PlanHead(5, 25, 15, 0, 90, 1, "R-VAN18")],
            points=[visual_plan.PlanPoint(2, 2, "POC", "Point of connection")])
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))
        for token in ("Test Plan", "Silverton, OR", "2026-08-23", "Scale",
                      "NOT FOR CONSTRUCTION", "Zone 1", "POC", ">N<"):
            self.assertIn(token, svg)

    def test_construction_status_removes_watermark(self):
        svg = self.render(status="For construction")
        self.assertNotIn("NOT FOR CONSTRUCTION</text>", svg)

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            self.render(status="Looks fine to me")

    def test_missing_title_rejected(self):
        with self.assertRaises(ValueError):
            visual_plan.render_svg("", "Silverton", "2026-08-23",
                                   "For review", self.AREAS)

    def test_unknown_area_kind_rejected(self):
        with self.assertRaises(ValueError):
            visual_plan.render_svg("T", "L", "D", "For review",
                                   [visual_plan.PlanArea("swamp", 0, 0, 10, 10)])

    def test_labels_are_escaped(self):
        svg = visual_plan.render_svg(
            'Plan <with> "quotes" & ampersands', "Loc", "2026-08-23",
            "For review", self.AREAS)
        ET.fromstring(svg)  # would raise if unescaped
        self.assertIn("&amp;", svg)


if __name__ == "__main__":
    unittest.main()
