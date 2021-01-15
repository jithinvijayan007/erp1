from django.conf.urls import url

from enquiry_mobile.views import AddImei,PendingEnquiryList,SaveEnquiry,EnquiryInvoicedSave, PendingEnquiryListSide,PendingEnquiryListUser,AssignEnquiry,AddEnquiry,GetDetailsForAddMobileLead,getProductPrice,getItemStock,SavePartialAmount,SaveOfferDetails,UpdateGdp,EnquiryFinanceImage,EnquiryInvoiceUpdate,BookCreditEnquiry,AddReturnItemEnquiry,CreateExchangeItem,AddCreditPayment
from enquiry_mobile import views0_1
from enquiry_mobile import views0_2
from enquiry_mobile import views0_3
urlpatterns=[
    url(r'^add_mobile_enquiry/$',AddEnquiry.as_view(),name='add_mobile_enquiry'),
    url(r'^invoiced_enquiry/$',EnquiryInvoicedSave.as_view(),name='invoiced_enquiry'),
    url(r'^pending_enquiry_list/$', PendingEnquiryList.as_view(),name='pending_enquiry_list'),
    url(r'^pending_enquiry_list_side/$', PendingEnquiryListSide.as_view(),name='pending_enquiry_list_side'),

    url(r'^pending_enquiry_list_user/$', PendingEnquiryListUser.as_view(),name='pending_enquiry_list_user'),
    url(r'^assign_enquiry/$', AssignEnquiry.as_view(),name='assign_enquiry'),
    url(r'^get_for_add_mobile_enquiry/$', GetDetailsForAddMobileLead.as_view(),name='get_for_add_mobile_enquiry'),
    url(r'^get_price_for_product/$', getProductPrice.as_view(),name='get_price_for_product'),
    url(r'^get_stock_for_item/$', getItemStock.as_view(),name='get_stock_for_item'),
    url(r'^updategdp/$',UpdateGdp.as_view(),name='updategdp'),
    url(r'^enquiry_finance_image/$',EnquiryFinanceImage.as_view(),name='enquiry_finance_image'),
    url(r'^enquiry_invoice_update/$',EnquiryInvoiceUpdate.as_view(),name='enquiry_invoice_update'),
    url(r'^book_credit_enquiry/$',BookCreditEnquiry.as_view(),name='book_credit_enquiry'),



    # mobile app urls
    url(r'^v0.1/add_enquiry/$',views0_1.AddEnquiry.as_view(),name='add_enquiry'),
    url(r'^v0.1/add_followup/$',views0_1.AddFollowup.as_view(),name='add_followup'),
    url(r'^v0.1/products/$',views0_1.ProductList.as_view(),name='products'),
    url(r'^v0.1/enquiry_list/$',views0_1.EnquiryList.as_view(),name='enquiry_list'),
    url(r'^v0.1/enquiry_view/$',views0_1.EnquiryView.as_view(),name='enquiry_view'),
    url(r'^v0.1/pending_enquiry_list_side/$', views0_1.PendingEnquiryListSide.as_view(),name='pending_enquiry_list_side'),
    url(r'^v0.1/source_priority_list/$', views0_1.Source_PriorityAPIView.as_view(),name='Source_Priority'),
    url(r'^v0.1/item_amount/$', views0_1.getProductPrice.as_view(),name='item_amount'),
    url(r'^v0.1/mobile_enquiry_data/$',views0_1.GetDataForMobileEnquiry.as_view(),name='mobile_enquiry_data'),
    url(r'^v0.3/enquiry_list/$',views0_3.EnquiryList.as_view(),name='enquiry_list'),
    url(r'^v0.3/enquiry_view/$',views0_3.EnquiryView.as_view(),name='enquiry_list'),
    url(r'^v0.3/add_followup/$',views0_3.AddFollowup.as_view(),name='add_followup'),
    url(r'^v0.3/mobile_enquiry_data/$',views0_3.GetDataForMobileEnquiry.as_view(),name='mobile_enquiry_data'),
    url(r'^v0.3/branchTypeahed/$',views0_3.BranchTypeahed.as_view(),name='branchTypeahed'),
    url(r'^v0.3/add_enquiry/$',views0_3.AddEnquiry.as_view(),name='add_enquiry'),
    url(r'^v0.3/gdprange/$',views0_3.GDPRangeGET.as_view(),name='gdprange'),
    url(r'^save_ball_game_amt/$',SavePartialAmount.as_view(),name='save_ball_game_amt'),
    url(r'^save_offer_details/$',SaveOfferDetails.as_view(),name='save_offer_details'),
    url(r'^add_imei/$',AddImei.as_view(),name='add_imei'),

    url(r'^add_return_item_enquiry/$',AddReturnItemEnquiry.as_view(),name='add_return_item_enquiry'), # pos

    #Exchange hits from POS
    url(r'^create_exchange_item/$',CreateExchangeItem.as_view(),name='create_exchange_item'),
    url(r'^addpayment/$',AddCreditPayment.as_view(),name='addpayment'),

]
