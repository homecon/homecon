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
		<title>KNX control</title>

		<meta charset='utf-8'/>
		<meta name='viewport' content='width=device-width, user-scalable=yes, initial-scale=1, maximum-scale=1.3, minimum-scale=1' />
		<meta name='mobile-web-app-capable' content='yes' />
		<meta name='apple-mobile-web-app-capable' content='yes' />
		<meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
		<meta http-equiv='expires' content='0' />

		<link rel='icon' href='favicon.png'/>
		<link rel='apple-touch-icon' href='favicon.png' />
		<link rel='icon' href='favicon.ico' type='image/x-icon' />

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
		<script type='text/javascript' src='js/widgets.js'></script>
		<script type='text/javascript' src='js/view.js'></script>
		<script type='text/javascript' src='js/pagebuilder.js'></script>
				
		<link rel='stylesheet' type='text/css' href='css/layout.css'/>
		<link rel='stylesheet' type='text/css' href='css/widget.css'/>
	</head>
	<body>

<?php
	include("data/authentication.php");
	
	if($_SESSION['user_id']>0){
	
		include("pages/pages.php");
		include("pages/menu.php");
		include("data/header.php");
		include("data/modules.php");
		include("data/templates.php");
		
	}
	else{
		include("data/login.php");
	}
?>		

	</body>
</html>
