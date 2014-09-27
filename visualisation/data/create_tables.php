<?php
// connect to the database
if (!mysql_connect("localhost","root","admin")) {
  die('Could not connect: ' . mysql_error());
}
mysql_select_db("knxcontrol");

	
for($id=1;$id<=17;$id++){
	echo $id;
	//mysql_query("CREATE TABLE measurements_signal".$id." (id INT AUTO_INCREMENT PRIMARY KEY, time TIMESTAMP, value FLOAT)");
	
	mysql_query("DROP TABLE measurements_signal".$id."_week");
	//mysql_query("CREATE TABLE measurements_signal".$id."_week (id INT AUTO_INCREMENT PRIMARY KEY, starttime TIMESTAMP, endtime TIMESTAMP, value FLOAT)");
}

?>