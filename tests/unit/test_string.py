from backend.diagnostics.rules.string import (
    diagnose_string_fault,
)


def test_detects_string_fault():
    result = diagnose_string_fault(
        target_string="String-07",
        target_current_a=6.0,
        peer_currents_a=[9.8, 10.1, 10.0, 9.9],
        irradiance_poa_wm2=850.0,
    )

    assert result.fault == "string_or_mppt_fault"
    assert result.detected is True
    assert result.confidence == 1.0
    assert result.target_string == "String-07"
    assert result.peer_median_current_a == 9.95
    assert result.deviation_percent == 39.698
    assert len(result.evidence) == 3


def test_normal_string_is_not_flagged():
    result = diagnose_string_fault(
        target_string="String-03",
        target_current_a=9.7,
        peer_currents_a=[9.8, 10.0, 9.9, 9.7],
        irradiance_poa_wm2=850.0,
    )

    assert result.detected is False
    assert result.fault == "no_string_fault"


def test_low_irradiance_prevents_diagnosis():
    result = diagnose_string_fault(
        target_string="String-02",
        target_current_a=4.0,
        peer_currents_a=[8.0, 8.2, 7.9],
        irradiance_poa_wm2=150.0,
    )

    assert result.detected is False
    assert result.fault == "no_string_fault"


def test_insufficient_peers_prevents_diagnosis():
    result = diagnose_string_fault(
        target_string="String-02",
        target_current_a=4.0,
        peer_currents_a=[8.0],
        irradiance_poa_wm2=800.0,
    )

    assert result.detected is False
    assert result.fault == "no_string_fault"


def test_zero_peer_current_is_safe():
    result = diagnose_string_fault(
        target_string="String-01",
        target_current_a=0.0,
        peer_currents_a=[0.0, 0.0, 0.0],
        irradiance_poa_wm2=800.0,
    )

    assert result.detected is False
    assert result.confidence == 0.55


def test_negative_target_current_is_rejected():
    try:
        diagnose_string_fault(
            target_string="String-01",
            target_current_a=-1.0,
            peer_currents_a=[8.0, 8.1, 8.2],
            irradiance_poa_wm2=800.0,
        )
        assert False
    except ValueError as exc:
        assert "target_current_a" in str(exc)


def test_negative_peer_current_is_rejected():
    try:
        diagnose_string_fault(
            target_string="String-01",
            target_current_a=5.0,
            peer_currents_a=[8.0, -1.0, 8.2],
            irradiance_poa_wm2=800.0,
        )
        assert False
    except ValueError as exc:
        assert "peer_currents_a" in str(exc)


def test_empty_string_name_is_rejected():
    try:
        diagnose_string_fault(
            target_string="",
            target_current_a=5.0,
            peer_currents_a=[8.0, 8.1, 8.2],
            irradiance_poa_wm2=800.0,
        )
        assert False
    except ValueError as exc:
        assert "target_string" in str(exc)
