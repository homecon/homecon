import logging
import requests
import json
import time

from datetime import datetime
from typing import List
from dataclasses import asdict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor


from homecon.core.plugins.plugin import IPlugin
from homecon.core.event import Event
from homecon.core.states.state import IStateManager, StateEventsTypes
from homecon.plugins.weather.weather import ForecastClient, Forecast, DailyForecast, NoForecastAvailableException


logger = logging.getLogger(__name__)


class IOpenWeatherMapApiClient:
    def get_forecast(self, api_key: str, longitude: float, latitude: float) -> dict:
        raise NotImplementedError


class OpenWeatherMapApiClient(IOpenWeatherMapApiClient):
    ONE_CALL_URL = 'https://api.openweathermap.org/data/2.5/onecall'

    def get_forecast(self, api_key: str, longitude: float, latitude: float) -> dict:
        url = f'{self.ONE_CALL_URL}?appid={api_key}&lat={latitude}&lon={longitude}&exclude=minutely,alerts&units=metric'
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.text)


class OpenWeatherMapForecastClient(ForecastClient):
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

    def __init__(self, api_client: IOpenWeatherMapApiClient, api_key: str, longitude: float, latitude: float):
        self._api_client = api_client
        self._api_key = api_key
        self._longitude = longitude
        self._latitude = latitude

    def get_forecast(self) -> (List[DailyForecast], List[Forecast]):
        """
        Loads a forecast from openweathermap.net
        """

        try:
            forecast = self._api_client.get_forecast(self._api_key, self._longitude, self._latitude)
        except Exception as e:
            raise NoForecastAvailableException from e
        else:
            forecast_hourly = []
            for hourly in forecast['hourly']:
                forecast_hourly.append(
                    Forecast(
                        timestamp=hourly['dt'],
                        temperature=hourly['temp'],
                        pressure=hourly['pressure'],
                        relative_humidity=hourly['humidity'],
                        dew_point=hourly['dew_point'],
                        cloud_cover=hourly['clouds']/100,
                        wind_speed=hourly['wind_speed'],
                        wind_direction=hourly['wind_deg'],
                        icon=self.ICON_MAP.get(hourly['weather'][0]['icon'], 'blank'),
                        rain=hourly.get('rain', {}).get('1h', 0),
                    )
                )

            forecast_daily = []
            for daily in forecast['daily']:
                forecast_daily.append(
                    DailyForecast(
                        timestamp=daily['dt'],
                        temperature_min=daily['temp']['min'],
                        temperature_max=daily['temp']['max'],
                        pressure=daily['pressure'],
                        relative_humidity=daily['humidity'],
                        dew_point=daily['dew_point'],
                        cloud_cover=daily['clouds']/100,
                        wind_speed=daily['wind_speed'],
                        wind_direction=daily['wind_deg'],
                        icon=self.ICON_MAP.get(daily['weather'][0]['icon'], 'blank'),
                        rain=daily.get('rain', 0)
                    )
                )

            return forecast_daily, forecast_hourly


class OpenWeatherMap(IPlugin):
    BASE_STATE = 'openweathermap'
    API_KEY_STATE = 'api_key'

    def __init__(self, state_manager: IStateManager, interval=7200):
        self._state_manager = state_manager

        openweathermap = self._state_manager.add(self.BASE_STATE, parent=None)
        self._state_manager.add(self.API_KEY_STATE, parent=openweathermap, type='str')

        executors = {
            'default': ThreadPoolExecutor(5),
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 3,
            'misfire_grace_time': 3600
        }
        self._interval = interval
        self._scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
        self._scheduler.add_job(self._get_forecast, trigger='interval', seconds=self._interval)

    @property
    def name(self):
        return 'openweathermap'

    def start(self):
        self._scheduler.start()
        logger.info('OpenWeatherMap plugin Initialized')

    def stop(self):
        self._scheduler.shutdown(wait=False)

    def handle_event(self, event: Event):
        if event.type == StateEventsTypes.STATE_VALUE_CHANGED or event.type == StateEventsTypes.STATE_UPDATED:
            if event.data['state'].path == f'/{self.BASE_STATE}/{self.API_KEY_STATE}':
                logger.info('api key updated, getting forecasts')
                self._get_forecast()

    def _get_forecast(self):
        last_update = self._state_manager.get(path=f'/weather/forecast/last_update')

        if last_update.value < time.time() - 0.9 * self._interval:
            api_key = self._state_manager.get(path=f'/{self.BASE_STATE}/{self.API_KEY_STATE}').value
            if api_key is not None and api_key != '':
                longitude = self._state_manager.get(path='/settings/location/longitude').value
                latitude = self._state_manager.get(path='/settings/location/latitude').value

                client = OpenWeatherMapForecastClient(OpenWeatherMapApiClient(), api_key, longitude, latitude)
                try:
                    daily_forecasts, hourly_forecasts = client.get_forecast()
                except NoForecastAvailableException:
                    logger.exception('no forecast available')
                else:
                    for i, forecast in enumerate(daily_forecasts):
                        state = self._state_manager.get(path=f'/weather/forecast/daily/{i}')
                        if state is not None:
                            state.set_value(asdict(forecast), source=self.name)

                    for i, forecast in enumerate(hourly_forecasts):
                        state = self._state_manager.get(path=f'/weather/forecast/hourly/{i}')
                        if state is not None:
                            state.set_value(asdict(forecast), source=self.name)

                    last_update.set_value(int(time.time()), source=self.name)
        else:
            logger.debug('last update was not long ago, not updating forecasts to avoid api flooding')
