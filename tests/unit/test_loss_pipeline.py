from backend.loss.loss_pipeline import calculate_losses


def test_calculates_complete_loss_pipeline():
    result = calculate_losses(
        expected_power_kw=900.0,
        actual_power_kw=700.0,
        duration_hours=2.0,
        tariff_per_kwh=8.0,
    )

    assert result.power_loss_kw == 200.0
    assert result.energy_loss_kwh == 400.0
    assert result.financial_loss == 3200.0


def test_no_loss_when_actual_matches_expected():
    result = calculate_losses(
        expected_power_kw=900.0,
        actual_power_kw=900.0,
        duration_hours=2.0,
        tariff_per_kwh=8.0,
    )

    assert result.power_loss_kw == 0.0
    assert result.energy_loss_kwh == 0.0
    assert result.financial_loss == 0.0


def test_actual_above_expected_does_not_create_loss():
    result = calculate_losses(
        expected_power_kw=700.0,
        actual_power_kw=900.0,
        duration_hours=2.0,
        tariff_per_kwh=8.0,
    )

    assert result.power_loss_kw == 0.0
    assert result.energy_loss_kwh == 0.0
    assert result.financial_loss == 0.0
