<?php
	echo "
				<article class='main'>
					<header>
						<h1>Login</h1>
					</header>
					<section data-role='collapsible' data-theme='c' data-content-theme='a' data-collapsed='false'>
					<h1>Couple device</h1>
						<form action='index.php?web=$web&login=1' method='post' name='login' class='login'>
							
							<div data-role='fieldcontain' class='ui-hide-label'>
								<label for='username'>Usernaam:</label>
								<input type='text' name='username' id='username' placeholder='Usernaam'>
							</div>
							<div data-role='fieldcontain' class='ui-hide-label'>
								<label for='password'>Paswoord:</label>
								<input type='password' name='password' id='password' placeholder='Paswoord'>
							</div>
							<div data-role='fieldcontain' class='ui-hide-label'>
								<label for='login'>Login:</label>
								<input type='submit' value='Login' name='login' id='login'>
							</div>
						</form>
					</section>
				</article>";
?>