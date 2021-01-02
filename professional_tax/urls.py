from django.conf.urls import url
from professional_tax.views import ProfessionalTaxAdd,PtPeriodList,UpdatePtPeriod
urlpatterns = [
    url(r'^add/',ProfessionalTaxAdd.as_view(), name='add'),
    url(r'^period_list/',PtPeriodList.as_view(), name='period_list'),
    url(r'^update_period/',UpdatePtPeriod.as_view(), name='update_period'),


]
