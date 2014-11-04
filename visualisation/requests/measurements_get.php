<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['userid']>0){
		date_default_timezone_set('Europe/Brussels');

		// parse the table and time scale
		date_default_timezone_set("UTC");
		if($_GET['scale']=='quarter'){
			$after_date = time()-2*24*3600;
			$table = "measurements_quarterhouraverage";
		}
		elseif($_GET['scale']=='week'){
			$after_date = time()-365*24*3600;
			$table = "measurements_weekaverage";
		}
		elseif($_GET['scale']=='month'){
			$after_date = time()-365*24*3600;
			$table = "measurements_monthaverage";
		}
		else{
			$after_date = time()-2*24*3600;
			$table = "measurements";
		}
		
		// parse the signal
		$signal_str = $_GET['signal'];
		
		// start creating the json string
		echo '{';
		
		// name and unit
		$result = mysql_query("SELECT * FROM measurements_legend WHERE id = ".$signal_str);
		$row = mysql_fetch_array($result);
		
		echo '"name":"'.$row['name'].'", "unit":"'.$row['unit'].'", "quantity":"'.$row['quantity'].'", "description":"'.$row['description'].'", ';
		echo '"series":{"name":"'.$row['name'].'", "data":[';
		
		
		$result = mysql_query("SELECT time, value FROM $table WHERE signal_id = ".$signal_str." AND time > $after_date");
		$count = 0;
		while($row = mysql_fetch_array($result)) {
			// do not echo a comma before the first entry
			if($count==0){
				$count++;
			}
			else{
				echo ",";
			}
			
			// echo the actual data
			if(!is_null($row['value'])){
				echo '{"time":'.$row['time'].'000, "value":'.$row['value'].'}';
			}
			else{
				echo '{"time":'.$row['time'].'000, "value":"null"}';
			}
		}

		echo "]}}";
	}
	
?>