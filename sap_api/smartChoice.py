import requests
import json
import urllib.request
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import os
from sqlalchemy import create_engine
from django.http import JsonResponse
import simplejson as json
from bs4 import BeautifulSoup
import sys

def smart_choice_to_pos(lst_smt_chc,str_entry,doc_date):
    """
    Used to push mygoal pos sales data to SAP
    paramerters(to SAP):
            Master data :- MYGOAL_KEY,ShowRoomID,CardCode,CardName,DocDate,DocNum,Type
            Sub details :- ItemCode,Quantity,Amount,TaxCode,Costcenter,MnfSerial,LocCode
    response(from SAP):suceess/failed
    """
    try:
        try:
            # db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/pos_sap"
            db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/myg_pos_live2"

            conn = create_engine(db_connetion_string)
        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})
        try:
#            import pdb; pdb.set_trace()
            rst_freight = conn.execute("select array_agg(vchr_category||':'||vchr_code) from freight").fetchall()[0][0]
            dct_freight_data = {str_freight.split(':')[0]:str_freight.split(':')[1] for str_freight in rst_freight}
            for str_id in lst_smt_chc:
                try:
                    str_id=str(str_id)
                    # import pdb; pdb.set_trace()
                    # Query to get sales data
                    # str_query_data = "select sm.int_sale_type,sm.pk_bint_id as sales_id,sm.jsn_deduction as deduction,pd.vchr_name as product,bd.vchr_code as brand,sm.jsn_addition as addition,sd.dbl_buyback as buyback,br.vchr_code as showroom_code,br.fk_states_id as branch_state_id,br.pk_bint_id as sh_id,cust.int_cust_type as cust_type,cust.vchr_name as card_name,cust.vchr_gst_no as gst_no,cust.vchr_code as card_code,cust.int_mobile as cust_mobile,cust.pk_bint_id as cust_id,cust.fk_state_id as cust_state_id,cust.txt_address as cust_address,st.vchr_code as state_code,sm.dat_invoice as doc_date,sm.vchr_invoice_num as doc_num,it.vchr_item_code as item_code,it.pk_bint_id as item_id,itc.json_tax_master as tax,lm.int_code as loc_code,sd.int_qty as quantity,sd.int_sales_status as sale_status,sd.dbl_discount as discount,(sd.dbl_amount-sd.dbl_discount) as amount,sd.json_imei as mnf_serial,sd.vchr_batch batch_no,sd.dbl_tax as tax_amount from sales_master sm join sales_details sd on sm.pk_bint_id=sd.fk_master_id join branch br on br.pk_bint_id=sm.fk_branch_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sales_customer_details cust on cust.pk_bint_id = sm.fk_customer_id join states st on st.pk_bint_id=cust.fk_state_id join item it on it.pk_bint_id = sd.fk_item_id join brands bd on bd.pk_bint_id=it.fk_brand_id join products pd on pd.pk_bint_id=it.fk_product_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join sap_api_track sap on sap.int_document_id = sm.pk_bint_id and sap.int_type=1 where sm.pk_bint_id = "+str_id+";"
                    str_query_data = "select sm.int_sale_type,sm.pk_bint_id as sales_id,sm.jsn_deduction as deduction,pd.vchr_name as product,bd.vchr_code as brand,sm.jsn_addition as addition,sd.dbl_buyback as buyback,br.vchr_code as showroom_code,br.fk_states_id as branch_state_id,br.pk_bint_id as sh_id,cust.int_cust_type as cust_type,cust.vchr_name as card_name,cust.vchr_gst_no as gst_no,cust.vchr_code as card_code,cust.int_mobile as cust_mobile,cust.pk_bint_id as cust_id,cust.fk_state_id as cust_state_id,cust.txt_address as cust_address,st.vchr_code as state_code,sm.dat_invoice as doc_date,sm.vchr_invoice_num as doc_num,it.vchr_item_code as item_code,it.pk_bint_id as item_id,itc.json_tax_master as tax,lm.int_code as loc_code,sd.int_qty as quantity,sd.int_sales_status as sale_status,sd.dbl_discount as discount,(sd.dbl_selling_price) as amount,sd.json_imei as mnf_serial,sd.vchr_batch batch_no,sd.dbl_tax as tax_amount from sales_master sm join sales_details sd on sm.pk_bint_id=sd.fk_master_id join branch br on br.pk_bint_id=sm.fk_branch_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sales_customer_details cust on cust.pk_bint_id = sm.fk_customer_id join states st on st.pk_bint_id=cust.fk_state_id join item it on it.pk_bint_id = sd.fk_item_id join brands bd on bd.pk_bint_id=it.fk_brand_id join products pd on pd.pk_bint_id=it.fk_product_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join products pr on pr.pk_bint_id=it.fk_product_id join sap_api_track sap on sap.int_document_id = sm.pk_bint_id and sap.int_type=1 where sm.pk_bint_id = "+str_id+";"
                    rst_sales_data = conn.execute(str_query_data).fetchall()
                    if not rst_sales_data:
                        continue
                    # Query to get payment details
                    str_payment_data = "select sm.pk_bint_id as sales_id,br.pk_bint_id as sh_id,br.vchr_code as showroom_code,pd.vchr_name as fin_code,pd.vchr_reff_number as tr_id,pd.dbl_receved_amt as amount,pd.int_fop as fop,pd.vchr_card_number as card_num,pd.fk_bank_id as bank_id,pd.dat_created_at::DATE as transfer_date,case when pd.int_fop =0 then 'Financier-Payment' when pd.int_fop =1 then 'Cash' when pd.int_fop =2 then 'Debit Card' when pd.int_fop =3 then 'Credit Card' when pd.int_fop =5 then 'PAYTM' when pd.int_fop =6 then 'PAYTM MALL' when pd.int_fop =7 then 'Bharath QR' else 'Cheque' end as payment_mode from sales_master sm join payment_details pd on sm.pk_bint_id=pd.fk_sales_master_id join branch br on br.pk_bint_id=sm.fk_branch_id join sap_api_track sap on sap.int_document_id = sm.pk_bint_id and sap.int_type=1 where pd.int_fop!=4 and pd.fk_sales_master_id = "+str_id+";"
                    rst_payment_details = conn.execute(str_payment_data).fetchall()

                    # Query to get advance receipt data
                    str_advance_data = "select rim.fk_sales_master_id as sale_id,rc.int_fop as fop,rc.vchr_sap_key,rim.dbl_amount from receipt_invoice_matching rim join receipt rc on rim.fk_receipt_id = rc.pk_bint_id where int_pstatus = 0 and int_receipt_type in (1,2) and rc.vchr_sap_key !='404' and rim.fk_sales_master_id="+str_id+";"
                    rst_advance_details = conn.execute(str_advance_data).fetchall()

                    # Query to get bank details
                    str_bank_data = "select array_agg(pk_bint_id||':' ||vchr_name) from bank;"
                    rst_bank_details = conn.execute(str_bank_data).fetchall()[0][0]
                    # create dictionary of bank and pk_bint_id
                    dct_bank = {str_bank.split(':')[0]:str_bank.split(':')[1] for str_bank in rst_bank_details}

                    str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
                    rst_tax_details = conn.execute(str_tax_master).fetchall()[0][0]

                    str_account_code = "select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id where acm.int_status=0 and acm.fk_branch_id {} and acm.vchr_category = '{}';"

                    dct_tax = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in rst_tax_details}
                    conn.execute("update sales_master SET jsn_deduction=jsn_deduction-'162' where (jsn_deduction->>'162')::numeric= 0")
                    conn.execute("update sales_master SET jsn_deduction=jsn_deduction-'118' where (jsn_deduction->>'118')::numeric= 0")
                    if not rst_sales_data:
                        print('No data found')
                        return

                    dct_data = {}
                    dct_data['Header'] = []
                    dct_data['Purchase Line level'] = []
                    dct_data['Invoice'] = []
                    dct_data['Invoice Line level'] = []
                    dct_data['Invoice Payment Level'] = []
                    dct_data['Invoice Freight'] = []
                    dct_header = {}
                    dct_freight_discount={}
                    dct_freight_buyback={}
                    dct_pur_header = {}
                    bln_kfc = False
                    bln_igst = False
                    str_fin_code = None
                    for ins_data in rst_sales_data:
                        ins_data = dict(ins_data)
                        if ins_data['sale_status'] == 1:
                            if 'MYGOAL_KEY' not in dct_header:

            # ===================================Header Data ===========================================================
                                if ins_data['branch_state_id'] != ins_data['cust_state_id']:
                                    bln_igst = True
                                elif not ins_data['gst_no']:
                                    bln_kfc = True
                                if ins_data['int_sale_type'] == 2:
                                    card_code = 'AMAZONE'
                                    card_name = 'Amazon Customer'
                                elif ins_data['int_sale_type'] == 3:
                                    card_code = 'FLIPKART'
                                    card_name = 'Flipkart Customer'
                                elif ins_data['int_sale_type'] == 4:
                                    card_code = 'E-COMMERCE'
                                    card_name = 'E-commerce Customer'
                                elif ins_data['card_code']:
                                    card_code = ins_data['card_code']
                                    card_name = ins_data['card_name']
                                else:
                                    card_code = "EXCG_Customer"
                                    card_name = "Exchange Customer"

                                dct_header['MYGOAL_KEY'] = ins_data['doc_num']
                                dct_header['ShowRoomID'] = ins_data['showroom_code']
                                dct_header['CardCode'] = card_code #"EXCG_Customer" if not ins_data['card_code'] else ins_data['card_code']
                                dct_header['CardName'] = card_name #"Exchange Customer" if not ins_data['card_code'] else ins_data['card_name']
                                #dct_header['BranchID'] = 1
                                dct_header['CustomerName'] = ins_data['card_name']
                                dct_header['MobileNumber'] = ins_data['cust_mobile']
                                dct_header["BillTo"]= ins_data['state_code'] if ins_data['state_code'] else 'KL'
                                dct_header["ShipTo"]= ins_data['state_code'] if ins_data['state_code'] else 'KL'
                                dct_header["CustAddr"]= ins_data['cust_address']

                                dct_header['DealID'] = ""
                                dct_header['Financier'] = ""
                                dct_header['DocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                                dct_header['BpGSTN'] = ins_data['gst_no']
                                jsn_addition = ins_data['addition']
                                jsn_deduction = ins_data['deduction']
                                dbl_buyback = ins_data['buyback']


                                dct_data['Invoice'].append(dct_header)

            # ====================================Line Data==================================================================================
#                            import pdb; pdb.set_trace()
                            dct_line_data = {}
                            dct_line_data['ItemCode'] = ins_data['item_code']
                            dct_line_data['Quantity'] = ins_data['quantity']
                            dct_line_data['WhsCode'] = ins_data['showroom_code']
                            # dct_line_data['Amount'] = round(ins_data['amount'],2)
                            dct_line_data['DiscAmnt'] = ins_data['discount'] if ins_data['discount'] else 0
                            json_tax = ins_data['tax']
                            dbl_tax=0
                            dbl_tax_to_check=0
                            if json_tax and ins_data.get('cust_type') !=3:
                                if bln_igst:
                                    json_tax.pop(dct_tax['CGST'],'')
                                    json_tax.pop(dct_tax['SGST'],'')
                                    dbl_tax = json_tax[dct_tax['IGST']]
                                    dbl_tax_to_check= json_tax[dct_tax['IGST']]
                                elif bln_kfc:
                                    json_tax.pop(dct_tax['IGST'],'')
                                    json_tax[dct_tax['KFC']] = 1
                                    dbl_tax = json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]+1
                                    dbl_tax_to_check= json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                                else:
                                    json_tax.pop(dct_tax['IGST'],'')
                                    dbl_tax_to_check= json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                                    dbl_tax = json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]

                                str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                                rst_tax_code = conn.execute(str_tax_code).fetchall()[0][0]
                            else:
                                #if bln_igst:
                                rst_tax_code ='IGST0'
                                #else:
                                #rst_tax_code = 'GST0'

                            dct_line_data['Amount'] = round((ins_data['amount']+ins_data['discount']+ins_data['buyback'])/((100+dbl_tax)/100),2)
                            if ins_data['product'].upper()=='RECHARGE' or ins_data['item_code'] in ['GDC00001','GDC00002']:
                                dct_line_data['Quantity'],dct_line_data['Amount'] = dct_line_data['Amount'],dct_line_data['Quantity'] 
                            dct_line_data['TaxCode'] = rst_tax_code if rst_tax_code != 'GST0K' else 'GST0'
                            dct_line_data['Store'] = ins_data['showroom_code']
                            dct_line_data['Department'] = 'SAL'
                            if(ins_data['brand']== None):
                                dct_line_data['Brand'] = ""
                            else:
                                dct_line_data['Brand'] = ins_data['brand'].upper().replace(" ", "") if ins_data['brand'].upper() != 'MYG' else 'myG'
                            dct_line_data['Employee'] = ""
                            if ins_data['mnf_serial']:#Item with imei number
                                dct_line_data['MnfSerial'] = ins_data['mnf_serial']
                            else:#Item with serial number
                                dct_line_data['MnfSerial'] = ins_data['batch_no']
                            if ins_data['product'].upper() in ['SERVICE','SIM','RECHARGE','CARE PLUS']:
                                dct_line_data['MnfSerial'] = []
                            dct_line_data['LocCode'] = ins_data['loc_code']
                            dct_line_data['SalesDiscount'] = ins_data['discount'] if ins_data['discount'] else 0
                            dct_line_data['BuyBack'] = ins_data['buyback'] if ins_data['buyback'] else 0
                            if dbl_tax_to_check and (dbl_tax_to_check%1) ==0:
                               dbl_tax_to_check = int(dbl_tax_to_check)
                            if ins_data['discount'] and rst_tax_code not in dct_freight_discount:
                                dct_freight_discount[rst_tax_code] = {}
                                dct_freight_discount[rst_tax_code]['tax_code'] = str(dbl_tax_to_check) if dbl_tax_to_check==0 or dbl_tax_to_check>10 else '0'+str(dbl_tax_to_check)
                                dct_freight_discount[rst_tax_code]['amount'] = round(ins_data['discount']/((100+dbl_tax)/100),3)
                            elif ins_data['discount']:
                                dct_freight_discount[rst_tax_code]['amount'] += round(ins_data['discount']/((100+dbl_tax)/100),3)

                            if ins_data['buyback'] and rst_tax_code not in dct_freight_buyback:
                                dct_freight_buyback[rst_tax_code] = {}
                                dct_freight_buyback[rst_tax_code]['tax_code'] = str(dbl_tax_to_check) if dbl_tax_to_check==0 or dbl_tax_to_check>10 else '0'+str(dbl_tax_to_check)
                                dct_freight_buyback[rst_tax_code]['amount'] = round(ins_data['buyback']/((100+dbl_tax)/100),3)
                            elif ins_data['buyback']:
                                dct_freight_buyback[rst_tax_code]['amount'] += round(ins_data['buyback']/((100+dbl_tax)/100),3)

                            dct_data['Invoice Line level'].append(dct_line_data)
                        elif ins_data['sale_status'] == 2:
                            if not dct_pur_header:
                                if ins_data['branch_state_id'] != ins_data['cust_state_id']:
                                    bln_igst = True
                                elif not ins_data['gst_no']:
                                    bln_kfc = True
                                dct_pur_header['MYGOAL_KEY'] = ins_data['doc_num']
                                dct_pur_header['ShowRoomID'] = ins_data['showroom_code']
                                dct_pur_header['CardName'] = "Exchange Vendor" if not ins_data['card_code'] else ins_data['card_name']
                                dct_pur_header['BranchID'] = 1 if dct_pur_header['ShowRoomID'] !='AGY' else 2
                                dct_pur_header['BillNo'] = ins_data['doc_num']
                                #dct_pur_header['VendorCode'] = "V00392"
                                dct_pur_header["Type"]= "REGULAR" if ins_data.get('cust_type') !=3 else 'SEZ'
                                dct_pur_header['DocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                                # dct_pur_header['DocDate'] = '2020-04-12'
                                dct_pur_header['BillNo'] = ins_data['sales_id']
                                #dct_pur_header['WhsCode'] = ins_data['showroom_code']
                                dct_pur_header["CardCode"] = "EXCG_Vendor" if not ins_data['card_code'] else ins_data['card_code']

                                # if int_entry == '-1':
                                # import pdb; pdb.set_trace()
                                str_log_key_data = "select txt_remarks from sap_api_track where int_type = 1 and int_status in(-1,-2) and int_document_id ="+str_id+";"
                                rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                                if rst_log_key_details:
                                    dct_pur_header['Log_Key'] = json.loads(rst_log_key_details[0].values()[0]).get("Log_Key")

                                dct_data['Header'].append(dct_pur_header)
                            dct_line_data = {}
                            dct_line_data['ItemCode'] = ins_data['item_code']
                            dct_line_data['Quantity'] = ins_data['quantity']
                            dct_line_data['CostPrice'] = round(ins_data['amount']*(-1),2)
                            json_tax = ins_data['tax']
                            # import pdb; pdb.set_trace()
                            if bln_igst or ins_data.get('cust_type') ==3:
                                rst_tax_code = 'IGST0'
                                json_tax.pop(dct_tax['CGST'],'')
                                json_tax.pop(dct_tax['SGST'],'')
                            elif bln_kfc:
                                rst_tax_code = 'GST0'
                                json_tax.pop(dct_tax['IGST'],'')
                                json_tax[dct_tax['KFC']] = 1
                            else:
                                rst_tax_code = 'GST0'
                                json_tax.pop(dct_tax['IGST'],'')
                            #str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                            #rst_tax_code = conn.execute(str_tax_code).fetchall()[0][0]
                            dct_line_data['TaxCode'] = rst_tax_code if not rst_tax_code != 'GST0K' else 'GST0'
                            dct_line_data['Store'] = ins_data['showroom_code']
                            dct_line_data['Department'] = 'SAL'
                            # dct_line_data['Brand'] = "SAMSUNG"
                            dct_line_data['Brand'] = ""
                            dct_line_data['Employee'] = ""
                            if ins_data['mnf_serial']:#Item with imei number
                                dct_line_data['MnfSerial'] = ins_data['mnf_serial']
                            else:#Item with serial number
                                dct_line_data['MnfSerial'] = ins_data['batch_no']
                            dct_line_data['LocCode'] = ins_data['loc_code']
                            dct_data['Purchase Line level'].append(dct_line_data)

                    dct_advance = {}
                    if ins_data.get('cust_type') in [1,2]:
                        dct_data['Invoice Payment Level'] = [{"BankName": "-1", "AdvanceReceiptNo": "-1", "TranId": "-1", "TransferDate": "", "PaymentMode": "", "AcctCode": "", "ChequeNum": -1, "Amount":-1}]
                    # craete dictionary of advance amount
                    else:
                        dct_data['Invoice Payment Level'] = [{"BankName": "-1", "AdvanceReceiptNo": "-1", "TranId": "-1", "TransferDate": "","PaymentMode": "", "AcctCode": "", "ChequeNum": -1, "Amount":-1}]
                        if rst_advance_details:
                            dct_data['Invoice Payment Level'] = []
                            for ins_adv in rst_advance_details:
                                dct_advance[ins_adv['sale_id']] = {'receipt_num':ins_adv['vchr_sap_key'],'dbl_amount':ins_adv['dbl_amount']}
                                dct_payment = {}
                                dct_payment['BankName'] = "-1"
                                dct_payment['AdvanceReceiptNo'] = ins_adv['vchr_sap_key']
                                dct_payment['TranId'] = "-1"
                                dct_payment['TransferDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                                dct_payment['PaymentMode'] = "Customer-Advance"
                                dct_payment['ChequeNum'] = "-1"
                                dct_payment['Amount'] = ins_adv['dbl_amount']
                            #import pdb;pdb.set_trace()
                                str_branch='is null'
                                if ins_adv['fop'] == 1:
                                    str_acc_type = 'CASH A/C'
                                    str_branch= "="+str(ins_data['sh_id'])
                                elif ins_adv['fop'] in [2,3,4,5,6]:
                                    str_acc_type = 'TRANSFER'
                                    str_branch='is null'
                                elif ins_adv['fop'] ==7:
                                    rst_acc = conn.execute("select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id where acm.int_status=0 and acm.fk_branch_id is null and acm.vchr_category = 'PAYTM' and acm.vchr_module_name='PAYMENT'").fetchall()
                                elif ins_adv['fop'] ==8:
                                    str_acc_type = 'PAYTM MALL'
                                    str_branch='is null'
                                elif ins_adv['fop'] ==9:
                                    str_acc_type = 'BHARATH QR'
                                    str_branch='is null'
                            #if ins_adv[']:
                                if ins_adv['fop'] !=7:
                                    rst_acc = conn.execute(str_account_code.format(str_branch,str_acc_type)).fetchall()
                                dct_payment['AcctCode'] = ""
                                if rst_acc:
                                    dct_payment['AcctCode'] = rst_acc[0][0]
                                dct_data['Invoice Payment Level'].append(dct_payment)
                        if rst_payment_details:
                            if not rst_advance_details:
                                dct_data['Invoice Payment Level'] = []
                            for ins_payment in rst_payment_details:
                                dct_payment = {}
                                dct_payment['BankName'] = "-1"
                                if ins_payment['bank_id']:
                                    dct_payment['BankName'] = dct_bank[str(ins_payment['bank_id'])]
                                dct_payment['ShowRoomID'] = ins_payment['showroom_code']
                                dct_payment['AdvanceReceiptNo'] = "-1"
                            # Advance Receipt number
                                #if ins_payment['sales_id'] in dct_advance:
                                    #dct_payment['AdvanceReceiptNo'] = dct_advance[ins_payment['sales_id']]['receipt_num']
                                dct_payment['TranId'] = ins_payment['tr_id'] if ins_payment['tr_id'] else "-1"
                                dct_payment['Currency'] = 'INR'
                                dct_payment['Exchangerate'] = 0

                                dct_payment['TransferDate'] = datetime.strftime(ins_payment['transfer_date'],'%Y-%m-%d')
                                dct_payment['PaymentMode'] = ins_payment['payment_mode']
                                if ins_payment['fop'] == 0:
                                    str_fin_code = ins_payment['fin_code']
                                if ins_payment['fop'] in [1,0]:
                                    str_acc_type = 'CASH A/C'
                                    str_branch= "="+str(ins_payment['sh_id'])
                                elif ins_payment['fop'] in [2,3,4]:
                                    str_acc_type = 'TRANSFER'
                                    str_branch='is null'
                                elif ins_payment['fop'] ==5:
                                    rst_acc = conn.execute("select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id where acm.int_status=0 and acm.fk_branch_id is null and acm.vchr_category = 'PAYTM' and acm.vchr_module_name='PAYMENT'").fetchall()
                                elif ins_payment['fop'] ==6:
                                    str_acc_type = 'PAYTM MALL'
                                    str_branch='is null'
                                elif ins_payment['fop'] ==7:
                                    str_acc_type = 'BHARATH QR'
                                    str_branch='is null'
                                if ins_payment['fop'] !=5:
                                    rst_acc = conn.execute(str_account_code.format(str_branch,str_acc_type)).fetchall()
                                dct_payment['AcctCode'] = "-1"
                                if rst_acc:
                                    dct_payment['AcctCode'] = rst_acc[0][0]
                                dct_payment['ChequeNum'] = ins_payment['card_num'] if ins_payment['fop'] !=7 and ins_payment['card_num'] else "-1"
                                dct_payment['Amount'] = ins_payment['amount']
                            # add advance amount with payment details amount
                                #if ins_payment['sales_id'] in dct_advance:
                                    #dct_payment['Amount'] += dct_advance[ins_payment['sales_id']]['dbl_amount']
                                if ins_payment['fop'] !=4:
                                    dct_data['Invoice Payment Level'].append(dct_payment)
                    if str_fin_code:
                       dct_data['Invoice'][0]['Financier']=str_fin_code
                    if jsn_addition:
                        for ins_addition in jsn_addition:
                            dct_freight= {}
                            add_acc_code=conn.execute("select upper(vchr_acc_name) from chart_of_accounts coa join accounts_map acm on acm.fk_coa_id=coa.pk_bint_id where acm.pk_bint_id="+ins_addition).fetchall()[0][0]
                            dct_freight["ExpCode"]=dct_freight_data[add_acc_code]
                            dct_freight["LineTotal"]=float(jsn_addition[ins_addition])
                            dct_freight["LineTotal"] = round(dct_freight["LineTotal"],2)
                            dct_freight["TaxCode"]="GST0"
                            dct_freight["Store"]= dct_data['Invoice Line level'][0]["Store"]
                            dct_freight["Department"]= dct_data['Invoice Line level'][0]["Department"]
                            dct_freight["Employee"]= dct_data['Invoice Line level'][0]["Employee"]
                            dct_freight["Brand"]= ""
                            if float(jsn_addition[ins_addition]):
                                dct_data['Invoice Freight'].append(dct_freight)
                    if jsn_deduction:

                        for ins_deduction in jsn_deduction:
                            dct_freight= {}
                            add_acc_code=conn.execute("select upper(vchr_acc_name) from chart_of_accounts coa join accounts_map acm on acm.fk_coa_id=coa.pk_bint_id where acm.pk_bint_id="+ins_deduction).fetchall()[0][0]
                            dct_freight["ExpCode"]=dct_freight_data[add_acc_code]
                            dct_freight["LineTotal"]=(-1)*float(jsn_deduction[ins_deduction])
                            dct_freight["LineTotal"] = round(dct_freight["LineTotal"],2)
                            dct_freight["TaxCode"]="GST0"
                            dct_freight["Store"]= dct_data['Invoice Line level'][0]["Store"]
                            dct_freight["Department"]= dct_data['Invoice Line level'][0]["Department"]
                            dct_freight["Employee"]= dct_data['Invoice Line level'][0]["Employee"]
                            dct_freight["Brand"]= ""
                            if float(jsn_deduction[ins_deduction]):
                                dct_data['Invoice Freight'].append(dct_freight)

                    if dct_freight_buyback:
                        for str_buy_back in dct_freight_buyback:
                            dct_freight= {}
                            rst_code=conn.execute("select vchr_code from freight where upper(vchr_category)='BUY BACK' and vchr_tax_code='"+dct_freight_buyback[str_buy_back]['tax_code']+"' and int_status=0").fetchall()
                            dct_freight["ExpCode"]=rst_code[0][0] if rst_code else '-1'
                            dct_freight["LineTotal"]=(-1)*dct_freight_buyback[str_buy_back]['amount']
                            dct_freight["LineTotal"] = round(dct_freight["LineTotal"],2)
                            dct_freight["TaxCode"]=str_buy_back
                            dct_freight["Store"]= dct_data['Invoice Line level'][0]["Store"]
                            dct_freight["Department"]= dct_data['Invoice Line level'][0]["Department"]
                            dct_freight["Employee"]= dct_data['Invoice Line level'][0]["Employee"]
                            dct_freight["Brand"]= ""
                            dct_data['Invoice Freight'].append(dct_freight)
                    if dct_freight_discount:
                        for str_discount in dct_freight_discount:
                            dct_freight= {}
                            rst_code=conn.execute("select vchr_code from freight where upper(vchr_category)='SALES DISCOUNT' and vchr_tax_code='"+dct_freight_discount[str_discount]['tax_code']+"' and int_status=0").fetchall()
                            dct_freight["ExpCode"]=rst_code[0][0] if rst_code else '-1'
                            dct_freight["LineTotal"]=(-1)*dct_freight_discount[str_discount]['amount']
                            dct_freight["LineTotal"] = round(dct_freight["LineTotal"],2)
                            dct_freight["TaxCode"]=str_discount
                            dct_freight["Store"]= dct_data['Invoice Line level'][0]["Store"]
                            dct_freight["Department"]= dct_data['Invoice Line level'][0]["Department"]
                            dct_freight["Employee"]= dct_data['Invoice Line level'][0]["Employee"]
                            dct_freight["Brand"]= ""
                            dct_data['Invoice Freight'].append(dct_freight)
                    if not dct_data['Invoice Freight']:
                        dct_data['Invoice Freight']=[{"ExpCode":-1,"TaxCode":"GST0","LineTotal":0.0}]
                    headers = {"Content-type": "application/json"}
                    # url = 'http://myglive.tmicloud.net:8084/api/In/ExchangeSales'

                    if dct_data['Header'][0]['MYGOAL_KEY'] in ['I-EDY-14805']:
                         print('I-EDY-14805')
                         import pdb; pdb.set_trace()
#                    dct_data['Invoice Payment Level'] = [{"BankName": "-1", "AdvanceReceiptNo": "-1", "TranId": "-1", "TransferDate": "","PaymentMode": "", "AcctCode": "", "ChequeNum": -1, "Amount":-1}]
                    data = json.dumps(dct_data)
                    url = 'http://13.71.18.142:8086/api/In/ExchangeSales'
                    print("ID : ",str_id)
                    print("Data : ",data,"\n\n")
                    # print("Error : ",rst_log_key_details[0].values()[0])
                    #import pdb; pdb.set_trace()
                    try:
                        res_data = requests.post(url,data,headers=headers)
                        print(res_data.text)
                        conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str_id+" and int_type=1")
                        response = json.loads(res_data.text)
                        if str(response['status']).upper() == 'SUCCESS':
                            conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=1")
                            conn.execute("update sales_master set vchr_sap_key='"+str(response['sapKey'])+"',dat_sap_doc_date='"+str(datetime.now())+"' where pk_bint_id="+str_id)
                        else:
                            str_file = doc_date.replace("-","")+'/BillsIssues.txt'
                            file_object = open(str_file, 'a+')
                            file_object.write(data)
                            file_object.write('\n\n')
                            file_object.write(res_data.text)
                            file_object.write('\n\n\n\n')
                            file_object.close()
                            response.pop('message')
                            str_error_text = json.dumps(response)
                            if str_entry == '0':
                                conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str_id+" and int_type=1")
                            else:
                                conn.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str_id+" and int_type=1")

                    except Exception as e:
                        raise
                        
                except Exception as e:
                    print(e)
                    continue
            conn.dispose()
            return True
        except Exception as e:
            raise
    except Exception as e:
        conn.dispose()
        print(str(e))
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        #import pdb; pdb.set_trace()

if __name__ == '__main__':
    smart_choice_to_pos()
