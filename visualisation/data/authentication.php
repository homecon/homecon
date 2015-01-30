<?php
	include("data/mysql.php");
	$_SESSION['user_id'] = 0;
	$incorrect = 0;
	
	// check if the user machine has the required cookie
	if(array_key_exists('knxcontrol_user',$_COOKIE) && array_key_exists('knxcontrol_pass',$_COOKIE)){
		$result = mysql_query("SELECT * FROM users WHERE username = '".$_COOKIE['knxcontrol_user']."'");
		if($user = mysql_fetch_array($result)){
			if(md5($_COOKIE['knxcontrol_pass'])==$user['password']){
				$_SESSION['user_id'] = $user['id'];
				
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
				$incorrect = 0;
			}
		}
	}
	
	if($_SESSION['user_id']>0){
		echo "
		<script>
			$(document).trigger('connect',".$user['id'].");
		</script>";
	}
?>	