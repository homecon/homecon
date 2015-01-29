//
// 
// model.js is part of KNXControl
// @author: Brecht Baeten
// @license: GNU GENERAL PUBLIC LICENSE
// 
//



/*****************************************************************************/
/*                     Smarthome                                             */
/*****************************************************************************/
//  This part is created based on the smartVISU io_smarthome.py.js file by Martin Gleiﬂ
var smarthome = {
// Connection variables                                                      //
    adress:     '',
    port:       '',
	token:      '',
	
// write an item to smarthome.py                                             //
    write: function(item, val){
                smarthome.send({'cmd': 'item', 'id': item, 'val': val, 'token': smarthome.token});
                widget.update(item, val);
    },
// initialization                                                            //   
	init: function(address, port, token) {
		smarthome.address = address;
		smarthome.port = port;
		smarthome.token = token;
		smarthome.open();
	},
// continuosly run the driver                                                //
    run: function(realtime){
        // old items
        widget.refresh();
                
        // new items
        smarthome.monitor();   
    },
	version: 2,
	socket: false,
	
// Opens the connection and add some handlers                                //
    open: function(){
        smarthome.socket = new WebSocket('ws://' + smarthome.address + ':' + smarthome.port + '/');

        smarthome.socket.onopen = function(){
            smarthome.send({'cmd': 'proto', 'ver': smarthome.version});
            smarthome.monitor();
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
                    break;

                case 'dialog':
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
    monitor: function() {
		if( widget.listening() ){
			smarthome.send({'cmd': 'monitor', 'items': widget.listeners()});
				
			// series: avg, min, max, sum, diff, rate
			widget.plot().each(function(idx){
				var items = widget.explode($(this).attr('data-item')); 
				
				$.each(items,function(index,item){
				//for(var i = 0; i < items.length; i++){ 
			
					if (widget.is_series(item) && !widget.get(item)) {
						var pt = item.split('.');
						var split_item = item.substr(0, item.length - 3 - pt[pt.length - 3].length - pt[pt.length - 2].length - pt[pt.length - 1].length);
						smarthome.send({'cmd': 'series', 'item': split_item, 'series' : pt[pt.length - 3], 'start': pt[pt.length - 2]});
					};
				});
			});
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