

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
							update: function(name,type){
								this.name = name;
								this.type = type;
							},
							add_widget: function(type,options){
								this.widget.push({
									type: type,
									options: options,
									update: function(type,options){
										this.type = type;
										this.options = options;
									}
								});
							},
							del: function(){
								delete this;
							
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
	}
};


/*****************************************************************************/
/*                     views                                                 */
/*****************************************************************************/
render_page = function(section_id,page_id){
	console.log('rendering page');
	page = pagebuilder.section[section_id].page[page_id];
	
	var select_widget_values = {};
	// if the page is rebuilt get the widget select values
	$.each($('#renderpage').find('select.select_widget'),function(index,select){
		select_widget_values[$(select).parents('section').attr('data-id')] = $(select).val();
	});

	// add the page elements to the DOM for temporary displaying
	// clear the container and start fresh
	$('#renderpage').empty();
	$('#renderpage').attr('data-page_id',page_id);
	$('#renderpage').attr('data-page_section_id',section_id);
	// add header
	$('#renderpage').append('<header><img src="icons/ws/'+page.img+'"><h1>'+page.name+'</h1></header>');
	if(page.temperature_item != ''){
		$('#renderpage header').append('<div class="value"><span data-role="displayvalue" data-item="'+page.temperature_item+'" data-digits="1"></span>&deg;C</div>');
	}
	
	// sections
	$.each(page.section,function(index,section){
		if(section.type=='collabsible'){
			$('#renderpage').append('<section data-role="collapsible" data-theme="a" data-collapsed="false" data-id="'+index+'"><h1>'+section.name+'</h1>');
		}
		else if(section.type=='collabsible'){
			$('#renderpage').append('<section data-role="collapsible" data-theme="a" data-collapsed="true" data-id="'+index+'"><h1>'+section.name+'</h1>');
		}
		else{
			$('#renderpage').append('<section data-id="'+index+'"></section>');
		}
		// widgets
		section_index = index;
		$.each(section.widget,function(index,widget){
			$('#renderpage section[data-id="'+section_index+'"]').append('<div data-role="'+widget.type+'" '+widget.options+' data-id="'+index+'"><a href"#" class="edit_widget" data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext" data-inline="true">Edit</a></div>');
		});
		$('#renderpage section[data-id="'+section_index+'"]').append('<fieldset class="ui-grid-a"><div class="ui-block-a"><select class="select_widget" data-native-menu="false"><option>Select Widget</option></select></div><div class="ui-block-b"><a href="#" class="add_widget" data-role="button" data-id="'+page.id+'">Add</a></div>');
		$('#renderpage section[data-id="'+section_index+'"] select').append('<option value="lightswitch">Light switch</option>');
		if(index in select_widget_values){
			$('#renderpage section[data-id="'+section_index+'"] select').val(select_widget_values[index]);
		}
	});
	$('#renderpage').append('<a data-role="button" data-id="'+page.id+'">Add section</a>');
	
	// enhance
	$('#pagebuilder').enhanceWithin();
}
	
render_menu = function(){
	console.log('rendering menu');
	$('#rendermenu').empty();
	
	// sections
	$.each(pagebuilder.section,function(index,section){
		$('#rendermenu').append('<section data-role="collapsible" data-id="'+index+'"  data-section="'+section.id+'" data-theme="a" data-content-theme="b"><h1>'+section.name+'</h1><ul data-role="listview" data-inset="false"></ul><a href="#" data-role="button">Add page</a></section>');
		//pages
		section_index = index;
		$.each(section.page,function(index,page){
			$('#rendermenu section[data-id="'+section_index+'"] ul').append('<li><a href="#"><img src="icons/ws/'+page.img+'" data-id="'+index+'" ><h1>'+page.name+'</h1></a></li>');
		});
	});
	$('#rendermenu').append('<a href="#" data-role="button">Add section</a>');
	
	// enhance
	$('#menu').enhanceWithin();
}


/*****************************************************************************/
/*                     controls                                              */
/*****************************************************************************/
$(document).on('click','a.add_widget',function(){

	var page_section_id = $(this).parents('#renderpage').attr('data-page_section_id');
	var page_id = $(this).parents('#renderpage').attr('data-page_id');
	var section_id = $(this).parents('section').attr('data-id');
	
	var widget_type = $(this).parents('section').find('select.select_widget').val();

	if(widget_type!='Select Widget'){
		pagebuilder.section[page_section_id].page[page_id].section[section_id].add_widget(widget_type,'');
		render_page(page_section_id,page_id);
	}
	
});



// test
pagebuilder.add_section();
pagebuilder.section[0].update('firstfloor','First floor');
pagebuilder.section[0].add_page();
pagebuilder.section[0].page[0].update('living','Living','scene_livingroom.png','living.measurements.temperature');
pagebuilder.section[0].page[0].add_section();
pagebuilder.section[0].page[0].section[0].update('Light','collabsible');
pagebuilder.section[0].page[0].section[0].add_widget('lightswitch','data-item="item1" data-label="Lightswitch"');
pagebuilder.section[0].page[0].section[0].add_widget('lightswitch','data-item="item1" data-label="Lightswitch"');
pagebuilder.section[0].page[0].section[0].add_widget('lightdimmer','data-item="item2" data-label="Lightdimmer"');
pagebuilder.section[0].page[0].section[0].add_widget('shading','data-item="item3" data-label="Shading"');

$(document).on('pageinit','#pagebuilder',function(){
	
	render_menu();
	render_page(0,0);
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