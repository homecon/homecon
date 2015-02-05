


		<div id='users' data-role='page' data-theme='b'>
			<div data-role='content'>
		

			</div>
		</div>
		
		
		<div id='alarms' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ws/control_alarm.png'>
					<h1>Alarms</h1>
				</header>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Actions</h1>
					<div class='action_list'>
					
					</div>
					<a href="#action_def_popup" class="add" data-role='button' data-rel='popup'>Add action</a>
				</section>
				
			</div>
			
			<div id='action_def_popup' class='action popup ui-content' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
				<input type='text'  data-field='name'       placeholder='name'>
				<input type='text'  data-field='section_id'  placeholder='section id filter'>
				<div class='action_def_list'>
					<div>
						<input type='number'  data-field='delay1'   placeholder='delay 1' value='0'>
						<input type='text'    data-field='item1'    placeholder='item 1'>
						<input type='text'    data-field='value1'   placeholder='value 1'>
					</div>
					<div>
						<input type='number'  data-field='delay2'   placeholder='delay 2'>
						<input type='text'    data-field='item2'    placeholder='item 2'>
						<input type='text'    data-field='value2'   placeholder='value 2'>
					</div>
					<div>
						<input type='number'  data-field='delay3'   placeholder='delay 3'>
						<input type='text'    data-field='item3'    placeholder='item 3'>
						<input type='text'    data-field='value3'   placeholder='value 3'>
					</div>
					<div>
						<input type='number'  data-field='delay4'   placeholder='delay 4'>
						<input type='text'    data-field='item4'    placeholder='item 4'>
						<input type='text'    data-field='value4'   placeholder='value 4'>
					</div>
					<div>
						<input type='number'  data-field='delay5'   placeholder='delay 5'>
						<input type='text'    data-field='item5'    placeholder='item 5'>
						<input type='text'    data-field='value5'   placeholder='value 5'>
					</div>
				<div>
				<a id='action_def_save' data-role='button'>Save</a>
			</div>
		</div>