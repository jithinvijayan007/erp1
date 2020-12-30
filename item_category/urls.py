from django.conf.urls import url
from .views import ECommerceItemPriceAPI,ItemTypeHeadStock,ItemPriceAPI,ItemMopMrp,ItemCategoryAdd,GetTaxSpecification,ItemAdd,GetItemSpecData,ItemTypeHead,ListItemData,ItemCategoryTypeHead,ItemTypeaheadAPI,BiItemUpdateAPI,ItemTypeHeadWithProduct


urlpatterns = [
    url(r'^add_category/$', ItemCategoryAdd.as_view(), name='ItemCategoryAdd'),
    url(r'^get_item_category/$', GetTaxSpecification.as_view(), name='GetTaxSpecification'),
    url(r'^add_item/$', ItemAdd.as_view(), name='ItemAdd'),
    url(r'^get_itemspec/$', GetItemSpecData.as_view(), name='GetItemSpecData'),
    url(r'^item_typeahead/$', ItemTypeHead.as_view(), name='ItemTypeHead'),
    url(r'^item_typeahead_product/$', ItemTypeHeadWithProduct.as_view(), name='ItemTypeHeadWithProduct'),
    url(r'^list_item/$', ListItemData.as_view(), name='ListItemData'),
    url(r'^item_category_typeahead/$', ItemCategoryTypeHead.as_view(), name='ItemCategoryTypeHead'),
    url(r'^item_typeahead_api/$', ItemTypeaheadAPI.as_view(), name='item_typeahead_api'),
    url(r'^bi_item_update_api/$', BiItemUpdateAPI.as_view(), name='BiItemUpdateAPI'),
    url(r'^itemmopmrp/$', ItemMopMrp.as_view(), name='itemmopmrp'),
    url(r'^itempriceapi/$', ItemPriceAPI.as_view(), name='itempriceapi'),
    url(r'^item_typeahead_stock/$', ItemTypeHeadStock.as_view(), name='item_typeahead_stock'),
    url(r'^ecommerceitempriceapi/$', ECommerceItemPriceAPI.as_view(), name='itempriceapi'),

]
