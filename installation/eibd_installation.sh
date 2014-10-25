#!/bin/bash
# eibd installation script

sudo apt-get install build-essential

# create and eibd directory
sudo mkdir /var/eibd
sudo chown -R pi /var/eibd
cd /var/eibd

# install pthsem
tar zxvf /var/knxcontrol_installation/pthsem_2.0.8.tar.gz
cd pthsem-2.0.8/
./configure
make
sudo make install



# install eibd
cd /var/eibd
tar -zxvf /var/knxcontrol_installation/bcusdk_0.0.5.tar.gz
cd bcusdk-0.0.5/
$ export LD_LIBRARY_PATH=/usr/local/lib
$ ./configure --enable-onlyeibd --enable-eibnetiptunnel --enable-usb 
                               --enable-eibnetipserver --enable-ft12 
$ sudo ln -s /usr/local/lib/libeibclient.so.0 /usr/lib/libeibclient.so.0
$ sudo ln -s /usr/local/lib/libeibclient.so.0 /lib/libeibclient.so.0