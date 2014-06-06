#!/usr/bin/python
import sys
sys.path.append('/home/vhosts/helomx.com/helomx/')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime import datetime
from hosts.models import QueueAlert
from monitor.views import *
from mxhelpers import compose_sms, compose_email, generate_probe_status



# This check runs through and looks at the PortHistoryQueue list.  If
# more than two instances exist, it marks it down.
#mx_list = get_all_mailservers()
#for mx in mx_list:
#    check_port_queue(mx)


# This checks the probe statuses
generate_probe_status()

# This part goes through the QueueAlert (alerts with a delay until emailed)
# and sends any that need to be sent.  These somewhat repetitive tests are to
# determine if the reason why the alert is being sent is still true.  The alert
# gets deleted in the end.
alert_list = QueueAlert.objects.filter(delivery_time__lte=datetime.now())
for alert_item in alert_list:
    if alert_item.delivery_type == 'email':
        if (alert_item.type == 'portdown' and alert_item.mailserver.mailserverstatus_set.get().port == 'down') or (alert_item.type == 'portup' and alert_item.mailserver.mailserverstatus_set.get().port == 'up'):
            compose_email(alert_item.mailserver, alert_item.alert, alert_item.type)
        elif (alert_item.mailserver.mailserverstatus_set.get().blacklist == 'blacklisted' and alert_item.type == 'blacklist') or (alert_item.mailserver.mailserverstatus_set.get().blacklist == 'clear' and alert_item.type == 'clear'):
            compose_email(alert_item.mailserver, alert_item.alert, alert_item.type)
    elif alert_item.delivery_type == 'sms':
        if (alert_item.type == 'portdown' and alert_item.mailserver.mailserverstatus_set.get().port == 'down') or (alert_item.type == 'portup' and alert_item.mailserver.mailserverstatus_set.get().port == 'up'):
            compose_sms(alert_item.mailserver, alert_item.alert, alert_item.type)
        elif (alert_item.mailserver.mailserverstatus_set.get().blacklist == 'blacklisted' and alert_item.type == 'blacklist') or (alert_item.mailserver.mailserverstatus_set.get().blacklist == 'clear' and alert_item.type == 'clear'):
            compose_sms(alert_item.mailserver, alert_item.alert, alert_item.type)
    alert_item.delete()

