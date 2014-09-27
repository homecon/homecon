<?php
begin_article($page_class);

	add_header("Living","scene_livingroom","living.measurements.temperature");
	
	begin_collapsible("light",false);
		begin_controlgroup();
			add_button("living.scenes","0","Dinner");
			add_button("living.scenes","1","Company");
			add_button("living.scenes","2","TV");
			add_button("living.scenes","3","Lights off");
		end_controlgroup();	
		begin_group(2);
			add_switch("living.lights.spots_kitchen","Kitchen spots");
			add_switch("living.lights.light_dinnertable","Dinner table");
		end_group();
		begin_group();
			add_dimmer("living.lights.light_tv","TV lights");
		end_group();
	end_collapsible();	
	
	begin_collapsible("Shading",true);	
		begin_group();
			add_shade_control("living.windows.back.shading","Back");
		end_group();
	end_collapsible();
	
end_article();
?>