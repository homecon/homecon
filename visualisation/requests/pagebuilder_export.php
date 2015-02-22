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