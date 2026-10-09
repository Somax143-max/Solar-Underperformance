from backend.diagnostics.diagnosis_pipeline import (
    DiagnosticInput,
)
from backend.diagnostics.full_diagnosis import (
    run_full_diagnosis,
)


def test_full_diagnosis_combines_root_cause_and_loss():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=500.0,
        inverter_temperature_c=85.0,
    )

    result = run_full_diagnosis(
        data=data,
        duration_hours=2.0,
        tariff_per_kwh=8.0,
    )

    assert result.diagnosis.expected_power_kw == 900.0
    assert result.diagnosis.actual_power_kw == 500.0
    assert result.diagnosis.root_cause == (
        "inverter_thermal_derating"
    )

    assert result.loss.power_loss_kw == 400.0
    assert result.loss.energy_loss_kwh == 800.0
    assert result.loss.financial_loss == 6400.0


def test_full_diagnosis_normal_operation_has_no_loss():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=880.0,
        inverter_temperature_c=45.0,
    )

    result = run_full_diagnosis(
        data=data,
        duration_hours=2.0,
        tariff_per_kwh=8.0,
    )

    assert result.diagnosis.root_cause == (
        "unknown_or_insufficient_evidence"
    )

    assert result.loss.power_loss_kw == 20.0
    assert result.loss.energy_loss_kwh == 40.0
    assert result.loss.financial_loss == 320.0


def test_full_result_can_be_converted_to_dict():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=500.0,
        inverter_temperature_c=85.0,
    )

    result = run_full_diagnosis(
        data=data,
        duration_hours=1.0,
        tariff_per_kwh=8.0,
    )

    output = result.to_dict()

    assert "diagnosis" in output
    assert "loss" in output
    assert output["loss"]["power_loss_kw"] == 400.0
