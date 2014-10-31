<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['userid']>0){

		$zone = $_GET['zone'];
		$table = "temperature_setpoints";


		// get all entries and sort them
		$result = mysql_query("SELECT * FROM $table WHERE zone = '$zone' ORDER BY day");
		while($row = mysql_fetch_array($result)) {

			$day[] = $row['day'];
			$hour[] = $row['hour'];
			$minute[] = $row['minute'];
			$setpoint[] = $row['setpoint'];
			
			//construct time array
			$time[] = $row['day'] + $row['hour']/24 + $row['minute']/24/60;
		}

		array_multisort($day,$time,SORT_ASC,$hour,$minute,$setpoint);

		//add an element at the start of the week with the last value
		array_unshift($day,0);
		array_unshift($hour,0);
		array_unshift($minute,0);
		array_unshift($setpoint,end($setpoint));

		array_push($day,7);
		array_push($hour,0);
		array_push($minute,0);
		array_push($setpoint,end($setpoint));

		// add values to create zero order hold and echo
		for($i=0;$i<count($day);$i++){
			if($i>0){
				echo  "2018-01-0".($day[$i]+1)." ".$hour[$i].":".$minute[$i].":00," . $setpoint[$i-1]. ";";
			}
			echo  "2018-01-0".($day[$i]+1)." ".$hour[$i].":".$minute[$i].":00," . $setpoint[$i]. ";";
			
		}
	}
?>