from django.db import models
from branch.models import Branch

class SapApiTrack(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    int_document_id = models.IntegerField(blank=True, null=True)
    int_type = models.IntegerField(blank=True, null=True) # 1:-salesMaster,2:- Advance Refund (Payment) ,3:-StockTransfer 4. Advance Payment (Receipt) 5. Check Receipt(After Received),6-SalesReturn,7.Expense, (SalesDetails) 8:-StockRequest 9. GRPO(SalesMaster),10-Discount Journal
    int_status = models.IntegerField(blank=True, null=True) # 0:-initial,1:-Send Data,2:-Success,-1:-Failed
    dat_document = models.DateTimeField(blank=True, null=True)
    dat_push = models.DateTimeField(blank=True, null=True)
    txt_remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sap_api_track'

class ChartOfAccounts(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_acc_code = models.CharField(max_length=30, blank=True, null=True)
    vchr_acc_name = models.CharField(max_length=100, blank=True, null=True)
    vchr_acc_type = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False

        db_table = 'chart_of_accounts'


class Freight(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=10, blank=True, null=True)
    vchr_category = models.CharField(max_length=30, blank=True, null=True)
    vchr_tax_code = models.CharField(max_length=10, blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'freight'
