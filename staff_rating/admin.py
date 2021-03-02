from django.contrib import admin
from staff_rating.models import StaffRating

# Register your models here.

class StaffRatingAdmin(admin.ModelAdmin):
    list_display = ['fk_user','fk_customer','dbl_rating','dat_created']
    list_filter = ['dbl_rating']
    search_fields = ['vchr_comments','vchr_staff_attitude','vchr_staff_knowledge','vchr_store_ambience','vchr_recommended','dbl_rating']
admin.site.register(StaffRating,StaffRatingAdmin)
