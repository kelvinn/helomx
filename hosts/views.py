import string
import socket
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from helomx.hosts.models import Mailserver, MailserverStatus, MailserverPrefs, Blacklist
from helomx.monitor.models import BlacklistHistory, MailserverRblStatus, Rtt, PortHistory
from helomx.profiles.models import Engineer
from helomx.forms import MailserverForm, AddCompanyForm, UpdateNameForm
from mxhelpers import get_mx_list, get_incidents, add_feed_mailserver, run_diag, mark_checked
from django.template.defaultfilters import slugify

@login_required
def add_mailserver(request):
    from datetime import datetime
    from datetime import timedelta
    from mxhelpers import fake_fill
    engineer = Engineer.objects.get(user__username=request.user.username)
    mailserver_list = get_mx_list(engineer.company)
    message = None
    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)
    if request.method == 'POST':
        site_form = MailserverForm(request.POST)
        if site_form.is_valid():
            if request.user.is_authenticated():
                mx_url=site_form.cleaned_data['mx_url']
                ipaddr=site_form.cleaned_data['ipaddr']
                new_mailserver = Mailserver(name=site_form.cleaned_data['name'],
                                      slug=slugify(site_form.cleaned_data['name']),
                                      company=engineer.company,
                                      mx_url=mx_url,
                                      ipaddr=ipaddr,
                                      )
                new_mailserver.save()
                new_mailserver.alert_contact.add(engineer)

                
                MailserverPrefs.objects.create(mailserver=new_mailserver)
                rbl_all = Blacklist.objects.all()
                for rbl_obj in rbl_all:
                    new_mailserver.rbl.add(rbl_obj)
                    mx_status = MailserverRblStatus(mailserver=new_mailserver, rbl=rbl_obj, status='clear')
                    mx_status.save()
                end_results, rbl_result = run_diag(mx_url, ipaddr)

                if end_results['revdns_result'] is not "no":
                    revdns_status = "yes"
                else:
                    revdns_status = "no"
                    
                MailserverStatus.objects.create(mailserver=new_mailserver, port="up",
                    blacklist="clear", webmail="up", relay=end_results['relay_result'],
                    backupmx=end_results['redund_result'], backupmxport=end_results['backupmxport_result'], revdns=revdns_status)

                add_feed_mailserver(new_mailserver)
                fake_fill(new_mailserver) # DO NOT remove.
                mark_checked(new_mailserver, 'port', 'us') # DO NOT remove
                
                message = "Mailserver has been created successfully."
                site_form = MailserverForm() # this clears the form to add more
    else:
        site_form = MailserverForm()
    return render_to_response("hosts/add_mailserver.html", {
                                'mailserver_form': site_form,
                                'mailserver_list': mailserver_list,
                                'message': message,
                                'company': company,
                                'engineer_list': engineer_list,
                                },
                                context_instance=RequestContext(request))

@login_required
def upt_mailserver(request, slug):
    from forms import UptMailserverForm, MailserverPrefsForm
    engineer = Engineer.objects.get(user__username=request.user.username)
    mailserver_list = get_mx_list(engineer.company)
    mx = Mailserver.objects.get(slug=slug)
    form = UptMailserverForm(mx, instance=mx)
    threshold_form = MailserverPrefsForm(instance=mx.mailserverprefs_set.get())
    message = None
    
    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)
    if request.method == 'POST':
        form = UptMailserverForm(mx, data=request.POST, instance=mx)
        threshold_form = MailserverPrefsForm(request.POST)
        form.user = engineer.user
        if form.is_valid():
            message = "Mailserver details updated successfully"
            form.save()
            name = form.cleaned_data['name']
            mx.slug = slugify(name)
            mx.save()
            add_feed_mailserver(mx)
            threshold_form = MailserverPrefsForm(data=request.POST, instance=mx.mailserverprefs_set.get())
            threshold_form.save()
            
    return render_to_response("hosts/update_mailserver.html", {
                                'mx': mx,
                                'form': form,
                                'threshold_form': threshold_form,
                                'mailserver_list': mailserver_list,
                                'message': message,
                                'company': company,
                                'engineer_list': engineer_list,
                                },
                                context_instance=RequestContext(request)) 
         
