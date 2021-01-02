from django.contrib import admin
from .models import *
# Register your models here.


class SessionHandlerAdmin(admin.ModelAdmin):
    list_display = ['fk_user', 'vchr_session_key']
    search_fields = ['vchr_session_key', 'fk_user__username', 'fk_user__first_name', 'fk_user__last_name']
admin.site.register(SessionHandler, SessionHandlerAdmin)
