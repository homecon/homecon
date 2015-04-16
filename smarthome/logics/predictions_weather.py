###########################################################################
# load weatherforecast
###########################################################################
# function to load a weather forecast to smarthome.py

import urllib.request
import json

# detailed predictions
weatherforecast = []

response = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?lat=%s&lon=%s' % (sh._lat,sh._lon))
response = json.loads(response.read().decode('utf-8'))

for forecast in response['list']:
	currentforecast = {'datetime': forecast['dt']}
	currentforecast['temperature'] = forecast['main']['temp']-273.15
	currentforecast['pressure'] = forecast['main']['pressure']
	currentforecast['humidity'] = forecast['main']['humidity']
	currentforecast['icon'] = forecast['weather'][0]['icon']
	currentforecast['cloudfactor'] = forecast['clouds']['all']
	currentforecast['wind_speed'] = forecast['wind']['speed']
	currentforecast['wind_directions'] = forecast['wind']['deg']
	if 'rain' in forecast:
		currentforecast['rain'] = forecast['rain']['3h']
	else:
		currentforecast['rain'] = 0
		
	weatherforecast.append(currentforecast)

sh.knxcontrol.weather.predictions.detailed(weatherforecast)


# daily predictions
weatherforecast = []

response = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast/daily?lat=%s&lon=%s' % (sh._lat,sh._lon))
response = json.loads(response.read().decode('utf-8'))

for forecast in response['list']:
	currentforecast = {'datetime': forecast['dt']}
	currentforecast['temperature_day'] = forecast['temp']['day']-273.15
	currentforecast['temperature_night'] = forecast['temp']['night']-273.15
	currentforecast['pressure'] = forecast['pressure']
	currentforecast['humidity'] = forecast['humidity']
	currentforecast['icon'] = forecast['weather'][0]['icon']
	currentforecast['cloudfactor'] = forecast['clouds']
	currentforecast['wind_speed'] = forecast['speed']
	currentforecast['wind_directions'] = forecast['deg']
	if 'rain' in forecast:
		currentforecast['rain'] = forecast['rain']
	else:
		currentforecast['rain'] = 0
		
	weatherforecast.append(currentforecast)

sh.knxcontrol.weather.predictions.daily(weatherforecast)



logger.info('Weather forecast loaded')
