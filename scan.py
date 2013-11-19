#! /usr/bin/python
# http://resources.infosecinstitute.com/port-scanning-using-scapy/

from scapy.all import *

dst_ip = "192.168.1.1"
src_port = RandShort()
dst_port=80
tcp_connect_scan_resp = (sr1(IP(dst=dst_ip) /
                    TCP(sport=src_port,dport=dst_port,flags="S"),timeout=10))
if tcp_connect_scan_resp is None:
    print "Closed"
elif tcp_connect_scan_resp.haslayer(TCP):
    if tcp_connect_scan_resp.getlayer(TCP).flags == 0x12:
        send_rst = (sr(IP(dst=dst_ip) /
               TCP(sport=src_port,dport=dst_port,flags="AR"),timeout=10))
    print "Open"
elif tcp_connect_scan_resp.getlayer(TCP).flags == 0x14:
    print "Closed"
