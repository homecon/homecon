import logging
import random
import time

from datetime import datetime
from typing import List

from homecon.plugins.weather.weather import ForecastClient, Forecast, DailyForecast
from homecon.plugins.openweathermap.openweathermap import OpenWeatherMap as OriginalOpenWeatherMap


logger = logging.getLogger(__name__)


class MockOpenWeatherMapForecastClient(ForecastClient):
    ICON_MAP = {
        '01d': 'sun_1',
        '02d': 'sun_3',
        '03d': 'cloud_4',
        '04d': 'cloud_5',
        '09d': 'cloud_7',
        '10d': 'sun_7',
        '11d': 'cloud_10',
        '13d': 'cloud_13',
        '50d': 'sun_6',
        '01n': 'moon_1',
        '02n': 'moon_3',
        '03n': 'cloud_4',
        '04n': 'cloud_5',
        '09n': 'cloud_7',
        '10n': 'moon_7',
        '11n': 'cloud_10',
        '13n': 'cloud_13',
        '50n': 'moon_6',
        'clear-day': 'sun_1',
        'clear-night': 'moon_1',
        'rain': 'cloud_8',
        'snow': 'cloud_13',
        'sleet': 'cloud_15',
        'wind': 'wind',
        'fog': 'cloud_6',
        'cloudy': 'cloud_4',
        'partly-cloudy-day': 'sun_4',
        'partly-cloudy-night': 'moon_4',
        'hail': 'cloud_11',
        'thunderstorm': 'cloud_10'
    }

    def get_forecast(self) -> (List[DailyForecast], List[Forecast]):
        """
        create a mock forecast
        """
        now = int(datetime.fromtimestamp(time.time()).replace(minute=0, second=0, microsecond=0).timestamp())
        noon = int(datetime.fromtimestamp(time.time()).replace(hour=12, minute=0, second=0, microsecond=0).timestamp())

        forecast_hourly = []
        for i in range(48):
            forecast_hourly.append(
                Forecast(
                    timestamp=now + i * 3600,
                    temperature=round(20 * random.random(), 2),
                    pressure=round(1000 + 20 * random.random(), 2),
                    relative_humidity=round(0.1 + 0.9 * random.random(), 2),
                    dew_point=round(12 * random.random(), 2),
                    cloud_cover=round(random.random(), 2),
                    wind_speed=round(15 * random.random(), 2),
                    wind_direction=round(360 * random.random(), 2),
                    icon=list(self.ICON_MAP.values())[random.randint(0, len(self.ICON_MAP)-1)],
                    rain=round(30 * random.random(), 0),
                )
            )

        forecast_daily = []
        for i in range(7):
            temp_max = round(20 * random.random(), 2)

            forecast_daily.append(
                DailyForecast(
                    timestamp=noon + i * 24 * 3600,
                    temperature_min=temp_max-5,
                    temperature_max=temp_max,
                    pressure=round(1000 + 20 * random.random(), 2),
                    relative_humidity=round(0.1 + 0.9 * random.random(), 2),
                    dew_point=round(12 * random.random(), 2),
                    cloud_cover=round(random.random(), 2),
                    wind_speed=round(15 * random.random(), 2),
                    wind_direction=round(360 * random.random(), 2),
                    icon=list(self.ICON_MAP.values())[random.randint(0, len(self.ICON_MAP)-1)],
                    rain=round(30 * random.random(), 0),
                )
            )

        return forecast_daily, forecast_hourly


class OpenWeatherMap(OriginalOpenWeatherMap):
    def _get_forecast_client(self):
        return MockOpenWeatherMapForecastClient()
