from pytest import approx

from homecon.core.states.state import TimestampedValue
from homecon.plugins.timeseries.average_timeseries import AverageTimeseries


class TestAverageTimeseries:
    def test_calculate_average(self):
        timeseries = [
            TimestampedValue(0, 0),
            TimestampedValue(8, 1),
            TimestampedValue(17, 2),
            TimestampedValue(20, 1),
            TimestampedValue(20.1, 0),
            TimestampedValue(25, 1),
            TimestampedValue(35, 0),
        ]

        average = AverageTimeseries._calculate_average(timeseries, 5, 26)
        assert average == approx(((8-5)*0 + (17-8)*1 + (20-17)*2 + (20.1-20)*1 + (25-20.1)*0 + (26-25)*1)/(26-5))
