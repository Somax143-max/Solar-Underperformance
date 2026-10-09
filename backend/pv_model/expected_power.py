"""
Physics-informed expected PV power model.

MVP purpose:
    Estimate the AC power a solar PV plant should produce under
    current environmental and operating conditions.

This model is intentionally simple and transparent for the hackathon.
It is NOT intended to be a bankable PV performance model.
"""

from dataclasses import dataclass


REFERENCE_IRRADIANCE_WM2 = 1000.0
REFERENCE_MODULE_TEMP_C = 25.0

DEFAULT_TEMPERATURE_COEFFICIENT = -0.004
DEFAULT_PERFORMANCE_RATIO = 0.90


@dataclass
class ExpectedPowerResult:
    expected_power_kw: float
    irradiance_factor: float
    temperature_factor: float
    performance_ratio: float


def calculate_expected_power(
    plant_capacity_kw: float,
    irradiance_poa_wm2: float,
    module_temperature_c: float,
    temperature_coefficient: float = DEFAULT_TEMPERATURE_COEFFICIENT,
    performance_ratio: float = DEFAULT_PERFORMANCE_RATIO,
) -> ExpectedPowerResult:
    """
    Calculate expected AC PV power in kW.

    plant_capacity_kw:
        Installed plant capacity in kW.

    irradiance_poa_wm2:
        Plane-of-array irradiance in W/m2.

    module_temperature_c:
        PV module temperature in degrees Celsius.

    temperature_coefficient:
        Relative power temperature coefficient per degree Celsius.
        Typical silicon PV value is approximately -0.004 per degree C.

    performance_ratio:
        Simplified system performance factor representing normal
        electrical and system losses.
    """

    if plant_capacity_kw <= 0:
        raise ValueError("plant_capacity_kw must be greater than zero.")

    if irradiance_poa_wm2 < 0:
        raise ValueError("irradiance_poa_wm2 cannot be negative.")

    if not 0 < performance_ratio <= 1:
        raise ValueError("performance_ratio must be between 0 and 1.")

    irradiance_factor = irradiance_poa_wm2 / REFERENCE_IRRADIANCE_WM2

    temperature_difference = (
        module_temperature_c - REFERENCE_MODULE_TEMP_C
    )

    temperature_factor = (
        1.0 + temperature_coefficient * temperature_difference
    )

    temperature_factor = max(temperature_factor, 0.0)

    expected_power_kw = (
        plant_capacity_kw
        * irradiance_factor
        * temperature_factor
        * performance_ratio
    )

    expected_power_kw = min(
        expected_power_kw,
        plant_capacity_kw,
    )

    return ExpectedPowerResult(
        expected_power_kw=round(expected_power_kw, 3),
        irradiance_factor=round(irradiance_factor, 4),
        temperature_factor=round(temperature_factor, 4),
        performance_ratio=performance_ratio,
    )
