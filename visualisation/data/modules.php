<!--
    Copyright 2015 Brecht Baeten
    This file is part of KNXControl.

    KNXControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    KNXControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
-->

		<div id='home_users' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ffffff/knxcontrol_users.png'>
					<h1>Users</h1>
				</header>
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Profile</h1>
					<div data-role='user_profile'></div>
				</section>
				<?php if($_SESSION['user_id']==1){ ?>
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Users</h1>
					<div data-role='user_list'></div>
				</section>
				<?php } ?>
			</div>
		</div>
		
		
		<div id='home_alarms' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ffffff/control_alarm.png'>
					<h1>Alarms</h1>
				</header>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Actions</h1>
					<div data-role='action_list'></div>
				</section>
				
			</div>
		</div>
		
		
		<div id='home_measurements' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ffffff/measure_power_meter.png'>
					<h1>Measurements</h1>
				</header>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>List</h1>
					<div data-role='measurement_list'></div>
				</section>
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Export</h1>
					<div data-role='measurement_export'></div>
				</section>
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Profiles</h1>
					<div data-role='profile_list'></div>
				</section>
			</div>
		</div>
		
		
		<div id='home_settings' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ffffff/edit_settings.png'>
					<h1>Settings</h1>
				</header>
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>General</h1>
					<div data-role='settings'></div>
				</section>
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Smarthome log</h1>
					<div data-role='smarthome_log'></div>
				</section>
			</div>
		</div>
		

		<div id='home_pagebuilder' data-role='page' data-theme='b'>
			<div id='renderpage' data-role='content'>
			</div>
			
			<div id='section_def_popup' class='ui-content def' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
				<div class='options'>
					<input type='text' data-field='name' placeholder='name'>
					<input type='text' data-field='init' placeholder='initially open'>
				</div>
				<div class='move'>
					<a class='move_up' data-role='button' data-icon="arrow-u" data-iconpos="notext">Move up</a>
					<a class='move_down' data-role='button' data-icon="arrow-d" data-iconpos="notext">Move down</a>
				</div>
				<a class='save' data-role='button'>Save</a>
				<a class='delete' data-role='button'>Delete</a>
				<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
			</div>
			<div id='page_def_popup' class='ui-content def' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
				<div class='options'>
					<input type='text' data-field='name' placeholder='name'>
					<input type='text' data-field='measurement_item' placeholder='measurement_item'>
					<select data-field='img'></select>
				</div>
				<div class='move'>
					<a class='move_up' data-role='button' data-icon="arrow-u" data-iconpos="notext">Move up</a>
					<a class='move_down' data-role='button' data-icon="arrow-d" data-iconpos="notext">Move down</a>
				</div>
				<a class='save' data-role='button'>Save</a>
				<a class='delete' data-role='button'data-section_id='1'>Delete</a>
				<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
			</div>
			<div id='page_section_def_popup' class='ui-content def' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
				<div class='options'>
					<input type='text' data-field='name' placeholder='name'>
					<select data-field='type'><option value=''>Invisible</option><option value='collapsible'>Collapsible</option><option value='collapsed'>Collapsed</option></select>
				</div>
				<div class='move'>
					<a class='move_up' data-role='button' data-icon="arrow-u" data-iconpos="notext">Move up</a>
					<a class='move_down' data-role='button' data-icon="arrow-d" data-iconpos="notext">Move down</a>
				</div>
				<a class='save' data-role='button'>Save</a>
				<a class='delete' data-role='button'data-section_id='1'>Delete</a>
				<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
			</div>
			<div id='widget_def_popup' class='ui-content def' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
				<div class='options'>
				</div>
				<div class='move'>
					<a class='move_up' data-role='button' data-icon="arrow-u" data-iconpos="notext">Move up</a>
					<a class='move_down' data-role='button' data-icon="arrow-d" data-iconpos="notext">Move down</a>
				</div>
				<a class='save' data-role='button' data-mini='true'>Save</a>
				<a class='delete' data-role='button' data-mini='true' data-section_id='1'>Delete</a>
				<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
			</div>
		</div>
		
		
		<div id='action_def_popup' class='ui-content' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
			<div class='labeledfield'>
				<div class='label'>Name:</div>
				<input type='text' data-field='name'>
			</div>	
			<div class='labeledfield'>
				<div class='label'>Section filter:</div>
				<input type='text' data-field='section_id'>
			</div>	
			
			<div class='ui-grid-b action_def_list'>
				<div class='ui-block-a'>
					Delay:
				</div>
				<div class='ui-block-b'>
					Items:
				</div>
				<div class='ui-block-c'>
					Value:
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay1' value='0'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item1'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value1'>
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay2'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item2'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value2'>
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay3'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item3'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value3'>
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay4'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item4'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value4'>
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay5'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item5'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value5'>
				</div>
			</div>
			<a id='action_def_popup_save' data-role='button' data-id='1'>Save</a>
			<a id='action_def_popup_delete' data-role='button' data-id='1'>Delete</a>
			<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
		</div>
		
		
		<div id='measurement_def_popup' class='ui-content' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
			<div class='labeledfield'>
				<div class='label'>Name:</div>
				<input type='text' data-field='name'/>
			</div>	
			<div class='labeledfield'>
				<div class='label'>Item:</div>
				<input type='text' data-field='item'/>
			</div>
			<div class='labeledfield'>
				<div class='label'>Quantity:</div>
				<input type='text' data-field='quantity'/>
			</div>	
			<div class='labeledfield'>
				<div class='label'>Unit:</div>
				<input type='text' data-field='unit'/>
			</div>
			<div class='labeledfield'>
				<div class='label'>Description:</div>
				<input type='text' data-field='description'/>
			</div>
			<a id='measurement_def_popup_save' data-role='button' data-id='1'>Save</a>
			<a id='measurement_def_popup_delete' data-role='button' data-id='1'>Delete</a>
			<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
		</div>
		
		
		<div id='user_def_popup' class='ui-content' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
			<div class='labeledfield'>
				<div class='label'>Name:</div>
				<input type='text' data-field='name'/>
			</div>
			<a id='user_def_popup_save' data-role='button' data-id='1'>Save</a>
			<a id='user_def_popup_reset' data-role='button' data-id='1'>Reset password</a>
			<a id='user_def_popup_delete' data-role='button' data-id='1'>Delete</a>
			<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
		</div>
		
		
		<div id='password_def_popup' class='ui-content' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
			<div class='labeledfield'>
				<div class='label'>Name:</div>
				<input type='text' data-field='name'/>
			</div>
			<div class='labeledfield'>
				<div class='label'>Password:</div>
				<input type='password' data-field='pass'/>
			</div>
			<div class='labeledfield'>
				<div class='label'>Repeat password:</div>
				<input type='password' id='measurement_def_popup_pass2' data-field='pass2'/>
			</div>
			<a id='password_def_popup_save' data-role='button' data-id='1'>Save</a>
			<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
		</div>
		
		
		<div id='profile_def_popup' class='ui-content' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
			<div class='labeledfield'>
				<div class='label'>Name:</div>
				<input type='text' id='action_def_popup_name' data-field='name'>
			</div>	
			<div class='labeledfield'>
				<div class='label'>Quantity:</div>
				<input type='text' id='action_def_popup_quantity' data-field='quantity'>
			</div>
			<div class='labeledfield'>
				<div class='label'>Unit:</div>
				<input type='text' id='action_def_popup_unit' data-field='unit'>
			</div>	
			<div class='labeledfield'>
				<div class='label'>Description:</div>
				<input type='text' id='action_def_popup_description' data-field='description'>
			</div>	
			<div class='ui-grid-a profile_def_list'>
				<div class='ui-block-a'>
					Time:
				</div>
				<div class='ui-block-b'>
					Value:
				</div>
			</div>
			<a id='profile_def_popup_addrow' data-role='button'>Add row</a>
			<a id='profile_def_popup_save' data-role='button' data-id='1'>Save</a>
			<a id='profile_def_popup_delete' data-role='button' data-id='1'>Delete</a>
			<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
		</div>
		
		
		<div id='message_popup' class='ui-content' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
		</div>