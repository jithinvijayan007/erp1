from django.db import models
from userdetails.models import UserDetails as UserAppUsermodel
from item_category.models import Item as Items
from products.models import Products
from branch.models import Branch
from enquiry_mobile.models import ItemEnquiry
from django.contrib.postgres.fields import JSONField
from groups.models import Groups

# Create your models here.
class RewardsMaster2(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dat_from = models.DateTimeField(blank=True, null=True)
    dat_to = models.DateTimeField(blank=True, null=True)
    vchr_area_type = models.CharField(max_length=20, blank=True, null=True)
    json_branch = JSONField()
    vchr_reward_name = models.CharField(max_length=250, blank=True, null=True)
    dbl_slab1_percentage = models.FloatField(blank=True, null=True)
    dbl_slab2_percentage = models.FloatField(blank=True, null=True)
    dbl_slab3_percentage = models.FloatField(blank=True, null=True)
    dat_created_at = models.DateTimeField(auto_now_add=True)
    fk_created_by = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'rewards_master2'
    def __str__(self):
            return str(self.vchr_reward_name)


class RewardsDetails2(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_rewards_master = models.ForeignKey(RewardsMaster2, models.DO_NOTHING)
    int_quantity_from = models.BigIntegerField(blank=True, null=True)
    int_quantity_to = models.BigIntegerField(blank=True, null=True)
    dbl_value_from = models.FloatField(blank=True, null=True)
    dbl_value_to = models.FloatField(blank=True, null=True)
    dbl_slab1_percentage = models.FloatField(blank=True, null=True)
    dbl_slab1_amount = models.FloatField(blank=True, null=True)
    dbl_slab2_percentage = models.FloatField(blank=True, null=True)
    dbl_slab2_amount = models.FloatField(blank=True, null=True)
    dbl_slab3_percentage = models.FloatField(blank=True, null=True)
    dbl_slab3_amount = models.FloatField(blank=True, null=True)
    int_map_id = models.BigIntegerField(blank=True, null=True)
    int_map_type = models.IntegerField() # 0. Product, 1. Brand, 2. Item, 3. Value, 4. TurnOver
    int_mop_sale = models.IntegerField(blank=True, null=True) # 0. Not MOP, 1. MOP Sale
    int_to = models.IntegerField(blank=True, null=True) # 1. All, 2. Promoter, 3. Non-Promoter, 4. SM/ASM

    class Meta:
        managed = False
        db_table = 'rewards_details2'
    def __str__(self):
            return str(self.fk_rewards_master)


class RewardsAvailable2(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_rewards_master = models.ForeignKey(RewardsMaster2, models.DO_NOTHING, blank=True, null=True)
    fk_rewards_details = models.ForeignKey(RewardsDetails2, models.DO_NOTHING, blank=True, null=True)
    fk_item_enquiry = models.ForeignKey(ItemEnquiry, models.DO_NOTHING, blank=True, null=True)
    dbl_mop_amount = models.FloatField(blank=True, null=True)
    dat_reward = models.DateTimeField(blank=True, null=True)
    json_staff = JSONField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'rewards_available2'
    def __str__(self):
        return str(self.pk_bint_id)


class RewardsPaid2(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_staff = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING, related_name='fk_staff2')
    dbl_paid = models.FloatField()
    int_status = models.IntegerField(blank=True, null=True) # 0. Paid, 1. Acknowledge
    dat_paid = models.DateTimeField(auto_now_add=True)
    dat_acknowledge = models.DateTimeField(blank=True, null=True)
    fk_created_by = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING, related_name='fk_created_by2')
    vchr_transaction_id = models.CharField(max_length=50)


    class Meta:
        managed = False
        db_table = 'rewards_paid2'
    def __str__(self):
            return str(self.fk_staff)
