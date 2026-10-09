from backend.loss.energy import calculate_energy_loss


def test_calculates_energy_loss():
    assert calculate_energy_loss(200.0, 2.0) == 400.0


def test_calculates_fractional_duration():
    assert calculate_energy_loss(100.0, 1.5) == 150.0


def test_zero_power_loss():
    assert calculate_energy_loss(0.0, 5.0) == 0.0


def test_zero_duration():
    assert calculate_energy_loss(200.0, 0.0) == 0.0


def test_rejects_negative_power_loss():
    try:
        calculate_energy_loss(-100.0, 2.0)
        assert False
    except ValueError:
        assert True


def test_rejects_negative_duration():
    try:
        calculate_energy_loss(100.0, -2.0)
        assert False
    except ValueError:
        assert True
