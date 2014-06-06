from django.db import models
from django.contrib.auth.models import User

TICKET_STATUS = (
    ('new', 'New'),
    ('investigating', 'Investigating'),
    ('hold', 'Holding'),
    ('closed', 'Closed'),
)

STATUS_OPTIONS = (
    ('up', 'Up'),
    ('down', 'Down'),
)

PROBE_OPTIONS = (
    ('uk', 'United Kingdom'),
    ('us', 'United States'),
    ('sg', 'Singapore'),
)

class ProbeStatus(models.Model):
    probe = models.CharField(max_length = 15, choices=PROBE_OPTIONS, null=False)
    status = models.CharField(max_length = 10, choices=STATUS_OPTIONS, null=False)
    ip_address = models.IPAddressField()
    alerted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.probe

class MOTD(models.Model):
    title = models.CharField(max_length=40)
    slug = models.SlugField(
        unique_for_date='publish_date',
        help_text='Automatically built from the title.'
    )
    publish_date = models.DateField()
    content = models.TextField()

    class Meta:
        ordering = ('-publish_date', 'title')

    def __unicode__(self):
        return '%s %s' % (self.title, self.publish_date)

    def get_absolute_url(self):
        return "/motd/%s/" % self.slug

class FAQ(models.Model):
    title = models.CharField(max_length=40)
    slug = models.SlugField(
        unique_for_date='publish_date',
        help_text='Automatically built from the title.'
    )
    publish_date = models.DateField()
    content = models.TextField()
    popularity = models.IntegerField(max_length=4)

    class Meta:
        ordering = ('-publish_date', 'title')

    def __unicode__(self):
        return '%s %s' % (self.title, self.publish_date)

    def get_absolute_url(self):
        return "/motd/%s/" % self.slug

class Response(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

class Ticket(models.Model):
    ticket_id = models.CharField(max_length=10)
    created_by = models.ForeignKey(User)
    add_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True, blank=True)
    ticket_type = models.CharField(max_length = 20, null=False)
    contact_method = models.CharField(max_length = 20, null=False)
    content = models.TextField()
    status = models.CharField(max_length = 15, choices=TICKET_STATUS, null=False, default='new')
    note = models.ForeignKey(Response, null=True, blank=True)
