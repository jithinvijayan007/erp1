from django.shortcuts import render
from django.views import generic
from rest_framework import generics
from rest_framework import authentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.http import JsonResponse
from rest_framework.response import Response
from django.views.generic import View,TemplateView,CreateView
from rest_framework.views import APIView
from states.models import States, Location, District
from customer.models import CustomerDetails
from item_category.models import Item
from django.db.models import Q
from receipt.models import Receipt
from django.db import transaction
# Create your views here.
from POS import ins_logger
import sys, os
from datetime import datetime
from django.db.models import Value, CharField, DateField
from django.db.models.functions import Cast
from purchase.models import Document

from userdetails.models import UserDetails as Userdetails
from receipt.models import ReceiptInvoiceMatching

from django.db.models import Q

from sap_api.mygoalAdvanceToSap import advance_to_sap

class AddReceipt(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            """add receipt"""
            dat_issue = request.data.get('datIssue')
            fk_customer_id = request.data.get('customerId')
            int_fop = request.data.get('intFop')
            dbl_amount = request.data.get('amount')
            vchr_remarks = request.data.get('remarks')
            int_pstatus=request.data.get('intPaymentStatus')
            int_receipt_type=request.data.get('intReceiptType')

            ins_document = Document.objects.select_for_update().get(vchr_module_name = 'RECEIPT',vchr_short_code = 'RV')
            str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
            ins_document.int_number = ins_document.int_number+1
            ins_document.save()
            # ins_receipt = Receipt.objects.create_recpt_num(str_inv_num)
            if request.data.get('fk_item'):
                ins_receipt = Receipt.objects.create(vchr_receipt_num=str_inv_num,dat_issue = dat_issue,fk_item_id=request.data.get("fk_item"),fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.now(),int_doc_status = 0,int_pstatus=int_pstatus,int_receipt_type=int_receipt_type)
            else:
                ins_receipt = Receipt.objects.create(vchr_receipt_num=str_inv_num,dat_issue = dat_issue,fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.now(),int_doc_status = 0,int_pstatus=int_pstatus,int_receipt_type=int_receipt_type)

            advance_to_sap(ins_receipt.pk_bint_id)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e)})

    def get(self,request):
        try:
            """list receipt"""
            # import pdb; pdb.set_trace()
            receipt_id = request.GET.get('receiptId')
            # import pdb;
            # pdb.set_trace()
            if receipt_id:
                ins_receipt = list(Receipt.objects.filter(pk_bint_id = int(receipt_id)).values('pk_bint_id','dat_issue','fk_customer_id','fk_customer_id__vchr_name','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','fk_item_id','fk_item__vchr_name','vchr_receipt_num').annotate(vchr_fop = Value('', output_field=CharField())).filter(int_doc_status = 0))
            else:
                ins_receipt = list(Receipt.objects.filter(~Q(int_doc_status=-1)).values('pk_bint_id','fk_customer_id','fk_customer_id__vchr_name','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','vchr_receipt_num').annotate(vchr_fop = Value('', output_field=CharField()),dat_issue = Cast('dat_issue', DateField())).filter(int_doc_status = 0).order_by('-pk_bint_id'))
            bln_ho=False
            if request.user.userdetails.fk_branch.int_type==2:
                bln_ho=True
            for ins_data in ins_receipt:
                if ins_data['int_fop'] == 1:
                    ins_data['vchr_fop'] = "CASH"
                    ins_data['vchr_payment_status'] = "RECEIVED"
                elif ins_data['int_fop'] == 2:
                    ins_data['vchr_fop'] = "DEBIT CARD"
                elif ins_data['int_fop'] == 3:
                    ins_data['vchr_fop'] = "CREDIT CARD"
                elif ins_data['int_fop'] == 4:
                    ins_data['vchr_fop'] = "CHEQUE"
                elif ins_data['int_fop'] == 5:
                    ins_data['vchr_fop'] = "RTGS"
                elif ins_data['int_fop'] == 6:
                    ins_data['vchr_fop'] = "NEFT"
                if ins_data['int_receipt_type'] == 1:
                    ins_data['vchr_receipt_type'] = "ADVANCE"
                if ins_data['int_receipt_type'] == 2:
                    ins_data['vchr_receipt_type'] = "PRE-BOOKING"
                if ins_data['int_receipt_type'] == 3:
                    ins_data['vchr_receipt_type'] = "OTHERS"
                if ins_data['int_pstatus'] == 0:
                    ins_data['vchr_payment_status'] = "RECEIVED"
                if ins_data['int_pstatus'] == 1:
                    ins_data['vchr_payment_status'] = "PENDING"
                ins_data['bln_ho'] = bln_ho
                if ins_data['dat_issue']:
                    ins_data['dat_issue_edit']=ins_data['dat_issue']
                    ins_data['dat_issue']=ins_data['dat_issue'].strftime('%d-%m-%y')



            return Response({'status':1 , 'data' : ins_receipt})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e) })

    def put(self,request):
        try:
            """update receipt"""
            # import pdb; pdb.set_trace()
            dat_issue = request.data.get('datIssue')
            fk_customer_id = request.data.get('customerId')
            int_fop = request.data.get('intFop')
            dbl_amount = request.data.get('amount')
            vchr_remarks = request.data.get('remarks')
            receipt_id = request.data.get('receiptId')
            int_pstatus=request.data.get('intPaymentStatus')
            vchr_receipt_num = request.data.get('vchrReceiptNum')

            int_receipt_type=request.data.get('intReceiptType')

            if receipt_id:
                ins_receipt = Receipt.objects.filter(pk_bint_id = receipt_id).update(fk_updated_id = request.user.id,dat_updated = datetime.now(),int_doc_status =-1)

                if request.data.get('fk_item'):
                        ins_receipt = Receipt.objects.create(int_pstatus=int_pstatus,fk_item_id=request.data.get('fk_item'),dat_issue = dat_issue,int_receipt_type=int_receipt_type,fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.now(),int_doc_status = 0,vchr_receipt_num = vchr_receipt_num)
                else:
                    ins_receipt = Receipt.objects.create(int_pstatus=int_pstatus,dat_issue = dat_issue,int_receipt_type=int_receipt_type,fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.now(),int_doc_status = 0,vchr_receipt_num = vchr_receipt_num)
            else:
                return Response({'status':0 , 'data' : "No Receipt Id"})

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def patch(self,request):
        try:
            """delete receipt"""
            # import pdb; pdb.set_trace()
            receipt_id = request.data.get('receiptId')

            if receipt_id:
                ins_receipt = Receipt.objects.filter(pk_bint_id = receipt_id).update(int_doc_status = -1)
            else:
                return Response({'status':0 , 'data' : "No Receipt Id"})

            return Response({'status':1 , 'data' : ins_receipt})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e)})

