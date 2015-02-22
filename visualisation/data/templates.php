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

		<div id='templates' data-role='page' data-theme='b'>
					
			<div class='alarm ui-body-b ui-corner-all' data-id='0'>
				<input type='time' data-field='time' value='12:00'>
				<a href="#" class='delete' data-role="button" data-icon="delete" data-iconpos="notext">Delete</a>
				<h1></h1>
				<div class='days'>
					<div data-role='controlgroup' data-type='horizontal'>
						<label><input type='checkbox' data-field='mon' class='custom' data-mini='true' checked>maa</label>
						<label><input type='checkbox' data-field='tue' class='custom' data-mini='true' checked>din</label>
						<label><input type='checkbox' data-field='wed' class='custom' data-mini='true' checked>woe</label>
						<label><input type='checkbox' data-field='thu' class='custom' data-mini='true' checked>don</label>
						<label><input type='checkbox' data-field='fri' class='custom' data-mini='true' checked>vri</label>
						<label><input type='checkbox' data-field='sat' class='custom' data-mini='true'>zat</label>
						<label><input type='checkbox' data-field='sun' class='custom' data-mini='true'> zon</label>
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