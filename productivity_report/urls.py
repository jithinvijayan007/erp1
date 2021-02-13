from django.conf.urls import url
from productivity_report.views import ProductivityReport,ProductivityReportMobile,ProductivityReportMobileTable,ProductProductivityReport,ProductivityReportTableData,  ItemTypehead, BrandTypehead,ProductTypehead,PromoterTypehead,ProductTypeheadGDP
from productivity_report import views0_1_1, views0_2

urlpatterns = [
    url(r'^$', ProductivityReport.as_view(), name='productivityreport'),
    url(r'^mobile', ProductivityReportMobile.as_view(), name='productivityreport-mobile'),
    url(r'^productivitytabledata', ProductivityReportMobileTable.as_view(), name='tableproductivitymobile'),
    url(r'^productdata', ProductProductivityReport.as_view(), name='productdata'),
    url(r'^product_table_data', ProductivityReportTableData.as_view(), name='product_table_data'),
    url(r'^list_brand', BrandTypehead.as_view(), name='list_brand'),
    url(r'^list_promoter', PromoterTypehead.as_view(), name='list_brand'),
    url(r'^list_item', ItemTypehead.as_view(), name='list_item'),
    url(r'^product_api_gdp', ProductTypeheadGDP.as_view(), name='product_api_gdp'),
    url(r'^product_api', ProductTypehead.as_view(), name='product_api'),
    # mobile app urls
    url(r'^v0.1.1/$', views0_1_1.ProductivityReport.as_view(),name='productivityreport0.1.1'),
    url(r'^v0.2/$', views0_2.ProductivityReport.as_view(),name='productivityreport0.2'),
]
