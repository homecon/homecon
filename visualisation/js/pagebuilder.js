

pagebuilder = {
	model: {
		home: {
			name: 'Home',
			section: [
				{
					type: 'clock'
				},
				{
					type: 'weather_current'
				},
				{
					type: 'weather_forecast'
				},
			]
		},
		section: [];
	},
	add_menu_section: function(){
		model.section.push({
			id: '',
			name: '',
			page: [],
			add_page: function(){
				this.page.push({
					id: '',
					name: '',
					img: '',
					temperature_item:'',
					section: [],
					add_section: function(){
						this.section.push({
							name: '',
							group: [],
							add_control: function(group,widget,options){
							
							},
							del_control: function(group,widget){
							
							},
						});
					},
					del: function(){
						delete this;
					}
				});
			},
			del: function(){
				delete this;
			}
		});
	},
};


/* example model
model = {
	home: {
		name: 'Home',
		section: [
			{
				type: 'clock'
			},
			{
				type: 'weather_current'
			},
			{
				type: 'weather_forecast'
			},
		]
	},
	section: [
		{
			id: 'central',
			name: 'Central',
			page: [
				{
					id: 'light',
					name: 'Light',
					img: 'light_light.png',
					temperature_item: '',
				}
			]
		},
		{
			id: 'firstfloor',
			name: 'First floor',
			page: [
				{
					id: 'living',
					name: 'Living',
					img: 'scene_livingroom.png',
					temperature_item: 'living.measurements.temperature',
					section: [
						{
							name: 'Light',
							group: [
								[
									{type: 'buttongroup', item: ['living.scenes','living.scenes','living.scenes','living.scenes'], value: [1,2,3,4], text: ['Dinner','Company','TV','Lights Off']}
								],
								[
									{type: 'lightswitch', item: 'living.lights.spots_kitchen'    , value: [0,1], text: 'Kitchen spots'},
									{type: 'lightswitch', item: 'living.lights.light_kitchen'    , value: [0,1], text: 'Kitchen'},
									{type: 'lightswitch', item: 'living.lights.spots_dinnertable', value: [0,1], text: 'Dinnertable spots'},
									{type: 'lightswitch', item: 'living.lights.light_dinnertable', value: [0,1], text: 'Dinnertable'}
									
								],
								[
									{type: 'lightdimmer', item: 'living.lights.light_tv', value: [0,255], text: 'TV lights'}
								]
							]
						},
						{
							name: 'Shading',
							group: [
								[
									{type: 'shadingcontrol', item: '', value: [0,255], text: 'Back shading'}
								]
							]
						}
					]
				},
				{
					id: 'hallway',
					name: 'Hallway',
					img: 'scene_hall.png',
					temperature_item: '',
					section: [
						{
							name: 'Light',
							group: [
								[
									{type: 'lightswitch', item: 'hallway.lights.light'    , value: [0,1], text: 'Light'},
	
								]
							]
						}
					]
				}
			]	
		}
	]
}

alert(JSON.stringify(model));
*/