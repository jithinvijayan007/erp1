from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth.models import User
from datetime import datetime,date
from payment.models import Payment,ContraDetails
from POS import ins_logger,settings
import sys, os
import requests
from userdetails.models import Userdetails
from django.db.models import Q
from purchase.models import Document
from purchase.views import doc_num_generator
from django.db import transaction
from customer.models import CustomerDetails
from payment.models import Payment
from invoice.models import Bank
from receipt.models import ReceiptInvoiceMatching,Receipt
from django.db.models import CharField, Case, Value, When,Sum,F,IntegerField,Count
from django.db.models.functions import Concat
from day_closure.models import DayClosureMaster
from accounts_map.models import AccountsMap
from branch.models import Branch
from tool_settings.models import Tools
from django.core.files.storage import FileSystemStorage
import pdfkit
import base64
import num2words
from transaction.views import payment_posting
from supplier.models import Supplier
from generate_file_name import name_change
import pandas as pd

def PrintPayment(int_payment_id):
        # int_payment_id = '2'    # 1
        # int_payment_id = '16'   # 2
        # int_payment_id = '3'    # 3
        # int_payment_id = '11'   # 4
        str_particulars = ""
        int_payee_phone = ""
        dict_payment_details=Payment.objects.filter(pk_bint_id=int_payment_id).values("fk_accounts_map__vchr_category","fk_accounts_map__fk_coa__vchr_acc_name","fk_branch__vchr_code","fk_branch__vchr_mygcare_no","fk_branch__vchr_name","fk_branch__vchr_address","fk_branch__vchr_phone","fk_branch__vchr_email","vchr_doc_num","dat_payment","int_fop", "int_payee_type","fk_payee_id","dbl_amount","fk_bank","fk_approved_by__first_name","fk_approved_by__last_name","vchr_remarks","fk_branch__fk_location_master__int_code").first()
        str_mygcare_num = dict_payment_details['fk_branch__vchr_mygcare_no'] if dict_payment_details['fk_branch__vchr_mygcare_no']  else " "
        if dict_payment_details['int_payee_type'] in [2,3]:
            dict_paid_to = Userdetails.objects.filter(user_ptr_id=dict_payment_details['fk_payee_id']).values("first_name","last_name").first()
            str_paid_to=dict_paid_to['first_name'].title()+" "+dict_paid_to['last_name'].title()
        elif dict_payment_details['int_payee_type'] in [4]:
            str_paid_to=''
        elif dict_payment_details['int_payee_type'] in [6]:
            dict_paid_to = Supplier.objects.filter(pk_bint_id = dict_payment_details['fk_payee_id']).values("vchr_name").first()
            str_paid_to = dict_paid_to["vchr_name"].title()
        else:
            str_paid_to=CustomerDetails.objects.filter(pk_bint_id=dict_payment_details['fk_payee_id']).values('vchr_name','int_mobile').first()
            if(str_paid_to['int_mobile'] != None):
                int_payee_phone=str(str_paid_to['int_mobile'])
                str_paid_to=str(str_paid_to['vchr_name'].title())+'<br>'+int_payee_phone

        str_amount_words=num2words.num2words(dict_payment_details['dbl_amount']).title().split("Point")
        if len(str_amount_words)==2:
            str_amount_words=str_amount_words[0]+" Rupees and "+str_amount_words[1]+" Paise only/-"
        else:
            str_amount_words=str_amount_words[0] +" Rupees only/-"

        """ Particulars Item Text"""
        if(dict_payment_details['int_payee_type'] == 1):
            str_particulars = "Paid by Cash Drawn at "+str(dict_payment_details['fk_branch__vchr_name'].title())
        elif(dict_payment_details['int_payee_type'] == 2):
            str_particulars = (str_paid_to.title()) #Staff Incentive"
            str_paid_to = "Paid by Cash,For <b>Staff Incentive</b>"
        elif(dict_payment_details['int_payee_type'] == 3):
            if(dict_payment_details['fk_accounts_map__vchr_category'] != None):
                str_particulars = "Paid by Cash For Expense,<b>"+str(dict_payment_details['fk_accounts_map__vchr_category'].title())+"</b>"
            else :
                str_particulars = "Paid by Cash For Expense"
            str_particulars,str_paid_to = str_paid_to+str(int_payee_phone),str_particulars
        elif(dict_payment_details['int_payee_type'] == 4):
            str_particulars = str_paid_to
            str_acc_name = dict_payment_details["fk_accounts_map__fk_coa__vchr_acc_name"]
            str_paid_to = "Contra Payee to Contra Payee Account "+str_acc_name+" of Amount "+str(dict_payment_details['dbl_amount'])
            dict_payment_details['vchr_remarks'] = ""
        # else:
        #     str_particulars = "Paid by Cash"
        dict_payment_details['branch_GSTIN'] = '32AAAFZ4615J1Z8'
        if dict_payment_details['fk_branch__vchr_code']=='AGY':
            dict_payment_details['branch_GSTIN'] = '32AAIFC7578H2Z7'
        str_gstin = str(dict_payment_details['branch_GSTIN'])
        str_branch_address = dict_payment_details.get('fk_branch__vchr_address') or " "
        str_branch_phone = dict_payment_details.get('fk_branch__vchr_phone') or " "
        str_branch_email = dict_payment_details.get('fk_branch__vchr_email') or " "
        str_branch_pin_code = dict_payment_details.get('fk_branch__fk_location_master__int_code') or " "

        html_data="""<!doctype html>
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
                                        <p>  """+str(str_branch_phone)+"""</p>
                                           </div>

                                       </div>
                                             <div style="width:50%;float:right;">

                                        <div style="width:25%;float:left">
                                           <p><span style="font-weight: 600;">MOB : </span></p>
                                           </div>
                                           <div style="width:73%;float: right">
                                        <p> """+str(str_branch_phone)+"""</p>
                                           </div>
                                    </div>
                                                    <div style="width:50%;float:left;">
                                       <div style="width:45%;float:left">
                                      <p><span style="font-weight: 600;">MYG CARE : </span></p>
                                       </div>
                                       <div style="width:54%;float: right">
                                    <p> """+str(str_mygcare_num)+"""</p>
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
                        								<th colspan="3" style="text-align: center;font-size: 20px;text-decoration-line: underline;color: green;">Payment Voucher</th>
                        						    </tr>
                        				    </thead>
                        					<tbody>
                        						    <tr>
                        								<td>To,</td>
                        								<td style="text-align: right;">PV No :</td>
                        								<td style="text-align: right;width: 110px;">"""+str(dict_payment_details['vchr_doc_num'])
        html_data+="""</td>
                        						    </tr>
                        						    <tr>

                        							    <td style="padding-left: 44px;">"""+str(str_paid_to)
                                                        # Travelling Expense
        # html_data+="""<br> """+str(int_payee_phone)
        html_data+="""</td>
                        								<td style="text-align: right;">PV Date :</td>
                        								<td style="text-align: right;width: 110px;">"""+str(dict_payment_details['dat_payment'].strftime('%d-%m-%Y'))
        html_data+="""</td>
                        						    </tr>
                        						    <tr style="border-top: 1px solid #e2e2e2;border-bottom: 1px solid #e2e2e2;">
                        								<th colspan="2" style="text-align: left;">Particulars</th>
                        								<th style="text-align: right">Amount</th>
                        						    </tr>
                                                    <tr>

                                                            <td colspan="2">"""+str_particulars
                        								 # <td colspan="2">Paid by Cash Drawn at """+str(dict_payment_details['fk_branch__vchr_name'])
                                                        #  Cash Drawn at
        html_data+="""</td>
                        								 <td style="text-align: right">"""+str(dict_payment_details['dbl_amount'])+"""</td>
                        						    </tr>
                        						    <tr>
                        								<td colspan="2">"""+str(dict_payment_details['vchr_remarks'])
                        									#  Fayis Rahman.T.P (Event & Management Team)
                        									# Travelling exp from   27/8/19</span> to <span style="color: green;font-weight: 600">25/9/19

        html_data+="""<br>"""
                                            # <span style="color: green;font-weight: 600">"""+str(dict_payment_details['vchr_remarks'])+"""</span><br>
        html_data+=                									"""Rs.<span style="color: green;font-weight: 600">"""+str(dict_payment_details['dbl_amount'])+"""</span>
                        								</td>
                        						    </tr>
                        					</tbody>

                        				 <tfoot>

                        					       <tr style="background-color: whitesmoke;">
                        							    <td></td>
                        							    <td style="text-align: right;font-weight: 600;">Total : </td>
                        							    <td style="text-align: right;font-weight: 600;">"""+str(dict_payment_details['dbl_amount'])
                                        # 2259.00
        html_data+="""</td>
                        					       </tr>
                        				 </tfoot>
                        		     </table>
                        		    <div class="clear"></div>
                        		    <p>"""+str_amount_words
                                    # Rupees : Two  thousand two hundred fifty nine only/-
        html_data+="""</p>
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
                        </html>"""
        try:
            pdf_path = settings.MEDIA_ROOT+'/'
            pdf_name =name_change("PaymentVoucher")+'.pdf'
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

