#!/bin/bash

username="homecon"
password=$1

# Get the setup directory
setupdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the current working directory
cwd=$(pwd)

apt-get -y install python3 git
easy_install3 pip
pip3 install ephem
pip3 install PyMySQL
pip3 install sympy

# generate a token
token=$(date +%s | sha256sum | base64 | head -c 32)

# generate a salt
salt=$(date +%s | sha256sum | base64 | head -c 32)

# generate a json web token key
jwt_key=$(date +%s | sha256sum | base64 | head -c 32)



# Cloning HomeCon to it's default destination
# move the Homecon app to it's default destination
cd $setupdir
cd ..
mv www /home/$username/www

# Set permissions
chown -R $username:$username /home/$username/www
chmod -R 755 /home/$username/www
chown -R www-data:www-data /home/$username/www/pages
chown -R www-data:www-data /home/$username/www/requests/exportfiles
chmod 005 /home/$username/www/requests/config.php


# Create the password hash to enter in the database
hash=$(php -r "echo base64_encode(hash('sha256', '$password$salt', true));")

# MySQL
## Create MySQL database and user
echo "CREATE DATABASE IF NOT EXISTS homecon;
      GRANT ALL PRIVILEGES ON homecon.* TO 'homecon'@'localhost'  identified by '$password';" | mysql -u root -p$password

