<?php

	include('../data/mysql.php');

	// add alarm to the mysql database
	$query = "INSERT INTO alarm_actions";
	$result = mysql_query($query) or die('Error: ' . mysql_error());
		
		
	// get the id of the last added element to return to jquery
	echo mysql_insert_id();


?>