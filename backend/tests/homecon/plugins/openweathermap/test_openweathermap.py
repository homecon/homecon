from homecon.plugins.openweathermap.openweathermap import OpenWeatherMapForecastClient
from plugins.openweathermap.mock import MockOpenWeatherMapApiClient


class TestOpenWeatherMapApiClient:
    def test_get_forecast(self):
        client = OpenWeatherMapForecastClient(api_client=MockOpenWeatherMapApiClient(), api_key='test', longitude=5.58, latitude=51.05)
        daily_forecasts, hourly_forecasts = client.get_forecast()
        assert len(daily_forecasts) == 8
        assert daily_forecasts[0].timestamp == 1635937200
        assert daily_forecasts[0].temperature_min == 4.51
        assert daily_forecasts[0].temperature_max == 8.34
        assert daily_forecasts[0].icon == 'sun_7'

        assert len(hourly_forecasts) == 48
