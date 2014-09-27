<?php

if(array_key_exists('exec',$_GET)){

	if($_GET['exec'] == 'restart_smarthome'){
		shell_exec('cat /dev/null > /usr/smarthome/var/log/smarthome.log');
		shell_exec('/etc/init.d/smarthome.py restart');
	}
	if($_GET['exec'] == 'restart_eibd'){
		shell_exec('/etc/init.d/eibd restart');
	}	
	echo "<meta http-equiv='refresh' content='1; URL=index.php?page=modules/settings'>";
}



echo "
		<article class=$page_class>
			<header><img src='icons/ws/edit_settings.png'><h1>Settings</h1></header>
			
			<section data-role='collapsible' data-theme='c' data-content-theme='a' data-collapsed='false'>
				<h1>Algemeen</h1>
				<div>

					<a href='index.php?page=modules/settings&exec=restart_smarthome' data-role='button'>Restart SmartHome.py</a>
					<a href='index.php?page=modules/settings&exec=restart_eibd' data-role='button'>Restart eibd</a>
					
				
";			
			
echo "
				</div>
			</section>
			<section data-role='collapsible' data-theme='c' data-content-theme='a'>
				<h1>SmartHome.py log</h1>
				<div>
					<a href='data/smarthome.log' target='_blank' data-role='button'>download log file</a>
					<font size='2'>";
					echo nl2br( file_get_contents('data/smarthome.log') );
					
echo "		
					</font>
				</div>
			</section>
		</article>
";
?>