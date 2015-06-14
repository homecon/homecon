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
# Weather
#########################################################################
class Weather():
	def __init__(self,knxcontrol):
		self.knxcontrol = knxcontrol
		
		# find weather item
		items = self.knxcontrol.find_item('weather')
		if len(items) == 0:
			self.item = None
			logger.warning('No weather item found')
		else:
			self.item = items[0]


		# find a irradiationsensor item
		items = self.knxcontrol.find_item('irradiationsensor')
		if len(items) == 0:
			self.irradiationsensor = None
		else:
			self.irradiationsensor = items[0]


		# find a clouds item
		items = self.knxcontrol.find_item('clouds')
		if len(items) == 0:
			self.clouds = None
		else:
			self.clouds = items[0]

		self.cloudsarraylength = 30
		self.cloudsarray = []


		# find a horizontal_irradiation item
		items = self.knxcontrol.find_item('horizontal_irradiation')
		if len(items) == 0:
			self.horizontal_irradiation = None
		else:
			self.horizontal_irradiation = items[0]

		
		# find prediction items
		items = self.knxcontrol.find_item('weatherforecast_detailed')
		if len(items) == 0:
			self.prediction_detailed = None
		else:
			self.prediction_detailed = items[0]

		items = self.knxcontrol.find_item('weatherforecast_daily')
		if len(items) == 0:
			self.prediction_daily = None
		else:
			self.prediction_daily = items[0]

		

		# create an ephem observer
		# http://rhodesmill.org/pyephem/quick.html
		self.obs = ephem.Observer()
		self.obs.lat = self.knxcontrol.lat*np.pi/180     #N+
		self.obs.lon = self.knxcontrol.lon*np.pi/180     #E+
		self.obs.elev = self.knxcontrol.elev

		# update the parent
		self.knxcontrol.weather = self

		logger.warning('Weather initialized')

	def update(self):
		"""
		Function calculates the total horizontal irradiation, cloud coverage and zone irradiation
		based on the sensor measurement, predictions or theoretical depending on which data is available
		is called every minute
		"""

		if self.irradiationsensor != None:
			# use the sensor to determine the cloud coverage
			sensor_orientation = float(self.irradiationsensor.conf['orientation'])*np.pi/180
			sensor_tilt = float(self.irradiationsensor.conf['tilt'])*np.pi/180

			I_sensor_clearsky = self.incidentradiation(clouds=0,surface_azimuth=sensor_orientation,surface_tilt=sensor_tilt)

			if I_sensor_clearsky > 0:
				clouds = 1-min(1, self.irradiationsensor() / I_sensor_clearsky )
			else:
				clouds = 0
		else:
			try:
				# use the predictions to determine the cloud coverage
				prediction = self.prediction_detailed()
				clouds = prediction[0]['clouds']
			except:
				# assume no cloud coverage
				clouds = 0


		# set items
		self.clouds(clouds)
		self.horizontal_irradiation(self.incidentradiation(clouds=clouds,surface_azimuth=0,surface_tilt=0))
	
		# set cloudsarray
		if len(self.cloudsarray) >= self.cloudsarraylength:
			self.cloudsarray.pop(0)
		self.cloudsarray.append(clouds)


	def clearskyirrradiation(self,utcdate=datetime.datetime.utcnow()):
		"""
		Method returns the clear sky theoretical direct and diffuse solar irradiation
		according to ASHRAE
		"""
		
		(azi,alt) = self.sunposition(utcdate)

		# air mass between the observer and the sun
		if 6.07995 + alt > 0:
			m = 1/(np.sin(alt) + 0.50572*(6.07995 + alt)**-1.6364);
		else:
			m = 0
		
		# day of the year
		n = float(utcdate.strftime('%j'))

		# extraterrestrial solar radiation
		Esc = 1367 # solar constant
		E0 = Esc*(1 + 0.033*np.cos(2*np.pi*(n-3)/365))

		# optical depths
		tau_b = np.interp(n,np.cumsum([-10,31,31,28,31,30,31,30,31,31,30,31,30,31]),[0.320,0.325,0.349,0.383,0.395,0.448,0.505,0.556,0.593,0.431,0.373,0.339,0.320,0.325]);
		tau_d = np.interp(n,np.cumsum([-10,31,31,28,31,30,31,30,31,31,30,31,30,31]),[2.514,2.461,2.316,2.176,2.175,2.028,1.892,1.779,1.679,2.151,2.317,2.422,2.514,2.461]);
	   
		ab = 1.219 - 0.043*tau_b - 0.151*tau_d - 0.204*tau_b*tau_d; 
		ad = 0.202 + 0.852*tau_b - 0.007*tau_d -0.357*tau_b*tau_d;

		if np.degrees(alt) > 0:
			I_b = E0*np.exp(-tau_b*m**ab);
		else:
			I_b = 0
			
		if np.degrees(alt) > -2:	
			I_d = E0*np.exp(-tau_d*m**ad);
		else:
			I_d = 0

		return (I_b,I_d)

	def sunposition(self,utcdate=datetime.datetime.utcnow()):
		"""
		Method returns the sun azimuth and altitude at a certain utcdate
		at the location specified in smarthome.conf
		Output is in radians
		"""
		
		obs = self.obs
		obs.date = utcdate

		sun = ephem.Sun(obs)
		sun.compute(obs)
		
		return (sun.az,sun.alt)

	def incidentradiation(self,utcdate=None,clouds=None,average=False,surface_azimuth=0,surface_tilt=np.pi/2):
		"""
		Method returns irradiation on a surface 
		according to ASHRAE
		
		input:
		I_b: local beam irradiation (W/m2)
		I_d: local diffuse irradiation (W/m2)
		solar_azimuth:   sun azimuth angle from N in E direction (0=N, pi/2=E, pi=S, -pi/2 = W) (radians)
		solar_altitude:  sun altitude angle (radians)
		surface_azimuth: surface normal azimuth angle from N in E direction (0=N, pi/2=E, pi=S, -pi/2 = W) (radians)
		surface_tilt:    surface tilt angle (0: facing up, pi/2: vertical, pi: facing down) (radians)
		
		output:
		I: irradiation (W/m2)
		"""
		if utcdate==None:
			utcdate = datetime.datetime.now()

		if clouds==None:
			if average:
				clouds = mean(self.cloudsarray)
			else:
				clouds = self.clouds()

		
		(solar_azimuth,solar_altitude) = self.sunposition(utcdate)
		(I_b,I_d) = self.clearskyirrradiation(utcdate)

		# surface solar azimuth (-pi/2< gamma < pi/2, else surface is in shade)
		gamma = solar_azimuth-surface_azimuth;
		
		# incidence
		cos_theta = np.cos(solar_altitude)*np.cos(gamma)*np.sin(surface_tilt) + np.sin(solar_altitude)*np.cos(surface_tilt)
    
		# beam irradiation
		if cos_theta > 0:
			I_tb = I_b*cos_theta
		else:
			I_tb = 0
		
		# diffuse irradiation
		Y = max(0.45, 0.55 + 0.437*cos_theta+ 0.313*cos_theta**2)
		if surface_tilt < np.pi/2:
			I_td = I_d*(Y*np.sin(surface_tilt) + np.cos(surface_tilt))
		else:
			I_td = I_d*Y*np.sin(surface_tilt)
			
		# ground reflected radiation
		rho_g = 0.2;
		I_gr = (I_b*np.sin(solar_altitude) +I_d)*rho_g*(1-np.cos(surface_tilt))/2
		
		# total irradiation
		I_t = (I_tb + I_td + I_gr)*(1-clouds)
		
		return I_t



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
			self.prediction_detailed(weatherforecast)
		
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
			self.prediction_daily(weatherforecast)
		
			logger.warning('Daily weatherforecast loaded')
		except:
			logger.warning('Error loading daily weatherforecast')



