<?php
// connect to the database
include('./pages/mysql.php');
	
for($id=1;$id<=17;$id++){
	echo $id;
	//mysql_query("CREATE TABLE measurements_signal".$id." (id INT AUTO_INCREMENT PRIMARY KEY, time TIMESTAMP, value FLOAT)");
	
	mysql_query("DROP TABLE measurements_signal".$id."_week");
	//mysql_query("CREATE TABLE measurements_signal".$id."_week (id INT AUTO_INCREMENT PRIMARY KEY, starttime TIMESTAMP, endtime TIMESTAMP, value FLOAT)");
}

?>