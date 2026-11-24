#!/bin/sh
iptables -t nat -A OUTPUT -d 127.0.80.80 -p tcp  --dport 80 -j DNAT --to-destination 127.0.80.80:8080

