from backend.diagnostics.diagnosis_pipeline import DiagnosticInput
from backend.diagnostics.full_diagnosis import run_full_diagnosis


def test_end_to_end_thermal_fault_and_financial_loss():
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
    assert result.diagnosis.power_gap_kw == 400.0
    assert result.diagnosis.root_cause == "inverter_thermal_derating"

    assert result.loss.power_loss_kw == 400.0
    assert result.loss.energy_loss_kwh == 800.0
    assert result.loss.financial_loss == 6400.0


def test_end_to_end_result_is_json_friendly():
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

    output = result.to_dict()

    assert set(output.keys()) == {"diagnosis", "loss"}
    assert output["diagnosis"]["root_cause"] == "inverter_thermal_derating"
    assert output["loss"]["energy_loss_kwh"] == 800.0
    assert output["loss"]["financial_loss"] == 6400.0