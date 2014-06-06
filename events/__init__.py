import sys
import lxml.etree
import pytz

from django import http

from django.shortcuts import *
from django import template

iso_countries = {'linux2': '/usr/share/xml/iso-codes/iso_3166.xml',
                 'win32': r'C:\iso_3166.xml'}

def country_codes ():
    iso_countries = {'linux2': '/usr/share/xml/iso-codes/iso_3166.xml',
                 'win32': r'C:\iso_3166.xml'}
    t = lxml.etree.parse (iso_countries[sys.platform])
    return sorted ([(e.get ('alpha_2_code'), e.get ('name')) for e in t.getroot ().getiterator () if e.tag == 'iso_3166_entry'], key = lambda x: x[1])

def timezones():
    t = pytz.common_timezones
    return sorted ([(x, x) for x in t])
    
def timezones_for_country(request, cc):
    if request.method == "GET" and cc:
        code = cc
        countrycodes = pytz.country_timezones(code)
        data = ",".join([c for c in countrycodes])
        return HttpResponse(data, content_type = 'text/plain')
    return
