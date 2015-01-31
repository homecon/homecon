//
// 
// smarhome.js is part of KNXControl
// based on smartVISU - io_smarthome.py.js by Martin Gleiﬂ
// @author: Brecht Baeten
// @license: GNU GENERAL PUBLIC LICENSE
// 
//


/*****************************************************************************/
/*                     Smarthome                                             */
/*****************************************************************************/
var smarthome = {
// Connection variables                                                      //
    adress:     '',
    port:       '',
	token:      '',
	version: 3,
	socket: false,
	
// public functions	
// initialization                                                            //   
	init: function(address, port, token) {
		smarthome.address = address;
		smarthome.port = port;
		smarthome.token = token;
		smarthome.open();
	},
// write an item to smarthome.py                                             //
    write: function(item, val){
		smarthome.send({'cmd': 'item', 'id': item, 'val': val, 'token': smarthome.token});
		//widget.update(item, val);
    },
	
// private functions	
// Opens the connection and add some handlers                                //
    open: function(){
        smarthome.socket = new WebSocket('ws://' + smarthome.address + ':' + smarthome.port + '/');

        smarthome.socket.onopen = function(){
            smarthome.send({'cmd': 'proto', 'ver': smarthome.version});
            console.log('connected to smarthome.py');
			//smarthome.monitor();
         };
		
        smarthome.socket.onmessage = function(event){
            var data = JSON.parse(event.data);
                       
            switch(data.cmd){
                case 'item':
					for(var i = 0; i < data.items.length; i++){
                        var item = data.items[i][0];
                        var val = data.items[i][1];
                        if ( data.items[i].length > 2 ){
                            // not supported: data.p[i][2] options for visu
                        };

                        // convert binary values
                        if (val === false) val = 0;
                        if (val === true) val = 1;

						// update widgets
                        widget.update(item, val);
                    };
                    break;

                case 'series':                   
                    data.sid = data.sid.substr(0, data.sid.length - 3) + '0';
                    widget.update(data.sid.replace(/\|/g, '\.'), data.series);
					console.log(data)
                    break;

                case 'dialog':
					console.log(data);
                    break;

                case 'proto':
                    var proto = parseInt(data.ver);
                    if (proto != smarthome.version){
                        console.log('Driver: smarthome.py', 'Protocol mismatch<br \>driver is: v' + smarthome.version + '<br />smarthome.py is: v' + proto);
                    };
                    break;
            };
        };

        smarthome.socket.onerror = function(error){
            console.log('Driver: smarthome.py', 'Could not connect to smarthome.py server!<br \> Websocket error ' + error.data + '.');
        };

        smarthome.socket.onclose = function(){
			console.log('Driver: smarthome.py', 'Connection closed to smarthome.py server!');
        };
		
    },
// Send data over the websocket                                              //
    send: function(data){ 
        if (smarthome.socket.readyState == 1){
            smarthome.socket.send(unescape(encodeURIComponent(JSON.stringify(data))));
        };
    },

// Monitors items                                                            //
    monitor: function(){
		if( widget.listening() ){
			smarthome.send({'cmd': 'monitor', 'items': widget.listeners()});
        };
    },

// Close the connection                                                      //
    close: function() {
        console.log("[smarthome.py] close connection");
                
        if (smarthome.socket.readyState > 0){
			smarthome.socket.close();         
			smarthome.socket = null;
		}
    }
	
};


