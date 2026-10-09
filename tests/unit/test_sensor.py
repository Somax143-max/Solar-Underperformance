from backend.diagnostics.rules.sensor import (
    diagnose_sensor_fault,
)


def test_detects_irradiance_sensor_fault():
    result = diagnose_sensor_fault(
        measured_irradiance_wm2=700.0,
        reference_irradiance_wm2=1000.0,
        actual_power_kw=890.0,
        reference_expected_power_kw=900.0,
    )

    assert result.fault == "irradiance_sensor_fault"
    assert result.detected is True
    assert result.confidence == 1.0
    assert len(result.evidence) == 3


def test_sensor_fault_requires_large_sensor_deviation():
    result = diagnose_sensor_fault(
        measured_irradiance_wm2=950.0,
        reference_irradiance_wm2=1000.0,
        actual_power_kw=890.0,
        reference_expected_power_kw=900.0,
    )

    assert result.detected is False
    assert result.fault == "no_sensor_fault"


def test_sensor_fault_requires_generation_consistency():
    result = diagnose_sensor_fault(
        measured_irradiance_wm2=700.0,
        reference_irradiance_wm2=1000.0,
        actual_power_kw=600.0,
        reference_expected_power_kw=900.0,
    )

    assert result.detected is False
    assert result.fault == "no_sensor_fault"


def test_sensor_fault_requires_sufficient_generation():
    result = diagnose_sensor_fault(
        measured_irradiance_wm2=300.0,
        reference_irradiance_wm2=500.0,
        actual_power_kw=44.0,
        reference_expected_power_kw=50.0,
    )

    assert result.detected is False
    assert result.fault == "no_sensor_fault"


def test_zero_reference_irradiance_is_safe():
    result = diagnose_sensor_fault(
        measured_irradiance_wm2=100.0,
        reference_irradiance_wm2=0.0,
        actual_power_kw=0.0,
        reference_expected_power_kw=0.0,
    )

    assert result.detected is False
    assert result.confidence == 0.0


def test_negative_irradiance_is_rejected():
    try:
        diagnose_sensor_fault(
            measured_irradiance_wm2=-1.0,
            reference_irradiance_wm2=1000.0,
            actual_power_kw=900.0,
            reference_expected_power_kw=900.0,
        )
        assert False
    except ValueError as exc:
        assert "measured_irradiance_wm2" in str(exc)


def test_negative_power_is_rejected():
    try:
        diagnose_sensor_fault(
            measured_irradiance_wm2=700.0,
            reference_irradiance_wm2=1000.0,
            actual_power_kw=-1.0,
            reference_expected_power_kw=900.0,
        )
        assert False
    except ValueError as exc:
        assert "actual_power_kw" in str(exc)
