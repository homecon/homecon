//////////////////////////////////////////////////////////////////////////////
// set alarm
//////////////////////////////////////////////////////////////////////////////
$(document).ready(
	function(){
		$('.alarm input, .alarm select').change(
			function(){
				id = $( this ).parents('.alarm').attr('id');
				time = $('#'+id+' .alarm_time').val();
				
				mon = $('#'+id+' .mon').is(':checked');
				tue = $('#'+id+' .tue').is(':checked');
				wed = $('#'+id+' .wed').is(':checked');
				thu = $('#'+id+' .thu').is(':checked');
				fri = $('#'+id+' .fri').is(':checked');
				sat = $('#'+id+' .sat').is(':checked');
				sun = $('#'+id+' .sun').is(':checked');
				
				item = $('#'+id+' .alarm_item').val();
				action = $('#'+id+' .alarm_action').val();
				
				// get actual alarm id
				id = id.split('_');
				id = id[1];
				
				$.post( 'requests/alarm_set.php',
						{'id': id , 'time': time, 'mon': mon, 'tue': tue, 'wed': wed, 'thu': thu, 'fri': fri, 'sat': sat, 'sun': sun, 'item': item, 'action': action}
				); 
				
				//for debugging: 
				//$.post( 'requests/set_alarm.php',
				//        {'id': $id , 'time': time, 'mon': mon, 'tue': tue, 'wed': wed, 'thu': thu, 'fri': fri, 'sat': sat, 'sun': sun, 'item': item, 'action': action},
				//        function(response){alert(response);}
				//); 
			}
		);
	}
);

//////////////////////////////////////////////////////////////////////////////
// add alarm
//////////////////////////////////////////////////////////////////////////////
$(document).ready(
	function(){
		var helperfunction = function(id) {
			return function(result, textStatus, jqXHR) {
				$('#'+id).html(result).trigger('create');
			};
		};
	
		$('.add_alarm').click(
			function(){
				id = $( this ).parents('.alarm_container').attr('id');
				sectionid = id.split('_');
				sectionid = id[2];
				
				$.post( 'requests/alarm_add.php',
						{sectionid: id},
						helperfunction(id)
				);
			}
		);
	}
);
