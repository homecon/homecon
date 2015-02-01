//
// 
// widget.js is part of KNXControl
// @author: Brecht Baeten
// @license: GNU GENERAL PUBLIC LICENSE
// 
//

/*****************************************************************************/
/*                     Main event handlers                                   */
/*****************************************************************************/
// initialize
$(document).on('connect',function(event,user_id){
	knxcontrol.user_id = user_id;
	
	if(!smarthome.socket){
		//get connection data
		$.post('requests/select_from_table.php',{table: 'data', column: '*', where: 'id=1'},function(result){
			data = JSON.parse(result);
			data = data[0];
			
			// initialize connection
			smarthome.init(data['ip'],data['port'],data['token']);
			

		});
	};
});


			

/*****************************************************************************/
/*                     KNXControl data                                       */
/*****************************************************************************/

var knxcontrol = {
	user_id: 0,
	location:	{
		latitude: 0,
		longitude: 0
	},
	item: new Object(),

// initialize
	init: function(){
		knxcontrol.get_items();
		
		// request the values from smarthome.py
		smarthome.monitor();
	},
// gets items from all widgets in the dom
	get_items: function(){
		$('[data-item]').each(function(index){
			var item = $(this).attr('data-item');
			knxcontrol.item[item] = 0;
		});
	},	
// update an item with a certain value
	update: function(item,value){
		// set the item value
		knxcontrol.item[item] = value;
		
		// write the new value of the item to smarthome.py
		smarthome.write(item, knxcontrol.item[item]);

		// trigger a widget update event
		$('[data-item="'+item+'"]').trigger('update');
	}
}