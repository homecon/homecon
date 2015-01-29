<?php
	$_SESSION['user_id'] = 0;
	$show_form = 1;
	$incorrect = 0;
	
	// check if the user machine has the required cookie
	if(array_key_exists('knxcontrol_user',$_COOKIE) && array_key_exists('knxcontrol_pass',$_COOKIE)){
		$result = mysql_query("SELECT * FROM users WHERE username = '".$_COOKIE['knxcontrol_user']."'");
		if($user = mysql_fetch_array($result)){
			if(md5($_COOKIE['knxcontrol_pass'])==$user['password']){
				$_SESSION['user_id'] = $user['id'];
				$show_form = 0;
				
				echo "<script>model.user.id = ".$user['id']."</script>";
			}
		}
	}
	// check if a login request was sent
	elseif(array_key_exists('username',$_POST)){
		$incorrect = 1;
		$result = mysql_query("SELECT * FROM users WHERE username = '".$_POST['username']."'");
		// check if the user exists
		if($user = mysql_fetch_array($result)){
			// check if the password is correct
			if(md5(md5($_POST['password']))==$user['password']){
			
				setcookie("knxcontrol_user", $_POST['username'], time()+3600*24*365*10);
				setcookie("knxcontrol_pass", md5($_POST['password']), time()+3600*24*365*10);
				
				$_SESSION['user_id'] = $user['id'];
				$show_form = 0;
?>		
		<div id='authentication' data-role='page' data-theme='b'>
			<div class='content' data-role='content'>
				<h1>Login successful</h1>
				<meta http-equiv='refresh' content='1; URL=index.php'>
			</div>
		</div>
<?php
			}
		}
	}
	
	if($show_form){
		// display the login form
?>	
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
<?php	

	}
	
?>