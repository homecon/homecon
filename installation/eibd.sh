#!/bin/bash
# eibd installation script
# must be run from the homecon installation folder

username=$1

read -p "KNX Gateway ip adress: " knxip
read -p "Enter a KNX group adress to test eibd: " testgroupadress

# make sure we have essential build tools
apt-get install build-essential

cd installation

# unpack and install pthsem
tar zxvf pthsem_2.0.8.tar.gz
cd pthsem-2.0.8/
./configure
make
make install
cd ..


# unpack and install eibd
tar -zxvf bcusdk_0.0.5.tar.gz
cd bcusdk-0.0.5
export LD_LIBRARY_PATH=/usr/local/lib
./configure --with-pth=yes --without-pth-test --enable-onlyeibd --enable-eibnetip --enable-eibnetiptunnel --enable-eibnetipserver
make
make install
cd ..

# you have to load the dynamic library in /usr/local/lib in order for eibd to work, do the following:
echo "/usr/local/lib" | sudo tee -a /etc/ld.so.conf.d/bcusdk.conf
sudo ldconfig

touch /var/log/eibd.log
chown $username /var/log/eibd.log

# Preliminary test
# /usr/local/bin/eibd -D -S -T -i --eibaddr=0.0.1 --daemon=/var/log/eibd.log --no-tunnel-client-queuing ipt:$knxip
# groupswrite ip:localhost 1/1/71 1

# create a configuration file
echo -e "EIB_ARGS=\"--daemon --Server --Tunnelling --Discovery --GroupCache --listen-tc\"

EIB_ADDR=\"0.0.255\"

EIB_IF=\"ipt:$knxip\"" > /etc/default/eibd

# copy the init script and set permissions
cp initscripts/eibd /etc/init.d/eibd

sed -i -e "s/EIB_UID=\"homecon\"/EIB_UID=\"$username\"/g" /etc/init.d/eibd

chown root:root /etc/init.d/eibd
chmod 755 /etc/init.d/eibd

# activate auto starting
update-rc.d eibd defaults
/etc/init.d/eibd restart

# test	
groupswrite ip:localhost $testgroupadress 1
groupswrite ip:localhost $testgroupadress 0

cd ..

