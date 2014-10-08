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