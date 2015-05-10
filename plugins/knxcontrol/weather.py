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
import numpy as np

logger = logging.getLogger('')

class Weather:

	def __init__(self,smarthome):
		self._sh = smarthome
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
			item = self._sh.return_item('knxcontrol.weather.prediction.detailed')
			item(weatherforecast)
			
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
			item = self._sh.return_item('knxcontrol.weather.prediction.daily')
			item(weatherforecast)
			
			logger.warning('Daily weatherforecast loaded')
		except:
			logger.warning('Error loading daily weatherforecast')
	


	def update_irradiation(self):
		"""
		Function calculates the total horizontal irradiation, cloud coverage and zone irradiation
		based on the sensor measurement, predictions or theoretical depending on which data is available
		"""
		
		utcdate = datetime.datetime.utcnow()
		(solar_azimuth,solar_altitude) = self._sh.energytools.sunposition(utcdate)
		(I_b_clearsky,I_d_clearsky) = self._sh.energytools.clearskyirrradiation(utcdate)

		if hasattr(self._sh.knxcontrol.weather.current.irradiation, 'sensor'):
			# use the sensor to determine the cloud coverage
			sensor_orientation = float(self._sh.knxcontrol.weather.current.irradiation.sensor.conf['orientation'])*np.pi/180
			sensor_tilt = float(self._sh.knxcontrol.weather.current.irradiation.sensor.conf['tilt'])*np.pi/180


			I_sensor_clearsky = self._sh.energytools.incidentradiation(I_b_clearsky,I_d_clearsky,solar_azimuth,solar_altitude,sensor_orientation,sensor_tilt)

			if I_sensor_clearsky > 0:
				clouds = 1-min(1, self._sh.knxcontrol.weather.current.irradiation.sensor() / I_sensor_clearsky )
			else:
				clouds = 0
		else:
			try:
				# use the predictions to determine the cloud coverage
				prediction = self._sh.knxcontrol.weather.prediction.detailed()
				clouds = prediction[0]['clouds']
			except:
				# assume no cloud coverage
				clouds = 0

		self._sh.knxcontrol.weather.current.irradiation.clouds(clouds)
		self._sh.knxcontrol.weather.current.irradiation.horizontal((1-clouds)*self._sh.energytools.incidentradiation(I_b_clearsky,I_d_clearsky,solar_azimuth,solar_altitude,0,0))
		

		# calculate the zone irradiation
		for zone in self._sh.knxcontrol.building:
			zone_str  = zone.id().split('.')
			zone_str = zone_str[-1]

			irradiation = 0.0

			for room in self._sh.find_items('zone'):
				if room.conf['zone'] == zone_str:

					if hasattr(room,'windows'):
						for window in room.windows.return_children():
							window_orientation = float(window.conf['orientation'])*np.pi/180
							window_tilt = float(window.conf['tilt'])*np.pi/180
							window_area = float(window.conf['area'])
							window_transmittance = float(window.conf['transmittance'])
							I_window_clearsky = window_transmittance*self._sh.energytools.incidentradiation(I_b_clearsky,I_d_clearsky,solar_azimuth,solar_altitude,window_orientation,window_tilt)
							
							
							if hasattr(window,'shading'):
								shading = window.shading
								shading_open_value = 0.0
								shading_closed_value = 255.0
								shading_pos = (shading.value()-shading_open_value)/(shading_closed_value-shading_open_value)
								shading_trans = float(shading.conf['transmittance'])
								shading = shading_pos - shading_pos*shading_trans
							else:
								shading = 0.0
							irradiation += window_area*(1-clouds)*(1-shading)*I_window_clearsky

			zone.irradiation.power(irradiation)


