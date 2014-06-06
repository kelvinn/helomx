#!/usr/bin/python
import sys
sys.path.append('/home/vhosts/helomx.com/helomx/')

from django.core.management import setup_environ
import settings
setup_environ(settings)


from monitor.models import Rtt
from datetime import datetime, time, timedelta, date

t_now = datetime.now()

x = 300
while x > 45:
    t_filter = t_now - timedelta(days=x)
    rtt_list = Rtt.objects.filter(ping_time__lte=t_filter)
    rtt_list.delete()
    print x
    x = x - 5
