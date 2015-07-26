/*
    Copyright 2015 Brecht Baeten
    This file is part of KNXControl.

    KNXControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    KNXControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
*/

/*****************************************************************************/
/*                     Main event handlers                                   */
/*****************************************************************************/
// initialize
$(document).on('authenticated',function(event,user_id){

	// gather values for knxcontrol and make connection to smarthome.py
	knxcontrol.user_id = user_id;
	
	knxcontrol.settings.get();
	knxcontrol.location.get();
	knxcontrol.alarm.get();
	knxcontrol.measurement.get();
	knxcontrol.user.get();
	knxcontrol.profile.get();
});
$(document).on('connect',function(event){
	// initialize connection to smarthome.py
	if((document.URL).indexOf(knxcontrol.settings.ip) > -1){
		// the address is local if the smarthome.py ip is the same as the website ip
		smarthome.init(knxcontrol.settings.ip,knxcontrol.settings.port,knxcontrol.settings.token);
	}
	else{
		// we are on the www
		smarthome.init(knxcontrol.settings.web_ip,knxcontrol.settings.web_port,knxcontrol.settings.token);
	}
});
/*****************************************************************************/
/*                     KNXControl model                                      */
/*****************************************************************************/
var knxcontrol = {
	user_id: 0,
	location:	{
		latitude: 0,
		longitude: 0,
		altitude: 80,
		get: function(){
			$.post('requests/select_from_table.php',{table: 'data', column: 'latitude,longitude', where: 'id=1'},function(result){
				data = JSON.parse(result);
				data = data[0];
				
				knxcontrol.location.latitude = data['latitude'];
				knxcontrol.location.longitude = data['longitude'];
			});
		},
		update: function(){
			$.post('requests/update_table.php',{table: 'data', column: ['latitude','longitude'].join(';'), value: [this.latitude,this.longitude].join(';'), where: 'id=1'},function(result){
				$("#message_popup").html('<h3>'+language.settings_saved+'</h3>');
				$("#message_popup").popup('open');
				setTimeout(function(){$("#message_popup").popup('close');}, 500);
			});
		}
	},
	settings:{
		ip: '',
		port: '',
		web_ip: '',
		web_port: '',
		token: '',
		get: function(){
			$.post('requests/select_from_table.php',{table: 'data', column: '*', where: 'id=1'},function(result){

				data = JSON.parse(result);
				data = data[0];
				
				knxcontrol.settings.ip = data['ip'];
				knxcontrol.settings.port = data['port'];
				knxcontrol.settings.web_ip = data['web_ip'];
				knxcontrol.settings.web_port = data['web_port'];
				knxcontrol.settings.token = data['token'];
				
				$(document).trigger('connect');
				$('[data-role="settings"]').trigger('update');
			});
		},
		update: function(){
			$.post('requests/update_table.php',{table: 'data', column: ['ip','port','web_ip','web_port','token'].join(';'), value: [this.ip,this.port,this.web_ip,this.web_port,this.token].join(';'), where: 'id=1'},function(result){
				$("#message_popup").html('<h3>'+language.settings_saved+'</h3>');
				$("#message_popup").popup('open');
				setTimeout(function(){$("#message_popup").popup('close');}, 500);
			});
		}
	},
//items                                                                      //
	item: {
		// living.lights.light: 0
		get: function(){
			$('[data-item]').each(function(index){
				var item = $(this).attr('data-item');
				knxcontrol.item[item] = 0;
			});
			knxcontrol.item['knxcontrol.mpc.model.identification'] = 0;
			knxcontrol.item['knxcontrol.mpc.model.validation'] = 0;
			knxcontrol.item['knxcontrol.mpc.model.identification.result'] = 0;
			knxcontrol.item['knxcontrol.mpc.model.validation.result'] = 0;
		},	
		update: function(item,value){
			knxcontrol.item[item] = value;
			$('[data-item="'+item+'"]').trigger('update');
		},
	},
	smarthome_log: {
		log: [],
		update: function(log){
			var templog = log.concat(this.log);

			// remove items with equal time
			var uniquetimes = [];
			var newlog = []
			$.each(templog, function(index,value){
				if($.inArray(value.time, uniquetimes) === -1){
					uniquetimes.push(value.time);
					newlog.push(value)
				}
			});
			this.log = newlog

			$('[data-role="smarthome_log"]').trigger('update');
		}
	},
// users                                                                     //	
	user:{
		// 1: {id: 1, username: 'test',...}
		get: function(id){
			var where = 'id>0';
			if(id){
				where = 'id='+id;
			}
			$.post('requests/select_from_table.php',{table: 'users', column: 'id,username', where: where},function(result){
				var users = JSON.parse(result);
				$.each(users,function(index,user){
					knxcontrol.user[user.id] = {
						id: user.id,
						username: user.username,
					};
					$('[data-role="user_list"]').trigger('update',user.id);
					$('[data-role="user_profile"]').trigger('update');
				});
			});
		},
		update: function(id,field,value){
			// set the user in the database
			$.post('requests/update_table.php',{table: 'users', column: field.join(';'), value: value.join(';'), where: 'id='+id},function(result){
				// on success update knxcontrol
				console.log(result);
				knxcontrol.user.get(id);
			});
		},
		add: function(){
			$.post('requests/insert_into_table.php',{table: 'users', column: ['name','password'].join(';'), value: ['New user','newpass'].join(';')},function(result){
				id = JSON.parse(result);
				id = id[0];
				// add the action to knxcontrol
				knxcontrol.user.get(id);
			});
		},
		del: function(id){
			$.post('requests/delete_from_table.php',{table: 'users', where: 'id='+id},function(result){
				delete knxcontrol.user[id];
				$('[data-role="user_list"]').trigger('update',id);
			});
		}
	},

// alarms                                                                    //
	alarm: {
		// 1: {id: 1, section_id: 2, hour: 13, minute: 12, mon: 1, tue: 1, wed: 1, thu: 1, fri: 1, sat: 1, sun: 1, action_id: 2},...
		get: function(id){
			var where = 'id>0';
			if(id){
				where = 'id='+id;
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
				knxcontrol.action.get();
			});
		},
		update: function(id,field,value){
			// set the alarm in the database
			$.post('requests/update_table.php',{table: 'alarms', column: field, value: value, where: 'id='+id},function(result){
				// on success update knxcontrol
				knxcontrol.alarm[id][field] = value;
			});
		},
		add: function(section_id){
			$.post('requests/insert_into_table.php',{table: 'alarms', column: ['hour','minute','sectionid','mon','tue','wed','thu','fri','sat','sun','action_id'].join(';'), value: [12,0,section_id,1,1,1,1,1,0,0,0].join(';')},function(result){
				alarm_id = JSON.parse(result);
				alarm_id = alarm_id[0];
				
				// add the alarm to knxcontrol
				knxcontrol.alarm.get(alarm_id);
			});
		},
		del: function(id){
			$.post('requests/delete_from_table.php',{table: 'alarms', where: 'id='+id},function(result){
				delete knxcontrol.alarm[id];
				$('[data-role="alarm"]').trigger('update',id);
			});
		}
	},
	
