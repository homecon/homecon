//////////////////////////////////////////////////////////////////////////////
// set alarm
//////////////////////////////////////////////////////////////////////////////
$(document).ready(function(){
	$('.alarm input,.alarm select').change(function(){
		
		// get the alarm id
		id = $(this).parents('.alarm').attr('data-id');
		
		// get the column tot add value to
		column = $(this).attr('data-column');
		value = $(this).val();
		
		if($(this).attr('type')=='checkbox'){
			value = $(this).is(':checked');
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
$(document).ready(function(){

	$('.alarm_container a.add').click(function(){

		var container = $( this ).parents('.alarm_container');
		var sectionid = container.attr('data-id');
		
		var itemlist = $(this).attr('data-itemlist');
		var actionlist = $(this).attr('data-actionlist');
		
		// give temprary ids and add the alarm, final id's are assigned after adding to the database
		oldid = -1;
		var values = {id: oldid, hour: 12, minute: 0, mon: 1, tue: 1, wed: 1, thu: 1, fri: 1, sat: 0, sun: 0, item: '', action: '' };
		
		display_alarm(sectionid,itemlist,actionlist,values);
		
		// post sectionid to add to database
		$.post('requests/alarm_add.php',{sectionid: sectionid},function(id){
			
			alert(id);
			
			// change ids according to the database
			// days
			var days         = ['mon','tue','wed','thu','fri','sat','sun'];
			var days_string  = ['maa','din','woe','don','vri','zat','zon'];
			var days_checked = [''   ,''   ,''   ,''   ,''   ,''   ,''];
			for(i=0;i<days.length;i++){
				$('#'+days[i]+oldid).attr('id',days[i]+id);
				newAlarm.find('#'+days[i]+oldid+'_lab').attr('for',days[i]+id);
			}
		});
		
		
	});
});

//////////////////////////////////////////////////////////////////////////////
// delete alarm
//////////////////////////////////////////////////////////////////////////////
$(document).ready(function(){
	$('.alarm_container a.add').click(function(){
	
		var alarm = $( this ).parents('.alarm');
		var id = alarm.attr('data-id');
		
		// remove the display of the alarm
		alarm.remove();
		
		// post id to remove from database
		$.post('requests/alarm_delete.php',{id: id});
	
	});
});

//////////////////////////////////////////////////////////////////////////////
// display alarm code
//////////////////////////////////////////////////////////////////////////////
display_alarm = function(sectionid,itemlist,actionlist,values){

	var id = values['id'];
	
	
	// duplicate template and change what needs to be changed
	var newAlarm = $('#alarm_template').clone();
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
		if( values[days[i]] ){
			newAlarm.find('#id_'+days[i]).prop('checked', true);
		}
		else{
			newAlarm.find('#id_'+days[i]).prop('checked', false);
		}
		newAlarm.find('#id_'+days[i]).attr('id',days[i]+id);
		newAlarm.find('#id_'+days[i]+'_lab').attr('for',days[i]+id);
		newAlarm.find('#id_'+days[i]+'_lab').attr('id',days[i]+id+'_lab');
	}
	
	
	// parse items
	var items   = values['item'].split(',');
	var itemlist   = itemlist.split(',');
	
	var newOption = newAlarm.find('.alarm_items option:first').clone();
	
	for(i=0;i<itemlist.length;i++){
		var itemselected = '';
		var item = itemlist[i];
		
		if($.inArray(item, values['item'])){
			itemselected =  'selected=selected';
		}
		newAlarm.find("select[data-column='item']").append("<option "+itemselected+" value='"+item+"'>"+item+"</option>");
	}
	
	
	// parse actions
	var actions   = values['action'].split(',');
	var actionlist   = actionlist.split(',');

	var newOption = newAlarm.find('.alarm_actions option:first').clone();
	for(i=0;i<actionlist.length;i++){
		var actionselected = '';
		var action = actionlist[i];
			
		if($.inArray(action, values['action'])){
			actionselected =  'selected=selected';
		}	
		newAlarm.find("select[data-column='action']").append("<option "+actionselected+" value='"+action+"'>"+action+"</option>");
	}
	
	newAlarm.show();
	$('#alarm_add_'+sectionid).before(newAlarm);
	
};