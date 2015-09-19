# Raspbery Pi preparation for KNXControl

## Start fresh
Write a fresh raspbian image to a 8GB SD card using win32diskimager. 
A high end SD card is preferable as we will write to it a lot. 
Plug in the raspberry pi and connect to your network.

The rest of these instruction might also work for any other linux Debian systems.

## General configuration
### First login
Find the ip adress of the raspberry.pi using Advanced IP Scanner or `sudo nmap -sP 192.168.1.1/24` on Linux
Use PuTTy to connect to your raspberry over ssh with any computer in your network
Use the above found ip adress, port 22
login as: `pi`, password: `raspberry`

Run configuration
```
$ sudo raspi-config
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
$ sudo nano /etc/network/interfaces
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
$ sudo /etc/init.d/networking restart
```
you can safely ignore error messages

Now close your current putty session and start a new one using the static ip adress 192.168.1.2 in this example.
A reboot might also be required for the static ip to come to effect:
```
$ sudo reboot
```

From now on you can allways acces your pi through that ip adress.
It must be noted that it is best to choose an ip adress outside of your routers DHCP range, so set the DHCP range accordingly.

### User	
Add a user named "admin" with password "admin" (for now), this user will own all eibd and smarthome stuff
```
$ sudo adduser admin
```
type the password (admin) twice and keep hitting enter and finally hit "y" when asked if the info is correct

Add admin to the sudoers file to be able to use sudo
```
$ sudo adduser admin sudo
```

Logout 
```
$ logout
```
	
Start a new PuTTy session using the new credentials
We can leave the pi user for now but it will have to be deleted at some point
	
### Time
To automatically set the timezone we use a Network Time Protocol, just install ntp and the time should be fine
```
$ sudo apt-get install ntp
```


### Tools
Some essential linux tools we will be using need to be installed now, when sudo is called you will be asked for a password, enter admin
```	
$ sudo apt-get update
$ sudo apt-get -y install apache2 vsftpd php5 php5-json openntpd python3 python3-dev python3-setuptools git unzip wget libawl-php php5-curl
$ sudo easy_install3 pip
$ sudo pip install ephem
$ sudo pip install PyMySQL
```
	
	
	
## HomeCon
Clone the repository to a directory where all files will be kept
```
$ cd /usr/local
$ sudo git clone --recursive git://github.com/brechtba/homecon.git
```

Set permissions
```
$ sudo chown -R admin:admin /usr/local/knxcontrol
$ sudo chmod -R 755 /usr/local/knxcontrol
$ sudo chmod -R 755 /usr/local/knxcontrol/visualisation
$ sudo chmod 755 /usr
$ sudo chmod 755 /usr/local
$ sudo chmod 755 /usr/local/knxcontrol
```
	
	
## EIBD
Go to the installation directory
```
$ cd /usr/local/knxcontrol/installation
```

Execute the eibd_installation.sh file.
```
$ ./eibd_installation.sh
```

Preliminary test
```
$ /usr/local/bin/eibd -D -S -T -i --eibaddr=0.0.1 --daemon=/var/log/eibd.log --no-tunnel-client-queuing ipt:192.168.1.3
$ groupswrite ip:localhost 1/1/71 1
```
	
### Configuration
Create a configuration file
```
$ sudo nano /etc/default/eibd
```

Write the following within, use your knx ip gateway ip adress
```
EIB_ARGS="--daemon --Server --Tunnelling --Discovery --GroupCache --listen-tcp"

EIB_ADDR="0.0.255"

EIB_IF="ipt:192.168.1.3"
```
Save the file and Exit using `Ctrl+O` `Return` and `Ctrl+X`

Copy the file "eibd" from the installation folder to /etc/init.d
```
$ sudo cp /usr/local/knxcontrol/installation/eibd /etc/init.d/eibd
```

Change the owner and group to root and set permissions
```
$ sudo chown root /etc/init.d/eibd
$ sudo chgrp root /etc/init.d/eibd
$ sudo chmod 755 /etc/init.d/eibd
```

Activate auto starting
```
$ sudo update-rc.d eibd defaults
```

Restart EIBD
```
$ sudo /etc/init.d/eibd restart
```

