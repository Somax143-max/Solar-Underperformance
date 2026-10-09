"""
String / MPPT fault diagnostic rule.

Detects a likely abnormal PV string by comparing its measured
current against the median current of peer strings operating
under the same irradiance conditions.

The rule is intentionally peer-based rather than using a fixed
absolute current threshold.
"""

from dataclasses import dataclass
from statistics import median

from backend.diagnostics.evidence.scoring import (
    EvidenceItem,
    calculate_confidence,
)


DEFAULT_MIN_IRRADIANCE_WM2 = 300.0
DEFAULT_MIN_PEER_COUNT = 2
DEFAULT_MIN_CURRENT_DEVIATION_PERCENT = 20.0


@dataclass
class StringDiagnosis:
    fault: str
    detected: bool
    confidence: float
    evidence: list[str]
    recommendation: str
    target_string: str | None = None
    target_current_a: float = 0.0
    peer_median_current_a: float = 0.0
    deviation_percent: float = 0.0


def diagnose_string_fault(
    target_string: str,
    target_current_a: float,
    peer_currents_a: list[float],
    irradiance_poa_wm2: float,
    min_irradiance_wm2: float = DEFAULT_MIN_IRRADIANCE_WM2,
    min_peer_count: int = DEFAULT_MIN_PEER_COUNT,
    min_current_deviation_percent: float = (
        DEFAULT_MIN_CURRENT_DEVIATION_PERCENT
    ),
) -> StringDiagnosis:
    """
    Diagnose a likely string/MPPT fault.

    Detection requires:

        1. Sufficient irradiance for meaningful comparison.
        2. Enough peer strings.
        3. Target current materially below peer median.

    Peer comparison reduces dependence on plant-specific absolute
    current thresholds.
    """

    if not target_string.strip():
        raise ValueError("target_string cannot be empty.")

    if target_current_a < 0:
        raise ValueError("target_current_a cannot be negative.")

    if irradiance_poa_wm2 < 0:
        raise ValueError("irradiance_poa_wm2 cannot be negative.")

    if min_irradiance_wm2 < 0:
        raise ValueError(
            "min_irradiance_wm2 cannot be negative."
        )

    if min_peer_count < 1:
        raise ValueError("min_peer_count must be at least 1.")

    if min_current_deviation_percent < 0:
        raise ValueError(
            "min_current_deviation_percent cannot be negative."
        )

    if any(current < 0 for current in peer_currents_a):
        raise ValueError(
            "peer_currents_a cannot contain negative values."
        )

    peer_count_sufficient = (
        len(peer_currents_a) >= min_peer_count
    )

    sufficient_irradiance = (
        irradiance_poa_wm2 >= min_irradiance_wm2
    )

    if peer_count_sufficient:
        peer_median_current_a = median(peer_currents_a)
    else:
        peer_median_current_a = 0.0

    if peer_median_current_a == 0:
        deviation_percent = 0.0
    else:
        deviation_percent = (
            (
                peer_median_current_a
                - target_current_a
            )
            / peer_median_current_a
        ) * 100.0

    significant_current_deviation = (
        deviation_percent >= min_current_deviation_percent
    )

    evidence_items = [
        EvidenceItem(
            description=(
                f"Target string current is "
                f"{deviation_percent:.1f}% below the peer median."
            ),
            weight=0.45,
            satisfied=significant_current_deviation,
        ),
        EvidenceItem(
            description=(
                f"Sufficient peer strings are available "
                f"({len(peer_currents_a)} peers)."
            ),
            weight=0.25,
            satisfied=peer_count_sufficient,
        ),
        EvidenceItem(
            description=(
                f"Irradiance is sufficient for comparison "
                f"({irradiance_poa_wm2:.1f} W/m²)."
            ),
            weight=0.30,
            satisfied=sufficient_irradiance,
        ),
    ]

    confidence = calculate_confidence(evidence_items)

    satisfied_evidence = [
        item.description
        for item in evidence_items
        if item.satisfied
    ]

    detected = (
        significant_current_deviation
        and peer_count_sufficient
        and sufficient_irradiance
    )

    if detected:
        fault = "string_or_mppt_fault"
        recommendation = (
            f"Inspect {target_string} for string-level faults, "
            "connector issues, fuse problems, module faults, "
            "or MPPT abnormalities. Compare voltage and current "
            "with neighboring strings before intervention."
        )
    else:
        fault = "no_string_fault"
        recommendation = (
            "String-fault evidence is insufficient. "
            "Check other diagnostic rules."
        )

    return StringDiagnosis(
        fault=fault,
        detected=detected,
        confidence=confidence,
        evidence=satisfied_evidence,
        recommendation=recommendation,
        target_string=target_string,
        target_current_a=round(target_current_a, 3),
        peer_median_current_a=round(peer_median_current_a, 3),
        deviation_percent=round(max(deviation_percent, 0.0), 3),
    )
