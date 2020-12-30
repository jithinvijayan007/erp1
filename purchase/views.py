from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from sap_api.models import SapApiTrack
from internal_stock.models import StockTransfer,IstDetails,StockTransferImeiDetails
from brands.models import Brands
from django.contrib.auth.models import User
from branch.models import Branch
from item_category.models import Item,TaxMaster
from supplier.models import Supplier,AddressSupplier
from .models import PoMaster,PoDetails,Document,GrnMaster,GrnDetails,PurchaseVoucher
from django.db.models import Q,F,CharField,Case,When,Value,Sum
from django.db import transaction
from datetime import datetime,timedelta,date
from POS import ins_logger
import sys, os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import json
from branch_stock.models import BranchStockDetails
from django.db.models.functions import Concat
from django.db.models import Value

from invoice.models import SalesDetails

class PurchaseOrderRequest(APIView):
    """
    to request order of purchase to supplier
    """
    permission_classes = [AllowAny]
    def post(self,request):
        """
        To save purchase order request
        parameter:date of request,supplier details,branch details,purchase item details and count
        return : 1 response
        """
        try:
            dat_po = request.data.get('orderDat')
            # dat_po_expiry
            int_supplier_id = request.data.get('intSupplier')
            int_branch_id = request.data.get('branch')
            vchr_notes = request.data.get('remarks')
            dbl_grand_amount = request.data.get('grandTot')
            dbl_grand_qty = request.data.get('grandQty')
            lst_item_details = request.data['items']
            ins_supplier = Supplier.objects.get(pk_bint_id=int_supplier_id)
            with transaction.atomic():
                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'PURCHASE ORDER')
                # str_code = ins_document[0].vchr_short_code
                # int_doc_num = ins_document[0].int_number + 1
                # ins_document.update(int_number = int_doc_num)
                # str_number = str(int_doc_num).zfill(4)
                # str_po_no = str_code + '-' + str_number

                # LG 27-06-2020
                str_po_no = doc_num_generator('PURCHASE ORDER',request.user.userdetails.fk_branch.pk_bint_id)
                if not str_po_no:
                    return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                # ins_po_master = PoMaster.objects.create_pomaster_doc(str_po_no)
                ins_po_master = PoMaster.objects.create(
                    vchr_po_num = str_po_no,
                    dat_po = dat_po,
                    dat_po_expiry = datetime.strptime(dat_po,'%Y-%m-%d')+timedelta(days=int(ins_supplier.int_po_expiry_days)),
                    fk_supplier_id = int_supplier_id,
                    fk_branch_id = int_branch_id,
                    vchr_notes = vchr_notes,
                    fk_created_id = request.user.id,
                    dat_created = datetime.now(),
                    int_doc_status = 0,
                    int_status = 0,
                    int_total_qty = dbl_grand_qty,
                    dbl_total_amount = dbl_grand_amount
                )
                ins_po_master.save()
                lst_query_set = []
                for dct_item in lst_item_details:
                    ins_po_details = PoDetails(
                        fk_item_id = dct_item['itemId'],
                        fk_po_master_id = ins_po_master.pk_bint_id,
                        int_qty = dct_item['qty'],
                        dbl_prate = round(float(dct_item['rate']),2),
                        dbl_total_amount = round(float(dct_item['totAmt']),2)
                    )
                    lst_query_set.append(ins_po_details)
                if lst_query_set:
                    PoDetails.objects.bulk_create(lst_query_set)

                return Response({'status':'1','message':'Request Successfully Registered'})
        except Exception as e:
            return Response({'status':'failed','message':str(e)})

class PORequestListView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            lst_po_details = []
            lst_po_details = list(PoMaster.objects.filter(int_doc_status__in = [1,0]).extra(select={'date_po':"to_char(po_master.dat_po, 'DD-MM-YYYY')",'date_po_expiry':"to_char(po_master.dat_po_expiry, 'DD-MM-YYYY')"}).values('vchr_po_num','date_po','date_po_expiry','fk_branch_id__vchr_name','fk_supplier_id__vchr_name','pk_bint_id').order_by('-dat_po','-pk_bint_id'))
            return Response({'status':'1','lst_po_details':lst_po_details})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


    def post(self,request):
        try:
            int_master_id = request.data.get('intMasterId')
            rst_po_details = PoDetails.objects.filter(fk_po_master_id =int_master_id,fk_po_master__int_doc_status__in = [1,0]).values('fk_po_master__dat_po','fk_po_master__dat_po_expiry','fk_po_master__fk_supplier_id','fk_po_master__fk_supplier__vchr_name','fk_po_master__fk_branch_id__vchr_name','fk_po_master__fk_branch_id','fk_po_master__vchr_notes','fk_item_id','fk_item__vchr_name','int_qty','dbl_prate')
            dct_po_details = {}
            dct_po_details['netQty'] = 0
            dct_po_details['netAmount'] = 0
            dct_po_details['lst_item_details'] = []
            for ins_details in rst_po_details:
                dct_details = {}
                dct_details['item_name'] = ins_details['fk_item__vchr_name']
                dct_details['item_id'] = ins_details['fk_item_id']
                dct_details['int_qty'] = ins_details['int_qty']
                dct_details['rate'] = ins_details['dbl_prate']
                dct_details['amount'] = ins_details['dbl_prate'] * ins_details['int_qty']
                dct_po_details['netQty'] += ins_details['int_qty']
                dct_po_details['netAmount'] += dct_details['amount']
                dct_po_details['lst_item_details'].append(dct_details)
            if dct_po_details['lst_item_details']:
                dct_po_details['dat_po'] = datetime.strftime(ins_details['fk_po_master__dat_po'],'%d-%m-%Y')
                dct_po_details['dat_po_expiry'] = datetime.strftime(ins_details['fk_po_master__dat_po_expiry'],'%d-%m-%Y')
                dct_po_details['supplier_id'] = ins_details['fk_po_master__fk_supplier_id']
                dct_po_details['supplier_name'] = ins_details['fk_po_master__fk_supplier__vchr_name']
                dct_po_details['branch_id'] = ins_details['fk_po_master__fk_branch_id']
                dct_po_details['branch_name'] = ins_details['fk_po_master__fk_branch_id__vchr_name']
                dct_po_details['notes'] = ins_details['fk_po_master__vchr_notes']
            return Response({'status':'1','data':dct_po_details})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

