from django.shortcuts import render

from django.views import generic
from rest_framework import generics
from rest_framework import authentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.http import JsonResponse
from rest_framework.response import Response
from django.views.generic import View,TemplateView,CreateView
from rest_framework.views import APIView
from datetime import datetime
from django.db.models import Q
from django.db.models import CharField, Case, Value, When, Value,Sum,F
from django.db.models.functions import Concat
# ----------models import
from branch.models import Branch
from internal_stock.models import StockRequest,IsrDetails,StockTransfer,IstDetails,TransferHistory,TransferModeDetails,StockTransferImeiDetails,\
PurchaseRequest,PurchaseRequestDetails
from branch_stock.models import BranchStockMaster,BranchStockDetails,BranchStockImeiDetails,NonSaleable
from purchase.models import GrnDetails
from branch.models import Branch
from django.db import transaction
from purchase.models import Document
from pricelist.models import PriceList
from item_category.models import Item,TaxMaster
import requests
from POS import settings
from django.core.mail import send_mail, EmailMultiAlternatives
import pdfkit
from django.core.files.storage import FileSystemStorage
import base64
import json
from supplier.models import Supplier
from bulk_update.helper import bulk_update
from generate_file_name import name_change
import copy
# from django.db.models import Sum
# from django.db.models.functions import Cast
# from django.db.models import Avg, Count, Min, Sum


# Create your views here.
from POS import ins_logger
import sys, os
import num2words
from uuid import uuid3, NAMESPACE_DNS
from random import random,randint
from django.shortcuts import render

from sqlalchemy.orm.session import sessionmaker

import pandas as pd
from django.db.models.functions import TruncMonth

from geopy.distance import geodesic
from .models import CourierMaster
import pyqrcode
import png
from pyqrcode import QRCode

