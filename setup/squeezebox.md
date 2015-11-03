# Turn a Pi into a Squeezebox player

## Squeezelite
Installing a sound card driver
```
sudo apt-get install alsa
```

Install some libraries
```
sudo apt-get install libfaad2 libmad0 libmpg123-0 libasound2
```

And install squeezelite
```
wget https://squeezelite.googlecode.com/files/squeezelite-armv6hf
chmod +x squeezelite-armv6hf
sudo mv squeezelite-armv6hf /usr/bin/
sudo adduser admin audio
```

Show audio devices
```
/usr/bin/squeezelite-armv6hf -l
```

Test squeezelite
```
/usr/bin/squeezelite-armv6hf -s 192.168.1.2 -n pi1 -z
```

# download autostart script
wget http://www.gerrelt.nl/RaspberryPi/squeezelitehf.sh
# edit script, only the squeezelite name needs to be changed to pi1 or something
nano squeezelitehf.sh
SL_NAME = "pi1" # needs to be uncommented

chmod u+x squeezelitehf.sh
sudo mv squeezelitehf.sh /etc/init.d/squeezelite
sudo update-rc.d squeezelite defaults

sudo /etc/init.d/squeezelite start