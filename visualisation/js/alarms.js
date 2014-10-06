//////////////////////////////////////////////////////////////////////////////
// set alarm
//////////////////////////////////////////////////////////////////////////////
$('.alarm input, .alarm select').change(function(){

	// get the alarm id
	id = $(this).parents('.alarm').attr('id');
	alarmid = id.split('_');
	alarmid = alarmid[1];
	
	// get the column tot add value to
	column = $(this).attr('data-column');
	value = $(this).val();
	
	// post id column and value to add to database
	$.post( 'requests/alarm_set.php', {'id': alarmid , 'column': column , 'value': value}); 
	//for debugging: 
	//$.post( 'requests/alarm_set.php', {'id': $id , 'column': 'time' , 'value': $(this).val()}, function(response){alert(response);}); 
						


});

//////////////////////////////////////////////////////////////////////////////
// add alarm
//////////////////////////////////////////////////////////////////////////////
var helperfunction = function(id) {
	return function(result, textStatus, jqXHR) {
		$('#'+id).html(result).trigger('create');
	};
};
	
$('.add_alarm').click(function(){
	id = $( this ).parents('.alarm_container').attr('id');
	sectionid = id.split('_');
	sectionid = id[2];
	
	$.post( 'requests/alarm_add.php',{sectionid: id},helperfunction(id));
});