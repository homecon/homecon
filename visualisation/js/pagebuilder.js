

pagebuilder = {
	section: [],
	add_section: function(){
		pagebuilder.section.push({
			id: '',
			name: '',
			page: []
		});
	},
	update_section: function(id,name){
		this.id = id;
		this.name = name;
	},
	add_page: function(section){
		section.page.push({
			id: '',
			name: '',
			img: '',
			temperature_item:'',
			section: [],
		});
	},
	update_page: function(page,id,name,img,temperature_item){
		page.id = id;
		page.name = name;
		page.img = img;
		page.temperature_item = temperature_item;
	},
	delete_page: function(section,id){
		delete section.page[id];
	},
	add_page_section: function(page){
		page.section.push({
			name: '',
			type: '',
			widget: []
		});
	},
	update_page_section: function(section,name,type){
		section.name = name;
		section.type = type;
	},
	add_widget: function(section,type,options){
		section.widget.push({
			type: type,
			options: options,
		});
	},
	update_widget: function(widget,type,options){
		widget.type = type;
		widget.options = options;
	}
};
/*****************************************************************************/
/*                     methods                                               */
/*****************************************************************************/




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
	$('#renderpage').attr('data-section_id',section_id);
	$('#renderpage').attr('data-page_id',page_id);
	
	
	// add header
	if(page.id != 'home'){
		$('#renderpage').append('<header><img src="icons/ws/'+page.img+'"><h1>'+page.name+'</h1></header>');
		if(page.temperature_item != ''){
			$('#renderpage header').append('<div class="value"><span data-role="displayvalue" data-item="'+page.temperature_item+'" data-digits="1"></span>&deg;C</div>');
		}
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
	$('#renderpage').append('<a href="#" class="add_page_section" data-role="button" data-id="'+page.id+'">Add section</a>');
	
	// enhance
	$('#pagebuilder').enhanceWithin();
}
	
render_menu = function(){
	console.log('rendering menu');
	$('#rendermenu').empty();
	
	
	// sections
	$.each(pagebuilder.section,function(index,section){
		if(section.id!='home'){
			$('#rendermenu').append('<section data-role="collapsible" data-id="'+index+'"  data-section="'+section.id+'" data-theme="a" data-content-theme="b"><h1><span>'+section.name+'</span><div class=edit_button><input type="button" data-inline="true" data-icon="grid" data-iconpos="notext"/></div></h1><ul data-role="listview" data-inset="false"></ul><a href="#" data-role="button">Add page</a><a href"#section_def_popup" class="edit_section" data-role="button" data-rel="popup" data-icon="grid">Edit</a></section>');
			//pages
			section_index = index;
			$.each(section.page,function(index,page){
				$('#rendermenu section[data-id="'+section_index+'"] ul').append('<li><a href="#"><img src="icons/ws/'+page.img+'" data-id="'+index+'" ><h1>'+page.name+'</h1></a></li>');
			});
		}
	});
	$('#rendermenu').append('<a href="#" class="add_section" data-role="button">Add section</a>');
	
	// enhance
	$('#menu').enhanceWithin();
}


/*****************************************************************************/
/*                     controls                                              */
/*****************************************************************************/
$(document).on('click','a.add_section',function(){
	pagebuilder.add_section();
	render_menu();
});
$(document).on('click','a.edit_section',function(){
	var section_id = $(this).parents('section').attr('data-id');
	$('#section_def_popup').popup('open');
	$('#section_def_popup_save').attr('data-id',section_id);
	$('#section_def_popup input[data-field="name"]').val(pagebuilder.section[section_id].name);
});
$(document).on('click','#section_def_popup_save',function(){
	var section_id = $(this).attr('data-id');
	$('#section_def_popup').popup('close');
	pagebuilder.section[section_id].name = $('#section_def_popup input[data-field="name"]').val();
	pagebuilder.section[section_id].id = $('#section_def_popup input[data-field="name"]').val().toLowerCase();
	render_menu();
});

$(document).on('click','a.add_widget',function(){

	var section_id = $(this).parents('#renderpage').attr('data-section_id');
	var page_id = $(this).parents('#renderpage').attr('data-page_id');
	var page_section_id = $(this).parents('section').attr('data-id');
	
	var widget_type = $(this).parents('section').find('select.select_widget').val();

	if(widget_type!='Select Widget'){
		pagebuilder.add_widget(pagebuilder.section[section_id].page[page_id].section[page_section_id],widget_type,'');
		render_page(section_id,page_id);
	}
});



$(document).on('pageinit','#pagebuilder',function(){
	
	$.post('requests/select_from_table.php',{table: 'pagebuilder', column: 'model', where: 'id=1'},function(result){
		console.log(result);
		var model = JSON.parse(result);
		console.log(JSON.parse(model[0].model));
		
		pagebuilder.section = JSON.parse(model[0].model);
	
		render_menu();
		render_page(0,0);
		
		$('#menu').panel("open");	
	});
});
$(document).on('click','a.pagebuilder.save',function(){
	console.log(JSON.stringify(pagebuilder.section));
	$.post('requests/update_table.php',{table: 'pagebuilder', column: 'model', value: JSON.stringify(pagebuilder.section), where: 'id=1'},function(result){
		console.log(result);
	});
});