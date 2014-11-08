<?php

function display_local_weather(){

	echo "
						<div id='current_weather'>
							<img src='icons/weather/blank.png'>
							<div class='temperature'>Temperature: ";
	add_value("building.ambient_temperature","",1);
	echo "		
								&deg;C
							</div>
							<div class='wind'>Wind speed: ";
	add_value("building.wind_velocity","",1);
	echo "
								 m/s
							<div>Irradiation: ";
	add_value("building.irradiation.horizontal","",0);
	echo "
								W/m2
							</div>
							</div>
						</div>
						<hr>";
}						
						
function display_weather_forecast(){

	// add a temperature and cloud factor chart
	echo "
						<div id='weather_forecast_averaged'>
							<div class='forecast_details'>
								<div class='time'></div>
								<img src='icons/weather/blank.png'>
								<div class='temperature'></div>
								<div class='precipitation'></div>
								<div class='wind'></div>
								<div class='pressure'></div>
							</div>
							<div class='forecast_details'>
								<div class='time'></div>
								<img src='icons/weather/blank.png'>
								<div class='temperature'></div>
								<div class='precipitation'></div>
								<div class='wind'></div>
								<div class='pressure'></div>
							</div>
							<div class='forecast_details'>
								<div class='time'></div>
								<img src='icons/weather/blank.png'>
								<div class='temperature'></div>
								<div class='precipitation'></div>
								<div class='wind'></div>
								<div class='pressure'></div>
							</div>
							<div class='forecast_details'>
								<div class='time'></div>
								<img src='icons/weather/blank.png'>
								<div class='temperature'></div>
								<div class='precipitation'></div>
								<div class='wind'></div>
								<div class='pressure'></div>
							</div>
						</div>
						<hr>";

}
function display_weather_forecast_detailed(){	

	// add a temperature and cloud factor chart
	echo "
						<div id='weather_forecast_detailed'>
							<div id='weather_chart_container'></div>
							
							<div class='forecast_details'>
								<div class='time'></div>
								<img src='icons/weather/blank.png'>
								<div class='temperature'></div>
								<div class='precipitation'></div>
								<div class='wind'></div>
								<div class='pressure'></div>
							</div>
							<div class='forecast_details'>
								<div class='time'></div>
								<img src='icons/weather/blank.png'>
								<div class='temperature'></div>
								<div class='precipitation'></div>
								<div class='wind'></div>
								<div class='pressure'></div>
							</div>
							<div class='forecast_details'>
								<div class='time'></div>
								<img src='icons/weather/blank.png'>
								<div class='temperature'></div>
								<div class='precipitation'></div>
								<div class='wind'></div>
								<div class='pressure'></div>
							</div>
							<div class='forecast_details'>
								<div class='time'></div>
								<img src='icons/weather/blank.png'>
								<div class='temperature'></div>
								<div class='precipitation'></div>
								<div class='wind'></div>
								<div class='pressure'></div>
							</div>
							<div class='forecast_details'>
								<div class='time'></div>
								<img src='icons/weather/blank.png'>
								<div class='temperature'></div>
								<div class='precipitation'></div>
								<div class='wind'></div>
								<div class='pressure'></div>
							</div>
						</div>";
}

?>