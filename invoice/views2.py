from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from invoice.models import PartialInvoice
from customer.models import CustomerDetails,SalesCustomerDetails
from userdetails.models import Userdetails
from branch.models import Branch
from invoice.models import PartialInvoice, SalesMaster, SalesDetails, CustServiceDelivery, LoyaltyCardInvoice, PaymentDetails,SalesMasterJio,Bank
from item_category.models import Item,TaxMaster
from loyalty_card.models import LoyaltyCard, LoyaltyCardStatus
from company.models import FinancialYear
from purchase.models import Document
from states.models import States, Location, District
from purchase.models import GrnDetails
from branch_stock.models import BranchStockDetails, BranchStockImeiDetails
from sales_return.models import SalesReturn
from brands.models import Brands
from products.models import Products
from pricelist.models import PriceList
from coupon.models import Coupon
from datetime import datetime,date
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
from terms.models import Terms

from POS.dftosql import Savedftosql
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from datetime import timedelta
import pdfkit
import base64
import json

from receipt.models import ReceiptInvoiceMatching
from tool_settings.models import Tools

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


class SalesList(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request):
        try:
            dat_to = (datetime.strptime(request.data.get("datTo")[:10],'%Y-%m-%d')).date()
            dat_from = (datetime.strptime(request.data.get("datFrom")[:10],'%Y-%m-%d')).date()
            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                ins_partial_inv = PartialInvoice.objects.filter(int_active = 0,dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
            else:
                ins_partial_inv = PartialInvoice.objects.filter(int_active = 0,json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id},dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')

            lst_data = []
            dct_branch=dict(Branch.objects.values_list('pk_bint_id','vchr_name'))
            for ins_data in ins_partial_inv:
                dct_data = {}
                dct_data['intId'] = ins_data['pk_bint_id']
                dct_data['datBooked'] = ins_data['dat_created'].strftime("%d-%m-%Y")
                dct_data['strCustomer'] = ins_data['json_data']['str_cust_name'].title()
                dct_data['strStaff'] = ins_data['json_data'].get('str_staff_name').title()
                dct_data['strEnqNo'] = ins_data['json_data'].get('vchr_enquiry_num')
                dct_data['branch'] = dct_branch.get(ins_data['json_data'].get('int_branch_id'))

                dct_data['sales_status'] = ins_data['int_status']
                dct_data['strItem'] = ''
                dct_data['strItem'] = ' , '.join([ i['vchr_item_name']for i in ins_data['json_data']['lst_items']])
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
            # import pdb;pdb.set_trace()
            int_id = request.data.get('intId')
            ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = int_id,int_active = 0).values('dat_created','json_data','int_status').first()
            if not ins_partial_inv:
                return Response({'status':'0','message':'Already Invoiced'})
            dct_data = {}
            ins_customer = SalesCustomerDetails.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_sales_cust_id']).values('pk_bint_id','fk_customer_id','vchr_name','vchr_email','int_mobile','txt_address','vchr_gst_no','fk_location__vchr_name','fk_location__vchr_pin_code','fk_location_id','fk_state_id','fk_state__vchr_name','int_loyalty_points','int_redeem_point').first()
            # ================================================================================
            dct_data['intSalesCustId'] =  ins_customer['pk_bint_id']
            # ================================================================================
            dct_data['intStaffId'] = ins_partial_inv['json_data']['int_staff_id']
            dct_data['strStaffName'] = Userdetails.objects.filter(user_ptr_id = ins_partial_inv['json_data']['int_staff_id']).annotate(str_name=Concat('first_name', Value(' '), 'last_name')).values('str_name').first()['str_name']
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
            dct_data['txtRemarks'] = ins_partial_inv['json_data']['str_remarks']
            dct_data['intLoyaltyPoint'] = (ins_customer['int_loyalty_points'] if ins_customer['int_loyalty_points'] else 0)- (ins_customer['int_redeem_point'] if ins_customer['int_redeem_point'] else 0)
            dct_data['job_status']=ins_partial_inv['int_status']
            dct_data['partial_id'] = int_id
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
                dct_data['dblDownPayment'] = ins_partial_inv['json_data']['dbl_down_payment']
                dct_data['vchrFinOrdrNum'] = ins_partial_inv['json_data']['vchr_fin_ordr_num']
            dct_data['intAmtPerPoints'] = 1/settings.LOYALTY_POINT
            dct_data['lstItems'] = []
            dct_data['blnIGST'] = False
            if request.user.userdetails.fk_branch.fk_states_id != ins_customer['fk_state_id']:
                dct_data['blnIGST'] = True
            dct_tax_master = {}
            for ins_tax in TaxMaster.objects.values('pk_bint_id','vchr_name'):
                dct_tax_master[ins_tax['vchr_name']] = str(ins_tax['pk_bint_id'])
            for ins_items_data in ins_partial_inv['json_data']['lst_items']:
                ins_items = Item.objects.filter(vchr_item_code = ins_items_data['vchr_item_code'],int_status=0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master').first()

                if not ins_items:
                    return Response({'status':'0','message':'Item Not Found'})
                for row in range(int(ins_items_data['int_quantity'])):
                    dct_item = {}
                    dct_item['strItemCode'] = ins_items['vchr_item_code']
                    dct_item['intItemId'] = ins_items['pk_bint_id']
                    dct_item['strItemName'] = ins_items['vchr_name']
                    dct_item['intQuantity'] = ins_items_data['int_quantity']
                    dct_item['intStatus'] = ins_items_data['int_status']
                    dct_item['itemEnqId'] = ins_items_data['item_enquiry_id']
                    if ins_items_data['int_status'] == 2:
                        dct_item['dctImages'] = ins_items_data['dct_images']

                    if len(ins_items_data['json_imei']['imei'])>0:
                        dct_item['strImei'] = ins_items_data['json_imei']['imei'][row]
                        ins_grn_details = GrnDetails.objects.filter(fk_item_id=ins_items['pk_bint_id'],jsn_imei_avail__contains={'imei_avail':[dct_item['strImei']]}).values('jsn_tax').last()
                    # else:
                    #     ins_grn_details = GrnDetails.objects.filter(fk_item_id=ins_items['pk_bint_id'],vchr_batch_no=dct_item['strBatchNo']).values('jsn_tax').last()
                    dbl_buyback = ins_items_data['dbl_buyback'] / int(ins_items_data['int_quantity'])
                    dbl_discount = ins_items_data['dbl_discount'] / int(ins_items_data['int_quantity'])
                    dbl_rate = (ins_items_data['dbl_amount'] / int(ins_items_data['int_quantity']))
                    dbl_tax=0
                    dct_item['dblBuyBack'] = round(dbl_buyback,2)
                    dct_item['dblDiscount'] = round(dbl_discount,2)
                    dbl_amt = (dbl_rate+dbl_buyback+dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))/100)
                    dct_item['dblIGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))
                    dct_item['dblIGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0)/100)
                    dbl_amt = (dbl_rate+dbl_buyback+dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))/100)
                    dct_item['dblCGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0))
                    dct_item['dblCGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)/100)
                    dct_item['dblSGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))
                    dct_item['dblSGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0)/100)
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
                        # dct_item['dblRate'] = round(dbl_rate-dct_item['dblCGST']-dct_item['dblSGST'],2)
                    # dct_item['dblAmount'] = round(dct_item['dblRate'] - dct_item['dblBuyBack'] - dct_item['dblDiscount']+dbl_tax,2)
                    # dct_item['dblAmount'] = 0
                    dct_item['dblAmount'] = round(dbl_rate-dbl_buyback-dbl_discount,2)
                    # dct_item['status'] = False
                    dct_data['lstItems'].append(dct_item)



            """adddition and deduction on admin tools"""
            # import pdb; pdb.set_trace()
            rst_admin_tools = dict(Tools.objects.filter(vchr_tool_code__in =("ADDITION","DEDUCTION")).values_list('vchr_tool_code','jsn_data'))
            dct_data['admin_tools'] = rst_admin_tools

            return Response({'status':1,'data':dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


class AddInvoice(APIView):
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

                """admin tools"""
                json_addition = json.loads(request.data.get('json_additions'))
                json_deduction = json.loads(request.data.get('json_deductions'))

                dct_addition = {}
                dct_deduction = {}
                for ins_addition in json_addition:
                    dct_addition[ins_addition['name']] = ins_addition['value']
                for ins_deduction in json_deduction:
                    dct_deduction[ins_deduction['name']] = ins_deduction['value']


                if request.data.get('offerAmt'):
                    int_offer=int(request.data.get('offerAmt')[0])
                else:
                    int_offer=0
                ins_branch_code = Branch.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_branch_id']).values('vchr_code').first()['vchr_code']
                ins_document = Document.objects.select_for_update().filter(vchr_module_name = ins_branch_code,vchr_short_code = ins_branch_code)
                if not ins_document:
                    ins_document = Document.objects.create(vchr_module_name = ins_branch_code,vchr_short_code = ins_branch_code,int_number = 1)
                str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                ins_document.int_number = ins_document.int_number+1
                ins_document.save()

                ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId')).values().first()

                ins_branch = Branch.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_branch_id']).first()
                ins_staff = Userdetails.objects.filter(user_ptr_id = ins_partial_inv['json_data']['int_staff_id']).first()
                ins_customer = CustomerDetails.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_cust_id']).first()
                ins_sales_customer = SalesCustomerDetails.objects.filter(pk_bint_id = request.data.get('intSalesCustId')).first()

                if request.user.userdetails.fk_branch.fk_states_id != ins_sales_customer.fk_state_id:
                # if request.user.userdetails.fk_branch.fk_states_id != ins_customer.fk_state_id:
                    bln_igst = True
                odct_item_data = OrderedDict()
                dbl_total_amt = 0
                dbl_total_tax = 0
                json_total_tax = {'dblIGST':0,'dblCGST':0,'dblSGST':0}
                dbl_total_rate = 0
                dbl_total_buyback = 0
                dbl_total_discount = 0

                for dct_item in dct_item_data:
                    # import pdb; pdb.set_trace()
                    # dct_item['status'] = 1
                    str_temp = str(dct_item['intItemId'])+'-'+str(dct_item['dblAmount'])+'-'+str(dct_item['intStatus'])
                    # str_temp = str(dct_item['intItemId'])+'-'+str(dct_item['dblAmount'])
                    if str_temp in odct_item_data:
                    # if str_temp in odct_item_data and odct_item_data[str_temp]['dblBuyBack'] == dct_item['dblBuyBack'] and odct_item_data[str_temp]['dblDiscount'] == dct_item['dblDiscount'] and odct_item_data[str_temp]['dblAmount'] == dct_item['dblAmount'] and odct_item_data[str_temp]['dblRate'] == dct_item['dblRate']:
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
                            odct_item_data[str_temp]['dblCGST'] += dct_item['dblCGST']
                            odct_item_data[str_temp]['dblSGST'] += dct_item['dblSGST']
                            dbl_total_tax += dct_item['dblCGST'] + dct_item['dblSGST']
                            json_total_tax['dblCGST'] += dct_item['dblCGST']
                            json_total_tax['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['jsonTax']['dblCGST'] += dct_item['dblCGST']
                            odct_item_data[str_temp]['jsonTax']['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['dblTax'] += dct_item['dblCGST']+dct_item['dblSGST']

                        # odct_item_data[str_temp]['itemEnqId'] = dct_item['itemEnqId']
                        odct_item_data[str_temp]['dblBuyBack'] += dct_item['dblBuyBack']
                        odct_item_data[str_temp]['dblDiscount'] += dct_item['dblDiscount']
                        odct_item_data[str_temp]['dblRate'] += dct_item['dblRate']
                        odct_item_data[str_temp]['dblAmount'] += dct_item['dblAmount']
                        odct_item_data[str_temp]['intQuantity'] += 1
                        if dct_item.get('strImei',''):
                            odct_item_data[str_temp]['jsonImei'].append(dct_item.get('strImei',''))
                        odct_item_data[str_temp]['int_type'] = dct_item.get('int_type') or 0

                    else:
                        odct_item_data[str_temp] = {}
                        odct_item_data[str_temp]['strItemCode'] = dct_item['strItemCode']
                        odct_item_data[str_temp]['intItemId'] = dct_item['intItemId']
                        odct_item_data[str_temp]['dblBuyBack'] = dct_item['dblBuyBack']
                        odct_item_data[str_temp]['dblDiscount'] = dct_item['dblDiscount']
                        odct_item_data[str_temp]['dblAmount'] = dct_item['dblAmount']
                        odct_item_data[str_temp]['dblRate'] = dct_item['dblRate']
                        odct_item_data[str_temp]['itemEnqId'] = dct_item.get('itemEnqId',0)

                        odct_item_data[str_temp]['jsonImei'] = []
                        if dct_item.get('strImei',''):
                            odct_item_data[str_temp]['jsonImei'] = [dct_item.get('strImei','')]
                        odct_item_data[str_temp]['int_type'] = dct_item.get('int_type') or 0
                        odct_item_data[str_temp]['jsonTax'] = {'dblIGST':0,'dblCGST':0,'dblSGST':0}
                        odct_item_data[str_temp]['dblTax'] = 0
                        odct_item_data[str_temp]['dblIndirectDis'] = dct_item.get('dblIndirectDis')
                        # import pdb; pdb.set_trace()
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
                            odct_item_data[str_temp]['dblCGST'] = dct_item['dblCGST']
                            odct_item_data[str_temp]['dblSGST'] = dct_item['dblSGST']
                            dbl_total_tax += dct_item['dblCGST'] + dct_item['dblSGST']
                            json_total_tax['dblCGST'] += dct_item['dblCGST']
                            json_total_tax['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['jsonTax']['dblCGST'] += dct_item['dblCGST']
                            odct_item_data[str_temp]['jsonTax']['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['dblTax'] += dct_item['dblCGST'] + dct_item['dblSGST']
                        odct_item_data[str_temp]['intQuantity'] = 1


                # ins_sales_master = SalesMaster.objects.create_inv_num(str_inv_num)
                ins_sales_master = SalesMaster.objects.create(
                                        fk_customer = ins_sales_customer,
                                        # fk_customer = ins_customer,
                                        fk_branch = ins_branch,
                                        vchr_invoice_num = str_inv_num,
                                        dat_invoice = date.today(),
                                        vchr_remarks = str_remarks,
                                        dat_created = datetime.now(),
                                        int_doc_status = 1,
                                        dbl_total_amt = dbl_total_amt,
                                        dbl_rounding_off = dbl_rounding_off,
                                        jsn_addition = json.dumps(dct_addition),
                                        jsn_deduction = json.dumps(dct_deduction),
                                        dbl_total_tax = dbl_total_tax,
                                        dbl_discount = dbl_total_discount + int_offer,
                                        json_tax = json_total_tax,
                                        dbl_buyback = dbl_total_buyback,
                                        fk_loyalty_id = request.data.get('intLoyaltyId',None),
                                        dbl_loyalty = (1/settings.LOYALTY_POINT)*int_redeem_point,
                                        fk_staff = ins_staff,
                                        fk_created = request.user.userdetails,
                                        fk_coupon_id = request.data.get('intCouponId',None),
                                        dbl_coupon_amt = request.data.get('intCouponDisc',None),
                                        fk_financial_year = FinancialYear.objects.filter(dat_start__lte = date.today(),dat_end__gte = date.today()).first())
                ins_sales_master.save()

                for ins_data in odct_item_data:
                    for vchr_stk_imei in odct_item_data[ins_data]['jsonImei']:
                        ins_br_stock = BranchStockDetails.objects.filter(Q(jsn_imei_avail__contains={'imei':[str(vchr_stk_imei)]}),fk_item_id=odct_item_data[ins_data]['intItemId']).first()
                        ins_br_stk_imei = BranchStockImeiDetails.objects.filter(Q(jsn_imei__contains={'imei':[str(vchr_stk_imei)]}),fk_details=ins_br_stock).first()
                        if ins_br_stock:
                            lst_imei = ins_br_stock.jsn_imei_avail['imei']
                            lst_imei.remove(vchr_stk_imei)
                            int_qty = ins_br_stock.int_qty-1
                            BranchStockDetails.objects.filter(pk_bint_id=ins_br_stock.pk_bint_id).update(jsn_imei_avail={'imei':lst_imei},int_qty=int_qty)
                        if ins_br_stk_imei:
                            lst_imei = ins_br_stk_imei.jsn_imei['imei']
                            lst_imei.remove(vchr_stk_imei)
                            int_qty = ins_br_stock.int_qty-1
                            BranchStockImeiDetails.objects.filter(Q(jsn_imei__contains={'imei':[str(vchr_stk_imei)]}),fk_details=ins_br_stock).update(jsn_imei={'imei':lst_imei},int_qty=int_qty)
                    SalesDetails.objects.create(fk_master = ins_sales_master,
                                        fk_item_id = odct_item_data[ins_data]['intItemId'],
                                        int_qty = odct_item_data[ins_data]['intQuantity'],
                                        dbl_amount = odct_item_data[ins_data]['dblRate'],
                                        dbl_selling_price = odct_item_data[ins_data]['dblAmount'],
                                        dbl_tax = odct_item_data[ins_data]['dblTax'],
                                        dbl_discount = odct_item_data[ins_data]['dblDiscount'] + int_offer,
                                        dbl_buyback = odct_item_data[ins_data]['dblBuyBack'],
                                        json_tax = odct_item_data[ins_data]['jsonTax'],
                                        # vchr_batch=odct_item_data[ins_data][''],
                                        json_imei = odct_item_data[ins_data]['jsonImei'],
                                        int_sales_status=odct_item_data[ins_data].get('status'),
                                        dbl_indirect_discount=odct_item_data[ins_data].get('dblIndirectDis'),
                                        int_doc_status = 1,
                                        dbl_supplier_amount = 0)

                    #==========sales return============
                    # import pdb; pdb.set_trace()
                    if odct_item_data[ins_data]['status'] == 0:
                        ins_sales_returned = SalesDetails.objects.filter(fk_item__pk_bint_id = odct_item_data[ins_data]['intItemId'],fk_master__fk_customer = ins_sales_customer).values('fk_master__pk_bint_id')
                        # ins_sales_returned = SalesDetails.objects.filter(fk_item__pk_bint_id = odct_item_data[ins_data]['intItemId'],fk_master__fk_customer = ins_customer).values('fk_master__pk_bint_id')

                        if request.FILES.get(str(odct_item_data[ins_data]['intItemId'])):
                            img_item = request.FILES.get(str(odct_item_data[ins_data]['intItemId']))
                            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                            str_img = fs.save(img_item.name, img_item)
                            str_img_path = fs.url(str_img)

                        else:
                            str_img_path = ""
                        SalesReturn.objects.create(
                        fk_returned_id = odct_item_data[ins_data]['intMasterId'],
                        fk_sales = ins_sales_master,
                        fk_item_id = odct_item_data[ins_data]['intItemId'],
                        int_qty = odct_item_data[ins_data]['intQuantity'],
                        dbl_amount = odct_item_data[ins_data]['dblRate'],
                        dbl_selling_price = odct_item_data[ins_data]['dblAmount'],
                        jsn_imei = odct_item_data[ins_data]['jsonImei'],
                        dat_returned = date.today(),
                        fk_staff = ins_staff,
                        dat_created = datetime.now(),
                        fk_created = request.user.userdetails,
                        int_doc_status = 0,
                        vchr_image = str_img_path,
                        vchr_remark = lst_returned_id.get(str(odct_item_data[ins_data]['intItemId'])).get('strRemarks'),
                        bln_damaged = lst_returned_id.get(str(odct_item_data[ins_data]['intItemId'])).get('blnDamage')
                        )

                # ------------ Customer Delivery Details ---------
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
                # import pdb; pdb.set_trace()
                for ins_mode in dct_payment_data:
                    if dct_payment_data[ins_mode].get('dblAmt') or dct_payment_data[ins_mode].get('intFinanceAmt'):
                        PaymentDetails.objects.create(fk_sales_master = ins_sales_master,
                                                    int_fop = int(ins_mode),
                                                    vchr_card_number = dct_payment_data[ins_mode].get('strCardNo',None),
                                                    vchr_name = dct_payment_data[ins_mode].get('strName',None),
                                                    vchr_finance_schema = dct_payment_data[ins_mode].get('strScheme',None),
                                                    vchr_reff_number = dct_payment_data[ins_mode].get('strRefNo',None),
                                                    dbl_receved_amt = dct_payment_data[ins_mode].get('dblAmt',None),
                                                    dbl_finance_amt = dct_payment_data[ins_mode].get('intFinanceAmt',None),
                                                    dbl_cc_charge = dct_payment_data[ins_mode].get('intCcCharge',None),
                                                    fk_bank_id = dct_payment_data[ins_mode].get('intBankId',None))
                    # PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId')).update(dat_invoice = datetime.now(),fk_invoice = ins_sales_master,int_active = 1)


                # PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId')).update(dat_invoice = datetime.now(),fk_invoice = ins_sales_master,int_active = 1)

                # import pdb;pdb.set_trace()
                lstPaymentData=json.loads(request.data.get("lstPaymentData"))
                if '4' in lstPaymentData and lstPaymentData['4']['bln_receipt']:
                        bln_matching=json.loads(request.data['bln_matching'])

                        if bln_matching:

                                int_total=0.0
                                lstReceipt=lstPaymentData['4']['lstReceipt']
                                flag=False
                                int_total_pre=0
                                # import pdb;
                                # pdb.set_trace()
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

                # ------------------------- BI API ------------------------
                bln_allow = True
                PartialInvoice.objects.filter(pk_bint_id = int(request.data.get('salesRowId'))).update(dat_invoice = datetime.now(),fk_invoice = ins_sales_master,int_active = 1)
                #==============================================================================================================================================================================
                try:
                    # import pdb;pdb.set_trace()
                    int_enq_master_id = PartialInvoice.objects.filter(pk_bint_id = int(request.data.get('salesRowId'))).values().first()['json_data']['int_enq_master_id']
                    url =settings.BI_HOSTNAME + "/mobile/enquiry_invoice_update/"
                    lst_item_id = [x['intItemId'] for x in odct_item_data.values()]
                    dct_item_sup_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_supp_amnt'))
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
                            raise ValueError('Something happened in BI')
                            # return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                    raise ValueError('Something happened in BI')
                # ===============================================================================================================================================================================

                # ---------------- Loyalty Card -------------------
                if bln_allow:
                    loyalty_card(dbl_total_amt,ins_customer,ins_sales_master,request.user)
                # -------------------------------------------------
                return Response({'status':1,'sales_master_id':ins_sales_master.pk_bint_id,'bln_jio':False})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


    def put(self,request):
        try:
            int_partial_id = request.data.get('intPartialId')
            # int_partial_id = 11
            with transaction.atomic():
                int_partail = PartialInvoice.objects.filter(pk_bint_id=int_partial_id)
                # url = "http://192.168.0.174:2121/invoice/update_enquiry/"
                url =settings.BI_HOSTNAME + "/invoice/update_enquiry/"
                res_data = requests.post(url,json={'enquiry_id':int_partail.values('json_data')[0]['json_data']['int_enq_master_id'],'user_code':request.user.username})
                if res_data.json().get('status')=='Success':
                    int_partail.update(int_active=-1)
                    return Response({'status':1,'message':'Successfully Rejected'})
                else:
                    return Response({'status': 'Failed','data':res_data.json().get('message',res_data.json())})

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
            dct_data['str_remarks'] = request.data.get('str_remarks')
            dct_data['dat_created'] = request.data.get('dat_enquiry')
            dct_data['dbl_total_amt'] = request.data.get('dbl_total_amt')
            dct_data['dbl_total_tax'] = request.data.get('dbl_total_tax')
            dct_data['dbl_discount'] = request.data.get('dbl_discount')
            dct_data['int_enq_master_id'] = request.data.get('int_enq_master_id')
            dct_data['vchr_enquiry_num'] = request.data.get('vchr_enquiry_num')
            dct_data['vchr_finance_name'] = request.data.get('vchr_finance_name')
            dct_data['vchr_finance_schema'] = request.data.get('vchr_finance_schema')
            dct_data['dbl_finance_amt'] = request.data.get('dbl_finance_amt')
            dct_data['dbl_emi'] = request.data.get('dbl_emi')
            dct_data['dbl_down_payment'] = request.data.get('dbl_down_payment')
            dct_data['vchr_fin_ordr_num'] = request.data.get('vchr_fin_ordr_num')
            dct_data['lst_items'] = request.data.get('lst_item')
            dct_data['str_cust_name'] = str_cust_name
            dct_data['int_staff_id'] = 0
            dct_data['str_staff_name'] = ''
            dct_data['int_branch_id'] = 0
            dct_data['str_branch'] = ''
            if request.data.get('lst_offers'):
                dct_data['lst_offers']=request.data.get('lst_offers')
            int_status=request.data.get('int_status',1)

            ins_staff = Userdetails.objects.filter(username = request.data.get('vchr_staff_code'),is_active = True).values('user_ptr_id','first_name','last_name').first()
            ins_branch = Branch.objects.filter(vchr_code = request.data.get('vchr_branch_code')).values('pk_bint_id','vchr_name','fk_states_id').first()
            if ins_staff:
                dct_data['int_staff_id'] = ins_staff['user_ptr_id']
                dct_data['str_staff_name'] = ins_staff['first_name']+' '+ins_staff['last_name']
            if ins_branch:
                dct_data['int_branch_id'] = ins_branch['pk_bint_id']
                dct_data['str_branch'] = ins_branch['vchr_name']
            ins_state = None
            if request.data.get('vchr_state_code'):
                ins_state = States.objects.filter(vchr_code = request.data.get('vchr_state_code')).first()
            ins_district = None
            if request.data.get('vchr_district'):
                ins_district = District.objects.filter(vchr_name = request.data.get('vchr_district')).first()
                if not ins_district:
                    ins_district = District.objects.create(vchr_name = request.data.get('vchr_district'),fk_state=ins_state)
                if not ins_state:
                    ins_state = ins_district.fk_state
            ins_location = None
            if request.data.get('vchr_location'):
                ins_location = Location.objects.filter(vchr_name__contains=request.data.get('vchr_location',None),vchr_pin_code=request.data.get('int_pin_code',None)).first()
                if not ins_location:
                    ins_location = Location.objects.create(vchr_name=request.data.get('vchr_location',None),vchr_pin_code=request.data.get('int_pin_code',None),fk_district=ins_district)
                if not ins_district:
                    ins_district = ins_location.fk_district
                if not ins_state:
                    ins_state = ins_district.fk_state
            if not ins_state and ins_branch:
                ins_state =  States.objects.filter(pk_bint_id=ins_branch['fk_states_id']).first()
            ins_customer = CustomerDetails.objects.filter(vchr_name = str_cust_name,int_mobile = int_cust_mob).values('pk_bint_id').first()
            if not ins_customer:
                ins_cust = CustomerDetails.objects.create(
                                                                vchr_name = str_cust_name,
                                                                vchr_email = str_cust_email,
                                                                int_mobile = int_cust_mob,
                                                                vchr_gst_no = request.data.get('vchr_gst_no',None),
                                                                txt_address = request.data.get('txt_address',None),
                                                                fk_location = ins_location,
                                                                fk_state = ins_state
                                                             )

                # ========================================================================================================
                ins_sales_customer = SalesCustomerDetails.objects.create(
                                                        fk_customer_id = ins_cust.pk_bint_id,
                                                        dat_created = datetime.now(),
                                                        fk_created_id = ins_staff['user_ptr_id'],
                                                        vchr_name = str_cust_name,
                                                        vchr_email = str_cust_email,
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
                ins_customer_exist = CustomerDetails.objects.filter(vchr_name = str_cust_name,vchr_email = str_cust_email,int_mobile = int_cust_mob,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)
                ins_cus = CustomerDetails.objects.get(pk_bint_id=dct_data['int_cust_id'])
                if not ins_customer_exist:
                    ins_cus.vchr_email = str_cust_email
                    ins_cus.vchr_gst_no = request.data.get('vchr_gst_no',None)
                    ins_cus.txt_address = request.data.get('txt_address',None)
                    ins_cus.fk_location = ins_location
                    ins_cus.fk_state = ins_state
                    ins_cus.save()

                ins_sales_customer = SalesCustomerDetails.objects.create(
                                                        fk_customer_id = ins_cus.pk_bint_id,
                                                        dat_created = datetime.now(),
                                                        fk_created_id = ins_staff['user_ptr_id'],
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
                                                        vchr_code = ins_cus.vchr_code
                                                    )

                dct_data['int_sales_cust_id'] = ins_sales_customer.pk_bint_id
                # =============================================================================================================
                # dct_data['int_cust_id'] = ins_customer['pk_bint_id']
                # ins_customer = CustomerDetails.objects.filter(vchr_name = str_cust_name,vchr_email = str_cust_email,int_mobile = int_cust_mob,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)
                # if not ins_customer:
                #     CustomerDetails.objects.filter(pk_bint_id=dct_data['int_cust_id']).update(vchr_email = str_cust_email,vchr_gst_no = request.data.get('vchr_gst_no',None), txt_address = request.data.get('txt_address',None), fk_location = ins_location,fk_state = ins_state)
            # -------- Followup ----------
            ins_partial_inv = PartialInvoice.objects.filter(int_enq_master_id = int(request.data.get('int_enq_master_id')), int_active = 0, dat_created__date = request.data.get('dat_enquiry')).first()
            if ins_partial_inv:
                json_data = ins_partial_inv.json_data
                json_data['vchr_finance_name'] = request.data.get('vchr_finance_name', ins_partial_inv.json_data.get('vchr_finance_name'))
                json_data['vchr_finance_schema'] = request.data.get('vchr_finance_schema', ins_partial_inv.json_data.get('vchr_finance_schema'))
                json_data['dbl_finance_amt'] = request.data.get('dbl_finance_amt', ins_partial_inv.json_data.get('dbl_finance_amt'))
                json_data['dbl_emi'] = request.data.get('dbl_emi', ins_partial_inv.json_data.get('dbl_emi'))
                json_data['dbl_down_payment'] = request.data.get('dbl_down_payment', ins_partial_inv.json_data.get('dbl_down_payment'))
                json_data['vchr_fin_ordr_num'] = request.data.get('vchr_fin_ordr_num', ins_partial_inv.json_data.get('vchr_fin_ordr_num'))
                json_data['lst_items'].extend(request.data.get('lst_item'))
                json_data['dbl_total_amt'] += request.data.get('dbl_total_amt')
                json_data['dbl_discount'] += request.data.get('dbl_discount')
                ins_partial_inv.save()
                return Response({'status':'1'})
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
            ins_coupon = Coupon.objects.filter(Q(fk_product_id__in=lst_product)|Q(fk_brand_id__in=lst_brand)|Q(fk_item_category_id__in=lst_item_category)|Q(fk_item_group_id__in=lst_item_group)|Q(fk_item_id__in=lst_item),vchr_coupon_code=str_coupon_code,dat_expiry__gte=date.today()).values('pk_bint_id','int_discount_percentage','bint_max_discount_amt','bint_min_purchase_amt','int_max_usage_no').first()
            if ins_coupon:
                if flt_total>=ins_coupon['bint_min_purchase_amt']:
                    int_used_count = SalesMaster.objects.filter(fk_coupon_id=ins_coupon['pk_bint_id']).aggregate(coupon_count=Count('pk_bint_id'))['coupon_count']
                    if int_used_count>=ins_coupon['int_max_usage_no']:
                        return Response({'status':0,'message':'Coupon Usage Limit Exceeded'})
                    flt_disc = round(flt_total*ins_coupon['int_discount_percentage']/100,2)
                    if flt_disc>ins_coupon['bint_max_discount_amt']:
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
            # import pdb; pdb.set_trace()
            session = Connection()
            vchr_invoice_num = request.data.get('invoiceId')
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
            rst_invoice = session.query(SalesDetailsJS.c.int_qty.label('qty'),SalesDetailsJS.c.dbl_amount.label('item_amount'),SalesDetailsJS.c.dbl_discount.label('item_discount'),\
                            SalesDetailsJS.c.dbl_buyback.label('item_buyback'),SalesDetailsJS.c.json_tax.label('item_tax'),SalesDetailsJS.c.dbl_indirect_discount.label('indirect_discount'),\
                            ItemsSA.vchr_name.label('item'),ItemsSA.vchr_item_code.label('item_code'),\
                            SalesMasterJS.c.dat_created.label('invoice_date'),SalesMasterJS.c.vchr_invoice_num.label('invoice_num'),SalesMasterJS.c.dbl_total_amt.label('total_amount'),\
                            SalesMasterJS.c.dbl_total_tax.label('total_tax'),SalesMasterJS.c.dbl_coupon_amt.label('coupon_amount'),SalesMasterJS.c.dbl_buyback.label('total_buy_back'),\
                            SalesMasterJS.c.dbl_loyalty.label('total_loyalty'),SalesMasterJS.c.dbl_discount.label('total_discount'),CustServiceDeliverySA.vchr_cust_name.label('sh_cust_name'),CustServiceDeliverySA.int_mobile.label('sh_mobile'),\
                            CustServiceDeliverySA.txt_address.label('sh_txt_add'),CustServiceDeliverySA.vchr_landmark.label('sh_landmark'),CustServiceDeliverySA.vchr_gst_no.label('sh_gst'),\
                            SalesCustomerDetailsSA.vchr_name.label('cust_name'),SalesCustomerDetailsSA.vchr_email.label('cust_mail'),SalesCustomerDetailsSA.int_mobile.label('cust_mobile'),\
                            SalesCustomerDetailsSA.txt_address.label('cust_add'),SalesCustomerDetailsSA.vchr_gst_no.label('cust_gst'),\
                            func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('staff'))\
                            .join(SalesMasterJS,SalesMasterJS.c.pk_bint_id==SalesDetailsJS.c.fk_master_id)\
                            .outerjoin(CustServiceDeliverySA,CustServiceDeliverySA.fk_sales_master_id == SalesMasterJS.c.pk_bint_id)\
                            .join(SalesCustomerDetailsSA,SalesCustomerDetailsSA.pk_bint_id == SalesMasterJS.c.fk_customer_id)\
                            .outerjoin(AuthUserSA,AuthUserSA.id==SalesMasterJS.c.fk_staff_id)\
                            .join(ItemsSA,ItemsSA.pk_bint_id == SalesDetailsJS.c.fk_item_id)\
                            .filter(SalesMasterJS.c.pk_bint_id == vchr_invoice_num)

            dct_invoice = {}
            dct_invoice['total'] = 0
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
            rst_state = SalesMaster.objects.filter(pk_bint_id = vchr_invoice_num).values('fk_customer__fk_state__vchr_name','fk_customer__fk_state__vchr_code','fk_branch__fk_states__vchr_name','fk_branch__fk_states__vchr_code')
            if rst_state:
                dct_invoice['cust_state'] = rst_state[0]['fk_customer__fk_state__vchr_name']
                dct_invoice['cust_state_code'] = rst_state[0]['fk_customer__fk_state__vchr_code']
                if not rst_state[0]['fk_customer__fk_state__vchr_name'].upper() == rst_state[0]['fk_branch__fk_states__vchr_name'].upper():
                    dct_invoice['bln_igst'] = True
            for ins_invoice in rst_invoice.all():
                dct_item = {}
                dct_item['item'] = ins_invoice.item
                dct_item['item_code'] = ins_invoice.item_code
                dct_item['qty'] = ins_invoice.qty
                dct_item['amount'] = round(ins_invoice.item_amount,2)
                dct_item['discount'] = round(ins_invoice.item_discount,2)
                dct_item['buyback'] = round(ins_invoice.item_buyback,2)

                if ins_invoice.item_tax:
                    dct_item['sgst'] = 0
                    dct_item['cgst'] = 0
                    dct_item['igst'] = 0
                    total_tax = 0
                    if not dct_invoice['bln_igst']:
                        if ins_invoice.item_tax['dblSGST']:
                            total_tax += ins_invoice.item_tax['dblSGST']
                            flt_sgst = round(((ins_invoice.item_tax['dblSGST']/ins_invoice.qty)/ins_invoice.item_amount)*100,1)
                            dct_item['sgst'] = flt_sgst
                            if flt_sgst not in dct_invoice['tax']['SGST']:
                                dct_invoice['tax']['SGST'][flt_sgst]=round(ins_invoice.item_tax['dblSGST'],2)
                            else:
                                dct_invoice['tax']['SGST'][flt_sgst]+=round(ins_invoice.item_tax['dblSGST'],2)
                        if ins_invoice.item_tax['dblCGST']:
                            total_tax += ins_invoice.item_tax['dblCGST']
                            flt_cgst = round(((ins_invoice.item_tax['dblCGST']/ins_invoice.qty)/ins_invoice.item_amount)*100,1)
                            dct_item['cgst'] = flt_cgst
                            if flt_cgst not in dct_invoice['tax']['CGST']:
                                dct_invoice['tax']['CGST'][flt_cgst]=round(ins_invoice.item_tax['dblCGST'],2)
                            else:
                                dct_invoice['tax']['CGST'][flt_cgst]+=round(ins_invoice.item_tax['dblCGST'],2)
                    else:

                        if ins_invoice.item_tax['dblIGST']:
                            total_tax += ins_invoice.item_tax['dblIGST']
                            flt_igst = round(((ins_invoice.item_tax['dblIGST']/ins_invoice.qty)/ins_invoice.item_amount)*100,1)
                            dct_item['igst'] = flt_igst
                            if flt_igst not in dct_invoice['tax']['IGST']:
                                dct_invoice['tax']['IGST'][flt_igst] = round(ins_invoice.item_tax['dblIGST'],2)
                            else:
                                dct_invoice['tax']['IGST'][flt_igst]+=round(ins_invoice.item_tax['dblIGST'],2)
                # dct_item['tax'] = ins_invoice.item_tax
                dct_item['total'] = round((ins_invoice.item_amount)+total_tax-ins_invoice.item_discount,2)#-ins_invoice.item_buyback
                dct_invoice['total'] += dct_item['total']
                dct_invoice['indirect_discount'] += ins_invoice.indirect_discount if ins_invoice.indirect_discount else 0
                dct_invoice['lst_item'].append(dct_item)

            dct_invoice['bln_dup'] = False
            if request.data.get('blnDuplicate'):
                dct_invoice['bln_dup'] = True
            dct_invoice['invoice_no'] = ins_invoice.invoice_num
            dct_invoice['staff'] = ins_invoice.staff
            dct_invoice['invoice_date'] = datetime.strftime(ins_invoice.invoice_date,'%d-%m-%Y')
            dct_invoice['invoice_time'] = datetime.strftime(ins_invoice.invoice_date,'%I:%M %p')


            dct_invoice['cust_name'] = ins_invoice.cust_name
            dct_invoice['cust_mobile'] = ins_invoice.cust_mobile
            dct_invoice['cust_email'] = ins_invoice.cust_mail
            dct_invoice['cust_add'] = ins_invoice.cust_add
            dct_invoice['cust_gst'] = ins_invoice.cust_gst

            if ins_invoice.sh_cust_name:
                dct_invoice['cust_name'] = ins_invoice.sh_cust_name
                dct_invoice['cust_mobile'] = ins_invoice.sh_mobile
                dct_invoice['cust_email'] = ins_invoice.cust_mail
                dct_invoice['cust_add'] = ins_invoice.sh_txt_add
                dct_invoice['cust_gst'] = ins_invoice.sh_gst
            # dct_invoice['sh_cust_name'] = ins_invoice.sh_cust_name
            # dct_invoice['sh_cust_mobile'] = ins_invoice.sh_mobile
            # dct_invoice['sh_landmark'] = ins_invoice.sh_landmark
            # dct_invoice['sh_cust_add'] = ins_invoice.sh_txt_add
            # dct_invoice['sh_cust_gst'] = ins_invoice.sh_gst

            dct_invoice['amount'] = ins_invoice.total_amount
            dct_invoice['discount'] = round(ins_invoice.total_discount,2)
            dct_invoice['buyback'] = round(ins_invoice.total_buy_back,2)
            if ins_invoice.coupon_amount:
                dct_invoice['coupon'] = round(ins_invoice.coupon_amount,2)
            # dct_invoice['loyalty'] = ins_invoice.sh_gst
            dct_invoice['total_tax'] = ins_invoice.total_tax
            if ins_invoice.total_loyalty:
                dct_invoice['loyalty'] = round(ins_invoice.total_loyalty,2)

            rst_terms = Terms.objects.filter(int_status=1).values('jsn_terms')
            dct_invoice['terms'] = {}
            if rst_terms:
                dct_invoice['terms'] = rst_terms[0]['jsn_terms']

            data = print_invoice(dct_invoice)
            session.close()
            return Response({"status":1,'file':data['file'],'file_name':data['file_name']})

            # return Response({'status':'1','data':'data'})

        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})





def print_invoice(dct_invoice):
    try:
        ins_tool_set =Tools.objects.filter(vchr_tool_code = 'MYG_CARE_NUMBER').values('jsn_data').first()
        str_mygcare_num ='1800 123 2006'
        if ins_tool_set:
            str_mygcare_num = str(ins_tool_set['jsn_data'])

        # import pdb; pdb.set_trace()

        if 0:
            html_data = """<!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Invoice Format</title>
    	<style>
    		      body{
    			        font-family:Segoe, "Segoe UI", "DejaVu Sans", "Trebuchet MS", Verdana, "sans-serif";
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
    	table, th, td {
    				    border: 1px solid #cecdcd;
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
                        text-align:center;
    					color:  #e06a2b;

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
						<p> Maniyattukudi Asfa Building, Mavoor Rd, Arayidathupalam, Kozhikode, Kerala</p>
						</div>
					 </div>

    				   <div style="width:50%;float:left;">

    					   <div style="width:15%;float:left">
    					   <p><span style="font-weight: 600;">PH : </span></p>
    					   </div>
    					   <div style="width:83%;float: right">
    						<p>  0487 234566</p>
    					   </div>

				   </div>
    				     <div style="width:50%;float:right;">

    						 <div style="width:25%;float:left">
    					   <p><span style="font-weight: 600;">MOB : </span></p>
    					   </div>
    					   <div style="width:73%;float: right">
    						<p>   1234567890</p>
    					   </div>
					</div>
                <div style="width:50%;float:left;">
					   <div style="width:45%;float:left">
					  <p><span style="font-weight: 600;">MYG CARE : </span></p>
					   </div>
					   <div style="width:54%;float: right">
						<p> """ +str_mygcare_num+"""</p>
					   </div>

				   </div>
    				     <div style="width:50%;float:right;">
    						<div style="width:35%;float:left">
    					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
    					   </div>
    					   <div style="width:65%;float: right">
    						<p>    contact@myg.in</p>
    					   </div>
						 </div>
    				   <div style="width:100%;float:left;">
					    <p><span style="font-weight: 600;">GSTN : </span>23AAAAA0000A1Z9</p>
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
    				<div class="section1">



    				</div>
    				<div class="section2">

    					<div style="width:40%;float:left;"><p>Invoice No :</p></div>
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
    						     <div class="clear"></div>

    						     <div style="width:30%;float: left;"><h6>ADDRESS</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_add']+"""</p></div>
    						     <div class="clear"></div>



    						     <div style="width:30%;float: left;"><h6>CITY PIN CODE</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+"""680307"""+"""</p></div>
    						     <div class="clear"></div>

    						     <div style="width:30%;float: left;"><h6>MOB NO</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+str(dct_invoice['cust_mobile'])+"""</p></div>
    						     <div class="clear"></div>

    						     <div style="width:30%;float: left;"><h6>GSTN NO</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+str(dct_invoice['cust_gst'])+"""</p></div>
    						     <div class="clear"></div>

    						     <div style="width:30%;float: left;"><h6>STATE</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_state'].title()+"""/"""+dct_invoice['cust_state_code']+"""</p></div>
    						     <div class="clear"></div>

    						</div>
    				    </div>

    				       <div class="section4">
    							 <div style="width:100%;float: left;"><h6 style="border-bottom: 1px solid #c7c2c2;padding-bottom: 6px;color: green;">SHIPPED TO</h6></div>

    						     <div style="width:30%;float: left;"><h6>Name</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+dct_invoice['sh_cust_name'].title()+"""</p></div>
    						     <div class="clear"></div>

    						     <div style="width:30%;float: left;"><h6>Address</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+dct_invoice['sh_cust_add']+"""</p></div>
    						     <div class="clear"></div>

    						     <div style="width:30%;float: left;"><h6>Landmark</h6></div>
    						     <div style="width:70%;float:right;"><p>: """+dct_invoice['sh_landmark']+"""</p></div>
    						     <div class="clear"></div>


    						     <div style="width:30%;float: left;"><h6>CITY PIN CODE</h6></div>
    						     <div style="width:70%;float:right;"><p>: 680307</p></div>
    						     <div class="clear"></div>

    						    <div style="width:30%;float: left;"><h6>MOB No</h6></div>
    						    <div style="width:70%;float:right;"><p>: """+str(dct_invoice['sh_cust_mobile'])+"""</p></div>
    						    <div class="clear"></div>

    						    <div style="width:30%;float: left;"><h6>GSTN No</h6></div>
    						    <div style="width:70%;float:right;"><p>: """+str(dct_invoice['sh_cust_gst'])+"""</p></div>
    						    <div class="clear"></div>

    						    <div style="width:30%;float: left;"><h6>State</h6></div>
    						    <div style="width:70%;float:right;"><p>: """+dct_invoice['cust_state'].title()+"""/"""+dct_invoice['cust_state_code']+"""</p></div>
    						    <div class="clear"></div>

    				    </div>
                     </div>
    			             <div class="clear"></div>
    			              <div class="table-responsive">
    							  <table style="width:100%">

    								  <tr style="background-color: #e06a2b;color: white;">
    									<th>SLNO</th>
    									<th>ITEM DESCRIPTION/DETAIL</th>
    									<th>HSN/SAC</th>
    									<th>QTY</th>
    									<th>RATE</th>
    								    <th>DISCOUNT</th>"""
            if dct_invoice['bln_igst']:
                html_data +="""<th>IGST %</th>"""
            else:
                html_data +="""
    									<th>SGST %</th>
    									<th>CGST %</th>"""
            html_data +="""<th>GROSS AMOUNT</th>
    								  </tr>"""
            int_index = 1
            for str_item in dct_invoice['lst_item']:
                html_data +="""<tr>		<td>"""+str(int_index)+"""</td>
    									<td style="text-align:left">"""+str_item['item']+"""</td>
    									<td style="text-align:right">"""+str(str_item['item_code'])+"""</td>
    									<td style="text-align:right">"""+str(str_item['qty'])+"""</td>
    									<td style="text-align:right">"""+str(str_item['amount'])+"""</td>
    									<td style="text-align:right">"""+str(str_item['discount'])+"""</td>"""
                if dct_invoice['bln_igst']:
                    html_data +="""<td style="text-align:right">"""+str(str_item['igst'])+"""</td>"""
                else:
                    html_data +="""	<td style="text-align:right">"""+str(str_item['sgst'])+"""</td>
    									<td style="text-align:right">"""+str(str_item['cgst'])+"""</td>"""
                html_data +="""<td style="text-align:right">"""+str(str_item['total'])+"""</td>
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
                            html_data+="""<div style="width:50%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
            						        <div style="width:50%;float:right;"><p>"""+str(dct_invoice['tax'][dct_tax][str_tax])+"""</p></div>
            						        <div class="clear"></div>"""
                    else:
                        if dct_tax.upper() in ['CGST','SGST']:
                            html_data+="""<div style="width:50%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+dct_tax+""" """+str(str_tax)+"""% :</p></div>
            						        <div style="width:50%;float:right;"><p>"""+str(dct_invoice['tax'][dct_tax][str_tax])+"""</p></div>
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
            # import pdb; pdb.set_trace()
            html_data+="""<div style="padding-bottom: 12px;background-color: #ffede3;margin-top: 12px;padding-right: 10px;">
    									<div style="width:50%;float: left;"><p>SUB TOTAL :</p></div>
    									<div style="width:50%;float:right;"><p> """+str(round(dct_invoice['total'],2))+"""</p></div>
    									<div class="clear"></div>


    									<div style="width:50%;float: left;"><p>COUPON AMOUNT :</p></div>
    									<div style="width:50%;float:right;"><p> """+str(dct_invoice['coupon'])+"""</p></div>
    									<div class="clear"></div>


    									<div style="width:50%;float: left;"><p>LOYALTY AMOUNT :</p></div>
    									<div style="width:50%;float:right;"><p> """+str(dct_invoice['loyalty'])+"""</p></div>
    									<div class="clear"></div>


    									<div style="width:50%;float: left;"><p>BUYBACK AMOUNT :</p></div>
    									<div style="width:50%;float:right;"><p> """+str(dct_invoice['buyback'])+"""</p></div>
    									<div class="clear"></div>

    									<div style="width:50%;float: left;"><p style="margin-top: 5px;"><b>TOTAL : </b></p></div>
    									<div style="width:50%;float:right;"><p style="margin-top: 4px;"><b> """+str(round(dct_invoice['total']-dct_invoice['buyback']-dct_invoice['coupon']-dct_invoice['loyalty'],2))+""" </b></p></div>
    									<div class="clear"></div>
    							  </div>
    							   </div>
    						 </div>
    		               </div>
    			           <div class="box2" style="border-top: 1px solid #c7c2c2;">

    						   <p style="font-weight: 600;">TERMS / CONDITIONS:</p>

    							<ul style="list-style-type:disc;">"""
            for index in range(1,len(dct_invoice['terms'])+1):
                html_data+="""<li>"""+dct_invoice['terms'][str(index)]+"""</li>"""

            html_data +="""</ul>
                            </div>
    			          </div>
    		        </div>
    	     </div>
    </body>
    </html> """
        else:
            html_data2 = """<!doctype html>
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
    	table, th, td {
    				    border: 1px solid #cecdcd;
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
						<p> Maniyattukudi Asfa Building, Mavoor Rd, Arayidathupalam, Kozhikode, Kerala</p>
						</div>
					 </div>

    				   <div style="width:50%;float:left;">

    					   <div style="width:15%;float:left">
    					   <p><span style="font-weight: 600;">PH : </span></p>
    					   </div>
    					   <div style="width:83%;float: right">
    						<p>  0487 234566</p>
    					   </div>

				   </div>
    				     <div style="width:50%;float:right;">

    						 <div style="width:25%;float:left">
    					   <p><span style="font-weight: 600;">MOB : </span></p>
    					   </div>
    					   <div style="width:73%;float: right">
    						<p>   1234567890</p>
    					   </div>
					</div>
                <div style="width:50%;float:left;">
					   <div style="width:45%;float:left">
					  <p><span style="font-weight: 600;">MYG CARE : </span></p>
					   </div>
					   <div style="width:54%;float: right">
						<p>   1800 123 2006</p>
					   </div>

				   </div>
    				     <div style="width:50%;float:right;">
    						<div style="width:35%;float:left">
    					     <p><span style="font-weight: 600;">EMAIL ID : </span></p>
    					   </div>
    					   <div style="width:65%;float: right">
    						<p>    contact@myg.in</p>
    					   </div>
						 </div>
    				   <div style="width:100%;float:left;">
					    <p><span style="font-weight: 600;">GSTN : </span>23AAAAA0000A1Z9</p>
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
    				<div class="section2">

    					<div style="width:50%;float:left;"><p>Invoice No :</p></div>
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
    							  <table style="width:100%">

    								  <tr style="background-color: #e06a2b;color: white;">
    									<th>SLNO</th>
    									<th>ITEM DESCRIPTION/DETAIL</th>
    									<th>HSN/SAC</th>
    									<th>QTY</th>
    									<th>RATE</th>
    									<th>DISCOUNT</th>"""
            if dct_invoice['bln_igst']:
                html_data2 +="""<th>IGST %</th>"""
            else:
                html_data2 +="""<th>SGST %</th>
    							<th>CGST %</th>"""
            html_data2 +="""<th>GROSS AMOUNT</th>
    								  </tr>"""
            int_index = 1
            for str_item in dct_invoice['lst_item']:
                html_data2+="""<tr>		<td>"""+str(int_index)+"""</td>
    									<td style="text-align:left">"""+str_item['item']+"""</td>
    									<td style="text-align:right">"""+str_item['item_code']+"""</td>
    									<td style="text-align:right">"""+str(str_item['qty'])+"""</td>
    									<td style="text-align:right">"""+str(str_item['amount'])+"""</td>
    									<td style="text-align:right">"""+str(str_item['discount'])+"""</td>"""
                if dct_invoice['bln_igst']:
                    html_data2 +="""<td style="text-align:right">"""+str(str_item['igst'])+"""</th>"""
                else:
                    html_data2 +="""	<td style="text-align:right">"""+str(str_item['sgst'])+"""</td>
    									<td style="text-align:right">"""+str(str_item['cgst'])+"""</td>"""
                html_data2 +="""<td style="text-align:right">"""+str(str_item['total'])+"""</td>
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


    									<div style="width:50%;float: left;"><p>LOYALTY AMOUNT :</p></div>
    									<div style="width:50%;float:right;"><p> """+str(dct_invoice['loyalty'])+"""</p></div>
    									<div class="clear"></div>


    									<div style="width:50%;float: left;"><p>BUYBACK AMOUNT :</p></div>
    									<div style="width:50%;float:right;"><p> """+str(dct_invoice['buyback'])+"""</p></div>
    									<div class="clear"></div>"""
            if dct_invoice['indirect_discount']:
                html_data2+="""<div style="width:50%;float: left;"><p>VOUCHER AMOUNT:</p></div>
    									<div style="width:50%;float:right;"><p> """+str(round(dct_invoice['indirect_discount'],2))+"""</p></div>
    									<div class="clear"></div>"""

            html_data2+="""	<div style="width:50%;float: left;"><p style="margin-top: 5px;"><b>TOTAL : </b></p></div>
    									<div style="width:50%;float:right;"><p style="margin-top: 4px;"><b> """+str(round(dct_invoice['total']-dct_invoice['buyback']-dct_invoice['coupon']-dct_invoice['loyalty']-dct_invoice['indirect_discount'],2))+""" </b></p></div>
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

            html_data2 +="""</ul>
                            </div>"""
            # if dct_invoice['bln_dup']:
            #     html_data2 +="""<div><p style="color:red;">Duplicate</p></div>"""
            html_data2+="""</div>
    		        </div>
    	     </div>
    </body>
    </html> """


        # import pdb; pdb.set_trace()
        file_path = settings.MEDIA_ROOT
        # str_base_path = settings.MEDIA_ROOT+'/schemes'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        str_file_name = 'invoice-'+dct_invoice['invoice_no']+'-'+dct_invoice['invoice_date']+'.pdf'
        filename =  file_path+'/'+str_file_name
        options = {'margin-top': '10.00mm',
                   'margin-right': '10.00mm',
                   'margin-bottom': '10.00mm',
                   'margin-left': '10.00mm',
                   'dpi':400}
        # if dct_invoice['sh_cust_name']:
        #     pdfkit.from_string(html_data,filename,options=options)
        # else:
            # filename =  file_path+'/invoice-'+dct_invoice['invoice_no']+dct_invoice['invoice_date']+'.pdf'
        pdfkit.from_string(html_data2,filename,options=options)

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
        return file_details
    except Exception as e:
        raise


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
            # import pdb; pdb.set_trace()

            if request.data.get('blnReturn'):
                rst_invoice = session.query(SalesMasterSA.pk_bint_id.label('int_id'),SalesDetailsSA.int_sales_status.label('int_sales_status'),SalesMasterSA.dat_invoice.label('dat_invoice'),SalesReturnSA.vchr_doc_code.label('str_inv_num'),SalesMasterSA.dat_created.label('dat_created'),BranchSA.vchr_name.label('str_branch_name'),\
                                SalesCustomerDetailsSA.vchr_name.label('str_cust_name'),SalesCustomerDetailsSA.int_mobile.label('int_mobile'),func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('str_staff_name'),ProductsSA.vchr_name.label('str_product_name'),func.coalesce(False).label('bln_jio_invoice'))\
                                .join(SalesDetailsSA, SalesDetailsSA.fk_master_id == SalesMasterSA.pk_bint_id)\
                                .join(BranchSA, BranchSA.pk_bint_id == SalesMasterSA.fk_branch_id)\
                                .join(SalesCustomerDetailsSA, SalesCustomerDetailsSA.pk_bint_id == SalesMasterSA.fk_customer_id)\
                                .join(AuthUserSA, AuthUserSA.id == SalesMasterSA.fk_staff_id)\
                                .join(ItemsSA, ItemsSA.pk_bint_id == SalesDetailsSA.fk_item_id)\
                                .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                                .join(SalesReturnSA,SalesReturnSA.fk_sales_id == SalesMasterSA.pk_bint_id)\
                                .filter(cast(SalesMasterSA.dat_created,Date) >= dat_from,cast(SalesMasterSA.dat_created,Date) <= dat_to,SalesDetailsSA.int_sales_status==0)
            else:
                rst_invoice = session.query(SalesMasterSA.pk_bint_id.label('int_id'),SalesDetailsSA.int_sales_status.label('int_sales_status'),SalesMasterSA.dat_invoice.label('dat_invoice'),SalesMasterSA.vchr_invoice_num.label('str_inv_num'),SalesMasterSA.dat_created.label('dat_created'),BranchSA.vchr_name.label('str_branch_name'),\
                                SalesCustomerDetailsSA.vchr_name.label('str_cust_name'),SalesCustomerDetailsSA.int_mobile.label('int_mobile'),func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('str_staff_name'),ProductsSA.vchr_name.label('str_product_name'),func.coalesce(False).label('bln_jio_invoice'))\
                                .join(SalesDetailsSA, SalesDetailsSA.fk_master_id == SalesMasterSA.pk_bint_id)\
                                .join(BranchSA, BranchSA.pk_bint_id == SalesMasterSA.fk_branch_id)\
                                .join(SalesCustomerDetailsSA, SalesCustomerDetailsSA.pk_bint_id == SalesMasterSA.fk_customer_id)\
                                .join(AuthUserSA, AuthUserSA.id == SalesMasterSA.fk_staff_id)\
                                .join(ItemsSA, ItemsSA.pk_bint_id == SalesDetailsSA.fk_item_id)\
                                .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                                .filter(cast(SalesMasterSA.dat_created,Date) >= dat_from,cast(SalesMasterSA.dat_created,Date) <= dat_to)

            rst_jio_invoice = session.query(SalesMasterJioSa.pk_bint_id.label('int_id'),literal_column('100').label('int_sales_status'),SalesMasterJioSa.dat_invoice.label('dat_invoice'),SalesMasterJioSa.vchr_invoice_num.label('str_inv_num'),SalesMasterJioSa.dat_created.label('dat_created'),BranchSA.vchr_name.label('str_branch_name'),\
                            SalesCustomerDetailsSA.vchr_name.label('str_cust_name'),SalesCustomerDetailsSA.int_mobile.label('int_mobile'),func.concat(AuthUserSA.first_name+' '+AuthUserSA.last_name).label('str_staff_name'),ProductsSA.vchr_name.label('str_product_name'),func.coalesce(True).label('bln_jio_invoice'))\
                            .join(BranchSA, BranchSA.pk_bint_id == SalesMasterJioSa.fk_branch_id)\
                            .join(SalesCustomerDetailsSA, SalesCustomerDetailsSA.pk_bint_id == SalesMasterJioSa.fk_customer_id)\
                            .join(AuthUserSA, AuthUserSA.id == SalesMasterJioSa.fk_staff_id)\
                            .join(ItemsSA, ItemsSA.pk_bint_id == SalesMasterJioSa.fk_item_id)\
                            .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                            .filter(cast(SalesMasterJioSa.dat_created,Date) >= dat_from,cast(SalesMasterJioSa.dat_created,Date) <= dat_to)
            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                pass
            else:
                rst_invoice = rst_invoice.filter(SalesMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
                rst_jio_invoice = rst_jio_invoice.filter(SalesMasterJioSa.fk_branch_id == request.user.userdetails.fk_branch_id)

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

            rst_data = rst_invoice.union_all(rst_jio_invoice).order_by(desc('dat_created')).all()
            lst_invoice = []
            for ins_data in rst_data:
                dct_data = {}
                dct_data['fk_master__fk_customer__int_mobile'] = ins_data.int_mobile
                dct_data['fk_master__fk_customer__vchr_name'] = ins_data.str_cust_name
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
                lst_master = SalesMasterJio.objects.filter(pk_bint_id = int_id).values('dat_invoice','fk_branch__vchr_name','fk_staff__first_name','fk_staff__last_name','fk_customer__vchr_name','fk_customer__vchr_email','fk_customer__int_mobile','vchr_remarks')
                rst_data = session.query(SalesMasterJioJS.c.int_qty.label('int_qty'), SalesMasterJioJS.c.dbl_total_amt.label('dbl_amount'), SalesMasterJioJS.c.dbl_total_amt.label('dbl_selling_price'), literal_column("0.0").label('dbl_tax'),\
                                        literal_column("0.0").label('dbl_discount'), literal_column("0.0").label('dbl_buyback'), literal_column("4").label('int_sales_status'), literal_column("NULL").label('json_tax'),\
                                        SalesMasterJioJS.c.json_imei.label('json_imei'), ItemsSA.pk_bint_id.label('int_item_id'),ItemsSA.vchr_item_code.label('vchr_item_code'), ItemsSA.vchr_name.label('vchr_item_name'), BrandSA.vchr_name.label('vchr_brand_name'),\
                                        ProductsSA.vchr_name.label('vchr_product_name'), literal_column("NULL").label('vchr_image'), literal_column("NULL").label('vchr_remark'), literal_column("NULL").label('bln_damaged'))\
                                        .join(ItemsSA, ItemsSA.pk_bint_id == SalesMasterJioJS.c.fk_item_id)\
                                        .join(BrandSA, BrandSA.pk_bint_id == ItemsSA.fk_brand_id)\
                                        .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                                        .filter(SalesMasterJioJS.c.pk_bint_id == int_id)

            else:
                lst_master = SalesMaster.objects.filter(pk_bint_id = int_id).values('dat_invoice','fk_branch__vchr_name','fk_staff__first_name','fk_staff__last_name','fk_customer__vchr_name','fk_customer__vchr_email','fk_customer__int_mobile','vchr_remarks')
                rst_data = session.query(SalesDetailsJS.c.int_qty.label('int_qty'), SalesDetailsJS.c.dbl_amount.label('dbl_amount'), SalesDetailsJS.c.dbl_selling_price.label('dbl_selling_price'), SalesDetailsJS.c.dbl_tax.label('dbl_tax'),\
                                        SalesDetailsJS.c.dbl_discount.label('dbl_discount'), SalesDetailsJS.c.dbl_buyback.label('dbl_buyback'), SalesDetailsJS.c.int_sales_status.label('int_sales_status'), SalesDetailsJS.c.json_tax.label('json_tax'),\
                                        SalesDetailsJS.c.json_imei.label('json_imei'), ItemsSA.pk_bint_id.label('int_item_id'),ItemsSA.vchr_item_code.label('vchr_item_code'), ItemsSA.vchr_name.label('vchr_item_name'), BrandSA.vchr_name.label('vchr_brand_name'),PartialInvoiceJS.c.json_data.label('dct_invoice'),\
                                        ProductsSA.vchr_name.label('vchr_product_name'), case([((SalesReturnSA.fk_item_id == ItemsSA.pk_bint_id), SalesReturnSA.vchr_image)], else_=literal_column("NULL")).label('vchr_image'),\
                                        case([((SalesReturnSA.fk_item_id == ItemsSA.pk_bint_id), SalesReturnSA.vchr_remark)], else_=literal_column("NULL")).label('vchr_remark'), case([((SalesReturnSA.fk_item_id == ItemsSA.pk_bint_id), SalesReturnSA.bln_damaged)], else_=literal_column("NULL")).label('bln_damaged'))\
                                        .join(SalesMasterSA, SalesMasterSA.pk_bint_id == SalesDetailsJS.c.fk_master_id)\
                                        .join(ItemsSA, ItemsSA.pk_bint_id == SalesDetailsJS.c.fk_item_id)\
                                        .join(BrandSA, BrandSA.pk_bint_id == ItemsSA.fk_brand_id)\
                                        .join(ProductsSA, ProductsSA.pk_bint_id == ItemsSA.fk_product_id)\
                                        .join(PartialInvoiceJS, PartialInvoiceJS.c.fk_invoice_id == SalesMasterSA.pk_bint_id)\
                                        .outerjoin(SalesReturnSA, SalesReturnSA.fk_sales_id == SalesMasterSA.pk_bint_id)\
                                        .filter(SalesMasterSA.pk_bint_id == int_id)

                 # 0. Finance, 1. Cash, 2. Debit Card, 3. Credit Card 4. Receipt
                rst_payment = PaymentDetails.objects.filter(fk_sales_master_id = int_id)\
                                                    .annotate(payment_type=Case(When(int_fop=0, then=Value('Finance')),When(int_fop=1, then=Value('Cash')), When(int_fop=2, then=Value('Debit Card')),When(int_fop=3, then=Value('Credit Card')),When(int_fop=4, then=Value('Receipt')),default=Value('Other'),output_field=CharField(),),)\
                                                    .values('dat_created_at','payment_type','dbl_receved_amt','vchr_reff_number')

            if not rst_data.all():
                session.close()
                return Response({'status':0,'message':'No Data'})
            lst_details = []
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
                dct_data['dblBuyBack'] = ins_data.dbl_buyback
                dct_data['jsonTax'] = {"dblCGST": 0, "dblIGST": 0, "dblSGST": 0}
                if ins_data.json_tax:
                    dct_data['jsonTax'] = ins_data.json_tax
                dct_data['strImei'] = ''
                for int_imei in ins_data.json_imei:
                    dct_data['strImei'] += str(int_imei) + ','
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
            return Response({'status':1,'master':lst_master,'details':lst_details,'lst_payment':rst_payment})
        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})



class InvoiceListPrintApi(APIView):
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            lst_imei = [request.data.get('imei')]
            int_customer = request.data.get('intCustomer')
            str_invoice_no = request.data.get('invoiceNo')
            if request.data.get('imei'):
                lst_imei = [request.data.get('imei')]
                ins_sales_details = SalesDetails.objects.filter(json_imei__contains=lst_imei,int_sales_status__in =[1,2,3,4]).values_list('fk_master_id',flat=True).distinct()
            elif request.data.get('datFrom'):
                dat_from = datetime.strptime(request.data.get('datFrom'),'%Y-%m-%d').date()
                dat_to = datetime.strptime(request.data.get('datTo'),'%Y-%m-%d').date()
                ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id=int_customer,fk_master__dat_invoice__range=(dat_from,dat_to),int_sales_status__in =[1,2,3,4]).values_list('fk_master_id',flat=True).distinct()

            elif str_invoice_no :
                 ins_sales_details = SalesDetails.objects.filter(fk_master__vchr_invoice_num = str_invoice_no,int_sales_status__in =[1,2,3,4]).values_list('fk_master_id',flat=True).distinct()


            else:
                ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id=int_customer,int_sales_status__in =[1,2,3,4]).values_list('fk_master_id',flat=True).distinct()
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

                ins_document = Document.objects.select_for_update().get(vchr_module_name = 'DELIVERY CHALLAN',vchr_short_code = 'DC')
                str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                ins_document.int_number = ins_document.int_number+1
                ins_document.save()

                ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId')).values().first()

                ins_branch = Branch.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_branch_id']).first()
                ins_staff = Userdetails.objects.filter(user_ptr_id = ins_partial_inv['json_data']['int_staff_id']).first()

                # ins_customer = CustomerDetails.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_cust_id']).first()
                ins_sales_customer = SalesCustomerDetails.objects.filter(pk_bint_id = request.data.get('intSalesCustId')).first()

                if request.user.userdetails.fk_branch.fk_states_id != ins_sales_customer.fk_state_id:
                # if request.user.userdetails.fk_branch.fk_states_id != ins_customer.fk_state_id:
                    bln_igst = True
                odct_item_data = OrderedDict()
                dbl_total_amt = 0
                dbl_total_tax = 0
                json_total_tax = {'dblIGST':0,'dblCGST':0,'dblSGST':0}
                dbl_total_rate = 0
                dbl_total_buyback = 0
                dbl_total_discount = 0

                for dct_item in dct_item_data:
                    # dct_item['status'] = 1
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
                            odct_item_data[str_temp]['dblCGST'] += dct_item['dblCGST']
                            odct_item_data[str_temp]['dblSGST'] += dct_item['dblSGST']
                            dbl_total_tax += dct_item['dblCGST'] + dct_item['dblSGST']
                            json_total_tax['dblCGST'] += dct_item['dblCGST']
                            json_total_tax['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['jsonTax']['dblCGST'] += dct_item['dblCGST']
                            odct_item_data[str_temp]['jsonTax']['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['dblTax'] += dct_item['dblCGST']+dct_item['dblSGST']
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
                        odct_item_data[str_temp]['dblTax'] = 0
                        odct_item_data[str_temp]['dblIndirectDis'] = dct_item.get('dblIndirectDis')
                        # import pdb; pdb.set_trace()
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
                            odct_item_data[str_temp]['dblCGST'] = dct_item['dblCGST']
                            odct_item_data[str_temp]['dblSGST'] = dct_item['dblSGST']
                            dbl_total_tax += dct_item['dblCGST'] + dct_item['dblSGST']
                            json_total_tax['dblCGST'] += dct_item['dblCGST']
                            json_total_tax['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['jsonTax']['dblCGST'] += dct_item['dblCGST']
                            odct_item_data[str_temp]['jsonTax']['dblSGST'] += dct_item['dblSGST']
                            odct_item_data[str_temp]['dblTax'] += dct_item['dblCGST'] + dct_item['dblSGST']
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
                                if ins_br_stk_imei:
                                    lst_imei = ins_br_stk_imei.jsn_imei['imei']
                                    lst_imei.remove(vchr_stk_imei)
                                    int_qty = ins_br_stock.int_qty-1
                                    BranchStockImeiDetails.objects.filter(Q(jsn_imei__contains={'imei':[str(vchr_stk_imei)]}),fk_details=ins_br_stock).update(jsn_imei={'imei':lst_imei},int_qty=int_qty)

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
                                                          fk_financial_year=FinancialYear.objects.filter(dat_start__lte = date.today(),dat_end__gte = date.today()).first(),
                                                          int_fop = int(ins_mode),
                                                          vchr_card_number = dct_payment_data[ins_mode].get('strCardNo',None),
                                                          vchr_name = dct_payment_data[ins_mode].get('strName',None),
                                                          vchr_reff_number = dct_payment_data[ins_mode].get('strRefNo',None),
                                                          dbl_receved_amt = dct_payment_data[ins_mode].get('dblAmt',None),
                                                          fk_bank_id=dct_payment_data[ins_mode].get('intBankId',None))

                            ins_sales_jio.save()
                        break
                    #==========sales return============
                    # import pdb; pdb.set_trace()
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
                    dct_item_sup_amnt =  dict(PriceList.objects.filter(fk_item_id__in = lst_item_id).values_list('fk_item_id','dbl_supp_amnt'))
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
            # import pdb; pdb.set_trace()
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
    #         # import pdb; pdb.set_trace()
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
    #                 dbl_amt = (dbl_rate+dbl_buyback+dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))/100)
    #                 dct_item['dblIGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))
    #                 dct_item['dblIGST'] = dbl_amt*(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0)/100)
    #                 dbl_amt = (dbl_rate+dbl_buyback+dbl_discount)/((100+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0)+ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))/100)
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
