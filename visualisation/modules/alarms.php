<?php
// display a form for alarm_action manipulation
begin_article($page_class);
	add_header("Alarms","control_alarm");

	begin_collapsible("Define actions",false);	
		begin_group(1);
		
		
	echo "	
			<div class=alarm_action_container>";
	
	$result = mysql_query("SELECT * FROM alarm_actions");
	$count = 0;
	while($row = mysql_fetch_array($result)){
	
		echo " 
				<div class='alarm_action_placeholder' data-id='".$row['id']."' data-name='".$row['name']."' data-sectionid='".$row['sectionid']."' data-delay1='".$row['delay1']."' data-item1='".$row['item1']."' data-value1='".$row['value1']."' data-delay2='".$row['delay2']."' data-item2='".$row['item2']."' data-value2='".$row['value2']."' data-delay3='".$row['delay3']."' data-item3='".$row['item3']."' data-value3='".$row['value3']."' data-delay4='".$row['delay4']."' data-item4='".$row['item4']."' data-value4='".$row['value4']."' data-delay5='".$row['delay5']."' data-item2='".$row['item5']."' data-value5='".$row['value5']."'></div>";
	}
	echo "
				<a class='add' href='#' data-role='button'>Add action</a>
			</div>";
				
		end_group();
	end_collapsible();		
end_article();


// echo a hidden template for the alarm

	echo "
				<div class='alarm_action' id='alarm_action_template' data-id='id' style='display:none'>
					<a class='delete' href='#'><img src=icons/ws/control_x.png></a>
					<input type='text'  data-column='name'       placeholder='name'>
					<input type='text'  data-column='sectionid'  placeholder='section id filter'>
					<div>
						<input type='number'  data-column='delay1'   placeholder='delay 1'>
						<input type='text'    data-column='item1'    placeholder='item 1'>
						<input type='text'    data-column='value1'   placeholder='value 1'>
					</div>
					<div>
						<input type='number'  data-column='delay2'   placeholder='delay 2'>
						<input type='text'    data-column='item2'    placeholder='item 2'>
						<input type='text'    data-column='value2'   placeholder='value 2'>
					</div>
					<div>
						<input type='number'  data-column='delay3'   placeholder='delay 3'>
						<input type='text'    data-column='item3'    placeholder='item 3'>
						<input type='text'    data-column='value3'   placeholder='value 3'>
					</div>
					<div>
						<input type='number'  data-column='delay4'   placeholder='delay 4'>
						<input type='text'    data-column='item4'    placeholder='item 4'>
						<input type='text'    data-column='value4'   placeholder='value 4'>
					</div>
					<div>
						<input type='number'  data-column='delay5'   placeholder='delay 5'>
						<input type='text'    data-column='item5'    placeholder='item 5'>
						<input type='text'    data-column='value5'   placeholder='value 5'>
					</div>
				</div>";
			
	
?>
