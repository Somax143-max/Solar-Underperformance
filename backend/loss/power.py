"""
Power-loss calculation.

Calculates instantaneous power loss from the difference
between expected and actual PV output.
"""


def calculate_power_loss(
    expected_power_kw: float,
    actual_power_kw: float,
) -> float:
    """
    Calculate instantaneous power loss in kW.

    Positive value:
        Plant is producing less than expected.

    Zero:
        Actual output equals expected output.

    Negative values are clamped to zero because this module
    measures underperformance loss only.
    """

    if expected_power_kw < 0:
        raise ValueError(
            "expected_power_kw cannot be negative."
        )

    if actual_power_kw < 0:
        raise ValueError(
            "actual_power_kw cannot be negative."
        )

    power_loss_kw = expected_power_kw - actual_power_kw

    return round(max(power_loss_kw, 0.0), 3)