class StaffTypeahead(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_search_term = request.data.get('term',-1)
            int_branch = request.data.get('blnBranch',0)
            lst_staff = []
            if str_search_term != -1:
                str_search_term = str_search_term.strip()
                if not int_branch:
                    int_branch = request.user.userdetails.fk_branch_id
                ins_staff = Userdetails.objects.filter((Q(first_name__icontains=str_search_term) | Q(last_name__icontains=str_search_term) ) &Q(is_active = True))
                if request.data.get('blnBranch'):
                    ins_staff=ins_staff.filter(fk_branch_id=int_branch)
                if ins_staff:
                    ins_staff=ins_staff.values('id','first_name','last_name','is_staff','username')
                    for itr_item in ins_staff:
                        dct_staff = {}
                        dct_staff['name'] = itr_item['first_name'] + ' ' + str(itr_item['last_name'])
                        dct_staff['id'] = itr_item['id']
                        if request.data.get('blnBranch'):
                            dct_staff['username'] = itr_item['username']
                        lst_staff.append(dct_staff)
                return Response({'status':1,'data':lst_staff})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


# class ExpenseTypeahead(APIView):
#     permission_classes=[AllowAny]
#     def post(self,request):
#         try:
#             str_search_term = request.data.get('term',-1)
#             lst_expenses = []
#             if str_search_term != -1:
#                 ins_expenses = Userdetails.objects.filter((Q(first_name__icontains=str_search_term) | Q(last_name__icontains=str_search_term))& Q(is_active = True) ).values('id','first_name','last_name','is_staff')
#                 if ins_expenses:
#                     for itr_item in ins_expenses:
#                         dct_expenses = {}
#                         dct_expenses['name'] = itr_item['first_name'] + ' ' + str(itr_item['last_name'])
#                         dct_expenses['id'] = itr_item['id']
#                         lst_expenses.append(dct_expenses)
#                 return Response({'status':1,'data':lst_expenses})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
#             return Response({'status':0,'reason':e})

class ExpenseTypeahead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_terms = request.data.get('terms') or request.data.get('term')
            lst_expenses = []
            if str_terms:
                if request.user.userdetails.fk_group.vchr_name == 'ADMIN':
                    ins_expenses = Userdetails.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name')).filter(Q(full_name__icontains = str_terms) | Q(username__icontains = str_terms), fk_company = request.user.userdetails.fk_company, is_active = True).values('username', 'user_ptr_id','full_name')
                else:
                    ins_expenses = Userdetails.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name')).filter(Q(full_name__icontains = str_terms) | Q(username__icontains = str_terms), is_active = True,fk_branch_id = request.user.userdetails.fk_branch_id).values('username', 'user_ptr_id','full_name')
                for itr_item in ins_expenses:
                    dct_expenses = {}
                    dct_expenses['name'] = itr_item['full_name']
                    dct_expenses['username'] = itr_item['username']
                    dct_expenses['id'] = itr_item['user_ptr_id']
                    lst_expenses.append(dct_expenses)
            return Response({'status':1,'data':lst_expenses})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})


