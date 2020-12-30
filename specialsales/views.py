from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from datetime import datetime,time,date,timedelta
from django.conf import settings
from django.db.models.functions import Concat
# from django.db.models import Q, Value, F
import requests
import sys
from POS import ins_logger
from django.db import transaction
import json
from django.db.models import Q, Value, BooleanField, Case, When,IntegerField,CharField,Sum,F
from collections import OrderedDict
from transaction.views import create_invoice_posting_data,create_posting_data





from branch.models import Branch
from sap_api.models import SapApiTrack
from tool_settings.models import Tools
from invoice.views import tools_keys
from customer.models import CustomerDetails,SalesCustomerDetails
from userdetails.models import Userdetails,Financiers
from receipt.models import Receipt,ReceiptInvoiceMatching
from item_category.models import TaxMaster,Item
from purchase.models import GrnDetails
from branch_stock.models import BranchStockMaster,BranchStockDetails
from exchange_sales.models import ExchangeStock
from accounts_map.models import AccountsMap
from purchase.models import Document
from pricelist.models import PriceList
from company.models import FinancialYear,Company
from branch_stock.models import BranchStockDetails, BranchStockImeiDetails,BranchStockMaster
from invoice.models import PartialInvoice, SalesMaster, SalesDetails, CustServiceDelivery, LoyaltyCardInvoice, FinanceDetails,PaymentDetails,SalesMasterJio,Bank,TheftDetails,Depreciation,FinanceScheme



"""
PartialInvoice


"""

