from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from datetime import datetime
from POS import ins_logger
import json
import sys  
from django.db import transaction
from django.db.models import CharField, Case, Value, When, Value,Sum,F, Q
from bulk_update.helper import bulk_update


from purchase.views import doc_num_generator
from purchase.models import GrnrDetails,GrnrMaster,GrnrImeiDetails
from branch.models import Branch
from branch_stock.models import BranchStockMaster,BranchStockDetails,BranchStockImeiDetails
from purchase.models import GrnDetails

from sqlalchemy.orm.session import sessionmaker
def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()
# Create your views here.

class GoodsList(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    def post(self,request):
        # {"datFrom":"2020-10-06", "datTo":"2020-10-06"}
        try:
            session = Session()

            lst_data = []
            lst_branch = []
            filter = ''
            branch = request.data.get('branch',{})
            dat_date_from = request.data.get('datFrom',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            dat_date_to = request.data.get('datTo',datetime.strftime(datetime.now(),'%Y-%m-%d'))

            for data in branch:
                lst_branch.append(data['pk_bint_id'])
            if lst_branch:
                filter += """and b.pk_bint_id  in ("""+str(lst_branch)[1:-1]+""")"""
                

            str_query = """
                SELECT
                    gm.pk_bint_id,
                    gm.vchr_purchase_return_num,
                    gm.dat_purchase_return as dat_return,
                    b.vchr_name as branch,
                    SUM(gd.int_qty) as qty
                FROM grnr_master gm
                    JOIN grnr_details gd ON gd.fk_master_id = gm.pk_bint_id
                    JOIN branch b ON b.pk_bint_id = gm.fk_branch_id
                WHERE gm.dat_purchase_return::Date BETWEEN '"""+dat_date_from+"""' and '"""+dat_date_to+"""' """+filter+"""
                GROUP BY gm.vchr_purchase_return_num,gm.dat_purchase_return,b.vchr_name,gm.pk_bint_id
                ORDER BY gm.pk_bint_id desc

            """
            rst_data = session.execute(str_query).fetchall()
            # import pdb; pdb.set_trace()
            if rst_data:
                # import pdb; pdb.set_trace()
                for data in rst_data:
                    dct_data = {}
                    dct_data["Date"] = datetime.strftime(data['dat_return'],'%d-%m-%Y')
                    dct_data['PurchaseNum'] = data['vchr_purchase_return_num']
                    dct_data['Branch'] = data['branch']
                    dct_data['Qty'] = data['qty']
                    dct_data['Id'] = data['pk_bint_id']
                    lst_data.append(dct_data)

                return Response({'status':1,'data':lst_data})
            

            return Response({'status':0,'message':'No Data..!'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':'Something Went Wrong..!'+str(e)})
            
        finally:
            session.close()

    def put(self,request):
        try:
            session = Session()
            int_id = request.data.get('Id','')
            lst_data = []
            if int_id:
                str_query = """
                    SELECT
                        gm.vchr_purchase_return_num,
                        gm.dat_purchase_return as dat_return,
                        b.vchr_name as branch,
                        it.vchr_name as item,
                        it.vchr_item_code,
                        gd.int_qty,
                        gd.jsn_imei as imei,
                        gd.vchr_batch_no as batch
                    FROM grnr_master gm
                        JOIN grnr_details gd ON gd.fk_master_id = gm.pk_bint_id
                        JOIN grnr_imei_details gid ON gid.fk_details_id = gd.pk_bint_id
                        JOIN branch b ON b.pk_bint_id = gm.fk_branch_id
                        JOIN item it ON it.pk_bint_id = gd.fk_item_id
                    WHERE gm.pk_bint_id = """+str(int_id)+"""
                    GROUP BY gm.vchr_purchase_return_num,gm.dat_purchase_return,b.vchr_name,it.vchr_name,gd.jsn_imei,gd.vchr_batch_no,it.vchr_item_code,gd.int_qty  
                """

                rst_data = session.execute(str_query).fetchall()

                dct_data_batch = {}
                if rst_data:
                    for data in rst_data:
                        if data['imei'] != None:
                            dct_temp = {}
                            dct_temp['Name'] = data['item']
                            dct_temp["ItemCode"] = data['vchr_item_code']
                            dct_temp["Qty"] = data['int_qty']
                            dct_temp['Header'] = "IMEI"
                            dct_temp["Imei/Batch"] = [{"imei": [imei], "qty":1} for imei in data['imei']]
                            lst_data.append(dct_temp)
                        else:
                            if dct_data_batch.get(data['item']) == None:
                                dct_data_batch[data['item']] = []
                                dct_temp = {}
                                dct_temp['ItemCode'] = data['vchr_item_code']
                                dct_temp['Imei/Batch'] = data['batch']
                                dct_temp['Qty'] = data['int_qty']
                                dct_temp['Header'] = "Batch"
                                dct_data_batch[data['item']].append(dct_temp)
                            else:
                                dct_temp = {}
                                dct_temp['ItemCode'] = data['vchr_item_code']
                                dct_temp['Imei/Batch'] = data['batch']
                                dct_temp['Qty'] = data['int_qty']
                                dct_temp['Header'] = "Batch"
                                dct_data_batch[data['item']].append(dct_temp)


                    for item,data in dct_data_batch.items():
                        dct_temp = {}
                        dct_temp['Name'] = item
                        dct_temp['Header'] = "Batch"
                        dct_temp["ItemCode"] = data[0]['ItemCode']
                        dct_temp['Qty'] = 0
                        dct_temp["Imei/Batch"] = []
                        for datas in data: 
                            dct_temp["Qty"] += datas['Qty']
                            dct_temp1 = {}
                            dct_temp1['imei'] = eval(datas['Imei/Batch'])
                            dct_temp1['qty'] = datas['Qty']
                            dct_temp["Imei/Batch"].append(dct_temp1)
                        lst_data.append(dct_temp)


                    #     if dct_data.get(data['item']) == None:
                    #         if data['imei'] != None:
                    #             dct_data[data['item']] = {}
                    #             dct_data[data['item']]['ItemCode'] = data['vchr_item_code']
                    #             if dct_data[data['item']].get('Imei/Batch') == None:
                    #                 dct_data[data['item']]['Qty'] = 0
                    #                 dct_data[data['item']]['Imei/Batch'] = []
                    #                 dct_data[data['item']]['Imei/Batch'].extend(data['imei'])
                    #             else:
                    #                 dct_data[data['item']]['Imei/Batch'].extend(data['imei'])
                    #             # dct_data[data['item']]['Batch'] = data['batch'] if data['batch'] != None else []
                    #             dct_data[data['item']]['Qty'] += data['int_qty']
                    #             dct_data[data['item']]['Header'] = "IMEI"
                    #         else:
                    #             dct_data[data['item']] = []
                    #             dct_temp = {}
                    #             dct_temp['ItemCode'] = data['vchr_item_code']
                    #             dct_temp['Imei/Batch'] = data['batch']
                    #             dct_temp['Qty'] = data['int_qty']
                    #             dct_temp['Header'] = "Batch"
                    #             dct_data[data['item']].append(dct_temp)
                    #     else:
                    #         if data['imei'] != None:
                    #             dct_data[data['item']]['ItemCode'] = data['vchr_item_code']
                    #             if dct_data[data['item']].get('Imei/Batch') == None:
                    #                 dct_data[data['item']]['Qty'] = 0
                    #                 dct_data[data['item']]['Imei/Batch'] = []
                    #                 dct_data[data['item']]['Imei/Batch'].extend(data['imei'])
                    #             else:
                    #                 dct_data[data['item']]['Imei/Batch'].extend(data['imei'])
                    #             # dct_data[data['item']]['Batch'] = data['batch'] if data['batch'] != None else []
                    #             dct_data[data['item']]['Qty'] += data['int_qty']
                    #             dct_data[data['item']]['Header'] = "IMEI"
                    #         else:
                    #             dct_temp = {}
                    #             dct_temp['ItemCode'] = data['vchr_item_code']
                    #             dct_temp['Imei/Batch'] = data['batch']
                    #             dct_temp['Qty'] = data['int_qty']
                    #             dct_temp['Header'] = "Batch"
                    #             dct_data[data['item']].append(dct_temp)
                                
                    # lst_data.append(dct_data)
                    # lst_data_final = []
                    # if lst_data:
                    #     for item,data in lst_data.items():
                    #         dct_temp = {}
                    #         dct_temp['Item'] = item
                    #         dct_temp['ItemCode'] = data['vchr_item_code']
                    #         dct_temp['Imei/Batch'] = data['batch']
                    #         dct_temp['Qty'] = data['int_qty']
                    #         dct_temp['Header'] = "Batch"

                    return Response({'status':1,'data':lst_data})
                else:
                    return Response({'status':0,'message':'No data'})
            return Response({'status':0,'message':'Id is not provided'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':'Something Went Wrong..!'+str(e)})
        finally:
            session.close()

# class to get the imei's availiable for branch's and warehouse's
class ImeiList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        pass
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()

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
            return Response({'status':0, 'message' : 'no imei available'})
       
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
            return Response({'status':0, 'message' : 'no batch available'})

class GoodsReturn(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                lst_item_details = request.data.get('lst_items',[])
                vchr_remarks = request.data.get('remarks','')
                session = Session()
                # import pdb; pdb.set_trace()
                if (Branch.objects.filter(pk_bint_id=request.user.userdetails.fk_branch_id).values('int_type').first()['int_type'] in [3,2]):   
                    str_doc_num = doc_num_generator('GOODS RETURN',request.user.userdetails.fk_branch.pk_bint_id)
                    if not str_doc_num:
                        return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                    str_query_grnr_master = "INSERT INTO grnr_master (vchr_purchase_return_num,dat_purchase_return,fk_branch_id,dat_created,vchr_remarks,fk_created_id) values('"+str_doc_num+"','"+str(datetime.now())+"',"+str(request.user.userdetails.fk_branch_id)+",'"+str(datetime.now())+"','"+vchr_remarks+"',"+str(request.user.id)+") returning pk_bint_id"
                    # import pdb; pdb.set_trace()
                    rst_data_grnr_master = session.execute(str_query_grnr_master).fetchall()
                    if rst_data_grnr_master:
                        grnr_master_id = rst_data_grnr_master[0]['pk_bint_id']

                        dct_goodsreturnimeidetails_data = {}
                        for dct_item in lst_item_details:
                            # import pdb; pdb.set_trace()
                            dct_goodsreturnimeidetails_data = {}
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

                                    if dct_goodsreturnimeidetails_data.get(data['grn_id']) == None:
                                        dct_goodsreturnimeidetails_data[data['grn_id']] = {}
                                        dct_goodsreturnimeidetails_data[data['grn_id']]['int_qty'] = 1
                                        dct_goodsreturnimeidetails_data[data['grn_id']]['jsn_imei'] = []
                                        dct_goodsreturnimeidetails_data[data['grn_id']]['jsn_batch_no'] = []
                                        dct_goodsreturnimeidetails_data[data['grn_id']]['jsn_imei'].extend([data['imei']])
                                    else:
                                        dct_goodsreturnimeidetails_data[data['grn_id']]['int_qty'] += 1
                                        dct_goodsreturnimeidetails_data[data['grn_id']]['jsn_imei'].extend([data['imei']])
                                    lst_imei_transfer.extend([data['imei']])
                                ins_sr_details = GrnrDetails(
                                    fk_item_id = dct_item.get('item_id'),
                                    fk_master_id = grnr_master_id,
                                    int_qty = dct_item['int_qty'],
                                    jsn_imei=json.dumps(lst_imei_transfer),
                                    # dbl_rate=dct_item['rate'],
                                    vchr_batch_no = None
                                )
                                ins_sr_details.save()
                                for grnid,data in dct_goodsreturnimeidetails_data.items():
                                    ins_grnr_imei=GrnrImeiDetails(
                                        fk_details_id=ins_sr_details.pk_bint_id,
                                        fk_grn_details_id= int(grnid),
                                        int_qty = data['int_qty'],
                                        jsn_imei=json.dumps(data['jsn_imei']),
                                        jsn_batch_no='{}'
                                    )
                                    # import pdb; pdb.set_trace()
                                    ins_grnr_imei.save()
                                    

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

                                        if dct_goodsreturnimeidetails_data.get(data['id']) == None:
                                            dct_goodsreturnimeidetails_data[data['id']] = {}
                                            dct_goodsreturnimeidetails_data[data['id']]['int_qty'] = data['transfer_qty']
                                            dct_goodsreturnimeidetails_data[data['id']]['jsn_imei'] = []
                                            dct_goodsreturnimeidetails_data[data['id']]['jsn_batch_no'] = []
                                            dct_goodsreturnimeidetails_data[data['id']]['jsn_batch_no'].extend(data['batch'])
                                        else:
                                            dct_goodsreturnimeidetails_data[data['id']]['int_qty'] += data['transfer_qty']
                                            dct_goodsreturnimeidetails_data[data['id']]['jsn_batch_no'].extend(data['batch'])
                                # import pdb; pdb.set_trace()
                                for grnid,data in dct_goodsreturnimeidetails_data.items():
                                    
                                    ins_sr_details = GrnrDetails(
                                        fk_item_id = dct_item.get('item_id'),
                                        fk_master_id = grnr_master_id,
                                        int_qty = data['int_qty'],
                                        jsn_imei=None,
                                        # dbl_rate=dct_item['rate'],
                                        vchr_batch_no=json.dumps(list(set(data['jsn_batch_no'])))
                                    )
                                    ins_sr_details.save()

                                    ins_goodsreturnimei=GrnrImeiDetails(
                                        fk_details_id=ins_sr_details.pk_bint_id,
                                        fk_grn_details_id= int(grnid),
                                        int_qty = data['int_qty'],
                                        jsn_imei='{}',
                                        jsn_batch_no=json.dumps(list(set(data['jsn_batch_no'])))
                                    )
                                    # import pdb; pdb.set_trace()
                                    ins_goodsreturnimei.save()
                        # return Response({'status':1,'message':'Goods Returned Successfully...'})
                    # import pdb; pdb.set_trace()
                    rst_transfer_qty=GrnrImeiDetails.objects.filter(fk_details__fk_master_id=grnr_master_id).aggregate(inserted_qty=Sum('int_qty'))
                    if not rst_transfer_qty or not rst_transfer_qty['inserted_qty'] or rst_transfer_qty['inserted_qty']!=request.data.get('totQty'):
                        dct_issue_data = {'data':lst_item_details}
                        with open('Goodsretrun_issue.txt','w') as f:
                            f.write(json.dumps(dct_issue_data))
                        raise ValueError('Some Issues With Goods Return')
                    else:
                        return Response({'status':1,'message':'Goods Return Successfully Registered'})

                    
                else:
                    return Response({'status':0,'message':'You Are Not Authorize To Access This Session...'})
                
                return Response({'status':0,'message':'Something Went Wrong..!'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':'Something Went Wrong..!'+str(e)})
        finally:
            session.close()
    