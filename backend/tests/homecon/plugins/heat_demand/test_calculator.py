from pytest import approx
from homecon.plugins.heat_demand.calculator import HeatingCurveHeatDemandCalculator


class TestStateBasedHeatingCurveWantedHeatGainCalculator:
    def test_calculate_wanted_heat_gain(self):

        calculator = HeatingCurveHeatDemandCalculator(
            ambient_temperature=10.0,
            indoor_temperature=20.0,
            setpoint_temperature=20.0,
            ambient_temperature_min=-10.0,
            ambient_temperature_max=18.0,
            heat_demand_max=8000.0,
            indoor_temperature_correction_factor=0.2,
        )
        heat = calculator.calculate_wanted_heat_gain()
        assert heat == approx(2285, rel=0.01)

        calculator = HeatingCurveHeatDemandCalculator(
            ambient_temperature=18.0,
            indoor_temperature=20.0,
            setpoint_temperature=20.0,
            ambient_temperature_min=-10.0,
            ambient_temperature_max=18.0,
            heat_demand_max=8000.0,
            indoor_temperature_correction_factor=0.2,
        )
        heat = calculator.calculate_wanted_heat_gain()
        assert heat == 0

        calculator = HeatingCurveHeatDemandCalculator(
            ambient_temperature=18.0,
            indoor_temperature=21.0,
            setpoint_temperature=20.0,
            ambient_temperature_min=-10.0,
            ambient_temperature_max=18.0,
            heat_demand_max=8000.0,
            indoor_temperature_correction_factor=0.2,
        )
        heat = calculator.calculate_wanted_heat_gain()
        assert heat == -0.2 * 8000

        calculator = HeatingCurveHeatDemandCalculator(
            ambient_temperature=0.0,
            indoor_temperature=23.0,
            setpoint_temperature=20.0,
            ambient_temperature_min=-10.0,
            ambient_temperature_max=18.0,
            heat_demand_max=8000.0,
            indoor_temperature_correction_factor=0.2,
        )
        heat = calculator.calculate_wanted_heat_gain()
        assert heat == approx(342, rel=0.01)