// actions                                                                   //
	action:{
		// 1: {id: 1, name: 'Licht aan', section_id: 0, actions: [{id: 1, delay: 0, item: 'living.lights.licht', value: 0},{...},...]},...
		get: function(id){
			var where = 'id>0';
			if(id){
				where = 'id='+id;
			}
			$.post('requests/select_from_table.php',{table: 'actions', column: '*', where: where},function(result){
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
		update: function(id,data_field,value){
			// set the alarm in the database
			$.post('requests/update_table.php',{table: 'actions', column: data_field.join(';'), value: value.join(';'), where: 'id='+id},function(result){
				// on success update knxcontrol
				console.log(result);
				knxcontrol.action.get(id);
			});
		},
		add: function(){
			$.post('requests/insert_into_table.php',{table: 'actions', column: ['name','sectionid','delay1'].join(';'), value: ['Name',0,0].join(';')},function(result){
				id = JSON.parse(result);
				id = id[0];
				// add the action to knxcontrol
				knxcontrol.action.get(id);
			});
		},
		del: function(id){
			$.post('requests/delete_from_table.php',{table: 'actions', where: 'id='+id},function(result){
				delete knxcontrol.action[id];
				$('[data-role="action_list"]').trigger('update',id);
			});
		}
	},
	
// measurement                                                             //
	measurement: {
		// 1: {id: 1, name: 'Temperatuur', item: 'buiten.measurements.temperature', quantity: 'Temperature', unit: 'degC', description: 'Buiten temeratuur', quarterhourdata: [], daydata: [], weekdata: [], monthdata: []},
		get: function(id){
			var where = 'id>0';
			if(id){
				where = 'id='+id;
			}
			var that = this;
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
						loading_quarterhourdata: false,
						loading_weekdata: false,
						loading_monthdata: false
					};
					$('[data-role="measurement_list"]').trigger('update',result.id);
					//that.get_data(result.id);  // this will load all data which results in a lot of data traffic
				});
				$('[data-role="chart"]').trigger('get_data');
			});
		},
		update: function(id,field,value){
			var that = this;
			$.post('requests/update_table.php',{table: 'measurements_legend', column: field, value: value, where: 'id='+id},function(result){
				that.get(id);
			});
		},
		get_quarterhourdata: function(id){
			if(this[id]){
				
				var that = this[id];
				// a loading variable as the load time is significant to not load double
				if(that.loading_quarterhourdata==false){
					that.loading_quarterhourdata = true;
					$.post('requests/select_from_table.php',{table: 'measurements_average_quarterhour', column: 'time,value', where: 'signal_id='+id+' AND time > '+((new Date()).getTime()/1000-7*24*3600), orderby: 'time'},function(result){
						that.quarterhourdata = []
						$.each(JSON.parse(result),function(index,value){
							that.quarterhourdata.push([parseFloat(value.time)*1000,parseFloat(value.value)]);
						});
						
						// devide the data in days and average
						var starttime = [];
						var sum = [];
						var numel = [];
						
						var oldhour =  0;
						
						$.each(that.quarterhourdata,function(index,value){
							var date = new Date(value[0]);
							var hour =  date.getHours();

							if(hour<oldhour){
								starttime.push(value[0]);
								sum.push(0);
								numel.push(0);
							}
							if(sum.length>0){
								sum[sum.length - 1] += value[1];
								numel[sum.length - 1] += 1;
							}
							oldhour = hour;
						});

						that.daydata = [];
						$.each(sum,function(index,value){
							that.daydata.push([starttime[index],sum[index]/numel[index]]);
						});
						that.loading_quarterhourdata = false;
						$('[data-role="chart"]').trigger('update',id);
						
					});
				}
			}
		},
		get_weekdata: function(id){
			if(this[id]){
			
				var that = this[id];
				if(that.loading_weekdata==false){
					that.loading_weekdata = true;
					$.post('requests/select_from_table.php',{table: 'measurements_average_week', column: 'time,value', where: 'signal_id='+id+' AND time > '+((new Date()).getTime()/1000-52*7*24*3600), orderby: 'time'},function(result){
						that.weekdata = []
						
						$.each(JSON.parse(result),function(index,value){
							that.weekdata.push([parseFloat(value.time)*1000,parseFloat(value.value)]);
						});
						
						that.loading_weekdata = false;
						$('[data-role="chart"]').trigger('update',id);
					});
				}
			}
		},
		get_monthdata: function(id){
			if(this[id]){
			
				that = this[id];
				if(that.loading_monthdata==false){
					that.loading_monthdata = true;
					$.post('requests/select_from_table.php',{table: 'measurements_average_month', column: 'time,value', where: 'signal_id='+id+' AND time > '+((new Date()).getTime()/1000-365*24*3600), orderby: 'time'},function(result){
						that.monthdata = []
						
						$.each(JSON.parse(result),function(index,value){
							that.monthdata.push([parseFloat(value.time)*1000,parseFloat(value.value)]);
						});
						
						that.loading_monthdata = false;
						$('[data-role="chart"]').trigger('update',id);
					});
				}
			}
		}
	},