class GetBranchDetails(APIView):
    """ This view provide data for branch typeahead"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_search_term=request.data.get('str_search')
            if request.user.userdetails.fk_branch.int_type in [2,3]:
                lst_branch=list(Branch.objects.filter(Q(vchr_code__icontains = str_search_term,int_status = 0) | Q(vchr_name__icontains = str_search_term,int_status = 0)).exclude(pk_bint_id=request.user.userdetails.fk_branch_id).values('pk_bint_id','vchr_code','vchr_name'));
            elif request.user.userdetails.fk_branch.vchr_code =='AGY':
                lst_branch=list(Branch.objects.filter(Q(vchr_code__icontains = str_search_term,int_status = 0) | Q(vchr_name__icontains = str_search_term,int_status = 0),int_type__in=[2,3]).exclude(pk_bint_id=request.user.userdetails.fk_branch_id).values('pk_bint_id','vchr_code','vchr_name'));
            else:
                if request.data.get('blnStockTransfer'):
                    lst_branch=list(Branch.objects.filter(Q(vchr_code__icontains = str_search_term,int_status = 0) | Q(vchr_name__icontains = str_search_term,int_status = 0),int_type__in=[2,3]).exclude(Q(pk_bint_id=request.user.userdetails.fk_branch_id)|Q(vchr_code='AGY')).values('pk_bint_id','vchr_code','vchr_name'));
                else:
                    lst_branch=list(Branch.objects.filter(Q(vchr_code__icontains = str_search_term,int_status = 0) | Q(vchr_name__icontains = str_search_term,int_status = 0)).exclude(Q(pk_bint_id=request.user.userdetails.fk_branch_id)|Q(vchr_code='AGY')).values('pk_bint_id','vchr_code','vchr_name'));
            return Response({'status':1, 'branch_list' : lst_branch})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})
class AddRequest(APIView):
    """This view save internal stock request"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()

            int_branch_to=request.data.get('fk_branch_id')
            dat_request=request.data.get('dat_request')
            vchr_remarks=request.data.get('vchr_notes')
            dat_expected=request.data.get('dat_expected')
            tim_expected=request.data.get('tim_expected')
            lst_item_details=request.data.get('lst_details')






            with transaction.atomic():
                # import pdb; p db.set_trace()
                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'STOCK REQUEST')
                # str_code = ins_document[0].vchr_short_code
                # int_doc_num = ins_document[0].int_number + 1
                # ins_document.update(int_number = int_doc_num)
                # str_number = str(int_doc_num).zfill(4)
                # str_request_no = str_code + '-' + str_number
                # BranchStockImeiDetails.objects.filter(fk_details__fk_item_id= 3,fk_details__fk_master__fk_branch_id=1).annotate(sm=Sum('fk_grn_details__dbl_ppu')).values('sm')

                # ins_stockrequest = StockRequest.objects.create_stock_doc(str_request_no)

                # LG 27-06-2020
                ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'STOCK REQUEST',fk_branch_id =request.user.userdetails.fk_branch_id).first()
                if ins_document:
                    str_request_no = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                    Document.objects.filter(vchr_module_name = "STOCK REQUEST",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                else:
                    ins_document_search = Document.objects.filter(vchr_module_name = 'STOCK REQUEST',fk_branch_id = None).first()
                    if ins_document_search:
                        ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                        ins_document = Document.objects.create(vchr_module_name = 'STOCK REQUEST', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                        str_request_no = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                        ins_document.int_number = ins_document.int_number+1
                        ins_document.save()
                    else:
                        return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                ins_stockrequest = StockRequest.objects.create(
                    fk_from_id = request.user.userdetails.fk_branch_id, #need to change
                    fk_to_id = int_branch_to,
                    vchr_stkrqst_num = str_request_no,
                    dat_request = datetime.strptime(dat_request,'%Y-%m-%d'),
                    dat_expected = datetime.strptime(dat_expected+'-'+tim_expected,'%Y-%m-%d-%H:%M'),
                    vchr_remarks = vchr_remarks,
                    fk_created_id = request.user.id,
                    dat_created = datetime.now(),
                    fk_updated_id = request.user.id,
                    dat_updated = datetime.now(),
                    int_doc_status = 0
                )
                ins_stockrequest.save()

                ins_stock=BranchStockImeiDetails.objects.filter(fk_details__fk_master__fk_branch_id=request.user.userdetails.fk_branch_id).values('fk_grn_details__dbl_ppu','int_qty')
                stock_available=0
                total_required=0
                # lst_stock = [ data['fk_grn_details__dbl_ppu'] * data['int_qty'] for data in ins_stock ]
                # stock_available=sum(lst_stock)
                lst_query_set = []
                lst_item=[]
                for dct_item in lst_item_details:
                    ins_rq_details = IsrDetails(
                        fk_item_id = dct_item['intId'],
                        fk_request_id = ins_stockrequest.pk_bint_id,
                        int_qty = dct_item['intQty'],
                    )
                    lst_query_set.append(ins_rq_details)
                    lst_item.append(dct_item['intId'])
                    dbl_price=GrnDetails.objects.filter(fk_item_id=dct_item['intId']).values('dbl_ppu')
                    if dbl_price:
                        total_required+=dbl_price[0]['dbl_ppu']*dct_item['intQty']
                if lst_query_set:
                    IsrDetails.objects.bulk_create(lst_query_set)
                if Branch.objects.filter(bint_stock_limit__lt=stock_available+total_required,pk_bint_id=request.user.userdetails.fk_branch_id):
                    StockRequest.objects.filter(pk_bint_id=ins_stockrequest.pk_bint_id).update(int_status=1)


                ############ Territory manager mail


                    url=settings.HOSTNAME+'/user/get_territory_manager/'

                    str_approve = hash_approve(ins_stockrequest,'APPROVE')
                    str_reject = hash_approve(ins_stockrequest,'REJECT')
                    StockRequest.objects.filter(pk_bint_id=ins_stockrequest.pk_bint_id).update(vchr_reject=str_reject,vchr_approve=str_approve)
                    #asd=requests.post(url,json=dct_data)
                    lst_items=Item.objects.filter(pk_bint_id__in=lst_item).values_list('vchr_name',flat=True)
                    str_items=",".join(lst_items)
                    from_email = settings.EMAIL_HOST_EMAIL
                    dct_data={}
                    dct_data['username']=request.user.username
                    try:
                        # import pdb; pdb.set_trace()
                        dt_api=requests.post(url,json=dct_data)
                        if dt_api.json()['status']==1:
                            str_name=dt_api.json()['data']['name']
                            str_email=dt_api.json()['data']['email']
                        str_name=str_name
                        to_mail=str_email
                        subject = 'Stock Request Aproval'
                        text_content = 'Travidux'
                        from_email=settings.EMAIL_HOST_EMAIL
                        html_content = '''Dear '''+str(str_name).title()+''',<br>
                        '''+str(request.user.first_name+' '+request.user.last_name).title()+''' requested for a stock worth '''+str(total_required)+''' on '''+ str(datetime.now().date())+'''.<br>Items - '''+str_items
                        approveurl = settings.HOSTNAME+"/internalstock/approve_mail/"+str_approve
                        rejecturl = settings.HOSTNAME+"/internalstock/approve_mail/"+str_reject
                        html_content = html_content +  '''<br><button style="border:none; cursor: pointer; font-weight: 600;background:#1e8dcc;padding: 5px 10PX;border-radius: 5px;margin-top:8px;margin-right:10px;"><a style="color: #fff;text-decoration: none;" target ='_blank' href="'''+approveurl+'''">Approve</a></button> <button style="border:none; cursor: pointer; font-weight: 600;background: #d64747;padding: 5px 10px;border-radius: 5px;margin-top:8px;"><a style="color: #fff;text-decoration: none;" target ='_blank' href="'''+rejecturl+'''">Reject</a></button>'''
                        if to_mail:
                            mail = EmailMultiAlternatives(subject, text_content, from_email, [to_mail])
                            mail.attach_alternative(html_content, "text/html")
                            mail.send()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                else:
                    StockRequest.objects.filter(pk_bint_id=ins_stockrequest.pk_bint_id).update(int_status=2)



            # to_email = UserModel.objects.filter(fk_branch_id = request.user.usermodel.fk_branch_id,fk_company_id = request.user.usermodel.fk_company_id,fk_group__vchr_name = group_name,is_active=True).values('email').first()['email']

            return Response({'status':1,'message':'Request Successfully Registered'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class GetRequestList(APIView):
    """List the internal stock requests for each branch"""
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            str_request=request.GET.get('type')
            if str_request=='from':
                lst_requests=list(StockRequest.objects.filter(fk_from_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0]).annotate(status=Case(When(int_status=1,then=Value('TM APPROVAL REQUESTED')),When(int_status=2,then=Value('PENDING')),When(int_status=3,then=Value('APPROVED')),When(int_status=4,then=Value('REJECTED')),default=Value('PENDING'),output_field=CharField())).values('pk_bint_id','dat_request','dat_expected','fk_from__vchr_name','fk_to__vchr_name','status','vchr_stkrqst_num').order_by('-dat_request','-vchr_stkrqst_num'))
            else:
                lst_requests=list(StockRequest.objects.filter(fk_to_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0]).annotate(status=Case(When(int_status=1,then=Value('TM APPROVAL REQUESTED')),When(int_status=2,then=Value('PENDING')),When(int_status=3,then=Value('APPROVED')),When(int_status=4,then=Value('REJECTED')),default=Value('PENDING'),output_field=CharField())).values('pk_bint_id','dat_request','dat_expected','fk_from__vchr_name','fk_to__vchr_name','status','vchr_stkrqst_num').order_by('-dat_request','-vchr_stkrqst_num'))
            return Response({'status':1, 'request_list' : lst_requests})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})
    def post(self,request):
        try:
            str_request=request.data.get('type')
            dat_to= request.data.get('datTo')
            dat_from= request.data.get('datFrom')
            int_branch = request.data.get('intBranchId')
            if str_request=='from':
                lst_requests=StockRequest.objects.filter(fk_from_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0,1],dat_request__lte=dat_to,dat_request__gte = dat_from).annotate(status=Case(When(int_status=1,then=Value('TM APPROVAL REQUESTED')),When(int_status=2,then=Value('PENDING')),When(int_status=3,then=Value('APPROVED')),When(int_status=4,then=Value('REJECTED')),default=Value('PENDING'),output_field=CharField())).values('pk_bint_id','dat_request','dat_expected','fk_from__vchr_name','fk_to__vchr_name','status','vchr_stkrqst_num').order_by('-dat_request','-vchr_stkrqst_num')
                if int_branch:
                    lst_requests=lst_requests.filter(fk_to_id = int_branch )
            else:
                lst_requests=StockRequest.objects.filter(fk_to_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0,1],dat_request__lte=dat_to,dat_request__gte = dat_from).annotate(status=Case(When(int_status=1,then=Value('TM APPROVAL REQUESTED')),When(int_status=2,then=Value('PENDING')),When(int_status=3,then=Value('APPROVED')),When(int_status=4,then=Value('REJECTED')),default=Value('PENDING'),output_field=CharField())).values('pk_bint_id','dat_request','dat_expected','fk_from__vchr_name','fk_to__vchr_name','status','vchr_stkrqst_num').order_by('-dat_request','-vchr_stkrqst_num')
                if int_branch:
                    lst_requests=lst_requests.filter(fk_from_id = int_branch)
            return Response({'status':1, 'request_list' : list(lst_requests)})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class RequestView(APIView):
    """Provide data for view request from request list"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            int_request_id=request.data.get('int_id')
            lst_requests=list(StockRequest.objects.filter(pk_bint_id = int_request_id).annotate(status=Case(When(int_status=1,then=Value('TM APPROVAL REQUESTED')),When(int_status=2,then=Value('PENDING')),When(int_status=3,then=Value('APPROVED')),When(int_status=4,then=Value('REJECTED')),default=Value('PENDING'),output_field=CharField())).values('dat_request','dat_expected','fk_from__vchr_name','fk_to__vchr_name','status','vchr_remarks','vchr_stkrqst_num','vchr_rej_remark'))
            lst_details=list(IsrDetails.objects.filter(fk_request__pk_bint_id = int_request_id).values('fk_item__vchr_name','int_qty'))
            return Response({'status':1, 'request_data' : lst_requests,'details_data':lst_details})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class ApproveRequest(APIView):
    """direct approval of stock request """
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            int_request_id=request.data.get('int_id')
            bln_approve =request.data.get('bln_approve')
            # dat_expected=datetime.strptime(request.data.get('dat_expected'),'%Y-%m-%d')
            StockRequest.objects.filter(pk_bint_id = int_request_id).update(int_status=3)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

class GetdetailsByRequestNum(APIView):
    """provide request details by request number"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            vchr_request_num=request.data.get('vchr_request_num')
            if request.user.userdetails.fk_branch.int_type == 1:
                lst_item_id = IsrDetails.objects.filter(fk_request__vchr_stkrqst_num = vchr_request_num).values_list('fk_item_id',flat=True)
                dct_item_qty =dict(BranchStockDetails.objects.filter(fk_item__in = lst_item_id,fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(total_qty=Sum('int_qty') ).values_list('fk_item_id','total_qty'))

            else:
                lst_item_id = IsrDetails.objects.filter(fk_request__vchr_stkrqst_num = vchr_request_num).values_list('fk_item_id',flat=True)
                dct_item_qty = dict(GrnDetails.objects.filter(fk_item__in = list(lst_item_id),fk_purchase__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(total_qty=Sum('int_avail') ).values_list('fk_item_id','total_qty'))
                dct_item_qty_branch = dict(BranchStockDetails.objects.filter(fk_item__in = lst_item_id,fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(total_qty=Sum('int_qty') ).values_list('fk_item_id','total_qty'))
                if dct_item_qty_branch:
                    for dct_branch_data in  dct_item_qty_branch:
                        if dct_branch_data in dct_item_qty:
                            dct_item_qty[dct_branch_data]+=dct_item_qty_branch[dct_branch_data]
                        else:
                            dct_item_qty[dct_branch_data]=dct_item_qty_branch[dct_branch_data]
            # import pdb; pdb.set_trace()
            lst_requests=list(StockRequest.objects.filter(vchr_stkrqst_num = vchr_request_num).annotate(status=Case(When(int_status=1,then=Value('TM APPROVAL REQUESTED')),When(int_status=2,then=Value('PENDING')),When(int_status=3,then=Value('APPROVED')),When(int_status=4,then=Value('REJECTED')),default=Value('PENDING'),output_field=CharField())).values('pk_bint_id','dat_request','dat_expected','fk_from_id','fk_from__vchr_name','status','vchr_remarks','vchr_stkrqst_num'))
            if lst_requests:
                ins_stock_transfer=StockTransfer.objects.filter(fk_request_id=lst_requests[0]['pk_bint_id'])
                if not ins_stock_transfer:
                    lst_details=list(IsrDetails.objects.filter(fk_request__vchr_stkrqst_num = vchr_request_num).annotate(item_name=Concat('fk_item__vchr_item_code', Value('-'), 'fk_item__vchr_name'),imei=Concat(Value(''),Value(''),output_field=CharField()),bnt_bchno=Concat(Value(''),Value(''),output_field=CharField())).annotate(product_name=F('fk_item__fk_product__vchr_name'),brand_name=F('fk_item__fk_brand__vchr_name')).values('item_name','fk_item_id','int_qty','imei','bnt_bchno','fk_item__imei_status','product_name','brand_name'))
                    dct_item_price = dict(Item.objects.filter(pk_bint_id__in = lst_item_id ).annotate(item_price=F('dbl_dealer_cost')).values_list('pk_bint_id','item_price'))
                    for ins_data in lst_details:
                        ins_data['bln_product_disabled'] = True
                        ins_data['item_qty'] = dct_item_qty.get(ins_data['fk_item_id']) or 0
                        ins_data['flt_price'] = dct_item_price.get(ins_data['fk_item_id']) or 0
                        ins_data['qtyDisabled'] = False
                    return Response({'status':1, 'request_data' : lst_requests,'details_data':lst_details})
                else:
                    return Response({'status':0,'reason':'Already Transferred '})
            else:
                return Response({'status':0,'reason':'No Document Number Found'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':'Failed'})




class AddStockTransfer(APIView):
    """This  save internal stock transfer"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            int_branch_to=request.data.get('intBranchId')
            int_branch_from = request.data.get('intBranchFromId')
            dat_transfer=request.data.get('dat_transfer')
            vchr_remarks=request.data.get('vchr_remarks')
            int_request_id=request.data.get('pk_bint_id')
            lst_item_details=request.data.get('lst_details')

            '''VALIDATION STOCK TRANSFER'''
            lst_imei_validation=[]
            lst_batch_validation=[]
            lst_item_id=[]
            for dct_item in lst_item_details:
                if dct_item['fk_item__imei_status']:
                    for dct_imei_grn in dct_item['imei']:
                        if len(dct_item['imei'][dct_imei_grn]) != len(set(dct_item['imei'][dct_imei_grn])):
                            dct_issue_data = {'data':lst_item_details}
                            with open('transfer_issue.txt','w') as f:
                                f.write(json.dumps(dct_issue_data))
                            raise ValueError('Some issues with stock transfer please contact admin')
                if dct_item.get('lst_all_imei'):
                    lst_imei_validation.extend(dct_item.get('lst_all_imei'))

                if dct_item.get('bnt_bchno'):
                    lst_batch_validation.extend(dct_item.get('bnt_bchno'))
                    lst_item_id.append(dct_item.get('fk_item_id'))
            lst_transfer_imei=IstDetails.objects.filter(jsn_imei__imei__has_any_keys=lst_imei_validation,fk_transfer__fk_from_id = int_branch_from,fk_transfer__fk_to_id=int_branch_to,fk_transfer__int_status__in=[0,1]).values('fk_transfer__fk_to__vchr_name','jsn_imei')
            message=''
            # for qry_set in lst_transfer_imei:
            #     for imei2 in lst_imei_validation:
            #         if imei2 in qry_set['jsn_imei']['imei']:
            #             message += imei2 +' imei '+', already transfered to '+qry_set['fk_transfer__fk_to__vchr_name']

            dct_show={}

            for qry_set in lst_transfer_imei:
                for imei2 in lst_imei_validation:
                    if imei2 in qry_set['jsn_imei']['imei']:
                            if qry_set['fk_transfer__fk_to__vchr_name'] not in dct_show:
                                dct_show[qry_set['fk_transfer__fk_to__vchr_name']] =imei2
                            else:
                                dct_show[qry_set['fk_transfer__fk_to__vchr_name']] +=', ' +imei2

            for key in dct_show:
                message +=dct_show[key] +' imeis transfered to branch '+key+' '


            if lst_transfer_imei:
                return Response({'status':0,'message':message,'bln_imei':True})




            lst_transfer_batch=IstDetails.objects.filter(jsn_batch_no__batch__has_any_keys=lst_batch_validation,fk_item_id__in=lst_item_id,fk_transfer__fk_from_id = int_branch_from,fk_transfer__fk_to_id=int_branch_to,fk_transfer__int_status__in=[0,1],fk_transfer_id__dat_created__contains=datetime.today().date()).values('fk_transfer__fk_to__vchr_name','jsn_batch_no')
            message = ''
            dct_show={}
            lst_batch=set([])
            for qry_set in lst_transfer_batch:
                for batch2 in lst_batch_validation:
                    if batch2 in qry_set['jsn_batch_no']['batch'] and batch2 not in lst_batch:
                            if qry_set['fk_transfer__fk_to__vchr_name'] not in dct_show  :
                                dct_show[qry_set['fk_transfer__fk_to__vchr_name']] =batch2
                            else:
                                dct_show[qry_set['fk_transfer__fk_to__vchr_name']] +=', ' +batch2
                            lst_batch.add(batch2)

            for key in dct_show:
                message +=dct_show[key] +' batches transfered to branch '+key+' '
            if lst_transfer_batch and not request.data.get('bln_batch_pass'):
                return Response({'status':1,'message':message,'bln_batch':True})



            vchr_branch_code = Branch.objects.filter(pk_bint_id = int_branch_from).values('vchr_code').first()['vchr_code']
            vchr_branch_code_to = Branch.objects.filter(pk_bint_id = int_branch_to).values('vchr_code').first()['vchr_code']
            # import pdb; pdb.set_trace()
            int_transfered_qty=0
            with transaction.atomic():
                if int_request_id:
                    StockRequest.objects.filter(pk_bint_id = int_request_id).update(int_status=3)
                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'STOCK TRANSFER')
                # str_code = ins_document[0].vchr_short_code
                # if vchr_branch_code_to.upper() == 'AGY':
                #     str_code = 'BB'
                # int_doc_num = ins_document[0].int_number + 1
                # ins_document.update(int_number = int_doc_num)
                # str_number = str(int_doc_num).zfill(4)
                # str_transfer_no = str_code + '-' +vchr_branch_code+'-'+ str_number

                # LG 27-06-2020
                if vchr_branch_code_to.upper() == 'AGY':
                    ins_document = Document.objects.select_for_update().filter(vchr_module_name = "STOCK TRANSFER TO AGY",fk_branch_id = request.user.userdetails.fk_branch_id).first()
                    if ins_document:
                        str_transfer_no = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                        Document.objects.filter(vchr_module_name = "STOCK TRANSFER TO AGY",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                    else:
                        ins_document_search = Document.objects.filter(vchr_module_name = 'STOCK TRANSFER TO AGY',fk_branch_id = None).first()
                        if ins_document_search:
                            ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                            ins_document = Document.objects.create(vchr_module_name = 'STOCK TRANSFER TO AGY', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                            str_transfer_no = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                            ins_document.int_number = ins_document.int_number+1
                            ins_document.save()
                        else:
                            return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})
                else:
                    ins_document = Document.objects.select_for_update().filter(vchr_module_name = "STOCK TRANSFER",fk_branch_id = request.user.userdetails.fk_branch_id).first()
                    if ins_document:
                        str_transfer_no = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                        Document.objects.filter(vchr_module_name = "STOCK TRANSFER",fk_branch_id = request.user.userdetails.fk_branch_id).update(int_number = ins_document.int_number+1)
                    else:
                        ins_document_search = Document.objects.filter(vchr_module_name = 'STOCK TRANSFER',fk_branch_id = None).first()
                        if ins_document_search:
                            ins_branch_code = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_code').first()['vchr_code']
                            ins_document = Document.objects.create(vchr_module_name = 'STOCK TRANSFER', int_number = 1, vchr_short_code = ins_document_search.vchr_short_code + ins_branch_code + ins_document_search.vchr_short_code[::-1][:1], fk_branch_id = request.user.userdetails.fk_branch_id)
                            str_transfer_no = (ins_document.vchr_short_code).upper()+str(ins_document.int_number).zfill(4)
                            ins_document.int_number = ins_document.int_number+1
                            ins_document.save()
                        else:
                            return Response({'status':0, 'message' : 'Document Numbering Series not Assigned'})

                # ins_stocktransfer = StockTransfer.objects.create_stock_trans(str_transfer_no)







                ins_stocktransfer = StockTransfer.objects.create(
                    fk_from_id = int_branch_from, #changed
                    fk_to_id = int_branch_to,
                    fk_request_id=int_request_id,
                    vchr_stktransfer_num = str_transfer_no,
                    dat_transfer = datetime.strptime(dat_transfer,'%Y-%m-%d'),
                    vchr_remarks = vchr_remarks,
                    fk_created_id = request.user.id,
                    dat_created = datetime.now(),
                    fk_updated_id = request.user.id,
                    dat_updated = datetime.now(),
                    int_doc_status = 0,
                    int_status=0
                )
                ins_stocktransfer.save()
                lst_query_set = []
                for dct_item in lst_item_details:
                    lst_imei=[]
                    # str_imei=''
                    if dct_item['imei']:
                        lst_imei=dct_item['imei']
                        if not dct_item.get('bnt_bchno'):
                            dct_item['bnt_bchno']=[]
                    int_transfered_qty +=dct_item['int_qty']
                    ins_st_details = IstDetails(
                        fk_item_id = dct_item.get('fk_item_id'),
                        fk_transfer_id = ins_stocktransfer.pk_bint_id,
                        int_qty = dct_item['int_qty'],
                        jsn_imei={"imei":dct_item.get('lst_all_imei',[])},
                        dbl_rate=dct_item['flt_price'],
                        jsn_batch_no={"batch":dct_item.get('bnt_bchno')}
                    )
                    # import pdb; pdb.set_trace()
                    ins_st_details.save()
                    # ins_br_stock = BranchStockDetails.objects.filter(Q(jsn_imei_avail__contains={'imei':dct_item.get('lst_all_imei',[])}),fk_item_id=dct_item.get('fk_item_id')).first()
                    # ============================================================
                    lst_br_stock = BranchStockDetails.objects.filter(Q(jsn_imei_avail__imei__has_any_keys = dct_item.get('lst_all_imei',[])),fk_item_id=dct_item.get('fk_item_id'))
                    if lst_br_stock:
                        # lst_diff_imei=set(ins_br_stock.jsn_imei_avail['imei'])-set(dct_item.get('lst_all_imei',[]))
                        # BranchStockDetails.objects.filter(pk_bint_id=ins_br_stock.pk_bint_id).update(jsn_imei_avail={'imei':list(lst_diff_imei)},int_qty=len(list(lst_diff_imei)))
                        for ins_data in lst_br_stock:
                            ins_data.jsn_imei_avail['imei']=list(set(ins_data.jsn_imei_avail['imei'])-(set(dct_item.get('lst_all_imei',[])) & set(ins_data.jsn_imei_avail['imei'])))
                            ins_data.int_qty=len(list(set(ins_data.jsn_imei_avail['imei'])-(set(dct_item.get('lst_all_imei',[])) & set(ins_data.jsn_imei_avail['imei']))))
                        bulk_update(lst_br_stock)
                        # lst_br_stock.bulk_update()

                    # ============================================================
                    # if int_type in [2,3]:
                    #     # import pdb; pdb.set_trace()
                    #     lst_left_imei=list(set(set(GrnDetails.objects.filter(pk_bint_id=dct_key).values().first()['jsn_imei_avail']['imei_avail'])-set(dct_item['imei'][dct_key])))
                    #     GrnDetails.objects.filter(pk_bint_id=dct_key).update(jsn_imei_avail={'imei_avail':lst_left_imei},int_avail=len(lst_left_imei))
                    # else:
                    #     ins_br_stk_imei = BranchStockImeiDetails.objects.filter(Q(jsn_imei__contains={'imei':[str(vchr_stk_imei)]}),fk_details=ins_br_stock).first()
                    #     lst_left_imei=list(set(set(BranchStockImeiDetails.objects.filter(jsn_imei__contains={'imei':[dct_item['imei'][dct_key]]}).values().first()['jsn_imei']['imei'])-set(dct_item['imei'][dct_key])))
                    #     BranchStockImeiDetails.objects.filter(jsn_imei__contains={'imei':dct_item['imei'][dct_key]}).update(jsn_imei={'imei':lst_left_imei},int_qty=len(lst_left_imei))

                    if dct_item['imei']:
                        for dct_key in dct_item['imei']:
                            if not dct_item['imei'][dct_key]:
                                continue
                            ins_stocktransferimei=StockTransferImeiDetails(
                            fk_details_id=ins_st_details.pk_bint_id,
                            fk_grn_details_id=int(dct_key),
                            int_qty = len(dct_item['imei'][dct_key]),
                            jsn_imei={"imei":dct_item['imei'][dct_key]},
                            jsn_batch_no={"batch":dct_item.get('bnt_bchno',[])}
                            )
                            ins_stocktransferimei.save()
                            int_type=Branch.objects.filter(pk_bint_id=request.user.userdetails.fk_branch_id).values('int_type').first()['int_type']
                            if int_type in [2,3]:
                                # import pdb; pdb.set_trace()
                                if GrnDetails.objects.filter(pk_bint_id=dct_key).values().first()['jsn_imei_avail']:
                                    lst_left_imei=list(set(set(GrnDetails.objects.filter(pk_bint_id=dct_key).values().first()['jsn_imei_avail']['imei_avail'])-set(dct_item['imei'][dct_key])))
                                    GrnDetails.objects.filter(pk_bint_id=dct_key).update(jsn_imei_avail={'imei_avail':lst_left_imei},int_avail=len(lst_left_imei))

                                # ===========================================================================================
                                lst_branch_stock_id = BranchStockImeiDetails.objects.filter(jsn_imei__imei__has_any_keys=dct_item['imei'][dct_key])
                                if lst_branch_stock_id:
                                    for ins_data in lst_branch_stock_id:
                                        ins_data.jsn_imei['imei']=list(set(ins_data.jsn_imei['imei'])-(set(dct_item['imei'][dct_key]) & set(ins_data.jsn_imei['imei'])))
                                        ins_data.int_qty=len(list(set(ins_data.jsn_imei['imei'])-(set(dct_item['imei'][dct_key]) & set(ins_data.jsn_imei['imei']))))
                                    bulk_update(lst_branch_stock_id)
                                    # lst_branch_stock_id.bulk_update()
                                # ===========================================================================================

                            else:
                                # lst_left_imei=list(set(set(BranchStockImeiDetails.objects.filter(jsn_imei__contains={'imei':dct_item['imei'][dct_key]}).values().first()['jsn_imei']['imei'])-set(dct_item['imei'][dct_key])))
                                # BranchStockImeiDetails.objects.filter(jsn_imei__contains={'imei':dct_item['imei'][dct_key]}).update(jsn_imei={'imei':lst_left_imei},int_qty=len(lst_left_imei))

                                # ========================================================================================
                                lst_branch_stock_id = BranchStockImeiDetails.objects.filter(jsn_imei__imei__has_any_keys=dct_item['imei'][dct_key])
                                if lst_branch_stock_id:
                                    for ins_data in lst_branch_stock_id:
                                        ins_data.jsn_imei['imei']=list(set(ins_data.jsn_imei['imei'])-(set(dct_item['imei'][dct_key]) & set(ins_data.jsn_imei['imei'])))
                                        ins_data.int_qty=len(list(set(ins_data.jsn_imei['imei'])-(set(dct_item['imei'][dct_key]) & set(ins_data.jsn_imei['imei']))))
                                    # lst_branch_stock_id.bulk_update()
                                    bulk_update(lst_branch_stock_id)
                                # ========================================================================================

                    else:
                        for dct_key in dct_item['dct_bchno']:
                            if not dct_item.get('bnt_bchno'):
                                continue
                            ins_stocktransferimei=StockTransferImeiDetails(
                            fk_details_id=ins_st_details.pk_bint_id,
                            fk_grn_details_id= int(dct_key),
                            int_qty = dct_item['int_qty'],
                            jsn_imei={"imei":[]},
                            jsn_batch_no={"batch":dct_item.get('bnt_bchno',[])}
                            )
                            ins_stocktransferimei.save()
                            int_type=Branch.objects.filter(pk_bint_id=request.user.userdetails.fk_branch_id).values('int_type').first()['int_type']
                            if int_type in [2,3]:
                                ins_branch_stock=BranchStockImeiDetails.objects.filter(fk_grn_details_id= int(dct_key),int_qty__gt=0,fk_details__fk_master_id__fk_branch_id=int_branch_from,fk_details__fk_item_id=dct_item.get('fk_item_id'),jsn_batch_no__contains={'batch':[dct_item['dct_bchno'][dct_key]]}).values('pk_bint_id','int_qty','fk_details_id')
                                if ins_branch_stock:
                                    for ins_batch_stock in ins_branch_stock:
                                        if dct_item['int_qty']==0:
                                            break
                                        if ins_batch_stock['int_qty']>=dct_item['int_qty']:
                                            BranchStockImeiDetails.objects.filter(pk_bint_id=ins_batch_stock['pk_bint_id'],jsn_batch_no__contains={'batch':[dct_item['dct_bchno'][dct_key]]}).update(int_qty=F('int_qty')-dct_item['int_qty'])
                                            BranchStockDetails.objects.filter(pk_bint_id=ins_batch_stock['fk_details_id']).update(int_qty=F('int_qty')-dct_item['int_qty'])
                                            dct_item['int_qty']=0
                                        else:
                                            BranchStockImeiDetails.objects.filter(pk_bint_id=ins_batch_stock['pk_bint_id'],jsn_batch_no__contains={'batch':[dct_item['dct_bchno'][dct_key]]}).update(int_qty=0)
                                            BranchStockDetails.objects.filter(pk_bint_id=ins_batch_stock['fk_details_id']).update(int_qty=0)
                                            dct_item['int_qty']=dct_item['int_qty']-ins_batch_stock['int_qty']
                                if dct_item['int_qty']>0:
                                    ins_grn=GrnDetails.objects.filter(pk_bint_id=dct_key,int_avail__gt=0).values('pk_bint_id','int_avail')
                                    if ins_grn:
                                        if ins_grn[0]['int_avail']>=dct_item['int_qty']:
                                            GrnDetails.objects.filter(pk_bint_id=ins_grn[0]['pk_bint_id']).update(int_avail=(ins_grn[0]['int_avail']-dct_item['int_qty']))
                                            dct_item['int_qty']=0
                                        else:
                                            GrnDetails.objects.filter(pk_bint_id=ins_grn[0]['pk_bint_id']).update(int_avail=0)
                                            dct_item['int_qty']=dct_item['int_qty']-ins_grn[0]['int_avail']
                                    elif not ins_grn or dct_item['int_qty']<0:
                                        # return Response({'status':0,'reason':"no batch number available"})
                                        raise ValueError('no batch number available')
                            else:
                                ins_branch_stock=BranchStockImeiDetails.objects.filter(fk_grn_details_id= int(dct_key),int_qty__gt=0,fk_details__fk_master_id__fk_branch_id=int_branch_from,fk_details__fk_item_id=dct_item.get('fk_item_id'),jsn_batch_no__contains={'batch':[dct_item['dct_bchno'][dct_key]]}).values('pk_bint_id','int_qty','fk_details_id')
                                if ins_branch_stock:
                                    for ins_batch_stock in ins_branch_stock:
                                        if dct_item['int_qty']==0:
                                            break
                                        if ins_batch_stock['int_qty']>=dct_item['int_qty']:
                                            BranchStockImeiDetails.objects.filter(pk_bint_id=ins_batch_stock['pk_bint_id'],jsn_batch_no__contains={'batch':[dct_item['dct_bchno'][dct_key]]}).update(int_qty=F('int_qty')-dct_item['int_qty'])
                                            BranchStockDetails.objects.filter(pk_bint_id=ins_batch_stock['fk_details_id']).update(int_qty=F('int_qty')-dct_item['int_qty'])
                                            dct_item['int_qty']=0
                                        else:
                                            BranchStockImeiDetails.objects.filter(pk_bint_id=ins_batch_stock['pk_bint_id'],jsn_batch_no__contains={'batch':[dct_item['dct_bchno'][dct_key]]}).update(int_qty=0)
                                            BranchStockDetails.objects.filter(pk_bint_id=ins_batch_stock['fk_details_id']).update(int_qty=0)
                                            dct_item['int_qty']=dct_item['int_qty']-ins_batch_stock['int_qty']
                                if dct_item['int_qty']>0:
                                    raise ValueError('no batch number available')
                rst_transfer_qty=StockTransferImeiDetails.objects.filter(fk_details__fk_transfer_id=ins_stocktransfer.pk_bint_id).aggregate(inserted_qty=Sum('int_qty'))
                if not rst_transfer_qty or not rst_transfer_qty['inserted_qty'] or rst_transfer_qty['inserted_qty']!=int_transfered_qty:
                    dct_issue_data = {'data':lst_item_details}
                    with open('transfer_issue.txt','w') as f:
                        f.write(json.dumps(dct_issue_data))
                    raise ValueError('Some issues with stock transfer please contact admin')
                else:
                    return Response({'status':1,'message':'Transfer Successfully Registered'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':str(e)})

class CancelRequest(APIView):
    """cancel request"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_type=request.data.get('type')
            int_request_id=request.data.get('int_id')
            str_remarks=request.data.get('remarks') or ''
            if str_type=='from':
                StockRequest.objects.filter(pk_bint_id = int_request_id).update(int_doc_status=-1)
            else:
                StockRequest.objects.filter(pk_bint_id = int_request_id).update(int_status=4,vchr_rej_remark=str_remarks)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class GetTransferList(APIView):
    """List the internal stock transfer for each branch(transfer as well as transferred)"""
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            str_request=request.GET.get('type')
            if str_request=='from':
                lst_requests=list(StockTransfer.objects.filter(fk_from_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0,1]).annotate(status=Case(When(int_status=0,then=Value('BILLED')),When(int_status=1,then=Value('TRANSFERRED')),When(int_status=2,then=Value('RECEIVED')),When(int_status=3,then=Value('ACKNOWLEDGED')),When(int_status=5,then=Value('PARTIALLY RECIEVED')),default=Value('PENDING'),output_field=CharField())).values('pk_bint_id','dat_transfer','fk_from__vchr_name','fk_to__vchr_name','status','vchr_stktransfer_num').order_by('-dat_transfer','-vchr_stktransfer_num'))
            else:
                lst_requests=list(StockTransfer.objects.filter(fk_to_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0,1]).annotate(status=Case(When(int_status=0,then=Value('BILLED')),When(int_status=1,then=Value('TRANSFERRED')),When(int_status=2,then=Value('RECEIVED')),When(int_status=3,then=Value('ACKNOWLEDGED')),When(int_status=5,then=Value('PARTIALLY RECIEVED')),default=Value('PENDING'),output_field=CharField())).values('pk_bint_id','dat_transfer','fk_from__vchr_name','fk_to__vchr_name','status','vchr_stktransfer_num').order_by('-dat_transfer','-vchr_stktransfer_num'))
            return Response({'status':1, 'request_list' : lst_requests})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})
    def post(self,request):
        try:
            str_request=request.data.get('type')
            dat_to= request.data.get('datTo')
            dat_from= request.data.get('datFrom')
            int_branch = request.data.get('intBranchId')
            # import pdb; pdb.set_trace()
            if str_request=='from':
                lst_requests = StockTransfer.objects.filter(fk_from_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0,1],dat_transfer__lte=dat_to,dat_transfer__gte = dat_from).annotate(status=Case(When(int_status=0,then=Value('BILLED')),When(int_status=1,then=Value('TRANSFERRED')),When(int_status=2,then=Value('RECEIVED')),When(int_status=3,then=Value('ACKNOWLEDGED')),When(int_status=5,then=Value('PARTIALLY RECIEVED')),default=Value('PENDING'),output_field=CharField()),str_user=Concat('fk_created_id__first_name',Value(' '),'fk_created_id__last_name')).values('pk_bint_id','dat_transfer','fk_from__vchr_name','fk_to__vchr_name','status','vchr_stktransfer_num','str_user').order_by('-dat_transfer','-vchr_stktransfer_num')
                lst_stock_ids  = StockTransfer.objects.filter(fk_to_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0,1],dat_transfer__lte=dat_to,dat_transfer__gte = dat_from).values('pk_bint_id')
                if int_branch:
                    lst_requests = lst_requests.filter(fk_to_id = int_branch)
                    # lst_stock_ids = lst_stock_ids.filter(fk_from_id = int_branch)
                lst_ids = lst_requests.values('pk_bint_id')

                ist_details = list(IstDetails.objects.filter(fk_transfer_id__in = lst_ids).values('fk_transfer_id','fk_item_id__fk_product_id__vchr_name'))
                for data in lst_requests:
                    ins_ist_filterd = list(filter(lambda d: d['fk_transfer_id'] in [data['pk_bint_id']], ist_details))
                    lst_product_data = []
                    if ins_ist_filterd:
                        for obj_details in ins_ist_filterd:
                            if obj_details['fk_item_id__fk_product_id__vchr_name'].upper() not in lst_product_data:
                                lst_product_data.append(obj_details['fk_item_id__fk_product_id__vchr_name'])
                    data['list_products'] = lst_product_data
            else:
                lst_requests = StockTransfer.objects.filter(fk_to_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0,1],dat_transfer__lte=dat_to,dat_transfer__gte = dat_from).annotate(status=Case(When(int_status=0,then=Value('BILLED')),When(int_status=1,then=Value('TRANSFERRED')),When(int_status=2,then=Value('RECEIVED')),When(int_status=3,then=Value('ACKNOWLEDGED')),When(int_status=5,then=Value('PARTIALLY RECIEVED')),default=Value('PENDING'),output_field=CharField()),str_user=Concat('fk_created_id__first_name',Value(' '),'fk_created_id__last_name')).values('pk_bint_id','dat_transfer','fk_from__vchr_name','fk_to__vchr_name','status','vchr_stktransfer_num','str_user').order_by('-dat_transfer','-vchr_stktransfer_num')
                # lst_stock_ids  = StockTransfer.objects.filter(fk_to_id =request.user.userdetails.fk_branch_id,int_doc_status__in=[0,1],dat_transfer__lte=dat_to,dat_transfer__gte = dat_from).values('pk_bint_id')
                if int_branch:
                    lst_requests=lst_requests.filter(fk_from_id = int_branch)
                    # lst_stock_ids = lst_stock_ids.filter(fk_from_id = int_branch)
                lst_ids = lst_requests.values('pk_bint_id')
                ins_ist_details = IstDetails.objects.filter(fk_transfer_id__in = lst_ids).values('fk_transfer_id','fk_item_id__fk_product_id__vchr_name')
                for data in lst_requests:
                    ins_ist_filterd = list(filter(lambda d: d['fk_transfer_id'] in [data['pk_bint_id']], ins_ist_details))
                    lst_product_data = []
                    if ins_ist_filterd:
                        for obj_details in ins_ist_filterd:
                            if obj_details['fk_item_id__fk_product_id__vchr_name'].upper() not in lst_product_data:
                                lst_product_data.append(obj_details['fk_item_id__fk_product_id__vchr_name'])
                    data['list_products'] = lst_product_data

                if request.user.userdetails.fk_group.vchr_name.upper() in ['SERVICE MANAGER','SERVICE ENGINEER']:
                    lst_stf_id_with_spare_data = IstDetails.objects.filter(fk_transfer__fk_from__vchr_code__in = ['MCL3','MPL4','MCH'],fk_transfer__dat_transfer__lte=dat_to,fk_transfer__dat_transfer__gte = dat_from,fk_transfer__fk_to_id = request.user.userdetails.fk_branch_id,fk_item__fk_product__vchr_name = 'SPARE').values_list('fk_transfer_id',flat =True)
                    if lst_stf_id_with_spare_data:
                        lst_requests.filter(pk_bint_id__in = lst_stf_id_with_spare_data)

            return Response({'status':1, 'request_list' : list(lst_requests)})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

