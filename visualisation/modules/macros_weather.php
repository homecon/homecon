<?php

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
						<div id='weather_forecast'>
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