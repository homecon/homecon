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

import logging
import urllib.request
import json
import datetime
import ephem
import numpy as np

logger = logging.getLogger('')



def weather_update_irradiation(self):
	"""
	Function calculates the total horizontal irradiation, cloud coverage and zone irradiation
	based on the sensor measurement, predictions or theoretical depending on which data is available
	is called every minute
	"""

	self.set_irradiation()

	if hasattr(self.current.irradiation, 'sensor'):
		# use the sensor to determine the cloud coverage
		sensor_orientation = float(self.current.irradiation.sensor.conf['orientation'])*np.pi/180
		sensor_tilt = float(self.current.irradiation.sensor.conf['tilt'])*np.pi/180


		I_sensor_clearsky = self._sh.energytools.incidentradiation(self.I_b_clearsky,self.I_d_clearsky,self.solar_azimuth,self.solar_altitude,sensor_orientation,sensor_tilt)

		if I_sensor_clearsky > 0:
			clouds = 1-min(1, self.current.irradiation.sensor() / I_sensor_clearsky )
		else:
			clouds = 0
	else:
		try:
			# use the predictions to determine the cloud coverage
			prediction = self.prediction.detailed()
			clouds = prediction[0]['clouds']
		except:
			# assume no cloud coverage
			clouds = 0

	# set items
	self.current.irradiation.clouds(clouds)
	self.current.irradiation.horizontal((1-clouds)*self._sh.energytools.incidentradiation(self.I_b_clearsky,self.I_d_clearsky,self.solar_azimuth,self.solar_altitude,0,0))
	
	# set cloudsarray
	cloudsarraylen = 30
	if not hasattr(self.current.irradiation.clouds,'arr'):
		self.current.irradiation.clouds.arr = []

	if len(self.current.irradiation.clouds.arr) >= cloudsarraylen:
		self.current.irradiation.clouds.arr.pop(0)
	self.current.irradiation.clouds.arr.append(clouds)	
		
	# update dependant objects
	#self._sh.knxcontrol.building.update_irradiation()


def weather_set_irradiation(self):
	utcdate = datetime.datetime.utcnow()
	(self.solar_azimuth,self.solar_altitude) = self._sh.energytools.sunposition(utcdate)
	(self.I_b_clearsky,self.I_d_clearsky) = self._sh.energytools.clearskyirrradiation(utcdate)

def weather_incidentradiation(self,orientation,tilt,average=False):

	if average and len(self.current.irradiation.clouds.arr)>0: 
		clouds = sum(self.current.irradiation.clouds.arr)/len(self.current.irradiation.clouds.arr)	
	else:
		clouds = self.current.irradiation.clouds()

	return (1-clouds)*self._sh.energytools.incidentradiation(self.I_b_clearsky,self.I_d_clearsky,self.solar_azimuth,self.solar_altitude,orientation*np.pi/180,tilt*np.pi/180)
	




#########################################################################
# forecast item methods
#########################################################################
def prediction_detailed_load(self):
	"""
	method to load a detailed weather forecast from openweathermap.org and set write it to the appropriate item
	"""
	try:
		weatherforecast = []

		response = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?lat=%s&lon=%s' % (self._sh._lat,self._sh._lon))
		response = json.loads(response.read().decode('utf-8'))

		for forecast in response['list']:
			currentforecast = {'datetime': forecast['dt']}
			currentforecast['temperature'] = forecast['main']['temp']-273.15
			currentforecast['pressure'] = forecast['main']['pressure']
			currentforecast['humidity'] = forecast['main']['humidity']
			currentforecast['icon'] = forecast['weather'][0]['icon']
			currentforecast['clouds'] = forecast['clouds']['all']
			currentforecast['wind_speed'] = forecast['wind']['speed']
			currentforecast['wind_directions'] = forecast['wind']['deg']
			if 'rain' in forecast:
				currentforecast['rain'] = forecast['rain']['3h']
			else:
				currentforecast['rain'] = 0
				
			weatherforecast.append(currentforecast)
		
		# set the smarthome item
		self(weatherforecast)
		
		logger.warning('Detailed weatherforecast loaded')
	except:
		logger.warning('Error loading detailed weatherforecast')


def prediction_daily_load(self):
	"""
	method to load a daily weather forecast from openweathermap.org and set write it to the appropriate item
	"""
	
	try:
		weatherforecast = []
		response = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast/daily?lat=%s&lon=%s' % (self._sh._lat,self._sh._lon))
		response = json.loads(response.read().decode('utf-8'))

		for forecast in response['list']:
			currentforecast = {'datetime': forecast['dt']}
			currentforecast['temperature_day'] = forecast['temp']['day']-273.15
			currentforecast['temperature_night'] = forecast['temp']['night']-273.15
			currentforecast['pressure'] = forecast['pressure']
			currentforecast['humidity'] = forecast['humidity']
			currentforecast['icon'] = forecast['weather'][0]['icon']
			currentforecast['clouds'] = forecast['clouds']
			currentforecast['wind_speed'] = forecast['speed']
			currentforecast['wind_directions'] = forecast['deg']
			if 'rain' in forecast:
				currentforecast['rain'] = forecast['rain']
			else:
				currentforecast['rain'] = 0
				
			weatherforecast.append(currentforecast)
	
		# set the smarthome item
		self(weatherforecast)
		
		logger.warning('Daily weatherforecast loaded')
	except:
		logger.warning('Error loading daily weatherforecast')


