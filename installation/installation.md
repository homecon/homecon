Installation
============

# Hardware
#### Required
* KNX/EIB home installation
* KNX/EIB Gateway, Ethernet interface
* Router
* Raspberry-Pi or some old PC

Connect your KNX/EIB gateway to your home network, the same network the server computer is on.
Make sure the KNX/EIB gateway has a static ip adress and that you know it.
By default the server you're going to setup will use the static ip adress 192.168.1.234.
Make sure this adress is outside of the DHCP range of your router (Most of the time this is the case by default).

#### Optional
* Flukso meter

Connect your Flukso meter to your home network and make sure it has a static ip adress.



# Installation and configuration
Several installation scripts are created to simplify the installation process.
When starting from a clean installation of Debian or Raspbian on a Raspberry Pi the full installation script can be used.
When installing HomeCon on a machine which is allready used for webserving or other services some parts must be ommitted and some tweaking might be necessary, check the installation scripts.

First of all I must say that the power of a Raspberry pi is sufficient for using HomeCon, running a small webserver alongside of it and even setup a logitech media server (allthough the web interface will be slow).
If you want more, for instance an OwnCloud service you'll need some more power but this comes at a cost! As the server will be on 24/7 365 days a year, it will use a lot of energy!
For instance a modern desktop consumes around 40W when not working hard.
This amounts to around 350kWh on a yearly basis, which in Belgium will cost you around €70.
Furthermore the accompanying 100kg CO2 emissions (according to [The european Association for battery electric vehicels](http://ec.europa.eu/transport/themes/strategies/consultations/doc/2009_03_27_future_of_transport/20090408_eabev_%28scientific_study%29.pdf)) are perfectly avoidable.
A Raspberry Pi uses only 5W, thus around €9 per year and 13kg CO2 emissions.
Some laptops give a good compromise between power and electricity use. I tested some laptops which used around 20W, but older laptops usually perform worse.

That aside, here are the installation instructions:


## Preparation of a fresh Raspberry Pi
Write a fresh raspbian image to a 8GB SD card using win32diskimager. 
A high end SD card is preferable as we will write to it a lot. 
Plug in the raspberry pi and connect to your network.

Find the ip adress of the raspberry.pi using Advanced IP Scanner or `sudo nmap -sP 192.168.1.*` on Linux
Use PuTTy or ssh to connect to your raspberry over ssh with any computer in your network
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

## Preparation of a fresh Debian distro
Install the operating system from a live cd or usb and add the ssh server during installation.
Make sure the machine is connected to the internet when doing so.
You will be asked for a root password and a user for you to work with.
Use any username but 'homecon' as this will be the user to own the homecon installation

if you forgot to check the ssh server mark you can do it in root mode:
```
$ su
# apt-get install openssh-server
```

Find the ip adress of the machine using Advanced IP Scanner or `sudo nmap -sP 192.168.1.*` on Linux
Use PuTTy or ssh to connect to your machine over ssh with any computer in your network
Use the above found ip adress, port 22

it is possible that you need to install sudo manually
```
$ su
# apt-get install sudo
```
add yourself to sudoers
```
$ su
# adduser yourusername sudo
```

## Installing homecon
Download the installation folder of homecon into some temp folder
```
$ cd
$ sudo mkdir temp
$ cd temp
$ sudo apt-get -y install git
$ sudo git clone git://github.com/brechtba/homecon.git
```

Now run the installation script
```
$ cd ~/temp/homecon/installation
$ sudo ./installation.sh
```

You will be asked for a homecon password and the ip adress of your KNX/EIB Gateway and a group adress to test eibd. Ghoose the adress of a light control, if everything works out it should go on and off and you're done!


## Smarthome Items
Create smarthome configuration files. I'm hoping to make the configuration files obsolete in the near future so no instructions here yet. This is fairly well explained on the [Smarthome.py website](http://mknx.github.io/smarthome/)


## First connection
Go to 192.168.1.234/homecon in a web browser.
You can log in using username 'homecon' and the password you've entered during the installation.
Click the pagebuilder Icon on the top navigation bar and start adding pages and controls to HomeCon!











# Other installation steps which might come in handy
## Reconfiguring locales
```
$ sudo export LC_ALL=en_US.UTF-8
$ sudo locale-gen en_US.UTF-8
$ sudo dpkg-reconfigure locales
```

## Nano
nano is a great linux shell text editor
```
$ sudo nano filename
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

### Network storage
```
$ sudo apt-get install samba samba-common-bin
```
add users to samba
```
$ sudo smbpasswd -a username
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
	path = /mnt/hdd1/HomeServer
	force user = admin
	force group = admin
	create mask = 0774
	force create mode = 0774
	directory mask = 0774
	force directory mode = 0774
	read only = no
```

And restart Samba
```
$ sudo /etc/init.d/samba restart
```

Now go to another machine and install cifs-utils
```
$ sudo apt-get install cifs-utils
```
Create a .smbcredentials file in your home directory
```
$ echo "username=MyUsername
password=MyPassword" > ~/.smbcredentials
$ sudo chown root .smbcredentials
$ sudo chmod 600 .smbcredentials
```

create a group for the share, add users and get the group id from the groups file
```
$ nano /etc/group
```

create a mount directory
```
$ sudo /mnt/HomeServer
```
Create a credentials file 


And edit the fstab file to mount the network drive
```
$ sudo nano /etc/fstab
```
add
```
//192.168.1.234/harddrive //mnt/hdd1/HomeServer cifs credentials=//home//username//.smbcredentials,iocharset=utf8,sec=ntlm,gid=yourgroupid 0 0
```

and mount all drives
```
$ sudo mount -a
```



## Changing passwords
Before we open up ports to the www it's time to change all relevant passwords so our system is secure.
I suggest using a different, strong password for every application and storing them is some password manager (LastPass free works well for me).

### Raspberry pi
Start with the Raspberry pi password. To do this just type `passwd` in a ssh session.
You will be asked for your old password and the new one twice and you're done.
Definetely do this for the `pi` user as it has a default password which is a serious security hazzard when connecting the Pi to the web.


## Connecting to the web
To connect to your HomeCon server from anywhere in the world you need to do some port forwarding from your router to the ports set up for HomeCon.
Be warned that I am no internet security expert, far from it. The HomeCon websocket is only secured using a server side token which must match the client side token.
Connecting your server to the web is at your own risk! Don't come complaining when someone hacks your server and opens your garage door!

First you need to forward a port to the http port of the server, so go to your routers configuration page (usualy found at 192.168.1.1) and set up port forwarding from some port to 192.168.1.234 and port 80.
By default the port used to forward the websocket is port 9024 so setup another port forwarding from port 9024 to 192.168.1.234 port 2424 and you're good to go.
The port used for the websocket forwarding can be changed under settings in KNXcontrol.

### Dynamic dns
Most internet providers don't provide a static ip address to your router, but when you want to access your router from the outside you need to know it's ip address.
The trick to use id DDNS. We basically install a small program on the raspberry pi which continuously checks its outside ip address and sends it to a DDNS server.
This server links an easily readable name to the ip address so you can access the pi from the outside.

#### DuckDNS
Go to [www.duckdns.org](www.duckdns.org) and login using facebook or some other options (this is the huge downside of DuckDNS if you ask me), create a blank Facebook account if necessary.

Choose a domain name and fill it in and click go.

Go to install, select your new domain name in the box at the bottom and click linux cron, this will give you a set of instructions for which the essentials are copied here.
Go to a folder using  `cd /usr/local`, make a directory and a shell script
```
$ sudo mkdir duckdns
$ cd duckdns
$ sudo nano duck.sh
```
No copy the text from the website into the file. It should look something like this:
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
You can also use NO-IP for this service.
It's free and provides nice names so thats fun, the downside is you have to confirm your address every month.
To install it go to www.noip.com and register. Now add a host and choose a domain name to your liking.

Now we need to download the client, install it on the server and configure it to point to your domain name:
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



## Create an image of your Raspbery Pi
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


## Laptop lid functions
To keep a laptop from shutting down when you close the lid edit the logind.conf file
```
$ sudo nano /etc/systemd/logind.conf
```

Add a line `HandleLidSwitch=ignore`



## Users and groups

```
$ sudo adduser username
```

Create a new group:
```
$ sudo groupadd groupname
```

Show all groups:
```
$ cut -d: -f1 /etc/group
```


Add a user to an existing group
```
$ sudo usermod -a -G groupname username
```

