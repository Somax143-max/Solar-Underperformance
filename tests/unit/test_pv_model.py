import pytest

from backend.pv_model.expected_power import calculate_expected_power


def test_expected_power_under_standard_conditions():
    result = calculate_expected_power(
        plant_capacity_kw=1000,
        irradiance_poa_wm2=1000,
        module_temperature_c=25,
    )

    assert result.expected_power_kw == pytest.approx(900)
    assert result.irradiance_factor == pytest.approx(1.0)
    assert result.temperature_factor == pytest.approx(1.0)


def test_high_module_temperature_reduces_expected_power():
    normal = calculate_expected_power(
        plant_capacity_kw=1000,
        irradiance_poa_wm2=1000,
        module_temperature_c=25,
    )

    hot = calculate_expected_power(
        plant_capacity_kw=1000,
        irradiance_poa_wm2=1000,
        module_temperature_c=50,
    )

    assert hot.expected_power_kw < normal.expected_power_kw


def test_lower_irradiance_reduces_expected_power():
    high_irradiance = calculate_expected_power(
        plant_capacity_kw=1000,
        irradiance_poa_wm2=1000,
        module_temperature_c=25,
    )

    low_irradiance = calculate_expected_power(
        plant_capacity_kw=1000,
        irradiance_poa_wm2=500,
        module_temperature_c=25,
    )

    assert low_irradiance.expected_power_kw < high_irradiance.expected_power_kw


def test_negative_irradiance_is_rejected():
    with pytest.raises(ValueError):
        calculate_expected_power(
            plant_capacity_kw=1000,
            irradiance_poa_wm2=-100,
            module_temperature_c=25,
        )


def test_invalid_capacity_is_rejected():
    with pytest.raises(ValueError):
        calculate_expected_power(
            plant_capacity_kw=0,
            irradiance_poa_wm2=1000,
            module_temperature_c=25,
        )
