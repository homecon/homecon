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
//


/*****************************************************************************/
/*                     separation line                                       */
/*****************************************************************************/
$.widget('knxcontrol.line',{
	options: {
		line: 'true'
    },
	_create: function(){
		// enhance
		if(this.options.line){
			this.element.addClass("line");
		}
	},
});

/*****************************************************************************/
/*                     display value                                         */
/*****************************************************************************/
$.widget('knxcontrol.displayvalue',{
	options: {
      item: '',
	  digits: 1
    },
	_create: function(){
		// enhance
		this.update();
		
		// bind events
		this._on(this.element, {
			'update': function(event){	
				this.update();
			}
		});
	},
	update: function(){
		var item = this.options.item;
		var rounding = Math.pow(10,this.options.digits);
		
		var value = Math.round(knxcontrol.item[item]*rounding)/rounding;
		
		this.element.html(value);
	}
});

/*****************************************************************************/
/*                     button                                                */
/*****************************************************************************/
$.widget('knxcontrol.btn',{
	options: {
		label: '',
		item: '',
		value: '',
		src: '',
    },
	
	_create: function(){
		// enhance
		this.element.append('<a data-role="button" data-corners="false">'+this.options.label+'</a>');
		if(this.options.src!=''){
			this.element.append('<img src="'+this.options.src+'"/>');
		}
		this.element.enhanceWithin();
	
		// bind events
		this._on(this.element, {
            'click a': function(event){
				// update the value in smarthome
				smarthome.write(this.options.item, this.options.value);
			},
        });
	}
});

/*****************************************************************************/
/*                     light switch                                          */
/*****************************************************************************/
$.widget('knxcontrol.lightswitch',{
	options: {
		label: '',
		item: '',
		src_on: 'icons/f79a1f/light_light.png',
		src_off: 'icons/ffffff/light_light.png',
    },
	
	_create: function(){
		// enhance
		this.element.prepend('<a href="#" class="switch"><img src="'+this.options.src_off+'">'+this.options.label+'</a>');
		this.update();
		
		// bind events
		this._on(this.element, {
            'click a.switch': function(event){
				var item = this.options.item;
				// update the value in smarthome
				smarthome.write(item, (knxcontrol.item[item]+1)%2);
			},
			'update': function(event){
				this.update();
			}
        });
	},
	update: function(){
		var item = this.options.item;
				
		if(knxcontrol.item[item]){
			this.element.find('img').attr('src',this.options.src_on);
		}
		else{
			this.element.find('img').attr('src',this.options.src_off);
		}
	}

});

/*****************************************************************************/
/*                     light dimmer                                          */
/*****************************************************************************/
$.widget("knxcontrol.lightdimmer",{
	options: {
		label: '', 
		item: '',
		src_on: 'icons/f79a1f/light_light.png',
		src_off: 'icons/ffffff/light_light.png',
		val_on: 255,
		val_off: 0
    },
	lock: false,
	_create: function(){
		// enhance
		this.element.prepend('<p>'+this.options.label+'</p>'+
							 '<a href="#" class="switch"><img src="icons/ffffff/light_light.png"></a>'+
							 '<input type="range" value="'+this.options.val_off+'" min="'+this.options.val_off+'" max="'+this.options.val_on+'" step="'+(this.options.val_on-this.options.val_off)/51+'" data-highlight="true"/>');
		this.element.enhanceWithin();
		this.update();

		// bind events
		this._on(this.element, {
			'change input': function(event){
				var item = this.options.item;
				if(!this.lock){
					smarthome.write(item, this.element.find('input').val());
				}
			},
            'click a.switch': function(event){
				var item = this.options.item;
				// update the value in smarthome
				if( knxcontrol.item[item] > this.options.val_off){
					smarthome.write(item, this.options.val_off);
				}
				else{
					smarthome.write(item, this.options.val_on);
				}
			},
			'update': function(event){
				this.update();
			}
        });
	},
	update: function(){
		this.lock = true;
		//console.log(this.options.item+' locked');
		var that = this;
		setTimeout(function(){
			that.lock = false;
			//console.log(that.options.item+' unlocked');
		},500);
		
		var item = this.options.item;
		this.element.find('input').val(knxcontrol.item[item]).slider('refresh');
	
		if(knxcontrol.item[item]>this.options.val_off){
			this.element.find('img').attr('src',this.options.src_on);
		}
		else{
			this.element.find('img').attr('src',this.options.src_off);
		}
	}
});

/*****************************************************************************/
/*                     shading                                               */
/*****************************************************************************/ 
$.widget("knxcontrol.shading",{
	options: {
		label: '',
		item: '',
		val_on: 255,
		val_off: 0
    },
	_create: function(){
		// enhance
		var text = this.element.html();
		this.element.prepend('<p>'+this.options.label+'</p>'+
							 '<a href="#" class="open"><img src="icons/ffffff/fts_shutter_10.png"></a>'+
							 '<a href="#" class="close"><img src="icons/ffffff/fts_shutter_100.png"></a>'+
							 '<input type="range" value="'+this.options.val_off+'" min="'+this.options.val_off+'" max="'+this.options.val_on+'" step="'+(this.options.val_on-this.options.val_off)/51+'" data-highlight="true"/>');
		this.element.enhanceWithin();
		this.update();
		
		// bind events
		this._on(this.element, {
			'change input': function(event){
				var item = this.options.item;
				if(!this.lock){
					smarthome.write(item, this.element.find('input').val());
				}
			},
            'click a.open': function(event){
				var item = this.options.item;
				smarthome.write(item, this.options.val_off);
			},
			'click a.close': function(event){
				var item = this.options.item;
				smarthome.write(item, this.options.val_on);
			},
			'update': function(event){
				this.update();
			}
        });
	},
	update: function(){
		this.lock = true;
		//console.log(this.options.item+' locked');
		var that = this;
		setTimeout(function(){
			that.lock = false;
			//console.log(that.options.item+' unlocked');
		},500);
		
		
		var item = this.options.item;

		this.element.find('input').val(knxcontrol.item[item]).slider('refresh');
	}
});

