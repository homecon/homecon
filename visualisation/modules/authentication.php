





		<div id='authentication' data-role='page' data-theme='b'>
			<div class='content' data-role='content'>

			
			
			
			
			
			
<?php
	if($_GET['login']==1){
	
		$result = mysql_query("SELECT * FROM users WHERE username = '".$_POST['username']."'");
		if($user = mysql_fetch_array($result)){
			if(md5(md5($_POST['password']))==$user['password']){
			
				setcookie("knxcontrol_user", $_POST['username'], time()+3600*24*365*10);
				setcookie("knxcontrol_pass", md5($_POST['password']), time()+3600*24*365*10);
				
				$_SESSION['userid'] = $user['id'];
				
				echo "<meta http-equiv='refresh' content='0; URL=index.php'>";
			}
			else{
				echo "<header><section><h1>Verkeerd wachtwoord</h1></section></header>";
			}
		}
		else{
			echo "<header><section><h1>Usernaam bestaat niet</h1></section></header>";
		}
	}
	elseif($_GET['login']==0){
		echo "test";
	
		unset($_COOKIE['knxcontrol_user']);
		setcookie('knxcontrol_user', "", time()-3600);
		unset($_COOKIE['knxcontrol_pass']);
		setcookie('knxcontrol_pass', "", time()-3600);
		
		$_SESSION['userid'] = 0;
		echo "<meta http-equiv='refresh' content='0; URL=index.php?web=$web'>";
	}
	

?>