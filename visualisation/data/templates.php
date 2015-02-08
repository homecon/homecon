

		<div id='templates' data-role='page' data-theme='b'>
					
			<div class='alarm ui-body-b ui-corner-all' data-id='0'>
				<input type='time' data-field='time' value='12:00'>
				<a href="#" class='delete' data-role="button" data-icon="delete" data-iconpos="notext">Delete</a>
				<h1></h1>
				<div class='days'>
					<div data-role='controlgroup' data-type='horizontal'>
						<input type='checkbox' data-field='mon' id='mon_0' class='custom' data-mini='true' checked> <label for='mon_0'>maa</label>
						<input type='checkbox' data-field='tue' id='tue_0' class='custom' data-mini='true' checked> <label for='tue_0'>din</label>
						<input type='checkbox' data-field='wed' id='wed_0' class='custom' data-mini='true' checked> <label for='wed_0'>woe</label>
						<input type='checkbox' data-field='thu' id='thu_0' class='custom' data-mini='true' checked> <label for='thu_0'>don</label>
						<input type='checkbox' data-field='fri' id='fri_0' class='custom' data-mini='true' checked> <label for='fri_0'>vri</label>
						<input type='checkbox' data-field='sat' id='sat_0' class='custom' data-mini='true'> <label id='id_sat_lab' for='sat_0'>zat</label>
						<input type='checkbox' data-field='sun' id='sun_0' class='custom' data-mini='true'> <label id='id_sun_lab' for='sun_0'>zon</label>
					</div>
				</div>
				<div class='alarm_action'>
					<select data-field='action_id' data-native-menu='false'>
						<option class='action_select' value='0' data-id='0'>Select action</option>
					</select>
				</div>
			</div>
			
			
			<div class='action' data-id='0'>
				<div data-field='name'></div>
				<a href="#action_def_popup" class='edit' data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext">Edit</a>
				<a href="#" class='delete' data-role="button" data-icon="delete" data-iconpos="notext">Delete</a>
			</div>
			
			<div class='measurement' data-id='0'>
				<div class='id' data-field='id'></div>
				<div class='name' data-field='name'></div>
				<a href="#measurement_def_popup" class='edit' data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext">Edit</a>
			</div>
			
			
		<div>