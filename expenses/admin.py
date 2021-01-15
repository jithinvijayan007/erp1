from django.contrib import admin
from expenses.models import Expenses,ExpensesCategory

# Register your models here.

class ExpensesAdmin(admin.ModelAdmin):
    list_display = ['vchr_name','fk_category','fk_branch','bln_status']
    list_filter = ['bln_status','bln_recurring','bln_status']
    search_fields = ['vchr_name']
admin.site.register(Expenses,ExpensesAdmin)

class ExpensesCategoryAdmin(admin.ModelAdmin):
    list_display = ['vchr_category_name']
    search_fields = ['vchr_category_name']
admin.site.register(ExpensesCategory,ExpensesCategoryAdmin)
