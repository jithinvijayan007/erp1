from django.contrib import admin

# Register your models here.
from products.models import Products,Specifications
admin.site.register(Products)
admin.site.register(Specifications)
