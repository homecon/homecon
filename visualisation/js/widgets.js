/*
    Copyright 2015 Brecht Baeten
    This file is part of KNXControl.

    KNXControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    KNXControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
*/


/*****************************************************************************/
/*                     light switch                                          */
/*****************************************************************************/
$.widget('homecon.lightswitch',{
	options: {
		label: '',
		item: '',
		src_on: 'icons/f79a1f/light_light.png',
		src_off: 'icons/ffffff/light_light.png',
	},
	_create: function(){
		this.element.prepend('<div data-role="toggleswitch" data-item="'+this.options.item+'" data-label="'+this.options.label+'" data-val_on="1" data-val_off="0" data-src_on="'+this.options.src_on+'" data-src_off="'+this.options.src_off+'"></div>');
		this.element.find('div[data-role="toggleswitch"]').toggleswitch()
	}
});


/*****************************************************************************/
/*                     light dimmer                                          */
/*****************************************************************************/
$.widget("homecon.lightdimmer",{
	options: {
		label: '', 
		item: '',
		src_on: 'icons/f79a1f/light_light.png',
		src_off: 'icons/ffffff/light_light.png',
		val_on: 255,
		val_off: 0
    },
	_create: function(){
		// enhance
		this.element.prepend('<p>'+this.options.label+'</p>'+
						     '<div data-role="toggleswitch" data-item="'+this.options.item+'" data-val_on="'+this.options.val_on+'" data-val_off="'+this.options.val_off+'" data-src_on="'+this.options.src_on+'" data-src_off="'+this.options.src_off+'"></div>'+
						     '<div data-role="inputslider"  data-item="'+this.options.item+'" data-val_on="'+this.options.val_on+'" data-val_off="'+this.options.val_off+'"></div>');
		
		this.element.find('div[data-role="toggleswitch"]').toggleswitch()
		this.element.find('div[data-role="inputslider"]').inputslider()
		this.element.enhanceWithin();
	}
});

/*****************************************************************************/
/*                     shading                                               */
/*****************************************************************************/ 
$.widget("homecon.shading",{
	options: {
		label: '',
		item: '',
		val_on: 255,
		val_off: 0,
		advanced: false
    },
	_create: function(){
		// enhance
		this.element.prepend('<p>'+this.options.label+'</p>'+
						     '<div data-role="valueswitch" class="open" data-item="'+this.options.item+'" data-value="'+this.options.val_off+'" data-src="icons/ffffff/fts_shutter_10.png"></div>'+
							 '<div data-role="valueswitch" class="close" data-item="'+this.options.item+'" data-value="'+this.options.val_on+'" data-src="icons/ffffff/fts_shutter_100.png"></div>'+    
							 '<div data-role="inputslider" data-item="'+this.options.item+'" data-val_on="'+this.options.val_on+'" data-val_off="'+this.options.val_off+'"></div>');
		
		this.element.find('div[data-role="valueswitch"]').valueswitch()
		this.element.find('div[data-role="inputslider"]').inputslider()
		this.element.enhanceWithin();

		if(this.options.advanced){
			// get the parent item
			arr = this.options.item.split('.');
			parent = arr.slice(0,arr.length-1).join('.');

			this.element.append('<div class="advanced">'+
									'<div class="threecols"><div data-role="checkbox" data-label="Auto" data-item="'+parent+'.auto"></div></div>'+
									'<div class="threecols"><div data-role="checkbox" data-label="Closed" data-item="'+parent+'.closed"></div></div>'+
									'<div class="threecols"><div data-role="checkbox" data-label="Override" data-item="'+parent+'.override"></div></div>'+
								'</div>');
			$('div[data-role="checkbox"]').checkbox();
		}
	}
});


/*****************************************************************************/
/*                     clock                                                 */
/*****************************************************************************/ 
$.widget("homecon.clock",{
	options: {
    },
	_create: function(){
		// enhance
		this.element.append('<div class="time"><div>'+
								'<img class="bg" src="icons/clock/clockbg1.png">'+
								'<img class="hoursLeft" src="icons/clock/0.png"/>'+
								'<img class="hoursRight" src="icons/clock/1.png"/><hr>'+
							  '</div><div>'+
								'<img class="bg" src="icons/clock/clockbg1.png">'+
								'<img class="minutesLeft" src="icons/clock/2.png"/>'+
								'<img class="minutesRight" src="icons/clock/3.png"/><hr>'+
							  '</div></div>'+
							  '<div class="date">1 januari 2015</div>');
		//this.element.enhanceWithin();

		// bind events
		this.setDate();
		this.setTime();
		
		var that = this;
		setInterval(function(){that.setDate()}, 30000);
		setInterval(function(){that.setTime()}, 5000);
	},
	setDate: function(){
		now = new Date();
		var weekday = (now.getDay()+6)%7;
		var day = now.getDate();
		var month = now.getMonth();
		var year = now.getFullYear();

		var date_string = language.capitalize(language.weekday[weekday])+' '+day+' '+language.capitalize(language.month[month])+' '+year;
	
		this.element.find('.date').html(date_string);
	},
	setTime: function(){
		now = new Date();
		h1 = Math.floor( now.getHours() / 10 );
		h2 = now.getHours() % 10;
		m1 = Math.floor( now.getMinutes() / 10 );
		m2 = now.getMinutes() % 10;

		if(h2 != this.h2_current){
			this.flip('img.hoursRight',h2);
			this.h2_current = h2;
					
			this.flip('img.hoursLeft',h1);
			this.h1_current = h1;
		}
		   
		if( m2 != this.m2_current){
			this.flip('img.minutesRight',m2);
			this.m2_current = m2;

			this.flip('img.minutesLeft',m1);
			this.m1_current = m1;
		}
	},
	flip: function(selector,num){
	
		var src1 = 'icons/clock/'+num+'-1.png';
		var src2 = 'icons/clock/'+num+'-2.png';
		var src3 = 'icons/clock/'+num+'-3.png';
		var src  = 'icons/clock/'+num+'.png';
		
		var that = this;
		if(this.h1_current==-1){
			// avoid animation on refresh
			that.element.find(selector).attr('src',src);
		}
		else{
			that.element.find(selector).attr('src',src1);
			
			setTimeout(function(){
				that.element.find(selector).attr('src',src2);
			},60);
			setTimeout(function(){
				that.element.find(selector).attr('src',src3);
			},120);
			setTimeout(function(){
				that.element.find(selector).attr('src',src);
			},180);
		}
	},
	h1_current: -1,
	h2_current: -1,
	m1_current:-1,
	m2_current:-1
});

