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
	
	// check if a logout request was sent
	if(array_key_exists('logout',$_GET)){
		unset($_COOKIE['knxcontrol_user']);
		unset($_COOKIE['knxcontrol_pass']);
		$_SESSION['user_id'] = -1;	
		setcookie('knxcontrol_user',null,-1);
		setcookie('knxcontrol_pass',null,-1);
	}
	
	if($_SESSION['user_id']>0){
		echo "
		<script>
			$(document).on('pagebeforeshow',function(){
				$(document).trigger('connect',".$user['id'].");
			});
		</script>";
	}
?>	