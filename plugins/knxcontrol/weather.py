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

class Weather:

	def __init__(self,knxcontrol):
		self.knxcontrol = knxcontrol 
		self._sh = knxcontrol._sh

		self.prediction_detailed = None
		self.prediction_daily = None
		self.olar_azimuth = None
		self.solar_altitude = None
		self.I_b_clearsky = 0
		self.I_d_clearsky = 0
		self.clouds = 0
		self.clouds_array = []


		logger.warning('Weather initialized')
		self.load_detailed_predictions()
		self.load_daily_predictions()
	
	
	def load_detailed_predictions(self):
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
			
			self.prediction_detailed = weatherforecast;

			# set the smarthome item
			self._sh.knxcontrol.weather.prediction.detailed(weatherforecast)
			
			logger.warning('Detailed weatherforecast loaded')
		except:
			logger.warning('Error loading detailed weatherforecast')
	

	def load_daily_predictions(self):
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

			self.prediction_daily = weatherforecast;
			
			# set the smarthome item
			self._sh.knxcontrol.weather.prediction.daily(weatherforecast)
			
			logger.warning('Daily weatherforecast loaded')
		except:
			logger.warning('Error loading daily weatherforecast')


	def update_irradiation(self):
		"""
		Function calculates the total horizontal irradiation, cloud coverage and zone irradiation
		based on the sensor measurement, predictions or theoretical depending on which data is available
		is called every minute
		"""
		
		utcdate = datetime.datetime.utcnow()
		(self.solar_azimuth,self.solar_altitude) = self._sh.energytools.sunposition(utcdate)
		(self.I_b_clearsky,self.I_d_clearsky) = self._sh.energytools.clearskyirrradiation(utcdate)


		if hasattr(self._sh.knxcontrol.weather.current.irradiation, 'sensor'):
			# use the sensor to determine the cloud coverage
			sensor_orientation = float(self._sh.knxcontrol.weather.current.irradiation.sensor.conf['orientation'])*np.pi/180
			sensor_tilt = float(self._sh.knxcontrol.weather.current.irradiation.sensor.conf['tilt'])*np.pi/180


			I_sensor_clearsky = self._sh.energytools.incidentradiation(self.I_b_clearsky,self.I_d_clearsky,self.solar_azimuth,self.solar_altitude,sensor_orientation,sensor_tilt)

			if I_sensor_clearsky > 0:
				self.clouds = 1-min(1, self._sh.knxcontrol.weather.current.irradiation.sensor() / I_sensor_clearsky )
			else:
				self.clouds = 0
		else:
			try:
				# use the predictions to determine the cloud coverage
				prediction = self._sh.knxcontrol.weather.prediction.detailed()
				self.clouds = prediction[0]['clouds']
			except:
				# assume no cloud coverage
				self.clouds = 0

			
		if len(self.clouds_array) >= 60:
			self.clouds_array.pop(0)
		self.clouds_array.append(self.clouds)	
			
		# set items
		self._sh.knxcontrol.weather.current.irradiation.clouds(self.clouds)
		self._sh.knxcontrol.weather.current.irradiation.horizontal((1-self.clouds)*self._sh.energytools.incidentradiation(self.I_b_clearsky,self.I_d_clearsky,self.solar_azimuth,self.solar_altitude,0,0))
		
		# update dependant objects
		self.knxcontrol.building.update_irradiation()


	def incidentradiation(self,orientation,tilt,average=False):
		if average and len(clouds_array)>0: 
			clouds = sum(self.clouds_array)/len(clouds_array)	
		else:
			clouds = self.clouds

		return (1-clouds)*self._sh.energytools.incidentradiation(self.I_b_clearsky,self.I_d_clearsky,self.solar_azimuth,self.solar_altitude,orientation,tilt)
		

