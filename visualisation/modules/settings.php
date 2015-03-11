<?php

if(array_key_exists('exec',$_GET)){

	if($_GET['exec'] == 'restart_smarthome'){
		shell_exec('/etc/init.d/smarthome restart');
	}
	if($_GET['exec'] == 'restart_eibd'){
		shell_exec('/etc/init.d/eibd restart');
	}
	if($_GET['exec'] == 'clear_log'){
		shell_exec('cat /dev/null > /usr/local/knxcontrol/smarthome/var/log/smarthome.log');
	}	
	echo "<meta http-equiv='refresh' content='1; URL=index.php?page=modules/settings'>";
}

// get data from mysql
$result = mysql_query("SELECT * FROM data WHERE id=1");
$row = mysql_fetch_array($result);
$ip = $row['ip'];
$port = $row['port'];
$webip = $row['web_ip'];
$webport = $row['web_port'];
$token = $row['token'];

// echo page

echo "
		<article class=$page_class>
			<header><img src='icons/ffffff/edit_settings.png'><h1>Settings</h1></header>

			<section data-role='collapsible' data-theme='c' data-content-theme='a' data-collapsed='false'>
				<h1>General</h1>
				<div class='general_settings'>
					<div data-role='fieldcontain'>
						<label for='ip'>IP:</label>
						<input type='text' name='ip' id='ip' data-mini='true' value='$ip'>
					</div>
					<div data-role='fieldcontain'>
						<label for='port'>Port:</label>
						<input type='text' name='port' id='port' data-mini='true' value='$port'>
					</div>
					<div data-role='fieldcontain'>
						<label for='webip'>Web-IP:</label>
						<input type='text' name='webip' id='webip' data-mini='true' value='$webip'>
					</div>
					<div data-role='fieldcontain'>
						<label for='webport'>Web-Port:</label>
						<input type='text' name='webport' id='webport' data-mini='true' value='$webport'>
					</div>
					<div data-role='fieldcontain'>
						<label for='token'>Token:</label>
						<input type='text' name='token' id='token' data-mini='true' value='$token'>
					</div>
					<a data-role='button'>Save settings</a>
					<script>
						$(document).on('click','.general_settings a',function(){
						
							$.post('requests/settings_set.php',{'ip': $('#ip').val(), 'port': $('#port').val(), 'webip': $('#webip').val(), 'webport': $('#webport').val(), 'token': $('#token').val()});
						});
					</script>
				</div>
			</section>

			<section data-role='collapsible' data-theme='c' data-content-theme='a' data-collapsed='true'>
				<h1>Restart</h1>
				<div>

					<a href='index.php?page=modules/settings&exec=restart_smarthome' data-role='button'>Restart SmartHome.py</a>
					
				</div>
			</section>
			<section data-role='collapsible' data-theme='c' data-content-theme='a' data-collapsed='true'>
				<h1>SmartHome.py log</h1>
				<div>
					<a href='data/smarthome.log' target='_blank' data-role='button'>Download log file</a>
					<a href='index.php?page=modules/settings&exec=clear_log' data-role='button'>Clear log file</a>
					<font size='2'>";
					echo nl2br( file_get_contents('data/smarthome.log') );
					
echo "		
					</font>
				</div>
			</section>
		</article>
";
?>