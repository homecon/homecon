<?php
echo "
		<article class=$page_class>";
		
include("clock.php");
	
echo "
			<hr>
";	
	
include("weather_measurement.php");

echo "
			<hr>
";	
	
include("weather_forecast.php");

echo "		<hr>
		</article>	
";
?>