@login_required
def delete_mailserver(request, slug):
    engineer = Engineer.objects.get(user__username=request.user.username)
    mailserver_list = get_mx_list(engineer.company)
    mx = Mailserver.objects.get(slug=slug)
    message = None
    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)
    if request.method == 'POST':
        if request.user.is_authenticated():
            mx = Mailserver.objects.get(slug=slug)
            mx.active = False
            mx.save()
            return HttpResponseRedirect('/dashboard/?success=mailserver')

    return render_to_response("hosts/delete_mailserver.html", {
                                'mailserver_list': mailserver_list,
                                'message': message,
                                'company': company,
                                'engineer_list': engineer_list,
                                'mx': mx,
                                },
                                context_instance=RequestContext(request)) 
    
    
    
@login_required
def rtt_json_update(request):
    from django.http import HttpResponse
    from django.core import serializers
    if request.method == 'GET':
        slug = request.GET.get('mx')
        disp_range = request.GET.get('range')

        if slug:
            if (disp_range == '60'):
                data = serializers.serialize('json', Rtt.objects.filter(mailserver__slug__exact=slug).order_by('-ping_time')[:240], fields=('ping_time', 'ping_rtt', 'probe'))
                return HttpResponse(data, mimetype='application/json')

        else:
            return HttpResponseRedirect('/error/json/')

@login_required
def add_credit(request):
    from datetime import datetime
    from datetime import timedelta
    engineer = Engineer.objects.get(user__username=request.user.username)
    mailserver_list = get_mx_list(engineer.company)
    message = None
    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)
    return render_to_response("hosts/add_credit.html", {
                                'mailserver_list': mailserver_list,
                                'message': message,
                                'company': company,
                                'engineer_list': engineer_list,
                                },
                                context_instance=RequestContext(request))

@login_required
def realtime_json(request):
    if request.user:
        engineer = Engineer.objects.get(user__username=request.user.username)

        if engineer:

            open_blacklist_history, open_avail_history = get_incidents(engineer.company)
            data = []
            for obj in open_blacklist_history:
                msg = "%s on %s was marked BLACKLISTED" % (obj.mailserver.name, obj.add_time)
                data.append(msg)
            for obj in open_avail_history:
                msg = "%s on %s was marked DOWN" % (obj.mailserver.name, obj.add_time)
                data.append(msg)
            return render_to_response("hosts/realtime_result.html", {
                        'alert_list': data,
                        },
                        context_instance=RequestContext(request))


@login_required
def addtime_json(request):
    from django.http import HttpResponse
    from django.core import serializers
    from datetime import timedelta
    if request.method == 'GET':
        mx_name = request.GET.get('mx')
        credit_amt = request.GET.get('amt')
        engineer = Engineer.objects.get(user__username=request.user.username)
        company = engineer.company
        mx_obj = Mailserver.objects.get(name=mx_name)
        if mx_obj:
            credit_obj = Credit.objects.get(company=company)
            credit_obj.credit_left = credit_obj.credit_left - int(credit_amt)
            credit_obj.save()
            mx_obj.expiry_date = mx_obj.expiry_date+timedelta(days=credit_amt)
            mx_obj.save()
            
def diagnostic_json(request):
    from django.http import HttpResponse
    from django.core import serializers
    data = []
    if request.method == 'GET':
        ipaddr = request.GET.get('ipaddr')
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
                rbl_result.append([item.name, 'Blacklisted'])
            except socket.gaierror:
                rbl_result.append([item.name, 'Clear'])



        return HttpResponse(data, mimetype='application/json')
    else:
        return HttpResponseRedirect('/error/json/')
    
@login_required
def realtime(request):
    from django.http import HttpResponse
    from django.core import serializers

    return render_to_response("hosts/realtime.html", {

                                },
                                context_instance=RequestContext(request))

