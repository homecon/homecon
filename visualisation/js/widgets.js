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
	action_def: ''
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
		item: '',
		src_on: 'icons/or/light_light.png',
		src_off: 'icons/ws/light_light.png',
    },
	
	_create: function(){
		// enhance
		var text = this.element.html();
		this.element.html('<a href="#"><img src="'+this.options.src_off+'">'+text+'</a>');
		this.update();
		
		// bind events
		this._on(this.element, {
            'click a': function(event){
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
		item: '',
		src_on: 'icons/or/light_light.png',
		src_off: 'icons/ws/light_light.png',
		val_on: 255,
		val_off: 0
    },
	lock: false,
	_create: function(){
		// enhance
		var text = this.element.html();
		this.element.html('<p>'+text+'</p><a href="#"><img src="icons/ws/light_light.png"></a><input type="range" value="'+this.options.val_off+'" min="'+this.options.val_off+'" max="'+this.options.val_on+'" step="'+(this.options.val_on-this.options.val_off)/51+'" data-highlight="true"/>');
		this.element.enhanceWithin();
		this.update();
		
		// bind events
		this._on(this.element, {
			'change input': function(event){
				var item = this.options.item;
				if(!this.lock){
					knxcontrol.update_item(item,this.element.find('input').val());
				}
			},
            'click a.ui-link': function(event){
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
		item: '',
		val_on: 255,
		val_off: 0
    },
	_create: function(){
		// enhance
		var text = this.element.html();
		this.element.html('<p>'+text+'</p><a href="#" class="open"><img src="icons/ws/fts_shutter_10.png"></a><a href="#" class="close"><img src="icons/ws/fts_shutter_100.png"></a><input type="range" value="'+this.options.val_off+'" min="'+this.options.val_off+'" max="'+this.options.val_on+'" step="'+(this.options.val_on-this.options.val_off)/51+'" data-highlight="true"/>');
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
		this.element.html('<div class="time"><div><img class="bg" src="icons/clock/clockbg1.png"><img class="hoursLeft" src="icons/clock/0.png"/><img class="hoursRight" src="icons/clock/1.png"/><hr></div><div><img class="bg" src="icons/clock/clockbg1.png"><img class="minutesLeft" src="icons/clock/2.png"/><img class="minutesRight" src="icons/clock/3.png"/><hr></div></div><div class="date">1 januari 2015</div>');
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
		var weekday = (now.getDay()-1)%7;
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
		this.element.html('<img src="icons/weather/blank.png"><div><span data-role="displayvalue" data-item="'+this.options.item_temperature+'"></span>&deg;C</div><div><span data-role="displayvalue" data-item="'+this.options.item_windspeed+'"></span>m/s <span data-role="displayvalue" data-item="'+this.options.item_winddirection+'">m/s</span></div><div><span data-role="displayvalue" data-item="'+this.options.item_irradiation+'"></span>W/m<sup>2</sup></div>');
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
		this.element.html('<div class="alarm_list"></div><a class="add" data-role="button">'+language.capitalize(language.add_alarm)+'</a>');
		that = this;
		$.each(knxcontrol.alarm,function(index,alarm){
			that.update(alarm.id);
		});
		$.each(knxcontrol.action,function(index,action){
			that.update_action(action.id);
		});
		this.element.enhanceWithin();
		
		// bind events
		this._on(this.element, {
			'change': function(event){
				
				alarm_id = $(event.target).parents('.alarm').attr('data-id');
				data_field = $(event.target).attr('data-field');
				
				if(data_field=='time'){
					time = $(event.target).val().split(':');
					hour = time[0];
					minute = time[1];
					knxcontrol.update_alarm(alarm_id,'hour',hour);
					knxcontrol.update_alarm(alarm_id,'minute',minute);
				}
				else if(data_field=='action_id'){
					value = $(event.target).val();
					knxcontrol.update_alarm(alarm_id,data_field,value);
				}
				else{
					if($(event.target).prop('checked')){
						value = 1;
					}
					else{
						value = 0;
					}
					knxcontrol.update_alarm(alarm_id,data_field,value);
				}
			},
			'update': function(event,alarm_id){
				this.update(alarm_id);
			},
			'update_action': function(event,action_id){
				this.update_action(action_id);
			}
        });
	},
	update: function(alarm_id){
		// check if the alarm exists in knxcontrol
		if(knxcontrol.alarm[alarm_id]){
			// check if the alarm belongs in this section
			if(knxcontrol.alarm[alarm_id].section_id==this.options.section){
				// check if the alarm does not already exists in the DOM
				if(this.element.find('.alarm_list').find('.alarm [data-id="'+alarm_id+'"]').length==0){
					//set ids
					var newobject = template.alarm;
					
					newobject = newobject.replace(/_0/g, "_"+alarm_id);
					newobject = newobject.replace(/Select action/g, language.capitalize(language.select_action));

					//add the alarm to the DOM
					this.element.find('.alarm_list').append(newobject).enhanceWithin();
					this.element.find('.alarm[data-id="0"]').attr('data-id',alarm_id);
				}
				// update the alarm time
				var time = this.padtime(knxcontrol.alarm[alarm_id].hour) + ":" + this.padtime(knxcontrol.alarm[alarm_id].minute);
				this.element.find('.alarm[data-id="'+alarm_id+'"]').find('[data-field="time"]').val(time);

				// update alarm days
				this.element.find('.alarm[data-id="'+alarm_id+'"]').find('[data-field="mon"]').prop('checked', !!+knxcontrol.alarm[alarm_id].mon).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+alarm_id+'"]').find('[data-field="tue"]').prop('checked', !!+knxcontrol.alarm[alarm_id].tue).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+alarm_id+'"]').find('[data-field="wed"]').prop('checked', !!+knxcontrol.alarm[alarm_id].wed).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+alarm_id+'"]').find('[data-field="thu"]').prop('checked', !!+knxcontrol.alarm[alarm_id].thu).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+alarm_id+'"]').find('[data-field="fri"]').prop('checked', !!+knxcontrol.alarm[alarm_id].fri).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+alarm_id+'"]').find('[data-field="sat"]').prop('checked', !!+knxcontrol.alarm[alarm_id].sat).checkboxradio('refresh');
				this.element.find('.alarm[data-id="'+alarm_id+'"]').find('[data-field="sun"]').prop('checked', !!+knxcontrol.alarm[alarm_id].sun).checkboxradio('refresh');
				
			}
		}
		else{
			// remove the alarm from the DOM
			this.element.find('.alarm[data-id="'+alarm_id+'"]').remove();
		}
	},
	update_action: function(action_id){
		// check if the action belongs in this widget
		if(knxcontrol.action[action_id].section_id==0 || knxcontrol.action[action_id].section_id==this.options.section){
			// check if the action option exists
			if(this.element.find('option [data-id="'+action_id+'"]').length==0){	
				// add the action to the select list
				var newobject = template.action_select;
				newobject = newobject.replace(/0/g, action_id);
				this.element.find('div.alarm_action select').append(newobject).selectmenu('refresh');
			}
			// update the option
			this.element.find('option[data-id="'+action_id+'"]').html(knxcontrol.action[action_id].name);
			
			// check if it is the selected option
			that = this;
			$.each(this.element.find('.alarm'),function(index,object){
				alarm_id = $(object).attr('data-id');
				if(knxcontrol.alarm[alarm_id].action_id==action_id){
					that.element.find('.alarm[data-id="'+alarm_id+'"]').find('option[data-id="'+action_id+'"]').attr('selected', true).siblings('option').removeAttr('selected');
				}
			});
			
			
			this.element.find('select').selectmenu('refresh');
			// select action
			//this.element.find('div.alarm_action select').val(knxcontrol.alarm[alarm_id].action_id).selectmenu('refresh');
		}
	},
	padtime: function(num) {
		var s = num+"";
		while (s.length < 2) s = "0" + s;
		return s;
	}
});