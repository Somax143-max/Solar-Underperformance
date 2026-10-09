"""
End-to-end solar diagnosis pipeline.

Combines:
    - Physics-based expected power
    - Underperformance analysis
    - Thermal diagnosis
    - Soiling diagnosis
    - Shading diagnosis
    - Sensor-fault diagnosis
    - String/MPPT diagnosis
    - Root-cause selection
"""

from dataclasses import dataclass

from backend.diagnostics.diagnosis_result import DiagnosisResult
from backend.diagnostics.root_cause import (
    RootCauseCandidate,
    select_root_cause,
)
from backend.diagnostics.rules.sensor import (
    diagnose_sensor_fault,
)
from backend.diagnostics.rules.shading import (
    diagnose_shading,
)
from backend.diagnostics.rules.soiling import (
    diagnose_soiling,
)
from backend.diagnostics.rules.string import (
    diagnose_string_fault,
)
from backend.diagnostics.rules.thermal import (
    diagnose_thermal_derating,
)
from backend.pv_model.expected_power import (
    calculate_expected_power,
)
from backend.pv_model.performance import (
    calculate_performance,
)


@dataclass
class DiagnosticInput:
    """Telemetry and historical evidence required by the MVP."""

    plant_capacity_kw: float
    irradiance_poa_wm2: float
    module_temperature_c: float
    actual_power_kw: float
    inverter_temperature_c: float

    # Historical/environmental evidence for soiling.
    sustained_decline: bool = False
    stable_irradiance: bool = False

    # Historical evidence for shading.
    repeated_time_pattern: bool = False
    sufficient_irradiance: bool = False

    # Independent/reference irradiance evidence for sensor diagnosis.
    reference_irradiance_wm2: float | None = None
    reference_expected_power_kw: float | None = None

    # Optional string/MPPT evidence.
    target_string: str | None = None
    target_string_current_a: float | None = None
    peer_string_currents_a: list[float] | None = None


def run_diagnosis(
    data: DiagnosticInput,
) -> DiagnosisResult:
    """
    Run the complete MVP solar diagnosis pipeline.

    Pipeline:
        1. Calculate expected power.
        2. Compare expected vs actual power.
        3. Run thermal diagnostic.
        4. Run soiling diagnostic.
        5. Run shading diagnostic.
        6. Run sensor diagnostic when reference data is available.
        7. Run string diagnostic when string data is available.
        8. Select strongest root cause.
        9. Return unified DiagnosisResult.
    """

    expected = calculate_expected_power(
        plant_capacity_kw=data.plant_capacity_kw,
        irradiance_poa_wm2=data.irradiance_poa_wm2,
        module_temperature_c=data.module_temperature_c,
    )

    performance = calculate_performance(
        expected_power_kw=expected.expected_power_kw,
        actual_power_kw=data.actual_power_kw,
    )

    thermal = diagnose_thermal_derating(
        inverter_temperature_c=data.inverter_temperature_c,
        expected_power_kw=performance.expected_power_kw,
        actual_power_kw=performance.actual_power_kw,
    )

    soiling = diagnose_soiling(
        expected_power_kw=performance.expected_power_kw,
        actual_power_kw=performance.actual_power_kw,
        underperformance_percent=performance.underperformance_percent,
        sustained_decline=data.sustained_decline,
        stable_irradiance=data.stable_irradiance,
    )

    shading = diagnose_shading(
        expected_power_kw=performance.expected_power_kw,
        actual_power_kw=performance.actual_power_kw,
        underperformance_percent=performance.underperformance_percent,
        repeated_time_pattern=data.repeated_time_pattern,
        sufficient_irradiance=data.sufficient_irradiance,
    )

    candidates = [
        RootCauseCandidate(
            fault=thermal.fault,
            detected=thermal.detected,
            confidence=thermal.confidence,
            evidence=thermal.evidence,
            recommendation=thermal.recommendation,
        ),
        RootCauseCandidate(
            fault=soiling.fault,
            detected=soiling.detected,
            confidence=soiling.confidence,
            evidence=soiling.evidence,
            recommendation=soiling.recommendation,
        ),
        RootCauseCandidate(
            fault=shading.fault,
            detected=shading.detected,
            confidence=shading.confidence,
            evidence=shading.evidence,
            recommendation=shading.recommendation,
        ),
    ]

    # Sensor diagnosis is optional because independent/reference
    # irradiance data may not always be available.
    if (
        data.reference_irradiance_wm2 is not None
        and data.reference_expected_power_kw is not None
    ):
        sensor = diagnose_sensor_fault(
            measured_irradiance_wm2=data.irradiance_poa_wm2,
            reference_irradiance_wm2=data.reference_irradiance_wm2,
            actual_power_kw=data.actual_power_kw,
            reference_expected_power_kw=data.reference_expected_power_kw,
        )

        candidates.append(
            RootCauseCandidate(
                fault=sensor.fault,
                detected=sensor.detected,
                confidence=sensor.confidence,
                evidence=sensor.evidence,
                recommendation=sensor.recommendation,
            )
        )

    # String/MPPT diagnosis is optional because not every telemetry
    # source exposes string-level current measurements.
    if (
        data.target_string is not None
        and data.target_string_current_a is not None
        and data.peer_string_currents_a is not None
    ):
        string_diagnosis = diagnose_string_fault(
            target_string=data.target_string,
            target_current_a=data.target_string_current_a,
            peer_currents_a=data.peer_string_currents_a,
            irradiance_poa_wm2=data.irradiance_poa_wm2,
        )

        candidates.append(
            RootCauseCandidate(
                fault=string_diagnosis.fault,
                detected=string_diagnosis.detected,
                confidence=string_diagnosis.confidence,
                evidence=string_diagnosis.evidence,
                recommendation=string_diagnosis.recommendation,
            )
        )

    root_cause = select_root_cause(candidates)

    return DiagnosisResult(
        expected_power_kw=performance.expected_power_kw,
        actual_power_kw=performance.actual_power_kw,
        power_gap_kw=performance.power_gap_kw,
        underperformance_percent=performance.underperformance_percent,
        root_cause=root_cause.root_cause,
        confidence=root_cause.confidence,
        evidence=root_cause.evidence,
        recommendation=root_cause.recommendation,
    )
