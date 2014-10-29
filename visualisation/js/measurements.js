//////////////////////////////////////////////////////////////////////////////
// set measurement
//////////////////////////////////////////////////////////////////////////////
$(document).ready(function(){
	$('.measurements_define').on('click','#measurements_submit',function(){
		
		// cycle through all signals
		$( "#measurements_define" ).children().each(function(){
			// get the signal id
			id = $(this).attr('data-id');
			
			$(this).children.each({function(){
				// get the column tot add value to
				column = $(this).attr('data-column');
				value = $(this).val();
				
				// post id column and value to add to database
				$.post( 'requests/measurements_set.php', {'id': id , 'column': column , 'value': value}); 
				
				//for debugging: 
				//$.post( 'requests/alarm_set.php', {'id': id , 'column': column , 'value': value}, function(response){alert(response);}); 
			});
		});				
	});
});

//////////////////////////////////////////////////////////////////////////////
// initialize measurements
//////////////////////////////////////////////////////////////////////////////
$(document).on('pagebeforecreate',function(){

	//cycle through all signal_placeholder
	$( ".signal_placeholder" ).each(function(){
		
		// create variables
		var values = {
			id: $(this).attr('data-id'),
			item: $(this).attr('data-hour'),
			name: $(this).attr('data-minute'),
			quantity: $(this).attr('data-mon'),
			unit: $(this).attr('data-tue'),
			description: $(this).attr('data-wed'),
		};
		
		//creat the alarm and display
		newSignal= display_signal(values);
		$(this).replaceWith(newSignal);
		
	});
});

//////////////////////////////////////////////////////////////////////////////
// display signal code
//////////////////////////////////////////////////////////////////////////////
display_signal = function(values){

	var id = values['id'];
	
	// duplicate template and change what needs to be changed
	var newSignal = $('#signal_template').clone();
	newSignal.attr('id','signal'+id); 
	newSignal.attr('data-id',id);
	
	
	
	newSignal.find('#id_id').val(id);
	newSignal.find('#id_id').attr('id','signal'+id+'_id');
	
	newSignal.find('#id_item').val(values['item']);
	newSignal.find('#id_item').attr('id','signal'+id+'_item');

	newSignal.find('#id_name').val(values['name']);
	newSignal.find('#id_name').attr('id','signal'+id+'_name');

	newSignal.find('#id_quantity').val(values['quantity']);
	newSignal.find('#id_quantity').attr('id','signal'+id+'_quantity');	
	
	newSignal.find('#id_unit').val(values['unit']);
	newSignal.find('#id_unit').attr('id','signal'+id+'_unit');
	
	newSignal.find('#id_dectription').val(values['dectription']);
	newSignal.find('#id_dectription').attr('id','signal'+id+'_dectription');
	
	newSignal.show();
	return newSignal;

};