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
import lib.item

logger = logging.getLogger('')

#########################################################################
# WeatherItem
#########################################################################
class KNXControlItem(lib.item.Item):
	def update_irradiation(self):
		"""
		Update all values dependent on the solar irradiation
		"""
		for zone in self._sh.find_items('zonetype'):
			zone.irradiation_est()

	def control(self):
		"""
		Execute control actions
		"""

		# optimization	


		# set controls
		self.shading_control()

	def shading_control(self):
		for zone in self._sh.find_items('zonetype'):
			zone.irradiation.setpoint(5000)
			zone.emission.setpoint(5000)
			zone.shading_control()




#########################################################################
# WeatherItem
#########################################################################
class WeatherItem(lib.item.Item):

	def update_irradiation(self):
		"""
		Function calculates the total horizontal irradiation, cloud coverage and zone irradiation
		based on the sensor measurement, predictions or theoretical depending on which data is available
		is called every minute
		"""

		self.set_solarproperties()

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

		# update dependent objects
		self._sh.knxcontrol.update_irradiation()


	def set_solarproperties(self):
		"""
		Sets the solar azimuth and altitude and beam and diffuse clearsky irradiation as object properties
		"""
		utcdate = datetime.datetime.utcnow()
		(self.solar_azimuth,self.solar_altitude) = self._sh.energytools.sunposition(utcdate)
		(self.I_b_clearsky,self.I_d_clearsky) = self._sh.energytools.clearskyirrradiation(utcdate)

	def incidentradiation(self,orientation,tilt,average=False):
		"""
		Calculates the current or averaged incident solar irradiation on a surface
		Arguments:		
		orientation: surface orientation in degrees
		tilt: surface tilt in degrees 
		"""

		if average and len(self.current.irradiation.clouds.arr)>0: 
			clouds = sum(self.current.irradiation.clouds.arr)/len(self.current.irradiation.clouds.arr)	
		else:
			clouds = self.current.irradiation.clouds()

		return (1-clouds)*self._sh.energytools.incidentradiation(self.I_b_clearsky,self.I_d_clearsky,self.solar_azimuth,self.solar_altitude,orientation*np.pi/180,tilt*np.pi/180)
	

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


