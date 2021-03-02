from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import GeneralizeStatusReport,GetChartDetails

urlpatterns = [
    url(r'^report_download/$',GeneralizeStatusReport.as_view(),name='report_download'),
    url(r'^get_chart_data/$',GetChartDetails.as_view(),name='get_chart_data'),
    ]