### Test	
Test eibd by writing to the knx bus using groupswrite to an existing knx adress
```
$ groupswrite ip:localhost 1/1/71 1
$ groupswrite ip:localhost 1/1/71 0
```

Also test if eibd is loaded on reboot by rebooting (`sudo reboot`), starting a new PuTTy session and retrying the above commands



## FTP
We will set up an ftp server to move files to your pi. The actual server is already installed
To configure the server open the configure file
```
$ sudo nano /etc/vsftpd.conf
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
$ sudo service vsftpd restart
```

## www directory
Create a symlink in the www directory to the `knxcontrol/visualisation` folder:
```
$ cd /var/www
$ sudo ln -s /usr/local/knxcontrol/visualisation  knxcontrol
```



## MySQL
Install the mysql server package
```
$ sudo apt-get install mysql-server
```
During the install procedure a root account for mysql will be created. Set it to "admin" as the default setting.

Enable php to communicate with mysql by installing php5-mysql:
```
$ sudo apt-get install  php5-mysql
```

### phpMyAdmin
Install phpMyadmin
```
$ sudo apt-get install phpmyadmin
```
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
```

You can now login to php myadmin at 192.168.1.2/phpmyadmin using usernamer `root` and password `admin`.

### Setup tables
Login to myqsl from the command line using
```
$ mysql -u root -p
```
enter the password (admin) when asked.

Create a database:
```
> CREATE DATABASE knxcontrol;
```

Create a new user:
```
> CREATE USER 'knxcontrol'@'localhost' IDENTIFIED BY 'admin';
```

Set privileges of the new user:
```
> GRANT ALL PRIVILEGES ON knxcontrol.* TO 'knxcontrol'@'localhost';
```

Log out using
```
> quit
```

Open a browser window and go to "http://192.168.1.2/knxcontrol/data/create_tables.php". This will create all required mysql tables 

## SMARTHOME.PY
The next step is configuring smarthome.py. First we set the permissions of some files:
```
$ sudo chmod 744 /usr/local/knxcontrol/smarthome/bin/smarthome.py
$ sudo chmod 755 /usr/local/knxcontrol/smarthome/var/log/smarthome.log
```

Copy the file "smarthome" from the installation folder to /etc/init.d
```
$ sudo cp /usr/local/knxcontrol/installation/smarthome /etc/init.d/smarthome
```

Change the owner and group to root and set permissions
```
$ sudo chown root:root /etc/init.d/smarthome
$ sudo chmod 755 /etc/init.d/smarthome
```

Activate auto starting
```
$ sudo update-rc.d smarthome defaults
```

### Test
Start smarthome.py with
```
$ sudo /etc/init.d/smarthome restart
```

And check the log file for errors
```
$ tail /usr/local/knxcontrol/smarthome/var/log/smarthome.log
```

Add a symlink to the smarthome log file
```
$ sudo ln -s /usr/local/knxcontrol/smarthome/var/log/smarthome.log /usr/local/knxcontrol/visualisation/data/smarthome.log
```

## External hard drive
### Mounting
Next we will mount an external hard drive to use as network storage and mysql backup. This is recommended as the SD card in the raspberrry pi will probably be corruptes sooner or later.
A usb drive with external power supply is required as the Raspberry pi will probably not be able to supply the required power leading to death and destruction.
It is also recomended that you format the hard drive to an EXT4 filesystem beforehand.
Plug in the usb hard drive to one of the Raspberry pi usb ports and check if the hard drive is found:
```
$ sudo fdisk -l
```

The output will be something like this:
```
Disk /dev/sdb: 60.0 GB, 60060155904 bytes
255 heads, 63 sectors/track, 7301 cylinders
Units = cylinders of 16065 * 512 = 8225280 bytes
Disk identifier: 0x000b2b03

   Device Boot      Start         End      Blocks   Id  System
/dev/sda1               1        7301    58645251    b  W95 EXT4
```

Create a directory where to mount the drive
```
$ sudo mkdir /mnt/hdd 
```

To automate the mounting on reboot we neet to edit the filesystem table:
```
$ sudo nano /etc/fstab
```
Add the following line
```
/dev/sda1       /mnt/hdd           ext4    defaults        0       0 
```

And finally mount all remaining devices:
```
$ sudo mount -a 
```


### network storage
```
$ sudo apt-get install samba samba-common-bin
```

Create a backup of the conf file and edit the original file
```
$ sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.old
$ sudo nano /etc/samba/smb.conf
```
Add
```
[Home]
	comment = Home network storage
	path = /mnt/hdd
	force user = admin
	force group = admin
	create mask = 0775
	directory mask = 0775
	read only = no
