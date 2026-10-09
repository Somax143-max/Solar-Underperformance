import pytest

from backend.diagnostics.rules.thermal import diagnose_thermal_derating


def test_thermal_derating_is_detected():
    result = diagnose_thermal_derating(
        inverter_temperature_c=85,
        expected_power_kw=900,
        actual_power_kw=720,
    )

    assert result.detected is True
    assert result.fault == "inverter_thermal_derating"
    assert result.confidence == pytest.approx(1.0)
    assert len(result.evidence) == 3


def test_normal_temperature_does_not_trigger_thermal_fault():
    result = diagnose_thermal_derating(
        inverter_temperature_c=55,
        expected_power_kw=900,
        actual_power_kw=720,
    )

    assert result.detected is False
    assert result.fault == "no_thermal_derating"


def test_small_underperformance_does_not_trigger_thermal_fault():
    result = diagnose_thermal_derating(
        inverter_temperature_c=85,
        expected_power_kw=900,
        actual_power_kw=860,
    )

    assert result.detected is False
    assert result.fault == "no_thermal_derating"


def test_low_expected_generation_does_not_trigger_thermal_fault():
    result = diagnose_thermal_derating(
        inverter_temperature_c=85,
        expected_power_kw=30,
        actual_power_kw=10,
    )

    assert result.detected is False
    assert result.fault == "no_thermal_derating"


def test_custom_temperature_threshold():
    result = diagnose_thermal_derating(
        inverter_temperature_c=70,
        expected_power_kw=900,
        actual_power_kw=700,
        high_temperature_threshold_c=65,
    )

    assert result.detected is True


def test_negative_expected_power_is_rejected():
    with pytest.raises(ValueError):
        diagnose_thermal_derating(
            inverter_temperature_c=85,
            expected_power_kw=-100,
            actual_power_kw=50,
        )


def test_negative_actual_power_is_rejected():
    with pytest.raises(ValueError):
        diagnose_thermal_derating(
            inverter_temperature_c=85,
            expected_power_kw=900,
            actual_power_kw=-50,
        )
