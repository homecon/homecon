<?php
begin_article($page_class);

	add_header("Hallway","scene_stairs");
	
	begin_collapsible("Light",false);
		begin_group(2);
			add_switch("corridor.lights.light_stairs","Stairs");
		end_group();
		begin_group();
			add_dimmer("corridor.lights.spots_corridor","corridor");
		end_group();
	end_collapsible();	
	
	begin_collapsible("Shading",true);	
		begin_group();	
			add_shade_control("corridor.windows.right.shading","Right");
			add_shade_control("corridor.windows.back.shading","Back");
		begin_group();	
			add_alarm(3,"","corridor.windows.right.shading.closed,corridor.windows.back.shading.closed","0,1");
		end_group();
	end_collapsible();
	
end_article();
?>