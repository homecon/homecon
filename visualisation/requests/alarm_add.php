<?php

	include('../data/mysql.php');
	include('../modules/macros_alarms.php');
	
	$sectionid = $_POST['sectionid'];

	// add alarm to the mysql database
	$query = "INSERT INTO alarms (sectionid,hour,minute,mon,tue,wed,thu,fri,sat,sun) VALUES ($sectionid,12,0,1,1,1,1,1,0,0)";
	$result = mysql_query($query) or die('Error: ' . mysql_error());
		
	// find alarms with $sectionid in mysql and cycle through them
	$result = mysql_query("SELECT * FROM alarms WHERE sectionid = ".$sectionid);
	while($row = mysql_fetch_array($result)){
		echo_alarm($sectionid,"","","",$row);
	}


?>