#########################################################################
# Zone
#########################################################################
class Zone():
	def __init__(self,knxcontrol,item):
		self.knxcontrol = knxcontrol
		self.item = item


		self.windows = []
		self.emission = []

		for item in self.knxcontrol._sh.find_children(self.item, 'knxcontrolitem'):
			if item.conf['knxcontrolitem']== 'window':
				self.windows.append( Window(knxcontrol,self,item) )

		
		self.irradiation = self.item.irradiation
		self.emission = self.item.emission

	def irradiation_max(self,average=False):
		"""
		calculates the maximum zone irradiation
		will be bound to all zone items
		"""
		return sum([window.irradiation_max(average=average) for window in self.windows])


	def irradiation_min(self,average=False):
		"""
		calculates the minimum zone irradiation
		will be bound to all zone items
		"""
		return sum([window.irradiation_min(average=average) for window in self.windows])	

	def irradiation_est(self,average=False):
		"""
		calculates the estimated zone irradiation and sets it to the appropriate item
		will be bound to all zone items
		"""
		value = sum([window.irradiation_est(average=average) for window in self.windows])

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


		differ = [w.irradiation_max(average=True)-w.irradiation_min(average=True) for w in self.windows()]
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
				elif not window.shading.auto():
					newpos[idx] = 0
				elif self._sh.knxcontrol.weather.current.precipitation() and ('open_when_raining' in window.shading.conf):
					newpos[idx] = 0
				elif window.shading.override():
					newpos[idx] = (window.shading.value()-float(window.shading.conf['open_value']))/(float(window.shading.conf['closed_value'])-float(window.shading.conf['open_value']))
				else:
					newpos[idx] = 1
					newirradiation = sum([w.irradiation_max(average=True)*(1-p)+w.irradiation_min(average=True)*(p) for w,p in zip(windows,newpos)])
					newpos[idx] = min(1,max(0,(irradiation_set - oldirradiation)/(newirradiation - oldirradiation)))

		# set all shading positions
		for idx,window in enumerate(windows):
			if hasattr(window,'shading'):
				if not window.shading.override():
					if abs( newpos[idx]-oldpos[idx]) > 0.2 or newpos[idx]==0.0 or newpos[idx]==1.0:
						# only actually set the shading position if the change is larger than 20% or it is closed or open
						window.shading.value( float(window.shading.conf['open_value'])+newpos[idx]*(float(window.shading.conf['closed_value'])-float(window.shading.conf['open_value'])) )

