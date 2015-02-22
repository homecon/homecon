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
		
		$value = $_POST['value'];
		$where = $_POST['where'];
		
		$column = explode(';', $column);
		$value  = explode(';', $value);
		
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