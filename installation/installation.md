# Raspbery Pi preparation for KNXControl

## Start fresh
Write a fresh raspbian image to a 8GB SD card using win32diskimager
A high end SD card is preferable as we will write to it a lot
Plug in the raspberry pi and connect to your network



## General configuration
### First login
Find the ip adress of the raspberry.pi using Advanced IP Scanner
Use PuTTy to connect to your raspberry over ssh with any computer in your network
Use the above found ip adress, port 22
login as: `pi`, password: `raspberry`

Run configuration
```
sudo raspi-config
```
Choose
Enlarge the root partition

Under the internationalisation options choose Change Timezone and set it to your time zone
I'm not changing the password yet to make a general image of this pi with the default password.

When asked choose Reboot now
	
### Networking
After the reboot find the ip adress again and connect using PuTTy

#### Static ip
Setup a static ip adress open the network interfaces file
```
sudo nano /etc/network/interfaces
```

Change file contents to:
```
auto lo

iface lo inet loopback


auto eth0

iface eth0 inet static

address 192.168.1.2

gateway 192.168.1.1

netmask 255.255.255.0
```
Save the file and Exit using `Ctrl+O` `Return` and `Ctrl+X`

restart networking
```
sudo /etc/init.d/networking restart
```
you can safely ignore error messages

Now close your current putty session and start a new one using the static ip adress 192.168.1.2 in this example.
A reboot might also be required for the static ip to come to effect:
```
sudo reboot
```

From now on you can allways acces your pi through that ip adress.
It must be noted that it is best to choose an ip adress outside of your routers DHCP range, so set the DHCP range accordingly.

### User	
Add a user named "admin" with password "admin" (for now), this user will own all eibd and smarthome stuff
```
sudo adduser admin
```
type the password (admin) twice and keep hitting enter and finally hit "y" when asked if the info is correct

Add admin to the sudoers file to be able to use sudo
```
sudo adduser admin sudo
```

Logout 
```
logout
```
	
Start a new PuTTy session using the new credentials
We can leave the pi user for now but it will have to be deleted at some point
	
### Time
To automatically set the timezone we use a Network Time Protocol, just install ntp and the time should be fine
```
sudo apt-get install ntp
```


### Tools
Some essential linux tools we will be using need to be installed now, when sudo is called you will be asked for a password, enter admin
```	
sudo apt-get update

sudo apt-get -y install apache2 vsftpd php5 php5-json openntpd python3 python3-dev python3-setuptools git unzip wget libawl-php php5-curl

sudo easy_install3 pip

sudo pip install ephem

sudo pip install PyMySQL
```
	
	
	
## KNXControl
Clone the repository to a directory where all files will be kept
```
cd /usr/local

sudo git clone git://github.com/brechtba/knxcontrol.git
```

Set permissions
```
sudo chown -R admin:admin /usr/local/knxcontrol

sudo chmod -R 744 /usr/local/knxcontrol

sudo chmod -R 755 /usr/local/knxcontrol/visualisation

sudo chmod 755 /usr

sudo chmod 755 /usr/local

sudo chmod 755 /usr/local/knxcontrol
```
	

	
## EIBD
Go to the installation directory
```
cd /usr/local/knxcontrol/installation
```

Execute the eibd_installation.sh file.
```
./eibd_installation.sh
```

Preliminary test
```
/usr/local/bin/eibd -D -S -T -i --eibaddr=0.0.1 --daemon=/var/log/eibd.log --no-tunnel-client-queuing ipt:192.168.1.3

groupswrite ip:localhost 1/1/71 1
```
	
### Configuration
Create a configuration file
```
sudo nano /etc/default/eibd
```

Write the following within, use your knx ip gateway ip adress
```
EIB_ARGS="--daemon --Server --Tunnelling --Discovery --GroupCache --listen-tcp"

EIB_ADDR="0.0.255"

EIB_IF="ipt:192.168.1.3"
```
Save the file and Exit using `Ctrl+O` `Return` and `Ctrl+X`

Move the file "eibd" from the installation folder to /etc/init.d
```
sudo mv /usr/local/knxcontrol/installation/eibd /etc/init.d/eibd
```

Change the owner and group to root and set permissions
```
sudo chown root /etc/init.d/eibd

sudo chgrp root /etc/init.d/eibd

sudo chmod 755 /etc/init.d/eibd
```

Activate auto starting
```
sudo update-rc.d eibd defaults
```

Restart EIBD
```
/etc/init.d/eibd restart
```