#########################################################################
# Window
#########################################################################
class Window():
	def __init__(self,knxcontrol,zone,item):
		self.knxcontrol = knxcontrol
		self.zone = zone
		self.item = item

		self.shading = None
		for item in self.knxcontrol._sh.find_children(self.item, 'knxcontrolitem'):
			if item.conf['knxcontrolitem']== 'shading':
				self.shading = item


	def irradiation_open(self,average=False):
		"""
		Returns the irradiation through a window when the shading is open
		"""

		return float(self.item.conf['area'])*float(self.item.conf['transmittance'])*self.knxcontrol.weather.incidentradiation(surface_azimuth=float(self.item.conf['orientation'])*np.pi/180,surface_tilt=float(self.item.conf['tilt'])*np.pi/180,average=average)


	def irradiation_closed(self,average=False):
		"""
		Returns the irradiation through a window when the shading is closed if there is shading
		"""
		if self.shading != None:
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

		if self.shading != None:
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
		if self.shading != None:
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
		if self.shading != None:
			shading = (self.shading.value()-float(self.shading.conf['open_value']))/(float(self.shading.conf['closed_value'])-float(self.shading.conf['open_value']))
			return self.irradiation_open(average=average)*(1-shading) + self.irradiation_closed(average=average)*shading
		else:
			return self.irradiation_open(average=average)



