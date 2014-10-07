
$(document).ready(function(){

    $('a.alarm_action.delete').click(function(){
		// get the id of the action which needs to be deleted	
		id = $(this).parent().attr('data-id');
		
		// immediately remove the action from the table 
		$(this).parent().remove()
		
		// remove the action from the database in the background
		$.post('requests/alarm_action_remove.php', { 'id': id });

	});
	
	
	$('a.alarm_action.add').click(function(){
	
		// get the id of the last action to determine the new action id
		actionids = $(this).parent().children().filter('div').map( function(){ return $(this).attr('data-id'); }).get();
        alert(actionids);
	
		oldid = Math.max.apply(Math, actionids);
		id = oldid+1;
		alert(id);
		
		// immediately add the action to the table 
		$(this).before( "<div data-id='"+id+"'><a class='alarm_action delete' href='#'><img src=icons/ws/control_x.png></a><input type='text' name='name"+id+"'        id='name"+id+"'      value='' disabled placeholder='name'><input type='text' name='sectionid"+id+"'   id='sectionid"+id+"' value='' disabled placeholder='section id filter'><div><input type='number' name='delay1"+id+"'   id='delay1"+id+"'  value=''  placeholder='delay 1'><input type='text'   name='item1"+id+"'    id='item1"+id+"'   value=''   placeholder='item 1'><input type='text'   name='action1"+id+"'  id='action1"+id+"' value='' placeholder='action 1'></div><div><input type='number' name='delay2"+id+"'   id='delay2"+id+"'  value=''  placeholder='delay 2'><input type='text'   name='item2"+id+"'    id='item2"+id+"'   value=''   placeholder='item 2'><input type='text'   name='action2"+id+"'  id='action2"+id+"' value='' placeholder='action 2'></div><div><input type='number' name='delay3"+id+"'   id='delay3"+id+"'  value=''  placeholder='delay 3'><input type='text'   name='item3"+id+"'    id='item3"+id+"'   value=''   placeholder='item 3'><input type='text'   name='action3"+id+"'  id='action3"+id+"' value='' placeholder='action 3'></div><div><input type='number' name='delay4"+id+"'   id='delay4"+id+"'  value=''  placeholder='delay 4'><input type='text'   name='item4"+id+"'    id='item4"+id+"'   value=''   placeholder='item 4'><input type='text'   name='action4"+id+"'  id='action4"+id+"' value='' placeholder='action 4'></div><div><input type='number' name='delay5"+id+"'   id='delay5"+id+"'  value=''  placeholder='delay 5'><input type='text'   name='item5"+id+"'    id='item5"+id+"'   value=''   placeholder='item 5'><input type='text'   name='action5"+id+"'  id='action5"+id+"' value='' placeholder='action 5'></div></div>");
		
		// add new action to the database in the background
		$.post('requests/alarm_action_add.php', {'id': id });

	});
}):
