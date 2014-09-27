<?php
begin_article($page_class);

	add_header("Bedroom","scene_sleeping_alternat","bedroom1.measurements.temperature");

	begin_collapsible("Light",false);
		begin_controlgroup();
			add_button("central.lights.night","off","Night setting");
			add_button("bedroom1.scenes","0","Mood 1");
			add_button("bedroom1.scenes","1","Mood 2");
		end_controlgroup();
		begin_group(2);
			add_switch("bedroom1.lights.light","Light");
			add_switch("bedroom1.lights.light_dressing","Dressing");
		end_group();
		begin_group();
			add_dimmer("bedroom1.lights.nightlight_right","Night light right");
			add_dimmer("bedroom1.lights.nightlight_left","Night light left");
		end_group();
	end_collapsible();
	
	begin_collapsible("Alarms",false);
		begin_group();			
			add_alarm(7,"","bedroom1.lights.nightlight_right.value,bedroom1.lights.nightlight_left.value,bedroom1.lights.light,bedroom1.lights.light_dressing","0,50,100,150,200,250,1");
		end_group();
	end_collapsible();
	
	begin_collapsible("Shading",true);
		begin_group();			
			add_shade_control("bedroom1.windows.right.shading","Right");
			add_shade_control("bedroom1.windows.front.shading","Front");
		end_group();
		begin_group();	
			add_alarm(4,"","bedroom1.windows.right.shading.closed,bedroom1.windows.front.shading.closed","0,1");
		end_group();
	end_collapsible();
	
end_article();
?>