class TransferView(APIView):
    """Provide data for view transfer from transfer list"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_request=request.data.get('type')
            int_transfer_id=request.data.get('int_id')
            ins_medium={}
            if str_request=='from':
                ins_requests=StockTransfer.objects.filter(pk_bint_id=int_transfer_id).annotate(bln_visible=Case(When(fk_from_id=request.user.userdetails.fk_branch_id,then=Value('True')),default=Value('False'),output_field=CharField())).annotate(status=Case(When(int_status=0,then=Value('BILLED')),When(int_status=1,then=Value('TRANSFERRED')),When(int_status=2,then=Value('RECIEVED')),When(int_status=3,then=Value('ACKNOWLEDGED')),default=Value('PENDING'),output_field=CharField())).values('dat_transfer','fk_to__vchr_name','status','vchr_remarks','vchr_stktransfer_num','bln_visible','int_status','bln_direct_transfer',)
                lst_details=list(IstDetails.objects.filter(fk_transfer__pk_bint_id = int_transfer_id).values('jsn_batch_no','fk_item__vchr_name','int_qty','dbl_rate','jsn_imei','fk_item_id').order_by('fk_item__vchr_name','-pk_bint_id'))
            else :
                ins_requests=StockTransfer.objects.filter(pk_bint_id=int_transfer_id).annotate(bln_visible=Case(When(fk_to_id=request.user.userdetails.fk_branch_id,then=Value('True')),default=Value('False'),output_field=CharField())).annotate(status=Case(When(int_status=0,then=Value('BILLED')),When(int_status=1,then=Value('TRANSFERRED')),When(int_status=2,then=Value('RECIEVED')),When(int_status=3,then=Value('ACKNOWLEDGED')),default=Value('PENDING'),output_field=CharField())).values('dat_transfer','fk_from__vchr_name','status','vchr_remarks','vchr_stktransfer_num','bln_visible','int_status','bln_direct_transfer')
                lst_details=list(IstDetails.objects.filter(fk_transfer__pk_bint_id = int_transfer_id).values('jsn_batch_no','fk_item__vchr_name','int_qty','dbl_rate','jsn_imei','fk_item_id').order_by('fk_item__vchr_name','-pk_bint_id'))
            lst_item=[data['fk_item_id'] for data in lst_details]
            lst_jsns=BranchStockDetails.objects.filter(fk_transfer_details__fk_transfer__pk_bint_id=int_transfer_id,fk_item_id__in=lst_item).values('fk_item__vchr_name','jsn_imei','jsn_imei_dmgd','jsn_batch_no','jsn_imei_avail').order_by('fk_item__vchr_name','-pk_bint_id',)
            lst_avail=[]
            lst_damaged=[]
            lst_missing=[]


            ins_courier=CourierMaster.objects.filter().values('pk_bint_id','vchr_name')
            # import pdb; pdb.set_trace()
            for i in range(len(lst_jsns)):

                #######imeis#########

                lst_temp=[]
                #lst_avail.extend([{'imei':data,'status':'available'} for data in lst_jsns[i]['jsn_imei_avail']['imei']])  ##Commented to fix the avail mismatch issue
                lst_avail.extend([{'imei':data,'status':'available'} for data in lst_jsns[i]['jsn_imei']['imei']])
                lst_damaged.extend([{'imei':data,'status':'damaged'} for data in lst_jsns[i]['jsn_imei_dmgd']['imei']])
                # lst_temp.extend([data for data in lst_details[i]['jsn_imei']['imei'] if data not in lst_jsns[i]['jsn_imei']['imei']])
                # LG
                lst_jsns_data = []
                for data in lst_jsns:
                    lst_jsns_data.extend(data['jsn_imei']['imei'])
                lst_temp.extend([data for data in lst_details[i]['jsn_imei']['imei'] if data not in lst_jsns_data])
                lst_details[i]['imei']=[]
                lst_missing=[{'imei':data,'status':'missing'} for data in lst_temp]
                if lst_missing:
                    lst_details[i]['imei'].extend(lst_missing)
                if lst_damaged:
                    lst_details[i]['imei'].extend(lst_damaged)
                if lst_avail:
                    lst_details[i]['imei'].extend(lst_avail)

                ####batch no.s########

                lst_avail=[]
                lst_avail.extend([{'imei':data,'status':'available'} for data in lst_jsns[i]['jsn_batch_no']['batch']])
                lst_temp=[]
                lst_temp.extend([data for data in lst_details[i]['jsn_batch_no']['batch'] if data not in lst_jsns[i]['jsn_batch_no']['batch']])
                lst_missing=[{'imei':data,'status':'missing'} for data in lst_temp]


                if lst_missing:
                    lst_details[i]['imei'].extend(lst_missing)
                if lst_avail:
                    lst_details[i]['imei'].extend(lst_avail)
                lst_avail=[]
                lst_temp=[]
                lst_damaged = []
                lst_missing = []

            # getting imei and batch number for billed tranfer by processing stock transfer data
            if not lst_jsns:
                for data in lst_details:
                    lst_billed = []
                    if data["jsn_batch_no"]:
                        lst_billed.extend([{'imei':data,'status':'available'} for data in data['jsn_batch_no']['batch']])
                    if data["jsn_imei"]:
                        lst_billed.extend([{'imei':data,'status':'available'} for data in data['jsn_imei']['imei']])
                    data['imei']=lst_billed
            # end processing stock transfer data for imei and batch number fo billed status
            if ins_requests:
                if ins_requests[0]['int_status']>0:
                    ins_medium=TransferModeDetails.objects.filter(fk_transfer_id=int_transfer_id).values('int_medium','vchr_name_responsible','fk_courier__vchr_name','bnt_contact_number','bnt_number','int_packet_no','dbl_expense')
            return Response({'status':1, 'request_data' : ins_requests,'details_data':lst_details,'transfer_details':ins_medium,'courier_name':ins_courier})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class TransferSave(APIView):
    """Save data for transfer medium and history"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            int_stocktrans_id=request.data.get('int_id')
            with transaction.atomic():
                ins_tr_details = TransferModeDetails(
                    int_medium = request.data.get('intMedium'),
                    fk_transfer_id = request.data.get('int_id'),
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
                    fk_courier_id=request.data.get('int_courier_id')

                )
                ins_tr_details.save()
                ins_th_details = TransferHistory(
                    vchr_status = 'TRANSFERRED',
                    fk_transfer_id = request.data.get('int_id'),
                    fk_created_id = request.user.id,
                    dat_created = datetime.now(),
                    fk_updated_id = request.user.id,
                    dat_updated = datetime.now(),
                    int_doc_status = 0,
                )
                ins_th_details.save()
                # lst_items=[18,31]

                # fk_item_id
                if request.data.get('intMedium') in ('2',2):
                    StockTransfer.objects.filter(pk_bint_id = request.data.get('int_id')).update(int_status=1)
                else:
                    StockTransfer.objects.filter(pk_bint_id = request.data.get('int_id')).update(int_status=1,vchr_vehicle_num=request.data.get('str_vehicle'))

                return Response({'status':1})
        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e)})


