<?php
// connect to the database
include('../data/mysql.php');
	
//mysql_query("DROP TABLE measurements_signal".$id."_week");


// users
mysql_query("CREATE TABLE IF NOT EXISTS `users` (`id` int(11) NOT NULL AUTO_INCREMENT,
                                                 `username` varchar(255) NOT NULL,
                                                 `password` varchar(255) NOT NULL,
                                                  PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1");
// add default user
mysql_query("INSERT INTO `users` (id,username,password) VALUES (1,'admin','".md5('admin')."')");
												  
												  
// data
mysql_query("CREATE TABLE IF NOT EXISTS `data` (`password` varchar(255) NOT NULL,
                                                `ip` varchar(255) NOT NULL,
                                                `port` varchar(255) NOT NULL,
                                                `web_ip` varchar(255) NOT NULL,
                                                `web_port` varchar(255) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=latin1)");
												
// alarms
mysql_query("CREATE TABLE IF NOT EXISTS `alarms` (`id` int(11) NOT NULL AUTO_INCREMENT,
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

												   
mysql_query("CREATE TABLE IF NOT EXISTS `alarm_actions` (`id` int(11) NOT NULL AUTO_INCREMENT,
														 `name` varchar(255) DEFAULT NULL,
                                                         `sectionid` varchar(255) DEFAULT NULL,
														 `delay1` int(11) DEFAULT NULL,
												         `item1` varchar(255) DEFAULT NULL,
                                                         `action1` varchar(255) DEFAULT NULL,
														 `delay2` int(11) DEFAULT NULL,
												         `item2` varchar(255) DEFAULT NULL,
                                                         `action2` varchar(255) DEFAULT NULL,	
														 `delay3` int(11) DEFAULT NULL,
												         `item3` varchar(255) DEFAULT NULL,
                                                         `action3` varchar(255) DEFAULT NULL,	
														 `delay4` int(11) DEFAULT NULL,
												         `item4` varchar(255) DEFAULT NULL,
                                                         `action4` varchar(255) DEFAULT NULL,	
														 `delay5` int(11) DEFAULT NULL,
												         `item5` varchar(255) DEFAULT NULL,
                                                         `action5` varchar(255) DEFAULT NULL,	
												          PRIMARY KEY (`id`) ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1");
														  
// measurements
$num_signals = 50;
mysql_query("CREATE TABLE IF NOT EXISTS `measurements_legend` (`id` tinyint(4) NOT NULL AUTO_INCREMENT,
															   `item` varchar(255) NOT NULL,
															   `name` varchar(255) NOT NULL,
															   `quantity` varchar(255) NOT NULL,
															   `unit` varchar(255) NOT NULL,
															   `description` text NOT NULL,
															   UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ");

$query = "CREATE TABLE IF NOT EXISTS `measurements` (`id` bigint(20) NOT NULL AUTO_INCREMENT,
												     `time` bigint(20) NOT NULL, ";
for($i=1;$i<=$num_signals;$i++){
	$query = $query."`signal$i` float DEFAULT NULL,";
}
$query =  $query. "PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1";
mysql_query( $query );

$query = "CREATE TABLE IF NOT EXISTS `measurements_monthaverage` (`id` bigint(20) NOT NULL AUTO_INCREMENT,
												     `month` int(11) NOT NULL,
													 `year` int(11) NOT NULL,
													 `timestamp` int(11) NOT NULL, ";
for($i=1;$i<=$num_signals;$i++){
	$query = $query."`signal$i` float DEFAULT NULL, ";
}
$query =  $query. "PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1";
mysql_query( $query );													 
	
$query = "CREATE TABLE IF NOT EXISTS `measurements_weekaverage` (`id` bigint(20) NOT NULL AUTO_INCREMENT,
												                 `week` int(11) NOT NULL,
													             `year` int(11) NOT NULL,
													             `timestamp` int(11) NOT NULL, ";
for($i=1;$i<=$num_signals;$i++){
	$query = $query."`signal$i` float DEFAULT NULL, ";
}
$query =  $query. "PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1";
mysql_query( $query );													 
					
// Temperature setpoints
mysql_query( "CREATE TABLE IF NOT EXISTS `temperature_setpoints` (`id` int(11) NOT NULL AUTO_INCREMENT,
																  `zone` varchar(128) NOT NULL,
																  `day` tinyint(4) NOT NULL,
																  `hour` tinyint(4) NOT NULL,
																  `minute` tinyint(4) NOT NULL,
																  `setpoint` float NOT NULL,
																  PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1");
																  
echo "succes";
?>