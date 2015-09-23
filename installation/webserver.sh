
password=$1

apt-get update 
apt-get -y install apache2 vsftpd php5 php5-json libawl-php php5-curl

# Create a symlink in the www directory
ln -s /home/homecon/homecon/visualisation  /var/www/homecon

# MySQL
echo "mysql-server mysql-server/root_password password $password" | sudo debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $password" | sudo debconf-set-selections

apt-get -y install mysql-server
apt-get -y install php5-mysql


# phpMyAdmin
echo "phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/dbconfig-install boolean true" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/app-password-confirm password $password" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/mysql/admin-pass password $password" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/mysql/app-pass password $password" | sudo debconf-set-selections

apt-get -y install phpmyadmin

echo "# phpmyadmin
Include /etc/phpmyadmin/apache.conf" | tee -a /etc/apache2/apache2.conf

# ftp
apt-get -y install vsftpd

sed -i -e "s/\(anonymous_enable=\).*/\1NO/" \
-e "s/\(local_enable=\).*/\1YES/" \
-e 's/#local_umask=022/local_umask=0002\nfile_open_mode=0777/g' \
-e 's/#write_enable=YES/write_enable=YES/g' /etc/vsftpd.conf

service vsftpd restart

# virtual hosts
#echo "<VirtualHost *:80>
#    ServerAdmin admin@test.com
#    ServerName homecon
#    ServerAlias homecon
#    DocumentRoot /home/homecon/homecon/visualization
#    ErrorLog ${APACHE_LOG_DIR}/error.log
#    CustomLog ${APACHE_LOG_DIR}/access.log combined
#</VirtualHost>" | tee /etc/apache2/sites-available/homecon.conf

#a2ensite /etc/apache2/sites-available/homecon.conf

service apache2 restart
