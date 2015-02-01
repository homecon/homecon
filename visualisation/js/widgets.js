//
// 
// widget.js is part of KNXControl
// @author: Brecht Baeten
// @license: GNU GENERAL PUBLIC LICENSE
// 
//

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

		// bind events
		this._on(this.element, {
			'update': function(event){	
				var item = this.options.item;
				var rounding = Math.pow(10,this.options.digits);
				
				var value = Math.round(knxcontrol.item[item]*rounding)/rounding;
				
				this.element.html(value);
			}
		});
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
		
		// bind events
		this._on(this.element, {
            'click a': function(event){
				var item = this.options.item;
				// update the value in knxcontrol
				knxcontrol.update(item,(knxcontrol.item[item]+1)%2);
			},
			'update': function(event){	
				var item = this.options.item;
				
				if(knxcontrol.item[item]){
					this.element.find('img').attr('src',this.options.src_on);
				}
				else{
					this.element.find('img').attr('src',this.options.src_off);
				}
			}
        });
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
		
		// bind events
		this._on(this.element, {
			'change input': function(event){
				console.log('change');
				var item = this.options.item;
				if(!this.lock){
					knxcontrol.update(item,this.element.find('input').val());
				}
			},
            'click a.ui-link': function(event){
				var item = this.options.item;
				// update the value in knxcontrol
				if( knxcontrol.item[item] > this.options.val_off){
					knxcontrol.update(item,this.options.val_off);
				}
				else{
					knxcontrol.update(item,this.options.val_on);
				}
			},
			'update': function(event){
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
		
		// bind events
		this._on(this.element, {
			'change input': function(event){
				var item = this.options.item;
				if(!this.lock){	
					knxcontrol.update(item,this.element.find('input').val());
				}
			},
            'click a.open': function(event){
				var item = this.options.item;
				knxcontrol.update(item,this.options.val_off);
			},
			'click a.close': function(event){
				var item = this.options.item;
				knxcontrol.update(item,this.options.val_on);
			},
			'update': function(event){
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
		var text = this.element.html();
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
		var weekday = now.getDay();
		var day = now.getDate();
		var month = now.getMonth();
		var year = now.getFullYear();
		
		var date_string = language.weekday[weekday]+' '+day+' '+language.month[month]+' '+year;
	
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
    },
	_create: function(){
		// enhance
		var text = this.element.html();
		this.element.html('<img src="icons/weather/blank.png"><div class="value"></div>');
		this.element.enhanceWithin();
		
		// bind events
	},
	icons: {'01d': 'sun_1.png','02d': 'sun_3.png','03d': 'cloud_4.png','04d': 'cloud_5.png','09d': 'cloud_7.png','10d': 'sun_7.png' ,'11d': 'cloud_10.png','13d': 'cloud_13.png','50d': 'sun_6.png','01n': 'moon_1.png','02n': 'moon_3.png','03n': 'cloud_4.png','04n': 'cloud_5.png','09n': 'cloud_7.png','10n': 'moon_7.png','11n': 'cloud_10.png','13n': 'cloud_13.png','50n': 'moon_6.png'}
});