<?php
	session_start();
	
	// functions
	include('data/mysql.php');
	include('data/authentication.php');
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
	
	if($_SESSION['userid']>0){
		// get ip and port from mysql
		$result = mysql_query("SELECT * FROM data WHERE id = 1");
		$data = mysql_fetch_array($result);
		if($web){
			$smarthome_adress = $data['web_ip'];
			$smarthome_port = $data['web_port'];
		}
		else{
			$smarthome_adress = $data['ip'];
			$smarthome_port = $data['port'];
		}	
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
		<script src='jquery/jquery-1.8.3.js'></script>
		<script src='jquery/jquery.mobile-1.3.2.js'></script>
		<link rel='stylesheet' href='jquery/jquery.mobile-1.3.2.css'>
		
		<!-- highcharts -->
		<script type='text/javascript' src='js/highstock.js' ></script>
		<script src='js/highchartstheme.js'></script>
		
		<!-- smarthome.py -->
		<script type='text/javascript' src='js/io_smarthome.py.js'></script>
		<script type='text/javascript' src='js/widget.js'></script>
		
		<!-- knxcontrol -->
		<script type='text/javascript' src='js/menu.js'></script>
		<script type='text/javascript' src='js/alarms.js'></script>
		<script type='text/javascript' src='js/measurements.js'></script>
		<script type='text/javascript' src='js/charts.js'></script>
		<link rel='stylesheet' type='text/css' href='css/layout.css'/>
		<link rel='stylesheet' type='text/css' href='css/widget.css'/>
	</head>
	<body>
		<script type='text/javascript'>
			io.init('<?php echo $smarthome_adress; ?>', '<?php echo $smarthome_port; ?>');
		
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
		</script>
	
	
		<div id='page' data-role='page' data-theme='a'>
			<div data-role='header' id='header' data-position='fixed' data-tap-toggle='false'>
				<?php include("modules/header.php"); ?>
			</div>
			<div data-role='panel' id='menu' class='<?php echo $page_class;?>' data-theme='a' data-display='overlay' data-position='left' data-position-fixed='true' data-dismissable='false'>
				<?php include("pages/menu.php"); ?>
			</div>
			<div data-role='content' id='content' class='<?php echo $page_class;?>'>
				<?php include("$page.php"); ?>
			</div>
		</div>

		
	</body>
</html>

<?php 
	}
	elseif($page=='modules/set_cookie'){
		include("modules/set_cookie.php");
	}
	else{
		echo "No permission!";
		echo "<meta http-equiv='refresh' content='0; URL=index.php?web=$web&page=modules/set_cookie'>";
	}
?>
	
