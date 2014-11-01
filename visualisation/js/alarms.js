//////////////////////////////////////////////////////////////////////////////
// set alarm
//////////////////////////////////////////////////////////////////////////////
$(document).ready(function(){
	$('.alarm_container').on('change','.alarm input,.alarm select',function(){
		
		// get the alarm id
		id = $(this).parents('.alarm').attr('data-id');
		
		// get the column tot add value to
		column = $(this).attr('data-column');
		value = $(this).val();
		
		if($(this).attr('type')=='checkbox'){
			value = $(this).is(':checked');
		}
		
		if($(this).attr('data-column')=='action'){
			column = 'action_id'
		}
		
		
		// post id column and value to add to database
		$.post( 'requests/alarm_set.php', {'id': id , 'column': column , 'value': value}); 
		
		//for debugging: 
		//$.post( 'requests/alarm_set.php', {'id': id , 'column': column , 'value': value}, function(response){alert(response);}); 
							
	});
});

//////////////////////////////////////////////////////////////////////////////
// add alarm
//////////////////////////////////////////////////////////////////////////////
$(document).on('click','.alarm_container a.add',function(){

	var container = $( this ).parents('.alarm_container');
	var sectionid = container.attr('data-id');
	
	// give temprary ids and add the alarm, final id's are assigned after adding to the database
	var oldid = -1;
	var values = {'id': oldid, 'hour': 12, 'minute': 0, 'mon': 1, 'tue': 1, 'wed': 1, 'thu': 1, 'fri': 1, 'sat': 0, 'sun': 0, 'action': '' };
	
	var newAlarm = display_alarm(sectionid,values);
	$(this).parent().before(newAlarm);
	
	// post sectionid to add to database
	$.post('requests/alarm_add.php',{sectionid: sectionid},function(id){
		
		// change ids according to the database
		$('#alarm'+oldid).attr('data-id',id);
		$('#alarm'+oldid).attr('id','alarm'+id);
		
		// days
		var days         = ['mon','tue','wed','thu','fri','sat','sun'];
		var days_string  = ['maa','din','woe','don','vri','zat','zon'];
		var days_checked = [''   ,''   ,''   ,''   ,''   ,''   ,''];
		for(i=0;i<days.length;i++){
			$('#'+days[i]+oldid).attr('id',days[i]+id);
			$('#'+days[i]+oldid+'_lab').attr('for',days[i]+id);
			
		}
	});
		
});

//////////////////////////////////////////////////////////////////////////////
// delete alarm
//////////////////////////////////////////////////////////////////////////////
$(document).on('click','.alarm a.delete',function(){

	var alarm = $( this ).parents('.alarm');
	var id = alarm.attr('data-id');
	
	// remove the display of the alarm
	alarm.remove();
	
	// post id to remove from database
	$.post('requests/alarm_delete.php',{'id': id});

});
//////////////////////////////////////////////////////////////////////////////
// initialize alarms
//////////////////////////////////////////////////////////////////////////////
$(document).on('pagebeforecreate',function(){

	//cycle through all alarm_placeholder
	$( ".alarm_placeholder" ).each(function(){
		
		// create variables
		var sectionid = $(this).parents('.alarm_container').attr('data-id');
		var values = {
			id: $(this).attr('data-id'),
			hour: $(this).attr('data-hour'),
			minute: $(this).attr('data-minute'),
			mon: $(this).attr('data-mon'),
			tue: $(this).attr('data-tue'),
			wed: $(this).attr('data-wed'),
			thu: $(this).attr('data-thu'),
			fri: $(this).attr('data-fri'),
			sat: $(this).attr('data-sat'),
			sun: $(this).attr('data-sun'),
			action: $(this).attr('data-action')
		};
		
		//creat the alarm and display
		newAlarm = display_alarm(sectionid,values);
		$(this).replaceWith(newAlarm);
		
	});
});

//////////////////////////////////////////////////////////////////////////////
// display alarm code
//////////////////////////////////////////////////////////////////////////////
display_alarm = function(sectionid,values){

	var id = values['id'];
	
	// duplicate template and change what needs to be changed
	var newAlarm = $('#alarm_template'+sectionid).clone();
	newAlarm.attr('id','alarm'+id); 
	newAlarm.attr('data-id',id);
	
	
	//parse time
	function padtime(num) {
		var s = num+"";
		while (s.length < 2) s = "0" + s;
		return s;
	}
	var time = padtime(values['hour']) + ":" + padtime(values['minute']);
	
	newAlarm.find('input[type=time]').val(time);
	
	
	// parse days
	var days         = ['mon','tue','wed','thu','fri','sat','sun'];
	var days_string  = ['maa','din','woe','don','vri','zat','zon'];
	var days_checked = [''   ,''   ,''   ,''   ,''   ,''   ,''];
	for(i=0;i<days.length;i++){
		if( values[days[i]]==1 ){
			newAlarm.find('#id_'+days[i]).prop('checked', true);
		}
		else{
			newAlarm.find('#id_'+days[i]).prop('checked', false);
		}
		newAlarm.find('#id_'+days[i]).attr('id',days[i]+id);
		newAlarm.find('#id_'+days[i]+'_lab').attr('for',days[i]+id);
		newAlarm.find('#id_'+days[i]+'_lab').attr('id',days[i]+id+'_lab');
	}
	
	// parse actions
	var actions    = values['action'].split(',');
	var actionlist = newAlarm.attr('data-actionlist').split(',');
	var actionname = newAlarm.attr('data-actionname').split(',');
	for(i=0;i<actionlist.length;i++){
		var actionselected = ' selected=selected';
		var actionid = actionlist[i];
		
		if($.inArray(actionid, actions)<0){
			actionselected = '';
		}	
		newAlarm.find("select[data-column='action']").append("<option"+actionselected+" value='"+actionid+"'>"+actionname[i]+"</option>");
	}
	
	newAlarm.show();
	return newAlarm;
	
};


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// alarm actions
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// set alarm action
//////////////////////////////////////////////////////////////////////////////
$(document).ready(function(){
	$('.alarm_action_container').on('change','.alarm_action input',function(){
		
		// get the alarm id
		id = $(this).parents('.alarm_action').attr('data-id');
		
		// get the column tot add value to
		column = $(this).attr('data-column');
		value = $(this).val();

		// post id column and value to add to database
		$.post( 'requests/alarm_action_set.php', {'id': id , 'column': column , 'value': value}); 
						
	});
});

