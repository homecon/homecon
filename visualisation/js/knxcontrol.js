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
		
	// get a weather forecast and schedule it to run every hour
	//knxcontrol.get_weatherforecast()
	//setInterval(function(){knxcontrol.get_weatherforecast()}, 3600000);
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
		// 1: {id: 1, section_id: 2, hour: 13, minute: 12, mon: 1, tue: 1, wed: 1, thu: 1, fri: 1, sat: 1, sun: 1, action_id: 2},...
	},
	action:{
		// 1: {id: 1, name: 'Licht aan', section_id: 0, actions: [{id: 1, delay: 0, item: 'living.lights.licht', value: 0},{...},...]},...
	},
	measurement:{
		// 1: {id: 1, name: 'Temperatuur', item: 'buiten.measurements.temperature', quantity: 'Temperature', unit: 'degC', description: 'Buiten temeratuur'}, 
	},
// initialize
	init: function(){
		knxcontrol.get_items();
		knxcontrol.get_alarms();
		knxcontrol.measurement.get();
		
		// request the values of all items from smarthome.py
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
	update_item: function(item,value){
		// set the item value
		knxcontrol.item[item] = value;
		// write the new value of the item to smarthome.py

		// trigger a widget update event
		$('[data-item="'+item+'"]').trigger('update');
	},
// get an or all alarms from mysql	
	get_alarms: function(alarm_id){
		var where = 'id>0';
		if(alarm_id){
			where = 'id='+alarm_id;
		}
		$.post('requests/select_from_table.php',{table: 'alarms', column: '*', where: where},function(result){
			var alarms = JSON.parse(result);
			$.each(alarms,function(index,alarm){
				knxcontrol.alarm[alarm.id] = {
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
			//??? here ???
			knxcontrol.get_actions();
		});
	},
	update_alarm: function(alarm_id,data_field,value){
		// set the alarm in the database
		$.post('requests/update_table.php',{table: 'alarms', column: data_field, value: value, where: 'id='+alarm_id},function(result){
			// on success update knxcontrol
			knxcontrol.alarm[alarm_id][data_field] = value;
		});
	},
	add_alarm: function(section_id){
		$.post('requests/insert_into_table.php',{table: 'alarms', column: ['hour','minute','sectionid','mon','tue','wed','thu','fri','sat','sun','action_id'].join(), value: [12,0,section_id,1,1,1,1,1,0,0,0].join()},function(result){
			alarm_id = JSON.parse(result);
			alarm_id = alarm_id[0];
			
			// add the alarm to knxcontrol
			knxcontrol.get_alarms(alarm_id);
		});
	},
	delete_alarm: function(alarm_id){
		$.post('requests/delete_from_table.php',{table: 'alarms', where: 'id='+alarm_id},function(result){
			delete knxcontrol.alarm[alarm_id];
			$('[data-role="alarm"]').trigger('update',alarm_id);
		});
	},
// get alarm actions data	
	get_actions: function(action_id){
		var where = 'id>0';
		if(action_id){
			where = 'id='+action_id;
		}
		$.post('requests/select_from_table.php',{table: 'alarm_actions', column: '*', where: where},function(result){
			var actions = JSON.parse(result);
			$.each(actions,function(index,action){
				knxcontrol.action[action.id] = {
					id: action.id,
					section_id: action.sectionid,
					name: action.name,
					actions: [
						{id:1, delay: action.delay1, item: action.item1, value: action.value1},
						{id:2, delay: action.delay2, item: action.item2, value: action.value2},
						{id:3, delay: action.delay3, item: action.item3, value: action.value3},
						{id:4, delay: action.delay4, item: action.item4, value: action.value4},
						{id:5, delay: action.delay5, item: action.item5, value: action.value5},
					]
				};
				$('[data-role="alarm"]').trigger('update_action',action.id);
				$('[data-role="action_list"]').trigger('update',action.id);
			});
			
		});
	},
	update_action: function(action_id,data_field,value){
		// set the alarm in the database
		$.post('requests/update_table.php',{table: 'alarm_actions', column: data_field, value: value, where: 'id='+action_id},function(result){
			// on success update knxcontrol
			knxcontrol.get_actions(action_id);
		});
	},
	add_action: function(){
		$.post('requests/insert_into_table.php',{table: 'alarm_actions', column: ['name','sectionid','delay1'].join(), value: ['Name',0,0].join()},function(result){
			action_id = JSON.parse(result);
			action_id = action_id[0];
			// add the alarm to knxcontrol
			knxcontrol.get_actions(action_id);
		});
	},
	delete_action: function(action_id){
		$.post('requests/delete_from_table.php',{table: 'alarm_actions', where: 'id='+action_id},function(result){
			delete knxcontrol.action[action_id];
			$('[data-role="action_list"]').trigger('update',action_id);
		});
	},
	measurement: {
		// 1: {id: 1, name: 'Temperatuur', item: 'buiten.measurements.temperature', quantity: 'Temperature', unit: 'degC', description: 'Buiten temeratuur', data: []},
		get: function(id){
			var where = 'id>0';
			if(id){
				where = 'id='+id;
			}
			that = this;
			$.post('requests/select_from_table.php',{table: 'measurements_legend', column: '*', where: where},function(result){
				var results = JSON.parse(result);
				$.each(results,function(index,result){
					that[result.id] = {
						id: result.id,
						name: result.name,
						item: result.item,
						quantity: result.quantity,
						unit: result.unit,
						description: result.description,
						data: []
					};
					$('[data-role="measurement_list"]').trigger('update',result.id);
					//that.get_data(result.id);
				});
				$('[data-role="chart"]').trigger('get_data');
			});
		},
		update: function(id,field,value){
			that = this;
			$.post('requests/update_table.php',{table: 'measurements_legend', column: field, value: value, where: 'id='+id},function(result){
				that.get(id);
			});
		},
		get_data: function(id){
			that = this;
			$.post('requests/select_from_table.php',{table: 'measurements_quarterhouraverage', column: 'time,value', where: 'signal_id='+id+' AND time > '+((new Date()).getTime()/1000-7*27*3600), orderby: 'time'},function(result){
				that[id].data = [];
				
				$.each(JSON.parse(result),function(index,value){
					that[id].data.push([parseFloat(value.time)*1000,parseFloat(value.value)]);
				});
				$('[data-role="chart"]').trigger('update',id);
				
			});
		}
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