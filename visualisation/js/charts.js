//////////////////////////////////////////////////////////////////////////////
// initialize charts
//////////////////////////////////////////////////////////////////////////////
$(document).on('pagebeforecreate',function(){

	var chart = [];
	//cycle through all chart_placeholder
	$( ".chart_placeholder" ).each(function(j){
	
		var id = $(this).attr('id');
		var title_str = $(this).attr('data-title');
		var signals_str = $(this).attr('data-signals');
		
		// set some options
		var options = {
			chart: {
				renderTo: id,
				type: 'line'
			},
			title: {
				text: title_str
			},
			xAxis: {
				type: 'datetime',
				range: 2 * 24 * 3600 * 1000
			},
			tooltip: {
				xDateFormat: '%Y-%m-%d %H:%M',
				valueDecimals: 1,
				shared: true
			},
			rangeSelector : {
				enabled: false
			},
			series: []
		}
		
		// tell highcharts to convert utc time to local time
		Highcharts.setOptions({
			global: {
				useUTC: false
			}
		});
		
		chart[j] = new Highcharts.StockChart(options);

		console.time("total");
		
		// Load data asynchronously using jQuery. On success, add the data to the options and initiate the chart.
		jQuery.each(signals_str.split(/,/), function(i, signal_id) {

			$.post('requests/measurements_get.php?signal='+signal_id+'&scale=quarter',function(series){
			
				var series = JSON.parse(series);
				
				chart[j].addSeries({name: series.name ,data: series.data});
				chart[j].yAxis[0].setTitle({text:series.unit});

				
			});
		
		});
		console.timeEnd("total");
	});
	
	
	var barchart = [];
	//cycle through all bar_chart_placeholder
	$( ".bar_chart_placeholder" ).each(function(j){
	
		var id = $(this).attr('id');
		var title_str = $(this).attr('data-title');
		var signals_str = $(this).attr('data-signals');
		
		// set some options
		var options = {
			chart: {
				renderTo: id,
				type: 'column'
			},
			title: {
				text: title_str
			},
			xAxis: {
				type: 'datetime',
			},
			tooltip: {
				xDateFormat: '%Y-%m-%d',
				shared: true
			},
			rangeSelector : {
				enabled: false
			},
			series: []
		}
		
		// tell highcharts to convert utc time to local time
		Highcharts.setOptions({
			global: {
				useUTC: false
			}
		});
		
		barchart[j] = new Highcharts.StockChart(options);


		// Load data asynchronously using jQuery. On success, add the data to the options and initiate the chart.
		jQuery.each(signals_str.split(/,/), function(i, signal_id) {

			$.post('requests/measurements_get.php?signal='+signal_id+'&scale=week',function(series){
			
				var series = JSON.parse(series);
				
				barchart[j].addSeries({name: series.name ,data: series.data});
				barchart[j].yAxis[0].setTitle({text:series.unit});

				
			});
		
		});
	});
});