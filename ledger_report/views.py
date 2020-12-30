from transaction.models import Transaction
from payment.models import Payment
from branch.models import Branch
from userdetails.models import Userdetails,Financiers
from company.models import FinancialYear
from receipt.models import Receipt,ReceiptInvoiceMatching
from accounts_map.models import AccountsMap
from invoice.models import PaymentDetails
from accounts_map.models import AccountsMap
from invoice.models import SalesMaster
from django.db import transaction
from datetime import datetime
from django.db.models import Q,Value
from sap_api.models import ChartOfAccounts

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from customer.models import CustomerDetails
from django.contrib.auth.models import User
from django.db.models.functions import Concat
import sys
from POS import ins_logger
from django.db.models import Sum
# Create your views here.
from transaction.models import Journal
import psycopg2
from django.conf import settings
# from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
import psycopg2.extras
from global_methods import get_user_privileges,get_price_perm
try:
    userName = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    host = settings.DATABASES['default']['HOST']
    database = settings.DATABASES['default']['NAME']
    conn = psycopg2.connect(host=host,database=database, user=userName, password=password)
    # conn = psycopg2.connect(host="localhost",database="bi", user="admin", password="tms@123")
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    conn.autocommit = True
except Exception as e:
    print ("Cannot connect to Data Base..")



