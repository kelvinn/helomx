# Create your views here.
import smtplib
from django.conf import settings
from django.shortcuts import render_to_response
from django.core.mail import send_mail
from django.template import RequestContext
from django import forms
from django.contrib.auth.models import User
from helomx.forms import ContactForm
from helomx.contact.models import Contact

def contact(request):
    form = ContactForm()
    user = request.user
    message = None
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            form.save()
            message = "Comments submitted successfully"
            send_mail('New Comment', 'You have a new comment.', settings.DEFAULT_FROM_EMAIL,
                ['user@example.com'], fail_silently=False)

    return render_to_response("contact/contact.html", {
                                'contact_form':form.as_ul(),
                                'message': message,
                                },
                                context_instance=RequestContext(request))
