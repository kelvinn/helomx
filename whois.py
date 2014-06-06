import sys
import re
import socket


def whois_lookup(domain_obj):
    whois = "whois.internic.net"
    str = ""
    desen = re.compile(r'Expiration Date: ([0-9]{1,2}-[a-z]{1,3}-[0-9]{4})')
    desen2 = re.compile('No match for')
    s = socket.socket()
    try:
        s.connect( ( whois, 43 ) )
        s.send(domain_obj+'\n')
    except socket.error, msg1:
        print msg1


    while 1:
        try:
            data = s.recv( 1024 )
        except socket.error, msg2:
            print msg2

        if data:
            str=str+data
        else:
            break

    s.close()
    m = desen.search(str)
    m2 = desen2.search(str)
    if not m2:
        if m:
            print m.group(1)
