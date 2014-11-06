//////////////////////////////////////////////////////////////////////////////
// initialize charts
//////////////////////////////////////////////////////////////////////////////
$(document).on('pagebeforecreate',function(){

	var chart = [];
	var scale = [];
	//cycle through all chart_placeholder
	$( ".chart_placeholder" ).each(function(j){
	
		var id = $(this).attr('id');
		var title_str = $(this).attr('data-title');
		var signals_str = $(this).attr('data-signals');
		scale[j] = $(this).attr('data-scale');
		
		// set some options
		var options = {
			chart: {
				renderTo: id,
			},
			title: {
				text: title_str
			},
			xAxis: {
				type: 'datetime',
			},
			tooltip: {
				xDateFormat: '%Y-%m-%d',
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
		
		// change options depending on the chart type
		if($(this).attr('data-chart')=='bar'){
			options.chart.type = 'bar';
			chart[j] = new Highcharts.Chart(options);
		}
		else{
			options.chart.type = 'line';
			options.xAxis.range = 2 * 24 * 3600 * 1000;
			options.tooltip.xDateFormat='%Y-%m-%d %H:%M';
			chart[j] = new Highcharts.StockChart(options);
		}
		
		
		// Load data asynchronously using jQuery. On success, add the data to the options and initiate the chart.
		jQuery.each(signals_str.split(/,/), function(i, signal_id) {

			$.post('requests/measurements_get.php?signal='+signal_id+'&scale='+scale[j],function(series){
			
				var series = JSON.parse(series);
				
				// update the chart
				chart[j].addSeries({name: series.name ,data: series.data});
				chart[j].yAxis[0].setTitle({text:series.unit});

			});
		});
	});
});