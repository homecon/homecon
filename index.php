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
	
	// error reporting for debugging
	ini_set('display_startup_errors',1);
	ini_set('display_errors',1);
	error_reporting(-1);
?>

<!DOCTYPE html>
<html>
	<head>
		<title>HomeCon</title>

		<meta charset='utf-8'/>
		<meta name='viewport' content='width=device-width, user-scalable=yes, initial-scale=1, maximum-scale=1.3, minimum-scale=1' />
		<meta name='mobile-web-app-capable' content='yes' />
		<meta name='apple-mobile-web-app-capable' content='yes' />
		<meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
		<meta http-equiv='expires' content='0' />

		<link rel='icon' href='icons/favicon.png'/>
		<link rel='apple-touch-icon' href='icons/favicon.png' />

		<!-- jquery mobile -->
		<script src='lib/jquery-1.11.0.min.js'></script>
		<script src='lib/jquery.mobile-1.4.5.min.js'></script>
		<link rel='stylesheet' href='lib/jquery.mobile-1.4.5.min.css'/>
		<link rel='stylesheet' href='lib/jquery.mobile.icons-1.4.5.min.css'/>
		
		<!-- highcharts -->
		<script type='text/javascript' src='lib/highstock.js' ></script>
		<script src='lib/highchartstheme.js'></script>
		
		<!-- knxcontrol -->
		<script type='text/javascript' src='js/language_dutch.js'></script>
		<script type='text/javascript' src='js/smarthome.js'></script>
		<script type='text/javascript' src='js/knxcontrol.js'></script>
		<script type='text/javascript' src='js/widgets_base.js'></script>
		<script type='text/javascript' src='js/widgets.js'></script>
		<script type='text/javascript' src='js/view.js'></script>
		<script type='text/javascript' src='js/pagebuilder.js'></script>
				
		<link rel='stylesheet' type='text/css' href='css/layout.css'/>
		<link rel='stylesheet' type='text/css' href='css/widgets_base.css'/>
		<link rel='stylesheet' type='text/css' href='css/widgets.css'/>
	</head>
	<body>

<?php
	include("data/authentication.php");
	
	if($_SESSION['user_id']>0){
	
		include("pages/pages.html");
		include("pages/menu.html");
		include("data/header.html");
		include("data/settings.html");
		include("data/pagebuilder.html");
		
	}
	else{
		include("data/login.php");
	}
?>		

	</body>
</html>