/*****************************************************************************/
/*                     clock                                                 */
/*****************************************************************************/ 
$.widget("knxcontrol.clock",{
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

		if( h2 != this.h2_current){
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
$.widget("knxcontrol.weather_block",{
	options: {
		item: 'building.weatherforecast',
		item_temperature: '',
		item_windspeed: '',
		item_winddirection: '',
		item_irradiation: '',
		mini: false,
		daysahead: -1
    },
	_create: function(){
		// enhance
		this.element.append('<div data-field="date"></div>'+
							'<img src="icons/weather/blank.png">'+
							'<div data-field="temperature"></div>'+
							'<div data-field="wind"></div>'+
							'<div data-field="irradiation"></div>'
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
		if(knxcontrol.item['building.weatherforecast']){
			if(this.options.daysahead>=0){
				// find noon of the correct day
				for(var index = 0+Math.max(0,(this.options.daysahead-1)*8);index<knxcontrol.item['building.weatherforecast'].length;index++){
					date = new Date(knxcontrol.item['building.weatherforecast'][index].datetime*1000);
					if((date.getHours()>11 && date.getHours()<15)) break;
				}
			}
			else{
				index = 0;
			}
			
			if(index < knxcontrol.item['building.weatherforecast'].length){
				
				this.element.find('img').attr('src','icons/weather/'+this.icons[knxcontrol.item['building.weatherforecast'][index].icon]);
				
				var temperature = 0;
				var windspeed = 0;
				var winddirection = '';
				var irradiation = 0;
				
				
				date = new Date(knxcontrol.item['building.weatherforecast'][index].datetime*1000);
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
					temperature = knxcontrol.item['building.weatherforecast'][index].temperature;
				}
				else{
					temperature = knxcontrol.item[this.options.item_temperature];
				}
				if(this.options.item_windspeed == ''){
					windspeed = knxcontrol.item['building.weatherforecast'][index].wind_speed;
				}
				else{
					windspeed = knxcontrol.item[this.options.item_windspeed];
				}
				if(this.options.item_winddirection == ''){
					winddirection = language.winddirection(knxcontrol.item['building.weatherforecast'][index].wind_direction)
				}
				else{
					winddirection = language.winddirection(knxcontrol.item[this.options.item_winddirection]);
				}
				if(this.options.item_irradiation == ''){
					irradiation = knxcontrol.item['building.weatherforecast'][index].cloudfactor;
				}
				else{
					irradiation = knxcontrol.item[this.options.item_irradiation];
				}
				
				if(this.options.mini){
					this.element.find('[data-field="date"]').html(date_string);
					this.element.find('[data-field="temperature"]').html(Math.round(temperature)/10+'&deg;C');
					this.element.find('[data-field="wind"]').html(Math.round(windspeed*1)/1+' m/s '+ winddirection);
					this.element.find('[data-field="irradiation"]').html(Math.round(irradiation*1)/1+' W/m<sup>2</sup>');
				}
				else{
					this.element.find('[data-field="temperature"]').html(language.capitalize(language.temperature)+': '+Math.round(temperature)/10+'&deg;C');
					this.element.find('[data-field="wind"]').html(language.capitalize(language.wind)+': '+Math.round(windspeed*1)/1+' m/s '+ winddirection);
					this.element.find('[data-field="irradiation"]').html(language.capitalize(language.irradiation)+': '+Math.round(irradiation*1)/1+' W/m<sup>2</sup>');
				}
			}
			else{
				this.element.find('img').attr('src','icons/weather/na.png');
				
				this.element.find('[data-field="date"]').html('-');
				this.element.find('[data-field="temperature"]').html('-');
				this.element.find('[data-field="wind"]').html('-');
				this.element.find('[data-field="irradiation"]').html('-');
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
$.widget("knxcontrol.alarm",{
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
/*                     action list                                           */
/*****************************************************************************/
$.widget("knxcontrol.action_list",{
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
$.widget("knxcontrol.measurement_list",{
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
/*                     measurement export                                    */
/*****************************************************************************/
$.widget("knxcontrol.measurement_export",{
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
$.widget("knxcontrol.settings",{
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
$.widget('knxcontrol.chart',{
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
/*                     profile list                                          */
/*****************************************************************************/
$.widget('knxcontrol.profile_list',{
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
			var tempdata = knxcontrol.profile[id].data;
			if(tempdata[0][0] > 0){
				// add last data point at time 0 to obtain a cyclic signal
				tempdata.unshift([0,tempdata[tempdata.length-1][1]]);
			}
			
			this.chart_options.series[0].data = tempdata;
			this.chart_options.yAxis.title({text: knxcontrol.profile[id].unit});
			$(this.element).children('.profile[data-id="'+id+'"] .chart_container').highcharts(this.chart_options);
			
		}
		else{
			// remove the measurement from the DOM
			this.element.find('.profile[data-id="'+id+'"]').remove();
		}
	},
	chart_options: {
		chart: {
			type: 'line',
			margin: [20, 20, 20, 70]
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



/*****************************************************************************/
/*                     smarthome log                                         */
/*****************************************************************************/
$.widget("knxcontrol.smarthome_log",{
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
		this.element.empty();
		
		that = this;
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
$.widget("knxcontrol.user_list",{
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
$.widget("knxcontrol.user_profile",{
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
