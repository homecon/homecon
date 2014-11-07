//////////////////////////////////////////////////////////////////////////////
// initialize forecast
//////////////////////////////////////////////////////////////////////////////

var icons = {	'01d': 'sun_1.png',
				'02d': 'sun_3.png',
				'03d': 'cloud_4.png',
				'04d': 'cloud_5.png',
				'09d': 'cloud_7.png',
				'10d': 'sun_7.png' ,
				'11d': 'cloud_10.png',
				'13d': 'cloud_13.png',
				'50d': 'sun_6.png',
				'01n': 'moon_1.png',
				'02n': 'moon_3.png',
				'03n': 'cloud_4.png',
				'04n': 'cloud_5.png',
				'09n': 'cloud_7.png',
				'10n': 'moon_7.png',
				'11n': 'cloud_10.png',
				'13n': 'cloud_13.png',
				'50n': 'moon_6.png'
			};

				  
$(document).on('pagebeforecreate',function(){

	var lat=51;
	var lon=5;

	// load forecast
	$.post('http://api.openweathermap.org/data/2.5/forecast?lat='+lat+'&lon='+lon,function(result){
		
		var forecast = [];
				
		
		if($('#weather_forecast').length == 1){
		
			// get detailed forecast and display if required
			for(var i=0;i<result.list.length; i++){
				data = result.list[i];
				var temp = {
					timestamp: data.dt*1000,
					temperature: data.main.temp-273.15,
					minimum_temperature: data.main.temp_min-273.15,
					maximum_temperature: data.main.temp_max-273.15,
					pressure: data.main.pressure,
					humidity: data.main.humidity,
					windspeed: data.wind.speed,
					winddirection: data.wind.deg,
					cloudfactor: 1-data.clouds.all/100,
					precipitation: 0,
					icon: icons[ data.weather.icon ]
				};
		
				if(data.hasOwnProperty('rain')){
					temp.precipitation= data.rain['3h']/3;
				}
				forecast.push(temp);
			}
		
			// create a arrays for chart
			var temperature = [];
			var cloudfactor = [];
			for(var i=0;i<forecast.length; i++){
				temperature.push([forecast[i].timestamp,forecast[i].temperature]);
				cloudfactor.push([forecast[i].timestamp,forecast[i].cloudfactor*100]);
			}
			alert(cloudfactor);
			
			
			// create the chart
			var options = {
				chart: {
					renderTo: 'weather_chart_container',
					type: 'line'
				},
				title: {
					text: 'forecast'
				},
				xAxis: {
					type: 'datetime'
				},
				yAxis:	[{ // Primary yAxis
					labels: {
						format: '{value}°C',
						style: {
							color: Highcharts.getOptions().colors[0]
						}
					},
					title: {
						text: 'Temperature',
						style: {
							color: Highcharts.getOptions().colors[0]
						}
					},
					opposite: false
				}, { // Secondary yAxis
					labels: {
						format: '{value} %',
						style: {
							color: Highcharts.getOptions().colors[1]
						}
					},
					title: {
						text: 'Cloudfactor',
						style: {
							color: Highcharts.getOptions().colors[1]
						}
					},
					opposite: true
				}],
				tooltip: {
					xDateFormat: '%Y-%m-%d %H:%M',
					valueDecimals: 1,
					shared: true
				},
				rangeSelector : {
					enabled: false
				},
				series: [{
						name: 'temperature',
						data: temperature
				},{
						name: 'cloudfactor',
						yAxis: 1,
						data: cloudfactor
				}]
			}
			
			// tell highcharts to convert utc time to local time
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			
			var weatherchart = new Highcharts.Chart(options);
			
		// get averaged forecast and display if required
		}

		
		
		
		
     
	 
	 
	 
	 
	});
});