from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.db.models import Q
from aldjemy.core import get_engine
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.db import transaction
from purchase.views import doc_num_generator
from bulk_update.helper import bulk_update
from django.db.models import CharField, Case, Value, When, Value,Sum,F, Q
import json
import sys
from POS import ins_logger

# Models
from branch.models import Branch
from branch_stock.models import BranchStockMaster,BranchStockDetails,BranchStockImeiDetails
from purchase.models import GrnDetails
from internal_stock.models import CourierMaster,IsrDetails,StockTransfer,IstDetails,TransferHistory,TransferModeDetails,StockTransferImeiDetails

class CourierData(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    def get(self,request):
        try:
            ins_courier=CourierMaster.objects.filter().values('pk_bint_id','vchr_name')
            return Response({'status':1, 'courier_name':ins_courier})
        except Exception as e:
            return Response({'status':0, 'message':'Data Not Availiable'})
class CourierVehicle(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_courier=request.data.get('courier_id')
            int_courier= 1
            ins_vehicle=CourierMaster.objects.filter(pk_bint_id=int_courier).values('json_vehicle_no','vchr_gst_no')
            if ins_vehicle:
                dict_data={}
                lst_vehicle=ins_vehicle.first()['json_vehicle_no']
            else:
                return Response ({'status':0,'message':'no data found'})
            return Response ({'status':1,'vehicle':lst_vehicle})

        except Exception as e:
            return Response ({'status':0,'message':str(e)})


# class to get the imei's availiable for branch's and warehouse's
class ImeiList(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:

            lst_data = []
            int_branch_id = request.user.userdetails.fk_branch_id or None
            int_item_id = request.data.get('intItem',None)
            # int_item_id = request.data.get('fk_item_id',None)

            if int_branch_id:
                ins_branch_type = Branch.objects.filter(pk_bint_id=request.user.userdetails.fk_branch_id).values('int_type').first()['int_type']
                # Checking the branch is warehouse,headoffice (2,3)or normal branch(1)
                # if normal branch conside only BranchStockImeiDetails else conside both BranchStockImeiDetails and grndetails
                # import pdb; pdb.set_trace()
                if ins_branch_type in [2,3]:
                    dct_data = {}
                    dct_data['lst_imei_data'] = []
                    dct_data['lst_imei'] = []
                    ins_imei = BranchStockImeiDetails.objects.filter(int_qty__gte = 1,fk_details__fk_master__fk_branch_id = int_branch_id,fk_details__fk_item_id = int_item_id).values('jsn_imei','fk_grn_details_id','fk_details__fk_master__dat_stock','pk_bint_id').order_by('-fk_details__fk_master__dat_stock')
                    if ins_imei:
                        for data  in ins_imei:
                            dct_imei={}
                            dct_imei['imei_age'] = (datetime.now() - data['fk_details__fk_master__dat_stock']).days
                            dct_imei['qty'] = len(data['jsn_imei']['imei'])
                            dct_imei['imei'] = data['jsn_imei']['imei']
                            dct_imei['id'] = data['fk_grn_details_id']
                            dct_imei['pk_id'] = data['pk_bint_id']

                            dct_data['lst_imei_data'].append(dct_imei)
                            dct_data['lst_imei'].extend(data['jsn_imei']['imei'])
                        
                    
                    ins_imei = GrnDetails.objects.filter(int_avail__gte=1,fk_purchase__fk_branch_id=request.user.userdetails.fk_branch_id,fk_item_id=int_item_id).values('jsn_imei_avail','pk_bint_id','fk_purchase__dat_purchase')
                    if ins_imei:
                        dct_imei={}
                        for data  in ins_imei:
                            dct_imei={}
                            # import pdb; pdb.set_trace()
                            dct_imei['imei_age'] = (datetime.now() - data['fk_purchase__dat_purchase']).days
                            dct_imei['qty'] = len(data['jsn_imei_avail']['imei_avail'])
                            dct_imei['imei'] = data['jsn_imei_avail']['imei_avail']
                            dct_imei['id'] = data['pk_bint_id']
                            dct_imei['pk_id'] = data['pk_bint_id']

                            dct_data['lst_imei_data'].append(dct_imei)
                            dct_data['lst_imei'].extend(data['jsn_imei_avail']['imei_avail'])
                    lst_data.append(dct_data)

                else:
                    dct_data = {}
                    dct_data['lst_imei_data'] = []
                    dct_data['lst_imei'] = []
                    ins_imei = BranchStockImeiDetails.objects.filter(int_qty__gte = 1,fk_details__fk_master__fk_branch_id = int_branch_id,fk_details__fk_item_id = int_item_id).values('jsn_imei','fk_grn_details_id','fk_details__fk_master__dat_stock','pk_bint_id').order_by('-fk_details__fk_master__dat_stock')
                    if ins_imei:
                        for data  in ins_imei:
                            dct_imei={}
                            # import pdb; pdb.set_trace()
                            dct_imei['imei_age'] = (datetime.now() - data['fk_details__fk_master__dat_stock']).days
                            dct_imei['qty'] = len(data['jsn_imei']['imei'])
                            dct_imei['imei'] = data['jsn_imei']['imei']
                            dct_imei['id'] = data['fk_grn_details_id']
                            dct_imei['pk_id'] = data['pk_bint_id']

                            dct_data['lst_imei_data'].append(dct_imei)
                            dct_data['lst_imei'].extend(data['jsn_imei']['imei'])
                    lst_data.append(dct_data)

            # import pdb; pdb.set_trace()          
            return Response({'status':1, 'data' :lst_data})

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0, 'reason' : 'no imei available'})
       
# class to get the batch's availiable for branch's and warehouse's 
class BatchList(APIView):
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:

            lst_data = []
            dct_data = {}
            int_branch_id = request.user.userdetails.fk_branch_id or None
            int_item_id = request.data.get('intItem',None)
            # int_item_id = request.data.get('fk_item_id',None)

            if int_branch_id:
                # Checking the branch is warehouse,headoffice (2,3)or normal branch(1)
                # if normal branch conside only BranchStockImeiDetails else conside both BranchStockImeiDetails and grndetails
                # import pdb; pdb.set_trace()
                if request.user.userdetails.fk_branch.int_type in [2,3]:
                    dct_data = {}
                    dct_data['lst_batch_data'] = []
                    dct_data['lst_batch'] = []
                    ins_batch = BranchStockImeiDetails.objects.filter(int_qty__gte = 1,fk_details__fk_master__fk_branch_id = int_branch_id,fk_details__fk_item_id = int_item_id).values('jsn_batch_no','fk_grn_details_id','fk_details__fk_master__dat_stock','int_qty','pk_bint_id').order_by('-fk_details__fk_master__dat_stock')
                    if ins_batch:
                        for data  in ins_batch:
                            dct_batch={}
                            dct_batch['batch_age'] = (datetime.now() - data['fk_details__fk_master__dat_stock']).days
                            dct_batch['qty'] = data['int_qty']
                            dct_batch['batch'] = data['jsn_batch_no']['batch']
                            dct_batch['id'] = data['fk_grn_details_id']
                            dct_batch['pk_id'] = data['pk_bint_id']
                            dct_batch['transfer_qty'] = 0

                            dct_data['lst_batch_data'].append(dct_batch)
                            dct_data['lst_batch'].extend(data['jsn_batch_no']['batch'])
                        
                    
                    ins_batch = GrnDetails.objects.filter(int_avail__gte=1,fk_purchase__fk_branch_id=request.user.userdetails.fk_branch_id,fk_item_id=int_item_id).values('vchr_batch_no','pk_bint_id','fk_purchase__dat_purchase','int_avail')
                    if ins_batch:
                        dct_batch={}
                        for data  in ins_batch:
                            dct_batch={}
                            # import pdb; pdb.set_trace()
                            dct_batch['batch_age'] = (datetime.now() - data['fk_purchase__dat_purchase']).days
                            dct_batch['qty'] = data['int_avail']
                            dct_batch['batch'] = [data['vchr_batch_no']]
                            dct_batch['id'] = data['pk_bint_id']
                            dct_batch['pk_id'] = data['pk_bint_id']
                            dct_batch['transfer_qty'] = 0

                            dct_data['lst_batch_data'].append(dct_batch)
                            dct_data['lst_batch'].append(data['vchr_batch_no'])
                    lst_data.append(dct_data)

                else:
                    dct_data = {}
                    dct_data['lst_batch_data'] = []
                    dct_data['lst_batch'] = []
                    ins_batch = BranchStockImeiDetails.objects.filter(int_qty__gte = 1,fk_details__fk_master__fk_branch_id = int_branch_id,fk_details__fk_item_id = int_item_id).values('jsn_batch_no','fk_grn_details_id','fk_details__fk_master__dat_stock','int_qty','pk_bint_id').order_by('-fk_details__fk_master__dat_stock')
                    if ins_batch:
                        for data  in ins_batch:
                            dct_batch={}
                            # import pdb; pdb.set_trace()
                            dct_batch['batch_age'] = (datetime.now() - data['fk_details__fk_master__dat_stock']).days
                            dct_batch['qty'] = data['int_qty']
                            dct_batch['batch'] = data['jsn_batch_no']['batch']
                            dct_batch['id'] = data['fk_grn_details_id']
                            dct_batch['pk_id'] = data['pk_bint_id']
                            dct_batch['transfer_qty'] = 0

                            dct_data['lst_batch_data'].append(dct_batch)
                            dct_data['lst_batch'].extend(data['jsn_batch_no']['batch'])
                    lst_data.append(dct_data)

            # import pdb; pdb.set_trace()          
            return Response({'status':1, 'data' :dct_data})

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0, 'reason' : 'no batch available'})

