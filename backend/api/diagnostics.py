from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from backend.diagnostics.diagnosis_pipeline import (
    DiagnosticInput,
    run_diagnosis,
)
from backend.diagnostics.full_diagnosis import run_full_diagnosis

router = APIRouter(tags=["Diagnostics"])


class DiagnosisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plant_capacity_kw: float = Field(gt=0)
    irradiance_poa_wm2: float = Field(ge=0)
    module_temperature_c: float
    actual_power_kw: float = Field(ge=0)
    inverter_temperature_c: float
    sustained_decline: bool = False
    stable_irradiance: bool = False
    repeated_time_pattern: bool = False
    sufficient_irradiance: bool = False
    reference_irradiance_wm2: float | None = Field(default=None, ge=0)
    reference_expected_power_kw: float | None = Field(default=None, ge=0)
    target_string: str | None = None
    target_string_current_a: float | None = Field(default=None, ge=0)
    peer_string_currents_a: list[float] | None = None


class FullDiagnosisRequest(DiagnosisRequest):
    duration_hours: float = Field(gt=0)
    tariff_per_kwh: float = Field(ge=0)


@router.post("/diagnostics")
def diagnose(request: DiagnosisRequest):
    data = DiagnosticInput(**request.model_dump())
    result = run_diagnosis(data)
    return result.to_dict()


@router.post("/diagnostics/full")
def diagnose_full(request: FullDiagnosisRequest):
    values = request.model_dump(
        exclude={"duration_hours", "tariff_per_kwh"}
    )
    data = DiagnosticInput(**values)

    result = run_full_diagnosis(
        data=data,
        duration_hours=request.duration_hours,
        tariff_per_kwh=request.tariff_per_kwh,
    )
    return result.to_dict()
