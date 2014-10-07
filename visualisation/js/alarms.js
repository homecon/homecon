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
		
	$('.alarm a.add').click(function(){
		container = $( this ).parents('.alarm_container');
		sectionid = container.attr('data-id');
		
		//container.children().filter('.alarm').map( function(){ return $(this).attr('data-id'); }).get();
		//get last alarm in the container
		alarm = container.children().filter('.alarm').last();
		
		// post sectionid to add to database
		$.post('requests/alarm_add.php',{sectionid: sectionid},function(response){
			id = response;
			
			alert(response);
		
			alarm.clone().insertAfter(alarm);
		});
		
		
	});
});