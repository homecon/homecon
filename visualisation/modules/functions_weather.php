<?php
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