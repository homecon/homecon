<?php

function weather_forecast($detailed = NULL){

	// latitude and longitude should be loaded from smarthome or mysql in the future
	$lat = 51;
	$lon = 5;
	
	// load weather forecast from openweaterhmap
	$weatherdata = json_decode(file_get_contents('http://api.openweathermap.org/data/2.5/forecast?lat=$lat&lon=$lon'));

	// get a detailed array of weather data
	$timestamp = array();
	$temperature = array();
	$precipitation = array();
	$windspeed = array();
	$winddirection = array();
	$pressure = array();
	$symbol = array();
	
	foreach($weatherdata->forecast->tabular->time as $forecast) {
		$timestamp[]     = $forecast->timestamp['value'];
		$temperature[]   = $forecast->temperature['value'];
		$precipitation[] = $forecast->precipitation['value'];
		$windspeed[]     = $forecast->windSpeed['mps'];
		$winddirection[] = $forecast->windDirection['code'];
		$pressure[]      = $forecast->pressure['value'];	
		$symbol[]        = $forecast->symbol['value'];	
	}
	
	$forecast = array('timestamp'=>$timestamp,'temperature'=>$temperature,'precipitation'=>$precipitation,'windspeed'=>$windspeed,'winddirection'=>$winddirection,'pressure'=>$pressure,'symbol'=>$symbol)
	
	if($detailed){
		// return the detailed array of weather data
		return $forecast
	}
	else{
		// return an averaged array of weather data
		
		
		
		return $forecast
	}
}

function display_weather_forecast(){	
	$forecast = weather_forecast();
	
	echo "
				<div class='weatherforecast'>";
	
	
	// display result
	echo "
					<div>
						<p>$day</p>
						<img src='$forecast_img_src'>
						<p class='small'>$temperature &deg;C</p>
						<p class='small'>$precipitation mm</p>
						<p class='small'>$windSpeed m/s   $windDirection</p>
						<p class='small'>$pressure hPa</p>
					</div>";
	echo "
				</div>";
}
function display_detailed_weather_forecast(){	
	$forecast = weather_forecast(1);
	
	// add a temperature chart
	
	
	// add details in a table
	
}
function get_forecast_img($forecast){

	// get a nice image
	if(strcmp($forecast->symbol['number'],'1') == 0){
		$forecast_img_src = "icons/weather/sun_1.png";
	}
	elseif(strcmp($forecast->symbol['number'],'2') == 0){
		$forecast_img_src = "icons/weather/sun_2.png";
	}
	elseif(strcmp($forecast->symbol['number'],'3') == 0){
		$forecast_img_src = "icons/weather/sun_5.png";
	}
	elseif(strcmp($forecast->symbol['number'],'4') == 0){
		$forecast_img_src = "icons/weather/cloud_4.png";
	}
	elseif(strcmp($forecast->symbol['number'],'5') == 0){
		$forecast_img_src = "icons/weather/sun_7.png";
	}
	elseif(strcmp($forecast->symbol['number'],'6') == 0){
		$forecast_img_src = "icons/weather/sun_9.png";
	}
	elseif(strcmp($forecast->symbol['number'],'7') == 0){
		$forecast_img_src = "icons/weather/cloud_7.png";
	}
	elseif(strcmp($forecast->symbol['number'],'8') == 0){
		$forecast_img_src = "icons/weather/cloud_7.png";
	}
	elseif(strcmp($forecast->symbol['number'],'9') == 0){
		$forecast_img_src = "icons/weather/cloud_7.png";
	}
	elseif(strcmp($forecast->symbol['number'],'10') == 0){
		$forecast_img_src = "icons/weather/cloud_8.png";
	}
	elseif(strcmp($forecast->symbol['number'],'13') == 0){
		$forecast_img_src = "icons/weather/cloud_13.png";
	}
	elseif(strcmp($forecast->symbol['number'],'22') == 0){
		$forecast_img_src = "icons/weather/cloud_10.png";
	}
	else{
		$forecast_img_src = "icons/weather/na.png";
	}
	return $forecast_img_src;
}

?>