class SaveAcknowledge(APIView):
    """Acknowledge save in reciever side"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            with transaction.atomic():
                if request.data['bln_acknowledge']:
                    vchr_status='RECIEVED'
                    StockTransfer.objects.filter(pk_bint_id = request.data.get('int_id')).update(int_status=2)

                else:
                    vchr_status='PARTIALLY RECIEVED'
                    StockTransfer.objects.filter(pk_bint_id = request.data.get('int_id')).update(int_status=5)
                str_request=request.GET.get('type')
                TransferModeDetails.objects.filter(fk_transfer_id=request.data.get('int_id')).update(int_packet_received=request.data.get('int_packets'))
                ins_th_details = TransferHistory(
                    vchr_status = vchr_status,
                    fk_transfer_id = request.data.get('int_id'),
                    fk_created_id = request.user.id,
                    dat_created = datetime.now(),
                    fk_updated_id = request.user.id,
                    dat_updated = datetime.now(),
                    int_doc_status = 0,
                )
            ins_th_details.save()

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})



class GetImeiList(APIView):
    """List all imeie available for particular product for a branch"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_item=request.data.get('fk_item_id')
            dct_imei={}
            dct_batch={}
            dct_imei_branch = {}
            dct_batch_branch = {}
            dct_age={}
            dct_batch_age={}

            # return Response({"status":1,"dct_imei":{"717":["GBM0CS190088","GBM0CS190097"]},"dct_batch":{"717":[]},"dct_age":{"GBM0CS190088":{"int_age":1194,"int_qty":1},"GBM0CS190097":{"int_age":1194,"int_qty":1}},"dct_batch_age":{}})
            if request.data['fk_branch_id']:
                int_type=Branch.objects.filter(pk_bint_id=request.user.userdetails.fk_branch_id).values('int_type').first()['int_type']
                if int_type in [2,3]:
                    ins_imei = GrnDetails.objects.filter(int_avail__gte=1,fk_purchase__fk_branch_id=request.user.userdetails.fk_branch_id,fk_item_id=int_item).values('jsn_imei_avail','pk_bint_id','fk_purchase__dat_purchase')
                    if ins_imei:
                        dct_imei={}
                        for data  in ins_imei:
                            lst_saleable = copy.deepcopy(data['jsn_imei_avail']['imei_avail'])
                            for imei in data['jsn_imei_avail']['imei_avail']:
                                rst_non_saleable=NonSaleable.objects.filter(fk_item_id = int_item,int_status = 0,jsn_non_saleable__icontains=imei)
                                if rst_non_saleable:
                                    lst_saleable.remove(imei)
                            dct_imei_warehouse={datas:{'int_age':(datetime.now() - data['fk_purchase__dat_purchase']).days,'int_qty':1 } for datas in lst_saleable}
                            # dct_imei_warehouse={data['pk_bint_id']:{'int_age':(datetime.now() - data['fk_purchase__dat_purchase']).days,'int_qty':1 , 'batch':datas} for datas in data['jsn_imei_avail']['imei_avail']}
                            dct_age.update(dct_imei_warehouse)
                            if data['pk_bint_id'] in dct_imei:
                                dct_imei[data['pk_bint_id']].extend(lst_saleable)
                            else:
                                dct_imei[data['pk_bint_id']]=lst_saleable
                        # dct_imei ={data['pk_bint_id']:data['jsn_imei_avail']['imei_avail'] for data in ins_imei}
                    ins_batch_no=GrnDetails.objects.filter(int_avail__gte=1,fk_purchase__fk_branch_id=request.user.userdetails.fk_branch_id,fk_item_id=int_item).values('vchr_batch_no','pk_bint_id','fk_purchase__dat_purchase','int_avail')
                    if ins_batch_no:
                        dct_batch={}
                        for data  in ins_batch_no:
                            # dct_age[data['vchr_batch_no']]={}
                            # dct_age[data['vchr_batch_no']]['int_age']=(datetime.now() - data['fk_purchase__dat_purchase']).days
                            # dct_age[data['vchr_batch_no']]['int_qty'] = data['int_avail']

                            dct_batch_age[data['pk_bint_id']]={}
                            dct_batch_age[data['pk_bint_id']]['int_age']=(datetime.now() - data['fk_purchase__dat_purchase']).days
                            dct_batch_age[data['pk_bint_id']]['int_qty'] = data['int_avail']
                            dct_batch_age[data['pk_bint_id']]['batch'] = data['vchr_batch_no']

                            if data['pk_bint_id'] in dct_batch:
                                #pass
                                dct_batch[data['pk_bint_id']].extend(data['vchr_batch_no'])
                            else:
                                dct_batch[data['pk_bint_id']]=[data['vchr_batch_no']]
                        # dct_batch={data['pk_bint_id']:[data['vchr_batch_no']] for data in ins_batch_no}
                    ins_imei = BranchStockImeiDetails.objects.filter(int_qty__gte=1,fk_details__fk_master__fk_branch_id=request.user.userdetails.fk_branch_id,fk_details__fk_item_id=int_item).values('jsn_imei','fk_grn_details_id','fk_details__fk_master__dat_stock')
                    if ins_imei:
                        dct_imei_branch={}
                        for data  in ins_imei:
                            lst_saleable = copy.deepcopy(data['jsn_imei']['imei'])
                            for imei in data['jsn_imei']['imei']:
                                rst_non_saleable=NonSaleable.objects.filter(fk_item_id = int_item,int_status = 0,jsn_non_saleable__icontains=imei)
                                if rst_non_saleable:
                                    lst_saleable.remove(imei)
                            dct_imei_branch_temp={datas:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty':1 } for datas in lst_saleable}
                            dct_age.update(dct_imei_branch_temp)
                            if data['fk_grn_details_id'] in dct_imei:
                                dct_imei[data['fk_grn_details_id']].extend(lst_saleable)
                            else:
                                dct_imei[data['fk_grn_details_id']]=lst_saleable
                        # dct_imei_branch={data['fk_grn_details_id']:data['jsn_imei']['imei'] for data in ins_imei}

                    ins_batch=BranchStockImeiDetails.objects.filter(int_qty__gte=1,fk_details__fk_master__fk_branch_id=request.user.userdetails.fk_branch_id,fk_details__fk_item_id=int_item).values('jsn_batch_no','fk_grn_details_id','fk_details__fk_master__dat_stock','int_qty')
                    if ins_batch:
                        dct_batch_branch=[]
                        for data  in ins_batch:
                            # dct_branch_branch_temp={datas:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty' :data['int_qty'] } for datas in data['jsn_batch_no']['batch']}
                            #dct_branch_branch_temp={data['fk_grn_details_id']:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty' :data['int_qty'],'batch': datas} for datas in data['jsn_batch_no']['batch']}
                            if data['fk_grn_details_id'] in dct_batch_age:
                                dct_batch_age[data['fk_grn_details_id']]['int_qty']+=data['int_qty']
                            else:
                                dct_batch_age[data['fk_grn_details_id']]={}
                                dct_batch_age[data['fk_grn_details_id']]['int_age']=(datetime.now() - data['fk_details__fk_master__dat_stock']).days
                                dct_batch_age[data['fk_grn_details_id']]['int_qty'] = data['int_qty']
                                dct_batch_age[data['fk_grn_details_id']]['batch'] = data['jsn_batch_no']['batch']
                                # dct_batch_age.update(dct_branch_branch_temp)
                            if data['fk_grn_details_id'] in dct_batch:
                                pass
                                #dct_batch[data['fk_grn_details_id']].extend(data['jsn_batch_no']['batch'])
                            else:
                                dct_batch[data['fk_grn_details_id']]=data['jsn_batch_no']['batch']

                        # dct_batch_branch={data['fk_grn_details_id']:data['jsn_batch_no']['batch'] for data in ins_batch}


                    if (dct_imei or dct_imei_branch) or (dct_batch or dct_batch_branch):
                        dct_imei.update(dct_imei_branch)
                        dct_batch.update(dct_batch_branch)

                        return Response({'status':1, 'dct_imei' : dct_imei,'dct_batch':dct_batch,'dct_age':dct_age,'dct_batch_age' :dct_batch_age})
                    else:

                        return Response({'status':0, 'reason' : 'no imei available'})

                else:
                    ins_imei=BranchStockImeiDetails.objects.filter(int_qty__gte=1,fk_details__fk_master__fk_branch_id=request.user.userdetails.fk_branch_id,fk_details__fk_item_id=int_item).values('jsn_imei','fk_grn_details_id','fk_details__fk_master__dat_stock')
                    if ins_imei:
                        dct_imei={}
                        for data  in ins_imei:
                            lst_saleable = copy.deepcopy(data['jsn_imei']['imei'])
                            for imei in data['jsn_imei']['imei']:
                                rst_non_saleable=NonSaleable.objects.filter(fk_item_id = int_item,int_status = 0,jsn_non_saleable__icontains=imei)
                                if rst_non_saleable:
                                    lst_saleable.remove(imei)
                            dct_imei_branch={datas:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty':1 } for datas in lst_saleable}
                            dct_age.update(dct_imei_branch)
                            if data['fk_grn_details_id'] in dct_imei:
                                dct_imei[data['fk_grn_details_id']].extend(lst_saleable)
                            else:
                                dct_imei[data['fk_grn_details_id']]=lst_saleable

                        # dct_imei={data['fk_grn_details_id']:data['jsn_imei']['imei'] for data in ins_imei}
                    ins_batch=BranchStockImeiDetails.objects.filter(int_qty__gte=1,fk_details__fk_master__fk_branch_id=request.user.userdetails.fk_branch_id,fk_details__fk_item_id=int_item).values('jsn_batch_no','fk_grn_details_id','fk_details__fk_master__dat_stock','int_qty')
                    if ins_batch:
                        dct_batch={}
                        for data  in ins_batch:
                            if data['fk_grn_details_id'] in dct_batch_age:
                                dct_batch_age[data['fk_grn_details_id']]['int_qty']+=data['int_qty']
                            else:
                                dct_batch_age[data['fk_grn_details_id']]={}
                                dct_batch_age[data['fk_grn_details_id']]['int_age']=(datetime.now() - data['fk_details__fk_master__dat_stock']).days
                                dct_batch_age[data['fk_grn_details_id']]['int_qty'] = data['int_qty']
                                dct_batch_age[data['fk_grn_details_id']]['batch'] = data['jsn_batch_no']['batch']
                                # dct_batch_age.update(dct_branch_branch_temp)
                            if data['fk_grn_details_id'] in dct_batch:
                                pass
                                #dct_batch[data['fk_grn_details_id']].extend(data['jsn_batch_no']['batch'])
                            else:
                                dct_batch[data['fk_grn_details_id']]=data['jsn_batch_no']['batch']
                            # dct_batch_branch={data['fk_grn_details_id']:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty' :data['int_qty'] ,'batch': datas} for datas in data['jsn_batch_no']['batch']}

                            # dct_batch_age.update(dct_batch_branch)

                            # if data['fk_grn_details_id'] in dct_batch:
                            #     dct_batch[data['fk_grn_details_id']].extend(data['jsn_batch_no']['batch'])
                            # else:
                            #     dct_batch[data['fk_grn_details_id']]=data['jsn_batch_no']['batch']
                        # dct_batch={data['fk_grn_details_id']:data['jsn_batch_no']['batch'] for data in ins_batch}
                        # import pdb; pdb.set_trace()
                        return Response({'status':1, 'dct_imei' :dct_imei,'dct_batch':dct_batch,'dct_age':dct_age,'dct_batch_age' : dct_batch_age})
                    else:
                        return Response({'status':0, 'reason' : 'no imei available'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class ApproveMail(APIView):
    permission_classes = [AllowAny]
    def get(self, request, hash=None):
        """Approve/Reject leave through mail"""
        try:
            if hash:
                ins_approve = StockRequest.objects.filter(vchr_approve = hash, int_status = 1).values()
                ins_reject = StockRequest.objects.filter(vchr_reject = hash, int_status = 1).values()
                if ins_approve:
                    ins_approve.update(int_status = 2)
                    vchr_statusmsg = 'approved'
                elif ins_reject:
                    ins_approve.update(int_status = 4)
                    vchr_statusmsg = 'rejected'
                else:
                    return render(request,template_name = 'error.html')
                return render(request,template_name = 'success.html')
            else:
                return render(request,template_name = 'invalid.html')
        except Exception as e:
            return JsonResponse({'error':'error'})



def hash_approve(ins_stockrequest,vchr_status):
    try:
        # import pdb; pdb.set_trace()
        arg = [ins_stockrequest.vchr_stkrqst_num,
        str(ins_stockrequest.dat_expected),
        str(ins_stockrequest.dat_created),
        str(ins_stockrequest.pk_bint_id),
        str(ins_stockrequest.fk_created),
        str(ins_stockrequest.fk_created),
        str(vchr_status)
        ]
        hex1 = uuid3(NAMESPACE_DNS,arg[0]).hex
        hex2 = uuid3(NAMESPACE_DNS,arg[1]).hex
        hex3 = uuid3(NAMESPACE_DNS,arg[2]).hex
        hex4 = uuid3(NAMESPACE_DNS,arg[3]).hex
        hex5 = uuid3(NAMESPACE_DNS,arg[4]).hex
        hex6 = uuid3(NAMESPACE_DNS,arg[5]).hex
        hex7 = uuid3(NAMESPACE_DNS,arg[6]).hex
        if random() < 0.5:
            leave_hex = hex1[:12]+hex2[:12]+hex3[:2]+hex4[:2]+hex5[:2]+hex6[:2]+hex7[:2]
        else:
            leave_hex = hex1[-12:]+hex2[-12:]+hex3[-2:]+hex4[-2:]+hex5[-2:]+hex6[-2:]+hex7[-2:]
        return leave_hex
    except Exception as e:
        return False


def print_transfer_recipt(int_st_id):
    try:

        rst_stock_transfer = IstDetails.objects.filter(fk_transfer_id = int_st_id).values('fk_transfer__fk_to__vchr_name','fk_transfer__fk_to__vchr_code','fk_transfer__fk_to__vchr_address',\
                            'fk_transfer__fk_to__vchr_phone','fk_transfer__fk_to__fk_states__vchr_name','fk_transfer__fk_to__fk_states__vchr_code',\
                            'fk_transfer__vchr_remarks','fk_transfer__vchr_stktransfer_num','fk_transfer__dat_transfer','fk_item__vchr_name','fk_item__fk_product__vchr_name','fk_item__fk_item_category__vchr_hsn_code','fk_item__fk_item_category__json_tax_master',\
                            'int_qty','dbl_rate','jsn_batch_no','jsn_imei','fk_transfer__fk_from__fk_states_id','fk_transfer__fk_to__fk_states_id','fk_transfer__fk_from__vchr_address',\
                            'fk_transfer__fk_from__vchr_phone','fk_transfer__fk_from__vchr_email','fk_transfer__fk_from__vchr_name','fk_transfer__fk_from__vchr_code','fk_transfer_id__vchr_eway_bill_no','fk_transfer__vchr_irn_no','fk_transfer__txt_qr_code'
)

        dct_tax = {str(item['pk_bint_id']):item['vchr_name'] for item in TaxMaster.objects.filter(bln_active=True).values('pk_bint_id','vchr_name')}
        if rst_stock_transfer:
            dct_data = {}
            dct_data['item_details'] = []
            dct_data['total_amount'] = 0
            dct_data['total_qty'] = 0
            dct_data['product_details'] = {}
            for ins_data in rst_stock_transfer:
                dct_item = {}
                dct_item['item_name']= ins_data['fk_item__vchr_name']
                dct_item['product_name']= ins_data['fk_item__fk_product__vchr_name']
                dct_item['hsn_code']= ins_data['fk_item__fk_item_category__vchr_hsn_code']
                dct_item['qty']= ins_data['int_qty']
                dct_item['rate']= round(ins_data['dbl_rate'],2)
                dct_item['taxable_value'] = round(ins_data['dbl_rate'] * ins_data['int_qty'],2)
                # dct_item['taxable_rate'] = round(ins_data['dbl_rate'] * ins_data['int_qty'],2)
                dct_item['tax'] = {dct_tax[tax]:ins_data['fk_item__fk_item_category__json_tax_master'][tax] for tax in ins_data['fk_item__fk_item_category__json_tax_master']}
                if ins_data['fk_transfer__fk_from__fk_states_id']==ins_data['fk_transfer__fk_to__fk_states_id']:
                    if 'IGST' in dct_item['tax']:
                        dct_item['tax'].pop('IGST')
                else:
                    if 'CGST' in dct_item['tax']:
                        dct_item['tax'].pop('CGST')
                    if 'SGST' in dct_item['tax']:
                        dct_item['tax'].pop('SGST')
                dct_item['tax_percentage'] = sum(dct_item['tax'].values())
                # dct_item['taxable_value'] = (ins_data['dbl_rate'] * ins_data['int_qty'])
                #----------------
                dct_item['taxable_value_per_piece'] = round(ins_data['dbl_rate']/((100+dct_item['tax_percentage'])/100),2)
                dct_item['total_taxable_value'] = round(dct_item['taxable_value_per_piece'] * ins_data['int_qty'],2)
                dct_item['total_item_amount'] =  (ins_data['dbl_rate'] * ins_data['int_qty'])


                #----------------
                dct_data['item_details'].append(dct_item)
                dct_data['total_amount'] += dct_item['total_item_amount']
                dct_data['total_qty'] += ins_data['int_qty']
                dct_item['lst_imei'] = ins_data['jsn_imei']['imei']
                dct_item['lst_batch'] = ins_data['jsn_batch_no']['batch']
                if ins_data['fk_item__fk_product__vchr_name'] not in dct_data['product_details'].keys():
                    dct_data['product_details'][ins_data['fk_item__fk_product__vchr_name']] = {}
                    dct_data['product_details'][ins_data['fk_item__fk_product__vchr_name']]['str_product_name'] = ins_data['fk_item__fk_product__vchr_name']
                    dct_data['product_details'][ins_data['fk_item__fk_product__vchr_name']]['total_qty']= ins_data['int_qty']
                    dct_data['product_details'][ins_data['fk_item__fk_product__vchr_name']]['total_amount']=  (ins_data['dbl_rate'] * ins_data['int_qty'])
                    dct_data['product_details'][ins_data['fk_item__fk_product__vchr_name']]['tax_percentage']=  sum(dct_item['tax'].values())
                else:
                    dct_data['product_details'][ins_data['fk_item__fk_product__vchr_name']]['total_qty']+= ins_data['int_qty']
                    dct_data['product_details'][ins_data['fk_item__fk_product__vchr_name']]['total_amount']+=  (ins_data['dbl_rate'] * ins_data['int_qty'])
            dct_data['branch_name'] = ins_data['fk_transfer__fk_to__vchr_name']
            dct_data['from_branch_GSTIN'] = '32AAAFZ4615J1Z8'
            dct_data['branch_GSTIN'] = '32AAAFZ4615J1Z8'
            dct_data['fk_transfer_id__vchr_eway_bill_no'] =  ins_data['fk_transfer_id__vchr_eway_bill_no']

            str_reciept_name = 'DELIVERY CHALLAN'
            if ins_data['fk_transfer__fk_to__vchr_code']=='AGY':
                dct_data['branch_GSTIN'] = '32AAIFC7578H2Z7'
                str_reciept_name = 'TAX INVOICE'
                dct_data['branch_name'] = 'CALICUT MOBILE L L P (Angamaly)'
            if ins_data['fk_transfer__fk_from__vchr_code']=='AGY':
                dct_data['from_branch_GSTIN'] = '32AAIFC7578H2Z7'

            dct_data['branch_name_from'] = ins_data['fk_transfer__fk_from__vchr_name']
            dct_data['from_address'] = ins_data['fk_transfer__fk_from__vchr_address']
            dct_data['from_phone'] = round(float(ins_data['fk_transfer__fk_from__vchr_phone'])) if ins_data['fk_transfer__fk_from__vchr_phone'] else None
            dct_data['from_mail'] = ins_data['fk_transfer__fk_from__vchr_email'] if ins_data['fk_transfer__fk_from__vchr_email'] else ''

            dct_data['address'] = ins_data['fk_transfer__fk_to__vchr_address']
            dct_data['phone'] = round(float(ins_data['fk_transfer__fk_to__vchr_phone'])) if ins_data['fk_transfer__fk_to__vchr_phone'] else None
            dct_data['transfer_date'] = datetime.strftime(ins_data['fk_transfer__dat_transfer'],'%d-%m-%Y')
            dct_data['transfer_num'] = ins_data['fk_transfer__vchr_stktransfer_num']
            dct_data['remarks'] = ins_data['fk_transfer__vchr_remarks'] or ''
            dct_data['state'] = ins_data['fk_transfer__fk_to__fk_states__vchr_name'].title()+"/"+ins_data['fk_transfer__fk_to__fk_states__vchr_code']
            if dct_data['branch_name'] == 'CALICUT MOBILE L L P (Angamaly)':
                dct_data['tcs']= round(dct_data['total_amount']*0.00075,2)
                dct_data['total_amount'] = dct_data['total_amount']+dct_data['tcs']
            dct_data['round_off'] = round(round(dct_data['total_amount']) - round(dct_data['total_amount'],2),2)
            dct_data['total_amount'] = round(dct_data['total_amount'])
            dct_data['vchr_irn_no'] = ins_data['fk_transfer__vchr_irn_no']
            dct_data['txt_qr_code'] = ins_data['fk_transfer__txt_qr_code']
            str_amount_words=num2words.num2words(dct_data['total_amount']).title().split("Point")
            if len(str_amount_words)==2:
                str_amount_words=str_amount_words[0]+" Rupees and "+str_amount_words[1]+" Paise only/-"
            else:
                str_amount_words=str_amount_words[0] +" Rupees only/-"
            dct_data['total_amount_words'] = str_amount_words

            html_data = """
            <!doctype html>
                <html>
                    <head>
                    <meta charset="utf-8">
                        <title>Untitled Document</title>
	                    <style>

                        	.container{
                        			         width:1170px;
                        			         margin:auto;

                    		      }
                            .section1{
                   			        width:64%;
                   			        float: left;
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
                    	</style>
                    </head>

                    <body>
	                   <div class="container">
                        <div style="text-align:right; padding-bottom: 15px; margin-bottom: 15px; line-height:18px;">
                            <img src ="http://www.gdot.in/theme/images/store.png" style="float:left;display: block;" width="100px" height="100px">
                            <h2 style="font-weight:bold; font-size:20px; margin:0; color:#1c252b;">MyG</h2>
                            <h2 style="font-weight:100; font-size:14px; margin:0; color:#1c252b;">"""+dct_data['branch_name_from']+"""</h2>
                            <h2 style="font-weight:100; font-size:14px; margin:0; color:#1c252b;">"""+(dct_data['from_address'].title() if dct_data['from_address'] else '')+"""</h2>
                            <h2 style="font-weight:100; font-size:14px; margin:0; color:#1c252b;"> GSTIN: """+dct_data['from_branch_GSTIN'] +"""</h2>
                            """
            if dct_data['from_phone']:
                html_data +="""<h3 style="font-weight:100; font-size:14px; margin:5px 0; color:#1c252b;">"""+str(dct_data['from_phone'])+"""</h3>"""
            if dct_data['from_mail']:
                html_data +="""<h4 style="font-weight:100; font-size:14px; margin:5px 0; color:#1990e4;">"""+dct_data['from_mail']+"""</h4>"""
            html_data +="""<h4 style="font-weight:100; font-size:14px; margin:5px 0; color:#1c252b;">"""+datetime.strftime(datetime.now(),'%d-%m-%Y %H:%M %p')+"""</h4>
                        </div>

                        <div class="col-sm-12 col-xs-12 ">
                            <h1 style="font-weight:bold; text-align:center; font-size:30px; margin-left:8px;  color:green;">"""+str_reciept_name+"""</h1>
                        </div>
                        <table id="voucher">
				                    <tbody>
						    <tr>
								<td style="padding: 3px !important;">To,</td>
								<td style="text-align: right;padding: 3px !important;">Doc No :</td>
								<td style="text-align: right;width: 200px;padding: 3px !important;font-weight: 600;">"""+dct_data['transfer_num']+"""</td>
						    </tr>
						    <tr>

							    <td style="padding: 3px 3px 3px 44px !important;">
									"""+(dct_data['branch_name'].title() if dct_data['branch_name'] else '')+ """<br>
                                    """+(dct_data['address'].title() if dct_data['address'] else '')+"""
                                </td>
								<td style="text-align: right;padding: 3px !important;">DOC Date :</td>
								<td style="text-align: right;width: 110px;padding: 3px !important;font-weight: 600;">"""+str(dct_data['transfer_date'])+"""</td>
						    </tr>
						    <tr>

							    <td style="padding:3px 3px 3px 44px  !important;">GSTIN:&nbsp;<span style="font-weight: 600;">"""+str(dct_data['branch_GSTIN'])+"""</span>,</td>
								<td style="text-align: right;padding: 3px 3px 3px 44px  !important;">State/Code :</td>
								<td style="text-align: right;width: 110px;padding: 3px 3px 3px 44px !important;font-weight: 600;">"""+dct_data['state']+"""</td>
						    </tr>
						    <tr>
								 <td style="padding:3px 3px 3px 44px  !important;">Phone No:&nbsp;<span style="font-weight: 600;">"""+str(dct_data['phone'])+"""</span>
								</td>"""
            if dct_data['fk_transfer_id__vchr_eway_bill_no']:
                        html_data +="""<br><td style="text-align: right;padding: 3px 3px 3px 44px  !important;">Eway Bill No :</td>
								<td style="text-align: right;width: 110px;padding: 3px 3px 3px 44px !important;font-weight: 600;">"""+dct_data['fk_transfer_id__vchr_eway_bill_no']+"""</td>


							"""
            html_data +=                """</tr>


					</tbody> </table>"""

            if dct_data["vchr_irn_no"]:
                if not os.path.exists(settings.MEDIA_ROOT+"/"+dct_data['transfer_num']+"_qr_code.png"):
                    url = pyqrcode.create(dct_data["txt_qr_code"])
                    qr_code_file_name = dct_data['transfer_num']+"_qr_code.png"

                    url.png(settings.MEDIA_ROOT+"/"+qr_code_file_name, scale = 6)
                html_data+="""
                        <div class="section1">
    				    <span style="padding:5px; display: flex;">IRN - """+dct_data["vchr_irn_no"]+"""</span>
    				    <div><img style="float:left;width:128px;padding:5px" src='"""+settings.MEDIA_ROOT+"""/"""+dct_data['transfer_num']+"""_qr_code.png'></div>
                        </div>"""



            html_data += """
		     <table id="sales" style="margin-top: 20px;">
				      <thead>
						  <tr style="background-color: whitesmoke;">
								  <th>SNO</th>
								  <th>Particulars</th>
								  <th style="text-align: right">HSN/SAC</th>
								  <th style="text-align: right">Qty</th>
								  <th style="text-align: right">Taxable Value</th>
								  <th style="text-align: right">Total Taxable Value</th>
								  <th style="text-align: right">Taxable Rate</th>
								  <th style="text-align:right;">Amount</th>
								  <th style="text-align:right;">Total Amount</th>
						  </tr>
				      </thead>
				      <tbody>"""
            int_index = 1
            for dct_item in dct_data['item_details']:
                html_data +="""<tr>
							   <td>"""+str(int_index)+"""</td>
							   <td style="width:200px;">"""+dct_item['item_name']+""" <br>"""
                if dct_item['lst_imei']:
                    str_imei = "IMEI :"
                    for index,item in enumerate(dct_item['lst_imei']):
                        if index%2==0:
                            str_imei+= '<br>'+str(item)+','
                        else:
                            str_imei+= str(item)+','
                    html_data += """<span>"""+ str_imei[:-1] +"""</span>"""
                elif dct_item['lst_batch']:
                    str_batch = "Batch No :"
                    for index,item in enumerate(dct_item['lst_batch']):
                        if index%2==0:
                            str_batch+= '<br>'+str(item)+','
                        else:
                            str_batch+= str(item)+','
                    html_data += """<span>"""+ str_batch[:-1] +"""</span>"""
                int_index +=1

                html_data += """</td>
							   <td style="text-align: right">"""+dct_item['hsn_code']+"""</td>
							   <td style="text-align: right">"""+str(dct_item['qty'])+"""</td>
							   <td style="text-align: right">"""+str(dct_item['taxable_value_per_piece'])+"""</td>
							   <td style="text-align: right">"""+str(dct_item['total_taxable_value'] )+"""</td>
							   <td style="text-align: right">"""+str(dct_item['tax_percentage'] )+"""%</td>
							   <td style="text-align: right">"""+str(dct_item['rate'])+"""</td>
							   <td style="text-align: right">"""+str(dct_item['total_item_amount'])+"""</td>
						   </tr>"""
            if dct_data['branch_name']=='CALICUT MOBILE L L P (Angamaly)':
                html_data +="""<tr>
                                                           <td></td>
                                                           <td></td>
                                                           <td></td>
                                                           <td></td>
                                                           <td></td>
                               <td style="text-align: right">TCS </td>
                                                           <td style="text-align: right">"""+str(dct_data['tcs'])+"""</td>
                                                   </tr>"""
            html_data +="""<tr>
							   <td></td>
							   <td></td>
							   <td></td>
							   <td></td>
							   <td></td>
                               <td style="text-align: right">Round Off(+/-)</td>
							   <td style="text-align: right">"""+str(dct_data['round_off'])+"""</td>
						   </tr>
				      </tbody>

				      <tfoot>

					       <tr style="background-color: whitesmoke;">

							    <td colspan="3" style="text-align: left;font-weight: 600;color: #213fad;">Total </td>
							    <td style="text-align: right;font-weight: 600;color: #213fad;">"""+str(dct_data['total_qty'])+"""</td>
							    <td colspan="6" style="text-align: right;font-weight: 600;color: #213fad;">"""+str(dct_data['total_amount'])+"""</td>
					       </tr>
				     </tfoot>
		     </table>
		    <div class="clear"></div>"""






            html_data +="""<table id="sales" style="margin-top: 20px;">
                     <thead>
                         <tr style="background-color: whitesmoke;">
                                 <th>SNO</th>
                                 <th style="text-align: right">Products</th>
                                 <th></th>
                                 <th></th>
                                 <th></th>
                                 <th style="text-align: right">Qty</th>
                                 <th style="text-align: right">Taxable Rate</th>
                                 <th style="text-align:right;">Amount</th>
                         </tr>
                     </thead>
                     <tbody>

                     """
            int_index = 1
            for dct_product in dct_data['product_details'].values():
                html_data += """<tr>
							   <td style="text-align: left">"""+str(int_index)+"""</td>
							   <td style="text-align: right">"""+dct_product['str_product_name']+"""</td>
                               <td></td>
                               <td></td>
                               <td></td>
							   <td style="text-align: right">"""+str(dct_product['total_qty'])+"""</td>
							   <td style="text-align: right">"""+str(dct_product['tax_percentage'])+"""</td>
							   <td style="text-align: right">"""+str(dct_product['total_amount'])+""" </td>
						   </tr>"""
                int_index +=1
            html_data += """</tbody><tfoot>"""
            if dct_data['branch_name']=='CALICUT MOBILE L L P (Angamaly)':
                html_data += """<tr>
                                                           <td style="text-align: left">TCS </td>
                                                           <td></td>
                               <td></td>
                               <td></td>
                               <td></td>
                               <td></td>
                               <td></td>

                               <td style="text-align: right">"""+str(dct_data['tcs'])+"""</td>
                                                   </tr>"""
            html_data += """<tr style="background-color: whitesmoke;">

     							    <td colspan="3" style="text-align: left;font-weight: 600;color: #213fad;">Total </td>
                                     <td></td>
                                     <td></td>
     							    <td style="text-align: right;font-weight: 600;color: #213fad;">"""+str(dct_data['total_qty'])+"""</td>
     							    <td colspan="6" style="text-align: right;font-weight: 600;color: #213fad;">"""+str(dct_data['total_amount'])+"""</td>
     					       </tr>
     				     </tfoot>

                           </table>
                           """

            html_data += """ <p>"""+dct_data['total_amount_words']+"""</p>
     		             <p>"""+dct_data['remarks']+""" </p>"""
            html_data += """

            		    <div style="width: 50%;float:left;">
            				 <p style="font-weight: 600;">Receivers Signature</p>
            		    </div>
            		    <div style="width: 50%;float:right;text-align: right">
            				 <p style="font-weight: 600;">For MyG</p>
            				 <p style="margin-top: 30px">Authorized Signatory</p>
            		    </div>

                    	</div>

                    </body>
                    </html> """


            # pdf_path = settings.MEDIA_ROOT+'/'
            # pdf_name =dct_data['transfer_num']+'.pdf'
            # filename = pdf_path+pdf_name
            # pdfkit.from_string(html_data,filename)
            # return filename
            # =============================================

            file_path = settings.MEDIA_ROOT
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            pdf_name = name_change(dct_data['transfer_num'])+'.pdf'
            filename =  file_path+'/'+pdf_name
            options = {'margin-top': '10.00mm',
                   'margin-right': '10.00mm',
                   'margin-bottom': '10.00mm',
                   'margin-left': '10.00mm',
                   'dpi':400}
            pdfkit.from_string(html_data,filename,options=options)
            fs = FileSystemStorage()
            encoded_string = ''
            if fs.exists(filename):
                with fs.open(filename) as pdf:
                    encoded_string=str(base64.b64encode(pdf.read()))
            file_details = {}
            file_details['file'] = encoded_string
            file_details['file_name'] = pdf_name
            return file_details
    except Exception as e:
        raise



class StockAgeReport(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            int_branch_id=request.data.get('branchId')
            int_brand_id=request.data.get('brandId')
            vchr_imei=''
            ins_branch=BranchStockImeiDetails.objects.filter(fk_details__fk_master__fk_branch_id=int_branch_id,fk_grn_details__fk_purchase__dat_purchase__isnull=False)
            if int_brand_id:
                ins_branch=ins_branch.filter(fk_details__fk_item__fk_brand_id=int_brand_id)

            if request.data.get('productId'):
                int_product_id=request.data.get('productId')
                ins_branch=ins_branch.filter(fk_details__fk_item__fk_product_id=int_product_id)

            if request.data.get('itemId'):
                int_item_id=request.data.get('itemId')
                ins_branch=ins_branch.filter(fk_details__fk_item_id=int_item_id)
            list_branch_imei=list(ins_branch.extra(select={'imei': "jsonb_array_elements(branch_stock_details.jsn_imei->'imei')",'batch_no':"'--'",'bln_imei':'true','total_age':"ROUND(EXTRACT(EPOCH FROM now()::timestamp-grn_master.dat_purchase::timestamp)/86400)",'branch_age':"ROUND(EXTRACT(EPOCH FROM now()::timestamp - branch_stock_master.dat_stock::timestamp)/86400)"}).values('batch_no','imei','branch_age','int_qty','total_age','fk_details__fk_item__fk_brand__vchr_name' , 'fk_details__fk_item__fk_product__vchr_name' ,'fk_details__fk_master__fk_branch__vchr_name','fk_details__fk_item__vchr_name','bln_imei'))

            list_branch_imei.extend(list(ins_branch.extra(select={'batch_no': "jsonb_array_elements(branch_stock_details.jsn_batch_no->'batch')","imei":"'--'",'bln_imei':'false','total_age':"ROUND(EXTRACT(EPOCH FROM now()::timestamp-grn_master.dat_purchase::timestamp)/86400)",'branch_age':"ROUND(EXTRACT(EPOCH FROM now()::timestamp - branch_stock_master.dat_stock::timestamp)/86400)"}).values('batch_no','imei','branch_age','int_qty','total_age','fk_details__fk_item__fk_brand__vchr_name' , 'fk_details__fk_item__fk_product__vchr_name' ,'fk_details__fk_master__fk_branch__vchr_name','fk_details__fk_item__vchr_name','bln_imei')))
            return Response({'status':1,'lst_data':list_branch_imei})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':'Failed'})



class PurchaseRequestGenerateApi(APIView):
    def post(self,request):
        try:
            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')
            # import pdb; pdb.set_trace()
            lst_requestslist = IsrDetails.objects.filter(fk_request__fk_to__int_type__in=[2,3],fk_request__dat_request__date__gte=dat_from,fk_request__dat_request__date__lte=dat_to).values('fk_item_id','fk_item__vchr_name','fk_item__vchr_item_code','fk_item__fk_brand__vchr_name','fk_item__fk_product__vchr_name').annotate(int_Qty=Sum('int_qty')).order_by('fk_item__fk_product_id','fk_item__fk_brand_id')
            if request.data.get('productId'):
                lst_requestslist = lst_requestslist.filter(fk_item__fk_product_id=request.data.get('productId'))
            if request.data.get('brandId'):
                lst_requestslist = lst_requestslist.filter(fk_item__fk_brand_id=request.data.get('brandId'))
            lst_request_item = []
            if lst_requestslist:
                for ins_item in lst_requestslist:
                    dct_item={}
                    dct_item['item_id'] = ins_item['fk_item_id']
                    dct_item['item_code'] = ins_item['fk_item__vchr_item_code']
                    dct_item['item_name'] = ins_item['fk_item__vchr_name']
                    dct_item['product'] = ins_item['fk_item__fk_product__vchr_name']
                    dct_item['brand'] = ins_item['fk_item__fk_brand__vchr_name']
                    dct_item['bln_true'] = False
                    dct_item['bln_check'] = False
                    dct_item['item_requested_qty'] = ins_item['int_Qty']
                    dct_item['item_needed_qty'] = ins_item['int_Qty']
                    ins_stock_quantity = BranchStockDetails.objects.filter(fk_item_id = ins_item['fk_item_id'],fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_qty'))
                    ins_grn_quantity = []
                    if request.user.userdetails.fk_branch.int_type in [2,3]:
                        ins_grn_quantity = GrnDetails.objects.filter(fk_item_id = ins_item['fk_item_id'],fk_purchase__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_avail'))
                    dct_item['item_stock_qty']= ins_stock_quantity[0]['int_Qty'] if ins_stock_quantity else 0 + ins_grn_quantity[0]['int_Qty'] if ins_grn_quantity else 0
                    if dct_item['item_stock_qty']:
                        dct_item['item_needed_qty']= dct_item['item_stock_qty']-dct_item['item_requested_qty']
                    lst_request_item.append(dct_item)
            return Response({'status':1,'lst_data':lst_request_item})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

    def put(self,request):
        try:
            # import pdb; pdb.set_trace()
            lst_data = request.data.get('lstDetails')
            dat_expected = request.data.get('datExpected')
            int_supplier = request.data.get('intVendor')
            ins_purchase = PurchaseRequest(
            fk_supplier_id=int_supplier,
            fk_branch_id=request.user.userdetails.fk_branch_id,
            dat_request=dat_expected,
            int_status=0,
            fk_created_id=request.user.id,
            dat_created=datetime.now()
            )
            ins_purchase.save()
            lst_query_set=[]
            for dct_item in lst_data:
                if not dct_item['bln_true']:
                    continue
                ins_details=PurchaseRequestDetails(
                fk_request_id = ins_purchase.pk_bint_id,
                fk_item_id = dct_item['item_id'],
                int_qty = dct_item['item_requested_qty']
                )
                lst_query_set.append(ins_details)
            if lst_query_set:
                PurchaseRequestDetails.objects.bulk_create(lst_query_set)

            return Response({'status':1,'message':'success'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

class SupplierTypeahead(APIView):
    def post(self,request):
        try:
            str_search_term=request.data.get('term')
            lst_supplier=list(Supplier.objects.filter(Q(vchr_code__icontains = str_search_term,is_act_del = 0) | Q(vchr_name__icontains = str_search_term,is_act_del = 0)).values('pk_bint_id','vchr_code','vchr_name'));
            return Response({'status':1, 'supplier_list' : lst_supplier})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class SalesReportPurchase(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            grn_filter = {}
            grn_filter['fk_purchase__dat_purchase__gte'] = request.data.get('datFrom')
            grn_filter['fk_purchase__dat_purchase__lte'] = request.data.get('datTo')
            grn_filter['int_avail__gt'] = 0

            branch_filter = {}
            branch_filter['fk_master__dat_stock__gte'] = request.data.get('datFrom')
            branch_filter['fk_master__dat_stock__lte'] = request.data.get('datTo')
            branch_filter['int_qty__gt'] = 0

            if request.data.get('fk_brand_id'):
                grn_filter['fk_item__fk_brand_id']=request.data.get('fk_brand_id')
                branch_filter['fk_item__fk_brand_id']=request.data.get('fk_brand_id')

            if request.data.get('fk_product_id'):
                grn_filter['fk_item__fk_product_id']=request.data.get('fk_product_id')
                branch_filter['fk_item__fk_product_id']=request.data.get('fk_product_id')
            if request.data.get('fk_item_id'):
                grn_filter['fk_item_id']=request.data.get('fk_item_id')
                branch_filter['fk_item_id']=request.data.get('fk_item_id')
            if request.data.get('fk_item_category_id'):
                grn_filter['fk_item__fk_item_category_id']=request.data.get('fk_item_category_id')
                branch_filter['fk_item__fk_item_category_id']=request.data.get('fk_item_category_id')
            if request.data.get('fk_item_group_id'):
                grn_filter['fk_item__fk_item_group_id']=request.data.get('fk_item_group_id')
                branch_filter['fk_item__fk_item_group_id']=request.data.get('fk_item_group_id')




            # qry_branch=BranchStockDetails.objects.filter(dat_stock__gte=request.data.get('datFrom'),dat_stock__lte=request.data.get('datTo'))
            # qry_grn =GrnDetails.objects.filter(fk_purchase__dat_purchase__gte=request.data.get('datFrom'),fk_purchase__dat_purchase__lte=request.data.get('datFrom'))
            # if request.data.get('fk_brand_id'):
            #     qry_grn=qry_grn.filter(fk_item__fk_brand_id=request.data.get('fk_brand_id'))
            #     qry_branch=qry_branch.filter(fk_item__fk_brand_id=request.data.get('fk_brand_id'))
            # if request.data.get('fk_product_id'):
            #     qry_grn=qry_grn.filter(fk_item__fk_product_id=request.data.get('fk_product_id'))
            #     qry_branch=qry_branch.filter(fk_item__fk_product_id=request.data.get('fk_product_id'))
            # if request.data.get()
            lst_company_stock=GrnDetails.objects.filter(**grn_filter).annotate(month=TruncMonth('fk_purchase__dat_purchase')).values('fk_item__dbl_mop','month','fk_item__vchr_name','fk_purchase__fk_branch__vchr_name','fk_item__fk_product__vchr_name').annotate(sum_qty=Sum('int_avail')).values('fk_item__dbl_mop','fk_item__vchr_name','fk_purchase__fk_branch__vchr_name','fk_item__fk_product__vchr_name').order_by('fk_purchase__fk_branch__vchr_name','fk_item__fk_product__vchr_name','fk_item__vchr_name')
            lst_branch_stock=BranchStockDetails.objects.filter(**branch_filter).annotate(month=TruncMonth('fk_master__dat_stock')).values('fk_item__dbl_mop','month','fk_item__vchr_name','fk_master__fk_branch__vchr_name','fk_item__fk_product__vchr_name').annotate(sum_qty=Sum('int_qty')).values('fk_item__dbl_mop','sum_mop','sum_qty','fk_item__vchr_name','fk_master__fk_branch__vchr_name','fk_item__fk_product__vchr_name','month').order_by('fk_master__fk_branch__vchr_name','fk_item__fk_product__vchr_name','fk_item__vchr_name')

            bln_branch=True if len(lst_branch_stock)>=len(lst_company_stock) else False
            lst_stock=[]
            int_iterator_branch=0
            int_iterator_grn=0
            int_length=len(lst_branch_stock)+len(lst_company_stock)
            for i in range(0,int_length):
                if len(lst_company_stock)>int_iterator_grn and int_iterator_branch<len(lst_branch_stock):
                    if lst_branch_stock[int_iterator_branch]['fk_master__fk_branch__vchr_name']<lst_company_stock[int_iterator_grn]['fk_purchase__fk_branch__vchr_name']:
                        dct_stock={}
                        dct_stock['branch_name']=lst_branch_stock[int_iterator_branch]['fk_master__fk_branch__vchr_name']
                        dct_stock['dbl_mop']=lst_branch_stock[int_iterator_branch]['fk_item__dbl_mop']
                        dct_stock['item_name']=lst_branch_stock[int_iterator_branch]['fk_item__vchr_name']
                        dct_stock['product_name']=lst_branch_stock[int_iterator_branch]['fk_item__fk_product__vchr_name']
                        dct_stock['int_qty']=lst_branch_stock[int_iterator_branch]['int_qty']
                        lst_stock.append(dct_stock)
                        int_iterator_branch+=1
                    else:
                        dct_stock={}
                        dct_stock['branch_name']=lst_company_stock[int_iterator_grn]['fk_purchase__fk_branch__vchr_name']
                        dct_stock['dbl_mop']=lst_company_stock[int_iterator_grn]['fk_item__dbl_mop']
                        dct_stock['item_name']=lst_company_stock[int_iterator_grn]['fk_item__vchr_name']
                        dct_stock['product_name']=lst_company_stock[int_iterator_grn]['fk_item__fk_product__vchr_name']
                        dct_stock['int_qty']=lst_company_stock[int_iterator_branch]['int_avail']

                        lst_stock.append(dct_stock)
                        int_iterator_grn+=1

                elif bln_branch:
                    dct_stock={}
                    dct_stock['branch_name']=lst_branch_stock[int_iterator_branch]['fk_master__fk_branch__vchr_name']
                    dct_stock['dbl_mop']=lst_branch_stock[int_iterator_branch]['fk_item__dbl_mop']
                    dct_stock['item_name']=lst_branch_stock[int_iterator_branch]['fk_item__vchr_name']
                    dct_stock['product_name']=lst_branch_stock[int_iterator_branch]['fk_item__fk_product__vchr_name']
                    dct_stock['int_qty']=lst_branch_stock[int_iterator_branch]['int_qty']

                    lst_stock.append(dct_stock)

                    int_iterator_branch+=1
                else:
                    dct_stock={}
                    dct_stock['branch_name']=lst_company_stock[int_iterator_grn]['fk_purchase__fk_branch__vchr_name']
                    dct_stock['dbl_mop']=lst_company_stock[int_iterator_grn]['fk_item__dbl_mop']
                    dct_stock['item_name']=lst_company_stock[int_iterator_grn]['fk_item__vchr_name']
                    dct_stock['product_name']=lst_company_stock[int_iterator_grn]['fk_item__fk_product__vchr_name']
                    dct_stock['int_qty']=lst_company_stock[int_iterator_branch]['int_avail']
                    lst_stock.append(dct_stock)
                    int_iterator_grn+=1
            df_stock=pd.DataFrame(list(lst_stock))
            excel_file = settings.MEDIA_ROOT+'/stockreport.xlsx'
            file_name_export = excel_file
            writer = pd.ExcelWriter(file_name_export,engine='xlsxwriter')
            df_stock.to_excel(writer,sheet_name='Sheet1',index=True, startrow=0,startcol=0)
            writer.save()
            data = settings.HOSTNAME+'/'+settings.MEDIA_ROOT+'/stockreport.xlsx'

            return Response({'status':1,'lst_stock':lst_stock})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class ImeiBatchScan(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_imei = request.data.get('strImei')
            if request.user.userdetails.fk_branch.int_type in[2,3]:
                ins_stock_quantity = GrnDetails.objects.filter(Q(Q(jsn_imei_avail__imei_avail__has_any_keys  = [str_imei])|Q(vchr_batch_no = str_imei,int_avail__gte = 1)),fk_purchase__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_avail'))
                if not ins_stock_quantity:
                    ins_stock_quantity = BranchStockDetails.objects.filter(Q(Q(jsn_imei_avail__imei__has_any_keys = [str_imei])|Q(jsn_batch_no__icontains = str_imei,int_qty__gte = 1)) ,fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_qty'))
            else:
                ins_stock_quantity = BranchStockDetails.objects.filter(Q(Q(jsn_imei_avail__imei__has_any_keys = [str_imei])|Q(jsn_batch_no__icontains = str_imei,int_qty__gte = 1)) ,fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).values('fk_item_id').annotate(int_Qty =Sum('int_qty'))
            if ins_stock_quantity:
                ins_items = Item.objects.filter(pk_bint_id = ins_stock_quantity[0]['fk_item_id']).annotate(vchr_item_name = Concat('vchr_item_code',Value('-'),'vchr_name')).values('pk_bint_id','vchr_name','vchr_item_name',
                                                                                                                                                                              'vchr_item_code',
                                                                                                                                                                              'fk_item_category__json_tax_master',
                                                                                                                                                                              'dbl_mop','fk_product_id',
                                                                                                                                                                              'imei_status','fk_brand_id',
                                                                                                                                                                              'fk_product__vchr_name',
                                                                                                                                                                              'fk_brand__vchr_name')
                dct_data = {**ins_stock_quantity[0],**ins_items[0]}
                dct_data['int_Qty']=0
                if request.user.userdetails.fk_branch.int_type in[2,3]:
                    ins_grn_qty=GrnDetails.objects.filter(fk_item_id=ins_stock_quantity[0]['fk_item_id'],fk_purchase__fk_branch_id = request.user.userdetails.fk_branch_id).aggregate(int_Qty =Sum('int_avail'))
                    if ins_grn_qty:
                        dct_data['int_Qty']=ins_grn_qty['int_Qty'] or 0

                ins_qty=BranchStockDetails.objects.filter(fk_item_id=ins_stock_quantity[0]['fk_item_id'],fk_master__fk_branch_id = request.user.userdetails.fk_branch_id).aggregate(int_Qty =Sum('int_qty'))
                if ins_qty:
                    dct_data['int_Qty']+=ins_qty['int_Qty'] or 0
                if not dct_data['imei_status']:
                    return Response({'status':0,'data':'Please select an item having serial number'})
            else:
                return Response({'status':0,'data':'No item found'})


            int_item=dct_data['fk_item_id']
            dct_imei={}
            dct_batch={}
            dct_imei_branch = {}
            dct_batch_branch = {}
            dct_age={}
            dct_batch_age={}
            if request.data['fk_branch_id']:
                int_type=Branch.objects.filter(pk_bint_id=request.user.userdetails.fk_branch_id).values('int_type').first()['int_type']
                if int_type in [2,3]:
                    ins_imei = GrnDetails.objects.filter(int_avail__gte=1,fk_purchase__fk_branch_id=request.user.userdetails.fk_branch_id,fk_item_id=int_item).values('jsn_imei_avail','pk_bint_id','fk_purchase__dat_purchase')
                    if ins_imei:
                        dct_imei={}
                        for data  in ins_imei:
                            dct_imei_warehouse={datas:{'int_age':(datetime.now() - data['fk_purchase__dat_purchase']).days,'int_qty':1 } for datas in data['jsn_imei_avail']['imei_avail']}
                            # dct_imei_warehouse={data['pk_bint_id']:{'int_age':(datetime.now() - data['fk_purchase__dat_purchase']).days,'int_qty':1 , 'batch':datas} for datas in data['jsn_imei_avail']['imei_avail']}
                            dct_age.update(dct_imei_warehouse)
                            if data['pk_bint_id'] in dct_imei:
                                dct_imei[data['pk_bint_id']].extend(data['jsn_imei_avail']['imei_avail'])
                            else:
                                dct_imei[data['pk_bint_id']]=data['jsn_imei_avail']['imei_avail']
                        # dct_imei ={data['pk_bint_id']:data['jsn_imei_avail']['imei_avail'] for data in ins_imei}
                    ins_batch_no=GrnDetails.objects.filter(int_avail__gte=1,fk_purchase__fk_branch_id=request.user.userdetails.fk_branch_id,fk_item_id=int_item).values('vchr_batch_no','pk_bint_id','fk_purchase__dat_purchase','int_avail')
                    if ins_batch_no:
                        dct_batch={}
                        for data  in ins_batch_no:
                            # dct_age[data['vchr_batch_no']]={}
                            # dct_age[data['vchr_batch_no']]['int_age']=(datetime.now() - data['fk_purchase__dat_purchase']).days
                            # dct_age[data['vchr_batch_no']]['int_qty'] = data['int_avail']

                            dct_batch_age[data['pk_bint_id']]={}
                            dct_batch_age[data['pk_bint_id']]['int_age']=(datetime.now() - data['fk_purchase__dat_purchase']).days
                            dct_batch_age[data['pk_bint_id']]['int_qty'] = data['int_avail']
                            dct_batch_age[data['pk_bint_id']]['batch'] = data['vchr_batch_no']

                            if data['pk_bint_id'] in dct_batch:
                                dct_batch[data['pk_bint_id']].extend(data['vchr_batch_no'])
                            else:
                                dct_batch[data['pk_bint_id']]=[data['vchr_batch_no']]
                        # dct_batch={data['pk_bint_id']:[data['vchr_batch_no']] for data in ins_batch_no}
                    ins_imei = BranchStockImeiDetails.objects.filter(int_qty__gte=1,fk_details__fk_master__fk_branch_id=request.user.userdetails.fk_branch_id,fk_details__fk_item_id=int_item).values('jsn_imei','fk_grn_details_id','fk_details__fk_master__dat_stock')
                    if ins_imei:
                        dct_imei_branch={}
                        for data  in ins_imei:
                            dct_imei_branch_temp={datas:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty':1 } for datas in data['jsn_imei']['imei']}
                            dct_age.update(dct_imei_branch_temp)
                            if data['fk_grn_details_id'] in dct_imei:
                                dct_imei[data['fk_grn_details_id']].extend(data['jsn_imei']['imei'])
                            else:
                                dct_imei[data['fk_grn_details_id']]=data['jsn_imei']['imei']
                        # dct_imei_branch={data['fk_grn_details_id']:data['jsn_imei']['imei'] for data in ins_imei}

                    ins_batch=BranchStockImeiDetails.objects.filter(int_qty__gte=1,fk_details__fk_master__fk_branch_id=request.user.userdetails.fk_branch_id,fk_details__fk_item_id=int_item).values('jsn_batch_no','fk_grn_details_id','fk_details__fk_master__dat_stock','int_qty')
                    if ins_batch:
                        dct_batch_branch=[]
                        for data  in ins_batch:
                            # dct_branch_branch_temp={datas:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty' :data['int_qty'] } for datas in data['jsn_batch_no']['batch']}
                            dct_branch_branch_temp={data['fk_grn_details_id']:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty' :data['int_qty'],'batch': datas} for datas in data['jsn_batch_no']['batch']}
                            dct_batch_age.update(dct_branch_branch_temp)
                            if data['fk_grn_details_id'] in dct_batch:
                                dct_batch[data['fk_grn_details_id']].extend(data['jsn_batch_no']['batch'])
                            else:
                                dct_batch[data['fk_grn_details_id']]=data['jsn_batch_no']['batch']

                        # dct_batch_branch={data['fk_grn_details_id']:data['jsn_batch_no']['batch'] for data in ins_batch}


                    if (dct_imei or dct_imei_branch) or (dct_batch or dct_batch_branch):
                        dct_imei.update(dct_imei_branch)
                        dct_batch.update(dct_batch_branch)

                        return Response({'status':1,'data':dct_data, 'dct_imei' : dct_imei,'dct_batch':dct_batch,'dct_age':dct_age,'dct_batch_age' :dct_batch_age})
                    else:

                        return Response({'status':0, 'reason' : 'no imei available'})

                else:
                    ins_imei=BranchStockImeiDetails.objects.filter(int_qty__gte=1,fk_details__fk_master__fk_branch_id=request.user.userdetails.fk_branch_id,fk_details__fk_item_id=int_item).values('jsn_imei','fk_grn_details_id','fk_details__fk_master__dat_stock')
                    if ins_imei:
                        dct_imei={}
                        for data  in ins_imei:
                            dct_imei_branch={datas:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty':1 } for datas in data['jsn_imei']['imei']}
                            dct_age.update(dct_imei_branch)

                            if data['fk_grn_details_id'] in dct_imei:
                                dct_imei[data['fk_grn_details_id']].extend(data['jsn_imei']['imei'])
                            else:
                                dct_imei[data['fk_grn_details_id']]=data['jsn_imei']['imei']

                        # dct_imei={data['fk_grn_details_id']:data['jsn_imei']['imei'] for data in ins_imei}
                    ins_batch=BranchStockImeiDetails.objects.filter(int_qty__gte=1,fk_details__fk_master__fk_branch_id=request.user.userdetails.fk_branch_id,fk_details__fk_item_id=int_item).values('jsn_batch_no','fk_grn_details_id','fk_details__fk_master__dat_stock','int_qty')
                    if ins_batch:
                        dct_batch={}
                        for data  in ins_batch:
                            dct_batch_branch={data['fk_grn_details_id']:{'int_age':(datetime.now() - data['fk_details__fk_master__dat_stock']).days,'int_qty' :data['int_qty'] ,'batch': datas} for datas in data['jsn_batch_no']['batch']}

                            dct_batch_age.update(dct_batch_branch)

                            if data['fk_grn_details_id'] in dct_batch:
                                dct_batch[data['fk_grn_details_id']].extend(data['jsn_batch_no']['batch'])
                            else:
                                dct_batch[data['fk_grn_details_id']]=data['jsn_batch_no']['batch']
                        # dct_batch={data['fk_grn_details_id']:data['jsn_batch_no']['batch'] for data in ins_batch}
                        # import pdb; pdb.set_trace()
                        return Response({'status':1,'data':dct_data, 'dct_imei' :dct_imei,'dct_batch':dct_batch,'dct_age':dct_age,'dct_batch_age' : dct_batch_age})
                    else:
                        return Response({'status':0, 'reason' : 'no imei available'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class CourierVehicleList(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_courier=request.data.get('courier_id')
            ins_vehicle=CourierMaster.objects.filter(pk_bint_id=int_courier).values('json_vehicle_no','vchr_gst_no')
            if ins_vehicle:
                dict_data={}
                lst_vehicle=ins_vehicle.first()['json_vehicle_no']
                # dict_data['gst_no']=ins_vehicle.first()['vchr_gst_no']
            else:
                return Response ({'status':0,'reason':'no data found'})
            return Response ({'status':1,'vehicle':lst_vehicle})

        except Exception as e:
            return Response ({'status':0,'reason':str(e)})

class EwayBillGeneration(APIView):
    """Save data for transfer medium and history"""
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            int_stocktrans_id=request.data.get('int_id')
            bln_eway=False
            if StockTransfer.objects.filter(pk_bint_id=int_stocktrans_id,vchr_eway_bill_no__isnull=True):
                bln_eway=True
            StockTransfer.objects.filter(pk_bint_id=int_stocktrans_id,vchr_eway_bill_no__isnull=True).update(vchr_eway_bill_no='EWAY BILL')
            with transaction.atomic():

                in_stock_transfer = StockTransfer.objects.filter(pk_bint_id=int_stocktrans_id).values('fk_to__int_pincode','fk_from__int_pincode','fk_to__flt_latitude','fk_from__vchr_code','fk_to__vchr_code','fk_to__flt_longitude','fk_from__flt_latitude','fk_from__flt_longitude', 'fk_to__fk_location_master__int_code','fk_to__fk_location_master__vchr_location','fk_to__vchr_address','fk_to__vchr_name','fk_from__vchr_gstno','fk_from__vchr_address','fk_from__fk_location_master__vchr_location','fk_from__fk_location_master__int_code','fk_to__vchr_gstno',
'vchr_stktransfer_num','vchr_vehicle_num')
                dict_courier_details = TransferModeDetails.objects.filter(fk_transfer_id=int_stocktrans_id).values('fk_courier__vchr_name','fk_courier__vchr_gst_no').first()

                # raise Exception('error')

                vchr_code_from=in_stock_transfer.values('fk_from__vchr_code')[0]['fk_from__vchr_code']
                vchr_code_to=in_stock_transfer.values('fk_to__vchr_code')[0]['fk_to__vchr_code']

                if not (vchr_code_from.upper() in ('ROC','WHO1','ECO','ITC') and bln_eway):
                        if bln_eway:
                            StockTransfer.objects.filter(pk_bint_id=int_stocktrans_id).update(vchr_eway_bill_no=None)

                        return Response({'status':0,'bln_permitted':False,'reason':'E-Way Bill Generation already generated/not permitted'})

                if not  in_stock_transfer[0].get('vchr_vehicle_num'):
                        StockTransfer.objects.filter(pk_bint_id=int_stocktrans_id).update(vchr_eway_bill_no=None)
                        return Response({'status':0,'bln_permitted':False,'reason':"Can't Generate E-Way Bill because vehicle number not entered"})

                else:
                        try:
                            dict_eway_data={}
                            #generating doc number
                            int_first = str(datetime.today()).replace('-','')
                            str_doc_num = str(in_stock_transfer[0].get('vchr_stktransfer_num'))
                            inst_ist = IstDetails.objects.filter(fk_transfer_id=int_stocktrans_id).values('dbl_rate','fk_item_id','int_qty','fk_item__fk_product__vchr_name','fk_item__fk_item_category__vchr_hsn_code','fk_item__vchr_name','fk_item__fk_item_category__json_tax_master')

                            lst_items = []
                            inst_tax = TaxMaster.objects.values()
                            int_cgst_sum=0
                            int_igst_sum=0
                            int_cess_sum=0
                            int_sgst_sum=0
                            int_sum=0
                            int_sum_without_tax= 0
                            vchr_from_gstin='32AAAFZ4615J1Z8'

                            if vchr_code_to.upper()=='AGY':
                                vchr_to_gstin='32AAIFC7578H2Z7'
                                str_sub_supply_type='1'
                                str_supply_type='O'
                                str_doc_type='INV'
                                bln_tax=True

                            else:
                                vchr_to_gstin='32AAAFZ4615J1Z8'

                                str_sub_supply_type='5'
                                str_supply_type='O'
                                str_doc_type='CHL'
                                bln_tax=False
                            for item in inst_ist:
                                dict_data={}



                                dict_data["productName"] = item['fk_item__vchr_name']
                                dict_data["productDesc"] = item['fk_item__fk_product__vchr_name']
                                dict_data["hsnCode"] = item['fk_item__fk_item_category__vchr_hsn_code'].split('.')[0]
                                # dict_data["quantity"] =item['int_qty']
                                dict_data["qtyUnit"] ='PCS'
                                int_cgst = inst_tax.filter(vchr_name='CGST').values('pk_bint_id').first().get('pk_bint_id')
                                int_igst = inst_tax.filter(vchr_name='IGST').values('pk_bint_id').first().get('pk_bint_id')
                                int_sgst = inst_tax.filter(vchr_name='SGST').values('pk_bint_id').first().get('pk_bint_id')
                                int_kfc = inst_tax.filter(vchr_name='KFC').values('pk_bint_id').first().get('pk_bint_id')


                                # dict_data["sgstRate"] =item['fk_item__fk_item_category__json_tax_master'].get(str(int_sgst))
                                #
                                # dict_data["cgstRate"] =item['fk_item__fk_item_category__json_tax_master'].get(str(int_cgst))
                                #
                                #
                                # dict_data["cessRate"] = item['fk_item__fk_item_category__json_tax_master'].get(str(int_kfc)) or 0
                                # dict_data["igstRate"] = 0
                                dict_data["sgstRate"] =0

                                dict_data["cgstRate"] =0


                                dict_data["cessRate"] = (item['fk_item__fk_item_category__json_tax_master'].get(str(int_kfc)) or 0) if bln_tax else 0

                                dict_data["sgstRate"] =(item['fk_item__fk_item_category__json_tax_master'].get(str(int_sgst)) or 0) if bln_tax else 0

                                dict_data["cgstRate"] =(item['fk_item__fk_item_category__json_tax_master'].get(str(int_cgst)) or 0) if bln_tax else 0


                                dict_data["cessRate"] = (item['fk_item__fk_item_category__json_tax_master'].get(str(int_kfc)) or 0) if bln_tax else 0

                                # dict_data["igstRate"] = (item['fk_item__fk_item_category__json_tax_master'].get(str(int_igst)) or 0) if bln_tax else 0

                                # dict_data["igstRate"] =  0
                                tax_percentage = dict_data["cessRate"] + dict_data["sgstRate"] + dict_data["cgstRate"]
                                dict_data["taxableAmount"] =round((item['dbl_rate']*item['int_qty'])/((100+tax_percentage)/100),2) if bln_tax else (item['dbl_rate']*item['int_qty'])
                                dict_data['quantity']= item['int_qty']
                                # dict_data["cessAdvol"] =0

                                int_cgst_sum += (dict_data["cgstRate"]*dict_data["taxableAmount"])/100
                                # int_igst_sum += (dict_data["igstRate"]*item['dbl_rate']*item['int_qty'])/100
                                int_cess_sum += (dict_data["cessRate"]*dict_data["taxableAmount"])/100
                                int_sgst_sum += (dict_data["sgstRate"]*dict_data["taxableAmount"])/100
                                int_sum += dict_data["taxableAmount"]

                                # int_sum_with_tax += (item['dbl_rate']*item['int_qty'])

                                lst_items.append(dict_data)


                            #
                            int_cgst_sum = round(int_cgst_sum,2)
                            int_cess_sum = round(int_cess_sum,2)
                            int_sgst_sum = round(int_sgst_sum,2)
                            tpl_cur_coord= (in_stock_transfer.values('fk_to__flt_latitude')[0]['fk_to__flt_latitude'],in_stock_transfer.values('fk_to__flt_longitude')[0]['fk_to__flt_longitude'])
                            tpl_other_coord = (in_stock_transfer.values('fk_from__flt_latitude')[0]['fk_from__flt_latitude'],in_stock_transfer.values('fk_from__flt_longitude')[0]['fk_from__flt_longitude'])
                            #

                            dict_eway_data["itemList"]=lst_items

                            lst_address=in_stock_transfer.values('fk_from__vchr_address')[0]['fk_from__vchr_address'].split(',')

                            int_half=len(lst_address)/2
                            fromaddress1=''
                            fromaddress2=''
                            for i in range(round(int_half)):
                                fromaddress1+=lst_address[i]
                            for i in range(round(int_half),len(lst_address)):
                                fromaddress2+=lst_address[i]

                            lst_address=in_stock_transfer.values('fk_to__vchr_address')[0]['fk_to__vchr_address'].split(',')
                            int_half=len(lst_address)/2
                            toaddress1=''
                            toaddress2=''
                            for i in range(round(int_half)):
                                toaddress1+=lst_address[i]
                            for i in range(round(int_half),len(lst_address)):
                                toaddress2+=lst_address[i]
                            #
                            # dict_eway_data ={
                        	# "supplyType": str_supply_type,
                        	# "subSupplyType":str_sub_supply_type,
                        	# "docType": str_doc_type,
                        	# "docNo": str_doc_num,
                        	# "docDate": datetime.strftime(datetime.now(), '%d/%m/%Y'),
                        	# "fromGstin":'05AAACG2115R1ZN' or vchr_from_gstin,
                        	# "fromAddr1": fromaddress1.replace('\n',''),
                        	# "fromAddr2": fromaddress2.replace('\n',''),
                        	# "fromPincode": 560042 or in_stock_transfer.values('fk_from__int_pincode')[0]['fk_from__int_pincode'],
                        	# "actFromStateCode": 29,
                        	# "fromStateCode": 29 ,
                        	# "toGstin":('05AAACG2140A1ZL' if bln_tax else '05AAACG2115R1ZN') or vchr_to_gstin,
                        	# "toAddr1":  toaddress1.replace('\n',''),
                        	# "toAddr2": toaddress2.replace('\n',''),
                        	# "toPincode": (500003 if bln_tax else 560042) or  in_stock_transfer.values('fk_to__int_pincode')[0]['fk_to__int_pincode'],
                        	# "actToStateCode": 36 if bln_tax else 29,
                        	# "toStateCode": 36 if bln_tax else 29,
                        	# "totalValue": int_sum,
                        	# "cgstValue": 0 or (int_cgst_sum  if bln_tax else 0),
                        	# "sgstValue": 0 or (int_sgst_sum  if bln_tax else 0),
                        	# "igstValue": int_igst_sum  if bln_tax else 0,
                        	# "cessValue": int_cess_sum  if bln_tax else 0,
                        	# # "totInvValue": (int_sum + int_cgst_sum + int_sgst_sum + int_cess_sum)  if bln_tax else int_sum ,
                        	# "totInvValue": (int_sum + int_igst_sum + int_cess_sum)  if bln_tax else int_sum ,
                        	# "transporterId": "",
                        	# "transporterName": "",
                        	# "transDocNo": "",
                        	# "transMode": "1",
                        	# "transDistance": 10 or round(geodesic(tpl_cur_coord,tpl_other_coord).km),
                        	# "transDocDate": "",
                        	# "vehicleNo":str(in_stock_transfer[0].get('vchr_vehicle_num')),
                        	# "vehicleType": "R",
                        	# "TransactionType": "1",
                        	# "itemList":lst_items,
                            # "fromTrdName": in_stock_transfer.values('fk_from__vchr_name')[0]['fk_from__vchr_name'],
                            # "fromPlace": in_stock_transfer.values('fk_from__vchr_name')[0]['fk_from__vchr_name'],
                            # "toTrdName": in_stock_transfer.values('fk_to__vchr_name')[0]['fk_to__vchr_name'],
                        	# "toPlace": in_stock_transfer.values('fk_to__vchr_name')[0]['fk_to__vchr_name'],
                            #
                            # }


                            dict_eway_data ={
                        	"supplyType": str_supply_type,
                        	"subSupplyType":str_sub_supply_type,
                        	"docType": str_doc_type,
                        	"docNo": str_doc_num,
                        	"docDate": datetime.strftime(datetime.now(), '%d/%m/%Y'),
                        	"fromGstin":vchr_from_gstin,
                        	"fromAddr1": fromaddress1.replace('\n',''),
                        	"fromAddr2": fromaddress2.replace('\n',''),
                        	"fromPincode": in_stock_transfer.values('fk_from__int_pincode')[0]['fk_from__int_pincode'],
                        	"actFromStateCode": 32,
                        	"fromStateCode": 32 ,
                        	"toGstin":vchr_to_gstin,
                        	"toAddr1":  toaddress1.replace('\n',''),
                        	"toAddr2": toaddress2.replace('\n',''),
                        	"toPincode": in_stock_transfer.values('fk_to__int_pincode')[0]['fk_to__int_pincode'],
                            'dispatchFromGSTIN':vchr_from_gstin,
                        	"actToStateCode": 32,
                        	"toStateCode": 32,
                        	"totalValue": round(int_sum,2),
                        	"cgstValue": int_cgst_sum  if bln_tax else 0,
                        	"sgstValue": int_sgst_sum  if bln_tax else 0,
                        	"igstValue": 0,
                        	"cessValue": int_cess_sum  if bln_tax else 0,
                        	# "totInvValue": (int_sum + int_cgst_sum + int_sgst_sum + int_cess_sum)  if bln_tax else int_sum ,
                        	"totInvValue": round((int_cgst_sum + int_cess_sum + int_sgst_sum + int_sum),2) if bln_tax else round(int_sum,2) ,
                        	"transporterId": "",
                        	"transporterName": "",
                        	"transDocNo": "",
                        	"transMode": "1",
                        	"transDistance": round(geodesic(tpl_cur_coord,tpl_other_coord).km),
                        	"transDocDate": "",
                        	"vehicleNo":str(in_stock_transfer[0].get('vchr_vehicle_num')),
                        	"vehicleType": "R",
                        	"TransactionType": "1",
                        	"itemList":lst_items,
                            "fromTrdName": in_stock_transfer.values('fk_from__vchr_name')[0]['fk_from__vchr_name'],
                            "fromPlace": in_stock_transfer.values('fk_from__vchr_name')[0]['fk_from__vchr_name'],
                            "toTrdName": in_stock_transfer.values('fk_to__vchr_name')[0]['fk_to__vchr_name'],
                        	"toPlace": in_stock_transfer.values('fk_to__vchr_name')[0]['fk_to__vchr_name'],
                            "transporterId":dict_courier_details.get('fk_courier__vchr_gst_no') or '',
                            "transporterName":dict_courier_details.get('fk_courier__vchr_name') or '',
                            }
                            json_eway_data=json.dumps(dict_eway_data)
                            int_request_id=datetime.strftime(datetime.now(),'%d%m%Y%H%M%S%f')+str(request.data.get('int_id'))
                            headers=		{
                                "Content-Type": "application/json",
                                "username":'Mygmobile_API_myg',
                                "password":"myGoal@98466699",
                                "gstin": '32AAAFZ4615J1Z8',
                                "Authorization":'bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJnc3AiXSwiZXhwIjoxNjAyNjU2ODcwLCJhdXRob3JpdGllcyI6WyJST0xFX1BST0RfRV9BUElfRVdCIl0sImp0aSI6ImMwYjc2ZTk3LTYzMzctNGQwZS04NzYwLWY2OTUxZDdlNjhiMSIsImNsaWVudF9pZCI6IjE1QkQ4MkY3QkJCNTRERDlBOTNBMTk5OTA1QjFBMTY0In0.lRgm0vkMS4lM46K4llLbGXB5TjqKBu97PcecOi-jaN8',
                                "requestid":int_request_id
                            }
                            headers['requestid']=int_request_id
                            if request.scheme+'://'+request.get_host() == 'http://pos.mygoal.biz:4001' or request.scheme+'://'+request.get_host() == 'http://pos.mygoal.biz:5555':
                                res1 = requests.post("https://gsp.adaequare.com/enriched/ewb/ewayapi?action=GENEWAYBILL",headers=headers,data=json_eway_data)
                                if res1.status_code == 401:
                                    headers_access={"gspappid" :"15BD82F7BBB54DD9A93A199905B1A164",
                                    "gspappsecret":"884F4D1FGCA97G4E17G824BG98F69CABDDC0"}
                                    res1 = requests.post("https://gsp.adaequare.com/gsp/authenticate?grant_type=token",headers=headers_access)
                                    headers['Authorization']='bearer '+json.loads(str(res1.content)[2:-1])['access_token']

                                    res1 = requests.post("https://gsp.adaequare.com/enriched/ewb/ewayapi?action=GENEWAYBILL",headers=headers,data=json_eway_data)
                            else:
                                res1 = requests.post("https://gsp.adaequare.com/test/enriched/ewb/ewayapi?action=GENEWAYBILL",headers=headers,data=json_eway_data)
                                if res1.status_code == 401:
                                    headers_access={"gspappid" :"15BD82F7BBB54DD9A93A199905B1A164",
                                    "gspappsecret":"884F4D1FGCA97G4E17G824BG98F69CABDDC0"}
                                    res1 = requests.post("https://gsp.adaequare.com/test/gsp/authenticate?grant_type=token",headers=headers_access)
                                    headers['Authorization']='bearer '+json.loads(str(res1.content)[2:-1])['access_token']

                                    res1 = requests.post("https://gsp.adaequare.com/test/enriched/ewb/ewayapi?action=GENEWAYBILL",headers=headers,data=json_eway_data)



                            StockTransfer.objects.filter(pk_bint_id = request.data.get('int_id')).update(vchr_eway_bill_no=json.loads(res1.content.decode('utf-8'))['result']['ewayBillNo'])

                        except  Exception as e:
                            StockTransfer.objects.filter(pk_bint_id = request.data.get('int_id'),vchr_eway_bill_no='EWAY BILL').update(vchr_eway_bill_no=None)
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)+' '+res1.content.decode('utf-8')})
                            return Response({"status":0,"reason":str(e)+' '+res1.content.decode('utf-8'),'bln_permitted':True})

                        return Response({"status":1,'bln_permitted':True})

        except  Exception as e:
                StockTransfer.objects.filter(pk_bint_id = request.data.get('int_id'),vchr_eway_bill_no='EWAY BILL').update(vchr_eway_bill_no=None)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                return Response({"status":0,"reason":str(e),'bln_permitted':True})
