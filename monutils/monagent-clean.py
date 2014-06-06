#!/usr/bin/python
import timeit
import sys, os, socket, daemonize, time, logging
sys.path.append('/home/vhosts/helomx.com/helomx/')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from helomx.monitor.models import PortHistoryQueue
from helomx.hosts.models import Mailserver

queue_list = PortHistoryQueue.objects.all()
for item in queue_list:
    try:
        z = """\
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(('%s', 25))
        s.close()
        """ % item.mailserver.ipaddr
        t = timeit.Timer(stmt=z).timeit(number=1)*1000
        item.delete()
    except:
        pass # port is still down