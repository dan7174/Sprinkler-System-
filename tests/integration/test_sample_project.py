"""Integration test: docs/08 fixture 1 — a small municipal-water
residential lawn — run through calculators, design engine and
deliverable generators end to end.

Everything numeric flows from the committed catalog and the calculators;
this test would fail if the catalog, engine and reports stopped agreeing
with each other.
"""

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from agent import compatibility, product_selection
from calculators import hydraulics
from reports import bill_of_materials, design_report, visual_plan, zone_schedule
from validation.product_data import load_catalog

CATALOG, _ = load_catalog()
DESIGN_PRESSURE = 45.0
SAFE_ZONE_FLOW = 8.0


class TestSmallLawnProject(unittest.TestCase):
    def build_zone_devices(self):
        # Published R-VAN18 performance at 45 psi: 270 deg -> 1.51 gpm.
        row270 = product_selection.published_performance(
            "r-van18.csv", DESIGN_PRESSURE, {"arc_degrees": 270.0})
        row90 = product_selection.published_performance(
            "r-van18.csv", DESIGN_PRESSURE, {"arc_degrees": 90.0})
        rvan18 = next(r for r in CATALOG if r["model"] == "R-VAN18")
        corners = [{"model": "R-VAN18", "application_type": "rotary_nozzle",
                    "flow_gpm": row90["flow_gpm"], "arc_degrees": 90.0,
                    "pressure_range_psi": rvan18["pressure_range_psi"]} for _ in range(4)]
        edge = {"model": "R-VAN18", "application_type": "rotary_nozzle",
                "flow_gpm": row270["flow_gpm"], "arc_degrees": 270.0,
                "pressure_range_psi": rvan18["pressure_range_psi"]}
        return corners + [edge]

    def test_full_pipeline_produces_consistent_deliverables(self):
        # 1. Product selection finds R-VAN18 for a 15 ft strip at 45 psi.
        sel = product_selection.select_products(
            CATALOG, "rotary_nozzle", DESIGN_PRESSURE, radius_needed_ft=15.0)
        self.assertTrue(any(c.model == "R-VAN18" for c in sel.candidates))

        # 2. Zone compatibility passes with published matched-precip flows.
        devices = self.build_zone_devices()
        compat = compatibility.check_zone(devices, DESIGN_PRESSURE, SAFE_ZONE_FLOW)
        self.assertTrue(compat.passes, compat.failures)
        total_flow = round(sum(d["flow_gpm"] for d in devices), 2)
        self.assertLessEqual(total_flow, SAFE_ZONE_FLOW)

        # 3. Critical pressure path from a synthetic-but-labeled dynamic test.
        # (62 psi source - 14.4 psi losses - 1.3 psi elevation = 46.3 psi, +1.3 margin)
        path = hydraulics.pressure_path(
            source_pressure_psi=62.0,
            losses=[("water meter (fixture value)", 2.2),
                    ("backflow assembly (fixture value)", 5.0),
                    ("mainline friction (calculated)", 1.9),
                    ("100-DV valve (published at 5 gpm)", 3.8),
                    ("lateral friction (calculated)", 1.5)],
            elevation_rise_ft=3.0,
            required_device_pressure_psi=DESIGN_PRESSURE)
        self.assertTrue(path.passes, path.explain())

        # 4. Deliverables assemble without inventing anything.
        rows = [zone_schedule.ZoneRow(
            zone_number=1, name="Front lawn", hydrozone="turf / full sun / silt loam / flat",
            application="rotary_nozzle", area_sqft=600.0, device_model="R-VAN18",
            nozzle_and_arc="R-VAN18, 90/270 deg", quantity=len(devices),
            device_flow_gpm="0.50-1.51 (published)", total_flow_gpm=total_flow,
            required_pressure_psi=DESIGN_PRESSURE,
            critical_path_loss_psi=round(62.0 - path.device_pressure_psi, 2),
            residual_pressure_psi=round(path.device_pressure_psi, 2),
            design_margin_psi=round(path.margin_psi, 2))]
        bom = bill_of_materials.build_bom(
            [{"model": "R-VAN18", "quantity": len(devices)},
             {"model": "1804-SAM-PRS", "quantity": len(devices)},
             {"model": "100-DV", "quantity": 1}], CATALOG)
        report = design_report.render_markdown(design_report.ReportInputs(
            project_name="Sample Small Lawn (fixture)",
            location="Fixture City, OR", date="2026-08-23",
            status="Preliminary — Not for construction",
            understanding="Small municipal-water front lawn, single hydrozone.",
            missing_information=["Field-verified lawn dimensions"],
            assumptions=[{"description": "Fixture loss values represent the meter and backflow",
                          "impact_if_wrong": "Device pressure margin changes",
                          "how_to_verify": "Replace with published losses for the actual models"}],
            concept="One rotary-nozzle zone on pressure-regulated spray bodies.",
            pressure_paths=[("Zone 1", path)],
            zone_rows=rows, bom_lines=bom,
            installation_sequence=["Locate utilities (811)", "Trench and install mainline",
                                   "Set valve box and wire valve", "Install laterals and bodies",
                                   "Flush, install nozzles, commission"],
            methods={"rotary_nozzle"},
            winterization_note="Fixture climate: drain before first freeze (verify locally).",
            risks_and_field_items=["Backflow selection/test requires certified tester"],
            sources=[{"title": "R-VAN Rotary Nozzles Technical Specifications",
                      "url": "https://www.rainbird.com/media/5917",
                      "revision_or_verified_date": "D41159B (2024), retrieved 2026-08-23"}]))

        for token in ("critical pressure path", "PASS", "R-VAN18",
                      "Prices are omitted", "not a stamped engineering plan",
                      "## 12. Sources"):
            self.assertIn(token, report)
        # The zone schedule's flow equals the sum of published device flows.
        self.assertIn(f"{total_flow:g}", report)

        # 5. The plan sheet renders as valid SVG with the watermark.
        svg = visual_plan.render_svg(
            "Sample Small Lawn — Irrigation Plan", "Fixture City, OR", "2026-08-23",
            "Preliminary — Not for construction",
            areas=[visual_plan.PlanArea("lot", 0, 0, 40, 30),
                   visual_plan.PlanArea("lawn", 0, 15, 40, 15, "Front lawn")],
            heads=[visual_plan.PlanHead(0, 15, 15, 270, 90, 1),
                   visual_plan.PlanHead(40, 15, 15, 180, 90, 1),
                   visual_plan.PlanHead(0, 30, 15, 0, 90, 1),
                   visual_plan.PlanHead(40, 30, 15, 90, 90, 1),
                   visual_plan.PlanHead(20, 22.5, 15, 0, 270, 1)],
            points=[visual_plan.PlanPoint(1, 1, "POC")])
        ET.fromstring(svg)
        self.assertIn("NOT FOR CONSTRUCTION", svg)

    def test_low_pressure_variant_fails_and_report_shows_it(self):
        # docs/08 fixture 6: low-pressure failure must surface as FAIL, not be hidden.
        path = hydraulics.pressure_path(
            source_pressure_psi=42.0,
            losses=[("water meter (fixture value)", 2.2),
                    ("backflow assembly (fixture value)", 5.0),
                    ("mainline friction (calculated)", 1.9),
                    ("100-DV valve (published at 5 gpm)", 3.8),
                    ("lateral friction (calculated)", 1.5)],
            elevation_rise_ft=3.0,
            required_device_pressure_psi=DESIGN_PRESSURE)
        self.assertFalse(path.passes)
        self.assertIn("FAIL", path.explain())


if __name__ == "__main__":
    unittest.main()
