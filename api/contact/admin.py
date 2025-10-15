from django.contrib import admin
from .models import Contact, Setting

class ContactView(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'updated_at', 'checked_by_admin')
    search_fields = ('name', 'email')

admin.site.register(Contact, ContactView)
admin.site.register(Setting)