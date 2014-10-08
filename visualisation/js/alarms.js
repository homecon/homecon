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

		container = $( this ).parents('.alarm_container');
		sectionid = container.attr('data-id');
		
		var newAlarm = $('#alarm_template').clone();
		
		// give temprary ids and add the alarm, final id's are assigned after adding to the database
		
		$('#alarm_add_'+sectionid).before(newAlarm);
		
		// post sectionid to add to database
		$.post('requests/alarm_add.php',{sectionid: sectionid},function(response){
			
			id = response;
			
			alert(id);
			
			newAlarm.attr('id','alarm'+id); 
			newAlarm.attr('data-id',id); 
			newAlarm.find('#id_mon').attr('id','mon'+id);
			newAlarm.find('#id_tue').attr('id','tue'+id);
			newAlarm.find('#id_wed').attr('id','wed'+id);
			newAlarm.find('#id_thu').attr('id','thu'+id);
			newAlarm.find('#id_fri').attr('id','fri'+id);
			newAlarm.find('#id_sat').attr('id','sat'+id);
			newAlarm.find('#id_sun').attr('id','sun'+id);
			
			newAlarm.find('#id_mon_lab').attr('for','mon'+id);
			newAlarm.find('#id_tue_lab').attr('for','tue'+id);
			newAlarm.find('#id_wed_lab').attr('for','wed'+id);
			newAlarm.find('#id_thu_lab').attr('for','thu'+id);
			newAlarm.find('#id_fri_lab').attr('for','fri'+id);
			newAlarm.find('#id_sat_lab').attr('for','sat'+id);
			newAlarm.find('#id_sun_lab').attr('for','sun'+id);
			
			newAlarm.show();
			$('#alarm_add_'+sectionid).before(newAlarm);
		});
		
		
	});
});

//////////////////////////////////////////////////////////////////////////////
// add alarm code
//////////////////////////////////////////////////////////////////////////////
add_alarm = function(sectionid,itemlist,actionlist,values){

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