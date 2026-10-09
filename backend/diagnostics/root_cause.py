"""
Root-cause selection engine.

Combines individual diagnostic rule outputs and selects
the most likely root cause based on detection status
and evidence confidence.
"""

from dataclasses import dataclass


DEFAULT_MIN_CONFIDENCE = 0.50


@dataclass
class RootCauseCandidate:
    """Standard representation of a candidate root cause."""

    fault: str
    detected: bool
    confidence: float
    evidence: list[str]
    recommendation: str


@dataclass
class RootCauseResult:
    """Final root-cause selection result."""

    root_cause: str
    confidence: float
    evidence: list[str]
    recommendation: str


def select_root_cause(
    candidates: list[RootCauseCandidate],
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
) -> RootCauseResult:
    """
    Select the strongest detected root cause.

    Selection logic:
        1. Ignore undetected candidates.
        2. Ignore candidates below minimum confidence.
        3. Select the highest-confidence candidate.
        4. Return insufficient-evidence result if none qualify.
    """

    if not 0.0 <= min_confidence <= 1.0:
        raise ValueError(
            "min_confidence must be between 0 and 1."
        )

    for candidate in candidates:
        if not 0.0 <= candidate.confidence <= 1.0:
            raise ValueError(
                "Candidate confidence must be between 0 and 1."
            )

    eligible_candidates = [
        candidate
        for candidate in candidates
        if candidate.detected
        and candidate.confidence >= min_confidence
    ]

    if not eligible_candidates:
        return RootCauseResult(
            root_cause="unknown_or_insufficient_evidence",
            confidence=0.0,
            evidence=[],
            recommendation=(
                "Insufficient evidence for a reliable root-cause "
                "diagnosis. Collect additional telemetry and "
                "continue monitoring."
            ),
        )

    selected = max(
        eligible_candidates,
        key=lambda candidate: candidate.confidence,
    )

    return RootCauseResult(
        root_cause=selected.fault,
        confidence=selected.confidence,
        evidence=list(selected.evidence),
        recommendation=selected.recommendation,
    )
