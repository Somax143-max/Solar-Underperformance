from backend.diagnostics.rules.shading import (
    diagnose_shading,
)


def test_detects_shading():
    result = diagnose_shading(
        expected_power_kw=900.0,
        actual_power_kw=800.0,
        underperformance_percent=11.111,
        repeated_time_pattern=True,
        sufficient_irradiance=True,
    )

    assert result.fault == "shading"
    assert result.detected is True
    assert result.confidence == 1.0
    assert len(result.evidence) == 4


def test_rejects_missing_time_pattern():
    result = diagnose_shading(
        expected_power_kw=900.0,
        actual_power_kw=800.0,
        underperformance_percent=11.111,
        repeated_time_pattern=False,
        sufficient_irradiance=True,
    )

    assert result.detected is False
    assert result.fault == "no_shading"


def test_rejects_insufficient_irradiance():
    result = diagnose_shading(
        expected_power_kw=900.0,
        actual_power_kw=800.0,
        underperformance_percent=11.111,
        repeated_time_pattern=True,
        sufficient_irradiance=False,
    )

    assert result.detected is False
    assert result.fault == "no_shading"


def test_rejects_small_underperformance():
    result = diagnose_shading(
        expected_power_kw=900.0,
        actual_power_kw=880.0,
        underperformance_percent=2.222,
        repeated_time_pattern=True,
        sufficient_irradiance=True,
    )

    assert result.detected is False
    assert result.fault == "no_shading"


def test_rejects_low_expected_generation():
    result = diagnose_shading(
        expected_power_kw=20.0,
        actual_power_kw=15.0,
        underperformance_percent=25.0,
        repeated_time_pattern=True,
        sufficient_irradiance=True,
    )

    assert result.detected is False
    assert result.fault == "no_shading"


def test_invalid_expected_power_is_rejected():
    try:
        diagnose_shading(
            expected_power_kw=-1.0,
            actual_power_kw=10.0,
            underperformance_percent=10.0,
            repeated_time_pattern=True,
            sufficient_irradiance=True,
        )
        assert False
    except ValueError:
        assert True


def test_invalid_actual_power_is_rejected():
    try:
        diagnose_shading(
            expected_power_kw=100.0,
            actual_power_kw=-1.0,
            underperformance_percent=10.0,
            repeated_time_pattern=True,
            sufficient_irradiance=True,
        )
        assert False
    except ValueError:
        assert True