//////////////////////////////////////////////////////////////////////////////
// add alarm action
//////////////////////////////////////////////////////////////////////////////
$(document).on('click','.alarm_action_container a.add',function(){

	var container = $( this ).parents('.alarm_action_container');
	
	// give temprary ids and add the alarm, final id's are assigned after adding to the database
	var oldid = -1;
	var values = {'id': oldid, 'name': '', 'sectionid': '0', 'delay1': '', 'item1': '', 'value1': '', 'delay2': '', 'item2': '', 'value2': '', 'delay3': '', 'item3': '', 'value3': '', 'delay4': '', 'item4': '', 'value4': '', 'delay5': '', 'item5': '', 'value5': '' };
	
	var newAction = display_alarm_action(values);
	$(this).before(newAction);
	
	// post sectionid to add to database
	$.post('requests/alarm_action_add.php',function(id){
		
		// change ids according to the database
		$('#alarm_action'+oldid).attr('data-id',id);
		$('#alarm_action'+oldid).attr('id','alarm_action'+id);
		
	});

});
//////////////////////////////////////////////////////////////////////////////
// delete alarm action
//////////////////////////////////////////////////////////////////////////////
$(document).on('click','.alarm_action a.delete',function(){
	var action = $( this ).parents('.alarm_action');
	var id = action.attr('data-id');
	
	// remove the display of the alarm
	action.remove();
	
	// post id to remove from database
	$.post('requests/alarm_action_delete.php',{'id': id});

});
//////////////////////////////////////////////////////////////////////////////
// initialize alarm_actions
//////////////////////////////////////////////////////////////////////////////
$(document).on('pagebeforecreate',function(){

	//cycle through all alarm_placeholder
	$( ".alarm_action_placeholder" ).each(function(){

		// create variables
		var values = {
			id: $(this).attr('data-id'),
			name: $(this).attr('data-name'),
			sectionid: $(this).attr('data-sectionid'),
			delay1: $(this).attr('data-delay1'),
			item1:  $(this).attr('data-item1'),
			value1: $(this).attr('data-value1'),
			delay2: $(this).attr('data-delay2'),
			item2:  $(this).attr('data-item2'),
			value2: $(this).attr('data-value2'),
			delay3: $(this).attr('data-delay3'),
			item3:  $(this).attr('data-item3'),
			value3: $(this).attr('data-value3'),
			delay4: $(this).attr('data-delay4'),
			item4:  $(this).attr('data-item4'),
			value4: $(this).attr('data-value4'),
			delay5: $(this).attr('data-delay5'),
			item5:  $(this).attr('data-item5'),
			value5: $(this).attr('data-value5')
		};
		
		//create the alarm and display
		newAction = display_alarm_action(values);
		$(this).replaceWith(newAction);
		
	});
});
//////////////////////////////////////////////////////////////////////////////
// display alarm action code
//////////////////////////////////////////////////////////////////////////////
display_alarm_action = function(values){
	
	var id = values['id'];
	
	// duplicate template and change what needs to be changed
	var newAction = $('#alarm_action_template').clone();
	newAction.attr('id','alarm_action'+id); 
	newAction.attr('data-id',id);
	
	newAction.find("input[data-column=name]").val(values['name']);
	newAction.find("input[data-column=sectionid]").val(values['sectionid']);
	
	newAction.find("input[data-column=delay1]").val(values['delay1']);
	newAction.find("input[data-column=item1]").val(values['item1']);
	newAction.find("input[data-column=value1]").val(values['value1']);
	newAction.find("input[data-column=delay2]").val(values['delay2']);
	newAction.find("input[data-column=item2]").val(values['item2']);
	newAction.find("input[data-column=value2]").val(values['value2']);
	newAction.find("input[data-column=delay3]").val(values['delay3']);
	newAction.find("input[data-column=item3]").val(values['item3']);
	newAction.find("input[data-column=value3]").val(values['value3']);
	newAction.find("input[data-column=delay4]").val(values['delay4']);
	newAction.find("input[data-column=item4]").val(values['item4']);
	newAction.find("input[data-column=value4]").val(values['value4']);
	newAction.find("input[data-column=delay5]").val(values['delay5']);
	newAction.find("input[data-column=item5]").val(values['item5']);
	newAction.find("input[data-column=value5]").val(values['value5']);
	
	newAction.show();
	return newAction;
	
};