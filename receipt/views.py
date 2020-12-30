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
from item_category.models import Item
from django.db.models import Q
from receipt.models import Receipt,PartialReceipt
from django.db import transaction
from customer.models import CustomerDetails,SalesCustomerDetails

from accounts_map.models import AccountsMap
# Create your views here.
from POS import ins_logger
import json
import sys, os
from datetime import datetime
from django.db.models import Value, CharField, DateField
from django.db.models.functions import Cast
from purchase.models import Document
from purchase.views import doc_num_generator
from invoice.models import Bank
from branch.models import Branch
from terms.models import Terms,Type

from userdetails.models import Userdetails
from receipt.models import ReceiptInvoiceMatching
from django.db.models import CharField, Case, Value, When,Sum,F,IntegerField,Count
from tool_settings.models import Tools
# from sap_api.mygoalAdvanceToSap import advance_to_sap

from POS import settings
from invoice.models import PartialInvoice
from company.models import FinancialYear
from transaction.models import Transaction
from transaction.views import create_posting_data
from django.core.files.storage import FileSystemStorage
import pdfkit
import base64
import requests
from invoice.models import SalesMaster,PaymentDetails

import num2words
from generate_file_name import name_change
import pandas as pd

# LG
class ReceiptOrderList(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        """Data to Receipt List"""
        try:
            dat_to = request.data.get("datTo")[:10]
            dat_from = request.data.get("datFrom")[:10]

            # import pdb; pdb.set_trace()
            ins_partial_receipt = PartialReceipt.objects.filter(int_status = 0, dat_created__date__gte = dat_from,dat_created__date__lte = dat_to,vchr_branchcode=request.user.userdetails.fk_branch.vchr_code).order_by('-dat_created')
            dct_branch = dict(Branch.objects.values_list('vchr_code','vchr_name'))
            lst_data = []
            for data in ins_partial_receipt.values():

                json_data = data['json_data']
                dct_user=Userdetails.objects.filter(username=json_data['staffcode']).values('first_name','last_name').first()
                dct_data = {}
                dct_data['strEnqNo'] = json_data['vchrenquirynum']
                dct_data['strItem'] = json_data['strItemnName']
                dct_data['strCustomer'] = json_data['strCustName']
                dct_data['intId'] = data['pk_bint_id']
                dct_data['strStaff'] =dct_user.get('first_name','')+' '+dct_user.get('last_name','')
                dct_data['datBooked'] = datetime.strftime(data['dat_created'],'%d-%m-%Y')
                dct_data['branch'] = dct_branch[data['vchr_branchcode']]
                dct_data['bln_view'] = True
                lst_data.append(dct_data)
            if lst_data:
                return Response({'status':1,'data':lst_data})
            return Response({'status':1,'data':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':str(e)})

    def put(self,request):
        pass

    def get(self,request):
        """Date to Add Receipt"""
        try:
            # import pdb; pdb.set_trace()
            receipt_id = request.GET.get('receiptId')

            data = {}
            ins_partial_receipt = PartialReceipt.objects.get(pk_bint_id = receipt_id)
            json_data = ins_partial_receipt.json_data

            data['dbl_amount'] = json_data.get('dblAdvAmount')
            data['vchr_remarks'] = json_data.get('strRemarks')
            data['fk_customer_id__vchr_name'] = json_data.get('strCustName')
            data['int_pstatus'] = ins_partial_receipt.int_status
            data['fk_item__vchr_name'] = json_data.get('strItemnName')
            data['dat_issue_edit'] = datetime.today()
            data['fk_customer_id__vchr_name'] = ''
            data['fk_customer_id'] = ''
            data['fk_item_id'] = ''
            data['fk_item_id__fk_product_id__vchr_name'] = ''
            data['fk_item_id__fk_product_id'] = ''
            data['int_document_id'] = json_data.get("intPartialInvoiceId")
            data['bln_service'] = ins_partial_receipt.bln_service or False


            ins_customer = CustomerDetails.objects.filter(int_mobile = json_data['strMobNum']).values('pk_bint_id','vchr_name').first()
            if ins_customer:
                data['fk_customer_id__vchr_name'] = ins_customer['vchr_name']
                data['fk_customer_id'] = ins_customer['pk_bint_id']
            ins_item = Item.objects.filter(vchr_item_code = ins_partial_receipt.vchr_item_code).values('pk_bint_id','fk_product_id__vchr_name','fk_product_id').first()
            if ins_item:
                data['fk_item_id'] = ins_item['pk_bint_id']
                data['fk_item_id__fk_product_id__vchr_name'] = ins_item['fk_product_id__vchr_name']
                data['fk_item_id__fk_product_id'] = ins_item['fk_product_id']
            return Response({'status':1 , 'data' : [data]})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e) })


# def create_posting_data(pk_bint_id):

#     str_account_type = ''
#     int_account_id = 0
#     lst_data = []
#     ins_receipt = Receipt.objects.filter(pk_bint_id = pk_bint_id).values('fk_customer_id','dbl_amount','fk_branch_id','int_fop').order_by('-pk_bint_id').first()

#     if ins_receipt['int_fop'] in [1]: # 1 cash
#         ins_branch_data = AccountsMap.objects.filter(fk_branch_id = ins_receipt['fk_branch_id'],vchr_category = 'CASH A/C',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
#     elif ins_receipt['int_fop'] in [2,3,4,5,6]: # 2 debit card , 3 credit card, 4 Cheque, 5 RTGS, 6 NEFT
#         ins_branch_data = AccountsMap.objects.filter(vchr_category = 'TRANSFER',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
#     elif ins_receipt['int_fop'] in [7]: # 7 Paytm
#         ins_branch_data = AccountsMap.objects.filter(vchr_category = 'PAYTM',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
#     elif ins_receipt['int_fop'] in [8]: # 8 Paytm Mall
#         ins_branch_data = AccountsMap.objects.filter(vchr_category = 'PAYTM MALL',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
#     elif ins_receipt['int_fop'] in [9]: # 9 Bharath Qr
#         ins_branch_data = AccountsMap.objects.filter(vchr_category = 'BHARATH QR',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()

#     if ins_branch_data:
#         dct_data = {}
#         dct_data['ACCOUNT_ID'] = ins_receipt['fk_customer_id']
#         dct_data['ACCOUNT_TYPE']  = CustomerDetails.objects.filter(pk_bint_id=ins_receipt['fk_customer_id']).values("int_cust_type").first()['int_cust_type']
#         dct_data['DEBIT']  = 0
#         dct_data['CREDIT']  = ins_receipt['dbl_amount']
#         lst_data.append(dct_data)
#         dct_data = {}
#         dct_data['ACCOUNT_ID'] = ins_branch_data['fk_coa_id__pk_bint_id']
#         dct_data['ACCOUNT_TYPE']  = ins_branch_data['int_type']
#         dct_data['DEBIT']  = ins_receipt['dbl_amount']
#         dct_data['CREDIT']  = 0
#         lst_data.append(dct_data)
#     else:
#         return 1
#     return(lst_data)




