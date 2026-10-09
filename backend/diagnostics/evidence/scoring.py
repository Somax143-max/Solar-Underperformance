"""
Reusable evidence scoring utilities for the diagnostic engine.

The scoring system converts weighted diagnostic evidence into
a normalized confidence score between 0 and 1.
"""

from dataclasses import dataclass


@dataclass
class EvidenceItem:
    description: str
    weight: float
    satisfied: bool


def calculate_confidence(
    evidence_items: list[EvidenceItem],
) -> float:
    """
    Calculate normalized confidence from weighted evidence.

    Only satisfied evidence contributes to the score.

    Example:
        Evidence A = 0.4 and satisfied
        Evidence B = 0.3 and satisfied
        Evidence C = 0.3 and not satisfied

        Confidence = 0.7
    """

    if not evidence_items:
        return 0.0

    total_weight = 0.0
    satisfied_weight = 0.0

    for item in evidence_items:
        if item.weight < 0:
            raise ValueError(
                "Evidence weights cannot be negative."
            )

        total_weight += item.weight

        if item.satisfied:
            satisfied_weight += item.weight

    if total_weight == 0:
        return 0.0

    confidence = satisfied_weight / total_weight

    return round(min(max(confidence, 0.0), 1.0), 3)
