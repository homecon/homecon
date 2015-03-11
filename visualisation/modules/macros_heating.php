<?php
function add_setpoint($zone){
	global $page;
	global $web;
	
	$page = explode('/',$page);
	$page = end($page);
	
	// check if a setpoint must be added
	if(array_key_exists('add_setpoint',$_GET)){
		if($_GET['add_setpoint']==$zone){
			mysql_query("INSERT INTO temperature_setpoints (zone,day,hour,minute,setpoint) VALUES  ('$zone',0,0,0,20)");
		}
	}
	// check if a setpoint must be deleted
	if(array_key_exists('delete_setpoint',$_GET)){
		if($_GET['delete_zone']==$zone){
			$id=$_GET['delete_setpoint'];
			mysql_query("DELETE FROM temperature_setpoints WHERE id=$id");
		}
	}

	echo "
		<div class='setpoint_container'>";

	// display a chart with the setpoints over time
	// $container = $page."_setpoint_".$zone;
	// echo "
			// <div id='$container' class='setpoint_chart'></div>";
	// echo "
			// <script type='text/javascript'>
				// var chart;
				// $(document).ready(function() {
					// var options = {
						// chart: {
							// renderTo: '$container',
							// type: 'line',
							// marginLeft: 45,
							// marginRight: 130,
							// marginBottom: 35,
							// backgroundColor: {
								// linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
								// stops: [
									// [0, 'rgb(76, 76, 76)'],
									// [1, 'rgb(16, 16, 16)']
								// ]
							// },
							// borderWidth: 0,
							// borderRadius: 10,
							// plotBackgroundColor: null,
							// plotShadow: false,
							// plotBorderWidth: 0
						// },
						// title: {
							// text: '$zone temperatuur setpoint',
							// x: -20,
							// style: {
									// color: '#AAAAAA'
							// },
						// },
						// xAxis: {
							// type: 'datetime',
							// gridLineWidth: 1,
							// labels: {
								// align: 'center',
								// x: -3,
								// y: 20,
								// style: {
									// color: '#808080'
								// },
							// },
							// dateTimeLabelFormats: {
								// day: '%a %H:%M'
							// },
							// range: 7 * 24 * 3600 * 1000
						// },
						// yAxis: {
							// title: {
							
								// x: -20,
								// text: 'degC',
								// style: {
									// color: '#808080'
								// }
							// },
							// labels: {
								// x: -20,
								// style: {
									// color: '#808080'
								// }
							// }
						// },
						// tooltip: {
							// xDateFormat: '%a %H:%M',
							// valueDecimals: 1,
							// shared: true
						// },
						// legend: {
							// enabled: false,
						// },
						// rangeSelector : {
							// enabled: false
						// },
						// series: [{
							// marker: {
								// enabled: false
							// },
							// color: '#88AA00'
						// }]
					// }
					// // Load data asynchronously using jQuery. On success, add the data
					// // to the options and initiate the chart.
					// // http://api.jquery.com/jQuery.get/
					
					// setInterval(function () {
						// jQuery.ajax({
							// url:    'requests/get_setpoint.php?zone=$zone',
							// success: function(result) {
								// try {
									// // split the data return into signals and lines lines and parse them
									// signal = result;
									// data = [];

									// signal = signal.slice(0,signal.length-1)
									// jQuery.each(signal.split(/;/), function(j, line) {
										// line = line.split(/,/);
										// if(line[0]){
											// if(!isNaN(parseFloat(line[1]))){
												// data.push([
													// Date.parse(line[0] +' UTC'),
													// parseFloat(line[1])
												// ]);
											// }
											// else{
												// data.push([
													// Date.parse(line[0] +' UTC'),
													// null
												// ]);
											// }
										// }
										
									// });
									
									// options.series[0].data = data;

									
									
								// } catch (e) {  }
								
								
								
								// chart = new Highcharts.Chart(options);
							
								// Highcharts.setOptions({
									// global: {
										// useUTC: false
									// }
								// });
							// },
							// async: true
						// });
					// },10000);
					
				// });
			// </script>";
		
		
		
		// find setpoints with zone in mysql and cycle through them
		$result = mysql_query("SELECT * FROM temperature_setpoints WHERE zone = '$zone'");
		while($row = mysql_fetch_array($result)){
			$id = $row['id'];
			$id_day = $page."_setpoint_".$zone."_day".$id;
			$id_time = $page."_setpoint_".$zone."_time".$id;
			$id_setpoint = $page."_setpoint_".$zone."_setpoint".$id;
	
			$mon_selected = "";
			$tue_selected = "";
			$wed_selected = "";
			$thu_selected = "";
			$fri_selected = "";
			$sat_selected = "";
			$sun_selected = "";
	
			if(floor($row['day'])==0){
				$mon_selected = "selected=selected";
			}
			if(floor($row['day'])==1){
				$tue_selected = "selected=selected";
			}
			if(floor($row['day'])==2){
				$wed_selected = "selected=selected";
			}
			if(floor($row['day'])==3){
				$thu_selected = "selected=selected";
			}
			if(floor($row['day'])==4){
				$fri_selected = "selected=selected";
			}
			if(floor($row['day'])==5){
				$sat_selected = "selected=selected";
			}
			if(floor($row['day'])==6){
				$sun_selected = "selected=selected";
			}
			
			$str_time = sprintf('%02d', $row['hour']).":".sprintf('%02d', $row['minute']);

			
			$setpoint = $row['setpoint'];
			
			echo "
			<div class='setpoint'>
				<select name='$id_day' id='$id_day' data-native-menu='false'>
					<option $mon_selected value='0'>maa</option>
					<option $tue_selected value='1'>din</option>
					<option $wed_selected value='2'>woe</option>
					<option $thu_selected value='3'>don</option>
					<option $fri_selected value='4'>vri</option>
					<option $sat_selected value='5'>zat</option>
					<option $sun_selected value='6'>zon</option>
				</select>
				<input type='time' name='$id_time' id='$id_time' value='$str_time'>
				<input type='number' name='$id_setpoint' id='$id_setpoint' value='$setpoint' min='10' max='30'>
				<p>&deg;C</p>
				<a class='delete' href='index.php?web=$web&page=pages/$page&delete_zone=$zone&delete_setpoint=$id'><img src=icons/ffffff/control_x.png></a>";

			
			// echo the script to change values through ajax
			echo "
				<script>
					$('#$id_time').change(
						function(){
							$.post( 'requests/set_setpoint.php', {'id': $id , 'column': 'time' , 'value': $(this).val()}); 
							//for debugging: 
							//$.post( 'requests/set_setpoint.php', {'id': $id , 'column': 'time' , 'value': $(this).val()}, function(response){alert(response);}); 
						}
					);
					$('#$id_day').change(
						function(){
							$.post( 'requests/set_setpoint.php', { 'id': $id , 'column': 'day', 'value': $(this).val()});
						}
					);
					$('#$id_setpoint').change(
						function(){
							$.post( 'requests/set_setpoint.php', { 'id': $id , 'column': 'setpoint', 'value': $(this).val()});
						}
					);
				</script>
			</div>";
			
		}
	
	echo "
			<a name='add_setpoint_$zone'></a>
			<a class='add' href='index.php?web=$web&page=pages/$page&add_setpoint=$zone' data-role='button'>Setpoint toevoegen</a>
		</div>";
}

function add_ventilation_control(){
	global $page;
	
	$page = explode('/',$page);
	$page = end($page);
	$item = 'building.ventilation.speedcontrol';
	
	$switch_id = $page .'_'. str_replace('.','_',$item)."_switch";
	$slider_id = $page .'_'. str_replace('.','_',$item)."_slider";
	
	echo "
		<span class='dimmer'>
			<p>Ventilatie</p>
			<input id='$slider_id' data-widget='basic.slider' data-item='$item' type='range' value='0' min='0' max='3' step='1' data-highlight='true'/>
		</span>";
	
}
?>



