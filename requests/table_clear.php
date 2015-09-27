<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['userid']>0){

		$table = $_POST['table'];
		echo $table;

		$result = mysql_query("TRUNCATE $table") or die('Error: ' . mysql_error());

	}
?>