class AddReceipt(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            with transaction.atomic():
                # print("47")
                """add receipt"""
                dat_issue = request.data.get('datIssue')
                fk_customer_id = request.data.get('customerId')
                int_fop = request.data.get('intFop')
                dbl_amount = request.data.get('amount')
                vchr_remarks = request.data.get('remarks')
                int_pstatus=request.data.get('intPaymentStatus')
                int_receipt_type=request.data.get('intReceiptType')
                int_card_no=request.data.get('vchrCardNUmber')
                int_bank_id=request.data.get('intBankId')
                bln_service = request.data.get('blnService')

                # if dbl_amount > 200000:
                #     return Response({'status':0 , 'data' : 'Amount should be less than 200000'})

                # LG
                """If Partial Receipt id is present Updating the status to 1"""
                if request.data.get('receiptId'):
                    PartialReceipt.objects.filter(pk_bint_id = request.data.get('receiptId')).update(int_status = 1)

                IntCustomerType=CustomerDetails.objects.filter(pk_bint_id=fk_customer_id).values("int_cust_type").first()['int_cust_type'] #1:credit customer 2:corporate customers

                # import pdb; pdb.set_trace()

                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).first()
                # if not ins_document:

                #     ins_document = Document.objects.create(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code,int_number = 1)
                #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     ins_document.int_number = ins_document.int_number+1
                #     ins_document.save()
                # else:
                #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     Document.objects.filter(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).update(int_number = ins_document.int_number+1)

                # LG 27-06-2020
                str_inv_num = doc_num_generator('RECEIPT',request.user.userdetails.fk_branch.pk_bint_id)
                if not str_inv_num:
                    return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                # ins_document = Document.objects.get(vchr_module_name = 'RECEIPT',vchr_short_code = 'RV')
                # str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                # ins_document.int_number = ins_document.int_number+1
                # ins_document.save()

                # ins_receipt = Receipt.objects.create_recpt_num(str_inv_num)
                if request.data.get('fk_item'):
                    ins_receipt = Receipt.objects.create(vchr_receipt_num=str_inv_num,vchr_card_num=int_card_no,vchr_transaction_id=request.data.get('vchrReferenceNumber'),dat_issue = dat_issue,fk_item_id=request.data.get("fk_item"),fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.today(),int_doc_status = 0,int_pstatus=int_pstatus,int_receipt_type=int_receipt_type,fk_branch = request.user.userdetails.fk_branch)
                else:
                    if bln_service:
                        ins_receipt = Receipt(vchr_receipt_num=str_inv_num,
                                            int_document_id = request.data.get('partialId'),
                                            fk_branch_id = request.user.userdetails.fk_branch_id,
                                            dat_issue = dat_issue,
                                            fk_customer_id = fk_customer_id,
                                            int_fop = int_fop,
                                            dbl_amount = dbl_amount,
                                            vchr_remarks = vchr_remarks,
                                            fk_created_id = request.user.id,
                                            dat_created = datetime.now(),
                                            int_doc_status = 0,
                                            int_pstatus = 0,
                                            int_receipt_type = 4,
                                            vchr_card_num=int_card_no,
                                            vchr_transaction_id=request.data.get('vchrReferenceNumber'),
                                            fk_bank_id = request.data.get('intBankId'))

                        ins_receipt.save()
                        if create_posting_data(request,ins_receipt.pk_bint_id):

                            ins_partial_receipt = PartialReceipt.objects.filter(pk_bint_id = request.data.get('receiptId')).values('json_data').first()
                            flt_adv_amount = ins_partial_receipt['json_data']['dblAdvAmount']
                            str_job_num = ins_partial_receipt['json_data']['vchrenquirynum']
                            url =settings.BI_HOSTNAME +'/service/new_advance/'

                            dct_param_data = {'str_job_num':str_job_num,'flt_adv_amount' :flt_adv_amount}

                            res_data = requests.post(url,json=dct_param_data)
                            if res_data.json()['status']=='failed':
                                return JsonResponse({'status': 'Failed','data':res_data.json()['message']})
                            pass
                        else:
                            raise ValueError('Something happened in POS Receipt')


                    else:

                        ins_receipt = Receipt.objects.create(vchr_receipt_num=str_inv_num,vchr_card_num=int_card_no,vchr_transaction_id=request.data.get('vchrReferenceNumber'),dat_issue = dat_issue,fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.today(),int_doc_status = 0,int_pstatus=int_pstatus,int_receipt_type=int_receipt_type,fk_branch = request.user.userdetails.fk_branch,fk_bank_id = int_bank_id)
                # import pdb; pdb.set_trace()
                if int_fop in [1,2,3,7,8,9] and IntCustomerType in [1,2]:
                    # print("85")
                    CustomerDetails.objects.filter(pk_bint_id=fk_customer_id).update(dbl_credit_balance=F('dbl_credit_balance')+dbl_amount)
                # elif IntCustomerType!=1:
                #     return Response({'status':0,'data':"User is not a credit customer"})
                # advance_to_sap(ins_receipt.pk_bintjson_data['lst_items'][0]_id)
                if int_fop not in [4,5,6]:
                    if create_posting_data(request,ins_receipt.pk_bint_id):
                        return Response({'status':1})
                    else:
                        return Response({'status':0 , 'data' : 'Posting Failed'})
                return Response({'status':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e)})

    def get(self,request):
        try:
            # print("99")

            receipt_id = request.GET.get('receiptId')

            bln_ho=False
            if receipt_id:
                if request.user.userdetails.fk_branch.int_type==2:
                    bln_ho=True
                ins_receipt = list(Receipt.objects.filter(pk_bint_id = int(receipt_id)).values('vchr_card_num','pk_bint_id','dat_issue','fk_customer_id','fk_customer_id__vchr_name','int_fop','dbl_amount','fk_customer_id__int_mobile','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','fk_item_id','fk_item__vchr_name','vchr_receipt_num','fk_item_id__fk_product_id','fk_item_id__fk_product_id__vchr_name','dat_approval','fk_bank__vchr_name','vchr_transaction_id','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField())))
            else:
                if request.user.userdetails.fk_branch.int_type==2:
                    bln_ho=True
                    ins_receipt = list(Receipt.objects.exclude(int_doc_status=-1).values('vchr_card_num','pk_bint_id','fk_customer_id','fk_customer_id__vchr_name','fk_customer_id__int_mobile','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','vchr_receipt_num','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField()),dat_issue = Cast('dat_issue', DateField())).filter(int_doc_status = 0).order_by('-pk_bint_id'))
                else:
                    ins_receipt = list(Receipt.objects.filter(fk_branch_id = request.user.userdetails.fk_branch_id).exclude(int_doc_status=-1).values('vchr_card_num','pk_bint_id','fk_customer_id','fk_customer_id__vchr_name','fk_customer_id__int_mobile','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','vchr_receipt_num','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField()),dat_issue = Cast('dat_issue', DateField())).filter(int_doc_status = 0).order_by('-pk_bint_id'))


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
                elif ins_data['int_fop'] == 7:
                    ins_data['vchr_fop'] = "Paytm"
                elif ins_data['int_fop'] == 8:
                    ins_data['vchr_fop'] = "Paytm Mall"
                elif ins_data['int_fop'] == 9:
                    ins_data['vchr_fop'] = "Bharath QR"

                if ins_data['int_receipt_type'] == 1:
                    ins_data['vchr_receipt_type'] = "ADVANCE"
                elif ins_data['int_receipt_type'] == 2:
                    ins_data['vchr_receipt_type'] = "PRE-BOOKING"
                elif ins_data['int_receipt_type'] == 3:
                    ins_data['vchr_receipt_type'] = "OTHERS"
                elif ins_data['int_receipt_type'] == 4:
                    ins_data['vchr_receipt_type'] = "SERVICE"
                elif ins_data['int_receipt_type'] == 5:
                    ins_data['vchr_receipt_type'] = "FINANCIER"

                if ins_data['int_pstatus'] == 0:
                    ins_data['vchr_payment_status'] = "RECEIVED"
                if ins_data['int_pstatus'] == 1:
                    ins_data['vchr_payment_status'] = "PENDING"
                ins_data['bln_ho'] = bln_ho
                if ins_data['dat_issue']:
                    ins_data['dat_issue_edit']=ins_data['dat_issue']
                    ins_data['dat_issue']=ins_data['dat_issue'].strftime('%d-%m-%Y')




            return Response({'status':1 , 'data' : ins_receipt})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e) })



    def put(self,request):
        try:
            with transaction.atomic():
                # print("168")
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
                # if dbl_amount > 200000:
                #     return Response({'status':0 , 'data' : 'Amount should be less than 200000'})


                int_receipt_type=request.data.get('intReceiptType')

                if receipt_id:
                    ins_receipt = Receipt.objects.filter(pk_bint_id = receipt_id).update(fk_updated_id = request.user.id,dat_updated = datetime.now(),int_doc_status =-1)

                    if request.data.get('fk_item'):
                        ins_receipt = Receipt.objects.create(vchr_transaction_id=request.data.get('vchrReferenceNumber'),int_pstatus=int_pstatus,fk_item_id=request.data.get('fk_item'),dat_issue = dat_issue,int_receipt_type=int_receipt_type,fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.now(),int_doc_status = 0,vchr_receipt_num = vchr_receipt_num,fk_branch=request.user.userdetails.fk_branch)
                    else:
                        int_sales_master_id = Receipt.objects.get(pk_bint_id = receipt_id).fk_sales_master_id
                        ins_receipt = Receipt.objects.create(vchr_transaction_id=request.data.get('vchrReferenceNumber'),int_pstatus=int_pstatus,dat_issue = dat_issue,int_receipt_type=int_receipt_type,fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.now(),int_doc_status = 0,vchr_receipt_num = vchr_receipt_num,fk_branch = request.user.userdetails.fk_branch,fk_sales_master_id=int_sales_master_id)
                else:
                    return Response({'status':0 , 'data' : "No Receipt Id"})

                # import pdb; pdb.set_trace()
                IntCustomerType=CustomerDetails.objects.filter(pk_bint_id=fk_customer_id).values("int_cust_type").first()['int_cust_type']
                if int_fop in [1,2,3,7,8,9] and IntCustomerType in [1,2]:
                #     # print("85")
                    CustomerDetails.objects.filter(pk_bint_id=fk_customer_id).update(dbl_credit_balance=F('dbl_credit_balance')+dbl_amount)
                    if int_sales_master_id and int_receipt_type==7:
                        ReceiptInvoiceMatching.objects.create(fk_receipt_id=ins_receipt.pk_bint_id,dbl_amount=dbl_amount,dat_created=datetime.now(),fk_sales_master_id=int_sales_master_id)
                        PaymentDetails.objects.create(fk_sales_master_id=int_sales_master_id,int_fop=4,vchr_reff_number=vchr_receipt_num,dbl_receved_amt=dbl_amount,dat_created_at=datetime.now())
                        dct_bi_data = {'fop':4,'amount':dbl_amount,'enq_id':PartialInvoice.objects.get(fk_invoice_id = int_sales_master_id).int_enq_master_id}
                        url = settings.BI_HOSTNAME+'/mobile/addpayment/'
                        res_data = requests.post(url,json=dct_bi_data)
                        if res_data.json().get('status')=='success':
                            SalesMaster.objects.filter(pk_bint_id=int_sales_master_id).update(dbl_cust_outstanding=F('dbl_cust_outstanding')-dbl_amount)
                            # pass
                        else:
                            raise ValueError('Something happened in BI')

                    if create_posting_data(request,ins_receipt.pk_bint_id):
                        return Response({'status':1})
                    else:
                        return Response({'status':0 , 'data' : 'Posting Failed'})

                return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def patch(self,request):
        try:
            # print("200")
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
        with transaction.atomic():
            dbl_amount = Receipt.objects.filter(pk_bint_id = request.data.get('intreceiptId')).values("dbl_amount").first()["dbl_amount"]
            fk_customer_id = Receipt.objects.filter(pk_bint_id = request.data.get('intreceiptId')).values("fk_customer").first()["fk_customer"]

            IntCustomerType=CustomerDetails.objects.filter(pk_bint_id=fk_customer_id).values("int_cust_type").first()['int_cust_type'] #1:credit customer 2:corporate customers

            if request.user.userdetails.fk_branch.int_type==2:
                        str_bank=request.data.get('strBank')
                        int_bank=request.data.get('intBankId')
                        str_transaction_id=request.data.get('strTransactionId')
                        int_pstatus=request.data.get('intPaymentStatus')
                        ins_receipt = Receipt.objects.filter(pk_bint_id = request.data.get('intreceiptId')).update(fk_updated_id = request.user.id,dat_updated = datetime.now(),dat_approval=request.data.get('dateTransaction'),int_pstatus=int_pstatus,vchr_bank=str_bank,fk_bank_id=int_bank,vchr_transaction_id=str_transaction_id)
                        if IntCustomerType in [1,2]:
                            CustomerDetails.objects.filter(pk_bint_id=fk_customer_id).update(dbl_credit_balance=F('dbl_credit_balance')+dbl_amount)
                        ins_receipt_credit = Receipt.objects.get(pk_bint_id = request.data.get('intreceiptId'))
                        int_origin_branch_id=ins_receipt_credit.fk_branch_id
                        if ins_receipt_credit.fk_sales_master_id:
                            ReceiptInvoiceMatching.objects.create(fk_receipt_id=ins_receipt_credit.pk_bint_id,dbl_amount=ins_receipt_credit.dbl_amount,dat_created=datetime.now(),fk_sales_master_id=ins_receipt_credit.fk_sales_master_id)
                            PaymentDetails.objects.create(fk_sales_master_id=ins_receipt_credit.fk_sales_master_id,int_fop=4,vchr_reff_number=ins_receipt_credit.vchr_receipt_num,dbl_receved_amt=ins_receipt_credit.dbl_amount,dat_created_at=datetime.now())
                            dct_bi_data = {'fop':4,'amount':ins_receipt_credit.dbl_amount,'enq_id':PartialInvoice.objects.get(fk_invoice_id = ins_receipt_credit.fk_sales_master_id).int_enq_master_id}
                            url = settings.BI_HOSTNAME+'/mobile/addpayment/'
                            res_data = requests.post(url,json=dct_bi_data)
                            if res_data.json().get('status')=='success':
                                SalesMaster.objects.filter(pk_bint_id=ins_receipt_credit.fk_sales_master_id).update(dbl_cust_outstanding=F('dbl_cust_outstanding')-ins_receipt_credit.dbl_amount)
                                # pass
                            else:
                                raise ValueError('Something happened in BI')
                        if create_posting_data(request,request.data.get('intreceiptId'),int_origin_branch_id=int_origin_branch_id):
                            return Response({'status':1})
                        else:
                            return Response({'status':0 , 'data' : 'Posting Failed'})
            return Response({'status':1})

class ListReceipt(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        int_customer_mobile = request.data.get("intCustomerMob")
        int_cust_type = request.data.get("intCustType")

        # lst_receipt=Receipt.objects.filter(fk_customer__int_mobile=int_customer_mobile,int_pstatus=0,int_doc_status.not_=-1)).values('dbl_amount','pk_bint_id','vchr_receipt_num').exclude(int_doc_status = -1)
        # lst_receipt=Receipt.objects.filter( ~Q(int_doc_status=-1),fk_customer__int_mobile=int_customer_mobile,int_pstatus=0,fk_branch_id = request.user.userdetails.fk_branch_id).values('dbl_amount','pk_bint_id','vchr_receipt_num').exclude(int_receipt_type=4) # okd code
        lst_receipt=Receipt.objects.filter( ~Q(int_doc_status=-1),fk_customer__int_mobile=int_customer_mobile,int_pstatus=0,fk_branch_id = request.user.userdetails.fk_branch_id,fk_customer__int_cust_type = int_cust_type).exclude(int_receipt_type=7).values('dbl_amount','pk_bint_id','vchr_receipt_num') # new code with no exclude command
        blnService=request.data.get("blnService") or False
        if blnService:
            lst_receipt=lst_receipt.filter(int_receipt_type=4,int_document_id = request.data.get('partial_id'))
        else:
            lst_receipt=lst_receipt.exclude(int_receipt_type=4)
        lst_receipt_id=lst_receipt.values_list('pk_bint_id',flat=True)
        receipt_tot=0
        lst_receipt_exists=[]
        if lst_receipt:
            for i in lst_receipt:
                i['amount_entered'] = 0
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
                    if rm['amount']==0:
                        lst_matching[i]=None
                    i=i+1

                lst_matching = list(filter(None, lst_matching))
                for i in lst_receipt:
                    if i['pk_bint_id'] not in lst_receipt_exists:
                        lst_matching.append(i)
                        lst_receipt_exists.append(i['pk_bint_id'])
                lst_matching =list({x['pk_bint_id']:x for x in lst_matching}.values())
                for i in lst_matching:
                    receipt_tot +=i['amount']
                    i['amount_entered'] = 0
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
                if request.data.get('blnPrint'):
                        url = settings.BI_HOSTNAME +'/service/print_service/'
                        try:
                            res_data = requests.post(url,json={"item_service_id":request.data.get('int_service_id'),"bln_pos":True})
                            if res_data.json()['status']=='failed':
                                return JsonResponse({'status': 'Failed','data':res_data.json()['message']})
                        except Exception as e:
                            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})

                        pdf_path = settings.BI_HOSTNAME+'/'+'media'+'/'
                        # pdf_name ='Jobslip.pdf'
                        # filename = pdf_path+pdf_name
                        # pdfkit.from_string(res_data.json()['file'],filename)
                        # fs = FileSystemStorage()
                        # lst_encoded_string=[]
                        # if fs.exists(filename):
                        #     with fs.open(filename) as pdf:
                        #         lst_encoded_string.append(str(base64.b64encode(pdf.read())))
                        # file_details = {}
                        # file_details['file'] = lst_encoded_string
                        # file_details['file_name'] = pdf_name
                        file_details = res_data.json()['file']

                        file_url = settings.BI_HOSTNAME+'/media/'+file_details['file_name']
                        # return Response({"status":1,"file":file_details,'file_url':file_url})
                        return Response({"status":1,"file":file_details,'file_url':file_url})
                int_fop = request.data.get('intFop') or 1
                dbl_amount = request.data.get('dblAdvAmount',) or request.data.get('service_advance')
                vchr_remarks = request.data.get('strRemarks')
                ins_user = Userdetails.objects.filter(username=request.data.get('strUserCode')).values('user_ptr_id').first()
                int_user_id = None
                if ins_user:
                    int_user_id = ins_user['user_ptr_id']

                ins_customer = CustomerDetails.objects.filter(vchr_name__contains = dct_cust_details['strCustName'],int_mobile = dct_cust_details['strMobNum'],int_cust_type = dct_cust_details['intcustomertype']).values('pk_bint_id').first()

                # import pdb; pdb.set_trace()
                if not ins_customer:
                    ins_state = States.objects.filter(vchr_code = dct_cust_details['strStateCode']).first()
                    ins_location = Location.objects.filter(vchr_name__contains = dct_cust_details['strLocation'], vchr_pin_code = dct_cust_details['intPinCode']).first()
                    ins_customer = CustomerDetails.objects.create(
                                                                    vchr_name = dct_cust_details['strCustName'],
                                                                    vchr_email = dct_cust_details['strEmail'],
                                                                    int_mobile = dct_cust_details['strMobNum'],
                                                                    int_cust_type = dct_cust_details['intcustomertype'],
                                                                    txt_address = dct_cust_details['vchr_customer_addres'],
                                                                    fk_location = ins_location,
                                                                    fk_state = ins_state
                                                                 )
    # ================================================================================================================
                    ins_sales_customer = SalesCustomerDetails.objects.create(
                                                            fk_customer_id = ins_customer.pk_bint_id,
                                                            dat_created = datetime.now(),
                                                            fk_created_id = int_user_id,
                                                            vchr_name = dct_cust_details['strCustName'],
                                                            vchr_email = dct_cust_details['strEmail'],
                                                            int_mobile = dct_cust_details['strMobNum'],
                                                            txt_address = dct_cust_details['vchr_customer_addres'],
                                                            fk_location = ins_location,
                                                            fk_state = ins_state,
                                                            int_cust_type = dct_cust_details['intcustomertype'],

                                                         )
                    # int_sales_customer_id = ins_sales_customer.pk_bint_id
    # ================================================================================================================
                    int_customer_id = ins_customer.pk_bint_id

                else:
                    int_customer_id = ins_customer['pk_bint_id']
                    CustomerDetails.objects.filter(pk_bint_id = int_customer_id).update(txt_address = dct_cust_details['vchr_customer_addres'])
                    SalesCustomerDetails.objects.filter(fk_customer_id = int_customer_id).update(txt_address = dct_cust_details['vchr_customer_addres'])

                # ins_document = Document.objects.get(vchr_module_name = 'RECEIPT',
                # vchr_short_code = 'RV')
                # str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                # ins_document.int_number = ins_document.int_number+1
                # ins_document.save()
                # import pdb; pdb.set_trace()
                if not request.data.get('AdvanceBookingStatus'):
                    if request.data.get('branchcode'):
                        vchr_branch_code_is = request.data.get('branchcode')
                        ins_branch_id_data = Branch.objects.filter(vchr_code = request.data.get('branchcode')).values('pk_bint_id').first()
                        int_branch_id_is = ins_branch_id_data['pk_bint_id']
                    else:
                        vchr_branch_code_is = request.user.userdetails.fk_branch.vchr_code
                        int_branch_id_is = request.user.userdetails.fk_branch_id

                    # ins_document = Document.objects.select_for_update().filter(vchr_module_name = "RECEIPT",vchr_short_code = vchr_branch_code_is).first()
                    # if not ins_document:
                    #     ins_document = Document.objects.create(vchr_module_name = "RECEIPT",vchr_short_code = vchr_branch_code_is,int_number = 1)
                    #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                    #     ins_document.int_number = ins_document.int_number+1
                    #     ins_document.save()
                    # else:
                    #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                    #     Document.objects.filter(vchr_module_name = "RECEIPT",vchr_short_code = vchr_branch_code_is).update(int_number = ins_document.int_number+1)

                    # LG 27-06-2020
                    str_inv_num = doc_num_generator('RECEIPT',request.user.userdetails.fk_branch.pk_bint_id)
                    if not str_inv_num:
                        return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                    ins_item = Item.objects.filter(vchr_item_code=request.data.get('strItemCode')).first()
                    if ins_item:
                        # ins_receipt = Receipt.objects.create_recpt_num(str_inv_num)
                        ins_receipt = Receipt.objects.create(vchr_receipt_num=str_inv_num,fk_branch_id = int_branch_id_is,dat_issue = datetime.now(),fk_item = ins_item, fk_customer_id = int_customer_id, int_fop = int_fop, dbl_amount = dbl_amount, vchr_remarks = vchr_remarks, fk_created_id = int_user_id, dat_created = datetime.now(), int_doc_status = 6, int_pstatus = 6, int_receipt_type = 6)
                    else:
                        return Response({'status':0 , 'message' : 'Item Not Found'})

                else:
                    # import pdb; pdb.set_trace()
                    ins_partial_receipt = PartialReceipt.objects.create(
                                                                        json_data = json.dumps(dct_cust_details),
                                                                        fk_enquiry_master_id = request.data.get('intenqmasterid'),
                                                                        vchr_branchcode = request.data.get('branchcode'),
                                                                        vchr_item_code = request.data.get('strItemCode'),
                                                                        int_status = 0,
                                                                        dat_created=datetime.now()
                                                                        )
                    ins_partial_receipt.save()
                    return Response({'status':1})

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e)})