class SystemACTypeahead(APIView):
    """ Expense List"""
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            int_branch_id = request.data.get('int_branch_id')
            str_search = request.data.get('term')
            lst_expense = []

            lst_expense =  ChartOfAccounts.objects.filter(vchr_acc_name__icontains = str_search).values('vchr_acc_name','pk_bint_id')
            return Response({'status':1 , 'data': lst_expense})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class ledger_view(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                lst_branch = list(Branch.objects.values_list('pk_bint_id',flat=True))
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER', 'ASSISTANT BRANCH MANAGER', 'ASM1', 'ASM2', 'ASM3', 'ASM4']:
                lst_branch = [request.user.userdetails.fk_branch_id]
            else:
                dct_privilege = get_user_privileges(request)
                if dct_privilege.get('lst_branches'):
                    lst_branch=dct_privilege['lst_branches']
                else:
                    lst_branch=[request.user.userdetails.fk_branch_id]

            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')
            user_id = request.data.get('userId')
            int_acc_type = request.data.get('intType')
            if request.data.get('blnFromPayment'):
                int_acc_type=4
                user_id = AccountsMap.objects.filter(fk_branch_id = request.user.userdetails.fk_branch_id,vchr_category = 'CASH A/C',int_status = 0).values('fk_coa_id').first()['fk_coa_id']
            if int_acc_type ==4:
                int_acc_type=3
            if request.data.get('intType') ==3:
                ins_expense = AccountsMap.objects.filter(pk_bint_id = user_id).values('fk_coa_id').first()['fk_coa_id']
                user_id = ins_expense

            lst_data = []
            ins_opening_balance = Transaction.objects.filter(int_accounts_id = user_id, int_account_type = int_acc_type, dat_created__date__lt = dat_from,fk_branch_id__in=lst_branch).aggregate(dbl_tot_credit=Sum('dbl_credit'),dbl_tot_debit=Sum('dbl_debit'))
            dbl_tot_cr_dr = 0
            bln_ob_is_credit = False
            if ins_opening_balance:
                dbl_tot_debit = ins_opening_balance['dbl_tot_debit'] if ins_opening_balance['dbl_tot_debit'] else 0
                dbl_tot_credit = ins_opening_balance['dbl_tot_credit'] if ins_opening_balance['dbl_tot_credit'] else 0
                if dbl_tot_debit>dbl_tot_credit:
                    dbl_tot_cr_dr = round(dbl_tot_debit - dbl_tot_credit,2)
                elif dbl_tot_credit>dbl_tot_debit:
                    bln_ob_is_credit=True
                    dbl_tot_cr_dr = round(dbl_tot_credit - dbl_tot_debit,2)

            ins_transactions = Transaction.objects.filter(int_accounts_id = user_id, int_account_type = int_acc_type, dat_created__date__gte = dat_from,dat_created__date__lte = dat_to,fk_branch_id__in=lst_branch).values().order_by('dat_created')
            if ins_transactions and request.data.get('intType') in [1]: # Customer
                for data in ins_transactions:
                    doc_number = ''

                    if data['int_document_type'] in [1]:
                        doc_number = Receipt.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_receipt_num').first()['vchr_receipt_num']
                    elif data['int_document_type'] in [2]:
                        doc_number = Payment.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_doc_num').first()['vchr_doc_num']
                    elif data['int_document_type'] in [3]:
                        doc_number = SalesMaster.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_invoice_num').first()['vchr_invoice_num']
                    elif data['int_document_type'] in [4]:
                        doc_number = Journal.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_jv_num').first()['vchr_jv_num']
                    dct_data = {}
                    dct_data['datDate'] = datetime.strftime(data['dat_created'],'%d-%m-%Y')
                    dct_data['strName'] = CustomerDetails.objects.filter(pk_bint_id = user_id).values('vchr_name').first()['vchr_name']
                    dct_data['dblCredit'] = data['dbl_credit']
                    dct_data['dblDebit'] = data['dbl_debit']
                    dct_data['strDocNumber'] = doc_number
                    lst_data.append(dct_data)

            elif ins_transactions and request.data.get('intType') in [2]: # Staff
                for data in ins_transactions:
                    doc_number = ''
                    if data['int_document_type'] in [1]:
                        doc_number = Receipt.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_receipt_num').first()['vchr_receipt_num']
                    elif data['int_document_type'] in [2]:
                        doc_number = Payment.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_doc_num').first()['vchr_doc_num']
                    elif data['int_document_type'] in [3]:
                        doc_number = SalesMaster.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_invoice_num').first()['vchr_invoice_num']
                    elif data['int_document_type'] in [4]:
                        doc_number = Journal.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_jv_num').first()['vchr_jv_num']

                    dct_data = {}
                    dct_data['datDate'] = datetime.strftime(data['dat_created'],'%d-%m-%Y')
                    dct_data['strName'] = User.objects.filter(id = user_id).annotate(str_name=Concat('first_name', Value(' '), 'last_name')).values('str_name').first()['str_name']
                    dct_data['dblCredit'] = data['dbl_credit']
                    dct_data['dblDebit'] = data['dbl_debit']
                    dct_data['strDocNumber'] = doc_number
                    lst_data.append(dct_data)

            elif ins_transactions and request.data.get('intType') in [3]: # Expense
                for data in ins_transactions:
                    doc_number = ''
                    if data['int_document_type'] in [1]:
                        doc_number = Receipt.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_receipt_num').first()['vchr_receipt_num']
                    elif data['int_document_type'] in [2]:
                        doc_number = Payment.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_doc_num').first()['vchr_doc_num']
                    elif data['int_document_type'] in [3]:
                        doc_number = SalesMaster.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_invoice_num').first()['vchr_invoice_num']
                    elif data['int_document_type'] in [4]:
                        doc_number = Journal.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_jv_num').first()['vchr_jv_num']


                    dct_data = {}
                    dct_data['datDate'] = datetime.strftime(data['dat_created'],'%d-%m-%Y')
                    dct_data['strName'] = AccountsMap.objects.filter(fk_coa_id = user_id).values('fk_coa_id__vchr_acc_name').first()['fk_coa_id__vchr_acc_name']
                    dct_data['dblCredit'] = data['dbl_credit']
                    dct_data['dblDebit'] = data['dbl_debit']
                    dct_data['strDocNumber'] = doc_number
                    lst_data.append(dct_data)

            elif ins_transactions and request.data.get('intType') in [4]: # System A/c
                for data in ins_transactions:
                    doc_number = ''
                    if data['int_document_type'] in [1]:
                        doc_number = Receipt.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_receipt_num').first()['vchr_receipt_num']
                    elif data['int_document_type'] in [2]:
                        doc_number = Payment.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_doc_num').first()['vchr_doc_num']
                    elif data['int_document_type'] in [3]:
                        doc_number = SalesMaster.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_invoice_num').first()['vchr_invoice_num']
                    elif data['int_document_type'] in [4]:
                        doc_number = Journal.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_jv_num').first()['vchr_jv_num']



                    dct_data = {}
                    dct_data['datDate'] = datetime.strftime(data['dat_created'],'%d-%m-%Y')
                    dct_data['strName'] = ChartOfAccounts.objects.filter(pk_bint_id = user_id).values('vchr_acc_name')[0]['vchr_acc_name']
                    dct_data['dblCredit'] = data['dbl_credit']
                    dct_data['dblDebit'] = data['dbl_debit']
                    dct_data['strDocNumber'] = doc_number
                    lst_data.append(dct_data)
            elif ins_transactions and request.data.get('intType') in [5]: # System A/c
                for data in ins_transactions:
                    doc_number = ''
                    if data['int_document_type'] in [1]:
                        doc_number = Receipt.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_receipt_num').first()['vchr_receipt_num']
                    elif data['int_document_type'] in [2]:
                        doc_number = Payment.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_doc_num').first()['vchr_doc_num']
                    elif data['int_document_type'] in [3]:
                        doc_number = SalesMaster.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_invoice_num').first()['vchr_invoice_num']
                    elif data['int_document_type'] in [4]:
                        doc_number = Journal.objects.filter(pk_bint_id = data['int_document_id']).values('vchr_jv_num').first()['vchr_jv_num']

                    dct_data = {}
                    dct_data['datDate'] = datetime.strftime(data['dat_created'],'%d-%m-%Y')
                    dct_data['strName'] = Financiers.objects.filter(pk_bint_id = user_id).values('vchr_name')[0]['vchr_name']
                    dct_data['dblCredit'] = data['dbl_credit']
                    dct_data['dblDebit'] = data['dbl_debit']
                    dct_data['strDocNumber'] = doc_number
                    lst_data.append(dct_data)
            if lst_data:
                return Response({'status':1,'data':sorted(lst_data,key = lambda x: x['datDate'], reverse=True),'dblTotCrDr':dbl_tot_cr_dr,'bln_ob_is_credit':bln_ob_is_credit})
            else:
                return Response({'status':1,'data':[],'dblTotCrDr':dbl_tot_cr_dr,'bln_ob_is_credit':bln_ob_is_credit})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})

    def get(self,request):
        pass
        lst_data = []
        return Response({'status':1,'data':lst_data})



