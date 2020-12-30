from django.contrib import admin
from purchase.models import PoMaster,PoDetails,Document,GrnMaster,GrnDetails,PurchaseVoucher
# Register your models here.


class PoMasterAdmin(admin.ModelAdmin):
    list_display = ['vchr_po_num','fk_supplier','fk_branch','int_doc_status']
    list_filter = ['int_doc_status']
    search_fields = ['vchr_po_num','fk_supplier','fk_branch']
admin.site.register(PoMaster,PoMasterAdmin)

class PoDetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_item','fk_po_master','int_qty']
    list_filter = ['fk_item']
    search_fields = ['fk_item','fk_po_master']
admin.site.register(PoDetails,PoDetailsAdmin)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ['vchr_module_name','vchr_short_code','int_number']
    list_filter = ['int_number']
    search_fields = ['vchr_module_name','vchr_short_code']
admin.site.register(Document,DocumentAdmin)

class GrnMasterAdmin(admin.ModelAdmin):
    list_display = ['vchr_purchase_num','fk_po','fk_supplier','fk_branch','int_doc_status']
    list_filter = ['int_doc_status']
    search_fields = ['vchr_purchase_num','fk_supplier','fk_branch']
admin.site.register(GrnMaster,GrnMasterAdmin)

class GrnDetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_purchase','fk_item','int_avail','vchr_batch_no']
    list_filter = ['int_avail']
    search_fields = ['fk_purchase','fk_item']
admin.site.register(GrnDetails,GrnDetailsAdmin)


class PurchaseVoucherAdmin(admin.ModelAdmin):
    list_display = ['vchr_voucher_num','fk_supplier','vchr_voucher_bill_no']
    list_filter = ['dbl_voucher_amount']
    search_fields = ['fk_supplier','fk_grn']
admin.site.register(PurchaseVoucher,PurchaseVoucherAdmin)
