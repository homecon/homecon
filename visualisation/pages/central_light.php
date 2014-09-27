<?php

begin_article($page_class);
	add_header("Central Lights","light_light");
	
	begin_collapsible("General",false);
		begin_group();
			add_button("centraal.lights.alles","0","Alles uit");
			add_button("centraal.lights.gelijkvloers","0","Gelijkvloers uit");
			add_button("centraal.lights.verdieping","0","Verdieping uit");
			add_button("centraal.lights.buiten","0","Buiten uit");
		end_group();
	end_collapsible();
	
end_article();

?>