
from django.conf.urls import url
from inventory.views import CategoryApiView, CategoryTypeahead, SubCategoryView,SubCategoryTypeahead,ProductView,GetProductById, SubCategoryByCat,itemBySub,itemByBrand,SynchronizeView,ProductTypeAhead,AddItemGroupApi,ItemGroupTypeahead,\
getStock,NearByStockCheck,ItemAgingCheck,ItemTypeahead,ProductSpecAPI
from rest_framework import routers
from inventory import views0_2

router = routers.DefaultRouter()
router.register(r'category', CategoryApiView)

urlpatterns = [
    url(r'^api_category_typeahead/$', CategoryTypeahead.as_view(),name='api_category'),
    url(r'^api_subcategory_typeahead/$', SubCategoryTypeahead.as_view(),name='api_subcategory'),
    url(r'^subcategory/$', SubCategoryView.as_view(),name='subcategory'),
    url(r'^product/$', ProductView.as_view(),name='product'),
    url(r'^get_product/$', GetProductById.as_view(),name='get_product'),
    url(r'^api_subcategory_by_cat/$', SubCategoryByCat.as_view(),name='api_subcategory_by_cat'),
    url(r'^api_item_by_sub/$', itemBySub.as_view(),name='api_item_by_sub'),
    # mobile app urls
    url(r'^v0.2/mobileItemsTypeahed/$',views0_2.MobileItemsTypeahed.as_view(),name='api_mobile_items_typeahed'),
    url(r'^v0.2/api_item_by_sub/$', views0_2.itemBySub.as_view(),name='api_item_by_sub'),
    url(r'^v0.2/api_scan_barcode/$', views0_2.barcodeScan.as_view(),name='api_scan_barcode'),
    url(r'^v0.2/MobileItemsWithBrandTypeahed/$',views0_2.MobileItemsWithBrandTypeahed.as_view(),name='api_mobile_items_brand_typeahed'),
    url(r'^api_item_by_brand/$', itemByBrand.as_view(),name='api_item_by_brand'),
    url(r'^api_product/$', ProductTypeAhead.as_view(),name='api_product'),
    url(r'^synchronize/$', SynchronizeView.as_view(),name='synchronize'),
    url(r'^item_group/$', AddItemGroupApi.as_view(),name='item_group'),
    url(r'^item_group_typeahead/$', ItemGroupTypeahead.as_view(),name='item_group_typeahead'),
    url(r'^api_stock_by_item/$', getStock.as_view(),name='api_stock_by_item'),
    url(r'^nearbystockbranch/$', NearByStockCheck.as_view(),name='NearByStockCheck'),
    url(r'^itemagingcheck/$', ItemAgingCheck.as_view(),name='ItemAgingCheck'),
    url(r'^item_typeahead/$',ItemTypeahead.as_view(),name='item_typeahead'),
    url(r'^set_product_specs/$',ProductSpecAPI.as_view(),name='ProductSpecAPI'),
]
urlpatterns += router.urls
