from django.conf.urls import url
from salary_advance.views import AddSalaryAdvanceDetails,SalaryAdvanceApproval
urlpatterns = [
    url(r'^add_details/',AddSalaryAdvanceDetails.as_view(), name='add_details'),
    url(r'^approval/',SalaryAdvanceApproval.as_view(), name='approval'),


]
