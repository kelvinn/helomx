from django.contrib import admin
from helomx.profiles.models import Company, Engineer

class CompanyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'primary_contact',)
    list_filter    = ('name', 'primary_contact',)
    ordering       = ('name', 'primary_contact',)
    search_fields  = ('name', 'primary_contact', 'mobile',)
    #prepopulated_fields = {'slug': ('name',)}
    
class EngineerAdmin(admin.ModelAdmin): 
    list_display   = ('user',)
    ordering       = ('user',)
    search_fields  = ('first_name', 'last_name', 'mobile',)

admin.site.register(Company, CompanyAdmin)
admin.site.register(Engineer, EngineerAdmin)


