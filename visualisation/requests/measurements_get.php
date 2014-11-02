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
		
		// parse the signals
		$signal_str = $_GET['signal'];
		$signals = explode(',',$signal_str);


		// start writing signals
		for($i = 0; $i < count($signals); $i++){

			// keyword signal to delimit different signals
			echo "signal";
			
			// name and unit
			$result = mysql_query("SELECT * FROM measurements_legend WHERE id = ".$signals[$i]);
			while($row = mysql_fetch_array($result)) {

				echo $row['name'].";";
				echo $row['unit'].";";
			}
			
			//echo times and values
			$result = mysql_query("SELECT time, value FROM $table WHERE signal_id = ".$signals[$i]." AND time > $after_date");
			while($row = mysql_fetch_array($result)) {
				if(!is_null($row['value'])){
					//echo date('Y-m-d H:i:s',$row['time']). "," . $row['value']. ";";
					echo $row['time']."000,".$row['value'].";";
				}
				else{
					//echo date('Y-m-d H:i:s',$row['time']). ",null;";
					echo $row['time']."000,null;";
				}
			}
		}
	}
?>