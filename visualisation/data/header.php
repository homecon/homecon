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

		<div id='header' data-role='header' data-position='fixed' data-tap-toggle='false' data-theme='b'>
			<nav>
				<a href='index.php' data-ajax='false' id='home'><img src='icons/ffffff/knxcontrol_home.png'></a>
				<a href='#' id='menu_button'><img src='icons/ffffff/control_bars.png'></a>
				<div class='home'>
					<a class='hide' href='#home_users'><img src='icons/ffffff/knxcontrol_users.png'></a>
					<a class='hide' href='#home_alarms'><img src='icons/ffffff/knxcontrol_alarm.png'></a>
					<a class='hide' href='#home_measurements'><img src='icons/ffffff/measure_power_meter.png'></a>
					<a class='hide' href='#home_settings'><img src='icons/ffffff/knxcontrol_gears.png'></a>
					<a class='hide' href='#home_pagebuilder'><img src='icons/ffffff/pagebuilder_pagebuilder.png'></a>
					<a href='index.php?logout=1' data-ajax='false'><img src='icons/ffffff/knxcontrol_logout.png'></a>
				</div>	
				<div class='pagebuilder'>
					<a class='publish' href='#'><img src='icons/ffffff/pagebuilder_publish.png'></a>
					<input type='file' id='pagebuilder_import'/>
					<a class='import' href='#'><img src='icons/ffffff/pagebuilder_open.png'></a>
					<a class='export' href='#'><img src='icons/ffffff/pagebuilder_export.png'></a>
				</div>
			</nav>
		</div>