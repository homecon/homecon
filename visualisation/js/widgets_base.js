/*
    Copyright 2015 Brecht Baeten
    This file is part of HomeCon.

    HomeCon is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    HomeCon is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
*/


/******************************************************************************/
/*                     separation line                                        */
/******************************************************************************/
$.widget('homecon.line',{
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

/******************************************************************************/
/*                     display value                                          */
/******************************************************************************/
$.widget('homecon.displayvalue',{
	options: {
      item: '',
	  pre: '',
	  app: '',
	  digits: 1,
	  scale: 1
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
		
		var value = Math.round(knxcontrol.item[item]*this.options.scale*rounding)/rounding;
		
		this.element.html(this.options.pre + value + this.options.app);
	}
});

/******************************************************************************/
/*                     input value                                            */
/******************************************************************************/
$.widget("homecon.inputvalue",{
	options: {
		item: ''
    },
	lock: false,
	_create: function(){
		// enhance
		this.element.prepend('<input type="text"/>');
		this.element.enhanceWithin();
		this.update();

		// bind events
		this._on(this.element, {
			'change input': function(event){
				var item = this.options.item;
				smarthome.write(item, this.element.find('input').val());
				
			},
			'update': function(event){
				this.update();
			}
        });
	},
	update: function(){	
		var item = this.options.item;
		this.element.find('input').val(knxcontrol.item[item]);
	}
});

/******************************************************************************/
/*                     value switch                                           */
/******************************************************************************/
$.widget('homecon.valueswitch',{
	options: {
		label: '',
		item: '',
		value: 1,
		src: '',
    },
	
	_create: function(){
		// enhance
		this.element.prepend('<a href="#" class="switch"><img src="'+this.options.src+'">'+this.options.label+'</a>');
		this.element.enhanceWithin();
	
		// bind events
		this._on(this.element, {
            'click a.switch': function(event){
				// update the value in smarthome
				smarthome.write(this.options.item, this.options.value);
			},
        });
	}
});

/******************************************************************************/
/*                     pushbutton                                             */
/******************************************************************************/
$.widget('homecon.pushbutton',{
	options: {
		label: '',
		item: '',
		value: 1,
		src: '',
    },
	
	_create: function(){
		// enhance
		this.element.prepend('<a  class="switch" data-role="button" data-corners="false">'+this.options.label+'</a>');
		if(this.options.src!=''){
			this.element.append('<img src="'+this.options.src+'"/>');
		}
		this.element.enhanceWithin();
	
		// bind events
		this._on(this.element, {
            'click a.switch': function(event){
				// update the value in smarthome
				smarthome.write(this.options.item, this.options.value);
			},
        });
	}
});

/******************************************************************************/
/*                     toggle switch                                          */
/******************************************************************************/
$.widget('homecon.toggleswitch',{
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
		this.element.prepend('<a href="#" class="switch"><img src="'+this.options.src_off+'">'+this.options.label+'</a>');
		this.update();
		
		// bind events
		this._on(this.element, {
            'click a.switch': function(event){
				// update the value in smarthome
				if(knxcontrol.item[this.options.item] > this.options.val_off){
					smarthome.write(this.options.item, this.options.val_off);
				}
				else{
					smarthome.write(this.options.item, this.options.val_on);
				}
			},
			'update': function(event){
				this.update();
			}
        });
	},
	update: function(){
		if(knxcontrol.item[this.options.item]>this.options.val_off){
			this.element.find('img').attr('src',this.options.src_on);
		}
		else{
			this.element.find('img').attr('src',this.options.src_off);
		}
	}

});

/******************************************************************************/
/*                     checkbox                                               */
/******************************************************************************/
$.widget('homecon.checkbox',{
	options: {
		label: '',
		item: '',
    },
	
	_create: function(){
		// enhance
		this.element.prepend('<label>'+this.options.label+'<input type="checkbox" data-mini="true"/></label>');
		this.element.enhanceWithin();
		this.update();

		// bind events
		this._on(this.element, {
            'change input': function(event){
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
			this.element.find('input').prop('checked', true).checkboxradio('refresh');
		}
		else{
			this.element.find('input').prop('checked', false).checkboxradio('refresh');
		}
	}

});

/******************************************************************************/
/*                     input slider                                           */
/******************************************************************************/
$.widget("homecon.inputslider",{
	options: {
		label: '', 
		item: '',
		val_on: 1,
		val_off: 0
    },
	lock: false,
	_create: function(){
		// enhance
		this.element.prepend('<input type="range" value="'+this.options.val_off+'" min="'+this.options.val_off+'" max="'+this.options.val_on+'" step="1" data-highlight="true"/>');
		this.element.enhanceWithin();
		this.update();

		// bind events
		elem = this.element
		this._on(this.element, {
			'slidestop input': function(event){
				var item = this.options.item;
				smarthome.write(item, this.element.find('input').val());
			},
			'update': function(event){
				this.update();
			}
        });
	},
	update: function(){
		this.element.find('input').val(knxcontrol.item[this.options.item]).slider('refresh');
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
/*                     chart                                                 */
/*****************************************************************************/
$.widget('homecon.chart',{
	options: {
	},
	_create: function(){

		// set global options
		Highcharts.setOptions({
			global: {
				useUTC: false
			}
		});

		// fix width bug
		this.chart_options.chart['width'] = 0.9*this.element.parents('div.ui-content').width()/100*Math.max(document.documentElement.clientWidth, window.innerWidth || 0)

		// Enhance
		this.element.append('<div class="chart_container"></div>');
		this.create_chart()
		this.chart = $(this.element).children('.chart_container').highcharts();
		this.chart.reflow();

		// bind events
		this._on(this.element, {
			'update': function(event,series){			
				this.update(series);
			},
			'get_series': function(event,id){
				this.get_series(id)
			},
			'get_data': function(event){			
				this.get_data()
			}
		});

	},
	create_chart: function(){
		$(this.element).children('.chart_container').highcharts(this.chart_options);
	},
	update: function(series){
		var add = true;
		$.each(this.chart.series,function(index,ser){
			if(ser.name == series.name){
				// update the data
				ser.setData(series.data);
				add = false;
			}
		});
		if(add){
			this.chart.addSeries(series);
		}
		this.chart.yAxis[0].setTitle({text: series.unit})
		this.chart.reflow();
	},
	get_series: function(id){
	},
	get_data: function(){
	},
	chart_options: {
		chart: {
			type: 'line'
		},
		title: {
			text: ''
		},
		xAxis: {
			type: 'datetime',
			ordinal: false
		},
		tooltip: {
			xDateFormat: '%Y-%m-%d %H:%M',
			valueDecimals: 1,
			shared: true
		},
		rangeSelector: {
			enabled: false
		},
		plotOptions: {
			line: {
				marker: {
					enabled: false
				}
			}
		},
		series: []
	}
});

