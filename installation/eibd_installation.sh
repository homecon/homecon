#!/bin/bash
# eibd installation script

# make sure we have essential build tools
sudo apt-get install build-essential

cd /tmp/knxcontrol_installation

# install pthsem
tar zxvf /tmp/knxcontrol_installation/pthsem_2.0.8.tar.gz
cd pthsem-2.0.8/
./configure
make
sudo make install



# install eibd
cd /var/knxcontrol_installation

tar -zxvf /var/knxcontrol_installation/bcusdk_0.0.5.tar.gz
cd bcusdk-0.0.5
export LD_LIBRARY_PATH=/usr/local/lib
./configure --with-pth=yes --without-pth-test --enable-onlyeibd --enable-eibnetip --enable-eibnetiptunnel --enable-eibnetipserver
make
sudo make install

# You have to load the dynamic library in /usr/local/lib in order for eibd to work, do the following:
echo "/usr/local/lib" | sudo tee -a /etc/ld.so.conf.d/bcusdk.conf
sudo ldconfig

sudo touch /var/log/eibd.log
sudo chown $USER /var/log/eibd.log