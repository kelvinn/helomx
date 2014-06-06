from django.contrib import admin
from helomx.billing.models import Credit, InvoiceHistory
snipp
class CreditAdmin(admin.ModelAdmin):
    list_display   = ('company', 'credit_left',)
    list_filter    = ('company', )
    ordering       = ('company', )
    search_fields  = ('company', )

admin.site.register(Credit, CreditAdmin)

class InvoiceHistoryAdmin(admin.ModelAdmin):
    list_display   = ('company', 'add_time', 'credit_added')
    list_filter    = ('company', )
    ordering       = ('company', )
    search_fields  = ('company', )

admin.site.register(InvoiceHistory, InvoiceHistoryAdmin)
