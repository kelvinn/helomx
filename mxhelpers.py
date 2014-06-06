import smtplib, sys, os
from datetime import datetime, timedelta
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from helomx.hosts.models import Mailserver, MailserverStatus, Blacklist, QueueAlert
from helomx.monitor.models import CheckHistory, BlacklistHistory, PortHistory, Rtt, RttMinified
from helomx.infolog.models import ProbeStatus

def compose_sms(mailserver, alert, type):
    import urllib2
    from urllib import quote_plus
    RECIPIENTS = []

    if type == "portdown":
        mssg = "Port %s on %s (%s) is down." % (alert, mailserver.ipaddr, mailserver.name)
    elif type == "blacklist":
        mssg = "Your server, %s (%s), is listed on %s." % (mailserver.ipaddr, mailserver.name, alert)

    message = quote_plus(mssg)
    for person in mailserver.alert_contact.all():
        if person.mobile and person.blackout_start and person.blackout_end:
            if check_sms_blacklist(person):
                RECIPIENTS.append(person.mobile)

    for mobile_num in RECIPIENTS:
        try:
            urllib2.urlopen('http://api.clickatell.com/http/sendmsg?user=USERNAME&password=PASSWORD&api_id=APIID&from=FROM&to=%s&text=%s' % (mobile_num, message))
        except:
            pass # should log error


def compose_email(mailserver, alert, type):
    
    RECIPIENTS = []
    for person in mailserver.alert_contact.all():
        RECIPIENTS.append(person.user.email)

    if type == "portup":
        mssg = "Port %s on %s (%s) is now marked as up." % (alert, mailserver.ipaddr, mailserver.name)
    elif type == "portdown":
        mssg = "Port %s on %s (%s) is down." % (alert, mailserver.ipaddr, mailserver.name)
    elif type == "blacklist":
        mssg = "Your server, %s (%s), is listed on %s." % (mailserver.ipaddr, mailserver.name, alert)

    send_mail('Mailserver Status Change', mssg, settings.DEFAULT_FROM_EMAIL,
                RECIPIENTS, fail_silently=True)
                

