
password=$1

apt-get update 
apt-get -y install apache2 vsftpd php5 php5-json libawl-php php5-curl

# Create a symlink in the www directory
ln -s /home/homecon/visualisation  /var/www/homecon

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
