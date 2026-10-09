"""
Full solar diagnosis pipeline.

Combines:
    - Physics-based expected power
    - Underperformance detection
    - Root-cause diagnosis
    - Power loss
    - Energy loss
    - Financial loss

This is the main MVP orchestration layer.
"""

from dataclasses import dataclass

from backend.diagnostics.diagnosis_pipeline import (
    DiagnosticInput,
    run_diagnosis,
)
from backend.diagnostics.diagnosis_result import DiagnosisResult
from backend.loss.loss_pipeline import calculate_losses
from backend.loss.loss_result import LossResult


@dataclass
class FullDiagnosisResult:
    """Complete technical diagnosis and business-impact result."""

    diagnosis: DiagnosisResult
    loss: LossResult

    def to_dict(self) -> dict:
        """Convert the complete result to a JSON-friendly dictionary."""

        return {
            "diagnosis": self.diagnosis.to_dict(),
            "loss": self.loss.to_dict(),
        }


def run_full_diagnosis(
    data: DiagnosticInput,
    duration_hours: float,
    tariff_per_kwh: float,
) -> FullDiagnosisResult:
    """
    Run complete solar underperformance diagnosis.

    Flow:

        Telemetry
            ↓
        Expected Power
            ↓
        Performance Gap
            ↓
        Root Cause
            ↓
        Power Loss
            ↓
        Energy Loss
            ↓
        Financial Impact
    """

    diagnosis = run_diagnosis(data)

    loss = calculate_losses(
        expected_power_kw=diagnosis.expected_power_kw,
        actual_power_kw=diagnosis.actual_power_kw,
        duration_hours=duration_hours,
        tariff_per_kwh=tariff_per_kwh,
    )

    return FullDiagnosisResult(
        diagnosis=diagnosis,
        loss=loss,
    )
