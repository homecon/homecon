<?php
	include('../requests/mysql.php');

	if(1){

		$table = $_POST['table'];
		echo $table;

		$result = mysql_query("TRUNCATE $table") or die('Error: ' . mysql_error());

	}
?>
