<?php
	include('../requests/mysql.php');
	
	if(1){
		
		$table = $_POST['table'];
		$column = $_POST['column'];
		$value = $_POST['value'];
		$id = $_POST['id'];
		
		
		// convert column, value pairs to column=value set with encryption
		$set = $column."=".md5($value);
		$where = "id=".$id;
		
		$query = "UPDATE $table SET $set WHERE $where";
		$result = mysql_query($query) or die('MySQL Error: ' . mysql_error());
		echo $result;
	}
?>
