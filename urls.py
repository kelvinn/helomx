import datetime
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.sitemaps import Sitemap
from helomx.monitor.views import check_status_json, api_feed_mx, api_read_mx, do_chart
from helomx.hosts.views import user_login, user_logout, free_diag, diag_html, realtime, addtime_json, realtime_json, add_credit, add_mailserver, delete_mailserver, detail_mx, upt_mailserver
from helomx.profiles.views import disp_error, password_redirect, dashboard, companymap, add_company, upt_engineer_profile, index, tour, add_engineer, delete_engineer, company_profile
from helomx.billing.views import pay_invoice
from helomx.contact.views import contact
from helomx.infolog.models import FAQ, MOTD
from helomx.infolog.views import add_ticket
from helomx.registration.views import register
from helomx.registration.forms import RegistrationFormTermsOfService

admin.autodiscover()

faq_dict = {
    'queryset': FAQ.objects.all().order_by("popularity"),
    'paginate_by': 10,
}

motd_dict = {
    'queryset': MOTD.objects.all().order_by("-publish_date"),
    'paginate_by': 30,
}

class PagesMap(Sitemap):
    changefreq = 'never' #or pick your frequency
    priority = 0.5 #or pick your priority
    page_dict = {
        'Home':'/',
        'Live Demo':'/tour/',
        'Contact Us':'/contact/',
        'Free Diagnostics':'/diagnostics/',
        'Register':'/accounts/register/',
        'Login':'/accounts/login/',
    }

    def items(self):
        return self.page_dict.keys()

    def location(self, url):
        return self.page_dict[url]

    def lastmod(self, obj):
        return datetime.datetime.now()

sitemaps = {
    'pages': PagesMap,
}

urlpatterns = patterns('',
    (r'^$', index),
    (r'^mx/(?P<slug>[-\w]+)/.*', detail_mx),
    (r'^dashboard/$', dashboard),
    (r'^realtime/$', realtime),
    (r'^api/feed/(?P<probe_loc>[-\w]+)/$', api_feed_mx),
    (r'^api/read/.*', api_read_mx),
    (r'^charting/(?P<slug>[-\w]+)/.*', do_chart),
    (r'^update/company/$', company_profile),
    (r'^update/engineer/(?P<slug>[-\w]+)/$', upt_engineer_profile),
    (r'^update/mailserver/(?P<slug>[-\w]+)/$', upt_mailserver),
    (r'^add/engineer/$', add_engineer),
    (r'^add/mailserver/$', add_mailserver),
    (r'^add/company/', add_company),
    (r'^add/credit/', add_credit),
    (r'^add/ticket/', add_ticket),
    (r'^delete/mailserver/(?P<slug>[-\w]+)/$', delete_mailserver),
    (r'^delete/engineer/(?P<slug>[-\w]+)/$', delete_engineer),
    (r'^realtime/$', realtime),
    (r'^realtime_html/$', realtime_json),
    (r'^addtime_json/$', addtime_json),
    (r'^status_json/.*', check_status_json),
    (r'^companymap/$', companymap),
    (r'^invoices/$', pay_invoice),
    (r'^tour/$', tour),
    (r'^answers/$', 'django.views.generic.list_detail.object_list', dict(faq_dict)),
    (r'^motd/$', 'django.views.generic.list_detail.object_list', dict(motd_dict)),
    (r'^diagnostics/$', free_diag),
    (r'^diag_html/$', diag_html),
    (r'^contact/$', contact),
    (r'^paypal/api/notify/', include('paypal.standard.ipn.urls')),
    (r'^error/(?P<slug>[-\w]+)/$', disp_error),
    (r'^/accounts/password/change/done/$', password_redirect),
    (r'^accounts/logout/$', user_logout),
    (r'^accounts/profile/$', user_login),
    (r'^accounts/', include('helomx.registration.backends.default.urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^admin/(.*)', admin.site.root),

    # This is overwritten by apache on the production server
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/vhosts/helomx.com/helomx/static_media/css'}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/vhosts/helomx.com/helomx/static_media/js'}),
    (r'^img/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/vhosts/helomx.com/helomx/static_media/img'}),

)