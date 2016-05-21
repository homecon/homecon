/*
    Copyright 2015 Brecht Baeten
    This file is part of HomeCon.

	smarhome.js is part of HomeCon based on smartVISU - io_smarthome.py.js by Martin Gleiﬂ

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
    write: function(item, value){
		smarthome.send({'cmd': 'item', 'id': item, 'val': value, 'token': smarthome.token});
		homecon.item.update(item, value);
    },
// Ask for item values over the websocket                                    //
    monitor: function(items){
		if(typeof items == 'undefined'){
			smarthome.send({'cmd': 'monitor', 'items': homecon.getkeys('item'), 'token': smarthome.token});
			smarthome.send({'cmd': 'log', 'name': 'env.core.log', 'max': 100, 'token': smarthome.token});
		}
		else{
			smarthome.send({'cmd': 'monitor', 'items': items, 'token': smarthome.token});
		}
    },
// private functions	
// Opens the connection and add some handlers                                //
    open: function(){
        smarthome.socket = new WebSocket('ws://' + smarthome.address + ':' + smarthome.port + '/');

        smarthome.socket.onopen = function(){
            smarthome.send({'cmd': 'proto', 'ver': smarthome.version, 'token': smarthome.token});
            console.log('connected to smarthome.py');

			$(document).trigger('connected');
         };
		
        smarthome.socket.onmessage = function(event){
			//console.log(event.data);
			
            var data = JSON.parse(event.data);
            switch(data.cmd){
                case 'item':
					for(var i = 0; i < data.items.length; i++){
                        var item = data.items[i][0];
                        var value = data.items[i][1];
                        if ( data.items[i].length > 2 ){
                            // not supported: data.p[i][2] options for visu
                        };

                        // convert binary values
                        if (value === false) value = 0;
                        if (value === true) value = 1;

						// update widgets
                        homecon.item.update(item, value);

                    };
                    break;
				case 'log':
					homecon.smarthome_log.update(data.log);
					break;
                case 'series':                   
                    data.sid = data.sid.substr(0, data.sid.length - 3) + '0';
                    widget.update(data.sid.replace(/\|/g, '\.'), data.series);
					console.log(data);
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

// Close the connection                                                      //
    close: function() {
        console.log("[smarthome.py] close connection");
                
        if (smarthome.socket.readyState > 0){
			smarthome.socket.close();         
			smarthome.socket = null;
		}
    }
	
};
