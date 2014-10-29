<?php

include('../data/mysql.php');

$table = $_POST['table'];
$id = $_POST['id'];
$column = $_POST['column'];
$value = $_POST['value'];


echo $id."<br>";
echo $column."<br>";
echo $value."<br>";

$query = "UPDATE $table SET $column=$value WHERE id=$id";
$result = mysql_query($query) or die('Error: ' . mysql_error());


?>