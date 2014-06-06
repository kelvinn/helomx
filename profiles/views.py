from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django import forms
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
from helomx.hosts.models import Mailserver
from helomx.profiles.models import Company, Engineer
from helomx.billing.models import Credit
from helomx.forms import EngineerProfileForm, DiagnosticForm, AddEngineerForm, EngineerPermForm, AddCompanyForm, UpdateNameForm
from mxhelpers import get_mx_list, get_daily_cost

def index(request):
    diag_form = DiagnosticForm()
    return render_to_response("index.html", {
                        'form': diag_form,
                        },
                        context_instance=RequestContext(request))

def tour(request):
    return render_to_response("profiles/tour.html", {
                                    },
                                    )

@login_required
def add_engineer(request):
    from django.contrib.auth.models import User, Permission
    from django.template.defaultfilters import slugify
    site_form = AddEngineerForm()
    perm_form = EngineerPermForm()
    message = None
    engineer = Engineer.objects.get(user__username=request.user.username)
    mailserver_list = get_mx_list(engineer.company)
    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)
    if request.method == 'POST':
        site_form = AddEngineerForm(request.POST)
        if site_form.is_valid():
            if request.user.is_authenticated():
                new_user = User.objects.create_user(slugify(site_form.cleaned_data['user']), site_form.cleaned_data['email'], site_form.cleaned_data['password1'])
                new_user.is_active = True
                new_user.first_name = site_form.cleaned_data['first_name']
                new_user.last_name = site_form.cleaned_data['last_name']
                new_user.save()
                if site_form.cleaned_data['can_edit_mx'] == True:
                    perm = Permission.objects.get(codename="delete_mailserver")
                    new_user.user_permissions.add(perm)
                    perm = Permission.objects.get(codename="change_mailserver")
                    new_user.user_permissions.add(perm)
                    perm = Permission.objects.get(codename="add_mailserver")
                    new_user.user_permissions.add(perm)
                if site_form.cleaned_data['can_edit_company'] == True:
                    perm = Permission.objects.get(codename="change_company")
                    new_user.user_permissions.add(perm)
                if site_form.cleaned_data['can_edit_billing'] == True:
                    perm = Permission.objects.get(codename="add_invoicehistory")
                    new_user.user_permissions.add(perm)
                    perm = Permission.objects.get(codename="change_credit")
                    new_user.user_permissions.add(perm)
                new_engineer = Engineer(user=new_user,
                                      timezone=site_form.cleaned_data['timezone'],
                                      company=company,
                                      mobile=site_form.cleaned_data['mobile'])
                new_engineer.save()
                message = "Engineer added successfully"
    return render_to_response("profiles/add_engineer.html", {
                                'mailserver_list': mailserver_list,
                                'engineer_form': site_form,
                                'message': message,
                                'company': company,
                                'engineer_list': engineer_list,
                                },
                                context_instance=RequestContext(request))

@login_required
def add_company(request):
    from django.contrib.auth.models import User, Permission
    site_form = AddCompanyForm()
    name_form = UpdateNameForm()
    if request.method == 'POST':
        site_form = AddCompanyForm(request.POST)
        try:
            name_form = UpdateNameForm(request.POST)
        except:
            name_form = None

        #engineer = Engineer.objects.get(user__username=request.user.username)
        if site_form.is_valid() and name_form.is_valid():
            if request.user.is_authenticated():
                new_company = Company(primary_contact=request.user,
                                    name=site_form.cleaned_data['name'],
                                    slug=slugify(site_form.cleaned_data['name']),
                                    street=site_form.cleaned_data['street'],
                                    city=site_form.cleaned_data['city'],
                                    state=site_form.cleaned_data['state'],
                                    postcode=site_form.cleaned_data['postcode'],
                                    country=site_form.cleaned_data['country'],
                                    telephone=site_form.cleaned_data['telephone'],
                                    )
                new_company.save()
                new_user = request.user
                perm = Permission.objects.get(codename="delete_mailserver")
                new_user.user_permissions.add(perm)
                perm = Permission.objects.get(codename="change_mailserver")
                new_user.user_permissions.add(perm)
                perm = Permission.objects.get(codename="add_mailserver")
                new_user.user_permissions.add(perm)
                perm = Permission.objects.get(codename="change_company")
                new_user.user_permissions.add(perm)
                perm = Permission.objects.get(codename="add_invoicehistory")
                new_user.user_permissions.add(perm)
                perm = Permission.objects.get(codename="change_credit")
                new_user.user_permissions.add(perm)

                credit_obj = Credit(company=new_company, credit_left=0)
                credit_obj.save()

                engineer_list = Engineer.objects.filter(user__username=request.user.username)
                if len(engineer_list) > 0:
                    return HttpResponseRedirect('/dashboard/')
                else:
                    name_form = UpdateNameForm(data=request.POST, instance=request.user)
                    name_form.save()
                    new_engineer = Engineer(user=request.user,
                                            timezone=site_form.cleaned_data['timezone'],
                                            company=new_company,
                                            )
                    new_engineer.save()
                    return HttpResponseRedirect('/add/mailserver/')

        return render_to_response("profiles/firstlogin.html", {
                                    'company_form': site_form,
                                    'name_form': name_form,
                                    },
                                    context_instance=RequestContext(request))
                                    
