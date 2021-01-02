from django.contrib import admin
from userdetails.models import UserDetails as Userdetails,GuestUserDetails,UserLogDetails,BackendUrls,ReligionCaste
# Register your models here.


# class UserdetailsAdmin(admin.ModelAdmin):
#     list_display = ['bint_phone','fk_branch','fk_group','dat_created']
#     list_filter = ['dat_created','dat_updated']
#     search_fields = ['bint_phone','fk_group__vchr_name','fk_company__vchr_name','fk_branch__vchr_name','fk_brand__vchr_name']
# admin.site.register(Userdetails,UserdetailsAdmin)

class GuestUserDetailsAdmin(admin.ModelAdmin):
    list_display = ['pk_bint_id','fk_branch','fk_user_id','session_expiry_time']
    list_filter = ['dat_created','dat_updated']
    search_fields = ['pk_bint_id','fk_user__vchr_name','fk_branch__vchr_name']
admin.site.register(GuestUserDetails,GuestUserDetailsAdmin)
admin.site.register(UserLogDetails)
admin.site.register(BackendUrls)
admin.site.register(ReligionCaste)