/*
var widget = {
// a list with all item and values
    buffer: new Object(),
	
	
// Static function for exploding the a text with comma-seperated values into unique lists
	explode: function(text) {
		var ret = Array();
		var unique = Array();

		// More than one item?
		if (text.indexOf(',') >= 0) {
			var parts = text.explode();

			for(var i=0; i<parts.length; i++){
				if (parts[i] != ''){
					unique[parts[i]] = '';
				}
			}
		} 
		// One item
		else if (text != '') {
			unique[text] = '';
		};
		for(var part in unique){  
			ret.push(part);
		}
		return ret;   
    },

// Checks if there are any listeners 
    listening: function() {
		var ret = false;
		if ($('[data-item]').size() > 0){
			ret = true;
		}
        return ret;        
    },


// Returns all items listening on. This is used to get an unique list of the items independent on the number of widgets.
	listeners: function() {
		var ret = Array();
		var unique = Array();

		$('[data-item]').each(function(index){
			var items = widget.explode($(this).attr('data-item')); 
			for (var i = 0; i < items.length; i++){
				unique[items[i]] = '';
			}
		}); 

		for (var item in unique){    
			ret.push(item);
		}
        return ret;       
    },

// List all items and the number of listeners in console.log.         
	list: function(){
		var widgets = 0;
		$('[data-item]').each(function(idx) {
			if ($(this).attr('data-item').trim() != ''){
				console.log("[widget] '" + this.id + "' listen on '" + $(this).attr('data-item') + "'");
				widgets++;
			}
		});
        console.log("[widget] --> " + widgets + " listening.");
    },
    

// Checks if the value/s are valid (not undefined and not null) 
    check: function(values) {
		if (values instanceof Array) {
			for (var i = 0; i < values.length; i++){
				if (values[i] === undefined || values[i] == null){
					return false;
				}
			}
		} 
		else{
			if (values === undefined || values == null){
				return false;
			}
		}
		
		return true;
	},

// Get one or more value/s for an item/s from the buffer.    
    get: function(items) {
        if (items instanceof Array){
			var ret = Array();

			for (var i = 0; i < items.length; i++) { 
				ret.push(widget.buffer[items[i]]);
			}
		}
		else{
			var ret = widget.buffer[items]; 
        }        
		return ret;
	},

// Set a value of an item in the buffer.
	set: function(item, value) {
		if (widget.buffer[item] instanceof Array){
            // don't add it to the buffer, because highchart will do it for us.   
			//var series = widget.buffer[item];
			//series.push(value);
                
		}
		else if (value !== undefined){
			widget.buffer[item] = value; 
		}
		// DEBUG: console.log("[widget] '" + item, widget.buffer[item]);
	},

// Update an item and all widgets listening on that. The value is been written to the buffer and the widgets are called if all values are set.
    update: function(item, value) {
                
		// update if value has changed
        if( value === undefined || widget.buffer[item] !== value || (widget.buffer[item] instanceof Array && widget.buffer[item].toString() != value.toString()) ){
			widget.set(item, value);
                        
			$('[data-item*="' + item + '"]').each(function(index) {
				var items = widget.explode($(this).attr('data-item')); 

				// only the item witch is been updated
				for (var i = 0; i < items.length; i++) { 
					if (items[i] == item) {
						var values = Array();
                                
						// update to a plot: only add a point
						if ($(this).attr('data-widget').substr(0,5) == 'plot.' && $('#' + this.id).highcharts()) {

							// if more than one item, only that with the value
                            if (items instanceof Array) {
								for (var j = 0; j < items.length; j++) {
                                    values.push (items[j] == item ? value : null );
								}
							}
							if (value !== undefined || value != null){
								$(this).trigger('point', [values]);
							}
						} 
						// regular update to the widget with all items   
						else {
							values = widget.get(items);
							if(widget.check(values)){
								$(this).trigger('update', [values]);
							}
					    }
					}
				}
			});
		}
	},

// Prepares some widgets on the current page.  Bind to jquery mobile 'pagebeforeshow'.
	prepare: function() {
        // all plots on the current page.
		$('[id^="' + $.mobile.activePage.attr('id') + '-"][data-widget^="plot."][data-item]').each(function(idx) {
            
			if ($('#' + this.id).highcharts()){
				$('#' + this.id).highcharts().destroy();
			}
        });   
    },
    
// Refreshes all widgets on the current page. Used to put the values to the widgets if a new page has been opened. Bind to jquery mobile 'pageshow'.
	refresh: function() {             
		$('[id^="' + $.mobile.activePage.attr('id') + '-"][data-item]').each(function(idx) {
            
			var values = widget.get(widget.explode($(this).attr('data-item'))); 

			if (widget.check(values)){
				$(this).trigger('update', [values]);
			}
		})
	},
};
*/