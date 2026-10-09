import pytest

from backend.pv_model.performance import calculate_performance


def test_normal_performance():
    result = calculate_performance(
        expected_power_kw=900,
        actual_power_kw=890,
    )

    assert result.power_gap_kw == pytest.approx(10)
    assert result.underperformance_percent == pytest.approx(1.111)
    assert result.is_underperforming is False


def test_underperformance_is_detected():
    result = calculate_performance(
        expected_power_kw=900,
        actual_power_kw=750,
    )

    assert result.power_gap_kw == pytest.approx(150)
    assert result.underperformance_percent == pytest.approx(16.667)
    assert result.is_underperforming is True


def test_custom_threshold():
    result = calculate_performance(
        expected_power_kw=900,
        actual_power_kw=855,
        underperformance_threshold_percent=4.0,
    )

    assert result.underperformance_percent == pytest.approx(5.0)
    assert result.is_underperforming is True


def test_actual_above_expected_is_not_underperformance():
    result = calculate_performance(
        expected_power_kw=900,
        actual_power_kw=950,
    )

    assert result.power_gap_kw == pytest.approx(-50)
    assert result.underperformance_percent == pytest.approx(0.0)
    assert result.is_underperforming is False


def test_negative_expected_power_is_rejected():
    with pytest.raises(ValueError):
        calculate_performance(
            expected_power_kw=-100,
            actual_power_kw=90,
        )


def test_negative_actual_power_is_rejected():
    with pytest.raises(ValueError):
        calculate_performance(
            expected_power_kw=900,
            actual_power_kw=-10,
        )


def test_zero_expected_power():
    result = calculate_performance(
        expected_power_kw=0,
        actual_power_kw=0,
    )

    assert result.power_gap_kw == 0.0
    assert result.underperformance_percent == 0.0
    assert result.is_underperforming is False
