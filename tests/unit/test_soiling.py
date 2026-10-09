from backend.diagnostics.rules.soiling import (
    diagnose_soiling,
)


def test_detects_soiling():
    result = diagnose_soiling(
        expected_power_kw=900.0,
        actual_power_kw=800.0,
        underperformance_percent=11.111,
        sustained_decline=True,
        stable_irradiance=True,
    )

    assert result.fault == "soiling"
    assert result.detected is True
    assert result.confidence == 1.0
    assert len(result.evidence) == 4


def test_rejects_single_observation_without_decline():
    result = diagnose_soiling(
        expected_power_kw=900.0,
        actual_power_kw=800.0,
        underperformance_percent=11.111,
        sustained_decline=False,
        stable_irradiance=True,
    )

    assert result.detected is False
    assert result.fault == "no_soiling"


def test_rejects_unstable_irradiance():
    result = diagnose_soiling(
        expected_power_kw=900.0,
        actual_power_kw=800.0,
        underperformance_percent=11.111,
        sustained_decline=True,
        stable_irradiance=False,
    )

    assert result.detected is False
    assert result.fault == "no_soiling"


def test_rejects_small_underperformance():
    result = diagnose_soiling(
        expected_power_kw=900.0,
        actual_power_kw=880.0,
        underperformance_percent=2.222,
        sustained_decline=True,
        stable_irradiance=True,
    )

    assert result.detected is False
    assert result.fault == "no_soiling"


def test_rejects_low_expected_generation():
    result = diagnose_soiling(
        expected_power_kw=20.0,
        actual_power_kw=15.0,
        underperformance_percent=25.0,
        sustained_decline=True,
        stable_irradiance=True,
    )

    assert result.detected is False
    assert result.fault == "no_soiling"


def test_invalid_expected_power_is_rejected():
    try:
        diagnose_soiling(
            expected_power_kw=-1.0,
            actual_power_kw=10.0,
            underperformance_percent=10.0,
            sustained_decline=True,
            stable_irradiance=True,
        )
        assert False
    except ValueError:
        assert True


def test_invalid_actual_power_is_rejected():
    try:
        diagnose_soiling(
            expected_power_kw=100.0,
            actual_power_kw=-1.0,
            underperformance_percent=10.0,
            sustained_decline=True,
            stable_irradiance=True,
        )
        assert False
    except ValueError:
        assert True