/*****************************************************************************/
/*                     weather block                                         */
/*****************************************************************************/ 
$.widget("homecon.weather_block",{
	options: {
		item: 'knxcontrol.weather.prediction.detailed',
		item_temperature: '',
		item_windspeed: '',
		item_winddirection: '',
		item_clouds: '',
		mini: false,
		daysahead: -1
    },
	_create: function(){
		// enhance
		this.element.append('<div data-field="date"></div>'+
							'<img src="icons/weather/blank.png">'+
							'<div data-field="temperature"></div>'+
							'<div data-field="wind"></div>'+
							'<div data-field="clouds"></div>'
		);
		if(this.options.mini){
			this.element.addClass("mini");
		}
		this.element.enhanceWithin();
		
		// bind events
		this._on(this.document,{
		
			'update': function(){
				this.update();
			}
		});
	},
	update: function(){
		var item = this.options.item;
		if(knxcontrol.item[item]){
			if(this.options.daysahead>=0){
				index = this.options.daysahead
			}
			else{
				index = 0;
			}

			if(index < knxcontrol.item[item].length){
				this.element.find('img').attr('src','icons/weather/'+this.icons[knxcontrol.item[item][index].icon]);
				var temperature = 0;
				var windspeed = 0;
				var winddirection = '';
				var clouds = 0;
				
				
				date = new Date(knxcontrol.item[item][index].datetime*1000);
				var weekday = (date.getDay()+6)%7;
				var day = date.getDate();
				var month = date.getMonth();

				var hour =  date.getHours();
				var minutes = date.getMinutes();
				if(hour<10){
					hour = '0'+hour;
				}
				if(minutes<10){
					minutes = '0'+minutes;
				}
				
				var date_string = language.weekday_short[weekday];
				
				if(this.options.item_temperature == ''){
					if(item =='knxcontrol.weather.prediction.detailed'){
						temperature = knxcontrol.item[item][index].temperature;
					}
					else{
						temperature = knxcontrol.item[item][index].temperature_day;
					}
				}
				else{
					temperature = knxcontrol.item[this.options.item_temperature];
				}
				if(this.options.item_windspeed == ''){
					windspeed = knxcontrol.item[item][index].wind_speed;
				}
				else{
					windspeed = knxcontrol.item[this.options.item_windspeed];
				}
				if(this.options.item_winddirection == ''){
					winddirection = language.winddirection(knxcontrol.item[item][index].wind_direction)
				}
				else{
					winddirection = language.winddirection(knxcontrol.item[this.options.item_winddirection]);
				}
				if(this.options.item_clouds == ''){
					clouds = knxcontrol.item[item][index].clouds;
				}
				else{
					clouds = knxcontrol.item[this.options.item_clouds];
				}
				
				if(this.options.mini){
					this.element.find('[data-field="date"]').html(date_string);
					this.element.find('[data-field="temperature"]').html(Math.round(temperature*10)/10+'&deg;C');
					this.element.find('[data-field="wind"]').html(Math.round(windspeed*1)/1+' m/s '+ winddirection);
					this.element.find('[data-field="clouds"]').html(Math.round(clouds*1)/1+'%');
				}
				else{
					this.element.find('[data-field="temperature"]').html(language.capitalize(language.temperature)+': '+Math.round(temperature*10)/10+'&deg;C');
					this.element.find('[data-field="wind"]').html(language.capitalize(language.wind)+': '+Math.round(windspeed*1)/1+' m/s '+ winddirection);
					this.element.find('[data-field="clouds"]').html(language.capitalize(language.clouds)+': '+Math.round(clouds*1)/1+'%');
				}
			}
			else{
				this.element.find('img').attr('src','icons/weather/na.png');
				
				this.element.find('[data-field="date"]').html('-');
				this.element.find('[data-field="temperature"]').html('-');
				this.element.find('[data-field="wind"]').html('-');
				this.element.find('[data-field="clouds"]').html('-');
			}
		}
	},
	icons: {'01d': 'sun_1.png',
			'02d': 'sun_3.png',
			'03d': 'cloud_4.png',
			'04d': 'cloud_5.png',
			'09d': 'cloud_7.png',
			'10d': 'sun_7.png' ,
			'11d': 'cloud_10.png',
			'13d': 'cloud_13.png',
			'50d': 'sun_6.png',
			'01n': 'moon_1.png',
			'02n': 'moon_3.png',
			'03n': 'cloud_4.png',
			'04n': 'cloud_5.png',
			'09n': 'cloud_7.png',
			'10n': 'moon_7.png',
			'11n': 'cloud_10.png',
			'13n': 'cloud_13.png',
			'50n': 'moon_6.png'}
});

