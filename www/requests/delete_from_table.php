<?php
	include('../requests/mysql.php');

	if(1){
	
		$table = $_POST['table'];
		$where = $_POST['where'];

		$query = "DELETE FROM $table WHERE $where";
		$result = mysql_query($query) or die('MySQL Error: ' . mysql_error());
		
		echo $result;
	}
?>
