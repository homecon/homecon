//
// 
// widget.js is part of KNXControl
// @author: Brecht Baeten
// @license: GNU GENERAL PUBLIC LICENSE
// 
//

/*****************************************************************************/
/*                     Templates                                             */
/*****************************************************************************/
var template = {
	alarm: '',
	action_select: '',
	action: '',
	measurement: ''
};

$(document).on('pagebeforecreate',function(){
	$.each(template,function(key,value){
		template[key] = $('#templates .'+key).prop('outerHTML');
	});
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
/*                     light switch                                          */
/*****************************************************************************/                                                             //
$.widget('knxcontrol.lightswitch',{
	options: {
		label: '',
		item: '',
		src_on: 'icons/or/light_light.png',
		src_off: 'icons/ws/light_light.png',
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
/*****************************************************************************/                                                             //
$.widget("knxcontrol.lightdimmer",{
	options: {
		label: '', 
		item: '',
		src_on: 'icons/or/light_light.png',
		src_off: 'icons/ws/light_light.png',
		val_on: 255,
		val_off: 0
    },
	lock: false,
	_create: function(){
		// enhance
		this.element.prepend('<p>'+this.options.label+'</p><a href="#" class="switch"><img src="icons/ws/light_light.png"></a><input type="range" value="'+this.options.val_off+'" min="'+this.options.val_off+'" max="'+this.options.val_on+'" step="'+(this.options.val_on-this.options.val_off)/51+'" data-highlight="true"/>');
		this.element.enhanceWithin();
		this.update();
		
		// bind events
		this._on(this.element, {
			'change input': function(event){
				var item = this.options.item;
				if(!this.lock){
					knxcontrol.item.update(item,this.element.find('input').val());
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
		this.element.prepend('<p>'+this.options.label+'</p><a href="#" class="open"><img src="icons/ws/fts_shutter_10.png"></a><a href="#" class="close"><img src="icons/ws/fts_shutter_100.png"></a><input type="range" value="'+this.options.val_off+'" min="'+this.options.val_off+'" max="'+this.options.val_on+'" step="'+(this.options.val_on-this.options.val_off)/51+'" data-highlight="true"/>');
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
		this.element.prepend('<div class="time"><div><img class="bg" src="icons/clock/clockbg1.png"><img class="hoursLeft" src="icons/clock/0.png"/><img class="hoursRight" src="icons/clock/1.png"/><hr></div><div><img class="bg" src="icons/clock/clockbg1.png"><img class="minutesLeft" src="icons/clock/2.png"/><img class="minutesRight" src="icons/clock/3.png"/><hr></div></div><div class="date">1 januari 2015</div>');
		this.element.enhanceWithin();
		
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
		
		that = this;
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
/*                     current weather                                       */
/*****************************************************************************/ 
$.widget("knxcontrol.current_weather",{
	options: {
		item: '',
		item_temperature: '',
		item_windspeed: '',
		item_winddirection: '',
		item_irradiation: ''
    },
	_create: function(){
		// enhance
		this.element.prepend('<img src="icons/weather/blank.png"><div><span data-role="displayvalue" data-item="'+this.options.item_temperature+'"></span>&deg;C</div><div><span data-role="displayvalue" data-item="'+this.options.item_windspeed+'"></span>m/s <span data-role="displayvalue" data-item="'+this.options.item_winddirection+'">m/s</span></div><div><span data-role="displayvalue" data-item="'+this.options.item_irradiation+'"></span>W/m<sup>2</sup></div>');
		this.element.enhanceWithin();
		
		// bind events
		this._on(this.document,{
			
			'weatherforecastupdate': function(){
				this.element.find('img').attr('src','icons/weather/'+this.icons[knxcontrol.weatherforecast[0].icon]);
				/*
				var temperature = 0;
				var windspeed = 0;
				var winddirection = '';
				var irradiation = 0;
				
				if(this.options.item_temperature == ''){temperature = knxcontrol.weatherforecast[0].temperature;}
				else{console.log(knxcontrol.item[this.options.item_temperature]); temperature = knxcontrol.item[this.options.item_temperature];}
				if(this.options.item_windspeed == ''){windspeed = knxcontrol.weatherforecast[0].windspeed;}
				else{windspeed = knxcontrol.item[this.options.item_windspeed];}
				if(this.options.item_winddirection == ''){winddirection = language.winddirection(knxcontrol.weatherforecast[0].winddirection)}
				else{winddirection = language.winddirection(knxcontrol.item[this.options.item_winddirection]);}
				if(this.options.item_windspeed == ''){irradiation = knxcontrol.weatherforecast[0].cloudfactor;}
				else{irradiation = knxcontrol.weatherforecast[0].cloudfactor;}
				
				this.element.find('.temperature').html(language.capitalize(language.temperature)+': '+Math.round(temperature)/10+'&deg;C');
				this.element.find('.wind').html(language.capitalize(language.wind)+': '+Math.round(windspeed*1)/1+' m/s '+ winddirection);
				this.element.find('.irradiation').html(language.capitalize(language.irradiation)+': '+Math.round(irradiation*1)/1+' W/m<sup>2</sup>');
				*/
			}
		});
	},
	icons: {'01d': 'sun_1.png','02d': 'sun_3.png','03d': 'cloud_4.png','04d': 'cloud_5.png','09d': 'cloud_7.png','10d': 'sun_7.png' ,'11d': 'cloud_10.png','13d': 'cloud_13.png','50d': 'sun_6.png','01n': 'moon_1.png','02n': 'moon_3.png','03n': 'cloud_4.png','04n': 'cloud_5.png','09n': 'cloud_7.png','10n': 'moon_7.png','11n': 'cloud_10.png','13n': 'cloud_13.png','50n': 'moon_6.png'}
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
					knxcontrol.alarm.update(alarm_id,'hour',hour);
					knxcontrol.alarm.update(alarm_id,'minute',minute);
				}
				else if(field=='action_id'){
					value = $(event.target).val();
					knxcontrol.alarm.update(alarm_id,field,value);
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
					//set ids
					var newobject = template.alarm;
					
					//newobject = newobject.replace(/_0/g, "_"+id);
					newobject = newobject.replace(/Select action/g, language.capitalize(language.select_action));

					//add the alarm to the DOM
					this.element.find('.alarm_list').append(newobject).enhanceWithin();
					this.element.find('.alarm[data-id="0"]').attr('data-id',id);
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
			// check if the action option exists
			if(this.element.find('option [data-id="'+id+'"]').length==0){	
				// add the action to the select list
				var newobject = template.action_select;
				newobject = newobject.replace(/0/g, id);
				this.element.find('div.alarm_action select').append(newobject).selectmenu('refresh');
			}
			// update the option
			this.element.find('option[data-id="'+id+'"]').html(knxcontrol.action[id].name);
			
			// check if it is the selected option
			that = this;
			$.each(this.element.find('.alarm'),function(index,object){
				alarm_id = $(object).attr('data-id');
				if(knxcontrol.alarm[alarm_id].id==id){
					that.element.find('.alarm[data-id="'+alarm_id+'"]').find('option[data-id="'+id+'"]').attr('selected', true).siblings('option').removeAttr('selected');
				}
			});
			
			
			this.element.find('select').selectmenu('refresh');
			// select action
			//this.element.find('div.alarm_action select').val(knxcontrol.alarm[alarm_id].id).selectmenu('refresh');
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
		this.element.html('<div class="action_list"></div><a href="#" class="add" data-role="button" data-rel="popup">'+language.capitalize(language.add_action)+'</a>');
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
			},
			'click a.add': function(event){
				knxcontrol.action.add();
			},
			'click a.delete': function(event){
				id = $(event.target).parents('.action').attr('data-id');
				knxcontrol.action.del(id);
			}
		});		
	},
	update: function(id){
		// check if the action exists in knxcontrol
		if(knxcontrol.action[id]){
			
			// check if the action does not already exists in the DOM
			if(this.element.find('.action_list').find('.action[data-id="'+id+'"]').length==0){
				//set ids
				var newobject = template.action;
				
				newobject = newobject.replace(/_0/g, "_"+id);
				
				//add the action to the DOM
				this.element.find('.action_list').append(newobject).enhanceWithin();
				this.element.find('.action[data-id="0"]').attr('data-id',id);
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
	data_field = ['name','sectionid','delay1','item1','value1','delay2','item2','value2','delay3','item3','value3','delay4','item4','value4','delay5','item5','value5'].join();
	value = [$('#action_def_popup').find('input[data-field="name"]').val(),$('#action_def_popup').find('input[data-field="section_id"]').val(),$('#action_def_popup').find('input[data-field="delay1"]').val(),$('#action_def_popup').find('input[data-field="item1"]').val(),$('#action_def_popup').find('input[data-field="value1"]').val(),$('#action_def_popup').find('input[data-field="delay2"]').val(),$('#action_def_popup').find('input[data-field="item2"]').val(),$('#action_def_popup').find('input[data-field="value2"]').val(),$('#action_def_popup').find('input[data-field="delay3"]').val(),$('#action_def_popup').find('input[data-field="item3"]').val(),$('#action_def_popup').find('input[data-field="value3"]').val(),$('#action_def_popup').find('input[data-field="delay4"]').val(),$('#action_def_popup').find('input[data-field="item4"]').val(),$('#action_def_popup').find('input[data-field="value4"]').val(),$('#action_def_popup').find('input[data-field="delay5"]').val(),$('#action_def_popup').find('input[data-field="item5"]').val(),$('#action_def_popup').find('input[data-field="value5"]').val()].join();
	
	knxcontrol.action.update(id,data_field,value);
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
				//set ids
				var newobject = template.measurement;
				
				newobject = newobject.replace(/_0/g, "_"+id);
				
				//add the measurement to the DOM
				this.element.find('.measurement_list').append(newobject).enhanceWithin();
				this.element.find('.measurement[data-id="0"]').attr('data-id',id);
			}
			// update the measurement
			this.element.find('.measurement[data-id="'+id+'"]').find('[data-field="id"]').html(id);
			this.element.find('.measurement[data-id="'+id+'"]').find('[data-field="name"]').html(knxcontrol.measurement[id].name+'&nbsp;');
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
	value = [$('#measurement_def_popup').find('input[data-field="name"]').val(),$('#measurement_def_popup').find('input[data-field="item"]').val(),$('#measurement_def_popup').find('input[data-field="quantity"]').val(),$('#measurement_def_popup').find('input[data-field="unit"]').val(),$('#measurement_def_popup').find('input[data-field="description"]').val()].join();
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
/*                     chart                                                 */
/*****************************************************************************/
$.widget('knxcontrol.chart',{
	options: {
      signals: '',
	  type: 'line'
    },
	_create: function(){
		
		// Enhance
		Highcharts.setOptions({
			global: {
				useUTC: false
			}
		});
		
		this.chart_options.chart.type = this.options.type;
		
		if(this.options.type == 'line'){
			this.chart_options.xAxis.range = 2 * 24 * 3600 * 1000;
			this.chart_options.tooltip.xDateFormat='%Y-%m-%d %H:%M';
			$(this.element).highcharts('StockChart',this.chart_options);
		}
		else{
			$(this.element).highcharts(this.chart_options);
		}
		
		this.chart = $(this.element).highcharts();
		//this.update(this.options.signals);
		
		// bind events
		this._on(this.element, {
			'update': function(event,id){			
				this.update(id);
			},
			'get_data': function(event){			
				this.get_data();
			}
		});
	},
	update: function(id){
		this.chart.addSeries({name: 'test' ,data: knxcontrol.measurement[id].data});
	},
	get_data: function(){
		$.each((''+this.options.signals).split(),function(index,id){
			knxcontrol.measurement.get_data(id);
		});
		
	},
	chart: {},
	chart_options: {
		chart: {
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
});