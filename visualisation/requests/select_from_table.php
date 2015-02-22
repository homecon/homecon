<!--
    Copyright 2015 Brecht Baeten
    This file is part of KNXControl.

    KNXControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    KNXControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
-->

<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['user_id']>0){
		$table = $_POST['table'];
		$column = $_POST['column'];
		$where = $_POST['where'];
		$orderby = "";
		
		if(array_key_exists('orderby',$_POST)){
			$orderby = " ORDER BY ".$_POST['orderby'];
		}
		
		$query = "SELECT $column FROM $table WHERE $where$orderby";
		$result = mysql_query($query) or die('MySQL Error: ' . mysql_error());

		$rows = array();
		while($row=mysql_fetch_array($result)){
			$rows[] = $row;
		}
		
		echo json_encode($rows);
	}
?>