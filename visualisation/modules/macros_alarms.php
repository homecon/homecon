<?php
function add_alarm($sectionid,$text,$itemlist,$actionlist){
	global $page;
	global $web;
	
	$page = explode('/',$page);
	$page = end($page);
	
	//$itemlist = explode(',',$itemlist);
	//$actionlist = explode(',',$actionlist);

	//$itemlist = "['".str_replace(",","','",$itemlist)."']";
	//$actionlist = "['".str_replace(",","','",$actionlist)."']";
	
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
		<div class='alarm_container' id='alarm_section$sectionid' data-id=$sectionid>
			<div id='alarm_add$sectionid'>
				<a class='add' class='add_alarm' data-role='button'>wekker toevoegen</a>
			</div>
		</div>";
		
	// find alarms with $sectionid in mysql and cycle through them
	$result = mysql_query("SELECT * FROM alarms WHERE sectionid = ".$sectionid);
	
	while($row = mysql_fetch_array($result)){
	
		$id = $row['id'];
		$items = "['".str_replace(",","','",$row['item'])."']";
		$actions = "['".str_replace(",","','",$row['action'])."']";
		
		echo " 
		<script>
			$(document).on('pagecreate',function(event){
				var values = {id: ".$row['id'].", hour: ".$row['hour'].", minute: ".$row['minute'].", mon: ".$row['mon'].", tue: ".$row['tue'].", wed: ".$row['wed'].", thu: ".$row['thu'].", fri: ".$row['fri'].", sat: ".$row['sat'].", sun: ".$row['sun'].", item: '".$row['item']."', action: '".$row['action']."' };
				display_alarm($sectionid,values);
			});
		</script>";
	}

		
	// echo a hidden template for the alarm
	echo "
			<div class='alarm' id='alarm_template$sectionid' data-id='id' style='display:none' data-itemlist='$itemlist' data-actionlist='$actionlist'>
				<input type='time' data-column='time' value='12:00'>
				<h1></h1>
				<a class='delete'><img src='icons/ws/control_x.png'></a>
				<div class='days'>
					<div data-role='controlgroup' data-type='horizontal'>
						<input type='checkbox' data-column='mon' id='id_mon' class='custom' data-widget='basic.checkbox' data-mini='true' checked> <label id='id_mon_lab' for='id_mon'>maa</label>
						<input type='checkbox' data-column='tue' id='id_tue' class='custom' data-widget='basic.checkbox' data-mini='true' checked> <label id='id_tue_lab' for='id_tue'>din</label>
						<input type='checkbox' data-column='wed' id='id_wed' class='custom' data-widget='basic.checkbox' data-mini='true' checked> <label id='id_wed_lab' for='id_wed'>woe</label>
						<input type='checkbox' data-column='thu' id='id_thu' class='custom' data-widget='basic.checkbox' data-mini='true' checked> <label id='id_thu_lab' for='id_thu'>don</label>
						<input type='checkbox' data-column='fri' id='id_fri' class='custom' data-widget='basic.checkbox' data-mini='true' checked> <label id='id_fri_lab' for='id_fri'>vri</label>
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