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

		<div id='authentication' data-role='page' data-theme='b'>
			<div class='content' data-role='content'>
				<h1>Login</h1>
				<?php if($incorrect){ echo "<h3>Usernaam of paswoord niet correct</h3>";} ?>
				<section data-role='collapsible' data-theme='a' data-content-theme='b' data-collapsed='false'>
					<h1>Couple device</h1>
					<form action='index.php' method='post' data-ajax='false' name='login' class='login'>
						<div class='ui-field-contain ui-hide-label'>
							<label for='username'>Usernaam:</label>
							<input type='text' id='username' name='username' placeholder='Usernaam'>
						</div>
						<div class='ui-field-contain ui-hide-label'>
							<label for='password'>Paswoord:</label>
							<input type='password' id='password' name='password' placeholder='Paswoord'>
						</div>
						<div class='ui-field-contain ui-hide-label'>
							<label for='login'>Login:</label>
							<input type='submit' value='Login' name='login' id='login'>
						</div>
					</form>
				</section>
			</div>
		</div>