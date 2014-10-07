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
	var helperfunction = function(id) {
		return function(result, textStatus, jqXHR) {
			$('#'+id).html(result).trigger('create');
		};
	};
		
	$('.alarm a.add').click(function(){
		id = $( this ).parents('.alarm_container').attr('id');
		sectionid = id.split('_');
		sectionid = id[2];
		
		$.post( 'requests/alarm_add.php',{sectionid: sectionid},helperfunction(sectionid));
	});
});