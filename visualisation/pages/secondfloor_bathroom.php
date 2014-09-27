<?php
begin_article($page_class);

	add_header("Bathroom","scene_bath","bathroom.measurements.temperature");
	
	begin_collapsible("Light",false);
		begin_group(2);
			add_switch("bathroom.lights.light","Light");
			add_switch("bathroom.lights.light_shower","Shower");
			add_switch("bathroom.lights.light_mirror","Mirror");
		end_group();
	end_collapsible();	
		
end_article();
?>