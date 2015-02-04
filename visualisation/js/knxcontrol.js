//
// 
// widget.js is part of KNXControl
// @author: Brecht Baeten
// @license: GNU GENERAL PUBLIC LICENSE
// 
//

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
			
			// set location
			knxcontrol.location.latitude = data['latitude'];
			knxcontrol.location.longitude = data['longitude'];
		});
	};
	
	// get the alarms 
	//knxcontrol.get_alarms();
		
	// get a weather forecast and schedule it to run every hour
	knxcontrol.get_weatherforecast()
	setInterval(function(){knxcontrol.get_weatherforecast()}, 3600000);
});


			

/*****************************************************************************/
/*                     KNXControl model                                      */
/*****************************************************************************/

var knxcontrol = {
	user_id: 0,
	location:	{
		latitude: 51,
		longitude: -5,
		altitude: 80
	},
	weatherforecast: [], // will be removed
	item: {
		// living.lights.light: 0
	},
	alarm: {
		// 2: [1: {id: 1, section_id: 2, hour: 13, minute: 12, mon: 1, tue: 1, wed: 1, thu: 1, fri: 1, sat: 1, sun: 1, action_id: 2},...]
	},
	
// initialize
	init: function(){
		knxcontrol.get_items();
		knxcontrol.get_alarms();
		
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
		
		// write the new value of the item to smarthome.py
		smarthome.write(item, knxcontrol.item[item]);

		// trigger a widget update event
		$('[data-item="'+item+'"]').trigger('update');
	},
// update alarm data	
	get_alarms: function(){
		$.post('requests/select_from_table.php',{table: 'alarms', column: '*', where: 'id>0'},function(result){
			var alarms = JSON.parse(result);
			$.each(alarms,function(index,alarm){
				if(!(alarm.sectionid in knxcontrol.alarm)){
					// define an object if it doesn't exist yet
					knxcontrol.alarm[alarm.sectionid] = {};
				}
				knxcontrol.alarm[alarm.sectionid][alarm.id] = {
					id: alarm.id,
					section_id: alarm.sectionid,
					hour: alarm.hour,
					minute: alarm.minute,
					mon: alarm.mon,
					tue: alarm.tue,
					wed: alarm.wed,
					thu: alarm.thu,
					fri: alarm.fri,
					sat: alarm.sat,
					sun: alarm.sun,
					action_id: alarm.action_id
				};
				$('[data-role="alarm"][data-section="'+alarm.sectionid+'"]').trigger('update',alarm.id);
			});
		});
	},
	
////////////////////////////////////////////////////////////////////////
// this will be moved to smarthome.py in the near future so no dev is happening and widget is broken	
// update weather forecast data
	get_weatherforecast: function(){
		
		$.post('http://api.openweathermap.org/data/2.5/forecast?lat='+this.location.latitude+'&lon='+this.location.longitude,function(result){
			var weatherforecast = [];

			for(var i=0;i<result.list.length; i++){
				data = result.list[i];
				var temp = {
					timestamp: data.dt*1000,
					temperature: data.main.temp-273.15,
					minimum_temperature: data.main.temp_min-273.15,
					maximum_temperature: data.main.temp_max-273.15,
					pressure: data.main.pressure,
					humidity: data.main.humidity,
					windspeed: data.wind.speed,
					winddirection: data.wind.deg,
					cloudfactor: 1-data.clouds.all/100,
					precipitation: 0,
					icon: data.weather[0].icon
				};
				
				if(data.hasOwnProperty('rain')){
					temp.precipitation= data.rain['3h']/3;
				}
				weatherforecast.push(temp);
			}
			knxcontrol.weatherforecast = weatherforecast;
			
			// trigger a widget update event
			$(document).trigger('weatherforecastupdate');
		});
	},
///////////////////////////////////////////////////////////////////////////:	
}