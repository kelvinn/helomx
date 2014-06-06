#!/usr/bin/python
import sys
sys.path.append('/home/vhosts/helomx.com/helomx/')

from django.core.management import setup_environ

import settings
setup_environ(settings)

from django.db import connection
from hosts.models import MailserverStatus
from mxhelpers import run_diag, get_all_mailservers, mark_checked, get_diag_score

rbl_result=None
ipaddr = None
relay_result = None
avail_result=None
redund_result=None
diag_score=None
revdns_result = None


def run_tests(mx_obj):
    try:
        end_results, rbl_result = run_diag(mx_obj.mx_url, mx_obj.ipaddr)
        p_status, created = MailserverStatus.objects.get_or_create(mailserver=mx)
        if created == False:
            p_status.relay = end_results['relay_result']
            p_status.backupmx = end_results['redund_result']
            p_status.backupmxport = end_results['backupmxport_result']
            p_status.score = get_diag_score(end_results['diag_count'])
            if end_results['revdns_result'] is not "no":
                p_status.revdns = "yes"
            else:
                p_status.revdns = "no"
            p_status.save()
    except:
        end_results = None
        
mx_list = get_all_mailservers()
for mx in mx_list:
    run_tests(mx)
    connection.close()
    mark_checked(mx, 'misc', 'us')