class AddReceiptPending(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            with transaction.atomic():
                if request.data.get('blnPrint'):
                        url = settings.BI_HOSTNAME +'/service/print_service/'
                        try:
                            res_data = requests.post(url,json={"item_service_id":request.data.get('int_service_id'),"bln_pos":True})
                            if res_data.json()['status']=='failed':
                                return JsonResponse({'status': 'Failed','data':res_data.json()['message']})
                        except Exception as e:
                            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})

                        # pdf_path = settings.MEDIA_ROOT+'/'
                        # pdf_name ='Jobslip.pdf'
                        # filename = pdf_path+pdf_name
                        # pdfkit.from_string(res_data.json()['file'],filename)
                        # fs = FileSystemStorage()
                        # lst_encoded_string=[]
                        # if fs.exists(filename):
                        #     with fs.open(filename) as pdf:
                        #         lst_encoded_string.append(str(base64.b64encode(pdf.read())))
                        # file_details = {}
                        # file_details['file'] = lst_encoded_string
                        # file_details['file_name'] = pdf_name
                        file_details = request.data.get('file')
                        return Response({"status":1,"file":file_details})

                int_fop = request.data.get('intFop') or 1
                dbl_amount = request.data.get('service_advance')
                vchr_remarks = request.data.get('vchr_followup_remarks')
                ins_user = request.user
                int_user_id = request.user.id
                dct_toBi=request.data
                dct_toBi['username']=request.user.username
                ins_p=PartialInvoice.objects.filter(pk_bint_id=request.data.get('partial_id')).values()
                dct_cust_details=ins_p.values('json_data').first()['json_data']
                for item in dct_cust_details['lst_items']:
                    if item['int_service_id']==request.data.get('int_service_id'):
                        item['vchr_job_status']=request.data['vchr_followup_status']
                        item['dat_exp_delivery']=request.data['dat_followup']
                        item['dbl_advc_paid'] = request.data.get('service_advance') or 0
                        item['dbl_discount'] = request.data.get('service_discount') or 0
                        # item['dbl_est_amt'] =request.data.get('int_followup_amount')
                        item['str_remarks']= request.data.get('vchr_followup_remarks')

                ins_p.update(json_data=dct_cust_details)

                if  request.data['vchr_followup_status'] == 'LOST':
                    url =settings.BI_HOSTNAME + "/service/service_invoice_update/"

                    res_data = requests.post(url,json={'status':'LOST',"int_enq_master_id":ins_p[0]['int_enq_master_id'],"str_remarks":request.data.get('vchr_followup_remarks')})
                    if res_data.json().get('status')=='success':
                        pass
                    else:
                        raise ValueError('Something happened in BI')
                else:
                    ins_customer = CustomerDetails.objects.filter(int_mobile = dct_cust_details['int_cust_mob']).values('pk_bint_id').first()
                    if not ins_customer:
                        ins_state = States.objects.filter(vchr_code = dct_cust_details['vchr_state_code']).first()
                        ins_location = Location.objects.filter(vchr_name__contains = dct_cust_details['vchr_location'], vchr_pin_code = dct_cust_details['vchr_pin_code']).first()
                        ins_customer = CustomerDetails.objects.create(vchr_name = dct_cust_details['str_cust_name'],vchr_email = dct_cust_details['vchr_cust_email'],int_mobile = dct_cust_details['int_cust_mob'], fk_location = ins_location,fk_state = ins_state)
                        int_customer_id = ins_customer.pk_bint_id
                    else:
                        int_customer_id = ins_customer['pk_bint_id']

                    # ins_document = Document.objects.get(vchr_module_name = 'RECEIPT',vchr_short_code = 'RV')
                    # str_inv_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                    # ins_document.int_number = ins_document.int_number+1
                    # ins_document.save()
                    # ins_document = Document.objects.select_for_update().filter(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).first()
                    # if not ins_document:
                    #     ins_document = Document.objects.create(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code,int_number = 1)
                    #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                    #     ins_document.int_number = ins_document.int_number+1
                    #     ins_document.save()
                    # else:
                    #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                    #     Document.objects.filter(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).update(int_number = ins_document.int_number+1)

                    # LG 27-06-2020
                    str_inv_num = doc_num_generator('RECEIPT',request.user.userdetails.fk_branch.pk_bint_id)
                    if not str_inv_num:
                        return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                    ins_item = Item.objects.filter(vchr_item_code=request.data.get('int_item_code')).first()
                    if ins_item:
                        # int_document_id LG added fk_branch_id
                        # import pdb; pdb.set_trace()
                        # ins_receipt = Receipt.objects.create_recpt_num(str_inv_num)
                        ins_receipt = Receipt.objects.create(vchr_receipt_num=str_inv_num,int_document_id = request.data.get('partial_id'), fk_branch_id = request.user.userdetails.fk_branch_id, dat_issue = datetime.now(),fk_item = ins_item, fk_customer_id = int_customer_id, int_fop = int_fop, dbl_amount = dbl_amount, vchr_remarks = vchr_remarks, fk_created_id = int_user_id, dat_created = datetime.now(), int_doc_status = 0, int_pstatus = 0, int_receipt_type = 4,vchr_card_num=request.data.get('vchrCardNUmber'),vchr_transaction_id=request.data.get('vchrReferenceNumber'),fk_bank_id = request.data.get('intBankId'))
                        if create_posting_data(request,ins_receipt.pk_bint_id):
                            pass
                        else:
                            raise ValueError('Something happened in POS Receipt')
                    else:
                        return Response({'status':0 , 'message' : 'Item Not Found'})
                    url = settings.BI_HOSTNAME+"/service/service_followup/"
                    # try:
                    res_data = requests.post(url,json=dct_toBi)
                    if res_data.json()['status']=='failed':
                        return JsonResponse({'status': 'Failed','data':res_data.json()['message']})
                    # except Exception as e:
                        # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
                    #FOR PRINTING A RECEIPT TO THE CUSTOMER


            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e)})


