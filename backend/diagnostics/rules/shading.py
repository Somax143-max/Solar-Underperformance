"""
Shading diagnostic rule.

Detects likely PV shading from a repeated time-of-day
dependent production reduction under suitable irradiance.
"""

from dataclasses import dataclass

from backend.diagnostics.evidence.scoring import (
    EvidenceItem,
    calculate_confidence,
)


DEFAULT_MIN_UNDERPERFORMANCE_PERCENT = 8.0
DEFAULT_MIN_EXPECTED_POWER_KW = 50.0


@dataclass
class ShadingDiagnosis:
    """Result of the shading diagnostic rule."""

    fault: str
    detected: bool
    confidence: float
    evidence: list[str]
    recommendation: str


def diagnose_shading(
    expected_power_kw: float,
    actual_power_kw: float,
    underperformance_percent: float,
    repeated_time_pattern: bool,
    sufficient_irradiance: bool,
    min_underperformance_percent: float = (
        DEFAULT_MIN_UNDERPERFORMANCE_PERCENT
    ),
    min_expected_power_kw: float = (
        DEFAULT_MIN_EXPECTED_POWER_KW
    ),
) -> ShadingDiagnosis:
    """
    Detect likely PV shading.

    Evidence:
        - measurable underperformance
        - repeated time-of-day pattern
        - sufficient irradiance
        - sufficient expected generation

    The repeated time pattern is important because shading
    is typically geometric and therefore tied to solar position.
    """

    if expected_power_kw < 0:
        raise ValueError(
            "expected_power_kw cannot be negative."
        )

    if actual_power_kw < 0:
        raise ValueError(
            "actual_power_kw cannot be negative."
        )

    if underperformance_percent < 0:
        raise ValueError(
            "underperformance_percent cannot be negative."
        )

    if min_underperformance_percent < 0:
        raise ValueError(
            "min_underperformance_percent cannot be negative."
        )

    if min_expected_power_kw < 0:
        raise ValueError(
            "min_expected_power_kw cannot be negative."
        )

    significant_underperformance = (
        underperformance_percent
        >= min_underperformance_percent
    )

    sufficient_generation = (
        expected_power_kw >= min_expected_power_kw
    )

    evidence_items = [
        EvidenceItem(
            description=(
                f"Actual output is "
                f"{underperformance_percent:.1f}% below expected output."
            ),
            weight=0.30,
            satisfied=significant_underperformance,
        ),
        EvidenceItem(
            description=(
                "Underperformance repeats at a similar time of day."
            ),
            weight=0.35,
            satisfied=repeated_time_pattern,
        ),
        EvidenceItem(
            description=(
                "Irradiance is sufficient for meaningful comparison."
            ),
            weight=0.15,
            satisfied=sufficient_irradiance,
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
        significant_underperformance
        and repeated_time_pattern
        and sufficient_irradiance
        and sufficient_generation
    )

    if detected:
        fault = "shading"
        recommendation = (
            "Inspect the affected array area for nearby structures, "
            "vegetation, or other objects causing recurring shade."
        )
    else:
        fault = "no_shading"
        recommendation = (
            "Shading evidence is insufficient. "
            "Check other diagnostic rules."
        )

    return ShadingDiagnosis(
        fault=fault,
        detected=detected,
        confidence=confidence,
        evidence=satisfied_evidence,
        recommendation=recommendation,
    )
