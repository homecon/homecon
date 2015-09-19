apt-get update 
apt-get -y install apache2 vsftpd php5 php5-json libawl-php php5-curl

# Create a symlink in the www directory
ln -s /home/homecon/visualisation  /var/www/homecon

# MySQL
debconf-set-selections <<< 'mysql-server mysql-server/root_password password $1'
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password $1'
apt-get -y install mysql-server

apt-get -y install php5-mysql


# phpMyAdmin
echo 'phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/dbconfig-install boolean true' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/app-password-confirm password $1' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/mysql/admin-pass password $1' | debconf-set-selections
echo 'phpmyadmin phpmyadmin/mysql/app-pass password $1' | debconf-set-selections

apt-get -y install phpmyadmin




During the installation you will be asked several questions:
- Select Apache2 for the server
- Choose YES when asked about whether to Configure the database for phpmyadmin with dbconfig-common
- Enter your MySQL password when prompted (admin)
- Enter the password that you want to use to log into phpmyadmin (admin)

After the installation has completed, add phpmyadmin to the apache configuration.
```
$ sudo nano /etc/apache2/apache2.conf
```
Add the phpmyadmin config to the end of the file.
```
# phpmyadmin

Include /etc/phpmyadmin/apache.conf
```

And restart apache
```
$ sudo service apache2 restart
