<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['userid']>0){
		$id = $_POST['id'];
		$column = $_POST['column'];
		$value = $_POST['value'];
		
		
		
		// convert value array to comma seperated list
		if(is_array($value)){
			$value = implode(',',$value);
		}
		
		// used for debugging
		echo "$id, $column, $value";
		
		
		$query = "UPDATE alarm_actions SET $column='$value' WHERE id=$id";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
	}
	
?>