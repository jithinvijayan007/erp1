from transaction.models import Transaction
from payment.models import Payment
from branch.models import Branch
from userdetails.models import Userdetails,Financiers
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


# from aldjemy.core import get_engine
str_exception=''

"""Main Function"""
def transaction_posting():
    try:
        dat_start = datetime(2020,7,6)
        dat_end = datetime(2020,7,7)
        dat_today = datetime.today()
        f= open('posting_issues.txt','w')
        f.write('Start time :'+str(datetime.now()))
        ins_sales = list(SalesDetails.objects.filter(fk_master__dat_created__gte=dat_start,fk_master__dat_created__lte=dat_end,fk_master__int_doc_status=1).exclude(int_sales_status=0).values('fk_master_id'))
        lst_id = [ item['fk_master_id'] for item in ins_sales ]
        lst_id = list(set(lst_id))
        int_issue=0
        for int_id in lst_id:
            try:
                ins_trans = Transaction.objects.filter(int_document_type=3,int_document_id=int_id).values('pk_bint_id')
                lst_trans_id = [ item['pk_bint_id'] for item in ins_trans ]
                dct_return_value = create_invoice_posting_data(int_id)
                if dct_return_value['status'] == 0:
                    int_issue += 1
                    str_issue = '\nError in transaction('+dct_return_value['reason']+') SalesMasterID -'+str(int_id) +' '+ str(datetime.now())
                    # with open('posting_issues.txt','a') as f:
                    f.write(str_issue)
                elif dct_return_value['status'] == 2:
                    int_issue += 1
                    str_issue = '\nCredit and Debit not balanced in transaction SalesMasterID -'+str(int_id) +' '+ str(datetime.now())
                    # with open('posting_issues.txt','a') as f:
                    f.write(str_issue)
                else:
                    Transaction.objects.filter(pk_bint_id__in=lst_trans_id).delete()
            except Exception as e:
                with open('posting_issues.txt','a') as f:
                    f.write('Error in Loop'+str(e))
                continue
        f.write('\nTotal Documents:'+str(len(lst_id)))
        f.write('\nDocuments that have issues:'+str(int_issue))
        f.write('\nEnd time :'+str(datetime.now()))
        f.close()
    except Exception as e:
        with open('posting_issues.txt','a') as f:
            f.write('Error in Main Function'+str(e))
        # raise ValueError('Error in Main Function')
        return 0


"""Creating Invoice Posting Data's"""
def create_invoice_posting_data(pk_bint_id):
    try:
        with transaction.atomic():
            lst_data = []
            ins_branch_data = None
            ins_sales_detail = SalesDetails.objects.filter(fk_master_id=pk_bint_id).aggregate(dbl_indirect_discount =Sum('dbl_indirect_discount'))
            ins_sales_master = SalesMaster.objects.filter(pk_bint_id = pk_bint_id).values('fk_customer__fk_customer_id','dbl_total_amt','dbl_total_tax','fk_branch_id','fk_created_id','json_tax','jsn_addition','jsn_deduction','dat_created').first()
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
                dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
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
                dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
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
                dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
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
            dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
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
                    dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
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
            dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
            dbl_sale_amt += dct_data['CREDIT']
            lst_data.append(dct_data)
            # round-off total amount
            dbl_sale_amt = round((dbl_sale_amt + dbl_addition - dbl_deduction - dbl_indirect_discount),2)
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
                dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
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
                dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
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
                    dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
                    dbl_cust_credit_amount+=dct_data['DEBIT']
                    lst_data.append(dct_data)
                # for down payment in the case of finance --starts
                if data['int_fop'] not in [4]:
                    dct_data = {}
                    if data['int_fop'] in [0] and data['dbl_receved_amt']!=0:
                        ins_finance = FinanceDetails.objects.filter(fk_payment=data['pk_bint_id']).values('dbl_service_amt','dbl_processing_fee','dbl_dbd_amt').first()
                        dbl_fin_charge=data['dbl_receved_amt']
                        dbl_fin_charge += ins_finance['dbl_service_amt'] if ins_finance['dbl_service_amt'] else 0
                        dbl_fin_charge += ins_finance['dbl_processing_fee'] if ins_finance['dbl_processing_fee'] else 0
                        dbl_fin_charge += ins_finance['dbl_dbd_amt'] if ins_finance['dbl_dbd_amt'] else 0
                        dct_data['ACCOUNT_TYPE']  = 3
                        dct_data['ACCOUNT_ID'] = ChartOfAccounts.objects.filter(vchr_acc_code='FINANCE_CHARGES').values('pk_bint_id').first()['pk_bint_id']
                        dct_data['CREDIT']  = dbl_fin_charge
                        dct_data['DEBIT']  = 0
                        dct_data['DOCUMENT_ID'] = pk_bint_id
                        dct_data['DOCUMENT_TYPE'] = 3
                        dct_data['USER_CREATED'] = ins_sales_master['fk_created_id']
                        dct_data['BRANCH_ID'] = ins_sales_master['fk_branch_id']
                        dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
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
                dct_data['DATE_CREATED'] = ins_sales_master['dat_created']
                lst_data.append(dct_data)
            # dbl_credit_sum=0
            # dbl_debit_sum=0
            # for item in lst_data:
            #     dbl_credit_sum+=item['CREDIT']
            #     print('credit',item['CREDIT'],dbl_credit_sum)
            #     dbl_debit_sum+=item['DEBIT']
            #     print('debit',item['DEBIT'],dbl_debit_sum)
            # print(dbl_credit_sum)
            # print(dbl_debit_sum)
            return(create_transaction_posting(lst_data))
    except Exception as e:
        return {'status':0,'reason':str(e)}



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
            # print(credit,debit)
            if round(credit,2) != round(debit,2):
                print('issues',round(credit,2),round(debit,2))
                return {'status':2}
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
                return {'status':0,'reason':'No Data'}
            else:
                return {'status':1}
    except Exception as e:
        return {'status':0,'reason':str(e)}
