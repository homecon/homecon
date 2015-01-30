<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['user_id']>0){
	
		$table = $_POST['table'];
		$where = $_POST['where'];
		
		// parse for user_id
		$where = str_replace('$user_id',$_SESSION['user_id'],$where);
		

		$query = "DELETE FROM $table WHERE $where";
		$result = mysql_query($query) or die('MySQL Error: ' . mysql_error());
		
		echo $result;
	}
?>