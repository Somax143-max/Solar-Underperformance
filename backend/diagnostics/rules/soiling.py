"""
Soiling diagnostic rule.

Detects likely PV module soiling from sustained underperformance
under otherwise suitable generation conditions.
"""

from dataclasses import dataclass

from backend.diagnostics.evidence.scoring import (
    EvidenceItem,
    calculate_confidence,
)


DEFAULT_MIN_UNDERPERFORMANCE_PERCENT = 8.0
DEFAULT_MIN_EXPECTED_POWER_KW = 50.0


@dataclass
class SoilingDiagnosis:
    """Result of the soiling diagnostic rule."""

    fault: str
    detected: bool
    confidence: float
    evidence: list[str]
    recommendation: str


def diagnose_soiling(
    expected_power_kw: float,
    actual_power_kw: float,
    underperformance_percent: float,
    sustained_decline: bool,
    stable_irradiance: bool,
    min_underperformance_percent: float = (
        DEFAULT_MIN_UNDERPERFORMANCE_PERCENT
    ),
    min_expected_power_kw: float = (
        DEFAULT_MIN_EXPECTED_POWER_KW
    ),
) -> SoilingDiagnosis:
    """
    Detect likely module soiling.

    Evidence:
        - measurable underperformance
        - sustained production decline
        - relatively stable irradiance
        - sufficient expected generation

    The rule is intentionally conservative. A single low-power
    observation is not enough to claim soiling.
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
                "Production decline is sustained across observations."
            ),
            weight=0.30,
            satisfied=sustained_decline,
        ),
        EvidenceItem(
            description=(
                "Irradiance conditions are relatively stable."
            ),
            weight=0.20,
            satisfied=stable_irradiance,
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
        and sustained_decline
        and stable_irradiance
        and sufficient_generation
    )

    if detected:
        fault = "soiling"
        recommendation = (
            "Inspect PV module surfaces for dust or soiling "
            "and schedule cleaning if confirmed."
        )
    else:
        fault = "no_soiling"
        recommendation = (
            "Soiling evidence is insufficient. "
            "Check other diagnostic rules."
        )

    return SoilingDiagnosis(
        fault=fault,
        detected=detected,
        confidence=confidence,
        evidence=satisfied_evidence,
        recommendation=recommendation,
    )
