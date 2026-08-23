import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from calculators import hydraulics


class TestVelocity(unittest.TestCase):
    def test_known_chart_value_1in_sch40_at_10gpm(self):
        # 1 in SCH40 PVC actual ID = 1.049 in. Published friction charts
        # list about 3.71 ft/s at 10 gpm — cross-check against that.
        velocity = hydraulics.water_velocity_fps(10.0, 1.049)
        self.assertAlmostEqual(velocity, 3.71, delta=0.02)

    def test_zero_flow_gives_zero_velocity(self):
        self.assertEqual(hydraulics.water_velocity_fps(0.0, 1.049), 0.0)

    def test_velocity_scales_linearly_with_flow(self):
        v1 = hydraulics.water_velocity_fps(5.0, 1.049)
        v2 = hydraulics.water_velocity_fps(10.0, 1.049)
        self.assertAlmostEqual(v2, 2 * v1, places=9)

    def test_zero_diameter_rejected(self):
        with self.assertRaises(ValueError):
            hydraulics.water_velocity_fps(10.0, 0.0)

    def test_negative_flow_rejected(self):
        with self.assertRaises(ValueError):
            hydraulics.water_velocity_fps(-1.0, 1.049)


class TestHazenWilliams(unittest.TestCase):
    def test_known_chart_value_1in_sch40_pvc_at_10gpm(self):
        # Published PVC SCH40 friction charts (C=150) list roughly
        # 2.3-2.4 psi per 100 ft for 1 in pipe at 10 gpm.
        loss = hydraulics.hazen_williams_loss_psi(10.0, 1.049, 100.0, 150)
        self.assertAlmostEqual(loss, 2.38, delta=0.10)

    def test_loss_scales_linearly_with_length(self):
        loss_100 = hydraulics.hazen_williams_loss_psi(10.0, 1.049, 100.0, 150)
        loss_250 = hydraulics.hazen_williams_loss_psi(10.0, 1.049, 250.0, 150)
        self.assertAlmostEqual(loss_250, 2.5 * loss_100, places=9)

    def test_larger_pipe_loses_less(self):
        # 1.25 in SCH40 actual ID = 1.380 in
        small = hydraulics.hazen_williams_loss_psi(10.0, 1.049, 100.0, 150)
        large = hydraulics.hazen_williams_loss_psi(10.0, 1.380, 100.0, 150)
        self.assertLess(large, small)

    def test_rougher_pipe_loses_more(self):
        smooth = hydraulics.hazen_williams_loss_psi(10.0, 1.049, 100.0, 150)
        rough = hydraulics.hazen_williams_loss_psi(10.0, 1.049, 100.0, 100)
        self.assertGreater(rough, smooth)

    def test_zero_flow_is_zero_loss(self):
        self.assertEqual(hydraulics.hazen_williams_loss_psi(0.0, 1.049, 100.0, 150), 0.0)

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            hydraulics.hazen_williams_loss_psi(10.0, -1.0, 100.0, 150)
        with self.assertRaises(ValueError):
            hydraulics.hazen_williams_loss_psi(10.0, 1.049, -5.0, 150)
        with self.assertRaises(ValueError):
            hydraulics.hazen_williams_loss_psi(10.0, 1.049, 100.0, 0)


class TestElevation(unittest.TestCase):
    def test_rise_reduces_pressure(self):
        # 10 ft rise costs about 4.33 psi
        self.assertAlmostEqual(hydraulics.elevation_pressure_change_psi(10.0), -4.33, places=6)

    def test_drop_gains_pressure(self):
        self.assertAlmostEqual(hydraulics.elevation_pressure_change_psi(-10.0), 4.33, places=6)

    def test_flat_is_zero(self):
        self.assertEqual(hydraulics.elevation_pressure_change_psi(0.0), 0.0)


class TestVelocityCheck(unittest.TestCase):
    def test_pass_below_limit(self):
        result = hydraulics.check_velocity(
            10.0, 1.049, limit_fps=5.0,
            limit_source="Rain Bird Landscape Irrigation Design Manual (PVC mainline practice)",
        )
        self.assertTrue(result.passes)
        self.assertAlmostEqual(result.velocity_fps, 3.71, delta=0.02)

    def test_fail_above_limit(self):
        # Excessive-velocity failure case (docs/08 fixture 7):
        # 20 gpm through 1 in SCH40 is about 7.4 ft/s.
        result = hydraulics.check_velocity(
            20.0, 1.049, limit_fps=5.0,
            limit_source="Rain Bird Landscape Irrigation Design Manual (PVC mainline practice)",
        )
        self.assertFalse(result.passes)
        self.assertGreater(result.velocity_fps, 7.0)

    def test_limit_source_required(self):
        with self.assertRaises(ValueError):
            hydraulics.check_velocity(10.0, 1.049, limit_fps=5.0, limit_source="  ")


class TestPressurePath(unittest.TestCase):
    LOSSES = [
        ("water meter", 3.0),
        ("backflow assembly", 6.0),
        ("mainline friction", 2.4),
        ("control valve", 2.5),
        ("lateral friction", 1.8),
    ]

    def test_passing_path_shows_all_intermediate_values(self):
        result = hydraulics.pressure_path(
            source_pressure_psi=55.0,
            losses=self.LOSSES,
            elevation_rise_ft=5.0,
            required_device_pressure_psi=30.0,
        )
        # 55 - 15.7 total losses - 2.165 elevation = 37.135 psi at the device
        self.assertAlmostEqual(result.device_pressure_psi, 37.135, places=3)
        self.assertAlmostEqual(result.margin_psi, 7.135, places=3)
        self.assertTrue(result.passes)
        # every step is visible, in order, plus the elevation step
        self.assertEqual(len(result.steps), len(self.LOSSES) + 1)
        self.assertEqual(result.steps[0].label, "water meter")
        self.assertAlmostEqual(result.steps[0].running_pressure_psi, 52.0, places=6)
        explanation = result.explain()
        self.assertIn("backflow assembly", explanation)
        self.assertIn("PASS", explanation)

    def test_low_pressure_failure_case(self):
        # Low-pressure failure case (docs/08 fixture 6)
        result = hydraulics.pressure_path(
            source_pressure_psi=38.0,
            losses=self.LOSSES,
            elevation_rise_ft=8.0,
            required_device_pressure_psi=30.0,
        )
        self.assertLess(result.margin_psi, 0)
        self.assertFalse(result.passes)
        self.assertIn("FAIL", result.explain())

    def test_pressure_exhausted_mid_path_warns(self):
        result = hydraulics.pressure_path(
            source_pressure_psi=10.0,
            losses=[("water meter", 4.0), ("backflow assembly", 8.0)],
            elevation_rise_ft=0.0,
            required_device_pressure_psi=25.0,
        )
        self.assertFalse(result.passes)
        self.assertTrue(any("cannot operate" in w for w in result.warnings))

    def test_negative_loss_rejected(self):
        with self.assertRaises(ValueError):
            hydraulics.pressure_path(55.0, [("meter", -3.0)], 0.0, 30.0)

    def test_unlabeled_step_rejected(self):
        with self.assertRaises(ValueError):
            hydraulics.pressure_path(55.0, [("", 3.0)], 0.0, 30.0)


if __name__ == "__main__":
    unittest.main()
