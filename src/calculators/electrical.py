"""Low-voltage electrical calculations: valve-wire voltage drop and
conductor sizing.

Method sources (registered in knowledge/source_manifest.yaml):

- Two-wire (out-and-back) DC-resistance voltage drop:

      Vd = 2 * I * L * R / 1000

  where I is current in amps, L the ONE-WAY wire run in feet and R the
  conductor resistance in ohms per 1000 ft. The factor 2 accounts for
  the common wire returning the current.
- Conductor resistance values are the published DC resistance values for
  uncoated solid copper at 75 C from NEC (NFPA 70) Chapter 9, Table 8.
  Verify against the actual wire specification before final design;
  actual AC impedance for long runs and multi-valve commons is higher.

Solenoid inrush/holding current and minimum operating voltage are
manufacturer data — this module requires them as cited inputs and never
assumes them. Line-voltage (120/240 V) work is outside scope and
requires a licensed electrician (Agent Charter safety rule).
"""

from dataclasses import dataclass

from .units import _require_non_negative, _require_positive

# NEC (NFPA 70) Chapter 9, Table 8: DC resistance, ohms per 1000 ft,
# uncoated solid copper at 75 C. Verify against actual wire spec.
COPPER_RESISTANCE_OHMS_PER_1000FT = {
    18: 7.77,
    16: 4.89,
    14: 3.07,
    12: 1.93,
    10: 1.21,
    8: 0.764,
    6: 0.491,
    4: 0.308,
}
RESISTANCE_TABLE_SOURCE = "NEC (NFPA 70) Chapter 9 Table 8, uncoated solid copper, 75C"


def wire_resistance_ohms_per_1000ft(awg: int) -> float:
    """Published resistance for a supported AWG size (see table source)."""
    if awg not in COPPER_RESISTANCE_OHMS_PER_1000FT:
        raise ValueError(
            f"AWG {awg!r} is not in the built-in table "
            f"{sorted(COPPER_RESISTANCE_OHMS_PER_1000FT)}; supply the resistance "
            "directly from the wire manufacturer's data"
        )
    return COPPER_RESISTANCE_OHMS_PER_1000FT[awg]


def voltage_drop_volts(
    current_amps: float,
    one_way_length_ft: float,
    ohms_per_1000ft: float,
) -> float:
    """Round-trip voltage drop for a two-wire run: Vd = 2*I*L*R/1000."""
    _require_positive(current_amps, "current_amps")
    _require_non_negative(one_way_length_ft, "one_way_length_ft")
    _require_positive(ohms_per_1000ft, "ohms_per_1000ft")
    return 2.0 * current_amps * one_way_length_ft * ohms_per_1000ft / 1000.0


@dataclass(frozen=True)
class SolenoidVoltageCheck:
    supply_volts: float
    voltage_drop: float
    voltage_at_solenoid: float
    min_operating_volts: float
    min_operating_source: str
    margin_volts: float
    passes: bool


def check_solenoid_voltage(
    supply_volts: float,
    current_amps: float,
    one_way_length_ft: float,
    ohms_per_1000ft: float,
    min_operating_volts: float,
    min_operating_source: str,
) -> SolenoidVoltageCheck:
    """Check the voltage reaching a solenoid against its published minimum.

    ``current_amps`` should be the worst credible case — solenoid INRUSH
    current, plus any other solenoids sharing the common wire.
    ``min_operating_source`` cites the manufacturer document for the
    minimum operating voltage so the check stays traceable.
    """
    _require_positive(supply_volts, "supply_volts")
    _require_positive(min_operating_volts, "min_operating_volts")
    if not min_operating_source or not min_operating_source.strip():
        raise ValueError("min_operating_source is required so the check is traceable")
    drop = voltage_drop_volts(current_amps, one_way_length_ft, ohms_per_1000ft)
    at_solenoid = supply_volts - drop
    margin = at_solenoid - min_operating_volts
    return SolenoidVoltageCheck(
        supply_volts=supply_volts,
        voltage_drop=drop,
        voltage_at_solenoid=at_solenoid,
        min_operating_volts=min_operating_volts,
        min_operating_source=min_operating_source,
        margin_volts=margin,
        passes=margin >= 0,
    )


def smallest_adequate_awg(
    supply_volts: float,
    current_amps: float,
    one_way_length_ft: float,
    min_operating_volts: float,
    min_operating_source: str,
) -> int:
    """Smallest built-in copper wire size (largest AWG number) that keeps the
    solenoid at or above its minimum operating voltage.

    Raises ValueError when no size in the table is adequate — the fix is
    then a shorter run, a thicker custom conductor, or a different
    supply, decided by the designer.
    """
    for awg in sorted(COPPER_RESISTANCE_OHMS_PER_1000FT, reverse=True):
        result = check_solenoid_voltage(
            supply_volts,
            current_amps,
            one_way_length_ft,
            COPPER_RESISTANCE_OHMS_PER_1000FT[awg],
            min_operating_volts,
            min_operating_source,
        )
        if result.passes:
            return awg
    raise ValueError(
        f"no wire size in the built-in table ({sorted(COPPER_RESISTANCE_OHMS_PER_1000FT)} AWG) "
        f"holds {min_operating_volts} V at {one_way_length_ft} ft and {current_amps} A"
    )
