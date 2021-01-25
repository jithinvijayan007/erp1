
from transaction.views import create_invoice_posting_data,create_posting_data,create_return_posting_data
from sap_api.models import SapApiTrack
import inflect
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from userdetails.models import UserDetails as Userdetails,GuestUserDetails,Financiers
from django.contrib.auth import authenticate, login
from company.models import Company
from brands.models import Brands
from groups.models import Groups
from branch.models import Branch
from django.db.models import F, Func, Value, CharField
from products.models import Products
import copy
from django.contrib.auth.models import User
from random import randint
from accounts_map.models import AccountsMap

from django.core.files.storage import FileSystemStorage
from django.db.models import Q, Value, BooleanField, Case, When,IntegerField,CharField,Sum,F
from django.db.models.functions import Concat,Coalesce

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from invoice.models import PartialInvoice,TheftDetails
from customer.models import CustomerDetails,SalesCustomerDetails
from invoice.models import PartialInvoice, SalesMaster, SalesDetails, CustServiceDelivery, LoyaltyCardInvoice, FinanceDetails,PaymentDetails,SalesMasterJio,Bank,TheftDetails,Depreciation,FinanceScheme
from item_category.models import Item,TaxMaster,ItemCategory
from loyalty_card.models import LoyaltyCard, LoyaltyCardStatus
from company.models import FinancialYear,Company
from purchase.models import Document
from purchase.views import doc_num_generator
from states.models import States, Location, District
from purchase.models import GrnDetails,GrnMaster
from branch_stock.models import BranchStockDetails, BranchStockImeiDetails,BranchStockMaster
from sales_return.models import SalesReturn
from pricelist.models import PriceList
from coupon.models import Coupon
from datetime import datetime,date,timedelta
from collections import OrderedDict
from django.db.models import Q,Case,When,Value,CharField,Count,Sum
from sqlalchemy.orm.session import sessionmaker
from aldjemy.core import get_engine
from django.conf import settings
from POS import ins_logger
from django.db import transaction
from django.db.models.functions import Concat
import sys, os
import requests
from loyalty_card.views import loyalty_card
# Create your views here.
from sqlalchemy.orm import sessionmaker
import aldjemy
from sqlalchemy.orm.session import sessionmaker
# from sqlalchemy.sql.expression import cast
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date,case, literal_column,or_,MetaData,desc
import sqlalchemy
from sqlalchemy.sql.expression import literal,union_all
from django.contrib.auth.models import User as AuthUser
from terms.models import Terms,Type

from POS.dftosql import Savedftosql
import pdfkit
import base64
import json
from dateutil.relativedelta import relativedelta

from receipt.models import ReceiptInvoiceMatching,Receipt,PartialReceipt
from tool_settings.models import Tools

from os import remove
from django.core.mail import EmailMultiAlternatives
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import re

from django.db.models import Q

from internal_stock.models import StockTransfer,IstDetails
from internal_stock.views import print_transfer_recipt

from exchange_sales.models import ExchangeStock

from PyPDF2 import PdfFileWriter, PdfFileReader
from global_methods import get_user_privileges,check_if_imei_exist
import pyqrcode
import png
from pyqrcode import QRCode


from enquiry.models import EnquiryMaster
from enquiry_mobile.models import ItemEnquiry, ItemFollowup
from staff_rewards.models import RewardsAvailable
from invoice.models import GDPRange
from reminder.models import Reminder


PartialInvoiceSA = PartialInvoice.sa
SalesMasterSA = SalesMaster.sa
SalesDetailsSA = SalesDetails.sa
SalesReturnSA = SalesReturn.sa
BranchSA = Branch.sa
CustomerDetailsSA = CustomerDetails.sa
SalesCustomerDetailsSA = SalesCustomerDetails.sa
CustServiceDeliverySA = CustServiceDelivery.sa
AuthUserSA = AuthUser.sa
ItemsSA = Item.sa
BrandSA = Brands.sa
ProductsSA = Products.sa
SalesMasterJioSa = SalesMasterJio.sa
UserdetailsSA=Userdetails.sa
CompanySA=Company.sa
StatesSA=States.sa
ItemCategorySA = ItemCategory.sa

sqlalobj = Savedftosql('','')
engine = sqlalobj.engine
metadata = MetaData()
metadata.reflect(bind=engine)
Connection = sessionmaker()
Connection.configure(bind=engine)

PartialInvoiceJS = metadata.tables['partial_invoice']
SalesMasterJS = metadata.tables['sales_master']
SalesDetailsJS = metadata.tables['sales_details']
SalesMasterJioJS = metadata.tables['sales_master_jio']
CustServiceDeliveryJS = metadata.tables['cust_service_delivery']
TermsJS = metadata.tables['terms']

engine = get_engine()
def Session():
    _Session = sessionmaker(bind = engine)
    return _Session()

def tools_keys(dct_data,request):

        """adddition and deduction on admin tools"""
        if 'intBranchId' in dct_data.keys():
            rst_admin_tools = list(Tools.objects.filter(vchr_tool_code__in =("ADDITION","DEDUCTION"),dat_from__date__lte=datetime.now().date(),dat_to__date__gte=datetime.now().date(),jsn_data__icontains = dct_data['intBranchId']).extra(select={'name': "jsonb_array_elements(jsn_keys)",'value': 0 }).values('name','value','vchr_tool_code').order_by('vchr_tool_code'))
        else:
            rst_admin_tools = list(Tools.objects.filter(vchr_tool_code__in =("ADDITION","DEDUCTION"),dat_from__date__lte=datetime.now().date(),dat_to__date__gte=datetime.now().date()).extra(select={'name': "jsonb_array_elements(jsn_keys)",'value': 0 }).values('name','value','vchr_tool_code').order_by('vchr_tool_code'))
        dct_data['admin_tools']={}
        dct_data['admin_tools']['ADDITION']=[]
        dct_data['admin_tools']['DEDUCTION']=[]
        for data in rst_admin_tools:
            if data['vchr_tool_code']=='ADDITION':
                dct_data['admin_tools']['ADDITION'].append(data)
            if data['vchr_tool_code']=='DEDUCTION':
                dct_data['admin_tools']['DEDUCTION'].append(data)
        return dct_data

class SalesList(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request):
        try:

            dat_to = (datetime.strptime(request.data.get("datTo")[:10],'%Y-%m-%d')).date()
            dat_from = (datetime.strptime(request.data.get("datFrom")[:10],'%Y-%m-%d')).date()

            
            if request.data.get('blnService'):
                if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    ins_partial_inv = PartialInvoice.objects.filter(int_status__in=(3,5,6,10),int_active=0,int_approve__in=(0,2,4),dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-pk_bint_id')
                else:
                    ins_partial_inv = PartialInvoice.objects.filter(int_status__in=(3,5,6,10),int_active=0,int_approve__in=(0,2,4),dat_created__date__gte = dat_from,dat_created__date__lte = dat_to,json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id}).values('pk_bint_id','dat_created','json_data','int_status').order_by('-pk_bint_id')

            elif request.data.get('blnBajaj') :
                if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    ins_partial_inv = PartialInvoice.objects.filter(int_status=11,int_active = 0,int_approve__in=(0,2),dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
                else:
                    ins_partial_inv = PartialInvoice.objects.filter(int_status=11,int_active = 0,int_approve__in=(0,2),json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id},dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')

            elif request.data.get('ecom_api') :
                if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    ins_partial_inv = PartialInvoice.objects.filter(int_status=20,int_sale_type =1,int_active = 0,dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
                else:
                    ins_partial_inv = PartialInvoice.objects.filter(int_status=20,int_sale_type =1,int_active = 0,json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id},dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')




            else:
                if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    ins_partial_inv = PartialInvoice.objects.filter(~Q(json_data__contains={'bln_specialsale':'True'}),int_active = 0,int_approve__in=(0,2,4),dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).exclude(int_status__in=(3,6,5,10,11,20)).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
                else:
                    ins_partial_inv = PartialInvoice.objects.filter(Q(json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id}) & ~Q(json_data__contains={'bln_specialsale':'True'}),int_active = 0,int_approve__in=(0,2,4,3),dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).exclude(int_status__in=(3,6,5,10,11,20)).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')

            #--------------------
            lst_branch_id = []
            ins_tool = Tools.objects.filter(vchr_tool_code='ALLOW_SERVICER_PRINT').values('jsn_data').first()
            if  ins_tool:
                if ins_tool['jsn_data']:
                    lst_branch_id = ins_tool['jsn_data']
            #--------------------
            lst_data = []
            dct_branch = dict(Branch.objects.values_list('pk_bint_id','vchr_name'))
            lst_cust_id = [data['json_data']['int_cust_id'] for data in ins_partial_inv]
            dct_customer = dict(CustomerDetails.objects.filter(pk_bint_id__in=lst_cust_id).values_list('pk_bint_id','int_cust_type'))

            for ins_data in ins_partial_inv:

                dct_data = {}

                dct_data['blnSez'] = True if dct_customer[ins_data['json_data'].get('int_cust_id')]==3 else False
                dct_data['intId'] = ins_data['pk_bint_id']
                dct_data['datBooked'] = ins_data['dat_created'].strftime("%d-%m-%Y")
                dct_data['strCustomer'] = ins_data['json_data']['str_cust_name'].title()

                dct_data['strStaff'] = ins_data['json_data'].get('str_staff_name').title()
                dct_data['strEnqNo'] = ins_data['json_data'].get('vchr_enquiry_num')
                dct_data['branch'] = dct_branch.get(ins_data['json_data'].get('int_branch_id'))
                if request.user.userdetails.fk_group.vchr_name.upper() in ['SERVICE MANAGER','SERVICE ENGINEER','BRANCH MANAGER','ASSISTANT BRANCH MANAGER','ADMIN']:
                    if ins_data['json_data'].get('int_branch_id') in lst_branch_id and ins_data['json_data']['lst_items'][0].get('vchr_job_status') not in ['GDP NORMAL NEW','GDEW NEW','CHECKED']:
                        dct_data['bln_view'] = True
                    elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ADMIN']:
                        dct_data['bln_view'] = True
                    else:
                        dct_data['bln_view'] = False
                else:
                        dct_data['bln_view'] = False


                dct_data['sales_status'] = ins_data['int_status']
                dct_data['strItem'] = ''
                dct_data['strItem'] = ' , '.join([ i['vchr_item_name']for i in ins_data['json_data']['lst_items']])
                if request.data.get('blnService'):
                    # dct_data['datBooked'] = datetime.strftime(datetime.strptime(ins_data['json_data']['dat_created_at'],'%Y-%m-%d'),"%d-%m-%Y") if ins_data['json_data'].get('dat_created_at') else ''
                    dct_data['int_service_id']= ins_data['json_data']['lst_items'][0]['int_service_id'] if ins_data['json_data']['lst_items'][0].get('int_service_id') else ''
                    dct_data['vchr_status']= ins_data['json_data']['lst_items'][0]['vchr_job_status'] if ins_data['json_data']['lst_items'][0].get('vchr_job_status') else ''
                    dct_data['vchr_job_num']=ins_data['json_data'].get('vchr_job_num') or "---"

                    if dct_data['vchr_status'] == 'SERVICED & DELIVERED':
                        dct_data['sales_status'] = 7 # if servie is SERVICED & DELIVERED

                if len(dct_data['strItem'])>30:
                    dct_data['strItem'] = dct_data['strItem'][:30]+'...'

                lst_data.append(dct_data)
            return Response({'status':1,'data':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

    def post(self,request):
        try:
            
            int_id = request.data.get('intId')
            ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = int_id,int_active = 0).exclude(int_approve__in=[5]).values('dat_created','json_data','int_status','int_approve','json_updated_data').first()
            if not ins_partial_inv:
                return Response({'status':'0','message':'Already Invoiced'})
            dct_data = {}
            ins_customer = SalesCustomerDetails.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_sales_cust_id']).values('pk_bint_id','fk_customer_id','fk_customer__dbl_credit_balance','fk_customer__int_cust_type','vchr_name','vchr_email','int_mobile','txt_address','vchr_gst_no','fk_location__vchr_name','fk_location__vchr_pin_code','fk_location_id','fk_state_id','fk_state__vchr_name','int_loyalty_points','int_redeem_point','fk_customer__int_edit_count','int_cust_type').first()
            # ================================================================================
            if ins_partial_inv['json_data']['int_branch_id']:
                dct_data['intBranchId'] = ins_partial_inv['json_data']['int_branch_id']
            dct_data['intSalesCustId'] =  ins_customer['pk_bint_id']
            dct_data['edit_count']=ins_customer['fk_customer__int_edit_count']
            if ins_partial_inv['int_approve'] in [1,2,3,4]:
                ins_partial_inv['json_data'] = ins_partial_inv['json_updated_data']
            # ================================================================================
            dct_data['intStaffId'] = ins_partial_inv['json_data']['int_staff_id']
            dct_data['strStaffName'] = Userdetails.objects.filter(user_ptr_id = ins_partial_inv['json_data']['int_staff_id']).annotate(str_name=Concat('first_name', Value(' '), 'last_name')).values('str_name').first()['str_name'] if Userdetails.objects.filter(user_ptr_id = ins_partial_inv['json_data']['int_staff_id']) else ''
            dct_data['intContactNo'] = ins_customer['int_mobile']
            dct_data['intCustId'] = ins_customer['fk_customer_id']

            dct_data['strCustName'] = ins_customer['vchr_name']
            dct_data['strCustEmail'] = ins_customer['vchr_email']
            dct_data['txtAddress'] = ins_customer['txt_address']
            dct_data['strGSTNo'] = ins_customer['vchr_gst_no']
            dct_data['intLocation'] = ins_customer['fk_location_id']
            dct_data['strLocation'] = ins_customer['fk_location__vchr_name']
            dct_data['intPinCode'] = ins_customer['fk_location__vchr_pin_code']
            dct_data['intState'] = ins_customer['fk_state_id']
            dct_data['strState'] = ins_customer['fk_state__vchr_name']
            dct_data['int_enquiry_type'] = ins_partial_inv['json_data'].get('int_enquiry_type',0)
            dct_data['vchr_reference_num'] = ins_partial_inv['json_data'].get('vchr_reference_num',None)
            dct_data['dbl_loyalty_amt'] =  ins_partial_inv['json_data'].get('dbl_loyalty_amt',None)
            dct_data['vchr_order_num'] = ins_partial_inv['json_data'].get('vchr_order_num',None)
            dct_data['txtRemarks'] = ins_partial_inv['json_data']['str_remarks']
            rst_recpts = Receipt.objects.filter(fk_customer = ins_customer['fk_customer_id'],int_doc_status__in=[0,1]).exclude(fk_customer__int_cust_type=1).values('pk_bint_id')
            lst_invoiced_recpts = list(ReceiptInvoiceMatching.objects.filter(fk_sales_master__fk_customer_id__fk_customer_id=ins_customer['fk_customer_id']).exclude(fk_sales_master__fk_customer_id__fk_customer_id__int_cust_type=1).values_list('fk_receipt_id',flat=True))
            cmp_rceipts = rst_recpts.exclude(pk_bint_id__in=lst_invoiced_recpts)
            dct_data['bln_status'] = True if cmp_rceipts else False
            dct_data['int_status'] = ins_partial_inv['int_status']
            dct_data['int_approve'] = ins_partial_inv['int_approve']
            # LG
            
            if request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER'] and ins_partial_inv['int_approve'] in [3]:
                dct_data['bln_approve'] = True
            elif request.data.get('int_approve') in [2,4]:
                dct_data['bln_approve']=True
            else:
                dct_data['bln_approve'] = False
            dct_data['sales_status'] = ins_partial_inv['int_status']
            dct_data['dbl_credit_balance'] = ins_customer['fk_customer__dbl_credit_balance'] or 0
            dct_data['int_cust_type'] = ins_customer['fk_customer__int_cust_type'] or 0
            dct_data['lst_fin_data'] = []
            dct_data['dbl_total_fin_amount'] = 0
            if ins_partial_inv['int_status']==3:
                dct_data['lst_advc_paid']=Receipt.objects.filter(fk_customer__int_mobile=ins_customer['int_mobile']).values('pk_bint_id','dbl_amount')
            dct_data['intLoyaltyPoint'] = (ins_customer['int_loyalty_points'] if ins_customer['int_loyalty_points'] else 0)- (ins_customer['int_redeem_point'] if ins_customer['int_redeem_point'] else 0)
            dct_data['job_status']=ins_partial_inv['int_status']
            dct_data['partial_id'] = int_id
            bln_kfc = False
            if ins_customer['fk_state_id'] == request.user.userdetails.fk_branch.fk_states_id and not ins_customer['vchr_gst_no']:
                bln_kfc = True
            
            if ins_partial_inv['json_data'].get('offerName'):
                dct_data['offerName'] = ins_partial_inv['json_data'].get('offerName')
            if ins_partial_inv['json_data'].get('partial_amt'):
                dct_data['partialAmount'] = ins_partial_inv['json_data'].get('partial_amt')
            if ins_partial_inv['json_data'].get('offerId'):
                dct_data['offerId'] = ins_partial_inv['json_data'].get('offerId')
            dct_data['offerAmt'] = ins_partial_inv['json_data'].get('offerAmt')
            if ins_partial_inv['json_data'].get('lst_offers'):
                dct_data['lst_offers'] = [{'offer':int(data['offerName'].split("%")[0]) if  data['bln_item'] else None,'offerName':data['offerName'],'offerId':data['offerId'],'bln_item':data['bln_item']} for data in ins_partial_inv['json_data'].get('lst_offers')]
            if ins_partial_inv['json_data'].get('vchr_finance_name') or ins_partial_inv['json_data'].get('vchr_finance_schema') or ins_partial_inv['json_data'].get('dbl_finance_amt') or ins_partial_inv['json_data'].get('vchr_fin_ordr_num'):
                dct_data['vchrFinanceName'] = ins_partial_inv['json_data']['vchr_finance_name']
                dct_data['vchrFinanceSchema'] = ins_partial_inv['json_data']['vchr_finance_schema']
                dct_data['dblFinanceAmt'] = ins_partial_inv['json_data']['dbl_finance_amt']
                dct_data['dblEMI'] = ins_partial_inv['json_data']['dbl_emi']
                dct_data['dblDownPayment'] = int(ins_partial_inv['json_data']['dbl_down_payment']) if ins_partial_inv['json_data'].get('dbl_down_payment') and ins_partial_inv['json_data'].get('dbl_down_payment') !='' else 0
                dct_data['int_fin_id']=''
                dct_data['lst_fin_data'] = [{'name':'Margin money','value':ins_partial_inv['json_data']['dbl_margin_money'] or 0},
                                {'name':'Down Payment','value':int(ins_partial_inv['json_data']['dbl_down_payment']) if ins_partial_inv['json_data'].get('dbl_down_payment') and ins_partial_inv['json_data'].get('dbl_down_payment') !='' else 0},
                                {'name':'Processing fee','value':ins_partial_inv['json_data']['dbl_processing_fee'] or 0},
                                {'name':'DBD charge','value':ins_partial_inv['json_data']['dbl_dbd_amount'] or 0},
                                {'name':'Service charge','value':ins_partial_inv['json_data']['dbl_service_charge'] or 0},
                                ]
                lst_fin_data = [int(ins_partial_inv['json_data']['dbl_down_payment']) if ins_partial_inv['json_data'].get('dbl_down_payment') and ins_partial_inv['json_data'].get('dbl_down_payment') !='' else 0,ins_partial_inv['json_data']['dbl_processing_fee'],ins_partial_inv['json_data']['dbl_dbd_amount'],ins_partial_inv['json_data']['dbl_service_charge']]
                dct_data['dbl_total_fin_amount'] = sum(filter(None, lst_fin_data))
                ins_finance =Financiers.objects.filter(vchr_code=ins_partial_inv['json_data'].get('vchr_fin_comp'))
                if ins_finance:
                    dct_data['int_fin_id'] =ins_finance[0].pk_bint_id
                else:
                    ins_finance=Financiers.objects.create(vchr_code=ins_partial_inv['json_data'].get('vchr_fin_comp'),vchr_name=ins_partial_inv['json_data']['vchr_finance_name'],bln_active=True)
                    dct_data['int_fin_id'] =ins_finance.pk_bint_id

                # dct_data['vchrFinOrdrNum'] = ins_partial_inv['json_data']['vchr_fin_ordr_num']
                # LG
                dct_data['vchrFinOrdrNum'] = ins_partial_inv['json_data'].get('vchr_fin_ordr_num',None)
            dct_data['intAmtPerPoints'] = 1/settings.LOYALTY_POINT
            dct_data['lstItems'] = []
            dct_data['blnIGST'] = False
            
            rst_branch_state_code=Branch.objects.get(pk_bint_id=ins_partial_inv['json_data']['int_branch_id']).fk_states_id
            if rst_branch_state_code != ins_customer['fk_state_id']:
            # if request.user.userdetails.fk_branch.fk_states_id != ins_customer['fk_state_id']:
                dct_data['blnIGST'] = True
            dct_tax_master = {}
            dct_data['dbl_kfc_amount'] = 0.0
            
            dct_data['dblBalanceAmount'] = int(ins_partial_inv['json_data'].get('dbl_balance_amt') if  ins_partial_inv['json_data'].get('dbl_balance_amt') else 0)
            dct_data['dblPartialAmount'] = int(str(ins_partial_inv['json_data'].get('dbl_partial_amt')).replace(',','') if ins_partial_inv['json_data'].get('dbl_partial_amt') else 0 )

            if ins_partial_inv['json_data'].get('int_credit_sale'):
                    dct_data['int_credit_sale'] = int(ins_partial_inv['json_data'].get('int_credit_sale'))

            for ins_tax in TaxMaster.objects.values('pk_bint_id','vchr_name'):
                dct_tax_master[ins_tax['vchr_name']] = str(ins_tax['pk_bint_id'])
            for ins_items_data in ins_partial_inv['json_data']['lst_items']:
                ins_items = Item.objects.filter(vchr_item_code = ins_items_data['vchr_item_code'],int_status=0).values('pk_bint_id','dbl_mrp','vchr_name','vchr_item_code','fk_item_category__json_tax_master','imei_status','fk_product__vchr_name').first()

                if not ins_items:
                    return Response({'status':'0','message':'Item Not Found'})
                for row in range(int(ins_items_data['int_quantity'])):
                    if bln_kfc and ins_items['fk_item_category__json_tax_master']:
                        ins_kfc = TaxMaster.objects.filter(vchr_name__iexact='KFC').values('pk_bint_id')
                        if ins_kfc:
                            ins_items['fk_item_category__json_tax_master'][str(ins_kfc[0]['pk_bint_id'])] = 1

                    dct_item = {}
                    dct_item['strItemCode'] = ins_items['vchr_item_code']
                    dct_item['intItemId'] = ins_items['pk_bint_id']
                    dct_item['strItemName'] = ins_items['vchr_name']
                    dct_item['dblMarginAmount'] = ins_items_data.get('dbl_margin_amount',0)

                    dct_item['intQuantity'] = ins_items_data['int_quantity']
                    dct_item['intStatus'] = ins_items_data['int_status']
                    dct_item['imeiStatus'] = ins_items['imei_status']
                    dct_item['mrp'] = ins_items['dbl_mrp']
                    dct_item['vchr_product_name'] = ins_items['fk_product__vchr_name']
                    if dct_item['strItemCode'] in ['GDC00001','GDC00002'] :
                            dct_item['imeiStatus']=True
# <<<<<<< HEAD
                    # dct_item['itemEnqId'] = ins_items_data['item_enquiry_id']
                    dct_item['itemEnqId'] = ins_items_data.get('item_enquiry_id') # conflicted code
                    if ins_partial_inv['int_status'] == 3:

                        dbl_total_spare = 0
                        dct_data['lst_spare'] = []
                        dct_data['dbl_total_spare'] = 0
                        dct_data['dbl_advc_paid'] = ins_partial_inv['json_data']['lst_items'][-1]['dbl_advc_paid']
                        # if ins_items_data.get('lst_spare'):
                        #     lst_spare = []
                        for ins_spare in  ins_partial_inv['json_data']['lst_items'][0:-2]:
                            # dct_spare = {}
                            # dct_spare['str_item_name'] = ins_spare['fk_item_id__vchr_item_name']
                            # dct_spare['dbl_amount'] = ins_spare['dbl_amount'] or 0
                            dbl_total_spare = dbl_total_spare +  ins_spare['dbl_amount'] or 0
                            # lst_spare.append(dct_spare)
                        # dct_data['lst_spare'] = lst_spare
                        dct_data['lst_spare'] = []
                        dct_data['dbl_total_spare'] = dbl_total_spare


                        dbl_rate = ins_items_data['dbl_amount']
                        dbl_discount = ins_items_data['dbl_discount']
                        dct_item['dblBuyBack'] = 0
                        dct_item['dblRate'] = 0
                        dct_item['dblDiscount'] = round(dbl_discount,2)
                        # conflicted

                        dct_item['dblIGSTPer'] = 0.0
                        dct_item['dblCGSTPer'] = 0.0
                        dct_item['dblSGSTPer'] = 0.0
                        dct_item['dblIGST'] = 0.0
                        dct_item['dblCGST'] = 0.0
                        dct_item['dblSGST'] = 0.0
                        #--------------check--------------------------------------------------
                        if dct_data['blnIGST']:
                            dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))/100)
                            dct_item['dblIGSTPer'] = round(float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0)),2)
                            dct_item['dblIGST'] = round(dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0)/100),2)
                        if ins_items['fk_item_category__json_tax_master'] and bln_kfc:
                            dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['KFC'],0))/100)
                            dct_data['dbl_kfc_amount'] += dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['KFC'],0)/100)
                            dbl_item_kfc = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['KFC'],0)/100)
                            dct_item['dblSGSTPer'] = dct_item['dblCGSTPer'] = round(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST']),2)
                            dct_item['dblSGST'] = dct_item['dblCGST'] = round(dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)/100),2)

                        elif ins_items['fk_item_category__json_tax_master'] and not bln_kfc:
                            dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))/100)
                            dct_item['dblSGSTPer'] = dct_item['dblCGSTPer'] = round(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST']),2)
                            dct_item['dblSGST'] = dct_item['dblCGST'] = round(dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)/100),2)
                        else:
                            dct_item['dblSGSTPer'] = dct_item['dblCGSTPer'] =0
                            dct_item['dblSGST'] = dct_item['dblCGST'] = 0
                        #--------------check--------------------------------------------------

                        dct_item['strImei'] = '---'
                        if ins_items_data.get('vchr_imei'):
                            dct_item['strImei'] = ins_items_data['vchr_imei']
                        elif ins_items_data.get('json_imei'):
                            if ins_items_data.get('json_imei').get('imei'):
                                if len(ins_items_data.get('json_imei').get('imei'))>0:
                                    dct_item['strImei'] = ins_items_data.get('json_imei').get('imei')[0]

                        dct_item['dblAmount'] = round(dbl_rate-dbl_discount,2)

                        # dct_data['lstItems'].append(dct_item)


                        if dct_data['blnIGST']:
                            dct_item['GST'] = dct_item['dblIGSTPer']
                        else :
                            dct_item['GST'] = dct_item['dblSGSTPer'] +  dct_item['dblCGSTPer']

                        dct_item['dblMopAmount'] = dbl_rate
                        dct_data['lstItems'].append(dct_item)
                    else:
                        if ins_items_data['int_status'] == 2:

                            dct_item['dctImages'] = ins_items_data.get('dct_images')
                            dct_item['blnVerified'] = False
                        
                        if len(ins_items_data['json_imei']['imei'])>0:
                            dct_item['strImei'] = ins_items_data['json_imei']['imei'][row]
                            ins_grn_details = GrnDetails.objects.filter(fk_item_id=ins_items['pk_bint_id'],jsn_imei_avail__contains={'imei_avail':[dct_item['strImei']]}).values('jsn_tax').last()
                        # else:
                        #     ins_grn_details = GrnDetails.objects.filter(fk_item_id=ins_items['pk_bint_id'],vchr_batch_no=dct_item['strBatchNo']).values('jsn_tax').last()
                        dbl_buyback = (ins_items_data['dbl_buyback'] or 0) / int(ins_items_data['int_quantity'])
                        dbl_discount = (ins_items_data['dbl_discount'] or 0)/ int(ins_items_data['int_quantity'])
                        dbl_rate = (ins_items_data['dbl_amount'] / int(ins_items_data['int_quantity']))

                        dbl_tax=0
                        dbl_item_kfc = 0
                        dct_item['dblBuyBack'] = round(dbl_buyback,2)
                        dct_item['dblDiscount'] = round(dbl_discount,2)
                        if dct_data['blnIGST']:
                            dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))/100)
                            dct_item['dblIGSTPer'] = round(float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0)),2)
                            dct_item['dblIGST'] = round(dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0)/100),2)
                        
                        if ins_items['fk_item_category__json_tax_master'] and bln_kfc:
                            dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['KFC'],0))/100)
                            dct_data['dbl_kfc_amount'] += dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['KFC'],0)/100)
                            dbl_item_kfc = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['KFC'],0)/100)
                            dct_item['dblSGSTPer'] = dct_item['dblCGSTPer'] = round(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST']),2)
                            dct_item['dblSGST'] = dct_item['dblCGST'] = round(dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)/100),2)

                        elif ins_items['fk_item_category__json_tax_master'] and not bln_kfc:
                            dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))/100)
                            dct_item['dblSGSTPer'] = dct_item['dblCGSTPer'] = round(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST']),2)
                            dct_item['dblSGST'] = dct_item['dblCGST'] = round(dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)/100),2)
                        else:
                            dct_item['dblSGSTPer'] = dct_item['dblCGSTPer'] =0
                            dct_item['dblSGST'] = dct_item['dblCGST'] = 0

                        if dct_item['intStatus'] in [2,3,4]:
                            dct_item['dblIGSTPer'] = 0.0
                            dct_item['dblCGSTPer'] = 0.0
                            dct_item['dblSGSTPer'] = 0.0
                            dct_item['dblIGST'] = 0.0
                            dct_item['dblCGST'] = 0.0
                            dct_item['dblSGST'] = 0.0
                        # dct_item['dblRate'] = round(dbl_rate,2)
                        dct_item['dblRate'] = 0
                        if dct_data['blnIGST']:
                            # dct_item['dblRate'] = round(dbl_rate-dct_item['dblIGST'],2)
                            dbl_tax += dct_item['dblIGST']
                        else:
                            dbl_tax += dct_item['dblCGST']
                            dbl_tax += dct_item['dblSGST']

                        if dct_data['blnIGST']:
                            dct_item['GST'] = dct_item['dblIGSTPer']
                        else :
                            dct_item['GST'] = dct_item['dblSGSTPer'] +  dct_item['dblCGSTPer']

                        # dct_item['dblMarginAmount'] = 0
                        dct_item['dblMopAmount'] = dbl_rate
                            # dct_item['dblRate'] = round(dbl_rate-dct_item['dblCGST']-dct_item['dblSGST'],2)
                        # dct_item['dblAmount'] = round(dct_item['dblRate'] - dct_item['dblBuyBack'] - dct_item['dblDiscount']+dbl_tax,2)
                        # dct_item['dblAmount'] = 0
                        dct_item['dblAmount'] = round(dbl_rate-dbl_buyback-dbl_discount,2)
                        # dct_item['status'] = False
                        dct_data['lstItems'].append(dct_item)

                    # dct_item['dblSGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))
                    # dct_item['dblSGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)/100)
#                     if dct_item['intStatus'] in [2,3,4]:
# ===========================================================some problems with below code =======================================================
                    # dct_item['itemEnqId'] = ins_items_data.get('item_enquiry_id') # conflicted code
                    #
                    # if ins_partial_inv['int_status'] == 3:
                    #
                    #     dbl_total_spare = 0
                    #     dct_data['lst_spare'] = []
                    #     dct_data['dbl_total_spare'] = 0
                    #     dct_data['dbl_advc_paid'] = ins_partial_inv['json_data']['lst_items'][0]['dbl_advc_paid']
                    #
                    #     if ins_items_data.get('lst_spare'):
                    #         lst_spare = []
                    #         for ins_spare in ins_items_data.get('lst_spare'):
                    #             dct_spare = {}
                    #             dct_spare['str_item_name'] = ins_spare['fk_item_id__vchr_item_name']
                    #             dct_spare['dbl_amount'] = ins_spare['dbl_amount'] or 0
                    #             dbl_total_spare = dbl_total_spare +  dct_spare['dbl_amount']
                    #             lst_spare.append(dct_spare)
                    #         dct_data['lst_spare'] = lst_spare
                    #         dct_data['dbl_total_spare'] = dbl_total_spare
                    #
                    #
                    #     dbl_rate = ins_items_data['dbl_amount']
                    #     dbl_discount = ins_items_data['dbl_discount']
                    #     dct_item['dblBuyBack'] = 0
                    #     dct_item['dblRate'] = 0
                    #     dct_item['dblDiscount'] = round(dbl_discount,2)
                    #     # conflicted
                    #
                    #     dct_item['dblIGSTPer'] = 0.0
                    #     dct_item['dblCGSTPer'] = 0.0
                    #     dct_item['dblSGSTPer'] = 0.0
                    #     dct_item['dblIGST'] = 0.0
                    #     dct_item['dblCGST'] = 0.0
                    #     dct_item['dblSGST'] = 0.0
                    #
                    #     dct_item['strImei'] = '---'
                    #     if ins_items_data.get('vchr_imei'):
                    #         dct_item['strImei'] = ins_items_data['vchr_imei']
                    #
                    #     dct_item['dblAmount'] = round(dbl_rate-dbl_discount-dbl_total_spare,2)
                    #
                    #     dct_data['lstItems'].append(dct_item)
                    #
                    # else:
                    #     dct_item['itemEnqId'] = ins_items_data['item_enquiry_id']
                    #
                    #     if ins_items_data['int_status'] == 2:
                    #         dct_item['dctImages'] = ins_items_data['dct_images']
                    #
                    #     if len(ins_items_data['json_imei']['imei'])>0:
                    #         dct_item['strImei'] = ins_items_data['json_imei']['imei'][row]
                    #         ins_grn_details = GrnDetails.objects.filter(fk_item_id=ins_items['pk_bint_id'],jsn_imei_avail__contains={'imei_avail':[dct_item['strImei']]}).values('jsn_tax').last()
                    #     # else:
                    #     #     ins_grn_details = GrnDetails.objects.filter(fk_item_id=ins_items['pk_bint_id'],vchr_batch_no=dct_item['strBatchNo']).values('jsn_tax').last()
                    #     dbl_buyback = ins_items_data['dbl_buyback'] / int(ins_items_data['int_quantity'])
                    #     dbl_discount = ins_items_data['dbl_discount'] / int(ins_items_data['int_quantity'])
                    #     dbl_rate = (ins_items_data['dbl_amount'] / int(ins_items_data['int_quantity']))
                    #     dbl_tax=0
                    #     dct_item['dblBuyBack'] = round(dbl_buyback,2)
                    #     dct_item['dblDiscount'] = round(dbl_discount,2)
                    #     if dct_data['blnIGST']:
                    #         dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))/100)
                    #         dct_item['dblIGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))
                    #         dct_item['dblIGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0)/100)
                    #     if ins_items['fk_item_category__json_tax_master'] and bln_kfc:
                    #     dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))/100)
                    #     dct_item['dblCGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0))
                    #     dct_item['dblCGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)/100)
                    #     dct_item['dblSGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))
                    #     dct_item['dblSGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)/100)

            """admin tools"""
            tools_keys(dct_data,request)
            return Response({'status':1,'data':dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

# ===========================================================================================================================================================================
    def patch(self,request):
        """
            To invoice the return items .
            param : sales_details pk_bint_id .
            return : dct of sales return details .
        """
        try:

            if request.data.get('lst_return'):
                dct_tax_master = {}
                dct_data = {}
                dct_item = {}
                dct_data['lstItems'] = []
                

                return_master_check = list(SalesDetails.objects.filter(pk_bint_id__in = request.data.get("int_id")).values_list('fk_master_id',flat = True))
                rst_data = SalesDetails.objects.filter(Q(json_imei__has_any_keys = request.data.get('imei',[]),),int_sales_status = 1,fk_item_id__vchr_item_code__in = ['GDC00001','GDC00002']).values('json_imei','pk_bint_id','fk_master_id')
                if rst_data:
                    for data in rst_data:
                        dct_return_data = {}
                        # if data['fk_master_id'] in return_master_check:
                        ins_is_returned = SalesReturn.objects.filter(fk_sales_details_id=data['pk_bint_id']).values()
                        if not ins_is_returned:
                            dct_return_data['imei'] = data['json_imei'][0]
                            dct_return_data['id'] = data['pk_bint_id']
                            request.data.get('lst_return').append(dct_return_data)
                int_master_id=0
                for data in request.data.get('lst_return'):
                    int_id = data.get('id')
                    str_imei = data.get('imei')
                    
                    dct_sales = SalesDetails.objects.filter(pk_bint_id = int_id).values('pk_bint_id','fk_master_id','fk_master_id__fk_customer_id','fk_master_id__fk_staff_id','fk_item_id','fk_item_id__vchr_item_code','dbl_selling_price','json_imei','json_tax','dbl_tax','dbl_amount','dbl_discount','dbl_buyback','int_qty','dbl_indirect_discount','fk_master_id__jsn_addition','fk_master_id__jsn_deduction').first()
                    int_master_id = dct_sales['fk_master_id']
                    if not dct_sales:
                        return Response({'status':'0','message':'No Data'})

                    # dct_data = {}
                    ins_customer = SalesCustomerDetails.objects.filter(pk_bint_id = dct_sales['fk_master_id__fk_customer_id']).values('pk_bint_id','fk_customer_id','vchr_name','vchr_email','int_mobile','txt_address','vchr_gst_no','fk_location__vchr_name','fk_location__vchr_pin_code','fk_location_id','fk_state_id','fk_state__vchr_name','int_loyalty_points','int_redeem_point','fk_customer_id__int_cust_type').first()
                    dct_data['intSalesCustId'] =  ins_customer['pk_bint_id']
                    dct_data['intStaffId'] = dct_sales['fk_master_id__fk_staff_id']
                    dct_data['strStaffName'] = Userdetails.objects.filter(user_ptr_id = dct_sales['fk_master_id__fk_staff_id']).annotate(str_name=Concat('first_name', Value(' '), 'last_name')).values('str_name').first()['str_name']
                    dct_data['intContactNo'] = ins_customer['int_mobile']
                    dct_data['intCustId'] = ins_customer['fk_customer_id']
                    dct_data['strCustName'] = ins_customer['vchr_name']
                    dct_data['strCustEmail'] = ins_customer['vchr_email']
                    dct_data['txtAddress'] = ins_customer['txt_address']
                    dct_data['strGSTNo'] = ins_customer['vchr_gst_no']
                    dct_data['intLocation'] = ins_customer['fk_location_id']
                    dct_data['strLocation'] = ins_customer['fk_location__vchr_name']
                    dct_data['intPinCode'] = ins_customer['fk_location__vchr_pin_code']
                    dct_data['intState'] = ins_customer['fk_state_id']
                    dct_data['strState'] = ins_customer['fk_state__vchr_name']


                    dct_data['blnIGST'] = False

                    if request.user.userdetails.fk_branch.fk_states_id != ins_customer['fk_state_id']:
                        dct_data['blnIGST'] = True

                    dct_tax_master = {}

                    for ins_tax in TaxMaster.objects.values('pk_bint_id','vchr_name'):
                        dct_tax_master[ins_tax['vchr_name']] = str(ins_tax['pk_bint_id'])
                    ins_items = Item.objects.filter(vchr_item_code = dct_sales['fk_item_id__vchr_item_code'],int_status=0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master').first()
                    if not ins_items:
                        return Response({'status':'0','message':'Item Not Found'})

                    dct_item = {}
                    rst_gdot = SalesDetails.objects.filter(json_imei__contains = str_imei if str_imei else '',int_sales_status = 1,fk_item_id__vchr_name__in =['GDP','GDEW (EXTENDED WARRANTY)'])\
                                                   .values('pk_bint_id','fk_item_id__vchr_name','dbl_amount','dbl_selling_price','int_qty')
                    dct_item['GDP'] = 0
                    dct_item['GDEW'] = 0
                    if rst_gdot:
                        for ins_gdot in rst_gdot:
                            if ins_gdot['fk_item_id__vchr_name'] == 'GDP':
                                dct_item['GDP'] = ins_gdot['dbl_selling_price']/ins_gdot['int_qty'] or 0
                            elif ins_gdot['fk_item_id__vchr_name'] == 'GDEW (EXTENDED WARRANTY)':
                                dct_item['GDEW'] = ins_gdot['dbl_selling_price']/ins_gdot['int_qty'] or 0
                    
                    dct_item['strItemCode'] = ins_items['vchr_item_code']
                    dct_item['intItemId'] = ins_items['pk_bint_id']
                    dct_item['strItemName'] = ins_items['vchr_name']

                    dct_item['intQuantity'] = 1
                    dct_item['intStatus'] = 0

                    dct_item['strImei'] = str_imei if str_imei else ''
                    dct_item['id'] = data['id']
                    dct_item['dblAmount'] = dct_sales['dbl_selling_price']/dct_sales['int_qty']
                    dct_item['dblBuyBack'] = dct_sales['dbl_buyback']/dct_sales['int_qty']
                    dct_item['dblDiscount'] = dct_sales['dbl_discount']/dct_sales['int_qty']
                    dct_item['dblIndirectDis'] = dct_sales['dbl_indirect_discount'] if dct_sales['dbl_indirect_discount'] else 0

                    # dct_item['dblRate'] = dct_item['dblAmount'] - (dct_item['dblBuyBack'] + dct_item['dblDiscount'] + (dct_sales['dbl_tax']/dct_sales['int_qty']))
                    # LG
                    
                    dct_item['dblRate'] = dct_item['dblAmount'] - (dct_sales['dbl_tax']/dct_sales['int_qty'])

                    dct_item['dblIGST'] = dct_sales['json_tax']['dblIGST']/dct_sales['int_qty']
                    dct_item['dblCGST'] = dct_sales['json_tax']['dblCGST']/dct_sales['int_qty']
                    dct_item['dblSGST'] = dct_sales['json_tax']['dblSGST']/dct_sales['int_qty']
                    dct_item['dblKFC'] = dct_sales['json_tax'].get('dblKFC',0.0)/dct_sales['int_qty']

                    dct_item['dblIGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))
                    dct_item['dblCGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0))
                    dct_item['dblSGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))
                    dct_item['dblKFCPer'] = 1.0 if dct_item['dblKFC'] else 0


                    dct_data['lstItems'].append(dct_item)
            dbl_addition=0
            dbl_deduction=0
            if request.data.get('blnReturnAll'):
                dct_master = SalesMaster.objects.filter(pk_bint_id = int_master_id).values('jsn_addition','jsn_deduction').first()
                int_master_id = dct_sales['fk_master_id']
                if dct_master['jsn_addition']:
                    for item in dct_master['jsn_addition'].values():
                        dbl_addition += float(item)
                if dct_master['jsn_deduction']:
                    for item in dct_master['jsn_deduction'].values():
                        dbl_deduction += float(item)
            
            return Response({'status':1,'data':dct_data,'dbl_addition':dbl_addition,'dbl_deduction':dbl_deduction})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

class AddInvoice(APIView):
    permission_classes = [AllowAny]

    def patch(self,request):
        try:
            with transaction.atomic():
                
                if request.data.get('approveId'):
                    if request.data.get('intCreditSale'):
                        """int_credit_sale - 1 - Credit Sale ticked and when total Amount > 200,000 2- Credit Sale approved when amount >200000
                                                3 - Credit Sale Disapproved when amount >200000"""


                        ins_partial=PartialInvoice.objects.filter(pk_bint_id = request.data.get('approveId'),int_active = 0).first()
                        json_updated_data=ins_partial.json_updated_data
                        json_updated_data['int_credit_sale']= request.data.get('intCreditSale')
                        if request.data.get('intCreditSale')==3:
                            json_updated_data['dbl_partial_amt']=0
                            json_updated_data['dbl_balance_amt']=0
                            PartialInvoice.objects.filter(pk_bint_id = request.data.get('approveId'),int_active = 0).update(int_approve=0,json_updated_data=json_updated_data,dat_created=datetime.now())
                        else:
                            PartialInvoice.objects.filter(pk_bint_id = request.data.get('approveId'),int_active = 0).update(int_approve=4,json_updated_data=json_updated_data,dat_created=datetime.now())

                    else:
                        PartialInvoice.objects.filter(pk_bint_id = request.data.get('approveId'),int_active = 0).update(int_approve=2,dat_created=datetime.now())
                    # ins_partial=PartialInvoice.objects.filter(pk_bint_id = int_partial_id,int_active = 0)
                    # ins_partial.int_approve=1
                    # ins_partial.save()
                    return Response({'status':1,'bln_approve':True})

                int_partial_id = request.data.get('partial_id')
                if int_partial_id:

                    ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = int_partial_id,int_active = 0).values('dat_created','json_data','int_status','int_approve').first()
                    lst_items = json.loads(request.data.get('lstItems'))
                    # for i in range(len(lst_items)):
                    #     if lst_items[i]['itemEnqId']:
                    #         del lst_items[i]
                    #         break
                    if ins_partial_inv['json_data']:
                        json_partial_data=copy.deepcopy(ins_partial_inv['json_data'])
                        json_partial_data['dbl_total_amt']=request.data.get('dblTotalAmount')

                        '''1 - when invoice amount is greater than 200000 and  credit sale is requested'''
                        if request.data.get('blnCreditSale'):
                            json_partial_data['dbl_partial_amt']=request.data.get('dblPartialAmount',0)
                            json_partial_data['dbl_balance_amt']=request.data.get('dblBalanceAmount',0)
                            json_partial_data['int_credit_sale']= 1

                        json_partial_data['lst_items']=[]
                        dct_item={}
                        int_index=1

                        for ins_item in lst_items:

                            if ins_item.get('itemEnqId') and ins_item['strItemCode']+"-"+str(ins_item['itemEnqId']) in  dct_item:
                                
                                # dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['int_quantity']=dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['int_quantity']+1
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['json_imei']['imei'].append(ins_item.get('strImei'))
                                # dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_amount'] += ins_item['dblAmount']

                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_amount'] += (ins_item.get('dblAmount') or 0)+(ins_item.get('dblDiscount') or 0)+(ins_item.get('dblBuyBack') or 0)

                            elif ins_item.get('itemEnqId'):
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]={}
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['int_quantity'] = ins_item['intQuantity']
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['json_imei'] = {'imei': [ins_item.get('strImei')]}
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['vchr_item_code'] = ins_item['strItemCode']
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['vchr_item_name'] = ins_item['strItemName']
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['int_status'] = ins_item['intStatus']
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['vchr_remarks'] = request.data.get('strRemarks')
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['item_enquiry_id'] = ins_item['itemEnqId']
                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_buyback'] = ins_item['dblBuyBack']
                                #dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_amount'] = ins_item['dblAmount']

                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_amount'] = (ins_item.get('dblAmount') or 0)+(ins_item.get('dblDiscount') or 0)+(ins_item.get('dblBuyBack') or 0)


                                dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_discount'] = ins_item['dblDiscount']
                            else:
                                str_key = ins_item['strItemCode'] +"-"+str(int_index)
                                int_index +=1
                                dct_item[str_key]={}
                                dct_item[str_key]['int_quantity'] = ins_item['intQuantity']
                                dct_item[str_key]['json_imei'] = {'imei': [ins_item.get('strImei')]}
                                dct_item[str_key]['vchr_item_code'] = ins_item['strItemCode']
                                dct_item[str_key]['vchr_item_name'] = ins_item['strItemName']
                                dct_item[str_key]['int_status'] = ins_item['intStatus']
                                dct_item[str_key]['vchr_remarks'] = request.data.get('strRemarks')
                                dct_item[str_key]['item_enquiry_id'] = None
                                dct_item[str_key]['dbl_buyback'] = ins_item['dblBuyBack']
                                #dct_item[str_key]['dbl_amount'] = ins_item['dblAmount']

                                dct_item[str_key]['dbl_amount'] = (ins_item.get('dblAmount') or 0)+(ins_item.get('dblDiscount') or 0)+(ins_item.get('dblBuyBack') or 0)


                                dct_item[str_key]['dbl_discount'] = ins_item['dblDiscount']

                        json_partial_data['lst_items'] = list(dct_item.values())
                            # dct_data['int_quantity'] = ins_item['intQuantity']
                            # dct_data['json_imei'] = {'imei': [ins_item['strImei']]}
                            # dct_data['vchr_item_code'] = ins_item['strItemCode']
                            # dct_data['vchr_item_name'] = ins_item['strItemName']
                            # dct_data['int_status'] = ins_item['intStatus']
                            # dct_data['vchr_remarks'] = request.data.get('strRemarks')
                            # dct_data['item_enquiry_id'] = ins_item['itemEnqId'] or None
                            # dct_data['dbl_buyback'] = ins_item['dblBuyBack']
                            # dct_data['dbl_amount'] = ins_item['dblAmount']
                            # dct_data['dbl_discount'] = ins_item['dblDiscount']
                            # json_partial_data['lst_items'].append(dct_data)
                    PartialInvoice.objects.filter(pk_bint_id = int_partial_id,int_active = 0).update(int_approve=1,json_updated_data=json_partial_data,dat_created=datetime.now())
                    return Response({'status':1,'int_approve':1})

                else:
                    dat_to = (datetime.strptime(request.data.get("datTo")[:10],'%Y-%m-%d')).date()
                    dat_from = (datetime.strptime(request.data.get("datFrom")[:10],'%Y-%m-%d')).date()
                    # if request.data.get('blnService'):
                    #     if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    #         ins_partial_inv = PartialInvoice.objects.filter(int_status__in=(3,5,6,10),int_active=0,int_approve=1,dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-pk_bint_id')
                    #     else:
                    #         ins_partial_inv = PartialInvoice.objects.filter(int_status__in=(3,5,6,10),int_active=0,int_approve=1,dat_created__date__gte = dat_from,dat_created__date__lte = dat_to,json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id}).values('pk_bint_id','dat_created','json_data','int_status').order_by('-pk_bint_id')
                    #     # ------------------If int_active = 0 ---------------------------
                    #     # if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    #     #     ins_partial_inv = PartialInvoice.objects.filter(int_status__in=(3,6),int_active = 0,dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
                    #     # else:
                    #     #     ins_partial_inv = PartialInvoice.objects.filter(int_status__in=(3,6),int_active = 0,dat_created__date__gte = dat_from,dat_created__date__lte = dat_to,json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id}).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
                    #     # ------------------If int_active = 0 ---------------------------
                    # elif request.data.get('blnBajaj') :
                    #     if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    #         ins_partial_inv = PartialInvoice.objects.filter(int_status=11,int_active = 0,int_approve=1,dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
                    #     else:
                    #         ins_partial_inv = PartialInvoice.objects.filter(int_status=11,int_active = 0,int_approve=1,json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id},dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
                    # else:
                    
                    if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN']:
                        ins_partial_inv = PartialInvoice.objects.filter(int_active = 0,int_approve=1,dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).exclude(int_status__in=(3,6,5,10,11)).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
                    else:
                        return Response({'status':1,'data':[]})
                    # else:
                    #     ins_partial_inv = PartialInvoice.objects.filter(int_active = 0,int_approve=1,json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id},dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).exclude(int_status__in=(3,6,5,10,11)).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')

                    #--------------------
                    lst_branch_id = []
                    ins_tool = Tools.objects.filter(vchr_tool_code='ALLOW_SERVICER_PRINT').values('jsn_data').first()
                    if  ins_tool:
                        if ins_tool['jsn_data']:
                            lst_branch_id = ins_tool['jsn_data']
                    #--------------------
                    lst_data = []
                    dct_branch = dict(Branch.objects.values_list('pk_bint_id','vchr_name'))
                    for ins_data in ins_partial_inv:
                        dct_data = {}
                        dct_data['intId'] = ins_data['pk_bint_id']
                        dct_data['datBooked'] = ins_data['dat_created'].strftime("%d-%m-%Y")
                        dct_data['strCustomer'] = ins_data['json_data']['str_cust_name'].title()
                        dct_data['strStaff'] = ins_data['json_data'].get('str_staff_name').title()
                        dct_data['strEnqNo'] = ins_data['json_data'].get('vchr_enquiry_num')
                        dct_data['branch'] = dct_branch.get(ins_data['json_data'].get('int_branch_id'))
                        if request.user.userdetails.fk_group.vchr_name.upper() in ['SERVICE MANAGER','SERVICE ENGINEER','BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                            if ins_data['json_data'].get('int_branch_id') in lst_branch_id and ins_data['json_data']['lst_items'][0].get('vchr_job_status') not in ['GDP NORMAL NEW','GDEW NEW','CHECKED']:
                                dct_data['bln_view'] = True
                            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER']:
                                dct_data['bln_view'] = True
                            else:
                                dct_data['bln_view'] = False
                        else:
                                dct_data['bln_view'] = False


                        dct_data['sales_status'] = ins_data['int_status']
                        dct_data['strItem'] = ''
                        dct_data['strItem'] = ' , '.join([ i['vchr_item_name']for i in ins_data['json_data']['lst_items']])
                        if request.data.get('blnService'):
                            # dct_data['datBooked'] = datetime.strftime(datetime.strptime(ins_data['json_data']['dat_created_at'],'%Y-%m-%d'),"%d-%m-%Y") if ins_data['json_data'].get('dat_created_at') else ''
                            dct_data['int_service_id']= ins_data['json_data']['lst_items'][0]['int_service_id'] if ins_data['json_data']['lst_items'][0].get('int_service_id') else ''
                            dct_data['vchr_status']= ins_data['json_data']['lst_items'][0]['vchr_job_status'] if ins_data['json_data']['lst_items'][0].get('vchr_job_status') else ''
                            dct_data['vchr_job_num']=ins_data['json_data'].get('vchr_job_num') or "---"

                            if dct_data['vchr_status'] == 'SERVICED & DELIVERED':
                                dct_data['sales_status'] = 7 # if servie is SERVICED & DELIVERED

                        if len(dct_data['strItem'])>30:
                            dct_data['strItem'] = dct_data['strItem'][:30]+'...'
                        # for ins_data in  ins_data['json_data']['lst_items']:
                        #     dct_data['strItem'] += ins_data['vchr_item_name']
                        #     if len(dct_data['strItem'])>30:
                        #         dct_data['strItem'] = dct_data['strItem'][:30]+'...'
                        #         break
                        lst_data.append(dct_data)
                    return Response({'status':1,'data':lst_data})
        except Exception as e:
            

            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            if request.data.get('salesRowId'):
                    if PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId'),fk_invoice_id__isnull=False).exists():
                        return Response({'status':0,'message':'Already sold'})
            inst_partial_validation=None
            if request.data.get('salesRowId'):
              inst_partial_validation = PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId'))
            if inst_partial_validation:
               inst_partial_validation.update(fk_invoice_id=1)
            with transaction.atomic():

                dct_item_data = json.loads(request.data.get('dctTableData'))
                lst_returned_id  = json.loads(request.data.get('dctReturnId'))
                int_redeem_point = json.loads(request.data.get('intRedeemPoint'))
                dbl_rounding_off = json.loads(request.data.get('intRounding','0.0'))
                str_remarks = request.data.get('strRemarks',None)
                bln_igst = False
                """admin tools"""
                json_addition = request.data.get('json_additions')
                json_deduction = request.data.get('json_deductions')
                dct_addition={}
                dct_deduction={}




                 # LG
                """~~~~~~~~~~~~~~~~~~~~Checking Item is available or not~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
                lst_for_comparison = []
                lst_imei_data_exists = []
                lst_batch_data_exists = []
                #commented for o2force
                # for data in dct_item_data:
                #     """~~~~~~~~~~~~~~~~~~~~To avoid smart choice and return from imei available check~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
                #     if not data['intStatus'] in [0,2,3] and (data.get('vchr_product_name') not in ['RECHARGE','SIM','SERVICE','SERVICES']):
                #         if data.get('strImei'):
                #             if data["imeiStatus"]:
                #                 lst_imei_data_exists.append(data['strImei'][0] if type(data['strImei']) == list else data['strImei'] )
                #             else:
                #                 lst_batch_data_exists.append(data['strImei'][0] if type(data['strImei']) == list else data['strImei'] )
                #     """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

                # if lst_imei_data_exists or lst_batch_data_exists:
                #     rst_imei_exist_data = BranchStockDetails.objects.filter(jsn_imei_avail__imei__has_any_keys = lst_imei_data_exists, fk_master_id__fk_branch_id=request.user.userdetails.fk_branch_id).values('jsn_imei_avail','int_qty')
                #     rst_imei_exchange_data = ExchangeStock.objects.filter(jsn_avail__has_any_keys = lst_imei_data_exists, fk_branch_id=request.user.userdetails.fk_branch_id).annotate(jsn_imei_avail=F('jsn_avail'),int_qty=F('int_avail')).values('jsn_imei_avail','int_qty')

                #     # rst_exist_data = BranchStockDetails.objects.filter(Q(jsn_imei_avail__imei__has_any_keys = lst_data_exists) | Q(jsn_batch_no__batch__has_any_keys = lst_data_exists ), fk_master_id__fk_branch_id=request.user.userdetails.fk_branch_id).values('jsn_imei_avail','jsn_batch_no','int_qty')
                #     rst_batch_no_exist_data = BranchStockDetails.objects.filter(jsn_batch_no__batch__has_any_keys = lst_batch_data_exists , fk_master_id__fk_branch_id=request.user.userdetails.fk_branch_id).values('jsn_batch_no').annotate(sum_qty = Sum('int_qty'))
                #     for data in rst_imei_exist_data:
                #         for imei in data['jsn_imei_avail']['imei']:
                #             if imei in lst_imei_data_exists:
                #                 lst_for_comparison.append(imei)


                #     for data in rst_imei_exchange_data:
                #         if data['jsn_imei_avail'][0] in lst_imei_data_exists:
                #             lst_for_comparison.append(data['jsn_imei_avail'][0])

                #     for data in rst_batch_no_exist_data:
                #         for batch in data['jsn_batch_no']['batch']:
                #             if batch in lst_batch_data_exists:
                #                 if  lst_batch_data_exists.count(batch) <= data['sum_qty']:
                #                     lst_for_comparison.append(batch)
                #                 else:
                #                     if inst_partial_validation:
                #                         inst_partial_validation.update(fk_invoice_id=None)

                #                     return Response({'status':0,'message':'The Item Batch No '+str(batch)+' is Not Available for this quantity'})

                #     imei_notfound = set(lst_imei_data_exists+lst_batch_data_exists).difference(set(lst_for_comparison))
                #     
                #     if imei_notfound:
                #         if inst_partial_validation:
                #             inst_partial_validation.update(fk_invoice_id=None)

                #         return Response({'status':0,'message':'The Item IMEI/Batch No ('+','.join(imei_notfound)+') is Not Available Now'})
                # """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
#end comment for o2force
                if json_addition:
                    json_addition = json.loads(request.data.get('json_additions'))

                    for ins_addition in json_addition:
                        rst_addition = AccountsMap.objects.filter(vchr_module_name='ADDITION',vchr_category=ins_addition['name'],int_status=0).values('pk_bint_id')
                        if rst_addition:
                            dct_addition[rst_addition[0]['pk_bint_id']] = ins_addition['value']
                if json_deduction:
                    json_deduction = json.loads(request.data.get('json_deductions'))

                    for ins_deduction in json_deduction:
                        rst_deduction = AccountsMap.objects.filter(vchr_module_name='DEDUCTIONS',vchr_category=ins_deduction['name'],int_status=0).values('pk_bint_id')
                        if rst_deduction:
                            dct_deduction[rst_deduction[0]['pk_bint_id']] = ins_deduction['value']
                # if (1/settings.LOYALTY_POINT)*int_redeem_point:
                #     rst_deduction = AccountsMap.objects.filter(vchr_module_name='DEDUCTIONS',vchr_category='CUSTOMER LOYALTY',int_status=0).values('pk_bint_id')
                #     if rst_deduction:
                #         dct_deduction[rst_deduction[0]['pk_bint_id']] = (1/settings.LOYALTY_POINT)*int_redeem_point
                if request.data.get('offerAmt'):
                    int_offer=int(request.data.get('offerAmt')[0])
                else:
                    int_offer=0
                if request.data.get('blnExchange'):
                    ins_partial_inv={}
                    ins_partial_inv['json_data']={}
                    ins_partial_inv['json_data']['int_cust_id']=request.data.get('intCustId')
                    ins_partial_inv['json_data']['intSalesCustId']=request.data.get('intSalesCustId')
                    ins_partial_inv['json_data']['int_staff_id']=request.user.id
                    ins_partial_inv['json_data']['int_branch_id']=request.user.userdetails.fk_branch_id

                    # jsn_avail=[data for data in ins_exchange.jsn_avail if data!=dct_item.get('strImei','')]
                    # ins_exchange.jsn_avail=jsn_avail
                    # ins_exchange.int_avail=ins_exchange.int_avail-1
                    # if ins_exchange.int_avail == 0:
                    #     ins_exchange.int_status=1
                    # ins_exchange.save()
                    # LG
                    """Updating ExchangeStock"""
                    dct_item = json.loads(request.data.get('dctTableData'))
                    for data in dct_item:
                        ins_exchange=ExchangeStock.objects.filter(pk_bint_id =data.get('intsalesid'),jsn_avail__icontains = data.get('strImei')).update(int_status = 1,int_avail = 0,jsn_avail=[])


                else:
                    ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId')).values().first()
                ins_branch_code = Branch.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_branch_id']).values('vchr_code').first()['vchr_code']
                # # ins_document = Document.objects.filter(vchr_module_name = "INVOICE",vchr_short_code = ins_branch_code).first()
                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = "INVOICE",fk_branch_id = request.user.userdetails.fk_branch_id).first()
                # if not ins_document:
                #     ins_document = Document.objects.create(vchr_module_name = "INVOICE",vchr_short_code = ins_branch_code,int_number = 1)
                #     str_inv_num = 'INV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     ins_document.int_number = ins_document.int_number+1
                #     ins_document.save()
                # else:
                #     str_inv_num = 'INV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     Document.objects.filter(vchr_module_name = "INVOICE",vchr_short_code = ins_branch_code).update(int_number = ins_document.int_number+1)

                # LG 27-06-2020
                moduel_name = "INVOICE"
                if request.data.get('blnExchange'):
                    moduel_name = "EXCHANGE SALE"

                ins_document = Document.objects.select_for_update().filter(vchr_module_name = moduel_name,fk_branch_id = request.user.userdetails.fk_branch_id).first()
                if ins_document:
                    str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                    Document.objects.filter(vchr_module_name = moduel_name,fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                else:
                    ins_document_search = Document.objects.filter(vchr_module_name = moduel_name,fk_branch_id = None).first()
                    if ins_document_search:
                        ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                        ins_document = Document.objects.create(vchr_module_name = moduel_name, int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                        str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                        ins_document.int_number = ins_document.int_number+1
                        ins_document.save()
                    else:
                        if inst_partial_validation:
                            inst_partial_validation.update(fk_invoice_id=None)
                        return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})


                ins_branch = Branch.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_branch_id']).first()
                ins_staff = Userdetails.objects.filter(user_ptr_id = ins_partial_inv['json_data']['int_staff_id']).first()
                ins_customer = CustomerDetails.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_cust_id']).first()
                ins_sales_customer = SalesCustomerDetails.objects.filter(pk_bint_id = request.data.get('intSalesCustId')).first()


                '''For sez customer'''
                int_cust_type=ins_customer.int_cust_type


                if request.user.userdetails.fk_branch.fk_states_id != ins_sales_customer.fk_state_id or int_cust_type==3:
                # if request.user.userdetails.fk_branch.fk_states_id != ins_customer.fk_state_id:
                    bln_igst = True
                odct_item_data = OrderedDict()
                dbl_total_amt = 0
                dbl_total_tax = 0
                json_total_tax = {'dblIGST':0,'dblCGST':0,'dblSGST':0}
                bln_kfc = False
                if not bln_igst and not ins_sales_customer.vchr_gst_no:
                    json_total_tax['dblKFC'] = 0
                    bln_kfc = True
                dbl_total_rate = 0
                dbl_total_buyback = 0
                dbl_total_discount = 0
                vchr_journal_num = None
                jsn_avail=[]
                lst_already_exchanged=[]
                ins_sales_master = None

                lst_item_id = [x['intItemId'] for x in dct_item_data]
                dct_item_sup_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_supp_amnt'))
                dct_item_mop_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_mop'))
                dct_item_mrp_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_mrp'))
                dct_item_cost_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_cost_amnt'))
                dct_item_myg_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','int_myg_amt'))
                dct_item_dealer_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_dealer_amt'))

                
                for dct_item in dct_item_data:

                    '''Converting null from front end values to 0'''
                    if 'dblIndirectDis' in dct_item:
                        dct_item['dblIndirectDis']=dct_item['dblIndirectDis'] or 0
                    if 'dblSGST' in dct_item:
                        dct_item['dblSGST'] = dct_item['dblSGST'] or 0
                    if 'dblIGST' in dct_item:
                        dct_item['dblIGST'] = dct_item['dblIGST'] or 0
                    if 'dblCGST' in dct_item:
                        dct_item['dblCGST'] = dct_item['dblCGST'] or 0
                    dct_item['dblBuyBack'] = dct_item['dblBuyBack'] or 0
                    dct_item['dblDiscount'] = dct_item['dblDiscount'] or 0
                    dct_item['dblRate'] = dct_item['dblRate'] or 0
                    dct_item['dblAmount'] = dct_item['dblAmount'] or 0

                    if 'dblIGSTPer' in dct_item:
                        dct_item['dblIGSTPer'] = dct_item['dblIGSTPer'] or 0
                    if 'dblCGSTPer' in dct_item:
                        dct_item['dblCGSTPer'] = dct_item['dblCGSTPer'] or 0
                    if 'dblSGSTPer' in dct_item:
                        dct_item['dblSGSTPer'] = dct_item['dblSGSTPer'] or 0
                    if not ins_sales_master:
                        # import pdb; pdb.set_trace()
                        # ins_sales_master = SalesMaster.objects.create_inv_num(str_inv_num)
                        ins_sales_master = SalesMaster.objects.create(
                                            fk_customer = ins_sales_customer,
                                            # fk_customer = ins_customer,
                                            fk_branch = ins_branch,
                                            vchr_invoice_num = str_inv_num,
                                            dat_invoice = date.today(),
                                            # vchr_journal_num = vchr_journal_num,
                                            vchr_remarks = str_remarks,
                                            dat_created = datetime.now(),
                                            int_doc_status = 1,
                                            # dbl_total_amt = dbl_total_amt,
                                            dbl_rounding_off = (dbl_rounding_off or 0),
                                            jsn_addition = json.dumps(dct_addition),
                                            jsn_deduction = json.dumps(dct_deduction),
                                            # dbl_total_tax = dbl_total_tax,
                                            # dbl_discount = dbl_total_discount + int_offer,
                                            # json_tax = json_total_tax,
                                            # dbl_buyback = dbl_total_buyback,
                                            fk_loyalty_id = request.data.get('intLoyaltyId',None),
                                            dbl_loyalty = (1/settings.LOYALTY_POINT)*int_redeem_point,
                                            fk_staff = ins_staff,
                                            fk_created = request.user.userdetails,
                                            fk_coupon_id = request.data.get('intCouponId',None),
                                            dbl_coupon_amt = request.data.get('intCouponDisc',None),
                                            fk_financial_year = FinancialYear.objects.filter(dat_start__lte = date.today(),dat_end__gte = date.today(),bln_status = True).first(),
                                            int_sale_type = request.data.get('int_enquiry_type',None),
                                            int_order_no = request.data.get('vchr_order_num',None),
                                            vchr_reff_no = request.data.get('vchr_reference_num',None),
                                            dbl_cust_outstanding = request.data.get('dblBalanceAmount',0)
                                            )

                        ins_sales_master.save()
                    
                    if dct_item.get('dblIndirectDis') and not vchr_journal_num:
                        # ins_branch_code = Branch.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_branch_id']).values('vchr_code').first()['vchr_code']
                        # ins_document = Document.objects.select_for_update().filter(vchr_module_name = "INDIRECT DISCOUNT",vchr_short_code = ins_branch_code).first()
                        # if not ins_document:
                        #     ins_document = Document.objects.create(vchr_module_name = "INDIRECT DISCOUNT",vchr_short_code = ins_branch_code,int_number = 1)
                        #     vchr_journal_num = 'JV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                        #     ins_document.int_number = ins_document.int_number+1
                        #     ins_document.save()
                        # else:
                        #     vchr_journal_num = 'JV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                        #     Document.objects.filter(vchr_module_name = "INDIRECT DISCOUNT",vchr_short_code = ins_branch_code).update(int_number = ins_document.int_number+1)

                        # LG 27-06-2020
                        ins_document = Document.objects.select_for_update().filter(vchr_module_name = "INDIRECT DISCOUNT",fk_branch_id = request.user.userdetails.fk_branch_id).first()
                        if ins_document:
                            vchr_journal_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                            Document.objects.filter(vchr_module_name = "INDIRECT DISCOUNT",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                        else:
                            ins_document_search = Document.objects.filter(vchr_module_name = 'INDIRECT DISCOUNT',fk_branch_id = None).first()
                            if ins_document_search:
                                ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                                ins_document = Document.objects.create(vchr_module_name = 'INDIRECT DISCOUNT', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                                vchr_journal_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                                ins_document.int_number = ins_document.int_number+1
                                ins_document.save()
                            else:
                                if inst_partial_validation:
                                    inst_partial_validation.update(fk_invoice_id=None)

                                return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                    item_total_tax = 0
                    item_total_tax_percent = 0
                    json_item_tax = {'dblIGST':0,'dblCGST':0,'dblSGST':0}
                    if dct_item['intStatus'] == 0:
                        dct_item['dblIGST'] = round((-1)*dct_item['dblIGST'],2)
                        dct_item['dblCGST'] = round((-1)*dct_item['dblCGST'],2)
                        dct_item['dblSGST'] = round((-1)*dct_item['dblSGST'],2)
                        # LG
                        json_item_tax['dblIGST%'] = round((-1)*dct_item['dblIGSTPer'],2) if dct_item['dblIGSTPer'] else 0
                        json_item_tax['dblCGST%'] = round((-1)*dct_item['dblCGSTPer'],2) if dct_item['dblCGSTPer'] else 0
                        json_item_tax['dblSGST%'] = round((-1)*dct_item['dblSGSTPer'],2) if dct_item['dblSGSTPer'] else 0

                        dct_item['intKfc'] = round((-1)*dct_item['intKfc'],2) if dct_item.get('intKfc') else 0
                        dct_item['dblDiscount'] = (-1)*dct_item['dblDiscount']
                        dct_item['dblBuyBack'] = (-1)*dct_item['dblBuyBack']
                        dct_item['dblAmount'] = (-1)*dct_item['dblAmount']
                        dct_item['dblRate'] = round((-1)*dct_item['dblRate'],2)
                    # if dct_item['intStatus'] in [0,2]:
                    #     dct_item['dblAmount'] = (-1)*dct_item['dblAmount']
                    #     dct_item['dblRate'] = (-1)*dct_item['dblRate']

                    if bln_igst:
                        json_item_tax['dblIGST'] += dct_item['dblIGST']
                        dbl_total_tax += round(dct_item['dblIGST'],2)
                        json_total_tax['dblIGST'] += dct_item['dblIGST']
                        item_total_tax += round(dct_item['dblIGST'],2)
                        json_item_tax['dblIGST%'] = dct_item['dblIGSTPer'] if dct_item['dblIGSTPer'] else 0

                        item_total_tax_percent = json_item_tax['dblIGST%']
                    else:
                        if bln_kfc:
                            json_item_tax['dblKFC'] = round(dct_item['intKfc'],2) if dct_item.get('intKfc') else 0
                            json_item_tax['dblKFC%'] = dct_item['dblKFCPer'] if dct_item.get('dblKFCPer') else 1

                            if 'dblKFC' not in json_total_tax:
                                json_total_tax['dblKFC'] = round(dct_item['intKfc'],2) if dct_item.get('intKfc') else 0
                            else:
                                json_total_tax['dblKFC'] += round(dct_item['intKfc'],2) if dct_item.get('intKfc') else 0
                            item_total_tax += round(dct_item.get('intKfc',0),2)
                            dbl_total_tax += round(dct_item.get('intKfc',0),2)

                        json_item_tax['dblCGST'] += round(dct_item['dblCGST'],2)
                        json_item_tax['dblSGST'] += round(dct_item['dblSGST'],2)
                        dbl_total_tax += round(dct_item['dblCGST'],2) + round(dct_item['dblSGST'],2)
                        json_total_tax['dblCGST'] += round(dct_item['dblCGST'],2)
                        json_total_tax['dblSGST'] += round(dct_item['dblSGST'],2)
                        item_total_tax += round(dct_item['dblCGST'],2)+round(dct_item['dblSGST'],2)

                        # LG
                        json_item_tax['dblCGST%'] = dct_item['dblCGSTPer'] if dct_item['dblCGSTPer'] else 0
                        json_item_tax['dblSGST%'] = dct_item['dblSGSTPer'] if dct_item['dblSGSTPer'] else 0

                    if item_total_tax_percent == 0:
                        item_total_tax_percent = json_item_tax.get('dblCGST%',0) +json_item_tax.get('dblSGST%',0) + json_item_tax.get('dblKFC%',0)

                    

                    ins_sales_details=SalesDetails.objects.create(fk_master = ins_sales_master,
                                        fk_item_id = dct_item['intItemId'],
                                        int_qty = 1,
                                        dbl_amount = round(dct_item['dblRate'],2),
                                        dbl_selling_price = dct_item['dblAmount'] if int_cust_type!=3 else  round(dct_item['dblRate'],2),
                                        dbl_tax = item_total_tax,
                                        dbl_discount = (dct_item['dblDiscount'] or 0) + int_offer,
                                        dbl_buyback = (dct_item['dblBuyBack'] or 0),
                                        json_tax = json_item_tax,
                                        # vchr_batch=odct_item_data[ins_data][''],
                                        json_imei = [dct_item.get('strImei')],
                                        int_sales_status=dct_item['intStatus'],
                                        dbl_indirect_discount=(dct_item.get('dblIndirectDis') or 0),
                                        int_doc_status = 1,
                                        dbl_supplier_amount = 0,
                                        # dbl_supplier_amount = dct_item_sup_amnt.get(dct_item['intItemId'],0.0),
                                        dbl_dealer_price = dct_item_dealer_amnt.get(dct_item['intItemId']) or 0.0,
                                        dbl_cost_price = dct_item_cost_amnt.get(dct_item['intItemId']) or 0.0,
                                        dbl_mrp = dct_item_mrp_amnt.get(dct_item['intItemId']) or 0.0,
                                        dbl_mop = dct_item_mop_amnt.get(dct_item['intItemId']) or 0.0,
                                        dbl_tax_percentage = item_total_tax_percent)
                    ins_sales_details.save()
                    dbl_total_amt += dct_item['dblAmount']
                    dbl_total_rate += round(dct_item['dblRate'],2)
                    dbl_total_buyback += (dct_item['dblBuyBack'] or 0)
                    dbl_total_discount += (dct_item['dblDiscount'] or 0)


                    if dct_item['intStatus'] == 1:
                        vchr_stk_imei = dct_item.get('strImei')
                        ins_br_stock = BranchStockDetails.objects.filter(Q(jsn_imei_avail__contains={'imei':[str(vchr_stk_imei)]}),fk_item_id=dct_item['intItemId'],fk_item__imei_status=True,fk_master__fk_branch_id=request.user.userdetails.fk_branch_id).first()
                        ins_br_stk_imei = BranchStockImeiDetails.objects.filter(Q(jsn_imei__contains={'imei':[str(vchr_stk_imei)]}),fk_details=ins_br_stock).first()
                        if ins_br_stock:
                            lst_imei = ins_br_stock.jsn_imei_avail['imei']
                            lst_imei.remove(vchr_stk_imei)
                            int_qty = ins_br_stock.int_qty-1
                            BranchStockDetails.objects.filter(pk_bint_id=ins_br_stock.pk_bint_id).update(jsn_imei_avail={'imei':lst_imei},int_qty=int_qty)
                        if ins_br_stk_imei:
                            lst_imei = ins_br_stk_imei.jsn_imei['imei']
                            lst_imei.remove(vchr_stk_imei)
                            int_qty = ins_br_stk_imei.int_qty-1
                            BranchStockImeiDetails.objects.filter(Q(jsn_imei__contains={'imei':[str(vchr_stk_imei)]}),fk_details=ins_br_stock).update(jsn_imei={'imei':lst_imei},int_qty=int_qty)
                        if not ins_br_stock and not ins_br_stk_imei:
                            ins_batch_stock = BranchStockDetails.objects.filter(Q(jsn_batch_no__contains={'batch':[str(vchr_stk_imei)]}),fk_item_id=dct_item['intItemId'],fk_item__imei_status=False,fk_master__fk_branch_id=request.user.userdetails.fk_branch_id,int_qty__gt=0).first()
                            ins_batch_stk = BranchStockImeiDetails.objects.filter(Q(jsn_batch_no__contains={'batch':[str(vchr_stk_imei)]}),fk_details=ins_batch_stock,int_qty__gt=0).first()
                            if ins_batch_stock:
                                int_qty = ins_batch_stock.int_qty-1
                                BranchStockDetails.objects.filter(pk_bint_id=ins_batch_stock.pk_bint_id).update(int_qty=int_qty)
                            if ins_batch_stk:
                                int_qty = ins_batch_stk.int_qty-1
                                BranchStockImeiDetails.objects.filter(pk_bint_id=ins_batch_stk.pk_bint_id,fk_details=ins_batch_stock).update(int_qty=int_qty)
                        # elif data.get('vchr_product_name') in ['RECHARGE','SIM']:
                        #     ins_br_stock = BranchStockDetails.objects.filter(int_qty__gte = 1,fk_master__fk_branch_id = request.user.userdetails.fk_branch_id,fk_item_id=dct_item['intItemId']).order_by('fk_master__dat_stock').first()
                        #     ins_br_stk_imei = BranchStockImeiDetails.objects.filter(fk_details=ins_br_stock).first()
                        #     if ins_br_stock:
                        #         int_qty = ins_br_stock.int_qty-1
                        #         BranchStockDetails.objects.filter(pk_bint_id=ins_br_stock.pk_bint_id).update(int_qty=int_qty)
                        #     if ins_br_stk_imei:
                        #         int_qty = ins_br_stock.int_qty-1
                        #         BranchStockImeiDetails.objects.filter(fk_details=ins_br_stock).update(int_qty=int_qty)

                    if dct_item['intStatus'] == 2:
                        ins_branch_stock_details = ExchangeStock(dat_exchanged=date.today(),fk_item_id=dct_item['intItemId'],int_avail=dct_item['intQuantity'],jsn_imei=[dct_item['strImei']],jsn_avail=[dct_item['strImei']],fk_branch=ins_branch,fk_sales_details_id=ins_sales_details.pk_bint_id,dbl_unit_price=dct_item['dblAmount'])
                        ins_branch_stock_details.save()


                        # if '-r' in dct_item.get('strImei',''): #-r is the imei for an exchanged item
                        #      lst_already_exchanged.append(dct_item.get('strImei'))
                             # ins_exchange=ExchangeStock.objects.filter(jsn_avail__icontains=dct_item.get('strImei','')).first()
                             # if ins_exchange:
                             #     for data in ins_exchange.jsn_avail:
                             #         if dct_item.get('strImei','') !=data and data not in lst_already_exchanged:
                             #             jsn_avail.append(data)
                             #
                             #     ins_exchange.jsn_avail=jsn_avail
                             #     ins_exchange.int_avail = ins_exchange.int_avail -1
                             #     if ins_exchange.int_avail == 0:
                             #            ins_exchange.int_status=1
                             #
                             #     ins_exchange.save()
                    

                    if dct_item['intStatus'] == 0:
                        ins_sales_returned = SalesDetails.objects.filter(fk_item__pk_bint_id = dct_item['intItemId'],fk_master__fk_customer = ins_sales_customer).values('fk_master__pk_bint_id')

                        if request.FILES.get(str(dct_item['intItemId'])):
                            img_item = request.FILES.get(str(dct_item['intItemId']))
                            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                            str_img = fs.save(img_item.name, img_item)
                            str_img_path = fs.url(str_img)

                        else:
                            str_img_path = ""

                        ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'SALES RETURN',fk_branch_id=request.user.userdetails.fk_branch_id).first()
                        # if ins_document:
                        #     pass
                        # else:
                        #     ins_document=Document(vchr_short_code='SRN',
                        #                             fk_branch_id=request.user.userdetails.fk_branch_id,
                        #                             vchr_module_name='SALES RETURN',
                        #                             int_number=0
                        #                             )
                        # str_code = ins_document.vchr_short_code
                        # int_doc_num = ins_document.int_number + 1
                        # ins_document.int_number = int_doc_num
                        # str_number = str(int_doc_num).zfill(4)
                        # str_document = str_code + '-'+ins_branch.vchr_code+'-'+ str_number
                        # ins_document.save()

                        # LG 27-06-2020
                        if ins_document:
                            vchr_journal_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                            Document.objects.filter(vchr_module_name = "SALES RETURN",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                        else:
                            ins_document_search = Document.objects.filter(vchr_module_name = 'SALES RETURN',fk_branch_id = None).first()
                            if ins_document_search:
                                ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                                ins_document = Document.objects.create(vchr_module_name = 'SALES RETURN', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                                vchr_journal_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                                ins_document.int_number = ins_document.int_number+1
                                ins_document.save()
                            else:
                                if inst_partial_validation:
                                    inst_partial_validation.update(fk_invoice_id=None)

                                return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                        # ins_sales_return = SalesReturn.objects.create_sales_return(str_inv_num)

                        ins_sales_return = SalesReturn.objects.create(
                        fk_returned_id = ins_sales_master.pk_bint_id,
                        fk_sales = ins_sales_master,
                        fk_item_id = dct_item['intItemId'],
                        int_qty = 1,
                        dbl_amount = round(dct_item['dblRate'],2),
                        dbl_selling_price = dct_item['dblAmount'],
                        jsn_imei = [dct_item.get('strImei','')],
                        dat_returned = date.today(),
                        fk_staff = ins_staff,
                        dat_created = datetime.now(),
                        fk_created = request.user.userdetails,
                        int_doc_status = 0,
                        vchr_image = str_img_path,
                        vchr_remark = lst_returned_id.get(str(dct_item['intItemId'])).get('strRemarks'),
                        bln_damaged = lst_returned_id.get(str(dct_item['intItemId'])).get('blnDamage'),
                        vchr_doc_code=str_document

                        )

                        vchr_stk_imei = dct_item.get('strImei')
                        ins_br_stock = BranchStockDetails.objects.filter(Q(jsn_imei__contains={'imei':[str(vchr_stk_imei)]}),fk_item_id=dct_item['intItemId']).first()
                        ins_br_stk_imei = BranchStockImeiDetails.objects.filter(jsn_imei_reached__contains={'imei':[str(vchr_stk_imei)]},fk_details=ins_br_stock).first()
                        if ins_br_stock:
                            lst_imei = ins_br_stock.jsn_imei_avail['imei']
                            lst_imei.append(vchr_stk_imei)
                            int_qty = ins_br_stock.int_qty+1
                            BranchStockDetails.objects.filter(pk_bint_id=ins_br_stock.pk_bint_id).update(jsn_imei_avail={'imei':lst_imei},int_qty=int_qty)
                        if ins_br_stk_imei:
                            lst_imei = ins_br_stk_imei.jsn_imei['imei']
                            lst_imei.append(vchr_stk_imei)
                            int_qty = ins_br_stock.int_qty+1
                            BranchStockImeiDetails.objects.filter(jsn_imei_reached__contains={'imei':[str(vchr_stk_imei)]},fk_details=ins_br_stock).update(jsn_imei={'imei':lst_imei},int_qty=int_qty)

                    if dct_item.get('itemEnqId'):
                        str_temp = '0-'+str(dct_item['itemEnqId'])+'-'+str(ins_sales_details.pk_bint_id)
                    else:
                        str_temp = '1-'+str(dct_item['strItemCode'])+'-'+str(ins_sales_details.pk_bint_id)


                    if str_temp and str_temp not in odct_item_data:
                        odct_item_data[str_temp] = {}
                        odct_item_data[str_temp]['jsonTax'] = dct_item['dblSGST']
                        odct_item_data[str_temp]['dblTax'] = item_total_tax

                        odct_item_data[str_temp]['strItemCode'] = dct_item['strItemCode']
                        odct_item_data[str_temp]['intItemId'] = dct_item['intItemId']
                        odct_item_data[str_temp]['dblIndirectDis'] = dct_item.get('dblIndirectDis')
                        odct_item_data[str_temp]['dblBuyBack'] = dct_item['dblBuyBack']
                        odct_item_data[str_temp]['dblDiscount'] = dct_item['dblDiscount']
                        odct_item_data[str_temp]['dblRate'] = dct_item['dblRate']
                        odct_item_data[str_temp]['dblAmount'] = dct_item['dblAmount'] if int_cust_type!=3 else  round(dct_item['dblRate'],2)
                        odct_item_data[str_temp]['intQuantity'] = 1
                        odct_item_data[str_temp]['status'] = dct_item['intStatus']

                        odct_item_data[str_temp]["dbl_supp_amnt"] = dct_item_sup_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_mop_amnt"] = dct_item_mop_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_mrp_amnt"] = dct_item_mrp_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_cost_amnt"] = dct_item_cost_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_myg_amnt"] = dct_item_myg_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_dealer_amnt"] = dct_item_dealer_amnt.get(dct_item['intItemId']) or 0.0

                        odct_item_data[str_temp]["dbl_tax"] = item_total_tax
                        odct_item_data[str_temp]["json_tax"] = json_item_tax
                        if dct_item.get('strImei',''):
                            odct_item_data[str_temp]['jsonImei']=[dct_item.get('strImei','')]
                        if dct_item['strItemCode'] == 'GDC00001':
                            odct_item_data[str_temp]['int_type'] = 1
                        elif dct_item['strItemCode'] == 'GDC00002':
                            odct_item_data[str_temp]['int_type'] = 2
                        else:
                            odct_item_data[str_temp]['int_type'] = 0

                ins_sales_master.vchr_journal_num = vchr_journal_num
                ins_sales_master.dbl_total_amt = dbl_total_amt
                ins_sales_master.dbl_total_tax = dbl_total_tax
                ins_sales_master.dbl_discount = dbl_total_discount + int_offer
                ins_sales_master.json_tax = json_total_tax
                ins_sales_master.dbl_buyback = dbl_total_buyback
                ins_sales_master.save()
                dbl_finance_extra_payment = 0
                if request.data.get('dctFinDetails'):
                    dct_fin_extra_payment = eval(request.data.get('dctFinDetails'))
                    dbl_finance_extra_payment =  sum(filter (None,dct_fin_extra_payment.values()))
                    dbl_total_amt+=dbl_finance_extra_payment

                #----------------------------------------------------------
                #creditcustomers dbl_credit_balance substract from total_amount
                # -------------------------------------------------------------
                rst_sales_customer = SalesCustomerDetails.objects.filter(pk_bint_id = request.data.get('intSalesCustId'),fk_customer__int_cust_type__in=[1,2]).values('fk_customer_id','fk_customer__dbl_credit_balance').first()
                rst_payment_customer = SalesCustomerDetails.objects.filter(pk_bint_id = request.data.get('intSalesCustId')).values('int_cust_type').first()
                if rst_sales_customer:
                    dbl_credit_balance =  rst_sales_customer['fk_customer__dbl_credit_balance']
                    int_total_amt = dbl_credit_balance-int(request.data.get('intGrandTot'))
                    ins_customer.dbl_credit_balance = int_total_amt
                    ins_customer.save()
                
                dct_delivery_data =  json.loads(request.data.get('dctDeliveryData'))
                if dct_delivery_data.get('strCustName') and dct_delivery_data.get('intCustContactNo'):
                    CustServiceDelivery.objects.create(fk_sales_master = ins_sales_master,
                                                    fk_customer = ins_customer,
                                                    vchr_cust_name = dct_delivery_data.get('strCustName',None),
                                                    int_mobile = dct_delivery_data.get('intCustContactNo',None),
                                                    txt_address = dct_delivery_data.get('strCustAddress',None),
                                                    vchr_landmark = dct_delivery_data.get('strCustPlace',None),
                                                    vchr_gst_no = dct_delivery_data.get('strCustGST',None),
                                                    fk_location_id = dct_delivery_data.get('intCustCityId',None),
                                                    fk_state_id = dct_delivery_data.get('intCustStateId',None))
                dct_payment_data = json.loads(request.data.get('lstPaymentData'))
                # LG
                
                bln_payment_check=False
                lst_bi_payment_details = []

                for ins_mode in dct_payment_data:
                    #LG
                    dct_bi_payment_details = {}
                    if request.data.get('dblPartialAmount'):
                        dct_bi_payment_details['int_fop'] = -1
                        dct_bi_payment_details['dbl_amt'] = request.data.get('dblPartialAmount')
                        lst_bi_payment_details.append(dct_bi_payment_details)
                    if ins_mode == '0' and dct_payment_data[ins_mode].get('intFinanceAmt') != None and dct_payment_data[ins_mode].get('intFinanceAmt') != 0:
                        dct_bi_payment_details['int_fop'] = int(ins_mode)
                        dct_bi_payment_details['dbl_amt'] = dct_payment_data[ins_mode].get('intFinanceAmt',None)
                        lst_bi_payment_details.append(dct_bi_payment_details)
                    else:
                        if dct_payment_data[ins_mode].get('dblAmt') != None and dct_payment_data[ins_mode].get('dblAmt') != 0:
                            dct_bi_payment_details['int_fop'] = int(ins_mode)
                            dct_bi_payment_details['dbl_amt'] = dct_payment_data[ins_mode].get('dblAmt',None)
                            lst_bi_payment_details.append(dct_bi_payment_details)

                    """"""""""""
                    card_key = ""
                    if "debitCard" in  dct_payment_data[ins_mode] :
                        card_key = "debitCard"
                    elif "creditCard" in dct_payment_data[ins_mode]:
                        card_key = "creditCard"
                    elif "BharathQR" in dct_payment_data[ins_mode]:
                        card_key = "BharathQR"
                    if card_key:
                        for ins_payment_data in dct_payment_data[ins_mode][card_key]:
                            if ins_payment_data.get('dblAmt') or ins_payment_data.get('intFinanceAmt'):

                                ins_payment = PaymentDetails(fk_sales_master = ins_sales_master,
                                                            int_fop = int(ins_mode),
                                                            vchr_card_number = ins_payment_data.get('strCardNo',None),
                                                            vchr_name = ins_payment_data.get('strName',None),
                                                            vchr_finance_schema = ins_payment_data.get('strScheme',None),
                                                            vchr_reff_number = ins_payment_data.get('strRefNo',None),
                                                            dbl_receved_amt = ins_payment_data.get('dblAmt',None),
                                                            dbl_finance_amt = ins_payment_data.get('intFinanceAmt',None),
                                                            dbl_cc_charge = ins_payment_data.get('intCcCharge',None),
                                                            fk_bank_id = ins_payment_data.get('intBankId',None))
                                ins_payment.save()
                                bln_payment_check=True

                            if dct_payment_data[ins_mode].get('intFinanceAmt'):

                                FinanceDetails.objects.create(fk_payment_id = ins_payment.pk_bint_id,
                                                              dbl_finance_amt = ins_payment_data.get('intFinanceAmt',None),
                                                              dbl_receved_amt =  ins_payment_data.get('dblAmt',None),
                                                              dbl_processing_fee =  ins_payment_data.get('dblProcessingFee',None),
                                                              dbl_margin_fee = ins_payment_data.get('dblMarginFee',None),
                                                              dbl_service_amt = ins_payment_data.get('dblServiceAmount',None),
                                                              dbl_dbd_amt =ins_payment_data.get('dblDbdAmount',None) )
                    else:
                        if dct_payment_data[ins_mode].get('dblAmt') or dct_payment_data[ins_mode].get('intFinanceAmt'):
                            if ins_mode =='4':
                                vchr_ref_no=','.join([data['vchr_receipt_num'] for data in dct_payment_data['4']['lstReceipt'] if data.get('receipt')])
                            else:
                                vchr_ref_no=dct_payment_data[ins_mode].get('strRefNo',None)
                            if dct_payment_data[ins_mode].get('intFinanceId'):
                                ins_fin=Financiers.objects.filter(pk_bint_id=dct_payment_data[ins_mode].get('intFinanceId'))
                                str_name=ins_fin[0].vchr_code
                            else:
                                str_name=dct_payment_data[ins_mode].get('strName',None)

                            
                            ins_payment = PaymentDetails(fk_sales_master = ins_sales_master,
                                                        int_fop = int(ins_mode),
                                                        vchr_card_number = dct_payment_data[ins_mode].get('strCardNo',None),
                                                        vchr_name = str_name,
                                                        vchr_finance_schema = dct_payment_data[ins_mode].get('strScheme',None),
                                                        vchr_reff_number = vchr_ref_no,
                                                        dbl_receved_amt = dct_payment_data[ins_mode].get('dblAmt',None),
                                                        dbl_finance_amt = dct_payment_data[ins_mode].get('intFinanceAmt',None),
                                                        dbl_cc_charge = dct_payment_data[ins_mode].get('intCcCharge',None),
                                                        fk_bank_id = dct_payment_data[ins_mode].get('intBankId',None))
                            ins_payment.save()
                            bln_payment_check=True
                    #------------------------------------------------------------------------------------------------

                        if dct_payment_data[ins_mode].get('intFinanceAmt'):
                            FinanceDetails.objects.create(fk_payment_id = ins_payment.pk_bint_id,
                                                          dbl_finance_amt = dct_payment_data[ins_mode].get('intFinanceAmt',None),
                                                          dbl_receved_amt = dct_payment_data[ins_mode].get('dblAmt',None),
                                                          dbl_processing_fee = dct_payment_data[ins_mode].get('dblProcessingFee',None),
                                                          dbl_margin_fee = dct_payment_data[ins_mode].get('dblMarginFee',None),
                                                          dbl_service_amt = dct_payment_data[ins_mode].get('dblServiceAmount',None),
                                                          dbl_dbd_amt  = dct_payment_data[ins_mode].get('dblDbdAmount',None))

                
                if not bln_payment_check and rst_payment_customer['int_cust_type'] not in [1,2] and ins_sales_master.int_sale_type not in ['2','3'] and not ins_sales_master.dbl_cust_outstanding:
                    file_object = open('payment_issue.txt', 'a')
                    data_payment_to_write = json.dumps({'Date':request.data})
                    file_object.write(data_payment_to_write)
                    file_object.write('\n\n\n\n')
                    file_object.close()
                    raise ValueError("Some Issues With Payment")
                lstPaymentData=json.loads(request.data.get("lstPaymentData"))
                if '4' in lstPaymentData and lstPaymentData['4']['bln_receipt']:
                        bln_matching=json.loads(request.data['bln_matching'])

                        if bln_matching:

                                int_total=0.0
                                lstReceipt=[data for data in lstPaymentData['4']['lstReceipt'] if data.get('receipt')]
                                flag=False
                                int_total_pre=0
                                #lstReceipt : Receipt Amount balance and id  dblAmt send needed amount from all receipts
                                for r in lstReceipt:
                                        int_total=int_total+r['amount']
                                        if float(lstPaymentData['4']['dblAmt'])>int_total:
                                            if r.get('fk_receipt_id'):
                                                ReceiptInvoiceMatching.objects.create(fk_receipt_id=r['pk_bint_id'],dbl_amount=r['amount'],dat_created=datetime.now(),fk_sales_master_id=ins_sales_master.pk_bint_id)

                                            else:
                                                ReceiptInvoiceMatching.objects.create(dbl_amount=r['dbl_amount'],dat_created=datetime.now(),fk_receipt_id=r['pk_bint_id'],fk_sales_master_id=ins_sales_master.pk_bint_id)

                                        elif flag==False:
                                                    ReceiptInvoiceMatching.objects.create(dbl_amount=(float(lstPaymentData['4']['dblAmt'])-int_total_pre),dat_created=datetime.now(),fk_receipt_id=r['pk_bint_id'],fk_sales_master_id=ins_sales_master.pk_bint_id)
                                                    flag=True
                                        int_total_pre=int_total
                        if bln_matching== False:
                                int_total=0.0
                                lstReceipt=lstPaymentData['4']['lstReceipt']

                                flag=False
                                for r in lstReceipt:
                                        int_total=int_total+r['dbl_amount']
                                        if float(lstPaymentData['4']['dblAmt'])>int_total:
                                            ReceiptInvoiceMatching.objects.create(dbl_amount=r['dbl_amount'],dat_created=datetime.now(),fk_receipt_id=r['pk_bint_id'],fk_sales_master_id=ins_sales_master.pk_bint_id)
                                        elif flag==False:
                                            ReceiptInvoiceMatching.objects.create(dbl_amount=r['dbl_amount']-(int_total-float(lstPaymentData['4']['dblAmt'])),dat_created=datetime.now(),fk_receipt_id=r['pk_bint_id'],fk_sales_master_id=ins_sales_master.pk_bint_id)
                                            flag=True



                # -----------position changed code -------------------------
                if not request.data.get('blnExchange'):
                    loyalty_card(dbl_total_amt,ins_customer,ins_sales_master,request.user)
                # -------------------------------------------------
                # import pdb; pdb.set_trace()
                if create_invoice_posting_data(request,ins_sales_master.pk_bint_id):
                    if ins_sales_master.pk_bint_id:
                        ins_sap_api = SapApiTrack.objects.create(int_document_id = ins_sales_master.pk_bint_id,
                                            int_type = 1,
                                            int_status=0,
                                            dat_document = ins_sales_master.dat_created)
                        ins_sap_api.save()
                        if ins_sales_master.vchr_journal_num:
                            ins_sap_api = SapApiTrack.objects.create(int_document_id = ins_sales_master.pk_bint_id,
                                            int_type = 10,
                                            int_status=0,
                                            dat_document = ins_sales_master.dat_created)
                            ins_sap_api.save()
                    # return Response({'status':1,'sales_master_id':ins_sales_master.pk_bint_id,'bln_jio':False})
                else:
                    if inst_partial_validation:
                        inst_partial_validation.update(fk_invoice_id=None)

                    raise ValueError('Something happened in Transaction')
                # ------------------------- BI API ------------------------
                
                bln_allow = True
                if not request.data.get('blnExchange'):
                    PartialInvoice.objects.filter(pk_bint_id = int(request.data.get('salesRowId'))).update(dat_invoice = datetime.now(),fk_invoice = ins_sales_master,int_active = 1)

                #==============================================================================================================================================================================
                try:
                    # url =settings.BI_HOSTNAME + "/mobile/enquiry_invoice_update/"
                    # import pdb; pdb.set_trace()
                    if not request.data.get('blnExchange'): #exchanged item doesnt have partial invoice
                        ins_partial_inv = PartialInvoice.objects.get(pk_bint_id = int(request.data.get('salesRowId')))
                        int_enq_master_id = PartialInvoice.objects.filter(pk_bint_id = int(request.data.get('salesRowId'))).values().first()['json_data']['int_enq_master_id']
                    else:
                        bln_allow = False
                        int_enq_master_id=None #so that error doesnt occur in an exchanged item
                        url = settings.BI_HOSTNAME+ '/mobile/create_exchange_item/'
                        res_data = requests.post(url,json={'dct_item_data':odct_item_data,"int_enq_master_id":int_enq_master_id,"str_remarks":str_remarks,'cust_mobile':ins_sales_customer.int_mobile,'staff':request.user.username,'bi_payment_details':lst_bi_payment_details})
                        if res_data.json().get('status')=='success':
                            pass
                        else:
                            if inst_partial_validation:
                                inst_partial_validation.update(fk_invoice_id=None)

                            raise ValueError('Something happened in BI')
                            return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                    
                    for ins in odct_item_data:
                        if odct_item_data[ins]['status'] == 3:
                            bln_allow = True
                            # ------------------------------To Change  status in table PartialInvoice of field json_data -----------------------------------------------------
                            json_data_all = ins_partial_inv.json_data
                            json_data_all['lst_items'][0]['vchr_job_status'] = 'SERVICED & DELIVERED'
                            ins_partial_inv.json_data = json_data_all
                            ins_partial_inv.int_active=0
                            ins_partial_inv.save()

                            # -----------------------------------------------------------------------------------

                            url =settings.BI_HOSTNAME + "/service/service_invoice_update/"

                    if bln_allow:
                        
                        credit_sale = False
                        if ins_partial_inv.int_approve in [2, 4]:#test with partial invoice inst status field that credit aproved
                            credit_sale = True
                        # res_data = requests.post(url,json={'dct_item_data':odct_item_data,"int_enq_master_id":int_enq_master_id,"str_remarks":str_remarks,'bi_payment_details':lst_bi_payment_details,"credit_sale":credit_sale})
                        res_data = EnquiryInvoiceUpdate({'dct_item_data':odct_item_data,"int_enq_master_id":int_enq_master_id,"str_remarks":str_remarks,'bi_payment_details':lst_bi_payment_details,"credit_sale":credit_sale})
                        if res_data.get('status')=='success':
                            pass
                        else:
                            if inst_partial_validation:
                                inst_partial_validation.update(fk_invoice_id=None)

                            raise ValueError('Something happened in BI')
                            return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})

                except Exception as e:
                    if inst_partial_validation:
                       inst_partial_validation.update(fk_invoice_id=None)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                    raise ValueError('Something happened in BI')
                # ===============================================================================================================================================================================

                # ---------------- Loyalty Card -------------------

                # if bln_allow:
                #     loyalty_card(dbl_total_amt,ins_customer,ins_sales_master,request.user)
                # # -------------------------------------------------
                # if create_invoice_posting_data(request,ins_sales_master.pk_bint_id):
                #     if ins_sales_master.pk_bint_id:
                #         ins_sap_api = SapApiTrack.objects.create(int_document_id = ins_sales_master.pk_bint_id,
                #                             int_type = 1,
                #                             int_status=0,
                #                             dat_document = ins_sales_master.dat_created)
                #         ins_sap_api.save()
                #         if ins_sales_master.vchr_journal_num:
                #             ins_sap_api = SapApiTrack.objects.create(int_document_id = ins_sales_master.pk_bint_id,
                #                             int_type = 10,
                #                             int_status=0,
                #                             dat_document = ins_sales_master.dat_created)
                #             ins_sap_api.save()
                #     return Response({'status':1,'sales_master_id':ins_sales_master.pk_bint_id,'bln_jio':False})
                # else:
                #     raise ValueError('Something happened in Transaction')
                #     return Response({'status':'0','message':'Transaction Failed'})



                return Response({'status':1,'sales_master_id':ins_sales_master.pk_bint_id,'bln_jio':False})
        except Exception as e:
            if inst_partial_validation:
               inst_partial_validation.update(fk_invoice_id=None)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})




    def put(self,request):
        try:
            int_partial_id = request.data.get('intPartialId')
            str_remark = request.data.get('strRemark')
            # int_partial_id = 11
            with transaction.atomic():
                if request.data.get('blnService'):
                    int_partail = PartialInvoice.objects.filter(pk_bint_id=int_partial_id).first()
                    # url = "http://192.168.0.174:2121/invoice/update_enquiry/"
                    url =settings.BI_HOSTNAME + "/invoice/update_service/"
                    res_data = requests.post(url,json={'enquiry_id':int_partail.json_data['int_enq_master_id'],'str_remark':str_remark,'user_code':request.user.username})
                    if res_data.json().get('status')=='Success':
                        dct_jsn_data = int_partail.json_data
                        dct_jsn_data['str_remarks'] = str_remark
                        int_partail.json_data = dct_jsn_data
                        int_partail.int_active=-1
                        int_partail.save()
                        return Response({'status':1,'message':'Successfully Rejected'})
                    else:
                        return Response({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                else:
                    int_partail = PartialInvoice.objects.filter(pk_bint_id=int_partial_id).first()
                    # url = "http://192.168.0.174:2121/invoice/update_enquiry/"
                    url =settings.BI_HOSTNAME + "/invoice/update_enquiry/"
                    res_data = requests.post(url,json={'enquiry_id':int_partail.json_data['int_enq_master_id'],'str_remark':str_remark,'user_code':request.user.username})
                    if res_data.json().get('status')=='Success':
                        dct_jsn_data = int_partail.json_data
                        dct_jsn_data['str_remarks'] = str_remark
                        int_partail.json_data = dct_jsn_data
                        int_partail.int_active=-1
                        int_partail.save()
                        return Response({'status':1,'message':'Successfully Rejected'})
                    else:
                        return Response({'status': 'Failed','data':res_data.json().get('message',res_data.json())})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


class AddFollowUpAPI(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:

            if request.data.get('partial_id'):
                ins_part=PartialInvoice.objects.filter(pk_bint_id=request.data['partial_id']).values('json_data','int_enq_master_id','fk_invoice_id').first()
                lst_item_name=[]
                for item in ins_part['json_data']['lst_items']:
                    lst_item_name.append(item['vchr_item_code'])
                item_products={data['vchr_item_code']:(data['fk_product__vchr_name'],data['fk_brand__vchr_name'])  for data in list(Item.objects.filter(vchr_item_code__in=lst_item_name).values('vchr_item_code','fk_product__vchr_name','fk_brand__vchr_name'))}
                dct_enquiry_details={}
                dct_customer={}
                dct_customer['vchr_cust_name']= ins_part['json_data']['str_cust_name']
                dct_customer['vchr_cust_email']=ins_part['json_data']['vchr_cust_email']
                dct_customer['int_cust_mob']=ins_part['json_data']['int_cust_mob']
                dct_customer['staff_full_name']=ins_part['json_data']['str_staff_name']
                dct_customer['vchr_job_num']=ins_part['json_data']['vchr_job_num']
                dct_customer['vchr_bname']=ins_part['json_data']['str_branch']
                dct_customer['vchr_source_name']=ins_part['json_data']['vchr_source_name']
                dct_customer['dat_created_at']=ins_part['json_data']['dat_created']
                dct_customer['partial_id'] = request.data.get('partial_id')
                dct_customer['int_enq_master_id']=ins_part['int_enq_master_id']
                dct_customer['lst_worked_on']=ins_part['json_data']['lst_items'][0].get('json_worked_on')
                dct_customer['lst_worked_on']=ins_part['json_data']['lst_items'][0].get('json_worked_on')


                ins_partial_receipt = PartialReceipt.objects.filter(json_data__contains = request.data.get('partial_id'),int_status=1).values()
                dbl_advc_new =0

                if ins_partial_receipt:
                    for dct_recp_data in ins_partial_receipt:
                        if dct_recp_data['json_data'].get('intPartialInvoiceId') and request.data.get('partial_id'):
                            if dct_recp_data['json_data'].get('intPartialInvoiceId') == int(request.data.get('partial_id')):
                                dbl_advc_new = dct_recp_data['json_data'].get('dblAdvAmount')

                # if 'str_servicer_name' in ins_part['json_data']:
                #     dct_customer['str_servicer_name']=ins_part['json_data']['str_servicer_name']
                '''Adding customer address'''
                dct_customer['txt_address'] = CustomerDetails.objects.filter(pk_bint_id=ins_part['json_data']['int_cust_id']).values('txt_address').first().get('txt_address')


                if ins_part['json_data']['lst_items'][0]['vchr_job_status']=='SERVICED' and ins_part['json_data']['vchr_type'] in ['GDP-Normal','GDEW-Normal']:
                    dct_customer['bln_mail_button'] = True
                dbl_service = 0.0
                dbl_total_spare = 0.0
                lst_spare=[]
                dbl_est = 0
                dbl_advance = 0
                dbl_discount = 0
                for item in ins_part['json_data']['lst_items'][:-1]:
                    dct_data={}
                    if item['vchr_item_code'] =='SRV00002':

                        dbl_est=item['dbl_amount']
                        dbl_advance = item.get('dbl_advc_paid') or 0
                        dbl_discount = item.get('dbl_discount') or 0
                        dbl_total=dbl_est- dbl_advance - dbl_discount

                    else:
                        dct_data={}
                        dct_data['vchr_item_name']=item['vchr_item_name']
                        dct_data['vchr_item_code'] = item['vchr_item_code']
                        dct_data['vchr_imei'] = item['vchr_imei']
                        dct_data['amount'] = item['dbl_amount']
                        dbl_total_spare+=item['dbl_amount']
                        lst_spare.append(dct_data)
                item =ins_part['json_data']['lst_items'][-1]
                dct_data={}

                dct_data['staff_name_assigned']=''
                if ins_part['json_data'].get("staff_name_assigned"):
                        dct_data['staff_name_assigned'] = ins_part['json_data'].get("staff_name_assigned")

                if item_products[item['vchr_item_code']][0] not in dct_enquiry_details:
                    dct_enquiry_details[item_products[item['vchr_item_code']][0]]=[]
                dct_data['vchr_item_name']=item['vchr_item_name']
                dct_data['vchr_item_code'] = item['vchr_item_code']
                dct_data['vchr_imei'] = item['vchr_imei']
                
                dct_data['str_remarks'] = item.get('str_remarks') or ''
                dct_data['vchr_digital_signature']=settings.EQT_HOSTNAME+'/'+str(item['vchr_digital_signature']) if item.get('vchr_digital_signature') else None
                # checking screen lock picture and pin lock is in json file
                if 'vchr_screen_lock' in item:
                    dct_data['vchr_screen_lock']=str(item['vchr_screen_lock']) if item.get('vchr_screen_lock') else None
                if 'vchr_pin_lock' in item:
                    dct_data['vchr_pin_lock']=item['vchr_pin_lock']


                dct_data['vchr_service_image']=item['vchr_service_image'] if item.get('vchr_service_image') else None
                dct_data['vchr_brand']=item_products[item['vchr_item_code']][1]
                dct_data['vchr_job_status']=item['vchr_job_status']
                dct_data['int_service_id']=item['int_service_id']
                dct_data['vchr_type']=ins_part['json_data']['vchr_type']
                if item['vchr_job_status'] in ['GDP NORMAL NEW','GDP ADVANCED RECEIVED','GDEW NORMAL','GDEW ADVANCED RECEIVED'] or ins_part['json_data']['vchr_type'] in ['GDP-Normal','GDEW-Normal']:
                    dct_data['int_adv_amount']=round(item['int_adv_amount'])
                    dct_data['json_observation']={}
                    dct_data['json_problem_category']={'problem_category':[]}
                    dct_data['json_acc_received']={"acc_received":[]}
                    dct_data['vchr_gdp_type']=item.get('vchr_gdp_type')
                    dct_data['int_service_expense']=item.get('int_service_expense')
                if item['vchr_job_status'] in ['MISSING','MISSING & PENDING','MISSING & APPROVED','MISSING & PAID']:

                    dct_data['dat_purchase']=item['dat_purchase']
                    dct_data['theft_id']=None
                    dct_data['int_days_missing']=item['int_days_missing']
                    dct_data['int_depreciation_amt']=round(item['int_depreciation_amt'],2)
                    dct_data['purchase_branch']=item['purchase_branch']
                    dct_data['json_observation']={}
                    dct_data['json_problem_category']={'problem_category':[]}
                    dct_data['json_acc_received']={"acc_received":[]}
                if item['vchr_job_status'] in ['MISSING & APPROVED','MISSING & PENDING','MISSING & PAID']:
                        dct_data['json_documents']=[settings.HOSTNAME+str(data) for data in item['json_documents']]
                if item['vchr_job_status'] not in ['MISSING & PENDING','MISSING','MISSING & APPROVED','MISSING & PAID','GDP NORMAL NEW','GDP ADVANCED RECEIVED','GDEW NEW','GDEW ADVANCED RECEIVED']:
                 if not ins_part['json_data']['vchr_type']=='GDP-Normal' and not ins_part['json_data']['vchr_type']=='GDEW-Normal':
                    dct_data['dat_exp_delivery']=item['dat_exp_delivery'] if item.get('dat_exp_delivery') else None
                    dct_data['json_observation']=item['json_observation'] if item.get('json_observation') else None
                    dct_data['json_problem_category']=item['json_problem_category'] if item.get('json_problem_category') else None
                    dct_data['json_acc_received']=item['json_acc_received'] if item.get('json_acc_received') else 0
                    dbl_advc_paid_temp = float(item.get('dbl_advc_paid',0))
                    dct_data['dbl_advc_paid']=dbl_advc_paid_temp + dbl_advc_new
                    # dct_data["dbl_discount"]=item.get("dbl_discount") or 0
                    dct_data["dbl_discount"]=ins_part['json_data'].get("dbl_discount") or 0
                    dct_data["dbl_est_amt"] = item.get ('dbl_est_amt') or 0
                    dct_data["dbl_total_amount"]=dct_data["dbl_est_amt"]-(int(dct_data['dbl_advc_paid'])+dct_data["dbl_discount"])
                    if ins_part['json_data'].get('image'):
                        dct_data["image"]=ins_part['json_data'].get('image')
                if dct_data['vchr_job_status'] == 'SERVICED & DELIVERED':
                    dct_data["dbl_est_amt"] =  item.get('dbl_amount') or 0
                    dct_data["dbl_total_amount"] = dbl_total+dbl_total_spare
                    # if item.get('dbl_amount'):
                    # else:
                    #     dct_data["dbl_total_amount"]=0
                dct_enquiry_details[item_products[item['vchr_item_code']][0]].append(dct_data)
                #---------------payment Details-----------------------------------------------
                 # 0. Finance, 1. Cash, 2. Debit Card, 3. Credit Card 4. Receipt
                rst_payment = PaymentDetails.objects.filter(fk_sales_master_id = ins_part['fk_invoice_id'])\
                                                    .annotate(payment_type=Case(When(int_fop=0, then=Value('Finance')),When(int_fop=1, then=Value('Cash')), When(int_fop=2, then=Value('Debit Card')),When(int_fop=3, then=Value('Credit Card')),When(int_fop=4, then=Value('Receipt')),When(int_fop=5, then=Value('Paytm')),When(int_fop=6, then=Value('Paytm mall')),When(int_fop=7, then=Value('Bharath QR')),default=Value('Other'),output_field=CharField(),),)\
                                                    .values('dat_created_at','payment_type','dbl_receved_amt','vchr_reff_number','vchr_card_number','int_fop','vchr_finance_schema','dbl_finance_amt','vchr_name')
                dct_finance={}
                lst_finance=[]
                for data in rst_payment:
                    if data['int_fop']==0:
                        ins_fin=Financiers.objects.filter(vchr_code=data['vchr_name'])
                        dct_finance=data
                        dct_finance['company']=ins_fin[0].vchr_name
                        lst_finance.append(dct_finance)
                if lst_finance:
                    dct_finance=lst_finance[0]
                rst_payment=rst_payment.exclude(int_fop=0)
                #--------------------------------------------------------------
                return Response({'status':1,'dct_enquiry_details':dct_enquiry_details,'dct_customer':dct_customer,'dct_spare':lst_spare,'lst_payment':rst_payment})
            else:

                    int_status = 10 if request.data['lst_item'][0]['vchr_job_status']=='CHECKED SERVICE CENTER' else 6
                    ins_p=PartialInvoice(int_enq_master_id=request.data['int_enq_master_id'],dat_created=datetime.now(),int_status=int_status,int_active=0)
                    json_data=request.data
                    # =================================================================================
                    ins_staff = Userdetails.objects.filter(username = request.data.get('vchr_staff_code'),is_active = True).values('user_ptr_id','first_name','last_name').first()
                    ins_branch = Branch.objects.filter(vchr_code = request.data.get('vchr_branch_code')).values('pk_bint_id','vchr_name','fk_states_id').first()
                    ins_sales=None


                    if ins_staff:
                        json_data['int_staff_id'] = ins_staff['user_ptr_id']
                        json_data['str_staff_name'] = ins_staff['first_name']+' '+ins_staff['last_name']
                    else:
                        return Response({'error_status': 'NO','message':'No User in POS with user code '+request.data.get('vchr_staff_code')})

                    if ins_branch:
                        json_data['int_branch_id'] = ins_branch['pk_bint_id']
                        json_data['str_branch'] = ins_branch['vchr_name']
                    else:
                        return Response({'error_status':'NO','message':'No Branch in POS with Branch code '+request.data.get('vchr_branch_code')})

                    ins_state = None
                    str_cust_name = request.data.get('vchr_cust_name')
                    str_cust_email = request.data.get('vchr_cust_email',None)
                    int_cust_mob = request.data.get('int_cust_mob')
                    int_cust_type = request.data.get('int_customer_type',4)

                    if request.data.get('vchr_state_code'):
                        ins_state = States.objects.filter(vchr_code = request.data.get('vchr_state_code')).first()
                    ins_district = None
                    if 0 and request.data.get('vchr_district'):
                        ins_district = District.objects.filter(vchr_name = request.data.get('vchr_district')).first()
                        if not ins_district:
                            ins_district = District.objects.create(vchr_name = request.data.get('vchr_district'),fk_state=ins_state)
                        if not ins_state:
                            ins_state = ins_district.fk_state
                    ins_location = None
                    if request.data.get('vchr_location'):
                        ins_location = Location.objects.filter(vchr_name__contains=request.data.get('vchr_location',None),vchr_pin_code=request.data.get('vchr_pin_code',None)).first()
                        if not ins_location:
                            ins_location = Location.objects.create(vchr_name=request.data.get('vchr_location',None),vchr_pin_code=request.data.get('vchr_pin_code',None))
                        #if not ins_district:
                            #ins_district = ins_location.fk_district
                        if not ins_state:
                            ins_state = ins_location.fk_state
                    if not ins_state and ins_branch:
                        ins_state =  States.objects.filter(pk_bint_id=ins_branch['fk_states_id']).first()
                    ins_customer = CustomerDetails.objects.filter(int_mobile = int_cust_mob,int_cust_type = int_cust_type).values('pk_bint_id').first()
                    if not ins_customer:
                        ins_customer = CustomerDetails.objects.create(vchr_name = str_cust_name,vchr_email = str_cust_email,int_mobile = int_cust_mob,int_cust_type = int_cust_type,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)
                        json_data['int_cust_id'] = ins_customer.pk_bint_id
                    else:
                        json_data['int_cust_id'] = ins_customer['pk_bint_id']
                        ins_customer = CustomerDetails.objects.filter(vchr_name = str_cust_name,vchr_email = str_cust_email,int_mobile = int_cust_mob,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)
                        if not ins_customer:
                            CustomerDetails.objects.filter(pk_bint_id=json_data['int_cust_id']).update(vchr_email = str_cust_email,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)

                    # =================================================================================
                    json_data['lst_items']=request.data['lst_item']
#fk_item__vchr_item_code=json_data['lst_items'][0]['vchr_item_code'],
                    if json_data['lst_items'][0]['vchr_job_status']=='GDP NORMAL NEW':
                        if not json_data['lst_items'][0]['int_adv_amount']:
                            int_amount=SalesDetails.objects.filter(json_imei__contains=json_data['lst_items'][0]['vchr_imei']).values('fk_item_id__dbl_mop').exclude(fk_item__vchr_name__in=['gdp','gdew','GDP','GDEW']).first()['fk_item_id__dbl_mop']
                            json_data['lst_items'][0]['int_adv_amount']=int_amount*5/100 if int_amount*5/100>500 else 500

                    if json_data['lst_items'][0]['vchr_job_status']=='GDEW NEW':
                        if not json_data['lst_items'][0]['int_adv_amount']:
                            int_amount=SalesDetails.objects.filter(json_imei__contains=json_data['lst_items'][0]['vchr_imei']).values('fk_item_id__dbl_mop').exclude(fk_item__vchr_name__in=['gdp','gdew','GDP','GDEW']).first()['fk_item_id__dbl_mop']
                            json_data['lst_items'][0]['int_adv_amount']=int_amount*5/100 if int_amount*5/100>500 else 500

                    if json_data['lst_items'][0]['vchr_job_status']=='MISSING':

                        ins_sales=SalesDetails.objects.filter(fk_item__vchr_item_code=json_data['lst_items'][0]['vchr_item_code'],json_imei__contains=json_data['lst_items'][0]['vchr_imei']).values('int_qty','fk_master__dat_invoice','dbl_selling_price','fk_master__fk_branch__vchr_name').first()
                        int_days_missing=abs((ins_sales['fk_master__dat_invoice']-datetime.now().date()).days)
                        int_dep_percentage=Depreciation.objects.filter(int_days_upto__gte=int_days_missing).order_by("int_days_upto").values('int_dep_percentage').first()['int_dep_percentage']
                        int_amount=ins_sales['dbl_selling_price']/ins_sales['int_qty']
                        int_amount=int_amount-int_dep_percentage*int_amount/100
                        ins_theft=TheftDetails(dat_purchase=ins_sales['fk_master__dat_invoice'],\
                                                    int_days_missing=int_days_missing,\
                                                    int_depreciation_amt=int_amount,\
                                                    fk_created_id=request.user.id,\
                                                    dat_created=datetime.now()\
                                                    )
                        ins_theft.save()
                        json_data['lst_items'][0]['dat_purchase']= ins_sales['fk_master__dat_invoice'].strftime('%d-%m-%Y')

                        json_data['lst_items'][0]['int_days_missing']=int_days_missing
                        json_data['lst_items'][0]['int_depreciation_amt']=int_amount
                        json_data['lst_items'][0]['purchase_branch']=ins_sales['fk_master__fk_branch__vchr_name']







                    json_data['int_branch_id']=Branch.objects.filter(vchr_code=json_data['vchr_branch_code']).values('pk_bint_id').first()['pk_bint_id']
                    del json_data['lst_item']
                    del json_data['int_enq_master_id']
                    json_data['str_cust_name']=json_data['vchr_cust_name']
                    del json_data['vchr_cust_name']
                    json_data['dbl_total_amt']=0
                    json_data['dbl_discount']=0

                    ins_p.json_data=json_data
                    ins_p.save()
                    if ins_sales:

                      return Response({'status':1,"dat_purchase":ins_sales['fk_master__dat_invoice'],'int_days_missing':int_days_missing,'int_amount':int_amount})
                    else:
                         pass
            return Response({'status':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

class AddSalesAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            
            dct_data = {}
            str_cust_name = request.data.get('vchr_cust_name')
            str_cust_email = request.data.get('vchr_cust_email',None)
            int_cust_mob = request.data.get('int_cust_mob')
            int_cust_type = request.data.get('int_customer_type',4)
            dbl_cust_credit_amount = request.data.get('dbl_credit_amount')
            dct_data['str_remarks'] = request.data.get('str_remarks')
            dct_data['dat_created'] = request.data.get('dat_enquiry')
            dct_data['dbl_total_amt'] = request.data.get('dbl_total_amt')
            dct_data['dbl_total_tax'] = request.data.get('dbl_total_tax')
            dct_data['dbl_discount'] = request.data.get('dbl_discount')
            dct_data['int_enq_master_id'] = request.data.get('int_enq_master_id')
            dct_data['vchr_enquiry_num'] = request.data.get('vchr_enquiry_num')
            dct_data['vchr_finance_name'] = request.data.get('vchr_finance_name')
            dct_data['vchr_fin_comp'] = request.data.get('vchr_fin_comp')
            dct_data['vchr_finance_schema'] = request.data.get('vchr_finance_schema')
            dct_data['dbl_finance_amt'] = request.data.get('dbl_finance_amt')
            dct_data['int_enquiry_type'] = request.data.get('int_enquiry_type',0)
            dct_data['vchr_reference_num'] = request.data.get('vchr_reference_num',None)
            dct_data['dbl_loyalty_amt'] = request.data.get('dbl_loyalty_amt',None)
            dct_data['vchr_order_num'] = request.data.get('vchr_order_num',None)
            dct_data['dbl_emi'] = request.data.get('dbl_emi')
            dct_data['dbl_down_payment'] = request.data.get('dbl_down_payment')
            dct_data['vchr_fin_ordr_num'] = request.data.get('vchr_fin_ordr_num')
            dct_data['lst_items'] = request.data.get('lst_item')
            dct_data['str_cust_name'] = str_cust_name
            dct_data['int_staff_id'] = 0
            dct_data['str_staff_name'] = ''
            dct_data['int_branch_id'] = 0
            dct_data['str_branch'] = ''

            # finance
            dct_data['dbl_processing_fee'] = float(request.data.get('processing_fee')) if request.data.get('processing_fee') else None
            dct_data['dbl_margin_money'] = float(request.data.get('margin_money')) if request.data.get('margin_money') else None
            dct_data['dbl_dbd_amount'] = float(request.data.get('dbd_amount')) if request.data.get('dbd_amount') else None
            dct_data['dbl_service_charge'] = float(request.data.get('service_charge')) if request.data.get('service_charge') else None
            dct_data['dbl_net_loan_amount'] = float(request.data.get('net_loan_amount')) if request.data.get('net_loan_amount') else None
            # LG 08-07-2020
            # dct_data['bln_bajaj_online'] = request.data.get('bln_bajaj') or False
            dct_data['int_finance_type'] = request.data.get('finance_type')

            dct_data['vchr_bank_name'] = request.data.get('vchr_bank_name')
            dct_data['bint_account_number'] = request.data.get('bint_account_number')
            dct_data['vchr_cheque_number'] = request.data.get('vchr_cheque_number')
            dct_data['vchr_initial_payment_type'] = request.data.get('vchr_initial_payment_type')
            dct_data['bln_specialsale'] = request.data.get('bln_specialsale','False')

            bln_ecom_sale =  request.data.get('bln_ecom_sale',False)
            dct_data['bln_ecom_sale'] = bln_ecom_sale
            



            if request.data.get('lst_offers'):
                dct_data['lst_offers']=request.data.get('lst_offers')
            int_status=request.data.get('int_status',1)


            ins_branch = Branch.objects.filter(vchr_code = request.data.get('vchr_branch_code')).values('pk_bint_id','vchr_name','fk_states_id').first()




            if bln_ecom_sale:
                """Ecom User Creation"""



                dct_ecom_staff = request.data.get('ecom_staff')




                str_branch_code = dct_ecom_staff.get('str_branch_code')
                str_company_code = dct_ecom_staff.get('str_comp_code')

                int_branch_id = Branch.objects.filter(vchr_code = str_branch_code).values_list('pk_bint_id',flat = True).first()

                int_company_id = Company.objects.filter(vchr_name__icontains = str_company_code ).values_list('pk_bint_id',flat = True).first()
                str_first_name = dct_ecom_staff.get("first_name")
                str_last_name = dct_ecom_staff.get("last_name")
                int_phone = dct_ecom_staff.get("bint_phone")
                str_username = dct_ecom_staff.get("username")
                str_com_code = dct_ecom_staff.get("str_comp_code")


                ins_staff, bln_created = Userdetails.objects.get_or_create(
                                        username = str_username,
                                        defaults = {
                                        'bint_phone'  :  int_phone,
                                        'fk_company_id' : int_company_id,
                                        'fk_branch_id' : int_branch_id,
                                        'vchr_profpic' : '/media/default.jpg',
                                        'first_name' : str_first_name,
                                        'last_name' : str_last_name,
                                        'email' : '--',
                                        'username' : str_username,
                                        'is_active' : False,
                                        'is_superuser' : False,
                                        'dat_created' : datetime.now(),
                                        'dat_updated' : datetime.now()
                                        }


                                        )

                ins_staff.set_password('testpass')
                ins_staff.save()
                int_staff_id = ins_staff.user_ptr_id
                dct_data['int_staff_id'] = ins_staff.user_ptr_id
                dct_data['str_staff_name'] = ins_staff.first_name+' '+ins_staff.last_name


            else:
                ins_staff = Userdetails.objects.filter(username = request.data.get('vchr_staff_code'),is_active = True).values('user_ptr_id','first_name','last_name').first()
                if ins_staff :
                    int_staff_id = ins_staff['user_ptr_id']
                    dct_data['int_staff_id'] = ins_staff['user_ptr_id']
                    dct_data['str_staff_name'] = ins_staff['first_name']+' '+ins_staff['last_name']
                else:
                    return Response({'error_status':'0','message':'No User in POS with user code '+request.data.get('vchr_staff_code')})




            if ins_branch:
                dct_data['int_branch_id'] = ins_branch['pk_bint_id']
                dct_data['str_branch'] = ins_branch['vchr_name']
            else:
                return Response({'error_status':'0','message':'No Branch in POS with Branch code '+request.data.get('vchr_branch_code')})



            ins_state = None
            if request.data.get('vchr_state_code'):
                ins_state = States.objects.filter(vchr_code = request.data.get('vchr_state_code')).first()
            ins_district = None
            if 0 and request.data.get('vchr_district'):
                ins_district = District.objects.filter(vchr_name = request.data.get('vchr_district')).first()
                if not ins_district:
                    ins_district = District.objects.create(vchr_name = request.data.get('vchr_district'),fk_state=ins_state)
                if not ins_state:
                    ins_state = ins_district.fk_state
            ins_location = None
            if request.data.get('vchr_pin_code'):
                ins_location = Location.objects.filter(vchr_pin_code=request.data.get('vchr_pin_code',None)).first()
                if not ins_location:
                    ins_location = Location.objects.create(vchr_name=request.data.get('vchr_location',None),vchr_pin_code=request.data.get('int_pin_code',None))
                #if not ins_district:
                    #ins_district = ins_location.fk_district
                if not ins_state:
                    ins_state = ins_location.fk_state
            if not ins_state and ins_branch:
                ins_state =  States.objects.filter(pk_bint_id=ins_branch['fk_states_id']).first()
            ins_customer = CustomerDetails.objects.filter(int_mobile = int_cust_mob,int_cust_type = int_cust_type).values('pk_bint_id').first()
            if not ins_customer:
                ins_cust = CustomerDetails.objects.create(
                                                                vchr_name = str_cust_name,
                                                                vchr_email = str_cust_email,
                                                                int_cust_type = int_cust_type,
                                                                dbl_credit_balance = dbl_cust_credit_amount,
                                                                dbl_credit_limit =  dbl_cust_credit_amount,
                                                                int_mobile = int_cust_mob,
                                                                vchr_gst_no = request.data.get('vchr_gst_no',None),
                                                                txt_address = request.data.get('txt_address',None),
                                                                fk_location = ins_location,
                                                                fk_state = ins_state,
                                                                int_edit_count=0

                                                             )

                # ========================================================================================================
                ins_sales_customer = SalesCustomerDetails.objects.create(
                                                        fk_customer_id = ins_cust.pk_bint_id,
                                                        dat_created = datetime.now(),
                                                        fk_created_id = int_staff_id,
                                                        vchr_name = str_cust_name,
                                                        vchr_email = str_cust_email,
                                                        int_cust_type = int_cust_type,
                                                        int_mobile = int_cust_mob,
                                                        vchr_gst_no = request.data.get('vchr_gst_no',None),
                                                        txt_address = request.data.get('txt_address',None),
                                                        fk_location = ins_location,
                                                        fk_state = ins_state
                                                     )
                dct_data['int_sales_cust_id'] = ins_sales_customer.pk_bint_id
                # ========================================================================================================
                dct_data['int_cust_id'] = ins_cust.pk_bint_id
            else:
                # =============================================================================================================
                dct_data['int_cust_id'] = ins_customer['pk_bint_id']
                CustomerDetails.objects.filter(pk_bint_id = dct_data['int_cust_id']).update(txt_address = request.data.get('txt_address',None))
                ins_customer_exist = CustomerDetails.objects.filter(vchr_name = str_cust_name,vchr_email = str_cust_email,int_mobile = int_cust_mob,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state,int_cust_type = int_cust_type)
                ins_cus = CustomerDetails.objects.get(pk_bint_id=dct_data['int_cust_id'])
                int_edit_count=ins_cus.int_edit_count if ins_cus.int_edit_count else 0
                if not ins_customer_exist:
                    ins_cus.vchr_email = str_cust_email
                    ins_cus.int_cust_type = int_cust_type
                    ins_cus.vchr_gst_no = request.data.get('vchr_gst_no',None)
                    ins_cus.txt_address = request.data.get('txt_address',None)
                    ins_cus.fk_location = ins_location
                    ins_cus.fk_state = ins_state
                    ins_cus.int_edit_count=int_edit_count+1
                    ins_cus.save()
                ins_sales_customer=SalesCustomerDetails.objects.filter(vchr_name = str_cust_name,vchr_email = str_cust_email,int_mobile = int_cust_mob,vchr_gst_no = request.data.get('vchr_gst_no',None),  fk_location = ins_location,fk_state = ins_state).order_by('-pk_bint_id').first()
                if not ins_sales_customer:

                    ins_sales_customer = SalesCustomerDetails.objects.create(
                                                            fk_customer_id = ins_cus.pk_bint_id,
                                                            dat_created = datetime.now(),
                                                            fk_created_id = int_staff_id,
                                                            vchr_name = ins_cus.vchr_name,
                                                            vchr_email = ins_cus.vchr_email,
                                                            int_mobile = ins_cus.int_mobile,
                                                            fk_state_id = ins_cus.fk_state_id,
                                                            int_loyalty_points = ins_cus.int_loyalty_points,
                                                            int_redeem_point = ins_cus.int_redeem_point,
                                                            dbl_purchase_amount = ins_cus.dbl_purchase_amount,
                                                            vchr_loyalty_card_number = ins_cus.vchr_loyalty_card_number,
                                                            txt_address = ins_cus.txt_address,
                                                            vchr_gst_no = ins_cus.vchr_gst_no,
                                                            int_otp_number = ins_cus.int_otp_number,
                                                            fk_location_id = ins_cus.fk_location_id,
                                                            fk_loyalty_id = ins_cus.fk_loyalty_id,
                                                            vchr_code = ins_cus.vchr_code,
                                                            int_cust_type=ins_cus.int_cust_type
                                                        )
                else:
                    SalesCustomerDetails.objects.filter(pk_bint_id = ins_sales_customer.pk_bint_id).update(txt_address = ins_cus.txt_address)
                    pass
                dct_data['int_sales_cust_id'] = ins_sales_customer.pk_bint_id
                # =============================================================================================================
                # dct_data['int_cust_id'] = ins_customer['pk_bint_id']
                # ins_customer = CustomerDetails.objects.filter(vchr_name = str_cust_name,vchr_email = str_cust_email,int_mobile = int_cust_mob,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)
                # if not ins_customer:
                #     CustomerDetails.objects.filter(pk_bint_id=dct_data['int_cust_id']).update(vchr_email = str_cust_email,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)

            #
            # for data in dct_daa['lst_items']:
            #     if data['int_status']==2:
            #         ins_branch_stock_details = ExchangeStock(fk_item=Items.objects.get(vchr_item_code=data['vchr_item_code']),int_avail=data['int_quantity'],jsn_imei={'imei'=[data['vchr_imei']]},jsn_avail={'imei':[data['vchr_imei']]},fk_branch

            # -------- Followup ----------
            if  request.data.get('bln_service'):
                
                # ins_par_inv = PartialInvoice.objects.filter(int_status=6,int_enq_master_id = int(request.data.get('int_enq_master_id')), int_active__in = [0,3], dat_created__date = request.data.get('dat_enquiry'))
                # LG
                ins_par_inv = PartialInvoice.objects.filter(int_status__in=[5,6],int_enq_master_id = int(request.data.get('int_enq_master_id')), int_active__in = [0,3])
                #********************************NOT SERVICED,DELETION FROM RECEIPT**********************************
                # if request.data.get('int_status')==5:
                #     Receipt.objects.filter(dbl_amount=request.data.get('lst_item')[0]['dbl_advc_paid']).update(int_doc_status=-1)
                #     ins_par_inv.update(int_active=1)
                #*****************************************************************************************************
                if ins_par_inv:
                    int_partial_id = ins_par_inv[0].pk_bint_id
                    json_data_all={}
                    vchr_status = dct_data['lst_items'][-1]['vchr_job_status']
                    vchr_remark = dct_data['lst_items'][-1]['vchr_remarks']
                    int_amount = dct_data['lst_items'][-1]['dbl_amount']
                    str_imei =dct_data['lst_items'][-1]['vchr_imei']
                    dbl_discount_amount = dct_data['lst_items'][-1]['dbl_discount']

                    json_data_all = ins_par_inv.first().json_data
                    dct_data['lst_items'][-1].update(json_data_all['lst_items'][0])
                    json_data_all.update(dct_data)

                    json_data_all['lst_items'][-1]['vchr_job_status'] = vchr_status
                    json_data_all['lst_items'][-1]['vchr_job_status'] = vchr_status
                    json_data_all['lst_items'][-1]['vchr_remarks'] = vchr_remark
                    json_data_all['lst_items'][-1]['dbl_amount'] = int_amount
                    json_data_all['lst_items'][-1]['vchr_imei'] = str_imei
                    json_data_all['lst_items'][-1]['dbl_discount'] = dbl_discount_amount
                    json_data_all['lst_items'][-1]['json_worked_on']=request.data.get('json_worked_on')
                    ins_par_inv.update(int_status=int_status,json_data = json_data_all,dat_created = datetime.now(),int_active=0)

                if  request.data.get('bln_spare_avd_amount'):
                    dct_json_data = {"branchid": request.data.get('int_branch_id'),
                                     "strEmail": request.data.get('vchr_cust_email',None),
                                     "staffcode": request.data.get("vchr_staff_code"),
                                     "strMobNum": request.data.get('int_cust_mob'),
                                     "vchrgstno": request.data.get('vchr_gst_no'),
                                     "intPinCode": request.data.get('int_pin_code'),
                                     "strRemarks": request.data.get("str_remarks"),
                                     "strCustName":request.data.get('vchr_cust_name'),
                                     "strLocation": request.data.get('vchr_location'),
                                     "dblAdvAmount":request.data.get('flt_advance_spare_amount'),
                                     "strItemnName": "",
                                     "strStateCode": "",
                                     "intPartialInvoiceId": int_partial_id,
                                     "vchrenquirynum":request.data.get('vchr_job_num'),
                                     "dblcreditamount": 0.0,
                                      "intcustomertype": request.data.get('int_customer_type',4),
                                      "vchr_customer_addres": request.data.get('txt_address')}

                    dct_cust_details = dct_json_data

                    ins_partial_receipt = PartialReceipt.objects.create(
                                                                        json_data = json.dumps(dct_json_data),
                                                                        fk_enquiry_master_id = int(request.data.get('int_enq_master_id')),
                                                                        vchr_branchcode =  request.data.get('vchr_branch_code'),
                                                                        vchr_item_code = request.data.get('strItemCode'),
                                                                        int_status = 0,
                                                                        bln_service =True,
                                                                        dat_created=datetime.now()

                                                                        )




            else:
                ins_partial_inv = PartialInvoice.objects.filter(int_enq_master_id = int(request.data.get('int_enq_master_id')), int_active=0, dat_created__date = request.data.get('dat_enquiry')).first()
                if ins_partial_inv:
                    json_data = ins_partial_inv.json_data
                    json_data['vchr_finance_name'] = request.data.get('vchr_finance_name', ins_partial_inv.json_data.get('vchr_finance_name'))
                    json_data['vchr_finance_schema'] = request.data.get('vchr_finance_schema', ins_partial_inv.json_data.get('vchr_finance_schema'))
                    json_data['vchr_finance_comp']=request.data.get('vchr_fin_comp', ins_partial_inv.json_data.get('vchr_fin_comp'))
                    json_data['dbl_finance_amt'] = request.data.get('dbl_finance_amt', ins_partial_inv.json_data.get('dbl_finance_amt'))
                    json_data['dbl_emi'] = request.data.get('dbl_emi', ins_partial_inv.json_data.get('dbl_emi'))
                    json_data['dbl_down_payment'] = request.data.get('dbl_down_payment', ins_partial_inv.json_data.get('dbl_down_payment'))
                    json_data['vchr_fin_ordr_num'] = request.data.get('vchr_fin_ordr_num', ins_partial_inv.json_data.get('vchr_fin_ordr_num'))
                    json_data['lst_items'].extend(request.data.get('lst_item'))
                    json_data['dbl_total_amt'] += request.data.get('dbl_total_amt')
                    json_data['dbl_discount'] += request.data.get('dbl_discount')

                    ins_partial_inv.json_data = json_data


                    ins_partial_inv.save()
                    return Response({'status':'1'})
                else:

                    if bln_ecom_sale:
                        """For ecommmerce Third-party api"""
                        ins_ecom_part = PartialInvoice(int_status=int_status,
                                                    json_data = dct_data,dat_created = datetime.now(),
                                                    int_enq_master_id=request.data.get('int_enq_master_id'),
                                                    int_sale_type = 1
                                                    )
                        ins_ecom_part.save()

                        return Response({'status':'1','SO_NUM':ins_ecom_part.pk_bint_id})


                    else:
                        PartialInvoice.objects.create(int_status=int_status,json_data = dct_data,dat_created = datetime.now(),int_enq_master_id=request.data.get('int_enq_master_id'))
            # ----------------------------
            return Response({'status':'1'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

class ItemAdvanceFilter(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            conn = engine.connect()

            int_product_id = request.data.get('intProductId')
            int_brand_id = request.data.get('intBrandId')
            int_item_cate_id = request.data.get('intItemCategoryId')
            int_item_group_id = request.data.get('intItemGroupId')
            int_item_id = request.data.get('intItemId')
            lst_item_id = []
            if int_product_id:
                if int_brand_id:
                    if int_item_cate_id:
                        if int_item_group_id:
                            if int_item_id:
                                lst_item_id = list(Item.objects.filter(pk_bint_id=int_item_id).values_list('pk_bint_id',flat=True))
                            else:
                                lst_item_id = list(Item.objects.filter(fk_product_id=int_product_id,fk_brand_id=int_brand_id,fk_item_category_id=int_item_cate_id,fk_item_group_id=int_item_group_id).values_list('pk_bint_id',flat=True))
                        else:
                            if int_item_id:
                                lst_item_id = list(Item.objects.filter(pk_bint_id=int_item_id).values_list('pk_bint_id',flat=True))
                            else:
                                lst_item_id = list(Item.objects.filter(fk_product_id=int_product_id,fk_brand_id=int_brand_id,fk_item_category_id=int_item_cate_id).values_list('pk_bint_id',flat=True))
                    else:
                        if int_item_group_id:
                            if int_item_id:
                                lst_item_id = list(Item.objects.filter(pk_bint_id=int_item_id).values_list('pk_bint_id',flat=True))
                            else:
                                lst_item_id = list(Item.objects.filter(fk_product_id=int_product_id,fk_brand_id=int_brand_id,fk_item_group_id=int_item_group_id).values_list('pk_bint_id',flat=True))
                        else:
                            if int_item_id:
                                lst_item_id = list(Item.objects.filter(pk_bint_id=int_item_id).values_list('pk_bint_id',flat=True))
                            else:
                                lst_item_id = list(Item.objects.filter(fk_product_id=int_product_id,fk_brand_id=int_brand_id).values_list('pk_bint_id',flat=True))
                else:
                    if int_item_cate_id:
                        if int_item_group_id:
                            if int_item_id:
                                lst_item_id = list(Item.objects.filter(pk_bint_id=int_item_id).values_list('pk_bint_id',flat=True))
                            else:
                                lst_item_id = list(Item.objects.filter(fk_product_id=int_product_id,fk_item_category_id=int_item_cate_id,fk_item_group_id=int_item_group_id).values_list('pk_bint_id',flat=True))
                        else:
                            if int_item_id:
                                lst_item_id = list(Item.objects.filter(pk_bint_id=int_item_id).values_list('pk_bint_id',flat=True))
                            else:
                                lst_item_id = list(Item.objects.filter(fk_product_id=int_product_id,fk_item_category_id=int_item_cate_id).values_list('pk_bint_id',flat=True))
                    else:
                        if int_item_group_id:
                            if int_item_id:
                                lst_item_id = list(Item.objects.filter(pk_bint_id=int_item_id).values_list('pk_bint_id',flat=True))
                            else:
                                lst_item_id = list(Item.objects.filter(fk_product_id=int_product_id,fk_item_group_id=int_item_group_id).annotate().values_list('pk_bint_id',flat=True))
                        else:
                            if int_item_id:
                                lst_item_id = list(Item.objects.filter(pk_bint_id=int_item_id).values_list('pk_bint_id',flat=True))
                            else:
                                return Response({'status':'0','message':'Minimum 2 Filters are Required'})
            else:
                return Response({'status':'0','message':'Product Required'})
            str_filter = ''
            if request.data.get('blnAvailStock'):
                str_filter = ' and stkm.fk_branch_id='+str(request.user.userdetails.fk_branch_id) +' and stkd.int_qty>0'
            if not lst_item_id:
                return Response({'status':'1','data':[]})
            int_price_template = request.user.userdetails.fk_branch.int_price_template
            if int_price_template == 0:
                str_amt_filter = 'dbl_cost_amnt'
            elif int_price_template == 1:
                str_amt_filter = 'dbl_dealer_amt'
            elif int_price_template == 2:
                str_amt_filter = 'dbl_mop'
            elif int_price_template == 3:
                str_amt_filter = 'dbl_my_amt'
            else:
                str_amt_filter = 'dbl_mrp'
            query = "select itm.pk_bint_id,itm.vchr_item_code,itm.vchr_name as vchr_item_name,br.vchr_name as vchr_brand_name,case when sum(stkd.int_qty)>0 then sum(stkd.int_qty) else 0 end as int_quantity, (select case when "+str_amt_filter+" is null then 0 else "+str_amt_filter+" end from price_list where int_status=1 and fk_item_id=itm.pk_bint_id and dat_efct_from<=current_date and int_status>=0 order by dat_efct_from desc limit 1) as dbl_price from item as itm join brands as br on br.pk_bint_id=itm.fk_brand_id left outer join branch_stock_details as stkd on stkd.fk_item_id=itm.pk_bint_id left outer join branch_stock_master as stkm on stkm.pk_bint_id=stkd.fk_master_id where itm.pk_bint_id in ("+str(lst_item_id)[1:-1]+")"+str_filter+" group by itm.pk_bint_id,itm.vchr_item_code,vchr_item_name,vchr_brand_name"
            ins_item_data = conn.execute(query).fetchall()
            lst_item_data = []
            for ins_data in ins_item_data:
                dct_data = {}
                dct_data['intItemId'] = ins_data.pk_bint_id
                dct_data['strItemCode'] = ins_data.vchr_item_code
                dct_data['strItemName'] = ins_data.vchr_item_name
                dct_data['strBrandName'] = ins_data.vchr_brand_name.title()
                dct_data['intQuantity'] = ins_data.int_quantity
                dct_data['dblPrice'] = ins_data.dbl_price
                dct_data['status']=True
                lst_item_data.append(dct_data)
            return Response({'status':1,'data':lst_item_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


class ApplyCoupon(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            
            str_coupon_code = request.data.get('strCode')
            lst_item_details = request.data.get('lstItemDetails')
            flt_total = request.data.get('intTotal')
            lst_product = []
            lst_brand = []
            lst_item_category = []
            lst_item_group = []
            lst_item = []
            for ins_data in lst_item_details:
                ins_item = Item.objects.filter(pk_bint_id=ins_data['intItemId']).values('pk_bint_id','fk_product_id','fk_brand_id','fk_item_category_id','fk_item_group_id').first()
                lst_product.append(ins_item['fk_product_id'])
                lst_brand.append(ins_item['fk_brand_id'])
                lst_item_category.append(ins_item['fk_item_category_id'])
                lst_item_group.append(ins_item['fk_item_group_id'])
                lst_item.append(ins_item['pk_bint_id'])
            ins_coupon = Coupon.objects.filter(Q(fk_product_id__in=lst_product)|Q(fk_brand_id__in=lst_brand)|Q(fk_item_category_id__in=lst_item_category)|Q(fk_item_group_id__in=lst_item_group)|Q(fk_item_id__in=lst_item)|Q(int_which=0),vchr_coupon_code=str_coupon_code,dat_expiry__gte=date.today()).values('pk_bint_id','int_discount_percentage','bint_max_discount_amt','bint_min_purchase_amt','int_max_usage_no').first()
            if ins_coupon:
                if flt_total>=ins_coupon['bint_min_purchase_amt']:
                    int_used_count = SalesMaster.objects.filter(fk_coupon_id=ins_coupon['pk_bint_id']).aggregate(coupon_count=Count('pk_bint_id'))['coupon_count']
                    if int_used_count>=ins_coupon['int_max_usage_no']:
                        return Response({'status':0,'message':'Coupon Usage Limit Exceeded'})
                    flt_disc = round(flt_total*ins_coupon['int_discount_percentage']/100,2)
                    if flt_disc>ins_coupon['bint_max_discount_amt']:
                        flt_disc = ins_coupon['bint_max_discount_amt']
                    elif flt_disc == 0.0 :
                        flt_disc = ins_coupon['bint_max_discount_amt']


                else:
                    return Response({'status':0,'message':'Minimum Purchase Amount '+str(ins_coupon['bint_min_purchase_amt'])})
            else:
                return Response({'status':0,'message':'Coupon Not Valid or Expired'})

            dct_data = {'intCouponId':ins_coupon['pk_bint_id'],'dblDisc':flt_disc}
            return Response({'status':1,'data':dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


class InvoicePrintApi(APIView):
    """
    to print invoice Details
    parameter:enquiry id
    return:pdf details
    """
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            
            session = Connection()
            p = inflect.engine()
            vchr_invoice_num = request.data.get('invoiceId')
            int_invoice_id = request.data.get('invoiceId')
            ins_gst_check = SalesMaster.objects.filter(pk_bint_id = int_invoice_id).values("fk_customer__vchr_gst_no",'vchr_irn_no','dat_invoice').first()
            dat_einvoice_avail = datetime.strptime('2020-10-01','%Y-%m-%d').date()
            ins_return_check = SalesDetails.objects.filter(fk_master_id = int_invoice_id).values("int_sales_status").first()
            if ins_gst_check["fk_customer__vchr_gst_no"] and  request.user.userdetails.fk_branch.vchr_code != 'AGY' and not ins_gst_check['vchr_irn_no'] and ins_gst_check["dat_invoice"] >= dat_einvoice_avail and ins_return_check["int_sales_status"] != 0:
                bln_host_status = False
                if request.scheme+'://'+request.get_host() == 'http://pos.mygoal.biz:4001' or request.scheme+'://'+request.get_host() == 'http://pos.mygoal.biz:5555':
                    bln_host_status = True
                bln_status = False
                res = einvoice_generation(int_invoice_id,bln_status,bln_host_status)
                if res["status"] == 0:
                    raise ValueError(res["reason"])
            # vchr_invoice_num = 'INV-0044'
            # vchr_invoice_num = 'INC-0001'
            # rst_invoice = session.query(SalesDetailsJS.c.int_qty.label('qty'),SalesDetailsJS.c.dbl_amount.label('item_amount'),SalesDetailsJS.c.dbl_discount.label('item_discount'),\
                            # SalesDetailsJS.c.dbl_buyback.label('item_buyback'),SalesDetailsJS.c.json_tax.label('item_tax'),ItemsSA.vchr_name.label('item'),ItemsSA.vchr_item_code.label('item_code'),\
                            # SalesMasterJS.c.dat_created.label('invoice_date'),SalesMasterJS.c.vchr_invoice_num.label('invoice_num'),SalesMasterJS.c.dbl_total_amt.label('total_amount'),\
                            # SalesMasterJS.c.dbl_total_tax.label('total_tax'),SalesMasterJS.c.dbl_coupon_amt.label('coupon_amount'),SalesMasterJS.c.dbl_buyback.label('total_buy_back'),\
                            # SalesMasterJS.c.dbl_loyalty.label('total_loyalty'),SalesMasterJS.c.dbl_discount.label('total_discount'),CustServiceDeliverySA.vchr_cust_name.label('sh_cust_name'),CustServiceDeliverySA.int_mobile.label('sh_mobile'),\
                            # CustServiceDeliverySA.txt_address.label('sh_txt_add'),CustServiceDeliverySA.vchr_landmark.label('sh_landmark'),CustServiceDeliverySA.vchr_gst_no.label('sh_gst'),\
                            # CustomerDetailsSA.vchr_name.label('cust_name'),CustomerDetailsSA.vchr_email.label('cust_mail'),CustomerDetailsSA.int_mobile.label('cust_mobile'),\
                            # CustomerDetailsSA.txt_address.label('cust_add'),CustomerDetailsSA.vchr_gst_no.label('cust_gst'),\
                            # func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('staff'))\
                            # .join(SalesMasterJS,SalesMasterJS.c.pk_bint_id==SalesDetailsJS.c.fk_master_id)\
                            # .outerjoin(CustServiceDeliverySA,CustServiceDeliverySA.fk_sales_master_id == SalesMasterJS.c.pk_bint_id)\
                            # .join(CustomerDetailsSA,CustomerDetailsSA.pk_bint_id == SalesMasterJS.c.fk_customer_id)\
                            # .outerjoin(AuthUserSA,AuthUserSA.id==SalesMasterJS.c.fk_staff_id)\
                            # .join(ItemsSA,ItemsSA.pk_bint_id == SalesDetailsJS.c.fk_item_id)\
                            # .filter(SalesMasterJS.c.pk_bint_id == vchr_invoice_num)


            rst_invoice = session.query(SalesDetailsJS.c.int_qty.label('qty'),SalesDetailsJS.c.dbl_amount.label('item_amount'),SalesDetailsJS.c.dbl_discount.label('item_discount'),SalesDetailsJS.c.int_sales_status.label('int_status'),\
                            SalesDetailsJS.c.dbl_buyback.label('item_buyback'),SalesDetailsJS.c.dbl_selling_price.label('selling_price'),SalesDetailsJS.c.json_tax.label('item_tax'),SalesDetailsJS.c.dbl_indirect_discount.label('indirect_discount'),\
                            SalesDetailsJS.c.json_imei.label('json_imei'),ItemsSA.vchr_name.label('item'),ItemsSA.vchr_item_code.label('item_code'),\
                            BranchSA.vchr_phone.label('branch_mob'),BranchSA.vchr_code.label('branch_code'),BranchSA.vchr_email.label('branch_mail'),BranchSA.vchr_address.label('branch_address'),BranchSA.vchr_mygcare_no.label('mygcare_no'),SalesMasterJS.c.dat_created.label('invoice_date'),SalesMasterJS.c.vchr_invoice_num.label('invoice_num'),SalesMasterJS.c.vchr_irn_no,SalesMasterJS.c.txt_qr_code,SalesMasterJS.c.dbl_total_amt.label('total_amount'),\
                            SalesMasterJS.c.vchr_journal_num.label('journal_num'),SalesMasterJS.c.dbl_total_tax.label('total_tax'),SalesMasterJS.c.dbl_coupon_amt.label('coupon_amount'),SalesMasterJS.c.dbl_buyback.label('total_buy_back'),SalesMasterJS.c.jsn_addition.label('jsn_addition'),SalesMasterJS.c.jsn_deduction.label('jsn_deduction'),\
                            SalesMasterJS.c.dbl_loyalty.label('total_loyalty'),SalesMasterJS.c.dbl_discount.label('total_discount'),CustServiceDeliverySA.vchr_cust_name.label('sh_cust_name'),CustServiceDeliverySA.int_mobile.label('sh_mobile'),\
                            CustServiceDeliverySA.txt_address.label('sh_txt_add'),CustServiceDeliverySA.vchr_landmark.label('sh_landmark'),CustServiceDeliverySA.vchr_gst_no.label('sh_gst'),\
                            SalesCustomerDetailsSA.vchr_name.label('cust_name'),SalesCustomerDetailsSA.vchr_email.label('cust_mail'),SalesCustomerDetailsSA.int_mobile.label('cust_mobile'),\
                            SalesCustomerDetailsSA.txt_address.label('cust_add'),SalesCustomerDetailsSA.vchr_gst_no.label('cust_gst'),\
                            ProductsSA.vchr_name.label('product_name'),BrandSA.vchr_name.label('brand_name'),\
                            func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('staff'),UserdetailsSA.bint_phone.label('phone'),CompanySA.vchr_gstin.label('gstin'),\
                            StatesSA.vchr_name.label('state'),StatesSA.vchr_code.label('state_code'),\
                            ItemCategorySA.vchr_hsn_code.label('vchr_hsn_code'))\
                            .join(SalesMasterJS,SalesMasterJS.c.pk_bint_id==SalesDetailsJS.c.fk_master_id)\
                            .join(BranchSA,SalesMasterJS.c.fk_branch_id==BranchSA.pk_bint_id)\
                            .join(StatesSA,StatesSA.pk_bint_id==BranchSA.fk_states_id)\
                            .outerjoin(CustServiceDeliverySA,CustServiceDeliverySA.fk_sales_master_id == SalesMasterJS.c.pk_bint_id)\
                            .join(SalesCustomerDetailsSA,SalesCustomerDetailsSA.pk_bint_id == SalesMasterJS.c.fk_customer_id)\
                            .outerjoin(AuthUserSA,AuthUserSA.id==SalesMasterJS.c.fk_staff_id)\
                            .outerjoin(UserdetailsSA,UserdetailsSA.user_ptr_id==AuthUserSA.id)\
                            .join(CompanySA,CompanySA.pk_bint_id==UserdetailsSA.fk_company_id)\
                            .join(ItemsSA,ItemsSA.pk_bint_id == SalesDetailsJS.c.fk_item_id)\
                            .join(ItemCategorySA,ItemCategorySA.pk_bint_id == ItemsSA.fk_item_category_id)\
                            .join(BrandSA,BrandSA.pk_bint_id == ItemsSA.fk_brand_id)\
                            .join(ProductsSA,ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                            .filter(SalesMasterJS.c.pk_bint_id == vchr_invoice_num)

            rst_return = session.query(SalesReturnSA.vchr_doc_code.label('srn_no'),SalesReturnSA.dat_returned.label('srn_date'),\
                            SalesReturnSA.fk_returned_id.label('return_invoice_id'))\
                            .join(SalesMasterJS,SalesReturnSA.fk_sales_id==SalesMasterJS.c.pk_bint_id)\
                            .filter(SalesMasterJS.c.pk_bint_id == vchr_invoice_num)

            lst_payment_details  = PaymentDetails.objects.filter(fk_sales_master_id = vchr_invoice_num ).values('int_fop').annotate( amt=Case(When (int_fop=0,then = Coalesce(Sum('dbl_finance_amt'), Value(0))),default =Coalesce(Sum('dbl_receved_amt'), Value(0)) ),
                                                                                                                                     payment = Case( When(int_fop=0, then=Value('FINANCE')),
                                                                                                                                                     When(int_fop=1, then=Value('CASH')),
                                                                                                                                                     When(int_fop=2, then=Value('DC')),
                                                                                                                                                     When(int_fop=3, then=Value('CC')),
                                                                                                                                                     When(int_fop=4, then=Value('ADVANCE')),
                                                                                                                                                     When(int_fop=5, then=Value('PAYTM')),
                                                                                                                                                     When(int_fop=6, then=Value('PAYTM MALL')),
                                                                                                                                                     When(int_fop=7, then=Value('Bharath QR')),
                                                                                                                                                     default=Value('OTHER'),
                                                                                                                                                     output_field=CharField()
                                                                                                                                                   )
                                                                                                                                    )

            ins_finance_details = FinanceDetails.objects.filter(fk_payment__fk_sales_master_id = vchr_invoice_num).values('dbl_receved_amt',
                                                                                                                          'dbl_finance_amt',
                                                                                                                          'dbl_processing_fee',
                                                                                                                          'dbl_margin_fee',
                                                                                                                          'dbl_service_amt',
                                                                                                                          'dbl_dbd_amt').first()
            dbl_total_finance_extra_charge = 0
            dct_invoice = {}
            dct_voucher = {}
            dct_invoice['total'] = 0
            dct_voucher['total_amount'] = 0
            dct_voucher['lst_item'] = []
            dct_invoice['lst_returned']=[]
            dct_invoice['lst_insurance'] =[]
            dct_invoice['service_charge'] = 0
            bln_service_customer_print=False
            bln_exchange_print = False
            
            #if finance ,have to  add dbl_processing_fee dbl_margin_fee,dbl_service_amt from financedetails
            # if  ins_finance_details:
            #     lst_finance_extra_charge =  [ins_finance_details['dbl_processing_fee'],  ins_finance_details['dbl_service_amt'],  ins_finance_details['dbl_dbd_amt'] ]
            #     dbl_total_finance_extra_charge  = sum(filter(None, lst_finance_extra_charge))
            #     dct_invoice['service_charge'] = ins_finance_details.get('dbl_processing_fee',0) + ins_finance_details.get('dbl_service_amt',0) +ins_finance_details.get('dbl_dbd_amt',0)
            #     dct_invoice['total']+=dbl_total_finance_extra_charge
            if lst_payment_details and not ins_finance_details:
                dct_invoice['lst_payment_details'] = ' , '.join('{} - {}'.format(*data) for data in {item['payment']:str('{0:.2f}'.format(round(item['amt'],2))) if item['payment'] !='FINANCE' else str('{0:.2f}'.format(round((item['amt']),2)))    for item in lst_payment_details}.items())
                print(dct_invoice['lst_payment_details'])
                    # dct_invoice['lst_payment_details'].append()

            dct_invoice['lst_item']=[]
            dct_invoice['tax'] = {}
            dct_invoice['tax']['CGST'] = {}
            dct_invoice['tax']['SGST'] = {}
            dct_invoice['tax']['IGST'] = {}
            dct_invoice['bln_igst'] = False

            dct_invoice['amount'] = 0.0
            dct_invoice['discount'] = 0.0
            dct_invoice['buyback'] = 0.0
            dct_invoice['coupon'] = 0.0
            # dct_invoice['loyalty'] = 0.0
            dct_invoice['total_tax'] = 0.0
            dct_invoice['loyalty'] = 0.0
            dct_invoice['indirect_discount'] = 0.0
            dct_invoice['bln_kfc'] = False
            dct_invoice['dbl_kfc'] = 0.0
            dct_invoice['return_amount'] = 0.0
            rst_state = SalesMaster.objects.filter(pk_bint_id = vchr_invoice_num).values('fk_customer__fk_state__vchr_name','fk_customer__fk_state__vchr_code','fk_branch__fk_states__vchr_name','fk_branch__fk_states__vchr_code','fk_customer__vchr_gst_no','fk_customer__fk_customer__int_cust_type')
            if rst_state:
                dct_invoice['cust_state'] = rst_state[0]['fk_customer__fk_state__vchr_name']
                dct_invoice['cust_state_code'] = rst_state[0]['fk_customer__fk_state__vchr_code'] if rst_state[0]['fk_customer__fk_state__vchr_code'] else ''
                if not rst_state[0]['fk_customer__fk_state__vchr_name'].upper() == rst_state[0]['fk_branch__fk_states__vchr_name'].upper() or rst_state[0]['fk_customer__fk_customer__int_cust_type']==3:
                    dct_invoice['bln_igst'] = True
                elif not rst_state[0]['fk_customer__vchr_gst_no']:
                    dct_invoice['bln_kfc'] = True

            for ins_invoice in rst_invoice.all():

                dct_item = {}
                dct_item['item'] = ins_invoice.item
                dct_item['item_code'] = ins_invoice.item_code
                dct_item['hsn_code'] = ins_invoice.vchr_hsn_code
                dct_item['qty'] = ins_invoice.qty
                dct_item['selling_price'] = abs(ins_invoice.selling_price)


                if ins_invoice.int_status==0:
                    int_item_amount=-(ins_invoice.item_amount)
                else:
                    int_item_amount=ins_invoice.item_amount
                dct_item['amount'] = round(int_item_amount,2)
                dct_item['discount'] = abs(ins_invoice.item_discount if ins_invoice.item_discount else 0)
                dct_item['buyback'] = abs(ins_invoice.item_buyback if ins_invoice.item_buyback else 0)
                dct_item['int_status'] = ins_invoice.int_status


                dct_item['str_imei'] = ""
                if ins_invoice.json_imei:
                    dct_item['str_imei'] = ",".join(imei for imei in ins_invoice.json_imei if imei)

                if ins_invoice.int_status!=0:

                    if ins_invoice.item_tax:
                        dct_item['sgst'] = 0
                        dct_item['cgst'] = 0
                        dct_item['igst'] = 0
                        total_tax = 0
                        if not dct_invoice['bln_igst']:
                            if dct_invoice['bln_kfc'] :

                                dct_invoice['dbl_kfc'] += ins_invoice.item_tax['dblKFC']
                                total_tax += ins_invoice.item_tax['dblKFC']
                            dct_item['sgstp'] = ins_invoice.item_tax.get('dblSGST%',0)
                            if ins_invoice.item_tax['dblSGST']:
                                total_tax += ins_invoice.item_tax['dblSGST']
                                # flt_sgst = round(((ins_invoice.item_tax['dblSGST'])/(int_item_amount-ins_invoice.item_discount))*100,1)
                                # flt_sgst = round(((ins_invoice.item_tax['dblSGST']/ins_invoice.qty)/(ins_invoice.item_amount-ins_invoice.item_discount))*100,1)
                                dct_item['sgst'] = ins_invoice.item_tax.get('dblSGST%',0)
                                if dct_item['sgst'] not in dct_invoice['tax']['SGST']:
                                    dct_invoice['tax']['SGST'][dct_item['sgst']]=round(ins_invoice.item_tax['dblSGST'],2)
                                else:
                                    dct_invoice['tax']['SGST'][dct_item['sgst']]+=round(ins_invoice.item_tax['dblSGST'],2)
                            dct_item['cgstp'] = ins_invoice.item_tax.get('dblCGST%',0)
                            if ins_invoice.item_tax['dblCGST']:
                                total_tax += ins_invoice.item_tax['dblCGST']
                                dct_item['cgst'] = ins_invoice.item_tax.get('dblCGST%',0)
                                if dct_item['cgst'] not in dct_invoice['tax']['CGST']:
                                    dct_invoice['tax']['CGST'][dct_item['cgst']]=round(ins_invoice.item_tax['dblCGST'],2)
                                else:
                                    dct_invoice['tax']['CGST'][dct_item['cgst']]+=round(ins_invoice.item_tax['dblCGST'],2)
                        else:

                            if ins_invoice.item_tax['dblIGST']:
                                total_tax += ins_invoice.item_tax['dblIGST']
                                dct_item['igst'] = ins_invoice.item_tax.get('dblIGST%',0)
                                if dct_item['igst'] not in dct_invoice['tax']['IGST']:
                                    dct_invoice['tax']['IGST'][dct_item['igst']] = round(ins_invoice.item_tax['dblIGST'],2)
                                else:
                                    dct_invoice['tax']['IGST'][dct_item['igst']]+=round(ins_invoice.item_tax['dblIGST'],2)


                # dct_item['tax'] = ins_invoice.item_tax
                        dct_item['total'] = round((int_item_amount)+total_tax,2)#-ins_invoice.item_buyback
                        dct_invoice['total'] += dct_item['total']
                if ins_invoice.indirect_discount:
                    dct_voucher['branch'] = request.user.userdetails.fk_branch.vchr_name.title()
                    dct_voucher_item = {}
                    dct_voucher_item['item_name'] = ins_invoice.item
                    dct_voucher_item['amount'] = round(ins_invoice.indirect_discount,2)
                    dct_voucher['total_amount'] += round(ins_invoice.indirect_discount,2)
                    dct_voucher['lst_item'].append(dct_voucher_item)

                dct_invoice['indirect_discount'] += ins_invoice.indirect_discount if ins_invoice.indirect_discount else 0
                if ins_invoice.int_status==0:
                    ins_return_details = rst_return.all()[0] if rst_return.all() else None
                    if rst_return.all() :
                        int_return_invoice_id = ins_return_details.return_invoice_id if rst_return.all() else ''
                        
                        inst_json=SalesMaster.objects.filter(pk_bint_id=vchr_invoice_num).values('jsn_addition','jsn_deduction').first()
                        dct_invoice['total_addition'] =0
                        dct_invoice['total_deduction'] =0
                        dct_invoice['dct_addition_data'] = {}
                        dct_invoice['dct_deduction_data'] = {}

                        if inst_json:
                            if inst_json.get('jsn_addition'):
                                lst_accnt_map_id_ADDITION =   list(map(int, inst_json.get('jsn_addition').keys()))
                                dct_accnt_map_ADDITION = dict(AccountsMap.objects.filter(pk_bint_id__in = lst_accnt_map_id_ADDITION).values_list('pk_bint_id','vchr_category'))
                                dct_addition_data = {x[1]:y[1] for x in dct_accnt_map_ADDITION.items() for y in inst_json.get('jsn_addition').items() if str(x[0]) == str(y[0])}
                                total_addition = sum(map(float,dct_addition_data.values()))
                                dct_invoice['total_addition'] = total_addition
                                dct_invoice['dct_addition_data'] = dct_addition_data
                            if inst_json.get('jsn_deduction'):
                                lst_accnt_map_id_DEDUCTION  = list(map(int, inst_json.get('jsn_deduction').keys()))
                                dct_accnt_map_DEDUCTION = dict(AccountsMap.objects.filter(pk_bint_id__in = lst_accnt_map_id_DEDUCTION).values_list('pk_bint_id','vchr_category'))
                                dct_deduction_data = {x[1]:y[1] for x in dct_accnt_map_DEDUCTION.items() for y in inst_json.get('jsn_deduction').items() if str(x[0]) == str(y[0])}
                                total_deduction = sum(map(float,dct_deduction_data.values()))
                                dct_invoice['total_deduction'] = total_deduction
                                dct_invoice['dct_deduction_data'] = dct_deduction_data
                        dct_invoice['flt_add_ded_total'] = dct_invoice['total_addition']-dct_invoice['total_deduction']


                    dct_invoice['srn_no'] = ins_return_details.srn_no if rst_return.all() else ''
                    dct_invoice['srn_date'] = ins_return_details.srn_date if rst_return.all() else datetime.strftime(ins_invoice.invoice_date,'%d-%m-%Y')
                    ins_sales_master=SalesMaster.objects.filter(pk_bint_id=ins_return_details.return_invoice_id).first()
                    dct_invoice['dat_invoice_returned']=ins_sales_master.dat_invoice if ins_sales_master else datetime.strftime(ins_invoice.invoice_date,'%d-%m-%Y')
                    dct_invoice['invoice_num_returned'] = ins_sales_master.vchr_invoice_num if ins_sales_master else '' # ref doc no. credit note
                    dct_item['vchr_hsn_code'] = ins_invoice.vchr_hsn_code
                    if ins_invoice.item_tax:
                            dct_item['sgst'] = 0.0
                            dct_item['cgst'] = 0.0
                            dct_item['sgstp'] = 0.0
                            dct_item['cgstp'] = 0.0

                            dct_item['igst'] = 0.0
                            dct_item['kfcp'] = 0.0
                            dct_item['igst'] = 0.0
                            dct_item['igstp'] = 0.0
                            dct_item['kfc'] = 0.0

                            total_tax = 0

                            if ins_invoice.item_tax.get('dblKFC'):
                                dct_item['kfc'] = abs(round(ins_invoice.item_tax.get('dblKFC'),2))
                                dct_item['kfcp'] = abs(round(ins_invoice.item_tax.get('dblKFC%',0),2))

                            if ins_invoice.item_tax['dblSGST']:
                                total_tax += ins_invoice.item_tax['dblSGST']
                                flt_sgst = abs(round(((ins_invoice.item_tax['dblSGST'])/(int_item_amount-ins_invoice.item_discount))*100,2))
                                # flt_sgst = round(((ins_invoice.item_tax['dblSGST']/ins_invoice.qty)/(ins_invoice.item_amount-ins_invoice.item_discount))*100,1)
                                dct_item['sgstp'] = abs(ins_invoice.item_tax.get('dblSGST%',0))
                                dct_item['sgst'] = abs(round(ins_invoice.item_tax['dblSGST'],2))
                            if ins_invoice.item_tax['dblCGST']:
                                total_tax += ins_invoice.item_tax['dblCGST']
                                flt_cgst = abs(round(((ins_invoice.item_tax['dblCGST'])/(int_item_amount-ins_invoice.item_discount))*100,2))
                                # flt_cgst = round(((ins_invoice.item_tax['dblCGST']/ins_invoice.qty)/(ins_invoice.item_amount-ins_invoice.item_discount))*100,2)
                                dct_item['cgstp'] = abs(ins_invoice.item_tax.get('dblCGST%',0))
                                dct_item['cgst'] = abs(round(ins_invoice.item_tax['dblCGST'],2))

                            if ins_invoice.item_tax['dblIGST']:
                                total_tax += ins_invoice.item_tax['dblIGST']
                                flt_igst = abs(round(((ins_invoice.item_tax['dblIGST'])/(int_item_amount-ins_invoice.item_discount))*100,1))

                                dct_item['igstp'] = abs(ins_invoice.item_tax.get('dblIGST%',0))
                                dct_item['igst'] = abs(round(ins_invoice.item_tax['dblIGST'],2))
                            dbl_current_amount=dct_item['amount']
                            # dct_item['amount']=dbl_current_amount +dct_item['cgst']+dct_item['sgst']+dct_item['igst']+dct_item['discount']
                            # dct_invoice['return_amount'] +=dct_item['selling_price']-dct_item['buyback']
                            dct_invoice['return_amount'] +=dct_item['selling_price']
                            dct_invoice['return_amount'] = round(dct_invoice['return_amount'],2)
                    dct_invoice['lst_returned'].append(dct_item)
                    dct_invoice['company_gstin'] = ins_invoice.gstin

                    dct_invoice['state'] = ins_invoice.state
                    dct_invoice['state_code'] = ins_invoice.state_code


                else:
                    dct_invoice['lst_item'].append(dct_item)
                if ins_invoice.int_status==3:
                    bln_service_customer_print=True
                    dct_invoice['branch_location']=Branch.objects.filter(vchr_code=ins_invoice.branch_code).values('fk_location_master__vchr_location').first()['fk_location_master__vchr_location']
                    dct_invoice['serviced_item']=dct_item
                if ins_invoice.int_status==2:
                    bln_exchange_print=True



                if ins_invoice.int_status!=0 and ins_invoice.item_code.upper() == 'GDC00001':
                    rst_sales = SalesDetails.objects.filter(json_imei__contains=ins_invoice.json_imei).values('fk_item_id__vchr_name','fk_item__fk_product__vchr_name','fk_item__fk_brand__vchr_name','dbl_selling_price','dbl_mop').exclude(fk_item__vchr_name__iexact=ins_invoice.item).first()
                    dct_item['brand'] =  rst_sales['fk_item__fk_brand__vchr_name']
                    dct_item['model'] =  rst_sales['fk_item_id__vchr_name']
                    dct_item['product'] = rst_sales['fk_item__fk_product__vchr_name']
                    dct_item['item_selling_price'] = rst_sales['dbl_mop']
                    dct_item['selling_price'] = ins_invoice.selling_price
                    if ins_invoice.qty > 1:
                        dct_item['selling_price'] = (ins_invoice.selling_price)/ins_invoice.qty
                    dct_item['json_imei'] = ins_invoice.json_imei
                    dat_pro_start_date=ins_invoice.invoice_date
                    dat_pro_start=datetime.strftime(dat_pro_start_date,'%d-%m-%Y')
                    dct_item['dat_pro_start'] = dat_pro_start
                    year = relativedelta(years=+1)
                    dat_pro_date=ins_invoice.invoice_date+year
                    dat_pro_end=datetime.strftime(dat_pro_date,'%d-%m-%Y')
                    dct_item['dat_pro_end'] = dat_pro_end
                    str_invoice_no = ins_invoice.invoice_num
                    str_certf_no =str(str_invoice_no.replace('I','GDOT'))
                    dct_item['certf_no'] = str_certf_no
                    dct_item['item_type'] = 'gdot'
                    ins_type = Type.objects.filter(vchr_name='gdp')
                    rst_terms = Terms.objects.filter(int_status=0,fk_type=ins_type).values('jsn_terms')
                    dct_invoice['gdotterms'] = {}
                    if rst_terms:
                        dct_invoice['gdotterms'] = rst_terms[0]['jsn_terms']
                    dct_invoice['lst_insurance'].append(dct_item)
                if ins_invoice.int_status!=0 and ins_invoice.item_code.upper() == 'GDC00002':
                    rst_sales = SalesDetails.objects.filter(json_imei__contains=ins_invoice.json_imei).values('fk_item_id__vchr_name','fk_item__fk_product__vchr_name','fk_item__fk_brand__vchr_name','dbl_selling_price','dbl_mop').exclude(fk_item__vchr_name__iexact=ins_invoice.item).first()
                    dct_item['brand'] =  rst_sales['fk_item__fk_brand__vchr_name']
                    dct_item['model'] =  rst_sales['fk_item_id__vchr_name']
                    dct_item['product'] = rst_sales['fk_item__fk_product__vchr_name']
                    dct_item['selling_price'] = ins_invoice.selling_price
                    dct_item['item_selling_price'] = rst_sales['dbl_mop']
                    if ins_invoice.qty > 1:
                        dct_item['selling_price'] = (ins_invoice.selling_price)/ins_invoice.qty
                    dct_item['json_imei'] = ins_invoice.json_imei
                    dat_pro_start_date=ins_invoice.invoice_date
                    dat_pro_start=datetime.strftime(dat_pro_start_date,'%d-%m-%Y')
                    dct_item['dat_pro_start'] = dat_pro_start
                    year = relativedelta(years=+2)
                    dat_pro_date=ins_invoice.invoice_date+year
                    dat_pro_end=datetime.strftime(dat_pro_date,'%d-%m-%Y')
                    dct_item['dat_pro_end'] = dat_pro_end
                    str_invoice_no = ins_invoice.invoice_num
                    str_certf_no =str(str_invoice_no.replace('I','GDEW'))
                    dct_item['certf_no'] = str_certf_no
                    dct_item['item_type'] = 'gdew'
                    ins_type = Type.objects.filter(vchr_name='gdew')
                    rst_terms = Terms.objects.filter(int_status=0,fk_type=ins_type).values('jsn_terms')
                    dct_invoice['gdewterms'] = {}
                    if rst_terms:
                        dct_invoice['gdewterms'] = rst_terms[0]['jsn_terms']

                    dct_invoice['lst_insurance'].append(dct_item)
            dct_invoice['bln_dup'] = False
            if request.data.get('blnDuplicate'):
                dct_invoice['bln_dup'] = True
            ins_invoice=rst_invoice.first()
            dct_invoice['invoice_no'] = ins_invoice.invoice_num
            dct_invoice['vchr_irn_no'] = ins_invoice.vchr_irn_no
            dct_invoice['txt_qr_code'] = ins_invoice.txt_qr_code
            dct_invoice['staff'] = ins_invoice.staff
            dct_invoice['invoice_date'] = datetime.strftime(ins_invoice.invoice_date,'%d-%m-%Y')
            dct_invoice['invoice_time'] = datetime.strftime(ins_invoice.invoice_date,'%I:%M %p')
            dct_invoice['branch_mob'] = ins_invoice.branch_mob
            dct_invoice['branch_mail'] = ins_invoice.branch_mail

            dct_voucher['journal_num'] = ins_invoice.journal_num
            dct_voucher['invoice_date'] = datetime.strftime(ins_invoice.invoice_date,'%d-%m-%Y')
            dct_voucher['invoice_time'] = datetime.strftime(ins_invoice.invoice_date,'%I:%M %p')
            dct_voucher['branch_mob'] = ins_invoice.branch_mob
            dct_voucher['branch_mail'] = ins_invoice.branch_mail
            dct_invoice['branch_address'] = ins_invoice.branch_address
            dct_invoice['mygcare_no'] = ins_invoice.mygcare_no
            dct_voucher['branch_address'] = ins_invoice.branch_address
            dct_invoice['branch_GSTIN'] = '32AAAFZ4615J1Z8'
            dct_invoice['company_name'] = 'For 3G Mobile World'

            if ins_invoice.branch_code=='AGY':

                dct_invoice['branch_GSTIN'] = '32AAIFC7578H2Z7'
                dct_invoice['company_name'] = 'For Calicut Mobile LLP'
            dct_invoice['total_addition'] =0
            dct_invoice['total_deduction'] =0

            if ins_invoice.int_status!=0:

                dct_invoice['dct_addition_data'] = {}
                dct_invoice['dct_deduction_data'] = {}

                if ins_invoice.jsn_addition:
                    lst_accnt_map_id_ADDITION =   list(map(int, ins_invoice.jsn_addition.keys()))
                    dct_accnt_map_ADDITION = dict(AccountsMap.objects.filter(pk_bint_id__in = lst_accnt_map_id_ADDITION).values_list('pk_bint_id','vchr_category'))
                    dct_addition_data = {x[1]:y[1] for x in dct_accnt_map_ADDITION.items() for y in ins_invoice.jsn_addition.items() if str(x[0]) == str(y[0])}
                    total_addition = sum(map(float,dct_addition_data.values()))
                    dct_invoice['total_addition'] = total_addition
                    dct_invoice['dct_addition_data'] = dct_addition_data
                if ins_invoice.jsn_deduction:
                    lst_accnt_map_id_DEDUCTION  = list(map(int, ins_invoice.jsn_deduction.keys()))
                    dct_accnt_map_DEDUCTION = dict(AccountsMap.objects.filter(pk_bint_id__in = lst_accnt_map_id_DEDUCTION).values_list('pk_bint_id','vchr_category'))
                    dct_deduction_data = {x[1]:y[1] for x in dct_accnt_map_DEDUCTION.items() for y in ins_invoice.jsn_deduction.items() if str(x[0]) == str(y[0])}
                    total_deduction = sum(map(float,dct_deduction_data.values()))
                    dct_invoice['total_deduction'] = total_deduction
                    dct_invoice['dct_deduction_data'] = dct_deduction_data
                dct_invoice['flt_add_ded_total'] = dct_invoice['total_addition']-dct_invoice['total_deduction']

            ins_payment_fin=PaymentDetails.objects.filter(int_fop=0,fk_sales_master_id=vchr_invoice_num).values('vchr_name')
            if ins_payment_fin:
                ins_financier=Financiers.objects.filter(vchr_code=ins_payment_fin[0]['vchr_name']).values('vchr_name')
                dct_invoice['fin_name']=ins_financier[0]['vchr_name']
                if ins_finance_details.get('dbl_receved_amt'):
                    dct_invoice['dbl_down_payment'] = ins_finance_details.get('dbl_receved_amt')
            dct_invoice['cust_name'] = ins_invoice.cust_name
            dct_voucher['cust_name'] = ins_invoice.cust_name #credit note name to
            dct_invoice['cust_mobile'] = ins_invoice.cust_mobile
            dct_voucher['cust_mobile'] = ins_invoice.cust_mobile
            dct_invoice['cust_email'] = ins_invoice.cust_mail
            dct_invoice['cust_add'] = ins_invoice.cust_add
            dct_voucher['cust_add'] = ins_invoice.cust_add or '' # credit note name to under
            dct_invoice['cust_gst'] = ins_invoice.cust_gst

            dct_invoice['sh_cust_name'] = ins_invoice.cust_name
            dct_invoice['sh_cust_mobile'] = ins_invoice.cust_mobile
            dct_invoice['sh_cust_add'] = ins_invoice.cust_add
            dct_invoice['sh_cust_gst'] = ins_invoice.cust_gst
            dct_invoice['sh_landmark'] = "Not provided"

            if ins_invoice.sh_cust_name:
                dct_invoice['sh_cust_name'] = ins_invoice.sh_cust_name
                dct_invoice['sh_cust_mobile'] = ins_invoice.sh_mobile
                dct_invoice['sh_landmark'] = ins_invoice.sh_landmark
                dct_invoice['sh_cust_add'] = ins_invoice.sh_txt_add
                dct_invoice['sh_cust_gst'] = ins_invoice.sh_gst

            dct_invoice['discount'] = round(ins_invoice.total_discount,2) if ins_invoice.total_discount else 0.0
            dct_invoice['amount'] = ins_invoice.total_amount
            dct_invoice['buyback'] = round(ins_invoice.total_buy_back,2) if ins_invoice.total_buy_back else 0.0
            dct_invoice['return_amount_words']=p.number_to_words(round(dct_invoice['return_amount']+dct_invoice['flt_add_ded_total'])).title() +" Rupees" if dct_invoice['return_amount'] else 'Zero Rupees'
            dct_invoice['total_amount_words']=p.number_to_words(round(abs(dct_invoice['amount']))).title() +" Rupees" if dct_invoice['amount'] else 'Zero Rupees'

            if ins_invoice.coupon_amount:
                dct_invoice['coupon'] = round(ins_invoice.coupon_amount,2)
            # dct_invoice['loyalty'] = ins_invoice.sh_gst
            dct_invoice['total_tax'] = ins_invoice.total_tax
            if ins_invoice.total_loyalty:
                dct_invoice['loyalty'] = round(ins_invoice.total_loyalty,2)

            rst_terms = Terms.objects.filter(int_status=0,fk_type__vchr_name__in=['invoice-A','invoice-B','invoice-C']).values('fk_type__vchr_name','jsn_terms')
            dct_invoice['terms'] = {}
            if rst_terms:
                for ins_term in rst_terms:
                    dct_invoice['terms'][ins_term['fk_type__vchr_name']] = ins_term['jsn_terms']
            dct_voucher['total_amount_in_words']= p.number_to_words(round(dct_voucher['total_amount'])).title() +" Rupees Only"
            # data = print_invoice(dct_invoice,dct_voucher)
            
            dct_invoice['int_cust_type'] = rst_state[0]['fk_customer__fk_customer__int_cust_type']
            html_voucher = ""
            html_data = ""
            lst_html_insurance = "";
            html_returned = ""
            html_credit_note = ""
            html_service_customer = ""
            html_exchange = ""
            
            dct_invoice['lst_item']=sorted(dct_invoice['lst_item'], key = lambda i: i['int_status'],reverse=False)
            html_voucher = print_voucher(dct_invoice,dct_voucher)
            if dct_invoice['lst_insurance']:
                lst_html_insurance = print_insurance(dct_invoice,dct_voucher)
            if dct_invoice['lst_returned']:
                html_return_and_credit = print_return_and_credit_note(dct_invoice,dct_voucher)
                html_returned = html_return_and_credit[0]
                html_credit_note  = html_return_and_credit[1]
            if dct_invoice['lst_item']:
                html_data = print_invoices(dct_invoice,dct_voucher)
            if bln_service_customer_print==True:
                html_service_customer = print_service_customer(dct_invoice,dct_voucher)
            if bln_exchange_print ==True:
                html_exchange = print_exchange(int_invoice_id)
            file_path = settings.MEDIA_ROOT
            # str_base_path = settings.MEDIA_ROOT+'/schemes'
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            # ==================================================================================================

            options = {'margin-top': '10.00mm',
                       'margin-right': '10.00mm',
                       'margin-bottom': '10.00mm',
                       'margin-left': '10.00mm',
                       'dpi':400,
                       }

            lst_pdfs = []




            if html_voucher:
                str_file_name = dct_invoice['invoice_no']+'_voucher.pdf'
                filename_voucher =  file_path+'/'+str_file_name
                pdfkit.from_string(html_voucher,filename_voucher,options=options)
                lst_pdfs.append(filename_voucher)
            if html_data:
                str_file_name = dct_invoice['invoice_no']+'_invoice.pdf'
                filename_inovice =  file_path+'/'+str_file_name
                # if html_data2:
                #     html_data = html_data2
                pdfkit.from_string(html_data,filename_inovice,options=options)
                lst_pdfs.append(filename_inovice)
            if html_returned:
                str_file_name = dct_invoice['invoice_no']+'_sales_return.pdf'
                filename_return =  file_path+'/'+str_file_name
                pdfkit.from_string(html_returned,filename_return,options=options)
                lst_pdfs.append(filename_return)
            if html_credit_note:
                str_file_name = dct_invoice['invoice_no']+'_credit.pdf'
                filename_credit =  file_path+'/'+str_file_name
                pdfkit.from_string(html_credit_note,filename_credit,options=options)
                lst_pdfs.append(filename_credit)
            if lst_html_insurance:
                for ins_html_insurance in lst_html_insurance:
                    filename= dct_invoice['invoice_no']+"_insurance"+str(lst_html_insurance.index(ins_html_insurance))
                    str_file_name = filename+'.pdf'
                    filename_insurance =  file_path+'/'+str_file_name
                    pdfkit.from_string(ins_html_insurance,filename_insurance,options=options)
                    lst_pdfs.append(filename_insurance)
            if html_service_customer:
                str_file_name = dct_invoice['invoice_no']+'_service_customer.pdf'
                filename_service_customer =  file_path+'/'+str_file_name
                pdfkit.from_string(html_service_customer,filename_service_customer,options=options)
                lst_pdfs.append(filename_service_customer)
            if html_exchange:
                str_file_name = dct_invoice['invoice_no']+'_exchange.pdf'
                filename_exchange =  file_path+'/'+str_file_name
                pdfkit.from_string(html_exchange,filename_exchange,options=options)
                lst_pdfs.append(filename_exchange)
            # To merge all pdf to one
            pdf_writer = PdfFileWriter()
            for path in lst_pdfs:
                pdf_reader = PdfFileReader(path)
                for page in range(pdf_reader.getNumPages()):
                    pdf_writer.addPage(pdf_reader.getPage(page))

            str_file_name = 'Invoice-'+str(datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f'))+'.pdf'
            filename =  file_path+'/'+str_file_name
            with open(filename, 'wb') as fh:
                pdf_writer.write(fh)

            fs = FileSystemStorage()
            # lst_file =[filename]
            # lst_encoded_string=[]
            encoded_string = ''
            # for filename in lst_file:
            if fs.exists(filename):
                with fs.open(filename) as pdf:
                    encoded_string=str(base64.b64encode(pdf.read()))
                    # lst_encoded_string.append(str(base64.b64encode(pdf.read())))
            file_details = {}
            file_details['file'] = encoded_string
            file_details['file_name'] = str_file_name
            data=file_details
            str_request_protocol = request.META.get('HTTP_REFERER').split(':')[0]
            session.close()
            return Response({"status":1,'file':data['file'],'file_name':data['file_name'],'file_url':str_request_protocol+'://'+request.META['HTTP_HOST']+'/media/'+data['file_name']})


        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

def print_voucher(dct_invoice,dct_voucher):
    try:
        str_mygcare_num = dct_invoice['mygcare_no'] if  dct_invoice['mygcare_no'] else ''
        
        str_style = """   	<style>

            		table#voucher {
            				  border-collapse: collapse;
            				  border-spacing: 0;
            				  width: 100%;
            			  }

            	  #voucher th,#voucher td {
            				  padding: 8px;
            		     }
                   body{
                                                        background: url(/home/sudheesh/Desktop/V0.1.8.5/TBS/static_root/media/duplicate.png);
                                                        background-size: contain;
                                                        background-repeat: no-repeat;font-family:Segoe, "Segoe UI", "DejaVu Sans", "Trebuchet MS", Verdana, "sans-serif";
                                    		          }
                                    		        h6{
                                    			        font-size: 0.85em;
                                    					padding-left: 10px;
                                    		          }
                                    		        p{
                                    			        font-size:17px;
                                    					word-spacing: 2px;
                                    					padding-left: 10px;
                                    					padding-right: 10px;
                                    		         }
                                    		.container{
                                    			         width:1170px;
                                    			         margin:auto;
                                    		          }
                                    		    .clear{
                                    			         clear:both;
                                    			      }
                                    		 .imagebox{
                                    			         width:100%;
                                    			         float: left;
                                    			         border-bottom: 1px solid #c7c2c2;
                                    			         padding-bottom: 12px;margin-top: 20px;
                                    		          }
                                    		    .ibox1{
                                    				    width: 25%;
                                    				    float: left;

                                    		          }
                                    		    .ibox2{
                                    				    width: 50%;
                                    				    float: left;
                                    		          }
                                    		 .ibox2 h6{
                                    			       margin-bottom: 0;
                                                       margin-top: 10px;
                                    			       padding-left: 0 !important;
                                    		          }

                                              .ibox2 p{
                                    			       margin-bottom: 0;
                                                       margin-top: 5px;
                                    			       padding-right: 0;
                                                       padding-left: 0;
                                		              }
                                    		    .ibox3{
                                    				    width: 25%;
                                    				    float: left;
                                    		          }
                                    		     .box1{
                                    			        width:100%;
                                    			        float: left;
                                    				    padding-bottom: 16px;

                                    		          }
                                    		 .section1{
                                    			        width:64%;
                                    			        float: left;
                                    		          }
                                          .section1 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;
                                    		          }
                                           .section1 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;
                                    		          }
                                    		 .section2{
                                    			        width:32%;
                                    			        float: right;
                                    			        text-align: right;
                                    		          }
                                    	  .section2 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;
                                    		          }
                                           .section2 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;
                                    		          }
                                    		 .section3{
                                    					width:50%;
                                    					float: left;

                                    		          }
                                          .section3 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;
                                    		          }
                                    	   .section3 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;

                                    		          }
                                    		 .section4{
                                    			        width:50%;
                                    					float: right;
                                    		          }
                                          .section4 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;

                                    		          }
                                    	   .section4 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;
                                    		          }
                                                      table{
                                                      border-collapse:collapse;
                                                      }
                                    		        th{
                                    			        font-weight: 400;
                                    		          }
                                               th, td {
                                                        padding: 15px;
                                    			        text-align: center;
                                                      }
                                    		 .section5{
                                    			        width:40%;
                                    					float: right;
                                    			        text-align: right;
                                    		          }
                                    	  .section5 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;
                                    		            padding-left: 0px !important;
                                    		            font-size: 16px;
                                    		          }
                                    	   .section5 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;
                                    		          }
                                    		     .box2{
                                    			        width:100%;
                                    			        float: left;

                                    		          }
                                    		    @page {
                                    				   size: 7in 9.25in;
                                    				   margin: 27mm 16mm 27mm 16mm;
                                                      }
                                    		        li{
                                    			       font-size:17px;
                                    		         }
                                    		  .header{
                                    					width:100%;
                                    					float: left;
                                                        text-align:center;
                                    					# color:  #e06a2b;

                                    		          }

                                    		  .invoice{

                                    					background-color: #e06a2b;
                                    					color: white;
                                    					padding: 15px 10px 15px 10px;

                                    		         }
                                    		.innerbox{
                                    					background: white;
                                    					width: 100%;
                                    				}

          	</style>
            """


        html_voucher = ""
        if dct_voucher and dct_voucher['total_amount']:
            html_voucher = """<!doctype html>
            <html>
            <head>
            <meta charset="utf-8">
            <title>Untitled Document</title>
            	<style>

            	.container{
            			         width:1170px;
            			         margin:auto;

            		      }
            	    .clear{
            			        clear:both;
            			  }
            		#voucher .table{
            				  width: 100%;
                              border:none;
                                    }

            	  #voucher th,#voucher td {
            				  padding: 8px;
            		     }
            	</style>"""+str_style+"""
            </head>

            <body>
            	<div class="container">
            		<div class="imagebox">

            		       <div class="ibox1">
            				   <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
            			   </div>
            			   <div class="ibox2">

                            <div style="width:100%;float:left;">

        						<p><span style="font-weight: 600;">ADDRESS  : </span>
        						"""+str(dct_invoice['branch_address'])+ """</p>

        					 </div>

            				   <div style="width:50%;float:left;">

            					   <div style="width:15%;float:left">
            					   <p><span style="font-weight: 600;">PH : </span></p>
            					   </div>
            					   <div style="width:83%;float: right">
            						<p>"""+str(dct_voucher['branch_mob'])+"""</p>
            					   </div>

        				      </div>
            				     <div style="width:50%;float:right;">

            						 <div style="width:30%;float:left">
            					   <p><span style="font-weight: 600;">Branch : </span></p>
            					   </div>
            					   <div style="width:70%;float: right">
            						<p>   """
            if dct_voucher['branch_mob']:
                html_voucher+=str(dct_voucher['branch_mob'])
            else:
                html_voucher+="**********"
            html_voucher+="""</p>
            					   </div>
        					</div>
                        <div style="width:50%;float:left;">
        					   <div style="width:45%;float:left">
        					  <p><span style="font-weight: 600;">MYG CARE :</span></p>
        					   </div>
        					   <div style="width:54%;float: right">
        						<p>"""+str(str(str_mygcare_num))+"""</p>
        					   </div>

        				   </div>
            				     <div style="width:50%;float:right;">
            						<div style="width:35%;float:left">
            					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
            					   </div>
            					   <div style="width:65%;float: right">
            						<p>"""+str(dct_voucher['branch_mail'])+"""</p>
            					   </div>
        						 </div>
            				   <div style="width:100%;float:left;">
        					    <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
        				   </div>

            			 </div>
            			   <div class="ibox3" style="text-align: right;">
            				   <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
            				   <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
            				   <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
            			   </div>

            		</div>
                   <br><br><br><br><br><br><br><br><br><br><br><br>
            		<h4 colspan="3" style="text-align: center;font-size: 20px;text-decoration: underline;color: green;margin-top:10px;">Journal Voucher</h4>
            		<div class="clear"></div>
                    <div id="voucher">
            		    <table border="0" style="width:100%;border:0px !important;border-spacing: 0 !important;">

            					<tbody>
            						    <tr>
            								<td style="text-align:left;">To,</td>
            								<td style="text-align: right;">JV No :</td>
            								<td style="text-align: right;width: 150px;">"""+str(dct_voucher['journal_num'])+"""</td>
            						    </tr>
            						    <tr>

            							    <td style="padding-left: 44px;text-align:left;font-weight:600">"""+str(dct_voucher['cust_name'])+"""</td>
            								<td style="text-align: right;">JV Date :</td>
            								<td style="text-align: right;width: 110px;">"""+str(dct_voucher['invoice_date'])+"""</td>
            						    </tr>"""
            if dct_voucher['cust_add']:
                html_voucher+="""<tr>
                                         <td colspan="3" style="text-align:left;padding: 3px 3px 3px 44px  !important;"><span style="font-weight: 600;">Address:</span>"""+dct_voucher['cust_add']+""" ,</td>
                                        </tr>"""
            html_voucher+="""<tr>
                                          <td colspan="3" style="text-align:left;padding:3px 3px 10px 44px  !important;"><span style="font-weight: 600;">Phone:</span>&nbsp;"""+str(dct_voucher['cust_mobile'])+"""</td>
                                        </tr>

            						    <tr style="border-top: 1px solid #e2e2e2;border-bottom: 1px solid #e2e2e2;margin-top:10px;">
            								<th colspan="2" style="text-align: left;font-weight:600">Particulars</th>
            								<th style="text-align: right;font-weight:600">Amount</th>
            						    </tr>"""
            for voucher_data in dct_voucher['lst_item']:
                html_voucher +="""<tr>
            								 <td colspan="2" style="text-align:left;">"""+voucher_data['item_name']+"""</td>
            								 <td style="text-align: right">"""+str("{0:.2f}".format(round(voucher_data['amount'],2)))+"""</td>
            					</tr>"""
            html_voucher +="""</tbody>

            				 <tfoot>

            					       <tr style="background-color: whitesmoke;">
            							    <td></td>
            							    <td style="text-align: right;font-weight: 600;">Total : </td>
            							    <td style="text-align: right;font-weight: 600;">"""+str("{0:.2f}".format(round(dct_voucher['total_amount'],2)))+"""</td>
            					       </tr>
            				 </tfoot>
            		     </table>
                         <div>
            		    <div class="clear"></div>
            		    <p>"""+dct_voucher['total_amount_in_words']+"""/-</p>
            		    <div style="width: 25%;float:left;">
            				 <p style="font-weight: 600;">Entered By</p>
            		    </div>
            		    <div style="width: 25%;float:left;">
            				 <p style="font-weight: 600;">Verified By</p>
            		    </div>
            		    <div style="width: 25%;float:left;text-align: right;">
            				 <p style="font-weight: 600;">Approved By</p>
            		    </div>
            		    <div style="width: 25%;float:left;text-align: right;">
            				 <p style="font-weight: 600;">Recieved By</p>
            		    </div>
            	</div>

            </body>
            </html>

            """
        return html_voucher
    except Exception as e:
        raise



def print_insurance(dct_invoice,dct_voucher):
    try:
        lst_html_insurance=[]
        str_mygcare_num = dct_invoice['mygcare_no'] if  dct_invoice['mygcare_no'] else ''
        for ins_insurance in dct_invoice['lst_insurance']:
            terms='gdewterms'
            for i in range(ins_insurance['qty']):

                html_insurance = '''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Untitled Document</title>
<style>
    .container{
                 width:1170px;
                 margin:auto;
              }
        .clear{
                 clear: both;
              }
             p{
                margin-top: 6px;
                margin-bottom: 6px;
              }

           ul {
                list-style: none;
                padding-left: 17px;
              }

ul li::before {
                  content: "■";
                  color: #ffa56e;
                  font-weight: bold;
                  display: inline-block;
                  width: 1em;
                  margin-left: -1em;
            }
       ul li{
                 margin: 5px 0px 5px 0px;
            }
         ol {

                padding-left: 17px;
            }

       ol li{
                 margin: 5px 0px 5px 0px;

            }


</style>
</head>

<body>
<div class="container">
<!--Image section-->
    <div style="width: 33%;float: left">
            <div style="width: 27%;float: left;">
                <img src="'''+settings.MEDIA_ROOT+'''/3g.png" width="100px">
            </div>
            <div style="width: 63%">
                <img src="'''+settings.MEDIA_ROOT+'''/0.jpg" width="25%">
                <img src="'''+settings.MEDIA_ROOT+'''/brandlogo.jpg" width="40%">
            </div>
    </div>
    <div style="width: 33%;float: left;text-align: center;">
        <img src="'''+settings.MEDIA_ROOT+'''/gdot.png" width="55%">
    </div>
    <div style="width: 33%;float: right;text-align: right;">
        <img src="'''+settings.MEDIA_ROOT+'''/myglogo.jpg" width="25%">
    </div>
    <div class="clear"></div>
<!--Image section ends-->'''

                if ins_insurance['item_type'] == 'gdot':
                    html_insurance+='''
    <h4 align="center" style="color: green;"><span style="border-bottom: 2px solid orange;">GD</span>OT PROTECTION PLUS CERTIFICATE</h4>'''
                else:
                    html_insurance+='''
    <h4 align="center" style="color: green;"><span style="border-bottom: 2px solid orange;">GD</span>OT EXTENDED WARRANTY CERTIFICATE</h4>'''
                html_insurance+='''
<!--section1 starts-->
    <div style="width: 50%;float: left">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Name Of Customer</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: '''+dct_invoice['cust_name'].title()+'''</p>
        </div>
    </div>
    <div style="width: 50%;float: right">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Certificate No</p>
        </div>'''
                if ins_insurance['item_type'] == 'gdot':
                    terms='gdotterms'
                    html_insurance+='''
        <div style="width: 70%;float: left">
            <p>: '''+ins_insurance['certf_no']+'-'+str(dct_invoice['lst_insurance'].index(ins_insurance)+1)+'-'+(str(i+1))+'''</p>
        </div>
    </div>'''
                else:
                    html_insurance+='''
                    <div style="width: 70%;float: left">
            <p>: '''+ins_insurance['certf_no']+'-'+str(dct_invoice['lst_insurance'].index(ins_insurance)+1)+'-'+(str(i+1))+'''</p>
        </div>
    </div>'''
                html_insurance+='''
    <div class="clear"></div>


    <div class="clear"></div>

    <div style="width: 50%;float: left">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Contact Number</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: '''+str(dct_invoice['cust_mobile'])+'''</p>
        </div>
    </div>
    <div style="width: 50%;float: right">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Email</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: '''+str(dct_invoice['cust_email'] or '')+'''</p>
        </div>
    </div>
    <div class="clear"></div>

    <div style="width: 50%;float: left">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Product Category</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: '''+str(ins_insurance['product'])+'''</p>
        </div>
    </div>
    <div style="width: 50%;float: right">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Model</p>
        </div>
        <div style="width: 70%;float: left">
            <p>:  '''+str(ins_insurance['model'])+'''</p>
        </div>
    </div>
    <div class="clear"></div>

    <div style="width: 50%;float: left">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Product Brand</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: '''+str(ins_insurance['brand'])+'''</p>
        </div>
    </div>
    <div style="width: 50%;float: right">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">GDP Plus Pack</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: <span>&#x20b9; </span>'''+str(ins_insurance['selling_price'] +ins_insurance['discount'])+'''</p>
        </div>
    </div>
    <div class="clear"></div>

    <div style="width: 50%;float: left">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Protection Start Date</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: '''+str(ins_insurance['dat_pro_start'])+'''</p>
        </div>
    </div>
    <div style="width: 50%;float: right">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Protection End Date</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: '''+str(ins_insurance['dat_pro_end'])+'''</p>
        </div>
    </div>
    <div class="clear"></div>


    <div style="width: 50%;float: left">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Serial/IMEI No</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: '''+ins_insurance['json_imei'][i]+''' </p>
        </div>
    </div>
    <div style="width: 50%;float: right">
        <div style="width: 30%;float: left">
            <p style="font-weight:600">Invoice No</p>
        </div>
        <div style="width: 70%;float: left">
            <p>: '''+dct_invoice['invoice_no']+'''</p>
        </div>
    </div>
    <div class="clear"></div>

    <div style="width: 100%;float: left">
        <div style="width: 15%;float: left">
            <p style="font-weight:600">Product Value</p>
        </div>
        <div style="width: 85%;float: left">
            <p>: <span>&#x20b9; </span>'''+str(ins_insurance['item_selling_price'])+'''</p>
        </div>
    </div>
    <div class="clear"></div>
      <div style="width: 100%;float: left">
        <div style="width: 15%;float: left">
            <p style="font-weight:600">Address</p>
        </div>
        <div style="width: 85%;float: left">
            <p>: '''+str(dct_invoice['cust_add'])+'''</p>
        </div>
    </div>
    <div class="clear"></div>
<!--section1 ends-->'''
#                     if ins_insurance['item_type'] == 'gdot':
#                         html_insurance+='''
#
# <!--section2 Begins-->
# 		<div style="margin-top: 30px">
# 			<p style="font-weight: 600;color: #118b98;"><span style="border-bottom: 2px solid #118b98;">Sa</span>lient features of the GDOT Protection Plus</p>
# 			<p style="color:gray">Loss or damage to handset resulted due to </p>
# 			<div style="width:50%;float:left;">
# 				<ol style="padding-left: 15px;">
# 				  <li>Accidental physical damage</li>
# 				  <li>Burglary and house breaking</li>
# 				  <li>Act of god perils</li>
# 				</ol>
# 			</div>
# 			<div style="width:50%;float:right;">
# 				<ol start="4">
# 				  <li>Accidental entry of water/fluid</li>
# 				  <li>Stolen from locked building/room/vehicle by violent or forcible entry</li>
# 				  <li>Theft following use of violence</li>
# 				</ol>
# 			</div>
# 		</div>
#
#
#
# <!--section2 ends-->'''
                html_insurance+='''

<!--section3 starts-->
    <div style="margin-top: 20px">
        <p style="font-weight: 600;color: #118b98;"><span style="border-bottom: 2px solid #118b98;">Te</span>rms & Condition</p>
        <ul>'''
                
                for index in range(1,len(dct_invoice[terms])+1):
                    html_insurance+='''<li>'''+dct_invoice[terms][str(index)]+'''</li>'''
                    html_insurance+='''<br>'''
                html_insurance +='''</ul>'''

                if ins_insurance['item_type'] == 'gdot':
                    html_insurance+='''<div class="clear"></div>
                            <div class="table-responsive print">
                                           <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
                                                    <caption>ANNEXURE 1</caption>
                                                  <tr style="background-color: #e06a2b;color: white;">
                                                        <td style="border: 1px solid #cecdcd;text-align:center;">Period in days (ദിവസങ്ങളില്‍)</td><td style="border: 1px solid #cecdcd;text-align:center;">Depreciation(തേയ്മാനം)</td>
                                            </tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">0-90</td><td style="text-align:center;border: 1px solid #cecdcd;">15%</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">91-180</td><td style="text-align:center;border: 1px solid #cecdcd;">35%</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">181-270</td><td style="text-align:center;border: 1px solid #cecdcd;">50%</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">271-365</td><td style="text-align:center;border: 1px solid #cecdcd;">60%</td></tr>

                                </table>
                                <br>
                                <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
                                       <caption>ANNEXURE 2</caption>
                                       <tr style="background-color: #e06a2b;color: white;">
                                             <td style="border: 1px solid #cecdcd;">GDP PLUS പരിരക്ഷയുള്ളവ</td>
                                 </tr>
                                 <tr><td style="text-align:left;border: 1px solid #cecdcd;">ആകസ്മികമായി ഉണ്ടാകുന്ന ഫിസിക്കല്‍/ലിക്വിഡ് ഡാമേജുകള്‍ ഉദാ: വാഹനാപകടത്തില്‍ സംഭവിക്കുന്നവ,ആക്രമിക്കപ്പെടുന്നതിലൂടെ സംഭവിക്കുന്നവ</td></tr>
                                 <tr><td style="text-align:left;border: 1px solid #cecdcd;">തീ, ഇടിമിന്നല്‍, പ്രകൃതിക്ഷോഭം കാരണമുണ്ടാകുന്ന ഡാമേജ്(മതിയായ ഗവ: രേഖകള്‍ സഹിതം).</td></tr>
                                 <tr><td style="text-align:left;border: 1px solid #cecdcd;">ലോക്ക് ചെയ്യപെട്ട റൂമില്‍ നിന്നു ,വാഹനത്തില്‍ നിന്നുണ്ടാകുന്ന മോഷണം.</td></tr>
                                 <tr><td style="text-align:left;border: 1px solid #cecdcd;">പിടിച്ചുപറി,കൊള്ള കാരണമുള്ള ഡാമേജ്/നഷ്ടപെടല്</td></tr>

                                 </table>

                                 <br>
                                 <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
                                        <tr style="background-color: #e06a2b;color: white;">
                                              <td style="border: 1px solid #cecdcd;">GDP PLUS പരിരക്ഷയില്ലാത്തവ</td>
                                  </tr>
                                  <tr><td style="text-align:left;border: 1px solid #cecdcd;">ഏതെങ്കിലും തരത്തിലുള്ള പോക്കറ്റടി.</td></tr>
                                  <tr><td style="text-align:left;border: 1px solid #cecdcd;">ഉപഭോക്താവിന്റെ അശ്രദ്ധ കാരണത്താലുണ്ടാകുന്ന മോഷണം/ഡാമേജ് (ഉദാ:ബസ്സില്‍ വച്ച് ഉറങ്ങുന്ന സമയത്തു ഉണ്ടാകുന്ന മോഷണം).</td></tr>
                                  <tr><td style="text-align:left;border: 1px solid #cecdcd;">ഉപയോഗം മൂലമുണ്ടാകുന്ന തേയ്മാനം.</td></tr>
                                  <tr><td style="text-align:left;border: 1px solid #cecdcd;">പോറലുകള്‍, ചതവുകള്‍, നിറം മങ്ങല്‍ മുതലായ ഭംഗിപരമായ കേടുപാടുകള്‍(പ്രൊഡക്ടിന്റെ മെയിന്‍ ഫങ്ഷനുകളെ ബാധിക്കാത്ത കേടുപാടുകള്‍ ഉദാ:പ്രൊഡക്ടിന്റെ കെയ്‌സ് പൊട്ടുക പക്ഷെ ഫങ്ഷനുകള്‍ക് ബുദ്ധിമുട്ടാവാത്ത അവസ്ഥ).</td></tr>
                                  <tr><td style="text-align:left;border: 1px solid #cecdcd;">മനപ്പൂര്‍വം ഉണ്ടാക്കിയതായ ഫിസിക്കല്‍/ലിക്വിഡ് ഡാമേജുകള്‍.</td></tr>
                                  <tr><td style="text-align:left;border: 1px solid #cecdcd;">മെയിന്‍ പ്രൊഡക്ടിന്റെ കൂടെ വരുന്ന ഒരു തരത്തിലുള്ള ആക്‌സസറീസിനും. ഉദാ: ബാറ്ററി, സിം,ഹെഡ്‌സെറ്റ്,പൗച്, അഡാപ്റ്റര്‍, ചാര്‍ജര്‍,മെമ്മറി കാര്‍ഡ്,സ്‌റ്റൈലസ് etc..</td></tr>
                                  <tr><td style="text-align:left;border: 1px solid #cecdcd;">അംഗീകൃത സര്‍വിസ് സെന്ററില്‍ നിന്നല്ലാതെ റിപ്പയര്‍ ചെയ്യപ്പെട്ട പ്രൊഡക്ടുകള്‍ക്.</td></tr>
                                  <tr><td style="text-align:left;border: 1px solid #cecdcd;">സോഫ്ട് വെയര്‍ തകരാറുകള്‍,ഏതെങ്കിലും തരത്തിലുള്ള ഡാറ്റ നഷ്ടപെടല്‍,തേര്‍ഡ് പാര്‍ട്ടി ആപ്പുകള്‍ കാരണമുണ്ടാകുന്ന തകരാറുകള്‍.</td></tr>
                                  <tr><td style="text-align:left;border: 1px solid #cecdcd;">സോഫ്ട് വെയര്‍ തകരാറുകള്‍,ഏതെങ്കിലും തരത്തിലുള്ള ഡാറ്റ നഷ്ടപെടല്‍,തേര്‍ഡ് പാര്‍ട്ടി ആപ്പുകള്‍ കാരണമുണ്ടാകുന്ന തകരാറുകള്‍.</td></tr>

                                  </table>
                            </div>
                    <div class="clear"></div>'''
                elif ins_insurance['item_type'] == 'gdew':
                    html_insurance+='''<div class="clear"></div>
                            <div class="table-responsive print">
                                           <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
                                                  <caption>ANNEXURE 1</caption>
                                                  <tr style="background-color: #e06a2b;color: white;">
                                                        <th style="border: 1px solid #cecdcd;"></th>
                                                        <th style="border: 1px solid #cecdcd;">MOBILE</th>
                                                        <th style="border: 1px solid #cecdcd;">CAMERA</th>
                                                        <th style="border: 1px solid #cecdcd;">LAPTOP</th>
                                                        <th style="border: 1px solid #cecdcd;">TAB</th>
                                            </tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">SOFTWARE (OS)</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">DISPLAY</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">PCB</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">CAMERA</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">CAMERA LENS</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">COSMETIC</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">LIQUID DAMAGE</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">ALL TYPE OF PHYSICAL DAMAGE</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td></tr>
                                            <tr><td style="text-align:center;border: 1px solid #cecdcd;">THEFT</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td></tr>

                                </table>
                                <br>

                                <div class="clear"></div>
                                        <div class="table-responsive print">
                                                       <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
                                                              <caption>ANNEXURE 1</caption>
                                                              <tr style="background-color: #e06a2b;color: white;">
                                                                    <th style="border: 1px solid #cecdcd;">PRODUCT PRICE</th>
                                                                    <th style="border: 1px solid #cecdcd;">PACKAGE</th>
                                                                    <th style="border: 1px solid #cecdcd;">GDEW</th>
                                                                    <th style="border: 1px solid #cecdcd;">1st Claim</th>
                                                        </tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">0-2000</td><td style="text-align:center;border: 1px solid #cecdcd;">199</td><td style="text-align:center;border: 1px solid #cecdcd;">199</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">2001-4000</td><td style="text-align:center;border: 1px solid #cecdcd;">299</td><td style="text-align:center;border: 1px solid #cecdcd;">299</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">4001-10000</td><td style="text-align:center;border: 1px solid #cecdcd;">599</td><td style="text-align:center;border: 1px solid #cecdcd;">599</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">10001-15000</td><td style="text-align:center;border: 1px solid #cecdcd;">899</td><td style="text-align:center;border: 1px solid #cecdcd;">899</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">15001-20000</td><td style="text-align:center;border: 1px solid #cecdcd;">1199</td><td style="text-align:center;border: 1px solid #cecdcd;">1199</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">20001-25000</td><td style="text-align:center;border: 1px solid #cecdcd;">1499</td><td style="text-align:center;border: 1px solid #cecdcd;">1499</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">25001-30000</td><td style="text-align:center;border: 1px solid #cecdcd;">1999</td><td style="text-align:center;border: 1px solid #cecdcd;">1499</td><td style="text-align:center;border: 1px solid #cecdcd;">500</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">30001-40000</td><td style="text-align:center;border: 1px solid #cecdcd;">2399</td><td style="text-align:center;border: 1px solid #cecdcd;">1899</td><td style="text-align:center;border: 1px solid #cecdcd;">500</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">40001-50000</td><td style="text-align:center;border: 1px solid #cecdcd;">2999</td><td style="text-align:center;border: 1px solid #cecdcd;">2499</td><td style="text-align:center;border: 1px solid #cecdcd;">500</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">50001-60000</td><td style="text-align:center;border: 1px solid #cecdcd;">3599</td><td style="text-align:center;border: 1px solid #cecdcd;">2599</td><td style="text-align:center;border: 1px solid #cecdcd;">1000</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">60001-70000</td><td style="text-align:center;border: 1px solid #cecdcd;">4199</td><td style="text-align:center;border: 1px solid #cecdcd;">2999</td><td style="text-align:center;border: 1px solid #cecdcd;">1200</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">70001-80000</td><td style="text-align:center;border: 1px solid #cecdcd;">4799</td><td style="text-align:center;border: 1px solid #cecdcd;">2999</td><td style="text-align:center;border: 1px solid #cecdcd;">1800</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">80001-90000</td><td style="text-align:center;border: 1px solid #cecdcd;">5399</td><td style="text-align:center;border: 1px solid #cecdcd;">2999</td><td style="text-align:center;border: 1px solid #cecdcd;">2000</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">90001-100000</td><td style="text-align:center;border: 1px solid #cecdcd;">5999</td><td style="text-align:center;border: 1px solid #cecdcd;">3999</td><td style="text-align:center;border: 1px solid #cecdcd;">2400</td></tr>
                                                        <tr><td style="text-align:center;border: 1px solid #cecdcd;">100001-110000</td><td style="text-align:center;border: 1px solid #cecdcd;">6599</td><td style="text-align:center;border: 1px solid #cecdcd;">3999</td><td style="text-align:center;border: 1px solid #cecdcd;">2600</td></tr>

                                </table>'''
        #     html_insurance+='''
        # # # <p style="font-weight: 600;margin-top: 25px;color: #118b98;"><span style="border-bottom: 2px solid #118b98;">Ca</span>ses in which GDP PLUS protection available:</p>
        # # # <ul>
        # # #     <li>Accidental/Liquid damages Eg: (Incidents in vehicle or in case of physical attack )</li>
        # # # 	<li>Damages due to Fire, lightning, Natural Calamities (Subject to submission of proper documents) </li>
        # # # 	<li>Theft from locked house, room and vehicle</li>
        # # # 	<li>Damage/loss due to forceful robbery and burglary.</li>
        # # # </ul>
        # # #
        # # # <p style="font-weight: 600;margin-top: 25px;color: #118b98;"><span style="border-bottom: 2px solid #118b98;">Ca</span>ses in which GDP PLUS protection not available:</p>
        # # # <ul>
        # # #     <li>Any type of pick pocketing</li>
        # # # 	<li>Loss due to the carelessness and negligence from the part of the customer ( Eg: lost while sleeping in the vehicle)  </li>
        # # # 	<li>Depreciation due the usage</li>
        # # # 	<li>Damages which is not affecting the main functioning of the product ,like abrasions ,fading of the color </li>
        # # # 	<li>Damages created by deliberate intention by the customer or any one else</li>
        # # # 	<li>Accessories attached to the main product like ,Battery, Head set, pouch, Adapter ,charger Memory Card, Etc</li>
        # # # 	<li>Product repaired from unauthorized service centers</li>
        # # # 	<li>Any kind of software problem, Data ,loss or damage due to the use of any third party apps</li>
        # # # 	<li>in which the Manufacturers is not given warranty.</li>
        # # </ul>
                html_insurance+='''</div>
<!--section3 ends-->

</div>
</body>
</html>'''

                
                lst_html_insurance.append(html_insurance)
        return lst_html_insurance
    except Exception as e:
        raise



def print_return_and_credit_note(dct_invoice,dct_voucher):
    try:
        str_style = """   	<style>

            		table#voucher {
            				  border-collapse: collapse;
            				  border-spacing: 0;
            				  width: 100%;
            			  }

            	  #voucher th,#voucher td {
            				  padding: 8px;
            		     }
                   body{
                                                        background: url(/home/sudheesh/Desktop/V0.1.8.5/TBS/static_root/media/duplicate.png);
                                                        background-size: contain;
                                                        background-repeat: no-repeat;font-family:Segoe, "Segoe UI", "DejaVu Sans", "Trebuchet MS", Verdana, "sans-serif";
                                    		          }
                                    		        h6{
                                    			        font-size: 0.85em;
                                    					padding-left: 10px;
                                    		          }
                                    		        p{
                                    			        font-size:17px;
                                    					word-spacing: 2px;
                                    					padding-left: 10px;
                                    					padding-right: 10px;
                                    		         }
                                    		.container{
                                    			         width:1170px;
                                    			         margin:auto;
                                    		          }
                                    		    .clear{
                                    			         clear:both;
                                    			      }
                                    		 .imagebox{
                                    			         width:100%;
                                    			         float: left;
                                    			         border-bottom: 1px solid #c7c2c2;
                                    			         padding-bottom: 12px;margin-top: 20px;
                                    		          }
                                    		    .ibox1{
                                    				    width: 25%;
                                    				    float: left;

                                    		          }
                                    		    .ibox2{
                                    				    width: 50%;
                                    				    float: left;
                                    		          }
                                    		 .ibox2 h6{
                                    			       margin-bottom: 0;
                                                       margin-top: 10px;
                                    			       padding-left: 0 !important;
                                    		          }

                                              .ibox2 p{
                                    			       margin-bottom: 0;
                                                       margin-top: 5px;
                                    			       padding-right: 0;
                                                       padding-left: 0;
                                		              }
                                    		    .ibox3{
                                    				    width: 25%;
                                    				    float: left;
                                    		          }
                                    		     .box1{
                                    			        width:100%;
                                    			        float: left;
                                    				    padding-bottom: 16px;

                                    		          }
                                    		 .section1{
                                    			        width:64%;
                                    			        float: left;
                                    		          }
                                          .section1 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;
                                    		          }
                                           .section1 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;
                                    		          }
                                    		 .section2{
                                    			        width:32%;
                                    			        float: right;
                                    			        text-align: right;
                                    		          }
                                    	  .section2 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;
                                    		          }
                                           .section2 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;
                                    		          }
                                    		 .section3{
                                    					width:50%;
                                    					float: left;

                                    		          }
                                          .section3 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;
                                    		          }
                                    	   .section3 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;

                                    		          }
                                    		 .section4{
                                    			        width:50%;
                                    					float: right;
                                    		          }
                                          .section4 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;

                                    		          }
                                    	   .section4 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;
                                    		          }
                                                      table{
                                                      border-collapse:collapse;
                                                      }
                                    		        th{
                                    			        font-weight: 400;
                                    		          }
                                               th, td {
                                                        padding: 15px;
                                    			        text-align: center;
                                                      }
                                    		 .section5{
                                    			        width:40%;
                                    					float: right;
                                    			        text-align: right;
                                    		          }
                                    	  .section5 h6{
                                    			        margin-bottom: 0px;
                                                        margin-top: 14px;
                                    		            padding-left: 0px !important;
                                    		            font-size: 16px;
                                    		          }
                                    	   .section5 p{
                                    			        margin-bottom: 0px;
                                                        margin-top: 10px;
                                    		          }
                                    		     .box2{
                                    			        width:100%;
                                    			        float: left;

                                    		          }
                                    		    @page {
                                    				   size: 7in 9.25in;
                                    				   margin: 27mm 16mm 27mm 16mm;
                                                      }
                                    		        li{
                                    			       font-size:17px;
                                    		         }
                                    		  .header{
                                    					width:100%;
                                    					float: left;
                                                        text-align:center;
                                    					# color:  #e06a2b;

                                    		          }

                                    		  .invoice{

                                    					background-color: #e06a2b;
                                    					color: white;
                                    					padding: 15px 10px 15px 10px;

                                    		         }
                                    		.innerbox{
                                    					background: white;
                                    					width: 100%;
                                    				}

          	</style>
            """

        str_mygcare_num = dct_invoice['mygcare_no'] if  dct_invoice['mygcare_no'] else ''
        html_returned=""
        html_credit_note = ""
        html_returned = """<!doctype html>
                            <html>
                            <head>
                            <meta charset="utf-8">
                            <title>Untitled Document</title>
                                <style>
                            .imagebox{
                                                 width:100%;
                                                 float: left;
                                                 border-bottom: 1px solid #c7c2c2;
                                                 padding-bottom: 12px;margin-top: 20px;
                                              }

                                @media print {
                                      .new-page {
                                        page-break-before: always;
                                      }
                                    }
                                .container{
                                                 width:1170px;
                                                 margin:auto;

                                          }
                                    .clear{
                                                clear:both;
                                          }
                                    table#voucher {

                                              width: 100%;

                                          }

                                  #voucher th,#voucher td {
                                              padding: 8px;
                                         }
                                    table#sales {

                                              width: 100%;

                                          }

                                  #sales th,#sales td {
                                              padding: 8px;
                                              text-align: left;
                                         }
                                .ibox1{
                                                width: 25%;
                                                float: left;

                                              }
                                        .ibox2{
                                                width: 50%;
                                                float: left;
                                              }
                 .ibox2 h6{
                                   margin-bottom: 0;
                                   margin-top: 10px;
                                   padding-left: 0 !important;
                                  }
                          .ibox2 p{
                                   margin-bottom: 0;
                                   margin-top: 5px;
                                   padding-right: 0;
                                   padding-left: 0;
                                  }
                            .ibox3{
                                    width: 25%;
                                    float: left;
                                  }

                                </style>"""+str_style+"""
                            </head>

                            <body>
                                <div class="container" >
                                                                            <div class="header">

                                                                                        <h3  style="font-size: 25px;margin-top: 0;margin-bottom: 0;padding:10px 10px 10px 10px;">SALE RETURN NOTE </h3>
                                                                                    <div class="clear"></div>
                                                                                </div>
                                                                            <div class="imagebox">

                                                                                   <div class="ibox1">
                                                                                       <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
                                                                                   </div>
                                                                                   <div class="ibox2">

                                                                                 <div style="width:100%;float:left;">
                                                                                        <div style="width:20%;float:left">
                                                                                        <p><span style="font-weight: 600;">ADDRESS  : </span></p>
                                                                                        </div>
                                                                                        <div style="width:79%;float: right">
                                                                                        <p>"""+str(dct_invoice['branch_address'])+ """</p>
                                                                                        </div>
                                                                                     </div>

                                                                                       <div style="width:50%;float:left;">

                                                                                           <div style="width:15%;float:left">
                                                                                           <p><span style="font-weight: 600;">PH : </span></p>
                                                                                           </div>
                                                                                           <div style="width:83%;float: right">
                                                                                            <p>"""+str(dct_voucher['branch_mob'])+"""</p>
                                                                                           </div>

                                                                                   </div>
                                                                                         <div style="width:50%;float:right;">

                                                                                             <div style="width:25%;float:left">
                                                                                           <p><span style="font-weight: 600;">MOB : </span></p>
                                                                                           </div>
                                                                                           <div style="width:73%;float: right">
                                                                                            <p>   """+str(dct_invoice['branch_mob'] or "**********")+"""</p>
                                                                                           </div>
                                                                                    </div>
                                                                                <div style="width:50%;float:left;">
                                                                                       <div style="width:45%;float:left">
                                                                                      <p><span style="font-weight: 600;">MYG CARE : </span></p>
                                                                                       </div>
                                                                                       <div style="width:54%;float: right">
                                                                                        <p> """ +str(str_mygcare_num)+"""</p>
                                                                                       </div>

                                                                                   </div>
                                                                                         <div style="width:50%;float:right;">
                                                                                            <div style="width:35%;float:left">
                                                                                             <p><span style="font-weight: 600;">EMAIL ID : </span></p>
                                                                                           </div>
                                                                                           <div style="width:65%;float: right">
                                                                                            <p>"""+str(dct_invoice['branch_mail'])+"""</p>
                                                                                           </div>
                                                                                         </div>
                                                                                       <div style="width:100%;float:left;">
                                                                                        <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
                                                                                   </div>

                                                                                 </div>
                                                                                   <div class="ibox3" style="text-align: right;">
                                                                                       <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>

                                                                                       <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
                                                                                       <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>

                                                                                   </div>

                                                                            </div>


                                        <table id="voucher">
                                                <tbody>
                                                        <tr>
                                                            <td style="text-align: left;padding: 3px !important;">Received From ,</td>
                                                            <td style="text-align: right;padding: 3px !important;">SRN No :</td>
                                                            <td style="text-align: right;width: 110px;padding: 3px !important;font-weight: 600;">"""+str(dct_invoice['srn_no'])+ """</td>
                                                        </tr>
                                                        <tr>

                                                            <td style="text-align: left;padding: 3px 3px 3px 44px !important;">"""+str((dct_invoice['sh_cust_name'] or '-----'))+"""</td>
                                                            <td style="text-align: right;padding: 3px !important;">SRN Date :</td>
                                                            <td style="text-align: right;width: 110px;padding: 3px !important;font-weight: 600;">"""+datetime.strftime(dct_invoice['srn_date'],'%d-%m-%Y')+"""</td>
                                                        </tr>
                                                        <tr>

                                                            <td style="text-align: left;padding:3px 3px 3px 44px  !important;">GSTIN:&nbsp;<span style="font-weight: 300;">"""+(dct_invoice['sh_cust_gst'] or '------')+"""</span>,</td>
                                                            <td style="text-align: right;padding: 3px 3px 3px 44px  !important;">State/Code :</td>
                                                            <td style="text-align: right;width: 110px;padding: 3px 3px 3px 44px !important;font-weight: 600;">"""+(dct_invoice['state'] or '-----')+'/'+(dct_invoice['state_code'] or '---')+"""</td>
                                                        </tr>
                                                        <tr>
                                                             <td style="text-align: left;padding:3px 3px 3px 44px  !important;">Phone No:&nbsp;<span style="font-weight: 300;">"""+str(dct_invoice['sh_cust_mobile'] or '**********')+"""</span><br>Address:&nbsp;<span style="font-weight: 300;">"""+str(dct_invoice['sh_cust_add'])+"""</span>
                                                            </td>
                                                        </tr>


                                                </tbody>

                                         </table>
                                         <table id="sales" style="margin-top: 20px;">
                                                  <thead>
                                                      <tr style="background-color: whitesmoke;">
                                                              <th>SNO</th>
                                                              <th>Particulars</th>
                                                              <th style="text-align: right">HSN/SAC</th>
                                                              <th style="text-align: right">Qty</th>
                                                              <th style="text-align: right">Rate</th>

                                                              <th style="text-align: right">Discount</th>"""
        if dct_invoice['lst_returned'][0]['igstp']:
            html_returned += """
                                                              <th style="text-align: right">IGST%</th>"""
        else:
            html_returned += """
                                                              <th style="text-align: right">CGST%</th>
                                                              <th style="text-align: right">SGST%</th>"""
        html_returned += """
                                                              <th style="text-align:right;">Amount</th>
                                                      </tr>
                                                  </thead>
                                                  <tbody>"""
        int_count=0
        dbl_cgst_tot=0
        dbl_sgst_tot=0
        dbl_kfc_tot=0
        dbl_amount_tot=0
        dbl_buyback_tot=0

        dbl_igst_tot=0
        lst_already=[]
        count=1
        for data in dct_invoice['lst_returned']:

            #
            if 1 or data['str_imei']  not in lst_already:
                lst_already.append(data['str_imei'])
                int_count += 1
                dbl_cgst_tot+=data['cgst']
                dbl_sgst_tot += data['sgst']
                dbl_igst_tot += data['igst']
                dbl_kfc_tot += data['kfc']
                dbl_amount_tot += data['amount']
                dbl_buyback_tot +=data['buyback']
                bln_last_row=count==len(dct_invoice['lst_returned'])
                count+=1

                #
                if not data['igstp']:
                    html_returned += """       						   <tr>
                                                                       <td>"""+str(int_count)+"""</td>
                                                                       <td>"""+(data['item'] or '')+""" <br>
                                                                        Imei:- """+data['str_imei']+"""<br>
                                                                            CGST 	"""+str(data['cgstp'] or '')+"""%<br>
                                                                            SGST 	"""+str(data['sgstp'] or '' )+"""%<br>"""
                    if (data['kfcp']>0):
                        html_returned +="""
                                                                            KFC 	"""+str(data['kfcp'] or '')+"""%<br>"""
                        if dct_invoice['dct_addition_data'] and bln_last_row:
                            for key,value in dct_invoice['dct_addition_data'].items():
                                 html_returned+=str(key)+"""<br>"""

                        if dct_invoice['dct_deduction_data'] and bln_last_row:
                            for key,value in dct_invoice['dct_deduction_data'].items():
                                 html_returned+=str(key)+"""<br>"""

                        html_returned +="""        							 </td>  <td style="text-align: right">"""+(data['vchr_hsn_code'] or '')+"""</td>
                                                                       <td style="text-align: right">"""+str(data['qty'])+"""</td>
                                                                       <td style="text-align: right">"""+str("{0:.2f}".format(round(data['amount'],2)))+"""</td>
                                                                       <td style="text-align: right">"""+str(data['discount'])+"""</td>
                                                                       <td style="text-align: right">"""+str(data['cgstp'])+"""</td>
                                                                       <td style="text-align: right">"""+str(data['sgstp'])+""" </td>
                                                                       <td style="text-align: right;">"""+str("{0:.2f}".format(round(data['amount'],2)))+"""<br><br>
                                                                           """+str("{0:.2f}".format(round(data['cgst'],2)))+"""<br>
                                                                           """+str("{0:.2f}".format(round(data['sgst'],2)))+"""<br>
                                                                           """+str("{0:.2f}".format(round(data['kfc'],2))) if data['kfc']>0 else ''+"""<br>"""
                        html_returned +="""<br>"""
                        if dct_invoice['dct_addition_data'] and bln_last_row:
                            for key,value in dct_invoice['dct_addition_data'].items():
                                 html_returned+=str("{0:.2f}".format(round(float(value),2)))+"""<br>"""
                        if dct_invoice['dct_deduction_data'] and bln_last_row:
                            for key,value in dct_invoice['dct_deduction_data'].items():
                                 html_returned+="""-"""+str("{0:.2f}".format(round(float(value),2)))+"""<br>"""

                    html_returned +="""                                                    </td>
                                                               </tr>"""


                else:

                    html_returned += """       						   <tr>
                                                                       <td>"""+str(int_count)+"""</td>
                                                                       <td>"""+(data['item'] or '')+""" <br>
                                                                       Imei:- """+data['str_imei']+"""<br>
                                                                            IGST 	"""+str(data['igstp'])+"""%<br>"""
                    if (data['kfcp']>0):
                        html_returned +="""
                                                                            KFC 	"""+str(data['kfcp'] or '')+"""%"""

                    html_returned +="""        							 </td>  <td style="text-align: right">"""+(data['vchr_hsn_code'] or '')+"""</td>
                                                                       <td style="text-align: right">"""+str(data['qty'])+"""</td>
                                                                       <td style="text-align: right">"""+str("{0:.2f}".format(round(data['amount']-data['igst']-data['kfc'],2)))+"""</td>

                                                                       <td style="text-align: right">"""+str(data['discount'])+"""</td>
                                                                       <td style="text-align: right">"""+str(data['igstp'])+"""</td>
                                                                       <td style="text-align: right">"""+str("{0:.2f}".format(round(data['amount']-data['igst']-data['kfc'],2)))+"""<br><br>
                                                                           """+str("{0:.2f}".format(round(data['igst'],2)))+"""<br>"""
                    html_returned += """                                  """+str("{0:.2f}".format(round(data['kfc'],2))) if data['kfc']>0 else ''+""""""
                    html_returned +="""                                                   </td>
                                                               </tr>"""


        html_returned +="""     				      </tbody>

                                                  <tfoot>"""
        if abs(dbl_buyback_tot)>0 :
            html_returned +="""                                            <tr>
                                                   <td colspan="3" style="text-align: left;">BuyBack Amount </td>
                                                    <td style="text-align: right;font-weight: 600;"></td>
                                                    <td colspan="6" style="text-align: right;">"""+str("{0:.2f}".format(round(abs(dbl_buyback_tot),2)))+"""</td><br>
                                                       </tr>"""
        # if dct_invoice['dct_addition_data']:
        #     for key,value in dct_invoice['dct_addition_data'].items():
        #          html_returned+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(+) </span>"""+str(key)+"""  :</p></div>
        #             <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(float(value),2)))+"""</p></div>
        #             <div class="clear"></div>"""
        #
        # if dct_invoice['dct_deduction_data']:
        #     for key,value in dct_invoice['dct_deduction_data'].items():
        #          html_returned+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(-) </span>"""+str(key)+"""  :</p></div>
        #             <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(float(value),2)))+"""</p></div>
        #             <div class="clear"></div>"""


        html_returned +="""                               <tr style="background-color: whitesmoke;">

                                                            <td colspan="3" style="text-align: left;font-weight: 600;color: #213fad;">Total </td>
                                                            <td style="text-align: right;font-weight: 600;color: #213fad;"></td>
                                                            <td colspan="6" style="text-align: right;font-weight: 600;color: #213fad;">"""+str("{0:.2f}".format(round(abs(dct_invoice['return_amount']+dct_invoice['flt_add_ded_total']),2)))+"""</td>
                                                       </tr>
                                                 </tfoot>
                                         </table>
                                        <div class="clear"></div>
                                        <p>"""+str(dct_invoice['return_amount_words'])+"""  only/-</p>"""
        if dct_invoice['invoice_num_returned']:
            html_returned +=""" <p>Notes:Ref.  <br>Sales Invoice No. """+str(dct_invoice['invoice_num_returned'])+"""<br>dt."""+str(datetime.strftime(dct_invoice['dat_invoice_returned'],'%d-%m-%Y'))+"""</p>"""
        html_returned +="""<div style="width: 50%;float:left;">
                                             <p style="font-weight: 600;">Receivers Signature</p>
                                        </div>
                                        <div style="width: 50%;float:right;text-align: right">
                                             <p style="font-weight: 600;">"""+dct_invoice['company_name']+"""</p>
                                             <p style="margin-top: 30px">Authorized Signatory</p>
                                        </div>

                                </div>


                            </body>
                                </html"""

        html_credit_note= """<!doctype html>
                            <html>
                            <head>
                            <meta charset="utf-8">
                            <title>Untitled Document</title>
                                <style>

                                .container{
                                                 width:1170px;
                                                 margin:auto;

                                          }
                                    .clear{
                                                clear:both;
                                          }
                                    table#voucher {
                                              border-collapse: collapse;
                                              border-spacing: 0;
                                              width: 100%;

                                          }

                                  #voucher th,#voucher td {
                                              padding: 8px;
                                         }
                                </style>"""+str_style+"""
                            </head>

                            <body>
                                <div class="container">
                                <br>
                                <br>
                                                                            <div class="header">

                                                                                        <h3  style="font-size: 25px;margin-top: 0;margin-bottom: 0;padding:10px 10px 10px 10px;">CREDIT&nbsp;NOTE </h3>
                                                                                    <div class="clear"></div>
                                                                                </div>
                                                                            <div class="imagebox">

                                                                                   <div class="ibox1">
                                                                                       <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
                                                                                   </div>
                                                                                   <div class="ibox2">

                                                                                 <div style="width:100%;float:left;">
                                                                                        <div style="width:20%;float:left">
                                                                                        <p><span style="font-weight: 600;">ADDRESS  : </span></p>
                                                                                        </div>
                                                                                        <div style="width:79%;float: right">
                                                                                        <p>"""+str(dct_invoice['branch_address'])+ """</p>
                                                                                        </div>
                                                                                     </div>

                                                                                       <div style="width:50%;float:left;">

                                                                                           <div style="width:15%;float:left">
                                                                                           <p><span style="font-weight: 600;">PH : </span></p>
                                                                                           </div>
                                                                                           <div style="width:83%;float: right">
                                                                                            <p>"""+str(dct_voucher['branch_mob'])+"""</p>
                                                                                           </div>

                                                                                   </div>
                                                                                         <div style="width:50%;float:right;">

                                                                                             <div style="width:25%;float:left">
                                                                                           <p><span style="font-weight: 600;">MOB : </span></p>
                                                                                           </div>
                                                                                           <div style="width:73%;float: right">
                                                                                            <p>   """+str(dct_invoice['branch_mob'] or "**********")+"""</p>
                                                                                           </div>
                                                                                    </div>
                                                                                <div style="width:50%;float:left;">
                                                                                       <div style="width:45%;float:left">
                                                                                      <p><span style="font-weight: 600;">MYG CARE : </span></p>
                                                                                       </div>
                                                                                       <div style="width:54%;float: right">
                                                                                        <p>"""+str(str_mygcare_num)+""" </p>
                                                                                       </div>

                                                                                   </div>
                                                                                         <div style="width:50%;float:right;">
                                                                                            <div style="width:35%;float:left">
                                                                                             <p><span style="font-weight: 600;">EMAIL ID : </span></p>
                                                                                           </div>
                                                                                           <div style="width:65%;float: right">
                                                                                            <p>"""+str(dct_invoice['branch_mail'])+"""</p>
                                                                                           </div>
                                                                                         </div>
                                                                                       <div style="width:100%;float:left;">
                                                                                        <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
                                                                                   </div>

                                                                                 </div>
                                                                                   <div class="ibox3" style="text-align: right;">
                                                                                       <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>

                                                                                       <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
                                                                                       <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>

                                                                                   </div>

                                                                            </div>

                                        <table id="voucher">
                                                <tbody>
                                                        <tr>
                                                            <td style="text-align: left;padding: 3px !important;">To,</td>
                                                            <td style="text-align: right;">CRN No :</td>
                                                            <td style="text-align: right;width: 110px;font-weight: 600;">"""+dct_invoice['srn_no'].replace('SRN-','CR-',1)+"""</td>
                                                        </tr>
                                                        <tr>

                                                            <td style="text-align: left;padding: 3px 3px 3px 44px !important;font-weight: 600;">"""+dct_invoice['sh_cust_name']+"""</td>
                                                            <td style="text-align: right;">CRN Date :</td>
                                                            <td style="text-align: right;width: 110px;font-weight: 600;">"""+datetime.strftime(dct_invoice['srn_date'],'%d-%m-%Y')+"""</td>
                                                        </tr>
                                                      <tr>

                                                            <td  style="text-align: left;padding: 3px 3px 3px 44px !important;">"""+dct_invoice['sh_cust_add']+"""</td>
                                                            <td style="text-align: right;">Ref. Doc. No.:</td>
                                                            <td style="text-align: right;width: 110px;font-weight: 600;">"""+dct_invoice['invoice_num_returned']+"""</td>
                                                        </tr>

                                                        <tr style="border-top: 1px solid #e2e2e2;border-bottom: 1px solid #e2e2e2;">
                                                            <th colspan="2" style="text-align: left;">Particulars</th>
                                                            <th style="text-align: right">Amount</th>
                                                        </tr>
                                                        <tr>
                                                             <td colspan="2" style="text-align: left">Sales Return A/c.</td>
                                                             <td style="text-align: right">"""+str("{0:.2f}".format(round(dbl_amount_tot,2)))+"""</td>
                                                        </tr>"""
        if dbl_igst_tot>0:
            html_credit_note += """                       <tr>
                                                            <td colspan="2" style="text-align: left">Output IGST A/c.</td>
                                                            <td style="text-align: right">"""+str("{0:.2f}".format(round(dbl_igst_tot,2)))+"""</td>
                                                        </tr>"""

        else:
            html_credit_note +="""
                                                        <tr>
                                                            <td colspan="2" style="text-align: left">Output CGST A/c.</td>
                                                            <td style="text-align: right">"""+ str("{0:.2f}".format(round(dbl_cgst_tot,2)))+"""</td>
                                                        </tr>
                                                        <tr>
                                                            <td colspan="2" style="text-align: left">Output SGST A/c.</td>
                                                            <td style="text-align: right">"""+ str("{0:.2f}".format(round(dbl_sgst_tot,2)))+"""</td>
                                                        </tr>"""
        if dbl_kfc_tot>0:
            html_credit_note +="""
                                                        <tr>
                                                            <td colspan="2" style="text-align: left">Kerala Flood Cess</td>
                                                            <td style="text-align: right">"""+str("{0:.2f}".format(round(dbl_kfc_tot,2)))+"""</td>
                                                        </tr>"""
        if dct_invoice['dct_addition_data']:
            for key,value in dct_invoice['dct_addition_data'].items():
                if value:
                    html_credit_note +="""
                                                            <tr>
                                                                <td colspan="2" style="text-align: left">"""+str(key)+"""</td>
                                                                <td style="text-align: right">"""+str("{0:.2f}".format(round(float(value),2)))+"""</td>
                                                            </tr>"""

        if dct_invoice['dct_deduction_data']:
            for key,value in dct_invoice['dct_deduction_data'].items():
                if value:
                    html_credit_note +="""
                                                            <tr>
                                                                <td colspan="2" style="text-align: left">"""+str(key)+"""</td>
                                                                <td style="text-align: right">-"""+str("{0:.2f}".format(round(float(value),2)))+"""</td>
                                                            </tr>"""



        html_credit_note +="""                            <tr>
                                                            <td colspan="2" style="text-align: left">Action(Credit Note issued) taken for the Sales</td>

                                                        </tr>
                                                     <tr>
                                                            <td colspan="2" style="text-align: left">Return Note : """+dct_invoice['srn_no']+""" dt. """+datetime.strftime(dct_invoice['srn_date'],'%d-%m-%Y')+"""</td>

                                                        </tr>"""

        html_credit_note +="""</tbody>

                                             <tfoot>"""



        html_credit_note +=""" <tr style="background-color: whitesmoke;">
                                                            <td></td>
                                                            <td style="text-align: right;font-weight: 600;">Total : </td>
                                                            <td style="text-align: right;font-weight: 600;">"""+str("{0:.2f}".format(round(dct_invoice['return_amount']+dct_invoice['flt_add_ded_total'],2)))+"""</td>
                                                       </tr>
                                             </tfoot>
                                         </table>
                                        <div class="clear"></div>
                                        <p>Rupees : """+dct_invoice['return_amount_words']+"""/-</p>
                                        <div style="width: 50%;float:left;">
                                             <p style="font-weight: 600;">Receivers Signature</p>
                                        </div>

                                        <div style="width: 50%;float:left;text-align: right;">
                                             <p style="font-weight: 600;">"""+dct_invoice['company_name']+"""</p><br><br><br>
                                             <p style="font-weight: 600;">Authorised Signatory</p>
                                        </div>
                                </div>
                            </body>
                            </html>"""
        return html_returned,html_credit_note
    except Exception as e:
        raise
def print_invoices(dct_invoice,dct_voucher):
    try:
        
        str_mygcare_num = dct_invoice['mygcare_no'] if  dct_invoice['mygcare_no'] else ''
        html_data = ""
        html_data2 = ""
        int_cust_type = dct_invoice['int_cust_type']
        int_amt_redeemed=0
        if 'sh_landmark' in dct_invoice :
            html_data ="""<!doctype html>
                                        <html>
                                        <head>
                                        <meta charset="utf-8">
                                        <title>Invoice Format</title>
                                        	<style>
    		      body{"""
            if dct_invoice['bln_dup']:
                html_data += """
                        background: url("""+settings.MEDIA_ROOT+"""/duplicate.png);
                        background-size: contain;
                        background-repeat: no-repeat;"""
            html_data += """font-family:Segoe, "Segoe UI", "DejaVu Sans", "Trebuchet MS", Verdana, "sans-serif";
    		          }
    		        h6{
    			        font-size: 0.85em;
    					padding-left: 10px;
    		          }
    		        p{
    			        font-size:17px;
    					word-spacing: 2px;
    					padding-left: 10px;
    					padding-right: 10px;
    		         }
    		.container{
    			         width:1170px;
    			         margin:auto;
    		          }
    		    .clear{
    			         clear:both;
    			      }
    		 .imagebox{
    			         width:100%;
    			         float: left;
    			         border-bottom: 1px solid #c7c2c2;
    			         padding-bottom: 12px;margin-top: 20px;
    		          }
    		    .ibox1{
    				    width: 25%;
    				    float: left;

    		          }
    		    .ibox2{
    				    width: 50%;
    				    float: left;
    		          }
    		 .ibox2 h6{
    			       margin-bottom: 0;
                       margin-top: 10px;
    			       padding-left: 0 !important;
    		          }

              .ibox2 p{
    			       margin-bottom: 0;
                       margin-top: 5px;
    			       padding-right: 0;
                       padding-left: 0;
		              }
    		    .ibox3{
    				    width: 25%;
    				    float: left;
    		          }
    		     .box1{
    			        width:100%;
    			        float: left;
    				    padding-bottom: 16px;

    		          }
    		 .section1{
    			        width:64%;
    			        float: left;
    		          }
          .section1 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;
    		          }
           .section1 p{
    			        margin-bottom: 0px;
                        margin-top: 10px;
    		          }
    		 .section2{
    			        width:32%;
    			        float: right;
    			        text-align: right;
    		          }
    	  .section2 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;
    		          }
           .section2 p{
    			        margin-bottom: 0px;
                        margin-top: 10px;
    		          }
    		 .section3{
    					width:50%;
    					float: left;

    		          }
          .section3 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;
    		          }
    	   .section3 p{
    			        margin-bottom: 0px;
                        margin-top: 10px;

    		          }
    		 .section4{
    			        width:50%;
    					float: right;
    		          }
          .section4 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;

    		          }
    	   .section4 p{
    			        margin-bottom: 0px;
                        margin-top: 10px;
    		          }
                      table{
                      border-collapse:collapse;
                      }
    		        th{
    			        font-weight: 400;
    		          }
               th, td {
                        padding: 15px;
    			        text-align: center;
                      }
    		 .section5{
    			        width:40%;
    					float: right;
    			        text-align: right;
    		          }
    	  .section5 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;
    		            padding-left: 0px !important;
    		            font-size: 16px;
    		          }
    	   .section5 p{
    			        margin-bottom: 0px;
                        margin-top: 10px;
    		          }
    		     .box2{
    			        width:100%;
    			        float: left;

    		          }
    		    @page {
    				   size: 7in 9.25in;
    				   margin: 27mm 16mm 27mm 16mm;
                      }
    		        li{
    			       font-size:17px;
    		         }
    		  .header{
    					width:100%;
    					float: left;
                        text-align:center;
    					# color:  #e06a2b;

    		          }

    		  .invoice{

    					background-color: #e06a2b;
    					color: white;
    					padding: 15px 10px 15px 10px;

    		         }
    		.innerbox{
    					background: white;
    					width: 100%;
    				}
    	</style>
    </head>

    <body>
    	<div class="container">
    		<div class="header">

    			        <h3  style="font-size: 25px;margin-top: 0;margin-bottom: 0;padding:10px 10px 10px 10px;">TAX INVOICE </h3>
    				<div class="clear"></div>
    			</div>
    		<div class="imagebox">

    		       <div class="ibox1">
    				   <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
    			   </div>
    			   <div class="ibox2">

                 <div style="width:100%;float:left;">
						<div style="width:20%;float:left">
						<p><span style="font-weight: 600;">ADDRESS  : </span></p>
						</div>
						<div style="width:79%;float: right">
						<p> """+str(dct_invoice['branch_address'])+"""</p>
						</div>
					 </div>

    				   <div style="width:50%;float:left;">

    					   <div style="width:15%;float:left">
    					   <p><span style="font-weight: 600;">PH : </span></p>
    					   </div>
    					   <div style="width:83%;float: right">
    						<p> """+(str(dct_invoice['branch_mob']) or " ")+"""</p>
    					   </div>

				   </div>
    				     <div style="width:50%;float:right;">

    						 <div style="width:25%;float:left">
    					   <p><span style="font-weight: 600;">MOB : </span></p>
    					   </div>
    					   <div style="width:73%;float: right">
    						<p>   """
            if dct_invoice['branch_mob']:
                html_data+=str(dct_invoice['branch_mob'])
            else:
                html_data+="**********"
            html_data+="""</p>
    					   </div>
					</div>
                <div style="width:50%;float:left;">
					   <div style="width:45%;float:left">
					  <p><span style="font-weight: 600;">MYG CARE : </span></p>
					   </div>
					   <div style="width:54%;float: right">
						<p>"""+str(str_mygcare_num)+""" </p>
					   </div>

				   </div>
    				     <div style="width:50%;float:right;">
    						<div style="width:35%;float:left">
    					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
    					   </div>
    					   <div style="width:65%;float: right">
    						<p>"""+str(dct_invoice['branch_mail'])+"""</p>
    					   </div>
						 </div>
    				   <div style="width:100%;float:left;">
					    <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
				   </div>

    			 </div>
    			   <div class="ibox3" style="text-align: right;">
    				   <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
    				   <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
    				   <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
    			   </div>

    		</div>





    	    <div style="float: left;width: 100%;">


    		    <div class="box1" style="border-bottom: 1px solid #c7c2c2;">
    				<div class="section1">"""

            if dct_invoice["vchr_irn_no"]:
                if not os.path.exists(settings.MEDIA_ROOT+"/"+dct_invoice['invoice_no']+"_qr_code.png"):
                    url = pyqrcode.create(dct_invoice["txt_qr_code"])
                    qr_code_file_name = dct_invoice['invoice_no']+"_qr_code.png"

                    url.png(settings.MEDIA_ROOT+"/"+qr_code_file_name, scale = 6)
                html_data+="""
    				    <span style="padding:5px">IRN - """+dct_invoice["vchr_irn_no"]+"""</span>
    				    <span><img style="float:left;width:128px;padding:5px" src='"""+settings.MEDIA_ROOT+"""/"""+dct_invoice['invoice_no']+"""_qr_code.png'></span>"""



            html_data+=	"""</div>
                        <div class="section2">"""
            if dct_invoice.get('fin_name'):
                html_data += """<div style="width:40%;float:left;"><p>Financier :</p></div>
        					<div style="width:60%;float:right;font-weight:600"><p>"""+dct_invoice['fin_name']+"""</p></div>
        					<div class="clear"></div>"""
            html_data+=	"""<div style="width:40%;float:left;"><p>Invoice No :</p></div>
    					<div style="width:60%;float:right;font-weight:600"><p>"""+dct_invoice['invoice_no']+"""</p></div>
    					<div class="clear"></div>

    					<div style="width: 40%;float:left;"><p>Invoice Date :</p></div>
    					<div style="width:60%;float:right;font-weight:600"><p> """+str(dct_invoice['invoice_date'])+""" </p></div>
    					<div class="clear"></div>

    					<div style="width: 40%;float:left;"><p>Invoice Time :</p></div>
    					<div style="width:60%;float:right;font-weight:600"><p> """+str(dct_invoice['invoice_time'])+"""</p></div>
    					<div class="clear"></div>
    					<div style="width:40%;float:left;"><p>State :</p></div>
    					<div style="width:60%;float:right;font-weight:600"><p> """+dct_invoice['cust_state'].title()+""" ("""+dct_invoice['cust_state_code']+""")</p></div>
    					<div class="clear"></div>"""


                        # </div> </div>"""

            if dct_invoice['staff']:
                html_data += """<div style="width: 40%;float:left;"><p>Sales Person :</p></div>
        					<div style="width:60%;float:right;font-weight:600"><p> """+dct_invoice['staff'].title()+"""</p></div>
        					<div class="clear"></div>"""

            html_data +="""</div>
    			</div>
    			<div class="clear"></div>
    			 <div class="box1">
                        <div class="section3">
    						<div style="border-right: 1px solid #c7c2c2;">
    							 <div style="width:100%;float: left;"><h6 style="border-bottom: 1px solid #c7c2c2;padding-bottom: 6px;color: green;">BILLED TO</h6></div>

    						     <div style="width:30%;float: left;"><h6>CUSTOMER NAME</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_name'].title()+"""</p></div>
    						     <div class="clear"></div>"""
            if dct_invoice['cust_add']:
                html_data +=""" <div style="width:30%;float: left;"><h6>ADDRESS</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_add']+"""</p></div>
    						     <div class="clear"></div>"""
            # if dct_invoice['cust_add']:
            #     html_data +="""   <div style="width:30%;float: left;"><h6>CITY PIN CODE</h6></div>
    		# 				     <div style="width:70%;float:right;"><p>: """+"""680307"""+"""</p></div>
    		# 				     <div class="clear"></div>"""
            html_data +="""	     <div style="width:30%;float: left;"><h6>MOB NO</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+str(dct_invoice['cust_mobile'])+"""</p></div>
    						     <div class="clear"></div>"""
            if dct_invoice['cust_gst']:
                html_data +="""  <div style="width:30%;float: left;"><h6>GSTN NO</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+str(dct_invoice['cust_gst'])+"""</p></div>
    						     <div class="clear"></div>"""
            if dct_invoice['cust_state']:
                html_data +="""  <div style="width:30%;float: left;"><h6>STATE</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_state'].title()+"""/"""+dct_invoice['cust_state_code']+"""</p></div>
    						     <div class="clear"></div>"""

            html_data +="""</div>
            		    </div>

            		       <div class="section4">
            					 <div style="width:100%;float: left;"><h6 style="border-bottom: 1px solid #c7c2c2;padding-bottom: 6px;color: green;">SHIPPED TO</h6></div>

            				     <div style="width:30%;float: left;"><h6>Name</h6></div>
            				     <div style="width:70%;float:right;"><p>: """+dct_invoice['sh_cust_name'].title()+"""</p></div>
            				     <div class="clear"></div>"""
            if dct_invoice['sh_cust_add']:
                html_data +=""" <div style="width:30%;float: left;"><h6>Address</h6></div>
            				     <div style="width:70%;float:right;"><p>: """+dct_invoice['sh_cust_add']+"""</p></div>
            				     <div class="clear"></div>"""
            if 'sh_landmark' in dct_invoice:
                html_data +=""" <div style="width:30%;float: left;"><h6>Landmark</h6></div>
            				     <div style="width:70%;float:right;"><p>: """+dct_invoice['sh_landmark']+"""</p></div>
            				     <div class="clear"></div>"""
            # html_data +="""<div style="width:30%;float: left;"><h6>CITY PIN CODE</h6></div>
            # 				     <div style="width:70%;float:right;"><p>: 680307</p></div>
            # 				     <div class="clear"></div>

            html_data +="""<div style="width:30%;float: left;"><h6>MOB No</h6></div>
            				    <div style="width:70%;float:right;"><p>: """+str(dct_invoice['sh_cust_mobile'])+"""</p></div>
            				    <div class="clear"></div>"""
            if dct_invoice['sh_cust_gst']:
                html_data +=""" <div style="width:30%;float: left;"><h6>GSTN No</h6></div>
            				    <div style="width:70%;float:right;"><p>: """+str(dct_invoice['sh_cust_gst'])+"""</p></div>
            				    <div class="clear"></div>"""
            if dct_invoice['cust_state']:
                html_data +=""" <div style="width:30%;float: left;"><h6>State</h6></div>
            				    <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_state'].title()+"""/"""+dct_invoice['cust_state_code']+"""</p></div>
            				    <div class="clear"></div>"""

            html_data+="""</div>"""



            html_data +="""
                     </div>
            	             <div class="clear"></div>
            	              <div class="table-responsive print">
            					  <table style="width:100%;border: 1px solid #cecdcd;">

            						  <tr style="background-color: #e06a2b;color: white;">
            							<th style="border: 1px solid #cecdcd;">SLNO</th>
            							<th style="border: 1px solid #cecdcd;">ITEM DESCRIPTION/DETAIL</th>
            							<th style="border: 1px solid #cecdcd;">HSN/SAC</th>
            							<th style="border: 1px solid #cecdcd;">QTY</th>
            							<th style="border: 1px solid #cecdcd;">RATE</th>
            						    <th style="border: 1px solid #cecdcd;">DISCOUNT</th>"""
            if dct_invoice['bln_igst']:
                html_data +="""<th style="border: 1px solid #cecdcd;">IGST %</th>"""
            else:
                html_data +="""
            							<th style="border: 1px solid #cecdcd;">SGST %</th>
    									<th style="border: 1px solid #cecdcd;">CGST %</th>"""
            html_data +="""<th style="border: 1px solid #cecdcd;">GROSS AMOUNT</th>
    								  </tr>"""
            int_index = 1
            for str_item in dct_invoice['lst_item']:
                html_data +="""<tr>		<td style="border: 1px solid #cecdcd;">"""+str(int_index)+"""</td>
    									<td style="text-align:left;border: 1px solid #cecdcd;">"""+str_item['item']
                if str_item['str_imei']:
                    html_data +="""<br>Imei:-"""+str_item['str_imei']
                html_data +="""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['hsn_code'])+"""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['qty'])+"""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str("{0:.2f}".format(round(str_item['amount'],2)))+"""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str("{0:.2f}".format(round(str_item['discount'],2)))+"""</td>"""
                if dct_invoice['bln_igst']:
                    html_data +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['igst'])+"""</td>"""
                else:
                    html_data +="""	<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['sgst'])+"""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['cgst'])+"""</td>"""
                html_data +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str("{0:.2f}".format(round(str_item['amount'],2)))+"""</td>
    								  </tr>"""
                int_index +=1
            html_data+="""</table>
    						  </div>
    			           <div class="clear"></div>
    			        <div class="box2">
    						   <div class="section5">
    							   <div style="margin-top: 10px;">"""
            for dct_tax in dct_invoice['tax']:
                for str_tax in dct_invoice['tax'][dct_tax]:
                    if dct_invoice['bln_igst']:
                        if dct_tax.upper() == 'IGST':
                            html_data+="""<div style="width:60%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
            						        <div style="width:40%;float:right;"><p>"""+str("{0:.2f}".format(round(dct_invoice['tax'][dct_tax][str_tax],2)))+"""</p></div>
            						        <div class="clear"></div>"""
                    else:
                        if dct_tax.upper() in ['CGST','SGST']:
                            html_data+="""<div style="width:60%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
            						        <div style="width:40%;float:right;"><p>"""+str("{0:.2f}".format(round(dct_invoice['tax'][dct_tax][str_tax],2)))+"""</p></div>
            						        <div class="clear"></div>"""

    							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> SGST 9% :</p></div>
    						        # <div style="width:65%;float:right;"><p>0.00</p></div>
    						        # <div class="clear"></div>
                                    #
    							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> CGST 6% :</p></div>
    						        # <div style="width:65%;float:right;"><p>0.00</p></div>
    						        # <div class="clear"></div>
                                    #
    							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> SGST 6% :</p></div>
    						        # <div style="width:65%;float:right;"><p>0.00</p></div>
    						        # <div class="clear"></div>
            if dct_invoice['bln_kfc'] and int_cust_type != 3:
                html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(+) </span>KERALA FLOOD CESS(1%) :</p></div>
                <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['dbl_kfc'],2)))+"""</p></div>
                <div class="clear"></div>"""
            if dct_invoice['dct_addition_data']:
                for key,value in dct_invoice['dct_addition_data'].items():
                    if value:
                        html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(+) </span>"""+str(key)+"""  :</p></div>
                        <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(float(value),2)))+"""</p></div>
                        <div class="clear"></div>"""

            if dct_invoice['dct_deduction_data']:
                for key,value in dct_invoice['dct_deduction_data'].items():
                    if key=='POINT REDUMPTION':
                        int_amt_redeemed=value
                    if value and key!='POINT REDUMPTION':
                        html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(-) </span>"""+str(key)+"""  :</p></div>
                        <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(float(value),2)))+"""</p></div>
                        <div class="clear"></div>"""

            if dct_invoice['service_charge']:
                html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(+) </span>PROCESSING CHARGE :</p></div>
                <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['service_charge'],2)))+"""</p></div>
                <div class="clear"></div>"""

            html_data+="""<div style="padding-bottom: 12px;background-color: #ffede3;margin-top: 12px;padding-right:2px;">
    									<div style="width:60%;float: left;"><p>SUB TOTAL :</p></div>
    									<div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['total']+dct_invoice['flt_add_ded_total']+int_amt_redeemed,2)))+"""</p></div>
    									<div class="clear"></div>"""

            if dct_invoice['coupon']:
                html_data+="""<div style="width:60%;float: left;"><p>COUPON AMOUNT :</p></div>
    									<div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['coupon'],2)))+"""</p></div>
    									<div class="clear"></div>"""

            # if dct_invoice['loyalty']:
            #     html_data+="""<div style="width:60%;float: left;"><p>LOYALTY AMOUNT :</p></div>
    		# 							<div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['loyalty'],2)))+"""</p></div>
    		# 							<div class="clear"></div>"""
            if dct_invoice['buyback']:
                html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(-) </span>BUYBACK AMOUNT :</p></div>
    									<div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['buyback'],2)))+"""</p></div>
    									<div class="clear"></div>"""
            dbl_total = round(dct_invoice['total']+dct_invoice['flt_add_ded_total']-dct_invoice['coupon']+int_amt_redeemed,2)
            dbl_total_rounded = round(dct_invoice['total']+dct_invoice['flt_add_ded_total']-dct_invoice['coupon']+int_amt_redeemed)
            p = inflect.engine()
            vchr_amount = p.number_to_words(dbl_total_rounded).title() +' Rupees only.'
            dbl_round_off = round(dbl_total_rounded - dbl_total,2)
            if dbl_round_off != 0.0:
                html_data+="""<div style="width:60%;float: left;"><p>ROUNDING OFF :</p></div>
							  <div style="width:40%;float:right;"><p> """+str(dbl_round_off)+"""</p></div>
    						  <div class="clear"></div>"""

            html_data+="""<div style="width:60%;float: left;"><p style="margin-top: 5px;"><b>TOTAL : </b></p></div>
    					  <div style="width:40%;float:right;"><p style="margin-top: 4px;"><b> """+str("{0:.2f}".format(round(dbl_total_rounded,2)))+""" </b></p></div>
    					  <div class="clear"></div>
    							  </div>
    							   </div>
    						 </div></div>

                             <div style="width:90%;float: left;"><p style="margin-top: 5px;"><b>TOTAL(in words) :  &nbsp&nbsp&nbsp"""+str(vchr_amount)+"""</b></p></div>"""
            if not dct_invoice['service_charge']:
                html_data += """<div style="width:90%;float: left;"><p style="margin-top: 5px;"><b>"""+dct_invoice['company_name']+"""</b></p></div>"""
            if dct_invoice.get('dbl_down_payment'):
                html_data+= """ <div class="box2" style="border-top: 1px solid #c7c2c2;padding-top:10px;  padding-bottom:10px"> Down Payment : """+str(dct_invoice['dbl_down_payment'])+"""</div>"""
            if int_amt_redeemed and int_amt_redeemed!=0:
                html_data+= """ <div class="box2" style="border-top: 1px solid #c7c2c2;padding-top:10px;  padding-bottom:10px">Amount Redeemed -"""+str("{0:.2f}".format(round(int_amt_redeemed,2)))+"""</div>"""
            if dct_invoice.get('lst_payment_details'):
                html_data+= """ <div class="box2" style="border-top: 1px solid #c7c2c2;padding-top:10px;  padding-bottom:10px">"""+dct_invoice['lst_payment_details']+"""</div>"""
            html_data+= """ <div class="box2" style="border-top: 1px solid #c7c2c2;">
    						   <p style="font-weight: 600;">TERMS / CONDITIONS:</p>
    							<ul style="list-style-type:disc;"> """

            
            if dct_invoice['terms']:
                for dct_terms in ['invoice-A','invoice-B','invoice-C']:
                    for index in range(1,len(dct_invoice['terms'][dct_terms])+1):
                        if index==1:
                            html_data+="""<p style="text-align:center;color:#fa5e07;">"""+dct_invoice['terms'][dct_terms][str(index)]+"""</p><br>"""
                        elif dct_terms.upper() == 'INVOICE-A' and index==2:
                            html_data+="""<p style="text-align:center;color:#055f7a;">"""+dct_invoice['terms'][dct_terms][str(index)]+"""</p><br>"""
                        else:
                        # if 1:
                            html_data+="""<li style="font-weight:5000px">"""+dct_invoice['terms'][dct_terms][str(index)]+"""</li>"""
                            html_data+="""<br>"""
            html_data +="""</ul>
                            </div>
    			          </div>
    		        </div>
    	     </div>

    </body>
    </html> """

        else:
            html_data2 = html_voucher+"""<!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Invoice Format</title>
    	<style>
    		      body{"""
            if dct_invoice['bln_dup']:
                html_data2 += """
                        background: url("""+settings.MEDIA_ROOT+"""/duplicate.png);
                        background-size: contain;
                        background-repeat: no-repeat;"""
            html_data2 += """font-family:Segoe, "Segoe UI", "DejaVu Sans", "Trebuchet MS", Verdana, "sans-serif";

    		          }
    		        h6{
    			        font-size: 0.85em;
    					padding-left: 10px;
    		          }
    		        p{
    			        font-size:17px;
    					word-spacing: 2px;
    					padding-left: 10px;
    					padding-right: 10px;
    		         }
    		.container{
    			         width:1170px;
    			         margin:auto;
    		          }
    		    .clear{
    			         clear:both;
    			      }
    		 .imagebox{
    			         width:100%;
    			         float: left;
    			         border-bottom: 1px solid #c7c2c2;
    			         padding-bottom: 12px;margin-top: 20px;
    		          }
    		    .ibox1{
    				    width: 25%;
    				    float: left;

    		          }
    		    .ibox2{
    				    width: 50%;
    				    float: left;
    		          }
    		 .ibox2 h6{
    			       margin-bottom: 0;
                       margin-top: 10px;
    			       padding-left: 0 !important;
    		          }
    		  .ibox2 p{
    			       margin-bottom: 0;
                       margin-top: 5px;
    			       padding-right: 0;
                       padding-left: 0;
		              }
    		    .ibox3{
    				    width: 25%;
    				    float: left;
    		          }
    		     .box1{
    			        width:100%;
    			        float: left;
    				    padding-bottom: 16px;

    		          }
    		 .section1{
    			        width:50%;
    			        float: left;
    			        margin-top: 10px;
    		          }
          .section1 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;
    		          }
           .section1 p{
    			        margin-bottom: 0px;
                        margin-top: 5px;
    		            color: gray;
    		          }
    		 .section2{
    			        width:40%;
    			        float: right;
    			        margin-top: 10px;
    			        text-align: right;
    		          }
    	  .section2 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;
    		          }
           .section2 p{
    			        margin-bottom: 0px;
                        margin-top: 10px;
    		          }
    		 .section3{
    					width:50%;
    					float: left;

    		          }
          .section3 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;
    		          }
    	   .section3 p{
    			        margin-bottom: 0px;
                        margin-top: 10px;
    		          }
    		 .section4{
    			        width:50%;
    					float: right;
    		          }
          .section4 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;

    		          }
    	   .section4 p{
    			        margin-bottom: 0px;
                        margin-top: 10px;
    		          }
    	         table{
    				   border-collapse: collapse;
                      }
    		        th{

    					font-weight: 400;
    		          }
               th, td {
                        padding: 15px;
    			        text-align: center;
                      }
    		 .section5{
    			        width:40%;
    					float: right;
    			        text-align: right;
    		          }
    	  .section5 h6{
    			        margin-bottom: 0px;
                        margin-top: 14px;
    		            padding-left: 0px !important;
    		            font-size: 16px;
    		          }
    	   .section5 p{
    			        margin-bottom: 0px;
                        margin-top: 10px;

    		          }
    		     .box2{
    			        width:100%;
    			        float: left;

    		          }
    		    @page {
    				   size: 7in 9.25in;
    				   margin: 27mm 16mm 27mm 16mm;
                      }
    		        li{
    			       font-size:17px;
    		          }
    		   .header{
    					width:100%;
    					float: left;
        				color: #e06a2b;
                        text-align:center;

    		          }

    		  .invoice{

    					background-color: #e06a2b;
    					color: white;
    					padding: 15px 10px 15px 10px;

    		         }
    		.innerbox{
    			    background: white;
    				width: 100%;
    				}
    	</style>
    </head>

    <body>

    	<div class="container">
    		<div class="header">

    			        <h3  style="font-size: 25px;margin-top: 0;margin-bottom: 0;padding:10px 10px 10px 10px;">INVOICE </h3>
    				<div class="clear"></div>
    			</div>
    		<div class="imagebox">

    		       <div class="ibox1">
    				   <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
    			   </div>
    			   <div class="ibox2">

                 <div style="width:100%;float:left;">

                        <div style="width:20%;float:left">
						<p><span style="font-weight: 600;">ADDRESS  : </span></p>
						</div>
						<div style="width:79%;float: right">
						<p> """+str(dct_invoice['branch_address'])+"""</p>
						</div>

					 </div>

    				   <div style="width:50%;float:left;">

    					   <div style="width:15%;float:left">
    					   <p><span style="font-weight: 600;">PH : </span></p>
    					   </div>
    					   <div style="width:83%;float: right">
    						<p>"""+str(dct_voucher['branch_mob'])+"""</p>
    					   </div>

				   </div>
    				     <div style="width:50%;float:right;">

    						 <div style="width:25%;float:left">
    					   <p><span style="font-weight: 600;">MOB : </span></p>
    					   </div>
    					   <div style="width:73%;float: right">
    						<p>   """
            if dct_invoice['branch_mob']:
                html_data2+=str(dct_invoice['branch_mob'])
            else:
                html_data2+="**********"
            html_data2+="""</p>
    					   </div>
					</div>
                <div style="width:50%;float:left;">
					   <div style="width:45%;float:left">
					  <p><span style="font-weight: 600;">MYG CARE : </span></p>
					   </div>
					   <div style="width:54%;float: right">
						<p> """+str(str_mygcare_num)+""" </p>
					   </div>

				   </div>
    				     <div style="width:50%;float:right;">
    						<div style="width:35%;float:left">
    					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
    					   </div>
    					   <div style="width:65%;float: right">
    						<p>"""+str(dct_invoice['branch_mail'])+"""</p>
    					   </div>
						 </div>
    				   <div style="width:100%;float:left;">
					    <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
				   </div>

    			 </div>
    			   <div class="ibox3" style="text-align: right;">
    				   <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>

    				   <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
    				   <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>

    			   </div>

    		</div>





    	    <div style="float: left;width: 100%;">


    		    <div class="box1">
    				<div class="section1">
    					<div>	<p style="color: gray;">SHIPPING ADDRESS </p></div>






    					        <div style="width:100%;float:left;"><p style="font-weight: 600;color: black"> """+dct_invoice['cust_name'].title()+"""</p></div>
    						     <div class="clear"></div>


    						     <div style="width:100%;float:left;"><p> """+dct_invoice['cust_add']+"""</p></div>
    						     <div class="clear"></div>


    <!--
    						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_name'].title()+"""</p></div>
    						     <div class="clear"></div>

    						     <div style="width:30%;float: left;"><h6>ADRESS 1</h6></div>
    						     <div style="width:70%;float:right;"><p>: J D Tower, Opp. Reliance Fresh, KSRTC Road, Chalakudy, Thrissur, Kerala ,India, Chalakudy, Kerala 680307</p></div>
    						     <div class="clear"></div>

    -->


    <!--						     <div style="width:30%;float: left;"><h6>CITY PIN CODE</h6></div>-->
    <!--
    <!--						     <div style="width:100%;float:left;"><p> 680307</p></div>-->
    						     <div class="clear"></div>


    <!--						     <div style="width:30%;float: left;"><h6>MOB NO</h6></div>-->
    						     <div style="width:100%;float:left;"><p> """+str(dct_invoice['cust_mobile'])+"""</p></div>
    						     <div class="clear"></div>

    <!--						     <div style="width:30%;float: left;"><h6>GSTN NO</h6></div>-->
    						     <div style="width:100%;float:left;"><p> """+str(dct_invoice['cust_gst'])+"""</p></div>
    						     <div class="clear"></div>

    <!--						     <div style="width:30%;float: left;"><h6>STATE</h6></div>-->
    						     <div style="width:100%;float:left;"><p> """+dct_invoice['cust_state'].title()+"""/"""+dct_invoice['cust_state_code']+"""</p></div>
    						     <div class="clear"></div>


    				</div>
    				<div class="section1">"""
            if dct_invoice["vchr_irn_no"]:
                if not os.path.exists(settings.MEDIA_ROOT+"/"+dct_invoice['invoice_no']+"_qr_code.png"):
                    url = pyqrcode.create(dct_invoice["txt_qr_code"])
                    qr_code_file_name = dct_invoice['invoice_no']+"_qr_code.png"

                    url.png(settings.MEDIA_ROOT+"/"+qr_code_file_name, scale = 6)
                html_data2+="""
            		    <span style="padding:5px">IRN - """+dct_invoice["vchr_irn_no"]+"""</span>
            		    <span><img style="float:left;width:128px;padding:5px" src='"""+settings.MEDIA_ROOT+"""/"""+dct_invoice['invoice_no']+"""_qr_code.png'></span>"""



            html_data2+=	"""</div>
                        <div class="section2">"""
            html_data2+="""<div style="width:50%;float:left;"><p>Invoice No :</p></div>
                    		<div style="width:50%;float:right;font-weight:600"><p> """+dct_invoice['invoice_no']+"""</p></div>
                    		<div class="clear"></div>

                    		<div style="width: 50%;float:left;"><p>Invoice Date :</p></div>
                    		<div style="width:50%;float:right;font-weight:600"><p> """+dct_invoice['invoice_date']+""" </p></div>
                    		<div class="clear"></div>

                    		<div style="width: 50%;float:left;"><p>Invoice Time :</p></div>
                    		<div style="width:50%;float:right;font-weight:600"><p>"""+dct_invoice['invoice_time']+"""</p></div>
                    		<div class="clear"></div>
                    		<div style="width:50%;float:left;"><p>State :</p></div>
                    		<div style="width:50%;float:right;font-weight:600"><p> """+dct_invoice['cust_state'].title()+""" ("""+dct_invoice['cust_state_code']+""")</p></div>
                    		<div class="clear"></div>"""

            if dct_invoice['staff']:
                html_data2 +="""<div style="width: 50%;float:left;"><p>Sales Person :</p></div>
    					<div style="width:50%;float:right;font-weight:600"><p> """+dct_invoice['staff'].title()+"""</p></div>
    					<div class="clear"></div>"""

            html_data2+="""</div>
    			</div>
    			<div class="clear"></div>


    			              <div class="table-responsive">
    							  <table style="width:100%;border: 1px solid #cecdcd;">

    								  <tr style="background-color: #e06a2b;color: white;">
    									<th style="border: 1px solid #cecdcd;">SLNO</th>
    									<th style="border: 1px solid #cecdcd;">ITEM DESCRIPTION/DETAIL</th>
    									<th style="border: 1px solid #cecdcd;">HSN/SAC</th>
    									<th style="border: 1px solid #cecdcd;">QTY</th>
    									<th style="border: 1px solid #cecdcd;">RATE</th>
    									<th style="border: 1px solid #cecdcd;">DISCOUNT</th>"""
            if dct_invoice['bln_igst']:
                html_data2 +="""<th style="border: 1px solid #cecdcd;">IGST %</th>"""
            else:
                html_data2 +="""<th style="border: 1px solid #cecdcd;">SGST %</th>
    							<th style="border: 1px solid #cecdcd;">CGST %</th>"""
            html_data2 +="""<th>GROSS AMOUNT</th>
    								  </tr>"""
            int_index = 1
            for str_item in dct_invoice['lst_item']:
                html_data2+="""<tr>		<td style="border: 1px solid #cecdcd;">"""+str(int_index)+"""</td>
    									<td style="text-align:left;border: 1px solid #cecdcd;">"""+str_item['item']+"""<br>Imei:-"""+str_item['str_imei']+"""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str_item['hsn_code']+"""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['qty'])+"""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['amount'])+"""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['discount'])+"""</td>"""
                if dct_invoice['bln_igst']:
                    html_data2 +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['igst'])+"""</th>"""
                else:
                    html_data2 +="""	<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['sgst'])+"""</td>
    									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['cgst'])+"""</td>"""
                html_data2 +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['total'])+"""</td>
    								  </tr>"""
                int_index +=1

            html_data2 +="""</table>
    						  </div>
    			           <div class="clear"></div>
    			           <div class="box2">
    						   <div class="section5">
    							   <div style="margin-top: 10px;">"""
            for dct_tax in dct_invoice['tax']:
                for str_tax in dct_invoice['tax'][dct_tax]:
                    if dct_invoice['bln_igst']:
                        if dct_tax.upper() == 'IGST':
                            html_data2+="""<div style="width:50%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
            						        <div style="width:50%;float:right;"><p>"""+str(dct_invoice['tax'][dct_tax][str_tax])+"""</p></div>
            						        <div class="clear"></div>"""
                    else:
                        if dct_tax.upper() in ['CGST','SGST']:
                            html_data2+="""<div style="width:50%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
            						        <div style="width:50%;float:right;"><p>"""+str(dct_invoice['tax'][dct_tax][str_tax])+"""</p></div>
            						        <div class="clear"></div>"""
    							    # <div style="width:35%;float: left;">  <p><span style="font-size: 13px">(+) </span>CGST 9% :</p></div>
    						        # <div style="width:65%;float:right;"><p>0.00</p></div>
    						        # <div class="clear"></div>
                                    #
    							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> SGST 9% :</p></div>
    						        # <div style="width:65%;float:right;"><p>0.00</p></div>
    						        # <div class="clear"></div>
                                    #
    							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> CGST 6% :</p></div>
    						        # <div style="width:65%;float:right;"><p>0.00</p></div>
    						        # <div class="clear"></div>
                                    #
    							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> SGST 6% :</p></div>
    						        # <div style="width:65%;float:right;"><p>0.00</p></div>
    						        # <div class="clear"></div>

            html_data2+="""<div style="padding-bottom: 12px;background-color: #ffede3;margin-top: 12px;padding-right: 10px;">
    									<div style="width:50%;float: left;"><p>SUB TOTAL :</p></div>
    									<div style="width:50%;float:right;"><p> """+str(round(dct_invoice['total'],2))+"""</p></div>
    									<div class="clear"></div>


    									<div style="width:50%;float: left;"><p>COUPON AMOUNT :</p></div>
    									<div style="width:50%;float:right;"><p> """+str(dct_invoice['coupon'])+"""</p></div>
    									<div class="clear"></div>


    									# <div style="width:50%;float: left;"><p>LOYALTY AMOUNT :</p></div>
    									# <div style="width:50%;float:right;"><p> """+str(dct_invoice['loyalty'])+"""</p></div>
    									# <div class="clear"></div>


    									<div style="width:50%;float: left;"><p><span style="font-size: 13px">(-) </span>BUYBACK AMOUNT :</p></div>
    									<div style="width:50%;float:right;"><p> """+str(dct_invoice['buyback'])+"""</p></div>
    									<div class="clear"></div>"""
            # if dct_invoice['indirect_discount']:
            #     html_data2+="""<div style="width:50%;float: left;"><p>VOUCHER AMOUNT:</p></div>
    		# 							<div style="width:50%;float:right;"><p> """+str(round(dct_invoice['indirect_discount'],2))+"""</p></div>
    		# 							<div class="clear"></div>"""

            html_data2+="""	<div style="width:50%;float: left;"><p style="margin-top: 5px;"><b>TOTAL : </b></p></div>
    									<div style="width:50%;float:right;"><p style="margin-top: 4px;"><b> """+str(round(dct_invoice['total']-dct_invoice['buyback']-dct_invoice['coupon'],2))+""" </b></p></div>
    									<div class="clear"></div>
    							  </div>
    							   </div>
    						 </div>
    		               </div>
    			           <div class="box2" style="border-top: 1px solid #c7c2c2;">

    						   <p style="font-weight: 600;">TERMS / CONDITIONS:</p>

    							<ul style="list-style-type:disc;">"""
            for index in range(1,len(dct_invoice['terms'])+1):
                html_data2+="""<li>"""+dct_invoice['terms'][str(index)]+"""</li>"""
                html_data+="""<br>"""

            html_data2 +="""</ul>
                            </div>"""
            # if dct_invoice['bln_dup']:
            #     html_data2 +="""<div><p style="color:red;">Duplicate</p></div>"""
            html_data2+="""</div>
    		        </div>
    	     </div>
    </body>
    </html> """
        
        if html_data2:
            return html_data2
        else:
            return html_data

    except Exception as e:
        raise
def print_service_customer(dct_invoice,dct_voucher):
    try:
        html_service_customer = " "

        html_service_customer+='''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Untitled Document</title>
<style>
     .container{
		  width:95%;
		  margin:auto;
		 }
		.clear{
			clear:both;
			}
		h4{
			 text-align:center;
			}
</style>
</head>

<body>
       <div class="container">
           <h4 style="margin-bottom:0px;">myG Care</h4>
           <h4 style="margin-top:10px;">'''+str(dct_invoice['branch_location']).upper()+'''</h4>
           <h4 style="text-decoration: underline;color:green">SERVICE CENTRE GATEPASS</h4>
           <div style="width:50%;float:left;">
              <p>To,</p>
               <p style="padding-left: 20px;">'''+str(dct_invoice['cust_name']).title()+'''</p>
               <p style="padding-left: 20px;">'''+str(dct_invoice['cust_mobile'])+'''</p>
           </div>
           <div style="width:50%;float:right;text-align:right;">
               <p>Doc No: '''+ str(dct_invoice['invoice_no'])+'''</p>
               <p>DATE: '''+ str(dct_invoice['invoice_date'])+'''</p>
           </div>
           <div class="clear"></div>
           <div style="width:100%;float:left;">
              <h4 style="margin-top:0px;">PRODUCT:&nbsp; '''+str(dct_invoice['serviced_item']['item'])+'''</h4>
              <p style="margin-bottom:0px;">I certify that above product has been delivered to me.</p>
           </div>
            <div class="clear"></div>
              <div style="width:50%;float:left;">
              <p>Collection Date: </p>
              <br />
              <p>Name & Signature of Customer</p>

           </div>
           <div style="width:50%;float:right;text-align:right;">
               <p>Delivered by </p> <br />
               <p>Signature</p>
           </div>
       </div>
</body>
</html>

        '''
        return html_service_customer
    except Exception as e:
        raise

def print_exchange(int_sm_id):
    try:
        ins_partial_inv  = PartialInvoice.objects.filter(fk_invoice_id = int_sm_id ).annotate(
                                        str_formatted_date=Func( F('dat_invoice'), Value('dd-MM-yyyy'), function='to_char', output_field=CharField()

                                        )).values('json_data','dat_invoice','fk_invoice__vchr_invoice_num','fk_invoice__fk_customer_id','str_formatted_date').first()



        if ins_partial_inv:
            str_branch = ins_partial_inv['json_data']['str_branch']
            dat_invoice = ins_partial_inv['str_formatted_date']
            str_invoice_no = ins_partial_inv['fk_invoice__vchr_invoice_num']
            ins_cust = SalesCustomerDetails.objects.filter(pk_bint_id = ins_partial_inv['fk_invoice__fk_customer_id'] ).values().first()
            str_cust_mob = ins_cust['int_mobile']
            str_cus_name = ins_cust['vchr_name']
            str_add = ins_cust['txt_address'] or ''
            lst_product_images= []
            vchr_item_code = ''










        str_html = """<html>
                                    <head>
                                        <meta charset="utf-8">

                                        <link href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.css" rel="stylesheet" />
                                        <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js"></script>
                                        <script src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.js"></script>

                                        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                                        <style>
                                            body{
                                                    background: url("""+settings.MEDIA_ROOT+"""/watermarks/servicercopy.png);
                                                    background-size: contain;
                                                    background-repeat: repeat-y;
                                                    background-position: center;
                                                }
                                        </style>
                                    </head>
                                <body style="margin-left: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 0px; font-family: sans-serif; font-size: 14px;">
                                <div style="width:1000px; height:100%; margin:0 auto; padding:15px;font-family: sans-serif; float:center; ">

                                    <div style="text-align:right; padding-bottom: 15px; margin-bottom: 15px; line-height:18px;">
                                        <img src ="http://www.gdot.in/theme/images/store.png" style="float:left;display: block;" width="100px" height="100px">
                                        <h2 style="font-weight:bold; font-size:20px; margin:0; color:#1c252b;"></h2>"""
                    # if dct_data['branch_add']:
                        # str_html+="""<h2 style="font-weight:100; font-size:14px; margin:0; color:#1c252b;">"""+dct_data['branch_add'].upper()+"""</h2>"""
                    # if dct_data['contact']:
                        # str_html+="""<h3 style="font-weight:100; font-size:14px; margin:5px 0; color:#1c252b;">"""+dct_data['contact']+"""</h3>"""
                    # if dct_data['mail']:
                        # str_html+="""<h4 style="font-weight:100; font-size:14px; margin:5px 0; color:#1990e4;">"""+dct_data['mail']+"""</h4>"""
        str_html+="""<h4 style="font-weight:100; font-size:14px; margin:5px 0; color:#1c252b;">"""+"""</h4>
                        </div>

                        <div class="col-sm-12 col-xs-12 ">
                            <h1 style="font-weight:bold; text-align:center; font-size:30px; margin-left:8px;  color:green;">EXCHANGE DETAILS SHEET</h1>
                        </div>

                        <p> </p>

                        """
        str_html+="""
                            <div class="col-sm-12 col-xs-12" style="margin-bottom:20px;">

                                <table width="100%" border="1" cellpadding="0" cellspacing="0" style="line-height:24px; margin-top:60px;margin-bottom:40px;" >
                            <tr>
                            <td bgcolor="transparent" style="padding:5px; font-size:14px; ">BRANCH : </td><td style="padding:5px;" bgcolor="transparent">"""+str_branch+"""</td>"""

        str_html+="""
                        </tr>
                        <td bgcolor="transparent" style="padding:5px; font-size:14px; ">DATE : </td><td style="padding:5px;" bgcolor="transparent"> """+dat_invoice+"""</td></tr>"""

        str_html += """ <tr><td bgcolor="transparent" style="padding:5px; font-size:14px; ">INVOICE NUMBER:  </td><td style="padding:5px;" bgcolor="transparent"> """+str_invoice_no+"""</td></tr>
        <tr>
        <td bgcolor="transparent" style="padding:5px; font-size:14px; ">CUSTOMER NAME & ADDRESS :</td><td style="padding:5px;" bgcolor="transparent"> """+str_cus_name+','+str_add+"""</td></tr>
        <td bgcolor="transparent" style="padding:5px; font-size:14px; ">MOBILE NO.: </td><td style="padding:5px;" bgcolor="transparent"> """+str(str_cust_mob)+"""</td></tr>


         """
        int_sm_items=0
        for data in ins_partial_inv['json_data']['lst_items']:

            if data['int_status'] == 2:
                int_sm_items += 1
                str_imei = data['json_imei']['imei'][0]
                lst_product_images = data['dct_images']['product']
                flt_taken_price = abs(data['dbl_amount'])
                vchr_item_code = data['vchr_item_code']

                ins_item = Item.objects.filter(vchr_item_code = vchr_item_code).values('fk_brand__vchr_name').first()
                str_brand_name = ins_item['fk_brand__vchr_name']

                str_html += """
                        <tr><td bgcolor="transparent" style="padding:5px; font-size:14px; " colspan="2"><u><b>Item """+str(int_sm_items)+"""</b></u></td</tr>
                        <tr><td bgcolor="transparent" style="padding:5px; font-size:14px; ">BRAND :  </td><td style="padding:5px;" bgcolor="transparent"> """+str_brand_name+"""</td></tr>
                        <tr><td bgcolor="transparent" style="padding:5px; font-size:14px; ">IMEI/SERIAL NO :</td><td style="padding:5px;" bgcolor="transparent"> """+str_imei+"""</td></tr>
                        <tr><td bgcolor="transparent" style="padding:5px; font-size:14px; ">TAKEN PRICE :</td><td style="padding:5px;" bgcolor="transparent"> """+str(flt_taken_price)+"""</td></tr>
                                    """


                str_html +=""" <tr><td bgcolor="transparent" style="padding:5px; font-size:14px; ">PRODUCT IMAGES :</td> <td> """
                if lst_product_images:
                    for image in lst_product_images:
                        # pass
                        str_html+= """<span><img src=""" +settings.CHAT_URL+image+""" style="float:left;display: block;" width="100px" height="100px"></span>"""

                str_html +="""</td></tr>"""
        # str_html+= """<td style="padding:5px;" bgcolor="transparent"><img src=""" +settings.CHAT_URL+lst_acknowledge[0]+""" style="float:left;display: block;" width="100px" height="100px"></td>"""
        # str_html +="""</td></tr><tr><td bgcolor="transparent" style="padding:5px; font-size:14px; ">REMARKS: </td><td style="padding:5px;" bgcolor="transparent"> """+str(dct_data['vchr_remarks'])+"""</td></tr>
        #     <tr><td bgcolor="transparent" style="padding:5px; font-size:14px; ">WARRANTY: </td><td style="padding:5px;" bgcolor="transparent"> """+str(lst_service_type[dct_data['int_status']])+"""</td></tr>"""
        # if lst_acknowledge:
        #     str_html +="""<tr><td bgcolor="transparent" style="padding:5px; font-size:14px; ">ACKNOWLEDGEMENTS: </td><td style="padding:5px;" bgcolor="transparent"><img src=""" +settings.CHAT_URL+lst_acknowledge+""" style="float:left;display: block;" width="100px" height="100px"></td></tr>"""
        str_html +="""</table>
                         <div class="box2" >

                    <br>
                    <br>

                    <p style="line-height: 1.8;">
                    പരിമിതമായ സമയത്തിനുള്ളിൽ എക്സ്ചേഞ്ച് ചെയ്യുന്ന  ഉപകരണങ്ങൾ വിശദമായ പരിശോധന സാധ്യമല്ലാത്തതിനാൽ വില്പനാന്തരം 48  മണിക്കൂറിനുള്ളിൽ  എക്സ്ചേഞ്ച് ചെയ്യപ്പെടുന്ന ഉപകരണത്തിൽ കാണപ്പെടുന്ന തകരാറുകൾ പരിഹരിക്കാൻ സഹകരിക്കേണ്ട ഉത്തരവാദിത്വം ഉപഭോക്താവിൽ നിക്ഷിപ്തമാണ് </p>
                    <pstyle="line-height: 1.8;>മുകളിൽ കാണിച്ചിരിക്കുന്ന  .............................................................എൻറെ ഉടമസ്ഥതയിൽ ഉള്ളതാണെന്നും വ്യവസ്ഥകൾ അംഗീകരിക്കുന്നതായും ഞാൻ ഇതിനാൽ സാക്ഷ്യപ്പെടുത്തുന്നു . </p>


                    <div style = "margin-top :80px"><span style="font-weight: 600;">CUSTOMER SIGN</span><span style="font-weight: 600;float:right"> SHOP IN CHARGE </span></div>
                </div>
            </div>
        </div>
                    </body>
                    </html>"""

        return str_html
    except Exception as e:
        raise


# def print_invoice(dct_invoice,dct_voucher):
#     try:
#         lst_html_insurance=[]
#         str_mygcare_num = dct_invoice['mygcare_no'] if  dct_invoice['mygcare_no'] else ''
#
#         str_style = """   	<style>
#
#             		table#voucher {
#             				  border-collapse: collapse;
#             				  border-spacing: 0;
#             				  width: 100%;
#             			  }
#
#             	  #voucher th,#voucher td {
#             				  padding: 8px;
#             		     }
#                    body{
#                                                         background: url(/home/sudheesh/Desktop/V0.1.8.5/TBS/static_root/media/duplicate.png);
#                                                         background-size: contain;
#                                                         background-repeat: no-repeat;font-family:Segoe, "Segoe UI", "DejaVu Sans", "Trebuchet MS", Verdana, "sans-serif";
#                                     		          }
#                                     		        h6{
#                                     			        font-size: 0.85em;
#                                     					padding-left: 10px;
#                                     		          }
#                                     		        p{
#                                     			        font-size:17px;
#                                     					word-spacing: 2px;
#                                     					padding-left: 10px;
#                                     					padding-right: 10px;
#                                     		         }
#                                     		.container{
#                                     			         width:1170px;
#                                     			         margin:auto;
#                                     		          }
#                                     		    .clear{
#                                     			         clear:both;
#                                     			      }
#                                     		 .imagebox{
#                                     			         width:100%;
#                                     			         float: left;
#                                     			         border-bottom: 1px solid #c7c2c2;
#                                     			         padding-bottom: 12px;margin-top: 20px;
#                                     		          }
#                                     		    .ibox1{
#                                     				    width: 25%;
#                                     				    float: left;
#
#                                     		          }
#                                     		    .ibox2{
#                                     				    width: 50%;
#                                     				    float: left;
#                                     		          }
#                                     		 .ibox2 h6{
#                                     			       margin-bottom: 0;
#                                                        margin-top: 10px;
#                                     			       padding-left: 0 !important;
#                                     		          }
#
#                                               .ibox2 p{
#                                     			       margin-bottom: 0;
#                                                        margin-top: 5px;
#                                     			       padding-right: 0;
#                                                        padding-left: 0;
#                                 		              }
#                                     		    .ibox3{
#                                     				    width: 25%;
#                                     				    float: left;
#                                     		          }
#                                     		     .box1{
#                                     			        width:100%;
#                                     			        float: left;
#                                     				    padding-bottom: 16px;
#
#                                     		          }
#                                     		 .section1{
#                                     			        width:64%;
#                                     			        float: left;
#                                     		          }
#                                           .section1 h6{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 14px;
#                                     		          }
#                                            .section1 p{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 10px;
#                                     		          }
#                                     		 .section2{
#                                     			        width:32%;
#                                     			        float: right;
#                                     			        text-align: right;
#                                     		          }
#                                     	  .section2 h6{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 14px;
#                                     		          }
#                                            .section2 p{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 10px;
#                                     		          }
#                                     		 .section3{
#                                     					width:50%;
#                                     					float: left;
#
#                                     		          }
#                                           .section3 h6{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 14px;
#                                     		          }
#                                     	   .section3 p{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 10px;
#
#                                     		          }
#                                     		 .section4{
#                                     			        width:50%;
#                                     					float: right;
#                                     		          }
#                                           .section4 h6{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 14px;
#
#                                     		          }
#                                     	   .section4 p{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 10px;
#                                     		          }
#                                                       table{
#                                                       border-collapse:collapse;
#                                                       }
#                                     		        th{
#                                     			        font-weight: 400;
#                                     		          }
#                                                th, td {
#                                                         padding: 15px;
#                                     			        text-align: center;
#                                                       }
#                                     		 .section5{
#                                     			        width:40%;
#                                     					float: right;
#                                     			        text-align: right;
#                                     		          }
#                                     	  .section5 h6{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 14px;
#                                     		            padding-left: 0px !important;
#                                     		            font-size: 16px;
#                                     		          }
#                                     	   .section5 p{
#                                     			        margin-bottom: 0px;
#                                                         margin-top: 10px;
#                                     		          }
#                                     		     .box2{
#                                     			        width:100%;
#                                     			        float: left;
#
#                                     		          }
#                                     		    @page {
#                                     				   size: 7in 9.25in;
#                                     				   margin: 27mm 16mm 27mm 16mm;
#                                                       }
#                                     		        li{
#                                     			       font-size:17px;
#                                     		         }
#                                     		  .header{
#                                     					width:100%;
#                                     					float: left;
#                                                         text-align:center;
#                                     					# color:  #e06a2b;
#
#                                     		          }
#
#                                     		  .invoice{
#
#                                     					background-color: #e06a2b;
#                                     					color: white;
#                                     					padding: 15px 10px 15px 10px;
#
#                                     		         }
#                                     		.innerbox{
#                                     					background: white;
#                                     					width: 100%;
#                                     				}
#
#           	</style>
#             """
#
#
#         html_voucher = ""
#         html_data = ""
#         html_data2 = ""
#         html_returned=""
#         html_credit_note = ""
#         if dct_voucher and dct_voucher['total_amount']:
#             html_voucher = """<!doctype html>
#             <html>
#             <head>
#             <meta charset="utf-8">
#             <title>Untitled Document</title>
#             	<style>
#
#             	.container{
#             			         width:1170px;
#             			         margin:auto;
#
#             		      }
#             	    .clear{
#             			        clear:both;
#             			  }
#             		#voucher .table{
#             				  width: 100%;
#                               border:none;
#                                     }
#
#             	  #voucher th,#voucher td {
#             				  padding: 8px;
#             		     }
#             	</style>"""+str_style+"""
#             </head>
#
#             <body>
#             	<div class="container">
#             		<div class="imagebox">
#
#             		       <div class="ibox1">
#             				   <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
#             			   </div>
#             			   <div class="ibox2">
#
#                             <div style="width:100%;float:left;">
#
#         						<p><span style="font-weight: 600;">ADDRESS  : </span>
#         						"""+str(dct_invoice['branch_address'])+ """</p>
#
#         					 </div>
#
#             				   <div style="width:50%;float:left;">
#
#             					   <div style="width:15%;float:left">
#             					   <p><span style="font-weight: 600;">PH : </span></p>
#             					   </div>
#             					   <div style="width:83%;float: right">
#             						<p>"""+str(dct_voucher['branch_mob'])+"""</p>
#             					   </div>
#
#         				      </div>
#             				     <div style="width:50%;float:right;">
#
#             						 <div style="width:30%;float:left">
#             					   <p><span style="font-weight: 600;">Branch : </span></p>
#             					   </div>
#             					   <div style="width:70%;float: right">
#             						<p>   """
#             if dct_voucher['branch_mob']:
#                 html_voucher+=str(dct_voucher['branch_mob'])
#             else:
#                 html_voucher+="**********"
#             html_voucher+="""</p>
#             					   </div>
#         					</div>
#                         <div style="width:50%;float:left;">
#         					   <div style="width:45%;float:left">
#         					  <p><span style="font-weight: 600;">MYG CARE :</span></p>
#         					   </div>
#         					   <div style="width:54%;float: right">
#         						<p>"""+str(str(str_mygcare_num))+"""</p>
#         					   </div>
#
#         				   </div>
#             				     <div style="width:50%;float:right;">
#             						<div style="width:35%;float:left">
#             					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
#             					   </div>
#             					   <div style="width:65%;float: right">
#             						<p>"""+str(dct_voucher['branch_mail'])+"""</p>
#             					   </div>
#         						 </div>
#             				   <div style="width:100%;float:left;">
#         					    <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
#         				   </div>
#
#             			 </div>
#             			   <div class="ibox3" style="text-align: right;">
#             				   <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
#             				   <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
#             				   <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
#             			   </div>
#
#             		</div>
#                    <br><br><br><br><br><br><br><br><br><br><br><br>
#             		<h4 colspan="3" style="text-align: center;font-size: 20px;text-decoration: underline;color: green;margin-top:10px;">Journal Voucher</h4>
#             		<div class="clear"></div>
#                     <div id="voucher">
#             		    <table border="0" style="width:100%;border:0px !important;border-spacing: 0 !important;">
#
#             					<tbody>
#             						    <tr>
#             								<td style="text-align:left;">To,</td>
#             								<td style="text-align: right;">JV No :</td>
#             								<td style="text-align: right;width: 150px;">"""+dct_voucher['journal_num']+"""</td>
#             						    </tr>
#             						    <tr>
#
#             							    <td style="padding-left: 44px;text-align:left;font-weight:600">"""+dct_voucher['cust_name']+"""</td>
#             								<td style="text-align: right;">JV Date :</td>
#             								<td style="text-align: right;width: 110px;">"""+str(dct_voucher['invoice_date'])+"""</td>
#             						    </tr>"""
#             if dct_voucher['cust_add']:
#                 html_voucher+="""<tr>
#                                          <td colspan="3" style="text-align:left;padding: 3px 3px 3px 44px  !important;"><span style="font-weight: 600;">Address:</span>"""+dct_voucher['cust_add']+""" ,</td>
#                                         </tr>"""
#             html_voucher+="""<tr>
#                                           <td colspan="3" style="text-align:left;padding:3px 3px 10px 44px  !important;"><span style="font-weight: 600;">Phone:</span>&nbsp;"""+str(dct_voucher['cust_mobile'])+"""</td>
#                                         </tr>
#
#             						    <tr style="border-top: 1px solid #e2e2e2;border-bottom: 1px solid #e2e2e2;margin-top:10px;">
#             								<th colspan="2" style="text-align: left;font-weight:600">Particulars</th>
#             								<th style="text-align: right;font-weight:600">Amount</th>
#             						    </tr>"""
#             for voucher_data in dct_voucher['lst_item']:
#                 html_voucher +="""<tr>
#             								 <td colspan="2" style="text-align:left;">"""+voucher_data['item_name']+"""</td>
#             								 <td style="text-align: right">"""+str("{0:.2f}".format(round(voucher_data['amount'],2)))+"""</td>
#             					</tr>"""
#             html_voucher +="""</tbody>
#
#             				 <tfoot>
#
#             					       <tr style="background-color: whitesmoke;">
#             							    <td></td>
#             							    <td style="text-align: right;font-weight: 600;">Total : </td>
#             							    <td style="text-align: right;font-weight: 600;">"""+str("{0:.2f}".format(round(dct_voucher['total_amount'],2)))+"""</td>
#             					       </tr>
#             				 </tfoot>
#             		     </table>
#                          <div>
#             		    <div class="clear"></div>
#             		    <p>"""+dct_voucher['total_amount_in_words']+"""/-</p>
#             		    <div style="width: 25%;float:left;">
#             				 <p style="font-weight: 600;">Entered By</p>
#             		    </div>
#             		    <div style="width: 25%;float:left;">
#             				 <p style="font-weight: 600;">Verified By</p>
#             		    </div>
#             		    <div style="width: 25%;float:left;text-align: right;">
#             				 <p style="font-weight: 600;">Approved By</p>
#             		    </div>
#             		    <div style="width: 25%;float:left;text-align: right;">
#             				 <p style="font-weight: 600;">Recieved By</p>
#             		    </div>
#             	</div>
#
#             </body>
#             </html>
#
#             """
#
#         if dct_invoice['lst_insurance']:
#
#             for ins_insurance in dct_invoice['lst_insurance']:
#                 terms='gdewterms'
#                 for i in range(ins_insurance['qty']):
#
#                     html_insurance = '''<!doctype html>
# <html>
# <head>
# <meta charset="utf-8">
# <title>Untitled Document</title>
# 	<style>
# 		.container{
# 			         width:1170px;
# 			         margin:auto;
# 		          }
# 		    .clear{
# 			         clear: both;
# 		          }
# 		         p{
# 					margin-top: 6px;
# 					margin-bottom: 6px;
# 		          }
#
#                ul {
#                     list-style: none;
# 				    padding-left: 17px;
#                   }
#
#     ul li::before {
# 					  content: "■";
# 					  color: #ffa56e;
# 					  font-weight: bold;
# 					  display: inline-block;
# 					  width: 1em;
# 					  margin-left: -1em;
#                 }
# 		   ul li{
# 			         margin: 5px 0px 5px 0px;
# 		        }
# 		     ol {
#
# 				    padding-left: 17px;
#                 }
#
# 		   ol li{
# 			         margin: 5px 0px 5px 0px;
#
# 		        }
#
#
# 	</style>
# </head>
#
# <body>
# 	<div class="container">
# <!--Image section-->
# 		<div style="width: 33%;float: left">
# 				<div style="width: 27%;float: left;">
# 					<img src="'''+settings.MEDIA_ROOT+'''/3g.png" width="100px">
# 				</div>
# 				<div style="width: 63%">
# 					<img src="'''+settings.MEDIA_ROOT+'''/0.jpg" width="25%">
# 					<img src="'''+settings.MEDIA_ROOT+'''/brandlogo.jpg" width="40%">
# 				</div>
# 		</div>
# 		<div style="width: 33%;float: left;text-align: center;">
# 			<img src="'''+settings.MEDIA_ROOT+'''/gdot.png" width="55%">
# 		</div>
# 		<div style="width: 33%;float: right;text-align: right;">
# 			<img src="'''+settings.MEDIA_ROOT+'''/myglogo.jpg" width="25%">
# 		</div>
# 		<div class="clear"></div>
# <!--Image section ends-->'''
#
#                     if ins_insurance['item_type'] == 'gdot':
#                         html_insurance+='''
# 		<h4 align="center" style="color: green;"><span style="border-bottom: 2px solid orange;">GD</span>OT PROTECTION PLUS CERTIFICATE</h4>'''
#                     else:
#                         html_insurance+='''
#         <h4 align="center" style="color: green;"><span style="border-bottom: 2px solid orange;">GD</span>OT EXTENDED WARRANTY CERTIFICATE</h4>'''
#                     html_insurance+='''
# 	<!--section1 starts-->
# 		<div style="width: 50%;float: left">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Name Of Customer</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: '''+dct_invoice['cust_name'].title()+'''</p>
# 			</div>
# 		</div>
# 		<div style="width: 50%;float: right">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Certificate No</p>
# 			</div>'''
#                     if ins_insurance['item_type'] == 'gdot':
#                         terms='gdotterms'
#                         html_insurance+='''
# 			<div style="width: 70%;float: left">
# 				<p>: '''+ins_insurance['certf_no']+'-'+str(dct_invoice['lst_insurance'].index(ins_insurance)+1)+'-'+(str(i+1))+'''</p>
# 			</div>
# 		</div>'''
#                     else:
#                         html_insurance+='''
#                         <div style="width: 70%;float: left">
# 				<p>: '''+ins_insurance['certf_no']+'-'+str(dct_invoice['lst_insurance'].index(ins_insurance)+1)+'-'+(str(i+1))+'''</p>
# 			</div>
# 		</div>'''
#                     html_insurance+='''
# 		<div class="clear"></div>
#
#
# 		<div class="clear"></div>
#
# 		<div style="width: 50%;float: left">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Contact Number</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: '''+str(dct_invoice['cust_mobile'])+'''</p>
# 			</div>
# 		</div>
# 		<div style="width: 50%;float: right">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Email</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: '''+str(dct_invoice['cust_email'] or '')+'''</p>
# 			</div>
# 		</div>
# 		<div class="clear"></div>
#
# 		<div style="width: 50%;float: left">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Product Category</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: '''+str(ins_insurance['product'])+'''</p>
# 			</div>
# 		</div>
# 		<div style="width: 50%;float: right">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Model</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>:  '''+str(ins_insurance['model'])+'''</p>
# 			</div>
# 		</div>
# 		<div class="clear"></div>
#
# 		<div style="width: 50%;float: left">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Product Brand</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: '''+str(ins_insurance['brand'])+'''</p>
# 			</div>
# 		</div>
# 		<div style="width: 50%;float: right">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">GDP Plus Pack</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: <span>&#x20b9; </span>'''+str(ins_insurance['selling_price'])+'''</p>
# 			</div>
# 		</div>
# 		<div class="clear"></div>
#
# 		<div style="width: 50%;float: left">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Protection Start Date</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: '''+str(ins_insurance['dat_pro_start'])+'''</p>
# 			</div>
# 		</div>
# 		<div style="width: 50%;float: right">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Protection End Date</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: '''+str(ins_insurance['dat_pro_end'])+'''</p>
# 			</div>
# 		</div>
# 		<div class="clear"></div>
#
#
# 		<div style="width: 50%;float: left">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Serial/IMEI No</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: '''+ins_insurance['json_imei'][i]+''' </p>
# 			</div>
# 		</div>
# 		<div style="width: 50%;float: right">
# 			<div style="width: 30%;float: left">
# 				<p style="font-weight:600">Invoice No</p>
# 			</div>
# 			<div style="width: 70%;float: left">
# 				<p>: '''+dct_invoice['invoice_no']+'''</p>
# 			</div>
# 		</div>
# 		<div class="clear"></div>
#
# 		<div style="width: 100%;float: left">
# 			<div style="width: 15%;float: left">
# 				<p style="font-weight:600">Product Value</p>
# 			</div>
# 			<div style="width: 85%;float: left">
# 				<p>: <span>&#x20b9; </span>'''+str(ins_insurance['item_selling_price'])+'''</p>
# 			</div>
# 		</div>
# 		<div class="clear"></div>
#           <div style="width: 100%;float: left">
# 			<div style="width: 15%;float: left">
# 				<p style="font-weight:600">Address</p>
# 			</div>
# 			<div style="width: 85%;float: left">
# 				<p>: '''+str(dct_invoice['cust_add'])+'''</p>
# 			</div>
# 		</div>
#         <div class="clear"></div>
# 	<!--section1 ends-->'''
# #                     if ins_insurance['item_type'] == 'gdot':
# #                         html_insurance+='''
# #
# # <!--section2 Begins-->
# # 		<div style="margin-top: 30px">
# # 			<p style="font-weight: 600;color: #118b98;"><span style="border-bottom: 2px solid #118b98;">Sa</span>lient features of the GDOT Protection Plus</p>
# # 			<p style="color:gray">Loss or damage to handset resulted due to </p>
# # 			<div style="width:50%;float:left;">
# # 				<ol style="padding-left: 15px;">
# # 				  <li>Accidental physical damage</li>
# # 				  <li>Burglary and house breaking</li>
# # 				  <li>Act of god perils</li>
# # 				</ol>
# # 			</div>
# # 			<div style="width:50%;float:right;">
# # 				<ol start="4">
# # 				  <li>Accidental entry of water/fluid</li>
# # 				  <li>Stolen from locked building/room/vehicle by violent or forcible entry</li>
# # 				  <li>Theft following use of violence</li>
# # 				</ol>
# # 			</div>
# # 		</div>
# #
# #
# #
# # <!--section2 ends-->'''
#                     html_insurance+='''
#
# <!--section3 starts-->
# 		<div style="margin-top: 20px">
# 			<p style="font-weight: 600;color: #118b98;"><span style="border-bottom: 2px solid #118b98;">Te</span>rms & Condition</p>
#             <ul>'''
#                     
#                     for index in range(1,len(dct_invoice[terms])+1):
#                         html_insurance+='''<li>'''+dct_invoice[terms][str(index)]+'''</li>'''
#                         html_insurance+='''<br>'''
#                     html_insurance +='''</ul>'''
#
#                     if ins_insurance['item_type'] == 'gdot':
#                         html_insurance+='''<div class="clear"></div>
#                                 <div class="table-responsive print">
#                         					   <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
#                                                         <caption>ANNEXURE 1</caption>
#                               						  <tr style="background-color: #e06a2b;color: white;">
#                                   							<td style="border: 1px solid #cecdcd;text-align:center;">Period in days (ദിവസങ്ങളില്‍)</td><td style="border: 1px solid #cecdcd;text-align:center;">Depreciation(തേയ്മാനം)</td>
#                                                 </tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">0-90</td><td style="text-align:center;border: 1px solid #cecdcd;">15%</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">91-180</td><td style="text-align:center;border: 1px solid #cecdcd;">35%</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">181-270</td><td style="text-align:center;border: 1px solid #cecdcd;">50%</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">271-365</td><td style="text-align:center;border: 1px solid #cecdcd;">60%</td></tr>
#
#                                     </table>
#                                     <br>
#                                     <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
#                                            <caption>ANNEXURE 2</caption>
#                                            <tr style="background-color: #e06a2b;color: white;">
#                                                  <td style="border: 1px solid #cecdcd;">GDP PLUS പരിരക്ഷയുള്ളവ</td>
#                                      </tr>
#                                      <tr><td style="text-align:left;border: 1px solid #cecdcd;">ആകസ്മികമായി ഉണ്ടാകുന്ന ഫിസിക്കല്‍/ലിക്വിഡ് ഡാമേജുകള്‍ ഉദാ: വാഹനാപകടത്തില്‍ സംഭവിക്കുന്നവ,ആക്രമിക്കപ്പെടുന്നതിലൂടെ സംഭവിക്കുന്നവ</td></tr>
#                                      <tr><td style="text-align:left;border: 1px solid #cecdcd;">തീ, ഇടിമിന്നല്‍, പ്രകൃതിക്ഷോഭം കാരണമുണ്ടാകുന്ന ഡാമേജ്(മതിയായ ഗവ: രേഖകള്‍ സഹിതം).</td></tr>
#                                      <tr><td style="text-align:left;border: 1px solid #cecdcd;">ലോക്ക് ചെയ്യപെട്ട റൂമില്‍ നിന്നു ,വാഹനത്തില്‍ നിന്നുണ്ടാകുന്ന മോഷണം.</td></tr>
#                                      <tr><td style="text-align:left;border: 1px solid #cecdcd;">പിടിച്ചുപറി,കൊള്ള കാരണമുള്ള ഡാമേജ്/നഷ്ടപെടല്</td></tr>
#
#                                      </table>
#
#                                      <br>
#                                      <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
#                                             <tr style="background-color: #e06a2b;color: white;">
#                                                   <td style="border: 1px solid #cecdcd;">GDP PLUS പരിരക്ഷയില്ലാത്തവ</td>
#                                       </tr>
#                                       <tr><td style="text-align:left;border: 1px solid #cecdcd;">ഏതെങ്കിലും തരത്തിലുള്ള പോക്കറ്റടി.</td></tr>
#                                       <tr><td style="text-align:left;border: 1px solid #cecdcd;">ഉപഭോക്താവിന്റെ അശ്രദ്ധ കാരണത്താലുണ്ടാകുന്ന മോഷണം/ഡാമേജ് (ഉദാ:ബസ്സില്‍ വച്ച് ഉറങ്ങുന്ന സമയത്തു ഉണ്ടാകുന്ന മോഷണം).</td></tr>
#                                       <tr><td style="text-align:left;border: 1px solid #cecdcd;">ഉപയോഗം മൂലമുണ്ടാകുന്ന തേയ്മാനം.</td></tr>
#                                       <tr><td style="text-align:left;border: 1px solid #cecdcd;">പോറലുകള്‍, ചതവുകള്‍, നിറം മങ്ങല്‍ മുതലായ ഭംഗിപരമായ കേടുപാടുകള്‍(പ്രൊഡക്ടിന്റെ മെയിന്‍ ഫങ്ഷനുകളെ ബാധിക്കാത്ത കേടുപാടുകള്‍ ഉദാ:പ്രൊഡക്ടിന്റെ കെയ്‌സ് പൊട്ടുക പക്ഷെ ഫങ്ഷനുകള്‍ക് ബുദ്ധിമുട്ടാവാത്ത അവസ്ഥ).</td></tr>
#                                       <tr><td style="text-align:left;border: 1px solid #cecdcd;">മനപ്പൂര്‍വം ഉണ്ടാക്കിയതായ ഫിസിക്കല്‍/ലിക്വിഡ് ഡാമേജുകള്‍.</td></tr>
#                                       <tr><td style="text-align:left;border: 1px solid #cecdcd;">മെയിന്‍ പ്രൊഡക്ടിന്റെ കൂടെ വരുന്ന ഒരു തരത്തിലുള്ള ആക്‌സസറീസിനും. ഉദാ: ബാറ്ററി, സിം,ഹെഡ്‌സെറ്റ്,പൗച്, അഡാപ്റ്റര്‍, ചാര്‍ജര്‍,മെമ്മറി കാര്‍ഡ്,സ്‌റ്റൈലസ് etc..</td></tr>
#                                       <tr><td style="text-align:left;border: 1px solid #cecdcd;">അംഗീകൃത സര്‍വിസ് സെന്ററില്‍ നിന്നല്ലാതെ റിപ്പയര്‍ ചെയ്യപ്പെട്ട പ്രൊഡക്ടുകള്‍ക്.</td></tr>
#                                       <tr><td style="text-align:left;border: 1px solid #cecdcd;">സോഫ്ട് വെയര്‍ തകരാറുകള്‍,ഏതെങ്കിലും തരത്തിലുള്ള ഡാറ്റ നഷ്ടപെടല്‍,തേര്‍ഡ് പാര്‍ട്ടി ആപ്പുകള്‍ കാരണമുണ്ടാകുന്ന തകരാറുകള്‍.</td></tr>
#                                       <tr><td style="text-align:left;border: 1px solid #cecdcd;">സോഫ്ട് വെയര്‍ തകരാറുകള്‍,ഏതെങ്കിലും തരത്തിലുള്ള ഡാറ്റ നഷ്ടപെടല്‍,തേര്‍ഡ് പാര്‍ട്ടി ആപ്പുകള്‍ കാരണമുണ്ടാകുന്ന തകരാറുകള്‍.</td></tr>
#
#                                       </table>
#                                 </div>
#                         <div class="clear"></div>'''
#                     elif ins_insurance['item_type'] == 'gdew':
#                         html_insurance+='''<div class="clear"></div>
#                                 <div class="table-responsive print">
#                         					   <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
#                                                       <caption>ANNEXURE 1</caption>
#                               						  <tr style="background-color: #e06a2b;color: white;">
#                                   							<th style="border: 1px solid #cecdcd;"></th>
#                                                             <th style="border: 1px solid #cecdcd;">MOBILE</th>
#                                                             <th style="border: 1px solid #cecdcd;">CAMERA</th>
#                                                             <th style="border: 1px solid #cecdcd;">LAPTOP</th>
#                                                             <th style="border: 1px solid #cecdcd;">TAB</th>
#                                                 </tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">SOFTWARE (OS)</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">DISPLAY</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">PCB</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">CAMERA</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">CAMERA LENS</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">✔</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">COSMETIC</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">LIQUID DAMAGE</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">ALL TYPE OF PHYSICAL DAMAGE</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td></tr>
#                                                 <tr><td style="text-align:center;border: 1px solid #cecdcd;">THEFT</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td><td style="text-align:center;border: 1px solid #cecdcd;">x</td></tr>
#
#                                     </table>
#                                     <br>
#
#                                     <div class="clear"></div>
#                                             <div class="table-responsive print">
#                                     					   <table style="width:100%;border: 1px solid #cecdcd;page-break-inside: avoid !important;">
#                                                                   <caption>ANNEXURE 1</caption>
#                                           						  <tr style="background-color: #e06a2b;color: white;">
#                                               							<th style="border: 1px solid #cecdcd;">PRODUCT PRICE</th>
#                                                                         <th style="border: 1px solid #cecdcd;">PACKAGE</th>
#                                                                         <th style="border: 1px solid #cecdcd;">GDEW</th>
#                                                                         <th style="border: 1px solid #cecdcd;">1st Claim</th>
#                                                             </tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">0-2000</td><td style="text-align:center;border: 1px solid #cecdcd;">199</td><td style="text-align:center;border: 1px solid #cecdcd;">199</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">2001-4000</td><td style="text-align:center;border: 1px solid #cecdcd;">299</td><td style="text-align:center;border: 1px solid #cecdcd;">299</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">4001-10000</td><td style="text-align:center;border: 1px solid #cecdcd;">599</td><td style="text-align:center;border: 1px solid #cecdcd;">599</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">10001-15000</td><td style="text-align:center;border: 1px solid #cecdcd;">899</td><td style="text-align:center;border: 1px solid #cecdcd;">899</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">15001-20000</td><td style="text-align:center;border: 1px solid #cecdcd;">1199</td><td style="text-align:center;border: 1px solid #cecdcd;">1199</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">20001-25000</td><td style="text-align:center;border: 1px solid #cecdcd;">1499</td><td style="text-align:center;border: 1px solid #cecdcd;">1499</td><td style="text-align:center;border: 1px solid #cecdcd;">0</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">25001-30000</td><td style="text-align:center;border: 1px solid #cecdcd;">1999</td><td style="text-align:center;border: 1px solid #cecdcd;">1499</td><td style="text-align:center;border: 1px solid #cecdcd;">500</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">30001-40000</td><td style="text-align:center;border: 1px solid #cecdcd;">2399</td><td style="text-align:center;border: 1px solid #cecdcd;">1899</td><td style="text-align:center;border: 1px solid #cecdcd;">500</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">40001-50000</td><td style="text-align:center;border: 1px solid #cecdcd;">2999</td><td style="text-align:center;border: 1px solid #cecdcd;">2499</td><td style="text-align:center;border: 1px solid #cecdcd;">500</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">50001-60000</td><td style="text-align:center;border: 1px solid #cecdcd;">3599</td><td style="text-align:center;border: 1px solid #cecdcd;">2599</td><td style="text-align:center;border: 1px solid #cecdcd;">1000</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">60001-70000</td><td style="text-align:center;border: 1px solid #cecdcd;">4199</td><td style="text-align:center;border: 1px solid #cecdcd;">2999</td><td style="text-align:center;border: 1px solid #cecdcd;">1200</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">70001-80000</td><td style="text-align:center;border: 1px solid #cecdcd;">4799</td><td style="text-align:center;border: 1px solid #cecdcd;">2999</td><td style="text-align:center;border: 1px solid #cecdcd;">1800</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">80001-90000</td><td style="text-align:center;border: 1px solid #cecdcd;">5399</td><td style="text-align:center;border: 1px solid #cecdcd;">2999</td><td style="text-align:center;border: 1px solid #cecdcd;">2000</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">90001-100000</td><td style="text-align:center;border: 1px solid #cecdcd;">5999</td><td style="text-align:center;border: 1px solid #cecdcd;">3999</td><td style="text-align:center;border: 1px solid #cecdcd;">2400</td></tr>
#                                                             <tr><td style="text-align:center;border: 1px solid #cecdcd;">100001-110000</td><td style="text-align:center;border: 1px solid #cecdcd;">6599</td><td style="text-align:center;border: 1px solid #cecdcd;">3999</td><td style="text-align:center;border: 1px solid #cecdcd;">2600</td></tr>
#
#                                     </table>'''
#             #     html_insurance+='''
# 			# # # <p style="font-weight: 600;margin-top: 25px;color: #118b98;"><span style="border-bottom: 2px solid #118b98;">Ca</span>ses in which GDP PLUS protection available:</p>
# 			# # # <ul>
# 			# # #     <li>Accidental/Liquid damages Eg: (Incidents in vehicle or in case of physical attack )</li>
# 			# # # 	<li>Damages due to Fire, lightning, Natural Calamities (Subject to submission of proper documents) </li>
# 			# # # 	<li>Theft from locked house, room and vehicle</li>
# 			# # # 	<li>Damage/loss due to forceful robbery and burglary.</li>
# 			# # # </ul>
#             # # #
# 			# # # <p style="font-weight: 600;margin-top: 25px;color: #118b98;"><span style="border-bottom: 2px solid #118b98;">Ca</span>ses in which GDP PLUS protection not available:</p>
# 			# # # <ul>
# 			# # #     <li>Any type of pick pocketing</li>
# 			# # # 	<li>Loss due to the carelessness and negligence from the part of the customer ( Eg: lost while sleeping in the vehicle)  </li>
# 			# # # 	<li>Depreciation due the usage</li>
# 			# # # 	<li>Damages which is not affecting the main functioning of the product ,like abrasions ,fading of the color </li>
# 			# # # 	<li>Damages created by deliberate intention by the customer or any one else</li>
# 			# # # 	<li>Accessories attached to the main product like ,Battery, Head set, pouch, Adapter ,charger Memory Card, Etc</li>
# 			# # # 	<li>Product repaired from unauthorized service centers</li>
# 			# # # 	<li>Any kind of software problem, Data ,loss or damage due to the use of any third party apps</li>
# 			# # # 	<li>in which the Manufacturers is not given warranty.</li>
# 			# # </ul>
#                     html_insurance+='''</div>
# <!--section3 ends-->
#
# 	</div>
# </body>
# </html>'''
#
#                     
#                     lst_html_insurance.append(html_insurance)
#         if dct_invoice['lst_item']:
#
#                                 if 'sh_landmark' in dct_invoice :
#                                     html_data ="""<!doctype html>
#                                                                 <html>
#                                                                 <head>
#                                                                 <meta charset="utf-8">
#                                                                 <title>Invoice Format</title>
#                                                                 	<style>
#                             		      body{"""
#                                     if dct_invoice['bln_dup']:
#                                         html_data += """
#                                                 background: url("""+settings.MEDIA_ROOT+"""/duplicate.png);
#                                                 background-size: contain;
#                                                 background-repeat: no-repeat;"""
#                                     html_data += """font-family:Segoe, "Segoe UI", "DejaVu Sans", "Trebuchet MS", Verdana, "sans-serif";
#                             		          }
#                             		        h6{
#                             			        font-size: 0.85em;
#                             					padding-left: 10px;
#                             		          }
#                             		        p{
#                             			        font-size:17px;
#                             					word-spacing: 2px;
#                             					padding-left: 10px;
#                             					padding-right: 10px;
#                             		         }
#                             		.container{
#                             			         width:1170px;
#                             			         margin:auto;
#                             		          }
#                             		    .clear{
#                             			         clear:both;
#                             			      }
#                             		 .imagebox{
#                             			         width:100%;
#                             			         float: left;
#                             			         border-bottom: 1px solid #c7c2c2;
#                             			         padding-bottom: 12px;margin-top: 20px;
#                             		          }
#                             		    .ibox1{
#                             				    width: 25%;
#                             				    float: left;
#
#                             		          }
#                             		    .ibox2{
#                             				    width: 50%;
#                             				    float: left;
#                             		          }
#                             		 .ibox2 h6{
#                             			       margin-bottom: 0;
#                                                margin-top: 10px;
#                             			       padding-left: 0 !important;
#                             		          }
#
#                                       .ibox2 p{
#                             			       margin-bottom: 0;
#                                                margin-top: 5px;
#                             			       padding-right: 0;
#                                                padding-left: 0;
#                         		              }
#                             		    .ibox3{
#                             				    width: 25%;
#                             				    float: left;
#                             		          }
#                             		     .box1{
#                             			        width:100%;
#                             			        float: left;
#                             				    padding-bottom: 16px;
#
#                             		          }
#                             		 .section1{
#                             			        width:64%;
#                             			        float: left;
#                             		          }
#                                   .section1 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#                             		          }
#                                    .section1 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 10px;
#                             		          }
#                             		 .section2{
#                             			        width:32%;
#                             			        float: right;
#                             			        text-align: right;
#                             		          }
#                             	  .section2 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#                             		          }
#                                    .section2 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 10px;
#                             		          }
#                             		 .section3{
#                             					width:50%;
#                             					float: left;
#
#                             		          }
#                                   .section3 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#                             		          }
#                             	   .section3 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 10px;
#
#                             		          }
#                             		 .section4{
#                             			        width:50%;
#                             					float: right;
#                             		          }
#                                   .section4 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#
#                             		          }
#                             	   .section4 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 10px;
#                             		          }
#                                               table{
#                                               border-collapse:collapse;
#                                               }
#                             		        th{
#                             			        font-weight: 400;
#                             		          }
#                                        th, td {
#                                                 padding: 15px;
#                             			        text-align: center;
#                                               }
#                             		 .section5{
#                             			        width:40%;
#                             					float: right;
#                             			        text-align: right;
#                             		          }
#                             	  .section5 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#                             		            padding-left: 0px !important;
#                             		            font-size: 16px;
#                             		          }
#                             	   .section5 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 10px;
#                             		          }
#                             		     .box2{
#                             			        width:100%;
#                             			        float: left;
#
#                             		          }
#                             		    @page {
#                             				   size: 7in 9.25in;
#                             				   margin: 27mm 16mm 27mm 16mm;
#                                               }
#                             		        li{
#                             			       font-size:17px;
#                             		         }
#                             		  .header{
#                             					width:100%;
#                             					float: left;
#                                                 text-align:center;
#                             					# color:  #e06a2b;
#
#                             		          }
#
#                             		  .invoice{
#
#                             					background-color: #e06a2b;
#                             					color: white;
#                             					padding: 15px 10px 15px 10px;
#
#                             		         }
#                             		.innerbox{
#                             					background: white;
#                             					width: 100%;
#                             				}
#                             	</style>
#                             </head>
#
#                             <body>
#                             	<div class="container">
#                             		<div class="header">
#
#                             			        <h3  style="font-size: 25px;margin-top: 0;margin-bottom: 0;padding:10px 10px 10px 10px;">TAX INVOICE </h3>
#                             				<div class="clear"></div>
#                             			</div>
#                             		<div class="imagebox">
#
#                             		       <div class="ibox1">
#                             				   <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
#                             			   </div>
#                             			   <div class="ibox2">
#
#                                          <div style="width:100%;float:left;">
#                         						<div style="width:20%;float:left">
#                         						<p><span style="font-weight: 600;">ADDRESS  : </span></p>
#                         						</div>
#                         						<div style="width:79%;float: right">
#                         						<p> """+str(dct_invoice['branch_address'])+"""</p>
#                         						</div>
#                         					 </div>
#
#                             				   <div style="width:50%;float:left;">
#
#                             					   <div style="width:15%;float:left">
#                             					   <p><span style="font-weight: 600;">PH : </span></p>
#                             					   </div>
#                             					   <div style="width:83%;float: right">
#                             						<p>  0487 234566</p>
#                             					   </div>
#
#                         				   </div>
#                             				     <div style="width:50%;float:right;">
#
#                             						 <div style="width:25%;float:left">
#                             					   <p><span style="font-weight: 600;">MOB : </span></p>
#                             					   </div>
#                             					   <div style="width:73%;float: right">
#                             						<p>   """
#                                     if dct_invoice['branch_mob']:
#                                         html_data+=str(dct_invoice['branch_mob'])
#                                     else:
#                                         html_data+="**********"
#                                     html_data+="""</p>
#                             					   </div>
#                         					</div>
#                                         <div style="width:50%;float:left;">
#                         					   <div style="width:45%;float:left">
#                         					  <p><span style="font-weight: 600;">MYG CARE : </span></p>
#                         					   </div>
#                         					   <div style="width:54%;float: right">
#                         						<p>"""+str(str_mygcare_num)+""" </p>
#                         					   </div>
#
#                         				   </div>
#                             				     <div style="width:50%;float:right;">
#                             						<div style="width:35%;float:left">
#                             					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
#                             					   </div>
#                             					   <div style="width:65%;float: right">
#                             						<p>"""+str(dct_invoice['branch_mail'])+"""</p>
#                             					   </div>
#                         						 </div>
#                             				   <div style="width:100%;float:left;">
#                         					    <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
#                         				   </div>
#
#                             			 </div>
#                             			   <div class="ibox3" style="text-align: right;">
#                             				   <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
#                             				   <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
#                             				   <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
#                             			   </div>
#
#                             		</div>
#
#
#
#
#
#                             	    <div style="float: left;width: 100%;">
#
#
#                             		    <div class="box1" style="border-bottom: 1px solid #c7c2c2;">
#                             				<div class="section1">
#
#
#
#                             				</div>
#                             				<div class="section2">"""
#                                     if dct_invoice.get('fin_name'):
#                                         html_data += """<div style="width:40%;float:left;"><p>Financier :</p></div>
#                                 					<div style="width:60%;float:right;font-weight:600"><p>"""+dct_invoice['fin_name']+"""</p></div>
#                                 					<div class="clear"></div>"""
#                                     html_data+=	"""<div style="width:40%;float:left;"><p>Invoice No :</p></div>
#                             					<div style="width:60%;float:right;font-weight:600"><p>"""+dct_invoice['invoice_no']+"""</p></div>
#                             					<div class="clear"></div>
#
#                             					<div style="width: 40%;float:left;"><p>Invoice Date :</p></div>
#                             					<div style="width:60%;float:right;font-weight:600"><p> """+str(dct_invoice['invoice_date'])+""" </p></div>
#                             					<div class="clear"></div>
#
#                             					<div style="width: 40%;float:left;"><p>Invoice Time :</p></div>
#                             					<div style="width:60%;float:right;font-weight:600"><p> """+str(dct_invoice['invoice_time'])+"""</p></div>
#                             					<div class="clear"></div>
#                             					<div style="width:40%;float:left;"><p>State :</p></div>
#                             					<div style="width:60%;float:right;font-weight:600"><p> """+dct_invoice['cust_state'].title()+""" ("""+dct_invoice['cust_state_code']+""")</p></div>
#                             					<div class="clear"></div>"""
#
#
#                                     if dct_invoice['staff']:
#                                         html_data += """<div style="width: 40%;float:left;"><p>Sales Person :</p></div>
#                                 					<div style="width:60%;float:right;font-weight:600"><p> """+dct_invoice['staff'].title()+"""</p></div>
#                                 					<div class="clear"></div>"""
#
#                                     html_data +="""</div>
#                             			</div>
#                             			<div class="clear"></div>
#                             			 <div class="box1">
#                                                 <div class="section3">
#                             						<div style="border-right: 1px solid #c7c2c2;">
#                             							 <div style="width:100%;float: left;"><h6 style="border-bottom: 1px solid #c7c2c2;padding-bottom: 6px;color: green;">BILLED TO</h6></div>
#
#                             						     <div style="width:30%;float: left;"><h6>CUSTOMER NAME</h6></div>
#                             						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_name'].title()+"""</p></div>
#                             						     <div class="clear"></div>"""
#                                     if dct_invoice['cust_add']:
#                                         html_data +=""" <div style="width:30%;float: left;"><h6>ADDRESS</h6></div>
#                             						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_add']+"""</p></div>
#                             						     <div class="clear"></div>"""
#                                     # if dct_invoice['cust_add']:
#                                     #     html_data +="""   <div style="width:30%;float: left;"><h6>CITY PIN CODE</h6></div>
#                             		# 				     <div style="width:70%;float:right;"><p>: """+"""680307"""+"""</p></div>
#                             		# 				     <div class="clear"></div>"""
#                                     html_data +="""	     <div style="width:30%;float: left;"><h6>MOB NO</h6></div>
#                             						     <div style="width:70%;float:right;"><p>: """+str(dct_invoice['cust_mobile'])+"""</p></div>
#                             						     <div class="clear"></div>"""
#                                     if dct_invoice['cust_gst']:
#                                         html_data +="""  <div style="width:30%;float: left;"><h6>GSTN NO</h6></div>
#                             						     <div style="width:70%;float:right;"><p>: """+str(dct_invoice['cust_gst'])+"""</p></div>
#                             						     <div class="clear"></div>"""
#                                     if dct_invoice['cust_state']:
#                                         html_data +="""  <div style="width:30%;float: left;"><h6>STATE</h6></div>
#                             						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_state'].title()+"""/"""+dct_invoice['cust_state_code']+"""</p></div>
#                             						     <div class="clear"></div>"""
#
#                                     html_data +="""</div>
#                                     		    </div>
#
#                                     		       <div class="section4">
#                                     					 <div style="width:100%;float: left;"><h6 style="border-bottom: 1px solid #c7c2c2;padding-bottom: 6px;color: green;">SHIPPED TO</h6></div>
#
#                                     				     <div style="width:30%;float: left;"><h6>Name</h6></div>
#                                     				     <div style="width:70%;float:right;"><p>: """+dct_invoice['sh_cust_name'].title()+"""</p></div>
#                                     				     <div class="clear"></div>"""
#                                     if dct_invoice['sh_cust_add']:
#                                         html_data +=""" <div style="width:30%;float: left;"><h6>Address</h6></div>
#                                     				     <div style="width:70%;float:right;"><p>: """+dct_invoice['sh_cust_add']+"""</p></div>
#                                     				     <div class="clear"></div>"""
#                                     if 'sh_landmark' in dct_invoice:
#                                         html_data +=""" <div style="width:30%;float: left;"><h6>Landmark</h6></div>
#                                     				     <div style="width:70%;float:right;"><p>: """+dct_invoice['sh_landmark']+"""</p></div>
#                                     				     <div class="clear"></div>"""
#                                     # html_data +="""<div style="width:30%;float: left;"><h6>CITY PIN CODE</h6></div>
#                                     # 				     <div style="width:70%;float:right;"><p>: 680307</p></div>
#                                     # 				     <div class="clear"></div>
#
#                                     html_data +="""<div style="width:30%;float: left;"><h6>MOB No</h6></div>
#                                     				    <div style="width:70%;float:right;"><p>: """+str(dct_invoice['sh_cust_mobile'])+"""</p></div>
#                                     				    <div class="clear"></div>"""
#                                     if dct_invoice['sh_cust_gst']:
#                                         html_data +=""" <div style="width:30%;float: left;"><h6>GSTN No</h6></div>
#                                     				    <div style="width:70%;float:right;"><p>: """+str(dct_invoice['sh_cust_gst'])+"""</p></div>
#                                     				    <div class="clear"></div>"""
#                                     if dct_invoice['cust_state']:
#                                         html_data +=""" <div style="width:30%;float: left;"><h6>State</h6></div>
#                                     				    <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_state'].title()+"""/"""+dct_invoice['cust_state_code']+"""</p></div>
#                                     				    <div class="clear"></div>"""
#
#                                     html_data +="""</div>
#                                              </div>
#                                     	             <div class="clear"></div>
#                                     	              <div class="table-responsive print">
#                                     					  <table style="width:100%;border: 1px solid #cecdcd;">
#
#                                     						  <tr style="background-color: #e06a2b;color: white;">
#                                     							<th style="border: 1px solid #cecdcd;">SLNO</th>
#                                     							<th style="border: 1px solid #cecdcd;">ITEM DESCRIPTION/DETAIL</th>
#                                     							<th style="border: 1px solid #cecdcd;">HSN/SAC</th>
#                                     							<th style="border: 1px solid #cecdcd;">QTY</th>
#                                     							<th style="border: 1px solid #cecdcd;">RATE</th>
#                                     						    <th style="border: 1px solid #cecdcd;">DIS./BB</th>"""
#                                     if dct_invoice['bln_igst']:
#                                         html_data +="""<th style="border: 1px solid #cecdcd;">IGST %</th>"""
#                                     else:
#                                         html_data +="""
#                                     							<th style="border: 1px solid #cecdcd;">SGST %</th>
#                             									<th style="border: 1px solid #cecdcd;">CGST %</th>"""
#                                     html_data +="""<th style="border: 1px solid #cecdcd;">GROSS AMOUNT</th>
#                             								  </tr>"""
#                                     int_index = 1
#                                     for str_item in dct_invoice['lst_item']:
#                                         html_data +="""<tr>		<td style="border: 1px solid #cecdcd;">"""+str(int_index)+"""</td>
#                             									<td style="text-align:left;border: 1px solid #cecdcd;">"""+str_item['item']
#                                         if str_item['str_imei']:
#                                             html_data +="""<br>Imei:-"""+str_item['str_imei']
#                                         html_data +="""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['hsn_code'])+"""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['qty'])+"""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str("{0:.2f}".format(round(str_item['amount'],2)))+"""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str("{0:.2f}".format(round(str_item['discount']+str_item['buyback'],2)))+"""</td>"""
#                                         if dct_invoice['bln_igst']:
#                                             html_data +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['igst'])+"""</td>"""
#                                         else:
#                                             html_data +="""	<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['sgst'])+"""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['cgst'])+"""</td>"""
#                                         html_data +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str("{0:.2f}".format(round(str_item['amount'],2)))+"""</td>
#                             								  </tr>"""
#                                         int_index +=1
#                                     html_data+="""</table>
#                             						  </div>
#                             			           <div class="clear"></div>
#                             			        <div class="box2">
#                             						   <div class="section5">
#                             							   <div style="margin-top: 10px;">"""
#                                     for dct_tax in dct_invoice['tax']:
#                                         for str_tax in dct_invoice['tax'][dct_tax]:
#                                             if dct_invoice['bln_igst']:
#                                                 if dct_tax.upper() == 'IGST':
#                                                     html_data+="""<div style="width:60%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
#                                     						        <div style="width:40%;float:right;"><p>"""+str("{0:.2f}".format(round(dct_invoice['tax'][dct_tax][str_tax],2)))+"""</p></div>
#                                     						        <div class="clear"></div>"""
#                                             else:
#                                                 if dct_tax.upper() in ['CGST','SGST']:
#                                                     html_data+="""<div style="width:60%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
#                                     						        <div style="width:40%;float:right;"><p>"""+str("{0:.2f}".format(round(dct_invoice['tax'][dct_tax][str_tax],2)))+"""</p></div>
#                                     						        <div class="clear"></div>"""
#
#                             							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> SGST 9% :</p></div>
#                             						        # <div style="width:65%;float:right;"><p>0.00</p></div>
#                             						        # <div class="clear"></div>
#                                                             #
#                             							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> CGST 6% :</p></div>
#                             						        # <div style="width:65%;float:right;"><p>0.00</p></div>
#                             						        # <div class="clear"></div>
#                                                             #
#                             							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> SGST 6% :</p></div>
#                             						        # <div style="width:65%;float:right;"><p>0.00</p></div>
#                             						        # <div class="clear"></div>
#                                     if dct_invoice['bln_kfc']:
#                                         html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(+) </span>KERALA FLOOD CESS(1%) :</p></div>
#                                         <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['dbl_kfc'],2)))+"""</p></div>
#                                         <div class="clear"></div>"""
#                                     if dct_invoice['dct_addition_data']:
#                                         for key,value in dct_invoice['dct_addition_data'].items():
#                                              html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(+) </span>"""+str(key)+"""  :</p></div>
#                                                 <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(float(value),2)))+"""</p></div>
#                                                 <div class="clear"></div>"""
#
#                                     if dct_invoice['dct_deduction_data']:
#                                         for key,value in dct_invoice['dct_deduction_data'].items():
#                                              html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(-) </span>"""+str(key)+"""  :</p></div>
#                                                 <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(float(value),2)))+"""</p></div>
#                                                 <div class="clear"></div>"""
#
#                                     if dct_invoice['service_charge']:
#                                         html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(+) </span>PROCESSING CHARGE :</p></div>
#                                         <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['service_charge'],2)))+"""</p></div>
#                                         <div class="clear"></div>"""
#
#                                     html_data+="""<div style="padding-bottom: 12px;background-color: #ffede3;margin-top: 12px;padding-right:2px;">
#                             									<div style="width:60%;float: left;"><p>SUB TOTAL :</p></div>
#                             									<div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['total']+dct_invoice['flt_add_ded_total'],2)))+"""</p></div>
#                             									<div class="clear"></div>"""
#
#                                     if dct_invoice['coupon']:
#                                         html_data+="""<div style="width:60%;float: left;"><p>COUPON AMOUNT :</p></div>
#                             									<div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['coupon'],2)))+"""</p></div>
#                             									<div class="clear"></div>"""
#
#                                     if dct_invoice['loyalty']:
#                                         html_data+="""<div style="width:60%;float: left;"><p>LOYALTY AMOUNT :</p></div>
#                             									<div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['loyalty'],2)))+"""</p></div>
#                             									<div class="clear"></div>"""
#                                     if 0 and dct_invoice['buyback']:
#                                         html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(-) </span>BUYBACK AMOUNT :</p></div>
#                             									<div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['buyback'],2)))+"""</p></div>
#                             									<div class="clear"></div>"""
#                                     dbl_total = round(dct_invoice['total']+dct_invoice['flt_add_ded_total']-dct_invoice['coupon']-dct_invoice['loyalty'],2)
#                                     dbl_total_rounded = round(dct_invoice['total']+dct_invoice['flt_add_ded_total']-dct_invoice['coupon']-dct_invoice['loyalty'])
#                                     p = inflect.engine()
#                                     vchr_amount = p.number_to_words(dbl_total_rounded).title() +' Rupees only.'
#                                     dbl_round_off = round(dbl_total_rounded - dbl_total,2)
#                                     if dbl_round_off != 0.0:
#                                         html_data+="""<div style="width:60%;float: left;"><p>ROUNDING OFF :</p></div>
#                         							  <div style="width:40%;float:right;"><p> """+str(dbl_round_off)+"""</p></div>
#                             						  <div class="clear"></div>"""
#
#                                     html_data+="""<div style="width:60%;float: left;"><p style="margin-top: 5px;"><b>TOTAL : </b></p></div>
#                             					  <div style="width:40%;float:right;"><p style="margin-top: 4px;"><b> """+str("{0:.2f}".format(round(dbl_total_rounded,2)))+""" </b></p></div>
#                             					  <div class="clear"></div>
#                             							  </div>
#                             							   </div>
#                             						 </div></div>
#
#                                                      <div style="width:90%;float: left;"><p style="margin-top: 5px;"><b>TOTAL(in words) :  &nbsp&nbsp&nbsp"""+str(vchr_amount)+"""</b></p></div>
#                                                      """
#
#                                     if dct_invoice.get('lst_payment_details'):
#                                         html_data+= """ <div class="box2" style="border-top: 1px solid #c7c2c2;padding-top:10px;  padding-bottom:10px">"""+dct_invoice['lst_payment_details']+"""</div>"""
#                                     html_data+= """ <div class="box2" style="border-top: 1px solid #c7c2c2;">
#                             						   <p style="font-weight: 600;">TERMS / CONDITIONS:</p>
#                             							<ul style="list-style-type:disc;"> """
#
#                                     
#                                     if dct_invoice['terms']:
#                                         for dct_terms in ['invoice-A','invoice-B','invoice-C']:
#                                             for index in range(1,len(dct_invoice['terms'][dct_terms])+1):
#                                                 if index==1:
#                                                     html_data+="""<p style="text-align:center;color:#fa5e07;">"""+dct_invoice['terms'][dct_terms][str(index)]+"""</p><br>"""
#                                                 elif dct_terms.upper() == 'INVOICE-A' and index==2:
#                                                     html_data+="""<p style="text-align:center;color:#055f7a;">"""+dct_invoice['terms'][dct_terms][str(index)]+"""</p><br>"""
#                                                 else:
#                                                 # if 1:
#                                                     html_data+="""<li style="font-weight:5000px">"""+dct_invoice['terms'][dct_terms][str(index)]+"""</li>"""
#                                                     html_data+="""<br>"""
#                                     html_data +="""</ul>
#                                                     </div>
#                             			          </div>
#                             		        </div>
#                             	     </div>
#
#                             </body>
#                             </html> """
#                                 else:
#                                     html_data2 = html_voucher+"""<!doctype html>
#                             <html>
#                             <head>
#                             <meta charset="utf-8">
#                             <title>Invoice Format</title>
#                             	<style>
#                             		      body{"""
#                                     if dct_invoice['bln_dup']:
#                                         html_data2 += """
#                                                 background: url("""+settings.MEDIA_ROOT+"""/duplicate.png);
#                                                 background-size: contain;
#                                                 background-repeat: no-repeat;"""
#                                     html_data2 += """font-family:Segoe, "Segoe UI", "DejaVu Sans", "Trebuchet MS", Verdana, "sans-serif";
#
#                             		          }
#                             		        h6{
#                             			        font-size: 0.85em;
#                             					padding-left: 10px;
#                             		          }
#                             		        p{
#                             			        font-size:17px;
#                             					word-spacing: 2px;
#                             					padding-left: 10px;
#                             					padding-right: 10px;
#                             		         }
#                             		.container{
#                             			         width:1170px;
#                             			         margin:auto;
#                             		          }
#                             		    .clear{
#                             			         clear:both;
#                             			      }
#                             		 .imagebox{
#                             			         width:100%;
#                             			         float: left;
#                             			         border-bottom: 1px solid #c7c2c2;
#                             			         padding-bottom: 12px;margin-top: 20px;
#                             		          }
#                             		    .ibox1{
#                             				    width: 25%;
#                             				    float: left;
#
#                             		          }
#                             		    .ibox2{
#                             				    width: 50%;
#                             				    float: left;
#                             		          }
#                             		 .ibox2 h6{
#                             			       margin-bottom: 0;
#                                                margin-top: 10px;
#                             			       padding-left: 0 !important;
#                             		          }
#                             		  .ibox2 p{
#                             			       margin-bottom: 0;
#                                                margin-top: 5px;
#                             			       padding-right: 0;
#                                                padding-left: 0;
#                         		              }
#                             		    .ibox3{
#                             				    width: 25%;
#                             				    float: left;
#                             		          }
#                             		     .box1{
#                             			        width:100%;
#                             			        float: left;
#                             				    padding-bottom: 16px;
#
#                             		          }
#                             		 .section1{
#                             			        width:50%;
#                             			        float: left;
#                             			        margin-top: 10px;
#                             		          }
#                                   .section1 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#                             		          }
#                                    .section1 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 5px;
#                             		            color: gray;
#                             		          }
#                             		 .section2{
#                             			        width:40%;
#                             			        float: right;
#                             			        margin-top: 10px;
#                             			        text-align: right;
#                             		          }
#                             	  .section2 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#                             		          }
#                                    .section2 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 10px;
#                             		          }
#                             		 .section3{
#                             					width:50%;
#                             					float: left;
#
#                             		          }
#                                   .section3 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#                             		          }
#                             	   .section3 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 10px;
#                             		          }
#                             		 .section4{
#                             			        width:50%;
#                             					float: right;
#                             		          }
#                                   .section4 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#
#                             		          }
#                             	   .section4 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 10px;
#                             		          }
#                             	         table{
#                             				   border-collapse: collapse;
#                                               }
#                             		        th{
#
#                             					font-weight: 400;
#                             		          }
#                                        th, td {
#                                                 padding: 15px;
#                             			        text-align: center;
#                                               }
#                             		 .section5{
#                             			        width:40%;
#                             					float: right;
#                             			        text-align: right;
#                             		          }
#                             	  .section5 h6{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 14px;
#                             		            padding-left: 0px !important;
#                             		            font-size: 16px;
#                             		          }
#                             	   .section5 p{
#                             			        margin-bottom: 0px;
#                                                 margin-top: 10px;
#
#                             		          }
#                             		     .box2{
#                             			        width:100%;
#                             			        float: left;
#
#                             		          }
#                             		    @page {
#                             				   size: 7in 9.25in;
#                             				   margin: 27mm 16mm 27mm 16mm;
#                                               }
#                             		        li{
#                             			       font-size:17px;
#                             		          }
#                             		   .header{
#                             					width:100%;
#                             					float: left;
#                                 				color: #e06a2b;
#                                                 text-align:center;
#
#                             		          }
#
#                             		  .invoice{
#
#                             					background-color: #e06a2b;
#                             					color: white;
#                             					padding: 15px 10px 15px 10px;
#
#                             		         }
#                             		.innerbox{
#                             			    background: white;
#                             				width: 100%;
#                             				}
#                             	</style>
#                             </head>
#
#                             <body>
#
#                             	<div class="container">
#                             		<div class="header">
#
#                             			        <h3  style="font-size: 25px;margin-top: 0;margin-bottom: 0;padding:10px 10px 10px 10px;">INVOICE </h3>
#                             				<div class="clear"></div>
#                             			</div>
#                             		<div class="imagebox">
#
#                             		       <div class="ibox1">
#                             				   <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
#                             			   </div>
#                             			   <div class="ibox2">
#
#                                          <div style="width:100%;float:left;">
#
#                                                 <div style="width:20%;float:left">
#                         						<p><span style="font-weight: 600;">ADDRESS  : </span></p>
#                         						</div>
#                         						<div style="width:79%;float: right">
#                         						<p> """+str(dct_invoice['branch_address'])+"""</p>
#                         						</div>
#
#                         					 </div>
#
#                             				   <div style="width:50%;float:left;">
#
#                             					   <div style="width:15%;float:left">
#                             					   <p><span style="font-weight: 600;">PH : </span></p>
#                             					   </div>
#                             					   <div style="width:83%;float: right">
#                             						<p>"""+str(dct_voucher['branch_mob'])+"""</p>
#                             					   </div>
#
#                         				   </div>
#                             				     <div style="width:50%;float:right;">
#
#                             						 <div style="width:25%;float:left">
#                             					   <p><span style="font-weight: 600;">MOB : </span></p>
#                             					   </div>
#                             					   <div style="width:73%;float: right">
#                             						<p>   """
#                                     if dct_invoice['branch_mob']:
#                                         html_data2+=str(dct_invoice['branch_mob'])
#                                     else:
#                                         html_data2+="**********"
#                                     html_data2+="""</p>
#                             					   </div>
#                         					</div>
#                                         <div style="width:50%;float:left;">
#                         					   <div style="width:45%;float:left">
#                         					  <p><span style="font-weight: 600;">MYG CARE : </span></p>
#                         					   </div>
#                         					   <div style="width:54%;float: right">
#                         						<p> """+str(str_mygcare_num)+""" </p>
#                         					   </div>
#
#                         				   </div>
#                             				     <div style="width:50%;float:right;">
#                             						<div style="width:35%;float:left">
#                             					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
#                             					   </div>
#                             					   <div style="width:65%;float: right">
#                             						<p>"""+str(dct_invoice['branch_mail'])+"""</p>
#                             					   </div>
#                         						 </div>
#                             				   <div style="width:100%;float:left;">
#                         					    <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
#                         				   </div>
#
#                             			 </div>
#                             			   <div class="ibox3" style="text-align: right;">
#                             				   <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
#
#                             				   <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
#                             				   <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
#
#                             			   </div>
#
#                             		</div>
#
#
#
#
#
#                             	    <div style="float: left;width: 100%;">
#
#
#                             		    <div class="box1">
#                             				<div class="section1">
#                             					<div>	<p style="color: gray;">SHIPPING ADDRESS </p></div>
#
#
#
#
#
#
#                             					        <div style="width:100%;float:left;"><p style="font-weight: 600;color: black"> """+dct_invoice['cust_name'].title()+"""</p></div>
#                             						     <div class="clear"></div>
#
#
#                             						     <div style="width:100%;float:left;"><p> """+dct_invoice['cust_add']+"""</p></div>
#                             						     <div class="clear"></div>
#
#
#                             <!--
#                             						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_name'].title()+"""</p></div>
#                             						     <div class="clear"></div>
#
#                             						     <div style="width:30%;float: left;"><h6>ADRESS 1</h6></div>
#                             						     <div style="width:70%;float:right;"><p>: J D Tower, Opp. Reliance Fresh, KSRTC Road, Chalakudy, Thrissur, Kerala ,India, Chalakudy, Kerala 680307</p></div>
#                             						     <div class="clear"></div>
#
#                             -->
#
#
#                             <!--						     <div style="width:30%;float: left;"><h6>CITY PIN CODE</h6></div>-->
#                             <!--
#                             <!--						     <div style="width:100%;float:left;"><p> 680307</p></div>-->
#                             						     <div class="clear"></div>
#
#
#                             <!--						     <div style="width:30%;float: left;"><h6>MOB NO</h6></div>-->
#                             						     <div style="width:100%;float:left;"><p> """+str(dct_invoice['cust_mobile'])+"""</p></div>
#                             						     <div class="clear"></div>
#
#                             <!--						     <div style="width:30%;float: left;"><h6>GSTN NO</h6></div>-->
#                             						     <div style="width:100%;float:left;"><p> """+str(dct_invoice['cust_gst'])+"""</p></div>
#                             						     <div class="clear"></div>
#
#                             <!--						     <div style="width:30%;float: left;"><h6>STATE</h6></div>-->
#                             						     <div style="width:100%;float:left;"><p> """+dct_invoice['cust_state'].title()+"""/"""+dct_invoice['cust_state_code']+"""</p></div>
#                             						     <div class="clear"></div>
#
#
#                             				</div>
#                             				<div class="section2">
#
#                             					<div style="width:50%;float:left;"><p>Invoice No :</p></div>
#                             					<div style="width:50%;float:right;font-weight:600"><p> """+dct_invoice['invoice_no']+"""</p></div>
#                             					<div class="clear"></div>
#
#                             					<div style="width: 50%;float:left;"><p>Invoice Date :</p></div>
#                             					<div style="width:50%;float:right;font-weight:600"><p> """+dct_invoice['invoice_date']+""" </p></div>
#                             					<div class="clear"></div>
#
#                             					<div style="width: 50%;float:left;"><p>Invoice Time :</p></div>
#                             					<div style="width:50%;float:right;font-weight:600"><p>"""+dct_invoice['invoice_time']+"""</p></div>
#                             					<div class="clear"></div>
#                             					<div style="width:50%;float:left;"><p>State :</p></div>
#                             					<div style="width:50%;float:right;font-weight:600"><p> """+dct_invoice['cust_state'].title()+""" ("""+dct_invoice['cust_state_code']+""")</p></div>
#                             					<div class="clear"></div>"""
#
#                                     if dct_invoice['staff']:
#                                         html_data2 +="""<div style="width: 50%;float:left;"><p>Sales Person :</p></div>
#                             					<div style="width:50%;float:right;font-weight:600"><p> """+dct_invoice['staff'].title()+"""</p></div>
#                             					<div class="clear"></div>"""
#
#                                     html_data2+="""</div>
#                             			</div>
#                             			<div class="clear"></div>
#
#
#                             			              <div class="table-responsive">
#                             							  <table style="width:100%;border: 1px solid #cecdcd;">
#
#                             								  <tr style="background-color: #e06a2b;color: white;">
#                             									<th style="border: 1px solid #cecdcd;">SLNO</th>
#                             									<th style="border: 1px solid #cecdcd;">ITEM DESCRIPTION/DETAIL</th>
#                             									<th style="border: 1px solid #cecdcd;">HSN/SAC</th>
#                             									<th style="border: 1px solid #cecdcd;">QTY</th>
#                             									<th style="border: 1px solid #cecdcd;">RATE</th>
#                             									<th style="border: 1px solid #cecdcd;">DISCOUNT</th>"""
#                                     if dct_invoice['bln_igst']:
#                                         html_data2 +="""<th style="border: 1px solid #cecdcd;">IGST %</th>"""
#                                     else:
#                                         html_data2 +="""<th style="border: 1px solid #cecdcd;">SGST %</th>
#                             							<th style="border: 1px solid #cecdcd;">CGST %</th>"""
#                                     html_data2 +="""<th>GROSS AMOUNT</th>
#                             								  </tr>"""
#                                     int_index = 1
#                                     for str_item in dct_invoice['lst_item']:
#                                         html_data2+="""<tr>		<td style="border: 1px solid #cecdcd;">"""+str(int_index)+"""</td>
#                             									<td style="text-align:left;border: 1px solid #cecdcd;">"""+str_item['item']+"""<br>Imei:-"""+str_item['str_imei']+"""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str_item['hsn_code']+"""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['qty'])+"""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['amount'])+"""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['discount'])+"""</td>"""
#                                         if dct_invoice['bln_igst']:
#                                             html_data2 +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['igst'])+"""</th>"""
#                                         else:
#                                             html_data2 +="""	<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['sgst'])+"""</td>
#                             									<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['cgst'])+"""</td>"""
#                                         html_data2 +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(str_item['total'])+"""</td>
#                             								  </tr>"""
#                                         int_index +=1
#
#                                     html_data2 +="""</table>
#                             						  </div>
#                             			           <div class="clear"></div>
#                             			           <div class="box2">
#                             						   <div class="section5">
#                             							   <div style="margin-top: 10px;">"""
#                                     for dct_tax in dct_invoice['tax']:
#                                         for str_tax in dct_invoice['tax'][dct_tax]:
#                                             if dct_invoice['bln_igst']:
#                                                 if dct_tax.upper() == 'IGST':
#                                                     html_data2+="""<div style="width:50%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
#                                     						        <div style="width:50%;float:right;"><p>"""+str(dct_invoice['tax'][dct_tax][str_tax])+"""</p></div>
#                                     						        <div class="clear"></div>"""
#                                             else:
#                                                 if dct_tax.upper() in ['CGST','SGST']:
#                                                     html_data2+="""<div style="width:50%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
#                                     						        <div style="width:50%;float:right;"><p>"""+str(dct_invoice['tax'][dct_tax][str_tax])+"""</p></div>
#                                     						        <div class="clear"></div>"""
#                             							    # <div style="width:35%;float: left;">  <p><span style="font-size: 13px">(+) </span>CGST 9% :</p></div>
#                             						        # <div style="width:65%;float:right;"><p>0.00</p></div>
#                             						        # <div class="clear"></div>
#                                                             #
#                             							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> SGST 9% :</p></div>
#                             						        # <div style="width:65%;float:right;"><p>0.00</p></div>
#                             						        # <div class="clear"></div>
#                                                             #
#                             							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> CGST 6% :</p></div>
#                             						        # <div style="width:65%;float:right;"><p>0.00</p></div>
#                             						        # <div class="clear"></div>
#                                                             #
#                             							    # <div style="width:35%;float: left;"><p><span style="font-size: 13px">(+) </span> SGST 6% :</p></div>
#                             						        # <div style="width:65%;float:right;"><p>0.00</p></div>
#                             						        # <div class="clear"></div>
#
#                                     html_data2+="""<div style="padding-bottom: 12px;background-color: #ffede3;margin-top: 12px;padding-right: 10px;">
#                             									<div style="width:50%;float: left;"><p>SUB TOTAL :</p></div>
#                             									<div style="width:50%;float:right;"><p> """+str(round(dct_invoice['total'],2))+"""</p></div>
#                             									<div class="clear"></div>
#
#
#                             									<div style="width:50%;float: left;"><p>COUPON AMOUNT :</p></div>
#                             									<div style="width:50%;float:right;"><p> """+str(dct_invoice['coupon'])+"""</p></div>
#                             									<div class="clear"></div>
#
#
#                             									<div style="width:50%;float: left;"><p>LOYALTY AMOUNT :</p></div>
#                             									<div style="width:50%;float:right;"><p> """+str(dct_invoice['loyalty'])+"""</p></div>
#                             									<div class="clear"></div>
#
#
#                             									<div style="width:50%;float: left;"><p><span style="font-size: 13px">(-) </span>BUYBACK AMOUNT :</p></div>
#                             									<div style="width:50%;float:right;"><p> """+str(dct_invoice['buyback'])+"""</p></div>
#                             									<div class="clear"></div>"""
#                                     # if dct_invoice['indirect_discount']:
#                                     #     html_data2+="""<div style="width:50%;float: left;"><p>VOUCHER AMOUNT:</p></div>
#                             		# 							<div style="width:50%;float:right;"><p> """+str(round(dct_invoice['indirect_discount'],2))+"""</p></div>
#                             		# 							<div class="clear"></div>"""
#
#                                     html_data2+="""	<div style="width:50%;float: left;"><p style="margin-top: 5px;"><b>TOTAL : </b></p></div>
#                             									<div style="width:50%;float:right;"><p style="margin-top: 4px;"><b> """+str(round(dct_invoice['total']-dct_invoice['buyback']-dct_invoice['coupon']-dct_invoice['loyalty'],2))+""" </b></p></div>
#                             									<div class="clear"></div>
#                             							  </div>
#                             							   </div>
#                             						 </div>
#                             		               </div>
#                             			           <div class="box2" style="border-top: 1px solid #c7c2c2;">
#
#                             						   <p style="font-weight: 600;">TERMS / CONDITIONS:</p>
#
#                             							<ul style="list-style-type:disc;">"""
#                                     for index in range(1,len(dct_invoice['terms'])+1):
#                                         html_data2+="""<li>"""+dct_invoice['terms'][str(index)]+"""</li>"""
#                                         html_data+="""<br>"""
#
#                                     html_data2 +="""</ul>
#                                                     </div>"""
#                                     # if dct_invoice['bln_dup']:
#                                     #     html_data2 +="""<div><p style="color:red;">Duplicate</p></div>"""
#                                     html_data2+="""</div>
#                             		        </div>
#                             	     </div>
#                             </body>
#                             </html> """
#
#         if dct_invoice['lst_returned']:
#
#             html_returned = """<!doctype html>
#                                 <html>
#                                 <head>
#                                 <meta charset="utf-8">
#                                 <title>Untitled Document</title>
#                                 	<style>
#                                 .imagebox{
#                                                      width:100%;
#                                                      float: left;
#                                                      border-bottom: 1px solid #c7c2c2;
#                                                      padding-bottom: 12px;margin-top: 20px;
#                                                   }
#
#                                     @media print {
#                                           .new-page {
#                                             page-break-before: always;
#                                           }
#                                         }
#                                 	.container{
#                                 			         width:1170px;
#                                 			         margin:auto;
#
#                                 		      }
#                                 	    .clear{
#                                 			        clear:both;
#                                 			  }
#                                 		table#voucher {
#
#                                 				  width: 100%;
#
#                                 			  }
#
#                                 	  #voucher th,#voucher td {
#                                 				  padding: 8px;
#                                 		     }
#                                 		table#sales {
#
#                                 				  width: 100%;
#
#                                 			  }
#
#                                 	  #sales th,#sales td {
#                                 				  padding: 8px;
#                                 		          text-align: left;
#                                 		     }
#                                     .ibox1{
#                                                     width: 25%;
#                                                     float: left;
#
#                                                   }
#                                             .ibox2{
#                                                     width: 50%;
#                                                     float: left;
#                                                   }
#                      .ibox2 h6{
#                                        margin-bottom: 0;
#                                        margin-top: 10px;
#                                        padding-left: 0 !important;
#                                       }
#                               .ibox2 p{
#                                        margin-bottom: 0;
#                                        margin-top: 5px;
#                                        padding-right: 0;
#                                        padding-left: 0;
#                                       }
#                                 .ibox3{
#                                         width: 25%;
#                                         float: left;
#                                       }
#
#                                 	</style>"""+str_style+"""
#                                 </head>
#
#                                 <body>
#                                 	<div class="container" >
#                                 			                            		<div class="header">
#
#                                                                         			        <h3  style="font-size: 25px;margin-top: 0;margin-bottom: 0;padding:10px 10px 10px 10px;">SALE RETURN NOTE </h3>
#                                                                         				<div class="clear"></div>
#                                                                         			</div>
#                                                                         		<div class="imagebox">
#
#                                                                         		       <div class="ibox1">
#                                                                         				   <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
#                                                                         			   </div>
#                                                                         			   <div class="ibox2">
#
#                                                                                      <div style="width:100%;float:left;">
#                                                                     						<div style="width:20%;float:left">
#                                                                     						<p><span style="font-weight: 600;">ADDRESS  : </span></p>
#                                                                     						</div>
#                                                                     						<div style="width:79%;float: right">
#                                                                     						<p>"""+str(dct_invoice['branch_address'])+ """</p>
#                                                                     						</div>
#                                                                     					 </div>
#
#                                                                         				   <div style="width:50%;float:left;">
#
#                                                                         					   <div style="width:15%;float:left">
#                                                                         					   <p><span style="font-weight: 600;">PH : </span></p>
#                                                                         					   </div>
#                                                                         					   <div style="width:83%;float: right">
#                                                                         						<p>"""+str(dct_voucher['branch_mob'])+"""</p>
#                                                                         					   </div>
#
#                                                                     				   </div>
#                                                                         				     <div style="width:50%;float:right;">
#
#                                                                         						 <div style="width:25%;float:left">
#                                                                         					   <p><span style="font-weight: 600;">MOB : </span></p>
#                                                                         					   </div>
#                                                                         					   <div style="width:73%;float: right">
#                                                                         						<p>   """+str(dct_invoice['branch_mob'] or "**********")+"""</p>
#                                                                         					   </div>
#                                                                     					</div>
#                                                                                     <div style="width:50%;float:left;">
#                                                                     					   <div style="width:45%;float:left">
#                                                                     					  <p><span style="font-weight: 600;">MYG CARE : </span></p>
#                                                                     					   </div>
#                                                                     					   <div style="width:54%;float: right">
#                                                                     						<p> """ +str(str_mygcare_num)+"""</p>
#                                                                     					   </div>
#
#                                                                     				   </div>
#                                                                         				     <div style="width:50%;float:right;">
#                                                                         						<div style="width:35%;float:left">
#                                                                         					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
#                                                                         					   </div>
#                                                                         					   <div style="width:65%;float: right">
#                                                                         						<p>"""+str(dct_invoice['branch_mail'])+"""</p>
#                                                                         					   </div>
#                                                                     						 </div>
#                                                                         				   <div style="width:100%;float:left;">
#                                                                     					    <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
#                                                                     				   </div>
#
#                                                                         			 </div>
#                                                                         			   <div class="ibox3" style="text-align: right;">
#                                                                         				   <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
#
#                                                                         				   <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
#                                                                         				   <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
#
#                                                                         			   </div>
#
#                                                                         		</div>
#
#
#                                 		    <table id="voucher">
#                                 					<tbody>
#                                 						    <tr>
#                                 								<td style="text-align: left;padding: 3px !important;">Received From ,</td>
#                                 								<td style="text-align: right;padding: 3px !important;">SRN No :</td>
#                                 								<td style="text-align: right;width: 110px;padding: 3px !important;font-weight: 600;">"""+str(dct_invoice['srn_no'])+ """</td>
#                                 						    </tr>
#                                 						    <tr>
#
#                                 							    <td style="text-align: left;padding: 3px 3px 3px 44px !important;">"""+str((dct_invoice['sh_cust_name'] or '-----'))+"""</td>
#                                 								<td style="text-align: right;padding: 3px !important;">SRN Date :</td>
#                                 								<td style="text-align: right;width: 110px;padding: 3px !important;font-weight: 600;">"""+datetime.strftime(dct_invoice['srn_date'],'%d-%m-%Y')+"""</td>
#                                 						    </tr>
#                                 						    <tr>
#
#                                 							    <td style="text-align: left;padding:3px 3px 3px 44px  !important;">GSTIN:&nbsp;<span style="font-weight: 600;">"""+(dct_invoice['sh_cust_gst'] or '------')+"""</span>,</td>
#                                 								<td style="text-align: right;padding: 3px 3px 3px 44px  !important;">State/Code :</td>
#                                 								<td style="text-align: right;width: 110px;padding: 3px 3px 3px 44px !important;font-weight: 600;">"""+(dct_invoice['state'] or '-----')+'/'+(dct_invoice['state_code'] or '---')+"""</td>
#                                 						    </tr>
#                                 						    <tr>
#                                 								 <td style="text-align: left;padding:3px 3px 3px 44px  !important;">Phone No:&nbsp;<span style="font-weight: 600;">"""+str(dct_invoice['sh_cust_mobile'] or '**********')+"""</span>,&nbsp;Address:&nbsp;<span style="font-weight: 600;">"""+str(dct_invoice['sh_cust_add'])+"""</span>
#                                 								</td>
#                                 							</tr>
#
#
#                                 					</tbody>
#
#                                 		     </table>
#                                 		     <table id="sales" style="margin-top: 20px;">
#                                 				      <thead>
#                                 						  <tr style="background-color: whitesmoke;">
#                                 								  <th>SNO</th>
#                                 								  <th>Particulars</th>
#                                 								  <th style="text-align: right">HSN/SAC</th>
#                                 								  <th style="text-align: right">Qty</th>
#                                 								  <th style="text-align: right">Rate</th>
#                                 								  <th style="text-align: right">Dis%</th>
#                                 								  <th style="text-align: right">Dis/BB</th>
#                                 								  <th style="text-align: right">CGST</th>
#                                 								  <th style="text-align: right">SGST</th>
#                                 								  <th style="text-align:right;">Amount</th>
#                                 						  </tr>
#                                 				      </thead>
#                                 				      <tbody>"""
#             int_count=0
#             dbl_cgst_tot=0
#             dbl_sgst_tot=0
#             dbl_kfc_tot=0
#             dbl_amount_tot=0
#             dbl_igst_tot=0
#             lst_already=[]
#             for data in dct_invoice['lst_returned']:
#                 #
#                 if 1 or data['str_imei']  not in lst_already:
#                     lst_already.append(data['str_imei'])
#                     int_count += 1
#                     dbl_cgst_tot+=data['cgst']
#                     dbl_sgst_tot += data['sgst']
#                     dbl_igst_tot += data['igst']
#                     dbl_kfc_tot += data['kfc']
#                     dbl_amount_tot += data['amount']
#
#
#                     if not data['igstp']:
#                         html_returned += """       						   <tr>
#                                             							   <td>"""+str(int_count)+"""</td>
#                                             							   <td>"""+(data['item'] or '')+""" <br>
#                                             								    CGST 	"""+str(data['cgstp'] or '')+"""%<br>
#                                             									SGST 	"""+str(data['sgstp'] or '' )+"""%<br>
#                                             									KFC 	"""+str(data['kfcp'] or '0.00')+"""%
#                                                                            </td>"""
#                         html_returned +="""        							   <td style="text-align: right">"""+(data['vchr_hsn_code'] or '')+"""</td>
#                                             							   <td style="text-align: right">"""+str(data['qty'])+"""</td>
#                                             							   <td style="text-align: right">"""+str("{0:.2f}".format(round(data['amount'],2)))+"""</td>
#                                             							   <td style="text-align: right"></td>
#                                             							   <td style="text-align: right">"""+str(data['discount']+data['buyback'])+"""</td>
#                                             							   <td style="text-align: right">"""+str(data['cgstp'])+"""</td>
#                                             							   <td style="text-align: right">"""+str(data['sgstp'])+""" </td>
#                                             							   <td style="text-align: right">"""+str("{0:.2f}".format(round(data['amount'],2)))+"""<br><br>
#                                             								   """+str("{0:.2f}".format(round(data['cgst'],2)))+"""<br>
#                                             								   """+str("{0:.2f}".format(round(data['sgst'],2)))+"""<br>
#                                             								   """+str("{0:.2f}".format(round(data['kfc'],2)))+"""
#                                             							   </td>
#                                         						   </tr>"""
#
#
#                     else:
#
#                         html_returned += """       						   <tr>
#                                             							   <td>"""+str(int_count)+"""</td>
#                                             							   <td>"""+(data['item'] or '')+""" <br>
#                                             								    IGST 	"""+str(data['igstp'])+"""%<br>
#                                             									KFC 	"""+str(data['kfcp'] or '')+"""%
#                                                                            </td>"""
#                         html_returned +="""        							   <td style="text-align: right">"""+(data['vchr_hsn_code'] or '')+"""</td>
#                                             							   <td style="text-align: right">"""+str(data['qty'])+"""</td>
#                                             							   <td style="text-align: right">"""+str("{0:.2f}".format(round(data['amount']-data['igst']-data['kfc'],2)))+"""</td>
#                                             							   <td style="text-align: right"></td>
#                                             							   <td style="text-align: right"></td>
#                                             							   <td style="text-align: right">"""+str(data['igstp'])+"""</td>
#                                                                            <td style="text-align: right"></td>
#                                             							   <td style="text-align: right">"""+str("{0:.2f}".format(round(data['amount']-data['igst']-data['kfc'],2)))+"""<br><br>
#                                             								   """+str("{0:.2f}".format(round(data['igst'],2)))+"""<br>
#                                             								   """+str("{0:.2f}".format(round(data['kfc'],2)))+"""
#                                             							   </td>
#                                         						   </tr>"""
#
#
#             html_returned +="""     				      </tbody>
#
#                                 				      <tfoot>
#
#                                 					       <tr style="background-color: whitesmoke;">
#
#                                 							    <td colspan="3" style="text-align: left;font-weight: 600;color: #213fad;">Total </td>
#                                 							    <td style="text-align: right;font-weight: 600;color: #213fad;"></td>
#                                 							    <td colspan="6" style="text-align: right;font-weight: 600;color: #213fad;">"""+str("{0:.2f}".format(round(abs(dct_invoice['return_amount']),2)))+"""</td>
#                                 					       </tr>
#                                 				     </tfoot>
#                                 		     </table>
#                                 		    <div class="clear"></div>
#                                 		    <p>"""+str(dct_invoice['return_amount_words'])+"""  only/-</p>"""
#             if dct_invoice['invoice_num_returned']:
#                 html_returned +=""" <p>Notes:Ref.  <br>Sales Invoice No. """+str(dct_invoice['invoice_num_returned'])+"""<br>dt."""+str(datetime.strftime(dct_invoice['dat_invoice_returned'],'%d-%m-%Y'))+"""</p>"""
#             html_returned +="""<div style="width: 50%;float:left;">
#                                 				 <p style="font-weight: 600;">Receivers Signature</p>
#                                 		    </div>
#                                 		    <div style="width: 50%;float:right;text-align: right">
#                                 				 <p style="font-weight: 600;">For MyG</p>
#                                 				 <p style="margin-top: 30px">Authorized Signatory</p>
#                                 		    </div>
#
#                                 	</div>
#
#
#                                 </body>
#                                     </html"""
#
#
#             html_credit_note= """<!doctype html>
#                                 <html>
#                                 <head>
#                                 <meta charset="utf-8">
#                                 <title>Untitled Document</title>
#                                 	<style>
#
#                                 	.container{
#                                 			         width:1170px;
#                                 			         margin:auto;
#
#                                 		      }
#                                 	    .clear{
#                                 			        clear:both;
#                                 			  }
#                                 		table#voucher {
#                                 				  border-collapse: collapse;
#                                 				  border-spacing: 0;
#                                 				  width: 100%;
#
#                                 			  }
#
#                                 	  #voucher th,#voucher td {
#                                 				  padding: 8px;
#                                 		     }
#                                 	</style>"""+str_style+"""
#                                 </head>
#
#                                 <body>
#                                 	<div class="container">
#                                     <br>
#                                     <br>
#                                 			                            		<div class="header">
#
#                                                                         			        <h3  style="font-size: 25px;margin-top: 0;margin-bottom: 0;padding:10px 10px 10px 10px;">CREDIT&nbsp;NOTE </h3>
#                                                                         				<div class="clear"></div>
#                                                                         			</div>
#                                                                         		<div class="imagebox">
#
#                                                                         		       <div class="ibox1">
#                                                                         				   <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
#                                                                         			   </div>
#                                                                         			   <div class="ibox2">
#
#                                                                                      <div style="width:100%;float:left;">
#                                                                     						<div style="width:20%;float:left">
#                                                                     						<p><span style="font-weight: 600;">ADDRESS  : </span></p>
#                                                                     						</div>
#                                                                     						<div style="width:79%;float: right">
#                                                                     						<p>"""+str(dct_invoice['branch_address'])+ """</p>
#                                                                     						</div>
#                                                                     					 </div>
#
#                                                                         				   <div style="width:50%;float:left;">
#
#                                                                         					   <div style="width:15%;float:left">
#                                                                         					   <p><span style="font-weight: 600;">PH : </span></p>
#                                                                         					   </div>
#                                                                         					   <div style="width:83%;float: right">
#                                                                         						<p>"""+str(dct_voucher['branch_mob'])+"""</p>
#                                                                         					   </div>
#
#                                                                     				   </div>
#                                                                         				     <div style="width:50%;float:right;">
#
#                                                                         						 <div style="width:25%;float:left">
#                                                                         					   <p><span style="font-weight: 600;">MOB : </span></p>
#                                                                         					   </div>
#                                                                         					   <div style="width:73%;float: right">
#                                                                         						<p>   """+str(dct_invoice['branch_mob'] or "**********")+"""</p>
#                                                                         					   </div>
#                                                                     					</div>
#                                                                                     <div style="width:50%;float:left;">
#                                                                     					   <div style="width:45%;float:left">
#                                                                     					  <p><span style="font-weight: 600;">MYG CARE : </span></p>
#                                                                     					   </div>
#                                                                     					   <div style="width:54%;float: right">
#                                                                     						<p>"""+str(str_mygcare_num)+""" </p>
#                                                                     					   </div>
#
#                                                                     				   </div>
#                                                                         				     <div style="width:50%;float:right;">
#                                                                         						<div style="width:35%;float:left">
#                                                                         					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
#                                                                         					   </div>
#                                                                         					   <div style="width:65%;float: right">
#                                                                         						<p>"""+str(dct_invoice['branch_mail'])+"""</p>
#                                                                         					   </div>
#                                                                     						 </div>
#                                                                         				   <div style="width:100%;float:left;">
#                                                                     					    <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_invoice['branch_GSTIN'])+"""</p>
#                                                                     				   </div>
#
#                                                                         			 </div>
#                                                                         			   <div class="ibox3" style="text-align: right;">
#                                                                         				   <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
#
#                                                                         				   <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
#                                                                         				   <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
#
#                                                                         			   </div>
#
#                                                                         		</div>
#
#                                 		    <table id="voucher">
#                                 					<tbody>
#                                 						    <tr>
#                                 								<td style="text-align: left;padding: 3px !important;">To,</td>
#                                 								<td style="text-align: right;">CRN No :</td>
#                                 								<td style="text-align: right;width: 110px;font-weight: 600;">"""+dct_invoice['srn_no'].replace('SRN-','CR-',1)+"""</td>
#                                 						    </tr>
#                                 						    <tr>
#
#                                 							    <td style="text-align: left;padding: 3px 3px 3px 44px !important;font-weight: 600;">"""+dct_invoice['sh_cust_name']+"""</td>
#                                 								<td style="text-align: right;">CRN Date :</td>
#                                 								<td style="text-align: right;width: 110px;font-weight: 600;">"""+datetime.strftime(dct_invoice['srn_date'],'%d-%m-%Y')+"""</td>
#                                 						    </tr>
#                                 						  <tr>
#
#                                 							    <td  style="text-align: left;padding: 3px 3px 3px 44px !important;">"""+dct_invoice['sh_cust_add']+"""</td>
#                                 								<td style="text-align: right;">Ref. Doc. No.:</td>
#                                 								<td style="text-align: right;width: 110px;font-weight: 600;">"""+dct_invoice['invoice_num_returned']+"""</td>
#                                 						    </tr>
#
#                                 						    <tr style="border-top: 1px solid #e2e2e2;border-bottom: 1px solid #e2e2e2;">
#                                 								<th colspan="2" style="text-align: left;">Particulars</th>
#                                 								<th style="text-align: right">Amount</th>
#                                 						    </tr>
#                                                             <tr>
#                                 								 <td colspan="2" style="text-align: left">Sales Return A/c.</td>
#                                 								 <td style="text-align: right">"""+str("{0:.2f}".format(round(dbl_amount_tot,2)))+"""</td>
#                                 						    </tr>"""
#             if dbl_igst_tot>0:
#                 html_credit_note += """                       <tr>
#                                 								<td colspan="2" style="text-align: left">Output IGST A/c.</td>
#                                 								<td style="text-align: right">"""+str("{0:.2f}".format(round(dbl_igst_tot,2)))+"""</td>
#                                 						    </tr>"""
#
#             else:
#                 html_credit_note +="""
#                                 						    <tr>
#                                 								<td colspan="2" style="text-align: left">Output CGST A/c.</td>
#                                 								<td style="text-align: right">"""+ str("{0:.2f}".format(round(dbl_cgst_tot,2)))+"""</td>
#                                 						    </tr>
#                                 						    <tr>
#                                 								<td colspan="2" style="text-align: left">Output SGST A/c.</td>
#                                 								<td style="text-align: right">"""+ str("{0:.2f}".format(round(dbl_sgst_tot,2)))+"""</td>
#                                 						    </tr>"""
#             html_credit_note +="""
#                                 						    <tr>
#                                 								<td colspan="2" style="text-align: left">Kerala Flood Cess</td>
#                                 								<td style="text-align: right">"""+str("{0:.2f}".format(round(dbl_kfc_tot,2)))+"""</td>
#                                 						    </tr>
#                                 						    <tr>
#                                 								<td colspan="2" style="text-align: left">Action(Credit Note issued) taken for the Sales</td>
#
#                                 						    </tr>
#                                 						 <tr>
#                                 								<td colspan="2" style="text-align: left">Return Note : """+dct_invoice['srn_no']+""" dt. """+datetime.strftime(dct_invoice['srn_date'],'%d-%m-%Y')+"""</td>
#
#                                 						    </tr>
#                                 					</tbody>
#
#                                 				 <tfoot>
#
#                                 					       <tr style="background-color: whitesmoke;">
#                                 							    <td></td>
#                                 							    <td style="text-align: right;font-weight: 600;">Total : </td>
#                                 							    <td style="text-align: right;font-weight: 600;">"""+str("{0:.2f}".format(round(dct_invoice['return_amount'],2)))+"""</td>
#                                 					       </tr>
#                                 				 </tfoot>
#                                 		     </table>
#                                 		    <div class="clear"></div>
#                                 		    <p>Rupees : """+dct_invoice['return_amount_words']+"""/-</p>
#                                 		    <div style="width: 50%;float:left;">
#                                 				 <p style="font-weight: 600;">Receivers Signature</p>
#                                 		    </div>
#
#                                 		    <div style="width: 50%;float:left;text-align: right;">
#                                 				 <p style="font-weight: 600;">For MyG</p><br><br><br>
#                                 				 <p style="font-weight: 600;">Authorised Signatory</p>
#                                 		    </div>
#                                 	</div>
#                                 </body>
#                                 </html>"""
#         file_path = settings.MEDIA_ROOT
#         # str_base_path = settings.MEDIA_ROOT+'/schemes'
#         if not os.path.exists(file_path):
#             os.makedirs(file_path)
#         # ==================================================================================================
#
#         options = {'margin-top': '10.00mm',
#                    'margin-right': '10.00mm',
#                    'margin-bottom': '10.00mm',
#                    'margin-left': '10.00mm',
#                    'dpi':400,
#                    }
#
#         lst_pdfs = []
#
#         if html_voucher:
#             str_file_name = 'voucher.pdf'
#             filename_voucher =  file_path+'/'+str_file_name
#             pdfkit.from_string(html_voucher,filename_voucher,options=options)
#             lst_pdfs.append(filename_voucher)
#         if html_data or html_data2:
#             str_file_name = 'invoice.pdf'
#             filename_inovice =  file_path+'/'+str_file_name
#             if html_data2:
#                 html_data = html_data2
#             pdfkit.from_string(html_data,filename_inovice,options=options)
#             lst_pdfs.append(filename_inovice)
#         if html_returned:
#             str_file_name = 'sales_return.pdf'
#             filename_return =  file_path+'/'+str_file_name
#             pdfkit.from_string(html_returned,filename_return,options=options)
#             lst_pdfs.append(filename_return)
#         if html_credit_note:
#             str_file_name = 'credit.pdf'
#             filename_credit =  file_path+'/'+str_file_name
#             pdfkit.from_string(html_credit_note,filename_credit,options=options)
#             lst_pdfs.append(filename_credit)
#         if lst_html_insurance:
#
#             for ins_html_insurance in lst_html_insurance:
#                 filename= "insurance"+str(lst_html_insurance.index(ins_html_insurance))
#                 str_file_name = filename+'.pdf'
#                 filename_insurance =  file_path+'/'+str_file_name
#                 pdfkit.from_string(ins_html_insurance,filename_insurance,options=options)
#                 lst_pdfs.append(filename_insurance)
#         # To merge all pdf to one
#         pdf_writer = PdfFileWriter()
#         for path in lst_pdfs:
#             pdf_reader = PdfFileReader(path)
#             for page in range(pdf_reader.getNumPages()):
#                 pdf_writer.addPage(pdf_reader.getPage(page))
#
#         str_file_name = 'invoice-'+dct_invoice['invoice_no']+'-'+dct_invoice['invoice_date']+'.pdf'
#         filename =  file_path+'/'+str_file_name
#         with open(filename, 'wb') as fh:
#             pdf_writer.write(fh)
#
#
#         # =================================Old code=================================================================
#         #
#         # str_file_name = 'invoice-'+dct_invoice['invoice_no']+'-'+dct_invoice['invoice_date']+'.pdf'
#         # filename =  file_path+'/'+str_file_name
#         # options = {'margin-top': '10.00mm',
#         #            'margin-right': '10.00mm',
#         #            'margin-bottom': '10.00mm',
#         #            'margin-left': '10.00mm',
#         #            'dpi':400,
#         #            }
#         # # if dct_invoice['sh_cust_name']:
#         # #     pdfkit.from_string(html_data,filename,options=options)
#         # # else:
#         #     # filename =  file_path+'/invoice-'+dct_invoice['invoice_no']+dct_invoice['invoice_date']+'.pdf'
#         # if dct_invoice['lst_item']:
#         #     if 'sh_landmark' in dct_invoice:
#         #         if html_returned:
#         #
#         #             html_data=html_data + html_returned + html_credit_note
#         #         pdfkit.from_string(html_data,filename,options=options)
#         #     else:
#         #         if html_returned:
#         #             html_data2=html_data2 + html_returned + html_credit_note
#         #
#         #         pdfkit.from_string(html_data2,filename,options=options)
#         # elif dct_invoice['lst_returned']:
#         #     html_returned += html_credit_note
#         #     pdfkit.from_string(html_returned,filename,options=options)
# # ===================================================================================================================
#
#         fs = FileSystemStorage()
#         # lst_file =[filename]
#         # lst_encoded_string=[]
#         encoded_string = ''
#         # for filename in lst_file:
#         if fs.exists(filename):
#             with fs.open(filename) as pdf:
#                 encoded_string=str(base64.b64encode(pdf.read()))
#                 # lst_encoded_string.append(str(base64.b64encode(pdf.read())))
#         file_details = {}
#         file_details['file'] = encoded_string
#         file_details['file_name'] = str_file_name
#         return file_details
#     except Exception as e:
#         raise



class InvoiceList(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            
            dat_to = (datetime.strptime(request.data.get("datTo"),'%Y-%m-%d')).date()
            dat_from = (datetime.strptime(request.data.get("datFrom"),'%Y-%m-%d')).date()
            # ins_invoice = None
            # ins_jio_sales = None
            # if request.data.get("datTo") and request.data.get("datFrom"):
            #     ins_invoice = SalesDetails.objects.filter(fk_master__dat_invoice__gte=dat_from,fk_master__dat_invoice__lte=dat_to)
            #     ins_jio_sales = SalesMasterJio.objects.filter(dat_invoice__gte=dat_from,dat_invoice__lte=dat_to)
            # if request.data.get("intPhone"):
            #     ins_invoice = ins_invoice.filter(fk_master__fk_customer__int_mobile=request.data['intPhone'])
            #     ins_jio_sales = ins_jio_sales.filter(fk_customer__int_mobile=request.data['intPhone'])
            #
            # if request.data.get('intBrandId'):
            #     ins_invoice = ins_invoice.filter(fk_item__fk_brand_id = request.data.get('intBrandId'))
            #     ins_jio_sales = ins_jio_sales.filter(fk_item__fk_brand_id = request.data.get('intBrandId'))
            # if request.data.get('intItemId'):
            #     ins_invoice = ins_invoice.filter(fk_item_id = request.data.get('intItemId'))
            #     ins_jio_sales = ins_jio_sales.filter(fk_item_id = request.data.get('intItemId'))
            # if request.data.get('intProductId'):
            #     ins_invoice = ins_invoice.filter(fk_item__fk_product_id = request.data.get('intProductId'))
            #     ins_jio_sales = ins_jio_sales.filter(fk_item__fk_product_id = request.data.get('intProductId'))
            # if request.data.get('intStaffId'):
            #     ins_invoice = ins_invoice.filter(fk_master__fk_staff_id = request.data.get('intStaffId'))
            #     ins_jio_sales = ins_jio_sales.filter(fk_staff_id = request.data.get('intStaffId'))
            #
            # ins_invoice = ins_invoice.values('fk_master_id','fk_master__fk_customer__int_mobile','fk_master__fk_customer__vchr_name','fk_master__fk_branch__vchr_name','fk_master__dat_invoice','fk_master__fk_staff__first_name','fk_master__fk_staff__last_name','fk_master__vchr_invoice_num','fk_item__fk_product__vchr_name').order_by("-fk_master__vchr_invoice_num")
            # ins_jio_sales = ins_jio_sales.values('fk_customer__int_mobile','fk_customer__vchr_name','fk_branch__vchr_name','dat_invoice','fk_staff__first_name','fk_staff__last_name','vchr_invoice_num','fk_item__fk_product__vchr_name').order_by("-vchr_invoice_num")

            session = Connection()
            

            lst_service_id = list(set(SalesDetails.objects.filter(int_sales_status=3,fk_master__dat_invoice__gte=dat_from,fk_master__dat_invoice__lte=dat_to).values_list('fk_master_id',flat=True)))
            if request.data.get('blnReturn'):
                rst_invoice = session.query(SalesMasterSA.pk_bint_id.label('int_id'),SalesDetailsSA.int_sales_status.label('int_sales_status'),SalesMasterSA.dat_invoice.label('dat_invoice'),SalesReturnSA.vchr_doc_code.label('str_inv_num'),SalesMasterSA.dat_created.label('dat_created'),BranchSA.vchr_name.label('str_branch_name'),\
                                SalesCustomerDetailsSA.vchr_name.label('vchr_gst_no'),SalesCustomerDetailsSA.vchr_name.label('str_cust_name'),SalesCustomerDetailsSA.int_mobile.label('int_mobile'),func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('str_staff_name'),ProductsSA.vchr_name.label('str_product_name'),func.coalesce(False).label('bln_jio_invoice'))\
                                .join(SalesDetailsSA, SalesDetailsSA.fk_master_id == SalesMasterSA.pk_bint_id)\
                                .join(BranchSA, BranchSA.pk_bint_id == SalesMasterSA.fk_branch_id)\
                                .join(SalesCustomerDetailsSA, SalesCustomerDetailsSA.pk_bint_id == SalesMasterSA.fk_customer_id)\
                                .join(AuthUserSA, AuthUserSA.id == SalesMasterSA.fk_staff_id)\
                                .join(ItemsSA, ItemsSA.pk_bint_id == SalesDetailsSA.fk_item_id)\
                                .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                                .join(SalesReturnSA,SalesReturnSA.fk_sales_id == SalesMasterSA.pk_bint_id)\
                                .filter(cast(SalesMasterSA.dat_created,Date) >= dat_from,cast(SalesMasterSA.dat_created,Date) <= dat_to,SalesDetailsSA.int_sales_status==0)
            elif request.data.get('blnService'):
                rst_invoice = session.query(SalesMasterSA.pk_bint_id.label('int_id'),SalesDetailsSA.int_sales_status.label('int_sales_status'),SalesMasterSA.dat_invoice.label('dat_invoice'),SalesMasterSA.vchr_invoice_num.label('str_inv_num'),SalesMasterSA.dat_created.label('dat_created'),BranchSA.vchr_name.label('str_branch_name'),\
                                SalesCustomerDetailsSA.vchr_name.label('vchr_gst_no'),SalesCustomerDetailsSA.vchr_name.label('str_cust_name'),SalesCustomerDetailsSA.int_mobile.label('int_mobile'),func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('str_staff_name'),ProductsSA.vchr_name.label('str_product_name'),func.coalesce(False).label('bln_jio_invoice'))\
                                .join(SalesDetailsSA, SalesDetailsSA.fk_master_id == SalesMasterSA.pk_bint_id)\
                                .join(BranchSA, BranchSA.pk_bint_id == SalesMasterSA.fk_branch_id)\
                                .join(SalesCustomerDetailsSA, SalesCustomerDetailsSA.pk_bint_id == SalesMasterSA.fk_customer_id)\
                                .join(AuthUserSA, AuthUserSA.id == SalesMasterSA.fk_staff_id)\
                                .join(ItemsSA, ItemsSA.pk_bint_id == SalesDetailsSA.fk_item_id)\
                                .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                                .filter(SalesMasterSA.pk_bint_id.in_(lst_service_id))


            else:
                rst_invoice = session.query(SalesMasterSA.pk_bint_id.label('int_id'),SalesDetailsSA.int_sales_status.label('int_sales_status'),SalesMasterSA.dat_invoice.label('dat_invoice'),SalesMasterSA.vchr_invoice_num.label('str_inv_num'),SalesMasterSA.dat_created.label('dat_created'),BranchSA.vchr_name.label('str_branch_name'),\
                                SalesCustomerDetailsSA.vchr_name.label('vchr_gst_no'),SalesCustomerDetailsSA.vchr_name.label('str_cust_name'),SalesCustomerDetailsSA.int_mobile.label('int_mobile'),func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('str_staff_name'),ProductsSA.vchr_name.label('str_product_name'),func.coalesce(False).label('bln_jio_invoice'))\
                                .join(SalesDetailsSA, SalesDetailsSA.fk_master_id == SalesMasterSA.pk_bint_id)\
                                .join(BranchSA, BranchSA.pk_bint_id == SalesMasterSA.fk_branch_id)\
                                .join(SalesCustomerDetailsSA, SalesCustomerDetailsSA.pk_bint_id == SalesMasterSA.fk_customer_id)\
                                .join(AuthUserSA, AuthUserSA.id == SalesMasterSA.fk_staff_id)\
                                .join(ItemsSA, ItemsSA.pk_bint_id == SalesDetailsSA.fk_item_id)\
                                .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                                .filter(cast(SalesMasterSA.dat_created,Date) >= dat_from,cast(SalesMasterSA.dat_created,Date) <= dat_to)\
                                .filter(~SalesMasterSA.pk_bint_id.in_(lst_service_id))
                                # .filter(and_(ProductsSA.pk_bint_id.notin_([4,28]),SalesDetailsSA.int_sales_status != 3 )) #if there any error with invoice list that not showing any servicce please comment this line

            rst_jio_invoice = session.query(SalesMasterJioSa.pk_bint_id.label('int_id'),literal_column('100').label('int_sales_status'),SalesMasterJioSa.dat_invoice.label('dat_invoice'),SalesMasterJioSa.vchr_invoice_num.label('str_inv_num'),SalesMasterJioSa.dat_created.label('dat_created'),BranchSA.vchr_name.label('str_branch_name'),\
                            SalesCustomerDetailsSA.vchr_name.label('vchr_gst_no'),SalesCustomerDetailsSA.vchr_name.label('str_cust_name'),SalesCustomerDetailsSA.int_mobile.label('int_mobile'),func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('str_staff_name'),ProductsSA.vchr_name.label('str_product_name'),func.coalesce(True).label('bln_jio_invoice'))\
                            .join(BranchSA, BranchSA.pk_bint_id == SalesMasterJioSa.fk_branch_id)\
                            .join(SalesCustomerDetailsSA, SalesCustomerDetailsSA.pk_bint_id == SalesMasterJioSa.fk_customer_id)\
                            .join(AuthUserSA, AuthUserSA.id == SalesMasterJioSa.fk_staff_id)\
                            .join(ItemsSA, ItemsSA.pk_bint_id == SalesMasterJioSa.fk_item_id)\
                            .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                            .filter(cast(SalesMasterJioSa.dat_created,Date) >= dat_from,cast(SalesMasterJioSa.dat_created,Date) <= dat_to)
            #----------------------------------User Privilege--------------------------------------------------------------------
            dct_privilege = get_user_privileges(request)

            lst_branch = []

            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN' or request.user.userdetails.fk_branch.int_type in [2,3]:
                if request.user.userdetails.fk_branch.vchr_code in ['MCL3']:
                    lst_branch = [request.user.userdetails.fk_branch_id]
                else:
                    pass

            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER', 'ASSISTANT BRANCH MANAGER', 'ASM1', 'ASM2', 'ASM3', 'ASM4']:
                lst_branch = [request.user.userdetails.fk_branch_id]
            elif dct_privilege:
                if dct_privilege.get('lst_branches'):
                    lst_branch =  dct_privilege['lst_branches']
                else:
                    lst_branch = [request.user.userdetails.fk_branch_id]
            else:
                lst_branch = [request.user.userdetails.fk_branch_id]

            #------------------------------------------------------------------------------------------------------------------

            # rst_invoice = rst_invoice.filter(SalesMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            # rst_jio_invoice = rst_jio_invoice.filter(SalesMasterJioSa.fk_branch_id == request.user.userdetails.fk_branch_id)
            if not (request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN' ):
                rst_invoice = rst_invoice.filter(SalesMasterSA.fk_branch_id.in_(lst_branch) )
                rst_jio_invoice = rst_jio_invoice.filter(SalesMasterJioSa.fk_branch_id.in_(lst_branch))

            if request.data.get("intPhone"):
                rst_invoice = rst_invoice.filter(SalesCustomerDetailsSA.int_mobile == request.data.get("intPhone"))
                rst_jio_invoice = rst_jio_invoice.filter(SalesCustomerDetailsSA.int_mobile == request.data.get("intPhone"))
            if request.data.get('intBrandId'):
                rst_invoice = rst_invoice.filter(ItemsSA.fk_brand_id == int(request.data.get('intBrandId')))
                rst_jio_invoice = rst_jio_invoice.filter(ItemsSA.fk_brand_id == int(request.data.get('intBrandId')))
            if request.data.get('intItemId'):
                rst_invoice = rst_invoice.filter(ItemsSA.pk_bint_id == int(request.data.get('intItemId')))
                rst_jio_invoice = rst_jio_invoice.filter(ItemsSA.pk_bint_id == int(request.data.get('intItemId')))
            if request.data.get('intProductId'):
                rst_invoice = rst_invoice.filter(ProductsSA.pk_bint_id == int(request.data.get('intProductId')))
                rst_jio_invoice = rst_jio_invoice.filter(ProductsSA.pk_bint_id == int(request.data.get('intProductId')))
            if request.data.get('intStaffId'):
                rst_invoice = rst_invoice.filter(SalesMasterSA.fk_staff_id == int(request.data.get('intStaffId')))
                rst_jio_invoice = rst_jio_invoice.filter(SalesMasterJioSa.fk_staff_id == int(request.data.get('intStaffId')))
            if request.data.get('intBranchId'):
                rst_invoice = rst_invoice.filter(SalesMasterSA.fk_branch_id == request.data.get('intBranchId') )
                rst_jio_invoice = rst_jio_invoice.filter(SalesMasterJioSa.fk_branch_id ==  request.data.get('intBranchId'))

            rst_data = rst_invoice.union_all(rst_jio_invoice).order_by(desc('dat_created')).all()
            lst_invoice = []
            for ins_data in rst_data:
                dct_data = {}
                dct_data['fk_master__fk_customer__int_mobile'] = ins_data.int_mobile
                dct_data['fk_master__fk_customer__vchr_name'] = ins_data.str_cust_name or ''
                dct_data['fk_master__fk_customer__vchr_gst_no'] = ins_data.vchr_gst_no

                dct_data['fk_master__fk_branch__vchr_name'] = ins_data.str_branch_name
                dct_data['fk_master__vchr_invoice_num'] = ins_data.str_inv_num
                dct_data['fk_master__dat_invoice'] = ins_data.dat_invoice
                dct_data['fk_master__fk_staff__first_name'] = ins_data.str_staff_name
                dct_data['fk_master__fk_staff__last_name'] = ''
                dct_data['fk_item__fk_product__vchr_name'] = ins_data.str_product_name
                dct_data['intId'] = ins_data.int_id
                dct_data['blnJioInvoice'] = ins_data.bln_jio_invoice
                dct_data['blnReturn'] = 0
                if ins_data.int_sales_status == 0:
                    dct_data['blnReturn'] = 1
                lst_invoice.append(dct_data)

            dict_inv={}
            j=0
            for i in lst_invoice:
                if i['fk_master__vchr_invoice_num'] not in dict_inv:
                    dict_inv[i['fk_master__vchr_invoice_num']]=j
                else:
                    if i['fk_item__fk_product__vchr_name'] not in lst_invoice[dict_inv[i['fk_master__vchr_invoice_num']]]['fk_item__fk_product__vchr_name']:
                        lst_invoice[dict_inv[i['fk_master__vchr_invoice_num']]]['fk_item__fk_product__vchr_name']=lst_invoice[dict_inv[i['fk_master__vchr_invoice_num']]]['fk_item__fk_product__vchr_name']+" , "+i['fk_item__fk_product__vchr_name']
                    lst_invoice[j]=None
                j=j+1
            lst_invoice = filter(None, lst_invoice)
            session.close()
            return Response({'status':1,'lst_invoice':lst_invoice})
        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

    def put(self,request):
        try:
            
            if request.data.get('InvoiceNum'):
                ins_sales=SalesMaster.objects.filter(vchr_invoice_num=request.data.get('InvoiceNum'))
                if not ins_sales:
                    return Response({'status':0,'message':'No Data'})
                else:
                    int_id=ins_sales[0].pk_bint_id
            else:
                int_id = int(request.data.get('intId'))

            # lst_details=SalesDetails.objects.filter(fk_master__vchr_invoice_num=str_invoice_num).values('fk_item__vchr_name','fk_item__fk_brand__vchr_name','int_qty','dbl_amount','dbl_selling_price','fk_item__fk_product__vchr_name','dbl_tax','dbl_discount','dbl_buyback','json_tax','json_imei','int_sales_status')
            #
            # for i in lst_details:
            #
            #     if i['json_tax']['dblCGST']==0 and i['json_tax']['dblSGST']==0:
            #         i['json_tax'].pop('dblCGST')
            #         i['json_tax'].pop('dblSGST')
            #     else:
            #         i['json_tax'].pop('dblIGST')
            #     if i['int_sales_status']==1:
            #         i['bln_return']=True
            #     else:
            #         i['bln_return']=False
            #     m=""
            #     for k in i['json_imei']:
            #         if len(i['json_imei'])>=2:
            #             m=k+" , "+m
            #         else:
            #             m=k
            #     i['json_imei']=m
            rst_payment = []
            session = Connection()
            if request.data.get('blnJioInvoice'):
                lst_master = SalesMasterJio.objects.filter(pk_bint_id = int_id).values('dat_invoice','fk_branch__vchr_name','fk_staff__first_name','fk_staff__last_name','fk_customer__vchr_name','fk_customer__vchr_email','fk_customer__int_mobile','vchr_remarks','fk_customer_id','fk_customer__fk_customer_id','fk_customer_id','fk_customer__txt_address','fk_customer__vchr_gst_no','fk_customer__fk_location_id','fk_customer__fk_location__vchr_name','fk_customer__fk_location__vchr_pin_code','fk_customer__fk_state_id','fk_customer__fk_state__vchr_name','fk_customer__int_cust_type')
                rst_data = session.query(SalesMasterJioJS.c.int_qty.label('int_qty'), SalesMasterJioJS.c.dbl_total_amt.label('dbl_amount'), SalesMasterJioJS.c.dbl_total_amt.label('dbl_selling_price'), literal_column("0.0").label('dbl_tax'),\
                                        literal_column("0.0").label('dbl_discount'), literal_column("0.0").label('dbl_buyback'), literal_column("4").label('int_sales_status'), literal_column("NULL").label('json_tax'),\
                                        SalesMasterJioJS.c.json_imei.label('json_imei'), ItemsSA.pk_bint_id.label('int_item_id'),ItemsSA.vchr_item_code.label('vchr_item_code'), ItemsSA.vchr_name.label('vchr_item_name'), BrandSA.vchr_name.label('vchr_brand_name'),\
                                        ProductsSA.vchr_name.label('vchr_product_name'), literal_column("NULL").label('vchr_image'), literal_column("NULL").label('vchr_remark'), literal_column("NULL").label('bln_damaged'))\
                                        .join(ItemsSA, ItemsSA.pk_bint_id == SalesMasterJioJS.c.fk_item_id)\
                                        .join(BrandSA, BrandSA.pk_bint_id == ItemsSA.fk_brand_id)\
                                        .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                                        .filter(SalesMasterJioJS.c.pk_bint_id == int_id)

            else:
                lst_master = SalesMaster.objects.filter(pk_bint_id = int_id).extra({'time_invoice':"to_char(sales_master.dat_created::timestamp, 'HH:MI:SS PM')"}).  values('dat_invoice','fk_branch__vchr_name','fk_staff__first_name','fk_staff__last_name','fk_customer__vchr_name','fk_customer__vchr_email','fk_customer__int_mobile','vchr_remarks','fk_customer_id','fk_customer__fk_customer_id','fk_customer__txt_address','fk_customer__vchr_gst_no','fk_customer__fk_location_id','fk_customer__fk_location__vchr_name','fk_customer__fk_location__vchr_pin_code','fk_customer__fk_state_id','fk_customer__fk_state__vchr_name','vchr_invoice_num','time_invoice','fk_customer__int_cust_type')

                rst_data = session.query(SalesDetailsJS.c.int_qty.label('int_qty'), SalesDetailsJS.c.dbl_amount.label('dbl_amount'), SalesDetailsJS.c.dbl_selling_price.label('dbl_selling_price'), SalesDetailsJS.c.dbl_tax.label('dbl_tax'),\
                                        SalesDetailsJS.c.dbl_discount.label('dbl_discount'),SalesDetailsJS.c.dbl_indirect_discount.label('dbl_indirect_discount'), SalesDetailsJS.c.dbl_buyback.label('dbl_buyback'), SalesDetailsJS.c.int_sales_status.label('int_sales_status'), SalesDetailsJS.c.json_tax.label('json_tax'),\
                                        SalesDetailsJS.c.json_imei.label('json_imei'), ItemsSA.pk_bint_id.label('int_item_id'),ItemsSA.vchr_item_code.label('vchr_item_code'), ItemsSA.vchr_name.label('vchr_item_name'), BrandSA.vchr_name.label('vchr_brand_name'),PartialInvoiceJS.c.json_data.label('dct_invoice'),\
                                        ProductsSA.vchr_name.label('vchr_product_name'), case([((SalesReturnSA.fk_item_id == ItemsSA.pk_bint_id), SalesReturnSA.vchr_image)], else_=literal_column("NULL")).label('vchr_image'),\
                                        case([((SalesReturnSA.fk_item_id == ItemsSA.pk_bint_id), SalesReturnSA.vchr_remark)], else_=literal_column("NULL")).label('vchr_remark'), case([((SalesReturnSA.fk_item_id == ItemsSA.pk_bint_id), SalesReturnSA.bln_damaged)], else_=literal_column("NULL")).label('bln_damaged'))\
                                        .join(SalesMasterSA, SalesMasterSA.pk_bint_id == SalesDetailsJS.c.fk_master_id)\
                                        .join(ItemsSA, ItemsSA.pk_bint_id == SalesDetailsJS.c.fk_item_id)\
                                        .join(BrandSA, BrandSA.pk_bint_id == ItemsSA.fk_brand_id)\
                                        .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                                        .outerjoin(PartialInvoiceJS, PartialInvoiceJS.c.fk_invoice_id == SalesMasterSA.pk_bint_id)\
                                        .outerjoin(SalesReturnSA, and_(SalesReturnSA.fk_sales_id == SalesMasterSA.pk_bint_id,ItemsSA.pk_bint_id == SalesReturnSA.fk_item_id))\
                                        .filter(SalesMasterSA.pk_bint_id == int_id)


# .join(SalesMasterSA,and_(SalesMasterSA.pk_bint_id == SalesDetailsJS.c.fk_master_id,SalesMasterSA.int_sales_status==0))\
                 # 0. Finance, 1. Cash, 2. Debit Card, 3. Credit Card 4. Receipt
                rst_payment = PaymentDetails.objects.filter(fk_sales_master_id = int_id)\
                                                    .annotate(payment_type=Case(When(int_fop=0, then=Value('Finance')),When(int_fop=1, then=Value('Cash')), When(int_fop=2, then=Value('Debit Card')),When(int_fop=3, then=Value('Credit Card')),When(int_fop=4, then=Value('Receipt')),When(int_fop=5, then=Value('Paytm')),When(int_fop=6, then=Value('Paytm mall')),When(int_fop=7, then=Value('Bharath QR')),default=Value('Other'),output_field=CharField(),),)\
                                                    .values('dat_created_at','payment_type','dbl_receved_amt','vchr_reff_number','vchr_card_number','int_fop','vchr_finance_schema','dbl_finance_amt','vchr_name')
                dct_finance={}
                lst_finance=[]


                for data in rst_payment:
                    if data['int_fop']==0:
                        ins_fin=Financiers.objects.filter(vchr_code=data['vchr_name'])
                        dct_finance=data
                        dct_finance['company']=ins_fin[0].vchr_name
                        lst_finance.append(dct_finance)
                if lst_finance:
                    dct_finance=lst_finance[0]
                    rst_finance_data = FinanceDetails.objects.filter(fk_payment__fk_sales_master_id = int_id).values('dbl_dbd_amt','dbl_margin_fee','dbl_service_amt','dbl_processing_fee')
                    if rst_finance_data:
                        dct_finance['service_charge'] = rst_finance_data[0]['dbl_service_amt']
                        dct_finance['margin_fee'] = rst_finance_data[0]['dbl_margin_fee']
                        dct_finance['processing_fee'] = rst_finance_data[0]['dbl_processing_fee']
                        dct_finance['dbd_amount'] = rst_finance_data[0]['dbl_dbd_amt']
                rst_payment=rst_payment.exclude(int_fop=0)

            if not rst_data.all():
                return Response({'status':0,'message':'No Data'})
            lst_details = []
            # dct_data = {}
            # ins_customer = SalesCustomerDetails.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_sales_cust_id']).values('pk_bint_id','fk_customer_id','vchr_name','vchr_email','int_mobile','txt_address','vchr_gst_no','fk_location__vchr_name','fk_location__vchr_pin_code','fk_location_id','fk_state_id','fk_state__vchr_name','int_loyalty_points','int_redeem_point').first()
            # # ================================================================================
            # dct_data['customer']={}
            # dct_data['customer']['intSalesCustId'] =  ins_customer['pk_bint_id']
            # # ================================================================================
            # dct_data['customer']['intContactNo'] = ins_customer['int_mobile']
            # dct_data['customer']['intCustId'] = ins_customer['fk_customer_id']
            # dct_data['customer']['strCustName'] = ins_customer['vchr_name']
            # dct_data['customer']['strCustEmail'] = ins_customer['vchr_email']
            # dct_data['customer']['txtAddress'] = ins_customer['txt_address']
            # dct_data['customer']['strGSTNo'] = ins_customer['vchr_gst_no']
            # dct_data['customer']['intLocation'] = ins_customer['fk_location_id']
            # dct_data['customer']['strLocation'] = ins_customer['fk_location__vchr_name']
            # dct_data['customer']['intPinCode'] = ins_customer['fk_location__vchr_pin_code']
            # dct_data['customer']['intState'] = ins_customer['fk_state_id']
            # dct_data['customer']['strState'] = ins_customer['fk_state__vchr_name']


            # LG
            if request.data.get('blnReturn') == 1:
                rst_data = SalesReturn.objects.filter(fk_sales_id = int_id).values('int_qty','dbl_amount','dbl_selling_price','jsn_imei','fk_item_id','fk_item_id__vchr_item_code','fk_item_id__vchr_name','fk_item_id__fk_brand_id__vchr_name','fk_item_id__fk_product_id__vchr_name','vchr_image','vchr_remark','bln_damaged','fk_sales_details_id__dbl_buyback','fk_sales_details_id__dbl_selling_price','vchr_old_inv_no')

                for ins_data in rst_data:
                    dct_data = {}
                    if not ins_data['fk_sales_details_id__dbl_selling_price']:
                        ins_data['fk_sales_details_id__dbl_selling_price']= ins_data.get('dbl_selling_price',0)
                    
                    dct_data['intItemId'] = ins_data['fk_item_id']
                    dct_data['jsonTax'] = {"dblCGST": 0, "dblIGST": 0, "dblSGST": 0}
                    dct_data['dblAmount'] = round(abs(ins_data['fk_sales_details_id__dbl_selling_price']),2)*-1
                    # dct_data['dblAmount'] = round(abs(ins_data['fk_sales_details_id__dbl_selling_price'])- abs(ins_data['fk_sales_details_id__dbl_buyback']),2)*-1
                    dct_data['strItemCode'] = ins_data['fk_item_id__vchr_item_code']
                    dct_data['strItemName'] = ins_data['fk_item_id__vchr_name']
                    dct_data['strBrandName'] = ins_data['fk_item_id__fk_brand_id__vchr_name']
                    dct_data['strProductName'] = ins_data['fk_item_id__fk_product_id__vchr_name']
                    dct_data['intQuantity'] = ins_data['int_qty']
                    dct_data['dblRate'] = round(ins_data['dbl_amount'],2)
                    dct_data['strImei'] = ins_data['jsn_imei']
                    dct_data['strImage'] = ins_data['vchr_image']
                    dct_data['strRemarks'] = ins_data['vchr_remark']
                    dct_data['blnDamage'] = ins_data['bln_damaged']
                    dct_data['dblTax'] = ''
                    dct_data['dblDiscount'] = ''
                    dct_data['dblIndirectDiscount'] = ''
                    dct_data['dblBuyBack'] = ''
                    dct_data['jsonTax'] = ''
                    dct_data['dctImage'] = ''
                    dct_data['intSaleStatus'] = 0
                    dct_data['old_inv_no'] = ins_data['vchr_old_inv_no']


                    lst_details.append(dct_data)
                session.close()
                return Response({'status':1,'master':lst_master,'details':lst_details,'lst_payment':rst_payment,'dct_finance':dct_finance})


            for ins_data in rst_data.all():
                dct_data = {}
                dct_data['intItemId'] = ins_data.int_item_id
                dct_data['strItemCode'] = ins_data.vchr_item_code
                dct_data['strItemName'] = ins_data.vchr_item_name
                dct_data['strBrandName'] = ins_data.vchr_brand_name
                dct_data['strProductName'] = ins_data.vchr_product_name
                dct_data['intQuantity'] = ins_data.int_qty
                dct_data['dblRate'] = ins_data.dbl_amount
                dct_data['dblAmount'] = ins_data.dbl_selling_price
                dct_data['dblTax'] = ins_data.dbl_tax
                dct_data['dblDiscount'] = ins_data.dbl_discount
                dct_data['dblIndirectDiscount'] = ins_data.dbl_indirect_discount
                dct_data['dblBuyBack'] = ins_data.dbl_buyback
                dct_data['jsonTax'] = {"dblCGST": 0, "dblIGST": 0, "dblSGST": 0}
                if ins_data.json_tax:
                    dct_data['jsonTax'] = ins_data.json_tax
                if ins_data.dct_invoice:
                    if 'bajaj_images' in ins_data.dct_invoice:
                        dct_data['bajaj_images'] = ins_data.dct_invoice['bajaj_images']
                dct_data['strImei'] = ''
                for int_imei in ins_data.json_imei:
                    dct_data['strImei'] += str(int_imei if int_imei else '' ) + ','
                dct_data['strImei'] = dct_data['strImei'][:-1]
                dct_data['intSaleStatus'] = ins_data.int_sales_status
                if ins_data.int_sales_status == 0:
                    dct_data['strImage'] = ins_data.vchr_image
                    dct_data['strRemarks'] = ins_data.vchr_remark
                    dct_data['blnDamage'] = ins_data.bln_damaged
                if ins_data.int_sales_status == 2:
                    for ins_item in ins_data.dct_invoice['lst_items']:
                        if ins_item['int_status'] == 2:
                            dct_data['dctImage'] = ins_item['dct_images']
                lst_details.append(dct_data)
            session.close()
            return Response({'status':1,'master':lst_master,'details':lst_details,'lst_payment':rst_payment,'dct_finance':dct_finance})
        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})



class InvoiceListPrintApi(APIView):
    def post(self,request):
        try:
            lst_imei = [request.data.get('imei')]
            int_customer = request.data.get('intCustomer')
            str_invoice_no = request.data.get('invoiceNo')
            request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN' or request.user.userdetails.fk_branch.int_type in [2,3]
            if request.data.get('imei'):
                lst_imei = [request.data.get('imei')]
                ins_sales_details = SalesDetails.objects.filter(json_imei__contains=lst_imei,int_sales_status__in =[1,2,3,4,0]).values_list('fk_master_id',flat=True).distinct()
                if not request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN' or not request.user.userdetails.fk_branch.int_type in [2,3]:
                    ins_sales_details = ins_sales_details.filter(fk_master__fk_branch_id = request.user.userdetails.fk_branch_id)

            elif request.data.get('datFrom'):
                dat_from = datetime.strptime(request.data.get('datFrom'),'%Y-%m-%d').date()
                dat_to = datetime.strptime(request.data.get('datTo'),'%Y-%m-%d').date()
                ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id=int_customer,fk_master__dat_invoice__range=(dat_from,dat_to),int_sales_status__in =[1,2,3,4,0]).values_list('fk_master_id',flat=True).distinct()

            elif str_invoice_no :
                 ins_sales_details = SalesDetails.objects.filter(fk_master__vchr_invoice_num = str_invoice_no,int_sales_status__in =[1,2,3,4,0]).values_list('fk_master_id',flat=True).distinct()


            else:
                ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id=int_customer,int_sales_status__in =[1,2,3,4,0]).values_list('fk_master_id',flat=True).distinct()
                # ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id=int_customer,int_sales_status__in =[1,2,3,4]).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
            if not ins_sales_details:
                return Response({'status':0})

            rst_invoice = SalesDetails.objects.filter(fk_master_id__in = ins_sales_details).values('fk_master_id','fk_item__vchr_name','fk_master__vchr_invoice_num','fk_master__dat_invoice').order_by('-fk_master_id')

            dct_data={}
            lst_data=[]
            for ins_data in rst_invoice:
                # dct_data['tax']={'dblCGST': 0, 'dblIGST': 0, 'dblSGST': 0}
                if ins_data['fk_master__vchr_invoice_num'] not in dct_data:
                    dct_data[ins_data['fk_master__vchr_invoice_num']] = {}
                    dct_data[ins_data['fk_master__vchr_invoice_num']]['invoice_id'] = ins_data['fk_master_id']
                    dct_data[ins_data['fk_master__vchr_invoice_num']]['invoice_num'] = ins_data['fk_master__vchr_invoice_num']
                    dct_data[ins_data['fk_master__vchr_invoice_num']]['dat_invoice'] = datetime.strftime(ins_data['fk_master__dat_invoice'],'%d-%m-%Y')
                    dct_data[ins_data['fk_master__vchr_invoice_num']]['item'] = []
                    dct_data[ins_data['fk_master__vchr_invoice_num']]['item'].append(ins_data['fk_item__vchr_name'])
                else:
                    dct_data[ins_data['fk_master__vchr_invoice_num']]['item'].append(ins_data['fk_item__vchr_name'])
            return Response({'status':1, 'data' : list(dct_data.values())})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})




class AddInvoiceJIO(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            with transaction.atomic():
                dct_item_data = json.loads(request.data.get('dctTableData'))
                lst_returned_id  = json.loads(request.data.get('dctReturnId'))
                int_redeem_point = json.loads(request.data.get('intRedeemPoint'))
                dbl_rounding_off = json.loads(request.data.get('intRounding','0.0'))
                str_remarks = request.data.get('strRemarks',None)
                bln_igst = False

                # ins_document = Document.objects.select_for_update().get(vchr_module_name = 'DELIVERY CHALLAN',vchr_short_code = 'DC')
                # str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                # ins_document.int_number = ins_document.int_number+1
                # ins_document.save()

                # LG 27-06-2020
                ins_document = Document.objects.select_for_update().get(vchr_module_name = 'DELIVERY CHALLAN',fk_branch_id = request.user.userdetails.fk_branch_id).first()
                if ins_document:
                    str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                    Document.objects.filter(vchr_module_name = "DELIVERY CHALLAN",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                else:
                    ins_document_search = Document.objects.filter(vchr_module_name = 'DELIVERY CHALLAN',fk_branch_id = None).first()
                    if ins_document_search:
                        ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                        ins_document = Document.objects.create(vchr_module_name = 'DELIVERY CHALLAN', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                        str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                        ins_document.int_number = ins_document.int_number+1
                        ins_document.save()
                    else:
                        return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId')).values().first()

                ins_branch = Branch.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_branch_id']).first()
                ins_staff = Userdetails.objects.filter(user_ptr_id = ins_partial_inv['json_data']['int_staff_id']).first()

                # ins_customer = CustomerDetails.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_cust_id']).first()
                ins_sales_customer = SalesCustomerDetails.objects.filter(pk_bint_id = request.data.get('intSalesCustId')).first()

                if request.user.userdetails.fk_branch.fk_states_id != ins_sales_customer.fk_state_id or ins_sales_customer.int_cust_type==3:
                # if request.user.userdetails.fk_branch.fk_states_id != ins_customer.fk_state_id:
                    bln_igst = True
                odct_item_data = OrderedDict()
                dbl_total_amt = 0
                dbl_total_tax = 0
                json_total_tax = {'dblIGST':0,'dblCGST':0,'dblSGST':0}
                bln_kfc = False
                if not bln_igst and not ins_sales_customer.vchr_gst_no:
                    json_total_tax['dblKFC'] = 0
                    bln_kfc = True
                dbl_total_rate = 0
                dbl_total_buyback = 0
                dbl_total_discount = 0

                for dct_item in dct_item_data:
                    # dct_item['status'] = 1
                    dbl_kfc = 0
                    if bln_kfc and dct_item['intStatus'] == 1:
                        dbl_kfc = round((dct_item['dblRate']-dct_item['dblDiscount'])*(1/100),2)
                    dct_item['dblAmount'] = dct_item['dblAmount']+dbl_kfc
                    str_temp = str(dct_item['intItemId'])+'-'+str(dct_item['dblAmount'])+'-'+str(dct_item['intStatus'])
                    # str_temp = str(dct_item['intItemId'])+'-'+str(dct_item['dblAmount'])
                    if str_temp in odct_item_data and odct_item_data[str_temp]['dblBuyBack'] == dct_item['dblBuyBack'] and odct_item_data[str_temp]['dblDiscount'] == dct_item['dblDiscount'] and odct_item_data[str_temp]['dblAmount'] == dct_item['dblAmount'] and odct_item_data[str_temp]['dblRate'] == dct_item['dblRate']:
                        if not dct_item['intStatus'] == 0:
                            dbl_total_amt += dct_item['dblAmount']
                            dbl_total_rate += dct_item['dblRate']
                            dbl_total_buyback += dct_item['dblBuyBack']
                            dbl_total_discount += dct_item['dblDiscount']
                        else:
                            dbl_total_amt += (dct_item['dblAmount']*-1)
                            dbl_total_rate += (dct_item['dblRate']*-1)
                            dbl_total_buyback += (dct_item['dblBuyBack']*-1)
                            dbl_total_discount += (dct_item['dblDiscount']*-1)

                        if bln_igst:
                            odct_item_data[str_temp]['dblIGST'] += dct_item['dblIGST']
                            dbl_total_tax += dct_item['dblIGST']
                            json_total_tax['dblIGST'] += dct_item['dblIGST']
                            odct_item_data[str_temp]['jsonTax']['dblIGST'] += dct_item['dblIGST']
                            odct_item_data[str_temp]['dblTax'] += dct_item['dblIGST']
                        else:
                            if bln_kfc:
                                json_total_tax['dblKFC'] += dct_item['intKfc'] if dct_item.get('intKfc') else 0
                                odct_item_data[str_temp]['dblKFC'] += dct_item['intKfc'] if dct_item.get('intKfc') else 0
                                odct_item_data[str_temp]['jsonTax']['dblKFC'] += dct_item['intKfc'] if dct_item.get('intKfc') else 0
                            odct_item_data[str_temp]['dblCGST'] += dct_item['dblCGST']
                            odct_item_data[str_temp]['dblSGST'] += dct_item['dblSGST']
                            dbl_total_tax += dct_item['dblCGST'] + dct_item['dblSGST'] + dct_item['intKfc'] if dct_item.get('intKfc') else 0
                            json_total_tax['dblCGST'] += dct_item['dblCGST']
                            json_total_tax['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['jsonTax']['dblCGST'] += dct_item['dblCGST']
                            odct_item_data[str_temp]['jsonTax']['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['dblTax'] += dct_item['dblCGST']+dct_item['dblSGST'] + dct_item['intKfc'] if dct_item.get('intKfc') else 0
                        odct_item_data[str_temp]['dblBuyBack'] += dct_item['dblBuyBack']
                        odct_item_data[str_temp]['dblDiscount'] += dct_item['dblDiscount']
                        odct_item_data[str_temp]['dblRate'] += dct_item['dblRate']
                        odct_item_data[str_temp]['dblAmount'] += dct_item['dblAmount']
                        odct_item_data[str_temp]['intQuantity'] += 1
                        odct_item_data[str_temp]['jsonImei'].append(dct_item['strImei'])
                    else:
                        odct_item_data[str_temp] = {}
                        odct_item_data[str_temp]['strItemCode'] = dct_item['strItemCode']
                        odct_item_data[str_temp]['intItemId'] = dct_item['intItemId']
                        odct_item_data[str_temp]['dblBuyBack'] = dct_item['dblBuyBack']
                        odct_item_data[str_temp]['dblDiscount'] = dct_item['dblDiscount']
                        odct_item_data[str_temp]['dblAmount'] = dct_item['dblAmount']
                        odct_item_data[str_temp]['dblRate'] = dct_item['dblRate']
                        odct_item_data[str_temp]['jsonImei'] = [dct_item.get('strImei')]
                        odct_item_data[str_temp]['jsonTax'] = {'dblIGST':0,'dblCGST':0,'dblSGST':0}
                        if bln_kfc:
                            odct_item_data[str_temp]['jsonTax']['dblKFC'] = 0
                        odct_item_data[str_temp]['dblTax'] = 0
                        odct_item_data[str_temp]['dblIndirectDis'] = dct_item.get('dblIndirectDis')
                        # odct_item_data[str_temp]['status']=1 if not dct_item['intStatus'] == 1 else 0
                        # if dct_item['intStatus'] == 2:
                        #     odct_item_data[str_temp]['status']= 2
                        odct_item_data[str_temp]['status'] = dct_item['intStatus']
                        if not dct_item['intStatus'] == 0:
                            dbl_total_amt += dct_item['dblAmount']
                            dbl_total_rate += dct_item['dblRate']
                            dbl_total_buyback += dct_item['dblBuyBack']
                            dbl_total_discount += dct_item['dblDiscount']
                        else:
                            odct_item_data[str_temp]['dblBuyBack'] = dct_item['dblBuyBack']*-1
                            odct_item_data[str_temp]['dblDiscount'] = dct_item['dblDiscount']*-1
                            odct_item_data[str_temp]['dblAmount'] = dct_item['dblAmount']*-1
                            odct_item_data[str_temp]['dblRate'] = dct_item['dblRate']*-1
                            odct_item_data[str_temp]['intMasterId'] = dct_item.get('intMasterId')
                            dbl_total_amt += (dct_item['dblAmount']*-1)
                            dbl_total_rate += (dct_item['dblRate']*-1)
                            dbl_total_buyback += (dct_item['dblBuyBack']*-1)
                            dbl_total_discount += (dct_item['dblDiscount']*-1)
                        if bln_igst:
                            odct_item_data[str_temp]['dblIGST'] = dct_item['dblIGST']
                            dbl_total_tax += dct_item['dblIGST']
                            json_total_tax['dblIGST'] += dct_item['dblIGST']
                            odct_item_data[str_temp]['jsonTax']['dblIGST'] += dct_item['dblIGST']
                            odct_item_data[str_temp]['dblTax'] += dct_item['dblIGST']
                        else:
                            if bln_kfc:
                                odct_item_data[str_temp]['dblKFC'] = dct_item['intKfc'] if dct_item.get('intKfc') else 0
                                json_total_tax['dblKFC'] += dct_item['intKfc'] if dct_item.get('intKfc') else 0
                                odct_item_data[str_temp]['jsonTax']['dblKFC'] += dct_item['intKfc'] if dct_item.get('intKfc') else 0
                            odct_item_data[str_temp]['dblCGST'] = dct_item['dblCGST']
                            odct_item_data[str_temp]['dblSGST'] = dct_item['dblSGST']
                            dbl_total_tax += dct_item['dblCGST'] + dct_item['dblSGST'] + dct_item['intKfc'] if dct_item.get('intKfc') else 0
                            json_total_tax['dblCGST'] += dct_item['dblCGST']
                            json_total_tax['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['jsonTax']['dblCGST'] += dct_item['dblCGST']
                            odct_item_data[str_temp]['jsonTax']['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['dblTax'] += dct_item['dblCGST'] + dct_item['dblSGST'] + dct_item['intKfc'] if dct_item.get('intKfc') else 0
                        odct_item_data[str_temp]['intQuantity'] = 1

                # ins_sales_master = SalesMaster.objects.create(fk_customer = ins_customer,
                #                         fk_branch = ins_branch,
                #                         vchr_invoice_num = str_inv_num,
                #                         dat_invoice = date.today(),
                #                         vchr_remarks = str_remarks,
                #                         dat_created = datetime.now(),
                #                         int_doc_status = 1,
                #                         dbl_total_amt = dbl_total_amt,
                #                         dbl_rounding_off = dbl_rounding_off,
                #                         dbl_total_tax = dbl_total_tax,
                #                         dbl_discount = dbl_total_discount,
                #                         json_tax = json_total_tax,partialAmount
                #                         dbl_buyback = dbl_total_buyback,
                #                         fk_loyalty_id = request.data.get('intLoyaltyId',None),
                #                         dbl_loyalty = (1/settings.LOYALTY_POINT)*int_redeem_point,
                #                         fk_staff = ins_staff,
                #                         fk_created = request.user.userdetails,
                #                         fk_coupon_id = request.data.get('intCouponId',None),
                #                         dbl_coupon_amt = request.data.get('intCouponDisc',None),
                #                         fk_financial_year = FinancialYear.objects.filter(dat_start__lte = date.today(),dat_end__gte = date.today()).first())
                # ins_sales_master.save()

                dct_payment_data = json.loads(request.data.get('lstPaymentData'))
                for ins_mode in dct_payment_data:
                    if dct_payment_data[ins_mode].get('dblAmt'):
                        # PaymentDetails.objects.create(fk_sales_master = ins_sales_master,lst_offer
                        #                             int_fop = int(ins_mode),
                        #                             vchr_card_number = dct_payment_data[ins_mode].get('strCardNo',None),
                        #                             vchr_name = dct_payment_data[ins_mode].get('strName',None),
                        #                             vchr_finance_schema = dct_payment_data[ins_mode].get('strScheme',None),
                        #                             vchr_reff_number = dct_payment_data[ins_mode].get('strRefNo',None),
                        #                             dbl_receved_amt = dct_payment_data[ins_mode].get('dblAmt',None),
                        #                             dbl_finance_amt = dct_payment_data[ins_mode].get('intFinanceAmt',None),
                        #                             dbl_cc_charge = dct_payment_data[ins_mode].get('intCcCharge',None))

                        for ins_data in odct_item_data:
                            for vchr_stk_imei in odct_item_data[ins_data]['jsonImei']:
                                ins_br_stock = BranchStockDetails.objects.filter(Q(jsn_imei_avail__contains={'imei':[str(vchr_stk_imei)]}),fk_item_id=odct_item_data[ins_data]['intItemId']).first()
                                ins_br_stk_imei = BranchStockImeiDetails.objects.filter(Q(jsn_imei__contains={'imei':[str(vchr_stk_imei)]}),fk_details=ins_br_stock).first()
                                if ins_br_stock:
                                    lst_imei = ins_br_stock.jsn_imei_avail['imei']
                                    lst_imei.remove(vchr_stk_imei)
                                    int_qty = ins_br_stock.int_qty-1
                                    BranchStockDetails.objects.filter(pk_bint_id=ins_br_stock.pk_bint_id).update(jsn_imei_avail={'imei':lst_imei},int_qty=int_qty)
                                else:
                                    return Response({'status':'0','message':'Out of Stock'})
                                if ins_br_stk_imei:
                                    lst_imei = ins_br_stk_imei.jsn_imei['imei']
                                    lst_imei.remove(vchr_stk_imei)
                                    int_qty = ins_br_stock.int_qty-1
                                    BranchStockImeiDetails.objects.filter(Q(jsn_imei__contains={'imei':[str(vchr_stk_imei)]}),fk_details=ins_br_stock).update(jsn_imei={'imei':lst_imei},int_qty=int_qty)
                                else:
                                    return Response({'status':'0','message':'Out of Stock'})

                            # ins_sales_jio = SalesMasterJio.objects.create_inv_num(str_inv_num)

                            ins_sales_jio = SalesMasterJio.objects.create(
                                                          fk_customer = ins_sales_customer,
                                                          # fk_customer=ins_customer,
                                                          fk_branch=ins_branch,
                                                          dat_invoice= date.today(),
                                                          fk_staff=ins_staff,
                                                          vchr_invoice_num=str_inv_num,
                                                          vchr_remarks=str_remarks,
                                                          fk_item_id=odct_item_data[ins_data]['intItemId'],
                                                          int_qty=odct_item_data[ins_data]['intQuantity'],
                                                          json_imei=odct_item_data[ins_data]['jsonImei'],
                                                          dbl_total_amt=odct_item_data[ins_data]['dblAmount'],
                                                          dbl_rounding_off=dbl_rounding_off,
                                                          int_doc_status=1,
                                                          dat_created=datetime.now(),
                                                          fk_created= request.user.userdetails,
                                                          fk_financial_year=FinancialYear.objects.filter(dat_start__lte = date.today(),dat_end__gte = date.today(),bln_status = True).first(),
                                                          int_fop = int(ins_mode),
                                                          vchr_card_number = dct_payment_data[ins_mode].get('strCardNo',None),
                                                          vchr_name = dct_payment_data[ins_mode].get('strName',None),
                                                          vchr_reff_number = dct_payment_data[ins_mode].get('strRefNo',None),
                                                          dbl_receved_amt = dct_payment_data[ins_mode].get('dblAmt',None),
                                                          fk_bank_id=dct_payment_data[ins_mode].get('intBankId',None))

                            ins_sales_jio.save()
                        break
                    #==========sales return============
                    # if odct_item_data[ins_data]['status'] == 0:
                    #     ins_sales_returned = SalesDetails.objects.filter(fk_item__pk_bint_id = odct_item_data[ins_data]['intItemId'],fk_master__fk_customer = ins_customer).values('fk_master__pk_bint_id')
                    #
                    #     if request.FILES.get(str(odct_item_data[ins_data]['intItemId'])):
                    #         img_item = request.FILES.get(str(odct_item_data[ins_data]['intItemId']))
                    #         fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                    #         str_img = fs.save(img_item.name, img_item)
                    #         str_img_path = fs.url(str_img)
                    #
                    #     else:
                    #         str_img_path = ""
                    #     SalesReturn.objects.create(
                    #     fk_returned_id = odct_item_data[ins_data]['intMasterId'],
                    #     fk_sales = ins_sales_master,
                    #     fk_item_id = odct_item_data[ins_data]['intItemId'],
                    #     int_qty = odct_item_data[ins_data]['intQuantity'],
                    #     dbl_amount = odct_item_data[ins_data]['dblRate'],
                    #     dbl_selling_price = odct_item_data[ins_data]['dblAmount'],
                    #     jsn_imei = odct_item_data[ins_data]['jsonImei'],
                    #     dat_returned = date.today(),
                    #     fk_staff = ins_staff,
                    #     dat_created = datetime.now(),
                    #     fk_created = request.user.userdetails,
                    #     int_doc_status = 0,
                    #     vchr_image = str_img_path,
                    #     vchr_remark = lst_returned_id.get(str(odct_item_data[ins_data]['intItemId'])).get('strRemarks'),
                    #     bln_damaged = lst_returned_id.get(str(odct_item_data[ins_data]['intItemId'])).get('blnDamage')
                    #     )




                # # ------------ Customer Delivery Details ---------
                # dct_delivery_data =  json.loads(request.data.get('dctDeliveryData'))
                # if dct_delivery_data.get('strCustName') and dct_delivery_data.get('intCustContactNo'):
                #     CustServiceDelivery.objects.create(fk_sales_master = ins_sales_master,
                #                                     fk_customer = ins_customer,
                #                                     vchr_cust_name = dct_delivery_data.get('strCustName',None),
                #                                     int_mobile = dct_delivery_data.get('intCustContactNo',None),
                #                                     txt_address = dct_delivery_data.get('strCustAddress',None),
                #                                     vchr_landmark = dct_delivery_data.get('strCustPlace',None),
                #                                     vchr_gst_no = dct_delivery_data.get('strCustGST',None),
                #                                     fk_location_id = dct_delivery_data.get('intCustCityId',None),
                #                                     fk_state_id = dct_delivery_data.get('intCustStateId',None))
                # # -------------------------------------------------



                bln_allow = True
                PartialInvoice.objects.filter(pk_bint_id = int(request.data.get('salesRowId'))).update(dat_invoice = datetime.now(),int_active = 1)
                #==============================================================================================================================================================================

                try:
                    int_enq_master_id = PartialInvoice.objects.filter(pk_bint_id = int(request.data.get('salesRowId'))).values().first()['json_data']['int_enq_master_id']
                    url =settings.BI_HOSTNAME + "/mobile/enquiry_invoice_update/"
                    lst_item_id = [x['intItemId'] for x in odct_item_data.values()]
                    dct_item_sup_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_supp_amnt',))

                    for ins in odct_item_data:
                        if odct_item_data[ins]['intItemId'] in lst_item_id:
                            odct_item_data[ins].update({"dbl_supp_amnt":dct_item_sup_amnt.get(odct_item_data[ins]['intItemId'],0.0)})
                        if odct_item_data[ins]['status'] == 3:
                            bln_allow = False
                    if bln_allow:
                        res_data = requests.post(url,json={'dct_item_data':odct_item_data,"int_enq_master_id":int_enq_master_id,"str_remarks":str_remarks})
                        if res_data.json().get('status')=='success':
                            pass
                        else:
                            return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})


                #===============================================================================================================================================================================
                # ---------------- Loyalty Card -------------------
                # if bln_allow:
                #     loyalty_card(dbl_total_amt,ins_customer,ins_sales_master,request.user)
                # -------------------------------------------------

                # dct_payment_data = json.loads(request.data.get('lstPaymentData'))
                # for ins_mode in dct_payment_data:
                #     if dct_payment_data[ins_mode].get('dblAmt') or dct_payment_data[ins_mode].get('intFinanceAmt'):
                #         PaymentDetails.objects.create(fk_sales_master = ins_sales_master,
                #                                     int_fop = int(ins_mode),
                #                                     vchr_card_number = dct_payment_data[ins_mode].get('strCardNo',None),
                #                                     vchr_name = dct_payment_data[ins_mode].get('strName',None),
                #                                     vchr_finance_schema = dct_payment_data[ins_mode].get('strScheme',None),
                #                                     vchr_reff_number = dct_payment_data[ins_mode].get('strRefNo',None),
                #                                     dbl_receved_amt = dct_payment_data[ins_mode].get('dblAmt',None),
                #                                     dbl_finance_amt = dct_payment_data[ins_mode].get('intFinanceAmt',None),
                #                                     dbl_cc_charge = dct_payment_data[ins_mode].get('intCcCharge',None))


                # lstPaymentData=json.loads(request.data.get("lstPaymentData"))
                # if lstPaymentData['4']['blnReceipt']:
                #     bln_matching=json.loads(request.data['bln_matching'])
                #     if bln_matching:
                #         int_total=0.0
                #         lstReceipt=lstPaymentData['4']['lstReceipt']
                #         flag=False
                #         int_total_pre=0
                #         for r in lstReceipt:
                #             int_total=int_total+r['amount']
                #             if float(request.data['intGrandTot'])>int_total:
                #                 if r.get('fk_receipt_id'):
                #                     ReceiptInvoiceMatching.objects.create(fk_receipt_id=r['pk_bint_id'],dbl_amount=r['amount'],dat_created=datetime.now(),fk_sales_master_id=ins_sales_master.pk_bint_id)
                #                 else:
                #                     ReceiptInvoiceMatching.objects.create(dbl_amount=r['dbl_amount'],dat_created=datetime.now(),fk_receipt_id=r['pk_bint_id'],fk_sales_master_id=ins_sales_master.pk_bint_id)
                #             elif flag==False:
                #                 ReceiptInvoiceMatching.objects.create(dbl_amount=(float(request.data['intGrandTot'])-int_total_pre),dat_created=datetime.now(),fk_receipt_id=r['pk_bint_id'],fk_sales_master_id=ins_sales_master.pk_bint_id)
                #             int_total_pre=int_total
                #     if bln_matching== False:
                #         int_total=0.0
                #         lstReceipt=lstPaymentData['4']['lstReceipt']
                #         flag=False
                #         for r in lstReceipt:
                #             int_total=int_total+r['dbl_amount']
                #             if float(request.data['intGrandTot'])>int_total:
                #                 ReceiptInvoiceMatching.objects.create(dbl_amount=r['dbl_amount'],dat_created=datetime.now(),fk_receipt_id=r['pk_bint_id'],fk_sales_master_id=ins_sales_master.pk_bint_id)
                #             elif flag==False:
                #                 ReceiptInvoiceMatching.objects.create(dbl_amount=r['dbl_amount']-(int_total-float(request.data['intGrandTot'])),dat_created=datetime.now(),fk_receipt_id=r['pk_bint_id'],fk_sales_master_id=ins_sales_master.pk_bint_id)
                #                 flag=True

                return Response({'status':1,'sales_master_id':ins_sales_jio.pk_bint_id,'bln_jio':True})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


class Banklist(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            lst_brank = Bank.objects.filter(int_status = 0).values('pk_bint_id','vchr_name')
            return Response({'status':1,'data':lst_brank})

        except Exception as e:
            return JsonResponse({'result':0,'reason':e})

class AddAmountOfferAPI(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            if request.data.get('partial_amt') and request.data.get('job_status')<8:
                ins_partial=PartialInvoice.objects.filter(pk_bint_id=request.data.get('partial_id')).values('json_data')
                json_data=ins_partial.first()['json_data']
                json_data['partial_amt']=request.data.get('partial_amt')
                ins_partial.update(int_status=8,json_data=json_data)

            elif request.data.get('offerId'):
                ins_partial=PartialInvoice.objects.filter(pk_bint_id=request.data.get('partial_id')).values('json_data')
                json_data=ins_partial.first()['json_data']
                json_data['offerId']=request.data.get('offerId')
                json_data['offerName']=request.data.get('offerName')
                json_data['partial_amt']=request.data.get('partial_amt')
                json_data['offerAmt']=request.data.get('offerAmt') or 0
                ins_partial.update(int_status=9,json_data=json_data)
                url= settings.BI_HOSTNAME + '/mobile/update_offer_api/'
                res_data=requests.post(url,json=json_data)
            return Response({'status':1})
        except Exception as e:
            return Response({'status':1,'reason':e})

#
class ListBallGame(APIView):
    permission_classes=[IsAuthenticated]
    def put(self,request):
        try:
            dat_to = (datetime.strptime(request.data.get("datTo")[:10],'%Y-%m-%d')).date()
            dat_from = (datetime.strptime(request.data.get("datFrom")[:10],'%Y-%m-%d')).date()

            ins_partial_inv = PartialInvoice.objects.filter(int_status__in=[7,8,9],int_active = 0,json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id}).annotate(job_status=Case(When(int_status=7,then=Value('BALL GAME')),When(int_status=9,then=Value('OFFER ADDED')),When(int_status=8,then=Value('PARTIAL AMOUNT ADDED'))\
            ,output_field=CharField())).values('pk_bint_id','dat_created','json_data','int_status','job_status').order_by('-dat_created')
            lst_data = []
            for ins_data in ins_partial_inv:
                dct_data = {}
                dct_data['intId'] = ins_data['pk_bint_id']
                dct_data['datBooked'] = ins_data['dat_created'].strftime("%d-%m-%Y")
                dct_data['strCustomer'] = ins_data['json_data']['str_cust_name'].title()
                dct_data['strStaff'] = ins_data['json_data'].get('str_staff_name').title()


                dct_data['sales_status'] = ins_data['int_status']
                dct_data['strItem'] = ''
                dct_data['strItem'] = ' , '.join([ i['vchr_item_name']for i in ins_data['json_data']['lst_items']])
                dct_data['job_status'] = ins_data['job_status']
                if len(dct_data['strItem'])>30:
                    dct_data['strItem'] = dct_data['strItem'][:30]+'...'
                # for ins_data in  ins_data['json_data']['lst_items']:
                #     dct_data['strItem'] += ins_data['vchr_item_name']
                #     if len(dct_data['strItem'])>30:
                #         dct_data['strItem'] = dct_data['strItem'][:30]+'...'
                #         break
                lst_data.append(dct_data)
            return Response({'status':1,'data':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

    # def put(self,request):
    #     try:
    #         int_id = request.data.get('intId')
    #         ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = int_id,int_active = 0).values('dat_created','json_data','int_status').first()
    #         if not ins_partial_inv:
    #             return Response({'status':'0','message':'Already Invoiced'})
    #         dct_data = {}
    #         ins_customer = CustomerDetails.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_cust_id']).values('pk_bint_id','vchr_name','vchr_email','int_mobile','txt_address','vchr_gst_no','fk_location__vchr_name','fk_location__vchr_pin_code','fk_location_id','fk_state_id','fk_state__vchr_name','int_loyalty_points','int_redeem_point').first()
    #         dct_data['intStaffId'] = ins_partial_inv['json_data']['int_staff_id']
    #         dct_data['strStaffName'] = Userdetails.objects.filter(user_ptr_id = ins_partial_inv['json_data']['int_staff_id']).annotate(str_name=Concat('first_name', Value(' '), 'last_name')).values('str_name').first()['str_name']
    #         dct_data['intContactNo'] = ins_customer['int_mobile']
    #         dct_data['intCustId'] = ins_customer['pk_bint_id']
    #         dct_data['strCustName'] = ins_customer['vchr_name']
    #         dct_data['strCustEmail'] = ins_customer['vchr_email']
    #         dct_data['txtAddress'] = ins_customer['txt_address']
    #         dct_data['strGSTNo'] = ins_customer['vchr_gst_no']
    #         dct_data['intLocation'] = ins_customer['fk_location_id']
    #         dct_data['strLocation'] = ins_customer['fk_location__vchr_name']
    #         dct_data['intPinCode'] = ins_customer['fk_location__vchr_pin_code']
    #         dct_data['intState'] = ins_customer['fk_state_id']
    #         dct_data['strState'] = ins_customer['fk_state__vchr_name']
    #         dct_data['intLoyaltyPoint'] = ins_customer['int_loyalty_points']-ins_customer['int_redeem_point']
    #         dct_data['job_status']=ins_partial_inv['int_status']
    #         dct_data['partial_id'] = int_id
    #         if ins_partial_inv['json_data'].get('offerName'):
    #             dct_data['offerName'] = ins_partial_inv['json_data'].get('offerName')
    #         if ins_partial_inv['json_data'].get('partial_amt'):
    #             dct_data['partialAmount'] = ins_partial_inv['json_data'].get('partial_amt')
    #         if ins_partial_inv['json_data'].get('offerId'):
    #             dct_data['offerId'] = ins_partial_inv['json_data'].get('offerId')
    #
    #         if ins_partial_inv['json_data'].get('vchr_finance_name') or ins_partial_inv['json_data'].get('vchr_finance_schema') or ins_partial_inv['json_data'].get('dbl_finance_amt') or ins_partial_inv['json_data'].get('vchr_fin_ordr_num'):
    #             dct_data['vchrFinanceName'] = ins_partial_inv['json_data']['vchr_finance_name']
    #             dct_data['vchrFinanceSchema'] = ins_partial_inv['json_data']['vchr_finance_schema']
    #             dct_data['dblFinanceAmt'] = ins_partial_inv['json_data']['dbl_finance_amt']
    #             dct_data['dblEMI'] = ins_partial_inv['json_data']['dbl_emi']
    #             dct_data['dblDownPayment'] = ins_partial_inv['json_data']['dbl_down_payment']
    #             dct_data['vchrFinOrdrNum'] = ins_partial_inv['json_data']['vchr_fin_ordr_num']
    #         dct_data['intAmtPerPoints'] = 1/settings.LOYALTY_POINT
    #         dct_data['lstItems'] = []
    #         dct_data['blnIGST'] = False
    #         dct_data['strStaffName'] = Userdetails.objects.filter(user_ptr_id = ins_partial_inv['json_data']['int_staff_id']).annotate(str_name=Concat('first_name', Value(' '), 'last_name')).values('str_name').first()['str_name']
    #         dct_data['fk_customer__int_mobile'] = ins_customer['int_mobile']
    #         dct_data['fk_customer__vchr_name'] = ins_customer['vchr_name']
    #         dct_data['fk_customer__vchr_email'] = ins_customer['vchr_email']
    #         dct_data['vchr_remarks'] = ins_partial_inv['json_data']['str_remarks']
    #         lst_items=[]
    #         dct_tax_master = {}
    #         for ins_tax in TaxMaster.objects.values('pk_bint_id','vchr_name'):
    #             dct_tax_master[ins_tax['vchr_name']] = str(ins_tax['pk_bint_id'])
    #         for ins_items_data in ins_partial_inv['json_data']['lst_items']:
    #             ins_items = Item.objects.filter(vchr_item_code = ins_items_data['vchr_item_code'],int_status=1).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master').first()
    #
    #             if not ins_items:
    #                 return Response({'status':'0','message':'Item Not Found'})
    #             for row in range(int(ins_items_data['int_quantity'])):
    #                 dct_item = {}
    #                 dct_item['strItemCode'] = ins_items['vchr_item_code']
    #                 dct_item['intItemId'] = ins_items['pk_bint_id']
    #                 dct_item['strItemName'] = ins_items['vchr_name']
    #                 dct_item['intQuantity'] = ins_items_data['int_quantity']
    #                 # dct_item['intStatus'] = ins_items_data['int_status']
    #                 if ins_items_data['int_status'] == 2:
    #                     dct_item['dctImages'] = ins_items_data['dct_images']
    #
    #                 if len(ins_items_data['json_imei']['imei'])>0:
    #                     dct_item['strImei'] = ins_items_data['json_imei']['imei'][row]
    #                     ins_grn_details = GrnDetails.objects.filter(fk_item_id=ins_items['pk_bint_id'],jsn_imei_avail__contains={'imei_avail':[dct_item['strImei']]}).values('jsn_tax').last()
    #                 # else:
    #                 #     ins_grn_details = GrnDetails.objects.filter(fk_item_id=ins_items['pk_bint_id'],vchr_batch_no=dct_item['strBatchNo']).values('jsn_tax').last()
    #                 dbl_buyback = ins_items_data['dbl_buyback'] / int(ins_items_data['int_quantity'])
    #                 dbl_discount = ins_items_data['dbl_discount'] / int(ins_items_data['int_quantity'])
    #                 dbl_rate=dct_item['dbl_rate'] = (ins_items_data['dbl_amount'] / int(ins_items_data['int_quantity']))
    #                 dbl_tax=0
    #                 dct_item['dblBuyBack'] = round(dbl_buyback,2)
    #                 dct_item['dblDiscount'] = round(dbl_discount,2)
    #                 dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))/100)
    #                 dct_item['dblIGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))
    #                 dct_item['dblIGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0)/100)
    #                 dbl_amt = (dbl_rate-dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))/100)
    #                 dct_item['dblCGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0))
    #                 dct_item['dblCGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)/100)
    #                 dct_item['dblSGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))
    #                 dct_item['dblSGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)/100)
    #                 dct_item['intSaleStatus']=ins_items_data['int_status']
    #
    #                 if dct_item['intSaleStatus'] in [2,3,4]:
    #                     dct_item['dblIGSTPer'] = 0.0
    #                     dct_item['dblCGSTPer'] = 0.0
    #                     dct_item['dblSGSTPer'] = 0.0
    #                     dct_item['dblIGST'] = 0.0
    #                     dct_item['dblCGST'] = 0.0
    #                     dct_item['dblSGST'] = 0.0
    #                 # dct_item['dblRate'] = round(dbl_rate,2)
    #                 # dct_item['dblRate'] = 0
    #                 # if dct_data['blnIGST']:
    #                 #     # dct_item['dblRate'] = round(dbl_rate-dct_item['dblIGST'],2)
    #                 #     dbl_tax += dct_item['dblIGST']
    #                 # else:
    #                 #     dbl_tax += dct_item['dblCGST']
    #                 #     dbl_tax += dct_item['dblSGST']
    #                     # dct_item['dblRate'] = round(dbl_rate-dct_item['dblCGST']-dct_item['dblSGST'],2)
    #                 # dct_item['dblAmount'] = round(dct_item['dblRate'] - dct_item['dblBuyBack'] - dct_item['dblDiscount']+dbl_tax,2)
    #                 # dct_item['dblAmount'] = 0
    #                 dct_item['dblAmount'] = round(dbl_rate-dbl_buyback-dbl_discount,2)
    #                 # dct_item['status'] = False
    #                 dct_item['jsonTax']={"dblIGST":dct_item['dblIGST'],"dblCGST": dct_item['dblCGST'],"dblSGST":  dct_item['dblSGST']}
    #                 ins_item=Item.objects.filter(vchr_item_code=ins_items_data['vchr_item_code']).values('fk_product__vchr_name','fk_brand__vchr_name').first()
    #                 dct_item['strProductName']=ins_item['fk_product__vchr_name']
    #                 dct_item['strBrandName']=ins_item['fk_brand__vchr_name']
    #                 dct_data['fk_branch__vchr_name'] = ins_partial_inv['json_data'].get('str_branch')
    #
    #                 lst_items.append(dct_item)
    #
    #         return Response({'status':1,'master':dct_data,"details":lst_items})
    #     except Exception as e:
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
    #         return Response({'status':'0','message':str(e)})


class TheftFollowup(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            # ins_sales=SalesDetails.objects.filter(fk_item__vchr_item_code=request.data.get('vchr_item_code'),json_imei__contains=[request.data.get('imei')]).values('fk_sales_master__dat_invoice','dbl_amount').first()
            # int_dep_percentage=Depreciation.objects.filter(int_days_upto__lte=request.data.get('int_days_missing')).order_by('-int_days_upto').first()['int_dep_percentage']
            # int_amount=ins_sales['dbl_amount']
            # TheftDetails.objects.create(dat_purchase=ins_sales['fk_sales_master__dat_invoice'],\
            #                             int_days_missing=request.data.get('int_days_missing'),\
            #                             int_depreciation_amt=int_dep_percentage*int_amount/100,\
            #                             fk_created_id=request.user.id,\
            #                             dat_created_id=datetime.now()\
            #                             )
            # my_file = request.FILES.get('image')
            # fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            # filename = fs.save(my_file.name, my_file)
            # str_profpic = fs.url(filename)

            my_file = request.FILES.get('ntc_cert')
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(request.data['itemImei']+my_file.name, my_file)
            vchr_ntc_cert = fs.url(filename)
            my_file = request.FILES.get('not_sub_letter')
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(request.data['itemImei']+my_file.name, my_file)
            vchr_not_sub_letter = fs.url(filename)
            my_file = request.FILES.get('gdot_pro_cert')
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(request.data['itemImei']+my_file.name, my_file)
            vchr_gdot_pro_cert = fs.url(filename)
            my_file = request.FILES.get('police_int_letter')
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(request.data['itemImei']+my_file.name, my_file)
            vchr_police_int_letter = fs.url(filename)
            my_file = request.FILES.get('id_proof')
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(request.data['itemImei']+my_file.name, my_file)
            vchr_id_proof = fs.url(filename)
            my_file = request.FILES.get('dig_signature')
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(request.data['itemImei']+my_file.name, my_file)
            vchr_dig_signature = fs.url(filename)
            json_documents=[vchr_ntc_cert,vchr_not_sub_letter,vchr_gdot_pro_cert,vchr_police_int_letter,vchr_id_proof,vchr_dig_signature]
            ins_part=PartialInvoice.objects.filter(pk_bint_id=request.data.get('partialId'))
            json_data=ins_part.values('json_data').first()['json_data']

            dct_upload={'vchr_staff_code':request.user.username,"service_id":int(json_data['lst_items'][0]['int_service_id']),"json_documents":json_documents,"bln_upload":True}
            url=settings.BI_HOSTNAME + '/service/up_down_documents/'
            res_data = requests.post(url,json=dct_upload)

            if res_data.json()['status']==1:

                        json_data['lst_items'][0]['json_documents']=[vchr_ntc_cert,vchr_not_sub_letter,vchr_gdot_pro_cert,vchr_police_int_letter,vchr_id_proof,vchr_dig_signature]
                        json_data['lst_items'][0]['vchr_job_status']='MISSING & PENDING'
                        ins_part.update(json_data=json_data)

            return Response({'status':1})

        except Exception as e:
            if str(e) == "'status'":
                return Response({'status': 'Failed','data':res_data.json().get('message')})
            else:
                return Response({'result':0,'reason':e})


class  ServiceAddAssigned(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                ins_partial=PartialInvoice.objects.filter(pk_bint_id=request.data.get('partialId')).values('json_data','int_enq_master_id')
                json_data=ins_partial.first()['json_data']
                json_data['fk_assigned']=request.data.get('id')
                json_data['staff_name_assigned']=request.data.get('name')
                json_data['lst_items'][0]['vchr_job_status']='WARRANTY CLAIM ASSIGNED'
                ins_partial.update(json_data=json_data)
                url=settings.BI_HOSTNAME + '/service/add_assigned/'
                res_data=requests.post(url=url,json={'int_job_master_id':ins_partial.first()['int_enq_master_id'],'Username':request.data.get('username'),'name':request.data.get('name')})
                # ins_partial.update(json_data=json_data)
                if res_data.json()['status']==1:
                        pass

                return Response({'status':1})

        except Exception as e:
            if str(e) == "'status'":
                return Response({'status': 'Failed','data':res_data.json().get('message')})
            else:
                return Response({'result':0,'reason':e})

class ServiceCenterAndGDPFollowup(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:

              with transaction.atomic():
                    """add receipt"""
                    dat_issue = request.data.get('datIssue')
                    int_phone = request.data.get('customerPhone')
                    int_fop = request.data.get('intFop')
                    dbl_amount = request.data.get('amount')
                    vchr_remarks = request.data.get('remarks')
                    int_pstatus=request.data.get('intPaymentStatus')
                    int_receipt_type=request.data.get('intReceiptType')
                    int_card_no=request.data.get('vchrCardNUmber')
                    int_bank_id=request.data.get('intBankId')
                    if int_fop:
                        IntCustomerType=CustomerDetails.objects.filter(int_mobile=int_phone).values("int_cust_type").first()['int_cust_type'] #1:credit customer 2:corporate customers
                        fk_customer_id=CustomerDetails.objects.filter(int_mobile=int_phone).values("pk_bint_id").first()['pk_bint_id']

                        ins_document = Document.objects.select_for_update().filter(vchr_module_name = "RECEIPT",fk_branch_id = request.user.userdetails.fk_branch_id).first()
                        # if not ins_document:

                        #     ins_document = Document.objects.create(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code,int_number = 1)
                        #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                        #     ins_document.int_number = ins_document.int_number+1
                        #     ins_document.save()
                        # else:
                        #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                        #     Document.objects.filter(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).update(int_number = ins_document.int_number+1)

                        # LG 27-06-2020
                        if ins_document:
                            str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                            Document.objects.filter(vchr_module_name = "RECEIPT",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                        else:
                            ins_document_search = Document.objects.filter(vchr_module_name = 'RECEIPT',fk_branch_id = None).first()
                            if ins_document_search:
                                ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                                ins_document = Document.objects.create(vchr_module_name = 'RECEIPT', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                                str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                                ins_document.int_number = ins_document.int_number+1
                                ins_document.save()
                            else:
                                return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                        # ins_receipt = Receipt.objects.create_recpt_num(str_inv_num)
                        ins_receipt = Receipt.objects.create(vchr_receipt_num=str_inv_num,vchr_card_num=int_card_no,vchr_transaction_id=request.data.get('vchrReferenceNumber'),dat_issue = dat_issue,fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.today(),int_doc_status = 0,int_pstatus=int_pstatus,int_receipt_type=int_receipt_type,fk_branch = request.user.userdetails.fk_branch,fk_bank_id = int_bank_id)
                        if int_fop in [1,2,3,7,8,9] and IntCustomerType in [1,2]:
                            CustomerDetails.objects.filter(pk_bint_id=fk_customer_id).update(dbl_credit_balance=F('dbl_credit_balance')+dbl_amount)

                        if int_fop not in [4,5,6]:
                            if not create_posting_data(request,ins_receipt.pk_bint_id):
                                return Response({'status':0 , 'data' : 'Posting Failed'})

                    ins_partial=PartialInvoice.objects.filter(int_enq_master_id=request.data.get('job_id')).values('json_data')
                    json_data=ins_partial.first()['json_data']
                    if request.data.get('dat_exp_delivery'):
                        json_data['lst_items'][0]['dat_exp_delivery']=request.data.get('dat_exp_delivery')
                    if request.data.get('status'):
                        json_data['lst_items'][0]['vchr_job_status']=request.data.get('status')
                    if request.data.get('image'):
                        json_data['image']=request.data.get('image')
                    if request.data.get('service_amt'):
                        json_data['lst_items'][0]['int_service_expense']=request.data.get('service_amt')
                    if request.data.get('vchr_previous_status'):
                        json_data['lst_items'][0]['vchr_gdp_type']=request.data.get('vchr_previous_status')
                    if request.data.get('status') not in ['SENT TO SERVICE CENTER','GDP MYG CARE','GDP SERVICE CENTER','GDEW MYG CARE','GDEW SERVICE CENTER'] and not request.data.get('service_amt'):
                       url=settings.BI_HOSTNAME + '/service/change_status/'
                       res_data=requests.post(url=url,json={'vchr_staff_code':request.user.username,'service_id':json_data['lst_items'][0]['int_service_id'],'status':request.data.get('status')})
                       if res_data.json()['status']==1:
                            pass
                    # bln foward is used in case of a forwarded item,bln_gdp is  gdp/gdew case and the mail is not sent
                    if (request.data.get('status')=='SERVICED' and not request.data.get('bln_forward') and  not request.data.get('bln_gdp')) or request.data.get('bln_sent_mail'):
                                        html_head = """<!doctype html>
                                                        <html>
                                                        <head>
                                                        <meta charset="utf-8">
                                                        <title>Untitled Document</title>
                                                        </head>
                                                        <style>
                                                    						  .container{
                                                    										  margin: auto;
                                                    										  width: 1150px;
                                                    						            }
                                                    		                     .header{
                                                    										  margin: auto;
                                                    										  width: 1150px;
                                                    								          height:126px;
                                                        									  border-bottom: 1px solid #8c8b8b;
                                                    						            }
                                                    							  .imgbox{
                                                                                             width: 116px;
                                                    								         float:left;
                                                    							          }
                                                    								  .left1{
                                                    									  width:575;
                                                    									  float: left;
                                                    									  text-align: left;
                                                    								  }
                                                    								  .right1{
                                                    									   width:575;
                                                    									  float: right;
                                                    									  text-align: right;
                                                    								  }
                                                    						    .address{
                                                    										  width: 1034px;
                                                    										  text-align: right;
                                                    										  float: right;
                                                    									}
                                                    							    .box{
                                                                                              width: 1150px;
                                                    										  float: left;
                                                    									}
                                                    							 .clear{
                                                    								  		  clear: both;
                                                    								   }
                                                    		                      .clr{
                                                    										  color: #0b880b;
                                                    									      text-align: center;
                                                    		                         }
                                                    		  				    .left{
                                                    										   float: left;
                                                    										   width: 500px;
                                                    								           text-align: left;
                                                    								           padding-left: 16px;
                                                    								           border-left: 2px solid dodgerblue;
                                                    		                         }
                                                    		 				   .right{
                                                    										   float: right;
                                                    										   width: 500px;
                                                    							               text-align: right;
                                                    							               color: slategray;
                                                    							               padding-right: 19px;
                                                    		  					     }
                                                    		                      .m2{
                                                    			                  			      margin-bottom: 14px;
                                                    		                       }
                                                    							 h3{
                                                    								          color: #FF7A29;
                                                    							   }
                                                    						  .bgclr{
                                                    								    width: 100%;
                                                    									background-color: #f1f1f191;
                                                    									float: left;
                                                    							        margin-bottom: 14px;
                                                    						        }
                                                    					      .addbx{
                                                                                    float: right;
                                                    							    text-align: right;
                                                    							        width: 240px;
                                                    								}
                                                    		                .addbx p{
                                                    			                     margin-bottom: 0px;
                                                    							     text-align: left;
                                                    		                        }
                                                    		  					.l1{
                                                    									float: left;
                                                    								     width: 120px;
                                                    		  					   }
                                                    		  					.ri{
                                                    									float:right;
                                                    								     width: 102px;
                                                    		  					   }
                                                    					   table, td, th{
                                                    							  border: 1px solid #c5c4c4;
                                                    							  text-align: left;
                                                    								   }
                                                    						     table{
                                                    							  border-collapse: collapse;
                                                    							  width: 100%;
                                                    							     }
                                                    						   th, td{
                                                    							  padding: 15px;
                                                    							  TEXT-ALIGN: left;
                                                    							     }
                                                    	  </style>"""

                                        html_image = html_head + """<body>
                                                    <div class="container">
                                        	                       	<div style="float: left;width: 500px;text-align: left;">
                                        										</div>
                                        											   <div style="float: right;width: 250px;text-align: left;">
                                        													 </div>
                                        	                           <div class="clear"></div>
                                        		                    <h1 class="margin clr" style="margin-top:32px;">Your item has been serviced and is available for dispensing at the following MYG branch</h1>
                                        	                                     <p style="margin-top:32px;font-size: 20px;">Kindly pick up the item when you are ready! <b>""" + datetime.today().date().strftime ("%d/%m/%Y")+ """</b></p>
                                        	                                   <p>Service details are as follows :-</p> <b>"""

                                        serviced_items=str("ITEM NAME : " + str(json_data['lst_items'][0]['vchr_item_name'])+"<br>BRANCH NAME : "+str(json_data['str_branch'])+"<br>JOB NUMBER : " +str(json_data['vchr_job_num']))

                                        html_data = html_image + serviced_items+ """</b></div>
                                                                </body>
                                                                </html>"""

                                        to = [CustomerDetails.objects.filter(int_mobile=json_data['int_cust_mob']).values('vchr_email').first()['vchr_email']]
                                        # to=['kavya.r@travidux.in']
                                        server = smtplib.SMTP('smtp.pepipost.com', 587)
                                        server.starttls()

                                        server.login("shafeer","Tdx@9846100662")
                                        msg = MIMEMultipart()
                                        msg['Subject'] = "Your item has been serviced"
                                        msg['To']=to[0]
                                        msgAlternative = MIMEMultipart('alternative')
                                        msg.attach(msgAlternative)

                                        str_html = """<b> <i></i></b><br>"""+html_data+"""<br>"""

                                        msgText = MIMEText(str_html, 'html')
                                        msgAlternative.attach(msgText)

                                        server.sendmail("info@enquirytrack.com",to,msg.as_string())
                                        server.quit()
                    ins_partial.update(json_data=json_data)

                    return Response({'status':1})

        except Exception as e:
            if str(e) == "'status'":
                return Response({'status': 'Failed','data':res_data.json().get('message')})
            else:
                return Response({'result':0,'reason':e})


class CompleteApprovalMissing(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            ins_partial=PartialInvoice.objects.filter(int_enq_master_id=request.data.get('job_id')).values('json_data','pk_bint_id')
            json_data=ins_partial.first()['json_data']
            json_data['lst_items'][0]['vchr_job_status']='MISSING & APPROVED'
            ins_document = Document.objects.get(vchr_module_name = 'RECEIPT',fk_branch_id = request.user.userdetails.fk_branch_id).first()
            # str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
            # ins_document.int_number = ins_document.int_number+1
            # ins_document.save()

            # LG 27-06-2020
            if ins_document:
                str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                Document.objects.filter(vchr_module_name = "RECEIPT",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
            else:
                ins_document_search = Document.objects.filter(vchr_module_name = 'RECEIPT',fk_branch_id = None).first()
                if ins_document_search:
                    ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                    ins_document = Document.objects.create(vchr_module_name = 'RECEIPT', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                    str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                    ins_document.int_number = ins_document.int_number+1
                    ins_document.save()
                else:
                    return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

            ins_receipt = Receipt.objects.create_recpt_num(str_inv_num)
            Receipt.objects.filter(pk_bint_id = ins_receipt.pk_bint_id).update(int_fop = 1,int_doc_status =0,int_pstatus = 0,int_receipt_type = 3,dat_created = datetime.now(),dat_issue = datetime.now(),dbl_amount=request.data.get('int_amount'),fk_customer_id=json_data['int_cust_id'])
            ins_partial.update(json_data=json_data,int_active=0)
            return Response({'status':1})
        except Exception as e:
            return Response({'error_status': 'Failed','data':e})

# class WarrantyFollowup(APIView):
#     permission_classes=[AllowAny]
#     def post(self,request):
#         try:
#             with transaction.atomic():
#                     ins_p=PartialInvoice(int_enq_master_id=request.data['int_enq_master_id'],dat_created=datetime.now(),int_status=6)
#                     json_data=request.data
#                     # =================================================================================
#                     ins_staff = Userdetails.objects.filter(username = request.data.get('vchr_staff_code'),is_active = True).values('user_ptr_id','first_name','last_name').first()
#                     ins_branch = Branch.objects.filter(vchr_code = request.data.get('vchr_branch_code')).values('pk_bint_id','vchr_name','fk_states_id').first()
#
#
#
#                     if ins_staff:
#                         json_data['int_staff_id'] = ins_staff['user_ptr_id']
#                         json_data['str_staff_name'] = ins_staff['first_name']+' '+ins_staff['last_name']
#                     else:
#                         return Response({'error_status': 'NO','message':'No User in POS with user code '+request.data.get('vchr_staff_code')})
#
#                     if ins_branch:
#                         json_data['int_branch_id'] = ins_branch['pk_bint_id']
#                         json_data['str_branch'] = ins_branch['vchr_name']
#                     else:
#                         return Response({'error_status':'NO','message':'No Branch in POS with Branch code '+request.data.get('vchr_branch_code')})
#
#                     ins_state = None
#                     str_cust_name = request.data.get('vchr_cust_name')
#                     str_cust_email = request.data.get('vchr_cust_email',None)
#                     int_cust_mob = request.data.get('int_cust_mob')
#
#                     if request.data.get('vchr_state_code'):
#                         ins_state = States.objects.filter(vchr_code = request.data.get('vchr_state_code')).first()
#                     ins_district = None
#                     if request.data.get('vchr_district'):
#                         ins_district = District.objects.filter(vchr_name = request.data.get('vchr_district')).first()
#                         if not ins_district:
#                             ins_district = District.objects.create(vchr_name = request.data.get('vchr_district'),fk_state=ins_state)
#                         if not ins_state:
#                             ins_state = ins_district.fk_state
#                     ins_location = None
#                     if request.data.get('vchr_location'):
#                         ins_location = Location.objects.filter(vchr_name__contains=request.data.get('vchr_location',None),vchr_pin_code=request.data.get('vchr_pin_code',None)).first()
#                         if not ins_location:
#                             ins_location = Location.objects.create(vchr_name=request.data.get('vchr_location',None),vchr_pin_code=request.data.get('vchr_pin_code',None))
#                         if not ins_district:
#                             ins_district = ins_location.fk_district
#                         if not ins_state:
#                             ins_state = ins_district.fk_state
#                     if not ins_state and ins_branch:
#                         ins_state =  States.objects.filter(pk_bint_id=ins_branch['fk_states_id']).first()
#                     ins_customer = CustomerDetails.objects.filter(vchr_name = str_cust_name,int_mobile = int_cust_mob).values('pk_bint_id').first()
#                     if not ins_customer:
#                         ins_customer = CustomerDetails.objects.create(vchr_name = str_cust_name,vchr_email = str_cust_email,int_mobile = int_cust_mob,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)
#                         json_data['int_cust_id'] = ins_customer.pk_bint_id
#                     else:
#                         json_data['int_cust_id'] = ins_customer['pk_bint_id']
#                         ins_customer = CustomerDetails.objects.filter(vchr_name = str_cust_name,vchr_email = str_cust_email,int_mobile = int_cust_mob,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)
#                         if not ins_customer:
#                             CustomerDetails.objects.filter(pk_bint_id=json_data['int_cust_id']).update(vchr_email = str_cust_email,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)
#
#
#                     # =================================================================================
#
#
#                     json_data['lst_items']=request.data['lst_item']
#                     json_data['int_branch_id']=Branch.objects.filter(vchr_code=json_data['vchr_branch_code']).values('pk_bint_id').first()['pk_bint_id']
#                     del json_data['lst_item']
#                     del json_data['int_enq_master_id']
#                     json_data['str_cust_name']=json_data['vchr_cust_name']
#                     del json_data['vchr_cust_name']
#
#                     ins_p.json_data=json_data
#                     ins_p.save()
#             return Response({'status':1})
#
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
#             return Response({'status':'0','message':str(e)})
#
# #
# class TheftFollowup(APIView):
#     permission_classes=[IsAuthenticated]
#     def get(self,request):
#         try:
#             int_dep_percentage=Depreciation.objects.filter(int_days_upto__lte=request.data.get('int_days_missing')).order_by('-int_days_upto').first()['int_dep_percentage']
#             int_amount =
#             TheftDetails.objects.create(dat_purchase=request.data.get('dat_purchase'),\
#                                         int_days_missing=request.data.get('int_days_missing'),\
#                                         int_depreciation_amt=int_dep_percentage*,\
#                                         fk_created_id=request.user.id,
#                                         dat_created_id=datetime.now(),
#                                         fk_partial_invoice_id=request.data.get('partial_id'),
#                                         fk_purchase_branch_id=Branch.objects.filter(vchr_name=request.data.get('branch')).values('pk_bint_id').first()['pk_bint_id']
#                                         )



class ReturnItemInvoice(APIView):
    """
        To add invoice of details of return item
        param : sales_details_id,list of item details, lst return details
        return : success
    """
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                

                dct_data = request.data
                #import pdb; pdb.set_trace()
                lst_item_detail = json.loads(dct_data.get('lstItemDetails'))
                lst_return_details = json.loads(dct_data.get('dctReturnId'))
                int_sale_details_id = eval(dct_data['salesReturnId'])[0]
                # LG
                
                ins_sale_detail = SalesDetails.objects.filter(pk_bint_id = int_sale_details_id).values('fk_master_id','fk_master_id__fk_branch_id','fk_master_id__fk_branch_id__vchr_code','fk_master_id__fk_customer_id','fk_master_id__fk_staff_id','fk_master_id__fk_branch_id__fk_states_id','fk_master_id__jsn_addition','fk_master_id__jsn_deduction','fk_master_id__vchr_invoice_num').first()
                str_old_inv_no = ins_sale_detail["fk_master_id__vchr_invoice_num"]
                if (request.user.userdetails.fk_branch_id != ins_sale_detail['fk_master_id__fk_branch_id']) and (request.user.userdetails.fk_branch.vchr_code == 'AGY' or ins_sale_detail['fk_master_id__fk_branch_id__vchr_code'] =='AGY'):
                    return Response({'status':4,'message':'Return is not possible between Angamali and other branches'})
                # ins_document = Document.objects.filter(vchr_module_name = "INVOICE",vchr_short_code = ins_sale_detail['fk_master_id__fk_branch_id__vchr_code']).first()
                # if not ins_document:
                #     ins_document = Document.objects.create(vchr_module_name = "INVOICE",vchr_short_code = ins_sale_detail['fk_master_id__fk_branch_id__vchr_code'],int_number = 1)
                # str_inv_num = 'INV-'+ins_document.vchr_short_code.upper()+'-'+str(ins_document.int_number).zfill(4)
                # ins_document.int_number = ins_document.int_number+1
                # ins_document.save()

                # ========================================================================================
                ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'SALES RETURN',fk_branch_id=request.user.userdetails.fk_branch_id).first()
                # if ins_document:
                #     pass
                # else:
                #     ins_document=Document(vchr_short_code='SRN',
                #                          fk_branch_id=request.user.userdetails.fk_branch_id,
                #                          vchr_module_name='SALES RETURN',
                #                          int_number=0
                #                             )
                # str_code = ins_document.vchr_short_code
                # int_doc_num = ins_document.int_number + 1
                # ins_document.int_number = int_doc_num
                # str_number = str(int_doc_num).zfill(4)
                # str_document = str_code + '-'+  ins_sale_detail['fk_master_id__fk_branch_id__vchr_code']+'-'+ str_number
                # ins_document.save()

                # LG 27-06-2020
                if ins_document:
                    str_document = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                    Document.objects.filter(vchr_module_name = "SALES RETURN",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                else:
                    ins_document_search = Document.objects.filter(vchr_module_name = 'SALES RETURN',fk_branch_id = None).first()
                    if ins_document_search:
                        ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                        ins_document = Document.objects.create(vchr_module_name = 'SALES RETURN', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                        str_document = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                        ins_document.int_number = ins_document.int_number+1
                        ins_document.save()
                    else:
                        return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                str_reciept_num = str_document
                # ins_sales_master = SalesMaster.objects.create_inv_num(str_document)
                ins_sales_master = SalesMaster.objects.create(
                                                fk_customer_id = ins_sale_detail['fk_master_id__fk_customer_id'],
                                                fk_branch_id = request.user.userdetails.fk_branch_id,
                                                vchr_invoice_num = str_document,
                                                dat_invoice = date.today(),
                                                vchr_remarks = dct_data['strRemarks'],
                                                dat_created = datetime.now(),
                                                int_doc_status = 1,
                                                dbl_total_amt = round(float(dct_data['intGrandTot'])*(-1),2) if dct_data['intGrandTot'] else 0,
                                                dbl_rounding_off = 0,
                                                jsn_addition = {},
                                                jsn_deduction = {},
                                                dbl_total_tax = round(float(dct_data['intTotIGST']),2) + round(float(dct_data['intTotSGST']),2) + round(float(dct_data['intTotCGST']),2)+ round(float(dct_data['intTotKFC']),2),
                                                dbl_discount = float(dct_data['intDiscount'])*(-1) if dct_data['intDiscount'] else 0,
                                                json_tax = {'dblIGST': round(float(dct_data['intTotIGST']),2),'dblCGST':round(float(dct_data['intTotCGST']),2),'dblSGST':round(float(dct_data['intTotSGST']),2),'dblKFC':round(float(dct_data['intTotKFC']),2)},
                                                dbl_buyback =  float(dct_data['intBuyBack'])*(-1) if dct_data['intBuyBack'] else 0,
                                                fk_staff_id = request.user.id,
                                                fk_created = request.user.userdetails
                                               )
                ins_sales_master.save()
                # for additions and deductions in the case of return all items
                if dct_data['blnSalesReturnAll'] == 'true':
                    ins_sales_master.jsn_addition = json.dumps(ins_sale_detail['fk_master_id__jsn_addition'])
                    ins_sales_master.jsn_deduction = json.dumps(ins_sale_detail['fk_master_id__jsn_deduction'])
                    ins_sales_master.save()
                # for additions and deductions in the case of return all items
                json_total_tax = {'dblIGST':0,'dblCGST':0,'dblSGST':0,'dblKFC':0}
                total_tax=0
                total_discount=0
                total_buy_back = 0
                int_cust_type=SalesCustomerDetails.objects.filter(pk_bint_id=ins_sale_detail['fk_master_id__fk_customer_id']).values('fk_customer_id__int_cust_type').first().get('fk_customer_id__int_cust_type')
                if lst_item_detail:
                    lst_return_data = []
                    count=-1

                    lst_item_id = [x['intItemId'] for x in lst_item_detail]
                    dct_item_sup_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_supp_amnt'))
                    dct_item_mop_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_mop'))
                    dct_item_mrp_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_mrp'))
                    dct_item_cost_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_cost_amnt'))
                    dct_item_myg_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','int_myg_amt'))
                    dct_item_dealer_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_dealer_amt'))
                    for lst_item_details in lst_item_detail:
                        count +=1
                        dct_tax = {'dblCGST':round(-1*lst_item_details.get('dblCGST',0),2) if int_cust_type!=3 else 0, 'dblIGST':round(-1*lst_item_details.get('dblIGST',0),2) if int_cust_type!=3 else 0, 'dblIGST%':lst_item_details.get('dblIGSTPer',0) if int_cust_type!=3 else 0, 'dblSGST%':lst_item_details.get('dblSGSTPer',0) if int_cust_type!=3 else 0, 'dblKFC':round(-1*lst_item_details.get('dblKFC',0),2) if int_cust_type!=3 else 0, 'dblCGST%':lst_item_details.get('dblCGSTPer',0) if int_cust_type!=3 else 0, 'dblSGST':round(-1*lst_item_details.get('dblSGST',0),2) if int_cust_type!=3 else 0, 'dblKFC%':lst_item_details.get('dblKFCPer',0) if int_cust_type!=3 else 0}
                        dbl_tax = sum(value for key,value in dct_tax.items() if '%' not in key)
                        json_total_tax['dblIGST'] += dct_tax['dblIGST']
                        json_total_tax['dblCGST'] += dct_tax['dblCGST']
                        json_total_tax['dblSGST'] += dct_tax['dblSGST']
                        json_total_tax['dblKFC'] += dct_tax['dblKFC']
                        total_tax +=dbl_tax
                        total_discount += lst_item_details.get('dblDiscount',0)*-1
                        total_buy_back += lst_item_details.get('dblBuyBack',0)*-1
                        dct_item_filter_tr={}
                        dct_item_filter_tr['fk_details__fk_item_id'] =lst_item_details['intItemId']
                        dct_item_filter_grn={}
                        dct_item_filter_grn['fk_item_id'] =lst_item_details['intItemId']
                        dct_item_filter_bs={}
                        dct_item_filter_bs['fk_details__fk_item_id'] =lst_item_details['intItemId']
                        if check_if_imei_exist(lst_item_details['strImei'],bln_transit=True,dct_filter_bs=dct_item_filter_bs,dct_filter_grn=dct_item_filter_grn,dct_filter_st=dct_item_filter_tr):
                            return Response({'status':0,'blnStock':True,'message':str(lst_item_details['strImei'])+' already exists in stock'})
                        
                        item_total_tax_percent = 0
                        if lst_item_details.get('dblIGSTPer') != 0 and lst_item_details.get('dblKFCPer') == 0:
                            item_total_tax_percent = lst_item_details.get('dblIGSTPer')
                        else:
                            item_total_tax_percent = lst_item_details.get('dblSGSTPer',0) + lst_item_details.get('dblCGSTPer',0) + lst_item_details.get('dblKFCPer',0)
                        ins_sales_details = SalesDetails(fk_master = ins_sales_master,
                                                    fk_item_id = lst_item_details['intItemId'],
                                                    int_qty = int(lst_item_details['intQuantity']),
                                                    dbl_amount = round(float(lst_item_details['dblRate'])*(-1),2) if lst_item_details['dblRate'] else 0,
                                                    # dbl_selling_price = float(float(lst_item_details['dblRate']) + lst_item_details['dblSGST'] + lst_item_details['dblCGST'] + lst_item_details['dblIGST'] + lst_item_details.get('dblKFC',0) - (float(lst_item_details['dblDiscount']) + float(lst_item_details['dblBuyBack'])))*(-1) if lst_item_details['dblRate'] else 0,
                                                    dbl_selling_price = (float(lst_item_details['dblAmount'])*(-1)) if lst_item_details['dblAmount'] else 0,
                                                    dbl_tax = dbl_tax,
                                                    dbl_discount = lst_item_details.get('dblDiscount',0)*-1,
                                                    dbl_buyback = lst_item_details.get('dblBuyBack',0)*-1,
                                                    json_tax =  dct_tax,
                                                    json_imei = [lst_item_details['strImei']] if lst_item_details['strImei'] else [],
                                                    int_sales_status = 0,
                                                    int_doc_status = 1,
                                                    dbl_supplier_amount = 0,
                                                    dbl_indirect_discount=lst_item_details.get('dblIndirectDis',0)*-1,
                                                    # dbl_supplier_amount = (dct_item_sup_amnt.get(lst_item_details['intItemId'],0.0)) *-1,
                                                    dbl_dealer_price = (dct_item_dealer_amnt.get(lst_item_details['intItemId']) or 0.0) *-1,
                                                    dbl_cost_price = (dct_item_cost_amnt.get(lst_item_details['intItemId']) or 0.0) *-1,
                                                    dbl_mrp = (dct_item_mrp_amnt.get(lst_item_details['intItemId']) or 0.0) *-1,
                                                    dbl_mop = (dct_item_mop_amnt.get(lst_item_details['intItemId']) or 0.0) *-1,
                                                    dbl_tax_percentage = item_total_tax_percent
                                                    )
                        ins_sales_details.save()
                        str_img_path=''
                        
                        if lst_item_details['strItemCode'] not in ['GDC00001','GDC00002'] :
                        # Check if the return imei in jsn_imei(List of all imei )field branch_stock_details ,then append the return imei to the jsn_imei_avail(list of available imei) field.
                            if request.user.userdetails.fk_branch_id == ins_sale_detail['fk_master_id__fk_branch_id']:
                                ins_branch_stock_details = BranchStockDetails.objects.filter(jsn_imei__contains={"imei": [lst_item_details['strImei']]},fk_master__fk_branch_id=request.user.userdetails.fk_branch_id).first()
                                if ins_branch_stock_details:
                                    if lst_item_details['strImei'] not in ins_branch_stock_details.jsn_imei_avail['imei']:
                                        ins_branch_stock_details.jsn_imei_avail['imei'].append(lst_item_details['strImei'])
                                        ins_branch_stock_details.int_qty = ins_branch_stock_details.int_qty + 1
                                        ins_branch_stock_details.save()
                                else:
                                    ins_branch_stock_details = BranchStockDetails.objects.filter(jsn_batch_no__contains={"batch": [lst_item_details['strImei']]},fk_master__fk_branch_id=request.user.userdetails.fk_branch_id).first()

                                    if lst_item_details['strImei'] in ins_branch_stock_details.jsn_batch_no['batch'] :
                                        ins_branch_stock_details.int_qty = ins_branch_stock_details.int_qty + 1
                                        ins_branch_stock_details.save()
                                    else:
                                        ins_branch_stock_details.jsn_batch_no['batch'].append(lst_item_details['strImei'])
                                        ins_branch_stock_details.int_qty = ins_branch_stock_details.int_qty + 1
                                        ins_branch_stock_details.save()

                                ins_branch_stock_imei_details = BranchStockImeiDetails.objects.filter(fk_details_id=ins_branch_stock_details.pk_bint_id,jsn_imei_reached__contains={"imei": [lst_item_details['strImei']]}).first()
                                if ins_branch_stock_imei_details:
                                    if lst_item_details['strImei'] not in ins_branch_stock_imei_details.jsn_imei['imei']:
                                        ins_branch_stock_imei_details.jsn_imei['imei'].append(lst_item_details['strImei'])
                                        ins_branch_stock_imei_details.int_qty = ins_branch_stock_imei_details.int_qty + 1
                                        ins_branch_stock_imei_details.save()
                                else:
                                    ins_branch_stock_imei_details = BranchStockImeiDetails.objects.filter(fk_details_id=ins_branch_stock_details.pk_bint_id,jsn_batch_reached__contains={"batch": [lst_item_details['strImei']]}).first()
                                    if ins_branch_stock_imei_details:
                                        if lst_item_details['strImei'] in ins_branch_stock_imei_details.jsn_batch_no['batch']:
                                            ins_branch_stock_imei_details.int_qty = ins_branch_stock_imei_details.int_qty + 1
                                            ins_branch_stock_imei_details.save()
                                        else:
                                            ins_branch_stock_imei_details.jsn_batch_no['batch'].append(lst_item_details['strImei'])
                                            ins_branch_stock_imei_details.int_qty = ins_branch_stock_imei_details.int_qty + 1
                                            ins_branch_stock_imei_details.save()

                                if  request.FILES.get(str(lst_item_details['strImei'])+'-'+str(count)):
                                    img_item =  request.FILES.get(str(lst_item_details['strImei'])+'-'+str(count))
                                    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                                    str_img = fs.save(img_item.name, img_item)
                                    str_img_path = fs.url(str_img)

                            else:
                                
                                if request.user.userdetails.fk_branch.vchr_code != 'AGY' and ins_sale_detail['fk_master_id__fk_branch_id__vchr_code'] !='AGY':
                                    imei_stock = {'imei':[]}
                                    batch_stock = {'batch':[]}
                                    invoiced_branch_check = BranchStockDetails.objects.filter(jsn_imei__contains={"imei": [lst_item_details['strImei']]},fk_master__fk_branch_id=ins_sale_detail['fk_master_id__fk_branch_id']).values().first()
                                    invoiced_check_stock_master = BranchStockMaster.objects.filter(pk_bint_id = invoiced_branch_check['fk_master_id']).values().first()
                                    ins_item = Item.objects.filter(vchr_item_code = lst_item_details['strItemCode']).values('pk_bint_id','fk_item_category__json_tax_master','dbl_mop').first()
                                    if invoiced_branch_check:
                                        dict_data={}
                                        inst_tax = TaxMaster.objects.values()
                                        int_cgst = inst_tax.filter(vchr_name='CGST').values('pk_bint_id').first().get('pk_bint_id')
                                        int_igst = inst_tax.filter(vchr_name='IGST').values('pk_bint_id').first().get('pk_bint_id')
                                        int_sgst = inst_tax.filter(vchr_name='SGST').values('pk_bint_id').first().get('pk_bint_id')
                                        int_kfc = inst_tax.filter(vchr_name='KFC').values('pk_bint_id').first().get('pk_bint_id')

                                        dict_data["sgstRate"] =(ins_item['fk_item_category__json_tax_master'].get(str(int_sgst)) or 0)
                                        dict_data["cessRate"] = (ins_item['fk_item_category__json_tax_master'].get(str(int_kfc)) or 0)
                                        dict_data["igstRate"] = (ins_item['fk_item_category__json_tax_master'].get(str(int_igst)) or 0)
                                        dict_data["cgstRate"] =(ins_item['fk_item_category__json_tax_master'].get(str(int_cgst)) or 0)


                                        int_cgst_sum = (dict_data["cgstRate"]*ins_item['dbl_mop'])/100
                                        int_igst_sum = (dict_data["igstRate"]*ins_item['dbl_mop'])/100
                                        int_cess_sum = (dict_data["cessRate"]*ins_item['dbl_mop'])/100
                                        int_sgst_sum = (dict_data["sgstRate"]*ins_item['dbl_mop'])/100
                                        dict_jsn_tax = {}
                                        dbl_total_tax = 0
                                        if ins_sale_detail['fk_master_id__fk_branch_id__fk_states_id'] == request.user.userdetails.fk_branch.fk_states_id:
                                            dict_jsn_tax['CGST'] = int_cgst_sum
                                            dict_jsn_tax['SGST'] = int_sgst_sum
                                            dbl_total_tax = int_cgst_sum+int_sgst_sum
                                        else:
                                            dict_jsn_tax['IGST'] = int_igst_sum
                                            dbl_total_tax = int_igst_sum

                                        ins_stock_master = BranchStockMaster(
                                                                            dat_stock = datetime.now(),
                                                                            fk_branch_id = request.user.userdetails.fk_branch_id,
                                                                            fk_created = request.user,
                                                                            dbl_tax = dbl_total_tax,
                                                                            dbl_amount = ins_item['dbl_mop'],
                                                                            jsn_tax = dict_jsn_tax,
                                                                        )
                                        ins_stock_master.save()

                                        ins_stock_details = BranchStockDetails(
                                                                            fk_item_id = ins_item['pk_bint_id'],
                                                                            fk_master = ins_stock_master,
                                                                            int_qty = 1,
                                                                            int_received = 1,
                                                                            jsn_imei = {"imei":[lst_item_details['strImei']]},
                                                                            jsn_imei_avail = {"imei":[lst_item_details['strImei']]},
                                                                            jsn_imei_dmgd = {"imei":[]},
                                                                            jsn_batch_no = {"batch":[]},
                                                                            fk_transfer_details_id = None
                                                                        )
                                        ins_stock_details.save()
                                        imei_stock = {"imei":[lst_item_details['strImei']]}
                                        ins_grn_details = GrnDetails.objects.filter(fk_item_id = ins_item['pk_bint_id'],jsn_imei__contains={"imei": [lst_item_details['strImei']]}).first()
                                    else:
                                        invoiced_branch_check = BranchStockDetails.objects.filter(jsn_batch_no__contains={"batch": [lst_item_details['strImei']]},fk_master__fk_branch_id=ins_sale_detail['fk_master_id__fk_branch_id']).first()
                                        ins_item = Item.objects.filter(vchr_item_code = lst_item_details['strItemCode']).values().first()
                                        if  invoiced_branch_check:
                                            invoiced_check_stock_master = BranchStockMaster.objects.filter(pk_bint_id = invoiced_branch_check['fk_master_id']).values().first()
                                            ins_stock_master = BranchStockMaster(
                                                                                dat_stock = datetime.now(),
                                                                                fk_branch_id = request.user.userdetails.fk_branch_id,
                                                                                fk_created = request.user,
                                                                                dbl_tax = dbl_total_tax,
                                                                                dbl_amount = ins_item['dbl_mop'],
                                                                                jsn_tax = dict_jsn_tax,
                                                                            )
                                            ins_stock_master.save()
                                            ins_stock_details = BranchStockDetails(
                                                                                fk_item_id = ins_item['pk_bint_id'],
                                                                                fk_master = ins_stock_master,
                                                                                int_qty = 1,
                                                                                int_received = 1,
                                                                                jsn_imei = {"imei":[]},
                                                                                jsn_imei_avail = {"imei":[]},
                                                                                jsn_imei_dmgd = {"imei":[]},
                                                                                jsn_batch_no = {"batch":[lst_item_details['strImei']]},
                                                                                fk_transfer_details_id = None
                                                                            )
                                            ins_stock_details.save()
                                            batch_stock = {"batch":[lst_item_details['strImei']]}
                                            ins_grn_details = GrnDetails.objects.filter(fk_item_id = ins_item['pk_bint_id'],vchr_batch =lst_item_details['strImei']).first()
                                    # ins_branch_stock_imei_details = BranchStockImeiDetails.objects.filter(fk_details_id=ins_stock_details.pk_bint_id,jsn_imei_reached__contains={"imei": [lst_item_details['strImei']]}).first()
                                    # if not ins_branch_stock_imei_details:

                                    grn_details_id = ins_grn_details.pk_bint_id or None
                                    ins_imei_details = BranchStockImeiDetails(
                                                                                fk_details = ins_stock_details,
                                                                                fk_grn_details_id = grn_details_id,
                                                                                jsn_imei = imei_stock,
                                                                                int_qty = 1,
                                                                                jsn_batch_no = batch_stock,
                                                                                jsn_imei_reached = imei_stock,
                                                                                jsn_batch_reached = batch_stock,
                                                                                int_received=1
                                                                            )
                                    ins_imei_details.save()


                                else:
                                    raise ValueError('Return is not possible between Angamali and other branches')

                        
                        ins_sales_return = SalesReturn(
                                                    fk_returned_id = ins_sale_detail['fk_master_id'],
                                                    fk_sales = ins_sales_master,
                                                    fk_item_id = lst_item_details['intItemId'],
                                                    int_qty = int(lst_item_details['intQuantity']),
                                                    dbl_amount = ins_sales_details.dbl_amount,
                                                    dbl_selling_price = ins_sales_details.dbl_selling_price,
                                                    jsn_imei = ins_sales_details.json_imei,
                                                    dat_returned = date.today(),
                                                    fk_staff_id = ins_sales_master.fk_staff_id,
                                                    dat_created = datetime.now(),
                                                    fk_created = request.user.userdetails,
                                                    int_doc_status = 0,
                                                    vchr_image = str_img_path,
                                                    vchr_remark = lst_return_details[str(lst_item_details['strImei'])+'-'+str(count)]['strRemarks'] if lst_item_details['strItemCode'] not in ['GDC00001','GDC00002'] else '',
                                                    bln_damaged = lst_return_details[str(lst_item_details['strImei'])+'-'+str(count)]['blnDamage'] if lst_item_details['strItemCode'] not in ['GDC00001','GDC00002'] else False,
                                                    vchr_doc_code=str_document,
                                                    fk_sales_details_id = lst_item_details['id'],
                                                    dbl_indirect_discount = lst_item_details.get('dblIndirectDis',0),
                                                    dbl_discount = lst_item_details.get('dblDiscount',0)*-1,
                                                    dbl_buyback = lst_item_details.get('dblBuyBack',0)*-1,
                                                    vchr_old_inv_no = str_old_inv_no if str_old_inv_no else None
                                                  )
                        ins_sales_return.save()



                        dct_customer = SalesCustomerDetails.objects.filter(pk_bint_id = ins_sales_master.fk_customer_id).values('vchr_name','int_mobile').first()
                        vchr_branch_code = Branch.objects.filter(pk_bint_id = ins_sales_master.fk_branch_id).values('vchr_code').first()['vchr_code']
                        vchr_item_code = Item.objects.filter(pk_bint_id = ins_sales_details.fk_item_id).values('vchr_item_code').first()['vchr_item_code']


                        dct_enquiry_data = {}

                        dct_enquiry_data['vchr_customer_name'] = dct_customer['vchr_name']
                        dct_enquiry_data['int_customer_mobile'] = dct_customer['int_mobile']
                        dct_enquiry_data['vchr_user_code'] = request.user.username
                        dct_enquiry_data['vchr_branch_code'] = vchr_branch_code
                        dct_enquiry_data['vchr_item_code'] = vchr_item_code
                        dct_enquiry_data['dbl_amount'] = ins_sales_details.dbl_selling_price
                        dct_enquiry_data['dbl_imei_json'] = {"imei": ins_sales_details.json_imei}
                        # dct_enquiry_data['vchr_remarks'] = ins_sales_master.vchr_remarks
                        dct_enquiry_data['vchr_remarks'] = lst_return_details[str(lst_item_details['strImei'])+'-'+str(count)]['strRemarks'] if lst_item_details['strItemCode'] not in ['GDC00001','GDC00002'] else ''
                        dct_enquiry_data['dbl_discount'] = ins_sales_details.dbl_discount
                        dct_enquiry_data['dbl_buyback'] = ins_sales_details.dbl_buyback

                        dct_enquiry_data["dbl_supp_amnt"] = dct_item_sup_amnt.get(lst_item_details['intItemId']) or 0.0
                        dct_enquiry_data["dbl_mop_amnt"] = dct_item_mop_amnt.get(lst_item_details['intItemId']) or 0.0
                        dct_enquiry_data["dbl_mrp_amnt"] = dct_item_mrp_amnt.get(lst_item_details['intItemId']) or 0.0
                        dct_enquiry_data["dbl_cost_amnt"] = dct_item_cost_amnt.get(lst_item_details['intItemId']) or 0.0
                        dct_enquiry_data["dbl_myg_amnt"] = dct_item_myg_amnt.get(lst_item_details['intItemId']) or 0.0
                        dct_enquiry_data["dbl_dealer_amnt"] = dct_item_dealer_amnt.get(lst_item_details['intItemId']) or 0.0
                        dct_enquiry_data["dbl_indirect_discount"] =  ins_sales_details.dbl_indirect_discount or 0.0

                        dct_enquiry_data["dbl_tax"] = dbl_tax
                        dct_enquiry_data["json_tax"] = dct_tax
                        
                        lst_return_data.append(dct_enquiry_data)


                
                ins_sales_master.json_tax = json_total_tax
                ins_sales_master.dbl_total_tax=total_tax
                ins_sales_master.dbl_discount =total_discount
                ins_sales_master.dbl_buyback=total_buy_back
                ins_sales_master.save()


                # ============================To Bi ====================================================================================
                
                if ins_sales_master.dbl_total_amt:
                    ins_document = Document.objects.select_for_update().filter(vchr_module_name = "CREDIT NOTE",fk_branch_id = request.user.userdetails.fk_branch_id).first()
                    # if not ins_document:
                    #     ins_document = Document.objects.create(vchr_module_name = "CREDIT NOTE",vchr_short_code = request.user.userdetails.fk_branch.vchr_code,int_number = 1)
                    #     str_receipt_num = 'CN-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                    #     ins_document.int_number = ins_document.int_number+1
                    #     ins_document.save()
                    # else:
                    #     str_receipt_num = 'CN-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                    #     Document.objects.filter(vchr_module_name = "CREDIT NOTE",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).update(int_number = ins_document.int_number+1)

                    # LG 27-06-2020
                    if ins_document:
                        str_receipt_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                        Document.objects.filter(vchr_module_name = "CREDIT NOTE",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                    else:
                        ins_document_search = Document.objects.filter(vchr_module_name = 'CREDIT NOTE',fk_branch_id = None).first()
                        if ins_document_search:
                            ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                            ins_document = Document.objects.create(vchr_module_name = 'CREDIT NOTE', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                            str_receipt_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                            ins_document.int_number = ins_document.int_number+1
                            ins_document.save()
                        else:
                            return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                    # ins_receipt = Receipt.objects.create_recpt_num(str_receipt_num)
                    ins_receipt = Receipt.objects.create(vchr_receipt_num=str_receipt_num,dat_issue=datetime.now(),fk_customer_id=ins_sales_master.fk_customer.fk_customer_id,int_fop=1,dbl_amount=abs(ins_sales_master.dbl_total_amt),vchr_remarks='sales return amount',fk_created_id=request.user.id,int_doc_status=0,dat_created=datetime.now(),int_pstatus=0,int_receipt_type=1,fk_branch_id=request.user.userdetails.fk_branch_id,fk_sales_return_id=ins_sales_return.pk_bint_id)
                if create_return_posting_data(request,ins_sales_master.pk_bint_id):
                    pass
                else:
                    raise ValueError('Something happened with Transaction')
                url = settings.BI_HOSTNAME + "/mobile/add_return_item_enquiry/"
                res_data = requests.post(url,json={'dct_enquiry_data':lst_return_data})
                if res_data.json().get('status')=='success':
                    pass
                else:
                    raise ValueError('Something happened in BI')

                return Response({'status':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


class SchemeList(APIView):
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_scheme = []
            if str_search_term != -1:
                ins_scheme = FinanceScheme.objects.filter(vchr_schema__icontains=str_search_term).values('pk_bint_id','vchr_schema')
                lst_scheme = [{'name':'None','id':0}]
                if ins_scheme:
                    for itr_scheme in ins_scheme:
                        dct_scheme = {}
                        dct_scheme['name'] = itr_scheme['vchr_schema']
                        dct_scheme['id'] = itr_scheme['pk_bint_id']
                        lst_scheme.append(dct_scheme)
                return Response({'status':1,'data':lst_scheme})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})


class GdpNormal(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():

                ins_partial=PartialInvoice.objects.filter(pk_bint_id=request.data.get('partial_id')).first()
                json_data=ins_partial.json_data
                json_data['lst_items'][0]['vchr_job_status']='GDP ADVANCED RECEIVED' if json_data['lst_items'][0]['vchr_job_status']=='GDP NORMAL NEW' else 'GDEW ADVANCED RECEIVED'
                json_data['lst_items'][0]['int_adv_amount']=request.data.get('int_adv_amount')
                ins_partial.json_data=json_data

                ins_partial.save()

# ===============================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
                int_fop = request.data.get('intFop') or 1
                dbl_amount = request.data.get('amount')
                ins_user = request.user
                int_user_id = request.user.id
                int_customer_id = ins_partial.json_data['int_cust_id']

                ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'RECEIPT',fk_branch_id = request.user.userdetails.fk_branch_id).first()
                # str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                # ins_document.int_number = ins_document.int_number+1
                # ins_document.save()

                # LG 27-06-2020
                if ins_document:
                    str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                    Document.objects.filter(vchr_module_name = "RECEIPT",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                else:
                    ins_document_search = Document.objects.filter(vchr_module_name = 'RECEIPT',fk_branch_id = None).first()
                    if ins_document_search:
                        ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                        ins_document = Document.objects.create(vchr_module_name = 'RECEIPT', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                        str_inv_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                        ins_document.int_number = ins_document.int_number+1
                        ins_document.save()
                    else:
                        return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})
                ins_item = Item.objects.filter(vchr_item_code=request.data.get('int_item_code')).first()

                if ins_item:
                    # ins_receipt = Receipt.objects.create_recpt_num(str_inv_num)
                    ins_receipt = Receipt(vchr_receipt_num=str_inv_num,fk_branch_id = request.user.userdetails.fk_branch_id,dat_issue = datetime.now(),fk_item = ins_item, fk_customer_id = int_customer_id, int_fop = int_fop, dbl_amount = dbl_amount,fk_created_id = int_user_id, dat_created = datetime.now(), int_doc_status = 0, int_pstatus = 0, int_receipt_type = 4, vchr_card_num=request.data.get('vchrCardNUmber'),vchr_transaction_id=request.data.get('vchrReferenceNumber'),fk_bank_id = request.data.get('intBankId'))
                    ins_receipt.save()

                    if create_posting_data(request,ins_receipt.pk_bint_id):
                        pass
                    else:
                        raise ValueError('Something happened in POS Receipt')
                else:
                    return Response({'status':0 , 'message' : 'Item Not Found'})

# ================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
                url =settings.BI_HOSTNAME + "/service/change_status/"

                res_data = requests.post(url,json={'int_adv_amount':request.data.get('int_adv_amount'),'vchr_staff_code':request.user.username,'service_id':json_data['lst_items'][0]['int_service_id'],'status':json_data['lst_items'][0]['vchr_job_status']})
                if res_data.json().get('status')=='success':
                    pass
                else:
                    raise ValueError('Something happened in BI')

                return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})

# class ChangeStatus(APIView):
#     permission_classes=[AllowAny]
#     def post (self,request):
#         try:
#             ins_partial=PartialInvoice.objects.filter(int_enq_master_id=request.data.get('job_id')).first()
#             json_data=ins_partial.json_data
#             json_data['lst_items'][0]['vchr_job_status']=request.data.get("status")
#             if request.data.get('service_amt'):
#                 json_data['lst_items'][0]['int_service_expense']=request.data.get('service_amt')
#             ins_partial.json_data=json_data
#             ins_partial.save()
#
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
#             return Response({'result':0,'reason':e})



class DeliveryChallanPrinf(APIView):
    """
    To print Bill ,when stock tranfered to Angamaly Branch
    """
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:

            int_transfer_id  = request.data.get('id')
            if int_transfer_id:
                # if not request.data.get('bln_challan'):
                if False:

                    int_mobile_no = 8943119922 # Customer Angamli Branch
                    int_mobile_no = 9048691722 # Customer Angamli Branch
                    lst_data = IstDetails.objects.filter(fk_transfer_id= int_transfer_id).values('dbl_rate','jsn_imei','int_qty','pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','jsn_batch_no','fk_transfer__vchr_stktransfer_num','fk_transfer__fk_from__vchr_name','fk_transfer__fk_from__vchr_phone','fk_transfer__fk_to__vchr_name','fk_transfer__dat_created','fk_transfer__fk_created__first_name','fk_transfer__fk_created__last_name','fk_item__fk_item_category__json_tax_master')
                    dct_cust = CustomerDetails.objects.filter(int_mobile = int_mobile_no).values('pk_bint_id','txt_address','vchr_email','vchr_gst_no','int_mobile','vchr_name','fk_state__vchr_name','fk_state__vchr_code').first()
                    dct_tax = {str(item['pk_bint_id']):item['vchr_name'] for item in TaxMaster.objects.filter(bln_active=True).values('pk_bint_id','vchr_name')}

                    lst_item = []
                    dbl_grand_total = 0
                    dct_invoice = {}
                    dct_voucher = {}
                    bln_igst = False
                    dct_total_tax = {'CGST':{},'IGST':{},'SGST':{}}
                    if lst_data:
                        for item in lst_data:
                            dct_data = { 'buyback': 0.0,'cgst': 0,'discount': 0.0,'igst': 0,'sgst': 0
                                       }

                            dct_data['amount'] = item['dbl_rate'] or 0

                            # ===============================Tax====================================================
                            dct_item_tax = {dct_tax[tax]:item['fk_item__fk_item_category__json_tax_master'][tax] for tax in item['fk_item__fk_item_category__json_tax_master']}

                            total_tax_per =  sum(dct_item_tax.values())
                            dct_data['amount'] = round((item['dbl_rate']*100) /(100+total_tax_per),2)


                            if 'IGST' in dct_item_tax:
                                bln_igst = True
                                dct_data['igst'] = dct_item_tax['IGST']
                                if dct_item_tax['IGST'] not in dct_total_tax['IGST']:
                                    dct_total_tax['IGST'][dct_item_tax['IGST']] = round(((dct_data['amount'] * dct_item_tax['IGST'])/100) * (item['int_qty'] or 1),2)
                                else:
                                    dct_total_tax['IGST'][dct_item_tax['IGST']] += round(((dct_data['amount'] * dct_item_tax['IGST'])/100) * (item['int_qty'] or 1),2)
                            else:
                                if 'CGST' in dct_item_tax:
                                    dct_data['cgst'] = dct_item_tax['CGST']
                                    if dct_item_tax['CGST'] not in dct_total_tax['CGST']:
                                        dct_total_tax['CGST'][dct_item_tax['CGST']] = round(((dct_data['amount'] * dct_item_tax['CGST'])/100) * (item['int_qty'] or 1),2)
                                    else:
                                        dct_total_tax['CGST'][dct_item_tax['CGST']] += round(((dct_data['amount'] * dct_item_tax['CGST'])/100) * (item['int_qty'] or 1),2)
                                if 'SGST' in dct_item_tax:
                                    dct_data['sgst'] = dct_item_tax['SGST']
                                    if dct_item_tax['SGST'] not in dct_total_tax['SGST']:
                                        dct_total_tax['SGST'][dct_item_tax['SGST']] = round(((dct_data['amount'] * dct_item_tax['SGST'])/100) * (item['int_qty'] or 1),2)
                                    else:
                                        dct_total_tax['SGST'][dct_item_tax['SGST']] += round(((dct_data['amount'] * dct_item_tax['SGST'])/100) * (item['int_qty'] or 1),2)

                            # ===================================================================================


                            dct_data['item'] = item['fk_item__vchr_name']
                            dct_data['item_code'] = item['fk_item__vchr_item_code']
                            dct_data['qty'] = item['int_qty'] or 1
                            dct_data['str_imei'] = ",".join(item['jsn_imei']['imei'])
                            dct_data['total'] = (item['dbl_rate'] * dct_data['qty'])
                            dbl_grand_total += dct_data['total']
                            lst_item.append(dct_data)

                            if not dct_invoice:

                                dct_invoice = {'amount': 0,'bln_dup': False,'bln_kfc': False,'buyback': 0.0,'coupon': 0.0,'dbl_kfc': 0.0,'discount': 0.0,'indirect_discount': 0.0,'loyalty': 0.0,'terms': {},'total_tax': 0.0
                                              }
                                dct_invoice['staff'] = item['fk_transfer__fk_created__first_name']+' '+item['fk_transfer__fk_created__last_name']
                                dct_invoice['invoice_date'] = datetime.strftime(item['fk_transfer__dat_created'],'%d-%m-%Y')
                                dct_invoice['invoice_no'] = item['fk_transfer__vchr_stktransfer_num']
                                dct_invoice['invoice_time'] = datetime.strftime(item['fk_transfer__dat_created'],'%H:%M %p')
                                dct_invoice['branch_mob'] = item['fk_transfer__fk_from__vchr_phone']

                        dct_invoice['total'] = dbl_grand_total
                        dct_invoice['lst_item'] = lst_item
                        dct_invoice['tax'] = dct_total_tax
                        dct_invoice['bln_igst'] = bln_igst
                        # customer Details
                        dct_invoice['cust_add'] = dct_cust['txt_address']
                        dct_invoice['cust_email'] = dct_cust['vchr_email']
                        dct_invoice['cust_gst'] = dct_cust['vchr_gst_no']
                        dct_invoice['cust_mobile'] = dct_cust['int_mobile']
                        dct_invoice['cust_name'] = dct_cust['vchr_name']
                        dct_invoice['cust_state'] = dct_cust['fk_state__vchr_name']
                        dct_invoice['cust_state_code'] = dct_cust['fk_state__vchr_code']
                        # shiping
                        dct_invoice['sh_cust_add'] = dct_cust['txt_address']
                        dct_invoice['sh_cust_gst'] = dct_cust['vchr_gst_no']
                        dct_invoice['sh_cust_mobile'] = dct_cust['int_mobile']
                        dct_invoice['sh_cust_name'] = dct_cust['vchr_name']
                        dct_invoice['sh_landmark'] = "Not provided"
                        data = (dct_invoice,dct_voucher)

                else:
                    ins_angamali_check = StockTransfer.objects.filter(pk_bint_id = int_transfer_id).values("fk_to_id__vchr_code",'vchr_irn_no','dat_transfer','int_status').first()
                    dat_einvoice_avail = datetime.strptime('2020-10-01','%Y-%m-%d').date()
                    if ins_angamali_check["fk_to_id__vchr_code"] == 'AGY' and not ins_angamali_check['vchr_irn_no'] and ins_angamali_check["dat_transfer"].date() >= dat_einvoice_avail and ins_angamali_check['int_status'] == 1:
                    # if ins_gst_check["fk_customer__vchr_gst_no"] and  request.user.userdetails.fk_branch.vchr_code != 'AGY':
                        bln_status = True
                        bln_host_status = False
                        if request.scheme+'://'+request.get_host() == 'http://pos.mygoal.biz:4001' or request.scheme+'://'+request.get_host() == 'http://pos.mygoal.biz:5555':
                            bln_host_status = True
                        res = einvoice_generation(int_transfer_id,bln_status,bln_host_status)
                        if res["status"] == 0:
                            raise ValueError(res["reason"])
                    data = print_transfer_recipt(int_transfer_id)

                str_request_protocol = request.META.get('HTTP_REFERER').split(':')[0]

                return Response({"status":1,'file':data['file'],'file_name':data['file_name'],'file_url':str_request_protocol+'://'+request.META['HTTP_HOST']+'/media/'+data['file_name']})

        except Exception as e:
            return Response({'result':0,'reason':str(e)})

class BajajOnlineAPI(APIView):

    """docstring for ."""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            if request.data.get('partial_id'):
                ins_part=PartialInvoice.objects.filter(pk_bint_id=request.data['partial_id']).values('json_data','int_enq_master_id').first()
                lst_item_name=[]
                
                for item in ins_part['json_data']['lst_items']:
                    lst_item_name.append(item['vchr_item_code'])
                item_products={data['vchr_item_code']:(data['fk_product__vchr_name'],data['fk_brand__vchr_name'])  for data in list(Item.objects.filter(vchr_item_code__in=lst_item_name).values('vchr_item_code','fk_product__vchr_name','fk_brand__vchr_name'))}
                dct_enquiry_details={}
                dct_customer={}
                dct_customer['vchr_cust_name']= ins_part['json_data'].get('str_cust_name')
                dct_customer['vchr_cust_email']=ins_part['json_data'].get('vchr_cust_email')
                dct_customer['int_cust_mob']=ins_part['json_data'].get('int_cust_mob')
                dct_customer['staff_full_name']=ins_part['json_data'].get('str_staff_name')
                dct_customer['vchr_job_num']=ins_part['json_data'].get('vchr_job_num')
                dct_customer['vchr_bname']=ins_part['json_data'].get('str_branch')
                dct_customer['vchr_source_name']=ins_part['json_data'].get('vchr_source_name')
                dct_customer['dat_created_at']=ins_part['json_data'].get('dat_created')
                dct_customer['partial_id'] = request.data.get('partial_id')
                dct_customer['int_enq_master_id']=ins_part['int_enq_master_id']
                dct_customer['vchr_enquiry_num']=ins_part['json_data'].get('vchr_enquiry_num')

                dct_customer['dbl_down_payment']=ins_part['json_data'].get('dbl_down_payment')
                dct_customer['dbl_margin_money']=ins_part['json_data'].get('dbl_margin_money')
                dct_customer['dbl_dbd_amount']=ins_part['json_data'].get('dbl_dbd_amount')
                dct_customer['dbl_service_charge']=ins_part['json_data'].get('dbl_service_charge')
                dct_customer['dbl_net_loan_amount']=ins_part['json_data'].get('dbl_net_loan_amount')
                dct_customer['dbl_processing_fee']=ins_part['json_data'].get('dbl_processing_fee')
                dct_customer['vchr_finance_schema']=ins_part['json_data'].get('vchr_finance_schema')

                dct_customer['vchr_bank_name']=ins_part['json_data'].get('vchr_bank_name')
                dct_customer['bint_account_number']=ins_part['json_data'].get('bint_account_number')
                dct_customer['vchr_cheque_number']=ins_part['json_data'].get('vchr_cheque_number')
                dct_customer['vchr_initial_payment_type']=ins_part['json_data'].get('vchr_initial_payment_type')


                int_lst_item = len(ins_part['json_data']['lst_items'])
                temp_count = 0
                for item in ins_part['json_data']['lst_items']:
                    dct_data={}
                    dct_data['vchr_item_name'] = item['vchr_item_name']
                    dct_data['vchr_item_code'] = item['vchr_item_code']

                    dct_item = Item.objects.filter(vchr_item_code =  item['vchr_item_code']).values('pk_bint_id').first()
                    dct_data['int_item_id'] = dct_item['pk_bint_id'] if dct_item else None

                    dct_data['dbl_discount'] = item['dbl_discount']
                    dct_data['dbl_buyback'] = item['dbl_buyback']
                    dct_data['int_quantity'] = item['int_quantity']
                    dct_data['dbl_amount'] = item['dbl_amount']
                    dct_data['item_enquiry_id'] = item['item_enquiry_id']
                    dct_data['bln_IMEI_add'] = item['bln_IMEI_add']
                    dct_data['vchr_enquiry_status'] = item['vchr_enquiry_status']
                    dct_data['str_remarks'] = item['str_remarks']

                    if not item['bln_IMEI_add']:
                        dct_data['lst_imei'] = {}
                        dct_data['lst_imei'][item['item_enquiry_id']] = [{'imei':None} for i in range(dct_data['int_quantity'])]
                    else:
                        dct_data['lst_imei'] = {}
                        dct_data['lst_imei'][item['item_enquiry_id']] = [{'imei':str(imei)} for imei in item['json_imei']['imei']]
                        temp_count += 1

                    if item_products[item['vchr_item_code']][0] not in dct_enquiry_details:
                        dct_enquiry_details[item_products[item['vchr_item_code']][0]] = [dct_data]
                    else:
                        dct_enquiry_details[item_products[item['vchr_item_code']][0]].append(dct_data)

                dct_customer['bln_IMEI_add'] =  False
                if int_lst_item == temp_count:
                    dct_customer['bln_IMEI_add'] =  True
                return Response({'status':1,'dct_customer':dct_customer,'dct_enquiry_details':dct_enquiry_details})

        except Exception as e:
            return Response({'result':0,'reason':e})

    def put(self,request):
        try:
            with transaction.atomic():
                dct_data = request.data
                if dct_data:
                    ins_part = PartialInvoice.objects.filter(pk_bint_id=request.data['int_partial_id']).first()
                    dct_jsn_data = ins_part.json_data
                    ins_user = Userdetails.objects.filter(user_ptr_id = request.data['int_staff']).annotate(name=Concat('first_name',Value(' '),'last_name')).values('name','username').first()

                    dct_jsn_data['int_staff_id'] = request.data['int_staff']
                    dct_jsn_data['str_staff_name'] = ins_user['name']

                    dct_imei = request.data['dct_imei']
                    for item in dct_jsn_data['lst_items']:
                        if str(item['item_enquiry_id']) in dct_imei:
                            item['json_imei']['imei'] = dct_imei[str(item['item_enquiry_id'])]
                            item['bln_IMEI_add'] = True
                            item['vchr_enquiry_status'] = 'IMEI REQUESTED'

                    ins_part.json_data = dct_jsn_data
                    ins_part.save()
                    # ============================BI API====================================================
                    dct_data['enquiry_master'] = ins_part.int_enq_master_id
                    dct_data['str_staff_code'] = ins_user['username']
                    url = settings.BI_HOSTNAME+"/bajajonline/add_enquiry/"
                    try:
                        res_data = requests.put(url,json = dct_data)
                        if res_data.json().get('status')==1:
                            pass
                        else:
                            return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                    except Exception as e:
                        return Response({'status':'error'})

                return Response({'status':1})
        except Exception as e:
            return Response({'result':0,'reason':e})


class BajajApproveRejectAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            
            dct_data = request.data
            rst_par_inv = PartialInvoice.objects.filter(int_enq_master_id = dct_data['int_enquiry_master_id']).first()
            dct_jsn_data = rst_par_inv.json_data
            for item in dct_jsn_data['lst_items']:
                if item['item_enquiry_id'] == dct_data['int_item_enq_id']:
                    item['bln_IMEI_add'] = False
                    item['str_remarks'] = dct_data.get('str_remark')
                    item['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
            rst_par_inv.json_data = dct_jsn_data
            rst_par_inv.save()

            return Response({'status':1})

        except Exception as e:
            return Response({'result':0,'reason':e})

    def put(self,request):
        try:
            with transaction.atomic():
                dct_data = request.data
                rst_par_inv = PartialInvoice.objects.filter(int_enq_master_id = dct_data['fk_enquiry_master_id']).first()
                if rst_par_inv:
                    dct_jsn_data = rst_par_inv.json_data
                    for item in dct_jsn_data['lst_items']:
                        item['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
                        item['int_status'] = 1
                        rst_par_inv.json_data = dct_jsn_data
                    rst_par_inv.int_status = 1
                    rst_par_inv.save()
                    return Response({'status':1})
                return Response({'status':0,'reason':'data not found'})

        except Exception as e:
            return Response({'result':0,'reason':e})


class SaveReturnedSales(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                
                dct_data = request.data
                ins_customer = CustomerDetails.objects.get(pk_bint_id = dct_data["intCustId"])
                ins_sales_cust = SalesCustomerDetails.objects.filter(fk_customer_id = dct_data["intCustId"]).values("pk_bint_id").order_by("-pk_bint_id")
                int_cust_id = ins_sales_cust[0]["pk_bint_id"]
                lst_item_details = dct_data.get('lstItemDetails')
                ins_document = Document.objects.filter(vchr_module_name = 'SALES RETURN',fk_branch_id=request.user.userdetails.fk_branch_id).first()
                # if ins_document:
                #     pass
                # else:
                #     ins_document=Document(
                #                             vchr_short_code='SRT',
                #                             fk_branch_id=request.user.userdetails.fk_branch_id,
                #                             vchr_module_name='SALES RETURN',
                #                             int_number=0
                #                         )
                # str_code = ins_document.vchr_short_code
                # int_doc_num = ins_document.int_number + 1
                # ins_document.int_number = int_doc_num
                # str_number = str(int_doc_num).zfill(4)
                # str_document = str_code + '-'+  request.user.userdetails.fk_branch.vchr_code.upper()+'-'+ str_number
                # ins_document.save()

                # LG 27-06-2020
                if ins_document:
                    str_document = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                    Document.objects.filter(vchr_module_name = "SALES RETURN",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                else:
                    ins_document_search = Document.objects.filter(vchr_module_name = 'SALES RETURN',fk_branch_id = None).first()
                    if ins_document_search:
                        ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                        ins_document = Document.objects.create(vchr_module_name = 'SALES RETURN', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                        str_document = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                        ins_document.int_number = ins_document.int_number+1
                        ins_document.save()
                    else:
                        return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                if int_cust_id:
                    if lst_item_details:

                        sum_tax_CGST = 0.0
                        sum_tax_IGST = 0.0
                        sum_tax_SGST = 0.0
                        sum_tax_KFC = 0.0
                        dbl_total_amount = 0.0
                        dbl_total_rate = 0.0

                        sum_tax_CGST = round(float(request.data.get("intTotCGST") or 0.0),2)
                        sum_tax_IGST = round(float(request.data.get("intTotIGST") or 0.0),2)
                        sum_tax_SGST = round(float(request.data.get("intTotSGST") or 0.0),2)
                        sum_tax_KFC  = round(float(request.data.get("intKCESS") or 0.0),2)
                        for dct_data_item in lst_item_details:
                            dbl_total_amount = dbl_total_amount + float(dct_data_item["dblAmount"])
                            dbl_total_rate = dbl_total_rate + round(float(dct_data_item["dblRate"]) if dct_data_item["dblRate"] else 0,2)

                        jsn_tax_master = {
                                            "dblKFC" : sum_tax_KFC,
                                            "dblCGST": sum_tax_CGST,
                                            "dblIGST": sum_tax_IGST,
                                            "dblSGST": sum_tax_SGST}
                    lst_return_data = []

                    lst_item_id = [x['fk_item_id'] for x in lst_item_details]
                    dct_item_sup_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_supp_amnt'))
                    dct_item_mop_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_mop'))
                    dct_item_mrp_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_mrp'))
                    dct_item_cost_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_cost_amnt'))
                    dct_item_myg_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','int_myg_amt'))
                    dct_item_dealer_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_dealer_amt'))

                    for dct_item_details in lst_item_details:

                        # SAVES DATA IN SalesDetails
                        dbl_SGST = 0.0
                        dbl_CGST = 0.0
                        dbl_IGST = 0.0
                        dbl_KFC = 0.0
                        dbl_SGST_perc = 0.0
                        dbl_CGST_perc = 0.0
                        dbl_IGST_perc = 0.0

                        if dct_data["blnIGST"] == True:
                            dbl_IGST = dct_item_details["dblAmount"] - dct_item_details["dblRate"]
                            dbl_IGST_perc = dct_item_details["dblIGSTPer"]
                        else :
                            dbl_SGST = float(dct_item_details["dblAmount"] - dct_item_details["itemKCESS"] - (dct_item_details["dblRate"] if dct_item_details["dblRate"] else 0))/2
                            dbl_CGST = float(dct_item_details["dblAmount"] - dct_item_details["itemKCESS"] - (dct_item_details["dblRate"] if dct_item_details["dblRate"] else 0))/2
                            dbl_CGST_perc = dct_item_details["dblCGSTPer"]
                            dbl_SGST_perc = dct_item_details["dblSGSTPer"]
                            dbl_KFC = dct_item_details["itemKCESS"]
                        jsn_tax_sales = {
                                          "dblKFC" : dbl_KFC,
                                          "dblCGST": dbl_CGST,
                                          "dblIGST": dbl_IGST,
                                          "dblSGST": dbl_SGST,
                                          "dblKFC%" : dct_item_details.get("dblKFCPer",1),
                                          "dblCGST%": dct_item_details.get("dblCGSTPer",0),
                                          "dblIGST%": dct_item_details.get("dblIGSTPer",0),
                                          "dblSGST%":dct_item_details.get("dblSGSTPer",0)
                                        }
                        jsn_tax_stock = {
                                            "CGST": sum_tax_CGST,
                                            "IGST": sum_tax_IGST,
                                            "SGST": sum_tax_SGST
                                        }
                        total_tax = dbl_total_amount - dbl_total_rate

                        # ins_sales_master = SalesMaster.objects.create_inv_num(str_document)
                        ins_sales_master = SalesMaster.objects.create(
                                                        fk_customer_id = int_cust_id,
                                                        fk_branch_id = request.user.userdetails.fk_branch_id,
                                                        dat_invoice = date.today(),
                                                        vchr_invoice_num = str_document,
                                                        vchr_remarks = 'return',
                                                        dat_created = datetime.now(),
                                                        int_doc_status = 0,
                                                        dbl_total_amt = (float(dbl_total_amount)*(-1)) if dbl_total_amount else 0,
                                                        dbl_rounding_off = 0,
                                                        jsn_addition = {},
                                                        jsn_deduction = {},
                                                        dbl_total_tax = total_tax,
                                                        dbl_discount = 0,
                                                        json_tax = jsn_tax_master,
                                                        dbl_buyback =  0,
                                                        fk_staff_id = request.user.id,
                                                        fk_created = request.user.userdetails,
                                                        # dbl_supplier_amount = dct_data['intGrandTot'] - total_tax
                                                    )
                        ins_sales_master.save()

                        ins_branch_id = Branch.objects.filter(int_type__in=[2,3]).values('pk_bint_id').first()['pk_bint_id']
                        ins_grn_master = GrnMaster(
                                                    vchr_purchase_num= 'GRN/'+str_document,
                                                    dat_purchase=datetime.now(),
                                                    fk_branch_id = ins_branch_id,
                                                    dbl_total = (float(dbl_total_amount)*(-1)) if dbl_total_amount else 0,
                                                    vchr_notes = 'Old Sales return',
                                                    fk_created = request.user.userdetails,
                                                    dat_created =  datetime.now(),
                                                    int_doc_status = 4,
                                                    dat_bill = datetime.now()
                                                )
                        ins_grn_master.save()


                        ins_stock_master = BranchStockMaster(
                                                            dat_stock = datetime.now(),
                                                            fk_branch_id = request.user.userdetails.fk_branch_id,
                                                            fk_created = request.user,
                                                            dbl_tax = total_tax,
                                                            dbl_amount = float(dbl_total_amount),
                                                            jsn_tax = jsn_tax_stock,
                                                        )
                        ins_stock_master.save()

                        lst_return_data = []

                        for dct_item_details in lst_item_details:

                            # SAVES DATA IN SalesDetails
                            dbl_SGST = 0.0
                            dbl_CGST = 0.0
                            dbl_IGST = 0.0
                            dbl_KFC = 0.0
                            dbl_SGST_perc = 0.0
                            dbl_CGST_perc = 0.0
                            dbl_IGST_perc = 0.0
                            item_total_tax_percent = 0

                            if dct_data["blnIGST"] == True:
                                dbl_IGST = dct_item_details["dblAmount"] - dct_item_details["dblRate"]
                                dbl_IGST_perc = dct_item_details["dblIGSTPer"]
                                item_total_tax_percent = dct_item_details["dblIGSTPer"]
                            else :
                                dbl_SGST = float(dct_item_details["dblAmount"] - dct_item_details["itemKCESS"] - (dct_item_details["dblRate"] if dct_item_details["dblRate"] else 0))/2
                                dbl_CGST = float(dct_item_details["dblAmount"] - dct_item_details["itemKCESS"] - (dct_item_details["dblRate"] if dct_item_details["dblRate"] else 0))/2
                                dbl_CGST_perc = dct_item_details["dblCGSTPer"]
                                dbl_SGST_perc = dct_item_details["dblSGSTPer"]
                                dbl_KFC = dct_item_details["itemKCESS"]
                            jsn_tax_sales = {
                                            "dblKFC" : dbl_KFC,
                                            "dblCGST": dbl_CGST,
                                            "dblIGST": dbl_IGST,
                                            "dblSGST": dbl_SGST,
                                            "dblKFC%" : dct_item_details.get("dblKFCPer",1),
                                            "dblCGST%": dct_item_details.get("dblCGSTPer",0),
                                            "dblIGST%": dct_item_details.get("dblIGSTPer",0),
                                            "dblSGST%":dct_item_details.get("dblSGSTPer",0)
                                            }
                            jsn_tax = { "CGST": dbl_CGST or 0.0 ,
                                        "IGST": dbl_IGST or 0.0 ,
                                        "SGST": dbl_SGST or 0.0 ,
                                        "CGST%": dbl_CGST_perc  ,
                                        "IGST%": dbl_IGST_perc  ,
                                        "SGST%": dbl_SGST_perc
                                    }
                            dbl_item_tax = (jsn_tax["CGST"] + jsn_tax["IGST"] + jsn_tax["SGST"] + dct_item_details["itemKCESS"]) * -1
                            lst_imei = []
                            lst_imei.append(dct_item_details["imei"])
                            if item_total_tax_percent == 0:
                                item_total_tax_percent = jsn_tax_sales.get('dblKFC%',0) + jsn_tax_sales.get('dblCGST%',0) + jsn_tax_sales.get('dblSGST%',0)

                            imei_status = Item.objects.get(pk_bint_id = dct_item_details['fk_item_id']).imei_status

                            jsn_imei = {'imei':[]}
                            jsn_imei_avail = {'imei_avail':[]}
                            jsn_batch_no = {'batch':[]}
                            vchr_batch_no = None
                            if imei_status :
                                jsn_imei = {"imei" : lst_imei }
                            else :
                                vchr_batch_no = dct_item_details["imei"]
                                jsn_batch_no = {"batch" : lst_imei}
                            dct_item_filter_tr={}
                            dct_item_filter_tr['fk_details__fk_item_id'] = dct_item_details['fk_item_id']
                            dct_item_filter_grn={}
                            dct_item_filter_grn['fk_item_id'] =dct_item_details['fk_item_id']
                            dct_item_filter_bs={}
                            dct_item_filter_bs['fk_details__fk_item_id'] =dct_item_details['fk_item_id']
                            if check_if_imei_exist(dct_item_details["imei"],bln_transit=True,dct_filter_bs=dct_item_filter_bs,dct_filter_grn=dct_item_filter_grn,dct_filter_st=dct_item_filter_tr):
                                return Response({'status':0,'blnStock':True,'message':str(dct_item_details["imei"])+' already exists in stock'})
                            ins_sales_details = SalesDetails(
                                                            fk_master = ins_sales_master,
                                                            fk_item_id = dct_item_details['fk_item_id'],
                                                            int_qty = 1,
                                                            dbl_amount = round(float(dct_item_details['dblRate'])*(-1),2) if dct_item_details['dblRate'] else 0,
                                                            dbl_selling_price = (float(dct_item_details["dblAmount"])*(-1)) if dct_item_details["dblAmount"] else 0,
                                                            dbl_tax = dbl_item_tax,
                                                            dbl_discount = ins_sales_master.dbl_discount,
                                                            dbl_buyback = ins_sales_master.dbl_buyback,
                                                            vchr_batch = vchr_batch_no,
                                                            json_tax =  jsn_tax_sales,
                                                            json_imei = lst_imei, #jsn_imei["imei"],
                                                            int_sales_status = 0,
                                                            # int_doc_status = 1,
                                                            dbl_indirect_discount = 0,
                                                            dbl_supplier_amount = 0,
                                                            dbl_dealer_price = (dct_item_dealer_amnt.get(dct_item_details['fk_item_id']) or 0.0)*(-1),
                                                            dbl_cost_price = (dct_item_cost_amnt.get(dct_item_details['fk_item_id']) or 0.0)*(-1),
                                                            dbl_mrp = (dct_item_mrp_amnt.get(dct_item_details['fk_item_id']) or 0.0)*(-1),
                                                            dbl_mop = (dct_item_mop_amnt.get(dct_item_details['fk_item_id']) or 0.0)*(-1),
                                                            dbl_tax_percentage = item_total_tax_percent
                                                            )


                            ins_sales_details.save()
                            
                            # SAVES DATA IN SALES RETURN
                            inst_sales_return = SalesReturn(
                                                                fk_sales = ins_sales_master,
                                                                fk_item_id = dct_item_details['fk_item_id'],
                                                                int_qty = 1,
                                                                dbl_amount = round(float(dct_item_details['dblRate'])*(-1),2) if dct_item_details['dblRate'] else 0,
                                                                dbl_selling_price =(float( dct_item_details["dblAmount"])*(-1)) if  dct_item_details["dblAmount"] else 0,
                                                                jsn_imei = lst_imei, #jsn_imei["imei"],
                                                                dat_returned = date.today(),
                                                                fk_staff_id = ins_sales_master.fk_staff_id,
                                                                dat_created = datetime.now(),
                                                                fk_created = request.user.userdetails,
                                                                int_doc_status = 0,
                                                                dbl_discount = 0,
                                                                dbl_buyback = 0,
                                                                dbl_indirect_discount = 0,
                                                                # vchr_image = str_img_path,
                                                                # vchr_remark = dct_item_details['strRemarks'],
                                                                # bln_damaged = lst_return_details['blnDamage'],
                                                                vchr_doc_code=str_document,
                                                                vchr_old_inv_no = request.data.get("strOldInvoiceNum") if request.data.get("strOldInvoiceNum") else None,
                                                                vchr_remark = request.data.get("strRemarks")
                                                            )
                            inst_sales_return.save()
                            # SAVES DATA IN GrnDetails
                            ins_grn_details = GrnDetails(
                                                        fk_item_id = dct_item_details['fk_item_id'],
                                                        fk_purchase = ins_grn_master,
                                                        int_qty = 1,
                                                        int_avail=0,
                                                        jsn_imei_avail=jsn_imei_avail,
                                                        dbl_costprice = round(float(dct_item_details['dblRate']) if dct_item_details['dblRate'] else 0,2),
                                                        jsn_tax = jsn_tax,
                                                        dbl_tax = dbl_item_tax,
                                                        dbl_ppu = dct_item_details["dblAmount"],
                                                        dbl_total_amount = dct_item_details["dblAmount"],
                                                        vchr_batch_no = vchr_batch_no,
                                                        jsn_imei = jsn_imei
                                                        )
                            ins_grn_details.save()
                            # aSAVES DATA IN BranchStockDetails
                            ins_stock_details = BranchStockDetails(
                                                                    fk_item_id =  dct_item_details['fk_item_id'],
                                                                    fk_master = ins_stock_master,
                                                                    int_qty = 1,
                                                                    jsn_imei = jsn_imei,
                                                                    jsn_imei_avail = jsn_imei,
                                                                    jsn_batch_no = jsn_batch_no,
                                                                    int_received=1
                                                                )
                            ins_stock_details.save()
                            # SAVES DATA IN BranchStockImeiDetails
                            ins_imei_details = BranchStockImeiDetails(
                                                                        fk_details = ins_stock_details,
                                                                        fk_grn_details = ins_grn_details,
                                                                        jsn_imei = jsn_imei,
                                                                        int_qty = 1,
                                                                        jsn_batch_no = jsn_batch_no,
                                                                        jsn_imei_reached = jsn_imei,
                                                                        jsn_batch_reached = jsn_batch_no,
                                                                        int_received=1
                                                                    )
                            ins_imei_details.save()


                            vchr_branch_code = Branch.objects.filter(pk_bint_id = ins_sales_master.fk_branch_id).values('vchr_code').first()['vchr_code']
                            vchr_item_code = Item.objects.filter(pk_bint_id = ins_sales_details.fk_item_id).values('vchr_item_code').first()['vchr_item_code']


                            dct_enquiry_data = {}
                            dct_enquiry_data['vchr_customer_name'] = ins_customer.vchr_name
                            dct_enquiry_data['int_customer_mobile'] = ins_customer.int_mobile
                            dct_enquiry_data['int_cust_type'] = ins_customer.int_cust_type
                            dct_enquiry_data['vchr_user_code'] = request.user.username
                            dct_enquiry_data['vchr_branch_code'] = vchr_branch_code
                            dct_enquiry_data['vchr_item_code'] = vchr_item_code
                            dct_enquiry_data['dbl_amount'] = ins_sales_details.dbl_selling_price
                            dct_enquiry_data['dbl_imei_json'] = {"imei": ins_sales_details.json_imei}
                            dct_enquiry_data['vchr_remarks'] = ''
                            dct_enquiry_data['dbl_discount'] = ins_sales_details.dbl_discount
                            dct_enquiry_data['dbl_buyback'] = ins_sales_details.dbl_buyback
                            dct_enquiry_data["dbl_indirect_discount"] =  ins_sales_details.dbl_indirect_discount or 0.0
                            dct_enquiry_data["dbl_supp_amnt"] = dct_item_sup_amnt.get(dct_item_details['fk_item_id']) or 0.0
                            dct_enquiry_data["dbl_mop_amnt"] = dct_item_mop_amnt.get(dct_item_details['fk_item_id']) or 0.0
                            dct_enquiry_data["dbl_mrp_amnt"] = dct_item_mrp_amnt.get(dct_item_details['fk_item_id']) or 0.0
                            dct_enquiry_data["dbl_cost_amnt"] = dct_item_cost_amnt.get(dct_item_details['fk_item_id']) or 0.0
                            dct_enquiry_data["dbl_myg_amnt"] = dct_item_myg_amnt.get(dct_item_details['fk_item_id']) or 0.0
                            dct_enquiry_data["dbl_dealer_amnt"] = dct_item_dealer_amnt.get(dct_item_details['fk_item_id']) or 0.0

                            dct_enquiry_data["dbl_tax"] = dbl_item_tax

                            lst_return_data.append(dct_enquiry_data)


                        # url = settings.BI_HOSTNAME + "/mobile/add_return_item_enquiry/"
                        # res_data = requests.post(url,json={'dct_enquiry_data':lst_return_data})
                        # if res_data.json().get('status')=='success':
                        #     pass
                        # else:
                        #     raise ValueError('Something happened in BI')

                        
                        if ins_sales_master.dbl_total_amt:
                            ins_document = Document.objects.filter(vchr_module_name = "CREDIT NOTE",fk_branch_id = request.user.userdetails.fk_branch_id).first()
                            # if not ins_document:
                            #     ins_document = Document.objects.create(vchr_module_name = "CREDIT NOTE",vchr_short_code = request.user.userdetails.fk_branch.vchr_code,int_number = 1)
                            #     str_receipt_num = 'CN-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                            #     ins_document.int_number = ins_document.int_number+1
                            #     ins_document.save()
                            # else:
                            #     str_receipt_num = 'CN-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                            #     Document.objects.filter(vchr_module_name = "CREDIT NOTE",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).update(int_number = ins_document.int_number+1)

                            # LG 27-06-2020
                            if ins_document:
                                str_receipt_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                                Document.objects.filter(vchr_module_name = "CREDIT NOTE",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                            else:
                                ins_document_search = Document.objects.filter(vchr_module_name = 'CREDIT NOTE',fk_branch_id = None).first()
                                if ins_document_search:
                                    ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                                    ins_document = Document.objects.create(vchr_module_name = 'CREDIT NOTE', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                                    str_receipt_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                                    ins_document.int_number = ins_document.int_number+1
                                    ins_document.save()
                                else:
                                    return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                            # ins_receipt = Receipt.objects.create_recpt_num(str_receipt_num)
                            ins_receipt = Receipt.objects.create(vchr_receipt_num=str_receipt_num,dat_issue=datetime.now(),fk_customer_id=ins_sales_master.fk_customer.fk_customer_id,int_fop=1,dbl_amount=abs(ins_sales_master.dbl_total_amt),vchr_remarks='sales return amount',fk_created_id=request.user.id,int_doc_status=0,dat_created=datetime.now(),int_pstatus=0,int_receipt_type=1,fk_branch_id=request.user.userdetails.fk_branch_id,fk_sales_return_id = inst_sales_return.pk_bint_id)
                        if create_return_posting_data(request,ins_sales_master.pk_bint_id):
                            pass
                        else:
                            raise ValueError('Something happened with Transaction')

                        url = settings.BI_HOSTNAME + "/mobile/add_return_item_enquiry/"
                        res_data = requests.post(url,json={'dct_enquiry_data':lst_return_data})
                        if res_data.json().get('status')=='success':
                            pass
                        else:
                            raise ValueError('Something happened in BI')
                        return Response({ "status" : 1 , "data": "Saved Successfully"})

                    else:
                        return_data = "no details about item"
                else :
                    return_data = "no customer exists"
                return Response({ "status": 0 , "data":return_data })

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})

class BajajDeliveryImageAPI(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            with transaction.atomic():
                dict_bajaImages=request.data
                int_enqui_mas_id=dict_bajaImages.pop('enq_master_id')
                rst_par_inv = PartialInvoice.objects.filter(int_enq_master_id = int_enqui_mas_id,int_status=1).first()
                if rst_par_inv:
                    jsn_old_data = rst_par_inv.json_data
                    jsn_old_data['bajaj_images'] = dict_bajaImages
                    rst_par_inv.json_data = jsn_old_data
                    rst_par_inv.save()
                    return Response({ "status": 1 , "message":"Saved Successfully" })

                else:
                    return Response({ "status": 0 , "message":"data not found" })

        except Exception as e:
            return Response({'result':0,'reason':e})





        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return Response({'status':'0','message':str(e)})


class CreditSaleAPI(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                
                if request.data.get('approveId'):
                    ins_partial_inv=PartialInvoice.objects.filter(pk_bint_id = request.data.get('approveId'),int_active = 0).first()
                    json_updated_data=ins_partial_inv.json_updated_data
                    dbl_total_amt=int(json_updated_data.get('dbl_total_amt'))

                    if dbl_total_amt>200000:
                        json_updated_data['int_credit_sale']=2

                    PartialInvoice.objects.filter(pk_bint_id = request.data.get('approveId'),int_active = 0).update(int_approve=4,dat_created=datetime.now(),json_updated_data=json_updated_data)
                    return Response({'status':1,'bln_approve':True})
                elif request.data.get('rejectId'):
                    PartialInvoice.objects.filter(pk_bint_id = request.data.get('rejectId'),int_active = 0).update(int_approve=0,dat_created=datetime.now())
                    return Response({'status':1,'bln_approve':True})

                int_partial_id = request.data.get('partial_id')
                if int_partial_id:

                    ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = int_partial_id,int_active = 0).values('dat_created','json_data','int_status','int_approve').first()
                    lst_items = json.loads(request.data.get('lstItems'))
                    if ins_partial_inv['json_data']:
                        json_partial_data=copy.deepcopy(ins_partial_inv['json_data'])
                        json_partial_data['dbl_total_amt']=request.data.get('dblTotalAmount')
                        json_partial_data['dbl_partial_amt']=request.data.get('dblPartialAmount',0)
                        json_partial_data['dbl_balance_amt']=request.data.get('dblBalanceAmount',0)
                        json_partial_data['lst_items']=[]
                        dct_item={}
                        int_index=1
                        

                        for ins_item in lst_items:

                            # if ins_item.get('itemEnqId') and ins_item['strItemCode']+"-"+str(ins_item['itemEnqId']) in  dct_item:
                            #     
                            #     # dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['int_quantity']=dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['int_quantity']+1
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['json_imei']['imei'].append(ins_item.get('strImei'))
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_amount'] += ins_item['dblAmount']


                            # elif ins_item.get('itemEnqId'):
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]={}
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['int_quantity'] = ins_item['intQuantity']
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['json_imei'] = {'imei': [ins_item.get('strImei')]}
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['vchr_item_code'] = ins_item['strItemCode']
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['vchr_item_name'] = ins_item['strItemName']
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['int_status'] = ins_item['intStatus']
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['vchr_remarks'] = request.data.get('strRemarks')
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['item_enquiry_id'] = ins_item['itemEnqId']
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_buyback'] = ins_item['dblBuyBack']
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_amount'] = ins_item['dblAmount']
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_margin_amount'] = ins_item.get('dblMarginAmount',0)
                            #     dct_item[ins_item['strItemCode'] +"-"+str(ins_item['itemEnqId'])]['dbl_discount'] = ins_item['dblDiscount']
                            # else:
                            str_key = ins_item['strItemCode'] +"-"+str(int_index)
                            int_index +=1
                            dct_item[str_key]={}
                            dct_item[str_key]['int_quantity'] = 1
                            dct_item[str_key]['json_imei'] = {'imei': [ins_item.get('strImei')]}
                            dct_item[str_key]['vchr_item_code'] = ins_item['strItemCode']
                            dct_item[str_key]['vchr_item_name'] = ins_item['strItemName']
                            dct_item[str_key]['int_status'] = ins_item['intStatus']
                            dct_item[str_key]['vchr_remarks'] = request.data.get('strRemarks')
                            dct_item[str_key]['item_enquiry_id'] = ins_item.get('itemEnqId',None)
                            dct_item[str_key]['dbl_buyback'] = ins_item['dblBuyBack']
                            dct_item[str_key]['dbl_amount'] = (ins_item.get('dblAmount') or 0)+(ins_item.get('dblDiscount') or 0)+(ins_item.get('dblBuyBack') or 0)-(ins_item.get('dblMarginAmount') or 0)
                            dct_item[str_key]['dbl_margin_amount'] = ins_item.get('dblMarginAmount',0)
                            dct_item[str_key]['dbl_discount'] = ins_item['dblDiscount']



                        json_partial_data['lst_items'] = list(dct_item.values())

                        if request.data.get('bln_service') == 'true':
                            json_partial_data['lst_items'][-1]['dbl_advc_paid'] = int(request.data.get('dbl_advc_paid',0))

                    PartialInvoice.objects.filter(pk_bint_id = int_partial_id,int_active = 0).update(int_approve=3,json_updated_data=json_partial_data,dat_created=datetime.now())
                    return Response({'status':1,'int_approve':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

    def put(self,request):
        try:
            dat_to = (datetime.strptime(request.data.get("datTo")[:10],'%Y-%m-%d')).date()
            dat_from = (datetime.strptime(request.data.get("datFrom")[:10],'%Y-%m-%d')).date()

            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                ins_partial_inv = PartialInvoice.objects.filter(int_active = 0,int_approve=3,dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).exclude(int_status__in=(6,5,10,11)).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
            else:
                ins_partial_inv = PartialInvoice.objects.filter(int_active = 0,int_approve=3,json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id},dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).exclude(int_status__in=(6,5,10,11)).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')

            #--------------------
            lst_branch_id = []

            #--------------------
            lst_data = []
            dct_branch = dict(Branch.objects.values_list('pk_bint_id','vchr_name'))
            for ins_data in ins_partial_inv:
                dct_data = {}
                dct_data['intId'] = ins_data['pk_bint_id']
                dct_data['datBooked'] = ins_data['dat_created'].strftime("%d-%m-%Y")
                dct_data['strCustomer'] = ins_data['json_data']['str_cust_name'].title()
                dct_data['strStaff'] = ins_data['json_data'].get('str_staff_name').title()
                dct_data['strEnqNo'] = ins_data['json_data'].get('vchr_enquiry_num') if ins_data['json_data'].get('vchr_enquiry_num') else ins_data['json_data'].get('vchr_job_num')
                dct_data['branch'] = dct_branch.get(ins_data['json_data'].get('int_branch_id'))
                if request.user.userdetails.fk_group.vchr_name.upper() in ['SERVICE MANAGER','SERVICE ENGINEER','BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                    if ins_data['json_data'].get('int_branch_id') in lst_branch_id and ins_data['json_data']['lst_items'][0].get('vchr_job_status') not in ['GDP NORMAL NEW','GDEW NEW','CHECKED']:
                        dct_data['bln_view'] = True
                    elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER']:
                        dct_data['bln_view'] = True
                    else:
                        dct_data['bln_view'] = False
                else:
                        dct_data['bln_view'] = False


                dct_data['sales_status'] = ins_data['int_status']
                dct_data['strItem'] = ''
                dct_data['strItem'] = ' , '.join([ i['vchr_item_name']for i in ins_data['json_data']['lst_items']])
                if request.data.get('blnService'):
                    dct_data['int_service_id']= ins_data['json_data']['lst_items'][0]['int_service_id'] if ins_data['json_data']['lst_items'][0].get('int_service_id') else ''
                    dct_data['vchr_status']= ins_data['json_data']['lst_items'][0]['vchr_job_status'] if ins_data['json_data']['lst_items'][0].get('vchr_job_status') else ''
                    dct_data['vchr_job_num']=ins_data['json_data'].get('vchr_job_num') or "---"

                    dct_data['vchr_status'] == 'CREDIT SALE REQUESTED'

                if len(dct_data['strItem'])>30:
                    dct_data['strItem'] = dct_data['strItem'][:30]+'...'

                lst_data.append(dct_data)
            return Response({'status':1,'data':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


def einvoice_generation(int_id,bln_status,bln_host_status):
    try:
        str_Version =  "1.03"
        str_temp = ''
        if bln_status:
            """E-Invoice Generation for Angamali Stock transfer"""

            ins_stock_transfer = StockTransfer.objects.filter(pk_bint_id=int_id).values('fk_to__vchr_email','fk_to__vchr_phone','fk_from__vchr_gstno','fk_to__vchr_gstno','dat_transfer','vchr_stktransfer_num','fk_from__vchr_email','fk_from__vchr_name','fk_from__vchr_phone','fk_to__int_pincode','fk_from__int_pincode','fk_to__flt_latitude','fk_from__vchr_code','fk_to__vchr_code','fk_to__flt_longitude','fk_from__flt_latitude','fk_from__flt_longitude', 'fk_to__fk_location_master__int_code','fk_to__fk_location_master__vchr_location','fk_to__vchr_address','fk_to__vchr_name','fk_from__vchr_gstno','fk_from__vchr_address','fk_from__fk_location_master__vchr_location','fk_from__fk_location_master__int_code','fk_to__vchr_gstno',
'vchr_stktransfer_num','vchr_vehicle_num').first()
            ins_ist_details = IstDetails.objects.filter(fk_transfer_id=int_id).values('dbl_rate','fk_item_id','int_qty','fk_item__fk_product__vchr_name','fk_item__fk_item_category__vchr_hsn_code','fk_item__vchr_name','fk_item__fk_item_category__json_tax_master')
            lst_address_seller=ins_stock_transfer['fk_from__vchr_address'].split(',')
            int_half=len(lst_address_seller)/2
            strSelleraddress1=''
            strSelleraddress2=''
            for i in range(round(int_half)):
                 strSelleraddress1+=lst_address_seller[i]
            for i in range(round(int_half),len(lst_address_seller)):
                 strSelleraddress2+=lst_address_seller[i]

            str_seller_legal_name='3G Mobile World'
            str_seller_trade_name= ins_stock_transfer.get('fk_from__vchr_name')
            str_seller_pincode= ins_stock_transfer.get('fk_from__int_pincode')
            str_seller_phone= ins_stock_transfer.get('fk_from__vchr_phone')
            str_seller_email = ins_stock_transfer.get('fk_from__vchr_email')
            str_seller_gstin = '32AAAFZ4615J1Z8'

            """SELLER DETAILS"""
            dct_seller_details =  {
                    "Gstin":'32AAAFZ4615J1Z8' or str_seller_gstin,
                    "LglNm": str_seller_legal_name,
                    "TrdNm":str_seller_trade_name,
                    "Addr1":strSelleraddress1,
                    "Addr2": strSelleraddress2,
                    "Loc": str_seller_trade_name,
                    "Pin": str_seller_pincode,
                    "Ph":str_seller_phone,
                    "Em": str_seller_email,
                    "Stcd":'32'
                  }
            dct_doc_dtls = {
                "Typ": "INV",
                "No": ins_stock_transfer['vchr_stktransfer_num'],
                "Dt": datetime.strftime(ins_stock_transfer['dat_transfer'],'%d/%m/%Y')
              }

            dct_tran_dtls =  {
                "TaxSch": "GST",
                "SupTyp": "B2B",
                "RegRev": "N",
                "IgstOnIntra": "N"
              }


            lst_address_buyer=ins_stock_transfer['fk_to__vchr_address'].split(',')
            int_half=len(lst_address_buyer)/2
            strbuyeraddress1=''
            strbuyeraddress2=''
            for i in range(round(int_half)):
                 strbuyeraddress1+=lst_address_buyer[i]
            for i in range(round(int_half),len(lst_address_buyer)):
                 strbuyeraddress2+=lst_address_buyer[i]

            """BUYER DETAILS"""
            dct_buyer_details={"Gstin":ins_stock_transfer['fk_to__vchr_gstno'],
            "Pos":'32',
            "LglNm": ins_stock_transfer['fk_to__vchr_name'],
            "TrdNm": ins_stock_transfer['fk_to__vchr_name'],
            "Addr1": strbuyeraddress1,
            "Addr2": strbuyeraddress2,
            "Loc": ins_stock_transfer['fk_to__vchr_name'],
            # "Pin": 175101 or int(ins_sales_master.get('fk_customer__fk_location__vchr_pin_code')),
            "Pin": ins_stock_transfer['fk_to__int_pincode'],
            "Stcd":'32',
            "Ph":str(ins_stock_transfer['fk_to__vchr_phone']),
            "Em": ins_stock_transfer['fk_to__vchr_email'],
            }

            lst_item=[]
            int_sl_no=0
            int_tot_amt=0
            int_ass_amt_sum=0
            int_tot_amt_sum=0
            int_discount_sum=0
            int_cgst_sum=0
            int_sgst_sum=0
            int_igst_sum=0
            inst_tax = TaxMaster.objects.values()

            for data in ins_ist_details:
                data=dict(data)
                vchr_hsn = data['fk_item__fk_item_category__vchr_hsn_code'].split('.')[0]
                vchr_product_desc =data['fk_item__vchr_name']
                int_qty= data['int_qty']
                int_sl_no+=1

                int_igst=0.0
                int_igstp=0.0

                int_cgst=0
                int_cgstp=0
                int_cgst_key = inst_tax.filter(vchr_name='CGST').values('pk_bint_id').first().get('pk_bint_id')
                # int_igst = inst_tax.filter(vchr_name='IGST').values('pk_bint_id').first().get('pk_bint_id')
                int_sgst_key = inst_tax.filter(vchr_name='SGST').values('pk_bint_id').first().get('pk_bint_id')
                # int_kfc = inst_tax.filter(vchr_name='KFC').values('pk_bint_id').first().get('pk_bint_id')
                int_sgstp = data['fk_item__fk_item_category__json_tax_master'][str(int_sgst_key)]
                int_cgstp = data['fk_item__fk_item_category__json_tax_master'][str(int_cgst_key)]
                int_gst_rate=int_cgstp+int_sgstp
                dbl_taxable_amount =round((data['dbl_rate']*data['int_qty'])/((100+int_gst_rate)/100),2)
                int_cgst = (dbl_taxable_amount*int_cgstp)/100
                int_sgst = (dbl_taxable_amount*int_sgstp)/100
                dct_data= {
                      "SlNo": str(int_sl_no),
                      "PrdDesc": vchr_product_desc,
                      "IsServc": "N",
                      "HsnCd": vchr_hsn,
                      "Qty":float(int_qty),
                      "Unit": "PCS",
                      "UnitPrice":round(float(dbl_taxable_amount/data['int_qty']),2),
                      "TotAmt": round(float(dbl_taxable_amount),2),
                      "Discount":0.0,
                    #   "PreTaxVal": 1,
                      "AssAmt": float(round(dbl_taxable_amount,2)),
                      "GstRt": int_gst_rate,
                      "IgstAmt": float(round(int_igst,2)),
                      "CgstAmt": float(round(int_cgst,2)),
                      "SgstAmt": float(round(int_sgst,2)),
                      "CesRt": 0.0,
                      "CesAmt": 0.0,
                      "CesNonAdvlAmt": 0,
                      "StateCesRt": 0,
                      "StateCesAmt": 0.0,
                      "StateCesNonAdvlAmt": 0,
                      "OthChrg": 0,
                      "TotItemVal": round(float(int_igst+int_cgst+int_sgst+dbl_taxable_amount),0),
                      "OrgCntry": "IN",

                    }
                int_ass_amt_sum+=dct_data['AssAmt']
                int_tot_amt_sum+=(dct_data['TotItemVal'])
                int_discount_sum+=dct_data['Discount']
                int_cgst_sum+=dct_data['CgstAmt']
                int_sgst_sum+=dct_data['SgstAmt']
                int_igst_sum+=dct_data['IgstAmt']

                lst_item.append(dct_data)

            dct_val_dtls=  {
            "AssVal": round(int_ass_amt_sum,2),
            "CgstVal": round(int_cgst_sum,2),
            "SgstVal": round(int_sgst_sum,2),
            "IgstVal": round(int_igst_sum,2),
            "CesVal": 0.0,
            "StCesVal": 0.0,
            "Discount":0,
            "OthChrg": 0,
            "RndOffAmt": 0.0,
            "TotInvVal": round(int_tot_amt_sum),
            "TotInvValFc": round(int_tot_amt_sum,2)
                  }


            dct_invoice_data={
            "Version":str_Version,
            "TranDtls":dct_tran_dtls,
            "DocDtls":dct_doc_dtls,
            "SellerDtls":dct_seller_details,
            "BuyerDtls":dct_buyer_details,
            "ItemList":lst_item,
            "ValDtls":dct_val_dtls
            }



        else:
            """E-Invoice Generation for Other branches"""

            ins_sales_master=SalesMaster.objects.filter(pk_bint_id = int_id).values('fk_branch__fk_location_master__vchr_location','fk_customer__vchr_gst_no','fk_branch__vchr_address','fk_branch__int_pincode','fk_branch__int_pincode','fk_branch__vchr_name','fk_branch__vchr_email',
                              'fk_customer__vchr_gst_no','fk_customer__vchr_name','fk_customer__txt_address','fk_customer__fk_location__vchr_pin_code','fk_customer__fk_location__vchr_name','vchr_invoice_num','dat_invoice','fk_branch__vchr_phone','fk_customer__int_mobile','fk_customer__vchr_email','txt_qr_code','vchr_irn_no').first()
            lst_details= SalesDetails.objects.filter(fk_master_id=int_id).values('dbl_amount','dbl_selling_price','json_tax','dbl_discount','dbl_buyback','fk_item__vchr_name','fk_item__fk_item_category__vchr_hsn_code','int_qty','int_sales_status')
            lst_address_seller=ins_sales_master['fk_branch__vchr_address'].split(',')

            """ SELLER DETAILS """
            int_half=len(lst_address_seller)/2
            strSelleraddress1=''
            strSelleraddress2=''

            for i in range(round(int_half)):
                 strSelleraddress1+=lst_address_seller[i]
            for i in range(round(int_half),len(lst_address_seller)):
                 strSelleraddress2+=lst_address_seller[i]

            str_seller_legal_name='3G Mobile World'
            str_seller_trade_name=ins_sales_master.get('fk_branch__vchr_name')
            str_seller_pincode=ins_sales_master.get('fk_branch__int_pincode')
            str_seller_phone=ins_sales_master.get('fk_branch__vchr_phone')
            str_seller_email = ins_sales_master.get('fk_branch__vchr_email')
            str_seller_gstin = '32AAAFZ4615J1Z8'

            """SELLER DETAILS"""
            dct_seller_details =  {
                    "Gstin":'32AAAFZ4615J1Z8' or str_seller_gstin,
                    "LglNm": str_seller_legal_name,
                    "TrdNm":str_seller_trade_name,
                    "Addr1":strSelleraddress1,
                    "Addr2": strSelleraddress2,
                    "Loc": str_seller_trade_name,
                    "Pin": str_seller_pincode,
                    "Ph":str_seller_phone,
                    "Em": str_seller_email,
                    "Stcd":'32'
                  }

            dct_doc_dtls = {
                "Typ": "INV",
                "No": ins_sales_master.get('vchr_invoice_num'),
                "Dt": datetime.strftime(ins_sales_master.get('dat_invoice'),'%d/%m/%Y')
              }

            dct_tran_dtls =  {
                "TaxSch": "GST",
                "SupTyp": "B2B",
                "RegRev": "N",
                "IgstOnIntra": "N"
              }

            lst_address_buyer=ins_sales_master['fk_customer__txt_address'].split(',')
            int_half=len(lst_address_buyer)/2
            strbuyeraddress1=''
            strbuyeraddress2=''
            for i in range(round(int_half)):
                 strbuyeraddress1+=lst_address_buyer[i]
            for i in range(round(int_half),len(lst_address_buyer)):
                 strbuyeraddress2+=lst_address_buyer[i]

            """ BUYER DETAILS """
            dct_buyer_details={"Gstin":ins_sales_master.get('fk_customer__vchr_gst_no'),
            "Pos":ins_sales_master.get('fk_customer__vchr_gst_no')[0:2],
            "LglNm": ins_sales_master.get('fk_customer__vchr_name'),
            "TrdNm": ins_sales_master.get('fk_customer__vchr_name'),
            "Addr1": strbuyeraddress1,
            "Addr2": strbuyeraddress2,
            "Loc": ins_sales_master.get('fk_customer__fk_location__vchr_name'),
            # "Pin": 175101 or int(ins_sales_master.get('fk_customer__fk_location__vchr_pin_code')),
            "Pin": int(ins_sales_master.get('fk_customer__fk_location__vchr_pin_code')),
            "Stcd":ins_sales_master.get('fk_customer__vchr_gst_no')[0:2],
            "Ph":str(ins_sales_master.get('fk_customer__int_mobile')),
            "Em": ins_sales_master.get('fk_customer__vchr_email'),
            }

            lst_item=[]
            int_sl_no=0
            int_tot_amt=0
            int_ass_amt_sum=0
            int_tot_amt_sum=0
            int_discount_sum=0
            int_cgst_sum=0
            int_sgst_sum=0
            int_igst_sum=0

            """ITEM DETAILS"""
            for data in lst_details:
                data=dict(data)
                if data['int_sales_status']!=2:
                    vchr_hsn = data['fk_item__fk_item_category__vchr_hsn_code'].split('.')[0]
                    vchr_product_desc =data['fk_item__vchr_name']
                    int_qty= data['int_qty']
                    int_sl_no+=1

                    int_igst=0
                    int_igstp=0
                    if data['json_tax']['dblIGST']:
                        int_igst=data['json_tax']['dblIGST']
                        int_igstp=data['json_tax']['dblIGST%']

                    int_cgst=0
                    int_cgstp=0
                    if data['json_tax']['dblCGST']:
                        int_cgst=data['json_tax']['dblCGST']
                        int_cgstp=data['json_tax']['dblCGST%']

                    int_sgst=0
                    int_sgstp=0
                    if data['json_tax']['dblSGST']:
                        int_sgst=data['json_tax']['dblSGST']
                        int_sgstp=data['json_tax']['dblSGST%']
                    #
                    # data['json_tax']['dblSGST']
                    #
                    # data['json_tax']['dblCGST%']
                    #
                    # data['json_tax']['dblSGST%']

                    int_gst_rate=int_cgstp+int_sgstp+int_igstp
                    amount_without_dis = data['dbl_amount']+ data['dbl_discount']+data['dbl_buyback']
                    dct_data= {
                        "SlNo": str(int_sl_no),
                        "PrdDesc": vchr_product_desc,
                        "IsServc": "N",
                        "HsnCd": vchr_hsn,
                        "Qty":float(int_qty),
                        "Unit": "PCS",
                        "UnitPrice":round(float(data['dbl_amount'] + data['dbl_discount']+data['dbl_buyback']),2),
                        "TotAmt": round(float(data['dbl_amount'] + data['dbl_discount']+data['dbl_buyback']),2),
                        "Discount":round(float( data['dbl_discount']+data['dbl_buyback']),2),
                        #   "PreTaxVal": 1,
                        "AssAmt": float(round(data['dbl_amount']*data['int_qty'],2)),
                        "GstRt": int_gst_rate,
                        "IgstAmt": float(round(int_igst,2)),
                        "CgstAmt": float(round(int_cgst,2)),
                        "SgstAmt": float(round(int_sgst,2)),
                        "CesRt": 0.0,
                        "CesAmt": 0.0,
                        "CesNonAdvlAmt": 0,
                        "StateCesRt": 0,
                        "StateCesAmt": 0.0,
                        "StateCesNonAdvlAmt": 0,
                        "OthChrg": 0,
                        "TotItemVal": round(float((int_igst+int_cgst+int_sgst+data['dbl_amount'])*data['int_qty']),0),
                        "OrgCntry": "IN",

                        }
                    int_ass_amt_sum+=dct_data['AssAmt']
                    int_tot_amt_sum+=(dct_data['TotItemVal'])
                    int_discount_sum+=dct_data['Discount']
                    int_cgst_sum+=dct_data['CgstAmt']
                    int_sgst_sum+=dct_data['SgstAmt']
                    int_igst_sum+=dct_data['IgstAmt']

                    lst_item.append(dct_data)

            dct_val_dtls=  {
            "AssVal": round(int_ass_amt_sum,2),
            "CgstVal": round(int_cgst_sum,2),
            "SgstVal": round(int_sgst_sum,2),
            "IgstVal": round(int_igst_sum,2),
            "CesVal": 0.0,
            "StCesVal": 0.0,
            "Discount":0,
            "OthChrg": 0,
            "RndOffAmt": 0.0,
            "TotInvVal": round(int_tot_amt_sum),
            "TotInvValFc": round(int_tot_amt_sum,2)
                  }


            dct_invoice_data={
            "Version":str_Version,
            "TranDtls":dct_tran_dtls,
            "DocDtls":dct_doc_dtls,
            "SellerDtls":dct_seller_details,
            "BuyerDtls":dct_buyer_details,
            "ItemList":lst_item,
            "ValDtls":dct_val_dtls
            }
        
        json_invoice_data=json.dumps(dct_invoice_data)
        int_request_id=datetime.strftime(datetime.now(),'%d%m%Y%H%M%S%f')+str(int_id)
        headers= { "Content-Type": "application/json", "user_name":'adqgsphpusr1', "password":"Gsp@1234", "gstin": '02AMBPG7773M002', "Authorization":'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJnc3AiXSwiZXhwIjoxNjAzNDU1MzEyLCJhdXRob3JpdGllcyI6WyJST0xFX1NCX0VfQVBJX0VJIl0sImp0aSI6ImE1YTc5NjdkLWM4ODItNGViMS1hY2MzLTE1NjEwYmRkNGUzMiIsImNsaWVudF9pZCI6IjA1MTQ5NTIyNDAwNTQ4RkM4OTUxRjQ2QzhFMjY4RDlGIn0.Wa5Q2vuyWSjEd5_YtWGVk6bEcZbvDxPxaTZt2RlLsqQ', "requestid":int_request_id }
        url = "https://gsp.adaequare.com/test/enriched/ei/api/invoice"
        if bln_host_status:
            headers={ "Content-Type": "application/json", "user_name":'Mygmobile_API_myg', "password":"myGoal@98466699", "gstin": '32AAAFZ4615J1Z8', "Authorization":'bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJnc3AiXSwiZXhwIjoxNjA0MDYwOTY4LCJhdXRob3JpdGllcyI6WyJST0xFX1BST0RfRV9BUElfRUkiLCJST0xFX1BST0RfRV9BUElfRVdCIl0sImp0aSI6IjUwOTgwOTYzLTY2ZTktNDlmOS1hY2EwLTg5NWRjOTdkNGEzNCIsImNsaWVudF9pZCI6IjE1QkQ4MkY3QkJCNTRERDlBOTNBMTk5OTA1QjFBMTY0In0.8D1sPBD8zUX4BTYQg_MDlCEqxTXcUktR5up0VQYO8G8', "requestid":int_request_id }
            url = "https://gsp.adaequare.com/enriched/ei/api/invoice"

        res1 = requests.post(url,headers=headers,data=json_invoice_data)
        if res1.status_code == 401:
            headers_access={"gspappid" :"15BD82F7BBB54DD9A93A199905B1A164", "gspappsecret":"884F4D1FGCA97G4E17G824BG98F69CABDDC0"}
            # headers_access={"gspappid" :"15BD82F7BBB54DD9A93A199905B1A164", "gspappsecret":"884F4D1FGCA97G4E17G824BG98F69CABDDC0"}
            # headers_access={"gspappid" :"4F14C9BB0DDD45A9B5BD5DCE1B7FA23B", "gspappsecret":"3A770CF5G1D97G4032GBDF8G1D5C436162EA"}
            # requests.post("https://gsp.adaequare.com/gsp/authenticate?grant_type=token",headers=headers_access)
            res1 = requests.post("https://gsp.adaequare.com/gsp/authenticate?grant_type=token",headers=headers_access)
            headers['Authorization']='bearer '+json.loads(str(res1.content)[2:-1])['access_token']
            res1 = requests.post(url,headers=headers,data=json_invoice_data)

        if not json.loads(res1.content.decode('utf-8')).get('success'):
            data = json.loads(res1.text).get('error_description')
            raise ValueError(data)

        str_temp = res1.content.decode('utf-8')
        if bln_status:
            StockTransfer.objects.filter(pk_bint_id =int_id).update(txt_qr_code = json.loads(res1.content.decode('utf-8'))['result']['SignedQRCode'], vchr_irn_no = json.loads(res1.content.decode('utf-8'))['result']['Irn'])
            qr_code_file_name = ins_stock_transfer['vchr_stktransfer_num']+"_qr_code.png"
        else:
            SalesMaster.objects.filter(pk_bint_id =int_id).update(txt_qr_code = json.loads(res1.content.decode('utf-8'))['result']['SignedQRCode'], vchr_irn_no = json.loads(res1.content.decode('utf-8'))['result']['Irn'])
            qr_code_file_name = ins_sales_master["vchr_invoice_num"]+"_qr_code.png"

        qr_code = json.loads(res1.content.decode('utf-8'))['result']['SignedQRCode']
        url = pyqrcode.create(qr_code)
        url.png(settings.MEDIA_ROOT+"/"+qr_code_file_name, scale = 6)

        data = {"status":1,"reason":"success"}
        return data
    except  Exception as e:
        # SalesMaster.objects.filter(pk_bint_id =int_id).update(txt_qr_code = None, vchr_irn_no = None)
        
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # ins_logger.logger.error(e, extra={'details':'line no: ' + str(exc_tb.tb_lineno)})
        # data = {"status":0,"reason":str(e)+' '+str_temp,'bln_permitted':True}
        raise



class EcomSalesCancelApi(APIView):
    permission_classes=[AllowAny]
    def patch(self,request):
        try:
            int_enq_master_id = request.data.get('int_enq_id')
            str_remark = request.data.get('strRemark')
            if not str_remark:
                str_remark='Sale cancelled by Ecom'
            # int_partial_id = 11
            with transaction.atomic():
                int_partail = PartialInvoice.objects.filter(int_enq_master_id = int_enq_master_id).first()
                dct_jsn_data = int_partail.json_data
                dct_jsn_data['str_remarks'] = str_remark
                int_partail.json_data = dct_jsn_data
                int_partail.int_active=-1
                int_partail.save()
                return Response({'status':1,'message':'Successfully Rejected'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':str(e)})

def EnquiryInvoiceUpdate(data):
        try:
            """ bi class for adding invoice data for enquiry master """            
            with transaction.atomic():
                # import pdb; pdb.set_trace()
                str_remark = data.get('str_remarks') or ""  
                dct_item_data = data.get('dct_item_data')
                int_type=data.get('int_type')
                lst_item_data = list(dct_item_data.values())
                int_enq_master_id = data.get('int_enq_master_id')
                ins_user_id = EnquiryMaster.objects.filter(pk_bint_id=int_enq_master_id).values('fk_assigned_id').first()['fk_assigned_id']
                lst_item_code_cur_all = ItemEnquiry.objects.filter(fk_enquiry_master_id = int_enq_master_id,vchr_enquiry_status__in=['BOOKED','FINANCED','SPECIAL SALE']).values_list('pk_bint_id',flat=True)
                if not lst_item_code_cur_all:
                    return Response({'status':'success'})
                int_sale_type = EnquiryMaster.objects.get(pk_bint_id=int_enq_master_id).int_customer_type
                str_status = 'INVOICED'
                if int_sale_type and int_sale_type == 1:
                    str_status = 'IMAGE PENDING'
                lst_old_item = []
                lst_service_item = []
                # Structure the old item details with item enquiry id keys to update item enquiry table

                """Data to payment_details"""

                # if data.get('bi_payment_details'):
                #     lst_payment_details=[]
                #     for data in data['bi_payment_details']:
                #         ins_payment_details=PaymentDetails(fk_enquiry_master_id = int_enq_master_id, int_fop = data['int_fop'], dbl_amount = data['dbl_amt'], dat_created = datetime.today())
                #         lst_payment_details.append(ins_payment_details)
                #     PaymentDetails.objects.bulk_create(lst_payment_details)
                # else:
                #     if data.get("credit_sale"):
                #         dct_item_data_ = data.get("dct_item_data")
                #         if dct_item_data_:
                #             total_amount_ = sum([dct_item_data_[x]['dblAmount'] for x in dct_item_data_])
                #             ins_payment_details = PaymentDetails.objects.create(fk_enquiry_master_id=int_enq_master_id, int_fop= -1,
                #             dbl_amount = total_amount_, dat_created = datetime.today()) # -1 for credit sale


                # import pdb; pdb.set_trace()
                for str_data in dct_item_data:
                    apx_amount = None
                    if str_data.split('-')[0] == '0' and ItemEnquiry.objects.filter(pk_bint_id =  str_data.split('-')[1]).exclude(vchr_enquiry_status='INVOICED'):
                        ins_item_enq = ItemEnquiry.objects.filter(pk_bint_id =  str_data.split('-')[1])
                        ins_product = ins_item_enq.values('fk_product__vchr_name')[0]['fk_product__vchr_name']
                        if ins_product.upper() != 'SERVICE':
                            apx_amount = ins_item_enq.values('fk_item__dbl_mop')[0]['fk_item__dbl_mop']
                        else:
                            lst_service_item.append(str_data)

                        lst_old_item.append(int(str_data.split('-')[1]))
                        ins_item_enq.update(dbl_buy_back_amount = dct_item_data[str_data]['dblBuyBack'],
                                                dbl_discount_amount = dct_item_data[str_data]['dblDiscount'],
                                                dbl_amount = dct_item_data[str_data]['dblAmount'] +dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                dbl_imei_json = {'imei' : dct_item_data[str_data].get('jsonImei')},
                                                int_sold = dct_item_data[str_data]['intQuantity'],
                                                dbl_sup_amount = dct_item_data[str_data]['dbl_supp_amnt'],
                                                vchr_remarks = str_remark,
                                                vchr_enquiry_status = str_status,
                                                dat_sale = datetime.now(),
                                                dbl_indirect_discount_amount=dct_item_data[str_data]['dblIndirectDis'],

                                                # LG
                                                dbl_cost_price = dct_item_data[str_data]['dbl_cost_amnt'],
                                                dbl_dealer_price  = dct_item_data[str_data]['dbl_dealer_amnt'],
                                                dbl_mop_price = dct_item_data[str_data]['dbl_mop_amnt'],
                                                dbl_myg_price = dct_item_data[str_data]['dbl_myg_amnt'],
                                                dbl_mrp_price = dct_item_data[str_data]['dbl_mrp_amnt'],

                                                dbl_tax = dct_item_data[str_data]['dbl_tax'],
                                                json_tax = dct_item_data[str_data]['json_tax']
                                                )



                        ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = str_data.split('-')[1],
                                                            vchr_notes = str_status,
                                                            vchr_enquiry_status = str_status,
                                                            int_status = 1,
                                                            dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack']+dct_item_data[str_data]['dblDiscount'],
                                                            fk_user_id = ins_user_id,
                                                            int_quantity = dct_item_data[str_data]['intQuantity'],
                                                            fk_updated_id = ins_user_id,
                                                            dat_followup = datetime.now(),
                                                            dat_updated = datetime.now())

                    else:
                        # import pdb;pdb.set_trace()
                        ins_item = Item.objects.filter(vchr_item_code= dct_item_data[str_data]['strItemCode'])
                        ins_product = ins_item.values('fk_product__vchr_name')[0]['fk_product__vchr_name']
                        if ins_product.upper() != 'SERVICE':
                            # ins_item_enq.update(dbl_actual_est_amt = dct_old_item[int_id]['data']['apx_amount'])
                            apx_amount = ins_item.values('dbl_mop')[0]['dbl_mop']
                        else:
                            lst_service_item.append(str_data)
                        if dct_item_data[str_data]['status']==1:
                            ins_item_enq = ItemEnquiry(fk_enquiry_master_id = int_enq_master_id,
                                                        fk_item_id = ins_item.values('pk_bint_id')[0]['pk_bint_id'],
                                                        dbl_buy_back_amount = dct_item_data[str_data]['dblBuyBack'],
                                                        dbl_discount_amount = dct_item_data[str_data]['dblDiscount'],
                                                        dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                        # dbl_imei_json = dct_item_data[str_data]['jsonImei'],
                                                        dbl_imei_json = {'imei' : dct_item_data[str_data].get('jsonImei')},
                                                        int_quantity = dct_item_data[str_data]['intQuantity'],
                                                        int_sold = dct_item_data[str_data]['intQuantity'],
                                                        fk_product_id = ins_item.values('fk_product_id')[0]['fk_product_id'],
                                                        fk_brand_id =  ins_item.values('fk_brand_id')[0]['fk_brand_id'],
                                                        vchr_enquiry_status = str_status,
                                                        dbl_actual_est_amt = apx_amount,
                                                        dbl_sup_amount = dct_item_data[str_data]['dbl_supp_amnt'],
                                                        dat_sale = datetime.now(),
                                                        vchr_remarks = str_remark,
                                                        dbl_indirect_discount_amount=dct_item_data[str_data]['dblIndirectDis'],

                                                        # LG
                                                        dbl_cost_price = dct_item_data[str_data]['dbl_cost_amnt'],
                                                        dbl_dealer_price  = dct_item_data[str_data]['dbl_dealer_amnt'],
                                                        dbl_mop_price = dct_item_data[str_data]['dbl_mop_amnt'],
                                                        dbl_myg_price = dct_item_data[str_data]['dbl_myg_amnt'],
                                                        dbl_mrp_price = dct_item_data[str_data]['dbl_mrp_amnt'],

                                                        dbl_tax = dct_item_data[str_data]['dbl_tax'],
                                                        json_tax = dct_item_data[str_data]['json_tax']
                                                        )
                            ins_item_enq.save()

                            ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq.pk_bint_id,
                                                                vchr_notes =str_status,
                                                                vchr_enquiry_status = str_status,
                                                                int_status = 1,
                                                                dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                                fk_user_id = ins_user_id,
                                                                int_quantity = dct_item_data[str_data]['intQuantity'],
                                                                fk_updated_id = ins_user_id,
                                                                dat_followup = datetime.now(),
                                                                dat_updated = datetime.now())
                        elif dct_item_data[str_data]['status']==0:
                            ins_item_enq = ItemEnquiry(fk_enquiry_master_id = int_enq_master_id,
                                                        fk_item_id = ins_item.values('pk_bint_id')[0]['pk_bint_id'],
                                                        dbl_buy_back_amount = dct_item_data[str_data]['dblBuyBack'],
                                                        dbl_discount_amount = dct_item_data[str_data]['dblDiscount'],
                                                        dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                        # dbl_imei_json = dct_item_data[str_data]['jsonImei'],
                                                        dbl_imei_json = {'imei' : dct_item_data[str_data].get('jsonImei')},
                                                        int_quantity = dct_item_data[str_data]['intQuantity'],
                                                        int_sold = dct_item_data[str_data]['intQuantity'],
                                                        fk_product_id = ins_item.values('fk_product_id')[0]['fk_product_id'],
                                                        fk_brand_id =  ins_item.values('fk_brand_id')[0]['fk_brand_id'],
                                                        vchr_enquiry_status = 'RETURNED',
                                                        dbl_actual_est_amt = apx_amount,
                                                        dbl_sup_amount = dct_item_data[str_data]['dbl_supp_amnt'],
                                                        dat_sale = datetime.now(),
                                                        vchr_remarks = str_remark,

                                                        # LG
                                                        dbl_cost_price = dct_item_data[str_data]['dbl_cost_amnt'],
                                                        dbl_dealer_price  = dct_item_data[str_data]['dbl_dealer_amnt'],
                                                        dbl_mop_price = dct_item_data[str_data]['dbl_mop_amnt'],
                                                        dbl_myg_price = dct_item_data[str_data]['dbl_myg_amnt'],
                                                        dbl_mrp_price = dct_item_data[str_data]['dbl_mrp_amnt'],

                                                        dbl_tax = dct_item_data[str_data]['dbl_tax'],
                                                        json_tax = dct_item_data[str_data]['json_tax']
                                                        )
                            ins_item_enq.save()
                            ins_enquiry_master=EnquiryMaster.objects.get(pk_bint_id=int_enq_master_id)
                            ins_item_enquiry_return=ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer_id=ins_enquiry_master.fk_customer_id,dbl_imei_json__contains={'imei':dct_item_data[str_data]['jsonImei']})
                            if ins_item_enquiry_return:
                                ins_avaialble=RewardsAvailable.objects.filter(fk_item_enquiry_id=ins_item_enquiry_return[0].pk_bint_id).values()
                                if ins_avaialble:
                                    for data in ins_avaialble:
                                        RewardsAvailable.objects.create(fk_rewards_master_id=data['fk_rewards_master_id'],fk_rewards_details_id=data['fk_rewards_details_id'],fk_item_enquiry_id=data['fk_item_enquiry_id'],dat_reward=datetime.now(),dbl_mop_amount=data['dbl_mop_amount'],json_staff={dct_rwd_data:-data['json_staff'][dct_rwd_data] for dct_rwd_data in data['json_staff']})
                            ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq.pk_bint_id,
                                                            vchr_notes = 'RETURNED',
                                                            vchr_enquiry_status = 'RETURNED',
                                                            int_status = 1,
                                                            dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                            fk_user_id = ins_user_id,
                                                            int_quantity = dct_item_data[str_data]['intQuantity'],
                                                            fk_updated_id = ins_user_id,
                                                            dat_followup = datetime.now(),
                                                            dat_updated = datetime.now())
                lst_deleted_item = list(set(lst_item_code_cur_all)-set(lst_old_item))
                # import pdb; pdb.set_trace()
                # IMAGE PENDING -NOTIFICATION
                if str_status == 'IMAGE PENDING':
                    if str_data.split('-')[0] == '0' and ItemEnquiry.objects.filter(pk_bint_id =  str_data.split('-')[1]).exclude(vchr_enquiry_status='INVOICED'):
                        ins_assigned = EnquiryMaster.objects.filter(pk_bint_id = ins_item_enq[0].fk_enquiry_master_id).values('fk_assigned_id').first()
                    else:
                        ins_assigned = EnquiryMaster.objects.filter(pk_bint_id = ins_item_enq.fk_enquiry_master_id).values('fk_assigned_id').first()

                    int_assigned = ins_assigned['fk_assigned_id']
                    ins_rem = Reminder.objects.filter(fk_user = int_assigned, vchr_description__icontains = '(IMAGE PENDING)')
                    count_old = ItemEnquiry.objects.filter(fk_enquiry_master_id__fk_assigned_id = int_assigned,vchr_enquiry_status = 'IMAGE PENDING').values('fk_enquiry_master_id__fk_assigned_id').count()
                    actual_count = count_old
                    if actual_count > 1:
                        str_notification = str(actual_count) + ' enquiries need to be updated with proper images(IMAGE PENDING)'

                    elif actual_count == 1:
                        str_notification = str(actual_count) + ' enquiry needs to be updated with proper images(IMAGE PENDING)'

                    if actual_count != 0:
                        ins_reminder = Reminder.objects.create(fk_user_id        = int_assigned,
                                                                dat_created_at   = datetime.now(),
                                                                dat_updated_at   = datetime.now(),
                                                                vchr_title       = 'IMAGE PENDING ENQUIRY',
                                                                vchr_description = str_notification,
                                                                dat_reminder     = datetime.now()
                                                                )
                # NOTIFICATION END
                for int_enq_id in lst_deleted_item:
                    ins_item_enq=ItemEnquiry.objects.filter(pk_bint_id =  int_enq_id)
                    ins_item_enq.update(vchr_enquiry_status = 'PENDING')
                    ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = int_enq_id,
                                                        vchr_notes = 'PENDING',
                                                        vchr_enquiry_status = 'PENDING',
                                                        int_status = 1,
                                                        dbl_amount = ins_item_enq[0].dbl_amount,
                                                        fk_user_id = ins_user_id,
                                                        int_quantity = ins_item_enq[0].int_quantity,
                                                        fk_updated_id = ins_user_id,
                                                        dat_followup = datetime.now(),
                                                        dat_updated = datetime.now()
                    )
                for str_data in lst_service_item:
                    if dct_item_data[str_data]['int_type']==1 or dct_item_data[str_data]['int_type']==2:
                        ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[str_data].get('jsonImei')})|Q(dbl_imei_json__contains=dct_item_data[str_data].get('jsonImei')),fk_enquiry_master_id=int_enq_master_id).values('fk_item__dbl_apx_amount','int_type','int_quantity').exclude(fk_product__vchr_product_name='SERVICE').first()
                        if not ins_up_item_enq:
                            ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[str_data].get('jsonImei')})|Q(dbl_imei_json__contains=dct_item_data[str_data].get('jsonImei'))).values('fk_item__dbl_apx_amount','int_type','int_quantity').exclude(fk_product__vchr_product_name='SERVICE').first()
                        ins_up_item_enq['fk_item__dbl_apx_amount'] = ins_up_item_enq['fk_item__dbl_apx_amount'] if ins_up_item_enq.get('fk_item__dbl_apx_amount') else 0
                        gdp_value=GDPRange.objects.filter(dbl_from__lte=(ins_up_item_enq['fk_item__dbl_apx_amount']),dbl_to__gte=(ins_up_item_enq['fk_item__dbl_apx_amount']),int_type=dct_item_data[str_data]['int_type']).values('dbl_amt').first()
                        if ins_up_item_enq['int_type']!=0:
                            if ins_up_item_enq['int_type']!=dct_item_data[str_data]['int_type']:
                                ins_up_item_enq.update(int_type=3)
                        else:
                            ins_up_item_enq.update(int_type=dct_item_data[str_data]['int_type'])
                        gdp_value = gdp_value['dbl_amt'] if gdp_value else 0
                        if dct_item_data[str_data]['int_type']==1:
                            ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[str_data].get('jsonImei')})|Q(dbl_imei_json__contains=dct_item_data[str_data].get('jsonImei')),fk_item__vchr_item_code='GDC00001',fk_enquiry_master_id=int_enq_master_id).update(dbl_actual_est_amt=gdp_value)
                        if dct_item_data[str_data]['int_type']==2:
                            ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[str_data].get('jsonImei')})|Q(dbl_imei_json__contains=dct_item_data[str_data].get('jsonImei')),fk_item__vchr_item_name='GDC00002',fk_enquiry_master_id=int_enq_master_id).update(dbl_actual_est_amt=gdp_value)
                # commented for o2force
                # special_rewards_script_sudheesh(int_enq_master_id)
                # custome_enq(int_enq_master_id,
                # Uncomment When using celery
                # send_feedback_sms.delay(int_enq_master_id)
                # send_feedback_sms(int_enq_master_id)

                return {'status':'success'}
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' })
            return {'status':'failed','message':str(e)}
