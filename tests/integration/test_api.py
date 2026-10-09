from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

SAMPLE_INPUT = {
    "plant_capacity_kw": 1000.0,
    "irradiance_poa_wm2": 1000.0,
    "module_temperature_c": 25.0,
    "actual_power_kw": 500.0,
    "inverter_temperature_c": 85.0,
}


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "solar-diagnostic-api",
    }


def test_basic_diagnosis_endpoint():
    response = client.post("/api/v1/diagnostics", json=SAMPLE_INPUT)

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()


def test_full_diagnosis_endpoint():
    payload = {
        **SAMPLE_INPUT,
        "duration_hours": 2.0,
        "tariff_per_kwh": 8.0,
    }

    response = client.post("/api/v1/diagnostics/full", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert set(result.keys()) == {"diagnosis", "loss"}
    assert result["diagnosis"]["root_cause"] == "inverter_thermal_derating"
    assert result["loss"]["energy_loss_kwh"] == 800.0
    assert result["loss"]["financial_loss"] == 6400.0


def test_rejects_zero_plant_capacity():
    payload = {**SAMPLE_INPUT, "plant_capacity_kw": 0}

    response = client.post("/api/v1/diagnostics", json=payload)

    assert response.status_code == 422


def test_rejects_missing_required_input():
    payload = {
        key: value
        for key, value in SAMPLE_INPUT.items()
        if key != "actual_power_kw"
    }

    response = client.post("/api/v1/diagnostics", json=payload)

    assert response.status_code == 422


def test_rejects_unknown_input_fields():
    payload = {**SAMPLE_INPUT, "unknown_field": 123}

    response = client.post("/api/v1/diagnostics", json=payload)

    assert response.status_code == 422
