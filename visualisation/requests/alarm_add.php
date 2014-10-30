<?php
	
	include('../data/mysql.php');
	
	if($_SESSION['userid']>0){
		$sectionid = $_POST['sectionid'];

		// add alarm to the mysql database
		$query = "INSERT INTO alarms (sectionid,hour,minute,mon,tue,wed,thu,fri,sat,sun) VALUES ($sectionid,12,0,1,1,1,1,1,0,0)";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
			
			
		// get the id of the last added element to return to jquery
		echo mysql_insert_id();
	}

?>