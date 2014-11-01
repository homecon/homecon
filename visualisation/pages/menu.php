<?php


begin_menu();

	begin_menu_collapsible("Central","central");
		add_menu_item("Light","central_light","light_light.png");
		add_menu_item("Shading","central_shading","fts_sunblind.png");
		add_menu_item("Indoor climate","central_indoor","sani_heating.png");
		add_menu_item("Weather","central_weather","weather_cloudy_light.png");
		add_menu_item("Energy","central_energy","measure_power_meter.png");
	end_menu_collapsible();
	
	begin_menu_collapsible("First Floor","firstfloor",true);
		add_menu_item("Living","firstfloor_living","scene_livingroom.png");
		add_menu_item("Hallway","firstfloor_hallway","scene_hall.png");
	end_menu_collapsible();
	
	begin_menu_collapsible("Second Floor","secondfloor");
		add_menu_item("Corridor","secondfloor_corridor","scene_stairs.png");
		add_menu_item("Bathroom","secondfloor_bathroom","scene_bath.png");
		add_menu_item("Bedroom","secondfloor_bedroom1","scene_sleeping_alternat.png");
	end_menu_collapsible();
	
end_menu();	
	

		
?>