// profile                                                                   //
	profile: {
		// 1: {id: 1, name: 'Temperatuur', quantity: 'Temperature', unit: 'degC', description: 'Buiten temeratuur', data: []},
		get: function(id){
			var where = 'id>0';
			if(id){
				where = 'id='+id;
			}
			var that = this;
			$.post('requests/select_from_table.php',{table: 'profiles_legend', column: '*', where: where},function(result){
				var results = JSON.parse(result);
				$.each(results,function(index,result){
					that[result.id] = {
						id: result.id,
						name: result.name,
						quantity: result.quantity,
						unit: result.unit,
						description: result.description,
						data: []
					};
					// get values
					that.get_data(result.id);
				});
			});
		},
		update: function(id,field,value){
			var that = this;
			$.post('requests/update_table.php',{table: 'profiles_legend', column: field, value: value, where: 'id='+id},function(result){
				that.get(id);
			});
		},
		add: function(){
			var that = this;
			$.post('requests/insert_into_table.php',{table: 'profiles_legend', column: ['name','quantity','unit','description'].join(';'), value: ["'Name'","''","''","''"].join(';')},function(result){
				var id = JSON.parse(result);
				id = id[0];
				//add blank data
				$.post('requests/insert_into_table.php',{table: 'profile', column: ['profile_id','time','value'].join(';'), value: [id,0,0].join(';')},function(result){
					that.get(id);
				});
			});
		},
		del: function(id){
			var that = this;
			$.post('requests/delete_from_table.php',{table: 'profiles_legend', where: 'id='+id},function(result){
				$.post('requests/delete_from_table.php',{table: 'profile', where: 'profile_id='+id},function(result){
					delete that[id];
					$('[data-role="profile_list"]').trigger('update',id);
				});
			});
		},
		get_data: function(id){
			if(this[id]){
			
				var that = this;
				$.post('requests/select_from_table.php',{table: 'profile', column: 'time,value', where: 'profile_id='+id, orderby: 'time'},function(result){
					var data = [];
					$.each(JSON.parse(result),function(index,value){
						data.push([parseFloat(value.time)*1000,parseFloat(value.value)]);
					});
					that[id].data = data;
					$('[data-role="profile_list"]').trigger('update',id);
				});
			}
		},
		update_data: function(id,time,value){
			if(this[id]){
			
				var that = this;
				$.post('requests/delete_from_table.php',{table: 'profile', where: 'profile_id='+id},function(result){
				
					$.each(time,function(index,data){
						$.post('requests/insert_into_table.php',{table: 'profile', column: ['profile_id','time','value'].join(';'), value: [id,time[index],value[index]].join(';')},function(result){
							console.log(result);
							that.get_data(id);
						});
					});
				});
			}
		}
	},
	
// helping functions                                                         //
	getkeys: function(objectstring){
		var ind = [];
		
		$.each(knxcontrol[objectstring],function(index,object){
			if(typeof object == 'object' || typeof object == 'number'){
				ind.push(index);
			}
		});
		return ind;
	}	
}
