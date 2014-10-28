<?php
date_default_timezone_set('Europe/Brussels');

include('../data/mysql.php');

$signal_str = $_GET['signal'];
$signals = explode(',',$signal_str);

date_default_timezone_set("UTC");
$after_date = time()-2*24*3600;

$table = "measurements";

ini_set('display_startup_errors',1);
ini_set('display_errors',1);
error_reporting(-1);

for($i = 0; $i < count($signals); $i++){

	echo "signal";
	
	$result = mysql_query("SELECT * FROM measurements_legend WHERE id = ".$signals[$i]);
	while($row = mysql_fetch_array($result)) {

		echo $row['name'].";";
		echo $row['unit'].";";
	}
	
	
	$result = mysql_query("SELECT time, value FROM $table WHERE signal_id = ".$signals[$i]." AND time > $after_date");
	while($row = mysql_fetch_array($result)) {
		if(!is_null($row['value'])){
			echo date('Y-m-d H:i:s',$row['time']). "," . $row['value']. ";";
		}
		else{
			echo date('Y-m-d H:i:s',$row['time']). ",null;";
		}
	}
}
?>