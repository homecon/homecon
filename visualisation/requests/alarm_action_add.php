<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['userid']>0){
		// add alarm to the mysql database
		$query = "INSERT INTO alarm_actions (sectionid) VALUES (0)";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
			
			
		// get the id of the last added element to return to jquery
		echo mysql_insert_id();
	}

?>