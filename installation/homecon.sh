#!/bin/bash

password=$1

echo $password
mysql -u root -p$password

# MySQL
## Create MySQL database and user
echo "CREATE DATABASE homecon;CREATE USER 'homecon'@'localhost' IDENTIFIED BY '$password';GRANT ALL PRIVILEGES ON homecon.* TO 'homecon'@'localhost';" | mysql -u root -p$password

#echo "mysql -u root -p$password -e \"CREATE DATABASE homecon;CREATE USER 'homecon'@'localhost' IDENTIFIED BY '$password';GRANT ALL PRIVILEGES ON homecon.* TO 'homecon'@'localhost';\""

## Create tables
### users
#echo "" | mysql -u root -p$password

#echo "USE homecon; CREATE TABLE IF NOT EXISTS `users` (`id` int(11) NOT NULL AUTO_INCREMENT, `username` varchar(255) NOT NULL, `password` varchar(255) NOT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1\""

