from django.contrib import admin
from .models import RewardsMaster2,RewardsDetails2,RewardsAvailable2,RewardsPaid2,RewardsDetails2
from branch.models import Branch
# # Register your models here.


class RewardsMasterAdmin(admin.ModelAdmin):
    list_display = ['vchr_reward_name','dat_from','dat_to','created_by']
    list_filter = ['dat_from','dat_to']
    search_fields = ['vchr_reward_name','fk_created_by__first_name','fk_created_by__last_name']
    def created_by(self, obj):
        return obj.fk_created_by.first_name+' '+obj.fk_created_by.last_name
admin.site.register(RewardsMaster2,RewardsMasterAdmin)


class RewardsDetailsAdmin(admin.ModelAdmin):
    list_display = ['reward_name','int_quantity_from','int_quantity_to','dbl_value_from','dbl_value_to',]
    list_filter = ['int_to']
    search_fields = ['fk_rewards_master__vchr_reward_name']
    def reward_name(self, obj):
        return obj.fk_rewards_master.vchr_reward_name
admin.site.register(RewardsDetails2,RewardsDetailsAdmin)


class RewardsAvailableAdmin(admin.ModelAdmin):
    list_display = ['staff_name','dat_reward','fk_rewards_details']
    list_filter = ['dat_reward','fk_rewards_master']
    search_fields = ['fk_rewards_master__vchr_reward_name']
    def staff_name(self, obj):
        return obj.dat_reward
admin.site.register(RewardsAvailable2,RewardsAvailableAdmin)


class RewardsPaidAdmin(admin.ModelAdmin):
    list_display = ['staff_name','dbl_paid','dat_paid','dat_acknowledge','int_status']
    list_filter = ['int_status','dat_paid','dat_acknowledge']
    search_fields = ['fk_staff__last_name']
    def staff_name(self, obj):
        return obj.fk_staff.first_name+' '+obj.fk_staff.last_name
admin.site.register(RewardsPaid2,RewardsPaidAdmin)
