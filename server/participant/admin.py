from django.contrib import admin
from .models import SessionParticipant


@admin.register(SessionParticipant)
class SessionParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'hezb','joined_at')
    list_filter = ('session', 'user', 'hezb')
    search_fields = ('user__username', 'session__start_time')