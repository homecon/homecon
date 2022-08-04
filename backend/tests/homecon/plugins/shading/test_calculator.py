from datetime import datetime
from typing import Optional

from pytest import approx

from homecon.plugins.shading.calculator import IrradianceThresholdPositionCalculator, LinearIrradianceThresholdCalculator
from homecon.plugins.shading.domain import IShading


class MockShading(IShading):
    def __init__(self, position=0.0, minimum_position=0.0, maximum_position=1.0, irradiance=250., area=4.):
        self._position = position
        self._minimum_position = minimum_position
        self._maximum_position = maximum_position
        self._irradiance = irradiance
        self._area = area

    @property
    def position(self) -> float:
        return self._position

    def set_position(self, value) -> None:
        pass

    @property
    def minimum_position(self) -> float:
        return self._minimum_position

    @property
    def maximum_position(self) -> float:
        return self._maximum_position

    def get_heat_gain(self, position: float, date: datetime, cloud_cover: Optional[float] = 0.0) -> float:
        return (1-position) * (1-cloud_cover) * self._irradiance * self._area

    def get_irradiance(self, position: float, date: datetime, cloud_cover: Optional[float] = 0.0) -> float:
        return (1-position) * (1-cloud_cover) * self._irradiance


class TestWantedHeatGainIrradianceThresholdCalculator:
    def test_get_irradiance_thresholds(self):
        calculator = LinearIrradianceThresholdCalculator(-2000, 0, 20, 100)
        thresholds = calculator.get_irradiance_thresholds(2000)
        assert len(thresholds) == 0

        thresholds = calculator.get_irradiance_thresholds(0)
        assert thresholds[0].irradiance == 100

        thresholds = calculator.get_irradiance_thresholds(-1000)
        assert thresholds[0].irradiance == 60

        thresholds = calculator.get_irradiance_thresholds(-2000)
        assert thresholds[0].irradiance == 20

        thresholds = calculator.get_irradiance_thresholds(-5000)
        assert thresholds[0].irradiance == 20


class TestIrradianceThresholdPositionCalculator:

    def test_get_positions_empty(self):
        shadings = []
        calculator = IrradianceThresholdPositionCalculator()
        positions = calculator.get_positions(shadings, 1000)
        assert positions == []

    def test_get_positions_open(self):
        shadings = [MockShading(), MockShading()]
        calculator = IrradianceThresholdPositionCalculator()
        positions = calculator.get_positions(shadings, 5000)
        assert positions == [0.0, 0.0]

    def test_get_positions_minimum_position(self):
        shadings = [MockShading(minimum_position=0.5), MockShading(minimum_position=1.0)]
        calculator = IrradianceThresholdPositionCalculator()
        positions = calculator.get_positions(shadings, 5000)
        assert positions == [0.5, 1.0]

    def test_get_positions_closed(self):
        shadings = [MockShading(), MockShading()]
        calculator = IrradianceThresholdPositionCalculator()
        positions = calculator.get_positions(shadings, -1)
        assert positions == [1.0, 1.0]

    def test_get_positions_linear_threshold(self):
        shadings = [MockShading(irradiance=50), MockShading(irradiance=50)]
        calculator = IrradianceThresholdPositionCalculator(
            irradiance_threshold_calculator=LinearIrradianceThresholdCalculator(-2000, 0, 20, 100)
        )
        positions = calculator.get_positions(shadings, 0)
        assert positions == [0.0, 0.0]

        positions = calculator.get_positions(shadings, -1000)
        assert positions == [0.5, 0.5]

        positions = calculator.get_positions(shadings, -2000)
        assert positions == [1.0, 1.0]

    def test_get_positions_half(self):
        shadings = [MockShading(irradiance=80), MockShading(irradiance=80, area=50)]
        calculator = IrradianceThresholdPositionCalculator()
        positions = calculator.get_positions(shadings, -1)
        assert positions == [0.5, 0.5]
