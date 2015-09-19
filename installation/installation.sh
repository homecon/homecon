#!/bin/bash
# HomeCon installation file

# get a password to use throughout the installation
username="homecon"
password="pass"
password2="pass2"

while [ "$password" != "$password2" ]; do
	read -s -p "Enter Password: " password
	echo
	read -s -p "Re-enter Password: " password2
	echo
	if [ "$password" != "$password2" ]; then
		echo "Passwords do not match!"
		echo
	fi
done

# add the user
useradd -d /home/$username $username 
echo -e "$password\n$password\n" | passwd $username

# Tools
apt-get update 
apt-get -y install openntpd python3 python3-dev python3-setuptools git unzip wget gcc g++ gfortran subversion patch 
easy_install3 pip
pip install ephem
pip install PyMySQL


# Installing Homecon
cd /home/$username
git clone --recursive git://github.com/brechtba/homecon.git
#chown -R admin:admin /usr/local/homecon
#chmod -R 755 /usr/local/knxcontrol
cd homecon


# networking
./installation/networking.sh

# eibd
./installation/eibd.sh $username





