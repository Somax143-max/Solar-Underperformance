from backend.loss.financial import calculate_financial_loss


def test_calculates_financial_loss():
    assert calculate_financial_loss(400.0, 8.0) == 3200.0


def test_calculates_fractional_tariff():
    assert calculate_financial_loss(400.0, 7.5) == 3000.0


def test_zero_energy_loss():
    assert calculate_financial_loss(0.0, 8.0) == 0.0


def test_zero_tariff():
    assert calculate_financial_loss(400.0, 0.0) == 0.0


def test_rejects_negative_energy_loss():
    try:
        calculate_financial_loss(-100.0, 8.0)
        assert False
    except ValueError:
        assert True


def test_rejects_negative_tariff():
    try:
        calculate_financial_loss(100.0, -8.0)
        assert False
    except ValueError:
        assert True
