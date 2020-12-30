"""
    commented lines are not purely functioning
    uncommented lines are fully functioning
"""

from vendorCustomerExpense import vendorExpense
from advanceOrDepositRefund import AdvanceRefundMethod # inbound
from ang_stock_transfer_with_apinvoice_api import purchase_invoice_api # inbound
from ang_stock_transfer_with_bill_api import bill_api_call # inbound
from ang_stock_transfer_with_creditmemo_api import return_api_call # inbound
from ang_stock_transfer_with_salesreturn_api import purchase_return_api # inbound
from discountJournal import discountJournal # inbound
from expenseToSap import expense_to_sap  # inbound
from mygoalAdvanceToSap import advance_to_sap # inbound
from mygoalBillsToSap import bills_to_sap # inbound
from salesReturn import sales_return_to_sale # inbound
from stock_transfer_api_ import stock_transfer_api # inbound
from grpo import GRPO_sapre_part
from datetime import datetime,time,timedelta
import time as t
import os

from sqlalchemy import create_engine
import sys


date = datetime.strftime(datetime.now(),'%Y-%m-%d')

def is_time_between(begin_time, end_time, check_time=None):
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:
        return check_time >= begin_time or check_time <= end_time

def integration_calls(doc_date):
    grpo_purchase,stock_transfer_api2,stock_transfer_api1,purchase_invoice_api2,purchase_invoice_api1,bill_api_call2,bill_api_call1,return_api_call2,return_api_call1,purchase_return_api2,purchase_return_api1,advance_to_sap2,advance_to_sap1,AdvanceRefundMethod2,AdvanceRefundMethod1,bills_to_sap2,bills_to_sap1,discountJournal2,discountJournal1,sales_return_to_sale2,sales_return_to_sale1,expense_to_sap2,expense_to_sap1,vendorExpense1,vendorExpense2 = False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False

    #doc_date1 = datetime.strftime(datetime. strptime(doc_date,'%Y-%m-%d') - timedelta(days=1),'%Y-%m-%d')
    doc_date1 = doc_date
    print("\n-----------------------------------------------------------grpo purchase-----------------------------------------------\n")
    
    while not  grpo_purchase:
        grpo_purchase = GRPO_sapre_part('-1,1,-2,0',doc_date)
    
    print("\n-----------------------------------------------------------stock transfer-----------------------------------------------\n")
    
    while not  stock_transfer_api1:
        stock_transfer_api1 = stock_transfer_api("0,1,-1,-2",doc_date)
    print("\n-----------------------------------------------------------ang_stock_transfer_with_bill_api---------------------------------------")
    #while not  bill_api_call2:
     #   bill_api_call2 = bill_api_call("-1,-2",doc_date1)
    while not  bill_api_call1:
        bill_api_call1 = bill_api_call("0,1,-1,-2",doc_date)
    print("\n-----------------------------------------------------------ang_stock_transfer_with_apiinvoice_api-----------------------------------------------\n")
  #  while not  purchase_invoice_api2:
   #     purchase_invoice_api2 = purchase_invoice_api('-1,-2',doc_date1)
    while not  purchase_invoice_api1:
        purchase_invoice_api1 = purchase_invoice_api("0,1,-1,-2",doc_date)
    print("\n-----------------------------------------------------------ang_stock_transfer_with_creditmemo_api-----------------------------------------------\n")
    
   # while not  return_api_call2:
    #    return_api_call2 = return_api_call("-1,-2",doc_date1)
    while not  return_api_call1:
        return_api_call1 = return_api_call("-1,-2,0,1",doc_date)
    print("\n-----------------------------------------------------------ang_stock_transfer_with_salesreturn_api-----------------------------------------------\n")
    #while not  purchase_return_api2:
     #   purchase_return_api2 = purchase_return_api("-1,-2",doc_date1)
    while not  purchase_return_api1:
        purchase_return_api1 = purchase_return_api("-1,-2,0,1",doc_date)
    print("\n-----------------------------------------------------------advance to sap-----------------------------------------------\n")
    
    #while not  advance_to_sap2:
     #   advance_to_sap2 = advance_to_sap("-1,-2,0,1",doc_date1)
    while not  advance_to_sap1:
        advance_to_sap1 = advance_to_sap("-1,-2,0,1",doc_date)
    print("\n-----------------------------------------------------------advance refund-----------------------------------------------\n")
    
    #while not  AdvanceRefundMethod2:
     #   AdvanceRefundMethod2 = AdvanceRefundMethod("-1,-2",doc_date1)
    while not  AdvanceRefundMethod1:
        AdvanceRefundMethod1 = AdvanceRefundMethod("-2,-1,0,1",doc_date)
    
    print("\n-----------------------------------------------------------Customer Vendor Expense-----------------------------------------------\n")
   # while not  vendorExpense2:
    #    vendorExpense2 = vendorExpense("-1,-2",doc_date1)
    while not  vendorExpense1:
        vendorExpense1 = vendorExpense("-2,-1,0,1",doc_date)
    #print("\n-----------------------------------------------------------bills to sap-----------------------------------------------\n")
    
    #while not  bills_to_sap2:
     #   bills_to_sap2 = bills_to_sap("-2,-1",doc_date1)
    while not  bills_to_sap1:
        bills_to_sap1 = bills_to_sap("-2,-1,0,1",doc_date)
    
    print("\n-----------------------------------------------------------discount journal-----------------------------------------------\n")
    #while not  discountJournal2:
     #   discountJournal2 = discountJournal("-1,-2",doc_date1)
    while not  discountJournal1:
        discountJournal1 = discountJournal("0,1,-1,-2",doc_date)
    print("\n-----------------------------------------------------------sales return-----------------------------------------------\n")
    
    #while not  sales_return_to_sale2:
     #   sales_return_to_sale2 = sales_return_to_sale("-1,-2",doc_date1)
    while not  sales_return_to_sale1:
        sales_return_to_sale1 = sales_return_to_sale("0,1,-1,-2",doc_date)
    print("\n-----------------------------------------------------------expense to sap-----------------------------------------------\n")
    
    #while not  expense_to_sap2:
     #   expense_to_sap2 = expense_to_sap("-1,-2",doc_date1)
    while not  expense_to_sap1:
        expense_to_sap1 = expense_to_sap("-1,-2,0,1",doc_date)
    
    print("Integration Finished ")

while True:
#    dat_integration = '2020-11-05'
    dat_integration = datetime.strftime(datetime.now(),'%Y-%m-%d')
    date_file = dat_integration.replace("-","")
    if not os.path.exists(date_file):
        os.mkdir(date_file)
    lst_log =['CustomerRefundIssues.txt','APinvoiceIssues.txt','Ang_BillsIssues.txt','CreditMemoIssues.txt','AngSalesReturnIssues.txt','DiscountJournalIssues.txt','ExpenseIssues.txt','ReceiptsIssues.txt','BillsIssues.txt','SalesReturnIssues.txt','STockTransferIssues.txt','Grpo.txt']
    for str_file in lst_log:
        file_object = open(date_file+"/"+str_file, 'w')
        file_object.close()
    integration_calls(dat_integration)
    integration_calls(dat_integration)
    exit()

