from backend.diagnostics.diagnosis_result import DiagnosisResult


def test_diagnosis_result_creation():
    result = DiagnosisResult(
        expected_power_kw=828.0,
        actual_power_kw=700.0,
        power_gap_kw=128.0,
        underperformance_percent=15.459,
        root_cause="inverter_thermal_derating",
        confidence=1.0,
        evidence=[
            "Inverter temperature is high (85.0 C).",
            "Actual output is 15.5% below expected output.",
        ],
        recommendation="Inspect inverter cooling system.",
    )

    assert result.expected_power_kw == 828.0
    assert result.actual_power_kw == 700.0
    assert result.power_gap_kw == 128.0
    assert result.root_cause == "inverter_thermal_derating"
    assert result.confidence == 1.0
    assert len(result.evidence) == 2


def test_diagnosis_result_to_dict():
    result = DiagnosisResult(
        expected_power_kw=900.0,
        actual_power_kw=720.0,
        power_gap_kw=180.0,
        underperformance_percent=20.0,
        root_cause="inverter_thermal_derating",
        confidence=1.0,
        evidence=["High inverter temperature."],
        recommendation="Inspect inverter cooling.",
    )

    data = result.to_dict()

    assert isinstance(data, dict)
    assert data["expected_power_kw"] == 900.0
    assert data["actual_power_kw"] == 720.0
    assert data["power_gap_kw"] == 180.0
    assert data["underperformance_percent"] == 20.0
    assert data["root_cause"] == "inverter_thermal_derating"
    assert data["confidence"] == 1.0
    assert data["evidence"] == ["High inverter temperature."]
    assert data["recommendation"] == "Inspect inverter cooling."


def test_negative_expected_power_is_rejected():
    try:
        DiagnosisResult(
            expected_power_kw=-1.0,
            actual_power_kw=100.0,
            power_gap_kw=-101.0,
            underperformance_percent=0.0,
            root_cause="test",
            confidence=0.5,
        )
        assert False
    except ValueError:
        assert True


def test_negative_actual_power_is_rejected():
    try:
        DiagnosisResult(
            expected_power_kw=500.0,
            actual_power_kw=-1.0,
            power_gap_kw=501.0,
            underperformance_percent=0.0,
            root_cause="test",
            confidence=0.5,
        )
        assert False
    except ValueError:
        assert True


def test_invalid_confidence_is_rejected():
    try:
        DiagnosisResult(
            expected_power_kw=500.0,
            actual_power_kw=400.0,
            power_gap_kw=100.0,
            underperformance_percent=20.0,
            root_cause="test",
            confidence=1.5,
        )
        assert False
    except ValueError:
        assert True


def test_negative_underperformance_is_rejected():
    try:
        DiagnosisResult(
            expected_power_kw=500.0,
            actual_power_kw=600.0,
            power_gap_kw=-100.0,
            underperformance_percent=-20.0,
            root_cause="test",
            confidence=0.5,
        )
        assert False
    except ValueError:
        assert True
