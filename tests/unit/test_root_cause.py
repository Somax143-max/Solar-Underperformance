from backend.diagnostics.root_cause import (
    RootCauseCandidate,
    select_root_cause,
)


def test_selects_highest_confidence_detected_fault():
    candidates = [
        RootCauseCandidate(
            fault="inverter_thermal_derating",
            detected=True,
            confidence=1.0,
            evidence=[
                "Inverter temperature is high (85.0 C).",
                "Actual output is below expected output.",
            ],
            recommendation="Inspect inverter cooling system.",
        ),
        RootCauseCandidate(
            fault="soiling",
            detected=True,
            confidence=0.6,
            evidence=["Gradual production decline detected."],
            recommendation="Inspect and clean PV modules.",
        ),
    ]

    result = select_root_cause(candidates)

    assert result.root_cause == "inverter_thermal_derating"
    assert result.confidence == 1.0
    assert len(result.evidence) == 2
    assert result.recommendation == (
        "Inspect inverter cooling system."
    )


def test_ignores_undetected_faults():
    candidates = [
        RootCauseCandidate(
            fault="inverter_thermal_derating",
            detected=False,
            confidence=1.0,
            evidence=[],
            recommendation="No action.",
        ),
        RootCauseCandidate(
            fault="soiling",
            detected=True,
            confidence=0.7,
            evidence=["Gradual production decline detected."],
            recommendation="Inspect and clean PV modules.",
        ),
    ]

    result = select_root_cause(candidates)

    assert result.root_cause == "soiling"
    assert result.confidence == 0.7


def test_ignores_candidates_below_confidence_threshold():
    candidates = [
        RootCauseCandidate(
            fault="inverter_thermal_derating",
            detected=True,
            confidence=0.4,
            evidence=["Weak thermal evidence."],
            recommendation="Continue monitoring.",
        )
    ]

    result = select_root_cause(candidates)

    assert result.root_cause == (
        "unknown_or_insufficient_evidence"
    )
    assert result.confidence == 0.0


def test_returns_fallback_when_no_fault_is_detected():
    candidates = [
        RootCauseCandidate(
            fault="inverter_thermal_derating",
            detected=False,
            confidence=0.0,
            evidence=[],
            recommendation="No action.",
        )
    ]

    result = select_root_cause(candidates)

    assert result.root_cause == (
        "unknown_or_insufficient_evidence"
    )
    assert result.confidence == 0.0
    assert result.evidence == []


def test_custom_confidence_threshold():
    candidates = [
        RootCauseCandidate(
            fault="soiling",
            detected=True,
            confidence=0.7,
            evidence=["Production decline detected."],
            recommendation="Inspect modules.",
        )
    ]

    result = select_root_cause(
        candidates,
        min_confidence=0.8,
    )

    assert result.root_cause == (
        "unknown_or_insufficient_evidence"
    )


def test_invalid_min_confidence_is_rejected():
    try:
        select_root_cause([], min_confidence=1.5)
        assert False
    except ValueError:
        assert True


def test_invalid_candidate_confidence_is_rejected():
    candidates = [
        RootCauseCandidate(
            fault="test_fault",
            detected=True,
            confidence=1.5,
            evidence=[],
            recommendation="Test.",
        )
    ]

    try:
        select_root_cause(candidates)
        assert False
    except ValueError:
        assert True
