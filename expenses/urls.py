from django.conf.urls import url
from expenses.views import AddExpensesAPIView,DeleteExpenseAPIView,ViewCategoryAPIView,AddExpensesAPI

urlpatterns = [
    url(r'^expense_api/$', AddExpensesAPIView.as_view(),name='expense_api'),
    url(r'^delete_expense/$', DeleteExpenseAPIView.as_view(),name='delete_expense'),
    url(r'^expenses_category/$',ViewCategoryAPIView.as_view(),name='expenses_category'),
    url(r'^add_payment_pos/$',AddExpensesAPI.as_view(),name='add_expenses_pos'),
]
