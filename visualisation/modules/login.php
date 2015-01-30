		<div id='authentication' data-role='page' data-theme='b'>
			<div class='content' data-role='content'>
				<h1>Login</h1>
				<?php if($incorrect){ echo "<h3>Usernaam of paswoord niet correct</h3>";} ?>
				<section data-role='collapsible' data-theme='a' data-content-theme='b' data-collapsed='false'>
					<h1>Couple device</h1>
					<form action='index.php' method='post' name='login' class='login'>
						<div data-role='fieldcontain' class='ui-hide-label'>
							<label for='username'>Usernaam:</label>
							<input type='text' id='username' name='username' placeholder='Usernaam'>
						</div>
						<div data-role='fieldcontain' class='ui-hide-label'>
							<label for='password'>Paswoord:</label>
							<input type='password' id='password' name='password' placeholder='Paswoord'>
						</div>
						<div data-role='fieldcontain' class='ui-hide-label'>
							<label for='login'>Login:</label>
							<input type='submit' value='Login' name='login' id='login'>
						</div>
					</form>
				</section>
			</div>
		</div>