class AddPayment(APIView):
    permission_classes=[AllowAny]
    """add new payment"""
    def post(self,request):
        try:
            with transaction.atomic():
                int_fop = request.data.get("fopSelected")
                # import pdb;pdb.set_trace()
                int_payee_type = request.data.get("intPayeeType") # 1: Adv. Refund, 2:STAFF INCENTIVES, 3: EXPENSES, 4: CONTRA(Bank), 5: CUSTOMER , 6: Ventor
                int_payee_id = request.data.get("intPayeeId")
                int_branch_id = request.data.get("intBranchId")
                flt_amount = request.data.get("intAmount")
                str_remarks = request.data.get("strRemarks")
                dat_payment = request.data.get("date")
                fk_accounts_map_id=None
                if request.data.get("intPayeeType")==2:
                    fk_accounts_map_id = AccountsMap.objects.filter(fk_coa__vchr_acc_code='701020301002',int_status=0).values('pk_bint_id').first()['pk_bint_id']
                elif request.data.get("intPayeeType")==3:
                    fk_accounts_map_id = request.data.get('intAccountsMapId')
                elif request.data.get("intPayeeType")==4 or int_fop == 2:
                    if request.user.userdetails.fk_branch.vchr_code.upper()=='AGY':
                        fk_accounts_map_id = AccountsMap.objects.filter(fk_coa__vchr_acc_code='101010101009',int_status=0).values('pk_bint_id').first()['pk_bint_id']
                    else:
                        fk_accounts_map_id = AccountsMap.objects.filter(fk_coa__vchr_acc_code='201000201001',int_status=0).values('pk_bint_id').first()['pk_bint_id']

                # ins_document = Document.objects.get(vchr_module_name = 'PAYMENT',vchr_short_code = 'DOC')
                # str_doc_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                # ins_document.int_number = ins_document.int_number+1
                # ins_document.save()
                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = "PAYMENT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).first()
                # if not ins_document:
                #     ins_document = Document.objects.create(vchr_module_name = "PAYMENT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code,int_number = 1)
                #     str_doc_num = 'PV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     ins_document.int_number = ins_document.int_number+1
                #     ins_document.save()
                # else:
                #     str_doc_num = 'PV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     Document.objects.filter(vchr_module_name = "PAYMENT",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).update(int_number = ins_document.int_number+1)

                # LG 27-06-2020
                str_doc_num = doc_num_generator('PAYMENT',request.user.userdetails.fk_branch_id)
                if not str_doc_num:
                    return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})

                '''BI API FOR ADDING EXPENSES'''
                if request.data.get("intPayeeType")==3:
                        ins_branch = Branch.objects.filter(pk_bint_id=int_branch_id).values('vchr_code').first()
                        ins_accounts = AccountsMap.objects.filter(pk_bint_id=request.data.get('intAccountsMapId')).values('vchr_category').first()
                        vchr_expenses=vchr_branch_code=''
                        if ins_branch:
                            vchr_branch_code = ins_branch.get('vchr_code')

                        else:
                             raise ValueError('Branch not found')
                        if ins_accounts:
                            vchr_expenses = ins_accounts.get('vchr_category')
                        else:
                            raise ValueError('Expense name not found')
                        dct_data={
                            'vchr_doc_num':str_doc_num,
                            'dat_payment':dat_payment,
                            'vchr_branch_code':vchr_branch_code ,
                            'dbl_amount':flt_amount,
                            'vchr_expenses':vchr_expenses,
                            'user':request.user.username
                            }
                        res_data=requests.post(settings.BI_HOSTNAME+'/expenses/add_payment_pos/',json=dct_data)

                        if res_data.json().get('status')=='failed':
                            raise Exception('Something Happend in BI' +' : '+res_data.json().get('data') )

                # ins_payment = Payment.objects.create_payment_doc(str_doc_num)
                ins_payment = Payment.objects.create(
                                      vchr_doc_num = str_doc_num,
                                      dat_payment = dat_payment,
                                      int_fop = int_fop,
                                      int_payee_type = int_payee_type,
                                      fk_payee_id = int_payee_id,
                                      fk_branch_id = int_branch_id,
                                      dbl_amount = flt_amount,
                                      vchr_remarks = str_remarks,
                                      fk_created_id = request.user.id,
                                      int_approved = 0,
                                      int_doc_status = 0,
                                      dat_created = datetime.now(),
                                      fk_accounts_map_id = fk_accounts_map_id
                                    )
                ins_payment.save()
                #ins_payment = ins_payment.objects.get(pk_bint_id = ins_payment.pk_bint_id)
                ins_contra=ContraDetails(fk_payment=ins_payment,
                                        json_denomination=request.data.get('lstDenominations'))
                ins_contra.save()

                # If customer
                if int_payee_type == 1:
                    lst_receipt = request.data.get("lstReceipt")
                    lst_ins_receipt = []
                    if lst_receipt: #if customer has receipt
                        for receipt in lst_receipt:
                            ins_receipt_matching = ReceiptInvoiceMatching(
                                                    fk_receipt_id = receipt['pk_bint_id'],
                                                    dbl_amount = receipt['amount_entered'],
                                                    dat_created = datetime.now(),
                                                    fk_payment = ins_payment
                                                   )

                            lst_ins_receipt.append(ins_receipt_matching)
                        ReceiptInvoiceMatching.objects.bulk_create(lst_ins_receipt)
                if int_payee_type ==1:
                    CustomerDetails.objects.filter(pk_bint_id=int_payee_id,int_cust_type__in=[1,2]).update(dbl_credit_balance=F('dbl_credit_balance')-flt_amount)
                if payment_posting(ins_payment.pk_bint_id):
                    return Response({'status':1})
                else:
                    raise ValueError('Some Error with Transaction savings')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':str(e)})
    def get(self,request):
        try:
            bln_ho = False
            branch = request.data.get('intBranchId')
            if request.user.userdetails.fk_branch.int_type in [2,3]:
                branch_id=list(Branch.objects.values_list('pk_bint_id',flat=True))
                bln_ho = True
            else:
                branch_id=[request.user.userdetails.fk_branch_id]
            lst_invoice = list(Payment.objects.filter(int_doc_status = 0,fk_branch_id__in=branch_id).extra(select={'date':"to_char(dat_payment, 'DD-MM-YYYY')"}).values('pk_bint_id',
                                                                                                                'date',
                                                                                                                'vchr_doc_num',
                                                                                                                'fk_branch__vchr_name',
                                                                                                                'dbl_amount',
                                                                                                                'int_approved').order_by('-dat_updated','-dat_created'))


            return Response({'status':1 , 'lst_invoice' : lst_invoice, 'bln_ho': bln_ho })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

    def put(self,request):
        try:
            """edit"""
            with transaction.atomic():
                int_fop = request.data.get("fopSelected")
                int_payee_type = request.data.get("intPayeeType")
                int_payee_id = request.data.get("intPayeeId")
                int_branch_id = request.data.get("intBranchId")
                flt_amount = request.data.get("intAmount")
                str_remarks = request.data.get("strRemarks")
                dat_payment = request.data.get("date")
                str_doc_number = request.data.get("strDocNo")

                fk_accounts_map_id=None
                if request.data.get("intPayeeType")==2:
                    fk_accounts_map_id = AccountsMap.objects.filter(fk_coa__vchr_acc_code='701020301002',int_status=0).values('pk_bint_id').first()['pk_bint_id']
                elif request.data.get("intPayeeType")==3:
                    fk_accounts_map_id = request.data.get('intAccountsMapId')
                elif request.data.get("intPayeeType")==4:
                    if request.user.userdetails.fk_branch.vchr_code.upper()=='AGY':
                        fk_accounts_map_id = AccountsMap.objects.filter(fk_coa__vchr_acc_code='101010101009',int_status=0).values('pk_bint_id').first()['pk_bint_id']
                    else:
                        fk_accounts_map_id = AccountsMap.objects.filter(fk_coa__vchr_acc_code='201000201001',int_status=0).values('pk_bint_id').first()['pk_bint_id']


                Payment.objects.filter(vchr_doc_num=str_doc_number).update(
                                                                         int_doc_status = 1,
                                                                         dat_updated = datetime.now()
                                                                        )

                ins_payment = Payment(vchr_doc_num = str_doc_number,
                                      dat_payment = dat_payment,
                                      int_fop = int_fop,
                                      int_payee_type = int_payee_type,
                                      fk_payee_id = int_payee_id,
                                      fk_branch_id = int_branch_id,
                                      dbl_amount = flt_amount,
                                      vchr_remarks = str_remarks,
                                      fk_created_id = request.user.id,
                                      int_approved = 0,
                                      int_doc_status = 0,
                                      dat_created = datetime.now(),
                                      fk_accounts_map_id = fk_accounts_map_id
                                    )
                ins_payment.save()