```

And restart Samba
```
$ sudo /etc/init.d/samba restart
```


## Optimization tools
### Ipopt
Ipopt (pronounced eye pee opt) is a solver for large scale non-linear programs (NLP) using the interior point algorithm. 
In KNXControl we will use the program from Smarthome.py to do a system identification. 
We will compile the program from source ourself as there is no suitable binary for Raspberry-pi. 
Documentation is found at http://www.coin-or.org/Ipopt/documentation/

Install prequisites
```
$ sudo apt-get install gcc g++ gfortran subversion patch wget
```

Get ipopt from the repository
```
$ cd /etc
$ sudo svn co https://projects.coin-or.org/svn/Ipopt/stable/3.11 CoinIpopt 
$ cd /etc/CoinIpopt
```

Getting 3rd party libraries, there are files present in the Ipopt source to do this so we will use them. 
We will use the MUMPS Linear solver as it is open, not everyone has access to an academic solver like MA57 and for our purpose it will be sufficient.
```
$ cd /etc/CoinIpopt/ThirdParty/Blas/
$ sudo ./get.Blas
$ cd ../Lapack
$ sudo ./get.Lapack
$ cd ../ASL
$ sudo ./get.ASL
$ cd ../Mumps
$ sudo ./get.Mumps
$ cd ../Metis
$ sudo ./get.Metis
$ cd /etc/CoinIpopt
```

Run the following commands to compile Ipopt, and go for a cup of coffee as it will take about two hours.
```
$ sudo mkdir /etc/CoinIpopt/build
$ cd /etc/CoinIpopt/build
$ sudo /etc/CoinIpopt/configure --prefix=/usr/local/ -C ADD_CFLAGS="-DNO_fpu_control"
$ sudo make
$ sudo make test
$ sudo make install
```

Test the example
```
$ cd /etc/CoinIpopt/build/Ipopt/examples/hs071_cpp
$ sudo make
$ sudo ./hs071_cpp
```
If everything works you should see some program iterations and a reported that a solution was found `*** The problem solved!`.

### pyipopt
We'll use a package to let us interface ipopt from python and thus from within smarthome.py. 
First we need some prequisites.
```
$ sudo apt-get install python3.2-dev
```

Install pyipopt I'v forked the repository and changed some things 
```
$ cd /etc
$ sudo git clone https://github.com/BrechtBa/pyipopt.git
$ cd /etc/pyipopt

