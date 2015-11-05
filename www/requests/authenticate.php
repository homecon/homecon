<?php
	include_once('../requests/mysql.php');
	include_once('../requests/hashfunctions.php');
	
	$status = 0;
	$token = '';
	
	// check if a valid token is sent in the header, if so renew the token
	$result = jwt_decode(getallheaders()['Authentication']);
	if( $result['status'] == 1 ){
	
		$payload = $result['payload'];
		$token = generate_token($payload['id'],$payload['username'],$payload['permission']);
		$status = 1;
		
	}
	elseif( isset($_POST['username']) && isset($_POST['password']) ){
		// try authentication via the login form
		$username = $_POST['username'];
		
		// select the user from the table
		$query = "SELECT * FROM users WHERE username='$username'";
		$result = mysql_query($query) or die('Error: ' . mysql_error());

		if( mysql_num_rows($result) > 0 ){
			$dbuser = mysql_fetch_array($result);
			
			// verify the user password
			if( create_hash($_POST['password'])==$dbuser['password'] ){
				
				// generate a token
				$token = generate_token($dbuser['id'],$dbuser['username'],$dbuser['permission']);
				$status = 1;
			}
			else{
				$status = -2;
			}
		}
		else{
			// user does not exist
			$status = -1;
		}
	}

	// return the status and token to the user
	echo json_encode( array('status' => $status, 'token' => $token) );
	
	// generate a token	
	function generate_token($id,$username,$permission){

		$payload = array('id' => $id, 'username' => $username, 'permission' => $permission, 'exp' => time()+365*24*3600);

		return jwt_encode($payload);
	}


/*
	include("mysql.php");
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
				$(document).trigger('authenticated',".$user['id'].");
			});
		</script>";
	}
*/
?>
