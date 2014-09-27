<?php

	include('./pages/mysql.php'); 
	
	// create and download the data
	if(array_key_exists('export',$_POST)){

		// column names
		$result = mysql_query("SELECT * FROM measurements_legend");
		$content = 'timestamp';
		$count = 0;
		while($row = mysql_fetch_array($result)){
			$content .= ','.$row['name'];
			$count++;
		}
		$content .= PHP_EOL;
		
		// units
		$result = mysql_query("SELECT * FROM measurements_legend");
		$content .= 's';
		while($row = mysql_fetch_array($result)){
			$content .= ','.$row['unit'];
		}
		$content .= PHP_EOL;
		
		//data
		if(strcmp("",$_POST['startdate'])==0 && strcmp("",$_POST['enddate'])==0){
			$query = "SELECT * FROM measurements";
		}
		elseif(strcmp("",$_POST['startdate'])==0){
			$query = "SELECT * FROM measurements WHERE time<=".strtotime($_POST['enddate'])."";
			$startdate = '_'.'start';
			$enddate   = '_'.$_POST['enddate'];
		}
		elseif(strcmp("",$_POST['enddate'])==0){
			$query = "SELECT * FROM measurements WHERE time>=".strtotime($_POST['startdate'])."";
			$startdate = '_'.$_POST['startdate'];
			$enddate   = '_'.'end';
		}
		else{
			$query = "SELECT * FROM measurements WHERE time>=".strtotime($_POST['startdate'])." AND time<=".strtotime($_POST['enddate'])."";
			$startdate = '_'.$_POST['startdate'];
			$enddate   = '_'.$_POST['enddate'];
		}
		$result = mysql_query($query);
		while($row = mysql_fetch_array($result)){
			$content .= $row['time'];
			for($i=1;$i<$count;$i++){
				 $content .= ",".$row['signal'.$i];
			}
			$content .= PHP_EOL;
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