/*****************************************************************************/
/*                     alarm                                                 */
/*****************************************************************************/ 
$.widget("homecon.alarm",{
	options: {
		section: 1
    },
	_create: function(){
		// enhance
		this.element.prepend('<div class="alarm_list"></div><a class="add" data-role="button">'+language.capitalize(language.add_alarm)+'</a>');
		that = this;
		$.each(knxcontrol.alarm,function(index,alarm){
			if(typeof alarm == 'object'){
				that.update(alarm.id);
			}
		});
		$.each(knxcontrol.action,function(index,action){
			if(typeof action == 'object'){
				that.update_action(action.id);
			}
		});
		this.element.enhanceWithin();
		
		// bind events
		this._on(this.element, {
			'change': function(event){
				
				id = $(event.target).parents('.alarm').attr('data-id');
				field = $(event.target).attr('data-field');
				
				if(field=='time'){
					time = $(event.target).val().split(':');
					hour = time[0];
					minute = time[1];
					knxcontrol.alarm.update(id,'hour',hour);
					knxcontrol.alarm.update(id,'minute',minute);
				}
				else if(field=='action_id'){
					value = $(event.target).val();
					knxcontrol.alarm.update(id,field,value);
				}
				else{
					if($(event.target).prop('checked')){
						value = 1;
					}
					else{
						value = 0;
					}
					knxcontrol.alarm.update(id,field,value);
				}
			},
			'update': function(event,id){
				this.update(id);
			},
			'update_action': function(event,id){
				this.update_action(id);
			},
			'click a.add': function(event){
				knxcontrol.alarm.add(this.options.section);
			},
			'click a.delete': function(event){
				knxcontrol.alarm.del($(event.target).parents('.alarm').attr('data-id'));
			}
        });
	},
	update: function(id){
		// check if the alarm exists in knxcontrol
		if(knxcontrol.alarm[id]){
			// check if the alarm belongs in this section
			if(knxcontrol.alarm[id].section_id==this.options.section){
				// check if the alarm does not already exists in the DOM
				if(this.element.find('.alarm_list').find('.alarm[data-id="'+id+'"]').length==0){
					//add the alarm to the DOM
					this.element.find('.alarm_list').append('<div class="alarm ui-body-b ui-corner-all" data-id="'+id+'">'+
																'<input type="time" data-field="time" value="12:00">'+
																'<a href="#" class="delete" data-role="button" data-icon="delete" data-iconpos="notext">Delete</a>'+
																'<h1></h1>'+
																'<div class="days">'+
																	'<div data-role="controlgroup" data-type="horizontal">'+
																		'<label><input type="checkbox" data-field="mon" class="custom" data-mini="true">'+language.capitalize(language.weekday_short[0])+'</label>'+
																		'<label><input type="checkbox" data-field="tue" class="custom" data-mini="true">'+language.capitalize(language.weekday_short[1])+'</label>'+
																		'<label><input type="checkbox" data-field="wed" class="custom" data-mini="true">'+language.capitalize(language.weekday_short[2])+'</label>'+
																		'<label><input type="checkbox" data-field="thu" class="custom" data-mini="true">'+language.capitalize(language.weekday_short[3])+'</label>'+
																		'<label><input type="checkbox" data-field="fri" class="custom" data-mini="true">'+language.capitalize(language.weekday_short[4])+'</label>'+
																		'<label><input type="checkbox" data-field="sat" class="custom" data-mini="true">'+language.capitalize(language.weekday_short[5])+'</label>'+
																		'<label><input type="checkbox" data-field="sun" class="custom" data-mini="true"> '+language.capitalize(language.weekday_short[6])+'</label>'+
																	'</div>'+
																'</div>'+
																'<div class="alarm_action">'+
																	'<select data-field="action_id" data-native-menu="false">'+
																		'<option class="action_select" value="0" data-id="0">Select action</option>'+
																	'</select>'+
																'</div>'+
															'</div>').enhanceWithin();
				}
				// update the alarm time
				var time = this.padtime(knxcontrol.alarm[id].hour) + ":" + this.padtime(knxcontrol.alarm[id].minute);
				this.element.find('.alarm[data-id="'+id+'"]').find('[data-field="time"]').val(time);

				// update alarm days
				this.element.find('.alarm[data-id="'+id+'"]').find('[data-field="mon"]').prop('checked', !!+knxcontrol.alarm[id].mon).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+id+'"]').find('[data-field="tue"]').prop('checked', !!+knxcontrol.alarm[id].tue).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+id+'"]').find('[data-field="wed"]').prop('checked', !!+knxcontrol.alarm[id].wed).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+id+'"]').find('[data-field="thu"]').prop('checked', !!+knxcontrol.alarm[id].thu).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+id+'"]').find('[data-field="fri"]').prop('checked', !!+knxcontrol.alarm[id].fri).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+id+'"]').find('[data-field="sat"]').prop('checked', !!+knxcontrol.alarm[id].sat).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+id+'"]').find('[data-field="sun"]').prop('checked', !!+knxcontrol.alarm[id].sun).checkboxradio('refresh');
			}
		}
		else{
			// remove the alarm from the DOM
			this.element.find('.alarm[data-id="'+id+'"]').remove();
		}
	},
	update_action: function(id){
		// check if the action belongs in this widget
		if(knxcontrol.action[id].section_id==0 || knxcontrol.action[id].section_id==this.options.section){
			//loop through all alarms
			$.each(this.element.find('.alarm'),function(index,alarm){
				// check if the action option exists
				if($(alarm).find('option[data-id="'+id+'"]').length==0){
					// add the action to the select list
					$(alarm).find('div.alarm_action select').append('<option class="action_select" value="'+id+'" data-id="'+id+'">'+knxcontrol.action[id].name+'</option>').selectmenu('refresh');
				}
				// check the selected action
				var alarm_id = $(alarm).attr('data-id');
				$(alarm).find('div.alarm_action select').val( knxcontrol.alarm[alarm_id].action_id );
				
				$(alarm).find('div.alarm_action select').selectmenu('refresh');
			});
		}
	},
	padtime: function(num) {
		var s = num+"";
		while (s.length < 2) s = "0" + s;
		return s;
	}
});

/*****************************************************************************/
/*                     measurement export                                    */
/*****************************************************************************/
$.widget("homecon.measurement_export",{
	options: {
	},
	_create: function(){
		// enhance
		this.element.html('<div class="ui-field-contain">Startdate:<input type="date" class="startdate"></div><div class="ui-field-contain">Enddate:<input type="date" class="enddate"></div><a href="#" class="export" data-role="button" data-rel="popup">'+language.capitalize(language.export_measurements)+'</a>');
		this.element.enhanceWithin();	

		// bind events
		this._on(this.element, {
			'click a.export': function(event){
				// get start and end date
				
				var startdate = $(this.element.find('input.startdate')).val();
				var enddate   = $(this.element.find('input.enddate')).val();

				// not sure if this will work
				window.open('requests/measurements_export.php?table=measurements&startdate='+startdate+'&enddate='+enddate);
			}
		});
	}
});

