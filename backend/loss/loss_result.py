"""
Unified loss calculation result.

Contains instantaneous power loss, estimated energy loss,
and estimated financial impact.
"""

from dataclasses import dataclass


@dataclass
class LossResult:
    """Combined solar underperformance loss result."""

    power_loss_kw: float
    energy_loss_kwh: float
    financial_loss: float

    def __post_init__(self) -> None:
        if self.power_loss_kw < 0:
            raise ValueError(
                "power_loss_kw cannot be negative."
            )

        if self.energy_loss_kwh < 0:
            raise ValueError(
                "energy_loss_kwh cannot be negative."
            )

        if self.financial_loss < 0:
            raise ValueError(
                "financial_loss cannot be negative."
            )

    def to_dict(self) -> dict:
        """Convert the result into a JSON-friendly dictionary."""

        return {
            "power_loss_kw": self.power_loss_kw,
            "energy_loss_kwh": self.energy_loss_kwh,
            "financial_loss": self.financial_loss,
        }
