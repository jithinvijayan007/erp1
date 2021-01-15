from django.contrib import admin

from enquiry_mobile.models import MobileEnquiry,TabletEnquiry,ComputersEnquiry,AccessoriesEnquiry,MobileFollowup,TabletFollowup,ComputersFollowup,AccessoriesFollowup,ItemEnquiry,ItemExchange,Notification,GDPRange,ItemFollowup
# Register your models here.

# Register your models here.

# admin.site.register(MobileEnquiry)
# admin.site.register(TabletEnquiry)
# admin.site.register(AccessoriesEnquiry)
# admin.site.register(ComputersEnquiry)
#
# admin.site.register(MobileFollowup)
# admin.site.register(TabletFollowup)
# admin.site.register(ComputersFollowup)
# admin.site.register(AccessoriesFollowup)

class ItemEnquiryAdmin(admin.ModelAdmin):
    list_display = ['fk_enquiry_master','fk_item','fk_brand','fk_product']
    list_filter = ['vchr_enquiry_status','fk_product']
    search_fields = ['fk_enquiry_master__vchr_enquiry_num','fk_product__vchr_product_name','fk_brand__vchr_brand_name','fk_item__vchr_item_name']
admin.site.register(ItemEnquiry,ItemEnquiryAdmin)

# class EnquiryFinanceAdmin(admin.ModelAdmin):
#     list_display = ['fk_financiers','vchr_delivery_order_no','fk_enquiry_master','vchr_finance_status']
#     list_filter = ['vchr_finance_status']
#     search_fields = ['vchr_finance_status','vchr_delivery_order_no','vchr_name_in_card','fk_financiers__vchr_name','fk_enquiry_master__vchr_enquiry_num']
# admin.site.register(EnquiryFinance,EnquiryFinanceAdmin)

class ItemExchangeAdmin(admin.ModelAdmin):
    list_display = ['fk_item']
    search_fields = ['fk_item__vchr_item_name']
admin.site.register(ItemExchange,ItemExchangeAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['username','vchr_module','vchr_message','bln_active_status']
    list_filter = ['vchr_module']
    search_fields = ['username','vchr_module','vchr_message','vchr_url']
admin.site.register(Notification,NotificationAdmin)

class GDPRangeAdmin(admin.ModelAdmin):
    list_display = ['dbl_from','dbl_to','dbl_amt']
    list_filter = ['int_type']
    search_fields = ['dbl_from','dbl_to','dbl_amt']
admin.site.register(GDPRange,GDPRangeAdmin)

class ItemFollowupAdmin(admin.ModelAdmin):
    list_display = ['fk_item_enquiry','item_name','dat_followup','vchr_enquiry_status']
    list_filter = ['vchr_enquiry_status','int_status']
    search_fields = ['vchr_enquiry_status','int_status','vchr_notes','fk_item_enquiry__fk_item__vchr_item_name']
    def item_name(self, obj):
        return obj.fk_item_enquiry.fk_item.vchr_item_name
admin.site.register(ItemFollowup,ItemFollowupAdmin)
