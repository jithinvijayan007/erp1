
from transaction.models import Transaction
from payment.models import Payment
from branch.models import Branch
from userdetails.models import UserDetails as Userdetails,Financiers
from company.models import FinancialYear
from receipt.models import Receipt,ReceiptInvoiceMatching
from accounts_map.models import AccountsMap
from invoice.models import PaymentDetails
from accounts_map.models import AccountsMap
from invoice.models import SalesMaster,SalesDetails,FinanceDetails
from django.db import transaction
from datetime import datetime
from sap_api.models import ChartOfAccounts
from django.db.models import CharField, Case, Value, When, Value,Sum,F
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from POS import ins_logger
import sys, os

from purchase.models import Document
from purchase.views import doc_num_generator
from transaction.models import Journal
from sales_return.models import SalesReturn

from aldjemy.core import get_engine


"""Creating Invoice Posting Data's"""
def create_invoice_posting_data(request,pk_bint_id):
    try:
        with transaction.atomic():
            lst_data = []
            ins_branch_data = None
            ins_sales_detail = SalesDetails.objects.filter(fk_master_id=pk_bint_id).aggregate(dbl_indirect_discount =Sum('dbl_indirect_discount'))
            ins_sales_master = SalesMaster.objects.filter(pk_bint_id = pk_bint_id).values('fk_customer__fk_customer_id','dbl_total_amt','dbl_total_tax','fk_branch_id','fk_created_id','json_tax','jsn_addition','jsn_deduction').first()
            # ins_branch_data = AccountsMap.objects.filter(fk_branch_id = ins_sales_master['fk_branch_id'],vchr_category = 'CASH A/C',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first() # Cash Account
            ins_branch_data = ChartOfAccounts.objects.filter(vchr_acc_code='401010101002').values('pk_bint_id')
            """Invoice Entry"""
            # additions and deductions
            dbl_addition=0
            dbl_deduction=0
            if ins_sales_master['jsn_addition']:
                for item in ins_sales_master['jsn_addition'].values():
                    dbl_addition += float(item)
            if ins_sales_master['jsn_deduction']:
                for item in ins_sales_master['jsn_deduction'].values():
                    dbl_deduction += float(item)
            if dbl_addition!=0:
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ChartOfAccounts.objects.filter(vchr_acc_code='ADDITIONS').values('pk_bint_id').first()['pk_bint_id']
                dct_data['ACCOUNT_TYPE']  = 3
                dct_data['DEBIT']  = 0
                dct_data['CREDIT']  = dbl_addition
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 3
                dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)
            if dbl_deduction!=0:
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ChartOfAccounts.objects.filter(vchr_acc_code='DEDUCTIONS').values('pk_bint_id').first()['pk_bint_id']
                dct_data['ACCOUNT_TYPE']  = 3
                dct_data['DEBIT']  = dbl_deduction
                dct_data['CREDIT']  = 0
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 3
                dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)
            # additions and deductions
            # indirect_discount vchr_acc_code='701130101003' and vchr_acc_name = 'Discount Voucher Given A/c.'
            dbl_indirect_discount=0
            if ins_sales_detail and ins_sales_detail['dbl_indirect_discount']!=0:
                dbl_indirect_discount=ins_sales_detail['dbl_indirect_discount']
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ChartOfAccounts.objects.filter(vchr_acc_code='701130101003').values('pk_bint_id').first()['pk_bint_id']
                dct_data['ACCOUNT_TYPE']  = 3
                dct_data['DEBIT']  = ins_sales_detail['dbl_indirect_discount']
                dct_data['CREDIT']  = 0
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 3
                dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)
            # indirect_discount
            dbl_cust_debit_amt = round(ins_sales_master['dbl_total_amt'] + dbl_addition - dbl_deduction - dbl_indirect_discount)
            dbl_sale_amt = 0
            dct_data = {}
            dct_data['ACCOUNT_ID'] = ins_sales_master['fk_customer__fk_customer_id']
            dct_data['ACCOUNT_TYPE']  = 1
            dct_data['DEBIT']  = dbl_cust_debit_amt
            dct_data['CREDIT']  = 0
            dct_data['DOCUMENT_ID'] = pk_bint_id
            dct_data['DOCUMENT_TYPE'] = 3
            dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
            dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
            dct_data['DATE_CREATED'] = datetime.today()
            lst_data.append(dct_data)
            dbl_tot_tax=0
            # import pdb;pdb.set_trace()
            if ins_sales_master['json_tax']:
                dct_tax = dict(ChartOfAccounts.objects.filter(vchr_acc_name__in=['Input IGST A/c.','Input CGST A/c.','Input SGST A/c.','Kerala Flood Cess(KFC)']).values_list('vchr_acc_name','pk_bint_id'))
            for str_tax,tax_amount in ins_sales_master['json_tax'].items():
                if 'SGST' in str_tax:
                    str_tax_acc = 'Input SGST A/c.'
                if 'CGST' in str_tax:
                    str_tax_acc = 'Input CGST A/c.'
                if 'IGST' in str_tax:
                    str_tax_acc = 'Input IGST A/c.'
                if 'KFC' in str_tax:
                    str_tax_acc = 'Kerala Flood Cess(KFC)'
                if tax_amount != 0 and '%' not in str_tax:
                    dct_data = {}
                    dct_data['ACCOUNT_ID'] = dct_tax[str_tax_acc]#ins_branch_data['fk_coa_id__pk_bint_id']
                    dct_data['ACCOUNT_TYPE']  = 3
                    dct_data['DEBIT']  = 0
                    dct_data['CREDIT']  = tax_amount
                    dct_data['DOCUMENT_ID'] = pk_bint_id
                    dct_data['DOCUMENT_TYPE'] = 3
                    dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                    dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                    dct_data['DATE_CREATED'] = datetime.today()
                    dbl_sale_amt += dct_data['CREDIT']
                    dbl_tot_tax += dct_data['CREDIT']
                    lst_data.append(dct_data)
            dct_data = {}
            dct_data['ACCOUNT_ID'] = ins_branch_data[0]['pk_bint_id']
            dct_data['ACCOUNT_TYPE']  = 3
            dct_data['DEBIT']  = 0
            dct_data['CREDIT']  = ins_sales_master['dbl_total_amt'] - dbl_tot_tax
            dct_data['DOCUMENT_ID'] = pk_bint_id
            dct_data['DOCUMENT_TYPE'] = 3
            dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
            dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
            dct_data['DATE_CREATED'] = datetime.today()
            dbl_sale_amt += dct_data['CREDIT']
            lst_data.append(dct_data)
            dbl_sale_amt = round((dbl_sale_amt + dbl_addition - dbl_deduction - dbl_indirect_discount),2)
            # round-off total amount
            if (dbl_sale_amt-dbl_cust_debit_amt)>0:
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ChartOfAccounts.objects.filter(vchr_acc_code='701060301010').values('pk_bint_id').first()['pk_bint_id']
                dct_data['ACCOUNT_TYPE']  = 3
                dct_data['DEBIT']  = round(dbl_sale_amt-dbl_cust_debit_amt,2)
                dct_data['CREDIT']  = 0
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 3
                dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)
            if (dbl_sale_amt-dbl_cust_debit_amt)<0:
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ChartOfAccounts.objects.filter(vchr_acc_code='701060301010').values('pk_bint_id').first()['pk_bint_id']
                dct_data['ACCOUNT_TYPE']  = 3
                dct_data['DEBIT']  = 0
                dct_data['CREDIT']  = round(abs(dbl_sale_amt-dbl_cust_debit_amt),2)
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 3
                dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)
            # round-off total amount
            """Receipt Entry"""
            # if ins_sales_master['dbl_total_amt'] >0:
            dbl_cust_credit_amount=0
            dbl_adv_amount = 0
            ins_fop = PaymentDetails.objects.filter(fk_sales_master_id = pk_bint_id).values('pk_bint_id','int_fop','dbl_receved_amt','vchr_name','dbl_finance_amt')
            ins_adv_amount = PaymentDetails.objects.filter(fk_sales_master_id=pk_bint_id,int_fop=4).values('dbl_receved_amt')
            dbl_adv_amount = ins_adv_amount[0]['dbl_receved_amt'] if ins_adv_amount else 0

            bln_fin=False
            """If Customer has One or Morethan One Payment Method"""
            for data in ins_fop:
                if data['int_fop'] in [1]: # 1 Cash Account
                    ins_branch_data = AccountsMap.objects.filter(fk_branch_id = ins_sales_master['fk_branch_id'],vchr_category = 'CASH A/C',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
                elif data['int_fop'] in [2,3]: # 2 debit card , 3 credit card
                    ins_branch_data = AccountsMap.objects.filter(vchr_category = 'TRANSFER',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
                elif data['int_fop'] in [5]: # 5 Paytm
                    ins_branch_data = AccountsMap.objects.filter(vchr_category = 'PAYTM',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
                elif data['int_fop'] in [6]: # 6 Paytm Mall
                    ins_branch_data = AccountsMap.objects.filter(vchr_category = 'PAYTM MALL',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
                elif data['int_fop'] in [7]: # 7 Bharath Qr
                    ins_branch_data = AccountsMap.objects.filter(vchr_category = 'BHARATH QR',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
                elif data['int_fop'] in [0]: # 0 Finance
                    bln_fin = True
                    ins_branch_data = Financiers.objects.filter(vchr_code=data['vchr_name']).values('pk_bint_id').first()

                if data['int_fop'] not in [4]:
                    dct_data = {}
                    dct_data['ACCOUNT_TYPE']  = 3
                    if data['int_fop'] in [0]:
                        dct_data['ACCOUNT_TYPE']  = 5
                        dct_data['ACCOUNT_ID'] = ins_branch_data['pk_bint_id']
                        dct_data['DEBIT']  = data['dbl_finance_amt']
                    else:
                        dct_data['ACCOUNT_ID'] = ins_branch_data['fk_coa_id__pk_bint_id']
                        dct_data['DEBIT']  = data['dbl_receved_amt']
                    dct_data['CREDIT']  = 0
                    dct_data['DOCUMENT_ID'] = pk_bint_id
                    dct_data['DOCUMENT_TYPE'] = 3
                    dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                    dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                    dct_data['DATE_CREATED'] = datetime.today()
                    dbl_cust_credit_amount+=dct_data['DEBIT']
                    lst_data.append(dct_data)
                # for down payment in the case of finance --starts
                if data['int_fop'] not in [4]:
                    dct_data = {}
                    if data['int_fop'] in [0]:
                        ins_finance = FinanceDetails.objects.filter(fk_payment=data['pk_bint_id']).values('dbl_service_amt','dbl_processing_fee','dbl_dbd_amt').first()
                        dbl_fin_charge=data['dbl_receved_amt'] if data['dbl_receved_amt'] else 0
                        dbl_fin_charge += ins_finance['dbl_service_amt'] if ins_finance['dbl_service_amt'] else 0
                        dbl_fin_charge += ins_finance['dbl_processing_fee'] if ins_finance['dbl_processing_fee'] else 0
                        dbl_fin_charge += ins_finance['dbl_dbd_amt'] if ins_finance['dbl_dbd_amt'] else 0
                        if dbl_fin_charge !=0:
                            dct_data['ACCOUNT_TYPE']  = 3
                            dct_data['ACCOUNT_ID'] = ChartOfAccounts.objects.filter(vchr_acc_code='FINANCE_CHARGES').values('pk_bint_id').first()['pk_bint_id']
                            dct_data['CREDIT']  = dbl_fin_charge
                            dct_data['DEBIT']  = 0
                            dct_data['DOCUMENT_ID'] = pk_bint_id
                            dct_data['DOCUMENT_TYPE'] = 3
                            dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                            dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                            dct_data['DATE_CREATED'] = datetime.today()
                            dbl_cust_credit_amount+=dct_data['DEBIT']
                            lst_data.append(dct_data)
                # for down payment in the case of finance --ends
            if bln_fin:#finance enquiry customer credit amount will full amount
                dbl_cust_credit_amount = round(ins_sales_master['dbl_total_amt'] + dbl_addition - dbl_deduction - dbl_indirect_discount)- dbl_adv_amount

            if dbl_cust_credit_amount:
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ins_sales_master['fk_customer__fk_customer_id']
                dct_data['ACCOUNT_TYPE']  = 1
                dct_data['DEBIT']  = 0
                dct_data['CREDIT']  = dbl_cust_credit_amount
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 3
                dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)
            return(create_transaction_posting(lst_data))
    except Exception as e:
        raise ValueError('Something happened in Transaction')
        return 0


""" Creating Receipt Posting Data's"""
def create_posting_data(request,pk_bint_id,int_origin_branch_id=None):
    try:
        with transaction.atomic():
            str_account_type = ''
            int_account_id = 0
            lst_data = []
            ins_receipt = Receipt.objects.filter(pk_bint_id = pk_bint_id).values('fk_customer_id','dbl_amount','fk_branch_id','fk_branch__vchr_code','int_fop').order_by('-pk_bint_id').first()

            if ins_receipt['int_fop'] in [1]: # 1 cash
                ins_branch_data = AccountsMap.objects.filter(fk_branch_id = ins_receipt['fk_branch_id'],vchr_category = 'CASH A/C',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
            elif ins_receipt['int_fop'] in [2,3]: # 2 debit card , 3 credit card, 4 Cheque, 5 RTGS, 6 NEFT
                ins_branch_data = AccountsMap.objects.filter(vchr_category = 'TRANSFER',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
            elif ins_receipt['int_fop'] in [4,5,6]: #4 Cheque, 5 RTGS, 6 NEFT
                ins_branch_data = AccountsMap.objects.filter(vchr_category = 'CNR',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
                if ins_receipt['fk_branch__vchr_code'] =='AGY':
                    ins_branch_data = AccountsMap.objects.filter(vchr_category = 'ACNR',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()

            elif ins_receipt['int_fop'] in [7]: # 7 Paytm
                ins_branch_data = AccountsMap.objects.filter(vchr_category = 'PAYTM',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
            elif ins_receipt['int_fop'] in [8]: # 8 Paytm Mall
                ins_branch_data = AccountsMap.objects.filter(vchr_category = 'PAYTM MALL',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()
            elif ins_receipt['int_fop'] in [9]: # 9 Bharath Qr
                ins_branch_data = AccountsMap.objects.filter(vchr_category = 'BHARATH QR',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first()

            if ins_branch_data:
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ins_receipt['fk_customer_id']
                dct_data['ACCOUNT_TYPE']  = 1
                dct_data['DEBIT']  = 0
                dct_data['CREDIT']  = ins_receipt['dbl_amount']
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 1
                dct_data['USER_CREATED'] = request.user.userdetails.user_ptr_id
                dct_data['BRANCH_ID'] = int_origin_branch_id or request.user.userdetails.fk_branch.pk_bint_id
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ins_branch_data['fk_coa_id__pk_bint_id']
                dct_data['ACCOUNT_TYPE']  = 3
                dct_data['DEBIT']  = ins_receipt['dbl_amount']
                dct_data['CREDIT']  = 0
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 1
                dct_data['USER_CREATED'] = request.user.userdetails.user_ptr_id
                dct_data['BRANCH_ID'] =  request.user.userdetails.fk_branch.pk_bint_id
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)

            return(create_transaction_posting(lst_data))
    except Exception as e:
        raise ValueError('Something happened in Transaction')
        return 0

"""Creating Transaction Posting"""
def create_transaction_posting(lst_data):
    try:
        with transaction.atomic():
            """Test CREDIT = DEBIT"""
            credit = 0
            debit = 0
            for data in lst_data:
                credit += data['CREDIT']
                debit += data['DEBIT']
            print(credit,debit)

            """Inserting Date to Transaction Data"""
            flag = 0
            if lst_data:
                ins_financial_year = FinancialYear.objects.filter(bln_status = True).first()
                for dct_data in lst_data:
                    if dct_data['DEBIT'] and dct_data['DEBIT']<0:
                        dct_data['DEBIT'],dct_data['CREDIT'] = dct_data['CREDIT'],abs(dct_data['DEBIT'])
                    elif dct_data['CREDIT'] and dct_data['CREDIT']<0:
                        dct_data['CREDIT'],dct_data['DEBIT'] = dct_data['DEBIT'],abs(dct_data['CREDIT'])
                    # ins_user_created = Userdetails.objects.filter(user_ptr_id = dct_data['USER_CREATED']).first()
                    # ins_branch = Branch.objects.filter(pk_bint_id = dct_data['BRANCH_ID']).first()
                    ins_transactions = Transaction.objects.create(
                                                                    dat_created = dct_data['DATE_CREATED'],
                                                                    int_accounts_id = dct_data['ACCOUNT_ID'],
                                                                    int_account_type = dct_data['ACCOUNT_TYPE'],
                                                                    dbl_debit = round(dct_data['DEBIT'],2) if dct_data['DEBIT'] else 0.0,
                                                                    dbl_credit = round(dct_data['CREDIT'],2) if dct_data['CREDIT'] else 0.0,
                                                                    int_document_id = dct_data['DOCUMENT_ID'],
                                                                    int_document_type = dct_data['DOCUMENT_TYPE'],
                                                                    fk_created_id = dct_data['USER_CREATED'],
                                                                    fk_financialyear = ins_financial_year,
                                                                    int_type = 0,
                                                                    fk_branch_id = dct_data['BRANCH_ID']
                                                                    )
                    ins_transactions.save()
                    if not ins_transactions:
                        flag = 1

            if flag:
                raise ValueError('Something happened in Transaction')
                return 0
            else:
                return 1
    except Exception as e:
        raise ValueError('Something happened in Transaction')
        return 0


def payment_posting(pk_bint_id):
    try:
        # import pdb; pdb.set_trace()
        ins_payment = Payment.objects.filter(pk_bint_id=pk_bint_id).values('fk_accounts_map_id__fk_coa_id','fk_branch_id','fk_payee_id','int_fop','int_payee_type','dbl_amount','fk_created_id','dat_created').first()
        int_fop=ins_payment['int_fop']
        lst_data=[]
        if int_fop == 1:#1:CASH 2:BANK
            ins_branch_data = AccountsMap.objects.filter(fk_branch_id = ins_payment['fk_branch_id'],vchr_category = 'CASH A/C',int_status = 0).values('fk_coa_id__pk_bint_id').first()['fk_coa_id__pk_bint_id']
        elif int_fop == 2:
            # ins_branch_data = AccountsMap.objects.filter(vchr_category = 'TRANSFER',int_status = 0).values('fk_coa_id__pk_bint_id').first()['fk_coa_id__pk_bint_id']
            vchr_branchcode=Branch.objects.filter(pk_bint_id=ins_payment['fk_branch_id']).values('vchr_code').first()['vchr_code']
            if vchr_branchcode.upper()=='AGY':
                ins_branch_data = AccountsMap.objects.filter(fk_coa__vchr_acc_code='101010101009',int_status=0).values('fk_coa_id').first()['fk_coa_id']
            else:
                ins_branch_data = AccountsMap.objects.filter(fk_coa__vchr_acc_code='201000201001',int_status=0).values('fk_coa_id').first()['fk_coa_id']
        if ins_payment["int_payee_type"]==1:#Adv. Refund
            int_debt_id=ins_payment['fk_payee_id']
            int_payee_id=1

        elif ins_payment["int_payee_type"]==5:#Customer
            int_debt_id=ins_payment['fk_payee_id']
            int_payee_id=1

        elif ins_payment["int_payee_type"]==2:#2.staff
            dct_data = {}
            dct_data['ACCOUNT_ID'] = ins_payment['fk_payee_id']
            dct_data['ACCOUNT_TYPE']  = 2
            dct_data['DEBIT']  = ins_payment['dbl_amount']
            dct_data['CREDIT']  = 0
            dct_data['DOCUMENT_ID'] = pk_bint_id
            dct_data['DOCUMENT_TYPE'] = 2
            dct_data['USER_CREATED'] = ins_payment['fk_created_id']
            dct_data['BRANCH_ID'] = ins_payment['fk_branch_id']
            dct_data['DATE_CREATED'] = ins_payment['dat_created']
            lst_data.append(dct_data)
            int_debt_id=ins_payment['fk_payee_id']
            int_payee_id=3

        elif ins_payment["int_payee_type"]==3:# 3.expenses
            int_debt_id=ins_payment['fk_payee_id']
            int_payee_id=3

        elif ins_payment["int_payee_type"]==6:# 3.Ventor
            int_debt_id=ins_payment['fk_payee_id']
            int_payee_id=5

        elif ins_payment["int_payee_type"]==4:#4.contra
            int_payee_id=3
            vchr_branchcode=Branch.objects.filter(pk_bint_id=ins_payment['fk_branch_id']).values('vchr_code').first()['vchr_code']
            if vchr_branchcode.upper()=='AGY':
                int_debt_id = AccountsMap.objects.filter(fk_coa__vchr_acc_code='101010101009',int_status=0).values('fk_coa_id').first()['fk_coa_id']
            else:
                int_debt_id = AccountsMap.objects.filter(fk_coa__vchr_acc_code='201000201001',int_status=0).values('fk_coa_id').first()['fk_coa_id']

        if int_debt_id:

            dct_data={}
            if int_payee_id in [2,3,4]:
                dct_data['ACCOUNT_ID']=ins_payment['fk_accounts_map_id__fk_coa_id']
            else:
                dct_data['ACCOUNT_ID'] = ins_payment['fk_payee_id']
            dct_data['ACCOUNT_TYPE']  = int_payee_id
            dct_data['DEBIT']  = ins_payment['dbl_amount']
            dct_data['CREDIT']  = 0
            dct_data['DOCUMENT_ID']=pk_bint_id
            dct_data['DOCUMENT_TYPE']=2
            dct_data['USER_CREATED']=ins_payment['fk_created_id']
            dct_data['BRANCH_ID']=ins_payment['fk_branch_id']
            dct_data['DATE_CREATED']=ins_payment['dat_created']
            lst_data.append(dct_data)

            dct_data = {}
            dct_data['ACCOUNT_ID'] = ins_branch_data
            dct_data['ACCOUNT_TYPE']  = 3
            dct_data['DEBIT']  = 0
            dct_data['CREDIT']  = ins_payment['dbl_amount']
            dct_data['DOCUMENT_ID']=pk_bint_id
            dct_data['DOCUMENT_TYPE']=2
            dct_data['USER_CREATED']=ins_payment['fk_created_id']
            dct_data['BRANCH_ID']=ins_payment['fk_branch_id']
            dct_data['DATE_CREATED']=ins_payment['dat_created']
            lst_data.append(dct_data)

            return(create_transaction_posting(lst_data))
        else:
            return 0

    except Exception as e:
        return 0


"""Creating Invoice Posting Data's"""
def create_return_posting_data(request,pk_bint_id):
    try:
        with transaction.atomic():
            lst_data = []
            ins_branch_data = None

            ins_sales_master = SalesMaster.objects.filter(pk_bint_id = pk_bint_id).values('fk_customer__fk_customer_id','dbl_total_amt','dbl_total_tax','fk_branch_id','fk_created_id','json_tax').first()
            ins_branch_data = ChartOfAccounts.objects.filter(vchr_acc_code='401010101002').values('pk_bint_id') # Cash Account

            dbl_cust_credit_amt = round(abs(ins_sales_master['dbl_total_amt']))
            dbl_retrn_amt = 0

            """Invoice Entry"""
            dct_data = {}
            dct_data['ACCOUNT_ID'] = ins_sales_master['fk_customer__fk_customer_id']
            dct_data['ACCOUNT_TYPE']  = 1
            dct_data['DEBIT']  = 0 #ins_sales_master['dbl_total_amt']
            dct_data['CREDIT']  = dbl_cust_credit_amt
            dct_data['DOCUMENT_ID'] = pk_bint_id
            dct_data['DOCUMENT_TYPE'] = 3
            dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
            dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
            dct_data['DATE_CREATED'] = datetime.today()
            lst_data.append(dct_data)
            dct_data = {}
            dct_data['ACCOUNT_ID'] = ins_branch_data[0]['pk_bint_id']
            dct_data['ACCOUNT_TYPE']  = 3
            dct_data['CREDIT']  = 0
            dct_data['DEBIT']  = abs(ins_sales_master['dbl_total_amt']) - abs(ins_sales_master['dbl_total_tax'])
            dct_data['DOCUMENT_ID'] = pk_bint_id
            dct_data['DOCUMENT_TYPE'] = 3
            dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
            dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
            dct_data['DATE_CREATED'] = datetime.today()
            dbl_retrn_amt += dct_data['DEBIT']
            lst_data.append(dct_data)
            # import pdb;pdb.set_trace()
            if ins_sales_master['json_tax']:
                dct_tax = dict(ChartOfAccounts.objects.filter(vchr_acc_name__in=['Input IGST A/c.','Input CGST A/c.','Input SGST A/c.','Kerala Flood Cess(KFC)']).values_list('vchr_acc_name','pk_bint_id'))
            for str_tax,tax_amount in ins_sales_master['json_tax'].items():
                if 'SGST' in str_tax:
                    str_tax_acc = 'Input SGST A/c.'
                if 'CGST' in str_tax:
                    str_tax_acc = 'Input CGST A/c.'
                if 'IGST' in str_tax:
                    str_tax_acc = 'Input IGST A/c.'
                if 'KFC' in str_tax:
                    str_tax_acc = 'Kerala Flood Cess(KFC)'
                if tax_amount != 0 and '%' not in str_tax:
                    dct_data = {}
                    dct_data['ACCOUNT_ID'] = dct_tax[str_tax_acc]#ins_branch_data['fk_coa_id__pk_bint_id']
                    dct_data['ACCOUNT_TYPE']  = 3
                    dct_data['CREDIT']  = 0
                    dct_data['DEBIT']  = abs(tax_amount)
                    dct_data['DOCUMENT_ID'] = pk_bint_id
                    dct_data['DOCUMENT_TYPE'] = 3
                    dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                    dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                    dct_data['DATE_CREATED'] = datetime.today()
                    dbl_retrn_amt += dct_data['DEBIT']
                    lst_data.append(dct_data)
            dbl_retrn_amt = round(abs(dbl_retrn_amt),2)
            # round-off total amount
            if (dbl_retrn_amt-dbl_cust_credit_amt)>0:
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ChartOfAccounts.objects.filter(vchr_acc_code='701060301010').values('pk_bint_id').first()['pk_bint_id']
                dct_data['ACCOUNT_TYPE']  = 3
                dct_data['DEBIT']  = 0
                dct_data['CREDIT']  = round(dbl_retrn_amt-dbl_cust_credit_amt,2)
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 3
                dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)
            if (dbl_retrn_amt-dbl_cust_credit_amt)<0:
                dct_data = {}
                dct_data['ACCOUNT_ID'] = ChartOfAccounts.objects.filter(vchr_acc_code='701060301010').values('pk_bint_id').first()['pk_bint_id']
                dct_data['ACCOUNT_TYPE']  = 3
                dct_data['DEBIT']  = round(abs(dbl_retrn_amt-dbl_cust_credit_amt),2)
                dct_data['CREDIT']  = 0
                dct_data['DOCUMENT_ID'] = pk_bint_id
                dct_data['DOCUMENT_TYPE'] = 3
                dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                dct_data['DATE_CREATED'] = datetime.today()
                lst_data.append(dct_data)
            # round-off total amount
            return(create_transaction_posting(lst_data))
    except Exception as e:
        raise ValueError('Something happened in Transaction')
        return 0

class JournalView(APIView):
    """
    to add,edit,list,view of journal for pos
    """
    permissions_class = [IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                lst_type=[None,1,2,3,3,3,3,3]            #1 - customer 2-staff 3 - expenses 5- vendor

                # ins_document = Document.objects.select_for_update().filter(vchr_module_name = "JOURNAL",vchr_short_code = request.user.userdetails.fk_branch.vchr_code).first()
                # vchr_short_code=Branch.objects.get(pk_bint_id=request.data.get('intBranchId')).vchr_code

                # if not ins_document:
                #     ins_document = Document.objects.create(vchr_module_name = "JOURNAL",vchr_short_code = vchr_short_code,int_number = 1)
                #     vchr_jvu = 'JV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     ins_document.int_number = ins_document.int_number+1
                #     ins_document.save()
                # else:
                #     vchr_jvu = 'JV-'+(ins_document.vchr_short_code).upper()+'-'+str(ins_document.int_number).zfill(4)
                #     Document.objects.filter(vchr_module_name = "JOURNAL",vchr_short_code = vchr_short_code).update(int_number = ins_document.int_number+1)

                # LG 27-06-2020
                vchr_jvu = doc_num_generator('JOURNAL',request.data.get('intBranchId'))
                if not vchr_jvu:
                    return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})


                ins_financial_year = FinancialYear.objects.filter(bln_status = True).first()
                ins_cash_id=ins_account_id=None
                int_debit_id=int_credit_id=None

                if 5==request.data.get('intDebitType'):
                        int_debit_id = AccountsMap.objects.filter(fk_branch_id = request.data.get('intDebitBranchId'),vchr_category = 'CASH A/C',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first().get('fk_coa_id__pk_bint_id')
                if 5==request.data.get('intCreditType'):

                        int_credit_id = AccountsMap.objects.filter(fk_branch_id = request.data.get('intCreditBranchId'),vchr_category = 'CASH A/C',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first().get('fk_coa_id__pk_bint_id')
                if 6 in (request.data.get('intDebitType'),request.data.get('intCreditType')):
                        ins_account_id= AccountsMap.objects.filter(vchr_category = 'TRANSFER',int_status = 0).values('int_type','fk_coa_id__pk_bint_id').first().get('fk_coa_id__pk_bint_id')


                if request.data.get('intDebitType')==6:
                        int_debit_id=ins_account_id
                if request.data.get('intCreditType')==6:
                        int_credit_id=ins_account_id


                ins_journal=Journal(vchr_jv_num =   vchr_jvu,
                                    fk_debit_branch_id =  request.data.get('intDebitBranchId'),
                                    fk_credit_branch_id =  request.data.get('intCreditBranchId'),
                                    dat_journal =  request.data.get('datJournal'),
                                    int_debit_type=request.data.get('intDebitType'),
                                    int_credit_type =    request.data.get('intCreditType') ,
                                    fk_debit_id = request.data.get('intDebitId') or int_debit_id,
                                    fk_credit_id = request.data.get('intCreditId') or  int_credit_id,
                                    dbl_amount =    request.data.get('intAmount'),
                                    dat_created=datetime.now(),
                                    fk_created_id=request.user.id,
                                    vchr_remarks=request.data.get('strRemarks')
                                    )
                ins_journal.save()




                if request.data.get('intDebitType') not in (5,6,None):
                    int_debit_transaction_type=lst_type[request.data.get('intDebitType')]
                else:
                    int_debit_transaction_type=3
                if request.data.get('intCreditType') not in (5,6):
                    int_credit_transaction_type=lst_type[request.data.get('intCreditType')]
                else:
                    int_credit_transaction_type=3


                int_accounts_debit_id = None
                int_accounts_credit_id= None

                if request.data.get('intDebitType')==3:
                      int_accounts_debit_id=AccountsMap.objects.filter(pk_bint_id=request.data.get('intDebitId')).values('fk_coa_id__pk_bint_id').first().get('fk_coa_id__pk_bint_id')
                if request.data.get('intCreditType')==3:
                      int_accounts_credit_id=AccountsMap.objects.filter(pk_bint_id=request.data.get('intCreditId')).values('fk_coa_id__pk_bint_id').first().get('fk_coa_id__pk_bint_id')





                ins_transaction_debit=Transaction.objects.create(fk_branch_id=request.data.get('intDebitBranchId'),int_document_id=ins_journal.pk_bint_id,int_document_type=4,dat_created=datetime.now(),int_account_type=int_debit_transaction_type,int_accounts_id=int_debit_id or int_accounts_debit_id or request.data.get('intDebitId'),dbl_debit=request.data.get('intAmount'),dbl_credit=0,fk_financialyear=ins_financial_year,int_type=0)

                ins_transaction_credit=Transaction.objects.create(fk_branch_id=request.data.get('intCreditBranchId'),int_document_id=ins_journal.pk_bint_id,int_document_type=4,dat_created=datetime.now(),int_account_type=int_credit_transaction_type,int_accounts_id=int_credit_id or int_accounts_credit_id or request.data.get('intCreditId'),dbl_credit=request.data.get('intAmount'),dbl_debit=0,fk_financialyear=ins_financial_year,int_type=0)
                ins_journal.save()

                return Response({'status':1})

        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(exc, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':exc})
    def put(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()
            str_query="""SELECT jsonb_agg(json_build_object('pk_bint_id',pk_bint_id,'vchr_debit_branch_name',vchr_debit_branch_name,'vchr_credit_branch_name', vchr_credit_branch_name, 'vchr_remarks', vchr_remarks, 'vchr_debit_name', vchr_debit_name,'vchr_credit_name',vchr_credit_name,'vchr_debit_type',vchr_debit_type,'vchr_credit_type',vchr_credit_type,'int_debit_type',int_debit_type,'int_credit_type',int_credit_type,'dat_journal',dat_journal,'dbl_amount',dbl_amount,'vchr_jv_num',vchr_jv_num))
                        FROM   (SELECT fk_debit_branch_id,fk_credit_branch_id,j.pk_bint_id as pk_bint_id,j.dbl_amount as dbl_amount,j.vchr_jv_num as vchr_jv_num,to_char(dat_journal,'DD-MM-YYYY') as dat_journal,int_debit_type,int_credit_type,brd.vchr_name as vchr_debit_branch_name,brc.vchr_name as vchr_credit_branch_name ,vchr_remarks as vchr_remarks,
                                    CASE WHEN int_debit_type=1 THEN INITCAP(cdd.vchr_name) WHEN int_debit_type=2 THEN INITCAP(CONCAT (aud.first_name,' ',aud.last_name))
                                            WHEN int_debit_type=3 THEN INITCAP(amd.vchr_category) WHEN int_debit_type=4 THEN INITCAP(spd.vchr_name) WHEN int_debit_type=5 THEN 'Cash A/C'
                                            WHEN int_debit_type=6 THEN 'Bank A/C' WHEN int_debit_type=7 THEN INITCAP(coad.vchr_acc_name) END as vchr_debit_name,
                                        CASE WHEN int_credit_type=1 THEN INITCAP(cdc.vchr_name) WHEN int_credit_type=2 THEN INITCAP(CONCAT (auc.first_name,' ',auc.last_name))
                                                            WHEN int_credit_type=3 THEN INITCAP(amc.vchr_category) WHEN int_credit_type=4 THEN INITCAP(spc.vchr_name) WHEN int_credit_type=5 THEN 'Cash A/C'
                                                            WHEN int_credit_type=6 THEN 'Bank A/C' WHEN int_credit_type=7 THEN INITCAP(coac.vchr_acc_name) END as vchr_credit_name,
                                        CASE WHEN int_debit_type=1 THEN 'Customer' WHEN int_debit_type=2 THEN 'Staff'
                                                            WHEN int_debit_type=3 THEN 'Expenses' WHEN int_debit_type=4 THEN 'Vendor' WHEN int_debit_type=5 THEN 'Cash A/C'
                                                            WHEN int_debit_type=6 THEN 'Bank A/C' WHEN int_debit_type=7 THEN 'System a/c'  END as vchr_debit_type,
                                        CASE WHEN int_credit_type=1 THEN 'Customer' WHEN int_credit_type=2 THEN 'Staff'
                                                            WHEN int_credit_type=3 THEN 'Expenses' WHEN int_credit_type=4 THEN 'Vendor' WHEN int_credit_type=5 THEN 'Cash A/C'
                                                            WHEN int_credit_type=6 THEN 'Bank A/C' WHEN int_credit_type=7 THEN 'System a/c' END as vchr_credit_type
                                             FROM journal j join branch brd on j.fk_debit_branch_id=brd.pk_bint_id join branch brc on j.fk_credit_branch_id=brc.pk_bint_id  left outer join customer_details cdc on (int_credit_type =1 and cdc.pk_bint_id=j.fk_credit_id) left outer join customer_details cdd on (int_debit_type =1 and cdd.pk_bint_id=j.fk_debit_id)
                                             left outer join auth_user auc on (int_credit_type =2 and auc.id=j.fk_credit_id) left outer join auth_user aud on (int_debit_type =2 and aud.id=j.fk_debit_id)
                                             left outer join accounts_map amc on (int_credit_type =3 and amc.pk_bint_id=j.fk_credit_id) left outer join accounts_map amd on (int_debit_type =3 and amd.pk_bint_id=j.fk_debit_id)
                                             left outer join supplier spc on (int_credit_type =4 and spc.pk_bint_id=j.fk_credit_id) left outer join supplier spd on (int_debit_type =4 and spd.pk_bint_id=j.fk_debit_id)
                                             left outer join chart_of_accounts coac on (int_credit_type =7 and coac.pk_bint_id=j.fk_credit_id) left outer join chart_of_accounts coad on (int_debit_type =7 and coad.pk_bint_id=j.fk_debit_id)

                                               where dat_journal >= '"""+ request.data.get('datFrom') + """' and dat_journal <= '"""+request.data.get('datTo')+"""' order by -j.pk_bint_id) as subquery"""

            # str_query.format(filter = ' dat_journal >= '+ request.data.get('datFrom') + ' and dat_journal <= '+request.data.get('datTo'))
            # str_query=str_query.replace("""
            if request.user.userdetails.fk_group.vchr_name.upper()=='ADMIN':
                pass
            else:
                str_query +=  ' where fk_debit_branch_id ='+str(request.user.userdetails.fk_branch_id)+' or fk_credit_branch_id='+str(request.user.userdetails.fk_branch_id)
            # """,' ')
            rst_data = conn.execute(str_query).fetchall()


            return Response({'status':1,'lst_data':rst_data[0]['jsonb_agg']})

        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(exc, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':exc})
    def patch(self,request):
        try:
            dct_debit_select={1:""" select INITCAP(vchr_name) from customer_details where pk_bint_id=journal.fk_debit_id""",
                              2:""" select INITCAP(CONCAT(au.first_name,' ',au.last_name)) from auth_user au where au.id=journal.fk_debit_id""",
                              3:"""select INITCAP(vchr_category) from accounts_map where pk_bint_id=journal.fk_debit_id""",
                              4:"""select INITCAP(vchr_name) from supplier where pk_bint_id=journal.fk_debit_id""",
                              5:"""select 'CASH A/C'""",
                              6:"""select 'BANK A/C'""",
                              7:"""select INITCAP(vchr_acc_name) from chart_of_accounts where pk_bint_id=journal.fk_debit_id"""}

            dct_credit_select={1:""" select INITCAP(vchr_name) from customer_details where pk_bint_id=journal.fk_credit_id""",
                              2:""" select INITCAP(CONCAT(au.first_name,' ',au.last_name)) from auth_user au where au.id=journal.fk_credit_id""",
                              3:"""select INITCAP(vchr_category) from accounts_map where pk_bint_id=journal.fk_credit_id""",
                              4:"""select INITCAP(vchr_name) from supplier where pk_bint_id=journal.fk_credit_id""",
                              5:"""select 'CASH A/C'""",
                              6:"""select 'BANK A/C'""",
                              7:"""select INITCAP(vchr_acc_name) from chart_of_accounts where pk_bint_id=journal.fk_credit_id"""}

            int_debit_type=int(request.data.get('intDebitType'))
            int_credit_type=int(request.data.get('intCreditType'))

            lst_type_vchr=[None,'Customer','Staff','Expenses','Vendor','Cash A/C','Bank A/C','System A/C']
            ins_journal =Journal.objects.filter(pk_bint_id=request.data.get('intJournalId')).extra(select={'vchr_created_name':"select INITCAP(CONCAT(auth_user.first_name,' ',auth_user.last_name)) from auth_user where journal.fk_created_id=auth_user.id",'vchr_debit_name':dct_debit_select[int_debit_type],'vchr_credit_name':dct_credit_select[int_credit_type],'dat_journal_format':"TO_CHAR(dat_journal,'DD-MM-YYYY')"})\
            .values('vchr_debit_name','vchr_credit_name','vchr_created_name','vchr_remarks','dbl_amount','fk_debit_branch_id__vchr_name','fk_credit_branch_id__vchr_name','vchr_jv_num','dat_journal_format').first()
            ins_journal['vchr_debit_type']=lst_type_vchr[int_debit_type]
            ins_journal['vchr_credit_type']=lst_type_vchr[int_credit_type]
            return Response({'status':1,'dct_data':ins_journal})

        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(exc, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':exc})
