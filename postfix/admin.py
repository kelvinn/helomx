from django.contrib import admin
from postfix.models import *

class MailboxAdmin(admin.ModelAdmin):
    list_display   = ('username', 'name', 'modified')
    ordering       = ('modified',)
    exclude         = ('maildir',)
    
admin.site.register(Mailbox, MailboxAdmin)

class DomainAdmin(admin.ModelAdmin):
    list_display   = ('domain', 'modified')
    ordering       = ('modified',)

admin.site.register(Domain, DomainAdmin)

class AliasAdmin(admin.ModelAdmin):
    list_display   = ('address', 'domain')
    ordering       = ('modified',)

admin.site.register(Alias, AliasAdmin)