/*****************************************************************************/
/*                     settings                                              */
/*****************************************************************************/
$.widget("homecon.settings",{
	options: {
	},
	_create: function(){
		// enhance
		this.element.html('<div data-role="fieldcontain"><label for="home_settings_ip">IP:</label><input type="text" id="home_settings_ip" data-field="ip"></div>'+
						  '<div data-role="fieldcontain"><label for="home_settings_port">Port:</label><input type="text" id="home_settings_port" data-field="port"></div>'+
						  '<div data-role="fieldcontain"><label for="home_settings_webip">Web-IP:</label><input type="text" id="home_settings_webip" data-field="web_ip"></div>'+
						  '<div data-role="fieldcontain"><label for="home_settings_webport">Web-Port:</label><input type="text" id="home_settings_webport" data-field="web_port"></div>'+
						  '<div data-role="fieldcontain"><label for="home_settings_token">Token:</label><input type="text" id="home_settings_token" data-field="token"></div>'+
						  '<a href="#" class="save" data-role="button" data-rel="popup">'+language.capitalize(language.save)+'</a>');
		this.element.enhanceWithin();	
		this.update();

		// bind events
		this._on(this.element, {
			'update': function(event){
				this.update();
			},
			'click a.save': function(event){
				knxcontrol.settings.ip = this.element.find('[data-field="ip"]').val();
				knxcontrol.settings.port = this.element.find('[data-field="port"]').val();
				knxcontrol.settings.web_ip = this.element.find('[data-field="web_ip"]').val();
				knxcontrol.settings.web_port = this.element.find('[data-field="web_port"]').val();
				knxcontrol.settings.token = this.element.find('[data-field="token"]').val();
				knxcontrol.settings.update();
				
			}
		});
	},
	update: function(){
		this.element.find('[data-field="ip"]').val(knxcontrol.settings.ip);
		this.element.find('[data-field="port"]').val(knxcontrol.settings.port);
		this.element.find('[data-field="web_ip"]').val(knxcontrol.settings.web_ip);
		this.element.find('[data-field="web_port"]').val(knxcontrol.settings.web_port);
		this.element.find('[data-field="token"]').val(knxcontrol.settings.token);
	}
});