@login_required
def detail_mx(request, slug):
    from mxhelpers import get_rtt_dataset, get_availability, run_diag, get_diag_score
    from django.http import HttpResponse
    from django.core import serializers
    engineer = Engineer.objects.get(user__username=request.user.username)
    mailserver_list = get_mx_list(engineer.company)
    mx_obj = Mailserver.objects.get(slug=slug)
    blacklist_history = BlacklistHistory.objects.filter(mailserver=mx_obj).order_by('-close_time')
    avail_history = PortHistory.objects.filter(mailserver=mx_obj)
    blacklist_status = MailserverRblStatus.objects.filter(mailserver=mx_obj)
    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)
    dataset = None
    rtt_labels = None
    scale_num = None
    img_url = None
    message = None

    end_results = MailserverStatus.objects.get(mailserver=mx_obj)


    if request.method == 'GET':   
        if request.GET.get('range'):
            disp_range = request.GET.get('range')
        else:
            disp_range = 'hourly'





    return render_to_response("hosts/detail_mx.html", {
                                'message': message,
                                'mailserver_list': mailserver_list,
                                'mx': mx_obj,
                                'company': company,
                                'disp_range': disp_range,
                                'engineer_list': engineer_list,
                                'blacklist_history': blacklist_history,
                                'avail_history': avail_history,
                                'blacklist_status': blacklist_status,
                                'redund_result': end_results.backupmx,
                                'backupmxport_result': end_results.backupmxport,
                                'relay_result': end_results.relay,
                                'avail_result': end_results.port,
                                'revdns_result': end_results.revdns,
                                'diag_score': end_results.score,
                                },
                                context_instance=RequestContext(request))

def diag_html(request):
    import timeit
    import smtplib
    import dns.resolver
    from datetime import datetime
    from monitor.models import FreeCheckHistory
    from mxhelpers import check_relay, check_rbl, check_rtt, get_diag_score
    
    rbl_result=None
    ipaddr = None
    diag_score=None

    if request.method == 'GET':
        mx_domain = request.GET.get('mx')
        mx_tld = request.GET.get('tld')
        if mx_domain:

            raw_ip = dns.resolver.query(mx_domain)

            ipaddr = raw_ip[0].to_text()

            end_results, rbl_result = run_diag(mx_tld, ipaddr)

            # Lastly, calculate the score
            diag_score = get_diag_score(end_results['diag_count'])

            try:
                checker_ip = request.META.get("REMOTE_ADDR", "")
                # this is for the counter on the front page
                b = FreeCheckHistory(ipaddr=ipaddr, checker=checker_ip)
                b.save()
            except:
                pass

    return render_to_response("hosts/diag_result.html", {
                        'rbl_result': rbl_result,
                        'ipaddr': ipaddr,
                        'redund_result': end_results['redund_result'],
                        'relay_result': end_results['relay_result'],
                        'avail_result': end_results['avail_result'],
                        'revdns_result': end_results['revdns_result'],
                        'diag_score': diag_score,

                        },
                        context_instance=RequestContext(request))

def free_diag(request):
    import timeit
    import dns.resolver
    from forms import DiagnosticForm
    
    diag_form = DiagnosticForm()
    pick_mx=None
    domain=None

    if request.method == 'POST':
        diag_form = DiagnosticForm(request.POST)
        if diag_form.is_valid():
            domain = diag_form.cleaned_data['domain']
            answers = dns.resolver.query(domain, 'MX')
            #if len(answers) > 1:
                # need to pick one
                # TODO: if user has only one MX, go straight to it
            pick_mx = []
            for rdata in answers:
                raw_ip = dns.resolver.query(rdata.exchange.to_text().strip('.'))
                ipaddr = raw_ip[0].to_text()
                try:
                    z = """\
                    import socket
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2.0)
                    s.connect(('%s', 25))
                    s.close()
                    """ % ipaddr
                    t = timeit.Timer(stmt=z).timeit(number=1)*1000
                    pick_mx.append([rdata.exchange.to_text().strip('.'), "Up"])

                except:
                    pick_mx.append([rdata.exchange.to_text().strip('.'), "Down"])

    if request.user.is_authenticated():
        engineer = Engineer.objects.get(user__username=request.user.username)
        mailserver_list = get_mx_list(engineer.company)
        template = "hosts/diagnostic_int.html"
    else:
        mailserver_list = None
        template = "hosts/diagnostic.html"
    return render_to_response(template, {
                        'diagnostic_form': diag_form.as_ul(),
                        'pick_mx': pick_mx,
                        'tld': domain,
                        'mailserver_list': mailserver_list,
                        },
                        context_instance=RequestContext(request))

def user_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def user_login(request):
    engineer = Engineer.objects.filter(user=request.user)
    if len(engineer) == 0:
        form = AddCompanyForm()
        name_form = UpdateNameForm()
        return render_to_response("profiles/firstlogin.html", {
                                    'company_form': form,
                                    'name_form': name_form,
                                    },
                                    context_instance=RequestContext(request))
    else:
        try:
            message = None
            mailserver_list = get_mx_list(engineer.company)
            return HttpResponseRedirect('/dashboard/')
        except:
            return HttpResponseRedirect('/add/mailserver/')
