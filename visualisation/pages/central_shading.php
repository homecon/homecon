<?php

begin_article($page_class);

	add_header("Central shading control","fts_sunblind");

	begin_collapsible("General",false);
		begin_group(1);
			add_shade_control("central.shading.shading_firstfloor","Shading first floor");
			add_shade_control("central.shading.shading_secondfloor","Shading second floor");
			begin_controlgroup();
				add_button("logics.reset_override","on","Reset override");
			end_controlgroup();
		end_group();
	end_collapsible();
	begin_collapsible("Alarms",false);
		begin_group(1);	
			add_alarm(1,"","building.shading.closed","0,1");
		end_group();
	end_collapsible();

	begin_collapsible("Solar gains",true);	
		begin_group();
			add_quantity("Azimut: ",'building.irradiation.azimut','deg',1);
			add_quantity("Altitude: ",'building.irradiation.altitude','deg',1);
		end_group();
		begin_group();
			add_quantity("Theoretical direct irradiation: ",'building.irradiation.direct_theoretical','W/m2',1);
			add_quantity("Theoretical diffuse irradiation: ",'building.irradiation.diffuse_theoretical','W/m2',1);
			add_quantity("Theoretical sensor measurement: ",'building.irradiation.sensor.theoretical_value','W/m2',1);
			add_quantity("Sensor measurement: ",'buiten.measurements.lichtsterkte','lux',0);
			add_quantity("Cloud factor: ",'building.irradiation.cloud_factor','',2);
		end_group();
	end_collapsible();

end_article();


?>