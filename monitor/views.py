from datetime import datetime
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from helomx.hosts.models import Mailserver, MailserverStatus
from helomx.profiles.models import Engineer
from helomx.monitor.models import PortHistory, Rtt, CheckHistory
from helomx.mxhelpers import broadcast_alert, check_port_queue

def get_blacklists(mailserver):
    #result = Blacklist.objects.all()
    blacklist_list = []
    for item in mailserver.rbl:
        blacklist_list.append(item)
    return blacklist_list

def minifyrtt(mx_obj, probe_loc, ping_time, ping_rtt, p_status):
    from monitor.models import RttMinified
    from datetime import datetime, time, timedelta, date

    t_now = datetime.now()
    t_filter = t_now.replace(minute=0)

    rtt_obj, created = RttMinified.objects.get_or_create(mailserver=mx_obj, probe=probe_loc, ping_time__gte=t_filter)
    if created == True:
        rtt_obj.ping_rtt = ping_rtt
    elif p_status == 'up' and ping_rtt > 0 and rtt_obj.ping_rtt > 0:
        rtt_obj.ping_rtt = ((rtt_obj.ping_rtt * t_now.minute) + ping_rtt) / (t_now.minute + 1)
    elif p_status == 'down':
        rtt_obj.ping_rtt = 0
    rtt_obj.ping_time = ping_time
    rtt_obj.save()

def api_feed_mx(request, probe_loc):
    from django.http import HttpResponse
    from django.core import serializers
    from mxhelpers import get_portcheck_mailservers
    mx_list = get_portcheck_mailservers(probe_loc)
    data = serializers.serialize('json', mx_list, fields=('ipaddr'))
    return HttpResponse(data, mimetype='application/json')

def api_read_mx(request):
    from django.http import HttpResponse
    if request.method == 'GET':
        ipaddr = request.GET.get('ipaddr')
        check_pk = request.GET.get('pk')
        check_port = request.GET.get('check_port')
        probe_time_epoch = request.GET.get('probe_time')
        probe_loc = request.GET.get('probe_loc')
        rtt = request.GET.get('rtt')
        if check_port == '25': # This is a mailserver object
            mx_obj = Mailserver.objects.get(pk=check_pk)
            p_status = MailserverStatus.objects.get(mailserver=mx_obj)
            try:
                port_inst = PortHistory.objects.get(mailserver=mx_obj, close_time=None)
            except:
                port_inst = None

            if (p_status.port == "down" or p_status.port == 'flap') and int(rtt) > 1:
                if p_status.port != 'flap':
                    broadcast_alert(mx_obj.ipaddr, '25', mx_obj.pk)
                check_port_queue(mx_obj)
            elif (p_status.port == "up" or p_status.port == 'flap') and int(rtt) == 0:
                if p_status.port != 'flap':
                    broadcast_alert(mx_obj.ipaddr, '25', mx_obj.pk)
                check_port_queue(mx_obj)
            elif p_status.port == "up" and port_inst:
                port_inst.close_time = datetime.now()
                port_inst.save()
            ping_time = datetime.fromtimestamp(int(probe_time_epoch))
            Rtt.objects.create(mailserver=mx_obj, probe=probe_loc, ping_rtt=rtt, ping_time=ping_time)
            minifyrtt(mx_obj, probe_loc, ping_time, rtt, p_status)
            
    return HttpResponse("OK", mimetype='text/plain')

@login_required
def check_status_json(request):
    from django.db.models import Q
    from django.http import HttpResponse
    from django.core import serializers
    if request.method == 'GET':
        slug = request.GET.get('id')
        #check_history = CheckHistory.objects.filter(Q(mailserver__slug=slug), check_type=chk_type)
        if slug:
            #data = serializers.serialize('json', Rtt.objects.filter(mailserver__slug__exact=slug).order_by('-ping_time')[:240], fields=('ping_time', 'ping_rtt', 'probe'))
            data = serializers.serialize('json', CheckHistory.objects.filter(mailserver__slug=slug), fields=('check_time', 'check_type'))
            return HttpResponse(data, mimetype='application/json')
        else:
            return HttpResponseRedirect('/error/json/')

@login_required
def detail_host(request, slug):
    from datetime import datetime, time, timedelta, date
    engineer = Engineer.objects.get(user__username=request.user.username)
    host_list = Host.objects.filter(access=engineer)
    host = Host.objects.get(slug=slug)

    if request.method == 'GET':
        new_ip = request.GET.get('ip')
        rtt_data = get_rtt(new_ip)
    return render_to_response("monitoring/detail_host.html", {                                          
                                'host_list': host_list,
                                'host': host,
                                'rtt_data': rtt_data,
                                },
                                context_instance=RequestContext(request))

@login_required
def do_chart(request, slug):
    import re
    from django.http import HttpResponse
    from mxhelpers import get_rtt_dataset

   
    mx_obj = Mailserver.objects.get(slug=slug)

    graph_dataset = get_rtt_dataset(mx_obj, request.GET.get('range'))
    #rtt_labels = graph_dataset['rtt_labels']

    
    data_temp = "t:%s|%s|%s" % (graph_dataset['sg_rtt_dataset'], graph_dataset['us_rtt_dataset'], graph_dataset['uk_rtt_dataset'])
    #au_rtt_list = re.sub("[\[\]]", '', str(graph_dataset['au_rtt_dataset']))

    #au_rtt_dataset = graph_dataset['au_rtt_dataset']
    
    #data_points = "t:%s" % re.sub("[\[\]\' ']", '', str(au_rtt_dataset))

    data_points = re.sub("[\[\]\' ']", '', str(data_temp))

    import urllib
    import urllib2
    import time


    url = 'http://chart.apis.google.com/chart?'

    #data_points = 't:40,20,50,20,100|50,20,30,40,50'

    values = {'cht' : 'lc',
              'chs' : '700x200',
              'chds' : '0,%s' % graph_dataset['max_num'],
              'chco' : '96513c,008000,2865cc',
              'chdlp' : 'b',
              'chxt' : 'x,y',
              'chxl' : '0:|%s|1:|0|%s' % (graph_dataset['rtt_labels'], graph_dataset['rtt_y_labels']),
              'chdl' : 'Singapore|United Status|United Kingdom',
              'chd' : data_points
              }


    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    #url_resp = urllib2.urlopen(req)
    #response = url_resp.read()

    from django.core.files import File
    from django.core.files.temp import NamedTemporaryFile

    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(req).read())
    img_temp.flush()

    response = HttpResponse(File(img_temp), mimetype="image/png")

    return response
