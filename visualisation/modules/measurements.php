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
				<form action='index.php?page=modules/measurements' method='post' name='define' class='define'>";
	$result = mysql_query("SELECT * FROM measurements_legend");
	$count = 0;
	while($row = mysql_fetch_array($result)){
		$count++;
		
		$id = $row['id'];
		$item = $row['item'];
		$name = $row['name'];
		$quantity = $row['quantity'];
		$unit = $row['unit'];
		$description = $row['description'];
		
		$id_id = "id".$id;
		$item_id = "item".$id;
		$name_id = "name".$id;
		$quantity_id = "quantity".$id;
		$unit_id = "unit".$id;
		$description_id = "description".$id;
		
		$readonly = "";
		if($count<=35){
			$readonly = "readonly";
		}
		echo "
					<div>
						<input type='text' name='$id_id' id='$id_id' value='$id' disabled placeholder='id'>
						<input type='text' name='$item_id' id='$item_id' value='$item' $readonly placeholder='item'>
						<input type='text' name='$name_id' id='$name_id' value='$name' placeholder='name'>
						<input type='text' name='$quantity_id' id='$quantity_id' value='$quantity' placeholder='quantity'>
						<input type='text' name='$unit_id' id='$unit_id' value='$unit' placeholder='unit'>
						<input type='text' name='$description_id' id='$description_id' value='$description' placeholder='description'>
					</div>";
	}
	echo "
					<p>Warning: the user is responsible for identifying signals after changes are made</p>
					<button type='submit' name='define'>Submit</button>
				</form>";
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
