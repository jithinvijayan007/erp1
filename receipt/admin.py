from django.contrib import admin

# Register your models here.
from receipt.models import Receipt,ReceiptInvoiceMatching

class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['dat_issue','fk_customer','int_fop','dbl_amount','vchr_remarks','fk_created','fk_updated','int_doc_status','dat_created','dat_updated']
    list_filter = ['dat_issue','fk_customer']
    search_fields = ['dat_issue','fk_customer']
admin.site.register(Receipt,ReceiptAdmin)
admin.site.register(ReceiptInvoiceMatching)
