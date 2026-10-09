"""
Sensor fault diagnostic rule.

Detects likely irradiance-sensor problems by comparing the plant's
measured irradiance against an independent/reference irradiance
measurement and checking whether actual generation is consistent
with the reference conditions.
"""

from dataclasses import dataclass

from backend.diagnostics.evidence.scoring import (
    EvidenceItem,
    calculate_confidence,
)


DEFAULT_MIN_SENSOR_DEVIATION_PERCENT = 15.0
DEFAULT_MIN_EXPECTED_POWER_KW = 50.0
DEFAULT_MAX_REFERENCE_POWER_DEVIATION_PERCENT = 8.0


@dataclass
class SensorDiagnosis:
    fault: str
    detected: bool
    confidence: float
    evidence: list[str]
    recommendation: str


def diagnose_sensor_fault(
    measured_irradiance_wm2: float,
    reference_irradiance_wm2: float,
    actual_power_kw: float,
    reference_expected_power_kw: float,
    sensor_deviation_percent: float = DEFAULT_MIN_SENSOR_DEVIATION_PERCENT,
    min_expected_power_kw: float = DEFAULT_MIN_EXPECTED_POWER_KW,
    max_reference_power_deviation_percent: float = (
        DEFAULT_MAX_REFERENCE_POWER_DEVIATION_PERCENT
    ),
) -> SensorDiagnosis:
    """
    Diagnose a likely irradiance sensor fault.

    A sensor fault is considered likely when:

        1. Measured irradiance differs substantially from an
           independent/reference irradiance measurement.
        2. Actual plant output is reasonably consistent with the
           reference-based expected power.
        3. Reference generation conditions are sufficient.

    Zero-reference conditions are treated as insufficient evidence.
    """

    if measured_irradiance_wm2 < 0:
        raise ValueError(
            "measured_irradiance_wm2 cannot be negative."
        )

    if reference_irradiance_wm2 < 0:
        raise ValueError(
            "reference_irradiance_wm2 cannot be negative."
        )

    if actual_power_kw < 0:
        raise ValueError("actual_power_kw cannot be negative.")

    if reference_expected_power_kw < 0:
        raise ValueError(
            "reference_expected_power_kw cannot be negative."
        )

    if sensor_deviation_percent < 0:
        raise ValueError(
            "sensor_deviation_percent cannot be negative."
        )

    if min_expected_power_kw < 0:
        raise ValueError(
            "min_expected_power_kw cannot be negative."
        )

    if max_reference_power_deviation_percent < 0:
        raise ValueError(
            "max_reference_power_deviation_percent cannot be negative."
        )

    # A zero reference irradiance means there is not enough
    # information to compare the sensor meaningfully.
    if reference_irradiance_wm2 == 0:
        return SensorDiagnosis(
            fault="no_sensor_fault",
            detected=False,
            confidence=0.0,
            evidence=[],
            recommendation=(
                "Insufficient reference irradiance data. "
                "Continue monitoring before diagnosing a sensor fault."
            ),
        )

    irradiance_deviation_percent = (
        abs(
            measured_irradiance_wm2
            - reference_irradiance_wm2
        )
        / reference_irradiance_wm2
    ) * 100.0

    if reference_expected_power_kw == 0:
        power_deviation_percent = 0.0
    else:
        power_deviation_percent = (
            abs(
                actual_power_kw
                - reference_expected_power_kw
            )
            / reference_expected_power_kw
        ) * 100.0

    significant_sensor_deviation = (
        irradiance_deviation_percent
        >= sensor_deviation_percent
    )

    generation_consistent_with_reference = (
        power_deviation_percent
        <= max_reference_power_deviation_percent
    )

    sufficient_generation = (
        reference_expected_power_kw >= min_expected_power_kw
    )

    evidence_items = [
        EvidenceItem(
            description=(
                f"Irradiance sensor differs from the reference by "
                f"{irradiance_deviation_percent:.1f}%."
            ),
            weight=0.45,
            satisfied=significant_sensor_deviation,
        ),
        EvidenceItem(
            description=(
                f"Actual generation is only "
                f"{power_deviation_percent:.1f}% away from "
                f"reference-based expected generation."
            ),
            weight=0.35,
            satisfied=generation_consistent_with_reference,
        ),
        EvidenceItem(
            description=(
                f"Reference expected generation is sufficiently high "
                f"({reference_expected_power_kw:.1f} kW)."
            ),
            weight=0.20,
            satisfied=sufficient_generation,
        ),
    ]

    confidence = calculate_confidence(evidence_items)

    satisfied_evidence = [
        item.description
        for item in evidence_items
        if item.satisfied
    ]

    detected = (
        significant_sensor_deviation
        and generation_consistent_with_reference
        and sufficient_generation
    )

    if detected:
        fault = "irradiance_sensor_fault"
        recommendation = (
            "Inspect and recalibrate the irradiance sensor. "
            "Compare it with an independent reference sensor "
            "before diagnosing PV equipment."
        )
    else:
        fault = "no_sensor_fault"
        recommendation = (
            "Sensor-fault evidence is insufficient. "
            "Check other diagnostic rules."
        )

    return SensorDiagnosis(
        fault=fault,
        detected=detected,
        confidence=confidence,
        evidence=satisfied_evidence,
        recommendation=recommendation,
    )
