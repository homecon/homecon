#!/usr/bin/python3
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of KNXControl.
#
#    KNXControl is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KNXControl is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################


# function to load current weather data when measurements are not available

import urllib.request
import json

response = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s' % (sh._lat,sh._lon))
response = json.loads(response.read().decode('utf-8'))


if sh.knxcontrol.weather.current.temperature.conf['sh_listen'] == '':
	sh.knxcontrol.weather.current.temperature( response['main']['temp']-273.15 )

if sh.knxcontrol.weather.current.humidity.conf['sh_listen'] == '':
	sh.knxcontrol.weather.current.humidity( response['main']['humidity']-273.15 )

if sh.knxcontrol.weather.current.irradiation.sensor.conf['sh_listen'] == '':
	sh.knxcontrol.weather.current.irradiation.clouds( response['clouds']['all'] )

if sh.knxcontrol.weather.current.precipitation.conf['sh_listen'] == '':
	if 'rain' in response:
		sh.knxcontrol.weather.current.precipitation( response['rain']['3h'] )
	else:
		sh.knxcontrol.weather.current.precipitation( 0 )

if sh.knxcontrol.weather.current.irradiation.sensor.conf['sh_listen'] == '':
	sh.knxcontrol.weather.current.irradiation.clouds( response['clouds']['all'] )

if sh.knxcontrol.weather.current.wind.speed.conf['sh_listen'] == '':
	sh.knxcontrol.weather.current.wind.speed( response['wind']['speed'] )

if sh.knxcontrol.weather.current.wind.direction.conf['sh_listen'] == '':
	sh.knxcontrol.weather.current.wind.direction( response['wind']['deg'] )

logger.info('Current weather loaded')

