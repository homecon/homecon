<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['userid']>0){
		$id = $_POST['id'];
		
		// add alarm to the mysql database
		$query = "DELETE FROM alarm_actions WHERE id=$id";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
	}
?>