## Create tables
### users
echo "USE homecon;
      CREATE TABLE IF NOT EXISTS users (
      	id int(11) NOT NULL AUTO_INCREMENT,
		username varchar(255) NOT NULL,
		password varchar(255) NOT NULL,
		permission tinyint(4) NOT NULL DEFAULT '1',
		PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;" | mysql -u root -p$password


# this line will be removed in the future, when no users are found a registration screen should be shown
# this way passwords for database and admin user can be separated
echo "USE homecon;
	  INSERT IGNORE INTO users (id,username,password) VALUES (1,'homecon','$hash',9);" | mysql -u root -p$password

### data
echo "USE homecon;
	  CREATE TABLE IF NOT EXISTS data (
		id int(11) NOT NULL AUTO_INCREMENT,
		ip varchar(255) NOT NULL,
		port varchar(255) NOT NULL,
		web_ip varchar(255) NOT NULL,
		web_port varchar(255) NOT NULL,
		token varchar(255) NOT NULL,
		latitude float NOT NULL,
		longitude float NOT NULL,
		elevation float NOT NULL,
		PRIMARY KEY (id) ) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;" | mysql -u root -p$password

echo "USE homecon;
	  INSERT IGNORE INTO data (id,ip,port,web_ip,web_port,token,latitude,longitude,elevation) VALUES (1,'192.168.234.1','9024','mydomain.duckdns.org','9024','$token',51,5,70);" | mysql -u root -p$password

### alarms
echo "USE homecon;
	  CREATE TABLE IF NOT EXISTS alarms (
		id int(11) NOT NULL AUTO_INCREMENT,
		sectionid int(11) NOT NULL DEFAULT '1',
		active tinyint(4) NOT NULL DEFAULT '1',
		action_id int(11) DEFAULT NULL,
		hour tinyint(4) NOT NULL DEFAULT '12',
		minute tinyint(4) NOT NULL DEFAULT '0',
		sunrise tinyint(4) NOT NULL DEFAULT '0',
		sunset tinyint(4) NOT NULL DEFAULT '0',
		mon tinyint(4) NOT NULL DEFAULT '1',
		tue tinyint(4) NOT NULL DEFAULT '1',
		wed tinyint(4) NOT NULL DEFAULT '1',
		thu tinyint(4) NOT NULL DEFAULT '1',
		fri tinyint(4) NOT NULL DEFAULT '1',
		sat tinyint(4) NOT NULL DEFAULT '0',
		sun tinyint(4) NOT NULL DEFAULT '0',
		PRIMARY KEY (id) ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;" | mysql -u root -p$password

### actions
echo "USE homecon;
	  CREATE TABLE IF NOT EXISTS actions (
		id int(11) NOT NULL AUTO_INCREMENT,
		name varchar(255) DEFAULT NULL,
		sectionid varchar(255) DEFAULT NULL,
		delay1 int(11) DEFAULT NULL,
		item1 varchar(255) DEFAULT NULL,
		value1 varchar(255) DEFAULT NULL,
		delay2 int(11) DEFAULT NULL,
		item2 varchar(255) DEFAULT NULL,
		value2 varchar(255) DEFAULT NULL,
		delay3 int(11) DEFAULT NULL,
		item3 varchar(255) DEFAULT NULL,
		value3 varchar(255) DEFAULT NULL,	
		delay4 int(11) DEFAULT NULL,
		item4 varchar(255) DEFAULT NULL,
		value4 varchar(255) DEFAULT NULL,	
		delay5 int(11) DEFAULT NULL,
		item5 varchar(255) DEFAULT NULL,
		value5 varchar(255) DEFAULT NULL,	
		PRIMARY KEY (id) ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;" | mysql -u root -p$password

### profiles_legend
echo "USE homecon;
	  CREATE TABLE IF NOT EXISTS profiles_legend (
		id int(11) NOT NULL AUTO_INCREMENT,
		name varchar(255) DEFAULT NULL,
		quantity varchar(255) DEFAULT NULL,
		unit varchar(255) DEFAULT NULL,
		description text DEFAULT NULL,
		UNIQUE KEY ID (id)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;" | mysql -u root -p$password

### profiles
echo "USE homecon;
	  CREATE TABLE IF NOT EXISTS profiles (
		id bigint(20) NOT NULL AUTO_INCREMENT,
		profile_id int(11) NOT NULL,
		time bigint(20) NOT NULL,
		value float DEFAULT NULL,
		UNIQUE KEY ID (id)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;" | mysql -u root -p$password

### pagebuilder	
echo "USE homecon;
	  CREATE TABLE IF NOT EXISTS pagebuilder (
		id int(11) NOT NULL AUTO_INCREMENT,
		model MEDIUMTEXT DEFAULT NULL,
		PRIMARY KEY (id)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;" | mysql -u root -p$password

echo "USE homecon;
	  INSERT IGNORE INTO pagebuilder (id,model) VALUES (1,'[{\"id\":\"home\",\"name\":\"Home\",\"page\":[{\"id\":\"home\",\"name\":\"Home\",\"img\":\"\",\"temperature_item\":\"\",\"section\":[]}]}]');" | mysql -u root -p$password
echo "USE homecon;
	  INSERT IGNORE INTO pagebuilder (id,model) VALUES (2,'[{\"id\":\"home\",\"name\":\"Home\",\"page\":[{\"id\":\"home\",\"name\":\"Home\",\"img\":\"\",\"temperature_item\":\"\",\"section\":[]}]}]');" | mysql -u root -p$password



## website backend MySQL config 
echo "<?php
// define variables to access mysql
define(\"HOST\", \"localhost\");
define(\"USER\", \"homecon\");
define(\"PASSWORD\", \"$password\");
define(\"DATABASE\", \"homecon\");
define(\"SALT\", \"homecon\");
define(\"JWT_KEY\", \"$jwt_key\");
?>" | tee /home/$username/homecon/pages/config.php




# install parsenlp
# parsenlp is a helping module to define optimization problems in python
cd /usr/local/lib/python3.4/dist-packages
rm -f parsenlp
git clone git://github.com/brechtba/parsenlp.git
sudo chmod -R 755 parsenlp



# Smarthome
# Clone homecon version of smarthome
cd /home/$username
rm -f smarthome
git clone -b homecon git://github.com/brechtba/smarthome.git

chown -R $username:$username /home/$username/smarthome
chmod -R 755 //home/$username/smarthome

# copy the init script and set permissions
cp $setupdir/initscripts/smarthome /etc/init.d/smarthome

sed -i -e "s%SH_UID=\"homecon\"%SH_UID=\"$username\"%g" \
-e "s%DIR=/home/homecon/smarthome/bin%DIR=/home/$username/smarthome/bin%g" /etc/init.d/smarthome

# set token in smarthome plugin.conf
sed -i -e "s%token=token%token=$token%g" \ 
-e "s%mysql_pass=mysql_pass%mysql_pass=$password%g"  /home/$username/smarthome/etc/plugin.conf

chown root:root /etc/init.d/smarthome
chmod 755 /etc/init.d/smarthome

# activate auto starting
update-rc.d smarthome defaults

# test
/etc/init.d/smarthome restart
tail /home/$username/smarthome/var/log/smarthome.log


cd $cwd