### Test	
Test eibd by writing to the knx bus using groupswrite to an existing knx adress
```
groupswrite ip:localhost 1/1/71 1

groupswrite ip:localhost 1/1/71 0
```

Also test if eibd is loaded on reboot by rebooting (`sudo reboot`), starting a new PuTTy session and retrying the above commands



## FTP
We will set up an ftp server to move files to your pi. The actual server is already installed
To configure the server open the configure file
```
sudo nano /etc/vsftpd.conf
```

Search through the file and change the following lines:
change `anonymous_enable=YES` to anonymous_enable=NO
Uncomment the following lines:
```
#local_enable=YES
#write_enable=YES
```

To set default file permissions
Change the line `#local_unmask=022` to
```
local_unmask=02
file_open_mode=0777
```

Also, add a line to the bottom of the file:
```
force_dot_files=YES
```

Save the file and Exit using `Ctrl+O` `Return` and `Ctrl+X` and restart the ftp server:
```
sudo service vsftpd restart
```

## www directory
Create a symlink in the www directory to the `knxcontrol/visualisation` folder:
```
cd /var/www
sudo ln -s /usr/local/knxcontrol/visualisation  knxcontrol
```



## MySQL
Install the mysql server package
```
sudo apt-get install mysql-server
```
During the install procedure a root account for mysql will be created. Set it to admin as the default setting.

Enable php to comunicate with mysql by installing php5-mysql:
```
sudo apt-get install  php5-mysql
```

### phpMyAdmin
Install phpMyadmin
```
sudo apt-get install phpmyadmin
```
During the installation you will be asked several questions:
- Select Apache2 for the server
- Choose YES when asked about whether to Configure the database for phpmyadmin with dbconfig-common
- Enter your MySQL password when prompted (admin)
- Enter the password that you want to use to log into phpmyadmin (admin)

After the installation has completed, add phpmyadmin to the apache configuration.
```
sudo nano /etc/apache2/apache2.conf
```
Add the phpmyadmin config to the end of the file.
```
# phpmyadmin

Include /etc/phpmyadmin/apache.conf
```

And restart apache
```
sudo service apache2 restart
```

You can now login to php myadmin at 192.168.1.2/phpmyadmin using usernamer `root` and password `admin`.

### Setup tables
Login to myqsl from the command line using
```
mysql -u root -p
```
enter the password (admin) when asked.

Create a database:
```
CREATE DATABASE knxcontrol;
```

Create a new user:
```
CREATE USER 'knxcontrol'@'localhost' IDENTIFIED BY 'admin';
```

Set privileges of the new user:
```
GRANT ALL PRIVILEGES ON knxcontrol.* TO 'knxcontrol'@'localhost';
```

Open a browser window and go to "http://192.168.1.2/knxcontrol/data/create_tables.php". This will create all required mysql tables 


### Moving the database to another location
This step is not executed in the base image and commands are given here for reference also not tested.
```
sudo /etc/init.d/mysql stop

sudo cp -R -p /var/lib/mysql /media/hdd/mysql
```
Edit the config file `sudo nano /etc/mysql/my.cnf` Look for the entry for `datadir`, and change the path (which should be /var/lib/mysql) to the new data directory.

Edit the another file `sudo nano /etc/apparmor.d/usr.sbin.mysqld` Look for lines beginning with `/var/lib/mysql`. Change `/var/lib/mysql` in the lines with the new path.

Restart the AppArmor profiles with the command:
```
sudo /etc/init.d/apparmor reload
```

Restart MySQL with the command:
```
sudo /etc/init.d/mysql restart
```



## SMARTHOME.PY
The next step is configuring smarthome.py. First we set the permissions of some files:
```
sudo chmod 744 /usr/local/knxcontrol/smarthome/bin/smarthome.py

sudo chmod 755 /usr/local/knxcontrol/smarthome/var/log/smarthome.log
```

Move the file "smarthome" from the installation folder to /etc/init.d
```
sudo mv /usr/local/knxcontrol/installation/smarthome /etc/init.d/smarthome
```

Change the owner and group to root and set permissions
```
sudo chown root:root /etc/init.d/smarthome

sudo chmod 755 /etc/init.d/smarthome
```

Activate auto starting
```
sudo update-rc.d smarthome defaults
```

### Test
Start smarthome.py with
```
/etc/init.d/smarthome start
```

And check the log file for errors
```
tail /usr/local/knxcontrol/smarthome/var/log/smarthome.log
```

## Create an image
At this step the base image is created. This is done on a different machine running some linux version. I used a bootable usb drive with Ubuntu 14.04.1.

