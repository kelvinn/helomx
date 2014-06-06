from django.contrib import admin
from helomx.infolog.models import MOTD, FAQ, Response, Ticket, ProbeStatus

class MOTDAdmin(admin.ModelAdmin):
    list_display   = ('title',)
    ordering       = ('publish_date',)
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(MOTD, MOTDAdmin)

class FAQAdmin(admin.ModelAdmin):
    list_display   = ('title',)
    ordering       = ('publish_date',)
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(FAQ, FAQAdmin)

class TicketAdmin(admin.ModelAdmin):
    list_display   = ('created_by', 'add_time', 'close_time', 'status', 'note')
    ordering       = ('close_time',)

admin.site.register(Ticket, TicketAdmin)

class ProbeStatusAdmin(admin.ModelAdmin):
    list_display   = ('probe', 'status',)

admin.site.register(ProbeStatus, ProbeStatusAdmin)

class ResponseAdmin(admin.ModelAdmin):
    list_display   = ('creation_date',)
    ordering       = ('creation_date',)

admin.site.register(Response, ResponseAdmin)