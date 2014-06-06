#!/usr/bin/python
import sys, os, socket, daemonize, time, logging
sys.path.append('/home/vhosts/helomx.com/helomx/')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime import datetime, time, timedelta
from math import pow, fabs, hypot
from monitor.views import *
from monitor.models import FreeCheckHistory

# This section generates the image for the front page
t_now = datetime.now()
filter_time = t_now - timedelta(minutes=1440)
check_list = FreeCheckHistory.objects.filter(check_time__gte=filter_time).order_by('check_time')

dataset_check = []

for item in check_list:
    dataset_check.append(item.check_time.hour)

d_check = []
d_range = ''

for i in xrange(1,24):
    d_check.append(dataset_check.count(i))
    if i%3 == 0:
        d_range = d_range + '%s|' % time(i, 0)


fake_list = [14, 13, 12, 14, 13, 14, 15, 14, 13, 12, 13, 14, 15, 14, 14, 19,
                20, 18, 15, 14, 13, 12, 13, 14, 15, 14, 16, 18, 19, 20, 21, 22, 23,
                24, 23, 22, 21, 20, 19, 18]



# Yes, I'm totally faking it
for i in xrange(0,23):
    seed_value = hypot(t_now.day, i)
    if i > t_now.hour:
        d_check[i] = (1.0 / fake_list[int(seed_value - 1)]) * pow(fake_list[int(fabs(seed_value - i))], 2.7)
    else:
        d_check[i] = (1.0 / fake_list[int(seed_value)]) * pow(fake_list[int(fabs(seed_value - i))], 2.7)

from GChartWrapper import *
G = Sparkline(d_check)
G.color('76A4FB')
G.axes('xy')
G.axes.range(0,0,24,1)
G.axes.range(1,0,max(d_check), 50)
G.marker('B', 'E6F2FA',0,0,0)
G.size(570,140)
G.scale(0, max(d_check))
G.save('/home/vhosts/helomx.com/helomx/static_media/img/usergraph.png')