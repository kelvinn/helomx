from django.db import models
from django.contrib import admin
from helomx.hosts.models import Mailserver, Note, Blacklist

STATUS_OPTIONS = (
    ('up', 'Up'),
    ('down', 'Down'),
    ('flap', 'Flapping')
)

BLACKLIST_OPTIONS = (
    ('blacklisted', 'Blacklisted'),
    ('clear', 'Clear'),
)

PROBE_OPTIONS = (
    ('us', 'United States'),
    ('sg', 'Singapore'),
    ('uk', 'United Kingdom'),
)

CHECK_TYPES = (
    ('blacklist', 'Blacklist'),
    ('port', 'Port'),
    ('misc', 'Misc')
)

class FreeCheckHistory(models.Model):
    ipaddr = models.IPAddressField(unique=False)
    checker = models.IPAddressField(unique=False)
    check_time = models.DateTimeField(auto_now_add=True)

class CheckHistory(models.Model):
    mailserver = models.ForeignKey(Mailserver)
    check_type = models.CharField(max_length = 10, choices=CHECK_TYPES, null=False)
    check_time = models.DateTimeField(auto_now_add=True)
    probe = models.CharField(max_length = 10, choices=PROBE_OPTIONS, null=True, blank=True)

class PortHistory(models.Model):
    mailserver = models.ForeignKey(Mailserver)       
    add_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True, blank=True)
    ticket_url = models.URLField(null=True, blank=True)
    ack = models.BooleanField(default=False)

    class Meta:
        ordering = ['-add_time']

class BlacklistHistory(models.Model):
    mailserver = models.ForeignKey(Mailserver)
    add_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True, blank=True)
    rbl = models.ManyToManyField(Blacklist)
    ticket_url = models.URLField(null=True, blank=True)
    ack = models.BooleanField(default=False)
    
class MailserverRblStatus(models.Model):
    mailserver = models.ForeignKey(Mailserver)
    rbl = models.ForeignKey(Blacklist)
    status =  models.CharField(max_length = 15, choices=BLACKLIST_OPTIONS, null=True, default='clear')
    

"""
class Alert(models.Model):
    mailserver = models.ForeignKey(Mailserver)
    alert_type = models.CharField(max_length = 10, choices=CHECK_TYPES, null=False)
    emailed = models.BooleanField(default=False)
    smsed = models.BooleanField(default=False)
    ignored = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    note = models.ManyToManyField(Note, null=True, blank=True)

    def __unicode__(self):
        return str(self.id)
"""

class Rtt(models.Model):
    mailserver = models.ForeignKey(Mailserver, db_index=True)
    probe = models.CharField(max_length = 10, choices=PROBE_OPTIONS, null=False)
    ping_time = models.DateTimeField(null=True, db_index=True)
    ping_rtt = models.IntegerField()

    def __int__(self):
        return self.ping_rtt

    class Meta:
        ordering = ['-ping_time']

class RttMinified(models.Model):
    mailserver = models.ForeignKey(Mailserver, db_index=True)
    probe = models.CharField(max_length = 10, choices=PROBE_OPTIONS, null=False, db_index=True)
    ping_time = models.DateTimeField(null=True, db_index=True)
    ping_rtt = models.IntegerField(null=True)

    def __int__(self):
        return self.ping_rtt

    class Meta:
        ordering = ['-ping_time']
