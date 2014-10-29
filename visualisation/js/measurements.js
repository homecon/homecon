//////////////////////////////////////////////////////////////////////////////
// set measurement
//////////////////////////////////////////////////////////////////////////////
$(document).ready(function(){
	$('.measurements_define').on('click','#measurements_submit',function(){
		// display please wait
		$('#measurements_submit_popup').popup('open');
		
		// cycle through all fields
		$('#measurements_define :input').each(function(){
			//if the field has column id do nothing else
			if($(this).attr('data-column')!='id' && $(this).parents().filter('.signal').attr('id')!='signal_template'){
				id = $(this).parents().filter('.signal').attr('data-id');
				column = $(this).attr('data-column');
				value = $(this).attr('value')
				
				$.post( 'requests/table_set.php', {'table':'measurements_legend' , 'id': id , 'column': column , 'value': value}); 
			}
		
		});
		
		// hide
		setTimeout(function(){
			$('#measurements_submit_popup').popup('close');
		}, 5000);
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
			item: $(this).attr('data-item'),
			name: $(this).attr('data-name'),
			quantity: $(this).attr('data-quantity'),
			unit: $(this).attr('data-unit'),
			description: $(this).attr('data-description'),
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
	
	
	
	newSignal.find('#id_id').attr('value',id);
	newSignal.find('#id_id').attr('id','signal'+id+'_id');
	
	newSignal.find('#id_item').attr('value',values['item']);
	newSignal.find('#id_item').attr('id','signal'+id+'_item');

	newSignal.find('#id_name').attr('value',values['name']);
	newSignal.find('#id_name').attr('id','signal'+id+'_name');

	newSignal.find('#id_quantity').attr('value',values['quantity']);
	newSignal.find('#id_quantity').attr('id','signal'+id+'_quantity');	
	
	newSignal.find('#id_unit').attr('value',values['unit']);
	newSignal.find('#id_unit').attr('id','signal'+id+'_unit');
	
	newSignal.find('#id_description').attr('value',values['description']);
	newSignal.find('#id_description').attr('id','signal'+id+'_description');
	
	newSignal.show();
	return newSignal;

};