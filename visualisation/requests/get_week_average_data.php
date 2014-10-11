<?php
date_default_timezone_set('Europe/Brussels');

include('../data/mysql.php');

$signal_str = $_GET['signal'];
$signals = explode(',',$signal_str);

date_default_timezone_set("UTC");
$after_time = time()-366*24*3600;



$table = "measurements_weekaverage";

ini_set('display_startup_errors',1);
ini_set('display_errors',1);
error_reporting(-1);

for($i = 0; $i < count($signals); $i++){

	echo "signal";
	
	$result = mysql_query("SELECT * FROM measurements_legend WHERE ID = ".$signals[$i]);
	while($row = mysql_fetch_array($result)) {

		echo $row['name'].";";
		echo $row['unit'].";";
	}
			
	// return the sum of values in the table between given times
	$result = mysql_query("SELECT week, signal".$signals[$i]." FROM $table WHERE timestamp > $after_time");
	while($row = mysql_fetch_array($result)) {
		echo $row['week'] . "," . $row['signal'.$signals[$i]]. ";";
	}
}

?>