class saveStockTransfer(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                # import pdb; pdb.set_trace()
                lst_item_details = request.data.get('lst_items',[])
                bln_trans_status = 1
                trans_vechile_no = ''

                vchr_branch_code = request.user.userdetails.fk_branch.vchr_code
                vchr_branch_code_to = Branch.objects.filter(vchr_name = request.data.get('toBranch','')).values('vchr_code').first()['vchr_code']
                int_branch_to = Branch.objects.filter(vchr_name = request.data.get('toBranch','')).values('pk_bint_id').first()['pk_bint_id']

                if vchr_branch_code_to.upper() == 'AGY':
                    str_transfer_no = doc_num_generator('STOCK TRANSFER TO AGY',request.user.userdetails.fk_branch.pk_bint_id)
                    if not str_transfer_no:
                        return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})
                else:
                    str_transfer_no = doc_num_generator('STOCK TRANSFER',request.user.userdetails.fk_branch.pk_bint_id)
                    if not str_transfer_no:
                        return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                if not request.data.get('bln_transfer'):
                # if True == False:
                    bln_trans_status = 0
                else:
                    trans_vechile_no = request.data.get('strVehicleNo')


                ins_stocktransfer = StockTransfer.objects.create(
                    fk_from_id = request.user.userdetails.fk_branch.pk_bint_id, #changed
                    fk_to_id = int_branch_to,
                    vchr_stktransfer_num = str_transfer_no,
                    dat_transfer =datetime.strftime(datetime.now(),'%Y-%m-%d'),
                    vchr_remarks = request.data.get('remarks'),
                    fk_created_id = request.user.id,
                    dat_created = datetime.now(),
                    fk_updated_id = request.user.id,
                    dat_updated = datetime.now(),
                    int_doc_status = 0,
                    vchr_vehicle_num=trans_vechile_no,
                    int_status = bln_trans_status
                )
                ins_stocktransfer.save()
                # import pdb; pdb.set_trace()
                int_type=Branch.objects.filter(pk_bint_id=request.user.userdetails.fk_branch_id).values('int_type').first()['int_type']
                if int_type in [2,3]:

                    dct_stocktransferimeidetails_data = {}
                    for dct_item in lst_item_details:
                        # import pdb; pdb.set_trace()
                        dct_stocktransferimeidetails_data = {}
                        lst_imei_transfer = []
                        if dct_item['bln_imei']:

                            for data in dct_item['lstItemImei']:
                                if GrnDetails.objects.filter(Q(jsn_imei_avail__imei_avail__has_any_keys=[data['imei']]),pk_bint_id=data['grn_id']).values():
                                    lst_left_imei=list(set(set(GrnDetails.objects.filter(pk_bint_id=data['grn_id']).values().first()['jsn_imei_avail']['imei_avail'])-set([data['imei']])))
                                    GrnDetails.objects.filter(pk_bint_id=data['grn_id']).update(jsn_imei_avail={'imei_avail':lst_left_imei},int_avail=len(lst_left_imei))

                                else:
                                    lst_branch_stock_id = BranchStockImeiDetails.objects.filter(jsn_imei__imei__has_any_keys=[data['imei']])
                                    if lst_branch_stock_id:
                                        bln_imei_avail = True
                                        for ins_data in lst_branch_stock_id:
                                            ins_data.jsn_imei['imei']=list(set(ins_data.jsn_imei['imei'])-(set([data['imei']]) & set(ins_data.jsn_imei['imei'])))
                                            ins_data.int_qty=len(list(set(ins_data.jsn_imei['imei'])-(set([data['imei']]) & set(ins_data.jsn_imei['imei']))))

                                            lst_br_stock = BranchStockDetails.objects.filter(Q(jsn_imei_avail__imei__has_any_keys = [data['imei']]),fk_item_id=dct_item.get('item_id'),pk_bint_id = ins_data.fk_details_id)
                                            if lst_br_stock:
                                                bln_imei_avail = False
                                                for ins_data1 in lst_br_stock:
                                                    ins_data1.jsn_imei_avail['imei']=list(set(ins_data1.jsn_imei_avail['imei'])-(set([data['imei']])) & set(ins_data1.jsn_imei_avail['imei']))
                                                    ins_data1.int_qty=len(list(set(ins_data1.jsn_imei_avail['imei'])-(set([data['imei']])) & set(ins_data1.jsn_imei_avail['imei'])))
                                                bulk_update(lst_br_stock)
                                        if bln_imei_avail:
                                            raise ValueError('This imei('+data['imei']+') is not availiable')
                                        bulk_update(lst_branch_stock_id)
                                    else:
                                        raise ValueError('This imei('+data['imei']+') is not availiable')

                                if dct_stocktransferimeidetails_data.get(data['grn_id']) == None:
                                    dct_stocktransferimeidetails_data[data['grn_id']] = {}
                                    dct_stocktransferimeidetails_data[data['grn_id']]['int_qty'] = 1
                                    dct_stocktransferimeidetails_data[data['grn_id']]['jsn_imei'] = []
                                    dct_stocktransferimeidetails_data[data['grn_id']]['jsn_batch_no'] = []
                                    dct_stocktransferimeidetails_data[data['grn_id']]['jsn_imei'].extend([data['imei']])
                                else:
                                    dct_stocktransferimeidetails_data[data['grn_id']]['int_qty'] += 1
                                    dct_stocktransferimeidetails_data[data['grn_id']]['jsn_imei'].extend([data['imei']])
                                lst_imei_transfer.extend([data['imei']])

                            ins_st_details = IstDetails(
                                fk_item_id = dct_item.get('item_id'),
                                fk_transfer_id = ins_stocktransfer.pk_bint_id,
                                int_qty = dct_item['int_qty'],
                                jsn_imei={"imei":lst_imei_transfer},
                                dbl_rate=dct_item['rate'],
                                jsn_batch_no={"batch":[]}
                            )
                            ins_st_details.save()
                            for grnid,data in dct_stocktransferimeidetails_data.items():
                                ins_stocktransferimei=StockTransferImeiDetails(
                                    fk_details_id=ins_st_details.pk_bint_id,
                                    fk_grn_details_id= int(grnid),
                                    int_qty = data['int_qty'],
                                    jsn_imei={"imei":data['jsn_imei']},
                                    jsn_batch_no={"batch":data['jsn_batch_no']}
                                )
                                # import pdb; pdb.set_trace()
                                ins_stocktransferimei.save()
                                

                        else:
                            for data in dct_item['lstItemTabBatch']:
                                if data['transfer_qty'] > 0:
                                    if data['id'] == data['pk_id']:
                                        ins_grn=GrnDetails.objects.filter(pk_bint_id=data['id'],int_avail__gt=0).values('pk_bint_id','int_avail')
                                        if ins_grn:
                                            if ins_grn[0]['int_avail']>=data['transfer_qty']:
                                                GrnDetails.objects.filter(pk_bint_id=ins_grn[0]['pk_bint_id']).update(int_avail=(ins_grn[0]['int_avail']-data['transfer_qty']))
                                            else:
                                                raise ValueError('The batch number('+str(data['batch'])+') is not available now.')
                                        else:
                                            raise ValueError('The batch number('+str(data['batch'])+') is not available now.')
                                    else:
                                        ins_branch_stock=BranchStockImeiDetails.objects.filter(fk_grn_details_id= data['id'],int_qty__gt=0,fk_details__fk_master_id__fk_branch_id=request.user.userdetails.fk_branch_id,pk_bint_id = data['pk_id']).values('pk_bint_id','int_qty','fk_details_id')
                                        if ins_branch_stock:
                                            for ins_batch_stock in ins_branch_stock:
                                                if ins_batch_stock['int_qty']>=data['transfer_qty']:
                                                    BranchStockImeiDetails.objects.filter(pk_bint_id=ins_batch_stock['pk_bint_id'],jsn_batch_no__contains={'batch':[data['batch'][0]]}).update(int_qty=F('int_qty')-data['transfer_qty'])
                                                    BranchStockDetails.objects.filter(pk_bint_id=ins_batch_stock['fk_details_id']).update(int_qty=F('int_qty')-data['transfer_qty'])
                                                else:
                                                    raise ValueError('The batch number('+str(data['batch'])+') is not available now.')
                                        else:
                                            raise ValueError('The batch number('+str(data['batch'])+') is not available now.')

                                    if dct_stocktransferimeidetails_data.get(data['id']) == None:
                                        dct_stocktransferimeidetails_data[data['id']] = {}
                                        dct_stocktransferimeidetails_data[data['id']]['int_qty'] = data['transfer_qty']
                                        dct_stocktransferimeidetails_data[data['id']]['jsn_imei'] = []
                                        dct_stocktransferimeidetails_data[data['id']]['jsn_batch_no'] = []
                                        dct_stocktransferimeidetails_data[data['id']]['jsn_batch_no'].extend(data['batch'])
                                    else:
                                        dct_stocktransferimeidetails_data[data['id']]['int_qty'] += data['transfer_qty']
                                        dct_stocktransferimeidetails_data[data['id']]['jsn_batch_no'].extend(data['batch'])
                            # import pdb; pdb.set_trace()
                            for grnid,data in dct_stocktransferimeidetails_data.items():
                                
                                ins_st_details = IstDetails(
                                    fk_item_id = dct_item.get('item_id'),
                                    fk_transfer_id = ins_stocktransfer.pk_bint_id,
                                    int_qty = data['int_qty'],
                                    jsn_imei={"imei":data['jsn_imei']},
                                    dbl_rate=dct_item['rate'],
                                    jsn_batch_no={"batch":list(set(data['jsn_batch_no']))}
                                )
                                ins_st_details.save()

                                ins_stocktransferimei=StockTransferImeiDetails(
                                    fk_details_id=ins_st_details.pk_bint_id,
                                    fk_grn_details_id= int(grnid),
                                    int_qty = data['int_qty'],
                                    jsn_imei={"imei":data['jsn_imei']},
                                    jsn_batch_no={"batch":list(set(data['jsn_batch_no']))}
                                )
                                # import pdb; pdb.set_trace()
                                ins_stocktransferimei.save()
                else:
                    # import pdb; pdb.set_trace()
                    for dct_item in lst_item_details:
                        dct_stocktransferimeidetails_data = {}
                        lst_imei_transfer = []
                        if dct_item['bln_imei']:
                            for data in dct_item['lstItemImei']:
                                lst_branch_stock_id = BranchStockImeiDetails.objects.filter(jsn_imei__imei__has_any_keys=[data['imei']])
                                if lst_branch_stock_id:
                                    bln_imei_avail = True
                                    for ins_data in lst_branch_stock_id:
                                        ins_data.jsn_imei['imei']=list(set(ins_data.jsn_imei['imei'])-(set([data['imei']]) & set(ins_data.jsn_imei['imei'])))
                                        ins_data.int_qty=len(list(set(ins_data.jsn_imei['imei'])-(set([data['imei']]) & set(ins_data.jsn_imei['imei']))))
                                        lst_br_stock = BranchStockDetails.objects.filter(Q(jsn_imei_avail__imei__has_any_keys = [data['imei']]),fk_item_id=dct_item.get('item_id'),pk_bint_id = ins_data.fk_details_id)
                                        if lst_br_stock:
                                            bln_imei_avail = False
                                            for ins_data1 in lst_br_stock:
                                                ins_data1.jsn_imei_avail['imei']=list(set(ins_data1.jsn_imei_avail['imei'])-(set([data['imei']])) & set(ins_data1.jsn_imei_avail['imei']))
                                                ins_data1.int_qty=len(list(set(ins_data1.jsn_imei_avail['imei'])-(set([data['imei']])) & set(ins_data1.jsn_imei_avail['imei'])))
                                            bulk_update(lst_br_stock)
                                    if bln_imei_avail:
                                        raise ValueError('This imei('+data['imei']+') is not availiable')
                                    bulk_update(lst_branch_stock_id)
                                else:
                                    raise ValueError('This imei('+data['imei']+') is not availiable') 

                                if dct_stocktransferimeidetails_data.get(data['grn_id']) == None:
                                    dct_stocktransferimeidetails_data[data['grn_id']] = {}
                                    dct_stocktransferimeidetails_data[data['grn_id']]['int_qty'] = 1
                                    dct_stocktransferimeidetails_data[data['grn_id']]['jsn_imei'] = []
                                    dct_stocktransferimeidetails_data[data['grn_id']]['jsn_batch_no'] = []
                                    dct_stocktransferimeidetails_data[data['grn_id']]['jsn_imei'].extend([data['imei']])
                                else:
                                    dct_stocktransferimeidetails_data[data['grn_id']]['int_qty'] += 1
                                    dct_stocktransferimeidetails_data[data['grn_id']]['jsn_imei'].extend([data['imei']])
                                lst_imei_transfer.extend([data['imei']])


                            ins_st_details = IstDetails(
                                fk_item_id = dct_item.get('item_id'),
                                fk_transfer_id = ins_stocktransfer.pk_bint_id,
                                int_qty = dct_item['int_qty'],
                                jsn_imei={"imei":lst_imei_transfer},
                                dbl_rate=dct_item['rate'],
                                jsn_batch_no={"batch":[]}
                            )
                            ins_st_details.save()
                            for grnid,data in dct_stocktransferimeidetails_data.items():
                                ins_stocktransferimei=StockTransferImeiDetails(
                                    fk_details_id=ins_st_details.pk_bint_id,
                                    fk_grn_details_id= int(grnid),
                                    int_qty = data['int_qty'],
                                    jsn_imei={"imei":data['jsn_imei']},
                                    jsn_batch_no={"batch":data['jsn_batch_no']}
                                )
                                # import pdb; pdb.set_trace()
                                ins_stocktransferimei.save()

                        else:
                            for data in dct_item['lstItemTabBatch']:
                                if data['transfer_qty'] > 0:
                                    ins_branch_stock=BranchStockImeiDetails.objects.filter(fk_grn_details_id= data['id'],int_qty__gt=0,fk_details__fk_master_id__fk_branch_id=request.user.userdetails.fk_branch_id,pk_bint_id = data['pk_id']).values('pk_bint_id','int_qty','fk_details_id')
                                    if ins_branch_stock:
                                        for ins_batch_stock in ins_branch_stock:
                                            if ins_batch_stock['int_qty']>=data['transfer_qty']:
                                                BranchStockImeiDetails.objects.filter(pk_bint_id=ins_batch_stock['pk_bint_id'],jsn_batch_no__contains={'batch':[data['batch'][0]]}).update(int_qty=F('int_qty')-data['transfer_qty'])
                                                BranchStockDetails.objects.filter(pk_bint_id=ins_batch_stock['fk_details_id']).update(int_qty=F('int_qty')-data['transfer_qty'])
                                            else:
                                                raise ValueError('The batch number('+str(data['batch'])+') is not available now.')
                                    else:
                                        raise ValueError('The batch number('+str(data['batch'])+') is not available now.')

                                    if dct_stocktransferimeidetails_data.get(data['id']) == None:
                                        dct_stocktransferimeidetails_data[data['id']] = {}
                                        dct_stocktransferimeidetails_data[data['id']]['int_qty'] = data['transfer_qty']
                                        dct_stocktransferimeidetails_data[data['id']]['jsn_imei'] = []
                                        dct_stocktransferimeidetails_data[data['id']]['jsn_batch_no'] = []
                                        dct_stocktransferimeidetails_data[data['id']]['jsn_batch_no'].extend(data['batch'])
                                    else:
                                        dct_stocktransferimeidetails_data[data['id']]['int_qty'] += data['transfer_qty']
                                        dct_stocktransferimeidetails_data[data['id']]['jsn_batch_no'].extend(data['batch'])

                            for grnid,data in dct_stocktransferimeidetails_data.items():
                                # import pdb; pdb.set_trace()
                                ins_st_details = IstDetails(
                                    fk_item_id = dct_item.get('item_id'),
                                    fk_transfer_id = ins_stocktransfer.pk_bint_id,
                                    int_qty = data['int_qty'],
                                    jsn_imei={"imei":data['jsn_imei']},
                                    dbl_rate=dct_item['rate'],
                                    jsn_batch_no={"batch":list(set(data['jsn_batch_no']))}
                                )
                                ins_st_details.save()

                                ins_stocktransferimei=StockTransferImeiDetails(
                                    fk_details_id=ins_st_details.pk_bint_id,
                                    fk_grn_details_id= int(grnid),
                                    int_qty = data['int_qty'],
                                    jsn_imei={"imei":data['jsn_imei']},
                                    jsn_batch_no={"batch":list(set(data['jsn_batch_no']))}
                                )
                                # import pdb; pdb.set_trace()
                                ins_stocktransferimei.save()
                                
                if bln_trans_status == 1:
                    ins_tr_details = TransferModeDetails(
                        int_medium = request.data.get('transportType'),
                        fk_transfer_id = ins_stocktransfer.pk_bint_id,
                        vchr_name_responsible=request.data.get('strMediumName'),
                        bnt_contact_number = request.data.get('strMediumPhNo'),
                        bnt_number=request.data.get('strMediumNo'),
                        int_packet_no=request.data.get('intPackets'),
                        dbl_expense=request.data.get('dblExpense'),
                        fk_created_id = request.user.id,
                        dat_created = datetime.now(),
                        fk_updated_id = request.user.id,
                        dat_updated = datetime.now(),
                        int_doc_status = 0,
                        fk_courier_id=request.data.get('intCourierId')

                    )
                    ins_tr_details.save()
                    ins_th_details = TransferHistory(
                        vchr_status = 'TRANSFERRED',
                        fk_transfer_id = ins_stocktransfer.pk_bint_id,
                        fk_created_id = request.user.id,
                        dat_created = datetime.now(),
                        fk_updated_id = request.user.id,
                        dat_updated = datetime.now(),
                        int_doc_status = 0,
                    )
                    ins_th_details.save()
                

                # import pdb; pdb.set_trace()
                rst_transfer_qty=StockTransferImeiDetails.objects.filter(fk_details__fk_transfer_id=ins_stocktransfer.pk_bint_id).aggregate(inserted_qty=Sum('int_qty'))
                if not rst_transfer_qty or not rst_transfer_qty['inserted_qty'] or rst_transfer_qty['inserted_qty']!=request.data.get('totQty'):
                    dct_issue_data = {'data':lst_item_details}
                    with open('transfer_issue.txt','w') as f:
                        f.write(json.dumps(dct_issue_data))
                    raise ValueError('Some issues with stock transfer please contact admin')
                else:
                    return Response({'status':1,'message':'Transfer Successfully Registered'})
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':str(e)})






# data{
#     "branchform":"pottamal",
#     "branchto":"kattappana",
#     "datetransfer":"2020-09-12 12:30:00:00",
#     "remarks":"transfer to kattappana",
#     "total_qty":20,
#     "lst_items":[{
#         "item_id":1,
#         "item_name":"iphone X11",
#         "product_id":1,
#         "product_name":"mobile",
#         "slected_imei/batch":['123','1234','12345'],
#         "grn_id":"123" (id that i have send),
#         "pk_id":"123",
#         "bln_imei":True,
#         "qty":3
#     },
#     {
#         "item_id":2,
#         "item_name":"accbgn",
#         "product_id":2,
#         "product_name":"accessory",
#         "slected_imei/batch":['azrd004'],
#         "grn_id":"123" (id that i have send),
#         "pk_id":"123",
#         "bln_imei":False,
#         "qty":17
#     }]],
#     "intMedium": "2",
#     "intPackets": 2,
#     "int_courier_id": null,
#     "int_id": "25532",
#     "strMediumName": "sdfsd",
#     "strMediumNo": "sdfsdfs",
#     "strMediumPhNo": 9658987456,
#     "str_vehicle": "kl-06-e-4516",

# }