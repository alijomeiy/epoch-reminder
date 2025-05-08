from django.contrib import admin
from .models import Session

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'start_register_time', 'end_register_time', 'status')
    list_filter = ('status',)
    search_fields = ('start_time', 'end_time', 'status')
