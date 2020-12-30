from django.shortcuts import render
# Create your views here.
from products.models import Products
from category.models import Category
from item_category.models import Item
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.serializers import ModelSerializer,FileField
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import F,Value
from django.db.models.functions import Concat
from rest_framework.parsers import MultiPartParser,FileUploadParser
from django.db.models.functions import Upper
from datetime import datetime, timedelta,date
import xlrd
from django.conf import settings
from sap_api.models import ChartOfAccounts
import pandas as pd
from userdetails.models import Userdetails
from branch.models import Branch
from POS.dftosql import Savedftosql
cell_value = ''
from ledger_details.models import OpeningBalance,ImportFiles
from transaction.models import Transaction

def ob_ledger_data():

    df = pd.read_excel('cash_ob.xlsx',header=0)
    lst_query = []
    for ind,row in df.iterrows():
        ins_trns = Transaction(
            dat_created=datetime.now(),
            int_account_type=3,
            dbl_debit= row['DR'],
            dbl_credit=row['CR'],
            int_document_id=0,
            int_document_type=10,
            fk_created_id=Userdetails.objects.filter(fk_group__vchr_name='ADMIN').values('user_ptr_id')[0]['user_ptr_id'],
            vchr_status ='N',
            fk_financialyear_id=1,
            fk_branch_id=Branch.objects.get(vchr_code=row['BRANCH CODE']).pk_bint_id,
            int_accounts_id=ChartOfAccounts.objects.get(vchr_acc_code=row['SAP CODE']).pk_bint_id,
            int_type = 1
        )
        lst_query.append(ins_trns)
    if lst_query:
        Transaction.objects.bulk_create(lst_query)
    return 'Success'

def products():
    df = pd.read_excel('Productissue.xlsx',header=0)
    df = df.fillna(False)
    df['vchr_name'] = df['Product']
    df['vchr_item_code'] = df['Item Code']
    df['fk_financial_id'] = df['Category']

    uploadcolumns = ['vchr_acc_no','fk_financial_id','vchr_acc_name','dbl_debit_amount','dbl_credit_amount']
    xlsdf = Savedftosql(df[uploadcolumns],'opening_balance')
    xlsdf.insert_data()


    return 'Success'


def opening_stock_data():
    df = pd.read_excel('Stock Opening.xlsx',header=0)
    df = df.fillna(False)
    df['vchr_acc_no'] = df['Account Code']
    df['vchr_acc_name'] = df['Account Name']
    df['fk_financial_id'] = None
    df['dbl_debit_amount'] = 0
    df['dbl_credit_amount'] = 0
    uploadcolumns = ['vchr_acc_no','fk_financial_id','vchr_acc_name','dbl_debit_amount','dbl_credit_amount']
    xlsdf = Savedftosql(df[uploadcolumns],'opening_balance')
    xlsdf.insert_data()
    return 'Success'

def open_brs_data():
    df = pd.read_excel('Open BRS Template.xlsx',header=0)
    df = df.fillna(False)
    df['vchr_acc_no'] = df['Account Code']
    df['vchr_acc_name'] = df['Account Name']
    df['fk_financial_id'] = None
    df['dbl_debit_amount'] = 0
    df['dbl_credit_amount'] = 0
    uploadcolumns = ['vchr_acc_no','fk_financial_id','vchr_acc_name','dbl_debit_amount','dbl_credit_amount']
    xlsdf = Savedftosql(df[uploadcolumns],'opening_balance')
    xlsdf.insert_data()
    return 'Success'


def customer_vendor_balance():
    df = pd.read_excel('Customer_Vendor Opening Balance Template.xlsx',header=0)
    df = df.fillna(False)
    df['vchr_acc_no'] = df['Account Code']
    df['vchr_acc_name'] = df['Account Name']
    df['fk_financial_id'] = None
    df['dbl_debit_amount'] = 0
    df['dbl_credit_amount'] = 0
    uploadcolumns = ['vchr_acc_no','fk_financial_id','vchr_acc_name','dbl_debit_amount','dbl_credit_amount']
    xlsdf = Savedftosql(df[uploadcolumns],'opening_balance')
    xlsdf.insert_data()
    return 'Success'

def fixed_asset_balance():
    df = pd.read_excel('Fixed Asset - Opening Balance Template.xlsx',header=0)
    df = df.fillna(False)
    df['vchr_acc_no'] = df['Account Code']
    df['vchr_acc_name'] = df['Account Name']
    df['fk_financial_id'] = None
    df['dbl_debit_amount'] = 0
    df['dbl_credit_amount'] = 0
    uploadcolumns = ['vchr_acc_no','fk_financial_id','vchr_acc_name','dbl_debit_amount','dbl_credit_amount']
    xlsdf = Savedftosql(df[uploadcolumns],'opening_balance')
    xlsdf.insert_data()
    return 'Success'
