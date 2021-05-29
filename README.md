# arpgen
Python tool to generate gratuitous ARPS by Patrick Kutch

Sometimes when doing DPDK testing I tire of having to setup VLANs so I don't cause a broadcast storm.  This utility allows you to tell the switch which port a MAC address should be associated with by sending gratuitous ARPS.

Real use (for me) is when I want to use DPDK on SR-IOV VFs.  I use this utility to send gratitous ARPs from the PF to the switch specifying the VF's MAC address.  

For example, I have  PF called 'enp24s0f0' and it has the following VFs:
~~~
4: enp24s0f0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether 68:05:ca:a3:7a:80 brd ff:ff:ff:ff:ff:ff
    vf 0 MAC ae:28:e4:e8:1c:fe, spoof checking on, link-state auto, trust off
    vf 1 MAC be:c1:29:bb:b3:8d, spoof checking on, link-state auto, trust off
    vf 2 MAC a6:90:bb:8c:8a:f1, spoof checking on, link-state auto, trust off
    vf 3 MAC ee:77:19:05:43:4a, spoof checking on, link-state auto, trust off
~~~
To 'tell' the switch that VF0 traffic goes to same switch port as the PF, do this:
~~~
arpgen.py -m ae:28:e4:e8:1c:fe -d enp24s0f0 
~~~
Which will associate the MAC of VF0 to the same port as the PF, and a default IP address of 1.1.1.1.  If you want to also program the switch with an IP address:
~~~
arpgen.py -m ae:28:e4:e8:1c:fe -d enp24s0f0 -a 100.100.100.32
~~~
You can also specify multiple MAC addresses, for example VF0 and VF1:
~~~
/arpgen.py -m ae:28:e4:e8:1c:fe be:c1:29:bb:b3:8d -d enp24s0f0 
~~~
You can also specify more than one IP for a 1:1 relationship
~~~
/arpgen.py -m ae:28:e4:e8:1c:fe be:c1:29:bb:b3:8d -d enp24s0f0 -a 100.100.100.125 100.100.100.133 -i 1 
~~~
Which will specify 100.100.100.125 be associated with VF0 MAC and  100.100.100.133 with VF1 MAC and sent at an interval of one secone
~~~
/arpgen.py -m ae:28:e4:e8:1c:fe be:c1:29:bb:b3:8d a6:90:bb:8c:8a:f1 -d enp24s0f0 -a 100.100.100.125 100.100.100.133 -i 1 
~~~
Will do the same as the previous example, but will also send a gratuitous ARP for VF3 MAC with default IP of 1.1.1.1