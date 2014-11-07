<?php

function weather_forecast($detailed = NULL){
	$forecast = 0;

	
	// icon translation array
	$icon = array('01d'=>'sun_1.png' ,'02d'=>'sun_3.png' ,'03d'=>'cloud_4.png','04d'=>'cloud_5.png','09d'=>'cloud_7.png','10d'=>'sun_7.png' ,'11d'=>'cloud_10.png','13d'=>'cloud_13.png','50d'=>'sun_6.png',
	              '01n'=>'moon_1.png','02n'=>'moon_3.png','03n'=>'cloud_4.png','04n'=>'cloud_5.png','09n'=>'cloud_7.png','10n'=>'moon_7.png','11n'=>'cloud_10.png','13n'=>'cloud_13.png','50n'=>'moon_6.png');

	// latitude and longitude should be loaded from smarthome or mysql in the future
	$lat = 51;
	$lon = 5;
	

	echo file_get_html('http://api.openweathermap.org/data/2.5/forecast?lat=51&lon=5');
	
	// load weather forecast from openweaterhmap
	// $weatherdata = json_decode('{"cod":"200","message":0.0168,"city":{"id":1851632,"name":"Shuzenji","coord":{"lon":138.933334,"lat":34.966671},"country":"JP","population":0},"cnt":27,"list":[{"dt":1415253600,"main":{"temp":292.16,"temp_min":287.023,"temp_max":292.16,"pressure":926.96,"sea_level":1022.96,"grnd_level":926.96,"humidity":75,"temp_kf":5.14},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":24},"wind":{"speed":0.79,"deg":43.0035},"sys":{"pod":"d"},"dt_txt":"2014-11-06 06:00:00"},{"dt":1415264400,"main":{"temp":285.98,"temp_min":281.102,"temp_max":285.98,"pressure":926.42,"sea_level":1022.24,"grnd_level":926.42,"humidity":96,"temp_kf":4.88},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":0.72,"deg":5.00027},"sys":{"pod":"n"},"dt_txt":"2014-11-06 09:00:00"},{"dt":1415275200,"main":{"temp":285.04,"temp_min":280.414,"temp_max":285.04,"pressure":925.88,"sea_level":1022.47,"grnd_level":925.88,"humidity":92,"temp_kf":4.62},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":1.4,"deg":333.003},"sys":{"pod":"n"},"dt_txt":"2014-11-06 12:00:00"},{"dt":1415286000,"main":{"temp":284.69,"temp_min":280.32,"temp_max":284.69,"pressure":926.55,"sea_level":1023.44,"grnd_level":926.55,"humidity":89,"temp_kf":4.37},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":36},"wind":{"speed":1.23,"deg":328.001},"sys":{"pod":"n"},"dt_txt":"2014-11-06 15:00:00"},{"dt":1415296800,"main":{"temp":283.98,"temp_min":279.875,"temp_max":283.98,"pressure":927.58,"sea_level":1024.84,"grnd_level":927.58,"humidity":84,"temp_kf":4.11},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":1.21,"deg":331.507},"sys":{"pod":"n"},"dt_txt":"2014-11-06 18:00:00"},{"dt":1415307600,"main":{"temp":281.14,"temp_min":277.287,"temp_max":281.14,"pressure":929.49,"sea_level":1027.23,"grnd_level":929.49,"humidity":94,"temp_kf":3.85},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"02n"}],"clouds":{"all":8},"wind":{"speed":1.06,"deg":319.502},"sys":{"pod":"n"},"dt_txt":"2014-11-06 21:00:00"},{"dt":1415318400,"main":{"temp":286.65,"temp_min":283.057,"temp_max":286.65,"pressure":932.18,"sea_level":1029.98,"grnd_level":932.18,"humidity":75,"temp_kf":3.6},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":12},"wind":{"speed":0.9,"deg":297.501},"sys":{"pod":"d"},"dt_txt":"2014-11-07 00:00:00"},{"dt":1415329200,"main":{"temp":290.99,"temp_min":287.649,"temp_max":290.99,"pressure":932.79,"sea_level":1029.94,"grnd_level":932.79,"humidity":74,"temp_kf":3.34},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03d"}],"clouds":{"all":44},"wind":{"speed":0.99,"deg":150.506},"sys":{"pod":"d"},"dt_txt":"2014-11-07 03:00:00"},{"dt":1415340000,"main":{"temp":288.7,"temp_min":285.622,"temp_max":288.7,"pressure":934.08,"sea_level":1031.19,"grnd_level":934.08,"humidity":89,"temp_kf":3.08},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":88},"wind":{"speed":0.98,"deg":151.502},"rain":{"3h":1},"sys":{"pod":"d"},"dt_txt":"2014-11-07 06:00:00"},{"dt":1415350800,"main":{"temp":286.73,"temp_min":283.909,"temp_max":286.73,"pressure":936.13,"sea_level":1034.05,"grnd_level":936.13,"humidity":100,"temp_kf":2.83},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.76,"deg":124.501},"rain":{"3h":3},"sys":{"pod":"n"},"dt_txt":"2014-11-07 09:00:00"},{"dt":1415361600,"main":{"temp":285.72,"temp_min":283.152,"temp_max":285.72,"pressure":938.01,"sea_level":1036.49,"grnd_level":938.01,"humidity":100,"temp_kf":2.57},"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.81,"deg":118.002},"rain":{"3h":5},"sys":{"pod":"n"},"dt_txt":"2014-11-07 12:00:00"},{"dt":1415372400,"main":{"temp":284.84,"temp_min":282.526,"temp_max":284.84,"pressure":939.24,"sea_level":1037.95,"grnd_level":939.24,"humidity":100,"temp_kf":2.31},"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.81,"deg":113.002},"rain":{"3h":4},"sys":{"pod":"n"},"dt_txt":"2014-11-07 15:00:00"},{"dt":1415383200,"main":{"temp":284.19,"temp_min":282.134,"temp_max":284.19,"pressure":939.92,"sea_level":1039.03,"grnd_level":939.92,"humidity":100,"temp_kf":2.05},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.76,"deg":81.5067},"rain":{"3h":3},"sys":{"pod":"n"},"dt_txt":"2014-11-07 18:00:00"},{"dt":1415394000,"main":{"temp":283.29,"temp_min":281.49,"temp_max":283.29,"pressure":940.68,"sea_level":1040.2,"grnd_level":940.68,"humidity":100,"temp_kf":1.8},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.82,"deg":40.0031},"rain":{"3h":2},"sys":{"pod":"n"},"dt_txt":"2014-11-07 21:00:00"},{"dt":1415404800,"main":{"temp":282.8,"temp_min":281.255,"temp_max":282.8,"pressure":942.27,"sea_level":1041.68,"grnd_level":942.27,"humidity":100,"temp_kf":1.54},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":92},"wind":{"speed":0.82,"deg":38.0018},"rain":{"3h":1},"sys":{"pod":"d"},"dt_txt":"2014-11-08 00:00:00"},{"dt":1415415600,"main":{"temp":282.99,"temp_min":281.709,"temp_max":282.99,"pressure":941.51,"sea_level":1040.42,"grnd_level":941.51,"humidity":100,"temp_kf":1.28},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":92},"wind":{"speed":0.96,"deg":45.5001},"rain":{"3h":2},"sys":{"pod":"d"},"dt_txt":"2014-11-08 03:00:00"},{"dt":1415426400,"main":{"temp":282.68,"temp_min":281.654,"temp_max":282.68,"pressure":940.41,"sea_level":1039.44,"grnd_level":940.41,"humidity":100,"temp_kf":1.03},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04d"}],"clouds":{"all":92},"wind":{"speed":0.95,"deg":44.5003},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-11-08 06:00:00"},{"dt":1415437200,"main":{"temp":281.71,"temp_min":280.944,"temp_max":281.71,"pressure":940.62,"sea_level":1039.8,"grnd_level":940.62,"humidity":100,"temp_kf":0.77},"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.9,"deg":39.0014},"rain":{"3h":6},"sys":{"pod":"n"},"dt_txt":"2014-11-08 09:00:00"},{"dt":1415448000,"main":{"temp":281.04,"temp_min":280.527,"temp_max":281.04,"pressure":940.04,"sea_level":1039.27,"grnd_level":940.04,"humidity":100,"temp_kf":0.51},"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.86,"deg":32.5003},"rain":{"3h":10},"sys":{"pod":"n"},"dt_txt":"2014-11-08 12:00:00"},{"dt":1415458800,"main":{"temp":280.62,"temp_min":280.364,"temp_max":280.62,"pressure":938.98,"sea_level":1038.05,"grnd_level":938.98,"humidity":100,"temp_kf":0.26},"weather":[{"id":502,"main":"Rain","description":"heavy intensity rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.75,"deg":12.5052},"rain":{"3h":13},"sys":{"pod":"n"},"dt_txt":"2014-11-08 15:00:00"},{"dt":1415469600,"main":{"temp":280.231,"temp_min":280.231,"temp_max":280.231,"pressure":936.83,"sea_level":1035.66,"grnd_level":936.83,"humidity":100},"weather":[{"id":502,"main":"Rain","description":"heavy intensity rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.81,"deg":30.0007},"rain":{"3h":14},"sys":{"pod":"n"},"dt_txt":"2014-11-08 18:00:00"},{"dt":1415480400,"main":{"temp":280.229,"temp_min":280.229,"temp_max":280.229,"pressure":934.54,"sea_level":1033.06,"grnd_level":934.54,"humidity":100},"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":0.92,"deg":37.5016},"rain":{"3h":10},"sys":{"pod":"n"},"dt_txt":"2014-11-08 21:00:00"},{"dt":1415491200,"main":{"temp":280.854,"temp_min":280.854,"temp_max":280.854,"pressure":933.45,"sea_level":1031.18,"grnd_level":933.45,"humidity":100},"weather":[{"id":502,"main":"Rain","description":"heavy intensity rain","icon":"10d"}],"clouds":{"all":92},"wind":{"speed":0.88,"deg":17.0035},"rain":{"3h":13},"sys":{"pod":"d"},"dt_txt":"2014-11-09 00:00:00"},{"dt":1415502000,"main":{"temp":281.721,"temp_min":281.721,"temp_max":281.721,"pressure":929.45,"sea_level":1026.99,"grnd_level":929.45,"humidity":100},"weather":[{"id":502,"main":"Rain","description":"heavy intensity rain","icon":"10d"}],"clouds":{"all":92},"wind":{"speed":0.9,"deg":339.001},"rain":{"3h":17},"sys":{"pod":"d"},"dt_txt":"2014-11-09 03:00:00"},{"dt":1415512800,"main":{"temp":283.128,"temp_min":283.128,"temp_max":283.128,"pressure":927.29,"sea_level":1023.99,"grnd_level":927.29,"humidity":100},"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"clouds":{"all":92},"wind":{"speed":0.76,"deg":344.003},"rain":{"3h":5},"sys":{"pod":"d"},"dt_txt":"2014-11-09 06:00:00"},{"dt":1415523600,"main":{"temp":282.42,"temp_min":282.42,"temp_max":282.42,"pressure":926.78,"sea_level":1023.4,"grnd_level":926.78,"humidity":100},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":44},"wind":{"speed":0.71,"deg":313.001},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-11-09 09:00:00"},{"dt":1415566800,"main":{"temp":278.87,"temp_min":278.87,"temp_max":278.87,"pressure":924.81,"sea_level":1022.3,"grnd_level":924.81,"humidity":100},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":24},"wind":{"speed":1.23,"deg":333.004},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-11-09 21:00:00"}]}',true);
	$weatherdata = json_decode(file_get_contents('http://api.openweathermap.org/data/2.5/forecast?lat=$lat&lon=$lon'),true);

	echo file_get_contents('http://api.openweathermap.org/data/2.5/forecast?lat=$lat&lon=$lon');
	
	// get a detailed array of weather data
	$timestamp = array();
	$temperature = array();
	$temperature_min = array();
	$temperature_max = array();
	$pressure = array();
	$humidity = array();
	$windspeed = array();
	$winddirection = array();
	$cloudfactor = array();
	$precipitation = array();
	$symbol = array();
	
	
	foreach($weatherdata['list'] as $forecast) {
		$timestamp[]     	= $forecast['dt'];
		$temperature[]   	= $forecast['main']['temp']-273.15;
		$temperature_min[]  = $forecast['main']['temp_min']-273.15;
		$temperature_max[]  = $forecast['main']['temp_max']-273.15;
		$pressure[]      	= $forecast['main']['pressure'];
		$humidity[]      	= $forecast['main']['humidity'];	
		$windspeed[]     	= $forecast['wind']['speed'];
		$winddirection[] 	= $forecast['wind']['deg'];
		$cloudfactor[] 		= $forecast['clouds']['all']/100;
		$icon[]        		= $icon[$forecast['weather']['icon']];
		if(array_key_exists($forecast,'rain')){
			$precipitation[] 	= $forecast['rain']['3h']/3;  // not sure this is allways present		
		}
		else{
			$precipitation[] = 0;
		}			
	}
	
	$forecast = array(	'timestamp'=>$timestamp,
						'temperature'=>$temperature,
						'temperature_min'=>$temperature_min,
						'temperature_max'=>$temperature_max,
						'precipitation'=>$precipitation,
						'windspeed'=>$windspeed,
						'winddirection'=>$winddirection,
						'pressure'=>$pressure,
						'humidity'=>$humidity,
						'cloudfactor'=>$cloudfactor,
						'icon'=>$icon);
	
	if($detailed){
		// return the detailed array of weather data
		return $forecast;
	}
	else{
		// return an averaged array of weather data
		return $forecast;
	}

}
/*
function display_weather_forecast(){

	$forecast = weather_forecast();
	
	echo "
				<div class='weatherforecast'>";
	
	// add details in a table
	for($i=0;$i<count($forecast['temperature']);$i++){			
		echo "
					<div class='table'>
						<p>time and day</p>
						<img src='images/weather/".$forecast['icon'][$i]."'>
						<p class='small'>".$forecast['temperature'][$i]." &deg;C</p>
						<p class='small'>".$forecast['precipitation'][$i]." mm/h</p>
						<p class='small'>".$forecast['windspeed'][$i]." m/s   ".$forecast['winddirection'][$i]."&deg;</p>
					</div>";
	}
	echo "
				</div>";
				
				

}
*/
function display_weather_forecast_detailed(){	

	// add a temperature and cloud factor chart
		echo "
						<div class='weather_forecast'>
							<div id='weather_chart_container'></div>
							
							<div class='forecast' id='forecast_template'>
								<div id='id_time'></div>
								<img src='icons/weather/blank.png'>
								<div id='id_time'></div>
								<div id='id_time'></div>
								<div id='id_time'></div>
								<div id='id_time'></div>
							</div>
						</div>";
}

?>