# =========================================================================================================
                """In case of payment Edit, if payee is customer, then Delete receipt_invoice_matching rows having current payment id.Then add new rows by edited data"""
                if int_payee_type == 1:  # If customer
                    ReceiptInvoiceMatching.objects.filter(fk_payment_id__vchr_doc_num=str_doc_number).delete()
                    lst_receipt =  request.data.get("lstReceipt")
                    lst_ins_receipt = []
                    for receipt in lst_receipt:
                        ins_receipt_matching = ReceiptInvoiceMatching(
                                                        fk_receipt_id = receipt['pk_bint_id'],
                                                        dbl_amount = receipt['amount_entered'],
                                                        dat_created = datetime.now(),
                                                        fk_payment = ins_payment
                                                       )
                        lst_ins_receipt.append(ins_receipt_matching)
                    ReceiptInvoiceMatching.objects.bulk_create(lst_ins_receipt)
# =========================================================================================================
                if int_payee_type ==1:
                    CustomerDetails.objects.filter(pk_bint_id=int_payee_id,int_cust_type__in=[1,2]).update(dbl_credit_balance=F('dbl_credit_balance')-flt_amount)
                ins_contra=ContraDetails(fk_payment=ins_payment,
                                        json_denomination=request.data.get('lstDenominations'))
                ins_contra.save()

                return Response({'status':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})




    def patch(self,request):
        try:
            """approve payment"""
            payment_id = request.data.get("id")
            Payment.objects.filter(pk_bint_id=payment_id).update(int_approved = 1,
                                                                         fk_approved_by_id = request.user.id,
                                                                         dat_updated = datetime.now(),

                                                                        )
            return Response({'status':1 })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class ViewPayment(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    """view payment"""
    def post(self,request):

        try:

            # str_request_protocol = request.META.get('HTTP_REFERER').split(':')[0]
            # file_name=PrintPayment('14')
            # file_url = str_request_protocol+'://'+request.META['HTTP_HOST']+'/media/'+file_name['file_name']
            # return Response({'status':1,"file_name":file_name,'file_url':file_url})


            if request.data.get('paymentId'):
                    str_request_protocol = request.META.get('HTTP_REFERER').split(':')[0]
                    file_name=PrintPayment(request.data.get('paymentId'))
                    file_url = str_request_protocol+'://'+request.META['HTTP_HOST']+'/media/'+file_name['file_name']
                    return Response({'status':1,"file_name":file_name,'file_url':file_url})
            str_doc_num = request.data.get("strDocNo")
            lst_payment = list(Payment.objects.filter(vchr_doc_num = str_doc_num,int_doc_status = 0).extra(select={'date':"to_char(dat_payment, 'DD-MM-YYYY')"}).values('vchr_doc_num',
                                                                                                                                                    'fk_branch__vchr_name',
                                                                                                                                                    'fk_branch_id',
                                                                                                                                                    'date','dbl_amount','dat_payment','dat_created',
                                                                                                                                                    'vchr_remarks',
                                                                                                                                                    'int_payee_type',
                                                                                                                                                    'int_fop',
                                                                                                                                                    'fk_payee_id',
                                                                                                                                                    'pk_bint_id',
                                                                                                                                                    'fk_accounts_map_id',
                                                                                                                                                    'fk_accounts_map__vchr_category')
                                                                                                                                                    )

            if lst_payment[0]['int_payee_type'] == 1:
                lst_customer = CustomerDetails.objects.filter(pk_bint_id = lst_payment[0]['fk_payee_id']).values('vchr_name','int_mobile')
                str_payee_name = lst_customer[0]['vchr_name']
                str_payee_type = "Advance Refund"
                str_cust_mobile = lst_customer[0]['int_mobile']
            elif lst_payment[0]['int_payee_type'] == 5:
                lst_customer = CustomerDetails.objects.filter(pk_bint_id = lst_payment[0]['fk_payee_id']).values('vchr_name','int_mobile')
                str_payee_name = lst_customer[0]['vchr_name']
                str_payee_type = "CUSTOMER"
                str_cust_mobile = lst_customer[0]['int_mobile']

            elif lst_payment[0]['int_payee_type'] == 6:
                lst_supplier = Supplier.objects.filter(pk_bint_id = lst_payment[0]['fk_payee_id']).values('vchr_name')
                str_payee_name = lst_supplier[0]['vchr_name']
                str_payee_type = "VENDOR"

            elif lst_payment[0]['int_payee_type'] == 2:

                lst_staff = Userdetails.objects.filter(Q(id = lst_payment[0]['fk_payee_id']) & Q(is_active=True)).values('id','first_name','last_name')
                str_payee_name = lst_staff[0]['first_name'] + " " +lst_staff[0]['last_name']
                str_payee_type = "STAFF INCENTIVES"
            elif lst_payment[0]['int_payee_type'] == 3:
                lst_expense = Userdetails.objects.filter(id = lst_payment[0]['fk_payee_id'],is_active=True).values('id','first_name','last_name')
                str_payee_name = lst_expense[0]['first_name'] + " " +lst_expense[0]['last_name']
                str_payee_type = "EXPENSES"
            elif lst_payment[0]['int_payee_type'] == 4:
                lst_bank = Bank.objects.filter(pk_bint_id = lst_payment[0]['fk_payee_id'],int_status =0).values('pk_bint_id','vchr_name').first()
                str_payee_name = lst_bank['vchr_name']
                str_payee_type = "CONTRA"
            else:
                pass
            str_time_created=lst_payment[0]['dat_created'].time().strftime('%H:%M')
            if lst_payment[0]['int_fop'] == 1:
                str_fop_type = "CASH"
            elif lst_payment[0]['int_fop'] == 2:
                str_fop_type = "BANK"


            dict_extra = {"str_payee_name":str_payee_name,'str_payee_type':str_payee_type,"str_fop_type":str_fop_type,'str_time_created':str_time_created}

            lst_payment[0].update(dict_extra) #updating dictionary inside list with new keys in 'dict_extra'

            #ContraDetails
            ins_contra=ContraDetails.objects.filter(fk_payment_id=lst_payment[0]['pk_bint_id']).first()
            if ins_contra:
                lst_payment[0]['dct_denomination']=ins_contra.json_denomination

            lst_payment[0]['bln_receipt'] = False
            # ================If customer used receipt for payment =====================================
            if lst_payment[0]['int_payee_type'] == 1:
                lst_data_receipt = []

                lst_receipt = Receipt.objects.filter( ~Q(int_doc_status=-1),fk_customer_id = lst_payment[0]['fk_payee_id'],int_pstatus=0).values('dbl_amount','pk_bint_id','vchr_receipt_num').exclude(int_receipt_type=4).annotate(amount_entered=Value(0,IntegerField()))
                lst_receipt_id = [item['pk_bint_id'] for item in lst_receipt] # list of receipt_id corresponds to the customer

                # sum of receipt amount correspond to same receipt numer without current payment id
                lst_receipt_matching_all = ReceiptInvoiceMatching.objects.filter(Q(fk_receipt_id__in = lst_receipt_id),~Q(fk_payment__vchr_doc_num = str_doc_num)).values('fk_receipt_id').annotate(sum_amt =Sum('dbl_amount'))
                dct_receipt_matching = {item['fk_receipt_id']:item['sum_amt'] for item in lst_receipt_matching_all}

                for receipt in range(len(lst_receipt)):
                    if lst_receipt[receipt]['pk_bint_id'] in dct_receipt_matching:
                        lst_receipt[receipt]['dbl_amount'] = lst_receipt[receipt]['dbl_amount'] - dct_receipt_matching[lst_receipt[receipt]['pk_bint_id']]

                if ReceiptInvoiceMatching.objects.filter(fk_payment__vchr_doc_num = str_doc_num):

                    lst_receipt_matching = ReceiptInvoiceMatching.objects.filter(fk_payment__vchr_doc_num = str_doc_num).values('fk_receipt_id','fk_receipt__vchr_receipt_num','dbl_amount')
                    if lst_receipt_matching:
                        lst_payment[0]['dct_receipt_entered'] = {item['fk_receipt_id']:item['dbl_amount'] for item in lst_receipt_matching}

                        if lst_receipt:
                            for item in range(len(lst_receipt)):
                                lst_receipt[item]['amount_entered'] = lst_payment[0]['dct_receipt_entered'].get(lst_receipt[item]['pk_bint_id'],0)
                                # lst_receipt[item]['dbl_amount'] = lst_receipt[item]['dbl_amount'] + lst_receipt[item]['amount_entered']
                                if lst_receipt[item]['dbl_amount']>0:
                                    lst_data_receipt.append(lst_receipt[item])

                            lst_payment[0]['lst_receipt']  = lst_data_receipt
                            lst_payment[0]['bln_receipt'] = True
                            # lst_payment[0]['lst_receipt']  = lst_receipt
                        lst_payment[0]['str_receipt'] = ','.join([item['fk_receipt__vchr_receipt_num']+' - Amount : '+str(int(item['dbl_amount']))  for item in lst_receipt_matching])
                # =====================================================



            return Response({'status':1 , 'data' : lst_payment})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class BankList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            lst_bank = Bank.objects.filter(int_status=0).values('pk_bint_id','vchr_name') or []
            return Response({'status':1 , 'data': lst_bank})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

# class BankList(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self,request):
#         try:
#             lst_bank = Bank.objects.filter(int_status=0).values('pk_bint_id','vchr_name') or []
#             return Response({'status':1 , 'data': lst_bank})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
#             return Response({'status':0,'reason':e})

class DenominationList(APIView):
    permission_classes=[IsAuthenticated]
    def get (self,request):
        try:
            lst_denomination = list(DayClosureMaster.objects.values())
            # import pdb; pdb.set_trace()
            dat_today=date.today().strftime("%Y-%m-%d")
            #checking for today contra entry using todays date and ordering in descenting using pk_bint_id
            ins_today_check=Payment.objects.filter(dat_created__date=dat_today,int_payee_type=4,fk_branch_id=request.user.userdetails.fk_branch_id).order_by("-pk_bint_id").values("fk_created__first_name","fk_created__last_name","dbl_amount","dat_created").first()
            if ins_today_check:
                ins_today_check['name'] = str(ins_today_check['fk_created__first_name']) +' '+str(ins_today_check['fk_created__last_name'])
                return Response({'status':1 , 'data': lst_denomination,"contra_data":ins_today_check})
            else:
                return Response({'status':1 , 'data': lst_denomination,"contra_data":{}})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class ExpenseAccountApi(APIView):
    permission_classes=[IsAuthenticated]
    def post (self,request):
        try:
            vchr_module_name = request.data.get('moduleName').upper()
            lst_accounts = list(AccountsMap.objects.filter(vchr_module_name=vchr_module_name,int_status=0).values('pk_bint_id','vchr_category'))
            return Response({'status':1 , 'data': lst_accounts})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class ExpenseList(APIView):
    """ Expense List"""
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            int_branch_id = request.data.get('int_branch_id')
            str_search = request.data.get('term')
            lst_expense = []
            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                lst_expense =  AccountsMap.objects.filter(vchr_module_name='EXPENSE',int_status=0,vchr_category__icontains = str_search).values('vchr_category','pk_bint_id')
            else:
                lst_expense =  AccountsMap.objects.filter(Q(fk_branch_id = request.user.userdetails.fk_branch_id) | Q(fk_branch_id = None),vchr_module_name='EXPENSE',int_status=0,vchr_category__icontains = str_search).values('vchr_category','pk_bint_id')
            return Response({'status':1 , 'data': lst_expense})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class AddIncentiveApi(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            with transaction.atomic():
                int_fop = 1
                int_payee_type = 2 # 1: CUSTOMER, 2:STAFF INCENTIVES, 3: EXPENSES, 4: CONTRA(Bank)
                lst_incentive_id = request.data.get("lstIncentive")
                int_branch_id = Branch.objects.filter(vchr_code=request.data.get("branch_code")).values('pk_bint_id')[0]['pk_bint_id']
                dat_payment = request.data.get("dat_created")
                created_by = User.objects.get(username=request.data.get("created_by")).id
                fk_accounts_map_id=None
                fk_accounts_map_id = AccountsMap.objects.filter(fk_coa__vchr_acc_code='701160101002',int_status=0).values('pk_bint_id').first()['pk_bint_id']
                lst_query_set = []
                for dct_incent in lst_incentive_id:
                    # ins_document = Document.objects.select_for_update().get(vchr_module_name = 'DOCUMENT',vchr_short_code = 'DOC')
                    # str_doc_num = ins_document.vchr_short_code+'-'+str(ins_document.int_number).zfill(4)
                    # ins_document.int_number = ins_document.int_number+1
                    # ins_document.save()

                    # LG 27-06-2020
                    str_doc_num = doc_num_generator('DOCUMENT',request.user.userdetails.fk_branch.pk_bint_id)
                    if not str_doc_num:
                        return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})
                    int_payee_id = User.objects.get(username=dct_incent['staff_code']).id

                    # ins_payment = Payment.objects.create_payment_doc(str_doc_num)

                    ins_payment = Payment.objects.create(
                                          vchr_doc_num = str_doc_num,
                                          dat_payment = dat_payment,
                                          int_fop = int_fop,
                                          int_payee_type = int_payee_type,
                                          fk_payee_id = int_payee_id,
                                          fk_branch_id = int_branch_id,
                                          dbl_amount = dct_incent['amount'],
                                          vchr_remarks = 'Staff reward incentive from mygoal',
                                          fk_created_id = created_by,
                                          int_approved = 0,
                                          int_doc_status = 0,
                                          dat_created = dat_payment,
                                          fk_accounts_map_id = fk_accounts_map_id
                                        )
                    lst_query_set.append(ins_payment)
                if lst_query_set:
                    Payment.objects.bulk_create(lst_query_set)
                return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
