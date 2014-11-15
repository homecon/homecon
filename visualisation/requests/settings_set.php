<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['userid']>0){
	
		$webip = $_POST['webip'];
		$webport = $_POST['webport'];
		
		$query = "UPDATE data SET web_ip='$webip', web_port=$webport WHERE id=1";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
		
	}
?>