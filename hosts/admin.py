from django.contrib import admin
from helomx.hosts.models import Blacklist, QueueAlert, Mailserver, MailserverPrefs, MailserverStatus, Note

class BlacklistAdmin(admin.ModelAdmin):
    list_display   = ('name', 'site_url')
    list_filter    = ('name', )
    ordering       = ('name', )
    search_fields  = ('name', )
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Blacklist, BlacklistAdmin)

class QueueAlertAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'delivery_type', 'delivery_time',)

admin.site.register(QueueAlert, QueueAlertAdmin)

class MailserverStatusAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'blacklist', 'port', 'webmail')

admin.site.register(MailserverStatus, MailserverStatusAdmin)

class MailserverPrefAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'send_email_min', 'send_page_min',)

admin.site.register(MailserverPrefs, MailserverPrefAdmin)

class MailserverAdmin(admin.ModelAdmin):
    list_display   = ('name', 'ipaddr', 'active')
    list_filter    = ('name', )
    ordering       = ('name', )
    search_fields  = ('name', )
    prepopulated_fields = {'slug': ('name',)}
    
admin.site.register(Mailserver, MailserverAdmin)

class NoteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Note, NoteAdmin)