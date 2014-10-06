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
	echo $id."<br>";
	echo $column."<br>";
	echo $value."<br>";
	
	
	if(strcmp($column,'time')==0){
		// if collumn is time
		$list = explode(':',$value);

		$hour = intval($list[0]);
		$minute = intval($list[1]);
		
		$query = "UPDATE alarms SET hour=$hour, minute=$minute WHERE id=$id";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
	}
	elseif(strcmp($column,'item')==0 || strcmp($column,'action')==0){
		// if collumn is item or action
		$query = "UPDATE alarms SET $column='$value' WHERE id=$id";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
	}
	else{
		// else
		$query = "UPDATE alarms SET $column=$value WHERE id=$id";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
	}

?>