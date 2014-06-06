from django.db import models
from django.contrib.auth.models import User
from helomx.hosts.models import Mailserver
from helomx.profiles.models import Company
from paypal.standard.ipn.signals import payment_was_successful

class Credit(models.Model):
    company = models.ForeignKey(Company)
    credit_left = models.FloatField()

class InvoiceHistory(models.Model):
    company = models.ForeignKey(Company)
    add_time = models.DateTimeField(auto_now_add=True)
    credit_added = models.FloatField()

def notify_credit(sender, **kwargs):

    #import logging
    #LOG_FILENAME = '/tmp/logging_ipn.out'
    #logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

    ipn_obj = sender
    #logging.debug(ipn_obj.mc_gross)


    amt = float(ipn_obj.mc_gross)

    if amt == 10.0:
        credit_amt = 10.0
    elif amt == 25.0:
        credit_amt = 27.0
    elif amt == 50.0:
        credit_amt = 55.0
    elif amt == 100.0:
        credit_amt = 115.0
    elif amt == 500.0:
        credit_amt = 600.0
    elif amt == 1.0:
        credit_amt = 28.0

    company = Company.objects.get(slug=ipn_obj.custom)

    new_credit = InvoiceHistory(company=company,
                         credit_added=credit_amt,
                         )
    new_credit.save()

    # Actuall add credit to company
    credit_obj = Credit.objects.get(company=company)
    credit_obj.credit_left = credit_obj.credit_left + float(credit_amt)
    credit_obj.save()
payment_was_successful.connect(notify_credit)