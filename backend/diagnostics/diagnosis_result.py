"""
Unified diagnostic result model.

This module defines the standard output structure used by the
solar underperformance diagnostic engine.
"""

from dataclasses import dataclass, field


@dataclass
class DiagnosisResult:
    """
    Standard result returned by the diagnostic engine.
    """

    expected_power_kw: float
    actual_power_kw: float
    power_gap_kw: float
    underperformance_percent: float

    root_cause: str
    confidence: float

    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""

    def __post_init__(self) -> None:
        """Validate the diagnostic result."""

        if self.expected_power_kw < 0:
            raise ValueError(
                "expected_power_kw cannot be negative."
            )

        if self.actual_power_kw < 0:
            raise ValueError(
                "actual_power_kw cannot be negative."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1."
            )

        if self.underperformance_percent < 0:
            raise ValueError(
                "underperformance_percent cannot be negative."
            )

    def to_dict(self) -> dict:
        """
        Convert the diagnosis result into a JSON-friendly dictionary.
        """

        return {
            "expected_power_kw": self.expected_power_kw,
            "actual_power_kw": self.actual_power_kw,
            "power_gap_kw": self.power_gap_kw,
            "underperformance_percent": (
                self.underperformance_percent
            ),
            "root_cause": self.root_cause,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "recommendation": self.recommendation,
        }
