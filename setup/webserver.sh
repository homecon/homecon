#!/bin/bash

username="homecon"
password=$1

apt-get update 
apt-get -y install apache2 vsftpd php5 php5-json libawl-php php5-curl

# MySQL
echo "mysql-server mysql-server/root_password password $password" | sudo debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $password" | sudo debconf-set-selections

apt-get -y install mysql-server php5-mysql

# you can now acces mysql from the command line using
# mysql -u root -p $password

# phpMyAdmin
echo "phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/dbconfig-install boolean true" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/app-password-confirm password $password" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/mysql/admin-pass password $password" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/mysql/app-pass password $password" | sudo debconf-set-selections

apt-get -y install phpmyadmin

echo "# phpmyadmin
Include /etc/phpmyadmin/apache.conf" | tee -a /etc/apache2/apache2.conf

# You can now login to php myadmin at 192.168.1.234/phpmyadmin using usernamer root and password $password


# FTP
# We will set up an ftp server to move files to your system.
apt-get -y install vsftpd

# Configure the ftp server
sed -i -e "s/\(anonymous_enable=\).*/\1NO/" \
-e "s/\(local_enable=\).*/\1YES/" \
-e 's/#local_enable=YES/local_enable=YES/g' \
-e 's/#local_umask=022/local_umask=0002\nfile_open_mode=0777/g' \
-e "s/\(write_enable=\).*/\1YES/" \
-e 's/#write_enable=YES/write_enable=YES/g' /etc/vsftpd.conf

service vsftpd restart

# Create a symlink in the www directory
ln -s /home/homecon/homecon  /var/www/homecon

# add an alias to apache
echo "# homecon
Alias /homecon \"/home/homecon/www\"
<Directory \"/home/homecon/www\">
	Order allow,deny
	Allow from all
	Require all granted
</Directory>" | tee -a /etc/apache2/apache2.conf


service apache2 restart
