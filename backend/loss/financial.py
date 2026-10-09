"""
Financial-loss calculation.

Converts estimated energy loss into estimated monetary
impact using a user-supplied electricity tariff.
"""


def calculate_financial_loss(
    energy_loss_kwh: float,
    tariff_per_kwh: float,
) -> float:
    """
    Calculate estimated financial loss.

    Parameters
    ----------
    energy_loss_kwh:
        Estimated lost energy in kWh.

    tariff_per_kwh:
        Applicable electricity value/tariff per kWh.

    Returns
    -------
    float
        Estimated financial loss in the same currency
        units as the supplied tariff.
    """

    if energy_loss_kwh < 0:
        raise ValueError(
            "energy_loss_kwh cannot be negative."
        )

    if tariff_per_kwh < 0:
        raise ValueError(
            "tariff_per_kwh cannot be negative."
        )

    financial_loss = (
        energy_loss_kwh * tariff_per_kwh
    )

    return round(financial_loss, 2)