def PrintReceipt(int_receipt_id):

    purchase_item = ""
    # int_receipt_id = 3
    dict_receipt_details=Receipt.objects.filter(pk_bint_id=int_receipt_id).values('fk_customer__vchr_name','fk_customer__int_mobile','dat_issue','vchr_bank','dbl_amount','vchr_receipt_num','int_fop','vchr_remarks','fk_item_id__vchr_name',"fk_branch__vchr_code","fk_branch__vchr_mygcare_no","fk_branch__vchr_address","fk_branch__vchr_phone","fk_branch__vchr_email","fk_branch__fk_location_master__int_code").first()
    dict_terms= Terms.objects.filter(int_status=0,fk_type__vchr_name='receipt').values('jsn_terms').first()
    dict_receipt_details['terms']=dict_terms.get('jsn_terms')
    str_mygcare_num = dict_receipt_details['fk_branch__vchr_mygcare_no'] if dict_receipt_details['fk_branch__vchr_mygcare_no'] else " "
    list_type=['',"Cash","Debit Card","Credit Card","Cheque","RTGS","NEFT","Paytm","Paytm Mall","Bharath QR"]

    str_amount_words=num2words.num2words(dict_receipt_details['dbl_amount']).title().split("Point")
    if len(str_amount_words)==2:
        str_amount_words=str_amount_words[0]+" Rupees and "+str_amount_words[1]+" Paise only/-"
    else:
        str_amount_words=str_amount_words[0] +" Rupees only/-"


    if(dict_receipt_details['fk_item_id__vchr_name'] != None):
        purchase_item =" Pre Booking For  " + str(dict_receipt_details['fk_item_id__vchr_name']) +"<br> Received With Thanks,<br> By  "
    else:
        purchase_item = "Received With Thanks,<br> By "
    dict_receipt_details['branch_GSTIN'] = '32AAAFZ4615J1Z8'
    if dict_receipt_details['fk_branch__vchr_code']=='AGY':
        dict_receipt_details['branch_GSTIN'] = '32AAIFC7578H2Z7'
    str_gstin = str(dict_receipt_details['branch_GSTIN'])
    str_branch_address = dict_receipt_details.get('fk_branch__vchr_address') or " "
    str_branch_phone = dict_receipt_details.get('fk_branch__vchr_phone') or " "
    str_branch_email = dict_receipt_details.get('fk_branch__vchr_email') or " "
    str_branch_pin_code = dict_receipt_details.get('fk_branch__fk_location_master__int_code') or " "
    # import pdb; pdb.set_trace()

    html_data="""<!doctype html>,
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
                	</style>
                </head>

                <body>
<div class="container">
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
        <p> """+str(str_branch_address)+"""</p>
        </div>
        </div>

               <div style="width:50%;float:left;">

               <div style="width:15%;float:left">
               <p><span style="font-weight: 600;">PH : </span></p>
               </div>
               <div style="width:83%;float: right">
            <p> """+str(str_branch_phone)+"""</p>
               </div>

           </div>
                 <div style="width:50%;float:right;">

            <div style="width:25%;float:left">
               <p><span style="font-weight: 600;">MOB : </span></p>
               </div>
               <div style="width:73%;float: right">
            <p>  """+str(str_branch_phone)+"""</p>
               </div>
        </div>
                        <div style="width:50%;float:left;">
           <div style="width:45%;float:left">
          <p><span style="font-weight: 600;">MYG CARE : </span></p>
           </div>
           <div style="width:54%;float: right">
        <p>   """+str(str_mygcare_num)+"""</p>
           </div>

           </div>
                 <div style="width:50%;float:right;">
            <div style="width:35%;float:left">
                 <p><span style="font-weight: 600;">EMAIL ID : </span></p>
               </div>
               <div style="width:65%;float: right">
            <p>    """+str(str_branch_email)+"""</p>
               </div>
        </div>
               <div style="width:100%;float:left;">
            <p><span style="font-weight: 600;">GSTN : </span>"""+str_gstin+"""</p>
           </div>

            </div>
               <div class="ibox3" style="text-align: right;">
               <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
               <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
               <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
               </div>

                			<div style="width: 100%;float:left;text-align: center;">
                				<!-- <h4>3G MOBILE WORLD MANIYATTUKKUDI ASFA BUILDING CALICUT-673004</h4> -->
                		    </div>

                		    <table id="voucher">
                				    <thead>
                						    <tr>
                								<th colspan="3" style="text-align: center;font-size: 20px;text-decoration-line: underline;color: green;">Receipt Voucher</th>
                						    </tr>
                				    </thead>
                					<tbody>
                						    <tr>
                								<td>To,</td>
                								<td style="text-align: right;">RV No :</td>
                								<td style="text-align: right;width: 110px;">"""+str(dict_receipt_details['vchr_receipt_num'])

    html_data +=                          """</td>
                						    </tr>
                						    <tr>

                							    <td style="padding-left: 44px;">"""+str(dict_receipt_details['fk_customer__vchr_name'])+"""<br>"""+str(dict_receipt_details['fk_customer__int_mobile'])
    html_data+=                            """</td>
                								<td style="text-align: right;">RV Date :</td>
                								<td style="text-align: right;width: 110px;">"""+str(dict_receipt_details['dat_issue'].strftime('%d-%m-%Y'))

    html_data+=                            """</td>
                						    </tr>
                						    <tr style="border-top: 1px solid #e2e2e2;border-bottom: 1px solid #e2e2e2;">
                								<th colspan="2" style="text-align: left;">Particulars</th>
                								<th style="text-align: right">Amount</th>
                						    </tr>
                                            <tr>
                								 <td colspan="2">""" +str(purchase_item)+"""
                									 <span style="color: green;font-weight: 600">"""+str(list_type[dict_receipt_details['int_fop']])
    temp_data=                           """<span style="color: green;font-weight: 600">06/10/2019 </span><br>
                									 Drawn at:HDFC"""
    html_data+= """								</td>
                								 <td style="text-align: right">"""+str(dict_receipt_details['dbl_amount'])
    html_data+=                          """</td>
                						    </tr>
                						    <tr>
                								<td colspan="2">"""+str(dict_receipt_details['vchr_remarks'])
    html_data+= """								</td>
                						    </tr>
                					</tbody>

                				 <tfoot>

                					       <tr style="background-color: whitesmoke;">
                							    <td></td>
                							    <td style="text-align: right;font-weight: 600;">Total : </td>
                							    <td style="text-align: right;font-weight: 600;">"""+str(dict_receipt_details['dbl_amount'])
    html_data+=                        """</td>
                					       </tr>
                				 </tfoot>
                		     </table>
                		    <div class="clear"></div>
                		    <p>"""+str(str_amount_words)


    html_data+= """

                		    <div style="width: 50%;float:left;">
                				 <p style="font-weight: 600;">Receivers Signature</p>
                		    </div>

                		    <div style="width: 50%;float:left;text-align: right;">
                				 <p style="font-weight: 600;">For Myg</p><br><br><br>
                				 <p style="font-weight: 600;">Authorised Signatory</p>
                		    </div>"""
    html_data+=        """</p>
                            <div style="margin-top: 20px;padding-down: 20px;">
        <p style="font-weight: 600;color: #118b98;"><span style="border-bottom: 2px solid #118b98;">Te</span>rms & Condition</p>
        <ul>"""
    for index in range(1,len(dict_receipt_details['terms'])+1):
        html_data+="""<li>"""+dict_receipt_details['terms'][str(index)]+"""</li>"""
        html_data+="""<br>"""
    html_data +="""</ul></div>

                	</div>
                </body>
                </html>"""

    try:

        pdf_path = settings.MEDIA_ROOT+'/'
        pdf_name = name_change('ReceiptVoucher')+'.pdf'
        filename = pdf_path+pdf_name
        pdfkit.from_string(html_data,filename)
        fs = FileSystemStorage()
        lst_encoded_string=[]
        if fs.exists(filename):
            with fs.open(filename) as pdf:
                lst_encoded_string.append(str(base64.b64encode(pdf.read())))
        file_details = {}
        file_details['file'] = lst_encoded_string
        file_details['file_name'] = pdf_name
        return file_details

    except Exception as e:
        raise


