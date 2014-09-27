<?php

include('mysql.php');

$id = $_POST['id'];
$column = $_POST['column'];
$value = $_POST['value'];


echo $id."<br>";
echo $column."<br>";
echo $value."<br>";

if(strcmp($column,'time')==0){
	$list = explode(':',$value);

	$hour = intval($list[0]);
	$minute = intval($list[1]);
	
	$query = "UPDATE temperature_setpoints SET hour=$hour, minute=$minute WHERE id=$id";
	$result = mysql_query($query) or die('Error: ' . mysql_error());
}
else{
	$query = "UPDATE temperature_setpoints SET $column=$value WHERE id=$id";
	$result = mysql_query($query) or die('Error: ' . mysql_error());
}

?>