<?php
	session_start();
	include('../data/mysql.php');
	
	ini_set('display_errors',1);
	ini_set('display_startup_errors',1);
	error_reporting(-1);
	
	set_time_limit(600);  // 10 minutes maximum execution time
	
	if($_SESSION['user_id']>0){
		$content = '';
		
		$content .= $_GET['model'];
		$date = date("Ymd_His");
		header('content-Description: File Transfer');
		header('content-Type: application/octet-stream');
		header('content-disposition: attachment; filename=knxcontrol_pagebuilder_'.$date.'.txt');
		header('content-Length: '.strlen($content));
		header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
		header('Expires: 0');
		header('Pragma: public');
		
		echo $content;
		//exit;

	}
?>