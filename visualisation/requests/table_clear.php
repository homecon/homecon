<?php

include('../data/mysql.php');

$table = $_POST['table'];
echo $table;

$result = mysql_query("TRUNCATE $table") or die('Error: ' . mysql_error());


?>