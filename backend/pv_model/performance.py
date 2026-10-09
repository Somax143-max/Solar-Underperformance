"""
PV performance analysis.

Compares expected PV power against actual measured power
and calculates the current underperformance level.
"""

from dataclasses import dataclass


@dataclass
class PerformanceResult:
    expected_power_kw: float
    actual_power_kw: float
    power_gap_kw: float
    underperformance_percent: float
    is_underperforming: bool


def calculate_performance(
    expected_power_kw: float,
    actual_power_kw: float,
    underperformance_threshold_percent: float = 5.0,
) -> PerformanceResult:
    """
    Compare expected and actual AC power.

    Parameters
    ----------
    expected_power_kw:
        Physics-model expected AC power.

    actual_power_kw:
        Measured AC power from the plant/inverter.

    underperformance_threshold_percent:
        Percentage gap above which the system considers
        the plant to be underperforming.
    """

    if expected_power_kw < 0:
        raise ValueError("expected_power_kw cannot be negative.")

    if actual_power_kw < 0:
        raise ValueError("actual_power_kw cannot be negative.")

    if underperformance_threshold_percent < 0:
        raise ValueError(
            "underperformance_threshold_percent cannot be negative."
        )

    if expected_power_kw == 0:
        return PerformanceResult(
            expected_power_kw=0.0,
            actual_power_kw=round(actual_power_kw, 3),
            power_gap_kw=0.0,
            underperformance_percent=0.0,
            is_underperforming=False,
        )

    power_gap_kw = expected_power_kw - actual_power_kw

    underperformance_percent = (
        power_gap_kw / expected_power_kw
    ) * 100.0

    # A negative gap means actual production is higher than expected.
    # That is not considered underperformance.
    is_underperforming = (
        underperformance_percent >= underperformance_threshold_percent
    )

    return PerformanceResult(
        expected_power_kw=round(expected_power_kw, 3),
        actual_power_kw=round(actual_power_kw, 3),
        power_gap_kw=round(power_gap_kw, 3),
        underperformance_percent=round(
            max(underperformance_percent, 0.0),
            3,
        ),
        is_underperforming=is_underperforming,
    )
