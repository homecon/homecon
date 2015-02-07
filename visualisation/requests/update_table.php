<?php
	session_start();
	include('../data/mysql.php');
	
	if($_SESSION['user_id']>0){
		
		$table = $_POST['table'];
		$column = $_POST['column'];
		$value = $_POST['value'];
		$where = $_POST['where'];
		
		$column = explode(',', $column);
		$value  = explode(',', $value);
		
		// convert column, value pairs to column=value set
		$set = array();

		for($i=0;$i<count($column);$i++){
			if(is_string($value[$i])){
				$value[$i] = "'".$value[$i]."'";
			}
			$set[] = $column[$i].'='.$value[$i];
		}
		$set = implode(',',$set);
		
		
		$query = "UPDATE $table SET $set WHERE $where";
		$result = mysql_query($query) or die('MySQL Error: ' . mysql_error());
		echo $result;
	}
?>