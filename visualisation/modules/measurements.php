<?php

	if(array_key_exists('clear',$_POST)){
		mysql_query("TRUNCATE measurements");
		mysql_query("TRUNCATE measurements_weekaverage");
		mysql_query("TRUNCATE measurements_monthaverage");
	}
	elseif(array_key_exists('define',$_POST)){
	
		$result = mysql_query("SELECT * FROM measurements_legend");
		while($row = mysql_fetch_array($result)){
			$id = $row['id'];
			$item = $_POST['item'.$id];
			$name = $_POST['name'.$id];
			$quantity = $_POST['quantity'.$id];
			$unit = $_POST['unit'.$id];
			$description = $_POST['description'.$id];
			
			mysql_query("UPDATE measurements_legend SET item='$item', name='$name', quantity='$quantity', unit='$unit', description='$description' WHERE id=$id");
		}
	}


	// display a form for data selection and table manipulation
	
	begin_article($page_class);
		add_header("Measurements","measure_power_meter");
		begin_collapsible("Export data",false);
			begin_group(1);
	echo "
				<form action='modules/measurements_export.php' method='post' target='_blank' name='export' id='export'>
					<label for='startdate'>Start datum:</label>
					<input type='date' name='startdate' id='startdate'>
					
					<label for='enddate'>Eind datum:</label>
					<input type='date' name='enddate' id='enddate'>
					
					<button type='submit' name='export'>Export</button>
				</form>";
				
			end_group();
		end_collapsible();
		
		begin_collapsible("Define signals",true);	
			begin_group(1);
	echo "
				<div class='measurements_define' id='measurements_define'>";

	$result = mysql_query("SELECT * FROM measurements_legend");
	$count = 0;
	while($row = mysql_fetch_array($result)){
		echo "
					 
					<div class='signal_placeholder' data-id=".$row['id']." data-item=".$row['item']." data-name=".$row['name']." data-quantity=".$row['quantity']." data-unit=".$row['unit']." data-description=".$row['description']."'></div>";
	}
	echo "
					<p>Warning: the user is responsible for identifying signals after changes are made</p>
					<div>
						<a class='add' data-role='button'>Submit</a>
					</div>
				</div>";
				
	// echo a hidden template for the measurement
	echo "
	
					<div class='signal' id='signal_template' data-id='id' style='display:none'>
						<input type='text' data-column='id' id='id_id' disabled placeholder='id'>
						<input type='text' data-column='item' id='id_item' placeholder='item'>
						<input type='text' data-column='name' id='id_name' placeholder='name'>
						<input type='text' data-column='quantity' id='id_quantity' placeholder='quantity'>
						<input type='text' data-column='unit' id='id_unit' placeholder='unit'>
						<input type='text' data-column='description' id='id_description' value='$description' placeholder='description'>
					</div>";
				
			end_group();
		end_collapsible();		
			
		begin_collapsible("Clear data",true);	
			begin_group(1);	
	echo "	
				<form action='index.php?page=modules/measurements' method='post' name='clear'>
					<button type='submit' name='clear'>Clear all data</button>
				</form>";	
				
			end_group();
		end_collapsible();
	end_article();



?>
