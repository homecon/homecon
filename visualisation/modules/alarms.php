<?php
// display a form for alarm_action manipulation
begin_article($page_class);
	add_header("Alarms","measure_power_meter");

	begin_collapsible("Define actions",true);	
		begin_group(1);
		
	echo "
				<form action='index.php?page=modules/alarms' method='post' name='define' class='define'>";
	$result = mysql_query("SELECT * FROM alarm_actions");
	$count = 0;
	while($row = mysql_fetch_array($result)){
		$count++;
		
		$id = $row['id'];
		$name = $row['name'];
		$sectionid = $row['sectionid'];
		
		$delay1 = $row['delay1'];
		$item1 = $row['item1'];
		$action1 = $row['action1'];
		$delay2 = $row['delay2'];
		$item2 = $row['item2'];
		$action2 = $row['action2'];
		$delay3 = $row['delay3'];
		$item3 = $row['item3'];
		$action3 = $row['action3'];
		$delay4 = $row['delay4'];
		$item4 = $row['item4'];
		$action4 = $row['action4'];
		$delay5 = $row['delay5'];
		$item5 = $row['item5'];
		$action5 = $row['action5'];
		
		
		
		$id_id = "id".$id;
		$name_id = "name".$id;
		
		$delay1_id = "delay1".$id;
		$item1_id = "item1".$id;
		$action1_id = "action1".$id;
		$delay2_id = "delay2".$id;
		$item2_id = "item2".$id;
		$action2_id = "action2".$id;
		$delay3_id = "delay3".$id;
		$item3_id = "item3".$id;
		$action3_id = "action3".$id;
		$delay4_id = "delay4".$id;
		$item4_id = "item4".$id;
		$action4_id = "action4".$id;
		$delay5_id = "delay5".$id;
		$item5_id = "item5".$id;
		$action5_id = "action5".$id;
		
		$readonly = "";
		if($count<=35){
			$readonly = "readonly";
		}
		echo "
					<div>
						<input type='text' name='$id_id'          id='$id_id'        value='$id' disabled placeholder='id'>
						<input type='text' name='$item_id'        id='$item_id'      value='$item' $readonly placeholder='item'>
						<input type='text' name='$name_id'        id='$name_id'      value='$name' placeholder='name'>
						<input type='text' name='$quantity_id'    id='$quantity_id'  value='$quantity' placeholder='quantity'>
						<input type='text' name='$unit_id'        id='$unit_id'      value='$unit' placeholder='unit'>
						<input type='text' name='$description_id' id='$description_id' value='$description' placeholder='description'>
					</div>";
	}
	echo "
					<button type='submit' name='define'>Submit</button>
				</form>";
				
		end_group();
	end_collapsible();		
end_article();



?>
