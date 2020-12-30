from django.contrib import admin
from loyalty_card.models import LoyaltyCard,LoyaltyCardStatus
# Register your models here.


class LoyaltyCardAdmin(admin.ModelAdmin):
    list_display = ['vchr_card_name','int_price_range_from','int_price_range_to','int_min_redeem_days','int_min_redeem_point']
    list_filter = ['bln_status','dat_created','dat_updated']
    search_fields = ['vchr_card_name']
admin.site.register(LoyaltyCard,LoyaltyCardAdmin)

class LoyaltyCardAdmin(admin.ModelAdmin):
    list_display = ['fk_customer','fk_old_card','fk_new_card','vchr_status']
    list_filter = ['vchr_status','dat_eligible','dat_given']
    search_fields = ['fk_customer__vchr_name','fk_old_card__vchr_card_name','fk_new_card__vchr_card_name','vchr_remark','vchr_status']
admin.site.register(LoyaltyCardStatus)
