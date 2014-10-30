<?php

			begin_article($page_class);
				add_header("Measurements","measure_power_meter");
				
				begin_collapsible("Define signals",false);	
					begin_group(1);
	echo "
						<div class='measurements_define' id='measurements_define'>";

	$result = mysql_query("SELECT * FROM measurements_legend");
	$count = 0;
	while($row = mysql_fetch_array($result)){
		echo "
					 
							<div class='signal_placeholder' data-id='".$row['id']."' data-item='".$row['item']."' data-name='".$row['name']."' data-quantity='".$row['quantity']."' data-unit='".$row['unit']."' data-description='".$row['description']."'></div>";
	}
	echo "
							<p>Warning: the user is responsible for identifying signals after changes are made</p>
							<div>
								<a class='add' id='measurements_submit' data-role='button'>Submit</a>
							</div>
							<div data-role='popup' id='measurements_submit_popup' class='ui-content' data-position-to='window' data-overlay-theme='a' data-dismissible='false'>
								<p>Please wait<p>
							</div>
							<div class='signal' id='signal_template' data-id='id' style='display:none'>
								<input type='text' data-column='id' id='id_id' disabled placeholder='id'>
								<input type='text' data-column='item' id='id_item' placeholder='item'>
								<input type='text' data-column='name' id='id_name' placeholder='name'>
								<input type='text' data-column='quantity' id='id_quantity' placeholder='quantity'>
								<input type='text' data-column='unit' id='id_unit' placeholder='unit'>
								<input type='text' data-column='description' id='id_description' placeholder='description'>
							</div>
						</div>";
				
					end_group();
				end_collapsible();	
				
				begin_collapsible("Export data",true);	
					begin_group(1);
	echo "
						<div class='measurements_export'>
							<label id='measurements_export_startdate_lab' for='measurements_export_startdate'>From:</label>
							<input type='date' id='measurements_export_startdate'>
							<label id='measurements_export_enddate_lab' for='measurements_export_enddate'>Untill:</label>
							<input type='date' id='measurements_export_enddate'>
							<div>
								<a class='add' id='measurements_export' data-role='button'>Export data</a>
							</div>
						</div>";	
						
					end_group();
				end_collapsible();
				
				begin_collapsible("Clear data",true);	
					begin_group(1);	
	echo "	
						<div class='measurements_clear'>
							<div>
								<a class='add' id='measurements_clear' data-role='button'>Clear all data</a>
							</div>
							<div data-role='popup' id='measurements_clear_popup' data-overlay-theme='a'>
								<div data-role='header' class='ui-corner-top'>
									<h1>Clear measurements?</h1>
								</div>
								<div data-role='content' class='ui-corner-bottom ui-content'>
									<h3 class='ui-title'>Are you sure you want to clear all measurement data?</h3>
									<a data-role='button' id='measurements_clear_cancel' data-inline='true' data-theme='c'>Cancel</a>    
									<a data-role='button' id='measurements_clear_confirm' data-inline='true' data-theme='b'>Clear</a>  
								</div>
							</div>
						</div>";	
				
					end_group();
				end_collapsible();
			end_article();



?>
