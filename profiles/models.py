from django.db import models
from django.contrib.auth.models import User
import events

# This is the business giving support
class Company(models.Model):
    primary_contact = models.ForeignKey(User, unique = True)
    name = models.CharField (max_length = 64, unique = True)
    slug = models.SlugField(unique=True, editable=False)
    street = models.TextField (max_length = 256, null = True, blank = True)
    city = models.CharField (max_length = 30, null = True, blank = True)
    state = models.CharField (max_length = 40, null = True, blank = True)
    postcode = models.CharField (max_length = 16, null = True, blank = True)
    country = models.CharField (max_length = 2, choices=[('0', '')]+events.country_codes(), null = True, blank = True)
    telephone = models.CharField (max_length = 64, blank = True, null = True)
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/dashboard/%s/" % self.slug

# These are engineers that can be associated with each company.
class Engineer(models.Model):
    user = models.ForeignKey (User, unique = True)
    timezone = models.CharField (max_length = 64, choices=events.timezones(), default = "Europe/London")
    company = models.ForeignKey(Company)
    mobile = models.CharField(max_length = 64, blank = True, null = True, verbose_name="Mobile (Optional)")
    blackout_end = models.TimeField(null = True, blank = True, default="08:30:00", verbose_name="Allow SMS (Optional)")
    blackout_start = models.TimeField(null = True, blank = True, default="17:00:00", verbose_name="Stop SMS (Optional)")

    def __unicode__(self):
        return self.user.__str__()


