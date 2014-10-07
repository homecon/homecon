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
		
		echo "
				<div data-id='$id'>
					<a class='alarm_action delete' href='#'><img src=icons/ws/control_x.png></a>
					<input type='text' name='name$id'        id='name$id'      value='$name'      placeholder='name'>
					<input type='text' name='sectionid$id'   id='sectionid$id' value='$sectionid' placeholder='section id filter'>
					<div>
						<input type='number' name='delay1$id'   id='delay1$id'  value='$delay1'  placeholder='delay 1'>
						<input type='text'   name='item1$id'    id='item1$id'   value='$item1'   placeholder='item 1'>
						<input type='text'   name='action1$id'  id='action1$id' value='$action1' placeholder='action 1'>
					</div>
					<div>
						<input type='number' name='delay2$id'   id='delay2$id'  value='$delay2'  placeholder='delay 2'>
						<input type='text'   name='item2$id'    id='item2$id'   value='$item2'   placeholder='item 2'>
						<input type='text'   name='action2$id'  id='action2$id' value='$action2' placeholder='action 2'>
					</div>
					<div>
						<input type='number' name='delay3$id'   id='delay3$id'  value='$delay3'  placeholder='delay 3'>
						<input type='text'   name='item3$id'    id='item3$id'   value='$item3'   placeholder='item 3'>
						<input type='text'   name='action3$id'  id='action3$id' value='$action3' placeholder='action 3'>
					</div>
					<div>
						<input type='number' name='delay4$id'   id='delay4$id'  value='$delay4'  placeholder='delay 4'>
						<input type='text'   name='item4$id'    id='item4$id'   value='$item4'   placeholder='item 4'>
						<input type='text'   name='action4$id'  id='action4$id' value='$action4' placeholder='action 4'>
					</div>
					<div>
						<input type='number' name='delay5$id'   id='delay5$id'  value='$delay5'  placeholder='delay 5'>
						<input type='text'   name='item5$id'    id='item5$id'   value='$item5'   placeholder='item 5'>
						<input type='text'   name='action5$id'  id='action5$id' value='$action5' placeholder='action 5'>
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
