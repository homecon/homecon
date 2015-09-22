#!/bin/bash
# networking
echo -e "auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
address 192.168.1.254
gateway 192.168.1.1
netmask 255.255.255.0" > /etc/network/interfaces

/etc/init.d/networking restart