class ApproveReceipt(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        # import pdb;
        # pdb.set_trace()
        if request.user.userdetails.fk_branch.int_type==2:
                    str_bank=request.data.get('strBank')
                    str_transaction_id=request.data.get('strTransactionId')
                    int_pstatus=request.data.get('intPaymentStatus')
                    ins_receipt = Receipt.objects.filter(pk_bint_id = request.data.get('intreceiptId')).update(fk_updated_id = request.user.id,dat_updated = datetime.now(),dat_approval=request.data.get('dateTransaction'),int_pstatus=int_pstatus,vchr_bank=str_bank,vchr_transaction_id=str_transaction_id)


        return Response({'status':1})

class ListReceipt(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        # import pdb;
        # pdb.set_trace()
        int_customer_mobile = request.data.get("intCustomerMob")
        # lst_receipt=Receipt.objects.filter(fk_customer__int_mobile=int_customer_mobile,int_pstatus=0,int_doc_status.not_=-1)).values('dbl_amount','pk_bint_id','vchr_receipt_num').exclude(int_doc_status = -1)
        lst_receipt=Receipt.objects.filter( ~Q(int_doc_status=-1),fk_customer__int_mobile=int_customer_mobile,int_pstatus=0).values('dbl_amount','pk_bint_id','vchr_receipt_num')

        blnService=request.data.get("blnService") or False

        if blnService:
            lst_receipt.filter(int_receipt_type=4)
        else:
            lst_receipt.exclude(int_receipt_type=4)
        lst_receipt_id=lst_receipt.values_list('pk_bint_id',flat=True)
        receipt_tot=0
        lst_receipt_exists=[]
        if lst_receipt:
            for i in lst_receipt:
                i['amount']=i['dbl_amount']
                receipt_tot=receipt_tot+i['amount']


            lst_matching=list(ReceiptInvoiceMatching.objects.filter(fk_receipt_id__in=lst_receipt_id).values('dbl_amount','fk_receipt_id','fk_receipt__dbl_amount','fk_receipt__vchr_receipt_num'))
            # import pdb;
            # pdb.set_trace()
            if lst_matching:
                receipt_tot=0
                add={}
                for rm in lst_matching:

                    rm['pk_bint_id']=rm['fk_receipt_id']
                    rm['vchr_receipt_num']=rm['fk_receipt__vchr_receipt_num']
                    del rm['fk_receipt__vchr_receipt_num']
                    # rm['amount']= rm['fk_receipt__dbl_amount']-rm['dbl_amount']
                    lst_receipt_exists.append(rm['pk_bint_id'])
                #     if add[rm['pk_bint_id']]:
                #         add[rm['pk_bint_id']]=add[rm['pk_bint_id']]+rm['amount']
                    if rm['pk_bint_id'] in add:
                        add[rm['pk_bint_id']]=add[rm['pk_bint_id']]+rm['dbl_amount']
                    else:
                        add[rm['pk_bint_id']]=rm['dbl_amount']


                i=0
                flag=False
                lst_dict_keys=[]
                for rm in lst_matching:
                        if rm['dbl_amount']!=add[rm['pk_bint_id']]:
                            rm['dbl_amount']=add[rm['pk_bint_id']]
                        if rm in lst_dict_keys:
                            lst_matching[i]=None
                        lst_dict_keys.append(rm['pk_bint_id'])
                        i=i+1
                i=0

                for rm in lst_matching:
                    rm['amount']= rm['fk_receipt__dbl_amount']-rm['dbl_amount']
                    receipt_tot=receipt_tot+rm['amount']
                    if rm['amount']==0:
                        lst_matching[i]=None
                    i=i+1

                lst_matching = list(filter(None, lst_matching))
                for i in lst_receipt:
                    if i['pk_bint_id'] not in lst_receipt_exists:
                        lst_matching.append(i)
                        receipt_tot=receipt_tot+i['amount']
                lst_matching =list({x['pk_bint_id']:x for x in lst_matching}.values())
                if lst_matching:

                        return Response({'status':1,'lst_receipt':list(lst_matching),'bln_receipt':True,'receipt_tot':receipt_tot,'bln_matching':True})
                else:
                        return Response({'status':1,'bln_receipt':False})

            else:
                return Response({'status':1,'lst_receipt':list(lst_receipt),'bln_receipt':True,'receipt_tot':receipt_tot,'bln_matching':False})
        else:
            return Response({'status':1,'bln_receipt':False})


class AddReceiptAPI(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            with transaction.atomic():
                dct_cust_details = request.data.get('insCustomerDetails')
                int_fop = request.data.get('intFop')
                dbl_amount = request.data.get('dblAdvAmount')
                vchr_remarks = request.data.get('strRemarks')
                ins_user = Userdetails.objects.filter(username=request.data.get('strUserCode')).values('user_ptr_id').first()
                int_user_id = None
                if ins_user:
                    int_user_id = ins_user['user_ptr_id']

                ins_customer = CustomerDetails.objects.filter(vchr_name__contains = dct_cust_details['strCustName'],int_mobile = dct_cust_details['strMobNum']).values('pk_bint_id').first()
                if not ins_customer:
                    ins_state = States.objects.filter(vchr_code = dct_cust_details['strStateCode']).first()
                    ins_location = Location.objects.filter(vchr_name__contains = dct_cust_details['strLocation'], vchr_pin_code = dct_cust_details['intPinCode']).first()
                    ins_customer = CustomerDetails.objects.create(
                                                                    vchr_name = dct_cust_details['strCustName'],
                                                                    vchr_email = dct_cust_details['strEmail'],
                                                                    int_mobile = dct_cust_details['strMobNum'],
                                                                    fk_location = ins_location,
                                                                    fk_state = ins_state
                                                                 )
    # ================================================================================================================
                    ins_sales_customer = CustomerDetails.objects.create(
                                                            fk_customer_id = ins_customer.pk_bint_id,
                                                            dat_created = datetime.now(),
                                                            fk_created_id = int_user_id,
                                                            vchr_name = dct_cust_details['strCustName'],
                                                            vchr_email = dct_cust_details['strEmail'],
                                                            int_mobile = dct_cust_details['strMobNum'],
                                                            fk_location = ins_location,
                                                            fk_state = ins_state
                                                         )
                    # int_sales_customer_id = ins_sales_customer.pk_bint_id
    # ================================================================================================================
                    int_customer_id = ins_customer.pk_bint_id


                else:
                    int_customer_id = ins_customer['pk_bint_id']

                ins_document = Document.objects.select_for_update().get(vchr_module_name = 'RECEIPT',
                vchr_short_code = 'RV')
                str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                ins_document.int_number = ins_document.int_number+1
                ins_document.save()
                ins_item = Item.objects.filter(vchr_item_code=request.data.get('strItemCode')).first()
                if ins_item:
                    # ins_receipt = Receipt.objects.create_recpt_num(str_inv_num)
                    Receipt.objects.create(vchr_receipt_num=str_inv_num,dat_issue = datetime.now(),fk_item = ins_item, fk_customer_id = int_customer_id, int_fop = int_fop, dbl_amount = dbl_amount, vchr_remarks = vchr_remarks, fk_created_id = int_user_id, dat_created = datetime.now(), int_doc_status = 0, int_pstatus = 0, int_receipt_type = 4, vchr_receipt_num = str_inv_num)
                else:
                    return Response({'status':0 , 'message' : 'Item Not Found'})

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e)})
