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
		
		console.time("php request");
		// Load data asynchronously using jQuery. On success, add the data to the options and initiate the chart.
		$.post( 'requests/measurements_get.php', {'scale': 'quarter' , 'signal': signals_str},function(result){
			console.timeEnd("php request");
			
			console.time("post processing");
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
			console.timeEnd("post processing");
			
			
			console.time("chart creation");
			// create the chart
			chart = new Highcharts.StockChart(options);
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			console.timeEnd("chart creation");
			
		});
	});
});