/*****************************************************************************/
/*                     chart                                                 */
/*****************************************************************************/
$.widget('homecon.chart',{
	options: {
      signals: '1',
	  type: 'quarterhour',
	  step: false
    },
	_create: function(){
		
		// Enhance
		this.element.append('<div class="chart_container"></div>');
		
		Highcharts.setOptions({
			global: {
				useUTC: false
			}
		});
				
		// add empty series
		var that = this;
		that.chart_options.series = [];
		$.each((''+this.options.signals).split(','),function(index,id){
			that.chart_options.series.push({name: ' ', step: that.options.step});
		});
		
		if(this.options.type == 'quarterhour'){
			this.chart_options.chart.type = 'line';
			this.chart_options.xAxis.range = 2 * 24 * 3600 * 1000;
			this.chart_options.tooltip.xDateFormat='%Y-%m-%d %H:%M';
			$(this.element).children('.chart_container').highcharts('StockChart',this.chart_options);
		}
		else if(this.options.type == 'week'){
			this.chart_options.chart.type = 'line';
			this.chart_options.plotOptions = { line: { marker: { enabled: false} } };
			$(this.element).children('.chart_container').highcharts(this.chart_options);
		}
		else{
			this.chart_options.chart.type = 'column';
			$(this.element).children('.chart_container').highcharts(this.chart_options);
		}
		
		this.chart = $(this.element).children('.chart_container').highcharts();
		this.chart.reflow();

		// try to get data
		this.get_data();		
		
		// bind events
		this._on(this.element, {
			'update': function(event,id){			
				this.update(id);
				this.chart.reflow();
			},
			'get_data': function(event){			
				this.get_data();
			}
		});
	},
	update: function(id){
		var that = this;
		$.each((''+this.options.signals).split(','),function(index,signal){
			if(signal==id){
				that.chart.series[index].name = knxcontrol.measurement[id].name;
				that.chart.yAxis[0].setTitle({text: knxcontrol.measurement[id].unit});
				
				if(that.options.type == 'quarterhour'){
					that.chart.series[index].setData(knxcontrol.measurement[id].quarterhourdata);
				}
				else if(that.options.type == 'day'){
					that.chart.series[index].setData(knxcontrol.measurement[id].daydata);
					that.chart.legend.allItems[index].update({name: knxcontrol.measurement[id].name});
				}
				else if(that.options.type == 'week'){
					that.chart.series[index].setData(knxcontrol.measurement[id].weekdata);
					that.chart.legend.allItems[index].update({name: knxcontrol.measurement[id].name});
				}
				else if(that.options.type == 'month'){
					that.chart.series[index].setData(knxcontrol.measurement[id].monthdata);
					that.chart.legend.allItems[index].update({name: knxcontrol.measurement[id].name});
				}
			}
		});
		
	},
	get_data: function(){
		var that = this;
		$.each((''+this.options.signals).split(','),function(index,id){
			if(that.options.type == 'quarterhour' || that.options.type == 'day'){
				knxcontrol.measurement.get_quarterhourdata(id);
			}
			else if(that.options.type == 'week'){
				knxcontrol.measurement.get_weekdata(id);
			}
			else if(that.options.type == 'month'){
				knxcontrol.measurement.get_monthdata(id);
			}
		});
	},
	chart: {},
	chart_options: {
		chart: {
		},
		title: {
			text: ''
		},
		xAxis: {
			type: 'datetime',
			ordinal: false
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
});

/*****************************************************************************/
/*                     action list                                           */
/*****************************************************************************/
$.widget("homecon.action_list",{
	options: {
		section: 1
    },
	_create: function(){
		// enhance
		this.element.html('<div class="action_list"></div>'+
		                  '<a href="#" class="add" data-role="button" data-rel="popup">'+language.capitalize(language.add_action)+'</a>');
		that = this;
		$.each(knxcontrol.action,function(index,action){
			if(typeof action == 'object'){
				that.update(action.id);
			}
		});
		this.element.enhanceWithin();	

		// bind events
		this._on(this.element, {
			'update': function(event,id){
				this.update(id);
			},
			'click a.edit': function(event){
				// populate the popup
				id = $(event.target).parents('.action').attr('data-id');
				$('#action_def_popup').find('input[data-field="name"]').val(knxcontrol.action[id].name);
				$('#action_def_popup').find('input[data-field="section_id"]').val(knxcontrol.action[id].section_id);
				
				$('#action_def_popup').find('input[data-field="delay1"]').val(knxcontrol.action[id].actions[0].delay);
				$('#action_def_popup').find('input[data-field="item1"]').val(knxcontrol.action[id].actions[0].item);
				$('#action_def_popup').find('input[data-field="value1"]').val(knxcontrol.action[id].actions[0].value);
				
				$('#action_def_popup').find('input[data-field="delay2"]').val(knxcontrol.action[id].actions[1].delay);
				$('#action_def_popup').find('input[data-field="item2"]').val(knxcontrol.action[id].actions[1].item);
				$('#action_def_popup').find('input[data-field="value2"]').val(knxcontrol.action[id].actions[1].value);
				
				$('#action_def_popup').find('input[data-field="delay3"]').val(knxcontrol.action[id].actions[2].delay);
				$('#action_def_popup').find('input[data-field="item3"]').val(knxcontrol.action[id].actions[2].item);
				$('#action_def_popup').find('input[data-field="value3"]').val(knxcontrol.action[id].actions[2].value);
				
				$('#action_def_popup').find('input[data-field="delay4"]').val(knxcontrol.action[id].actions[3].delay);
				$('#action_def_popup').find('input[data-field="item4"]').val(knxcontrol.action[id].actions[3].item);
				$('#action_def_popup').find('input[data-field="value4"]').val(knxcontrol.action[id].actions[3].value);
				
				$('#action_def_popup').find('input[data-field="delay5"]').val(knxcontrol.action[id].actions[4].delay);
				$('#action_def_popup').find('input[data-field="item5"]').val(knxcontrol.action[id].actions[4].item);
				$('#action_def_popup').find('input[data-field="value5"]').val(knxcontrol.action[id].actions[4].value);
				
				$('#action_def_popup').find('#action_def_popup_save').attr('data-id',id);
				$('#action_def_popup').find('#action_def_popup_delete').attr('data-id',id);
			},
			'click a.add': function(event){
				knxcontrol.action.add();
			}
		});		
	},
	update: function(id){
		// check if the action exists in knxcontrol
		if(knxcontrol.action[id]){
			
			// check if the action does not already exists in the DOM
			if(this.element.find('.action_list').find('.action[data-id="'+id+'"]').length==0){

				//add the action to the DOM
				this.element.find('.action_list').append('<div class="action" data-id="'+id+'">'+
															'<div data-field="name"></div>'+
															'<a href="#action_def_popup" class="edit" data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext">Edit</a>'+
														 '</div>').enhanceWithin();
			}
			// update the action
			this.element.find('.action[data-id="'+id+'"]').find('[data-field="name"]').html(knxcontrol.action[id].name);
		}
		else{
			// remove the alarm from the DOM
			this.element.find('.action[data-id="'+id+'"]').remove();
		}
	}
});
$(document).on('click','#action_def_popup_save',function(event){
	id = $(this).attr('data-id');
	$('#action_def_popup').popup('close');
	data_field = ['name','sectionid',
				  'delay1','item1','value1',
				  'delay2','item2','value2',
				  'delay3','item3','value3',
				  'delay4','item4','value4',
				  'delay5','item5','value5'];
	value = [$('#action_def_popup').find('input[data-field="name"]').val(),
			 $('#action_def_popup').find('input[data-field="section_id"]').val(),
			 $('#action_def_popup').find('input[data-field="delay1"]').val(),
			 $('#action_def_popup').find('input[data-field="item1"]').val(),
			 $('#action_def_popup').find('input[data-field="value1"]').val(),
			 $('#action_def_popup').find('input[data-field="delay2"]').val(),
			 $('#action_def_popup').find('input[data-field="item2"]').val(),
			 $('#action_def_popup').find('input[data-field="value2"]').val(),
			 $('#action_def_popup').find('input[data-field="delay3"]').val(),
			 $('#action_def_popup').find('input[data-field="item3"]').val(),
			 $('#action_def_popup').find('input[data-field="value3"]').val(),
			 $('#action_def_popup').find('input[data-field="delay4"]').val(),
			 $('#action_def_popup').find('input[data-field="item4"]').val(),
			 $('#action_def_popup').find('input[data-field="value4"]').val(),
			 $('#action_def_popup').find('input[data-field="delay5"]').val(),
			 $('#action_def_popup').find('input[data-field="item5"]').val(),
			 $('#action_def_popup').find('input[data-field="value5"]').val()];
			 
	knxcontrol.action.update(id,data_field,value);
});
$(document).on('click','#action_def_popup_delete',function(event){
	id = $(this).attr('data-id');
	$('#action_def_popup').popup('close');
	
	knxcontrol.action.del(id);
});

/*****************************************************************************/
/*                     measurement list                                      */
/*****************************************************************************/
$.widget("homecon.measurement_list",{
	options: {
	},
	_create: function(){
		// enhance
		this.element.html('<div class="measurement_list"></div><a href="#" class="add" data-role="button" data-rel="popup">'+language.capitalize(language.add_measurement)+'</a>');
		that = this;
		$.each(knxcontrol.measurement,function(index,measurement){
			if(typeof measurement == 'object'){
				that.update(measurement.id);
			}
		});
		this.element.enhanceWithin();	

		// bind events
		this._on(this.element, {
			'update': function(event,id){
				this.update(id);
			},
			'click a.edit': function(event){
				// populate the popup
				id = $(event.target).parents('.measurement').attr('data-id');
				$('#measurement_def_popup').find('input[data-field="name"]').val(knxcontrol.measurement[id].name);
				$('#measurement_def_popup').find('input[data-field="item"]').val(knxcontrol.measurement[id].item);
				$('#measurement_def_popup').find('input[data-field="quantity"]').val(knxcontrol.measurement[id].quantity);
				$('#measurement_def_popup').find('input[data-field="unit"]').val(knxcontrol.measurement[id].unit);
				$('#measurement_def_popup').find('input[data-field="description"]').val(knxcontrol.measurement[id].description);
				
				$('#measurement_def_popup').find('#measurement_def_popup_save').attr('data-id',id);
			}
		});
	},
	update: function(id){
		// check if the measurement exists in knxcontrol
		if(knxcontrol.measurement[id]){
			
			// check if the measurement does not already exists in the DOM
			if(this.element.find('.measurement_list').find('.measurement[data-id="'+id+'"]').length==0){
				//add the measurement to the DOM
				this.element.find('.measurement_list').append('<div class="measurement" data-id="'+id+'">'+
																'<div class="id" data-field="id">'+id+'</div>'+
																'<div class="name" data-field="name">'+knxcontrol.measurement[id].name+'&nbsp;</div>'+
																'<a href="#measurement_def_popup" class="edit" data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext">Edit</a>'+
															  '</div>').enhanceWithin();
			}
		}
		else{
			// remove the measurement from the DOM
			this.element.find('.measurement[data-id="'+id+'"]').remove();
		}
	}
});
$(document).on('click','#measurement_def_popup_save',function(event){
	id = $(this).attr('data-id');
	$('#measurement_def_popup').popup('close');
	data_field = ['name','item','quantity','unit','description'].join();
	value = [$('#measurement_def_popup').find('input[data-field="name"]').val(),
			 $('#measurement_def_popup').find('input[data-field="item"]').val(),
			 $('#measurement_def_popup').find('input[data-field="quantity"]').val(),
			 $('#measurement_def_popup').find('input[data-field="unit"]').val(),
			 $('#measurement_def_popup').find('input[data-field="description"]').val()].join();
	console.log(id);
	knxcontrol.measurement.update(id,data_field,value);
});

/*****************************************************************************/
/*                     profile list                                          */
/*****************************************************************************/
$.widget('homecon.profile_list',{
	options: {
    },
	_create: function(){
		// enhance
		this.element.html('<div class="profile_list"></div><a href="#" class="add" data-role="button" data-rel="popup">'+language.capitalize(language.add)+'</a>');
		that = this;
		$.each(knxcontrol.profile,function(index,profile){
			if(typeof profile == 'object'){
				that.update(profile.id);
			}
		});
		this.element.enhanceWithin();	

		// bind events
		this._on(this.element, {
			'update': function(event,id){
				this.update(id);
			},
			'click a.add': function(event){
				knxcontrol.profile.add();
				
			},
			'click a.edit': function(event){
				// populate the popup
				id = $(event.target).parents('.profile').attr('data-id');
				$('#profile_def_popup').find('input[data-field="name"]').val(knxcontrol.profile[id].name);
				$('#profile_def_popup').find('input[data-field="quantity"]').val(knxcontrol.profile[id].quantity);
				$('#profile_def_popup').find('input[data-field="unit"]').val(knxcontrol.profile[id].unit);
				$('#profile_def_popup').find('input[data-field="description"]').val(knxcontrol.profile[id].description);
				
				$('#profile_def_popup').find('#profile_def_popup_save').attr('data-id',id);
				$('#profile_def_popup').find('#profile_def_popup_delete').attr('data-id',id);
				
				// add data
				$('#profile_def_popup').find('.profile_def_list').html('<div class="ui-block-a">Time:</div>'+
																	   '<div class="ui-block-b">Value:</div>');
				$.each(knxcontrol.profile[id].data,function(index,data){
				
					// convert timestamp to day of the week and time
					var date = (data[0]-345600*1000)/1000;
					var day = Math.floor(date/24/3600);
					var time = 0+date-day*24*3600;
					hour = Math.floor(time/3600);
					minute = Math.floor((time-hour*3600)/60);
	
					if(hour<10){
						hour = '0'+hour;
					}
					if(minute<10){
						minute = '0'+minute;
					}
					console.log(date);
					console.log(day);
					console.log(hour);
					console.log(minute);
					
					var date_string = language.weekday_short[day]+' '+hour+':'+minute;
					console.log(date_string);

					$('#profile_def_popup').find('.profile_def_list').append('<div class="ui-block-a"><input value="'+date_string+'" data-field="time"/></div>'+
																			 '<div class="ui-block-b"><input value="'+data[1]+'" data-field="value"/></div>');
				});
				$('#profile_def_popup').find('.profile_def_list').enhanceWithin();
			}
		});
	},
	update: function(id){
		// check if the profile exists in knxcontrol
		if(knxcontrol.profile[id]){
			// check if the measurement does not already exists in the DOM
			if(this.element.find('.profile_list').find('.profile[data-id="'+id+'"]').length==0){
				//add the measurement to the DOM
				this.element.find('.profile_list').append('<div class="profile" data-id="'+id+'">'+
														  '</div>');
			}
			// update
			this.element.find('.profile[data-id="'+id+'"]').html('<div class="chart_container"></div>'+
																 '<div class="data">'+
																	'<div class="id" data-field="id">'+id+'</div>'+
																	'<div class="name" data-field="name">'+knxcontrol.profile[id].name+'&nbsp;</div>'+
																	'<a href="#profile_def_popup" class="edit" data-role="button" data-rel="popup" data-icon="grid">Edit</a>'+
																 '</div>').enhanceWithin();
			// update chart
			var tempdata = knxcontrol.profile[id].data.slice();
			if(knxcontrol.profile[id].data[0][0] > 0){
				// add last data point at time 0 to obtain a cyclic signal
				tempdata.unshift([0,tempdata[tempdata.length-1][1]]);
			}
			if(knxcontrol.profile[id].data[knxcontrol.profile[id].data.length-1][0] < 604800*1000){
				tempdata.push([604800*1000,tempdata[tempdata.length-1][1]]);
			}
			// update time to start on monday 0h
			$.each(tempdata,function(index,value){
				tempdata[index][0] = tempdata[index][0]+4*24*3600*1000;
			});
			
			this.chart_options.series[0].data = tempdata;
			this.chart_options.yAxis.title = {text: knxcontrol.profile[id].unit};
			$(this.element).find('.profile[data-id="'+id+'"] div.chart_container').highcharts(this.chart_options);
			
		}
		else{
			// remove the measurement from the DOM
			this.element.find('.profile[data-id="'+id+'"]').remove();
		}
	},
	chart_options: {
		chart: {
			type: 'line',
			margin: [20, 20, 30, 60]
		},
		plotOptions: {
			line: {
				marker: { 
					enabled: false
				}
			}
		},
		legend: {
			enabled: false
		},
		title: {
			text: ''
		},
		xAxis: {
			type: 'datetime',
			ordinal: false,
			dateTimeLabelFormats: {
				millisecond: '%H:%M:%S.%L',
				second: '%H:%M:%S',
				minute: '%H:%M',
				hour: '%H:%M',
				day: '%a %H:%M',
				week: '%a %H:%M'
			}
		},
		yAxis:{
			title: {}
		},
		tooltip: {
			xDateFormat: '%a %H:%M',
			valueDecimals: 1,
			shared: true
		},
		series: [{
			name: '',
			step: true,
			data: []
		}]
	}
});
$(document).on('click','#profile_def_popup_save',function(event){
	id = $(this).attr('data-id');
	$('#profile_def_popup').popup('close');
	var field = ['name','quantity','unit','description'].join(';');
	var value = [$('#profile_def_popup').find('input[data-field="name"]').val(),
			     $('#profile_def_popup').find('input[data-field="quantity"]').val(),
			     $('#profile_def_popup').find('input[data-field="unit"]').val(),
			     $('#profile_def_popup').find('input[data-field="description"]').val()].join(';');

	knxcontrol.profile.update(id,field,value);
		
	
	var time = [];
	var value = [];
	$.each( $('#profile_def_popup div.profile_def_list').find('[data-field="time"]'),function(index,datestr){
		// convert datestring to timestamp
		var datestr = $(datestr).val();
		var dateParts = datestr.split(' ');
		
		var day = language.weekday_short.indexOf(dateParts[0]);
		var timeParts = dateParts[1].split(':');
		
		var timestamp = day*24*3600 + timeParts[0]*3600 + timeParts[1]*60;
		console.log(timestamp);
	
		time.push(timestamp);
	});
	$.each( $('#profile_def_popup div.profile_def_list').find('[data-field="value"]'),function(index,data){
		value.push($(data).val());
	});
	

	knxcontrol.profile.update_data(id,time,value);
});
$(document).on('click','#profile_def_popup_addrow',function(event){
	$('#profile_def_popup').find('.profile_def_list').append('<div class="ui-block-a"><input value="0" data-field="time"/></div>'+
															 '<div class="ui-block-b"><input value="0" data-field="value"/></div>');
	$('#profile_def_popup').find('.profile_def_list').enhanceWithin();
});
$(document).on('click','#profile_def_popup_delete',function(event){
	id = $(this).attr('data-id');
	$('#profile_def_popup').popup('close');
	knxcontrol.profile.del(id);
});

/*****************************************************************************/
/*                     ventilation control                                   */
/*****************************************************************************/
$.widget('homecon.ventilation_control',{
	options: {
		label: '',
		item: 'building.ventilation.speedcontrol',
		src_auto_off: 'icons/ffffff/vent_ventilation_level_automatic.png',
		src_auto_on: 'icons/f79a1f/vent_ventilation_level_automatic.png',
		src_0_off: 'icons/ffffff/vent_ventilation_level_0.png',
		src_1_off: 'icons/ffffff/vent_ventilation_level_1.png',
		src_2_off: 'icons/ffffff/vent_ventilation_level_2.png',
		src_3_off: 'icons/ffffff/vent_ventilation_level_3.png',
		src_0_on: 'icons/f79a1f/vent_ventilation_level_0.png',
		src_1_on: 'icons/f79a1f/vent_ventilation_level_1.png',
		src_2_on: 'icons/f79a1f/vent_ventilation_level_2.png',
		src_3_on: 'icons/f79a1f/vent_ventilation_level_3.png'
    },
	
	_create: function(){
		// enhance
		this.element.prepend('<p>'+this.options.label+'</p>'+
							 '<!--<a href="#" class="auto"><img src="'+this.options.src_auto_off+'"></a>-->'+
							 '<div class="speedcontrol">'+
								'<a href="#" data-value="0"><img src="'+this.options.src_0_off+'"></a>'+
								'<a href="#" data-value="1"><img src="'+this.options.src_1_off+'"></a>'+
								'<a href="#" data-value="2"><img src="'+this.options.src_2_off+'"></a>'+
								'<a href="#" data-value="3"><img src="'+this.options.src_3_off+'"></a>'+
							 '</div>').enhanceWithin();
		this.update();
		
		// bind events
		this._on(this.element, {
            'click div.speedcontrol a': function(event){
				// update the value in smarthome
				smarthome.write(this.options.item, $(event.target).parents('a').attr('data-value'));
			},
			'update': function(event){
				this.update();
			}
        });
	},
	update: function(){
		var item = this.options.item;
		var speedcontrol = item+'.speedcontrol';
		
		if(knxcontrol.item[item]==0){
			this.element.find('a[data-value="0"] img').attr('src',this.options.src_0_on);
			this.element.find('a[data-value="1"] img').attr('src',this.options.src_1_off);
			this.element.find('a[data-value="2"] img').attr('src',this.options.src_2_off);
			this.element.find('a[data-value="3"] img').attr('src',this.options.src_3_off);
		}
		else if(knxcontrol.item[item]==1){
			this.element.find('a[data-value="0"] img').attr('src',this.options.src_0_off);
			this.element.find('a[data-value="1"] img').attr('src',this.options.src_1_on);
			this.element.find('a[data-value="2"] img').attr('src',this.options.src_2_off);
			this.element.find('a[data-value="3"] img').attr('src',this.options.src_3_off);
		}
		else if(knxcontrol.item[item]==2){
			this.element.find('a[data-value="0"] img').attr('src',this.options.src_0_off);
			this.element.find('a[data-value="1"] img').attr('src',this.options.src_1_off);
			this.element.find('a[data-value="2"] img').attr('src',this.options.src_2_on);
			this.element.find('a[data-value="3"] img').attr('src',this.options.src_3_off);
		}
		else if(knxcontrol.item[item]==3){
			this.element.find('a[data-value="0"]  img').attr('src',this.options.src_0_off);
			this.element.find('a[data-value="1"]  img').attr('src',this.options.src_1_off);
			this.element.find('a[data-value="2"]  img').attr('src',this.options.src_2_off);
			this.element.find('a[data-value="3"]  img').attr('src',this.options.src_3_on);
		}
	}

});

/*****************************************************************************/
/*                     smarthome log                                         */
/*****************************************************************************/
$.widget("homecon.smarthome_log",{
	options: {
	},
	_create: function(){
		// enhance
		this.element.html('');
		this.element.enhanceWithin();	
		this.update();
		
		// bind events
		this._on(this.element, {
			'update': function(event,id,data){			
				this.update();
			},
		});
	},
	update: function(){
		that = this;

		that.element.empty();
		
		$.each(knxcontrol.smarthome_log.log,function(index,value){
			var date = new Date(value.time);
			var hour = date.getHours();
			var minute = date.getMinutes();
			var second = date.getSeconds();
			if(hour<10){
				hour = '0'+hour;
			}
			if(minute<10){
				minute = '0'+minute;
			}
			if(second<10){
				second = '0'+second;
			}

			date_string = date.getDate()+'-'+(date.getMonth()+1)+'-'+date.getFullYear()+', '+hour+':'+minute+':'+second;

		
			that.element.append('<div><div class="time">'+date_string+'</div><div class="message">'+value.level+':'+value.message+'</div></div>')
		});
	}
});

/*****************************************************************************/
/*                     users list                                            */
/*****************************************************************************/
$.widget("homecon.user_list",{
	options: {
	},
	_create: function(){
		this.element.html('<div class="user_list"></div><a href="#" class="add" data-role="button" data-rel="popup">'+language.capitalize(language.add_user)+'</a>');
		var that = this;
		$.each(knxcontrol.user,function(index,user){
			if(typeof user == 'object'){
				that.update(user.id);
			}
		});
		this.element.enhanceWithin();	

		// bind events
		this._on(this.element, {
			'update': function(event,id){
				this.update(id);
			},
			'click a.edit': function(event){
				// populate the popup
				id = $(event.target).parents('.user').attr('data-id');
				$('#user_def_popup').find('input[data-field="name"]').val(knxcontrol.user[id].username);
				
				$('#user_def_popup').find('#user_def_popup_save').attr('data-id',id);
			}
		});
	},
	update: function(id){
		// check if the user exists in knxcontrol
		if(knxcontrol.user[id]){
			
			// check if the user does not already exists in the DOM
			if(this.element.find('.user_list').find('.user[data-id="'+id+'"]').length==0){
				//add the user to the DOM
				this.element.find('.user_list').append('<div class="user" data-id="'+id+'">'+
															'<div class="name" data-field="name">'+knxcontrol.user[id].username+'&nbsp;</div>'+
															'<a href="#user_def_popup" class="edit" data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext">Edit</a>'+
													   '</div>').enhanceWithin();
			}
			else{
				// update the user in the DOM
				this.element.find('.user_list').find('.user[data-id="'+id+'"]').html('<div class="user" data-id="'+id+'">'+
																						'<div class="name" data-field="name">'+knxcontrol.user[id].username+'&nbsp;</div>'+
																						'<a href="#user_def_popup" class="edit" data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext">Edit</a>'+
																					 '</div>').enhanceWithin();
			}
		}
		else{
			// remove the user from the DOM
			this.element.find('.user[data-id="'+id+'"]').remove();
		}
	}
});
$(document).on('click','#user_def_popup_save',function(event){
	id = $(this).attr('data-id');
	$('#user_def_popup').popup('close');
	field = ['username'];
	value = [$('#user_def_popup').find('input[data-field="name"]').val()];
	console.log(id);
	knxcontrol.user.update(id,field,value);
});
/*****************************************************************************/
/*                     user profile                                          */
/*****************************************************************************/
$.widget("homecon.user_profile",{
	options: {
	},
	_create: function(){
		var id = knxcontrol.user_id;
		this.element.html('<div class="user" data-id="'+id+'">'+
							'<div class="name" data-field="name">'+knxcontrol.user[id].username+'&nbsp;</div>'+
							'<a href="#user_def_popup" class="edit" data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext">Edit</a>'+
					     '</div><a href="#" class="delete" data-role="button" data-rel="popup">'+language.capitalize(language.delete_user)+'</a>');
		this.element.enhanceWithin();	

		// bind events
		this._on(this.element, {
			'update': function(event){
				this.update();
			},
			'click a.edit': function(event){
				// populate the popup
				var id = knxcontrol.user_id;
				$('#password_def_popup').find('input[data-field="name"]').val(knxcontrol.user[id].username);
				
				$('#password_def_popup').find('#password_def_popup_save').attr('data-id',id);
			}
		});
	},
	update: function(){
		// check if the user exists in knxcontrol
		var id = knxcontrol.user[knxcontrol.user_id];
		if(id){
			// update user to the DOM
			this.element.find('.name').html(knxcontrol.user[id].username).enhanceWithin();
		}
		else{
			// remove the user from the DOM
			this.element.find('.user[data-id="'+id+'"]').remove();
		}
	}
});
$(document).on('click','#password_def_popup_save',function(event){
	id = $(this).attr('data-id');
	$('#user_def_popup').popup('close');
	field = ['username'];
	value = [$('#user_def_popup').find('input[data-field="name"]').val()];
	console.log(id);
	//knxcontrol.user.update(id,field,value);
});



/*****************************************************************************/
/*                     system identification                                 */
/*****************************************************************************/
$.widget("homecon.system_identification",{
	options: {
	},
	_create: function(){
		this.element.html('<div class="buttons">'+
						      '<div class="twocols"><div data-role="btn" data-label="Identify" data-item="knxcontrol.mpc.model.identification" data-value=1></div></div>'+
						      '<div class="twocols"><div data-role="btn" data-label="Validate" data-item="knxcontrol.mpc.model.validation" data-value=1></div></div>'+
						  '</div>'+
						  '<div class="chart_container">'+
						  '</div>');

		$('div[data-role="btn"]').btn();

		Highcharts.setOptions({
			global: {
				useUTC: false
			}
		});

		this.chart_options.chart.type = 'line';
		this.chart_options.xAxis.range = 2 * 24 * 3600 * 1000;
		this.chart_options.tooltip.xDateFormat='%Y-%m-%d %H:%M';
		$(this.element).children('.chart_container').highcharts('StockChart',this.chart_options);
		this.chart = $(this.element).children('.chart_container').highcharts();
		this.chart.reflow()

		this.element.enhanceWithin();	

		// bind events
		this._on(this.element, {
			'update': function(event){
				this.update();
			}
		});
	},
	update: function(){
		var that = this;

		console.log(knxcontrol.item['knxcontrol.mpc.model.validation.result']['measured_states'])

		// remove all data from the chart
		//while(that.chart.series.length > 0){
		//	that.chart.series[0].remove(true);
		//}

		$.each((knxcontrol.item['knxcontrol.mpc.model.validation.result']['measured_states']),function(index,value){
			that.chart.addSeries({                        
    			name: index+' measurement',
    			data: value['measurement']
			}, false);
			that.chart.addSeries({                        
    			name: index+' simulation',
    			data: value['simulation']
			}, false);
			that.chart.redraw();
		});
		
	},
	chart: {},
	chart_options: {
		chart: {
		},
		title: {
			text: ''
		},
		xAxis: {
			type: 'datetime',
			ordinal: false
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
});