class BranchWiseLedger(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()

            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')

            # str_cash_acc_query = """ with ledger as ( SELECT am.fk_branch_id as am_branch_id,tr.dat_created as dat_created,ca.vchr_acc_name , ca.pk_bint_id as int_cao_id, tr.dbl_credit as dbl_credit ,tr.dbl_debit as dbl_debit ,tr.fk_branch_id as int_branch FROM transaction as tr join chart_of_accounts as ca on tr.int_accounts_id = ca.pk_bint_id and tr.int_account_type = 3 join accounts_map as am on am.fk_coa_id=ca.pk_bint_id and am.vchr_category='CASH A/C' ) select br.pk_bint_id,coa.vchr_acc_name,l.int_cao_id, ROUND(SUM (COALESCE(l.dbl_credit,0))::NUMERIC,2) AS tot_credit, ROUND(SUM (COALESCE(l.dbl_debit,0))::NUMERIC,2) as tot_debit, CASE WHEN (ROUND(SUM (COALESCE(l.dbl_debit,0))::NUMERIC,2) - ROUND(SUM (COALESCE(l.dbl_credit,0))::NUMERIC,2) )>0 THEN (ROUND(SUM (COALESCE(l.dbl_debit,0))::NUMERIC,2) - ROUND(SUM (COALESCE(l.dbl_credit,0))::NUMERIC,2)) ELSE 0 END as tot_amount_debit, CASE WHEN (ROUND(SUM (COALESCE(l.dbl_credit,0))::NUMERIC,2)-ROUND(SUM (COALESCE(l.dbl_debit,0))::NUMERIC,2)) >0 THEN (ROUND(SUM (COALESCE(l.dbl_credit,0))::NUMERIC,2)-ROUND(SUM (COALESCE(l.dbl_debit,0))::NUMERIC,2)) ELSE 0 END as tot_amount_credit, br.vchr_name from branch as br left join ledger as l on br.pk_bint_id = l.int_branch and br.pk_bint_id = l.am_branch_id {dat_filter} join accounts_map as acm on acm.fk_branch_id = br.pk_bint_id join chart_of_accounts as coa on acm.fk_coa_id=coa.pk_bint_id and acm.vchr_category='CASH A/C' where  br.int_status = 0 {branch_filter} group by coa.vchr_acc_name, l.int_cao_id, br.vchr_name,br.pk_bint_id ORDER BY coa.vchr_acc_name ; """

            str_cash_acc_query = """ SELECT opening_balance,current_balance, (opening_balance + current_balance) as closing_balance,account_name,cao_id FROM ((with ledger as ( SELECT am.fk_branch_id as am_branch_id,tr.dat_created as dat_created,ca.vchr_acc_name , ca.pk_bint_id as int_cao_id, tr.dbl_credit as dbl_credit ,tr.dbl_debit as dbl_debit ,tr.fk_branch_id as int_branch FROM transaction as tr join chart_of_accounts as ca on tr.int_accounts_id = ca.pk_bint_id and tr.int_account_type = 3 join accounts_map as am on am.fk_coa_id=ca.pk_bint_id and am.vchr_category='CASH A/C' ) select br.pk_bint_id as branch_id,coa.vchr_acc_name as account_name,l.int_cao_id as cao_id , (ROUND(SUM (COALESCE(l.dbl_debit,0))::NUMERIC,2) - ROUND(SUM (COALESCE(l.dbl_credit,0))::NUMERIC,2) ) as opening_balance from branch as br left join ledger as l on br.pk_bint_id = l.int_branch and br.pk_bint_id = l.am_branch_id {dat_filter_opening} join accounts_map as acm on acm.fk_branch_id = br.pk_bint_id join chart_of_accounts as coa on acm.fk_coa_id=coa.pk_bint_id and acm.vchr_category='CASH A/C' where  br.int_status = 0 {branch_filter} group by coa.vchr_acc_name, l.int_cao_id, br.vchr_name,br.pk_bint_id ORDER BY coa.vchr_acc_name ) as open JOIN (with ledger as ( SELECT am.fk_branch_id as am_branch_id,tr.dat_created as dat_created,ca.vchr_acc_name , ca.pk_bint_id as int_cao_id, tr.dbl_credit as dbl_credit ,tr.dbl_debit as dbl_debit ,tr.fk_branch_id as int_branch FROM transaction as tr join chart_of_accounts as ca on tr.int_accounts_id = ca.pk_bint_id and tr.int_account_type = 3 join accounts_map as am on am.fk_coa_id=ca.pk_bint_id and am.vchr_category='CASH A/C' ) select br.pk_bint_id as branch_id ,coa.vchr_acc_name,l.int_cao_id, (ROUND(SUM (COALESCE(l.dbl_debit,0))::NUMERIC,2) - ROUND(SUM (COALESCE(l.dbl_credit,0))::NUMERIC,2) ) as current_balance from branch as br left join ledger as l on br.pk_bint_id = l.int_branch and br.pk_bint_id = l.am_branch_id {dat_filter_current} join accounts_map as acm on acm.fk_branch_id = br.pk_bint_id join chart_of_accounts as coa on acm.fk_coa_id=coa.pk_bint_id and acm.vchr_category='CASH A/C' where  br.int_status = 0 {branch_filter} group by coa.vchr_acc_name, l.int_cao_id, br.vchr_name,br.pk_bint_id ORDER BY coa.vchr_acc_name ) as current ON current.branch_id = open.branch_id ) as ledg """

            dat_filter_current = "AND l.dat_created :: DATE >= '"+ dat_from+ "'AND l.dat_created :: DATE <= '" + dat_to+"'"
            dat_filter_opening = "AND l.dat_created :: DATE <'"+dat_from+"'"
            branch_filter = ''
            if request.data.get("intBranchId"):
                branch_filter = "AND br.pk_bint_id = " + str(request.data.get("intBranchId"))

            str_cash_acc_query = str_cash_acc_query.format(dat_filter_current = dat_filter_current,dat_filter_opening=dat_filter_opening,branch_filter=branch_filter)
            cur.execute( str_cash_acc_query)
            lst_ledger_data = list(cur.fetchall())

            return Response({'status':1,'data':lst_ledger_data})
            #----------------------------------------------------------------------------------------------------------

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})
