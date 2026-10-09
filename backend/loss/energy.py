"""
Energy-loss calculation.

Converts instantaneous PV power loss into estimated
energy loss over a specified time duration.
"""


def calculate_energy_loss(
    power_loss_kw: float,
    duration_hours: float,
) -> float:
    """
    Calculate energy loss in kWh.

    Parameters
    ----------
    power_loss_kw:
        Instantaneous power loss in kW.

    duration_hours:
        Duration over which the loss is assumed
        to continue, in hours.

    Returns
    -------
    float
        Estimated energy loss in kWh.
    """

    if power_loss_kw < 0:
        raise ValueError(
            "power_loss_kw cannot be negative."
        )

    if duration_hours < 0:
        raise ValueError(
            "duration_hours cannot be negative."
        )

    energy_loss_kwh = (
        power_loss_kw * duration_hours
    )

    return round(energy_loss_kwh, 3)
