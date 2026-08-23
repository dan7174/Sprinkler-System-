import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from calculators import electrical

MIN_V_SOURCE = "synthetic manufacturer minimum for tests (fixture value)"


class TestVoltageDrop(unittest.TestCase):
    def test_known_value_14awg(self):
        # 0.3 A holding, 500 ft one-way, 14 AWG (3.07 ohm/1000ft):
        # Vd = 2 * 0.3 * 500 * 3.07 / 1000 = 0.921 V
        drop = electrical.voltage_drop_volts(0.3, 500.0, 3.07)
        self.assertAlmostEqual(drop, 0.921, places=6)

    def test_hand_calculation_cross_check(self):
        # Independent check: 1 A over 1000 ft of 1 ohm/1000ft wire is
        # 2 ohms round trip -> 2 V.
        self.assertEqual(electrical.voltage_drop_volts(1.0, 1000.0, 1.0), 2.0)

    def test_thinner_wire_drops_more(self):
        thin = electrical.voltage_drop_volts(0.3, 500.0, electrical.wire_resistance_ohms_per_1000ft(18))
        thick = electrical.voltage_drop_volts(0.3, 500.0, electrical.wire_resistance_ohms_per_1000ft(12))
        self.assertGreater(thin, thick)

    def test_unknown_awg_rejected(self):
        with self.assertRaises(ValueError):
            electrical.wire_resistance_ohms_per_1000ft(22)


class TestSolenoidCheck(unittest.TestCase):
    def test_passing_check(self):
        result = electrical.check_solenoid_voltage(
            supply_volts=24.0, current_amps=0.3, one_way_length_ft=500.0,
            ohms_per_1000ft=3.07, min_operating_volts=21.6,
            min_operating_source=MIN_V_SOURCE,
        )
        self.assertTrue(result.passes)
        self.assertAlmostEqual(result.voltage_at_solenoid, 23.079, places=3)

    def test_failing_check_long_thin_run(self):
        # 18 AWG at 2000 ft with 0.4 A inrush: Vd = 2*0.4*2000*7.77/1000 = 12.43 V
        result = electrical.check_solenoid_voltage(
            supply_volts=24.0, current_amps=0.4, one_way_length_ft=2000.0,
            ohms_per_1000ft=7.77, min_operating_volts=21.6,
            min_operating_source=MIN_V_SOURCE,
        )
        self.assertFalse(result.passes)
        self.assertAlmostEqual(result.voltage_drop, 12.432, places=3)

    def test_source_citation_required(self):
        with self.assertRaises(ValueError):
            electrical.check_solenoid_voltage(24.0, 0.3, 500.0, 3.07, 21.6, "  ")


class TestWireSizing(unittest.TestCase):
    def test_short_run_takes_smallest_wire(self):
        awg = electrical.smallest_adequate_awg(24.0, 0.3, 50.0, 21.6, MIN_V_SOURCE)
        self.assertEqual(awg, 18)

    def test_long_run_needs_thicker_wire(self):
        awg = electrical.smallest_adequate_awg(24.0, 0.4, 2000.0, 21.6, MIN_V_SOURCE)
        self.assertLess(awg, 18)
        # verify the chosen size actually passes and the next smaller fails
        chosen = electrical.check_solenoid_voltage(
            24.0, 0.4, 2000.0,
            electrical.wire_resistance_ohms_per_1000ft(awg), 21.6, MIN_V_SOURCE)
        self.assertTrue(chosen.passes)

    def test_impossible_run_raises(self):
        with self.assertRaises(ValueError):
            electrical.smallest_adequate_awg(24.0, 2.0, 20000.0, 21.6, MIN_V_SOURCE)


if __name__ == "__main__":
    unittest.main()
