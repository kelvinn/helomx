from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from helomx.profiles.models import Company, Engineer
from datetime import datetime, timedelta
import events

PORT_STATUS = (
    ('up', 'Up'),
    ('down', 'Down'),
    ('flap', 'Flapping')
)

BOOL_STATUS = (
    ('yes', 'Yes'),
    ('no', 'No'),
    ('unknown', 'Unknown')
)

DELIVERY_TYPE = (
    ('sms', 'SMS'),
    ('email', 'Email'),
)

BLACKLIST_OPTIONS = (
    ('blacklisted', 'Blacklisted'),
    ('clear', 'Clear'),
)

class Blacklist(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=True)
    site_url = models.CharField(max_length=100, unique=True, editable=True)
    remediation_url = models.CharField(max_length=100, unique=True, editable=True)
    
    def __unicode__(self):
        return self.name

class Note(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField() 
    owner = models.ForeignKey(Engineer)
    enable_comment = models.BooleanField(default=True)

class Mailserver(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(unique=True, editable=True)
    street = models.TextField (max_length = 256, null = True, blank = True, verbose_name="Street Address (Optional)")
    city = models.CharField (max_length = 30, null = True, blank = True, verbose_name="City (Optional)")
    state = models.CharField (max_length = 40, null = True, blank = True)
    postcode = models.CharField (max_length = 16, null = True, blank = True, verbose_name="Postcode (Optional)")
    country = models.CharField (max_length = 2, choices=[('0', '')]+events.country_codes(), null = True, blank = True, verbose_name="Country (Optional)")
    alert_contact = models.ManyToManyField(Engineer, related_name="alert")
    mx_url = models.CharField(max_length=40, unique=True, null=True)
    webmail_url = models.URLField(unique=False, null=True, blank=True, verbose_name="Webmail URL (Optional)")
    ipaddr = models.IPAddressField(unique=False)
    rbl = models.ManyToManyField(Blacklist, verbose_name="Blacklist Checking (Optional)")
    company = models.ForeignKey(Company)
    add_time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/mx/%s/" % self.slug

    def is_trial(self):
        if self.add_time < datetime.now()-timedelta(days=30):
            return False
        else:
            return True

    def get_free_days(self):
        days_left = self.add_time - (datetime.now()-timedelta(days=30))
        return days_left.days
    
    def check_access(self, engineer):
        if self.access.filter(user=engineer):
            return True
        else:
            return False

    def get_alert_contacts(self):
        alert_list = Engineer.objects.filter(company=self.company)
        return Mailserver.objects.filter(alert_contact = alert_list)

class MailserverPrefs(models.Model):
    mailserver = models.ForeignKey(Mailserver)
    send_email_min = models.IntegerField(default=0, verbose_name="Minutes to wait before sending email")
    send_page_min = models.IntegerField(default=10, verbose_name="Minutes to wait before sending SMS")

class QueueAlert(models.Model):
    mailserver = models.ForeignKey(Mailserver)
    delivery_type = models.CharField(max_length = 6, choices=DELIVERY_TYPE, null=False)
    delivery_time = models.DateTimeField()
    alert = models.CharField(max_length = 50, null=True)
    type = models.CharField(max_length = 30, null=True)

class MailserverStatus(models.Model):
    mailserver = models.ForeignKey(Mailserver)
    port = models.CharField(max_length = 6, choices=PORT_STATUS, null=False)
    blacklist = models.CharField(max_length = 15, choices=BLACKLIST_OPTIONS, null=False)
    webmail = models.CharField(max_length = 6, choices=PORT_STATUS, null=False)
    relay = models.CharField(max_length = 10, choices=BOOL_STATUS, null=False)
    backupmx = models.CharField(max_length = 10, choices=BOOL_STATUS, null=False)
    backupmxport = models.CharField(max_length = 10, choices=BOOL_STATUS, null=False)
    revdns = models.CharField(max_length = 10, choices=BOOL_STATUS, null=False)
    score = models.CharField(max_length = 3, null=False)

    def has_incident(self):
        if self.port == 'down' or self.blacklist == 'blacklisted' or self.has_expired():
            return True
        else:
            return False
 
