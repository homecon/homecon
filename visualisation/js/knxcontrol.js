

/*****************************************************************************/
/*                     Main event handlers                                   */
/*****************************************************************************/
// initialize
$(document).on('connect',function(event,user_id){
	knxcontrol.user_id = user_id;
	
	if(!smarthome.socket){
		//get connection data
		$.post('requests/select_from_table.php',{table: 'data', column: '*', where: 'id=1'},function(result){
			data = JSON.parse(result);
			data = data[0];
			
			// initialize connection
			smarthome.init(data['ip'],data['port'],data['token']);
			

		});
	};
});


			

/*****************************************************************************/
/*                     KNXControl                                            */
/*****************************************************************************/

var knxcontrol = {
	user_id: 0,
	item: new Object(),

// initialize
	init: function(){
		knxcontrol.get_items();
		
		// request the values from smarthome.py
		smarthome.monitor();
	},
// gets items from all widgets in the dom
	get_items: function(){
		$('[data-item]').each(function(index){
			var item = $(this).attr('data-item');
			knxcontrol.item[item] = 0;
		});
	},	
// update an item with a certain value
	update: function(item,value){
		// set the item value
		knxcontrol.item[item] = value;
		
		console.log(item+' set to '+value);
		// write the new value of the item to smarthome.py
		smarthome.write(item, knxcontrol.item[item]);

		// trigger a widget update event
		$('[data-item="'+item+'"]').trigger('update');
	}
	
}

/*****************************************************************************/
/*                     Widget definitions                                    */
/*****************************************************************************/

///////////////////////////////////////////////////////////////////////////////
// displayvalue                                                               //
$.widget('knxcontrol.displayvalue',{
	options: {
      item: '',
	  digits: 'icons/or/light_light.png'
    },
	_create: function(){
		// enhance
		
		// bind events
		this._on(this.element, {
			'update': function(event){	
				var item = this.options.item;
				
				this.element.html(knxcontrol.item[item]);
			}
		});
	}
});

///////////////////////////////////////////////////////////////////////////////
// lightswitch                                                               //
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

///////////////////////////////////////////////////////////////////////////////
// light dimmer                                                              //
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
				console.log(this.options.item+' locked');
				var that = this;
				setTimeout(function(){
					that.lock = false;
					console.log(that.options.item+' unlocked');
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

///////////////////////////////////////////////////////////////////////////////
// shading                                                                   //
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
				console.log(this.options.item+' locked');
				var that = this;
				setTimeout(function(){
					that.lock = false;
					console.log(that.options.item+' unlocked');
				},500);
				
				
				var item = this.options.item;

				this.element.find('input').val(knxcontrol.item[item]).slider('refresh');
			}
        });
	}
});