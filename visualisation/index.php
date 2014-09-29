<?php
	// functions
	include('data/mysql.php');
	include('modules/macros_structure.php');
	include('modules/macros_basic.php');
	include('modules/macros_charts.php');
	include('modules/macros_weather.php');
	include('modules/macros_alarms.php');
	include('modules/macros_heating.php');
	
	
	ini_set('display_startup_errors',1);
	ini_set('display_errors',1);
	error_reporting(-1);

	if(array_key_exists('page',$_GET)){
		$page = $_GET['page'];
		$page_class = 'main';
	}
	else{
		$page = 'modules/home';
		$page_class = 'home';
	}
	
	// check if the server is accessed over the internet
	if(array_key_exists('web',$_GET)){
		$web = $_GET['web'];
	}
	else{
		$web = 0;
	}

	// check if the user machine has the required cookie
	$cookie_check = 0;
	if(array_key_exists('knxcontrol_user',$_COOKIE) && array_key_exists('knxcontrol_pass',$_COOKIE)){
		$result = mysql_query("SELECT * FROM users WHERE username = '".$_COOKIE['knxcontrol_user']."'");
		if($user = mysql_fetch_array($result)){
			if(md5($_COOKIE['knxcontrol_pass'])==$user['password']){
				$cookie_check = 1;
			}
		}
	}
	
	if($cookie_check){
		if($web){
			$smarthome_adress = "baeten-gielen.ddns.net";
			$smarthome_port = "9024";
		}
		else{
			$smarthome_adress = "192.168.1.2";
			$smarthome_port = "2424";
		}	

		echo "
<html>
	<head>
		<title>KNX control</title>

		<meta charset='utf-8'/>
		<meta name='viewport' content='width=device-width, user-scalable=yes, initial-scale=1, maximum-scale=1.3, minimum-scale=1' />
		<meta name='apple-mobile-web-app-capable' content='yes' />
		<meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
		<meta http-equiv='expires' content='0' />

		<link rel='icon' href='favicon.png'/>
		<link rel='apple-touch-icon' href='favicon.png' />
		<link rel='icon' href='favicon.ico' type='image/x-icon' />

		<!-- jquery mobile -->
		<script src='http://code.jquery.com/jquery-1.8.3.min.js'></script>
		<script src='http://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.js'></script>
		<link rel='stylesheet' href='http://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.css'>
		
		<!-- highcharts -->
		<script type='text/javascript' src='js/highstock.js' ></script>

		<!-- smarthome.py -->
		<script type='text/javascript' src='js/io_smarthome.py.js'></script>
		<script type='text/javascript' src='js/widget.js'></script>
		<script type='text/javascript' src='js/object.js'></script>
		
		<link rel='stylesheet' type='text/css' href='css/layout.css'/>
		<link rel='stylesheet' type='text/css' href='css/widget.css'/>
	</head>";
	
		echo "	
	<body>";
	
		echo "
		<script type='text/javascript'>
			io.init('$smarthome_adress', '$smarthome_port');
		
			// Do some actions before page is shown
			$(document).on('pagebeforeshow', function () {
				//fx.init();
				//repeater.init();
				widget.prepare();
				//repeater.list();
			});

			// Run the io and all widgets
			$(document).on('pageshow', function () {
				io.run(1);
				// console.log('[io] run');       	
				//notify.display();
				// widget.list();
			});
			

			//$.mobile.page.prototype.options.domCache = true;
		</script>";
	

// basic layout		
		echo "
		<div data-role='page' data-theme='a'>
			<header data-role='header' class='header'>";
			
		include("modules/header.php");

		echo "
			</header>
			<div data-role='content' class='content'>";
			
		include("pages/menu.php");
		
		include("$page.php");
			
		echo "
			</div>";

		echo"
		</div>";
		echo "		
	</body>
</html>";
	}
	elseif($page=='modules/set_cookie'){
		include("modules/set_cookie.php");
	}
	else{
		echo "No permission!";
		echo "<meta http-equiv='refresh' content='0; URL=index.php?web=$web&page=modules/set_cookie'>";
	}
	
?>
	
