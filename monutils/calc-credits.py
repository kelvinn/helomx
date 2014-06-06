#!/usr/bin/python
import sys
sys.path.append('/home/vhosts/helomx.com/helomx/')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from monitor.views import *
from profiles.models import Company
from billing.models import Credit
from mxhelpers import get_daily_cost

if __name__ == "__main__":
    company_list = Company.objects.filter(active=True)

    for company_obj in company_list:
        deduct_count = get_daily_cost(company_obj)
        credit_obj = Credit.objects.get(company=company_obj)
        credit_obj.credit_left = credit_obj.credit_left - deduct_count
        credit_obj.save()
        if credit_obj < 0:
            pass # send out an email
