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
		
		
		$name_id = "name".$id;
		$sectionid_id = "sectionid".$id;
		
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
		
		echo "
				<div data-id='$id'>
					<a class='alarm_action delete' href='#'><img src=icons/ws/control_x.png></a>
					<input type='text' name='$name_id'        id='$name_id'      value='$id' disabled placeholder='name'>
					<input type='text' name='$sectionid_id'   id='$sectionid_id' value='$id' disabled placeholder='name'>
					<div>
						<input type='number' name='$delay1_id'   id='$delay1_id'  value='$delay1'  placeholder='delay 1'>
						<input type='text'   name='$item1_id'    id='$item1_id'   value='$item1'   placeholder='item 1'>
						<input type='text'   name='$action1_id'  id='$action1_id' value='$action1' placeholder='action 1'>
					</div>
					<div>
						<input type='number' name='$delay2_id'   id='$delay2_id'  value='$delay2'  placeholder='delay 2'>
						<input type='text'   name='$item2_id'    id='$item2_id'   value='$item2'   placeholder='item 2'>
						<input type='text'   name='$action2_id'  id='$action2_id' value='$action2' placeholder='action 2'>
					</div>
					<div>
						<input type='number' name='$delay3_id'   id='$delay3_id'  value='$delay3'  placeholder='delay 3'>
						<input type='text'   name='$item3_id'    id='$item3_id'   value='$item3'   placeholder='item 3'>
						<input type='text'   name='$action3_id'  id='$action3_id' value='$action3' placeholder='action 3'>
					</div>
					<div>
						<input type='number' name='$delay4_id'   id='$delay4_id'  value='$delay4'  placeholder='delay 4'>
						<input type='text'   name='$item4_id'    id='$item4_id'   value='$item4'   placeholder='item 4'>
						<input type='text'   name='$action4_id'  id='$action4_id' value='$action4' placeholder='action 4'>
					</div>
					<div>
						<input type='number' name='$delay5_id'   id='$delay5_id'  value='$delay5'  placeholder='delay 5'>
						<input type='text'   name='$item5_id'    id='$item5_id'   value='$item5'   placeholder='item 5'>
						<input type='text'   name='$action5_id'  id='$action5_id' value='$action5' placeholder='action 5'>
					</div>
				</div>";
	}
	echo "
				<a class='alarm_action add' href='#' data-role='button'>Add action</a>
				<button type='submit' name='define'>Submit</button>
			</form>";
				
		end_group();
	end_collapsible();		
end_article();


// some jQuery to add and delete input fields
echo "
	<script type='text/javascript' src='js/alarm_actions.js'></script>";


?>
