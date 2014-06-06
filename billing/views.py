from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.forms.models import formset_factory
from helomx.profiles.models import Company, Engineer
from helomx.hosts.models import *
from helomx.billing.models import *
from helomx.mxhelpers import get_mx_list
from helomx.forms import BillingForm
from paypal.standard.forms import PayPalEncryptedPaymentsForm, PayPalPaymentsForm



from datetime import datetime, timedelta

@login_required
def pay_invoice(request):
    from random import random
    engineer = Engineer.objects.get(user__username=request.user.username)
    mailserver_list = get_mx_list(engineer.company)
    message = None

    company = engineer.company
    engineer_list = Engineer.objects.filter(company=company)

    inv_num = int(random()*10000000)


    # What you want the button to do.
    ten_dolla_dict = {
        "business": "user@example.com",
        "item_name": "HeloMX Credit",
        "amount": "10.00",
        "invoice": inv_num,
        'custom':"%s" % company.slug,
        "notify_url": "https://www.helomx.com/paypal/api/notify/",
        "return_url": "https://www.helomx.com/dashboard/?success=funds",
        "cancel_return": "https://www.helomx.com/dashboard/?success=fundscancel",

    }

    test_dolla_dict = {
        "business": "user@example.com",
        "item_name": "HeloMX Credit",
        "amount": "1.00",
        "invoice": inv_num,
        'custom':"%s" % company.slug,
        "notify_url": "https://www.helomx.com/paypal/api/notify/",
        "return_url": "https://www.helomx.com/dashboard/?success=funds",
        "cancel_return": "https://www.helomx.com/dashboard/?success=fundscancel",

    }

    tf_dolla_dict = {
        "business": "user@example.com",
        "item_name": "HeloMX Credit",
        "amount": "25.00",
        "invoice": inv_num,
        'custom':"%s" % company.slug,
        "notify_url": "https://www.helomx.com/paypal/api/notify/",
        "return_url": "https://www.helomx.com/dashboard/?success=funds",
        "cancel_return": "https://www.helomx.com/dashboard/?success=fundscancel",

    }
    f_dolla_dict = {
        "business": "user@example.com",
        "item_name": "HeloMX Credit",
        "amount": "50.00",
        "invoice": inv_num,
        'custom':"%s" % company.slug,
        "notify_url": "https://www.helomx.com/paypal/api/notify/",
        "return_url": "https://www.helomx.com/dashboard/?success=funds",
        "cancel_return": "https://www.helomx.com/dashboard/?success=fundscancel",

    }

    oh_dolla_dict = {
        "business": "user@example.com",
        "item_name": "HeloMX Credit",
        "amount": "100.00",
        "invoice": inv_num,
        'custom':"%s" % company.slug,
        "notify_url": "https://www.helomx.com/paypal/api/notify/",
        "return_url": "https://www.helomx.com/dashboard/?success=funds",
        "cancel_return": "https://www.helomx.com/dashboard/?success=fundscancel",

    }
    fh_dolla_dict = {
        "business": "user@example.com",
        "item_name": "HeloMX Credit",
        "amount": "500.00",
        "invoice": inv_num,
        'custom':"%s" % company.slug,
        "notify_url": "https://www.helomx.com/paypal/api/notify/",
        "return_url": "https://www.helomx.com/dashboard/?success=funds",
        "cancel_return": "https://www.helomx.com/dashboard/?success=fundscancel",

    }
    # Create the instance.
    #coupon_form = CouponForm(request.POST)

    return render_to_response("billing/payment.html", {
                        'mailserver_list': mailserver_list,
                        'message': message,
                        'company': company,
                        'engineer_list': engineer_list,
                        'test_dolla_form': PayPalEncryptedPaymentsForm(initial=test_dolla_dict),
                        'ten_dolla_form': PayPalEncryptedPaymentsForm(initial=ten_dolla_dict),
                        'tf_dolla_form': PayPalEncryptedPaymentsForm(initial=tf_dolla_dict),
                        'f_dolla_form': PayPalEncryptedPaymentsForm(initial=f_dolla_dict),
                        'oh_dolla_form': PayPalEncryptedPaymentsForm(initial=oh_dolla_dict),
                        'fh_dolla_form': PayPalEncryptedPaymentsForm(initial=fh_dolla_dict),
                        },
                        context_instance=RequestContext(request))



