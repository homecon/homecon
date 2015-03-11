<?php
	session_start();
	include('../data/mysql.php');
	
	ini_set('display_errors',1);
	ini_set('display_startup_errors',1);
	error_reporting(-1);
	
	set_time_limit(600);  // 10 minutes maximum execution time
	
	if($_SESSION['user_id']>0){
	
		$page = $_POST['page'];
		$content = $_POST['model'];
		
		$content = str_replace('%t',"\t",$content);
		$content = str_replace('%n',"\n",$content);
		
		echo $content;
		file_put_contents("../pages/$page.html",$content);
		//exit;

	}
?>