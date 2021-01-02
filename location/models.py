from django.db import models

# Create your models here.
class Country(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=15, blank=True, null=True)
    vchr_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'country'
    def __str__(self):
        return self.vchr_name


class State(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=15, blank=True, null=True)
    vchr_name = models.CharField(max_length=50, blank=True, null=True)
    fk_country = models.ForeignKey(Country, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'states'
    def __str__(self):
        return self.vchr_name


class District(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=15, blank=True, null=True)
    vchr_name = models.CharField(max_length=50, blank=True, null=True)
    fk_state = models.ForeignKey(State, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'district'
    def __str__(self):
        return self.vchr_name


class PhysicalLocation(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_physical_loc = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'physical_location'
    def __str__(self):
        return self.vchr_physical_loc