class PrintReceiptView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        str_request_protocol = request.META.get('HTTP_REFERER').split(':')[0]
        file_name=PrintReceipt(request.data.get('receiptId'))
        customer_file_name=PrintReceipt(request.data.get('receiptId'))
        return Response({'status':1,"file_name":file_name,'file_url':str_request_protocol+'://'+request.META['HTTP_HOST']+'/media/'+str(file_name['file_name'])})


class ListReceiptForPayment(APIView):
    """
        Function to get receipt of required customer.
        param  : customer mobile int_number
        return : List of receipt
    """
    permission_classes=[IsAuthenticated]
    def post(self,request):
        bln_receipt = False
        int_customer_mobile = request.data.get("intCustomerMob")

        lst_receipt = Receipt.objects.filter( ~Q(int_doc_status=-1),fk_customer_id__int_mobile = int_customer_mobile,int_pstatus=0,fk_branch_id=request.user.userdetails.fk_branch_id).exclude(int_receipt_type=7).values('dbl_amount','pk_bint_id','vchr_receipt_num').annotate(amount_entered=Value(0,IntegerField()))

        lst_receipt_id = [item['pk_bint_id'] for item in lst_receipt] # list of receipt_id corresponds to the customer

        # sum of receipt amount correspond to same receipt numer without current payment id
        lst_receipt_matching_all = ReceiptInvoiceMatching.objects.filter(fk_receipt_id__in = lst_receipt_id).values('fk_receipt_id').annotate(sum_amt =Sum('dbl_amount'))
        dct_receipt_matching = {item['fk_receipt_id']:item['sum_amt'] for item in lst_receipt_matching_all}

        lst_data = []
        for receipt in range(len(lst_receipt)):
            if lst_receipt[receipt]['pk_bint_id'] in dct_receipt_matching:
                lst_receipt[receipt]['dbl_amount'] = lst_receipt[receipt]['dbl_amount'] - dct_receipt_matching[lst_receipt[receipt]['pk_bint_id']]
            if lst_receipt[receipt]['dbl_amount'] > 0:
                lst_data.append(lst_receipt[receipt])
        if lst_data:
            bln_receipt = True
        return Response({'status':1 , 'lst_receipt' : lst_data,'bln_receipt':bln_receipt})


