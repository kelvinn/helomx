from django import template
from helomx.hosts.models import *
from helomx.infolog.models import MOTD, FAQ, ProbeStatus
from django.template import Library
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='get_status')
def get_status(value, arg):
    port = MailserverStatus.objects.filter(mailserverslug=arg, )
    blacklist = MailserverStatus.objects.filter(slug=arg)
    return value.replace(arg, '')


@register.inclusion_tag('infolog/motd.html')
#@register.filter(name='get_motd')
def get_motd(slice_num):
    motd_list = MOTD.objects.all().order_by('-publish_date')
    return {'motd_list': motd_list[:slice_num]}

@register.inclusion_tag('infolog/probestatus.html')
def get_probe_status():
    probe_list = ProbeStatus.objects.all()
    return {'probe_list': probe_list}

@register.inclusion_tag('infolog/faq.html')
#@register.filter(name='get_motd')
def get_faq(slice_num):
    faq_list = FAQ.objects.all().order_by('-publish_date')
    return {'faq_list': faq_list[:slice_num]}

@register.inclusion_tag('hosts/side_list.html')
def get_side_list(user, perms):
    from helomx.mxhelpers import get_mx_list
    engineer = Engineer.objects.get(user__username=user.username)
    company=engineer.company
    mailserver_list = get_mx_list(company)
    engineer_list = Engineer.objects.filter(company=company)
    return {'mailserver_list': mailserver_list, 'engineer_list': engineer_list,
                'company': company, 'perms':perms}

@register.inclusion_tag('hosts/mailserver_list.html')
def mailserver_dropdown(user, perms):
    from helomx.mxhelpers import get_mx_list
    try:
        engineer = Engineer.objects.get(user__username=user.username)
        company=engineer.company
        mailserver_list = get_mx_list(company)
    except:
        mailserver_list = None
        engineer = None
        company = None
    return {'mailserver_list': mailserver_list, 'company': company, 'perms':perms}

def truncate_chars(s, num):
    """
    Template filter to truncate a string to at most num characters respecting word
    boundaries.
    """
    s = force_unicode(s)
    length = int(num)
    if len(s) > length:
        length = length - 3
        if s[length-1] == ' ' or s[length] == ' ':
            s = s[:length].strip()
        else:
            words = s[:length].split()
            if len(words) > 1:
                del words[-1]
            s = u' '.join(words)
        s += '...'
    return s
truncate_chars = allow_lazy(truncate_chars, unicode)

def truncatechars(value, arg):
    """
    Truncates a string after a certain number of characters, but respects word boundaries.

    Argument: Number of characters to truncate after.
    """
    try:
        length = int(arg)
    except ValueError: # If the argument is not a valid integer.
        return value # Fail silently.
    return truncate_chars(value, length)
truncatechars.is_safe = True
truncatechars = stringfilter(truncatechars)

register.filter(truncatechars)
