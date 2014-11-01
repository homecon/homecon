<?php
	session_start();
	include('../data/mysql.php');

	if($_SESSION['userid']>0){
		
		$table = $_POST['table'];

		// name
		$result = mysql_query("SELECT name FROM measurements_legend");
		$content = 'timestamp';
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

		
		
		// prepare data query
		$query = "SELECT * FROM $table WHERE time >='1414568100' AND time < '1414646560' ORDER BY time,signal_id";
		
		// if(strcmp("",$_POST['startdate'])==0 && strcmp("",$_POST['enddate'])==0){
			// $query = "SELECT * FROM $table ORDER BY time,signal_id";
		// }
		// elseif(strcmp("",$_POST['startdate'])==0){
			// $query = "SELECT * FROM $table WHERE time<=".strtotime($_POST['enddate'])." ORDER BY time,signal_id";
			// $startdate = '_'.'start';
			// $enddate   = '_'.$_POST['enddate'];
		// }
		// elseif(strcmp("",$_POST['enddate'])==0){
			// $query = "SELECT * FROM $table WHERE time>=".strtotime($_POST['startdate'])." ORDER BY time,signal_id";
			// $startdate = '_'.$_POST['startdate'];
			// $enddate   = '_'.'end';
		// }
		// else{
			// $query = "SELECT * FROM $table WHERE time>=".strtotime($_POST['startdate'])." AND time<=".strtotime($_POST['enddate'])." ORDER BY time,signal_id";
			// $startdate = '_'.$_POST['startdate'];
			// $enddate   = '_'.$_POST['enddate'];
		// }
		
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
				if($count<$row['signal_id']){
					$content .= ",";
				}

			}
			$content .= ",".$row['value'];
		}
		
		
			
			
		header('Content-Description: File Transfer');
		header('Content-Type: application/octet-stream');
		header('Content-disposition: attachment; filename=knxcontrol_measurements'.str_replace('-','',$startdate ).str_replace('-','',$enddate).'.csv');
		header('Content-Length: '.strlen($content));
		header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
		header('Expires: 0');
		header('Pragma: public');
		echo $content;
		//exit;

	}
?>