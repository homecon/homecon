<?php

	include('../data/mysql.php');

	$id = $_POST['id'];
	$time = $_POST['time'];
	
	$mon = $_POST['mon'];
	$tue = $_POST['tue'];
	$wed = $_POST['wed'];
	$thu = $_POST['thu'];
	$fri = $_POST['fri'];
	$sat = $_POST['sat'];
	$sun = $_POST['sun'];
	
	$item = $_POST['item'];
	$action = $_POST['action'];
	
	
	// convert arrays to comma seperated list
	if(is_array($item)){
		$item = implode(',',$item);
	}
	if(is_array($action)){
		$action = implode(',',$action);
	}
	
	// convert time
	$time = explode(':',$time);
	$hour = intval($time[0]);
	$minute = intval($time[1]);
	
	
	echo $id."<br>";
	echo $hour."<br>";
	echo $minute."<br>";
	echo $mon."<br>";
	echo $tue."<br>";
	echo $wed."<br>";
	echo $thu."<br>";
	echo $item."<br>";
	echo $action."<br>";
	
	
	$query = "UPDATE alarms SET hour=$hour, minute=$minute, mon=$mon, tue=$tue , wed=$wed , thu=$thu , fri=$fri , sat=$sat, sun=$sun, item='$item', action='$action' WHERE id=$id";
	echo $query;
	$result = mysql_query($query) or die('Error: ' . mysql_error());

?>