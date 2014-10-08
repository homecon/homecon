// declaring global functions

var function display_alarm(id,itemlist,actionlist,values){
	// function returns variable containing html code for an alarm
	
	var id = values['id'];
	
	// parse days
	var days         = ['mon','tue','wed','thu','fri','sat','sun'];
	var days_string  = ['maa','din','woe','don','vri','zat','zon'];
	var days_checked = [''   ,''   ,''   ,''   ,''   ,''   ,''];
	
	for(i=0;i<days.length;i++){
		if( values[days[i]] ){
			days_checked[i] = ' checked';
		}
	}
	
	var actions = values['action'];
	
	// parse items
	var items   = values['item'].split(',');

	//parse time
	function padtime(num) {
		var s = num+"";
		while (s.length < 2) s = "0" + s;
		return s;
	}
	var time = padtime(values['hour']) + ":" + padtime(values['minute']);
		
	
	// build html
	var alarm_html = "";
	
	alarm_html += "<div class='alarm' id='alarm"+id+"' data-id='"+id+"'>";
	alarm_html += "    <input type='time' data-column='time' id='time"+id+"' value='$str_time'>";
	alarm_html += "        <h1>$text</h1>"
	alarm_html += "        <a class='delete' href='#'><img src=icons/ws/control_x.png></a>";
	alarm_html += "        <div class='days'>";
	alarm_html += "				<div data-role='controlgroup' data-type='horizontal'>";
	
	for(i=0;i<days.length;i++){
		alarm_html += "					<input type='checkbox' data-column='"+days[i]+"' id='"+days[i]+id+"' class='custom' data-widget='basic.checkbox' data-mini='true'"+days_checked+"> <label for='"+days[i]+id+"'>"+days_string[i]+"</label>";		 
	}
	
	alarm_html += "				</div>";
	alarm_html += "			</div>";
	alarm_html += "			<div class='alarm_items'>";
	alarm_html += "				<select multiple='multiple' data-column='item' id='itemselect"+id+"' data-native-menu='false'>";
	alarm_html += "					<option>Select items</option>";
						
	for(i=0;i<itemlist.length;i++){
		itemselected = "";
		item = itemlist[i];
			
		if($.inArray(item, items)){
			itemselected =  'selected=selected';
		}	
		alarm_html += "					<option "+itemselected+" value='"+item+"'>"+item+"</option>";
	}
				
	alarm_html += "				</select>";
	alarm_html += "			</div>";
	alarm_html += "			<div class='alarm_action'>";
	alarm_html += "				<select data-column='action' id='actionselect"+id+"' data-native-menu='false'>";
	alarm_html += "					<option>Select action</option>";
						
	for(i=0;i<actionlist.length;i++){
		actionselected = "";
		action = actionlist[i];
		
		if($.inArray(action, actions))==0){
			actionselected =  'selected=selected';
		}
		alarm_html += "			<option "+actionselected+" value='"+action+"'>"+action+"</option>";
	}
				
	alarm_html += "				</select>";
	alarm_html += "			</div>";
	alarm_html += "		</div>";
	
	return alarm_html;
}
