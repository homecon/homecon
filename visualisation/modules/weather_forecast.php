<?php

echo "
		<section class='weerbericht'>";
		
$weatherdata = simplexml_load_file('http://www.yr.no/stad/Belgium/Flanders/Opglabbeek/varsel.xml');
		
$count = 0;
foreach($weatherdata->forecast->tabular->time as $forecast) {
	if(strcmp($forecast['period'],'2') == 0 && $count < 4){
		$count = $count + 1;
		
		$forecast_img_src = get_forecast_img($forecast);
		
		// get the day of the week
		$dayofweek = array("maa", "din", "woe", "don", "vri", "zat", "zon");
		
		$day_of_week = date('N',strtotime($forecast['from']));
		$day = $dayofweek[$day_of_week-1];
		
		
		$temperature = $forecast->temperature['value'];
		$precipitation = $forecast->precipitation['value'];
		$windSpeed = $forecast->windSpeed['mps'];
		$windDirection = $forecast->windDirection['code'];
		$pressure = $forecast->pressure['value'];
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

	}
}

echo "
		</section>";
?>