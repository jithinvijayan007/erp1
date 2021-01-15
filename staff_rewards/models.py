from django.db import models
from userdetails.models import UserDetails as UserAppUsermodel
from item_category.models import Item as Items
from products.models import Products
from branch.models import Branch
from enquiry_mobile.models import ItemEnquiry
from django.contrib.postgres.fields import JSONField
from groups.models import Groups
from branch.models import Branch
# Create your models here.
class RewardsMaster(models.Model):
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
    fk_updated_by = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING, blank=True, null=True,related_name='reward_updated_by')
    int_status = models.IntegerField(blank=True, null=True)
    dbl_slab4_percentage = models.FloatField(blank=True, null=True)
    dbl_slab5_percentage = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'rewards_master'
    def __str__(self):
            return str(self.vchr_reward_name)


class RewardsDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_rewards_master = models.ForeignKey(RewardsMaster, models.DO_NOTHING)
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
    int_map_type = models.IntegerField() # 0. Product QTY , 1. Brand QTY , 2. Item QTY, 3. Value, 4. TurnOver ,5.Product Value ,6.Brand Value,7.Item Value
    int_mop_sale = models.IntegerField(blank=True, null=True) # 0. Not MOP, 1. MOP Sale
    int_to = models.IntegerField(blank=True, null=True) # 1. All, 2. Promoter, 3. Non-Promoter, 4. SM/ASM
    int_status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rewards_details'
    def __str__(self):
            return str(self.fk_rewards_master)


class RewardsAvailable(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_rewards_master = models.ForeignKey(RewardsMaster, models.DO_NOTHING, blank=True, null=True)
    fk_rewards_details = models.ForeignKey(RewardsDetails, models.DO_NOTHING, blank=True, null=True)
    # fk_staff = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING, blank=True, null=True)
    fk_item_enquiry = models.ForeignKey(ItemEnquiry, models.DO_NOTHING, blank=True, null=True)
    dbl_mop_amount = models.FloatField(blank=True, null=True)
    dat_reward = models.DateTimeField(blank=True, null=True)
    # dbl_reward = models.FloatField()
    json_staff = JSONField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'rewards_available'
    def __str__(self):
            return str(self.pk_bint_id)


class RewardsPaid(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_staff = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING, related_name='fk_staff')
    dbl_paid = models.FloatField()
    int_status = models.IntegerField(blank=True, null=True) # 0. Paid, 1. Acknowledge
    dat_paid = models.DateTimeField(auto_now_add=True)
    dat_acknowledge = models.DateTimeField(blank=True, null=True)
    fk_created_by = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING, related_name='fk_created_by')
    vchr_transaction_id = models.CharField(max_length=50)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'rewards_paid'
    def __str__(self):
            return str(self.fk_staff)



class RewardAssigned(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_reward_details = models.ForeignKey(RewardsDetails, models.DO_NOTHING, blank=True, null=True)
    int_to = models.IntegerField(blank=True, null=True) # 1. All, 2. Promoter, 3. Non-Promoter, 4. Ass-Branch Manager, 5. Branch Manager, 6. Territory Manager
    int_status = models.IntegerField(blank=True, null=True)
    fk_group = models.ForeignKey(Groups, models.DO_NOTHING, blank=True, null=True)
    dbl_slab1_percentage = models.FloatField(blank=True, null=True)
    dbl_slab1_amount = models.FloatField(blank=True, null=True)
    dbl_slab2_percentage = models.FloatField(blank=True, null=True)
    dbl_slab2_amount = models.FloatField(blank=True, null=True)
    dbl_slab3_percentage = models.FloatField(blank=True, null=True)
    dbl_slab3_amount = models.FloatField(blank=True, null=True)
    dbl_slab4_percentage = models.FloatField(blank=True, null=True)
    dbl_slab5_amount = models.FloatField(blank=True, null=True)
    dbl_slab4_amount = models.FloatField(blank=True, null=True)
    dbl_slab5_percentage = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False

        db_table = 'reward_assigned'

    def __str__(self):
            return str(self.fk_reward_details.fk_rewards_master.vchr_reward_name)
