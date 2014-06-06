from django.contrib import admin
from helomx.contact.models import *

class ContactAdmin(admin.ModelAdmin):
    list_display   = ('first_name', 'last_name', 'add_time')
    ordering       = ('add_time',)

admin.site.register(Contact, ContactAdmin)