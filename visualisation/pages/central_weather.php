<?php
begin_article($page_class);
	add_header("Weather","weather_cloudy_light");
	
	begin_collapsible("Forecast",false);
	
	end_collapsible();
	
	begin_collapsible("Measurements",false);
		begin_group();
			add_chart('Outside temperature','1');
		end_group();			
	end_collapsible();	
	
	begin_collapsible("Sun",true);
		begin_group();
			add_chart('Azimut','2');
			add_chart('Altitude','3');
			add_chart('Theoretical solar gains','4,5');
			add_chart('Clouds','6');
		end_group();	
	end_collapsible();			
end_article();

?>