class addInvoice(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            if request.data.get('salesRowId'):
                    if PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId'),fk_invoice_id__isnull=False).exists():
                        return Response({'status':0,'message':'Already sold'})
                        # pass
            with transaction.atomic():
                inst_partial_validation=PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId'))
                inst_partial_validation.update(fk_invoice_id=1)
                json_deduction = request.data.get('json_deductions')
                dct_deduction={}
                if json_deduction:
                    json_deduction = json.loads(request.data.get('json_deductions'))

                    for ins_deduction in json_deduction:
                        rst_deduction = AccountsMap.objects.filter(vchr_module_name='DEDUCTIONS',vchr_category=ins_deduction['name'],int_status=0).values('pk_bint_id')
                        if rst_deduction:
                            dct_deduction[rst_deduction[0]['pk_bint_id']] = ins_deduction['value']
                dct_item_data = json.loads(request.data.get('dctTableData'))
                # lst_returned_id  = json.loads(request.data.get('dctReturnId'))
                # int_redeem_point = json.loads(request.data.get('intRedeemPoint'))
                dbl_rounding_off = json.loads(request.data.get('intRounding','0.0'))
                str_remarks = request.data.get('strRemarks',None)
                bln_igst = False


                 # LG
                """~~~~~~~~~~~~~~~~~~~~Checking Item is available or not~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
                lst_for_comparison = []
                lst_data_exists = []
                for data in dct_item_data:
                    """~~~~~~~~~~~~~~~~~~~~To avoid smart choice and return from imei available check~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
                    if not data['intStatus'] in [0,2,3] and (data.get('vchr_product_name') not in ['RECHARGE','SIM','SERVICE','SERVICES']):
                        if data.get('strImei'):
                            lst_data_exists.append(data['strImei'][0] if type(data['strImei']) == list else data['strImei'] )
                    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

                if lst_data_exists:
                    rst_imei_exist_data = BranchStockDetails.objects.filter(jsn_imei_avail__imei__has_any_keys = lst_data_exists, fk_master_id__fk_branch_id=request.user.userdetails.fk_branch_id).values('jsn_imei_avail','int_qty')
                    rst_imei_exchange_data = ExchangeStock.objects.filter(jsn_avail__has_any_keys = lst_data_exists, fk_branch_id=request.user.userdetails.fk_branch_id).annotate(jsn_imei_avail=F('jsn_avail'),int_qty=F('int_avail')).values('jsn_imei_avail','int_qty')

                    # rst_exist_data = BranchStockDetails.objects.filter(Q(jsn_imei_avail__imei__has_any_keys = lst_data_exists) | Q(jsn_batch_no__batch__has_any_keys = lst_data_exists ), fk_master_id__fk_branch_id=request.user.userdetails.fk_branch_id).values('jsn_imei_avail','jsn_batch_no','int_qty')
                    rst_batch_no_exist_data = BranchStockDetails.objects.filter(jsn_batch_no__batch__has_any_keys = lst_data_exists , fk_master_id__fk_branch_id=request.user.userdetails.fk_branch_id).values('jsn_batch_no').annotate(sum_qty = Sum('int_qty'))
                    for data in rst_imei_exist_data:
                        for imei in data['jsn_imei_avail']['imei']:
                            if imei in lst_data_exists:
                                lst_for_comparison.append(imei)


                    for data in rst_imei_exchange_data:
                        if data['jsn_imei_avail'][0] in lst_data_exists:
                            lst_for_comparison.append(data['jsn_imei_avail'][0])

                    for data in rst_batch_no_exist_data:
                        for batch in data['jsn_batch_no']['batch']:
                            if batch in lst_data_exists:
                                if  lst_data_exists.count(batch) <= data['sum_qty']:
                                    lst_for_comparison.append(batch)
                                else:

                                    inst_partial_validation.update(fk_invoice_id=None)

                                    return Response({'status':0,'message':'The Item Batch No '+str(batch)+' is Not Available for this quantity'})

                    imei_notfound = set(lst_data_exists).difference(set(lst_for_comparison))
                    # import pdb;pdb.set_trace()
                    if imei_notfound:

                        inst_partial_validation.update(fk_invoice_id=None)

                        return Response({'status':0,'message':'The Item IMEI/Batch No ('+','.join(imei_notfound)+') is Not Available Now'})
                """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

                ins_partial_inv = PartialInvoice.objects.filter(pk_bint_id = request.data.get('salesRowId')).values().first()
                ins_branch_code = Branch.objects.filter(pk_bint_id = ins_partial_inv['json_data']['int_branch_id']).values('vchr_code').first()['vchr_code']
                moduel_name = "INVOICE"

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

                        inst_partial_validation.update(fk_invoice_id=None)
                        return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})


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

                # import pdb; pdb.set_trace()
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
                    dct_item['dblRate'] = float(dct_item['dblRate']) or 0
                    dct_item['dblMopAmount'] = float(dct_item['dblMopAmount']) or 0

                    if 'dblIGSTPer' in dct_item:
                        dct_item['dblIGSTPer'] = dct_item['dblIGSTPer'] or 0
                    if 'dblCGSTPer' in dct_item:
                        dct_item['dblCGSTPer'] = dct_item['dblCGSTPer'] or 0
                    if 'dblSGSTPer' in dct_item:
                        dct_item['dblSGSTPer'] = dct_item['dblSGSTPer'] or 0

                    if not ins_sales_master:
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
                                            jsn_addition = '{}',
                                            jsn_deduction = json.dumps(dct_deduction),
                                            # dbl_total_tax = dbl_total_tax,
                                            # dbl_discount = dbl_total_discount,
                                            # json_tax = json_total_tax,
                                            # dbl_buyback = dbl_total_buyback,
                                            fk_loyalty_id = request.data.get('intLoyaltyId',None),
                                            dbl_loyalty = 0,
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
                        dct_item['dblMopAmount'] = (-1)*float(dct_item['dblMopAmount'])
                        dct_item['dblRate'] = round((-1)*float(dct_item['dblRate']),2)
                    # if dct_item['intStatus'] in [0,2]:
                    #     dct_item['dblMopAmount'] = (-1)*dct_item['dblMopAmount']
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

                        json_item_tax['dblCGST'] += round(dct_item['dblCGST'],2)
                        json_item_tax['dblSGST'] += round(dct_item['dblSGST'],2)
                        dbl_total_tax += round(dct_item['dblCGST'],2) + round(dct_item['dblSGST'],2) + round(dct_item['intKfc'],2) if dct_item.get('intKfc') else 0
                        json_total_tax['dblCGST'] += round(dct_item['dblCGST'],2)
                        json_total_tax['dblSGST'] += round(dct_item['dblSGST'],2)
                        item_total_tax += round(dct_item['dblCGST'],2)+round(dct_item['dblSGST'],2)+ round(dct_item['intKfc'],2) if dct_item.get('intKfc') else 0

                        # LG
                        json_item_tax['dblCGST%'] = dct_item['dblCGSTPer'] if dct_item['dblCGSTPer'] else 0
                        json_item_tax['dblSGST%'] = dct_item['dblSGSTPer'] if dct_item['dblSGSTPer'] else 0

                    if item_total_tax_percent == 0:
                        item_total_tax_percent = json_item_tax.get('dblCGST%',0) +json_item_tax.get('dblSGST%',0) + json_item_tax.get('dblKFC%',0)

                    # import pdb;pdb.set_trace()
                    ins_sales_details=SalesDetails.objects.create(fk_master = ins_sales_master,
                                        fk_item_id = dct_item['intItemId'],
                                        int_qty = 1,
                                        dbl_amount = round(float(dct_item['dblRate']),2),
                                        dbl_selling_price = dct_item['dblMopAmount'],
                                        dbl_tax = round(item_total_tax,2),
                                        dbl_discount = (dct_item['dblDiscount'] or 0),
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
                    dbl_total_amt += float(dct_item['dblMopAmount'])
                    dbl_total_rate += round(float(dct_item['dblRate']),2)
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

                    if dct_item['intStatus'] == 2:
                        ins_branch_stock_details = ExchangeStock(dat_exchanged=date.today(),fk_item_id=dct_item['intItemId'],int_avail=dct_item['intQuantity'],jsn_imei=[dct_item['strImei']],jsn_avail=[dct_item['strImei']],fk_branch=ins_branch,fk_sales_details_id=ins_sales_details.pk_bint_id,dbl_unit_price=float(dct_item['dblMopAmount']))
                        ins_branch_stock_details.save()


                    if dct_item.get('itemEnqId'):
                        str_temp = '0-'+str(dct_item['itemEnqId'])+'-'+str(ins_sales_details.pk_bint_id)
                    else:
                        str_temp = '1-'+str(dct_item['strItemCode'])+'-'+str(ins_sales_details.pk_bint_id)


                    if str_temp and str_temp not in odct_item_data:
                        odct_item_data[str_temp] = {}
                        odct_item_data[str_temp]['jsonTax'] = dct_item['dblSGST']
                        odct_item_data[str_temp]['dblTax'] = round(item_total_tax,2)

                        odct_item_data[str_temp]['strItemCode'] = dct_item['strItemCode']
                        odct_item_data[str_temp]['intItemId'] = dct_item['intItemId']
                        odct_item_data[str_temp]['dblIndirectDis'] = dct_item.get('dblIndirectDis',0)
                        odct_item_data[str_temp]['dblBuyBack'] = dct_item['dblBuyBack']
                        odct_item_data[str_temp]['dblDiscount'] = dct_item['dblDiscount']
                        odct_item_data[str_temp]['dblRate'] = float(dct_item['dblRate'])
                        odct_item_data[str_temp]['dblAmount'] = float(dct_item['dblMopAmount'])
                        odct_item_data[str_temp]['intQuantity'] = 1
                        odct_item_data[str_temp]['status'] = dct_item['intStatus']

                        odct_item_data[str_temp]["dbl_supp_amnt"] = dct_item_sup_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_mop_amnt"] = dct_item_mop_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_mrp_amnt"] = dct_item_mrp_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_cost_amnt"] = dct_item_cost_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_myg_amnt"] = dct_item_myg_amnt.get(dct_item['intItemId']) or 0.0
                        odct_item_data[str_temp]["dbl_dealer_amnt"] = dct_item_dealer_amnt.get(dct_item['intItemId']) or 0.0

                        odct_item_data[str_temp]["dbl_tax"] = round(item_total_tax,2)
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
                ins_sales_master.dbl_discount = dbl_total_discount
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
                # import pdb; pdb.set_trace()
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

                dct_payment_data = json.loads(request.data.get('lstPaymentData'))
                # LG
                bln_payment_check=False
                lst_bi_payment_details = []
                for ins_mode in dct_payment_data:
                    #LG
                    dct_bi_payment_details = {}
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
                    if card_key:
                        for ins_payment_data in dct_payment_data[ins_mode][card_key]:
                            if ins_payment_data.get('dblAmt'):

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
                            # str_name=dct_payment_data[ins_mode].get('strName',None)

                            # import pdb; pdb.set_trace()
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
                        if dct_payment_data[ins_mode].get('intFinanceAmt'):
                            FinanceDetails.objects.create(fk_payment_id = ins_payment.pk_bint_id,
                                                          dbl_finance_amt = dct_payment_data[ins_mode].get('intFinanceAmt',None),
                                                          dbl_receved_amt = dct_payment_data[ins_mode].get('dblAmt',None),
                                                          dbl_processing_fee = dct_payment_data[ins_mode].get('dblProcessingFee',None),
                                                          dbl_margin_fee = dct_payment_data[ins_mode].get('dblMarginFee',None),
                                                          dbl_service_amt = dct_payment_data[ins_mode].get('dblServiceAmount',None),
                                                          dbl_dbd_amt  = dct_payment_data[ins_mode].get('dblDbdAmount',None))

                # import pdb;pdb.set_trace()
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

                else:
                    raise ValueError('Something happened in Transaction')
                # ------------------------- BI API ------------------------
                PartialInvoice.objects.filter(pk_bint_id = int(request.data.get('salesRowId'))).update(dat_invoice = datetime.now(),fk_invoice = ins_sales_master,int_active = 1)

                try:
                    ins_partial_inv = PartialInvoice.objects.get(pk_bint_id = int(request.data.get('salesRowId')))
                    int_enq_master_id = PartialInvoice.objects.filter(pk_bint_id = int(request.data.get('salesRowId'))).values().first()['json_data']['int_enq_master_id']

                    url =settings.BI_HOSTNAME + "/mobile/enquiry_invoice_update/"
                    res_data = requests.post(url,json={'dct_item_data':odct_item_data,"int_enq_master_id":int_enq_master_id,"str_remarks":str_remarks,'bi_payment_details':lst_bi_payment_details})
                    if res_data.json().get('status')=='success':
                        pass
                    else:
                        inst_partial_validation.update(fk_invoice_id=None)
                        raise ValueError('Something happened in BI')
                        return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})

                except Exception as e:
                    inst_partial_validation.update(fk_invoice_id=None)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                    raise ValueError('Something happened in BI')


                return Response({'status':1,'sales_master_id':ins_sales_master.pk_bint_id,'bln_jio':False})
        except Exception as e:
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
                int_partail = PartialInvoice.objects.filter(pk_bint_id=int_partial_id)
                # url = "http://192.168.0.174:2121/invoice/update_enquiry/"
                url =settings.BI_HOSTNAME + "/invoice/update_enquiry/"
                res_data = requests.post(url,json={'enquiry_id':int_partail.values('json_data')[0]['json_data']['int_enq_master_id'],'str_remark':str_remark,'user_code':request.user.username})
                if res_data.json().get('status')=='Success':
                    int_partail.update(int_active=-1)
                    return Response({'status':1,'message':'Successfully Rejected'})
                else:
                    return Response({'status': 'Failed','data':res_data.json().get('message',res_data.json())})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})


class viewList(APIView):
    permission_classes = [AllowAny]
    def put(self,request):
        try:
            # import pdb; pdb.set_trace()
            dat_to = (datetime.strptime(request.data.get("datTo")[:10],'%Y-%m-%d')).date()
            dat_from = (datetime.strptime(request.data.get("datFrom")[:10],'%Y-%m-%d')).date()

            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                ins_partial_inv = PartialInvoice.objects.filter(int_active = 0,int_approve__in=(0,2,4),dat_created__date__gte = dat_from,dat_created__date__lte = dat_to,json_data__contains={'bln_specialsale':'True'} ).exclude(int_status__in=(3,6,5,10,11)).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
            else:
                ins_partial_inv = PartialInvoice.objects.filter(Q(json_data__contains={'int_branch_id':request.user.userdetails.fk_branch_id}) & Q(json_data__contains={'bln_specialsale':'True'}),int_active = 0,int_approve__in=(0,2,4),dat_created__date__gte = dat_from,dat_created__date__lte = dat_to).exclude(int_status__in=(3,6,5,10,11)).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')

            # ins_partial_inv = PartialInvoice.objects.filter(int_active = 0,int_approve__in=(0,2,4),json_data__contains={'bln_specialsale':'True'} ).exclude(int_status__in=(3,6,5,10,11)).values('pk_bint_id','dat_created','json_data','int_status').order_by('-dat_created')
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
            dct_data['intSalesCustId'] =  ins_customer['pk_bint_id']
            dct_data['edit_count']=ins_customer['fk_customer__int_edit_count']
            if ins_partial_inv['int_approve'] in [1,2,3,4]:
                ins_partial_inv['json_data'] = ins_partial_inv['json_updated_data']
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
            dct_data['int_enquiry_type'] = ins_partial_inv['json_data'].get('int_enquiry_type',0)
            dct_data['vchr_reference_num'] = ins_partial_inv['json_data'].get('vchr_reference_num',None)
            dct_data['vchr_order_num'] = ins_partial_inv['json_data'].get('vchr_order_num',None)
            dct_data['txtRemarks'] = ins_partial_inv['json_data']['str_remarks']
            rst_recpts = Receipt.objects.filter(fk_customer = ins_customer['fk_customer_id'],int_doc_status__in=[0,1]).exclude(fk_customer__int_cust_type=1).values('pk_bint_id')
            lst_invoiced_recpts = list(ReceiptInvoiceMatching.objects.filter(fk_sales_master__fk_customer_id__fk_customer_id=ins_customer['fk_customer_id']).exclude(fk_sales_master__fk_customer_id__fk_customer_id__int_cust_type=1).values_list('fk_receipt_id',flat=True))
            cmp_rceipts = rst_recpts.exclude(pk_bint_id__in=lst_invoiced_recpts)
            dct_data['bln_status'] = True if cmp_rceipts else False
            dct_data['int_status'] = ins_partial_inv['int_status']
            dct_data['int_approve'] = ins_partial_inv['int_approve']
            if request.data.get('int_approve') in [2,4]:
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
            dct_data['lstItems'] = []
            dct_data['blnIGST'] = False
            rst_branch_state_code=Branch.objects.get(pk_bint_id=ins_partial_inv['json_data']['int_branch_id']).fk_states_id
            if rst_branch_state_code != ins_customer['fk_state_id']:
            # if request.user.userdetails.fk_branch.fk_states_id != ins_customer['fk_state_id']:
                dct_data['blnIGST'] = True
            dct_tax_master = {}
            dct_data['dbl_kfc_amount'] = 0.0
            dct_data['dblBalanceAmount'] = int(ins_partial_inv['json_data'].get('dbl_balance_amt') if  ins_partial_inv['json_data'].get('dbl_balance_amt') else 0)
            dct_data['dblPartialAmount'] = int(ins_partial_inv['json_data'].get('dbl_partial_amt') if ins_partial_inv['json_data'].get('dbl_partial_amt') else 0 )

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

                    dct_item['itemEnqId'] = ins_items_data.get('item_enquiry_id') # conflicted code

                    if ins_items_data['int_status'] == 2:

                        dct_item['dctImages'] = ins_items_data.get('dct_images')
                        dct_item['blnVerified'] = False
                    # import pdb;pdb.set_trace()
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

            """admin tools"""
            tools_keys(dct_data,request)


            return Response({'status':1,'data':dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

class invoiceView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        pass
