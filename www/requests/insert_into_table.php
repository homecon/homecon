<?php
	include('../requests/mysql.php');

	if(1){
	
		$table = $_POST['table'];
		$column = $_POST['column'];
		$value = $_POST['value'];
		
		$column = str_replace(';',',', $column);
		$value  = str_replace(';',',', $value);
		
		// insert into the table
		$query = "INSERT INTO $table ($column) VALUES ($value)";
		$result = mysql_query($query) or die('Error: ' . mysql_error());
		
		// return the last row
		$query = "SELECT LAST_INSERT_ID()";
		$result = mysql_query($query) or die('MySQL Error: ' . mysql_error());
		echo json_encode(mysql_fetch_array($result));
	}
?>