class BranchList(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            lst_branch =[]
            lst_branch = list(Branch.objects.filter(int_type__in=[2,3],int_status =0).annotate(branch_type=Case(
                    When(int_type=2,then=Value('HO')),
                    When(int_type=3,then=Value('WH')),
                    output_field=CharField(),
            )).values('pk_bint_id','vchr_name','vchr_code','branch_type','fk_states_id'))
            return Response({'status':'1','lst_branch':lst_branch})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

class SupplierTypeahead(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_supplier = []
            if str_search_term != -1:
                ins_supplier = Supplier.objects.filter(Q(vchr_code__icontains=str_search_term)\
                | Q(vchr_name__icontains=str_search_term),is_act_del = 0).values('int_batch_no_offset','vchr_code','pk_bint_id','vchr_name','vchr_code','int_credit_days')
                dct_states_id = dict(AddressSupplier.objects.filter(fk_supplier__is_act_del = 0).values_list('fk_supplier_id','fk_states_id'))
                if ins_supplier:
                    for itr_item in ins_supplier:
                        dct_supplier = {}
                        dct_supplier['name'] = itr_item['vchr_code'].upper()+'-'+itr_item['vchr_name'].title()
                        dct_supplier['id'] = itr_item['pk_bint_id']
                        # str_number = str(int(itr_item['int_batch_no_offset'])+1).zfill(4)
                        # dct_supplier['batch_num'] = itr_item['vchr_code'] + '-' + str_number
                        dct_supplier['credit_days'] = itr_item['int_credit_days']
                        dct_supplier['supplier_states_id'] = dct_states_id.get(itr_item['pk_bint_id'])
                        lst_supplier.append(dct_supplier)
                return Response({'status':'1','data':lst_supplier})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


class ItemTypeahead(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_items = []
            ins_grn_items =[]
            tax_name = dict(TaxMaster.objects.values_list('pk_bint_id','vchr_name'))
            if str_search_term != -1:
                ins_items = Item.objects.filter(Q(vchr_name__icontains=str_search_term)\
                    | Q(vchr_item_code__icontains=str_search_term),int_status = 0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master','imei_status','dbl_mop','fk_product_id','fk_brand_id','fk_product__vchr_name', 'fk_brand__vchr_name')
                if ins_items:
                    if request.data.get('intProduct'):
                        ins_items=ins_items.filter(fk_product_id=request.data.get('intProduct'))
                    if request.data.get('intBrand'):
                        ins_items=ins_items.filter(fk_brand_id=request.data.get('intBrand'))

                    for itr_item in ins_items[:20]:
                        dct_item = {}
                        # dct_item['code'] = itr_item['vchr_code'].upper()
                        dct_item['name'] = itr_item['vchr_item_code'].upper()+'-'+itr_item['vchr_name'].title()
                        dct_item['id'] = itr_item['pk_bint_id']
                        dct_item['rate']=itr_item['dbl_mop']
                        dct_item['product_id']=itr_item['fk_product_id']
                        dct_item['product_name']=itr_item['fk_product__vchr_name']
                        dct_item['brand_id']=itr_item['fk_brand_id']
                        dct_item['brand_name']=itr_item['fk_brand__vchr_name']
                        if  itr_item['fk_item_category__json_tax_master']:
                            dct_item['jsn_tax']={}
                            for ins_tax in itr_item['fk_item_category__json_tax_master']:
                                # dct_item['jsn_tax'][ins_tax] ={}
                                dct_item['jsn_tax'][tax_name[int(ins_tax)]] =  itr_item['fk_item_category__json_tax_master'][ins_tax]
                        else:
                            dct_item['jsn_tax']=0
                        dct_item['imei_status']=itr_item['imei_status']
                        ins_stock_quantity = BranchStockDetails.objects.filter(fk_item_id = itr_item['pk_bint_id'],fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_qty'))
                        ins_grn_quantity = []
                        # import pdb; pdb.set_trace()
                        if request.user.userdetails.fk_branch.int_type in[2,3]:
                            ins_grn_quantity = GrnDetails.objects.filter(fk_item_id = itr_item['pk_bint_id'],fk_purchase__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_avail'))

                        dct_item['item_qty']= (ins_stock_quantity[0]['int_Qty'] if ins_stock_quantity else 0) + (ins_grn_quantity[0]['int_Qty'] if ins_grn_quantity else 0)
                        lst_items.append(dct_item)
                    return Response({'status':'1','data':lst_items})
                else:
                    return Response({'status':'empty'})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

class ImeiScan(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_imei = request.data.get('strImei')
            if request.user.userdetails.fk_branch.int_type in[2,3]:
                ins_stock_quantity = GrnDetails.objects.filter(Q(Q(jsn_imei_avail__icontains  = str_imei)|Q(vchr_batch_no = str_imei,int_avail__gte = 1)),fk_purchase__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_avail'))
                if not ins_stock_quantity:
                    ins_stock_quantity = BranchStockDetails.objects.filter(Q(Q(jsn_imei_avail__icontains = str_imei)|Q(jsn_batch_no__icontains = str_imei,int_qty__gte = 1)) ,fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_qty'))
            else:
                ins_stock_quantity = BranchStockDetails.objects.filter(Q(Q(jsn_imei_avail__icontains = str_imei)|Q(jsn_batch_no__icontains = str_imei,int_qty__gte = 1)) ,fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_qty'))
            if ins_stock_quantity:
                ins_items = Item.objects.filter(pk_bint_id = ins_stock_quantity[0]['fk_item_id']).annotate(vchr_item_name = Concat('vchr_item_code',Value('-'),'vchr_name')).values('pk_bint_id','vchr_name','vchr_item_name',
                                                                                                                                                                              'vchr_item_code',
                                                                                                                                                                              'fk_item_category__json_tax_master',
                                                                                                                                                                              'dbl_mop','fk_product_id',
                                                                                                                                                                              'imei_status','fk_brand_id',
                                                                                                                                                                              'fk_product__vchr_name',
                                                                                                                                                                              'fk_brand__vchr_name')
                dct_data = {**ins_stock_quantity[0],**ins_items[0]}
            else:
                return Response({'status':0,'data':'No item found'})

            return Response({'status':1,'data':dct_data})



        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


class PurchaseOrderList(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            lst_po = []
            lst_po = list(PoMaster.objects.filter(int_doc_status__in = [1,0]).values('vchr_po_num','pk_bint_id'))
            return Response({'status':'1','lst_po_num':lst_po})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

    def post(self,request):
        try:
            rst_purchase_details = []
            vchr_pro_num = request.data.get('purOrderNum')
            rst_po_details = PoDetails.objects.filter(fk_po_master__vchr_po_num =vchr_pro_num).values('fk_po_master__fk_supplier__int_credit_days','fk_po_master__fk_supplier_id','fk_po_master__fk_supplier__vchr_code','fk_po_master__fk_supplier__int_batch_no_offset','fk_po_master__fk_supplier__vchr_name','fk_po_master__fk_branch_id__vchr_name','fk_po_master__fk_branch__fk_states_id','fk_po_master__fk_branch_id','fk_po_master__vchr_notes','fk_item_id','dbl_prate','fk_item__vchr_name','fk_item__vchr_item_code','fk_item__fk_item_category__json_tax_master','int_qty','fk_item__imei_status')
            rst_purchase_details = GrnDetails.objects.filter(fk_purchase__fk_po__vchr_po_num = vchr_pro_num,fk_purchase__int_approve__in=[1,0,2]).values('fk_item__vchr_name','fk_item__vchr_item_code','fk_purchase__fk_supplier__vchr_code','fk_item__fk_item_category__json_tax_master','fk_item_id','fk_purchase__fk_supplier_id','fk_purchase__fk_supplier__int_batch_no_offset','fk_purchase__fk_supplier__vchr_name','fk_purchase__fk_supplier__int_credit_days','fk_purchase__fk_branch__fk_states_id','fk_purchase__fk_branch_id','fk_purchase__fk_branch__vchr_name','fk_item__imei_status').annotate(total_qty=Sum(F('int_qty')))
            dct_po_details = {}
            dct_po_details['lst_item_details'] = []
            if not rst_purchase_details and not rst_po_details:
                return Response({'status':'0','message':'No data'})
            dct_tax_master = {}
            for ins_tax in TaxMaster.objects.values('vchr_name','pk_bint_id'):
                dct_tax_master[ins_tax['vchr_name']] = str(ins_tax['pk_bint_id'])
            if not rst_purchase_details:
                for ins_details in rst_po_details:
                    dct_details = {}
                    dct_details['item_name'] = ins_details['fk_item__vchr_item_code'].upper()+'-'+ins_details['fk_item__vchr_name'].title()
                    dct_details['item_id'] = ins_details['fk_item_id']
                    dct_details['int_qty'] = ins_details['int_qty']
                    dct_details['imei_status'] = ins_details['fk_item__imei_status']
                    dct_details['cgst'] = 0
                    dct_details['sgst'] = 0
                    dct_details['igst'] = 0
                    if ins_details['fk_item__fk_item_category__json_tax_master']:
                        if dct_tax_master['CGST'] in ins_details['fk_item__fk_item_category__json_tax_master']:
                            dct_details['cgst'] = ins_details['fk_item__fk_item_category__json_tax_master'][dct_tax_master['CGST']]
                        if dct_tax_master['SGST'] in ins_details['fk_item__fk_item_category__json_tax_master']:
                            dct_details['sgst'] = ins_details['fk_item__fk_item_category__json_tax_master'][dct_tax_master['SGST']]
                        if dct_tax_master['IGST'] in ins_details['fk_item__fk_item_category__json_tax_master']:
                            dct_details['igst'] = ins_details['fk_item__fk_item_category__json_tax_master'][dct_tax_master['IGST']]

                    dct_details['free']= 0
                    dct_details['rate']= ins_details['dbl_prate']
                    dct_details['disPer']= 0
                    dct_details['disPerUnit']= 0
                    dct_details['disAmt']= 0
                    # dct_details['cgst']= 0
                    # dct_details['sgst']= 0
                    dct_details['totAmt']= 0
                    dct_details['lstImei']= []
                    # dct_details['batchNo'] = 0
                    dct_po_details['lst_item_details'].append(dct_details)
                if dct_po_details['lst_item_details']:
                    dct_po_details['supplier_id'] = ins_details['fk_po_master__fk_supplier_id']
                    dct_po_details['supplier_name'] = ins_details['fk_po_master__fk_supplier__vchr_name']
                    str_number = str(int(ins_details['fk_po_master__fk_supplier__int_batch_no_offset'])+1).zfill(4)
                    dct_po_details['batch_num'] = ins_details['fk_po_master__fk_supplier__vchr_code'] + '-' + str_number
                    dct_po_details['branch_id'] = ins_details['fk_po_master__fk_branch_id']
                    dct_po_details['branch_name'] = ins_details['fk_po_master__fk_branch_id__vchr_name']
                    dct_po_details['branch_state_id'] = ins_details['fk_po_master__fk_branch__fk_states_id']
                    dct_po_details['supplier_state_id'] = ins_details['fk_po_master__fk_branch__fk_states_id']
                    rst_supplier_state = AddressSupplier.objects.filter(fk_supplier_id=ins_details['fk_po_master__fk_supplier_id']).values('fk_states_id')
                    if rst_supplier_state and rst_supplier_state[0]['fk_states_id']:
                        dct_po_details['supplier_state_id'] = rst_supplier_state[0]['fk_states_id']

                    dct_po_details['int_credit_days'] = ins_details['fk_po_master__fk_supplier__int_credit_days']
            else:
                dct_item={}
                for ins_item in rst_po_details:
                    dct_item[ins_item['fk_item_id']] = {}
                    dct_item[ins_item['fk_item_id']]['qty'] = ins_item['int_qty']
                    dct_item[ins_item['fk_item_id']]['name'] = ins_item['fk_item__vchr_name']
                    dct_item[ins_item['fk_item_id']]['rate'] = ins_item['dbl_prate']
                for ins_details in rst_purchase_details:
                    if ins_details['total_qty'] and ins_details['fk_item_id'] in dct_item and (dct_item[ins_details['fk_item_id']]['qty'] - ins_details['total_qty'])>0:
                        dct_details = {}
                        dct_details['item_name'] = ins_details['fk_item__vchr_item_code'].upper()+'-'+ins_details['fk_item__vchr_name'].title()
                        dct_details['item_id'] = ins_details['fk_item_id']
                        dct_details['imei_status'] = ins_details['fk_item__imei_status']
                        dct_details['int_qty'] = dct_item[ins_details['fk_item_id']]['qty'] - ins_details['total_qty']
                        dct_details['free']= 0
                        dct_details['rate']= dct_item[ins_details['fk_item_id']]['rate']
                        dct_details['disPer']= 0
                        dct_details['disPerUnit']= 0
                        dct_details['disAmt']= 0
                        # dct_details['cgst']= 0
                        # dct_details['sgst']= 0
                        dct_details['cgst'] = 0
                        dct_details['sgst'] = 0
                        dct_details['igst'] = 0
                        if ins_details['fk_item__fk_item_category__json_tax_master']:
                            if dct_tax_master['CGST'] in ins_details['fk_item__fk_item_category__json_tax_master']:
                                dct_details['cgst'] = ins_details['fk_item__fk_item_category__json_tax_master'][dct_tax_master['CGST']]
                            if dct_tax_master['SGST'] in ins_details['fk_item__fk_item_category__json_tax_master']:
                                dct_details['sgst'] = ins_details['fk_item__fk_item_category__json_tax_master'][dct_tax_master['SGST']]
                            if dct_tax_master['IGST'] in ins_details['fk_item__fk_item_category__json_tax_master']:
                                dct_details['igst'] = ins_details['fk_item__fk_item_category__json_tax_master'][dct_tax_master['IGST']]

                        dct_details['totAmt']= 0
                        dct_details['lstImei']= []
                        # dct_details['batchNo'] = 0
                        dct_po_details['lst_item_details'].append(dct_details)
                        del dct_item[ins_details['fk_item_id']]
                    elif (ins_details['fk_item_id'] in dct_item) and not (dct_item[ins_details['fk_item_id']]['qty'] - ins_details['total_qty']) >0:
                        del dct_item[ins_details['fk_item_id']]
                if dct_po_details['lst_item_details']:
                    dct_po_details['supplier_id'] = ins_details['fk_purchase__fk_supplier_id']
                    dct_po_details['supplier_name'] = ins_details['fk_purchase__fk_supplier__vchr_name']
                    str_number = str(int(ins_details['fk_purchase__fk_supplier__int_batch_no_offset'])+1).zfill(4)
                    dct_po_details['batch_num'] = ins_details['fk_purchase__fk_supplier__vchr_code'] + '-' + str_number
                    dct_po_details['branch_id'] = ins_details['fk_purchase__fk_branch_id']
                    dct_po_details['branch_name'] = ins_details['fk_purchase__fk_branch__vchr_name']
                    dct_po_details['branch_state_id'] = ins_details['fk_purchase__fk_branch__fk_states_id']
                    dct_po_details['supplier_state_id'] = ins_details['fk_purchase__fk_branch__fk_states_id']
                    rst_supplier_state = AddressSupplier.objects.filter(fk_supplier_id=ins_details['fk_purchase__fk_supplier_id']).values('fk_states_id')
                    if rst_supplier_state and rst_supplier_state[0]['fk_states_id']:
                        dct_po_details['supplier_state_id'] = rst_supplier_state[0]['fk_states_id']
                    dct_po_details['int_credit_days'] = ins_details['fk_purchase__fk_supplier__int_credit_days']
                if dct_item:
                    for ins_details in rst_po_details:
                        if ins_details['fk_item_id'] in dct_item:
                            dct_details = {}
                            dct_details['item_name'] = ins_details['fk_item__vchr_item_code'].upper()+'-'+ins_details['fk_item__vchr_name'].title()
                            dct_details['item_id'] = ins_details['fk_item_id']
                            dct_details['imei_status'] = ins_details['fk_item__imei_status']
                            dct_details['int_qty'] = ins_details['int_qty']
                            dct_details['free']= 0
                            dct_details['rate']= ins_details['dbl_prate']
                            dct_details['disPer']= 0
                            dct_details['disPerUnit']= 0
                            dct_details['disAmt']= 0
                            dct_details['cgst']= 0
                            dct_details['sgst']= 0
                            dct_details['igst'] = 0
                            if ins_details['fk_item__fk_item_category__json_tax_master']:
                                if 'CGST' in ins_details['fk_item__fk_item_category__json_tax_master']:
                                    dct_details['cgst'] = ins_details['fk_item__fk_item_category__json_tax_master']['CGST']
                                if 'SGST' in ins_details['fk_item__fk_item_category__json_tax_master']:
                                    dct_details['sgst'] = ins_details['fk_item__fk_item_category__json_tax_master']['SGST']
                                if 'IGST' in ins_details['fk_item__fk_item_category__json_tax_master']:
                                    dct_details['igst'] = ins_details['fk_item__fk_item_category__json_tax_master']['IGST']

                            dct_details['totAmt']= 0
                            dct_details['lstImei']= []
                            # dct_details['batchNo'] = 0
                            dct_po_details['lst_item_details'].append(dct_details)

                    if dct_po_details['lst_item_details']:
                        dct_po_details['supplier_id'] = ins_details['fk_po_master__fk_supplier_id']
                        dct_po_details['supplier_name'] = ins_details['fk_po_master__fk_supplier__vchr_name']
                        str_number = str(int(ins_details['fk_po_master__fk_supplier__int_batch_no_offset'])+1).zfill(4)
                        dct_po_details['batch_num'] = ins_details['fk_po_master__fk_supplier__vchr_code'] + '-' + str_number
                        dct_po_details['branch_id'] = ins_details['fk_po_master__fk_branch_id']
                        dct_po_details['branch_name'] = ins_details['fk_po_master__fk_branch_id__vchr_name']
                        dct_po_details['branch_state_id'] = ins_details['fk_po_master__fk_branch__fk_states_id']
                        dct_po_details['supplier_state_id'] = ins_details['fk_po_master__fk_branch__fk_states_id']
                        rst_supplier_state = AddressSupplier.objects.filter(fk_supplier_id=ins_details['fk_po_master__fk_supplier_id']).values('fk_states_id')
                        if rst_supplier_state and rst_supplier_state[0]['fk_states_id']:
                            dct_po_details['supplier_state_id'] = rst_supplier_state[0]['fk_states_id']

                        dct_po_details['int_credit_days'] = ins_details['fk_po_master__fk_supplier__int_credit_days']
            if not dct_po_details['lst_item_details']:
                return Response({'status':'2','message':'Given Order Closed'})
            return Response({'status':'1','data':dct_po_details})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


class GnrListApi(APIView):
    """
    list and approve and view GNR list
    parameter : GnrId
    Response : Success and list
    """
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            lst_gnr_details = []
            lst_gnr_details = list(GrnMaster.objects.exclude(int_doc_status__in = [-1,4]).extra(select={'date_purchase':"to_char(grn_master.dat_purchase, 'DD-MM-YYYY')"}).values('pk_bint_id','vchr_purchase_num','date_purchase','dbl_total','fk_supplier__vchr_name','fk_branch__vchr_name','int_approve').order_by('-dat_purchase','-pk_bint_id'))
            return Response({'status':'1','data':lst_gnr_details})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


    def post(self,request):
        try:
            # import pdb;pdb.set_trace()
            int_purchase_id = request.data.get('intMasterId')
            if not int_purchase_id:
                lst_gnr_details = []
                dat_from = request.data.get("datFrom")
                dat_to= request.data.get("datTo")
                lst_branch=[request.user.userdetails.fk_branch_id]
                if request.user.userdetails.fk_group.vchr_name.upper() =='ADMIN':
                    lst_branch = list(Branch.objects.filter().values_list('pk_bint_id',flat=True))
                lst_gnr_details = list(GrnMaster.objects.filter(dat_purchase__date__gte=dat_from,dat_purchase__date__lte=dat_to,fk_branch_id__in=lst_branch).exclude(int_doc_status__in = [-1,4]).extra(select={'date_purchase':"to_char(grn_master.dat_purchase, 'DD-MM-YYYY')"}).values('pk_bint_id','vchr_purchase_num','date_purchase','dbl_total','fk_supplier__vchr_name','fk_branch__vchr_name','int_approve').order_by('-dat_purchase','-pk_bint_id'))
                lst_grn_ids = GrnMaster.objects.filter(dat_purchase__date__gte=dat_from,dat_purchase__date__lte=dat_to,fk_branch_id__in=lst_branch).exclude(int_doc_status__in = [-1,4]).values('pk_bint_id')
                grn_products = list(GrnDetails.objects.filter(fk_purchase_id__in =  lst_grn_ids).values('fk_purchase_id','fk_item_id__fk_product_id__vchr_name'))
                for ins_details in lst_gnr_details:
                    lst_products = list(filter(lambda d: d['fk_purchase_id'] in [ins_details['pk_bint_id']], grn_products))
                    lst_prod = []
                    if lst_products:
                        for ins_product in lst_products:
                            if ins_product['fk_item_id__fk_product_id__vchr_name'].upper() not in lst_prod:
                                lst_prod.append(ins_product['fk_item_id__fk_product_id__vchr_name'])
                    ins_details['list_products'] = lst_prod
                return Response({'status':'1','data':lst_gnr_details})
            rst_purchase = GrnDetails.objects.filter(fk_purchase_id = int(int_purchase_id)).\
            values('fk_purchase_id','fk_purchase__dat_purchase','fk_purchase__vchr_purchase_num','fk_purchase__fk_supplier__vchr_name','fk_purchase__fk_supplier_id','fk_purchase__fk_branch__vchr_name','fk_purchase__fk_branch__fk_states_id','fk_purchase__fk_branch_id',\
                    'fk_purchase__int_fop','fk_purchase__fk_po__vchr_po_num','fk_purchase__fk_po_id','fk_purchase__dat_pay_before',\
                    'fk_purchase__dbl_total','fk_purchase__vchr_notes','fk_purchase__dbl_addition','fk_purchase__dbl_deduction',\
                    'fk_purchase__dbl_roundoff_value','fk_purchase__vchr_bill_no','fk_purchase__dat_bill','fk_purchase__vchr_reject_reason',\
                    'fk_purchase__int_approve','fk_purchase__dbl_bill_amount','fk_purchase__vchr_bill_image','fk_item_id','fk_item__vchr_name','fk_item__imei_status','fk_item__vchr_item_code','int_qty','int_avail','int_free','int_damaged','dbl_costprice','dbl_dscnt_percent','dbl_dscnt_perunit','dbl_discount','jsn_tax','vchr_batch_no',\
                        'dbl_total_amount','vchr_batch_no','jsn_imei','jsn_imei_dmgd','dbl_perpie_aditn','dbl_perpie_dedctn','fk_item__fk_item_category__json_tax_master')

            dct_purchase = {}
            dct_purchase['lst_item'] = []
            dct_purchase['bln_transfer']=True
            for ins_item in rst_purchase:
                dct_item = {}
                if ins_item['int_qty'] != ins_item['int_avail']:
                    dct_purchase['bln_transfer']=False
                dct_item['item_id'] = ins_item['fk_item_id']
                dct_item['item_name'] = ins_item['fk_item__vchr_item_code'].upper()+'-'+ins_item['fk_item__vchr_name'].title()
                dct_item['int_qty'] = ins_item['int_qty']
                dct_item['int_free'] = ins_item['int_free']
                dct_item['int_damage'] = ins_item['int_damaged']
                dct_item['unit_price'] = ins_item['dbl_costprice']
                dct_item['discount_percent'] = ins_item['dbl_dscnt_percent']
                dct_item['discount_per_unit'] = ins_item['dbl_dscnt_perunit']
                dct_item['total_discount'] = ins_item['dbl_discount']
                dct_item['cgst'] = ins_item['jsn_tax']['CGST%'] if ins_item['jsn_tax'] else 0
                dct_item['sgst'] = ins_item['jsn_tax']['SGST%'] if ins_item['jsn_tax'] else 0
                dct_item['igst'] = 0
                dct_item['igst'] = ins_item['jsn_tax']['IGST%'] if ins_item['jsn_tax'] else 0
                dct_item['batch_num'] = ins_item['vchr_batch_no']
                dct_item['imei_status'] = ins_item['fk_item__imei_status']
                ins_item['dbl_perpie_aditn'] = ins_item['dbl_perpie_aditn'] if ins_item['dbl_perpie_aditn'] else 0
                ins_item['dbl_perpie_dedctn'] = ins_item['dbl_perpie_dedctn'] if ins_item['dbl_perpie_dedctn'] else 0
                dct_item['total_amount'] = round(ins_item['dbl_total_amount'] - (ins_item['dbl_perpie_aditn']*ins_item['int_qty']) + (ins_item['dbl_perpie_dedctn']*ins_item['int_qty']),2)
                dct_item['imei_damaged'] = []
                if ins_item['jsn_imei']:
                    dct_item['imei'] = ins_item['jsn_imei']['imei']
                if ins_item['jsn_imei_dmgd']:
                    dct_item['imei_damaged'] = ins_item['jsn_imei_dmgd']['imei_damage']


                dct_purchase['lst_item'].append(dct_item)

            if dct_purchase['lst_item']:
                dct_purchase['purchase_id'] = ins_item['fk_purchase_id']
                dct_purchase['purchase_num'] = ins_item['fk_purchase__vchr_purchase_num']
                dct_purchase['supplier_id'] = ins_item['fk_purchase__fk_supplier_id']
                dct_purchase['supplier_name'] = ins_item['fk_purchase__fk_supplier__vchr_name']
                dct_purchase['branch_id'] = ins_item['fk_purchase__fk_branch_id']
                dct_purchase['branch_name'] = ins_item['fk_purchase__fk_branch__vchr_name']
                dct_purchase['branch_state_id'] = ins_item['fk_purchase__fk_branch__fk_states_id']
                dct_purchase['supplier_state_id'] = ins_item['fk_purchase__fk_branch__fk_states_id']
                dct_purchase['dbl_bill_amount'] = ins_item['fk_purchase__dbl_bill_amount']
                dct_purchase['vchr_bill_image'] = ins_item['fk_purchase__vchr_bill_image']
                rst_supplier_state = AddressSupplier.objects.filter(fk_supplier_id=ins_item['fk_purchase__fk_supplier_id']).values('fk_states_id')
                if rst_supplier_state and rst_supplier_state[0]['fk_states_id']:
                    dct_purchase['supplier_state_id'] = rst_supplier_state[0]['fk_states_id']
                dct_purchase['dat_purchase'] = datetime.strftime(ins_item['fk_purchase__dat_purchase'],'%d-%m-%Y')
                dct_purchase['vchr_notes'] = ins_item['fk_purchase__vchr_notes']
                dct_purchase['fk_po_id'] = ins_item['fk_purchase__fk_po_id']
                dct_purchase['fk_po_num'] = ins_item['fk_purchase__fk_po__vchr_po_num']
                dct_purchase['int_fop'] = ins_item['fk_purchase__int_fop']
                if ins_item['fk_purchase__dat_pay_before']:
                    dct_purchase['dat_pay_before'] = datetime.strftime(ins_item['fk_purchase__dat_pay_before'],'%d-%m-%Y')
                dct_purchase['dbl_total'] = ins_item['fk_purchase__dbl_total']
                dct_purchase['dbl_addition'] = ins_item['fk_purchase__dbl_addition']
                dct_purchase['dbl_deduction'] = ins_item['fk_purchase__dbl_deduction']
                dct_purchase['dbl_roundoff_value'] = ins_item['fk_purchase__dbl_roundoff_value']
                dct_purchase['int_approve'] = ins_item['fk_purchase__int_approve']
                dct_purchase['bill_no'] = ins_item['fk_purchase__vchr_bill_no']

                if ins_item['fk_purchase__dat_bill']:
                    dct_purchase['bill_date'] = datetime.strftime(ins_item['fk_purchase__dat_bill'],'%d-%m-%Y')
                dct_purchase['reason'] = ins_item['fk_purchase__vchr_reject_reason']
                # fk_purchase__vchr_bill_no

            return Response({'status':'1','dct_purchase':dct_purchase})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

    def patch(self,request):
        try:
            int_gnr_id = request.data.get('intMasterId')
            vchr_action = request.data.get('blnApproved')
            vchr_remarks = request.data.get('strReason')
            if vchr_action:
                GrnMaster.objects.filter(pk_bint_id= int_gnr_id).update(int_approve=1,fk_updated_id=request.user.id,dat_updated=datetime.now())
            else:
                GrnMaster.objects.filter(pk_bint_id= int_gnr_id).update(int_approve=-1,fk_updated_id=request.user.id,dat_updated=datetime.now(),vchr_reject_reason = vchr_remarks)
            return Response({'status':'1'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

class PurchaseVoucherApi(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            int_grn_id = request.data.get('intMasterId')
            int_supplier_id = request.data.get('intSupllierId')
            dat_bill = request.data.get('billDat')
            vchr_bill_no = request.data.get('billNo')
            dbl_total_amount = request.data.get('dbl_amount')
            vchr_remarks = request.data.get('strRemarks')
            with transaction.atomic():
                # GrnMaster.objects.filter(pk_bint_id=int_gnr_id,int_approve=1).update(dat_updated=datetime.now(),fk_updated_id=request.user.id,int_doc_status=-1)
                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'PURCHASE VOUCHER')
                # str_code = ins_document[0].vchr_short_code
                # int_doc_num = ins_document[0].int_number + 1
                # ins_document.update(int_number = int_doc_num)
                # str_number = str(int_doc_num).zfill(4)
                # str_voucher_no = str_code + '-' + str_number

                # LG 27-06-2020
                str_voucher_no = doc_num_generator('PURCHASE VOUCHER',request.user.userdetails.fk_branch.pk_bint_id)
                if not str_voucher_no:
                    return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                # ins_voucher = PurchaseVoucher.objects.create_pur_vouch_doc(str_voucher_no)
                ins_voucher = PurchaseVoucher.objects.create(
                    vchr_voucher_num = str_voucher_no,
                    fk_grn_id = int_grn_id,
                    fk_supplier_id = int_supplier_id,
                    dbl_voucher_amount = dbl_total_amount,
                    vchr_voucher_bill_no = vchr_bill_no,
                    dat_voucher_bill = dat_bill,
                    fk_created_id = request.user.id,
                    dat_created = datetime.now(),
                    vchr_remark = vchr_remarks,
                    int_doc_status = 0
                )
                ins_voucher.save()
                GrnMaster.objects.filter(pk_bint_id = int_grn_id).update(int_approve=2)
                return Response({'status':'1','message':'Purchase bill generated'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

    def get(self,request):
        try:
            lst_voucher = []
            lst_voucher = list(PurchaseVoucher.objects.exclude(int_doc_status=-1).values('pk_bint_id','dat_created','fk_supplier__vchr_name','vchr_voucher_num'))
            return Response({'status':'1','data':lst_voucher})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

    def put(self,request):
        try:
            rst_voucher = []
            int_voucher_id = request.data.get('intMasterId')
            rst_voucher = PurchaseVoucher.objects.filter(pk_bint_id=int_voucher_id).values('pk_bint_id','dat_created','fk_supplier__vchr_name','vchr_voucher_num','fk_grn__vchr_purchase_num','vchr_voucher_bill_no','dbl_voucher_amount','dat_voucher_bill','vchr_remark')
            return Response({'status':'1','data':rst_voucher})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

    def patch(self,request):
        try:
            int_voucher_id = request.data.get('intMasterId')
            PurchaseVoucher.objects.filter(pk_bint_id=int_voucher_id).update(fk_updated_id=request.user.id,dat_updated=datetime.now(),int_doc_status = -1)
            return Response({'status':'1','message':'Voucher Deleted'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


class BatchItemUniqueCheck(APIView):
    """
    to check the batch is unique to item
    """
    permission_classes = [AllowAny]
    def post(self,request):
        """

        """
        try:
            item_id = request.data.get('itemId')
            batch_no = request.data.get('batchNo')

            ins_check = GrnDetails.objects.filter(fk_item_id=item_id,vchr_batch_no=batch_no).exclude(fk_purchase__int_approve = -1).values('pk_bint_id')
            if ins_check:
                return Response({'status':'0','message':'Already Exists'})
            else:
                return Response({'status':'1','message':'Success'})

        except Exception as e:
            return Response({'status':'failed','message':str(e)})




class PurschaseApi(APIView):
    permission_classes = [AllowAny]
    def put(self,request):
        try:
            bln_branch_stock=BranchStockDetails.objects.filter(jsn_imei_avail__imei__icontains='"'+request.data.get('imei')+'"').exists()
            bln_grn_stock=GrnDetails.objects.filter(jsn_imei_avail__imei_avail__icontains='"'+request.data.get('imei')+'"').exists()

            bln_transfer_details=StockTransferImeiDetails.objects.filter(jsn_imei__icontains='"'+request.data.get('imei')+'"').exists()

            bln_sales_details=SalesDetails.objects.filter(json_imei__icontains='"'+request.data.get('imei')+'"').exists()

            if  bln_sales_details:
                return Response({'status':0,'message':'Item with this imei is already sold'})

            elif bln_branch_stock or bln_grn_stock or  bln_transfer_details:
                return Response({'status':0,'message':'Item with this imei exists in stock'})
            else:
                return Response({'status':1})


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

    def post(self,request):
        try:
            dat_purchase = request.data.get('purDat')
            int_supplier_id = int(request.data.get('intSupplier'))
            int_branch_id = request.user.userdetails.fk_branch_id
            int_branch_to = request.data.get('intBranch')
            vchr_notes = request.data.get('remarks')
            int_po_id = request.data.get('orderId')
            int_fop = int(request.data.get('paymentType'))
            dat_pay_before = request.data.get('payBefore')
            dbl_total_amount = float(request.data.get('netAmt'))
            flt_addition = float(request.data.get('fltAddition',0.0))
            flt_deduction = float(request.data.get('fltDeduction',0.0))
            flt_roundoff = float(request.data.get('roundOff',0.0))
            str_bill_no = request.data.get('billNo')
            dat_bill = request.data.get('billDat')
            bln_igst = request.data.get('blnIgst')
            lst_item_details = json.loads(request.data['items'])
            dbl_bill_amount = float(request.data['billAmount'])
            if int_branch_id==int_branch_to:
                return Response({'status':0,'message':'Transfer not possible with same branches details'})

            if request.FILES.get('billImage'):
                img_bill_image = request.FILES.get('billImage')
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                vchr_bill_image = fs.save(img_bill_image.name, img_bill_image)
                vchr_bill_image_path = fs.url(vchr_bill_image)
            else:
                vchr_bill_image_path=''
            if int_fop == 1:
                int_fop = 0
            else:
                int_fop = 1
            lst_item_id = list(set([data['item_id'] for data in lst_item_details]))
            dct_imei_item = dict(Item.objects.filter(pk_bint_id__in=lst_item_id,imei_status=True).values_list('pk_bint_id','vchr_item_code'))
            dct_batch_item = dict(Item.objects.filter(pk_bint_id__in=lst_item_id,imei_status=False).values_list('pk_bint_id','vchr_item_code')) # taking items, which have bachcode(imei statusd = false), in a list
            lst_imei_check=[]
            lst_existing_imei = []
            for dct_data in lst_item_details:
                if dct_data['item_id'] in dct_imei_item:
                    if dct_data.get('lstImei'):
                        lst_imei = [data['imei'] for data in dct_data['lstImei']]
                        rst_imei_stock_data = BranchStockDetails.objects.filter(jsn_imei__imei__has_any_keys = lst_imei,fk_item__imei_status=True).values('jsn_imei')
                        if rst_imei_stock_data:
                            for ins_imei in rst_imei_stock_data:
                                lst_imei_check=lst_imei_check +list(set(ins_imei['jsn_imei']['imei']).intersection(set(lst_imei)))
                            dct_imei={}
                            dct_imei['item'] = dct_imei_item[dct_data['item_id']]
                            dct_imei['imei'] = lst_imei_check
                            lst_existing_imei.append(dct_imei)
                        rst_imei_grn_data = GrnDetails.objects.filter(jsn_imei__imei__has_any_keys = lst_imei,fk_item__imei_status=True).values('jsn_imei')
                        if rst_imei_grn_data:
                            for ins_imei in rst_imei_grn_data:
                                lst_imei_check=lst_imei_check +list(set(ins_imei['jsn_imei']['imei']).intersection(set(lst_imei)))
                            dct_imei={}
                            dct_imei['item'] = dct_imei_item[dct_data['item_id']]
                            dct_imei['imei'] = lst_imei_check
                            lst_existing_imei.append(dct_imei)
#block to check whether batch number is already present in the database
                elif dct_data['item_id'] in dct_batch_item:
                    if dct_data.get('vchr_batch_no'):
                        vchr_batch = dct_data.get('vchr_batch_no')
                        rst_batch_stock_data = BranchStockDetails.objects.filter(jsn_batch_no__batch__contains = vchr_batch,fk_item__imei_status=False).values('jsn_batch_no')
                        if rst_batch_stock_data:
                            # for ins_imei in rst_batch_stock_data:
                            #     vchr_batch_check=vchr_batch_check +list(set(ins_imei['jsn_imei']['imei']).intersection(set(vchr_batch)))
                            dct_batch={}
                            dct_batch['item'] = dct_batch_item[dct_data['item_id']]
                            dct_batch['imei'] = vchr_batch
                            lst_existing_imei.append(dct_batch)
                            continue
                        rst_batch_grn_data = GrnDetails.objects.filter(vchr_batch_no__iexact = vchr_batch,fk_item__imei_status=False).values('vchr_batch_no')
                        if rst_batch_grn_data:
                            # for ins_imei in rst_batch_grn_data:
                            #     vchr_batch_check=vchr_batch_check +list(set(ins_imei['jsn_imei']['imei']).intersection(set(vchr_batch)))
                            dct_batch={}
                            dct_batch['item'] = dct_batch_item[dct_data['item_id']]
                            dct_batch['imei'] = vchr_batch
                            lst_existing_imei.append(dct_batch)

###### end batch number duplicate check block 
            if lst_existing_imei:
                return Response({'status':2,'data':lst_existing_imei})
            
                

            with transaction.atomic():
                # ins_document = Document.objects.filter(vchr_module_name = 'GRN')
                # str_code = ins_document[0].vchr_short_code
                # int_doc_num = ins_document[0].int_number + 1
                # ins_document.update(int_number = int_doc_num)
                # str_number = str(int_doc_num).zfill(4)
                # str_purchase_no = str_code + '-' + str_number

                # LG 27-06-2020
                str_purchase_no = doc_num_generator('GRN',request.user.userdetails.fk_branch.pk_bint_id)
                if not str_purchase_no:
                    return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})
                ins_po = None
                if int_po_id:
                    ins_po = PoMaster.objects.get(vchr_po_num = int_po_id)

                lst_imei=[]
                lst_batch=[]
                for dct_item in lst_item_details:
                    if dct_item['lst_all_imei'] and dct_item['imei_status']:
                        # if len(dct_item['lst_all_imei']) == dct_item['int_qty']:
                        lst_imei.extend(dct_item['lst_all_imei'])
                        if None in dct_item['lst_all_imei']:
                            all_data = request.data
                            if all_data['billImage'] == 'undefined':
                                pass
                            else:
                                del all_data['billImage']
                            with open('imei_as_null_details.txt','a+') as file:
                                file.write('\n\n'+str(datetime.now())+'\n'+json.dumps(all_data))
                            raise ValueError('Something happened While execution')

                    if not dct_item['imei_status']:
                        lst_batch.append(dct_item['vchr_batch_no'])


                dct_filter_grn={
                                'fk_purchase__fk_branch_id':int_branch_id,
                                'fk_purchase__dat_created__contains' :datetime.now().date(),


                }
                lst_grn_details=GrnDetails.objects.filter(jsn_imei__imei__has_any_keys=lst_imei,**dct_filter_grn).values('jsn_imei')
                message = ''
                for imei in lst_grn_details:
                    for imei2 in lst_imei:
                        if imei2 in imei['jsn_imei']['imei']:
                            message +=str(imei2) +','
                message += ' imeis already purchased today'
                if lst_grn_details:
                    return Response({'status':0,'message':message,'bln_imei':True})

                lst_grn_details=GrnDetails.objects.filter(vchr_batch_no__in=lst_batch,**dct_filter_grn).values_list('vchr_batch_no',flat=True)
                message = ''
                if lst_grn_details and not request.data.get('bln_batch_pass'):
                    message += '{batch} batches already purchased'.format(batch = ','.join(set(lst_grn_details)))

                    return Response({'status':1,'message':message,'bln_batch':True})


                # ins_purchase = GrnMaster.objects.create_grnmaster_doc(str_purchase_no)
                ins_purchase = GrnMaster.objects.create(
                    dat_purchase = dat_purchase,
                    vchr_purchase_num = str_purchase_no,
                    fk_supplier_id = int_supplier_id,
                    fk_branch_id = int_branch_id,
                    fk_po = ins_po,
                    int_fop = int_fop,
                    dat_pay_before = dat_pay_before,
                    dbl_total = round(float(dbl_total_amount),2),
                    vchr_notes = vchr_notes,
                    fk_created_id = request.user.id,
                    dat_created = datetime.now(),
                    int_doc_status = 0,
                    dbl_addition = round(float(flt_addition),2),
                    dbl_deduction = round(float(flt_deduction),2),
                    dbl_roundoff_value = flt_roundoff,
                    int_approve = 2,
                    vchr_bill_no = str_bill_no,
                    dat_bill = dat_bill,
                    dbl_bill_amount =dbl_bill_amount,
                    vchr_bill_image = vchr_bill_image_path
                )
                ins_purchase.save()
                if int_branch_to:
                    # ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'STOCK TRANSFER')
                    # str_code = ins_document[0].vchr_short_code
                    vchr_branch_code_to = Branch.objects.get(pk_bint_id=int_branch_to).vchr_code
                    # if vchr_branch_code_to.upper() == 'AGY':
                    #     str_code = 'BB'
                    # int_doc_num = ins_document[0].int_number + 1
                    # ins_document.update(int_number = int_doc_num)
                    # str_number = str(int_doc_num).zfill(4)
                    # str_transfer_no = str_code + '-' +request.user.userdetails.fk_branch.vchr_code+'-'+ str_number

                    # LG 27-06-2020
                    if vchr_branch_code_to.upper() == 'AGY':
                        str_transfer_no = doc_num_generator('STOCK TRANSFER TO AGY',request.user.userdetails.fk_branch.pk_bint_id)
                    else:
                        str_transfer_no = doc_num_generator('STOCK TRANSFER',request.user.userdetails.fk_branch.pk_bint_id)

                    if not str_transfer_no:
                        return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                    ins_stocktransfer = StockTransfer.objects.create(
                        fk_from_id = int_branch_id, #changed
                        fk_to_id = int_branch_to,
                        vchr_stktransfer_num = str_transfer_no,
                        dat_transfer = datetime.strftime(datetime.now(),'%Y-%m-%d'),
                        vchr_remarks = vchr_notes,
                        fk_created_id = request.user.id,
                        dat_created = datetime.now(),
                        int_doc_status = 0,
                        int_status=0
                        )
                    ins_stocktransfer.save()

                lst_query_set = []
                for dct_item in lst_item_details:
                    ins_purchase_details = GrnDetails()
                    ins_purchase_details.fk_item_id = dct_item['item_id']
                    ins_purchase_details.int_qty = dct_item['int_qty']
                    ins_purchase_details.int_free = dct_item['free']
                    ins_purchase_details.int_avail = dct_item['int_qty']+dct_item['free']-dct_item['damageNum']
                    ins_purchase_details.int_damaged = dct_item['damageNum']
                    ins_purchase_details.dbl_ppu = round(float(dct_item['rate']),2)

                    ins_purchase_details.dbl_dscnt_percent = round(float(dct_item['disPer']),2)
                    ins_purchase_details.dbl_dscnt_perunit = round(float(dct_item['disPerUnit']),2)
                    ins_purchase_details.dbl_discount = round(float(dct_item['disAmt']),2)
                    if bln_igst:
                        dct_item['sgst'] = 0
                        dct_item['cgst'] = 0
                    else:
                        dct_item['igst'] = 0
                    ins_purchase_details.jsn_tax = {'SGST':(dct_item['rate']/100)*dct_item['sgst'],'CGST':(dct_item['rate']/100)*dct_item['cgst'],'IGST':(dct_item['rate']/100)*dct_item['igst'],'SGST%':dct_item['sgst'],'CGST%':dct_item['cgst'],'IGST%':dct_item['igst']}

                    flt_contrib = (float(dct_item['totAmt'])/(dbl_total_amount-flt_addition+flt_deduction))
                    flt_totalad_contrib = 0.0
                    flt_totaldd_contrib = 0.0
                    flt_per_piec_ad = 0.0
                    flt_per_piec_dd = 0.0
                    if flt_addition:
                        flt_totalad_contrib = flt_addition*flt_contrib
                        flt_per_piec_ad = round(float(flt_totalad_contrib/dct_item['int_qty']),2)

                    if flt_deduction:
                        flt_totaldd_contrib = flt_deduction*flt_contrib
                        flt_per_piec_dd = round(float(flt_totaldd_contrib/dct_item['int_qty']),2)

                    ins_purchase_details.dbl_perpie_aditn = flt_per_piec_ad
                    ins_purchase_details.dbl_perpie_dedctn = flt_per_piec_dd
                    ins_purchase_details.dbl_costprice = round(float(dct_item['rate'] - float(dct_item['disPerUnit']) + flt_per_piec_ad - flt_per_piec_dd),2)
                    ins_purchase_details.dbl_total_amount = round(float(float(dct_item['totAmt'])- flt_totaldd_contrib + flt_totalad_contrib),2)
                    ins_purchase_details.dbl_tax = ((dct_item['rate']/100)*dct_item['sgst']) + ((dct_item['rate']/100)*dct_item['cgst']) + ((dct_item['rate']/100)*dct_item['igst'])
                    str_imei = ''
                    lst_imei = []
                    lst_avail = []
                    lst_damage = []
                    if dct_item['lst_all_imei'] and dct_item['imei_status']:
                        lst_imei = dct_item['lst_all_imei']
                        lst_avail = dct_item['lst_all_imei']
                        # lst_damage = []
                        # ins_purchase_details.int_avail = len(lst_avail)
                        # ins_purchase_details.int_damaged = len(lst_damage)
                    ins_purchase_details.jsn_imei = {"imei":lst_imei}
                    ins_purchase_details.jsn_imei_avail = {"imei_avail":lst_avail}
                    ins_purchase_details.jsn_imei_dmgd = {"imei_damage":lst_damage}
                    ins_purchase_details.vchr_batch_no = dct_item['vchr_batch_no'] if not dct_item['imei_status'] else None
                    ins_purchase_details.fk_purchase_id = ins_purchase.pk_bint_id
                    ins_purchase_details.save()

                    if int_branch_to:
                        ins_st_details = IstDetails(
                        fk_item_id = dct_item['item_id'],
                        fk_transfer_id = ins_stocktransfer.pk_bint_id,
                        int_qty = ins_purchase_details.int_avail,
                        jsn_imei=ins_purchase_details.jsn_imei,
                        dbl_rate=Item.objects.get(pk_bint_id=dct_item['item_id']).dbl_mop or 0,
                        jsn_batch_no={"batch":[dct_item['vchr_batch_no']]} if not dct_item['imei_status'] else {"batch":[]}
                    )
                        ins_st_details.save()
                        ins_purchase_details.int_avail=0
                        ins_purchase_details.jsn_imei_avail={"imei_avail":[]}
                        ins_purchase_details.save()

                        ins_imei_details=StockTransferImeiDetails(
                            fk_details_id=ins_st_details.pk_bint_id,
                            fk_grn_details_id=ins_purchase_details.pk_bint_id,
                            int_qty = ins_st_details.int_qty,
                            jsn_imei=ins_st_details.jsn_imei,
                            jsn_batch_no=ins_st_details.jsn_batch_no
                            )
                        ins_imei_details.save()

                ins_sap_api = SapApiTrack.objects.create(int_document_id = ins_purchase.pk_bint_id,
                                            int_type = 15,
                                            int_status=0,
                                            dat_document = ins_purchase.dat_created)
                ins_sap_api.save()

                return Response({'status':'1','message':'Successfully saved'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})



class DirectTransferApi(APIView):
    """
    list and approve and view GNR list
    parameter : GnrId
    Response : Success and list
    """
    permission_classes = [IsAuthenticated]
    def put(self,request):
        try:
            dat_from=request.data.get('datFrom')
            dat_to=request.data.get('datTo')
            dct_filter={}
            if request.user.userdetails.fk_group.vchr_name =='ADMIN':
                pass
            else:
                dct_filter['fk_branch_id']=request.user.userdetails.fk_branch_id

            lst_gnr_details = []

            lst_changed_grn = list(set(GrnDetails.objects.filter(int_qty__gt=F('int_avail')).values_list('fk_purchase_id',flat=True)))
            lst_gnr_details = list(GrnMaster.objects.filter(dat_purchase__date__gte=dat_from,dat_purchase__date__lte=dat_to,**dct_filter).exclude(Q(int_doc_status__in = [-1,4])|Q(pk_bint_id__in=lst_changed_grn)).extra(select={'date_purchase':"to_char(grn_master.dat_purchase, 'DD-MM-YYYY')"}).values('pk_bint_id','vchr_purchase_num','date_purchase','dbl_total','fk_supplier__vchr_name','fk_branch__vchr_name','int_approve').order_by('-dat_purchase','-pk_bint_id'))
            return Response({'status':1,'data':lst_gnr_details})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


    def post(self,request):
        try:
            # import pdb;pdb.set_trace()
            int_purchase_id = request.data.get('intMasterId')
            rst_purchase = GrnDetails.objects.filter(fk_purchase_id = int(int_purchase_id)).\
            values('fk_purchase_id','fk_purchase__dat_purchase','fk_purchase__vchr_purchase_num','fk_purchase__fk_supplier__vchr_name','fk_purchase__fk_supplier_id','fk_purchase__fk_branch__vchr_name','fk_purchase__fk_branch__fk_states_id','fk_purchase__fk_branch_id',\
                    'fk_purchase__int_fop','fk_purchase__fk_po__vchr_po_num','fk_purchase__fk_po_id','fk_purchase__dat_pay_before',\
                    'fk_purchase__dbl_total','fk_purchase__vchr_notes','fk_purchase__dbl_addition','fk_purchase__dbl_deduction',\
                    'fk_purchase__dbl_roundoff_value','fk_purchase__vchr_bill_no','fk_purchase__dat_bill','fk_purchase__vchr_reject_reason',\
                    'fk_purchase__int_approve','fk_purchase__dbl_bill_amount','fk_purchase__vchr_bill_image','fk_item_id','fk_item__vchr_name','fk_item__imei_status','fk_item__vchr_item_code','int_qty','int_avail','int_free','int_damaged','dbl_costprice','dbl_dscnt_percent','dbl_dscnt_perunit','dbl_discount','jsn_tax','vchr_batch_no',\
                        'dbl_total_amount','vchr_batch_no','jsn_imei','jsn_imei_dmgd','dbl_perpie_aditn','dbl_perpie_dedctn','fk_item__fk_item_category__json_tax_master')
            dct_purchase = {}
            dct_purchase['lst_item'] = []
            dct_purchase['bln_transfer']=True
            for ins_item in rst_purchase:
                dct_item = {}
                if ins_item['int_qty'] != ins_item['int_avail']:
                    dct_purchase['bln_transfer']=False
                dct_item['item_id'] = ins_item['fk_item_id']
                dct_item['item_name'] = ins_item['fk_item__vchr_item_code'].upper()+'-'+ins_item['fk_item__vchr_name'].title()
                dct_item['int_qty'] = ins_item['int_qty']
                dct_item['int_free'] = ins_item['int_free']
                dct_item['int_damage'] = ins_item['int_damaged']
                dct_item['unit_price'] = ins_item['dbl_costprice']
                dct_item['discount_percent'] = ins_item['dbl_dscnt_percent']
                dct_item['discount_per_unit'] = ins_item['dbl_dscnt_perunit']
                dct_item['total_discount'] = ins_item['dbl_discount']
                dct_item['cgst'] = ins_item['jsn_tax']['CGST%'] if ins_item['jsn_tax'] else 0
                dct_item['sgst'] = ins_item['jsn_tax']['SGST%'] if ins_item['jsn_tax'] else 0
                dct_item['igst'] = 0
                dct_item['igst'] = ins_item['jsn_tax']['IGST%'] if ins_item['jsn_tax'] else 0
                dct_item['batch_num'] = ins_item['vchr_batch_no']
                dct_item['imei_status'] = ins_item['fk_item__imei_status']
                ins_item['dbl_perpie_aditn'] = ins_item['dbl_perpie_aditn'] if ins_item['dbl_perpie_aditn'] else 0
                ins_item['dbl_perpie_dedctn'] = ins_item['dbl_perpie_dedctn'] if ins_item['dbl_perpie_dedctn'] else 0
                dct_item['total_amount'] = round(ins_item['dbl_total_amount'] - (ins_item['dbl_perpie_aditn']*ins_item['int_qty']) + (ins_item['dbl_perpie_dedctn']*ins_item['int_qty']),2)
                dct_item['imei_damaged'] = []
                if ins_item['jsn_imei']:
                    dct_item['imei'] = ins_item['jsn_imei']['imei']
                if ins_item['jsn_imei_dmgd']:
                    dct_item['imei_damaged'] = ins_item['jsn_imei_dmgd']['imei_damage']


                dct_purchase['lst_item'].append(dct_item)

            if dct_purchase['lst_item']:
                dct_purchase['purchase_id'] = ins_item['fk_purchase_id']
                dct_purchase['purchase_num'] = ins_item['fk_purchase__vchr_purchase_num']
                dct_purchase['supplier_id'] = ins_item['fk_purchase__fk_supplier_id']
                dct_purchase['supplier_name'] = ins_item['fk_purchase__fk_supplier__vchr_name']
                dct_purchase['branch_id'] = ins_item['fk_purchase__fk_branch_id']
                dct_purchase['branch_name'] = ins_item['fk_purchase__fk_branch__vchr_name']
                dct_purchase['branch_state_id'] = ins_item['fk_purchase__fk_branch__fk_states_id']
                dct_purchase['supplier_state_id'] = ins_item['fk_purchase__fk_branch__fk_states_id']
                dct_purchase['dbl_bill_amount'] = ins_item['fk_purchase__dbl_bill_amount']
                dct_purchase['vchr_bill_image'] = ins_item['fk_purchase__vchr_bill_image']
                rst_supplier_state = AddressSupplier.objects.filter(fk_supplier_id=ins_item['fk_purchase__fk_supplier_id']).values('fk_states_id')
                if rst_supplier_state and rst_supplier_state[0]['fk_states_id']:
                    dct_purchase['supplier_state_id'] = rst_supplier_state[0]['fk_states_id']
                dct_purchase['dat_purchase'] = datetime.strftime(ins_item['fk_purchase__dat_purchase'],'%d-%m-%Y')
                dct_purchase['vchr_notes'] = ins_item['fk_purchase__vchr_notes']
                dct_purchase['fk_po_id'] = ins_item['fk_purchase__fk_po_id']
                dct_purchase['fk_po_num'] = ins_item['fk_purchase__fk_po__vchr_po_num']
                dct_purchase['int_fop'] = ins_item['fk_purchase__int_fop']
                if ins_item['fk_purchase__dat_pay_before']:
                    dct_purchase['dat_pay_before'] = datetime.strftime(ins_item['fk_purchase__dat_pay_before'],'%d-%m-%Y')
                dct_purchase['dbl_total'] = ins_item['fk_purchase__dbl_total']
                dct_purchase['dbl_addition'] = ins_item['fk_purchase__dbl_addition']
                dct_purchase['dbl_deduction'] = ins_item['fk_purchase__dbl_deduction']
                dct_purchase['dbl_roundoff_value'] = ins_item['fk_purchase__dbl_roundoff_value']
                dct_purchase['int_approve'] = ins_item['fk_purchase__int_approve']
                dct_purchase['bill_no'] = ins_item['fk_purchase__vchr_bill_no']

                if ins_item['fk_purchase__dat_bill']:
                    dct_purchase['bill_date'] = datetime.strftime(ins_item['fk_purchase__dat_bill'],'%d-%m-%Y')
                dct_purchase['reason'] = ins_item['fk_purchase__vchr_reject_reason']
                # fk_purchase__vchr_bill_no

            return Response({'status':1,'dct_purchase':dct_purchase})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

    def patch(self,request):
        try:
            int_branch_id = request.data.get('intBranchId')
            int_master_id = request.data.get('purchase_id')
            rst_purchase = GrnDetails.objects.filter(fk_purchase_id = int_master_id).\
            values('fk_purchase__fk_branch_id','fk_purchase__fk_branch_id__vchr_code','fk_purchase__vchr_notes','fk_item_id','int_avail','dbl_costprice',\
                    'vchr_batch_no','jsn_imei','pk_bint_id','int_avail')
            if not rst_purchase:
                return Response({"status":0,'message':'No data found'})
            with transaction.atomic():
                int_master=rst_purchase[0]
                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'STOCK TRANSFER')
                # str_code = ins_document[0].vchr_short_code
                vchr_branch_code_to = Branch.objects.get(pk_bint_id=int_branch_id).vchr_code
                # if vchr_branch_code_to.upper() == 'AGY':
                #     str_code = 'BB'
                # int_doc_num = ins_document[0].int_number + 1
                # ins_document.update(int_number = int_doc_num)
                # str_number = str(int_doc_num).zfill(4)
                # str_transfer_no = str_code + '-' +int_master['fk_purchase__fk_branch_id__vchr_code']+'-'+ str_number

                # LG 27-06-2020
                if vchr_branch_code_to.upper() == 'AGY':
                    str_transfer_no = doc_num_generator('STOCK TRANSFER TO AGY',request.user.userdetails.fk_branch.pk_bint_id)
                else:
                    str_transfer_no = doc_num_generator('STOCK TRANSFER',request.user.userdetails.fk_branch.pk_bint_id)


                if not str_transfer_no:
                    return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                lst_imei_validation=[]
                lst_batch_validation=[]
                lst_item_id=[]

                for dct_item in rst_purchase:


                    if dct_item.get('jsn_imei'):

                        lst_imei_validation.extend(dct_item.get('jsn_imei')['imei'])

                    if dct_item['vchr_batch_no']:
                        lst_batch_validation.append(dct_item['vchr_batch_no'])
                        lst_item_id.append(dct_item.get('fk_item_id'))


                lst_transfer_imei=IstDetails.objects.filter(jsn_imei__imei__has_any_keys=lst_imei_validation,fk_transfer__fk_from_id = int_master['fk_purchase__fk_branch_id'],fk_transfer__fk_to_id=int_branch_id,fk_transfer__int_status__in=[0,1]).values('fk_transfer__fk_to__vchr_name','jsn_imei')

                # message=''
                # for qry_set in lst_transfer_imei:
                #     for imei2 in lst_imei_validation:
                #         if imei2 in qry_set['jsn_imei']['imei']:
                #             message += imei2 +' imei '+', already transfered to '+qry_set['fk_transfer__fk_to__vchr_name']
                #
                # dct_show={}
                # for qry_set in lst_transfer_imei:
                #     for imei2 in lst_imei_validation:
                #         if imei2 in qry_set['jsn_imei']['imei']:
                #                 if qry_set['fk_transfer__fk_to__vchr_name'] not in dct_show:
                #                     dct_show[qry_set['fk_transfer__fk_to__vchr_name']] =imei2
                #                 else:
                #                     dct_show[qry_set['fk_transfer__fk_to__vchr_name']] +=', ' +imei2
                #
                # for key in dct_show:
                #     message +=dct_show[key] +' imeis transfered to branch '+key+' '


                if lst_transfer_imei:
                    return Response({'status':0,'message':'Imeis transfered to '+lst_transfer_imei[0]['fk_transfer__fk_to__vchr_name'],'bln_imei':True})


                lst_transfer_batch=IstDetails.objects.filter(jsn_batch_no__batch__has_any_keys=lst_batch_validation,fk_item_id__in=lst_item_id,fk_transfer__fk_from_id = int_master['fk_purchase__fk_branch_id'],fk_transfer__fk_to_id=int_branch_id,fk_transfer__int_status__in=[0,1],fk_transfer_id__dat_created__contains=datetime.today().date()).values('fk_transfer__fk_to__vchr_name','jsn_batch_no')


                # lst_transfer_batch=IstDetails.objects.filter(jsn_batch_no__batch__has_any_keys=lst_batch_validation,fk_item_id__in=lst_item_id,fk_transfer__fk_from_id = int_master['fk_purchase__fk_branch_id'],fk_transfer__int_status__in=[0,1]).values('fk_transfer__fk_to__vchr_name','jsn_batch_no')
                # message = ''
                # dct_show={}
                # for qry_set in lst_transfer_batch:
                #     for batch2 in lst_batch_validation:
                #         if batch2 in qry_set['jsn_batch_no']['batch']:
                #                 if qry_set['fk_transfer__fk_to__vchr_name'] not in dct_show:
                #                     dct_show[qry_set['fk_transfer__fk_to__vchr_name']] =batch2
                #                 else:
                #                     dct_show[qry_set['fk_transfer__fk_to__vchr_name']] +=', ' +batch2
                #
                # for key in dct_show:
                #     message +=dct_show[key] +' batches transfered to branch '+key+' '
                if lst_transfer_batch and not request.data.get('bln_batch_pass'):
                    return Response({'status':1,'data':'Batch transfered to '+lst_transfer_batch[0]['fk_transfer__fk_to__vchr_name'],'bln_batch':True})




                ins_stocktransfer = StockTransfer.objects.create(
                    fk_from_id = int_master['fk_purchase__fk_branch_id'], #changed
                    fk_to_id = int_branch_id,
                    vchr_stktransfer_num = str_transfer_no,
                    dat_transfer = datetime.strftime(datetime.now(),'%Y-%m-%d'),
                    vchr_remarks = int_master['fk_purchase__vchr_notes'],
                    fk_created_id = request.user.id,
                    dat_created = datetime.now(),
                    int_doc_status = 0,
                    int_status=0,
                    bln_direct_transfer = True
                    )
                ins_stocktransfer.save()
                for ins_item in rst_purchase:

                    ins_st_details = IstDetails(
                        fk_item_id = ins_item['fk_item_id'],
                        fk_transfer_id = ins_stocktransfer.pk_bint_id,
                        int_qty = ins_item['int_avail'],
                        jsn_imei=ins_item['jsn_imei'],
                        dbl_rate=Item.objects.get(pk_bint_id=ins_item['fk_item_id']).dbl_mop or 0,
                        jsn_batch_no={"batch":([ins_item['vchr_batch_no']] if ins_item['vchr_batch_no'] else [])}
                    )
                    ins_st_details.save()

                    ins_imei_details=StockTransferImeiDetails(
                        fk_details_id=ins_st_details.pk_bint_id,
                        fk_grn_details_id=ins_item['pk_bint_id'],
                        int_qty = ins_st_details.int_qty,
                        jsn_imei=ins_st_details.jsn_imei,
                        jsn_batch_no=ins_st_details.jsn_batch_no
                        )
                    ins_imei_details.save()
                GrnDetails.objects.filter(fk_purchase_id = int_master_id).update(
                    int_avail=0,
                    jsn_imei_avail={"imei_avail":[]}
                )
                return Response({'status':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


class ItemSpareTypeahead(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_items = []
            ins_grn_items =[]
            tax_name = dict(TaxMaster.objects.values_list('pk_bint_id','vchr_name'))
            if str_search_term != -1:
                ins_items = Item.objects.filter(Q(vchr_name__icontains=str_search_term)\
                    | Q(vchr_item_code__icontains=str_search_term),int_status = 0,fk_product__vchr_name__in=['SPARE','GDP-SPARE']).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master','imei_status','dbl_mop','fk_product_id','fk_brand_id','fk_product__vchr_name', 'fk_brand__vchr_name')
                if ins_items:
                    if request.data.get('intProduct'):
                        ins_items=ins_items.filter(fk_product_id=request.data.get('intProduct'))
                    if request.data.get('intBrand'):
                        ins_items=ins_items.filter(fk_brand_id=request.data.get('intBrand'))

                    for itr_item in ins_items[:20]:
                        dct_item = {}
                        # dct_item['code'] = itr_item['vchr_code'].upper()
                        dct_item['name'] = itr_item['vchr_item_code'].upper()+'-'+itr_item['vchr_name'].title()
                        dct_item['id'] = itr_item['pk_bint_id']
                        dct_item['rate']=itr_item['dbl_mop']
                        dct_item['product_id']=itr_item['fk_product_id']
                        dct_item['product_name']=itr_item['fk_product__vchr_name']
                        dct_item['brand_id']=itr_item['fk_brand_id']
                        dct_item['brand_name']=itr_item['fk_brand__vchr_name']
                        if  itr_item['fk_item_category__json_tax_master']:
                            dct_item['jsn_tax']={}
                            for ins_tax in itr_item['fk_item_category__json_tax_master']:
                                # dct_item['jsn_tax'][ins_tax] ={}
                                dct_item['jsn_tax'][tax_name[int(ins_tax)]] =  itr_item['fk_item_category__json_tax_master'][ins_tax]
                        else:
                            dct_item['jsn_tax']=0
                        dct_item['imei_status']=itr_item['imei_status']
                        ins_stock_quantity = BranchStockDetails.objects.filter(fk_item_id = itr_item['pk_bint_id'],fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_qty'))
                        ins_grn_quantity = []
                        # import pdb; pdb.set_trace()
                        if request.user.userdetails.fk_branch.int_type in[2,3]:
                            ins_grn_quantity = GrnDetails.objects.filter(fk_item_id = itr_item['pk_bint_id'],fk_purchase__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_avail'))

                        dct_item['item_qty']= (ins_stock_quantity[0]['int_Qty'] if ins_stock_quantity else 0) + (ins_grn_quantity[0]['int_Qty'] if ins_grn_quantity else 0)
                        lst_items.append(dct_item)
                    return Response({'status':'1','data':lst_items})
                else:
                    return Response({'status':'empty'})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})

# LG 27-06-2020
def doc_num_generator(module,branch_id):
    try:
        # LG
        # import pdb; pdb.set_trace()
        # with transaction.atomic():
        ins_document = Document.objects.select_for_update().filter(vchr_module_name = module,fk_branch_id = branch_id).first()
        if ins_document:
            str_doc_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
            Document.objects.filter(vchr_module_name = module,fk_branch_id = branch_id).update(int_number = ins_document.int_number+1)
            print(str_doc_num)
            return str_doc_num
        else:
            ins_document_search = Document.objects.filter(vchr_module_name = module,fk_branch_id = None).first()
            if ins_document_search:
                ins_branch_code = Branch.objects.filter(pk_bint_id = branch_id).values('vchr_code').first()['vchr_code']
                ins_document = Document.objects.create(vchr_module_name = module, int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = branch_id)
                str_doc_num = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                ins_document.int_number = ins_document.int_number+1
                ins_document.save()
                print(str_doc_num)
                return str_doc_num
            else:
                return False

    except Exception as e:
        print(e)
        return False
# LG 27-06-2020 class for testing only
class doc_num_generator1(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        with transaction.atomic():
            data = doc_num_generator('INVOICE',19)
        return Response({"data":data})
