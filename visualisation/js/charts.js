//////////////////////////////////////////////////////////////////////////////
// initialize charts
//////////////////////////////////////////////////////////////////////////////
$(document).on('pagebeforecreate',function(){


	//cycle through all alarm_placeholder
	$( ".chart_placeholder" ).each(function(){
	
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
				dateTimeLabelFormats: {
					hour: '%H:%M'
				},
				range: 2 * 24 * 3600 * 1000
			},
			yAxis: {
				title: {
				}
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
		
		// tell highcharts to convert utc time to local time
		Highcharts.setOptions({
			global: {
				useUTC: false
			}
		});
		
		chart = new Highcharts.StockChart(options);
		
		console.time("total");
		
		// Load data asynchronously using jQuery. On success, add the data to the options and initiate the chart.
		jQuery.each(signals_str.split(/,/), function(i, signal_id) {

			$.post('requests/measurements_get.php?signal='+signal_id+'&scale=quarter',function(data){
			
				var data = JSON.parse(data);
				
				options.series[i].data = data.series.data;
				options.series[i].name = data.series.name;
				
				options.yAxis.title.text = data.unit;
				
				chart.destroy();
				chart = new Highcharts.StockChart(options);
				
			});
		
		});
		console.timeEnd("total");
	});
});