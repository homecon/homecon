//////////////////////////////////////////////////////////////////////////////
// set alarm
//////////////////////////////////////////////////////////////////////////////
$(document).ready(function(){
	$('.alarm input').change(function(){
		
		// get the alarm id
		id = $(this).parents('.alarm').attr('data-id');
		
		// get the column tot add value to
		column = $(this).attr('data-column');
		value = $(this).val();
		
		if($(this).attr('type')=='checkbox'){
			if($(this).is(':checked')){
				value = 1;
			}
			else{
				value = 0;
			}
		}
		
		alert(value);
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
	var helperfunction = function(id) {
		return function(result, textStatus, jqXHR) {
			$('#'+id).html(result).trigger('create');
		};
	};
		
	$('.add_alarm').click(function(){
		id = $( this ).parents('.alarm_container').attr('id');
		sectionid = id.split('_');
		sectionid = id[2];
		
		$.post( 'requests/alarm_add.php',{sectionid: sectionid},helperfunction(sectionid));
	});
});