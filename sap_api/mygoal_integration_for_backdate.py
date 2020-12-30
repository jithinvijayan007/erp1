"""
    commented lines are not purely functioning
    uncommented lines are fully functioning
"""

from location_master import location_master # out bound
from showRoomMaster import ShowRoomDataFromSap # out bound Date
from brandCostcenter import pricelistfromsap as CostCenters # out bound Date
from freightfromSap import freightDate # out bound
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

from datetime import datetime,time,timedelta
import time as t

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
    stock_transfer_api2,stock_transfer_api1,purchase_invoice_api2,purchase_invoice_api1,bill_api_call2,bill_api_call1,return_api_call2,return_api_call1,purchase_return_api2,purchase_return_api1,advance_to_sap2,advance_to_sap1,AdvanceRefundMethod2,AdvanceRefundMethod1,bills_to_sap2,bills_to_sap1,discountJournal2,discountJournal1,sales_return_to_sale2,sales_return_to_sale1,expense_to_sap2,expense_to_sap1,vendorExpense1,vendorExpense2 = False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False

    doc_date1 = datetime.strftime(datetime. strptime(doc_date,'%Y-%m-%d') - timedelta(days=1),'%Y-%m-%d')
    doc_date1 = doc_date
    print("\n-----------------------------------------------------------stock transfer-----------------------------------------------\n")
    while not  stock_transfer_api2:
        stock_transfer_api2 = stock_transfer_api('-1,-2',doc_date1)
    while not  stock_transfer_api1:
        stock_transfer_api1 = stock_transfer_api("0,1,-1,-2",doc_date)
    print("\n-----------------------------------------------------------ang_stock_transfer_with_apiinvoice_api-----------------------------------------------\n")
    while not  purchase_invoice_api2:
        purchase_invoice_api2 = purchase_invoice_api('-1,-2',doc_date1)
    while not  purchase_invoice_api1:
        purchase_invoice_api1 = purchase_invoice_api("-1,-2,0,1",doc_date)
    print("\n-----------------------------------------------------------ang_stock_transfer_with_bill_api-----------------------------------------------\n")
    while not  bill_api_call2:
        bill_api_call2 = bill_api_call("-1,-2",doc_date1)
    while not  bill_api_call1:
        bill_api_call1 = bill_api_call("0,1,-1,-2",doc_date)
    print("\n-----------------------------------------------------------ang_stock_transfer_with_creditmemo_api-----------------------------------------------\n")
    while not  return_api_call2:
        return_api_call2 = return_api_call("-1,-2",doc_date1)
    while not  return_api_call1:
        return_api_call1 = return_api_call("-1,-2,0,1",doc_date)
    print("\n-----------------------------------------------------------ang_stock_transfer_with_salesreturn_api-----------------------------------------------\n")
    while not  purchase_return_api2:
        purchase_return_api2 = purchase_return_api("-1,-2",doc_date1)
    while not  purchase_return_api1:
        purchase_return_api1 = purchase_return_api("-1,-2,0,1",doc_date)
    print("\n-----------------------------------------------------------advance to sap-----------------------------------------------\n")
    while not  advance_to_sap2:
        advance_to_sap2 = advance_to_sap("-1,-2",doc_date1)
    while not  advance_to_sap1:
        advance_to_sap1 = advance_to_sap("-1,-2,0,1",doc_date)
    print("\n-----------------------------------------------------------advance refund-----------------------------------------------\n")
    while not  AdvanceRefundMethod2:
        AdvanceRefundMethod2 = AdvanceRefundMethod("-1",doc_date1)
    while not  AdvanceRefundMethod1:
        AdvanceRefundMethod1 = AdvanceRefundMethod("-2,-1,0,1",doc_date)
    
    print("\n-----------------------------------------------------------Customer Vendor Expense-----------------------------------------------\n")
    while not  vendorExpense2:
        vendorExpense2 = vendorExpense("-1",doc_date1)
    while not  vendorExpense1:
        vendorExpense1 = vendorExpense("-2,-1,0,1",doc_date)
    print("\n-----------------------------------------------------------bills to sap-----------------------------------------------\n")
    while not  bills_to_sap2:
        bills_to_sap2 = bills_to_sap("-1,-2",doc_date1)
    while not  bills_to_sap1:
        bills_to_sap1 = bills_to_sap("0,1,-2,-1",doc_date)
    print("\n-----------------------------------------------------------discount journal-----------------------------------------------\n")
    while not  discountJournal2:
        discountJournal2 = discountJournal("-1,-2",doc_date1)
    while not  discountJournal1:
        discountJournal1 = discountJournal("0,1,-1,-2",doc_date)
    print("\n-----------------------------------------------------------sales return-----------------------------------------------\n")
    while not  sales_return_to_sale2:
        sales_return_to_sale2 = sales_return_to_sale("-1,-2",doc_date1)
    while not  sales_return_to_sale1:
        sales_return_to_sale1 = sales_return_to_sale("0,1,-1,-2",doc_date)
    print("\n-----------------------------------------------------------expense to sap-----------------------------------------------\n")
    while not  expense_to_sap2:
        expense_to_sap2 = expense_to_sap("-1",doc_date1)
    while not  expense_to_sap1:
        expense_to_sap1 = expense_to_sap("0,1",doc_date)
    print("Integration Finished ")

while True:
    #lst_date=['2020-07-01','2020-07-02', '2020-07-03', '2020-07-04', '2020-07-05', '2020-07-06','2020-07-07', '2020-07-08', '2020-07-09', '2020-07-10']  #, '2020-06-11', '2020-06-12', '2020-06-13', '2020-06-14', '2020-06-15', '2020-06-16', '2020-06-17', '2020-06-18', '2020-06-19', '2020-06-20', '2020-06-21', '2020-06-22', '2020-06-23', '2020-06-24'] #, '2020-06-25', '2020-06-26', '2020-06-27', '2020-06-28', '2020-06-29', '2020-06-30']
    lst_date=['2020-07-05', '2020-07-06','2020-07-07', '2020-07-08', '2020-07-09','2020-07-10']
    #lst_date=[]
    for doc_date in lst_date:
        print(doc_date)
        integration_calls(doc_date)
#    integration_calls(datetime.strftime(datetime.now(),'%Y-%m-%d'))
    exit()
