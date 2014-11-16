<?php
	$message = '';
	if(array_key_exists('login',$_GET)){
		if($_GET['login']==1){
		
			$result = mysql_query("SELECT * FROM users WHERE username = '".$_POST['username']."'");
			if($user = mysql_fetch_array($result)){
				if(md5(md5($_POST['password']))==$user['password']){
				
					setcookie("knxcontrol_user", $_POST['username'], time()+3600*24*365*10);
					setcookie("knxcontrol_pass", md5($_POST['password']), time()+3600*24*365*10);
					
					$_SESSION['userid'] = $user['id'];
					
					//$message = "<meta http-equiv='refresh' content='0; URL=index.php?web=$web'>";
				}
				else{
					$message = "<header><h1>Wrong password</h1></header>";
				}
			}
			else{
				$message = "<header><h1>Username does not exist</h1></header>";
			}
		}
		elseif($_GET['login']==0){
			echo "test";
		
			unset($_COOKIE['knxcontrol_user']);
			setcookie('knxcontrol_user', "", time()-3600);
			unset($_COOKIE['knxcontrol_pass']);
			setcookie('knxcontrol_pass', "", time()-3600);
			
			$_SESSION['userid'] = 0;
			//$message = "<meta http-equiv='refresh' content='0; URL=index.php?web=$web'>";
		}
	}
	echo "
<!DOCTYPE html>
<html>
	<head>
		<title>KNX control</title>
		
		<link rel='icon' href='favicon.png'/>
		<link rel='apple-touch-icon' href='favicon.png' />
		<link rel='icon' href='favicon.ico' type='image/x-icon' />

		<!-- jquery mobile -->
		<script src='jquery/jquery-1.8.3.js'></script>
		<script src='jquery/jquery.mobile-1.3.2.js'></script>
		<link rel='stylesheet' href='jquery/jquery.mobile-1.3.2.css'>
		
		<!-- knxcontrol -->
		<link rel='stylesheet' type='text/css' href='css/layout.css'/>
		
	</head>
	<body>
		<div id='page' data-role='page' data-theme='a'>
			<div data-role='content' id='content'>
				<article class='main'>
					$message
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
				</article>
			</div>
		</div>
	</body>
</html>";
?>