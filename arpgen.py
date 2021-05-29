#!/usr/bin/env python
##############################################################################
#  Copyright (c) 2021 Intel Corporation
# 
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
##############################################################################
#    File Abstract: 
#    simple utility to send gratituitous ARPs.  Useful when doing L2 DPDK testing
##############################################################################
from __future__ import print_function
import signal
import sys
    
from time import sleep
import argparse

BCAST_MAC = 'ff:ff:ff:ff:ff:ff'
_Version = "5.28.21 Build 1"
pktCnt = 1

try:
    from scapy.all import * # pylint: disable=unused-import, unused-wildcard-import
except:
    print("Arp Generator v" + _Version +"\nERROR: SCAPY library must be installed: 'pip install scapy'")
    sys.exit()


def create_ARP_request_gratuituous(MAC_ADDR,ipaddr):
    #op=2 means 'is at'
    arp = ARP(psrc=ipaddr,hwsrc=MAC_ADDR,pdst=ipaddr,hwdst=BCAST_MAC,op=2)
              
    return Ether(dst=BCAST_MAC) / arp
    

def signal_handler(sig, frame):
    global pktCnt

    print("Sent {} gratitous ARP packets".format(pktCnt))
    sys.exit(0)


def main():
    defaultIP = '1.1.1.1'
    parser = argparse.ArgumentParser(description='Arp Generator v' + _Version,usage='''arpgen -m mac1 [mac2 mac2] -a ip1 [ip2 ipn] -d dev
    if you specify more MAC addresses than IP addresses, the default IP of 1.1.1.1 will be used
    if you specify more IP addresses than MAC addressed, the last MAC address specified will be used''')
    parser.add_argument("-m","--mac",help="List of 1+ MAC addresses to broadcast",type=str,nargs='+',required=True)
    parser.add_argument("-a","--addr",help="List IP Addresses to advertise via gratitous ARP",nargs='+',type=str,default=[defaultIP,])
    parser.add_argument("-d","--dev",help="Device to send gratitous over",type=str,required=True)
    parser.add_argument("-i","--interval",help="Frequency (in seconds) to send gratitous ARP, default is 10",type=int,default=10)
    parser.add_argument("-q","--quiet",help="Does not print anything while running.",action='store_true')

    args = parser.parse_args()
    
    interval = args.interval
    dev = args.dev
    
    signal.signal(signal.SIGINT, signal_handler)
    
    arpPktList=[]
    if len(args.mac) >= len(args.addr):
        index = 0
        for mac in args.mac:
            if index < len(args.addr):
                ip = args.addr[index]
                index += 1
            else:
               ip = defaultIP
            print(ip)
            arpPkt = create_ARP_request_gratuituous(mac,ip)
            if not args.quiet:
                arpPkt.show2()
            arpPktList.append(arpPkt)
            
    else:
        index = 0
        for ip in args.addr:
            mac = args.mac[index]
            if index +1 < len(args.mac):
                index += 1
            
            arpPkt = create_ARP_request_gratuituous(mac,ip)
            arpPkt.show2()
            arpPktList.append(arpPkt)
    
    try:
        for arpPkt in arpPktList:
            macAddr = arpPkt.hwsrc
            ipAddr = arpPkt.psrc
            if not args.quiet:
                print("Sending gratitous arp on {} with SrcIP: {} MAC: {}".format(dev,ipAddr,macAddr))
            sendp(arpPkt,iface=dev,verbose=False)
    except:
        print("Error sending gratitous ARP, please confirm parameters")
        return
    
    print('Press Ctrl+C to exit')    
    
    global pktCnt
    while True:
        try:
            sleep(interval)
            for arpPkt in arpPktList:
                macAddr = arpPkt.hwsrc
                ipAddr = arpPkt.psrc

                if not args.quiet:
                    print("Sending gratitous arp on {} with SrcIP: {} MAC: {}".format(dev,ipAddr,macAddr))
                sendp(arpPkt,iface=dev,verbose=False)
                pktCnt += 1
        except Exception as ex:
            print(str(ex))
            break
            
    print("Sent {} gratitous ARP packets".format(pktCnt))

if __name__ == "__main__":
    main()

