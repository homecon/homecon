

pagebuilder = {
	home: {
		name: 'Home',
		section: [
			{
				type: ''
			},
			{
				type: ''
			},
			{
				type: ''
			},
		]
	},
	section: [],
	publish: function(){
		// create pages.php
	},
	add_section: function(){
		pagebuilder.section.push({
			id: '',
			name: '',
			page: [],
			update: function(id,name){
				this.id = id;
				this.name = name;
			},
			add_page: function(){
				this.page.push({
					id: '',
					name: '',
					img: '',
					temperature_item:'',
					section: [],
					update: function(id,name,img,temperature_item){
						this.id = id;
						this.name = name;
						this.img = img;
						this.temperature_item = temperature_item;
					},
					add_section: function(){
						this.section.push({
							name: '',
							type: '',
							widget: [],
							add_widget: function(widget,options){
								this.widget.push({
									
								});
							},
							del: function(){
								delete this;
							
							},
						});
					},
					del: function(){
						delete this;
					},
					render: function(){
						console.log('rendering');
						// add the page elements to the DOM for temporary displaying
						// clear the container and start fresh
						$('#pagebuilder div').empty();
						// add header
						$('#pagebuilder div').append('<header><img src="icons/ws/'+this.img+'"><h1>'+this.name+'</h1></header>');
						if(this.temperature_item != ''){
							$('#pagebuilder div header').append('<div class="value"><span data-role="displayvalue" data-item="'+this.temperature_item+'" data-digits="1"></span>&deg;C</div>');
						}
						
						// sections
						$.each(this.section,function(index,section){
							if(section.type=='collabsible'){
								$('#pagebuilder div').append('<section data-role="collapsible" data-theme="a" data-collapsed="false" data-id="'+index+'"><h1>'+section.name+'</h1>');
							}
							else if(section.type=='collabsible'){
								$('#pagebuilder div').append('<section data-role="collapsible" data-theme="a" data-collapsed="true" data-id="'+index+'"><h1>'+section.name+'</h1>');
							}
							else{
								$('#pagebuilder div').append('<section data-id="'+index+'">');
							}
							// widgets
							$.each(section.widget,function(index,widget){
								$('#pagebuilder div').append('<div data-role="'+widget+'" '+options+' data-id="'+index+'"></div>');
							});
							$('#pagebuilder div').append('</section>');
						});
						
						// enhance
						$('#pagebuilder').enhanceWithin();
					}
				});
			},
			del: function(){
				delete this;
			}
		});
	}
};


// test
pagebuilder.add_section();
pagebuilder.section[0].update('firstfloor','First floor');
pagebuilder.section[0].add_page();
pagebuilder.section[0].page[0].update('living','Living','scene_livingroom.png','living.measurements.temperature');
console.log(JSON.stringify(pagebuilder));

$(document).on('pageinit','#pagebuilder',function(){
	pagebuilder.section[0].page[0].render();
});

/* example model
pagebuilder = {
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