<?php
	include_once('../requests/config.php');

	// password hashing
	function create_hash($password){
		return base64_encode(hash('sha256', $password.SALT, true));
	}
	
	// json web tokens
	function jwt_signature($header,$payload){
		return base64_encode(hash_hmac($header['alg'],base64_encode(json_encode($header)).'.'.base64_encode(json_encode($payload)),JWT_KEY));
	}
	function jwt_encode($payload){
		$header = array('alg' => 'SHA256', 'typ' => 'JWT');
		$signature =  jwt_signature($header,$payload);
		
		return base64_encode(json_encode($header)).'.'.base64_encode(json_encode($payload)).'.'.$signature;
	}
	function jwt_decode($token){
		$result = array('status' => -1, 'payload' =>array());
		if($token != ''){
			$parts = explode('.',$token);
			$header = json_decode(base64_decode($parts[0]),true);
			$payload = json_decode(base64_decode($parts[1]),true);
			$signature = $parts[2];
		
			// verify the signature
			if($signature == jwt_signature($header,$payload)){
				$result = array('status' => 1, 'payload' =>$payload);
			}
		}
		return $result;
	}

	
?>
