"""
Inverter thermal derating diagnostic rule.

Uses the shared evidence scoring engine so all diagnostic
rules can produce confidence consistently.
"""

from dataclasses import dataclass

from backend.diagnostics.evidence.scoring import (
    EvidenceItem,
    calculate_confidence,
)


DEFAULT_HIGH_TEMPERATURE_C = 75.0
DEFAULT_MIN_UNDERPERFORMANCE_PERCENT = 10.0
DEFAULT_MIN_EXPECTED_POWER_KW = 50.0


@dataclass
class ThermalDiagnosis:
    fault: str
    detected: bool
    confidence: float
    evidence: list[str]
    recommendation: str


def diagnose_thermal_derating(
    inverter_temperature_c: float,
    expected_power_kw: float,
    actual_power_kw: float,
    high_temperature_threshold_c: float = DEFAULT_HIGH_TEMPERATURE_C,
    min_underperformance_percent: float = DEFAULT_MIN_UNDERPERFORMANCE_PERCENT,
    min_expected_power_kw: float = DEFAULT_MIN_EXPECTED_POWER_KW,
) -> ThermalDiagnosis:
    """
    Detect likely inverter thermal derating.

    Evidence:
        - high inverter temperature
        - significant underperformance
        - sufficient expected generation

    Confidence is calculated by the shared evidence engine.
    """

    if expected_power_kw < 0:
        raise ValueError("expected_power_kw cannot be negative.")

    if actual_power_kw < 0:
        raise ValueError("actual_power_kw cannot be negative.")

    if high_temperature_threshold_c <= 0:
        raise ValueError(
            "high_temperature_threshold_c must be greater than zero."
        )

    if min_underperformance_percent < 0:
        raise ValueError(
            "min_underperformance_percent cannot be negative."
        )

    if min_expected_power_kw < 0:
        raise ValueError(
            "min_expected_power_kw cannot be negative."
        )

    if expected_power_kw == 0:
        underperformance_percent = 0.0
    else:
        underperformance_percent = (
            (expected_power_kw - actual_power_kw)
            / expected_power_kw
        ) * 100.0

    high_temperature = (
        inverter_temperature_c >= high_temperature_threshold_c
    )

    significant_underperformance = (
        underperformance_percent >= min_underperformance_percent
    )

    sufficient_generation = (
        expected_power_kw >= min_expected_power_kw
    )

    evidence_items = [
        EvidenceItem(
            description=(
                f"Inverter temperature is high "
                f"({inverter_temperature_c:.1f} C)."
            ),
            weight=0.40,
            satisfied=high_temperature,
        ),
        EvidenceItem(
            description=(
                f"Actual output is {underperformance_percent:.1f}% "
                f"below expected output."
            ),
            weight=0.40,
            satisfied=significant_underperformance,
        ),
        EvidenceItem(
            description=(
                f"Expected generation is sufficiently high "
                f"({expected_power_kw:.1f} kW)."
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
        high_temperature
        and significant_underperformance
        and sufficient_generation
    )

    if detected:
        recommendation = (
            "Inspect inverter cooling system, heat-sink condition, "
            "ventilation, and thermal operating environment."
        )
        fault = "inverter_thermal_derating"
    else:
        recommendation = (
            "Thermal derating evidence is insufficient. "
            "Check other diagnostic rules."
        )
        fault = "no_thermal_derating"

    return ThermalDiagnosis(
        fault=fault,
        detected=detected,
        confidence=confidence,
        evidence=satisfied_evidence,
        recommendation=recommendation,
    )
