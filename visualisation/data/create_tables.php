<!--
    Copyright 2015 Brecht Baeten
    This file is part of KNXControl.

    KNXControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    KNXControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
-->

<?php
// connect to the database
include('../data/mysql.php');
	
//mysql_query("DROP TABLE measurements_signal".$id."_week");

// users
$res = mysql_query("CREATE TABLE IF NOT EXISTS `users` (`id` int(11) NOT NULL AUTO_INCREMENT,
														`username` varchar(255) NOT NULL,
														`password` varchar(255) NOT NULL,
														PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1");
if($res){
	echo "users table created <br>";
}
else{
	echo "users table creation failed <br>";
}

// add default user
$res = mysql_query("INSERT INTO `users` (id,username,password) VALUES (1,'admin','".md5(md5('admin'))."')");
if($res){
	echo "default user added <br>";
}
											  
												  
// data
$res = mysql_query("CREATE TABLE IF NOT EXISTS `data` (	`id` int(11) NOT NULL AUTO_INCREMENT,
														`ip` varchar(255) NOT NULL,
														`port` varchar(255) NOT NULL,
														`web_ip` varchar(255) NOT NULL,
														`web_port` varchar(255) NOT NULL,
														`token` varchar(255) NOT NULL,
														`latitude` float NOT NULL,
														`longitude` float NOT NULL,
														`elevation` float NOT NULL,
														PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1");
if($res){
	echo "data table created<br>";
}
else{
	echo "data table creation failed <br>";
}

// add default data
$res = mysql_query("INSERT INTO `data` (id,ip,port,web_ip,web_port,token,latitude,longitude,elevation) VALUES (1,'192.168.1.2','2424','mydomain.ddns.net','9024','admin',51,5,70)");												
if($res){
	echo "default data added<br>";
}
								
// alarms
$res = mysql_query("CREATE TABLE IF NOT EXISTS `alarms` (	`id` int(11) NOT NULL AUTO_INCREMENT,
															`sectionid` int(11) NOT NULL DEFAULT '1',
															`active` tinyint(4) NOT NULL DEFAULT '1',
															`item` varchar(255) DEFAULT NULL,
															`action` varchar(255) DEFAULT NULL,
															`action_id` int(11) DEFAULT NULL,
															`hour` tinyint(4) NOT NULL DEFAULT '12',
															`minute` tinyint(4) NOT NULL DEFAULT '0',
															`sunrise` tinyint(4) NOT NULL DEFAULT '0',
															`sunset` tinyint(4) NOT NULL DEFAULT '0',
															`mon` tinyint(4) NOT NULL DEFAULT '1',
															`tue` tinyint(4) NOT NULL DEFAULT '1',
															`wed` tinyint(4) NOT NULL DEFAULT '1',
															`thu` tinyint(4) NOT NULL DEFAULT '1',
															`fri` tinyint(4) NOT NULL DEFAULT '1',
															`sat` tinyint(4) NOT NULL DEFAULT '0',
															`sun` tinyint(4) NOT NULL DEFAULT '0',
															PRIMARY KEY (`id`) ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1");
if($res){
	echo "alarms table created<br>";
}
else{
	echo "alarms table creation failed <br>";
}
												   
$res = mysql_query("CREATE TABLE IF NOT EXISTS `alarm_actions` (`id` int(11) NOT NULL AUTO_INCREMENT,
																`name` varchar(255) DEFAULT NULL,
																`sectionid` varchar(255) DEFAULT NULL,
																`delay1` int(11) DEFAULT NULL,
																`item1` varchar(255) DEFAULT NULL,
																`value1` varchar(255) DEFAULT NULL,
																`delay2` int(11) DEFAULT NULL,
																`item2` varchar(255) DEFAULT NULL,
																`value2` varchar(255) DEFAULT NULL,	
																`delay3` int(11) DEFAULT NULL,
																`item3` varchar(255) DEFAULT NULL,
																`value3` varchar(255) DEFAULT NULL,	
																`delay4` int(11) DEFAULT NULL,
																`item4` varchar(255) DEFAULT NULL,
																`value4` varchar(255) DEFAULT NULL,	
																`delay5` int(11) DEFAULT NULL,
																`item5` varchar(255) DEFAULT NULL,
																`value5` varchar(255) DEFAULT NULL,	
																 PRIMARY KEY (`id`) ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1");
if($res){
	echo "alarm actions table created<br>";
}
else{
	echo "alarm action table creation failed <br>";
}
														  
// measurements
$num_signals = 50;
$res = mysql_query("CREATE TABLE IF NOT EXISTS `measurements_legend` (	`id` tinyint(4) NOT NULL AUTO_INCREMENT,
																		`item` varchar(255) DEFAULT NULL,
																		`name` varchar(255) DEFAULT NULL,
																		`quantity` varchar(255) DEFAULT NULL,
																		`unit` varchar(255) DEFAULT NULL,
																		`description` text DEFAULT NULL,
																		UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ");
if($res){
	echo "measurements legend table created<br>";
}
else{
	echo "measurements legend table creation failed <br>";
}
// add default measurement entries
$res = mysql_query("REPLACE INTO `measurements_legend` (id,item,name,quantity,unit,description) VALUES 	(1,'building.ambient_temperature','Temperature','Temperature','degC','Outside temperature'),
																										(2,'building.irradiation.azimut','Azimut','Angle','deg','Solar azimut'),
																										(3,'building.irradiation.altitude','Altitude','Angle','deg','Solar altitude'),
																										(4,'building.irradiation.direct_theoretical','Direct','Heat flux','W/m2','Theoretical direct solar irradiation'),
																										(5,'building.irradiation.diffuse_theoretical','Diffuse','Heat flux','W/m2','Theoretical diffuse solar irradiation'),
																										(6,'building.irradiation.cloud_factor','Clouds','','-','Cloud factor'),
																										(7,'building.wind_velocity','Wind speed','Velocity','m/s','Wind speed'),
																										(8,'building.rain','Rain','','-','Rain or not')");												
if($res){
	echo "default measurements added<br>";
}


$res = mysql_query("CREATE TABLE IF NOT EXISTS `measurements` (	`id` bigint(20) NOT NULL AUTO_INCREMENT,
																`signal_id` tinyint(4) NOT NULL,
																`time` bigint(20) NOT NULL,
																`value` float DEFAULT NULL,
																UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ");
if($res){
	echo "measurements table created<br>";
}
else{
	echo "measurements table creation failed <br>";
}
mysql_query("CREATE INDEX time_signal_id ON measurements(time, signal_id)");


$res = mysql_query("CREATE TABLE IF NOT EXISTS `measurements_quarterhouraverage` (	`id` bigint(20) NOT NULL AUTO_INCREMENT,
																					`signal_id` tinyint(4) NOT NULL,
																					`time` int(11) NOT NULL,
																					`value` float DEFAULT NULL,
																					UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ");												 						 
if($res){
	echo "quarterhour average measurements table created<br>";
}		
else{
	echo "quarterhour average measurements table creation failed <br>";
}
mysql_query("CREATE INDEX time_signal_id ON measurements_quarterhouraverage(time, signal_id)");

$res = mysql_query("CREATE TABLE IF NOT EXISTS `measurements_weekaverage` (	`id` bigint(20) NOT NULL AUTO_INCREMENT,
																			`signal_id` tinyint(4) NOT NULL,
																			`time` int(11) NOT NULL,
																			`value` float DEFAULT NULL,
																			UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ");												 						 
if($res){
	echo "week average measurements table created<br>";
}		
else{
	echo "week average measurements table creation failed <br>";
}
mysql_query("CREATE INDEX time_signal_id ON measurements_weekaverage(time, signal_id)");

$res = mysql_query("CREATE TABLE IF NOT EXISTS `measurements_monthaverage` (`id` bigint(20) NOT NULL AUTO_INCREMENT,
																			`signal_id` tinyint(4) NOT NULL,
																			`time` int(11) NOT NULL,
																			`value` float DEFAULT NULL,
																			UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ");												 
if($res){
	echo "month average measurements table created<br>";
}
else{
	echo "month average measurements table creation failed <br>";
}
mysql_query("CREATE INDEX time_signal_id ON measurements_monthaverage(time, signal_id)");
	

		
// Temperature setpoints
$res = mysql_query( "CREATE TABLE IF NOT EXISTS `temperature_setpoints` (	`id` int(11) NOT NULL AUTO_INCREMENT,
																			`zone` varchar(128) NOT NULL,
																			`day` tinyint(4) NOT NULL,
																			`hour` tinyint(4) NOT NULL,
																			`minute` tinyint(4) NOT NULL,
																			`setpoint` float NOT NULL,
																			PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1");
if($res){
	echo "setpoints table created<br>";
}
else{
	echo "setpoints table creation failed <br>";
}
				
// Pagebuilder
$res = mysql_query( "CREATE TABLE IF NOT EXISTS `pagebuilder` (	`id` int(11) NOT NULL AUTO_INCREMENT,
																`model` MEDIUMTEXT DEFAULT NULL,
																PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1");													
// add default data
$res = mysql_query("INSERT INTO `pagebuilder` (id,model) VALUES (1,'[{\"id\":\"home\",\"name\":\"Home\",\"page\":[{\"id\":\"home\",\"name\":\"Home\",\"img\":\"\",\"temperature_item\":\"\",\"section\":[]}]}]'");
$res = mysql_query("INSERT INTO `pagebuilder` (id,model) VALUES (2,'[{\"id\":\"home\",\"name\":\"Home\",\"page\":[{\"id\":\"home\",\"name\":\"Home\",\"img\":\"\",\"temperature_item\":\"\",\"section\":[]}]}]'");
												
if($res){
	echo "default data added<br>";
}
if($res){
	echo "pagebuilder table created<br>";
}
else{
	echo "pagebuilder table creation failed <br>";
}

				
echo "finished";
?>