First shutdown yout pi using `sudo halt`. Wait until it has stopped and remove the sd card. Fire up your linux machine, insert the sd card but do not mount it but check the name with:
```
sudo fdisk -l
```

We will resize the partition to around it's minimum size to be sure we can mount it on different sd cards. When inserted in a pi you can have it fill the entire space again using `sudo raspi-config`.

Start gparted, all your partitions should show up now. Find the ext4 partition on the sd-card (probably /dev/mmcblk0p2) select it and click Partition->Unmount. Then Click "Partition->Resize/Move". Click the right black arrow and move it until the wanted size is obtained.
Click "resize/move". and finally click "apply" and confirm to make the changes.

Now we will use dd to create the actual image
```
sudo dd if=/dev/mmcblk0 of=knxcontrol.img bs=4M
```

You can write the image back to an sd card using:
```
sudo dd if=knxcontrol.img of=/dev/mmcblk0
```
You will get an error message at the end of the process but this doesn't matter as the end is just blank.



## Changing passwords
After doing all this, or simply mounting the image, you will have to change thing for your own system. The first step is changing all passwords to more secure values.










## External hard drive
### Mounting
Next we will mount an external hard drive to use as network storage and mysql backup. This is recommended as the SD card in the raspberrry pi will probably be corruptes sooner or later.
A usb drive with external power supply is required as the Raspberry pi will probably not be able to supply the required power leading to death and destruction.
It is also recomended that you format the hard drive to an EXT4 filesystem beforehand.
Plug in the usb hard drive to one of the Raspberry pi usb ports and check if the hard drive is found:
´´´
sudo fdisk -l
´´´

The output will be something like this:
´´´
Disk /dev/sdb: 60.0 GB, 60060155904 bytes
255 heads, 63 sectors/track, 7301 cylinders
Units = cylinders of 16065 * 512 = 8225280 bytes
Disk identifier: 0x000b2b03

   Device Boot      Start         End      Blocks   Id  System
/dev/sda1               1        7301    58645251    b  W95 EXT4
´´´

Create a directory where to mount the drive
´´´
sudo mkdir /mnt/hdd 
´´´

To automate the mounting on reboot we neet to edit the filesystem table:
´´´
sudo nano /etc/fstab
´´´
Add the following line
```
/dev/sda1       /mnt/hdd           ext4    defaults        0       0 
```

And finally mount all remaining devices:
```
sudo mount -a 
```


### network storage
```
sudo apt-get install samba samba-common-bin
```

Create a backup of the conf file and edit the original file
```
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.old
sudo nano /etc/samba/smb.conf
```
Add
```
[Backup]
	comment = Backup Folder
	path = /media/hdd
	force user = admin
	force group = admin
	create mask = 0775
	directory mask = 0775
	read only = no
```

And restart Samba
```
sudo /etc/init.d/samba restart
```


## ipopt and pyipopt

Documentation is found at http://www.coin-or.org/Ipopt/documentation/
Install prequisites
```
sudo apt-get install gcc g++ gfortran subversion patch wget
```

Get ipopt from the repository
```
cd /etc
sudo svn co https://projects.coin-or.org/svn/Ipopt/stable/3.11 CoinIpopt 
cd CoinIpopt
```

Getting 3rd party libraries
```
cd ThirdParty/Blas 
sudo ./get.Blas 
cd ../Lapack 
sudo ./get.Lapack 
cd ../ASL 
sudo ./get.ASL
cd ../Mumps
sudo ./get.Mumps
cd ../Metis
sudo ./get.Metis
cd ..
cd ..
```

Compiling IPOPT
```
sudo mkdir build
cd build
sudo /etc/CoinIpopt/configure -C ADD_CFLAGS="-DNO_fpu_control"
sudo make
sudo make test
sudo make install
```

Test the example
```
cd /etc/CoinIpopt/build/Ipopt/examples/hs071_cpp
sudo ./hs071_cpp
```

Getting python.h
```
sudo apt-get install python3.2-dev
```

Install pyipopt
```
cd /etc
sudo git clone https://github.com/facat/py3ipopt.git
cd py3ipopt
```

edit setup.py
```
sudo nano setup.py 
```
Change directory line to `/etc/CoinIpopt/build/`
Change `blas` to `coinblas` and `lapack` to `coinlapack` in libraries 

```
#sudo ldconfig
sudo python3 setup.py build
sudo python3 setup.py install
cd examples
```
change print command in hs071.py, add (), This might not be required anymore
```
sudo nano hs071.py
python3 hs071.py
```
