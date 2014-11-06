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
			add_bar_chart('Electricity','9,10');
			add_bar_chart('Natural gas','11');
		end_group();			
	end_collapsible();	
	
end_article();

?>