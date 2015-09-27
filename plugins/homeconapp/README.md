HomeConGUI
==========

This plugin provides an WebSocket interface for the HomeCon Graphical User Interface.
Right now the WebSocket interface only supports unencrypted connections. Please use a internal network or VPN to connect to the service.

# Requirements
HomeCon

# Configuration

## plugin.conf
```
[homecon]
	class_name = HomeCon
	class_path = plugins.homecon
	mysql_pass = admin

[homecongui]
	class_name = HomeConGui
	class_path = plugins.homecongui
	token = xxx
```

This plugins listens by default on every IP address of the host on the TCP port 2424.
It provides read only access to every item. By changing the `acl` attribute to `rw` or `no` you could modify this default 
The `smartvisu_dir` attribute is described in the smartVISU section.
