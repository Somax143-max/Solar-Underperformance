from backend.diagnostics.diagnosis_pipeline import (
    DiagnosticInput,
    run_diagnosis,
)


def test_pipeline_detects_thermal_derating():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=500.0,
        inverter_temperature_c=85.0,
    )

    result = run_diagnosis(data)

    assert result.expected_power_kw == 900.0
    assert result.actual_power_kw == 500.0
    assert result.power_gap_kw == 400.0
    assert result.underperformance_percent == 44.444
    assert result.root_cause == "inverter_thermal_derating"
    assert result.confidence == 1.0
    assert len(result.evidence) == 3


def test_pipeline_detects_soiling():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=800.0,
        inverter_temperature_c=45.0,
        sustained_decline=True,
        stable_irradiance=True,
    )

    result = run_diagnosis(data)

    assert result.root_cause == "soiling"
    assert result.confidence == 1.0
    assert len(result.evidence) == 4


def test_pipeline_detects_shading():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=800.0,
        inverter_temperature_c=45.0,
        repeated_time_pattern=True,
        sufficient_irradiance=True,
    )

    result = run_diagnosis(data)

    assert result.root_cause == "shading"
    assert result.confidence == 1.0
    assert len(result.evidence) == 4


def test_pipeline_returns_insufficient_evidence_when_normal():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=880.0,
        inverter_temperature_c=45.0,
    )

    result = run_diagnosis(data)

    assert result.root_cause == (
        "unknown_or_insufficient_evidence"
    )
    assert result.confidence == 0.0
    assert result.evidence == []


def test_pipeline_handles_low_irradiance():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=500.0,
        module_temperature_c=25.0,
        actual_power_kw=440.0,
        inverter_temperature_c=45.0,
    )

    result = run_diagnosis(data)

    assert result.expected_power_kw == 450.0
    assert result.actual_power_kw == 440.0
    assert result.root_cause == (
        "unknown_or_insufficient_evidence"
    )
    assert result.confidence == 0.0
    assert result.evidence == []


def test_pipeline_detects_sensor_fault():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=700.0,
        module_temperature_c=25.0,
        actual_power_kw=890.0,
        inverter_temperature_c=45.0,
        reference_irradiance_wm2=1000.0,
        reference_expected_power_kw=900.0,
    )

    result = run_diagnosis(data)

    assert result.root_cause == "irradiance_sensor_fault"
    assert result.confidence == 1.0
    assert len(result.evidence) == 3


def test_pipeline_does_not_require_sensor_reference_data():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=800.0,
        inverter_temperature_c=45.0,
        sustained_decline=True,
        stable_irradiance=True,
    )

    result = run_diagnosis(data)

    assert result.root_cause == "soiling"
    assert result.confidence == 1.0


def test_pipeline_does_not_report_sensor_fault_without_reference():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=700.0,
        module_temperature_c=25.0,
        actual_power_kw=630.0,
        inverter_temperature_c=45.0,
    )

    result = run_diagnosis(data)

    assert result.root_cause == (
        "unknown_or_insufficient_evidence"
    )
    assert result.confidence == 0.0


def test_pipeline_sensor_reference_can_be_insufficient():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=700.0,
        module_temperature_c=25.0,
        actual_power_kw=890.0,
        inverter_temperature_c=45.0,
        reference_irradiance_wm2=0.0,
        reference_expected_power_kw=0.0,
    )

    result = run_diagnosis(data)

    assert result.root_cause == (
        "unknown_or_insufficient_evidence"
    )
    assert result.confidence == 0.0


def test_pipeline_detects_string_fault():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=850.0,
        module_temperature_c=25.0,
        actual_power_kw=800.0,
        inverter_temperature_c=45.0,
        target_string="String-07",
        target_string_current_a=6.0,
        peer_string_currents_a=[
            9.8,
            10.1,
            10.0,
            9.9,
        ],
    )

    result = run_diagnosis(data)

    assert result.root_cause == "string_or_mppt_fault"
    assert result.confidence == 1.0
    assert len(result.evidence) == 3


def test_pipeline_does_not_require_string_data():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=800.0,
        inverter_temperature_c=45.0,
        sustained_decline=True,
        stable_irradiance=True,
    )

    result = run_diagnosis(data)

    assert result.root_cause == "soiling"
    assert result.confidence == 1.0


def test_pipeline_ignores_incomplete_string_data():
    data = DiagnosticInput(
        plant_capacity_kw=1000.0,
        irradiance_poa_wm2=1000.0,
        module_temperature_c=25.0,
        actual_power_kw=880.0,
        inverter_temperature_c=45.0,
        target_string="String-07",
        target_string_current_a=6.0,
        peer_string_currents_a=None,
    )

    result = run_diagnosis(data)

    assert result.root_cause == (
        "unknown_or_insufficient_evidence"
    )
    assert result.confidence == 0.0
