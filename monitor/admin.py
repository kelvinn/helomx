from django.contrib import admin
from helomx.monitor.models import Rtt, RttMinified, MailserverRblStatus, BlacklistHistory, PortHistory, CheckHistory, FreeCheckHistory

class CheckHistoryAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'check_type', 'check_time', 'probe')

admin.site.register(CheckHistory, CheckHistoryAdmin)

"""
class AlertAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'emailed', 'smsed', 'ignored')

admin.site.register(Alert, AlertAdmin)
"""
class FreeCheckHistoryAdmin(admin.ModelAdmin):
    list_display   = ('ipaddr', 'checker', 'check_time')

admin.site.register(FreeCheckHistory, FreeCheckHistoryAdmin)

class MailserverRblStatusAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'status',)

admin.site.register(MailserverRblStatus, MailserverRblStatusAdmin)

class PortHistoryAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'add_time', 'close_time')

admin.site.register(PortHistory, PortHistoryAdmin)

class BlacklistHistoryAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'add_time', 'close_time')
    list_filter    = ('close_time', )
    
admin.site.register(BlacklistHistory, BlacklistHistoryAdmin)

class RttAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'ping_time', 'probe', 'ping_rtt')
    list_filter    = ('mailserver', )

admin.site.register(Rtt, RttAdmin)

class RttMinifiedAdmin(admin.ModelAdmin):
    list_display   = ('mailserver', 'ping_time', 'probe', 'ping_rtt')
    list_filter    = ('mailserver', )

admin.site.register(RttMinified, RttMinifiedAdmin)