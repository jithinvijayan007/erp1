from django.contrib import admin
from .models import SapApiTrack
# Register your models here.

class SapApiTrackAdmin(admin.ModelAdmin):
    list_display = ['str_type','str_status','dat_document','dat_push','txt_remarks']
    list_filter = ['dat_document','dat_push']
    search_fields = ['dat_document','dat_push']
    def str_type(self,obj):
        dct_type = {1:'Bills',2:'Payment',3:'Stock Transfer',4:'Receipt',5:'Cheque Receipt',6:'Sales Return',7:'Expense',8:'Angamally Stock Transfer',9:'Spare GRPO',10:'Discount Journal',12:'Purchase Request'}
        return  dct_type.get(obj.int_type,'No Type Specified')

    def str_status(self,obj):
        dct_status = {-1:'Failed',0:'New Entry',1:'Pushed to SAP',2:'Success'}
        return dct_status[obj.int_status]
admin.site.register(SapApiTrack,SapApiTrackAdmin)

