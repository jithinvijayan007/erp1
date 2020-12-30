from django.db import models
from django.contrib.auth.models import User
from customer.models import CustomerDetails


class LoyaltyCard(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_card_name = models.CharField(max_length=50, blank=True, null=True)
    int_price_range_from = models.BigIntegerField(blank=True, null=True)
    int_price_range_to = models.BigIntegerField(blank=True, null=True)
    dbl_loyalty_percentage = models.FloatField(blank=True, null=True)
    dbl_min_purchase_amount = models.FloatField(blank=True, null=True)
    int_min_redeem_days = models.IntegerField(blank=True, null=True)
    int_min_redeem_point = models.BigIntegerField(blank=True, null=True)
    bln_status = models.NullBooleanField()
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name="loyalty_fk_created")
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name="loyalty_fk_updated")
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loyalty_card'
    def __str__(self):
        return str(self.vchr_card_name)


class LoyaltyCardStatus(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_customer = models.ForeignKey(CustomerDetails, models.DO_NOTHING, blank=True, null=True)
    fk_old_card = models.ForeignKey(LoyaltyCard, models.DO_NOTHING, blank=True, null=True,related_name="fk_old_card")
    fk_new_card = models.ForeignKey(LoyaltyCard, models.DO_NOTHING, blank=True, null=True,related_name="fk_new_card")
    vchr_status = models.CharField(max_length=50, blank=True, null=True)
    fk_staff = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    dat_eligible = models.DateField(blank=True, null=True)
    dat_given = models.DateField(blank=True, null=True)
    vchr_remark = models.CharField(max_length=500, blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True, default=2)# 0.active 2.deactive

    class Meta:
        managed = False
        db_table = 'loyalty_card_status'
    def __str__(self):
        return str(self.fk_customer.vchr_name)
