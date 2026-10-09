from backend.loss.power import calculate_power_loss


def test_calculates_power_loss():
    assert calculate_power_loss(900.0, 700.0) == 200.0


def test_returns_zero_when_output_matches_expected():
    assert calculate_power_loss(900.0, 900.0) == 0.0


def test_clamps_negative_loss_to_zero():
    assert calculate_power_loss(700.0, 900.0) == 0.0


def test_rejects_negative_expected_power():
    try:
        calculate_power_loss(-100.0, 50.0)
        assert False
    except ValueError:
        assert True


def test_rejects_negative_actual_power():
    try:
        calculate_power_loss(100.0, -50.0)
        assert False
    except ValueError:
        assert True
