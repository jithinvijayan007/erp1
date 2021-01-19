from django.db import models
# from company.models import  CompanyDetails
# from django.contrib.postgres.fields import JSONField,ArrayField
# from product_group.models import ProductGroup
# from django.contrib.auth.models import User as AuthUser
from item_category.models import Item

class ItemDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING)
    json_spec = models.TextField()  # This field type is a guess.
    vchr_item_img = models.ImageField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item_details'

    def __str__(self):
            return str(self.fk_item)

# # from django_postgres_extensions.models.fields import ArrayField
# # Create your models here.

# class ItemCategory(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     vchr_category = models.CharField(max_length=100, blank=True, null=True)
#     json_specs = JSONField()  # This field type is a guess.
#     int_status = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'item_category'

# class Products(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     vchr_product_name = models.CharField(max_length=256)
#     fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, blank=True, null=True)
#     vchr_product_img = models.CharField(max_length=300, blank=True, null=True)
#     bln_visible = models.NullBooleanField()
#     #vchr_order = ArrayField(models.CharField(max_length=30),blank=True, null=True)
#     fk_group = models.ForeignKey(ProductGroup, models.DO_NOTHING, blank=True, null=True)
#     dct_product_spec = models.TextField(blank=True, null=True)  # This field type is a guess.

#     class Meta:
#         managed = False
#         db_table = 'products'

#     def __str__(self):
#         return "{}".format(self.vchr_product_name)

#     def delete(self):
#         super(Products, self).delete()

# class Brands(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     vchr_brand_name = models.CharField(max_length=100)
#     fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING)
#     # fk_product = models.ForeignKey(Products, blank=True, null=True)

#     class Meta:
#         managed = True
#         db_table = 'brands'

#     def __str__(self):
#         return "{}".format(self.vchr_brand_name)


# class ItemGroup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     vchr_item_group = models.CharField(max_length=100, blank=True, null=True)
#     int_status = models.IntegerField(blank=True, null=True)
#     fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='creater')
#     dat_created = models.DateTimeField(blank=True, null=True)
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='updater')
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'item_group'

#     def __str__(self):
#         return "{}".format(self.vchr_item_group)

# class Items(models.Model):
#     vchr_item_name = models.CharField(max_length = 100)
#     vchr_item_code = models.CharField(max_length = 100)
#     fk_product = models.ForeignKey(Products, blank=True, null=True)
#     fk_brand = models.ForeignKey(Brands, blank=True, null=True)
#     vchr_barcode = models.CharField(max_length=100, blank=True, null=True)
#     dbl_apx_amount = models.FloatField(blank=True, null=True)
#     dbl_mrp_price = models.FloatField(blank=True, null=True)
#     dbl_myg_amount = models.FloatField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)
#     fk_item_group = models.ForeignKey(ItemGroup, models.DO_NOTHING, blank=True, null=True)
#     fk_category = models.ForeignKey(ItemCategory, models.DO_NOTHING, blank=True, null=True)
#     class Meta:
#         managed = True
#         db_table = 'items'

#     def __str__(self):
#         return "{}".format(self.vchr_item_name)