def daemonize(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    # Perform first fork.
    try:
        pid = os.fork( )
        if pid > 0:
            sys.exit(0) # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %sn" % (e.errno, e.strerror))
        sys.exit(1)
    # Decouple from parent environment.
    os.chdir("/tmp")
    os.umask(0)
    os.setsid( )
    # Perform second fork.
    try:
        pid = os.fork( )
        if pid > 0:
            sys.exit(0) # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %sn" % (e.errno, e.strerror))
        sys.exit(1)
    # The process is now daemonized, redirect standard file descriptors.
    for f in sys.stdout, sys.stderr: f.flush( )
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    os.dup2(si.fileno( ), sys.stdin.fileno( ))
    os.dup2(so.fileno( ), sys.stdout.fileno( ))
    os.dup2(se.fileno( ), sys.stderr.fileno( ))

@transaction.autocommit
def mark_checked(mx, chk_type, probe_loc):
    p, created = CheckHistory.objects.get_or_create(mailserver=mx, check_type=chk_type, defaults={'check_time': datetime.now()})
    if created == False:
        p.check_time = datetime.now()
        p.probe=probe_loc
        p.save()

def check_rbl(ipaddr):
    import string
    import socket
    iplist = string.split(ipaddr, ".")
    iplist.reverse()
    ip = string.join(iplist, ".")
    rbl_list = Blacklist.objects.all()
    rbl_result = []
    for item in rbl_list:
        dnsbl = ip + "." + item.site_url
        try:
            #Is blacklisted
            socket.gethostbyname( dnsbl )
            item.status = 'blacklisted'
            rbl_result.append(item)
        except socket.gaierror:
            item.status = 'clear'
            rbl_result.append(item)
    return rbl_result

def check_rtt(ipaddr):
    import timeit
    try:
        z = """\
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(('%s', 25))
        s.close()
        """ % ipaddr
        t = timeit.Timer(stmt=z).timeit(number=1)*1000
        return t
    except:
        return 0

def check_revdns(ipaddr):
    import dns.resolver
    import dns.reversename
    try:
        revdns_result = dns.resolver.query(dns.reversename.from_address(ipaddr), 'PTR')
        return revdns_result[0]
    except:
        return False

def check_relay(ipaddr):
    smtpuser = 'relaytest@helomx.com'  # for SMTP AUTH, set SMTP username here
    RECIPIENTS = ['relay@helomx.com']
    SENDER = 'relaytest@helomx.com'

    mssg = """\
    From: HeloMX Monitoring
    To:
    Subject: MX Relay Test

    This is a test message"""

    try:
        session = smtplib.SMTP(ipaddr)
        session.sendmail(SENDER, RECIPIENTS, mssg)
        return True
        diag_count = diag_count + 1
    except:
        return False

def fake_fill(mx_obj):
    probe_list = ['sg', 'uk', 'us']
    for probe in probe_list:
        Rtt.objects.create(mailserver=mx_obj, probe=probe, ping_time=datetime.now(),ping_rtt=1)

def run_diag(mx_tld, ipaddr):
    import timeit
    import dns.resolver

    diag_count = 0
    end_results = []

    # First up, RTT check

    rtt_result = check_rtt(ipaddr)
    if int(rtt_result) > 0:
        t = "%sms" % int(rtt_result)
        end_results.append(('avail_result', t))
    else:
        end_results.append(('avail_result', 'down'))
        diag_count = diag_count + 4

    # Now, relay check
    if rtt_result > 0:
        relay_check_result = check_relay(ipaddr)
        if relay_check_result:
            end_results.append(('relay_result', 'yes'))
            diag_count = diag_count + 1
        else:
            end_results.append(('relay_result', 'no'))
    else:
        end_results.append(('relay_result', 'unknown'))

    # Reverse DNS
    revdns_result = check_revdns(ipaddr)
    if revdns_result:
        end_results.append(('revdns_result', revdns_result.to_text()))
    else:
        end_results.append(('revdns_result', "no"))
        diag_count = diag_count + 1

    # Next up, blacklist check

    rbl_result = check_rbl(ipaddr)
    rbl_blk_count = rbl_result.count("blacklisted")
    diag_count = diag_count + rbl_blk_count
    end_results.append(('rbl_blk_count', rbl_blk_count))

    try:
        answers = dns.resolver.query(mx_tld, 'MX')
    except:
        answers = []
        
    # Redundant servers?
    if len(answers) > 1:
        end_results.append(('redund_result','yes'))
    else:
        end_results.append(('redund_result','no'))
        diag_count = diag_count + 1


    # Redudant servers actually work
    if len(answers) > 1:
        for mx_domain in answers:
            is_down = False
            try:
                raw_ip = dns.resolver.query(mx_domain.to_text().split(' ')[1])
                ipaddr = raw_ip[0].to_text()
                rtt_result = check_rtt(ipaddr)
                if rtt_result == 0:
                    is_down = True
                    break
            except:
                continue
        if is_down:
            diag_count = diag_count + 1
            end_results.append(('backupmxport_result','no'))
        else:
            end_results.append(('backupmxport_result','yes'))

    else:
        end_results.append(('backupmxport_result','unknown'))

    end_results.append(('diag_count', diag_count))
    return dict(end_results), rbl_result

def get_all_mailservers():
    result = Mailserver.objects.filter(active=True)
    mailserver_list = []
    for item in result:
        mailserver_list.append(item)
    return mailserver_list

def get_portcheck_mailservers(probe_loc):
    f_time = datetime.now()-timedelta(seconds=50)
    result = CheckHistory.objects.filter(mailserver__active=True, check_time__lte=f_time, check_type='port')
    result = result.exclude(probe=probe_loc)
    mailserver_list = []
    # The below only takes the first half of the resut
    for item in result[len(result)/2:]:
        mailserver_list.append(item.mailserver)
        mark_checked(item.mailserver, 'port', probe_loc)
    return mailserver_list

def get_diag_score(diag_count):
    if diag_count == 0:
        diag_score = 'A'
    elif diag_count == 1:
        diag_score = 'B+'
    elif diag_count > 1 and diag_count < 3:
        diag_score = 'B-'
    elif diag_count > 3 and diag_count < 5:
        diag_score = 'C'
    elif diag_count > 5:
        diag_score = 'F'
    else:
        diag_score = 'Unscorable'
    return diag_score

def get_mx_list(filter_company):
    return Mailserver.objects.filter(company=filter_company, active=True).order_by('name')

def get_rbl_list():
    l = []
    for rbl in Blacklist.objects.all():
        l.append((rbl.slug, rbl.name))
    return l

def get_daily_cost(filter_company):
    deduct_count = 0
    mx_list = get_mx_list(filter_company)
    for mx_obj in mx_list:
        if mx_obj.is_trial() == False:
            deduct_count = deduct_count + 0.25
    return (deduct_count)

def broadcast_alert(ipaddr, ipport, mx_pk):
    from boto.sqs.connection import SQSConnection
    from boto.sqs.message import Message

    conn = SQSConnection('ID', 'KEY')

    sg_obj = ProbeStatus.objects.get(probe='sg')
    uk_obj = ProbeStatus.objects.get(probe='uk')
    us_obj = ProbeStatus.objects.get(probe='us')

    q_uk = conn.get_queue('helomx_to_uk')
    q_sg = conn.get_queue('helomx_to_sg')
    q_us = conn.get_queue('helomx_to_us')

    m = Message()
    host_to_send = "%s:%s:%s" % (ipaddr, ipport, mx_pk)
    m.set_body(host_to_send)

    if uk_obj.status == 'up':
        q_uk.write(m)
    if sg_obj.status == 'up':
        q_sg.write(m)
    if us_obj.status == 'up':
        q_us.write(m)

def add_feed_mailserver(mx):
    from boto.sqs.connection import SQSConnection
    from boto.sqs.message import Message
    conn = SQSConnection('ID', 'KEY')
    q = conn.get_queue('mailserver_list')
    m = Message()
    m.set_body(mx.ipaddr)
    q.write(m)
    return True

def check_flapping(mx):
    from datetime import datetime, timedelta
    f_time = datetime.now()-timedelta(seconds=750)
    recent_ports = PortHistory.objects.filter(mailserver=mx, close_time__gte=f_time)
    if recent_ports.count() > 0:
        return True
    else:
        return False

def check_port_queue(mx):
    from datetime import datetime, timedelta
    #probequeue_list = ProbeQueue.objects.filter(mailserver=mx)
    p_status = MailserverStatus.objects.get(mailserver=mx)

    flap_status = check_flapping(mx)

    if flap_status == True:
        p_status.port = "flap"
        p_status.save()
    else:
        f_time = datetime.now()-timedelta(seconds=300)
        recent_rtt = Rtt.objects.filter(mailserver=mx, ping_time__gte=f_time).order_by('-ping_time')[:3]
        to_count_rtt = [elem.ping_rtt for elem in recent_rtt]
        if sum(to_count_rtt) > 0 and (p_status.port == 'down' or p_status.port == 'flap'):
            port_inst_list = PortHistory.objects.filter(mailserver=mx, close_time=None)
            for port_inst in port_inst_list:
                port_inst.close_time = datetime.now()
                port_inst.save()
            p_status.port = "up"
            p_status.save()
            # Check if emailed or not
            email_wait_time = mx.mailserverprefs_set.get().send_email_min
            if email_wait_time == 0:
                compose_email(mx, 25, "portup") # mailserver, alert, type
            else:
                q_alert = QueueAlert.objects.get(mailserver=mx, type="portdown")
                # We do this check incase the DOWN email is still in the queue.  If
                # it is, we should delete it.
                if not q_alert:
                    queue_alert('email', mx, 25, email_wait_time, "portup")
                elif q_alert:
                    q_alert.delete()
        # The port is now down
        elif sum(to_count_rtt) == 0 and (p_status.port == 'up' or p_status.port == 'flap'):
            p, created = PortHistory.objects.get_or_create(mailserver=mx, close_time=None)
            if created == True:
                p_status.port = "down"
                p_status.save()
                email_wait_time = mx.mailserverprefs_set.get().send_email_min
                if email_wait_time == 0:
                    compose_email(mx, 25, "portdown") # mailserver, alert, type
                else:
                    queue_alert('email', mx, 25, email_wait_time, "portdown")

                sms_wait_time = mx.mailserverprefs_set.get().send_page_min
                if sms_wait_time == 0:
                    compose_sms(mx, 25, "portdown")
                else:
                    queue_alert('sms', mx, 25, sms_wait_time, "portdown")
   
def queue_alert(delivery_type, mx, alert, email_wait_time, type):
    from hosts.models import QueueAlert
    delivery_time = datetime.now() + timedelta(minutes=email_wait_time)
    QueueAlert.objects.create(mailserver=mx, delivery_type=delivery_type, delivery_time=delivery_time,
                    alert=alert, type=type,
                    )

def check_sms_blacklist(engineer):
    from pytz import utc, timezone
    from datetime import datetime
    from django.contrib.auth.models import User
    eng_timezone = timezone(engineer.timezone)
    t_now = datetime.utcnow()
    c = t_now.replace(tzinfo=utc)
    k = c.astimezone(eng_timezone)
    if (k.time() < engineer.blackout_start) and (k.time() > engineer.blackout_end):
        return True
    else:
        return False

def generate_scan(probe_loc, mx_slug):
    pass

def timediff(btime, stime):
    from datetime import timedelta, time
    """Difference between two datetime.time objects
    Accepts two datetime.time objects where btime > stime
    Returns a datetime.time object of the difference in time of
    the two datetime objects.
    """
    btdelta = timedelta(hours=btime.hour, minutes=btime.minute, seconds=btime.second)
    stdelta = timedelta(hours=stime.hour, minutes=stime.minute, seconds=stime.second)
    tdiff = btdelta - stdelta
    tdiffsec = tdiff.seconds
    if tdiffsec < 60 and tdiffsec > 0:
        return time(0, 0, int(tdiffsec))
    elif tdiffsec < 3600 and tdiffsec > 0:
        tdiffsplit = str(tdiffsec/60.0).split('.')
        tdiffmin = int(tdiffsplit[0])
        tdiffsec = float("0."+tdiffsplit[1])*60
        return time(0, int(tdiffmin), int(tdiffsec))
    elif tdiffsec > 0:
        tdiffhourmin = str(tdiffsec/3600.0).split('.')
        tdiffhour = int(tdiffhourmin[0])
        tdiffminsec = str(float("0."+tdiffhourmin[1])*60).split('.')
        tdiffmin = int(tdiffminsec[0])
        tdiffsec = float("0."+tdiffminsec[1])*60
        return time(tdiffhour, tdiffmin, int(tdiffsec))
    else:
        return time(0, 0, 0)

def get_incidents(company):
    open_avail_history = PortHistory.objects.filter(mailserver__company=company, mailserver__active=True, close_time=None).order_by('-add_time')
    open_blacklist_history = BlacklistHistory.objects.filter(mailserver__company=company, mailserver__active=True, close_time=None).order_by('-add_time')
    #result = list(open_avail_history) + list(open_blacklist_history)

    # Return a mailserver, message, and date
    return list(open_blacklist_history), list(open_avail_history)

def get_availability(mx, disp_range):
    from datetime import datetime, time, timedelta, date
    result = get_object_or_404(Mailserver, slug=mx.slug)
    total_avail = 60
    now = datetime.now()
    datetime.now()
    now.hour - 1
    today = datetime.today()
    for p in PortHistory.objects.filter(mailserver=result, add_time__gte=10):
        #port.total_time = time(0, 0, 0)
        t_diff = timediff(p.close_time, p.add_time)
        try:
            if p.add_time.day == p.close_time.day:
                total_avail = total_avail - timediff(now, p.add_time)
            else:
               pass
        except:
            # alert still open
            if p.add_time.day == now.day:
                t_diff = timediff(now, p.add_time)
                total_avail = total_avail - timediff(now, p.add_time)
            else:
                # still open
                p_temp = datetime(p.add_time.year, p.add_time.month, p.add_time.day+1)
                while p.add_time.day < now.day:
                    t_diff = timediff(p_temp, datetime(p.add_time.year, p.add_time.month, p.add_time.day, p.add_time.hour, p.add_time.minute, p.add_time.second+1))
                    d[p.add_time.date().isoformat()] = d[p.add_time.date().isoformat()] - (t_diff.hour*60 + t_diff.minute)
                    p.add_time = p_temp
                    p_temp = datetime(p.add_time.year, p.add_time.month, p.add_time.day+1)
                if p.add_time.day == now.day:
                    t_diff = timediff(now, p.add_time)
                    d[p.add_time.date().isoformat()] = d[p.add_time.date().isoformat()] - (t_diff.hour*60 + t_diff.minute)
    return d

def compose_probe_alert(probe_loc):
    import urllib2
    from urllib import quote_plus

    mssg = "Probe %s is down." % probe_loc

    message = quote_plus(mssg)

    mobile_num = '61429654255'

    try:
        urllib2.urlopen('')
        import xmlrpclib
        probeurl = "http://helomx:abcde@%s.helomx.com:9001" % probe_loc
        s = xmlrpclib.ServerProxy(probeurl)
        s.supervisor.stopProcess('helomx')
        s.supervisor.startProcess('helomx')
    except:
        pass # should log error

def generate_probe_status():
    pid = os.fork()
    if pid == 0:
        import dateutil.parser
        from datetime import datetime, time, timedelta, date

        disp_range = 5
        t_now = datetime.now()
        filter_time = t_now - timedelta(minutes=disp_range)

        rtt_temp_list = Rtt.objects.filter(ping_time__gte=filter_time)
        sg_obj = ProbeStatus.objects.get(probe='sg')
        uk_obj = ProbeStatus.objects.get(probe='uk')
        us_obj = ProbeStatus.objects.get(probe='us')

        if rtt_temp_list:
            probe_temp = []
            for item in rtt_temp_list: probe_temp.append(item.probe)

            if probe_temp.count('sg') > 0 and sg_obj.status == 'down':
                sg_obj.status = 'up'
                sg_obj.save()
            elif probe_temp.count('sg') == 0 and sg_obj.status == 'up':
                if sg_obj.alerted == False:
                    compose_probe_alert('sg')
                    sg_obj.alerted = True
                sg_obj.status = 'down'
                sg_obj.save()

            if probe_temp.count('uk') > 0 and uk_obj.status == 'down':
                uk_obj.status = 'up'
                uk_obj.save()
            elif probe_temp.count('uk') == 0 and uk_obj.status == 'up':
                if uk_obj.alerted == False:
                    compose_probe_alert('uk')
                    uk_obj.alerted = True
                uk_obj.status = 'down'
                uk_obj.save()

            if probe_temp.count('us') > 0 and us_obj.status == 'down':
                us_obj.status = 'up'
                us_obj.save()
            elif probe_temp.count('us') == 0 and us_obj.status == 'up':
                if us_obj.alerted == False:
                    compose_probe_alert('us')
                    us_obj.alerted = True
                us_obj.status = 'down'
                us_obj.save()

        elif len(rtt_temp_list) == 0:
            sg_obj.status = 'down'
            sg_obj.save()
            uk_obj.status = 'down'
            uk_obj.save()
            us_obj.status = 'down'
            us_obj.save()
        del(rtt_temp_list)
        os._exit(0)
    os.waitpid(pid, os.P_WAIT)
    return True

def chunk_avg(a,b,length=8):
    try:
        if len(a[-1]) == length:
            a.append([b])
            return a
        else:
            a[-1].append(b)
            return a
    except:
        return [sum(a,b)/length]


def get_rtt_dataset(mx, disp_range):
    import dateutil.parser
    from datetime import datetime, time, timedelta, date

    rtt_list_len = 0
    
    if disp_range:
        t_now = datetime.now()
        if disp_range == 'hourly':
            filter_time = t_now - timedelta(hours=1)
            rtt_list = Rtt.objects.filter(mailserver=mx, ping_time__gte=filter_time).order_by('ping_time')

        elif disp_range == 'daily':
            filter_time = t_now - timedelta(days=1)
            rtt_list = Rtt.objects.filter(mailserver=mx, ping_time__gte=filter_time).order_by('ping_time')

        elif disp_range == 'weekly':
            filter_time = t_now - timedelta(weeks=1)
            rtt_list = RttMinified.objects.filter(mailserver=mx, ping_time__gte=filter_time).order_by('ping_time')
        elif disp_range == 'monthly':
            filter_time = t_now - timedelta(weeks=4)
            rtt_list = RttMinified.objects.filter(mailserver=mx, ping_time__gte=filter_time).order_by('ping_time')
        rtt_list_len = len(rtt_list)
        
    if rtt_list_len > 0:
        rtt_labels = '%s|%s|%s|%s|%s' % (
                            rtt_list[0].ping_time.strftime("%b %d %I:%M%p"),
                            rtt_list[int(rtt_list_len*.25)].ping_time.strftime("%b %d %I:%M%p"),
                            rtt_list[int(rtt_list_len*.5)].ping_time.strftime("%b %d %I:%M%p"),
                            rtt_list[int(rtt_list_len*.75)].ping_time.strftime("%b %d %I:%M%p"),
                            rtt_list[rtt_list_len-1].ping_time.strftime("%b %d %I:%M%p")
                            )



        #rtt_query_au = RttMinified.objects.filter(mailserver=mx, probe='au', ping_time__gte=filter_time)
        #rtt_query_us = RttMinified.objects.filter(mailserver=mx, probe='au', ping_time__gte=filter_time)
        #rtt_query_uk = RttMinified.objects.filter(mailserver=mx, probe='au', ping_time__gte=filter_time)



        sg_rtt_dataset = rtt_list.filter(probe='sg').values_list('ping_rtt', flat=True)
        us_rtt_dataset = rtt_list.filter(probe='us').values_list('ping_rtt', flat=True)
        uk_rtt_dataset = rtt_list.filter(probe='uk').values_list('ping_rtt', flat=True)

            
        #au_rtt_dataset = au_rtt_temp[:100]
        #us_rtt_dataset= us_rtt_temp[:100]
        #uk_rtt_dataset = uk_rtt_temp[:100]
        #au_rtt_dataset = [elem['ping_rtt'] for elem in rtt_list if elem['probe'] == "au"]
        #us_rtt_dataset = [elem['ping_rtt'] for elem in rtt_list if elem['probe'] == "us"]
        #uk_rtt_dataset = [elem['ping_rtt'] for elem in rtt_list if elem['probe'] == "uk"]

        #au_rtt_dataset = smoothListGaussian(au_rtt_temp)
        #us_rtt_dataset = smoothListGaussian(us_rtt_temp)
        #uk_rtt_dataset = smoothListGaussian(uk_rtt_temp)

        try:
            # This gets the max of the max in each dataset
            max_num = max(max(sg_rtt_dataset), max(us_rtt_dataset), max(uk_rtt_dataset))
            rtt_y_labels = '%s|%s|%s|%s' % (max_num*.25, max_num*.5, max_num*.75, max_num)
        except:
            max_num = 0
        dataset = {'rtt_labels': rtt_labels,
                'rtt_y_labels': rtt_y_labels,
                'sg_rtt_dataset': list(sg_rtt_dataset),
                'us_rtt_dataset': list(us_rtt_dataset),
                'uk_rtt_dataset': list(uk_rtt_dataset),
                'max_num': max_num }
        return dataset
    else:
        return None