class PaymentList(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            """list of invoice"""
            bln_ho = False
            dat_to= request.data.get('datTo')
            dat_from= request.data.get('datFrom')
            int_branch = request.data.get('intBranchId')
            # import pdb; pdb.set_trace()
            if request.user.userdetails.fk_branch.int_type in [2,3]:
                branch_id=list(Branch.objects.values_list('pk_bint_id',flat=True))
                bln_ho = True
            elif request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                branch_id=list(Branch.objects.values_list('pk_bint_id',flat=True))
            else:
                branch_id=[request.user.userdetails.fk_branch_id]


            lst_invoice = Payment.objects.filter(int_doc_status = 0,fk_branch_id__in=branch_id,dat_payment__lte=dat_to,dat_payment__gte = dat_from).extra(select={'date':"to_char(dat_payment, 'DD-MM-YYYY')"}).values('pk_bint_id',
                                                                                                                'date',
                                                                                                                'vchr_doc_num',
                                                                                                                'fk_branch__vchr_name',
                                                                                                                'dbl_amount',
                                                                                                                'int_approved',
                                                                                                                'fk_accounts_map_id__fk_coa_id__vchr_acc_name').order_by('-dat_updated','-dat_created')
            if int_branch:
                lst_invoice = lst_invoice.filter(fk_branch_id=int_branch)



            return Response({'status':1 , 'lst_invoice' : list(lst_invoice), 'bln_ho': bln_ho })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

    def put(self,request):
        try:
            # import pdb; pdb.set_trace()
            bln_ho = False
            dat_to= request.data.get('datTo')
            dat_from= request.data.get('datFrom')
            int_branch = request.data.get('intBranchId')
            # import pdb; pdb.set_trace()
            if request.user.userdetails.fk_branch.int_type in [2,3]:
                branch_id=list(Branch.objects.values_list('pk_bint_id',flat=True))
                bln_ho = True
            elif request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                branch_id=list(Branch.objects.values_list('pk_bint_id',flat=True))
            else:
                branch_id=[request.user.userdetails.fk_branch_id]


            lst_invoice = Payment.objects.filter(int_doc_status = 0,fk_branch_id__in=branch_id,dat_payment__lte=dat_to,dat_payment__gte = dat_from).extra(select={'date':"to_char(dat_payment, 'DD-MM-YYYY')"}).values('pk_bint_id',
                                                                                                                'date',
                                                                                                                'vchr_doc_num',
                                                                                                                'fk_branch__vchr_name',
                                                                                                                'dbl_amount',
                                                                                                                'int_approved',
                                                                                                                'fk_accounts_map_id__fk_coa_id__vchr_acc_name').order_by('-dat_updated','-dat_created')
            if int_branch:
                lst_invoice = lst_invoice.filter(fk_branch_id=int_branch)

            dct_report = {'Slno':[],'Date':[],'Doc no':[],'Branch':[],'Ledger Name':[], 'Amount':[]}
            i = 1
            # total = 0
            for data in lst_invoice:

                dct_report['Slno'].append(i)
                dct_report['Date'].append(data['date'])
                dct_report['Doc no'].append(data['vchr_doc_num'])
                dct_report['Branch'].append(data['fk_branch__vchr_name'])
                dct_report['Ledger Name'].append(data['fk_accounts_map_id__fk_coa_id__vchr_acc_name'])
                dct_report['Amount'].append(data['dbl_amount'])

                i = i+1

            # print("Model : ",total)
            # import pdb; pdb.set_trace()
            df = pd.DataFrame(dct_report)
            str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_PaymentList.xlsx'
            filename =settings.MEDIA_ROOT+'/'+str_file


            # if(os.path.exists(filename)):
            #     os.remove(filename)


            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            workbook = writer.book
            cell_format = workbook.add_format()
            cell_format.set_align('center')
            cell_format1 = workbook.add_format()
            cell_format1.set_align('left')
            df.to_excel(writer,index=False, sheet_name='PaymentList',columns=['Slno','Date','Doc no','Branch','Ledger Name','Amount'],startrow=6, startcol=0)
            worksheet = writer.sheets['PaymentList']
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
            worksheet.merge_range('A1+:G2', 'Payment List', merge_format1)
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
            worksheet.set_column('C:C', 30,cell_format)
            worksheet.set_column('D:D', 30,cell_format)
            worksheet.set_column('E:E', 30,cell_format)
            worksheet.set_column('F:F', 40,cell_format)
            worksheet.set_column('G:G', 20,cell_format)

            # worksheet.set_column('X:X', 15,cell_format)
            # import pdb; pdb.set_trace()
            writer.save()
            return Response({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