@login_required
def company_profile(request):
    from forms import CompanyForm
    engineer = Engineer.objects.get(user__username=request.user.username)
    mailserver_list = get_mx_list(engineer.company)
    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)
    form = CompanyForm(instance=company)
    message = None
    if request.method == 'POST':
        form = CompanyForm(data=request.POST, instance=company)
        if form.is_valid():
            form.save()
            message = "Company details updated successfully"


    return render_to_response("profiles/upd_company.html", {
                                'company_form': form,
                                'mailserver_list': mailserver_list,
                                'message': message,
                                'company': company,
                                'engineer_list': engineer_list,
                                },
                                context_instance=RequestContext(request))

@login_required
def disp_error(request, slug):
    engineer = Engineer.objects.get(user__username=request.user.username)
    mailserver_list = get_mx_list(engineer.company)
    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)
    return render_to_response("profiles/company.html", {
                                'company_form': form.as_ul(),
                                'mailserver_list': mailserver_list,
                                'message': message,
                                'company': company,
                                'engineer_list': engineer_list,
                                'error_code': slug,
                                },
                                context_instance=RequestContext(request))

@login_required
def upt_engineer_profile(request, slug):
    from forms import EngineerForm, UserForm
    from django.contrib.auth.models import Permission
    message = None
    engineer = Engineer.objects.get(user__username=slug)
    mailserver_list = get_mx_list(engineer.company)
    user_form = UserForm(instance=engineer.user)
    form = EngineerForm(instance=engineer)
    if request.method == 'POST':
        form = EngineerForm(data=request.POST, instance=engineer)
        user_form = UserForm(data=request.POST, instance=engineer.user)
        perm_form = EngineerPermForm(request.POST)
        if form.is_valid() and user_form.is_valid() and perm_form.is_valid():
            form.save()
            user_form.save()
            message = "Engineer updated successfully"

    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)
        
    return render_to_response("profiles/engineer.html", {
                                'slug': slug,
                                'engineer_form': form.as_ul(),
                                'user_form': user_form.as_ul(),
                                'mailserver_list': mailserver_list,
                                'message': message,
                                'company': company,
                                'engineer_list': engineer_list,
                                },
                                context_instance=RequestContext(request))

def build_hist_dataset(avail_history):
    from datetime import datetime, time, timedelta, date
    import calendar
    #result = get_object_or_404(Mailserver, slug=mailserver.slug)
    t_now = datetime.now()
    filter_time = t_now - timedelta(days=int(t_now.day))
    dataset_hist = []
    avail_list = avail_history.filter(add_time__gte=filter_time)
    for hist in avail_list:
        dataset_hist.append(hist.add_time.day)
    d_hist = []
    d_range = ''
    for i in xrange(1,calendar.mdays[t_now.month]+1):
        d_hist.append(dataset_hist.count(i))
        d_range = d_range + '%s|' % i
    return d_hist, d_range[0:-1]

def merge(seq):
    merged = []
    for s in seq:
        for x in s:
            merged.append(x)
    return merged

@login_required
def dashboard(request):
    from monitor.models import PortHistory, BlacklistHistory
    try:
        engineer = Engineer.objects.get(user__username=request.user.username)
    except:
        return HttpResponseRedirect('/accounts/profile/')

    success_type = request.GET.get('success')
    if success_type == "mailserver":
        message = "Mailserver deleted successfully"
    elif success_type == "engineer":
        message = "Engineer deleted successfully"
    elif success_type == "password":
        message = "Password changed successfully"
    else:
        message = None

    mailserver_list = get_mx_list(engineer.company)
    avail_history = PortHistory.objects.filter(mailserver__company=engineer.company, mailserver__active=True).order_by('-add_time')
    open_avail_history = avail_history.filter(close_time=None)
    dataset_availability = [mailserver_list.filter(mailserverstatus__port='up').count(), mailserver_list.filter(mailserverstatus__port='down').count()]
    blacklist_history = BlacklistHistory.objects.filter(mailserver__company=engineer.company, mailserver__active=True).order_by('-add_time')
    open_blacklist_history = blacklist_history.filter(close_time=None)
    dataset_blacklist = [mailserver_list.filter(mailserverstatus__blacklist='blacklisted').count(), mailserver_list.filter(mailserverstatus__blacklist='clear').count()]
    dataset_hist, d_range = build_hist_dataset(avail_history)
    open_incidents = []
    for s in [open_blacklist_history, open_avail_history]:
        for x in s:
            open_incidents.append(x)
    company = engineer.company
    daily_cost = get_daily_cost(company)
    engineer_list = Engineer.objects.filter(company=company)
    return render_to_response("profiles/dashboard.html", {
                                'mailserver_list': mailserver_list,
                                'engineer_list': engineer_list,
                                'company': company,
                                'message': message,
                                'dataset_availability': dataset_availability,
                                'blacklist_history': open_blacklist_history,
                                'dataset_blacklist': dataset_blacklist,
                                'dataset_hist': dataset_hist,
                                'open_incidents': open_incidents,
                                'daily_cost': daily_cost,
                                'max_daily_incidents': max(dataset_hist),
                                'd_range': d_range,
                                },
                                context_instance=RequestContext(request))

@login_required
def companymap(request):
    return render_to_response("profiles/companymap.html", {
                                },
                                context_instance=RequestContext(request))

@login_required
def delete_engineer(request, slug):
    from django.contrib.auth.models import User
    try:
        to_delete_engineer = Engineer.objects.get(user__username=slug)
        user = User.objects.get(engineer=to_delete_engineer)
        user.delete()
        to_delete_engineer.delete()
        return HttpResponseRedirect('/dashboard/?success=engineer')
    except:
        return HttpResponseRedirect('/error/432534/')


@login_required
def password_redirect(requestg):
    try:
        return HttpResponseRedirect('/dashboard/?success=password')
    except:
        return HttpResponseRedirect('/error/4343534/')
