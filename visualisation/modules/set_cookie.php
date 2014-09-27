<?php
	if(array_key_exists('login',$_POST)){

		$result = mysql_query("SELECT * FROM users WHERE username = '".$_POST['username']."'");
		if($user = mysql_fetch_array($result)){
			if(md5(md5($_POST['password']))==$user['password']){
			
				setcookie("knxcontrol_user", $_POST['username'], time()+3600*24*365*10);
				setcookie("knxcontrol_pass", md5($_POST['password']), time()+3600*24*365*10);

				echo "<meta http-equiv='refresh' content='0; URL=index.php?web=$web'>";
			}
			else{
				echo "<h1>Verkeerd wachtwoord</h1>";
			}
		}
		else{
			echo "<h1>Usernaam bestaat niet</h1>";
		}
	}
	
	echo "
<html>
	<head>
		<title>KNX control</title>

		<meta charset='utf-8'/>
		<meta name='viewport' content='width=device-width, user-scalable=yes, initial-scale=1, maximum-scale=1.3, minimum-scale=1' />
		<meta name='apple-mobile-web-app-capable' content='yes' />
		<meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
		<meta http-equiv='expires' content='0' />
		
		<link rel='icon' href='favicon.png'/>
		<link rel='apple-touch-icon' href='favicon.png' />
		<link rel='icon' href='favicon.ico' type='image/x-icon' />

		<!-- jquery mobile  
		<script src='http://code.jquery.com/jquery-1.8.3.min.js'></script>
		<script src='http://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.js'></script>
		<link rel='stylesheet' href='http://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.css'> -->
			
	</head>	
	<body>
		<div data-role='page' data-theme='a'>
			<div data-role='content' class='content'>
				<section>
					<h1>Toestel aansluiten</h1>
					<form action='index.php?page=modules/set_cookie' method='post' name='login' class='login'>
						
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
			</div>
		</div>
	</body>
</html>";
?>