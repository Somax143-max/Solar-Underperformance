"""
End-to-end loss calculation pipeline.

Connects power loss, energy loss, and financial loss
calculations into one reusable workflow.
"""

from backend.loss.energy import calculate_energy_loss
from backend.loss.financial import calculate_financial_loss
from backend.loss.loss_result import LossResult
from backend.loss.power import calculate_power_loss


def calculate_losses(
    expected_power_kw: float,
    actual_power_kw: float,
    duration_hours: float,
    tariff_per_kwh: float,
) -> LossResult:
    """
    Calculate complete underperformance impact.

    Pipeline:

        Expected vs Actual Power
                ↓
            Power Loss
                ↓
            Energy Loss
                ↓
          Financial Loss
    """

    power_loss_kw = calculate_power_loss(
        expected_power_kw=expected_power_kw,
        actual_power_kw=actual_power_kw,
    )

    energy_loss_kwh = calculate_energy_loss(
        power_loss_kw=power_loss_kw,
        duration_hours=duration_hours,
    )

    financial_loss = calculate_financial_loss(
        energy_loss_kwh=energy_loss_kwh,
        tariff_per_kwh=tariff_per_kwh,
    )

    return LossResult(
        power_loss_kw=power_loss_kw,
        energy_loss_kwh=energy_loss_kwh,
        financial_loss=financial_loss,
    )