class BankTypeahead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_banks = []
            if str_search_term != -1:
                ins_bank = Bank.objects.filter((Q(vchr_name__icontains = str_search_term))&Q(int_status = 0)).values('pk_bint_id','vchr_name')
                if ins_bank:
                    for itr_item in ins_bank:
                        dct_bank = {}
                        dct_bank['name'] = itr_item['vchr_name']
                        dct_bank['id'] = itr_item['pk_bint_id']
                        lst_banks.append(dct_bank)
                return Response({'status':1,'data':lst_banks})
        except Exception as e:
            return Response({'result':0,'reason':e})
class ReceiptList(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        try:
            """list receipt"""
            receipt_id = request.GET.get('receiptId')
            dat_to= request.data.get('datTo')
            dat_from= request.data.get('datFrom')
            bln_ho=False
            if receipt_id:
                if request.user.userdetails.fk_branch.int_type in [2,3]:
                    bln_ho=True
                ins_receipt = list(Receipt.objects.filter(pk_bint_id = int(receipt_id)).values('vchr_card_num','pk_bint_id','dat_issue','fk_customer_id','fk_customer_id__vchr_name','int_fop','dbl_amount','fk_customer_id__int_mobile','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','fk_item_id','fk_item__vchr_name','vchr_receipt_num','fk_item_id__fk_product_id','fk_item_id__fk_product_id__vchr_name','dat_approval','fk_bank__vchr_name','vchr_transaction_id','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField())).filter(int_doc_status = 0))
            else:
                if request.user.userdetails.fk_branch.int_type in [2,3]:

                    ins_receipt = list(Receipt.objects.exclude(int_doc_status=-1).values('vchr_card_num','pk_bint_id','fk_customer_id','fk_customer_id__vchr_name','fk_customer_id__int_mobile','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','vchr_receipt_num','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField()),dat_issue = Cast('dat_issue', DateField())).filter(int_doc_status = 0,dat_issue__lte=dat_to,dat_issue__gte = dat_from).order_by('-pk_bint_id'))
                elif request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    ins_receipt = list(Receipt.objects.exclude(int_doc_status=-1).values('vchr_card_num','pk_bint_id','fk_customer_id','fk_customer_id__vchr_name','fk_customer_id__int_mobile','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','vchr_receipt_num','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField()),dat_issue = Cast('dat_issue', DateField())).filter(int_doc_status = 0,dat_issue__lte=dat_to,dat_issue__gte = dat_from).order_by('-pk_bint_id'))

                else:
                    ins_receipt = list(Receipt.objects.filter(fk_branch_id = request.user.userdetails.fk_branch_id,dat_issue__date__lte=dat_to,dat_issue__date__gte = dat_from).exclude(int_doc_status=-1).values('vchr_card_num','pk_bint_id','fk_customer_id','fk_customer_id__vchr_name','fk_customer_id__int_mobile','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','vchr_receipt_num','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField()),dat_issue = Cast('dat_issue', DateField())).filter(int_doc_status = 0).order_by('-pk_bint_id'))


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
                elif ins_data['int_fop'] == 7:
                    ins_data['vchr_fop'] = "Paytm"
                elif ins_data['int_fop'] == 8:
                    ins_data['vchr_fop'] = "Paytm Mall"
                elif ins_data['int_fop'] == 9:
                    ins_data['vchr_fop'] = "Bharath QR"

                if ins_data['int_receipt_type'] == 1:
                    ins_data['vchr_receipt_type'] = "ADVANCE"
                elif ins_data['int_receipt_type'] == 2:
                    ins_data['vchr_receipt_type'] = "PRE-BOOKING"
                elif ins_data['int_receipt_type'] == 3:
                    ins_data['vchr_receipt_type'] = "OTHERS"
                elif ins_data['int_receipt_type'] == 4:
                    ins_data['vchr_receipt_type'] = "SERVICE"
                elif ins_data['int_receipt_type'] == 5:
                    ins_data['vchr_receipt_type'] = "FINANCIER"

                if ins_data['int_pstatus'] == 0:
                    ins_data['vchr_payment_status'] = "RECEIVED"
                if ins_data['int_pstatus'] == 1:
                    ins_data['vchr_payment_status'] = "PENDING"
                ins_data['bln_ho'] = bln_ho
                if ins_data['dat_issue']:
                    ins_data['dat_issue_edit']=ins_data['dat_issue']
                    ins_data['dat_issue']=ins_data['dat_issue'].strftime('%d-%m-%Y')




            return Response({'status':1 , 'data' : ins_receipt})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e) })
    def put(self,request):
        try:
            # import pdb; pdb.set_trace()
            receipt_id = request.GET.get('receiptId')
            dat_to= request.data.get('datTo')
            dat_from= request.data.get('datFrom')
            bln_ho=False
            if receipt_id:
                if request.user.userdetails.fk_branch.int_type in [2,3]:
                    bln_ho=True
                ins_receipt = list(Receipt.objects.filter(pk_bint_id = int(receipt_id)).values('vchr_card_num','pk_bint_id','dat_issue','fk_customer_id','fk_customer_id__vchr_name','int_fop','dbl_amount','fk_customer_id__int_mobile','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','fk_item_id','fk_item__vchr_name','vchr_receipt_num','fk_item_id__fk_product_id','fk_item_id__fk_product_id__vchr_name','dat_approval','fk_bank__vchr_name','vchr_transaction_id','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField())).filter(int_doc_status = 0))
            else:
                if request.user.userdetails.fk_branch.int_type in [2,3]:

                    ins_receipt = list(Receipt.objects.exclude(int_doc_status=-1).values('vchr_card_num','pk_bint_id','fk_customer_id','fk_customer_id__vchr_name','fk_customer_id__int_mobile','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','vchr_receipt_num','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField()),dat_issue = Cast('dat_issue', DateField())).filter(int_doc_status = 0,dat_issue__lte=dat_to,dat_issue__gte = dat_from).order_by('-pk_bint_id'))
                elif request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    ins_receipt = list(Receipt.objects.exclude(int_doc_status=-1).values('vchr_card_num','pk_bint_id','fk_customer_id','fk_customer_id__vchr_name','fk_customer_id__int_mobile','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','vchr_receipt_num','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField()),dat_issue = Cast('dat_issue', DateField())).filter(int_doc_status = 0,dat_issue__lte=dat_to,dat_issue__gte = dat_from).order_by('-pk_bint_id'))

                else:
                    ins_receipt = list(Receipt.objects.filter(fk_branch_id = request.user.userdetails.fk_branch_id,dat_issue__date__lte=dat_to,dat_issue__date__gte = dat_from).exclude(int_doc_status=-1).values('vchr_card_num','pk_bint_id','fk_customer_id','fk_customer_id__vchr_name','fk_customer_id__int_mobile','int_fop','dbl_amount','vchr_remarks','fk_created_id' ,'dat_created','int_doc_status','dat_updated','int_receipt_type','int_pstatus','vchr_receipt_num','fk_branch__vchr_name').annotate(vchr_fop = Value('', output_field=CharField()),dat_issue = Cast('dat_issue', DateField())).filter(int_doc_status = 0).order_by('-pk_bint_id'))


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
                elif ins_data['int_fop'] == 7:
                    ins_data['vchr_fop'] = "Paytm"
                elif ins_data['int_fop'] == 8:
                    ins_data['vchr_fop'] = "Paytm Mall"
                elif ins_data['int_fop'] == 9:
                    ins_data['vchr_fop'] = "Bharath QR"

                if ins_data['int_receipt_type'] == 1:
                    ins_data['vchr_receipt_type'] = "ADVANCE"
                elif ins_data['int_receipt_type'] == 2:
                    ins_data['vchr_receipt_type'] = "PRE-BOOKING"
                elif ins_data['int_receipt_type'] == 3:
                    ins_data['vchr_receipt_type'] = "OTHERS"
                elif ins_data['int_receipt_type'] == 4:
                    ins_data['vchr_receipt_type'] = "SERVICE"
                elif ins_data['int_receipt_type'] == 5:
                    ins_data['vchr_receipt_type'] = "FINANCIER"

                if ins_data['int_pstatus'] == 0:
                    ins_data['vchr_payment_status'] = "RECEIVED"
                if ins_data['int_pstatus'] == 1:
                    ins_data['vchr_payment_status'] = "PENDING"
                ins_data['bln_ho'] = bln_ho
                if ins_data['dat_issue']:
                    ins_data['dat_issue_edit']=ins_data['dat_issue']
                    ins_data['dat_issue']=ins_data['dat_issue'].strftime('%d-%m-%Y')

            dct_report = {'Slno':[],'Date':[],'Branch':[],'Name':[],'Amount':[],'Mode':[], 'Status':[]}
            i = 1
            # total = 0
            for data in ins_receipt:

                dct_report['Slno'].append(i)
                dct_report['Date'].append(data['dat_issue'])
                dct_report['Branch'].append(data['fk_branch__vchr_name'])
                dct_report['Name'].append(data['fk_customer_id__vchr_name'])
                dct_report['Amount'].append(data['dbl_amount'])
                dct_report['Mode'].append(data['vchr_fop'])
                dct_report['Status'].append(data['vchr_payment_status'])

                i = i+1

            # print("Model : ",total)
            # import pdb; pdb.set_trace()
            df = pd.DataFrame(dct_report)
            str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_ReceiptList.xlsx'
            filename =settings.MEDIA_ROOT+'/'+str_file


            # if(os.path.exists(filename)):
            #     os.remove(filename)


            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            workbook = writer.book
            cell_format = workbook.add_format()
            cell_format.set_align('center')
            cell_format1 = workbook.add_format()
            cell_format1.set_align('left')
            df.to_excel(writer,index=False, sheet_name='ReceiptList',columns=['Slno','Date','Branch','Name','Amount','Mode','Status'],startrow=6, startcol=0)
            worksheet = writer.sheets['ReceiptList']
            merge_format1 = workbook.add_format({
                'bold': 20,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size':23
                })

            merge_format2 = workbook.add_format({
            'bold': 6,
            'border': 1,
            'align': 'left',
            'valign': 'vleft',
            'font_size':13
            })
            worksheet.merge_range('A1+:H2', 'Receipt List', merge_format1)
            worksheet.merge_range('A4+:D4', 'Taken By               :  '+request.user.username, merge_format2)
            worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)

            # i=str(i+2)
            # worksheet.write('F'+i, 'Total:-',cell_format)
            # worksheet.write('G'+i, sum_soldprice_mrp,cell_format)
            # worksheet.write('H'+i, sum_dp,cell_format)
            # worksheet.write('I'+i, sum_servicecahrge,cell_format)
            # worksheet.write('J'+i, sum_spareprofit,cell_format)
            # worksheet.write('K'+i, sum_profittax,cell_format)
            # worksheet.write('L'+i, sum_netprofitonjob,cell_format)
            worksheet.set_column('B:B', 20,cell_format)
            worksheet.set_column('B:B', 30,cell_format)
            worksheet.set_column('C:C', 30,cell_format)
            worksheet.set_column('D:D', 30,cell_format)
            worksheet.set_column('E:E', 40,cell_format)
            worksheet.set_column('F:F', 30,cell_format)
            worksheet.set_column('G:G', 20,cell_format)

            # worksheet.set_column('X:X', 15,cell_format)
            # import pdb; pdb.set_trace()
            writer.save()
            return Response({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class CreditSettlement(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                int_invoice_id = request.data.get('intInvoiceId')
                dat_issue = request.data.get('datIssue')
                fk_customer_id = request.data.get('customerId')
                int_fop = request.data.get('intFop')
                dbl_amount = request.data.get('amount')
                vchr_remarks = request.data.get('remarks')
                int_pstatus=request.data.get('intPaymentStatus')
                int_receipt_type=7
                int_card_no=request.data.get('vchrCardNUmber')
                int_bank_id=request.data.get('intBankId')


                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).first()
                # if not ins_document:

                #     ins_document = Document.objects.create(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code,int_number = 1)
                #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     ins_document.int_number = ins_document.int_number+1
                #     ins_document.save()
                # else:
                #     str_inv_num = 'RV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     Document.objects.filter(vchr_module_name = "RECEIPT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).update(int_number = ins_document.int_number+1)

                # LG 27-06-2020
                str_inv_num = doc_num_generator('RECEIPT',request.user.userdetails.fk_branch.pk_bint_id)
                if not str_inv_num:
                    return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                # ins_receipt = Receipt.objects.create_recpt_num(str_inv_num)
                ins_receipt = Receipt.objects.create(vchr_receipt_num=str_inv_num,vchr_card_num=int_card_no,vchr_transaction_id=request.data.get('vchrReferenceNumber'),dat_issue = dat_issue,fk_customer_id = fk_customer_id,int_fop = int_fop,dbl_amount = dbl_amount,vchr_remarks =  vchr_remarks,fk_created_id = request.user.id,dat_created = datetime.today(),int_doc_status = 0,int_pstatus=int_pstatus,int_receipt_type=int_receipt_type,fk_branch = request.user.userdetails.fk_branch,fk_bank_id = int_bank_id,fk_sales_master_id=int_invoice_id)
                if int_fop in [1,2,3,7,8,9]:
                    ReceiptInvoiceMatching.objects.create(fk_receipt_id=ins_receipt.pk_bint_id,dbl_amount=dbl_amount,dat_created=datetime.now(),fk_sales_master_id=int_invoice_id)
                    PaymentDetails.objects.create(fk_sales_master_id=int_invoice_id,int_fop=4,vchr_reff_number=str_inv_num,dbl_receved_amt=dbl_amount,dat_created_at=datetime.now())
                    dct_bi_data = {'fop':4,'amount':dbl_amount,'enq_id':PartialInvoice.objects.get(fk_invoice_id = int_invoice_id).int_enq_master_id}
                    url = settings.BI_HOSTNAME+'/mobile/addpayment/'
                    res_data = requests.post(url,json=dct_bi_data)
                    if res_data.json().get('status')=='success':
                        if create_posting_data(request,ins_receipt.pk_bint_id):
                            SalesMaster.objects.filter(pk_bint_id=int_invoice_id).update(dbl_cust_outstanding=F('dbl_cust_outstanding')-dbl_amount)
                            return Response({'status':1})
                        else:
                            return Response({'status':0 , 'data' : 'Posting Failed'})
                    else:
                        raise ValueError('Something happened in BI')

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0 , 'data' : str(e) })

class CreditCustTypeahead(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_search_term = request.data.get('term',-1)
            lst_customer = []
            if str_search_term != -1:
                ins_customer = CustomerDetails.objects.filter(Q(vchr_name__icontains=str_search_term,int_cust_type=4) | Q(int_mobile__icontains=str_search_term,int_cust_type=4)).values('pk_bint_id','vchr_name','int_mobile')
                lst_customer_ids = list(CustomerDetails.objects.filter(Q(vchr_name__icontains=str_search_term,int_cust_type=4) | Q(int_mobile__icontains=str_search_term,int_cust_type=4)).values_list('pk_bint_id',flat=True))
                dct_cust = SalesMaster.objects.filter(fk_customer__fk_customer_id__in=lst_customer_ids,dbl_cust_outstanding__gt=0).values('fk_customer__fk_customer_id','vchr_invoice_num','dbl_cust_outstanding','pk_bint_id')

                if ins_customer:
                    for itr_item in ins_customer:
                        dct_customer = {}
                        dct_customer['name'] = itr_item['vchr_name'] + ' - ' + str(itr_item['int_mobile'])
                        dct_customer['id'] = itr_item['pk_bint_id']
                        dct_customer['lst_invoice'] = [{'invoice_num':ins_cust['vchr_invoice_num'],'invoice_id':ins_cust['pk_bint_id'],'credit_amount':ins_cust['dbl_cust_outstanding']} for ins_cust in dct_cust if ins_cust['fk_customer__fk_customer_id']==itr_item['pk_bint_id']]
                        dct_customer['phone'] = itr_item['int_mobile']

                        lst_customer.append(dct_customer)
                return Response({'status':1,'data':lst_customer})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})
