
# Configuring Persistent IP Address

In SpinView, click on the camera in the top left menu. It's a good idea to start off by selecting the camera and running the suggested "Auto Force IP" so that SpinView can properly communicate with the camera.

First, observe the current subnet mask and IP address by dropping down "Blackfly S BFS-PGE-50S5C" (will say your model), then "Transport Layer Control", then "GigE Vision". Take note of the "Current IP Address" and "Current Subnet Mask", if those are important to you.

To set a custom and persistent IP address, subnet mask, and gateway, first determine what you want these values to be. Then convert the octets to integers by running our helper script `persistent_ip_octet.py`. For example,

```
$ python persistent_ip_octet.py --ip 192.168.1.1 --subnet 255.255.255.0 --gateway 0.0.0.0

ip       : integer for octet 192.168.1.1     is 3232235777
subnet   : integer for octet 255.255.255.0   is 4294967040
gateway  : integer for octet 0.0.0.0         is 0
```

To set these permanently, navigate back to the same GigE Vision tab then input the integers into "Persistent IP Address", "Persistent Subnet Mask" and "Persistent Default Gateway". Restart the device by unplugging and replugging and you should see the new IP address automatically initialize.