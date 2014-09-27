<?php

if (!mysql_connect("localhost","knxcontrol","password")) {
  die('Could not connect: ' . mysql_error());
}
mysql_select_db("knxcontrol");

?>