#########################################################################
# ZoneItem
#########################################################################
class ZoneItem(lib.item.Item):
	def find_windows(self):
		windows = []
		for room in self.return_children():
			if hasattr(room,'windows'):
				for window in room.windows.return_children():
					windows.append(window)

		return windows

	def irradiation_max(self,average=False):
		"""
		calculates the maximum zone irradiation
		will be bound to all zone items
		"""
		return sum([window.irradiation_max(average=average) for window in self.find_windows()])


	def irradiation_min(self,average=False):
		"""
		calculates the minimum zone irradiation
		will be bound to all zone items
		"""
		return sum([window.irradiation_min(average=average) for window in self.find_windows()])	

	def irradiation_est(self,average=False):
		"""
		calculates the estimated zone irradiation and sets it to the appropriate item
		will be bound to all zone items
		"""
		value = sum([window.irradiation_est(average=average) for window in self.find_windows()])

		 # set the irradiation item
		self.irradiation( value )
		return value


	def shading_control(self):
		"""
		Function tries to control the shading so the actual solar gains to the zone match the setpoint
		"""
		logger.warning('automatic shading control for zone: '+ self.id())
		irradiation_set = 0 #self.item.irradiation.setpoint()

		# close shadings until the setpoint is reached
		# try to keep as many shadings completely open, to maintain view through the windows
		# so start with the windows with the highest difference between max and min
		# create an array of irradiation difference for all windows


		differ = [w.irradiation_max(average=True)-w.irradiation_min(average=True) for w in self.find_windows()]
		windows = sorted(self.find_windows(), key=lambda w: w.irradiation_max(average=True)-w.irradiation_min(average=True), reverse=True)

		# get old shading positions
		newpos = []
		oldpos = []
		for window in windows:
			if hasattr(window,'shading'):
				newpos.append(0)
				oldpos.append( (window.shading.value()-float(window.shading.conf['open_value']))/(float(window.shading.conf['closed_value'])-float(window.shading.conf['open_value'])) )
			else:
				newpos.append(-1)
				oldpos.append(-1)

		# calculate new shading positions
		for idx,window in enumerate(windows):
			oldirradiation = sum( [w.irradiation_max(average=True)*(1-p)+w.irradiation_min(average=True)*p for w,p in zip(windows,newpos)] )
		
			if oldirradiation <= irradiation_set:
				break

			if hasattr(window,'shading'):
				if window.shading.closed():
					newpos[idx] = 1 
				elif window.shading.override() or not window.shading.auto():
					newpos[idx] = (window.shading.value()-float(window.shading.conf['open_value']))/(float(window.shading.conf['closed_value'])-float(window.shading.conf['open_value']))
				elif self._sh.knxcontrol.weather.current.precipitation() and ('open_when_raining' in window.shading.conf):
					newpos[idx] = 0
				else:
					newpos[idx] = 1
					newirradiation = sum([w.irradiation_max(average=True)*(1-p)+w.irradiation_min(average=True)*(p) for w,p in zip(windows,newpos)])
					newpos[idx] = min(1,max(0,(irradiation_set - oldirradiation)/(newirradiation - oldirradiation)))

		# set all shading positions
		logger.warning(newpos)
		for idx,window in enumerate(windows):
			if hasattr(window,'shading'):
				if not window.shading.override():
					if abs( newpos[idx]-oldpos[idx]) > 0.1 or newpos[idx]==float(window.shading.conf['closed_value']) or newpos[idx]==float(window.shading.conf['open_value']):
						# only actually set the shading position if the change is larger than 10% or it is closed or open
						window.shading.value( float(window.shading.conf['open_value'])+newpos[idx]*(float(window.shading.conf['closed_value'])-float(window.shading.conf['open_value'])) )

#########################################################################
# window item methods
#########################################################################
class WindowItem(lib.item.Item):
	def irradiation_open(self,average=False):
		"""
		Returns the irradiation through a window when the shading is open
		"""

		return float(self.conf['area'])*float(self.conf['transmittance'])*self._sh.knxcontrol.weather.incidentradiation(float(self.conf['orientation'])*np.pi/180,float(self.conf['tilt'])*np.pi/180,average=average)


	def irradiation_closed(self,average=False):
		"""
		Returns the irradiation through a window when the shading is closed if there is shading
		"""
		if hasattr(self,'shading'):
			shading = float(self.shading.conf['transmittance'])
		else:
			shading = 1.0
		return self.irradiation_open(average=average)*shading

	def irradiation_max(self,average=False):
		"""
		Returns the maximum amount of irradiation through the window
		It checks the closed flag indicating the shading must be closed
		And the override flag indicating the shading position is fixed
		"""

		if hasattr(self,'shading'):
			if self.shading.closed():
				return self.irradiation_closed(average=average)
			elif self.shading.override() or not self.shading.auto():
				return self.irradiation_est(average=average)
			else:
				return self.irradiation_open(average=average)
		else:
			return self.irradiation_open(average=average)

	def irradiation_min(self,average=False):
		"""
		Returns the minimum amount of irradiation through the window
		It checks the closed flag indicating the shading must be closed
		And the override flag indicating the shading position is fixed
		"""
		if hasattr(self,'shading'):
			if self.shading.override() or not self.shading.auto():
				return self.irradiation_est(average=average)
			else:
				return self.irradiation_closed(average=average)
		else:
			return self.irradiation_open(average=average)

	def irradiation_est(self,average=False):
		"""
		Returns the estimated actual irradiation through the window
		"""
		if hasattr(self,'shading'):
			shading = (self.shading.value()-float(self.shading.conf['open_value']))/(float(self.shading.conf['closed_value'])-float(self.shading.conf['open_value']))
			return self.irradiation_open(average=average)*(1-shading) + self.irradiation_closed(average=average)*shading
		else:
			return self.irradiation_open(average=average)



