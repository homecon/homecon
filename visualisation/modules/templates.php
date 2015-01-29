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
		
		<link rel='stylesheet' type='text/css' href='css/layout.css'/>
		<link rel='stylesheet' type='text/css' href='css/widget.css'/>
	</head>
	<body>



		<div id='templates' data-role='page' data-theme='a'>
				
				
			<div class='alarm' data-id='0' data-section=''>
				<input type='time' data-column='time' value='12:00'>
				<h1></h1>
				<a class='delete'><img src='icons/ws/control_x.png'></a>
				<div class='days'>
					<div data-role='controlgroup' data-type='horizontal'>
						<input type='checkbox' data-field='mon' id='mon_0' class='custom' data-mini='true' checked> <label for='mon_0'>maa</label>
						<input type='checkbox' data-field='tue' id='tue_0' class='custom' data-mini='true' checked> <label for='tue_0'>din</label>
						<input type='checkbox' data-field='wed' id='wed_0' class='custom' data-mini='true' checked> <label for='wed_0'>woe</label>
						<input type='checkbox' data-field='thu' id='thu_0' class='custom' data-mini='true' checked> <label for='thu_0'>don</label>
						<input type='checkbox' data-field='fri' id='fri_0' class='custom' data-mini='true' checked> <label for='fri_0'>vri</label>
						<input type='checkbox' data-field='sat' id='sat_0' class='custom' data-mini='true'> <label id='id_sat_lab' for='sat_0'>zat</label>
						<input type='checkbox' data-field='sun' id='sun_0' class='custom' data-mini='true'> <label id='id_sun_lab' for='sun_0'>zon</label>
					</div>
				</div>
				<div class='alarm_action'>
					<select data-field='action' data-native-menu='false'>
						<option>Select action</option>
					</select>
				</div>
			</div>
			
			<div class='alarm_action_def' data-id=0>
				<a class='delete' href='#'><img src=icons/ws/control_x.png></a>
				<input type='text'  data-field='name'       placeholder='name'>
				<input type='text'  data-field='sectionid'  placeholder='section id filter'>
				<div class='alarm_action_def_action'>
					<input type='number'  data-field='delay1'   placeholder='delay 1' value='0'>
					<input type='text'    data-field='item1'    placeholder='item 1'>
					<input type='text'    data-field='value1'   placeholder='value 1'>
				</div>
				<div class='alarm_action_def_action'>
					<input type='number'  data-field='delay2'   placeholder='delay 2'>
					<input type='text'    data-field='item2'    placeholder='item 2'>
					<input type='text'    data-field='value2'   placeholder='value 2'>
				</div>
				<div class='alarm_action_def_action'>
					<input type='number'  data-field='delay3'   placeholder='delay 3'>
					<input type='text'    data-field='item3'    placeholder='item 3'>
					<input type='text'    data-field='value3'   placeholder='value 3'>
				</div>
				<div class='alarm_action_def_action'>
					<input type='number'  data-field='delay4'   placeholder='delay 4'>
					<input type='text'    data-field='item4'    placeholder='item 4'>
					<input type='text'    data-field='value4'   placeholder='value 4'>
				</div>
				<div class='alarm_action_def_action'>
					<input type='number'  data-field='delay5'   placeholder='delay 5'>
					<input type='text'    data-field='item5'    placeholder='item 5'>
					<input type='text'    data-field='value5'   placeholder='value 5'>
				</div>
			</div>
			
		<div>
	</body>
</html>