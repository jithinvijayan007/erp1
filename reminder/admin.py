from django.contrib import admin
from reminder.models import Reminder
# Register your models here.

class ReminderAdmin(admin.ModelAdmin):
    list_display = ['fk_user','dat_created_at','dat_reminder','vchr_title']
    search_fields = ['vchr_description','vchr_title']
admin.site.register(Reminder,ReminderAdmin)
