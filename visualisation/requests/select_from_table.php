<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['user_id']>0){
		$table = $_POST['table'];
		$column = $_POST['column'];
		$where = $_POST['where'];
		
		
		$query = "SELECT $column FROM $table WHERE $where";
		$result = mysql_query($query) or die('MySQL Error: ' . mysql_error());

		$rows = array();
		while($row=mysql_fetch_array($result)){
			$rows[] = $row;
		}
		
		echo json_encode($rows);
	}
?>