```

Build and install
```
$ sudo ldconfig
$ sudo python3.2 setup.py build
$ sudo python3.2 setup.py install
```

Now we're ready to test the interface from python by running an example:
```
$ sudo python3.2 /etc/pyipopt/examples/hs071_PY3.py
```

You should see the same solution as above.



## Changing passwords
Before we open up ports to the www it's time to change all relevant passwords so our system is secure.
I suggest using a different, strong password for every application and storing them is some password manager (LastPass free works well for me).

### Raspberry pi
Start with the Raspberry pi password. To do this just type `passwd` in a ssh session. You will be asked for your old password and the new one twice and you're done.

### MySQL
Next is the MySQL root password, enter the following in a shell (change newpass with your new password)
```
$ mysqladmin -u root -p'admin' password newpass
```
No we need to set the MySQL knxcontrol user password. So login to mysql as root with your new password, switch to the users database and set the new password
```
$ mysql -u root -p
> use mysql;
> SET PASSWORD FOR 'knxcontrol'@'localhost' = PASSWORD('newpass');
```
Exit the MySQL shell using `Ctrl+D`

Now set the new password for the knxcontrol user in 'pages/config.php' and in 'items/building.conf' upload them to the raspberry and restart smarthome.py using
```
$ sudo /etc/init.d/smarthome restart
```

### knxcontrol
To secure the WebSocket which is used to talk to smarthome a token is transmitted on every write request. This token must be set in '/smarthome/items/building.conf' and in the settings page of KNXcontrol.


## Connecting to the web
To connect KNXControl to the web you need to do some port forwarding from your router to the ports set up for KNXcontrol.
First you need to forward a port to the http port of the raspbery pi, so go to your routers configuration page (usualy found at 192.168.1.1) and set up port forwarding from some port to 192.168.1.2 and port 80.

By default the port used to forward the websocket is port 9024 so setup another port forwarding from port 9024 to 192.168.1.2 port 2424 and you're good to go.
The port used for the websocket forwarding can be changed under settings in KNXcontrol.

### Dynamic dns
Most internet providers don't provide a static ip address to your router, but when you want to access your router from the outside you need to know it's ip address.
The trick to use id DDNS. We basically install a small program on the raspberry pi which continuously checks its outside ip address and sends it to a DDNS server.
This server links an easily readable name to the ip address so you can access the pi from the outside.

#### DuckDNS
Go to www.duckdns.org and login using facebook or some other options, create a blank Facebook account if necessary.

Choose a domain name and fill it in and click go.

Go to install, select your new domain name in the box at the bottom and click linux cron, this will give you a set of instructions for which the essentials are copied here.
Go to a folder using  `cd /usr/local`, make a directory and a shell script
```
$ sudo mkdir duckdns
$ cd duckdns
$ sudo nano duck.sh
```
No copy the text from the website into the file. I should look like this:
```
echo url="https://www.duckdns.org/update?domains=yourdomain&token=yourtoken&ip=" | curl -k -o /usr/local/duckdns/duck.log -K -
```
Save the file using `Ctrl+O` and exit `Ctrl+X`
Change the file permissions:
```
$ sudo chmod 700 duck.sh
```
Next change the cron file to run the script every 5 minutes. Open the crontab file
```
$ sudo crontab -e
```
Paste this at the bottom:
```
*/5 * * * * /usr/local/duckdns/duck.sh >/dev/null 2>&1
```
Test using
```
$ sudo ./duck.sh
$ cat duck.log
```
And were done.

#### NO-IP
You can also use NO-IP for this service. It's free and provides nice names so thats fun, the downside is you have to confirm your address every month. To install it go to www.noip.com and register. Now add a host and choose a domain name to your liking.

Now we need to download the client, install it on the raspberry pi and configure it to point to your domain name:
```
$ cd /usr/local/src
$ sudo wget http://www.no-ip.com/client/linux/noip-duc-linux.tar.gz
$ sudo tar xzf noip-duc-linux.tar.gz
$ cd noip-2.1.9-1
$ sudo make
$ sudo make install
```
During the install procedure you will be asked for several things.
* login/email: enter the email address with which you just signed up for noip
* password: the noip password
If you only have registered 1 host this will be detected automatically and you only need to choose an update interval, the suggested 30 minutes is fine.
You will also be asked if a script needs to be run on a successful update but this is not necessary so type `n`.

The installation ends with the a message that a configuration file was created and it's location. Start the client with:
```
$ sudo /usr/local/bin/noip2
```

Now we need to make sure the client starts automatically on reboot. To do this we need to become the root user for a second
```
$ sudo -i
# echo '/usr/local/bin/noip2' >> /etc/rc.local
# logout
```
And were done.


## Create an image
At this step you can make an image as backup. This is done on a different machine running some linux version. I used a bootable usb drive with Ubuntu 14.04.1.

First shutdown yout pi using `sudo halt`. Wait until it has stopped and remove the sd card. Fire up your linux machine, insert the sd card but do not mount it but check the name with:
```
$ sudo fdisk -l
```

We will resize the partition to around it's minimum size to be sure we can mount it on different sd cards. When inserted in a pi you can have it fill the entire space again using `sudo raspi-config`.

Start gparted, all your partitions should show up now. Find the ext4 partition on the sd-card (probably /dev/mmcblk0p2) select it and click Partition->Unmount. Then Click "Partition->Resize/Move". Click the right black arrow and move it until the wanted size is obtained.
Click "resize/move". and finally click "apply" and confirm to make the changes.

Now we will use dd to create the actual image
```
$ sudo dd if=/dev/mmcblk0 of=knxcontrol.img bs=4M
```

You can write the image back to an sd card using:
```
$ sudo dd if=knxcontrol.img of=/dev/mmcblk0
```
You will get an error message at the end of the process but this doesn't matter as the end is just blank.

