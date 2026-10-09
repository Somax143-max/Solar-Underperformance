import pytest

from backend.diagnostics.evidence.scoring import (
    EvidenceItem,
    calculate_confidence,
)


def test_all_evidence_satisfied():
    evidence = [
        EvidenceItem(
            description="High inverter temperature",
            weight=0.4,
            satisfied=True,
        ),
        EvidenceItem(
            description="Significant power deviation",
            weight=0.4,
            satisfied=True,
        ),
        EvidenceItem(
            description="Sufficient expected generation",
            weight=0.2,
            satisfied=True,
        ),
    ]

    assert calculate_confidence(evidence) == pytest.approx(1.0)


def test_partial_evidence():
    evidence = [
        EvidenceItem(
            description="High inverter temperature",
            weight=0.4,
            satisfied=True,
        ),
        EvidenceItem(
            description="Significant power deviation",
            weight=0.4,
            satisfied=False,
        ),
        EvidenceItem(
            description="Sufficient expected generation",
            weight=0.2,
            satisfied=True,
        ),
    ]

    assert calculate_confidence(evidence) == pytest.approx(0.6)


def test_no_evidence():
    assert calculate_confidence([]) == 0.0


def test_zero_total_weight():
    evidence = [
        EvidenceItem(
            description="Test",
            weight=0.0,
            satisfied=True,
        )
    ]

    assert calculate_confidence(evidence) == 0.0


def test_negative_weight_is_rejected():
    evidence = [
        EvidenceItem(
            description="Invalid",
            weight=-0.1,
            satisfied=True,
        )
    ]

    with pytest.raises(ValueError):
        calculate_confidence(evidence)
