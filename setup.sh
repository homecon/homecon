#!/bin/bash
# HomeCon setup file

# a new user will be created with the folloing username
# this username must be equal in all setup scripts
username="homecon"

# Get the setup file directory
setupdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# get a password to use throughout the installation
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
$setupdir/setup/networking.sh

# webserver
$setupdir/setup/webserver.sh $password

# eibd
$setupdir/setup/eibd.sh

# ipopt
$setupdir/setup/ipopt.sh

# homecon
$setupdir/setup/homecon.sh $password
