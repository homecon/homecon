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
	
	//ini_set('display_errors',1);
	//ini_set('display_startup_errors',1);
	//error_reporting(-1);
	
	set_time_limit(600);  // 10 minutes maximum execution time
	
	if($_SESSION['user_id']>0){
		$content = '';
		
		$table = $_GET['table'];

		// name
		$result = mysql_query("SELECT name FROM measurements_legend");
		$content .= 'timestamp';
		$num_signals = 0;
		while($row = mysql_fetch_array($result)){
			$content .= ','.$row['name'];
			$num_signals++;
		}
		$content .= PHP_EOL;
		
		// quantity
		$result = mysql_query("SELECT quantity FROM measurements_legend");
		$content .= 'time';
		while($row = mysql_fetch_array($result)){
			$content .= ','.$row['quantity'];
		}
		$content .= PHP_EOL;
		
		// unit
		$result = mysql_query("SELECT unit FROM measurements_legend");
		$content .= 's';
		while($row = mysql_fetch_array($result)){
			$content .= ','.$row['unit'];
		}
		$content .= PHP_EOL;
		
		// description
		$result = mysql_query("SELECT description FROM measurements_legend");
		$content .= 'unixtime';
		while($row = mysql_fetch_array($result)){
			$content .= ','.$row['description'];
		}

		
		
		// parse dates and prepare data query
		if(strcmp("",$_GET['startdate'])==0 && strcmp("",$_GET['enddate'])==0){
			$query = "SELECT * FROM $table";
			$startdate = '';
			$enddate = '';
		}
		elseif(strcmp("",$_GET['startdate'])==0){
			$query = "SELECT * FROM $table WHERE time<=".strtotime($_GET['enddate']);
			$startdate = '_'.'start';
			$enddate   = '_'.$_GET['enddate'];
		}
		elseif(strcmp("",$_GET['enddate'])==0){
			$query = "SELECT * FROM $table WHERE time>=".strtotime($_GET['startdate']);
			$startdate = '_'.$_GET['startdate'];
			$enddate   = '_'.'end';
		}
		else{
			$query = "SELECT * FROM $table WHERE time>=".strtotime($_GET['startdate'])." AND time<".strtotime($_GET['enddate']);
			$startdate = '_'.$_GET['startdate'];
			$enddate   = '_'.$_GET['enddate'];
		}

		// rearange data
		$result = mysql_query($query);
		$oldtime = 0;
		$count = 0;
		while($row = mysql_fetch_array($result)){

			if($row['time']>$oldtime){
				// finish the old line
				$content .= PHP_EOL;
				// start a new line
				$content .= $row['time'];
				$oldtime = $row['time'];
			}
			$count++;
			while($row['signal_id']!=$count){

				//reset count
				if($count>=$num_signals){
					$count = 0;
				}
				$count++;
				if($count<=$row['signal_id'] && $count>1){
					$content .= ",";
				}

			}
			$content .= ",".$row['value'];
		}
		
		
		header('content-Description: File Transfer');
		header('content-Type: application/octet-stream');
		header('content-disposition: attachment; filename=knxcontrol_measurements'.str_replace('-','',$startdate ).str_replace('-','',$enddate).'.csv');
		header('content-Length: '.strlen($content));
		header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
		header('Expires: 0');
		header('Pragma: public');
		
		echo $content;
		//exit;

	}
?>