#!/bin/bash
# HomeCon installation file

# get a password to use throughout the installation
username="homecon"
password="pass"
password2=""

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
# use sudo adduser $username when customizing
useradd -d /home/$username $username 
echo -e "$password\n$password\n" | passwd $username

# Tools
apt-get update 
apt-get -y install openntpd python3 python3-dev python3-setuptools git unzip wget gcc g++ gfortran subversion patch 
easy_install3 pip
pip install ephem
pip install PyMySQL

# networking
./installation/networking.sh

# webserver
./installation/webserver.sh $username $password

# eibd
./installation/eibd.sh $username

# ipopt
./ipopt.sh

# homecon
./installation/homecon.sh $username $password

