<?php
function add_chart($chart_title,$signals_str){

	$signals = explode(',',$signals_str);
	$container = str_replace(' ','_',$chart_title.'_'.$signals_str);
	
	echo "
		<div id='$container' class='chart'></div>";
	
	echo "
		<script type='text/javascript'>
			var chart;
			$(document).ready(function() {
				var options = {
					chart: {
						renderTo: '$container',
						type: 'line',
					},
					title: {
						text: '$chart_title',
					},
					xAxis: {
						type: 'datetime',
						dateTimeLabelFormats: {
							hour: '%H:%M'
						},
						range: 2 * 24 * 3600 * 1000
					},
					yAxis: {
						title: {
						},
					},
					tooltip: {
						xDateFormat: '%Y-%m-%d %H:%M',
						valueDecimals: 1,
						shared: true
					},
					rangeSelector : {
						enabled: false
					},
					series: [
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []}
					]
				}
				
				// Load data asynchronously using jQuery. On success, add the data to the options and initiate the chart.
				jQuery.ajax({
					url:    'requests/measurements_get.php?scale=quarter&signal=$signals_str',
					success: function(result) {
						try {
							// split result into signals
							result = result.split(/signal/);
							result = result.slice(1);
							
							jQuery.each(result, function(i, signal) {
								data = [];
								signal = signal.slice(0,signal.length-1)
								
								// split result into lines
								jQuery.each(signal.split(/;/), function(j, line) {
									if(j==0){
										legend = line;
									}
									else if(j==1){
										unit = line.replace('°', 'deg ');
									}
									else{
										// split line into x and y data
										line = line.split(/,/);
										if(line[0]){
											if(!isNaN(parseFloat(line[1]))){
												data.push([parseInt(line[0]),parseFloat(line[1])]);
											}
											else{
												data.push([parseInt(line[0]),null]);
											}
										}
									}
								});
								options.series[i].data = data;
								options.series[i].name = legend;
								options.yAxis.title.text = unit;
							});
							
						} catch (e) {  }
						
						chart = new Highcharts.StockChart(options);
						Highcharts.setOptions({
							global: {
								useUTC: false
							}
						});
						
					},
					async: true
				});
				
			});
		</script>";
};


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// bar chart with average week values
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function add_week_average_chart($chart_title,$signals_str){

	$signals = explode(',',$signals_str);
	$container = str_replace(' ','_',$chart_title);
	echo "
		<div id='$container' class='chart'></div>";
	
	echo "
		<script type='text/javascript'>
			var chart;
			$(document).ready(function() {
				var options = {
					chart: {
						renderTo: '$container',
						type: 'column',
					},
					title: {
						text: '$chart_title',
					},
					yAxis: {
						title: {
						},
					},
					tooltip: {
						xDateFormat: '%Y-%m-%d %H:%M',
						valueDecimals: 1,
						shared: true
					},
					rangeSelector : {
						enabled: false
					},
					series: [
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []},
						{showInLegend: false, data: []}
					]
				}
				
				// Load data asynchronously using jQuery. On success, add the data
				// to the options and initiate the chart.
				// http://api.jquery.com/jQuery.get/

				jQuery.ajax({
					url:    'requests/get_week_average_data.php?signal=$signals_str',
					success: function(result) {
						try {
							// split the data return into signals and lines lines and parse them
							result = result.split(/signal/);
							result = result.slice(1);
							
							jQuery.each(result, function(i, signal) {
								data = [];
								labels = [];
								signal = signal.slice(0,signal.length-1)
								jQuery.each(signal.split(/;/), function(j, line) {
									if(j==0){
										legend = line;
									}
									else if(j==1){
										unit = line.replace('°', 'deg ');;
									}
									else{
										line = line.split(/,/);
										if(line[0]){
											data.push([
												parseFloat(line[1])
											]);
											labels.push([
												parseInt(line[0])
											]);
										}
									}
								});
								
								options.series[i].data = data;
								options.series[i].name =  legend;
								options.xAxis.categories = labels;
								options.yAxis.title.text =  unit;
							});
							
						} catch (e) {  }
						
						
						
						chart = new Highcharts.Chart(options);
					
						Highcharts.setOptions({
							global: {
								useUTC: false
							}
						});
					},
					async: true
				});
				
			});
		</script>";
};
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// bar chart with monthly averages
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function add_month_average_chart($chart_title,$signals_str){

	$signals = explode(',',$signals_str);
	$container = str_replace(' ','_',$chart_title);
	echo "
		<div id='$container' class='chart'></div>";
	
	echo "
		<script type='text/javascript'>
			var chart;
			$(document).ready(function() {
				var options = {
					chart: {
						renderTo: '$container',
						type: 'column',
						marginLeft: 55,
						marginRight: 130,
						marginBottom: 35,
						backgroundColor: {
							linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
							stops: [
								[0, 'rgb(76, 76, 76)'],
								[1, 'rgb(16, 16, 16)']
							]
						},
						borderWidth: 0,
						borderRadius: 10,
						plotBackgroundColor: null,
						plotShadow: false,
						plotBorderWidth: 0
					},
					title: {
						text: '$chart_title',
						x: -20,
						style: {
								color: '#AAAAAA'
						},
					},
					xAxis: {
						gridLineWidth: 1,
						labels: {
							align: 'center',
							x: -3,
							y: 20,
							style: {
								color: '#808080'
							},
						}
					},
					yAxis: {
						title: {
							x: 10,
							style: {
								color: '#808080'
							}
						},
						labels: {
							x: -20,
							style: {
								color: '#808080'
							}
						}
					},
					tooltip: {
						xDateFormat: '%Y-%m-%d %H:%M',
						valueDecimals: 1,
						shared: true
					},
					legend: {
						enabled: true,
						layout: 'vertical',
						align: 'right',
						verticalAlign: 'top',
						x: -5,
						y: 60,
						borderWidth: 0,
						itemStyle: {
							color: '#808080'
						}
					},
					rangeSelector : {
						enabled: false
					},
					navigator: {
						handles: {
							backgroundColor: '#666',
							borderColor: '#808080'
						},
						outlineColor: '#808080',
						maskFill: 'rgba(16, 16, 16, 0.5)',
						series: {
							color: '#7798BF',
							lineColor: '#A6C7ED'
						}
					},
					//plotOptions: {
					//	column: {
					//		stacking: 'normal'
					//	}
					//},
					series: [{
						marker: {
							enabled: false
						},
						color: '#88AA00'
					}";
		if(count($signals) > 1){
			echo "		
					,{
						marker: {
							enabled: false
						},
						color: '#6F917C'
					}";
		}
		if(count($signals) > 2){
			echo "	
					,{
						marker: {
							enabled: false
						},
						color: '#0088AA'
					}";
		}
		if(count($signals) > 3){
			echo "
					,{
						marker: {
							enabled: false
						},
						color: '#3737C8'
					}";
		}			
		echo "
					]
				}
				// Load data asynchronously using jQuery. On success, add the data
				// to the options and initiate the chart.
				// http://api.jquery.com/jQuery.get/

				jQuery.ajax({
					url:    'requests/get_month_average_data.php?signal=$signals_str',
					success: function(result) {
						try {
							// split the data return into signals and lines lines and parse them
							result = result.split(/signal/);
							result = result.slice(1);
							
							jQuery.each(result, function(i, signal) {
								data = [];
								labels = [];
								signal = signal.slice(0,signal.length-1)
								jQuery.each(signal.split(/;/), function(j, line) {
									if(j==0){
										legend = line;
									}
									else if(j==1){
										unit = line.replace('°', 'deg ');;
									}
									else{
										line = line.split(/,/);
										if(line[0]){
											data.push([
												parseFloat(line[1])
											]);
											labels.push([
												line[0]
											]);
										}
									}
								});
								
								options.series[i].data = data;
								options.series[i].name =  legend;
								options.xAxis.categories = labels;
								options.yAxis.title.text =  unit;
							});
							
						} catch (e) {  }
						
						
						
						chart = new Highcharts.Chart(options);
					
						Highcharts.setOptions({
							global: {
								useUTC: false
							}
						});
					},
					async: true
				});
				
			});
		</script>";
};
?>