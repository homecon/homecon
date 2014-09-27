<?php

$weatherdata = simplexml_load_file('http://www.yr.no/stad/Belgium/Flanders/Opglabbeek/varsel_time_for_time.xml');

$count = 0;
foreach($weatherdata->forecast->tabular->time as $forecast) {
	if($count<1){
		$count = $count + 1;
		$forecast_img_src = get_forecast_img($forecast);
	}
	else{
		break;
	}
}
		

echo "
		<section class='lokaal_weer'>
			<img src='$forecast_img_src'>
			<div>Buitentemperatuur: ";
				add_value("building.ambient_temperature","",1);
echo "
				&deg;C
			</div>
			<div> Windsnelheid: ";
				add_value("building.wind_velocity","",1);
echo "
				m/s
			</div>
			<div> Lichtsterkte: ";
				add_value("buiten.measurements.lichtsterkte","",0);
echo "
				lux
			</div>
		</section>";
?>
			