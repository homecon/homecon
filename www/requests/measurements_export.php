<?php
	include('../requests/mysql.php');
	
	//ini_set('display_errors',1);
	//ini_set('display_startup_errors',1);
	//error_reporting(-1);
	
	set_time_limit(3600);  // 1 hour maximum execution time
	
	if(1){
	
		$path = 'exportfiles/';
		$table = $_GET['table'];

		// parse dates 
		if(strcmp("",$_GET['startdate'])==0 && strcmp("",$_GET['enddate'])==0){
				$timequery = '';
				$startdate = '';
				$enddate = '';
		}
		elseif(strcmp("",$_GET['startdate'])==0){
			$timequery = " AND time<".strtotime($_GET['enddate']);
			$startdate = '_'.'start';
			$enddate   = '_'.$_GET['enddate'];
		}
		elseif(strcmp("",$_GET['enddate'])==0){
			$timequery = " AND time>=".strtotime($_GET['startdate']);
			$startdate = '_'.$_GET['startdate'];
			$enddate   = '_'.'end';
		}
		else{
			$timequery = " AND time>=".strtotime($_GET['startdate'])." AND time<".strtotime($_GET['enddate']);
			$startdate = '_'.$_GET['startdate'];
			$enddate   = '_'.$_GET['enddate'];
		}
			
		$filenames = [];	
		$zipname = $path.'homecon_measurements'.str_replace('-','',$startdate ).str_replace('-','',$enddate).'.zip';

		// create a zip file
		$zip = new ZipArchive;
		if ($zip->open($zipname, ZipArchive::CREATE)!==TRUE) {
    		exit("cannot open <$zipname>\n");
		}

		// run through all sensors found in the legend
		$result = mysql_query("SELECT * FROM measurements_legend");
		while($signal = mysql_fetch_array($result)){
		
			$filename = $signal['item'].'.csv';
			
			// start creating new content and add a header
			$content = '';
			$content .= 'HEADER'.PHP_EOL;
			$content .= 'item: '.$signal['item'].PHP_EOL;
			$content .= 'name: '.$signal['name'].PHP_EOL;
			$content .= 'quantity: '.$signal['quantity'].PHP_EOL;
			$content .= 'unit: '.$signal['unit'].PHP_EOL;
			$content .= 'description: '.$signal['description'].PHP_EOL;
			//$content .= 'starttime: '.strtotime($_GET['startdate']).PHP_EOL;
			//$content .= 'endtime: '.strtotime($_GET['enddate']).PHP_EOL;
			
			// prepare data query
			$query = "SELECT * FROM $table WHERE signal_id=".$signal['id'].$timequery;
			
			//$content .= 'query: '.$query.PHP_EOL;


			$content .= PHP_EOL;
			$content .= 'DATA'.PHP_EOL;
			$content .= 'unixtime,value'.PHP_EOL;
			
			// write data
			$data_result = mysql_query($query);
			while($row = mysql_fetch_array($data_result)){
				$content .= $row['time'].','.$row['value'].PHP_EOL;
			}
			
			// create a temp file
			//$filenames[] = $path.$filename;
			//file_put_contents( $filename , $content ) or die ("Unable to create file!");
			$zip->addFromString($filename, $content);
		}
		
		$zip->close();
		
		// download the zip file
		header('Content-Type: application/zip');
		header('Content-disposition: attachment; filename='.$zipname);
		header('Content-Length: ' . filesize($zipname));
		readfile($zipname);

		// delete the zip file
		unlink($zipname);
	}
?>
