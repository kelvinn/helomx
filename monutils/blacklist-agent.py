#!/usr/bin/python
import sys, socket
sys.path.append('/home/vhosts/helomx.com/helomx/')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from monitor.views import *
from hosts.models import MailserverStatus
from monitor.models import BlacklistHistory
from mxhelpers import compose_email, mark_checked, get_all_mailservers, queue_alert
import string
from datetime import datetime

def unmark_blk(mx_obj, rbl_obj):
    b_rbl, created_rbl = mx_obj.mailserverrblstatus_set.get_or_create(rbl=rbl_obj)
    if created_rbl == True:
        b_rbl.status = 'clear'
        b_rbl.save()

    elif b_rbl.status == 'blacklisted':
        b_rbl.status = 'clear'
        b_rbl.save()
        b_rbl_count = mx_obj.mailserverrblstatus_set.filter(status='blacklisted')
        if b_rbl_count.count() == 0:
            blacklist_hist = BlacklistHistory.objects.get(mailserver=mx_obj, close_time=None)
            blacklist_hist.close_time = datetime.now()
            blacklist_hist.save()
            mx_status = MailserverStatus.objects.get(mailserver=mx_obj)
            mx_status.blacklist = 'clear'
            mx_status.save()

def mark_blk(mx_obj, rbl_obj):
    b_hist, created = BlacklistHistory.objects.get_or_create(mailserver=mx_obj, close_time=None)
    mx_status = MailserverStatus.objects.get(mailserver=mx_obj)

    # The following tests if this is a new detected blacklist or not
    # If it is, we just add it to the list.  If not, we return out of the
    # function so we don't keep writing to the database.
    b_rbl, created_rbl = mx_obj.mailserverrblstatus_set.get_or_create(rbl=rbl_obj)
    if b_rbl.status == 'clear':
        b_rbl.status = 'blacklisted'
        b_rbl.save()
        b_hist.rbl.add(rbl_obj) # Adds rbl to history

    if created or mx_status.blacklist == 'clear':
        mx_status.blacklist = 'blacklisted'
        mx_status.save()
        # If the mailserver goes from clear->blacklist, it is the first
        # time the blacklist happened, so alert the client.
        email_wait_time = mx_obj.mailserverprefs_set.get().send_email_min
        if email_wait_time == 0:
            compose_email(mx_obj, rbl_obj.name, 'blacklist')
        else:
            queue_alert('sms', mx_obj, rbl_obj.name, email_wait_time, "blacklist")


def blacklist_check( mx_obj ):
    # turn "1.2.3.4" into "4.3.2.1.sbl-xbl.spamhaus.org"
    # object = mailserver item
    iplist = string.split(mx_obj.ipaddr, ".")
    iplist.reverse()
    ip = string.join(iplist, ".")

    for item in mx_obj.rbl.all():
        dnsbl = ip + "." + item.site_url
        try:
            #Is blacklisted
             socket.gethostbyname( dnsbl )
             mark_blk(mx_obj, item)
        except socket.gaierror:
             unmark_blk(mx_obj, item)

def check_bad_mx(mailservers):
    #answers = dns.resolver.query(str(item.url), 'MX')
    #answers = item.mailserver.all()
    for object in mailservers:
        blacklist_check(object)
        mark_checked(object, 'blacklist', 'us')

if __name__ == "__main__":
    mailservers = get_all_mailservers()
    check_bad_mx(mailservers)
