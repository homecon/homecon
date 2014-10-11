<?php

	include('../data/mysql.php');

	$id = $_POST['id'];
	$column = $_POST['column'];
	$value = $_POST['value'];
	
	
	
	// convert value array to comma seperated list
	if(is_array($value)){
		$value = implode(',',$value);
	}
	
	// used for debugging
	echo "$id, $column, $value";
	
	
	if(strcmp($column,'time')==0){
		// if column is time
		$list = explode(':',$value);

		$hour = intval($list[0]);
		$minute = intval($list[1]);
		
		$query = "UPDATE alarms SET hour=$hour, minute=$minute WHERE id=$id";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
	}
	elseif(strcmp($column,'item')==0 || strcmp($column,'action')==0){
		// if column is item or action
		$query = "UPDATE alarms SET $column='$value' WHERE id=$id";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
	}
	else{
		// else column is a day
		$query = "UPDATE alarms SET $column=$value WHERE id=$id";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
	}

?>