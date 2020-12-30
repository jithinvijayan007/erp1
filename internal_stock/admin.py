from django.contrib import admin

# Register your models here.
from internal_stock.models import StockRequest,StockTransfer,IsrDetails,IstDetails
# Register your models here.
admin.site.register(StockRequest)
admin.site.register(StockTransfer)
admin.site.register(IsrDetails)
admin.site.register(IstDetails)
