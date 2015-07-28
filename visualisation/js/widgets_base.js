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


