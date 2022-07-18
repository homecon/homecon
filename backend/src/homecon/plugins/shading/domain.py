import logging
from datetime import datetime
from typing import Optional, Callable

from homecon.util.weather import sunposition, clearskyirrradiance, cloudyskyirrradiance, incidentirradiance

logger = logging.getLogger(__name__)


class IShading:
    """
    position: 0 means fully open, maximum solar gains, 1 means fully closed, minimum solar gains
    """

    @property
    def position(self) -> float:
        raise NotImplementedError

    def set_position(self, value) -> None:
        raise NotImplementedError

    @property
    def minimum_position(self) -> float:
        raise NotImplementedError

    @property
    def maximum_position(self) -> float:
        raise NotImplementedError

    def get_heat_gain(self, position: float, date: datetime, cloud_cover: Optional[float] = 0.0) -> float:
        raise NotImplementedError


class StateBasedShading(IShading):
    """
    position: 0 means fully open, 1 means fully closed
    """

    def __init__(self, name: str, position: float, set_position: Callable[[float], None],
                 minimum_position: Optional[float] = None,
                 maximum_position: Optional[float] = None,
                 controller_override: Optional[bool] = False,
                 area: float = 1., transparency: float = 0., azimuth: float = 180., tilt: float = 90.,
                 longitude: float = 0, latitude: float = 0, elevation: float = 80.):
        self._name = name
        self._position = position
        self._set_position = set_position
        self._controller_override = controller_override
        self._minimum_position = position if controller_override else minimum_position
        self._maximum_position = position if controller_override else maximum_position
        self._area = area
        self.transparency = transparency
        self._azimuth = azimuth
        self._tilt = tilt
        self._longitude = longitude
        self._latitude = latitude
        self._elevation = elevation

    def get_shading_factor(self, position):
        return position * self.transparency + (1 - position) * 1

    def get_heat_gain(self, position: float, date: datetime, cloud_cover: Optional[float] = 0.0) -> float:
        return self.get_shading_factor(position) * self.get_maximum_heat_gain(date, cloud_cover)

    def get_maximum_heat_gain(self, date: datetime, cloud_cover: Optional[float] = 0.0) -> float:
        solar_azimuth, solar_altitude = sunposition(self._latitude, self._longitude, self._elevation,
                                                    timestamp=int(date.timestamp()))
        irradiance_direct_clearsky, irradiance_diffuse_clearsky = clearskyirrradiance(solar_azimuth, solar_altitude)

        irradiance_direct, irradiance_diffuse = cloudyskyirrradiance(
            irradiance_direct_clearsky, irradiance_diffuse_clearsky, cloud_cover, solar_azimuth, solar_altitude,
            timestamp=int(date.timestamp()))
        irradiance_total_surface, irradiance_direct_surface, irradiance_diffuse_surface, irradiance_ground_surface = \
            incidentirradiance(
                irradiance_direct, irradiance_diffuse, solar_azimuth, solar_altitude, self._azimuth, self._tilt)

        return irradiance_total_surface * self._area

    @property
    def minimum_position(self) -> float:
        return self._minimum_position or 0

    @property
    def maximum_position(self) -> float:
        return self._maximum_position or 1

    @property
    def position(self) -> float:
        return self._position

    def set_position(self, value) -> None:
        if not self._controller_override:
            self._set_position(value)
        else:
            logger.debug('override active, not setting position')

    def __repr__(self):
        return f'<StateBasedShading {self._name}>'
