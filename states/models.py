from django.db import models

# Create your models here.
class Country(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=15, blank=True, null=True)
    vchr_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'country'
class States(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=20, blank=True, null=True)
    vchr_code = models.CharField(max_length=100, blank=True, null=True)
    fk_country = models.ForeignKey(Country, models.DO_NOTHING, blank=True, null=True)
    def __str__(self):
        return self.vchr_name

    class Meta:
        managed = False
        db_table = 'states'


class District(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    fk_state = models.ForeignKey(States, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'district'
    def __str__(self):
        return self.vchr_name


class Location(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    vchr_pin_code = models.CharField(max_length=10, blank=True, null=True)
    vchr_district = models.CharField(max_length=50, blank=True, null=True)
    fk_state = models.ForeignKey(States, models.DO_NOTHING, blank=True, null=True)
    vchr_state = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location'
    def __str__(self):
        return self.vchr_name


class LocationMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    int_code = models.BigIntegerField(blank=True, null=True)
    vchr_location = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location_master'
