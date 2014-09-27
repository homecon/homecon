<?php
begin_article($page_class);
	add_header("Energy","measure_power_meter");
	
	begin_collapsible("Energy use",false);
		begin_group();
			add_chart('Electricity','9,10');
			add_chart('Natural gas','11');
		end_group();			
	end_collapsible();	
	
	begin_collapsible("Averages",false);
		begin_group();
			add_week_average_chart('Electricity','9,10');
			add_week_average_chart('Natural gas','11');
		end_group();			
	end_collapsible();	
	
	begin_collapsible("Heat",false);
		begin_group();
			add_chart('Living zone','15,16,17,18,19');
			add_chart('Bathroom'   ,'23,24,25,26,27');
			add_chart('Bedrooms'   ,'31,32,33,34,35');
		end_group();			
	end_collapsible();
	
end_article();

?>