#!/bin/bash
# HomeCon installation file

# get a password to use throughout the installation
username="homecon"
password="pass"
password2=""

while [ "$password" != "$password2" ]; do
	read -s -p "Enter a HomeCon password: " password
	echo
	read -s -p "Re-enter password: " password2
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

# create the user home dir
mkdir /home/$username
chown $username:$username /home/$username

# Tools
apt-get update 
apt-get -y install openntpd

# networking
./networking.sh

# webserver
./webserver.sh $password

# eibd
./eibd.sh

# ipopt
./ipopt.sh

# homecon
./homecon.sh $password

