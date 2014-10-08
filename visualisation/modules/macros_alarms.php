<?php
function add_alarm($sectionid,$text,$itemlist,$actionlist){
	global $page;
	global $web;
	
	$page = explode('/',$page);
	$page = end($page);
	
	//$itemlist = explode(',',$itemlist);
	//$actionlist = explode(',',$actionlist);
	
	
	
	// check if an alarm must be added
	if(array_key_exists('add_alarm',$_GET)){
		if($_GET['add_alarm']==$sectionid){
			mysql_query("INSERT INTO alarms (sectionid,sunrise,sunset,hour,minute,mon,tue,wed,thu,fri,sat,sun) VALUES  ($sectionid,0,0,13,0,1,1,1,1,1,1,1)");
		}
	}
	// check if an alarm must be deleted
	if(array_key_exists('delete_alarm',$_GET)){
		if($_GET['delete_section']==$sectionid){
			$id=$_GET['delete_alarm'];
			mysql_query("DELETE FROM alarms WHERE id=$id");
		}
	}
	
	echo "
		<div class='alarm_container' id='alarm_section_$sectionid' data-id=$sectionid>";

	// find alarms with $sectionid in mysql and cycle through them
	$result = mysql_query("SELECT * FROM alarms WHERE sectionid = ".$sectionid);
	while($row = mysql_fetch_array($result)){
		$id = $row['id'];
		$items = $row['items'];
		$actions = $row['actions'];
		
		echo" 
			<script>
				$(document).ready(function(){
			
					var newAlarm = $('#alarm_template').clone();
					newAlarm.attr('id','alarm$id'); 
					newAlarm.attr('data-id',$id); 
					newAlarm.find('#id_mon').attr('id','mon$id');
					newAlarm.find('#id_tue').attr('id','tue$id');
					newAlarm.find('#id_wed').attr('id','wed$id');
					newAlarm.find('#id_thu').attr('id','thu$id');
					newAlarm.find('#id_fri').attr('id','fri$id');
					newAlarm.find('#id_sat').attr('id','sat$id');
					newAlarm.find('#id_sun').attr('id','sun$id');
					
					newAlarm.find('#id_mon_lab').attr('for','mon$id');
					newAlarm.find('#id_tue_lab').attr('for','tue$id');
					newAlarm.find('#id_wed_lab').attr('for','wed$id');
					newAlarm.find('#id_thu_lab').attr('for','thu$id');
					newAlarm.find('#id_fri_lab').attr('for','fri$id');
					newAlarm.find('#id_sat_lab').attr('for','sat$id');
					newAlarm.find('#id_sun_lab').attr('for','sun$id');
					
					var itemlist = [$itemlist];
					var items = [$items];
					
					for(i=0;i<itemlist.length;i++){
						itemselected = "";
						item = itemlist[i];
							
						if($.inArray(item, items)){
							itemselected =  'selected=selected';
						}	
						$(\"select[:data-column='item']\").append(\"<option \"+itemselected+\" value='\"+item+\"'>\"+item+\"</option>\");
					}
					
					var actionlist = [$actionlist];
					var action = [$actions];
					
					for(i=0;i<actionlist.length;i++){
						actionselected = "";
						action = actionlist[i];
							
						if($.inArray(action, actions)){
							actionselected =  'selected=selected';
						}	
						$(\"select[:data-column='action']\").append(\"<option \"+actionselected+\" value='\"+action+\"'>\"+action+\"</option>\");
					}
					
					newAlarm.show();
					$('#alarm_add_$sectionid').before(newAlarm);
				});
			</script>";
	}
	echo "
			<div id='alarm_add_$sectionid'>
				<a class='add' id='add_alarm_$sectionid' class='add_alarm' data-role='button'>wekker toevoegen</a>
			</div>
		</div>";
		
	// echo a hidden template for the alarm
	echo "
		<div class='alarm' id='alarm_template' data-id='id' style='display:none'>
			<input type='time' data-column='time'>
			<h1></h1>
			<a class='delete' href='#'><img src=icons/ws/control_x.png></a>
			<div class='days'>
				<div data-role='controlgroup' data-type='horizontal'>
					<input type='checkbox' data-column='mon' id='id_mon' class='custom' data-widget='basic.checkbox' data-mini='true'> <label id='id_mon_lab' for='id_mon'>maa</label>
					<input type='checkbox' data-column='tue' id='id_tue' class='custom' data-widget='basic.checkbox' data-mini='true'> <label id='id_tue_lab' for='id_tue'>din</label>
					<input type='checkbox' data-column='wed' id='id_wed' class='custom' data-widget='basic.checkbox' data-mini='true'> <label id='id_wed_lab' for='id_wed'>woe</label>
					<input type='checkbox' data-column='thu' id='id_thu' class='custom' data-widget='basic.checkbox' data-mini='true'> <label id='id_thu_lab' for='id_thu'>don</label>
					<input type='checkbox' data-column='fri' id='id_fri' class='custom' data-widget='basic.checkbox' data-mini='true'> <label id='id_fri_lab' for='id_fri'>vri</label>
					<input type='checkbox' data-column='sat' id='id_sat' class='custom' data-widget='basic.checkbox' data-mini='true'> <label id='id_sat_lab' for='id_sat'>zat</label>
					<input type='checkbox' data-column='sun' id='id_sun' class='custom' data-widget='basic.checkbox' data-mini='true'> <label id='id_sun_lab' for='id_sun'>zon</label>
				</div>
			</div>
			<div class='alarm_items'>
				<select multiple='multiple' data-column='item' data-native-menu='false'>
					<option>Select items</option>
				</select>
			</div>
			<div class='alarm_action'>
				<select data-column='action' data-native-menu='false'>
					<option>Select action</option>
				</select>
			</div>
		</div>";
	
}

?>