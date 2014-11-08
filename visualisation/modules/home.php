<?php
echo "
				<article class=$page_class>";
		
include("clock.php");
	
echo "
			<hr>
";	
	
display_local_weather();

display_weather_forecast();


echo "
				</article>";
?>