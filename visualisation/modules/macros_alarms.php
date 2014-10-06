<?php
function add_alarm($sectionid,$text,$itemlist,$actionlist){
	global $page;
	global $web;
	
	$page = explode('/',$page);
	$page = end($page);
	
	$itemlist = explode(',',$itemlist);
	$actionlist = explode(',',$actionlist);
	
	
	
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
		<div class='alarm_container'>
			<div id='alarms_$sectionid'>";

	// find alarms with $sectionid in mysql and cycle through them
	$result = mysql_query("SELECT * FROM alarms WHERE sectionid = ".$sectionid);
	while($row = mysql_fetch_array($result)){
		echo_alarm($sectionid,$text,$itemlist,$actionlist,$row);
	}
	echo "
				</div>
					<a class='add' id='add_alarm_$sectionid' class='add_alarm' data-role='button'>wekker toevoegen</a>
				</div>
		
				<script>
					$(document).ready(function(){
					  $('#add_alarm_$sectionid').click(function(){
						$.post(
						  'requests/alarm_add.php',
						  {sectionid: $sectionid},
						  function(result){
							$('#alarms_$sectionid').html(result).trigger('create');
						  }
						);
					  });
					});
				</script>
		";
	
}

function echo_alarm($sectionid,$text,$itemlist,$actionlist,$row){
	global $page;
	global $web;
	
		// create id's
		$id = $row['id'];
		$id_alarm = $page ."_alarm".$id;
		$id_time = $page ."_alarm".$id ."_time";

		$id_sunrise = $page ."_alarm". $id."_sunrise";
		$id_sunset = $page ."_alarm". $id."_sunset";
		
		$id_mon = $page ."_alarm". $id."_maa";
		$id_tue = $page ."_alarm". $id."_din";
		$id_wed = $page ."_alarm". $id."_woe";
		$id_thu = $page ."_alarm". $id."_don";
		$id_fri	= $page ."_alarm". $id."_vri";
		$id_sat = $page ."_alarm". $id."_zat";
		$id_sun = $page ."_alarm". $id."_zon";
	
		$iditemselect =  $page ."_alarm". $id."_itemselect";
		$idactionselect =  $page ."_alarm". $id."_actionselect";
	
	
		// parse mysql data
		$str_mon = "";
		$str_tue = "";
		$str_wed = "";
		$str_thu = "";
		$str_fri = "";
		$str_sat = "";
		$str_sun = "";
		
		$str_time = "00:00";
		
		$str_sunrise = "";
		$str_sunset = "";
	
		if($row['mon']){
			$str_mon = "checked";
		}
		if($row['tue']){
			$str_tue = "checked";
		}
		if($row['wed']){
			$str_wed = "checked";
		}
		if($row['thu']){
			$str_thu = "checked";
		}
		if($row['fri']){
			$str_fri = "checked";
		}
		if($row['sat']){
			$str_sat = "checked";
		}
		if($row['sun']){
			$str_sun = "checked";
		}
		if($row['sunrise']){
			$str_sunrise = "checked";
		}
		if($row['sunset']){
			$str_sunset = "checked";
		}
	
		// parse items and actions
		$items = explode(',',$row['item']);
		$actions = $row['action'];

		// parse time
		$str_time = sprintf('%02d', $row['hour']).":".sprintf('%02d', $row['minute']);
		
	
		// display individual alarm controls
		echo "
			<div class='alarm' id='alarm_$id'>
				<input type='time' class='alarm_time' name='$id_time' id='$id_time' value='$str_time'>
				<h1>$text</h1>
				<a class='delete' href='index.php?web=$web&page=pages/$page&delete_section=$sectionid&delete_alarm=$id'><img src=icons/ws/control_x.png></a>
				<div class='days'>
					<div data-role='controlgroup' data-type='horizontal'>
						<input type='checkbox' class='mon' name='$id_mon' id='$id_mon' class='custom' data-widget='basic.checkbox' data-mini='true' $str_mon>
						<label for='$id_mon'>maa</label>
					 
						<input type='checkbox' class='tue' name='$id_tue' id='$id_tue' class='custom' data-widget='basic.checkbox' data-mini='true' $str_tue>
						<label for='$id_tue'>din</label>
					 
						<input type='checkbox' class='wed' name='$id_wed' id='$id_wed' class='custom' data-widget='basic.checkbox' data-mini='true' $str_wed> 
						<label for='$id_wed'>woe</label>
						
						<input type='checkbox' class='thu' name='$id_thu' id='$id_thu' class='custom' data-widget='basic.checkbox' data-mini='true' $str_thu>
						<label for='$id_thu'>don</label>
						
						<input type='checkbox' class='fri' name='$id_fri' id='$id_fri' class='custom' data-widget='basic.checkbox' data-mini='true' $str_fri>
						<label for='$id_fri'>vri</label>
						
						<input type='checkbox' class='sat' name='$id_sat' id='$id_sat' class='custom' data-widget='basic.checkbox' data-mini='true' $str_sat>
						<label for='$id_sat'>zat</label>
						
						<input type='checkbox' class='sun' name='$id_sun' id='$id_sun' class='custom' data-widget='basic.checkbox' data-mini='true' $str_sun>
						<label for='$id_sun'>zon</label>
					</div>
				</div>
				<div class='alarm_items'>
					<select multiple='multiple' class='alarm_item' name='$iditemselect' id='$iditemselect' data-native-menu='false'>
						<option>Select items</option>";
						
		for($i=0;$i<count($itemlist);$i++){
		    $itemselected = "";
			$item = $itemlist[$i];
			
			if(in_array($item,$items)){
				$itemselected =  'selected=selected';
			}
			echo "
						<option $itemselected value='$item'>$item</option>";
		}
		
		echo "		
					</select>
				</div>
				<div class='alarm_action'>
					<select name='$idactionselect' class='alarm_action' id='$idactionselect' data-native-menu='false'>
						<option>Select action</option>";
						
		for($i=0;$i<count($actionlist);$i++){
		    $actionselected = "";
			$action = $actionlist[$i];
			
			if(strcmp($action,$actions)==0){
				$actionselected =  'selected=selected';
			}
			echo "
						<option $actionselected value='$action'>$action</option>";
		}
		
		echo "		
					</select>
				</div>
			</div>";
	
}

?>