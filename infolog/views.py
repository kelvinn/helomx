# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import send_mail
from django.conf import settings
from helomx.forms import TicketForm
from helomx.infolog.models import Ticket, FAQ

def get_ticket_form():
    from helomx.forms import TicketForm
    ticket_form = TicketForm()
    print ticket_form
    return {'ticket_form': ticket_form,}

def add_ticket(request):
    #form = UptMailserverForm(mx, instance=mx)
    message = None
    ticket_data = None
    faq_list = FAQ.objects.all().order_by("-popularity")[:3]
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST)
        if ticket_form.is_valid():
            if request.user.is_authenticated():
                from random import randrange
                ticket_type=ticket_form.cleaned_data['ticket_type']
                contact_method=ticket_form.cleaned_data['contact_method']
                content=ticket_form.cleaned_data['content']
                ticket_id=randrange(100000,999999)
                new_ticket = Ticket(ticket_id=ticket_id,
                        created_by=request.user, ticket_type=ticket_type,
                        contact_method=contact_method, content=content)
                new_ticket.save()
                message = "Ticket Created Successfully"
                send_mail('New Ticket Created', 'A new ticket has been created.', settings.DEFAULT_FROM_EMAIL,
                ['user@example.com'], fail_silently=False)
                
                ticket_data = {"ticket_id": ticket_id, "name": request.user.get_full_name(),
                            "contact_method": contact_method, "content": content,}
                
    else:
        ticket_form = TicketForm()
    return render_to_response("infolog/add_ticket.html", {
                                'message': message,
                                'ticket_form': ticket_form.as_ul(),
                                'ticket_data': ticket_data,
                                'faq_list': faq_list,
                                },
                                context_instance=RequestContext(request))
