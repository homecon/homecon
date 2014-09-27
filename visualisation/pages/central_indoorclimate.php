<?php
begin_article($page_class);
	add_header("Indoor Climate","sani_heating");
	
	begin_collapsible("Setpoints",false);
		add_title("Living zones");	
		add_setpoint("Living zones");
	end_collapsible();	
	begin_collapsible("Model",true);	
		begin_controlgroup();
			add_button("building.model.identify","on","Model identification");
		end_controlgroup();
			
	end_collapsible();	
	
	begin_collapsible("Temperature",true);
		add_chart('Temperature Leefruimtes','39,40,41,42');
		add_chart('Temperature Bathroom','43');
	end_collapsible();

	begin_collapsible("Ventilation",true);
		begin_group();
			add_ventilation_control();
		end_group();
		begin_controlgroup();
			add_button("building.ventilation.speedcontrol","0","Off");
			add_button("building.ventilation.speedcontrol","1","Low");
			add_button("building.ventilation.speedcontrol","2","Medium");
			add_button("building.ventilation.speedcontrol","3","High");
		end_controlgroup();
	end_collapsible();	
end_article();
?>